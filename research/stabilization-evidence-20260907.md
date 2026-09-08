# Stabilization evidence and reuse decisions — 2026-09-07

This is an implementation rationale, not an independent review or a completed
behavioral evaluation. Promoted entries are in the source registry and runtime
ledger; older registry sources retain their own verification dates.

| Source | Bounded use here |
|---|---|
| Cheng et al., Science (26 March 2026), [DOI 10.1126/science.aec8352](https://doi.org/10.1126/science.aec8352), [PMID 41886588](https://pubmed.ncbi.nlm.nih.gov/41886588/) | Separate validation of feelings from endorsement; measure agency and correction apart from satisfaction. See AGENCY-01. |
| Eyal et al. (2018), [DOI 10.1037/pspa0000115](https://doi.org/10.1037/pspa0000115) | Use attributed information, not confident simulation of private thoughts. See PERSPECTIVE-01. |
| Argyle et al. (2023), [DOI 10.1073/pnas.2311627120](https://doi.org/10.1073/pnas.2311627120) | Support optional wording changes without changing the user's substantive position. See AICOMM-01. |
| Ibrahim et al., [arXiv:2605.07912v3](https://arxiv.org/abs/2605.07912v3), revised 21 June 2026 | Provisional longitudinal evidence motivates follow-up on reliance and real-world satisfaction. A preprint, not promoted as settled evidence or a release identity-resolution result. |
| [SciPy exact binomial interval documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html) | Independent reference for Clopper–Pearson interval behavior. Implemented with Python's standard library; SciPy is not a runtime dependency. |

No study validates this package or its custom scores. One-sided accounts,
self-report outcomes, context differences, and human/model changes limit
transfer. Source identity resolution is necessary but does not establish
applicability or causal benefit for this product.

## Community pattern disposition

Keep the existing pinned [Waza secondary lane](../evals/waza/README.md). It is
not target-host qualification. The new plan, bounded adapter and blinding tools
use the existing canonical fixtures, not a second incompatible evaluation stack.

Use the already-reviewed SOTOPIA/Concordia patterns for scenario families and
separate actor/evaluator knowledge; use HiddenBench's information-gap pattern
in the existing interactive and equal-information protocols. These are design
references, not imported production dependencies or executed donor benchmarks.
The repository's prior exact-commit audits remain the provenance source.

Borrow the limited practice pattern of original wording, proposed wording,
reason, then one rehearsal target. Reject global communication/person scores,
unsupported emotion decoding, pressure tactics, blanket hedge deletion, and
automatic transcript or memory imports. Do not merge a donor merely because
its README advertises overlapping features or positive outcomes.

New runtime and evaluation code is original. No donor code, prompts, datasets,
licensed course text or raw research papers are redistributed. A future concrete
integration must pin its version, inspect the actual license and data rights,
pass a narrow adapter test, and retain privacy and qualification boundaries.
