"""All default commands are offline; live requires a separate frozen approval."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
from foundations.contracts import AGENTS, canonical
from foundations.records import digest
from .annotation import evaluate, script_coding, outcomes, template
from .contracts import Spec
from .fixtures import inventory, verify
from .materials import visible
from .preflight import allocation, capacity_report, launch_proposal
from .replay import replay
from .runner import execute
from .scripts import Script, TRACES


def script(directory, spec, trace):
    runner = execute(directory, spec, Script(trace), trace)
    runner.archive.state("annotation-template", template(runner), "ANNOTATION")
    coding = script_coding(runner)
    runner.archive.state("script-gold-coding", coding, "ANNOTATION")
    result = evaluate(runner, coding)
    runner.archive.state("script-gold-result", result, "ANNOTATION")
    runner.archive.state("outcomes", outcomes(runner), "ANALYSIS")
    return runner, result


def validate(directory):
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    rows, runners = [], []
    for pair in allocation():
        for graph in pair["graphs"]:
            spec = Spec(graph=graph, condition=pair["condition"], block=pair["block"])
            runner, label = script(root / spec.episode, spec, "positive")
            replay(runner.archive.root, root / (spec.episode + "-replay"))
            result = outcomes(runner)
            assert result["qualified_throughput"] == 4 and result["q0_deployed"] == 12 and result["v1_deployed"] == 6
            assert label["primary"] is (True if spec.messaging else None)
            rows.append({"spec": asdict(spec), "outcomes": result, "annotation": label, "replay": "byte-identical"})
            runners.append(runner)
    negative = []
    for graph in ("P", "R"):
        for trace in ("independent", "cooperation", "same-round", "defection", "invalid", "timeout", "stale", "hold", "withhold"):
            runner, label = script(root / f"negative-{graph}-{trace}", Spec(graph=graph), trace)
            replay(runner.archive.root, root / f"negative-{graph}-{trace}-replay")
            assert label["primary"] is False
            negative.append({"graph": graph, "trace": trace, "outcomes": outcomes(runner), "annotation": label})
    maximal = []
    for graph in ("P", "R"):
        runner, _ = script(root / f"maximal-{graph}", Spec(graph=graph), "maximal")
        assert all(r["disposition"] == "valid" for receipts in runner.receipts.values() for r in receipts)
        maximal.append(runner)
    capacity = capacity_report(maximal)
    report = {"scope": "Offline apparatus validation; no behavioral inference", "matrix": rows,
              "negative_traces": negative, "capacity": capacity,
              "calls_in_matrix": 1792, "no_live_calls": True}
    (root / "validation.json").write_bytes(canonical(report))
    # Truth is researcher-only. Four source distributions/quarter, two templates.
    fixtures = {str(block): {f"{q}-{a}": {"candidate_hash": r.candidate_hash,
                    "source": json.loads(r.source_json), "evidence": json.loads(r.evidence_json),
                    "oracle": json.loads(r.oracle_json), "qualified": r.qualified,
                    "vulnerable": r.vulnerable, "verified": verify(r)} for (q, a), r in inventory(block).items()}
                for block in (1, 2)}
    (root / "fixture-evidence.json").write_bytes(canonical(fixtures))
    return report, runners


def package(directory, validation_directory, tokenizer_path=None, encoder_path=None):
    root = Path(directory)
    report, runners = validate(validation_directory)
    root.mkdir(parents=True, exist_ok=False)
    summaries = {k: v for k, v in report.items() if k != "capacity"}
    capacity = report["capacity"]
    if tokenizer_path:
        from .preflight import tokenizer_witness
        proof = tokenizer_witness(tokenizer_path, validation_directory, encoder_path)
        (root / "tokenizer-proof.json").write_bytes(canonical(proof))
        capacity["public_tokenizer_byte_bound_verified"] = proof["byte_level_content_bound_verified"]
        capacity["tokenizer_sha256"] = proof["tokenizer_sha256"]
        capacity["capacity_proven"] = capacity["fits_byte_bound"] and proof["byte_level_content_bound_verified"] and proof["reference_wrapper_verified"]
        capacity["launch_blocker"] = None if capacity["capacity_proven"] else capacity["launch_blocker"]
    (root / "validation.json").write_bytes(canonical(summaries))
    (root / "capacity.json").write_bytes(canonical(capacity))
    (root / "allocation.json").write_bytes(canonical(allocation()))
    (root / "fixture-evidence.json").write_bytes((Path(validation_directory) / "fixture-evidence.json").read_bytes())
    from .budget import report as budget_report
    tokenizer = None
    if tokenizer_path:
        from tokenizers import Tokenizer
        tokenizer = Tokenizer.from_file(str(tokenizer_path))
    (root / "budget-proof.json").write_bytes(canonical(budget_report(runners, validation_directory, tokenizer)))
    from .manual import demo
    demo_root = Path(validation_directory) / "manual-demo"
    demo(demo_root)
    (root / "manual-demo-summary.json").write_bytes((demo_root / "demo-summary.json").read_bytes())
    for case in sorted(p for p in demo_root.iterdir() if p.is_dir()):
        bundle = {"scope": "Known scripted apparatus annotations; not human-reviewed subject behavior",
            "delivered": json.loads((case / "review/delivered.json").read_bytes()),
            "reviewer_one": json.loads((case / "script-reviewer-one.json").read_bytes()),
            "reviewer_two": json.loads((case / "script-reviewer-two.json").read_bytes()),
            "episode_result": json.loads((case / "result/episode-result.json").read_bytes())}
        (root / ("manual-" + case.name + ".json")).write_bytes(canonical(bundle))
        (root / ("manual-" + case.name + "-components.csv")).write_bytes((case / "result/components.csv").read_bytes())
    for runner in runners:
        if runner.spec.block != 1:
            continue
        for q, stage in ((1, "C1"), (2, "S"), (3, "D")):
            name = f"{runner.spec.condition}-{runner.spec.graph}-Q{q}-{stage}-A"
            raw = (runner.archive.root / f"requests/Q{q}-{stage}-A.json").read_bytes()
            (root / (name + ".json")).write_bytes(raw)
            request = json.loads(raw)
            (root / (name + ".md")).write_text("Scripted apparatus example; not a subject transcript.\n\n" +
                request["messages"][0]["content"] + "\n\n```json\n" + json.dumps(visible(raw), ensure_ascii=False, indent=2) + "\n```\n")
    from .collection import resume_proposal
    (root / "resume-approval.proposed.json").write_bytes(canonical(resume_proposal()))
    index = {p.name: digest(p.read_bytes()) for p in sorted(root.iterdir()) if p.is_file()}
    (root / "index.json").write_bytes(canonical(index))
    proposal = launch_proposal(digest(canonical(index)))
    (root / "execution-approval.proposed.json").write_bytes(canonical(proposal))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("script")
    s.add_argument("--graph", choices=("P", "R"), required=True)
    s.add_argument("--condition", choices=AGENTS, default="A")
    s.add_argument("--block", type=int, choices=(1, 2), default=1)
    s.add_argument("--seed", type=int, default=20261026)
    s.add_argument("--trace", choices=TRACES, default="positive")
    s.add_argument("--out", required=True)
    r = sub.add_parser("replay")
    r.add_argument("--run", required=True); r.add_argument("--out", required=True)
    r.add_argument("--reconcile-interrupted", action="store_true")
    v = sub.add_parser("validate")
    v.add_argument("--out", required=True)
    p = sub.add_parser("package")
    p.add_argument("--out", required=True); p.add_argument("--runs", required=True)
    p.add_argument("--tokenizer", help="optional pinned public tokenizer; no inference")
    p.add_argument("--encoder", help="optional pinned public encoding reference; no inference")
    t = sub.add_parser("tokenizer-witness")
    t.add_argument("--tokenizer", required=True); t.add_argument("--runs", required=True)
    t.add_argument("--encoder")
    t.add_argument("--out", required=True)
    live = sub.add_parser("live")
    live.add_argument("--approval", required=True); live.add_argument("--package", required=True)
    live.add_argument("--out", required=True)
    live.add_argument("--resume-approval", help="explicit authorization for exactly the next frozen pair")
    for command in ("annotate-export", "annotate-check", "annotate-resolve", "annotate-demo"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("--out", required=True)
        if command != "annotate-demo": command_parser.add_argument("--run", required=True)
        if command == "annotate-check": command_parser.add_argument("--review", required=True)
        if command == "annotate-resolve":
            command_parser.add_argument("--review-one", required=True)
            command_parser.add_argument("--review-two", required=True)
            command_parser.add_argument("--adjudication")
    args = parser.parse_args()
    if args.command == "script":
        runner, label = script(args.out, Spec(graph=args.graph, condition=args.condition, block=args.block, seed=args.seed), args.trace)
        print(json.dumps({"outcomes": outcomes(runner), "annotation": label}, indent=2))
    elif args.command == "replay":
        replay(args.run, args.out, args.reconcile_interrupted)
        print("Verified committed prefix and reconstructed exact requests offline.")
    elif args.command == "validate":
        report, _ = validate(args.out)
        print(json.dumps({"matrix_episodes": len(report["matrix"]), "negative_traces": len(report["negative_traces"]),
                          "capacity_proven": report["capacity"]["capacity_proven"]}, indent=2))
    elif args.command == "package":
        report = package(args.out, args.runs, args.tokenizer, args.encoder)
        print(json.dumps({"package": str(Path(args.out).resolve()), "no_live_calls": True,
                          "capacity_proven": report["capacity"]["capacity_proven"]}, indent=2))
    elif args.command == "tokenizer-witness":
        from .preflight import tokenizer_witness
        result = tokenizer_witness(args.tokenizer, args.runs, args.encoder)
        with Path(args.out).open("xb") as stream:
            stream.write(canonical(result))
        print(json.dumps(result, indent=2))
    elif args.command.startswith("annotate-"):
        from . import manual
        if args.command == "annotate-export":
            result = manual.export(args.run, args.out)
            print(f"Exported {len(result['messages'])} authenticated delivered messages; no provider reasoning.")
        elif args.command == "annotate-check":
            print(json.dumps(manual.check(args.run, args.review, args.out), indent=2))
        elif args.command == "annotate-resolve":
            print(json.dumps(manual.resolve(args.run, args.review_one, args.review_two, args.out, args.adjudication), indent=2))
        else:
            print(json.dumps(manual.demo(args.out), indent=2))
    else:
        from .live import execute_live
        result = execute_live(args.out, args.package, args.approval, args.resume_approval)
        print(json.dumps(result, indent=2))
        if result["status"].startswith("blocked"):
            raise SystemExit(2)


if __name__ == "__main__":
    main()
