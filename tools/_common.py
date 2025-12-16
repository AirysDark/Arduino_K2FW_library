#!/usr/bin/env python3
import os, re, json, hashlib
from pathlib import Path

TEXT_EXTS = {
    ".txt",".log",".cfg",".conf",".ini",".json",".yaml",".yml",".xml",
    ".sh",".service",".rc",".env",".md",".csv",".gcode",".gc",".tap",
    ".lua",".py",".js",".ts",".html",".css"
}

def sha256_file(path: Path, max_bytes=None) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        if max_bytes is None:
            while True:
                b = f.read(1024*1024)
                if not b: break
                h.update(b)
        else:
            h.update(f.read(max_bytes))
    return h.hexdigest()

def read_text_loose(path: Path, limit_bytes=2_000_000) -> str:
    data = path.read_bytes()
    if len(data) > limit_bytes:
        data = data[:limit_bytes]
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc, errors="ignore")
        except Exception:
            pass
    return data.decode("latin-1", errors="ignore")

def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTS:
        return True
    try:
        b = path.read_bytes()[:4096]
        return b.count(b"\x00") < 50
    except Exception:
        return False

def iter_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file():
            yield p

def extract_ascii_strings(blob: bytes, min_len=4):
    out = []
    cur = bytearray()
    for c in blob:
        if 32 <= c <= 126:
            cur.append(c)
        else:
            if len(cur) >= min_len:
                out.append(cur.decode("ascii", errors="ignore"))
            cur.clear()
    if len(cur) >= min_len:
        out.append(cur.decode("ascii", errors="ignore"))
    return out

def dump_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()
