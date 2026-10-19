"""只读固定节点、100图及既有首级输出流，统计精确快路的结构覆盖；无拟合或原生计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
from lutlab import io


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','bundle','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan=read(args.plan);bundle=read(args.bundle/'bundle-manifest.json');out=args.output.resolve()
    if out.exists():raise ValueError('结构剖面输出必须新建')
    paths={k:ROOT/plan['fixed_inputs'][k]['path'] for k in ('model','base','manifest','prior_full')}
    for k,path in paths.items():
        if digest(path)!=plan['fixed_inputs'][k]['sha256']:raise ValueError('固定输入不同：'+k)
    with np.load(paths['model']) as data:
        n=data['nodes'].astype(np.int32);grid=data['grid'];idx=data['shared_idx'].copy()
    if grid.ndim!=2 or grid.shape[0]!=3:raise ValueError('grid必须为3×m')
    m=grid.shape[1]
    if not 17<=m<=33 or n.shape!=(m,m,m,3):raise ValueError('节点/网格维度不符')
    if not np.array_equal(io.load_sparse(paths['base'],competition=True).nodes,n):raise ValueError('SLUT与模型节点不同')
    a=n[:-1,:-1,:-1];r=n[1:,:-1,:-1];g=n[:-1,1:,:-1];b=n[:-1,:-1,1:]
    affine=np.logical_and.reduce([n[1:,1:,:-1]==r+g-a,n[1:,:-1,1:]==r+b-a,
        n[:-1,1:,1:]==g+b-a,n[1:,1:,1:]==r+g+b-2*a])
    mask=np.sum(affine.astype(np.uint8)*np.array([1,2,4],np.uint8),axis=-1)
    w=[np.bincount(idx[k],minlength=m)[:m-1].astype(np.int64) for k in range(3)]
    volume=w[0][:,None,None]*w[1][None,:,None]*w[2][None,None,:]
    if int(volume.sum())!=256**3:raise ValueError('输入单元权重未覆盖整个RGB8')
    cells=[{'channel_mask':k,'cells':int(np.count_nonzero(mask==k)),'rgb8_inputs':int(volume[mask==k].sum())} for k in range(8)]
    first=args.bundle/bundle['single_oracle_stream'];first_sha=digest(first)
    if first_sha!=bundle['files'][bundle['single_oracle_stream']]['sha256'] or first_sha!=read(paths['prior_full'])['native']['cube_sha256']['single_oracle']:
        raise ValueError('首级预期流不是已验同一模型')
    source=args.bundle/bundle['photo_pixels'];expected_source=bundle['files'][bundle['photo_pixels']]['sha256']
    truth=np.memmap(first,np.uint8,'r',shape=(256**3,3));photos=read(paths['manifest'])['images'];frames=[];h=hashlib.sha256()
    if len(photos)!=100:raise ValueError('不是固定100图')
    with source.open('rb') as stream:
        for row in photos:
            raw=stream.read(1024*768*3)
            if len(raw)!=1024*768*3 or hashlib.sha256(raw).hexdigest()!=row['evaluation']['pixel_sha256']:raise ValueError('照片字节不同')
            h.update(raw);rgb=np.frombuffer(raw,np.uint8).reshape(-1,3)
            flags=mask[idx[0,rgb[:,0]],idx[1,rgb[:,1]],idx[2,rgb[:,2]]]==7
            key=(rgb[:,0].astype(np.int64)<<16)|(rgb[:,1].astype(np.int64)<<8)|rgb[:,2]
            intermediate=truth[key];after=(intermediate[:,0].astype(np.uint32)<<16)|(intermediate[:,1].astype(np.uint32)<<8)|intermediate[:,2]
            hist=[]
            for values in (key,after):
                sorted_values=np.sort(values.reshape(-1,8),axis=1)
                distinct=1+(sorted_values[:,1:]!=sorted_values[:,:-1]).sum(axis=1)
                hist.append(np.bincount(distinct,minlength=9)[1:].tolist())
            frames.append({'image':row['id'],'pixels':len(rgb),'packets':len(rgb)//8,'affine_pixels':int(flags.sum()),
                'all_eight_affine_packets':int(flags.reshape(-1,8).all(axis=1).sum()),
                'input_distinct_color_histogram_1_to_8':hist[0],'post_first_distinct_color_histogram_1_to_8':hist[1]})
        if stream.read(1):raise ValueError('照片流含额外数据')
    if h.hexdigest()!=expected_source:raise ValueError('照片总SHA不同')
    total=sum(f['packets'] for f in frames);out.mkdir()
    result={'purpose':__doc__,'model_sha256':plan['fixed_inputs']['model']['sha256'],'first_stream_sha256':first_sha,
        'photo_stream_sha256':h.hexdigest(),'source_sha256':digest(Path(__file__)),'plan_sha256':digest(args.plan),
        'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
        'm':m,'cell_count':(m-1)**3,'cell_channel_masks':cells,'all_three_affine_uniform_rgb8_fraction':cells[7]['rgb8_inputs']/256**3,
        'per_image':frames,'total_packets':total,
        'all_eight_affine_photo_fraction':sum(f['all_eight_affine_packets'] for f in frames)/total,
        'input_all_eight_equal_fraction':sum(f['input_distinct_color_histogram_1_to_8'][0] for f in frames)/total,
        'post_first_all_eight_equal_fraction':sum(f['post_first_distinct_color_histogram_1_to_8'][0] for f in frames)/total,
        'project_native_calls':0,'performance_calls':0,'new_fits':0,
        'scope':'已见数据的结构覆盖，复用首级已验流查询；不生成新模型或时间收益，不作为独立精度验收。包尺寸固定8。'}
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('all_three_affine_uniform_rgb8_fraction','all_eight_affine_photo_fraction',
        'input_all_eight_equal_fraction','post_first_all_eight_equal_fraction')},ensure_ascii=False))


if __name__=='__main__':main()
