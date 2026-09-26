"""Stable finite-matrix projector distance and explicit legacy roundoff compatibility."""
import numpy as np

def projector_distance(A,B):
 assert A.shape==B.shape and A.ndim==2 and np.isfinite(A).all() and np.isfinite(B).all()
 rank=A.shape[1];gA=np.linalg.norm(A.T@A-np.eye(rank),'fro');gB=np.linalg.norm(B.T@B-np.eye(rank),'fro')
 assert max(gA,gB)<1e-10
 direct=float(np.linalg.norm(A@A.T-B@B.T,'fro'))
 # Cross-check using a separate residual identity for orthonormal columns.
 residual=float(np.sqrt(2)*np.linalg.norm(B-A@(A.T@B),'fro'))
 assert abs(direct-residual)<8*(gA+gB)+128*rank*np.finfo(float).eps
 return direct,float(gA+gB)

def legacy_compatibility(legacy,direct,gram_defect,rank):
 # Numerical engineering guard in squared-distance units, not an interval error certificate.
 # The legacy expression subtracts O(rank) traces; its absolute precision is O(rank*epsilon),
 # plus the observed departure from exact orthonormality. No legacy value is relabeled exact.
 guard=float(128*rank*np.finfo(float).eps+4*gram_defect)
 error=float(abs(legacy**2-direct**2))
 return {'legacy_value':float(legacy),'stable_value':direct,'squared_difference':error,'squared_roundoff_guard':guard,'roundoff_compatible':bool(np.isfinite(legacy) and legacy>=0 and error<=guard)}
