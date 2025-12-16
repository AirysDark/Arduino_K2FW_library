#!/usr/bin/env python3
import sys
from pathlib import Path
from _gen_common import load_json, safe_cpp, safe_ident, write_header

def iter_services(obj):
    # Accept:
    # 1) {"services":[{"name":"ssh","port":22,"proto":"tcp"}]}
    # 2) {"services": {"SSH": {...}}}
    if isinstance(obj, dict):
        if isinstance(obj.get("services"), list):
            for s in obj["services"]:
                if isinstance(s, dict):
                    yield s.get("key") or s.get("id") or s.get("name"), s.get("host",""), s.get("port",""), s.get("proto","")
        elif isinstance(obj.get("services"), dict):
            for k,v in obj["services"].items():
                if isinstance(v, dict):
                    yield k, v.get("host",""), v.get("port",""), v.get("proto","")
        else:
            # attempt: treat top-level dict as services map if looks like it
            for k,v in obj.items():
                if k in ("meta","warnings","notes"): 
                    continue
                if isinstance(v, dict) and ("port" in v or "proto" in v):
                    yield k, v.get("host",""), v.get("port",""), v.get("proto","")
    elif isinstance(obj, list):
        for s in obj:
            if isinstance(s, dict):
                yield s.get("key") or s.get("id") or s.get("name"), s.get("host",""), s.get("port",""), s.get("proto","")

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_services_db.py <Services.json> <out_h>")
        return 2
    j = load_json(Path(sys.argv[1]))
    out_h = Path(sys.argv[2]).resolve()

    items = {}
    for name,host,port,proto in iter_services(j):
        if not name:
            continue
        key = safe_ident("SVC_" + str(name))
        items[key] = (str(host or ""), str(port or ""), str(proto or ""))

    keys = sorted(items.keys())
    lines = []
    lines.append("#pragma once")
    lines.append("#include <Arduino.h>")
    lines.append("namespace K2 {")
    lines.append("struct ServiceItem { const char* key; const char* host; const char* port; const char* proto; };")
    lines.append(f"static const size_t K2_SERVICE_COUNT = {len(keys)};")
    lines.append("static const ServiceItem K2_SERVICES[K2_SERVICE_COUNT] = {")
    for k in keys:
        host,port,proto = items[k]
        lines.append(f'  {{ "{safe_cpp(k)}", "{safe_cpp(host)}", "{safe_cpp(port)}", "{safe_cpp(proto)}" }},')
    lines.append("};")
    lines.append("} // namespace K2")
    write_header(out_h, lines)
    print("Wrote", out_h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
