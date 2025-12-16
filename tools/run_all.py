#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess

def run(cmd):
    print(">>", " ".join(str(x) for x in cmd))
    subprocess.check_call([str(x) for x in cmd])

def exists_any(*paths: Path) -> Path | None:
    for p in paths:
        if p and p.exists():
            return p
    return None

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
    run([sys.executable, repo / "tools" / "extract_paths.py", dump_root, paths_json])

    # 2) Core extractors (Paths.json passed in where supported)
    run([sys.executable, repo/"tools/extract_prompts.py",          dump_root, out_dir/"Prompts.json",         paths_json])
    run([sys.executable, repo/"tools/extract_signatures.py",       dump_root, out_dir/"Signatures.json",      paths_json])
    run([sys.executable, repo/"tools/extract_gcode_macros.py",     dump_root, out_dir/"GcodeMacros.json",     paths_json])

    # 3) PartitionMap: sw-description truth; GPT optional bounds-check
    swdesc_tool = repo / "tools" / "extract_partition_map_from_swdesc.py"
    legacy_gpt_tool = repo / "tools" / "extract_partition_map.py"
    partmap_json = out_dir / "PartitionMap.json"

    # Optional: if you already generate a GPT-based map somewhere else, point to it here.
    # (This script won't try to generate GPT map automatically — sw-description is primary.)
    gpt_partmap_json = exists_any(
        out_dir / "PartitionMap_GPT.json",
        out_dir / "PartitionMapGPT.json",
        out_dir / "PartitionMap_gpt.json",
    )

    sw_description = exists_any(dump_root / "sw-description", *list(dump_root.rglob("sw-description")))

    if swdesc_tool.exists() and sw_description:
        if gpt_partmap_json:
            run([sys.executable, swdesc_tool, dump_root, partmap_json, gpt_partmap_json])
        else:
            run([sys.executable, swdesc_tool, dump_root, partmap_json])
    else:
        # Fallback: old GPT/MBR extractor (kept for non-swupdate dumps)
        if legacy_gpt_tool.exists():
            run([sys.executable, legacy_gpt_tool, dump_root, partmap_json, paths_json])
        else:
            print("!! No partition map tool found; skipping PartitionMap.json")

    # 4) Remaining extractors
    run([sys.executable, repo/"tools/extract_command_scripts.py",   dump_root, out_dir/"CommandScripts.json",  paths_json])
    run([sys.executable, repo/"tools/extract_services.py",          dump_root, out_dir/"Services.json",        paths_json])
    run([sys.executable, repo/"tools/extract_motion_config.py",     dump_root, out_dir/"MotionConfig.json",    paths_json])
    run([sys.executable, repo/"tools/extract_web_hints.py",         dump_root, out_dir/"WebHints.json",        paths_json])
    run([sys.executable, repo/"tools/extract_mcu_proto_hints.py",   dump_root, out_dir/"McuProtoHints.json",   paths_json])
    run([sys.executable, repo/"tools/extract_printer_data.py",      dump_root, out_dir/"PrinterData.json",     paths_json])
    run([sys.executable, repo/"tools/extract_file_ops.py",          dump_root, out_dir/"FileOps.json",         paths_json])

    # 5) Print code meanings + context + macro links
    run([
        sys.executable, repo/"tools/extract_print_codes.py",
        dump_root,
        out_dir/"PrintCodes.json",
        paths_json,
        out_dir/"GcodeMacros.json"
    ])

    run([
        sys.executable, repo/"tools/link_macros_codes.py",
        out_dir/"GcodeMacros.json",
        out_dir/"PrintCodes.json"
    ])

    # 6) OPTIONAL: Unified key catalog (only if tool exists)
    key_catalog_tool = repo / "tools" / "extract_key_catalog.py"
    if key_catalog_tool.exists():
        run([sys.executable, key_catalog_tool, out_dir, out_dir/"KeyCatalog.json"])
    else:
        print("!! extract_key_catalog.py not found (skipping KeyCatalog.json)")

    # 7) NEW: Generate Arduino static DB header from PartitionMap.json (if generator exists)
    gen_db_tool = repo / "tools" / "gen_k2_partitions_db_from_partitionmap.py"
    out_h = repo / "DeviceBlueprintLib" / "src" / "generated" / "k2_partitions_db.h"
    if gen_db_tool.exists() and partmap_json.exists():
        run([sys.executable, gen_db_tool, partmap_json, out_h])
    else:
        print("!! gen_k2_partitions_db_from_partitionmap.py not found or PartitionMap missing (skipping header generation)")

    print("Done. Blueprint files written to:", out_dir)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())