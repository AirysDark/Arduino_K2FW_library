#include "GCodeSender.h"

void GCodeSender::begin(Stream& target, Stream* debug) {
  _t = &target;
  _dbg = debug;
}

bool GCodeSender::waitForOk(const String& okToken, uint32_t timeoutMs) {
  if (okToken.length()==0) return true;
  String line;
  uint32_t start = millis();
  while ((millis()-start) < timeoutMs) {
    while (_t->available()) {
      char c = (char)_t->read();
      if (c=='\r') continue;
      if (c=='\n') {
        if (line.indexOf(okToken) >= 0) return true;
        line = "";
      } else {
        if (line.length() < 256) line += c;
      }
    }
    delay(1);
  }
  return false;
}

bool GCodeSender::sendAndWaitOk(const String& gcode,
                                const String& okToken,
                                uint32_t timeoutMs)
{
  _t->print(gcode);
  return waitForOk(okToken, timeoutMs);
}
