#!/usr/bin/env python3
"""
audit_iso19650_project.py — Kiểm tra mức tuân thủ ISO 19650 của CẢ dự án.
                            Project-level ISO 19650 conformance audit.

Khác `iso19650-naming-check` (chỉ soát *tên file*), skill này soát **thông tin
quản lý** của cả CDE register: metadata đầy đủ, mã suitability/revision hợp lệ,
và **tính nhất quán giữa trạng thái CDE ↔ suitability ↔ revision** — rồi chấm
điểm tuân thủ toàn dự án.
Audits a whole CDE/container register for ISO 19650 information-management
conformance (metadata completeness, suitability/revision validity, and
state↔suitability↔revision consistency) and scores the project.

Chỉ dùng thư viện chuẩn; `--rules` cần pyyaml; `--expected` để đối chiếu MIDP.

Usage:
    python audit_iso19650_project.py register.csv
    python audit_iso19650_project.py register.csv --json
    python audit_iso19650_project.py register.csv --csv findings.csv
    python audit_iso19650_project.py register.csv --expected midp.csv --rules my.yaml
Exit: 0 = đạt ngưỡng (mặc định 100%), 1 = có container lỗi, 2 = usage error.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

# --- Quy tắc mặc định (UK BIM Framework) — tuỳ biến qua --rules -------------
DEFAULT_RULES = {
    # Mã suitability/status hợp lệ (khớp iso19650-naming-check).
    "suitability_allowed": [
        "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7",
        "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9",
        "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9",
        "CR", "D1", "D2", "D3", "D4",
    ],
    "revision_pattern": r"^[PC][0-9]{2}(\.[0-9]{1,2})?$",
    # Metadata bắt buộc cho mỗi container.
    "required_fields": ["name", "title", "originator", "suitability",
                        "revision", "date"],
    # Phân lớp suitability theo trạng thái CDE (để kiểm tính nhất quán).
    "wip_codes": ["S0"],
    "shared_codes": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"],
    "published_codes_prefix": ["A", "B"],   # A1..B9
    "published_codes_extra": ["CR"],
    # Số phần tối thiểu khi tách tên bằng '-' (cấu trúc ISO 19650).
    "min_name_fields": 6,
}

# --- Dò cột linh hoạt / flexible column aliases ----------------------------
ALIASES = {
    "name": ["file name", "filename", "file", "name", "document name",
             "document number", "container", "container id", "container name",
             "doc ref", "reference"],
    "title": ["title", "document title", "description", "sheet name"],
    "originator": ["originator", "author", "org", "organisation", "organization",
                   "company", "producer", "task team"],
    "suitability": ["suitability", "status", "suitability code", "status code",
                    "s-code", "scode"],
    "revision": ["revision", "rev", "version"],
    "state": ["state", "cde state", "workflow", "stage", "container state",
              "cde"],
    "date": ["date", "issue date", "revision date", "date issued", "modified",
             "last modified"],
}

STATE_NORMAL = {
    "wip": "WIP", "work in progress": "WIP", "s0": "WIP",
    "shared": "Shared", "share": "Shared",
    "published": "Published", "publish": "Published", "issued": "Published",
    "archived": "Archived", "archive": "Archived",
}


def load_rules(path: str | None) -> dict:
    rules = {k: (v[:] if isinstance(v, list) else v)
             for k, v in DEFAULT_RULES.items()}
    if not path:
        return rules
    try:
        import yaml
    except ImportError:
        print("ERROR: --rules cần pyyaml (pip install pyyaml)", file=sys.stderr)
        sys.exit(2)
    user = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    rules.update(user)
    return rules


def autodetect(headers: list[str]) -> dict:
    lower = {h.lower().strip(): h for h in headers}
    found = {}
    for key, cands in ALIASES.items():
        for c in cands:
            if c in lower:
                found[key] = lower[c]
                break
    return found


def is_published(code: str, rules: dict) -> bool:
    return (any(code.startswith(p) and code[1:].isdigit()
                for p in rules["published_codes_prefix"])
            or code in rules["published_codes_extra"])


def suitability_class(code: str, rules: dict) -> str:
    if code in rules["wip_codes"]:
        return "WIP"
    if code in rules["shared_codes"]:
        return "Shared"
    if is_published(code, rules):
        return "Published"
    return "?"


def audit_row(rec: dict, rules: dict) -> dict:
    """Trả về {check: bool} + danh sách message lỗi cho 1 container."""
    checks: dict[str, bool] = {}
    msgs: list[str] = []

    # 1) metadata đầy đủ
    missing = [f for f in rules["required_fields"] if not rec.get(f)]
    checks["metadata_complete"] = not missing
    if missing:
        msgs.append("thiếu: " + ", ".join(missing))

    # 2) cấu trúc tên (nhẹ — chi tiết field xem iso19650-naming-check)
    name = rec.get("name", "")
    n_fields = len(name.split("-")) if name else 0
    checks["name_structured"] = n_fields >= rules["min_name_fields"]
    if name and not checks["name_structured"]:
        msgs.append(f"tên chỉ {n_fields} trường (<{rules['min_name_fields']})")

    # 3) suitability hợp lệ
    suit = rec.get("suitability", "")
    checks["suitability_valid"] = bool(suit) and suit in rules["suitability_allowed"]
    if suit and not checks["suitability_valid"]:
        msgs.append(f"suitability '{suit}' không thuộc danh mục")

    # 4) revision hợp lệ
    rev = rec.get("revision", "")
    checks["revision_valid"] = bool(rev) and bool(re.match(rules["revision_pattern"], rev))
    if rev and not checks["revision_valid"]:
        msgs.append(f"revision '{rev}' sai định dạng")

    # 5) date ISO 8601
    d = rec.get("date", "")
    ok_date = False
    if d:
        try:
            date.fromisoformat(d[:10])
            ok_date = True
        except ValueError:
            ok_date = False
    checks["date_valid"] = ok_date
    if d and not ok_date:
        msgs.append(f"date '{d}' không phải ISO 8601 (YYYY-MM-DD)")

    # 6) nhất quán trạng thái CDE ↔ suitability ↔ revision
    state = rec.get("state", "")
    consistent = True
    if state and checks["suitability_valid"]:
        s_class = suitability_class(suit, rules)
        if s_class != "?" and s_class != state:
            consistent = False
            msgs.append(f"trạng thái '{state}' nhưng suitability '{suit}' thuộc lớp {s_class}")
        if checks["revision_valid"]:
            want = "C" if state == "Published" else "P"
            if not rev.startswith(want):
                consistent = False
                msgs.append(f"trạng thái '{state}' nên dùng revision '{want}xx', đang '{rev}'")
    checks["state_consistent"] = consistent

    return {"checks": checks, "msgs": msgs}


def read_register(path: Path, overrides: dict) -> tuple[list[dict], dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        cols = autodetect(headers)
        cols.update({k: v for k, v in overrides.items() if v})
        if "name" not in cols and "suitability" not in cols:
            print(f"ERROR: không dò được cột chính trong {headers}. "
                  f"Dùng --name-col/--suitability-col…", file=sys.stderr)
            sys.exit(2)
        records = []
        for row in reader:
            rec = {}
            for key, col in cols.items():
                rec[key] = (row.get(col) or "").strip()
            if "state" in rec:
                rec["state"] = STATE_NORMAL.get(rec["state"].lower(), rec["state"])
            records.append(rec)
    return records, cols


def read_expected(path: Path) -> set[str]:
    names = set()
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        col = autodetect(reader.fieldnames or []).get("name")
        if not col:
            col = (reader.fieldnames or ["name"])[0]
        for row in reader:
            v = (row.get(col) or "").strip()
            if v:
                names.add(v)
    return names


CHECK_LABELS = {
    "metadata_complete": "Metadata đầy đủ",
    "name_structured": "Tên có cấu trúc",
    "suitability_valid": "Suitability hợp lệ",
    "revision_valid": "Revision hợp lệ",
    "date_valid": "Date ISO 8601",
    "state_consistent": "Nhất quán trạng thái",
}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="ISO 19650 project conformance audit.")
    ap.add_argument("register", help="CDE register CSV")
    ap.add_argument("--rules", help="YAML ghi đè quy tắc mặc định")
    ap.add_argument("--expected", help="CSV danh sách container kỳ vọng (MIDP) để đối chiếu")
    ap.add_argument("--name-col")
    ap.add_argument("--suitability-col")
    ap.add_argument("--revision-col")
    ap.add_argument("--state-col")
    ap.add_argument("--date-col")
    ap.add_argument("--title-col")
    ap.add_argument("--originator-col")
    ap.add_argument("--threshold", type=float, default=100.0,
                    help="Ngưỡng %% đạt để exit 0 (mặc định 100)")
    ap.add_argument("--csv", dest="csv_out", help="Ghi findings ra CSV")
    ap.add_argument("--json", action="store_true", help="Xuất JSON")
    args = ap.parse_args(argv)

    path = Path(args.register)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.register}", file=sys.stderr)
        return 2

    rules = load_rules(args.rules)
    overrides = {
        "name": args.name_col, "suitability": args.suitability_col,
        "revision": args.revision_col, "state": args.state_col,
        "date": args.date_col, "title": args.title_col,
        "originator": args.originator_col,
    }
    records, cols = read_register(path, overrides)
    if not records:
        print("Register rỗng — không có container nào.", file=sys.stderr)
        return 2

    # audit từng container
    results = [audit_row(r, rules) for r in records]
    total = len(results)
    check_keys = list(CHECK_LABELS)
    tally = {k: 0 for k in check_keys}
    fully_ok = 0
    findings = []
    for rec, res in zip(records, results):
        for k in check_keys:
            if res["checks"].get(k):
                tally[k] += 1
        ok = all(res["checks"].get(k) for k in check_keys)
        fully_ok += ok
        if not ok:
            findings.append({
                "name": rec.get("name", ""),
                "state": rec.get("state", ""),
                "suitability": rec.get("suitability", ""),
                "revision": rec.get("revision", ""),
                "issues": "; ".join(res["msgs"]),
            })

    conformance = round(100.0 * fully_ok / total, 1)

    # đối chiếu MIDP (nếu có)
    missing_expected: list[str] = []
    if args.expected:
        exp = read_expected(Path(args.expected))
        have = {r.get("name", "") for r in records}
        missing_expected = sorted(exp - have)

    # rollups
    by_state: dict[str, int] = {}
    by_suit: dict[str, int] = {}
    for r in records:
        by_state[r.get("state", "") or "(trống)"] = by_state.get(r.get("state", "") or "(trống)", 0) + 1
        by_suit[r.get("suitability", "") or "(trống)"] = by_suit.get(r.get("suitability", "") or "(trống)", 0) + 1

    summary = {
        "containers": total,
        "fully_conformant": fully_ok,
        "conformance_pct": conformance,
        "checks": {CHECK_LABELS[k]: {"pass": tally[k],
                                     "pct": round(100.0 * tally[k] / total, 1)}
                   for k in check_keys},
        "by_state": by_state,
        "by_suitability": by_suit,
        "missing_from_expected": missing_expected,
        "findings": findings,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"ISO 19650 project audit — {path.name}")
        print(f"Cột dò được / columns: {cols}")
        print(f"\nContainer: {total}   |   Đạt hoàn toàn / fully conformant: "
              f"{fully_ok} ({conformance}%)")
        print("\nĐiểm theo hạng mục / conformance by check:")
        for k in check_keys:
            bar_pct = round(100.0 * tally[k] / total, 1)
            print(f"  {CHECK_LABELS[k]:22s} {tally[k]:3d}/{total}  ({bar_pct}%)")
        print("\nTheo trạng thái CDE / by state: " +
              ", ".join(f"{k}={v}" for k, v in by_state.items()))
        if missing_expected:
            print(f"\n⚠ Thiếu so với MIDP kỳ vọng ({len(missing_expected)}): " +
                  ", ".join(missing_expected[:10]) +
                  (" …" if len(missing_expected) > 10 else ""))
        if findings:
            print(f"\nContainer chưa đạt ({len(findings)}):")
            for f in findings:
                print(f"  ✗ {f['name'] or '(không tên)'}  [{f['state']}/"
                      f"{f['suitability']}/{f['revision']}]")
                print(f"      {f['issues']}")
        else:
            print("\n✓ Mọi container đạt tất cả hạng mục.")

    if args.csv_out:
        with open(args.csv_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["name", "state", "suitability",
                                               "revision", "issues"])
            w.writeheader()
            w.writerows(findings)
        print(f"\nĐã ghi findings → {args.csv_out}")

    return 0 if conformance >= args.threshold and not missing_expected else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
