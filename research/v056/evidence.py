"""Read-only evidence primitives. No imports or execution of project modules."""
import hashlib,json,math
from pathlib import Path,PurePosixPath

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def finite(x):
    if isinstance(x,float):require(math.isfinite(x),'nonfinite evidence')
    elif isinstance(x,dict):
        for v in x.values():finite(v)
    elif isinstance(x,list):
        for v in x:finite(v)
def pairs(items):
    d={}
    for k,v in items:
        require(k not in d,'duplicate JSON key: '+k);d[k]=v
    return d
def read(path):
    r=json.loads(Path(path).read_text(),object_pairs_hook=pairs);finite(r);return r
def safe(root,name):
    p=PurePosixPath(name);root=Path(root).resolve()
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in name,'unsafe evidence path')
    q=root.joinpath(*p.parts)
    require(q.resolve().is_relative_to(root) and not any(z.is_symlink() for z in [q,*q.parents] if z.is_relative_to(root)),'evidence path escapes root')
    return q
def accepted(path):
    r=read(path);require(r.get('status')=='ACCEPT','source is not accepted: '+str(path));return r
def write(path,value):
    p=Path(path);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');tmp.replace(p)
def pair_distance(a,b):
    require(len(a)==len(b)==2,'join requires exactly two roots')
    def dist(x,y):return math.dist(x['f'],y['f'])
    return min(max(dist(a[i],b[j]) for i,j in enumerate(order)) for order in [(0,1),(1,0)])
