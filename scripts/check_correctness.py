"""运行当前 CMake 构建的正确性测试，不下载数据或执行性能循环。"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_environment(build: Path, config: str) -> dict[str, str]:
    # 路径由 CMake 按目标与配置生成，避免猜测扩展名或多配置输出目录。
    manifest = build / f"test-artifacts-{config}.json"
    artifacts = json.loads(manifest.read_text(encoding="utf-8"))
    env = os.environ.copy()
    for variable in ("JSHC_BIN", "JSHC_FULL_FIT_LIB"):
        path = Path(artifacts[variable])
        if not path.is_file():
            raise FileNotFoundError(f"缺少测试产物，请先构建 {build}：{path}")
        env[variable] = str(path)
    env["PYTHONPATH"] = str(ROOT / "python")
    return env


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--config", default="Release")
    parser.add_argument("--only", choices=("all", "cpp", "python"), default="all")
    args = parser.parse_args(argv)
    build = args.build_dir.resolve()
    env = test_environment(build, args.config)
    if args.only in ("all", "cpp"):
        subprocess.run(
            ["ctest", "--test-dir", str(build), "-C", args.config,
             "--output-on-failure", "--no-tests=error"],
            cwd=ROOT, env=env, check=True,
        )
    if args.only in ("all", "python"):
        subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-ra", "tests"],
            cwd=ROOT, env=env, check=True,
        )


if __name__ == "__main__":
    main()
