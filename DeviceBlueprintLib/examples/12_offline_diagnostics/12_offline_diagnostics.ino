#include <Arduino.h>
#include "DeviceBlueprintLib.h"

void setup() {
  Serial.begin(115200);
  if (!DeviceBlueprintLib::init()) {
    Serial.println("DB init fail");
    while (1) {}
  }
  Serial.println("=== Offline Diagnostics ===");
  auto p = K2Partitions::get(PART_ROOTFS_A);
  Serial.printf("ROOTFS_A size_bytes=%llu\n", (unsigned long long)p.size_bytes);
  auto c = K2PrintCodes::get(M_28);
  Serial.printf("M28: %s\n", c.meaning);
}

void loop() {}
