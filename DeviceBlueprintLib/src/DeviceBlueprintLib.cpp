#include "DeviceBlueprintLib.h"

bool DeviceBlueprintLib::begin(Stream& target, Stream* debug) {
  _io  = &target;
  _dbg = debug;
  _runner.begin(target, _con, debug);
  _gcode.begin(target, debug);
  return true;
}

bool DeviceBlueprintLib::loadAssets(const char* gcodeJsonPath,
                                    const char* scriptJsonPath,
                                    const char* promptsJsonPath)
{
  if (!_reg.begin(_dbg)) return false;

  if (promptsJsonPath && *promptsJsonPath) {
    if (!_reg.loadPrompts(promptsJsonPath)) return false;
    _con.setPromptHints(_reg.prompts());
  }

  if (gcodeJsonPath && *gcodeJsonPath) {
    if (!_reg.loadGCodes(gcodeJsonPath)) return false;
  }

  if (scriptJsonPath && *scriptJsonPath) {
    if (!_reg.loadScripts(scriptJsonPath)) return false;
  }

  return true;
}

bool DeviceBlueprintLib::runGCode(const char* gcId, uint32_t timeoutMs) {
  if (!gcId || !*gcId) return false;
  auto gc = _reg.getGCode(gcId);
  if (!gc.valid) return false;
  return _gcode.sendAndWaitOk(gc.text, gc.okToken, timeoutMs);
}

bool DeviceBlueprintLib::runScript(const char* cmdId, uint32_t timeoutMs) {
  if (!cmdId || !*cmdId) return false;

  // Optional: gate scripts too
  // if (_guard && !_guard->allow(K2SafetyGuard::Op::ScriptRun, _guardToken, true)) return false;

  auto sc = _reg.getScript(cmdId);
  if (!sc.valid) return false;
  return _runner.runLines(sc.lines, sc.expectPrompt, timeoutMs);
}

void DeviceBlueprintLib::feedTargetChar(char c) {
  _con.feedChar(c);
}

bool DeviceBlueprintLib::allowFileWrite_() const {
  if (!_guard) return false; // fail-closed
  return _guard->allow(K2SafetyGuard::Op::FileWrite, _guardToken, true);
}

bool DeviceBlueprintLib::fileBegin(const String& remote) {
  if (!_io) return false;
  if (!allowFileWrite_()) return false;
  _ft.setIO(_io);
  return _ft.begin(remote);
}

bool DeviceBlueprintLib::fileWriteLine(const String& line) {
  if (!_io) return false;
  if (!allowFileWrite_()) return false;
  _ft.setIO(_io);
  return _ft.writeLine(line);
}

bool DeviceBlueprintLib::fileEnd() {
  if (!_io) return false;
  if (!allowFileWrite_()) return false;
  _ft.setIO(_io);
  return _ft.end();
}

bool DeviceBlueprintLib::uploadGcodeFromFS(FS& fs, const String& localPath, const String& remote) {
  if (!_io) return false;
  if (!allowFileWrite_()) return false;
  _ft.setIO(_io);
  return _ft.uploadFromFS(fs, localPath, remote);
}
