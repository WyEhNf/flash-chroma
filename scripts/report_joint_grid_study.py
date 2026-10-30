"""归档已完成联合网格实验；逐图取舍与聚合结果同时保存。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('归档不覆盖已有目录')
    args.output.mkdir(parents=True)
    full_rows, photo_rows, files, scopes = [], [], {}, []
    with zipfile.ZipFile(args.output / 'evidence.zip', 'w', zipfile.ZIP_DEFLATED) as evidence, \
            zipfile.ZipFile(args.output / 'models.zip', 'w', zipfile.ZIP_DEFLATED) as models:
        for folder in args.runs:
            run = read(folder / 'run.json')
            selected = read(folder / 'selection.json')
            if selected['run_identity'] != run['identity_sha256']:
                raise ValueError('选择与运行身份不同')
            names = ['run.json', 'selection.json', 'samples.json', 'historical-full-results.json',
                     'measured-source.zip', 'full-results.json']
            names += sorted(p.name for p in folder.glob('*-optimizer.json'))
            for name in names:
                path = folder / name
                if path.is_file():
                    member = folder.name + '/' + name
                    evidence.write(path, member)
                    files['evidence/' + member] = sha(path)
            baseline = folder / 'baseline.slut'
            models.write(baseline, folder.name + '/baseline.slut')
            files['models/' + folder.name + '/baseline.slut'] = sha(baseline)
            plan = run['identity']['plan']
            scopes.append(plan['limits'])
            for name, candidate in selected['candidates'].items():
                path = folder / name / 'model.slut'
                if sha(path) != candidate['model_sha256']:
                    raise ValueError('冻结候选字节不同于选型身份')
                member = folder.name + '/candidates/' + name + '.slut'
                models.write(path,member)
                files['models/' + member] = sha(path)
            if 'initial_model' in plan:
                for key, member in (('initial_model','initial.slut'),('initial_grid','initial-grid.npy')):
                    path = ROOT / plan[key]
                    if sha(path) != plan[key+'_sha256']:
                        raise ValueError('优化起点身份不同')
                    member = folder.name + '/' + member
                    models.write(path,member)
                    files['models/' + member] = sha(path)
            grid = ROOT / plan['offline_grid']
            if sha(grid) != plan['offline_grid_sha256']:
                raise ValueError('原离线小数网格身份不同')
            member = folder.name + '/offline-grid.npy'
            models.write(grid, member)
            files['models/' + member] = sha(grid)
            for key in ('baseline_results', 'baseline_run'):
                path = ROOT / plan[key]
                if sha(path) != run['identity'][key + '_sha256']:
                    raise ValueError('历史父证据身份不同')
                member = folder.name + '/parent-' + key + '.json'
                evidence.write(path, member)
                files['evidence/' + member] = sha(path)
            if not (folder / 'full-results.json').is_file():
                continue
            result = read(folder / 'full-results.json')
            if result['run_identity'] != run['identity_sha256']:
                raise ValueError('终验与运行身份不同')
            entries = {'baseline': result['baseline'], **result['candidates']}
            for name, item in entries.items():
                for scope in ('cube', 'photos'):
                    v = item[scope]
                    full_rows.append({'run': folder.name, 'name': name, 'scope': scope,
                        'mean': v['mean'], 'rms': v['rms'],
                        'p99': v['p99'] if scope == 'cube' else v['worst_image_p99'], 'max': v['max'],
                        'cvar_1pct': v['cvar_1pct'] if scope == 'cube' else sum(r['cvar_1pct'] for r in v['per_image']) / 100,
                        'accepted': item.get('acceptance', {}).get('accepted', ''),
                        'model_sha256': run['identity']['plan']['baseline_sha256'] if name == 'baseline' else item['model_sha256']})
                for image in item['photos']['per_image']:
                    photo_rows.append({'run': folder.name, 'name': name, **image})
                if name != 'baseline':
                    path = folder / name / 'model.slut'
                    if sha(path) != item['model_sha256']:
                        raise ValueError('模型字节不同于终验身份')
                    member = folder.name + '/' + name + '.slut'
                    models.write(path, member)
                    files['models/' + member] = sha(path)
    for name, rows in (('metrics.csv', full_rows), ('photos.csv', photo_rows)):
        with (args.output / name).open('w', encoding='utf-8', newline='') as stream:
            fields = list(rows[0]) if rows else (['run', 'name', 'scope', 'mean', 'rms', 'p99', 'max', 'cvar_1pct']
                if name == 'metrics.csv' else ['run', 'name', 'image', 'mean', 'rms', 'p99', 'max', 'cvar_1pct'])
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader(); writer.writerows(rows)
    summary = ['# 网格与整数节点：冻结选择和完整验收记录', '',
        '距离为RGB8欧氏距离。照片p99栏是100图最差逐图p99；CVaR栏是平均逐图CVaR。均不代表官方Threshold或CIEDE2000。', '',
        '|批次/模型|范围|mean|RMS|p99|最大误差|CVaR1%|', '|---|---|---:|---:|---:|---:|---:|']
    for row in full_rows:
        summary.append(f"|{row['run']}/{row['name']}|{row['scope']}|{row['mean']:.6f}|{row['rms']:.6f}|{row['p99']:.6f}|{row['max']:.6f}|{row['cvar_1pct']:.6f}|")
    summary += ['', '逐图明细见photos.csv，不能将聚合门禁通过理解为每张照片均改善。models.zip保存全部冻结候选及对应基线；evidence.zip保存选型、环境、源码快照和实际存在的完整指标。', '',
        '本归档完整指标行数为' + str(len(full_rows)) + '；若为0，表示未执行本轮完整终验，不将CSV空表头当作完整结果。全部历史照片已见，不代表四级比赛、68LUT整体或新的运行时性能成绩；没有升级默认模型或创建PR。', '',
        '复现依赖冻结计划指定的历史缓存/原参考表。原始TIFF和照片来源已在仓库，完整颜色流可由对应序列化模型和现有cube入口重新生成；本归档不包含50MB颜色流及全部训练数组。']
    summary += ['', *dict.fromkeys(scopes)]
    (args.output / 'report.md').write_text('\n'.join(summary) + '\n', encoding='utf-8')
    for name in ('evidence.zip', 'models.zip', 'metrics.csv', 'photos.csv', 'report.md'):
        files[name] = sha(args.output / name)
    (args.output / 'sha256.json').write_text(json.dumps(files, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'runs': len(args.runs), 'metric_rows': len(full_rows), 'photo_rows': len(photo_rows),
        'output': str(args.output.resolve())}, ensure_ascii=False))


if __name__ == '__main__':
    main()
