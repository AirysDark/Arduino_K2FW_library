#pragma once
#include <Arduino.h>
#include "../generated/k2_partitions_db.h"

namespace K2 {

class Layout {
public:
  static const Partition* findByKey(const char* key) {
    if (!key) return nullptr;
    for (size_t i=0;i<K2_PART_COUNT;i++) {
      if (strcmp(K2_PARTS[i].key, key) == 0) return &K2_PARTS[i];
    }
    return nullptr;
  }

  static const Partition* findByDevice(const char* device) {
    if (!device) return nullptr;
    for (size_t i=0;i<K2_PART_COUNT;i++) {
      if (strcmp(K2_PARTS[i].device, device) == 0) return &K2_PARTS[i];
    }
    return nullptr;
  }

  static uint64_t sizeBytes(const Partition& p) {
    if (p.last_lba < p.first_lba || (p.first_lba==0 && p.last_lba==0)) return 0;
    return (uint64_t)(p.last_lba - p.first_lba + 1ULL) * 512ULL;
  }

  static bool canWrite(const Partition& p) {
    // Safe default: only write partitions explicitly marked updateable AND not critical.
    return p.updateable && !p.critical;
  }

  static void forEach(void (*fn)(const Partition& p)) {
    if (!fn) return;
    for (size_t i=0;i<K2_PART_COUNT;i++) fn(K2_PARTS[i]);
  }
};

} // namespace K2
