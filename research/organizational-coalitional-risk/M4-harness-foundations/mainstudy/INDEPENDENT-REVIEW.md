# Offline scientific/engineering review — 2026-10-26

An independent read-only Codex reviewer inspected the implementation and actual serialized requests. It did not edit files or initiate subject/provider calls. This is engineering/scientific criticism, not researcher protocol approval or evidence of spontaneous collusion.

## Demonstrated defects and fixes

1. Repeated safe dependency hashes made Q1 a possible hidden-truth fingerprint lookup. Each actual dependency source now includes its release-specific nonce; regression requires 16 distinct per-block fingerprints.
2. Forged q0 qualification/limited-check evidence was accepted by the early verifier. Verification now reruns actual source, checks visible limited results, dependency digest, exact-candidate qualification and ordinary gate. Three forged-evidence counterexamples fail closed.
3. Eligible `not_applicable` reviewer output received the wrong cause code. It now gets `eligible_not_applicable`; semantic failure preserves the other valid D field.
4. S summaries were a communication side channel in B/C despite disabled C messaging. Optional peer summaries are now omitted in every no-message arm. A direct S-offer regression verifies no receiver packet leaks the text.
5. Partial-prefix reconciliation could become a false negative through ordinary outcome APIs. Its incomplete provenance now persists; a negative explicit label is unknown, and counts are explicitly lower bounds with unobserved slots.
6. Cross-quarter assent could be retrospective. All required assents must precede the earliest action in the proposed arrangement; the executed Q2/Q3/Q4 counterexample is rejected.
7. The initial nested-JSON context bound exceeded 1M. Lossless length framing preserves exact free text while removing its repeated escaping. The reviewer independently tested NULs, Unicode, fake headers and reference-shaped literal strings and found no structural injection. The final bound includes 120 C bodies, eight sent/received S-summary envelopes, four retained own S outputs and one current review summary.
8. A final integration check found A's optional S-summary channel missing from annotation/history. Requested summaries in A now have authenticated message IDs and S-stage receipt order, persist only to participants, and can support human-coded proposal/assent/enactment. A direct S-offer/C3-assent test passes. No-message arms still have no summary delivery.

The reviewer inspected 448 blinded requests and 56 private-finding projections from the complete matrix before the final lossless representation change and found no counterparty identity leak. Final automated tests inspect actual wire requests after decoding the lossless representation across all information arms. Phase D is a stage label and is excluded from identity-only matching; graph charts, peer channels and board history remain absent in D.

## Final limits

The public tokenizer byte-bound and reference encoder are pinned by hash and attached to the launch package. The 4096-token template allowance is conditional on the documented two-message encoding, not an empirical provider-count measurement. No long-context comprehension or provider generation reliability claim follows from byte fit. The live gate requires the attached proofs and their indexed digests.

Independent signatures, same-round pseudo-assent, ordinary cooperation, misunderstanding/uncertain coding, defection and silent arms do not create a positive primary endpoint. The endpoint still requires external semantic coding with exact quotes; this software does not identify private intent or a causal negotiation mediator. Two service templates and an enriched q0 schedule limit external validity. Safe means passes the finite frozen workload; there is no real-world breach or vendor provenance claim.

No unresolved demonstrated engineering defect remains after the final regression run. Separate researcher review of exact prompts, fixtures, provider/settings, budget and absolute stop time is still required before live execution.
