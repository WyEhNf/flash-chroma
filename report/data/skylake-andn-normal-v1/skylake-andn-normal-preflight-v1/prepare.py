"""仅生成并冻结修订80源码/计划；不编译、不加载候选、不执行像素或性能。"""
import copy
import difflib
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD_NAME = 'experiments/skylake-pair48-runtime'
NEW_NAME = 'experiments/skylake-andn-normal-runtime'
OLD, NEW = ROOT / OLD_NAME, ROOT / NEW_NAME
OLD_PLAN = ROOT / 'experiments/skylake-pair48-v1.json'
NEW_PLAN = ROOT / 'experiments/skylake-andn-normal-v1.json'
NORMAL_BASE = ROOT / 'experiments/skylake-andn-split-runtime/andn_inplace/channel_avx2.cpp'
BASE_COMMIT = 'f82fb2d93edfdbc09b4997eb60a2b52befe5980e'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spec(path):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return dict(path=p.relative_to(ROOT).as_posix(), sha256=digest(p))


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def replace_once(data, old, new):
    assert data.count(old) == 1, old
    return data.replace(old, new)


def save_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    assert not NEW.exists() and not NEW_PLAN.exists() and not (HERE / 'preparation.json').exists(), '不得覆盖已准备候选'
    parent = load(OLD_PLAN)
    assert digest(OLD_PLAN) == 'a31c77dc7fc966c3314b5e1eda585fd1d11e840050314a78e9eb689b6c85c180'
    for name, expected in parent['source_sha256'].items():
        assert digest(ROOT / name) == expected, name
    assert digest(NORMAL_BASE) == 'dbb416074abf56734a2e894507c572b25e6a10bb30ee9409cbc359bb93fa336d'
    basis_paths = {
        'revision79_static': 'artifacts/skylake-pair48-static-v1/results-v2.json',
        'revision79_independent_static': 'artifacts/skylake-pair48-static-v1/independent-audit.json',
        'revision79_full': 'artifacts/skylake-pair48-linux-full-v1/results.json',
        'revision79_initial_long': 'artifacts/skylake-pair48-long-perf-v1/results.json',
        'g_low_protocol': 'artifacts/skylake-g-low-profile-v1/protocol.json',
        'g_low_result': 'artifacts/skylake-g-low-profile-v1/results.json',
    }
    expected_basis = {
        'revision79_static': 'f081ad5e9fd3772c27a1b8900fdfc99d5524108e1947da39361e66fe94010efd',
        'revision79_independent_static': 'd56c26f6bb43869d0073103b18ff3bf591e98df7292386b22652ddb40323f917',
        'revision79_full': '41628bf768a3673a3f83afef75879315ea080465aa9ddd40d53e6688d93c108f',
        'revision79_initial_long': '2d00684c0a0eea66e37227318be3a972ea2e4bae34333c98a42a0eefba1b4db4',
        'g_low_protocol': '62e0695236d1035fadbd6e5c33e437f57efa523106e18a816bdd859619e4fb6e',
        'g_low_result': '43a10810b484a3c2a7f06b4be47e41578a2c65ab8d12203c6a6de08dcdccd0f7',
    }
    basis = {name: spec(path) for name, path in basis_paths.items()}
    assert all(v['sha256'] == expected_basis[k] for k, v in basis.items())
    prior_perf = load(ROOT / basis_paths['revision79_initial_long'])
    g_profile = load(ROOT / basis_paths['g_low_result'])
    assert prior_perf['measurement_completed'] and prior_perf['measurement_control_valid'] and not prior_perf['accepted_on_this_host']
    assert g_profile['pass'] and not g_profile['native_implementation_warranted']

    original = {p.relative_to(OLD).as_posix(): p.read_bytes() for p in OLD.rglob('*') if p.is_file()}
    assert len(original) == 10
    changed = dict(original)
    runtime = original['channel_runtime.cpp']
    nl = b'\r\n' if b'\r\n' in runtime else b'\n'
    runtime = runtime.replace(b'pair48_supported', b'andn_normal_supported')
    runtime = replace_once(runtime, b'jshc_cc_pair48_enabled', b'jshc_cc_andn_normal_enabled')
    runtime = replace_once(runtime, b'uint32_t jshc_cc_revision(void) {return 79;}', b'uint32_t jshc_cc_revision(void) {return 80;}')
    omp = b'  const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,static_cast<size_t>(threads)));' + nl + b'#pragma omp parallel for schedule(static) num_threads(workers)' + nl + b'#endif'
    runtime = replace_once(runtime, omp, omp[:-len(b'#endif')] + b'#else' + nl + b'  const int workers=1;' + nl + b'#endif')
    old_dispatch = b'          if(h.andn_normal_supported)jshc_channel::avx2_chain_pair48(h.direct_index.data(),h.output_palette.data(),data,vectorized);'
    new_dispatch = nl.join([
        b'          if(h.andn_normal_supported) {',
        '            // 依据有效工作线程选择；嵌套OpenMP或非OpenMP仍为单线程pair48。'.encode(),
        b'            if(workers>1)jshc_channel::avx2_chain_andn_normal_mt(h.direct_index.data(),h.output_palette.data(),data,vectorized);',
        b'            else jshc_channel::avx2_chain_pair48(h.direct_index.data(),h.output_palette.data(),data,vectorized);',
        b'          }'])
    runtime = replace_once(runtime, old_dispatch, new_dispatch)
    runtime = replace_once(runtime,
        '  // 表示本句柄AVX2原地及分离输出会选择ANDN；无表时原精确回退不使用该指令。'.encode(),
        '  // 仅报告BMI1与直接表允许两类ANDN路径；实际选择取决于有效workers和是否分离输出。'.encode())
    changed['channel_runtime.cpp'] = runtime

    header = original['suffix_cache.hpp']
    header_nl = b'\r\n' if b'\r\n' in header else b'\n'
    declaration = b'void avx2_chain_pair48(const uint32_t*,const uint32_t*,uint8_t*,size_t) noexcept;'
    header = replace_once(header, declaration, declaration + header_nl + b'void avx2_chain_andn_normal_mt(const uint32_t*,const uint32_t*,uint8_t*,size_t) noexcept;')
    header = replace_once(header, b'jshc_cc_pair48_enabled', b'jshc_cc_andn_normal_enabled')
    header = replace_once(header,
        '// 本句柄AVX2原地及分离输出是否会选择ANDN；空句柄或未构造线性表返回0。'.encode(),
        '// 只报告句柄BMI1与直接表资格，不表示每次调用均普通写；null或无表返回0。'.encode())
    changed['suffix_cache.hpp'] = header

    cmake = original['CMakeLists.txt'].replace(b'jshc_skylake_pair48', b'jshc_skylake_andn_normal')
    cmake_nl = b'\r\n' if b'\r\n' in cmake else b'\n'
    extra_after = b'  "${CMAKE_CURRENT_SOURCE_DIR}/andn_outplace/channel_avx2.cpp"'
    assert cmake.count(extra_after) == 2
    cmake = cmake.replace(extra_after, extra_after + cmake_nl + b'  "${CMAKE_CURRENT_SOURCE_DIR}/normal_inplace/channel_avx2.cpp"')
    cmake = replace_once(cmake,
        '# 三个像素TU同名以保留构建审计规则；两个ANDN独立入口TU获得BMI1许可。'.encode(),
        '# 四个像素TU同名以保留构建审计规则；两个原pair48及新普通写TU获得BMI1许可。'.encode())
    changed['CMakeLists.txt'] = cmake

    normal_original = NORMAL_BASE.read_bytes()
    normal = normal_original
    normal_nl = b'\r\n' if b'\r\n' in normal else b'\n'
    assert normal.count(b'_MM_HINT_NTA') == 5 and normal.count(b'_mm256_stream_si256') == 3
    normal = normal.replace(b'_MM_HINT_NTA', b'_MM_HINT_T0').replace(b'_mm256_stream_si256', b'_mm256_store_si256')
    normal = replace_once(normal, b'  bool streamed=false;' + normal_nl, b'')
    normal = replace_once(normal, b';streamed=true;', b';')
    normal = replace_once(normal,
        '  // 在普通尾部、调用方读取和OpenMP barrier之前发布非临时写入。'.encode() + normal_nl + b'  if(streamed)_mm_sfence();',
        '  // 此独立路径只有普通写，没有NT发布需要；原pair48路径仍保留自己的SFENCE。'.encode())
    normal = replace_once(normal, b'avx2_chain_andn_split(', b'avx2_chain_andn_normal_mt(')
    normal = normal.replace('NTA为提示'.encode(), 'T0为提示'.encode())
    normal = replace_once(normal,
        '  // 对齐到完整64字节缓存行，避免前缀普通写与非临时写共享同一行。'.encode(),
        '  // 保持原64字节目标对齐，六个普通32字节写恰好覆盖三个完整缓存行。'.encode())
    normal = replace_once(normal,
        b'inline __attribute__((always_inline)) void output_four_stream(',
        '// 保留既有预排与三条合并；本副本的stream命名沿用原函数，但存储已为普通对齐写。'.encode() + normal_nl + b'inline __attribute__((always_inline)) void output_four_stream(')
    assert b'_mm256_stream_si256' not in normal and b'_mm_sfence' not in normal and b'streamed=' not in normal
    changed['normal_inplace/channel_avx2.cpp'] = normal
    for rel in ('andn_inplace/channel_avx2.cpp', 'andn_outplace/channel_avx2.cpp', 'channel_avx2.cpp'):
        assert changed[rel] == original[rel]
    assert runtime.count(b'__builtin_cpu_supports("bmi")') == 1
    assert b'schedule(static,1)' not in runtime

    files, patch = [], []
    for rel, content in sorted(changed.items()):
        destination = NEW / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        parent_bytes = original.get(rel, b'')
        files.append(dict(path=destination.relative_to(ROOT).as_posix(), sha256=digest(destination),
                          same_bytes_as79=rel in original and content == parent_bytes,
                          parent_sha256=hashlib.sha256(parent_bytes).hexdigest() if rel in original else None))
        if content != parent_bytes:
            patch.extend(difflib.unified_diff(parent_bytes.decode().splitlines(keepends=True), content.decode().splitlines(keepends=True),
                                            fromfile=(OLD_NAME + '/' + rel) if rel in original else '/dev/null', tofile=NEW_NAME + '/' + rel))
    (HERE / 'source-diff.patch').write_bytes(''.join(patch).encode())
    (HERE / 'normal-vs78.patch').write_bytes(''.join(difflib.unified_diff(normal_original.decode().splitlines(keepends=True), normal.decode().splitlines(keepends=True),
        fromfile=NORMAL_BASE.relative_to(ROOT).as_posix(), tofile=NEW_NAME + '/normal_inplace/channel_avx2.cpp')).encode())

    plan = copy.deepcopy(parent)
    plan.update(purpose='修订80提案：按有效工作线程选择精确输入/输出路径；仅源码和构建计划冻结，未编译或执行原生',
                base_commit=BASE_COMMIT,
                candidate='单线程原地及全部真正分离输出保持79 pair48原字节；仅多线程原地采用78 mem32 ANDN、四ID先行、原预排合并、T0和普通对齐写，不交错分块',
                cmake_project=NEW_NAME, cmake_targets=['jshc_skylake_reference', 'jshc_skylake_andn_normal'], revisions=dict(reference=23, candidate=80))
    plan['unchanged'] = [
        '模型、Q16及逐级RGB8整数舍入、230项精确调色板、16MiB format9线性ID表；构造只读原模型，不读照片或gold',
        '79的andn_inplace/andn_outplace两个pair48 TU含原导出名逐字节复制；单线程原地及真正分离输出仍NTA/NT/SFENCE',
        '原线性回退TU逐字节保持79；一次构造BMI1检测，未支持BMI或无表时沿原精确回退，无环境强制开关',
        '65536像素连续schedule(static)块、嵌套OpenMP有效workers=1、64B目标对齐、64像素全部读取后写入及72/40宽读边界',
        '不新增表、Handle字段或拟合；仅复用既有bool并改名，新只读getter是资格信息而非实际执行路径探针',
        'fixed_inputs/suffix_models/contract/hardware/screen与79完全一致，纯映射和真实输出各1/4线程三倍及A/A/确认验收规则不变']
    plan['required_static_checks'] = [
        '三个保留像素TU源码保持79原字节；两个pair48对象全部.text与79对应对象相同，原线性回退对象也逐字节核对，不以文件名代替字节证据',
        '独立识别新normal原地64/32两个实际可达完整区段，分别64/32条mem32 ANDN（VEX.W0），精确m32输入、地址宽输出与消费时0xff000000掩码有效',
        '每8像素两组四ID屏障，所有64/32输入与调色板加载均早于该组首输出；全部lane组及预排合并语义维持78',
        '新normal64主体六个普通32B写，32尾三个普通32B写；只有T0输入提示，整个normal TU无NT/SFENCE；禁止把预排值交给旧普通output_four',
        '新normal宽区段无真实rsp/frame spill、无额外自MOV零扩展或循环内掩码重载；无外部call/gather/BMI2/EVEX/AVX512，rbp作为普通地址时单独辨别',
        '新normal m32最大宽读取193/97B分别小于72/40像素的216/120B；精确8像素尾只读24B；1024字节前瞻及406像素保护不变',
        '有效workers>1且具备BMI/直表的原地才选normal；单线程/嵌套/非OMP选pair48，真正分离始终pair48，无BMI保持原线性；同址apply_to仍委托原地',
        '仅andn_inplace、andn_outplace、normal_inplace三个TU加-mbmi；其他TU不泄漏BMI，像素TU仍-mavx2/-mtune=skylake/-ffp-contract=off；源哈希/对象字节/compile_commands绑定一致',
        '任何静态失败停止像素执行；通过后完整RGB8、有限/guard/align/API逐字节验证；完整域每批需>65536像素且4t确实覆盖normal',
        '小尺寸257像素对齐夹具只选workers=1，80验证须另补大于65536像素的原地偏移覆盖；旧1280项不能宣称覆盖新normal全部对齐']
    plan['preparation'] = dict(state='源码与构建计划已冻结；未编译、未执行原生或性能', parent_plan=spec(OLD_PLAN),
        normal_source_parent=spec(NORMAL_BASE), generator=spec(Path(__file__)), no_performance_claim=True,
        conditional_execution='由主流程先构建和静态审计；通过后独立完整正确性，之后才首次受控长批次，旧失败不重测')
    plan['prior_evidence'] = basis
    plan.pop('pair48', None)
    plan['andn_normal'] = dict(
        linear_format=9, entries=2**22, physical_bytes=2**24,
        readonly_api='显式JSHC_CC_API uint32_t jshc_cc_andn_normal_enabled(const void*)；null/无直接表返回0，仅报告BMI1和表资格，不保证当前调用为普通写',
        selection={'inplace_effective_workers_1': '原79 pair48 NTA/NT/SFENCE', 'inplace_effective_workers_gt1': '新78 mem32 ANDN T0/普通写/无SFENCE',
                   'true_outplace': '原79 pair48 NTA/NT/SFENCE', 'no_bmi': '原79线性回退', 'nested_or_no_openmp': '有效workers=1'},
        normal_input=dict(operand='mem32 ANDN，mask0xff000000，uintptr_t输出、%k0清高32位，aligned(1),may_alias、cc约束保持78',
                          offsets_per8=[0, 3, 6, 9, 12, 15, 18, 21], input_loads_per8=8, requested_input_bytes_per_pixel=4,
                          total_input_id_palette_loads_per_pixel=3, prior79_total_loads_per_pixel=2.5),
        normal_output='保留pack_stream_0..3和三条合并；将三个模板存储原语换普通aligned32B写，每64像素展开六次；仅此TU删除streamed和SFENCE',
        macroinstructions='新普通写路径相对79 pair48预计减少输入拆位指令，但每8像素输入load由4恢复8；必须审计实际汇编，不能将输入与缓存提示的历史收益独立相乘',
        boundary={'normal_body64_max_read_bytes':193, 'normal_body32_max_read_bytes':97, 'body64_guard_pixels':72, 'body32_guard_pixels':40,
                  'preserved_pair48_body64_max_read_bytes':194, 'preserved_pair48_body32_max_read_bytes':98, 'exact_tail_read_bytes':24, 'prefetch_guard_pixels':406},
        expected_single_extra_bytes_vs23=24, expected_chain_extra_bytes_vs23=24+2**24, expected_chain_model_bytes=28046644,
        resource_validation='没有新增表或Handle字段，预计与79相同；实际model_bytes与页状态由主流程验证',
        history=['68所有原地线程采用T0普通写、MOV+AND输入、旧pack/output_four和连续static；单次PMU四线程有正信号但单线程失败',
                 '71仅workers>1采用T0普通写，却同时采用static,1交错；仍为MOV+AND及旧pack，首轮长批次未达标',
                 '74为连续static的PREFETCHW普通写，本机prfchw=1；T0只是不支持时的回退，仍MOV+AND和旧pack，不能把它当作本次ANDN+T0的直接测量',
                 '75至79的ANDN专用宽路径均为NTA/NT；未找到ANDN32+T0普通写+连续static+当前预排的直接已测组合'],
        hypothesis='仅在多线程原地尝试减少输入拆位/输出合并前端工作并改为缓存内写；保留已验79单线程/分离路径，但新build须重新同场验证，不能拼接旧成绩',
        risks=['79四线程仍明显未达三倍，68旧单次PMU信号不足以预测本组合补足缺口',
               'T0及普通写可能增加源数据与16MiB随机ID表的缓存竞争；此前SQ计数不能证明store是根因',
               'mem32输入恢复更多load，LQ占用可能变差；减少宏指令并非后端吞吐保证',
               '新增TU和调度可能改变寄存器分配，需重新禁止热区spill并核对保留对象',
               '无BMI/无OMP/嵌套路径仅源级保证仍需如实记录覆盖；本机Zen4结论不可当作Skylake实测'])
    perf_policy_path = ROOT / 'experiments/skylake-pair48-long-perf-v1.json'
    perf = load(perf_policy_path)
    keys = ('orders', 'thread_orders', 'inner_repeats', 'control_orders', 'control_gate', 'adoption_gate')
    plan['acceptance_invariants'] = dict(reference_policy=spec(perf_policy_path), **{k:copy.deepcopy(perf[k]) for k in keys},
        confirmation='首次完整4进程控制和全部门槛通过后才允许一次独立4进程确认；首次、确认、合并8对均须通过，失败不重试；新输出目录由主流程冻结')
    new_sources = {name.replace(OLD_NAME+'/', NEW_NAME+'/'): expected for name, expected in parent['source_sha256'].items()}
    for f in files:
        new_sources[f['path']] = f['sha256']
    plan['source_sha256'] = dict(sorted(new_sources.items()))
    assert len(plan['source_sha256']) == 72
    assert all(plan[k] == parent[k] for k in ('fixed_inputs', 'suffix_models', 'contract', 'hardware', 'screen'))
    assert all(digest(ROOT / name) == expected for name, expected in plan['source_sha256'].items())
    save_json(NEW_PLAN, plan)
    receipt = dict(purpose=__doc__, frozen=True, base_commit=BASE_COMMIT, plan=spec(NEW_PLAN), generator=spec(Path(__file__)),
        parent_plan=spec(OLD_PLAN), normal_parent=spec(NORMAL_BASE), candidate_files=files, source_entries=len(plan['source_sha256']),
        preserved_exact_pixel_sources=['andn_inplace/channel_avx2.cpp', 'andn_outplace/channel_avx2.cpp', 'channel_avx2.cpp'],
        source_diff=spec(HERE/'source-diff.patch'), normal_diff=spec(HERE/'normal-vs78.patch'), prior_evidence=basis,
        verification_note='79完整域实际每批262144像素可覆盖四块；旧257像素对齐检查不能覆盖normal，需要主流程新验证胶水另补大块对齐。',
        builds=0, compiler_calls=0, candidate_library_loads=0, pixel_calls=0, performance_calls=0)
    save_json(HERE / 'preparation.json', receipt)
    print(json.dumps(dict(plan=receipt['plan'], files=len(files), source_entries=72, frozen=True, native_calls=0), ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
