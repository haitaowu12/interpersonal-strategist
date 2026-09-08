# Interpersonal Strategist

[![CI](https://github.com/haitaowu12/interpersonal-strategist/actions/workflows/ci.yml/badge.svg)](https://github.com/haitaowu12/interpersonal-strategist/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release candidate](https://img.shields.io/badge/release-0.12.0--alpha.1-yellow.svg)](CHANGELOG.md)

`interpersonal-strategist` is a portable Agent Skill for everyday interpersonal decisions. It helps a user distinguish evidence from interpretation, map power and decision structure, compare plausible readings, choose a proportionate next move, and prepare wording with response branches and stopping rules.

Current release: **`0.13.0-alpha.1`**

> `0.13.0-alpha.1` is a production-qualification candidate, not a production claim.
> The runtime, evidence governance, public evaluation program, and release
> controls are implemented. Independent holdouts, calibrated behavioral
> comparison, fluent bilingual review, clean-host validation, and a controlled
> pilot remain required gates in `release/qualification.json`.

The [development baseline record](handoff/BASELINE-0.12.0-alpha.1.md)
separates completed implementation from the remaining qualification work.

## Start here

Use it to prepare a conversation, think through a situation, practice a reply,
or review what happened. Read the [English/Chinese quickstart](QUICKSTART.md).
Session-only and an evidence table are the defaults; scoring is optional and
cannot override missing critical information or an active flag.

`0.13.0-alpha.1` stabilizes the earlier context-first workflow: consistent dossier
rules, status-first scoring, planned-run accounting, boundary-safe statistics,
bounded execution and blinding, and actual-artifact qualification checks.
The [qualification runbook](release/QUALIFICATION-RUNBOOK.md),
[pilot kit](release/PILOT.md), and [host capability matrix](release/host-capabilities.json)
separate implemented tooling from unrun human and host gates.

## What changed in the alpha workflow

The first decision is now whether enough context exists to advise. Sparse or
contradictory cases trigger a focused question and a real pause; explicit
“grill me” starts an interview before strategy. Answers must update the working
read and the chosen move. Quick mode, sufficiently specified requests, and
urgent protection retain a direct path.

The sidekick loop is interview → shared read → plan → optional rehearsal →
outcome update. It challenges unsupported assumptions while respecting feelings,
uses the user's actual constraints, and helps recover when a plan does not work.
It does not require a report template, a questionnaire UI, or persistent memory.

Examples:

```text
$interpersonal-strategist My manager keeps excluding me. Help me think it through.
$interpersonal-strategist Grill me about this friendship before giving advice.
$interpersonal-strategist Quick mode: help me decline this request politely.
$interpersonal-strategist Let's rehearse my opening, one turn at a time.
$interpersonal-strategist I tried that. Here is what they actually said back.
```

The review and limitations are in
[the integration review](research/context-first-integration-20260907.md).
The new [interactive development protocol](evals/interactive-context-protocol.md)
tests actual turn boundaries and whether different answers change advice. It
has not yet established superiority over the same model without the skill.

## Product boundary

The skill supports:

- workplace leadership, managing up and down, workload, credit, exclusion,
  feedback, conflict, negotiation, and commitments;
- friendship, family, roommates, neighbors, caregiving, networking, and shared
  arrangements;
- attraction, asking someone out, early dating, relationship definition,
  exclusivity, partnership, jealousy, intimacy boundaries, breakup, distance,
  and reconciliation;
- consent-aware intimate communication and relationship decisions without
  pretending to make a legal determination;
- ambiguous chat, email, screenshot, digital, and AI-mediated communication;
- multi-actor decisions, power, dependency, retaliation exposure, and workplace
  romance;
- adaptive quick, standard, and bounded deep-context interaction;
- optional governed user and relationship dossiers using a host adapter,
  portable card, or session-only mode;
- a transparent Decision Fit Score for a named user decision, with
  user-configurable dimensions, weights, evidence, counterevidence, unknowns,
  coverage, confidence, versioning, and correction;
- English, Simplified Chinese, and mixed-language communication across these
  settings.

The remaining exclusions are tied to harm or authority, not to relationship
category. The skill does **not** facilitate:

- coercion, sexual pressure, grooming, stalking, retaliation, surveillance,
  humiliation, impersonation, evidence manipulation, or pressure after refusal
  or withdrawal of consent;
- sexual conduct involving minors, an adult-minor pursuit, or a person unable to
  consent;
- psychological diagnosis, unsupported person typing, human-worth scoring, or
  scores that claim to infer another person's attraction, consent, loyalty,
  deception, or private state;
- substantive legal, HR, medical, clinical, safeguarding, abuse, crisis, or
  emergency determinations;
- automatic sending, uncontrolled connectors, or hidden personality,
  vulnerability, influence, loyalty, pressure-point, surveillance, or
  social-status dossiers.

Invocation is explicit-only: `$interpersonal-strategist`.

## Runtime architecture

The repository separates the distributable runtime from development research,
evaluation, and release evidence.

```mermaid
flowchart LR
    U["Explicit user invocation"] --> R["Route"]
    R --> E["Read evidence"]
    E --> D["Select quick / standard / deep context"]
    D --> G{"Decision-changing gap?"}
    G -->|Yes or explicit interview| I["Ask and wait"]
    I --> U2["User answer or correction"]
    U2 --> D
    G -->|Ready or quick override| P["Map power and exposure"]
    P --> V["Check authority / consent / voluntariness"]
    V --> C["Classify mechanism"]
    C --> M["Load method + required overlays"]
    M --> A["Recommend one action"]
    A --> W["Draft wording"]
    W --> B["Branches, review, escalation, stop"]

    C --> O1["Power / safety overlay"]
    C --> O2["Multi-actor overlay"]
    C --> O3["Bilingual speech-act overlay"]
    C --> O4["AI-authorization overlay"]
    C --> O5["Romance / consent overlay"]

    S["Source registry"] -. constrains .-> M
    T["Public evals"] -. tests .-> R
    Q["Qualification manifest"] -. gates .-> Z["Production claim"]
```

### Distributable layer

`skill/interpersonal-strategist/` contains the complete portable skill:

- `SKILL.md` — routing, bounded decision loop, overlays, output contract, and
  safety invariants;
- `agents/openai.yaml` — display metadata and explicit-only policy;
- `references/` — progressively loaded knowledge modules, including the
  governed dossier and scoring contract;
- `assets/` — a user-editable scoring template;
- `scripts/` — a deterministic, offline score calculator with no persistence;
- `LICENSE` and `NOTICE.md` — redistribution terms and release boundary.

The package declares no network dependency, connector, API key, or bundled
database. Its optional scoring helper is deterministic and offline; it neither
infers ratings nor writes memory. Optional continuity uses only a host-provided
memory adapter under the memory contract, with portable-card and session-only
fallbacks.

### Decision loop

1. **Route** — `IN_SCOPE`, `COACH_WITH_CAUTION`, `REFER_OR_ESCALATE`, or
   `REFUSE`.
2. **Read** — separate records, observations, reports, interpretations,
   contradictions, unknowns, and stale facts.
3. **Map** — identify decision rights, dependencies, downside bearer,
   protection, audience, reversibility, and exposure.
4. **Classify** — distinguish information, coordination, authority, resource,
   process, status, trust, relationship-norm, attraction, dating, intimacy,
   separation, digital, multilingual, structural, consent, and safety mechanisms.
5. **Widen** — compare evidence-linked hypotheses and the observations that
   would change them.
6. **Act** — select the smallest useful move that remains sound if motive is
   uncertain.
7. **Update** — prepare plausible branches, an observation window, an
   escalation or reliance trigger, and a stop.

### Implemented mechanisms

The current runtime includes:

- **user-controlled dossiers** that separate user, counterpart, and
  relationship records; label evidence and counterevidence; preserve unknowns;
  and support inspection, correction, versioning, expiry, export, and deletion;
- a **Decision Fit Score** for bounded choices rather than people, with explicit
  dimensions, anchors, weights, coverage, confidence, dealbreakers, and safety
  gates outside the average;
- an **offline deterministic calculator** and public adversarial fixtures for
  missing data, conflict, correction, expiry, deletion, multi-actor comparison,
  misuse, and score challenges;
- expanded relationship evidence and exact-commit community pattern audits,
  while preserving clean-room implementation and evidence limitations;

- **adaptive conversation depth** with automatic readiness checks, explicit
  “grill me,” user-controlled quick mode, bounded rounds, and stop controls;
- **governed continuity memory** with scoped consent, minimal case cards,
  stale-fact verification, inspect/correct/forget controls, and no hidden
  personality or vulnerability profiling;
- **Forum-Authority-Information-Constituency-Ratification** for multi-actor
  decisions and hidden information;
- a **relationship-scope gate** covering communal care, shared arrangements,
  professional exchange, friendship, dating, partnership, intimacy, separation,
  reconciliation, and disputed norms;
- **Voluntariness-Specificity-Reversibility** checks for romantic and intimate
  decisions, including workplace and dependency overlays;
- a **feedback-exposure check** for target knowledge, candor, image cost,
  retaliation exposure, and feedback-seeking method;
- **minimum-safe reliance** choices: no reliance, minimum access, dual control,
  reversible trial, or normal reliance after evidence;
- **speech-act adaptation** for requests, refusals, disagreement, correction,
  feedback, apology, escalation, reminders, and invitations;
- an **AI authorization gate** for data permission, minimization,
  representational authority, truth, force, disclosure, and human ownership;
- prediction cards and structured debriefs that separate decision quality from
  outcome quality and prohibit covert interpersonal tests.

## Progressive disclosure

The kernel normally loads one method and one matching playbook. It adds only the
overlays made mandatory by power, safety, multilingual force, AI mediation, or
multi-actor structure.

The reference layer includes:

- evidence readiness and situation classification;
- power, voice, fair process, and multi-actor decisions;
- conflict containment and trust-reliance decisions;
- negotiation, authority, ratification, and commitments;
- relationship norms, reciprocity, repeated helping, dating, partnership,
  intimacy, breakup, and reconciliation;
- communication, feedback exposure, channel, and control rules;
- digital pragmatics and AI-mediated authorization;
- bilingual speech-act adaptation;
- practice and outcome-independent learning;
- deep-context elicitation, situational models, memory, and continuity;
- twenty-seven end-to-end scene playbooks;
- safety, privacy, referral, and the evidence ledger.

The flat reference structure keeps discovery predictable and the portable skill
auditable.

## Evidence governance

Research constrains general mechanisms and contraindications. It does not prove
a specific person's motive or guarantee an intervention result.

- `provenance/evidence-sources.json` is the machine-readable release source of
  truth.
- `references/evidence-ledger.md` is the distributable runtime projection.
- Each promoted source records stable identity, evidence type, precise permitted
  claim, limitation, runtime rule, verification date, and licensing note.
- Validation requires registry-ledger ID, first-author or issuer, and stable-
  identity parity.
- Online DOI, PMID, and official-document resolution remains a separate release
  qualification gate.
- Branded practitioner frameworks are quarantined as optional mnemonics and are
  not represented as causal scientific authorities.
- Cultural averages are context variables, never individual predictions.

The repository redistributes original skill content and summaries, not source
papers, proprietary course text, or branded framework prose.

## Installation

### Supported Skills interface

In supported ChatGPT environments, open **Plugins**, select the **Skills** tab,
choose **Create**, then **Upload from your computer**, and upload the generated
release ZIP. Skills follow the Agent Skills open standard and may also be
available through Codex or workspace plugins. Availability and installation can
depend on plan, workspace settings, role, surface, and admin policy.

Official guidance:
[Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt/).
Review the source and contents before installation; platform scanning does not
replace organizational review or the qualification record in this repository.

### Local development installation

When the specific Codex host supports local Agent Skills discovery, copy the
skill directory into its documented skills location. A commonly supported
developer layout is:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R skill/interpersonal-strategist "$HOME/.agents/skills/"
```

Repository-scoped layout where supported:

```bash
mkdir -p .agents/skills
cp -R /path/to/interpersonal-strategist/skill/interpersonal-strategist \
  .agents/skills/
```

Host discovery behavior is version-dependent. Confirm it in a clean supported
host rather than treating directory presence as integration evidence.

Invoke explicitly:

```text
$interpersonal-strategist
```

## Develop and verify

Requirements: Python 3.11 or newer; no third-party Python dependencies.

```bash
python3 -m compileall -q scripts evals tests
python3 scripts/validate.py
python3 evals/run.py validate-fixtures
python3 evals/persona_conversation.py validate
python3 evals/relationship_scope.py validate
python3 evals/interactive_context.py validate
python3 -m unittest discover -s tests -v
python3 scripts/package.py
python3 scripts/smoke_install.py \
  --archive "dist/interpersonal-strategist-$(cat VERSION).zip"
(cd dist && shasum -a 256 -c \
  "interpersonal-strategist-$(cat ../VERSION).zip.sha256")
```

The static suite verifies:

- release metadata parity;
- portable runtime structure and context budget;
- twelve method contracts and twenty-seven playbooks;
- source registry and ledger parity;
- canonical invocation and substantive routing ontologies;
- public fixture integrity and bilingual-pair minimums;
- blocked-versus-qualified release logic;
- deterministic packaging and package layout;
- mutation failures for stale metadata, wrong source author, incomplete
  qualification, and machine-specific dependencies.

Static success is necessary but not behavioral qualification.

## Public behavioral development program

The repository contains more than 200 prompt-bearing public fixtures plus ten
metamorphic pairs across:

- ordinary workplace and everyday decisions;
- invocation ownership and four-state routing;
- power, structural conditions, and formal-process proximity;
- multi-actor information and authority topology;
- relationship norms, dating, romance, intimacy, separation, reconciliation,
  and repeated helping;
- trust reliance and re-entry contraindications;
- AI authorization, privacy, authorship, and representation;
- English, Simplified Chinese, and mixed-language speech acts;
- consent, coercion, refusal, stalking, manipulation, diagnosis, cultural
  prediction, and other hard failures.

The rubric uses hard gates and 1-5 anchored dimensions with per-dimension floors.
A high score in evidence analysis cannot compensate for unsafe routing,
unauthorized wording, unusable language, or a missing stop condition.

Prepare host-runner manifests:

```bash
python3 evals/run.py prepare \
  --condition skill --output build/skill-prompts.jsonl
python3 evals/run.py prepare \
  --condition no-skill --output build/no-skill-prompts.jsonl
python3 evals/relationship_scope.py prepare \
  --condition skill --output build/relationship-scope-skill-prompts.jsonl
python3 evals/relationship_scope.py prepare \
  --condition no-skill --output build/relationship-scope-no-skill-prompts.jsonl
```

Summarize externally collected results:

```bash
python3 evals/run.py summarize \
  --plan build/plan.json \
  --responses build/responses.jsonl \
  --judgments build/judgments.jsonl \
  --output build/summary.json
```

The summarizer does not invoke a model or confer qualification. The optional
`evals/execute.py` invokes only a reviewed external adapter after explicit opt-in.
Freeze `build/plan.json` first using the runbook; no plan means unknown completeness.

## Production qualification

`release/qualification.json` is canonical. The release remains blocked until
all required evidence is bound to an exact commit and package:

1. static repository CI;
2. deterministic package and layout;
3. evidence registry parity and online identity resolution;
4. clean-host discovery and explicit invocation;
5. reference selection and compound-overlay behavior;
6. calibrated no-skill comparison;
7. independently authored untouched holdouts;
8. at least 150 adversarial safety holdouts with zero hard failures, including
   romance, consent, breakup, stalking, workplace-romance, and intimate-privacy
   strata;
9. two-reviewer bilingual naturalness and status-fit review;
10. judge calibration;
11. privacy-safe 10-20 episode controlled pilot;
12. independent release review.

A production claim requires a separate promotion PR that changes the manifest to
`qualified`, supplies the exact evidence hashes, and makes no substantive
runtime change.

See:

- [release contract](release/README.md)
- [judge calibration](evals/judge-protocol.md)
- [no-skill comparison](evals/no-skill-protocol.md)
- [untouched holdouts](evals/holdout-protocol.md)
- [Codex qualification handoff](handoff/CODEX-PRODUCTION-QUALIFICATION.md)

## Build a deterministic release

```bash
python3 scripts/package.py
```

This creates:

```text
dist/interpersonal-strategist-0.13.0-alpha.1.zip
dist/interpersonal-strategist-0.13.0-alpha.1.zip.sha256
dist/interpersonal-strategist-0.13.0-alpha.1.manifest.json
```

The ZIP contains one directly installable `interpersonal-strategist/` directory.
File ordering, timestamps, modes, and manifest generation are fixed so identical
source produces identical bytes.

## Repository layout

```text
skill/interpersonal-strategist/  directly installable runtime
evals/                           public development fixtures and protocols
scripts/                         validation, packaging, and layout smoke tests
tests/                           deterministic and mutation tests
provenance/                      lineage and evidence source governance
release/                         canonical production-qualification record
handoff/                         exact remaining Codex execution contract
research/                        retained research and architecture records
external-feedback/               advisory reviews
dist/                            ignored reproducible release artifacts
```

Development research, public fixtures, and qualification records are excluded
from the distributable ZIP.

## Provenance and licensing

This is a standalone lineage beginning at `0.6.0-alpha.1`. It does not claim
source, byte, or behavioral equivalence to the unavailable historical `v0.5a`
candidate. Exact implementation inputs, hashes, clean-room exclusions, and
holdout governance are recorded in `provenance/`.

MIT. See [LICENSE](LICENSE). Third-party works remain subject to their own
terms.
