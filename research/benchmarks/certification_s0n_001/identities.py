"""Fixed identity controls for the analytic rotation formulas used by D prime."""
from pathlib import Path
import sys
import json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0f_001'))
from combined import Combined,rot,i,h
from flint import arb,ctx
ctx.prec=128;ctx.threads=1

def main():
    a,b=Combined(128,1),Combined(160,1,bump='361/500')
    a.repair();b.repair()
    checked=0
    def check(actual,expected):
        nonlocal checked
        residual=actual-expected
        assert all(residual[r,c].contains(0) and residual[r,c].abs_upper()<arb('1e-28') for r in range(2) for c in range(2))
        checked+=1
    for t in (arb(0),arb(1)/7,arb(1)/2,arb(1)):
        for g in (a,b):
            check(g.repaired(1,t),rot(-arb.pi()*t/g.d))
            phase=-2*arb.pi()/g.d+(2*arb.pi()*g.w-arb.pi()/g.d+g.defect)*t+4*g.bump*t*(1-t)+g.delta*h.chi(t)
            check(g.repaired(2,t),rot(phase))
        for edge in (1,2):
            for x,y in a.ends(edge,t):
                check(i.polar(b.frame(x,y).transpose()*a.frame(x,y)),rot(2*arb.pi()*(b.c(x)-a.c(x))*y))
    print(json.dumps({'status':'PASS_FIXED_ROTATION_IDENTITIES','checks':checked,'precision':128,'physical_evaluations':0,'limitation':'Fixed-point implementation controls; uniform formulas and derivative proof are documented separately.'}))

if __name__=='__main__': main()
