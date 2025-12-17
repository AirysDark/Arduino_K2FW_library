#!/usr/bin/env python3
import sys
from pathlib import Path
from _gen_common import load_json, safe_cpp, safe_ident, write_header

def emit_count_from_array(array_name: str) -> str:
    # Prefer sizeof-based counts to avoid ordering/scope issues.
    return f"inline constexpr size_t {array_name.upper()}_COUNT = sizeof({array_name}) / sizeof({array_name}[0]);\n"


def flatten_motion(obj, prefix=""):
    # output tuples (KEY, value_as_str)
    out = []
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k in ("meta","warnings","notes"):
                continue
            kk = f"{prefix}{k}" if prefix else str(k)
            if isinstance(v, dict):
                out.extend(flatten_motion(v, kk + "_"))
            elif isinstance(v, list):
                out.append((kk, ",".join([str(x) for x in v])))
            else:
                out.append((kk, str(v)))
    return out

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_motion_limits_db.py <MotionConfig.json> <out_h>")
        return 2
    j = load_json(Path(sys.argv[1]))
    out_h = Path(sys.argv[2]).resolve()

    # try common root keys
    root = j.get("motion") if isinstance(j, dict) and isinstance(j.get("motion"), dict) else j
    root = root.get("limits") if isinstance(root, dict) and isinstance(root.get("limits"), dict) else root

    items = {}
    for k,v in flatten_motion(root):
        if not k: 
            continue
        key = safe_ident("MOTION_" + k)
        items[key] = v

    keys = sorted(items.keys())
    lines = []
    lines.append("#pragma once")
    lines.append("#include <Arduino.h>")
    lines.append("namespace K2 {")
    lines.append("struct MotionKV { const char* key; const char* value; };")
    lines.append(f"static const size_t K2_MOTION_KV_COUNT = {len(keys)};")
    lines.append("static const MotionKV K2_MOTION_KV[K2_MOTION_KV_COUNT] = {")
    for k in keys:
        lines.append(f'  {{ "{safe_cpp(k)}", "{safe_cpp(items[k])}" }},')
    lines.append("};")
    lines.append("} // namespace K2")
    write_header(out_h, lines)
    print("Wrote", out_h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
