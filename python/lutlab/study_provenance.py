"""研究结果的环境身份与不可覆盖的运行来源记录。"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import uuid


def environment_fingerprint():
    """绑定数值依赖、CPU、系统及线程环境，不收集主机名或用户信息。"""
    packages = {}
    for name in ("numpy", "scipy", "numba", "llvmlite", "Pillow", "tifffile", "psutil"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    cpu_name = platform.processor()
    if sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    elif Path("/proc/cpuinfo").is_file():
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu_name = line.split(":", 1)[1].strip()
                break
    return {"python": sys.version, "implementation": platform.python_implementation(),
            "platform": platform.platform(), "machine": platform.machine(),
            "processor": platform.processor(), "cpu_name": cpu_name,
            "logical_cpu_count": os.cpu_count(), "packages": packages,
            "thread_environment": {name: os.environ.get(name) for name in
                ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMBA_NUM_THREADS", "NUMBA_THREADING_LAYER", "NUMBA_CPU_NAME",
                 "NUMBA_CPU_FEATURES")}}


def identity_digest(identity):
    return hashlib.sha256(json.dumps(identity, sort_keys=True, allow_nan=False).encode()).hexdigest()


def claim_run(path, metadata):
    """原子发布初始来源；恢复只读核验，身份不同时不修改任何既有文件。"""
    path = Path(path)
    if metadata.get("identity_sha256") != identity_digest(metadata["identity"]):
        raise ValueError("待发布的研究身份哈希不一致")

    def previous():
        recorded = json.loads(path.read_text(encoding="utf-8"))
        if (recorded.get("identity_sha256") != identity_digest(recorded["identity"])
                or recorded["identity"] != metadata["identity"]):
            raise ValueError("已有结果源码、输入或环境身份不同；请使用新输出目录，原始记录未改动")
        return recorded

    if path.exists():
        return previous()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.{uuid.uuid4().hex}.partial")
    try:
        temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2,
                                         allow_nan=False, default=str) + "\n", encoding="utf-8")
        try:
            # 同目录硬链接只在目标不存在时发布，避免不同进程覆盖最初的运行身份。
            os.link(temporary, path)
        except FileExistsError:
            return previous()
        return metadata
    finally:
        temporary.unlink(missing_ok=True)
