"""Frozen allocation, legal-context witnesses and conservative spending reserve."""
from dataclasses import asdict
from foundations.contracts import AGENTS, canonical
from foundations.records import digest
from f1.preflight import proposal_config
from .contracts import Spec
from .fixtures import inventory

CONTEXT_LIMIT = 1048576
OUTPUT_TOKENS = 8192
INPUT_RESERVATION = CONTEXT_LIMIT - OUTPUT_TOKENS
PAIR_RESERVATION_USD = 75
MAX_BUDGET_USD = 600


def allocation(seed=20261026):
    # Prespecified priority, counterbalanced graph order by block.
    pairs = [(1, "A"), (2, "A"), (1, "B"), (1, "C"), (1, "D"),
             (2, "B"), (2, "C"), (2, "D")]
    result = []
    for index, (block, condition) in enumerate(pairs):
        fixtures = inventory(block)
        case_hash = digest(canonical({f"{q}-{a}": r.candidate_hash for (q, a), r in fixtures.items()}))
        result.append({"pair": index + 1, "block": block, "condition": condition,
            "graphs": ["P", "R"] if block == 1 else ["R", "P"],
            "case_allocation_sha256": case_hash, "specs": [asdict(Spec(graph=g, condition=condition, block=block, seed=seed))
                              for g in (["P", "R"] if block == 1 else ["R", "P"])],
            "reserved_calls": 224, "reservation_usd": PAIR_RESERVATION_USD})
    return result


def capacity_report(runners):
    rows = []
    for runner in runners:
        for path in sorted((runner.archive.root / "requests").glob("*.json")):
            raw = path.read_bytes()
            # Actual provider receives decoded message content. JSON transport
            # escaping is not itself tokens; a nested user JSON remains text.
            from foundations.contracts import strict_json
            body = strict_json(raw)
            content_bytes = sum(len(m["content"].encode()) for m in body["messages"])
            rows.append({"episode": runner.spec.episode, "slot": path.stem,
                "wire_bytes": len(raw), "decoded_content_bytes": content_bytes,
                "conservative_token_planning_bound": content_bytes + 4096,
                "sha256": digest(raw)})
    worst = max(rows, key=lambda r: r["conservative_token_planning_bound"])
    # A witness is not a theorem about every legal token sequence. Structural
    # byte upper bound covers 120 visible envelopes, four S outputs and current
    # reviewer summary, decisions, receipts, up to four findings/quarter, boards,
    # schemas and source packets. 128KiB covers all fixed bounded records.
    # Each one-byte control can expand to six ASCII bytes in user JSON.
    structural_byte_bound = 120 * 2048 * 6 + 5 * 2048 * 6 + 131072
    return {"method": "Executed NUL-body/split-recipient maximal-history witnesses plus universal byte bound; not exact provider tokenization",
        "worst_witness": worst, "rows": rows, "structural_decoded_byte_upper_bound": structural_byte_bound,
        "provider_context_limit": CONTEXT_LIMIT, "output_tokens_including_reasoning": OUTPUT_TOKENS,
        "planning_token_upper_bound": structural_byte_bound + 4096,
        "capacity_proven": structural_byte_bound + 4096 + OUTPUT_TOKENS <= CONTEXT_LIMIT,
        "provider_tokenizer_verified": False,
        "launch_blocker": "Universal byte bound exceeds model context. An exact tokenizer/encoding bound or separately approved capacity configuration is required; do not truncate histories or narrow message legality.",
        "sources": ["https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/deepseek/deepseek-v41-flash",
                    "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing"],
        "checked_date": "2026-10-26", "usd_per_million": {"input": .30, "output": 1.20},
        "per_pair_ceiling_at_full_context_usd": 224 * (INPUT_RESERVATION * .30 + OUTPUT_TOKENS * 1.20) / 1e6,
        "pair_reservation_usd": PAIR_RESERVATION_USD, "maximum_budget_usd": MAX_BUDGET_USD}


def launch_proposal(package_hash):
    return {"status": "PROPOSED_NOT_AUTHORIZED", "researcher_approval_reference": None,
        "git_revision": "REPLACE_WITH_REVIEWED_COMMIT", "package_sha256": package_hash,
        "provider_config": proposal_config(), "calls_per_episode": 112, "max_calls": 1792,
        "max_pairs": 8, "maximum_budget_usd": MAX_BUDGET_USD,
        "reservation_per_pair_usd": PAIR_RESERVATION_USD,
        "stop_new_pairs_at": None, "timezone": "Asia/Kolkata",
        "capacity_proof_sha256": None, "capacity_proven": False,
        "approved_prompts_and_fixtures": False, "no_retries_or_replacements": True,
        "note": "Full-context conservative reserve, not an expected charge or approved spend. Freeze an absolute timestamp before launch."}
