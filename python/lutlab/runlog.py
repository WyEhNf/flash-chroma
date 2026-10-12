"""Independent run-log store.

Every experiment/benchmark run writes into `logs/` which is its *own* git repository
(ignored by the main repo). Rolling back or resetting the code repo therefore never
touches the logs, and each log entry records the exact code commit + dirty diff hash
that produced it.

Layout:
  logs/index.jsonl                      one summary line per run (append-only)
  logs/runs/<UTCstamp>-<name>-<id>/     run.json, stdout.log, extra artifacts
Usage:
  with Run("fit", params) as run: ...; run.metrics.update(...)
  python -m lutlab.runlog list [-n 20] | show <id-prefix>
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io as _io
import json
import os
import platform
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOGS = Path(os.environ.get("JSHC_LOG_DIR", ROOT / "logs"))


def _git(*args, cwd=ROOT) -> str:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def _ensure_repo() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    if not (LOGS / ".git").exists():
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=LOGS)
        subprocess.run(["git", "config", "user.name", "jshc-runlog"], cwd=LOGS)
        subprocess.run(["git", "config", "user.email", "runlog@localhost"], cwd=LOGS)
        (LOGS / "README.md").write_text("Run logs for problem 16 (independent repo, see the main project's docs/LOGGING.md).\n")


def _cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor()


def environment() -> dict:
    diff = _git("diff", "HEAD")
    return {
        "commit": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no")),
        "diff_sha": hashlib.sha256(diff.encode()).hexdigest()[:12] if diff else None,
        "host": platform.node(), "cpu": _cpu_model(), "nproc": os.cpu_count(),
        "python": sys.version.split()[0], "platform": platform.platform(),
    }


class _Tee(_io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
            st.flush()
        return len(s)

    def flush(self):
        for st in self.streams:
            st.flush()


class Run:
    def __init__(self, name: str, params: dict | None = None, commit_logs: bool = True):
        self.name = name
        self.params = params or {}
        self.metrics: dict = {}
        self.commit_logs = commit_logs
        self.id = uuid.uuid4().hex[:8]
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.dir = LOGS / "runs" / f"{stamp}-{name}-{self.id}"

    def __enter__(self):
        _ensure_repo()
        self.dir.mkdir(parents=True, exist_ok=True)
        self.t0 = time.time()
        self.start = dt.datetime.now(dt.timezone.utc).isoformat()
        if diff := _git("diff", "HEAD"):
            (self.dir / "code.diff").write_text(diff)
        self._log = open(self.dir / "stdout.log", "w")
        self._old = sys.stdout
        sys.stdout = _Tee(self._old, self._log)
        print(f"[runlog] {self.name} {self.id} -> {self.dir.relative_to(ROOT) if self.dir.is_relative_to(ROOT) else self.dir}")
        return self

    def path(self, name: str) -> Path:
        return self.dir / name

    def __exit__(self, et, ev, tb):
        sys.stdout = self._old
        self._log.close()
        rec = {
            "id": self.id, "name": self.name, "status": "ok" if et is None else f"error: {et.__name__}: {ev}",
            "start": self.start, "seconds": round(time.time() - self.t0, 3), "argv": sys.argv,
            "params": self.params, "metrics": self.metrics, "env": environment(),
            "dir": str(self.dir.relative_to(LOGS)),
        }
        (self.dir / "run.json").write_text(json.dumps(rec, indent=1, default=str))
        with open(LOGS / "index.jsonl", "a") as f:
            f.write(json.dumps({k: rec[k] for k in ("id", "name", "status", "start", "seconds", "params", "metrics", "dir")}
                               | {"commit": rec["env"]["commit"][:10], "dirty": rec["env"]["dirty"]}, default=str) + "\n")
        if self.commit_logs:
            subprocess.run(["git", "add", "-A"], cwd=LOGS, capture_output=True)
            subprocess.run(["git", "commit", "-q", "-m", f"{self.name} {self.id} ({rec['status'][:40]})"],
                           cwd=LOGS, capture_output=True)
        return False


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="runlog")
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list")
    l.add_argument("-n", type=int, default=30)
    l.add_argument("--name")
    s = sub.add_parser("show")
    s.add_argument("id")
    a = ap.parse_args(argv)
    idx = LOGS / "index.jsonl"
    rows = [json.loads(x) for x in idx.read_text().splitlines()] if idx.exists() else []
    if a.cmd == "list":
        if a.name:
            rows = [r for r in rows if r["name"] == a.name]
        for r in rows[-a.n:]:
            m = ", ".join(f"{k}={v}" for k, v in list(r["metrics"].items())[:4] if not isinstance(v, (dict, list)))
            print(f"{r['start'][:19]} {r['id']} {r['name']:<14} {r['status'][:10]:<10} {r['commit']}{'*' if r['dirty'] else ''} {m}")
    else:
        for r in rows:
            if r["id"].startswith(a.id):
                print((LOGS / r["dir"] / "run.json").read_text())


if __name__ == "__main__":
    _main(sys.argv[1:])
