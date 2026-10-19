"""一次静态核对本轮档案清单、Git实际blob原字节和新增文档链接；零数值调用。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
def digest(data):return hashlib.sha256(data).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--prefix',action='append',help='只核对这些名称前缀的档案；不传时保持既有精度交付范围')
    parser.add_argument('--documents',nargs='+',default=[],help='文档清单；传入时替代默认文档清单')
    args=parser.parse_args();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖交付检查')
    base=ROOT/'report/data';folders=[];records=[];documents=[]
    for folder in sorted(base.iterdir()):
        if not folder.is_dir() or folder==out:continue
        if args.prefix:
            if not folder.name.startswith(tuple(args.prefix)):continue
        elif not (folder.name.startswith(('channel-','velvia-channel-','cinema-channel-','cinema-current-anchor-'))
                or folder.name in ('emerald-calibrated-v1','cinema-cap-anchor-diagnosis-v1')):continue
        manifest=folder/'manifest.json'
        if not manifest.exists():continue
        value=json.loads(manifest.read_text(encoding='utf-8'))
        if not isinstance(value.get('files'),dict):raise ValueError('清单结构不适用：'+str(manifest))
        folders.append(folder.name)
        for name,spec in value['files'].items():
            p=folder/name;b=p.read_bytes()
            if digest(b)!=spec['sha256'] or len(b)!=spec['bytes']:raise ValueError('清单字节不同：'+str(p))
            records.append({'path':p.relative_to(ROOT).as_posix(),'sha256':digest(b),'bytes':len(b),'kind':'manifest_entry'})
            if p.suffix=='.md':documents.append(p)
        b=manifest.read_bytes();records.append({'path':manifest.relative_to(ROOT).as_posix(),'sha256':digest(b),'bytes':len(b),'kind':'manifest'})
    payload=''.join(':'+r['path']+'\n' for r in records).encode('utf-8')
    proc=subprocess.run(['git','cat-file','--batch'],input=payload,capture_output=True,cwd=ROOT,check=True)
    position=0
    for r in records:
        end=proc.stdout.index(b'\n',position);header=proc.stdout[position:end].split();position=end+1
        if len(header)!=3 or header[1]!=b'blob':raise ValueError('缺暂存blob：'+r['path'])
        size=int(header[2]);blob=proc.stdout[position:position+size];position+=size+1
        if len(blob)!=r['bytes'] or digest(blob)!=r['sha256']:raise ValueError('Git换行/交付字节不同：'+r['path'])
        r['git_blob_sha256']=digest(blob)
    if position!=len(proc.stdout):raise ValueError('Git批回执尾部不完整')
    documents += [ROOT/n for n in args.documents] if args.documents else [ROOT/'docs/README.md',ROOT/'report/data/DATA_INDEX.md',
        *[ROOT/'docs/stages'/n for n in ('2026-10-19-precision-latest.md','2026-10-19-cinema-current-anchor-accept.md',
            '2026-10-19-channel-runtime-specialized.md','2026-10-19-cinema-cap-anchor-diagnosis.md')]]
    links=[]
    for p in sorted(set(documents)):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if target.startswith(('https:','http:','#','mailto:')):continue
            path=unquote(target.strip('<>').split('#')[0])
            if not path:continue
            resolved=(p.parent/path).resolve()
            if not resolved.exists():raise ValueError('文档相对链接缺失：'+str(p)+' → '+target)
            links.append({'document':p.relative_to(ROOT).as_posix(),'target':target})
    out.mkdir(parents=True)
    record={'purpose':__doc__,'pass':True,'environment':{'python':sys.version,'platform':platform.platform(),
        'git':subprocess.check_output(['git','--version'],cwd=ROOT,text=True).strip(),
        'compiler_backend_threads':'不适用：只读标准库/文件与Git对象，没有数值或运行时调用'},
        'head_before_summary_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'audited_index_tree':subprocess.check_output(['git','write-tree'],cwd=ROOT,text=True).strip(),
        'archives':folders,'files':records,'checked_blob_count':len(records),'byte_mismatches':0,
        'links':links,'checked_local_links':len(links),'missing_links':0,
        'new_fits':0,'new_pixel_mappings':0,'native_calls':0,'performance_calls':0,
        'script_sha256':digest(Path(__file__).read_bytes()),
        'scope':'清单/原字节交付及本轮相关文档链接，不把静态通过当作新增精度/性能或全仓CI通过。'}
    save(out/'results.json',record)
    print(json.dumps({k:record[k] for k in ('pass','checked_blob_count','byte_mismatches','checked_local_links','missing_links')},ensure_ascii=False))

if __name__=='__main__':main()
