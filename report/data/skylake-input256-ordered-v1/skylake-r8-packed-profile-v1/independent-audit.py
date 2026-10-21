"""R连续8色离线结果的轻量独立审计；不重扫完整cube/照片、不运行原生或性能。"""
import ast
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def close(a,b):return math.isclose(a,b,rel_tol=1e-13,abs_tol=1e-13)


def literals(path):
    result={}
    for node in ast.parse(Path(path).read_text(encoding='utf-8')).body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            try:result[node.targets[0].id]=ast.literal_eval(node.value)
            except (ValueError,TypeError):pass
    return result


def main():
    target=HERE/'independent-audit.json';assert not target.exists()
    result=read(HERE/'analysis.json');protocol=read(HERE/'protocol.json')
    source=HERE/'analyze.py';generator=ROOT/'artifacts/prepare_r8_packed_profile.py'
    constants=literals(source);checks={};details={}
    checks['frozen_identity']=result['script_sha256']==protocol['script_sha256']==sha(source) and result['protocol_sha256']==sha(HERE/'protocol.json')
    checks['fixed_gate']=protocol['gate']=={'exception_packet8_fraction_max':.05,'mean_word_lines_per64_ratio_max':.8}
    checks['analysis_completed_without_native']=result['analysis_completed'] and all(result[k]==0 for k in ('native_calls','performance_calls','compiler_calls','new_fits'))

    # 只解释生成器的字符串替换，绝不执行其mkdir、写文件或原profile入口。
    generator_source=ROOT/'artifacts/skylake-brick2-packed-profile-v1/analyze.py'
    reconstructed=generator_source.read_text(encoding='utf-8');values={};replacements=0
    for node in ast.parse(generator.read_text(encoding='utf-8')).body:
        if not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name):continue
        name=node.targets[0].id
        if name=='old':values[name]=ast.literal_eval(node.value)
        if name=='text' and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='text' and node.value.func.attr=='replace':
            arguments=[values[a.id] if isinstance(a,ast.Name) else ast.literal_eval(a) for a in node.value.args]
            reconstructed=reconstructed.replace(*arguments);replacements+=1
    checks['generator_reproduces_exact_script']=reconstructed.encode()==source.read_bytes()
    details['generator_string_replacements']=replacements

    previous_path=ROOT/'artifacts/skylake-brick2-packed-profile-v1/analysis.json'
    previous=read(previous_path);input_checks=[]
    for name,(relative,expected) in constants['SPECS'].items():
        stored=result['inputs'][name];p=ROOT/relative;size=p.stat().st_size
        same=stored['path']==relative and stored['sha256']==expected and stored['bytes']==size
        cross=previous['inputs'][name]['sha256']==expected and previous['inputs'][name]['bytes']==size
        # 为不干扰主流程，不重读50MiB cube与225MiB照片；小文件独立重哈希。
        small=size<=2**20
        actual=sha(p) if small else None
        input_checks.append({'name':name,'path':relative,'recorded_sha256':expected,'bytes':size,
            'matches_frozen_script_and_size':same,'matches_prior_profile_identity':cross,
            'independently_rehashed_now':small,'actual_sha256':actual,'pass':same and cross and (not small or actual==expected)})
    checks['input_identities']=all(x['pass'] for x in input_checks)
    generation_path=ROOT/result['inputs']['cache_generation']['path'];generation=read(generation_path)
    checks['cache_generation_identity']=sha(generation_path)==result['inputs']['cache_generation']['sha256'] and generation['generation_completed'] and generation['gold_sha256']==constants['SPECS']['cache_gold'][1] and generation['inputs']==result['inputs']['cache_generation']['model_inputs']
    gold=(ROOT/constants['SPECS']['cache_gold'][0]).read_bytes()
    palette=sorted({x[0] for x in struct.iter_unpack('<I',gold)})
    old_palette=[x[0] for x in struct.iter_unpack('<I',(ROOT/constants['SPECS']['old_palette_crosscheck'][0]).read_bytes())]
    p=result['palette'];d=result['full_domain'];photos=result['photos'];rows=result['per_image']
    checks['exact_230_palette_from_gold']=len(palette)==230 and palette==p['values_rgb32']==old_palette[:230] and len(old_palette)==256 and old_palette[230:]==[0]*26
    checks['palette_frequency_totals']=len(p['output_id_frequency'])==230 and sum(p['output_id_frequency'])==2**24 and sum(x>0 for x in p['output_id_frequency'])==p['complete_cube_used_entries']==221
    checks['logical_id_hash_crosscheck']=d['linear_id_sha256']==constants['DIRECT_SHA']==previous['full_domain']['linear_id_sha256']

    # 分离低3位的双射是代数恒等式；仅对边界点辅助核对，不重跑16M循环。
    points=[0,1,7,8,127,128,255,256,65535,65536,2**24-1]
    checks['mapping_boundary_examples']=all(((c>>3)<<3)|(c&7)==c and 0<=c>>3<2**21 and 0<=c&7<8 for c in points)
    checks['mapping_source_formulas']=all(s in source.read_text(encoding='utf-8') for s in (
        'def coarse(c):return c>>3','def fine(c):return c&7','def inverse(q,k):return (q<<3)|k',
        'direct[:,:,r]=ids.T','members=linear.reshape(-1,8)','counts_word=set_counts(q>>4)','counts_old=set_counts(c>>6)'))
    span=d['span_histogram'];max_span=max(i for i,n in enumerate(span) if n)
    checks['span_histogram']=sum(span)==d['blocks']==2**21 and sum(span[8:])==d['exception_blocks']==324748 and sum(span[:8])==d['normal_blocks'] and max_span==d['max_id_span']==26
    checks['span_fraction']=close(d['exception_block_fraction'],d['exception_blocks']/d['blocks'])
    worst=d['worst_block'];base_code=worst['coarse']<<3
    checks['worst_block_consistent']=worst['rgb_min']==[base_code&255,(base_code>>8)&255,(base_code>>16)&255] and len(worst['ids'])==8 and max(worst['ids'])-min(worst['ids'])==max_span
    checks['encoding_resources']=max(palette)<2**24 and d['word_bytes']==2**21*4 and d['exception_payload_bytes']==d['exception_blocks']*8 and d['total_payload_bytes']==d['word_bytes']+d['exception_payload_bytes'] and d['exception_blocks']<2**24
    checks['recorded_full_verification_zero']=d['colors']==2**24 and d['decode_id_mismatches']==d['index_inverse_mismatches']==0

    manifest=read(ROOT/constants['SPECS']['manifest'][0]);old_rows=previous['per_image'];row_checks=[]
    for i,(row,meta,prior) in enumerate(zip(rows,manifest['images'],old_rows)):
        pixels=row['pixels'];packets=row['packets8'];windows=row['windows64']
        old=row['sum_original_id_lines'];word=row['sum_word_lines'];pool=row['sum_exception_pool_lines']
        good=row['image_index']==i and row['image_id']==meta['id'] and row['pixel_sha256']==meta['evaluation']['pixel_sha256']
        good &= row['pixel_sha256']==prior['pixel_sha256'] and row['sum_original_id_lines']==prior['sum_original_id_lines']
        good &= pixels==1024*768 and packets*8==pixels and windows*64==pixels
        good &= 0<=row['exception_packets8']<=row['exception_pixels']<=8*row['exception_packets8'] and row['exception_pixels']<=pixels
        good &= windows<=word<=old<=windows*64 and 0<=pool<=row['exception_pixels']
        good &= all(close(a,b) for a,b in (
            (row['exception_packet8_fraction'],row['exception_packets8']/packets),
            (row['mean_original_id_lines'],old/windows),(row['mean_word_lines'],word/windows),
            (row['word_lines_ratio'],word/old),(row['word_plus_exception_lines_ratio'],(word+pool)/old)))
        row_checks.append({'image_index':i,'pass':bool(good)})
    checks['all_100_per_image_rows']=len(rows)==len(manifest['images'])==len(old_rows)==100 and all(r['pass'] for r in row_checks)
    totals={k:sum(r[k] for r in rows) for k in ('pixels','packets8','windows64','exception_pixels','exception_packets8','sum_original_id_lines','sum_word_lines','sum_exception_pool_lines')}
    checks['photo_integer_totals']=all(photos[k]==totals[k] for k in ('pixels','packets8','windows64','exception_pixels','exception_packets8')) and photos['images']==100 and totals['pixels']==235929600//3
    old,word,pool=(totals[k] for k in ('sum_original_id_lines','sum_word_lines','sum_exception_pool_lines'))
    checks['photo_floats']=all(close(a,b) for a,b in (
        (photos['exception_packet8_fraction'],totals['exception_packets8']/totals['packets8']),
        (photos['mean_original_id_lines_per64'],old/totals['windows64']),
        (photos['mean_word_lines_per64'],word/totals['windows64']),
        (photos['mean_exception_pool_lines_per64'],pool/totals['windows64']),
        (photos['word_lines_ratio'],word/old),(photos['word_plus_exception_lines_ratio'],(word+pool)/old)))
    histogram_checks=[]
    for key,total,length in [('original_lines_histogram',old,65),('word_lines_histogram',word,65),('word_plus_exception_lines_histogram',word+pool,129)]:
        hist=photos[key]
        histogram_checks.append({'field':key,'count':sum(hist),'weighted_sum':sum(i*n for i,n in enumerate(hist)),
            'pass':len(hist)==length and all(isinstance(x,int) and x>=0 for x in hist) and sum(hist)==totals['windows64'] and sum(i*n for i,n in enumerate(hist))==total})
    checks['histograms_match_per_image_sums']=all(h['pass'] for h in histogram_checks)
    checks['original_histogram_matches_prior']=photos['original_lines_histogram']==previous['photos']['original_lines_histogram']
    checks['coarsened_line_histogram_dominates']=all(sum(photos['word_lines_histogram'][:i+1])>=sum(photos['original_lines_histogram'][:i+1]) for i in range(65))
    checks['reported_output_hash_matches_prior']=photos['decoded_output_sha256']==constants['PHOTO_OUTPUT_SHA']==previous['photos']['decoded_output_sha256']
    gate=result['gate'];expected_gate=totals['exception_packets8']/totals['packets8']<=.05 and word/old<=.8
    checks['gate_recomputed']=not expected_gate and not gate['passed'] and not gate['exception_packets_pass'] and not gate['line_set_pass'] and close(gate['exception_packet8_fraction'],totals['exception_packets8']/totals['packets8']) and close(gate['mean_word_lines_ratio'],word/old) and gate['exception_packet8_fraction_max']==.05 and gate['mean_word_lines_ratio_max']==.8

    histories={
        'revision23':'experiments/skylake-exception-runtime/channel_avx2.cpp',
        'revision42':'experiments/skylake-wordload-runtime/channel_avx2.cpp',
        'revision62':'experiments/skylake-pack5-runtime/channel_avx2.cpp'}
    text={k:(ROOT/v).read_text(encoding='utf-8') for k,v in histories.items()}
    checks['historical_axes_and_bits']=('_mm256_setr_epi8(2,1,0,-1' in text['revision23'] and '_mm256_srli_epi32(code,3)' in text['revision23']
        and '__builtin_bswap32(code)>>8' in text['revision42'] and 'table[code>>3]' in text['revision42']
        and '8+5*(code&7u)' in text['revision62'] and 'value(uint32_t(a&0xffffff))' in text['revision62'])
    checks['history_claim_is_limited']='不据关键词搜索断言完整组合从未实现' in result['history']['conclusion']
    findings=[
        'R低的c>>3/c&7及逆式严格双射；direct[b,g,r]按R低线性化，区别23/42的B低8色3bit；62为相同R连续8色但5bit。',
        '正常base在0..229，255哨兵不冲突；8个3bit差值恰占bit8..31，例外24bit块编号与8B原ID块无损。',
        '主词缓存行是c>>7，原ID行是c>>6；例外池按8B块/64B行计ordinal>>3且独立对齐，报告的是行集合而非miss或吞吐。',
        '固定8像素包的异常率23.500732421875%，超过5%；主词行比0.9978266665810297，高于0.80；含例外池为1.109097968148663，停止结论成立。']
    audit={'purpose':__doc__,'audit_passed':all(checks.values()),'checks':checks,'findings':findings,'blocking_findings':[],
        'identity':{'analysis_sha256':sha(HERE/'analysis.json'),'protocol_sha256':sha(HERE/'protocol.json'),'analyze_sha256':sha(source),
            'generator_sha256':sha(generator),'generator_source_sha256':sha(generator_source),'previous_profile_sha256':sha(previous_path),'audit_script_sha256':sha(__file__)},
        'input_checks':input_checks,'per_image_checks':row_checks,'recomputed_totals':totals,'histogram_checks':histogram_checks,
        'full_domain_aggregate':{'exception_blocks':sum(span[8:]),'max_span':max_span,'word_bytes':d['word_bytes'],
            'exception_payload_bytes':d['exception_payload_bytes'],'total_payload_bytes':d['total_payload_bytes']},
        'history_sources':{k:{'path':v,'sha256':sha(ROOT/v)} for k,v in histories.items()},'generator_check':details,
        'limitations':['不重扫完整16M颜色或100图；完整域零差、word/pool哈希及照片输出哈希为冻结原运行记录，独立审计只核对算法与汇总。',
            '50MiB cube和225MiB照片未在本次重新哈希；按冻结脚本、原结果、此前brick2原件、文件长度及逐图manifest哈希交叉核对。',
            '逐图原始结果仅保存计数汇总而非全部窗口序列；可验证直方图总数/加权和及100行汇总，不能据此重建每个窗口。'],
        'full_profile_reexecutions':0,'large_input_bytes_read':0,'native_calls':0,'compiler_calls':0,'performance_calls':0}
    audit['blocking_findings']=[k for k,v in checks.items() if not v]
    with target.open('x',encoding='utf-8') as f:json.dump(audit,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'audit_passed':audit['audit_passed'],'failed':audit['blocking_findings'],
        'exception_packet8_fraction':totals['exception_packets8']/totals['packets8'],'word_ratio':word/old,
        'word_plus_pool_ratio':(word+pool)/old,'audit_sha256':sha(target)},ensure_ascii=False))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
