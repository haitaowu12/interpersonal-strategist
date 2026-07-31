# Comparable Public Skills and Systems Audit

Date: 2026-07-30

Status: implementation input for `0.8.0-rc.1`; not qualification evidence

## Question

Which public skills, coaching applications, role-play systems, social-agent
benchmarks, and Agent Skill evaluation tools overlap with the intended product,
and which mechanisms can be adopted without weakening the explicit-only,
stateless, chat-only, non-romantic, non-manipulative boundary?

This audit distinguishes:

- **direct adoption:** a compatible implementation or schema from a verified
  permissive license;
- **clean-room adaptation:** a general pattern re-expressed independently;
- **research input:** useful evidence or a negative comparator, not donor code;
- **reject:** a mechanism that conflicts with scope, evidence, privacy, safety,
  portability, or licensing.

No third-party prose, scripts, examples, proprietary framework text, persona
profiles, or source corpora are copied into the distributable skill.

## Highest-value findings

### 1. Microsoft Waza is the strongest direct tooling candidate

- Repository: `microsoft/waza`
- Inspected commit: `f466c4fddf71144f42311d7c4157e8c8b3f0fed6`
- License: MIT
- Relevant capabilities: Agent Skill scaffolding, positive and negative trigger
  tests, skill-invocation grading, prompt and program graders, spec coverage,
  snapshots and replay, adversarial packs, token-budget checks, and result
  comparison.

**Adopt:** add a repository-owned Waza compatibility lane under `evals/waza/`
for cross-executor trigger, invocation, adversarial, token-budget, and replay
checks.

**Do not substitute:** Waza currently uses a Copilot-oriented execution path and
several documented human or comparison graders remain unimplemented. It cannot
replace the exact target-host skill/no-skill comparison, independent holdouts,
fluent bilingual review, or the release qualification manifest. Its weighted
aggregate model must not override this project's hard gates and per-dimension
floors.

### 2. Expression Trainer has a useful coaching cadence, not a safe social model

- Repository: `fxy2311-youyou/expression-trainer`
- Inspected commit: `f925434ae85871c6ad2294b3756ee2d2b4b026ca`
- License: MIT
- Useful pattern: one short real-time cue, followed by a post-session report and
  one next practice target; user-selected practice goals can change feedback
  priority.

**Adopt:** in role-play, provide at most one decision-relevant cue per turn when
live coaching is requested, then provide one prioritized practice target at the
end. Preserve a no-interruption mode.

**Reject:** 0-100 communication scores, treating hedging as proof of conflict
avoidance, inferring nervousness or confidence from wording, and universalizing
more direct language as better. Interpersonal directness depends on purpose,
power, culture, channel, and safety.

### 3. HiddenBench supplies a stronger distributed-information test pattern

- Repository: `jonradoff/hiddenbench`
- Inspected commit: `9c9491ad75a3b21ca73e680be0704fac897d5d1e`
- License: MIT
- Useful pattern: shared information versus uniquely held information,
  pre-discussion judgment, staged disclosure, post-discussion update, and a
  full-profile upper-bound comparison.

**Adopt:** extend multi-actor fixtures to test whether the skill identifies
which actor holds decision-critical information, requests independent input
before convergence, updates when that information appears, and distinguishes
information integration from consensus.

**Do not import:** benchmark datasets or task text. New scenarios must remain
original and privacy-safe.

### 4. Sotopia reinforces decomposed evaluation instead of one social score

- Repository: `sotopia-lab/sotopia`
- Inspected commit: `a0aaafb440e570e5e61b7c44a44e5e417c545383`
- License: MIT
- Useful dimensions: goal progress, information gain, relationship or standing
  effect, privacy leakage, social-rule or safety violations, and naturalness.

**Adopt:** use these as separate review questions for simulations and pilot
episodes. Do not add them into a single social-performance number, and do not
score a third party's personality, loyalty, or relationship value.

**Reject:** persistent persona consistency, secret-goal optimization, romance
coverage, and numeric pseudo-precision as runtime mechanisms.

### 5. Concordia supports separation of simulation, counterpart, and evaluator

- Repository: `google-deepmind/concordia`
- Inspected commit: `e71b3eff007d4c218246f46bd6084ff701685a09`
- License: Apache-2.0
- Useful pattern: a scenario controller governs what each simulated actor can
  know, while evaluation remains separate from the actor's turn.

**Adopt:** role-play must separate `SETUP`, `SIMULATION`, and `DEBRIEF` states.
The simulated counterpart receives only role-appropriate context, stays in
character for one natural turn, and must not leak hidden constraints or coach
analysis during the simulation.

**Reject:** persistent character memories and broad social simulation as runtime
requirements for this stateless skill.

## Additional systems reviewed

| System | Exact inspected identity | Useful observation | Decision |
|---|---|---|---|
| `bpainter/composable-dxp-claude-marketplace` group-dynamics coach | commit `4b42deabd31b5135f80578f3ea814ac702b1cf34`; repository license not established | independent idea generation, round-robin input, authority speaking later, visible dissent | Clean-room process concepts only; reject body-language mind reading and branded prose |
| `lyndonkl/claude` facilitation and negotiation skills | commit `44284a30610c7e881bbd4d623a318adcfbdaf886`; no verified root license | declare decision method, distinguish consultation from consent, close owners and open items | Clean-room concepts only; reject universal one-owner and disagree-and-commit rules |
| Peter Munro AI Roleplay Coach gist | inspected 2026-07-30; no license identified | explicit start and stop, adjustable difficulty, retries | Clean-room concepts only; never copy wording or invent personality profiles |
| `borghei/Claude-Skills` executive mentor | commit `da5a8626632f08c5513b0f73add1bf8075ef83bd`; Commons Clause + MIT | pre-mortems and observable tripwires | No direct import or redistribution; product concepts require independent sourcing |
| `travisjneuman/.claude` leadership skill | commit `e74cd20465be466b0f30c19da760bc986c50177f`; no verified license | broad scenario inventory | Reject omnibus import, influence types, and unbounded branded framework use |
| `Andropeee/conflict-coach` | commit `f4a5bec6f837d874ceb9d8db05f8f09c58f8fde0`; MIT | structured output and privacy engineering | Reject romance, attachment typing, persistent relationship tracking, and inferred hidden dynamics |
| `DHIWAHAR-K/social-coach-live` | commit `17a484372e8171402eacf134529a7bb7a5bf5f3c`; no root license found | accessibility motivation and structured reply output | Use as a negative comparator: reject facial-emotion, gaze, posture, and vocal-affect verdicts |
| `sukanyag16/persona-ai-communication-coach` | public repository inspected 2026-07-30; license not established | separates text and speech analysis | Reject persistent profiles, confidence/tone labels, badges, and longitudinal person scoring |
| Strands `evals` and AgentEvals | public repositories inspected 2026-07-30 | dynamic simulation and trace-oriented grading | Consider only when the target host exposes stable traces; no takeover now |

## Mechanisms applied to this branch

1. **Stateful role-play controller without persistent memory**
   - scenario card;
   - explicit `SETUP`, `SIMULATION`, and `DEBRIEF` states;
   - role-appropriate information;
   - turn budget and stop phrase;
   - one micro-cue per turn only when requested;
   - one-variable replay and one prioritized practice target.

2. **Facilitation safeguards**
   - collect independent or written input before convergence when information or
     power is uneven;
   - let the decision owner speak after relevant lower-power evidence when an
     early view would anchor discussion;
   - state whether the process is consultation, recommendation, vote, consent,
     consensus, or unilateral decision;
   - record dissent, assumptions, unresolved dependencies, and ratification.

3. **Nonverbal-evidence boundary**
   - facial movement, gaze, posture, fidgeting, silence, camera state, and vocal
     affect may be described as observations;
   - they do not establish emotion, honesty, consent, engagement, diagnosis,
     intent, or motive;
   - advice must use context, records, explicit behavior, and a decision-relevant
     clarification rather than a nonverbal verdict.

4. **Distributed-information evaluation**
   - partial-profile judgment;
   - independent elicitation;
   - staged disclosure;
   - update quality;
   - full-information counterfactual;
   - consensus-without-integration failure.

5. **Optional Waza compatibility lane**
   - trigger and anti-trigger probes;
   - explicit skill invocation;
   - role-play state separation;
   - nonverbal inference refusal;
   - coercion refusal;
   - distributed-information handling;
   - snapshots, replay, adversarial packs, and token-budget checks.

## Rejected takeover paths

Do not adopt or recreate:

- attachment-style, MBTI, personality, confidence, loyalty, attractiveness,
  manipulability, or influence scoring;
- facial-expression, gaze, posture, voice, punctuation, or latency as an emotion,
  deception, consent, diagnosis, or motive detector;
- persistent third-party dossiers, relationship-health histories, or secret
  goals;
- romance, intimacy, attraction, breakup, or sexual-consent strategy;
- coercive objection handling, agreement pressure, secret coalition building, or
  simulated refusal that continues after a clear stop;
- proprietary framework prose, course text, creator voice, or Commons-Clause
  material;
- a long omnibus skill that loads every framework for every case;
- a single aggregate social score that permits safety, privacy, or authority
  failure to be compensated by fluency or goal achievement.

## Remaining research and qualification implications

- Waza should be run as a **secondary cross-executor lane**, not as the
  production authority. Record its exact binary version, upstream commit,
  executor, model, prompt manifests, snapshots, and result hashes.
- Exact target-host qualification still requires the canonical public harness,
  independent untouched holdouts, human judge calibration, bilingual review,
  and a privacy-safe pilot.
- Trace-oriented simulators should be reconsidered only if Codex or the supported
  Skills host exposes stable reference-read and turn-level traces.
- The nonverbal boundary should receive independent adversarial cases, including
  accessibility and neurodivergence contexts, before promotion.
