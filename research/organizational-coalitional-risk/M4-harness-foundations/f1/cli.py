"""Offline validation plus a separately authorized future live execution path."""
import argparse
from dataclasses import replace
from pathlib import Path
import json

from foundations.contracts import AGENTS, Limits, canonical
from foundations.provider import ModelConfig
from .annotation import evaluate, gold_coding, template
from .archive import Archive, inspect
from .materials import Assets, HERE, ORDER, Spec
from .runner import Runner, initial, manifest
from .scripts import Script, TRACES
from .vertex import Reply


def script_spec(graph, namespace="scripted-apparatus"):
    return Spec("release-window-01", graph, namespace,
                canonical({"temperature": 0, "top_p": 1, "max_tokens": 8192,
                           "chat_template_kwargs": {"thinking": True},
                           "response_format": {"type": "json_object"}, "stream": False}),
                180, 393216, 8192, Limits(1024, 2048, True))


def execute(directory, spec, trace="positive", adapter=None, config=None, execution_approval=None):
    assets = Assets()
    config = config or ModelConfig("script", "offline", "offline-fixed-script", spec.generation_json)
    repository = HERE.parents[3]
    origin = {"kind": "live_unseeded" if execution_approval else "scripted_apparatus", "trace": trace}
    frozen = manifest(spec, assets, config, origin, repository)
    if execution_approval:
        frozen.update(live_execution_authorized=True, execution_approval=execution_approval.record)
    archive = Archive(directory, frozen)
    runner = Runner(spec, assets, config, adapter or Script(spec.graph, trace), archive,
                    execution_approval=execution_approval)
    board = runner.run()
    # Default human forms preserve uncertainty. Gold keys are used only on known
    # scripts, never to classify arbitrary text from a target model.
    forms = template(runner.messages, runner.state, spec.reviewers, {a: False for a in AGENTS})
    archive.state("annotation-template", forms, "annotation")
    if adapter is None:
        coding = gold_coding(spec.graph, trace, runner.messages)
        archive.state("script-gold-coding", coding, "annotation")
        archive.state("script-gold-result", evaluate(coding, runner.messages, runner.state,
                                                      spec.reviewers), "annotation")
    archive.event("END", None, "F1_complete", "authorization_and_board_only")
    return runner, board


class Replay:
    scripted = True

    def __init__(self, original):
        self.root = Path(original)
        _, events = inspect(self.root)
        self.representations = {(e["stage"], e["actor"]): e["details"].get("representation")
                                for e in events if e["event"] == "response_received"}
        self.status = {(e["stage"], e["actor"]): e["details"].get("http_status", 200)
                       for e in events if e["event"] == "response_received"}
        self.error_details = {(e["stage"], e["actor"]): e["details"]
                              for e in events if e["event"] == "error_body"}
        self.resolved = {stage: json.loads((self.root / f"states/slot-results-{stage}.json").read_bytes())
                         for stage in ORDER}

    def complete(self, request, timeout):
        key = (request.slot_nonce, request.session.actor)
        name = "-".join(key)
        if request.input_bytes != (self.root / "requests" / (name + ".json")).read_bytes():
            raise ValueError("replay_request_changed")
        resolved = self.resolved[request.slot_nonce][request.session.actor]
        payload_path = self.root / "responses" / (name + ".json")
        if not payload_path.exists():
            from .vertex import CallError
            partial = self.root / "responses" / (name + ".error-body")
            details = self.error_details.get(key, {})
            raise CallError(resolved["error"], partial.read_bytes() if partial.exists() else b"",
                            details.get("representation", "no_response_body"), status=details.get("http_status"))
        return Reply(payload_path.read_bytes(),
                     self.representations[key], self.status[key],
                     json.loads((self.root / "responses" / (name + ".metadata.json")).read_bytes()).get("final_byte"))


def replay(original, target):
    frozen, _ = inspect(original)
    s = frozen["run"]
    spec = Spec(s["run_id"], s["graph"], s["namespace"], canonical(s["generation_json"]),
                s["timeout_seconds"], s["input_token_limit"], s["output_token_limit"], Limits(**s["limits"]))
    model = frozen["model"]
    config = ModelConfig(model["provider"], model["endpoint"], model["model"], canonical(model["settings"]))
    result = execute(target, spec, trace=frozen["origin"]["trace"], adapter=Replay(original), config=config)
    # Compare the whole deterministic commit prefix, not timestamps/completion order.
    for stage in (*ORDER, "deployment", "board"):
        name = "states/" + stage + ".json"
        if (Path(original) / name).read_bytes() != (Path(target) / name).read_bytes():
            raise ValueError("replay_state_changed:" + stage)
    return result


def freeze(directory):
    from .materials import render
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    assets, state = Assets(), initial()
    index = {"status": "Review only; target model/configuration and execution unapproved", "requests": {}}
    for graph in ("P", "R"):
        spec = script_spec(graph, namespace="unseeded-review")
        for actor in AGENTS:
            raw = render(spec, assets, actor, "C1", state, {a: [] for a in AGENTS}, {a: [] for a in AGENTS})
            name = graph + "-C1-" + actor + ".json"
            (root / name).write_bytes(raw)
            from foundations.records import digest
            index["requests"][name] = digest(raw)
    (root / "index.json").write_bytes(canonical(index))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    script = commands.add_parser("script")
    script.add_argument("--graph", choices=("P", "R"), required=True)
    script.add_argument("--trace", choices=TRACES, default="positive")
    script.add_argument("--out", required=True)
    replay_command = commands.add_parser("replay")
    replay_command.add_argument("--run", required=True)
    replay_command.add_argument("--out", required=True)
    frozen = commands.add_parser("freeze")
    frozen.add_argument("--out", required=True)
    preflight = commands.add_parser("preflight")
    preflight.add_argument("--out", required=True)
    live = commands.add_parser("live", help="requires separately recorded researcher authorization")
    live.add_argument("--graph", choices=("P", "R"), required=True)
    live.add_argument("--out", required=True)
    live.add_argument("--approval", required=True)
    args = parser.parse_args()
    if args.command == "script":
        _, board = execute(args.out, script_spec(args.graph), args.trace)
        print(json.dumps({"archive": str(Path(args.out).resolve()), "board": board}, indent=2))
    elif args.command == "replay":
        replay(args.run, args.out)
        print("Verified byte-identical requests and committed states; no model call.")
    elif args.command == "preflight":
        from .preflight import generate
        summary = generate(args.out)
        print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    elif args.command == "live":
        from .live import execute_live
        execute_live(args.out, args.graph, args.approval)
    else:
        freeze(args.out)
        print("Frozen first P/R C1 requests for all four actors; review only.")


if __name__ == "__main__":
    main()
