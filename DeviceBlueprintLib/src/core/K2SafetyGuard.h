#pragma once
#include <Arduino.h>

/**
 * @brief Safety gate for any destructive operation (writes, partition ops, firmware update).
 *
 * Design goals:
 * - No guessing: only allow operations explicitly permitted by the compiled DB.
 * - Fail-closed: default deny.
 * - Optional "arming" step to prevent accidental calls.
 *
 * This class does NOT perform the write itself. It only validates requests.
 */
class K2SafetyGuard {
public:
  enum class Mode : uint8_t {
    Locked = 0,   ///< default deny
    Armed  = 1    ///< allow validated requests
  };

  struct Range {
    uint64_t base;   ///< absolute base (bytes) in target storage
    uint64_t size;   ///< size (bytes)
    bool     valid;
  };

  void lock() { _mode = Mode::Locked; }

  void arm(uint32_t token) { _mode = Mode::Armed; _token = token; }

  Mode mode() const { return _mode; }

  bool tokenOk(uint32_t token) const { return (_mode == Mode::Armed) && (token == _token) && (_token != 0); }

  bool canWrite(const Range& r, uint64_t offset, uint64_t len) const {
    if (_mode != Mode::Armed) return false;
    if (!r.valid) return false;
    if (len == 0) return false;
    if (offset > r.size) return false;
    if (len > r.size) return false;
    if (offset + len > r.size) return false;
    return true;
  }

private:
  Mode _mode = Mode::Locked;
  uint32_t _token = 0;
};
