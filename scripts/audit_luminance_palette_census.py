"""离线重算bank×ID频数、九bank失败与静态容量；不重新普查16M输出。"""
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    prefix='report/data/p16-luminance-palette-census-v1';directory=ROOT/prefix;manifest=read(directory/'manifest.json');names=[prefix+'/'+name for name in manifest['files']]+[prefix+'/manifest.json'];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT))
    for name in names:
        header=stream.readline().split()
        if len(header)!=3:raise AssertionError('未暂存原件')
        raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';relative=name[len(prefix)+1:];info=manifest['files'].get(relative)
        if raw!=(ROOT/name).read_bytes() or (info and (len(raw)!=info['bytes'] or sha(raw)!=info['sha256'])):raise AssertionError('发布原字节不同')
    plan=read(directory/'sources/experiments/luminance-palette-census-v1.json');results=read(directory/'results.json');run=read(directory/'run.json');support=read(directory/'frequency-support.json')
    plan_sha=sha((directory/'sources/experiments/luminance-palette-census-v1.json').read_bytes())
    if results['plan_sha256']!=plan_sha or run['plan_sha256']!=plan_sha or sha((directory/'frequency-support.json').read_bytes())!=results['frequency_support_sha256']:raise AssertionError('计划/支持身份不同')
    for name,value in plan['source_sha256'].items():
        if sha((directory/'sources'/name).read_bytes())!=value or sha((ROOT/name).read_bytes())!=value:raise AssertionError('冻结源不同')
    palette=support['palette_rgb24'];frequencies=support['bank_global_id_frequency']
    if len(palette)!=230 or len(set(palette))!=230 or len(frequencies)!=16 or any(len(row)!=230 or any(type(n)!=int or n<0 for n in row) for row in frequencies):raise AssertionError('频数/源palette不完整')
    # 独立三角计数R+B的和，再遍历256个G；不读取原ROM或重新分类输出。
    expected=[0]*16
    for green in range(256):
        for rb in range(511):expected[(rb+2*green)>>6]+=rb+1 if rb<256 else 511-rb
    counts=[];global_used=set()
    for bank,row in enumerate(frequencies):
        ids=[i for i,n in enumerate(row) if n];colors=sorted({palette[i] for i in ids});record=results['banks'][bank];counts.append(len(colors));global_used.update(colors)
        if record['bank']!=bank or record['input_colors']!=expected[bank] or sum(row)!=expected[bank] or record['global_ids']!=ids or record['output_rgb24']!=colors or record['distinct_output_colors']!=len(colors) or record['distinct_global_ids']!=len(ids) or record['seven_bit_feasible']!=(len(colors)<=128):raise AssertionError('bank色数或域大小不同')
    failing=[i for i,n in enumerate(counts) if n>128]
    if counts!=[21,69,94,113,132,145,157,173,190,201,198,155,134,89,38,1] or failing!=list(range(4,13)) or results['gate_passed'] or results['failing_banks']!=failing or results['max_bank_colors']!=201:raise AssertionError('冻结失败门槛不同')
    if sum(expected)!=(1<<24) or support['input_count_by_bank']!=expected or results['global_reachable_colors']!=len(global_used) or len(global_used)!=221:raise AssertionError('总域或实际命中色不同')
    rgb=read(directory/'rgb-stream-check.json');expected_rgb={palette[i]:sum(row[i] for row in frequencies) for i in range(230) if sum(row[i] for row in frequencies)};actual_rgb={row['rgb24']:row['count'] for row in rgb['rgb_frequencies']}
    if not rgb['passed'] or rgb['rgb_source_sha256']!='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22' or rgb['rgb_source_bytes']!=50331648 or actual_rgb!=expected_rgb or len(actual_rgb)!=221 or not rgb['sets_equal'] or not rgb['frequencies_equal'] or rgb['unreachable_legal_palette_count']!=9:raise AssertionError('独立完整RGB流与逻辑频数比较不同')
    verifier=directory/'sources/scripts/verify_luminance_palette_rgb_support.py'
    if sha(verifier.read_bytes())!=rgb['script_sha256'] or rgb['frequency_support_sha256']!=sha((directory/'frequency-support.json').read_bytes()) or rgb['logical_id_sha256']!=plan['logical_sha256']:raise AssertionError('独立核对身份不同')
    for data in (support,results):
        if data['source_rom_sha256']!=plan['input_rom_sha256'] or data['logical_sha256']!=plan['logical_sha256']:raise AssertionError('原域身份不同')
    layout=plan['projected_format']
    if sum(layout[n] for n in ('header_bytes','bank_count_bytes','local_palette_bytes','bitstream_bytes','zero_guard_bytes'))!=14688324 or layout['resident_expected_bytes']!=14688324+32 or layout['actual_abi_verified']:raise AssertionError('未实现容量投影口径不同')
    value=dict(passed=True,purpose=__doc__,published_files=len(names),plan_sha256=plan_sha,bank_colors=counts,failing_banks=failing,global_reachable_colors=221,rgb_stream_frequencies_equal=True,domain_colors=sum(expected),candidate_pixel_or_performance_calls=0,scope='从已封存全部联合频数及另授独立3c9c RGB核对原件复算；静态容量仍是不可行方案投影，未重复亮度分类/生成ROM/执行候选像素核或性能。')
    (directory/'git-byte-audit.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(value)
if __name__=='__main__':main()
