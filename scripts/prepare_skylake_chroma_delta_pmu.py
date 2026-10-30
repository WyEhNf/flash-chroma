"""冻结40/60同场单次计数输入与门槛；不执行像素。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def spec(path):
    path = ROOT / path
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source = ROOT / 'experiments/skylake-tilexy-pmu-v1.json'
    target = ROOT / 'experiments/skylake-chroma-delta-pmu-v1.json'
    if target.exists():
        raise FileExistsError(target)
    policy = json.loads(source.read_text(encoding='utf-8'))
    policy['purpose'] = '40对60通道差16MiB字节表的同场一次计数；1t≤0.95、4t≤1.05门槛与3倍墙钟目标均预冻结'
    policy['script'] = spec('scripts/profile_skylake_chroma_delta_pmu.py')
    policy['models_plan'] = spec('experiments/skylake-chroma-delta-v1.json')
    policy['cases']['chroma_delta60'] = policy['cases'].pop('tilexy54')
    candidate = policy['cases']['chroma_delta60']
    candidate['revision'] = 60
    candidate['plan'] = policy['models_plan']
    candidate['build'] = spec('artifacts/skylake-chroma-delta-linux-build-v1/build.json')
    candidate['full'] = spec('artifacts/skylake-chroma-delta-linux-full-v1/results.json')
    candidate['library'] = {'path': '/mnt/f/Hackathon/projects/16-lut-color/artifacts/skylake-chroma-delta-linux-build-v1/libjshc_skylake_chroma_delta.so',
                            'sha256': spec('artifacts/skylake-chroma-delta-linux-build-v1/libjshc_skylake_chroma_delta.so')['sha256']}
    for order in policy['orders']:
        order['variants'] = ['chroma_delta60' if x == 'tilexy54' else x for x in order['variants']]
    policy['python_sources'][0] = 'scripts/profile_skylake_chroma_delta_pmu.py'
    target.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(spec(target.relative_to(ROOT).as_posix()))


if __name__ == '__main__':
    main()
