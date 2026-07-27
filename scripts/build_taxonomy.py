#!/usr/bin/env python3
"""build_taxonomy.py — Sinh docs/skill-taxonomy.md từ metadata của các skill.
                       Generate docs/skill-taxonomy.md from skill metadata.

Đọc mọi skills/<software>/<name>/SKILL.md, rồi dựng 3 bảng tra cứu:
theo phần mềm / theo bộ môn / theo tính chất công việc.
Reads every SKILL.md and renders three cross-reference tables:
by software / by discipline / by category.

Cách dùng / Usage:
    python scripts/build_taxonomy.py            # ghi docs/skill-taxonomy.md
    python scripts/build_taxonomy.py --check    # exit 1 nếu file đã lỗi thời
"""
from __future__ import annotations
import argparse
import glob
import os
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "skill-taxonomy.md")

SOFTWARE_LABEL = {
    "revit": "Revit",
    "navisworks": "Navisworks",
    "acc-bim360": "ACC / BIM 360",
    "bluebeam-pdf": "Bluebeam / PDF",
    "office-data": "Office / CSV (agnostic)",
}
DISCIPLINE_LABEL = {
    "multi": "Đa bộ môn / Multi",
    "architecture": "Kiến trúc / Architecture",
    "structural": "Kết cấu / Structural",
    "mep": "MEP",
    "civil": "Hạ tầng / Civil",
}
CATEGORY_LABEL = {
    "coordination": "Coordination — Điều phối",
    "qa": "QA / QC — Kiểm tra",
    "standards": "Standards — Tiêu chuẩn",
    "documentation": "Documentation — Tài liệu",
    "project-management": "Project Management — Quản lý dự án",
    "cost": "Cost / QS — Khối lượng & chi phí",
    "automation": "Automation — Tự động hoá",
}
# thứ tự hiển thị / display order
SOFTWARE_ORDER = ["revit", "navisworks", "acc-bim360", "bluebeam-pdf", "office-data"]
DISCIPLINE_ORDER = ["multi", "architecture", "structural", "mep", "civil"]
CATEGORY_ORDER = ["coordination", "qa", "standards", "documentation",
                  "project-management", "cost", "automation"]


class Skill:
    def __init__(self, name, path, software, discipline, category, summary):
        self.name = name
        self.path = path          # relative to repo root
        self.software = software
        self.discipline = discipline
        self.category = category
        self.summary = summary


def short_summary(description: str) -> str:
    """Lấy phần 'làm gì' (trước 'Use when') / the 'what' before 'Use when'.
    Gộp mọi khoảng trắng/xuống dòng để không vỡ ô bảng Markdown."""
    s = " ".join(description.split())
    s = s.split(" Use when", 1)[0].strip()
    return s.rstrip(".").strip()


def load_skills() -> list[Skill]:
    skills = []
    for md in sorted(glob.glob(os.path.join(ROOT, "skills", "*", "*", "SKILL.md"))):
        txt = open(md, encoding="utf-8").read()
        meta = yaml.safe_load(txt.split("---", 2)[1])
        m = meta.get("metadata") or {}
        rel = os.path.relpath(md, ROOT).replace(os.sep, "/")
        skills.append(Skill(
            name=meta["name"],
            path=rel,
            software=m.get("software", "?"),
            discipline=m.get("discipline", "?"),
            category=m.get("category", "?"),
            summary=short_summary(meta["description"]),
        ))
    return skills


def link(sk: Skill) -> str:
    return f"[`{sk.name}`](../{sk.path})"


def order_key(value, order):
    return (order.index(value) if value in order else len(order), value)


def render(skills: list[Skill]) -> str:
    n = len(skills)
    L: list[str] = []
    L.append("# Skill Taxonomy — Bản đồ skill / Skill map")
    L.append("")
    L.append("> ⚙️ **Auto-generated** bởi `scripts/build_taxonomy.py` từ metadata "
             "của từng skill. Đừng sửa tay — chạy lại script sau khi thêm/sửa skill.")
    L.append("> Auto-generated from each skill's `metadata`. Do not edit by hand.")
    L.append("")
    L.append(f"Skill được tổ chức **theo phần mềm** (thư mục `skills/<software>/`) "
             f"và gắn **metadata** (`software`, `discipline`, `category`) để tra cứu "
             f"chéo. **{n} skill · {len(SOFTWARE_ORDER)} nhóm phần mềm.**")
    L.append("")
    L.append("- 🧭 [Theo phần mềm / By software](#-theo-phần-mềm--by-software)")
    L.append("- 🏗️ [Theo bộ môn / By discipline](#-theo-bộ-môn--by-discipline)")
    L.append("- 🧩 [Theo tính chất / By category](#-theo-tính-chất-công-việc--by-category)")
    L.append("")

    # --- By software (mirrors the folder structure) ---
    L.append("## 🧭 Theo phần mềm / By software")
    L.append("")
    L.append("*Đây cũng là cấu trúc thư mục / this is also the folder layout.*")
    L.append("")
    for sw in sorted({s.software for s in skills}, key=lambda v: order_key(v, SOFTWARE_ORDER)):
        group = [s for s in skills if s.software == sw]
        L.append(f"### {SOFTWARE_LABEL.get(sw, sw)} — `skills/{sw}/` ({len(group)})")
        L.append("")
        L.append("| Skill | Bộ môn | Tính chất | Tóm tắt / What it does |")
        L.append("|-------|--------|-----------|------------------------|")
        for s in sorted(group, key=lambda x: (order_key(x.category, CATEGORY_ORDER), x.name)):
            L.append(f"| {link(s)} | {DISCIPLINE_LABEL.get(s.discipline, s.discipline)} "
                     f"| {CATEGORY_LABEL.get(s.category, s.category)} | {s.summary} |")
        L.append("")

    # --- By discipline ---
    L.append("## 🏗️ Theo bộ môn / By discipline")
    L.append("")
    for dis in sorted({s.discipline for s in skills}, key=lambda v: order_key(v, DISCIPLINE_ORDER)):
        group = [s for s in skills if s.discipline == dis]
        L.append(f"### {DISCIPLINE_LABEL.get(dis, dis)} ({len(group)})")
        L.append("")
        L.append("| Skill | Phần mềm | Tính chất | Tóm tắt / What it does |")
        L.append("|-------|----------|-----------|------------------------|")
        for s in sorted(group, key=lambda x: (order_key(x.software, SOFTWARE_ORDER), x.name)):
            L.append(f"| {link(s)} | {SOFTWARE_LABEL.get(s.software, s.software)} "
                     f"| {CATEGORY_LABEL.get(s.category, s.category)} | {s.summary} |")
        L.append("")

    # --- By category (work nature) ---
    L.append("## 🧩 Theo tính chất công việc / By category")
    L.append("")
    for cat in sorted({s.category for s in skills}, key=lambda v: order_key(v, CATEGORY_ORDER)):
        group = [s for s in skills if s.category == cat]
        L.append(f"### {CATEGORY_LABEL.get(cat, cat)} ({len(group)})")
        L.append("")
        L.append("| Skill | Phần mềm | Bộ môn | Tóm tắt / What it does |")
        L.append("|-------|----------|--------|------------------------|")
        for s in sorted(group, key=lambda x: (order_key(x.software, SOFTWARE_ORDER), x.name)):
            L.append(f"| {link(s)} | {SOFTWARE_LABEL.get(s.software, s.software)} "
                     f"| {DISCIPLINE_LABEL.get(s.discipline, s.discipline)} | {s.summary} |")
        L.append("")

    L.append("---")
    L.append("*Xem lộ trình phát triển skill Revit: [`roadmap.md`](roadmap.md).*")
    L.append("")
    return "\n".join(L)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Generate skill taxonomy doc.")
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 nếu docs/skill-taxonomy.md lỗi thời")
    args = ap.parse_args(argv)

    content = render(load_skills())
    if args.check:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != content:
            print("docs/skill-taxonomy.md lỗi thời — chạy: python scripts/build_taxonomy.py",
                  file=sys.stderr)
            return 1
        print("docs/skill-taxonomy.md up to date.")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(content)
    print(f"Wrote {os.path.relpath(OUT, ROOT)} ({content.count(chr(10))+1} lines).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
