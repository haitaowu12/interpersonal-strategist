# Release Qualification

`release/qualification.json` is the canonical promotion record. The current
`0.8.0-rc.1` state is a production-qualification candidate, not a production
claim.

## Promotion rule

Production wording may be used only when:

- every required gate is `passed`;
- `status` is `qualified`;
- `production_claim_allowed` is `true`;
- `qualification_commit` equals the exact release commit;
- the release ZIP, prompt manifests, responses, judgments, source-resolution
  report, holdouts, bilingual review, and pilot evidence have recorded hashes;
- no unresolved hard-gate failure remains.

Static CI, a deterministic ZIP, or public development-case performance alone
cannot change the status.

## Evidence packages

Qualification evidence should be stored outside the distributable skill and may
be private when it contains sealed holdouts or privacy-controlled pilot data.
The public manifest may record cryptographic hashes, counts, protocol versions,
reviewer roles, aggregate results, and links to access-controlled artifacts.

Do not commit real conversations, identifying workplace records, confidential
attachments, or holdout answer structure.

## Release sequence

1. Merge and freeze the candidate.
2. Build the deterministic ZIP and record its SHA-256.
3. Verify source identities and registry parity.
4. Run clean-host discovery, explicit invocation, and reference-selection tests.
5. Calibrate human and automated judges.
6. Run blinded no-skill comparison.
7. Run independently authored untouched and adversarial holdouts.
8. Complete fluent English-Simplified Chinese review.
9. Run the privacy-safe controlled pilot.
10. Obtain independent release review.
11. Update the qualification manifest on a dedicated promotion PR.

A substantive runtime fix after steps 5-9 invalidates affected evidence and
requires a fresh qualification tranche.

## Failure handling

- Preserve raw failures in the internal qualification report.
- Classify root cause as routing, method selection, reference retrieval,
  generated wording, branch/control quality, bilingual function, judge error,
  host integration, or fixture defect.
- Add public synthetic regression cases without exposing private holdouts.
- Do not reuse a tuned-against holdout as untouched qualification evidence.
- Keep the release blocked until the affected gate is rerun.
