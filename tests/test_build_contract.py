"""构建产物选择与失败传播的回归检查。"""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from lutlab import fullfit, metrics


ROOT = Path(__file__).resolve().parents[1]


def test_default_fitting_library_precedes_legacy_and_invalid_override_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(fullfit, "ROOT", tmp_path)
    monkeypatch.delenv("JSHC_FULL_FIT_LIB", raising=False)
    name = "jshc_full_fit.dll" if os.name == "nt" else "libjshc_full_fit.so"
    legacy = tmp_path / "build-fit" / name
    current = tmp_path / "build" / name
    for path in (legacy, current):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    assert fullfit.resolve_library() == current
    monkeypatch.setenv("JSHC_FULL_FIT_LIB", str(tmp_path / "missing-library"))
    with pytest.raises(FileNotFoundError):
        fullfit.resolve_library()


def test_missing_build_library_fails_before_tests_despite_valid_environment(tmp_path):
    # 环境中已有有效拟合库，也不能掩盖所选构建缺失库的问题。
    try:
        library = fullfit.resolve_library()
    except FileNotFoundError:
        if os.environ.get("JSHC_FULL_FIT_LIB"):
            raise
        pytest.skip("未构建可选拟合库")
    env = os.environ.copy()
    env["JSHC_FULL_FIT_LIB"] = str(library)
    manifest = {
        "JSHC_BIN": str(metrics.resolve_jshc()),
        "JSHC_FULL_FIT_LIB": str(tmp_path / "missing-library"),
    }
    (tmp_path / "test-artifacts-Release.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_correctness.py"),
         "--build-dir", str(tmp_path)],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode != 0
    assert "缺少测试产物" in result.stderr
    assert "Test project" not in result.stdout
