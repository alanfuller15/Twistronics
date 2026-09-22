"""Reconcile retained evidence without running a new numerical campaign."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET,zipfile
import numpy as np
ROOT=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((ROOT/n).read_text())
def main():
    manifest=read('INPUT_MANIFEST.json')
    assert H(ROOT/'partner_v073p.zip')==manifest['archive_sha256']
    with zipfile.ZipFile(ROOT/'partner_v073p.zip') as z:
        for n,r in manifest['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==r['sha256']
        chiral=json.loads(z.read('CHIRAL_CONTROL.json')); valley=json.loads(z.read('VALLEY_MIRROR.json'))
    p=read('PROBES.json');plan=read('PLAN.json');rows=p['rows'];basis=read('BASIS.json')
    assert p['plan_sha256']==H(ROOT/'PLAN.json')
    assert len(rows)==len(plan['native_fast_comparison']['N'])*len(plan['native_fast_comparison']['valleys'])*len(plan['native_fast_comparison']['f'])
    for n,b in basis.items():
        assert len(b['ordered_indices'])==b['nG'] and b['dim']==4*b['nG']
        assert hashlib.sha256(json.dumps(b['ordered_indices'],separators=(',',':')).encode()).hexdigest()==b['indices_json_sha256']
    for r in rows:
        e=float(np.max(np.abs(np.array(r['native_bands_meV'])-r['fast_bands_meV'])))
        assert e==r['spectrum_error_meV'] and r['dim']==basis[str(r['N'])]['dim']
    K=[r for r in rows if r['valley']==1];P=[r for r in rows if r['valley']==-1]
    assert all(r['matrix_tolerance_met'] and r['spectrum_tolerance_met'] for r in K)
    assert all(not r['matrix_tolerance_met'] and not r['spectrum_tolerance_met'] for r in P)
    assert all(r['native_exact_time_reversal'] for r in P)
    assert max(r['fast_error_vs_positive_valley_at_same_k_meV'] for r in P)<1e-9
    tests=ET.parse(ROOT/'SUPPLIED_TESTS.xml').getroot()
    cases=list(tests.iter('testcase'));assert len(cases)==5
    assert not list(tests.iter('failure')) and not list(tests.iter('error'))
    c=p['contract_probes'];assert c['synthetic_rank_zero_W']['returned_min_polar_det']==1
    assert c['native_broken_reality']['imaginary_residual_meV']>.99
    assert c['native_broken_reality']['band_sign_holonomy']['status']=='RETURNED'
    replay=read('EXECUTIONS.json')[-1];replayed=read('REPLAY_VALLEY_MIRROR.json');replayed_chiral=read('REPLAY_CHIRAL_CONTROL.json')
    completed=replay['name']=='PARTNER_REPLAY' and replay['exit_code']==0
    def compare(a,b,path=''):
        out=[]
        if isinstance(a,dict) and isinstance(b,dict):
            for k in sorted(set(a)|set(b)):
                q=path+'/'+k
                if k not in b:out.append({'path':q,'status':'missing_after_replay','before':a[k]})
                elif k not in a:out.append({'path':q,'status':'added_by_replay','after':b[k]})
                else:out+=compare(a[k],b[k],q)
        elif a!=b:out.append({'path':path,'status':'changed','before':a,'after':b})
        return out
    diff={'CHIRAL_CONTROL.json':compare(chiral,replayed_chiral),'VALLEY_MIRROR.json':compare(valley,replayed)}
    result={
      'status':'EXPLORATORY_NATIVE_CONTROLS_USEFUL_FAST_VALLEY_INTEGRATION_WITHHELD',
      'supplied_tests_passed':len(cases),'comparison_rows':len(rows),
      'native_time_reversal_exact_rows':sum(r['native_exact_time_reversal'] for r in P),
      'positive_valley':{'rows':len(K),'max_matrix_error_meV':max(r['matrix_error_meV'] for r in K),'max_spectrum_error_meV':max(r['spectrum_error_meV'] for r in K)},
      'negative_valley':{'rows':len(P),'min_spectrum_error_meV':min(r['spectrum_error_meV'] for r in P),'max_spectrum_error_meV':max(r['spectrum_error_meV'] for r in P),'max_matrix_error_meV':max(r['matrix_error_meV'] for r in P)},
      'partner_chiral_record':{'node_winding_sum':chiral['chiral_euler']['w1']+chiral['chiral_euler']['w2'],'twice_euler':2*chiral['chiral_euler']['e2'],'reference_convention':'Ahn–Park–Yang uses total winding = -2 e2. This record is compatible in sign with that relation but does not establish common gauge orientation or mesh convergence.'},
      'partner_replay_completed':completed,'partner_replay_exit':replay,'replay_differences':diff,
      'chiral_fields_inherited_not_recomputed_by_runner':['magic_N6','magic_N8','chiral_symmetry_residual','note'],
      'scope':['Native BM only for valley extension; no independent K-prime TBG implementation added.','No complete node inventory, continuous topology certificate, full sparse acceptance or physical validation.','Signed Euler comparisons remain convention-dependent.','Replay call counts include profiler overhead and are not performance benchmarks.'],
      'input_sha256':{n:H(ROOT/n) for n in ['partner_v073p.zip','PLAN.json','PROBES.json','BASIS.json','SUPPLIED_TESTS.xml','EXECUTIONS.json','REPLAY_CHIRAL_CONTROL.json','REPLAY_VALLEY_MIRROR.json']}}
    (ROOT/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
