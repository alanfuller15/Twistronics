"""Static packet hash and retained-result checks."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def require(ok,msg):
    if not ok: raise ValueError(msg)
def main():
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    for row in manifest['files']:
        data=(ROOT/row['path']).read_bytes()
        require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path'])
    r=json.loads((HERE/'RETAINED/RESULTS.json').read_text())
    for name,digest in r['source_sha256'].items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,'source '+name)
    require(r['status']=='PASS' and len(r['checks'])==6 and all(x['passed'] for x in r['checks']),'bridge checks')
    p=json.loads((HERE/'INTEGRATION.json').read_text())
    require(p['status']=='PASS' and len(p['checks'])==3 and all(x['passed'] for x in p['checks']),'integration checks')
    require(r['physical_evaluations']==p['physical_evaluations']==0,'scope')
    print('PASS_PACKET_INTEGRITY: 6 bridge checks, 3 integration checks, zero physical evaluations')
if __name__=='__main__': main()
