#!/usr/bin/env python3
import json, re
from pathlib import Path

TEXT_EXT = {
  ".txt",".md",".ini",".cfg",".conf",".json",".yaml",".yml",".sh",".service",".js",".html",".css",".gcode",".gc",".csv",".xml"
}

def is_probably_text(p: Path) -> bool:
    ext = p.suffix.lower()
    if ext in TEXT_EXT:
        return True
    try:
        if p.stat().st_size > 2_000_000:
            return False
        b = p.read_bytes()[:4096]
        return b.count(b"\x00") == 0
    except Exception:
        return False

def read_text_loose(p: Path, limit_bytes: int = 1_000_000) -> str:
    b = p.read_bytes()[:limit_bytes]
    try:
        return b.decode("utf-8", errors="replace")
    except Exception:
        return b.decode("latin-1", errors="replace")

def dump_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_paths_json(paths_json: Path):
    try:
        data = json.loads(Path(paths_json).read_text(encoding="utf-8"))
        return data.get("paths", {})
    except Exception:
        return {}

def linux_to_dump_path(dump_root: Path, linux_path: str) -> Path:
    lp = (linux_path or "").strip()
    if not lp:
        return dump_root
    if not lp.startswith("/"):
        lp = "/" + lp
    return dump_root / lp.lstrip("/")

def iter_files(dump_root: Path, paths_json: Path | None = None):
    dump_root = Path(dump_root)
    yielded = set()

    if paths_json:
        pm = load_paths_json(paths_json)
        for _, v in pm.items():
            lp = v.get("path", "")
            if not lp.startswith("/"):
                continue
            f = linux_to_dump_path(dump_root, lp)
            if f.exists() and f.is_file():
                rp = str(f.resolve())
                if rp not in yielded:
                    yielded.add(rp)
                    yield f

    for f in dump_root.rglob("*"):
        if f.is_file():
            rp = str(f.resolve())
            if rp not in yielded:
                yielded.add(rp)
                yield f

_ASCII_RE = re.compile(rb"[\x20-\x7E]{4,}")

def extract_ascii_strings(p: Path, min_len: int = 4, limit_bytes: int = 8_000_000):
    """Extract printable ASCII strings from a binary or text file.
    Returns list[str]. Used by extract_prompts.py / extract_signatures.py."""
    try:
        b = p.read_bytes()[:limit_bytes]
    except Exception:
        return []
    out = []
    for m in _ASCII_RE.finditer(b):
        s = m.group(0)
        if len(s) >= min_len:
            try:
                out.append(s.decode("ascii", errors="ignore"))
            except Exception:
                pass
    return out
