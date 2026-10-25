# M3 pilot interaction candidate — review package

**Proposed, unapproved, 25 October 2026.** Originally prepared outside the canonical checkout. Published as review artifacts on a separate branch at the researcher's explicit request. Publication does not approve M3, amend M2, or authorize simulator implementation or behavioral runs. No simulator, fixture changes or behavioral runs were produced.

1. [Standalone interaction specification](interaction-spec.md): exact schedule, permissions/information, validation, memory, provenance, inferential scope and adversarial risks.
2. [Candidate JSON schemas](candidate-schemas.json): communication, owner/reviewer choices and historical-message projection. Validate against named `$defs`, not the unconstrained root. Runtime authorization is specified separately.
3. [Offline test matrix](offline-test-matrix.md): 68 proposed cases and hand-scripted P/R expressibility traces. These are not executed harness tests.
4. [Short decision register](decision-register.md): approved, proposed, recorded-but-unamended and unresolved choices with alternatives and effects.
5. [Independent critique/disposition](independent-review.md): six consequential corrections and qualified follow-up consistency result.
6. [Artifact validation report](validation-report.md) and [machine-readable checks](artifact-checks.json).

Recovered GitHub main at [commit 1c6927f](https://github.com/surajk-io/agent-collusion-risk/commit/1c6927f48824e657a5d15e2b67550a8b28e5f1b5). Local checkout was older and was left untouched. Eleven pinned source copies are under `sources/`; exact paths/blob IDs are in [source manifest](source-manifest.json). Every captured source matches its Git blob identity.

The five-round proposal gives **28 primary calls per complete main episode**, with atomic owners/reviews and no new-generation retries. Group recipient sets must be disjoint per sender/round. Historical conversations are automatically projected without extra model calls. These are candidate mechanics, not authorization to implement or run.

Next: compare with OpenCode's frozen packets, resolve the register (especially causal controls, reception-aware labels and all-assigned denominators), complete literal prompts/settings/parameters/analysis/budget, approve the M3 package and applicable M2 amendment, then implement and validate. Missing parameters block launch.
