"""将已有100张RGB8评测照片转换为框架raw格式；仅用于评价，不参与LUT拟合。"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare(output):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError('输出目录已存在，拒绝覆盖')
    inputs = [ROOT / name.strip() for name in (ROOT/'assets/photos/eval.txt').read_text(encoding='utf-8-sig').splitlines()
              if name.strip() and not name.lstrip().startswith('#')]
    if len(inputs) != 100 or len(set(inputs)) != 100:
        raise ValueError('现有评测列表必须是100份不同路径')
    output.mkdir(parents=True)
    records = []
    for i, source in enumerate(inputs, 1):
        with Image.open(source) as image:
            image.load()
            if image.mode != 'RGB' or image.size != (1024, 768):
                raise ValueError('不静默改尺寸/色彩模式：'+str(source))
            pixels = image.tobytes()
        target = output / f'{i}.bin'
        with target.open('xb') as stream:
            stream.write(pixels)
        records.append({'index': i, 'source': str(source), 'source_sha256': sha(source),
                        'raw': target.name, 'raw_sha256': sha(target), 'bytes': len(pixels)})
    (output/'images.txt').write_text(''.join(r['raw']+'\n' for r in records), encoding='utf-8', newline='\n')
    value = {'schema': 'framework_supplemental_photos_v1', 'images': records,
             'count': len(records), 'fit_uses_images': False,
             'scope': '已有100张照片仅作额外精度与执行评价，不是赛方新增正式样例，不用于拟合/准备。',
             'rights': '保留assets/photos/README.md中Kodak/DPED/DIV2K来源和使用范围。'}
    (output/'manifest.json').write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return {'images': len(records), 'list': str(output/'images.txt'), 'manifest_sha256': sha(output/'manifest.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(prepare(parser.parse_args().output), ensure_ascii=False, indent=2))
