# Main study implementation status

Engineering authorized 2026-10-26; live inference NOT authorized.
Branch: `codex/main-study-harness`; starting commit: `39e979c`.

Authority: `research/organizational-coalitional-risk/M3-IMPLEMENTATION-BASELINE-2026-10-26.md` (complete build contract), CURRENT-STUDY.md; earlier M3/M1/M2 are provenance where superseded.

## Milestones

| Phase | Modules | Required evidence | Status |
|---|---|---|---|
| E1 core | mainstudy/contracts, runner, materials, F1 archive/transport reuse | S != signature; dual atomic D; q0 allowed | Core implemented; replay pending E4 |
| E2 evidence | mainstudy/fixtures | two actual dependency implementations per archetype; executed limited/full oracle; exact hashes | Implemented; executed assertions passing |
| E3 controls | materials projection, runner memory/audit | all serialized arms, role privacy, blind counterparty masking | Implemented; full regression in progress |
| E4 dry runs | scripts/tests | four quarters × P/R × A/B/C/D × two blocks, no model calls | Pending |
| E5 review | annotation/preflight/package | adversarial traces; worst-case context bound; independent critique; launch gate | Pending |

Scientific semantics: preserve locked overarching/narrow questions verbatim in the baseline. No new scientific decisions adopted. No backlog, maintenance, scalar welfare or oracle veto. F1 remains unchanged.

First executed core suite: 4/5 passed; privacy assertion failed because it interpreted phase D as agent D. Corrected to inspect identity leaves excluding stage/phase. Independent read-only review demonstrated repeated safe dependency hash leakage and forged evidence accepted by verify. Fixed through authentic per-release dependency source comments and recomputation of limited/full evidence, qualification and gate. Added regression counterexamples. Full foundations/F1/mainstudy suite in progress.

Baseline review E1–E3: no F1 submit-signature or quarter-one Binding reused; only raw transport/archive reused. S produces no signature; q0 dual signatures can deploy. Full Q1 oracle detail stays researcher-only; visible accepted record has real check count, pass status and execution-record digest. Blind arm omits optional owner-authored reviewer summary to avoid self-identification; own accepted outputs remain private memory. Each archetype's narrow/full checks execute actual source. Safe means passes frozen finite workload, not universal security.

Strongest remaining scientific failure mode: independent signatures or same-round pseudo-assent producing a primary label. Next phase must add manually coded semantic evidence plus authenticated receipt/action checks; never classify arbitrary text lexically.

Next action: finish regression, checkpoint E1–E3, then E4 replay, complete matrix dry runs, E5 annotation and maximal legal context/budget gates. Final provider capacity/pricing/configuration, budget, stopping time, prompt and fixture signoff remain live-launch gates.
