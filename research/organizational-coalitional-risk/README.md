# Organizational coalitional risk

**Current status:** One four-quarter matched P/R study pair completed in the Apart AI Collusion Research Sprint (26 October 2026); no unauthorized final approvals or deployments observed. The planned second block and diagnostic control arms were **not executed**. [Latest status](CURRENT-STUDY.md) · [Measured outcomes and caveats](RESULTS-2026-10-26.md) · [Submitted report record](SUBMISSION-2026-10-26.md).

## Overarching research question

> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Long-term goal:** Design agent organizations that resist harmful coordination **while retaining legitimate cooperation and productivity**.

## Current working research focus (approved 29 October 2026)

> How do mathematically characterized properties of organizational structure interact with agent incentives and repeated interactions to shape the emergence, stability, and dynamics of collusion among task-specialized LLM agents?

This **refines the working emphasis**, not the historical sprint question. The primary target is intentional collusive coordination, **not** all harmful assistance or coordinated task behavior. Study differences in behavioral *responses* to incentive and structural interventions, including potential reciprocal agreements and persistence, rather than seeking a universal absolute collusion rate. The proposed magnification of incentive effects by structural exploitability is a **tentative hypothesis**. Mechanically feasible violations, modeled mutually profitable coalitions, and observed collusion must remain separate. See [29 October agenda refinement](RESEARCH-AGENDA-2026-10-28.md#october-29-refinement--approved-working-direction-not-a-protocol).

**Immediate next milestone:** Design a controlled structure-by-incentive contrast and collusion-specific evidence/annotation standards. No new experiment, model calls, or budget have yet been approved.

## Conceptual model

1. **Institutional design:** local objectives, permissions, decision rights, communication, information and starting state.
2. **Ex ante coalitional opportunities:** which joint deviations are feasible; minimal coalitions; potential individual gains and costs; commitment credibility; discoverability and coordination burden.
3. **Observed outcomes:** offers, reception/assent, genuine negotiation, independent violations, technical mistakes, deployed harm and legitimate throughput.

This is a **hypothesis about explanatory structure**, not an established mediated causal chain. Never infer actual collusion from a graph motif, a hidden software bug or one unsafe approval.

## Earlier prospective framing (2026-10-28; refined above on 29 October)

**The P/R study is a first example, not the intended scope of the research.** The longer-term question is whether mathematically characterized organizational coalition opportunities are informative about *observed* harmful coordination, first within a particular model/environment and eventually across held-out structures and different LLMs. The framework explicitly allows that different models may have different baseline propensities and respond differently to the same structural incentives. A universal model-independent risk predictor is **not** assumed.

The next scientific objective is to identify **one structural property and a realizable controlled intervention** that changes it while holding other relevant conditions fixed as far as possible. The P/R contrast is a bundled graph intervention: it changes direct reciprocity, complete mutually profitable cycle length, and information/relationship patterns together. Further comparisons must not automatically attribute any P/R effect to one of these. The candidate relationship between a formal opportunity measure and actual behavior is a hypothesis, not a finding.

Proceed in stages: bounded construct-valid calibration for a model/environment where opportunities can be understood and harmful coordination is observable; freeze an independently replicated causal contrast with outcome labels for offers, agreements, actions and legitimate productivity; test model dependence when feasible; only later ask whether pre-specified metrics predict outcomes on held-out organizational structures. Keep exploratory selection data separate from confirmatory trials and preserve nulls.

Engineering relevance is conditional: if a mechanically enforced verification gate eliminates a failure mode without undermining legitimate work, that can be preferable to relying on behavioral compliance. The scientific question concerns remaining coordination risks and trade-offs, not defending unnecessarily permissive architectures.

[Full prospective agenda, methodological gates and limits](RESEARCH-AGENDA-2026-10-28.md). **No new behavioral calls or protocol changes are approved by this document.**

## First scoped research contribution

In a four-agent software organization, compare **P: two direct reciprocal reviewer pairs** and **R: a four-agent review cycle**, keeping one owner task and one reviewer task per agent and the same two-signature release gate.

- **Mechanical possibility:** Two signatories can improperly deploy a release in either graph. There are different sets of eligible minimal owner–reviewer pairs.
- **Modeled strict mutual gain:** Under illustrative additive owner bonuses, positive reviewer costs, compliant outsiders and no transfers, everyone benefiting requires a complete directed reviewer cycle (two-agent cycles in P, four-agent in R). **This is conditional mathematics, not an LLM preference estimate.**
- **Independent-action null:** Closed cycles may be more frequent in P without anyone negotiating; therefore a cycle count is not collusion evidence.
- **Observed first pair:** Both graphs deployed 4/4 qualified Q1 releases and 0/12 unqualified Q2–Q4 releases; preliminary message review found no explicit reciprocal offer, but independent human adjudication is outstanding.

The submitted sprint contribution is an **exploratory formal-and-apparatus study with one matched behavioral pair**, not an experimentally established rule about safe topologies or collusion prevalence.

## Find the artifacts

| Purpose | Link |
|---|---|
| Prospective research agenda (28 Oct) | [RESEARCH-AGENDA-2026-10-28.md](RESEARCH-AGENDA-2026-10-28.md) |
| Complete milestone status | [ROADMAP.md](ROADMAP.md) |
| Current authoritative decisions and limitations | [CURRENT-STUDY.md](CURRENT-STUDY.md) |
| Sprint results | [RESULTS-2026-10-26.md](RESULTS-2026-10-26.md) |
| Submission snapshot | [SUBMISSION-2026-10-26.md](SUBMISSION-2026-10-26.md) |
| Literature and novelty boundary | [literature.md](literature.md) |
| Original scenario and review | [M1-approved-scenario.md](M1-approved-scenario.md), [M1-design-review.md](M1-design-review.md) |
| Formal derivation | [M2-approved-formal-bridge.md](M2-approved-formal-bridge.md) (historic vulnerability-based assumptions; see CURRENT-STUDY for q0 distinction) |
| Implemented experiment | [mainstudy README](M4-harness-foundations/mainstudy/README.md) |
| Frozen F1 engineering smoke | [f1 README](M4-harness-foundations/f1/README.md) |
| Old designs and predecessor research | [Archive index](../archive/README.md) |

**Preservation policy:** Original approved proposals, experimental source, fixture hashes, execution gates and historical logs remain unchanged as evidence. 'Unapproved' banners inside dated old documents describe their time of writing and are **not** current-state instructions. Raw behavioral archives are not in this repository.