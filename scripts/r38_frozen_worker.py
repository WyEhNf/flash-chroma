"""Run the unchanged R29 numerical driver with a declared JSON I/O overlay.

No frozen source file, fitter function/default, model identity, native kernel or
pixel calculation is edited. Only entry._write_report is replaced in memory by
the independently hashed bounded-retry publisher. Phase reports disclose both
overlay source hashes; the original numerical frozen fingerprint is retained.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import runpy
import sys


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--reportio", type=Path, required=True)
    parser.add_argument("--reportio-sha256", required=True)
    args, forwarded = parser.parse_known_args()
    source_root = args.source_root.resolve()
    io_path = args.reportio.resolve()
    if digest(io_path) != args.reportio_sha256:
        raise RuntimeError("declared I/O overlay changed before execution")
    spec = importlib.util.spec_from_file_location("jshc_declared_reportio_overlay", io_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    wrapper = Path(__file__).resolve()
    wrapper_hash = digest(wrapper)
    overlay = {"wrapper": str(wrapper), "wrapper_sha256": wrapper_hash,
               "reportio": str(io_path), "reportio_sha256": args.reportio_sha256,
               "scope": "JSON publication retry only; numerical fitter and native byte fingerprints unchanged"}
    sys.path.insert(0, str(source_root / "python"))
    sys.path.insert(1, str(source_root))
    from lutlab import entry
    def publish(path, value):
        if isinstance(value, dict) and "frozen" in value and "observations" in value:
            value.setdefault("execution_io_overlays", {})[wrapper_hash] = overlay
        module.write_report(path, value)
    entry._write_report = publish
    driver = source_root / "scripts/r29_strategy_matrix.py"
    sys.argv = [str(driver), *forwarded]
    runpy.run_path(str(driver), run_name="__main__")
    if digest(io_path) != args.reportio_sha256 or digest(wrapper) != wrapper_hash:
        raise RuntimeError("I/O overlay changed during execution")


if __name__ == "__main__":
    main()
