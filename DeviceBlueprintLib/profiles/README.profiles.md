# Multi-device Profile Support

Recommended layout:

profiles/
  k2_plus/
    blueprint/
    generated/
  other_device/
    blueprint/
    generated/

Compile-time selection idea:
- build flag: -D DEVICE_PROFILE_K2_PLUS
- include profile generated headers under generated/<profile>/
