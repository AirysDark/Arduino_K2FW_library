# Contributing

## Rules
- Keep outputs deterministic
- Prefer conservative safety defaults
- Never auto-enable writes to critical partitions
- Keep everything Windows-compatible

## Coding style
- Python: type hints where useful, clear error messages
- JSON: stable ordering, no random keys
- C++ headers: simple structs, avoid heap allocation

## Testing
At minimum:
- run `tools/run_all.py` on a sample dump
- confirm headers compile in Arduino build