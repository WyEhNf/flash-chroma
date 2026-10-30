"""只观察G分bank普查在max41的288路径前置失败；不重跑普查或像素。"""
import ctypes as ct
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts')]
from census_direct_gbank8 import WideInfo, Library, DLL, DLL_SHA, sha, save
from domain_cache_support import info as domain_info
from palette_support import info as palette_info


def main():
    out = ROOT / 'artifacts/p16-direct-gbank8-max41-observer-v1'
    if out.exists():
        raise FileExistsError('不覆盖失败前置观察')
    original = ROOT / 'artifacts/p16-direct-gbank8-census-v1/frozen.json'
    frozen = json.loads(original.read_text(encoding='utf-8'))
    spec = frozen['models']['max41']
    for path, expected in frozen['inputs_sha256'].items():
        assert sha(path) == expected, path
    out.mkdir(parents=True)
    sources = [Path(__file__), ROOT / 'scripts/census_direct_gbank8.py', ROOT / 'scripts/domain_cache_support.py',
               ROOT / 'scripts/palette_support.py', ROOT / 'experiments/channel-runtime/channel_native.py']
    save(out / 'protocol.json', {'purpose': __doc__, 'failed_frozen_sha256': sha(original), 'model': spec,
                                 'sources_sha256': {path.relative_to(ROOT).as_posix(): sha(path) for path in sources},
                                 'dll_sha256': DLL_SHA, 'pixel_apply_calls': 0, 'performance_calls': 0})
    dirs = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(DLL.parent))]
    library = Library(str(DLL), DLL_SHA)
    with library.chain(spec['models'], spec['sidecars']) as chain:
        f = library.dll.p16_cc_get_direct_u16_info
        f.argtypes = [ct.c_void_p, ct.POINTER(WideInfo), ct.c_size_t]
        f.restype = ct.c_int
        state = WideInfo()
        code = f(chain.handle, ct.byref(state), 96)
        result = {'returncode': code, 'wide': {name: getattr(state, name) for name, _ in WideInfo._fields_},
                  'domain': domain_info(chain), 'palette': palette_info(chain), 'model_bytes': chain.model_bytes,
                  'pixel_apply_calls': 0, 'performance_calls': 0}
        save(out / 'results.json', result)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
