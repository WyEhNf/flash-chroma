"""仅在审查目录构造失配目录，验证部署入口是否重新绑定精度与稳定性；不修改原件。"""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import p16_frontier as f
import run_flash_chroma as r
import flash_chroma_support as s

folder=ROOT/'report/data/p16-header-performance-20261028'
catalog=json.loads((folder/'catalog.json').read_text(encoding='utf8'))
raw=json.loads((folder/'results.json').read_text(encoding='utf8'))
candidate=next(c for c in catalog['candidates'] if c['id']=='default-direct_u8-avx2-1t')
original=next(v for v in raw['records'] if v['id']==candidate['id'])
assert original['aa_pass'] is False
changed=copy.deepcopy(candidate)
changed['verified']['time_stable']=True
changed['metrics']['mean_error']=0.01
changed['metrics']['worst_image_mean']=0.02
changed['metrics']['batch_ms']=0.001
changed['evidence']=str(folder/'results.json')+'#'+candidate['id']
fixture=copy.deepcopy(catalog);fixture['candidates']=[changed]
for model in fixture['models'].values():model['manifest']=str((folder/model['manifest']).resolve())
output=ROOT/'artifacts/pr95-review/binding-repro';output.mkdir(exist_ok=True)
f.save_new(output/'catalog.json',fixture)
selection=f.tradeoff(fixture,context=changed['context'],goal='fastest',max_error=0.03)
selection['catalog_sha256']=f.digest(output/'catalog.json')
f.save_new(output/'selection.json',selection)
bound,selected,_,_=r.bind_selection(output/'catalog.json',output/'selection.json')
_,model=r.bind_model(bound,selected,output/'catalog.json')
evidence,identity=r.bind_evidence(selected,bound['contexts'][selected['context']],output/'catalog.json')
result={'reproduced':selection['status']=='ok','actual_aa_pass':original['aa_pass'],
        'original_metrics':candidate['metrics'],'modified_metrics_accepted':selected['metrics'],
        'original_stability':candidate['verified']['time_stable'],'modified_stability_accepted':selected['verified']['time_stable'],
        'binding_stages_passed':['bind_selection','bind_model','bind_evidence'],
        'raw_evidence':identity,'scope':'仅元数据绑定复现，原始报告未修改；不声称现有档案造假，不执行错误目录的图片处理。'}
s.write_json(output/'result.json',result)
print(json.dumps(result,ensure_ascii=False,indent=2))
