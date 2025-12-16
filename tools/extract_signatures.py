#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json

ERROR_HINTS = [
    ("MOTOR_CHECK", r"MOTOR[_ ]CHECK|motor check", "SIG_MOTOR_CHECK"),
    ("THERMAL", r"thermal runaway|THERMAL|overtemp|heater fault", "SIG_THERMAL"),
    ("WATCHDOG", r"watchdog|wdt|hung task", "SIG_WATCHDOG"),
    ("KERNEL_PANIC", r"kernel panic|Oops:", "SIG_KERNEL_PANIC"),
    ("FS_CORRUPT", r"EXT4-fs error|I/O error|corrupt", "SIG_FS_CORRUPT"),
    ("OOM", r"Out of memory|oom-killer", "SIG_OOM"),
]

def main():
    if len(sys.argv) < 3:
        print("usage: extract_signatures.py <dump_root> <out_json>")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    sigs = {}
    evidence = {}

    for f in iter_files(dump_root):
        rel = f.relative_to(dump_root).as_posix().lower()
        if not any(x in rel for x in ("log","dmesg","messages","syslog","journal","stderr","stdout")):
            continue
        if not is_probably_text(f):
            continue
        try:
            text = read_text_loose(f, limit_bytes=2_000_000)
        except Exception:
            continue

        for label, pat, key in ERROR_HINTS:
            if re.search(pat, text, flags=re.IGNORECASE):
                sigs.setdefault(key, {"name": label, "pattern": pat, "severity": "warn", "suggest": []})
                evidence.setdefault(key, set()).add(rel)

    for key in list(sigs.keys()):
        if key == "SIG_KERNEL_PANIC":
            sigs[key]["severity"] = "fatal"
            sigs[key]["suggest"] = ["Check kernel cmdline, dtb, root= target", "Try fallback slot / safe boot args"]
        elif key == "SIG_MOTOR_CHECK":
            sigs[key]["suggest"] = ["Check homing/endstops/probe", "Review motion limits/config"]
        elif key == "SIG_FS_CORRUPT":
            sigs[key]["severity"] = "fatal"
            sigs[key]["suggest"] = ["fsck/repair partition", "restore from backup"]
        elif key == "SIG_THERMAL":
            sigs[key]["severity"] = "fatal"
            sigs[key]["suggest"] = ["Check thermistor wiring", "PID tuning / safety cutoffs"]

    out = {
      "meta": {"dump_root": str(dump_root)},
      "signatures": sigs,
      "evidence": {k: sorted(list(v)) for k, v in evidence.items()}
    }
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(sigs)} signatures)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
