#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json

ENDPOINT_RE = re.compile(r"(?:fetch\(|axios\.|XMLHttpRequest|websocket|WebSocket|/api/|/printer/|/server/|/machine/|/v1/|/rpc)", re.I)
PATH_LIT_RE = re.compile(r"(?:(/api/[^\s'\"]+)|(/printer/[^\s'\"]+)|(/server/[^\s'\"]+)|(/machine/[^\s'\"]+))")

def main():
    if len(sys.argv) < 3:
        print("usage: extract_web_hints.py <dump_root> <out_json>")
        return 2
    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    endpoints = set()
    files = []

    for f in iter_files(dump_root):
        rel = "/" + f.relative_to(dump_root).as_posix()
        rl = rel.lower()
        if not any(x in rl for x in ("/www", "/web", "/ui", "/printer_data", "/mnt/udisk")):
            continue
        if not (rl.endswith(".js") or rl.endswith(".html") or rl.endswith(".css") or rl.endswith(".json")):
            continue
        if not is_probably_text(f):
            continue
        try:
            txt = read_text_loose(f, limit_bytes=1_200_000)
        except Exception:
            continue

        if not ENDPOINT_RE.search(txt):
            continue

        files.append(rel)
        for m in PATH_LIT_RE.findall(txt):
            for g in m:
                if g:
                    # sanitize a bit
                    if len(g) <= 160 and g.startswith("/"):
                        endpoints.add(g.split('"')[0].split("'")[0])

        if len(files) >= 200:
            break

    # Emit as keys WEB_*
    out_eps = {}
    idx = 1
    for ep in sorted(endpoints):
        key = "WEB_" + re.sub(r"[^A-Za-z0-9]+","_", ep.strip("/")).upper()[:60]
        if key not in out_eps:
            out_eps[key] = {"path": ep, "id": idx}
            idx += 1

    out = {"meta": {"dump_root": str(dump_root), "files": files[:200]}, "web": out_eps}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(out_eps)} endpoints)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
