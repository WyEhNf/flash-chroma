"""从原定位器派生291对齐回归，保留290已失败定位器逐字节不变。"""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    source=ROOT/'scripts/diagnose_direct_sentinel_alignment.py';target=ROOT/'scripts/diagnose_direct_sentinel_alignment_v2.py';receipt=ROOT/'artifacts/p16-direct-sentinel-alignment-v2-generated.json'
    if target.exists() or receipt.exists():raise FileExistsError('不覆盖291定位回归')
    build_path=ROOT/'artifacts/p16-direct-sentinel-v2-build-v1/build-check.json';build=json.loads(build_path.read_text(encoding='utf-8'))
    if not build['passed']:raise ValueError('291构建未过')
    old_sha=sha(source);text=source.read_bytes().decode('utf-8')
    text=text.replace('from check_direct_sentinel_native import','from check_direct_sentinel_native_v2 import').replace('p16-direct-sentinel-alignment-diagnose-v1','p16-direct-sentinel-v2-alignment-diagnose-v1').replace("DLL_SHA='f54a505f128e515e165c9a13676d2f186939db7fefb7ea040d1aee2d15edd45a'",f"DLL_SHA='{build['dll_sha256']}'")
    ast.parse(text,filename=str(target));target.write_bytes(text.encode('utf-8'))
    assert sha(source)==old_sha
    receipt.write_text(json.dumps({'source_sha256':old_sha,'target_sha256':sha(target),'generator_sha256':sha(__file__),'build_check_sha256':sha(build_path),'dll_sha256':build['dll_sha256'],'scope':'同128对齐/参考模型与原定位器，仅换291库；不改旧失败','performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'generated':True,'target_sha256':sha(target),'performance_calls':0}))

if __name__=='__main__':main()
