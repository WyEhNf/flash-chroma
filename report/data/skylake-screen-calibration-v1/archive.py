"""保存同库短调用与原生长批次负对照全部原件，不覆盖或择优。"""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def main():
    paths = []
    summaries = {}
    for name in ('skylake-same-library-calibration-v1', 'skylake-native-batch-calibration-v1'):
        source, target = ROOT/'artifacts'/name, HERE/name
        if target.exists():
            raise ValueError('不得覆盖负对照原件')
        shutil.copytree(source, target)
        paths.extend(p for p in target.rglob('*') if p.is_file())
        summaries[name] = json.loads((target/'results.json').read_text(encoding='utf-8'))
    files = {p.relative_to(HERE).as_posix(): {'bytes': p.stat().st_size,
        'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}
    (HERE/'manifest.json').write_text(json.dumps({'schema': 1, 'files': files}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    audit = {'purpose': '负对照分辨能力检查，不作为优化成绩',
        'short_completed': summaries['skylake-same-library-calibration-v1']['calibration_completed'],
        'long_completed': summaries['skylake-native-batch-calibration-v1']['calibration_completed'],
        'short': summaries['skylake-same-library-calibration-v1']['summary'],
        'long': summaries['skylake-native-batch-calibration-v1']['summary'],
        'conclusion': '本机同库A/A仍有数个百分点至更大波动；单次PMU不足以可靠辨认约3%的小改动；保留全部旧失败，不用校准改判或拼接提速。'}
    (HERE/'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'short_completed': audit['short_completed'], 'long_completed': audit['long_completed']}))


if __name__ == '__main__':
    main()
