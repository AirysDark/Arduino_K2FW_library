# Arduino_K2FW_library

> Device Firmware Blueprint Database → Static Arduino/ESP32 Library

---

- [Overview](#overview)
- [Pipeline Summary](#pipeline-summary)
- [Folder Layout](#folder-layout)
- [Blueprint JSON Files](#blueprint-json-files)
- [Arduino Library Consumption](#arduino-library-consumption)
- [DeviceBlueprintLib (v1.1.0)](#deviceblueprintlib-v110)
- [Why This Design](#why-this-design)
- [Supported Use Cases](#supported-use-cases)
- [Safety Model](#safety-model)
- [Regeneration](#regeneration)
- [License & Ethics](#license--ethics)
- [Status](#status)
- [Documentation Index](#documentation-index)


---

## Overview

This repository builds a hardware / firmware blueprint database from a real device firmware dump
(e.g. Creality K2-class devices), then compiles that data into a static Arduino/ESP32 library.

The database is:

Extracted on PC (Python)

Normalized into JSON

Compiled into C++ headers

Consumed at runtime with zero guessing

No parsing on-device.
No heuristics.
No hard-coded offsets.

📘 Start here:

Database Specification: [read/README.db.md](read/README.db.md)  
Arduino Library API: [read/README.lib.md](read/README.lib.md)  

---  

## Pipeline Summary  

Firmware dump (libk2/)  
        ↓  
Python extractors (tools/)  
        ↓  
Normalized JSON (blueprint/)  
        ↓  
C++ generators (tools/gen_*)  
        ↓  
Static Arduino DB (DeviceBlueprintLib/src/generated/)  

Each stage is deterministic and reproducible.  

🔧 Full details:  
→ [read/README.tools.md](read/README.tools.md)  

---  

## Folder Layout  

libk2/                  ← Raw firmware dump (images, filesystems, sw-description)  
blueprint/              ← Extracted & normalized JSON (truth source)  
DeviceBlueprintLib/     ← Arduino/ESP32 library  
tools/                  ← Python extractors + generators  
read/                   ← Documentation  

📂 JSON schemas & meanings:  
→ [read/README.blueprint.md](read/README.blueprint.md)  

---  

## Blueprint JSON Files  

These files represent the authoritative device knowledge.  

PartitionMap.json  

Source of truth for flash layout.  

Parsed from sw-description (primary)  

GPT used only for bounds verification  

Partition names, LBA ranges, sizes, roles  

Generated header:  

k2_partitions_db.h  

📘 Details:  
→ [read/README.db.md#partitionmapjson](read/README.db.md#partitionmapjson)  

---  

Paths.json  

Filesystem discovery index used by all extractors.  

Generated header:  

k2_paths_db.h  

📘 Details:  
→ [read/README.db.md#pathsjson](read/README.db.md#pathsjson)  

---  

GcodeMacros.json  

Extracted G-code macros with referenced M/G codes.  

Generated header:  

k2_gcode_macros_db.h  

📘 Details:  
→ [read/README.db.md#gcodemacrosjson](read/README.db.md#gcodemacrosjson)  

---  

PrintCodes.json  

Semantic catalog of all M/G codes.  

Generated header:  

k2_printcodes_db.h  

📘 Details:  
→ [read/README.db.md#printcodesjson](read/README.db.md#printcodesjson)  

---  

MotionConfig.json  

Motion and kinematics limits.  

Generated header:  

k2_motion_limits_db.h  

📘 Details:  
→ [read/README.db.md#motionconfigjson](read/README.db.md#motionconfigjson)  

---  

Services.json  

Linux / application services and IPC hints.  

Generated header:  

k2_services_db.h  

📘 Details:  
→ [read/README.db.md#servicesjson](read/README.db.md#servicesjson)  

---  

WebHints.json  

Web UI & API discovery.  

Generated header:  

k2_web_endpoints_db.h  

📘 Details:  
→ [read/README.db.md#webhintsjson](read/README.db.md#webhintsjson)  

---  

KeyCatalog.json (optional)  

Unified ID registry:  

PART_*, PATH_*, GC_*  
M_*, G_*  
SVC_*, EP_*  

Generated header:  

k2_key_catalog.h  

📘 Details:  
→ [read/README.db.md#keycatalogjson](read/README.db.md#keycatalogjson)  

---  

## Arduino Library Consumption  

The Arduino library never parses JSON.  

It includes generated headers only:  

#include "generated/k2_partitions_db.h"  
#include "generated/k2_paths_db.h"  
#include "generated/k2_printcodes_db.h"  
#include "generated/k2_gcode_macros_db.h"  

auto part = K2Partitions::get(PART_ROOTFS_A);  
Serial.println(part.size_bytes);  

auto macro = K2Macros::get(GC_HOME_ALL);  
GCodeSender::run(macro);  

auto code = K2PrintCodes::get(M_28);  
Serial.println(code.meaning);  

📗 Full API:  

→ [read/README.lib.md](read/README.lib.md)  

---  

## DeviceBlueprintLib (v1.1.0)  

Static blueprint database + safe execution helpers for ESP32/Arduino.  

This library consumes:  

Compile-time generated headers (device truth)  

Optional runtime JSON assets (macros / scripts / prompts) from LittleFS or SD  

---  

## Safety Model  

Designed to:  

Never write outside known partitions  
Never guess offsets  
Never assume layout  
Fail closed, not open  

All destructive ops are gated by the database.  

🔒 Full rules:  
→ [read/SECURITY.md](read/SECURITY.md)  

---

## Status

✔ Extraction pipeline complete
✔ Static Arduino DB generation complete
✔ Safety guard integrated
✔ No runtime parsing
✔ Cross-device ready

---

## Documentation Index

- 📘 [Database Specification](read/README.db.md)
- 📗 [Arduino Library API](read/README.lib.md)
- 📂 [Blueprint JSON Reference](read/README.blueprint.md)
- 🔧 [Tools & Pipeline](read/README.tools.md)
- 🔒 [Security Model](read/SECURITY.md)
- ❓ [FAQ](read/FAQ.md)
- 🤝 [Contributing](read/CONTRIBUTING.md)
