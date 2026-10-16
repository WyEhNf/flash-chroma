"""Atomic JSON publication with bounded Windows sharing retries.

Only persistence changes here. A short-lived sharing/antivirus conflict may be
retried for at most five seconds; other errors propagate. Never switch to a
non-atomic truncate/write fallback, or suppress a failed publication.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import time


def read_text(path, *, encoding="utf-8", errors="strict"):
    """Close the file handle before decoding/parsing the complete snapshot.

    Windows MoveFileEx replacement can still reject even a SHARE_DELETE reader;
    do not promise POSIX replacement of an opened target. The writer retries.
    """
    with Path(path).open("rb") as stream:
        payload = stream.read()
    return payload.decode(encoding, errors=errors)


def read_json(path):
    return json.loads(read_text(path))


def write_report(path, value, *, retry_events=None):
    if path is None:
        return
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                prefix=destination.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
        started = time.monotonic()
        deadline = started + 5.
        delay = .005
        while True:
            try:
                os.replace(temporary, destination)
                break
            except PermissionError as error:
                remaining = deadline - time.monotonic()
                if os.name != "nt" or getattr(error, "winerror", None) not in (5, 32, 33) or remaining <= 0:
                    raise
                if retry_events is not None:
                    retry_events.append({"winerror": error.winerror, "elapsed_seconds": time.monotonic() - started})
                time.sleep(min(delay, remaining))
                delay = min(.1, delay * 2)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
