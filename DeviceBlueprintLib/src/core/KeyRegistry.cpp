#include "KeyRegistry.h"
#include <LittleFS.h>
#include <ArduinoJson.h>

bool KeyRegistry::begin(Stream* debug) {
  _dbg = debug;
  return LittleFS.begin(true);
}

bool KeyRegistry::readFileToString(const char* path, String& out) {
  File f = LittleFS.open(path, "r");
  if (!f) return false;
  out = "";
  while (f.available()) out += (char)f.read();
  f.close();
  return true;
}

bool KeyRegistry::loadPrompts(const char* path) {
  String s;
  if (!readFileToString(path, s)) return false;
  StaticJsonDocument<2048> doc;
  if (deserializeJson(doc, s)) return false;
  _prompts.ubootPrompt   = (const char*)doc["uboot"]["prompt"] | "=>";
  _prompts.linuxLogin    = (const char*)doc["linux"]["login"] | "login:";
  _prompts.linuxPassword = (const char*)doc["linux"]["password"] | "Password:";
  _prompts.shellRoot     = (const char*)doc["linux"]["shell_root"] | "#";
  _prompts.shellUser     = (const char*)doc["linux"]["shell_user"] | "$";
  return true;
}

bool KeyRegistry::loadGCodes(const char* path) {
  String s;
  if (!readFileToString(path, s)) return false;
  DynamicJsonDocument doc(16384);
  if (deserializeJson(doc, s)) return false;
  _gcodes.clear();
  for (JsonPair kv : doc.as<JsonObject>()) {
    GCodeEntry e;
    e.valid = true;
    e.id = kv.key().c_str();
    e.name = (const char*)kv.value()["name"] | "";
    e.text = (const char*)kv.value()["text"] | "";
    e.okToken = (const char*)kv.value()["ok"] | "ok";
    _gcodes.push_back(e);
  }
  return true;
}

bool KeyRegistry::loadScripts(const char* path) {
  String s;
  if (!readFileToString(path, s)) return false;
  DynamicJsonDocument doc(32768);
  if (deserializeJson(doc, s)) return false;
  _scripts.clear();
  for (JsonPair kv : doc.as<JsonObject>()) {
    ScriptEntry e;
    e.valid = true;
    e.id = kv.key().c_str();
    e.name = (const char*)kv.value()["name"] | "";
    e.mode = (const char*)kv.value()["mode"] | "any";
    e.expectPrompt = (const char*)kv.value()["expect"] | "";
    for (JsonVariant v : kv.value()["lines"].as<JsonArray>())
      e.lines.push_back((const char*)v);
    _scripts.push_back(e);
  }
  return true;
}

GCodeEntry KeyRegistry::getGCode(const char* id) const {
  for (auto& e : _gcodes) if (e.id == id) return e;
  return {};
}

ScriptEntry KeyRegistry::getScript(const char* id) const {
  for (auto& e : _scripts) if (e.id == id) return e;
  return {};
}
