#pragma once
#include "Transport.h"

class TransportUART : public BlueprintTransport {
public:
  explicit TransportUART(Stream& s) : _s(s) {}
  bool sendLine(const char* line) override { _s.println(line); return true; }
  bool sendBytes(const uint8_t* data, size_t len) override { return _s.write(data, len) == len; }
private:
  Stream& _s;
};
