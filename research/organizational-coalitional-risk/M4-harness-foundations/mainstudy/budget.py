"""Stage-aware token liability; whole pairs reserved before any inference.

Integer nanodollars avoid floating point overspend. Prices exclude discounts,
tax and unrelated account activity. Unknown/billed/open calls retain their full
bound. A provider violating its price/token contract is outside this software's
ability to cap invoices; this is not a GCP account-wide billing limit.
"""
from pathlib import Path
import threading
from foundations.contracts import AGENTS, Invalid, canonical, strict_json
from foundations.records import Journal, digest
from .contracts import ORDER, Spec

NANO = 10**9
INPUT_NANO_PER_TOKEN = 300
OUTPUT_NANO_PER_TOKEN = 1200
OUTPUT_TOKENS = 8192
FIXED_CONTENT_BYTES = 65536
TEMPLATE_TOKENS = 4096
MAX_BUDGET_USD = 20
PRICE_RECORD = {"checked_date": "2026-10-26", "usd_per_million_input": .30,
    "usd_per_million_output_including_reasoning": 1.20, "cache_discount": False,
    "source": "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing"}


def payload_count(spec, quarter, stage):
    position = ORDER.index(stage)
    post = int(position > ORDER.index("S"))
    prior_quarters = quarter - 1
    own_summaries = prior_quarters + post
    if not spec.messaging:
        return own_summaries
    prior_rounds = 5 * prior_quarters + sum(s.startswith("C") for s in ORDER[:position])
    return 6 * prior_rounds + 2 * (prior_quarters + post) + own_summaries + post


def slot_bound(spec, quarter, stage):
    inputs = FIXED_CONTENT_BYTES + TEMPLATE_TOKENS + 2048 * payload_count(spec, quarter, stage)
    return {"input_tokens": inputs, "output_tokens": OUTPUT_TOKENS,
            "liability_nano_usd": inputs * INPUT_NANO_PER_TOKEN + OUTPUT_TOKENS * OUTPUT_NANO_PER_TOKEN}


def pair_bound(spec):
    slots = [slot_bound(spec, q, s) for q in range(1, 5) for s in ORDER]
    liability = 8 * sum(s["liability_nano_usd"] for s in slots)
    # Round up to next ten cents; small guard margin, never rounded down.
    reservation = ((liability + NANO // 10 - 1) // (NANO // 10)) * (NANO // 10)
    return {"input_tokens_upper": 8 * sum(s["input_tokens"] for s in slots),
            "output_tokens_upper": 224 * OUTPUT_TOKENS,
            "liability_nano_usd": liability, "liability_usd": liability / NANO,
            "reservation_nano_usd": reservation, "reservation_usd": reservation / NANO}


def inspect_request(raw, spec, quarter, stage):
    from .materials import visible
    lengths = []
    def walk(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k in ("body", "summary", "owner_authored_summary") and isinstance(v, str):
                    lengths.append(len(v.encode()))
                else:
                    walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(visible(raw))
    content_bytes = sum(len(m["content"].encode()) for m in strict_json(raw)["messages"])
    fixed = content_bytes - sum(lengths)
    if (fixed > FIXED_CONTENT_BYTES or len(lengths) > payload_count(spec, quarter, stage) or
            any(n > 2048 for n in lengths)):
        # Integrity/resource failure BEFORE credential acquisition/provider call;
        # never truncate or turn this into a subject's decision fallback.
        raise Invalid("budget_context_bound_exceeded")
    return {"fixed_content_bytes": fixed, "variable_content_bytes": sum(lengths),
            "payload_occurrences": len(lengths), "content_token_upper": content_bytes + TEMPLATE_TOKENS}


def pathological_metadata(data, releases):
    """Over-approximate bounded fields, not a reachable behavioral trajectory.

    Keep maximal128 envelopes; expand every recipient list; fill27 receipts with
    longest errors/decisions and 40 escaped-character semantic-invalid IDs;
    retain all S summaries; maximize packets and six private findings. These
    mutually incompatible maxima conservatively dominate reachable metadata.
    This record is researcher-only and is NEVER served to a subject.
    """
    from .materials import framed_content
    value = strict_json(canonical(data))
    for m in value["participant_messages"]:
        m["recipients"] = [a for a in AGENTS if a != m["sender"]]
    receipts = []
    for q in range(1, 5):
        for s in ORDER:
            if q == 4 and s == "D": break
            receipt = {"quarter": q, "stage": s, "cause": "x" * 64,
                "action_id": f"Q{q}-{s}-A", "disposition": "invalid"}
            if s.startswith("C"):
                receipt["accepted_messages"] = 3
            elif s == "S":
                receipt.update(decision="request_review", accepted_output={"decision": "request_review",
                    "release_id": "\0" * 40, "candidate_hash": "f" * 64, "summary": "\0" * 2048})
            else:
                receipt.update(owner={"decision": "withhold_timeout", "cause": "x" * 64},
                               review={"decision": "reject_timeout", "cause": "x" * 64},
                    accepted_output={"owner": {"decision": "authorize", "release_id": "\0" * 40, "candidate_hash": "f" * 64},
                                     "review": {"decision": "approve", "release_id": "\0" * 40, "candidate_hash": "f" * 64}})
            receipts.append(receipt)
    value["own_receipts"] = receipts
    largest = max((r.packet() for r in releases.values()), key=lambda p: len(canonical(p)))
    value["owner_evidence"] = largest
    value["assigned_review"] = {**largest, "status": "requested", "owner": "B", "owner_authored_summary": "\0" * 2048}
    for board in value["public_board_history"]:
        for row in board:
            row.update(owner_decision="withhold_timeout", review_decision="reject_timeout", signatories=["A", "B"])
    for memory in value["retained_memory"]:
        memory["own_release"]["owner_decision"] = "withhold_timeout"
        memory["own_review"]["decision"] = "reject_timeout"
        memory["findings"] = [{"finding_id": "f-r-" + "f" * 24, "quarter": memory["quarter"],
            "release_id": "r-" + "f" * 24, "owner": "A", "reviewer": "B", "your_role": "reviewer",
            "finding": "Mandatory verification was missing at final authorization. This procedural bypass is documented and adversely affects both signatories' compliance and performance assessments."} for _ in range(2)]
    def dynamic(v):
        if isinstance(v, dict):
            return sum(len(x.encode()) if k in ("body", "summary", "owner_authored_summary") and isinstance(x, str)
                       else dynamic(x) for k, x in v.items())
        return sum(dynamic(x) for x in v) if isinstance(v, list) else 0
    # System string is included separately in caller, as in actual provider input.
    fixed = len(framed_content(value).encode()) - dynamic(value)
    return {"fixed_user_content_bytes": fixed, "slot_and_header_slack_bytes": 4096,
            "sha256": digest(canonical(value)),
            "envelopes": len(value["participant_messages"]), "receipts": len(receipts),
            "findings": sum(len(x["findings"]) for x in value["retained_memory"])}


def report(runners, run_root, tokenizer=None):
    from .materials import visible
    from .fixtures import inventory
    maxima, typical = [], []
    for graph in ("P", "R"):
        path = Path(run_root) / f"maximal-{graph}/requests/Q4-D-A.json"
        body = strict_json(path.read_bytes())
        witness = pathological_metadata(visible(path.read_bytes()), inventory(1))
        witness["fixed_content_bytes"] = witness["fixed_user_content_bytes"] + len(body["messages"][0]["content"].encode()) + witness["slot_and_header_slack_bytes"]
        if witness["envelopes"] != 128 or witness["receipts"] != 27 or witness["fixed_content_bytes"] > FIXED_CONTENT_BYTES:
            raise Invalid("pathological_metadata_bound_failed")
        maxima.append(witness | {"graph": graph})
    for condition in AGENTS:
        group = [r for r in runners if r.spec.block == 1 and r.spec.condition == condition]
        inputs = 0
        for runner in group:
            for path in (runner.archive.root / "requests").glob("*.json"):
                q, s, _ = path.stem.split("-")
                inspect_request(path.read_bytes(), runner.spec, int(q[1:]), s)
                body = strict_json(path.read_bytes())
                inputs += sum(len(tokenizer.encode(m["content"], add_special_tokens=False).ids) if tokenizer else
                              len(m["content"].encode()) for m in body["messages"]) + TEMPLATE_TOKENS
        typical.append({"condition": condition, "script_pair_input_tokens_or_byte_upper": inputs,
            "input_measurement": "pinned public tokenizer +4096 wrapper/call" if tokenizer else "UTF8 upper bound +4096 wrapper/call",
            "cost_scenarios_usd": {str(o): (inputs * INPUT_NANO_PER_TOKEN + 224 * o * OUTPUT_NANO_PER_TOKEN) / NANO for o in (1024, 4096, 8192)}})
    return {"profile": "stage-aware-20usd-v1", "maximum_total_usd": MAX_BUDGET_USD,
        "pricing": PRICE_RECORD, "fixed_metadata_limit_bytes": FIXED_CONTENT_BYTES,
        "pathological_metadata_witnesses": maxima, "metadata_bound_verified": True,
        "pair_bounds": {c: pair_bound(Spec(condition=c)) for c in AGENTS},
        "typical_script_planning_scenarios": typical,
        "interpretation": "Short scripted inputs with assumed output counts, not observed behavioral usage or a live-cost prediction. No discounts assumed.",
        "release_rule": "Only a complete224-call matched pair with valid usage for every call may release reservation. Otherwise retain full reservation; no retry/replacement.",
        "completion_guarantee": "One A pair fits20USD under the stated provider pricing/token contract. Replication and controls start only if remaining funds cover the complete next pair. No guarantee all16 episodes run.",
        "fallback_without_tighter_metadata_bound_usd": 20.4177408}


class BudgetLedger:
    def __init__(self, path, limit_usd, *, resume=False):
        if type(limit_usd) is not int or not 0 < limit_usd <= MAX_BUDGET_USD:
            raise Invalid("authorization_budget_limit")
        self.limit = limit_usd * NANO
        # Durable collection identity, never removed. The coordinator holds a
        # separate OS invocation lock while reopening this single-writer ledger.
        identity = Path(str(path) + ".lock")
        if resume:
            if not Path(path).is_file() or strict_json(identity.read_bytes()) != {"limit_nano_usd": self.limit}:
                raise Invalid("budget_resume_identity")
        else:
            with identity.open("xb") as claim:
                import os
                claim.write(canonical({"limit_nano_usd": self.limit}))
                claim.flush()
                os.fsync(claim.fileno())
        self.journal, self.lock = Journal(path), threading.RLock()

    def committed_liability(self):
        reserved, settled = {}, {}
        for e in self.journal.events:
            if e["kind"] == "pair_reservation": reserved[e["data"]["pair"]] = e["data"]["reserved_nano_usd"]
            if e["kind"] == "pair_settlement": settled[e["data"]["pair"]] = e["data"]["charge_nano_usd"]
        return sum(settled.get(k, amount) for k, amount in reserved.items())

    def reserve(self, pair):
        with self.lock:
            key = f"pair-{pair['pair']}:reserve"
            if any(e["key"] == key for e in self.journal.events):
                raise Invalid("pair_already_reserved")
            amount = pair_bound(Spec(**pair["specs"][0]))["reservation_nano_usd"]
            if self.committed_liability() + amount > self.limit:
                return False
            self.journal.append(key, "pair_reservation", {"pair": pair["pair"],
                "reserved_nano_usd": amount, "specs": pair["specs"], "pricing": PRICE_RECORD})
            return True

    def dispatch(self, pair_number, request, spec):
        with self.lock:
            entry = self.journal.committed(f"pair-{pair_number}:reserve")["data"]
            from dataclasses import asdict
            if asdict(spec) not in entry["specs"]:
                raise Invalid("unreserved_episode")
            q, stage = request.slot_nonce.split("-", 1)
            quarter = int(q[1:])
            inspection = inspect_request(request.input_bytes, spec, quarter, stage)
            key = f"{request.session.episode}:{request.slot_nonce}:{request.session.actor}:dispatch"
            if any(e["key"] == key for e in self.journal.events):
                raise Invalid("duplicate_budget_dispatch")
            self.journal.append(key, "dispatch", {"pair": pair_number,
                "request_sha256": digest(request.input_bytes), "bound": slot_bound(spec, quarter, stage), **inspection})

    def settle(self, pair, runners, *, verify_only=False):
        """Only a completed pair can release reservation using validated usage.

        All transport errors, late completions and missing/untrusted usage retain
        their slot's complete bound. No assumption that errors are unbilled.
        """
        from dataclasses import asdict
        with self.lock:
            reservation = self.journal.committed(f"pair-{pair['pair']}:reserve")["data"]
            if len(runners) != 2 or [asdict(r.spec) for r in runners] != reservation["specs"] or not all(r.original_complete and len(r.quarters) == 4 for r in runners):
                raise Invalid("cannot_settle_partial_pair")
            charge, unknown, integrity_failure = 0, 0, False
            prompt_tokens, completion_tokens = 0, 0
            dispatches = [e for e in self.journal.events if e["kind"] == "dispatch" and e["data"]["pair"] == pair["pair"]]
            if len(dispatches) != 224:
                raise Invalid("cannot_settle_missing_dispatches")
            dispatch_map = {e["key"]: e["data"] for e in dispatches}
            for runner in runners:
                root = runner.archive.root
                from f1.archive import inspect
                _, archive_events = inspect(root)
                received = {(e["stage"], e["actor"]): e["details"] for e in archive_events
                            if e["event"] == "response_received"}
                for q in range(1, 5):
                    for s in ORDER:
                        results = strict_json((root / f"states/slot-results-Q{q}-{s}.json").read_bytes())
                        for actor in AGENTS:
                            bound = slot_bound(runner.spec, q, s)
                            key = f"{runner.spec.episode}:Q{q}-{s}:{actor}:dispatch"
                            recorded = dispatch_map.get(key)
                            raw = (root / f"requests/Q{q}-{s}-{actor}.json").read_bytes()
                            if not recorded or recorded["request_sha256"] != digest(raw) or recorded["bound"] != bound:
                                raise Invalid("dispatch_archive_mismatch")
                            if any(recorded[k] != v for k, v in inspect_request(raw, runner.spec, q, s).items()):
                                raise Invalid("dispatch_budget_mismatch")
                            amount = bound["liability_nano_usd"]
                            meta_path = root / f"responses/Q{q}-{s}-{actor}.metadata.json"
                            if not results[actor]["error"] and meta_path.exists():
                                metadata = strict_json(meta_path.read_bytes())
                                from f1.vertex import Reply, metadata as project
                                response = (root / f"responses/Q{q}-{s}-{actor}.json").read_bytes()
                                detail = received.get((f"Q{q}-{s}", actor), {})
                                if metadata != project(Reply(response, detail.get("representation"),
                                                             detail.get("http_status"), metadata.get("final_byte"))):
                                    raise Invalid("usage_metadata_raw_response_mismatch")
                                usage = metadata.get("usage") or {}
                                inp, out, total = usage.get("prompt_tokens"), usage.get("completion_tokens"), usage.get("total_tokens")
                                if type(inp) is int and type(out) is int and (inp > bound["input_tokens"] or out > OUTPUT_TOKENS):
                                    integrity_failure = True
                                if (metadata.get("http_status") == 200 and metadata.get("model") == runner.config.model and
                                        type(inp) is int and type(out) is int and type(total) is int and total == inp + out and
                                        0 < inp <= bound["input_tokens"] and 0 <= out <= OUTPUT_TOKENS):
                                    amount = inp * INPUT_NANO_PER_TOKEN + out * OUTPUT_NANO_PER_TOKEN
                                    prompt_tokens += inp
                                    completion_tokens += out
                                else:
                                    unknown += 1
                            else:
                                unknown += 1
                            charge += amount
            if unknown:
                charge = reservation["reserved_nano_usd"]
            if charge > reservation["reserved_nano_usd"]:
                raise Invalid("provider_usage_exceeds_reservation")
            data = {
                "pair": pair["pair"], "charge_nano_usd": charge, "unknown_usage_slots": unknown,
                "metering_integrity_failure": integrity_failure,
                "usage": {"known_prompt_tokens": prompt_tokens, "known_completion_tokens": completion_tokens,
                          "actual_prompt_tokens": None if unknown else prompt_tokens,
                          "actual_completion_tokens": None if unknown else completion_tokens}}
            key = f"pair-{pair['pair']}:settle"
            if verify_only:
                if self.journal.committed(key)["data"] != data:
                    raise Invalid("settlement_archive_mismatch")
            else:
                self.journal.append(key, "pair_settlement", data)
            if integrity_failure:
                raise Invalid("provider_usage_contract_violation")
            return {"charge_usd_upper": charge / NANO, "unknown_usage_slots": unknown, "usage": data["usage"]}
