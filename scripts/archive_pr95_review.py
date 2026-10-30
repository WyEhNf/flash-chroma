"""归档 PR95 审查的小体积原始证据，或只读校验归档；不重跑数值实验。"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/pr95-review'
DEST = ROOT / 'report/pr95-review-20261028/evidence'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def archive():
    if DEST.exists():
        raise FileExistsError('归档目录已存在，拒绝覆盖；可使用 --verify 检查')
    names = ['plan.json', 'results.json', 'completed.json', 'supplement-plan.json',
             'supplement-results.json', 'supplement-completed.json', 'audit-manifest.json',
             'binding-repro/result.json', 'binding-repro/catalog.json', 'binding-repro/selection.json']
    paths = [SOURCE/name for name in names]
    paths += sorted(SOURCE.glob('*.log'))
    paths += sorted(SOURCE.glob('*/source-manifest.json'))
    paths += sorted(SOURCE.glob('*/started.json'))
    records = []
    for source in paths:
        relative = source.relative_to(SOURCE)
        target = DEST/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = source.read_bytes()
        transform = '原字节复制'
        if source.suffix == '.log':
            if payload.startswith((b'\xff\xfe', b'\xfe\xff')):
                payload = payload.decode('utf-16').encode('utf-8')
                transform = 'PowerShell UTF16日志转UTF8，保留原字符和换行'
            else:
                payload.decode('utf-8')
        target.write_bytes(payload)
        records.append({'path': relative.as_posix(), 'source_sha256': digest(source),
                        'sha256': digest(target), 'bytes': len(payload), 'transform': transform})
    for source in sorted(SOURCE.glob('*-full-hist.npy')):
        histogram = np.load(source, allow_pickle=False)
        target = DEST/(source.stem+'.json')
        target.write_text(json.dumps({'length': len(histogram), 'dtype': str(histogram.dtype),
                          'nonzero': [[int(i), int(histogram[i])] for i in np.flatnonzero(histogram)]},
                          separators=(',', ':'))+'\n', encoding='utf-8')
        records.append({'path': target.name, 'source_sha256': digest(source),
                        'sha256': digest(target), 'bytes': target.stat().st_size,
                        'transform': 'int64直方图非零项无损JSON；下标为RGB平方误差'})
    save(DEST/'manifest.json', {'reviewed_commit': 'fb7e195215f14df9f635394d75cde0e0e69c82c9',
         'scope': '已有实验的归档，不是新执行或编译回执；原绝对路径保留为历史来源',
         'omitted': ['源照片和LUT已在仓库', '本地DLL/对象文件', '25张稠密RGB8表', '新拟合SLUT二进制，可按已归档参数重建'],
         'scripts': {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted((ROOT/'scripts').glob('review_pr95_*.py'))},
         'files': records})


def verify():
    manifest = read(DEST/'manifest.json')
    for row in manifest['files']:
        path = DEST/row['path']
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], row['path']
    for path, sha in manifest['scripts'].items():
        assert digest(ROOT/path) == sha, path
    rows = read(DEST/'results.json') + read(DEST/'supplement-results.json')
    assert len(rows) == 20
    assert sum(c['status'] == 'ok' for r in rows for c in r['configs']) == 78
    assert sum(c['status'] == 'capacity' for r in rows for c in r['configs']) == 22
    assert all(r['c99_probe_mismatches'] == 0 for r in rows)
    assert all(c['probe_mismatches'] == c['photo_mismatches'] == 0
               for r in rows for c in r['configs'] if c['status'] == 'ok')
    for row in rows:
        if 'full_domain' not in row:
            continue
        sparse = read(DEST/(row['chain']+'-m33-full-hist.json'))
        hist = np.zeros(sparse['length'], dtype=sparse['dtype'])
        for index, count in sparse['nonzero']:
            hist[index] = count
        full = row['full_domain']
        assert int(hist.sum()) == full['colors'] == 256**3
        assert abs(float(hist@np.sqrt(np.arange(len(hist)))/hist.sum())-full['mean']) < 1e-12
        assert float(np.sqrt(np.flatnonzero(hist)[-1])) == full['max']
    assert read(DEST/'binding-repro/result.json')['reproduced'] is True
    print(json.dumps({'passed': True, 'archived_files': len(manifest['files']),
                      'models': len(rows), 'successful_configs': 78, 'capacity_rejections': 22,
                      'scope': '归档SHA、计数及完整域直方图复算；未重跑像素映射/性能'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='只读检查已有归档')
    args = parser.parse_args()
    if not args.verify:
        archive()
    verify()
