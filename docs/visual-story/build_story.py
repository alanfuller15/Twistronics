"""Build an explanatory plate, measured-step GIF and offline explorer.
Reads saved JSON only; never imports or executes research engines.
"""
import hashlib, io, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BG='#091525'; FG='#e9f0fa'; MUT='#a5b8ce'; CYAN='#4adbc8'; GOLD='#ffbd69'
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':FG,'axes.labelcolor':MUT,'xtick.color':MUT,'ytick.color':MUT,'axes.edgecolor':'#48617d','axes.facecolor':BG,'figure.facecolor':BG,'font.size':11})
data={}; inputs={}
for eng in ['bm_lab','ref_lab']:
    chain=[]
    for v in ['v060','v062']:
        path=f'research/{v}/results/second_{eng}_N8.json'
        b=(ROOT/path).read_bytes(); inputs[path]=hashlib.sha256(b).hexdigest()
        raw=json.loads(b)
        for s in raw['states']:
            entry={'ratio':s['ratio'],'label':s['label'],'nodes':{k:n['f'] for k,n in s['nodes'].items()},'source':v}
            assert all(n['success'] for n in s['nodes'].values())
            if chain and chain[-1]['ratio']==entry['ratio']:
                assert chain[-1]['label']==entry['label']
                assert max(np.linalg.norm(np.array(chain[-1]['nodes'][n])-entry['nodes'][n]) for n in entry['nodes'])<1e-8
                entry['source']='v060/v062 join'; chain[-1]=entry
            else: chain.append(entry)
    assert len(chain)==15
    data[eng]=chain
summary_bytes=(ROOT/'research/v062/SUMMARY.json').read_bytes()
inputs['research/v062/SUMMARY.json']=hashlib.sha256(summary_bytes).hexdigest()
summary=json.loads(summary_bytes)
for chain in summary['combined_braid2_chain']:
    assert chain['ratios']==[s['ratio'] for s in data[chain['engine']]]
    assert chain['labels']==[s['label'] for s in data[chain['engine']]]
manifest={'scope':'Conceptual layer/band illustrations; measured node states from retained v060/v062, no interpolated coordinates.','inputs_sha256':inputs}
(HERE/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n')

def lattice(angle=0):
    bonds=[]
    for i in range(-14,15):
        for j in range(-14,15):
            a=np.array([np.sqrt(3)*(i+j/2),1.5*j])
            for d in [[0,1],[-np.sqrt(3)/2,-.5],[np.sqrt(3)/2,-.5]]:
                b=a+d
                if max(np.linalg.norm(a),np.linalg.norm(b))<15: bonds.append([a,b])
    a=np.deg2rad(angle); r=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
    return np.array(bonds)@r.T

fig=plt.figure(figsize=(12,11),facecolor=BG)
fig.text(.065,.965,'SMALL TWIST. DIFFERENT ELECTRONIC LANDSCAPE.',color=CYAN,fontsize=12,weight='bold')
fig.text(.065,.855,'From graphene layers\nto moving band crossings',fontsize=31,weight='bold',linespacing=1.12)
fig.text(.065,.785,'Two explanatory views, followed by the actual saved calculation.',color=MUT,fontsize=13)
ax=fig.add_axes([.055,.36,.43,.37]);
for angle,c in [(0,CYAN),(7,GOLD)]:ax.add_collection(LineCollection(lattice(angle),colors=c,linewidths=.55,alpha=.7))
ax.set(xlim=(-15,15),ylim=(-15,15),aspect='equal');ax.axis('off')
fig.text(.065,.735,'01  ROTATED LAYERS',fontsize=13,weight='bold')
fig.text(.065,.315,'Two honeycomb patterns form a larger moiré pattern.\n7° is exaggerated here to make the geometry visible.',fontsize=11,color=MUT)
ax=fig.add_axes([.52,.355,.43,.38],projection='3d')
x=np.linspace(-1,1,65);X,Y=np.meshgrid(x,x);E=np.sqrt(X*X+Y*Y)
for sign,c in [(1,CYAN),(-1,GOLD)]:ax.plot_surface(X,Y,sign*E,color=c,alpha=.77,linewidth=0,antialiased=True)
ax.scatter([0],[0],[0],s=55,color=FG);ax.view_init(18,-58);ax.set_axis_off()
fig.text(.535,.735,'02  A BAND CROSSING',fontsize=13,weight='bold')
fig.text(.535,.315,'Two energy surfaces touch at a node in momentum space.\nIdealized cone; not a computed graphene band surface.',fontsize=11,color=MUT)
fig.text(.065,.225,'03  FOLLOW THE NODES',fontsize=13,weight='bold',color=CYAN)
fig.text(.065,.168,'The measured animation steps through 15 saved parameter states.\nIt follows selected crossings and compares their spatial charge labels.',fontsize=15)
fig.text(.065,.065,'Layer and cone views are schematic. The node animation uses recorded data.\nA charge-label change is not, by itself, proof of a complete braid or experimental realization.',color=MUT,fontsize=10)
fig.savefig(HERE/'visual-introduction.png',dpi=130);plt.close(fig)

# Each frame is a saved state. Deliberately no interpolation or fabricated camera motion.
frames=[]
colors={'U1':CYAN,'U2':CYAN,'X1':GOLD,'X2':GOLD,'X3':GOLD,'X4':GOLD}
for idx in range(15):
    fig=plt.figure(figsize=(11,7),facecolor=BG)
    s=data['bm_lab'][idx]
    fig.text(.065,.93,'FOLLOWING THE SAVED NODES',color=CYAN,fontsize=12,weight='bold')
    fig.text(.065,.867,f"w0 / w1 = {s['ratio']:.5f}",fontsize=26,weight='bold')
    fig.text(.65,.90,f"STATE {idx+1:02d} / 15",fontsize=12,color=MUT)
    fig.text(.65,.848,'Spatial comparison: '+s['label'],fontsize=15,color=GOLD if s['label']=='SAME' else CYAN)
    ax=fig.add_axes([.09,.18,.42,.60]); zoom=fig.add_axes([.60,.30,.34,.43])
    for a in [ax,zoom]:
        for n,c in colors.items():
            coords=np.array([q['nodes'][n] for q in data['bm_lab']]);pos=coords[idx]
            a.plot(*coords.T,color=c,alpha=.18,lw=1.3)
            a.plot(*coords[:idx+1].T,color=c,alpha=.8,lw=2)
            a.scatter(*pos,c=c,s=70 if n.startswith('U') else 40,marker='o' if n.startswith('U') else 'D',zorder=5)
            if a is ax or n in ['U1','X1','X2']:a.annotate(n,pos,xytext=(8,6),textcoords='offset points',color=c,fontsize=11)
        a.set_xlabel('f1 (fractional reciprocal coordinate)',fontsize=9);a.set_ylabel('f2',fontsize=10)
        a.spines[['top','right']].set_visible(False);a.grid(alpha=.12)
    ax.set(xlim=(.235,.60),ylim=(.59,1.06),aspect='equal');zoom.set(xlim=(.40,.57),ylim=(.75,.88),aspect='equal')
    zoom.set_title('Closer view: U1 and adjacent-gap nodes',fontsize=10,color=MUT,pad=12)
    fig.text(.60,.20,'Circles: selected U pair    Diamonds: X nodes\nFaint tracks: all saved positions',color=MUT,fontsize=10)
    fig.text(.065,.065,'BM engine · N8 · discrete saved states, no interpolation · '+s['source'],color=MUT,fontsize=10)
    fig.text(.065,.028,'Coordinates are momentum-space labels. Charge comparison follows a specified frame-transport path.',color=MUT,fontsize=9)
    buf=io.BytesIO();fig.savefig(buf,format='png',dpi=100);plt.close(fig);buf.seek(0);frames.append(Image.open(buf).convert('RGB'))
frames[0].save(HERE/'measured-nodes.gif',save_all=True,append_images=frames[1:],duration=[950]*14+[2500],loop=0,optimize=False)
frames[0].save(HERE/'measured-nodes-poster.png')
template=(HERE/'explorer-template.html').read_text()
(HERE/'explorer.html').write_text(template.replace('__MEASURED_DATA__',json.dumps(data,separators=(',',':'))))
print('Built explanatory plate, 15-state measured GIF, and offline explorer. Both engines match published chain labels.')
