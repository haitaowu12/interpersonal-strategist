# Interpersonal Strategist: context-first sidekick review

Reviewed 2026-09-07. First-pass candidate: `0.11.0-alpha.1`.

This audit originally covered `main` only. Continuation discovered draft PR #7
with newer governed profiles/scoring. The integrated `0.12.0-alpha.1` candidate
preserves that work and supersedes the first-pass runtime. See
[the integration record](context-first-integration-20260907.md).

The project has substantial domain coverage and safeguards, but it has not yet
shown that its interactive experience or advice beats the same model without
the skill. The alpha report is credible evidence of a product problem; without
an anonymized transcript and host/version, its exact cause is not reproduced.
This revision addresses the documented instruction conflict and adds a way to
test the conversation rather than only its final answer.

## Current state verified

| Surface | Observed state | Meaning |
|---|---|---|
| GitHub `main`, freshly cloned | `12b230be0e068cfae23acf28a8b438dd46a998cb`, `0.10.0-rc.1` | Current authoritative development baseline |
| `/Users/tony/Developer/interpersonal-strategist` | Clean `main` at `606a8fabce225240315d218b97b1375f8db7bf27`, 85 commits behind its tracked remote | Local checkout is stale; it was not used as the revision base |
| `/Users/tony/.agents/skills/interpersonal-strategist/NOTICE.md` | `0.8.0-rc.1` | Installed local artifact predates the deep-context and relationship expansion; not proof of what every alpha tester loaded |
| `release/qualification.json` | `blocked`, `production_claim_allowed: false`; model/host/package qualification fields null and required gates pending | No current qualified superiority or production-readiness claim |
| Baseline local checks | Repository validation and 34 unit tests passed before edits | Passing structural checks did not rule out the reported interaction failure |

The source's strengths are worth retaining: evidence/interpretation separation,
power and dependency awareness, consent and refusal precedence, practical scene
coverage, bilingual pragmatics, bounded rehearsal, and honest memory controls.
The bottleneck is their delivery and behavioral evidence, not lack of another
large library of interpersonal frameworks.

## Findings and dispositions

| Priority | Finding and source evidence | Product consequence | Revision |
|---|---|---|---|
| P1 | [Baseline entrypoint, depth selection](https://github.com/haitaowu12/interpersonal-strategist/blob/12b230be0e068cfae23acf28a8b438dd46a998cb/skill/interpersonal-strategist/SKILL.md#L43) presents four modes without a concrete first-turn wait contract; its [Act instruction](https://github.com/haitaowu12/interpersonal-strategist/blob/12b230be0e068cfae23acf28a8b438dd46a998cb/skill/interpersonal-strategist/SKILL.md#L142) requires an early recommendation. | Plausible mechanism for advice before elicitation, even when material facts are unknown. This is instruction analysis, not a measured causal attribution of the alpha failure. | Put readiness and ask/wait behavior in the entrypoint before analysis; scope “early recommendation” to an advice turn. Explicit grill begins with a real question and pause. |
| P1 | [Deep-context reference](https://github.com/haitaowu12/interpersonal-strategist/blob/12b230be0e068cfae23acf28a8b438dd46a998cb/skill/interpersonal-strategist/references/deep-context-elicitation.md#L29) asks for a provisional read first; its closing checklist expects a recommendation and controls for a deep-context exchange. | Even loading the reference can steer toward a complete answer instead of waiting. | Use a factual reflection before the question; make closing checks apply when delivering advice, not each interview turn. |
| P1 | Installed version is stale; host and version used by alpha testers are unknown. | Source fixes may never reach the runtime being tested. | Give the candidate a distinct alpha version and package hash; require exact package/host recording in comparisons. Installation still needs a writable target session. |
| P1 | [Depth test](https://github.com/haitaowu12/interpersonal-strategist/blob/12b230be0e068cfae23acf28a8b438dd46a998cb/tests/test_project.py#L350) checks strings, links, and fixture IDs. Existing depth prompts are single-turn. The qualification record has no passed model comparison. | Tests can stay green while the model skips waiting, ignores answers, or gives unchanged generic advice. | Add 18 multi-turn scenarios, answer-dependent pairs, separate actor/operator packets, and a three-condition plus equal-information comparison protocol. Behavioral execution remains pending. |
| P2 | [Default output](https://github.com/haitaowu12/interpersonal-strategist/blob/12b230be0e068cfae23acf28a8b438dd46a998cb/skill/interpersonal-strategist/SKILL.md#L268) encourages a six-part report; most kernel space enumerates methods and overlays. | Risks a polished report with little situational advantage. This is a design risk, not a scored naturalness result. | Replace the report default with per-turn purpose. Require a move linked to an actual elicited fact, usable wording, and the branch that matters. Avoid frameworks in the first interview turn. |
| P2 | Role-play, update, and continuity exist, but are dispersed among references rather than joined into a clear interaction. | May behave like a one-shot analyst instead of a continuing thinking partner. | Connect interview, shared read, plan, rehearsal, and result update. Carry corrections in conversation; do not imply persistent storage. |

## What changed for the user

A sparse “my manager keeps excluding me; what should I say?” now calls for a
focused question before a script. A revealed remit boundary should produce a
different move from a repeated documented approval bypass. “Grill me first”
requires waiting, not a plan with trailing questions. A fully specified coffee
confirmation stays one line. Quick mode bypasses optional intake. Urgent
protection precedes any interview. Stop, unknown answers, corrections, and
requested context confirmation have explicit handling.

The tone contract now asks for attentive support without endorsing accusations,
and candid challenge without humiliating or blaming the user. Advice connects
to evidence elicited during the conversation. Rehearsal proceeds one turn at a
time; a later result changes the recommendation rather than restarting intake.

English, Chinese, and mixed-language cases exercise these distinctions. This is
not a claim that the new language has passed fluent bilingual user review.

## Community intake

Selected dependency-aware questioning, actual wait boundaries, discovery before
synthesis, and a chat fallback from community interview/coaching repositories.
Rejected exhaustive grilling, recommended factual answers, mandatory popup
APIs, broad private-source exploration, automatic memory/files, and unverified
quantitative efficacy claims. No donor prose or question bank was copied.

Pinned sources and licensing observations:
[CONTEXT_INTERVIEW_DONORS.md](../provenance/CONTEXT_INTERVIEW_DONORS.md).
No academic claims were added to the evidence ledger.

## Validation and limits

Local results on the revised source:

- 44 unit tests pass, including ten new packet-isolation and mutation tests.
  New lane was red before implementation; its ten tests then passed.
- Repository validation, offline 40-source registry validation, existing fixture
  lanes, and the new interactive lane pass.
- Skill Creator validation passes using the vault's Python environment. System
  Python lacked PyYAML; the existing environment supplied it without installation.
- Deterministic packaging, package layout smoke test, and ZIP checksum pass.
  The smoke test verifies portable layout, not actual model invocation.
- Both 18-case actor/operator manifests prepare successfully with the same
  fixture and operator hashes; only invocation differs in actor prompts.
- `git diff --check` passes.

No model conversations, human judgments, paired preference scores, or real-life
outcomes were collected in this revision. No target-host alpha transcript was
provided. The new fixtures are publicly authored development scenarios, not
independent holdouts. Kernel instructions and package checks cannot enforce a
host's turn behavior or prove a measured improvement.

The release remains blocked. Do not call this production-ready or better than
native OpenAI on the basis of this review.

## Next acceptance evidence

1. Load the exact candidate in the actual alpha host and record package hash,
   host/version, model, and invocation. Confirm the first question is reached
   and the reference can be loaded; a directory or ZIP alone proves neither.
2. Execute the interactive protocol against candidate, frozen `0.10.0-rc.1`,
   and native baseline using matched conditions. A skipped explicit interview,
   ignored stop, unsafe delay, or unchanged advice across the paired facts is a
   regression to fix before more pilot use.
3. Run equal-information continuations to separate question-asking value from
   reasoning value. Preserve ties, failures, question burden, and incomplete
   episodes; do not judge length or polish as added value.
4. Use independent cases, calibrated reviewers, bilingual review, and the
   existing release gates before a superiority or production claim. Gather
   consented, anonymized alpha failure examples rather than private raw chats.

These steps use existing qualification ownership; they do not create another
framework expansion or waive any current gate.
