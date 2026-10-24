"""保留失败290全部原件，单独派生291：去除noinline的256bit按值返回。"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/p16-direct-sentinel-runtime'
NEW=ROOT/'experiments/p16-direct-sentinel-runtime-v2'
FROZEN=ROOT/'artifacts/p16-direct-sentinel-v2-source-v1'
GENERATED=ROOT/'artifacts/p16-direct-sentinel-v2-generated-v1.json'

def sha(data):return hashlib.sha256(data).hexdigest()

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('预期唯一修订不符：'+old[:80])
    return text.replace(old,new,1)

HELPER='''#pragma once
#include "direct_sentinel.hpp"
#include <immintrin.h>

namespace jshc_channel {
namespace {
// Windows x64的外部栈边界仅保证16B。跨noinline调用只传显式输出指针，禁止256bit按值返回。
inline __attribute__((noinline)) void sentinel_slow_eight_words(const DirectSentinelView& context,const uint8_t* source,uint32_t* words) noexcept {
  alignas(32) uint8_t rgb[24];std::memcpy(rgb,source,24);
  avx2_chain_cached(context.chain,context.cache,rgb,8);
  for(size_t i=0;i<8;++i)words[i]=uint32_t(rgb[3*i])|(uint32_t(rgb[3*i+1])<<8)|(uint32_t(rgb[3*i+2])<<16);
}
inline __attribute__((always_inline)) __m256i sentinel_slow_eight(const DirectSentinelView& context,const uint8_t* source) noexcept {
  uint32_t words[8];sentinel_slow_eight_words(context,source,words);
  return _mm256_loadu_si256(reinterpret_cast<const __m256i*>(words));
}
inline __attribute__((always_inline)) bool sentinel_any(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h) noexcept {
  return a==255 || b==255 || c==255 || d==255 || e==255 || f==255 || g==255 || h==255;
}
}
}
'''

def main():
    if NEW.exists() or FROZEN.exists() or GENERATED.exists():raise FileExistsError('不覆盖291派生源或证据')
    frozen_path=ROOT/'artifacts/p16-direct-sentinel-build-frozen-v1/frozen.json'
    previous=json.loads(frozen_path.read_text(encoding='utf-8'))
    for name,row in previous['sources'].items():
        if sha((ROOT/name).read_bytes())!=row['sha256']:raise ValueError('失败290原源已变：'+name)
    products={path.name:path.read_bytes().decode('utf-8') for path in OLD.iterdir() if path.is_file()}
    products['sentinel_read_avx2.hpp']=HELPER
    products['channel_runtime.cpp']=once(products['channel_runtime.cpp'],'return 290; // 精确top255哨兵研究，保留原87普通u8优先路线。','return 291; // 修复290回退向量按值返回的Windows栈对齐问题，数学表和top255不变。')
    products['CMakeLists.txt']=products['CMakeLists.txt'].replace('p16_direct_sentinel','p16_direct_sentinel_v2').replace('jshc_direct_sentinel','jshc_direct_sentinel_v2')
    scripts={}
    builder=(ROOT/'scripts/build_direct_sentinel.py').read_bytes().decode('utf-8')
    builder=builder.replace('p16-direct-sentinel-build-v1','p16-direct-sentinel-v2-build-v1').replace('p16-direct-sentinel-build-frozen-v1','p16-direct-sentinel-v2-build-frozen-v1').replace('p16-direct-sentinel-source-v1','p16-direct-sentinel-v2-source-v1').replace('p16-direct-sentinel-generated-v1','p16-direct-sentinel-v2-generated-v1').replace('experiments/p16-direct-sentinel-runtime','experiments/p16-direct-sentinel-runtime-v2').replace('jshc_direct_sentinel','jshc_direct_sentinel_v2').replace('p16_direct_sentinel_contracts','p16_direct_sentinel_v2_contracts')
    scripts['build_direct_sentinel_v2.py']=builder
    contract=(ROOT/'scripts/check_direct_sentinel_contracts.py').read_bytes().decode('utf-8')
    contract=contract.replace('p16-direct-sentinel-build-v1','p16-direct-sentinel-v2-build-v1').replace('p16-direct-sentinel-build-frozen-v1','p16-direct-sentinel-v2-build-frozen-v1').replace('p16-direct-sentinel-contracts-v1','p16-direct-sentinel-v2-contracts-v1').replace('libjshc_direct_sentinel.dll','libjshc_direct_sentinel_v2.dll').replace('p16_direct_sentinel_contracts.exe','p16_direct_sentinel_v2_contracts.exe')
    scripts['check_direct_sentinel_contracts_v2.py']=contract
    quality=(ROOT/'scripts/check_direct_sentinel_native.py').read_bytes().decode('utf-8')
    quality=quality.replace('p16-direct-sentinel-build-v1','p16-direct-sentinel-v2-build-v1').replace('p16-direct-sentinel-build-frozen-v1','p16-direct-sentinel-v2-build-frozen-v1').replace('p16-direct-sentinel-quality-frozen-v1','p16-direct-sentinel-v2-quality-frozen-v1').replace('p16-direct-sentinel-quality-v1','p16-direct-sentinel-v2-quality-v1').replace('p16-direct-sentinel-contracts-v1','p16-direct-sentinel-v2-contracts-v1').replace('libjshc_direct_sentinel.dll','libjshc_direct_sentinel_v2.dll').replace('scripts/check_direct_sentinel_contracts.py','scripts/check_direct_sentinel_contracts_v2.py').replace('p16_direct_sentinel_quality_v1','p16_direct_sentinel_quality_v2').replace("libraries['new'].revision==290","libraries['new'].revision==291")
    scripts['check_direct_sentinel_native_v2.py']=quality
    mt=(ROOT/'scripts/check_direct_sentinel_full_mt.py').read_bytes().decode('utf-8')
    mt=mt.replace('from check_direct_sentinel_native import','from check_direct_sentinel_native_v2 import').replace('p16-direct-sentinel-full-mt-frozen-v1','p16-direct-sentinel-v2-full-mt-frozen-v1').replace('p16-direct-sentinel-full-mt-v1','p16-direct-sentinel-v2-full-mt-v1')
    scripts['check_direct_sentinel_full_mt_v2.py']=mt
    for name,text in scripts.items():
        if (ROOT/'scripts'/name).exists():raise FileExistsError('不覆盖派生脚本：'+name)
        ast.parse(text,filename=name)
    inputs={name:(ROOT/name).read_bytes() for name in previous['sources']}
    inputs['scripts/fork_direct_sentinel_v2.py']=Path(__file__).read_bytes()
    for name in ('build_direct_sentinel.py','check_direct_sentinel_contracts.py','check_direct_sentinel_native.py','check_direct_sentinel_full_mt.py'):
        inputs['scripts/'+name]=(ROOT/'scripts'/name).read_bytes()
    FROZEN.mkdir(parents=True)
    for name,data in inputs.items():
        path=FROZEN/'sources'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    freeze={'status':'只派生291源，保留失败290，未构建/执行模型','sources':{name:{'sha256':sha(data),'bytes':len(data)} for name,data in inputs.items()},'failed290_frozen_sha256':sha(frozen_path.read_bytes()),'patch_scope':'仅noinline输出指针/inline loadu、revision291、独立目录/目标/证据路径；prepare、top255、四像素核和有限输入不改','performance_calls':0}
    (FROZEN/'freeze.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    NEW.mkdir()
    for name,text in products.items():(NEW/name).write_bytes(text.encode('utf-8'))
    for name,text in scripts.items():(ROOT/'scripts'/name).write_bytes(text.encode('utf-8'))
    generated={'sources':{name:sha(data) for name,data in inputs.items()},'outputs':{name:sha((NEW/name).read_bytes()) for name in products},'scripts':{name:sha((ROOT/'scripts'/name).read_bytes()) for name in scripts},'performance_calls':0}
    GENERATED.write_text(json.dumps(generated,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name,row in previous['sources'].items():
        if sha((ROOT/name).read_bytes())!=row['sha256']:raise ValueError('派生后原失败源被改')
    print(json.dumps({'passed':True,'generated_files':len(products),'generated_scripts':len(scripts),'freeze_sha256':sha((FROZEN/'freeze.json').read_bytes()),'performance_calls':0}))

if __name__=='__main__':main()
