"""Independent retained-byte, shell, geometry and loop-product review; no solves.

Usage: retained_review.py MATERIALIZED_021 SOURCE_021 OUTPUT.json
The pack decoder and all product calculations below do not call producer helpers.
"""
import base64
import hashlib
import io
import json
import math
import struct
import subprocess
import sys
import tarfile
import zlib
from fractions import Fraction as F
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / 'research/benchmarks'
COMMITS = {'022': ('4e0e6c4378609189a4fafc0c25ba06a0ac68bb81', '75d9d5806d65ba81a37b5b109a36d489d3c34096'),
           '023': ('99c0c4ee6845fb6b637dc11c670f684129c20436', '6394c414dee22421b370a312d80bbc03c3bae168')}
NAMES = {'022': 'controls_e_022', '023': 'cutoff_f_023'}
GROUPS = {'lo_minus_1': [0], 'lo': [1], 'hi': [2], 'hi_plus_1': [3], 'selected_pair': [1, 2], 'four': [0, 1, 2, 3]}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    return json.loads(Path(p).read_bytes())


def unpack(p):
    blob = Path(p).read_bytes()
    magic, body = blob.split(b'\n', 1)
    assert magic == b'twistronics-states-v1'
    length = int.from_bytes(body[:8], 'little')
    header = json.loads(body[8:8 + length])
    assert header['format'] == magic.decode()
    pos, arrays = 8 + length, {}
    for item in header['arrays']:
        assert item['dtype'] == '<f8' and item['name'] not in arrays
        count = math.prod(item['shape'])
        planes = zlib.decompress(body[pos:pos + item['bytes']])
        pos += item['bytes']
        assert len(planes) == count * 8
        raw = bytearray(count * 8)
        for j in range(8):
            raw[j::8] = planes[j * count:(j + 1) * count]
        assert sha(raw) == item['raw_sha256']
        arrays[item['name']] = np.frombuffer(raw, dtype='<f8').reshape(item['shape']).copy()
    assert pos == len(body)
    return arrays


def manifest(directory):
    m = read(directory / 'MANIFEST.json')
    for name, item in m['files'].items():
        b = (directory / name).read_bytes()
        assert sha(b) == item['sha256'] and len(b) == item['bytes'], name
    present = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert present - {'MANIFEST.json', 'check_replay.py', 'README.md'} == set(m['files'])
    return m


def archive_arrays(directory):
    """Read historical text-transport archive without rewriting or invoking replay."""
    m = read(directory / 'MANIFEST.json')
    chunks = []
    for part in m['parts']:
        raw = base64.b64decode((directory / part['path']).read_bytes(), validate=True)
        assert sha(raw) == part['decoded_sha256']
        chunks.append(raw)
    raw = b''.join(chunks)
    assert sha(raw) == m['archive_sha256']
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as t:
        files = {p.name: t.extractfile(p).read() for p in t.getmembers() if p.isfile()}
    assert set(files) == set(m['files'])
    for name, item in m['files'].items():
        assert sha(files[name]) == item['sha256'] and len(files[name]) == item['bytes']
    out = {}
    for name in sorted(files):
        if name.endswith('/SAMPLES.json'):
            z = np.load(io.BytesIO(files[name.replace('SAMPLES.json', 'STATES.npz')]), allow_pickle=False)
            for r, row in enumerate(json.loads(files[name])):
                out[tuple(row['center'])] = {k: z[k][r] for k in z.files}
    return out, len(m['files'])


def jobs(directory, cfg, keys):
    out, rows = {}, {}
    for j, owned in enumerate(cfg['jobs']):
        d = directory / f'job{j:03}'
        z = unpack(d / 'STATES.pack') if (d / 'STATES.pack').exists() else dict(np.load(d / 'STATES.npz', allow_pickle=False))
        saved = read(d / 'SAMPLES.json')
        assert [r['index'] for r in saved] == owned
        for local, row in enumerate(saved):
            i = row['index']
            assert row['center'] == cfg['points'][i] and i not in rows
            rows[i] = row
            out[i] = {k: (z[k + '_energies'][local], z[k + '_vectors'][local]) for k in keys}
    assert sorted(rows) == list(range(len(cfg['points'])))
    return out, rows


def geometry(cfg):
    assert len(set(map(tuple, cfg['points']))) == len(cfg['points'])
    assert sum(cfg['jobs'], []) == list(range(len(cfg['points'])))
    for loop in cfg['loops']:
        cx, cy = map(F, loop['center']); h = F(loop['half_width']); n = loop['points_per_side']
        expected = []
        for side in range(4):
            for j in range(n):
                u = F(j, n)
                dx, dy = [(-h + 2*h*u, -h), (h, -h + 2*h*u), (h - 2*h*u, h), (-h, h - 2*h*u)][side]
                expected.append([str(cx + dx), str(cy + dy)])
        assert [cfg['points'][i] for i in loop['point_indices']] == expected


def shells():
    case = read(ROOT / 'docs/certification-readiness/CASE.json')
    shells = dict(case['cutoffs'])
    for left, right, specpath, field in [
        ('b', 'c', BENCH / 'cutoff_ladder_003/SPEC.json', 'additional_cutoff'),
        ('c', 'd', BENCH / 'cutoff_shell_012/SPEC.json', 'additional_cutoff'),
        ('d', 'e', BENCH / 'controls_e_022/SPEC.json', 'additional_cutoff_e'),
        ('e', 'f', BENCH / 'cutoff_f_023/SPEC.json', 'additional_cutoff_f')]:
        nodes = sorted(set((x + a, y + b) for x, y in shells[left]['ordered_indices'] for a, b in shells['b']['stencil']))
        declared = read(specpath)[field]
        assert nodes == list(map(tuple, declared['ordered_indices']))
        assert declared['dimension'] == 4 * len(nodes)
        assert declared['selected_bands_zero_based'] == [2*len(nodes)-1, 2*len(nodes)]
        assert set(map(tuple, shells[left]['ordered_indices'])) <= set(nodes)
        shells[right] = declared
    return shells


def loop_products(cfg, data, retained, cutoffs):
    report, max_errors = [], {'raw_determinant': 0., 'log_abs_determinant': 0., 'min_step_singular_value': 0., 'minimum_sampled_external_gap_meV': 0., 'polar_determinant': 0.}
    for loop in cfg['loops']:
        idx = loop['point_indices']
        for k in data[idx[0]]:
            lo, hi = cutoffs[k]['selected_bands_zero_based']
            for group, cols in GROUPS.items():
                frames = [data[i][k][1][:, cols] for i in idx]
                dets, sigmas, polars = [], [], []
                for a, b in zip(frames, frames[1:] + frames[:1]):
                    overlap = a.T @ b
                    dets.append(float(np.linalg.det(overlap)))
                    u, s, vt = np.linalg.svd(overlap)
                    sigmas.append(float(s[-1])); polars.append(u @ vt)
                raw = math.prod(dets)
                sign = 1 if raw > 0 else -1 if raw < 0 else 0
                minimum = min(sigmas)
                p = np.eye(len(cols))
                for q in polars: p = p @ q
                bands = [lo - 1 + c for c in cols]
                gap = min(min(data[i][k][0][bands[0]] - data[i][k][0][bands[0]-1], data[i][k][0][bands[-1]+1] - data[i][k][0][bands[-1]]) for i in idx)
                measured = {'raw_determinant': raw, 'log_abs_determinant': math.fsum(math.log(abs(d)) for d in dets), 'min_step_singular_value': minimum, 'minimum_sampled_external_gap_meV': float(gap), 'polar_determinant': float(np.linalg.det(p))}
                r = retained['loops'][loop['id']]['cutoffs'][k][group]
                valid = minimum >= cfg['holonomy']['min_step_overlap'] and sign != 0
                assert valid == r['valid'] and (sign if valid else None) == r['sign']
                rev = frames[::-1]
                reverse = math.prod(float(np.linalg.det(a.T @ b)) for a,b in zip(rev, rev[1:] + rev[:1]))
                assert int(np.sign(reverse)) == sign == r['reverse_sign']
                assert bands == r['bands_zero_based']
                for field, value in measured.items():
                    error = abs(value - r[field]); max_errors[field] = max(max_errors[field], error)
                    assert error < 1e-11, (loop['id'], k, group, field, error)
                translated = 'offnode' in loop['id'] or 'translated' in loop['id']
                negative = ('hi', 'hi_plus_1', 'selected_pair') if loop['id'].startswith(('R3_', 'R1_')) else ('lo_minus_1', 'lo', 'selected_pair')
                assert sign == (-1 if not translated and group in negative else 1)
                report.append({'loop': loop['id'], 'cutoff': k, 'group': group, 'sign': sign, **measured})
    return {'products': len(report), 'max_abs_errors_vs_retained': max_errors, 'minimum_link_sigma': min(r['min_step_singular_value'] for r in report), 'rows': report}


def main():
    source021, materialized021 = Path(sys.argv[2]), Path(sys.argv[1])
    cfg = {tag: read(BENCH / name / 'SPEC.json') for tag, name in NAMES.items()}
    manifests, data, rows = {}, {}, {}
    evidence = {'physical_eigensolves': 0, 'source_freezes': {}, 'files': {}, 'cutoffs': {}}
    for tag, name in NAMES.items():
        implementation, execution = COMMITS[tag]
        for path, digest in cfg[tag]['dependencies'].items():
            assert sha((ROOT/path).read_bytes()) == digest
        for path in [f'research/benchmarks/{name}/run.py', f'research/benchmarks/{name}/SPEC.json', *cfg[tag]['dependencies']]:
            b = (ROOT/path).read_bytes()
            assert b == subprocess.check_output(['git','show',implementation+':'+path],cwd=ROOT)
            assert b == subprocess.check_output(['git','show',execution+':'+path],cwd=ROOT)
        geometry(cfg[tag])
        directory = BENCH / (name + '_execution')
        m = manifest(directory); assert m['implementation_commit'] == implementation
        manifests[tag] = m; evidence['files'][tag] = len(m['files'])
        data[tag], rows[tag] = jobs(directory, cfg[tag], 'cde' if tag == '022' else 'f')
        batch = read(directory/'BATCH.json')
        assert batch['wall_seconds'] <= cfg[tag]['limits']['batch_timeout_seconds'] and batch['concurrent_workers'] == 4
        for j in range(len(cfg[tag]['jobs'])):
            receipt = read(directory/f'job{j:03}'/'RECEIPT.json')
            assert receipt['termination'] == 'NORMAL_EXIT' and receipt['exit_code'] == 0 and receipt['process_group_empty']
            assert receipt['elapsed_seconds'] <= 90
            runtime = read(directory/f'job{j:03}'/'RUNTIME.json')
            assert runtime['mapped_native_libraries_bound_to_wheel'] and runtime['loaded_extension_bound_to_wheel']
            assert runtime['limits'] == cfg[tag]['limits'] and set(runtime['threads'].values()) == {'1'}
        evidence['source_freezes'][tag] = {'implementation': implementation, 'execution': execution, 'dependencies': len(cfg[tag]['dependencies'])}
    case = shells()
    evidence['cutoffs'] = {k: {'vectors': len(v['ordered_indices']), 'dimension': v['dimension'], 'pair': v['selected_bands_zero_based']} for k,v in case.items()}
    m021path = source021/'research/benchmarks/lower_controls_021_execution/MANIFEST.json'
    m021 = read(m021path); s021 = read(source021/'research/benchmarks/lower_controls_021/SPEC.json')
    for path, item in m021['files'].items():
        b = (materialized021/path).read_bytes(); assert sha(b) == item['sha256'] and len(b) == item['bytes']
    d021, _ = jobs(materialized021, s021, 'e')
    reuse = cfg['023']['reuse']; assert sha(m021path.read_bytes()) == reuse['sources']['021']['manifest_sha256']
    assert reuse['sources']['021']['manifest_commit'] == '38204bfc987108e60d7e2c1b9561fdd0fe3c6057'
    assert cfg['023']['points'] == cfg['022']['points'] + s021['points']
    assert cfg['023']['labels'] == cfg['022']['labels'] + s021['labels']
    for tag, src in reuse['sources'].items():
        expected = m021 if tag == '021' else manifests['022']
        root = materialized021 if tag == '021' else BENCH/'controls_e_022_execution'
        for path, digest in src['files'].items():
            assert digest == expected['files'][path]['sha256'] == sha((root/path).read_bytes())
    mapped = {}
    for tag, spec in [('022', cfg['022']), ('021', s021)]:
        offset = 0 if tag == '022' else 192
        for j, owned in enumerate(spec['jobs']):
            for local, i in enumerate(owned): mapped[str(i+offset)] = [tag, f'job{j:03}', local]
    assert mapped == reuse['point_source']
    expected_regression = [i for loop in cfg['023']['loops'] if loop['id'] in ('R3_r1_32', 'R2_baseline') for i in loop['point_indices']]
    assert expected_regression == reuse['regression_points'] and len(expected_regression) == 64
    for i in range(384):
        data['023'][i]['e'] = data['022'][i]['e'] if i < 192 else d021[i-192]['e']
        assert rows['023'][i]['reuse'] == ({'e_resolved_bit_identical': True} if i in expected_regression else {})
    evidence['reuse'] = {'sha256_bound_files': sum(len(s['files']) for s in reuse['sources'].values()), 'points': 384, 'regression_assertion_flags': len(expected_regression), 'manifest021_files_verified': len(m021['files'])}
    old013, _ = jobs(BENCH/'loop_cutoff_d_013_execution', read(BENCH/'loop_cutoff_d_013/SPEC.json'), 'cd')
    old015, _ = jobs(BENCH/'cutoff_e_015_execution', read(BENCH/'cutoff_e_015/SPEC.json'), 'e')
    old016, files016 = archive_arrays(source021/'research/benchmarks/r1_cutoff_e_016_execution')
    keyed015 = {tuple(p): old015[i]['e'] for i,p in enumerate(read(BENCH/'cutoff_e_015/SPEC.json')['points'])}
    arrays, gaps = 0, 0
    for i, p in enumerate(cfg['022']['points']):
        for k in 'cd':
            for a,b in zip(data['022'][i][k], old013[i][k]): assert a.tobytes() == b.tobytes(); arrays += 1
        if tuple(p) in keyed015:
            for a,b in zip(data['022'][i]['e'], keyed015[tuple(p)]): assert a.tobytes() == b.tobytes(); arrays += 1
        if tuple(p) in old016:
            for kind,a in zip(('e_energies','e_vectors'),data['022'][i]['e']): assert a.tobytes() == old016[tuple(p)][kind].tobytes(); arrays += 1
    for side, field in enumerate(('lower_gap_meV','upper_gap_meV')):
        for k, refs in cfg['022']['regression'][field].items():
            lo,hi = case[k]['selected_bands_zero_based']
            for i, expected in refs.items():
                E = data['022'][int(i)][k][0]
                actual = E[lo]-E[lo-1] if side == 0 else E[hi+1]-E[hi]
                assert actual == expected; gaps += 1
    assert arrays == gaps == 896
    evidence['022_history'] = {'bit_identical_arrays': arrays, 'bit_identical_gap_values': gaps, '016_archive_files_verified': files016}
    evidence['loops'] = {tag: loop_products(cfg[tag], data[tag], read(BENCH/(NAMES[tag]+'_execution')/'HOLONOMY.json'), case) for tag in NAMES}
    deltas = []
    for i in range(384):
        gaps = {}
        for k in 'ef':
            E = data['023'][i][k][0];lo,hi = case[k]['selected_bands_zero_based']
            gaps[k] = np.array([E[lo]-E[lo-1],E[hi+1]-E[hi]])
        deltas.append(abs(gaps['f']-gaps['e']))
    evidence['ef_max_abs_gap_change_meV'] = np.max(deltas,axis=0).tolist()
    evidence['status'] = 'RETAINED_CHECKS_PASS_NOT_A_PHYSICAL_RECOMPUTE'
    Path(sys.argv[3]).write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in evidence.items() if k != 'loops'}))
    print(json.dumps({'loop_products': {k:v['products'] for k,v in evidence['loops'].items()}}))


if __name__ == '__main__':
    main()
