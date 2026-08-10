# Scoring and Dossier Community Pattern Audit

## Record

- Review date: 2026-08-10
- Target baseline: `haitaowu12/interpersonal-strategist`
  `12b230be0e068cfae23acf28a8b438dd46a998cb`
- Purpose: identify reusable profile, scoring, correction, continuity, and
  evaluation patterns without importing unsupported psychology, manipulative
  dating tactics, forced persistence, or donor expression.
- Method: inspect public source at an exact commit; read license, skill and
  profile structure, executable surface, and safety posture; do not execute
  donor code or installation instructions.

Community repositories are software-pattern donors, not behavioral evidence.
No donor prompt, questionnaire, scoring formula, example, person profile,
creator voice, corpus, or script is copied into the distributable skill.

## Qualified repository set

| Repository | Exact inspected commit | License posture | Inspected scope and security notes | Adopted clean-room pattern | Rejected pattern |
|---|---|---|---|---|---|
| `tmstack/awesome-persona-skills` | `7648d7be53926a9441f47170ec2254d6f383c941` | No root license; index only | Repository discovery surface; linked projects require separate review. | Use as discovery map only. | No blanket reuse or trust inheritance. |
| `hotcoffeeshake/tong-jincheng-skill` | `c9caaa9a6576f581c29d016c60bbe935908e20d5` | MIT | Romance persona skill with opinionated stages and scripts. | Separate user context from target context and keep advice continuity visible. | Persona voice, physical-escalation tactics, hidden attraction claims, or copied prose. |
| `Pronting/chat-skills` | `0bc7fb6f8da1767d43bb9ac14c243b693357a332` | MIT | Chat-analysis instructions with social formulas and escalation logic. | Reconstruct observable turns, source quality, speech acts, and uncertainty. | Hidden-state formulas, refusal override, and strategic escalation. |
| `alchaincyf/nuwa-skill` | `27642f5bfed2dc1bbf8ee59a2c1ee602a626bbd7` | MIT | Source-window and boundary-oriented instruction set. | Record time window, source, contradiction, limitation, and update condition. | Any private-thought or stable-personality claim. |
| `titanwings/colleague-skill` | `47039d08fcf0330794caea14efdb5e183348f7bb` | MIT | Persistent colleague profiles with correction/version concepts. | User corrections change the active record; preserve bounded revision history. | Autonomous third-party persona completion or unbounded retention. |
| `vogtsw/boss-skills` | `93f5c7c0a5d7091ce45ce1343ab4bfad662a0c19` | No root license found | Manager-oriented profile and advice prompts. | Comparison questions only. | No direct import, copied wording, or authority assumptions. |
| `notdog1998/yourself-skill` | `9deb1a87b1231fec85cadf2ef690fa49fef519ca` | MIT | Self-profile snapshots and inspect/correct/delete concepts. | Give the user inspect, correct, delete, and snapshot controls. | Treating generated identity text as fact. |
| `leilei926524-tech/anti-distill` | `21e6aa9c72a03a5456eeb4cd63234a2fa2935387` | README says MIT; no root license found | Instructions explicitly conceal knowledge while presenting a complete-looking artifact. | Adversarial comparator only. | Deceptive withholding and false completeness. |
| `tomwong001/qingsheng-skill` | `ea23b10376b146abfcff20f71876889a0453a7e7` | MIT root license | `skill/SKILL.md` and `references/user-context.md` require global profile files, multi-target switching, and background version checks; setup and upgrade paths use network and shell writes. No donor command was run. | One dossier per relationship context, alias-based switching, last-action continuity, and explicit file visibility. | Forced global creation, implicit activation, background network checks, gendered targeting, IOI/IOD taxonomies, resistance-pushing, and automatic intimate-source retention. |
| `zesion21/cupid-skill` | `a6decc8dc1b9eb7cf04429a8babfb0b83744c5a4` | MIT root license | Skill and Python tools parse chats and images, create files, version profiles, and include a recursive delete command. No donor tool was run. | Separate profile, relationship context, correction log, current assessment, and version snapshot; distinguish historical from current observations. | Inferring MBTI, astrology, personality, or attraction from messages/photos; unbounded raw-media retention; auto-generated target persona; donor delete command. |
| `nataliecao323/partner-skill` | `5d80d609059713f586b9ff5b37430c2ba7f76491` | MIT root license | Skill and local Python tools build partner profiles, weighted RQI/attachment/love-language metrics, state simulations, snapshots, rollback, and deletion. No donor tool was run. | User-confirmed intake, evidence-linked dimension breakdown, correction propagation, versioned snapshots, rollback, deletion, and trend review. | Claims that arbitrary weights or attachment compatibility modifiers are empirically validated; diagnosis from chat; simulated probabilities; raw intimate archive; branded typologies as compatibility truth. |
| `acnlabs/OpenPersona` | `251cf1d838f35b89b2447ab043f7a07ad0879c7e` | MIT root license | Large persona platform with schemas, local state, network/social/economy surfaces, evolution, source fields, rolling snapshots, and many executable tools. No dependency or tool was run. | Schema version, immutable record identity, created/updated timestamps, source-tagged changes, bounded snapshots, and explicit migration rules. | Autonomous persona evolution, hidden mood/relationship state, network/economy behavior, and importing a general persona runtime into an advice skill. |

## Design decisions

### Adopt

The local scoring/profile contract uses the strongest common architecture:

1. separate the user's own preferences from observations about another person;
2. scope one dossier to one relationship or decision context;
3. label fact, report, inference, counterevidence, unknown, source, and date;
4. use anchored dimensions with user-controlled weights and visible coverage;
5. keep confidence separate from the score;
6. preserve correction history and a current active view;
7. version material changes and support rollback or deletion;
8. use score deltas as review prompts, not as truth about a person.

### Reject

- A score may summarize a stated decision model; it may not become human worth,
  attractiveness, truthfulness, consent, diagnosis, abuse, or legal status.
- Missing values remain unknown. They are not silently treated as neutral.
- Low-specificity cues such as photos, avatars, emoji, latency, punctuation,
  vocal affect, or body movement cannot support a numerical person judgment.
- MBTI, attachment labels, astrology, love languages, or other typologies may be
  recorded only when the user supplies them as a reflective preference. They do
  not generate compatibility multipliers or individual predictions.
- A safety concern or deal-breaker is not averaged away by favorable dimensions.
- Profiles are not created silently, updated with memory off, or expanded beyond
  the user's stated purpose.

## Clean-room linkage

- Runtime contract:
  `skill/interpersonal-strategist/references/profiles-and-scoring.md`
- Memory lifecycle:
  `skill/interpersonal-strategist/references/memory-and-continuity.md`
- Safety limits:
  `skill/interpersonal-strategist/references/safety-and-referral.md`
- Public development fixtures:
  `evals/profile-scoring.json`
- Deterministic enforcement: `tests/test_profile_scoring.py`

This review does not qualify any behavioral claim and does not change the
blocked production-qualification state.
