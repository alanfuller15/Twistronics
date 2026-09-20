"""Root-only exact-BM control; not an unexecuted full exact-BM replay."""
import json
from pathlib import Path
from replay import frozen_protocol,locate_crossing
from checkpoints import digest,load_steps,save_json
from measure import require

ROOT=Path(__file__).resolve().parent

def run():
    protocol=frozen_protocol();out=[]
    for N in [4,6]:
        folder=ROOT/'results'/f'early_ref_lab_N{N}'
        summary=json.loads((folder/'summary.json').read_text());rows,_=load_steps(folder,protocol)
        require(summary['status']=='ACCEPT' and summary['states']==rows,'reference route incomplete')
        for shift in [0.,.012]:
            event=locate_crossing('bm_exact',N,rows,shift)
            reference=next(e for e in summary['events'] if e['shift']==shift)
            event['ref_B']=reference['B'];event['difference']=event['B']-reference['B']
            require(abs(event['difference'])<1e-8,'exact-geometry crossing differs across engines')
            out.append(event);print('exact control',N,shift,event['B'],'difference',event['difference'],flush=True)
    result=dict(status='ACCEPT',scope='crossing roots and singular-path rejection only; no full bm_exact path replay',protocol_sha256=protocol,
                control_source_sha256=digest(Path(__file__)),events=out)
    save_json(ROOT/'results/exact_control.json',result);return result

if __name__=='__main__':run()
