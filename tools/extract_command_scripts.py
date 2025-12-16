#!/usr/bin/env python3
import sys, re, json
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json

UBOOT_HINTS = [
    ("CMD_UBOOT_PRINTENV", r"\bprintenv\b"),
    ("CMD_UBOOT_SAVEENV", r"\bsaveenv\b"),
    ("CMD_UBOOT_BOOT", r"\bboot\b"),
    ("CMD_UBOOT_RESET", r"\breset\b"),
    ("CMD_UBOOT_UMS0", r"\bums\s+0\s+mmc\s+0\b"),
    ("CMD_UBOOT_MMC_LIST", r"\bmmc\s+list\b"),
    ("CMD_UBOOT_MMC_INFO", r"\bmmc\s+info\b"),
]

LINUX_HINTS = [
    ("CMD_LINUX_REBOOT", r"\breboot\b"),
    ("CMD_LINUX_POWEROFF", r"\bpoweroff\b"),
    ("CMD_LINUX_DMESG", r"\bdmesg\b"),
    ("CMD_LINUX_JOURNALCTL", r"\bjournalctl\b"),
    ("CMD_LINUX_SYSTEMCTL", r"\bsystemctl\b"),
]

def main():
    if len(sys.argv) < 3:
        print("usage: extract_command_scripts.py <dump_root> <out_json>")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    scripts = {}

    for f in iter_files(dump_root):
        if not is_probably_text(f):
            continue
        try:
            txt = read_text_loose(f, limit_bytes=500_000)
        except Exception:
            continue

        for key, pat in UBOOT_HINTS:
            if re.search(pat, txt):
                scripts.setdefault(key, {
                    "context": "uboot",
                    "script": pat.replace("\\b","").replace("\\s+"," ")
                })

        for key, pat in LINUX_HINTS:
            if re.search(pat, txt):
                scripts.setdefault(key, {
                    "context": "linux",
                    "script": pat.replace("\\b","")
                })

    out = {
      "meta": {"dump_root": str(dump_root)},
      "commands": scripts
    }
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(scripts)} commands)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
