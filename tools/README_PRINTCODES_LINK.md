# extract_print_codes.py (macro-link mode)

Outputs `PrintCodes.json` with:

- Stable keys: `M_028`, `G_001`, ...
- `meaning` (best-effort standard meaning)
- `occurrences` (file + line + before/line/after)
- `used_by_macros` (list of `GC_*` macro keys that contain that code)

Run:

```bash
python tools/extract_print_codes.py libk2 blueprint/PrintCodes.json blueprint/Paths.json blueprint/GcodeMacros.json
```
