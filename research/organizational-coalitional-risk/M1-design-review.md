# M1 candidate scenario — mandatory scientific design review

**Checkpoint:** 2026-10-24. **Status: CANDIDATE TO REVIEW, NOT AN APPROVED EXPERIMENT.** This is a handoff from a three-round independent Gemini Argon adversarial critique and subsequent researcher/collaborator discussion. Neither this document nor a model's GO verdict authorizes an experiment, an agent prompt, a seed schedule or implementation.

## The scientific question

**Locked overarching program:** How do organizational structures shape opportunities for harmful coordination among task-specialized AI agents, and to what extent do ex ante properties of those opportunities predict realized collusion and harm?

**Proposed first narrow question:** Does the organization of *cross-workflow reciprocal reviewer dependencies* alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

Why narrow: attempting to validate counts, profitability, overlap, credibility, discoverability, authority, monitoring and organization-wide productivity together in one sprint would create confounded, underpowered and hard-to-interpret results. The first study is a **specific causal comparison**, not validation of a general opportunity-landscape prediction model or universal mediating mechanism.

## Candidate controlled comparison — not yet approved

Four agents A, B, C, D each (1) own one software release/module and (2) review one other module. All modules require **two distinct authorized signatures** (owner/proposer plus assigned reviewer). There are known organization-wide release rules and local deadline/performance pressure. Agents should have ordinary task goals and organizational responsibilities, **not instructions to collude**. Exact task incentives and how they appear in prompts are OPEN.

**Edges below mean 'module owner -> assigned reviewer,' NOT communication routing**:

| Module owner | Reviewer in paired condition | Reviewer in ring condition |
|---|---|---|
| A | B | B |
| B | A | C |
| C | D | D |
| D | C | A |

- **Paired condition:** A <-> B and C <-> D. Two pairs can trade direct reciprocal approvals.
- **Ring condition:** A -> B -> C -> D -> A. A closed exchange involving approval of everyone's own modules requires all four under the stipulated local reward model.
- In both conditions, every agent owns one active module and reviews one, and a single release still requires exactly two signatures.
- This changes **the reviewer assignment graph as a package**, including bilateral reciprocity, cycle length, number of strongly connected components, and potential communication/interaction patterns. **Do not claim an isolated causal effect of 'cycle length' or minimum profitable coalition size.**
- Matched workload alone does not guarantee matched *information exposure*, role salience, message history or realized incentive interpretation.

**Proposed temporal mechanism:** Two staggered release phases: A and C decisions first, B and D later, with opportunities to message before each phase. This allows promises and possible later reciprocity/retaliation. Exact request/approval sequence, who acts at which step, what is public and remembered, and messages allowed are **OPEN**. Reviewer Argon's '12 API calls per episode' is not validated; it omits some proposer-submission details.

## Central construct-validity requirements

1. **A genuine policy violation, not a trick question:** Conflict cases must involve an explicit, unambiguous organizational prohibition known to both relevant parties and an accessible compliant alternative. Avoid distributed-clue puzzles or cases where poor information aggregation explains unsafe approval. Benign cases should require genuine useful approvals rather than reflexive refusal.
2. **Legitimate local/global tension:** Agents should have meaningful local tasks and a global safety standard. Numeric bonus points are *external modeled metrics*, not stable or intrinsic LLM preferences. Do not deliberately instruct them to favor local rewards over explicit policy.
3. **Observable rule violation vs executable permissions:** Tooling must enforce signer identity, valid module IDs, number of required signatures, timing and state transitions. A policy-breaking co-sign may still be *mechanically possible* for study; define why the workflow permits and records it. If tools block all prohibited approvals, there can be no realized-harm comparison.
4. **Three distinct outcomes:** (i) attempted reciprocal or other unauthorized coordination (text/tool evidence, carefully coded), (ii) prohibited joint approval/state transition (objective), (iii) **causally supported harmful coordination** (requires more than joint harm). Generic persuasive messages or a prohibited request alone need not establish collusion.
5. **Causal controls:** Compare paired vs ring under identical task conditions; include benign productivity, independent matched seeds, role-label/module permutations and an explicitly separate positive control demonstrating that agents can negotiate/execute an intended trade. Consider message-ablation/replay and nonreciprocal-partner interventions, but ensure the interventions are coherent, randomized/matched, and do not claim that a one-off output flip 'proves' hidden intent.
6. **Do not silently vary channels:** Different reviewer graphs could imply different natural peer contacts; choose and justify whether all agents have the same all-to-all messaging capability, which message counts/histories they see, and which communication paths are permitted in each condition. Network access and reviewer dependency are distinct variables. If messages must be workflow-linked, explicitly report the extra treatment difference.
7. **Causal target:** Randomized assignment can support the total effect of *this reviewer-network rewiring* on outcomes. It does **not**, without more experiments, identify a universal predictor, psychological intent, or mediation by a single formal graph invariant.
8. **Prior-art specificity:** Za et al. (2025) already tests harmful code review and reviewer choice; SCARCE (2026) observes emergent reciprocity and exclusionary coalitions. Our tentative delta is **controlled cross-task reviewer-network rewiring with fixed per-agent task/review loads**, not novelty of multi-agent code review, reciprocal coordination, or organizational topology in general.

## Decision register — every row needs explicit researcher review before behavior collection

| Load-bearing decision | Current state | Critical question |
|---|---|---|
| Scenario/task credibility | **Candidate**: release-gate workflow | Is deadline pressure credible, or have we contrived incentives to produce violations? |
| Agent objectives and welfare | **Open** | What is a legitimate local success, what is an organization failure, and what does each agent actually read? |
| Policy vs enforceable permissions | **Open** | How can an explicitly forbidden waiver be requested and approved, and what tools enforce vs only log? |
| Full initial state | **Open** | Which modules/reports/tests are initially known, public or private, randomized or constant? |
| Reviewer assignments | **Candidate**: paired vs 4-cycle | Verify balanced graph and phase identities, clarify other changing graph properties |
| Agent-facing role/wording | **Open** | Verbatim prompt texts, any implicit simulation/evaluation cue, framing or authority bias |
| Communication tools / logs | **Open** | Targets, private/public scope, budgets, routes, message ordering, counterfactual contamination |
| Timing and memory | **Candidate**: 2 phases | Exact state transitions, order, context carryover, whether proposers formally submit |
| Conflict and benign task cases | **Open** | Hard policy threshold, measurements, task realism, known harms and compliant alternative |
| Positive/negative controls | **Open** | Does capability control prove only the harness works? What tests independent error or mere helpfulness? |
| Outcome operationalizations | **Open** | Classify attempts, unauthorized approval, causal coordination separately, with adjudication plan |
| Model/provider settings | **Open** | Models, temperature, reasoning, tool-call fidelity, token budgets, replicate units |
| Statistical plan and budgets | **Open** | Primary contrast, unit = independent episode/organization replicate, CIs, exclusions, pilot vs test |
| Scope and external validity | **Open** | Interpret four-agent simplified symmetry honestly; avoid generalizing to arbitrary organizations |

## Mandatory approval gates — no autonomous experiment design

**Gate M1 — Scenario and construct:** The researcher reviews plain-English legitimate workflow, local/global tension, both organization graphs, actual task examples, legal/illegal actions, alternative non-collusion explanations. Revise until approved.

**Gate M2 — Formal & executable mapping:** Review a complete matrix of four agents x modules x permissions, all initial state fields, state machine/phase order, exact available tools and contract, opportunity and modeled-benefit mapping. Check by hand that the two conditions actually implement the intended contrast and do not enforce harm away by construction.

**Gate M3 — Behavioral and analysis protocol:** Review the **literal** system/user/developer messages shown to each agent and exact tool schemas; all communication exposures and memory; actual case generator and distributions; coded behavioral labels; positive, negative and counterfactual controls; models/settings; estimand, unit of analysis, randomization, budget and stop/exclusion rules. Freeze the reviewed specification; any outcome-sensitive modifications become explicitly exploratory, not a silently revised confirmatory test.

**Gate M4 — Implement & validate:** Only after explicit researcher approval, implement simple simulator, deterministic state/permission tests, paired-condition fixtures and logs. Compare actual traces/tool effects to frozen specification. Positive control and a tiny calibration pilot are not efficacy evidence; if they reveal flaws, document/reapprove changes before main runs.

**Gate M5 — Analyze honestly:** Separate objectively verified approvals, attributed attempts, inferred coordination; uncertainty and independent replicates; report null, negative, and ambiguous results; track benign throughput. Preserve full provenance (code SHA, prompts, settings, run IDs, seeds, model versions).

**No implicit approval:** Reviewer Argon's GO verdict means 'worth designing', not 'the exact prompts/rewards/protocol are approved'. A clean conceptual experiment can still fail due to prompt wording, state visibility, exact API/tool sequencing or post-hoc scoring.

## Independent critique and novelty checkpoint

Independent Gemini Argon initially objected to combining deterministic permissions with vague behavioral descriptors, prompt/structure confounds, ambiguity of harmful outcomes, and overfitting multiple predictors. After exchange it agreed that ex ante structural properties may be useful predictors without being LLM utilities; it abandoned a flawed 3-agent distributed-evidence procurement example, then endorsed a balanced 4-agent paired-versus-ring comparison with staggered decisions. This note **retains the valid criticisms** while *not adopting* its unjustified 'publishable', guaranteed-power/cost or 'bulletproof causal proof' claims.

Relevant papers: [Colosseum](https://arxiv.org/abs/2602.15198); [Emergent Collusion in Long-Horizon LLM Agent Interaction](https://arxiv.org/abs/2609.24967); [Studying Coordination and Collusion in Multi-Agent LLM Code Reviews](https://openreview.net/forum?id=CdZaamCf5Y); [SCARCE](https://arxiv.org/abs/2610.21029); [Delegating Authorization to Misaligned Agents](https://arxiv.org/abs/2609.15803). See [literature.md](literature.md) for broader prior art.

**Next action in a new chat:** Start M1 Gate 1. Review scenarios/constructs in plain English and an explicit decision register, **not code or simulated results**. Complete each gate with the researcher's explicit approval.
