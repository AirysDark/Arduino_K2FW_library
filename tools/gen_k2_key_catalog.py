#!/usr/bin/env python3
import sys, json
from pathlib import Path
from _gen_common import safe_cpp, safe_ident, write_header, load_json

def collect_keys_from_json(j):
    keys = set()
    if isinstance(j, dict):
        for k,v in j.items():
            if k in ("meta","warnings","notes","images"):
                continue
            if isinstance(v, dict):
                # if dict-of-keys pattern
                for kk in v.keys():
                    if isinstance(kk, str) and (kk.startswith("PART_") or kk.startswith("PATH_") or kk.startswith("GC_") or kk.startswith("M_") or kk.startswith("G_") or kk.startswith("CMD_")):
                        keys.add(kk)
            if isinstance(k, str) and (k.startswith("PART_") or k.startswith("PATH_") or k.startswith("GC_") or k.startswith("M_") or k.startswith("G_") or k.startswith("CMD_")):
                keys.add(k)
        # special common containers
        for container in ("partitions","paths","macros","codes","commands"):
            if isinstance(j.get(container), dict):
                for kk in j[container].keys():
                    if isinstance(kk, str):
                        keys.add(kk)
    elif isinstance(j, list):
        for it in j:
            if isinstance(it, dict):
                k = it.get("key") or it.get("id")
                if isinstance(k, str):
                    keys.add(k)
    return keys

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_key_catalog.py <blueprint_dir_or_KeyCatalog.json> <out_h>")
        return 2

    src = Path(sys.argv[1]).resolve()
    out_h = Path(sys.argv[2]).resolve()

    keys = set()
    if src.is_dir():
        for name in ("PartitionMap.json","Paths.json","GcodeMacros.json","PrintCodes.json","CommandScripts.json"):
            p = src / name
            if p.exists():
                try:
                    j = load_json(p)
                    keys |= collect_keys_from_json(j)
                except Exception:
                    pass
        kc = src / "KeyCatalog.json"
        if kc.exists():
            try:
                j = load_json(kc)
                if isinstance(j, dict) and isinstance(j.get("keys"), list):
                    keys |= set([str(x) for x in j["keys"]])
            except Exception:
                pass
    else:
        j = load_json(src)
        if isinstance(j, dict) and isinstance(j.get("keys"), list):
            keys |= set([str(x) for x in j["keys"]])
        else:
            keys |= collect_keys_from_json(j)

    keys = sorted(set([safe_ident(k) for k in keys if k]))

    lines = []
    lines.append("#pragma once")
    lines.append("#include <Arduino.h>")
    lines.append("namespace K2 {")
    lines.append("enum KeyID : uint32_t {")
    for i,k in enumerate(keys):
        lines.append(f"  {k} = {i+1},")
    lines.append("};")
    lines.append(f"static const size_t K2_KEY_COUNT = {len(keys)};")
    lines.append("} // namespace K2")
    write_header(out_h, lines)
    print("Wrote", out_h)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
