"""标准库解NPZ/NPY，逐point及group重建补集账单；不导入NumPy/生产函数/solver。"""
from __future__ import annotations
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/cinema-cap40-complement-census-v1'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def arrays(path,names):
    formats={'|u1':'B','<u2':'H','<u4':'I','<u8':'Q','<i2':'h','<i4':'i','<i8':'q'}
    result={}
    with zipfile.ZipFile(path) as archive:
        assert len(archive.namelist())==len(set(archive.namelist()))
        for name in names:
            raw=archive.read(name+'.npy');assert raw[:6]==b'\x93NUMPY'
            major,minor=raw[6:8];assert major in (1,2,3) and minor==0
            n=2 if major==1 else 4;start=8+n;size=int.from_bytes(raw[8:start],'little')
            header=ast.literal_eval(raw[start:start+size].decode('utf-8').strip())
            assert header['fortran_order'] is False and header['descr'] in formats
            shape=header['shape'];assert isinstance(shape,tuple) and all(type(v) is int and v>=0 for v in shape)
            form='<'+formats[header['descr']];payload=raw[start+size:]
            assert len(payload)==math.prod(shape)*struct.calcsize(form)
            result[name]=[v[0] for v in struct.iter_unpack(form,payload)]
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖补集独立审核')
    frozen=read(OUT/'frozen.json');result=read(OUT/'results.json')
    contract=read(OUT/'contract.json')
    def verify():
        for name,value in frozen['sources_sha256'].items():
            assert sha(ROOT/name)==value,name
        for name,spec in frozen['inputs'].items():
            assert sha(spec['path'])==spec['sha256'] and Path(spec['path']).stat().st_size==spec['bytes'],name
    verify();assert result['passed'] and result['frozen_sha256']==sha(OUT/'frozen.json')
    assert contract==dict(passed=True,frozen_sha256=sha(OUT/'frozen.json'),scalar_boundary_points=6,
        empty_input_cases=1,invalid_cases=5,repeated_group_points=7,actual_suffix_queries=0,solver_calls=0)
    assert result['contract_sha256']==sha(OUT/'contract.json')
    assert read(OUT/'start.json')==dict(frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json'))
    groups=arrays(frozen['inputs']['geometry_groups']['path'],('inverse','multiplicity','source_keys'))
    point=arrays(frozen['inputs']['point_stats']['path'],('query_count','safe_count','maximum_squared','source_keys'))
    group=arrays(frozen['inputs']['group_stats']['path'],('query_count','safe_count','maximum_squared','offsets'))
    inverse=groups['inverse'];assert len(inverse)==171271 and len(groups['multiplicity'])==27817
    assert point['source_keys']==groups['source_keys']
    multiplicities=Counter(inverse)
    assert set(multiplicities)==set(range(27817))
    assert [multiplicities[i] for i in range(27817)]==groups['multiplicity']
    orientation=bytearray();positive=negative=mixed=danger=empty=pospoints=negpoints=0
    for i,g in enumerate(inverse):
        q,s=point['query_count'][i],point['safe_count'][i]
        assert 1<=q<=125 and 0<=s<=q
        assert q==group['query_count'][g] and s==group['safe_count'][g]
        assert point['maximum_squared'][i]==group['maximum_squared'][g]
        bad=q-s;assert (bad>0)==(point['maximum_squared'][i]>40)
        empty+=s==0
        if bad==0:
            orientation.append(0);continue
        danger+=1;positive+=s;negative+=bad;mixed+=min(s,bad)
        if bad<=s:
            orientation.append(2);negpoints+=1
        else:
            orientation.append(1);pospoints+=1
    counts=dict(points=len(inverse),dangerous_points=danger,empty_safe_points=empty,
        all_positive_rows=positive,all_negative_rows=negative,mixed_rows=mixed,
        mixed_positive_points=pospoints,mixed_negative_points=negpoints)
    assert counts==result['point_counts']
    gp=gn=gm=gd=ge=0;weighted=[0,0,0];gpos=gneg=0
    for i,(q,s,m) in enumerate(zip(group['query_count'],group['safe_count'],groups['multiplicity'])):
        assert group['offsets'][i+1]-group['offsets'][i]==s
        bad=q-s;assert 0<=bad<=125
        ge+=s==0
        if not bad:
            continue
        gd+=1;gp+=s;gn+=bad;gm+=min(s,bad)
        gneg+=bad<=s;gpos+=bad>s
        weighted[0]+=m*s;weighted[1]+=m*bad;weighted[2]+=m*min(s,bad)
    assert weighted==[positive,negative,mixed]
    assert result['group_counts']==dict(points=27817,dangerous_points=gd,empty_safe_points=ge,
        all_positive_rows=gp,all_negative_rows=gn,mixed_rows=gm,mixed_positive_points=gpos,mixed_negative_points=gneg)
    saved=(OUT/'orientation-per-point.u8').read_bytes();assert saved==orientation and len(saved)==171271
    assert sha(OUT/'orientation-per-point.u8')==result['orientation']['sha256']
    assert danger==17620 and positive==1525836 and empty==0
    assert gn==52952
    assert result['projected_node_variables']==819 and result['projected_output_variables']==3*danger
    assert result['projected_total_integer_variables']==819+3*danger==53679
    assert result['projected_rounding_rows']==3*danger==52860
    assert result['original_gates']==dict(danger_limit=8192,safe_row_limit=500000,danger_pass=False,positive_rows_pass=False)
    assert result['row_only_observations']==dict(negative_rows_under500000=negative<=500000,mixed_rows_under500000=mixed<=500000)
    assert result['orientation']['bytes']==171271
    assert result['no_new_resource_qualification'] and not result['new_candidate']
    assert result['actual_suffix_queries']==result['solver_calls']==result['native_calls']==result['performance_samples']==0
    verify()
    receipt=dict(passed=True,frozen_sha256=sha(OUT/'frozen.json'),results_sha256=sha(OUT/'results.json'),
        script_sha256=sha(Path(__file__)),points=171271,groups=27817,independent_point_counts=counts,
        weighted_group_counts_equal=True,orientation_equal=True,actual_suffix_queries=0,solver_calls=0,native_calls=0,
        scope='标准库完整读取已有计数/映射及NPY字节；不是新lookup、求解、精度或性能。')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(receipt,flush=True)


if __name__=='__main__':
    main()
