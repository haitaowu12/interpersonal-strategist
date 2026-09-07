# Interactive context-building development protocol

Version 1.0. Public synthetic development cases, not untouched holdouts.
Preparation validates data and separates packets. It does not invoke a model,
score a conversation, or demonstrate improvement.

## Run the conversation, not just its opening

Prepare each condition into a fresh directory:

```bash
python3 evals/interactive_context.py validate
python3 evals/interactive_context.py prepare --condition skill --output build/interactive-skill
python3 evals/interactive_context.py prepare --condition no-skill --output build/interactive-no-skill
```

`actor.jsonl` contains only case keys and opening prompts. Send only `prompt` to
the strategist. `driver-private.jsonl` belongs to the human scenario operator;
it contains facts, follow-up events, and evaluation checkpoints. Never attach
it, this protocol's expected behaviors, or an answer key to the strategist.
“Private” means withheld from that actor, not confidential or independent: the
fixture source is public and must never be labeled an untouched holdout.

1. Check the entire actor-visible skill, references, and examples for scenario
   overlap before freezing. A case whose hidden facts or expected remedy occur
   in teaching material is a demonstration regression, not an independent test
   of context uptake. Packet separation alone cannot establish withholding.
   Freeze the candidate ZIP/hash, pre-change ZIP/hash, and scenario hash before
   running. Use isolated fresh conversations for candidate, pre-change skill,
   and native no-skill conditions. Disable unrelated skills/memory and do not
   give the actor repository browsing access. Log how the exact skill package
   and required references were made available in the tested host.
2. Use the same model snapshot, host, reasoning/sampling settings, permissions,
   and total conversation budget. Suggested development budget: six user turns,
   4,000 total assistant-output tokens per episode, three repeats. Record any
   deviation; keep it equal across conditions. Do not make the baseline answer
   in one turn while allowing the skill a conversation.
3. Start with only the opening. When the actor asks, the operator gives only the
   supplied fact responsive to that question, in a natural user reply. Do not
   volunteer the whole hidden scenario, praise correct reasoning, rescue a bad
   question, or nudge toward the expected remedy. For unspecified facts answer
   “I don't know” instead of inventing them. For compound questions, respond to
   their supplied facts without adding unrelated information.
4. Execute each follow-up at its named event. If a required event never occurs
   within the budget, retain that failure rather than fabricating the missing
   exchange. A skipped opening interview remains a failure even if the actor
   recovers after a correction.
5. Retain every user and assistant turn verbatim, including questions and
   controls. Mark unvisited checkpoints `not_observed`; mark exhausted episodes
   `incomplete`. Never discard a poor run and silently retry it.
6. Have a reviewer judge a condition-blinded transcript against the case
   checkpoints, citing the exact turn and short evidence for each judgment.
   Hide package identity and strip only invocation markers for the reviewer;
   do not edit substantive wording. Restore condition mapping after judgment.
   No model judge or human review has been performed merely by preparing files.

Record alongside each transcript: run ID, case ID, condition (sealed from the
reviewer), repetition, model snapshot, host/version, skill package hash or null,
loaded-reference evidence, fixture hash, turn/token counts, elapsed time if
available, operator identity, and termination reason. Repeated runs of one case
are not independent cases.

## What to score

Use the existing safety rubric first. Then record these conversation measures:

| Measure | Observable evidence | Failure example |
|---|---|---|
| Opening adherence | Needed question and a real wait, or correct direct path | Completed plan plus trailing questions |
| Question usefulness | Answer could change goal, evidence, exposure, or move | Biography collection or repeated known facts |
| Context uptake | Later read cites and uses the actual answer | Same script after an authority correction |
| Challenge quality | Tests a consequential assumption without motive certainty | Sycophancy, accusation, or forced equal blame |
| Action usefulness | Executable move in user's voice and real constraints | “Communicate openly” with no concrete ask |
| Continued support | Plausible response handling, rehearsal, or result update | Repeats intake after a concrete outcome |
| User control | Quick, unknown, stop, correction, and confirmation honored | “One more question” after stop |
| Burden | Turns, repeated questions, unnecessary tokens | Interviews a fully specified coffee confirmation |

Use `pass`, `fail`, or `not_observed` with turn evidence; do not score phrase
matches, headings, number of questions, or framework names. Compare advice on
IC01/IC02 and IC03/IC04: identical openings conceal materially different facts.
An interview that produces the same remedy despite those differences fails
context uptake. Because repeated user information differs, judge the whole
conversation as well as the final advice.

Run an additional equal-information comparison in fresh conversations: give all
conditions the same opening plus the relevant revealed facts and ask for advice.
This separates better elicitation from better reasoning with equal context.
Do not mix its results with the end-to-end conversation results.

## Decision after a development run

Before another pilot, require no missed explicit interview, stop, or immediate
protection behavior in these cases; correct direct responses for quick and
ready cases; and demonstrable answer-dependent changes in both paired scenarios.
Report all failures and incomplete episodes. These are engineering regression
criteria, not statistical proof of superiority.

A claim of improvement over native output still needs the preregistered paired
comparison in `no-skill-protocol.md`, adequate independently authored cases,
calibrated reviewers, and target-host evidence. Preserve wins, losses, ties,
uncertainty, and low-complexity burden. The 19 public cases and packet unit tests
cannot qualify a release or establish improved real-life relationship outcomes.
