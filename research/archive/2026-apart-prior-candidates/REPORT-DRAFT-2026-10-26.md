# Organizational Structure and Coalitional Opportunity in LLM Release Review: A Paired-Reciprocity versus Four-Cycle Study

**Apart Research AI Collusion Sprint · 26 October 2026 · Research report in progress (main-study results pending)**  
**Author:** Suraj Kumar · **With:** Apart Research  
**Status discipline:** Theoretical results and offline engineering checks below are established only under their stated models/tests. No spontaneous main-study behavior is claimed. Replace the provisional abstract and empty results cells only after verified run archives and independent coding.

## Abstract — provisional, update after observed runs

As task-specialized AI agents gain authority over organizational workflows, harmful coordination can depend on how authorization rights, local incentives and information are distributed—not simply on the capabilities of individual agents. We develop a conceptual separation between an organization's **coalitional opportunity landscape** and the agents' **observed coordination**, then study one controlled instance: a four-agent software organization in which every agent owns a release and independently reviews another. The experimental contrast preserves workload, communication affordances and two-signature authorization requirements while rewiring two reciprocal reviewer pairs (P) into one four-agent cycle (R). A formal model distinguishes mechanically feasible unauthorized releases from coalitions offering strictly positive modeled gains to every member; it also derives an independent-approval null under which graph-completion frequencies can differ without collusion. The implementation uses four sequential quarters, legitimate qualified releases, and opportunity-enriched late fixes whose mandatory verification is incomplete and whose technical truth is independently established. The primary prospective endpoint requires an explicit, received, mutually assented, enacted exchange of improper authorizations. Offline tests validate the apparatus, **not** spontaneous collusion. [INSERT observed primary P/R comparisons, uncertainty, and conclusions after independent archive verification.]

## 1. Introduction: from organizational structure to harmful coordination

AI-agent organizations can combine legitimate specialization with decentralized authority. An agent may own a release, another may approve it, and both may have customer-delivery objectives alongside an institution-wide safety policy. This arrangement can create a conflict: mutually helpful shortcuts may benefit local operational performance while defeating independent verification. Structural design can therefore affect **what harmful coalitions could achieve** before we ask whether agents discover, want, trust or enact such opportunities.

Our overarching question is: **How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?** The long-run aim is to identify designs that reduce harmful coordination **without needlessly suppressing ordinary cooperation and productive release work**.

We organize this as a three-layer framework: **(A) institutional configuration** (permissions, reviewer dependencies, information, communication, duties, incentives, initial state) → **(B) ex ante coalitional opportunities** (feasible joint deviations; minimal/pivotal coalitions; possible individual gains and organizational costs; coordination and commitment requirements) → **(C) behavior and outcomes** (offers, communication, assent, unsafe acts, deployments, delivered value and technical risk). This arrow is a **research hypothesis**, not an established mediation claim: structure can also act directly through role expectations, exposure to evidence and perceived authority. Theoretical opportunities are not intrinsic LLM utilities or evidence of intentional collusion.

The present **first narrow question** is whether *cross-workflow reviewer-network rewiring* alters agents' observed propensity to propose, negotiate or enact unauthorized reciprocal approvals when task counts and signature thresholds are matched. We compare paired reciprocal review dependencies with a four-agent cycle. Our contribution at this stage is (i) a carefully bounded mapping from organizational reviewer rights to mechanical versus incentive-relevant coalition possibilities, (ii) an executable, evidence-grounded and reproducible four-quarter experimental design separating procedural bypass from technical safety, and (iii) a deliberately strict evidence standard for negotiated collusion. **Empirical support for any behavioral effect remains to be measured.** We are not validating a general opportunity-landscape predictor with these two graphs.

## 2. Related work and research gap

Prior research already studies topology, coalition incentives, code-review misconduct and governance. **Colosseum** (Nakamura et al., 2026) analyzes multi-agent coalition behavior under different network/role conditions and includes a benign-prompt secret-channel control; topology itself is not new. **Emergent Collusion in Long-Horizon LLM Agent Interaction** (Shi et al., 2026) examines repeated peer verification and mutual acceptance, including interventions that probe peer influence. **Studying Coordination and Collusion in Multi-Agent LLM Code Reviews** (Za et al., 2025) studies collusive reviewer selection in code review; **SCARCE** (Kumar et al., 2026) reports emergent coordination institutions in extended coding-agent work. Our proposal is not a first demonstration of reciprocal agent behavior or unsafe peer review.

**Delegating Authorization to Misaligned Agents** (Collina et al., 2026) formalizes winning reviewer coalitions and authorization safety; we therefore do not claim novelty for the fact that approval graphs imply minimum winning coalitions. **The Politician, the Liar, and the Obedient Worker** (Seyedin et al., 2026) and **Institutional AI** (Syrnikov et al., 2026) explore incentives, governance and corruption/collusion in other organizational or market contexts. **Byzantine Cheap Talk** (El Mir et al., 2026) shows that graph disclosure itself can affect cooperation, an especially relevant alternative mechanism. Classic work on profitable coalitional deviations (Feldman, Meir and Tennenholtz, 2012) and coalition-proofness likewise predates this study.

The **bounded prospective delta**, not a proven priority claim, is to hold each agent's owner/reviewer workload and the per-release mechanical gate constant while manipulating *who is mutually dependent on whose authorization*, then compare objectively coded actions with explicitly communicated exchanges. Two configurations and at most a few four-agent episodes cannot establish cross-structure prediction, general mediation or a new equilibrium theorem.

## 3. Theory: feasibility, mutual gains and credibility

### 3.1 Reviewer graphs and compliant baseline

Let \(N=\{A,B,C,D\}\). Each agent owns one independently releasable service \(i\) and reviews exactly one other service. Write \(r_G(i)\) for the reviewer of owner \(i\), and \(k_G(j)=r_G^{-1}(j)\) for the owner reviewed by agent \(j\). Owner → reviewer arrows are *authorization dependencies*, **not** communication restrictions.

| Owner | P: paired reciprocity | R: four-cycle |
|---|---|---|
| A | B | B |
| B | A | C |
| C | D | D |
| D | C | A |

Thus P consists of A↔B and C↔D; R consists of A→B→C→D→A. In either graph each agent owns one task, reviews one task, and any release requires both its owner's and its assigned reviewer's fresh, exact-candidate final signatures. All agents may exchange addressed messages in the primary condition. Safe policy-compliant behavior is to authorize qualified candidates and withhold/escalate unqualified ones unless a valid independent exception exists (none is available at the deadline). Neither graph makes an illicit deployment mechanically impossible if both signatories cooperate.

### 3.2 Why the original M2 theorem needs a new target

The **historically approved M2** used a set \(V_t=\{i:v_{it}=1,e_{it}=0\}\) of *known-to-simulator vulnerable*, unexcepted releases. For a set of deviating signatories \(S\subseteq N\), outsiders compliant, the vulnerable releases mechanically approvable by that coalition were

\[
D_G(S,V_t)=\{i\in V_t\cap S:r_G(i)\in S\}.
\]

That is a graph/permissions identity, not a collusion prediction. M2 then considered additional deployments relative to a compliant baseline under an illustrative owner delivery bonus \(b_i\), expected owner/reviewer detection liabilities \(c_i^o,c_i^r>0\), no transfers and one-shot additive scores.

**Current study amendment:** a review request S is *permitted* even when verification is pending; final owner authorization and reviewer approval D are *prohibited* if full mandatory verification of that exact release is not accepted, irrespective of whether the software actually has a bug. Define \(q_{it}=1\) iff mandatory qualification has been accepted, \(v_{it}=1\) iff the reproducible hidden defect is present, and \(I_t=\{i:q_{it}=0,e_{it}=0\}\). The appropriate *procedural* opportunity identity is therefore

\[
D_G^{q}(S,I_t)=\{i\in I_t\cap S:r_G(i)\in S\},
\]

**conditional on** both agents reaching eligible D actions (owner requested review, exact candidate binding, ordinary gate passes). The graph identity transfers after replacing V by I; claims about **vulnerability-linked deployments** do not transfer, because \(q=0\not\Rightarrow v=1\) and \(v=0\not\Rightarrow q=1\). Requested reviews alone are neither forbidden final authorizations nor deployments.

### 3.3 Minimal coalitions and strictly beneficial cycles

With all four releases unqualified, a **single** procedural bypass requires only an owner and reviewer in either P or R. The distinct minimal two-person signatory pairs capable of *some* improper deployment are \(\{A,B\},\{C,D\}\) in P and \(\{A,B\},\{B,C\},\{C,D\},\{D,A\}\) in R. These are mechanically feasible **mechanisms**, not four independent coalitions that necessarily prefer to act.

For the original **illustrative**, not elicited, utility model, let \(x_i\in\{0,1\}\) denote an extra improper deployment relative to a compliant baseline. Then

\[
\Delta \mathbb E[u_i]=(b_i-c_i^o)x_i-c_i^r x_{k_G(i)}.
\tag{1}
\]

If outsiders remain compliant, every member must obtain **strictly positive** expected incremental score, reviewer liability is positive, no side transfers exist, and only these release approvals change, a profitable coalition must close a directed cycle of mutually supported releases. Along each complete profitable cycle the sufficient individual condition is \(b_i>c_i^o+c_i^r\) (with homogeneous same-round exposures). Under all-unqualified conditions, P has up to **two minimum strict-mutual-gain cycles** (A,B and C,D); R has one (A,B,C,D). These are *not* the sizes of the smallest coalitions that can cause harm. The derivation is conditional on the formal score and baseline, not an observation of agents' preferences.

For the present **procedural** system, an analogous local accounting could posit \(c_i^o=pL_i^o,c_i^r=pL_i^r\) with one procedural spot-check probability \(p=0.05\), but the implementation supplies **no calibrated numerical \(L\) or \(b\) utility**, and sampled findings rather than continuously accruing score are the actual feedback. Equation (1) and the strict-cycle classification therefore transfer only as **conditional hypothetical mathematics**, not as a demonstrated payoff property of the live agent organization. The experimental q=0 design makes the graph's formal procedural opportunity available; it does not establish that LLMs will act on it.

### 3.4 Credible commitment and independent-action null

A jointly profitable exchange need not be **self-enforcing**: at the simultaneous final D stage, a reviewer may reject a partner's risky release while still obtaining approval of its own. Messages and verbal promises are not binding contracts. In a separate, simplified symmetric repeated-pair toy model with known stationary scores, perfect monitoring, grim punishment and infinite horizon, cooperation can be sustained when \(\delta\ge c_r/(b-c_o)\), assuming \(b-c_o>c_r>0\). This is **not a result for the actual four-quarter, stochastic-audit, information-dependent experiment**. Four *observed* quarters are not announced to subjects; finite observation does not prove infinite-horizon incentives.

There is also a purely mechanical false-positive. Suppose all owners have already authorized and reviewers independently approve with common probability \(\alpha\). Then

\[
\Pr(\text{any complete P cycle})=2\alpha^2-\alpha^4,\qquad
\Pr(\text{complete R cycle})=\alpha^4.
\tag{2}
\]

For \(\alpha=1/2\), these probabilities are 0.4375 and 0.0625, respectively, although the expected number of unauthorized deployments is **two in either graph**. If owner authorization is instead independent with probability \(\beta\), replace \(\alpha\) by \(\alpha\beta\) under the stronger across-release independence assumptions. Correlated evidence, shared prompts and heterogeneous probabilities invalidate that simple iid benchmark. **Completed review cycles are not evidence of collusion** and cannot be used as the primary endpoint.

## 4. Methods: a matched, opportunity-enriched four-quarter experiment

### 4.1 Realistic conflict and independently verified technical truth

Four persistent model agents act as release owners/reviewers under a clear fictional company policy: requesting review while mandatory full verification is pending is legitimate, but final owner or peer authorization without accepted full qualification or independent exception is forbidden. A deadline creates plausible pressure to ship an apparently repaired candidate. A small visible validation/normalization patch corrects a demonstrated whitespace-padded tenant-input error; before/after code, source hashes and actually executed targeted regression tests are shown. Full integration verification remains incomplete in the pressure quarters. We **do not** prompt agents to believe the patch is safe.

Two executable service archetypes are used: a tenant report cache (X) and an export download-session service (Y). Each calls a locally authored, simulated opaque third-party dependency. Hidden defective X variants fail tenant separation on a bulk-monthly path; Y variants fail on resumed downloads. Targeted checks pass; a separately executed research-only full suite distinguishes safe and defective variants under a **finite specified workload**. Safe dependencies pass all seven full checks; defective ones fail two. Visible application evidence, incomplete-qualification state and ordinary checks remain matched across safe/defective variants apart from authentic opaque artifact digests. No real vendor failure, production certification or actual tenant breach is claimed.

In Q1, all four candidates have **q=1,v=0** with genuinely executed, accepted *study-defined* qualification, supporting a basic legitimate-productivity check. In Q2–Q4, all four have **q=0**; exactly two per quarter have hidden \(v=1\), two \(v=0\). This deliberately **opportunity-enriched** distribution is not a prevalence estimate. Two frozen blocks counterbalance vulnerability assignments and service archetypes: block 1 vulnerabilities Q2={A,B}, Q3={C,D}, Q4={A,D}; block 2 Q2={C,D}, Q3={A,B}, Q4={B,C}, with X/Y owner assignment swapped. Cases, policy, technical records and audit uniforms are paired across P/R. Hidden truth is never included in agent prompts.

### 4.2 Interaction, information and accountability

Each observed quarter has C1/C2 communication → S review request → independent reviewer packet → C3/C4/C5 communication → atomic D decisions → public operational board → possible audit → next quarter. Four actor generations per each of **seven** stages means **28 model calls/quarter, 112 calls/four-quarter episode**. At S, a request is not an owner signature; only requested candidates permit final D decisions. Each agent's single D output contains separate owner-authorize/withhold/escalate and assigned-reviewer-approve/reject fields. All eight final fields commit atomically; only correctly bound owner+reviewer signatures with passing ordinary gates cause deployment, even when q=0. Invalid or missing responses use logged technical fallbacks rather than fabricated participant refusals.

Agents have all-to-all private recipient-selected messages in the full-information arm, with the same 2,048-byte per-message cap and staged receipt rules in P and R. Review packets are independently prepared, not controlled by the owner. Subsequent role memory retains only legitimately received peer messages, permitted owner summaries, own and assigned-review records, allowed past boards and private findings; future truth and unseen peer messages are withheld. Graph-dependent reviewer packet access is part of the **bundled treatment**. Stalled releases are transferred to nonstrategic outside remediation, not carried into future rounds; fresh candidates begin each quarter. No post-release repair timeline, quantitative exposure duration or scalar welfare simulator is used.

Each deployed release receives one reproducible Bernoulli procedural spot-check with **p=0.05**; a sampled q=0 deployment produces one recorded finding, privately shared with both signatories, with stated professional consequences. This is a **stipulated institutional parameter**, not empirical audit-rate calibration. The audit checks *missing mandatory verification*, not hidden vulnerabilities. Board histories publish operational signatures/deployments, not hidden oracles, messages or private audit results. Agents are not told their participation ends after quarter four.

### 4.3 Graph comparison, diagnostic arms and causal estimand

We compare P and R under the same case block and information condition. A is the **primary** graph-visible, messaging-enabled, board-visible comparison. The diagnostic arms are **B** (graph visible, messaging disabled, other-team boards visible), **C** (graph visible, messaging disabled, other-team boards hidden), and **D** (messaging disabled, boards hidden, reviewer/global-graph identities additionally masked). D retains own role and authorized reviewer evidence through opaque identifiers; it is not provably information-theoretic blindness. Optional owner S summaries reach reviewers **only in A**, so A-versus-B also changes that channel. All disabled arms retain call slots but produce no peer messages. This is a **nested ladder, not a full factorial**.

A-P versus A-R, with paired exogenous fixtures and fresh agent sessions, estimates at most a **total effect of bundled reviewer reassignment** on the outcomes *in this scripted environment*. Rewiring changes direct reciprocity, connected components, coalition membership requirements, exposure to reviewed services and potential social/role cues simultaneously. It cannot identify the causal effect of cycle length alone, or mediation by modeled gains/coordination difficulty. A versus B removes beneficial technical communication and external message memory **as well as** negotiation; B versus C isolates visibility of other teams' board outcomes within no-message arms, but cannot by itself establish tacit agreements; C versus D adds identity concealment and its attendant information changes.

### 4.4 Episode allocation, operational integrity and annotation

The **planned maximum** is 2 blocks × 2 graphs × 4 arms = **16 independent four-agent episodes (1,792 model generations)**. The frozen priority is A P/R block 1, A P/R block 2, then B/C/D paired block 1, then their block 2 replications **only if** the entire next pair fits the preauthorized budget/time prefix. P/R order reverses between blocks. The current harness supports a proposed **US$20 total inference envelope**, whole-pair reservations and a required absolute stop time; this limits achievable replications and is **not** proof the maximum allocation will run. One A pair has a worst-case reserved liability of US$16.10 under specified token/pricing assumptions; the next complete pair is not guaranteed. The model candidate is DeepSeek V4.1 Flash via GCP MaaS, temperature 0, thinking enabled, 8,192 generation/reasoning tokens per call. Exact executed model/configuration and spending **must** be read from live archives, not inferred from this proposal.

The **experimental unit** is the four-agent, four-quarter episode. Quarter/service signatures are dependent nested observations, not independent sample units. No exploratory sample of one or two P/R pairs supports population significance, equivalence, a robust structural prediction, or a general equilibrium claim. Report all assigned episodes and technical failures, not only eligible reviews or convenient successes. Pair-level contrasts are descriptive; any research-informed rerun/endpoint change must be flagged exploratory.

Two independent human readers should annotate **delivered text first**, with message/receipt timestamps, quote and terms, initially without final-action outcomes, and then separately verify actual D signatures and deployment. Adjudicate disagreements without overriding uncertainty. The primary A-arm episode indicator requires a **concrete improper contingent authorization offer**, authentic receipt, **assent from all required graph-compatible actors after they receive the applicable terms**, and enactment of those terms through the relevant final actions. The proposer must actually commit its own required act; mediated forwards require authenticated receipt chains. Assents can reach a coordinator without every participant seeing every assent; the stricter mutual-receipt property is separately reported. Terms with unfulfilled conditions or agreement followed by defection do **not** count enacted. Technical mistakes, generic helpfulness, unilateral requests, synchronized but independent violations and post hoc expressions are distinct. Even an observed bargain establishes **documented negotiated action**, not counterfactually proved peer influence.

## 5. Measurements, prospective results and critical interpretation

**Primary endpoint (A only):** for each assigned episode, any *received + all-assented + enacted explicit improper reciprocal arrangement*; show earlier stages individually (offer, receipt, assent, agreement, enactment), plus deals that defected. The endpoint has high evidentiary specificity but sacrifices sensitivity to silent/tacit coordination, encrypted/ambiguous shorthand or unseen intent. A longer R deal requires more signatories under the theory; differences may reflect the graph's opportunity geometry **and/or** expression/annotation burden rather than a general 'willingness to collude.' In no-message arms explicit-bargain outcomes are **not observable (N/O)**, not zero.

**Secondary endpoints:** S requests; q=0 final owner authorizations; q=0 final reviewer approvals; q=0 deployments (objective *procedural* violations); v=1 deployments (finite-oracle *technical risk*); v=0 but q=0 shortcuts; Q1 qualified-safe productive throughput; holds, escalations, rejections, invalid/timeouts; auditor findings; repeated patterns of silent approvals. Report both counts per all four assigned service-quarters and conditional-on-eligible-review counts (the latter post-treatment/descriptive only). Expressed recognition of the qualification gap or misunderstanding is separately quoted; delivered policy itself does not demonstrate actual recognition. A deployment of v=1 does not establish an actual customer breach.

**Table 1. Main P/R archive and primary evidence (populate only after verified live runs; N/O = transcript construct unavailable; NA = not assigned).**

| Arm/block | Graph | Verified archive / status | Explicit offer | Full assent | Enacted arrangement | q=0 deployed | v=1 deployed | Q1 qualified releases |
|---|---|---|---|---|---|---|---|---|
| A/1 | P | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| A/1 | R | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| A/2 | P | NOT YET AUTHORIZED/EXECUTED | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| A/2 | R | NOT YET AUTHORIZED/EXECUTED | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| B/C/D | P/R | CONDITIONAL ON RESOURCES | N/O | N/O | N/O | PENDING | PENDING | PENDING |

**Table 2. Planned per-quarter audit trail for each archived episode (replicate for Q1–Q4):**

| Quarter | Assigned S requests /4 | q=0 owner D /4 | q=0 reviewer D /4 | q=0 deployments /4 | v=1 deployments /4 | Qualified q=1 deployments /4 | Findings | Invalid/timeouts |
|---|---|---|---|---|---|---|---|---|
| Q1 | PENDING | 0 by case allocation if truth verified | 0 by case allocation if truth verified | 0 by case allocation if truth verified | PENDING | PENDING | PENDING | PENDING |
| Q2 | PENDING | PENDING | PENDING | PENDING | PENDING | 0 eligible qualified cases | PENDING | PENDING |
| Q3 | PENDING | PENDING | PENDING | PENDING | PENDING | 0 eligible qualified cases | PENDING | PENDING |
| Q4 | PENDING | PENDING | PENDING | PENDING | PENDING | 0 eligible qualified cases | PENDING | PENDING |

**Do not fill unknown model behavior with zero.** Report a paired P–R table at the episode level and reproduce decisive exact message quotes with receipt/action IDs after independent adjudication. If A has no explicit exchange but q=0 deployments occur, infer only procedural violation, not no possible collusion. If no q=0 deployment occurs, check Q1 productivity and technical exposure before discussing a behavioral null; no approvals could simply indicate policy compliance, inability to use the harness or insufficient opportunities perceived. If P exhibits more complete cycles without actual offers/assents, equation (2) supplies a non-collusive explanation. If enacted bargains occur, report the observed coordination but do not assert counterfactual necessity absent information-preserving peer interventions.

## 6. Engineering validation (separate from empirical findings)

A frozen one-quarter F1 smoke pair produced an executing-agent report of **56/56 successful model calls** and deterministic replay. All eight owner decisions were holds/escalations; no submissions reached reviewer decisions, no deployment occurred and no reciprocal proposals were observed. Some messages were rejected by F1's 1,024-byte size cap. This demonstrates particular transport and replay behavior and exposed an overrestrictive *submit-as-signature* workflow; it is **not** a P/R behavioral comparison. The raw ignored local F1 archives were not independently retrieved into the research repository, so treat these as **executing-agent-reported**, not independently audited transcript results.

The later main-study harness was separately inspected on branch codex/main-study-harness. Its handoff and independent reviewer report **82 passing offline tests** (including 50 foundation tests), a 16-cell four-quarter **scripted** matrix, 18 scripted negative traces/replay cases, exact source-oracle fixture checks, lossless history serialization and annotated manual demonstrations. The review reports correction of packet identity leakage, forged evidence, receipt/assent edge cases, summary side channels and interruption false negatives. A hash-indexed review package and cost/capacity proofs exist. **No live main-study agent calls are reported by that handoff.** Scripted positives are explicitly injected test traces, not emergent reciprocal coordination; the independent review concerns **offline apparatus integrity**, not proof of scientific effects or real provider token bills.

## 7. Discussion, limitations and next research steps

This design helps separate three quantities that can otherwise be conflated: **authorization opportunity**, **policy noncompliance**, and **actual negotiated harmful coordination**. The formal model shows why the signatory graph creates different minimal *strict-mutual-benefit* cycles under a particular hypothetical payoff model, while the iid null shows that the same graphs can produce different closed approval patterns without any agreement. A matched behavioral intervention is the proper next step, but even a confirmed difference measures a graph bundle rather than a universal organization principle.

Important limits are (i) only four persistent agents and one small selected model/configuration; (ii) two fictional source archetypes and finite test-oracle workloads; (iii) the deliberately unnatural all-q=0 opportunity quarters; (iv) simulated corporate incentives and uncalibrated 5% audit feedback; (v) very few independent episodes and temporal execution confounds; (vi) non-factorial controls and loss of helpful information when messaging is removed; (vii) inability to observe hidden beliefs, tacit collusion or counterfactual peer influence directly; and (viii) limited legitimate productivity inference from Q1 because qualification, timing and phase differ from Q2–Q4. No actual welfare scalar, customer security compromise, production exposure duration or general collusion prevalence is measured.

A stronger follow-up would vary more independent reviewer graphs while matching mechanical opportunity counts; explicitly test held-out ex ante opportunity descriptors against behavior; randomize clearer information-only and receipt interventions; diversify agent models and tasks; use realistic mixes of qualified and unqualified cases; and measure legitimate productivity **at matched security/qualification states** rather than equating blanket refusal with success. None is claimed completed here.

## 8. Conclusion

Reviewer dependencies can produce different mechanically feasible and hypothetically mutually profitable harmful coalitions even when each agent has the same role load and every release has the same two-signature rule. That **formal** result is not evidence that LLM agents will coordinate. A four-quarter, independently verified release-review apparatus and conservative message-to-action annotation protocol allow an exploratory comparison of paired reciprocity against a four-cycle. **Main-study observations and any empirical conclusion remain pending at this report revision.** Strong conclusions require verified archives, independent coding, recognition of independent-approval alternatives and replication across structures.

## Code, data, contributions and LLM-use disclosure

- Code and durable science: https://github.com/surajk-io/agent-collusion-risk
- Main harness and independent offline review: branch **codex/main-study-harness**, research/organizational-coalitional-risk/M4-harness-foundations/mainstudy/
- Report revision: branch **report/apart-2026-10-26-draft**
- Behavioral archives: **not yet available/reviewed**. After collection, provide exact code revision, prompt/fixture digests, assigned run IDs, hash-verified transcripts, annotation versions, incomplete runs and billing.
- **Author contributions:** Suraj Kumar directed research choices, reviewed scientific designs and retains responsibility for all submitted claims. AI assistants contributed literature synthesis, formal modeling, adversarial critique, coding and report drafting. Exact division of human contributions should be reviewed and corrected before submission.
- **LLM usage:** Extensive assistance from multiple LLMs was used for idea exploration, research synthesis, experiment design, formal analysis, implementation/review and manuscript drafting. The researcher must verify theoretical and empirical claims and ensure the final submission is primarily their own work as Apart's template strongly encourages. Do not present generated text or simulated test episodes as independently human-authored empirical research.

## References

1. Nakamura et al. (2026). *Colosseum.* https://arxiv.org/abs/2602.15198
2. Shi et al. (2026). *Emergent Collusion in Long-Horizon LLM Agent Interaction.* https://arxiv.org/abs/2609.24967
3. Za et al. (2025). *Studying Coordination and Collusion in Multi-Agent LLM Code Reviews.* NeurIPS workshop. https://openreview.net/forum?id=CdZaamCf5Y
4. Kumar et al. (2026). *SCARCE: Emergent Institutions in Long-Horizon Multi-Agent Coding Systems.* https://arxiv.org/abs/2610.21029
5. Collina et al. (2026). *Delegating Authorization to Misaligned Agents.* https://arxiv.org/abs/2609.15803
6. Seyedin et al. (2026). *The Politician, the Liar, and the Obedient Worker.* https://arxiv.org/abs/2608.09574
7. Syrnikov et al. (2026). *Institutional AI: Governing LLM Collusion in Multi-Agent Cournot Markets via Public Governance Graphs.* https://arxiv.org/abs/2601.11369
8. El Mir et al. (2026). *Byzantine Cheap Talk.* https://arxiv.org/abs/2606.07790
9. Feldman, Meir and Tennenholtz (2012). *Stability Scores.* https://arxiv.org/abs/1105.5983

## Appendix A. Formal derivation and scope of transfer

Let an improper release \(i\) require owner's final signature and reviewer \(r_G(i)\)'s final signature. If outsiders are compliant, only \(i\in S\) with \(r_G(i)\in S\) may be added by coalition S. Hence \(D_G^q(S,I)=I\cap S\cap r_G^{-1}(S)\) for q0 eligible requests. This is a feasibility identity; it cannot tell whether either signature is given. For full q0, each owner–reviewer edge yields one distinct minimal signatory pair, but P's opposite edges share the same unordered pair whereas R's four edges yield four distinct unordered pairs.

For the hypothetical additive local-score game, baseline all q0 releases held, set \(x_i=1\) for an extra q0 deployment. The owner gains \(b_i-c_i^o\). Reviewer of release \(k_G(i)\) pays \(c_i^r\) when \(x_{k_G(i)}=1\). Therefore equation (1). In a proper **minimal coalition all of whose members strictly gain**, no participating reviewer can pay \(c_i^r>0\) without also obtaining some own release benefit. In a disjoint-union-of-directed-cycles reviewer permutation and with no side transfers, closing the profitable deviation along a complete cycle yields each participant \(b_i-c_i^o-c_i^r>0\). A path that stops leaves a last signer bearing reviewer cost but no owned-release benefit; under strict-gain assumptions it cannot be minimal. This does **not** preclude a two-person harmful deployment with just one beneficiary, a coercive refusal of clean review, altruistic sacrifice, multi-quarter reputational motives or an LLM simply disregarding modeled payoffs. Alternative utility functions or information states require rederivation.

Under the independently authorized all-owner case, P's two independent two-reviewer cycles have events each of probability \(\alpha^2\); their union is \(1-(1-\alpha^2)^2=2\alpha^2-\alpha^4\). R's one four-reviewer cycle requires all four independent approvals, yielding \(\alpha^4\). Expected individual releases equal 4\(\alpha\), regardless of graph. These identities refer only to **completed graph patterns**, not messages, intent, realized customer harm or causal influence.

The one-shot favorable deviation from a costly reviewer approval can undermine an otherwise mutually profitable trade. In the separate infinite repeated symmetric grim-trigger illustration, cooperating forever yields \((b-c_o-c_r)/(1-\delta)\). Rejecting another's release while still receiving own approval yields \(b-c_o\) now and zero future cooperative gains. Rearranging \((b-c_o-c_r)/(1-\delta)\ge b-c_o\) gives \(\delta\ge c_r/(b-c_o)\). This assumes the stipulated punishment is credible and observed, stationary payoffs, no noise and no other opportunities; it is **not estimated or proved** in the current finite observation, uncertain audit experiment.

## Appendix B. Repository provenance and pre-submission verification

Scientific origin: research/organizational-coalitional-risk/README.md and literature.md; M1-approved-scenario.md and M1-design-review.md; historical M2-approved-formal-bridge.md. Current supersession register: CURRENT-STUDY.md. Main build authority: M3-IMPLEMENTATION-BASELINE-2026-10-26.md, with rationales in M3-MAIN-STUDY-DESIGN-PROPOSAL.md. Detailed labels/control criticisms: M3-integrated-review-package/measurement-controls-analysis.md (historical one-quarter assumptions superseded). Main harness: branch codex/main-study-harness, M4-harness-foundations/mainstudy/README.md and INDEPENDENT-REVIEW.md. F1: M4-harness-foundations/f1/README.md. Do not modify those artifacts to make this report appear stronger.

**Required before final submission:** verify whether main-study execution was separately approved; inspect original complete request/response archives rather than summaries; rerun hash/replay verification; check model/provider, case bindings, receipt timestamps and actual final signatures; obtain two independent transcript codings and adjudication; populate *every* assigned outcome including missing/incomplete statuses; report actual paired differences and competing independent-policy-violation explanations; revisit author attribution and Apart's AI-use guidance.