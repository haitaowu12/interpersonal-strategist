# Persona and Conversation Pattern Donors

## Record identity

- Review date: 2026-07-30
- Target baseline: `haitaowu12/interpersonal-strategist`
  `e1b607286a385faa84cb7f6ad9ef39b73548a6ef`
- Purpose: evaluate public persona and chat-analysis skills for transferable
  architecture, Chinese-language function, contraindications, and regression
  cases.
- Distribution rule: this repository redistributes original clean-room
  instructions and tests only.

No donor prose, prompts, formulas, examples, catchphrases, style imitation,
person profiles, transcripts, or source corpora are copied into the
distributable skill.

A permissive license permits copying under its terms; it does not make a donor
mechanism sound, in scope, or evidence-backed. An index does not grant a blanket license over linked repositories.

## Inspected repositories

| Repository | Exact commit | License finding at inspected commit | Role in this change |
|---|---|---|---|
| `tmstack/awesome-persona-skills` | `7648d7be53926a9441f47170ec2254d6f383c941` | No root `LICENSE` file identified. The repository is an index; each linked project requires its own review. | Discovery map only. |
| `hotcoffeeshake/tong-jincheng-skill` | `c9caaa9a6576f581c29d016c60bbe935908e20d5` | MIT `LICENSE` file. | Clean-room architecture comparison; romance content and persona voice excluded. |
| `Pronting/chat-skills` | `0bc7fb6f8da1767d43bb9ac14c243b693357a332` | MIT `LICENSE` file. | Negative-pattern donor plus limited observable-turn workflow comparison. |
| `alchaincyf/nuwa-skill` | `27642f5bfed2dc1bbf8ee59a2c1ee602a626bbd7` | MIT `LICENSE` file. | Clean-room source-window, tension, and honest-boundary patterns. |
| `titanwings/colleague-skill` | `47039d08fcf0330794caea14efdb5e183348f7bb` | MIT `LICENSE` file. | Correction/versioning and source-priority comparison; third-party persona retention rejected. |
| `vogtsw/boss-skills` | `93f5c7c0a5d7091ce45ce1343ab4bfad662a0c19` | No root `LICENSE` file identified. | Comparison questions only; no material copied or adapted. |
| `notdog1998/yourself-skill` | `9deb1a87b1231fec85cadf2ef690fa49fef519ca` | MIT `LICENSE` file. | Inspect/correct/delete and snapshot-language comparison; existing target controls are stronger. |
| `leilei926524-tech/anti-distill` | `21e6aa9c72a03a5456eeb4cd63234a2fa2935387` | README declares MIT; no root `LICENSE` file identified. | Rejected mechanism and adversarial comparator only. |

The two user-specified implementation donors with root license files,
`tong-jincheng-skill` and `chat-skills`, both use MIT terms. This change still
uses clean-room synthesis rather than direct text reuse.

## Applied patterns

### Source-backed rules instead of catchphrase imitation

The useful unit is a bounded decision rule with:

- source and time window;
- context;
- priority or criterion;
- action;
- exception;
- limitation;
- contradiction or change over time;
- evidence that would update the application.

This became the source-bounded Lens Card in
`references/pragmatics-and-digital-channels.md`.

### Visible uncertainty and honest boundary

A perspective lens must state what the source record does not support. Public
expression does not establish private thought, current endorsement, or a stable
personality. Contradictions narrow the rule rather than being explained away.

### Observable conversation reconstruction

A conversation may be reconstructed into exact turns, source quality, speech
acts, operational effects, and uncertainty. The sequence can identify receipt,
clarification, proposal, refusal, commitment, repair, closure, or reopening.

Only this observable structure was retained from chat-analysis donors. Their
social formulas, relationship stages, hidden scores, and strategic escalation
were not retained.

### Correction and versioning

A user correction changes the record. It is not evidence of resistance or
confirmation. A lens can be revised or discarded. Optional case memory remains
scoped, inspectable, correctable, deletable, and separate from a third-party
persona model.

### Prediction before outcome

Where enough source data exists, a lens can record an observable prediction,
alternative, falsifier, and decision relevance before the outcome. Evaluation
should use held-out or forward decisions, not train and score on the same set.
Prediction quality does not validate a personality ontology.

## Duplicated patterns not re-imported

The target already had stronger controls for:

- evidence versus inference;
- power and retaliation exposure;
- nonverbal and latency caution;
- English and Simplified Chinese speech-act parity;
- role-play state and stop rules;
- outcome-independent debriefs;
- memory consent, minimization, correction, and deletion;
- no diagnosis, cultural prediction, coercion, or covert testing.

Donor variants of these mechanisms were not added as extra frameworks.

## Rejected mechanisms

### Pseudo-precise social quantification

Rejected:

- intent-truth, social-power, attraction, compliance, loyalty, intimacy,
  deception, relationship, or “window” scores;
- arbitrary 0.05 adjustments from punctuation, emoji, message length, avatar,
  latency, or demeanor;
- formulas whose input variables are unsupported psychological constructs.

Precision cannot repair invalid measurement.

### Refusal override and compliance ladders

Rejected:

- treating inferred behavior as stronger than an explicit refusal;
- “口嫌体正直” as a reason to continue;
- sunk-cost escalation;
- sequential small requests designed to increase compliance;
- repeated asks, strategic delay, jealousy, withdrawal, or pressure after
  refusal.

An explicit refusal remains controlling until the person clearly and
voluntarily reopens the request.

### Internal-state and appearance inference

Rejected:

- avatar, profile photo, appearance, gaze, posture, voice, camera state,
  punctuation, emoji, or response time as proof of personality, emotion,
  honesty, attraction, competence, power, or motive.

### Persona imitation and dossiers

Rejected:

- first-person simulation of a living or named person as though they are
  present;
- private-thought or current-endorsement claims;
- MBTI, attachment, astrology, archetype, or nationality as individual
  evidence;
- persistent third-party transcript, recipient, relationship, vulnerability,
  influence, loyalty, pressure-point, or status dossiers;
- self-sealing “corrections prove the model” logic;
- catchphrase or voice fidelity as the primary quality measure.

### Deceptive knowledge withholding

`anti-distill` explicitly describes producing a submission that appears
complete while removing core knowledge and retaining a private version. That
mechanism conflicts with truth, ownership, and non-deception requirements. It
is recorded only so regression cases can reject equivalent requests.

### Romance and physical-escalation strategy

Romance, dating, sexual escalation, attraction scoring, and “attack window”
content remain outside the target product boundary even when a donor is
permissively licensed.

## Implementation linkage

- Runtime: `skill/interpersonal-strategist/SKILL.md`
- Conversation and lens method:
  `skill/interpersonal-strategist/references/pragmatics-and-digital-channels.md`
- Public development cases:
  `evals/persona-conversation-regressions.json`
- Deterministic secondary lane: `evals/persona_conversation.py`
- Hard-gate wording: `evals/rubric.json`
- Audit: `research/persona-and-conversation-systems-audit-20260730.md`

These additions do not alter `release/qualification.json`, create a production
claim, or count as untouched holdout evidence.
