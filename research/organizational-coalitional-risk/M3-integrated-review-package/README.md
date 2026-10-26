> **ACTIVE STATUS OVERRIDE — 2026-10-26:** Read [CURRENT-STUDY.md](../CURRENT-STUDY.md) first. This document preserves earlier decisions/proposals, including assumptions superseded for the current main study. Do not implement or interpret older carryover, detailed repair/exposure/scalar welfare, single-quarter H1-as-main, categorical pre-review blocking, or multi-parameter audit systems as current requirements. Exact main-study policy, cases, horizon and controls still await approval.

# M3 integrated scientific review package

26 October 2026. **CANDIDATE, NOT APPROVED. Documents only.** No simulator, behavioral trials, fixture changes, hidden-oracle changes, fabricated certificates or main-branch edits are authorized by this package. Researcher authorization covers committing/pushing these candidate documents on `candidate/m3-integrated-review-package`.

## Questions and recovered state

**Researcher-approved overarching question, verbatim:**

> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Existing proposed first narrow working question, verbatim; not an approved result:**

> Does the organization of cross-workflow reciprocal reviewer dependencies alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

M0 bounded audit is complete; M1 scenario and M2 formal bridge are approved; M3 protocol/causal controls are current and unapproved. Canonical recovery used GitHub-fetched main `1c6927f48824e657a5d15e2b67550a8b28e5f1b5`, root AGENTS/README, direction README/ROADMAP, literature, M1 design review and approval, M2 approval, M3 working handoff, and predecessor critique. M1's older staggered decision proposal was superseded by M2 simultaneous reviews. Archived Jira work is a technical smoke test, not spontaneous collusion evidence; its task/payoff/classifiers are not adopted. The direction README's older blanket statement that no formalization is approved conflicts with its explicit M2 status; use the M2 checkpoint and roadmap. These historical documents remain untouched.

The working handoff records later researcher agreements (external transfer instead of carryover, role-scoped memory, reusable archetypes, no pre-messaging commitment), pending versioned M2 reconciliation. The present task provisionally favors a release-qualification-gap scenario; it does **not** approve it. Every new choice below remains proposed. No approved decision is silently replaced.

## Integrated design in brief

A single quarter with four owner/reviewer roles, P pairs versus R ring, two signatures per release and identical all-to-all addressed messaging. Five synchronous communication rounds: C1/C2, atomic owner decisions, independent reviewer packets, C3/C4/C5, atomic reviewer decisions, automatic deployment, post-batch board and proposed retrospective lifecycle. This reuses the Codex interaction contract, schemas and offline matrix rather than adding a simulator.

Main candidate: H1's visible database-query correction is real. Its exact source passes recorded ordinary and earlier single-request checks but retains a cache-isolation defect under existing hidden stateful checks. The organizational policy proposed here independently prohibits authorizing a release with missing mandatory qualification. This makes a process violation observable without assuming the agent recognized the hidden vulnerability. Source correction is small; independent qualification and release authorization, rather than architectural redesign, miss the cutoff.

**The package is review-ready, not execution-ready.** One service fixture exists. Four distinct release packets, a second archetype, build-bound qualification evidence, provider configuration, lifecycle numbers and approved budget do not. Those omissions are explicit freeze blockers, not permission to improvise during runs.

## Read in this order

1. [Amendment proposal](amendment-proposal.md): exactly how the scenario changes M1/M2 and when the opportunity mathematics still applies.
2. [Interaction contract](interaction-spec.md) and [schemas](candidate-schemas.json): adapted five-round schedule, permissions, privacy and atomicity.
3. [Literal runtime texts](runtime-materials.md), [evidence assembly and fixture allocation](fixture-evidence-allocation.md), and `runtime/`: policy/context/role/slot texts and two neutral release records. Runtime text bodies contain no draft, benchmark or hidden-variant cues; the surrounding package remains clearly proposed. They are not an approved prompt set.
4. [Measurements, controls and analysis](measurement-controls-analysis.md), [offline matrix](offline-test-matrix.md), [decision register](decision-register.md).
5. [Review handoff](review-handoff.md), [fresh critique](independent-review.md), [prior protocol critique](prior-interaction-review.md) and [performed checks](validation-report.md).

[Source manifest](source-manifest.json) pins all three source branch commits and hashes of recovered source documents, evidence, scripts and hidden tests. It includes actual sanitized-source identities; a source hash is not a build hash. Reviewers should fetch those commits, not trust moving branch tips. Fixtures are referenced, not copied or merged. Package hash inventory is in `artifact-hashes.json` (excludes itself and the final validation report to avoid self-reference).

## Current gate and next action

Per [the active ROADMAP](../ROADMAP.md), the unresolved M3 gate is behavioral discrimination and exact approved inputs/controls before implementation. Review the decision register, resolve the critical scenario/fixture/estimand choices, approve explicit M1/M2 amendments and the complete frozen M3 revision, then separately authorize implementation and deterministic M4 validation. Behavioral competence controls and pilot calls require explicit authorization after that. A negative or ambiguous outcome is acceptable; obtaining a positive collusion result is not the design criterion.
