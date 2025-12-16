#include <Arduino.h>
#include <LittleFS.h>
#include "DeviceBlueprintLib.h"
#include "core/K2SafetyGuard.h"

static DeviceBlueprintLib bp;
static K2SafetyGuard guard;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);

  if (!LittleFS.begin()) {
    Serial.println("LittleFS mount failed");
    while (1) {}
  }

  bp.begin(Serial2, &Serial);
  bp.attachSafetyGuard(&guard);

  // Without arming, uploads are denied:
  // bp.uploadGcodeFromFS(LittleFS, "/test.gcode", "test.gcode") -> false

  bp.armSafety(0xC0FFEE01);

  bool ok = bp.uploadGcodeFromFS(LittleFS, "/test.gcode", "test.gcode");
  Serial.printf("upload ok=%d\n", (int)ok);
}

void loop() {}
