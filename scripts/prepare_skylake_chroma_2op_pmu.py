"""冻结40/61同场单次计数证据；不执行像素。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def spec(name):
    path = ROOT / name
    return {'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source = ROOT / 'experiments/skylake-chroma-delta-pmu-v1.json'
    target = ROOT / 'experiments/skylake-chroma-2op-pmu-v1.json'
    if target.exists():
        raise FileExistsError(target)
    policy = json.loads(source.read_text(encoding='utf-8'))
    policy['purpose'] = '40对61双指令通道差索引的同场单次计数；1t≤0.95、4t≤1.05门槛与3倍墙钟目标均预冻结'
    policy['script'] = spec('scripts/profile_skylake_chroma_2op_pmu.py')
    policy['models_plan'] = spec('experiments/skylake-chroma-2op-v1.json')
    candidate = policy['cases'].pop('chroma_delta60')
    policy['cases']['chroma_2op61'] = candidate
    candidate['revision'] = 61
    candidate['plan'] = policy['models_plan']
    candidate['build'] = spec('artifacts/skylake-chroma-2op-linux-build-v1/build.json')
    candidate['full'] = spec('artifacts/skylake-chroma-2op-linux-full-v1/results.json')
    candidate['library'] = {'path': '/mnt/f/Hackathon/projects/16-lut-color/artifacts/skylake-chroma-2op-linux-build-v1/libjshc_skylake_chroma_2op.so',
                            'sha256': spec('artifacts/skylake-chroma-2op-linux-build-v1/libjshc_skylake_chroma_2op.so')['sha256']}
    for order in policy['orders']:
        order['variants'] = ['chroma_2op61' if x == 'chroma_delta60' else x for x in order['variants']]
    policy['python_sources'][0] = 'scripts/profile_skylake_chroma_2op_pmu.py'
    target.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(spec('experiments/skylake-chroma-2op-pmu-v1.json'))


if __name__ == '__main__':
    main()
