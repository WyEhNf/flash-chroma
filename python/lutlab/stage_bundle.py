"""Byte-preserving assembly of independently fitted stages, including mixed m.

This is a provenance protocol, not a fitter. Each selected stage must occupy the
same position in a verified four-source parent chain. Copies of parent manifests
make the stage/source relation inspectable without changing the SLUT format.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import tempfile

from . import cache, io

KIND = "independent_stage_bundle_v1"


@dataclass
class Bundle:
    directory: Path
    paths: list[Path]
    manifest: dict


def inspect_bundle(directory):
    directory = Path(directory)
    try:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        identity = manifest["identity"]
        parameters = identity["parameters"]
        if (manifest["kind"] != KIND or manifest["schema_version"] != 2
                or manifest["identity_sha256"] != cache.identity_key(identity)
                or parameters["n_stages"] != 4 or parameters["semantics"] != "independent"
                or parameters["interpolation_basis"] != "tetra_q16"
                or len(identity["inputs"]) != 4 or len({row["sha256"] for row in identity["inputs"]}) != 4
                or len(identity["parents"]) != 4 or len(manifest["models"]) != 4
                or len(parameters["m"]) != 4):
            return None
        names = [f"stage{stage}.slut" for stage in range(1, 5)]
        if sorted(path.name for path in directory.glob("*.slut")) != names:
            return None
        paths = []
        for stage, (name, parent, record, m) in enumerate(zip(names, identity["parents"], manifest["models"], parameters["m"]), 1):
            if parent["stage"] != stage or parent["file"] != f"parents/stage{stage}-manifest.json" or record["file"] != name:
                return None
            path = directory / name
            parent_path = directory / parent["file"]
            if cache.file_sha256(parent_path) != parent["manifest_sha256"]:
                return None
            original = json.loads(parent_path.read_text(encoding="utf-8"))
            original_identity = original["identity"]
            original_parameters = original_identity["parameters"]
            if (original["schema_version"] != cache.SCHEMA_VERSION
                    or original["identity_sha256"] != cache.identity_key(original_identity)
                    or original["identity_sha256"] != parent["identity_sha256"]
                    or original_identity["inputs"] != identity["inputs"]
                    or original_parameters["n_stages"] != 4 or original_parameters["semantics"] != "independent"
                    or original_parameters["interpolation_basis"] != "tetra_q16"
                    or original_parameters["m"] != m or len(original["models"]) != 4):
                return None
            selected = original["models"][stage - 1]
            if (selected["file"] != name or selected["sha256"] != record["sha256"]
                    or selected["m"] != m or record["m"] != m
                    or selected["bytes"] != record["bytes"] or path.stat().st_size != record["bytes"]
                    or cache.file_sha256(path) != record["sha256"] or io.load_sparse(path, competition=True).m != m):
                return None
            paths.append(path.resolve())
        return Bundle(directory.resolve(), paths, manifest)
    except (OSError, ValueError, KeyError, TypeError, OverflowError):
        return None


def assemble(paths, destination):
    paths = [Path(path).resolve() for path in paths]
    if len(paths) != 4:
        raise ValueError("stage assembly requires exactly four ordered model paths")
    originals = []
    inputs = None
    payloads = []
    for stage, path in enumerate(paths, 1):
        payload = (path.parent / "manifest.json").read_bytes()
        original = json.loads(payload)
        parent = cache.inspect_entry(path.parent, original["identity"])
        if parent is None or parent.paths[stage - 1].resolve() != path:
            raise ValueError("selected stage is not in its own position in a verified original four-stage fit")
        parameters = original["identity"]["parameters"]
        if parameters["semantics"] != "independent" or parameters["interpolation_basis"] != "tetra_q16":
            raise ValueError("mixed stage assembly requires independent tetra_q16 parent fits")
        current_inputs = original["identity"]["inputs"]
        if inputs is not None and inputs != current_inputs:
            raise ValueError("selected parents belong to different ordered original source chains")
        inputs = current_inputs
        originals.append((original, payload))
        payloads.append(path.read_bytes())
    if len(inputs) != 4 or len({row["sha256"] for row in inputs}) != 4:
        raise ValueError("four distinct original source hashes required")
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError("preserve the existing bundle")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".stage-bundle-", dir=destination.parent)).resolve()
    try:
        (temporary / "parents").mkdir()
        parents = []
        records = []
        sizes = []
        for stage, (path, payload, (original, original_payload)) in enumerate(zip(paths, payloads, originals), 1):
            name = f"stage{stage}.slut"
            target = temporary / name
            target.write_bytes(payload)
            parent_file = f"parents/stage{stage}-manifest.json"
            (temporary / parent_file).write_bytes(original_payload)
            m = io.load_sparse(target, competition=True).m
            sizes.append(m)
            parents.append({"stage": stage, "file": parent_file,
                            "manifest_sha256": cache.file_sha256(temporary / parent_file),
                            "identity_sha256": original["identity_sha256"]})
            records.append({"file": name, "sha256": cache.file_sha256(target), "bytes": len(payload), "m": m})
        identity = {"schema_version": 2, "inputs": inputs, "parents": parents,
                    "parameters": {"mode": "seq", "method": "independent_stage_bundle", "grid": "per_stage",
                                   "m": sizes, "n_stages": 4, "semantics": "independent", "interpolation_basis": "tetra_q16"},
                    "source_sha256": {"python/lutlab/stage_bundle.py": cache.file_sha256(Path(__file__))},
                    "format": {"version": 1, "stage_io": "uint8 RGB after every mapping", "axis_tables": "serialized authoritative"}}
        manifest = {"kind": KIND, "schema_version": 2, "identity": identity,
                    "identity_sha256": cache.identity_key(identity), "models": records,
                    "fit": {"operation": "select and copy existing independent stages", "new_fits": 0}}
        (temporary / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if inspect_bundle(temporary) is None:
            raise RuntimeError("assembled stage bundle failed provenance validation")
        for path, payload, (original, original_payload) in zip(paths, payloads, originals):
            if path.read_bytes() != payload or (path.parent / "manifest.json").read_bytes() != original_payload:
                raise RuntimeError("selected parent changed during assembly")
        temporary.rename(destination)
        result = inspect_bundle(destination)
        if result is None:
            raise RuntimeError("published bundle failed validation")
        return result
    finally:
        if temporary.exists():
            if temporary.parent != destination.parent or not temporary.name.startswith(".stage-bundle-"):
                raise RuntimeError("refusing cleanup outside this assembly's temporary directory")
            shutil.rmtree(temporary)
