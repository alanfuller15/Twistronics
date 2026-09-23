"""Run only PLAN.json's frozen finite-model checks. Keep every attempted result."""
import argparse
import gzip
import hashlib
import inspect
import json
import platform
from pathlib import Path
import time
import numpy as np
import scipy
from threadpoolctl import threadpool_limits, threadpool_info
from response_inputs import ROOT, activate
INPUT = activate()
import guarded_topology as gt
import guarded_sparse as gs
from bm_strain import BM, sz
from knobs import add_harmonic


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, obj): Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')


def run(output, smoke=False):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    plan = json.loads((ROOT/'PLAN.json').read_text()); p = gt.Policy(**plan['policy'])
    models = {}; outcomes = []; geometries = {}; checks = []
    sources = {x.name: sha(x) for x in sorted(ROOT.glob('*.py'))}
    environment = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, threadpools=threadpool_info())
    start = time.perf_counter()
    def model(name, B=None, extra=None, **kw):
        args = {k: v.default for k, v in inspect.signature(BM).parameters.items()}
        args.update(kw)
        provisional = BM(**args)
        idx = gs.validate_indices(provisional.idx)
        args['index_set'] = idx
        m = gs.fixed_bm(idx, **{k: v for k, v in args.items() if k != 'index_set'})
        harms = []
        if B is not None:
            add_harmonic(m, B, mat=sz, use_sin=True)
            harms.append(dict(amplitude=B, matrix='sigma_z', use_sin=True, layer_sign=1))
        if extra is not None:
            add_harmonic(m, extra, mat=sz, use_sin=True, layer_sign=-1)
            harms.append(dict(amplitude=extra, matrix='sigma_z', use_sin=True, layer_sign=-1))
        models[name] = dict(parameters=args, harmonics=harms, dimension=m.dim, basis_vectors=m.nG,
                            ordered_basis_sha256=hashlib.sha256(json.dumps(idx, separators=(',', ':')).encode()).hexdigest(),
                            native_source_sha256=sha(INPUT/'bm_strain.py'))
        return m

    def checkpoint():
        write(output/'RESULTS.json', dict(plan_sha256=sha(ROOT/'PLAN.json'), sources=sources, input_archive_sha256=sha(ROOT/'partner_v074p.zip'),
              smoke=smoke, outcomes=outcomes, checks=checks, elapsed_seconds=time.perf_counter()-start, environment=environment))
        write(output/'MODELS.json', models)

    with gzip.open(output/'EVALUATIONS.jsonl.gz', 'wt') as log:
        def retain(records, attempt):
            for row in records:
                log.write(json.dumps(dict(attempt_id=attempt, **row), allow_nan=False)+'\n')
            log.flush()

        def attempt(name, m, call, metadata):
            S = gt.Sampler(m, p, name=metadata['model'])
            t = time.perf_counter()
            try:
                result = call(S)
            except gt.Rejected as ex:
                result = ex.record
            except Exception as ex:
                result = dict(status='ERROR', error_type=type(ex).__name__, message=str(ex))
            frames = [r for r in S.records if r['kind'] == 'frame']
            links = [r for r in S.records if r['kind'] == 'link']
            ext = [r['external_gap_meV'] for r in frames if r['external_gap_meV'] is not None]
            sew = [r['sewing_loss'] for r in links if r['sewing']]
            diag = dict(frame_evaluations=len(frames), link_evaluations=len(links),
                        min_external_gap_meV=min(ext) if ext else None,
                        min_overlap=min(r['min_overlap'] for r in links) if links else None,
                        max_endpoint_sewing_loss=max(sew) if sew else None,
                        max_reality_meV=max(r['reality_meV'] for r in frames) if frames else None)
            retain(S.records, name)
            outcomes.append(dict(id=name, **metadata, result=result, diagnostics=diag, elapsed_seconds=time.perf_counter()-t))
            checkpoint()
            print(name, result['status'], result.get('label', result.get('code', result.get('euler_estimate', result.get('sign')))), flush=True)
            return result

        seeds = json.loads((INPUT/'VALLEY_MIRROR.json').read_text())
        for B in plan['braid']['B'][:1] if smoke else plan['braid']['B']:
            pair = {}
            for valley in (1, -1):
                name = f'braid_B{B}_v{valley}'
                pair[valley] = model(name, N=4, eps=.003, phi_deg=0, A_scalar=.2, kinetic='lab_nn_full', geometry='exact', valley=valley, B=B)
            nodes = seeds[f'braid_{B}']['K']['nodes']
            for radius in plan['braid']['radii'][:1] if smoke else plan['braid']['radii']:
                for n, nt in plan['braid']['meshes'][:1] if smoke else plan['braid']['meshes']:
                    key = f'B{B}_r{radius}_n{n}_t{nt}'
                    g = gt.geometry(nodes, radius, n, nt); gm = gt.mirror(g)
                    geometries[key] = dict(K=g, Kprime=gm, seed_source='original/VALLEY_MIRROR.json', root_action='evaluate both native roots without relocation')
                    tr = []
                    points = np.concatenate([np.asarray(g['nodes']), np.asarray(g['transport']), *[np.asarray(x) for x in g['loops']]])
                    for j, f in enumerate(points):
                        h = pair[1].H(pair[1].frac_to_k(f)); hp = pair[-1].H(pair[-1].frac_to_k(-f))
                        error = float(np.max(np.abs(hp-h.conj())))
                        tr.append(dict(kind='native_time_reversal', sample=j, f_K=f.tolist(), f_Kprime=(-f).tolist(), matrix_error_meV=error))
                    retain(tr, 'TR_'+key)
                    mx = max(x['matrix_error_meV'] for x in tr)
                    checks.append(dict(kind='native_time_reversal', id=key, samples=len(tr), max_matrix_error_meV=mx, passed=mx <= plan['braid']['matrix_TR_tol_meV']))
                    res = []
                    for valley, geometry in [(1, g), (-1, gm)]:
                        res.append(attempt(f'pair_{key}_v{valley}', pair[valley], lambda S, geometry=geometry: gt.pair_charges(S, geometry),
                                   dict(kind='pair', model=f'braid_B{B}_v{valley}', B=B, valley=valley, radius=radius, loop_intervals=n, transport_intervals=nt, geometry_id=key)))
                    passed = all(r['status'] == 'PASSED_SAMPLED_GATES' for r in res)
                    diff = max(abs(abs(a)-abs(b)) for a, b in zip(res[0]['windings'], res[1]['windings'])) if passed else None
                    checks.append(dict(kind='mirror_labels', id=key, comparable=passed, abs_winding_difference=diff,
                                       passed=bool(passed and res[0]['label'] == res[1]['label'] and diff <= plan['braid']['paired_abs_winding_tol'])))

        if not smoke:
            for valley in plan['wilson']['valleys']:
                name = f'baseline_v{valley}'
                m = model(name, N=4, eps=.003, phi_deg=0, kinetic='lab_nn_full', geometry='exact', valley=valley)
                for n1, n2 in plan['wilson']['meshes']:
                    attempt(f'wilson_{name}_{n1}x{n2}', m, lambda S, a=n1, b=n2: gt.euler_wilson(S, nf1=a, nf2=b), dict(kind='wilson', model=name, valley=valley, mesh=[n1, n2]))
            m = model('chiral_N6', N=6, theta_deg=1.06, ratio=0., eps=0., kinetic='none')
            for n1, n2 in plan['wilson']['chiral_meshes']:
                attempt(f'wilson_chiral_{n1}x{n2}', m, lambda S, a=n1, b=n2: gt.euler_wilson(S, nf1=a, nf2=b), dict(kind='wilson', model='chiral_N6', valley=1, mesh=[n1, n2]))
            for valley in plan['sign']['valleys']:
                name = f'endpoint_v{valley}'
                m = model(name, N=4, eps=.003, phi_deg=80, A_scalar=-.30, ratio=.88, kinetic='lab_nn_full', geometry='exact', valley=valley, B=-.40, extra=-1.8)
                for label, band in [('flat1', m.dim//2-1), ('flat2', m.dim//2)]:
                    for axis in plan['sign']['axes']:
                        for n in plan['sign']['intervals']:
                            attempt(f'sign_{name}_{label}_a{axis}_n{n}', m, lambda S, b=band, a=axis, n=n: gt.band_sign_holonomy(S, b, a, 0., n=n), dict(kind='sign', model=name, valley=valley, band=band, band_label=label, axis=axis, intervals=n))

        sp = plan['sparse']
        for valley in sp['valleys'][:1] if smoke else sp['valleys']:
            name = f'sparse_v{valley}'
            m = model(name, N=sp['N'], eps=.003, kinetic='lab_nn_full', geometry='exact', valley=valley)
            ledger = gs.Ledger(); C = gs.CheckedSparse(m, m.idx, sp, ledger)
            for f in sp['points'][:1] if smoke else sp['points']:
                for sigma in sp['sigma']:
                    key = f'{name}_f{f}_sigma{sigma}'; lo = m.dim//2-3
                    try:
                        w, _ = C.window(f, lo, sp['n'], sigma=sigma, request_k=sp['request_k'])
                        result = dict(status='ACCEPTED_DENSE_CHECKED', energies_meV=w.tolist())
                    except gt.Rejected as ex: result = ex.record
                    outcomes.append(dict(id=key, kind='sparse', model=name, valley=valley, f=f, sigma=sigma, lo=lo, result=result))
                    print(key, result['status'], result.get('code', ''), flush=True)
            retain(ledger.entries, name)
            checks.append(dict(kind='sparse_work_counts', model=name, component_counts=ledger.counts(),
                               attempts=len([r for r in ledger.entries if r['kind'] == 'attempt']),
                               accounting='Components are disjoint. Inclusive attempt wall times are not added to component times.'))
        checkpoint()
    with gzip.open(output/'PATHS.json.gz', 'wt') as f:
        json.dump(geometries, f, allow_nan=False)
    checkpoint()
    if any(r['result']['status'] == 'ERROR' for r in outcomes):
        raise RuntimeError('Unexpected errors retained; inspect RESULTS.json')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default=str(ROOT)); ap.add_argument('--smoke', action='store_true'); args = ap.parse_args()
    with threadpool_limits(limits=1): run(args.output, args.smoke)
