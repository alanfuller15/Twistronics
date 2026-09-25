"""Curved, repaired partial-shift composition. Synthetic analytic fixtures only."""
import hashlib
import importlib.util
from pathlib import Path
import sys
from flint import arb, arb_mat
from primitives_s0f import enclosure, frobenius, identity, NonfiniteEnclosure

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0j_001'))
spec_j=importlib.util.spec_from_file_location('s0j_geometry',HERE.parent/'certification_s0j_001/cases.py')
j=importlib.util.module_from_spec(spec_j);spec_j.loader.exec_module(j)
i,h=j.prior,j.prior.prior
require,Refusal,rot,aa,F=h.require,h.Refusal,h.rot,h.aa,h.F


class Combined:
    def __init__(self,denominator,winding,reverse=False,bump='0',defect='1/4',endpoint_error='0'):
        self.d,self.w,self.reverse=denominator,winding,reverse
        self.defect=aa(defect)
        self.bump=aa(bump)
        self.endpoint_error=aa(endpoint_error)
        require(self.endpoint_error>=0,'NEGATIVE_ERROR')
        self.delta=None

    def c(self,x): return 1-arb(1)/self.d-x/(2*self.d)

    def normal(self,x,y):
        c=self.c(x);s=(1-c*c).sqrt();p=2*arb.pi()*y
        return [s*p.cos(),s*p.sin(),c]

    def frame(self,x,y):
        c=self.c(x);s=(1-c*c).sqrt();p=2*arb.pi()*y
        f=arb_mat([[c*p.cos(),-p.sin()],[c*p.sin(),p.cos()],[-s,0]])
        k=f*rot(-2*arb.pi()*c*y)
        return k*arb_mat([[1,0],[0,-1]]) if self.reverse else k

    ends=h.Geometry.ends
    repair=h.Geometry.repair
    repaired=h.Geometry.repaired

    def ambient(self,edge,t):
        # No frame call: ambient rotations are defined by the analytic normal.
        if edge==2:
            u=j.sewing.rodrigues(self.normal(t,arb(0)),(2*arb.pi()*self.w+self.defect)*t+4*self.bump*t*(1-t))
        else:
            c0,c1=self.c(arb(0)),self.c(arb(1))
            s0,s1=(1-c0*c0).sqrt(),(1-c1*c1).sqrt()
            c,s=c0*c1+s0*s1,s1*c0-c1*s0
            ry=arb_mat([[c,0,s],[0,1,0],[-s,0,c]])
            p=2*arb.pi()*t
            z=arb_mat([[p.cos(),-p.sin(),0],[p.sin(),p.cos(),0],[0,0,1]])
            u=z*ry*z.transpose()
        return arb_mat([[1,0,0],[0,1,0],[0,0,0]])*u

    def seam(self,edge,t,diagnostics=False):
        target,source=self.ends(edge,t)
        left,right=self.frame(*target),self.frame(*source)
        j.orientation(left,self.normal(*target));j.orientation(right,self.normal(*source))
        shift=self.ambient(edge,t)
        m=left.transpose()*shift*right
        u=i.polar(m)
        if not diagnostics: return u
        deletion=right.transpose()*(identity(3)-shift.transpose()*shift)*right
        off=(identity(3)-left*left.transpose())*shift*right
        residual=identity(2)-m.transpose()*m-deletion-off.transpose()*off
        require(all(residual[r,c].contains(0) for r in range(2) for c in range(2)),'DEFICIT_IDENTITY')
        return u,deletion.trace(),(off.transpose()*off).trace(),frobenius(residual)

    def certify(self,sign=1):
        require(sign==1,'EXACT_GLUING_REQUIRED')
        minimum=self.c(arb(1))**2
        require(minimum>=arb(19)/20,'SEAM_SINGULAR_GATE')
        corner=self.repair()
        require(not self.delta.contains(0),'NONZERO_REPAIR_REQUIRED')
        totals=[];debits=[]
        for edge in (1,2):
            total=arb(0)
            speed=arb.pi()/self.d if edge==1 else (2*arb.pi()*self.w-arb.pi()/self.d+self.defect).abs_upper()+self.delta.abs_upper()*arb(15)/8
            if edge==2: speed+=4*self.bump.abs_upper()
            require(speed/64+2*self.endpoint_error<arb.pi()/2,'LIFT_VARIATION')
            for k in range(64):
                u,v=self.repaired(edge,arb(k)/64),self.repaired(edge,arb(k+1)/64)
                total+=h.angle(u.transpose()*v)
            # A declared uniform phase-error model, not a numerical solver bound.
            # Lift errors telescope to the two endpoint errors on each edge.
            totals.append(total+arb(0,2*self.endpoint_error))
            _,deletion,off,residual=self.seam(edge,arb(0),True)
            require(deletion>0 and off>0,'BOTH_DEFICITS_REQUIRED')
            debits.append(dict(edge=edge,origin_deletion=enclosure(deletion),origin_off_target_squared=enclosure(off),identity_residual_F_bound=enclosure(residual),cell_variation_bound=enclosure(speed/64)))
        interval=(totals[1]-totals[0])/(2*arb.pi())
        q=i.integer_from_enclosure(interval)
        return dict(status='CERTIFIED',reason='CURVED_REPAIRED_PARTIAL_CLASS',q=q,q_interval=enclosure(interval),corner=corner,
                    uniform_seam_smin_lower=enclosure(minimum),connection_flux=enclosure(-arb.pi()/self.d),
                    edge_totals=[enclosure(x) for x in totals],deficits=debits,endpoint_phase_error=enclosure(self.endpoint_error),
                    scope='Exact analytic domain premises; finite arithmetic consistency checks')


def relative(a,b):
    # cos(theta_a-theta_b)>=c_a*c_b>=c_a(1)*c_b(1)>1/2.
    lower=a.c(arb(1))*b.c(arb(1))
    require(lower>arb(1)/2,'Q_SINGULAR_GATE')
    def q(x,y): return i.polar(b.frame(x,y).transpose()*a.frame(x,y))
    maximum=arb(0);count=1024
    for edge in (1,2):
        for k in range(count):
            t=arb(arb(2*k+1)/(2*count),arb(1)/(2*count))
            phase=arb(0) if edge==1 else (2*arb.pi()*(b.w-a.w)*t+(b.defect-a.defect)*(t-h.chi(t))+4*(b.bump-a.bump)*t*(1-t))
            distance=2*arb(2).sqrt()*(phase/2).sin().abs_upper()
            if not distance<=1:
                return dict(status='INCONCLUSIVE',reason='JOINT_EDGE_SCREEN',failed_edge=edge,failed_cell=k,distance_F_bound=enclosure(distance))
            maximum=max(maximum,distance.upper())
    # Independent matrix consistency checks of the analytic pullback reduction.
    for edge in (1,2):
        for k in range(9):
            t=arb(k)/8;target,source=a.ends(edge,t)
            pulled=q(*target).transpose()*b.repaired(edge,t)*q(*source)
            phase=arb(0) if edge==1 else (2*arb.pi()*(b.w-a.w)*t+(b.defect-a.defect)*(t-h.chi(t))+4*(b.bump-a.bump)*t*(1-t))
            residual=a.repaired(edge,t).transpose()*pulled-rot(phase)
            require(all(residual[r,c].contains(0) for r in range(2) for c in range(2)),'PULLBACK_IDENTITY')
    return dict(status='CERTIFIED',reason='CURVED_REPAIRED_Q_SCREEN',cells_per_edge=count,max_distance_F_bound=enclosure(maximum),uniform_Q_smin_lower=enclosure(lower))


def run(job,spec):
    try:
        for path,digest in spec['dependencies'].items():
            require(hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest()==digest,'DEPENDENCY_HASH_REFUSED')
        a=Combined(job.get('denominator',128),job['winding'],job['id']=='orientation_fault',endpoint_error=job.get('endpoint_error','0'))
        ar=a.certify(-1 if job['id']=='wrong_repair' else 1)
        if not job['id'].startswith('pair_'): return ar
        b=Combined(160,job['other_winding'],bump=job.get('other_bump','0'),defect=job.get('other_defect','1/4'));br=b.certify()
        return i.combine(ar,br,relative(a,b))
    except Refusal as exc: return dict(status='INCONCLUSIVE',reason=str(exc))
    except NonfiniteEnclosure as exc: return dict(status='INCONCLUSIVE',reason='NONFINITE_ENCLOSURE',message=str(exc))
