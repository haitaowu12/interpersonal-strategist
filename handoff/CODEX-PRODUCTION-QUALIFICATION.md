# Codex Production-Qualification Handoff

## Objective

Complete the remaining executable qualification work for
`interpersonal-strategist 0.8.0-rc.1` without weakening its explicit-only,
stateless, chat-only, non-romantic, non-manipulative, and formal-authority
boundaries.

## Exact context

- Repository: `haitaowu12/interpersonal-strategist`
- Base reviewed commit: `606a8fabce225240315d218b97b1375f8db7bf27`
- Implementation branch: `agent/production-readiness-hardening`
- Independent handoff identity:
  `c104e9da2617e0ef6d7a8f4134519f69a3a14cb2fb340b6cbac997274425d37d`
- Candidate version: `0.8.0-rc.1`
- Canonical promotion record: `release/qualification.json`

Do not mark the product production-ready merely because CI passes. Production
wording is authorized only after every required qualification gate passes on an
exact frozen commit and package.

## Implemented in this branch

- corrected release metadata and stale notice;
- added release-governed evidence registry and corrected source identities;
- strengthened runtime routing, compound overlays, multi-actor information
  topology, relationship norms, feedback exposure, trust-reliance levels,
  bilingual speech acts, AI authorization, and outcome-independent learning;
- aligned twenty scene playbooks with those controls;
- separated invocation ownership from four-state substantive routing;
- added domain, bilingual, metamorphic, and adversarial public fixtures;
- replaced aggregate scoring with hard gates and per-dimension floors;
- added no-skill, judge-calibration, holdout, and release protocols;
- added deterministic evaluation preparation and summarization tooling;
- added a blocked qualification manifest.

## Required Codex work

### 1. Check out and verify the exact branch

```bash
git fetch origin
git checkout agent/production-readiness-hardening
git status --short
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 evals/run.py validate-fixtures
python3 scripts/package.py
python3 scripts/smoke_install.py --archive "dist/interpersonal-strategist-$(cat VERSION).zip"
(cd dist && shasum -a 256 -c "interpersonal-strategist-$(cat ../VERSION).zip.sha256")
```

Fix deterministic defects only. Do not loosen a gate to make a test pass.

### 2. Run source-resolution verification

Create or complete `scripts/check_evidence.py` if the branch does not already
contain a working online resolver. It must:

- read `provenance/evidence-sources.json`;
- resolve DOI, PMID, and official-document identities through authoritative
  endpoints;
- compare normalized title, first author or issuing body, and year;
- distinguish online-first and issue year where relevant;
- emit a machine-readable report with per-source status and SHA-256;
- fail on identity mismatch, unresolved promoted source, or missing required
  metadata;
- avoid downloading or redistributing article text.

Attach the report to the qualification evidence and populate only the
`online_source_resolution` gate after human review of exceptions.

### 3. Perform clean-host discovery and invocation

Using a supported current Codex/Skills environment:

1. build the exact release ZIP;
2. install or upload it through the supported skill-management flow;
3. start a clean session;
4. confirm explicit discovery and invocation;
5. run one ordinary case, one compound multi-actor case, one refusal, one
   safety referral, and one bilingual case;
6. confirm the skill performs no connector use, file writes, automatic sending,
   or persistent profiling;
7. retain model snapshot, host version, package SHA, raw outputs, and run logs.

Do not treat `scripts/smoke_install.py` as host-discovery evidence; it verifies
package layout only.

### 4. Instrument reference selection

Where the host exposes reference-read traces, record:

- primary reference selected;
- mandatory overlays selected;
- irrelevant references loaded;
- missing-reference behavior.

Run at least 30 public development cases, including compound power,
multilingual, AI, safety, and multi-actor cases. Required gates are in
`evals/rubric.json`.

If traces are unavailable, use output-discriminating probes and label the
result as indirect behavioral evidence rather than retrieval telemetry.

### 5. Run calibrated no-skill comparison

Follow:

- `evals/no-skill-protocol.md`
- `evals/judge-protocol.md`
- `evals/rubric.json`

Generate manifests:

```bash
python3 evals/run.py prepare --condition skill --output build/skill-prompts.jsonl
python3 evals/run.py prepare --condition no-skill --output build/no-skill-prompts.jsonl
```

Hold model, host, tools, context, sampling, and response budget constant. Blind
condition identity. Use pointwise scoring first and pairwise preference second.
Run order-swap and verbosity-bias probes. Report strata, not only aggregate
results.

### 6. Commission independent untouched holdouts

Follow `evals/holdout-protocol.md` exactly.

- freeze the package before authoring;
- use authors who did not implement this release;
- keep prompts and adjudication outside the public repository;
- run lexical and semantic overlap checks;
- publish only hashes, composition, roles, protocol, and aggregate results;
- do not reuse a tuned-against set as untouched qualification evidence.

Required minimums:

- 60 general holdouts;
- 30 multi-actor cases;
- 30 bilingual or mixed-language cases;
- 150 adversarial safety/authority/privacy/coercion/AI/formal-boundary cases;
- zero hard-gate failures.

### 7. Complete fluent bilingual review

Use at least two fluent reviewers familiar with workplace pragmatics. Review
English-Simplified Chinese pairs for:

- fact and uncertainty parity;
- decision right and authority;
- meaningful ability to decline;
- boundary and consequence;
- escalation and stop;
- naturalness and status fit.

Minimum median naturalness/status-fit rating: 4/5. Every material drift is a
hard failure regardless of average score.

### 8. Run the privacy-safe controlled pilot

Use 10-20 consented episodes for usability and failure discovery only.

- no real conversations in the repository;
- no persistent third-party profiles;
- minimize and pseudonymize retained material;
- define access, retention, deletion, and incident handling;
- review decision quality separately from outcome quality;
- record unexpected escalation, inability to execute wording, privacy issues,
  over-analysis, and wrong routing;
- do not market pilot results as universal efficacy.

### 9. Produce the qualification evidence bundle

Create an access-controlled bundle containing:

- exact commit and ZIP SHA-256;
- static CI and package reports;
- source-resolution report;
- host discovery and invocation evidence;
- retrieval/overlay report;
- judge calibration report;
- no-skill comparison report;
- holdout-set hash, composition, overlap audit, and aggregate results;
- bilingual review record;
- pilot protocol, aggregate findings, and privacy disposition;
- independent release review.

Do not add private holdout prompts, real conversations, or identifying pilot
material to this repository.

### 10. Promotion PR

Open a separate promotion PR only after all gates pass. Update
`release/qualification.json` with:

- `status: qualified`;
- `production_claim_allowed: true`;
- exact `qualification_commit`;
- package, harness, response, judgment, holdout, and report hashes;
- evidence location for every gate.

Then update README and release badge from qualification candidate to production.
Do not combine substantive runtime changes with the promotion PR. Any runtime
change invalidates affected behavioral evidence and requires a fresh tranche.

## Stop conditions

Stop and leave the release blocked when:

- any hard-gate failure remains unresolved;
- source identity cannot be verified;
- host or model configuration differs between skill and no-skill conditions;
- judge calibration misses its agreement thresholds;
- bilingual function drifts;
- holdout independence or overlap cannot be established;
- pilot privacy controls are incomplete;
- the exact release commit or package hash changes.

## Return contract

Return:

1. exact branch, commit, and package SHA;
2. commands run and raw pass/fail status;
3. defects fixed, with files and tests;
4. qualification evidence produced, with hashes;
5. each gate status and blocker;
6. PR URL and exact head SHA;
7. explicit `QUALIFIED` or `BLOCKED` verdict.

Do not return a production-ready verdict without a fully populated passing
qualification manifest.
