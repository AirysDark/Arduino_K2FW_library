#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASS = "YOUR_PASS";
const char* MOONRAKER = "http://192.168.1.50:7125";

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) { delay(250); }

  HTTPClient http;
  String url = String(MOONRAKER) + "/printer/info";
  http.begin(url);
  int code = http.GET();
  Serial.printf("GET /printer/info -> %d\n", code);
  Serial.println(http.getString());
  http.end();
}

void loop() {}
