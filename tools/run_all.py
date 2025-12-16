#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    repo = Path(__file__).resolve().parents[1]
    dump_root = repo / "libk2"
    out_dir = repo / "blueprint"
    out_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) >= 2:
        dump_root = Path(sys.argv[1]).resolve()

    print("Dump root:", dump_root)

    run([sys.executable, str(repo / "tools" / "extract_paths.py"),
         str(dump_root), str(out_dir / "Paths.json")])

    run([sys.executable, str(repo / "tools" / "extract_prompts.py"),
         str(dump_root), str(out_dir / "Prompts.json")])

    run([sys.executable, str(repo / "tools" / "extract_signatures.py"),
         str(dump_root), str(out_dir / "Signatures.json")])

    run([sys.executable, str(repo / "tools" / "extract_gcode_macros.py"),
         str(dump_root), str(out_dir / "GcodeMacros.json")])

    run([sys.executable, str(repo / "tools" / "extract_partition_map.py"),
         str(dump_root), str(out_dir / "PartitionMap.json")])

    run([sys.executable, str(repo / "tools" / "extract_command_scripts.py"),
         str(dump_root), str(out_dir / "CommandScripts.json")])

    run([sys.executable, str(repo / "tools" / "extract_services.py"),
         str(dump_root), str(out_dir / "Services.json")])

    run([sys.executable, str(repo / "tools" / "extract_motion_config.py"),
         str(dump_root), str(out_dir / "MotionConfig.json")])

    run([sys.executable, str(repo / "tools" / "extract_web_hints.py"),
         str(dump_root), str(out_dir / "WebHints.json")])

    run([sys.executable, str(repo / "tools" / "extract_mcu_proto_hints.py"),
         str(dump_root), str(out_dir / "McuProtoHints.json")])

    print("Done. Blueprint files written to:", out_dir)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())