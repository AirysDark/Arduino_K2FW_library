#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, dump_json

def make_key(path_str: str) -> str:
    s = path_str.strip("/").replace("/", "_").replace("-", "_").replace(".", "_")
    s = re.sub(r"[^A-Za-z0-9_]+", "_", s).upper()
    return "PATH_" + s[:80]

def main():
    if len(sys.argv) < 3:
        print("usage: extract_paths.py <dump_root> <out_json>")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json = Path(sys.argv[2]).resolve()

    hot = ("etc","boot","usr","var","opt","home","root","overlay","data","userdata","mnt","www","srv")

    entries = {}
    for f in iter_files(dump_root):
        rel = f.relative_to(dump_root).as_posix()
        top = rel.split("/", 1)[0].lower()
        if top in hot:
            k = make_key(rel)
            if k not in entries:
                entries[k] = {"path": "/" + rel}

    out = {"meta": {"dump_root": str(dump_root)}, "paths": entries}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(entries)} paths)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
