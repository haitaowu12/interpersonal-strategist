# Owner Review Packet: Interpersonal Strategist 0.11.0-rc.1

Status: **candidate verification passed; ChatGPT Pro lane unavailable because
exact SHA-bound approval was not received**

This packet supports review of draft PR
[`#7`](https://github.com/haitaowu12/interpersonal-strategist/pull/7).
It does not authorize merge, installation, implicit invocation, production use,
or an efficacy claim.

## Decision summary

- Keep `interpersonal-strategist`, `goutoujunshi`, and
  `personal-growth-copilot` as separate experimental products. Overlap is
  permitted.
- Keep all three products manual/explicit invocation only.
- Support user-controlled dossiers and numerical decision-fit scoring instead
  of categorically prohibiting them.
- Remove dedicated LGBTQ+ and non-monogamy product content while preserving
  identity-neutral support, equal consent and safety treatment, and the user's
  own relationship labels and agreements.
- Use community products only as commit-pinned pattern donors. Do not copy
  donor prompts, formulas, datasets, questionnaires, examples, scripts, or
  creator voice.
- Keep production qualification blocked until independent behavioral gates are
  executed.

## Candidate identity

| Item | Value |
|---|---|
| Version | `0.11.0-rc.1` |
| Baseline | `12b230be0e068cfae23acf28a8b438dd46a998cb` |
| Implementation branch | `codex/interpersonal-tailoring-evidence` |
| Locally audited implementation head | `32fcb4d9e362e23dc666471d8713d2d5cd297b4b` |
| Draft PR | `https://github.com/haitaowu12/interpersonal-strategist/pull/7` |
| Exact-head CI | pass, run `31431664788` |
| Package SHA-256 | `e0f9b16b352d346e1d1826cb61404664e1eb67696390fdca2cca325c7e1e0f18` |

The final PR head will differ when this packet and the Pro-lane record are
committed. Re-run the verification chain and verify the live PR head before
owner approval.

## Requirement-to-evidence matrix

| Requested outcome | Current evidence | Verdict |
|---|---|---|
| Separate products; overlap allowed | This PR changes only the `interpersonal-strategist` runtime. Installed `goutoujunshi` receives explicit-only catalog metadata only. No installed or registered `personal-growth-copilot` product was found. | Implemented |
| Manual invocation for all three | `skill/interpersonal-strategist/agents/openai.yaml` sets `allow_implicit_invocation: false`; `SKILL.md` requires explicit invocation; a regression test locks both. Installed `goutoujunshi/agents/openai.yaml` sets the same policy. The personal-growth candidate remains uninstalled and unregistered. | Implemented within available catalog surfaces |
| Scoring is a useful tailoring capability | `references/profiles-and-scoring.md` defines a bounded Decision Fit Score; `scripts/profile_score.py` calculates it deterministically; `assets/profile-score-template.json` supplies an inspectable input model. | Implemented |
| Dossiers are useful and user-controlled | The dossier contract separates user, counterpart, and relationship records; labels evidence classes; supports session-only or host-backed persistence; and defines inspection, correction, version, rollback, export, expiry, deletion, and memory-off behavior. | Implemented; host persistence remains host-dependent |
| Avoid false precision and misuse | Scores apply to a named decision rather than human worth. Unknowns are not imputed, coverage and confidence are separate, safety/deal-breaker flags sit outside the average, and vulnerability or manipulation dossiers are refused. | Implemented and regression-tested |
| Strengthen thin relationship knowledge | Fourteen new primary or authoritative records cover relationship processes, measurement, consent, safety, and personality limits. Each has a permitted claim, limitation, and runtime rule in both registry and ledger. | Implemented |
| Learn selectively from community products | Twelve repositories were inspected at exact commits with license posture, inspected paths, adopted patterns, rejected patterns, and security notes. No donor tool was run and no donor implementation was copied. | Implemented |
| Remove dedicated LGBTQ+/non-monogamy content | Active runtime, public fixtures, and current release surfaces contain no dedicated category, fixture, or positioning for those topics. The runtime still uses neutral terms and the user's own labels and agreements. | Implemented |
| Preserve consent, safety, privacy, and authority | Runtime invariants and hard gates continue to cover refusal, withdrawn consent, coercion, stalking, exploitation, intimate-media misuse, privacy invasion, retaliation, incapacity, and formal authority boundaries. | Implemented and regression-tested |
| Review-ready implementation and evidence | Research audits, source registry/ledger, provenance, fixtures, calculator tests, deterministic package, clean-install smoke evidence, this packet, and a draft PR are present. | Passed locally; Pro lane blocker recorded |
| No silent merge or production promotion | PR `#7` is draft. `release/qualification.json` remains `blocked` with `production_claim_allowed: false`. | Preserved |

## Verification evidence

The following checks passed against implementation head `32fcb4d9...` on
2026-08-10:

| Check | Result |
|---|---|
| Repository validator | pass, zero errors |
| Unit and mutation suite | 44/44 pass |
| Public fixture validator | pass, zero errors |
| Evidence registry/ledger parity | pass, 54 registered sources |
| Online identity resolution | 54/54 resolved in the qualification run |
| Deterministic package build A | SHA-256 `e0f9b16b...e1e0f18` |
| Deterministic package build B | identical SHA-256 |
| Clean archive install/discovery smoke | pass; `$interpersonal-strategist` discovered under `.agents/skills` |
| Exact-head GitHub CI | pass on `32fcb4d9...`, run `31431664788` |

Public fixtures are development regression evidence, not untouched holdouts or
proof of behavioral improvement.

## Community-pattern disposition

Adopted clean-room architecture:

- separate actor and relationship context;
- evidence source, date, contradiction, and update conditions;
- current-state versus history separation;
- user-visible correction, versioning, snapshots, rollback, export, expiry,
  and deletion;
- role and decision lenses instead of private-thought simulation.

Rejected:

- forced persistence, implicit activation, network checks, or autonomous
  persona behavior;
- inferred MBTI, attraction, loyalty, intent, private thought, or social power;
- arbitrary multipliers, probabilities, compatibility guarantees, and
  validation claims;
- pickup, compliance, resistance-pushing, deceptive withholding, or
  vulnerability/pressure-point tactics;
- raw transcript, media, identifier, credential, or intimate-data retention.

The exact repository, commit, license, inspected paths, and per-donor decision
are recorded in `research/scoring-dossier-community-audit-20260810.md`.

## Evidence boundary

The research supports using goals, reciprocity, responsiveness, reliability,
boundaries, consent, repair, and practical constraints as review prompts. It
does **not** validate the custom score, its weights, its bands, or predictions
about an individual relationship. The score is a transparent user decision
model, not a psychological test or outcome forecast.

See `research/relationship-evidence-review-20260810.md`,
`provenance/evidence-sources.json`, and
`skill/interpersonal-strategist/references/evidence-ledger.md`.

## ChatGPT Pro crosscheck

The scoped brief was prepared with SHA-256
`17f8e34ec13043f27fa18afdbf0e35f301b9403256e086a91acadc730753f4c0`, but the
required exact SHA-bound approval reply was not received across three goal
turns. The protocol therefore prohibited navigation, upload, and transmission.
No external data was sent, no fallback was used, and no Pro review is claimed.

The full blocker and resumable approval contract are recorded in
`external-feedback/chatgpt-pro-20260810-scoring-dossier-blocker.md`. A later
crosscheck must capture the visible Pro label, attachment and nonce receipt,
conversation URL, inspected scope, response, local classification, and any
re-verification. Pro output would remain advisory and would not replace local
evidence or owner judgment.

## Production qualification still required

Do not promote this release from `blocked` based on this packet. The remaining
required gates include:

- clean-host discovery and invocation in the target host;
- reference selection and compound-overlay behavior;
- calibrated no-skill comparison;
- independently authored untouched holdouts;
- at least 150 adversarial safety holdouts with zero hard failures;
- two-reviewer bilingual naturalness and status-fit review;
- judge calibration;
- a privacy-safe 10-20 episode controlled pilot; and
- independent release review bound to the exact release commit and package.

## Owner decision

After noting that the Pro review remains incomplete and the final exact-head
checks are present, choose one:

- approve the bounded candidate PR for merge while keeping qualification
  blocked;
- request a named correction; or
- reject/hold the candidate and identify the missing evidence.
