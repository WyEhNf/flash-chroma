"""仅准备并冻结修订82源码和构建计划；不编译、加载候选或执行像素/性能。"""
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD_NAME='experiments/skylake-input256-runtime'
NEW_NAME='experiments/skylake-input256-deferred-runtime'
OLD,NEW=ROOT/OLD_NAME,ROOT/NEW_NAME
OLD_PLAN=ROOT/'experiments/skylake-input256-v1.json'
NEW_PLAN=ROOT/'experiments/skylake-input256-deferred-v1.json'
OLD_TU='input256_inplace/channel_avx2.cpp'
NEW_TU='deferred_inplace/channel_avx2.cpp'
BASE_COMMIT='e2752a80d981ca6901ded376364176f1ee1e40b5'


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
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    assert not NEW.exists() and not NEW_PLAN.exists() and not(HERE/'preparation.json').exists(), '不覆盖任何已冻结候选或回执'
    assert digest(OLD_PLAN)=='84150d8fcd166e94efb6ffe570cdf6fd9d1702c71f82d3477077243a2e188778'
    parent=load(OLD_PLAN)
    assert all(digest(ROOT/p)==h for p,h in parent['source_sha256'].items())
    basis={
        'revision81_build':spec('artifacts/skylake-input256-linux-build-v1/build.json'),
        'revision81_static':spec('artifacts/skylake-input256-static-v1/results-v2.json'),
        'revision81_independent_static':spec('artifacts/skylake-input256-static-v1/independent_results.json')}
    expected={
        'revision81_build':'ef6d8f23189c507142c746e2005adce18dbf9601ac10fc1539bfd491d9e355d8',
        'revision81_static':'5b3d7c9a3b3688cbedd66e79baca69d29f21895834a0b3959b172ea06ab4c9b2',
        'revision81_independent_static':'977cb954ff4133eaf8285d61182c9491203aa4c27b30a39995cefae061f36d08'}
    assert all(basis[k]['sha256']==h for k,h in expected.items())
    for name in ('revision81_static','revision81_independent_static'):
        previous=load(ROOT/basis[name]['path'])
        assert not previous['accepted'] and previous['pixel_calls']==0 and previous['performance_calls']==0

    original={p.relative_to(OLD).as_posix():p.read_bytes() for p in OLD.rglob('*') if p.is_file()}
    assert len(original)==11
    changed=dict(original)
    for rel in ('channel_runtime.cpp','suffix_cache.hpp'):
        changed[rel]=original[rel].replace(b'input256',b'input256_deferred')
    changed['channel_runtime.cpp']=once(changed['channel_runtime.cpp'],
        b'uint32_t jshc_cc_revision(void) {return 81;}',b'uint32_t jshc_cc_revision(void) {return 82;}')
    cmake=original['CMakeLists.txt'].replace(b'jshc_skylake_input256',b'jshc_skylake_input256_deferred')
    cmake=cmake.replace(b'input256_inplace/channel_avx2.cpp',b'deferred_inplace/channel_avx2.cpp')
    cmake=cmake.replace('新input256只需AVX2'.encode(),'新input256_deferred只需AVX2'.encode())
    assert cmake.count(b'deferred_inplace/channel_avx2.cpp')==2
    changed['CMakeLists.txt']=cmake

    old_tu=original[OLD_TU]
    nl=b'\r\n' if b'\r\n' in old_tu else b'\n'
    before='''    // 全部64像素先读后写，主体输出恰好192字节即三条完整缓存行。
    const __m256i r0=pack_stream_0(read_wide(table,palette,source+3*p)),r1=pack_stream_1(read_wide(table,palette,source+3*p+24));
    const __m256i r2=pack_stream_2(read_wide(table,palette,source+3*p+48)),r3=pack_stream_3(read_wide(table,palette,source+3*p+72));
    const __m256i r4=pack_stream_0(read_wide(table,palette,source+3*p+96)),r5=pack_stream_1(read_wide(table,palette,source+3*p+120));
    const __m256i r6=pack_stream_2(read_wide(table,palette,source+3*p+144)),r7=pack_stream_3(read_wide(table,palette,source+3*p+168));
    output_four_stream(destination+3*p,r0,r1,r2,r3);output_four_stream(destination+3*p+96,r4,r5,r6,r7);streamed=true;
'''.replace('\n',nl.decode()).encode()
    after='''    // 前32像素全部读完后只写首64B整行；其余32B留在pending，不提前写中间行。
    const __m256i r0=pack_stream_0(read_wide(table,palette,source+3*p)),r1=pack_stream_1(read_wide(table,palette,source+3*p+24));
    const __m256i r2=pack_stream_2(read_wide(table,palette,source+3*p+48)),r3=pack_stream_3(read_wide(table,palette,source+3*p+72));
    const __m256i s0=_mm256_blend_epi32(r0,r1,0xc0);
    const __m256i s1=_mm256_permute2x128_si256(r1,r2,0x30);
    const __m256i pending=_mm256_blend_epi32(r3,r2,0x03);
    // 三个最终输出值先就绪；四ID屏障仍只约束各组查表，不代替此输出生命期边界。
    asm volatile("" : : "x"(s0),"x"(s1),"x"(pending) : "memory");
    _mm256_stream_si256(reinterpret_cast<__m256i*>(destination+3*p),s0);
    _mm256_stream_si256(reinterpret_cast<__m256i*>(destination+3*p+32),s1);
    // 第二组源从96B开始，不读取已写首行；全部读取后补写中间行，再完成末行。
    const __m256i r4=pack_stream_0(read_wide(table,palette,source+3*p+96)),r5=pack_stream_1(read_wide(table,palette,source+3*p+120));
    const __m256i r6=pack_stream_2(read_wide(table,palette,source+3*p+144)),r7=pack_stream_3(read_wide(table,palette,source+3*p+168));
    _mm256_stream_si256(reinterpret_cast<__m256i*>(destination+3*p+64),pending);
    output_four_stream(destination+3*p+96,r4,r5,r6,r7);streamed=true;
'''.replace('\n',nl.decode()).encode()
    new_tu=once(old_tu,before,after)
    new_tu=once(new_tu,b'avx2_chain_input256_mt(',b'avx2_chain_input256_deferred_mt(')
    assert new_tu.replace(after,before).replace(b'avx2_chain_input256_deferred_mt(',b'avx2_chain_input256_mt(')==old_tu
    assert new_tu.count(b'_mm256_stream_si256')==6 and new_tu.count(b'_mm_sfence')==1
    assert new_tu.count(b'_MM_HINT_NTA')==5 and new_tu.count(b'_mm256_loadu_si256')==1
    assert new_tu.count(b'asm volatile')==3 and b'andn ' not in new_tu
    del changed[OLD_TU]
    changed[NEW_TU]=new_tu
    for rel in ('channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp'):
        assert changed[rel]==original[rel]

    files,patch=[],[]
    for rel,content in sorted(changed.items()):
        prior_rel=OLD_TU if rel==NEW_TU else rel
        prior=original[prior_rel]
        target=NEW/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
        files.append({'path':target.relative_to(ROOT).as_posix(),'sha256':digest(target),
            'parent_path':OLD_NAME+'/'+prior_rel,'same_bytes_as81':prior==content})
        if content!=prior:
            patch.extend(difflib.unified_diff(prior.decode().splitlines(keepends=True),content.decode().splitlines(keepends=True),
                fromfile=OLD_NAME+'/'+prior_rel,tofile=NEW_NAME+'/'+rel))
    (HERE/'source-diff.patch').write_bytes(''.join(patch).encode())
    (HERE/'deferred-vs81.patch').write_bytes(''.join(difflib.unified_diff(
        old_tu.decode().splitlines(keepends=True),new_tu.decode().splitlines(keepends=True),
        fromfile=OLD_NAME+'/'+OLD_TU,tofile=NEW_NAME+'/'+NEW_TU)).encode())

    plan=copy.deepcopy(parent)
    plan.update(purpose='修订82提案：多线程原地每64像素先提交完整首64B行，暂存32B输出，第二组读取完成后补齐；仅源码与构建计划冻结',
        base_commit=BASE_COMMIT,
        candidate='由81派生，仅新AVX2输入TU的64像素写入时序及实验身份改变；保留79的pair/linear原字节，先静态筛查寄存器溢出',
        cmake_project=NEW_NAME,cmake_targets=['jshc_skylake_reference','jshc_skylake_input256_deferred'],revisions={'reference':23,'candidate':82})
    plan['unchanged']=[
        '四级模型、Q16、逐级RGB8整数舍入、230项调色板、唯一16MiB format9线性ID表；构造不读照片或gold',
        '81保留的主线性与两个pair48 TU含导出名原字节不变，也仍与79相同；Handle、表、BMI检测及资源公式不变',
        '新deferred输入TU的read_wide、四ID屏障、pack_stream公式、32像素普通区段、精确24B尾、标量前缀均逐字节保持81',
        '64像素/192B整行推进、p+72/p+40边界、65536连续schedule(static)、NTA及406前瞻保护不变；整个64循环结束后一次SFENCE',
        '有效workers>1且AVX2和直表资格选新入口，不要求BMI；有效单线程/嵌套/非OMP和真正分离保留79分派，原pair资格getter保留',
        'fixed_inputs/suffix_models/contract/hardware/screen及完整域262144像素批次与80新增64个65793像素实际偏移夹具保持',
        '全部首次/确认/A/A/ABBA/16或64内轮/三倍验收门槛保持；82为独立同场新身份，81及其他失败不重测、不拼接旧成绩']
    plan['required_static_checks']=[
        '所有冻结源与构建身份一致；三个保留pair/linear对象.text必须与79和81相同，四个保留宽区段不缺失',
        '完整识别新64/32可达区段，每8像素仍仅一个32B输入内存操作，64/32分别8/4次；允许VPERMD合法内存源折叠',
        '逐字节追踪VPERMD与PSHUFB、GPR零扩展，64/32项ID及palette各完整一次；每四ID齐备后才读对应palette',
        '64区段真实地址按两组验证：第一组输入起点0/24/48/72、消费0..95，其全部输入/ID/palette均在首组图像写之前；首组仅写0和32两条NT，即完整首64B缓存行',
        '第二组输入起点96/120/144/168、物理范围96..199、实质消费96..191，不读取先写0..63所在缓存行；允许首两NT早于第二组源读，不得把合法分组顺序误判为64全部先读要求',
        'pending输出64..95及第二组96..191均须在第二组全部输入/ID/palette读取之后写；逐条验证六NT32B实际地址0/32/64/96/128/160、共192B且不重叠遗漏，不能把栈store算图像输出',
        '三结果x寄存器空asm必须使s0/s1/pending在首NT之前完成；它与保留的四ID屏障分工不同，须检查实际先两NT后第二组载荷，不以空asm源码替代对象证明；32区段仍全部先读后普通输出',
        '记录pending实际合并及寄存器使用，源级pending+4=5待输出向量只是减压假设，不冒称编译活跃上界；空asm自身不应生成机器指令，但可能改变调度/分配',
        '两个新宽区段均无真实rsp/frame spill、无循环内向量常量重复加载；尤其输入重排常量外提；无外部call/gather/BMI1/BMI2/EVEX/AVX512/FMA',
        '保留输入200/104B在216/120B内、精确8像素尾24B；首指针64B对齐，六NT均32B对齐，192B推进使下一轮及普通尾处于新完整行；SFENCE仍在整个64循环之后',
        '实际输入/重排/提取/写出宏指令分别报告，不以宏指令数或声明生命期代替微操作/性能证据；预排值只能使用原预排合并公式',
        '仅两个pair TU获-mbmi，新deferred TU只需AVX2；核对compile_commands、泛型dispatcher ISA及有效workers分派，无新增能力检测或字段',
        '任何静态失败即停止完整色域和性能，不放宽门槛、调参或重编择优；静态通过后由主流程冻结完整正确性及独立长批次身份']
    plan['preparation']={'state':'源码和构建计划已冻结；尚未编译、加载、执行像素或性能',
        'parent_plan':spec(OLD_PLAN),'new_tu_source_parent':spec(OLD/OLD_TU),'generator':spec(__file__),
        'no_performance_claim':True,'conditional_execution':'独立候选82只先做静态筛查；失败停止，81不重新执行；后续正确性与首次同场长批次由主流程冻结执行'}
    plan['prior_evidence'].update(basis)
    mechanism=plan.pop('input256')
    mechanism['selection']['inplace_effective_workers_gt1']='input256_deferred纯AVX2，不要求BMI'
    mechanism['readonly_apis']['new']=mechanism['readonly_apis']['new'].replace('input256','input256_deferred')
    mechanism['history'] += [
        '81同一输入机制在64区段0xe8..0x727出现0x4c9向-0x20(%rsp)写YMM及0x6e9读回，唯一构建静态停止，像素/性能0；32区段无栈，不把未测81写成性能负结果',
        '40/57/59及81均先保持r0..r7再两次output_four_stream；本次先完整首行、暂存中间32B的结构不同，不采用先写96B后读同一中间行的方案']
    mechanism['hypothesis']='仅通过更早提交完整首64B行、保留一个pending而缩短待输出生命期，尝试消除81已见YMM spill；输入、ID和palette操作量均不变，无已验证性能收益或三倍承诺'
    mechanism['risks'] += [
        '三结果x输入屏障要求pending提前形成，但源级5向量不等于实际分配；仍有七个重排常量与输入/输出临时量，屏障可能改变调度并继续spill或重载',
        '提前写首行可能改变指令调度、随机表请求并行窗口及写合并时机，不能据消除spill认定性能增益',
        '仅新多线程原地TU变更；相同源的其他路径也需本次同场验收，不得继承79旧成绩充当82结果']
    mechanism['deferred_output']={
        'pixels_per_iteration':64,'output_bytes':192,'nt_store_offsets':[0,32,64,96,128,160],
        'first_group_input_offsets':[0,24,48,72],'first_group_physical_read_range_inclusive':[0,103],
        'first_group_consumed_range_inclusive':[0,95],'first_group_early_store_offsets':[0,32],
        'early_written_range_inclusive':[0,63],'pending_range_inclusive':[64,95],
        'second_group_input_offsets':[96,120,144,168],'second_group_physical_read_range_inclusive':[96,199],
        'second_group_consumed_range_inclusive':[96,191],
        'result_barrier':'第一NT前asm volatile空模板，x(s0)/x(s1)/x(pending)输入及memory clobber，使三个最终输出值先完成；保留四ID屏障只负责ID齐备后读取palette',
        'source_lifetime_hypothesis':{'before':8,'after_pending_plus_outputs':5,'actual_compiler_live_count_known':False},
        'proof':'前组末32B载荷72..103仅消费72..95，额外96..103不参与索引；先写0..63与后组所有载荷所在行无重叠；pending64..95和后组三次NT均在后组读完后执行',
        'sfence':'仅整个64像素循环结束后一次，普通尾及OpenMP barrier之前；不在两组之间或每次迭代新增SFENCE'}
    plan['input256_deferred']=mechanism
    plan['correctness_requirements']['negative_getter_cases']=plan['correctness_requirements']['negative_getter_cases'].replace('input256','input256_deferred')
    plan['acceptance_invariants']['confirmation']['output']='artifacts/skylake-input256-deferred-long-confirm-v1'
    sources={p.replace(OLD_NAME+'/',NEW_NAME+'/').replace('/'+OLD_TU,'/'+NEW_TU):h
        for p,h in parent['source_sha256'].items()}
    sources.update({f['path']:f['sha256'] for f in files})
    plan['source_sha256']=dict(sorted(sources.items()))
    assert len(files)==11 and len(sources)==72
    assert all(digest(ROOT/p)==h for p,h in sources.items())
    invariants=('fixed_inputs','suffix_models','contract','hardware','screen')
    assert all(plan[k]==parent[k] for k in invariants)
    acceptance=copy.deepcopy(plan['acceptance_invariants'])
    acceptance['confirmation']['output']=parent['acceptance_invariants']['confirmation']['output']
    assert acceptance==parent['acceptance_invariants']
    correctness=copy.deepcopy(plan['correctness_requirements'])
    correctness['negative_getter_cases']=parent['correctness_requirements']['negative_getter_cases']
    assert correctness==parent['correctness_requirements']
    save(NEW_PLAN,plan)
    receipt={'purpose':__doc__,'frozen':True,'base_commit':BASE_COMMIT,'plan':spec(NEW_PLAN),'parent_plan':spec(OLD_PLAN),
        'generator':spec(__file__),'new_tu_parent':spec(OLD/OLD_TU),'candidate_files':files,'source_entries':len(sources),
        'preserved_exact_pixel_sources':['channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp'],
        'new_tu_outside_64_body_equal81_after_entry_rename':True,'unchanged_read_wide_and_exact_tail':True,
        'runtime_header_changes':'仅input256身份改input256_deferred、revision82；分派/Handle/getter语义保持',
        'source_diff':spec(HERE/'source-diff.patch'),'input_diff':spec(HERE/'deferred-vs81.patch'),
        'preserved_plan_fields':list(invariants),'acceptance_changed_only_confirmation_output_identity':True,
        'correctness_changed_only_getter_identity':True,'prior_evidence':basis,
        'source_lifetime_note':'pending+4是源级减压假设，实际编译活跃数未知，必须检查对象spill/常量重载',
        'builds':0,'compiler_calls':0,'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0}
    save(HERE/'preparation.json',receipt)
    print(json.dumps({'frozen':True,'plan':receipt['plan'],'files':len(files),'source_entries':len(sources),
        'new_tu':spec(NEW/NEW_TU),'preparation':spec(HERE/'preparation.json'),'native_calls':0},ensure_ascii=False))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
