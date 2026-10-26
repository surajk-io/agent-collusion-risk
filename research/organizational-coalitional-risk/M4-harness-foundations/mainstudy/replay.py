"""Replay authenticated responses; reconcile interrupted prefixes without calls.

Unknown/open dispatches remain explicit technical failures, never re-sampled.
Reconciliation makes an analysis artifact, never replaces the partial original.
"""
from pathlib import Path
import re
from foundations.contracts import AGENTS, canonical, strict_json, Invalid
from foundations.records import blob
from foundations.provider import ModelConfig
from f1.archive import inspect
from f1.vertex import Reply, CallError, extract
from .contracts import Spec, ORDER
from .fixtures import Release
from .runner import execute


class Replay:
    scripted = True

    def __init__(self, root, partial=False):
        self.root = Path(root)
        self.manifest, events = inspect(root)
        self.partial = partial
        self.files = {p for e in events for p in e["files"]}
        self.responses = {(e["stage"], e["actor"]): e["details"] for e in events if e["event"] == "response_received"}
        self.resolved = {f"Q{q}-{s}": strict_json((self.root / f"states/slot-results-Q{q}-{s}.json").read_bytes())
                         for q in range(1, 5) for s in ORDER
                         if f"states/slot-results-Q{q}-{s}.json" in self.files}
        # Reconcile every open slot from authenticated persisted evidence. No
        # receipt or response record means unknown outcome, not voluntary hold.
        for q in range(1, 5):
            for s in ORDER:
                key = f"Q{q}-{s}"
                if key not in self.resolved and partial:
                    resolved = {}
                    for actor in AGENTS:
                        raw, error = None, None
                        detail = self.responses.get((key, actor))
                        if detail:
                            try:
                                raw = extract(Reply((self.root / f"responses/{key}-{actor}.json").read_bytes(),
                                                    detail["representation"], detail.get("http_status", 200)))
                            except (Invalid, KeyError, TypeError, UnicodeError):
                                error = "provider_output"
                            if detail["receipt"]["monotonic_ns"] > detail["handoff"]["monotonic_ns"] + self.manifest["spec"]["timeout_seconds"] * 1e9:
                                error = "late_completion"
                        else:
                            error_file = f"responses/{key}-{actor}.error.json"
                            error = (strict_json((self.root / error_file).read_bytes())["code"] if error_file in self.files
                                     else "interrupted_unknown" if f"requests/{key}-{actor}.json" in self.files
                                     else "not_dispatched_after_interruption")
                        resolved[actor] = {"raw": blob(raw) if raw is not None else None, "error": error}
                    self.resolved[key] = resolved
        self.complete_archive = any(e["event"] == "mainstudy_complete" for e in events)
        if not partial and not self.complete_archive:
            raise Invalid("incomplete_archive_use_reconcile")

    def complete(self, request, timeout):
        stage, actor = request.slot_nonce, request.session.actor
        name = f"{stage}-{actor}.json"
        request_path = "requests/" + name
        if request_path in self.files:
            if request.input_bytes != (self.root / request_path).read_bytes():
                raise Invalid("replay_request_changed")
        elif not self.partial:
            raise Invalid("missing_request")
        result_path = f"states/slot-results-{stage}.json"
        if result_path in self.files:
            resolved = strict_json((self.root / result_path).read_bytes())[actor]
            if resolved["error"] and (stage, actor) not in self.responses:
                raise CallError(resolved["error"])
        key = stage, actor
        if key in self.responses:
            detail = self.responses[key]
            return Reply((self.root / "responses" / name).read_bytes(), detail["representation"], detail.get("http_status", 200))
        error_path = "responses/" + name.removesuffix(".json") + ".error.json"
        if error_path in self.files:
            raise CallError(strict_json((self.root / error_path).read_bytes())["code"])
        if not self.partial:
            raise Invalid("missing_response")
        raise CallError("interrupted_unknown" if request_path in self.files else "not_dispatched_after_interruption")


def replay(original, target, partial=False):
    adapter = Replay(original, partial)
    m = adapter.manifest
    spec = Spec(**m["spec"])
    config = ModelConfig(**(m["model"] | {"settings_json": canonical(m["model"]["settings_json"])}))
    releases = {}
    for key, item in m["releases"].items():
        q, a = key.split("-")
        releases[int(q), a] = Release(**(item | {k: canonical(item[k]) for k in ("source_json", "evidence_json", "oracle_json")}))
    runner = execute(target, spec, adapter, trace=m["trace"], config=config, releases=releases)
    # Compare every durable committed stage prefix, not nondeterministic clocks.
    for name in sorted(adapter.files):
        if re.fullmatch(r"states/Q[1-4]-(?:C[1-5]|S|D|board|audit|rollover)\.json", name):
            if (Path(original) / name).read_bytes() != (Path(target) / name).read_bytes():
                raise Invalid("replay_state_changed:" + name)
    runner.archive.state("replay-result", {"original": str(Path(original).resolve()),
        "kind": "interrupted_prefix_reconciliation" if partial else "complete_replay",
        "original_complete": adapter.complete_archive,
        "missing_slots_are_technical_failures": partial}, "REPLAY")
    return runner
