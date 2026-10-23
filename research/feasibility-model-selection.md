# Feasibility pilot: model selection (2026-10-23)

**Decision for the next feasibility run (not a permanent research-design choice):**
- Primary: **Gemini 3.7 Flash** via Google Cloud Vertex AI / Agent Platform. Reason: directly relevant independent observation of explicit coordination in a long-horizon collusion study. Avoid interpreting this as a universal collusion propensity or as an expected probability for our one-shot Jira setting.
- Cross-family comparison: **DeepSeek V4.1 Flash** (managed MaaS). Capable and economical, but no verified like-for-like published collusion propensity.
- Budget comparator: **GPT-OSS 120B** (managed MaaS). Very inexpensive and strong enough to test basic task reasoning, not selected for a known collusion predisposition.
- Defer **Gemini 3.8 Flash** until a robustness comparison; selecting 3.7 reflects direct relevant study evidence, not a claim of greater capability.
- Do **not** select best-colluding model post hoc and generalize: initial model selection intentionally enriches for feasibility. Freeze model panel and conditions before analyzing hypothesis tests.

**Relevant evidence:**
- Shi, Zhang & Yang, *Emergent Collusion in Long-Horizon LLM Agent Interaction*, https://arxiv.org/abs/2609.24967 : Gemini 3.7 Flash collusion in all 50 reported long-horizon trajectories, and 90% of collusive trajectories began with explicit coordination. Not transferable to one-shot settings.
- Lee, *Who Leads and Who Collects* (2026), https://arxiv.org/abs/2610.11256 : vendor/model differences in a *no-communication repeated pricing market*, different versions and metric.
- Nakamura et al., *Colosseum*, https://arxiv.org/abs/2602.15198 : communication and execution can diverge ('collusion on paper').

**Google Cloud published pay-as-you-go prices (USD / 1M input, output tokens):**
- Gemini 3.7 Flash $0.75/$3.75 through Dec 31, 2026
- DeepSeek V4.1 Flash $0.30/$1.20; preview, published minimum availability through Nov 28, 2026
- GPT-OSS 120B $0.09/$0.36; managed GA
Source: https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing

**Credits caveat:** Google's AI Pro Google Developer Program **$10 monthly general Cloud credit** is documented as applicable to Google Cloud products including Vertex AI. A different **$50 annual GenAI developer credit** is restricted to Google GenAI offerings (Gemini, Imagen, Veo). Actual eligibility for particular MaaS billing SKUs must be confirmed from user's billing promotion terms and cost report. https://developers.google.com/profile/help/benefits

**First run proposal:** For each model, compare uninstructed public planning, no-chat, and instructed coalition positive control on the same fixed instance/seeds; log actual prompt/version/temperature/reasoning settings, tokens, transcripts and payoffs; separately classify explicit attempts, successful execution, and ordinary harmful action profiles. Small number of episodes is feasibility only. No live model inference performed here.

**Critical warning:** The one-shot Jira miniature admits profitable unilateral harm and therefore a negative or positive harm rate alone is not evidence about emergent collusion. Longer-horizon replication may ultimately be needed.
