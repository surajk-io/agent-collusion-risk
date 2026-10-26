# Checks actually performed

Date: 25 October 2026. These checks validate review artifacts only.

- Parsed the candidate schema JSON successfully; all **19 local `$ref` occurrences** resolve to one of its **14 definitions**. All **9 object definitions** reject additional fields and declare required fields present in their properties.
- Confirmed **68 unique matrix case IDs** and existence of the five principal deliverables. Runtime and fixture rows are specified, not executed.
- Verified all **11 source captures** against the GitHub-provided native Git blob SHA, including the exact blob header/length. Sources are pinned to `1c6927f48824e657a5d15e2b67550a8b28e5f1b5`; capture SHA-256 values are in `artifact-checks.json`.
- Independently enumerated the 16 equally weighted independent approve/reject patterns for four submitted vulnerable candidates: P has 7 patterns with at least one complete approval cycle, R has 1; mean unauthorized deployments is 2 in both. This checks the approved M2 mathematical false-positive benchmark. It is not an observed behavioral result or a causal test.
- A separate reviewer with fresh context performed two textual reviews. Six consequential omissions were corrected; the follow-up found no remaining material contradiction affecting the stated contracts. See `independent-review.md` for scope and limits.

**Not executed:** full Draft 2020-12 JSON Schema meta-validation or instance validation (the `jsonschema` package was absent from both available Python runtimes; no dependencies were installed); any simulator/authorization/projection tests; Django tests or fixture inspection; provider calls, competence tests, positive-control LLM tests or behavioral trials. The JSON parse/reference checks do not substitute for full schema validation or runtime permission tests.

During the original design task, no canonical repository files, OpenCode files, Git refs or GitHub content were changed; artifacts were written only under `/private/tmp`. The researcher subsequently authorized publication of this package on a new branch. Publication changes portable links and publication-status wording only; scientific choices and approval statuses remain unchanged.
