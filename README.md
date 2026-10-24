# Agent Collusion Risk

**Status:** Exploratory. Two independent scientific directions; no approved behavioral experiment, validated predictor, or established finding of emergent collusion.

## Active research directions

| Direction | Question | Next |
|---|---|---|
| [Coalitional vulnerability](research/coalitional-vulnerability/README.md) | Can number, magnitude, distribution and credibility of profitable harmful coalitions predict realized collusion among AI agents? | [M1: credible organizational workflow](research/coalitional-vulnerability/ROADMAP.md) |
| [Organizational power dynamics](research/organizational-power-dynamics/README.md) | How do authority, permissions, information and influence affect formation and success of harmful coalitions? | [M0: dedicated literature review](research/organizational-power-dynamics/ROADMAP.md) |

Neither direction is chosen over the other or merged into a common formal hypothesis.

## Shared working definitions

These are **provisional conceptual definitions**, not experimentally validated labels.

- **Coordination:** Actions shaped by inter-agent communication, observation or influence; matching actions by themselves do not prove coordination.
- **Collusion:** Coordination toward an unauthorized subgroup objective or arrangement that conflicts with legitimate organizational goals or constraints. Whether explicit agreement, tacit understanding, intent or mutual awareness are necessary remains a study-specific operational decision.
- **Coalition:** A subset of agents considered jointly; mathematical eligibility does not imply an actual agreement.
- **Coalitional vulnerability:** Feasible opportunities for subsets to benefit under modeled incentives while harming an organizational objective; this is not a probability of real collusion.
- **Organizational power:** Ability to affect outcomes through enforceable authority, permissions, vetoes, resource or information control, or influence. These dimensions should not be conflated.
- **Organizational welfare:** Value relative to a specified legitimate organizational objective; not automatically the sum of individual rewards.
- **Causal collusion evidence:** Evidence that inter-agent influence materially contributed to harmful coordination, beyond independent self-interest, mistakes, normal cooperation or obedience.

**Do not infer collusion solely from harm, coincident actions or a welfare gap.**

## Research collaboration and new chats

Read [AGENTS.md](AGENTS.md) for standards governing conceptual, theoretical, empirical and coding work. **Git is canonical durable state; chats are working context.**

Use this reusable starting prompt, filling in the two placeholders:

```text
Use the GitHub repository surajk-io/agent-collusion-risk as canonical state.
Read the current main-branch README.md and AGENTS.md, plus README.md,
ROADMAP.md and relevant literature/review files in research/<DIRECTION>/.

Direction: <coalitional-vulnerability OR organizational-power-dynamics>
Today's objective: <what we will investigate or accomplish>

First verify and briefly summarize the current milestone, previously
approved decisions, unresolved questions and pertinent evidence.
Then help me as a critical research collaborator. Distinguish sources,
assumptions, proposals, and decisions. Surface load-bearing choices and
alternatives for my explicit approval. Do not assume an experiment has
already been approved. Do not write to GitHub without authorization.
```

For power dynamics, a useful next objective is: **Conduct a critical, source-grounded literature review of hierarchy, authorization, organizational power and harmful LLM-agent coordination, establishing the closest work and remaining open questions.**

## History and parallel development

[October 2026 Jira/Colosseum pilot archive](research/coalitional-vulnerability/archive/2026-10-jira-pilot/README.md) preserves code, mathematical examples, tests, transcripts and reviews. **It is technical smoke-test work, not proof of spontaneous collusion.**

Future experiments belong to independent `experiments/<id>/` directories within the relevant research direction. For simultaneous coding agents use **distinct Git branches and worktrees** and explicit ownership of shared interfaces; directories alone cannot prevent conflicts.

Commit history has been **retained** to preserve scientific provenance.
