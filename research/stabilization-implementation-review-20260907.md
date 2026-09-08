# Stabilization implementation review — 2026-09-07

Subject: `0.13.0-alpha.1`, based on main
`d1acd2dbbcf6808cd8f9bf221486bfd7682abe89`.
This is a source and infrastructure self-review, not independent behavioral or
production qualification. The implementation PR and CI identify the final
remote commit. Local snapshot commit identities are not release receipts.

## Finding closure

| Finding | Implemented change | Executable evidence |
|---|---|---|
| Contradictory counterpart-record policy | One scoped-record content policy plus the memory consent/capability contract; session-only default | Policy and host-capability assertions in `tests/test_stabilization.py`; compound public development case |
| Favorable score from sparse data or an active blocker | Status-first schema 1.1; headline withheld for blockers, unknown critical facts and partial models; sensitivity bounds and coverage; no favorable bands | One-of-eight, full-score blocker, unknown critical, noncritical partial, legacy input and malformed-input tests |
| Missing planned cases reported as complete | Frozen hashed run plan; every expected run accounted for; missing/failed/excluded runs preserved | Missing whole pair, unplanned/duplicate run, frozen-field tampering and no-plan tests |
| Pooled/missing classification labels | Per-condition metrics with missing eligible labels counted | Condition and denominator regressions |
| Degenerate win-rate bootstrap | Exact one-sided Clopper–Pearson bound over independent family votes; ties/repeats retained | Boundary, monotonicity, invalid-count and family-clustering tests |
| Hash declarations mistaken for evidence | Actual private evidence index, safe paths, byte hashes, current package parity, reconstructed run plan, blinding linkage, raw-review metric recomputation and receipts | End-to-end synthetic bundle plus missing files, tampering, stale package and dishonest recomputed-count tests |
| No bounded execution or blinding path | Opt-in trusted host-adapter runner, batch/time/output bounds, fail-stop, resume without silent retries; neutral judge packets and reversible private mapping | Dry-run, timeout, oversized output, process cleanup, blinding round-trip and stale-rubric tests |
| Satisfaction and sophistication substituted for benefit | Agency/correction/rumination guidance, short-prompt and context ablations, formative pilot outcomes and adverse-event workflow | Twelve public agency cases; pilot/runbook materials. Actual user benefit remains untested |
| Maintenance rewards feature volume | Method identifiers must be unique and nonempty; method/playbook count is not a quality target | Static validation retains required safety/content checks without requiring a larger inventory |

## Checks executed locally

- Python compilation and repository/release validation: pass.
- Offline source registry: 57 records, parity validation pass. This is not an
  online resolution receipt.
- Canonical, persona, relationship and interactive fixture validation: pass.
- Unit and mutation suite: **88 tests passed**.
- Five canonical prompt conditions: **224 records each** prepared; these are
  public development records, not independent holdouts.
- Frozen two-condition plan and default no-call execution path: pass; no model
  response file was produced.
- Repeated package builds produced identical ZIP bytes; package layout smoke
  and checksum validation passed. Layout smoke is not live host invocation.
- Exact-binomial implementation independently compared to the installed SciPy
  beta quantile on all counts for n = 1, 2, 10, 30, 100 and 150; numerical parity
  checked. SciPy is not a project dependency.
- Diff whitespace validation: pass.

Runtime ZIP SHA-256:
`76da30328bb7dc8744ba807a0f7fc8f7909101a4bb1070bb909ad21341bf17e1`.

The full-bundle fixtures are explicitly synthetic. Their passing result shows
that the verifier checks a consistent evidence chain and detects selected
mutations; it does not authenticate people, reviewer independence, actual host
behavior, or scientific truth. They are never release evidence.

## Release disposition

Mergeable as a development stabilization subject after remote CI passes.
`release/qualification.json` remains **blocked**, with production claims disabled
and all 13 gates pending. No paid model evaluation, live clean-host trial,
independent untouched holdout, fluent human review, controlled real-user pilot,
or independent release approval is claimed as completed.

The next execution is defined in `release/QUALIFICATION-RUNBOOK.md`, with private
record schemas, pilot consent/outcomes, and a host capability matrix. Do not
rename this alpha production-ready, enable persistence without capability
receipts, loosen thresholds to obtain a pass, or treat generated test cases as
independently authored evidence.
