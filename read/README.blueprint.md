---

# 4) `blueprint/README.md`

```md
# blueprint/ — Normalized Truth Database

This folder is the device blueprint in JSON form.

Everything here is produced by `tools/run_all.py`.

These JSON files are the source of truth for code generation.

---

## Files

- `PartitionMap.json` — storage layout + safety flags
- `Paths.json` — discovery index
- `GcodeMacros.json` — macros registry
- `PrintCodes.json` — M/G code meaning + macro links
- `MotionConfig.json` — motion limits (best effort)
- `Services.json` — services + ports
- `WebHints.json` — endpoints + UI hints
- `KeyCatalog.json` — optional unified key list

---

## How to review changes

When updating dumps:
- Diff PartitionMap.json carefully
  - critical/updateable changes are high risk
- Diff Paths.json
  - new discovery paths expand extraction
- Diff PrintCodes.json
  - meanings should remain stable; links may expand
- Diff GcodeMacros.json
  - macro bodies may change with firmware updates

---

## Trust model

- sw-description drives partition truth
- GPT validates physical bounds
- everything else is best-effort discovery from filesystem

---