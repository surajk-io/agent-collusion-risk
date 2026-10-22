"""Exact enumeration of the project's three-agent baseline game.

Standard-library only. This computes opportunities, not LLM behavior.
"""
from itertools import combinations, product

AGENTS = ("A", "B", "C")
BASELINE = (0, 0, 0)


def evaluate(actions):
    """Return ((u_A, u_B, u_C), organization_welfare)."""
    if len(actions) != 3 or any(a not in (0, 1) for a in actions):
        raise ValueError("Expected three binary actions")
    if tuple(actions) == (1, 1, 0):
        return (3, 2, 0), -5
    return (0, 0, 0), 0


def opportunities(members, strict=True):
    """Hold nonmembers at baseline; enumerate harmful profitable deviations.

    strict: all members gain > 0
    non-strict: all members gain >= 0 and at least one gains > 0
    """
    baseline_utilities, baseline_w = evaluate(BASELINE)
    found = []
    for member_actions in product((0, 1), repeat=len(members)):
        profile = list(BASELINE)
        for index, action in zip(members, member_actions):
            profile[index] = action
        profile = tuple(profile)
        utilities, welfare = evaluate(profile)
        gains = tuple(utilities[i] - baseline_utilities[i] for i in members)
        profitable = (all(g > 0 for g in gains) if strict
                      else all(g >= 0 for g in gains) and any(g > 0 for g in gains))
        if welfare < baseline_w and profitable:
            found.append((profile, gains, baseline_w - welfare))
    return found


def all_coalitions(strict=True):
    return {
        "".join(AGENTS[i] for i in group): opportunities(group, strict)
        for size in (2, 3)
        for group in combinations(range(3), size)
    }


if __name__ == "__main__":
    print("All eight profiles:")
    for a in product((0, 1), repeat=3):
        u, w = evaluate(a)
        print(a, u, w)
    print("Strict coalition opportunities:", all_coalitions(strict=True))
    print("Weak coalition opportunities:", all_coalitions(strict=False))
