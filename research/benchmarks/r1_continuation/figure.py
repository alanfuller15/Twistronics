"""Scientific figure from reconciled, source-bound interval records only."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from matplotlib.lines import Line2D
from scipy.spatial import ConvexHull
from bounds import ROOT, sha

summary = json.loads((ROOT/'SUMMARY.json').read_text())
assert summary['all_checks_pass']
assert all(sha(ROOT/n) == h for n, h in summary['source_hashes'].items())
data = json.loads((ROOT/'RESULTS.json').read_text())
campaigns = {c['engine']: c for c in data['campaigns'] if c['initial_intervals'] == 16}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 12,
                     'axes.labelsize': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.fonttype': 'none', 'savefig.facecolor': '#fafbf9'})
fig = plt.figure(figsize=(13.6, 9.8), facecolor='#fafbf9')
gs = fig.add_gridspec(2, 6, left=.075, right=.97, top=.78, bottom=.14,
                      height_ratios=[1.35, 1], hspace=.62, wspace=1.05)
teal, purple = '#147d82', '#8a528b'
node_colors = {'p': '#2971a9', 'q': '#168569', 'upper': '#c36b1e'}
fig.text(.075, .949, 'FOLLOWING THREE LOCAL NODES', fontsize=23, weight='bold', color='#192d37')
fig.text(.075, .916, 'Conditional continuous tracking  ·  N = 8  ·  layer potentials ±D  ·  fixed strain', fontsize=12, color='#465965')
t = summary['totals']
fig.text(.075, .867, f"{t['accepted_leaves']} accepted intervals    /    {t['endpoint_containments']} endpoint links    /    0 unresolved leaves",
         fontsize=15, color=teal, weight='bold')
fig.text(.075, .836, 'Counts combine two engines and both starting grids. Panels show the finer starting grid.', fontsize=10, color='#52616b')
for k, node in enumerate(['p', 'q', 'upper']):
    ax = fig.add_subplot(gs[0, 2*k:2*k+2])
    start = np.array(data['centers'][campaigns['bm']['nodes'][node]['points'][0]['center']]['raw']['y'][:2])
    for engine, color in [('bm', teal), ('ref', purple)]:
        path = campaigns[engine]['nodes'][node]
        for idx in path['leaf_ids']:
            cell = path['attempts'][idx]; raw = data['centers'][cell['center']]['raw']; cert = cell['certificate']
            ends = np.array([np.array(raw['y'][:2])+(D-raw['D_meV'])*np.array(raw['velocity'][:2]) for D in [cell['a'], cell['b']]])
            radius = np.array(cert['radii'][:2])
            corners = np.array([c+radius*[s1, s2] for c in ends for s1 in [-1, 1] for s2 in [-1, 1]])
            corners = (corners-start)*1000
            hull = ConvexHull(corners)
            ax.add_patch(Polygon(corners[hull.vertices], facecolor=color if engine == 'bm' else 'none',
                                 edgecolor=color, alpha=.2 if engine == 'bm' else .7,
                                 linewidth=.6, linestyle='-' if engine == 'bm' else ':'))
        points = np.array([data['centers'][p['center']]['raw']['y'][:2] for p in path['points']])
        xy = (points-start)*1000
        if engine == 'bm':
            ax.plot(xy[:, 0], xy[:, 1], '.', color='#3d505b', ms=3, zorder=4)
            ax.scatter(*xy[0], s=38, color='#192d37', zorder=5)
            ax.scatter(*xy[-1], s=68, color='#192d37', marker='*', zorder=5)
    ax.autoscale_view(); ax.margins(.15)
    ax.set_title(['p · flat-band crossing', 'q · flat-band crossing', 'Upper-gap crossing'][k], loc='left', weight='bold', pad=10)
    ax.set_xlabel(r'$10^3\,[f_1(D)-f_1(38)]$')
    ax.set_ylabel(r'$10^3\,[f_2(D)-f_2(38)]$')
    ax.grid(alpha=.16); ax.set_aspect('equal', adjustable='datalim')
fig.legend(handles=[Patch(facecolor=teal, edgecolor=teal, alpha=.25, label='BM tube projection'),
                    Patch(facecolor='none', edgecolor=purple, linestyle=':', label='REF tube projection'),
                    Line2D([], [], marker='o', color='none', markerfacecolor='#192d37', markeredgecolor='#192d37', label='D = 38'),
                    Line2D([], [], marker='*', color='none', markerfacecolor='#192d37', markeredgecolor='#192d37', markersize=9, label='D = 39')],
           loc='upper center', bbox_to_anchor=(.52, .455), ncol=4, frameon=False, fontsize=9)
ax = fig.add_subplot(gs[1, :3])
for engine in ['bm', 'ref']:
    for node, color in node_colors.items():
        path = campaigns[engine]['nodes'][node]
        leaves = [path['attempts'][i] for i in path['leaf_ids']]
        x = [c['a'] for c in leaves]+[leaves[-1]['b']]
        y = [c['certificate']['q'] for c in leaves]
        ax.step(x, y+[y[-1]], where='post', color=color, ls='-' if engine == 'bm' else '--', lw=1.5)
ax.axhline(.5, color='#ab4141', lw=1.1)
ax.text(38.02, .512, 'Acceptance limit q = 0.5', color='#934040', fontsize=9)
ax.set(xlim=(38, 39), ylim=(0, .565), xlabel='D (meV)', ylabel='Uniform contraction bound q')
ax.set_title('Each entire interval passes the contraction test', loc='left', weight='bold', pad=12)
ax.grid(alpha=.14)
ax.legend(handles=[Line2D([], [], color=c, label=n) for n, c in node_colors.items()], loc='center left', ncol=3, frameon=False, fontsize=9)
ax.text(.015, .03, 'BM solid · REF dashed', transform=ax.transAxes, fontsize=8.5, color='#52616b')
ax = fig.add_subplot(gs[1, 3:])
labels = []
for i, (engine, node) in enumerate((e, n) for e in ['bm', 'ref'] for n in ['p', 'q', 'upper']):
    path = campaigns[engine]['nodes'][node]
    leaves = [path['attempts'][k] for k in path['leaf_ids']]
    for c in leaves:
        ax.broken_barh([(c['a'], c['b']-c['a'])], (5-i-.28, .56), facecolor=node_colors[node], edgecolor='white', linewidth=.7)
    labels.append(f'{engine.upper()} {node}  ({len(leaves)})')
ax.set(yticks=list(range(5, -1, -1)), yticklabels=labels, xlim=(38, 39), ylim=(-.7, 5.7), xlabel='D (meV)')
ax.set_title('Accepted coverage, with every endpoint linked', loc='left', weight='bold', pad=12)
ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)
fig.text(.075, .075, 'Shading outlines coordinate projections of local uniqueness tubes; it is not a statistical uncertainty band.', fontsize=10, color='#465965')
fig.text(.075, .047, 'Floating-point bounds with declared allowances. No global node inventory, full braid or Euler-class conclusion.', fontsize=10, color='#465965')
for ext in ['png', 'svg']:
    fig.savefig(ROOT/f'node_continuation.{ext}', dpi=190)
print('Rendered source-bound continuation figure:', summary['status'])
