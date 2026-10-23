"""只构造明确基线和精度候选，检查当前最快后端的缓存/域/调色板资格。"""
from __future__ import annotations
import argparse
import ctypes as ct
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments/channel-runtime'))
from channel_native import Library, digest


class CacheInfo(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ('version', 'enabled', 'reason', 'reserved')]+[(n, ct.c_uint64) for n in
        ('entries', 'valid_entries', 'table_capacity_bytes', 'temporary_capacity_bytes')]+[('prepare_seconds', ct.c_double)]+[(n, ct.c_int32) for n in
        ('r_min', 'r_max', 'dg_min', 'dg_max', 'db_min', 'db_max')]


class DomainInfo(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ('version', 'eligible', 'cache_enabled', 'reserved')]+[(n, ct.c_uint64) for n in
        ('reachable_cells', 'unproven_cells')]+[(n, ct.c_int32) for n in ('dg_min', 'dg_max', 'db_min', 'db_max')]


class PaletteInfo(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ('version', 'enabled', 'palette_size', 'reason')]+[(n, ct.c_uint64) for n in
        ('blocks', 'fast_blocks', 'table_capacity_bytes', 'temporary_peak_bytes')]+[('prepare_seconds', ct.c_double)]


class DirectInfo(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ('version', 'enabled', 'format', 'reserved')]+[(n, ct.c_uint64) for n in
        ('entries', 'table_capacity_bytes')]+[(n, ct.c_int32) for n in ('dg_min', 'db_min')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--libraries', type=Path, nargs='+', required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--suffix-stage4', type=Path)
    parser.add_argument('--baseline-base', type=Path)
    parser.add_argument('--baseline-sidecar', type=Path)
    parser.add_argument('--baseline-label', default='a399')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖资格诊断')
    dll_dirs = [os.add_dll_directory('E:/mingw64/bin')]
    cache = args.cache_root.resolve()
    suffix = [cache/'artifacts/cinema-envelope-v1/stage4_sweep004'/f'selected-stage{k}.slut' for k in (2, 3, 4)]
    variants = {args.baseline_label: cache/'artifacts/cinema-current-anchor-accept-v1', 'candidate': args.candidate}
    records = []
    for path in args.libraries:
        dll_dirs.append(os.add_dll_directory(str(path.resolve().parent)))
        lib = Library(path, digest(path))
        for name, folder in variants.items():
            active_suffix = suffix.copy()
            if name == 'candidate' and args.suffix_stage4 is not None:
                active_suffix[2] = args.suffix_stage4.resolve()
            base, sidecar = folder/'candidate-base.slut', folder/'channel-frac.bin'
            sidecar = sidecar if sidecar.exists() else None
            if name == args.baseline_label and args.baseline_base is not None:
                base, sidecar = args.baseline_base.resolve(), args.baseline_sidecar
            with lib.chain([base, *active_suffix], [sidecar, None, None, None]) as chain:
                row = {'variant': name, 'library_path': str(path.resolve()), 'library_sha256': lib.sha256,
                       'revision': lib.revision, 'model_bytes': chain.model_bytes, 'input_sha256': chain.inputs_sha256}
                for label, cls in [('cache', CacheInfo), ('domain', DomainInfo), ('palette', PaletteInfo), ('direct', DirectInfo)]:
                    fn = getattr(lib.dll, 'jshc_cc_get_'+label+'_info')
                    fn.argtypes = [ct.c_void_p, ct.POINTER(cls), ct.c_size_t]; fn.restype = ct.c_int
                    value = cls()
                    if fn(chain.handle, ct.byref(value), ct.sizeof(value)):
                        raise RuntimeError('诊断ABI拒绝结构大小')
                    row[label] = {n: getattr(value, n) for n, _ in cls._fields_}
                records.append(row)
                print(json.dumps(row, ensure_ascii=False), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'purpose': __doc__, 'source_sha256': digest(Path(__file__)), 'records': records,
        'mapping_calls': 0, 'performance_calls': 0,
        'scope': 'prepare_seconds仅构造诊断，不作受控性能比较；资格相同不保证运行速度相同，资格改变也不单独量化吞吐。'}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for handle in dll_dirs:
        handle.close()


if __name__ == '__main__':
    main()
