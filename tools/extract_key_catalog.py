#!/usr/bin/env python3
import sys, json
from pathlib import Path
from _common import dump_json

def load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def flatten_section(prefix: str, data: dict, field: str):
    out = {}
    sec = data.get(field, {})
    if not isinstance(sec, dict):
        return out
    for k, v in sec.items():
        if isinstance(v, dict):
            out[k] = {"type": prefix, **v}
        else:
            out[k] = {"type": prefix, "value": v}
    return out

def main():
    if len(sys.argv) < 3:
        print("usage: extract_key_catalog.py <blueprint_dir> <out_json>")
        return 2
    bp = Path(sys.argv[1]).resolve()
    out_json = Path(sys.argv[2]).resolve()

    catalog = {}

    # Paths.json
    p = bp/"Paths.json"
    if p.exists():
        d = load(p)
        paths = d.get("paths", {})
        if isinstance(paths, dict):
            for k, v in paths.items():
                if isinstance(v, dict):
                    catalog[k] = {"type":"PATH", **v}
    # GcodeMacros.json
    p = bp/"GcodeMacros.json"
    if p.exists():
        d = load(p)
        gc = d.get("gcodes", {})
        if isinstance(gc, dict):
            for k, v in gc.items():
                catalog[k] = {"type":"GC", **(v if isinstance(v, dict) else {"text": str(v)})}
    # CommandScripts.json
    p = bp/"CommandScripts.json"
    if p.exists():
        d = load(p)
        cmds = d.get("commands", [])
        if isinstance(cmds, list):
            for item in cmds:
                if isinstance(item, dict) and "key" in item:
                    catalog[item["key"]] = {"type":"CMD", **item}
    # WebHints.json
    p = bp/"WebHints.json"
    if p.exists():
        d = load(p)
        web = d.get("web", {})
        if isinstance(web, dict):
            for k, v in web.items():
                catalog[k] = {"type":"WEB", **(v if isinstance(v, dict) else {"path": str(v)})}
    # PrintCodes.json
    p = bp/"PrintCodes.json"
    if p.exists():
        d = load(p)
        for k, v in (d.get("m_codes", {}) or {}).items():
            if isinstance(v, dict): catalog[k] = {"type":"M", **v}
        for k, v in (d.get("g_codes", {}) or {}).items():
            if isinstance(v, dict): catalog[k] = {"type":"G", **v}

    # Stable sort for readability in README generation etc.
    out = {"meta":{"blueprint_dir": str(bp)}, "keys": dict(sorted(catalog.items(), key=lambda kv: kv[0]))}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(out['keys'])} keys)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
