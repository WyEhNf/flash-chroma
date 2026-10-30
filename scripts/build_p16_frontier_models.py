"""从已归档源身份生成低内存拟合候选，并保留当前四个精度模型。"""
from __future__ import annotations
import argparse
import json
import shutil
import zipfile
from pathlib import Path

import flash_chroma_support as support
import p16_frontier


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-evidence', type=Path,
        default=support.ROOT/'report/data/p16-score-candidate-20261027/raw-evidence.zip')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('候选目录已存在，拒绝覆盖')
    with zipfile.ZipFile(args.source_evidence) as archive:
        previous = json.loads(archive.read('run-default/results.json'))
    sources = previous['quality']['sources']
    for record in sources:
        if support.digest(record['path']) != record['sha256']:
            raise ValueError('原始LUT身份不同')
    args.output.mkdir(parents=True)
    source_manifest = support.ROOT/'data/p16-score-models/manifest.json'
    registry = json.loads(source_manifest.read_text(encoding='utf-8'))
    registry['path_root'] = str(support.ROOT)
    registry['original_luts'] = sources
    registry['source_luts_sha256'] = [v['sha256'] for v in sources]
    registry['source_evidence_sha256'] = support.digest(args.source_evidence)
    for name, sizes in [('compact17', [17]*4), ('compact25', [25]*4), ('mixed', [17,25,25,33])]:
        folder = args.output/name
        fitted = p16_frontier.fit_candidate([v['path'] for v in sources], sizes,
                                            'sample_interp', 'uniform', folder)
        profile = fitted['profiles']['fitted']
        for record in profile['models'] + [v for v in profile['sidecars'] if v]:
            if not Path(record['path']).is_absolute():
                record['path'] = str((folder/record['path']).resolve())
        registry['profiles'][name] = profile
        print('已生成候选', name, sizes, flush=True)
    for profile in registry['profiles'].values():
        profile['source_luts_sha256'] = registry['source_luts_sha256']
    shutil.copyfile(support.ROOT/'data/p16-unified-models/LICENSE.stripedpurple',
                    args.output/'LICENSE.stripedpurple')
    support.write_json(args.output/'manifest.json', registry)


if __name__ == '__main__':
    main()
