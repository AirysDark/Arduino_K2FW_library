# extract_print_codes.py (context mode)

This extractor scans text-like files for M- and G-codes and outputs:

- Stable keys: `M_028`, `G_001`, `G_028_1`, ...
- Best-effort meanings for common standard codes
- Context evidence: file + line number + before/line/after

Run (recommended):
  python tools/extract_print_codes.py libk2 blueprint/PrintCodes.json blueprint/Paths.json
