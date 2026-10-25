"""Frozen visible assets, separate from researcher truth and annotations."""
from dataclasses import dataclass
from pathlib import Path
import re

from foundations.contracts import AGENTS, P, R, Binding, Limits, canonical, named_schema, strict_json
from foundations.records import digest

HERE = Path(__file__).parent
MATERIALS = HERE / "materials"
SOURCE = "16ba7b05cea8b2b4d23e2e445702a0386c3b55c79f056a2ac5c56cfbe8f7fe0e"
ORDER = ("C1", "C2", "O", "C3", "C4", "C5", "R")
WATERMARK = dict(zip(ORDER, (0, 1, 2, 2, 3, 4, 5)))
NAMES = ("system.txt", "policy.txt", "context.txt", "role.txt", "message-rules.txt",
         "communication.txt", "owner-slot.txt", "review-slot.txt", "technical-context.md",
         "case-c5b-release-record.md")
GENERATION_FIELDS = {"temperature", "topP", "topK", "seed", "maxOutputTokens",
                     "thinkingConfig", "responseMimeType", "candidateCount"}


@dataclass(frozen=True)
class Spec:
    run_id: str
    graph: str
    namespace: str
    generation_json: bytes
    timeout_seconds: float
    input_token_limit: int
    output_token_limit: int
    limits: Limits

    def __post_init__(self):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", self.run_id):
            raise ValueError("run_id")
        if self.graph not in {"P", "R"} or not self.namespace:
            raise ValueError("run_identity")
        generation = strict_json(self.generation_json)
        if (set(generation) - GENERATION_FIELDS or generation.get("responseMimeType") != "application/json"
                or generation.get("candidateCount") != 1 or self.timeout_seconds <= 0
                or self.input_token_limit <= 0 or self.output_token_limit <= 0
                or generation.get("maxOutputTokens") != self.output_token_limit):
            raise ValueError("generation_contract")

    @property
    def reviewers(self):
        return P if self.graph == "P" else R


class Assets:
    def __init__(self):
        self.texts = {name: (MATERIALS / name).read_text() for name in NAMES}
        inventory = strict_json((HERE / "material-provenance.json").read_bytes())
        actual = [[name, digest((MATERIALS / "source" / name).read_bytes())]
                  for name, _ in inventory["source_inventory"]]
        if actual != inventory["source_inventory"] or digest(canonical(actual)) != SOURCE:
            raise ValueError("source_integrity")
        # Ordinary test source is visible; no hidden security tests/results served.
        attachments = {name: (MATERIALS / "source" / name).read_text()
                       for name, _ in actual if name.startswith("tests/") or name == "LICENSE"}
        self.evidence = {"record": self.texts["case-c5b-release-record.md"],
                         "technical_context": self.texts["technical-context.md"],
                         "attachments": attachments}
        self.evidence_hash = digest(canonical(self.evidence))
        self.hashes = {str(path.relative_to(HERE)): digest(path.read_bytes())
                       for path in sorted(MATERIALS.rglob("*")) if path.is_file()}

    def binding(self, spec, actor):
        return Binding(spec.run_id, 1, actor, f"release-{actor}", SOURCE, None, self.evidence_hash)


def substitute(text, values):
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    if "{{" in text or "}}" in text:
        raise ValueError("unresolved_template")
    return text


def render(spec, assets, actor, stage, state, history, receipts):
    """Exact Vertex-compatible request BODY, before any adapter/authentication."""
    index = AGENTS.index(actor)
    reviewed = AGENTS[spec.reviewers.index(actor)]
    binding = assets.binding(spec, actor)
    values = {"agent_id": actor, "owned_service_id": "service-" + actor,
              "owned_release_id": binding.release_id, "owned_candidate_hash": SOURCE,
              "reviewed_service_id": "service-" + reviewed, "reviewed_release_id": "release-" + reviewed,
              "own_reviewer_id": spec.reviewers[index]}
    assigned = None
    if stage in {"C3", "C4", "C5", "R"}:
        target = state[reviewed]
        assigned = {"status": "not_submitted"}
        if target["owner_decision"] == "submit":
            assigned = {"status": "submitted", "release_id": "release-" + reviewed,
                        "candidate_hash": SOURCE, "build_hash": None,
                        "evidence_hash": assets.evidence_hash, "independent_evidence": assets.evidence,
                        "owner_authored_summary": target["summary"]}
    slot = {"actor": actor, "phase": stage, "limits": {
        "input_tokens": spec.input_token_limit, "output_tokens": spec.output_token_limit,
        "elapsed_seconds": spec.timeout_seconds}}
    if stage.startswith("C"):
        number = int(stage[1:])
        slot.update(round=number, output_schema=named_schema("CommunicationBatch"),
                    instruction=substitute(assets.texts["communication.txt"], {"round": number}))
    else:
        slot.update(output_schema=named_schema("OwnerDecision" if stage == "O" else "ReviewSlotOutput"),
                    instruction=assets.texts["owner-slot.txt" if stage == "O" else "review-slot.txt"],
                    allowed_release_id="release-" + (actor if stage == "O" else reviewed),
                    allowed_candidate_hash=SOURCE)
    visible = {"company_policy": assets.texts["policy.txt"], "release_window": assets.texts["context.txt"],
               "role_record": substitute(assets.texts["role.txt"], values),
               "organization_chart": [{"owner": a, "service_id": "service-" + a,
                   "current_release_id": "release-" + a, "assigned_reviewer": spec.reviewers[i]}
                  for i, a in enumerate(AGENTS)],
               "interaction_rules": assets.texts["message-rules.txt"], "owner_evidence": assets.evidence,
               "assigned_review": assigned, "own_receipts": receipts[actor],
               "participant_messages": history[actor], "slot": slot}
    # Insertion order is part of the literal rendering recipe.
    import json
    user = json.dumps(visible, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    request = {"systemInstruction": {"parts": [{"text": assets.texts["system.txt"]}]},
               "contents": [{"role": "user", "parts": [{"text": user}]}],
               "generationConfig": strict_json(spec.generation_json)}
    raw = json.dumps(request, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
    validate_visible(raw)
    return raw


def validate_visible(raw):
    request = strict_json(raw)
    if set(request) != {"systemInstruction", "contents", "generationConfig"}:
        raise ValueError("request_fields")
    if len(request["contents"]) != 1 or request["contents"][0]["role"] != "user":
        raise ValueError("request_roles")
    visible = strict_json(request["contents"][0]["parts"][0]["text"].encode())
    if set(visible) != {"company_policy", "release_window", "role_record", "organization_chart",
                        "interaction_rules", "owner_evidence", "assigned_review", "own_receipts",
                        "participant_messages", "slot"}:
        raise ValueError("visible_fields")
    return visible
