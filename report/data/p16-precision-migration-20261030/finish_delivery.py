import json, hashlib, re, subprocess, zipfile, sys
from pathlib import Path
import numpy as np
root=Path.cwd(); sys.path.insert(0,str(root/'scripts'))
import verify_precision_migration as verify
folder=Path('F:/Hackathon/极速焕彩测试框架/FlashChromaHistory'); art=root/'artifacts/precision'
manifest=json.loads((folder/'source-manifest.json').read_text(encoding='utf-8'))
for name,item in manifest['files'].items(): assert verify.digest(folder/name)==item['sha256']
for name,sha in manifest['components'].items(): assert verify.digest(root/name)==sha
assert verify.digest(folder.parent/'C++/main.cpp')==manifest['original_main_sha256']
cache=Path('F:/Hackathon/worktrees/p16-frontier-header-20261027/artifacts/framework-u16-cache-20261029')
tables=[np.memmap(cache/x['path'],dtype='<u2',mode='r').reshape(-1,3) for x in json.loads((cache/'manifest.json').read_text(encoding='utf-8'))['records']]
domain=np.memmap(art/'final/domain.rgb',dtype=np.uint8,mode='r').reshape(-1,3)
log=(art/'delivery-run.log').read_text(encoding='utf-8-sig'); measured=[]
printed=re.findall(r'^Img:.*Delta: \S+ (\S+)',log,re.M); assert len(printed)==4
for i in range(1,5):
    path=folder.parent/f'data/image/{i}.bin'; pixels=np.fromfile(path,np.uint8).reshape(-1,3); out=domain[verify.pack(pixels)]; gold=pixels
    for table in tables: gold=(table[verify.pack(gold),::-1]//16).astype(np.uint8)
    mean=float(np.sqrt(np.sum((out.astype(np.int32)-gold)**2,axis=1)).mean()); assert abs(mean-float(printed[i-1]))<.00000051
    measured.append(dict(image=i,input_sha256=verify.digest(path),independent_mean=mean,printed_mean=float(printed[i-1])))
imports=subprocess.check_output(['E:/mingw64/bin/objdump.exe','-p',str(folder/'main_flash_chroma.exe')]).decode('utf-8','replace')
dlls=re.findall(r'DLL Name:\s*(\S+)',imports)
package=folder.parent/'FlashChromaHistory-20261030.zip'; assert not package.exists()
with zipfile.ZipFile(package,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(folder.iterdir()):
        if p.is_file(): z.write(p,p.name)
with zipfile.ZipFile(package) as z:
    assert z.testzip() is None
    for name in z.namelist(): assert hashlib.sha256(z.read(name)).hexdigest()==verify.digest(folder/name)
result=dict(original_unchanged=True,components_match=True,independent_images=measured,dlls=dlls,package=str(package),package_bytes=package.stat().st_size,package_sha256=verify.digest(package),exe_sha256=verify.digest(folder/'main_flash_chroma.exe'),hpp_sha256=verify.digest(folder/'flash_chroma_framework.hpp'),hpp_bytes=(folder/'flash_chroma_framework.hpp').stat().st_size)
(art/'delivery-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,ensure_ascii=False))
