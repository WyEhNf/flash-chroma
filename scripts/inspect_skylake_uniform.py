"""枚举同色后缀固定循环的全部简单控制流路径并建模；不执行像素或性能基准。"""
from __future__ import annotations
import argparse
import collections
import concurrent.futures as cf
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from inspect_skylake_avx2 import ROOT,read,save,digest,functions
from inspect_skylake_preweight import linear_loops


def cycles(function):
    instructions=function['instructions'];lookup={x[0]:x for x in instructions};leaders={instructions[0][0]}
    for i,(at,op,operands) in enumerate(instructions):
        if op.startswith(('j','ret','call')):
            if i+1<len(instructions):leaders.add(instructions[i+1][0])
        if op.startswith('j'):
            m=re.match(r'([0-9a-f]+)\s+<',operands)
            if not m:raise ValueError('不支持间接跳转，停止静态枚举')
            if int(m[1],16) in lookup:leaders.add(int(m[1],16))
    blocks={};current=None
    for instruction in instructions:
        if instruction[0] in leaders:current=instruction[0];blocks[current]=[]
        blocks[current].append(instruction)
    starts=list(blocks);edges={}
    for i,start in enumerate(starts):
        _,op,operands=blocks[start][-1];nexts=[]
        if op.startswith('j'):
            target=int(re.match(r'([0-9a-f]+)',operands)[1],16)
            if target in blocks:nexts.append(target)
        if not op.startswith('ret') and op!='jmp' and i+1<len(starts):nexts.append(starts[i+1])
        edges[start]=nexts
    index={};low={};stack=[];active=set();components=[]
    def visit(v):
        index[v]=low[v]=len(index);stack.append(v);active.add(v)
        for w in edges[v]:
            if w not in index:visit(w);low[v]=min(low[v],low[w])
            elif w in active:low[v]=min(low[v],index[w])
        if low[v]==index[v]:
            group=set()
            while True:
                w=stack.pop();active.remove(w);group.add(w)
                if w==v:break
            components.append(group)
    for v in blocks:
        if v not in index:visit(v)
    groups=[s for s in components if len(s)>1 and any(op.startswith('vpgather') for v in s for _,op,_ in blocks[v])]
    if len(groups)!=1:raise ValueError('固定四级函数应只有一个含gather的外层循环')
    group=groups[0];entries={w for v in blocks if v not in group for w in edges[v] if w in group}
    # 编译器可把首轮入口旋转到环内多个位置；选移除后图无环的反馈锚点，不能漏掉任一路径。
    anchors=[]
    for cut in sorted(group):
        rest=group-{cut};degree={v:0 for v in rest}
        for v in rest:
            for w in edges[v]:
                if w in rest:degree[w]+=1
        queue=[v for v in rest if degree[v]==0];removed=0
        while queue:
            v=queue.pop();removed+=1
            for w in edges[v]:
                if w in rest:
                    degree[w]-=1
                    if degree[w]==0:queue.append(w)
        if removed==len(rest):anchors.append(cut)
    if not anchors:raise ValueError('没有覆盖全部环的单一反馈锚点，停止而不截取部分路径')
    vector_anchors=[v for v in anchors if any(op.startswith('vpgather') for _,op,_ in blocks[v])]
    header=min(vector_anchors or anchors);paths=[];steps=0
    def walk(v,path,seen):
        nonlocal steps
        steps+=1
        if steps>100000 or len(paths)>1024:raise ValueError('固定枚举预算超限，不自动扩大')
        if v==header and path:paths.append([i for k in path for i in blocks[k]]);return
        if v not in group or v in seen:return
        if any(op.startswith('call') for _,op,_ in blocks[v]):raise ValueError('循环内出现外部调用')
        for w in edges[v]:walk(w,path+[v],seen|{v})
    walk(header,[],set())
    return paths,{'blocks':len(blocks),'loop_blocks':len(group),'external_entries':[hex(v) for v in sorted(entries)],
        'header':hex(header),'feedback_anchor_count':len(anchors),'enumeration_steps':steps}


def measure_path(args,out,name,seq):
    labels={a:'.Li'+str(i) for i,(a,_,_) in enumerate(seq)};labels[seq[0][0]]='.Lloop';body=['.text']
    for at,op,operands in seq:
        body.append(labels[at]+':')
        if op.startswith('j'):
            target=int(re.match(r'([0-9a-f]+)',operands)[1],16);body.append(op+' '+labels.get(target,'.Loutside'))
        else:body.append(op+' '+operands.split('#')[0].strip())
    body.append('.Loutside:');p=out/(name+'.s');p.write_text('\n'.join(body)+'\n',encoding='ascii')
    command=[args.mca,'-mcpu=skylake','-iterations=100','-resource-pressure',str(p)];r=subprocess.run(command,capture_output=True)
    (out/(name+'.stdout.log')).write_bytes(r.stdout);(out/(name+'.stderr.log')).write_bytes(r.stderr)
    if r.returncode:raise ValueError('MCA失败，保留全部原始日志：'+name)
    text=r.stdout.decode();h=collections.Counter(x[1] for x in seq)
    return {'name':name,'instructions':len(seq),'gathers':sum(v for k,v in h.items() if k.startswith('vpgather')),
        'branches':sum(x[1].startswith('j') for x in seq),'rsp_operands':sum('%rsp' in x[2] for x in seq),
        'imul':sum(v for k,v in h.items() if k.startswith('imul')),'vpmulld':h['vpmulld'],
        'gpr_indexed_reads':sum(not op.startswith(('vpgather','lea')) and bool(re.search(r'\([^)]*,%r[a-z0-9]+,4\)',operands)) for _,op,operands in seq),
        'path_addresses':[hex(x[0]) for x in seq],
        'mca':{k:float(re.search(r'^'+re.escape(k)+r':\s*([0-9.]+)',text,re.M)[1]) for k in ('Total Cycles','Total uOps','Block RThroughput')},'command':command}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('plan','build','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--objdump',required=True);p.add_argument('--mca',required=True);args=p.parse_args();out=args.output.resolve()
    plan=read(args.plan);build=read(args.build/'build.json')
    if out.exists() or build['plan_sha256']!=digest(args.plan) or build['source_sha256']!=plan['source_sha256']:raise ValueError('输出/冻结构建不符')
    for n,s in plan['source_sha256'].items():
        if digest(ROOT/n)!=s:raise ValueError('冻结源变化：'+n)
    out.mkdir();jobs=[];inventory={};families={}
    for role,target in zip(('reference','candidate'),plan['cmake_targets']):
        objs=[x for x in args.build.rglob('channel_avx2.cpp.obj') if target+'.dir' in x.parts]
        if len(objs)!=1:raise ValueError('对象不唯一')
        raw=subprocess.check_output([args.objdump,'-d','-C',str(objs[0])]);(out/(role+'.asm')).write_bytes(raw)
        fs=functions(raw.decode());inventory[role]={'object_sha256':digest(objs[0]),'functions':{f['function']:len(f['instructions']) for f in fs}}
        if role=='reference':
            ls=[l for f in fs for l in linear_loops(f)]
            for gathers in (35,38):
                found=[l for l in ls if l['gathers']==gathers and l['calls']==0 and l['branches']==1]
                if len(found)!=1:raise ValueError('参考固定家族不唯一')
                jobs.append((f'reference-{gathers}',found[0]['seq']))
        else:
            for delta,gathers,prefix in ((True,35,14),(False,38,17)):
                found=[f for f in fs if 'fixed_four<'+str(delta).lower()+'>(' in f['function']]
                if len(found)!=1:raise ValueError('私有固定函数不唯一')
                paths,cfg=cycles(found[0]);counts=collections.Counter(sum(op.startswith('vpgather') for _,op,_ in seq) for seq in paths)
                if counts[gathers]!=1 or not counts[prefix] or set(counts)!={gathers,prefix}:raise ValueError('普通/同色路径结构不符')
                families[str(gathers)]={'cfg':cfg,'path_counts_by_gather':dict(counts)}
                for i,seq in enumerate(paths):jobs.append((f'candidate-{gathers}-{i}',seq))
    print('静态路径枚举完成，共',len(jobs),'条MCA任务；没有原生像素或性能调用。',flush=True)
    records=[]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(lambda job:measure_path(args,out,*job),jobs):records.append(r)
    for n,s in plan['source_sha256'].items():
        if digest(ROOT/n)!=s:raise ValueError('静态分析中源变化')
    save(out/'results.json',{'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'source_sha256':digest(Path(__file__)),'inventory':inventory,'families':families,'paths':records,
        'mca_calls':len(records),'project_native_calls':0,'performance_calls':0,
        'scope':'完整CFG简单路径的静态模型；含不可行比较组合的保守路径，不建模真实缓存/GDS/分支预测/分派序言，不作实测结论'})
    with zipfile.ZipFile(out/'all-paths.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.iterdir()):
            if f.suffix in ('.s','.log'):z.write(f,f.name)
    print('全部静态路径建模完成：',len(records),flush=True)


if __name__=='__main__':main()
