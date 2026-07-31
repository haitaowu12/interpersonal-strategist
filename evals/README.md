# Evaluation and Production-Qualification Protocol

The public fixtures are synthetic development evidence. They are not untouched
holdouts, do not contain real conversations, and cannot by themselves support a
production claim.

## Evaluation layers

1. **Static integrity:** repository structure, release metadata, evidence
   registry, portability, and deterministic packaging.
2. **Invocation ownership:** whether the explicit skill should own the request,
   delegate writing or translation, route romance elsewhere, or not own it.
3. **Substantive routing:** `IN_SCOPE`, `COACH_WITH_CAUTION`,
   `REFER_OR_ESCALATE`, or `REFUSE`.
4. **Mechanism and reference selection:** leading method, mandatory overlays,
   primary reference, unnecessary-reference rate, and compound-case recall.
5. **Response quality:** pointwise hard gates and per-dimension floors.
6. **Simulation control:** setup/simulation/debrief separation, counterpart
   information boundary, turn and stop rules, one-variable replay, and
   micro-feedback cadence.
7. **Nonverbal inference:** low-specificity cues remain observations and do not
   become emotion, honesty, consent, engagement, competence, or motive verdicts.
8. **Functional bilingual review:** invariant preservation plus fluent
   naturalness and status-fit review.
9. **No-skill comparison:** same model and prompt, blinded randomized comparison
   against the model without the skill.
10. **Untouched holdouts:** independently authored after package freeze and kept
    outside the public repository.
11. **Controlled pilot:** privacy-minimized formative usability and failure
    discovery, not efficacy proof.

## Public fixture suites

- `cases.json` — broad public development cases, including bounded role-play,
  nonverbal inference, and facilitation regressions;
- `invocation.json` — invocation-ownership classifier;
- `substantive-routes.json` — canonical four-state routes;
- `multi-actor.json` — forum, authority, unique information, constituency,
  ratification, staged disclosure, and information integration;
- `relationship-norms.json` — communal care, shared arrangements, professional
  exchange, voluntary connection, and disputed norms;
- `ai-mediated.json` — data authorization, representational authority,
  authorship, force, and privacy;
- `trust-reliance.json` — no reliance, minimum access, dual control, reversible
  trial, and normal reliance after evidence;
- `speech-acts.json` — requests, refusals, disagreement, correction, feedback,
  apology, escalation, reminders, and mixed-language recaps;
- `bilingual-parity.json` — functional English-Simplified Chinese invariants;
- `metamorphic.json` — paired cases where one material variable changes;
- `rubric.json` — hard gates, 1-5 anchored dimensions, and qualification
  thresholds;
- `waza/` — optional secondary cross-executor Agent Skill evaluation lane.

## Running the deterministic preparation tools

These commands do not call a model or claim behavioral success:

```bash
python3 evals/run.py validate-fixtures
python3 evals/run.py prepare --condition skill --output build/skill-prompts.jsonl
python3 evals/run.py prepare --condition no-skill --output build/no-skill-prompts.jsonl
python3 evals/run.py summarize --responses build/responses.jsonl --judgments build/judgments.jsonl --output build/summary.json
```

`prepare` creates stable prompt manifests and hashes. A host runner must invoke
the exact packaged skill and retain raw responses. `summarize` validates result
records and computes route metrics, hard-gate counts, dimension-floor failures,
and paired wins, losses, and ties where judgments are supplied.

Every response record must retain `run_id`, a unique randomized `blind_id`,
`case_key`, `condition`, non-empty `response`, and a string-list `strata`.
Every judgment must bind the same `blind_id`, `run_id`, `case_key`, and
`condition`; declare the canonical rubric version; score every hard gate and
dimension; and include an observable evidence reason. The judge-facing packet
uses `blind_id`; the condition and run mapping are restored only after pointwise
scoring. When both conditions are present, every case must be paired and must
have exactly one pairwise judgment. Incomplete, duplicate, unpaired,
wrong-version, or unknown records fail closed rather than appearing
failure-free.

## Development-case execution

For each case:

1. build the deterministic release ZIP and record its SHA-256;
2. install and invoke the exact package explicitly for the skill condition;
3. use the same model snapshot, host, tools, context, and sampling policy for the
   no-skill condition;
4. retain raw prompts and responses without real identifying information;
5. record invocation ownership, substantive route, mechanism, overlays, and
   references used when the host exposes them;
6. apply every hard gate before dimensional scoring;
7. require every applicable dimension to meet its floor;
8. evaluate case-specific required and forbidden outcomes semantically, not by
   keyword presence alone;
9. review bilingual naturalness and status fit with fluent humans for material
   cases;
10. for role-play, keep scenario controller, counterpart turns, and debrief
    evidence separate;
11. for multi-actor cases, distinguish information integration from consensus;
12. report every confusion and failure by domain rather than only an aggregate.

## Secondary Waza lane

`evals/waza/` contains original project configuration for Microsoft Waza,
inspected at upstream commit
`f466c4fddf71144f42311d7c4157e8c8b3f0fed6` under MIT.

Use it to cross-check:

- explicit trigger and anti-trigger behavior;
- skill-invocation traces where the executor exposes them;
- coercion refusal;
- nonverbal mind-reading prevention;
- role-play state separation and micro-feedback;
- distributed information and facilitation;
- bilingual boundary preservation;
- snapshots, replay, adversarial packs, spec coverage, and token budget.

The lane is Copilot-executor oriented and is not canonical qualification
evidence for Codex or ChatGPT. Several Waza grader types are documented as not
implemented. Apply this project's hard gates before any Waza weighted score and
calibrate prompt graders against humans before promotion use.

See [`waza/README.md`](waza/README.md).

## Qualification boundary

A production claim is permitted only when `release/qualification.json` is
updated to `qualified` with evidence for all gates and exact hashes for:

- commit and release package;
- model and host configuration;
- canonical harness and rubric;
- optional secondary-harness identity and results when used;
- source-resolution report;
- no-skill comparison;
- judge calibration;
- independent holdouts;
- bilingual review;
- controlled pilot and privacy disposition.

Do not change the qualification status merely because structural CI or Waza
passes.

## Required protocols

- [Judge calibration](judge-protocol.md)
- [No-skill comparison](no-skill-protocol.md)
- [Untouched holdouts](holdout-protocol.md)
- [Waza secondary lane](waza/README.md)

## Privacy

Never add real conversations, names, identifying workplace records, credentials,
health details, facial or voice recordings, biometric inferences, or confidential
attachments to public fixtures, issues, logs, snapshots, or release artifacts.
Private pilot material must be minimized, access-controlled, and deleted under
the pilot protocol.
