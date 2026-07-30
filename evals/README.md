# Evaluation protocol

These fixtures are synthetic development evidence. They are not untouched
holdouts and do not contain real conversations.

For each behavior case:

1. invoke the exact packaged skill explicitly;
2. retain the raw response;
3. score every rubric dimension;
4. apply case-specific `must_include` and `must_not` assertions;
5. fail immediately on any rubric hard failure;
6. compare against a no-skill response on the same prompt;
7. have a fluent human review Chinese-English parity cases.

Do not use these development cases as final qualification evidence. Freeze the
instruction package before an independent reviewer authors fresh holdouts.
