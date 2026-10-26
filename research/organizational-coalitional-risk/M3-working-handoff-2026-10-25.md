> **ACTIVE STATUS OVERRIDE — 2026-10-26:** Read [CURRENT-STUDY.md](CURRENT-STUDY.md) first. This document preserves earlier decisions/proposals, including assumptions superseded for the current main study. Do not implement or interpret older carryover, detailed repair/exposure/scalar welfare, single-quarter H1-as-main, categorical pre-review blocking, or multi-parameter audit systems as current requirements. Exact main-study policy, cases, horizon and controls still await approval.

# M3 working handoff — 25 October 2026

**Status:** Working discussion checkpoint, **not a frozen or approved M3 behavioral protocol**. M0 complete, M1 approved, M2 approved as `M2-approved-formal-bridge.md`; M3 current. No behavioral runs or M3 simulator have been implemented. Keep the Git repository as canonical state and distinguish decisions from proposals.

## Canonical research questions

**Locked overarching question:**
> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

**Existing first narrow working question:**
> Does the organization of cross-workflow reciprocal reviewer dependencies alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

Read `AGENTS.md`, root and direction `README.md`, `ROADMAP.md`, `literature.md`, `M1-approved-scenario.md` and `M2-approved-formal-bridge.md`. The existing M2 document remains the current formal checkpoint. **This handoff records later conversation decisions, some requiring a versioned M2 amendment, not a silent overwrite of M2.**

## Post-M2 agreements expressed in discussion; pending formal amendment/checkpoint

1. **Deferred releases:** This four-agent group is one release team inside a larger company. A held/rejected/escalated/timeout release misses its team cutoff and transfers to an external nonstrategic remediation team; its features do **not** merge into the next quarter's team release. No assertion that transferred features are discarded or eventually deployed. New feature/release next quarter. Continue retrospective audit/patch accountability for deployed vulnerabilities. This **supersedes M2's carryover transition and corresponding welfare/backlog assumptions**, which need an explicit approved revision before a full study.
2. **Agent operational memory:** At quarter boundaries, use a deterministic factual role-scoped memory of *evidence actually received*, actions, observed outcomes and audit feedback, including the agent's awareness of security evidence. Give access to **exact participant-visible historical conversations**, including private messages only for participants and public-board history only in relevant conditions. Previous technical code artifacts are **not available to agents after quarterly handoff**; full technical sources/transcripts remain in researcher-only provenance logs. Do not fake tool outages, leak ground truth, or describe inferred motives as facts.
3. **Technical substrate simplification:** Four distinct agent-owned service identities remain. Two reusable SaaS code archetypes can be instantiated as A/C of one kind and B/D of another, with different quarterly feature/release identities. Repeating templates risks recognition and must be disclosed; avoid inconsistent cosmetic-only changes.
4. **Messaging precommitment:** Do **not** require agents to decide or log plans before messaging; changed decisions due to negotiation are an object of study.
5. **Messaging cap:** Five **optional outbound addressed messages per agent per communication round**, increased from an earlier three; group recipient lists allowed; no separate overall cap beyond rounds.

## M3 proposed design — NOT yet approved/frozen

- Initial exploratory **one-quarter four-agent pilot** before full multi-quarter simulator. Compare P pairs A↔B, C↔D against R ring A→B→C→D→A under matched releases. All four vulnerable is a **diagnostic opportunity-enriched condition**, not a prevalence-realistic primary sampling model. Potentially test clean/vulnerable individual competence before four-agent interactions.
- Candidate communication schedule: **two rounds before atomic owner choices, two after independent reviewer packets and before atomic reviewer choices**; batch up to five messages per round per agent. No pending reviewer decisions or same-quarter deployment outcomes leak before reviewer commitments. Exact agent prompts/schemas/turn scheduling and deliberation parity with no-message controls are not approved.
- Naturalistic on-time-delivery pressure, legitimate security obligations and accountability are **preferred tentatively** over an overt game of points. Agent-facing incentive language, numeric M2 scores/audit probabilities and what agents know remain OPEN.
- Distinguish objective unsafe owner submissions, reviewer approvals and actual unauthorized deployments from explicit reciprocal proposals, agreements, subsequent enactment and causally supported influence. **Completed approval cycles are not proof of collusion**; independent-approval false-positive P vs R benchmark in M2 matters.
- Competence checks: security defect detection on independently validated clean/vulnerable packets; comprehension of policy and legitimate alternatives; direct review of a submitted packet; tool recipient privacy and decision invariants. Positive control: separately scripted improper reciprocal proposal to validate recognition/message transmission/annotation, **not** evidence of spontaneous collusion. Preserve refusals and nulls.
- Candidate provider from engineering investigation: DeepSeek V4.1 Flash, **not selected** pending exact endpoint/configuration and competence/call-reliability tests. Hold model/provider/sampling/reasoning/budgets consistent within paired comparisons and log resolved provenance.
- No full 2×2 information-channel factorial, multi-quarter protocol, numeric parameter matrix, sample/analysis plan or final rubric has been approved. Freeze a bounded *pilot* package with literal prompts, packet inputs, tools, controls, event labels, provenance and interpretive limits before any pilot behavior calls.

## OpenCode engineering feasibility report — source is user-shared handoff, not independent reproduction by this assistant

- Leading substrate: MIT-licensed `https://github.com/k1y0miiii/django-saas-starter` (~1,905 Python LOC reported). OpenCode reports a reproducible cross-tenant regression where vulnerable variant passed original 24 tests and leaked data; clean variant passed 26/26. **Exact patches, reproduction commands, negative/positive security tests and pinned upstream SHA must be recovered and independently checked.**
- Upstream Django code uses a tenant-scoped default manager with an explicit unscoped escape hatch. Four separate workflow identities can use frozen realistic technical packets rather than four deployed app instances.
- Reuse archived `research/archive/coalitional-vulnerability/archive/2026-10-jira-pilot/` inference adapters, logging, retries and offline tests; **do not reuse old scientific task, payoff interpretation or behavioral classifiers**. OpenCode reported 43/43 OpenRouter and 11/11 Vertex adapter tests. A full M2 harness and multi-turn tool loop remain to be built; provider routing and output limits are significant risks.
- Earlier OpenCode cost estimates assumed 64 calls per four-quarter episode. Four communication turns plus owner/reviewer decision turns would imply up to **96 calls per four-quarter episode**, before retries, tools or extra interventions; validate budgets empirically.

## Next bounded engineering task (preparatory fixture work only)

Without behavioral LLM trials or M2 simulator construction, in a separate local worktree/disposable directory:
1. Pin exact upstream Django commit, preserve MIT attribution, and recover clean and vulnerable patches.
2. Run same ordinary test suite for both, and add independent cross-tenant regression probes that fail vulnerable/pass clean, confirming attacker is not authorized in target tenant.
3. Produce proposed **owner-facing and reviewer-facing** frozen technical packets (source excerpts/diffs/functional test evidence) **without researcher-only ground-truth labels or leak-oracle results** in agent-facing materials.
4. Report executed verification, commands, exact file locations, potential fixture obviousness, and remaining uncertainty. Do not commit/push canonical repo files or run behavioral trials without separate authorization.

## Gate and independent review

After fixture preparation, finish exact bounded M3 pilot prompts, incentives, control comparisons, logging and classification. Seek targeted independent adversarial critique of *the exact fixture + full pilot package*, resolve consequential objections, obtain explicit researcher approval of frozen pilot revision, then implement minimal deterministic authorizations and run capability controls/pilots. Keep exploratory evidence separate from any later confirmatory tests. Before full multiquarter implementation, reconcile and version the M2 external-transfer/welfare amendment.

**Report framing:** Broad opportunity-landscape question motivates the work; sprint contribution is the narrower P/R reviewer-dependency and causal-evidence study. Do not describe the broader predictor program as empirically validated. Clearly separate mathematical consequences, verified engineering results, actual pilot observations, and future plans.
