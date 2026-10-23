"""离线重算512bank完整联合频数与54个固定6bit失败，不重复普查。"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    prefix='report/data/p16-rgb3d-palette-census-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('发布件未暂存')
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';path=ROOT/name;info=manifest['files'].get(path.name)
        if raw!=path.read_bytes() or (info and (len(raw)!=info['bytes'] or sha(raw)!=info['sha256'])):raise AssertionError('发布原字节不同')
        if path.suffix=='.zip':
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if z.testzip():raise AssertionError('ZIP CRC不同')
                members+=len(z.infolist())
    with zipfile.ZipFile(directory/'census-raw.zip') as z:run=json.loads(z.read('run.json'));results=json.loads(z.read('results.json'));support_raw=z.read('frequency-support.json');support=json.loads(support_raw)
    with zipfile.ZipFile(directory/'frozen-source.zip') as z:
        plan_raw=z.read('experiments/rgb3d-palette-census-v1.json');plan=json.loads(plan_raw)
        for name,value in plan['source_sha256'].items():
            if sha(z.read(name))!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('冻结源改变')
    if run['plan_sha256']!=sha(plan_raw) or results['plan_sha256']!=sha(plan_raw) or results['frequency_support_sha256']!=sha(support_raw) or results['finite_index_cases']!=8002:raise AssertionError('身份或有限合同记录不同')
    palette=support['palette_rgb24'];frequencies=support['bank_global_id_frequency']
    if len(palette)!=230 or len(set(palette))!=230 or len(frequencies)!=512 or any(len(row)!=230 or any(type(n)!=int or n<0 for n in row) for row in frequencies):raise AssertionError('完整频数格式错误')
    counts=[];global_used=set()
    for bank,row in enumerate(frequencies):
        ids=[i for i,n in enumerate(row) if n];colors=sorted({palette[i] for i in ids});record=results['banks'][bank];counts.append(len(colors));global_used.update(colors)
        if sum(row)!=32768 or record['bank']!=bank or record['input_colors']!=32768 or (record['red_high3'],record['green_high3'],record['blue_high3'])!=(bank&7,(bank>>3)&7,bank>>6) or record['global_ids']!=ids or record['output_rgb24']!=colors or record['distinct_output_colors']!=len(colors) or record['distinct_global_ids']!=len(ids) or record['six_bit_feasible']!=(len(colors)<=64):raise AssertionError('bank域或色数不符')
    failing=[bank for bank,n in enumerate(counts) if n>64]
    if len(failing)!=54 or max(counts)!=95 or counts.index(95)!=153 or results['failing_banks']!=failing or results['gate_passed'] or results['max_bank_colors']!=95 or len(global_used)!=221 or sum(sum(row) for row in frequencies)!=(1<<24):raise AssertionError('固定门槛/总域不同')
    if support['input_count_by_bank']!=[32768]*512 or results['global_reachable_colors']!=221:raise AssertionError('范围计数不符')
    for data in (support,results):
        if data['source_rom_sha256']!=plan['input_rom_sha256'] or data['logical_sha256']!=plan['logical_sha256']:raise AssertionError('原域身份不同')
    summary=read(directory/'census-summary.json')
    if summary['bank_distinct_output_colors']!=counts or summary['bank_input_counts']!=[32768]*512 or summary['failing_banks']!=failing or summary['gate_passed']:raise AssertionError('摘要不同')
    for key in ('plan_sha256','frequency_support_sha256','projected_format','before','after','resource_wall_seconds'):
        if summary[key]!=results[key]:raise AssertionError('摘要原件字段不同')
    layout=plan['projected_format']
    if sum(layout[key] for key in ('header_bytes','bank_count_bytes','bitstream_bytes','zero_guard_bytes','local_palette_bytes'))!=12715044 or layout['resident_expected_bytes']!=12715044+32 or layout['actual_abi_verified']:raise AssertionError('未实现容量投影错误')
    value=dict(passed=True,purpose=__doc__,published_files=len(names),zip_members=members,bank_count=512,failed_bank_count=len(failing),maximum_bank_colors=max(counts),maximum_bank=153,global_reachable_colors=221,domain_colors=1<<24,candidate_pixel_or_performance_calls=0,scope='仅从单次全域联合频数复算，不重读ROM/重新分类、生成可行6bit表或运行候选像素。');(directory/'git-byte-audit.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(value)
if __name__=='__main__':main()
