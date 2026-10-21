"""保存64静态淘汰和65完整域、计数、墙钟原件，不覆盖已存在档案。"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILDS = ('skylake-id-batch8-linux-build-v1', 'skylake-id-batch4-linux-build-v1')
OTHERS = ('skylake-id-batch4-linux-full-v1', 'skylake-id-batch4-pmu-v1',
          'skylake-id-batch4-quiet-perf-v1')
EXTRA = ('skylake-id-batch8-asm.txt', 'skylake-id-batch4-asm.txt')
BUILD_FILES = ('build-log.json', 'build.json', 'compile_commands.json',
               'libraries-Release.json', 'measured-source.zip')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for name in BUILDS:
        source, target = ROOT / 'artifacts' / name, HERE / name
        if target.exists():
            raise ValueError('不得覆盖既有构建档案：' + str(target))
        target.mkdir()
        chosen = [*BUILD_FILES, *sorted(p.name for p in source.glob('libjshc*.so'))]
        for filename in chosen:
            shutil.copy2(source / filename, target / filename)
        with zipfile.ZipFile(target / 'build-intermediates.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for path in sorted(source.rglob('*')):
                if path.is_file() and path.name not in chosen:
                    z.write(path, path.relative_to(source).as_posix())
    for name in OTHERS:
        source, target = ROOT / 'artifacts' / name, HERE / name
        if target.exists():
            raise ValueError('不得覆盖既有计数档案：' + str(target))
        shutil.copytree(source, target)
    with zipfile.ZipFile(HERE / 'static-asm.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in EXTRA:
            z.write(ROOT / 'artifacts' / name, name)
    paths = [p for name in (*BUILDS, *OTHERS) for p in (HERE / name).rglob('*') if p.is_file()]
    paths.append(HERE / 'static-asm.zip')
    files = {p.relative_to(HERE).as_posix(): {'bytes': p.stat().st_size, 'sha256': digest(p)}
             for p in sorted(paths)}
    (HERE / 'manifest.json').write_text(json.dumps({'schema': 1, 'files': files},
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    pmu = json.loads((HERE / 'skylake-id-batch4-pmu-v1/results.json').read_text(encoding='utf-8'))
    by = {(r['variant'], r['requested_threads']): r for r in pmu['records']}
    cycle_ratios = {str(n): by[('batch4_65', n)]['cycles_per_pixel'] / by[('reference40', n)]['cycles_per_pixel']
                    for n in (1, 4)}
    wall = json.loads((HERE / 'skylake-id-batch4-quiet-perf-v1/results.json').read_text(encoding='utf-8'))
    wall_ratios = {str(r['requested_threads']): {'apply': r['median_apply_ratio'],
        'outplace': r['median_outplace_ratio']} for r in wall['paired']}
    full = json.loads((HERE / 'skylake-id-batch4-linux-full-v1/results.json').read_text(encoding='utf-8'))
    audit = {'full_rgb8_pass': full['pass'], 'independent_colors': full['independent_table_colors'],
        'finite_comparisons': full['finite_backend_offset_comparisons'],
        'cycle_ratios_65_over_40': cycle_ratios,
        'incremental_screen_pass': cycle_ratios['1'] <= 0.95 and cycle_ratios['4'] <= 1.05,
        'counter_running_fraction_acceptable': all(r['multiplexing_acceptable'] for r in pmu['records']),
        'paired_wall_ratios_65_over_23': wall_ratios,
        'wall_threefold_pass': all(x['apply'] <= 1/3 and x['outplace'] <= 1/3 for x in wall_ratios.values()),
        'reported_wall_accepted': wall['accepted_on_this_host'],
        'failed_gates': wall['failed_gates'],
        'revision64_static_rejected': True,
        'note': '64宽循环每8像素发生栈溢出，静态淘汰；65仅一次冻结墙钟，未重测择优。'}
    (HERE / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'audit': audit}, ensure_ascii=False))


if __name__ == '__main__':
    main()
