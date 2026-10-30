"""保留固定G低布局唯一只读扫描并复算聚合；不重复扫描或执行原生。"""
import hashlib
import json
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT/'artifacts/skylake-g-low-profile-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    target = HERE/'raw'
    if target.exists():
        raise ValueError('不得覆盖既有统计档案')
    shutil.copytree(SOURCE,target)
    result,protocol = read(target/'results.json'),read(target/'protocol.json')
    assert result['pass'] and not result['native_implementation_warranted']
    assert result['script_sha256']==protocol['script_sha256']==digest(target/'analyze.py')
    assert result['protocol_sha256']==digest(target/'protocol.json')
    assert result['native_calls']==result['performance_calls']==0
    assert result['index_colors_checked']==2**24
    assert result['inverse_mismatches']==result['range_mismatches']==result['THP2M_page_mismatches']==0
    rows = result['images']
    windows = sum(row['windows'] for row in rows)
    old = sum(row['R_low_sum_lines'] for row in rows)
    new = sum(row['G_low_sum_lines'] for row in rows)
    assert len(rows)==100 and windows==1228800 and old==60721470
    assert new/old==result['G_over_R_mean_lines_ratio']
    assert max(row['ratio'] for row in rows)==result['maximum_image_ratio']
    for key,total in [('R_low',old),('G_low',new)]:
        hist = result['hist_unique_lines'][key]
        assert sum(hist)==windows and sum(i*count for i,count in enumerate(hist))==total
    files = {p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(target.rglob('*')) if p.is_file()}
    (HERE/'manifest.json').write_text(json.dumps({'schema':1,'files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'audit.json').write_text(json.dumps({'pass':True,'files':len(files),'global_ratio':new/old,
        'maximum_image_ratio':result['maximum_image_ratio'],'native_implementation_warranted':False,
        'new_scan_calls':0,'native_calls':0,'performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'files':len(files),'global_ratio':new/old},ensure_ascii=False))


if __name__=='__main__':
    main()
