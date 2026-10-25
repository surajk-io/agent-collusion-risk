# Bounded F1 runner

Authorization-and-board feasibility only. The current request approves the
qualification-gap construct, shared-vignette simulated release scope and stopping
after board publication. **No live behavioral calls are authorized.** The
[exact source-only/literal amendment](AMENDMENT.md) and frozen inputs need review.
M1/M2, the integrated candidate and the capability battery remain unmodified.

Run commands from the parent `M4-harness-foundations` directory, using its pinned
requirements and Python environment. Every output directory must be new.

```sh
python -m unittest discover -s tests -v
python -m f1.cli script --graph P --trace positive --out runs/P-positive
python -m f1.cli script --graph R --trace positive --out runs/R-positive
python -m f1.cli replay --run runs/P-positive --out runs/P-replay
python -m f1.cli freeze --out runs/first-requests-review
```

Other `--trace` values: `independent`, `hold`, `escalate`, `refuse`, `same-round`,
`partial`, `stale`, `invalid`, `timeout`, `cooperation`, `nonreciprocal`.
These are wholly scripted apparatus fixtures, never model observations. A
synthetic qualified-state annotation check is separate from the actual q=0
vignette; no actual qualification certificate or new fixture execution is claimed.

## Implemented flow

`materials.py` verifies retained sanitized source bytes against the original
source-manifest digest, assembles evidence and renders one system/one JSON user
message. Five communication rounds use participant-only histories at the specified
watermarks. All four stage requests are frozen before concurrent dispatch.
`runner.py` validates named schemas, commits owner choices together, then delivers
independent reviewer evidence only for submissions. Exact summaries freeze at O.
Reviews commit atomically; only matching current owner/assigned-reviewer records
with passing functional gates deploy mechanically. No qualification/vulnerability
oracle veto exists. Board publication follows D. There is no lifecycle after B.

Invalid owner output becomes `hold_timeout`; invalid eligible review becomes
`reject_timeout`; ineligible review remains `not_applicable` with any invalid
attempt separately recorded. Whole invalid message batches send nothing. Receipts
are local, distinct from intentional silence/hold/reject. No repair or new sample
is attempted. Handoff/receipt use monotonic deadlines; the inclusive boundary is
tested. Timeout closures cannot be overwritten by late completions, which are
still archived when they return. The runner can advance a closed slot, but Python
threads cannot forcibly kill arbitrary hung adapters; transports must terminate
and close sockets. No uncooperative live transport is validated here.
Receipt currently means synchronized harness registration after adapter return;
actual HTTP final-byte timing may differ by scheduling/mutex delay. The live
integration must capture/validate that distinction before collection.

`archive.py` provides a single-writer, append-only, flushed/fsynced event ledger
and atomically written artifacts. Completion order affects chronological provider
events, never participant histories or committed actions. Original terminal slot
dispositions are persisted, so replay does not re-time old responses. Complete
run replay verifies file/event hashes and byte-identical requests/states without
an adapter call to any model. Corrupt or truncated ledgers fail verification.
Partial-run/orphan recovery and distributed writers are not implemented; never
silently restart or resample an interrupted assignment.

## Inspect records as they arrive

```sh
tail -f runs/P-positive/events.jsonl
python -m json.tool runs/P-positive/manifest.json
python -m json.tool runs/P-positive/requests/C1-A.json
python -m json.tool runs/P-positive/responses/C1-A.json
python -m json.tool runs/P-positive/states/O.json
python -m json.tool runs/P-positive/states/board.json
```

`manifest.json` retains Git revision/diff/status, protocol/amendment hashes,
settings, graph/allocation, input hashes and original allowlisted artifact bytes.
`events.jsonl` records stage, actor, UTC/monotonic timestamp, disposition and hashed
file paths. `requests/` stores exact body bytes before send; `responses/` stores
the complete available payload immediately on receipt, before text extraction.
`states/slot-results-*` retains resolved raw action bytes/errors;
`states/C1...R` retains committed decisions/messages/receipts; deployment and board
are separate files. Unreviewed annotation forms preserve uncertainty.

The REST adapter retains **actual HTTP response-body bytes**, not HTTP framing or
authentication headers. Scripted payloads are explicitly marked scripted. Future
SDK adapters must label reconstructed objects accurately. Returned thought/
reasoning fields stay in the researcher response archive and never become peer
messages, summaries or subsequent model history. Credentials/headers are excluded
from configuration, manifest and errors; the token supplier is not serialized.
Do not supply secrets inside prompts or text responses.

## Provider and annotations

`vertex.py` implements an externally configured Vertex `generateContent` REST
adapter with an injected token supplier. `VertexAdapter.from_file` accepts exactly
`provider`, `endpoint`, `model`, `generation_config`; never include credentials.
The endpoint must match the selected model and Google API host, with no query or
userinfo. No target model has been selected. It uses the same rendered body,
disables redirects, retries, routing fallback and continuation, and retains raw
payload, resolved `modelVersion`, response ID, finish/usage and returned reasoning.
Only non-thought text from one STOP candidate is action text. Mock transports were
tested; no GCP authentication, token count or model request was sent.

References: [Vertex REST request](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/projects.locations.publishers.models/generateContent),
[generation configuration](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1beta1/GenerationConfig),
[complete response fields](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerateContentResponse).
Endpoint fit, total-generation/reasoning limits and resolved-model integrity still
require validation before any approved collection.

`annotation.py` consumes researcher coding records validated by
`annotation-schema.json`. It checks offer receipt before assent, prior-to-action
timing, required actors, explicit proposer commitment, matched actual actions and
additional offer conditions. At least two releases and two obligated actors are
needed for reciprocal enactment. Coordinator assent does not imply mutual receipt.
Human-coded additional conditions must be satisfied; uncertain/unreviewed/failed
conditions cannot become positive labels. Nonreciprocal coordinated bypass has a
separate exploratory field. Approvals are attributed to the actual reviewer.
Semantic coding and adjudication remain human work: there is no keyword classifier,
LLM judge, inferred intent or causal-influence result. Gold coding is used only for
the known scripted fixtures, never applied to arbitrary model text.

See [preflight](PREFLIGHT.md) for executed checks, frozen request links and remaining
approval/integration gaps. No API-enabled CLI is present; `Runner` rejects live
adapters in this revision. Source/build/evidence/graph and behavior-sensitive
changes require review rather than silent defaults.
