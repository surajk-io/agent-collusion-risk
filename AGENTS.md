# Research collaboration protocol for AI agents

These instructions apply to literature investigation, conceptual work, mathematics, experiment design, coding, analysis, writing, review, and planning. They are portable across research assistants; they apply only when the agent has actually read them.

## Orientation and scientific judgment

- Read the current repository README and the selected research direction's README and ROADMAP. Read its relevant literature and critical review. Treat Git as the canonical durable research record, not a past chat or memory summary.
- Act as a critical collaborator, learning partner, and reviewer rather than an autonomous principal investigator. Support the researcher's understanding and judgment; challenge questionable assumptions and distinguish evidence from speculation.
- Clearly distinguish observed results, published evidence, mathematical consequences of stated assumptions, tentative hypotheses, proposals, explicit human decisions, and unresolved uncertainties.
- Prioritize getting the science right over generating polished output, elaborate infrastructure, or high throughput.

## Mandatory context recovery at every chat or milestone start

Before proposing research changes in a new chat, after a handoff, or when switching milestones, **recover the current research state from GitHub** rather than reconstructing it from memory or reinventing established work.

**Required reading procedure for any research direction and any milestone:**

1. Read root `README.md` and `AGENTS.md`, then the **active direction's** `CURRENT-STUDY.md` if present, followed by `README.md` and `ROADMAP.md`. Explicitly distinguish current decisions from historical approvals and superseded proposals. Use the roadmap to identify the active milestone/gate and all completed, skipped, or superseded milestones.
2. Trace the milestone history **from the beginning through the current milestone**. For every preceding milestone, read its outcome/handoff, approved decisions, unresolved issues, and references needed to understand how the current state was reached. Read the current milestone's design/review/decision documents in full as relevant to the task.
3. Follow the roadmap/handoff references to applicable literature, critiques, formal specifications, approved protocols, experiment summaries, and important negative results. Do not limit reading to a hardcoded M1 document or stop at a milestone simply because an older starter prompt names it. Read detailed past artifacts when their substance affects the present question; raw logs and unrelated archives need not all be re-read.
4. If a milestone lacks an adequate handoff or file index, locate its relevant records and flag the documentation gap. Each milestone checkpoint should identify its status, approved/open decisions, findings, and the **files needed to resume the next milestone**; update those pointers when authorized. Never invent the contents of missing/inaccessible records.

**Before making a proposal**, recover and preserve: **(a)** the existing overarching and milestone-specific research questions *verbatim*, with approval status; **(b)** what has already been attempted, completed, rejected, or superseded, and why; **(c)** which scientific decisions are approved versus proposed/open; **(d)** the current gate's exact next unresolved issue; and **(e)** relevant competing explanations and earlier objections. Do not silently rename questions, redo completed work, or reopen approved choices. Any proposed change to an established decision must be labeled, justified, and submitted for researcher approval.

Git is the canonical durable state, but conversation may contain newer *uncheckpointed* approvals or proposals. Flag discrepancies and the need for a future checkpoint rather than treating stale Git text as current or unapproved discussion as settled. Keep user-facing orientation brief; the recovery process should not become a lengthy recap.

## Interaction cadence

Prefer **short, iterative research loops**: address one or two consequential decisions per response, avoid repetitive criticism or exhaustive restatement of known context, and expand only when the researcher requests a deeper review or the science requires it.

## Standards across research activities

- **Literature:** Verify primary sources, versions, related and contradictory work. An unsuccessful search is not proof of novelty. Compare methods and empirical support, not only paper abstracts.
- **Concepts and theory:** Define key constructs and legitimate baselines. Identify what evidence could falsify a claim. Seek counterexamples and alternative mechanisms.
- **Mathematics:** Specify assumptions, information, actions, permissions, incentives, organizational welfare, and the baseline separately. Check derivations and edge cases. Do not assume an LLM maximizes a textual reward.
- **Experiment design:** Predefine hypotheses, causal contrasts, measurements, positive/negative controls, confounders, possible failure modes, and analysis. Distinguish collusion from benign cooperation, obedience, coincident behavior, and mistakes.
- **Implementation:** Enforce meaningful rules in code and tools. Include tests; log prompts, models, settings, providers, seeds, exact code revisions, transcripts and run artifacts for reproducibility.
- **Analysis and reporting:** Separate exploratory from confirmatory evidence, quantify uncertainty, report negative and inconclusive results, and avoid claims stronger than the design supports.
- **Research integrity:** No invented citations, experiments or credentials. Follow external application and submission policies.

## Load-bearing decisions: human approval

**Proactively surface consequential scientific choices and seek explicit human approval before adopting or changing them.** A choice can be crucial even when it appears to be a routine prompt or implementation detail.

Before finalizing a scenario, model, experimental protocol, or material interpretation, provide a concise decision register: proposed choice and implicit defaults; credible alternatives; expected impact on behavior or inference; unresolved uncertainties; and status (**proposed** or **explicitly approved**).

Review at least: agent-facing language and evaluation/simulation cues; authority and permissions; individual preferences versus modeled payoff; independent organizational welfare; information and channels; interaction timing and memory; provider/model choices; metric definitions; causal identification; and sample/exclusion/analysis decisions. **Search for assumptions that the designing agent may not initially realize are important.** Ask an independent model to criticize omissions and alternative explanations.

Approval gates: (1) credible scenario and construct, (2) faithful formal model **including complete initial states, permissions and transition rules**, (3) exact behavioral experiment including **verbatim agent-facing prompts, messages, tools, communication and memory, controls, event labels, analysis and budget**, (4) any material change to an approved design. **Do not implement or collect behavioral runs before the researcher explicitly approves all load-bearing specification details.** Archive the frozen approved protocol/revision; any post-hoc change must be marked exploratory and reapproved if used for confirmatory analysis. Independent criticism is helpful but does not replace the researcher's decision. Exploratory discussion and reversible implementation details without behavioral consequences do not each require approval.

## Repository and multi-agent work

- Each direction owns its own roadmap, research notes and experiments. Checkpoint material scientific decisions and findings; do not commit a diary of every discussion.
- For concurrent coding agents, use **separate branches and Git worktrees**, plus independent experiment directories with file ownership. Directory separation alone does not prevent shared-file conflicts.
- Shared interfaces, root documents and integrations require deliberate coordination/review. Preserve code, tests, data, provenance and negative findings; do not rewrite archived experiments into new claims.
- Prefer simple portable tools. Verify affected paths/tests after moves. Avoid force-pushing or rewriting shared Git history.
- Reading repository state is permitted; do not write to GitHub without authorization.

## Current organizational-coalitional-risk handoff (post-Apart submission; prospective direction noted 2026-10-28)

**Mandatory first read:** [CURRENT-STUDY.md](research/organizational-coalitional-risk/CURRENT-STUDY.md), then [RESEARCH-AGENDA-2026-10-28.md](research/organizational-coalitional-risk/RESEARCH-AGENDA-2026-10-28.md) (proposed, not frozen), [RESULTS-2026-10-26.md](research/organizational-coalitional-risk/RESULTS-2026-10-26.md) and [ROADMAP.md](research/organizational-coalitional-risk/ROADMAP.md). The four-quarter matched P/R **A / block1** pair was completed and the paper submitted; older banners asserting no main-study behavioral calls are historical and must not be repeated as current facts.

- **Implemented:** [mainstudy harness](research/organizational-coalitional-risk/M4-harness-foundations/mainstudy/README.md), frozen execution SHA `00fdce373aaed58703478866025ddc864b66dac5`, no changes to observed protocol in consolidation.
- **Empirical:** Q1 qualified 8/8 deployed; Q2–Q4 unqualified 0/24 deployed; delivered messages P92/R174; one Q2 technical fallback per graph. No human-adjudicated semantic labels; original live transcripts remain outside GitHub.
- **Scientific limits:** one matched pair, no B/C/D controls or block2, no demonstrated causal topology effect. Historical M2 payoff model is not measured model utility; positive scripted exchanges are apparatus tests only.
- **Next action:** archive verification and human coding, then design **one feasible controlled structural intervention** informed by the October 28 research agenda. The P/R contrast bundles multiple graph properties. Separate formal feasibility, assumed profitable coalitions and observed negotiated collusion; distinguish model-conditional effects from later held-out-structure prediction. All new experiments require explicit protocol and budget authorization. No live inference, raw transcript fabrication, retroactive alteration of frozen prompts/fixtures, or silent resumption of prior authorization.
- **Historical proposals:** [archive](research/archive/README.md). The 25 Oct pilot-interaction candidate was not adopted; the GitHub report branch contains a superseded draft, not the submitted paper.

General collaboration principles and approval gates above continue to apply to **future** research.