#!/usr/bin/env python3
import sys, struct, re
from pathlib import Path
from _common import iter_files, dump_json

CANDIDATE_NAMES = ("gpt.bin","partition.bin","pt.bin","mmcblk0.bin","disk.img","emmc.img","mbr.bin")

def rd32le(b, off): return struct.unpack_from("<I", b, off)[0]
def rd64le(b, off): return struct.unpack_from("<Q", b, off)[0]

def parse_mbr(sector0: bytes):
    if len(sector0) < 512 or sector0[510:512] != b"\x55\xAA":
        return []
    parts = []
    pt = 0x1BE
    for i in range(4):
        e = sector0[pt+i*16:pt+(i+1)*16]
        ptype = e[4]
        lba_start = rd32le(e, 8)
        sectors   = rd32le(e, 12)
        if ptype == 0 or sectors == 0:
            continue
        parts.append({
            "name": f"mbr{i}",
            "first_lba": int(lba_start),
            "last_lba": int(lba_start + sectors - 1),
            "size_bytes": int(sectors * 512),
            "type": f"0x{ptype:02x}"
        })
    return parts

def parse_gpt(buf: bytes):
    if len(buf) < 1024 or buf[512:520] != b"EFI PART":
        return None
    hdr = buf[512:1024]
    part_lba  = rd64le(hdr, 72)
    num_parts = rd32le(hdr, 80)
    entry_sz  = rd32le(hdr, 84)

    entries_off = part_lba * 512
    need = entries_off + num_parts * entry_sz
    if len(buf) < need:
        return None

    parts = []
    for i in range(num_parts):
        eoff = entries_off + i*entry_sz
        e = buf[eoff:eoff+entry_sz]
        if e[:16] == b"\x00"*16:
            continue
        first = rd64le(e, 32)
        last  = rd64le(e, 40)
        if last < first:
            continue
        name_u16 = e[56:56+72]
        name = ""
        for j in range(0, len(name_u16), 2):
            ch = int.from_bytes(name_u16[j:j+2], "little")
            if ch == 0: break
            name += chr(ch) if ch < 128 else "?"
        if not name:
            name = f"gpt{i}"
        parts.append({
            "name": name,
            "first_lba": int(first),
            "last_lba": int(last),
            "size_bytes": int((last-first+1)*512),
            "type_guid_present": True
        })
    return parts

def find_candidate(dump_root: Path):
    for p in iter_files(dump_root):
        if p.name.lower() in CANDIDATE_NAMES:
            return p
    return None

def main():
    if len(sys.argv) < 3:
        print("usage: extract_partition_map.py <dump_root> <out_json>")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    cand = find_candidate(dump_root)
    parts = []
    mode = "none"
    source = None

    if cand:
        source = "/" + cand.relative_to(dump_root).as_posix()
        buf = None
        # SAFETY: do not read whole multi-GB images into RAM
        max_read = 512*4096  # 2 MiB
        with cand.open("rb") as f:
            buf = f.read(max_read)
        # legacy slice below kept
        buf = buf[: (512*256)]
        gpt = parse_gpt(buf)
        if gpt is not None:
            parts = gpt
            mode = "gpt"
        else:
            parts = parse_mbr(buf[:512])
            mode = "mbr" if parts else "unknown"

    out_parts = {}
    for p in parts:
        key = "PART_" + re.sub(r"[^A-Za-z0-9]+","_", p["name"]).upper()[:50]
        out_parts[key] = p

    out = {"meta": {"dump_root": str(dump_root), "source": source, "mode": mode},
           "partitions": out_parts}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(out_parts)} partitions, mode={mode})")
    if not cand:
        print("NOTE: No gpt.bin/disk.img found under dump_root. Drop one into libk2/ and rerun.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
