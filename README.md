# Interpersonal Strategist

`interpersonal-strategist` is a stateless Codex skill for workplace and
everyday interpersonal decisions. It helps users separate evidence from
interpretation, map power and constraints, test alternative readings, choose a
proportionate action, and prepare language with response branches and stopping
rules.

The alpha's deepest scenario coverage is workplace and project power,
workload, credit, boundaries, and bilingual pragmatics. Its general method also
supports non-romantic everyday cases, but equal depth across every listed
social domain is not yet claimed.

Current release: `0.6.0-alpha.1`

This is a new standalone lineage. It does not claim to reproduce the unavailable
historical `v0.5a` candidate.

## What it covers

- managing up and down;
- workload, scope, priority, and refusal;
- credit, visibility, sponsorship, and exclusion;
- feedback, conflict, repair, and boundaries;
- difficult friendship, family, roommate, neighbor, and networking situations;
- English and Simplified Chinese workplace communication.

It does not provide romance or intimacy strategy, psychological diagnosis,
coercive tactics, or substantive legal, HR, medical, crisis, or emergency
determinations.

## Install in Codex

Codex officially scans user skills from `$HOME/.agents/skills` and repository
skills from `.agents/skills` directories.

User-wide installation:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R skill/interpersonal-strategist "$HOME/.agents/skills/"
```

Repository-scoped installation:

```bash
mkdir -p .agents/skills
cp -R /path/to/interpersonal-strategist/skill/interpersonal-strategist .agents/skills/
```

Then invoke:

```text
$interpersonal-strategist
```

The alpha is explicit-only. If Codex does not show a newly installed skill,
restart Codex.

Official background: [Build skills](https://learn.chatgpt.com/docs/build-skills.md).

## Validate

Requires Python 3.11 or newer and no third-party packages.

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/smoke_install.py
```

## Build a deterministic release

```bash
python3 scripts/package.py
```

This creates:

```text
dist/interpersonal-strategist-0.6.0-alpha.1.zip
dist/interpersonal-strategist-0.6.0-alpha.1.zip.sha256
dist/interpersonal-strategist-0.6.0-alpha.1.manifest.json
```

The ZIP contains one directly installable `interpersonal-strategist/`
directory, including its license, notice, and internal package manifest. The
sidecar manifest records every packaged path, byte count, and SHA-256.
Packaging excludes repository tests, research notes, and private artifacts.

Verify the sidecar from the directory containing the release files:

```bash
cd dist
shasum -a 256 -c interpersonal-strategist-0.6.0-alpha.1.zip.sha256
```

## Project structure

```text
skill/interpersonal-strategist/  distributable skill
evals/                           synthetic development and routing cases
scripts/                         validation, packaging, and install smoke
tests/                           deterministic repository tests
provenance/                      source identity and clean-room boundaries
external-feedback/               saved advisory reviews
dist/                            generated release artifacts
```

## Release status

`0.6.0-alpha.1` is suitable for explicit local evaluation. It is not yet
claimed as behaviorally production-ready. Promotion requires independent
English-Chinese review, fresh behavior tests, untouched holdouts, and a
controlled private pilot.

## Research and development

The current boundary audit and proposed mechanism-driven v0.7 expansion are
documented in
[`research/v0.7-targeted-rd-20260729/`](research/v0.7-targeted-rd-20260729/README.md).
This is a recommendation package; it does not change the installed alpha.
