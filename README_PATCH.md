# Guarded write integration patch

This patch wires `K2SafetyGuard` directly into `DeviceBlueprintLib` write APIs.

## What changed
- `DeviceBlueprintLib` now supports:
  - `attachSafetyGuard(K2SafetyGuard*)`
  - `armSafety(token)` / `lockSafety()`
- File transfer APIs (`M28/M29`) are now **gated**:
  - If guard is missing OR not armed -> operation returns false (fail-closed).

## Why
Prevents accidental destructive calls when your blueprint DB is present but you haven't verified identity.

## Apply
Merge `DeviceBlueprintLib/src` into your library, keeping your existing core modules.
