"""Ambient sewing definitions. Intentionally independent of frame code."""
from flint import arb, arb_mat


def normal_flat(x, y, denominator):
    t=arb(1)/denominator
    c,s=(1-t*t)/(1+t*t),2*t/(1+t*t)
    phi=x/4+y/2+x*y/4
    return [s*phi.cos(),s*phi.sin(),c]


def normal_curved(x):
    c=arb(3)/4-x/4
    return [(1-c*c).sqrt(),arb(0),c]


def rodrigues(n, angle):
    x,y,z=n
    cross=arb_mat([[0,-z,y],[z,0,-x],[-y,x,0]])
    outer=arb_mat([[n[i]*n[j] for j in range(3)] for i in range(3)])
    ident=arb_mat([[int(i==j) for j in range(3)] for i in range(3)])
    return angle.cos()*ident+angle.sin()*cross+(1-angle.cos())*outer


def flat_shift(x, y, parameter, denominator, winding, defect):
    rotation=rodrigues(normal_flat(x,y,denominator),(2*arb.pi()*winding+defect)*parameter)
    deletion=arb_mat([[1,0,0],[0,1,0],[0,0,0]])
    return deletion*rotation


def curved_shift(edge, parameter, winding):
    if edge==2:
        return rodrigues(normal_curved(parameter),2*arb.pi()*winding*parameter)
    c0,c1=arb(3)/4,arb(1)/2
    s0,s1=(1-c0*c0).sqrt(),(1-c1*c1).sqrt()
    c,s=c0*c1+s0*s1,s1*c0-c1*s0
    ry=arb_mat([[c,0,s],[0,1,0],[-s,0,c]])
    phi=2*arb.pi()*parameter
    z=arb_mat([[phi.cos(),-phi.sin(),0],[phi.sin(),phi.cos(),0],[0,0,1]])
    return z*ry*z.transpose()
