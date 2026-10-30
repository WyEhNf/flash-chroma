"""只生成79独立源码和构建计划；不编译、不加载动态库、不执行像素或性能。"""
import copy
import difflib
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD_NAME = 'experiments/skylake-andn-split-runtime'
NEW_NAME = 'experiments/skylake-pair48-runtime'
OLD = ROOT / OLD_NAME
NEW = ROOT / NEW_NAME
OLD_PLAN = ROOT / 'experiments/skylake-andn-split-v1.json'
NEW_PLAN = ROOT / 'experiments/skylake-pair48-v1.json'
BASE_COMMIT = '91b7c7359f938876d22fc7fc12fa7b2b0e02ebe0'
START = '// 仅宽循环调用；最后一个32bit输入读取多出的1字节仍在当前线程块内。'.encode()
END = b'inline __attribute__((always_inline)) void output('
NEW_START = '// 仅宽循环调用；每对读取8字节并保留低48位，多出的2字节仍在当前线程块内。'.encode()

# 只替换宽输入函数；两对形成既有四ID屏障，调色板合成保持原顺序。
WIDE = '''// 仅宽循环调用；每对读取8字节并保留低48位，多出的2字节仍在当前线程块内。
inline __attribute__((always_inline)) __m256i read_wide(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  const uint8_t* bytes=reinterpret_cast<const uint8_t*>(table);
  // GNU低对齐可别名类型精确描述8字节输入；不得用于精确24字节尾部。
  typedef uint64_t unaligned_alias_u64 __attribute__((aligned(1),may_alias));
  const uint64_t high_mask=0xffff000000000000ULL;
  const auto input=[p,high_mask](size_t offset) {
    uint64_t packed;
    // AT&T源顺序：内存、取反掩码、目标；64位结果为~high_mask & input64。
    // %q选择完整64位寄存器，精确memory输入与cc描述依赖，不增加内存屏障。
    asm("andn %1, %q2, %q0" : "=r"(packed)
        : "m"(*reinterpret_cast<const unaligned_alias_u64*>(p+offset)),"r"(high_mask) : "cc");
    return packed;
  };
  const uint64_t q0=input(0);
  const uint32_t i0=bytes[q0&0xffffffULL],i1=bytes[q0>>24];
  const uint64_t q1=input(6);
  const uint32_t i2=bytes[q1&0xffffffULL],i3=bytes[q1>>24];
  asm volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
  const __m128i lo=_mm_setr_epi32(int32_t(palette[i0]),int32_t(palette[i1]),
      int32_t(palette[i2]),int32_t(palette[i3]));
  const uint64_t q2=input(12);
  const uint32_t i4=bytes[q2&0xffffffULL],i5=bytes[q2>>24];
  const uint64_t q3=input(18);
  const uint32_t i6=bytes[q3&0xffffffULL],i7=bytes[q3>>24];
  asm volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
  const __m128i hi=_mm_setr_epi32(int32_t(palette[i4]),int32_t(palette[i5]),
      int32_t(palette[i6]),int32_t(palette[i7]));
  return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spec(path):
    return {'path': Path(path).relative_to(ROOT).as_posix(), 'sha256': digest(path)}


def split_wide(data, marker):
    start = data.index(marker)
    end = data.index(END, start)
    return data[:start], data[start:end], data[end:]


def main():
    if NEW.exists() or NEW_PLAN.exists() or (HERE/'preparation.json').exists():
        raise FileExistsError('不得覆盖候选、计划或准备回执')
    parent = json.loads(OLD_PLAN.read_text(encoding='utf-8'))
    assert digest(OLD_PLAN) == 'c62d97a402705692977250f0e626c9587a7190e97cf9a9b44f4d6a22840532d8'
    for name, expected in parent['source_sha256'].items():
        assert digest(ROOT/name) == expected, name
    diagnostic = ROOT/'artifacts/skylake-dispatch-diagnostic-v1/results.json'
    independent = ROOT/'artifacts/skylake-dispatch-diagnostic-independent-v1/results.json'
    assert digest(diagnostic) == 'e68ec3f0ffa05cdfb9d4e3930d65058d7b0ae4cfc7234e100351938b57acdec9'
    assert digest(independent) == '788f7de92f13d8e10cf1f0051fdd5358a17c9a5cc81c591e994e396cf4e08c20'
    assert json.loads(diagnostic.read_text(encoding='utf-8'))['pass']
    assert json.loads(independent.read_text(encoding='utf-8'))['pass']
    files, diff, comparisons = [], [], {}
    for source in sorted(x for x in OLD.rglob('*') if x.is_file()):
        rel = source.relative_to(OLD)
        original = source.read_bytes()
        renamed = original.replace(b'andn_split', b'pair48')
        changed = renamed
        if rel.as_posix() in ('andn_inplace/channel_avx2.cpp', 'andn_outplace/channel_avx2.cpp'):
            before, old_wide, after = split_wide(renamed, START)
            newline = b'\r\n' if b'\r\n' in original else b'\n'
            changed = before + WIDE.encode().replace(b'\n', newline) + after
            new_before, _, new_after = split_wide(changed, NEW_START)
            assert before == new_before and after == new_after
            comparisons[rel.as_posix()] = {
                'outside_read_wide_equal_after_identity_rename': True,
                'prefix_sha256': hashlib.sha256(before).hexdigest(),
                'suffix_sha256': hashlib.sha256(after).hexdigest(),
                'parent_wide_sha256': hashlib.sha256(old_wide).hexdigest(),
                'wide_input_offsets': [0, 6, 12, 18], 'wide_input_bytes': 8,
                'preserved_exact_tail_bytes': 24, 'barriers_per8': 2}
        elif rel.as_posix() == 'channel_runtime.cpp':
            old_revision = b'uint32_t jshc_cc_revision(void) {return 78;}'
            assert renamed.count(old_revision) == 1
            changed = renamed.replace(old_revision, b'uint32_t jshc_cc_revision(void) {return 79;}')
        destination = NEW/rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(changed)
        files.append({'path': destination.relative_to(ROOT).as_posix(), 'sha256': digest(destination),
                      'parent_sha256': digest(source), 'same_bytes_as78': changed == original})
        if changed != original:
            diff.extend(difflib.unified_diff(original.decode().splitlines(keepends=True), changed.decode().splitlines(keepends=True),
                        fromfile=source.relative_to(ROOT).as_posix(), tofile=destination.relative_to(ROOT).as_posix()))
    assert len(files) == 10
    assert digest(NEW/'channel_avx2.cpp') == 'e0cb7f0539fdb5d7f35645978b1b2504dbf7e60c57e21acf8ae361cf1c343a30'
    plan = copy.deepcopy(parent)
    plan['purpose'] = '修订79提案：每两个RGB24以一次64位内存ANDN输入读取，保留精确两级查表与四ID先行；源码计划冻结时未编译、未执行原生'
    plan['base_commit'] = BASE_COMMIT
    plan['candidate'] = '从78只替换两独立BMI1像素TU的read_wide：8像素输入加载8次减为4次，以低48位拆成两项24位索引；可增加机器指令，目标是减少输入load个数，不改变随机ID/palette载荷、表或输出'
    plan['unchanged'] = [
        'a399四级模型、Q16、逐级RGB8舍入及精确230色调色板；构造不读照片、完整域gold或历史输出',
        '唯一16MiB线性ID表与format9；线性分配失败精确回退，构造一次BMI1检测，不支持BMI1走原线性',
        '主线性TU与78/72逐字节相同，泛型runtime只改导出/feature身份和revision，不改变别名或OpenMP语义',
        '两BMI1 TU的read_wide以外逐字节保持78（只导出身份改名）；四ID屏障、调色板及输出合成顺序保持',
        '65536像素块、schedule(static)、64B目的对齐、NTA/NT/SFENCE、64/32主体先读取全部像素再写保持',
        '原地p+72/40及分离remaining>=72/40条件不变，精确24字节8像素尾部、标量、406预取边界不变',
        '不新增强制环境开关、输入内容特判、近似输出、查表级数或跨调用状态']
    plan['cmake_project'] = NEW_NAME
    plan['cmake_targets'] = ['jshc_skylake_reference', 'jshc_skylake_pair48']
    plan['revisions'] = {'reference': 23, 'candidate': 79}
    plan['source_sha256'] = {name: expected for name, expected in parent['source_sha256'].items() if not name.startswith(OLD_NAME+'/')}
    plan['source_sha256'].update({row['path']: row['sha256'] for row in files})
    assert len(plan['source_sha256']) == 71
    plan['required_static_checks'] = [
        '原线性TU保持72/78原字节；两个BMI1 TU只允许read_wide及pair48入口身份变化，run/精确read/pack/output/scalar_one保持',
        '明确覆盖原地64/32和分离64/32四个实际可达宽区段；32尾若为最多一次直线区段仍完整检查入口条件及全部读写，不以缺失区段判通过',
        '64/32区段分别32/16条mem64 ANDN、VEX.W1、完整64位掩码和目的寄存器；每对低24位掩码及高24位移位语义逐条追踪，base+disp输入读取',
        '每8像素输入地址偏移0/6/12/18，每项8字节；四区段ID与palette加载仍分别64/32项，输入load数量减半，合计3降至2.5每像素；不能沿用75—78的机器指令减少门槛',
        '掩码0xffff000000000000在宽区段外初始化并在每次消费时有效；允许最后消费后的死寄存器复用，后续消费前必须重新初始化',
        '四ID先行及64/32全部像素先读后写成立，无真实栈spill、外部call、gather、BMI2、EVEX、AVX512；区分rbp普通基址和真实frame访问',
        '只andn_inplace/andn_outplace两个独立TU允许-mbmi，新增BMI1指令限ANDN；其他TU不泄漏BMI1，三个像素TU-mavx2/-mtune=skylake/-ffp-contract=off；源SHA/对象字节/compile_commands一致',
        '宽读取最大194/98字节小于原216/120字节合法窗口，8像素尾精确24B不变；静态失败停止不跑像素，随后完整RGB8/finite/guard/align/API通过才允许冻结长批次']
    plan['official_references'][0]['title'] = 'Intel SDM：ANDN语义、64位操作数形式及BMI1能力'
    plan['preparation'] = {'state': '仅源码与构建计划已冻结，未编译、未执行原生、未测性能',
        'conditional_execution': '由主流程安排79构建、静态、完整正确性及后续冻结性能；不重测78或旧失败',
        'parent_plan': spec(OLD_PLAN), 'generator': spec(Path(__file__)), 'no_performance_claim': True}
    plan.pop('primary_measurement_references', None)
    plan.pop('prior_static_failure', None)
    plan.pop('prior_static_failures', None)
    plan.pop('andn_split')
    plan['diagnostic_basis'] = {'result': spec(diagnostic), 'independent_audit': spec(independent),
        'policy': spec(ROOT/'experiments/skylake-dispatch-diagnostic-v2.json'),
        'finding': '78本机照片1/4线程LQ受阻约71.11%/72.94%，FE空槽约0.842%/2.425%；两个组分开采样，不能拼接为同时因果分解',
        'limit': '尚未证明输入load而非随机ID请求占据主要LQ时间；本机WSL Zen4诊断不是Skylake证据，不保证新增算术免费或达到目标',
        'unavailable_measurement': '64位内存ANDN的uops页面未成功获取，不引用其延迟、吞吐或端口作为已核实性能事实'}
    plan['pair48'] = {
        'linear_format': 9, 'entries': 2**22, 'physical_bytes': 2**24,
        'selection': 'AVX2且有直接表时按构造一次__builtin_cpu_supports("bmi")选择pair48；所有线程数原地/分离均适用，无BMI1走原线性',
        'readonly_api': '显式JSHC_CC_API uint32_t jshc_cc_pair48_enabled(const void*)；null或无直接表返回0，否则报告该句柄AVX2调用的BMI1可选路径',
        'instruction': 'GNU AT&T andn memory,%q2,%q0；uint64_t mask=0xffff000000000000ULL，完整uint64_t输出约束=r，结果为(~mask)&input64',
        'memory_contract': 'GNU aligned(1),may_alias uint64 typedef精确m输入；cc clobber，不额外加入memory clobber或volatile；读宽只在read_wide从4变8字节',
        'decode': '每对q低48位保留RGBRGB；低索引q&0xffffffULL，高索引q>>24。每对两个u8 ID、每两对形成既有四ID memory屏障，随后原palette合成',
        'input_offsets_per8': [0, 6, 12, 18], 'input_loads_per8': 4,
        'input_requested_bytes_per_pixel_before': 4, 'input_requested_bytes_per_pixel_after': 4,
        'input_load_instructions_per_pixel_before': 1, 'input_load_instructions_per_pixel_after': 0.5,
        'id_load_instructions_per_pixel': 1, 'palette_load_instructions_per_pixel': 1,
        'total_load_instructions_per_pixel_before': 3, 'total_load_instructions_per_pixel_after': 2.5,
        'macroinstruction_estimate': '每对ANDN64+MOV+AND24+SHR24约4条，代替78两条ANDN32，约增加1条机器指令每像素；实际对象为准，不设少于78的门槛',
        'boundary': {'body64_max_read_bytes': 194, 'body64_guard_pixels': 72, 'body64_available_bytes': 216,
                     'body32_max_read_bytes': 98, 'body32_guard_pixels': 40, 'body32_available_bytes': 120,
                     'exact_tail_read_bytes': 24,
                     'proof': '每8像素包最后输入从偏移18读取8字节；64主体末包168+18+8=194，32尾末包72+18+8=98；多出的两字节被mask丢弃且仍在当前线程块内'},
        'preserved_run': '原地p计数、分离游标/remaining计数与78逐字节一致；同样的前缀、循环迭代集合、406预取边界和SFENCE位置',
        'linear_source_sha256': digest(NEW/'channel_avx2.cpp'),
        'source_differences': comparisons,
        'expected_single_extra_bytes_vs23': 24, 'expected_chain_extra_bytes_vs23': 24+2**24,
        'expected_chain_model_bytes': 28046644, 'resource_validation': '没有新增句柄成员或表；真实资源与大页状态仍须后续验证',
        'risks': ['两个索引增加拆分依赖，可能推迟ID请求；输入load通常命中L1，削减它们未必显著减小LQ占用',
                  '64位常驻mask、pair值及四ID活跃期可能增加寄存器压力、spill或循环内常量重载',
                  '机器指令预期增加，低FE空槽不是新指令零成本证明；随机ID/palette加载与输入请求字节不减少',
                  'inline asm不透明、64位形式与地址调度可能改变代码生成，须重新完整静态审计',
                  '新增8字节读取可能跨缓存行，但只在已有宽窗口内；完整guard/align/别名验证仍不可省略',
                  '本机Zen4结果不能外推Skylake，静态少load不是实际吞吐成绩']}
    for key in ('fixed_inputs', 'suffix_models', 'contract', 'hardware', 'screen'):
        assert plan[key] == parent[key], key
    for name, expected in plan['source_sha256'].items():
        assert digest(ROOT/name) == expected, name
    NEW_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (HERE/'source-diff.patch').write_bytes(''.join(diff).encode())
    receipt = {'purpose': __doc__, 'frozen': True, 'base_commit': BASE_COMMIT,
               'plan': spec(NEW_PLAN), 'generator': spec(Path(__file__)), 'parent_plan': spec(OLD_PLAN),
               'new_builds': 0, 'new_candidate_calls': 0, 'new_performance_calls': 0,
               'source_entries': len(plan['source_sha256']), 'candidate_files': files,
               'comparisons': comparisons, 'linear_fallback_unchanged': True,
               'runtime_only_identity_and_revision_changed': True, 'source_diff': spec(HERE/'source-diff.patch')}
    (HERE/'preparation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'plan_sha256': digest(NEW_PLAN), 'candidate_files': len(files), 'source_entries': len(plan['source_sha256']),
                      'builds': 0, 'candidate_calls': 0}, ensure_ascii=True))


if __name__ == '__main__':
    main()
