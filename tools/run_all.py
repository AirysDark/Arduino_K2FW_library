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

    # 1) Always generate Paths.json first (used for discovery)
    paths_json = out_dir / "Paths.json"
    run([sys.executable, str(repo/"tools/extract_paths.py"), str(dump_root), str(paths_json)])

    # 2) Core extractors
    run([sys.executable, str(repo/"tools/extract_prompts.py"), str(dump_root), str(out_dir/"Prompts.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_signatures.py"), str(dump_root), str(out_dir/"Signatures.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_gcode_macros.py"), str(dump_root), str(out_dir/"GcodeMacros.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_partition_map.py"), str(dump_root), str(out_dir/"PartitionMap.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_command_scripts.py"), str(dump_root), str(out_dir/"CommandScripts.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_services.py"), str(dump_root), str(out_dir/"Services.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_motion_config.py"), str(dump_root), str(out_dir/"MotionConfig.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_web_hints.py"), str(dump_root), str(out_dir/"WebHints.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_mcu_proto_hints.py"), str(dump_root), str(out_dir/"McuProtoHints.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_printer_data.py"), str(dump_root), str(out_dir/"PrinterData.json"), str(paths_json)])
    run([sys.executable, str(repo/"tools/extract_file_ops.py"), str(dump_root), str(out_dir/"FileOps.json"), str(paths_json)])

    # 3) NEW: Print code meanings + context + macro links
    # (Pass GcodeMacros.json so we can fill used_by_macros)
    run([
        sys.executable, str(repo/"tools/extract_print_codes.py"),
        str(dump_root),
        str(out_dir/"PrintCodes.json"),
        str(paths_json),
        str(out_dir/"GcodeMacros.json")
    ])

    # 4) NEW: Reverse link macros -> uses_codes, and refresh PrintCodes.json
    run([
        sys.executable, str(repo/"tools/link_macros_codes.py"),
        str(out_dir/"GcodeMacros.json"),
        str(out_dir/"PrintCodes.json")
    ])

    # 5) OPTIONAL: Unified key catalog (only if tool exists)
    key_catalog_tool = repo / "tools" / "extract_key_catalog.py"
    if key_catalog_tool.exists():
        run([sys.executable, str(key_catalog_tool), str(out_dir), str(out_dir/"KeyCatalog.json")])
    else:
        print("!! extract_key_catalog.py not found (skipping KeyCatalog.json)")

    print("Done. Blueprint files written to:", out_dir)

if __name__ == "__main__":
    raise SystemExit(main())