# Agent Collusion Risk

**Status (2026-10-26):** M0 done; historical M1/M2 approved with superseding working decisions; F1 P/R smoke completed (56/56 successful model calls), **not the main study**. Main multi-quarter M3 design remains unfrozen/unapproved. **First read: [CURRENT-STUDY.md](research/organizational-coalitional-risk/CURRENT-STUDY.md).**

## Active research direction

**[Organizational coalitional risk](research/organizational-coalitional-risk/README.md)**

**Locked overarching question:**
> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Design motivation:** Seek organizations that reduce harmful coordination while preserving legitimate cooperation and productivity.

The research connects:
1. **Organizational design:** roles, local task objectives, an overarching organizational-welfare guideline, permissions, information and communication.
2. **Coalitional opportunities:** what joint deviations are feasible, potentially locally beneficial, harmful to legitimate goals, credible, discoverable or difficult to coordinate.
3. **Agent behavior and organizational outcomes:** actual attempts at harmful coordination, causally supported collusion, successful harmful actions, and legitimate task performance.

The middle layer is a **candidate explanatory abstraction**, not an assumed sufficient statistic or validated predictor. Structure may also affect behavior directly.

**Proposed new M3 study design:** [four-quarter scientific protocol — UNAPPROVED](research/organizational-coalitional-risk/M3-MAIN-STUDY-DESIGN-PROPOSAL.md). Read [CURRENT-STUDY.md](research/organizational-coalitional-risk/CURRENT-STUDY.md) for commitments versus proposals.\n\n**Current priority:** [M3 behavioral protocol and causal controls](research/organizational-coalitional-risk/ROADMAP.md), building on the [M2 approved formal bridge](research/organizational-coalitional-risk/M2-approved-formal-bridge.md), [M1 approved scenario](research/organizational-coalitional-risk/M1-approved-scenario.md), and [bounded novelty audit](research/organizational-coalitional-risk/literature.md). F1 limited smoke was separately authorized and completed; no **main** behavioral experiment is yet approved.

## Working definitions

These are provisional conceptual definitions, not experimentally validated labels.

- **Coordination:** Actions shaped by inter-agent communication, observation or influence; matching actions by themselves do not prove coordination.
- **Collusion:** Coordination toward an unauthorized subgroup objective or arrangement conflicting with legitimate organizational goals or constraints. Exact requirements for intent, tacit agreement and mutual awareness remain unresolved.
- **Coalition:** A subset of agents considered jointly; mathematical eligibility does not imply an actual agreement.
- **Coalitional opportunity:** A feasible joint deviation under specified permissions, states, information and modeled objectives, possibly beneficial to members while harmful to the organization. Count alone is not its full characterization; do not double-count supersets without an explicit counting rule.
- **Opportunity landscape:** The structure of feasible harmful joint deviations and their sizes, overlaps, distributions of gains/losses, coordination difficulty and credibility. Any proposed summary measure requires definition and validation.
- **Organizational power:** Multidimensional executable authority, vetoes, resources, access, information and influence; graph centrality is not automatically control.
- **Organizational welfare:** Value relative to a specified legitimate organizational objective, separate from agents' task-level objectives or modeled payoffs.
- **Causal collusion evidence:** Evidence that inter-agent influence materially contributed to harmful coordination, beyond ordinary cooperation, independent mistakes, obedience and unilateral abuse.

**Do not infer collusion solely from harm, similar actions, or an organizational-welfare gap.** Do not assume LLM preferences maximize mathematical/textual rewards.

## Prior directions and provenance

The previously separate directions are consolidated as complementary research components, **not deleted**:
- [Coalitional vulnerability](research/archive/coalitional-vulnerability/README.md): prior game-theoretic predictor framing, [literature](research/archive/coalitional-vulnerability/literature.md), [adversarial review](research/archive/coalitional-vulnerability/critical-review.md), and [October 2026 Jira pilot](research/archive/coalitional-vulnerability/archive/2026-10-jira-pilot/README.md).
- [Organizational power dynamics](research/archive/organizational-power-dynamics/README.md): prior authority/permissions framing and [literature leads](research/archive/organizational-power-dynamics/literature.md).

The pilot is a technical smoke test, **not evidence of spontaneous collusion**. Legacy roadmaps document the earlier state; the unified roadmap is canonical. Git history is retained.

## Research collaboration and new chats

Follow [AGENTS.md](AGENTS.md). Git is canonical durable state; chats are working context.

```text
Use the GitHub repository surajk-io/agent-collusion-risk as canonical state.
Read main-branch README.md, AGENTS.md, the authoritative\nresearch/organizational-coalitional-risk/CURRENT-STUDY.md, and
research/organizational-coalitional-risk/{README.md,ROADMAP.md,literature.md,M1-design-review.md,M1-approved-scenario.md,M2-approved-formal-bridge.md}.
Use predecessor notes where relevant.

Today's objective: <SPECIFY GOAL>

Verify current milestone, approved decisions, unresolved questions, and
pertinent evidence. Act as a critical research collaborator; distinguish
sources, assumptions, proposals, and human-approved decisions. Surface
load-bearing choices for approval. Do not assume any scenario, metric or
experiment has been approved. Do not write to GitHub without authorization.
```

For concurrent coding agents, use distinct Git branches and worktrees plus explicit ownership of shared interfaces. Real experiments, once approved, belong in `research/organizational-coalitional-risk/experiments/<id>/`.
