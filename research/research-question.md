# Research question and hypotheses

**Checkpoint date:** 2026-10-23  
**Status:** Provisional research direction; no settled experimental hypothesis or validated metric.

## Original motivation (author's idea)

A multi-agent organization divides responsibilities, permissions, and incentives across agents. A subset of agents may jointly control actions that allow its members to benefit at the expense of the organization's legitimate objective, even though individual members cannot achieve the same outcome alone.

The author's specific extension: vulnerability may depend not only on the *largest* coalition advantage, but on **how many different subsets have exploitable opportunities and the distribution of their magnitudes**. Can mathematical descriptions of real, executable agent organizations predict how often LLM agents actually exploit these opportunities?

## Fundamental research question

**Can game-theoretic measures of coalitional vulnerability predict the emergence of harmful coordination among LLM agents, and under what conditions do those predictions succeed or fail?**

This is a question, not an established relationship.

## Candidate empirical hypotheses (NOT committed)

- H1: A distribution of profitable coalitional deviations contains predictive information beyond maximum available gain alone.
- H2: Environments with identical maximum exploitable gain but different *numbers of profitable coalitions* may show different rates of realized, causally supported collusion.
- H3: Feasibility is insufficient: the credibility / self-enforcement of jointly profitable strategies can modify the relationship between structural exposure and realized behavior.
- H4: Any predictive relationship may depend heavily on the agent model, prompting, interaction history and communication structure; failure to generalize is an informative outcome.

Null results are valuable only with valid measurements, enough informative trials, and controls that distinguish absence of collusion from failures of task understanding, discovery or execution.

## Scientific distinctions

1. **Feasibility:** A subset can jointly change the outcome.
2. **Opportunity:** A feasible deviation benefits coalition members and harms organizational welfare under *specified* payoffs.
3. **Credibility:** Members have incentives to adhere to the proposed deviation; betrayal and enforcement may matter.
4. **Attempt:** Agents try to agree or influence each other.
5. **Realization:** Agents take relevant joint actions and the organization incurs a measurable loss.
6. **Causal collusion:** Evidence supports an inter-agent causal contribution, rather than independent convergence to harmful outcomes.

Do not conflate these steps, especially potential payoff with the probability of collusion.

## Modeling sketch (NOT a theorem or chosen specification)

For finite agents N, action sets A_i, individual payoff functions u_i, and organizational welfare W, choose a baseline a^0 and a coalition S. A candidate worst-member gain is:

    g(S) = max_{a'_S: W(a'_S, a^0_{-S}) < W(a^0)}
                min_{i in S} [u_i(a'_S,a^0_{-S}) - u_i(a^0)]

Define g(S) as undefined (or -infinity under an explicit convention) if the constrained action set is empty. Do not interpret it as a probability. To claim a profitable coalition under strict individual rationality, require g(S) > 0. Outside agents are held fixed; repeated-game retaliation, transferable utility, off-equilibrium credibility and alternative baselines remain unresolved. This candidate is closely related to established profitable coalitional-deviation concepts; no mathematical novelty is claimed.

## Open decisions

- The organizational domain, concrete responsibilities and actions; user will propose a 3–4-agent toy instance.
- Baseline policy and what should count as unauthorized harm.
- Whether the initial target is voluntary discovery, incentivized coordination, or sustained collusion.
- Proper operational evidence for *causal* coordination.
- Whether group formation is endogenous or whether candidate coalitions are only a formal diagnostic.
- Primary predictor and controls; do not optimize definitions after seeing results.

## Immediate next action

The author independently constructs a small concrete organization. Critique its internal consistency and map from permissions to feasible actions before designing an LLM run or spending limited frontier-model compute.
