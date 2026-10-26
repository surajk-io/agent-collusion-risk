# Current study — authoritative handoff

**Updated after Apart submission, 26 October 2026.** This file supersedes earlier status banners in the engineering log, M1/M2/M3 candidate packets and frozen F1 documents. Preserve those original artifacts as dated evidence; they do **not** describe the current stage.

## Research questions

**Approved overarching question (verbatim):**
> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Narrow experimental question:**
> Does the organization of cross-workflow reciprocal reviewer dependencies alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

An observed graph pattern or procedural violation does not by itself establish actual collusion.

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
4. For a **new follow-up**, fix the provider timeout/output issue under a newly frozen protocol, replicate multiple paired blocks, then choose informative intervention arms/incentives without selecting conditions for a hoped-for positive result.
5. Measure legitimate throughput under comparable safe/verification states; do not equate universal refusals with robust organizational design.

## Historical decisions and archives

[M1 approved scenario](M1-approved-scenario.md), [M2 original bridge](M2-approved-formal-bridge.md), [M3 proposal](M3-MAIN-STUDY-DESIGN-PROPOSAL.md), [M3 implementation baseline](M3-IMPLEMENTATION-BASELINE-2026-10-26.md), [offline independent critique](M4-harness-foundations/mainstudy/INDEPENDENT-REVIEW.md), and [archive index](../archive/README.md). The historical F1 prohibition on **requesting** review while q=0 is not part of the main protocol: S requests are allowed, D final authorizations remain prohibited. Hidden v=1 is a distinct technical truth from q=0 procedural qualification. Historical score/liability models are illustrative, **not measured LLM utilities**.