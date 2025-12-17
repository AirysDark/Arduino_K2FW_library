#pragma once
#include <Arduino.h>
namespace K2 {
struct MacroItem { const char* key; const char* gcode; const char* desc; };
static const size_t K2_GC_COUNT = 0;
static const MacroItem K2_MACROS[K2_GC_COUNT] = {
};
} // namespace K2
