#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, read_text_loose, is_probably_text, dump_json

def guess_ok_token(_text: str) -> str:
    return "ok"

def make_gc_key(name: str, idx: int) -> str:
    n = re.sub(r"[^A-Za-z0-9_]+", "_", name).upper().strip("_")
    if n and len(n) <= 24:
        return "GC_" + n
    return f"GC_{idx:05d}"

def main():
    if len(sys.argv) < 3:
        print("usage: extract_gcode_macros.py <dump_root> <out_json>")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    macros = {}
    idx = 1

    for f in iter_files(dump_root):
        rel = f.relative_to(dump_root).as_posix()
        rel_l = rel.lower()

        if not (rel_l.endswith(".gcode") or rel_l.endswith(".gc") or "macro" in rel_l or "start" in rel_l or "end" in rel_l):
            continue
        if not is_probably_text(f):
            continue

        try:
            txt = read_text_loose(f, limit_bytes=500_000)
        except Exception:
            continue

        if not re.search(r"(?m)^(G0|G1|G28|G29|M104|M109|M140|M190|M106|M107)\b", txt.strip()):
            continue

        name = Path(rel).stem
        key = make_gc_key(name, idx); idx += 1
        macros[key] = {
          "name": name,
          "source": "/" + rel,
          "text": txt if txt.endswith("\n") else (txt + "\n"),
          "ok": guess_ok_token(txt)
        }

        if len(macros) >= 600:
            break

    out = {"meta": {"dump_root": str(dump_root)}, "gcodes": macros}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(macros)} macros)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
