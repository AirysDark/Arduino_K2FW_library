#pragma once
#include <Arduino.h>
#include <vector>

struct PromptHints {
  String ubootPrompt;
  String linuxLogin;
  String linuxPassword;
  String shellRoot;
  String shellUser;
};

struct GCodeEntry {
  bool   valid = false;
  String id;
  String name;
  String text;
  String okToken;
};

struct ScriptEntry {
  bool valid = false;
  String id;
  String name;
  String mode;
  std::vector<String> lines;
  String expectPrompt;
};

class KeyRegistry {
public:
  bool begin(Stream* debug = nullptr);

  bool loadPrompts(const char* path);
  bool loadGCodes(const char* path);
  bool loadScripts(const char* path);

  const PromptHints& prompts() const { return _prompts; }

  GCodeEntry  getGCode(const char* id) const;
  ScriptEntry getScript(const char* id) const;

private:
  Stream* _dbg = nullptr;

  PromptHints _prompts;
  std::vector<GCodeEntry>  _gcodes;
  std::vector<ScriptEntry> _scripts;

  bool readFileToString(const char* path, String& out);

  inline void log(const String& s) const { if (_dbg) _dbg->println(s); }
};