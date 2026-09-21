"""Run the two synthetic acceptance modules and validate their recorded evidence."""
from pathlib import Path
import argparse,json
import test_evidence_bound as evidence
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    root=Path(__file__).resolve().parent
    bundle=evidence.record(str(root),out_root=str(args.output.resolve()),selection=['test_evidence_binding_partner.py','test_review_guards.py'])
    certificate=evidence.gate(bundle,str(root))
    print(json.dumps({'bundle':str(bundle),'certificate':certificate},indent=2))
if __name__=='__main__':main()
