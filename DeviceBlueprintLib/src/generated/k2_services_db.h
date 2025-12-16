#pragma once
#include <Arduino.h>
namespace K2 {
struct ServiceItem { const char* key; const char* host; const char* port; const char* proto; };
static const size_t K2_SERVICE_COUNT = 33;
static const ServiceItem K2_SERVICES[K2_SERVICE_COUNT] = {
  { "SVC_SVC_ADBD", "", "", "" },
  { "SVC_SVC_APP", "", "", "" },
  { "SVC_SVC_BOARD_INIT", "", "", "" },
  { "SVC_SVC_BOOT", "", "", "" },
  { "SVC_SVC_CRON", "", "", "" },
  { "SVC_SVC_DBUS", "", "", "" },
  { "SVC_SVC_DEVICE_MANAGER", "", "", "" },
  { "SVC_SVC_DONE", "", "", "" },
  { "SVC_SVC_DROPBEAR", "", "", "" },
  { "SVC_SVC_FLUIDD_UDISK", "", "", "" },
  { "SVC_SVC_FSTAB", "", "", "" },
  { "SVC_SVC_GPIO_SWITCH", "", "", "" },
  { "SVC_SVC_HOSTNAME", "", "", "" },
  { "SVC_SVC_KLIPPER", "", "", "" },
  { "SVC_SVC_KLIPPER_MCU", "", "", "" },
  { "SVC_SVC_LED", "", "", "" },
  { "SVC_SVC_LOG", "", "", "" },
  { "SVC_SVC_MCU_UPDATE", "", "", "" },
  { "SVC_SVC_MDNS", "", "", "" },
  { "SVC_SVC_MOONRAKER", "", "", "" },
  { "SVC_SVC_NETWORK", "", "", "" },
  { "SVC_SVC_NGINX", "", "", "" },
  { "SVC_SVC_PLAY", "", "", "" },
  { "SVC_SVC_REFRESH_DEVICE_STATUS", "", "", "" },
  { "SVC_SVC_S99SWUPDATE_AUTORUN", "", "", "" },
  { "SVC_SVC_SYSCTL", "", "", "" },
  { "SVC_SVC_SYSFIXTIME", "", "", "" },
  { "SVC_SVC_SYSNTPD", "", "", "" },
  { "SVC_SVC_SYSTEM", "", "", "" },
  { "SVC_SVC_TEE_SUPPLICANT", "", "", "" },
  { "SVC_SVC_UMOUNT", "", "", "" },
  { "SVC_SVC_WEBRTC", "", "", "" },
  { "SVC_SVC_WIPE_DATA", "", "", "" },
};
} // namespace K2
