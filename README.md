# Arduino_K2FW_library (refactor pack)

This pack adds:
- `DeviceBlueprintLib/` Arduino library (ESP32)
- `tools/` Python extractors (default dump root: `libk2/`)
- `blueprint/` JSON outputs

## Repo refactor you do

Move your existing dump folders into `libk2/`:

Example:
- before: `bin/ etc/ usr/ mnt/ ...`
- after: `libk2/bin libk2/etc libk2/usr libk2/mnt ...`

Then run:

```bash
python tools/run_all.py
```

Then upload JSON files to ESP32 LittleFS and call:

```cpp
lib.loadAssets("/GcodeMacros.json","/CommandScripts.json","/Prompts.json");
```
