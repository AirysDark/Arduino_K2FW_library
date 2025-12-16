#pragma once
#include <Arduino.h>

class GCodeSender {
public:
  void begin(Stream& target, Stream* debug=nullptr);
  bool sendAndWaitOk(const String& gcode,
                     const String& okToken,
                     uint32_t timeoutMs);

private:
  Stream* _t=nullptr;
  Stream* _dbg=nullptr;
  bool waitForOk(const String& okToken, uint32_t timeoutMs);
};
