#pragma once
#include <Arduino.h>
#include <FS.h>

#include "core/KeyRegistry.h"
#include "core/ConsoleDetect.h"
#include "core/ScriptRunner.h"
#include "core/GCodeSender.h"
#include "core/FileTransferM28.h"
#include "core/K2SafetyGuard.h"

// Generated static DBs (compile-time)
#include "generated/k2_key_catalog.h"
#include "generated/k2_partitions_db.h"
#include "generated/k2_paths_db.h"
#include "generated/k2_printcodes_db.h"
#include "generated/k2_gcode_macros_db.h"
#include "generated/k2_motion_limits_db.h"

/**
 * High-level facade over blueprint DB + execution helpers.
 *
 * Safety model:
 * - If no guard is attached OR it is not armed -> destructive ops are denied (fail-closed).
 * - Destructive ops currently gated:
 *     - M28/M29 file upload (fileBegin/fileWriteLine/fileEnd/uploadGcodeFromFS)
 *
 * You can also choose to gate scripts (CMD_*) by enabling the check in runScript().
 */
class DeviceBlueprintLib {
public:
  // -------------------------
  // Static init / self-check
  // -------------------------
  static bool init(Stream* debug = nullptr) {
    // Compile-time assertions live in generated headers.
    // Runtime: optional debug banner.
    if (debug) {
      debug->println(F("[DeviceBlueprintLib] init ok"));
      debug->print(F("  partitions: ")); debug->println((unsigned long)K2::K2_PART_COUNT);
      debug->print(F("  macros: "));      debug->println((unsigned long)K2::K2_GC_COUNT);
    }
    return true;
  }

  // -------------------------
  // Setup
  // -------------------------
  bool begin(Stream& target, Stream* debug = nullptr);

  // Attach optional safety guard (recommended). If not attached, destructive ops are denied.
  void attachSafetyGuard(K2SafetyGuard* guard) { _guard = guard; }
  bool armSafety(uint32_t token) { if (!_guard) return false; _guard->arm(token); _guardToken = token; return true; }
  void lockSafety() { if (_guard) _guard->lock(); }

  // Load JSON assets (LittleFS or SD). These are the runtime key->text maps.
  bool loadAssets(const char* gcodeJsonPath,
                  const char* scriptJsonPath,
                  const char* promptsJsonPath);

  // Run key-based ops
  bool runGCode(const char* gcId, uint32_t timeoutMs = 8000);
  bool runScript(const char* cmdId, uint32_t timeoutMs = 15000);

  // Feed raw target chars into console detector (optional)
  void feedTargetChar(char c);

  // -------------------------
  // File transfer (M28/M29)
  // -------------------------
  bool fileBegin(const String& remote);
  bool fileWriteLine(const String& line);
  bool fileEnd();
  bool uploadGcodeFromFS(FS& fs, const String& localPath, const String& remote);

private:
  bool allowFileWrite_() const;

private:
  Stream* _io  = nullptr;
  Stream* _dbg = nullptr;

  K2SafetyGuard* _guard = nullptr;
  uint32_t _guardToken = 0;

  KeyRegistry     _reg;
  ConsoleDetect   _con;
  ScriptRunner    _runner;
  GCodeSender     _gcode;
  FileTransferM28 _ft;
};
