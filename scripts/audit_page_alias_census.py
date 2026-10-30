"""按封存pageID独立重放原字节及频数，不重新归类页、不部署映射。"""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);a=p.parse_args();plan_path=ROOT/'experiments/page-alias-census-v1.json';plan=read(plan_path);result=read(a.input/'results.json');support=read(a.input/'support.json')
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or result['plan_sha256']!=sha(plan_path) or result['support_sha256']!=sha(a.input/'support.json'):raise AssertionError('冻结源/原件身份不同')
    ids=support['page_ids'];unique=len(support['unique_page_sha256']);classes=[None]*unique;counts=[0]*unique;first=[];digest=hashlib.sha256();source=hashlib.sha256();finite=0
    if len(ids)!=4096 or unique!=3082:raise AssertionError('封存页数不符')
    with Path(plan['rom']).open('rb') as stream:
        header=stream.read(1056);source.update(header)
        for page,identifier in enumerate(ids):
            raw=stream.read(4096);source.update(raw);digest.update(raw)
            if len(raw)!=4096 or not 0<=identifier<unique or hashlib.sha256(raw).hexdigest()!=support['unique_page_sha256'][identifier]:raise AssertionError('封存页身份不同')
            if classes[identifier] is None:classes[identifier]=raw;first.append(identifier)
            elif classes[identifier]!=raw:raise AssertionError('相同ID实际byte不同')
            counts[identifier]+=1
            probes=bytes.fromhex(support['source_page_probe_hex'][page])
            for index,offset in enumerate((0,1,4094,4095)):
                code=page*4096+offset
                if classes[ids[code>>12]][code&4095]!=probes[index] or 4096+code!=(page+1)*4096+offset:raise AssertionError('独立位移/有限byte重放不同')
                finite+=1
        if stream.read(1):raise AssertionError('源多余字节')
    replay=hashlib.sha256()
    for identifier in ids:replay.update(classes[identifier])
    if first!=list(range(unique)) or counts!=support['unique_page_references'] or sum(counts)!=4096 or source.hexdigest()!=plan['rom_sha256'] or digest.hexdigest()!=plan['logical_id_sha256'] or replay.hexdigest()!=plan['logical_id_sha256']:raise AssertionError('首次顺序/频数/完整摘要不同')
    owner=result['owner_state_bytes'];backing=4096+4*4096+4096*unique;total=backing+owner+1056;saving=16779328-total
    if owner!=48 or result['owner_offsets']!={'file':0,'section':8,'base':16,'span':24,'mapped_pages':32,'split_pages':36,'state':40,'reserved':44} or result['backing_bytes']!=backing or result['projected_total_bytes']!=total or result['net_backing_saving_bytes']!=saving or result['gate_pass']!=(saving>=1048576) or finite!=result['finite_contracts'] or result['invalid_codes_rejected']!=2:raise AssertionError('原型/容量/合同门槛不同')
    value=dict(passed=True,purpose=__doc__,plan_sha256=sha(plan_path),results_sha256=sha(a.input/'results.json'),support_sha256=sha(a.input/'support.json'),source_rom_sha256=source.hexdigest(),logical_id_sha256=replay.hexdigest(),unique_pages=unique,references=sum(counts),finite_contracts=finite,backing_bytes=backing,projected_model_owner_backing_bytes=total,net_backing_saving_bytes=saving,gate_pass=saving>=1048576,scope='只按既有pageID核原字节，不重新选择页尺寸/分类；没有部署/物理RAM/WS或速度结论。')
    (a.input/'offline-audit.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(value)
if __name__=='__main__':main()
