"""既有max41物理表的24种均匀轴bank普查；不prepare/apply/拟合/计时。"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('MKL_NUM_THREADS','1')
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import psutil

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'artifacts/p16-direct-active-packed-v2'
OUT=ROOT/'artifacts/p16-direct-axis-banks-v1'
PLAN=ROOT/'experiments/p16-direct-axis-banks-proposal-v1.md'
N=1<<24
MISSING=(1<<32)-1
BANKS=(2,4,8,16,32,64,128,256)
AXES=('R','G','B')
BINARY=('physical-ids-u16-with-guard.bin','whole-palette-u32.bin','packed-ids-with-guard.bin','active-palette-u32.bin')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path,value):
    if path.exists():
        raise FileExistsError('不覆盖轴bank普查：'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def freeze():
    if OUT.exists():
        raise FileExistsError('不覆盖轴bank阶段')
    assert sha(RAW/'frozen.json')=='ba77cb94813346b1906f696c30637933be7b62d738221331d725af34142268d4'
    assert sha(RAW/'results.json')=='728165235480fb336ef39ec4ce6ffb801c33d59a3c19676c62aa063ba249dc7e'
    prior,result,independent=[read(RAW/name) for name in ('frozen.json','results.json','independent.json')]
    assert result['passed'] and independent['passed']
    assert result['active_colors']==independent['active_colors']==344 and result['packed_bits']==independent['bits']==9
    assert independent['frozen_sha256']==sha(RAW/'frozen.json') and independent['results_sha256']==sha(RAW/'results.json')
    assert independent['independently_decoded_entries']==N and result['logical_entries']==N
    assert len(prior['source_sha256'])==223 and len(prior['inputs_sha256'])==13
    inputs={}
    for name in ('frozen.json','results.json','independent.json',*BINARY):
        path=RAW/name;actual=sha(path)
        if name in BINARY:
            expected=result['artifacts'][name]
            assert actual==expected['sha256'] and path.stat().st_size==expected['bytes'],name
        inputs[name]={'path':str(path),'sha256':actual,'bytes':path.stat().st_size}
    names=['scripts/census_direct_axis_banks.py','scripts/audit_direct_axis_banks.py',PLAN.relative_to(ROOT).as_posix()]
    sources={name:sha(ROOT/name) for name in names}
    for name in names:
        if name.endswith('.py'):
            ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))
    save(OUT/'frozen.json',dict(ast_pass=True,source_sha256=sources,inputs=inputs,proposal=PLAN.read_text(encoding='utf-8'),
        upstream_lineage_sources=223,upstream_lineage_inputs=13,actual_inputs_this_stage=len(inputs),
        axes=list(AXES),bank_counts=list(BANKS),configurations=24,logical_entries=N,
        python=sys.version,numpy=np.__version__,psutil=psutil.__version__,byteorder=sys.byteorder,
        native_prepare_calls=0,native_apply_calls=0,performance_samples=0,
        scope='引用已冻结223源谱系；本次只读7项实际证据，不加载native/模型/gold/照片'))
    print({'frozen_sha256':sha(OUT/'frozen.json'),'actual_inputs':len(inputs),'sources':len(sources)},flush=True)


def load_frozen():
    frozen=read(OUT/'frozen.json')
    for name,expected in frozen['source_sha256'].items():
        assert sha(ROOT/name)==expected,name
    for name,spec in frozen['inputs'].items():
        assert sha(spec['path'])==spec['sha256'] and Path(spec['path']).stat().st_size==spec['bytes'],name
    return frozen


def add_first(first,ids,whole,colors,codes):
    if first.dtype!=np.uint32 or first.shape!=(3,256,len(colors)):
        raise ValueError('需要3×256×活动RGB数的uint32 first矩阵')
    if np.any(ids>=len(whole)) or np.any(codes>=N) or len(ids)!=len(codes):
        raise ValueError('物理旧ID/输入地址越界')
    actual=whole[ids]
    column=np.searchsorted(colors,actual)
    if np.any(column>=len(colors)) or not np.array_equal(colors[column],actual):
        raise ValueError('实际RGB未在完整活动颜色集合中')
    for axis in range(3):
        coordinate=(codes>>(8*axis))&255
        np.minimum.at(first[axis],(coordinate,column),codes)


def configurations(first,colors):
    if first.shape!=(3,256,len(colors)):
        raise ValueError('固定三个轴/256坐标')
    records=[];representations={}
    for axis,name in enumerate(AXES):
        for banks in BANKS:
            width=256//banks
            coarse=first[axis].reshape(banks,width,len(colors)).min(axis=1)
            counts=(coarse!=MISSING).sum(axis=1,dtype=np.int64)
            failed=np.flatnonzero(counts>256)
            witness=[];first_bad=None
            if len(failed):
                first_bad=int(failed[0])
                ids=np.flatnonzero(coarse[first_bad]!=MISSING)
                assert len(ids)>256
                witness=[{'rgb32':int(colors[i]),'output_rgb':list(int(colors[i]).to_bytes(4,'little')[:3]),
                    'minimum_physical_input':int(coarse[first_bad,i])} for i in ids[:257]]
            record=dict(axis=name,axis_index=axis,bank_count=banks,coordinate_width=width,
                bank_color_counts=counts.tolist(),maximum_bank_colors=int(counts.max()),
                representable=not len(failed),first_overflow_bank=first_bad,overflow_257_colors=witness)
            records.append(record)
            representations[(axis,banks)]=coarse
    valid=[r for r in records if r['representable']]
    selected=min(valid,key=lambda r:(r['bank_count'],r['axis_index'])) if valid else None
    return records,selected,representations


def palette_for(coarse,colors):
    banks=len(coarse);palette=np.zeros((banks,256),np.uint32)
    local=np.full((banks,len(colors)),65535,np.uint16)
    for bank in range(banks):
        ids=np.flatnonzero(coarse[bank]!=MISSING)
        if len(ids)>256:
            raise ValueError('不可把257色截为8bit')
        palette[bank,:len(ids)]=colors[ids]
        local[bank,ids]=np.arange(len(ids),dtype=np.uint16)
    return palette,local


def encode_part(ids,whole,colors,codes,selected,palette,local):
    actual=whole[ids];column=np.searchsorted(colors,actual)
    if np.any(column>=len(colors)) or not np.array_equal(colors[column],actual):
        raise ValueError('编码RGB不在活动颜色中')
    coordinate=(codes>>(8*selected['axis_index']))&255
    bank=coordinate//selected['coordinate_width']
    encoded=local[bank,column]
    if np.any(encoded>=256):
        raise ValueError('ID不可表示，不截断')
    result=encoded.astype(np.uint8)
    np.testing.assert_array_equal(palette[bank,result],actual)
    return result


def contract():
    frozen=load_frozen()
    if (OUT/'contract.json').exists():
        raise FileExistsError('不覆盖轴bank有限合同')
    cases=[('all_axis_boundaries',np.array([0,1,255,256,257,65535,65536,65537,N-1],np.uint32),
             np.array([1,2,3,4],np.uint32),np.array([0,1,2,3,0,1,2,3,0],np.uint16)),
        ('same_rgb_different_old_id',np.array([0,256,65536,65537],np.uint32),
             np.array([7,7,3],np.uint32),np.array([0,1,2,1],np.uint16))]
    for count in (256,257):
        cases.append(('exact_'+str(count),np.arange(count,dtype=np.uint32)<<8,
            np.arange(count,dtype=np.uint32),np.arange(count,dtype=np.uint16)))
    records=[]
    for name,codes,whole,ids in cases:
        colors=np.unique(whole[ids]);first=np.full((3,256,len(colors)),MISSING,np.uint32)
        add_first(first,ids,whole,colors,codes)
        expected={}
        for code,old_id in zip(codes.tolist(),ids.tolist()):
            rgb=int(whole[old_id]);column=colors.tolist().index(rgb)
            for axis in range(3):
                key=(axis,(code>>(8*axis))&255,column)
                expected[key]=min(expected.get(key,MISSING),code)
        for axis in range(3):
            for coordinate in range(256):
                for column in range(len(colors)):
                    assert int(first[axis,coordinate,column])==expected.get((axis,coordinate,column),MISSING)
        matrix_records,selected,coarse=configurations(first,colors)
        assert len(matrix_records)==24 and selected is not None
        if name=='exact_256':
            assert selected['axis']=='R' and selected['bank_count']==2
        if name=='exact_257':
            assert all(not r['representable'] for r in matrix_records if r['axis']=='R')
            assert selected['axis']=='G' and selected['bank_count']==2
        if name=='same_rgb_different_old_id':
            assert len(colors)==2
        palette,local=palette_for(coarse[(selected['axis_index'],selected['bank_count'])],colors)
        result=encode_part(ids,whole,colors,codes,selected,palette,local)
        assert result.dtype==np.uint8
        owned=result.tobytes()+bytes(4)
        for i,value in enumerate(result):
            assert len(owned[i:i+4])==4 and int.from_bytes(owned[i:i+4],'little')&255==int(value)
        assert owned[-4:]==bytes(4)
        for bank in range(len(palette)):
            used=int(np.count_nonzero(coarse[(selected['axis_index'],selected['bank_count'])][bank]!=MISSING))
            assert np.all(palette[bank,used:]==0)
        if name=='exact_256':
            assert int(result[-1])==255
        records.append(dict(name=name,colors=len(colors),configurations=24,selected_axis=selected['axis'],
            selected_banks=selected['bank_count'],full_first_matrix_and_decode_equal=True))
    guard=[]
    for length in (0,1,2,3,4,255,256,257):
        owned=bytearray(length+4)
        assert all((length==0 or i+4<=len(owned)) for i in range(length))
        assert owned[-4:]==bytes(4)
        guard.append(length)
    artificial=np.zeros((3,256,257),np.uint32)
    rejected_records,no_choice,_=configurations(artificial,np.arange(257,dtype=np.uint32))
    assert len(rejected_records)==24 and all(not r['representable'] for r in rejected_records) and no_choice is None
    rejects=0
    try:
        palette_for(np.zeros((1,257),np.uint32),np.arange(257,dtype=np.uint32))
    except ValueError:
        rejects+=1
    selection={'axis_index':0,'coordinate_width':128}
    for invalid in (256,65535):
        try:
            encode_part(np.array([0],np.uint16),np.array([7],np.uint32),np.array([7],np.uint32),
                np.array([0],np.uint32),selection,np.zeros((2,256),np.uint32),np.full((2,1),invalid,np.uint16))
        except ValueError:
            rejects+=1
    assert rejects==3
    save(OUT/'contract.json',{'pass':True,'frozen_sha256':sha(OUT/'frozen.json'),'cases':records,
        'guard_lengths':guard,'all_24_rejected_configuration_fixture':True,
        'fixture_scope':'各finecoord放257色的人工presence矩阵，仅检验配置逻辑，不是已存在RGB模型',
        'pure_function_rejects_without_output_files':rejects,'native_calls':0,'performance_samples':0})
    print({'finite_pass':True,'cases':len(records),'guard_cases':len(guard),'rejects':rejects},flush=True)


def run():
    frozen=load_frozen();finite=read(OUT/'contract.json')
    assert finite['pass'] and finite['frozen_sha256']==sha(OUT/'frozen.json')
    save(OUT/'start.json',dict(frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json'),native_calls=0))
    ids=np.memmap(frozen['inputs'][BINARY[0]]['path'],dtype='<u2',mode='r')
    whole=np.fromfile(frozen['inputs'][BINARY[1]]['path'],dtype='<u4')
    colors=np.fromfile(frozen['inputs'][BINARY[3]]['path'],dtype='<u4')
    assert len(ids)==N+2 and np.all(ids[-2:]==0) and len(whole)==613 and len(colors)==344
    assert np.all(np.diff(colors.astype(np.int64))>0) and np.all(colors<=0xffffff)
    first=np.full((3,256,len(colors)),MISSING,np.uint32);frequencies=np.zeros(len(colors),np.uint64)
    for begin in range(0,N,65536):
        end=begin+65536;codes=np.arange(begin,end,dtype=np.uint32);part=ids[begin:end]
        add_first(first,part,whole,colors,codes)
        column=np.searchsorted(colors,whole[part])
        frequencies+=np.bincount(column,minlength=len(colors)).astype(np.uint64)
    assert int(frequencies.sum())==N and np.all(frequencies>0)
    assert np.all(np.any(first!=MISSING,axis=2))
    first.astype('<u4').tofile(OUT/'first-input-u32.bin')
    colors.astype('<u4').tofile(OUT/'active-colors-u32.bin')
    records,selected,coarse=configurations(first,colors)
    decoded=0;capacity=None
    if selected is not None:
        palette,local=palette_for(coarse[(selected['axis_index'],selected['bank_count'])],colors)
        encoded=np.zeros(N+4,np.uint8)
        for begin in range(0,N,65536):
            end=begin+65536;codes=np.arange(begin,end,dtype=np.uint32);part=ids[begin:end]
            encoded[begin:end]=encode_part(part,whole,colors,codes,selected,palette,local)
            bank=((codes>>(8*selected['axis_index']))&255)//selected['coordinate_width']
            np.testing.assert_array_equal(palette[bank,encoded[begin:end]],whole[part]);decoded+=len(part)
        assert np.all(encoded[-4:]==0)
        encoded.tofile(OUT/'selected-ids-u8-with-guard.bin')
        palette.astype('<u4').tofile(OUT/'selected-palette-u32.bin')
        capacity=N+4+selected['bank_count']*256*4
        assert capacity==encoded.nbytes+palette.nbytes
    load_frozen()
    save(OUT/'results.json',dict(passed=True,frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json'),
        physical_input_entries=N,active_colors=344,whole_palette_ids=613,
        configurations=records,selected_configuration=selected,stop='no_representable_configuration' if selected is None else None,
        selected_table_and_palette_bytes=capacity,selected_full_rgb_decode_entries=decoded,
        first_matrix_shape=list(first.shape),active_rgb_frequencies=frequencies.tolist(),
        first_matrix_payload_bytes=first.nbytes,first_matrix_missing_value=MISSING,
        main_first_matrix_original_scan_entries=N,main_selected_table_decode_entries=decoded,
        main_total_original_table_entries=N+decoded,
        entry_count_scope='只计矩阵扫描与可选解码的逻辑表项，不含身份SHA文件读取、序列化读取或OS页行为，非全部I/O',
        process_memory_observation=psutil.Process().memory_info()._asdict(),
        memory_scope='离线矩阵/时刻和OS进程峰观察；非运行时容量/RSS或prepare峰改进',
        native_prepare_calls=0,native_apply_calls=0,performance_samples=0,
        artifacts={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in OUT.iterdir() if p.is_file()},
        scope='固定max41的24均匀轴bank纯模型完整普查；唯一离线方案不授native或50%速度资格'))
    print({'passed':True,'configurations':len(records),'selected':None if selected is None else [selected['axis'],selected['bank_count']],
        'selected_table_and_palette_bytes':capacity,'native_calls':0},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('freeze','contract','run'))
    args=parser.parse_args();{'freeze':freeze,'contract':contract,'run':run}[args.mode]()
