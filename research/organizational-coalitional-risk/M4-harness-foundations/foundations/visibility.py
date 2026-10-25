"""Trusted projections and opaque four-slot barriers, without episode logic."""
from dataclasses import asdict, dataclass

from .contracts import AGENTS, Invalid, canonical, check_actor, communication
from .records import blob, unblob


class Barrier:
    """One private result per actor. The caller chooses phase, validation, timing.

    Exact duplicate bytes are idempotent; conflicts fail without overwriting.
    Missing/invalid results remain explicit errors, never behavioral decisions.
    """

    def __init__(self, key, episode, namespace):
        if not episode or not namespace:
            raise Invalid("barrier_identity")
        self.key = key
        self._run = {"episode": episode, "namespace": namespace}
        self._pending = {}

    def record(self, actor, raw, error=None):
        check_actor(actor)
        value = {"raw": blob(raw) if raw is not None else None, "error": error}
        if actor in self._pending and self._pending[actor] != value:
            raise Invalid("completion_conflict")
        self._pending[actor] = value

    def commit(self, journal):
        if set(self._pending) != set(AGENTS):
            raise Invalid("incomplete_barrier")
        return journal.append(self.key, "barrier", {"run": self._run,
                              "slots": {a: self._pending[a] for a in AGENTS}})


@dataclass(frozen=True)
class Envelope:
    round: int
    sender: str
    batch_index: int
    recipients: tuple[str, ...]
    body: str


class Messages:
    """Delivered communication only. Restore exclusively from committed barriers."""

    def __init__(self, episode, namespace, max_rounds):
        if not isinstance(max_rounds, int) or max_rounds <= 0:
            raise Invalid("round_limit")
        if not episode or not namespace:
            raise Invalid("message_identity")
        self._run = {"episode": episode, "namespace": namespace}
        self.max_rounds = max_rounds
        self._rounds = {}

    def deliver(self, journal, key, round_number, limits):
        event = journal.committed(key)
        if event["kind"] != "barrier" or not 1 <= round_number <= self.max_rounds:
            raise Invalid("message_barrier")
        if event["data"]["run"] != self._run:
            raise Invalid("message_identity")
        slots = event["data"]["slots"]
        if set(slots) != set(AGENTS):
            raise Invalid("message_barrier")
        deliveries, errors = [], {}
        for actor in AGENTS:
            item = slots[actor]
            try:
                if item["error"] is not None or item["raw"] is None:
                    raise Invalid(item["error"] or "missing")
                batch = communication(unblob(item["raw"]), actor, limits)
                deliveries.extend(Envelope(round_number, actor, i,
                                           tuple(m["recipients"]), m["body"])
                                  for i, m in enumerate(batch["messages"]))
            except Invalid as exc:
                errors[actor] = str(exc)
        value = (tuple(deliveries), errors)
        if round_number in self._rounds:
            if self._rounds[round_number] != value:
                raise Invalid("round_conflict")
        elif round_number != len(self._rounds) + 1:
            raise Invalid("round_order")
        self._rounds[round_number] = value
        return dict(errors)  # trusted caller routes local receipts; never public

    def history(self, actor, through_round):
        check_actor(actor)
        if not 0 <= through_round <= len(self._rounds):
            raise Invalid("history_watermark")
        return tuple(e for n in range(1, through_round + 1)
                     for e in self._rounds[n][0]
                     if actor == e.sender or actor in e.recipients)


def project(snapshot, actor, messages, through_round, public_context):
    """Neutral test projection, NOT the candidate literal prompt renderer.

    Only allowlisted evidence enters. No journal, pending state, annotations,
    provider reasoning or hidden truth field exists in this input contract.
    Trust/semantic review of supplied evidence bytes remains a caller obligation.
    """
    if messages._run != {"episode": snapshot.episode, "namespace": snapshot.namespace}:
        raise Invalid("projection_identity")
    own = snapshot.own(actor)
    reviewed = snapshot.reviewed(actor)
    assigned = {"status": "not_submitted"}
    if reviewed.submitted:
        assigned = {"status": "submitted", "binding": asdict(reviewed.binding),
                    "evidence": reviewed.reviewer_evidence.decode("utf-8"),
                    "owner_authored_summary": reviewed.owner_summary}
    # No global message IDs, batch indices, errors or cursor in visible envelopes.
    history = [{"round": e.round, "sender": e.sender,
                "recipients": e.recipients, "body": e.body}
               for e in messages.history(actor, through_round)]
    return canonical({"public_context": public_context.decode("utf-8"),
                      "actor": actor, "own_binding": asdict(own.binding),
                      "owner_evidence": own.owner_evidence.decode("utf-8"),
                      "own_summary": own.owner_summary,
                      "assigned_review": assigned, "participant_messages": history})
