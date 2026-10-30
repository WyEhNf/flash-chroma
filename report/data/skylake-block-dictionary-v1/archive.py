"""保存70完整色域、三份有效计数及原中止回执，不补造完整性能结果。"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    name = 'skylake-block-dictionary-linux-build-v1'
    source, target = ROOT / 'artifacts' / name, HERE / name
    if target.exists():
        raise ValueError('不得覆盖已归档构建')
    target.mkdir()
    chosen = ['build-log.json', 'build.json', 'compile_commands.json',
              'libraries-Release.json', 'measured-source.zip', *sorted(p.name for p in source.glob('libjshc*.so'))]
    for filename in chosen:
        shutil.copy2(source / filename, target / filename)
    with zipfile.ZipFile(target / 'build-intermediates.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(source.rglob('*')):
            if p.is_file() and p.name not in chosen:
                z.write(p, p.relative_to(source).as_posix())
    paths = [p for p in target.rglob('*') if p.is_file()]
    for name in ('skylake-block-dictionary-linux-full-v1', 'skylake-block-dictionary-pmu-v1',
            'skylake-block-dictionary-readonly-v1', 'skylake-palette-decode-readonly-v1'):
        source, target = ROOT / 'artifacts' / name, HERE / name
        if target.exists():
            raise ValueError('不得覆盖既有档案')
        shutil.copytree(source, target)
        paths.extend(p for p in target.rglob('*') if p.is_file())
    with zipfile.ZipFile(HERE / 'static-asm.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT / 'artifacts/skylake-block-dictionary-asm.txt', 'skylake-block-dictionary-asm.txt')
    paths.append(HERE / 'static-asm.zip')
    files = {p.relative_to(HERE).as_posix(): {'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(paths)}
    (HERE / 'manifest.json').write_text(json.dumps({'schema': 1, 'files': files}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    full = read(HERE / 'skylake-block-dictionary-linux-full-v1/results.json')
    pmu = HERE / 'skylake-block-dictionary-pmu-v1'
    a, b = read(pmu / 'sample-1-reference65.json'), read(pmu / 'sample-1-block_dictionary70.json')
    samples = [read(p) for p in sorted(pmu.glob('sample-*.json'))]
    assert len(samples) == 3 and not (pmu/'results.json').exists()
    audit = {'full_rgb8_pass': full['pass'], 'dictionary': full['block_dictionary'],
        'model_accounting_bytes': full['model_accounting_bytes'],
        'one_thread_cycle_ratio_over65': b['cycles_per_pixel']/a['cycles_per_pixel'],
        'one_thread_screen_pass': b['cycles_per_pixel']/a['cycles_per_pixel'] <= 1.03,
        'completed_counted_samples': len(samples),
        'valid_completed_samples': all(r['multiplexing_acceptable'] for r in samples),
        'pmu_series_complete': False, 'four_thread_ratio': None, 'wallclock_executed': False,
        'failure_receipt': read(pmu/'failure-receipt.json'),
        'note': '参考4线程前置状态断言失败；缺失数据不填零、不拼接其他场次，单线程已失败，停止且无补测。'}
    (HERE/'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'one_thread_ratio': audit['one_thread_cycle_ratio_over65'],
        'full_rgb8_pass': full['pass'], 'pmu_series_complete': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
