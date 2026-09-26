#!/usr/bin/env python3
"""Batch 006: depth-10 refinement restricted to cells left unresolved at depth 9."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'research/benchmarks/certification_s1b_quadrant_a_002'
sys.path.insert(0, str(OLD))
import common as durable
SPEC = HERE / 'SPEC.json'
MANIFEST = HERE / 'SOURCE_BINDINGS.json'
QUADRANTS = ('q00', 'q01', 'q10', 'q11')
PREDECESSOR = ROOT / 'research/benchmarks/parallel_domain_005_execution/PARTITION.json'
ACCEPT = 'CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def spec_and_bindings():
    for name, digest in json.loads(MANIFEST.read_text()).items():
        require(durable.sha256_file(ROOT / name) == digest, 'SOURCE_MISMATCH:' + name)
    return json.loads(SPEC.read_text())


def shard_names(spec, host=None):
    hosts = range(spec['hosts']) if host is None else [host]
    return [f'{q}h{h}' for h in hosts for q in QUADRANTS]


def split_shard(shard, spec):
    require(len(shard) == 5 and shard[:3] in QUADRANTS and shard[3] == 'h', 'SHARD_NAME')
    h = int(shard[4])
    require(0 <= h < spec['hosts'], 'SHARD_HOST')
    return shard[:3], h


def predecessor_quadrant(q):
    """Union of every predecessor shard state belonging to quadrant q."""
    merged = {'accepted': [], 'unresolved': [], 'frontier': []}
    for name, state in json.loads(PREDECESSOR.read_text()).items():
        if name[:3] == q:
            for key in merged:
                merged[key].extend(state[key])
    return merged


def initial(shard, spec):
    """Deterministic disjoint ownership.

    The predecessor frontier of each quadrant is sorted ascending and dealt
    round-robin to hosts: host h owns sorted positions i with i % hosts == h,
    and every descendant of an owned cell stays with that owner. Inherited
    accepted and unresolved cells belong to host 0 only, so the union of all
    shards is exactly the predecessor partition before any attempt.
    """
    q, h = split_shard(shard, spec)
    p = predecessor_quadrant(q)
    # Restricted refinement: the predecessor must be settled (no frontier), and
    # only its depth-9 unresolved cells are reopened, as their four depth-10
    # children. Nothing else is refined; accepted cells are inherited.
    require(not p['frontier'], 'PREDECESSOR_FRONTIER_NOT_EMPTY')
    require(all(c[0] == spec['refine_from_depth'] for c in p['unresolved']), 'UNRESOLVED_DEPTH')
    frontier = sorted(child for c in p['unresolved'] for child in durable.children(tuple(c)))
    return {'accepted': [tuple(c) for c in p['accepted']] if h == 0 else [],
            'unresolved': [],
            'frontier': [c for i, c in enumerate(frontier) if i % spec['hosts'] == h]}


def validate_partition(states, spec, max_depth=None):
    max_depth = spec['max_depth'] if max_depth is None else max_depth
    require(set(states) == set(shard_names(spec)), 'SHARD_SET')
    side = 1 << max_depth
    raster = bytearray(side * side)
    for q, state in states.items():
        quadrant, _ = split_shard(q, spec)
        qx, qy = int(quadrant[1]), int(quadrant[2])
        require(set(state) == {'accepted', 'unresolved', 'frontier'}, 'PARTITION_KEYS')
        for cells in state.values():
            for d, ix, iy in cells:
                require(type(d) is int and type(ix) is int and type(iy) is int, 'CELL_TYPES')
                require(1 <= d <= max_depth, 'CELL_DEPTH')
                require(ix >> (d-1) == qx and iy >> (d-1) == qy, 'CELL_OUTSIDE_ASSIGNED_QUADRANT')
                scale = 1 << (max_depth-d)
                for x in range(ix*scale, (ix+1)*scale):
                    for y in range(iy*scale, (iy+1)*scale):
                        i = x*side+y
                        require(raster[i] == 0, 'PARTITION_OVERLAP')
                        raster[i] = 1
    require(all(raster), 'PARTITION_GAP')


def area(cells):
    return sum((Fraction(1, 4**d) for d, _, _ in cells), Fraction())


def transition(state, cell, outcome, max_depth):
    require(state['frontier'] and min(state['frontier']) == cell, 'QUEUE_ORDER')
    state['frontier'].remove(cell)
    if outcome == ACCEPT:
        state['accepted'].append(cell)
    else:
        require(outcome == 'INCONCLUSIVE', 'OUTCOME')
        if cell[0] == max_depth:
            state['unresolved'].append(cell)
        else:
            require(cell[0] < max_depth, 'DEPTH_CAP')
            state['frontier'].extend(durable.children(cell))


def header(q, implementation, synthetic, provenance):
    return {'kind': 'header', 'sequence': -1, 'previous_record_sha256': None,
            'packet': 'PARALLEL-DOMAIN-006', 'shard': q,
            'implementation_commit': implementation, 'test_mode': synthetic,
            'source_bindings_sha256': durable.sha256_file(MANIFEST),
            'runtime_provenance': provenance,
            'runtime_provenance_digest': durable.sha256_bytes(durable.canonical_object_bytes(provenance))}


def worker(args):
    spec = spec_and_bindings()
    resource.setrlimit(resource.RLIMIT_AS, (spec['address_space_bytes_per_worker'],)*2)
    state = initial(args.shard, spec)
    if args.synthetic:
        evaluator = None
        provenance = {'synthetic': True}
    else:
        # Precision is set before coefficient assembly as well as every cell.
        from flint import ctx
        ctx.prec = 128
        ctx.threads = 1
        old_worker = load(OLD / 'worker.py', 'parallel_old_worker')
        evaluator = old_worker.PhysicalEvaluator(args.wheel, spec)
        provenance = evaluator.runtime_provenance
    log = args.output / 'ATTEMPTS.ndjson'
    _, line, previous = durable.hashed_record(header(args.shard, args.implementation_commit,
                                                    args.synthetic, provenance))
    durable.append_durable(log, line)
    for sequence in range(spec['max_attempts_per_worker']):
        if not state['frontier']:
            break
        cell = min(state['frontier'])
        if args.synthetic:
            outcome = ACCEPT if (cell[1]+cell[2]) % 3 else 'INCONCLUSIVE'
            evaluated = {'outcome': outcome, 'primary_factorizations': 0,
                         'recomputation_factorizations': 0,
                         'full_interval_evidence': {'synthetic': True}}
        else:
            evaluated = evaluator(cell, spec)
        unsigned = {'kind': 'attempt', 'sequence': sequence,
                    'previous_record_sha256': previous,
                    'cell': durable.cell_ref(cell), **evaluated}
        record, line, digest = durable.hashed_record(unsigned)
        if args.fault == 'partial' and sequence == 0:
            require(args.synthetic, 'FAULT_REQUIRES_SYNTHETIC')
            durable.append_durable(log, line[:len(line)//2])
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            (args.output / 'FAULT_READY').write_text('ready')
            while True:
                time.sleep(1)
        durable.append_durable(log, line)
        transition(state, cell, record['outcome'], spec['max_depth'])
        previous = digest


def empty_group(pid):
    try:
        os.killpg(pid, 0)
    except ProcessLookupError:
        return True
    return False


def supervise(args):
    spec = spec_and_bindings()
    if not args.synthetic:
        authority = json.loads((HERE / 'EXECUTION_AUTHORITY.json').read_text())
        require(authority['mode'] == 'USER_DIRECTED_ASYNC_AUDIT' and
                authority['audit_acceptance_blocks_execution'] is False, 'AUTHORITY_BINDING')
        require(args.wheel is not None, 'WHEEL_REQUIRED')
    require(args.host is not None and 0 <= args.host < spec['hosts'], 'HOST_REQUIRED')
    require(not args.output.exists(), 'OUTPUT_EXISTS')
    args.output.mkdir(parents=True)
    env = dict(os.environ)
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               BLIS_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    live = []
    try:
        for q in shard_names(spec, args.host):
            out = args.output / q
            out.mkdir()
            cmd = [sys.executable, '-B', str(Path(__file__).resolve()), 'worker',
                   '--output', str(out), '--shard', q,
                   '--implementation-commit', args.implementation_commit]
            if args.synthetic:
                cmd += ['--synthetic', '--fault', args.fault]
            else:
                cmd += ['--wheel', str(args.wheel.resolve())]
            stream = (out / 'WORKER.log').open('wb')
            p = subprocess.Popen(cmd, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            started = time.monotonic()
            soft = spec['worker_wall_seconds'] if not args.synthetic else (2 if args.fault == 'partial' else 30)
            grace = spec['grace_seconds'] if not args.synthetic else 1
            live.append(dict(q=q, process=p, stream=stream, start=started,
                             soft_deadline=started+soft, hard_deadline=started+soft+grace,
                             term=None, kill=None, reaped=None))
        while any(item['reaped'] is None for item in live):
            now = time.monotonic()
            for item in live:
                if item['reaped'] is not None:
                    continue
                p = item['process']
                if p.poll() is not None:
                    p.wait()
                    item['reaped'] = time.monotonic()
                    item['stream'].close()
                    continue
                if now >= item['soft_deadline'] and item['term'] is None:
                    os.killpg(p.pid, signal.SIGTERM)
                    item['term'] = time.monotonic()
                if now >= item['hard_deadline'] and item['kill'] is None:
                    os.killpg(p.pid, signal.SIGKILL)
                    item['kill'] = time.monotonic()
            time.sleep(.05)
        for item in live:
            p = item['process']
            require(empty_group(p.pid), 'WORKER_GROUP_NOT_EMPTY')
            out = args.output / item['q']
            log = out / 'ATTEMPTS.ndjson'
            raw = log.read_bytes() if log.exists() else b''
            trimmed = raw if raw.endswith(b'\n') else raw[:raw.rfind(b'\n')+1]
            if trimmed != raw:
                with log.open('wb') as stream:
                    stream.write(trimmed); stream.flush(); os.fsync(stream.fileno())
                durable.fsync_directory(out)
            reason = ('WATCHDOG_TIMEOUT' if item['term'] or item['kill'] else
                      'NORMAL_EXIT' if p.returncode == 0 else 'EXECUTION_ERROR')
            receipt = {k: v for k, v in item.items() if k not in ('process', 'stream')}
            receipt.update(implementation_commit=args.implementation_commit,
                           test_mode=args.synthetic, termination_reason=reason,
                           exit_code=p.returncode, group_empty=True,
                           raw_bytes=len(raw), durable_bytes=len(trimmed),
                           log_sha256=hashlib.sha256(trimmed).hexdigest(),
                           worker_log_sha256=durable.sha256_file(out / 'WORKER.log'),
                           execution_authority=(None if args.synthetic else authority))
            durable.atomic_json(out / 'RECEIPT.json', receipt)
    finally:
        for item in live:
            p = item['process']
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
            if not item['stream'].closed:
                item['stream'].close()
    return verify(args.output, args.implementation_commit, args.synthetic, write=True, host=args.host)


def strict_evidence(evidence, outcome, spec, cell, old_verify):
    require(evidence['status'] == outcome, 'EVIDENCE_STATUS')
    for definition in evidence['window_definitions'].values():
        require(Fraction(definition['right']) - Fraction(definition['left']) ==
                Fraction(definition['width_meV']), 'WINDOW_WIDTH_IDENTITY')
    for key in ('primary', 'recomputation'):
        attempt = evidence[key]
        if attempt is None:
            continue
        require(len(attempt['gram_margins']) == 196, 'GRAM_DIMENSION')
        for margin in attempt['gram_margins']:
            require(Fraction(margin[0]) > 0 and Fraction(margin[1]) >= Fraction(margin[0]), 'GRAM_MARGIN')
        for window in attempt['windows'].values():
            require([f['label'] for f in window['endpoints']] == ['left', 'right'], 'ENDPOINT_LABELS')
            for f in window['endpoints']:
                if f['status'] == 'CERTIFIED':
                    require(len(f['pivots']) == 196, 'PIVOT_DIMENSION')
                else:
                    require(f['status'] == 'INCONCLUSIVE' and
                            len(f['pivots']) == f['pivot_index'] + 1 <= 196, 'FAILED_PIVOT_LENGTH')
    return old_verify.verify_physical_evidence(evidence, outcome, spec, cell)


def verify(output, implementation, allow_synthetic=False, write=False, host=None):
    """host=h replays that host's shards only; host=None replays and merges every shard."""
    spec = spec_and_bindings()
    old_verify = load(OLD / 'verify.py', 'parallel_old_verify')
    shards = shard_names(spec, host)
    outputs = {'HOST_RESULTS.json'} if host is not None else {'RESULTS.json', 'PARTITION.json'}
    present = set(p.name for p in output.iterdir())
    require(present == set(shards) | (set() if write else outputs), 'ROOT_FILE_SET')
    states, summaries = {}, {}
    observed_modes = set()
    for q in shards:
        out = output / q
        names = set(p.name for p in out.iterdir())
        expected = {'ATTEMPTS.ndjson', 'RECEIPT.json', 'WORKER.log'}
        if 'FAULT_READY' in names:
            require(allow_synthetic, 'FAULT_ARTIFACT_PHYSICAL')
            expected.add('FAULT_READY')
        require(names == expected, 'WORKER_FILE_SET')
        raw = (out / 'ATTEMPTS.ndjson').read_bytes()
        r = json.loads((out / 'RECEIPT.json').read_text())
        require(r['implementation_commit'] == implementation and r['q'] == q and
                r['group_empty'] is True, 'RECEIPT_IDENTITY')
        require(r['durable_bytes'] == len(raw) <= r['raw_bytes'] and
                r['log_sha256'] == hashlib.sha256(raw).hexdigest(), 'LOG_BINDING')
        require(r['worker_log_sha256'] == durable.sha256_file(out / 'WORKER.log'), 'STDERR_BINDING')
        require(r['start'] <= r['reaped'] and r['soft_deadline'] < r['hard_deadline'], 'CLOCK_ORDER')
        h, records = durable.parse_and_verify_log(out / 'ATTEMPTS.ndjson', allow_test_mode=allow_synthetic)
        synthetic = h.get('test_mode')
        observed_modes.add(synthetic)
        require(type(synthetic) is bool and r['test_mode'] == synthetic, 'MODE_BINDING')
        require(h == {**header(q, implementation, synthetic, h['runtime_provenance']),
                      'record_sha256': h['record_sha256']}, 'HEADER_BINDING')
        old_verify.verify_runtime_provenance(h, test_mode=synthetic)
        if not synthetic:
            require(r['execution_authority'] == json.loads((HERE / 'EXECUTION_AUTHORITY.json').read_text()), 'AUTHORITY_BINDING')
            # Recompute with the supervisor's exact expressions; no float differencing.
            require(r['soft_deadline'] == r['start'] + spec['worker_wall_seconds'] and
                    r['hard_deadline'] == r['start'] + spec['worker_wall_seconds'] + spec['grace_seconds'],
                    'DEADLINE_BINDING')
        reason = r['termination_reason']
        if reason == 'NORMAL_EXIT':
            require(r['exit_code'] == 0 and r['term'] is None and r['kill'] is None, 'NORMAL_RECEIPT')
        elif reason == 'WATCHDOG_TIMEOUT':
            require(r['term'] is not None or r['kill'] is not None, 'TIMEOUT_SIGNAL')
            for field, deadline in [('term', 'soft_deadline'), ('kill', 'hard_deadline')]:
                if r[field] is not None:
                    require(r[deadline] <= r[field] <= r['reaped'], 'SIGNAL_TIME')
            require(r['exit_code'] in (0, -signal.SIGTERM, -signal.SIGKILL), 'TIMEOUT_EXIT')
        else:
            raise RuntimeError('EXECUTION_ERROR:' + q)
        require(len(records) <= spec['max_attempts_per_worker'], 'ATTEMPT_CAP')
        state = initial(q, spec)
        primary = recompute = 0
        for record in records:
            cell = durable.cell_tuple(record['cell'])
            if synthetic:
                require(record['full_interval_evidence'] == {'synthetic': True}, 'SYNTHETIC_EVIDENCE')
                require(record['outcome'] == (ACCEPT if (cell[1]+cell[2]) % 3 else 'INCONCLUSIVE'), 'SYNTHETIC_OUTCOME')
                counts = (0, 0)
            else:
                counts = strict_evidence(record['full_interval_evidence'], record['outcome'], spec, cell, old_verify)
            require(counts == (record['primary_factorizations'], record['recomputation_factorizations']), 'FACTOR_COUNTS')
            primary += counts[0]; recompute += counts[1]
            transition(state, cell, record['outcome'], spec['max_depth'])
        if reason == 'NORMAL_EXIT':
            require(not state['frontier'] or len(records) == spec['max_attempts_per_worker'], 'EARLY_NORMAL_EXIT')
        require(primary + recompute <= spec['max_factorizations_per_worker'], 'FACTORIZATION_CAP')
        states[q] = state
        summaries[q] = {'attempts': len(records), 'primary_factorizations': primary,
                        'recomputation_factorizations': recompute,
                        'accepted_cells': len(state['accepted']),
                        'new_accepted_cells': len(state['accepted'])-len(initial(q, spec)['accepted']),
                        'frontier_cells': len(state['frontier']), 'unresolved_cells': len(state['unresolved']),
                        'accepted_fraction_of_quadrant': str(4*area(state['accepted'])),
                        'accepted_fraction_of_full_domain': str(area(state['accepted'])),
                        'wall_seconds': r['reaped']-r['start'], 'termination_reason': reason}
    require(len(observed_modes) == 1, 'MIXED_MODES')
    actual_synthetic = observed_modes.pop()
    require(sum(q['primary_factorizations'] + q['recomputation_factorizations'] for q in summaries.values()) <= spec['max_total_factorizations'], 'AGGREGATE_FACTORIZATION_CAP')
    if host is not None:
        result = {'packet': 'PARALLEL-DOMAIN-006', 'host': host, 'test_mode': actual_synthetic,
                  'status': 'HOST_SHARDS_REPLAYED_MERGE_REQUIRED',
                  'implementation_commit': implementation, 'shards': summaries}
        path = output / 'HOST_RESULTS.json'
        if write:
            durable.atomic_json(path, result)
        else:
            encoded = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False).encode('ascii')+b'\n'
            require(path.read_bytes() == encoded, 'DERIVED_OUTPUT_MISMATCH:HOST_RESULTS.json')
        return result
    validate_partition(states, spec, spec['max_depth'])
    accepted = sum((area(s['accepted']) for s in states.values()), Fraction())
    baseline = sum((area(initial(q, spec)['accepted']) for q in shard_names(spec)), Fraction())
    unfinished = any(s['frontier'] or s['unresolved'] for s in states.values())
    result = {'packet': 'PARALLEL-DOMAIN-006', 'test_mode': actual_synthetic,
              'status': ('SYNTHETIC_CONTROLS_ONLY' if actual_synthetic else
                         'INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE' if unfinished else
                         'COMPLETE_DOMAIN_CELL_ISOLATION_PENDING_INDEPENDENT_EVIDENCE_REVIEW'),
              'scope': 'cutoff-a finite 196-dimensional model; local cell external isolation only',
              'implementation_commit': implementation,
              'baseline_fraction_of_full_domain': str(baseline),
              'accepted_fraction_of_full_domain': str(accepted),
              'new_fraction_of_full_domain': str(accepted-baseline),
              'complete_disjoint_accounting': True, 'shards': summaries}
    for name, value in [('RESULTS.json', result), ('PARTITION.json', states)]:
        path = output / name
        encoded = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False).encode('ascii')+b'\n'
        if write:
            durable.atomic_json(path, value)
        else:
            require(path.read_bytes() == encoded, 'DERIVED_OUTPUT_MISMATCH:' + name)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=('worker', 'run', 'verify'))
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--implementation-commit', required=True)
    p.add_argument('--shard')
    p.add_argument('--host', type=int)
    p.add_argument('--wheel', type=Path)
    p.add_argument('--synthetic', action='store_true')
    p.add_argument('--fault', choices=('none', 'partial'), default='none')
    args = p.parse_args()
    args.output = args.output.resolve()
    if args.mode == 'worker':
        worker(args)
    elif args.mode == 'run':
        print(json.dumps(supervise(args), sort_keys=True))
    else:
        print(json.dumps(verify(args.output, args.implementation_commit, args.synthetic, host=args.host), sort_keys=True))


if __name__ == '__main__':
    main()
