"""Skylake研究的构建身份、实际动态库来源与环境记录，不含像素映射。"""
from __future__ import annotations
import ctypes as ct
import hashlib
import json
from pathlib import Path
import platform
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
sys.path.insert(0, str(ROOT/'experiments/channel-runtime'))
from channel_native import Library
from lutlab import study_provenance


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def checked(spec):
    p = Path(spec['path'])
    if not p.is_absolute():
        p = ROOT/p
    if digest(p) != spec['sha256']:
        raise ValueError('冻结输入字节不同：'+str(p))
    return p


def build_libraries(plan_path, build_dir):
    plan = read(plan_path); build_path = Path(build_dir)/'build.json'; build = read(build_path)
    if build['plan_sha256'] != digest(plan_path) or build['source_sha256'] != plan['source_sha256']:
        raise ValueError('构建与计划的身份不同')
    for name, sha in plan['source_sha256'].items():
        if digest(ROOT/name) != sha:
            raise ValueError('构建后源码变化：'+name)
    libraries = {name: Library(checked(spec), spec['sha256']) for name, spec in build['libraries'].items()}
    for name, lib in libraries.items():
        if lib.capabilities != 7 or lib.revision != build['revisions'][name]:
            raise ValueError('需要实际AVX2/OpenMP及冻结修订：'+name)
    return plan, build, libraries, loaded_sources(build)


def loaded_sources(build):
    specs = [*build['libraries'].values()]
    folder = Path(next(iter(build['libraries'].values()))['path']).parent
    specs += [{'path': str(folder/name), 'sha256': sha} for name, sha in build['dependencies'].items()]
    records = []
    if sys.platform == 'win32':
        kernel = ct.WinDLL('kernel32', use_last_error=True)
        get_module = kernel.GetModuleHandleW
        get_module.argtypes = [ct.c_wchar_p]; get_module.restype = ct.c_void_p
        get_name = kernel.GetModuleFileNameW
        get_name.argtypes = [ct.c_void_p, ct.c_wchar_p, ct.c_uint32]; get_name.restype = ct.c_uint32
        for spec in specs:
            p = checked(spec); handle = get_module(p.name)
            if not handle:
                raise OSError('预期动态库未实际载入：'+p.name)
            buf = ct.create_unicode_buffer(32768); n = get_name(handle, buf, len(buf))
            if not n or n >= len(buf):
                raise OSError('实际动态库路径读取失败')
            actual = Path(buf.value)
            if digest(actual) != spec['sha256']:
                raise ValueError('实际已载动态库字节不同：'+p.name)
            records.append({'path': str(actual), 'sha256': spec['sha256']})
    elif Path('/proc/self/maps').is_file():
        actual = {Path(line.split()[-1]).resolve() for line in Path('/proc/self/maps').read_text().splitlines()
                  if '/' in line and Path(line.split()[-1]).is_file()}
        for spec in specs:
            p = checked(spec).resolve()
            if p not in actual:
                raise ValueError('Linux实际映射不含指定库：'+str(p))
            records.append({'path': str(p), 'sha256': spec['sha256']})
        for p in sorted(actual):
            if p.name.startswith(('libgomp.', 'libstdc++.', 'libgcc_s.', 'libc.', 'libm.')):
                records.append({'path': str(p), 'sha256': digest(p), 'kind': 'loaded_system_dependency'})
    else:
        raise ValueError('尚未支持此系统的实际动态库来源校验')
    return records


def environment():
    value = study_provenance.environment_fingerprint()
    value['target_status'] = '本机AMD可行性；不能替代Skylake服务器验收' if 'AMD' in value['cpu_name'] else '须结合具体CPU/系统判断目标'
    if Path('/proc/cpuinfo').is_file():
        first = Path('/proc/cpuinfo').read_text().split('\n\n')[0]
        fields = ('vendor_id', 'cpu family', 'model', 'stepping', 'microcode', 'flags')
        value['cpu_details'] = {k.strip(): v.strip() for line in first.splitlines() if ':' in line
                                for k, v in [line.split(':', 1)] if k.strip() in fields}
        gds = Path('/sys/devices/system/cpu/vulnerabilities/gather_data_sampling')
        value['gather_data_sampling'] = gds.read_text().strip() if gds.is_file() else '系统未提供；没有修改缓解状态'
    else:
        value['gather_data_sampling'] = '未通过此脚本取得Windows微码/缓解状态；没有修改安全缓解设置'
    return value


def claim(out, plan_path, names, extra=None):
    out = Path(out).resolve()
    if out.exists():
        raise ValueError('新阶段输出不得覆盖旧证据：'+str(out))
    out.mkdir(parents=True)
    names = sorted(set([*names, 'scripts/skylake_support.py', Path(plan_path).resolve().relative_to(ROOT).as_posix()]))
    sources = {n: digest(ROOT/n) for n in names}
    identity = {'source_sha256': sources, 'environment': environment(), **(extra or {})}
    save(out/'run.json', identity)
    with zipfile.ZipFile(out/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for n in sources:
            archive.write(ROOT/n, n)
    return out, identity


def unchanged(identity):
    for n, sha in identity['source_sha256'].items():
        if digest(ROOT/n) != sha:
            raise ValueError('运行期间源码改变：'+n)
