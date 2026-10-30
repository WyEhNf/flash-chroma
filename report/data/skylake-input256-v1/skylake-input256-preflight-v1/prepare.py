"""仅生成并冻结修订81源码/构建计划；不编译、不加载候选、不执行像素或性能。"""
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD_NAME='experiments/skylake-pair48-runtime'
NEW_NAME='experiments/skylake-input256-runtime'
OLD,NEW=ROOT/OLD_NAME,ROOT/NEW_NAME
OLD_PLAN=ROOT/'experiments/skylake-pair48-v1.json'
NEW_PLAN=ROOT/'experiments/skylake-input256-v1.json'
WIDE_PARENT=ROOT/'experiments/skylake-andn-split-runtime/andn_inplace/channel_avx2.cpp'
BASE_COMMIT='99cdfe7182e417ddea7a63cb48f2a665fd346af6'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def spec(path):
    path=Path(path)
    if not path.is_absolute():path=ROOT/path
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path)}


def once(data,old,new):
    assert data.count(old)==1,old
    return data.replace(old,new)


def save(path,value):
    with path.open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    assert not NEW.exists() and not NEW_PLAN.exists() and not(HERE/'preparation.json').exists(), '不覆盖已准备候选'
    parent=load(OLD_PLAN)
    assert digest(OLD_PLAN)=='a31c77dc7fc966c3314b5e1eda585fd1d11e840050314a78e9eb689b6c85c180'
    assert digest(WIDE_PARENT)=='dbb416074abf56734a2e894507c572b25e6a10bb30ee9409cbc359bb93fa336d'
    assert all(digest(ROOT/p)==h for p,h in parent['source_sha256'].items())
    basis_paths={
        'revision79_static':'artifacts/skylake-pair48-static-v1/results-v2.json',
        'revision79_independent_static':'artifacts/skylake-pair48-static-v1/independent-audit.json',
        'revision79_full':'artifacts/skylake-pair48-linux-full-v1/results.json',
        'revision79_initial_long':'artifacts/skylake-pair48-long-perf-v1/results.json',
        'revision80_static':'artifacts/skylake-andn-normal-static-v1/results-v2.json',
        'revision80_full':'artifacts/skylake-andn-normal-linux-full-v1/results.json',
        'revision80_initial_long':'artifacts/skylake-andn-normal-long-perf-v1/results.json',
        'revision34_input_source':'experiments/skylake-pack32-runtime/channel_avx2.cpp',
        'revision50_input_source':'experiments/skylake-vectorinput-runtime/channel_avx2.cpp',
        'revision51_input_source':'experiments/skylake-vectorwide-runtime/channel_avx2.cpp',
        'revision58_input_source':'experiments/skylake-splitpack-runtime/channel_avx2.cpp',
        'revision59_input_source':'experiments/skylake-vectorpack-runtime/channel_avx2.cpp',
        'revision34_stage':'docs/stages/2026-10-20-skylake-load-packing.md',
        'revision59_stage':'docs/stages/2026-10-21-skylake-lookup-overlap.md'}
    basis={k:spec(v) for k,v in basis_paths.items()}
    expected={
        'revision79_static':'f081ad5e9fd3772c27a1b8900fdfc99d5524108e1947da39361e66fe94010efd',
        'revision79_independent_static':'d56c26f6bb43869d0073103b18ff3bf591e98df7292386b22652ddb40323f917',
        'revision79_full':'41628bf768a3673a3f83afef75879315ea080465aa9ddd40d53e6688d93c108f',
        'revision79_initial_long':'2d00684c0a0eea66e37227318be3a972ea2e4bae34333c98a42a0eefba1b4db4',
        'revision80_static':'24ff9a6779c94aa61997c790ea0cd9e6fa2a1019945dbf4cd8ec72f1b8ab4e01',
        'revision80_full':'2e858c5f36d7b9ace81e0d514d2c149fb949fbf2acffb7698819c88d915213fc',
        'revision80_initial_long':'bb29645b05b16d6818e304745674b0e265eab0c1e124b3e7fe88b86f2bd954dc'}
    assert all(basis[k]['sha256']==h for k,h in expected.items())
    prior80=load(ROOT/basis_paths['revision80_initial_long'])
    assert prior80['measurement_completed'] and prior80['measurement_control_valid'] and not prior80['accepted_on_this_host']
    perf_path=ROOT/'experiments/skylake-andn-normal-long-perf-v1.json'
    assert digest(perf_path)=='1118b57055c89c94cd27845c171e8c1fd3cd7f1e14fb6e92232dd627fb91a642'
    perf=load(perf_path)

    original={p.relative_to(OLD).as_posix():p.read_bytes() for p in OLD.rglob('*') if p.is_file()}
    assert len(original)==10
    changed=dict(original)
    runtime=original['channel_runtime.cpp']
    nl=b'\r\n' if b'\r\n' in runtime else b'\n'
    runtime=once(runtime,b'uint32_t jshc_cc_revision(void) {return 79;}',b'uint32_t jshc_cc_revision(void) {return 81;}')
    omp=b'  const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,static_cast<size_t>(threads)));'+nl+b'#pragma omp parallel for schedule(static) num_threads(workers)'+nl+b'#endif'
    runtime=once(runtime,omp,omp[:-len(b'#endif')]+b'#else'+nl+b'  const int workers=1;'+nl+b'#endif')
    old_dispatch=b'          if(h.pair48_supported)jshc_channel::avx2_chain_pair48(h.direct_index.data(),h.output_palette.data(),data,vectorized);'
    new_dispatch=nl.join([
        '          // 新输入路径只需AVX2；依据有效workers分派，不要求BMI1。'.encode(),
        b'          if(workers>1)jshc_channel::avx2_chain_input256_mt(h.direct_index.data(),h.output_palette.data(),data,vectorized);',
        b'          else if(h.pair48_supported)jshc_channel::avx2_chain_pair48(h.direct_index.data(),h.output_palette.data(),data,vectorized);'])
    runtime=once(runtime,old_dispatch,new_dispatch)
    runtime=once(runtime,'  // 表示本句柄AVX2原地及分离输出会选择ANDN；无表时原精确回退不使用该指令。'.encode(),
        '  // 仅报告BMI1与直表资格；有效单线程原地及真正分离输出可选pair48，多线程原地走input256。'.encode())
    marker=b'int jshc_cc_apply_to(void* handle,'
    getter=nl.join([
        b'JSHC_CC_API uint32_t jshc_cc_input256_enabled(const void* handle) {',
        b'  if(!handle)return 0;',
        b'  const auto& h=*static_cast<const Handle*>(handle);',
        '  // 只报告AVX2与直表资格；不表示每次调用实际使用input256，不依赖BMI1。'.encode(),
        b'  return (jshc_cc_capabilities()&2) && !h.direct_index.empty()?1u:0u;',
        b'}',b''])
    runtime=once(runtime,marker,getter+marker)
    assert runtime.count(b'__builtin_cpu_supports("bmi")')==1
    assert b'schedule(static,1)' not in runtime
    changed['channel_runtime.cpp']=runtime

    header=original['suffix_cache.hpp'];hnl=b'\r\n' if b'\r\n' in header else b'\n'
    declaration=b'void avx2_chain_pair48(const uint32_t*,const uint32_t*,uint8_t*,size_t) noexcept;'
    header=once(header,declaration,declaration+hnl+b'void avx2_chain_input256_mt(const uint32_t*,const uint32_t*,uint8_t*,size_t) noexcept;')
    header=once(header,'// 本句柄AVX2原地及分离输出是否会选择ANDN；空句柄或未构造线性表返回0。'.encode(),
        '// BMI1与直表资格；有效单线程原地及真正分离输出可选pair48，空句柄或无表返回0。'.encode())
    declaration=b'JSHC_CC_API uint32_t jshc_cc_pair48_enabled(const void*);'
    header=once(header,declaration,declaration+hnl+
        '// 只报告AVX2与直表资格，不表示每次调用实际进入input256；null或无表返回0。'.encode()+hnl+
        b'JSHC_CC_API uint32_t jshc_cc_input256_enabled(const void*);')
    changed['suffix_cache.hpp']=header

    cmake=original['CMakeLists.txt'].replace(b'jshc_skylake_pair48',b'jshc_skylake_input256')
    cnl=b'\r\n' if b'\r\n' in cmake else b'\n'
    sequence=b'  "${CMAKE_CURRENT_SOURCE_DIR}/andn_outplace/channel_avx2.cpp"'+cnl+b'  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"'
    cmake=once(cmake,sequence,b'  "${CMAKE_CURRENT_SOURCE_DIR}/andn_outplace/channel_avx2.cpp"'+cnl+
        b'  "${CMAKE_CURRENT_SOURCE_DIR}/input256_inplace/channel_avx2.cpp"'+cnl+b'  "${JSHC_ROOT}/experiments/skylake-exception-runtime/channel_avx2.cpp"')
    sequence=b'  "${CMAKE_CURRENT_SOURCE_DIR}/channel_avx2.cpp"'+cnl+b'  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")'
    cmake=once(cmake,sequence,b'  "${CMAKE_CURRENT_SOURCE_DIR}/channel_avx2.cpp"'+cnl+
        b'  "${CMAKE_CURRENT_SOURCE_DIR}/input256_inplace/channel_avx2.cpp"'+cnl+b'  PROPERTIES COMPILE_OPTIONS "-mavx2;-mtune=skylake;-ffp-contract=off")')
    cmake=once(cmake,'# 三个像素TU同名以保留构建审计规则；两个ANDN独立入口TU获得BMI1许可。'.encode(),
        '# 四个像素TU同名保留审计规则；只有两个原pair48入口获得BMI1，新input256只需AVX2。'.encode())
    changed['CMakeLists.txt']=cmake

    wide_parent=WIDE_PARENT.read_bytes();wnl=b'\r\n' if b'\r\n' in wide_parent else b'\n'
    begin=wide_parent.index('// 仅宽循环调用'.encode())
    end=wide_parent.index(b'inline __attribute__((always_inline)) void output(')
    wide='''// 仅宽循环调用；32字节载荷由原p+72/p+40窗口保护，精确24字节尾部不调用此函数。
inline __attribute__((always_inline)) __m256i read_wide(const uint32_t* table,const uint32_t* palette,const uint8_t* p) {
  const uint8_t* bytes=reinterpret_cast<const uint8_t*>(table);
  const __m256i raw=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(p));
  const __m256i lanes=_mm256_permutevar8x32_epi32(raw,_mm256_setr_epi32(0,1,2,3,3,4,5,6));
  const __m256i code=_mm256_shuffle_epi8(lanes,
      _mm256_setr_epi8(0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1,0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1));
  // 低半对应RGB字节0..11；四个精确u8 ID到齐后才读取调色板。
  const __m128i low=_mm256_castsi256_si128(code);
  const uint32_t i0=bytes[uint32_t(_mm_extract_epi32(low,0))],i1=bytes[uint32_t(_mm_extract_epi32(low,1))];
  const uint32_t i2=bytes[uint32_t(_mm_extract_epi32(low,2))],i3=bytes[uint32_t(_mm_extract_epi32(low,3))];
  asm volatile("" : : "r"(i0),"r"(i1),"r"(i2),"r"(i3) : "memory");
  const __m128i lo=_mm_setr_epi32(int32_t(palette[i0]),int32_t(palette[i1]),
      int32_t(palette[i2]),int32_t(palette[i3]));
  // 高半由原字节12..27组成，只消费12..23；后四ID保持同样屏障。
  const __m128i high=_mm256_extracti128_si256(code,1);
  const uint32_t i4=bytes[uint32_t(_mm_extract_epi32(high,0))],i5=bytes[uint32_t(_mm_extract_epi32(high,1))];
  const uint32_t i6=bytes[uint32_t(_mm_extract_epi32(high,2))],i7=bytes[uint32_t(_mm_extract_epi32(high,3))];
  asm volatile("" : : "r"(i4),"r"(i5),"r"(i6),"r"(i7) : "memory");
  const __m128i hi=_mm_setr_epi32(int32_t(palette[i4]),int32_t(palette[i5]),
      int32_t(palette[i6]),int32_t(palette[i7]));
  return _mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
}
'''
    wide=wide.replace('\n',wnl.decode()).encode()
    new_tu=wide_parent[:begin]+wide+wide_parent[end:]
    new_tu=once(new_tu,b'avx2_chain_andn_split(',b'avx2_chain_input256_mt(')
    assert b'asm("andn' not in new_tu and new_tu.count(b'asm volatile')==2
    assert new_tu.count(b'_mm256_loadu_si256')==1 and new_tu.count(b'_MM_HINT_NTA')==5
    assert new_tu.count(b'_mm256_stream_si256')==3 and new_tu.count(b'_mm_sfence')==1
    assert new_tu[:begin]==wide_parent[:begin]
    assert new_tu[begin+len(wide):]==wide_parent[end:].replace(b'avx2_chain_andn_split(',b'avx2_chain_input256_mt(')
    changed['input256_inplace/channel_avx2.cpp']=new_tu
    for rel in ('channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp'):
        assert changed[rel]==original[rel]

    files,patch=[],[]
    for rel,content in sorted(changed.items()):
        path=NEW/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
        before=original.get(rel,b'')
        files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'same_bytes_as79':rel in original and content==before})
        if content!=before:
            patch.extend(difflib.unified_diff(before.decode().splitlines(keepends=True),content.decode().splitlines(keepends=True),
                fromfile=OLD_NAME+'/'+rel if rel in original else '/dev/null',tofile=NEW_NAME+'/'+rel))
    (HERE/'source-diff.patch').write_bytes(''.join(patch).encode())
    (HERE/'input256-vs78.patch').write_bytes(''.join(difflib.unified_diff(wide_parent.decode().splitlines(keepends=True),new_tu.decode().splitlines(keepends=True),
        fromfile=WIDE_PARENT.relative_to(ROOT).as_posix(),tofile=NEW_NAME+'/input256_inplace/channel_avx2.cpp')).encode())

    plan=copy.deepcopy(parent)
    plan.update(purpose='修订81提案：仅多线程原地用一次32B AVX2输入整形，保持精确四ID先行与预排NT输出；当前仅源码和计划冻结',
        base_commit=BASE_COMMIT,candidate='79单线程/分离与线性TU原字节保留；新AVX2 input256入口只替换78原地read_wide，按有效workers>1选择，不要求BMI',
        cmake_project=NEW_NAME,cmake_targets=['jshc_skylake_reference','jshc_skylake_input256'],revisions={'reference':23,'candidate':81})
    plan['unchanged']=[
        '四级模型、Q16、逐级RGB8整数舍入、230项精确调色板及唯一16MiB format9线性ID表；构造不读照片或gold',
        '79主线性TU和andn_inplace/andn_outplace两个pair48 TU含原导出名逐字节保留；没有新增Handle字段、表或拟合',
        '新input256的read_wide之外逐字节保持78原地TU，只有入口名称改变；精确24B尾、NTA、NT、SFENCE、pack_stream和64/32先读后写不变',
        '65536像素连续schedule(static)；嵌套/非OpenMP有效workers=1；同址apply_to仍委托原地，真正分离始终保留79 BMI分派',
        '构造一次BMI检测及旧pair48资格getter保留；新多线程路径只需AVX2，不新增强制环境开关或跨调用状态',
        'fixed_inputs/suffix_models/contract/hardware/screen与79相同；完整色域及80新增64个多块实际对齐夹具必须继续执行',
        '纯映射与真实输出1/4线程各三倍，ABBA/A/A/16或64内轮/唯一独立确认门槛不变；80及其他旧失败不重测']
    plan['required_static_checks']=[
        '所有冻结源与构建身份一致；79两个pair48和主线性对象.text逐字节相同，旧四个宽区段完整保留，不以源码身份代替对象核对',
        '新input256必须完整识别64/32两个可达宽区段；每8像素只产生一个32B输入内存操作，64/32区段分别8/4个，允许合法VPERMD内存源折叠但不得拆回多个源load',
        '逐字节标签核对VPERMD[0,1,2,3,3,4,5,6]与PSHUFB，八个GPR索引精确为R|G<<8|B<<16且高位为0，64/32项ID与palette各完整一次',
        '每8像素低/高两组四ID屏障实际成立，全部64/32输入、ID及palette读取均早于该区段首输出；不能仅凭空asm源码认定',
        '新宽区段无真实rsp/frame spill、无循环内向量常量重复加载，尤其输入排列/PSHUFB常量必须外提；无外部call/gather/BMI1/BMI2/EVEX/AVX512/FMA',
        '输入load、VPERMD、VPSHUFB、提取和输出各类真实指令分别记录；宏指令或load减少不作为微操作/周期收益证明',
        '新64/32最大读200/104B分别不超过72/40像素的216/120B；精确8像素尾只读24B，标量前缀/线程块边界/406预取保护不变',
        '新入口保留64B对齐、预排及六NT32B写；普通尾前SFENCE，NTA提示位置相同；静态核对输出字节组，禁止预排值交给旧普通合并',
        '新input256仅有AVX2许可；仅两个原pair48 TU带-mbmi，泛型dispatcher与其余回退无新增ISA泄漏，实际compile_commands逐项核对',
        '有效workers>1且有直表的AVX2原地选input256，无需BMI；workers1/嵌套/非OMP与真正分离保持79 pair48或linear；只读资格getter不冒充实际执行计数',
        '任何静态失败即停止完整色域与性能，不修改门槛追求通过；仅静态通过才由主流程做新身份完整正确性及冻结长批次，不重评旧失败']
    plan['preparation']={'state':'源码和构建计划已冻结；尚未编译、加载、执行像素或性能','parent_plan':spec(OLD_PLAN),
        'new_tu_source_parent':spec(WIDE_PARENT),'generator':spec(__file__),'no_performance_claim':True,
        'conditional_execution':'唯一新候选81只允许先做静态筛查；失败停止；其后正确性及性能由主流程决定并冻结新身份'}
    plan['prior_evidence']=basis
    plan.pop('pair48',None)
    plan['input256']={
        'linear_format':9,'entries':2**22,'physical_bytes':2**24,
        'selection':{'inplace_effective_workers_gt1':'input256纯AVX2，不要求BMI','inplace_effective_workers_1':'79 pair48具BMI则启用，否则原linear',
            'nested_or_no_openmp':'有效workers=1，保留79分派','true_outplace':'原79 pair48/BMI回退','same_address_apply_to':'委托原地有效workers规则'},
        'readonly_apis':{'preserved':'jshc_cc_pair48_enabled：BMI1与直表资格，null/无表0，不表示每次调用走pair48',
            'new':'显式JSHC_CC_API uint32_t jshc_cc_input256_enabled(const void*)：AVX2与直表资格，null/无表0，不依赖BMI，也不表示每次调用走input256'},
        'input':{'load_bytes':32,'loads_per8':1,'permd':[0,1,2,3,3,4,5,6],
            'pshufb_each_half':[0,1,2,-1,3,4,5,-1,6,7,8,-1,9,10,11,-1],
            'mapping':'低半源0..15、高半源12..27；各只用前12字节，每组三字节后补零，八个RGB24码按原R低布局提到GPR',
            'barriers_per8':2,'requested_input_bytes_per_pixel':4,'prior79_requested_input_bytes_per_pixel':4,
            'input_id_palette_loads_per8':17,'prior79_input_id_palette_loads_per8':20,
            'input_loads_per64':8,'aligned64_body_line_crossing_loads':3,
            'crossing_offsets_mod64':[48,56,40],
            'macroinstruction_estimate':'逻辑约1load+1VPERMD+1VPSHUFB+1高半提取+8项提取=12条/8像素；内存折叠、VMOVD替代等以对象为准，不当作微操作或吞吐成绩'},
        'boundary':{'body64_max_read_bytes':200,'body32_max_read_bytes':104,'body64_guard_pixels':72,'body32_guard_pixels':40,
            'body64_available_bytes':216,'body32_available_bytes':120,'exact_tail_read_bytes':24,
            'proof':'64末包起168，168+32=200；32末包起72，72+32=104；原宽窗口有效，新增多读字节从不参与索引'},
        'history':['34已用等价单YMM32→VPERMD→PSHUFB输入；其忽略dword排列为[0,1,2,0,3,4,5,0]且B低旧表，随后两级gather及32像素普通输出，无四ID标量方案',
            '50为精确load16+load8、PALIGNR、合并YMM后PSHUFB；51为[0,16)/[12,28)两load16，均无四ID屏障及预排输出',
            '58为精确16+8输入、两个独立XMM展开，加57预排；59为50输入+57预排，均无四ID屏障；完整新组合不是这四版的直接重复',
            '旧50/51/58/59均未通过各自筛查；34整体也失败，不能把新输入方法写成首次发明，不能重测旧失败或拼接旧成绩'],
        'hypothesis':'仅减少每8像素输入加载操作4→1，ID/palette请求仍各8次；是否缓解本机LQ等待或改善4线程纯apply未知，不承诺三倍',
        'risks':['八个ID地址共享load→VPERMD→VPSHUFB前缀，高半另有提取依赖；可能推迟随机ID请求',
            'VPERMD、VPSHUFB、XMM提取与现有输出争用重排资源；新常量和输入/输出同时活跃可能spill或重复加载',
            '每64B对齐主体的8次32B读取有3次跨缓存行，输入请求仍4B/像素，17比20只是加载操作计数，不能当作LQ占用同比减少',
            '78诊断高LQ等待不证明主要来自输入而非随机ID；本机Zen4/WSL结论不可外推Skylake',
            '新build会重新同场比较23，不能把79单线程旧成绩和新4线程拼接成功'],
        'expected_single_extra_bytes_vs23':24,'expected_chain_extra_bytes_vs23':24+2**24,
        'expected_single_model_bytes':272859,'expected_chain_model_bytes':28046644,
        'resource_validation':'不新增Handle字段或派生表；真实资源与THP仍须独立验证'}
    plan['correctness_requirements']={'preserve_full_matrix':True,'full_input_chunk_pixels':262144,'complete_rgb8_colors':2**24,
        'normal_matrix_reference':spec('scripts/verify_skylake_andn_normal_linux.py'),
        'additional_multiblock_alignment':{'pixels':65793,'effective_workers':2,'requested_threads':4,'kernel':1,'model':'四级候选',
            'actual_address_low6':list(range(64)),'expected':'独立cube原RGB坐标查期望，双侧全哨兵，继承80的实际对齐基址算法'},
        'negative_getter_cases':'pair48/input256两个getter分别检查null与单级无表为0；四级input256记录AVX2资格，与pair48 BMI资格分开解释',
        'limitations':'源级分派保证不代替无BMI/嵌套/非OMP真实运行；不得声称未执行环境已验'}
    keys=('orders','thread_orders','inner_repeats','control_orders','control_gate','adoption_gate','affinity_cpus','quiet_protocol','mode_order')
    confirmation=copy.deepcopy(perf['confirmation']);confirmation['output']='artifacts/skylake-input256-long-confirm-v1'
    plan['acceptance_invariants']={'reference_policy':spec(perf_path),**{k:copy.deepcopy(perf[k]) for k in keys},'confirmation':confirmation,
        'rules':'首次4进程、同库A/A、16/64内轮；首次通过才一次独立4进程确认，首次/确认/合并8对均通过；失败不重试、不择优、不改变纯映射或真实输出目标'}
    plan['official_references'] += [
        {'title':'uops.info原始Skylake测量：VPERMD寄存器形式；不外推本机性能','url':'https://uops.info/html-instr/VPERMD_YMM_YMM_YMM.html'},
        {'title':'uops.info原始Skylake测量：VEXTRACTI128；不把宏指令数当微操作数','url':'https://uops.info/html-instr/VEXTRACTI128_XMM_YMM_I8.html'}]
    sources={p.replace(OLD_NAME+'/',NEW_NAME+'/'):h for p,h in parent['source_sha256'].items()}
    sources.update({f['path']:f['sha256'] for f in files});plan['source_sha256']=dict(sorted(sources.items()))
    assert len(files)==11 and len(sources)==72
    assert all(plan[k]==parent[k] for k in ('fixed_inputs','suffix_models','contract','hardware','screen'))
    assert all(digest(ROOT/p)==h for p,h in sources.items())
    save(NEW_PLAN,plan)
    receipt={'purpose':__doc__,'frozen':True,'base_commit':BASE_COMMIT,'plan':spec(NEW_PLAN),'parent_plan':spec(OLD_PLAN),
        'generator':spec(__file__),'input_parent':spec(WIDE_PARENT),'candidate_files':files,'source_entries':len(sources),
        'preserved_exact_pixel_sources':['andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp','channel_avx2.cpp'],
        'new_tu_outside_read_wide_equal78_after_entry_rename':True,'source_diff':spec(HERE/'source-diff.patch'),
        'input_diff':spec(HERE/'input256-vs78.patch'),'prior_evidence':basis,
        'verification_note':'新多线程入口必须保留262144像素完整域批次和65793像素64实际偏移夹具；资格getter不记录实际执行路径',
        'builds':0,'compiler_calls':0,'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0}
    save(HERE/'preparation.json',receipt)
    print(json.dumps({'plan':receipt['plan'],'files':len(files),'source_entries':len(sources),'frozen':True,'native_calls':0},ensure_ascii=False))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
