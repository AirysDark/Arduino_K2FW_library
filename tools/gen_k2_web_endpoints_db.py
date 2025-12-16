#!/usr/bin/env python3
import sys
from pathlib import Path
from _gen_common import load_json, safe_cpp, safe_ident, write_header

def iter_endpoints(obj):
    # Accept:
    # 1) {"endpoints":[{"method":"GET","path":"/api/...","desc":"..."}]}
    # 2) {"endpoints": {"EP_X": {...}}}
    if isinstance(obj, dict):
        if isinstance(obj.get("endpoints"), list):
            for e in obj["endpoints"]:
                if isinstance(e, dict):
                    yield e.get("key") or e.get("id"), e.get("method",""), e.get("path",""), e.get("desc") or e.get("description") or ""
        elif isinstance(obj.get("endpoints"), dict):
            for k,v in obj["endpoints"].items():
                if isinstance(v, dict):
                    yield k, v.get("method",""), v.get("path",""), v.get("desc") or v.get("description") or ""
        else:
            # heuristic: any dict with method/path
            for k,v in obj.items():
                if k in ("meta","warnings","notes"): 
                    continue
                if isinstance(v, dict) and ("path" in v or "method" in v):
                    yield k, v.get("method",""), v.get("path",""), v.get("desc") or v.get("description") or ""
    elif isinstance(obj, list):
        for e in obj:
            if isinstance(e, dict):
                yield e.get("key") or e.get("id"), e.get("method",""), e.get("path",""), e.get("desc") or e.get("description") or ""

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_web_endpoints_db.py <WebHints.json> <out_h>")
        return 2
    j = load_json(Path(sys.argv[1]))
    out_h = Path(sys.argv[2]).resolve()

    items = {}
    idx = 0
    for key,method,path,desc in iter_endpoints(j):
        idx += 1
        if not path:
            continue
        k = key or f"EP_{idx}"
        kk = safe_ident("EP_" + str(k))
        items[kk] = (method or "", path, desc or "")

    keys = sorted(items.keys())
    lines = []
    lines.append("#pragma once")
    lines.append("#include <Arduino.h>")
    lines.append("namespace K2 {")
    lines.append("struct Endpoint { const char* key; const char* method; const char* path; const char* desc; };")
    lines.append(f"static const size_t K2_ENDPOINT_COUNT = {len(keys)};")
    lines.append("static const Endpoint K2_ENDPOINTS[K2_ENDPOINT_COUNT] = {")
    for k in keys:
        method,path,desc = items[k]
        lines.append(f'  {{ "{safe_cpp(k)}", "{safe_cpp(method)}", "{safe_cpp(path)}", "{safe_cpp(desc)}" }},')
    lines.append("};")
    lines.append("} // namespace K2")
    write_header(out_h, lines)
    print("Wrote", out_h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
