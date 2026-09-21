from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from impact_replay import forbid_legacy_calls
from bm_strain import BM


def test_legacy_trap_counts_and_refuses_calls_then_restores():
    original = BM.refine
    with forbid_legacy_calls() as calls:
        with pytest.raises(RuntimeError, match='forbidden'):
            BM.__new__(BM).refine([0, 0], lambda x: 0)
        assert calls['BM.refine'] == 1 and len(calls) == 11
    assert BM.refine is original
