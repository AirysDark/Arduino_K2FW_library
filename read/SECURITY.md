---

# 6) `SECURITY.md`

```md
# Security & Safety Model

This project manipulates knowledge about partitions, firmware, and update processes.
It must be safe by default.

---

## Threat model

- User accidentally writes wrong partition → brick
- User restores to wrong device → brick
- Tool guesses offset → corruption
- Malformed dump → wrong data generation

---

## Safety rules

1) sw-description is truth for update intent  
2) GPT is bounds-check only  
3) Unknown partitions are treated as critical  
4) Writes are forbidden unless explicitly updateable  
5) Restore requires identity guard (model/version/layout hash)

---

## Non-goals

- Bypassing secure boot
- Extracting secrets / keys
- Unauthorized access

---

## Responsible use

Use this project only on devices you own or have permission to service.