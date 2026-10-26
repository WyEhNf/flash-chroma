"""标准库只读核对本阶段归档与精度保留率；不执行原生或wasm数值测试。"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import math
import struct
import zipfile

ROOT=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
archive=(ROOT/'evidence.zip').read_bytes()
assert sha(archive)==manifest['zip_sha256']
with zipfile.ZipFile(ROOT/'evidence.zip') as z:
    assert z.testzip() is None
    names=z.namelist()
    assert len(names)==len(set(names))==len(manifest['files'])
    assert set(names)=={s['path'] for s in manifest['files']}
    for item in manifest['files']:
        p=PurePosixPath(item['path'])
        assert not p.is_absolute() and '..' not in p.parts
        data=z.read(item['path'])
        assert len(data)==item['bytes'] and sha(data)==item['sha256']
    full=json.loads(z.read('full/results.json'))['results']
    summary=json.loads((ROOT/'summary.json').read_text(encoding='utf-8'))['rows']
    assert len(full)==len(summary)==8
    def ratio(a,b):
        return min(1. if b[k]==0 else a[k]/b[k] for k in ('mean','p99','max'))
    for row,view in zip(full,summary):
        assert row['name']==view['name']
        assert row['metrics']['n']==16777216
        assert row['decompressed_native']['byte_mismatches']==0
        assert row['decompressed_native']['avx2_full_domain']
        assert len(row['photos']['per_image'])==100
        assert row['photos']['merged']['n']==78643200
        assert math.isclose(view['cube_retention'],ratio(full[0]['metrics'],row['metrics']),abs_tol=1e-14)
        assert math.isclose(view['photo_retention'],ratio(full[0]['photos']['merged'],row['photos']['merged']),abs_tol=1e-14)
        worst=min(ratio(a,b) for a,b in zip(full[0]['photos']['per_image'],row['photos']['per_image']))
        assert math.isclose(view['worst_image_retention'],worst,abs_tol=1e-14)
    wasm=json.loads(z.read('wasm/results.json'))
    assert wasm['passed'] and not wasm['imports'] and len(wasm['records'])==5
    assert wasm['model_view_bytes']==1044
    for record in wasm['records']:
        assert record['full_rgb_colors']==16777216 and record['byte_mismatches']==0
        assert record['prediction_sha256']==full[0]['prediction_sha256']
    for record in json.loads(z.read('cross/results.json'))['records']:
        obj=z.read('cross/'+record['label']+'.o')
        assert obj[:4]==b'\x7fELF' and obj[4]==record['elf_class']
        assert obj[5]==(1 if record['data_endianness']=='little' else 2)
        assert struct.unpack_from('<H' if obj[5]==1 else '>H',obj,18)[0]==record['elf_machine']
print('104份归档字节、8项精度曲线、五格式wasm及三类ELF静态核验通过')
