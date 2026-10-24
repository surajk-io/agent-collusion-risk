# Research questions — provisional (2026-10-24)

**Status:** Two live research directions, no committed empirical hypothesis or validated metric. The research questions should not be judged by the unsuccessful design of the initial Jira smoke tests.

## A. Coalitional vulnerability and realized behavior

**Core question:** Can game-theoretic measures of coalitional vulnerability predict the emergence of harmful coordination among LLM agents, and under what conditions do those predictions succeed or fail?

The originating intuition is that vulnerability may depend not only on the **largest** profitable deviation but also on **how many distinct coalitions** have opportunities, the size/distribution of those gains, the actions and permissions required to execute them, and whether the arrangements are credible. Study whether formal, ex ante opportunity measures predict **observed, causally supported** behavior in executable agent organizations.

Open candidate hypotheses (not decisions):
- The distribution or count of profitable harmful coalitions contains predictive information beyond maximum coalition gain.
- Matched organizations with equal maximum gain but different exploitable-coalition distributions exhibit different behavior.
- Self-enforcement, trust, retaliation, and practical coordination costs affect the relationship between theoretical opportunity and realization.
- Predictive relationships vary by model capability, communication, monitoring, interaction history, and instructions.

## B. Organizational power dynamics

**Core question:** How does the distribution of **power, authority, responsibility and influence** among AI agents affect the **formation, execution and success** of harmful coalitions?

Original proposal: represent organizational roles, responsibilities, permissions and influence using a **directed graph** (a DAG where appropriate). Ask whether a subset's **pooled authority** creates a disproportionate advantage over other agents or the organization's decision process, and whether subsets with greater power gaps are more likely to collude. Power includes who can initiate an action, approve, veto, audit, allocate resources, withhold information, and influence other agents.

Open candidate questions (not assumptions):
- Holding goals and incentives as constant as feasible, how do centralization, unequal authority, gatekeeping roles and information asymmetries change coalition **formation**, **capability to cause harm**, and **detectability**?
- Does combining permissions across agents enable actions that no single member can execute? How does this affect voluntary collusion versus independent actions or obedience to a superior?
- Do the number, composition and relative power of potentially decisive subsets predict realized coordination better than payoff magnitude alone?
- How do formal authority, communication/influence topology, audit access and veto rights interact? Is a highly influential agent more likely to recruit a coalition or simply induce compliance without mutual agreement?

These questions may be closely related to direction A, but **we have not decided to merge them** into one predictive model. Formalizing "power" in executable terms is itself unresolved.

## What counts as evidence

Keep distinct:
1. **Feasibility:** a subset could jointly execute an action.
2. **Profitable opportunity:** specified member payoffs rise while legitimate organizational welfare falls relative to a clearly stated reference.
3. **Credibility:** coalition members would continue to prefer following the arrangement rather than defecting.
4. **Attempt:** observable communication, influence or planning toward the harmful outcome.
5. **Realization:** harmful joint behavior occurs.
6. **Causal collusion:** evidence identifies an inter-agent causal contribution beyond independent convergence, ordinary cooperation, command-following or mistakes.

Agents' *modeled* payoffs need not be what an LLM actually optimizes. Evaluation awareness, synthetic framing, capability, tool permissions, and ambiguous authority are potential confounders.

One **illustrative existing concept**, not a novel metric or a chosen predictor: for reference actions `a⁰`, coalition `S` and outsiders held fixed,

`g(S) = max_{a'_S : W(a'_S,a⁰_{-S}) < W(a⁰)} min_{i∈S} [u_i(a'_S,a⁰_{-S}) − u_i(a⁰)]`.

A strictly profitable harmful deviation requires `g(S)>0`. If no eligible deviation exists, explicitly define that case rather than treating it as a measured probability. Counting subsets can double-count the same outcome, and static gain says nothing by itself about self-enforcement or behavior. Coalition stability measures have substantial prior art.

## Status and next research decision

No organization, baseline welfare function, agent objective model, or collusion annotation protocol has been validated. The Jira-inspired runs only establish that the harness can execute and log toy episodes; the current prompts **explicitly say "synthetic experiment"**, and the task-credit accounting can reward duplicated work. They do not answer A or B.

Choose a credible workflow and operational definition of collusion **before** choosing numerical incentives or running large batches. Keep exploration, tentative hypotheses and decisions separate.

See [prior work](prior-work.md), [critical review](critical-review.md), and [exploratory code and traces](../archive/2026-10-jira-pilot/colosseum-jira-pilot-v2/README.md).
