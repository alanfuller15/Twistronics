"""Bounded source-to-log attribution; retained text is not execution proof."""
import ast
from pathlib import Path
from evidence import read,sha,safe,require,write
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
ROWS=[
 ('B1','run_baseline_convergence.py',['TWISTRONICS_LOG_v023.md'],
  'v023 §3: baseline dimensions, bandwidth, two near-zero roots and remote minimum',
  'find_nodes and min_remote call BM.refine without return_result and do not inspect last_refine. find_nodes returns all refined local minima, including positive-gap candidates; it is not a certified node count.',
  'Fresh controlled baseline comparison at N4/N6; original N3/N5/N7 and phi sweeps not replayed.'),
 ('B2','run_scalar_sweep.py',['TWISTRONICS_LOG_v023.md'],
  'v023 §4: scalar-amplitude sweep',
  'Uses find_nodes/min_remote; filters candidates by value below 1e-3, without checking optimizer metadata.',
  'Only A=0 is shared with this batch baseline. Other scalar amplitudes remain impact-unverified.'),
 ('B3','lowergap_check.py',['TWISTRONICS_LOG_v035.md'],
  'v035 §2: edge minimum correction; lower|flat1 22.537986/22.691985 meV',
  'Calls refine(return_result=True), recomputes the selected gap and prints success. It does not reject success=False before selecting or printing the minimum.',
  'Fresh controlled lower|flat1 search at N4/N6, all selected seeds on grids 24/36. The separate below-lower gap is not replayed.'),
 ('E1','euler.py',['TWISTRONICS_LOG_v023.md','TWISTRONICS_LOG_v035.md'],
  'v023 §5 baseline e2=-1; v035 reports two gated Euler comparisons',
  'Raw Wilson routine returns winding, determinants and closure without a fail-closed acceptance decision. The current reality guard differs from the retained older assertion; neither supplies the missing isolation/orientability gate.',
  'Baseline raw value compared with two gated meshes at N4/N6. N4 A=0.1 and unstrained cases not replayed; no original Euler JSON run record was located by the stated search.'),
 ('E2','nodewind.py',['TWISTRONICS_LOG_v023.md'],
  'v023 §5 per-node eigenvector rotation and shared handedness',
  'Uses find_nodes, takes the first two filtered roots, prints rounded raw windings and their sum. Raw output is not a modern acceptance certificate.',
  'Source-to-log relationship is contextual. This batch does not rerun this node-winding driver.'),
 ('E3','braid.py',['TWISTRONICS_LOG_v024.md','TWISTRONICS_LOG_v034.md'],
  'v024 path-dependent charge diagnostics; v034 remediation claims',
  'Direct driver exposes fixed-radius windings and path detours. adjacent_nodes reaches BM.refine. Importing classify does not show that the CLI uses it to gate its printed winding.',
  'The whole driver and all detours remain impact-unverified. v024 already records a failed detour construction; v056 only tested its five explicitly selected later recipes.'),
 ('E4','transfer.py',['TWISTRONICS_LOG_v029.md'],
  'v029 §4: obstruction transfer and blocked Euler readout',
  'Defines its own Euler routine and a local frame() that takes HR.real without a reality guard. A fix in euler.real_frame does not repair this local function.',
  'v029 explicitly withholds an Euler-class conclusion because the relevant bundle is not isolated; it also warns that the 21-point gap grid misses U nodes. The printed raw Euler numbers are not adopted as valid invariants by that entry.'),
 ('E5','flat_e2.py',['TWISTRONICS_LOG_v032.md','TWISTRONICS_LOG_v033.md'],
  'v032–v033 revise the earlier prediction e2=0 to undefined for the nonorientable flat pair',
  'Defines a separate Euler routine and prints winding, closure and minimum determinant. These diagnostics are not enforced as an acceptance gate inside that routine.',
  'The logs already reject e2=0 as the endpoint statement and use per-band w1. This is a preserved correction, not a newly discovered label change.'),
]

def build():
    idx=read(ROOT/'SOURCE_INDEX.json');partner=safe(REPO,idx['partner']);logs=partner.parent
    preserved=read(ROOT/'PRESERVED_TREE.json')['files'];sources={};rows=[]
    def bind(p):
        name=p.relative_to(REPO).as_posix();sources[name]=sha(p);return name
    for id,name,entries,claim,consumer,disposition in ROWS:
        p=partner/name;source=p.read_text();tree=ast.parse(source)
        relevant=[dict(line=n.lineno,call=ast.unparse(n.func)) for n in ast.walk(tree) if isinstance(n,ast.Call) and (isinstance(n.func,ast.Name) and n.func.id in ['euler','node_winding','classify'] or isinstance(n.func,ast.Attribute) and n.func.attr in ['refine','find_nodes','min_remote'])]
        copies=[]
        for n in preserved:
            if Path(n).name==name and n.endswith('.py'):
                q=safe(REPO,n);copies.append(dict(path=bind(q),sha256=sha(q)))
        rows.append(dict(id=id,source=bind(p),source_sha256=sha(p),log_claim=claim,logs=[dict(path=bind(logs/e),sha256=sha(logs/e)) for e in entries],consumer=consumer,disposition=disposition,call_sites=sorted(relevant,key=lambda x:x['line']),retained_copies=copies,distinct_source_hashes=len({c['sha256'] for c in copies}),attribution='contextual code/parameter/log agreement; not original execution provenance'))
    history=safe(REPO,idx['batches']['v042']).parent/'prior_v040/our_v038'
    manifest=read(history/'sources/input_manifest.json');checks={}
    for name,entry in manifest['copied_engines'].items():
        p=history/'engines'/name;checks[name]=sha(p)==entry['sha256'];require(checks[name],'retained engine provenance mismatch');bind(p)
    bind(history/'sources/input_manifest.json')
    raw=history/'sources/v035_endpoint_gaps_N4.json';record=read(raw);require(record['status']=='ACCEPT' and record['N']==4,'unexpected retained v035 endpoint record');bind(raw)
    lower=next(c for c in record['comparisons'] if c['gap_index']==0)
    # Search scope is explicit: paths in the preserved repository, not arbitrary
    # unopened ZIP members or external storage. A string hit is not attribution.
    euler_json_hits=[];named_stdout=[]
    for name in preserved:
        p=safe(REPO,name)
        if p.suffix=='.json' and '"euler"' in p.read_text():euler_json_hits.append(name)
        if p.suffix=='.txt' and any(s in p.name.lower() for s in ['baseline','scalar','euler','nodewind']):named_stdout.append(name)
    return dict(schema=1,status='BOUNDED_ATTRIBUTION_COMPLETE',rows=rows,sources=sources,
      retained_v035_endpoint=dict(path=raw.relative_to(REPO).as_posix(),sha256=sha(raw),lower_gap=lower['observed_min_meV'],environment=record['environment'],provenance_engine_checks=checks,limit='A saved endpoint replay record; no original Euler run record is inferred from it.'),
      search=dict(scope='preserved repository manifest paths only',euler_key_json_hits=euler_json_hits,baseline_scalar_euler_nodewind_stdout_names=named_stdout),
      limits=['Retained snapshots need not be the exact source present when an early log was written.','No original v023 execution timestamp/source/runtime binding was recovered. v034 declares different Python/NumPy/SciPy versions; retained v035 endpoint direct versions match this session but do not specify its full native build.','Log text and code presence do not prove execution or scientific correctness.','Sibling exploratory drivers and arbitrary ZIP contents were not comprehensively traced. No claim that every historical consumer or conclusion is cleared.'])

if __name__=='__main__':
    r=build();write(ROOT/'results/attribution.json',r);print('attributed rows',len(r['rows']),'bound sources',len(r['sources']))
