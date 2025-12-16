#include "ScriptRunner.h"

void ScriptRunner::begin(Stream& target, ConsoleDetect& console, Stream* debug) {
  _t = &target;
  _con = &console;
  _dbg = debug;
}

bool ScriptRunner::waitForPromptToken(const String& token, uint32_t timeoutMs) {
  if (token.length() == 0) return true;
  uint32_t start = millis();
  while ((millis() - start) < timeoutMs) {
    while (_t->available()) {
      char c = (char)_t->read();
      _con->feedChar(c);
      if (_con->lastLine().endsWith(token)) return true;
    }
    delay(1);
  }
  return false;
}

bool ScriptRunner::runLines(const std::vector<String>& lines,
                            const String& expectPrompt,
                            uint32_t timeoutMs)
{
  for (auto& line : lines) {
    _t->print(line);
    _t->print("\n");
    if (!waitForPromptToken(expectPrompt, timeoutMs)) return false;
  }
  return true;
}
