#!/usr/bin/env python3
"""
audit_skill.py — Quét bảo mật tĩnh cho Claude Skill do người khác đóng góp.
                 Static security audit for community-contributed Claude Skills.

Mục tiêu / Goal: phát hiện mã độc, lệnh phá huỷ, rò rỉ dữ liệu, thực thi động
và prompt-injection TRƯỚC KHI merge. Chỉ dùng thư viện chuẩn (regex + AST)
để không phụ thuộc gói bên ngoài.

Cách dùng / Usage:
    python scripts/audit_skill.py skills/bim-coordination/clash-report-analysis
    python scripts/audit_skill.py skills               # quét đệ quy / recurse
    python scripts/audit_skill.py --json skills
    python scripts/audit_skill.py --fail-on medium skills

Severity: HIGH | MEDIUM | LOW.
Exit code: 0 = đạt ngưỡng / at-or-below threshold, 1 = vượt ngưỡng, 2 = usage.
Mặc định fail khi có HIGH. / Default fails on HIGH.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import unicodedata
from pathlib import Path

SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

# --- 1. Mẫu regex cho văn bản/shell/mọi file (áp cho .md, .py, .txt, ...) ---
# Mỗi rule: (id, severity, mô tả, regex đã biên dịch)
TEXT_RULES = [
    # Thực thi mã từ mạng / remote code execution
    ("curl-pipe-sh", "HIGH", "Tải & chạy trực tiếp từ mạng (curl|bash)",
     re.compile(r"(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba)?sh", re.I)),
    ("iex-download", "HIGH", "PowerShell tải & chạy (IEX/DownloadString)",
     re.compile(r"IEX\s*\(|DownloadString|Invoke-Expression", re.I)),
    ("base64-pipe-sh", "HIGH", "Giải mã base64 rồi chạy shell",
     re.compile(r"base64\s+(--?d(ecode)?)\b[^\n|]*\|\s*(ba)?sh", re.I)),
    # Lệnh phá huỷ / destructive
    ("rm-rf-root", "HIGH", "Xoá đệ quy thư mục hệ thống (rm -rf /)",
     re.compile(r"\brm\s+-[a-z]*r[a-z]*f[a-z]*\s+(/|~|\$HOME|\*)")),
    ("disk-wipe", "HIGH", "Ghi đè/format ổ đĩa (mkfs/dd/format)",
     re.compile(r"\b(mkfs\.\w+|dd\s+if=|:\(\)\s*\{|shred\s+)")),
    # Rò rỉ dữ liệu / data exfiltration
    ("read-ssh-keys", "HIGH", "Truy cập khoá SSH/GPG",
     re.compile(r"(~|/root|/home/[^/\s]+)/\.(ssh|gnupg)(/|\b)")),
    ("read-cloud-creds", "HIGH", "Truy cập credential đám mây",
     re.compile(r"\.(aws|azure|config/gcloud)/|/\.docker/config\.json")),
    ("env-secret", "MEDIUM", "Đọc biến môi trường bí mật",
     re.compile(r"(SECRET|TOKEN|PASSWORD|PASSWD|API[_-]?KEY|PRIVATE[_-]?KEY|ACCESS[_-]?KEY)", re.I)),
    ("crypto-wallet", "HIGH", "Truy cập ví tiền mã hoá",
     re.compile(r"wallet\.dat|\.electrum|keystore|metamask", re.I)),
    # Prompt-injection trong SKILL.md / instruction override
    ("prompt-injection", "HIGH", "Câu chỉ dẫn cố vượt quyền / prompt-injection",
     re.compile(r"ignore (all |the )?(previous|prior|above) (instructions?|prompts?)"
                r"|disregard (your |the )?(system|previous)"
                r"|exfiltrat|leak (the )?(secret|token|credential)"
                r"|do not (tell|inform|mention to) the user"
                r"|without (asking|telling) the user"
                r"|disable (the )?(safety|security|guardrail)", re.I)),
    ("hidden-instruction", "MEDIUM", "Chỉ dẫn ẩn cho AI (download & run/execute silently)",
     re.compile(r"(download|fetch).{0,40}(and|then).{0,20}(run|execute|eval)", re.I)),
]

# --- 2. Mẫu AST cho file Python -------------------------------------------
DANGEROUS_CALLS = {
    "eval": ("HIGH", "Thực thi động eval()"),
    "exec": ("HIGH", "Thực thi động exec()"),
    "compile": ("MEDIUM", "compile() mã động"),
    "__import__": ("MEDIUM", "Nạp module động __import__"),
}
# os.<attr> / subprocess.<attr> nguy hiểm
DANGEROUS_ATTR_CALLS = {
    ("os", "system"): ("HIGH", "os.system() chạy lệnh shell"),
    ("os", "popen"): ("HIGH", "os.popen() chạy lệnh shell"),
    ("os", "remove"): ("LOW", "os.remove() xoá file"),
    ("os", "unlink"): ("LOW", "os.unlink() xoá file"),
    ("os", "rmdir"): ("LOW", "os.rmdir() xoá thư mục"),
    ("shutil", "rmtree"): ("MEDIUM", "shutil.rmtree() xoá đệ quy"),
    ("subprocess", "call"): ("MEDIUM", "subprocess.call()"),
    ("subprocess", "run"): ("MEDIUM", "subprocess.run()"),
    ("subprocess", "Popen"): ("MEDIUM", "subprocess.Popen()"),
    ("subprocess", "check_output"): ("MEDIUM", "subprocess.check_output()"),
    ("pickle", "loads"): ("MEDIUM", "pickle.loads() có thể chạy mã tuỳ ý"),
    ("pickle", "load"): ("MEDIUM", "pickle.load() có thể chạy mã tuỳ ý"),
    ("marshal", "loads"): ("MEDIUM", "marshal.loads()"),
}
NETWORK_MODULES = {"socket", "requests", "urllib", "urllib2", "http", "httplib",
                   "ftplib", "smtplib", "telnetlib", "paramiko", "httpx"}

# Zero-width / bidi / control chars dùng để giấu payload.
HIDDEN_CHARS = {
    "​": "ZERO WIDTH SPACE", "‌": "ZERO WIDTH NON-JOINER",
    "‍": "ZERO WIDTH JOINER", "⁠": "WORD JOINER",
    "﻿": "ZERO WIDTH NO-BREAK SPACE", "‮": "RIGHT-TO-LEFT OVERRIDE",
    "‭": "LEFT-TO-RIGHT OVERRIDE", "⁦": "LEFT-TO-RIGHT ISOLATE",
    "⁧": "RIGHT-TO-LEFT ISOLATE",
}
SCAN_TEXT_EXT = {".md", ".py", ".txt", ".json", ".yaml", ".yml", ".xml",
                 ".csv", ".tsv", ".cfg", ".ini", ".toml", ".dyn"}
LONG_B64_RE = re.compile(r"['\"][A-Za-z0-9+/]{120,}={0,2}['\"]")


class Finding:
    __slots__ = ("severity", "rule", "path", "line", "message", "snippet")

    def __init__(self, severity, rule, path, line, message, snippet=""):
        self.severity = severity
        self.rule = rule
        self.path = path
        self.line = line
        self.message = message
        self.snippet = snippet

    def as_dict(self):
        return {
            "severity": self.severity, "rule": self.rule, "path": self.path,
            "line": self.line, "message": self.message, "snippet": self.snippet,
        }

    def __str__(self):
        loc = f"{self.path}:{self.line}" if self.line else self.path
        snip = f"  |  {self.snippet.strip()[:80]}" if self.snippet else ""
        return f"[{self.severity:6}] {self.rule:20} {loc}: {self.message}{snip}"


def scan_text(path: Path, findings: list[Finding]) -> None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        findings.append(Finding("LOW", "read-error", str(path), 0, f"Không đọc được: {exc}"))
        return
    for i, line in enumerate(lines, 1):
        for rule_id, sev, desc, rx in TEXT_RULES:
            if rx.search(line):
                findings.append(Finding(sev, rule_id, str(path), i, desc, line))
        for ch, cname in HIDDEN_CHARS.items():
            if ch in line:
                findings.append(Finding("HIGH", "hidden-unicode", str(path), i,
                                        f"Ký tự Unicode ẩn: {cname}", ""))
        if LONG_B64_RE.search(line):
            findings.append(Finding("MEDIUM", "long-base64", str(path), i,
                                    "Chuỗi base64 dài (khả năng obfuscation)", line))


def _dotted(node: ast.AST):
    """Trả về ('module', 'attr') cho node kiểu module.attr(...)."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return (node.value.id, node.attr)
    return None


def scan_python(path: Path, findings: list[Finding]) -> None:
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        findings.append(Finding("MEDIUM", "py-syntax", str(path), exc.lineno or 0,
                                f"Không parse được Python (khả nghi): {exc.msg}"))
        return

    imported_net = []
    for node in ast.walk(tree):
        # import mạng
        if isinstance(node, ast.Import):
            for a in node.names:
                root = a.name.split(".")[0]
                if root in NETWORK_MODULES:
                    imported_net.append((root, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in NETWORK_MODULES:
                imported_net.append((root, node.lineno))
        # lời gọi hàm
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in DANGEROUS_CALLS:
                sev, desc = DANGEROUS_CALLS[func.id]
                findings.append(Finding(sev, f"py-{func.id}", str(path), node.lineno, desc))
            dotted = _dotted(func)
            if dotted and dotted in DANGEROUS_ATTR_CALLS:
                sev, desc = DANGEROUS_ATTR_CALLS[dotted]
                # subprocess với shell=True nâng mức nghiêm trọng
                if dotted[0] == "subprocess" and any(
                    isinstance(k, ast.keyword) and k.arg == "shell"
                    and isinstance(k.value, ast.Constant) and k.value.value is True
                    for k in node.keywords
                ):
                    sev = "HIGH"
                    desc += " với shell=True"
                findings.append(Finding(sev, f"py-{dotted[0]}.{dotted[1]}", str(path), node.lineno, desc))

    for mod, line in imported_net:
        findings.append(Finding("MEDIUM", "py-network-import", str(path), line,
                                f"Import module mạng '{mod}' — kiểm tra rò rỉ dữ liệu"))


def audit_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for f in sorted(skill_dir.rglob("*")):
        if f.is_dir():
            continue
        ext = f.suffix.lower()
        if ext == ".py":
            scan_text(f, findings)
            scan_python(f, findings)
        elif ext in SCAN_TEXT_EXT:
            scan_text(f, findings)
    return findings


def find_skills(root: Path) -> list[Path]:
    if (root / "SKILL.md").is_file():
        return [root]
    return sorted(p.parent for p in root.rglob("SKILL.md"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Static security audit for Claude skills.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", choices=["low", "medium", "high"], default="high",
                    help="Ngưỡng fail (mặc định: high)")
    args = ap.parse_args(argv)

    skills: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"ERROR: không tìm thấy: {p}", file=sys.stderr)
            return 2
        skills.extend(find_skills(path))
    skills = sorted(set(skills))
    if not skills:
        print("Không tìm thấy skill nào (không có SKILL.md).", file=sys.stderr)
        return 2

    all_findings: list[Finding] = []
    for skill in skills:
        all_findings.extend(audit_skill(skill))

    all_findings.sort(key=lambda f: (-SEVERITY_ORDER[f.severity], f.path, f.line))
    threshold = SEVERITY_ORDER[args.fail_on.upper()]
    blocking = [f for f in all_findings if SEVERITY_ORDER[f.severity] >= threshold]

    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in all_findings:
        counts[f.severity] += 1

    if args.json:
        print(json.dumps({
            "skills_audited": len(skills),
            "counts": counts,
            "fail_on": args.fail_on,
            "blocking": len(blocking),
            "findings": [f.as_dict() for f in all_findings],
        }, ensure_ascii=False, indent=2))
    else:
        for f in all_findings:
            print(f)
        status = "FAIL" if blocking else "PASS"
        print(f"\n{status}: {len(skills)} skill  |  "
              f"HIGH={counts['HIGH']} MEDIUM={counts['MEDIUM']} LOW={counts['LOW']}  "
              f"(fail-on={args.fail_on}, blocking={len(blocking)})")

    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
