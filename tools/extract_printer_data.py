#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json

def mk(prefix, rel):
    s = rel.strip("/").replace("/", "_").replace("-", "_").replace(".", "_")
    s = re.sub(r"[^A-Za-z0-9_]+", "_", s).upper()
    return f"{prefix}_{s[:80]}"

def main():
    if len(sys.argv) < 3:
        print("usage: extract_printer_data.py <dump_root> <out_json>")
        return 2
    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    # Look for mnt/UDISK/printer_data anywhere (case-insensitive)
    pd_roots = []
    for p in dump_root.rglob("*"):
        if p.is_dir():
            rel = p.relative_to(dump_root).as_posix().lower()
            if rel.endswith("mnt/udisk/printer_data") or rel.endswith("mnt/udisk/printer_data/") or rel.endswith("mnt/udisk/printer_data".lower()):
                pd_roots.append(p)
    # Fallback: direct path
    fallback = dump_root/"mnt"/"UDISK"/"printer_data"
    if fallback.exists() and fallback.is_dir() and fallback not in pd_roots:
        pd_roots.append(fallback)

    out = {"meta": {"dump_root": str(dump_root)}, "printer_data": {"roots": ["/"+r.relative_to(dump_root).as_posix() for r in pd_roots], "items": {}}}

    for r in pd_roots:
        for f in r.rglob("*"):
            if not f.is_file():
                continue
            rel = "/" + f.relative_to(dump_root).as_posix()
            rl = rel.lower()
            # Categorize
            cat = "misc"
            if "/config/" in rl or rl.endswith((".cfg",".conf",".ini",".json",".yaml",".yml")):
                cat = "config"
            if "/macros/" in rl or "macro" in rl or rl.endswith((".gcode",".gc")):
                cat = "macros"
            if "/web/" in rl or "/ui/" in rl or rl.endswith((".js",".html",".css",".map")):
                cat = "webui"
            if rl.endswith((".db",".sqlite",".sqlite3")) or "/database/" in rl or "/db/" in rl:
                cat = "database"
            key = mk("PD", rel)
            out["printer_data"]["items"][key] = {"path": rel, "category": cat, "name": f.name}
    dump_json(out_json, out)
    print(f"Wrote {out_json} (roots={len(pd_roots)}, items={len(out['printer_data']['items'])})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
