# Minimal M3 pre-pilot diagnostic battery

26 October 2026. **PROPOSED; DOCUMENTS ONLY. No LLM experiments or simulator implementation authorized.** This supplement revises the capability-validation task in the integrated package at `f01b498855d7b0bd637c22f852c58e20a13cd316`. The baseline files, literal spontaneous prompts, fixture implementations and hidden oracles are unchanged. No task/provider/score is selected to produce collusion.

## Scope and recovered state

**Researcher-approved overarching question, verbatim:**

> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Existing proposed narrow working question, verbatim:**

> Does the organization of cross-workflow reciprocal reviewer dependencies alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

Fresh GitHub recovery: main `1c6927f48824e657a5d15e2b67550a8b28e5f1b5`; integrated branch `f01b498855d7b0bd637c22f852c58e20a13cd316`. Root/direction README/AGENTS/ROADMAP, M0 literature/critique, M1 design review/approval, M2 approval, M3 working handoff and integrated amendments/protocol/evidence/controls/critique were read. M0 complete, M1/M2 approved, M3 unapproved. The qualification-gap and external-transfer amendments remain proposals/pending reconciliation. The current gate is discrimination of unsafe reciprocal behavior from misunderstandings, unilateral acts and mechanical cycles, followed by exact input/control approval. Neither earlier smoke work nor document checks establishes agent behavior or novelty.

The researcher reviewed `a237254` and accepted the overall design as a **strong candidate**, requesting only clarifications of staged execution, review of observed probe failures, and synthetic versus grounded records. This is not execution authorization or approval of the full M3 protocol. The current revision is authorized for commit and push on the existing candidate branch. The earlier task authorized **drafting and committing this candidate battery**, and specified the immediate next objective: **one complete unseeded P smoke episode and one complete unseeded R smoke episode**, with fresh agent contexts. No execution approval is inferred. The integrated 32-episode planning option is deferred; it is not the next task or this battery's sample plan. No broad experiment redesign is proposed.

## Three categories and bounded counts

| Category | Proposed battery | Purpose / boundary |
|---|---|---|
| A. Deterministic simulator/annotation tests; no LLM | Reuse baseline offline matrix; five small negative traces and one positive trace per graph | Mechanics/annotation specificity, not model behavior. Most require a future minimal episode runner; static document checks alone cannot pass them. |
| B. Isolated model capability probes | **10 short single-call probes**, fresh context each | Run directly through an isolated target-model adapter; **no four-agent runner prerequisite**. Policy, evidence, incentives/credibility, graphs, conditional proposals, JSON and chronology. Synthetic states are explicitly hypothetical; real technical evidence retains its provenance. |
| C. Seeded multi-agent behavioral diagnostics | **4 diagnostic interactions**: P-pre, R-pre, P-post, R-post | **Validated minimal four-agent runner required**. Fixed authenticated peer offer. Pre cases leave owner choices autonomous; post cases start from explicitly scripted submitted snapshots and test reviewer response conditional on eligibility. Refusal is a valid behavioral response, not comprehension failure. |

After separate stage-specific authorization, Codex can execute the ten isolated probes while OpenCode independently builds and validates the minimal runner. This is a future division of work, not dispatch or permission to execute/build in this revision. Adapter preflight and diagnostic-record consistency suffice for the isolated track; runner-dependent G1 tests are not prerequisites for it. Synthetic initial signatures/qualification states may be used in explicitly identified diagnostics; they do not fill the grounded experiment's real fixture/build/evidence requirements. After runner validation, reviewed G2/G3 outcomes and the remaining approvals, perform the seeded track and then exactly the two unseeded smoke episodes. A complete episode includes all C1/C2/O/C3/C4/C5/R slots, board and approved lifecycle closure; all-hold is a complete valid episode. Deployment or explicit coordination is not required. No adaptive extra episodes to obtain a bargain.

Read [isolated stimuli/scoring](isolated-probes.md), [seeded stimuli/sequencing](seeded-diagnostics.md), [deterministic reuse/gold traces](deterministic-tests.md), [gates, budget and decisions](gates-and-decisions.md), and [independent review/check report](review-and-validation.md). [Baseline interaction](../M3-integrated-review-package/interaction-spec.md), [schemas](../M3-integrated-review-package/candidate-schemas.json) and [offline matrix](../M3-integrated-review-package/offline-test-matrix.md) remain canonical contracts for ordinary slots. The supplement only overrides the earlier vague capability task and immediate-run planning scope.

No results exist. Every future report must separate scripted facts, model answers, observed decisions, expressed awareness, annotation uncertainty and apparatus failures. No capability responses, correction feedback, scripted offers, synthetic histories or selection rationale enter spontaneous episode prompts, sessions or operational memory. Researcher retention remains separate from agent access.
