"""只分析获证坐标差的实际循环与原对象保留，不调用像素/性能。"""
import argparse,json,re,subprocess
from pathlib import Path
from inspect_skylake_avx2 import digest,read,save,functions,loops
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('plan','build','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--objdump',required=True);p.add_argument('--mca',required=True);args=p.parse_args()
 plan=read(args.plan);build=read(args.build/'build.json')
 assert digest(args.plan)==build['plan_sha256']
 for name,sha in plan['source_sha256'].items():assert digest(ROOT/name)==sha,name
 out=args.output;out.mkdir(exist_ok=False)
 def obj(target,folder):
  paths=[x for x in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in x.parts and
    (x.parent.name==target+'.dir' if folder=='local' else folder in x.parts)]
  if len(paths)!=1:raise ValueError('对象定位不唯一')
  return paths[0]
 old={}
 for folder in ('skylake-domain-isolated-runtime','skylake-suffix-cache-runtime'):
  a=obj('jshc_skylake_reference',folder);b=obj('jshc_skylake_domain_delta',folder)
  assert a.read_bytes()==b.read_bytes();old[folder]=digest(a)
 variants={};commands=[]
 for role,path,gathers in [('reference',obj('jshc_skylake_reference','skylake-domain-isolated-runtime'),18),('candidate',obj('jshc_skylake_domain_delta','local'),15)]:
  cmd=[args.objdump,'-d','-C',str(path)];commands.append(cmd);asm=subprocess.check_output(cmd);(out/f'{role}.asm').write_bytes(asm)
  candidates=[x for f in functions(asm.decode('utf-8')) for x in loops(f) if x['gathers']==gathers and x['calls']==0 and x['branches']==1]
  if len(candidates)!=1:raise ValueError('实际平坦循环不是唯一')
  hot=candidates[0];text='\n'.join(op+' .Lloop' if op.startswith('j') else op+' '+operand.split('#')[0].strip() for _,op,operand in hot['seq'])
  source=out/f'{role}-hot.s';source.write_text('.text\n.Lloop:\n'+text+'\n',encoding='ascii')
  cmd=[args.mca,'-mcpu=skylake','-iterations=100','-resource-pressure',str(source)];commands.append(cmd);proc=subprocess.run(cmd,capture_output=True)
  (out/f'{role}-mca.stdout.log').write_bytes(proc.stdout);(out/f'{role}-mca.stderr.log').write_bytes(proc.stderr)
  if proc.returncode:raise ValueError('MCA失败')
  text=proc.stdout.decode('utf-8');mca={key:float(re.search('^'+key+r':\s*([0-9.]+)',text,re.M)[1]) for key in ('Total Cycles','Total uOps','Block RThroughput')}
  variants[role]={'object':str(path),'sha256':digest(path),'hot':{k:v for k,v in hot.items() if k!='seq'},'mca':mca}
 r,c=variants['reference'],variants['candidate'];gates={'cycles':c['mca']['Total Cycles']<=.97*r['mca']['Total Cycles'],'throughput':c['mca']['Block RThroughput']<=1.03*r['mca']['Block RThroughput'],'rsp':c['hot']['rsp_operands']<=1.1*r['hot']['rsp_operands']}
 result={'pass':all(gates.values()),'gates':gates,'variants':variants,'original_objects':old,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),'script_sha256':digest(__file__),'commands':commands,'pixel_calls':0,'performance_calls':0}
 save(out/'results.json',result);print(json.dumps({'pass':result['pass'],'gates':gates,'variants':{k:{'instructions':v['hot']['instructions'],'rsp':v['hot']['rsp_operands'],'gathers':v['hot']['gathers'],'mca':v['mca']} for k,v in variants.items()}},ensure_ascii=False))
if __name__=='__main__':main()
