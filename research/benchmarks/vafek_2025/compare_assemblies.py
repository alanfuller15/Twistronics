"""Diagnose off-axis source consistency, without silently choosing a correction."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from model import Model
from run_benchmark import locate
class Direct(Model):
 def h(self,k,Q):return self.direct_projection(k,Q)
def main():
 literal=Model();direct=Direct();qn=brentq(lambda q:literal.gamma_branches(q)[1]-literal.gamma_branches(q)[2],0,1.5);qg=brentq(lambda q:literal.gamma_branches(q)[0]-literal.gamma_branches(q)[2],0,1.5)
 points=[]
 for k,q in [([0,0],0),([0,0],.5),([.2,0],0),([.23,-.17],.5),([.23,-.17],0)]:
  a=literal.h(k,q);b=direct.h(k,q)
  points.append(dict(K=k,Q=q,max_matrix_difference_meV=float(np.max(abs(a-b))),max_spectrum_difference_meV=float(np.max(abs(np.linalg.eigvalsh(a)-np.linalg.eigvalsh(b))))))
 rows=[]
 for name,m in [('literal_Eq73',literal),('direct_Eqs28_35_74_85',direct)]:
  for Q,g in [(qn-.02,1),(qn+.02,1),(qg-.02,0),(qg+.02,0)]:
   roots,_,_=locate(m,Q,g,41,.8)
   local,_,_=locate(m,Q,g,25,.12)
   rows.append(dict(assembly=name,Q=float(Q),gap=g,nodes=roots,nodes_within_radius_012=int(sum(np.linalg.norm(r['K'])<.12 for r in local)),local_search_nodes=local))
 result=dict(scope='Source-equation diagnostic, not an author-confirmed correction',thresholds=dict(Qn=qn,Qg=qg),points=points,rows=rows,derivation='In the fixed flat-band gauge C=I/sqrt(1+K²), F=-diag(Kx+iKy,Kx-iKy)/sqrt(1+K²), the Eq35 c-f block -i*c_doubleprime*epsilon_minus*sigma3 contributes -2*c_doubleprime*epsilon_minus*Ky/(1+K²) times I. Eq73 prints the opposite sign. Neither Gamma nor ky=0 checks can detect this difference.',limitations=['Both assemblies and the diagnostic were authored in this session.','Off-axis conventions require external review before asserting a paper error.','The local radius .12 is an explicitly diagnostic region, not a global node inventory or braid certificate.'])
 Path(__file__).with_name('ASSEMBLY_COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
