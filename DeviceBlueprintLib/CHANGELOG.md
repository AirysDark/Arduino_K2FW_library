# Changelog

## 1.1.0
- Added `K2SafetyGuard` and wired it into file-write APIs (M28/M29 upload) with fail-closed behavior.
- Added `DeviceBlueprintLib::init()` helper for basic runtime banner/self-check.
- Fixed broken/truncated `DeviceBlueprintLib.h`/`.cpp` and made includes consistent.
- Added compile-time `static_assert` sanity checks in generated DB headers.
- Updated `library.properties` version to 1.1.0.
