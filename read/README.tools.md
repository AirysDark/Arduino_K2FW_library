# tools/ — Extractors + Generators

This directory contains:

1) Extractors: `extract_*.py`
   - Read dumps in `libk2/`
   - Emit normalized JSON into `blueprint/`

2) Generators: `gen_*.py`
   - Read JSON in `blueprint/`
   - Emit static Arduino headers into `DeviceBlueprintLib/src/generated/`

---

## Entry point

```bash
python tools/run_all.py