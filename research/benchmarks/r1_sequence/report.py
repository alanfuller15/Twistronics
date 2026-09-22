"""Summarize raw evidence and render the numerical sequence; no model rerun."""
from pathlib import Path
import json, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

P = read(ROOT / 'PLAN.json')
raw = {e: read(ROOT / (e.upper() + '.json')) for e in P['engines']}
for e, d in raw.items():
    assert d['status'] != 'RUNNING', (e, 'still running')
    assert d['plan_sha256'] == sha(ROOT / 'PLAN.json')
    for path, digest in d['source_hashes'].items():
        assert sha(ROOT.parent / path) == digest, path

def compact(r):
    return {'label': r['label'], 'windings': r['windings'], 'diagnostics_pass': r['diagnostics_pass'],
            'expected_label_pass': r.get('expected_label_pass'),
            'minimum_conditioning': min(v for v in r['conditioning'].values() if v is not None),
            'transport_step_smin': r['conditioning']['transport_step_smin'],
            'minimum_isolation_lower_meV': min(v['min_lower_estimate_meV'] for v in r['isolation'].values()),
            'isolation_pass': all(v['pass'] for v in r['isolation'].values())}

summary = {'scope': 'N8 endpoint, targeted center-segment crossing, and matched-path diagnostics; not full braid acceptance',
           'status_by_engine': {e: d['status'] for e, d in raw.items()}, 'endpoint_rows': [], 'matched_path_rows': [],
           'crossing_by_cutoff': {}, 'matched_engine_comparisons': [], 'errors': {e: d['errors'] for e, d in raw.items()}}
summary['root_comparisons'] = []
for group in ['endpoints', 'matched_path_stations']:
    for a in raw['bm'][group]:
        b = next(s for s in raw['ref'][group] if s['D_meV'] == a['D_meV'])
        summary['root_comparisons'].append({'group': group, 'D_meV': a['D_meV'],
            'both_root_gates_pass': a['roots_pass'] and b['roots_pass'],
            'maximum_root_gap_meV': max(r['gap_meV'] for s in [a,b] for r in s['roots']),
            'maximum_engine_coordinate_difference': max(float(np.linalg.norm(np.array(x['f'])-y['f'])) for x,y in zip(a['roots'],b['roots']))})
for e, d in raw.items():
    for s in d['endpoints']:
        for r in s['trials']:
            summary['endpoint_rows'].append({'engine': e, 'D_meV': s['D_meV'], 'trial': r['configuration']['name'], **compact(r)})
    for s in d['matched_path_stations']:
        for r in s['trials']:
            summary['matched_path_rows'].append({'engine': e, 'D_meV': s['D_meV'], 'path': r['path'],
                                                'path_start': r['path_start'], 'path_end': r['path_end'], **compact(r)})
for N in [4, 6, 8]:
    crosses = ({e: d['crossing'] for e, d in raw.items()} if N == 8 else
               read(ROOT.parent / f'r1_events/N{N}.json')['crossing_refinements'])
    summary['crossing_by_cutoff'][str(N)] = {e: {'bracket_D_meV': c['bracket_D_meV'],
        'endpoint_offsets': c['endpoint_offsets'], 'root_evaluations': len(c['evaluations']),
        'maximum_root_gap_meV': max(r['gap_meV'] for row in c['evaluations'] for r in [*row['flat'], row['upper']])}
        for e, c in crosses.items() if c is not None}
summary['original_failed_rows'] = [r for r in summary['endpoint_rows'] + summary['matched_path_rows'] if not r['diagnostics_pass']]
for D in P['matched_path_D_meV']:
    for path in P['matched_paths']:
        rs = [next((r for r in summary['matched_path_rows'] if r['engine'] == e and r['D_meV'] == D and r['path'] == path), None)
              for e in P['engines']]
        if any(r is None for r in rs):
            summary['matched_engine_comparisons'].append({'D_meV': D, 'path': path, 'complete': False})
            continue
        summary['matched_engine_comparisons'].append({'D_meV': D, 'path': path, 'complete': True,
            'labels': [r['label'] for r in rs], 'labels_agree': rs[0]['label'] == rs[1]['label'],
            'both_diagnostics_pass': all(r['diagnostics_pass'] for r in rs),
            'maximum_endpoint_difference': max(float(np.linalg.norm(np.array(rs[0][key]) - rs[1][key])) for key in ['path_start', 'path_end'])})

merger = read(ROOT.parent / 'r1_n8/SUMMARY.json')
summary['previous_local_merger'] = {'source': '../r1_n8/SUMMARY.json',
    'D_meV_by_engine': {e: merger['N8'][e]['native_fold_check']['D_meV'] for e in P['engines']},
    'interpretation': 'Previously obtained local fold evidence, consistent with local pair annihilation; not recomputed here.'}
summary['all_planned_diagnostics_pass'] = (len(summary['endpoint_rows']) == 16 and len(summary['matched_path_rows']) == 8 and
    all(d['status'].startswith('N8_SEQUENCE_DIAGNOSTICS_PASS') for d in raw.values()) and
    all(c.get('complete') and c['labels_agree'] and c['both_diagnostics_pass'] and c['maximum_endpoint_difference'] < 1e-6
        for c in summary['matched_engine_comparisons']))
refined = {e: read(ROOT / ('REFINED_' + e.upper() + '.json')) for e in P['engines']}
assert refined['bm']['selected_D_meV'] == refined['ref']['selected_D_meV']
summary['refinement_status_by_engine'] = {e: d['status'] for e, d in refined.items()}
summary['refinement_rows'] = []
summary['mesh_comparisons'] = []
for e, d in refined.items():
    assert d['status'] != 'RUNNING'
    assert d['plan_sha256'] == sha(ROOT / 'REFINEMENT_PLAN.json')
    for path, digest in d['source_hashes'].items():
        assert sha(ROOT.parent / path) == digest, path
    for s in d['stations']:
        for r in s['trials']:
            summary['refinement_rows'].append({'engine': e, 'D_meV': s['D_meV'], 'path': r['path'],
                'transport_points': r['configuration']['transport_points'], **compact(r)})
        for path in P['matched_paths']:
            rows = [r for r in s['trials'] if r['path'] == path]
            summary['mesh_comparisons'].append({'engine': e, 'D_meV': s['D_meV'], 'path': path,
                'labels': [r['label'] for r in rows], 'labels_agree': len({r['label'] for r in rows}) == 1,
                'both_diagnostics_pass': len(rows) == 2 and all(r['diagnostics_pass'] for r in rows)})
summary['refined_engine_comparisons'] = []
for D in refined['bm']['selected_D_meV']:
    for path in P['matched_paths']:
        for nt in [4801, 9601]:
            rows = [next(r for r in summary['refinement_rows'] if r['engine'] == e and r['D_meV'] == D and r['path'] == path and r['transport_points'] == nt) for e in P['engines']]
            summary['refined_engine_comparisons'].append({'D_meV': D, 'path': path, 'transport_points': nt,
                'labels': [r['label'] for r in rows], 'labels_agree': rows[0]['label'] == rows[1]['label'],
                'both_diagnostics_pass': all(r['diagnostics_pass'] for r in rows)})
final_rows = [r for r in summary['matched_path_rows'] if r['D_meV'] not in refined[r['engine']]['selected_D_meV']]
final_comparisons = [r for r in summary['matched_engine_comparisons'] if r['D_meV'] not in refined['bm']['selected_D_meV']]
summary['resolved_followup_criteria_pass'] = (len(summary['endpoint_rows']) == 16 and
    all(r['diagnostics_pass'] and r['expected_label_pass'] for r in summary['endpoint_rows']) and
    all(r['diagnostics_pass'] for r in final_rows) and
    all(c['complete'] and c['labels_agree'] and c['both_diagnostics_pass'] and c['maximum_endpoint_difference'] < 1e-6 for c in final_comparisons) and
    all(c['both_root_gates_pass'] and c['maximum_engine_coordinate_difference'] < 1e-6 for c in summary['root_comparisons']) and
    all(d['status'].startswith('REFINED_TRANSPORT_DIAGNOSTICS_PASS') for d in refined.values()) and
    all(c['labels_agree'] and c['both_diagnostics_pass'] for c in summary['refined_engine_comparisons']) and
    all(c['labels_agree'] and c['both_diagnostics_pass'] for c in summary['mesh_comparisons']) and
    raw['bm']['crossing']['bracket_D_meV'] == raw['ref']['crossing']['bracket_D_meV'] and
    all(not d['errors'] for d in raw.values()))
inputs = [ROOT / 'PLAN.json', ROOT / 'BM.json', ROOT / 'REF.json', ROOT.parent / 'r1_n8/SUMMARY.json',
          ROOT / 'REFINEMENT_PLAN.json', ROOT / 'REFINED_BM.json', ROOT / 'REFINED_REF.json',
          *[ROOT.parent / f'r1_events/N{N}.json' for N in [4, 6]],
          *[ROOT.parent / f'r1_validation/N{N}.json' for N in [4, 6]]]
summary['input_sha256'] = {str(f.relative_to(ROOT.parent)): sha(f) for f in inputs}
(ROOT / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: summary[k] for k in ['status_by_engine', 'all_planned_diagnostics_pass', 'resolved_followup_criteria_pass', 'refined_engine_comparisons', 'crossing_by_cutoff']}, indent=2))

navy, blue, teal, amber, red = '#172c43', '#376bab', '#087f7d', '#b66b1d', '#b83f49'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.labelcolor': navy, 'text.color': navy,
                     'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(14, 10.6), facecolor='#f6f8fb')
gs = fig.add_gridspec(3, 2, height_ratios=[.8, 1.1, 1.0], left=.085, right=.96, top=.85, bottom=.15, hspace=.62, wspace=.3)
fig.text(.055, .955, 'N8 follow-up: endpoints, crossing, and comparison paths', fontsize=23, weight='bold')
fig.text(.055, .917, 'Declared strained TBG continuum model  •  two implementations  •  596 × 596 Hamiltonians', fontsize=12)

ax = fig.add_subplot(gs[0, :]); ax.set_facecolor('#f6f8fb')
cross = raw['bm']['crossing']['bracket_D_meV']
fold = summary['previous_local_merger']['D_meV_by_engine']['bm']
ax.plot([36, 42], [0, 0], color='#a6b5c7', lw=3)
events = [(36, 'SAME charges\nendpoint trials', teal), (np.mean(cross), 'Center-segment\ncrossing bracket', amber),
          (fold, 'Local fold*\nprevious checkpoint', blue), (42, 'OPPOSITE charges\nendpoint trials', red)]
for D, label, color in events:
    ax.scatter(D, 0, s=120, c=color, zorder=3, edgecolor='white', linewidth=2)
    ax.text(D, .32, label, ha='center', va='bottom', color=color, weight='bold', fontsize=11)
    value = f'{D:g}' if D in [36, 42] else (f'{cross[0]:.5f}–{cross[1]:.5f}' if D == np.mean(cross) else f'{D:.7f}')
    ax.text(D, -.22, value, ha='center', va='top', fontsize=10)
ax.set(xlim=(35.6, 42.4), ylim=(-.55, 1.0), yticks=[], xticks=[], xlabel='D (meV)  —  uniform layer energies +D and −D')
ax.spines[['left', 'bottom']].set_visible(False)
ax.set_title('A   Computed checkpoints on the parameter path', loc='left', fontsize=13, weight='bold', pad=12)

for col, D in enumerate(P['matched_path_D_meV']):
    ax = fig.add_subplot(gs[1, col])
    row = next(r for r in raw['bm']['crossing']['evaluations'] if r['D_meV'] == D)
    flat = [np.array(r['f']) for r in row['flat']]
    d = (flat[1] - flat[0] + .5) % 1 - .5
    normal = np.array([-d[1], d[0]]) / np.linalg.norm(d)
    shifted_offset = P['matched_path_config']['radius'] * normal[0] * 1000
    ax.axhline(0, color=teal, lw=2.4, label='Collinear path')
    ax.axhline(shifted_offset, color=blue, lw=2.4, ls='--', label='Shifted path')
    ax.scatter(row['t'], row['offset'] * 1000, s=100, marker='D', color=amber, edgecolors='white', zorder=4)
    ax.annotate('Adjacent-band node', (row['t'], row['offset']*1000), xytext=(-50, 30) if col == 0 else (-10, 16),
                textcoords='offset points', ha='center', fontsize=10, color=amber,
                bbox=dict(facecolor='white', edgecolor='none', pad=1.5), arrowprops=dict(arrowstyle='-',color=amber,lw=.8))
    ax.set(xlim=(row['t']-.026, row['t']+.026), ylim=(-4.9, 2.4), xlabel='Position along flat-node segment, t', ylabel='Normal offset × 1,000\n(fractional coordinates)')
    ax.set_title(f'{chr(66+col)}   D = {D:g} meV: actual local geometry', loc='left', fontsize=12, weight='bold', pad=12)
    ax.grid(axis='y', alpha=.14)
    if col == 0:
        ax.legend(loc='lower left', fontsize=10, frameon=False)
    ax.text(.98, .03, 'Local zoom; axes scaled separately', transform=ax.transAxes, ha='right', fontsize=8, color='#60748a')

ax = fig.add_subplot(gs[2, 0]); ax.axis('off')
ax.set_title('D   Relative charges on identical paths', loc='left', fontsize=12, weight='bold', pad=12)
cells=[]
for row in summary['matched_engine_comparisons']:
    refined_comps = [c for c in summary['refined_engine_comparisons'] if c['D_meV'] == row['D_meV'] and c['path'] == row['path']]
    shown = refined_comps[-1] if refined_comps else row
    checks = ('Pass*' if refined_comps else 'Pass') if shown['both_diagnostics_pass'] else 'Unresolved'
    cells.append([f"{row['D_meV']:g}", 'Shifted' if row['path']=='shifted_x' else 'Collinear', *shown['labels'], checks])
table=ax.table(cellText=cells, colLabels=['D', 'Path', 'BM', 'Reference', 'Checks'], cellLoc='center', bbox=[0,.05,1,.94], colWidths=[.10,.22,.23,.25,.20])
table.auto_set_font_size(False);table.set_fontsize(9)
for (r,c),cell in table.get_celld().items():
    cell.set_edgecolor('#dfe5ed');cell.set_facecolor('white' if r else '#e7edf5')
    if r==0:cell.set_text_props(weight='bold',color=navy)
    if r and c in [2,3]:cell.set_text_props(color=teal if cell.get_text().get_text()=='SAME' else red,weight='bold')

ax = fig.add_subplot(gs[2, 1])
for i, N in enumerate([4, 6, 8]):
    interval = summary['crossing_by_cutoff'][str(N)]['bm']['bracket_D_meV']
    ax.plot(interval, [i, i], color=[navy, blue, teal][i], lw=7, solid_capstyle='butt')
    ax.scatter(interval, [i, i], color=[navy, blue, teal][i], s=28)
ax.set(yticks=[0,1,2], yticklabels=['N = 4','N = 6','N = 8'], xlabel='Center-segment crossing bracket, D (meV)', ylim=(2.5,-.5))
ax.ticklabel_format(useOffset=False, axis='x');ax.grid(axis='x',alpha=.15)
ax.set_title('E   Cutoff comparison: both engines agree', loc='left', fontsize=12, weight='bold', pad=12)
fig.text(.055,.063,'Relative charge depends on the comparison path. The center-segment crossing and local merger are distinct checkpoints.',fontsize=10,weight='bold')
fig.text(.055,.041,'*D=38 uses refined meshes; failed 601-point checks are retained. The prior local fold is consistent with pair annihilation.',fontsize=10,color='#60748a')
fig.text(.055,.021,'Shared measurement framework; no full braid certificate, infinite-cutoff error bound, or experimental calibration.',fontsize=10,color='#60748a')
fig.savefig(ROOT / 'sequence.png', dpi=180, facecolor=fig.get_facecolor())
fig.savefig(ROOT / 'sequence.svg', facecolor=fig.get_facecolor())
