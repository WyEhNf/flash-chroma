"""只读统计R低地址直接ID表的4KiB页覆盖率，不加载原生库或测性能。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import numpy as np
from PIL import Image

def digest(data):return hashlib.sha256(data).hexdigest()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stats(values):return {'min':min(values),'median':statistics.median(values),'max':max(values),'mean':statistics.mean(values)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();plan=json.loads(args.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__).read_bytes())==plan['script_sha256']
    manifest=Path(plan['manifest']['path']).read_bytes();assert digest(manifest)==plan['manifest']['sha256']
    manifest=json.loads(manifest);assert len(manifest['images'])==100
    if args.output.exists():raise FileExistsError('保留已有只读profile，不覆盖或择优重跑')
    args.output.mkdir(parents=True);save(args.output/'executed-plan.json',plan)
    masks={scale:[] for scale in plan['scales']};rows=[];source=hashlib.sha256()
    for row in manifest['images']:
        path=Path(plan['data_root'])/row['evaluation']['path'];assert digest(path.read_bytes())==row['evaluation']['sha256']
        with Image.open(path) as image:frame=np.asarray(image)
        assert frame.shape==(768,1024,3) and frame.dtype==np.uint8
        assert digest(frame.tobytes())==row['evaluation']['pixel_sha256'];source.update(frame.tobytes())
        for scale in plan['scales']:
            photo=frame[::scale,::scale]
            # 字节地址为R|(G<<8)|(B<<16)，一页4096颜色，只需G/B即可求页号。
            gb=photo[:,:,1].astype(np.uint16)|(photo[:,:,2].astype(np.uint16)<<8);pages=gb>>4
            # 独立按全RGB地址>>12校验，与原生候选的半字取页公式分开。
            code=photo[:,:,0].astype(np.uint32)|(photo[:,:,1].astype(np.uint32)<<8)|(photo[:,:,2].astype(np.uint32)<<16)
            assert np.array_equal(pages,code>>12)
            present=np.bincount(pages.reshape(-1),minlength=4096)>0;assert present.size==4096
            masks[scale].append(present)
            rows.append({'id':row['id'],'scale':scale,'pixels':photo.size//3,'page_count':int(present.sum()),
                'page_fraction':float(present.mean()),'required_id_bytes':int(present.sum())*4096,
                'photo_pixel_sha256':digest(photo.tobytes())})
    assert source.hexdigest()==plan['source_sha256']
    all_masks=np.stack([np.stack(masks[s]) for s in plan['scales']]);bits=np.packbits(all_masks,axis=2,bitorder='little').tobytes()
    (args.output/'present-pages.bin').write_bytes(bits);summary=[]
    for scale in plan['scales']:
        stack=np.stack(masks[scale]);counts=stack.sum(axis=1).astype(int).tolist();prefix=[];groups=[]
        for n in plan['prefix_images']:
            union=np.any(stack[:n],axis=0);prefix.append({'images':n,'pages':int(union.sum()),'fraction':float(union.mean()),
                'required_id_bytes':int(union.sum())*4096,'compile_colors':int(union.sum())*4096,'uncompiled_colors':int((~union).sum())*4096,
                'input_pixels':n*1024*768//scale**2,'logical_gb_load_bytes':n*1024*768//scale**2*2,
                'naive_presence_stores':n*1024*768//scale**2,'source_cache_line_span_bytes':n*1024*768//scale**2*3})
        for begin in range(0,100,10):
            union=np.any(stack[begin:begin+10],axis=0);groups.append({'begin_image':begin,'images':10,'pages':int(union.sum()),'fraction':float(union.mean())})
        summary.append({'scale':scale,'individual_page_counts':stats(counts),'prefix':prefix,'fixed_ten_image_groups':groups})
    result={'native_loaded':False,'performance_claim':False,'source_sha256':source.hexdigest(),'page_bytes':4096,'pages':4096,
        'colors_per_page':4096,'bitmap':{'path':'present-pages.bin','sha256':digest(bits),'bytes':len(bits),
            'shape':[len(plan['scales']),100,4096],'order':'scale、manifest图序、低位优先packbits'},
        'summary':summary,'per_image':rows,'scan_budget':plan['scan_budget'],
        'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'scope':'精确输入页覆盖与逻辑扫描预算，不是速度或ready延迟；不实现lazy并发、后台补全或新像素内核。'}
    save(args.output/'results.json',result)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
