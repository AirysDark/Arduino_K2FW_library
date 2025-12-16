#pragma once
#include <Arduino.h>

/**
 * Safety gate for destructive operations.
 *
 * Default is Locked (deny).
 * Call arm(token) to enable.
 */
class K2SafetyGuard {
public:
  enum class Mode : uint8_t { Locked = 0, Armed = 1 };

  enum class Op : uint8_t {
    FileWrite = 0,
    ScriptRun = 1,
    RawWrite  = 2
  };

  struct Range {
    uint64_t base;
    uint64_t size;
    bool     valid;
  };

  void lock() { _mode = Mode::Locked; }
  void arm(uint32_t token) { _mode = Mode::Armed; _token = token; }

  Mode mode() const { return _mode; }
  bool tokenOk(uint32_t token) const { return (_mode == Mode::Armed) && (token == _token) && (_token != 0); }

  bool allow(Op /*op*/, uint32_t token, bool requireToken=true) const {
    if (_mode != Mode::Armed) return false;
    if (!requireToken) return true;
    return tokenOk(token);
  }

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
