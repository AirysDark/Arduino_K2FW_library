# Hardware Clone Controller (Blueprint-driven)

Concept:
- Use MotionConfig + PrintCodes + Macros as a semantic control-plane.
- Provide a hardware controller that can:
  - validate G-code
  - enforce motion limits
  - drive a replacement motion board (or proxy to existing)

This repo provides the *knowledge layer*.
Actual step generation is out-of-scope for Arduino library (must be real-time MCU firmware).
