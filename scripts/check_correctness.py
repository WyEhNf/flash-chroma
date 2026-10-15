"""运行 CI 的完整正确性门禁，不执行性能测试或下载实验数据。"""
from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build-correctness"


def main():
    executable = BUILD / ("jshc.exe" if os.name == "nt" else "jshc")
    library_name = (
        "jshc_full_fit.dll" if os.name == "nt"
        else "libjshc_full_fit.so"
    )
    library = BUILD / library_name
    for path in (executable, library):
        if not path.is_file():
            raise FileNotFoundError(f"缺少正确性测试产物，请运行 pixi run --locked correctness：{path}")

    # 显式指定同一次构建的产物；拟合库缺失或不可加载必须失败，不能跳过。
    env = os.environ.copy()
    env["JSHC_BIN"] = str(executable)
    env["JSHC_FULL_FIT_LIB"] = str(library)
    env["PYTHONPATH"] = str(ROOT / "python")
    subprocess.run(
        ["ctest", "--test-dir", str(BUILD), "--output-on-failure", "--no-tests=error"],
        cwd=ROOT, env=env, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-ra", "tests"],
        cwd=ROOT, env=env, check=True,
    )


if __name__ == "__main__":
    main()
