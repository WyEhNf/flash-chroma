"""复核发布原字节、全部RGB32序列化颜色、旧循环改动及五角色原始档位。"""
import hashlib
import io
import json
from pathlib import Path
import statistics
import struct
import subprocess
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    prefix='report/data/p16-color-dictionary-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('未暂存：'+name)
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;expected=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (expected and (len(raw)!=expected['bytes'] or sha(raw)!=expected['sha256'])):raise AssertionError('发布原字节变化')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if z.testzip():raise AssertionError('ZIP CRC失败')
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/color-dictionary-v1.json');export=read(directory/'export.json');quality=read(directory/'quality.json');build=read(directory/'build.json')
    if not quality['passed'] or set(quality['hashes'].values())!={'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'}:raise AssertionError('native全域未通过')
    if (quality['model_size'],quality['rom_bytes'],quality['resident'])!=(32,10039008,10039040):raise AssertionError('实际容量或ABI错误')
    with zipfile.ZipFile(directory/'exact-rom.zip') as z:rom=z.read('rom-24.bin');old=z.read('source-M16D.bin')
    if sha(rom)!=export['sha256'] or sha(rom)!=quality['rom_sha256'] or sha(old)!=plan['input_rom_sha256']:raise AssertionError('ROM身份不同')
    if rom[:4]!=b'M16C' or struct.unpack_from('<7I',rom,4)!=(1,24,4,len(rom)-32,0,0,0):raise AssertionError('M16C头错误')
    payload=np.frombuffer(rom,dtype=np.uint8,offset=32);maps=payload[:3145728].reshape(-1,3);offsets=maps[:,0].astype(np.uint32)|(maps[:,1].astype(np.uint32)<<8)|(maps[:,2].astype(np.uint32)<<16)
    if np.any(offsets<3145728) or np.any(offsets>len(payload)-64) or np.any((offsets-3145728)%64):raise AssertionError('实际map非法')
    palette=np.frombuffer(old,dtype='<u4',count=256,offset=32);oldoffsets=np.frombuffer(old,dtype='<u4',count=1048576,offset=1056);oldpool=np.frombuffer(old,dtype=np.uint8,offset=1056+4194304).reshape(-1,16);ids=(oldoffsets-4194304)//16;logical=hashlib.sha256();colors=hashlib.sha256()
    for start in range(0,1048576,65536):
        end=min(start+65536,1048576);expected_ids=oldpool[ids[start:end]];logical.update(expected_ids);expected=palette[expected_ids];addresses=offsets[start:end,None]+np.arange(16,dtype=np.uint32)[None,:]*4;actual=np.zeros(addresses.shape,dtype=np.uint32)
        for j in range(4):actual|=payload[addresses+j].astype(np.uint32)<<(8*j)
        if not np.array_equal(expected,actual):raise AssertionError('实际序列化全部RGB32不同')
        colors.update(actual.astype('<u4'))
    if logical.hexdigest()!=export['logical_sha256'] or colors.hexdigest()!=export['rgb32_new_sha256'] or export['rgb32_old_sha256']!=colors.hexdigest():raise AssertionError('全域摘要不同')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('冻结执行源不同')
    oldtext=(ROOT/'experiments/compact-dictionary-runtime/channel_avx2_24.cpp').read_text(encoding='utf-8');newtext=(ROOT/'experiments/color-dictionary-runtime/channel_avx2_color.cpp').read_text(encoding='utf-8');expected=oldtext.replace('// 精确全域字节索引：四包独立读取先行，按RGB24读取合法对齐词。','// 精确RGB32块：3B map直接指向64B最终颜色块，省去palette依赖读取。').replace('namespace jshc_dict_24 {','namespace jshc_color_24 {').replace('lookup_id','lookup_color').replace('uint32_t off;std::memcpy(&off,table+3*(code>>4),4);return table[(off&0xffffffu)+(code&15)];','uint32_t off,value;std::memcpy(&off,table+3*(code>>4),4);std::memcpy(&value,table+(off&0xffffffu)+4*(code&15),4);return value;').replace('const auto value=[table,palette](uint32_t code) {return int32_t(palette[lookup_color(table,code)]);};','const auto value=[table](uint32_t code) {return int32_t(lookup_color(table,code));};').replace('const uint32_t value=palette[lookup_color(table,code)];','const uint32_t value=lookup_color(table,code);')
    for i in range(8):expected=expected.replace('palette[i'+str(i)+']','i'+str(i))
    if expected!=newtext or 'palette[' in newtext:raise AssertionError('预定颜色查表之外的循环变化')
    with zipfile.ZipFile(directory/'performance-raw.zip') as z:workers=[json.loads(z.read(f'worker-{i}/results.json')) for i in range(4)]
    summary=read(directory/'performance.json')
    for worker in workers:
        if len(worker['rows'])!=20 or any(len(row['seconds'])!=5 or statistics.median(row['seconds'])!=row['median_seconds'] for row in worker['rows']):raise AssertionError('五角色或五轮不完整')
        if any(worker['roles'][label]['capacity']!=28046644 for label in ('ref78','ref80')):raise AssertionError('误用其它分支fast容量')
        if worker['roles']['avx2_24']['library_sha256']!='90c4081d16d4f8929247ba15af4a1a58afbc6f99246ccb95ddf35a8b9db33a6d':raise AssertionError('旧3B非原二进制')
        if any(worker['roles'][label]['capacity']!=10039040 or worker['roles'][label]['library_sha256']!=build['libraries']['jshc_memory_color_dict.dll'] for label in ('avx2_color','c99_color')):raise AssertionError('新角色库/容量不同')
    for row in summary['ratios']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==row['mode'] and r['threads']==row['threads']};values.append(min(times['ref78'],times['ref80'])/times[row['label']])
        if values!=row['per_worker'] or statistics.median(values)!=row['speed_retention']:raise AssertionError('主比值不同')
    for key,control in summary['controls'].items():
        mode,threads=key.rsplit('_',1);values=[next(c['ratio'] for c in worker['controls'] if c['mode']==mode and c['threads']==int(threads)) for worker in workers];passed=all(.8<=x<=1.25 for x in values) and 1/1.1<=statistics.median(values)<=1.1
        if values!=control['ratios'] or passed!=control['pass_']:raise AssertionError('A/A不同')
        for tier,selected in summary['tiers'][key].items():
            rows=[row for row in summary['ratios'] if row['mode']==mode and row['threads']==int(threads) and min(row['per_worker'])>=int(tier)/100];expected=min(rows,key=lambda row:row['capacity'],default=None) if passed else None
            if selected!=expected:raise AssertionError('六档不同')
    for pair in read(directory/'layout-pairs.json')['pairs']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==pair['mode'] and r['threads']==pair['threads']};values.append(times['avx2_24']/times['avx2_color'])
        if values!=pair['per_worker'] or statistics.median(values)!=pair['median'] or min(values)!=pair['worst']:raise AssertionError('3B同场配对不同')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,performance_rows=len(summary['ratios']),serialized_logical_sha256=logical.hexdigest(),serialized_rgb32_sha256=colors.hexdigest(),native_model_bytes=32,resident_bytes=10039040,scope='静态重建全部序列化颜色与统计；未补跑性能。');(directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
