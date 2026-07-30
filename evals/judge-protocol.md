# Judge Calibration Protocol

Use human-calibrated pointwise scoring as the primary evaluation. Pairwise
preference is secondary because presentation order, verbosity, polish, and
assertive style can bias judgments.

## Roles

A stratified calibration subset requires:

- a method and safety reviewer;
- a practical usability reviewer;
- a fluent language reviewer for every Chinese or mixed-language case;
- an adjudicator for every hard-gate disagreement.

One person may hold more than one role only when independence and language
competence are documented.

## Blinding and randomization

- Remove condition labels, package names, branch names, and implementation
  metadata from responses.
- Randomize skill and no-skill order.
- Include order-swapped duplicates.
- Include length-matched and verbosity-manipulated probes.
- Score pointwise before revealing the paired response.
- Do not ask judges for private chain-of-thought. Require a short evidence quote
  or observable reason for each hard gate and dimension score.

## Calibration set

The calibration subset must cover:

- all four substantive routes;
- low-, medium-, and high-exposure cases;
- every leading mechanism and mandatory overlay;
- English, Simplified Chinese, and mixed-language cases;
- short and long responses;
- known hard failures, near misses, and acceptable alternatives.

Do not tune the runtime or public rubric against untouched qualification
holdouts.

## Agreement gates

Before using an automated judge for release evidence:

- weighted kappa or Krippendorff's alpha must be at least 0.80 for routes and
  hard-gate judgments;
- agreement must be at least 0.67 for naturalness and other subjective
  dimensions, followed by adjudication;
- the automated judge's hard-gate false-negative rate must be below 5% on the
  calibration subset;
- every disagreement involving safety, authority, privacy, cultural prediction,
  bilingual drift, or coercion must receive human adjudication.

If agreement falls below a gate, revise the rubric, examples, or judge prompt and
rerun calibration. Do not average away disagreement.

## Judgment record

Each judgment must contain:

```json
{
  "case_id": "...",
  "condition": "skill|no-skill",
  "judge_id": "pseudonymous-reviewer-id",
  "rubric_version": "2.1",
  "invocation_label": "...",
  "substantive_route": "...",
  "hard_gates": {"gate_id": false},
  "dimensions": {"dimension_id": 1},
  "evidence": {"item": "short observable reason"},
  "pairwise_preference": "skill|no-skill|tie|not_scored"
}
```

Do not store reviewer private notes, chain-of-thought, or identifying user data.

## Reporting

Report:

- agreement by label and dimension;
- confusion matrices;
- hard-gate false positives and false negatives;
- order-swap consistency;
- verbosity and style-probe results;
- adjudicated changes;
- judge prompt, model snapshot, and host version;
- calibration dataset hash.

A favorable automated-judge score without passing calibration is development
feedback, not release evidence.
