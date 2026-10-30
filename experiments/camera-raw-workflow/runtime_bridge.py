"""修订78的Linux RGB8桥接：逐帧单次AVX2调用，计时外与同模型标量逐字节核对。

导入接口：Runtime(library, models, threads)，apply(bytes)->(bytes, 秒)，
check_scalar(输入bytes, 预期bytes)->标量调用秒数；应使用with或显式close。
本桥接不证明摄影机浮点参考精度、完整RGB8色域或历史加速倍数。
"""
from __future__ import annotations

import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIBRARY = ROOT / "artifacts/skylake-andn-split-linux-build-v1/libjshc_skylake_andn_split.so"
LIBRARY_SHA256 = "51ed7ccd99817c61e89487db8f4afe1970932f637050515ae937280c0cd1532b"


def _fields(kind, names):
    return [(name, kind) for name in names.split()]


class CacheInfo(ct.Structure):
    _fields_ = (_fields(ct.c_uint32, "version enabled reason reserved")
                + _fields(ct.c_uint64, "entries valid_entries table_capacity_bytes temporary_capacity_bytes")
                + [("prepare_seconds", ct.c_double)]
                + _fields(ct.c_int32, "r_min r_max dg_min dg_max db_min db_max"))


class DomainInfo(ct.Structure):
    _fields_ = (_fields(ct.c_uint32, "version eligible cache_enabled reserved")
                + _fields(ct.c_uint64, "reachable_cells unproven_cells")
                + _fields(ct.c_int32, "dg_min dg_max db_min db_max"))


class PaletteInfo(ct.Structure):
    _fields_ = (_fields(ct.c_uint32, "version enabled palette_size reason")
                + _fields(ct.c_uint64, "blocks fast_blocks table_capacity_bytes temporary_peak_bytes")
                + [("prepare_seconds", ct.c_double)])


class DirectInfo(ct.Structure):
    _fields_ = (_fields(ct.c_uint32, "version enabled format reserved")
                + _fields(ct.c_uint64, "entries table_capacity_bytes")
                + _fields(ct.c_int32, "dg_min db_min"))


def file_sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def model_info(path):
    path = Path(path).resolve()
    with path.open("rb") as stream:
        header = stream.read(16)
    if len(header) != 16:
        raise ValueError(f"SLUT头部过短：{path}")
    magic, version, m, reserved = struct.unpack("<4sIII", header)
    expected = 16 + 12*m + 3840 + 3*m**3
    if (magic != b"SLUT" or version != 1 or reserved or not 17 <= m <= 33
            or path.stat().st_size != expected):
        raise ValueError(f"需要普通SLUT v1、17至33节点及精确长度：{path}")
    return {"path": str(path), "sha256": file_sha256(path), "bytes": expected, "m": m}


class Runtime:
    """一个句柄依次处理各帧；同一实例不可并发调用或跨close使用。"""

    def __init__(self, library=None, models=None, threads=4):
        self.handle = ct.c_void_p()
        self.library = Path(library or DEFAULT_LIBRARY).resolve()
        if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
            raise ValueError("仅支持Linux x86_64；此检查不代表已在Skylake执行")
        if threads not in (1, 4) or models is None or len(models) != 4:
            raise ValueError("需要四个普通SLUT及1或4线程")
        self.threads = threads
        actual_sha = file_sha256(self.library)
        if actual_sha != LIBRARY_SHA256:
            raise ValueError(f"原生库不匹配冻结修订78：{self.library}")
        self.models = [model_info(p) for p in models]
        self.lib = ct.CDLL(str(self.library))
        self._bind()
        abi = self.lib.jshc_cc_abi_version()
        revision = self.lib.jshc_cc_revision()
        capabilities = self.lib.jshc_cc_capabilities()
        if abi != 1 or revision != 78 or not capabilities & 2 or (threads == 4 and not capabilities & 4):
            raise ValueError("实际ABI、修订或AVX2/OpenMP能力不符")
        paths = (ct.c_char_p * 4)(*(os.fsencode(m["path"]) for m in self.models))
        error = ct.create_string_buffer(1024)
        start = time.perf_counter()
        code = self.lib.jshc_cc_create(paths, None, 4, ct.byref(self.handle), error, len(error))
        self.prepare_seconds = time.perf_counter() - start
        if code:
            self.close()
            raise RuntimeError("创建失败：" + error.value.decode("utf-8", errors="replace"))
        try:
            start = time.perf_counter()
            actual = {}
            for name, cls, size in (("cache", CacheInfo, 80), ("domain", DomainInfo, 48),
                                    ("palette", PaletteInfo, 56), ("direct", DirectInfo, 40)):
                if ct.sizeof(cls) != size:
                    raise ValueError(f"ctypes结构布局不符：{name}")
                value = cls()
                if getattr(self.lib, f"jshc_cc_get_{name}_info")(self.handle, ct.byref(value), size):
                    raise RuntimeError(f"读取实际诊断失败：{name}")
                if value.version != 1:
                    raise ValueError(f"诊断ABI版本不符：{name}")
                actual[name] = {key: getattr(value, key) for key, _ in cls._fields_}
            actual["domain_fast_enabled"] = self.lib.jshc_cc_domain_fast_enabled(self.handle)
            actual["andn_split_enabled"] = self.lib.jshc_cc_andn_split_enabled(self.handle)
            actual["model_bytes"] = self.lib.jshc_cc_model_bytes(self.handle)
            self.info = {"library": str(self.library), "library_sha256": actual_sha,
                         "abi": abi, "revision": revision, "capabilities": capabilities,
                         "threads_requested": threads, "sidecars": None, "models": self.models,
                         "prepare_seconds": self.prepare_seconds, "actual": actual,
                         "diagnostics_seconds": time.perf_counter() - start}
        except Exception:
            self.close()
            raise

    def _bind(self):
        for name in ("abi_version", "revision", "capabilities"):
            f = getattr(self.lib, "jshc_cc_" + name)
            f.argtypes = []; f.restype = ct.c_uint32
        self.lib.jshc_cc_create.argtypes = [ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.c_size_t,
                                           ct.POINTER(ct.c_void_p), ct.POINTER(ct.c_char), ct.c_size_t]
        self.lib.jshc_cc_create.restype = ct.c_int
        self.lib.jshc_cc_destroy.argtypes = [ct.c_void_p]
        self.lib.jshc_cc_destroy.restype = None
        self.lib.jshc_cc_apply.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint8), ct.c_size_t,
                                          ct.c_int, ct.c_int, ct.POINTER(ct.c_char), ct.c_size_t]
        self.lib.jshc_cc_apply.restype = ct.c_int
        for name, cls in (("cache", CacheInfo), ("domain", DomainInfo),
                          ("palette", PaletteInfo), ("direct", DirectInfo)):
            f = getattr(self.lib, f"jshc_cc_get_{name}_info")
            f.argtypes = [ct.c_void_p, ct.POINTER(cls), ct.c_size_t]; f.restype = ct.c_int
        for name in ("domain_fast_enabled", "andn_split_enabled", "model_bytes"):
            f = getattr(self.lib, "jshc_cc_" + name)
            f.argtypes = [ct.c_void_p]
            f.restype = ct.c_size_t if name == "model_bytes" else ct.c_uint32

    def _apply(self, payload, kernel, threads):
        if not self.handle.value:
            raise RuntimeError("句柄已关闭")
        if not isinstance(payload, bytes) or not payload or len(payload) % 3:
            raise ValueError("输入必须为非空紧密RGB8 bytes，长度须为3的倍数")
        buffer = (ct.c_uint8 * len(payload)).from_buffer_copy(payload)
        error = ct.create_string_buffer(1024)
        start = time.perf_counter()
        code = self.lib.jshc_cc_apply(self.handle, buffer, len(payload), kernel, threads, error, len(error))
        seconds = time.perf_counter() - start
        if code:
            raise RuntimeError("apply失败：" + error.value.decode("utf-8", errors="replace"))
        return bytes(buffer), seconds

    def apply(self, payload: bytes) -> tuple[bytes, float]:
        """仅一次kernel1调用；返回耗时不含Python输入复制与输出bytes构造。"""
        return self._apply(payload, 1, self.threads)

    def check_scalar(self, payload: bytes, expected: bytes) -> float:
        """同输入kernel0、单线程核对；返回标量调用秒数，不算生产耗时。"""
        actual, seconds = self._apply(payload, 0, 1)
        if actual != expected:
            first = next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b),
                         min(len(actual), len(expected)))
            raise AssertionError(f"标量对照不一致，首差字节={first}，像素={first // 3}")
        return seconds

    def close(self):
        if self.handle.value:
            self.lib.jshc_cc_destroy(self.handle)
            self.handle = ct.c_void_p()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--models", type=Path, nargs=4, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, choices=(1, 4), default=4)
    args = parser.parse_args()
    source, destination = args.input.resolve(), args.output.resolve()
    directory = source.is_dir()
    inputs = sorted(p for p in source.glob("*.rgb") if p.is_file()) if directory else [source]
    if not inputs or any(not p.is_file() or p.stat().st_size == 0 or p.stat().st_size % 3 for p in inputs):
        raise ValueError("需要至少一份非空RGB8文件；目录模式只取排序后的顶层*.rgb")
    report_path = destination / "results.json" if directory else Path(str(destination) + ".json")
    if destination.exists() or report_path.exists():
        raise ValueError("输出及报告必须为新路径，不覆盖既有文件")
    if directory:
        destination.mkdir(parents=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
    report = {"passed": False, "script_sha256": file_sha256(__file__),
              "environment": {"platform": platform.platform(), "python": sys.version,
                              "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
                              "thread_environment": {k: os.environ.get(k) for k in
                                  ("OMP_NUM_THREADS", "OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_PLACES")}},
              "input": str(source), "output": str(destination), "frames": [],
              "scope": "同四份RGB8 SLUT逐帧标量核对；非摄影机浮点参考、完整色域或历史加速证明",
              "timing_scope": "prepare仅create；apply仅单次kernel1 API；标量核对、诊断、读写、哈希及Python复制另计或排除"}
    try:
        with Runtime(args.library, args.models, args.threads) as runtime:
            report["runtime"] = runtime.info
            for path in inputs:
                payload = path.read_bytes()
                input_sha = hashlib.sha256(payload).hexdigest()
                output, elapsed = runtime.apply(payload)
                scalar_seconds = runtime.check_scalar(payload, output)
                target = destination / path.name if directory else destination
                with target.open("xb") as stream:
                    stream.write(output)
                report["frames"].append({"input": str(path), "output": str(target), "bytes": len(payload),
                    "pixels": len(payload)//3, "input_sha256": input_sha,
                    "output_sha256": hashlib.sha256(output).hexdigest(), "apply_seconds": elapsed,
                    "scalar_seconds": scalar_seconds, "scalar_equal": True})
                del payload, output
        report["passed"] = True
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        report["totals"] = {"frames": len(report["frames"]),
            "bytes": sum(f["bytes"] for f in report["frames"]),
            "pixels": sum(f["pixels"] for f in report["frames"]),
            "apply_seconds": sum(f["apply_seconds"] for f in report["frames"]),
            "scalar_seconds": sum(f["scalar_seconds"] for f in report["frames"])}
        with report_path.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
    print(json.dumps({"passed": True, "report": str(report_path), "totals": report["totals"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
