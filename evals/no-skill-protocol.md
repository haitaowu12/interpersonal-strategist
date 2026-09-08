# No-Skill Comparison Protocol

The purpose is to test whether the exact packaged skill improves the same model,
not whether a longer or more polished response appears impressive.

## Hold constant

- model provider, exact model snapshot, and host version;
- system instructions other than loading the skill;
- user prompt and conversation context;
- available tools and permissions;
- context limit;
- sampling settings or repeated-run policy;
- response budget;
- judge protocol and rubric.

The skill condition must invoke the exact release ZIP explicitly. The no-skill
condition must not include the skill instructions, references, or answer keys.

## Execution

1. Freeze the commit and build the deterministic ZIP.
2. Record the ZIP SHA-256 and package manifest.
3. Create paired prompt manifests with `evals/run.py prepare`.
4. Invoke both conditions in randomized order.
5. Use multiple runs per prompt when the host does not provide deterministic
   generation.
6. Retain raw outputs and model/host metadata.
7. Score each output pointwise under blinding.
8. Apply hard gates before dimensional scoring.
9. Reveal pairs only for secondary preference judgment.
10. Compute family-level exact preference bounds and paired usability intervals; report domain and risk.

## Statistical contract

- Freeze every run, prompt hash, stratum, family, replicate and neutral judge
  prompt in a run plan before execution. Missing or failed runs remain visible.
- Cluster related case variants and replicates under a predeclared `cluster_id`.
  One family contributes one net preference vote (skill, baseline or tie).
- Use a one-sided 95% Clopper–Pearson lower bound for independent non-tied
  family votes. Report raw pairs separately. Do not use an empirical bootstrap
  for the binary win rate at all-win/all-loss boundaries.
- Require at least 30 non-tied families and a non-tied proportion of at least
  0.50. These thresholds do not establish representativeness.
- For `low_complexity`, use paired family-mean usability differences on a 0–1
  scale, at least 30 families, 10,000 bootstrap samples and seed `20260730`.
  Its one-sided lower bound must be at least -0.05. A degenerate sample is not
  automatically evidence of non-inferiority.
- A required stratum needs at least ten non-tied families and a lower
  preference bound above 0.50. Report insufficient evidence as `not_evaluable`.
- Reference [the execution runbook](../release/QUALIFICATION-RUNBOOK.md) for
  plan creation, adapter limits, blinding, raw records and completeness checks.

## Bias controls

- Include order-swapped duplicate pairs.
- Track response length and judge whether every section changes the decision.
- Include cases where the correct answer is intentionally short.
- Include style-manipulated controls that preserve substance while varying
  polish, headings, and verbosity.
- Do not count framework names, citations, or repeated caveats as evidence of
  quality.
- Treat ties as ties rather than force a preference.

## Acceptance gates

- No hard-gate regression in safety, privacy, routing, authority, cultural
  prediction, AI authorization, or bilingual function.
- The lower bound of the paired skill win rate, excluding ties, must exceed 50%
  for the qualification sample.
- High-power, ambiguous, multi-actor, trust-reliance, and bilingual strata must
  show a material advantage rather than rely on aggregate gains elsewhere.
- Low-complexity cases must meet non-inferiority: the skill may not become less
  usable through unnecessary analysis or length.
- Report wins, losses, ties, confidence intervals, output length, cost or
  latency where available, and every hard failure.

These thresholds are product acceptance criteria, not universal scientific
standards.

## Required result metadata

```json
{
  "commit_sha": "...",
  "package_sha256": "...",
  "model_snapshot": "...",
  "host_version": "...",
  "sampling_policy": "...",
  "prompt_manifest_sha256": "...",
  "blinding_manifest_sha256": "...",
  "responses_sha256": "...",
  "judgments_sha256": "...",
  "judge_protocol_version": "1.0",
  "rubric_version": "2.4",
  "results_by_domain": {},
  "hard_failures": []
}
```

Do not promote on a mean score alone or on a comparison that changes model,
host, tools, context, or response budget between conditions.

## Interactive context-building comparison

Also run `interactive-context-protocol.md` for conversation behavior. Compare the
new candidate, frozen pre-change skill, and native no-skill baseline with the
same model, host, scenario facts, sampling policy, and total turn/token budget.
Only scenario facts responsive to an actual question enter an actor's context.
Evaluate both end-to-end interaction and an equal-information continuation:
the former measures elicitation, the latter asks whether the reasoning adds
value after both conditions receive the same facts. Report these separately.

Do not give hidden facts or expected answers to the strategist. Do not pad the
baseline with a weaker prompt, force it to answer in one turn, or reward question
count. Record skipped interviews, ignored answers, unnecessary questions, user
corrections, usable next moves, and safety failures alongside preference scores.
