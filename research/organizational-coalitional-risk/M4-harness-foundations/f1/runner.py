"""One quarter: C1/C2/O/C3/C4/C5/R, deployment resolution, board. Nothing later."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import json
import threading
import time

from foundations.contracts import AGENTS, Invalid, communication, decode
from foundations.provider import Request, Session, now
from foundations.records import blob, digest, provenance, unblob
from .archive import Archive
from .materials import Assets, HERE, ORDER, SOURCE, PROMPT_REVISION, render
from .vertex import CallError, extract, metadata


def initial():
    return {actor: {"owner_decision": None, "review_decision": None, "summary": None,
                    "owner_signature": None, "reviewer_signature": None, "deployed": False}
            for actor in AGENTS}


def manifest(spec, assets, config, script_origin, repository):
    paths = [str(p.relative_to(repository)) for p in sorted(HERE.parent.rglob("*"))
             if p.is_file()
             and not any(x in p.parts for x in ("__pycache__", ".venv", "runs", "review-requests"))]
    return {"scope": "F1 authorization-and-board feasibility only", "run": asdict(spec) | {
        "generation_json": json.loads(spec.generation_json)},
        "protocol": {"integrated": "f01b498855d7b0bd637c22f852c58e20a13cd316",
                     "capability": "9eb31daa1fbdaf9c8512279afac3d59aeda64df4",
                     "F1_amendment_sha256": digest((HERE / "AMENDMENT.md").read_bytes()),
                     "F1_v2_amendment_sha256": digest((HERE / "PROMPT-AMENDMENT-v2.md").read_bytes())},
        "prompt_revision": PROMPT_REVISION,
        "model": {"provider": config.provider, "endpoint": config.endpoint, "model": config.model,
                  "settings": json.loads(config.settings_json)},
        "allocation": {a: {"service_id": "service-" + a, "release_id": "release-" + a,
                           "source_hash": SOURCE, "build_hash": None,
                           "evidence_hash": assets.evidence_hash, "qualification_complete": False,
                           "vulnerability": "not_inferred_by_runner", "functional_gate": True}
                       for a in AGENTS},
        "shared_source_provenance": json.loads((HERE / "material-provenance.json").read_bytes()),
        "input_hashes": assets.hashes, "origin": script_origin,
        "provenance": provenance(repository, paths),
        "live_execution_authorized": False}


class Runner:
    def __init__(self, spec, assets, config, adapter, archive, *, execution_approval=None):
        if not getattr(adapter, "scripted", False):
            from .live import Approval
            if not isinstance(execution_approval, Approval) or execution_approval.graph != spec.graph:
                raise Invalid("live_execution_not_authorized")
        if config.settings_json != spec.generation_json:
            raise Invalid("settings_mismatch")
        self.spec, self.assets, self.config = spec, assets, config
        self.adapter, self.archive = adapter, archive
        self.state = initial()
        self.messages = []
        self.receipts = {a: [] for a in AGENTS}
        self.stages = []

    def histories(self):
        result = {a: [] for a in AGENTS}
        for message in self.messages:
            for actor in [message["sender"]] + message["recipients"]:
                result[actor].append(dict(message))
        return result

    def _call(self, actor, stage, raw, output, starts, lock):
        name = f"{stage}-{actor}"
        self.archive.artifact(f"requests/{name}.json", raw, stage, actor,
                              "request_ready", "flushed_before_send")
        request = Request(Session(self.spec.run_id, actor, self.spec.namespace), stage,
                          self.config, raw)
        self.archive.event(stage, actor, "dispatch_ready", "recorded")
        handoff = now()
        with lock:
            starts[actor] = handoff["monotonic_ns"]
        try:
            reply = self.adapter.complete(request, self.spec.timeout_seconds)
            with lock:
                receipt = now()  # atomic receipt/deadline resolution vs watchdog
                starts.pop(actor, None)  # deadline concerns receipt, not disk latency
            # Save complete provider payload before parsing or deciding validity.
            self.archive.artifact(f"responses/{name}.json", reply.payload, stage, actor,
                "response_received", "recorded", {"representation": reply.representation,
                 "http_status": reply.status, "handoff": handoff, "receipt": receipt})
            self.archive.artifact(f"responses/{name}.metadata.json", json_bytes(metadata(reply)),
                                  stage, actor, "response_metadata", "recorded")
            error = None
            if receipt["monotonic_ns"] > handoff["monotonic_ns"] + self.spec.timeout_seconds * 1e9:
                error = "late_completion"
            try:
                action_bytes = extract(reply)
            except (Invalid, KeyError, TypeError, UnicodeError, AttributeError, IndexError):
                action_bytes, error = None, error or "provider_output"
        except CallError as exc:
            with lock:
                receipt = now()
                starts.pop(actor, None)
            if exc.payload:
                self.archive.artifact(f"responses/{name}.error-body", exc.payload, stage,
                    actor, "error_body", "recorded", {"representation": exc.representation,
                                                     "http_status": exc.status})
            self.archive.artifact(f"responses/{name}.error.json", json_bytes({"code": exc.code,
                "handoff": handoff, "receipt": receipt}), stage, actor, "provider_error", exc.code)
            action_bytes, error = None, exc.code
        except Exception:
            # Unexpected failures are integrity failures, not behavior/fallbacks.
            self.archive.event(stage, actor, "internal_error", "aborted")
            raise
        with lock:
            # Offline replay preserves the original terminal resolution, including
            # late HTTP bodies and watchdog dispositions, rather than re-timing it.
            if getattr(self.adapter, "scripted", False) and hasattr(self.adapter, "resolved"):
                original = self.adapter.resolved[stage][actor]
                action_bytes = unblob(original["raw"]) if original["raw"] is not None else None
                error = original["error"]
            if actor in output:
                self.archive.event(stage, actor, "late_completion", "ignored")
            else:
                output[actor] = {"raw": action_bytes, "error": error}

    def _validate(self, stage, actor, result):
        if result["error"]:
            return None, result["error"]
        try:
            if stage.startswith("C"):
                value = communication(result["raw"], actor, self.spec.limits)
            else:
                value = decode(result["raw"], "OwnerDecision" if stage == "O" else "ReviewSlotOutput")
                target = actor if stage == "O" else AGENTS[self.spec.reviewers.index(actor)]
                submitted = self.state[target]["owner_decision"] == "submit"
                if stage == "R" and not submitted:
                    if value != {"decision": "not_applicable"}:
                        raise Invalid("review_on_unsubmitted")
                    return value, None
                if value.get("release_id") != "release-" + target or value.get("candidate_hash") != SOURCE:
                    raise Invalid("release_binding")
                if len(value.get("summary", "").encode()) > self.spec.limits.summary_bytes:
                    raise Invalid("summary_bytes")
            return value, None
        except Invalid as exc:
            return None, str(exc)

    def run(self):
        for stage in ORDER:
            # Freeze every context before dispatch. No pending output enters one.
            histories = self.histories()
            requests = {a: render(self.spec, self.assets, a, stage, self.state,
                                  histories, self.receipts) for a in AGENTS}
            results, starts, lock = {}, {}, threading.Lock()
            pool = ThreadPoolExecutor(max_workers=4)
            futures = [pool.submit(self._call, a, stage, requests[a], results, starts, lock) for a in AGENTS]
            try:
                while True:
                    for future in futures:
                        if future.done():
                            future.result()  # abort on internal/persistence failure
                    with lock:
                        for actor, start in starts.items():
                            if actor not in results and time.monotonic_ns() > start + self.spec.timeout_seconds * 1e9:
                                results[actor] = {"raw": None, "error": "timeout"}
                                self.archive.event(stage, actor, "slot_timeout", "closed")
                        if len(results) == 4:
                            break
                    time.sleep(0.001)
            finally:
                # Timed-out requests may still deliver an archived late response;
                # they cannot change committed decisions. Transport must close.
                pool.shutdown(wait=False)
            self.archive.state("slot-results-" + stage, {a: {
                "raw": blob(results[a]["raw"]) if results[a]["raw"] is not None else None,
                "error": results[a]["error"]} for a in AGENTS}, stage)
            decisions = {a: self._validate(stage, a, results[a]) for a in AGENTS}
            next_state = json.loads(json_bytes(self.state))
            next_messages = []
            receipts = {}
            for actor in AGENTS:
                value, error = decisions[actor]
                receipt = {"phase": stage, "disposition": "valid" if error is None else "invalid",
                           "cause": error}
                if stage.startswith("C"):
                    if value is not None:
                        for i, message in enumerate(value["messages"]):
                            identifier = digest(json_bytes([stage, actor, message]))[:24]
                            next_messages.append({"message_id": "m-" + identifier,
                                "episode_id": self.spec.run_id, "quarter": 1, "round": int(stage[1:]),
                                "sender": actor, **message})
                    receipt["accepted_messages"] = len(value["messages"]) if value is not None else 0
                elif stage == "O":
                    chosen = value["decision"] if value else "hold_timeout"
                    next_state[actor]["owner_decision"] = chosen
                    receipt.update(decision=chosen, release_id="release-" + actor, candidate_hash=SOURCE)
                    if chosen == "submit":
                        summary = value["summary"]
                        next_state[actor]["summary"] = summary
                        next_state[actor]["owner_signature"] = signature(self.spec, self.assets, actor, actor, summary)
                        receipt["summary"] = summary
                else:
                    target = AGENTS[self.spec.reviewers.index(actor)]
                    eligible = self.state[target]["owner_decision"] == "submit"
                    chosen = value["decision"] if value else ("reject_timeout" if eligible else "not_applicable")
                    next_state[target]["review_decision"] = chosen
                    receipt.update(decision=chosen)
                    if chosen == "approve":
                        next_state[target]["reviewer_signature"] = signature(self.spec, self.assets, target, actor)
                receipts[actor] = receipt
            # Durable commit of ALL decisions/deliveries before state publication.
            record = {"state": next_state, "delivered_messages": next_messages, "receipts": receipts}
            self.archive.state(stage, record, stage)
            self.state = next_state
            self.messages.extend(next_messages)
            for actor in AGENTS:
                self.receipts[actor].append(receipts[actor])
            self.stages.append(stage)
        board = []
        for actor, reviewer in zip(AGENTS, self.spec.reviewers):
            item = self.state[actor]
            item["deployed"] = mechanically_valid(self.spec, self.assets, actor, item, functional_gate=True)
            board.append({"owner": actor, "release_id": "release-" + actor,
                          "owner_decision": item["owner_decision"], "reviewer": reviewer,
                          "review_decision": item["review_decision"],
                          "signatories": [actor, reviewer] if item["deployed"] else
                              ([actor] if item["owner_signature"] else []),
                          "deployed": item["deployed"]})
        self.archive.state("deployment", self.state, "D")
        self.archive.state("board", board, "B")
        return board


def json_bytes(value):
    from foundations.contracts import canonical
    return canonical(value)


def signature(spec, assets, owner, signer, summary=None):
    binding = asdict(assets.binding(spec, owner))
    return {"binding": binding, "signer": signer, "kind": "simulated_authorization_record",
            "summary_sha256": digest(summary.encode()) if summary is not None else None}


def mechanically_valid(spec, assets, owner, item, *, functional_gate):
    reviewer = spec.reviewers[AGENTS.index(owner)]
    return bool(functional_gate and item["owner_decision"] == "submit" and
                item["review_decision"] == "approve" and
                item["owner_signature"] == signature(spec, assets, owner, owner, item["summary"]) and
                item["reviewer_signature"] == signature(spec, assets, owner, reviewer))
