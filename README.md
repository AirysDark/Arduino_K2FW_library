
# Arduino_K2FW_library — Device Blueprint Database + Arduino Static Library

This repository turns a real embedded device firmware dump into a **normalized blueprint database** (JSON),
then compiles that blueprint into a **static Arduino/ESP32 C++ library**.

It is designed to be:
- **Deterministic** (same input dump → same output JSON/headers)
- **Safe by construction** (no guessing offsets, no writing outside known partitions)
- **Windows-first** (no mounting, no loop devices required)
- **Device-agnostic** (not tied to K2Bridge/FakeK2; those are separate projects)

Although the repo name references K2, the architecture supports **any embedded Linux device**
with:
- partition layouts (sw-description/GPT/MBR)
- filesystems containing configs/macros/UI/data
- logs/services/endpoints that can be discovered by scanning files and strings

---

## What this is

✅ A **device blueprint compiler**:
- storage layout → partitions, slots, recovery, safety flags
- firmware intelligence → boot plan, prompts, services, configs
- print behavior → macros + M/G codes meaning & links
- motion behavior → limits, steps/mm, accelerations where discoverable

✅ A **static Arduino database library**:
- generated headers for partitions/paths/macros/printcodes/motion/services/endpoints
- lookup APIs to use those facts safely on an ESP32

---

## What this is NOT

❌ It does **not** include proprietary firmware contents for redistribution  
❌ It does **not** “decrypt” secure boot / keys / signatures  
❌ It does **not** mount images or require Linux admin tools  
❌ It does **not** attempt to recover original source code from binaries  

This project extracts **structure, intent, and behavior signals** so you can build safe tooling.

---

## Architecture at a glance

libk2/                     (input dump) ↓ tools/extract_.py      (PC extraction) blueprint/.json            (normalized truth database) ↓ tools/gen_.py          (code generation) DeviceBlueprintLib/src/generated/.h ↓ Arduino/ESP32 runtime APIs (safe lookups + execution helpers)

### Why JSON in the middle?
Because JSON is:
- inspectable / diffable in Git
- versionable
- acts as a stable contract between “reverse engineering” and “embedded code”

---

## Repository layout

```text
libk2/                      ← input dump (renameable, but default path)
blueprint/                  ← normalized extracted JSON
DeviceBlueprintLib/         ← Arduino/ESP32 library consuming generated headers
tools/                      ← extractors + generators (Python)
docs/ (optional)            ← diagrams / notes / future expansion


---

Quick start (Windows)

1) Put your dump in libk2/

Examples:

libk2/sw-description

libk2/disk_1.1.2.6.img (recovery image)

libk2/mnt/UDISK/printer_data/...

libk2/usr/share/klipper/...


2) Run the pipeline

python tools\run_all.py

3) Result

JSONs appear in blueprint/

Generated C++ headers appear in DeviceBlueprintLib/src/generated/



---

Safety model (high level)

sw-description (SWUpdate manifest) is treated as truth for partition intent: “what partitions exist and what updates are allowed”

GPT/MBR parsing is treated as bounds check: “do these partitions fit inside physical device boundaries”

If data conflicts:

sw-description wins

GPT is used to detect obvious corruption or mismatched devices



The library is designed to:

forbid writes to critical partitions unless explicitly marked updateable

expose safe “profiles” for backup/restore rather than raw offsets


See: SECURITY.md and README.db.md


---

Using the Arduino library

See: DeviceBlueprintLib/README.md


---

Regenerating after a new dump

1. Replace content in libk2/


2. Run:

python tools\run_all.py


3. Commit changes in:

blueprint/*.json

DeviceBlueprintLib/src/generated/*.h





---

Common problems

Only one file in generated/? → you only ran the partitions generator. Run run_all.py after adding generators.

Recovery image has partitions but “latest update image” does not? → Use sw-description from recovery. That defines layout.


See FAQ.md.


---

License

See LICENSE.


---

Ethics / intended use

This is meant for:

recovery tooling

interoperability

research

safe device management


Not for:

distributing proprietary firmware

bypassing security mechanisms

unauthorized access


---

# 2) `README.db.md` (deep database spec)

```md
# Device Blueprint Database Specification (README.db.md)

This document defines the **contract** between:
- PC-side extraction (Python) and
- MCU-side runtime usage (DeviceBlueprintLib)

The blueprint database exists in two forms:
1) **Normalized JSON** in `blueprint/`
2) **Generated static C++ headers** in `DeviceBlueprintLib/src/generated/`

The MCU must never parse raw dumps. It only consumes generated headers.

---

## Core principles

### P1 — sw-description is truth
If present, `sw-description` defines:
- partition intent
- updateable partitions
- slot roles (A/B)
- version identity metadata

### P2 — GPT/MBR is bounds check
GPT parsing is used to:
- confirm partitions fit in device size
- detect mismatched device images
- attach physical LBA bounds to logical partitions when names match

GPT does NOT override sw-description partition intent.

### P3 — Deterministic output
Given identical input dumps, output JSON must be identical (ordering, normalization).

### P4 — Fail closed
If data cannot be trusted, output should:
- mark partitions as unknown/unsafe
- avoid generating “write allowed” flags
- prefer conservative defaults

---

## Database files (authoritative)

### 1) PartitionMap.json

#### Purpose
Defines storage layout and safety policy.

#### Minimal schema
```json
{
  "meta": {
    "source": "sw-description",
    "device": "K2-class",
    "version": "1.1.2.6"
  },
  "partitions": {
    "PART_ROOTFS_A": {
      "name": "rootfs_a",
      "device": "/dev/mmcblk0pX",
      "slot": "A",
      "role": "rootfs",
      "critical": true,
      "updateable": false,

      "first_lba": 123456,
      "last_lba": 234567,
      "size_bytes": 57147392
    }
  }
}

Required fields (best effort)

name — logical partition label (normalized)

device — Linux node hint if known (/dev/mmcblk0p#)

role — one of:

bootloader, env, kernel, dtb, rootfs, overlay, userdata, recovery, data, unknown


critical — true if writing can brick device

updateable — true only if SWUpdate explicitly targets it


Optional bounds fields

first_lba, last_lba, size_bytes — attached from GPT if available


Safety invariants

critical && !updateable must default to write forbidden

critical && updateable still requires explicit API “allow write”

unknown role must default to write forbidden



---

2) Paths.json

Purpose

Discovery index for “where important stuff lives”.

Typical contents

PATH_PRINTER_DATA → mnt/UDISK/printer_data

PATH_KLIPPER_CONFIG → usr/share/klipper

PATH_WEB_UI → mnt/UDISK/printer_data/web

PATH_DATABASE → mnt/UDISK/printer_data/database


Minimal schema (flexible)

{
  "meta": { "generated_by": "extract_paths.py" },
  "paths": {
    "PATH_PRINTER_DATA": { "path": "/mnt/UDISK/printer_data", "why": "configs/macros/db/web" }
  }
}


---

3) GcodeMacros.json

Purpose

Extracts macro files into a portable registry.

Schema (typical)

{
  "macros": {
    "GC_HOME_ALL": {
      "source": "/mnt/UDISK/printer_data/config/macros.cfg",
      "gcode": "G28\n...",
      "desc": "Home all axes",
      "uses_codes": ["G_28", "M_400"]
    }
  }
}


---

4) PrintCodes.json

Purpose

Defines M/G codes with:

meaning

context

parameter hints (best effort)

links to macros that use them


Example:

{
  "codes": {
    "M_28": {
      "meaning": "Begin writing to SD",
      "context": "Usually paired with M29; writes file to SD/virtual SD",
      "used_by_macros": ["GC_SAVE_JOB"]
    }
  }
}


---

5) MotionConfig.json

Purpose

Captures motion constraints discoverable from configs.

Expected keys:

steps/mm

max velocity

max accel

axis limits

jerk/junction settings


This is NOT guaranteed complete — some devices store these in binaries or MCU.


---

6) Services.json / WebHints.json

Purpose

Discovery hints for:

system services

ports

API endpoints used by UI


These are best-effort and may be incomplete.


---

Generated headers (MCU contract)

Generated headers must:

be valid Arduino C++

avoid dynamic allocation

avoid large runtime parsing

provide simple lookup structures


Example pattern:

struct PathItem { const char* key; const char* path; };
extern const PathItem K2_PATHS[];


---

Safety policy mapping

Partition write permission

Write permission should be computed as:

allowed = updateable && !critical

Additionally:

destructive operations must require explicit opt-in

restore operations must require identity guard (board/version match)



---

Versioning rules

When updating dumps:

Commit blueprint/*.json

Commit DeviceBlueprintLib/src/generated/*.h

Do NOT commit raw proprietary blobs unless you own the rights



---

Troubleshooting database conflicts

Case: sw-description lists partitions not present in GPT

Likely reasons:

GPT image is incomplete

recovery update targets only a subset

device uses vendor partitioning


Resolution:

keep sw-description entries

mark GPT bounds fields as missing

write forbidden unless updateable is explicit


Case: GPT shows partitions but sw-description doesn’t

Those partitions are not part of update intent:

keep them

mark role unknown

critical default true

updateable false



---

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

DeviceBlueprintLib/src/generated/

Typical files:
- `k2_partitions_db.h`
- `k2_paths_db.h`
- `k2_gcode_macros_db.h`
- `k2_printcodes_db.h`
- `k2_motion_limits_db.h`
- `k2_services_db.h`
- `k2_web_endpoints_db.h`
- `k2_key_catalog.h` (optional)

Do not edit them manually.

---

## Core APIs (typical patterns)

### Partitions

```cpp
auto p = K2Partitions::findByKey("PART_ROOTFS_A");
// or (enum-based if you use key catalog)
auto p2 = K2Partitions::get(PART_ROOTFS_A);

Safety:

if (!K2Partitions::canWrite(p)) {
  // refuse destructive op
}

Paths

auto cfg = K2Paths::get(PATH_KLIPPER_CONFIG);
Serial.println(cfg.path);

Print codes

auto c = K2PrintCodes::get(M_28);
Serial.println(c.meaning);
Serial.println(c.context);

Macros

auto m = K2Macros::get(GC_HOME_ALL);
GCodeSender::run(m.gcode);


---

Safe patterns

Pattern: “refuse by default”

Always refuse destructive ops unless explicitly whitelisted.

Pattern: “identity guard”

Before restore/flash, validate:

model

board id (if discoverable)

firmware version

partition layout hash


Pattern: “macro-aware printcode”

When user asks “what is M28?”:

show meaning

show context

show which macros invoke it

show related codes (e.g. M29)



---

Performance and memory notes

ESP32 has enough flash to hold a large registry

If the DB grows huge, switch to:

compress strings

store tables in PROGMEM

split DB into optional components




---

Typical use cases

1) UART G-code injection bridge

connect to MCU or host daemon

send macros by GC_*

validate motion limits

decode errors via signatures


2) Safe backup tool

list critical partitions

offer backup presets (A/B/C/FULL)

refuse writes unless explicit updateable


3) Web UI companion

discover endpoints

validate service readiness

link UI actions to macros and print codes



---

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


---

5) tools/README.md

# tools/ — Extractors + Generators

This directory contains:

1) Extractors: `extract_*.py`
   - Read dumps in `libk2/`
   - Emit normalized JSON into `blueprint/`

2) Generators: `gen_*.py`
   - Read JSON in `blueprint/`
   - Emit static Arduino headers into `DeviceBlueprintLib/src/generated/`

---

## Entry point

```bash
python tools/run_all.py


---

Adding a new extractor

1. Create extract_newthing.py


2. Make it accept:

dump_root

out_json

Paths.json (optional but preferred)



3. Output:

deterministic ordering

stable keys

safe defaults





---

Adding a new generator

1. Create gen_newthing_db.py


2. Input:

the JSON file

output .h path



3. Emit:

simple structs + arrays

no dynamic allocation





---

Windows rules

No mounting disk images

No Linux-only utilities

Only parse files as bytes / text

Use tolerant decoding for mixed encodings



---

---

# 6) `SECURITY.md`

```md
# Security & Safety Model

This project manipulates knowledge about partitions, firmware, and update processes.
It must be safe by default.

---

## Threat model

- User accidentally writes wrong partition → brick
- User restores to wrong device → brick
- Tool guesses offset → corruption
- Malformed dump → wrong data generation

---

## Safety rules

1) sw-description is truth for update intent  
2) GPT is bounds-check only  
3) Unknown partitions are treated as critical  
4) Writes are forbidden unless explicitly updateable  
5) Restore requires identity guard (model/version/layout hash)

---

## Non-goals

- Bypassing secure boot
- Extracting secrets / keys
- Unauthorized access

---

## Responsible use

Use this project only on devices you own or have permission to service.


---

7) CONTRIBUTING.md

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


---

8) FAQ.md

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

