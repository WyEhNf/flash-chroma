"""独立核暂存区或提交的交付字节及全部ZIP成员；不加载数值库/native。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='report/data/p16-cinema-cap40-complements-20261024/manifest.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',required=True,choices=('INDEX','HEAD'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖Git补集交付审核')
    def blob(name):
        spec=':'+name if args.revision=='INDEX' else 'HEAD:'+name
        return subprocess.run(['git','-c','gc.auto=0','-c','maintenance.auto=false','show',spec],
            cwd=ROOT,check=True,capture_output=True).stdout
    raw_manifest=blob(MANIFEST);manifest=json.loads(raw_manifest)
    assert manifest['passed'] and manifest['schema']=='p16_cap40_complement_delivery_v1'
    for name,expected in manifest['tracked_sha256'].items():
        assert digest(blob(name))==expected,name
    with zipfile.ZipFile(io.BytesIO(blob(manifest['archive']['path']))) as archive:
        assert archive.testzip() is None
        expected={**{'source/'+k:v for k,v in manifest['sources_sha256'].items()},
                  **{'raw/'+k:v['sha256'] for k,v in manifest['raw'].items()}}
        assert len(archive.namelist())==len(set(archive.namelist()))==manifest['archive']['members']==13
        assert set(archive.namelist())==set(expected)
        for name,value in expected.items():
            assert digest(archive.read(name))==value,name
        assert digest(blob('AGENTS.md'))==manifest['sources_sha256']['AGENTS.md']
        result=json.loads(archive.read('raw/results.json'))
        audit=json.loads(archive.read('raw/independent.json'))
        assert result['passed'] and audit['passed'] and audit['results_sha256']==manifest['results_sha256']
        assert result['point_counts']==dict(points=171271,dangerous_points=17620,empty_safe_points=0,
            all_positive_rows=1525836,all_negative_rows=187688,mixed_rows=182274,
            mixed_positive_points=307,mixed_negative_points=17313)
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    receipt=dict(passed=True,revision=args.revision,head=head,manifest_sha256=digest(raw_manifest),
        tracked_objects=len(manifest['tracked_sha256'])+1,source_rows=7,raw_rows=6,zip_members=13,
        actual_suffix_queries=0,solver_calls=0,native_calls=0,performance_samples=0,
        scope='Git实际blob、冻结只读AGENTS和ZIP逐成员CRC/SHA；不重跑数值，不替代完整历史交付审核。')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
