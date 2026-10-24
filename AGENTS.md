# Instructions for AI research collaborators

This file is a **portable research protocol** for ChatGPT, Codex, Gemini, and other agents working with this repository. It cannot automatically enforce itself in a chat that has not read it. **At the start of a new research thread, read this file, [ROADMAP.md](ROADMAP.md), and [research/research-question.md](research/research-question.md) from the current GitHub branch.** Check current status rather than relying on chat memory.

## Researcher retains scientific authority

**Always surface the most consequential load-bearing choices and obtain the human researcher's explicit approval before treating them as decisions or implementing a behavioral experiment.** This includes seemingly minor prompt wording when it could alter what is measured. Explain alternatives, expected consequences, uncertainties and whether the choice is reversible. Do not silently substitute defaults.

Exploration, ideas and criticism may proceed without approval. Reversible coding details that cannot affect experimental behavior do not require separate sign-off. **Do not** silently finalize or materially change scenarios, hypotheses, payoff functions, authority structure, action protocols, agent instructions, measurement labels, model/condition selection, intervention design, or sampling/analysis plans. If approval is missing, mark choices **PROPOSED**, not **APPROVED**, and stop at the relevant gate.

### Detect important choices you might not notice

**Before recommending implementation or any new behavioral run, explicitly inventory all experimental assumptions**, including choices that seem mundane:

1. **Agent epistemic framing:** Exact system/user prompt, "simulation"/"evaluation"/"synthetic" language, role legitimacy, reward display, what agents know, whether they might infer testing, and whether assumptions about real work are truthful.
2. **Organization and authority:** Roles, incentives, trust boundaries, who can act/approve/veto/audit, information access, covert/public communication, tool-enforced capabilities, and what one agent can do alone.
3. **Environment mathematics:** What generates true organizational value, how duplicates are valued, whose welfare is measured, individual payoffs versus actual agent preferences, baseline, counterfactuals and joint-action feasibility.
4. **Interaction protocol:** One-shot/repeated interaction, turn order, memory/context handling, private reasoning leakage, budgets, actions, failure handling, provider/model variants.
5. **Identification and measurement:** What distinguishes independent self-interest, mistakes, legitimate coordination, mere opportunity, collusion attempts, realized harm and **causally supported** collusion; comparison groups and positive controls.
6. **Statistical/evidential commitments:** Primary hypotheses, outcome definitions, controls, sample size/budget, model and seed selection, exclusions, data logging and interpretation of negative results.

**For every proposed design**, make a short **load-bearing decision register**: decision/implicit default; one or more reasonable alternatives; how this could change behavior or conclusions; what remains unknown; approval status. Surface material items to the human **before** generating final prompts/code or running agents. If no single choice seems critical, ask **"What consequential choices am I failing to notice?"** and invite an independent model to attack those omissions. The researcher should not need to discover critical assumptions by reading raw transcripts.

## Approval and review gates

1. **Scenario gate:** Present workflow, roles, goals, permissions, actual task effects, incentives, why collusion is plausible, and alternative explanations. Get explicit human approval.
2. **Model gate:** Present the formal abstraction, payoffs and independent organizational welfare, coalition baseline and proposed predictions. Check math and get explicit human approval.
3. **Experiment gate:** Present actual agent-facing prompts (especially test/simulation cues), tool permissions, conditions, causal controls, labels, model panel, run budget and stopping/analysis choices. Independent red-team review plus explicit human approval **before behavioral runs**.
4. **Material change gate:** Reopen approval when changing any accepted load-bearing assumption; log what changed. Don't bury a consequential change in "cleanup" or a refactor.

An independent reviewer (Gemini Argon, or another model, when available) should prioritize **fatal flaws, missing decisions, confounds, and the smallest discriminating control**, not generic praise or endless debate. Its critique is neither validation nor a substitute for researcher approval. Check claims, especially about prior work and model capabilities. No agent may declare its own design reviewed merely because another model agrees.

At the end of a design conversation, distinguish: **Observed evidence**, **proposals/hypotheses**, **explicitly approved decisions**, **unresolved questions**, and **what to checkpoint in Git**. If no material change occurred, no repository update is necessary.

## Research integrity and project hygiene

- The two questions are both **open**; neither is preferred or merged by default. Follow [ROADMAP.md](ROADMAP.md).
- Old Jira/Colosseum pilot experiments live under [archive/2026-10-jira-pilot](archive/2026-10-jira-pilot/README.md). They were exploratory smoke tests, **not evidence of spontaneous collusion**.
- Preserve original prompts, code, traces, caveats and negative results. Never retrofit a new claim to an old run.
- Prefer small, realistic, tool-enforced setups and falsifiable contrasts over elaborate infrastructure or tuned demonstrations.
- GitHub is the **canonical durable state**. Keep changes reviewable and documentation minimal. Do not overwrite or make major research decisions without the researcher.
