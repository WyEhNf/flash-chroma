"""沿用正确性CI的线程隔离设置，本地测试通过后运行批量研究；不会上传。"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
environment = os.environ.copy()
environment.update(PYTHONPATH=str(ROOT / "python"), OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                   OMP_NUM_THREADS="4", NUMBA_NUM_THREADS="4", PYTHONIOENCODING="utf-8")
(ROOT / "tmp").mkdir(exist_ok=True)
test_directory = tempfile.mkdtemp(prefix="lut-study-tests-", dir=ROOT / "tmp")
subprocess.run([sys.executable, "-m", "pytest", "-q", "--basetemp", test_directory, "tests/test_compatibility.py"],
               cwd=ROOT, env=environment, check=True)
subprocess.run([sys.executable, "-u", "-m", "lutlab.compatibility", *sys.argv[1:]],
               cwd=ROOT, env=environment, check=True)
