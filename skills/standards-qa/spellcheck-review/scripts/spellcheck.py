#!/usr/bin/env python3
"""
spellcheck.py — Soát lỗi chính tả (tiếng Anh) cho text tài liệu AEC.
                Spell-check English text from AEC documents/registers.

Hai chế độ / two modes:
  * Mặc định (không cần cài gì): bắt lỗi từ bảng lỗi thường gặp + từ lặp
    ("the the") — độ chính xác cao, ít báo nhầm.
  * --dict: nếu có 'pyspellchecker', bổ sung phát hiện từ lạ (unknown word),
    loại trừ theo glossary AEC.

Đầu vào: .csv (chọn cột) hoặc .txt (toàn văn). Chỉ dùng stdlib ở chế độ mặc định.

Usage:
    python spellcheck.py text.txt
    python spellcheck.py register.csv --col Comment
    python spellcheck.py register.csv --col Comment --dict
Exit: 0 = không phát hiện, 1 = có phát hiện, 2 = usage.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

# Bảng lỗi chính tả thường gặp -> gợi ý đúng (mở rộng tuỳ nhu cầu).
COMMON_MISSPELLINGS = {
    "teh": "the", "adn": "and", "recieve": "receive", "recieved": "received",
    "seperate": "separate", "seperated": "separated", "definately": "definitely",
    "occured": "occurred", "occurance": "occurrence", "neccessary": "necessary",
    "accomodate": "accommodate", "accomodation": "accommodation",
    "acheive": "achieve", "achievment": "achievement", "architectural": None,
    "arcitectural": "architectural", "arcitect": "architect", "achitect": "architect",
    "concrete": None, "concreate": "concrete", "reinforcment": "reinforcement",
    "reinforcated": "reinforced", "steal": "steel", "steelwork": None,
    "dimention": "dimension", "dimention": "dimension", "dimentions": "dimensions",
    "elevaton": "elevation", "elavation": "elevation", "foundaton": "foundation",
    "foundtion": "foundation", "instalation": "installation",
    "installaton": "installation", "maintainance": "maintenance",
    "maintenence": "maintenance", "equipement": "equipment", "equiptment": "equipment",
    "clearence": "clearance", "clearence": "clearance", "tolerence": "tolerance",
    "aligment": "alignment", "allignment": "alignment", "cordination": "coordination",
    "coordiation": "coordination", "coordinaton": "coordination",
    "specfication": "specification", "specificaton": "specification",
    "schedual": "schedule", "shedule": "schedule", "seperate": "separate",
    "verticle": "vertical", "horizonal": "horizontal", "horizontial": "horizontal",
    "insulaton": "insulation", "waterproofing": None, "waterproffing": "waterproofing",
    "sprinker": "sprinkler", "sprinlker": "sprinkler", "celing": "ceiling",
    "cieling": "ceiling", "widht": "width", "hieght": "height", "lenght": "length",
    "thru": "through", "recomend": "recommend", "recomended": "recommended",
    "existng": "existing", "existin": "existing", "buildng": "building",
    "structual": "structural", "strucutral": "structural", "mechancial": "mechanical",
    "electical": "electrical", "electcal": "electrical", "pleumbing": "plumbing",
    "plumming": "plumbing", "drawign": "drawing", "drawin": "drawing",
    "aproved": "approved", "aprove": "approve", "approvel": "approval",
    "comitted": "committed", "commited": "committed", "recored": "record",
    "responsable": "responsible", "responsiblity": "responsibility",
}
# bỏ các giá trị None (từ đúng lỡ đưa vào)
COMMON_MISSPELLINGS = {k: v for k, v in COMMON_MISSPELLINGS.items() if v}


def load_glossary(path: Path | None) -> set[str]:
    words: set[str] = set()
    if path and path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            w = line.strip().lower()
            if w and not w.startswith("#"):
                words.add(w)
    return words


def read_texts(path: Path, col: str | None) -> list[tuple[str, str]]:
    """Trả về [(location, text)]. location = 'row N' hoặc 'line N'."""
    out: list[tuple[str, str]] = []
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            headers = reader.fieldnames or []
            if col and col not in headers:
                print(f"ERROR: cột '{col}' không có. Cột hiện có: {headers}",
                      file=sys.stderr)
                sys.exit(2)
            for i, row in enumerate(reader, start=2):
                if col:
                    out.append((f"row {i}", row.get(col) or ""))
                else:
                    out.append((f"row {i}", " ".join(str(v) for v in row.values())))
    else:
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            out.append((f"line {i}", line))
    return out


def is_domain_ok(word: str, glossary: set[str]) -> bool:
    lw = word.lower()
    if lw in glossary:
        return True
    if word.isupper() and len(word) <= 6:      # acronym: MEP, HVAC, RFI…
        return True
    if any(c.isdigit() for c in word):
        return True
    return False


def check_texts(texts, glossary, use_dict: bool) -> list[dict]:
    findings: list[dict] = []
    spell = None
    if use_dict:
        try:
            from spellchecker import SpellChecker
            spell = SpellChecker()
        except ImportError:
            print("(--dict: chưa cài pyspellchecker → chỉ chạy chế độ mặc định)",
                  file=sys.stderr)

    for loc, text in texts:
        tokens = WORD_RE.findall(text)
        low = [t.lower() for t in tokens]

        # 1) lỗi thường gặp
        for t in tokens:
            sug = COMMON_MISSPELLINGS.get(t.lower())
            if sug:
                findings.append({"type": "MISSPELLING", "loc": loc,
                                 "word": t, "suggest": sug})
        # 2) từ lặp liên tiếp
        for a, b in zip(low, low[1:]):
            if a == b and a.isalpha() and len(a) > 1:
                findings.append({"type": "REPEATED", "loc": loc,
                                 "word": a, "suggest": f"bỏ 1 '{a}'"})
        # 3) từ lạ (chỉ khi --dict)
        if spell is not None:
            candidates = [t for t in tokens
                          if not is_domain_ok(t, glossary)
                          and t.lower() not in COMMON_MISSPELLINGS]
            unknown = spell.unknown([c.lower() for c in candidates])
            for t in candidates:
                if t.lower() in unknown:
                    corr = spell.correction(t.lower())
                    findings.append({"type": "UNKNOWN", "loc": loc, "word": t,
                                     "suggest": corr or "?"})
    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Spell-check AEC document text.")
    ap.add_argument("input", help="CSV hoặc TXT")
    ap.add_argument("--col", help="Cột text nếu đầu vào là CSV")
    ap.add_argument("--dict", action="store_true", help="Bật dò từ lạ (cần pyspellchecker)")
    ap.add_argument("--glossary", help="File glossary allowlist (mặc định references/aec-glossary.txt)")
    args = ap.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.input}", file=sys.stderr)
        return 2

    gloss_path = Path(args.glossary) if args.glossary else \
        path.parent.parent / "references" / "aec-glossary.txt"
    glossary = load_glossary(gloss_path if gloss_path.is_file() else None)

    texts = read_texts(path, args.col)
    findings = check_texts(texts, glossary, args.dict)

    if not findings:
        print("PASS: không phát hiện lỗi chính tả / từ lặp.")
        return 0

    order = {"MISSPELLING": 0, "REPEATED": 1, "UNKNOWN": 2}
    findings.sort(key=lambda f: (order[f["type"]], f["loc"]))
    for f in findings:
        print(f"  [{f['type']:11}] {f['loc']:8} '{f['word']}' → {f['suggest']}")
    print(f"\nTổng phát hiện / findings: {len(findings)}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
