# Waza Secondary Evaluation Lane

This directory adapts a bounded subset of the public development program to
[Microsoft Waza](https://github.com/microsoft/waza), an MIT-licensed CLI for
Agent Skill evaluation.

Inspected upstream identity:

```text
microsoft/waza
commit f466c4fddf71144f42311d7c4157e8c8b3f0fed6
license MIT
```

## Status

This is a **secondary cross-executor lane**. It does not replace:

- `evals/run.py` and the canonical response/judgment record format;
- clean target-host discovery and explicit invocation;
- the same-model skill versus no-skill comparison;
- independently authored untouched holdouts;
- human judge calibration and bilingual review;
- `release/qualification.json`.

Waza's current documented execution path is Copilot-oriented, while production
qualification targets the supported Codex/Skills host. Several Waza grader types
are also documented as not implemented. A Waza pass is therefore comparative
development evidence, not production qualification.

## Why keep this lane

It supplies an independent implementation of:

- trigger and anti-trigger tests;
- skill-invocation checks;
- prompt and program grading;
- snapshots and replay;
- adversarial packs;
- spec-coverage verification;
- token-budget checks;
- cross-model result comparison.

Using a second harness helps detect defects in the local harness, but the two
systems must not share a single unreviewed judge or convert hard failures into a
weighted average.

## Prepare a Waza workspace

Do not change the repository's distributable layout merely for Waza. Build a
temporary workspace:

```bash
rm -rf build/waza-workspace
mkdir -p build/waza-workspace/skills build/waza-workspace/evals
cp -R skill/interpersonal-strategist \
  build/waza-workspace/skills/interpersonal-strategist
cp -R evals/waza \
  build/waza-workspace/evals/interpersonal-strategist
cd build/waza-workspace
```

Record the Waza binary version and upstream commit used. Prefer a pinned release
or independently verified checksum rather than an unrecorded moving installer.

## Static and trigger checks

```bash
waza check skills/interpersonal-strategist
waza spec verify \
  skills/interpersonal-strategist \
  evals/interpersonal-strategist/eval.yaml \
  --fail --format github-actions
waza tokens count skills/interpersonal-strategist
```

Run trigger tests through the Waza command supported by the installed version.
The skill is explicit-only; an otherwise in-scope prompt without
`$interpersonal-strategist` belongs in the anti-trigger set.

## Run and preserve evidence

```bash
waza run evals/interpersonal-strategist/eval.yaml \
  --output results.json \
  --snapshot snapshots/ \
  -v
waza grade evals/interpersonal-strategist/eval.yaml \
  --results results.json
waza replay snapshots/<snapshot>.json
```

Also inspect available adversarial packs:

```bash
waza adversarial --list-packs
waza adversarial \
  --skill skills/interpersonal-strategist \
  --model <recorded-model>
```

Retain hashes for:

- exact skill package and branch commit;
- Waza binary and version;
- `eval.yaml`, task files, and trigger tests;
- model and executor;
- snapshots, raw results, grades, and comparison report.

## Interpretation rules

- Apply `../rubric.json` hard gates before any aggregate score.
- A Waza metric cannot compensate for coercion, fabrication, unsafe exposure,
  nonverbal mind reading, bilingual drift, privacy failure, or simulation
  leakage.
- Prompt graders must be calibrated against human review before their scores are
  used for promotion.
- Regex or text graders are smoke checks, not semantic qualification.
- Waza's skill-invocation trace is relevant only when the executor exposes the
  actual invocation event.
- A result from a Copilot executor does not prove behavior in Codex or ChatGPT.

## Files

- `eval.yaml` — secondary suite definition;
- `trigger_tests.yaml` — explicit invocation and collision probes;
- `tasks/` — original synthetic tasks for invocation, coercion, nonverbal
  inference, role-play state control, distributed information, facilitation, and
  bilingual function.
