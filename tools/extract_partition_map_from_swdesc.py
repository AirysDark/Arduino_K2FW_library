#!/usr/bin/env python3
import sys, re, json
from pathlib import Path

# Tolerant SWUpdate sw-description parser.
# Extracts partition targets (device=...) and associated images (filename=...).
# Output PartitionMap.json: sw-description is truth; GPT is optional bounds check.

KV_RE  = re.compile(r'(?P<k>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<v>"[^"]*"|[0-9]+|true|false)\s*;')
FILENAME_RE = re.compile(r'filename\s*=\s*"([^"]+)"\s*;')
NAME_RE = re.compile(r'\bname\s*=\s*"([^"]+)"\s*;')
DEVICE_RE = re.compile(r'\bdevice\s*=\s*"([^"]+)"\s*;|\bdevice\s*=\s*([^;]+);')
TYPE_RE = re.compile(r'\btype\s*=\s*"([^"]+)"\s*;')

def read_text_loose(p: Path, limit: int = 50_000_000) -> str:
    b = p.read_bytes()[:limit]
    try:
        return b.decode("utf-8", errors="replace")
    except Exception:
        return b.decode("latin-1", errors="replace")

def safe_key(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).upper().strip('_')
    if not s:
        s = "UNKNOWN"
    return s[:60]

def guess_slot(label: str) -> int:
    t = (label or "").upper()
    if "SLOT_A" in t or "_A" in t or "ROOTFS_A" in t or "KERNEL_A" in t: return 0
    if "SLOT_B" in t or "_B" in t or "ROOTFS_B" in t or "KERNEL_B" in t: return 1
    return -1

def classify_role(name: str, dev: str, fns: list[str], typ: str) -> str:
    t = " ".join([name or "", dev or "", typ or "", " ".join(fns or [])]).lower()
    if "uboot" in t or "u-boot" in t or "spl" in t or "bootloader" in t: return "bootloader"
    if "dtb" in t or "devicetree" in t: return "dtb"
    if "kernel" in t or "zimage" in t or "uimage" in t or "image" in t: return "kernel"
    if "rootfs" in t or "squashfs" in t: return "rootfs"
    if "system" in t: return "system"
    if "userdata" in t or "udisk" in t or "printer_data" in t or "data" in t: return "userdata"
    if "recovery" in t: return "recovery"
    if "env" in t: return "env"
    return "unknown"

def is_critical(role: str, name: str, dev: str) -> bool:
    if role in ("bootloader","kernel","rootfs","dtb","env","recovery"):
        return True
    t = (name or "" + " " + (dev or "")).lower()
    return any(x in t for x in ("boot", "uboot", "spl", "env"))

def parse_swdesc_blocks(text: str):
    # Find blocks that contain device=... and either filename=... or name=...
    blocks = []
    for m in re.finditer(r'\bdevice\s*=', text):
        start = m.start()
        lb = text.rfind("{", 0, start)
        if lb == -1: 
            continue
        depth = 0
        rb = None
        for i in range(lb, len(text)):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    rb = i
                    break
        if rb is None:
            continue
        blk = text[lb:rb+1]
        if "device" in blk and ("filename" in blk or "name" in blk):
            blocks.append(blk)
    # de-dupe
    uniq = {}
    for b in blocks:
        uniq[hash(b)] = b
    return list(uniq.values())

def extract_fields(block: str):
    fields = {}
    for m in KV_RE.finditer(block):
        k = m.group("k")
        v = m.group("v")
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        elif v.isdigit():
            v = int(v)
        elif v in ("true","false"):
            v = (v == "true")
        fields[k] = v

    dev = None
    m = DEVICE_RE.search(block)
    if m:
        dev = (m.group(1) or m.group(2) or "").strip().strip('"')

    name = None
    m = NAME_RE.search(block)
    if m:
        name = m.group(1)

    typ = None
    m = TYPE_RE.search(block)
    if m:
        typ = m.group(1)

    fns = [m.group(1) for m in FILENAME_RE.finditer(block)]
    return fields, name, dev, typ, fns

def load_gpt_partition_map(gpt_json: Path):
    try:
        pm = json.loads(gpt_json.read_text(encoding="utf-8"))
        parts = pm.get("partitions", {})
        return pm, parts if isinstance(parts, dict) else {}
    except Exception:
        return None, {}

def lba_match_by_name(gpt_parts: dict, sw_name: str):
    sw_norm = re.sub(r'[^A-Za-z0-9]+','', sw_name or "").lower()
    if not sw_norm:
        return None, None, None
    for k, rec in gpt_parts.items():
        nm = str(rec.get("name",""))
        nm_norm = re.sub(r'[^A-Za-z0-9]+','', nm).lower()
        if nm_norm == sw_norm:
            return rec.get("first_lba"), rec.get("last_lba"), k
    return None, None, None

def main():
    if len(sys.argv) < 3:
        print("usage: extract_partition_map_from_swdesc.py <dump_root> <out_json> [gpt_partition_map_json]")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()
    gpt_json  = Path(sys.argv[3]).resolve() if len(sys.argv) >= 4 else None

    sw = dump_root / "sw-description"
    if not sw.exists():
        cands = list(dump_root.rglob("sw-description"))
        if cands:
            sw = cands[0]
    if not sw.exists():
        print("ERROR: sw-description not found under", dump_root)
        return 1

    text = read_text_loose(sw)
    blocks = parse_swdesc_blocks(text)

    gpt_meta = None
    gpt_parts = {}
    if gpt_json and gpt_json.exists():
        gpt_meta, gpt_parts = load_gpt_partition_map(gpt_json)

    partitions = {}
    images = {}
    warnings = []

    # de-dupe by device node; merge images
    device_to_key = {}

    for blk in blocks:
        fields, name, dev, typ, fns = extract_fields(blk)
        if not dev:
            continue

        dev = dev.strip().strip('"')
        if not dev.startswith("/dev/"):
            if dev.startswith("mmcblk"):
                dev = "/dev/" + dev

        label = name or fields.get("partition") or fields.get("target") or dev
        key = "PART_" + safe_key(label)

        slot = guess_slot(label)
        role = classify_role(label, dev, fns, typ or "")
        critical = is_critical(role, label, dev)

        rec = {
            "name": label,
            "device": dev,
            "type": typ or fields.get("type") or "",
            "role": role,
            "slot": slot,
            "critical": critical,
            "updateable": True if fns else False,
            "images": sorted(set(fns)),
            "sw_fields": fields,
        }

        # attach GPT bounds if available (bounds check)
        if gpt_parts:
            first, last, gkey = lba_match_by_name(gpt_parts, label)
            if first is not None and last is not None:
                rec["first_lba"] = int(first)
                rec["last_lba"]  = int(last)
                rec["size_bytes"] = int((int(last)-int(first)+1)*512)
                rec["gpt_match"]  = gkey

        # merge by device
        if dev in device_to_key:
            ek = device_to_key[dev]
            old = partitions[ek]
            old_imgs = set(old.get("images") or [])
            old_imgs |= set(rec.get("images") or [])
            old["images"] = sorted(old_imgs)
            old["updateable"] = True if old["images"] else old.get("updateable", False)
            # prefer more descriptive name
            if label and (old.get("name","").startswith("/dev/") or len(label) > len(old.get("name",""))):
                old["name"] = label
            partitions[ek] = old
        else:
            partitions[key] = rec
            device_to_key[dev] = key

        for fn in fns:
            images.setdefault(fn, {"count": 0, "partitions": []})
            images[fn]["count"] += 1
            images[fn]["partitions"].append(device_to_key[dev])

    for fn in list(images.keys()):
        images[fn]["partitions"] = sorted(set(images[fn]["partitions"]))

    out = {
        "meta": {
            "dump_root": str(dump_root),
            "source_sw_description": str(sw),
            "source_gpt_partition_map": str(gpt_json) if gpt_json else None,
            "mode": "sw-description-primary",
            "notes": [
                "sw-description is treated as truth (update intent + device mapping).",
                "GPT PartitionMap (if provided) is used only as bounds-check; LBA ranges attached on name-match."
            ]
        },
        "partitions": partitions,
        "images": images,
        "warnings": warnings
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_json} ({len(partitions)} partitions, {len(images)} images)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
