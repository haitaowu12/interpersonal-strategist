"""Test isolation of model inputs from scenario facts and evaluation criteria."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('interactive_context', ROOT / 'evals/interactive_context.py')
lane = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lane)


class InteractiveContextTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads((ROOT / 'evals/interactive-context.json').read_text())

    def test_repository_suite_validates(self):
        self.assertEqual(lane.validate(self.suite), [])

    def test_actor_input_excludes_hidden_facts_and_oracle(self):
        case = copy.deepcopy(self.suite['cases'][0])
        case['private_facts'][0]['answer'] = 'PRIVATE_SENTINEL_417'
        case['checkpoints'][0]['must'].append('ORACLE_SENTINEL_923')
        actors, drivers = lane.records({'cases': [case]}, 'skill')
        self.assertEqual(set(actors[0]), {'case_key', 'prompt'})
        self.assertNotIn('PRIVATE_SENTINEL_417', json.dumps(actors))
        self.assertNotIn('ORACLE_SENTINEL_923', json.dumps(actors))
        self.assertIn('PRIVATE_SENTINEL_417', json.dumps(drivers))
        self.assertIn('ORACLE_SENTINEL_923', json.dumps(drivers))

    def test_only_invocation_differs_between_conditions(self):
        skill, _ = lane.records(self.suite, 'skill')
        native, _ = lane.records(self.suite, 'no-skill')
        self.assertEqual([x['case_key'] for x in skill], [x['case_key'] for x in native])
        for s, n in zip(skill, native):
            self.assertEqual(s['prompt'], lane.PREFIX + n['prompt'])
            self.assertNotIn('$interpersonal-strategist', n['prompt'])

    def test_rejects_unknown_condition(self):
        with self.assertRaises(ValueError):
            lane.records(self.suite, 'baseline-with-hints')

    def test_rejects_missing_paired_case(self):
        suite = copy.deepcopy(self.suite)
        suite['cases'][0]['paired_with'] = 'IC99'
        self.assertTrue(lane.validate(suite))

    def test_rejects_mismatched_pair_openings(self):
        suite = copy.deepcopy(self.suite)
        suite['cases'][0]['opening'] += ' Extra evidence.'
        self.assertTrue(lane.validate(suite))

    def test_rejects_duplicate_case_or_malformed_checkpoint(self):
        for mutate in (
            lambda d: d['cases'].append(copy.deepcopy(d['cases'][0])),
            lambda d: d['cases'][0]['checkpoints'][0].update(must='not a list'),
            lambda d: d['cases'][0].update(private_facts=[{'topic': '', 'answer': 'x'}]),
            lambda d: d['cases'][0].update(opening='Use $interpersonal-strategist. Hi'),
        ):
            suite = copy.deepcopy(self.suite)
            mutate(suite)
            self.assertTrue(lane.validate(suite))

    def test_wrong_top_level_does_not_crash(self):
        for value in (None, [], {}, {'schema_version':'1.0', 'cases':[None]}):
            self.assertTrue(lane.validate(value))

    def test_prepare_is_deterministic_and_fingerprints_inputs(self):
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            one = lane.prepare(self.suite, 'skill', target/'one')
            two = lane.prepare(self.suite, 'skill', target/'two')
            self.assertEqual(one, two)
            actors = target/'one/actor.jsonl'
            self.assertEqual(one['actor_sha256'], lane.digest(actors.read_bytes()))
            changed = copy.deepcopy(self.suite)
            changed['cases'][0]['private_facts'][0]['answer'] += ' Changed.'
            three = lane.prepare(changed, 'skill', target/'three')
            self.assertEqual(one['actor_sha256'], three['actor_sha256'])
            self.assertNotEqual(one['driver_sha256'], three['driver_sha256'])
            self.assertNotEqual(one['suite_sha256'], three['suite_sha256'])
            self.assertFalse(three['qualification_claim'])

    def test_prepare_refuses_overwriting_or_invalid_suite(self):
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)/'run'
            lane.prepare(self.suite, 'skill', target)
            with self.assertRaises(FileExistsError):
                lane.prepare(self.suite, 'skill', target)
            with self.assertRaises(ValueError):
                lane.prepare({}, 'skill', Path(raw)/'bad')
