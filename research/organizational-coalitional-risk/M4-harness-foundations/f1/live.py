"""Dormant future execution path. Requires separately recorded human approval.

No approved authorization file is shipped. Constructing a proposal, running tests,
freezing requests or pushing this code supplies no authorization.
"""
from dataclasses import dataclass
from pathlib import Path
import subprocess

from foundations.contracts import AGENTS, Invalid, canonical, strict_json
from foundations.records import digest
from .materials import Assets, HERE, PROMPT_REVISION, render
from .preflight import input_bound
from .runner import initial
from .vertex import CallError, VertexAdapter

REVIEW = HERE / "final-review-requests"


@dataclass(frozen=True)
class Approval:
    record: dict
    graph: str


def validate_approval(path, graph, repository):
    value = strict_json(Path(path).read_bytes())
    if value.get("status") != "explicitly_authorized" or not value.get("researcher_approval_reference"):
        raise Invalid("live_execution_not_authorized")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository).decode().strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=repository)
    if value.get("git_revision") != head or dirty:
        raise Invalid("approved_revision_or_clean_tree")
    if (value.get("prompt_revision") != PROMPT_REVISION or value.get("graphs") != ["P", "R"]
            or value.get("episodes_per_graph") != 1 or value.get("calls_per_episode") != 28
            or value.get("combined_spending_ceiling_usd") != 10
            or value.get("reservation_per_episode_usd") != 5
            or value.get("scope") != "fresh unseeded F1 authorization-and-board only"):
        raise Invalid("approval_scope")
    for name in ("index.json", "model-config.proposed.json", "capacity.json"):
        if value.get("review_sha256", {}).get(name) != digest((REVIEW / name).read_bytes()):
            raise Invalid("approval_artifact_changed")
    capacity = strict_json((REVIEW / "capacity.json").read_bytes())
    if not capacity["fits_planning_bound"] or capacity["two_episode_max_estimated_usd"] > 10:
        raise Invalid("approval_capacity_or_budget")
    from .cli import script_spec
    spec, assets = script_spec(graph, "fresh-unseeded-F1-" + graph), Assets()
    empty = {a: [] for a in AGENTS}
    for actor in AGENTS:
        raw = render(spec, assets, actor, "C1", initial(), empty, empty)
        name = f"{graph}-C1-{actor}.json"
        if raw != (REVIEW / name).read_bytes():
            raise Invalid("approved_request_changed")
    return Approval(value, graph)


class BoundedLive:
    scripted = False

    def __init__(self, adapter, spec):
        self.adapter, self.spec = adapter, spec
        self.used = set()
        import threading
        self.lock = threading.Lock()

    def complete(self, request, timeout):
        from .materials import ORDER
        key = (request.slot_nonce, request.session.actor)
        with self.lock:
            if (request.session.namespace != self.spec.namespace or request.session.episode != self.spec.run_id
                    or key[0] not in ORDER or key[1] not in AGENTS or key in self.used or len(self.used) >= 28):
                raise Invalid("live_call_scope_or_duplicate")
            if input_bound(request.input_bytes) > self.spec.input_token_limit:
                raise Invalid("input_capacity_exceeded")
            self.used.add(key)  # reserve before auth/send, including billed failures
        return self.adapter.complete(request, timeout)


def token():
    # ADC token only in process memory; no credential payload/error is archived.
    try:
        result = subprocess.run(["gcloud", "auth", "application-default", "print-access-token"],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                timeout=20, check=True)
        return result.stdout.decode().strip()
    except Exception:
        raise CallError("credential_acquisition_failed") from None


def execute_live(directory, graph, approval_path):
    from .cli import execute, script_spec
    repository = HERE.parents[3]
    approval = validate_approval(approval_path, graph, repository)
    # Exclusive persistent graph claim prevents repeats/resume/replacements and
    # reserves USD5 even for an interrupted run. Never release it automatically.
    # Canonical per-reviewed-revision root: copying/renaming the approval file
    # cannot allocate another budget or another pair of episodes.
    claims = HERE / "live-claims" / approval.record["git_revision"]
    claims.mkdir(parents=True, exist_ok=True)
    if graph == "R":
        from .archive import inspect
        prior = claims / "P.claim"
        if not prior.exists():
            raise Invalid("P_must_complete_before_R")
        _, events = inspect(strict_json(prior.read_bytes())["out"])
        if not any(e["event"] == "F1_complete" for e in events):
            raise Invalid("P_must_complete_before_R")
    spec = script_spec(graph, "fresh-unseeded-F1-" + graph)
    adapter = VertexAdapter.from_file(REVIEW / "model-config.proposed.json", token)
    Path(directory).parent.mkdir(parents=True, exist_ok=True)
    if Path(directory).exists():
        raise Invalid("run_directory_exists")
    with (claims / (graph + ".claim")).open("xb") as stream:
        import os
        stream.write(canonical({"out": str(Path(directory).resolve()), "approval": approval.record,
                                "reserved_usd": 5}))
        stream.flush()
        os.fsync(stream.fileno())
    return execute(directory, spec, trace="unseeded", adapter=BoundedLive(adapter, spec),
                   config=adapter.config, execution_approval=approval)
