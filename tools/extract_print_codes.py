#!/usr/bin/env python3
import sys, re, json
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json, load_paths_json

CODE_RE = re.compile(r'\b([MG])\s*([0-9]{1,4}(?:\.[0-9]+)?)\b')
GC_LINE_RE = re.compile(r'^(?:\s*[MG][0-9]{1,4}|\s*;|\s*#|\s*T\d+|\s*SET_|\s*SAVE_|\s*RESTORE_|\s*RESPOND)')

# Built-in common meanings (best-effort; firmware may vary)
KNOWN = {"G0": "Rapid move", "G1": "Linear move", "G2": "Clockwise arc move", "G3": "Counter-clockwise arc move", "G4": "Dwell", "G28": "Home axes", "G29": "Bed leveling / mesh", "G90": "Absolute positioning", "G91": "Relative positioning", "G92": "Set position", "M0": "Stop / pause", "M18": "Disable steppers", "M20": "List SD/virtual SD files", "M21": "Init SD card", "M23": "Select SD file", "M24": "Start/resume SD print", "M25": "Pause SD print", "M28": "Begin SD/virtual SD write (start upload)", "M29": "End SD/virtual SD write (finish upload)", "M30": "Delete SD file (varies)", "M82": "Extruder absolute mode", "M83": "Extruder relative mode", "M84": "Disable motors (idle)", "M104": "Set hotend temp (no wait)", "M109": "Set hotend temp and wait", "M140": "Set bed temp (no wait)", "M190": "Set bed temp and wait", "M106": "Fan on / set speed", "M107": "Fan off", "M112": "Emergency stop", "M114": "Get current position", "M115": "Get firmware info", "M117": "Display message", "M204": "Set acceleration", "M205": "Set advanced settings (jerk etc, varies)", "M220": "Set speed factor", "M221": "Set flow factor", "M400": "Wait for moves to finish"}

def norm_key(letter: str, num: str) -> str:
    if '.' in num:
        a,b = num.split('.',1)
        return f"{letter}_{int(a):03d}_{b}"
    return f"{letter}_{int(num):03d}"

def parse_gcode_macros(gcode_macros_json: Path):
    # Expected format: either
    #   { "macros": { "GC_X": { "gcode": "..." } } }
    # or
    #   { "gcodes": { "GC_X": { "lines": [...] } } }
    # We'll be permissive.
    if not gcode_macros_json or not gcode_macros_json.exists():
        return {}
    try:
        data = json.loads(gcode_macros_json.read_text(encoding="utf-8"))
    except Exception:
        return {} 

    macros = {}

    for topk in ("macros","gcodes","GcodeMacros","items"):
        if isinstance(data.get(topk), dict):
            src = data[topk]
            for mk, mv in src.items():
                if isinstance(mv, dict):
                    if isinstance(mv.get("lines"), list):
                        macros[mk] = [str(x) for x in mv["lines"]]
                    elif isinstance(mv.get("gcode"), str):
                        macros[mk] = mv["gcode"].splitlines()
                    elif isinstance(mv.get("text"), str):
                        macros[mk] = mv["text"].splitlines()
            if macros:
                return macros

    # Fallback walk
    def walk(obj):
        if isinstance(obj, dict):
            for k,v in obj.items():
                if isinstance(v, dict) and (isinstance(v.get("gcode"), str) or isinstance(v.get("text"), str) or isinstance(v.get("lines"), list)):
                    if isinstance(v.get("lines"), list):
                        macros[k] = [str(x) for x in v["lines"]]
                    elif isinstance(v.get("gcode"), str):
                        macros[k] = v["gcode"].splitlines()
                    else:
                        macros[k] = v["text"].splitlines()
                walk(v)
        elif isinstance(obj, list):
            for it in obj:
                walk(it)
    walk(data)
    return macros

def main():
    if len(sys.argv) < 3:
        print("usage: extract_print_codes.py <dump_root> <out_json> [Paths.json] [GcodeMacros.json]")
        return 2

    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()
    paths_json = Path(sys.argv[3]).resolve() if len(sys.argv) >= 4 and sys.argv[3] else None
    gcode_macros_json = Path(sys.argv[4]).resolve() if len(sys.argv) >= 5 and sys.argv[4] else None

    paths_map = load_paths_json(paths_json) if paths_json and paths_json.exists() else {}
    macro_map = parse_gcode_macros(gcode_macros_json) if gcode_macros_json else {}

    focus_prefixes = (
        "/mnt/UDISK/printer_data/",
        "/usr/share/klipper/",
        "/etc/",
        "/usr/",
        "/overlay/",
    )

    codes = {}
    occurrences_cap_per_code = 50

    def add_occ(key, code, file_rel, line_no, context):
        rec = codes.setdefault(key, {
            "code": code,
            "meaning": KNOWN.get(code, ""),
            "occurrences": [],
            "evidence_files": set(),
            "used_by_macros": [],
            "notes": ""
        })
        if len(rec["occurrences"]) < occurrences_cap_per_code:
            rec["occurrences"].append({
                "file": file_rel,
                "line": line_no,
                "context": context
            })
        rec["evidence_files"].add(file_rel)

    # Scan dump files (context evidence)
    for f in iter_files(dump_root, paths_json=paths_json):
        rel = "/" + f.relative_to(dump_root).as_posix()
        rl = rel.lower()
        if not is_probably_text(f):
            continue
        if paths_map:
            if not (any(rel.startswith(pref) for pref in focus_prefixes) or rl.endswith((".gcode",".gc",".cfg",".conf",".ini",".json",".yaml",".yml",".sh",".service",".txt",".md",".js",".html"))):
                continue
        try:
            txt = read_text_loose(f, limit_bytes=1_500_000)
        except Exception:
            continue

        lines = txt.splitlines()
        maybe_gc = any(GC_LINE_RE.search(ln) for ln in lines[:200])
        if not maybe_gc and not CODE_RE.search(txt):
            continue

        for i, ln in enumerate(lines, start=1):
            for m in CODE_RE.finditer(ln):
                letter = m.group(1).upper()
                num = m.group(2)
                code = f"{letter}{num}"
                key = norm_key(letter, num)

                before = lines[i-2].strip() if i-2 >= 0 else ""
                after  = lines[i].strip() if i < len(lines) else ""
                ctx = {"before": before[:180], "line": ln.strip()[:220], "after": after[:180]}
                add_occ(key, code, rel, i, ctx)

    # Link codes to GC_* macros
    if macro_map:
        for macro_key, macro_lines in macro_map.items():
            blob = "\n".join(macro_lines)
            for m in CODE_RE.finditer(blob):
                letter = m.group(1).upper()
                num = m.group(2)
                code = f"{letter}{num}"
                key = norm_key(letter, num)
                rec = codes.setdefault(key, {
                    "code": code,
                    "meaning": KNOWN.get(code, ""),
                    "occurrences": [],
                    "evidence_files": set(),
                    "used_by_macros": [],
                    "notes": ""
                })
                if macro_key not in rec["used_by_macros"]:
                    rec["used_by_macros"].append(macro_key)

    out = {
        "meta": {
            "dump_root": str(dump_root),
            "paths_json": str(paths_json) if paths_json else "",
            "gcode_macros_json": str(gcode_macros_json) if gcode_macros_json else ""
        },
        "codes": {}
    }

    for key, rec in codes.items():
        rec["evidence_files"] = sorted(list(rec["evidence_files"])) if isinstance(rec.get("evidence_files"), (set,list)) else []
        rec["used_by_macros"] = sorted(rec.get("used_by_macros", []))
        code = rec["code"]
        if code.startswith("M28"):
            rec["notes"] = "Often starts SD/virtual-SD write/upload; paired with M29. Firmware-specific."
        elif code.startswith("M29"):
            rec["notes"] = "Often ends SD/virtual-SD write/upload started by M28. Firmware-specific."
        elif code.startswith("G29"):
            rec["notes"] = "Bed mesh/leveling is firmware-specific; may be disabled or mapped to macros."
        out["codes"][key] = rec

    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(out['codes'])} codes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
