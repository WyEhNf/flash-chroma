"""静态核对18次配对计时回执并归档，不重新执行原生映射。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有性能归档')
    run, result = read(args.run/'run.json'), read(args.run/'results.json')
    identity = run['identity']
    expected = hashlib.sha256(json.dumps(identity,sort_keys=True,allow_nan=False).encode()).hexdigest()
    if run['identity_sha256'] != expected or result['run_identity'] != expected:
        raise ValueError('计时身份不一致')
    records = [read(p) for p in sorted(args.run.glob('threads*-cycle*.json'))]
    if len(records) != 18 or result['native_invocations'] != 18:
        raise ValueError('本阶段应有18个终态回执')
    versions = {row['name']: row for row in identity['versions']}
    for row in records:
        r = row['result']; v = versions[row['version']]
        if (r['kernel'] != identity['kernel'] or r['requested_threads'] != row['threads']
                or r['images'] != 100 or r['stages'] != 4 or r['reps'] != 5 or r['batch_mode']
                or r['executable_sha256'] != identity['executable_sha256']
                or list(r['models_sha256'].values()) != v['sha256']
                or len(r['set_ms_reps']) != 5 or len(r['apply_ms_reps']) != 5 or r['returncode'] != 0):
            raise ValueError('实际原生回执与冻结范围不同')
    for row in result['summary']:
        group = [r['result'] for r in records if r['version']==row['version'] and r['threads']==row['threads']]
        if len(group) != 3:
            raise ValueError('每组必须3个独立进程')
        for name, source in (('apply_ms_image_median','apply_ms_reps'),('copy_apply_ms_image_median','set_ms_reps')):
            measured = statistics.median(statistics.median(v[source])/100 for v in group)
            if abs(measured-row[name]) > 1e-12:
                raise ValueError('汇总不是集合中位/图数再跨进程中位')
    args.output.mkdir(parents=True)
    manifest = {}
    with zipfile.ZipFile(args.output/'evidence.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(args.run.glob('*.json')):
            archive.write(path,path.name); manifest['evidence/'+path.name]=digest(path)
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name, sha in identity['source_sha256'].items():
            path = ROOT/name
            if digest(path) != sha:
                raise ValueError('计时源码已变，必须恢复实际源码后才能归档')
            archive.write(path,name); manifest['source/'+name]=sha
        build = ROOT/'build-engineering-alignment/CMakeCache.txt'
        archive.write(build,'build/CMakeCache.txt'); manifest['source/build/CMakeCache.txt']=digest(build)
    (args.output/'report.md').write_text(args.report.read_text(encoding='utf-8'),encoding='utf-8')
    with (args.output/'metrics.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(result['summary'][0]));writer.writeheader();writer.writerows(result['summary'])
    audit = {'scope':'静态计时回执及聚合复算，不重映射、不执行性能调用',
        'native_invocations':len(records),'summary_rows_recomputed':len(result['summary']),
        'run_identity':expected,'source':str(args.run),'passed':True}
    (args.output/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for path in args.output.iterdir():
        if path.is_file():manifest[path.name]=digest(path)
    (args.output/'sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False))


if __name__=='__main__':
    main()
