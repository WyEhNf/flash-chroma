"""只读归档调色板研究的原始回执、源字节、二进制和协作检查；不运行像素核。"""
from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'report/data/skylake-palette-v1'
if OUT.exists():
    raise ValueError('不得覆盖历史档案')
OUT.mkdir(parents=True)

def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def copy_folder(name, label, patterns=('*.json', '*.zip', '*.log', '*.slut', '*.bin')):
    source = ROOT/'artifacts'/name; target = OUT/label; target.mkdir()
    for p in source.iterdir():
        if p.is_file() and any(p.match(pattern) for pattern in patterns):
            shutil.copyfile(p, target/p.name)

groups = {
    'skylake-palette-base-contract-v1': 'base-contract',
    'skylake-palette-cache-contract-v1': 'cache-contract',
    'skylake-palette-domain-contract-v1': 'domain-contract',
    'skylake-palette-packed-contract-v1': 'packed-contract',
    'skylake-palette-signed-contract-v1': 'signed-contract',
    'skylake-palette-fallback-contract-v1': 'failed-fallback-contract-v1',
    'skylake-palette-fallback-contract-v2': 'fallback-contract',
    'skylake-palette-full-v1': 'failed-full-v1',
    'skylake-palette-full-v2': 'full',
    'skylake-palette-linux-full-v1': 'linux-full',
    'skylake-palette-perf-v1': 'performance',
    'skylake-palette-audit-v1': 'audit',
}
for folder, label in groups.items():
    copy_folder(folder, label)
for folder, label in (('skylake-palette-build-v1', 'windows-build'),
                      ('skylake-palette-linux-build-v1', 'linux-build')):
    copy_folder(folder, label, ('build*.json', 'compile_commands.json', 'measured-source.zip', 'libraries-*.json'))
    source = ROOT/'artifacts'/folder
    with zipfile.ZipFile(OUT/label/'binaries-and-objects.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(source.rglob('*')):
            if p.is_file() and p.suffix in ('.dll', '.so', '.o', '.obj'):
                z.write(p, p.relative_to(source).as_posix())
copy_folder('skylake-palette-static-v1', 'static', ('*.json', '*.zip', '*.txt', '*.s', '*.asm'))
for file in ('profile_projection.py', 'profile_exact_runs.py', 'profile_palette_blocks.py',
             'profile_palette_blocks_v2.py'):
    target = OUT/'profiles'; target.mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'artifacts'/file, target/file)
for folder in ('skylake-projection-profile-v1', 'skylake-exact-runs-profile-v1',
               'skylake-palette-block-profile-v1', 'skylake-palette-block-profile-v2'):
    copy_folder(folder, 'profiles/'+folder, ('*.json',))
shutil.copyfile(__file__, OUT/'archive.py')
save(OUT/'failed-full-v1/failure.json', {'status': 'failed',
    'exception': 'ValueError: 调色板诊断ABI不同',
    'location': 'accept_skylake_palette.py回执构造中的palette_info(h)',
    'cause': '测试程序在with退出并销毁句柄后读取诊断；未生成results.json',
    'repair': '只将诊断读取移到句柄生命周期内；原生源/构建/模型未变，完整验收v2重跑；性能仅在v2通过后执行一次'})
save(OUT/'failed-fallback-contract-v1/failure.json', {'status': 'failed',
    'exception': 'ValueError: sparse nodes must have shape (m,m,m,3) and dtype uint8',
    'cause': '验证器把三轴grid数组当作单轴meshgrid输入',
    'repair': '按grid[0]/grid[1]/grid[2]分别构造；原生源与唯一性能不变；有限补验v2通过'})

remote = ROOT/'artifacts/skylake-palette-delivery-v1'
previous = ROOT/'artifacts/skylake-geometry-delivery-v1/final-refresh'
changed = []
for p in remote.glob('*.json'):
    if p.name not in ('repo.json', 'prs.json', 'issues.json', 'summary.json'):
        old = previous/p.name
        if not old.exists() or json.loads(p.read_text(encoding='utf-8')) != json.loads(old.read_text(encoding='utf-8')):
            changed.append(p.name)
assert not changed
prs = json.loads((remote/'prs.json').read_text(encoding='utf-8'))['items']
ancestry = {}
for commit in ('b19c5a0', '337a3dd', '876e15b8', '397cc367', '59586f7', '860d6bf', 'e3975ea'):
    ancestry[commit] = subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], cwd=ROOT).returncode == 0
assert all(ancestry.values())
with zipfile.ZipFile(OUT/'remote-snapshot.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(remote.glob('*.json')):
        z.write(p, p.name)
    z.write(remote/'fetch_remote.py', 'fetch_remote.py')
save(OUT/'remote-check.json', {'scope': '创建新Draft前获取全部PR/issue/正文/完整评论/review/行内线程/Discussion，复核既有相关意见与引用',
    'summary': json.loads((remote/'summary.json').read_text(encoding='utf-8')),
    'opinion_changes_since_prior_final_refresh': changed,
    'pr44': next({'head': p['head']['sha'], 'base': p['base']['ref'], 'draft': p['draft'], 'url': p['html_url']} for p in prs if p['number'] == 44),
    'included_commits': ancestry, 'fetched_main': subprocess.check_output(['git', 'rev-parse', 'github/main'], cwd=ROOT, text=True).strip(),
    'related': [
        {'url': 'https://github.com/WyEhNf/flash-chroma/pull/9#issuecomment-6213519540', 'status': '基线/环境修复337a3dd已包含；本轮模型/库/环境单独绑定'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/issues/7', 'status': '内核绑定修复337a3dd已包含；相关公共实现未改'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/pull/27#issuecomment-6229844096', 'status': '保护修复876e15b8已包含；固定模型且完整字节不变'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/pull/29', 'status': '相等mean修复397cc367已包含；本轮不拟合'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/pull/37#issuecomment-6230455676', 'status': '相关公共修复的历史集成证据；本轮不冒充重跑'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/discussions/4', 'status': '实现正确性与模型误差分列；无新评论'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/issues/8', 'status': '接口迁移/官方预算/实板待办保留，不关闭'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/pull/42', 'status': '固定同一a399模型与精度，不修改来源或训练'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/pull/43', 'status': '以其中较快已验16为唯一计时参考；不乘算历史收益'},
        {'url': 'https://github.com/WyEhNf/flash-chroma/pull/44', 'status': '五项静态停止保留；新22独立比较，依赖该分支'}],
    'unresolved': ['实际Skylake环境与性能', '官方侧表/派生缓存许可、内存预算和Threshold', 'issue8接口/实板与GUI40独立待办'],
    'decision': '保持Draft，不合并或关闭issue；当前已见意见与数值证据不存在本轮新增未披露阻塞',
    'redaction': '递归剔除API临时克隆元数据字段，不改正文/评论/数值证据'})

# 新Linux构建同样保留两套原AVX2对象的身份。
source = ROOT/'artifacts/skylake-palette-linux-build-v1'
objects = {}
for suffix in ('skylake-domain-isolated-runtime', 'skylake-suffix-cache-runtime'):
    paths = [p for p in source.rglob('channel_avx2.cpp.o') if suffix in p.parts]
    assert len(paths) == 2 and digest(paths[0]) == digest(paths[1])
    objects[suffix] = {'sha256': digest(paths[0]), 'paths': [p.relative_to(source).as_posix() for p in paths]}
save(OUT/'linux-fallback-object-proof.json', {'pass': True, 'objects': objects, 'scope': '同一新构建的原回退对象字节相同；不代表新构造器无成本'})

# 仅保存可再构造的小模型；不把完整域流或235MB照片流塞进Git。
plan = json.loads((ROOT/'experiments/skylake-palette-v1.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(OUT/'fixed-models.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for spec in [plan['fixed_inputs']['base'], plan['fixed_inputs']['sidecar'], *plan['suffix_models']]:
        assert digest(ROOT/spec['path']) == spec['sha256']
        z.write(ROOT/spec['path'], spec['path'])
save(OUT/'large-input-identities.json', {'not_in_git': True,
    'single_oracle': {'path': 'artifacts/skylake-domain-isolated-full-v1/first-stage.rgb',
        'bytes': 50331648, 'sha256': '7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146'},
    'chain_oracle': plan['fixed_inputs']['cube'],
    'photos': {'bytes': 235929600, 'sha256': 'e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd',
        'manifest': plan['fixed_inputs']['manifest']},
    'existing_packet': 'report/data/skylake-domain-server-v2/delivery-packet.json',
    'scope': '旧包包含上述相同SHA的大流；小模型归档不声称完整独立数据包'})
manifest = {'purpose': __doc__, 'files': {p.relative_to(OUT).as_posix():
    {'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(OUT.rglob('*')) if p.is_file()}}
save(OUT/'manifest.json', manifest)
print('归档文件数', len(manifest['files']), '总字节', sum(v['bytes'] for v in manifest['files'].values()))
