"""Load exact predecessor evidence and reject discontinuous seed/frame joins."""
from pathlib import Path
import numpy as np
from evidence import read,sha,require,safe

KEYS={'frame_a','frame_b','spatial','spatial_fast','coarse_a','coarse_b'}

def arrays_at(folder,row,dimension):
    folder=Path(folder)
    require(read(folder/'record.json')==row,'anchor/checkpoint record mismatch')
    require(sha(folder/'frames.npz')==row['frames_sha256'],'anchor/checkpoint frame hash mismatch')
    with np.load(folder/'frames.npz',allow_pickle=False) as z:arrays={k:z[k].copy() for k in z.files}
    require(set(arrays)==KEYS,'incomplete frame keys')
    for a in arrays.values():
        require(a.shape==(dimension,2) and np.isrealobj(a) and np.isfinite(a).all() and np.max(np.abs(a.T@a-np.eye(2)))<1e-8,'invalid frame array')
    return arrays

def anchor(repo,p,engine):
    spec=p['anchors'][engine]
    for name in ['aggregate','record','frames']:
        require(sha(safe(repo,spec[name]))==p['inputs'][spec[name]],'anchor hash changed')
    c=read(safe(repo,spec['aggregate']));row=read(safe(repo,spec['record']))
    require(c['status']=='ACCEPT_SAMPLED_BRAID2_WINDOW' and c['engine']==engine and c['N']==8 and c['dimension']==p['dimension'],'wrong anchor case')
    require(c['kinetic']==p['kinetic'] and c['geometry']==p['geometry'][engine] and c['cutoff_tol']==p['cutoff_tol'][engine],'anchor model convention changed')
    require(c['state']==p['state'] and c['numerical_plan_sha256']==p['anchor_plan_sha256'],'anchor state/protocol changed')
    require(row==c['states'][-1] and row['step']==4 and row['ratio']==p['ratios'][0] and row['protocol_sha256']==p['anchor_plan_sha256'],'anchor is not the retained endpoint')
    require({k:v['f'] for k,v in row['nodes'].items()}==p['seeds'][engine],'anchor seed mismatch')
    require(row['label']=='OPPOSITE' and row['coarse_check'] is not None,'wrong anchor comparison/coarse checkpoint')
    arrays=arrays_at(safe(repo,spec['record']).parent,row,p['dimension'])
    charges=[row['charge']['trials'][0][k]['charge'] for k in ['a','b']]
    require(charges==spec['temporal_charges'],'anchor temporal gauge changed')
    return row,arrays

def measure_join(old,nodes,raw,aligned,arrays,root_tol,frame_tol):
    shifts={k:float(np.linalg.norm(np.asarray(n['f'])-old['nodes'][k]['f'])) for k,n in nodes.items()}
    require(max(shifts.values())<root_tol,'anchor root join failed')
    overlaps={};errors={}
    for k,rawframe in zip(['a','b'],raw):
        for prefix in ['frame_','coarse_']:
            name=prefix+k;overlaps[name]=float(np.linalg.svd(rawframe.T@arrays[name],compute_uv=False).min())
    for k,new in zip(['a','b'],aligned):errors[k]=float(np.max(np.abs(new-arrays['frame_'+k])))
    require(min(overlaps.values())>1-frame_tol and max(errors.values())<frame_tol,'anchor basis/frame join failed')
    return dict(root_shifts=shifts,subspace_overlaps=overlaps,aligned_max_errors=errors)
