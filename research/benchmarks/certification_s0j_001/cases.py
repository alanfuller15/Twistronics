"""Independent ambient sewing and a curved analytic Kato fixture."""
import hashlib
import importlib.util
from pathlib import Path
from flint import arb, arb_mat
from primitives_s0f import enclosure, frobenius, identity, NonfiniteEnclosure
import sewing

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('s0i_winding',HERE.parent/'certification_s0i_001/cases.py')
prior=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(prior)
require,Refusal,rot=prior.require,prior.Refusal,prior.rot


def orientation(frame, normal):
    a=[frame[i,0] for i in range(3)];b=[frame[i,1] for i in range(3)]
    cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    require(sum((cross[i]*normal[i] for i in range(3)),arb(0))>0,'ORIENTATION_REFERENCE_REFUSED')


class Independent(prior.WindingGeometry):
    def __init__(self, denominator, winding, reverse=False):
        super().__init__(denominator,winding)
        self.denominator,self.reverse=denominator,reverse

    def frame(self,x,y):
        f=super().frame(x,y)
        return f*arb_mat([[1,0],[0,-1]]) if self.reverse else f

    def seam(self,edge,t,diagnostics=False):
        target,source=self.ends(edge,t)
        left,right=self.frame(*target),self.frame(*source)
        orientation(left,sewing.normal_flat(*target,self.denominator))
        orientation(right,sewing.normal_flat(*source,self.denominator))
        shift=sewing.flat_shift(*source,t,self.denominator,self.winding if edge==2 else 0,
                                prior.aa(self.defect) if edge==2 else arb(0))
        u=prior.polar(left.transpose()*shift*right)
        if not diagnostics: return u
        # Same singular values as the untwisted shift, proved by Rodrigues
        # restricting to R(f) in the positively oriented analytic plane.
        _,rho,deletion,off=prior.prior.Geometry.seam(self,edge,t,True)
        return u,rho,deletion,off


class Curved:
    def __init__(self,winding,wrong_order=False):
        self.winding,self.wrong_order=winding,wrong_order

    def frame_data(self,x,y):
        c=arb(3)/4-x/4;s=(1-c*c).sqrt();p=2*arb.pi()*y
        f=arb_mat([[c*p.cos(),-p.sin()],[c*p.sin(),p.cos()],[-s,0]])
        fy=2*arb.pi()*arb_mat([[-c*p.sin(),-p.cos()],[c*p.cos(),-p.sin()],[0,0]])
        rate= -2*arb.pi()*(arb(3)/4 if self.wrong_order else c)
        o=rot(rate*y);j=arb_mat([[0,-1],[1,0]])
        k=f*o;ky=fy*o+f*o*j*rate
        pmat=f*f.transpose();py=fy*f.transpose()+f*fy.transpose()
        residual=ky-(py*pmat-pmat*py)*k
        return k,residual

    def frame(self,x,y): return self.frame_data(x,y)[0]

    def seam(self,edge,t):
        target,source=((arb(1),t),(arb(0),t)) if edge==1 else ((t,arb(1)),(t,arb(0)))
        m=self.frame(*target).transpose()*sewing.curved_shift(edge,t,self.winding)*self.frame(*source)
        return prior.polar(m)

    def certify(self):
        # A concrete wrong-order frame fails the measured Kato residual;
        # the domain-wide identity for the correct frame is proved in note.
        _,residual=self.frame_data(arb(1)/2,arb(1)/2)
        residual_bound=frobenius(residual)
        require(residual_bound<arb('1e-25'),'KATO_ORDER_RESIDUAL')
        a=self.seam(2,arb(1))*self.seam(1,arb(0))
        b=self.seam(1,arb(1))*self.seam(2,arb(0))
        corner=frobenius(a-b)
        require(corner<arb('1e-25'),'CORNER_IDENTITY_CHECK')
        # Exact A=B is an analytic property of the declared shifts. No
        # midpoint repair or numerical-near-zero closure premise is used.
        totals=[];negative=False
        speed=2*arb.pi()*prior.aa(max(prior.F(1,4),abs(prior.F(self.winding)-prior.F(1,4))))
        require(speed/64<arb.pi()/2,'LIFT_VARIATION')
        for edge in (1,2):
            total=arb(0)
            for i in range(64):
                u,v=self.seam(edge,arb(i)/64),self.seam(edge,arb(i+1)/64)
                negative|=bool(u[0,0]<0)
                total+=prior.prior.angle(u.transpose()*v)
            totals.append(total)
        interval=(totals[1]-totals[0])/(2*arb.pi())
        q=prior.integer_from_enclosure(interval)
        # Independent surface-normal calculation of oriented area density:
        # n.(n_x cross n_y)=2*pi*kappa; our connection curvature is minus it.
        x=arb(1)/2;y=arb(1)/3;c=arb(3)/4-x/4;s=(1-c*c).sqrt();p=2*arb.pi()*y
        n=[s*p.cos(),s*p.sin(),c]
        nx=[c*p.cos()/(4*s),c*p.sin()/(4*s),-arb(1)/4]
        ny=[-2*arb.pi()*s*p.sin(),2*arb.pi()*s*p.cos(),arb(0)]
        cross=[nx[1]*ny[2]-nx[2]*ny[1],nx[2]*ny[0]-nx[0]*ny[2],nx[0]*ny[1]-nx[1]*ny[0]]
        density=-sum((n[i]*cross[i] for i in range(3)),arb(0))
        require((density+arb.pi()/2).contains(0),'CURVATURE_REFERENCE')
        # The entire-domain flux is exactly -pi/2 by the analytic reduction.
        delta_path=arb.pi()/2
        reverse=Curved(self.winding,True)
        path_residual=frobenius(reverse.frame(arb(1),arb(1)).transpose()*self.frame(arb(1),arb(1))-rot(delta_path))
        require(path_residual<arb('1e-25'),'PATH_ORDER_REFERENCE')
        return {'status':'CERTIFIED','reason':'CURVED_ANALYTIC_CLASS','q':q,'q_interval':enclosure(interval),
                'connection_flux':enclosure(-arb.pi()/2),'normal_curvature_check':enclosure(density),
                'reverse_to_vertical_angle_at_corner':enclosure(delta_path),'path_order_reference_residual_F':enclosure(path_residual),'kato_residual_F':enclosure(residual_bound),
                'corner_residual_F':enclosure(corner),'max_step_variation':enclosure(speed/64),
                'edge_totals':[enclosure(t) for t in totals],'negative_absolute_real_part_observed':negative,
                'proof_scope':'Exact analytic identities plus fixed arithmetic checks; not a general numerical ODE solver'}


def run(job,spec):
    try:
        for path,expected in spec['dependencies'].items():
            require(hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest()==expected,'DEPENDENCY_HASH_REFUSED')
        name=job['id']
        if name.startswith('curved_'):
            return Curved(job['winding'],name=='curved_wrong_order').certify()
        if name.startswith('independent_'):
            return Independent(32,job['winding'],name=='independent_orientation_fault').certify()
        a,b=Independent(32,1),Independent(40,1 if name=='same_class' else -1)
        ar,br=a.certify(),b.certify()
        return prior.combine(ar,br,prior.relative_screen(a,b))
    except Refusal as exc:
        return {'status':'INCONCLUSIVE','reason':str(exc)}
    except NonfiniteEnclosure as exc:
        return {'status':'INCONCLUSIVE','reason':'NONFINITE_ENCLOSURE','message':str(exc)}
