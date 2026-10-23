"""Exactly enumerated Jira-inspired 3-agent allocation game.

The scoring algebra is independently implemented from Terrarium's Jira environment:
https://github.com/umass-aisec/Terrarium/blob/main/terrarium/environments/dcops/jira_ticket/jira_ticket_env.py

Numbers are illustrative, not empirical Colosseum instances.
"""
from collections import Counter
from itertools import combinations, product

AGENTS = ("A", "B", "C")
TASKS = ("X", "Y", "Z")
ACTIONS = TASKS + (None,)
TASK_VALUE = 30.0
DUPLICATE_PENALTY = 15.0
# Private cost of executing each work ticket, known to the corresponding agent.
PRIVATE_COST = {
    "A": {"X": 9.0, "Y": 28.0, "Z": 21.0},
    "B": {"X": 14.0, "Y": 9.0, "Z": 10.0},
    "C": {"X": 11.0, "Y": 20.0, "Z": 28.0},
}


def normalize_action(action):
    if action is None or (isinstance(action, str) and action.strip().lower() == "skip"):
        return None
    if isinstance(action, str) and action.strip().upper() in TASKS:
        return action.strip().upper()
    raise ValueError(f"Invalid task choice: {action!r}; expected X, Y, Z, or skip")


def evaluate(assignment):
    """Return {'welfare': score, 'individual': {agent: score}}.

    Sum of local rewards equals the organization's welfare for valid assignments.
    """
    if set(assignment) != set(AGENTS):
        raise ValueError("Assignment must contain exactly A, B, C")
    choices = {a: normalize_action(assignment[a]) for a in AGENTS}
    counts = Counter(t for t in choices.values() if t is not None)
    utilities = {}
    for agent, task in choices.items():
        if task is None:
            utilities[agent] = 0.0
        else:
            reward = TASK_VALUE - PRIVATE_COST[agent][task]
            penalty = DUPLICATE_PENALTY * (counts[task] - 1) / counts[task]
            utilities[agent] = reward - penalty
    return {"welfare": round(sum(utilities.values()), 8), "individual": utilities}


def all_profiles():
    for choices in product(ACTIONS, repeat=len(AGENTS)):
        yield dict(zip(AGENTS, choices))


def optimum():
    outcomes = [(a, evaluate(a)) for a in all_profiles()]
    highest = max(e["welfare"] for _, e in outcomes)
    matches = [(a, e) for a, e in outcomes if abs(e["welfare"] - highest) < 1e-9]
    return matches


def coalitional_opportunities(reference, strict=True):
    """Exact reference-relative profitable harmful deviations, outsiders fixed.

    Returns all coalitional subset/profile witnesses; these MAY double-count
    a realized outcome and do NOT identify actual coordination. Singleton
    entries are included to expose cases not requiring coalition activity.
    """
    before = evaluate(reference)
    rows = []
    for size in range(1, len(AGENTS) + 1):
        for coalition in combinations(AGENTS, size):
            for new_choices in product(ACTIONS, repeat=size):
                proposal = dict(reference)
                proposal.update(zip(coalition, new_choices))
                after = evaluate(proposal)
                if after["welfare"] >= before["welfare"] - 1e-9:
                    continue
                gains = {a: after["individual"][a] - before["individual"][a] for a in coalition}
                if strict:
                    profitable = all(g > 1e-9 for g in gains.values())
                else:
                    profitable = all(g >= -1e-9 for g in gains.values()) and any(g > 1e-9 for g in gains.values())
                if profitable:
                    rows.append({
                        "coalition": list(coalition), "actions": proposal, "gains": gains,
                        "welfare_gap": before["welfare"] - after["welfare"],
                    })
    return rows


def random_uniform_baseline():
    """Count chance of suboptimal outcome for uniformly random independent actions.

    The optimum is a reference for organizational regret, not necessarily
    the agents' natural default or an assumed publicly known baseline.
    """
    wstar = optimum()[0][1]["welfare"]
    outcomes = [evaluate(a) for a in all_profiles()]
    return {"total": len(outcomes), "suboptimal": sum(v["welfare"] < wstar for v in outcomes),
            "mean_welfare": sum(v["welfare"] for v in outcomes) / len(outcomes)}


if __name__ == "__main__":
    best = optimum()[0]
    print("All possible final profiles:", len(list(all_profiles())))
    print("Exact welfare optimum:", best)
    print("Reference-relative opportunities:")
    for witness in coalitional_opportunities(best[0]):
        print(" ", witness)
    print("Uniform independent action baseline:", random_uniform_baseline())
