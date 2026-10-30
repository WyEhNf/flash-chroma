"""仅修独立291定位入口的DLL文件名；保留V2文件名预检失败。"""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    source=ROOT/'scripts/diagnose_direct_sentinel_alignment_v2.py';target=ROOT/'scripts/diagnose_direct_sentinel_alignment_v3.py';receipt=ROOT/'artifacts/p16-direct-sentinel-alignment-v3-generated.json'
    if target.exists() or receipt.exists():raise FileExistsError('不覆盖第三版定位入口')
    previous=json.loads((ROOT/'artifacts/p16-direct-sentinel-alignment-v2-generated.json').read_text(encoding='utf-8'))
    if sha(source)!=previous['target_sha256']:raise ValueError('第二版原源已变')
    text=source.read_bytes().decode('utf-8')
    if text.count("dll=BUILD/'libjshc_direct_sentinel.dll'")!=1:raise ValueError('文件名修复非唯一')
    text=text.replace("dll=BUILD/'libjshc_direct_sentinel.dll'","dll=BUILD/'libjshc_direct_sentinel_v2.dll'").replace('p16-direct-sentinel-v2-alignment-diagnose-v1','p16-direct-sentinel-v2-alignment-diagnose-v2')
    ast.parse(text);target.write_bytes(text.encode('utf-8'))
    receipt.write_text(json.dumps({'old_sha256':sha(source),'new_sha256':sha(target),'generator_sha256':sha(__file__),'change':'仅DLL文件名与独立证据目录；旧失败未执行原生像素','performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'generated':True,'target_sha256':sha(target),'performance_calls':0}))

if __name__=='__main__':main()
