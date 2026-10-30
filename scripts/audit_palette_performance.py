"""从全部原始轮次独立核对7bit性能摘要、控制和36格资格，不运行内核。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import statistics


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--performance',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('拒绝覆盖回执')
    summary=read(args.performance/'summary.json');workers=[read(args.performance/f'worker-{i}/results.json') for i in range(4)]
    source={str(path.relative_to(args.performance)):hashlib.sha256(path.read_bytes()).hexdigest() for path in args.performance.rglob('*.json')}
    execution=read(args.performance/'execution.json');assert len(execution)==10 and all(row['returncode']==0 for row in execution)
    ratios=[]
    for mode in ['inplace','outplace']:
        for threads in [1,4]:
            control=[];tables=[]
            for worker in workers:
                assert len(worker['rows'])==24 and len(worker['controls'])==4
                rows=[row for row in worker['rows'] if row['mode']==mode and row['threads']==threads]
                assert len(rows)==6
                for row in rows:
                    assert len(row['seconds'])==5 and min(row['seconds'])>0
                    assert statistics.median(row['seconds'])==row['median_seconds']
                table={row['role']:statistics.median(row['seconds']) for row in rows};tables.append(table)
                end=next(row for row in worker['controls'] if row['mode']==mode and row['threads']==threads)
                assert len(end['seconds'])==5
                value=statistics.median(end['seconds'])/table['ref80'];assert abs(value-end['ratio'])<1e-12;control.append(value)
            passed=all(.8<=value<=1.25 for value in control) and 1/1.1<=statistics.median(control)<=1.1
            original=summary['controls'][f'{mode}_{threads}'];assert original['values']==control and original['passed']==passed
            for role in ['exact_avx','ward_avx','maximin_avx','ward_c99']:
                values=[min(table['ref78'],table['ref80'])/table[role] for table in tables]
                original=next(row for row in summary['comparisons'] if row['role']==role and row['mode']==mode and row['threads']==threads)
                assert original['per_worker']==values and abs(original['speed_worst']-min(values))<1e-12
                assert abs(original['speed_median']-statistics.median(values))<1e-12 and original['control_passed']==passed
                ratios.append(original)
            cases=[row for row in ratios if row['mode']==mode and row['threads']==threads]
            for quality in [100,90,80,70,60,50]:
                for speed in [100,90,80,70,60,50]:
                    eligible=[row for row in cases if passed and row['accuracy_retention']+1e-12>=quality/100 and row['speed_worst']+1e-12>=speed/100]
                    expected=min(eligible,key=lambda row:row['resident_capacity'],default=None)
                    assert summary['grids'][f'{mode}_{threads}'][f'accuracy{quality}_speed{speed}']==expected
    result=dict(passed=True,raw_json_sha256=source,workers=4,primary_raw_rounds=4*24*5,control_raw_rounds=4*4*5,comparison_points=16,grid_cells=144,
        all_conditions={role:dict(speed_worst=min(row['speed_worst'] for row in ratios if row['role']==role),
            accuracy_retention=next(row['accuracy_retention'] for row in ratios if row['role']==role)) for role in ['exact_avx','ward_avx','maximin_avx','ward_c99']},
        limits='只独立复算已冻结原始时间/A/A/资格；不重跑映射、不新增性能观测。质量比例来自独立质量审计，另有918组记录复算。')
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('480主轮次、80控制轮次、16比较点、144格资格独立复算通过')


if __name__=='__main__':main()
