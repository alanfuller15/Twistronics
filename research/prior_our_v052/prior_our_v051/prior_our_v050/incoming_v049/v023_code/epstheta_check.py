"""Independent check of the team's v046 qualification: at finite twist, the mean over the two layers of the
valley radius |K_j^(l)| has an O(eps*theta) term, whereas the implemented 'average' projection (both layers on the
same UNROTATED direction) cancels exactly."""
import numpy as np
A0=2.46; KD=np.array([4*np.pi/(3*A0),0.0]); R=lambda t: np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
def E_of(eps,phi,nu=0.16):
    return eps*np.array([[np.cos(phi)**2-nu*np.sin(phi)**2,(1+nu)*np.sin(phi)*np.cos(phi)],[(1+nu)*np.sin(phi)*np.cos(phi),np.sin(phi)**2-nu*np.cos(phi)**2]])
def mean_radius_shift(eps,theta_deg,phi_deg=0.0):
    th=np.radians(theta_deg); E=E_of(eps,np.radians(phi_deg)); out=[]
    for j in range(3):
        Kj=R(2*np.pi*j/3)@KD; rs=[]
        for El,thl in ((-E/2,-th/2),(E/2,th/2)):
            rs.append(np.linalg.norm(np.linalg.inv(np.eye(2)+El).T@R(thl)@Kj))
        out.append((rs[0]+rs[1])/2/np.linalg.norm(Kj)-1.0)
    return np.array(out)
def implemented_average(eps,phi_deg=0.0):
    E=E_of(eps,np.radians(phi_deg)); out=[]
    for j in range(3):
        e=R(2*np.pi*j/3)@np.array([1.0,0.0]); out.append(0.5*(e@(-E/2)@e + e@(E/2)@e))
    return np.array(out)
eps,th=0.003,1.05
print("relative mean valley-radius shift, exact geometry, eps=0.3%, theta=1.05 deg, per K_j:", mean_radius_shift(eps,th))
print("implemented 'average' projection (unrotated direction):                          ", implemented_average(eps))
print("scaling checks (should be ~ linear in eps and in theta for the mean-radius term):")
for e2,t2 in [(0.006,1.05),(0.003,2.10),(0.0015,0.525)]:
    print(f"   eps={e2:.4f} theta={t2:.3f}: {mean_radius_shift(e2,t2)}")
print("second-order-only reference (theta=0):", mean_radius_shift(eps,0.0), " -> O(eps^2) =", eps**2)
