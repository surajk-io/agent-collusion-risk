#!/usr/bin/env python3
"""One minimal real OpenRouter GPT-OSS request with reasoning visibility checks.

This is an inference smoke test, not a research episode. It fails loudly if the
provider returns no meaningful reasoning trace or if the final JSON cannot be
extracted. It never prints or stores the API key.
"""
import argparse
import json
import os
from pathlib import Path
import sys

from run import extract_field, load_local_env, make_api_chat
from vertex_backends import Completion


def main(argv=None):
    load_local_env()
    parser = argparse.ArgumentParser(description="Minimal OpenRouter reasoning smoke test")
    parser.add_argument("--model", default="openai/gpt-oss-120b")
    parser.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--out", default="results/openrouter-reasoning-smoke.json")
    args = parser.parse_args(argv)

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is not set. Export it in your shell; never commit it.", file=sys.stderr)
        return 2

    chat = make_api_chat(
        "openrouter", args.model, 0.2, args.max_tokens,
        reasoning_effort=args.effort,
    )
    system = "You are a smoke-test assistant. Think carefully before answering."
    prompt = (
        "Compute (17 * 23 - 19) / 4 step by step. Then return exactly one JSON "
        'object with no prose outside it: {"answer": <number>, "status": "ok"}.'
    )
    reply = chat(system, prompt)
    if isinstance(reply, Completion):
        content = reply.text
        metadata = reply.metadata
    else:
        content = reply
        metadata = {}

    reasoning = metadata.get("reasoning_text") or metadata.get("reasoning")
    reasoning_details = metadata.get("reasoning_details")
    meaningful_reasoning = isinstance(reasoning, str) and len(reasoning.strip()) >= 40
    try:
        answer = extract_field(content, "answer")
        status = extract_field(content, "status")
    except ValueError as exc:
        answer = None
        status = None
        extraction_error = str(exc)
    else:
        extraction_error = None

    artifact = {
        "smoke_test": True,
        "not_a_research_episode": True,
        "provider": metadata.get("provider", "OpenRouter"),
        "requested_model": args.model,
        "served_model": metadata.get("served_model"),
        "reasoning_effort": args.effort,
        "max_tokens": args.max_tokens,
        "system_prompt": system,
        "user_prompt": prompt,
        "final_content": content,
        "extracted_answer": answer,
        "extracted_status": status,
        "extraction_error": extraction_error,
        "reasoning_returned": bool(reasoning_details) or bool(reasoning),
        "reasoning_meaningful": meaningful_reasoning,
        "reasoning_characters": len(reasoning.strip()) if isinstance(reasoning, str) else 0,
        "reasoning": reasoning,
        "reasoning_details": reasoning_details,
        "finish_reason": metadata.get("finish_reason"),
        "usage": metadata.get("usage"),
        "cost_usd": metadata.get("cost_usd"),
        "response_id": metadata.get("response_id"),
        "response_metadata": metadata.get("response_metadata"),
        "api_settings": metadata.get("api_settings"),
    }
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"requested model: {args.model}")
    print(f"served model:    {metadata.get('served_model')}")
    print(f"provider:        {metadata.get('provider')}")
    print(f"final content:   {content!r}")
    print(f"extracted:       answer={answer!r} status={status!r}")
    print(f"reasoning chars: {artifact['reasoning_characters']}")
    print(f"finish reason:   {metadata.get('finish_reason')}")
    print(f"usage:           {json.dumps(metadata.get('usage'), ensure_ascii=False)}")
    print(f"cost:            {metadata.get('cost_usd')}")
    print(f"saved:           {path}")

    if not meaningful_reasoning:
        print(
            "FAIL: no meaningful reasoning text was returned. Inspect OpenRouter's "
            "current reasoning and provider-routing documentation before running "
            "episodes; do not substitute a different model or claim trace capture.",
            file=sys.stderr,
        )
        print("Docs: https://openrouter.ai/docs/guides/best-practices/reasoning-tokens", file=sys.stderr)
        print("Docs: https://openrouter.ai/docs/features/provider-routing", file=sys.stderr)
        return 3
    if extraction_error or answer != 93 or status != "ok":
        print(f"FAIL: final JSON was not extracted correctly: {extraction_error}", file=sys.stderr)
        return 4
    print("PASS: meaningful reasoning and final JSON were both captured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
