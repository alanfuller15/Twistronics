from pathlib import Path
import os
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engines'))
import pytest
import euler
import braid
import knobs


@pytest.mark.parametrize('function,args', [(euler.euler, (None,)), (braid.adjacent_nodes, (None,)),
    (braid.transport, (None, None, None, None)), (braid.node_winding, (None, None, None, None, None, None)), (knobs.analyse, (None,))])
def test_legacy_entries_refuse_unqualified_acceptance(function, args):
    with pytest.raises(ValueError, match='exploratory'):
        function(*args)


@pytest.mark.parametrize('optimized', [False, True])
def test_runtime_guards_survive_python_optimization(optimized):
    engine = Path(__file__).resolve().parents[1] / 'engines'
    code = '''import numpy as np
from euler import real_frame
from knobs import add_harmonic
class M:
 dim=2
 def H(self,k):return np.array([[0,1j],[-1j,0]])
try:real_frame(M(),np.eye(2),[0,0])
except ValueError:pass
else:raise RuntimeError('reality guard disappeared')
class Bad:
 nG=1;w1=1.;pos={(0,0):0};Hstat=np.full((4,4),np.nan,dtype=complex)
try:add_harmonic(Bad(),0,np.eye(2))
except ValueError:pass
else:raise RuntimeError('harmonic guard disappeared')
'''
    proc = subprocess.run([sys.executable, '-B'] + (['-O'] if optimized else []) + ['-c', code],
        cwd=engine, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stdout + proc.stderr
