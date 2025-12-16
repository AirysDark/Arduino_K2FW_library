Arduino_K2FW_library

> Device Firmware Blueprint Database → Static Arduino/ESP32 Library




---

Table of Contents

Overview

Pipeline Summary

Folder Layout

Blueprint JSON Files

Arduino Library Consumption

DeviceBlueprintLib (v1.1.0)

Why This Design

Supported Use Cases

Safety Model

Regeneration

License & Ethics

Status

Documentation Index



---

Overview

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

Database Specification

Arduino Library API



---

Pipeline Summary

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
→ Tools & Pipeline


---

Folder Layout

libk2/                  ← Raw firmware dump (images, filesystems, sw-description)
blueprint/              ← Extracted & normalized JSON (truth source)
DeviceBlueprintLib/     ← Arduino/ESP32 library
tools/                  ← Python extractors + generators
read/                   ← Documentation

📂 JSON schemas & meanings:
→ Blueprint JSON Reference


---

Blueprint JSON Files

These files represent the authoritative device knowledge.

PartitionMap.json

Source of truth for flash layout.

Parsed from sw-description (primary)

GPT used only for bounds verification

Partition names, LBA ranges, sizes, roles


Generated header:

k2_partitions_db.h

📘 Details:
→ PartitionMap


---

Paths.json

Filesystem discovery index used by all extractors.

Generated header:

k2_paths_db.h

📘 Details:
→ Paths


---

GcodeMacros.json

Extracted G-code macros with referenced M/G codes.

Generated header:

k2_gcode_macros_db.h

📘 Details:
→ G-code Macros


---

PrintCodes.json

Semantic catalog of all M/G codes.

Generated header:

k2_printcodes_db.h

📘 Details:
→ Print Codes


---

MotionConfig.json

Motion and kinematics limits.

Generated header:

k2_motion_limits_db.h

📘 Details:
→ Motion Config


---

Services.json

Linux / application services and IPC hints.

Generated header:

k2_services_db.h

📘 Details:
→ Services


---

WebHints.json

Web UI & API discovery.

Generated header:

k2_web_endpoints_db.h

📘 Details:
→ Web Hints


---

KeyCatalog.json (optional)

Unified ID registry:

PART_*, PATH_*, GC_*

M_*, G_*

SVC_*, EP_*


Generated header:

k2_key_catalog.h

📘 Details:
→ Key Catalog


---

Arduino Library Consumption

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

📗 Full API: → Arduino Library API


---

DeviceBlueprintLib (v1.1.0)

Static blueprint database + safe execution helpers for ESP32/Arduino.

This library consumes:

Compile-time generated headers (device truth)

Optional runtime JSON assets (macros / scripts / prompts) from LittleFS or SD


Quick Start

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

  // Optional runtime assets
  // bp.loadAssets("/GcodeMacros.json", "/CommandScripts.json", "/Prompts.json");

  auto part = K2Partitions::get(PART_ROOTFS_A);
  Serial.printf("ROOTFS_A size=%llu\n",
    (unsigned long long)part.size_bytes);
}
void loop() {}

Safety

Destructive operations are fail-closed unless armed:

fileBegin / fileWriteLine / fileEnd

uploadGcodeFromFS (M28/M29)


Scripts (CMD_*) can also be gated if enabled.


---

Why This Design

Why sw-description is the truth

Defines real update layout

Independent of disk image quirks

Used by the device itself

Prevents destructive writes


GPT is used only for bounds sanity-checking.

🔒 Details:
→ Security Model


---

Why JSON first, C++ second

Python excels at parsing

JSON is inspectable & diffable

C++ headers are deterministic on MCUs



---

Supported Use Cases

ESP32 UART rescue bridges

Safe backup & restore

Semantic G-code injection

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

Never assume layout

Fail closed, not open


All destructive ops are gated by the database.

🔒 Full rules:
→ SECURITY.md


---

Regeneration

Rebuild everything from a new dump:

python tools/run_all.py <path_to_dump>

This will:

1. Rebuild all JSON


2. Regenerate all Arduino headers


3. Keep the library in sync




---

License & Ethics

No proprietary firmware distributed

No cryptography reversed

Structure & behavior only


Comparable in intent to Klipper, Marlin, OpenWRT.


---

Status

✔ Extraction pipeline complete
✔ Static Arduino DB generation complete
✔ Safety guard integrated
✔ No runtime parsing
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

