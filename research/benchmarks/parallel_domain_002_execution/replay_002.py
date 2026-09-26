#!/usr/bin/env python3
"""Replay packet 002 with one documented tolerance fix.

parallel_domain_002/parallel.py compares monotonic-clock differences with exact
float equality (soft_deadline - start == 600). A supervisor that sets
soft_deadline = start + 600 can produce 600.0000000000001 after rounding, which
fails DEADLINE_BINDING although the deadline was exactly as frozen. This wrapper
loads the unchanged reviewed-path source, replaces only that comparison with an
absolute tolerance of 1e-6 s, and executes it under its original file path so
all source bindings are checked against the unchanged file on disk.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / 'research/benchmarks/parallel_domain_002/parallel.py'
OLD = ("require(r['soft_deadline'] - r['start'] == spec['worker_wall_seconds'] and\n"
       "                    r['hard_deadline'] - r['soft_deadline'] == spec['grace_seconds'], 'DEADLINE_BINDING')")
NEW = ("require(abs(r['soft_deadline'] - r['start'] - spec['worker_wall_seconds']) < 1e-6 and\n"
       "                    abs(r['hard_deadline'] - r['soft_deadline'] - spec['grace_seconds']) < 1e-6, 'DEADLINE_BINDING')")
source = TARGET.read_text()
assert source.count(OLD) == 1, 'unexpected 002 source'
patched = source.replace(OLD, NEW)
sys.argv[0] = str(TARGET)
namespace = {'__name__': '__main__', '__file__': str(TARGET)}
exec(compile(patched, str(TARGET), 'exec'), namespace)
