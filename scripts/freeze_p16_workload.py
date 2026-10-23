"""冻结92独立质量或性能计划；只生成身份记录，不执行构造或测量。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def identity(path):
    path = path.resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def read_frozen(path, expected):
    assert identity(path)['sha256'] == expected, str(path)
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('quality', 'performance'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('计划冻结不覆盖')
    oldq = read_frozen(ROOT / 'experiments/p16-shared-domain-quality-v1.json',
        'ad82290dc8cfe87231c400eccfadca51c06f68b24e6150f25486b0b1da77547d')
    oldp = read_frozen(ROOT / 'experiments/p16-shared-domain-performance-v1.json',
        '0f8ee04e4fb8ea70e7f708e7c8d8109b912598a53fa780f8d431ee38cf4af40c')
    new_source = [ROOT / 'experiments/p16-workload-runtime' / n for n in
        ('CMakeLists.txt', 'channel_runtime.cpp', 'workload_hint.h', '静态设计.md')]
    new_source += [ROOT / 'scripts' / n for n in ('p16_workload_support.py',
        'verify_p16_workload.py', 'bench_p16_workload.py', 'freeze_p16_workload.py', 'audit_p16_workload.py')]
    skip = ('p16-shared-domain-runtime', 'verify_p16_shared_domain.py')
    deps = {row['path']: row for row in oldp['sources'] if not any(s in row['path'] for s in skip)}
    for path in new_source:
        row = identity(path)
        deps[row['path']] = row
    for row in deps.values():
        assert identity(Path(row['path'])) == row
    libs = {'reference': oldq['libraries']['reference'],
        'candidate': identity(ROOT / 'artifacts/p16-workload-build-v1/libjshc_workload.dll')}
    source_freeze = identity(ROOT / 'experiments/p16-workload-static-v1.json')
    if a.phase == 'quality':
        q = dict(oldq)
        q.update({'purpose': '92固定预计总像素阈值：默认/阈值两侧完整域及五unsigned hint有限合同，无性能',
            'script_sha256': identity(ROOT / 'scripts/verify_p16_workload.py')['sha256'],
            'sources': list(deps.values()), 'libraries': libs, 'source_freeze': source_freeze, 'threshold_pixels': 1 << 26,
            'photo_images': [1, 10, 85, 86, 100],
            'boundary': '2模型×默认/阈值−1/阈值的3完整域模式，各87scalar1对92scalar1/4、AVX2in/out1/4；五hint有限/拒绝；低高hint各八u64合同；五N各1/4线程in/out实际照片输出SHA；无参数扫描、性能、OOM或无AVX2故障注入。'})
    else:
        quality_plan = ROOT / 'experiments/p16-workload-quality-v1.json'
        quality_path = ROOT / 'artifacts/p16-workload-quality-v1/correctness.json'
        quality = json.loads(quality_path.read_text(encoding='utf-8'))
        assert quality['passed']
        q = dict(oldp)
        q.update({'purpose': '92显式总像素门控同模型87配对，固定2^26；N1/10/85/86/100各自冷/热和100~50档',
            'script_sha256': identity(ROOT / 'scripts/bench_p16_workload.py')['sha256'],
            'sources': [*deps.values(), identity(quality_plan)], 'libraries': libs,
            'quality_proof': identity(quality_path), 'source_freeze': source_freeze, 'photo_expected': quality['photos']['expected'],
            'threshold_pixels': 1 << 26, 'pixels_per_image': 786432, 'images': [1, 10, 85, 86, 100],
            'image_orders': [[1, 10, 85, 86, 100], [100, 86, 85, 10, 1],
                [1, 10, 85, 86, 100], [100, 86, 85, 10, 1]],
            'repeats': {'1': 64, '10': 16, '85': 9, '86': 9, '100': 9},
            'cold_scope': '每模型/角色/N各5新句柄正式+5新句柄AA，首真分离固定4t；candidate每次原生create_for_workload hint=N×786432，reference旧create。模型文件读取/解析/校验与全部prepare计入create，continuous wall从create前到首bench_to返回；路径/输入文件SHA/照片解码/分配/末输出SHA在外。文件缓存与进程OMP池可热，不称磁盘或进程冷。第10句柄对应热场。',
            'hot_scope': '每N每role warm2，正式及AA各64/16/9/9/9整组，1/4线程in/out；原地纯apply排除前置copy但另保留copy_apply数组。新hint与旧接口相同像素；cold不可由hot豁免。',
            'rss_scope': '另8新进程，2模型×2role×N1/100，每次构造不加载照片；记录RSS/peak_wset、nativecapacity/temporary，描述包装墙钟不作配对计时。',
            'sample_unit': '4workerABBA，320热记录×warm/measured/AA=960实际末组SHA；80冷记录×10句柄=800实际首组SHA，共1760输出核验。每worker中位配对，再四比中位；档按最劣worker吞吐。每冷metric/热边界独立.85..1.15 AA；无效全保留，禁止放宽/补测/改阈值。',
            'resources': 'ordinary低hint与87同容量，高hint额外16MiB；a399保持已有direct。输入含100图约236MB，各worker完整source/work和oracle照片预期非同时进程。allowedCPU0/2/4/6仅进程限制，非逐OMPTID绑定；无锁频温控/目标Intel实测，无AVX512。'})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
