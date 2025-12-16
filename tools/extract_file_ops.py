#!/usr/bin/env python3
import sys, re
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json

HTTP_UPLOAD_HINTS = [
    (r"/server/files/upload", "FILE_HTTP_MOONRAKER_UPLOAD"),
    (r"/api/files/upload", "FILE_HTTP_API_UPLOAD"),
]

def main():
    if len(sys.argv) < 3:
        print("usage: extract_file_ops.py <dump_root> <out_json>")
        return 2
    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    ops = {}

    # Always include M28 pipeline (generic)
    ops["FILE_M28_STREAM_GCODE"] = {
        "type": "m28_stream",
        "begin": "M28 {remote}",
        "end": "M29",
        "verify": ["M20", "M30 {remote}"],
        "notes": "Start SD/virtual-SD write with M28, stream lines, finish with M29. Verify with M20/M30 if supported."
    }

    # Detect if M28 appears in configs/docs and add evidence
    evidence = {"m28": [], "http": []}
    for f in iter_files(dump_root):
        rel = "/" + f.relative_to(dump_root).as_posix()
        try:
            if is_probably_text(f):
                txt = read_text_loose(f, limit_bytes=800_000)
                if "M28" in txt or "M29" in txt:
                    if len(evidence["m28"]) < 50:
                        evidence["m28"].append(rel)
                for pat, key in HTTP_UPLOAD_HINTS:
                    if re.search(pat, txt):
                        ops.setdefault(key, {"type":"http_upload", "endpoint": re.findall(pat, txt)[0] if re.findall(pat, txt) else pat})
                        if len(evidence["http"]) < 50:
                            evidence["http"].append(rel)
        except Exception:
            continue

    out = {"meta": {"dump_root": str(dump_root)}, "file_ops": ops, "evidence": evidence}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(ops)} ops)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
