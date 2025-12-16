#pragma once
#include <Arduino.h>
#include <FS.h>

#include "core/KeyRegistry.h"
#include "core/ConsoleDetect.h"
#include "core/ScriptRunner.h"
#include "core/GCodeSender.h"
#include "core/FileTransferM28.h"

class DeviceBlueprintLib {
public:
  // Main startup
  bool begin(Stream& target, Stream* debug = nullptr);

  // Load runtime assets (JSON) into KeyRegistry
  bool loadAssets(const char* gcodeJsonPath,
                  const char* scriptJsonPath,
                  const char* promptsJsonPath);

  // Execute a known key (string ID -> content -> run)
  bool runGCode(const char* gcId, uint32_t timeoutMs = 8000);
  bool runScript(const char* cmdId, uint32_t timeoutMs = 15000);

  // Feed characters from target into console detector
  void feedTargetChar(char c);

public:
  // ==========================
  // File transfer (M28/M29)
  // ==========================
  bool fileBegin(const String& remote) {
    if (!_io) return false;
    _ft.setIO(_io);
    return _ft.begin(remote);
  }

  bool fileWriteLine(const String& line) {
    if (!_io) return false;
    _ft.setIO(_io);
    return _ft.writeLine(line);
  }

  bool fileEnd() {
    if (!_io) return false;
    _ft.setIO(_io);
    return _ft.end();
  }

  bool uploadGcodeFromFS(FS& fs, const String& localPath, const String& remote) {
    if (!_io) return false;
    _ft.setIO(_io);
    return _ft.uploadFromFS(fs, localPath, remote);
  }

private:
  // Unified IO pointer (target UART, TCP stream, etc.)
  Stream* _io  = nullptr;
  Stream* _dbg = nullptr;

  // Core modules
  KeyRegistry    _reg;
  ConsoleDetect  _con;
  ScriptRunner   _runner;
  GCodeSender    _gcode;
  FileTransferM28 _ft;
};