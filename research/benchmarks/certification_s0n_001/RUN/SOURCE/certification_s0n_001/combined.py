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
    def __init__(self,denominator,winding,reverse=False,bump='0',defect='1/4',endpoint_error='0',repair_error='0',perturb=False,applied_endpoint_error=None):
        self.d,self.w,self.reverse=denominator,winding,reverse
        self.defect=aa(defect)
        self.bump=aa(bump)
        self.endpoint_error=aa(endpoint_error)
        self.applied_error=aa(endpoint_error if applied_endpoint_error is None else applied_endpoint_error)
        require(self.applied_error>=0,'NEGATIVE_APPLIED_ERROR')
        self.repair_error=aa(repair_error)
        self.perturb=perturb
        require(self.repair_error>=0,'NEGATIVE_REPAIR_ERROR')
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
            guard=speed/64+2*self.applied_error+(self.repair_error*arb(15)/8/64 if edge==2 else 0)
            require(guard<arb.pi()/2,'LIFT_VARIATION')
            def sample(k):
                t=arb(k)/64
                # Opposite edge patterns attain the endpoint-error extremes.
                error=(self.applied_error if k%2 else -self.applied_error)
                if k==64: error=self.applied_error
                if edge==1: error=-error
                if not self.perturb: error=arb(0)
                if edge==2 and self.perturb: error+=self.repair_error*h.chi(t)
                return self.repaired(edge,t)*rot(error)
            for k in range(64):
                u,v=sample(k),sample(k+1)
                total+=h.angle(u.transpose()*v)
            # A declared uniform phase-error model, not a numerical solver bound.
            # Lift errors telescope to the two endpoint errors on each edge.
            radius=2*self.endpoint_error+(self.repair_error if edge==2 else 0)
            totals.append(total+arb(0,radius))
            _,deletion,off,residual=self.seam(edge,arb(0),True)
            require(deletion>0 and off>0,'BOTH_DEFICITS_REQUIRED')
            debits.append(dict(edge=edge,origin_deletion=enclosure(deletion),origin_off_target_squared=enclosure(off),identity_residual_F_bound=enclosure(residual),cell_variation_bound=enclosure(speed/64)))
        interval=(totals[1]-totals[0])/(2*arb.pi())
        ledger=dict(q_interval=enclosure(interval),endpoint_phase_error=enclosure(self.endpoint_error),applied_endpoint_error=enclosure(self.applied_error),repair_angle_error=enclosure(self.repair_error),perturbed_samples=self.perturb)
        try: q=i.integer_from_enclosure(interval)
        except Refusal as exc: return dict(status='INCONCLUSIVE',reason=str(exc),**ledger)
        return dict(status='CERTIFIED',reason='CURVED_REPAIRED_PARTIAL_CLASS',q=q,q_interval=enclosure(interval),corner=corner,
                    uniform_seam_smin_lower=enclosure(minimum),connection_flux=enclosure(-arb.pi()/self.d),
                    edge_totals=[enclosure(x) for x in totals],deficits=debits,endpoint_phase_error=enclosure(self.endpoint_error),repair_angle_error=enclosure(self.repair_error),perturbed_samples=self.perturb,
                    scope='Exact analytic domain premises; finite arithmetic consistency checks')


def relative(a,b,count=256,order=2):
    # cos(theta_a-theta_b)>=c_a*c_b>=c_a(1)*c_b(1)>1/2.
    lower=a.c(arb(1))*b.c(arb(1))
    require(lower>arb(1)/2,'Q_SINGULAR_GATE')
    def q(x,y): return i.polar(b.frame(x,y).transpose()*a.frame(x,y))
    require(count in (128,256,4096) and order in (1,2),'FIXED_BUDGET_REQUIRED')
    maximum=arb(0)
    G=arb_mat([[0,-1],[1,0]])
    context=dict(cells_per_edge=count,order=order)
    # Only equal-defect, equal-winding fixture pairs have this exact reference.
    if a.w==b.w and a.defect==b.defect:
        context['synthetic_exact_max_F']=enclosure(2*arb(2).sqrt()*((b.bump-a.bump)/2).sin().abs_upper())
    debits=[]
    for edge in (1,2):
        def speed(g):
            if edge==1: return arb.pi()/g.d
            return (2*arb.pi()*g.w-arb.pi()/g.d+g.defect).abs_upper()+4*g.bump.abs_upper()+g.delta.abs_upper()*arb(15)/8
        # Q=R(2*pi*(c_b-c_a)*y). Bound target and source separately.
        if edge==1:
            qspeed=2*arb.pi()*((b.c(arb(1))-a.c(arb(1))).abs_upper()+(b.c(arb(0))-a.c(arb(0))).abs_upper())
        else:
            qspeed=arb.pi()*(arb(1)/a.d-arb(1)/b.d).abs_upper()
        lipschitz=arb(2).sqrt()*(speed(a)+speed(b)+qspeed)
        def acceleration(g):
            return arb(0) if edge==1 else 8*g.bump.abs_upper()+6*g.delta.abs_upper()
        L2=arb(2).sqrt()*(acceleration(a)+speed(a)**2+acceleration(b)+(speed(b)+qspeed)**2)
        radius=arb(1)/(2*count)
        debit=lipschitz*radius if order==1 else L2*radius**2/2
        debits.append(enclosure(debit))
        for k in range(count):
            t=arb(2*k+1)/(2*count)
            target,source=a.ends(edge,t)
            qt,qs=q(*target),q(*source)
            ja,jb=a.repaired(edge,t),b.repaired(edge,t)
            D=ja-qt.transpose()*jb*qs
            center=frobenius(D)
            if order==2:
                def angular(g):
                    if edge==1: return -arb.pi()/g.d
                    return 2*arb.pi()*g.w-arb.pi()/g.d+g.defect+4*g.bump*(1-2*t)+g.delta*30*t*t*(1-t)**2
                vt=2*arb.pi()*(b.c(arb(1))-a.c(arb(1))) if edge==1 else arb.pi()*(arb(1)/a.d-arb(1)/b.d)
                vs=2*arb.pi()*(b.c(arb(0))-a.c(arb(0))) if edge==1 else arb(0)
                dqt,dqs=qt*G*vt,qs*G*vs
                Dp=ja*G*angular(a)-dqt.transpose()*jb*qs-qt.transpose()*(jb*G*angular(b))*qs-qt.transpose()*jb*dqs
                affine=max(frobenius(D-Dp*radius).upper(),frobenius(D+Dp*radius).upper())
                distance=affine+debit
            else: distance=center+debit
            if not distance<=1:
                return dict(status='INCONCLUSIVE',reason='JOINT_EDGE_SCREEN',failed_edge=edge,failed_cell=k,distance_F_bound=enclosure(distance),center_distance_F=enclosure(center),cell_debit_F=enclosure(debit),**context)
            maximum=max(maximum,distance.upper())
    return dict(status='CERTIFIED',reason='TAYLOR_MATRIX_Q_SCREEN' if order==2 else 'CENTERED_MATRIX_Q_SCREEN',max_distance_F_bound=enclosure(maximum),uniform_Q_smin_lower=enclosure(lower),cell_debits_F=debits,**context)


def run(job,spec):
    try:
        for path,digest in spec['dependencies'].items():
            require(hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest()==digest,'DEPENDENCY_HASH_REFUSED')
        a=Combined(job.get('denominator',128),job['winding'],job['id']=='orientation_fault',endpoint_error=job.get('endpoint_error','0'),repair_error=job.get('repair_error','0'),perturb=job.get('perturb',False),applied_endpoint_error=job.get('applied_endpoint_error'))
        ar=a.certify(-1 if job['id']=='wrong_repair' else 1)
        if not job['id'].startswith('pair_'): return ar
        b=Combined(160,job['other_winding'],bump=job.get('other_bump','0'),defect=job.get('other_defect','1/4'));br=b.certify()
        return i.combine(ar,br,relative(a,b,job.get('cells',256),job.get('order',2)))
    except Refusal as exc: return dict(status='INCONCLUSIVE',reason=str(exc))
    except NonfiniteEnclosure as exc: return dict(status='INCONCLUSIVE',reason='NONFINITE_ENCLOSURE',message=str(exc))
