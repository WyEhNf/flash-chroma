"""93结束后归档原字节、固定模型和支持源码；不加载DLL或重测。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def pack(path, members):
    rows = []
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED) as z:
        for name, file in sorted(members.items()):
            raw = file.read_bytes()
            z.writestr(name, raw)
            rows.append({'member': name, 'bytes': len(raw), 'sha256': sha(raw)})
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert all(sha(z.read(r['member'])) == r['sha256'] for r in rows)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('93首次归档不覆盖')
    a.output.mkdir(parents=True)
    perf, quality = [ROOT / 'artifacts' / v for v in ('p16-default-layout-performance-v1', 'p16-default-layout-quality-v1')]
    plan = json.loads((perf / 'executed-plan.json').read_text(encoding='utf-8'))
    assert sha((perf / 'executed-plan.json').read_bytes()) == '22fd615b8aed01808f2f56896b38ebed4331095875fcd74a7c19c2431e7134e4'
    assert sha((quality / 'quality.json').read_bytes()) == plan['quality_proof']['sha256']
    for name in ('results.json', 'executed-plan.json', 'offline-audit.json'):
        shutil.copyfile(perf / name, a.output / name)
    shutil.copyfile(quality / 'quality.json', a.output / 'quality.json')
    raw = {f.relative_to(perf).as_posix(): f for f in perf.rglob('*') if f.is_file()}
    raw.update({'quality/' + f.relative_to(quality).as_posix(): f for f in quality.rglob('*') if f.is_file()})
    raw['preflight.json'] = ROOT / 'artifacts/p16-default-layout-preflight-v1.json'
    save(a.output / 'raw-members.json', pack(a.output / 'raw-evidence.zip', raw))
    prior = json.loads((ROOT / 'report/data/p16-workload-v1/identity.json').read_text(encoding='utf-8'))
    sources = {}
    for row in prior['execution_dependencies']:
        f = ROOT / row['path']
        assert sha(f.read_bytes()) == row['execution_sha256'], str(f)
        sources[row['path']] = f
    for row in plan['sources']:
        f = Path(row['path'])
        assert sha(f.read_bytes()) == row['sha256']
        sources[f.relative_to(ROOT).as_posix()] = f
    own = [*list((ROOT / 'experiments/p16-default-layout').glob('*')),
        ROOT / 'experiments/p16-default-layout-quality-v1.json', ROOT / 'experiments/p16-default-layout-performance-v1.json',
        ROOT / 'scripts/archive_p16_default_layout.py']
    for f in own:
        sources[f.relative_to(ROOT).as_posix()] = f
    rows = pack(a.output / 'execution-sources.zip', sources)
    save(a.output / 'source-members.json', rows)
    models = {}
    for row in plan['model']['models']:
        f = Path(row['path'])
        assert sha(f.read_bytes()) == row['sha256']
        models[f.relative_to(Path('F:/Hackathon/projects/16-lut-color')).as_posix()] = f
    save(a.output / 'model-members.json', pack(a.output / 'models.zip', models))
    shutil.copyfile(ROOT / 'experiments/p16-default-layout/machine-equivalence-v1.json', a.output / 'machine-equivalence.json')
    identity = {'date_asia_shanghai': '2026-10-24', 'parent_head': '7c904ea', 'libraries': plan['libraries'],
        'sources': {row['member']: row['sha256'] for row in rows},
        'source_scope': '沿92执行源及保守Python包支持闭包，补93诊断/冻结/audit/归档/计划与静态附录；不声称每个支持模块执行。ZIP为工作树执行原字节。',
        'prior_source_relations': {row['path']: {'parent7e3ef88_blob_sha256': row['parent_git_blob_sha256'],
            'execution_sha256': row['execution_sha256'], 'relation': row['relation']} for row in prior['execution_dependencies']},
        'native_reference_identity': '3210857:report/data/p16-prepare-simd-v1/identity.json',
        'native_candidate_identity': '7c904ea:report/data/p16-workload-v1/identity.json',
        'native_build_scope': '没有新编译；复用原87/92 DLL，既有构建flags/obj.d/链接元数据各保留在对应阶段。',
        'qualification_scope': '单一ordinary N1默认缓存的原因辨别；不改92阈值、80档、失效或原产品接口，不作频率/全部heap/ASLR因果。'}
    save(a.output / 'identity.json', identity)
    (a.output / 'README.md').write_text('''# 93默认小N原因辨别原字节

保留4worker全部2构造序×2对句柄×2共同work布局×2角色顺序，未筛选或补跑。两顺序原生边界数相同，每role各63正式/AA轮；2432块末实际SHA和16384整首图内轮全留。原92有效80档及失效没有恢复，研究10%交互线不是用户50底线或因果证明。

raw-evidence.zip保存全部原始JSON/partial/短质量/预检；execution-sources.zip为当前执行与保守支持源原字节，source-members逐SHA；models.zip只有固定ordinary四级稀疏模型，不打包照片/目标LUT。没有新原生代码或构建，87/92源与构建身份引用各既有阶段。静态机器码附录只证明相同对象及归一化指令，不证明运行时布局相同。

离线复算：python scripts/audit_p16_default_layout.py report/data/p16-default-layout-v1/raw-evidence.zip。不加载DLL，不追加测试。Git stage/HEAD另逐blob核执行原字节与既有CRLF/LF关系。
''', encoding='utf-8')
    save(a.output / 'manifest.json', {'files': [{'path': f.name, 'bytes': f.stat().st_size, 'sha256': sha(f.read_bytes())}
        for f in sorted(a.output.iterdir()) if f.is_file()]})
    print(json.dumps({'raw_members': len(raw), 'execution_source_members': len(rows), 'fixed_models': len(models)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
