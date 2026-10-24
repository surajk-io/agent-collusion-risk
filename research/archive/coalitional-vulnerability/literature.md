# Prior work and novelty status

**Checkpoint:** 2026-10-23. **Status:** Focused literature audit; not an exhaustive proof of novelty. Unverified claims must not be promoted to facts.

## Formal foundations — substantial existing prior art

- Feldman, Meir & Tennenholtz, *Stability Scores: Measuring Coalitional Stability* (2012): counts profitable coalitions by size, distinguishing strong and super-strong stability. https://arxiv.org/abs/1105.5983
- Liu, Farina & Ozdaglar, *Computing Equilibrium beyond Unilateral Deviation* (2026): formal coalitional deviation / exploitability objectives. https://arxiv.org/abs/2604.28186
- Bernheim, Peleg & Whinston, *Coalition-Proof Nash Equilibria I. Concepts* (1987): credibility and self-enforcement of coalitional deviations.

**Consequently:** Maximum gain, count of profitable coalitions, and coalitional stability are not automatically new mathematical concepts. Cite their antecedents; do not relabel known quantities and claim novelty.

## Closest empirical AI-agent precedents

- Nakamura et al., *Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems* (2026). Varies coalition objectives, composition/influential roles and communication topologies; measures realized behavior and regret/advantage. Does not appear to systematically compute an independent ex ante worst profitable group deviation per configuration and use it to predict uninstructed coalition formation. https://arxiv.org/abs/2602.15198
- Shi et al., *Emergent Collusion in Long-Horizon LLM Agent Interaction* (2026). Tests repeated protocol-violation behavior and ablations of shared vs. individual reward structure, feedback, and peer actions; not a continuous ex ante coalition-opportunity sweep. https://arxiv.org/abs/2609.24967
- Zeng & Rudzicz, *Voluntary Collusion with Secret Tools in Competing LLM Agents* (2026). Agents optionally accept/decline explicit offers of secret collusion tools; tests framing, not systematic magnitude of structural exploitability. 'Voluntary adoption' is not fully unscripted invention. https://arxiv.org/abs/2605.27593
- Seyedin et al., *The Politician, the Liar, and the Obedient Worker* (2026). Hierarchical organization experiments; manager salary and private deals alter behavior. Does not report ex ante coalition-gain prediction. https://arxiv.org/abs/2608.09574
- Keppo et al., *On the Fragility of AI Agent Collusion* (2026). Pricing collusion responds to heterogeneous patience, data access, agent count and algorithm diversity. Does not predict empirical formation probabilities from coalition distribution measures. https://arxiv.org/abs/2603.20281
- Guo et al., *Coalition Formation in LLM Agent Networks* (2026). Formal game-theoretic coalition dynamics for beneficial QA collaboration, not unauthorized harmful coordination. https://arxiv.org/abs/2604.14386
- Liu et al., *Breaking the Secret: Economic Interventions for Combating Collusion in Embodied Multi-Agent Systems* (2026). Sweeps incentive/deposit levels against observed collusion rates. Quantitative simulations designate colluding groups/attack modes rather than estimating purely uninstructed group formation. https://arxiv.org/abs/2604.23511
- Borah, *Bosses, Kings, and the Commons* (2026). Discrete organizational power asymmetries affect collective resource outcomes; no endogenous malicious coalition formation. https://arxiv.org/abs/2605.29062
- Collina et al., *Delegating Authorization to Misaligned Agents: Coalitional Alignment and Safe Control* (2026). Formal reviewer-panel safety conditions; safety depends on alignment of reviewer coalitions. Not an empirical endogenous-collusion predictor. https://arxiv.org/abs/2609.15803

## Plausible gap, stated carefully

A focused Undermind investigation (2026-10-22; 95 ranked candidate papers, targeted full-text reads of central works) did **not identify** an exact study that computes a coalition-specific ex ante vulnerability distribution for a formally specified LLM organization, independently varies profit/authority factors, and validates the structural measures as predictors of *uninstructed, realized causal collusion* on unseen organizational configurations.

**This is an absence from a bounded search, not proof the work is novel.** Related studies cover the ingredients individually, and the burden of evidence remains.

## Research resources and audit trail

Undermind workspace search:
https://app.undermind.ai/projects/e7b008db-6da8-40bb-b44c-5e61ab426b84?path=/Coalitional%20exploitability%20and%20emergent%20LLM%20collusion%20novelty%20audit

Consensus was requested but the connected account's monthly 30-search limit prevented new search queries; no completed new Consensus research synthesis should be claimed.

## Next literature action

After a concrete model is available, check exact closest experiments for matched manipulation and structural payoff mapping. Do not commission another general field survey merely to avoid doing empirical work.
