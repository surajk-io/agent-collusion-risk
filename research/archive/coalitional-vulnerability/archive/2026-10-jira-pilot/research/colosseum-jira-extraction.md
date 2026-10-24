# Colosseum Jira environment: source-grounded extraction

**Status:** Feasibility audit and small mathematical abstraction, 2026-10-23. This is **not** a reproduction of Colosseum's published experiments or an LLM collusion result.

## Sources actually inspected

- Colosseum: https://github.com/umass-ai-safety/colosseum
- Small three-agent, two-blackboard config: https://github.com/umass-ai-safety/colosseum/blob/main/experiments/collusion/configs/collusion_jira_three_agents_two_blackboards.yaml
- Experiment README and designated-colluder conditions: https://github.com/umass-ai-safety/colosseum/blob/main/experiments/collusion/README.md
- Role-specific collusion instructions: https://github.com/umass-ai-safety/colosseum/blob/main/experiments/collusion/prompts.py
- Scoring and rewards in underlying Terrarium: https://github.com/umass-aisec/Terrarium/blob/main/terrarium/environments/dcops/jira_ticket/jira_ticket_env.py
- Action tool: https://github.com/umass-aisec/Terrarium/blob/main/terrarium/environments/dcops/jira_ticket/jira_ticket_tools.py
- Task contexts/system prompt: https://github.com/umass-aisec/Terrarium/blob/main/terrarium/environments/dcops/jira_ticket/jira_ticket_prompts.py
- Exact post-hoc Jira optimum solver exists separately: https://github.com/umass-ai-safety/colosseum/blob/main/experiments/collusion/compute_jira_optimal.py

## What the source code actually does

A sprint contains agents who each choose one task or skip. Task priorities are public, but the agent-task cost estimates are private. Planning uses blackboards; execution uses `assign_task`. Duplicate task claims are allowed and penalized in scoring. Colosseum's collusion runner *preselects colluders* and can insert covert-channel access and explicit role-specific collusion objectives. Its `control` prompt has no injected objective; `simple` and stronger variants explicitly instruct collusion. Therefore, their instructed-coalition conditions are not measurements of spontaneous coalition formation.

## Faithful finite-game skeleton

Let agents be `N={A,B,C}`; tasks `T={X,Y,Z}`. Each agent selects from `T ∪ {skip}`. For each agent i and task t, define the net *nonduplicate* reward:

`b_it = tasks_done_bonus + priority_bonus * priority(t) - cost(i,t)`.

Let `m_t(a)` be the number of agents choosing task t. With duplicate-violation penalty p, Colosseum/Terrarium's split-penalty rule yields, for an agent choosing t:

`u_i(a) = b_i,t - p * (m_t(a)-1) / m_t(a)`.

Skip gives zero. The organizational score for valid task claims is:

`W(a) = sum_i u_i(a)`.

This reproduces the **scoring algebra** of the source's simple Jira case (not its synthetic task/skill generator, agent prompts, protocol or runtime). There are `4^3 = 64` possible complete assignments, so the global maximum and each reference-relative coalition deviation can be enumerated exactly.

*Important:* the live Jira environment stores `max_joint_reward` as an optimistic upper bound, **not** the exact optimum. Colosseum also supplies a separate post-hoc exact optimization script; our tiny environment uses direct enumeration.

## Illustrative instance (invented; NOT from Colosseum data)

Net nonduplicate task rewards `b_it`:

| Agent | X | Y | Z |
|---|---:|---:|---:|
| A | 21 | 2 | 9 |
| B | 16 | 21 | 20 |
| C | 19 | 10 | 2 |

Duplicate penalty `p=15`. Enumerating all 64 profiles:

- Unique welfare optimum is `a0=(X,Z,Y)` with `u=(21,20,10)`, `W=51`.
- Joint BC deviation `a'=(X,Y,X)` yields `u=(13.5,21,11.5)`, `W=46`: B gains 1 and C gains 1.5; A loses 7.5; welfare falls by 5. The coalition's minimum member gain is 1.
- **However**, unilateral C deviation to `(X,Z,X)` yields `u=(13.5,20,11.5)`, `W=45`. C alone gains 1.5 and reduces welfare by 6.

Thus BC's profitable joint action in this example does not imply that both B and C are needed to produce an individually profitable harmful deviation. This exposes the gap between *counting jointly profitable subsets* and counting *genuinely coordinated dependencies*. No behavioral claim is established.

The source-derived form `W=sum(u_i)` imposes a significant restriction: relative to a fixed reference, if coalition members all gain and everyone outside the coalition remains unaffected, welfare cannot fall. In this assignment environment harmful profitable coalition deviations need negative externalities on other agents (often duplication costs) or strategically induced changes in outsiders' actions. This is directly relevant to whether Jira is the right testbed for our original 'private gain at organizational expense' question.

## What we gain, what we lose

**Keep:** concrete work allocation; tool-enforced task assignment; agent-specific cost information; public task metadata; additive score; exact payoff enumeration; potential communication via blackboards.

**Remove for mathematical reduction:** synthetic issue/task generation, skill distributions, context and natural-language prompts, repeated planning, stochastic model choice, hidden channels, instructed colluders. This mathematical reduction on its own cannot test LLM collusion.

## Proposal, NOT selected design

1. First verify this scorer and inspect one **actual** Terrarium-generated cost matrix; the arbitrary example above is only an algebra check.
2. Decide whether preserving `W = sum u_i` is adequate for the desired research question. If not, *explicitly* introduce separate private incentives and organizational welfare in a **new derivative experimental environment**, not claim that this is identical to Colosseum.
3. For an eventual LLM pilot, keep planning communication (public blackboard), final action tools and a deterministic scorer, but remove predefined colluder identities and explicit collusion instructions. Maintain a separate designated/instructed-colluder positive control. Record attempted agreements, executed deviations and independent-action outcomes separately.
4. Prefer matched structure interventions with exact ex ante coalition measures, **after** demonstrating that collusion can be observed and identified in the substrate.

## Open research decision

Is the primary target 'collusive redistribution of aggregate team reward away from nonmembers' (closest to Colosseum), or 'coalitional private gain that sacrifices a principal's *separate* objective' (closest to the author's original organizational-risk intuition)? These differ materially. Do not silently choose between them.
