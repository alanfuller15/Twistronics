"""Frozen synthetic fixtures, kept outside the certification decisions."""
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'certification_s0b_001'))
from arithmetic import cell_family
from certified import ledger, certify_shift, certify_pair, identity
from flint import arb, arb_mat


def selections(labels, windows):
    out=[]
    for s in (Fraction(v) for w in windows for v in w):
        below=sorted([i for i,d in enumerate(labels) if d<s],key=lambda i:(s-labels[i],i))[:2]
        above=sorted([i for i,d in enumerate(labels) if d>s],key=lambda i:(labels[i]-s,i))[:2]
        out.append(below+above)
    return out


def diagonal(values):
    return arb_mat([[values[i] if i==j else 0 for j in range(len(values))] for i in range(len(values))])


def run(job,spec):
    kind=job['kind']
    if kind=='ledger':
        l=spec['ledger']
        return ledger(l['frame_error'],l['seam_map_error'],job['repair'],l['additional_phase_error'],l['q_halfwidth'])
    if kind=='inverse':
        center=diagonal([-3,-2,-1,1,2,3])
        cell=diagonal([arb(-3,4),-2,-1,1,2,3])
        if job['mode']=='center':
            center=cell
        return certify_shift(center,cell,[2,1,3,4])
    if kind=='dimension_fault':
        return certify_shift(arb_mat(6,5),identity(6),[1,2,3,4])
    if kind=='cell':
        k0,kx,gram,d=cell_family(job['dimension'])
        return certify_pair(k0,kx,gram,job['width'],spec['windows'],selections(d,spec['windows']),job['pair'])
    if kind in ('small_cell','gram'):
        d=[-4,-3,0,0,3,4]
        gram=identity(6)
        if kind=='gram':
            gram[0,0]=arb(1,2)
        return certify_pair(diagonal(d),arb_mat(6,6),gram,'0',spec['windows'],selections(d,spec['windows']),job.get('pair',[2,3]))
    raise ValueError('unknown fixed fixture kind')
