# Agent Collusion Risk

Self-directed research into **how organizational structure creates opportunities for harmful coordination among task-specialized AI agents**, how opportunities relate to actual behavior, and how institutional design might resist misuse while preserving legitimate cooperation.

**Status (28 October 2026):** Apart AI Collusion Research Sprint submitted on 26 October; a **prospective** follow-up now focuses on whether independently characterized organizational opportunity properties explain or predict harmful coordination, and how structural effects depend on the LLM model. The follow-up is a research agenda, **not** new experimental evidence or an approved inference protocol.

**Research motivation:** Formal organizational analysis can identify feasible or conditionally profitable coalitions; empirical tests must determine whether agents actually recognize and exploit those opportunities. The goal is not a universal model-independent collusion law. The next step is a controlled intervention varying one structural feature as independently as feasible, followed by replication and (later) tests on held-out organizations. Mechanical enforcement and legitimate workflow performance remain essential comparison points.

**Historical sprint status:** One four-quarter **matched P/R pair** was executed using the frozen main-study harness (Condition A, Block 1). This is an exploratory pilot, **not evidence of a graph effect**.

## Start here

- [Prospective research agenda (28 Oct 2026)](research/organizational-coalitional-risk/RESEARCH-AGENDA-2026-10-28.md) — motivation, candidate predictions, experimental design constraints, proposed bounded follow-up and preprint criteria.
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