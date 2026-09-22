"""Actual contour geometry and retained uniform clearance bounds."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from geometry import ROOT, sha
from inputs import read_inputs

summary = json.loads((ROOT/'SUMMARY.json').read_text())
assert summary['all_checks_pass']
assert all(sha(ROOT/n) == h for n, h in summary['source_hashes'].items())
data = json.loads((ROOT/'RESULTS.json').read_text())
cont, cases, _ = read_inputs()
case = next(c for c in cases if c['engine'] == 'bm' and c['mesh'] == 'fine' and c['radius'] == .003)
campaign = next(c for c in cont['campaigns'] if c['engine'] == 'bm' and c['initial_intervals'] == 16)
def root_at(node, D):
    rec = next(x for x in cont['centers'].values() if x['engine'] == 'bm' and x['node'] == node and x['D_meV'] == D)
    return np.array(rec['raw']['y'][:2])
p0, q0 = root_at('p', 38.), root_at('q', 38.)
along = (q0-p0)/np.linalg.norm(q0-p0); normal = np.array([-along[1], along[0]])
def transform(points):
    rel = np.asarray(points)-p0
    return np.c_[rel @ along, 1000*(rel @ normal)]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 12,
                     'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(13.6, 10.2), facecolor='#fafbf9')
grid = fig.add_gridspec(2, 6, left=.075, right=.97, top=.785, bottom=.155, hspace=.58, wspace=1.05, height_ratios=[1.35, 1])
fig.text(.075, .95, 'THE MOVING CONTOUR ENCLOSES q', fontsize=24, weight='bold', color='#192d37')
fig.text(.075, .916, 'Conditional geometric attachment  ·  D = 38–39 meV  ·  both engines  ·  N = 8', fontsize=12, color='#4b5d68')
fig.text(.075, .864, '8 cases passed    /    140 covered intervals    /    0 unresolved intervals', fontsize=16, weight='bold', color='#147d82')
fig.text(.075, .834, 'The other two tracked nodes stay outside the ring; the outgoing and return stem avoid all three.', fontsize=11, color='#4b5d68')
ax = fig.add_subplot(grid[0, :4])
colors = ['#899aa5', '#587e99', '#157d82']
for D, color in zip([38., 38.5, 39.], colors):
    geom = next(g for g in case['geometry'] if g['D_meV'] == D)
    v = transform(geom['vertices'])
    ax.plot(v[:, 0], v[:, 1], color=color, lw=1.5, label=f'D = {D:g}')
    for node, marker in [('p', 'o'), ('q', 'o'), ('upper', '^')]:
        r = transform([root_at(node, D)])[0]
        ax.scatter(*r, marker=marker, s=32, color=color, zorder=4)
for node, offset in [('p', (-10, 13)), ('q', (3, 17)), ('upper', (-12, 15))]:
    xy = transform([root_at(node, 38.)])[0]
    ax.annotate(node, xy, xytext=offset, textcoords='offset points', weight='bold', fontsize=11)
base = transform([case['geometry'][0]['vertices'][0]])[0]
ax.annotate('base', base, xytext=(-18, 17), textcoords='offset points', color='#4b5d68')
kink = transform([case['geometry'][-1]['vertices'][1]])[0]
ax.annotate('stem detour', kink, xytext=(-70, -12), textcoords='offset points', color='#4b5d68', arrowprops={'arrowstyle': '-', 'color': '#71818a'})
ax.set(xlim=(-.02, .475), ylim=(-12.5, 5), xlabel='Along p(38) → q(38), in fractional coordinates', ylabel='Transverse offset (×1,000)')
ax.set_title('Declared contour and tracked nodes at three D values', loc='left', weight='bold', pad=12)
ax.grid(alpha=.13); ax.legend(loc='upper left', bbox_to_anchor=(.13, .99), frameon=False, ncol=3, fontsize=9)
ax.text(.015, .025, 'Rotated fractional axes; unequal horizontal and vertical scales.', transform=ax.transAxes, fontsize=8, color='#596b75')

ax = fig.add_subplot(grid[0, 4:])
D = 38.5; q = root_at('q', D)
for radius, color in [(.003, '#147d82'), (.0015, '#9b598e')]:
    c = next(c for c in cases if c['engine'] == 'bm' and c['mesh'] == 'fine' and c['radius'] == radius)
    geom = next(g for g in c['geometry'] if g['D_meV'] == D)
    ring = (np.array(geom['vertices'][2:])-q)*1000
    ax.plot(ring[:, 0], ring[:, 1], color=color, lw=1.6, label=f'r = {radius:g}')
ax.scatter(0, 0, color='#192d37', s=25, zorder=5)
ax.annotate('q', (0, 0), xytext=(6, 6), textcoords='offset points', fontsize=12, weight='bold')
ax.set(xlim=(-3.5, 3.5), ylim=(-3.5, 3.5), xlabel='Δf₁ × 1,000', ylabel='Δf₂ × 1,000')
ax.set_title('Both ring sizes contain q', loc='left', weight='bold', pad=12)
ax.set_aspect('equal'); ax.grid(alpha=.12); ax.legend(loc='lower center', frameon=False, fontsize=8.5)
ax.text(.03, .96, 'D = 38.5\nBM fine', transform=ax.transAxes, va='top', fontsize=8.5, color='#52616b')
# The local uniqueness box is far smaller than the ring: show its true size
# in a separately labelled magnification, without inflating the ring-scale dot.
inset = ax.inset_axes([.67, .63, .31, .29])
path = campaign['nodes']['q']; cell = next(path['attempts'][i] for i in path['leaf_ids'] if path['attempts'][i]['a'] <= D < path['attempts'][i]['b'])
raw = cont['centers'][cell['center']]['raw']
center = np.array(raw['y'][:2])+(D-raw['D_meV'])*np.array(raw['velocity'][:2])
radii = np.array(cell['certificate']['radii'][:2]); lower = (center-radii-q)*1000
inset.add_patch(Rectangle(lower, *(2*radii*1000), facecolor='#147d8244', edgecolor='#147d82', linewidth=1.1))
inset.scatter(0, 0, s=7, color='#192d37'); inset.set(xlim=(-.012, .012), ylim=(-.009, .009))
inset.set_xticks([]); inset.set_yticks([]); inset.set_title('Local box, enlarged', fontsize=7)
for spine in inset.spines.values():
    spine.set_visible(True); spine.set_color('#aeb8bd')

ax = fig.add_subplot(grid[1, :3])
for engine in ['bm', 'ref']:
    for radius, color in [(.003, '#147d82'), (.0015, '#9b598e')]:
        record = next(c for c in data['cases'] if c['engine'] == engine and c['mesh'] == 'coarse' and c['radius'] == radius)
        leaves = [record['attempts'][i] for i in record['leaf_ids']]
        x = [c['a'] for c in leaves]+[leaves[-1]['b']]
        y = [1000*c['bound']['nodes']['q']['polygon']['clearance_bound'] for c in leaves]
        ax.step(x, y+[y[-1]], where='post', color=color, ls='-' if engine == 'bm' else '--', lw=1.6,
                label=f'r = {radius:g}' if engine == 'bm' else None)
ax.set(xlim=(38, 39), ylim=(0, 3.25), xlabel='D (meV)', ylabel='q-to-ring lower clearance × 1,000')
ax.set_title('Positive clearance over every complete interval', loc='left', weight='bold', pad=12)
ax.grid(alpha=.14); ax.legend(loc='center left', bbox_to_anchor=(0, .67), frameon=False, ncol=2, fontsize=9)
ax.text(.02, .05, 'Coarse starting grid · BM solid · REF dashed', transform=ax.transAxes, fontsize=8.5, color='#52616b')

ax = fig.add_subplot(grid[1, 3:])
minima = summary['global_minimum_clearances']
keys = ['q_inside', 'stem_q', 'upper_outside', 'stem_upper', 'p_outside', 'stem_p']
labels = ['q → ring', 'q → stem', 'upper → ring', 'upper → stem', 'p → ring', 'p → stem']
vals = [minima[k] for k in keys]
ax.barh(range(6), vals, color=['#147d82']*2+['#c07938']*2+['#567e9b']*2, height=.55)
ax.set_yticks(range(6), labels); ax.invert_yaxis(); ax.set_xscale('log'); ax.set_xlim(5e-4, 1.7)
for i, v in enumerate(vals):
    ax.text(v*1.12, i, f'{v:.3g}', va='center', fontsize=9)
ax.set_xlabel('Lower clearance, fractional-coordinate units (log scale)')
ax.set_title('Worst bounds across all eight cases', loc='left', weight='bold', pad=12)
ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0); ax.grid(axis='x', alpha=.15)
fig.text(.075, .09, 'The polygon interior beyond the local node box has not been inventoried for unknown nodes.', fontsize=11, weight='bold', color='#52616b')
fig.text(.075, .057, 'Conditional floating-point geometry. The inherited +k loop charge is reused; no complete braid or Euler-class change is claimed.', fontsize=10, color='#52616b')
for extension in ['png', 'svg']:
    fig.savefig(ROOT/f'contour_attachment.{extension}', dpi=190, facecolor=fig.get_facecolor())
print('Rendered source-bound geometry figure:', summary['status'])
