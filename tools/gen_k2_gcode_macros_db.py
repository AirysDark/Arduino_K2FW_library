#!/usr/bin/env python3
import sys
from pathlib import Path
from _gen_common import load_json, safe_cpp, safe_ident, write_header

def iter_macros(obj):
    # Accept:
    # 1) {"macros": {"GC_X": {"gcode":"...", "desc":"..."}}}
    # 2) {"GC_X": {...}} (flat)
    # 3) {"items":[{"key":"GC_X","gcode":"..."}]}
    if isinstance(obj, dict):
        src = obj.get("macros") if isinstance(obj.get("macros"), dict) else obj
        for k,v in src.items():
            if k in ("meta","warnings","notes","images","partitions","paths","codes"):
                continue
            if not str(k).upper().startswith("GC_"):
                continue
            if isinstance(v, dict):
                g = v.get("gcode") or v.get("value") or v.get("text") or ""
                d = v.get("desc") or v.get("description") or ""
                yield k, g, d
            elif isinstance(v, str):
                yield k, v, ""
        if isinstance(obj.get("items"), list):
            for it in obj["items"]:
                if isinstance(it, dict):
                    k = it.get("key") or it.get("id")
                    if k and str(k).upper().startswith("GC_"):
                        yield k, it.get("gcode") or it.get("value") or "", it.get("desc") or ""
    elif isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                k = it.get("key") or it.get("id")
                if k and str(k).upper().startswith("GC_"):
                    yield k, it.get("gcode") or it.get("value") or "", it.get("desc") or ""

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_gcode_macros_db.py <GcodeMacros.json> <out_h>")
        return 2
    j = load_json(Path(sys.argv[1]))
    out_h = Path(sys.argv[2]).resolve()

    items = {}
    for k,g,d in iter_macros(j):
        if not k or not g:
            continue
        kk = safe_ident(k)
        items[kk] = (g, d)

    keys = sorted(items.keys())
    lines = []
    lines.append("#pragma once")
    lines.append("#include <Arduino.h>")
    lines.append("namespace K2 {")
    lines.append("struct MacroItem { const char* key; const char* gcode; const char* desc; };")
    lines.append(f"static const size_t K2_MACRO_COUNT = {len(keys)};")
    lines.append("static const MacroItem K2_MACROS[K2_MACRO_COUNT] = {")
    for k in keys:
        g,d = items[k]
        lines.append(f'  {{ "{safe_cpp(k)}", "{safe_cpp(g)}", "{safe_cpp(d)}" }},')
    lines.append("};")
    lines.append("} // namespace K2")
    write_header(out_h, lines)
    print("Wrote", out_h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
