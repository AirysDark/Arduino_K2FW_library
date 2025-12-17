#!/usr/bin/env python3
import json, re
from pathlib import Path

def emit_count_from_array(array_name: str) -> str:
    # Prefer sizeof-based counts to avoid ordering/scope issues.
    return f"inline constexpr size_t {array_name.upper()}_COUNT = sizeof({array_name}) / sizeof({array_name}[0]);\n"


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def safe_cpp(s: str) -> str:
    s = "" if s is None else str(s)
    return s.replace("\\", "\\\\").replace('"', '\\"')

def safe_ident(s: str) -> str:
    s = "" if s is None else str(s)
    s = re.sub(r'[^A-Za-z0-9_]+', "_", s).upper().strip("_")
    if not s:
        s = "UNKNOWN"
    if s[0].isdigit():
        s = "K_" + s
    return s[:80]

def write_header(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
