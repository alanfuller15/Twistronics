"""Exploratory fold locations/domain checks; not accepted event measurements."""
import json
from pathlib import Path
from local_cases import CASES
from local_fold import locate
from checkpoints import save_json
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
 for case,c in CASES.items():
  r=locate('bm_lab',4,c);save_json(ROOT/'pilot'/f'{case}.json',dict(status='PILOT',engine='bm_lab',N=4,case=case,event=r))
  print(case,r['parameter'],r['f'],flush=True)
