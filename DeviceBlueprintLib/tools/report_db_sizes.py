#!/usr/bin/env python3
import sys, re
from pathlib import Path

RE_COUNT = re.compile(r'\b([A-Z0-9_]+_COUNT)\b\s*=?\s*(\d+)')
RE_ARRAY = re.compile(r'(?:PROGMEM\s+)?(?:const\s+)?(\w+)\s+(\w+)\s*\[(\d+)\]\s*=\s*\{', re.M)

TYPE_SIZES = {
  'uint8_t': 1, 'char': 1,
  'uint16_t': 2, 'int16_t': 2,
  'uint32_t': 4, 'int32_t': 4,
  'uint64_t': 8, 'int64_t': 8,
}

def main():
  if len(sys.argv) < 2:
    print('usage: report_db_sizes.py <generated_dir>')
    return 2
  gdir = Path(sys.argv[1]).resolve()
  if not gdir.exists():
    print('not found:', gdir)
    return 2

  totals = 0
  counts = {}
  arrays = []

  for h in sorted(gdir.glob('*.h')):
    txt = h.read_text(errors='ignore')

    for m in RE_COUNT.finditer(txt):
      counts[m.group(1)] = int(m.group(2))

    for m in RE_ARRAY.finditer(txt):
      t, name, n = m.group(1), m.group(2), int(m.group(3))
      sz = TYPE_SIZES.get(t)
      if sz:
        bytes_ = sz * n
        arrays.append((h.name, name, t, n, bytes_))
        totals += bytes_

  print('== Counts (if present) ==')
  for k in sorted(counts):
    print(f'  {k}: {counts[k]}')

  print('\n== Arrays (approx) ==')
  if not arrays:
    print('  (no simple arrays detected; DB may be structs/PROGMEM objects)')
  else:
    for fn, name, t, n, bytes_ in arrays:
      print(f'  {fn}: {name} [{n}] {t} ~ {bytes_} bytes')

  print(f'\n== Approx total for detected arrays: {totals} bytes ==')
  print('NOTE: This is an estimate. Struct tables and string pools may not be counted here.')
  return 0

if __name__ == '__main__':
  raise SystemExit(main())
