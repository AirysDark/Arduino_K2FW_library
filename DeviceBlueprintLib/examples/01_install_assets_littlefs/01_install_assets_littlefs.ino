
#include <DeviceBlueprintLib.h>

DeviceBlueprintLib lib;

void setup() {
  Serial.begin(115200);
  lib.begin(Serial, &Serial);
  lib.loadAssets("/GcodeMacros.json", "/CommandScripts.json", "/Prompts.json");
}

void loop() {}
