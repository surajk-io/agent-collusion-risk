> **ACTIVE STATUS OVERRIDE — 2026-10-26:** Read [CURRENT-STUDY.md](../../CURRENT-STUDY.md) first. This document preserves earlier decisions/proposals, including assumptions superseded for the current main study. Do not implement or interpret older carryover, detailed repair/exposure/scalar welfare, single-quarter H1-as-main, categorical pre-review blocking, or multi-parameter audit systems as current requirements. Exact main-study policy, cases, horizon and controls still await approval.

# Bounded F1 runner

Current review entry point: [F1-FINAL-PREFLIGHT.md](F1-FINAL-PREFLIGHT.md).
The implementation baseline is `be5c7c5`; latest main at task start was `bbd24a7`.
**No live F1 execution is authorized.** The exact [v2 prompt/settings amendment](PROMPT-AMENDMENT-v2.md) is proposed for researcher review. Historical v1 [amendment](AMENDMENT.md), [preflight](PREFLIGHT.md) and [eight requests](review-requests/index.json) are retained. Current [eight full HTTP bodies, hashes and diffs](final-review-requests/index.json) are separate.

From `research/organizational-coalitional-risk/M4-harness-foundations`, with the pinned `requirements.txt` installed:

```sh
python -m unittest discover -s tests -v
python -m f1.cli script --graph P --trace positive --out runs/P-positive
python -m f1.cli script --graph R --trace positive --out runs/R-positive
python -m f1.cli replay --run runs/P-positive --out runs/P-replay
python -m f1.cli preflight --out runs/new-preflight-review
```

Every output directory must be new. Script traces remain `positive`, `independent`, `hold`, `escalate`, `refuse`, `same-round`, `partial`, `stale`, `invalid`, `timeout`, `cooperation`, `nonreciprocal`. They are deterministic apparatus data, never observed behavior. Existing scripted P/R and replay tests are retained. Fixture security tests were not rerun.

`materials.py` verifies source bytes, assembles allowlisted evidence and renders exactly one system and one JSON user message. Each actor/slot uses a new stateless Chat Completions request with full permitted history, no diagnostic history and no provider session. Only participants retain messages. All four requests are frozen before concurrent stage dispatch; owner and reviewer commits are atomic. Reviewer evidence arrives only for submissions and cannot be rewritten by the owner. Qualification and vulnerability never veto mechanically valid signatures. F1 ends at deployment resolution and the board: no audit, maintenance or Q2.

`vertex.py` now targets Google Model Garden's global OpenAI-compatible endpoint and `deepseek-ai/deepseek-v4.1-flash-maas`. It passes exact serialized body bytes, with thinking=true, JSON object and stream=false. Authentication is injected separately. Only final assistant `message.content` under one `stop` choice becomes an action. Unknown model, missing content, reasoning-only, truncation, tool calls, HTTP errors and malformed JSON have no repair, retry or fallback. Complete raw responses, metadata/usage/finish reasons, returned reasoning and available partial response bytes are researcher-only. Historical native-shaped scripted responses are accepted only under their explicit scripted representation tag.

`archive.py` writes/fsyncs requests before send and complete available response bodies before extraction. An append-only hash-chained ledger links artifacts; replay verifies retained bytes and deterministic committed states without provider calls. Timeouts close at synchronized harness receipt >180 seconds from handoff; receipt at exactly180 seconds is valid. HTTP completion and harness receipt are separate timestamps. Late/partial/malformed responses remain archived and cannot overwrite a closed slot. The transport uses an absolute deadline and socket interruption; OS DNS and a provider continuing generation after disconnect remain real integration risks. Raw bytes are HTTP bodies, not encrypted framing or credentials.

The future `live` command requires a separately recorded human approval pinned to a clean Git revision and request/config/capacity hashes. No approved file is shipped. Once authorized, it reserves USD5 per graph via exclusive canonical claims, allows 28 slots per graph once, rejects reused/diagnostic sessions and excessive input bounds, and never resumes/replaces an interrupted assignment automatically. Reservation arithmetic is conservative under documented rates/token assumptions; it is not a provider-enforced billing cap. Authentication uses `gcloud auth application-default print-access-token`, with stderr excluded and a20-second acquisition timeout inside the slot's180-second allowance.

Annotation forms preserve uncertainty. Semantic coding remains human work; only scripts receive gold coding. Explicit assent, actual exact-version actions, independent approvals, policy misunderstandings, harmful arrangements and causal influence remain distinct. One P/R pair supports no population or causal graph-effect claim. Researcher-only documentation retains full transparency about simulated deployment, source-only signatures and one shared technical vignette.
