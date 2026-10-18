"""固定线程环境后启动本地双尺寸评测，不自动提交或上传。"""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
environment = dict(os.environ, PYTHONPATH=str(ROOT/"python"), NUMBA_NUM_THREADS="4",
    OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONIOENCODING="utf-8")
raise SystemExit(subprocess.call([sys.executable,"-u","-m","lutlab.paired_baselines",*sys.argv[1:]],
    cwd=ROOT,env=environment))
