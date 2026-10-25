"""Synthetic deterministic bytes. No actual release, build or qualification."""
from foundations.contracts import AGENTS, Binding, Limits, Release, Snapshot, canonical
from foundations.records import digest

# Deliberately explicit test parameters, not scientific launch defaults.
LIMITS = Limits(body_bytes=1024, summary_bytes=2048, disjoint_recipients=True)


def snapshot(graph, submitted=False, episode="fixture-episode"):
    releases = []
    for actor in AGENTS:
        raw = f"synthetic source {actor}".encode()
        evidence = f"synthetic visible evidence {actor}".encode()
        binding = Binding(episode, 1, actor, f"fixture-{actor}", digest(raw),
                          None, digest(evidence))
        releases.append(Release(binding, submitted, evidence, evidence))
    return Snapshot(episode, graph, tuple(releases), "unit-fixture")


def action(release, choice, summary=""):
    value = {"release_id": release.binding.release_id,
             "candidate_hash": release.binding.candidate_hash, "decision": choice}
    if choice == "submit":
        value["summary"] = summary
    return canonical(value)


def batch(*messages):
    return canonical({"messages": [{"recipients": recipients, "body": body}
                                   for recipients, body in messages]})
