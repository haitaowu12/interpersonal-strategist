# Development baseline: 0.12.0-alpha.1

The owner requested closure and merge of the open PRs and a clean baseline on
2026-09-07. This authorizes merging the reviewed development work and syncing
the local source. It does not change the production qualification contract.

## Included work

- PR #7: user-controlled user, counterpart, and relationship records; a bounded
  Decision Fit Score; calculator, misuse tests, and source provenance.
- PR #8: context readiness at entry, a real question-and-wait interview,
  answer-linked advice, rehearsal and outcome updates, and quick/urgent paths.
- Combined development suite: 54 unit/mutation tests and 19 interactive cases.
- Independent source review and finding closure are recorded in
  [the review](../research/context-first-run-20260907/review.md).

The reviewed runtime ZIP SHA-256 is
`819c80a860005b19d9bb0acf061e5eef987299dfa60f28582f7611d0f7b2a738`.
Documentation-only baseline closure leaves those runtime bytes unchanged.
Use the merged PR records and CI provenance to identify the resulting commit;
squash integration changes commit identity without changing the reviewed tree.

## Historical records

Earlier owner packets and integration notes describe their state at creation,
including draft status and then-unavailable write permission. The owner's new
merge request supersedes those development-merge holds. Those records remain
as evidence of earlier work; they are not current checkout or installation
receipts. The unavailable ChatGPT Pro review is not represented as completed.

## Remaining production work

`release/qualification.json` remains `blocked`, with
`production_claim_allowed: false`. Its pending gates must be completed against
one frozen subject before a separate promotion PR:

1. Capture exact model/host identity, clean-host explicit invocation, reference
   selection, and package/CI/source-resolution receipts.
2. Run a calibrated comparison against the same model without the skill and
   independently authored, untouched holdouts. Public cases and teaching
   examples cannot serve as untouched evidence.
3. Complete the specified adversarial safety cases, two-reviewer bilingual
   assessment, and judge calibration with their existing acceptance thresholds.
4. Complete the consented, privacy-safe 10–20 episode pilot and independent
   release review; preserve failures and corrections.

The synthetic development conversations demonstrate bounded ask/wait/update
behavior. They do not establish superiority over native OpenAI responses or
real-world social outcomes. See the
[qualification handoff](CODEX-PRODUCTION-QUALIFICATION.md) for execution details.
