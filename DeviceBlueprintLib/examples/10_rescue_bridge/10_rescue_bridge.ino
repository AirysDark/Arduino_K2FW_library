#include <Arduino.h>
#include "DeviceBlueprintLib.h"
#include "TransportUART.h"
#include "core/K2SafetyGuard.h"

static TransportUART* g_tx = nullptr;
static K2SafetyGuard g_guard;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);

  if (!DeviceBlueprintLib::init()) {
    Serial.println("DB init failed");
    while (1) {}
  }

  static TransportUART uart(Serial2);
  g_tx = &uart;

  g_guard.arm(0xC0FFEE01);

  Serial.println("Rescue bridge ready. Type 'help'.");
}

static void sendLine(const char* s){
  if (!g_tx) return;
  g_tx->sendLine(s);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "help") {
      Serial.println("Commands: uboot | reboot | status");
      return;
    }
    if (cmd == "uboot") {
      sendLine(" ");
      sendLine(" ");
      sendLine(" ");
      Serial.println("Sent interrupt spam (device-specific).");
      return;
    }
    if (cmd == "reboot") {
      sendLine("reboot");
      Serial.println("Sent reboot.");
      return;
    }
    if (cmd == "status") {
      auto p = K2Partitions::get(PART_ROOTFS_A);
      Serial.printf("ROOTFS_A size=%llu\n", (unsigned long long)p.size_bytes);
      return;
    }
    Serial.println("Unknown. Type help.");
  }

  while (Serial2.available()) Serial.write((char)Serial2.read());
}
