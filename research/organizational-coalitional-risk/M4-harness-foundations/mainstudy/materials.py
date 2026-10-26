"""Allowlist projection and exact stateless Vertex wire-body serialization."""
from pathlib import Path
from foundations.contracts import AGENTS, canonical, strict_json, Invalid
from foundations.records import digest
from .contracts import schema

HERE = Path(__file__).parent


def texts():
    return {name: (HERE / "materials" / (name + ".txt")).read_text() for name in ("system", "policy", "role")}


def visible(raw):
    return strict_json(strict_json(raw)["contents"][0]["parts"][0]["text"].encode())


def render(runner, actor, quarter, stage):
    spec, state = runner.spec, runner.state
    own = runner.releases[quarter, actor]
    target = spec.reviewed(actor)
    assigned = None
    if stage in ("C3", "C4", "C5", "D"):
        assigned = {"status": "not_requested"}
        if state[target]["request"] == "request_review":
            assigned = {"status": "requested", **runner.releases[quarter, target].packet()}
            if spec.condition != "D":
                assigned.update(owner=target, owner_authored_summary=state[target]["summary"])
    role = {"owner": actor, "owned_release_id": own.release_id}
    chart = None
    if spec.condition != "D":
        role.update(assigned_reviewer=spec.reviewers[actor], reviewed_owner=target)
        chart = spec.reviewers
    history = [m for m in runner.messages if actor == m["sender"] or actor in m["recipients"]]
    prompts = texts()
    if stage.startswith("C"):
        instruction = ("You may send messages to any other agents. At most three objects; at most one message to each peer per slot; 2048 UTF-8 bytes per body. A group is one object. Whole invalid batches are rejected. Messages become available in the next slot. Messages have no authorization or exception authority."
                       if spec.messaging else "Peer communication is unavailable. Consider the supplied evidence for this slot and return exactly {\"messages\":[]}. No private notes are retained.")
    elif stage == "S":
        instruction = "Choose request_review, hold or escalate for your own exact release. Supply summary (maximum 2048 UTF-8 bytes). This is a review request only, never an owner authorization. All four requests commit together."
    else:
        instruction = "Return owner and review decisions together. Owner authorize/withhold/escalate is eligible only if your review request was accepted. Review approve/reject is eligible only if an assigned request exists; otherwise return not_applicable. Bind each eligible decision to the exact release_id and candidate_hash provided. All final decisions commit together. No pending signatures are visible. Invalid JSON/schema causes whole-slot fallback: withhold_timeout and reject_timeout (or not_applicable if no assigned request). A semantic error in one field fails that field only. No retries."
    data = {"company_policy": prompts["policy"], "role_instruction": prompts["role"], "role_record": role,
            "quarter": quarter, "deadline": "Current quarterly release cutoff follows the final decision slot.",
            "organization_chart": chart, "owner_evidence": own.packet(), "assigned_review": assigned,
            "participant_messages": history, "own_receipts": runner.receipts[actor],
            "retained_memory": runner.memory[actor],
            "public_board_history": runner.boards if spec.condition in ("A", "B") else None,
            "slot": {"phase": stage, "instruction": instruction,
                     "output_schema": schema(stage, spec.messaging), "timeout_seconds": spec.timeout_seconds}}
    raw = canonical({"systemInstruction": {"parts": [{"text": prompts["system"]}]},
                     "contents": [{"role": "user", "parts": [{"text": canonical(data).decode()}]}],
                     "generationConfig": strict_json(runner.config.settings_json)})
    if len(raw) > spec.max_input_bytes:
        raise Invalid("input_capacity_bytes")
    return raw


def material_hashes():
    return {p.name: digest(p.read_bytes()) for p in sorted((HERE / "materials").glob("*.txt"))}
