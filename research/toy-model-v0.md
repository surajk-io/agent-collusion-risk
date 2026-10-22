**Note (2026-10-23): This is the original toy model, retained for history. The active experimental version replaces W=0/-5 with W=10/8 without altering member payoffs. See `toy-model-v1.md` and the updated enumerator.**

# Baseline toy model v0 — three-agent expense approval

**Status (2026-10-23): Selected as a deliberately artificial mathematical reference model, not an experimental finding or a proposed novel game.**

## Definition

Players: `N = {A, B, C}`. Each player has a binary action in `{0,1}`.

- A submits a claim; A=1 means submitting a fraudulent claim.
- B decides whether to bypass verification; B=1 means overriding the check.
- C decides whether to conduct an effective audit; C=1 means auditing and blocking fraudulent payment.

The reference action profile is `a0 = (0,0,0)`. For the moment all players move simultaneously, and the outcome is deterministic. Successful fraud occurs **if and only if** `(A,B,C) = (1,1,0)`. This is a one-step normal-form game, not yet a sequential organization.

```
if (A,B,C) == (1,1,0):
    (u_A, u_B, u_C, W) = (3,2,0,-5)
else:
    (u_A, u_B, u_C, W) = (0,0,0,0)
```

All eight profiles are therefore:

| (A,B,C) | u_A | u_B | u_C | W |
|---|---:|---:|---:|---:|
| (0,0,0) | 0 | 0 | 0 | 0 |
| (0,0,1) | 0 | 0 | 0 | 0 |
| (0,1,0) | 0 | 0 | 0 | 0 |
| (0,1,1) | 0 | 0 | 0 | 0 |
| (1,0,0) | 0 | 0 | 0 | 0 |
| (1,0,1) | 0 | 0 | 0 | 0 |
| **(1,1,0)** | **3** | **2** | **0** | **-5** |
| (1,1,1) | 0 | 0 | 0 | 0 |

## Exact coalitional property

For a nonempty subset `S`, hold actions of outsiders at their reference values. Call `S` **strictly profitable and harmful** if some permitted joint deviation lowers `W` relative to the reference and strictly raises *each participating member's payoff*.

- `{A,B}` qualifies via `(1,1,0)`, with member gains `(+3,+2)` and organizational loss `5`.
- `{A,C}` and `{B,C}` do not qualify.
- `{A,B,C}` does not qualify under *strict gain for all members*, since C receives `0`, not a positive gain.
- No unilateral deviation from the reference can cause harm.

A candidate worst-member gain is `g({A,B}) = min(3,2) = 2`. The other coalitions have **no strictly profitable harmful deviation**; one should not conflate this with a measured zero event probability.

If instead “profitable” means *all members weakly benefit, and at least one strictly benefits*, then `{A,B,C}` also qualifies: C remains at baseline while the harmful outcome occurs. This describes the **same single outcome**, exposing a potential duplicate-counting issue. We should explicitly choose a coalition-membership convention before defining aggregate vulnerability measures.

## What this model does not demonstrate

1. No communication, negotiation, or causal influence is modeled: the outcome `(1,1,0)` can occur under independent actions and is not proof of collusion.
2. C is indifferent between auditing and not auditing under the specified utilities, so auditing behavior cannot yet be predicted.
3. The model fixes noncoalition players at their reference actions. It does not address strategic responses, belief formation, repeated play, or incomplete information.
4. The reference is legitimate by stipulation, not derived uniquely from payoffs. Welfare is merely a specified number.
5. Mathematical opportunity alone does not determine an LLM's probability of choosing an action.
6. A “coalition” here means an analytically tested subset that can deviate, **not** an observed social group.

## Next scientifically meaningful step

Construct a *matched second game* with the same number of agents and the same maximum coalition gain but a different number of distinct minimal profitable harmful coalitions, and verify what other properties change. Whether it is possible to isolate the count from action framing, coordination complexity, or coalition overlap is itself a methodological question. Do not fit a probability model before defining an observable collusion outcome.

The small enumerator in `math/finite_game.py` serves as an executable arithmetic check, not a simulation of agent behavior.
