# Agent Collusion Risk

Self-directed research into **how organizational structure and task dependencies shape opportunities for collusion among task-specialized AI agents**, how agent incentives and repeated interactions affect the realization of those opportunities, and how organizations can preserve legitimate cooperation.

**Status (29 October 2026):** Apart AI Collusion Research Sprint submitted on 26 October. The researcher has approved a refined **working question**: how ex ante organizational structure interacts with incentives and repeated interactions to shape the emergence, stability and dynamics of **collusion** (not harmful coordination broadly). A controlled structure-by-incentive experiment is the next design milestone; **no** new protocol, inference runs or spend have been approved.

**Research motivation:** Formal organizational analysis can identify feasible or conditionally profitable coalitions; empirical tests must determine whether agents recognize, negotiate and sustain collusive arrangements. The central empirical target is **how structure modifies agents' responses to incentive and history changes**, not an absolute model-independent collusion rate. A structure-by-incentive contrast must distinguish collusion from harmful assistance or coincident violations and retain legitimate workflow and mechanical-enforcement baselines. Later tests may examine held-out organizations.

**Historical sprint status:** One four-quarter **matched P/R pair** was executed using the frozen main-study harness (Condition A, Block 1). This is an exploratory pilot, **not evidence of a graph effect**.

## Start here

- [Research agenda (28 Oct; refined 29 Oct 2026)](research/organizational-coalitional-risk/RESEARCH-AGENDA-2026-10-28.md) — motivation, candidate predictions, experimental design constraints, proposed bounded follow-up and preprint criteria.
- [Current scientific state and next steps](research/organizational-coalitional-risk/CURRENT-STUDY.md) — authoritative; distinguishes completed work, limitations, outstanding checks, and future plans.
- [Sprint empirical results](research/organizational-coalitional-risk/RESULTS-2026-10-26.md) — what was observed, what is preliminary, and what is missing.
- [Research overview](research/organizational-coalitional-risk/README.md) — broader motivation and hypotheses.
- [Roadmap](research/organizational-coalitional-risk/ROADMAP.md) — status of M0–M6 and reasonable next experiments.
- [Submitted-paper record](research/organizational-coalitional-risk/SUBMISSION-2026-10-26.md) — submission snapshot, external PDF/Google Doc pointer, and distinction from the historical Markdown draft.
- [Formal bridge](research/organizational-coalitional-risk/M2-approved-formal-bridge.md) — the original conditional mathematics; read the present-study qualification correction in CURRENT-STUDY before transferring its propositions.
- [Main-study code, offline tests and reproducibility guide](research/organizational-coalitional-risk/M4-harness-foundations/mainstudy/README.md) — the exact implemented apparatus, not newly authorized inference.
- [Project-wide agent protocol](AGENTS.md) — portable research collaboration practices.

## What happened in the first live matched pair

| | Paired P | Four-cycle R |
|---|---:|---:|
| Qualified releases deployed, Q1 | 4/4 | 4/4 |
| Unqualified releases deployed, Q2–Q4 | 0/12 | 0/12 |
| Unqualified owner authorizations | 0/12 | 0/12 |
| Delivered peer messages | 92 | 174 |
| Model call slots / accepted outputs | 112 / 111 | 112 / 111 |

The executing operator's handoff reports **224 call slots**, two Q2 technical fallbacks and no unauthorized final signatures. A preliminary **AI-assisted** scan found no explicit reciprocal offers; this message-level classification has **not** been independently human-adjudicated. Raw run archives were collected locally, **not committed to GitHub**. The reproducible code and fixed fixtures are in this repository, but public readers must not be told that the live transcripts are downloadable here.

## Repository map

- `research/organizational-coalitional-risk/`: active question, formal work, dated design decisions, finalized experiment code, pilot results and submission pointers.
- `research/archive/`: earlier framing, Jira pilot, design candidates that did not become the executed experiment, and the superseded GitHub Markdown report draft.
- `research/organizational-coalitional-risk/M4-harness-foundations/`: frozen F1 smoke materials plus the executable four-quarter main-study harness.
- `IMPLEMENTATION-STATUS.md`: **historical engineering log**, retained for reproducibility; start with CURRENT-STUDY for current status instead.

The original F1 smoke and scripted positive tests are engineering checks, **not behavioral collusion results**. Do not treat older M3 approval/proposal or execution-template files as permission to initiate inference. Do not run any live model calls without new explicit authorization.

## Provenance

Canonical repository: https://github.com/surajk-io/agent-collusion-risk . Historical branch tips are kept intact; the executed harness came from `codex/main-study-harness`, and the older report draft from `report/apart-2026-10-26-draft`. [Archive index](research/archive/README.md) explains what is superseded.