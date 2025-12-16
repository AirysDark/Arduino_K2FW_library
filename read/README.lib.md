---

# 3) `DeviceBlueprintLib/README.md` (deep Arduino API)

```md
# DeviceBlueprintLib — Arduino / ESP32 Runtime Blueprint API

This library provides a **runtime interface** over statically generated blueprint databases.

It is designed for:
- ESP32 UART bridges
- safe backup/restore tools
- semantic G-code drivers
- device discovery controllers

It is NOT a printer firmware.

---

## Key idea

Everything is accessed by stable IDs:

- partitions: `PART_*`
- paths: `PATH_*`
- macros: `GC_*`
- print codes: `M_*`, `G_*`
- services: `SVC_*`
- endpoints: `EP_*`

This prevents:
- string typos
- mismatched offsets
- unsafe writes
- fragile hardcoded magic values

---

## Generated headers

These live in: