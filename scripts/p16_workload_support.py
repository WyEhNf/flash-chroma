"""92显式预计总像素的有类型包装；默认create保持独立旧接口。"""
from __future__ import annotations
import ctypes as ct
from pathlib import Path
from channel_native import Chain, digest

THRESHOLD = 1 << 26


def validate_expected_pixels(value):
    # ctypes会静默截断/转换值，必须在进入unsigned C ABI前拒绝这些输入。
    if type(value) is not int or not 0 <= value <= (1 << 64) - 1:
        raise ValueError('预计像素必须是0..UINT64_MAX的Python int，不接收bool或隐式转换')
    return value


def bind_workload(library):
    d = library.dll
    d.jshc_cc_create_for_workload.argtypes = [ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p),
        ct.c_size_t, ct.c_uint64, ct.POINTER(ct.c_void_p), ct.POINTER(ct.c_char), ct.c_size_t]
    d.jshc_cc_create_for_workload.restype = ct.c_int
    d.jshc_cc_workload_threshold.argtypes = []
    d.jshc_cc_workload_threshold.restype = ct.c_uint64
    if d.jshc_cc_workload_threshold() != THRESHOLD:
        raise ValueError('预计总像素阈值与冻结92合同不一致')


def workload_chain(library, models, sidecars=None, *, expected_pixels):
    hint = validate_expected_pixels(expected_pixels)
    if not 1 <= len(models) <= 4:
        raise ValueError('实验链需要1..4个模型')
    if sidecars is None:
        sidecars = [None] * len(models)
    if len(sidecars) != len(models):
        raise ValueError('侧表必须逐级对应')
    paths = [Path(p).resolve() for p in models]
    sides = [Path(p).resolve() if p is not None else None for p in sidecars]
    for p in [*paths, *[p for p in sides if p is not None]]:
        if not p.is_file():
            raise FileNotFoundError(p)
    bind_workload(library)
    a = (ct.c_char_p * len(paths))(*(str(p).encode('utf-8') for p in paths))
    b = (ct.c_char_p * len(sides))(*(str(p).encode('utf-8') if p else None for p in sides))
    handle, error = ct.c_void_p(), ct.create_string_buffer(1024)
    rc = library.dll.jshc_cc_create_for_workload(a, b, len(paths), hint,
        ct.byref(handle), error, len(error))
    if rc:
        raise RuntimeError(error.value.decode('utf-8', errors='replace'))
    c = Chain.__new__(Chain)
    c.library, c.handle, c.models, c.sidecars = library, handle, paths, sides
    try:
        c.inputs_sha256 = {str(p): digest(p) for p in [*paths, *[p for p in sides if p is not None]]}
    except BaseException:
        c.close()
        raise
    return c


class HintLibrary:
    """质量脚本的固定hint视图；像素调用仍用原Chain，不引入新热路径。"""
    def __init__(self, library, expected_pixels):
        self.library = library
        self.expected_pixels = validate_expected_pixels(expected_pixels)

    def __getattr__(self, name):
        return getattr(self.library, name)

    def chain(self, models, sidecars=None):
        return workload_chain(self.library, models, sidecars, expected_pixels=self.expected_pixels)
