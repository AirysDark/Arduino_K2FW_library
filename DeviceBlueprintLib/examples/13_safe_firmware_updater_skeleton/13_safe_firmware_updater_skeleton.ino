#include <Arduino.h>
#include "DeviceBlueprintLib.h"
#include "core/K2SafetyGuard.h"

static K2SafetyGuard guard;

void setup() {
  Serial.begin(115200);
  if (!DeviceBlueprintLib::init()) {
    Serial.println("DB init failed");
    while (1) {}
  }
  guard.arm(0xC0FFEE01);

  auto part = K2Partitions::get(PART_ROOTFS_B);

  K2SafetyGuard::Range r;
  r.base  = (uint64_t)part.first_lba * 512ULL;
  r.size  = (uint64_t)part.size_bytes;
  r.valid = true;

  if (!guard.canWrite(r, 0, 4096)) {
    Serial.println("WRITE DENIED");
    while (1) {}
  }
  Serial.println("WRITE ALLOWED (implement transport)");
}

void loop() {}
