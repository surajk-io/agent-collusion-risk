"""Named candidate schemas plus explicit, provisional permission checks."""
import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

AGENTS = ("A", "B", "C", "D")
P = ("B", "A", "D", "C")  # owner -> reviewer, aligned with AGENTS
R = ("B", "C", "D", "A")
SLOT_ORDER_REFERENCE = ("C1", "C2", "O", "C3", "C4", "C5", "R")
SCHEMAS = json.loads((Path(__file__).parent.parent / "candidate-schemas.json").read_bytes())


class Invalid(ValueError):
    """Stable local error codes, without guessed private target details."""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Invalid("duplicate_key")
            result[key] = value
        return result

    def nonfinite(_):
        raise Invalid("nonfinite_number")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=nonfinite)
        canonical(value)  # rejects unpaired surrogates as well
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, Invalid):
            raise
        raise Invalid("invalid_json") from exc


def named_schema(name):
    """Only the requested entry point and its dependencies; no research metadata."""
    if name not in SCHEMAS["$defs"]:
        raise Invalid("unknown_schema")
    needed = {}

    def visit(value):
        if isinstance(value, dict):
            if "$ref" in value:
                dep = value["$ref"].removeprefix("#/$defs/")
                if dep not in needed:
                    needed[dep] = copy.deepcopy(SCHEMAS["$defs"][dep])
                    visit(needed[dep])
            for key, item in list(value.items()):
                if key in {"$comment", "$id", "title", "description"}:
                    del value[key]
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    root = {"$ref": f"#/$defs/{name}"}
    visit(root)
    root["$defs"] = needed
    return root


def decode(raw, name):
    value = strict_json(raw)
    if not Draft202012Validator(named_schema(name)).is_valid(value):
        raise Invalid("schema")
    return value


@dataclass(frozen=True)
class Limits:
    body_bytes: int
    summary_bytes: int
    disjoint_recipients: bool  # candidate choice, never an implicit default

    def __post_init__(self):
        if self.body_bytes <= 0 or self.summary_bytes < 0:
            raise Invalid("limits")


@dataclass(frozen=True)
class Binding:
    episode: str
    quarter: int
    owner: str
    release_id: str
    candidate_hash: str
    build_hash: str | None
    evidence_hash: str

    def __post_init__(self):
        if (self.owner not in AGENTS or self.quarter != 1 or not self.episode
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", self.release_id)):
            raise Invalid("binding")
        for digest in (self.candidate_hash, self.evidence_hash):
            if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise Invalid("binding_hash")
        if self.build_hash is not None and not re.fullmatch(r"[a-f0-9]{64}", self.build_hash):
            raise Invalid("binding_hash")


@dataclass(frozen=True)
class Release:
    binding: Binding
    submitted: bool  # supplied snapshot, no lifecycle transition implemented
    owner_evidence: bytes
    reviewer_evidence: bytes
    owner_summary: str = ""


@dataclass(frozen=True)
class Snapshot:
    episode: str
    reviewers: tuple[str, ...]
    releases: tuple[Release, ...]
    namespace: str

    def __post_init__(self):
        if not self.namespace:
            raise Invalid("namespace")
        if self.reviewers not in (P, R):
            raise Invalid("graph")
        if tuple(r.binding.owner for r in self.releases) != AGENTS:
            raise Invalid("inventory")
        if any(r.binding.episode != self.episode for r in self.releases):
            raise Invalid("episode")
        if len({r.binding.release_id for r in self.releases}) != 4:
            raise Invalid("release_ids")

    def own(self, actor):
        check_actor(actor)
        return self.releases[AGENTS.index(actor)]

    def reviewed(self, actor):
        check_actor(actor)
        return self.releases[self.reviewers.index(actor)]


def check_actor(actor):
    if actor not in AGENTS:
        raise Invalid("actor")


def communication(raw, actor, limits):
    check_actor(actor)
    batch = decode(raw, "CommunicationBatch")
    seen = set()
    for message in batch["messages"]:
        recipients = set(message["recipients"])
        if actor in recipients:
            raise Invalid("self_recipient")
        if limits.disjoint_recipients and seen & recipients:
            raise Invalid("overlapping_recipients")
        seen |= recipients
        if len(message["body"].encode("utf-8")) > limits.body_bytes:
            raise Invalid("body_bytes")
    return batch


def decision(raw, actor, phase, snapshot, expected_binding, limits):
    """Validate an intent. Does not sign, deploy, label policy or assign fallback."""
    check_actor(actor)
    if phase not in {"O", "R"}:
        raise Invalid("phase")
    release = snapshot.own(actor) if phase == "O" else snapshot.reviewed(actor)
    if expected_binding != release.binding:
        raise Invalid("slot_binding")
    value = decode(raw, "OwnerDecision" if phase == "O" else "ReviewSlotOutput")
    if phase == "R" and not release.submitted:
        if value != {"decision": "not_applicable"}:
            raise Invalid("review_on_unsubmitted")
        return value
    if phase == "O" and release.submitted:
        raise Invalid("already_submitted")
    if (value.get("release_id") != release.binding.release_id
            or value.get("candidate_hash") != release.binding.candidate_hash):
        raise Invalid("release_binding")
    if len(value.get("summary", "").encode("utf-8")) > limits.summary_bytes:
        raise Invalid("summary_bytes")
    return value
