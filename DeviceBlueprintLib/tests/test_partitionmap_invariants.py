import json
from pathlib import Path

def test_partitionmap_has_partitions():
    p = Path('blueprint/PartitionMap.json')
    if not p.exists():
        return
    data = json.loads(p.read_text())
    parts = data.get('partitions') or {}
    assert isinstance(parts, dict)
    assert len(parts) >= 1

def test_no_overlaps_if_lba_present():
    p = Path('blueprint/PartitionMap.json')
    if not p.exists():
        return
    data = json.loads(p.read_text())
    parts = data.get('partitions') or {}
    spans = []
    for k, v in parts.items():
        a = v.get('first_lba')
        b = v.get('last_lba')
        if a is None or b is None:
            continue
        spans.append((int(a), int(b), k))
    spans.sort()
    for i in range(1, len(spans)):
        prev = spans[i-1]
        cur = spans[i]
        assert cur[0] > prev[1], f'Overlap: {prev[2]} vs {cur[2]}'
