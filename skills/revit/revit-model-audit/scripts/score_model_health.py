#!/usr/bin/env python3
"""
score_model_health.py — Chấm điểm sức khoẻ model Revit từ file metrics export.
                        Score Revit model health from a metrics export.

Đầu vào: CSV hai cột (metric,value) HOẶC JSON {metric: value}. So với ngưỡng
đỏ/vàng/xanh (theo references/model-health-checklist.md) và cho điểm 0–100.
Chỉ dùng thư viện chuẩn; --thresholds nhận JSON để ghi đè ngưỡng.
Input: 2-col CSV (metric,value) OR JSON {metric: value}. Scores each axis
red/yellow/green against thresholds and gives a 0–100 index. Stdlib only.

Usage:
    python score_model_health.py metrics.csv
    python score_model_health.py metrics.json --thresholds my_thresholds.json
Exit: 0 = xanh/vàng (ổn), 1 = có mục ĐỎ, 2 = usage / không đọc được file.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# (key, nhãn / label, yellow, red, đơn vị / unit)
# Tất cả "cao hơn = xấu hơn". Ngưỡng gợi ý — chỉnh theo quy mô dự án qua --thresholds.
METRICS = [
    ("file_size_mb", "Dung lượng file / File size", 150, 300, "MB"),
    ("warnings_total", "Tổng warning / Warnings", 300, 1000, ""),
    ("warnings_high", "Warning nghiêm trọng / HIGH warnings", 10, 50, ""),
    ("purgeable_count", "Purge được / Purgeable", 200, 1000, ""),
    ("cad_imports", "CAD imports (không phải link)", 1, 5, ""),
    ("in_place_families", "In-place families", 5, 20, ""),
    ("unused_views", "View không lên sheet / Unused views", 50, 200, ""),
    ("unused_view_templates", "View template thừa / Unused templates", 3, 10, ""),
    ("groups", "Model groups", 20, 50, ""),
    ("editable_worksets_max", "Workset editable tối đa/người", 5, 10, ""),
]
STATUS_MARK = {"red": "🔴", "yellow": "🟡", "green": "🟢"}
STATUS_SCORE = {"green": 2, "yellow": 1, "red": 0}


def load_metrics(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON metrics phải là một object {metric: value}")
        return {str(k).strip().lower(): v for k, v in data.items()}
    out: dict = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        for row in reader:
            if len(row) < 2:
                continue
            key = row[0].strip().lower()
            if key in ("metric", "key", "name") and not out:
                continue  # bỏ dòng header nếu có
            out[key] = row[1].strip()
    return out


def to_number(v):
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def classify(value: float, yellow: float, red: float) -> str:
    if value >= red:
        return "red"
    if value >= yellow:
        return "yellow"
    return "green"


def load_thresholds(path: str | None) -> dict:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {str(k).lower(): v for k, v in data.items()}


def score(metrics: dict, overrides: dict) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    counts = {"red": 0, "yellow": 0, "green": 0, "n/a": 0}
    earned = possible = 0
    for key, label, yellow, red, unit in METRICS:
        if key in overrides:
            yellow, red = overrides[key].get("yellow", yellow), overrides[key].get("red", red)
        raw = metrics.get(key)
        num = to_number(raw) if raw is not None and raw != "" else None
        if num is None:
            counts["n/a"] += 1
            rows.append({"key": key, "label": label, "value": "(n/a)",
                         "status": "n/a", "threshold": f"≥{yellow} / ≥{red}", "unit": unit})
            continue
        st = classify(num, yellow, red)
        counts[st] += 1
        earned += STATUS_SCORE[st]
        possible += 2
        val = int(num) if num.is_integer() else num
        rows.append({"key": key, "label": label, "value": f"{val}{(' ' + unit) if unit else ''}",
                     "status": st, "threshold": f"≥{yellow} / ≥{red}", "unit": unit})
    index = round(100 * earned / possible) if possible else None
    counts["index"] = index
    return rows, counts


def render(rows: list[dict], counts: dict) -> str:
    L = ["Revit model health — chấm điểm / score", ""]
    L.append(f"{'':2} {'Mục / Metric':38} {'Giá trị / Value':>16}  Ngưỡng (🟡/🔴)")
    L.append("-" * 82)
    for r in rows:
        mark = STATUS_MARK.get(r["status"], "·")
        L.append(f"{mark:2} {r['label'][:38]:38} {r['value']:>16}  {r['threshold']}")
    L.append("-" * 82)
    idx = counts.get("index")
    idx_s = f"{idx}/100" if idx is not None else "n/a"
    L.append(f"🔴 {counts['red']}   🟡 {counts['yellow']}   🟢 {counts['green']}   "
             f"n/a {counts['n/a']}   |   Health index: {idx_s}")
    if counts["red"]:
        L.append("→ Có mục ĐỎ: ưu tiên xử lý trước mốc phát hành "
                 "(purge, đổi CAD import→link, sửa warning HIGH).")
    return "\n".join(L)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Score Revit model health from a metrics export.")
    ap.add_argument("metrics", help="CSV (metric,value) hoặc JSON {metric: value}")
    ap.add_argument("--thresholds", help="JSON ghi đè ngưỡng {key: {yellow, red}}")
    args = ap.parse_args(argv)

    path = Path(args.metrics)
    if not path.is_file():
        print(f"ERROR: không tìm thấy: {args.metrics}", file=sys.stderr)
        return 2
    try:
        metrics = load_metrics(path)
        overrides = load_thresholds(args.thresholds)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: không đọc được dữ liệu: {exc}", file=sys.stderr)
        return 2

    rows, counts = score(metrics, overrides)
    print(render(rows, counts))
    return 1 if counts["red"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
