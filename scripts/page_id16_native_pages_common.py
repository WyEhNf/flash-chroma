"""Native页指针独立绑定与借用owner；模块导入不执行native调用。"""
import ctypes as ct
from pathlib import Path
from page_id16_common import PageModel, ROOT, U8, FileView, sha, save, env, snapshot, query
from study_memory_rom import read

BUILD = ROOT / 'artifacts/p16-page-native-pages-observer-v2/build'


class PagesView(ct.Structure):
    _fields_ = [('base', PageModel), ('pages', ct.c_void_p)]


def pointer(view):
    return ct.byref(view) if isinstance(view, PagesView) else ct.cast(view, ct.POINTER(PagesView))


def library(path, parallel):
    value = ct.CDLL(str(path))
    for symbol in ('jshc_p4_pages_view_size', 'jshc_p4_pages_pointer_alignment',
                   'jshc_p4_pages_view_alignment', 'jshc_p4_pages_slots_bytes'):
        getattr(value, symbol).restype = ct.c_size_t
        getattr(value, symbol).argtypes = []
    value.jshc_p4_pages_prepare.argtypes = [ct.POINTER(PagesView), ct.c_void_p,
                                          ct.c_size_t, ct.c_void_p, ct.c_size_t]
    value.jshc_p4_pages_clear.argtypes = [ct.POINTER(PagesView)]
    value.jshc_p4_pages_apply.argtypes = [ct.POINTER(PagesView), U8, U8, ct.c_size_t]
    value.jshc_p4_pages_validate_io.argtypes = [ct.POINTER(PagesView), U8, U8, ct.c_size_t]
    if parallel:
        value.jshc_p4_pages_apply_parallel.argtypes = [ct.POINTER(PagesView), U8, U8, ct.c_size_t, ct.c_int]
    symbols = ['jshc_p4_pages_apply', 'jshc_p4_pages_prepare', 'jshc_p4_pages_clear',
               'jshc_p4_pages_validate_io', 'jshc_p4_apply']
    if parallel:
        symbols.append('jshc_p4_pages_apply_parallel')
    addresses = {symbol: int(ct.cast(getattr(value, symbol), ct.c_void_p).value) for symbol in symbols}
    if addresses['jshc_p4_pages_apply'] == addresses['jshc_p4_apply']:
        raise AssertionError('native-pages新入口不能指向旧apply')
    value.pages_receipt = dict(path=str(Path(path).resolve()), sha256=sha(path), addresses=addresses,
                               calls=dict(prepare=0, clear=0, core=0, omp_c99=0),
                               scope='Python实际入口尝试数，含setup与拒绝；不是内部OMP像素或CPU指令计数。')
    return value


def prepare(lib, view, blob, byte_count, slots, count=4096):
    lib.pages_receipt['calls']['prepare'] += 1
    return lib.jshc_p4_pages_prepare(pointer(view), blob, byte_count, slots, count)


def clear(lib, view):
    lib.pages_receipt['calls']['clear'] += 1
    return lib.jshc_p4_pages_clear(pointer(view))


def call(lib, view, source, target, pixels, threads=None):
    src, dst = ct.cast(source, U8), ct.cast(target, U8)
    label = 'core' if threads is None else 'omp_c99'
    lib.pages_receipt['calls'][label] += 1
    if threads is None:
        return lib.jshc_p4_pages_apply(pointer(view), src, dst, pixels)
    return lib.jshc_p4_pages_apply_parallel(pointer(view), src, dst, pixels, threads)


class BorrowedPages:
    def __init__(self, path, lib):
        self.file_view = FileView(path, 'readonly')
        self.model = PagesView()
        self.slots = (ct.c_void_p * 4096)()
        self.lib = lib
        self.file_view.models.append(self.model)
        try:
            if prepare(lib, self.model, self.file_view.address, self.file_view.length, ct.addressof(self.slots)):
                raise ValueError('新native-pages prepare拒绝原ROM')
        except BaseException:
            self.file_view.close()
            raise

    def close(self):
        if not self.file_view.closed and clear(self.lib, self.model):
            raise RuntimeError('native-pages清理view失败，保持owner供诊断')
        self.file_view.close()

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()
