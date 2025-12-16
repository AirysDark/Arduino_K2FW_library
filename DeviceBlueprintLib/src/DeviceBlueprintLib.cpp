#include "DeviceBlueprintLib.h"

bool DeviceBlueprintLib::begin(Stream& target, Stream* debug) {
  _target = &target;
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
  if (!_reg.loadPrompts(promptsJsonPath)) return false;
  if (!_reg.loadGCodes(gcodeJsonPath)) return false;
  if (!_reg.loadScripts(scriptJsonPath)) return false;
  _con.setPromptHints(_reg.prompts());
  return true;
}

bool DeviceBlueprintLib::runGCode(const char* gcId, uint32_t timeoutMs) {
  auto gc = _reg.getGCode(gcId);
  if (!gc.valid) return false;
  return _gcode.sendAndWaitOk(gc.text, gc.okToken, timeoutMs);
}

bool DeviceBlueprintLib::runScript(const char* cmdId, uint32_t timeoutMs) {
  auto sc = _reg.getScript(cmdId);
  if (!sc.valid) return false;
  return _runner.runLines(sc.lines, sc.expectPrompt, timeoutMs);
}

void DeviceBlueprintLib::feedTargetChar(char c) {
  _con.feedChar(c);
}
