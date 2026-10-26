"""Offline request freeze, visible-content comparison and capacity audit."""
import difflib
import json
from pathlib import Path

from foundations.contracts import AGENTS, canonical, communication
from foundations.records import digest
from .materials import Assets, HERE, MODEL, ORDER, WATERMARK, render
from .runner import initial

TEMPLATE_ALLOWANCE = 4096


def input_bound(raw):
    """Conservative byte/token planning bound, NOT provider tokenizer counting."""
    return len(raw) + TEMPLATE_ALLOWANCE


def proposal_config():
    from .cli import script_spec
    return {"provider": "gcp-model-garden", "model": MODEL,
            "endpoint": "https://aiplatform.googleapis.com/v1/projects/true-ion-507212-g5/locations/global/endpoints/openapi/chat/completions",
            "generation_config": json.loads(script_spec("P").generation_json)}


def maximal_contexts(spec, assets):
    """Synthetic adversarial size witnesses, never future actor histories.

    Six participant envelopes per round: 3 private outgoing + 3 incoming.
    NUL maximizes JSON expansion among legal one-byte characters. Both summaries
    and all own receipts are maximal. Fixed extra slack covers group recipient
    lists and reachable receipt variants. No histories or evidence are truncated.
    """
    state = initial()
    for a in AGENTS:
        state[a].update(owner_decision="submit", summary="\0" * spec.limits.summary_bytes)
    rows = []
    for stage in ORDER:
        history, receipts = {a: [] for a in AGENTS}, {a: [] for a in AGENTS}
        for actor in AGENTS:
            peers = [a for a in AGENTS if a != actor]
            for round_ in range(1, WATERMARK[stage] + 1):
                for sender, recipients in [(actor, [p]) for p in peers] + [(p, [actor]) for p in peers]:
                    body = "\0" * spec.limits.body_bytes
                    communication(canonical({"messages": [{"recipients": recipients, "body": body}]}),
                                  sender, spec.limits)
                    history[actor].append({"message_id": "m-" + "f" * 24,
                        "episode_id": spec.run_id, "quarter": 1, "round": round_,
                        "sender": sender, "recipients": recipients, "body": body})
            for previous in ORDER[:ORDER.index(stage)]:
                receipt = {"phase": previous, "disposition": "invalid", "cause": "overlapping_recipients"}
                if previous.startswith("C"):
                    receipt["accepted_messages"] = 3
                elif previous == "O":
                    receipt.update(decision="submit", release_id="release-" + actor,
                        candidate_hash=assets.binding(spec, actor).candidate_hash,
                        summary="\0" * spec.limits.summary_bytes)
                receipts[actor].append(receipt)
            raw = render(spec, assets, actor, stage, state, history, receipts)
            # <= 30 envelopes, at most 2 extra recipients each (under 300 bytes),
            # <= 6 receipts. 4096 bytes covers all fixed record variants.
            byte_bound = len(raw) + 4096
            rows.append({"graph": spec.graph, "actor": actor, "stage": stage,
                         "witness_request_bytes": len(raw), "serialized_byte_upper_bound": byte_bound,
                         "planning_input_tokens": byte_bound + TEMPLATE_ALLOWANCE,
                         "sha256": digest(raw)})
    return rows


def visible_text(raw):
    request = json.loads(raw)
    if "messages" in request:
        system = request["messages"][0]["content"]
        user = request["messages"][1]["content"]
    else:
        system = request["systemInstruction"]["parts"][0]["text"]
        user = request["contents"][0]["parts"][0]["text"]
    return system + "\n" + json.dumps(json.loads(user), ensure_ascii=False, indent=2) + "\n"


def generate(directory):
    from .cli import script_spec
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    assets, state = Assets(), initial()
    empty = {a: [] for a in AGENTS}
    index = {"status": "PROPOSED F1-prompt-v2 / DeepSeek config; no live authorization", "requests": {}}
    all_rows = []
    for graph in ("P", "R"):
        spec = script_spec(graph, namespace="unseeded-review")
        all_rows.extend(maximal_contexts(spec, assets))
        for actor in AGENTS:
            name = f"{graph}-C1-{actor}.json"
            raw = render(spec, assets, actor, "C1", state, empty, empty)
            (root / name).write_bytes(raw)
            index["requests"][name] = digest(raw)
            old = (HERE / "review-requests" / name).read_bytes()
            diff = "".join(difflib.unified_diff(visible_text(old).splitlines(True),
                visible_text(raw).splitlines(True), fromfile="frozen-v1/" + name, tofile="proposed-v2/" + name))
            (root / (name + ".agent-visible.diff")).write_text(diff)
    (root / "index.json").write_bytes(canonical(index))
    summary = {"method": "adversarial legal size witnesses + structural slack; UTF-8 byte/token planning bound, not provider tokenizer measurement",
               "template_allowance": TEMPLATE_ALLOWANCE, "rows": all_rows,
               "max_request_byte_bound": max(r["serialized_byte_upper_bound"] for r in all_rows),
               "max_planning_input_tokens": max(r["planning_input_tokens"] for r in all_rows),
               "input_ceiling": script_spec("P").input_token_limit,
               "provider_context_limit": 1048576, "generation_ceiling": 8192}
    summary["fits_planning_bound"] = summary["max_planning_input_tokens"] <= summary["input_ceiling"]
    summary["fits_provider_context"] = summary["input_ceiling"] + 8192 <= 1048576
    summary["two_episode_reserved_usage"] = {"calls": 56, "input_tokens": 56 * summary["input_ceiling"],
                                           "completion_tokens_including_reasoning": 56 * 8192}
    summary["two_episode_max_estimated_usd"] = (56 * summary["input_ceiling"] * .30 + 56 * 8192 * 1.20) / 1e6
    summary["pricing"] = {"checked_date": "2026-10-26", "usd_per_million_input": .30,
        "usd_per_million_output_including_reasoning": 1.20, "cache_discount_assumed": False,
        "source": "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing",
        "limit_source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/deepseek/deepseek-v41-flash?hl=en"}
    summary["limitation"] = "Planning/reservation under stated token and price assumptions; no exact MaaS tokenizer measurement or hard provider billing cap"
    (root / "capacity.json").write_bytes(canonical(summary))
    (root / "model-config.proposed.json").write_bytes(canonical(proposal_config()))
    if not summary["fits_planning_bound"] or not summary["fits_provider_context"]:
        raise ValueError("capacity_preflight_failed")
    return summary
