# Community design inputs for context-first interaction

Reviewed 2026-09-07 for `0.11.0-alpha.1`. These sources inform interaction design,
not scientific efficacy. Runtime text, questions, examples, and fixtures in this
revision are newly authored. No donor files or prompt bodies are redistributed;
no donor tool, network, delegation, or memory instruction is adopted as authority.

| Source and exact revision | Useful idea | Adaptation / rejection |
|---|---|---|
| [mattpocock/skills, grilling](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/grilling/SKILL.md) | Resolve prerequisites and let answers determine subsequent questions. | Adopt decision-dependent progression. Reject exhaustive interrogation, a mandatory confirmation for every case, recommended answers to factual questions, and broad environment exploration. Interpersonal facts belong to the user's account and authorized evidence. |
| [RobMitt/grill-me-skill](https://github.com/RobMitt/grill-me-skill/blob/31d61d68fc406f8cc2a944b4b10e6f23877720f1/SKILL.md) | One question followed by a real pause keeps elicitation interactive. | Adopt the pause as a portable conversation rule. Reject dependence on one named popup tool and mandatory multiple choice. A natural-language answer often carries essential nuance. |
| [BayramAnnakov/2026-coach](https://github.com/BayramAnnakov/2026-coach/blob/e0960852197739d59f485ca41cc673ed6e631195/SKILL.md) | Discovery precedes synthesis, with a chat fallback when structured question UI is absent. | Adopt host-independent elicitation and controllable next actions. Reject fixed annual-planning rounds, automatic artifact creation, tracking integrations, motivational scripts, and imported quantitative efficacy claims. |

GitHub metadata reported MIT for mattpocock/skills; its
[license at the pinned revision](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/LICENSE)
was inspected. The other two repositories had no detected license in GitHub
metadata at review time; a license field inside a skill is not a complete
redistribution review. They were used only to compare design ideas. Any future
copying of source text requires a separate license check and retained notices.

The runtime's existing research ledger remains unchanged. No “grill me” repo
establishes that this product improves interpersonal judgment or user outcomes.
See the development audit and interactive comparison protocol for that gap.

## Retrieved-byte checksums

Pinned raw files were retrieved on the review date. SHA-256:

```text
mattpocock grilling/SKILL.md 10ff989e7498b23b5acb49d5048f11dcd906757d2f79c5cdf8a00001381296f2
mattpocock LICENSE          0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5
RobMitt SKILL.md            4c4db26d8b01994cfa0ac755e105033c07f30dac4f6e8b84ca0b1d8c701eeab1
BayramAnnakov SKILL.md      a47784a834ef294569bc884765fcc76c0c95c959b2dd2cecb3fe44bacdabb7e7
```
