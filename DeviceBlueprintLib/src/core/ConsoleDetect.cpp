#include "ConsoleDetect.h"

void ConsoleDetect::reset() {
  _mode = ConsoleMode::Unknown;
  _buf = "";
  _lastLine = "";
}

void ConsoleDetect::setPromptHints(const PromptHints& p) {
  _ubootPrompt = p.ubootPrompt;
  _login = p.linuxLogin;
  _pass  = p.linuxPassword;
  _root  = p.shellRoot;
  _user  = p.shellUser;
}

void ConsoleDetect::feedChar(char c) {
  if (c == '\r') return;
  if (c == '\n') {
    _lastLine = _buf;
    _buf = "";
    classifyLine(_lastLine);
    return;
  }
  if (_buf.length() < 512) _buf += c;
}

void ConsoleDetect::classifyLine(const String& line) {
  if (line.indexOf("U-Boot") >= 0 || line.endsWith(_ubootPrompt)) {
    _mode = ConsoleMode::UBoot; return;
  }
  if (line.indexOf(_login) >= 0) { _mode = ConsoleMode::LinuxLoginUser; return; }
  if (line.indexOf(_pass) >= 0)  { _mode = ConsoleMode::LinuxLoginPass; return; }
  if (line.endsWith(_root) || line.endsWith(_root + " ") ||
      line.endsWith(_user) || line.endsWith(_user + " ")) {
    _mode = ConsoleMode::LinuxShell; return;
  }
}
