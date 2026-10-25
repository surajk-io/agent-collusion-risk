"""Single-run, live-inspectable archive; provider headers/credentials never enter."""
import os
import threading
from pathlib import Path

from foundations.contracts import Invalid, canonical, strict_json
from foundations.provider import now
from foundations.records import digest


def durable(path, raw):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Archive:
    def __init__(self, directory, manifest):
        self.root = Path(directory)
        self.root.mkdir(parents=True, exist_ok=False)
        for name in ("requests", "responses", "states"):
            (self.root / name).mkdir()
        durable(self.root / "manifest.json", canonical(manifest))
        self._lock = threading.RLock()
        self._index = 0
        self._previous = "0" * 64
        self.event("S0", None, "manifest", "recorded", {"manifest.json": digest(canonical(manifest))})

    def event(self, stage, actor, kind, disposition, files=None, details=None):
        with self._lock:
            event = {"index": self._index, "previous": self._previous,
                     "stage": stage, "actor": actor, "event": kind,
                     "timestamp": now(), "disposition": disposition,
                     "files": files or {}, "details": details or {}}
            event["hash"] = digest(canonical(event))
            with (self.root / "events.jsonl").open("ab") as stream:
                stream.write(canonical(event) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
            self._index += 1
            self._previous = event["hash"]
            return event

    def artifact(self, relative, raw, stage, actor, kind, disposition, details=None):
        with self._lock:
            path = self.root / relative
            if path.exists():
                raise Invalid("artifact_exists")
            durable(path, raw)
            return self.event(stage, actor, kind, disposition,
                              {relative: digest(raw)}, details)

    def state(self, name, value, stage):
        return self.artifact("states/" + name + ".json", canonical(value),
                             stage, None, "state_commit", "committed")


def inspect(directory):
    root = Path(directory)
    raw = (root / "events.jsonl").read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise Invalid("incomplete_event_tail")
    events, previous = [], "0" * 64
    for index, line in enumerate(raw.splitlines()):
        event = strict_json(line)
        stored = event.pop("hash")
        if event["index"] != index or event["previous"] != previous or digest(canonical(event)) != stored:
            raise Invalid("event_integrity")
        for relative, expected in event["files"].items():
            path = (root / relative).resolve()
            if not path.is_relative_to(root.resolve()) or digest(path.read_bytes()) != expected:
                raise Invalid("artifact_integrity")
        event["hash"] = stored
        events.append(event)
        previous = stored
    return strict_json((root / "manifest.json").read_bytes()), events
