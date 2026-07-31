# Persona and Conversation Systems Audit

**Date:** 2026-07-30  
**Target baseline:** `haitaowu12/interpersonal-strategist`
`e1b607286a385faa84cb7f6ad9ef39b73548a6ef`  
**Target release state:** `0.9.0-rc.1`, production qualification blocked  
**Review type:** fresh content, knowledge, safety, bilingual-function, donor, and
implementation audit

## Decision

### Content sufficiency

**Disposition: SUFFICIENT FOR THE CORE PURPOSE, WITH TARGETED GAPS.**

The target already contains enough breadth and method depth to support its
defined purpose: non-romantic workplace and everyday interpersonal decisions
involving ambiguity, power, boundaries, feedback, conflict, negotiation,
workload, credit, exclusion, trust, relationship maintenance, digital channels,
multi-actor decisions, English, Simplified Chinese, and mixed-language use.

This conclusion applies to content and architecture. It is not a production or
efficacy claim. Production qualification remains blocked because the governed
release record still requires exact-host evidence, calibrated comparison,
untouched holdouts, adversarial safety holdouts, fluent bilingual review, judge
calibration, a privacy-safe pilot, and independent release review.

### What was actually missing

The remaining gap was not another broad interpersonal framework. The missing
layer was an explicit method for:

1. checking the integrity of chat, email, OCR, forwarded-message, and screenshot
   evidence before interpreting it;
2. distinguishing receipt, understanding, agreement, commitment, completion,
   refusal, closure, and reopening;
3. preventing low-specificity digital cues from becoming pseudo-precise social
   scores;
4. preserving explicit refusal against “behavior outweighs words,” sunk-cost,
   compliance-ladder, or face-saving overrides;
5. applying public-person or mentor material as a source-bounded perspective
   lens rather than impersonation or a persistent persona;
6. testing those failure modes in English, Simplified Chinese, and mixed
   language.

Those gaps are addressed in this change.

## Baseline assessment

The baseline already had the following substantive coverage:

- four-state routing and explicit product boundaries;
- evidence, report, inference, contradiction, unknown, and confidence
  separation;
- Power-Reversibility-Exposure and multi-actor authority/information mapping;
- mechanism selection rather than framework dumping;
- twenty end-to-end scene playbooks;
- conflict containment, apology evaluation, trust repair, and minimum-safe
  reliance;
- negotiation, alternatives, criteria, authority, ratification, commitments,
  and review;
- relationship-norm and non-romantic reciprocity handling;
- digital ambiguity, channel selection, and AI authorization;
- English and Simplified Chinese speech-act adaptation;
- bounded role-play, prediction cards, and outcome-independent debriefs;
- optional governed case memory with consent, minimization, inspection,
  correction, and deletion;
- a release-governed evidence ledger and public evaluation program.

The target therefore did not need to absorb a persona framework wholesale. A
takeover would increase context load, duplicate controls, and import out-of-
scope assumptions without solving a demonstrated failure.

## Evaluation criteria

Donors were assessed on:

- fit to the target's non-romantic decision-support boundary;
- evidence and source traceability;
- separation of observed behavior from attributed internal state;
- power, authorization, privacy, and refusal controls;
- execution value rather than voice imitation;
- English and Simplified Chinese functional value;
- correction and falsifiability;
- evaluation design;
- exact license status;
- risk of coercion, deception, diagnosis, cultural prediction, or profiling.

## Requested repository review

### `tmstack/awesome-persona-skills`

**Inspected commit:** `7648d7be53926a9441f47170ec2254d6f383c941`

The repository is useful as a discovery index across workplace, relationship,
self-growth, business, public-person, traditional-culture, companion, and tool
skills. It demonstrates that persona projects often separate source gathering,
decision rules, expression style, examples, and evaluation.

It does not grant a blanket license over the linked repositories. No root
`LICENSE` file was identified at the inspected commit. Each linked project was
therefore reviewed independently before any implementation decision.

**Useful lesson:** maintain a discovery map, then inspect the actual donor,
commit, license, source boundary, and failure modes.

**Rejected lesson:** popularity, inclusion in an “awesome” list, or a polished
persona is not evidence that the method is safe or useful for interpersonal
decisions.

### `hotcoffeeshake/tong-jincheng-skill`

**Inspected commit:** `c9caaa9a6576f581c29d016c60bbe935908e20d5`  
**License:** MIT root license file

The repository provides a structured persona synthesis with source notes,
repeated claims, conversational behavior, external views, decisions, internal
tensions, limitations, and an honest-boundary section.

The strongest transferable patterns were:

- identify the source of each claimed rule;
- distinguish repeated first-party statements from external interpretation;
- record contradictions and changes of stance;
- expose information gaps;
- convert a claim into context, action, exception, and limitation;
- prefer directness and truthful preparation over secret tests.

The target did not import:

- first-person creator imitation;
- romantic or dating advice;
- deterministic attraction claims;
- “bragging proves insecurity” or similar internal-state shortcuts;
- false excuses offered as face-saving devices;
- status or gender cynicism;
- catchphrases, examples, or creator voice.

### `Pronting/chat-skills`

**Inspected commit:** `0bc7fb6f8da1767d43bb9ac14c243b693357a332`  
**License:** MIT root license file

The repository decomposes chat analysis into input extraction, stage
classification, calculations, output options, and risk notes. The limited
transferable idea is to reconstruct an exchange from observable turns and make
the operational state explicit.

The core mechanics are incompatible with this product:

- twenty-one psychological and strategic variables assigned 0.00-1.00 values;
- arbitrary 0.05 adjustments from punctuation, emoji, response delay, message
  length, and other low-specificity cues;
- intent-truth, social-power, and escalation-window formulas;
- compliance ladders and sunk-cost logic;
- response delay and unpredictability treated as status;
- emotional volatility treated as evidence of importance;
- inferred behavior allowed to override verbal refusal;
- romance stages and physical escalation;
- hidden-chain-of-thought requirements;
- “attack,” “pull,” and “withdraw” framing.

These mechanisms are recorded as adversarial regression targets, not imported
methods.

## Additional ecosystem sample

### `alchaincyf/nuwa-skill`

**Inspected commit:** `27642f5bfed2dc1bbf8ee59a2c1ee602a626bbd7`  
**License:** MIT root license file

Useful concepts include source windows, mental models, decision heuristics,
anti-patterns, internal tensions, honest boundaries, and structured quality
review. The target adopted a clean-room Lens Card with source, rule, tension,
application, limit, alternative, and update condition.

Rejected: first-person public-person simulation, private-thought implication,
style fidelity as a primary objective, and aggregate fidelity scores that can
reward imitation instead of decision quality.

### `titanwings/colleague-skill`

**Inspected commit:** `47039d08fcf0330794caea14efdb5e183348f7bb`  
**License:** MIT root license file

Useful concepts include source priority, correction, versioning, and separating
work rules from expressive style.

Rejected: ingesting third-party chat histories into durable colleague personas,
unsupported personality labels, or the claim that a model “thinks like” the
person. The target's existing memory contract is narrower and safer.

### `vogtsw/boss-skills`

**Inspected commit:** `93f5c7c0a5d7091ce45ce1343ab4bfad662a0c19`  
**License finding:** no root `LICENSE` file identified

Useful comparison concepts include decision cases, criteria, rules, playbooks,
and held-out replay. No material was copied or adapted because the inspected
repository did not establish a root license.

The held-out principle was independently re-expressed: a lens should be tested
on forward or held-out decisions, not fitted and scored on the same examples.

### `notdog1998/yourself-skill`

**Inspected commit:** `9deb1a87b1231fec85cadf2ef690fa49fef519ca`  
**License:** MIT root license file

Useful comparison concepts include inspect, correct, delete, version, and
snapshot language. These controls were already present in stronger form in the
target.

Rejected: broad personal-data collection, EXIF or private-history ingestion,
and MBTI, astrology, emotional-pattern, or diagnostic labels as person truth.

### `leilei926524-tech/anti-distill`

**Inspected commit:** `21e6aa9c72a03a5456eeb4cd63234a2fa2935387`  
**License finding:** README declares MIT; no root `LICENSE` file identified

The repository explicitly describes creating a submission that appears
complete while replacing valuable knowledge with hollow content and retaining a
private version. That mechanism conflicts with truth, ownership, and
non-deception invariants. It was rejected in full and retained only as a
negative comparator.

## Primary-source crosscheck

The runtime additions use already promoted evidence where possible and do not
add a new scientific claim to `provenance/evidence-sources.json`.

The audit also checked descriptive interaction concepts against primary
scholarship:

- Sacks, Schegloff, and Jefferson (1974), “A Simplest Systematics for the
  Organization of Turn-Taking for Conversation,” DOI `10.2307/412243`;
- Schegloff, Jefferson, and Sacks (1977), “The Preference for Self-Correction in
  the Organization of Repair in Conversation,” DOI `10.2307/413107`;
- Gu (1990), “Politeness Phenomena in Modern Chinese,” DOI
  `10.1016/0378-2166(90)90082-O`;
- Mao (1994), “Beyond Politeness Theory: 'Face' Revisited and Renewed,” DOI
  `10.1016/0378-2166(94)90025-6`.

These sources support attending to sequence, turn organization, repair,
speech-act function, and context-sensitive face concerns. They do not validate
a social score, a hidden-personality model, a national script, or a rule that
politeness overrides refusal.

The existing ledger remains the runtime authority for:

- grounding and shared understanding (`PRAGMATICS-01`);
- request and apology function (`PRAGMATICS-02`, `PRAGMATICS-03`);
- digital-norm and tone caution (`DIGITAL-01`, `DIGITAL-02`);
- channel selection (`CHANNEL-01`);
- AI authorization and representation (`AI-COMM-01`, `AI-COMM-02`,
  `AI-GOV-01`);
- humility about perceived evaluation (`PERCEPT-01`);
- no lie verdict from demeanor (`DECEPTION-01`);
- no individual prediction from cultural averages (`CULTURE-01`);
- prediction-before-outcome and outcome-bias control (`DECISION-01`).

## Gap matrix

| Capability | Baseline | Gap before change | Decision |
|---|---|---|---|
| Workplace and everyday scene coverage | Strong | No material breadth gap | Preserve |
| Power, authority, voice, and exposure | Strong | Donor versions duplicated existing controls | Preserve |
| Conflict, repair, negotiation, and commitments | Strong | No material method gap | Preserve |
| Chinese speech-act function | Good | Receipt versus approval and vague deferral needed more explicit operational rules | Enhance |
| Screenshot, OCR, forwarded-message, and transcript integrity | Partial | No dedicated pre-interpretation integrity gate | Enhance |
| Digital cue interpretation | Good caution | Donor-specific score and refusal-override attacks were not isolated | Harden |
| Explicit refusal precedence | Present in safety boundary | Needed direct counter-rules for face, sunk cost, and inferred-behavior overrides | Harden |
| Public-person or mentor perspective requests | Not explicit | Risk of first-person imitation and hidden persona claims | Add bounded Lens Card |
| Memory correction and deletion | Strong | Persona donors were weaker or broader | Do not import |
| Persona voice fidelity | Out of scope | Could displace decision quality | Reject |
| Romance and physical escalation | Out of scope | Donors would expand scope | Reject |
| Social formulas and scores | Prohibited in principle | Needed named regression coverage | Add tests |
| Public development evaluation | Broad | No focused persona/conversation lane | Add 31-case lane |

## Implemented changes

### Runtime kernel

`skill/interpersonal-strategist/SKILL.md` now:

- routes chat, email, screenshot, and perspective requests explicitly;
- requires source completeness, attribution, sequence, and OCR uncertainty
  checks;
- states that explicit refusal remains controlling;
- prohibits numerical social/person/intent/attraction/loyalty/compliance/
  deception/relationship scores;
- distinguishes role lenses, source-bounded public perspective lenses, and
  current-case hypotheses;
- prohibits named-person first-person impersonation, private-state claims,
  self-sealing models, style-fidelity substitution, and persistent third-party
  dossiers;
- adds Chinese receipt, approval, commitment, and vague-deferral cautions;
- preserves all existing routing, power, bilingual, memory, role-play, and
  release-governance controls.

### Reference layer

`skill/interpersonal-strategist/references/pragmatics-and-digital-channels.md`
now includes:

- permission and data minimization;
- screenshot, OCR, translation, forwarding, and edit integrity;
- a Conversation Evidence Table;
- descriptive interaction states;
- refusal and consent precedence;
- receipt-understanding-agreement-commitment-completion separation;
- context-sensitive Chinese terms including `收到`, `可以`, `回头看`, `有空`,
  `再看看`, and `没事`;
- truthful face-preserving communication;
- latency, punctuation, emoji, avatar, camera, and appearance boundaries;
- group-chat attribution and authority;
- role and source-bounded Lens Cards;
- correction, held-out prediction, and no-dossier controls.

### Evaluation and CI

The change adds:

- `evals/persona-conversation-regressions.json` with 31 public development
  cases across English, Simplified Chinese, and mixed language;
- `evals/persona_conversation.py` for deterministic validation and skill/no-skill
  prompt preparation;
- `tests/test_persona_conversation_hardening.py`;
- CI validation and exported prompt manifests;
- hard-gate wording for invented social scores, refusal override,
  compliance/sunk-cost ladders, avatar and latency inference, third-party
  transcript/persona dossiers, and strategic-response-delay tests.

Public regression cases are not untouched holdouts and cannot satisfy the
release holdout gate.

## Acceptance criteria

The change is acceptable only if:

- repository validation remains clean;
- Python 3.11 and 3.13 CI pass on the exact PR head;
- the skill remains under its context budget and links every packaged reference;
- the existing 0.9 routing, memory, role-play, bilingual, evidence, package, and
  mutation tests pass;
- the new 31-case fixture validates and prepares deterministically;
- packaging and smoke-install checks pass;
- `release/qualification.json` remains blocked;
- no donor content is redistributed.

## Remaining work after merge

1. Run the new lane in the target host under the same skill and no-skill
   conditions used by the governed comparison protocol.
2. Have fluent reviewers inspect the Simplified Chinese and mixed-language
   cases for naturalness and force parity.
3. Add private, independently authored holdout cases only after the instruction
   package and evaluation protocol are frozen. Do not derive them from the
   public cases.
4. Test source-bounded lenses on held-out public decisions and report
   calibration, abstentions, and failure cases rather than an aggregate
   “fidelity” claim.
5. Bind any qualification evidence to the exact post-merge commit, package hash,
   model snapshot, host version, and harness. Static success alone does not
   permit promotion.

## Final assessment

The skill's content and knowledge are sufficient for its intended core purpose.
The main risk was not missing interpersonal theory; it was that common persona
and chat-analysis patterns could introduce unsupported person models, coercive
optimization, romance scope, or pseudo-precise certainty.

The implemented change closes the highest-value gaps without expanding the
product into a persona emulator. Production qualification remains blocked until
the existing release gates are satisfied.
