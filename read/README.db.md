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