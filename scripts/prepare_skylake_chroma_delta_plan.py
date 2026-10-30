"""从54冻结实验派生一次固定60布局实验；只生成计划，不构建或计时。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    original = json.loads((ROOT / 'experiments/skylake-tilexy-v1.json').read_text(encoding='utf-8'))
    plan = ROOT / 'experiments/skylake-chroma-delta-v1.json'
    if plan.exists():
        raise FileExistsError(plan)
    original['purpose'] = '60研究16MiB RGB通道差索引表；全域精度不变，通用AVX2 Skylake兼容'
    original['base_commit'] = '7643bea227af63cecdea79b05fd6abcb7773ffa1'
    original['candidate'] = ('在40的16MiB字节表上仅改变物理排列和地址计算为'
                             'R, (G-R)&255, (B-G)&255；矢量索引三条指令/8像素；'
                             '保留GPR ID/调色板两级读取、原NT64/NTA和工作块')
    original['cmake_project'] = 'experiments/skylake-chroma-delta-runtime'
    original['cmake_targets'][1] = 'jshc_skylake_chroma_delta'
    original['revisions']['candidate'] = 60
    original['pageindex_policy']['scope_note'] = '该字段保留40来源；60物理布局以chroma_delta_policy为准'
    original.pop('tilexy_policy')
    original['chroma_delta_policy'] = {
        'format': 18, 'table_bytes': 16777216,
        'index': 'R | (((G-R)&255)<<8) | (((B-G)&255)<<16)',
        'inverse': 'R=h&255; G=(R+((h>>8)&255))&255; B=(G+((h>>16)&255))&255',
        'input_span_bytes': 24,
        'vector_index': 'VPSLLD 8, VPSUBB, VPAND 0x00ffffff; exact AVX2 input',
        'page_number_unchanged': False,
        'offline_100photo_lines_per_64': {'revision40': 49.415258789, 'revision54': 42.34256184896, 'candidate60': 44.509029947916666},
        'hypothesis': '照片通道相关性使表行重用增加，较54用更少索引操作；只选本布局一次，不扫参数',
        'pmu_screen': {'same_session_reference': 40, 'one_thread_cycle_ratio_max': 0.95,
                       'four_thread_cycle_ratio_max': 1.05, 'repetitions': 1,
                       'on_failure': '停止本版，不重复画像或整轮性能择优', 'goal_gate_unchanged': True},
        'scope': '照片离线行数仅提出假设，AMD/WSL计数不证明Skylake实测；目标仍为23的3倍吞吐且精度不降'
    }
    sources = {}
    for old in original['source_sha256']:
        name = old.replace('experiments/skylake-tilexy-runtime/', 'experiments/skylake-chroma-delta-runtime/')
        sources[name] = sha(ROOT / name)
    for name in ('scripts/prepare_skylake_chroma_delta_plan.py',
                 'scripts/inspect_skylake_chroma_delta.py',
                 'scripts/verify_skylake_chroma_delta_linux.py',
                 'scripts/profile_skylake_chroma_delta_pmu.py'):
        sources[name] = sha(ROOT / name)
    original['source_sha256'] = sources
    plan.write_text(json.dumps(original, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(plan, sha(plan), len(sources))


if __name__ == '__main__':
    main()
