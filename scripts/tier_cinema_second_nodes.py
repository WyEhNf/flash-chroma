"""仅从冻结结果计算100%至50%的误差倒数代理精度档，速度保持待测。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def ratio(old,new):
    if old==0:return 1. if new==0 else 0.
    return 1. if new==0 else min(1.,old/new)


def compare(before_cube,before_photo,after):
    records=[]
    for scope,before,now in (('cube',before_cube,after['cube']),('photos_merged',before_photo,after['photos'])):
        for metric in ('mean','p99','max'):
            records.append({'scope':scope,'metric':metric,'before':before[metric],'after':now[metric],
                'retention':ratio(before[metric],now[metric])})
    old_rows={row['image']:row for row in before_photo['per_image']};new_rows={row['image']:row for row in after['photos']['per_image']}
    if set(old_rows)!=set(new_rows) or len(old_rows)!=100:raise AssertionError('照片集合不等')
    for image in sorted(old_rows):
        for metric in ('mean','p99','max'):
            records.append({'scope':'photo/'+image,'metric':metric,'before':old_rows[image][metric],'after':new_rows[image][metric],
                'retention':ratio(old_rows[image][metric],new_rows[image][metric])})
    worst=min(records,key=lambda row:row['retention']);retention=worst['retention']
    return {'retention':retention,'bottleneck':worst,'tiers':{str(percent):retention>=percent/100 for percent in (100,90,80,70,60,50)},
        'records':records,'speed_tiers':None,'scope':'研究用误差倒数代理，非官方评分；未测速度不能宣称联合档。'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True)
    p.add_argument('--accept-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖精度档计算')
    assert ratio(0,0)==1 and ratio(0,1)==0 and ratio(1,0)==1 and ratio(1,2)==.5
    original=json.loads(args.original.read_text(encoding='utf-8'))
    if sha(args.original)!='ec8de74c65ec0252874c7c7e0ee371143ad6cbcfc9ad3dc869a853310912a41f':raise ValueError('原a399结果身份不同')
    original_photo={**original['photos']['merged'],'per_image':original['photos']['per_image']};records={};inputs={str(args.original):sha(args.original)}
    for mode in ('max_first','p99_first'):
        path=args.accept_root/('cinema-second-accept-'+mode+'-v1/results.json');now=json.loads(path.read_text(encoding='utf-8'));inputs[str(path)]=sha(path)
        records[mode]={'versus_a399':compare(original['cube'],original_photo,now),
            'versus_previous_best':compare(now['baseline'],now['baseline_photos'],now)}
    args.output.write_text(json.dumps({'records':records,'source_sha256':sha(Path(__file__)),'inputs_sha256':inputs,
        'policy':'各域/合并照片/100逐图mean,p99,max取min(1,基线误差/候选误差)再取最小；基线0必须候选0；六档逐项给出。未用此表选择节点。'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({mode:{base:{key:value[key] for key in ('retention','bottleneck','tiers')} for base,value in result.items()} for mode,result in records.items()},flush=True)


if __name__=='__main__':main()
