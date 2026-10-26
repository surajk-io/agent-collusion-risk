"""Main-study contracts; deliberately independent of frozen F1 action semantics."""
from dataclasses import dataclass
from foundations.contracts import AGENTS, P, R, Invalid, Limits, canonical, strict_json, communication
from jsonschema import Draft202012Validator

ORDER = ("C1", "C2", "S", "C3", "C4", "C5", "D")
LIMITS = Limits(2048, 2048, True)


def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}


def action(choices):
    return obj({"decision": {"enum": choices}, "release_id": {"type": "string", "maxLength": 40},
                "candidate_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"}})


REQUEST_SCHEMA = action(["request_review", "hold", "escalate"])
REQUEST_SCHEMA["properties"]["summary"] = {"type": "string", "maxLength": 2048}
REQUEST_SCHEMA["required"].append("summary")
DUAL_SCHEMA = obj({"owner": action(["authorize", "withhold", "escalate"]),
                   "review": {"oneOf": [action(["approve", "reject"]),
                                          obj({"decision": {"const": "not_applicable"}})]}})


def schema(stage, enabled):
    if stage == "S":
        return REQUEST_SCHEMA
    if stage == "D":
        return DUAL_SCHEMA
    if not enabled:
        return obj({"messages": {"const": []}})
    from foundations.contracts import named_schema
    return named_schema("CommunicationBatch")


def decode(raw, stage, actor, enabled):
    value = strict_json(raw)
    if not Draft202012Validator(schema(stage, enabled)).is_valid(value):
        raise Invalid("schema")
    if stage.startswith("C"):
        return communication(raw, actor, LIMITS)
    if stage == "S" and len(value["summary"].encode()) > LIMITS.summary_bytes:
        raise Invalid("summary_bytes")
    return value


@dataclass(frozen=True)
class Spec:
    graph: str = "P"
    condition: str = "A"
    block: int = 1
    seed: int = 20261026
    timeout_seconds: float = 180
    max_input_bytes: int = 2097152

    def __post_init__(self):
        if (self.graph not in ("P", "R") or self.condition not in AGENTS or
                self.block not in (1, 2) or type(self.seed) is not int or
                self.timeout_seconds <= 0 or self.max_input_bytes <= 0):
            raise Invalid("spec")

    @property
    def reviewers(self):
        return dict(zip(AGENTS, P if self.graph == "P" else R))

    def reviewed(self, actor):
        return next(a for a, reviewer in self.reviewers.items() if reviewer == actor)

    @property
    def episode(self):
        return f"main-{self.condition}-{self.graph}-b{self.block}-s{self.seed}"

    @property
    def messaging(self):
        return self.condition == "A"

    @property
    def run_id(self):
        return self.episode

    @property
    def namespace(self):
        return "mainstudy-offline"


GENERATION = canonical({"temperature": 0, "top_p": 1, "max_tokens": 8192,
                        "chat_template_kwargs": {"thinking": True},
                        "response_format": {"type": "json_object"}, "stream": False})
