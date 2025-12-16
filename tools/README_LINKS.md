# Reverse link upgrade (GC_* -> uses_codes)

This adds reverse links so each `GC_*` macro includes:

- `uses_codes`: ["M_028", "G_001", ...]

It also refreshes `PrintCodes.json` so each code includes:

- `used_by_macros`: ["GC_*", ...]

Run:
```bash
python tools/link_macros_codes.py blueprint/GcodeMacros.json blueprint/PrintCodes.json
```
