"""One integration check for model identity, integrity, and atomic batch publication."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace

import numpy as np
import pytest

from lutlab import box, cache, cli, fit, fullfit, io, selection


def test_verified_cache_contract_and_concurrent_batches(tmp_path: Path, monkeypatch):
    # Small files exercise identity hashing only. This control does not claim
    # to fit full input LUTs; all published sparse files are valid real SLUTs.
    sources = [tmp_path / f"source-{stage}.control" for stage in range(4)]
    for stage, path in enumerate(sources):
        path.write_bytes(bytes([stage]) * 256)
    args = SimpleNamespace(scenario="control", mode="seq", method="sample", m=17, adaptive=False)
    parameters = cli.fit_parameters(args)
    identity = cache.build_identity(sources, parameters)
    variant = tmp_path / "models"

    def chain(base):
        return [io.SparseLut(io.uniform_grid(17), np.full((17, 17, 17, 3), base + stage, np.uint8))
                for stage in range(4)]

    original = cache.publish(variant, identity, chain(10), {"fit_s": 0.0})
    assert cache.lookup(variant, identity).paths == original.paths
    assert io.inspect_submission_contract(original.paths)["pass"]
    assert io.inspect_submission_contract(original.paths)["semantics_evidence"] == "verified_model_manifest"
    assert not io.inspect_submission_contract(original.paths[:3])["pass"]
    assert not io.inspect_submission_contract(original.paths, semantics="residual")["pass"]

    changed_parameters = deepcopy(parameters)
    changed_parameters["grid"] = "error"
    assert cache.lookup(variant, cache.build_identity(sources, changed_parameters)) is None
    sources[0].write_bytes(bytes([7]) * 256)
    assert cache.lookup(variant, cache.build_identity(sources, parameters)) is None
    sources[0].write_bytes(bytes([0]) * 256)
    source_versions = cache.source_fingerprint()
    with monkeypatch.context() as patch:
        patch.setattr(cache, "source_fingerprint", lambda: {**source_versions, "test-version": "new"})
        assert cache.lookup(variant, cache.build_identity(sources, parameters)) is None

    original.paths[0].write_bytes(b"SLUT")
    assert cache.lookup(variant, identity) is None
    repaired = cache.publish(variant, identity, chain(20), {"fit_s": 0.0})
    assert repaired.directory != original.directory
    assert original.paths[0].read_bytes() == b"SLUT"  # old evidence is preserved
    repaired.paths[1].unlink()
    assert cache.lookup(variant, identity) is None

    concurrent_variant = tmp_path / "concurrent"
    ready = Barrier(2)

    def publish_batch(base):
        ready.wait(timeout=15)
        return cache.publish(concurrent_variant, identity, chain(base), {"fit_s": 0.0})

    with ThreadPoolExecutor(max_workers=2) as pool:
        entries = list(pool.map(publish_batch, [40, 140]))
    for entry in entries:
        assert cache.inspect_entry(entry.directory, identity) is not None
        values = [int(io.load_sparse(path).nodes[0, 0, 0, 0]) for path in entry.paths]
        assert values in ([40, 41, 42, 43], [140, 141, 142, 143])
    assert not list(concurrent_variant.rglob(".pending-*"))


def test_r18_entry_parameters_and_wrapped_defaults_are_identity_bound(tmp_path: Path, monkeypatch):
    args = SimpleNamespace(scenario="control", mode="seq", method="ls_tetra_jitter", m=18,
                           grid="dp", adaptive=False, inputs=[], model_dir=tmp_path / "published")
    parameters = cli.fit_parameters(args)
    assert cli.model_dir(args) == args.model_dir
    assert selection.PROFILES["dp_jitter"] == ("seq", "ls_tetra_jitter", "dp", "auto")
    assert "dp_jitter" in selection.DEFAULT_PROFILES and "dp_guarded" not in selection.DEFAULT_PROFILES
    with pytest.raises(ValueError, match="exactly four"):
        cli._source_paths(args, create=False)
    # Small files exercise identity only, never the actual fitting path.
    sources = [tmp_path / f"stage{k}.control" for k in range(4)]
    copies = [tmp_path / f"copy{k}.control" for k in range(4)]
    for k, (source, copy) in enumerate(zip(sources, copies)):
        source.write_bytes(bytes([k]) * 256)
        copy.write_bytes(source.read_bytes())
    args.inputs = sources
    with pytest.raises(ValueError, match="incorrect source LUT size"):
        cli._source_paths(args, create=False)
    identity = cache.build_identity(sources, parameters)
    assert cache.build_identity(copies, parameters) == identity  # path is not an algorithm parameter
    # A transient Windows WMI failure used to publish a batch the parent could
    # not find. Bind stable interpreter architecture, independent of this probe.
    with monkeypatch.context() as patch:
        patch.setattr(cache.platform, "machine", lambda: "")
        assert cache.build_identity(sources, parameters) == identity
        patch.setattr(cache.platform, "machine", lambda: "AMD64")
        assert cache.build_identity(sources, parameters) == identity
        patch.setattr(cache.sysconfig, "get_platform", lambda: "different-interpreter-platform")
        assert cache.identity_key(cache.build_identity(sources, parameters)) != cache.identity_key(identity)
    assert identity["solver_environment"]["pointer_bits"] in (32, 64)
    controls = identity["algorithm_settings"]
    assert controls["training"]["seed"] == 0x533138
    assert controls["training"]["sample_count"] == 262144
    assert controls["integer_refinement"]["sweeps"] == 4
    assert controls["grid"]["maximum_step"] == 30
    assert controls["grid"]["perpendicular_probes"] == 24
    assert identity["fitting_defaults"]["lutlab.fit.stratified_points"]["seed"] == 0x533138
    # A wrapper-default change must invalidate identity even with unchanged files.
    with monkeypatch.context() as patch:
        patch.setattr(fit.stratified_points.__wrapped__, "__defaults__", (0x533139,))
        assert cache.identity_key(cache.build_identity(sources, parameters)) != cache.identity_key(identity)
    args.method = "ls_tetra_guarded"
    guarded = cache.algorithm_settings(cli.fit_parameters(args))["q16_refinement"]
    assert (guarded["sweeps"], guarded["guard_count"], guarded["guard_seed"]) == (3, 65536, 0x473138)
    args.method = "ls_tetra_boundary"
    boundary = cache.algorithm_settings(cli.fit_parameters(args))["training"]
    assert (boundary["sample_count"], boundary["exact_boundary_count"]) == (652296, 390152)
    assert boundary["weight_sum"] == 262144 and boundary["boundary_weight"] == 1 / 64
    assert selection.PROFILES["dp_boundary"] == ("seq", "ls_tetra_boundary", "dp", "auto")
    assert "dp_boundary" not in selection.DEFAULT_PROFILES
    args.method = "ls_tetra_structured"
    structured = cache.algorithm_settings(cli.fit_parameters(args))
    assert structured["structured"]["max_node_value"] == 255
    assert structured["training"]["scope"] == "general three-dimensional fallback only"
    assert "curve.py" in cache.source_fingerprint()
    assert selection.PROFILES["dp_structured"] == ("seq", "ls_tetra_structured", "dp", "auto")
    assert "dp_structured" not in selection.DEFAULT_PROFILES
    args.method = "ls_tetra_supported"
    supported = cache.algorithm_settings(cli.fit_parameters(args))
    assert supported["training"]["full_grid_vertex_count"] == 18 ** 3
    assert supported["training"]["data_hessian_eigenvalue_lower_bound"] == 1 / 64
    assert supported["training"]["seed"] == 0x533231
    assert selection.PROFILES["dp_supported"] == ("seq", "ls_tetra_supported", "dp", "auto")
    assert "dp_supported" not in selection.DEFAULT_PROFILES
    args.grid = "uniform"
    with pytest.raises(ValueError, match="requires --grid dp"):
        cli.fit_parameters(args)
    args.grid = "dp"
    args.method = "ls_tetra_full"
    with monkeypatch.context() as patch:
        patch.setattr(fullfit, "trainer_fingerprint", lambda: {"abi_version": 1, "library_sha256": "baseline"})
        parameters = cli.fit_parameters(args)
        full = cache.algorithm_settings(parameters)
        assert full["training"]["sample_count"] == 256 ** 3
        assert full["training"]["requested_threads"] == 4
        before = cache.build_identity(sources, parameters)
        patch.setattr(fullfit, "trainer_fingerprint", lambda: {"abi_version": 1, "library_sha256": "new-binary"})
        assert cache.identity_key(cache.build_identity(sources, parameters)) != cache.identity_key(before)
    assert selection.PROFILES["dp_full"] == ("seq", "ls_tetra_full", "dp", "auto")
    assert "dp_full" not in selection.DEFAULT_PROFILES
    args.method = "ls_tetra_full_box"
    with monkeypatch.context() as patch:
        patch.setattr(fullfit, "trainer_fingerprint", lambda: {"abi_version": 1, "library_sha256": "box-control"})
        controls = cache.algorithm_settings(cli.fit_parameters(args))
        assert controls["least_squares"]["lambda"] == 0
        assert controls["least_squares"]["bounds"] == [0, 255]
        assert controls["least_squares"]["maxiter"] == 500
        assert controls["least_squares"]["scaled_kkt_tolerance"] == 1e-5
        before = cache.build_identity(sources, cli.fit_parameters(args))
        patch.setattr(box.solve_box, "__kwdefaults__", {**box.solve_box.__kwdefaults__, "tol": 2e-5})
        assert cache.identity_key(cache.build_identity(sources, cli.fit_parameters(args))) != cache.identity_key(before)
    assert selection.PROFILES["dp_full_box"] == ("seq", "ls_tetra_full_box", "dp", "auto")
    assert "dp_full_box" not in selection.DEFAULT_PROFILES
    args.method = "adaptive_full"
    with monkeypatch.context() as patch:
        patch.setattr(fullfit, "trainer_fingerprint", lambda: {"abi_version": 1, "library_sha256": "adaptive-control"})
        controls = cache.algorithm_settings(cli.fit_parameters(args))
        assert controls["training"]["scope"] == "full-domain fallback only"
        assert controls["adaptive_model"]["target_semantics"].startswith("each model samples/fits its own")
        assert "step.py" in cache.source_fingerprint()
        assert controls["training"]["sample_count"] == 256 ** 3
    assert selection.PROFILES["adaptive_full"] == ("seq", "adaptive_full", "dp", "auto")
    assert "adaptive_full" not in selection.DEFAULT_PROFILES
    args.mode = "composite"
    with pytest.raises(ValueError, match="four independent"):
        cli.fit_parameters(args)
    args.mode, args.method = "seq", "ls_tetra_full_box"
    args.mode = "residual"
    with pytest.raises(ValueError, match="residual fitting supports"):
        cli.fit_parameters(args)
    args.mode, args.method, args.m = "seq", "ls_tetra_jitter", 16
    with pytest.raises(ValueError, match="grid size"):
        cli.fit_parameters(args)
