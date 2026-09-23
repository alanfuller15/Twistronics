"""Counterexamples for the baseline observation checker; no model execution."""
import copy
import json
from pathlib import Path
import unittest
from probe_consumer import BASE, evaluate

EVIDENCE = Path(__file__).resolve().parent / 'evidence' / '20260923T0328Z'
FILES = json.loads((BASE / 'INPUT_MANIFEST.json').read_text())['files']
TRUSTED = {k: FILES[k]['sha256'] for k in ('guarded_topology.py', 'guarded_sparse.py',
           'migrated_valley_control.py', 'response_inputs.py', 'partner_v074p.zip')}


class OutcomeChecks(unittest.TestCase):
    def observation(self, name):
        return json.loads((EVIDENCE / name / 'OBSERVATION.json').read_text())

    def refused(self, name, obs, rc=None):
        verdict = evaluate(name, obs['returncode'] if rc is None else rc, obs, TRUSTED)
        self.assertFalse(verdict['baseline_observation_reproduced'])
        self.assertTrue(verdict['failed'])

    def test_retained_observations(self):
        for name in ('matching_plan', 'plan_N', 'plan_eps', 'existing_success', 'existing_abort'):
            with self.subTest(name=name):
                obs = self.observation(name)
                self.assertTrue(evaluate(name, obs['returncode'], obs, TRUSTED)['baseline_observation_reproduced'])

    def test_wrong_exit_cannot_pass(self):
        self.refused('plan_N', self.observation('plan_N'), rc=1)

    def test_unrelated_exception_cannot_pass(self):
        obs = self.observation('existing_abort')
        obs['exception'] = {'type': 'RuntimeError', 'message': 'unrelated import failure'}
        self.refused('existing_abort', obs)

    def test_successful_plan_binding_is_not_the_baseline_defect(self):
        obs = self.observation('plan_eps')
        for call in obs['constructor_calls']:
            call['defaults']['eps'] = .004
        self.refused('plan_eps', obs)

    def test_preserved_prior_bytes_are_not_truncation(self):
        obs = self.observation('existing_abort')
        obs['after_files'] = copy.deepcopy(obs['before_files'])
        self.refused('existing_abort', obs)

    def test_source_substitution_cannot_pass(self):
        obs = self.observation('matching_plan')
        obs['source_sha256']['migrated_valley_control.py'] = '0' * 64
        self.refused('matching_plan', obs)

    def test_duplicate_case_cannot_pass(self):
        obs = self.observation('matching_plan')
        obs['rows'][-1] = copy.deepcopy(obs['rows'][0])
        self.refused('matching_plan', obs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
