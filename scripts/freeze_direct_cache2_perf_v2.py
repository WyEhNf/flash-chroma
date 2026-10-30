"""293/294 V2静态freezer草稿；未经root授权不得执行导出、hash或冻结。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=Path('F:/Hackathon/projects/16-lut-color')
ROLES=['87-a399','87-best','293-best','294-best','293-max41','294-max41']
PAIRS=[('293-max41','87-a399',True),('293-max41','87-best',True),('293-max41','293-best',True),
    ('294-max41','87-a399',True),('294-max41','87-best',True),('294-max41','294-best',True),
    ('293-best','87-best',False),('294-best','87-best',False),('294-max41','293-max41',False)]

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,value):
    if path.exists():raise FileExistsError('V2冻结/导出不覆盖：'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def expected_states(quality,prior):
    # 仅消费既有质量/旧87原始诊断；不得用本次计时后首次状态反向定义期望。
    old={row['role']:row['state'] for row in prior['cold']}
    keys=('cache','domain','palette','direct','model_bytes')
    result={name:{**{key:old[source][key] for key in keys},'wide':None}
        for name,source in (('87-a399','87a399'),('87-best','87old'))}
    result.update({'293-best':quality['capacity']['u16_old_best'],'294-best':quality['capacity']['rgb24_old_best'],
        '293-max41':quality['capacity']['u16_max41'],'294-max41':quality['capacity']['rgb24_max41']})
    capacities={'87-a399':18579204,'87-best':18715680,'293-best':18715824,'294-best':18715824,
        '293-max41':35673508,'294-max41':52448272}
    for role,value in result.items():
        assert value['model_bytes']==capacities[role]
        assert value['cache']['enabled']==value['domain']['eligible']==value['domain']['cache_enabled']==1
        assert value['domain']['unproven_cells']==0 and value['domain']['reachable_cells']==32768
        assert value['domain']['fast_path_enabled']==value['direct']['enabled']==1
        if role.endswith('max41'):
            wide=value['wide'];u16=role.startswith('293-')
            assert value['palette']['enabled']==0 and value['palette']['palette_size']==613
            assert wide['enabled']==1 and wide['format']==value['direct']['format']==(16 if u16 else 18)
            assert wide['guard_bytes']==4 and wide['id_bytes']==(2 if u16 else 3)
            assert wide['palette_size']==(613 if u16 else 0) and wide['palette_capacity_bytes']==(2452 if u16 else 0)
            assert wide['input_entries']==16777216 and wide['raw_words']==value['direct']['entries']==(8388609 if u16 else 12582913)
            assert wide['table_capacity_bytes']==value['direct']['table_capacity_bytes']==(33554436 if u16 else 50331652)
        else:
            assert value['palette']['enabled']==1 and value['palette']['palette_size']==(230 if role.endswith('a399') else 234)
            assert value['direct']['format']==9 and value['direct']['entries']==4194304 and value['direct']['table_capacity_bytes']==16777216
            if value['wide'] is not None:
                assert value['wide']['enabled']==0 and value['wide']['reason']==1
                assert value['wide']['table_capacity_bytes']==value['wide']['palette_capacity_bytes']==0
        result[role]={key:({name:item for name,item in row.items() if name not in ('prepare_seconds','data_mod_64')}
            if isinstance(row,dict) else row) for key,row in value.items()}
    return result

def expected_pixels(primary,old,models,raw,output):
    # 优先已有实际完整百图SHA；缺失才用独立RGB域oracle导出真实像素流，绝不串接SHA文本。
    full={'a399':old.get('expected_output_sha256',{}).get('a399'),
        'best':old.get('expected_output_sha256',{}).get('old_best')}
    native=list(primary.get('native_100photos_sha256',{}).values())
    if native:
        assert len(set(native))==1;full['max41']=native[0]
    fields={'a399':'a399','best':'best','max41':'candidate'};result={}
    for name,spec in models.items():
        per_image=primary['photos'][fields[name]]['per_image'];assert len(per_image)==100
        expected_first=per_image[0]['prediction_sha256']
        source_pointer='/native_100photos_sha256' if name=='max41' else '/expected_output_sha256/'+('old_best' if name=='best' else name)
        row={'1':expected_first,'100':full.get(name),'first_source':'cinema-current-full-quality-v2/results.json/photos/'+fields[name]+'/per_image/0',
            'full_source_json_pointer':source_pointer,'derived_pixels':False,'per_image_sha256':[r['prediction_sha256'] for r in per_image]}
        if row['100'] is None:
            import numpy as np
            photos=np.memmap(raw,dtype=np.uint8,mode='r',shape=(100,786432,3))
            oracle=np.memmap(spec['oracle'],dtype=np.uint8,mode='r',shape=(1<<24,3));aggregate=hashlib.sha256()
            for index,image in enumerate(photos):
                keys=(image[:,0].astype(np.uint32)<<16)|(image[:,1].astype(np.uint32)<<8)|image[:,2].astype(np.uint32)
                pixels=oracle[keys];actual=hashlib.sha256(pixels).hexdigest()
                assert actual==row['per_image_sha256'][index]
                aggregate.update(pixels)
            row['100']=aggregate.hexdigest();row['derived_pixels']=True
            row['full_source_json_pointer']=None
        assert isinstance(row['100'],str) and len(row['100'])==64
        result[name]=row
    save(output,{'purpose':'冻结前输出期望导出，无native/正式性能','models':result,'raw_source':str(raw),
        'raw_source_sha256':sha(raw),'input_key_order':'Rhigh16 | Gmid8 | Blow0','native_calls':0,'performance_calls':0})
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('V2单版冻结不覆盖')
    quality_path=ROOT/'artifacts/p16-direct-cache2-quality-frozen-v1/frozen.json'
    quality=read(quality_path);quality_result=ROOT/'artifacts/p16-direct-cache2-quality-v1/results.json'
    quality_results=read(quality_result);assert quality_results['passed']
    primary_identity=ROOT/'artifacts/cinema-current-full-quality-v2/identity.json'
    primary_result=ROOT/'artifacts/cinema-current-full-quality-v2/results.json'
    identity=read(primary_identity);primary=read(primary_result)
    old_path=ROOT/'artifacts/p16-direct-sentinel-perf-frozen-v1/plan.json';old=read(old_path)
    old_state_path=ROOT/'artifacts/p16-direct-sentinel-perf-v1/worker0/results.json';old_state=read(old_state_path)
    assert old_state['worker']==0 and old_state['plan_sha256']==sha(old_path)
    representation=expected_states(quality_results,old_state)
    models={'a399':identity['roles']['a399'],'best':quality['models']['old_best'],'max41':quality['models']['max41']}
    for name in ('a399','best'):
        prior=old['models']['a399' if name=='a399' else 'old_best']
        assert all(models[name][key]==prior[key] for key in ('models','sidecars'))
    for spec in models.values():
        assert sha(spec['oracle'])==spec['oracle_sha256']
    raw=ORIGINAL/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
    assert raw.stat().st_size==235929600 and sha(raw)=='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
    expected_file=args.output.parent/'expected-pixels-v2.json'
    expected=expected_pixels(primary,old,models,raw,expected_file)
    libraries={'87':{**old['libraries']['old87'],'revision':87},'293':quality['libraries']['u16'],'294':quality['libraries']['rgb24']}
    roles={name:{'library':name.split('-')[0],'model':'a399' if name=='87-a399' else 'max41' if name.endswith('max41') else 'best'} for name in ROLES}
    dependencies={name:{'path':str(Path('E:/mingw64/bin')/name),'sha256':sha(Path('E:/mingw64/bin')/name)}
        for name in ('libgomp-1.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll')}
    assert dependencies['libgomp-1.dll']['sha256']=='fc7569276d33d23f55f143eb6723821ef2633c96cbb381c0f507b793d9585e88'
    helper=ROOT/'artifacts/p16-omp-affinity-control-build-v2/libp16_omp_affinity.dll'
    assert sha(helper)=='fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f'
    sources=dict(quality['sources_sha256'])
    own=['freeze_direct_cache2_perf_v2.py','p16_cache2_perf_support_v2.py','run_direct_cache2_perf_v2.py','audit_direct_cache2_perf_v2.py']
    for name in own:sources['scripts/'+name]=sha(ROOT/'scripts'/name)
    protocol=ROOT/'experiments/p16-direct-cache2-performance-protocol-v2.md'
    sources[str(protocol.relative_to(ROOT))]=sha(protocol)
    inputs={str(path):sha(path) for path in (quality_path,quality_result,primary_identity,primary_result,old_path,old_state_path,raw,helper,expected_file,Path(sys.executable))}
    for name,value in quality['inputs_sha256'].items():assert sha(name)==value;inputs[name]=value
    for row in libraries.values():assert sha(row['path'])==row['sha256'];inputs[row['path']]=row['sha256']
    for row in dependencies.values():inputs[row['path']]=row['sha256']
    for spec in models.values():
        for path in spec['models']+[p for p in spec['sidecars'] if p]+[spec['oracle']]:inputs[str(path)]=sha(path)
    for name,value in sources.items():assert sha(ROOT/name)==value,name
    modes=[['inplace',1],['outplace',4],['inplace',4],['outplace',1]]
    pair_order=list(range(9));role_rot=ROLES[2:]+ROLES[:2];pair_rot=pair_order[3:]+pair_order[:3]
    plan={'schema':'p16_direct_cache2_perf_v2','purpose':'U主/P辅分别完整授档，辅助不能救主profile',
        'expected_python':quality['environment']['python'],'expected_numpy':quality['environment']['packages']['numpy'],
        'sources_sha256':sources,'inputs_sha256':inputs,'libraries':libraries,'models':models,'roles':roles,'expected_states':representation,
        'role_names':ROLES,'pairs':[{'id':i,'candidate':a,'denominator':b,'main':main} for i,(a,b,main) in enumerate(PAIRS)],
        'profiles':['U','P'],'workers':4,'source':str(raw),'source_sha256':inputs[str(raw)],'expected':expected,
        'helper':{'path':str(helper),'sha256':sha(helper)},'gcc_dependencies':dependencies,'allowed_cpus':[0,2,4,6],
        'dependency_load_order':['libwinpthread-1.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libgomp-1.dll'],
        'required_environment':{'PYTHONUTF8':'1','OMP_NUM_THREADS':'4','OMP_DYNAMIC':'FALSE','OMP_THREAD_LIMIT':'4',
            'OMP_WAIT_POLICY':'PASSIVE','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'},
        'role_orders':[ROLES,list(reversed(ROLES)),role_rot,list(reversed(role_rot))],
        'pair_orders':[pair_order,list(reversed(pair_order)),pair_rot,list(reversed(pair_rot))],
        'mode_orders':[modes,list(reversed(modes)),modes[2:]+modes[:2],list(reversed(modes[2:]+modes[:2]))],
        'palindromes':[['A','B','B','A'],['B','A','A','B'],['B','A','A','B'],['A','B','B','A']],
        'cold_images':[1,100],'cold_repeats':5,'warmup':2,'timed_repeats':3,'AA_bounds':[.85,1.15],'tiers':[100,90,80,70,60,50],
        'per_profile_expected':{'hot_cells':144,'hot_sha':864,'cold_sha':480,'sha':1344,'hot_apply':2304,'cold_apply':480,'apply':2784,'rss':6},
        'per_worker_expected':{'hot_cells':36,'hot_sha':216,'cold_sha':120,'sha':336,'apply':696,'hot_create':6,'cold_create':120},
        'scope':'热六句柄关闭后才冷；nativecreate→bench_to continuouswall不夹元数据/hash；任何helper/native/identity失败保留STOP，AA失效不缩轮；U/P不可取较优拼资格。'}
    save(args.output,plan)
    print(json.dumps({'plan_sha256':sha(args.output),'sources':len(sources),'inputs':len(inputs),'performance_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
