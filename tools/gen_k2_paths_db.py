#!/usr/bin/env python3
import sys
from pathlib import Path
from _gen_common import load_json, safe_cpp, safe_ident, write_header

def emit_count_from_array(array_name: str) -> str:
    # Prefer sizeof-based counts to avoid ordering/scope issues.
    return f"inline constexpr size_t {array_name.upper()}_COUNT = sizeof({array_name}) / sizeof({array_name}[0]);\n"


def iter_paths(obj):
    # Accept:
    # 1) {"paths": {"PATH_X": {... or string}}}
    # 2) {"PATH_X": "..."} (flat dict)
    # 3) {"items":[{"key":"PATH_X","path":"/..."}]}
    if isinstance(obj, dict):
        if isinstance(obj.get("paths"), dict):
            for k,v in obj["paths"].items():
                if isinstance(v, dict):
                    yield k, v.get("path") or v.get("value") or v.get("v") or ""
                else:
                    yield k, v
            return
        if isinstance(obj.get("items"), list):
            for it in obj["items"]:
                if isinstance(it, dict):
                    yield it.get("key") or it.get("id"), it.get("path") or it.get("value") or ""
            return
        # flat dict
        for k,v in obj.items():
            if k in ("meta","warnings","notes"): 
                continue
            if isinstance(v, (str,int,float)):
                yield k, str(v)
            elif isinstance(v, dict) and ("path" in v or "value" in v):
                yield k, v.get("path") or v.get("value") or ""
    elif isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                yield it.get("key") or it.get("id"), it.get("path") or it.get("value") or ""

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_paths_db.py <Paths.json> <out_h>")
        return 2
    j = load_json(Path(sys.argv[1]))
    out_h = Path(sys.argv[2]).resolve()

    items = []
    for k,p in iter_paths(j):
        if not k or not p:
            continue
        items.append((safe_ident(k if k.startswith("PATH_") else f"PATH_{k}"), str(p)))
    items = sorted(dict(items).items(), key=lambda x: x[0])

    lines = []
    lines.append("#pragma once")
    lines.append("#include <Arduino.h>")
    lines.append("namespace K2 {")
    lines.append("struct PathItem { const char* key; const char* path; };")
    lines.append(f"static const size_t K2_PATH_COUNT = {len(items)};")
    lines.append("static const PathItem K2_PATHS[K2_PATH_COUNT] = {")
    for k,p in items:
        lines.append(f'  {{ "{safe_cpp(k)}", "{safe_cpp(p)}" }},')
    lines.append("};")
    lines.append("} // namespace K2")
    write_header(out_h, lines)
    print("Wrote", out_h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
