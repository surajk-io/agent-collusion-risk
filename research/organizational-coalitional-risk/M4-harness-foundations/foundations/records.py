"""Researcher-only durable records. Never expose this journal to an agent."""
import base64
import hashlib
import os
import tempfile
import subprocess
from pathlib import Path

from .contracts import Invalid, canonical, strict_json


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return {"base64": base64.b64encode(raw).decode("ascii"), "sha256": digest(raw)}


def unblob(value):
    raw = base64.b64decode(value["base64"], validate=True)
    if digest(raw) != value["sha256"]:
        raise Invalid("blob_hash")
    return raw


def provenance(repository, relative_paths):
    """Explicit researcher allowlist; retains bytes, including untracked sources."""
    root = Path(repository).resolve()
    files = {}
    for name in relative_paths:
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise Invalid("provenance_path")
        files[name] = blob(path.read_bytes())
    return {"git_revision": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            "dirty_diff": blob(subprocess.check_output(["git", "diff", "HEAD"], cwd=root)),
            "status": blob(subprocess.check_output(["git", "status", "--porcelain"], cwd=root)),
            "files": files}


class Journal:
    """Single-writer journal, atomic whole-file replacement per event.

    Small foundation logs only. A complete fsynced event is the commit point;
    restart reloads it. No partial batch publication or concurrent writers.
    Hash chaining detects corruption, not malicious rewriting of the entire file.
    """

    def __init__(self, path):
        self.path = Path(path)
        if self.path.exists():
            self._events = strict_json(self.path.read_bytes())
        else:
            self._events = []
        self.verify(self._events)

    @property
    def events(self):
        return self.replay()

    @staticmethod
    def verify(events):
        previous = "0" * 64
        keys = set()
        for index, event in enumerate(events):
            body = {k: v for k, v in event.items() if k != "hash"}
            if (event["index"] != index or event["previous"] != previous
                    or event["hash"] != digest(canonical(body)) or event["key"] in keys):
                raise Invalid("journal_integrity")
            keys.add(event["key"])
            previous = event["hash"]

    def append(self, key, kind, data):
        # Detach from caller-owned mutable dictionaries before persistence.
        data = strict_json(canonical(data))
        for event in self._events:
            if event["key"] == key:
                if event["kind"] != kind or event["data"] != data:
                    raise Invalid("event_conflict")
                return strict_json(canonical(event))
        body = {"index": len(self._events), "previous": self._events[-1]["hash"]
                if self._events else "0" * 64, "key": key, "kind": kind, "data": data}
        event = {**body, "hash": digest(canonical(body))}
        events = self._events + [event]
        fd, temporary = tempfile.mkstemp(dir=self.path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(canonical(events))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            # Even if the directory fsync fails, do not overwrite the new disk
            # state with a stale in-memory prefix on a subsequent append.
            self._events = events
            directory = os.open(self.path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return strict_json(canonical(event))

    def replay(self):
        self.verify(self._events)
        return tuple(strict_json(canonical(self._events)))

    def committed(self, key):
        for event in self.replay():
            if event["key"] == key:
                return event
        raise Invalid("uncommitted_event")
