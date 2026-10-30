"""78独立静态审计：独立解析四个实际区段，逐次验证掩码与ID依赖，不加载候选。"""
import hashlib,json,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BUILD=ROOT/'artifacts/skylake-andn-split-linux-build-v1'
OBJECTS=BUILD/'CMakeFiles/jshc_skylake_andn_split.dir'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(r):
 n=r.lstrip('%');a=dict(eax='rax',ebx='rbx',ecx='rcx',edx='rdx',esi='rsi',edi='rdi',ebp='rbp',esp='rsp')
 return a.get(n,re.sub(r'^(r\d+)d$',r'\1',n))
def args(t):return re.split(r',\s*(?![^()]*\))',t)
def parse(p):
 rows=[];func=None;section=None
 for line in p.read_text(encoding='utf-8').splitlines():
  z=re.match(r'Disassembly of section (.+):',line)
  if z:section=z[1]
  f=re.match(r'^([0-9a-f]+) <(.+)>:$',line)
  if f:func=f[2]
  m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9]*)\s*(.*)$',line)
  if m:rows.append(dict(a=int(m[1],16),raw=bytes.fromhex(m[2]),op=m[3],arg=m[4].split('#')[0].strip(),function=func,section=section))
 return rows
def texts(p):
 d=p.read_bytes();assert d[:6]==b'\x7fELF\x02\x01'
 sh=struct.unpack_from('<Q',d,40)[0];sz,num,ni=struct.unpack_from('<HHH',d,58)
 ss=[struct.unpack_from('<IIQQQQIIQQ',d,sh+i*sz) for i in range(num)]
 ns=ss[ni];names=d[ns[4]:ns[4]+ns[5]]
 return {names[s[0]:].split(b'\0',1)[0].decode():d[s[4]:s[4]+s[5]] for s in ss}
def forbidden(o,allow_call=False,allow_andn=False):
 b=o['raw'];i=0
 while i<len(b) and (b[i] in (0x66,0x67,0x2e,0x36,0x3e,0x26,0x64,0x65,0xf2,0xf3,0xf0) or 0x40<=b[i]<=0x4f):i+=1
 return ((not allow_call and o['op'].startswith('call')) or 'gather' in o['op'] or
  o['op'] in ('pext','pdep','mulx','bzhi','rorx','shlx','shrx','sarx','bextr','blsi','blsr','blsmsk') or (o['op']=='andn' and not allow_andn) or
  bool(re.search(r'%(?:zmm\d+|k[0-7])\b|%[xy]mm(?:1[6-9]|2\d|3[01])\b|\{',o['arg'])) or i<len(b) and b[i]==0x62)
def compact(o):return {'address':hex(o['a']),'instruction':o['op']+' '+o['arg']}
def main():
 assert not (HERE/'independent-audit.json').exists()
 runtime=HERE/'dispatcher.asm.txt'
 if not runtime.exists():
  t=subprocess.check_output(['E:/mingw64/bin/objdump.exe','-d','--insn-width=15','-C',str(OBJECTS/'channel_runtime.cpp.o')],text=True)
  with runtime.open('x',encoding='utf-8') as f:f.write(t)
 objects=[];regions=[]
 for role,rel in [('linear','channel_avx2.cpp.o'),('andn_inplace','andn_inplace/channel_avx2.cpp.o'),('andn_outplace','andn_outplace/channel_avx2.cpp.o'),('dispatcher','channel_runtime.cpp.o')]:
  asm=HERE/(role+'.asm.txt');obj=OBJECTS/rel;ops=parse(asm);sec=texts(obj)
  byteok=all(sec[o['section']][o['a']:o['a']+len(o['raw'])]==o['raw'] for o in ops)
  bad=[compact(o) for o in ops if forbidden(o,role=='dispatcher',role.startswith('andn'))]
  objects.append(dict(role=role,object_sha256=sha(obj),asm_sha256=sha(asm),instruction_bytes_match=byteok,forbidden=bad))
  if not role.startswith('andn'):continue
  spec=[('inplace',64,0xf0,0x6dd,321,True),('inplace',32,0x718,0xa10,170,True)] if role=='andn_inplace' else [('outplace',64,0xf8,0x6db,322,True),('outplace',32,0x731,0xa1d,171,False)]
  assert len({o['function'] for o in ops})==1
  for mode,n,lo,hi,ref,loop in spec:
   body=[o for o in ops if lo<=o['a']<=hi];an=[o for o in body if o['op']=='andn']
   assert len(an)==n
   mask_regs={canon(args(o['arg'])[1]) for o in an}
   assert len(mask_regs)==1
   mask=next(iter(mask_regs))
   definitions=[o for o in ops if o['a']<lo and o['op']=='mov' and len(args(o['arg']))==2 and args(o['arg'])[0]=='$0xff000000' and canon(args(o['arg'])[-1])==mask]
   assert definitions
   definition=definitions[-1];value=0xff000000;uses=[];writes=[];valid_operands=[]
   ids=[];versions={};palettes=[];stack=[]
   frame=any(o['a']<lo and o['op']=='mov' and o['arg']=='%rsp,%rbp' for o in ops)
   for o in ops:
    if not definition['a']<o['a']<=hi:continue
    p=args(o['arg'])
    if o['op']=='andn':
     assert canon(p[1])==mask
     uses.append(dict(address=hex(o['a']),mask_before=value,correct=value==0xff000000))
     valid_operands.append(bool(re.fullmatch(r'(?:-?0x[0-9a-f]+)?\(%r[a-z0-9]+\)',p[0])) and all(re.fullmatch(r'%(?:e[a-z]{2}|r(?:[89]|1[0-5])d)',r) for r in p[1:]) and o['raw'][0]==0xc4 and not(o['raw'][2]&0x80) and o['raw'][3]==0xf2)
    if p and p[-1].startswith('%') and canon(p[-1])==mask and o['op'] not in ('cmp','test','push') and not o['op'].startswith('j'):
     writes.append(o);value=0xff000000 if o['op']=='mov' and p[0]=='$0xff000000' else None
   for o in body:
    p=args(o['arg'])
    if '%rsp' in o['arg'] or frame and '%rbp' in o['arg']:stack.append(compact(o))
    if o['op']=='movzbl' and re.fullmatch(r'\(%rdi,%[a-z0-9]+,1\)',p[0]):versions[canon(p[-1])]=len(ids);ids.append(o['a'])
    m=re.search(r'\(%rsi,(%[a-z0-9]+),4\)',o['arg'])
    if m:
     v=versions.get(canon(m[1]));palettes.append(dict(address=hex(o['a']),id_version=v,completed_ids=len(ids),ready=v is not None and len(ids)>=v//4*4+4))
   stores=[o for o in body if o['op'].startswith('vmov') and '(' in args(o['arg'])[-1]]
   dead_ok=not loop and all(o['op']=='andn' and o['a']==an[-1]['a'] for o in writes) and not any(o['op']=='andn' and o['a']>hi for o in ops)
   selfmoves=[compact(o) for o in body if o['op']=='mov' and len(args(o['arg']))==2 and args(o['arg'])[0]==args(o['arg'])[1]]
   check=dict(complete_width=len(an)==n and len(ids)==n and len(palettes)==n,mem32_andn=all(valid_operands),
              mask_valid_at_each_use=all(u['correct'] for u in uses),mask_outside_with_dead_last_use=not writes or dead_ok,
              no_stack=not stack,no_extra_zext=not selfmoves,four_id=all(x['ready'] for x in palettes),
              fewer_instructions=len(body)<ref,all_palette_before_store=bool(stores) and max(int(x['address'],16) for x in palettes)<stores[0]['a'])
   regions.append(dict(mode=mode,width=n,start=hex(lo),end=hex(hi),kind='backedge_loop' if loop else 'at_most_once_straightline',
      instructions=len(body),reference_instructions=ref,andn_count=len(an),id_count=len(ids),palette_count=len(palettes),
      mask_initializer=compact(definition),mask_uses=uses,mask_writes=[compact(o) for o in writes],dead_last_use_accepted=bool(writes) and dead_ok,
      stack_references=stack,palette_dependencies=palettes,self_moves=selfmoves,checks=check))
 planpath=ROOT/'experiments/skylake-andn-split-v1.json';plan=json.loads(planpath.read_text(encoding='utf-8'))
 mismatch=[k for k,v in plan['source_sha256'].items() if sha(ROOT/k)!=v]
 commands=json.loads((BUILD/'compile_commands.json').read_text(encoding='utf-8'));flags=[]
 for e in commands:
  need=any('/skylake-andn-split-runtime/'+x+'/' in e['file'] for x in ('andn_inplace','andn_outplace'))
  has=bool(re.search(r'(?:^|\s)-mbmi(?:\s|$)',e['command']))
  required=all(f in e['command'].split() for f in ('-mavx2','-mtune=skylake','-ffp-contract=off')) if e['file'].endswith('/channel_avx2.cpp') else True
  flags.append(dict(file=e['file'],bmi_expected=need,bmi_actual=has,pixel_options=required,correct=need==has and required))
 source=ROOT/'experiments/skylake-andn-split-runtime'
 def read(p):return p.read_text(encoding='utf-8')
 pin=read(ROOT/'experiments/skylake-andn-zext-runtime/andn/channel_avx2.cpp').replace('andn_zext','andn_split')
 pout=read(ROOT/'experiments/skylake-andn-cursor-runtime/andn/channel_avx2.cpp').replace('andn_cursor','andn_split')
 exact=dict(inplace=read(source/'andn_inplace/channel_avx2.cpp')==''.join(l for l in pin.splitlines(keepends=True) if not l.startswith('void avx2_chain_andn_split_to(')),
  outplace=read(source/'andn_outplace/channel_avx2.cpp')==''.join(l for l in pout.splitlines(keepends=True) if not l.startswith('void avx2_chain_andn_split(')),
  linear_sha=sha(source/'channel_avx2.cpp')=='e0cb7f0539fdb5d7f35645978b1b2504dbf7e60c57e21acf8ae361cf1c343a30')
 passed=not mismatch and all(exact.values()) and all(o['instruction_bytes_match'] and not o['forbidden'] for o in objects) and all(f['correct'] for f in flags) and sum(f['bmi_actual'] for f in flags)==2 and len(regions)==4 and all(all(r['checks'].values()) for r in regions)
 result=dict(purpose=__doc__,accepted=passed,script_sha256=sha(__file__),plan_sha256=sha(planpath),build_sha256=sha(BUILD/'build.json'),
  first_results_sha256=sha(HERE/'results.json'),formal_results_sha256=sha(HERE/'results-v2.json'),objects=objects,sections=regions,compile_options=flags,source_hash_mismatches=mismatch,source_exact_comparison=exact,
  tail_guard='分离32入口0x722 cmp $0x27,%r13 / 0x726 jbe跳过；最后一次ANDN为0x95d，掩码0x72c外提，此后整个唯一入口无ANDN。64退出后remaining<72，故32最多一次。原地仍为原有循环。',
  stack_scope='四个热区无rsp或真实frame-pointer引用；函数序言/尾部可能保存callee-saved寄存器及循环外状态，不把这些等同热区spill。分离64退出0x6e1/0x6e6/0x6eb恢复三项循环外状态，已如实保留，不隐瞒为全函数无栈。',
  correctness_limit='源级精确24B尾部和标量读取保持；静态通过不等于完整RGB8或有限边界通过，仍需主流程独立验证。',
  decision='四个实际可达宽区段与全局静态门槛通过，可由主流程安排完整正确性验证' if passed else '独立审计失败，停止像素与性能',pixel_calls=0,performance_calls=0,candidate_library_loads=0,compiler_calls=0)
 with (HERE/'independent-audit.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(dict(accepted=passed,regions=[{k:r[k] for k in ('mode','width','instructions','checks')} for r in regions],sha256=sha(HERE/'independent-audit.json')),ensure_ascii=False))
if __name__=='__main__':main()
