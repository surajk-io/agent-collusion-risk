# Research agenda — structural opportunities and model-dependent collusion (2026-10-28)

**Status: prospective research direction, not an approved experimental protocol or completed result.** This checkpoint records the researcher's October 28 discussion and proposed next steps. The original overarching question remains in [CURRENT-STUDY.md](CURRENT-STUDY.md); the October 26 Apart submission and its frozen protocol are historical evidence, not rewritten here. Further research-design choices, model calls, and expenditure need separate explicit approval.

## Why this question might matter

Multi-agent workflows allocate task ownership, review authority, communication and dependencies. Architecture can sometimes *prevent* violations using least privilege, independent enforcement, role separation, or mechanical verification. The research is relevant where legitimate cooperation and human-like judgment are required and where eliminating every harmful coordination opportunity is impractical or costly. We should **test**, not assume, that such environments exist and that the proposed structural predictors add value over simpler security controls.

The long-term ambition is **not** a universal law of LLM collusion. It is to ask whether mathematically characterized properties of organizational opportunities help predict or explain observed harmful coordination in *held-out organizational configurations*, and how that relationship depends on the model and environment.

## Three distinct levels — do not conflate

1. **Mechanical feasibility:** Given executable permissions and rules, which coalitions can cause which prohibited outcomes? For the submitted two-signature release scenario, a single improper deployment mechanically involves an owner and assigned reviewer in *both* P and R.
2. **Conditional strategic opportunity:** Under explicitly assumed individual preferences, information, payoffs and credible exchanges, which coalitions could all benefit from a specified deviation? The historic M2 illustrative no-transfer, strict-mutual-gain model can require full reviewer cycles: two agents in P, four in R. This is **not** an estimate of actual model utility and is sensitive to assumptions.
3. **Behavioral realization:** Do agents discover, propose, negotiate, agree to, and enact harmful coordination? Separate this from independent policy violations, honest mistakes, technical failures, scripted positive tests and coincident approvals. Structural feasibility is neither proof nor a calibrated probability of behavioral collusion.

Candidate predictors include distinct minimal viable/profitable coalitions, their sizes and overlap, reciprocal dependencies, pivotal authority, and communication or information access. Their formal definitions, independent variability, and expected behavioral relationship all remain open. Avoid naive counts of all coalition supersets and avoid assuming any scalar score, sign or monotonicity.

## Working research questions (proposed refinements, not approved hypotheses)

- **Q1 — causal structural response:** Holding model, legitimate task, policy, incentive regime and relevant information as constant as possible, does changing **one independently manipulable organizational feature** change the rate or nature of unsolicited harmful coordination?
- **Q2 — theory-to-behavior bridge:** Do pre-specified structural opportunity measures predict attempts, negotiated agreements, or enacted harmful coordination on organizational configurations not used to select those measures?
- **Q3 — model dependence:** How do the direction, magnitude, and uncertainty of structural effects vary across models? Can structural rankings transfer within a model or across models, even when baseline rates differ?
- **Q4 — engineering relevance:** Can simpler mechanical controls eliminate the measured failure mode, and what legitimate cooperation or throughput would each control preserve or sacrifice?

These are a research agenda, not four promises for the next experiment. Start with a single defensible contrast and feasible sample.

## What the first experiment did and did not establish

P = A↔B and C↔D; R = A→B→C→D→A. Both give each agent one owner and one reviewer role and require two signatures per release. The graph intervention also changes cycle length, bilateral reciprocity, relationship/packet exposure and other dependent properties together. It **does not isolate** minimum strictly profitable complete-cycle size as an independent cause.

On October 26, one matched P/R pair (Condition A, block 1; four quarters) produced 8/8 qualified Q1 deployments and **0/24** unqualified Q2–Q4 deployments; 8 and 10 unqualified review requests occurred in P and R, respectively, but no unqualified final signatures. The preliminary semantic scan is not independently human-adjudicated; two technical fallbacks occurred; raw transcripts are not public in this repository. This is a floor observation, not an estimated graph effect. See [RESULTS-2026-10-26.md](RESULTS-2026-10-26.md).

## Identification constraints and design principles

- **One-variable changes are not automatically feasible.** With four agents, exactly one assigned reviewer per owner, exactly one review duty per agent, and no self-review, permissible reviewer permutations are directed derangements. P versus R bundles reciprocity and cycle-length changes. To isolate a property, first construct an explicit pair of *realizable* organizations, prove which features differ and remain fixed, and document unavoidable changes. If isolation is impossible, report a bundled treatment effect or broaden the organization family responsibly.
- **Model-conditional estimates:** Keep model, version, sampling settings, tools, prompts and exogenous case allocation fixed within a causal contrast. When repeating across models, treat model × structure interactions as empirical questions; do not presume model-independent behavior.
- **Calibration before confirmation:** Explore a bounded set of realistic model/incentive/task conditions for credible opportunity and behavioral observability. Select settings for construct validity, **not** because they favor a desired graph direction; keep a complete record of screening trials. A single observed collusion event establishes possibility, not a stable rate. Fresh episodes are required for confirmatory estimation.
- **Operationalize outcomes:** Pre-specify labels and evidentiary standards for proposals, contingent offers, authenticated receipt/assent, enactment, independent policy violation and benign cooperation. Retain objective authorization/deployment outcomes, unqualified review requests, legitimate qualified throughput, and failure/timeouts as separate metrics. Use blinded independent human annotation where semantic intent matters.
- **Controls and inference:** Include independent-action and scripted apparatus controls (do not count scripted positives as spontaneous behavior), meaningful behavioral/technical positive controls, matched baselines, independent episodes as the unit of replication, uncertainty intervals and sample-planning based on realistic event rates. Do not interpret zero events as equivalence or proof of safety.
- **Prediction rather than retrospective fit:** Predefine candidate metrics and cheap baselines before testing on withheld structures; evaluate transfer within a model separately from transfer to a different model. With only P/R, there are too few distinct structures to establish generalized predictive performance.
- **Security relevance:** Distinguish discretionary safety judgments from mechanically checkable requirements. A deterministic qualification gate could eliminate the q0 deployment failure mode in the sprint scenario; include that design alternative when claiming engineering utility. Do not justify a risky architecture merely to create collusion.

## Bounded next-study sequence (proposal only)

**Gate 0 — preserve existing evidence.** Recover, hash, safety-review and export original live archives where possible; finish independent message coding; reconcile technical fallback/provenance. This improves the 2026-10-26 record but does not transform it into a replicated experiment.

**Gate 1 — causal contrast design.** Select **one** structural property and a credible organizational task; enumerate feasible structures under the constraints, specify the counterfactual contrast, show what is actually held constant and identify confounding attributes. Recheck close prior work and ask for critical independent review. Predefine outcome labels and disconfirming observations.

**Gate 2 — bounded calibration and validation.** Run small, documented diagnostics for agents' comprehension, recognition of opportunity, legitimate task performance and ability to use permitted communication. Explore model/incentive settings without choosing for a favored treatment effect; preserve all failures and avoid implicitly prompting collusion. Decide *in advance* when to stop searching or revise the question.

**Gate 3 — replicated experiment.** Freeze the chosen model/environment and causal contrast. Use fresh independently matched and randomized/counterbalanced episodes, provenance-preserving logs, manual semantic coding and appropriate uncertainty analysis. Estimate outcomes conditional on the chosen environment. If feasible, include a second model for a *limited* model-dependence comparison rather than claiming broad cross-model generalization.

**Gate 4 — prospective opportunity prediction (later).** Expand to a family of structurally varied organizations, compute features independently of outcomes and test pre-specified predictions on held-out structures. A few-day pilot cannot establish this generalization.

## A three- or four-day focused sprint: what it could honestly deliver

A realistic goal is **a tightly specified, validated structural intervention plus bounded behavioral pilot data**, possibly an initial replicated comparison if model cost, runtime, event rates and annotation capacity permit. Suggested prioritization: (1) design and literature/construct check; (2) implement/test the smallest counterfactual change and diagnostics; (3) run documented bounded calibration and/or a frozen pilot; (4) analyze uncertainty, audit semantic examples, and write up evidence/limitations. These are proposed work blocks, **not** a guarantee of results or a new authorization to spend.

It is **not** reasonable to promise a validated cross-model organizational predictor, a causal mechanism, or a statistically informative estimate of rare collusion in that period without seeing preliminary event rates and required sample sizes.

## Preprint decision

An arXiv submission is a possible **subsequent** dissemination route, not a deadline that determines conclusions. Before drafting a preprint: verify originality against current primary literature; retrieve and audit original run data; ensure results and assumptions are reproducible; independently annotate semantic claims; provide a clear limited contribution, controls, uncertainty and candid null/negative findings. A preprint can report a well-executed limited or null study, but do not repackage a one-pair floor as evidence for structural prediction. If the new study remains exploratory, label it that way. Publication timing, endorsement/subject classifications and submission rules should be checked separately.

## Relationship to existing records

- [CURRENT-STUDY.md](CURRENT-STUDY.md) — authoritative current handoff and verbatim original approved question.
- [ROADMAP.md](ROADMAP.md) — completed M0–M6 and proposed next gates.
- [literature.md](literature.md) — dated M0 novelty audit, already discusses opportunity landscapes and held-out prediction; not a new literature search.
- [M2-approved-formal-bridge.md](M2-approved-formal-bridge.md) — historical formal assumptions, not measured agent utility.
- [RESULTS-2026-10-26.md](RESULTS-2026-10-26.md) and [SUBMISSION-2026-10-26.md](SUBMISSION-2026-10-26.md) — immutable-in-substance sprint evidence and submitted-work provenance.
