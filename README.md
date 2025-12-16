
# Arduino_K2FW_library

> **Device Firmware Blueprint Database → Static Arduino/ESP32 Library**

---

## Table of Contents
- [Overview](#overview)
- [Pipeline Summary](#pipeline-summary)
- [Folder Layout](#folder-layout)
- [Blueprint JSON Files](#blueprint-json-files)
  - [PartitionMap.json](#partitionmapjson)
  - [Paths.json](#pathsjson)
  - [GcodeMacros.json](#gcodemacrosjson)
  - [PrintCodes.json](#printcodesjson)
  - [MotionConfig.json](#motionconfigjson)
  - [Services.json](#servicesjson)
  - [WebHints.json](#webhintsjson)
  - [KeyCatalog.json (optional)](#keycatalogjson-optional)
- [Arduino Library Consumption](#arduino-library-consumption)
- [Why This Design](#why-this-design)
- [Supported Use Cases](#supported-use-cases)
- [Safety Model](#safety-model)
- [Regeneration](#regeneration)
- [License & Ethics](#license--ethics)
- [Status](#status)
- [Documentation Index](#documentation-index)

---

## Overview

This repository builds a **hardware / firmware blueprint database** from a real device firmware dump  
(e.g. Creality K2-class devices), then compiles that data into a **static Arduino/ESP32 library**.

The database is:

- Extracted on PC (Python)
- Normalized into JSON
- Compiled into C++ headers
- Consumed at runtime with **zero guessing**

**No parsing on-device.**  
**No heuristics.**  
**No hard-coded offsets.**

📘 Start here:
- [Database Specification](read/README.db.md)
- [Arduino Library API](read/README.lib.md)

---

## Pipeline Summary

Firmware dump (libk2/) ↓ Python extractors (tools/) ↓ Normalized JSON (blueprint/) ↓ C++ generators (tools/gen_*) ↓ Static Arduino DB (DeviceBlueprintLib/src/generated/)

Each stage is **deterministic and reproducible**.

🔧 Full pipeline details:  
→ [Tools & Pipeline](read/README.tools.md)

---

## Folder Layout

libk2/                 ← Raw firmware dump (images, filesystems, sw-description) blueprint/             ← Extracted & normalized JSON (truth source) DeviceBlueprintLib/    ← Arduino/ESP32 library tools/                 ← Python extractors + generators read/                  ← Documentation

📂 JSON meanings & schemas:  
→ [Blueprint JSON Reference](read/README.blueprint.md)

---

## Blueprint JSON Files

These files represent the **authoritative device knowledge**.

### PartitionMap.json

**Source of truth for flash layout.**

- Parsed from `sw-description` (primary)
- GPT used only for bounds verification
- Includes:
  - Partition names
  - LBA ranges
  - Sizes
  - Roles (boot, rootfs, data, recovery)

Generated header:

k2_partitions_db.h

📘 Details:  
→ [Database Spec → PartitionMap](read/README.db.md#partitionmapjson)

---

### Paths.json

**Filesystem discovery index.**

- Config directories
- Macro locations
- Databases
- Web UI roots
- Logs
- Update paths

Used by **all extractors** for auto-discovery.

Generated header:

k2_paths_db.h

📘 Details:  
→ [Database Spec → Paths](read/README.db.md#pathsjson)

---

### GcodeMacros.json

**Extracted G-code macros.**

- Macro name
- Source file
- Commands issued
- Referenced M/G codes

Generated header:

k2_gcode_macros_db.h

📘 Details:  
→ [Database Spec → G-code Macros](read/README.db.md#gcodemacrosjson)

---

### PrintCodes.json

**Full M-code / G-code catalog.**

For each code:
- Meaning / description
- Parameters
- Safety notes (when detectable)
- Macros that use it

Generated header:

k2_printcodes_db.h

Enables **semantic G-code usage**, not raw strings.

📘 Details:  
→ [Database Spec → Print Codes](read/README.db.md#printcodesjson)

---

### MotionConfig.json

**Motion and kinematics limits.**

- Steps/mm
- Max velocity
- Acceleration
- Jerk / junction deviation
- Axis limits

Generated header:

k2_motion_limits_db.h

📘 Details:  
→ [Database Spec → Motion Config](read/README.db.md#motionconfigjson)

---

### Services.json

**Linux / application services.**

- systemd / init services
- Ports
- IPC hints
- Readiness indicators

Generated header:

k2_services_db.h

📘 Details:  
→ [Database Spec → Services](read/README.db.md#servicesjson)

---

### WebHints.json

**Web UI and API discovery.**

- Endpoints
- Paths
- JSON schemas (where inferable)

Generated header:

k2_web_endpoints_db.h

📘 Details:  
→ [Database Spec → Web Hints](read/README.db.md#webhintsjson)

---

### KeyCatalog.json (optional)

**Unified key registry** for ID-based access.

Includes:
- `PART_*`, `PATH_*`, `GC_*`
- `M_*`, `G_*`
- `SVC_*`, `EP_*`

Generated header:

k2_key_catalog.h

📘 Details:  
→ [Database Spec → Key Catalog](read/README.db.md#keycatalogjson)

---

## Arduino Library Consumption

The Arduino library **never parses JSON**.

It includes **generated headers only**:

```cpp
#include "generated/k2_partitions_db.h"
#include "generated/k2_paths_db.h"
#include "generated/k2_printcodes_db.h"
#include "generated/k2_gcode_macros_db.h"

Example usage

auto part = K2Partitions::get(PART_ROOTFS_A);
Serial.println(part.size_bytes);

auto macro = K2Macros::get(GC_HOME_ALL);
GCodeSender::run(macro);

auto code = K2PrintCodes::get(M_28);
Serial.println(code.meaning);

📗 Full API & patterns:
→ Arduino Library API


---

Why This Design

Why sw-description is the truth

Defines actual update layout

Independent of disk image quirks

Used by the device itself

Prevents destructive writes


GPT is used only to sanity-check bounds.

🔒 More detail:
→ Security Model


---

Why JSON first, C++ second

Python excels at parsing and discovery

JSON is inspectable, diffable, versionable

C++ headers are fast, safe, and deterministic on MCUs


This keeps the ESP32 lean and predictable.


---

Supported Use Cases

ESP32 UART bridge / rescue tools

Safe backup & restore

G-code injection with semantic meaning

Motion validation

External UI controllers

Firmware replacement research

Device emulation

Hardware cloning



---

Safety Model

Designed to:

Never write outside known partitions

Never guess offsets

Never assume firmware layout

Fail closed, not open


All destructive operations are explicitly gated by the database.

🔒 Full rules:
→ SECURITY.md


---

Regeneration

Rebuild everything from a new dump:

python tools/run_all.py <path_to_dump>

This will:

1. Rebuild all JSON


2. Rebuild all Arduino headers


3. Keep the library in sync




---

License & Ethics

This project:

Does not distribute proprietary firmware

Does not reverse cryptography

Extracts structure and behavior, not source


Comparable in intent to Klipper, Marlin, OpenWRT.


---

Status

✔ Extraction pipeline complete
✔ Static Arduino DB generation complete
✔ No runtime parsing required
✔ Cross-device ready


---

Documentation Index

📘 Database Specification

📗 Arduino Library API

📂 Blueprint JSON Reference

🔧 Tools & Pipeline

🔒 Security Model

❓ FAQ

🤝 Contributing

