# DeviceBlueprintLib (v1.1.0)

Static blueprint database + safe execution helpers for ESP32/Arduino.

This library is designed to consume **generated headers** (compile-time DB) and optional
**runtime JSON assets** (key->text maps) stored on LittleFS/SD.

## Quick start

```cpp
#include <Arduino.h>
#include "DeviceBlueprintLib.h"
#include "core/K2SafetyGuard.h"

DeviceBlueprintLib bp;
K2SafetyGuard guard;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);

  DeviceBlueprintLib::init(&Serial);

  bp.begin(Serial2, &Serial);
  bp.attachSafetyGuard(&guard);
  bp.armSafety(0xC0FFEE01); // enables file upload APIs

  // Load runtime assets (optional but required for runGCode/runScript)
  // bp.loadAssets("/GcodeMacros.json", "/CommandScripts.json", "/Prompts.json");

  // Example: use compiled DB
  auto part = K2Partitions::get(PART_ROOTFS_A);
  Serial.printf("ROOTFS_A size=%llu\n", (unsigned long long)part.size_bytes);
}
void loop() {}
```

## Safety

Destructive ops are **fail-closed** unless a `K2SafetyGuard` is attached and armed:
- `fileBegin/fileWriteLine/fileEnd/uploadGcodeFromFS` (M28/M29 workflow)

Scripts (CMD_*) can be gated too by enabling the check in `runScript()`.

## Generated DB

Headers live in:
- `src/generated/`

They are produced by your PC pipeline (tools/) from a real dump.
