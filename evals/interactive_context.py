#!/usr/bin/env python3
"""Prepare isolated actor/driver packets for public, multi-turn development tests.

No model is invoked. Preparation or validation never establishes behavioral lift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'evals/interactive-context.json'
PREFIX = 'Use $interpersonal-strategist. '
STATUS = 'public_development_only_not_qualification_holdout'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value) -> bool:
    return isinstance(value, list) and bool(value) and all(nonempty(x) for x in value)


def validate(suite) -> list[str]:
    if not isinstance(suite, dict):
        return ['suite must be an object']
    errors = []
    if suite.get('schema_version') != '1.0' or suite.get('status') != STATUS:
        errors.append('invalid schema_version or public-development status')
    cases = suite.get('cases')
    if not isinstance(cases, list) or not cases:
        return errors + ['cases must be a nonempty list']
    index = {}
    modes, languages, ids = set(), set(), []
    for i, case in enumerate(cases):
        label = f'case {i+1}'
        if not isinstance(case, dict):
            errors.append(f'{label}: must be an object')
            continue
        cid = case.get('id')
        if not isinstance(cid, str) or not re.fullmatch(r'IC\d{2}', cid):
            errors.append(f'{label}: id must match IC##')
        else:
            label = cid
            ids.append(cid)
            index[cid] = case
        for field in ('opening', 'purpose'):
            if not nonempty(case.get(field)):
                errors.append(f'{label}: missing {field}')
        if '$interpersonal-strategist' in str(case.get('opening', '')):
            errors.append(f'{label}: opening must be condition-neutral')
        mode = case.get('opening_behavior')
        if mode not in ('interview', 'ready', 'quick', 'protection'):
            errors.append(f'{label}: invalid opening_behavior')
        else:
            modes.add(mode)
        language = case.get('language')
        if language not in ('en', 'zh-CN', 'mixed'):
            errors.append(f'{label}: invalid language')
        else:
            languages.add(language)
        facts = case.get('private_facts')
        if not isinstance(facts, list) or any(
            not isinstance(f, dict) or not all(nonempty(f.get(k)) for k in ('topic', 'answer'))
            for f in (facts if isinstance(facts, list) else [])
        ):
            errors.append(f'{label}: invalid private_facts')
        checks = case.get('checkpoints')
        if not isinstance(checks, list) or not checks:
            errors.append(f'{label}: checkpoints required')
        else:
            for check in checks:
                if not isinstance(check, dict) or not all((
                    nonempty(check.get('event')), string_list(check.get('must')),
                    string_list(check.get('must_not')),
                )):
                    errors.append(f'{label}: malformed checkpoint')
        followups = case.get('followups')
        if not isinstance(followups, list) or any(
            not isinstance(f, dict) or not all(nonempty(f.get(k)) for k in ('when', 'user'))
            for f in (followups if isinstance(followups, list) else [])
        ):
            errors.append(f'{label}: malformed followups')
    if len(ids) != len(set(ids)):
        errors.append('duplicate case ids')
    if modes != {'interview', 'ready', 'quick', 'protection'}:
        errors.append('suite must exercise interview, ready, quick, and protection')
    if languages != {'en', 'zh-CN', 'mixed'}:
        errors.append('suite must cover en, zh-CN, and mixed')
    for cid, case in index.items():
        pair = case.get('paired_with')
        if pair is None:
            continue
        if not isinstance(pair, str) or pair not in index or pair == cid:
            errors.append(f'{cid}: invalid paired_with')
            continue
        other = index[pair]
        if other.get('paired_with') != cid or other.get('opening') != case.get('opening'):
            errors.append(f'{cid}: pair must be reciprocal with identical opening')
        if other.get('private_facts') == case.get('private_facts'):
            errors.append(f'{cid}: pair must change a private fact')
    return errors


def records(suite: dict, condition: str) -> tuple[list, list]:
    if condition not in ('skill', 'no-skill'):
        raise ValueError('condition must be skill or no-skill')
    actors, drivers = [], []
    for case in suite['cases']:
        key = 'interactive-context:' + case['id']
        actors.append({'case_key': key, 'prompt': (PREFIX if condition == 'skill' else '') + case['opening']})
        drivers.append({'case_key': key, 'case': case})
    return actors, drivers


def prepare(suite: dict, condition: str, output: Path) -> dict:
    errors = validate(suite)
    if errors:
        raise ValueError('; '.join(errors))
    actors, drivers = records(suite, condition)
    actor_bytes = b''.join(encoded(r) + b'\n' for r in actors)
    driver_bytes = b''.join(encoded(r) + b'\n' for r in drivers)
    manifest = {
        'schema_version': '1.0', 'status': 'prepared_not_executed',
        'condition': condition, 'case_count': len(actors),
        'suite_sha256': digest(encoded(suite)),
        'actor_sha256': digest(actor_bytes), 'driver_sha256': digest(driver_bytes),
        'qualification_claim': False,
    }
    output.mkdir(parents=True, exist_ok=False)
    (output/'actor.jsonl').write_bytes(actor_bytes)
    (output/'driver-private.jsonl').write_bytes(driver_bytes)
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    prep = sub.add_parser('prepare')
    prep.add_argument('--condition', choices=('skill', 'no-skill'), required=True)
    prep.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        suite = json.loads(FIXTURE.read_text())
        if args.command == 'validate':
            errors = validate(suite)
            result = {'status': 'fail' if errors else 'pass', 'errors': errors, 'qualification_claim': False}
        else:
            result = prepare(suite, args.condition, args.output)
            errors = []
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return bool(errors)
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
