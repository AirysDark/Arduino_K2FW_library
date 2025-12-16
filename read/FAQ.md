# FAQ

## Why do I only see one generated file?
Because only one generator ran. Run `tools/run_all.py` after adding gen_* scripts.

## Why is sw-description the truth?
Because it defines what the device update system actually targets. GPT only describes disk structure.

## What about print codes like M28?
They live in PrintCodes.json and are generated into k2_printcodes_db.h.
M28 typically begins SD file write; usually paired with M29.

## Do I need mounting to extract from disk images?
No. This repo avoids mounting. We parse manifests, files, and strings.

## Can I read .bin or .img?
Yes as bytes. We don’t “execute” them; we scan structure and known signatures.