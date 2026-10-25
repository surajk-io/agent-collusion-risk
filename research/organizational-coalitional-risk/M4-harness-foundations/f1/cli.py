"""Offline scripts/replay/freeze only. No live execution entry point."""
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
                canonical({"temperature": 0, "candidateCount": 1,
                           "maxOutputTokens": 4096, "responseMimeType": "application/json"}),
                180, 65536, 4096, Limits(1024, 2048, True))


def execute(directory, spec, trace="positive", adapter=None, config=None):
    assets = Assets()
    config = config or ModelConfig("script", "offline", "offline-fixed-script", spec.generation_json)
    repository = HERE.parents[3]
    archive = Archive(directory, manifest(spec, assets, config,
                                         {"kind": "scripted_apparatus", "trace": trace}, repository))
    runner = Runner(spec, assets, config, adapter or Script(spec.graph, trace), archive)
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
        self.resolved = {stage: json.loads((self.root / f"states/slot-results-{stage}.json").read_bytes())
                         for stage in ORDER}

    def complete(self, request, timeout):
        key = (request.slot_nonce, request.session.actor)
        name = "-".join(key)
        if request.input_bytes != (self.root / "requests" / (name + ".json")).read_bytes():
            raise ValueError("replay_request_changed")
        resolved = self.resolved[request.slot_nonce][request.session.actor]
        if resolved["error"]:
            from .vertex import CallError
            raise CallError(resolved["error"])
        return Reply((self.root / "responses" / (name + ".json")).read_bytes(),
                     self.representations[key], self.status[key])


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
    args = parser.parse_args()
    if args.command == "script":
        _, board = execute(args.out, script_spec(args.graph), args.trace)
        print(json.dumps({"archive": str(Path(args.out).resolve()), "board": board}, indent=2))
    elif args.command == "replay":
        replay(args.run, args.out)
        print("Verified byte-identical requests and committed states; no model call.")
    else:
        freeze(args.out)
        print("Frozen first P/R C1 requests for all four actors; review only.")


if __name__ == "__main__":
    main()
