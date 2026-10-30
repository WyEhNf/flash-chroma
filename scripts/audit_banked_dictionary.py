"""复算bank离线唯一选择、真实ABI容量、序列化全ID与七角色原始档位。"""
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
    prefix='report/data/p16-banked-dictionary-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('未暂存：'+name)
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;expected=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (expected and (len(raw)!=expected['bytes'] or sha(raw)!=expected['sha256'])):raise AssertionError('原字节变化')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if z.testzip():raise AssertionError('ZIP CRC失败')
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/banked-dictionary-native-v1.json');profile=read(directory/'profile.json');eligible=[]
    if sha((directory/'profile.json').read_bytes())!=plan['profile_result_sha256']:raise AssertionError('离线选择原件身份不同')
    for row in profile['records']:
        total=sum(row['bank_unique']);rom=1056+2097152+4*row['banks']+16*total;resident=rom+1056;feasible=max(row['bank_unique'])<=65536
        if total!=row['sum_unique'] or rom!=row['rom_bytes'] or resident!=row['resident_bytes'] or feasible!=row['local16_feasible'] or row['cross_bank_duplicate_bytes']!=(total-row['global_unique'])*16:raise AssertionError('bank容量或重复pool错误')
        if feasible and resident<4871152:eligible.append(row)
    if min(eligible,key=lambda row:(row['resident_bytes'],row['banks']))!=profile['selected'] or plan['selected_banks']!=4:raise AssertionError('违反唯一最小容量选择')
    export=read(directory/'export.json');quality=read(directory/'quality.json')
    if not quality['passed'] or set(quality['hashes'].values())!={'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'}:raise AssertionError('实际native完整域未通过')
    if export['model_bytes']!=1072 or export['resident_bytes']!=profile['selected']['resident_bytes']+16 or quality['model_size']!=1072 or quality['resident']!=export['resident_bytes']:raise AssertionError('新ABI额外16B未完整计入')
    with zipfile.ZipFile(directory/'exact-rom.zip') as z:rom=z.read('rom-4.bin')
    if sha(rom)!=export['rom_sha256'] or sha(rom)!=quality['rom_sha256'] or len(rom)!=export['rom_bytes']:raise AssertionError('实际ROM身份错误')
    payload=rom[1056:];local=np.frombuffer(payload,dtype='<u2',count=1048576);bases=struct.unpack_from('<4I',payload,2097152);digest=hashlib.sha256()
    for bank in range(4):
        end=bases[bank+1] if bank<3 else len(payload);pool=np.frombuffer(payload,dtype=np.uint8,offset=bases[bank],count=end-bases[bank]).reshape(-1,16);digest.update(pool[local[bank*262144:(bank+1)*262144]].reshape(-1))
    if digest.hexdigest()!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('序列化ROM全部ID不同')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('冻结执行源不同')
    old=(ROOT/'experiments/split-dictionary-runtime/channel_avx2_split.cpp').read_text(encoding='utf-8');new=(ROOT/'experiments/banked-dictionary-runtime/channel_avx2_bank.cpp').read_text(encoding='utf-8').replace('namespace jshc_bank_4 {','namespace jshc_split_17 {')
    new=new.replace('const uint32_t* palette,const uint32_t* bases,','const uint32_t* palette,').replace('[table,palette,bases]','[table,palette]').replace('[bytes,p,bases]','[bytes,p]').replace('lookup_id(table,bases,code)','lookup_id(table,code)').replace('lookup_id(bytes,bases,code','lookup_id(bytes,code')
    for name in ('read','read_wide','scalar_one','run'):new=new.replace(name+'(table,palette,bases,',name+'(table,palette,')
    def strip(text):
        start=text.index('inline __attribute__((always_inline)) uint32_t lookup_id');begin=text.rfind('\n//',0,start);end=text.index('\n}',start)+2;return text[:begin]+text[end:]
    if strip(new)!=strip(old):raise AssertionError('lookup和bases参数传递以外的像素逻辑变化')
    with zipfile.ZipFile(directory/'performance-raw.zip') as z:workers=[json.loads(z.read(f'worker-{i}/results.json')) for i in range(4)]
    summary=read(directory/'performance.json')
    for worker in workers:
        if len(worker['rows'])!=28 or any(len(row['seconds'])!=5 or statistics.median(row['seconds'])!=row['median_seconds'] for row in worker['rows']):raise AssertionError('七角色或五轮不完整')
    for row in summary['ratios']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==row['mode'] and r['threads']==row['threads']};values.append(min(times['ref78'],times['ref80'])/times[row['label']])
        if values!=row['per_worker'] or statistics.median(values)!=row['speed_retention']:raise AssertionError('主比值不同')
    for pair in read(directory/'layout-pairs.json')['pairs']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==pair['mode'] and r['threads']==pair['threads']};values.append(times[pair['old']]/times['avx2_bank'])
        if values!=pair['per_worker'] or statistics.median(values)!=pair['median'] or min(values)!=pair['worst']:raise AssertionError('同场布局配对不同')
    for key,control in summary['controls'].items():
        mode,threads=key.rsplit('_',1);values=[next(c['ratio'] for c in worker['controls'] if c['mode']==mode and c['threads']==int(threads)) for worker in workers];passed=all(.8<=x<=1.25 for x in values) and 1/1.1<=statistics.median(values)<=1.1
        if values!=control['ratios'] or passed!=control['pass_']:raise AssertionError('A/A判定不同')
        for tier,selected in summary['tiers'][key].items():
            rows=[row for row in summary['ratios'] if row['mode']==mode and row['threads']==int(threads) and min(row['per_worker'])>=int(tier)/100];expected=min(rows,key=lambda row:row['capacity'],default=None) if passed else None
            if selected!=expected:raise AssertionError('档位选取不同')
    with zipfile.ZipFile(ROOT/'report/data/p16-compact-dictionary-v1/new-libraries.zip') as z:oldsha=sha(z.read('jshc_memory_rom.dll'))
    oldplan=read(ROOT/'experiments/compact-dictionary-v1.json')
    build=read(directory/'build.json')
    with zipfile.ZipFile(ROOT/'report/data/p16-memory-rom-v1/measured-libraries.zip') as z:
        for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll'):
            if sha(z.read(name))!=build['libraries'][name]:raise AssertionError('原运行库依赖包不同')
    for worker in workers:
        if worker['roles']['dict32']['library_sha256']!=oldplan['reference32']['sha256'] or any(worker['roles'][label]['library_sha256']!=oldsha for label in ('avx2_17','avx2_24')):raise AssertionError('旧控制并非原二进制')
        if any(worker['roles'][label]['library_sha256']!=build['libraries']['jshc_memory_bank.dll'] or worker['roles'][label]['capacity']!=4248656 for label in ('avx2_bank','c99_bank')):raise AssertionError('新角色实际库/容量不同')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,rows=len(summary['ratios']),selected_banks=4,actual_model_bytes=1072,serialized_logical_id_sha256=digest.hexdigest(),unchanged_pixel_logic_sha256=sha(strip(old).encode()),scope='只静态复算原字节、实际序列化ROM与全部统计，不重跑性能。');(directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
