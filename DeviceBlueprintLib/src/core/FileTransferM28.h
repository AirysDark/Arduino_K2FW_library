#pragma once
#include <Arduino.h>
#include <FS.h>

// M28/M29 file streaming (virtual SD / SD write)
// Typical flow:
//   M28 filename.gcode
//   <stream gcode lines>
//   M29
//
// This class is transport-agnostic: it writes to a Stream (UART/TCP bridge).
class FileTransferM28 {
public:
  explicit FileTransferM28(Stream* io=nullptr) : _io(io) {}

  void setIO(Stream* io) { _io = io; }

  bool begin(const String& remoteName);
  bool writeLine(const String& line);
  bool end();

  // Convenience: upload a local file (LittleFS/SD/etc) to remote using M28/M29.
  bool uploadFromFS(FS& fs, const String& localPath, const String& remoteName,
                    bool stripComments=true, bool stripBlank=true);

private:
  Stream* _io = nullptr;

  bool waitOk(uint32_t timeoutMs=5000);
  static String sanitizeLine(String s, bool stripComments, bool stripBlank, bool* skipOut);
};
