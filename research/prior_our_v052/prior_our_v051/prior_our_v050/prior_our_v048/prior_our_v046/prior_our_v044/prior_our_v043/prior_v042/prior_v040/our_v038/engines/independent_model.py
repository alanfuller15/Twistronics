"""Separate reciprocal-graph construction; imports no reference implementation.

Units: Angstrom and meV. Native reciprocal coordinates use (G1,G2-G1),
centered layer offsets, and sublattice-major / momentum-major / layer ordering.
kinetic_strain=0 reproduces the project's declared approximation; 1 is an
explicit sensitivity variant, not a claim to implement every BYF convention.
"""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Parameters:
    N: int = 4
    theta: float = 1.05
    strain: float = .003
    direction: float = 0.
    poisson: float = .16
    beta: float = 3.14
    lattice: float = 2.46
    velocity: float = 5944.
    tunneling: float = 110.
    ratio: float = .8
    scalar: float = 0.
    sine_mass: float = 0.
    uniform_mass: float = 0.
    kinetic_strain: float = 0.


def rotation(angle):
    z=np.exp(1j*angle)
    return np.array([[z.real,-z.imag],[z.imag,z.real]])


class ReciprocalModel:
    def __init__(self, parameters=Parameters()):
        self.p=parameters;p=parameters
        if p.N<1 or int(p.N)!=p.N:raise ValueError('N must be a positive integer')
        # Direct graphene lattice -> dual reciprocal lattice -> three equivalent K.
        direct=p.lattice*np.array([[1.,.5],[0.,np.sqrt(3)/2]])
        dual=2*np.pi*np.linalg.inv(direct).T
        corner=(2*dual[:,0]+dual[:,1])/3
        corners=np.array([corner,corner-dual[:,0],corner-dual[:,0]-dual[:,1]])
        axis=np.array([np.cos(np.deg2rad(p.direction)),np.sin(np.deg2rad(p.direction))])
        strain=p.strain*((1+p.poisson)*np.outer(axis,axis)-p.poisson*np.eye(2))
        self.strains=np.array([-.5*strain,.5*strain])
        self.angles=np.deg2rad(p.theta)*np.array([-.5,.5])
        deformed=np.array([corners@rotation(t).T@(np.eye(2)-s).T for t,s in zip(self.angles,self.strains)])
        self.transfers=deformed[0]-deformed[1]
        self.origin=.5*self.transfers[0]
        self.original_reciprocal=np.column_stack([self.transfers[1]-self.transfers[0],self.transfers[2]-self.transfers[0]])
        self.reciprocal=np.column_stack([self.original_reciprocal[:,0],self.original_reciprocal[:,1]-self.original_reciprocal[:,0]])
        self.gauge=np.sqrt(3)*p.beta/(2*p.lattice)*np.array([[s[0,0]-s[1,1],-2*s[0,1]] for s in self.strains])
        radius=p.N*np.linalg.norm(self.original_reciprocal[:,0])+1e-6
        # Rigorous enclosing integer box from ||B^-1 G||, not a fixed shell box.
        bound=np.ceil(radius*np.linalg.norm(np.linalg.inv(self.reciprocal),axis=1)).astype(int)
        ij=np.array([(a,b) for a in range(-bound[0],bound[0]+1) for b in range(-bound[1],bound[1]+1)])
        vectors=ij@self.reciprocal.T
        keep=np.linalg.norm(vectors,axis=1)<=radius
        ij=ij[keep];vectors=vectors[keep]
        order=np.lexsort((ij[:,0],ij[:,1],np.sum(vectors*vectors,axis=1)))
        self.indices=ij[order];self.vectors=vectors[order]
        self.M=len(self.indices);self.dim=4*self.M;self.orbitals=2*self.M
        # H[row,column] connects a ket with integer coordinate column to row.
        delta=self.indices[:,None,:]-self.indices[None,:,:]
        def adjacency(shift):return np.all(delta==shift,axis=2).astype(float)
        pauli_z=np.diag([1.,-1.]);identity=np.eye(2)
        blocks=np.zeros((self.orbitals,self.orbitals,2,2),complex)
        for j,shift in enumerate([(0,0),(1,0),(1,1)]):
            phase=np.exp(2j*np.pi*j/3)
            coupling=p.tunneling*np.array([[p.ratio,phase.conjugate()],[phase,p.ratio]])
            layer_block=np.zeros((2,2));layer_block[1,0]=1
            directed=np.kron(adjacency(shift),layer_block)[:,:,None,None]*coupling
            blocks+=directed+directed.transpose(1,0,3,2).conj()
        for shift in [(1,0),(1,1),(0,1)]:
            forward=adjacency(shift)
            orbital_forward=np.kron(forward,np.eye(2))
            scalar=p.scalar*p.tunneling*.5*identity
            odd=p.sine_mass*p.tunneling/(2j)*pauli_z
            directed=orbital_forward[:,:,None,None]*(scalar+odd)
            blocks+=directed+directed.transpose(1,0,3,2).conj()
        self.static=blocks.transpose(2,0,3,1).reshape(self.dim,self.dim)
        self._a=np.arange(self.orbitals);self._b=self._a+self.orbitals
        self.real_spinor=np.array([[1,1j],[1,-1j]])/np.sqrt(2)

    def from_original_fraction(self,f):
        return self.original_reciprocal@np.asarray(f)+self.origin

    def hamiltonian(self,k_centered):
        p=self.p;H=self.static.copy()
        momenta=np.asarray(k_centered)[None,None,:]+self.vectors[:,None,:]+np.array([-.5,.5])[None,:,None]*self.transfers[0]-self.gauge[None,:,:]
        local=np.empty_like(momenta)
        for layer in (0,1):
            tensor=rotation(-self.angles[layer])@(np.eye(2)+p.kinetic_strain*self.strains[layer])
            local[:,layer]=momenta[:,layer]@tensor.T
        z=p.velocity*(local[:,:,0]-1j*local[:,:,1]).reshape(-1)
        H[self._a,self._b]+=z;H[self._b,self._a]+=z.conj()
        H[self._a,self._a]+=p.uniform_mass;H[self._b,self._b]-=p.uniform_mass
        return H

    def real_hamiltonian(self,f):
        h=self.hamiltonian(self.from_original_fraction(f))
        if not np.isfinite(h).all():raise ValueError('nonfinite Hamiltonian')
        herm=float(np.max(np.abs(h-h.conj().T)))
        if herm>1e-9:raise ValueError('non-Hermitian Hamiltonian')
        blocks=h.reshape(2,self.orbitals,2,self.orbitals)
        real=np.einsum('ai,ambn,bj->imjn',self.real_spinor.conj(),blocks,self.real_spinor,optimize=True).reshape(self.dim,self.dim)
        imag=float(np.max(np.abs(real.imag)))
        if imag>1e-9:raise ValueError('C2zT broken')
        return real.real,dict(hermitian_residual=herm,reality_residual=imag)

    def reference_permutation(self,reference_indices):
        """Only comparison harness calls this; old |layer,G,s> -> native index."""
        lookup={tuple(x):i for i,x in enumerate(self.indices)}
        return np.array([s*self.orbitals+2*lookup[(m+n,n)]+layer
                         for layer in (0,1) for m,n in reference_indices for s in (0,1)])
