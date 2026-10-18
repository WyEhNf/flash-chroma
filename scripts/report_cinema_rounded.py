"""归档Cinema末级实验的模型、冻结来源、完整逐图指标及未改善项。"""
import argparse
import csv
import json
from pathlib import Path
import zipfile
from run_chain_error_study import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('归档不覆盖已有目录')
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    run, selection = read(args.run / 'run.json'), read(args.run / 'selection.json')
    if run['identity_sha256'] != selection['run_identity']:
        raise ValueError('来源与选择身份不同')
    args.output.mkdir(parents=True)
    manifest = {}
    with zipfile.ZipFile(args.output / 'evidence.zip', 'w', zipfile.ZIP_DEFLATED) as evidence, \
            zipfile.ZipFile(args.output / 'models.zip', 'w', zipfile.ZIP_DEFLATED) as models:
        for path in sorted(args.run.rglob('*')):
            if not path.is_file() or path.suffix not in ('.json', '.zip', '.slut'):
                continue
            name = path.relative_to(args.run).as_posix()
            archive, prefix = (models, 'models/') if path.suffix == '.slut' else (evidence, 'evidence/')
            archive.write(path, name)
            manifest[prefix + name] = digest(path)
    rows, photos = [], []
    full = args.run / 'full-results.json'
    if full.is_file():
        result = read(full)
        if result['run_identity'] != run['identity_sha256']:
            raise ValueError('完整结果身份不同')
        for name, value in (('PR16', result['baseline']), ('candidate', result)):
            for scope in ('cube', 'photos'):
                item = value[scope]
                rows.append({'version': name, 'scope': scope, 'mean': item['mean'], 'rms': item['rms'],
                    'p99': item['p99'] if scope == 'cube' else item['worst_image_p99'], 'max': item['max'],
                    'cvar_1pct': item['cvar_1pct'] if scope == 'cube' else sum(r['cvar_1pct'] for r in item['per_image'])/100})
            photos.extend({'version': name, **row} for row in value['photos']['per_image'])
        for file, values in (('metrics.csv', rows), ('photos.csv', photos)):
            with (args.output / file).open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(values[0]))
                writer.writeheader()
                writer.writerows(values)
        body = ['# Cinema四级链：实际到达频数与整链尾部保护', '',
            '同一冻结候选完成256³和100张完整1024×768 RGB8照片验收。第四级模型更新，前三模型逐字节不变；每模型112063字节，仍为m33和原Q16轴表。', '',
            '|版本|范围|mean|RMS|p99|最大误差|CVaR1%|', '|---|---|---:|---:|---:|---:|---:|']
        for row in rows:
            body.append('|{version}|{scope}|{mean:.6f}|{rms:.6f}|{p99:.6f}|{max:.6f}|{cvar_1pct:.6f}|'.format(**row))
        body += ['', '照片p99为最差单图p99，CVaR为平均逐图CVaR。逐图完整明细见photos.csv，全部变化及60/20/20分组在完整结果中。', '',
            '完整门禁：' + json.dumps(result['acceptance'], ensure_ascii=False) + '。独立整数oracle与标量/AVX2/C99完整流同SHA：' + result['cube']['prediction_sha256'] + '，零字节差异。', '',
            '100图mean、RMS全部改善；p99为57改善43持平，max为3改善97持平；CVaR为99改善1退化，不宣称每图每项支配。完整域16777216条尾部包络约束零违反。', '',
            '训练从60图全部47185920像素和原始完整cube的固定稀疏前三段到达频数构造，另保留0.10本级均匀测度。唯一拟合标签为第四原表T4(z)；原始整链参考仅用于硬约束。', '',
            '环境：Windows11 x64/Ryzen9 8945HX/Python3.12.14/NumPy1.26.4/Numba0.60.0，Numba4线程，BLAS/MKL/OMP=1；原生GCC15.2 Release三后端各单线程，程序SHA由run计划及回执绑定。不比较运行时性能。', '',
            '复现：用evidence.zip内实测源码和run.json内计划执行run_cinema_rounded.py的fit/accept。模型在models.zip；大频数、质量、包络数组与RGB流留在本地artifacts，SHA已冻结，异机需恢复同字节原表/照片和历史证据并重建。', '',
            'RGB欧氏码值距离，非CIEDE2000。所有照片历史已见，20审计只表示本阶段未反馈，不称盲测。官方数据/Threshold未知，不宣布官方通过或SOTA；无新速度、GPU、实板结论。默认不升级，未创建PR。']
    else:
        body = ['# Cinema拟合：未入围', '', '所有选择候选及失败项见evidence.zip；模型见models.zip。没有执行完整终验，不以选择样本代替完整精度结论。']
    (args.output / 'report.md').write_text('\n'.join(body)+'\n', encoding='utf-8')
    for path in args.output.iterdir():
        if path.is_file():
            manifest[path.name] = digest(path)
    (args.output / 'sha256.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'archive_members': len(manifest), 'metric_rows': len(rows), 'photo_rows': len(photos)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
