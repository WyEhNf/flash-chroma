"""按已保存连续目标选择执行真实百图；严格绑定库、模型、输入与候选记录。"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

import flash_chroma_support as support
import p16_frontier as frontier
import p16_submission as submission

REQUEST_FIELDS = {'context', 'target', 'goal', 'weights', 'max_error', 'max_ms',
                  'max_runtime_bytes', 'max_workspace_bytes', 'allow_unstable_time',
                  'ignore_time', 'backends', 'max_threads'}


def resolve_record_path(value, catalog_path):
    """catalog内相对路径始终以catalog所在目录为基准。"""
    if not isinstance(value, str) or not value:
        raise ValueError('记录路径不能为空')
    path = Path(value)
    return (path if path.is_absolute() else Path(catalog_path).resolve().parent / path).resolve()


def bind_selection(catalog_path, selection_path):
    catalog_path, selection_path = Path(catalog_path).resolve(), Path(selection_path).resolve()
    catalog = frontier.validate_catalog(json.loads(catalog_path.read_text(encoding='utf-8')))
    selection = json.loads(selection_path.read_text(encoding='utf-8'))
    if (selection.get('schema') != 'flash_chroma_selection_v1' or selection.get('status') != 'ok'
            or selection.get('catalog_sha256') != support.digest(catalog_path)):
        raise ValueError('选择记录的版本、状态或catalog摘要不符')
    request = selection.get('request')
    if not isinstance(request, dict) or set(request) != REQUEST_FIELDS:
        raise ValueError('选择记录缺少完整请求，不能重现连续目标选择')
    chosen = selection.get('selected')
    if not isinstance(chosen, dict):
        raise ValueError('选择记录没有可执行候选')
    matches = [row for row in catalog['candidates'] if row['id'] == chosen.get('id')]
    if len(matches) != 1 or chosen != matches[0]:
        raise ValueError('选择记录中的候选被修改，不能突破catalog原执行配置')
    recomputed = frontier.tradeoff(catalog, **request)
    if recomputed['status'] != 'ok' or recomputed['selected']['id'] != chosen['id']:
        raise ValueError('保存的请求不能重新选择同一候选')
    return catalog, copy.deepcopy(matches[0]), recomputed, {
        'catalog': {'path': str(catalog_path), 'sha256': support.digest(catalog_path)},
        'selection': {'path': str(selection_path), 'sha256': support.digest(selection_path)}}


def bind_model(catalog, candidate, catalog_path):
    record = catalog['models'][candidate['model_id']]
    path = resolve_record_path(record.get('manifest'), catalog_path)
    expected = record.get('manifest_sha256')
    if not frontier._sha(expected) or support.digest(path) != expected:
        raise ValueError('模型manifest缺少固定SHA或其内容已经改变')
    name = record.get('profile')
    if not isinstance(name, str) or not name:
        raise ValueError('模型记录必须明确指定profile')
    value, models = support.load_models(path, [name])
    context = catalog['contexts'][candidate['context']]
    sources = record.get('source_luts_sha256')
    if sources != context['source_luts_sha256']:
        raise ValueError('模型原始LUT与选择上下文不一致')
    declared_sources = models[name].profile.get('source_luts_sha256')
    if declared_sources is not None and declared_sources != sources:
        raise ValueError('模型profile与catalog声明的原始LUT不同')
    return models[name], {'path': str(path), 'sha256': expected, 'profile': name,
                          'source_luts_sha256': sources, 'files': models[name].records}


def bind_evidence(candidate, context, catalog_path):
    value = candidate['evidence']
    if '#' not in value:
        raise ValueError('执行入口要求evidence为results.json#记录id')
    filename, record_id = value.rsplit('#', 1)
    path = resolve_record_path(filename, catalog_path)
    evidence = json.loads(path.read_text(encoding='utf-8'))
    if evidence.get('completed') is not True:
        raise ValueError('原始测量尚未完成，不能作为冻结部署证据')
    matches = [row for row in evidence.get('records', []) if row.get('id') == record_id]
    if len(matches) != 1:
        raise ValueError('原始证据找不到唯一执行记录')
    row = matches[0]
    if (evidence.get('library', {}).get('sha256') != context['build_id']
            or evidence.get('source_pixels_sha256') != context['dataset_sha256']
            or row.get('config') != candidate['config']
            or not frontier._sha(row.get('batch_sha256'))):
        raise ValueError('原始证据与catalog的库、输入或执行配置不一致')
    return row, {'path': str(path), 'sha256': support.digest(path), 'record_id': record_id,
                 'environment': evidence.get('environment'), 'completed': evidence.get('completed')}


def create_output(path):
    output = Path(path).resolve()
    if output.exists():
        raise FileExistsError('输出目录已经存在，拒绝覆盖：' + str(output))
    output.mkdir(parents=True)
    return output


def write_frames(output, frames):
    """输出名字只由批次索引产生，输入文件名不能改变输出路径。"""
    folder = Path(output) / 'images'
    folder.mkdir()
    rows = []
    for index, frame in enumerate(frames, 1):
        path = folder / f'{index:04d}.png'
        with path.open('xb') as stream:
            Image.fromarray(frame).save(stream, format='PNG')
        rows.append({'path': str(path.resolve()), 'sha256': support.digest(path)})
    return rows


def _check_unchanged(records):
    for row in records:
        if support.digest(row['path']) != row['sha256']:
            raise RuntimeError('运行期间固定输入被修改：' + row['path'])


def _platform_record(current, context, evidence):
    current_hash = hashlib.sha256(json.dumps(current, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    source_environment = evidence.get('environment')
    source_hash = (hashlib.sha256(json.dumps(source_environment, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                   if isinstance(source_environment, dict) else None)
    return {'current_environment': current, 'current_fingerprint': current_hash,
            'catalog_platform_id': context['platform_id'],
            'current_matches_catalog_fingerprint': current_hash == context['platform_id'],
            'source_environment_matches_catalog_fingerprint': source_hash == context['platform_id'],
            'same_environment_speed_optimum_claimed': False,
            'scope': '完整环境指纹包含亲和、依赖和提交；不相等时仅报告当前实测，不继承同机速度排名。相等也不构成单次运行的稳定速度保证。'}


def run(args):
    if args.threshold is not None and (not math.isfinite(args.threshold) or args.threshold < 0 or not args.reference_luts):
        raise ValueError('阈值须为非负有限值，且必须提供四个原始参考LUT')
    if args.output.resolve().exists():
        raise FileExistsError('输出目录已存在，拒绝覆盖')
    catalog, candidate, selection, identities = bind_selection(args.catalog, args.selection)
    context = catalog['contexts'][candidate['context']]
    if support.digest(args.library) != context['build_id']:
        raise ValueError('实际运行库SHA与选定测量上下文不一致')
    model, model_identity = bind_model(catalog, candidate, args.catalog)
    model_buffer_hashes = [hashlib.sha256(bytes(buffer)).hexdigest() for buffer in model.buffers]
    expected_output, evidence_identity = bind_evidence(candidate, context, args.catalog)
    paths = submission.image_paths(args.images, args.image_root)
    list_record = {'path': str(args.images.resolve()), 'sha256': support.digest(args.images)}
    if args.reference_luts:
        references = frontier.source_records(args.reference_luts)
        if [row['sha256'] for row in references] != context['source_luts_sha256']:
            raise ValueError('提供的四个参考LUT与选定上下文不一致')
    support.native.setup(cpus=args.cpus)
    library = support.Library(args.library)
    if library.sha256 != context['build_id']:
        raise ValueError('加载前运行库字节发生变化')
    environment = support.native.environment()
    platform = _platform_record(environment, context, evidence_identity)
    output = create_output(args.output)
    try:
        plan = {'identities': identities, 'candidate': candidate, 'context': context,
                'selection': {'request': selection['request'], 'score': selection['score'],
                              'provisional': selection['provisional']},
                'library': library.record(), 'model': model_identity, 'images': list_record,
                'platform': platform, 'scripts': {str(Path(__file__).resolve()): support.digest(__file__)},
                'gpu_used': False, 'npu_used': False, 'write_images': bool(args.write_images)}
        frontier.save_new(output / 'executed-plan.json', plan)
        begin_application = time.perf_counter_ns()
        frames = np.empty((100, 768, 1024, 3), np.uint8)
        image_records = []
        for index, path in enumerate(paths):
            file_sha = support.digest(path)
            frames[index] = submission._rgb8(path)
            image_records.append({'index': index, 'path': str(path), 'sha256': file_sha,
                                  'pixel_sha256': support.sha(frames[index])})
        source_sha = support.sha(frames)
        if source_sha != context['dataset_sha256']:
            raise ValueError('百图解码像素SHA与选定验证数据不一致，拒绝继承精度或计时')
        target = np.empty_like(frames)
        before_prepare = support.native.rss()
        begin_prepare = time.perf_counter_ns()
        with library.create(model, candidate['config']) as engine:
            apply_ms = engine.apply(frames, target)
            stopped_first = time.perf_counter_ns()
            first_wall_ms = (stopped_first-begin_prepare)/1e6
            expected_backend = support.BACKENDS[candidate['config']['backend']]
            if engine.info['selected_backend'] != expected_backend:
                raise RuntimeError('运行库实际后端与候选记录不同')
            controlled_bytes = (model.total_bytes + engine.info['arena_bytes'] + engine.info['object_bytes']
                                + frames.nbytes + target.nbytes)
            if (engine.info['arena_bytes'] != candidate['metrics']['workspace_bytes']
                    or controlled_bytes != candidate['metrics']['runtime_bytes']):
                raise RuntimeError('实际工作区或受控运行内存账单与候选不一致')
            written = write_frames(output, target) if args.write_images else []
            application_ms = (time.perf_counter_ns()-begin_application)/1e6
            output_sha = support.sha(target)
            if output_sha != expected_output['batch_sha256']:
                raise RuntimeError('实际输出与原始证据的百图输出SHA不一致')
            per_image = [support.sha(frame) for frame in target]
            if expected_output.get('per_image_sha256') is not None and per_image != expected_output['per_image_sha256']:
                raise RuntimeError('实际逐图输出SHA与原始证据不一致')
            memory = {'resources': dict(engine.info), 'model_payload_bytes': model.total_bytes,
                      'source_image_bytes': frames.nbytes, 'output_image_bytes': target.nbytes,
                      'controlled_runtime_bytes': controlled_bytes, 'rss_before_prepare': before_prepare,
                      'rss_after_apply': support.native.rss(),
                      'scope': context.get('memory_scope', '模型载荷+Runtime对象+完整arena+百图输入输出；非进程峰值硬上界。')}
            timings = {'prepare_native_ms': engine.prepare_ms, 'batch_apply_ms': apply_ms,
                       'prepare_to_first_preloaded_batch_wall_ms': first_wall_ms,
                       'read_images_to_output_application_wall_ms': application_ms,
                       'application_includes_png_write': bool(args.write_images),
                       'scope': '单次实际百图；apply为原生映射调用，prepare含Runtime准备而不含模型读盘/离线拟合；application含输入SHA、解码、分配及数据身份检查，选配PNG写盘，不含库/模型读取、输出哈希和后续参考精度校验。'}
            frontier.save_new(output / 'runtime.json', {'timings': timings, 'memory': memory,
                'batch_output_sha256': output_sha, 'per_image_output_sha256': per_image, 'written_images': written})
        quality = {'verified_this_run': False, 'inherited_from_catalog': True,
                   'same_input_model_library_output_confirmed': True,
                   'metrics': {'mean_error': candidate['metrics']['mean_error'],
                               'worst_image_mean': candidate['metrics']['worst_image_mean']},
                   'evidence': evidence_identity,
                   'scope': '继承同一库、固定模型、百图像素和输出SHA对应的已验误差，本次未重新执行密集参考LUT。',
                   'official_threshold_pass': None, 'official_score_available': False}
        if args.reference_luts:
            quality = {'verified_this_run': True, 'inherited_from_catalog': False,
                       **submission._reference(frames, target, args.reference_luts, args.threshold)}
        if support.sha(frames) != source_sha:
            raise RuntimeError('运行过程中源像素被改写')
        if model_buffer_hashes != [hashlib.sha256(bytes(buffer)).hexdigest() for buffer in model.buffers]:
            raise RuntimeError('运行过程中固定模型内存被改写')
        _check_unchanged([list_record, *image_records, *model.records,
                          {'path': model_identity['path'], 'sha256': model_identity['sha256']},
                          identities['catalog'], identities['selection'],
                          {'path': str(args.library.resolve()), 'sha256': library.sha256},
                          {'path': evidence_identity['path'], 'sha256': evidence_identity['sha256']}])
        result = {'completed': True, 'candidate_id': candidate['id'], 'actual_config': candidate['config'],
                  'identities': identities, 'model': model_identity, 'context': context,
                  'library': library.record(), 'platform': platform, 'source_pixels_sha256': source_sha,
                  'images': image_records, 'batch_output_sha256': output_sha, 'per_image_output_sha256': per_image,
                  'timings': timings, 'memory': memory, 'quality': quality, 'written_images': written,
                  'official_score_available': False, 'new_speed_ranking_established': False}
        frontier.save_new(output / 'results.json', result)
        return result
    except Exception as error:
        frontier.save_new(output / 'failure.json', {'completed': False, 'candidate_id': candidate['id'],
                          'error': str(error), 'status': 'failed_preserved'})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('catalog', 'selection', 'library', 'images', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--image-root', type=Path, default=support.ROOT)
    parser.add_argument('--write-images', action='store_true')
    parser.add_argument('--reference-luts', type=Path, nargs=4)
    parser.add_argument('--threshold', type=float)
    parser.add_argument('--cpus', help='可选进程亲和CPU编号，以逗号分隔')
    args = parser.parse_args(argv)
    result = run(args)
    print(json.dumps({'completed': result['completed'], 'candidate_id': result['candidate_id'],
                      'batch_output_sha256': result['batch_output_sha256'], 'timings': result['timings'],
                      'quality_verified_this_run': result['quality']['verified_this_run'],
                      'output': str(args.output.resolve())}, ensure_ascii=False, indent=2))
    return 2 if result['quality'].get('all_image_mean_pass') is False else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError) as error:
        print('失败：' + str(error), file=sys.stderr)
        raise SystemExit(1)
