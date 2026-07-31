# Relationship Scope Expansion and Donor Boundary

## Record identity

- Review date: 2026-07-30
- Target baseline: `haitaowu12/interpersonal-strategist@d3008e2b1bc14ca1e74a8a6964dde8d4919d4954`
- Target release: `0.10.0-rc.1`
- Decision: include romance, dating, partnership, intimacy, breakup, and
  reconciliation while retaining risk-based safety and authority boundaries.

This record supersedes earlier **scope decisions** that treated romance as
categorically out of scope. It does not erase the historical audits or authorize
copying from their donors.

## Governing principle

Applicability is determined by the requested act and its risk, not by whether
the relationship is professional, familial, social, or romantic.

Ordinary interpersonal support may include:

- asking someone out once with a real decline path;
- interpreting ambiguous interest without claiming private motive;
- discussing relationship expectations, exclusivity, and long-distance needs;
- preparing consent, intimacy, jealousy, conflict, repair, breakup, distance,
  contact, and reconciliation conversations;
- rehearsing difficult conversations and drafting bilingual wording;
- deciding whether to continue, narrow, pause, repair, or end a relationship.

The skill must still refuse or route conduct involving coercion, pressure after
refusal, stalking, surveillance, deception, retaliation, intimate-media misuse,
sexual conduct involving minors or incapacity, imminent danger, diagnosis, or
formal legal, safeguarding, and clinical determinations.

## Inspected donor identities

| Repository or source | Exact identity | License finding | Permitted role |
|---|---|---|---|
| `tmstack/awesome-persona-skills` | `7648d7be53926a9441f47170ec2254d6f383c941` | No root license identified; linked repositories require individual review | Discovery map only |
| `hotcoffeeshake/tong-jincheng-skill` | `c9caaa9a6576f581c29d016c60bbe935908e20d5` | MIT | Clean-room source organization, explicit limitations, tensions, directness, and anti-covert-test comparison |
| `Pronting/chat-skills` | `0bc7fb6f8da1767d43bb9ac14c243b693357a332` | MIT | Observable conversation-stage and output-workflow comparison; unsafe scoring and escalation rejected |
| Historical romance skill | PolyForm Noncommercial 1.0.0, identity retained in historical project records | Redistribution and commercial-use restrictions | High-level comparison only; no expressive material imported |
| `Andropeee/conflict-coach` | `f4a5bec6f837d874ceb9d8db05f8f09c58f8fde0` | MIT at inspected commit | Conflict-flow comparison only; diagnosis and persistent relationship profiling rejected |

A permissive license permits use under its terms. It does not validate the
source's psychological claims, tactics, or fit to this product.

## Clean-room patterns retained

### Source and limitation discipline

A relationship method should expose:

- what was directly observed;
- what is inferred or unknown;
- the decision the user faces;
- the source and context of any general rule;
- its exception, limitation, and update condition.

### One proportionate move

For ordinary romantic interest, a single clear invitation with bounded
logistics and a real decline path produces more useful information than covert
experiments, response-delay manipulation, or attraction scoring.

### Voluntariness, specificity, and reversibility

Before dating, intimacy, or reconciliation advice, check:

1. whether refusal or withdrawal is materially safe;
2. whether the act, person, time, place, and conditions are clear;
3. whether the decision can be changed without punishment.

This is a product safeguard, not a legal test or clinical instrument.

### State and transition clarity

Distinguish interest, invitation, dating, agreed exclusivity, partnership,
pause, breakup, no-contact or limited-contact, and reconciliation. Do not infer a
shared state from one person's preferred label or from ambiguous behavior.

### Inclusive relationship structures

Do not presume gender, orientation, monogamy, marriage, cohabitation, or a
single culturally preferred relationship form. Apply the participants' stated
agreements and the same consent, honesty, privacy, and agency controls.

## Rejected mechanics

The scope expansion does not adopt:

- intent, attraction, desirability, intimacy, loyalty, or relationship-health
  scores;
- response latency, punctuation, emoji, avatar, appearance, gaze, posture, or
  voice as an attraction or consent detector;
- attachment-style, MBTI, astrology, gender, or nationality as person-level
  diagnosis;
- compliance ladders, sunk-cost pressure, jealousy induction, strategic
  withdrawal, hot-cold cycles, negging, manufactured scarcity, or false rivals;
- treating “no,” uncertainty, silence, freezing, intoxication, or inability to
  respond as permission;
- persistence after a rejection, breakup, or withdrawal of consent;
- stalking, surveillance, doxxing, location tracking, account access, or
  intimate-image misuse;
- adult-minor sexual or romantic strategy, grooming, or exploitation of
  incapacity;
- first-person impersonation of creators or copying their catchphrases and
  scripts.

## Implementation linkage

- Runtime: `skill/interpersonal-strategist/SKILL.md`
- Relationship method:
  `skill/interpersonal-strategist/references/romance-dating-and-intimacy.md`
- End-to-end scenes:
  `skill/interpersonal-strategist/references/scene-playbooks.md`
- Public development lane: `evals/relationship-scope.json`
- Deterministic adapter: `evals/relationship_scope.py`
- Routing: `evals/invocation.json`, `evals/substantive-routes.json`
- Qualification: `release/qualification.json`

No public fixture is an untouched holdout, and no static pass establishes
production readiness or efficacy.
