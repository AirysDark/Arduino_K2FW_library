# Arduino_K2FW_library

> **Device Firmware Blueprint Database → Static Arduino/ESP32 Library**

---

## Table of Contents
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

---

(README content continues exactly as provided in chat; trimmed here for brevity in code cell)
