"""仅用归档页位图独立复算覆盖率，不读照片、不加载原生库。"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args()
    read=lambda n:json.loads((a.source/n).read_text(encoding='utf-8'))
    result=read('results.json');plan=read('executed-plan.json');bits=(a.source/'present-pages.bin').read_bytes()
    assert hashlib.sha256(bits).hexdigest()==result['bitmap']['sha256'] and len(bits)==102400
    counts=[]
    for i,scale in enumerate(plan['scales']):
        masks=[int.from_bytes(bits[(i*100+j)*512:(i*100+j+1)*512],'little') for j in range(100)]
        each=[v.bit_count() for v in masks];counts.extend(each)
        rows=[r for r in result['per_image'] if r['scale']==scale]
        assert [r['page_count'] for r in rows]==each
        assert all(r['page_fraction']==n/4096 and r['required_id_bytes']==n*4096 for r,n in zip(rows,each))
        summary=result['summary'][i];assert summary['individual_page_counts']=={'min':min(each),'median':statistics.median(each),'max':max(each),'mean':statistics.mean(each)}
        def union(begin,n):
            value=0
            for mask in masks[begin:begin+n]:value|=mask
            return value.bit_count()
        for row in summary['prefix']:
            n=row['images'];pages=union(0,n);assert row['pages']==pages and row['fraction']==pages/4096
            assert row['required_id_bytes']==row['compile_colors']==pages*4096
            assert row['uncompiled_colors']==(4096-pages)*4096
            assert row['logical_gb_load_bytes']==row['input_pixels']*2 and row['naive_presence_stores']==row['input_pixels']
        for row in summary['fixed_ten_image_groups']:
            pages=union(row['begin_image'],row['images']);assert pages==row['pages'] and row['fraction']==pages/4096
    print(json.dumps({'bitmap_rows_recomputed':len(counts),'scales':plan['scales'],'source_sha256':result['source_sha256'],
        'prefix_and_fixed_groups_verified':True,'performance_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
