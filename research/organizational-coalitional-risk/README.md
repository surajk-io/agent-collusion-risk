# Organizational coalitional risk — unified research direction

**Status (2026-10-26):** Historical M1 and M2 approved; current scientific decisions and supersessions are governed by [CURRENT-STUDY.md](CURRENT-STUDY.md), which must be read first. F1 P/R engineering smoke finished; complete multi-quarter M3 main study not yet approved.

## Locked overarching question

> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Practical motivation:** Discover organizational designs that reduce harmful coordination while retaining legitimate cooperative productivity.

## Motivation and operating assumptions

- Agents perform specialized, legitimate work with distinct operational objectives. They are also instructed that their work should advance the organization's objectives. They are **not** assumed to have identical utility functions, to be intrinsically selfish, or to optimize a formal payoff function perfectly.
- Organizational structure includes executable permissions, approval/veto rights, resources, information, role dependencies, communication paths and the starting state.
- A coalition's theoretical ability to realize a harmful deviation is **not** evidence that agents will discover, prefer, negotiate or execute it.
- Power is multidimensional. Scalar summaries of the induced opportunity landscape may be useful but should be justified and compared against alternatives.
- Legitimate organizational welfare is specified separately from local task success and modeled individual payoffs.
- Ordinary cooperation that causes an error, obedience, independent convergence, unilateral misconduct and causally supported collusion are distinct potential outcomes.

## Unified conceptual framework

**A. Organizational configuration** (roles, incentives/objectives, information, permissions, communication, initial state)
  -> **B. Coalitional opportunity landscape** (feasibility, minimal coalitions, overlapping opportunities, distribution of member gains and organizational losses, discoverability, coordination requirements, credibility)
  -> **C. Observed behavior and outcomes** (recognizable attempts, recruited partners, enacted joint deviations, causal collusion evidence, welfare and legitimate productivity).

This is a **hypothesized explanatory pathway**, not a claim that B mediates every effect of A. A may affect C directly through salience, social/role cues, information, supervision and other channels. Distinguish objective opportunity features from an LLM's knowledge of those opportunities.

## Candidate hypotheses (not adopted or proven)

- **Opportunity predictiveness:** Ex ante coalition opportunity properties predict observed harmful coordination across held-out organizational configurations beyond simple baselines.
- **Distribution/overlap:** Configurations matched on opportunity count and modeled gains but different in coalition overlap, pivotal agents or arrangement may differ in behavioral outcomes.
- **Bridge/mediation:** Structural interventions may alter realized coordination partly through changes in opportunities, but residual effects may arise from information, discovery, role cues or prompting.
- **Robust organizational design:** Some interventions lower harmful coordination without disproportionate losses in legitimate productivity.

These compete with the null/alternative that such summaries have weak or no behavioral predictive value, that effects are only mechanical feasibility, or that agent prompt/model/context dominates structural variables. Avoid assuming monotonic trends.

## Required separations

1. **Independent structure -> opportunity derivation**: formal actions, permissions, information, modeled objectives, legitimate baseline; no using observed behavior to label the ex ante opportunity.
2. **Feasible opportunity vs actual behavior**: count distinct deviations carefully; coalitions of agents and distinct harmful mechanisms are not interchangeable. Partial observability and credible commitments matter.
3. **Attempted vs realized vs successful harm**: communications are suggestive, not conclusive; harm alone is not collusion.
4. **Predictive vs causal**: held-out prediction does not demonstrate intervention effect; manipulate meaningful permissions and control incentives/information/communication as far as possible.
5. **Safety vs utility**: quantify legitimate task performance, throughput and blockers alongside harms.

## Current state and next

See [ROADMAP.md](ROADMAP.md). A bounded focused novelty audit is **complete**; see [literature.md](literature.md). Novelty of the eventual experiment or result remains unestablished. The researcher approved the balanced four-agent cross-workflow reviewer-network scenario in [M1-approved-scenario.md](M1-approved-scenario.md), after critique documented in [M1-design-review.md](M1-design-review.md). This approval does not authorize a particular executable model, prompt, or experiment.

**Current bottleneck: reconcile/freeze the multi-quarter M3 scientific protocol** (late plausible fixes, independent authorization, hidden truth, audit/history, P/R controls) as recorded in [CURRENT-STUDY.md](CURRENT-STUDY.md). F1's single-quarter qualification-gap exercise is finished technical smoke, not the proposed main study.

The historical M2 formal bridge was approved but superseded in several present-study assumptions; no exact current M3 horizon, numeric audit values, case allocation, LLM provider, or main experiment has been approved. Approval gates follow [AGENTS.md](../../AGENTS.md).

### Predecessor materials retained

- [Coalitional vulnerability framing](../archive/coalitional-vulnerability/README.md) and [critical review](../archive/coalitional-vulnerability/critical-review.md)
- [Organizational power framing](../archive/organizational-power-dynamics/README.md)
- [Jira pilot archive](../archive/coalitional-vulnerability/archive/2026-10-jira-pilot/README.md)
