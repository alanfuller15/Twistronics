"""Source-bound inventory map, core energy capture, and coverage totals."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm
from matplotlib.cm import ScalarMappable
from inventory import ROOT, sha
from sources import read_attachment_inputs

summary = json.loads((ROOT/'SUMMARY.json').read_text())
assert summary['all_checks_pass']
assert all(sha(ROOT/n) == h for n, h in summary['source_hashes'].items())
data = json.loads((ROOT/'RESULTS.json').read_text())
campaign = next(c for c in data['campaigns'] if c['engine'] == 'bm' and c['grid'] == 8)
reference = campaign['references'][0]
assert sha(ROOT/campaign['arrays_file']) == campaign['arrays_sha256']
with np.load(ROOT/campaign['arrays_file']) as archive:
    rows = archive[reference['key']]
delta = .2*reference['halfwidth']; D = reference['primitives']['D_meV']+delta
leaves = rows[(rows[:, 10] == 1) & (rows[:, 2] <= delta) & (rows[:, 5] > delta)]
R = np.array(reference['outer_radii']); radius = np.array(reference['parent_certificate']['radii'])
p = reference['primitives']; predictor = np.array(p['y'][:2])+delta*np.array(p['velocity'][:2])
_, cases, _ = read_attachment_inputs()
norm = LogNorm(vmin=min(leaves[:, 17]), vmax=max(leaves[:, 17])); cmap = plt.get_cmap('YlGnBu')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 12,
                     'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(13.6, 9.8), facecolor='#fafbf9')
fig.text(.07, .949, 'SINGLE-NODE INVENTORY INSIDE THE LOOPS', fontsize=23, weight='bold', color='#192d37')
fig.text(.07, .916, 'Conditional finite-model result  ·  selected bands 297–299  ·  N = 8  ·  D = 38–39 meV', fontsize=11.5, color='#52616b')
fig.text(.07, .859, '1,248 exclusion cells    /    48 energy-capture checks    /    0 unresolved regions', fontsize=15.5, weight='bold', color='#147d82')
fig.text(.07, .828, 'Totals combine both engines and both continuation grids. The map below is one slice of the full continuous cover.', fontsize=10, color='#52616b')

ax = fig.add_axes([.075, .24, .49, .52])
def cells_on_axis(axis):
    for row in leaves:
        axis.add_patch(Rectangle(row[:2]*1000, *((row[3:5]-row[:2])*1000),
                                 facecolor=cmap(norm(row[17])), edgecolor='#607882', linewidth=.45))
    axis.add_patch(Rectangle(-radius[:2]*1000, *(2*radius[:2]*1000), facecolor='white', edgecolor='#192d37', linewidth=1.1, zorder=4))
    axis.scatter(0, 0, color='#bf533c', s=20, zorder=5, label='predictor; q lies in core')
cells_on_axis(ax)
for r, style in [(.003, '-'), (.0015, '--')]:
    case = next(c for c in cases if c['engine'] == 'bm' and c['mesh'] == 'fine' and c['radius'] == r)
    j = next(j for j in range(len(case['geometry'])-1) if case['geometry'][j]['D_meV'] <= D <= case['geometry'][j+1]['D_meV'])
    a, b = case['geometry'][j:j+2]; t = (D-a['D_meV'])/(b['D_meV']-a['D_meV'])
    ring = ((1-t)*np.array(a['vertices'][2:])+t*np.array(b['vertices'][2:])-predictor)*1000
    ax.plot(ring[:, 0], ring[:, 1], style, color='#7b344e', lw=1.4, label=f'ring r = {r:g}')
ax.set(xlim=(-R[0]*1000, R[0]*1000), ylim=(-R[1]*1000, R[1]*1000), xlabel='u₁ × 1,000 (relative to q predictor)', ylabel='u₂ × 1,000 (relative to q predictor)')
ax.set_aspect('equal'); ax.set_title(f'No additional crossing outside the white core\nBM, coarse continuation · D = {D:.3f} meV', loc='left', weight='bold', fontsize=12, pad=10)
ax.legend(loc='upper left', frameon=True, framealpha=.92, fontsize=8.5)
inset = ax.inset_axes([.65, .055, .31, .31])
cells_on_axis(inset); inset.set(xlim=(-.12, .12), ylim=(-.12, .12)); inset.set_xticks([]); inset.set_yticks([])
inset.set_title('Core enlarged', fontsize=8)
for spine in inset.spines.values():
    spine.set_visible(True); spine.set_color('#536872')
color_axis = fig.add_axes([.115, .158, .405, .022])
cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=color_axis, orientation='horizontal')
cb.set_label('Uniform node-exclusion margin over each 3D cell (meV)', fontsize=9)
cb.ax.tick_params(labelsize=8)

ax = fig.add_axes([.655, .535, .29, .205])
bridge = reference['core_energy_capture']; parent = bridge['parent_energy_radius']*1000; captured = bridge['candidate_energy_upper']*1000
ax.add_patch(Rectangle((-parent, .15), 2*parent, .65, facecolor='#e1eaf0', edgecolor='#516f85', linewidth=1.2))
ax.add_patch(Rectangle((-captured, .15), 2*captured, .65, facecolor='#70b6ae', edgecolor='#147d82', linewidth=1.2))
ax.axvline(0, color='#536872', ls=':', lw=.8)
ax.set(xlim=(-parent*1.15, parent*1.15), ylim=(0, 1.05), xlabel='E − Ebar(D)  (10⁻³ meV)', yticks=[])
ax.set_title('The core also fits in the energy window', loc='left', weight='bold', pad=14)
ax.text(0, .94, 'Parent uniqueness window', ha='center', va='center', fontsize=10, color='#516f85')
ax.text(0, .48, 'All candidate\ncrossing energies', ha='center', va='center', fontsize=9, color='#143b3b')
ax.text(.5, -.36, 'This bound covers the entire reference D interval\nand the unchanged momentum core.', ha='center', transform=ax.transAxes, fontsize=9, color='#52616b')
ax.spines['left'].set_visible(False)

ax = fig.add_axes([.655, .19, .29, .21])
labels = [f"{c['engine'].upper()} · {c['grid']} intervals" for c in summary['campaigns']]
values = [c['accepted_leaves'] for c in summary['campaigns']]
ax.barh(range(4), values, color=['#497f96', '#147d82', '#497f96', '#147d82'], height=.55)
ax.set_yticks(range(4), labels); ax.invert_yaxis(); ax.set_xlim(0, 535)
for i, v in enumerate(values):
    ax.text(v+9, i, str(v), va='center', fontsize=10)
ax.set_title('Complete exclusion coverage in both engines', loc='left', weight='bold', pad=12)
ax.set_xlabel('Accepted cells outside the core'); ax.tick_params(axis='y', length=0); ax.spines['left'].set_visible(False)
ax.grid(axis='x', alpha=.15)
fig.text(.07, .09, 'The prior +k based-loop label can now be assigned to q within the existing frame and stem convention.', fontsize=11, color='#192d37')
fig.text(.07, .055, 'Conditional floating-point bounds. This is a local three-band inventory, not a full braid, Euler-class calculation or global node count.', fontsize=10, color='#52616b')
for ext in ['png', 'svg']:
    fig.savefig(ROOT/f'interior_inventory.{ext}', dpi=190, facecolor=fig.get_facecolor())
print('Rendered source-bound interior inventory:', summary['status'])
