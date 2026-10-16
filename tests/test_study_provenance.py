"""研究恢复的环境隔离、不可覆盖来源及容量基线回归。"""
from copy import deepcopy
import json

import pytest

from lutlab.study_provenance import claim_run, identity_digest
from lutlab.study_reporting import select_baseline
from lutlab.execution_proof import validate_native_kernel


def test_reported_and_legacy_kernel_evidence_are_distinct():
    legacy = {"backend": "cpu", "command": ["jshc", "cube", "-k", "tetra_scalar"]}
    assert validate_native_kernel(legacy, "tetra_scalar") == "legacy_explicit_command"
    assert validate_native_kernel({**legacy, "kernel": "tetra_scalar"}, "tetra_scalar") == "native_reported_kernel"
    assert validate_native_kernel({"backend": "cpu", "kernel": "tetra_scalar",
        "command": ["jshc", "cube", "-k", "auto"]}, "tetra_scalar") == "native_reported_kernel"
    for bad in ({**legacy, "kernel": "tetra_avx2"},
                {"backend": "cpu", "command": ["jshc", "cube", "-k", "auto"]},
                {"backend": "cpu"}):
        with pytest.raises(ValueError, match="内核/后端"):
            validate_native_kernel(bad, "tetra_scalar")


def test_baseline_selection_does_not_depend_on_order():
    small = {"profile": "sample_tetra", "m": 17, "mean": .9}
    large = {"profile": "sample_tetra", "m": 33, "mean": .5}
    for rows in ([small, large], [large, small]):
        assert select_baseline(rows) is large
    for rows in ([small], [large, large]):
        with pytest.raises(ValueError, match="唯一"):
            select_baseline(rows)


def test_resume_preserves_first_metadata_and_rejects_environment_changes(tmp_path):
    identity = {"schema": 2, "environment": {"cpu_name": "cpu-a", "numpy": "1", "numba": "1",
                "threads": 4}, "source_sha256": {"code": "abc"}}
    meta = {"identity": identity, "identity_sha256": identity_digest(identity), "created_utc": "first"}
    path = tmp_path / "run.json"
    claim_run(path, meta)
    original = path.read_bytes()
    assert claim_run(path, {**meta, "created_utc": "second"})["created_utc"] == "first"
    assert path.read_bytes() == original
    for key, value in (("cpu_name", "cpu-b"), ("numpy", "2"), ("numba", "2"), ("threads", 8)):
        changed = deepcopy(meta)
        changed["identity"]["environment"][key] = value
        changed["identity_sha256"] = identity_digest(changed["identity"])
        with pytest.raises(ValueError, match="环境身份不同"):
            claim_run(path, changed)
        assert path.read_bytes() == original
    assert not list(tmp_path.glob("*.partial"))
    path.write_text(json.dumps({"identity": {"schema": 1}, "identity_sha256": "legacy"}))
    legacy = path.read_bytes()
    with pytest.raises(ValueError, match="环境身份不同"):
        claim_run(path, meta)
    assert path.read_bytes() == legacy
