#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, extract_ascii_strings, dump_json

BAUD_RE = re.compile(r"\b(9600|19200|38400|57600|115200|230400|250000|500000|921600)\b")
TTY_RE  = re.compile(r"(/dev/ttyS\d+|/dev/ttyUSB\d+|/dev/ttyACM\d+|/dev/ttyAMA\d+)", re.I)
TOK_RE  = re.compile(r"\b(ACK|NACK|ERR|ERROR|OK|READY|BUSY|CMD|RESP|JSON|RPC|FRAME|CRC)\b", re.I)

def main():
    if len(sys.argv) < 3:
        print("usage: extract_mcu_proto_hints.py <dump_root> <out_json>")
        return 2
    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    bauds = set()
    ttys  = set()
    tokens = set()
    evidence = []

    for f in iter_files(dump_root):
        rel = "/" + f.relative_to(dump_root).as_posix()
        rl = rel.lower()

        # configs and binaries both matter
        try:
            if is_probably_text(f):
                txt = read_text_loose(f, limit_bytes=800_000)
                for b in BAUD_RE.findall(txt): bauds.add(int(b))
                for t in TTY_RE.findall(txt): ttys.add(t)
                for tok in TOK_RE.findall(txt): tokens.add(tok.upper())
                if (BAUD_RE.search(txt) or TTY_RE.search(txt) or TOK_RE.search(txt)) and len(evidence) < 80:
                    evidence.append(rel)
            else:
                blob = f.read_bytes()[:2_000_000]
                ss = extract_ascii_strings(blob, min_len=4)
                hit = False
                for s in ss:
                    if BAUD_RE.search(s):
                        for b in BAUD_RE.findall(s): bauds.add(int(b))
                        hit = True
                    if TTY_RE.search(s):
                        for t in TTY_RE.findall(s): ttys.add(t)
                        hit = True
                    if TOK_RE.search(s):
                        for tok in TOK_RE.findall(s): tokens.add(tok.upper())
                        hit = True
                if hit and len(evidence) < 80:
                    evidence.append(rel)
        except Exception:
            continue

        if len(evidence) >= 80 and len(tokens) >= 20:
            # enough hints
            pass

    out = {
      "meta": {"dump_root": str(dump_root)},
      "proto": {
        "tty_candidates": sorted(ttys),
        "baud_candidates": sorted(bauds),
        "tokens": sorted(tokens)
      },
      "evidence": evidence[:80]
    }
    dump_json(out_json, out)
    print(f"Wrote {out_json} (tty={len(ttys)}, baud={len(bauds)}, tokens={len(tokens)})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
