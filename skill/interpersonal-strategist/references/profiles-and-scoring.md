# User-Controlled Profiles and Decision Fit Scoring

Use this reference when the user asks to create, update, compare, score, review,
remember, correct, export, roll back, or delete a profile about themselves,
another person, a relationship, a stakeholder, or an interpersonal option.

The product supports dossiers and numerical scoring. Treat them as inspectable
decision aids, not objective truth about a person.

## Start with user control

Before creating or materially expanding a persistent dossier, establish:

- the user's decision or support purpose;
- the actor or relationship scope;
- whether the record is session-only or persistent;
- an alias or role to use;
- the minimum source material needed;
- sensitive fields that must not be retained;
- the first review or expiry event.

Do not silently create a profile, infer that persistence is wanted, or claim a
write succeeded unless the host confirms it. If the host has no persistence,
offer the dossier as a copyable block and say that it has not been saved.

Honor `memory off` immediately. With memory off, the current response may use
provided context but must not write, update, or broaden a dossier.

## Keep three records distinct

### User profile

Record the user's own confirmed information:

- goal, priorities, values, boundaries, and deal-breakers;
- communication preferences and accessibility needs;
- resources, dependencies, deadlines, and downside exposure;
- relationship history needed for the current decision;
- optional self-descriptions such as Big Five or MBTI, marked `user-supplied`;
- preferred score dimensions and weights.

### Counterpart profile

Record only decision-relevant information about the other person:

- role or alias and relationship to the user;
- their directly stated preferences, boundaries, decisions, and commitments;
- dated observable behavior and material patterns;
- interpretations labeled as hypotheses;
- counterevidence, contradictions, and unknowns;
- current access, authority, dependency, and contact constraints;
- source, freshness, confidence, and next update condition.

Do not add a vulnerability, pressure-point, sexual-preference, medical,
credential, secret-location, surveillance, or manipulation field. Do not infer
personality, diagnosis, attachment, MBTI, attraction, honesty, or consent from
photos, avatars, body movement, voice, punctuation, emoji, or response time.

### Relationship or decision record

Record the shared context without collapsing the two people:

- relationship type as the user describes it;
- current state and decision to make;
- timeline of material events;
- agreements, commitments, refusals, boundaries, and open loops;
- support, burden, reciprocity, conflict, repair, and trust evidence;
- power, money, housing, work, caregiving, reputation, and safety exposure;
- options, score snapshots, selected action, review point, and stop conditions.

In multi-actor cases, keep one actor card per person. Do not merge one person's
statement, motive hypothesis, score, or boundary into another person's record.

## Use an evidence-labeled dossier schema

```markdown
# Interpersonal Dossier: [alias or role]

Profile ID: [stable alias]
Version: [number]
Created: [date]
Last updated: [date]
Review or expiry: [date or event]
Mode: session-only | persistent
Purpose: [decision this supports]
Scope: [people and relationship context]
Sensitive exclusions: [what must not be stored]

## User priorities
- [confirmed priority, weight, source/date]

## Counterpart and context
- Fact/report: [content, source/date]
- Observation: [content, source/date]
- Hypothesis: [content, evidence, counterevidence, confidence, update condition]
- Unknown: [question and materiality]

## Relationship timeline and commitments
- [date, event, source, status]

## Decision Fit Score snapshot
- Purpose and dimensions: [...]
- Score: [0-100 or not calculable]
- Coverage: [percentage and dimensions missing]
- Confidence: low | moderate | high
- Deal-breaker or safety flag: none | present: [...]
- Interpretation: [...]

## Current strategy
- Recommendation: [...]
- Branches: [...]
- Review point: [...]
- Stop condition: [...]

## Correction history
- [date, prior entry, correction, source, affected score/version]
```

Use plain Markdown or an equivalent inspectable host format. Do not hide a
parallel internal profile from the user.

## Separate evidence classes

Label each material entry:

- **confirmed fact:** directly established and attributable;
- **counterpart statement:** what the person explicitly said or wrote;
- **user report:** what the user recalls or reports;
- **observation:** behavior or event described without motive;
- **hypothesis:** interpretation that may be wrong;
- **counterevidence:** evidence against the leading interpretation;
- **unknown:** missing information that could change the decision.

For raw messages or records, retain a compact paraphrase and source pointer when
possible. Do not retain full private transcripts, intimate images, credentials,
or unnecessary identifiers merely because they were provided for analysis.

## Build a Decision Fit Score

The **Decision Fit Score (DFS)** is a custom 0–100 summary of the user's stated
decision model. It is not a validated psychological test, compatibility
instrument, diagnosis, consent determination, or prediction of success.

### Step 1: name the decision

Score a bounded question, not a human being.

Good:

- How well does continuing this friendship fit my current needs and evidence?
- How viable is relying on this colleague for this deliverable?
- How well does pursuing an exclusive partnership fit our stated goals now?
- Which of two conflict-repair options is stronger under my priorities?

Bad:

- What is this person's objective value?
- How loyal, attractive, truthful, or controllable are they?
- What is the probability they will consent, return, cheat, or change?

### Step 2: select dimensions

Use four to eight decision-relevant dimensions. The default library is:

| Dimension | What to assess |
|---|---|
| Goal and values fit | Compatibility of directly stated aims, standards, and non-negotiables for this decision |
| Reciprocity and burden | Balance of contribution, care, initiative, cost, and benefit over a relevant window |
| Responsiveness and care | Observable understanding, validation, support fit, and attention to material needs |
| Clarity and truthfulness | Directness of statements, correction of errors, consistency with records, and unresolved ambiguity; not lie detection |
| Reliability and follow-through | Commitments, delivery, repair after misses, and predictability under comparable conditions |
| Boundary and consent respect | Response to limits, refusals, privacy, choice, and current voluntary agreement |
| Conflict and repair capacity | Ability to address impact, lower escalation, remedy harm, change controls, and review behavior |
| Sustainability and constraints | Time, energy, distance, money, power, caregiving, work, health, or other practical conditions the user disclosed |

Optional modules may add user-rated attraction, intimacy satisfaction, role
authority, access, collaboration quality, family fit, or another construct that
materially changes the decision. User-rated attraction or intimacy is the
user's subjective experience; never infer the other person's attraction or
consent and never request intimate media to score it.

### Step 3: anchor every dimension

Use a 0–5 rating with dimension-specific evidence:

| Rating | General anchor |
|---:|---|
| 0 | Directly blocked, repeatedly contradicted, unsafe, or incompatible for this decision |
| 1 | Strong unfavorable evidence with little credible offset |
| 2 | More unfavorable than favorable; substantial condition or repair needed |
| 3 | Mixed or workable with explicit conditions and unresolved evidence |
| 4 | Strong favorable evidence with manageable limitations |
| 5 | Consistent favorable evidence across relevant situations and time |
| unknown | Evidence is insufficient; do not substitute 2.5 or zero |

For each rating record:

- dimension definition;
- user-selected weight from 0 to 3;
- rating and anchor;
- supporting evidence and source/date;
- counterevidence;
- material unknowns;
- confidence: low, moderate, or high;
- update condition.

### Step 4: calculate score and coverage

For dimensions with evidence:

```text
DFS = round(20 × sum(weight × rating) / sum(weight))
coverage = scored planned weight / total planned weight × 100
```

Exclude `unknown` dimensions from the DFS numerator and scored denominator, but
include their planned weight in coverage. Never hide a low-coverage score.

For deterministic arithmetic, copy
`assets/profile-score-template.json`, keep each evidence item source- and
date-labeled, then run `scripts/profile_score.py --input <model.json>`. The
helper validates structure and calculates the composite; it does not infer
ratings, write memory, or establish that the model is valid for the user's
decision. Use `--output` only when the user explicitly chooses a destination.

Interpretation bands:

| DFS | Decision-fit reading |
|---:|---|
| 0–20 | Currently blocked or strongly unfavorable |
| 21–40 | Weak fit; major change or protection needed |
| 41–60 | Mixed; clarify conditions and gather material evidence |
| 61–80 | Promising or workable with named limitations |
| 81–100 | Strong current fit under the stated model |

Bands are communication aids, not empirical thresholds. A result below 50 does
not order the user to leave, and a result above 80 does not certify safety or
success.

### Step 5: report confidence separately

Confidence describes the evidence basis, not decimal precision:

- **low:** sparse, stale, one-sided, contradictory, or mostly inferential;
- **moderate:** several relevant observations with some corroboration and open
  uncertainty;
- **high:** repeated recent behavior or explicit records across relevant
  contexts with little material contradiction.

Do not report invented probabilities or decimal confidence. If the score moves
because the user changed weights rather than because evidence changed, say so.

### Step 6: preserve gates outside the average

Do not average away:

- a user deal-breaker;
- a clear refusal or withdrawn consent;
- violence, threats, coercion, stalking, or exploitation;
- adult-minor sexual or romantic content or inability to consent;
- a binding authority, policy, legal, or safeguarding constraint;
- a material privacy or retaliation risk.

Show these as separate flags. Route safety and qualified-referral cases before
score interpretation.

## Compare people or options carefully

Use the same decision, dimensions, anchors, evidence window, and weight set for
each option. Show each score's coverage and confidence. Do not force a ranking
when one option has materially poorer data or a different relationship context.

When comparing people, state:

- this is fit for the user's bounded decision, not comparative human worth;
- each person has a separate evidence record;
- a higher score can still lose if it violates a deal-breaker or safety gate;
- the user may choose an option for reasons not represented in the model.

## Correct, version, expire, and delete

### Correction

When the user says an entry is wrong:

1. acknowledge the correction without treating it as resistance;
2. identify the affected fact, hypothesis, score, or source;
3. preserve the prior value in correction history unless the user requests
   deletion;
4. update dependent dimensions;
5. show which score change came from evidence, weights, or both;
6. create a new version for a material decision change.

### Version and rollback

Create a snapshot when the decision, people, weight model, material evidence,
recommendation, or safety status changes. Preserve version, date, change note,
and prior score. Rollback restores an earlier active view but does not erase the
fact that a rollback occurred.

### Expiry and freshness

Every hypothesis and score needs a review date or observable update event.
Mark a score stale when the decision, relationship state, evidence window, or
material constraints change. Do not silently carry a score into a new context.

### Deletion and export

On request, show the record, export it in an inspectable form, or delete the
specified profile. Confirm the exact target before deletion and report what the
host actually removed. Do not claim deletion from backups or external systems
the host cannot verify.

## Refuse misuse while preserving legitimate scoring

Refuse or redirect when the requested profile or score is for:

- exploitation, pressure, grooming, retaliation, surveillance, or stalking;
- identifying vulnerabilities, pressure points, or the best manipulation tactic;
- predicting consent, deception, diagnosis, criminality, or protected-trait
  behavior;
- secret recording, credential access, intimate-media analysis, or unauthorized
  third-party data collection;
- consequential formal decisions that require a validated instrument or
  qualified professional.

Offer a safe alternative: score the user's options, relationship fit, reliance,
exposure, or observable pattern using minimized evidence and explicit controls.

## Compact output

For ordinary use, return:

1. the score question;
2. a dimension table with weights, ratings, evidence, and unknowns;
3. DFS, coverage, confidence, and flags;
4. one interpretation tied to the decision;
5. one recommendation, update condition, and review point;
6. any dossier change made or proposed.

Do not dump the full dossier unless the user asks to inspect it or the detailed
record is needed for correction.

## Evidence boundary

Relationship research supports several dimensions as relevant review prompts.
Measurement standards support clear constructs, intended uses, limitations,
and user rights. Neither validates this product's weights, bands, or composite
as a predictive instrument. See `RELATION-02` through `RELATION-08`,
`MEASURE-01`, `MEASURE-02`, `CONSENT-01`, `CONSENT-02`, `SAFETY-01`,
`SAFETY-02`, and `PERSONALITY-01` in the evidence ledger.
