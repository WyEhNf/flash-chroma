"""读取既有完整首级输出，核算固定缓存未命中及输入反例；不重跑任何映射。"""
from __future__ import annotations
import argparse,hashlib,json,platform,sys,zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','bundle','gold','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan=read(args.plan);bundle=read(args.bundle/'bundle-manifest.json')
    gold=read(args.gold/'generation.json');out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖未命中分析')
    if gold['inputs']['base']!=plan['fixed_inputs']['base'] or gold['inputs']['suffix']!=plan['suffix_models']:
        raise ValueError('缓存范围不对应当前模型')
    first=args.bundle/bundle['single_oracle_stream'];final_output=args.bundle/plan['fixed_inputs']['cube']['path']
    if bundle['files'][plan['fixed_inputs']['cube']['path']]['sha256']!=plan['fixed_inputs']['cube']['sha256']:
        raise ValueError('完整最终输出流不是冻结计划所用字节')
    for path,expected_sha in ((first,bundle['files'][bundle['single_oracle_stream']]['sha256']),
                              (final_output,plan['fixed_inputs']['cube']['sha256'])):
        if sha(path)!=expected_sha:raise ValueError('既有完整流SHA不同')
    if first.stat().st_size!=256**3*3 or final_output.stat().st_size!=256**3*3:raise ValueError('完整域流大小不同')
    # cube.rgb是最终输出，不能误作输入；由原生成器及其逐字节归档证明首级流的RGB24枚举顺序。
    prior=ROOT/'report/data/skylake-suffix-cache-v1';manifest=read(prior/'manifest.json')
    for name in ('full-run.json','full-results.json','full-measured-source.zip'):
        if sha(prior/name)!=manifest['files'][name]['sha256']:raise ValueError('历史生成证据不同')
    proof=read(prior/'full-results.json');run=read(prior/'full-run.json')
    if (not proof['pass'] or proof['cube']['single_oracle_sha256']!=sha(first)
        or proof['base']!=plan['fixed_inputs']['base'] or proof['sidecar']!=plan['fixed_inputs']['sidecar']):
        raise ValueError('首级流不是已验固定模型')
    with zipfile.ZipFile(prior/'full-measured-source.zip') as z:producer=z.read('scripts/accept_skylake_runtime.py')
    producer_sha=hashlib.sha256(producer).hexdigest()
    if producer_sha!=run['source_sha256']['scripts/accept_skylake_runtime.py']:raise ValueError('原生成器SHA不同')
    text=producer.decode('utf-8')
    if ('np.column_stack((ids >> 16, (ids >> 8) & 255, ids & 255))' not in text
        or 'first_stream[start:start+len(single)] = single' not in text):raise ValueError('枚举生成器需重新审阅')
    bounds=gold['bounds'];lower=np.array([bounds['r_min'],bounds['dg_min'],bounds['db_min']],np.int16)
    upper=np.array([bounds['r_max'],bounds['dg_max'],bounds['db_max']],np.int16)
    data=np.memmap(first,np.uint8,'r',shape=(256**3,3))
    count=0;by_axis=np.zeros(3,np.int64);below=np.zeros(3,np.int64);above=np.zeros(3,np.int64)
    minimum=np.full(3,999,np.int16);maximum=np.full(3,-999,np.int16);examples=[];extremes={}
    for start in range(0,256**3,2**20):
        stop=min(start+2**20,256**3);keys=np.arange(start,stop,dtype=np.uint32)
        expected=np.column_stack((keys>>16,(keys>>8)&255,keys&255)).astype(np.uint8)
        rgb=data[start:stop].astype(np.int16);coord=rgb.copy();coord[:,1:]-=coord[:,0,None]
        lo=coord<lower;hi=coord>upper;bad=lo|hi;miss=bad.any(axis=1)
        count+=int(miss.sum());by_axis+=bad.sum(axis=0);below+=lo.sum(axis=0);above+=hi.sum(axis=0)
        for axis in range(3):
            for label,fn,target,comparison in (('minimum',np.argmin,minimum,np.less),('maximum',np.argmax,maximum,np.greater)):
                i=int(fn(coord[:,axis]));value=int(coord[i,axis])
                if comparison(value,target[axis]):
                    target[axis]=value;extremes[f'{axis}_{label}']={'input_rgb':expected[i].tolist(),
                        'first_stage_rgb':rgb[i].tolist(),'cache_coordinates_R_dG_dB':coord[i].tolist()}
        if len(examples)<8:
            for i in np.flatnonzero(miss)[:8-len(examples)]:
                examples.append({'input_rgb':expected[i].tolist(),'first_stage_rgb':rgb[i].tolist(),
                                 'cache_coordinates_R_dG_dB':coord[i].tolist(),'failed_axes':np.flatnonzero(bad[i]).tolist()})
    result={'purpose':__doc__,'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'source_sha256':sha(__file__),'plan_sha256':sha(args.plan),'bundle_manifest_sha256':sha(args.bundle/'bundle-manifest.json'),
        'gold_generation_sha256':sha(args.gold/'generation.json'),'first_stream_sha256':sha(first),'final_output_stream_sha256':sha(final_output),
        'enumeration_source_verified':True,'enumeration_producer_sha256':producer_sha,
        'prior_full_results_sha256':sha(prior/'full-results.json'),'prior_full_run_sha256':sha(prior/'full-run.json'),
        'total_colours':256**3,'bounds':bounds,'cache_miss_colours':count,'miss_fraction':count/256**3,
        'outside_by_axis_R_dG_dB':by_axis.tolist(),'below_by_axis':below.tolist(),'above_by_axis':above.tolist(),
        'observed_min_R_dG_dB':minimum.tolist(),'observed_max_R_dG_dB':maximum.tolist(),'first_eight_misses':examples,
        'extremes':extremes,'decision':'存在真实未命中，当前缓存不能无条件省去范围检查' if count else '既有固定完整域全部命中，但新实现仍须通用构造证明',
        'project_native_calls':0,'performance_calls':0,'new_fits':0,'new_pixel_mappings':0,
        'scope':'重读已验首级输出；未产生新映射或最终图像，未改变原正确回退路径，不把缓存miss当作数值错误。'}
    out.mkdir();(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('cache_miss_colours','miss_fraction','observed_min_R_dG_dB','observed_max_R_dG_dB','first_eight_misses','decision')},ensure_ascii=False))


if __name__=='__main__':main()
