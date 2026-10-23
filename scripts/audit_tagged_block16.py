"""离线复核M16T发布原字节、全部map/RGB、656调用、A/A及六档。"""
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
def sha(value):return hashlib.sha256(value).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    prefix='report/data/p16-tagged-block16-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('发布件未暂存')
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;value=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (value and (len(raw)!=value['bytes'] or sha(raw)!=value['sha256'])):raise AssertionError('发布原字节不同')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if z.testzip():raise AssertionError('ZIP CRC不同')
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/tagged-block16-native-v1.json');quality=read(directory/'quality.json');export=read(directory/'export.json');build=read(directory/'build.json');census=read(directory/'census.json')
    if not quality['passed'] or len(quality['hashes'])!=8 or set(quality['hashes'].values())!={'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'}:raise AssertionError('8完整域不同')
    if (quality['model_size'],quality['resident'],quality['finite'],quality['refusals'],quality['image_guards'],quality['rom_guards'])!=(1056,5916192,584,64,144,40):raise AssertionError('实际ABI或合同覆盖不同')
    if quality['fixtures']['constant_zero_pool']['pool_bytes'] or quality['fixtures']['mixed']['pool_bytes']!=16:raise AssertionError('零pool或混合夹具未覆盖')
    with zipfile.ZipFile(directory/'exact-rom.zip') as z:rom=z.read('new-M16T.bin');old=z.read('source-M16D-16.bin')
    if sha(rom)!=export['rom_sha256'] or sha(rom)!=quality['rom_sha256'] or sha(old)!=plan['input_rom_sha256'] or len(old)-len(rom)!=3536:raise AssertionError('ROM身份或节省不同')
    if rom[:4]!=b'M16T' or struct.unpack_from('<I',rom,8)[0]!=4 or rom[32:1056]!=old[32:1056]:raise AssertionError('格式或palette改变')
    palette=np.frombuffer(old,dtype='<u4',count=256,offset=32);pool=np.frombuffer(old,dtype=np.uint8,offset=1056+4194304).reshape(-1,16);ids=(np.frombuffer(old,dtype='<u4',count=1048576,offset=1056)-4194304)//16;constant=np.all(palette[pool]==palette[pool[:,:1]],axis=1);words=np.frombuffer(rom,dtype='<u4',count=1048576,offset=1056);payload=np.frombuffer(rom,dtype=np.uint8,offset=1056);tags=(words&0x80000000)!=0
    if int(constant.sum())!=221 or int(tags.sum())!=392293 or not np.array_equal(tags,constant[ids]) or rom[1056+4194304:]!=pool[~constant].tobytes():raise AssertionError('固定普查或稳定pool压紧不同')
    digest=hashlib.sha256();logical=hashlib.sha256()
    for start in range(0,len(ids),65536):
        end=min(start+65536,len(ids));w=words[start:end];tag=tags[start:end];decoded=np.empty((len(w),16),dtype='<u4');decoded[tag]=(w[tag]&0xffffff)[:,None];decoded[~tag]=palette[payload[w[~tag,None]+np.arange(16,dtype=np.uint32)]];expected=palette[pool[ids[start:end]]]
        if not np.array_equal(decoded,expected):raise AssertionError('完整序列化RGB不同')
        digest.update(decoded);logical.update(pool[ids[start:end]])
    if digest.hexdigest()!=export['rgb32_sha256'] or logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or census['constant_map_entries']!=392293:raise AssertionError('全部逻辑摘要不同')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('冻结源改变')
    with zipfile.ZipFile(directory/'performance-raw.zip') as z:workers=[json.loads(z.read(f'worker-{i}/results.json')) for i in range(4)]
    summary=read(directory/'performance.json');calls=0
    for worker in workers:
        if worker['affinity_start']['actual']['allowed']!=[0,2,4,6] or worker['affinity_end']['allowed']!=[0,2,4,6] or len(worker['rows'])!=24 or len(worker['controls'])!=4:raise AssertionError('六角色情形或允许集不完整')
        for row in worker['rows']:
            if len(row['seconds'])!=5 or len(row['cpu_calls'])!=6 or [r['seconds'] for r in row['cpu_calls'][1:]]!=row['seconds'] or statistics.median(row['seconds'])!=row['median_seconds']:raise AssertionError('完整五遍不同')
        for control in worker['controls']:
            primary=next(r['median_seconds'] for r in worker['rows'] if r['label']=='ref80' and r['threads']==control['threads'] and r['mode']==control['mode'])
            if len(control['seconds'])!=5 or len(control['cpu_calls'])!=5 or statistics.median(control['seconds'])/primary!=control['ratio']:raise AssertionError('AA原始比例不同')
        for row in worker['rows']+worker['controls']:
            for call in row['cpu_calls']:
                if call['cpu_before'] not in (0,2,4,6) or call['cpu_after'] not in (0,2,4,6):raise AssertionError('CPU端点越界')
                calls+=1
        expected_caps={'ref78':28046644,'ref80':28046644,'old32':5919728,'old3B':4871152,'tag_avx':5916192,'tag_c99':5916192}
        for role,value in expected_caps.items():
            if worker['roles'][role]['capacity']!=value:raise AssertionError('真实容量不同')
        for role in ('tag_avx','tag_c99'):
            if worker['roles'][role]['library_sha256']!=build['libraries']['jshc_memory_tag16.dll']:raise AssertionError('新库SHA不同')
        for role in ('old32','old3B'):
            if worker['roles'][role]['library_sha256']!=sha(Path(plan[role]['library']).read_bytes()):raise AssertionError('旧库SHA不同')
    if calls!=656:raise AssertionError('656调用不完整')
    for row in summary['ratios']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==row['mode'] and r['threads']==row['threads']};values.append(min(times['ref78'],times['ref80'])/times[row['label']])
        if values!=row['per_worker'] or statistics.median(values)!=row['speed_retention']:raise AssertionError('速度比值不同')
    for key,control in summary['controls'].items():
        mode,threads=key.rsplit('_',1);values=[next(c['ratio'] for c in w['controls'] if c['mode']==mode and c['threads']==int(threads)) for w in workers];passed=all(.8<=x<=1.25 for x in values) and 1/1.1<=statistics.median(values)<=1.1
        if values!=control['ratios'] or passed!=control['pass_']:raise AssertionError('AA门禁不同')
        for tier,selected in summary['tiers'][key].items():
            eligible=[r for r in summary['ratios'] if r['mode']==mode and r['threads']==int(threads) and min(r['per_worker'])>=int(tier)/100];expected=min(eligible,key=lambda r:r['capacity'],default=None) if passed else None
            if selected!=expected:raise AssertionError('六档不同')
    for pair in read(directory/'layout-pairs.json')['pairs']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==pair['mode'] and r['threads']==pair['threads']};values.append(times[pair['control']]/times['tag_avx'])
        if values!=pair['per_worker'] or statistics.median(values)!=pair['median'] or min(values)!=pair['worst']:raise AssertionError('新旧配对不同')
    for role,rss in summary['rss'].items():
        if rss['affinity_start']['actual']['allowed']!=[0,2,4,6] or rss['affinity_end']['allowed']!=[0,2,4,6]:raise AssertionError('RSS允许集不同')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,rgb32_sha256=digest.hexdigest(),native_calls=calls,allowed_cpus=[0,2,4,6],resident_bytes=5916192,tag_entries=392293,scope='离线重建序列化全部RGB与受控统计，未补跑性能。');(directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
