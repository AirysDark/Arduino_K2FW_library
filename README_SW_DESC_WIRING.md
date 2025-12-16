# sw-description -> PartitionMap.json -> Arduino static DB

## 1) Extract PartitionMap from sw-description (truth)

Windows:
  python tools\extract_partition_map_from_swdesc.py libk2 blueprint\PartitionMap.json

Optional bounds-check with existing GPT PartitionMap (if you have it):
  python tools\extract_partition_map_from_swdesc.py libk2 blueprint\PartitionMap.json blueprint\PartitionMap_GPT.json

## 2) Generate Arduino header DB

  python tools\gen_k2_partitions_db_from_partitionmap.py blueprint\PartitionMap.json DeviceBlueprintLib\src\generated\k2_partitions_db.h

## 3) Use on ESP32

Include:
  #include "src/core/K2Layout.h"

Example:
  auto p = K2::Layout::findByDevice("/dev/mmcblk0p7");
