"""Derive execution summary from retained records; no physical calculation."""
import json,sys
from pathlib import Path
root=Path(sys.argv[1]);rows=json.loads((root/'MAP.json').read_text())['samples'];s={'batch':json.loads((root/'BATCH_RECEIPT.json').read_text()),'independent_review':'PENDING'}
for group in ['four','pair']:
 d={}
 for key in ['min_singular_value','projector_frobenius_distance','mean_added_component_weight','max_added_component_weight']:
  vals=[(r['metrics'][group][key],r['index']) for r in rows];lo=min(vals);hi=max(vals);d[key]={'min':lo[0],'min_point':lo[1],'max':hi[0],'max_point':hi[1]}
 d['largest_principal_angle_degrees']=max(max(r['metrics'][group]['principal_angles_degrees']) for r in rows)
 d['external_gap_minima_meV']={c:min(min(r['metrics'][group][c+'_external_gaps_meV']) for r in rows) for c in ['a','b']};s[group]=d
s['upper_gap_change_microeV']=[f(r['metrics']['upper_gap_change_b_minus_a_microeV'] for r in rows) for f in [min,max]]
s['max_nested_residual_meV']=max(r['nested_matrix_residual_meV'] for r in rows)
s['max_eigenpair_residual_meV']=max(max(r['eigenpair_residuals_meV'].values()) for r in rows)
s['max_job_seconds']=max(json.loads(p.read_text())['elapsed_seconds'] for p in root.glob('job*/RECEIPT.json'))
assert s==json.loads((root/'SUMMARY.json').read_text()),'summary mismatch'
print('SUMMARY_MATCH')
