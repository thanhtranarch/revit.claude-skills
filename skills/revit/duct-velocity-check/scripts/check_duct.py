#!/usr/bin/env python3
"""
check_duct.py — Kiểm vận tốc & tỷ lệ cạnh ống gió từ duct schedule.
                Check duct air velocity & aspect ratio from a duct schedule.

Tính vận tốc = lưu lượng / tiết diện; cờ vượt vận tốc (ồn/áp cao) và tỷ lệ cạnh
W:H quá lớn (khó chế tạo, tổn thất áp). Hỗ trợ ống chữ nhật (W×H) và tròn (Ø).
Chỉ dùng thư viện chuẩn; --rules nhận JSON để ghi đè ngưỡng.

Usage:
    python check_duct.py ducts.csv
    python check_duct.py ducts.csv --airflow-unit cfm --rules limits.json
Exit: 0 = đạt, 1 = có duct vượt ngưỡng, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

DEFAULTS = {"max_velocity": 8.0, "warn_velocity": 6.0, "max_aspect": 4.0}
# hệ số đổi lưu lượng về m³/s
FLOW_TO_M3S = {"l/s": 1e-3, "lps": 1e-3, "cfm": 0.000471947, "m3/h": 1 / 3600, "m3/s": 1.0}

ID_COLS = ["duct id", "id", "tag", "mark", "ref", "no"]
W_COLS = ["width", "w", "duct width"]
H_COLS = ["height", "h", "duct height"]
D_COLS = ["diameter", "dia", "ø", "round"]
SIZE_COLS = ["size", "dimensions", "duct size"]
FLOW_COLS = ["airflow", "flow", "air flow", "cfm", "l/s", "lps", "volume flow", "q"]
SYS_COLS = ["system", "service", "type", "duct type"]


def find_col(headers, aliases):
    low = {h.strip().lower(): h for h in headers}
    for a in aliases:
        if a in low:
            return low[a]
    return None


def num(s):
    s = re.sub(r"[^\d.\-]", "", (s or "").replace(",", ""))
    try:
        return float(s) if s not in ("", "-", ".", "-.") else None
    except ValueError:
        return None


def parse_size(s: str):
    """Trả (w, h, d) mm từ ô Size như '600x400' hoặc 'Ø400'."""
    s = (s or "").strip()
    m = re.search(r"(\d+(?:\.\d+)?)\s*[x×X]\s*(\d+(?:\.\d+)?)", s)
    if m:
        return float(m.group(1)), float(m.group(2)), None
    m = re.search(r"[Øø]\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:dia|round)", s, re.I)
    if m:
        d = m.group(1) or m.group(2)
        return None, None, float(d)
    return None, None, None


def geometry(row, cols):
    w = num(row.get(cols["w"])) if cols["w"] else None
    h = num(row.get(cols["h"])) if cols["h"] else None
    d = num(row.get(cols["d"])) if cols["d"] else None
    if (w is None or h is None) and d is None and cols["size"]:
        sw, sh, sd = parse_size(row.get(cols["size"]) or "")
        w, h, d = w or sw, h or sh, d or sd
    if w and h:
        area = (w / 1000) * (h / 1000)
        aspect = max(w, h) / min(w, h)
        label = f"{int(w)}x{int(h)}"
    elif d:
        area = math.pi * (d / 1000) ** 2 / 4
        aspect = 1.0
        label = f"Ø{int(d)}"
    else:
        return None, None, "(no size)"
    return area, aspect, label


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check duct velocity & aspect ratio.")
    ap.add_argument("csv", help="CSV duct schedule")
    ap.add_argument("--airflow-unit", default="l/s", choices=sorted(FLOW_TO_M3S),
                    help="Đơn vị lưu lượng (mặc định l/s)")
    ap.add_argument("--rules", help="JSON ghi đè ngưỡng {max_velocity, warn_velocity, max_aspect}")
    args = ap.parse_args(argv)

    path = Path(args.csv)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.csv}", file=sys.stderr)
        return 2
    rules = {**DEFAULTS}
    if args.rules:
        try:
            rules.update(json.loads(Path(args.rules).read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: không đọc được --rules: {exc}", file=sys.stderr)
            return 2

    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        rows = list(reader)
    cols = {
        "id": find_col(headers, ID_COLS), "w": find_col(headers, W_COLS),
        "h": find_col(headers, H_COLS), "d": find_col(headers, D_COLS),
        "size": find_col(headers, SIZE_COLS), "flow": find_col(headers, FLOW_COLS),
        "sys": find_col(headers, SYS_COLS),
    }
    if not cols["flow"]:
        print(f"ERROR: không dò được cột lưu lượng trong {headers}", file=sys.stderr)
        return 2
    factor = FLOW_TO_M3S[args.airflow_unit]

    print(f"Duct velocity check — ngưỡng / limits: v_max={rules['max_velocity']} m/s, "
          f"cảnh báo/warn>{rules['warn_velocity']}, aspect_max={rules['max_aspect']}:1  "
          f"(flow {args.airflow_unit})")
    print(f"{'Duct':10} {'System':10} {'Size':10} {'Flow':>8} {'Vel m/s':>8} {'Aspect':>7}  Status")
    print("-" * 74)

    n_over = n_warn = 0
    for i, r in enumerate(rows, 1):
        did = (r.get(cols["id"]) or f"#{i}").strip() if cols["id"] else f"#{i}"
        system = (r.get(cols["sys"]) or "").strip() if cols["sys"] else ""
        flow = num(r.get(cols["flow"]))
        area, aspect, label = geometry(r, cols)
        tags = []
        vel = None
        if area and flow is not None:
            vel = flow * factor / area
            if vel > rules["max_velocity"]:
                tags.append("OVER-VELOCITY"); n_over += 1
            elif vel > rules["warn_velocity"]:
                tags.append("high-vel"); n_warn += 1
        else:
            tags.append("no data")
        if aspect and aspect > rules["max_aspect"]:
            tags.append(f"aspect {aspect:.1f}:1"); n_over += 1
        status = ", ".join(tags) if tags else "OK"
        vel_s = f"{vel:.2f}" if vel is not None else "—"
        asp_s = f"{aspect:.1f}" if aspect else "—"
        flow_s = f"{flow:,.0f}" if flow is not None else "—"
        print(f"{did[:10]:10} {system[:10]:10} {label[:10]:10} {flow_s:>8} {vel_s:>8} {asp_s:>7}  {status}")

    print("-" * 74)
    print(f"{'⛔' if n_over else '✅'} vượt ngưỡng / violations: {n_over}   "
          f"🟡 cảnh báo / warnings: {n_warn}   trên {len(rows)} duct")
    return 1 if n_over else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
