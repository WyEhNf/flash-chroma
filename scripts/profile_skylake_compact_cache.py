"""只读已验首级流、后缀金标准和固定100图，统计R连续基础上的无损半字组合资格及工作集；不调用新内核或计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('plan','bundle','gold','output'):p.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();plan=read(args.plan);bundle=read(args.bundle/'bundle-manifest.json');gold=read(args.gold/'generation.json')
    out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖已有剖面')
    for name in ('model','base','manifest'):
        spec=plan['fixed_inputs'][name]
        if digest(ROOT/spec['path'])!=spec['sha256']:raise ValueError('固定输入不同：'+name)
    if gold['inputs']['base']!=plan['fixed_inputs']['base'] or gold['inputs']['suffix']!=plan['suffix_models']:
        raise ValueError('缓存金标准不是固定四级模型')
    table=args.gold/'cache-gold.u32'
    if digest(table)!=gold['gold_sha256']:raise ValueError('缓存金标准字节不同')
    values=np.fromfile(table,dtype='<u4');bounds=gold['bounds'];entries=gold['entries']
    if len(values)!=entries or np.any(values>>24):raise ValueError('需要RGB24金标准')
    colours=np.column_stack((values&255,(values>>8)&255,values>>16)).astype(np.int32)
    differences=colours[:,1:]-colours[:,0,None];minimum=differences.min(axis=0);maximum=differences.max(axis=0)
    if np.any(maximum-minimum>15):raise ValueError('本方案要求整表两个通道差跨度均不超过15；未做位宽扫描')
    encoded=colours[:,0].astype(np.uint32)|((differences[:,0]-minimum[0]).astype(np.uint32)<<8)|((differences[:,1]-minimum[1]).astype(np.uint32)<<12)
    decoded=np.column_stack((encoded&255,(encoded&255)+((encoded>>8)&15).astype(np.int32)+minimum[0],
        (encoded&255)+((encoded>>12)&15).astype(np.int32)+minimum[1])).astype(np.uint32)
    if not np.array_equal(decoded,colours):raise ValueError('独立数学编码不能精确恢复整表')
    first=args.bundle/bundle['single_oracle_stream'];source=args.bundle/bundle['photo_pixels']
    if digest(first)!=bundle['files'][bundle['single_oracle_stream']]['sha256']:raise ValueError('首级已验流不同')
    truth=np.memmap(first,np.uint8,'r',shape=(256**3,3));photos=read(ROOT/plan['fixed_inputs']['manifest']['path'])['images']
    if len(photos)!=100:raise ValueError('需要原固定100图')
    offsets=np.arange(0,64,4,dtype=np.uint32);wg=bounds['dg_max']-bounds['dg_min']+1;wb=bounds['db_max']-bounds['db_min']+1
    rows=[];source_hash=hashlib.sha256();sums={name:np.zeros(16,np.int64) for name in ('r_contiguous_packet_lines','r_contiguous_u16_packet_lines','r_contiguous_block_lines','r_contiguous_u16_block_lines')}
    total_blocks=0;total_packets=0;hist=np.zeros(entries,np.int64)
    with source.open('rb') as stream:
        for position,row in enumerate(photos):
            raw=stream.read(1024*768*3)
            if len(raw)!=1024*768*3 or hashlib.sha256(raw).hexdigest()!=row['evaluation']['pixel_sha256']:raise ValueError('照片像素不符')
            source_hash.update(raw);rgb=np.frombuffer(raw,np.uint8).reshape(-1,3)
            keys=(rgb[:,0].astype(np.int64)<<16)|(rgb[:,1].astype(np.int64)<<8)|rgb[:,2]
            x=truth[keys].astype(np.int32);r=x[:,0];dg=x[:,1]-r;db=x[:,2]-r
            if not ((r>=bounds['r_min'])&(r<=bounds['r_max'])&(dg>=bounds['dg_min'])&(dg<=bounds['dg_max'])&(db>=bounds['db_min'])&(db<=bounds['db_max'])).all():
                raise ValueError('固定照片出现未命中，剖面不可假定全部命中')
            index=((r-bounds['r_min'])*wg*wb+(dg-bounds['dg_min'])*wb+db-bounds['db_min']).astype(np.uint32)
            hist+=np.bincount(index,minlength=entries)
            alternate=((db-bounds['db_min'])*wg+(dg-bounds['dg_min']))*(bounds['r_max']-bounds['r_min']+1)+(r-bounds['r_min'])
            ordered=np.sort(index.reshape(-1,8),axis=1);other=np.sort(alternate.reshape(-1,8),axis=1);detail={};total_packets+=len(ordered)
            for name,word in (('r_contiguous',other),('r_contiguous_u16',other>>1)):
                starts=word*4;counts=np.empty(16,np.int64)
                for i,offset in enumerate(offsets):
                    lines=(starts+offset)>>6;counts[i]=len(lines)+np.count_nonzero(lines[:,1:]!=lines[:,:-1])
                sums[name+'_packet_lines']+=counts;detail[name+'_packet_lines_by_base_offset']=counts.tolist()
            block_counts={name:np.zeros(16,np.int64) for name in ('r_contiguous','r_contiguous_u16')}
            for start in range(0,len(index),4096):
                ordered=np.unique(index[start:start+4096]);total_blocks+=1
                other=np.unique(alternate[start:start+4096]).astype(np.uint32)
                for name,word in (('r_contiguous',other),('r_contiguous_u16',other>>1)):
                    lines=(word[:,None]*4+offsets[None,:])>>6
                    block_counts[name]+=1+np.count_nonzero(lines[1:]!=lines[:-1],axis=0)
            for name,count in block_counts.items():
                sums[name+'_block_lines']+=count;detail[name+'_block_lines_by_base_offset']=count.tolist()
            rows.append({'image':row['id'],'pixels':len(index),'packets':len(index)//8,'blocks':(len(index)+4095)//4096,
                'distinct_keys':int(np.count_nonzero(np.bincount(index,minlength=entries))),**detail})
            if (position+1)%20==0:print('固定照片访问剖面：',position+1,'/100',flush=True)
        if stream.read(1):raise ValueError('照片流多余字节')
    if source_hash.hexdigest()!=bundle['files'][bundle['photo_pixels']]['sha256']:raise ValueError('照片流总SHA不同')
    result={'purpose':__doc__,'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'source_sha256':digest(__file__),'plan_sha256':digest(args.plan),'bundle_manifest_sha256':digest(args.bundle/'bundle-manifest.json'),
        'gold_generation_sha256':digest(args.gold/'generation.json'),'gold_sha256':digest(table),'first_stream_sha256':digest(first),'photo_stream_sha256':source_hash.hexdigest(),
        'bounds':bounds,'entries':entries,'output_differences_min':minimum.tolist(),'output_differences_max':maximum.tolist(),
        'encoding':'R8 | ((G-R-gmin)<<8) | ((B-R-bmin)<<12)，每个差字段4位；两个16位记录放一个u32，索引右移一位gather再选高/低半字',
        'unique_outputs':int(len(np.unique(values))),'original_table_bytes':entries*4,'halfword_table_bytes':((entries+1)//2)*4,
        'independent_encoding_roundtrip_mismatches':0,'total_packets':total_packets,'total_blocks':total_blocks,
        'cache_line_model_bytes':64,'base_offsets_mod64':offsets.tolist(),'totals':{k:v.tolist() for k,v in sums.items()},
        'packet_line_ratio_u16_over_r_contiguous':(sums['r_contiguous_u16_packet_lines']/sums['r_contiguous_packet_lines']).tolist(),
        'block_line_ratio_u16_over_r_contiguous':(sums['r_contiguous_u16_block_lines']/sums['r_contiguous_block_lines']).tolist(),
        'r_contiguous_table_bytes':entries*4,'accessed_keys':int(np.count_nonzero(hist)),'per_image':rows,'project_native_calls':0,'performance_calls':0,'new_fits':0,
        'scope':'已见固定照片访问结构，不模拟LRU/真实命中/PMU/GDS或速度；覆盖所有u32自然对齐的16种基址余数。字典/24位方案仅不选，未扫描位宽。'}
    out.mkdir();(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('output_differences_min','output_differences_max','original_table_bytes','halfword_table_bytes',
        'accessed_keys','packet_line_ratio_u16_over_r_contiguous','block_line_ratio_u16_over_r_contiguous')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
