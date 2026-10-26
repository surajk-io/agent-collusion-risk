"""Dormant pair-reserved live path. No authorized manifest is shipped.

Current packaged capacity proof fails: validation stops before credentials.
Only researcher-approved proof/configuration can open this execution path.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import threading
import time
from foundations.contracts import AGENTS, Invalid, canonical, strict_json
from foundations.provider import ModelConfig
from foundations.records import digest
from f1.live import token
from f1.vertex import VertexAdapter, CallError
from .contracts import Spec, ORDER, GENERATION
from .materials import HERE, visible, material_hashes
from .preflight import allocation, CONTEXT_LIMIT, OUTPUT_TOKENS, PAIR_RESERVATION_USD


@dataclass(frozen=True)
class LaunchApproval:
    record: dict


def validate_approval(package, approval, repository):
    package = Path(package)
    value = strict_json(Path(approval).read_bytes())
    if value.get("status") != "explicitly_authorized" or not value.get("researcher_approval_reference"):
        raise Invalid("live_execution_not_authorized")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository).decode().strip()
    if value.get("git_revision") != head or subprocess.check_output(["git", "status", "--porcelain"], cwd=repository):
        raise Invalid("approved_revision_or_clean_tree")
    index = strict_json((package / "index.json").read_bytes())
    if value.get("package_sha256") != digest(canonical(index)):
        raise Invalid("approved_package_changed")
    for name, expected in index.items():
        path = (package / name).resolve()
        if not path.is_relative_to(package.resolve()) or digest(path.read_bytes()) != expected:
            raise Invalid("approved_artifact_changed")
    capacity_raw = (package / "capacity.json").read_bytes()
    capacity = strict_json(capacity_raw)
    if (not value.get("capacity_proven") or not capacity.get("capacity_proven") or
            value.get("capacity_proof_sha256") != digest(capacity_raw) or
            capacity["planning_token_upper_bound"] + OUTPUT_TOKENS > CONTEXT_LIMIT):
        raise Invalid("unverified_maximal_context_capacity")
    if (not value.get("approved_prompts_and_fixtures") or value.get("calls_per_episode") != 112 or
            value.get("max_pairs") not in range(1, 9) or
            value.get("max_calls") != value["max_pairs"] * 224 or
            value.get("reservation_per_pair_usd") != PAIR_RESERVATION_USD or
            value.get("maximum_budget_usd", 0) < value["max_pairs"] * PAIR_RESERVATION_USD or
            value.get("maximum_budget_usd", 601) > 600 or value.get("no_retries_or_replacements") is not True):
        raise Invalid("approval_scope_or_budget")
    try:
        stop = datetime.fromisoformat(value["stop_new_pairs_at"])
        if stop.tzinfo is None or stop <= datetime.now(timezone.utc):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        raise Invalid("approval_stop_time") from None
    if strict_json((package / "allocation.json").read_bytes()) != allocation():
        raise Invalid("allocation_changed")
    proposed = strict_json((package / "execution-approval.proposed.json").read_bytes())
    if value["provider_config"] != proposed["provider_config"]:
        raise Invalid("approved_provider_changed")
    # Detect changed prompts/source/evidence even if somebody copies an old index.
    sample = visible((package / "A-P-Q1-C1-A.json").read_bytes())
    from .materials import texts
    if sample["company_policy"] != texts()["policy"] or sample["role_instruction"] != texts()["role"]:
        raise Invalid("approved_prompts_changed")
    return LaunchApproval(value)


class MainAdapter(VertexAdapter):
    """Same frozen DeepSeek MaaS HTTP/credential boundary as successful F1."""
    def complete(self, request, timeout):
        body = strict_json(request.input_bytes)
        if request.config != self.config:
            raise CallError("config_changed")
        if (body.get("model") != self.config.model or set(body) != {"model", "messages"} | set(strict_json(self.config.settings_json)) or
                {k: body[k] for k in strict_json(self.config.settings_json)} != strict_json(self.config.settings_json)):
            raise CallError("settings_changed")
        if [m.get("role") for m in body["messages"]] != ["system", "user"]:
            raise CallError("request_roles")
        visible(request.input_bytes)
        start = time.monotonic()
        try:
            bearer = self._token()
        except Exception:
            raise CallError("credential_acquisition_failed") from None
        remaining = timeout - (time.monotonic() - start)
        if remaining <= 0:
            raise CallError("credential_timeout")
        return self._transport(self.config.endpoint, request.input_bytes, bearer, remaining)


class BoundedLive:
    scripted = False

    def __init__(self, adapter, spec):
        self.adapter, self.spec = adapter, spec
        self.used, self.lock = set(), threading.Lock()

    def complete(self, request, timeout):
        key = request.slot_nonce, request.session.actor
        valid_slots = {f"Q{q}-{s}" for q in range(1, 5) for s in ORDER}
        with self.lock:
            if (request.session.episode != self.spec.episode or request.session.namespace != self.spec.namespace or
                    key[0] not in valid_slots or key[1] not in AGENTS or key in self.used or len(self.used) >= 112):
                raise Invalid("live_call_scope_or_duplicate")
            body = strict_json(request.input_bytes)
            bound = sum(len(m["content"].encode()) for m in body["messages"]) + 4096
            if len(request.input_bytes) > self.spec.max_input_bytes or bound + OUTPUT_TOKENS > CONTEXT_LIMIT:
                raise Invalid("input_capacity_exceeded")
            self.used.add(key)  # includes unsuccessful/billed/open dispatches
        return self.adapter.complete(request, timeout)


def claim_pair(path, pair, approval, out):
    # Exclusive persistent claim reserves BOTH episodes before either auth/send.
    # Never released after interruption; copying approval cannot add replacements.
    with Path(path).open("xb") as stream:
        stream.write(canonical({"pair": pair, "approval": approval.record,
                                "reserved_usd": PAIR_RESERVATION_USD, "out": str(Path(out).resolve())}))
        stream.flush()
        os.fsync(stream.fileno())


def execute_live(directory, package, approval_path):
    from .runner import execute
    from .annotation import template, outcomes
    approval = validate_approval(package, approval_path, HERE.parents[3])
    value = approval.record
    config_value = value["provider_config"]
    config = ModelConfig(config_value["provider"], config_value["endpoint"], config_value["model"], canonical(config_value["generation_config"]))
    if config.settings_json != GENERATION:
        raise Invalid("frozen_generation_changed")
    adapter = MainAdapter(config, token)
    claims = HERE / "live-claims" / value["git_revision"]
    claims.mkdir(parents=True, exist_ok=True)
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    for pair in allocation()[:value["max_pairs"]]:
        if datetime.now(timezone.utc) >= datetime.fromisoformat(value["stop_new_pairs_at"]):
            break
        claim_pair(claims / f"pair-{pair['pair']}.json", pair, approval, root)
        # A partial/error episode is retained; abort the whole collection on
        # integrity failure. Never silently replace or skip an assigned cell.
        for spec_value in pair["specs"]:
            spec = Spec(**spec_value)
            runner = execute(root / spec.episode, spec, BoundedLive(adapter, spec), "unseeded",
                             config=config, execution_approval=approval)
            runner.archive.state("annotation-template", template(runner), "ANNOTATION")
            runner.archive.state("outcomes", outcomes(runner), "ANALYSIS")
