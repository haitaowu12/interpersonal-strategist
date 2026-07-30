# Public Pattern Donors and Exclusions

This record governs ideas taken from the public-system audit dated 2026-07-30.
It is not an evidence ledger and does not make a donor project a scientific or
behavioral authority.

## Rules

- Record the exact inspected repository and commit.
- Verify the license before copying code, schemas, or substantial documentation.
- Prefer original implementation and clean-room expression even when the source
  is permissively licensed.
- Do not copy prompts, scripts, examples, creator voice, proprietary framework
  prose, datasets, or person profiles.
- A donor pattern must solve a demonstrated product or evaluation failure.
- Scientific claims still require promotion through
  `provenance/evidence-sources.json`; a software repository is not empirical
  proof.

## Applied permissive-license patterns

| Donor | Identity and license | Pattern retained | Local implementation | Material not imported |
|---|---|---|---|---|
| Microsoft Waza | `microsoft/waza@f466c4fddf71144f42311d7c4157e8c8b3f0fed6`; MIT | secondary Agent Skill evaluation lane, trigger tests, invocation checks, snapshots/replay, adversarial and token-budget commands | `evals/waza/` | Waza binaries, source code, weighted qualification policy, unimplemented grader claims |
| Expression Trainer | `fxy2311-youyou/expression-trainer@f925434ae85871c6ad2294b3756ee2d2b4b026ca`; MIT | one micro-feedback cue at a time and one prioritized next practice target | practice reference and role-play fixtures | prompt prose, word lists, UI, scores, emotion lexicon, directness assumptions |
| HiddenBench | `jonradoff/hiddenbench@9c9491ad75a3b21ca73e680be0704fac897d5d1e`; MIT | partial profile, shared versus unique information, staged disclosure, post-disclosure update, full-profile comparison | multi-actor fixtures | source code, benchmark data, task wording, provider integrations |
| Sotopia | `sotopia-lab/sotopia@a0aaafb440e570e5e61b7c44a44e5e417c545383`; MIT | separate goal, information, relationship/standing, privacy, safety, and naturalness review dimensions | role-play debrief and evaluation guidance | persona models, secrets, romance scenarios, numeric scoring, persistent state |
| Concordia | `google-deepmind/concordia@e71b3eff007d4c218246f46bd6084ff701685a09`; Apache-2.0 | separation of scenario control, actor-visible information, simulation turns, and evaluation | role-play state machine | framework code, persistent memory, prefabs, simulation data, character histories |

No copied donor code is included in the distributable skill. Waza-compatible YAML
files are original project configuration written against the documented public
schema.

## Clean-room conceptual references only

| Source | Reason direct import is not authorized | Concept considered | Exclusion |
|---|---|---|---|
| `bpainter/composable-dxp-claude-marketplace` group-dynamics coach at `4b42deabd31b5135f80578f3ea814ac702b1cf34` | repository license not established | independent input, lower-power participation, authority speaking later | no prompt prose, branded methods, body-language claims, or examples |
| `lyndonkl/claude` facilitation and negotiation skills at `44284a30610c7e881bbd4d623a318adcfbdaf886` | root license not established | explicit decision method and closure record | no prose, universal one-owner rule, assumed good intent, or forced commitment |
| Peter Munro AI Roleplay Coach gist | no license identified | start/stop state, adjustable difficulty, retry | no prompt text, personality completion, or agreement-pressure behavior |

These sources supplied comparison questions only. Local wording, methods, and
examples were independently created.

## Reviewed and rejected as donors

| Source | Rejected mechanism or licensing issue |
|---|---|
| `borghei/Claude-Skills@da5a8626632f08c5513b0f73add1bf8075ef83bd` | Commons Clause restrictions, branded frameworks, pseudo-precision, and no clean direct-import path |
| `travisjneuman/.claude@e74cd20465be466b0f30c19da760bc986c50177f` | no verified license, omnibus leadership scope, influence typologies, and unbounded practitioner imports |
| `Andropeee/conflict-coach@f4a5bec6f837d874ceb9d8db05f8f09c58f8fde0` | romance and attachment typing, persistent relationship history, inferred hidden dynamics |
| `DHIWAHAR-K/social-coach-live@17a484372e8171402eacf134529a7bb7a5bf5f3c` | facial-emotion and multimodal internal-state inference; no root license found |
| `sukanyag16/persona-ai-communication-coach` | persistent sessions, confidence and sentiment labels, badges, and person scoring |
| historical PolyForm Noncommercial romance skill | incompatible scope and license; prose, questionnaires, scripts, tactics, corpus, and creator voice excluded |

## Source-to-change trace

- `research/comparable-public-systems-audit-20260730.md` contains the assessment.
- `references/practice-and-after-action-learning.md` contains the simulation
  state machine and micro-feedback cadence.
- `references/power-and-workplace.md` contains participation and decision-method
  safeguards.
- `references/situation-classification-and-calibration.md` contains the
  nonverbal-evidence boundary.
- `evals/cases.json` and `evals/multi-actor.json` contain original regression
  scenarios.
- `evals/waza/` contains the optional secondary evaluation adapter.

Any future direct reuse beyond these recorded patterns requires a new provenance
entry, exact license review, notice assessment, and an independently reviewable
change.
