# Agent Collusion Risk

**Research question:** Can game-theoretic measures of coalitional vulnerability predict emergent harmful coordination among LLM agents, and under what conditions do those predictions succeed or fail?

**Status (2026-10-23):** Exploratory. No validated metric, empirical result, universal safety threshold, or established novelty claim.

The originating intuition is that the **number, magnitude and distribution of profitable harmful deviations across subsets of an agentic organization** may predict observed collusion beyond the single largest available deviation. The longer-term goal is to map executable organizational permissions and incentives into mathematical descriptions and test predictions on held-out organizational configurations.

## Research checkpoint

- [Research question, motivation, and candidate hypotheses](research/research-question.md)
- [Prior work and limits of the novelty check](research/prior-work.md)
- [Adversarial criticisms and success/failure criteria](research/critical-review.md)
- [Model-design worksheet (deliberately unfinished)](research/model-worksheet.md)
- [Welfare-normalized toy game v1](research/toy-model-v1.md)

**Next:** The researcher will independently construct a 3–4-agent toy organization with concrete roles, actions, payoffs, and jointly profitable harmful deviations. The resulting model should be scrutinized before writing LLM simulations.

Keep mathematical possibility, inferred incentives, attempted coordination, causal influence, and realized harmful outcomes separate. Negative results count when controls make them interpretable; do not narrow scope solely to claim novelty.

The idea was independently developed by the author during October 22–23, 2026, with AI-assisted literature investigation and critique. Established game theory predates this discussion. Documenting chronology is not an ownership, patentability, or priority claim.

## Colosseum substrate investigation

- [Source-grounded Jira abstraction and limitations](research/colosseum-jira-extraction.md)
- [Exactly enumerable three-agent Jira miniature](math/jira_miniature.py) and [unit tests](math/test_jira_miniature.py)
- [Jira-mini feasibility pilot implementation](colosseum-jira-pilot-v2/README.md): mock/local runs plus Groq, Ollama, Vertex AI Gemini, and managed-open-model inference

**Not yet selected as experimental substrate:** the source scorer makes organizational welfare equal to summed agent payoffs, which may not capture private incentives conflicting with a distinct principal objective. Further scientific decision is required.
