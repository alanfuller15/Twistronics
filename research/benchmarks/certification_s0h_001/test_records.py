"""Tampering and incomplete-run controls for the actual retained S0h record."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import verify,begin


def main():
    checks=[]
    verify(HERE/'RUN')
    checks.append({'name':'intact','passed':True})
    for mode in ('result','environment','source','marker'):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'run'
            shutil.copytree(HERE/'RUN',out)
            paths={'result':out/'joined.json','environment':out/'ENVIRONMENT.json',
                   'source':out/'SOURCE/certification_s0h_001/cases.py','marker':out/'COMPLETE.json'}
            if mode=='marker': paths[mode].unlink()
            else:
                with paths[mode].open('a') as f: f.write('\nchanged\n')
            try: verify(out)
            except (ValueError,FileNotFoundError): checks.append({'name':mode+'_refused','passed':True})
            else: raise ValueError('mutation passed: '+mode)
    try: begin(HERE/'RUN')
    except FileExistsError: checks.append({'name':'overwrite_refused','passed':True})
    else: raise ValueError('overwrite accepted')
    print(json.dumps({'status':'PASS','checks':checks}))


if __name__=='__main__': main()
