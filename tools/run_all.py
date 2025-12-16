#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess

def run(cmd):
    print(">>", " ".join(str(x) for x in cmd))
    subprocess.check_call([str(x) for x in cmd])

def exists_any(*paths: Path):
    for p in paths:
        if p and p.exists():
            return p
    return None

def tool(repo: Path, rel: str) -> Path:
    return repo / "tools" / rel

def gen_if_exists(py: Path, args, label: str):
    if py.exists():
        run([sys.executable, py, *args])
    else:
        print(f"!! {label} not found (skipping): {py}")

def main():
    repo = Path(__file__).resolve().parents[1]
    dump_root = repo / "libk2"
    out_dir = repo / "blueprint"
    out_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) >= 2:
        dump_root = Path(sys.argv[1]).resolve()

    print("Dump root:", dump_root)

    # ----------------------------
    # 1) Always generate Paths.json first (used for discovery)
    # ----------------------------
    paths_json = out_dir / "Paths.json"
    run([sys.executable, tool(repo, "extract_paths.py"), dump_root, paths_json])

    # ----------------------------
    # 2) Core extractors (Paths.json passed in where supported)
    # ----------------------------
    run([sys.executable, tool(repo, "extract_prompts.py"),      dump_root, out_dir/"Prompts.json",      paths_json])
    run([sys.executable, tool(repo, "extract_signatures.py"),   dump_root, out_dir/"Signatures.json",   paths_json])
    run([sys.executable, tool(repo, "extract_gcode_macros.py"), dump_root, out_dir/"GcodeMacros.json",  paths_json])

    # ----------------------------
    # 3) PartitionMap: sw-description truth; GPT optional bounds-check
    # ----------------------------
    swdesc_tool = tool(repo, "extract_partition_map_from_swdesc.py")
    legacy_gpt_tool = tool(repo, "extract_partition_map.py")
    partmap_json = out_dir / "PartitionMap.json"

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
            # NOTE: legacy tool signature may vary; keep your existing call pattern
            run([sys.executable, legacy_gpt_tool, dump_root, partmap_json, paths_json])
        else:
            print("!! No partition map tool found; skipping PartitionMap.json")

    # ----------------------------
    # 4) Remaining extractors
    # ----------------------------
    run([sys.executable, tool(repo, "extract_command_scripts.py"), dump_root, out_dir/"CommandScripts.json",  paths_json])
    run([sys.executable, tool(repo, "extract_services.py"),        dump_root, out_dir/"Services.json",        paths_json])
    run([sys.executable, tool(repo, "extract_motion_config.py"),   dump_root, out_dir/"MotionConfig.json",    paths_json])
    run([sys.executable, tool(repo, "extract_web_hints.py"),       dump_root, out_dir/"WebHints.json",        paths_json])
    run([sys.executable, tool(repo, "extract_mcu_proto_hints.py"), dump_root, out_dir/"McuProtoHints.json",   paths_json])
    run([sys.executable, tool(repo, "extract_printer_data.py"),    dump_root, out_dir/"PrinterData.json",     paths_json])
    run([sys.executable, tool(repo, "extract_file_ops.py"),        dump_root, out_dir/"FileOps.json",         paths_json])

    # ----------------------------
    # 5) Print code meanings + context + macro links
    # ----------------------------
    run([
        sys.executable, tool(repo, "extract_print_codes.py"),
        dump_root,
        out_dir/"PrintCodes.json",
        paths_json,
        out_dir/"GcodeMacros.json"
    ])

    run([
        sys.executable, tool(repo, "link_macros_codes.py"),
        out_dir/"GcodeMacros.json",
        out_dir/"PrintCodes.json"
    ])

    # ----------------------------
    # 6) OPTIONAL: Unified key catalog (only if tool exists)
    # ----------------------------
    key_catalog_tool = tool(repo, "extract_key_catalog.py")
    if key_catalog_tool.exists():
        run([sys.executable, key_catalog_tool, out_dir, out_dir/"KeyCatalog.json"])
    else:
        print("!! extract_key_catalog.py not found (skipping KeyCatalog.json)")

    # ============================================================
    # 7) GENERATE ARDUINO HEADERS (Option A generators)
    # ============================================================
    gen_out_dir = repo / "DeviceBlueprintLib" / "src" / "generated"
    gen_out_dir.mkdir(parents=True, exist_ok=True)

    # Partitions DB (you already had this)
    gen_if_exists(
        tool(repo, "gen_k2_partitions_db_from_partitionmap.py"),
        [partmap_json, gen_out_dir/"k2_partitions_db.h"],
        "gen_k2_partitions_db_from_partitionmap.py"
    )

    # Paths DB
    gen_if_exists(
        tool(repo, "gen_k2_paths_db.py"),
        [out_dir/"Paths.json", gen_out_dir/"k2_paths_db.h"],
        "gen_k2_paths_db.py"
    )

    # G-code macros DB
    gen_if_exists(
        tool(repo, "gen_k2_gcode_macros_db.py"),
        [out_dir/"GcodeMacros.json", gen_out_dir/"k2_gcode_macros_db.h"],
        "gen_k2_gcode_macros_db.py"
    )

    # Print codes DB (M_/G_ meanings + links)
    gen_if_exists(
        tool(repo, "gen_k2_printcodes_db.py"),
        [out_dir/"PrintCodes.json", gen_out_dir/"k2_printcodes_db.h"],
        "gen_k2_printcodes_db.py"
    )

    # Motion limits DB
    gen_if_exists(
        tool(repo, "gen_k2_motion_limits_db.py"),
        [out_dir/"MotionConfig.json", gen_out_dir/"k2_motion_limits_db.h"],
        "gen_k2_motion_limits_db.py"
    )

    # Services DB
    gen_if_exists(
        tool(repo, "gen_k2_services_db.py"),
        [out_dir/"Services.json", gen_out_dir/"k2_services_db.h"],
        "gen_k2_services_db.py"
    )

    # Web endpoints DB
    gen_if_exists(
        tool(repo, "gen_k2_web_endpoints_db.py"),
        [out_dir/"WebHints.json", gen_out_dir/"k2_web_endpoints_db.h"],
        "gen_k2_web_endpoints_db.py"
    )

    # Optional: Key catalog enum (generated from blueprint folder)
    gen_if_exists(
        tool(repo, "gen_k2_key_catalog.py"),
        [out_dir, gen_out_dir/"k2_key_catalog.h"],
        "gen_k2_key_catalog.py"
    )

    print("Done. Blueprint files written to:", out_dir)
    print("Done. Generated headers written to:", gen_out_dir)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())