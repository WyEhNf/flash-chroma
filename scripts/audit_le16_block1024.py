"""核LE16发布字节、整pool/逻辑域、560条CPU记录与四worker六档。"""
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
    prefix='report/data/p16-le16-block1024-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('发布件未暂存')
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;value=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (value and (len(raw)!=value['bytes'] or sha(raw)!=value['sha256'])):raise AssertionError('发布原字节不同')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if z.testzip():raise AssertionError('ZIP CRC不同')
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/le16-block1024-v1.json');quality=read(directory/'quality.json');export=read(directory/'export.json');build=read(directory/'build.json')
    if not quality['passed'] or len(quality['hashes'])!=8 or set(quality['hashes'].values())!={'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'}:raise AssertionError('8次完整域未通过')
    if (quality['model_size'],quality['resident'],quality['positive_maximum_id'],quality['positive_palette_count'],quality['positive_fixture_bytes'])!=(1056,10768448,65535,256,67142688):raise AssertionError('实际ABI或65535合法边界错误')
    with zipfile.ZipFile(directory/'exact-rom.zip') as z:rom=z.read('new-LE16.bin');old=z.read('source-M16D-1024.bin')
    if sha(rom)!=export['rom_sha256'] or sha(rom)!=quality['rom_sha256'] or sha(old)!=plan['input_rom_sha256'] or len(old)-len(rom)!=32768:raise AssertionError('ROM身份或节省错误')
    if rom[:4]!=b'M10L' or struct.unpack_from('<I',rom,8)[0]!=10 or rom[32:1056]!=old[32:1056]:raise AssertionError('格式/palette未保留')
    if rom[1056+32768:]!=old[1056+65536:]:raise AssertionError('pool字节有变化')
    ids=np.frombuffer(rom,dtype='<u2',count=16384,offset=1056);oldids=(np.frombuffer(old,dtype='<u4',count=16384,offset=1056)-65536)//1024;pool=np.frombuffer(rom,dtype=np.uint8,offset=1056+32768).reshape(-1,1024)
    if len(pool)!=10482 or not np.array_equal(ids,oldids) or int(ids.max())>=len(pool):raise AssertionError('实际map或块数错误')
    logical=sha(pool[ids].reshape(-1))
    if logical!=export['logical_sha256'] or logical!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('全部逻辑ID不同')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('冻结源不同')
        oldtext=z.read('old-control/memory_avx2_10.cpp')
        if sha(oldtext)!=plan['old_avx2_source_sha256']:raise AssertionError('旧像素源不同')
    expected=oldtext.decode().replace('\r\n','\n').replace('namespace jshc_mem_10 {','namespace jshc_le16_10 {').replace('uint32_t offset;std::memcpy(&offset,table+4*(code>>10),4);return table[offset+(code&1023)];','uint16_t id;std::memcpy(&id,table+2*(code>>10),2);return table[32768u+(uint32_t(id)<<10)+(code&1023)];')
    if expected!=(ROOT/'experiments/le16-block1024-runtime/channel_avx2_le16.cpp').read_text(encoding='utf-8'):raise AssertionError('lookup之外像素循环改变')
    with zipfile.ZipFile(directory/'performance-raw.zip') as z:workers=[json.loads(z.read(f'worker-{i}/results.json')) for i in range(4)]
    summary=read(directory/'performance.json');calls=0
    for worker in workers:
        if worker['affinity_start']['actual']['allowed']!=[0,2,4,6] or worker['affinity_end']['allowed']!=[0,2,4,6]:raise AssertionError('实际允许集不同')
        if len(worker['rows'])!=20 or len(worker['controls'])!=4:raise AssertionError('五角色情形不完整')
        for row in worker['rows']:
            if len(row['seconds'])!=5 or len(row['cpu_calls'])!=6 or [r['seconds'] for r in row['cpu_calls'][1:]]!=row['seconds'] or statistics.median(row['seconds'])!=row['median_seconds']:raise AssertionError('五轮及预热记录不完整')
        for control in worker['controls']:
            if len(control['seconds'])!=5 or len(control['cpu_calls'])!=5 or [r['seconds'] for r in control['cpu_calls']]!=control['seconds']:raise AssertionError('AA调用记录不完整')
        for row in worker['rows']+worker['controls']:
            for call in row['cpu_calls']:
                if call['cpu_before'] not in (0,2,4,6) or call['cpu_after'] not in (0,2,4,6):raise AssertionError('调用端点CPU越预定mask')
                calls+=1
        if any(worker['roles'][label]['capacity']!=28046644 for label in ('ref78','ref80')) or worker['roles']['old1024']['capacity']!=10801216 or worker['roles']['old1024']['library_sha256']!=plan['reference1024']['sha256']:raise AssertionError('旧控制真实容量/二进制不同')
        if any(worker['roles'][label]['capacity']!=10768448 or worker['roles'][label]['library_sha256']!=build['libraries']['jshc_memory_le16_1024.dll'] for label in ('avx2_le16','c99_le16')):raise AssertionError('新角色身份不同')
    if calls!=560:raise AssertionError('560调用记录不完整')
    for row in summary['ratios']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==row['mode'] and r['threads']==row['threads']};values.append(min(times['ref78'],times['ref80'])/times[row['label']])
        if values!=row['per_worker'] or statistics.median(values)!=row['speed_retention']:raise AssertionError('速度比值错误')
    for key,control in summary['controls'].items():
        mode,threads=key.rsplit('_',1);values=[next(c['ratio'] for c in w['controls'] if c['mode']==mode and c['threads']==int(threads)) for w in workers];passed=all(.8<=x<=1.25 for x in values) and 1/1.1<=statistics.median(values)<=1.1
        if values!=control['ratios'] or passed!=control['pass_']:raise AssertionError('AA判定错误')
        for tier,selected in summary['tiers'][key].items():
            eligible=[r for r in summary['ratios'] if r['mode']==mode and r['threads']==int(threads) and min(r['per_worker'])>=int(tier)/100];expected=min(eligible,key=lambda r:r['capacity'],default=None) if passed else None
            if selected!=expected:raise AssertionError('六档选取错误')
    for pair in read(directory/'layout-pairs.json')['pairs']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==pair['mode'] and r['threads']==pair['threads']};values.append(times['old1024']/times['avx2_le16'])
        if values!=pair['per_worker'] or statistics.median(values)!=pair['median'] or min(values)!=pair['worst']:raise AssertionError('同场旧新配对错误')
    for role,rss in summary['rss'].items():
        if rss['affinity_start']['actual']['allowed']!=[0,2,4,6] or rss['affinity_end']['allowed']!=[0,2,4,6]:raise AssertionError('RSS允许集不同')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,logical_sha256=logical,native_calls=calls,allowed_cpus=[0,2,4,6],model_bytes=1056,resident_bytes=10768448,saved_bytes=32768,scope='静态重建全ID/原字节与全部受控同场统计，不补跑性能。');(directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
