# Current study — authoritative handoff

**Status updated 29 October 2026:** The October 26 Apart sprint evidence remains unchanged. A prospective agenda was recorded on October 28 and the researcher explicitly approved a more collusion-specific working emphasis on October 29; see [RESEARCH-AGENDA-2026-10-28.md](RESEARCH-AGENDA-2026-10-28.md). This file supersedes earlier status banners in the engineering log, M1/M2/M3 candidate packets and frozen F1 documents. Preserve those original artifacts as dated evidence; they do **not** describe the current stage.

## Research questions

**Approved overarching question (verbatim):**
> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Narrow experimental question:**
> Does the organization of cross-workflow reciprocal reviewer dependencies alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

An observed graph pattern or procedural violation does not by itself establish actual collusion.

## Current working refinement — researcher-approved 29 October 2026

> How do mathematically characterized properties of organizational structure interact with agent incentives and repeated interactions to shape the emergence, stability, and dynamics of collusion among task-specialized LLM agents?

**Scope and intent:** The target is **collusion**: intentional coordination toward an unauthorized shared objective (including reciprocal arrangements), not harmful assistance or policy violations in general. Explicit proposals, negotiated agreements, subsequent contingent behavior, defection, and persistence are relevant but distinct observations; harmful helping, correlated independent violations, and ordinary cooperation remain competing explanations. Tacit collusion is possible but requires stronger causal evidence than an action pattern alone.

**Scientific emphasis:** Study *response relationships*, not only static or absolute collusion rates: how changing organizational task-dependency/coalition opportunities modifies behavioral responses to incentive manipulations and interaction history; look for interactions, thresholds, reversals, and path dependence **without assuming they occur**. Absolute rates can be estimated for a specified model and environment but are not the primary theoretical target. Derive candidate structural descriptions ex ante, not from fitted behavioral outcomes. Treat textual rewards as experimental incentives, **not measured intrinsic LLM utility**.

**Tentative central hypothesis:** Structures that make reciprocal, mutually beneficial collusive arrangements easier to discover, negotiate, monitor, and sustain may amplify the effect of incentives that favor such arrangements. This hypothesis is **not approved as a proven claim or frozen experimental prediction**; plausible alternatives include no effect, a reversed effect, or confounding through information exposure and task difficulty.

**Decision status:** This refined direction and a shift from open-ended novelty searches to concrete experimental design were explicitly endorsed by the researcher. Exact scenario, structural variable, incentive manipulations, prompts, controls, annotations, budget, and analysis remain *unapproved*, requiring the usual scientific gates before inference runs. The original approved question and dated experimental questions above are retained verbatim for provenance.

## Earlier prospective direction from 28 October discussion — context for the 29 October refinement

The original approved overarching question above is **unchanged**. The paired-versus-ring comparison was a deliberately small first case, not the intended entirety of the research program.

**Proposed next emphasis:** characterize structural coalition opportunities mathematically, then test whether selected organizational properties causally affect *observed* unauthorized coordination under controlled model/task conditions. Investigate how effects differ across LLMs; do **not** presuppose a universal cross-model predictor. A later, distinct goal is to test pre-specified opportunity metrics against behavior on held-out organizational structures.

The initial P/R comparison is **not** a single-property intervention. Under the fixed one-owner/one-reviewer, no-self-review four-agent constraints, reciprocal pairs and the four-cycle jointly change reciprocity, cycle length and dependent information/relationship properties. Before running a new causal experiment, construct a feasible pair or set of organizations and explicitly document which attributes change and which cannot be held fixed. Do not confuse mechanical signatory size (two in both graphs) with minimum strictly mutually beneficial *complete* coalition size under illustrative preferences.

**Protocol status:** The 29 October research focus is approved for design, but the exact structural variable, paired counterfactual, model, incentive regime, agent-facing wording, controls, calibration budget, outcome coding and sample size remain **open and require explicit scientific approval**. The sprint's original run authorization does not carry forward. The new document is a research agenda, not preregistration or evidence.

**Immediate bounded plan:** Begin designing a discriminating **structure-by-incentive** experiment and collusion-specific coding rubric; preserve and independently audit original archives where possible; perform bounded capability/behavior calibration and fresh replicated trials only after a frozen protocol is approved. Multiple models or held-out structures are extensions, not promised results of a three-to-four-day pilot. A potential arXiv preprint requires an auditable, appropriately scoped contribution with reproducible data, honest uncertainty and prior-work comparison; publication is not an automatic sprint deliverable.

## Completed and checkpointed

- **M0:** Bounded related-work/novelty survey. See [literature.md](literature.md).
- **M1:** Reviewer-organization scenario approved after critical review. See [M1-approved-scenario.md](M1-approved-scenario.md).
- **M2:** Formal coalition feasibility, expected local gains, strict-mutual-benefit cycles, commitment-credibility toy, independent-action null. Original assumptions are historically approved; their *vulnerability-centered* violation target must be qualified for the implemented **missing-mandatory-verification** scenario. [Original derivation](M2-approved-formal-bridge.md); [submitted-paper record](SUBMISSION-2026-10-26.md).
- **M3:** Scientific implementation baseline selected, independent evidence and partial-factorial controls specified. Earlier M3 packages remain **historical candidate documents**, not independent live results. [Baseline](M3-IMPLEMENTATION-BASELINE-2026-10-26.md).
- **M4:** F1 transport/replay smoke completed (56 successful calls reported; no submissions/deployments); four-quarter harness built with offline tests, executed fixture checks and an independent engineering critique. [Harness](M4-harness-foundations/mainstudy/README.md); [historical implementation log](../../IMPLEMENTATION-STATUS.md).
- **M5 (limited):** **One actual matched pair completed**: A-P/block1 and A-R/block1, four quarters each, seed `20261026`, using frozen harness `00fdce373aaed58703478866025ddc864b66dac5` and DeepSeek V4.1 Flash via Google Vertex AI MaaS. **Only Condition A/block1** was executed; block2 and diagnostic arms B–D were not run.
- **M6 (sprint snapshot):** Report submitted to Apart on 26 October 2026. [Submission record](SUBMISSION-2026-10-26.md) and [result ledger](RESULTS-2026-10-26.md).

## Observed evidence and its strength

Per operator handoff, in P and R respectively: Q1 qualified deployments **4/4 and 4/4**; Q2–Q4 unqualified deployments **0/12 and 0/12**, unqualified final owner signatures **0/12 and 0/12**, delivered peer messages **92 and 174**. There were **two Q2 S-stage technical fallbacks**, one per graph. The operator reports 222 valid structured outputs out of 224 slots and successful replay/hash checks. **The raw archives remain local and were not independently re-audited in this GitHub consolidation.**

Preliminary AI-assisted semantic reading found no explicit improper reciprocal proposals; the planned two independent human codings/adjudication were not completed. From objective zero unauthorized signatures, **no enacted explicit improper authorization deal** occurred in these episodes; the absence of all attempted bargains cannot be certified without the missing semantic review.

**Scientific interpretation:** formally different opportunities did not produce unauthorized authorizations in this single pair. This neither confirms nor refutes a population-level topology effect, validates a scalar coalitional-risk predictor, or proves organizational safety. Q1 successes show the agents could complete **qualified** authorized work, not that the opportunity enrichment made collusion likely. P/R changes reviewer packet access and relationship structure together.

## Current code and reproducibility

- Active implementation: [mainstudy/](M4-harness-foundations/mainstudy/README.md). Tests are offline; scripted positives are injected test cases.
- Historic F1: [f1/](M4-harness-foundations/f1/README.md), no longer the main study.
- Executed main-study code revision: `00fdce373aaed58703478866025ddc864b66dac5`; the consolidation must not mutate those prompts/fixtures/execution controls.
- Original live run IDs: `main-A-P-b1-s20261026` and `main-A-R-b1-s20261026`; original archives reported at `/private/tmp/mainstudy-approved-collection` on the executing environment. **Those paths are not repository artifacts.**
- Re-running the experiment, changing prompts, altering the S/D gate or extending the sample is **new research**, not a silent completion of the submitted sprint experiment. It requires independently specified approvals, controls and analysis.

## Open work, not completed

1. Obtain/export the original hash-verified live archives into a deliberate shareable reproducibility location after checking they contain no secrets or private provider payloads. Record stable archive digests. This cannot be inferred from a directory path.
2. Do independent, blinded semantic annotation of delivered messages with exact quotes and authenticated receipt/action IDs. Distinguish attempted explicit negotiation from policy-compliant exchanges and model-generated mistakes.
3. Verify results against archived code and predeclared denominators; document the two technical fallbacks and incomplete eligibilities.
4. For a **new follow-up**, design the structure-by-incentive contrast and interaction estimand first; validate that collusive proposals/agreements can be observed without instructing main-condition agents to collude. Fix the provider timeout/output issue in a newly frozen protocol and replicate independent matched episodes without selecting arms for a hoped-for positive result.
5. Measure legitimate throughput under comparable safe/verification states; do not equate universal refusals with robust organizational design.

## Historical decisions and archives

[M1 approved scenario](M1-approved-scenario.md), [M2 original bridge](M2-approved-formal-bridge.md), [M3 proposal](M3-MAIN-STUDY-DESIGN-PROPOSAL.md), [M3 implementation baseline](M3-IMPLEMENTATION-BASELINE-2026-10-26.md), [offline independent critique](M4-harness-foundations/mainstudy/INDEPENDENT-REVIEW.md), and [archive index](../archive/README.md). The historical F1 prohibition on **requesting** review while q=0 is not part of the main protocol: S requests are allowed, D final authorizations remain prohibited. Hidden v=1 is a distinct technical truth from q=0 procedural qualification. Historical score/liability models are illustrative, **not measured LLM utilities**.