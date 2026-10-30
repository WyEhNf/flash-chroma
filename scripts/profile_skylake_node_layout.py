"""仅剖析固定100图首级节点访问：B连续与R连续的缓存行工作集，不运行映射或测速。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
from lutlab import io


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'bundle', 'output'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args(); plan = read(args.plan)
    bundle = read(args.bundle/'bundle-manifest.json'); out = args.output.resolve()
    if out.exists():
        raise ValueError('不覆盖节点布局剖面')
    for name in ('base', 'sidecar', 'manifest'):
        spec = plan['fixed_inputs'][name]
        if sha(ROOT/spec['path']) != spec['sha256']:
            raise ValueError('固定输入不同：'+name)
    model = io.load_sparse(ROOT/plan['fixed_inputs']['base']['path'], competition=True)
    idx = model.tables()[0]; m = model.m
    fractions = np.fromfile(ROOT/plan['fixed_inputs']['sidecar']['path'], '<u4').reshape(3,3,256)
    photos = read(ROOT/plan['fixed_inputs']['manifest']['path'])['images']
    if len(photos) != 100:
        raise ValueError('不是固定100图')
    offsets = np.arange(0,64,4,dtype=np.uint32)
    sums = {layout: {unit: np.zeros(16,np.int64) for unit in ('packet','block')}
            for layout in ('b_contiguous','r_contiguous')}
    rows = []; source_hash = hashlib.sha256(); total_packets = 0; total_blocks = 0
    with (args.bundle/bundle['photo_pixels']).open('rb') as stream:
        for position, photo in enumerate(photos):
            raw = stream.read(1024*768*3)
            if len(raw) != 1024*768*3 or hashlib.sha256(raw).hexdigest() != photo['evaluation']['pixel_sha256']:
                raise ValueError('照片字节不同')
            source_hash.update(raw); rgb = np.frombuffer(raw,np.uint8).reshape(-1,3)
            cell = np.column_stack([idx[a,rgb[:,a]] for a in range(3)]).astype(np.uint32)
            axes = []
            for c in range(3):
                x,y,z = [fractions[c,a,rgb[:,a]] for a in range(3)]
                # 精确复现现有AVX2实际加载的顶点，包含全相等时的零权重顶点。
                first = np.where(z>np.maximum(x,y),2,np.where(y>x,1,0))
                last = np.where(z<np.minimum(x,y),2,np.where(x>y,1,0))
                axes.append((first,last))
            detail = {}
            for layout,strides in (('b_contiguous',(m*m,m,1)),('r_contiguous',(1,m,m*m))):
                strides = np.asarray(strides,np.uint32); base = cell@strides; diagonal = int(strides.sum())
                access = np.empty((len(rgb),8),np.uint32)
                access[:,0] = base; access[:,1] = base+diagonal
                for c,(first,last) in enumerate(axes):
                    access[:,2+c*2] = base+strides[first]
                    access[:,3+c*2] = base+diagonal-strides[last]
                if access.min() < 0 or access.max() >= m**3:
                    raise ValueError('节点访问越界')
                packets = np.sort(access.reshape(-1,64),axis=1)
                packet_count = np.empty(16,np.int64)
                for i,offset in enumerate(offsets):
                    lines = (packets*4+offset)>>6
                    packet_count[i] = len(lines)+np.count_nonzero(lines[:,1:] != lines[:,:-1])
                block_count = np.zeros(16,np.int64)
                for start in range(0,len(access),4096):
                    nodes = np.unique(access[start:start+4096])
                    lines = (nodes[:,None]*4+offsets[None,:])>>6
                    block_count += 1+np.count_nonzero(lines[1:] != lines[:-1],axis=0)
                for unit,count in (('packet',packet_count),('block',block_count)):
                    sums[layout][unit] += count; detail[layout+'_'+unit+'_lines'] = count.tolist()
            total_packets += len(rgb)//8; total_blocks += (len(rgb)+4095)//4096
            rows.append({'image':photo['id'], **detail})
            if (position+1)%20 == 0:
                print('首级节点布局剖面：',position+1,'/100',flush=True)
        if stream.read(1):
            raise ValueError('照片流有多余字节')
    if source_hash.hexdigest() != bundle['files'][bundle['photo_pixels']]['sha256']:
        raise ValueError('照片总SHA不同')
    ratios = {unit:(sums['r_contiguous'][unit]/sums['b_contiguous'][unit]).tolist()
              for unit in ('packet','block')}
    gate = max(ratios['block']) <= .90 and max(ratios['packet']) <= 1.03
    result = {'purpose':__doc__,'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
              'source_sha256':sha(__file__),'io_source_sha256':sha(ROOT/'python/lutlab/io.py'),
              'plan_sha256':sha(args.plan),'bundle_manifest_sha256':sha(args.bundle/'bundle-manifest.json'),
              'photo_stream_sha256':source_hash.hexdigest(),'grid_m':m,
              'total_packets':total_packets,'total_blocks':total_blocks,'node_gathers_per_packet':8,
              'base_offsets_mod64':offsets.tolist(),'cache_line_bytes':64,
              'gate_before_profile':{'all_block_ratios_at_most':.90,'all_packet_ratios_at_most':1.03},
              'totals':{layout:{unit:counts.tolist() for unit,counts in units.items()} for layout,units in sums.items()},
              'r_contiguous_over_b_contiguous':ratios,'profile_gate_pass':gate,'per_image':rows,
              'project_native_calls':0,'performance_calls':0,'new_fits':0,
              'scope':'仅已见照片首级节点的行并集；不含坐标/图像/后缀流，不模拟LRU、cache miss、GDS或速度；只比较事先选定的R连续，未扫描六种排列。'}
    out.mkdir(); (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ratios':ratios,'profile_gate_pass':gate},ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
