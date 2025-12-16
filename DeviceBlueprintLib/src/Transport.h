#pragma once
#include <Arduino.h>

/**
 * @brief Minimal transport interface for sending lines/bytes to a target.
 */
class BlueprintTransport {
public:
  virtual ~BlueprintTransport() = default;
  virtual bool sendLine(const char* line) = 0;
  virtual bool sendBytes(const uint8_t* data, size_t len) = 0;
};
