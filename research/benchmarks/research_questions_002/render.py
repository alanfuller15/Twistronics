"""Render retained calibration data and explicitly labelled analytic curves."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent


def main(preview=None):
    r = json.loads((ROOT/'RESULTS.json').read_text())
    if not r['passed'] or hashlib.sha256((ROOT/'calibrate.py').read_bytes()).hexdigest() != r['source_sha256']:
        raise RuntimeError('retained results must pass and match producer source')
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11,
                         'axes.spines.top':False, 'axes.spines.right':False,
                         'svg.hashsalt':'questions002', 'axes.titleweight':'bold'})
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.5), gridspec_kw={'width_ratios':[1, 1.25]})
    fig.patch.set_facecolor('#f6f5f0')
    for ax in axes:
        ax.set_facecolor('#f6f5f0')
    fig.suptitle('Production calibration — and a limit of sampling', x=.075, ha='left', fontsize=21, fontweight='bold')
    fig.text(.075, .883, 'Unmodified guarded Euler routine · synthetic three-band inputs', fontsize=12, color='#475569')

    ax=axes[0]
    for m, color in [(-1,'#176b70'),(-3,'#92702a')]:
        case=next(c for c in r['cases'] if c['name']==f'sphere_m{m}_mesh96')
        phase=np.array(case['result']['phases_rad'])
        phase=-case['base_orientation']*np.unwrap(phase)/(2*np.pi)
        phase-=phase[0]
        ax.plot(np.linspace(0,1,len(phase)),phase,lw=2.6,color=color,label=f'm={m}: Euler {2 if m==-1 else 0}')
    ax.set(title='Known answers recovered', xlabel='Transverse coordinate f₁', ylabel='Oriented phase change / 2π')
    ax.set_yticks([0,1,2]);ax.grid(axis='y',alpha=.15);ax.legend(frameon=False,loc='upper left')

    ax=axes[1]
    f=np.linspace(0,3/48,2401)
    # Along ky=0, H_zz=cos(2*folds*kx). These are analytic curves,
    # not additional production samples or an inferred interpolation.
    ax.plot(48*f,np.cos(196*np.pi*f),color='#bb604b',lw=1.7,label='49 folds: analytic Euler 98')
    ax.plot(48*f,np.cos(4*np.pi*f),color='#176b70',lw=2.6,label='1 fold: analytic Euler 2')
    samples=np.arange(4)/48
    ax.scatter(48*samples,np.cos(4*np.pi*samples),c='#152638',s=44,zorder=5,label='Identical sampled values')
    ax.set(title='Variation hidden between samples',xlabel='f₁ in units of one mesh interval (1/48)',ylabel='Hzz at ky=0 (analytic)')
    ax.set_xticks([0,1,2,3]);ax.set_ylim(-1.1,1.8);ax.set_yticks([-1,0,1]);ax.grid(axis='x',alpha=.15)
    ax.legend(frameon=False,fontsize=9,loc='upper right')
    fig.text(.075,.10,'Alias witness: sampled overlap ≥ 0.991, phase step ≤ 0.815 rad — yet the returned integer is 2, not 98.',fontsize=11,fontweight='bold',color='#793e31')
    fig.text(.075,.048,'Fixed reference calibration and explicit counterexample. No TBG sweep, experimental result, or continuous-resolution proof.',fontsize=10,color='#475569')
    fig.subplots_adjust(left=.075,right=.98,top=.77,bottom=.25,wspace=.32)
    svg = ROOT/'calibration-and-aliasing.svg'
    fig.savefig(svg,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    if preview:
        fig.savefig(preview,dpi=150)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview',type=Path)
    main(p.parse_args().preview)
