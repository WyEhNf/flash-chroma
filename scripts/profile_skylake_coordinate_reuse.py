"""只读固定坐标与100图，统计稳定四面体排序一致覆盖及共享ONE端点编码资格，不拟合/调用原生/计时。"""
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
    for n in ('plan','bundle','output'):p.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();plan=read(args.plan);bundle=read(args.bundle/'bundle-manifest.json');out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖坐标剖面')
    specs={k:plan['fixed_inputs'][k] for k in ('sidecar','base','model','manifest')}
    for k,s in specs.items():
        if digest(ROOT/s['path'])!=s['sha256']:raise ValueError('固定模型不同：'+k)
    f=np.fromfile(ROOT/specs['sidecar']['path'],dtype='<u4').reshape(3,3,256)
    if np.any(f>65536) or np.any(f[:,:,0]) or np.any(f[:,:,255]!=65536):raise ValueError('Q16数据范围/端点不符')
    one=f==65536;bad=(one[1]!=one[0])|(one[2]!=one[0]);endpoint_eligible=not bad.any()
    packed=(f[1]&65535)|((f[2]&65535)<<16);end=f[0]&65536
    expanded=np.stack((f[0],(packed&65535)|end,(packed>>16)|end))
    endpoint={'eligible':endpoint_eligible,'common_one_mismatched_axis_codes':int(bad.sum()),'one_counts_channel_axis':one.sum(axis=2).tolist(),
        'frac65535_counts_channel_axis':(f==65535).sum(axis=2).tolist(),'mathematical_expansion_mismatches':int(np.count_nonzero(expanded!=f)),
        'encoding':'R保留原17位fraction/idx；另一个u32存G16/B16，若三通道ONE掩码逐轴逐码相同，则R的bit16可恢复两通道17位值',
        'simd_proposal':'G用VPBLENDW(pair, Rword&65536, 0xAA)，B用(pair>>16)|(Rword&65536)；不假设65535缺失',
        'scope':'共享端点标志不等于共享三通道坐标或顶点排序；这不是新C++实现验证'}
    if endpoint_eligible and endpoint['mathematical_expansion_mismatches']:raise ValueError('端点条件或数学推导有错')
    photos=read(ROOT/specs['manifest']['path'])['images'];source=args.bundle/bundle['photo_pixels'];h=hashlib.sha256();rows=[]
    if len(photos)!=100:raise ValueError('必须是固定100图')
    total_pixels=0;total_packets=0;good_pixels=0;good_packets=0;all_hist=np.zeros((3,8),np.int64);first_counterexample=None
    with source.open('rb') as stream:
        for position,row in enumerate(photos):
            raw=stream.read(1024*768*3)
            if len(raw)!=1024*768*3 or hashlib.sha256(raw).hexdigest()!=row['evaluation']['pixel_sha256']:raise ValueError('照片字节不同')
            h.update(raw);rgb=np.frombuffer(raw,np.uint8).reshape(-1,3);classes=[];hist=[]
            for c in range(3):
                x=f[c,0,rgb[:,0]];y=f[c,1,rgb[:,1]];z=f[c,2,rgb[:,2]]
                key=(y>x).astype(np.uint8)|((z>x).astype(np.uint8)<<1)|((z>y).astype(np.uint8)<<2)
                count=np.bincount(key,minlength=8);all_hist[c]+=count;hist.append(count.tolist());classes.append(key)
            agree=(classes[0]==classes[1])&(classes[0]==classes[2]);packets=agree.reshape(-1,8).all(axis=1)
            a=int(agree.sum());b=int(packets.sum());good_pixels+=a;good_packets+=b;total_pixels+=len(rgb);total_packets+=len(packets)
            if first_counterexample is None and not agree.all():
                i=int(np.flatnonzero(~agree)[0]);point=rgb[i].tolist()
                first_counterexample={'image':row['id'],'pixel_index':i,'rgb':point,'classes':[int(v[i]) for v in classes],
                    'fractions_channel_axis':[[int(f[c,axis,point[axis]]) for axis in range(3)] for c in range(3)]}
            rows.append({'image':row['id'],'pixels':len(rgb),'packets':len(packets),'same_order_pixels':a,'all_eight_same_order_packets':b,
                'same_order_pixel_fraction':a/len(rgb),'same_order_packet_fraction':b/len(packets),'class_histograms':hist})
            if (position+1)%20==0:print('固定坐标覆盖：',position+1,'/100',flush=True)
        if stream.read(1):raise ValueError('照片流有额外字节')
    if h.hexdigest()!=bundle['files'][bundle['photo_pixels']]['sha256']:raise ValueError('照片总SHA不同')
    value={'purpose':__doc__,'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'source_sha256':digest(__file__),'plan_sha256':digest(args.plan),'sidecar_sha256':specs['sidecar']['sha256'],'photo_stream_sha256':h.hexdigest(),
        'stable_tie_priority':'R优先于G优先于B，使用(y>x,z>x,z>y)三位分类；共享时必须按稳定优先级构造首/末轴，不能直接复用旧全相等时首末可能同轴的几何结果',
        'geometry_profile_gate_before_native':.60,'endpoint_profile':endpoint,'total_pixels':total_pixels,'total_packets':total_packets,
        'same_order_pixel_fraction':good_pixels/total_pixels,'same_order_packet_fraction':good_packets/total_packets,
        'geometry_profile_gate_pass':good_packets/total_packets>=.60,'class_histograms':all_hist.tolist(),'first_order_counterexample':first_counterexample,
        'per_image':rows,'project_native_calls':0,'performance_calls':0,'new_fits':0,
        'scope':'已见照片的确定性结构剖面，不是时间收益、全色域质量或新实现正确性，不扫描覆盖门槛/排序规则。'}
    out.mkdir();(out/'results.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:value[k] for k in ('endpoint_profile','same_order_pixel_fraction','same_order_packet_fraction','geometry_profile_gate_pass','first_order_counterexample')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
