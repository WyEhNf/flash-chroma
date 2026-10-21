"""由60冻结计划派生唯一61输入展开候选，不构建或计时。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    src = ROOT / 'experiments/skylake-chroma-delta-v1.json'
    dst = ROOT / 'experiments/skylake-chroma-2op-v1.json'
    if dst.exists():
        raise FileExistsError(dst)
    plan = json.loads(src.read_text(encoding='utf-8'))
    plan['purpose'] = '61双指令通道差索引；表和60同一物理字节，完整RGB8精度不变'
    plan['base_commit'] = '226a0c49982ee61b6f372c082e408e79560ea9f8'
    plan['candidate'] = ('只更改60的24字节AVX2输入展开：每dword由[R,G,B,0]变为[R,G,B,B]；'
                         'VPSLLD 8加VPSUBB直接形成[R,G-R,B-G,0]，删除VPAND。')
    plan['cmake_project'] = 'experiments/skylake-chroma-2op-runtime'
    plan['cmake_targets'][1] = 'jshc_skylake_chroma_2op'
    plan['revisions']['candidate'] = 61
    p = plan.pop('chroma_delta_policy')
    p['format'] = 19
    p['input_dword'] = '[R,G,B,B]'
    p['vector_index'] = 'VPSLLD 8, VPSUBB；高字节B-B=0，不需要掩码'
    p['choice'] = '从60只删一条掩码操作，不改表布局/计算模型；只计数一次'
    plan['chroma_2op_policy'] = p
    rename = {
        'experiments/skylake-chroma-delta-runtime/': 'experiments/skylake-chroma-2op-runtime/',
        'scripts/prepare_skylake_chroma_delta_plan.py': 'scripts/prepare_skylake_chroma_2op_plan.py',
        'scripts/inspect_skylake_chroma_delta.py': 'scripts/inspect_skylake_chroma_2op.py',
        'scripts/verify_skylake_chroma_delta_linux.py': 'scripts/verify_skylake_chroma_2op_linux.py',
        'scripts/profile_skylake_chroma_delta_pmu.py': 'scripts/profile_skylake_chroma_2op_pmu.py',
    }
    sources = {}
    for old in plan['source_sha256']:
        name = old
        for prefix, replacement in rename.items():
            name = name.replace(prefix, replacement)
        sources[name] = sha(ROOT / name)
    plan['source_sha256'] = sources
    dst.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(dst, sha(dst), len(sources))


if __name__ == '__main__':
    main()
