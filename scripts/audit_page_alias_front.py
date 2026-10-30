"""只离线核页别名前置和两次STOP观察原件，不调用部署API或重测。"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def events(directory):
    schema=read(directory/'event-schema.json');raw=(directory/'events.bin').read_bytes();parser=struct.Struct('<8I11Q8I');names=[value['name'] for value in schema['fields']]
    if schema['record_bytes']!=parser.size or len(raw)!=schema['records']*parser.size or schema['allocated_bytes']!=32768*parser.size:raise AssertionError('实际固定缓冲/布局不同')
    expected_offset=0
    for value in schema['fields']:
        if value['offset']!=expected_offset:raise AssertionError('字段padding与独立格式不同')
        expected_offset+=value['bytes']
    rows=[]
    with (directory/'events.csv').open('r',encoding='utf-8',newline='') as stream:
        reader=csv.reader(stream)
        if next(reader)!=names:raise AssertionError('CSV列与binary schema不同')
        for index,values in enumerate(reader):
            values=tuple(map(int,values));binary=parser.unpack_from(raw,index*parser.size)
            if values!=binary or values[0]!=index:raise AssertionError('CSV/binary逐值不同')
            rows.append(dict(zip(names,binary)))
    if len(rows)!=schema['records']:raise AssertionError('事件数不同')
    result=read(directory/'results.json')
    if result['observation_completed'] or result['case']!=8 or result['owned_state']!=[0,0,0,0,0,0,7,1]:raise AssertionError('必须保留第8例STOP')
    baseline=next(value['details'] for value in schema['markers'] if value['label']=='v1既有第2次account/固定基线')
    if result['actual_count']!=baseline+1 or 'actual='+str(baseline+1) not in result['message']:raise AssertionError('实际首漂移不同')
    last=[value for value in rows if value['case']==8];getsize=next(value for value in last if schema['operations'][value['operation']]=='file_size');injected=next(value for value in last if schema['operations'][value['operation']]=='section');closed=next(value for value in last if schema['operations'][value['operation']]=='close_file')
    if getsize['result']!=1 or getsize['last_error'] or getsize['after_count']!=baseline+1 or injected['status']!=2 or injected['before_count']!=baseline+2 or closed['arg0']!=getsize['arg0'] or closed['result']!=1 or closed['last_error'] or closed['before_count']!=baseline+2 or closed['after_count']!=baseline+1:raise AssertionError('section前区间和owned关闭receipt不同')
    all_closes=[value for value in rows if schema['operations'][value['operation']] in ('close_file','close_section','legacy_close')]
    if any(value['result']!=1 or value['last_error'] or value['before_count']-value['after_count']!=1 for value in all_closes):raise AssertionError('有非成功owned关闭')
    for name,value in result['raw_files'].items():
        if sha(directory/name)!=value:raise AssertionError('封存原始SHA不同')
    return dict(records=len(rows),baseline=baseline,final_count=result['actual_count'],first_drift_case=8,owned_close_calls=len(all_closes),owned_file=getsize['arg0'],getsize_sequence=getsize['sequence'],injected_section_sequence=injected['sequence'],closed_sequence=closed['sequence'],closed_return=closed['result'],closed_last_error=closed['last_error'],source_of_extra_handle='未采身份，不能归因',all_csv_binary_fields_equal=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--front',type=Path,required=True);p.add_argument('--handles',type=Path,required=True);p.add_argument('--metadata',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    plans=[ROOT/'experiments'/name for name in ('page-alias-runtime-v1.json','page-alias-handle-observer-v1.json','page-alias-metadata-observer-v1.json')]
    for path in plans:
        plan=read(path)
        if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(Path(name))!=value for name,value in plan['input_sha256'].items()):raise AssertionError('冻结源/输入原件改变')
    run=read(a.front/'run.json');failure=read(a.front/'contracts/failure.json');export=read(a.front/'export/export.json')
    if run['passed'] or [row['returncode'] for row in run['jobs']]!=[0,0,0,0,1] or failure['message']!='合同后句柄未回基线' or failure['owner']['state']!={'file':0,'section':0,'base':0,'span':0,'mapped_pages':0,'split_pages':0,'state':7,'reserved':0}:raise AssertionError('v1必须保留原始STOP')
    fresh={}
    for mode in ('original','aligned','alias'):
        value=read(a.front/mode/'results.json');phases=value['phases'];expected_capacity={'original':16779328,'aligned':16782416,'alias':12645456}[mode]
        if not value['passed'] or value['capacity']!=expected_capacity or phases['before']['process_handles']!=phases['closed']['process_handles'] or any(point['Protect']!=2 or point['Type']!=0x40000 for point in value['protected_ends']):raise AssertionError('fresh实际保护/关闭/账本不同')
        flags=value['working_set_pages']['raw_attributes']
        if len(flags)!=4097 or any(not word&1 or (word>>4)&2047!=2 or not (word>>15)&1 for word in flags):raise AssertionError('QWS逐页属性不同')
        expected_regions={'original':1,'aligned':2,'alias':4098}[mode]
        if len(value['virtual_regions'])!=expected_regions:raise AssertionError('实际regions不同')
        if mode!='original' and (value['guard']['State']!=0x2000 or value['guard']['AllocationProtect']!=1 or value['view_span']!=16785408):raise AssertionError('实际guard/保留VA不同')
        fresh[mode]=dict(capacity=value['capacity'],handles=[phases[name]['process_handles'] for name in ('before','opened','all_pages_read','closed')],private=[phases[name]['PrivateUsage'] for name in ('before','opened','closed')],working_set=[phases[name]['WorkingSetSize'] for name in ('before','opened','closed')],quota_nonpaged=[phases[name]['all_process_counters']['QuotaNonPagedPoolUsage'] for name in ('before','opened','closed')],virtual_regions=len(value['virtual_regions']))
    for name,value in export['outputs'].items():
        if (a.front/'export'/name).stat().st_size!=value['bytes'] or sha(a.front/'export'/name)!=value['sha256']:raise AssertionError('实际backing文件不同')
    # 只按已封存map回放，独立文件stream而非实际MapView，不能称新census或新native质量。
    canonical=hashlib.sha256();logical=hashlib.sha256()
    with (a.front/'export/alias.bin').open('rb') as alias,(a.front/'export/aligned.bin').open('rb') as aligned:
        header=alias.read(4096);plain=aligned.read(4096);ids=struct.unpack('<4096I',alias.read(16384));canonical.update(header[3040:])
        if header[3040:]!=plain[3040:]:raise AssertionError('两个原header不同')
        for identifier in ids:
            alias.seek(20480+identifier*4096);block=alias.read(4096)
            if block!=aligned.read(4096):raise AssertionError('已封存pool重放不同')
            canonical.update(block);logical.update(block)
    if canonical.hexdigest()!=export['canonical_rom_sha256'] or logical.hexdigest()!=export['logical_id_sha256']:raise AssertionError('离线全blob/ID重放身份不同')
    handles=events(a.handles);metadata_events=events(a.metadata);metadata=read(a.metadata/'metadata.json')
    if len(metadata)!=15 or sorted({value['case'] for value in metadata})!=[1,2,8]:raise AssertionError('metadata固定3次opener不同')
    for case in (1,2,8):
        values=[value for value in metadata if value['case']==case]
        if [value['label'] for value in values]!=['open返回','enter前','enter后','exit前','exit后']:raise AssertionError('context委托顺序不同')
        opened,_,_,before,closed=values
        if opened['extra']['after_count']-opened['extra']['before_count']!=2 or before['count']-closed['count']!=1 or any(not value['closefd'] for value in values) or not closed['reader_closed'] or not closed['raw_closed'] or closed['handle_info']['result'] or closed['handle_info']['last_error']!=6 or len({value['winhandle'] for value in values})!=1:raise AssertionError('真实reader关闭/额外handle限定不同')
    output=dict(audit_passed=True,purpose=__doc__,front_gate_passed=False,status='STOP-额外句柄身份unknown，不追加alias微调',fresh=fresh,net_backing_saving=16779328-(12644352+48+1056),handles_observation=handles,metadata_observation=metadata_events,metadata_contexts=3,closed_reader_handle_invalid=True,canonical_sha256=canonical.hexdigest(),logical_id_sha256=logical.hexdigest(),scope='审计通过只表示原件/账本/STOP一致；没有完整像素域/百图/性能/物理RAM资格，未重导出/census或部署。')
    a.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(audit_passed=True,front_gate_passed=False,records=handles['records']+metadata_events['records'],net_backing_saving=output['net_backing_saving']))
if __name__=='__main__':main()
