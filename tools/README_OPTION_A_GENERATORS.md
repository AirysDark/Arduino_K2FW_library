# Option A generators (JSON -> DeviceBlueprintLib/src/generated/*.h)

These scripts turn your extracted blueprint JSON into Arduino/ESP32 headers.

## Scripts
- gen_k2_paths_db.py              Paths.json -> k2_paths_db.h
- gen_k2_gcode_macros_db.py       GcodeMacros.json -> k2_gcode_macros_db.h
- gen_k2_printcodes_db.py         PrintCodes.json -> k2_printcodes_db.h
- gen_k2_motion_limits_db.py      MotionConfig.json -> k2_motion_limits_db.h
- gen_k2_services_db.py           Services.json -> k2_services_db.h
- gen_k2_web_endpoints_db.py      WebHints.json -> k2_web_endpoints_db.h
- gen_k2_key_catalog.py           blueprint dir -> k2_key_catalog.h (optional)
- (you already have) gen_k2_partitions_db_from_partitionmap.py

## Typical usage (Windows)
python tools\gen_k2_paths_db.py blueprint\Paths.json DeviceBlueprintLib\src\generated\k2_paths_db.h
python tools\gen_k2_gcode_macros_db.py blueprint\GcodeMacros.json DeviceBlueprintLib\src\generated\k2_gcode_macros_db.h
python tools\gen_k2_printcodes_db.py blueprint\PrintCodes.json DeviceBlueprintLib\src\generated\k2_printcodes_db.h
python tools\gen_k2_motion_limits_db.py blueprint\MotionConfig.json DeviceBlueprintLib\src\generated\k2_motion_limits_db.h
python tools\gen_k2_services_db.py blueprint\Services.json DeviceBlueprintLib\src\generated\k2_services_db.h
python tools\gen_k2_web_endpoints_db.py blueprint\WebHints.json DeviceBlueprintLib\src\generated\k2_web_endpoints_db.h
python tools\gen_k2_key_catalog.py blueprint DeviceBlueprintLib\src\generated\k2_key_catalog.h
