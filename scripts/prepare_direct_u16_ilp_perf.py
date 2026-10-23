"""只生成288八角色正式计划/驱动/独立checker；不执行映射、拟合或性能。"""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('唯一源码标记失配：'+old)
    return text.replace(old,new,1)


def main():
    destinations=['experiments/p16-direct-u16-ilp-perf-v1.json','scripts/run_direct_u16_ilp_perf.py','scripts/check_direct_u16_ilp_perf.py']
    if any((ROOT/p).exists() for p in destinations):raise ValueError('不覆盖八角色源/计划')
    plan=json.loads((ROOT/'experiments/p16-direct-u16-perf-v1.json').read_text(encoding='utf-8'))
    quality=json.loads((ROOT/'artifacts/p16-direct-u16-ilp-quality-v1/results.json').read_text(encoding='utf-8'))
    assert quality['passed']
    plan['schema']='p16_direct_u16_ilp_perf_v1'
    plan['scope']='八角色同场：87a399/87old，288a399/288old，287max/p99及288max/p99。保持全部raw/AA/失败，不补跑挑样。'
    plan['roles']=['87a399','87old','288a399','288old','287max','287p99','288max','288p99']
    plan['group_order']=[r+'A' for r in plan['roles']]+[r+'B' for r in reversed(plan['roles'])]
    plan['comparisons']=[['87a399','288a399'],['87old','288old'],['87a399','288old'],['87a399','288max'],['87a399','288p99'],
        ['87old','288max'],['87old','288p99'],['288old','288max'],['288old','288p99'],['287max','288max'],['287p99','288p99']]
    plan['legacy_287_sha256']=plan['library_sha256'];plan['library_sha256']=quality['library_sha256']
    plan['quality_frozen_sha256']=hashlib.sha256((ROOT/'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json').read_bytes()).hexdigest()
    plan['candidate_gate']='288max/p99分别对87a399、87old、288old三分母，最劣>=50且全部对应AA通过；原87基线不可省。288/287同模型因果对照只用本场，不与旧31%相除。'
    plan['prepare_scope']=plan['prepare_scope'].replace('六角色','八角色')
    plan['memory']='287/288同模型直接表/palette逐字节相等、capacity相等、prepare/vector相同；分别记录实际mod64。8角色同时驻留，加完整百图source/work；实际RSS已独立进程观察，不以该单模型峰冒充八角色perf峰。'
    (ROOT/destinations[0]).write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    text=(ROOT/'scripts/run_direct_u16_perf.py').read_text(encoding='utf-8')
    text=text.replace('六角色','八角色').replace('from check_direct_u16_native import info','from check_direct_u16_ilp_native import info')
    text=text.replace('p16-direct-u16-frozen-v2','p16-direct-u16-ilp-frozen-v1').replace('p16-direct-u16-perf-v1.json','p16-direct-u16-ilp-perf-v1.json')
    text=text.replace('p16-direct-u16-quality-v1','p16-direct-u16-ilp-quality-v1')
    old="return {'87a399':(87,a399),'87old':(87,specs['old_best']),'287a399':(287,a399),'287old':(287,specs['old_best']),\n        '287max':(287,specs['max_first']),'287p99':(287,specs['p99_first'])}"
    new="return {'87a399':(87,a399),'87old':(87,specs['old_best']),'288a399':(288,a399),'288old':(288,specs['old_best']),\n        '287max':(287,specs['max_first']),'287p99':(287,specs['p99_first']),\n        '288max':(288,specs['max_first']),'288p99':(288,specs['p99_first'])}"
    text=once(text,old,new)
    text=once(text,"287:Library(ROOT/'artifacts/p16-direct-u16-build-v1/libjshc_direct_u16.dll',plan['library_sha256'])}",
        "287:Library(ROOT/'artifacts/p16-direct-u16-build-v1/libjshc_direct_u16.dll',plan['legacy_287_sha256']),288:Library(ROOT/'artifacts/p16-direct-u16-ilp-build-v1/libjshc_direct_u16_ilp.dll',plan['library_sha256'])}")
    text=text.replace("str((ROOT/'artifacts/p16-direct-u16-build-v1').resolve())","str((ROOT/'artifacts/p16-direct-u16-ilp-build-v1').resolve())")
    text=text.replace("info(c) if revision==287 else None","info(c) if revision!=87 else None")
    text=text.replace("('87a399','87old','287old')","('87a399','87old','288old')")
    text=text.replace("for role in ('287max','287p99')","for role in ('288max','288p99')")
    text=text.replace("'scripts/check_direct_u16_native.py'","'scripts/check_direct_u16_ilp_native.py'")
    (ROOT/destinations[1]).write_text(text,encoding='utf-8',newline='\n')
    text=(ROOT/'scripts/check_direct_u16_perf.py').read_text(encoding='utf-8').replace('六角色','八角色')
    text=text.replace("len(raw['groups'])==48","len(raw['groups'])==64").replace("len(raw['prepare'])==6","len(raw['prepare'])==8")
    text=text.replace('len(aa)==144 and len(comparisons)==432','len(aa)==192 and len(comparisons)==528').replace("'raw_groups':192","'raw_groups':256")
    text=text.replace("('87a399','87old','287old')","('87a399','87old','288old')").replace("for role in ('287max','287p99')","for role in ('288max','288p99')")
    (ROOT/destinations[2]).write_text(text,encoding='utf-8',newline='\n')
    print('288八角色静态源已生成，未执行性能。')


if __name__=='__main__':main()
