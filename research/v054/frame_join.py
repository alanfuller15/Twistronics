"""Join roots and relative frame orientation; allow a common orientation flip."""
import json
from pathlib import Path
import numpy as np
from measure import require
from checkpoints import digest
from protocol import match
ROOT=Path(__file__).resolve().parent

def join(engine,N,p,nodes,frames,basis_labels,trials,spatial_label):
 path=ROOT/'anchors'/f'v044_start_{engine}_N{N}.json';a=json.loads(path.read_text())
 require(a['status']=='ACCEPT' and a['engine']==engine and a['N']==N and a['kinetic']=='lab_nn_full','invalid frame anchor identity')
 require(a['geometry']==('linear' if engine=='bm_lab' else 'exact'),'frame anchor geometry mismatch')
 require(p.w_kappa==0 and p.w_mode=='average','historical frame anchor has no tunnelling sensitivity')
 require(all(a['state'][k]==getattr(p,k) for k in ['A','B','T','phi','ratio','theta','eps']),'frame anchor state mismatch')
 require(digest(path.with_suffix('.npz'))==a['frames_sha256'],'frame anchor digest mismatch')
 target=[a['nodes'][k] for k in ['F1','F3']];root_join=match(nodes,target);comparisons=[]
 with np.load(path.with_suffix('.npz'),allow_pickle=False) as data:
  require(np.array_equal(basis_labels,data['labels']),'frame anchor basis labels differ')
  old=[data['e1'],data['e2']]
  for i,(frame,side) in enumerate(zip(frames,['a','b'])):
   j=root_join['permutation'][i];require(np.isfinite(frame).all() and np.isfinite(old[j]).all(),'nonfinite endpoint frames')
   require(frame.shape==old[j].shape,'frame shape mismatch')
   overlap=frame.T@old[j];sv=np.linalg.svd(overlap,compute_uv=False);det=float(np.linalg.det(overlap));sign=int(np.sign(det))
   require(sv.min()>.999999 and abs(det)>.999999,'endpoint two-plane mismatch')
   old_charge=a['temporal_trials'][1][['a','b'][j]]['charge'];charge=trials[1][side]['charge']
   require(sign*old_charge==charge,'endpoint charge incompatible with frame orientation')
   comparisons.append(dict(node=i,anchor_node=j,min_overlap=float(sv.min()),determinant=det,orientation=sign,anchor_charge=old_charge,carried_charge=charge))
 relative=int(np.prod([r['orientation'] for r in comparisons]));require(relative==1,'endpoint relative frame orientation differs')
 require(spatial_label==a['label'],'endpoint spatial label differs from v044')
 return dict(root_join=root_join,frame_joins=comparisons,relative_orientation=relative,common_orientation=comparisons[0]['orientation'],label=spatial_label,anchor_frames_sha256=a['frames_sha256'])
