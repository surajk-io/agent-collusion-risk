"""One new matched pair per invocation; resume only a verified paused prefix.

There is deliberately no within-episode recovery or call resampling. A crashed,
partial, corrupt or unmetered pair permanently blocks automatic continuation.
"""
from contextlib import contextmanager
from pathlib import Path
import fcntl
import subprocess
import tempfile
from types import SimpleNamespace

from foundations.contracts import Invalid, canonical, strict_json
from foundations.records import digest
from f1.archive import durable, inspect
from .budget import BudgetLedger, NANO
from .contracts import Spec, GENERATION
from .materials import material_hashes
from .preflight import allocation

MODE = "one-pair-per-invocation-v1"


def claims_directory(repository, revision):
    # Managed Git worktrees must share claims; HERE would allocate a fresh
    # ledger in every checkout of the same approved revision.
    common = subprocess.check_output(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                     cwd=repository, text=True).strip()
    return Path(common).resolve() / "mainstudy-collections" / revision


@contextmanager
def invocation_lock(path):
    # OS releases ownership on process exit/crash; the file and collection
    # identity persist. No stale-lock deletion or force-unlock recovery path.
    with Path(path).open("a+b") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Invalid("collection_invocation_busy") from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def resume_proposal():
    return {"status": "PROPOSED_NOT_AUTHORIZED", "researcher_approval_reference": None,
        "execution_mode": MODE, "git_revision": "COPY_ORIGINAL_REVIEWED_REVISION",
        "package_sha256": "COPY_ORIGINAL_PACKAGE_SHA256",
        "collection_approval_sha256": "COPY_ORIGINAL_APPROVAL_SHA256",
        "collection_root": "COPY_ORIGINAL_ABSOLUTE_COLLECTION_PATH",
        "prior_ledger_head_sha256": "COPY_LAST_PAUSED_RECEIPT_LEDGER_HASH",
        "next_pair": 2}


def archive_check(path, spec, approval):
    from .replay import replay
    frozen, events = inspect(path)
    if (frozen["spec"] != spec or frozen["model"]["provider"] != approval["provider_config"]["provider"] or
            frozen["model"]["endpoint"] != approval["provider_config"]["endpoint"] or
            frozen["model"]["model"] != approval["provider_config"]["model"] or
            frozen["model"]["settings_json"] != approval["provider_config"]["generation_config"] or
            frozen.get("execution_approval") != approval or not frozen.get("live_execution_authorized") or
            frozen["provenance"]["git_revision"] != approval["git_revision"] or
            frozen["materials"] != material_hashes() or
            sum(e["event"] == "mainstudy_complete" for e in events) != 1):
        raise Invalid("completed_archive_identity_or_completion")
    from .fixtures import inventory
    for (quarter, actor), release in inventory(spec["block"]).items():
        stored = frozen["releases"][f"{quarter}-{actor}"]
        if (stored["candidate_hash"] != release.candidate_hash or
                stored["source_json"] != strict_json(release.source_json) or
                stored["evidence_json"] != strict_json(release.evidence_json)):
            raise Invalid("completed_archive_case_changed")
    indexed = {n for e in events for n in e["files"]} | {"events.jsonl"}
    actual = {str(p.relative_to(path)) for p in Path(path).rglob("*") if p.is_file()}
    if actual != indexed:
        raise Invalid("unindexed_archive_artifact")
    # Existing replay checks every retained request and deterministic commit.
    # This never dispatches a behavioral/provider call.
    with tempfile.TemporaryDirectory() as temporary:
        runner = replay(path, Path(temporary) / "verification")
    runner.archive = SimpleNamespace(root=Path(path))
    return runner, {"path": str(Path(path).resolve()), "manifest_sha256": digest((Path(path) / "manifest.json").read_bytes()),
                    "event_head_sha256": events[-1]["hash"], "event_count": len(events),
                    "integrity": "hash_chain_and_exact_replay_verified"}


def validate_prefix(budget, root, claims, approval):
    events = budget.journal.events
    completed = [e for e in events if e["kind"] == "pair_complete"]
    reserved = [e["data"]["pair"] for e in events if e["kind"] == "pair_reservation"]
    count = len(completed)
    if (reserved != list(range(1, count + 1)) or
            [e["data"]["pair"] for e in completed] != reserved or
            any(e["kind"] == "pair_blocked" for e in events)):
        raise Invalid("partial_or_unresolved_pair_blocks_resume")
    expected_claims = {f"pair-{i}.json" for i in reserved}
    if {p.name for p in claims.glob("pair-*.json")} != expected_claims:
        raise Invalid("duplicate_or_orphan_pair_claim")
    expected_root = {f"pair-{i:03d}-receipt.json" for i in reserved}
    for i, completed_event in enumerate(completed, 1):
        pair = allocation()[i - 1]
        claim = strict_json((claims / f"pair-{i}.json").read_bytes())
        expected = {"pair": pair, "approval": approval, "reserved_usd": pair["reservation_usd"], "out": str(root)}
        if claim != expected:
            raise Invalid("pair_claim_changed")
        runners, archives = [], []
        for spec in pair["specs"]:
            path = root / Spec(**spec).episode
            expected_root.add(path.name)
            runner, check = archive_check(path, spec, approval)
            runners.append(runner); archives.append(check)
        settlement = budget.settle(pair, runners, verify_only=True)
        data = completed_event["data"]
        if settlement["unknown_usage_slots"] or data["archives"] != archives or data["settlement"] != settlement:
            raise Invalid("unresolved_usage_or_checkpoint_changed")
        receipt = strict_json((root / f"pair-{i:03d}-receipt.json").read_bytes())
        if receipt != data | {"ledger_head_sha256": completed_event["hash"]}:
            raise Invalid("pair_receipt_changed")
    if {p.name for p in root.iterdir()} != expected_root:
        raise Invalid("unexpected_collection_path_or_replacement")
    if count and events[-1]["kind"] != "pair_complete":
        raise Invalid("unresolved_collection_tail")
    return count


def run_one_pair(directory, claims, approval, adapter, *, resume_authorization=None):
    from .live import BoundedLive, claim_pair
    from .runner import execute
    from .annotation import template, outcomes
    value, root, claims = approval.record, Path(directory).resolve(), Path(claims)
    if (value.get("execution_mode") != MODE or value.get("collection_root") != str(root) or
            canonical(value["provider_config"]["generation_config"]) != GENERATION):
        raise Invalid("collection_execution_mode_or_configuration")
    claims.mkdir(parents=True, exist_ok=True)
    with invocation_lock(claims / "invocation.lock"):
        resuming = resume_authorization is not None
        if not resuming:
            if root.exists():
                raise Invalid("collection_output_exists")
            if any(claims.glob("pair-*.json")) or (claims / "budget.json").exists() or (claims / "budget.json.lock").exists():
                raise Invalid("collection_already_initialized")
            # Do not create a persistent budget identity on an invalid --out.
            root.mkdir(parents=True, exist_ok=False)
        budget = BudgetLedger(claims / "budget.json", value["maximum_budget_usd"], resume=resuming)
        identity = {"execution_mode": MODE, "approval": value,
                    "approval_sha256": digest(canonical(value)), "collection_root": str(root),
                    "claims_root": str(claims.resolve())}
        if resuming:
            if budget.journal.committed("collection")["data"] != identity:
                raise Invalid("incompatible_collection_approval_or_root")
            count = validate_prefix(budget, root, claims, value)
            if not count:
                raise Invalid("no_completed_pair_to_resume")
            head = budget.journal.events[-1]["hash"]
            a = resume_authorization
            expected_fields = set(resume_proposal())
            if (set(a) != expected_fields or a.get("status") != "explicitly_authorized" or
                    not a.get("researcher_approval_reference") or a.get("execution_mode") != MODE or
                    a.get("git_revision") != value["git_revision"] or a.get("package_sha256") != value["package_sha256"] or
                    a.get("collection_approval_sha256") != identity["approval_sha256"] or
                    a.get("collection_root") != str(root) or a.get("prior_ledger_head_sha256") != head or
                    type(a.get("next_pair")) is not int or a["next_pair"] != count + 1):
                raise Invalid("explicit_resume_authorization_required_or_stale")
        else:
            budget.journal.append("collection", "collection_identity", identity)
            count = 0
        if count >= value["max_pairs"]:
            raise Invalid("authorized_collection_complete")
        from datetime import datetime, timezone
        if datetime.now(timezone.utc) >= datetime.fromisoformat(value["stop_new_pairs_at"]):
            raise Invalid("frozen_pair_start_cutoff")
        pair = allocation()[count]
        # Check all paths before reserving/sending. No overwrite/replacement.
        if (claims / f"pair-{pair['pair']}.json").exists() or any((root / Spec(**s).episode).exists() for s in pair["specs"]):
            raise Invalid("duplicate_pair_paths")
        if not budget.reserve(pair):
            raise Invalid("insufficient_whole_pair_budget")
        if resuming:
            budget.journal.append(f"pair-{pair['pair']}:resume", "resume_authorization", resume_authorization)
        claim_pair(claims / f"pair-{pair['pair']}.json", pair, approval, root)
        for spec_data in pair["specs"]:
            spec = Spec(**spec_data)
            runner = execute(root / spec.episode, spec, BoundedLive(adapter, spec, budget, pair["pair"]), "unseeded",
                             config=adapter.config, execution_approval=approval)
            runner.archive.state("annotation-template", template(runner), "ANNOTATION")
            runner.archive.state("outcomes", outcomes(runner), "ANALYSIS")
        # Re-open both original archives; integrity/replay and ledger/input/usage
        # links are checked before settlement or permission for another pair.
        runners, archives = [], []
        for spec_data in pair["specs"]:
            runner, check = archive_check(root / Spec(**spec_data).episode, spec_data, value)
            runners.append(runner); archives.append(check)
        settlement = budget.settle(pair, runners)
        committed = budget.committed_liability()
        next_pair = pair["pair"] + 1
        data = {"execution_mode": MODE, "pair": pair["pair"], "collection_root": str(root),
            "collection_approval_sha256": identity["approval_sha256"], "package_sha256": value["package_sha256"],
            "git_revision": value["git_revision"], "archives": archives, "settlement": settlement,
            "budget": {"limit_usd": budget.limit / NANO, "committed_liability_usd": committed / NANO,
                       "remaining_authorization_usd": (budget.limit - committed) / NANO,
                       "unresolved_reserved_usd": pair["reservation_usd"] if settlement["unknown_usage_slots"] else 0,
                       "next_pair_reservation_usd": allocation()[next_pair - 1]["reservation_usd"] if next_pair <= value["max_pairs"] else None,
                       "can_reserve_next_pair": not settlement["unknown_usage_slots"] and next_pair <= value["max_pairs"] and
                           committed + round(allocation()[next_pair - 1]["reservation_usd"] * NANO) <= budget.limit},
            "next_pair": next_pair if not settlement["unknown_usage_slots"] and next_pair <= value["max_pairs"] else None,
            "status": "blocked_unresolved_usage" if settlement["unknown_usage_slots"] else
                      "paused_requires_explicit_resume" if next_pair <= value["max_pairs"] else "collection_complete"}
        kind = "pair_blocked" if settlement["unknown_usage_slots"] else "pair_complete"
        event = budget.journal.append(f"pair-{pair['pair']}:checkpoint", kind, data)
        receipt = data | {"ledger_head_sha256": event["hash"]}
        path = root / f"pair-{pair['pair']:03d}-receipt.json"
        if path.exists():
            raise Invalid("pair_receipt_exists")
        durable(path, canonical(receipt))
        return receipt
