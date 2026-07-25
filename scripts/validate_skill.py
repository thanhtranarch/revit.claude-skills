#!/usr/bin/env python3
"""
validate_skill.py — Kiểm tra cấu trúc & metadata của một Claude Skill.
                    Validate the structure & metadata of a Claude Skill.

Chỉ dùng thư viện chuẩn + PyYAML (không phụ thuộc gói lạ) để lớp kiểm định
luôn chạy được. / Uses only stdlib + PyYAML so the gate always runs.

Cách dùng / Usage:
    python scripts/validate_skill.py skills/bim-coordination/clash-report-analysis
    python scripts/validate_skill.py skills            # quét đệ quy / recurse
    python scripts/validate_skill.py --json skills

Exit code: 0 = PASS, 1 = có lỗi / has errors, 2 = lỗi sử dụng / usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

# --- Quy ước / Conventions --------------------------------------------------
# Theo Agent Skills spec (agentskills.io/specification).
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")   # kebab-case, không '--'
DESC_MIN, DESC_MAX = 20, 1024
NAME_MAX = 64
COMPAT_MAX = 500
MAX_FILE_BYTES = 5 * 1024 * 1024                       # 5 MB / file
MAX_SKILL_BYTES = 50 * 1024 * 1024                     # 50 MB / skill

# Các key frontmatter được spec định nghĩa / spec-defined frontmatter keys.
KNOWN_KEYS = {
    "name", "description", "license", "compatibility",
    "metadata", "allowed-tools",
}

# Phần mở rộng cho phép trong 1 skill / allowed file extensions in a skill.
ALLOWED_EXT = {
    ".md", ".py", ".txt", ".json", ".yaml", ".yml", ".csv", ".tsv",
    ".xml", ".html", ".htm", ".pdf", ".png", ".jpg", ".jpeg", ".svg",
    ".xlsx", ".dyn", ".rvt", ".nwd", ".nwc", ".ifc", ".dwg", ".dwf",
    ".cfg", ".ini", ".toml",
}
# File thực thi / nhị phân đáng ngờ — chặn ngay / suspicious executables.
BLOCKED_EXT = {
    ".exe", ".dll", ".so", ".dylib", ".bat", ".cmd", ".sh", ".ps1",
    ".scr", ".com", ".jar", ".msi", ".apk", ".bin", ".vbs", ".wsf",
}


class Finding:
    __slots__ = ("level", "skill", "path", "message")

    def __init__(self, level: str, skill: str, path: str, message: str):
        self.level = level          # "error" | "warning"
        self.skill = skill
        self.path = path
        self.message = message

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "skill": self.skill,
            "path": self.path,
            "message": self.message,
        }

    def __str__(self) -> str:
        tag = "ERROR" if self.level == "error" else "WARN "
        loc = self.path or self.skill
        return f"[{tag}] {loc}: {self.message}"


def parse_frontmatter(text: str):
    """Tách YAML frontmatter giữa hai dấu '---'. Return (meta, error)."""
    if not text.startswith("---"):
        return None, "SKILL.md thiếu YAML frontmatter (phải bắt đầu bằng '---')"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "YAML frontmatter không đóng đúng (thiếu '---' thứ hai)"
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        return None, f"YAML frontmatter không hợp lệ: {exc}"
    if not isinstance(meta, dict):
        return None, "YAML frontmatter phải là một mapping (key: value)"
    return meta, None


def validate_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    name = skill_dir.name

    def err(msg, path=""):
        findings.append(Finding("error", name, path, msg))

    def warn(msg, path=""):
        findings.append(Finding("warning", name, path, msg))

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        err("Thiếu SKILL.md / Missing SKILL.md", str(skill_dir))
        return findings

    meta, fm_err = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
    if fm_err:
        err(fm_err, str(skill_md))
        return findings

    # --- name --------------------------------------------------------------
    fm_name = meta.get("name")
    if not fm_name:
        err("Frontmatter thiếu 'name'", str(skill_md))
    else:
        if not isinstance(fm_name, str) or not NAME_RE.match(fm_name):
            err(f"'name' phải là kebab-case: {fm_name!r}", str(skill_md))
        if isinstance(fm_name, str) and len(fm_name) > NAME_MAX:
            err(f"'name' quá dài (>{NAME_MAX} ký tự)", str(skill_md))
        if fm_name != name:
            err(f"'name' ({fm_name!r}) phải khớp tên thư mục ({name!r})", str(skill_md))

    # --- description -------------------------------------------------------
    desc = meta.get("description")
    if not desc:
        err("Frontmatter thiếu 'description'", str(skill_md))
    elif not isinstance(desc, str):
        err("'description' phải là chuỗi", str(skill_md))
    else:
        if len(desc) < DESC_MIN:
            warn(f"'description' hơi ngắn (<{DESC_MIN} ký tự) — nên nêu rõ khi nào dùng", str(skill_md))
        if len(desc) > DESC_MAX:
            err(f"'description' quá dài (>{DESC_MAX} ký tự)", str(skill_md))

    # --- license (tuỳ chọn / optional) -------------------------------------
    lic = meta.get("license")
    if lic is not None and not isinstance(lic, str):
        err("'license' phải là chuỗi (tên giấy phép hoặc file)", str(skill_md))

    # --- compatibility (tuỳ chọn / optional) -------------------------------
    compat = meta.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            err("'compatibility' phải là chuỗi", str(skill_md))
        elif len(compat) > COMPAT_MAX:
            err(f"'compatibility' quá dài (>{COMPAT_MAX} ký tự)", str(skill_md))

    # --- metadata (tuỳ chọn / optional) ------------------------------------
    md = meta.get("metadata")
    if md is not None:
        if not isinstance(md, dict):
            err("'metadata' phải là mapping key: value", str(skill_md))
        else:
            for k, v in md.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    err(f"'metadata' phải toàn chuỗi→chuỗi (lỗi ở {k!r})", str(skill_md))
                    break

    # --- allowed-tools (tuỳ chọn / optional) -------------------------------
    # Spec: chuỗi tách bằng dấu cách (thử nghiệm). Chấp nhận list cho tương thích.
    tools = meta.get("allowed-tools")
    if tools is not None and not isinstance(tools, (list, str)):
        err("'allowed-tools' phải là chuỗi (tách bằng dấu cách) hoặc list", str(skill_md))

    # --- key lạ / unknown frontmatter keys ---------------------------------
    if isinstance(meta, dict):
        for key in meta:
            if key not in KNOWN_KEYS:
                warn(f"Key frontmatter không thuộc spec: {key!r} "
                     f"(cân nhắc đưa vào 'metadata')", str(skill_md))

    # --- Quét file trong skill / scan files -------------------------------
    total_bytes = 0
    for f in sorted(skill_dir.rglob("*")):
        if f.is_dir():
            continue
        rel = f.relative_to(skill_dir)
        ext = f.suffix.lower()
        size = f.stat().st_size
        total_bytes += size

        if ext in BLOCKED_EXT:
            err(f"File thực thi/nhị phân bị chặn: {rel}", str(f))
        elif ext and ext not in ALLOWED_EXT:
            warn(f"Phần mở rộng không nằm trong danh sách cho phép: {rel}", str(f))
        if size > MAX_FILE_BYTES:
            err(f"File quá lớn ({size // 1024} KB > {MAX_FILE_BYTES // 1024} KB): {rel}", str(f))
        if f.name.startswith(".") and f.name not in {".gitkeep"}:
            warn(f"File ẩn trong skill: {rel}", str(f))

    if total_bytes > MAX_SKILL_BYTES:
        err(f"Skill quá lớn ({total_bytes // 1024} KB > {MAX_SKILL_BYTES // 1024} KB)", str(skill_dir))

    return findings


def find_skills(root: Path) -> list[Path]:
    """Một skill là thư mục chứa SKILL.md. / A skill = dir containing SKILL.md."""
    if (root / "SKILL.md").is_file():
        return [root]
    return sorted(p.parent for p in root.rglob("SKILL.md"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate Claude skill structure.")
    ap.add_argument("paths", nargs="+", help="Thư mục skill hoặc thư mục chứa skill")
    ap.add_argument("--json", action="store_true", help="Xuất JSON")
    args = ap.parse_args(argv)

    skills: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"ERROR: không tìm thấy đường dẫn: {p}", file=sys.stderr)
            return 2
        skills.extend(find_skills(path))

    skills = sorted(set(skills))
    if not skills:
        print("Không tìm thấy skill nào (không có SKILL.md).", file=sys.stderr)
        return 2

    all_findings: list[Finding] = []
    for skill in skills:
        all_findings.extend(validate_skill(skill))

    errors = [f for f in all_findings if f.level == "error"]
    warnings = [f for f in all_findings if f.level == "warning"]

    if args.json:
        print(json.dumps({
            "skills_checked": len(skills),
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [f.as_dict() for f in all_findings],
        }, ensure_ascii=False, indent=2))
    else:
        for f in all_findings:
            print(f)
        status = "FAIL" if errors else "PASS"
        print(f"\n{status}: {len(skills)} skill, {len(errors)} lỗi, {len(warnings)} cảnh báo.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
