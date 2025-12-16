#pragma once
#include <Arduino.h>
#include "KeyRegistry.h"

enum class ConsoleMode : uint8_t {
  Unknown,
  Boot,
  UBoot,
  LinuxLoginUser,
  LinuxLoginPass,
  LinuxShell
};

class ConsoleDetect {
public:
  void reset();
  void setPromptHints(const PromptHints& p);
  void feedChar(char c);
  ConsoleMode mode() const { return _mode; }
  const String& lastLine() const { return _lastLine; }

private:
  ConsoleMode _mode = ConsoleMode::Unknown;
  String _buf;
  String _lastLine;
  String _ubootPrompt = "=>";
  String _login = "login:";
  String _pass = "Password:";
  String _root = "#";
  String _user = "$";
  void classifyLine(const String& line);
};
