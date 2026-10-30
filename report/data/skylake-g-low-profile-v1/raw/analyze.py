"""单次只读G低布局地址统计；不构造原生表、不执行像素映射或计时。"""
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPECS = {
    'photos': ('artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb','e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'),
    'manifest': ('assets/photos/manifest.json','10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c'),
    'prior_R_B_profile': ('artifacts/skylake-lookup-diagnostics-v1/layout-64-window-v1.json','c2acdc53dbccac438fbf5495fde638c33b48309894382c840d59d24dc9788dad'),
}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def swap16(code):
    return (code & np.uint32(0xff0000)) | ((code & np.uint32(255)) << 8) | ((code >> 8) & np.uint32(255))


def counts(code):
    rows = (code >> 6).reshape(-1,64).copy()
    rows.sort(axis=1)
    return 1+np.count_nonzero(rows[:,1:]!=rows[:,:-1],axis=1)


def main():
    if (HERE/'results.json').exists():
        raise ValueError('不得覆盖已执行统计')
    protocol = read(HERE/'protocol.json')
    assert protocol['script_sha256']==digest(Path(__file__))
    assert protocol['gate']=={'mean_lines_ratio_max':0.80,'any_image_lines_ratio_max':1.05}
    inputs = {}
    for name,(relative,expected) in SPECS.items():
        path = ROOT/relative
        assert digest(path)==expected,name
        inputs[name] = {'path':relative,'sha256':expected,'bytes':path.stat().st_size}
    inverse_errors,range_errors,page_errors = 0,0,0
    for first in range(0,2**24,2**20):
        code = np.arange(first,first+2**20,dtype=np.uint32)
        permuted = swap16(code)
        inverse_errors += int(np.count_nonzero(swap16(permuted)!=code))
        range_errors += int(np.count_nonzero(permuted>=2**24))
        page_errors += int(np.count_nonzero((permuted>>21)!=(code>>21)))
    assert inverse_errors==range_errors==page_errors==0
    manifest = read(ROOT/SPECS['manifest'][0])
    assert len(manifest['images'])==100 and inputs['photos']['bytes']==235929600
    photos = np.memmap(ROOT/SPECS['photos'][0],mode='r',dtype=np.uint8,shape=(100,1024*768,3))
    histograms = {'R_low':np.zeros(65,dtype=np.int64),'G_low':np.zeros(65,dtype=np.int64)}
    rows = []
    for i,image in enumerate(photos):
        image_sha = hashlib.sha256(image).hexdigest()
        assert image_sha==manifest['images'][i]['evaluation']['pixel_sha256']
        code = image[:,0].astype(np.uint32) | (image[:,1].astype(np.uint32)<<8) | (image[:,2].astype(np.uint32)<<16)
        old,new = counts(code),counts(swap16(code))
        for key,values in [('R_low',old),('G_low',new)]:
            histograms[key] += np.bincount(values,minlength=65)
        sums = [int(old.sum()),int(new.sum())]
        rows.append({'image':i,'input_sha256':image_sha,'windows':len(old),
                     'R_low_sum_lines':sums[0],'G_low_sum_lines':sums[1],'ratio':sums[1]/sums[0]})
    windows = sum(row['windows'] for row in rows)
    old_sum = sum(row['R_low_sum_lines'] for row in rows)
    new_sum = sum(row['G_low_sum_lines'] for row in rows)
    prior = read(ROOT/SPECS['prior_R_B_profile'][0])
    assert windows==prior['windows']==1228800
    assert old_sum==prior['layouts']['R_low']['sum_unique_64']==60721470
    assert histograms['R_low'].tolist()==prior['layouts']['R_low']['hist_unique_64']
    ratio = new_sum/old_sum
    accepted = ratio<=protocol['gate']['mean_lines_ratio_max'] and max(row['ratio'] for row in rows)<=protocol['gate']['any_image_lines_ratio_max']
    result = {'purpose':__doc__,'pass':True,'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'inputs':inputs,'script_sha256':digest(Path(__file__)),'protocol_sha256':digest(HERE/'protocol.json'),
        'index_colors_checked':2**24,'inverse_mismatches':inverse_errors,'range_mismatches':range_errors,'THP2M_page_mismatches':page_errors,
        'windows':windows,'R_low_mean_unique_lines':old_sum/windows,'G_low_mean_unique_lines':new_sum/windows,
        'G_over_R_mean_lines_ratio':ratio,'maximum_image_ratio':max(row['ratio'] for row in rows),
        'hist_unique_lines':{key:value.tolist() for key,value in histograms.items()},'images':rows,
        'gate':protocol['gate'],'native_implementation_warranted':accepted,
        'decision':'只读门槛通过，仅允许继续研究，不是性能结论' if accepted else '只读门槛失败，停止G低路线，不构造原生或扫其他轴顺序',
        'native_calls':0,'performance_calls':0,'new_fits':0,
        'limits':['缓存行集合不是cache miss/字节带宽/吞吐；不模拟跨窗口替换、线程竞争或真实Skylake',
                  '只试固定G低/R中/B高，不选择最佳参数；另一高轴顺序仅重命名行，无需重复',
                  '16M输入索引自逆/范围证明不是执行全部RGB8映射精度，模型和运行时未改',
                  '拟议索引变换增加指令与依赖；不能从集合减少直接推断净收益']}
    with (HERE/'results.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({key:result[key] for key in ('R_low_mean_unique_lines','G_low_mean_unique_lines','G_over_R_mean_lines_ratio','maximum_image_ratio','native_implementation_warranted','decision')},ensure_ascii=False))


if __name__=='__main__':
    main()
