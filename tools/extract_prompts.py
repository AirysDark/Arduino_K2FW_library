#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, extract_ascii_strings, dump_json

PROMPT_PATTERNS = [
    (r"=>\s*$", "PROMPT_UBOOT"),
    (r"U-Boot", "BANNER_UBOOT"),
    (r"\blogin:\s*$", "PROMPT_LOGIN"),
    (r"\bPassword:\s*$", "PROMPT_PASSWORD"),
    (r"#\s*$", "PROMPT_ROOT"),
    (r"\$\s*$", "PROMPT_USER"),
]

def main():
    if len(sys.argv) < 3:
        print("usage: extract_prompts.py <dump_root> <out_json>")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    found = {k: set() for _, k in PROMPT_PATTERNS}

    for f in iter_files(dump_root):
        try:
            if is_probably_text(f):
                text = read_text_loose(f, limit_bytes=1_000_000)
                lines = text.splitlines()
                for line in lines[-200:]:
                    for pat, key in PROMPT_PATTERNS:
                        if re.search(pat, line):
                            found[key].add(line.strip())
            else:
                b = f.read_bytes()[:2_000_000]
                for s in extract_ascii_strings(b, min_len=5):
                    for pat, key in PROMPT_PATTERNS:
                        if re.search(pat, s):
                            found[key].add(s.strip())
        except Exception:
            continue

    out = {
      "meta": {"dump_root": str(dump_root)},
      "prompts": {
        "uboot": { "prompt": "=>" },
        "linux": {
          "login": "login:",
          "password": "Password:",
          "shell_root": "#",
          "shell_user": "$"
        }
      },
      "evidence": {k: sorted(list(v))[:50] for k, v in found.items()}
    }
    dump_json(out_json, out)
    print(f"Wrote {out_json}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
