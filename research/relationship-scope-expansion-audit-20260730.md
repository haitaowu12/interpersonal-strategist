# Relationship Scope Expansion Audit

**Date:** 2026-07-30
**Baseline:** `haitaowu12/interpersonal-strategist@d3008e2b1bc14ca1e74a8a6964dde8d4919d4954`
**Candidate:** `0.10.0-rc.1`
**Decision:** replace relationship-category exclusions with act- and risk-based
routing.

## Executive decision

The earlier non-romantic boundary was a product-design choice, not a necessary
safety boundary. It excluded ordinary requests—asking someone out, discussing
exclusivity, setting intimacy boundaries, ending a relationship, or considering
reconciliation—that can use the skill's existing evidence, power, privacy,
communication, conflict, trust, bilingual, role-play, and stopping controls.

The candidate therefore includes workplace, friendship, family, household,
dating, romance, partnership, intimacy, breakup, reconciliation, and other
consensual adult interpersonal situations. The exclusions that remain are tied
to harmful conduct, lack of meaningful consent, privacy invasion, minors or
incapacity, immediate danger, diagnosis, formal adjudication, and actions beyond
the user's authority.

## Why broad inclusion improves the product

### Shared mechanisms

Romantic cases frequently involve the same mechanisms already covered elsewhere:

- ambiguous evidence and digital cues;
- unequal power and dependency;
- invitations, refusals, boundaries, and commitments;
- relationship norms and differing expectations;
- conflict, repair, trust, and reliance;
- privacy and AI-mediated communication;
- multilingual speech acts;
- decisions to continue, reduce dependence, pause, repair, or exit.

A separate category-wide route-out duplicated these mechanisms and prevented
useful progressive disclosure.

### Better safety through routing

A broad skill can distinguish an ordinary invitation from persistence after
refusal, a consensual intimacy conversation from pressure, and a breakup plan
from stalking or imminent danger. Treating every romantic case as out of scope
removes the opportunity to make those distinctions.

### Better donor governance

Removing the category exclusion allows review and adoption of useful patterns
from relationship-focused repositories. Adoption still requires an exact source,
license review, source-quality assessment, clean-room implementation, local
failure case, and evaluation. Inclusion does not mean wholesale takeover.

## New scope matrix

| Situation | Default route | Required controls |
|---|---|---|
| One low-pressure invitation | `IN_SCOPE` | clear invitation, concrete logistics, real decline path, one follow-up maximum when ambiguity is genuine |
| Ambiguous interest | `IN_SCOPE` | observations versus inference, no attraction score, direct low-cost clarification |
| Exclusivity or relationship definition | `IN_SCOPE` | each person's current position, terms, timing, consent, no presumed agreement |
| Intimacy or sexual-boundary conversation among capable adults | `IN_SCOPE` or `COACH_WITH_CAUTION` | voluntariness, specificity, reversibility, contraception/STI facts routed to current qualified sources when needed |
| Breakup, distance, or contact boundary | `IN_SCOPE` | clear decision, logistics, safety, record/contact rule, no false hope |
| Reconciliation | `IN_SCOPE` or `COACH_WITH_CAUTION` | reason for breakup, remedy, changed controls, bounded trial or no re-entry |
| Workplace romance | `COACH_WITH_CAUTION` when power or policy matters | reporting line, evaluation control, retaliation, policy, privacy, real ability to decline |
| Threat, stalking, coercive control, intimate-image abuse, immediate danger | `REFER_OR_ESCALATE` | protection first, current authoritative route, minimal disclosure |
| Pressure after refusal, grooming, adult-minor sexual strategy, exploiting intoxication or incapacity | `REFUSE` | preserve legitimate objective only if it can be pursued safely and consensually |
| Legal consent, assault, harassment, custody, or safeguarding determination | `REFER_OR_ESCALATE` | organize facts and questions; do not adjudicate |

## Donor review conclusions

The requested Chinese repositories contain useful source-organization,
conversation-stage, output, and limitation patterns. They also contain or border
on mechanisms that this product should not adopt: attraction and status scores,
response-delay manipulation, compliance ladders, inferred refusal override,
gender essentialism, hidden-state claims, and creator impersonation.

The candidate adopts the useful structural patterns in original wording and
turns the rejected mechanisms into adversarial cases. Exact identities and
license findings are in `provenance/RELATIONSHIP_SCOPE_EXPANSION.md`.

## Runtime architecture

### Voluntariness-Specificity-Reversibility

For a consequential invitation, intimacy request, reconciliation, or contact
change, the skill checks whether:

- a refusal is safe and free of material punishment;
- the person, act, timing, conditions, and relationship state are clear;
- either person can pause, withdraw, or revise the decision.

The check narrows advice and creates stop conditions. It is not a substitute for
current law, medical advice, or a qualified consent assessment.

### Relationship-state clarity

The runtime distinguishes interest, invitation, dating, exclusivity,
partnership, pause, breakup, contact boundaries, and reconciliation. A state
requires current mutual agreement where mutual agreement is relevant; it is not
inferred from investment, sex, gifts, labels used by only one person, or social
media behavior.

### User-defined relationship terms

The runtime uses the participants' identities, roles, relationship terms,
agreements, and boundaries. It does not infer them from names, appearance,
platform, culture, or a relationship label.

### Symbolic and typology lenses

A user may request MBTI, attachment vocabulary, astrology, or another symbolic
frame for reflection. The runtime may use it only as a user-chosen prompt,
labelled non-diagnostic and non-predictive. It cannot override observed conduct,
consent, correction, safety, or formal authority.

## Evaluation plan

The public relationship-scope lane covers English, Simplified Chinese, and
mixed-language cases across:

- invitations and ambiguous interest;
- exclusivity and expectations;
- intimacy and consent;
- jealousy and third parties;
- breakup, contact, and reconciliation;
- workplace power and privacy;
- relationship agreements, privacy, disclosure, and dependency;
- requested typology lenses;
- stalking, coercion, minors, incapacity, and formal determinations;
- manipulative donor-pattern attacks.

The qualification manifest adds private adversarial strata for romance,
consent, workplace romance, breakup and stalking, and intimate privacy. The
release remains blocked because a changed runtime invalidates prior behavioral
evidence.

## Acceptance conditions

- no categorical romance route-out remains in active runtime or canonical
  routing;
- ordinary romance cases route in scope;
- power, consent, privacy, and safety conditions change the route;
- refusal, withdrawal, breakup, and contact boundaries are controlling;
- all required references are linked and packaged;
- public fixtures validate and prepare deterministically;
- Python 3.11 and 3.13 CI, packaging, checksum, and smoke install pass;
- `release/qualification.json` remains blocked until the expanded scope is
  tested on the exact candidate package.
