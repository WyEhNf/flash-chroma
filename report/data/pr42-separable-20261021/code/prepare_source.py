"""从已存在的Git对象只读提取固定PR42源码，拒绝覆盖已有快照。"""
import io,subprocess,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
DEST=ROOT/'tmp/stage-a-pr42'
SHA='59586f7bd6dd248cf0b68bcbdff8e41cf95ac572'
if (DEST/'python').exists():raise RuntimeError('源码快照已存在，请先核对run记录中的源码哈希，不覆盖')
archive=subprocess.check_output(['git','archive',SHA,'python/lutlab'],cwd=ROOT)
DEST.mkdir(parents=True,exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as t:t.extractall(DEST,filter='data')
print('已提取固定源码',SHA)
