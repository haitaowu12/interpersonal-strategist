# Context-first sidekick integration

Candidate `0.12.0-alpha.1`, based on development head
`c34f9840de172d9b2acff605cdbdfc4828d15789` of draft PR
[#7](https://github.com/haitaowu12/interpersonal-strategist/pull/7).
Branch: `improve/context-first-completion`.

## Result and scope

The first-pass review missed the open development PR and used `main` only.
This integration corrects that source selection: it preserves PR #7's governed
user/counterpart/relationship records, Decision Fit Score, calculator and
fixtures, source additions, explicit invocation, and user-control boundaries.
The earlier `0.11.0-alpha.1` packet is superseded; it must not replace the newer
profile/scoring work.

The new entrypoint makes incomplete context trigger a real interview and wait
before strategy. It connects context, assumption testing, a shared read, a
fact-linked next move, natural wording, optional rehearsal, and outcome updates.
Quick requests, sufficient context, stop/correction, and urgent protection keep
separate paths. Persistent memory and scoring remain optional and user-controlled.

## Development evidence

[Conversation records](context-first-run-20260907/conversations.json) contain
38 verbatim user/assistant turns from eight synthetic conversation threads.
[The execution record](context-first-run-20260907/agent-execution.json) binds
runtime file hashes, packages, attempts, and limitations. They are native
subagent observations under explicit source-isolation instructions. They are
not clean-host ChatGPT alpha tests, calibrated comparisons, or human outcomes.
Exact underlying model snapshot and tool-read attestation were not exposed.

| Observation | Result | Limit |
|---|---|---|
| Initial sparse work opening | First candidate asked and waited; frozen `0.10.0-rc.1` and unassisted condition drafted immediately | Single opening comparison; candidate scenario overlapped teaching material; not superiority evidence |
| Integrated work, friendship, Chinese cases | Questions, answer-linked updates, usable advice, and Chinese stop transition observed | Original examples exposed these cases; classified as instruction-seen smoke evidence |
| Quick then urgent-safety continuation | No optional intake in quick mode; immediate protective help despite “grill me” in urgent follow-up | One continuing thread, before the later example-only repair |
| Reviewer-authored household-device case after repair | Asked, waited, updated from employer ownership and retained bill access, then proposed a practical household routine | One unblinded development conversation; no matched comparator or general efficacy inference |

The fresh case did not demand a password, suggest access circumvention, invent
urgency, or equate an employer-device restriction with coercive control. The
user's answers changed the interpretation and the eventual message. These are
specific observations, not proof of real-world relationship improvement.

## Independent review and repair

The read-only reviewer found no supported high-severity runtime regression and
confirmed preservation of profile/scoring and relationship safeguards. It found
one material evaluation-design defect: some hidden fixture facts were also in
the required runtime examples. JSON packet separation did not prevent that leak.

Resolution:

- replace the overlapping examples with a distinct community-fundraiser
  teaching conversation;
- require source-wide teaching-material overlap review in the protocol;
- retain and explicitly label the affected runs, rather than deleting or
  presenting them as independent evidence;
- execute a new reviewer-authored household scenario with private facts
  delivered only in response to actual questions;
- add that scenario as IC19 for future public development regression use.

The previously missing link to this integration record is now resolved.
[Review record](context-first-run-20260907/review.md) records the review boundary
and the targeted follow-up disposition.

## Verification boundary

The combined candidate has 54 unit tests, 19 interactive fixtures, and the
existing broad routing, persona, relationship, memory, profile, and scoring
lanes. Package validation excludes generated Python cache using PR #7's fix.
Exact command results are preserved in the handoff validation record and hosted
CI, once publication completes. Do not infer model behavior from structural CI.

The final skill ZIP SHA-256 is
`819c80a860005b19d9bb0acf061e5eef987299dfa60f28582f7611d0f7b2a738`.
The fresh recovery conversation used these exact runtime package bytes.

## Remaining completion conditions

Source integration and development verification can be completed in this task;
production qualification cannot be asserted from these observations. The
canonical `release/qualification.json` remains blocked. Its required target-host
invocation/reference behavior, adequately powered calibrated no-skill comparison,
independent untouched holdouts, adversarial safety set, bilingual human review,
judge calibration, controlled privacy-safe pilot, and independent release review
still require actual evidence. Online evidence resolution remains governed by
that manifest; old successful reports are not silently promoted to current gates.

Original local checkout and installed skill locations are outside this task's
writable roots. The integrated branch and package are prepared through an
isolated writable clone; this does not update the installed runtime. GitHub
publication, merge, local synchronization, installation, and qualification are
separate states. The earlier draft PR's release gates remain in force.
