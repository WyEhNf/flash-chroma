"""静态复算M16S发布原字节、像素循环不变、七角色档位及旧二进制来源。"""
import hashlib
import io
import json
from pathlib import Path
import statistics
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    prefix='report/data/p16-split-dictionary-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+n for n in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('未暂存：'+name)
        blob=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;expected=manifest['files'].get(path.name)
        if blob!=path.read_bytes() or (expected and (len(blob)!=expected['bytes'] or sha(blob)!=expected['sha256'])):raise AssertionError('原字节变化：'+name)
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                if z.testzip():raise AssertionError('ZIP CRC失败')
                members+=len(z.infolist())
    plan=read(ROOT/'experiments/split-dictionary-v1.json')
    with zipfile.ZipFile(directory/'measured-source.zip') as z:
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('所测源码变化：'+name)
    def without_lookup(text):
        start=text.index('inline __attribute__((always_inline)) uint32_t lookup_id');begin=text.rfind('\n//',0,start);end=text.index('\n}',start)+2
        return text[:begin]+text[end:]
    old=(ROOT/'experiments/compact-dictionary-runtime/channel_avx2_17.cpp').read_text(encoding='utf-8');new=(ROOT/'experiments/split-dictionary-runtime/channel_avx2_split.cpp').read_text(encoding='utf-8').replace('namespace jshc_split_17 {','namespace jshc_dict_17 {')
    normalized=without_lookup(old)
    if normalized!=without_lookup(new):raise AssertionError('lookup之外的AVX2像素循环变化')
    quality=read(directory/'quality.json');export=read(directory/'export.json');summary=read(directory/'performance.json')
    if not quality['passed'] or len(set(quality['hashes'].values()))!=1 or export['logical_sha256']!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0' or quality['rom_sha256']!=export['sha256']:raise AssertionError('完整域或ROM身份不同')
    with zipfile.ZipFile(directory/'performance-raw.zip') as z:workers=[json.loads(z.read(f'worker-{i}/results.json')) for i in range(4)]
    rssplan=read(ROOT/'experiments/split-dictionary-rss-v1.json');rss=read(directory/'stream-rss.json')
    if sha((ROOT/'scripts/rss_split_dictionary.py').read_bytes())!=rssplan['script_sha256'] or sha((ROOT/'experiments/split-dictionary-v1.json').read_bytes())!=rssplan['parent_plan_sha256']:raise AssertionError('RSS补充计划不同')
    with zipfile.ZipFile(directory/'stream-rss-raw.zip') as z:
        for label in plan['roles']:
            record=json.loads(z.read(f'rss-{label}/rss.json'))
            if record!=rss['rss'][label] or record['library_sha256']!=workers[0]['roles'][label]['library_sha256'] or record['model_capacity']!=workers[0]['roles'][label]['capacity']:raise AssertionError('流式RSS角色身份不同')
    for worker in workers:
        if len(worker['rows'])!=28 or any(len(row['seconds'])!=5 or statistics.median(row['seconds'])!=row['median_seconds'] for row in worker['rows']):raise AssertionError('五轮或七角色不完整')
    for row in summary['ratios']:
        ratios=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==row['mode'] and r['threads']==row['threads']};ratios.append(min(times['ref78'],times['ref80'])/times[row['label']])
        if ratios!=row['per_worker'] or statistics.median(ratios)!=row['speed_retention']:raise AssertionError('主档位原始比值不同')
    for key,control in summary['controls'].items():
        mode,threads=key.rsplit('_',1);values=[next(c['ratio'] for c in worker['controls'] if c['mode']==mode and c['threads']==int(threads)) for worker in workers];passed=all(.8<=x<=1.25 for x in values) and 1/1.1<=statistics.median(values)<=1.1
        if values!=control['ratios'] or passed!=control['pass_']:raise AssertionError('A/A状态不同')
        for tier,result in summary['tiers'][key].items():
            rows=[r for r in summary['ratios'] if r['mode']==mode and r['threads']==int(threads) and min(r['per_worker'])>=int(tier)/100];expected=min(rows,key=lambda r:r['capacity'],default=None) if passed else None
            if result!=expected:raise AssertionError('档位选取不同')
    for pair in read(directory/'layout-pairs.json')['pairs']:
        values=[]
        for worker in workers:
            times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==pair['mode'] and r['threads']==pair['threads']};values.append(times[pair['old']]/times['avx2_split'])
        if values!=pair['per_worker'] or statistics.median(values)!=pair['median'] or min(values)!=pair['worst']:raise AssertionError('同场布局比值不同')
    with zipfile.ZipFile(ROOT/'report/data/p16-compact-dictionary-v1/new-libraries.zip') as z:oldsha=sha(z.read('jshc_memory_rom.dll'))
    oldplan=read(ROOT/'experiments/compact-dictionary-v1.json');expected32=oldplan['reference32']['sha256']
    for worker in workers:
        if worker['roles']['dict32']['library_sha256']!=expected32 or any(worker['roles'][label]['library_sha256']!=oldsha for label in ('avx2_17','avx2_24')):raise AssertionError('旧控制不是原DLL')
    with zipfile.ZipFile(ROOT/'report/data/p16-memory-rom-v1/measured-libraries.zip') as z:
        build=read(directory/'build.json')
        for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll'):
            if sha(z.read(name))!=build['libraries'][name]:raise AssertionError('原依赖包不同')
    result=dict(passed=True,purpose=__doc__,files=len(names),zip_members=members,statistics_rows=len(summary['ratios']),unchanged_avx2_loop_sha256=sha(normalized.encode()),old_dictionary_libraries_match=True,scope='仅静态字节/原始统计核验，不重复运行性能。');(directory/'git-byte-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
