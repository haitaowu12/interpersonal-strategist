# Release and qualification

Current version: `0.13.0-alpha.1`. This is a stabilized experimental candidate,
not a supported production release or a claim of improved social outcomes.
`qualification.json` remains the canonical blocked promotion record.

The [execution runbook](QUALIFICATION-RUNBOOK.md) defines the next bounded cycle;
the [pilot kit](PILOT.md) defines consent, outcomes, and stopping. Host capability
claims are limited by [host-capabilities.json](host-capabilities.json).

## What may ship, and what may be claimed

A development PR may merge when source review, regression checks, deterministic
packaging, and layout smoke tests pass. Those checks do not authorize a
production claim. A downloadable prerelease may be marked experimental only;
clean-host behavior must still be measured before claiming host compatibility.

A production promotion requires every existing required gate to pass against
one unchanged subject, actual evidence bytes, independent review, and zero
unresolved hard failures. Human and behavioral gates are not replaced by new
unit tests, generated fixtures, scripted mock adapters, or receipt templates.
Do not loosen thresholds because the candidate fails them.

## Freeze one subject, not a moving branch

Use the immutable candidate commit, its tree, the ZIP hash, exact model and host,
rubric and harness versions. Keep the runtime frozen during qualification.
A later metadata-only promotion can point to that already-qualified candidate;
it cannot claim that a different runtime was evaluated. Rebuild and compare
package bytes, and retain the candidate object in release history. Do not try to
embed a commit's own not-yet-existing hash into itself.

Private evidence belongs outside the repository. Set
`INTERPERSONAL_EVIDENCE_INDEX` to its local index during promotion validation.
`scripts/verify_evidence_bundle.py` checks actual artifact hashes and paths,
package/source parity, frozen-run completeness, blinding identity, receipts,
comparative statistics, and adjudicated review-record counts. Hash identity and
consistent records cannot establish reviewer independence or source truth.

A metadata-only promotion still needs access to the evidence. Public CI cannot
verify absent private files and must not bypass this check. Run qualification in
a controlled environment with read-only evidence access and publish only the
redacted report and cryptographic receipts. Ordinary blocked-alpha CI requires
no private data or model credentials.

## Maintainer operations

Use one PR per bounded stabilization slice. Keep static checks in CI; run paid
model evaluations only against a frozen candidate with an explicit run budget.
Do not repeatedly review or repair until a desired score appears. Preserve a
failure, classify it once, fix a reproducible cause, and use fresh holdouts for
any tuned behavior. Existing public fixtures remain regression tests.

For a model/host/runtime change, record which claims and tests it invalidates.
Recheck routing, reference reads, quick/interview/stop behavior, scores, memory,
and the relevant comparison before renewing compatibility claims. A new source
citation alone does not establish new behavior.

For a reported harmful output or privacy issue: stop the affected feature or
version, record a private minimal incident, assess scope, correct or withdraw the
claim/package, add a synthetic regression, and publish a redacted disposition.
Deletion requests need storage-specific receipts. No response-time or support
service level is promised without an assigned operator.

Before wider public distribution, the owner must assign a maintainer, safety
reviewer, fluent reviewers, pilot coordinator, and a working private reporting
route. Roles are required; no named independent reviewers are claimed here.
