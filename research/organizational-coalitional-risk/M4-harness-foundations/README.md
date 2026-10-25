# M4 preparatory deterministic foundations

**Continuation:** the separately authorized bounded F1 runner and its current
usage/preflight are in [f1/README.md](f1/README.md) and
[f1/PREFLIGHT.md](f1/PREFLIGHT.md). The original `dc0f7b4` foundation checkpoint
and its then-open decisions are retained below as historical scope. Three limited
F1 approvals supersede only the rows explicitly identified in [the amendment](f1/AMENDMENT.md).

Authorized engineering preparation, 26 October 2026. **M3 remains unapproved.**
This directory supplies small offline primitives, not an executable behavioral
protocol. The active gate remains [M3 in the roadmap](../ROADMAP.md).
No experimental LLM call, behavioral pilot, seeded model interaction, fixture
security rerun or empirical collusion result is produced here.

## Run locally

Python 3.10+; tested with Python 3.14.6. From this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Dependency installation downloads packages; the test command uses temporary files
and fixed scripts only, with no LLM/API/network calls or credentials. All resolved
validator dependencies are pinned. Tests require no candidate branch checkout.

## Architecture and boundary

| Component | Implemented responsibility |
|---|---|
| `contracts.py` | Named JSON Schema entry points; strict UTF-8/JSON; duplicate-key/unknown-field rejection; byte limits; recipient validation; immutable release/episode/source/build/evidence bindings; owner/reviewer intent permission checks in P and R |
| `visibility.py` | Private four-slot collection; one committed record per barrier; participant-only message delivery/history; explicit history watermark; independent reviewer evidence projection; no pending-decision projection |
| `records.py` | Exact bytes as base64 plus SHA-256; single-writer atomic journal, integrity chain, deterministic replay and idempotent event keys; retained Git revision, dirty diff, status and explicit artifact bytes |
| `provider.py` | Stateless `Adapter` protocol; fixed `ModelConfig`; actor/episode/namespace session identity; complete input/output byte recording; activation/handoff/receipt UTC and monotonic times; error lineage; only a fixed scripted implementation |
| `tests/fixtures.py` | Clearly synthetic release/evidence bytes, no real build or qualification claim |

Future flow: a separately approved context builder projects a frozen snapshot;
an adapter accepts a complete serialized request; raw output is retained;
named-schema/permission validation produces an intent; an opaque barrier records
all four slots in one durable event. Only committed communication records feed
participant histories. Replaying committed barriers reconstructs identical visible
bytes independently of completion order. Replaying never invokes a provider.

Owner/reviewer checks **validate intents only**. They do not create cryptographic
signatures, deploy releases, enforce security/qualification policy or assign
`hold_timeout`/`reject_timeout`. Invalid/missing results retain explicit errors.
The scripted snapshot supplies submission eligibility; this library does not
derive it by executing an unapproved protocol. The reference
`C1,C2,O,C3,C4,C5,R` tuple and its watermark test document compatibility;
there is no production episode scheduler, batch dispatch, board or lifecycle.

Each request is complete and stateless: there is no implicit provider history,
shared conversation ID, reasoning memory, tool execution or automatic retry.
Sessions distinguish actor, episode and diagnostic namespace. A future live
adapter must preserve this boundary and report requested/resolved route, model
version, dispatch, finish reason, usage/cost and unsupported settings. The fixed
configuration is supplied by the experimenter, independently of validation logic.
No endpoint/model is selected here. The protocol cannot prove an arbitrary future
adapter/server is isolated; that remains an integration test and approval gate.
Message barriers, ledgers and snapshot projections also enforce matching episode
and diagnostic namespace, preventing stale scripted histories from crossing runs.

For a researcher archive, explicitly append a `provenance(repository, paths)`
record before requests, including `sources.json`, schema, implementation, fixed
configuration, scripts and all input artifacts. This function retains actual
bytes, including named untracked files, along with Git SHA/status/diff. A dirty
diff alone does not capture untracked files. Never project this archive into
model input. `invoke` writes the request before adapter invocation, then records
actual adapter handoff and receipt separately from activation. Interrupted calls
remain unresolved; resampling the same invocation is denied. Dispatch timing,
stream receipt and billing are adapter responsibilities, untested for live APIs.

Journal commit uses fsync + atomic file replacement + directory fsync. Failure
before replacement leaves the previous prefix; after replacement memory follows
disk even if durability confirmation fails. Reopen and verify before recovery;
do not infer a behavioral result from an incomplete request. One trusted process
owns a journal. Concurrent writers, process sandboxing, malicious whole-file
rewrites, large-log performance and automated crash recovery are outside scope.
Agent isolation here is a data/session boundary, not an OS security boundary.

## Provisional profiles and provenance

`sources.json` pins fetched main `1c6927f`, integrated candidate `f01b498` and
capability candidate `a237254` to full SHAs. Main M0 literature/critique,
M1 design review/approval, M2 approval, M3 handoff and both requested candidate
packages were recovered. The vendored schema is byte-identical to the integrated
candidate, with a pinned digest; no candidate/approved document is modified.
The capability branch may advance concurrently; this work does not imply approval
of its pinned or subsequent revisions.

The approved overarching question remains:

> How do organizational structures shape the opportunities for harmful coordination among task-specialized AI agents, and to what extent do properties of those opportunities predict realized collusion and organizational harm?

The existing proposed narrow working question remains:

> Does the organization of cross-workflow reciprocal reviewer dependencies alter LLM agents' propensity to propose, negotiate or execute unauthorized reciprocal approvals, when agent workload and per-task sign-off requirements are matched?

Earlier staggered decisions were superseded by approved simultaneous reviews.
The archived Jira pilot is a technical smoke, not spontaneous collusion evidence.
M2 carryover versus the later external-transfer agreement still needs a versioned
amendment. None of those rules are implemented here. Independent mistakes,
shared evidence, helpfulness, authority claims, coercion and mechanical cycles
remain competing explanations; this code makes no collusion classification.

Candidate-schema validation is deliberately a **selected test profile**. Its
three-message object maximum is inherited, even when cross-message disjointness
is disabled. The earlier five-message alternative would need a separately
versioned schema; it is not represented by this profile. `Limits` requires explicit
byte/disjointness values, and `Messages` requires an explicit round bound.
Tests select 1024/2048 bytes, disjoint recipients and five rounds. These are
synthetic compatibility witnesses, not adopted behavioral defaults. The cutoff
helper tests an inclusive monotonic boundary; it selects no experiment timeout.
Permission checks compare trusted binding records and output release/hash fields;
they do not authenticate source/build/evidence bytes against those records. A
future approved manifest/preflight must define owner/reviewer evidence digest
scope and verify every supplied artifact before constructing these snapshots.

`named_schema` extracts only required definitions and removes research metadata.
`project` is a neutral JSON test projection, **not** the candidate prompt renderer:
it lacks slot instructions/receipts and does not select pre/post-owner exposure.
The trusted caller supplies the appropriate snapshot and watermark. No hidden
truth/annotation argument exists. Caller-provided evidence/public text still
requires semantic review and an approved artifact allowlist; a Python type cannot
certify that arbitrary supplied text is free of hidden labels.

## Validation and remaining decisions

**Executed: 22 unittest tests passed on Python 3.14.6**, using the command above
and the pinned requirements. The suite covers all actors in both graphs for authority and
stale bindings; named schemas, Unicode/byte boundaries and invalid output;
private/group delivery, whole-sender rejection, missing outputs and forwarding;
all 24 completion orders; atomic commit, detached records, idempotency/conflicts,
corruption, failures before/after file replacement, exact replay/projection;
session/configuration isolation, raw bytes/errors, interrupted calls and cutoffs.
Read-only independent implementation critique identified mutable event exposure,
a post-replace failure window, an implicit round bound and timestamp ambiguity;
all received code remedies and regression tests. It is criticism, not approval.

This is a **partial foundation** for the candidate offline matrix, not a claim
that its A/H/L/Q cases pass. No deployment, qualification, welfare, audit,
annotation, capacity or real-provider test is claimed. Gold-trace annotation and
positive/negative behavioral controls remain unimplemented. All four synthetic
sources are fixture strings, not replacements for missing release packets.

Before completing the runner, researcher decisions must freeze:

| Open scientific decision | Alternatives / inferential consequence |
|---|---|
| Scenario and policy amendment | Approved costly-defect scenario versus proposed qualification gap; q/v violation and confidential-metadata meanings change the construct |
| Release allocation and controls | Four evidenced distinct releases/two archetypes versus explicit duplicated-vignette amendment; real source/build/evidence bindings and genuine qualified-safe control remain missing |
| Literal inputs and visibility | Exact prompts, policy, evidence attachments, summary treatment, receipts, history and evaluation cues; determines what each actor can know |
| Timing, messaging and failures | Five-round schedule versus alternatives, one-contact-per-peer versus prior cap, no-message control, byte/token/time limits, concurrency, retries/fallbacks and cutoffs affect coordination opportunity |
| Lifecycle, accountability and welfare | External transfer versus M2 carryover; q/v audit union/dependence, feedback, latency/exposure, incentives, probabilities and independent value/cost accounting require explicit values and amendments |
| Provider/configuration | One target endpoint/resolved model, sampling/reasoning/seed/output format, capacity and isolation validation, retention and route-change handling |
| Evidence labels and causal controls | Reception-aware assent/enactment, coordinator versus mutual reception, uncertainty/human coding, unilateral/obedience/error alternatives, action versus transcript endpoints |
| Diagnostics and collection | Exact capability/seeded stimuli, scoring and gates; fresh-context separation; sample/randomization, order, exclusions, stopping, analysis and currency/call budgets |

These choices are **open/proposed**, not settled by tests. Preserve approved
M1/M2 decisions and archive approved amendments and exact M3 revision before
implementing behavioral transitions; separately authorize calls. Next research
action remains resolution of the M3 decision registers (D01–D16, CB01–CB10).
