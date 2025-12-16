#include "FileTransferM28.h"

bool FileTransferM28::begin(const String& remoteName) {
  if (!_io) return false;
  _io->print("M28 ");
  _io->println(remoteName);
  return waitOk(8000); // some firmwares respond slowly
}

bool FileTransferM28::writeLine(const String& line) {
  if (!_io) return false;
  _io->println(line);
  // Do NOT wait for ok on every line by default; too slow / not always emitted.
  return true;
}

bool FileTransferM28::end() {
  if (!_io) return false;
  _io->println("M29");
  return waitOk(15000);
}

String FileTransferM28::sanitizeLine(String s, bool stripComments, bool stripBlank, bool* skipOut) {
  if (skipOut) *skipOut = false;
  s.replace("\r", "");
  // Remove trailing newline if any
  if (s.endsWith("\n")) s.remove(s.length()-1);

  if (stripComments) {
    int sc = s.indexOf(';');
    if (sc >= 0) s = s.substring(0, sc);
    int hc = s.indexOf('#');
    if (hc >= 0) s = s.substring(0, hc);
  }

  // Trim
  s.trim();

  if (stripBlank && s.length() == 0) {
    if (skipOut) *skipOut = true;
  }
  return s;
}

bool FileTransferM28::uploadFromFS(FS& fs, const String& localPath, const String& remoteName,
                                  bool stripComments, bool stripBlank) {
  if (!_io) return false;
  File f = fs.open(localPath, "r");
  if (!f) return false;

  if (!begin(remoteName)) { f.close(); return false; }

  String line;
  while (f.available()) {
    line = f.readStringUntil('\n');
    bool skip = false;
    String clean = sanitizeLine(line, stripComments, stripBlank, &skip);
    if (skip) continue;
    writeLine(clean);
  }

  f.close();
  return end();
}

bool FileTransferM28::waitOk(uint32_t timeoutMs) {
  if (!_io) return false;
  uint32_t start = millis();
  String buf;
  while (millis() - start < timeoutMs) {
    while (_io->available()) {
      char c = (char)_io->read();
      if (c == '\r') continue;
      if (c == '\n') {
        String line = buf;
        buf = "";
        line.trim();
        if (line.length() == 0) continue;
        // Common success tokens
        if (line == "ok" || line.startsWith("ok") || line.indexOf("Done") >= 0 || line.indexOf("done") >= 0) {
          return true;
        }
        // Some firmwares: "Writing to file: ..." -> treat as ok too
        if (line.indexOf("Writing") >= 0 || line.indexOf("writing") >= 0) {
          return true;
        }
      } else {
        buf += c;
        if (buf.length() > 240) buf.remove(0, 120);
      }
    }
    delay(2);
  }
  // Timeout: still consider success in permissive mode? (keep strict)
  return false;
}
