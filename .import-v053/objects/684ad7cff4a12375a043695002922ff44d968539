"""Boundary witness: common geometry also requires a common cutoff rule."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
def module(folder,name):
    spec=importlib.util.spec_from_file_location(folder+'_'+name,ROOT/folder/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

old_bm=module('provenance/prior_engines','bm_strain');old_ref=module('provenance/prior_engines','tbg_ref')
new_bm=module('engines','bm_strain');new_ref=module('engines','tbg_ref')
PHI=15.843560625048124

def make(which,patched,**extra):
    if which=='bm':return (new_bm if patched else old_bm).BM(N=4,eps=.003,phi_deg=PHI,kinetic='lab_nn_full',geometry='exact',**extra)
    return (new_ref if patched else old_ref).TBG(N=4,eps=.003,phi=PHI,kinetic='lab_nn_full',**extra)

@pytest.mark.parametrize('which,dimension',[('bm',196),('ref',188)])
def test_defaults_preserve_boundary_truncation_and_matrix(which,dimension):
    a,b=make(which,False),make(which,True)
    assert a.dim==b.dim==dimension
    k=lambda m,f:m.frac_to_k(f) if which=='bm' else m.k(f)
    assert np.array_equal(a.H(k(a,[.31,.27])),b.H(k(b,[.31,.27])))

@pytest.mark.parametrize('tol,dimension',[(1e-9,188),(1e-6,196)])
def test_named_common_padding_restores_operator_agreement(tol,dimension):
    a,b=make('bm',True,cutoff_tol=tol),make('ref',True,cutoff_tol=tol)
    assert a.dim==b.dim==dimension and a.idx==b.mn
    for f in [[.31,.27],[1.13,.62]]:
        assert np.max(np.abs(a.H(a.frac_to_k(f))-b.H(b.k(f))))<1e-9

@pytest.mark.parametrize('which',['bm','ref'])
@pytest.mark.parametrize('tol',[-1.,np.nan])
def test_invalid_padding_rejects_instead_of_changing_the_basis(which,tol):
    with pytest.raises(ValueError,match='cutoff_tol'):make(which,True,cutoff_tol=tol)
