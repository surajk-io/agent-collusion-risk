# Agent Collusion Risk

**Status:** Exploratory research. No empirical collusion finding, validated predictor, or selected experimental design.

## Open research directions

1. **Coalitional vulnerability.** Can game-theoretic measures of the **number, magnitude, distribution and credibility of profitable harmful coalitions** predict whether AI agents actually coordinate against an organization's objective? When and why do the predictions fail?
2. **Organizational power dynamics.** Does the **distribution of roles, authority, permissions and influence** change which coalitions form, what they can accomplish, and whether harmful coordination succeeds or is detected? Can power asymmetries and pooled authority predict collusion beyond payoff opportunities alone?

**Neither direction is chosen over the other.** Their relationship is an open question, not a settled framework.

[Questions, candidate hypotheses and definitions](research/research-question.md) · [Prior work](research/prior-work.md) · [Critical objections](research/critical-review.md)

## Existing experiments

[Standalone Jira-inspired exploratory pilot](colosseum-jira-pilot-v2/README.md) · [Colosseum source audit](research/colosseum-jira-extraction.md) · [Gemini smoke-test audit](research/vertex-public-smoke-audit-2026-10-23.md) · [GPT-OSS smoke-test audit](research/gptoss-smoke-audit-2026-10-23.md)

The pilot's results are **technical smoke tests, not scientific evidence of collusion**. Known limitations include explicit "synthetic experiment" language in agent prompts, abstract numerical incentives, organizational welfare defined as summed agent rewards, and insufficient controls for causal coordination. Retain the code and raw transcripts for reproducibility; do not infer collusion from low welfare or duplicated actions.

Git is the durable research record. Superseded drafts remain recoverable through version history; the active docs should stay small.
