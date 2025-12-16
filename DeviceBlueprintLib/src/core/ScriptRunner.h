#pragma once
#include <Arduino.h>
#include <vector>
#include "ConsoleDetect.h"

class ScriptRunner {
public:
  void begin(Stream& target, ConsoleDetect& console, Stream* debug=nullptr);
  bool runLines(const std::vector<String>& lines,
                const String& expectPrompt,
                uint32_t timeoutMs);

private:
  Stream* _t = nullptr;
  Stream* _dbg = nullptr;
  ConsoleDetect* _con = nullptr;
  bool waitForPromptToken(const String& token, uint32_t timeoutMs);
};
