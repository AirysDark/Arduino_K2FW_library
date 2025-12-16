#!/usr/bin/env python3
import sys, re, json
from pathlib import Path
from _common import iter_files, is_probably_text, read_text_loose, dump_json

# Generic motion keys (Klipper-like + common printer configs)
KEYS = [
  "max_velocity","max_accel","max_accel_to_decel","square_corner_velocity",
  "microsteps","rotation_distance","gear_ratio","step_pin","dir_pin","enable_pin",
  "stepper_x","stepper_y","stepper_z","extruder","heater_bed",
  "sensor_type","control","pid_kp","pid_ki","pid_kd",
  "position_min","position_max","homing_speed","second_homing_speed","endstop_pin",
  "nozzle_diameter","filament_diameter","pressure_advance","max_extrude_only_velocity","max_extrude_only_accel"
]

SECTION_RE = re.compile(r"^\s*\[(.+?)\]\s*$")
KV_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*:\s*(.+?)\s*$")

def parse_cfg(text: str):
    section = None
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#",";")):
            continue
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1).strip()
            out.setdefault(section, {})
            continue
        m = KV_RE.match(line)
        if m and section:
            k = m.group(1).strip()
            v = m.group(2).strip()
            if k in KEYS or k.startswith(("max_","pid_","position_","homing_","rotation_","microsteps","gear_","step_","dir_","enable_")):
                out.setdefault(section, {})[k] = v
    return out

def main():
    if len(sys.argv) < 3:
        print("usage: extract_motion_config.py <dump_root> <out_json>")
        return 2
    dump_root = Path(sys.argv[1]).resolve()
    out_json  = Path(sys.argv[2]).resolve()

    motion = {}
    sources = []

    for f in iter_files(dump_root):
        rel = "/" + f.relative_to(dump_root).as_posix()
        rl = rel.lower()

        # Focus on klipper + printer_data config areas, but remain generic
        if not any(x in rl for x in ("/usr/share/klipper", "/printer_data", "/config", "/etc")):
            continue
        if not (rl.endswith(".cfg") or rl.endswith(".conf") or rl.endswith(".ini") or rl.endswith(".toml") or rl.endswith(".json")):
            continue
        if not is_probably_text(f):
            continue

        try:
            txt = read_text_loose(f, limit_bytes=900_000)
        except Exception:
            continue

        if "[" in txt and ":" in txt:
            parsed = parse_cfg(txt)
            if parsed:
                sources.append(rel)
                for sec, kv in parsed.items():
                    motion.setdefault(sec, {}).update(kv)

        if len(sources) >= 80:
            break

    # Create stable keys for key-driven use
    keys = {}
    idx = 1
    for sec, kv in motion.items():
        sk = "MC_" + re.sub(r"[^A-Za-z0-9]+","_", sec).upper()[:50]
        keys[sk] = {"section": sec, "values": kv, "id": idx}
        idx += 1

    out = {"meta": {"dump_root": str(dump_root), "sources": sources[:80]}, "motion": keys}
    dump_json(out_json, out)
    print(f"Wrote {out_json} ({len(keys)} sections)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
