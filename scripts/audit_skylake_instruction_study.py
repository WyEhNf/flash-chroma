"""标准库独立核对四项静态档案的身份与拒绝门槛；不加载原生库或调用像素/性能。"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,default=ROOT/'report/data/skylake-instruction-study-v1')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise ValueError('不得覆盖既有核对回执')
    manifest=json.loads((args.archive/'manifest.json').read_text(encoding='utf-8'))
    summary=json.loads((args.archive/'summary.json').read_text(encoding='utf-8'))
    for name,spec in manifest['files'].items():
        data=(args.archive/name).read_bytes()
        if sha(data)!=spec['sha256'] or len(data)!=spec['bytes']:raise ValueError('档案不同：'+name)
    records=[]
    for old in summary['records']:
        name=old['name']
        with zipfile.ZipFile(args.archive/f'{name}.zip') as z:
            def read(key):return json.loads(z.read(key))
            plan=read('plan.json');build=read('build/build.json');static=read('static/results.json')
            if sha(z.read('plan.json'))!=old['plan_sha256'] or build['plan_sha256']!=old['plan_sha256']:
                raise ValueError('计划身份不同')
            if sha(z.read('build/build.json'))!=old['build_sha256'] or static['build_sha256']!=old['build_sha256']:
                raise ValueError('构建身份不同')
            if sha(z.read('static/results.json'))!=old['static_sha256']:
                raise ValueError('静态回执身份不同')
            if sha(z.read('analysis-script.py'))!=old['analysis_script_sha256']:
                raise ValueError('实际分析脚本不同')
            with zipfile.ZipFile(io.BytesIO(z.read('build/measured-source.zip'))) as sources:
                for file,digest in plan['source_sha256'].items():
                    if sha(sources.read(file))!=digest:raise ValueError('原字节源码身份不同：'+file)
            variants=static['variants']
            if name in {'geometry','evex256'}:
                family={'35':{role:value for role,value in variants.items()}}
            else:
                family={count:{role:v['families'][count] for role,v in variants.items()} for count in ('35','38')}
            recomputed={}
            for count,roles in family.items():
                for role,value in roles.items():
                    log=z.read('static/'+(f'{role}-mca.stdout.log' if name in {'geometry','evex256'} else f'{role}-{count}-mca.stdout.log')).decode('utf-8')
                    for key,expected in value['mca'].items():
                        actual=float(re.search('^'+key+r':\s*([0-9.]+)',log,re.M)[1])
                        if actual!=expected:raise ValueError('原始MCA日志不能复现JSON')
                ref,cand=roles['reference'],roles['candidate']
                rh=ref.get('selected',ref.get('hot'));ch=cand.get('selected',cand.get('hot'))
                cycle_limit=.95 if name=='evex256' else .97
                stack_limit=1.1 if name=='geometry' else 1.
                recomputed[count]={'cycle_pass':cand['mca']['Total Cycles']<=cycle_limit*ref['mca']['Total Cycles'],
                    'stack_pass':ch['rsp_operands']<=stack_limit*rh['rsp_operands'],
                    'cycle_ratio':cand['mca']['Total Cycles']/ref['mca']['Total Cycles']}
                if rh['gathers']!=int(count) or ch['gathers']!=int(count) or rh['calls'] or ch['calls']:
                    raise ValueError('家族gather或调用数不同')
            accepted=all(x['cycle_pass'] and x['stack_pass'] for x in recomputed.values())
            if accepted or old['accepted_static']:raise ValueError('原拒绝结论不能复现')
            records.append({'name':name,'pass':True,'accepted_static':accepted,'families':recomputed,
                'checked_sources':len(plan['source_sha256'])})
    result={'purpose':__doc__,'pass':True,'records':records,'manifest_files':len(manifest['files']),
        'numerical_calls':0,'performance_calls':0,'script_sha256':sha(Path(__file__).read_bytes())}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'pass':True,'rejected_candidates':len(records),'manifest_files':len(manifest['files']),
        'checked_sources':sum(x['checked_sources'] for x in records),'numerical_calls':0,'performance_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
