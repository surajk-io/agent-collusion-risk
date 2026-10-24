# Research roadmap

**Status date:** 2026-10-24. **Current milestone for both tracks: M1 — credible organizational scenario.** This is a plan, not evidence that the theories are true. No new experimental design has been approved.

## Two parallel research tracks

| Track | Core question | Current status |
|---|---|---|
| **A. Coalitional vulnerability** | Can the number, magnitude, distribution or credibility of profitable harmful coalition opportunities predict realized, causally supported LLM-agent collusion? | **M0 complete:** question and relevant prior art provisionally mapped. **M1 next:** select a believable workflow in which individual and organizational objectives can differ; do not choose the payoff table first. |
| **B. Power dynamics** | How do authority, permission, information and influence structures affect coalition formation, harmful capabilities and successful collusion? | **M0 complete:** question and candidate organizational dimensions recorded. **M1 next:** choose a workflow with meaningful approval, veto, audit, allocation or other enforceable powers; consider a directed graph of role dependencies. |

**Explore in separate chats.** Preserve each track independently. Whether they should ultimately be combined is an open research decision.

## Milestones and exit criteria

| Milestone | What must be established to exit it | A: coalitional vulnerability | B: power dynamics |
|---|---|---|---|
| **M0 — Frame question** | Scientific question, plausible gap, key objections and definitions documented, without claiming novelty | Done provisionally | Done provisionally |
| **M1 — Credible workflow** | Small, understandable, executable organizational scenario; roles, legitimate tasks, permissions, information, action consequences, incentives, organizational objective, and credible source of conflicting interests. Identify alternative non-collusive explanations. | **Current target**: derive candidate harmful coalition opportunities from workflow, not synthetic payoff tuning | **Current target**: define actual authority/information dependencies and situations in which pooling permissions matters |
| **M2 — Formal model** | Precise actions, state transitions, individual utilities, welfare, baseline and possible deviations, with arithmetic/invariants checked. Explicitly state which agent preferences are assumptions, not facts. | Define coalition metrics and compare to simpler baselines; assess credibility and double-counting | Operationalize measurable power (permissions, vetoes, control of information, graph properties); check graph-to-action mapping |
| **M3 — Falsifiable experiment design** | One primary prediction and meaningful counterprediction; controlled contrast, outcomes, causal identification, positive/negative controls, evaluation-awareness treatment, sampling and analysis plan **approved by human before implementation** | E.g. match max coalition gain while varying number/structure of opportunities, if a clean contrast is feasible | E.g. vary enforceable permission distribution while limiting changes to incentives/information, if feasible |
| **M4 — Implement and validate** | Tools enforce rules; unit/edge tests cover permissions, payoffs, baselines and interventions; independent adversarial review; pilot positive control confirms relevant ability without prelabeling spontaneous collusion | Confirm opportunities are executable and metric computed before LLM outcomes | Confirm intended power differences actually affect executable capabilities |
| **M5 — Empirical study** | Pre-specified multi-run comparisons, full prompt/model/provider/data provenance, annotation and communication interventions, uncertainty and alternative explanations reported | Determine whether structural metrics add predictive value on held-out variants | Determine whether authority/intervention changes causally affect behavior |
| **M6 — Synthesis** | Report supported, unsupported and inconclusive results; limitations, artifacts, and implications, without conflating opportunity, harm and collusion | Evaluate predictive usefulness and failure conditions | Evaluate mechanistic role of power and detectability |

Milestone numbers describe **work stages**, not guaranteed scientific progress. Stop or pivot if realism, formal coherence, measurement validity, a proper comparison, or adequate controls cannot be obtained. M4 is not permission to run a consequential experiment: the **human approves the design at M3 and any substantive changes thereafter**.

## Shared validity rules

- **Separate individual payoffs from organizational welfare.** Actual output value should not automatically double when work is duplicated.
- **Do not assume LLMs optimize written rewards.** Derive mathematical opportunities conditional on explicit assumptions and test whether those assumptions describe behavior.
- **Do not treat harmful joint action as collusion.** Compare no-communication and communication conditions; use interpretable positive controls and interventions where appropriate.
- **Audit evaluation cues.** Prompt language, "synthetic experiment" disclosures, point tables, artificial names, and visible research framing may alter behavior. Do not secretly tell agents they're in a live company; accurate neutral framing or explicitly varied awareness is preferable.
- **Separate mathematical predictions from empirical hypotheses.** A game can establish that a deviation is feasible/profitable under its rules; it cannot alone establish the probability LLMs will take it.
- **Record what would disconfirm a claim**, not just what might produce a positive result.

## Human decisions and durable handoff

Before passing an approval gate, the researcher must see: the proposed **load-bearing decisions**, credible alternatives, why each matters, unresolved assumptions, controls, and the result of an independent critical review. The researcher, not an agent, chooses whether to proceed.

**Approvals recorded so far:** Both tracks are to be explored in parallel; historic Jira pilot is archived. **No workflow, mathematical predictor, new agent prompt, or experiment is approved.**

Only update this file or the research-question document when goals, milestones, critical assumptions, approvals, or consequential findings materially change. Keep routine brainstorms out of Git.
