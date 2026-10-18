"""同机交错比较三个已完整验收四级模型的原生速度与内存，不重拟合。"""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
from lutlab import io, runtime, study_provenance
from lutlab.compatibility import write_json
from run_chain_error_study import digest


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def version(folder):
    run, selected, full = (read(folder/name) for name in ('run.json', 'selection.json', 'full-results.json'))
    if (full['run_identity'] != run['identity_sha256'] or selected['run_identity'] != run['identity_sha256']
            or run['identity_sha256'] != study_provenance.identity_digest(run['identity'])
            or not full['acceptance']['accepted'] or not selected['winner']):
        raise ValueError('仅比较来源一致且完整门禁通过的版本')
    paths = [folder/selected['winner']/f'selected-stage{i+1}.slut' for i in range(4)]
    if [digest(p) for p in paths] != full['model_sha256']:
        raise ValueError('比较模型与完整验收SHA不一致')
    if any(m['byte_mismatches'] or m['sha256'] != full['cube']['prediction_sha256'] for m in full['native']):
        raise ValueError('比较模型没有完整逐字节后端一致证据')
    return {'name': folder.name, 'paths': paths, 'sha256': full['model_sha256'],
        'run_identity': run['identity_sha256'], 'full_results_sha256': digest(folder/'full-results.json'),
        'cube_sha256': full['cube']['prediction_sha256'], 'source_plan': run['identity']['plan']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--versions', type=Path, nargs=2, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有性能阶段')
    measured = [version(p.resolve()) for p in args.versions]
    first_plan = measured[0]['source_plan']
    original = {'name': 'PR16', 'paths': [ROOT/r['path'] for r in first_plan['baseline_models']],
        'sha256': [r['sha256'] for r in first_plan['baseline_models']],
        'cube_sha256': first_plan['baseline_evidence']['cube']['sha256'],
        'source_full_results_sha256': first_plan['baseline_evidence']['results']['sha256']}
    versions = [original, *measured]
    for item in versions:
        if [digest(p) for p in item['paths']] != item['sha256'] or any(io.load_sparse(p, competition=True).m != 33 for p in item['paths']):
            raise ValueError('性能比较需要同字节四级m33模型')
    expected_executable = first_plan['environment']['executable_sha256']
    if digest(args.executable) != expected_executable:
        raise ValueError('性能程序与完整正确性程序不同')
    manifest = read(ROOT/'assets/photos/manifest.json')
    images = [ROOT/row['evaluation']['path'] for row in manifest['images']]
    if len(images) != 100:
        raise ValueError('性能比较要求完整100图')
    for path, row in zip(images, manifest['images']):
        if digest(path) != row['evaluation']['sha256']:
            raise ValueError('性能图片字节与精度图片不同')
    args.output.mkdir(parents=True)
    image_list = args.output/'images.txt'
    image_list.write_text('\n'.join(p.resolve().as_posix() for p in images)+'\n', encoding='utf-8')
    git_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    capabilities = runtime.capabilities(executable=args.executable)
    identity = {'kind': 'paired_precision_runtime', 'git_head': git_head,
        'environment': study_provenance.environment_fingerprint(), 'capabilities': capabilities,
        'executable_sha256': expected_executable, 'manifest_sha256': digest(ROOT/'assets/photos/manifest.json'),
        'source_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in (
            Path(__file__), ROOT/'python/lutlab/runtime.py', ROOT/'cpp/src/main.cpp')},
        'versions': versions, 'threads': [1, 4], 'kernel': 'tetra_avx2', 'repetitions': 5,
        'cycles': 3, 'orders': [[v['name'] for v in versions[c:]+versions[:c]] for c in range(3)],
        'timing_scope': '每进程预加载100图，保留冷首图；5次完整集合原始时间。apply仅映射，set含复制+映射；均不含拟合、模型加载、解码和编码；不用逐图best-of-reps冒充均值',
        'limits': '同机同后端交错描述性比较，无统计显著性声明；OS后台负载未完全控制，不外推i7-14700或PR38的Intel/Numba环境'}
    # Path转字符串后再形成规范身份，避免不同序列化器产生不同摘要。
    identity = json.loads(json.dumps(identity, default=str))
    study_provenance.claim_run(args.output/'run.json', {'identity': identity, 'identity_sha256': study_provenance.identity_digest(identity)})
    records = []
    for threads in (1, 4):
        for cycle in range(3):
            for item in versions[cycle:]+versions[:cycle]:
                result = runtime.bench(item['paths'], image_list, executable=args.executable,
                    kernel='tetra_avx2', threads=threads, reps=5, competition=True)
                if (result['kernel'] != 'tetra_avx2' or result['images'] != 100 or result['stages'] != 4
                        or result['m'] != 33 or result['requested_threads'] != threads or result['batch_mode']
                        or len(result['set_ms_reps']) != 5 or len(result['apply_ms_reps']) != 5):
                    raise ValueError('实际性能内核或计时范围不符')
                entry = {'version': item['name'], 'cycle': cycle, 'threads': threads, 'result': result}
                records.append(entry)
                write_json(args.output/f"threads{threads}-cycle{cycle}-{item['name']}.json", entry)
                print(f"线程{threads} 轮{cycle+1} {item['name']}：映射中位{statistics.median(result['apply_ms_reps'])/100:.4f}ms/图，含复制中位{statistics.median(result['set_ms_reps'])/100:.4f}ms/图", flush=True)
    for path, row in zip(images, manifest['images']):
        if digest(path) != row['evaluation']['sha256']:
            raise ValueError('性能阶段期间图片发生变化')
    summary = []
    for threads in (1, 4):
        for item in versions:
            rows = [r['result'] for r in records if r['threads'] == threads and r['version'] == item['name']]
            apply = [statistics.median(r['apply_ms_reps'])/100 for r in rows]
            whole = [statistics.median(r['set_ms_reps'])/100 for r in rows]
            summary.append({'version': item['name'], 'threads': threads,
                'apply_ms_image_median': statistics.median(apply), 'apply_ms_image_process_values': apply,
                'copy_apply_ms_image_median': statistics.median(whole), 'copy_apply_ms_image_process_values': whole,
                'model_file_bytes': sum(p.stat().st_size for p in item['paths']),
                'model_runtime_bytes': [r['model_runtime_bytes'] for r in rows],
                'node_payload_bytes': [r['model_node_payload_bytes'] for r in rows],
                'work_image_bytes': [r['work_image_bytes'] for r in rows],
                'preloaded_image_bytes': [r['preloaded_image_bytes'] for r in rows],
                'process_peak_working_set_bytes': [r['observed_peak_working_set_bytes'] for r in rows],
                'kernel_scratch_per_worker': [r['kernel_block_scratch_bytes_per_worker'] for r in rows]})
    write_json(args.output/'results.json', {'run_identity': study_provenance.identity_digest(identity),
        'summary': summary, 'native_invocations': len(records), 'limits': identity['limits'],
        'scope': identity['timing_scope']})
    print(json.dumps({'native_invocations': len(records), 'summary': summary}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
