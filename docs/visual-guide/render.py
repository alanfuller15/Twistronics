"""Render retained research records only; never import or run numerical engines.

Run from any directory: python docs/visual-guide/render.py
Requires matplotlib and numpy. Outputs are confined to this guide's figures/.
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'figures'
MANIFEST = json.loads((HERE / 'sources.json').read_text())
for path, expected in MANIFEST['inputs'].items():
    if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
        raise ValueError(f'Source hash mismatch: {path}')
summary = json.loads((ROOT / 'research/v062/SUMMARY.json').read_text())
engines = ['bm_lab', 'ref_lab']
names = ['BM / linear reciprocal geometry', 'Reference / exact reciprocal geometry']
raw = [json.loads((ROOT / f'research/v062/results/second_{e}_N8.json').read_text()) for e in engines]
for data, case in zip(raw, summary['cases']):
    assert data['engine'] == case['engine']
    assert [s['ratio'] for s in data['states']] == summary['ratios']
    assert [s['label'] for s in data['states']] == case['labels']
    for node, point in case['endpoint_nodes'].items():
        assert data['states'][-1]['nodes'][node]['f'] == point
    for state in data['states']:
        assert all(n['success'] and np.isfinite(n['f']).all() for n in state['nodes'].values())
        assert all(t['label'] == state['label'] for t in state['charge']['trials'])
    gap = min(t['min_external_gap'] for s in data['states'] for t in s['spatial_transport'])
    assert np.isclose(gap, case['min_comparison_gap'], rtol=1e-10, atol=1e-12)

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.labelcolor': '#24354b', 'text.color': '#172a42',
    'axes.titleweight': 'bold', 'svg.fonttype': 'none', 'svg.hashsalt': 'twistronics-v062',
    'figure.facecolor': '#ffffff', 'axes.facecolor': '#f7f9fc'})
OUT.mkdir(exist_ok=True)

def finish(fig, name, title, subtitle, footnote):
    fig.suptitle(title, x=.08, y=.975, ha='left', fontsize=20, weight='bold')
    fig.text(.08, .89, subtitle, fontsize=11)
    fig.text(.08, .025, footnote + '\nSource: retained v062 records at ' + MANIFEST['source_commit'][:12], fontsize=9, color='#536579')
    fig.subplots_adjust(left=.13, right=.97, top=.72, bottom=.23, wspace=.34)
    fig.savefig(OUT / f'{name}.svg', metadata={'Date': None})
    fig.savefig(OUT / f'{name}.png', dpi=160)
    plt.close(fig)

# Coordinates are fractional and unwrapped. Lines connect samples only.
colors = ['#007f86', '#136aaf', '#b85b14', '#a94b79', '#7465a8', '#627226']
fig, axes = plt.subplots(1, 2, figsize=(12, 6.6), sharex=True, sharey=True)
for ax, data, title in zip(axes, raw, names):
    for node, color in zip(['U1', 'U2', 'X1', 'X2', 'X3', 'X4'], colors):
        coords = np.array([s['nodes'][node]['f'] for s in data['states']])
        ax.plot(*coords.T, '-o', color=color, lw=1.5, ms=3)
        ax.scatter(*coords[0], s=65, facecolor='white', edgecolor=color, zorder=4)
        ax.scatter(*coords[-1], s=45, marker='s', color=color, zorder=5)
        ax.annotate(node, coords[-1], xytext=(7, 5), textcoords='offset points', color=color)
    ax.axhline(1, lw=.8, ls=':', color='#8b98a6')
    ax.set(xlim=(.24,.61), ylim=(.59,1.055), xlabel='Fractional reciprocal coordinate f1', title=title)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(alpha=.15)
axes[0].set_ylabel('Fractional reciprocal coordinate f2')
fig.legend(handles=[Line2D([],[],marker='o',mfc='white',color='#536579',ls='',label='Start: ratio 0.991'),Line2D([],[],marker='s',color='#536579',ls='',label='End: ratio 1.000')],loc='lower center',bbox_to_anchor=(.55,.78),ncol=2,frameon=False)
finish(fig,'node-paths','Where the tracked band crossings move',
       'N8 continuation: 11 measured states per engine, six seeded nodes at each state.',
       'Lines guide the eye between samples; this segment alone does not demonstrate a full braid. f2 > 1 is intentional.')

# Discrete spatial comparisons: do not interpolate across the singular event.
fig, ax = plt.subplots(figsize=(12,4.6))
for i, chain in enumerate(summary['combined_braid2_chain']):
    for label, marker, color in [('SAME','s','#b85b14'),('OPPOSITE','o','#007f86')]:
        xs = [r for r,lab in zip(chain['ratios'],chain['labels']) if lab==label]
        ax.scatter(xs,[1-i]*len(xs),s=65,marker=marker,color=color,zorder=3)
ax.axvspan(.99075,.991,color='#ced8e3',alpha=.6)
ax.set(yticks=[0,1],yticklabels=['Reference N8','BM N8'],ylim=(-.6,1.6),xlim=(.9897,1.0003),xlabel='Interlayer tunnelling ratio w0 / w1')
ax.ticklabel_format(useOffset=False,axis='x')
ax.grid(axis='x',alpha=.2)
fig.legend(handles=[Line2D([],[],marker='s',color='#b85b14',ls='',label='SAME'),Line2D([],[],marker='o',color='#007f86',ls='',label='OPPOSITE')],loc='lower center',bbox_to_anchor=(.6,.78),ncol=2,frameon=False)
finish(fig,'charge-comparison','Both engines give the same spatial classification',
       '15 distinct sampled ratios per engine: retained v060 window + v062 continuation.',
       'Shading brackets the change between sampled labels, not its exact location. No continuous-path proof is implied.')

fig, axes = plt.subplots(1,2,figsize=(12,5.9))
for data, name, color, marker in zip(raw,['BM','Reference'],['#007f86','#a94b79'],['o','x']):
    xs=[s['ratio'] for s in data['states']]
    ys=[min(t['min_external_gap'] for t in s['spatial_transport']) for s in data['states']]
    axes[0].plot(xs,ys,marker=marker,color=color,label=name,ms=5,lw=1)
axes[0].set(xlabel='w0 / w1',ylabel='Located exterior gap minimum (meV)',yscale='log',title='Isolation along the comparison path')
axes[0].ticklabel_format(useOffset=False,axis='x')
axes[0].legend(frameon=False)
for c in summary['cutoff_comparisons']:
    offset=-.08 if c['engine']=='bm_lab' else .08
    color='#007f86' if c['engine']=='bm_lab' else '#a94b79'
    marker='o' if c['engine']=='bm_lab' else 'x'
    axes[1].scatter(c['saved_cutoff']+offset,c['max_node_displacement'],c=color,marker=marker,s=65)
axes[1].set(xlabel='Retained cutoff compared with N8',ylabel='Maximum root displacement (fractional coordinates)',yscale='log',xticks=[4,6],xticklabels=['N4 → N8','N6 → N8'],xlim=(3.5,6.5),title='Sensitivity to momentum cutoff')
for ax in axes: ax.grid(alpha=.18)
finish(fig,'numerical-checks','How sensitive are the reported results?',
       'Left: sampled/refined path minima. Right: maximum across six roots and ten common ratios.',
       'N4/N6 records are retained comparisons, not new runs. Located minima are not global gap bounds or error bars.')
print('Verified source hashes, 22 state labels, 132 root records, endpoints and gap minima; rendered three figures.')
