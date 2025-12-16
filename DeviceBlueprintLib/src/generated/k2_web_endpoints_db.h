#pragma once
#include <Arduino.h>
namespace K2 {
struct Endpoint { const char* key; const char* method; const char* path; const char* desc; };
static const size_t K2_ENDPOINT_COUNT = 0;
static const Endpoint K2_ENDPOINTS[K2_ENDPOINT_COUNT] = {
};
} // namespace K2
