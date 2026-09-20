"""Run N4 then N6 for one engine; each completed job can be resumed."""
import argparse
from run_focused import run

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);a=ap.parse_args()
    for N in [4,6]:run(a.engine,N)
