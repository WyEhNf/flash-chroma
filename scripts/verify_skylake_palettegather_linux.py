"""仅用Python标准库核验LinuxRGB24小调色板gather52实际启用、ABI与完整RGB8输出；不含拟合、照片计时或Skylake实测结论。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import mmap
import os
from pathlib import Path
import platform
import random
import sys
import zipfile

from outplace_support import apply_to,reject_to
from guarded_buffer_support import guarded_apply
from paged_table_support import direct_info,paged_info,DirectInfo,PagedInfo
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def checked(spec):
    path = Path(spec['path'])
    if not path.is_absolute():
        path = ROOT/path
    if digest(path) != spec['sha256']:
        raise ValueError('输入字节不同：'+str(path))
    return path


def bind(path):
    d = ct.CDLL(str(path)); text = ct.POINTER(ct.c_char); u8 = ct.POINTER(ct.c_uint8)
    for name in ('abi_version', 'revision', 'capabilities'):
        f = getattr(d, 'jshc_cc_'+name); f.argtypes = []; f.restype = ct.c_uint32
    d.jshc_cc_create.argtypes = [ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.c_size_t,
                                ct.POINTER(ct.c_void_p), text, ct.c_size_t]
    d.jshc_cc_create.restype = ct.c_int
    d.jshc_cc_destroy.argtypes = [ct.c_void_p]; d.jshc_cc_destroy.restype = None
    d.jshc_cc_apply.argtypes = [ct.c_void_p, u8, ct.c_size_t, ct.c_int, ct.c_int, text, ct.c_size_t]
    d.jshc_cc_apply.restype = ct.c_int
    d.jshc_cc_model_bytes.argtypes = [ct.c_void_p]; d.jshc_cc_model_bytes.restype = ct.c_size_t
    return d


def create(d, models, sides):
    paths = (ct.c_char_p*len(models))(*(str(p).encode('utf-8') for p in models))
    fractions = (ct.c_char_p*len(models))(*(str(p).encode('utf-8') if p else None for p in sides))
    handle = ct.c_void_p(); error = ct.create_string_buffer(1024)
    if d.jshc_cc_create(paths, fractions, len(models), ct.byref(handle), error, len(error)):
        raise RuntimeError(error.value.decode('utf-8', errors='replace'))
    return handle


def apply(d, handle, source, kernel, threads, offset=0):
    storage = (ct.c_uint8*(len(source)+offset+17))()
    ct.memset(storage, 0xa7, len(storage)); address = ct.addressof(storage)+offset
    ct.memmove(address, source, len(source)); error = ct.create_string_buffer(1024)
    if d.jshc_cc_apply(handle, ct.cast(address, ct.POINTER(ct.c_uint8)), len(source), kernel, threads, error, len(error)):
        raise RuntimeError(error.value.decode('utf-8', errors='replace'))
    if bytes(storage[:offset]) != b'\xa7'*offset or bytes(storage[offset+len(source):]) != b'\xa7'*17:
        raise AssertionError('Linux非对齐/尾部哨兵被改写')
    return ct.string_at(address, len(source))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'build', 'single-oracle-stream', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--affinity-cpus', help='可选固定CPU集合；由服务器入口预先核对物理核/L3/NUMA')
    args = p.parse_args()
    if platform.system() != 'Linux' or not Path('/proc/self/maps').is_file():
        raise ValueError('此入口只核验Linux原生库，不把其他系统伪装为Linux')
    if args.affinity_cpus:
        cpus = {int(x) for x in args.affinity_cpus.split(',')}
        if not cpus or not cpus <= os.sched_getaffinity(0):
            raise ValueError('请求CPU不在允许集合')
        os.sched_setaffinity(0, cpus)
    plan = read(args.plan); build = read(args.build/'build.json')
    if build['plan_sha256'] != digest(args.plan) or build['source_sha256'] != plan['source_sha256']:
        raise ValueError('构建不属于冻结计划')
    sources = dict(plan['source_sha256']); sources['scripts/paged_table_support.py']=digest(ROOT/'scripts/paged_table_support.py'); sources['scripts/outplace_support.py']=digest(ROOT/'scripts/outplace_support.py'); sources['scripts/guarded_buffer_support.py']=digest(ROOT/'scripts/guarded_buffer_support.py'); sources[Path(__file__).resolve().relative_to(ROOT).as_posix()] = digest(__file__)
    for name, sha in sources.items():
        if digest(ROOT/name) != sha:
            raise ValueError('源码变动：'+name)
    fixed = {name: checked(plan['fixed_inputs'][name]) for name in ('base', 'sidecar', 'cube', 'prior_full', 'model')}
    suffix = [checked(s) for s in plan['suffix_models']]
    prior = read(fixed['prior_full'])
    single_sha = prior['native']['cube_sha256']['single_oracle']
    if digest(args.single_oracle_stream) != single_sha:
        raise ValueError('单级完整oracle流与已验独立u64输出不同')
    out = args.output.resolve()
    if out.exists():
        raise ValueError('不覆盖既有Linux证据')
    out.mkdir(parents=True)
    cpu = Path('/proc/cpuinfo').read_text().split('\n\n')[0]
    environment = {'platform': platform.platform(), 'python': sys.version, 'machine': platform.machine(),
        'cpu': cpu, 'initial_affinity': sorted(os.sched_getaffinity(0)),
        'thread_environment': {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OMP_DYNAMIC', 'OMP_PROC_BIND', 'OMP_PLACES')},
        'gather_data_sampling': Path('/sys/devices/system/cpu/vulnerabilities/gather_data_sampling').read_text().strip()
            if Path('/sys/devices/system/cpu/vulnerabilities/gather_data_sampling').is_file() else '系统未提供'}
    save(out/'run.json', {'purpose': __doc__, 'source_sha256': sources, 'environment': environment,
        'build_sha256': digest(args.build/'build.json'), 'plan_sha256': digest(args.plan),
        'single_oracle_stream': {'path': str(args.single_oracle_stream.resolve()), 'sha256': single_sha},
        'inputs': {name: plan['fixed_inputs'][name] for name in fixed}, 'suffix_models': plan['suffix_models']})
    with zipfile.ZipFile(out/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
        archive.write(args.plan, args.plan.resolve().relative_to(ROOT).as_posix())
    libraries = {}; operators = {}; counts = {}; hashes = {}; memory = {}; compiled_states = {}; exception_state = None; direct_state = None; pages_state = None; out_hashes = {}; out_counts = {}; out_finite=0; out_negative=0;guarded_count=0;alignment_count=0
    models = [fixed['base'], *suffix]; sides = [fixed['sidecar'], None, None, None]
    with fixed['cube'].open('rb') as cf, args.single_oracle_stream.open('rb') as sf:
        cube = mmap.mmap(cf.fileno(), 0, access=mmap.ACCESS_READ)
        single = mmap.mmap(sf.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            for name, spec in build['libraries'].items():
                d = bind(checked(spec)); libraries[name] = d
                if d.jshc_cc_abi_version() != 1 or d.jshc_cc_revision() != build['revisions'][name] or d.jshc_cc_capabilities() != 7:
                    raise ValueError('实际Linux ABI/AVX2/OpenMP/修订不符')
                operators[name] = {'single': create(d, models[:1], sides[:1]), 'chain': create(d, models, sides)}
                memory[name] = {mode: d.jshc_cc_model_bytes(h) for mode, h in operators[name].items()}
                if name=='candidate':
                    class PaletteInfo(ct.Structure):
                        _fields_=[(n,ct.c_uint32) for n in ('version','enabled','palette_size','reason')]+[(n,ct.c_uint64) for n in ('blocks','fast_blocks','table_capacity_bytes','temporary_peak_bytes')]+[('prepare_seconds',ct.c_double)]
                    f=d.jshc_cc_get_palette_info;f.argtypes=[ct.c_void_p,ct.POINTER(PaletteInfo),ct.c_size_t];f.restype=ct.c_int
                    for mode,h in operators[name].items():
                        value=PaletteInfo()
                        if f(h,ct.byref(value),ct.sizeof(value)) or value.version!=1:raise ValueError('Linux调色板诊断不同')
                        compiled_states[mode]={n:getattr(value,n) for n,_ in value._fields_}
                    if compiled_states['single']['enabled'] or compiled_states['chain']['enabled']!=1 or compiled_states['chain']['table_capacity_bytes']!=8388608:
                        raise ValueError('Linux新内核没有实际启用固定编码')

                if name=='candidate':
                    class ExceptionInfo(ct.Structure):
                        _fields_=[('version',ct.c_uint32),('enabled',ct.c_uint32),('entries',ct.c_uint64),('table_capacity_bytes',ct.c_uint64)]
                    f=d.jshc_cc_get_exception_info;f.argtypes=[ct.c_void_p,ct.POINTER(ExceptionInfo),ct.c_size_t];f.restype=ct.c_int
                    value=ExceptionInfo()
                    if f(operators[name]['chain'],ct.byref(value),ct.sizeof(value)):raise ValueError('Linux例外诊断失败')
                    exception_state={n:getattr(value,n) for n,_ in value._fields_}
                    if value.version!=1 or value.enabled!=1 or value.entries!=269708 or value.table_capacity_bytes!=1078832:
                        raise ValueError('Linux实际例外池与冻结模型不同')
                if name=='candidate':
                    h=operators[name]['chain'];direct_state=direct_info(d,h);pages_state=paged_info(d,h)
                    if direct_state['enabled']!=1 or direct_state['format']!=9 or direct_state['entries']!=2**22 or direct_state['table_capacity_bytes']!=2**24:
                        raise ValueError('新RGB32直表没有实际启用')
                    if direct_info(d,operators[name]['single'])['enabled']:raise ValueError('单级不应启用直表')
                    if pages_state['bytes']!=2**24 or not pages_state['aligned_2m']:raise ValueError('直表容量/对齐不符')
                    words=(ct.c_uint32*(2**22))();f=d.jshc_cc_copy_direct
                    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
                    if f(h,words,len(words)):raise ValueError('直表快照失败')
                    table_hash=hashlib.sha256(memoryview(words).cast('B')).hexdigest()
                    old_words=(ct.c_uint32*(2**21))();palette=(ct.c_uint32*256)()
                    copy_palette=d.jshc_cc_copy_palette;copy_palette.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t,ct.POINTER(ct.c_uint32),ct.c_size_t];copy_palette.restype=ct.c_int
                    if copy_palette(h,old_words,len(old_words),palette,256):raise ValueError('原精确调色板读取失败')
                    palette_rgb=tuple(int(v).to_bytes(4,'little')[:3] for v in palette)
                    raw_table=ct.string_at(words,2**24)
                    for red in range(256):
                        # 固定R后，物理次序为B外层/G内层；独立按坐标转回RGB次序。
                        plane=raw_table[red::256];ids=b''.join(plane[g::256] for g in range(256))
                        if max(ids)>=compiled_states['chain']['palette_size']:raise AssertionError('索引越过调色板')
                        start=red*65536
                        if b''.join(palette_rgb[i] for i in ids)!=cube[start*3:(start+65536)*3]:raise AssertionError('独立小端字节索引全表不符')
                    del old_words,raw_table
                    guard=(ct.c_uint32*8)(*[0xa7a7a7a7]*8)
                    for handle,pointer,count in [(None,guard,len(words)),(h,guard,len(words)-1),(h,None,len(words))]:
                        if f(handle,pointer,count)!=1 or list(guard)!=[0xa7a7a7a7]*8:raise AssertionError('直表拒绝写入')
                    for structure,function in [(DirectInfo,d.jshc_cc_get_direct_info),(PagedInfo,d.jshc_cc_get_paged_info)]:
                        v=structure();ct.memset(ct.byref(v),0xa7,ct.sizeof(v));before=bytes(v)
                        for handle,pointer,count in [(None,ct.byref(v),ct.sizeof(v)),(h,None,ct.sizeof(v)),(h,ct.byref(v),ct.sizeof(v)-1)]:
                            if function(handle,pointer,count)!=1 or bytes(v)!=before:raise AssertionError('页诊断拒绝写入')
                    del words
                for mode in operators[name]:
                    for kernel, threads in ((0, 1), (1, 1), (1, 4)):
                        key = f'{name}_{mode}_{kernel}_{threads}'; hashes[key] = hashlib.sha256(); counts[key] = 0;out_hashes[key]=hashlib.sha256();out_counts[key]=0
            # 固定尾部、非对齐与批边界；预期来自已经独立核验的完整输出流。
            rng = random.Random(2026102003)
            probe = bytes(rng.randrange(256) for _ in range(131073*3)); finite = 0
            for n in plan['contract']['lengths']:
                source = probe[:n*3]
                for name, d in libraries.items():
                    for mode, truth_stream in (('single', single), ('chain', cube)):
                        expected = b''.join(truth_stream[(source[i]*65536+source[i+1]*256+source[i+2])*3:
                            (source[i]*65536+source[i+1]*256+source[i+2])*3+3] for i in range(0, len(source), 3))
                        for kernel, threads in ((0, 1), (1, 1), (1, 4)):
                            for offset in plan['contract']['byte_offsets']:
                                if apply(d, operators[name][mode], source, kernel, threads, offset) != expected:
                                    raise AssertionError('Linux有限输入输出不同')
                                finite += 1
                                if apply_to(d,operators[name][mode],source,kernel,threads,offset,3-offset)!=expected:raise AssertionError('分离有限输出不同')
                                if apply_to(d,operators[name][mode],source,kernel,threads,offset,offset,same=True)!=expected:raise AssertionError('同址输出不同')
                                out_finite+=2
                                if offset==0 and kernel==1:
                                    if guarded_apply(d,operators[name][mode],source,kernel,threads)!=expected:raise AssertionError('分离保护页输出不同')
                                    if guarded_apply(d,operators[name][mode],source,kernel,threads,same=True)!=expected:raise AssertionError('同址保护页输出不同')
                                    guarded_count+=2
            for name,d in libraries.items():
                for h in operators[name].values():out_negative+=reject_to(d,h)
            alignment_source=probe[:257*3]
            alignment_expected=b''.join(cube[(alignment_source[i]*65536+alignment_source[i+1]*256+alignment_source[i+2])*3:(alignment_source[i]*65536+alignment_source[i+1]*256+alignment_source[i+2])*3+3] for i in range(0,len(alignment_source),3))
            for name,d in libraries.items():
                for threads in (1,4):
                    for target_offset in range(64):
                        for source_offset in range(4):
                            if apply_to(d,operators[name]['chain'],alignment_source,1,threads,source_offset,target_offset)!=alignment_expected:raise AssertionError('完整64种目标对齐输出不同')
                            alignment_count+=1
                        if apply_to(d,operators[name]['chain'],alignment_source,1,threads,target_offset,target_offset,same=True)!=alignment_expected:raise AssertionError('完整64种原地对齐输出不同')
                        alignment_count+=1
            # 262144像素覆盖四个新65536工作块，显式请求4可覆盖四块；RGB顺序完整遍历。
            gb = bytes(x for g in range(256) for b in range(256) for x in (g, b))
            for red in range(0,256,4):
                source = bytearray(4*65536*3); source[0::3] = b''.join(bytes([r])*65536 for r in range(red,red+4))
                source[1::3] = gb[0::2]*4; source[2::3] = gb[1::2]*4; source = bytes(source)
                start = red*65536*3; end = start+len(source)
                for name, d in libraries.items():
                    for mode, truth_stream in (('single', single), ('chain', cube)):
                        expected = truth_stream[start:end]
                        for kernel, threads in ((0, 1), (1, 1), (1, 4)):
                            actual = apply(d, operators[name][mode], source, kernel, threads)
                            if actual != expected:
                                raise AssertionError('Linux完整RGB8输出不同')
                            key = f'{name}_{mode}_{kernel}_{threads}'; hashes[key].update(actual); counts[key] += 4*65536
                            actual_to=apply_to(d,operators[name][mode],source,kernel,threads,1,3)
                            if actual_to!=expected:raise AssertionError('完整分离输出不同')
                            out_hashes[key].update(actual_to);out_counts[key]+=4*65536
            outputs = {key: value.hexdigest() for key, value in hashes.items()};out_outputs={key:value.hexdigest() for key,value in out_hashes.items()}
            loaded = []
            mapped = {Path(line.split(maxsplit=5)[-1]).resolve() for line in Path('/proc/self/maps').read_text().splitlines()
                      if '/' in line and Path(line.split(maxsplit=5)[-1]).is_file()}
            for spec in build['libraries'].values():
                if checked(spec).resolve() not in mapped:
                    raise ValueError('实际Linux映射缺少已验库')
            for path in sorted(mapped):
                if path.name.startswith(('libjshc_', 'libgomp.', 'libstdc++.', 'libgcc_s.', 'libc.', 'libm.')):
                    loaded.append({'path': str(path), 'sha256': digest(path)})
        finally:
            for name, handles in operators.items():
                for handle in handles.values():
                    libraries[name].jshc_cc_destroy(handle)
            cube.close(); single.close()
    assert memory['candidate']['single']-memory['reference']['single']==24
    assert memory['candidate']['chain']-memory['reference']['chain']==24+2**24
    for name, sha in sources.items():
        if digest(ROOT/name) != sha:
            raise ValueError('核验期间源码改变：'+name)
    save(out/'results.json', {'pass': True, 'purpose': __doc__, 'build_sha256': digest(args.build/'build.json'),
        'plan_sha256': digest(args.plan), 'libraries': build['libraries'], 'loaded_libraries': loaded,
        'full_input_chunk_pixels':262144,'finite_backend_offset_comparisons': finite, 'full_domain_pixels_per_configuration': counts,
        'output_sha256': outputs, 'byte_mismatches': 0, 'sentinel_mismatches': 0,
        'model_accounting_bytes': memory,'compiled_palette':compiled_states,'compiled_exceptions':exception_state,'stream_alignment_comparisons':alignment_count,'guarded_page_comparisons':guarded_count,'outplace_full_pixels':out_counts,'outplace_output_sha256':out_outputs,'outplace_finite_comparisons':out_finite,'outplace_negative_checks':out_negative,'direct_info':direct_state,'paged_info':pages_state,'direct_table_sha256':table_hash,'independent_table_colors':2**24,'direct_negative_checks':9, 'performance_calls': 0, 'photo_calls': 0, 'new_fits': 0,
        'scope': 'Linux实际主机见run.json；两库单级/四级的标量1与AVX2请求1/4完整字节比较。'
            '预期来自Windows已验独立u64/完整流；本脚本不重算独立oracle，不代表Skylake实机。'})
    print('Linux标准库入口通过：', finite, '个有限后端/偏移比较，12组完整RGB8输出一致', flush=True)


if __name__ == '__main__':
    main()
