#pragma once
#include <Arduino.h>
#include "core/KeyRegistry.h"
#include "core/ConsoleDetect.h"
#include "core/ScriptRunner.h"
#include "core/GCodeSender.h"
#include "core/FileTransferM28.h"

class DeviceBlueprintLib {
public:
  // File transfer (M28/M29)
  bool fileBegin(const String& remote) { _ft.setIO(_io); return _ft.begin(remote); }
  bool fileWriteLine(const String& line) { _ft.setIO(_io); return _ft.writeLine(line); }
  bool fileEnd() { _ft.setIO(_io); return _ft.end(); }
  bool uploadGcodeFromFS(FS& fs, const String& localPath, const String& remote) { _ft.setIO(_io); return _ft.uploadFromFS(fs, localPath, remote); }


public:
  bool begin(Stream& target, Stream* debug = nullptr);
  bool loadAssets(const char* gcodeJsonPath,
                  const char* scriptJsonPath,
                  const char* promptsJsonPath);
  bool runGCode(const char* gcId, uint32_t timeoutMs = 8000);
  bool runScript(const char* cmdId, uint32_t timeoutMs = 15000);
  void feedTargetChar(char c);

private:
  Stream* _target = nullptr;
  Stream* _dbg    = nullptr;
  KeyRegistry _reg;
  ConsoleDetect _con;
  ScriptRunner _runner;
  GCodeSender _gcode;
};
