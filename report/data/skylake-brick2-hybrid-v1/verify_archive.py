"""在临时目录复用归档内原核验器，重算全部原始计时；不加载候选库。"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(prefix='brick2-hybrid-audit-') as directory:
    root=Path(directory)
    target=root/'report/data/skylake-brick2-hybrid-v1'
    target.mkdir(parents=True)
    for name in ['manifest.json',*[x['path'] for x in manifest['files']]]:
        shutil.copyfile(HERE/name,target/name)
    helper=root/'artifacts/verify_brick2_hybrid_archive.py';helper.parent.mkdir()
    with zipfile.ZipFile(HERE/'evidence.zip') as z:
        helper.write_bytes(z.read('artifacts/verify_brick2_hybrid_archive.py'))
    proc=subprocess.run([sys.executable,'-X','utf8',str(helper)],capture_output=True,text=True,encoding='utf-8')
    if proc.returncode:raise RuntimeError(proc.stdout+'\n'+proc.stderr)
    actual=json.loads((target/'archive-audit.json').read_text(encoding='utf-8'))
    expected=json.loads((HERE/'archive-audit.json').read_text(encoding='utf-8'))
    assert actual==expected
print('235份原件、48批计时/A/A/三倍判定复算一致；候选未执行。')
