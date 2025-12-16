#!/usr/bin/env python3
import sys, json, re
from pathlib import Path

CODE_RE = re.compile(r'\b([MG])\s*([0-9]{1,4}(?:\.[0-9]+)?)\b')

def norm_key(letter: str, num: str) -> str:
    if '.' in num:
        a,b = num.split('.',1)
        return f"{letter}_{int(a):03d}_{b}"
    return f"{letter}_{int(num):03d}"

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def save_json(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def extract_macro_map(gm: dict):
    # Returns macro_key -> text (joined)
    # be permissive: find any dict entries keyed by GC_* that contain gcode/text/lines
    macros = {}
    # common tops
    for topk in ("macros","gcodes","items","GcodeMacros"):
        src = gm.get(topk)
        if isinstance(src, dict):
            for mk, mv in src.items():
                if not isinstance(mv, dict): 
                    continue
                if isinstance(mv.get("lines"), list):
                    macros[mk] = "\n".join(str(x) for x in mv["lines"])
                elif isinstance(mv.get("gcode"), str):
                    macros[mk] = mv["gcode"]
                elif isinstance(mv.get("text"), str):
                    macros[mk] = mv["text"]
            if macros:
                return macros, topk
    # fallback: scan gm top-level if it already is GC_* mapping
    if all(isinstance(v, dict) for v in gm.values()):
        for mk, mv in gm.items():
            if isinstance(mv.get("lines"), list):
                macros[mk] = "\n".join(str(x) for x in mv["lines"])
            elif isinstance(mv.get("gcode"), str):
                macros[mk] = mv["gcode"]
            elif isinstance(mv.get("text"), str):
                macros[mk] = mv["text"]
    return macros, None

def apply_reverse_links(gm: dict, macro_to_codes: dict, topk: str|None):
    # Inject uses_codes into each macro dict
    if topk and isinstance(gm.get(topk), dict):
        for mk, codes in macro_to_codes.items():
            mv = gm[topk].get(mk)
            if isinstance(mv, dict):
                mv["uses_codes"] = sorted(codes)
    else:
        for mk, codes in macro_to_codes.items():
            mv = gm.get(mk)
            if isinstance(mv, dict):
                mv["uses_codes"] = sorted(codes)

def main():
    if len(sys.argv) < 3:
        print("usage: link_macros_codes.py <GcodeMacros.json> <PrintCodes.json> [out_gcode_macros_json] [out_print_codes_json]")
        return 2
    gcode_macros_path = Path(sys.argv[1]).resolve()
    print_codes_path   = Path(sys.argv[2]).resolve()
    out_gm = Path(sys.argv[3]).resolve() if len(sys.argv) >= 4 and sys.argv[3] else gcode_macros_path
    out_pc = Path(sys.argv[4]).resolve() if len(sys.argv) >= 5 and sys.argv[4] else print_codes_path

    gm = load_json(gcode_macros_path)
    pc = load_json(print_codes_path)

    macros, topk = extract_macro_map(gm)

    macro_to_codes = {}
    code_to_macros = {}

    for mk, text in macros.items():
        codes = set()
        for m in CODE_RE.finditer(text):
            letter = m.group(1).upper()
            num = m.group(2)
            k = norm_key(letter, num)  # e.g. M_028
            codes.add(k)
            code_to_macros.setdefault(k, set()).add(mk)
        if codes:
            macro_to_codes[mk] = codes

    # Update PrintCodes.json too (authoritative linkage)
    codes_obj = pc.get("codes", {})
    for code_key, macro_set in code_to_macros.items():
        rec = codes_obj.get(code_key)
        if rec is None:
            # create minimal record if missing
            codes_obj[code_key] = {"code": code_key.replace("_", "").replace("M","M").replace("G","G"),
                                   "meaning": "",
                                   "occurrences": [],
                                   "evidence_files": [],
                                   "used_by_macros": sorted(macro_set),
                                   "notes": ""}
        else:
            existing = set(rec.get("used_by_macros", []))
            rec["used_by_macros"] = sorted(existing.union(macro_set))

    pc["codes"] = codes_obj

    apply_reverse_links(gm, macro_to_codes, topk)

    save_json(out_gm, gm)
    save_json(out_pc, pc)
    print(f"Updated: {out_gm} and {out_pc} (macros linked={len(macro_to_codes)}, codes linked={len(code_to_macros)})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
