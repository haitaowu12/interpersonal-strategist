# ChatGPT Pro Architecture Crosscheck

Date: 2026-07-29
Mode: architecture review
Model surface: ChatGPT Pro
Conversation: https://chatgpt.com/c/6a6ab689-3868-83ea-a3d5-1cbe79a29b06
Outgoing brief SHA-256:
`06b24dd6ca8b1285b26b0f18d5b6860f0db57e9a4eae28d2ead1172473748cc0`

The external review was advisory. Recommendations below were checked against
the current official Codex manual and the local implementation before use.

## Apply

- Release only as explicit-invocation, manual-install, instruction-only alpha.
- Use `$HOME/.agents/skills/interpersonal-strategist` and
  `<repo>/.agents/skills/interpersonal-strategist` as current documented Codex
  locations.
- Ship a single top-level `interpersonal-strategist/` directory with exactly
  one `SKILL.md`, legal notice, minimal `agents/openai.yaml`, and directly
  linked references.
- Keep scope, privacy, anti-coercion, prompt-injection, output-mode, bilingual,
  escalation, stopping, and authority controls in `SKILL.md`.
- Keep runtime free of scripts, connectors, network dependencies, persistence,
  and tool declarations.
- Add Power-Reversibility-Exposure, Priority-Ownership-Cost, expectation
  contracts, factual contribution records, proportional attribution
  correction, first-class no-action/document/escalate/exit choices, functional
  bilingual drafting, and outcome-independent evaluation.
- Constrain alternative interpretations to plausible, evidence-linked readings;
  do not manufacture false symmetry.
- Treat quoted or attached material as untrusted evidence rather than
  executable instructions.
- Add repository `SECURITY.md`, distributable `LICENSE` and `NOTICE.md`,
  deterministic ZIPs, an internal path-and-byte manifest, and a sidecar archive
  hash.
- Narrow public claims: deepest alpha coverage is workplace/project power,
  workload, credit, boundaries, and bilingual pragmatics.

## Consider

- Expand to a 40-case behavior set with at least 12 mirrored bilingual pairs
  before a public readiness claim.
- Add signed tags or another publisher-authentication mechanism after the
  reproducible build is stable.
- Add plugin packaging later if distribution changes from manual skill
  installation to broader discoverability.
- Retain a private independently authored holdout set after the public
  development suite is frozen.

## Reject

- Do not publish `$CODEX_HOME/skills` or `~/.codex/skills` as the sole current
  installation contract.
- Do not include runtime Python, eval runners, source archives, vault paths, or
  generated history in the installable ZIP.
- Do not put controlling safety rules only in an optional reference.
- Do not add personality scores, manipulability labels, secret social graphs,
  motive certainty, current-law content, universal scripts, forced public
  correction, or outcome-based grading.
- Do not claim full bilingual or domain parity without behavior evidence.

## Needs user decision

- License: MIT selected as the permissive alpha default.
- Distribution: manual-install standalone Codex skill selected for this alpha;
  plugin packaging deferred.
- Artifact policy: chat-only output selected for this alpha.
- Public evaluation: public synthetic development fixtures plus future
  independently controlled holdouts.

## Applied locally

- Corrected install paths and scope claims in `README.md`.
- Added host-boundary and untrusted-content rules to `SKILL.md`.
- Added license, notice, security, provenance, deterministic validation,
  packaging, clean-install smoke testing, and release checksums.
- Kept the packaged runtime instruction-only and explicit-only.

## Remaining verification

- Independent behavior runs over the expanded public development suite.
- Twelve or more human-reviewed bilingual mirror pairs.
- Fresh untouched holdouts after instruction freeze.
- Clean discovery and invocation in fresh Codex CLI, IDE, and desktop sessions.
- Controlled pilot before any production-readiness claim.
