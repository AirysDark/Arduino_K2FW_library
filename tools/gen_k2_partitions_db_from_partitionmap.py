#!/usr/bin/env python3
import sys, json
from pathlib import Path

def safe_cpp(s: str) -> str:
    s = (s or "").replace("\\", "\\\\").replace('"', '\\"')
    return s

def main():
    if len(sys.argv) < 3:
        print("usage: gen_k2_partitions_db_from_partitionmap.py <PartitionMap.json> <out_h>")
        return 2

    pm = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    parts = pm.get("partitions", {})
    if not isinstance(parts, dict):
        print("ERROR: PartitionMap.json format unexpected: 'partitions' not a dict")
        return 1

    items = []
    for key, p in parts.items():
        if not isinstance(p, dict): 
            continue
        items.append({
            "key": key,
            "name": p.get("name","") or "",
            "device": p.get("device","") or "",
            "role": p.get("role","unknown") or "unknown",
            "slot": int(p.get("slot",-1)),
            "critical": bool(p.get("critical", False)),
            "updateable": bool(p.get("updateable", False)),
            "first_lba": int(p.get("first_lba", 0)) if "first_lba" in p else 0,
            "last_lba": int(p.get("last_lba", 0)) if "last_lba" in p else 0,
        })

    items.sort(key=lambda x: (x["device"], x["key"]))

    out = []
    out.append("#pragma once")
    out.append("#include <Arduino.h>")
    out.append("namespace K2 {")
    out.append("struct Partition {")
    out.append("  const char* key;")
    out.append("  const char* name;")
    out.append("  const char* device;")
    out.append("  const char* role;")
    out.append("  int8_t slot;")
    out.append("  bool critical;")
    out.append("  bool updateable;")
    out.append("  uint64_t first_lba;")
    out.append("  uint64_t last_lba;")
    out.append("};")
    out.append(f"static const size_t K2_PART_COUNT = {len(items)};")
    out.append("static const Partition K2_PARTS[K2_PART_COUNT] = {")
    for p in items:
        out.append(
            f'  {{ "{safe_cpp(p["key"])}", "{safe_cpp(p["name"])}", "{safe_cpp(p["device"])}", "{safe_cpp(p["role"])}", '
            f'(int8_t){p["slot"]}, {"true" if p["critical"] else "false"}, {"true" if p["updateable"] else "false"}, '
            f'{p["first_lba"]}ULL, {p["last_lba"]}ULL }},'
        )
    out.append("};")
    out.append("} // namespace K2")

    out_h = Path(sys.argv[2]).resolve()
    out_h.parent.mkdir(parents=True, exist_ok=True)
    out_h.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("Wrote", out_h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
