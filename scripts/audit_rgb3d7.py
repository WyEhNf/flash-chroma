"""离线核C7BK原字节、独立56bit组解码、8域/百图及656同场调用，不补跑。"""
import hashlib
import io
import json
from pathlib import Path
import statistics
import struct
import subprocess
import zipfile
import numpy as np
from recompute_rgb3d7_decimal import compute_raw
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    prefix='report/data/p16-rgb3d-palette7-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('发布件未暂存')
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;info=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (info and (len(raw)!=info['bytes'] or sha(raw)!=info['sha256'])):raise AssertionError('发布原字节不同')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if z.testzip():raise AssertionError('ZIP CRC不同')
                members+=len(z.infolist())
    quality=read(directory/'quality.json');export=read(directory/'export.json');build=read(directory/'build.json')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        plan_raw=z.read('experiments/rgb3d-palette7-native-v1.json');plan=json.loads(plan_raw)
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('冻结源不同')
        old_pixel=z.read('old-pixel/channel_avx2_tag.cpp');generation=json.loads(z.read('experiments/rgb3d-palette7-runtime/generation.json'))
        if sha(old_pixel)!=generation['inputs']['experiments/tagged-block16-runtime/channel_avx2_tag.cpp']:raise AssertionError('旧像素源身份不同')
        expected=old_pixel.decode().replace('jshc_tag_16','jshc_rgb3d7').replace('const uint32_t* palette','const uint8_t* palette').replace('// M16T常量直接RGB、其余原ID pool；AVX输入与输出循环保持。','// C7BK精确7bit本地palette；沿用原输入/输出循环。').replace('// LE32 map末项恰至map边界；全常量允许无pool，条件返回前不形成fallback地址。','// byte指针与memcpy允许非对齐ROM；最后bitstream短读只进入自有guard。').replace('uint32_t word;std::memcpy(&word,table+4*(code>>4),4);if(word&0x80000000u)return word&0xffffffu;return palette[table[word+(code&15)]];','const uint32_t bit=7*code,bank=((code>>5)&7)|((code>>10)&56)|((code>>15)&448);uint16_t word;std::memcpy(&word,table+(bit>>3),2);const uint32_t id=(word>>(bit&7))&127;uint32_t value;std::memcpy(&value,palette+4*((bank<<7)|id),4);return value;')
        if z.read('experiments/rgb3d-palette7-runtime/channel_avx2_rgb3d7.cpp').decode()!=expected:raise AssertionError('lookup/类型/namespace及说明以外循环有改动')
    with zipfile.ZipFile(directory/'new-libraries.zip') as z:
        for name in ('jshc_rgb3d7.dll','jshc_rgb3d7_c99.dll'):
            if sha(z.read(name))!=build['libraries'][name]:raise AssertionError('归档库与实际构建身份不同')
    if build['c99_forbidden']:raise AssertionError('C99对象有禁止ISA')
    with zipfile.ZipFile(directory/'exact-rom.zip') as z:rom=z.read('C7BK.bin')
    if len(rom)!=14943268 or sha(rom)!=export['rom_sha256'] or sha(rom)!=quality['rom_sha256'] or rom[:4]!=b'C7BK' or struct.unpack_from('<7I',rom,4)!=(1,512,7,14680064,1,128,0) or rom[14681120:14681124]!=bytes(4):raise AssertionError('实际格式/guard不同')
    census=ROOT/'report/data/p16-rgb3d-palette-census-v1/census-raw.zip'
    if sha(census.read_bytes())!=plan['census_zip_sha256']:raise AssertionError('原频数ZIP不同')
    with zipfile.ZipFile(census) as z:support_raw=z.read('frequency-support.json');support=json.loads(support_raw)
    if sha(support_raw)!=plan['frequency_support_sha256']:raise AssertionError('原完整频数不同')
    frequencies=np.asarray(support['bank_global_id_frequency']);original=np.asarray(support['palette_rgb24'],dtype='<u4');counts=np.frombuffer(rom,dtype='<u2',count=512,offset=32);palette=np.frombuffer(rom,dtype='<u4',count=65536,offset=14681124).reshape(512,128);global_ids=np.full((512,128),255,dtype=np.uint8)
    for bank in range(512):
        used=np.flatnonzero(frequencies[bank]);global_ids[bank,:len(used)]=used
        if len(used)!=counts[bank] or not np.array_equal(palette[bank,:len(used)],original[used]) or np.any(palette[bank,len(used):]):raise AssertionError('升序本地palette与原频数不同')
    if int(counts.max())!=95 or counts.tolist()!=export['bank_counts']:raise AssertionError('实际counts不同')
    digest=hashlib.sha256();logical=hashlib.sha256();table=np.frombuffer(rom,dtype=np.uint8,count=14680064,offset=1056)
    # 独立每7byte恢复8ID的56bit组解码，区别于export/native的逐pixel LE16位移。
    for begin in range(0,1<<24,1<<18):
        codes=np.arange(begin,begin+(1<<18),dtype=np.uint32);bytes7=table[7*begin//8:7*(begin+len(codes))//8].reshape(-1,7);words=np.zeros(len(bytes7),dtype=np.uint64)
        for k in range(7):words|=bytes7[:,k].astype(np.uint64)<<(8*k)
        local=((words[:,None]>>np.arange(0,56,7,dtype=np.uint64))&127).astype(np.uint8).reshape(-1);bank=((codes>>5)&7)|((codes>>10)&56)|((codes>>15)&448)
        if np.any(local>=counts[bank]):raise AssertionError('本地ID越count')
        decoded=palette[bank,local].astype('<u4');ids=global_ids[bank,local];digest.update(decoded);logical.update(ids)
    if digest.hexdigest()!='29a15ba4cb83d0840cfaa99015cda43848fa4ca43a9a1f224c19eaa7dd252497' or logical.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('独立全部RGB/ID摘要不同')
    if not quality['passed'] or quality['model_size']!=32 or quality['resident']!=14943300 or len(quality['hashes'])!=8 or set(quality['hashes'].values())!={'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'} or len(quality['photo_hashes'])!=8 or set(quality['photo_hashes'].values())!={'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'}:raise AssertionError('8域/8百图或真实ABI不符')
    if (quality['finite'],quality['refusals'],quality['image_guards'],quality['rom_guards'])!=(584,58,144,24) or quality['fixtures']['count128']['maximum_legal_local_id']!=127 or quality['fixtures']['count128']['input_cases']!=65536:raise AssertionError('有限/合法128/guard合同不符')
    with zipfile.ZipFile(directory/'performance-raw.zip') as z:worker_raw=[z.read(f'worker-{i}/results.json') for i in range(4)]
    workers=[json.loads(raw) for raw in worker_raw]
    if compute_raw(worker_raw,(directory/'performance.json').read_bytes())!=read(directory/'decimal-summary.json'):raise AssertionError('独立Decimal发布复算不同')
    summary=read(directory/'performance.json');calls=0
    for worker in workers:
        if worker['affinity_start']['actual']['allowed']!=[0,2,4,6] or worker['affinity_end']['allowed']!=[0,2,4,6] or len(worker['rows'])!=24 or len(worker['controls'])!=4:raise AssertionError('四worker/六角色或允许集不完整')
        for row in worker['rows']:
            if len(row['seconds'])!=5 or len(row['cpu_calls'])!=6 or [c['seconds'] for c in row['cpu_calls'][1:]]!=row['seconds'] or statistics.median(row['seconds'])!=row['median_seconds']:raise AssertionError('原五轮不完整')
        for control in worker['controls']:
            primary=next(r['median_seconds'] for r in worker['rows'] if r['label']=='ref80' and r['mode']==control['mode'] and r['threads']==control['threads'])
            if len(control['seconds'])!=5 or len(control['cpu_calls'])!=5 or statistics.median(control['seconds'])/primary!=control['ratio']:raise AssertionError('AA原五轮比例不同')
        for row in worker['rows']+worker['controls']:
            for call in row['cpu_calls']:
                if call['cpu_before'] not in (0,2,4,6) or call['cpu_after'] not in (0,2,4,6):raise AssertionError('CPU端点越预定允许集')
                calls+=1
        capacities={'ref78':28046644,'ref80':28046644,'linear8_avx':16779328,'linear8_clang_c99':16779328,'rgb3d7_avx':14943300,'rgb3d7_c99':14943300}
        for label,value in capacities.items():
            if worker['roles'][label]['capacity']!=value:raise AssertionError('真实角色容量不同')
        expected80=next(value for name,value in plan['input_sha256'].items() if name.endswith('libjshc_skylake_andn_normal.dll'))
        if worker['roles']['ref78']['library_sha256']!=plan['reference78']['sha256'] or worker['roles']['ref80']['library_sha256']!=expected80:raise AssertionError('较快78/80基准身份不同')
        for label in ('rgb3d7_avx','rgb3d7_c99'):
            if worker['roles'][label]['library_sha256']!=build['libraries']['jshc_rgb3d7.dll']:raise AssertionError('新冻结库不同')
        for label in ('linear8_avx','linear8_clang_c99'):
            if worker['roles'][label]['library_sha256']!=plan['linear_reference']['library_sha256']:raise AssertionError('旧冻结库不同')
    if calls!=656:raise AssertionError('656调用不完整')
    for row in summary['ratios']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==row['mode'] and r['threads']==row['threads']};values.append(min(times['ref78'],times['ref80'])/times[row['label']])
        if values!=row['per_worker'] or statistics.median(values)!=row['speed_retention']:raise AssertionError('全部组内保留率不同')
    for key,control in summary['controls'].items():
        mode,threads=key.rsplit('_',1);values=[next(c['ratio'] for c in w['controls'] if c['mode']==mode and c['threads']==int(threads)) for w in workers];passed=all(.8<=v<=1.25 for v in values) and 1/1.1<=statistics.median(values)<=1.1
        if values!=control['ratios'] or passed!=control['pass_']:raise AssertionError('AA门槛不同')
        for tier,selected in summary['tiers'][key].items():
            eligible=[r for r in summary['ratios'] if r['mode']==mode and r['threads']==int(threads) and min(r['per_worker'])>=int(tier)/100];expected=min(eligible,key=lambda r:r['capacity'],default=None) if passed else None
            if selected!=expected:raise AssertionError('独立六档不同')
    for pair in read(directory/'linear-pairs.json')['pairs']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==pair['mode'] and r['threads']==pair['threads']};values.append(times[pair['control']]/times[pair['candidate']])
        if values!=pair['per_worker'] or statistics.median(values)!=pair['median'] or min(values)!=pair['worst']:raise AssertionError('同场线性配对不同')
    for label,rss in summary['rss'].items():
        if rss['affinity_start']['actual']['allowed']!=[0,2,4,6] or rss['affinity_end']['allowed']!=[0,2,4,6]:raise AssertionError('正式RSS允许集不同')
    for name in ('quality-rss-pure.json','quality-rss-desktop.json'):
        rss=read(directory/name)
        if rss['model_bytes']!=32 or rss['resident']!=14943300 or rss['rom_sha256']!=export['rom_sha256']:raise AssertionError('质量RSS身份不同')
    value=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,model_bytes=32,resident_bytes=14943300,decoded_rgb32_sha256=digest.hexdigest(),logical_id_sha256=logical.hexdigest(),native_calls=calls,scope='独立56bit组解码与全部统计/字节核对，不重census、不补性能。');(directory/'git-byte-audit.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(value)
if __name__=='__main__':main()
