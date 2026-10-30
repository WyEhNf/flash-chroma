"""一次读取旧87普通SLUT域资格与精确cache唯一数；不构建91或生成直表。"""
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import numpy as np
import psutil
from bench_p16_model_pair import checked
from study_p16_direct_compile import Library, save, digest, env
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from palette_support import info as palette_info
from direct16_support import info as direct_info


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    static = json.loads(checked(plan['static_plan']).read_text(encoding='utf-8'))
    for row in static['sources']:
        checked(row)
    if a.output.exists():
        raise FileExistsError('仅一次固定普通模型资格读取，保留已有结果')
    a.output.mkdir(parents=True)
    psutil.Process().cpu_affinity(plan['cpus'])
    directory = os.add_dll_directory('E:/mingw64/bin') if os.name == 'nt' else None
    library = Library(checked(static['reference_library']), static['reference_library']['sha256'])
    assert library.revision == 87
    model = static['models']['fallback']
    paths = [checked(row) for row in model['models']]
    sides = [checked(row) if row else None for row in model['sidecars']]
    assert all(row is None for row in sides)
    with library.chain(paths, sides) as chain:
        cache, domain = cache_info(chain), domain_info(chain)
        palette, direct = palette_info(chain), direct_info(chain)
        assert not direct['enabled'] and not palette['enabled']
        unique_count = None
        unique_sha = None
        cache_sha = None
        if cache['enabled'] and domain['eligible']:
            values = np.empty(cache['entries'], np.uint32)
            f = library.dll.jshc_cc_copy_cache
            f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
            f.restype = ct.c_int
            assert f(chain.handle, values.ctypes.data_as(ct.POINTER(ct.c_uint32)), values.size) == 0
            unique = np.unique(values)
            unique_count = int(unique.size)
            cache_sha = hashlib.sha256(memoryview(values).cast('B')).hexdigest()
            unique_sha = hashlib.sha256(memoryview(unique).cast('B')).hexdigest()
        eligible = unique_count is not None and unique_count <= 255
        save(a.output / 'qualification.json', {'eligible_for_separate91_validation': eligible,
            'shared_first_proof': '四模型均无sidecar，旧构造view.shared为true，各通道axes指向同一packed轴。',
            'cache_unique_count_including_invalid_zero_slots': unique_count,
            'cache_sha256': cache_sha, 'sorted_unique_sha256': unique_sha,
            'state': {'cache': cache, 'domain': domain, 'palette': palette, 'direct': direct,
                'model_bytes': chain.model_bytes}, 'model': model,
            'library': static['reference_library'], 'environment': env(),
            'scope': '只读旧87既有suffix cache和完整域证书，未加载91、未构建直接表、未读取照片/oracle、非性能计时。',
            'decision': '允许下一阶段独立91构建及完整域质量，尚未证明91正确或加速。' if eligible else
                '立即停止本固定资格方案，不改模型/阈值/格式，不扫描参数或其它模型。'})
        save(a.output / 'executed-plan.json', plan)
        print('ordinary87 cache唯一数', unique_count, '下一阶段资格', eligible, flush=True)


if __name__ == '__main__':
    main()
