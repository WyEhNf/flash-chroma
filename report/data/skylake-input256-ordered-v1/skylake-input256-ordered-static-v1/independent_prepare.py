"""从82独立解析器准备83审计身份，保留分组和字节标签门槛，不执行候选。"""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
source=ROOT/'artifacts/skylake-input256-deferred-static-v1/independent_audit.py'
target=HERE/'independent_audit.py'
assert not target.exists(), '不覆盖已准备的独立审计器'
text=source.read_text(encoding='utf-8')
text=text.replace('82独立静态审计','83独立静态审计')
text=text.replace('skylake-input256-deferred','skylake-input256-ordered')
text=text.replace('jshc_skylake_input256_deferred','jshc_skylake_input256_ordered')
text=text.replace('input256_deferred','input256_ordered')
text=text.replace('deferred_inplace','ordered_inplace')
text=text.replace("'deferred'","'ordered'")
text=text.replace("replace('return 82;','return 81;')","replace('return 83;','return 81;')")
marker="    dispatch={'effective_workers':"
assert text.count(marker)==1
addition='''    old82=ROOT/'experiments/skylake-input256-deferred-runtime/deferred_inplace/channel_avx2.cpp'
    added='    // 阻止第二组输入被编译器前移到首行两次NT之间；这不是硬件栅栏。\\n    asm volatile("" : : : "memory");\\n'
    exact['only_memory_barrier_after82']=tu.count(added)==1 and tu.replace(added,'').replace('avx2_chain_input256_ordered_mt','avx2_chain_input256_deferred_mt')==read(old82)
    exact['three_result_barrier_retained']='asm volatile("" : : "x"(s0),"x"(s1),"x"(pending) : "memory");' in tu
    exact['memory_barrier_count']=tu.count('asm volatile')==4
'''
text=text.replace(marker,addition+marker)
with target.open('x',encoding='utf-8') as f:f.write(text)
print('独立审计器已准备：'+str(target.relative_to(ROOT)))
print('源解析器SHA256：'+hashlib.sha256(source.read_bytes()).hexdigest())
print('新解析器SHA256：'+hashlib.sha256(target.read_bytes()).hexdigest())
