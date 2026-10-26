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
TOKENIZER_SHA256 = "c90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b"
ENCODER_SHA256 = "502bdaec8a3fd88ebc24c4721a7038fbe42f2063c664638127056107920035c1"


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
            from .materials import visible
            def free_text(value):
                if isinstance(value, dict):
                    return sum(len(v.encode()) if k in ("body", "summary", "owner_authored_summary") and isinstance(v, str)
                               else free_text(v) for k, v in value.items())
                return sum(free_text(v) for v in value) if isinstance(value, list) else 0
            fixed_bytes = content_bytes - free_text(visible(raw))
            if fixed_bytes > 131072:
                from foundations.contracts import Invalid
                raise Invalid("metadata_context_bound_exceeded")
            rows.append({"episode": runner.spec.episode, "slot": path.stem,
                "wire_bytes": len(raw), "decoded_content_bytes": content_bytes,
                "fixed_record_and_frame_bytes": fixed_bytes,
                "conservative_token_planning_bound": content_bytes + 4096,
                "sha256": digest(raw)})
    worst = max(rows, key=lambda r: r["conservative_token_planning_bound"])
    # A witness is not a theorem about every legal token sequence. Structural
    # byte upper bound covers 120 C envelopes + eight S-summary envelopes,
    # four own S outputs and current
    # reviewer summary, decisions, receipts, up to four findings/quarter, boards,
    # schemas and source packets. 128KiB covers all fixed bounded records.
    # Verbatim variable fields do not expand inside the decoded user content.
    structural_byte_bound = 128 * 2048 + 5 * 2048 + 131072
    return {"method": "Lossless verbatim length frames: universal UTF-8 byte bound plus executed NUL-body/split-recipient maximal-history witnesses",
        "worst_witness": worst, "rows": rows, "structural_decoded_byte_upper_bound": structural_byte_bound,
        "provider_context_limit": CONTEXT_LIMIT, "output_tokens_including_reasoning": OUTPUT_TOKENS,
        "planning_token_upper_bound": structural_byte_bound + 4096,
        "fits_byte_bound": structural_byte_bound + 4096 + OUTPUT_TOKENS <= CONTEXT_LIMIT,
        "capacity_proven": False,
        "provider_token_count_empirically_verified": False,
        "launch_blocker": "Public byte-level tokenizer/encoding property must be verified and attached before launch; no provider call is made by this check.",
        "byte_bound_assumption": "Selected public model uses byte-level BPE without expanding normalization/prefix spaces: content tokens <= UTF-8 bytes. Two-message provider/template allowance 4096 tokens is reserved separately. No arbitrary tokenizer ratio or truncation is assumed.",
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


def tokenizer_witness(tokenizer_path, runs, encoder_path=None):
    """Optional official public-tokenizer measurement, never an inference call.

    Explicitly a witness rather than a universal/legal-input capacity proof.
    Provider-side prompt encoding/tokenizer equality has not been empirically
    tested here; no provider token/count/generation endpoint is called.
    """
    from pathlib import Path
    from tokenizers import Tokenizer, __version__
    from foundations.contracts import strict_json
    path = Path(tokenizer_path)
    if digest(path.read_bytes()) != TOKENIZER_SHA256:
        from foundations.contracts import Invalid
        raise Invalid("public_model_tokenizer_changed")
    tokenizer = Tokenizer.from_file(str(path))
    encoder = None
    if encoder_path:
        import importlib.util
        source = Path(encoder_path)
        if digest(source.read_bytes()) != ENCODER_SHA256:
            from foundations.contracts import Invalid
            raise Invalid("public_model_encoder_changed")
        module_spec = importlib.util.spec_from_file_location("pinned_public_deepseek_encoding", source)
        encoder = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(encoder)
    rows = []
    for graph in ("P", "R"):
        request_path = Path(runs) / f"maximal-{graph}/requests/Q4-D-A.json"
        raw = request_path.read_bytes()
        body = strict_json(raw)
        counts = [len(tokenizer.encode(m["content"], add_special_tokens=False).ids) for m in body["messages"]]
        row = {"graph": graph, "slot": "Q4-D-A", "request_sha256": digest(raw),
                     "message_content_tokens": sum(counts),
                     "with_conservative_two_message_template_allowance": sum(counts) + 4096}
        if encoder:
            prompt = encoder.encode_messages(body["messages"], thinking_mode="thinking")
            row["reference_full_prompt_tokens"] = len(tokenizer.encode(prompt, add_special_tokens=False).ids)
            row["reference_wrapper_utf8_bytes"] = len(prompt.encode()) - sum(len(m["content"].encode()) for m in body["messages"])
            if not all(m["content"] in prompt for m in body["messages"]):
                from foundations.contracts import Invalid
                raise Invalid("reference_content_changed")
        rows.append(row)
    descriptor = strict_json(path.read_bytes())
    # ByteLevel maps one input byte to one initial symbol; BPE merges can only
    # reduce symbol count. Splits isolate substrings but do not add text. No
    # normalization, prefix space, padding or truncation is accepted here.
    normalizer = descriptor["normalizer"]
    pretokens = descriptor["pre_tokenizer"]["pretokenizers"]
    bytelevel = pretokens[-1]
    byte_bound_valid = (normalizer == {"type": "Sequence", "normalizers": []} and
        descriptor["model"]["type"] == "BPE" and bytelevel["type"] == "ByteLevel" and
        bytelevel["add_prefix_space"] is False and bytelevel["use_regex"] is False and
        all(p["type"] == "Split" and p["behavior"] == "Isolated" and p["invert"] is False for p in pretokens[:-1]) and
        descriptor["truncation"] is None and descriptor["padding"] is None)
    from tokenizers.pre_tokenizers import ByteLevel
    byte_bound_valid &= set(ByteLevel.alphabet()) <= set(descriptor["model"]["vocab"])
    return {"scope": "Executed public-tokenizer witness and verified byte-level content-token upper-bound property; not a live provider token-count measurement",
        "tokenizer_sha256": digest(path.read_bytes()), "tokenizers_version": __version__,
        "reference_encoder_sha256": ENCODER_SHA256 if encoder else None,
        "reference_encoder_source": "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/encoding/encoding.py",
        "reference_wrapper_verified": bool(encoder and all(0 <= r["reference_wrapper_utf8_bytes"] <= 4096 for r in rows)),
        "source": "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/tokenizer.json",
        "rows": rows, "inference_calls": 0, "byte_level_content_bound_verified": byte_bound_valid,
        "provider_token_count_empirically_verified": False}
