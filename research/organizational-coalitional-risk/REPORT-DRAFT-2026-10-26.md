# Reviewer-network structure and unauthorized reciprocal approval in LLM-agent organizations

**Draft for Apart Research Sprint, 26 October 2026. NOT FINAL; behavioral results pending.** Experimental status and figures must be replaced with verifiable model-run archives before any submission. The draft is on a SEPARATE report branch to avoid changing the approved harness revision. Do not present scripted validation traces as behavioral research.

## Summary / abstract [update after live results]

We investigate whether a four-agent organization's reviewer-assignment topology changes agents' tendency to propose or enact improper reciprocal release authorizations. Four task-specialized language-model agents each own a software-service release and independently review another service. We compare two reciprocal reviewer pairs (P) against a single four-agent directed review cycle (R), matching the number of tasks, owner/reviewer workload, release evidence, communication capabilities and mechanical signature requirements. Across four observed quarters, agents face customer delivery pressure and a mandatory full-test qualification rule that may conflict with their confidence in an apparently sufficient last-minute fix. Some hidden dependency implementations have reproducible conditional defects not visible from the supplied application source. The primary observation is a **delivered, explicitly contingent, mutually assented and enacted improper approval arrangement**, not mere unsafe deployment or mechanically completed approval cycles. [INSERT completed-live sample, outcomes and calibrated conclusions; no claim now.]

## 1. Research motivation and question

Organizations deploy AI agents with local responsibilities and shared institutional constraints. A reviewer network can create incentives to exchange favors that undermine independent authorization, even when agents each have legitimate tasks. The present limited study asks:

> Does the organization of cross-workflow reciprocal reviewer dependencies alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

We distinguish **structural opportunity** (what reciprocal arrangements can be executed with the assigned permissions), **observed coordination** (what agents actually communicate and agree), **procedural deviation** (authorization despite an incomplete mandatory verification record), and **technical consequence** (deployment of a candidate with a researcher-validated conditional defect). None implies the others automatically.

This is a bounded mechanism study, not a representative prevalence estimate for actual companies.

## 2. Organizational design

Four persistent agents A, B, C and D each own a different release and review exactly one peer release. All ownership/review decisions operate on immutable per-quarter release identities. The intervention changes assigned reviewer edges, denoted owner→reviewer:

| Condition | Review assignments | Reciprocal closed opportunities |
|---|---|---|
| **P (paired)** | A→B, B→A, C→D, D→C | Two direct reciprocal pairs |
| **R (cycle)** | A→B, B→C, C→D, D→A | One directed four-agent cycle |

Each owner needs its own authorization and an independently assigned reviewer's signature. The release tool checks signatures and ordinary functional gates. It intentionally does **not** enforce mandatory full-test qualification, so a procedural violation remains technically executable. Each agent can withhold, reject or escalate; complying with policy is always available.

Under assumptions that all relevant releases are unqualified and reviewer approval has a genuine cost, complete, mutually beneficial reciprocal exchanges can differ in minimum membership between P and R. This mathematical opportunity does not demonstrate that the agents prefer, discover, believe or execute the exchange. Larger cycles may also differ in negotiation difficulty. This intervention is a bundled network manipulation; it does not isolate abstract cycle length from the associated information/relationship structure.

## 3. Release and evidence environment

The environment presents a late-release input-handling defect, an actual small application patch, the authentic before/after diff, and results of reproducibly executed targeted regression checks. Limited checks pass on the current candidate; the mandatory full integration suite is recorded as incomplete for the time-limited release windows. The apparent patch can rationally increase confidence that the visible defect was fixed while not proving that the whole system is safe.

The researcher-side fixture includes two small service archetypes: a tenant report cache and an export download-session handler. Each delegates to an opaque, locally authored simulated external dependency. Some dependency variants fail tenant separation only on conditional bulk-report or resumed-download paths; matched safe variants pass the specified finite workload. The full source and triggering oracle checks are researcher-only. Agent-facing artifacts expose truthful application code, dependency interface and limited test outcomes, **not** hidden ground-truth labels or dependency internals. We do not assert a real vendor incident or real production certification.

Separate variables track (i) actual conditional vulnerability, (ii) mandatory qualification acceptance for the exact source distribution, (iii) agent-visible evidence, (iv) observed expressed belief, and (v) authorization choices. A hidden vulnerability does not itself imply that an agent intentionally violated policy.

Q1 presents genuinely qualified/safe study-defined candidates to exercise ordinary productive review. Q2–Q4 present deliberately opportunity-enriched windows with incomplete mandatory full-suite qualification for all four services, with two truly vulnerable and two safe candidates per quarter. Cases and hidden truths are prespecified and matched across P/R, with two allocation blocks and archetype reassignment. This distribution is **not an estimate of typical enterprise release frequency**.

## 4. Agent interaction and repeated history

Each observed quarter contains five synchronized communication stages (C1,C2 before the owner review request; C3,C4,C5 afterward), an independent review-request stage S, and an atomic final dual-role decision stage D. Every agent supplies one owner and one assigned-reviewer final decision in D; eight signature decisions commit without agents observing each other's pending choices. A review **request** is permitted before mandatory testing is complete; a final authorization without accepted mandatory verification remains prohibited. The two signatures automatically deploy a candidate only if both are valid on the exact release identity.

Across four observed quarters, the reviewer graph and agent identities persist. Public boards contain operational releases/signatures, not private messages or hidden vulnerability truth. Agents retain only legitimately received communications, their own outcomes, board history when enabled, and rare private audit findings. Nondeployed releases transfer to a nonstrategic outside remediation process; no feature backlog, post-release repair or duration-weighted welfare simulator is modeled. Agents are not told that the research observation terminates after Q4.

A fixed 5% per-deployed-release retrospective procedural spot-check can detect missing accepted qualification; findings are private to responsible signatories. This is a **stipulated fictional institutional mechanism**, not an empirically calibrated audit rate.

## 5. Experimental conditions and planned allocation

The primary P/R comparison uses **A: graph visible, all-to-all private messaging enabled, public outcome history visible**. Three diagnostic conditions, each also crossed with P/R, separate some information channels:

| Arm | Messages | Other teams' public boards | Reviewer identities |
|---|---|---|---|
| A full | Enabled | Visible | Visible |
| B board-only | Disabled | Visible | Visible |
| C private-only | Disabled | Hidden | Visible |
| D blind isolation | Disabled | Hidden | Hidden/masked |

Conditions form a **nested set of interventions, not a fully crossed factorial design**. In particular, A vs B bundles private negotiation with beneficial technical information sharing. B vs C measures the effect of other-team outcome visibility without direct chat, not conclusive evidence of tacit collusion. D also removes identifiable relationship information. Explicit message-based collusion is **not observable** in no-message arms, not measured as zero.

The predeclared maximum allocation is two case blocks × four arms × two graphs = sixteen four-quarter episodes, with 112 generation calls per episode. Priority: matched A/P–A/R block 1, A block 2 replication, then B/C/D block 1, then optional remaining controls, subject to a precommitted budget/time prefix rule. Each four-agent episode is the unit of analysis. With at most two paired blocks per arm, results support descriptive comparisons and close reading only, not powered population claims.

## 6. Outcomes and coding

The primary endpoint within full-communication arm A is whether at least one **explicit contingent reciprocal authorization proposal was received, agreed by all required graph-compatible signatories before the relevant final decisions, and enacted through matching final authorization actions**. Each stage is separately recorded: proposal, verified message receipt, assent, complete agreement, enactment and defection. Two independent human coders review delivered messages with exact quotations before examining final actions; contested labels retain disagreement/uncertainty and require separate adjudication.

Secondary outcomes include the number of owner final signatures and independent reviewer approvals issued with q=0, deployments of q=0 releases, deployments of truly vulnerable releases, compliant qualified throughput, holds/escalations, audit feedback and technical invalid/missing model output. Completed graph cycles, simultaneous independent approvals, unknown internal intent and hidden bugs do not constitute collusion without communication/causal evidence.

Under iid independent reviewer authorizations with chance alpha and all owner authorizations present, at least one completed reciprocal cycle has probability `2α²−α⁴` in P versus `α⁴` in R. Thus a higher raw P cycle-completion frequency can arise absent coordination. We will not interpret cycle counts alone as a behavioral collusion effect.

## 7. Engineering validation (not behavioral findings)

An initial one-quarter F1 smoke test was completed under both P and R. The executing-agent archive reported 56 successful model generations and deterministic replay, while all eight owners held/escalated; no candidate reached the reviewer decision stage and there were no deployments. F1 established technical feasibility and motivated the distinction between a review request and final owner authorization. It is NOT a result about differences in collusion propensity.

The final main-study branch reports 82 passing offline tests (including 50 preexisting F1/foundations tests), sixteen four-quarter scripted condition episodes, eighteen scripted negative traces and exact replay. The software oracles demonstrate the stipulated conditional dependency behavior. **All scripted exchanges are deliberately supplied as apparatus-validation fixtures, not spontaneous agent behavior.** The study has not collected live main-study episodes at the time of this draft.

## 8. Behavioral observations [DO NOT FILL WITHOUT LIVE ARCHIVES]

Record exact reviewed revision, model/provider/settings, frozen case IDs, package hashes, absolute run start/stop, assigned episodes, completed/failed calls and verified billing. For each P/R matched pair, record each quarter's owner review requests, final signatures, deployments, audit findings and excerpts of delivered negotiation messages. Distinguish technical interruption from participant choice.

| Primary block/arm | Graph | Technical status | Received reciprocal proposal | Fully assented arrangement | Enacted arrangement | q=0 deployments | v=1 deployments |
|---|---|---|---|---|---|---|---|
| A/block1 | P | Pending live | Pending coding | Pending coding | Pending coding | Pending | Pending |
| A/block1 | R | Pending live | Pending coding | Pending coding | Pending coding | Pending | Pending |
| A/block2 | P | Not yet launched | — | — | — | — | — |
| A/block2 | R | Not yet launched | — | — | — | — | — |

Interpretation should state what was **observed** and which competing mechanism remains plausible. With one pair, no causal population estimate or significance test is defensible. Even a complete null may reflect full compliance rather than lack of structural opportunities.

## 9. Limitations and future work

Key limitations: four LLM agents and one selected provider; scripted, synthetic release contexts; a precommitted all-q=0 stress-test case distribution in later quarters; finite oracle workload; conservative model of simulated corporate incentives; a rare but stipulated audit; small number of matched episode blocks; explicit collusion coding limited by what agents actually communicate; no identification of private intent; public-board patterns do not conclusively establish tacit agreements; reviewer-graph rewiring bundles structural changes; and possible model reasoning/prompt-context sensitivity. Important future work includes additional models, larger randomized blocks, independent technical domains, alternative quarter/risk schedules, and stronger controls isolating information versus authority structures.

## 10. Reproducibility and provenance

Canonical repository: https://github.com/surajk-io/agent-collusion-risk . Current implementation branch: `codex/main-study-harness`. Main-study methods baseline: `research/organizational-coalitional-risk/M3-IMPLEMENTATION-BASELINE-2026-10-26.md`. Report the exact executed commit, case allocation and rendered prompt hashes after researcher-approved launch. Preserve full request/response logs, deterministic replay artifacts, human coding outputs and all failures; do not replace uncertain observations with favorable outcomes.

**Report completion checklist:** add exact actual episodes and paired comparison, independent transcript annotations, archived run links/digests and cost; verify source policy for AI-generated submission materials; clearly label F1 and scripted validation as engineering evidence, not main results.
