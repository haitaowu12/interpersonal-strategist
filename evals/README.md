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
6. **Functional bilingual review:** invariant preservation plus fluent
   naturalness and status-fit review.
7. **No-skill comparison:** same model and prompt, blinded randomized
   comparison against the model without the skill.
8. **Untouched holdouts:** independently authored after package freeze and kept
   outside the public repository.
9. **Controlled pilot:** privacy-minimized formative usability and failure
   discovery, not efficacy proof.

## Public fixture suites

- `cases.json` — broad public development cases;
- `invocation.json` — invocation-ownership classifier;
- `substantive-routes.json` — canonical four-state routes;
- `multi-actor.json` — forum, authority, unique information, constituency, and
  ratification;
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
  thresholds.

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

## Development-case execution

For each case:

1. build the deterministic release ZIP and record its SHA-256;
2. install and invoke the exact package explicitly for the skill condition;
3. use the same model snapshot, host, tools, context, and sampling policy for
   the no-skill condition;
4. retain raw prompts and responses without real identifying information;
5. record invocation ownership, substantive route, mechanism, overlays, and
   references used when the host exposes them;
6. apply every hard gate before dimensional scoring;
7. require every applicable dimension to meet its floor;
8. evaluate case-specific required and forbidden outcomes semantically, not by
   keyword presence alone;
9. review bilingual naturalness and status fit with fluent humans for material
   cases;
10. report every confusion and failure by domain rather than only an aggregate.

## Qualification boundary

A production claim is permitted only when `release/qualification.json` is
updated to `qualified` with evidence for all gates and exact hashes for:

- commit and release package;
- model and host configuration;
- harness and rubric;
- source-resolution report;
- no-skill comparison;
- judge calibration;
- independent holdouts;
- bilingual review;
- controlled pilot and privacy disposition.

Do not change the qualification status merely because structural CI passes.

## Required protocols

- [Judge calibration](judge-protocol.md)
- [No-skill comparison](no-skill-protocol.md)
- [Untouched holdouts](holdout-protocol.md)

## Privacy

Never add real conversations, names, identifying workplace records, credentials,
health details, or confidential attachments to public fixtures, issues, logs, or
release artifacts. Private pilot material must be minimized, access-controlled,
and deleted under the pilot protocol.
