"""保存66至69的构建、全域、单次计数与67首次墙钟；拒绝覆盖。"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
VARIANTS = ('chroma-batch4', 'chroma-batch4-io', 'inplace-t0', 'interleaved')
BUILD_FILES = ('build-log.json', 'build.json', 'compile_commands.json',
               'libraries-Release.json', 'measured-source.zip')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    paths = []
    for variant in VARIANTS:
        name = 'skylake-' + variant
        source = ROOT / 'artifacts' / (name + '-linux-build-v1')
        target = HERE / source.name
        if target.exists():
            raise ValueError('不得覆盖构建档案：' + str(target))
        target.mkdir()
        chosen = [*BUILD_FILES, *sorted(p.name for p in source.glob('libjshc*.so'))]
        for filename in chosen:
            shutil.copy2(source / filename, target / filename)
        with zipfile.ZipFile(target / 'build-intermediates.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(source.rglob('*')):
                if p.is_file() and p.name not in chosen:
                    z.write(p, p.relative_to(source).as_posix())
        paths.extend(p for p in target.rglob('*') if p.is_file())
        for suffix in ('-linux-full-v1', '-pmu-v1'):
            source = ROOT / 'artifacts' / (name + suffix)
            target = HERE / source.name
            if target.exists():
                raise ValueError('不得覆盖验证或计数档案：' + str(target))
            shutil.copytree(source, target)
            paths.extend(p for p in target.rglob('*') if p.is_file())
    for name in ('skylake-chroma-batch4-io-quiet-perf-v1', 'skylake-interleaved-readonly-v1'):
        source, target = ROOT / 'artifacts' / name, HERE / name
        if target.exists():
            raise ValueError('不得覆盖既有档案：' + str(target))
        shutil.copytree(source, target)
        paths.extend(p for p in target.rglob('*') if p.is_file())
    with zipfile.ZipFile(HERE / 'static-asm.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in ('skylake-chroma-batch4-asm.txt', 'skylake-chroma-batch4-io-asm.txt'):
            z.write(ROOT / 'artifacts' / name, name)
    paths.append(HERE / 'static-asm.zip')
    files = {p.relative_to(HERE).as_posix(): {'bytes': p.stat().st_size, 'sha256': digest(p)}
             for p in sorted(paths)}
    (HERE / 'manifest.json').write_text(json.dumps({'schema': 1, 'files': files},
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    rows = []
    for number, variant, label in ((66, VARIANTS[0], 'chroma_batch4_66'),
            (67, VARIANTS[1], 'chroma_batch4_67'), (68, VARIANTS[2], 'inplace_t0_68'),
            (69, VARIANTS[3], 'interleaved69')):
        name = 'skylake-' + variant
        full = read(HERE / (name + '-linux-full-v1') / 'results.json')
        pmu = read(HERE / (name + '-pmu-v1') / 'results.json')
        by = {(r['variant'], r['requested_threads']): r for r in pmu['records']}
        ratios = {str(n): by[(label, n)]['cycles_per_pixel'] / by[('reference65', n)]['cycles_per_pixel'] for n in (1, 4)}
        rows.append({'revision': number, 'full_rgb8_pass': full['pass'],
            'cycle_ratios_over65': ratios, 'screen_pass': ratios['1'] <= 1.03 and ratios['4'] <= .90,
            'pmu_valid': all(r['multiplexing_acceptable'] for r in pmu['records'])})
    wall = read(HERE / 'skylake-chroma-batch4-io-quiet-perf-v1/results.json')
    audit = {'variants': rows, 'revision67_wall': wall['paired'],
        'wall_accepted': wall['accepted_on_this_host'], 'failed_gates': wall['failed_gates'],
        'note': '所有首次结果保留；66/68/69筛查失败未运行完整墙钟；代理集合与静态指令不作为吞吐证明。'}
    (HERE / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'audit': audit}, ensure_ascii=False))


if __name__ == '__main__':
    main()
