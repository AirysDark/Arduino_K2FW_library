# blueprint/

This folder contains normalized JSON assets derived from `libk2/` (your dump).

These JSON files are intended to be uploaded to an ESP32 LittleFS image and consumed
by `DeviceBlueprintLib` using **Key IDs** (`GC_*`, `CMD_*`, `PART_*`, `PATH_*`, `SIG_*`, etc.).

## Generate / refresh

From repo root:

```bash
python tools/run_all.py
# or specify a custom dump root:
python tools/run_all.py libk2
```

## Output files

- `Paths.json`
- `Prompts.json`
- `Signatures.json`
- `GcodeMacros.json`
- `PartitionMap.json`
- `CommandScripts.json`
- `Services.json`
- `MotionConfig.json`
- `WebHints.json`
- `McuProtoHints.json`
