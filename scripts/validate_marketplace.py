#!/usr/bin/env python3
"""
validate_marketplace.py — Kiểm tính hợp lệ của marketplace & plugin manifests.
                          Validate the plugin marketplace and plugin manifests.

Chỉ dùng thư viện chuẩn. / Stdlib only.

Kiểm:
  * .claude-plugin/marketplace.json parse được, có name/owner/plugins.
  * Mỗi plugin trong marketplace có source trỏ tới thư mục tồn tại.
  * Mỗi thư mục plugin có .claude-plugin/plugin.json hợp lệ, name khớp.
  * Không lệch giữa marketplace và các thư mục trong plugins/.

Usage:
    python scripts/validate_marketplace.py
Exit: 0 = PASS, 1 = có lỗi.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKET = ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = ROOT / "plugins"


def fail(errors: list[str], msg: str):
    errors.append(msg)


def main() -> int:
    errors: list[str] = []

    if not MARKET.is_file():
        print(f"ERROR: thiếu {MARKET.relative_to(ROOT)}", file=sys.stderr)
        return 1
    try:
        market = json.loads(MARKET.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: marketplace.json không hợp lệ: {exc}", file=sys.stderr)
        return 1

    for key in ("name", "owner", "plugins"):
        if key not in market:
            fail(errors, f"marketplace.json thiếu khoá '{key}'")
    plugins = market.get("plugins", [])
    if not isinstance(plugins, list) or not plugins:
        fail(errors, "marketplace.json: 'plugins' phải là list không rỗng")

    listed_names: set[str] = set()
    for i, entry in enumerate(plugins):
        if not isinstance(entry, dict):
            fail(errors, f"plugins[{i}] phải là object")
            continue
        name = entry.get("name")
        source = entry.get("source")
        if not name:
            fail(errors, f"plugins[{i}] thiếu 'name'")
        if not source:
            fail(errors, f"plugin '{name}' thiếu 'source'")
            continue
        listed_names.add(name)

        # source dạng chuỗi đường dẫn tương đối "./plugins/<name>"
        if isinstance(source, str):
            src_dir = (ROOT / source).resolve()
            if not src_dir.is_dir():
                fail(errors, f"plugin '{name}': source '{source}' không tồn tại")
                continue
            manifest = src_dir / ".claude-plugin" / "plugin.json"
            if not manifest.is_file():
                fail(errors, f"plugin '{name}': thiếu {manifest.relative_to(ROOT)}")
                continue
            try:
                pj = json.loads(manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                fail(errors, f"plugin '{name}': plugin.json lỗi JSON: {exc}")
                continue
            if pj.get("name") != name:
                fail(errors, f"plugin '{name}': plugin.json name='{pj.get('name')}' "
                             f"không khớp marketplace/thư mục")
            if pj.get("name") != src_dir.name:
                fail(errors, f"plugin '{name}': name không khớp tên thư mục '{src_dir.name}'")
            # skills phải nằm ở gốc plugin, không trong .claude-plugin
            if (src_dir / ".claude-plugin" / "skills").exists():
                fail(errors, f"plugin '{name}': 'skills/' không được nằm trong .claude-plugin/")

    # đối chiếu thư mục plugins/ với danh sách marketplace
    if PLUGINS_DIR.is_dir():
        on_disk = {p.name for p in PLUGINS_DIR.iterdir()
                   if p.is_dir() and (p / ".claude-plugin" / "plugin.json").is_file()}
        missing = on_disk - listed_names
        extra = listed_names - on_disk
        for m in sorted(missing):
            fail(errors, f"plugin '{m}' có trên đĩa nhưng chưa liệt kê trong marketplace.json")
        for e in sorted(extra):
            fail(errors, f"plugin '{e}' trong marketplace.json nhưng không có thư mục")

    if errors:
        print(f"FAIL: {len(errors)} lỗi manifest:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: marketplace '{market['name']}' hợp lệ với {len(plugins)} plugin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
