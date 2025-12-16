#!/usr/bin/env python3
import sys, json, re
from pathlib import Path

def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def save_json(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def key_type(k: str) -> str:
    for prefix in ("PATH_", "GC_", "CMD_", "PART_", "WEB_", "SIG_", "PD_", "FILE_", "SVC_", "M_", "G_"):
        if k.startswith(prefix):
            return prefix[:-1]
    return "KEY"

def add_item(reg, key, kind, source, data=None, title=None, path=None, tags=None):
    if not key:
        return
    ent = reg.setdefault(key, {
        "key": key,
        "kind": kind or key_type(key),
        "title": title or "",
        "path": path or "",
        "tags": sorted(set(tags or [])),
        "sources": [],
        "data": {}
    })
    if source and source not in ent["sources"]:
        ent["sources"].append(source)
    if title and not ent["title"]:
        ent["title"] = title
    if path and not ent["path"]:
        ent["path"] = path
    if tags:
        ent["tags"] = sorted(set(ent["tags"]).union(tags))
    if isinstance(data, dict):
        # merge shallow
        for k,v in data.items():
            if k not in ent["data"]:
                ent["data"][k] = v

def main():
    if len(sys.argv) < 3:
        print("usage: extract_key_catalog.py <blueprint_dir> <out_json>")
        return 2

    bp = Path(sys.argv[1]).resolve()
    out_json = Path(sys.argv[2]).resolve()

    reg = {}
    meta = {"blueprint_dir": str(bp)}

    # ---------- Paths.json ----------
    paths = load_json(bp/"Paths.json") or {}
    for k, v in (paths.get("paths") or {}).items():
        add_item(
            reg, k, "PATH", "Paths.json",
            data={"path": v.get("path","")},
            title=v.get("path",""),
            path=v.get("path",""),
            tags=["path"]
        )

    # ---------- PartitionMap.json ----------
    pm = load_json(bp/"PartitionMap.json") or {}
    parts = (pm.get("partitions") or pm.get("PartitionMap") or pm.get("items") or {})
    if isinstance(parts, dict):
        for k, v in parts.items():
            add_item(reg, k, "PART", "PartitionMap.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=v.get("name","") if isinstance(v, dict) else "",
                     tags=["partition"])
    elif isinstance(parts, list):
        for i, v in enumerate(parts):
            if isinstance(v, dict):
                # attempt to form a stable key if missing
                name = v.get("name") or v.get("partition") or f"PART_{i:03d}"
                key = name if name.startswith("PART_") else ("PART_" + re.sub(r"[^A-Za-z0-9_]+","_", str(name)).upper())
                add_item(reg, key, "PART", "PartitionMap.json", data=v, title=str(name), tags=["partition"])

    # ---------- GcodeMacros.json ----------
    gm = load_json(bp/"GcodeMacros.json") or {}
    macros = gm.get("macros") or gm.get("gcodes") or gm.get("items") or {}
    if isinstance(macros, dict):
        for k, v in macros.items():
            if not k.startswith("GC_"):
                continue
            title = v.get("name","") if isinstance(v, dict) else ""
            add_item(reg, k, "GC", "GcodeMacros.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=title or k,
                     tags=["gcode","macro"])

    # ---------- CommandScripts.json ----------
    cs = load_json(bp/"CommandScripts.json") or {}
    scripts = cs.get("scripts") or cs.get("commands") or cs.get("items") or {}
    if isinstance(scripts, dict):
        for k, v in scripts.items():
            if not k.startswith("CMD_"):
                continue
            title = v.get("name","") if isinstance(v, dict) else ""
            add_item(reg, k, "CMD", "CommandScripts.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=title or k,
                     tags=["script","console"])

    # ---------- WebHints.json ----------
    wh = load_json(bp/"WebHints.json") or {}
    endpoints = wh.get("endpoints") or wh.get("api") or wh.get("items") or {}
    if isinstance(endpoints, dict):
        for k, v in endpoints.items():
            if not k.startswith("WEB_"):
                continue
            ep = v.get("endpoint","") if isinstance(v, dict) else ""
            add_item(reg, k, "WEB", "WebHints.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=ep or k,
                     tags=["web","api"])

    # ---------- Signatures.json ----------
    sig = load_json(bp/"Signatures.json") or {}
    sigs = sig.get("signatures") or sig.get("items") or {}
    if isinstance(sigs, dict):
        for k, v in sigs.items():
            if not k.startswith("SIG_"):
                continue
            add_item(reg, k, "SIG", "Signatures.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=v.get("label","") if isinstance(v, dict) else "",
                     tags=["signature"])

    # ---------- Services.json ----------
    sv = load_json(bp/"Services.json") or {}
    services = sv.get("services") or sv.get("items") or {}
    if isinstance(services, dict):
        for k, v in services.items():
            # allow SVC_ keys if you use them; otherwise still store
            kind = "SVC" if k.startswith("SVC_") else "SVC"
            add_item(reg, k, kind, "Services.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=v.get("name","") if isinstance(v, dict) else k,
                     tags=["service"])

    # ---------- PrinterData.json ----------
    pd = load_json(bp/"PrinterData.json") or {}
    items = ((pd.get("printer_data") or {}).get("items")) or pd.get("items") or {}
    if isinstance(items, dict):
        for k, v in items.items():
            if not k.startswith("PD_"):
                continue
            pth = v.get("path","") if isinstance(v, dict) else ""
            cat = v.get("category","") if isinstance(v, dict) else ""
            add_item(reg, k, "PD", "PrinterData.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=pth or k,
                     path=pth,
                     tags=["printer_data", cat] if cat else ["printer_data"])

    # ---------- FileOps.json ----------
    fo = load_json(bp/"FileOps.json") or {}
    file_ops = fo.get("file_ops") or fo.get("ops") or {}
    if isinstance(file_ops, dict):
        for k, v in file_ops.items():
            if not k.startswith("FILE_"):
                continue
            add_item(reg, k, "FILE", "FileOps.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=v.get("type","") if isinstance(v, dict) else k,
                     tags=["fileops"])

    # ---------- PrintCodes.json (M_/G_) ----------
    pc = load_json(bp/"PrintCodes.json") or {}
    codes = pc.get("codes") or pc.get("items") or {}
    if isinstance(codes, dict):
        for k, v in codes.items():
            if not (k.startswith("M_") or k.startswith("G_")):
                continue
            code = v.get("code","") if isinstance(v, dict) else ""
            meaning = v.get("meaning","") if isinstance(v, dict) else ""
            add_item(reg, k, "CODE", "PrintCodes.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=(f"{code} - {meaning}".strip(" -")) if (code or meaning) else k,
                     tags=["printcode"])

    # ---------- Prompts.json (optional registry) ----------
    pr = load_json(bp/"Prompts.json") or {}
    prompts = pr.get("prompts") or pr.get("items") or {}
    if isinstance(prompts, dict):
        for k, v in prompts.items():
            # you might not want these in final catalog, but it's useful
            add_item(reg, k, "PROMPT", "Prompts.json",
                     data=v if isinstance(v, dict) else {"value": v},
                     title=v.get("label","") if isinstance(v, dict) else k,
                     tags=["prompt"])

    # Final
    catalog = {
        "meta": meta,
        "counts": {
            "total": len(reg),
            "by_kind": {}
        },
        "keys": dict(sorted(reg.items(), key=lambda kv: kv[0]))
    }
    for k, ent in reg.items():
        catalog["counts"]["by_kind"][ent["kind"]] = catalog["counts"]["by_kind"].get(ent["kind"], 0) + 1

    save_json(out_json, catalog)
    print(f"Wrote {out_json} (keys={len(reg)})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())