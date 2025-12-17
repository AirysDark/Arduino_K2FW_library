#include "KeyRegistry.h"

#include <LittleFS.h>
#include <ArduinoJson.h>

// Safe string getter: returns default if missing or empty
static const char* jstrOr(JsonVariant v, const char* def) {
  if (v.isNull()) return def;
  const char* s = v.as<const char*>();
  if (!s || !*s) return def;
  return s;
}

bool KeyRegistry::begin(Stream* debug) {
  _dbg = debug;

  if (!LittleFS.begin(true)) {
    log("[KeyRegistry] LittleFS.begin() failed");
    return false;
  }
  return true;
}

bool KeyRegistry::readFileToString(const char* path, String& out) {
  File f = LittleFS.open(path, "r");
  if (!f) {
    log(String("[KeyRegistry] open failed: ") + path);
    return false;
  }

  out = "";
  out.reserve((size_t)f.size() + 16);
  while (f.available()) out += (char)f.read();
  f.close();
  return true;
}

bool KeyRegistry::loadPrompts(const char* path) {
  String s;
  if (!readFileToString(path, s)) return false;

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, s);
  if (err) {
    log(String("[KeyRegistry] Prompts JSON error: ") + err.c_str());
    return false;
  }

  _prompts.ubootPrompt   = jstrOr(doc["uboot"]["prompt"],      "=>");
  _prompts.linuxLogin    = jstrOr(doc["linux"]["login"],       "login:");
  _prompts.linuxPassword = jstrOr(doc["linux"]["password"],    "Password:");
  _prompts.shellRoot     = jstrOr(doc["linux"]["shell_root"],  "#");
  _prompts.shellUser     = jstrOr(doc["linux"]["shell_user"],  "$");

  log("[KeyRegistry] Prompts loaded");
  return true;
}

bool KeyRegistry::loadGCodes(const char* path) {
  String s;
  if (!readFileToString(path, s)) return false;

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, s);
  if (err) {
    log(String("[KeyRegistry] GCodes JSON error: ") + err.c_str());
    return false;
  }

  _gcodes.clear();

  JsonObject obj = doc["gcodes"].is<JsonObject>() ? doc["gcodes"].as<JsonObject>()
                                                  : doc.as<JsonObject>();

  for (JsonPair kv : obj) {
    JsonVariant v = kv.value();

    GCodeEntry e;
    e.valid = true;
    e.id = kv.key().c_str();

    if (v.is<const char*>()) {
      e.name = "";
      e.text = jstrOr(v, "");
      e.okToken = "ok";
    } else if (v.is<JsonObject>()) {
      e.name    = jstrOr(v["name"], "");
      e.text    = jstrOr(v["text"], "");
      e.okToken = jstrOr(v["ok"],   "ok");
    } else {
      continue;
    }

    if (e.text.length() == 0) continue;
    _gcodes.push_back(std::move(e));
  }

  log(String("[KeyRegistry] GCodes loaded: ") + _gcodes.size());
  return true;
}

bool KeyRegistry::loadScripts(const char* path) {
  String s;
  if (!readFileToString(path, s)) return false;

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, s);
  if (err) {
    log(String("[KeyRegistry] Scripts JSON error: ") + err.c_str());
    return false;
  }

  _scripts.clear();

  JsonObject obj = doc["scripts"].is<JsonObject>() ? doc["scripts"].as<JsonObject>()
                                                   : doc.as<JsonObject>();

  for (JsonPair kv : obj) {
    JsonVariant v = kv.value();
    if (!v.is<JsonObject>()) continue;

    ScriptEntry e;
    e.valid = true;
    e.id = kv.key().c_str();

    e.name         = jstrOr(v["name"],   "");
    e.mode         = jstrOr(v["mode"],   "any");
    e.expectPrompt = jstrOr(v["expect"], "");

    if (v["lines"].is<JsonArray>()) {
      for (JsonVariant lineV : v["lines"].as<JsonArray>()) {
        const char* line = lineV.as<const char*>();
        if (line && *line) e.lines.push_back(String(line));
      }
    }

    if (e.lines.empty()) continue;
    _scripts.push_back(std::move(e));
  }

  log(String("[KeyRegistry] Scripts loaded: ") + _scripts.size());
  return true;
}

GCodeEntry KeyRegistry::getGCode(const char* id) const {
  if (!id || !*id) return {};
  for (const auto& e : _gcodes) {
    if (e.id.equals(id)) return e;   // correct String compare
  }
  return {};
}

ScriptEntry KeyRegistry::getScript(const char* id) const {
  if (!id || !*id) return {};
  for (const auto& e : _scripts) {
    if (e.id.equals(id)) return e;   // correct String compare
  }
  return {};
}