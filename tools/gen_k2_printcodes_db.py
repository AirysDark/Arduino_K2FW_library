#!/usr/bin/env python3
import sys
from pathlib import Path
from _gen_common import load_json, safe_cpp, safe_ident, write_header

def iter_codes(obj):
    # Accept:
    # 1) {"codes": {"M_104": {...}}} or {"print_codes": {...}}
    # 2) {"M_104": {...}, "G_28": {...}} (flat)
    # 3) {"items":[{"key":"M_104",...}]}
    if isinstance(obj, dict):
        src = None
        for k in ("codes","print_codes","mg","m_g","items_by_key"):
            if isinstance(obj.get(k), dict):
                src = obj[k]
                break
        if src is None:
            src = obj
        for k,v in src.items():
            if k in ("meta","warnings","notes","images","partitions","paths","macros"):
                continue
            ku = str(k).upper()
            if not (ku.startswith("M_") or ku.startswith("G_")):
                continue
            if isinstance(v, dict):
                meaning = v.get("meaning") or v.get("desc") or v.get("description") or ""
                ctx = v.get("context") or v.get("notes") or ""
                used = v.get("used_by_macros") or v.get("macros") or []
                if not isinstance(used, list):
                    used = []
                yield k, meaning, ctx, used
            else:
                yield k, str(v), "", []
        if isinstance(obj.get("items"), list):
            for it in obj["items"]:
                if isinstance(it, dict):
                    k = it.get("key") or it.get("id")
                    if not k: 
                        continue
                    ku = str(k).upper()
                    if ku.startswith("M_") or ku.startswith("G_"):
                        yield k, it.get("meaning") or it.get("desc") or "", it.get("context") or "", it.get("used_by_macros") or []
    elif isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                k = it.get("key") or it.get("id")
                if not k: 
                    continue
                ku = str(k).upper()
                if ku.startswith("M_") or ku.startswith("G_"):
                    yield k, it.get("meaning") or it.get("desc") or "", it.get("context") or "", it.get("used_by_macros") or []

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_printcodes_db.py <PrintCodes.json> <out_h>")
        return 2
    j = load_json(Path(sys.argv[1]))
    out_h = Path(sys.argv[2]).resolve()

    items = {}
    for k,meaning,ctx,used in iter_codes(j):
        kk = safe_ident(k)
        used_s = ",".join([str(x) for x in used]) if isinstance(used, list) else ""
        items[kk] = (meaning, ctx, used_s)

    keys = sorted(items.keys())
    lines = []
    lines.append("#pragma once")
    lines.append("#include <Arduino.h>")
    lines.append("namespace K2 {")
    lines.append("struct PrintCode { const char* key; const char* meaning; const char* context; const char* used_by_macros; };")
    lines.append(f"static const size_t K2_PRINTCODE_COUNT = {len(keys)};")
    lines.append("static const PrintCode K2_PRINTCODES[K2_PRINTCODE_COUNT] = {")
    for k in keys:
        meaning,ctx,used_s = items[k]
        lines.append(f'  {{ "{safe_cpp(k)}", "{safe_cpp(meaning)}", "{safe_cpp(ctx)}", "{safe_cpp(used_s)}" }},')
    lines.append("};")
    lines.append("} // namespace K2")
    write_header(out_h, lines)
    print("Wrote", out_h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
