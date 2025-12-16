
#include <DeviceBlueprintLib.h>

DeviceBlueprintLib lib;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);
  lib.begin(Serial2, &Serial);
  lib.loadAssets("/GcodeMacros.json", "/CommandScripts.json", "/Prompts.json");
  lib.runGCode("GC_00012");
  lib.runGCode("GC_M_Z2");
  lib.runScript("CMD_UBOOT_UMS0");
}

void loop() {
  while (Serial2.available())
    lib.feedTargetChar((char)Serial2.read());
}
