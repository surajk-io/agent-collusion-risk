"""Exactly enumerable, Jira-inspired assignment game (not the full Colosseum environment).

The reward rule is adapted from Terrarium's JiraTicketEnvironment:
https://github.com/umass-aisec/Terrarium/blob/main/terrarium/environments/dcops/jira_ticket/jira_ticket_env.py

The 3x3 task rewards are *invented illustrative numbers*, not Colosseum output.
Run: python math/jira_miniature.py
"""
from collections import Counter
from itertools import combinations, product

AGENTS = ("A", "B", "C")
TASKS = ("X", "Y", "Z")
ACTIONS = TASKS + (None,)
# Net rewards after per-task value minus the agent-specific private cost.
NET_TASK_REWARDS = {
    "A": {"X": 21., "Y": 2., "Z": 9.},
    "B": {"X": 16., "Y": 21., "Z": 20.},
    "C": {"X": 19., "Y": 10., "Z": 2.},
}
DUPLICATE_PENALTY = 15.


def evaluate(assignment):
    """Returns (organizational_welfare, individual_utility_vector)."""
    if len(assignment) != len(AGENTS) or any(a not in ACTIONS for a in assignment):
        raise ValueError("Expected three choices from X/Y/Z/None")
    counts = Counter(task for task in assignment if task is not None)
    utilities = []
    for agent, task in zip(AGENTS, assignment):
        if task is None:
            utilities.append(0.)
        else:
            shared_penalty = DUPLICATE_PENALTY * (counts[task] - 1) / counts[task]
            utilities.append(NET_TASK_REWARDS[agent][task] - shared_penalty)
    return sum(utilities), tuple(utilities)


def enumerate_profiles():
    return {a: evaluate(a) for a in product(ACTIONS, repeat=3)}


def optima():
    states = enumerate_profiles()
    max_welfare = max(w for w, _ in states.values())
    return [(a, w, u) for a, (w, u) in states.items() if w == max_welfare]


def profitable_deviations(reference, strict=True):
    """Compare each coalition against reference with outsiders held fixed.

    Does not establish observed coordination or member necessity.
    """
    welfare0, utility0 = evaluate(reference)
    found = {}
    for size in range(1, len(AGENTS) + 1):
        for members in combinations(range(3), size):
            events = []
            for choices in product(ACTIONS, repeat=size):
                a = list(reference)
                for idx, choice in zip(members, choices):
                    a[idx] = choice
                a = tuple(a)
                welfare, utility = evaluate(a)
                gains = tuple(utility[i] - utility0[i] for i in members)
                acceptable = (
                    all(g > 0 for g in gains) if strict
                    else all(g >= 0 for g in gains) and any(g > 0 for g in gains)
                )
                if welfare < welfare0 and acceptable:
                    events.append((a, gains, welfare0 - welfare))
            found["".join(AGENTS[i] for i in members)] = events
    return found


if __name__ == "__main__":
    base = optima()[0][0]
    print("Profiles enumerated:", len(enumerate_profiles()))
    print("Exact optima:", optima())
    print("Profitable harmful deviation opportunities, including singletons:")
    for coalition, events in profitable_deviations(base).items():
        if events:
            print(coalition, events)
