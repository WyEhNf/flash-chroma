"""仅准备并冻结修订83编译顺序修复；保留82失败，不编译或执行候选。"""
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD_NAME='experiments/skylake-input256-deferred-runtime'
NEW_NAME='experiments/skylake-input256-ordered-runtime'
OLD,NEW=ROOT/OLD_NAME,ROOT/NEW_NAME
OLD_PLAN=ROOT/'experiments/skylake-input256-deferred-v1.json'
NEW_PLAN=ROOT/'experiments/skylake-input256-ordered-v1.json'
OLD_TU='deferred_inplace/channel_avx2.cpp'
NEW_TU='ordered_inplace/channel_avx2.cpp'
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
    assert not NEW.exists() and not NEW_PLAN.exists() and not(HERE/'preparation.json').exists(), '不覆盖已有候选或结果'
    assert digest(OLD_PLAN)=='20fedf0f1f0427ab7a9d078f5842fd24fe3943e7b8b8eeedc3846a1593f3009e'
    parent=load(OLD_PLAN)
    assert all(digest(ROOT/p)==h for p,h in parent['source_sha256'].items())
    basis={
        'revision82_build':spec('artifacts/skylake-input256-deferred-linux-build-v1/build.json'),
        'revision82_static':spec('artifacts/skylake-input256-deferred-static-v1/results.json'),
        'revision82_independent_static':spec('artifacts/skylake-input256-deferred-static-v1/independent_results.json')}
    expected={
        'revision82_build':'9a15636424ac4a59ce2cc3d694387ef504360c14ef78105b667c2b0abee9f601',
        'revision82_static':'f802919d4207b5c0e27842a0ad2c0d148ca9b45d74401903702c72aa9e630c93',
        'revision82_independent_static':'961dcc2658d6110d319cc23435935523439db4b3d5c9bcf3d69e69b43e7ae4f5'}
    assert all(basis[k]['sha256']==h for k,h in expected.items())
    for name in ('revision82_static','revision82_independent_static'):
        evidence=load(ROOT/basis[name]['path'])
        assert not evidence['accepted'] and evidence['pixel_calls']==0 and evidence['performance_calls']==0
    independent=load(ROOT/basis['revision82_independent_static']['path'])
    assert independent['failure_reason']==['64像素区段/second_input_after_two_nt']

    original={p.relative_to(OLD).as_posix():p.read_bytes() for p in OLD.rglob('*') if p.is_file()}
    assert len(original)==11
    changed=dict(original)
    for rel in ('channel_runtime.cpp','suffix_cache.hpp'):
        changed[rel]=original[rel].replace(b'input256_deferred',b'input256_ordered')
    changed['channel_runtime.cpp']=once(changed['channel_runtime.cpp'],
        b'uint32_t jshc_cc_revision(void) {return 82;}',b'uint32_t jshc_cc_revision(void) {return 83;}')
    changed['CMakeLists.txt']=original['CMakeLists.txt'].replace(b'input256_deferred',b'input256_ordered').replace(
        b'deferred_inplace/channel_avx2.cpp',b'ordered_inplace/channel_avx2.cpp')
    old_tu=original[OLD_TU]
    nl=b'\r\n' if b'\r\n' in old_tu else b'\n'
    marker=b'    _mm256_stream_si256(reinterpret_cast<__m256i*>(destination+3*p+32),s1);'+nl
    addition=nl.join([
        '    // 阻止第二组输入被编译器前移到首行两次NT之间；这不是硬件栅栏。'.encode(),
        b'    asm volatile("" : : : "memory");',b''])
    new_tu=once(old_tu,marker,marker+addition)
    new_tu=once(new_tu,b'avx2_chain_input256_deferred_mt(',b'avx2_chain_input256_ordered_mt(')
    assert new_tu.replace(addition,b'').replace(b'avx2_chain_input256_ordered_mt(',b'avx2_chain_input256_deferred_mt(')==old_tu
    assert new_tu.count(b'asm volatile')==4 and new_tu.count(b'_mm_sfence')==1
    assert new_tu.count(b'_mm256_stream_si256')==6 and new_tu.count(b'_MM_HINT_NTA')==5
    del changed[OLD_TU];changed[NEW_TU]=new_tu
    for rel in ('channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp'):
        assert changed[rel]==original[rel]
    files,patch=[],[]
    for rel,content in sorted(changed.items()):
        prior_rel=OLD_TU if rel==NEW_TU else rel;before=original[prior_rel]
        path=NEW/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
        files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),
            'parent_path':OLD_NAME+'/'+prior_rel,'same_bytes_as82':content==before})
        if content!=before:
            patch.extend(difflib.unified_diff(before.decode().splitlines(keepends=True),content.decode().splitlines(keepends=True),
                fromfile=OLD_NAME+'/'+prior_rel,tofile=NEW_NAME+'/'+rel))
    (HERE/'source-diff.patch').write_bytes(''.join(patch).encode())
    (HERE/'ordered-vs82.patch').write_bytes(''.join(difflib.unified_diff(
        old_tu.decode().splitlines(keepends=True),new_tu.decode().splitlines(keepends=True),
        fromfile=OLD_NAME+'/'+OLD_TU,tofile=NEW_NAME+'/'+NEW_TU)).encode())

    plan=copy.deepcopy(parent)
    plan.update(purpose='修订83提案：在首64B行的两次NT之后增加空memory编译器屏障，约束第二组输入不得前移；仅源码和计划冻结',
        base_commit=BASE_COMMIT,candidate='由82派生，唯一机制变化是首两NT后的编译器memory屏障；现有三结果x屏障和四ID屏障保留；不重新执行82',
        cmake_project=NEW_NAME,cmake_targets=['jshc_skylake_reference','jshc_skylake_input256_ordered'],revisions={'reference':23,'candidate':83})
    plan['unchanged']=[
        '四级模型、Q16、逐级RGB8整数舍入、230项调色板及唯一16MiB format9线性ID表；构造不读取照片或gold',
        '82的pair48/linear三个TU原字节保留，仍等79和81；Handle、BMI检测、资源、effective workers分派不变，仅实验身份和revision改变',
        '新ordered输入TU除首两NT后新增空memory屏障及入口名之外逐字节等82；read_wide、三结果x屏障、四ID屏障、预排及合并公式不变',
        '每64像素/192B推进、72/40边界、精确24B尾、NTA及406前瞻、65536连续schedule(static)、单次循环后SFENCE全部保留',
        '有效多线程原地只需AVX2及直表；单线程/嵌套/非OMP和真正分离仍保留79 pair48/BMI回退；两资格getter语义不变',
        '固定输入/模型/契约/硬件筛查范围、完整RGB8矩阵及64个65793像素真实对齐夹具不变',
        '三倍目标及首次/确认/A/A/ABBA/16或64内轮门槛不变；83独立身份只允许一次构建静态，失败停止，82原件保留且不执行']
    plan['required_static_checks']=[
        '全部冻结源、plan和build身份相同；保留三个pair/linear对象.text等79/81/82，四个保留宽区段不能缺失',
        '完整识别新64/32可达区段；每8像素只一个32B输入内存操作，64/32分别8/4次，VPERMD合法内存折叠允许；逐字节跟踪RGB24零扩展',
        '四ID屏障仍要求对应四个u8 ID全部到齐后才读palette；64/32项ID和palette每像素完整且恰一次',
        '第一组输入0/24/48/72及其全部ID/palette均早于首两NT；三个最终s0/s1/pending值必须在首NT之前实际形成，pending保持于寄存器而非栈',
        '首两NT目标集合恰{0,32}，每条32B，完整覆盖首64B行；两者内部顺序不限，但两者均必须早于第二组任一input load，不能只看源码屏障',
        '第二组物理load起点96/120/144/168、范围96..199，实质消费96..191，不回读先写首行；后四NT目标集合恰{64,96,128,160}，均在后组全部input/ID/palette之后，内部顺序不限',
        '六条NT精确写192B且全部输出RGB字节标签正确、无遗漏或重叠；栈存储须独立分类，不能充当图像写；32普通区段保持全部先读后写',
        '新宽区段无真实rsp/frame spill、无热循环常量重载；输入重排/输出常量外提，无外部call/gather/BMI1/BMI2/EVEX/AVX512/FMA',
        '空memory asm仅为编译器屏障，新增位置不应生成硬件栅栏；SFENCE仍恰在整个64循环之后一次；NTA位置/数量不变，不能在两组间新增SFENCE',
        '64/32宽读200/104B分别在216/120B内，精确8像素尾24B；64B首地址对齐、所有NT32B对齐、192B推进及原普通尾/线程块边界保持',
        '只有两个pair TU含-mbmi，新ordered仅AVX2；核对实际compile_commands及通用dispatcher ISA，资格getter不冒充每次实际路径执行计数',
        '报告真实宏指令、输入load、向量常量和寄存器使用；源级pending+4=5仍是假设，不据宏指令/消除spill宣称吞吐收益',
        '83只允许唯一构建与静态筛查；任何真实门槛失败停止，不修改冻结源/门槛或挑样重跑；只有静态通过后由主流程执行新身份完整正确性和同场受控长批次']
    plan['preparation']={'state':'源码和构建计划已冻结，尚未编译、加载、执行像素或性能',
        'parent_plan':spec(OLD_PLAN),'new_tu_source_parent':spec(OLD/OLD_TU),'generator':spec(__file__),
        'no_performance_claim':True,'maximum_builds':1,
        'conditional_execution':'83唯一新身份先静态；失败即止；82静态失败原件不变且像素/性能保持0，不以83替换82记录'}
    plan['prior_evidence'].update(basis)
    mechanism=plan.pop('input256_deferred')
    mechanism['selection']['inplace_effective_workers_gt1']='input256_ordered纯AVX2，不要求BMI'
    mechanism['readonly_apis']['new']=mechanism['readonly_apis']['new'].replace('input256_deferred','input256_ordered')
    mechanism['history'] += [
        '82唯一构建无spill/热常量重载，64/32宏指令281/151；独立输出标签及所有地址正确，但0x3f4 NT32、0x3f9 load96、0x3ff NT0违反预冻结先两NT后第二组load门槛，停止且像素/性能0',
        '82的32→0首两写顺序本身不影响完整行覆盖，load96也不回读已写首行；83事前用地址集合表达同组覆盖，并新增编译器屏障确保两个首写都在后组load之前；没有声称82已测精度或性能']
    mechanism['hypothesis']='首两NT后的空memory屏障约束编译器不把第二组输入夹入两次写之间；这是82静态调度约束修复，不是硬件排序机制，不保证性能提升或三倍'
    mechanism['risks'] += [
        '新增编译器屏障可能改变调度及寄存器分配，83仍可能spill/重载，必须重新静态核对',
        '空asm不提供硬件内存栅栏；本方案安全依赖后组输入与先写整行无重叠，硬件发布仍使用原循环后SFENCE']
    mechanism['deferred_output']['compiler_memory_barrier']='首两NT语句之后、r4读取之前的asm volatile空模板与memory clobber；仅编译器顺序屏障，不是SFENCE'
    mechanism['deferred_output']['ordering_gate']={
        'early_store_offset_set':[0,32],'all_early_before_any_second_input':True,
        'late_store_offset_set':[64,96,128,160],'all_late_after_all_second_reads':True,
        'within_each_store_group_order_required':False}
    plan['input256_ordered']=mechanism
    plan['correctness_requirements']['negative_getter_cases']=plan['correctness_requirements']['negative_getter_cases'].replace('input256_deferred','input256_ordered')
    plan['acceptance_invariants']['confirmation']['output']='artifacts/skylake-input256-ordered-long-confirm-v1'
    sources={p.replace(OLD_NAME+'/',NEW_NAME+'/').replace('/'+OLD_TU,'/'+NEW_TU):h for p,h in parent['source_sha256'].items()}
    sources.update({f['path']:f['sha256'] for f in files});plan['source_sha256']=dict(sorted(sources.items()))
    assert len(files)==11 and len(sources)==72 and all(digest(ROOT/p)==h for p,h in sources.items())
    invariants=('fixed_inputs','suffix_models','contract','hardware','screen')
    assert all(plan[k]==parent[k] for k in invariants)
    acceptance=copy.deepcopy(plan['acceptance_invariants']);acceptance['confirmation']['output']=parent['acceptance_invariants']['confirmation']['output']
    assert acceptance==parent['acceptance_invariants']
    correctness=copy.deepcopy(plan['correctness_requirements']);correctness['negative_getter_cases']=parent['correctness_requirements']['negative_getter_cases']
    assert correctness==parent['correctness_requirements']
    save(NEW_PLAN,plan)
    receipt={'purpose':__doc__,'frozen':True,'base_commit':BASE_COMMIT,'plan':spec(NEW_PLAN),'parent_plan':spec(OLD_PLAN),
        'generator':spec(__file__),'new_tu_parent':spec(OLD/OLD_TU),'candidate_files':files,'source_entries':len(sources),
        'preserved_exact_pixel_sources':['channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp'],
        'only_new_mechanism':'首两NT之后、r4之前新增空memory编译器屏障；三结果x屏障及四ID屏障原样保留',
        'new_tu_other_bytes_equal82_after_entry_rename':True,'source_diff':spec(HERE/'source-diff.patch'),
        'input_diff':spec(HERE/'ordered-vs82.patch'),'prior_evidence':basis,'preserved_plan_fields':list(invariants),
        'acceptance_changed_only_confirmation_output_identity':True,'correctness_changed_only_getter_identity':True,
        'builds':0,'compiler_calls':0,'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0}
    save(HERE/'preparation.json',receipt)
    print(json.dumps({'frozen':True,'plan':receipt['plan'],'new_tu':spec(NEW/NEW_TU),
        'preparation':spec(HERE/'preparation.json'),'files':len(files),'source_entries':len(sources),'native_calls':0},ensure_ascii=False))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
