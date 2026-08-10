# Provenance

## Release identity

This repository begins a new standalone lineage at
`interpersonal-strategist 0.6.0-alpha.1`. The current release candidate is
`0.11.0-rc.1`.

`0.11.0-rc.1` is a production-qualification candidate, not a production claim.
Promotion is permitted only when `release/qualification.json` records every
required gate as passed and binds the evidence to an exact commit, package,
model and host configuration, evaluation harness, and independent holdout set.

The historical `interpersonal-strategist-v0.5a-20260725` candidate is
unavailable. This project does not claim byte, source, or behavior equivalence
to that candidate.

## Implementation seed

The implementation was reconstructed from the verified clean-room v0.2
candidate:

```text
interpersonal-strategist-v0.2-candidate.zip
SHA-256 549a5c2810eb294d97fdffcc6005b57bc72586cc37ebbaf2815b8ab4e9fe8281
```

The v0.2 Phase 1 R&D package was also reviewed:

```text
interpersonal-strategist-phase1-rd-v0.2.zip
SHA-256 3bf3ac1119b3e6741ebf9b751fa060eafcda011a3ad6fc7e44ae0f8ba1c898bf
```

## v0.5 through v0.11 advisory inputs

The exact recovered v0.5 R&D package was used as advisory research and design
input:

```text
interpersonal-strategist-v05-rd-20260725.zip
SHA-256 08988d2056913a86c976e35dc5fb035de8f0120237d24e20c6dbd67d3ba622eb
```

The independent post-publication review used for the v0.8 production-readiness
program was:

```text
interpersonal-strategist-pro-followup-20260729.md
SHA-256 c104e9da2617e0ef6d7a8f4134519f69a3a14cb2fb340b6cbac997274425d37d
```

These inputs contained research, architecture, evaluation, and implementation
recommendations. They did not contain sealed holdouts or an authoritative
production verdict.

## Comparable public systems audit

A fresh public-system audit was completed on 2026-07-30 and is recorded in:

- `research/comparable-public-systems-audit-20260730.md`;
- `provenance/PATTERN_DONORS.md`;
- `research/nonverbal-inference-source-note-20260730.md`.

The audit inspected exact public commits and licenses for Agent Skill evaluation,
role-play coaching, distributed-information benchmarks, social-agent evaluation,
and social-simulation architecture. Applied permissive-license patterns include:

- Microsoft Waza's documented Agent Skill evaluation interfaces as an optional
  secondary compatibility lane;
- Expression Trainer's one-cue practice cadence, re-expressed without its
  scores or psychological assumptions;
- HiddenBench's staged shared-versus-unique-information benchmark structure;
- Sotopia's separation of goal, information, relationship, privacy, safety, and
  naturalness dimensions without a single social score;
- Concordia's separation of scenario control, actor-visible information,
  simulation turns, and evaluation.

No donor source code, task corpus, prompt prose, examples, user interface,
persistent persona data, or creator voice is redistributed. The Waza YAML is
original project configuration written to its public schema. Sources without a
verified permissive license supplied comparison questions only, not copied
material.

Rejected donor mechanisms include facial-emotion or body-language verdicts,
diagnostic personality or attachment typing, hidden vulnerability or
pressure-point profiling, unsupported scores inferred from sparse cues,
secret-goal optimization, attraction or compliance scoring, refusal override,
coercive sexual or dating tactics, and Commons-Clause or proprietary framework
imports. A user-controlled, evidence-labeled dossier and bounded Decision Fit
Score are permitted under the current runtime contract. Romance is not excluded
as a category.

## Relationship-scope expansion

The `0.10.0-rc.1` scope expansion is recorded in:

- `research/relationship-scope-expansion-audit-20260730.md`;
- `provenance/RELATIONSHIP_SCOPE_EXPANSION.md`.

It supersedes the earlier product decision to route romance, dating, intimacy,
breakup, and reconciliation out of scope. Those situations now use the same
evidence, power, voluntariness, consent, privacy, action, and stopping controls
as other interpersonal decisions. Category inclusion does not authorize
coercion, refusal override, stalking, covert tests, intimate-media misuse,
sexual conduct involving minors or incapacity, diagnosis, or formal legal and
clinical determinations.

## Clean-room boundary

A third-party romance skill licensed under PolyForm Noncommercial 1.0.0 was
reviewed historically, and permissively licensed Chinese relationship skills
were reviewed for source organization and conversational workflow. The project
may independently implement compatible ideas, but it does not copy donor:

- prose or creator voice;
- reference corpora or transcripts;
- examples, questionnaires, or scripts;
- attraction or consent claims about another person, compliance scores, or
  relationship scores that omit their construct, anchors, evidence,
  counterevidence, unknowns, coverage, confidence, version, or correction path;
- MBTI or attachment diagnoses;
- deceptive, coercive, or refusal-overriding tactics.

Any future direct adaptation from an external source requires exact source
identification, license review, required notices, and explicit approval before
distribution. Inclusion in an index or public availability is not a license.

## Evidence governance

`provenance/evidence-sources.json` is the machine-readable source registry. A
promoted record must include:

- a stable DOI, PMID, official-document number, or official guide identity;
- canonical title, first author or issuing body, and year;
- evidence type and population or context;
- the precise claim permitted at runtime;
- a limitation and prohibited inference;
- a concrete runtime rule;
- verification date and source;
- a licensing or access note.

The distributable evidence ledger is a compact projection of this registry.
The validator requires one-to-one source-ID parity and checks that each ledger
row contains the recorded author or issuer and stable identity. Online
resolution remains a release-qualification step because deterministic packaging
and normal runtime use do not require network access.

Private local professional-development and systems-practice notes may generate
product hypotheses. They are not empirical authorities. A runtime empirical
claim must be independently sourced, or the relevant method must be identified
as an original product safeguard or practitioner scaffold.

A candidate source may remain in `research/` without runtime promotion. It must
not be represented as a promoted claim until the source registry, runtime ledger,
resolver report, and mutation tests agree.

## Evaluation provenance

Public development fixtures are not qualification holdouts. Independent
holdouts must be authored after the instruction package is frozen, kept outside
the public repository, checked for semantic overlap, and identified in the
qualification record only by cryptographic hash, composition, author/custodian
roles, and protocol version.

The optional Waza lane is secondary development evidence. Its binary version,
upstream identity, executor, model, task hashes, snapshots, and results must be
recorded when used. A Waza pass cannot replace target-host evidence, and a
weighted score cannot compensate for a project hard-gate failure.

A behavioral release attestation must bind:

- exact commit and release ZIP SHA-256;
- model snapshot and host version;
- skill and no-skill condition definitions;
- canonical harness and rubric versions;
- secondary harness identities and results when used;
- judge identities and calibration results;
- holdout-set hash and composition;
- bilingual review record;
- pilot protocol and disposition of private material.

## Excluded material

This repository does not contain:

- real personal conversations;
- uncontrolled or undisclosed personal memory;
- hidden personality, vulnerability, influence, surveillance, or pressure-point
  dossiers; governed user-controlled dossiers are limited to decision-relevant,
  source-labeled records with inspection, correction, expiry, export, and
  deletion controls;
- sealed or reconstructed holdout answers;
- credentials;
- private vault content;
- third-party source papers or proprietary framework prose;
- donor prompts, examples, task corpora, or persistent personas;
- autonomous connector or sending behavior.
