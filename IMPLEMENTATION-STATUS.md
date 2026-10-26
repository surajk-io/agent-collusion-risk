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
| E4 dry runs | scripts, replay, CLI | four quarters × P/R × A/B/C/D × two blocks, no model calls | Complete matrix + 18 negative traces and exact replay executed |
| E5 review | annotation/preflight/live/package | adversarial traces; worst-case context bound; independent critique; launch gate | In progress; maximal context launch blocker established |

Scientific semantics: preserve locked overarching/narrow questions verbatim in the baseline. No new scientific decisions adopted. No backlog, maintenance, scalar welfare or oracle veto. F1 remains unchanged.

First executed core suite: 4/5 passed; privacy assertion failed because it interpreted phase D as agent D. Corrected to inspect identity leaves excluding stage/phase. Independent read-only review demonstrated repeated safe dependency hash leakage and forged evidence accepted by verify. Fixed through authentic per-release dependency source comments and recomputation of limited/full evidence, qualification and gate. Added regression counterexamples. Full foundations/F1/mainstudy suite in progress.

Baseline review E1–E3: no F1 submit-signature or quarter-one Binding reused; only raw transport/archive reused. S produces no signature; q0 dual signatures can deploy. Full Q1 oracle detail stays researcher-only; visible accepted record has real check count, pass status and execution-record digest. Blind arm omits optional owner-authored reviewer summary to avoid self-identification; own accepted outputs remain private memory. Each archetype's narrow/full checks execute actual source. Safe means passes frozen finite workload, not universal security.

Strongest remaining scientific failure mode: independent signatures or same-round pseudo-assent producing a primary label. Next phase must add manually coded semantic evidence plus authenticated receipt/action checks; never classify arbitrary text lexically.

## E4 checkpoint

E1–E3 implementation checkpoint: a96c5b6. Recovery discovered successful frozen F1 273c814 existed on the original checkout's branch but was absent from origin/main; merged its ancestry unchanged (merge commit shown by `git log`). Actual successful F1 regression suite then passed: 56 total tests (50 pre-existing + 6 mainstudy), 10.386s. No historical F1 source modified by mainstudy.

Executed `/private/tmp/mainstudy-env/bin/python -m mainstudy.cli validate --out /private/tmp/mainstudy-matrix-v1`: all 16 matrix episodes × 112 scripted generations and exact replay; 18 P/R negative episodes and replay; 2 maximal legal four-quarter NUL-message episodes. Each matrix episode had Q1 qualified throughput 4, Q2–4 q0 deployments 12 and hidden v1 deployments 6. These are SCRIPTED apparatus outcomes, not scientific behavioral evidence. Positive primary only in scripted A; silent arms report not_observable/None. Independent/cooperation/same-round/defection/stale/invalid/timeout/hold/withhold traces do not yield positive primary labels.

E4 baseline/self-review: no later-quarter truth narrative, carryover or final-horizon announcement; proposer/assent text exists only in scripts, never agent templates. Exact request/replay paths are Q1–Q4 nonces. New failure mode: partial open calls must not be retried or counted as voluntary holds. Added reconciliation with explicit unknown/not-dispatched classifications; interruption adversarial test pending E5.

**Established launch blocker:** maximal legal histories are not certified to fit proposed DeepSeek 1,048,576-token context. Structural byte/token bound exceeds it; normal scripted fits do not prove maximum fit. No truncation or cap reduction adopted. Expanded engineering wire-byte guard to 2MiB so legal histories can be inspected. Exact tokenization/encoding proof or separately approved provider capacity is still required. Proposed full-context reservation $75/matched pair, maximum $600/16 episodes (1,792 calls), NOT spending authorization. Budget, absolute stopping timestamp, prompts/fixtures/model config require separate researcher approval.

Next action: adversarial replay/interruption and concurrency tests, mocked provider/approval gates; publish rendered review package and source/oracle inventory; independent final critique and final test run.
