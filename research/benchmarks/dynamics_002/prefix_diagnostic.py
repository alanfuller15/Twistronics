from pathlib import Path
import numpy as np,json,hashlib,argparse
parser=argparse.ArgumentParser();parser.add_argument("coarse",type=Path);parser.add_argument("output",type=Path);args=parser.parse_args()
root=args.coarse;m=np.load(root/'MODES.npz');e=m['energies_meV'];v=m['vectors'];results={}
for tag in ['sigma0p07','sigma0p11']:
 w=m[tag+'_weights'];rows=[]
 for t in np.arange(0,200.1,2.5):
  amp=np.einsum('ijdb,ijb->ijd',v,w*np.exp(-1j*e*t/658.2119569));pad=np.zeros((128,128,196),complex);pad[48:80,48:80]=amp
  psi=np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(pad,axes=(0,1)),axes=(0,1)),axes=(0,1))*128
  prob=np.sum(abs(psi)**2,axis=2);edge=prob.sum()-prob[8:-8,8:-8].sum();rows.append({'time_fs':float(t),'edge_mass':float(edge)})
 valid=[]
 for r in rows:
  if r['edge_mass']>0.01:break
  valid.append(r)
 results[tag]={'edge_mass_by_frame':rows,'maximum_safe_prefix_fs':valid[-1]['time_fs'] if valid else None,'initial_edge':rows[0]['edge_mass']}
path=args.output;path.write_text(json.dumps({'source_modes_sha256':hashlib.sha256((root/'MODES.npz').read_bytes()).hexdigest(),'method':'reconstruct retained grid32 modes; outer 2 moire-cell border; longest original-time prefix with edge probability <=0.01','physical_eigensolver_calls':0,'packets':results},indent=2)+'\n');print(json.dumps({k:{'safe_prefix_fs':v['maximum_safe_prefix_fs'],'initial_edge':v['initial_edge']} for k,v in results.items()}))
