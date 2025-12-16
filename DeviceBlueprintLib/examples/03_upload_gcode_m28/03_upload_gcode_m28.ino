#include <Arduino.h>
#include <LittleFS.h>
#include <DeviceBlueprintLib.h>

// This example assumes:
//  - Your Serial is connected to the target printer/firmware console
//  - You have a local file in LittleFS at /job.gcode
//
// Flow:
//  - M28 job.gcode
//  - stream local lines
//  - M29

DeviceBlueprintLib lib;

void setup() {
  Serial.begin(115200);
  delay(500);

  LittleFS.begin(true);

  lib.begin(&Serial);

  bool ok = lib.uploadGcodeFromFS(LittleFS, "/job.gcode", "job.gcode");
  Serial.println(ok ? "[OK] upload" : "[FAIL] upload");
}

void loop() {}
