#pragma once
#include <Arduino.h>
namespace K2 {
struct Partition {
  const char* key;
  const char* name;
  const char* device;
  const char* role;
  int8_t slot;
  bool critical;
  bool updateable;
  uint64_t first_lba;
  uint64_t last_lba;
};
static const size_t K2_PART_COUNT = 4;
static const Partition K2_PARTS[K2_PART_COUNT] = {
  { "PART_DEV_BY_NAME_BOOTA", "/dev/by-name/bootA", "/dev/by-name/bootA", "kernel", (int8_t)-1, true, true, 0ULL, 0ULL },
  { "PART_DEV_BY_NAME_BOOTB", "/dev/by-name/bootB", "/dev/by-name/bootB", "kernel", (int8_t)-1, true, true, 0ULL, 0ULL },
  { "PART_DEV_BY_NAME_ROOTFSA", "/dev/by-name/rootfsA", "/dev/by-name/rootfsA", "rootfs", (int8_t)-1, true, true, 0ULL, 0ULL },
  { "PART_DEV_BY_NAME_ROOTFSB", "/dev/by-name/rootfsB", "/dev/by-name/rootfsB", "rootfs", (int8_t)-1, true, true, 0ULL, 0ULL },
};
} // namespace K2
