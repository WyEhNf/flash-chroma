"""赛前固定四级RGB8调试入口：体检、配置、拟合与逐图流式执行。"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'flash_chroma_event_v1'
DENSE_FORMAT = 'rgb8-r-g-b-c-bfast'
DENSE_BYTES = 256 ** 3 * 3
RUNTIME_DEFAULT = dict(target='desktop', backend='auto', representation='sparse', threads=4,
                       block_pixels=65536, max_workspace_bytes=48 * 1024 * 1024)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save_new(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def resolve(value, base):
    if not isinstance(value, str) or not value:
        raise ValueError('路径必须是非空字符串')
    path = Path(value).expanduser()
    return (path if path.is_absolute() else Path(base) / path).resolve()


def library_path(value=None, base=ROOT, *, must_exist=True):
    if value:
        path = resolve(os.fspath(value), base)
        if must_exist and not path.is_file():
            raise FileNotFoundError('指定运行库不存在，不自动换库：' + str(path))
        return path
    supplied = os.environ.get('FLASH_CHROMA_LIBRARY')
    if supplied:
        return library_path(supplied, ROOT, must_exist=must_exist)
    roots = [ROOT]
    shared = ROOT.parent.parent / 'projects/16-lut-color'
    if shared.is_dir(): roots.append(shared)
    for root in roots:
        for folder in ('artifacts/single-header-perf-build', 'build-single-header'):
            for name in ('libflash_chroma_bridge.dll', 'libflash_chroma_bridge.so', 'libflash_chroma_bridge.dylib'):
                path = root / folder / name
                if path.is_file(): return path.resolve()
    if not must_exist:
        return (ROOT / 'build-single-header' / ('libflash_chroma_bridge.dll' if os.name=='nt' else 'libflash_chroma_bridge.so')).resolve()
    raise FileNotFoundError('未找到当前单头bridge；先构建single_header或显式设置library')


def load_config(path, library_override=None):
    path = Path(path).resolve()
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        if isinstance(value, dict) and any(key in value for key in ('stages', 'preset', 'photo', 'native_profile')):
            raise ValueError('这是工作台创意配置，不能当作正式四张256³原LUT竞赛配置；请用event init生成独立配置')
        raise ValueError('配置schema须为' + SCHEMA)
    if value.get('dense_format') != DENSE_FORMAT:
        raise ValueError('仅接受dense_format=' + DENSE_FORMAT + '：每份50331648B uint8[R,G,B,C]、B最快；其他位深/格式/轴序须先显式适配')
    if value.get('cpu_only', True) is not True:
        raise ValueError('当前赛事入口只使用CPU，不接受GPU/NPU模式')
    runtime = dict(RUNTIME_DEFAULT)
    provided = value.get('runtime', {})
    if not isinstance(provided, dict) or set(provided) - runtime.keys():
        raise ValueError('runtime字段未知或不是对象，请核对参数拼写')
    runtime.update(provided)
    enums = {'target': ('desktop','mobile','embedded','portable'), 'backend': ('auto','scalar','avx2','avx512'),
             'representation': ('sparse','direct_u8','direct_u16','direct_rgb24')}
    for key, allowed in enums.items():
        if not isinstance(runtime[key], str) or runtime[key] not in allowed:
            raise ValueError('非法运行参数：' + key)
    for key, low, high in (('threads',1,256), ('block_pixels',1,2**63-1), ('max_workspace_bytes',0,2**63-1)):
        if type(runtime[key]) is not int or not low <= runtime[key] <= high:
            raise ValueError(key + '须为合法范围的整数')
    if not isinstance(value.get('profile'),str) or not value['profile']:
        raise ValueError('profile须为固定的非空名称')
    if type(value.get('expected_images',100)) is not int or value.get('expected_images',100)<1:
        raise ValueError('expected_images须为正整数')
    threshold = value.get('threshold')
    if threshold is not None and (isinstance(threshold,bool) or not isinstance(threshold,(int,float)) or not math.isfinite(threshold) or threshold < 0):
        raise ValueError('threshold须为非负有限值或null；门禁按每图未舍入mean严格<T')
    for key in ('write_images', 'validate_c99'):
        if key in value and type(value[key]) is not bool:
            raise ValueError(key + '须为布尔值')
    sources = value.get('source_luts', [])
    if not isinstance(sources, list) or (sources and len(sources) != 4):
        raise ValueError('source_luts须为空列表或按阶段顺序排列的四张原表路径')
    resolved = dict(value, runtime=runtime, config_path=path, base=path.parent)
    for key in ('manifest','image_list'):
        resolved[key] = resolve(value.get(key), path.parent)
    resolved['image_root'] = resolve(value.get('image_root','.'), path.parent)
    resolved['source_luts'] = [resolve(p,path.parent) for p in sources]
    resolved['library'] = library_path(library_override,Path.cwd(),must_exist=False) if library_override else library_path(value.get('library'),path.parent,must_exist=False)
    return value, resolved


def modules():
    return tuple(importlib.import_module(name) for name in ('flash_chroma_support','p16_frontier','p16_submission'))


def image_paths(config):
    lines = [line.strip() for line in config['image_list'].read_text(encoding='utf-8-sig').splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    if not lines: raise ValueError('图片清单不能为空')
    return [resolve(line, config['image_root']) for line in lines]


def batch_size_check(actual, expected, limit):
    """完整执行必须与显式预期数量一致；任何limit调用都只属于调试。"""
    if limit is None and actual != expected:
        raise ValueError(f'图片清单数量{actual}与expected_images={expected}不一致；完整执行拒绝漏图，调试请显式--limit或修改expected_images')
    return limit is None and actual == expected == 100


def model_and_library(config):
    support, frontier, submission = modules()
    value, models = support.load_models(config['manifest'], [config['profile']])
    library = support.Library(config['library'])
    receipt = library.build_receipt
    expected = {name:digest(ROOT/name) for name in ('include/flash_chroma.hpp','include/flash_chroma_c.h')}
    if not receipt or any(receipt.get('headers',{}).get(name) != sha for name,sha in expected.items()):
        raise ValueError('运行库缺少当前头文件的匹配链接回执；请用single_header重新构建，不能把旧DLL当新版本')
    model = models[config['profile']]
    status, requirements = library.query(model, config['runtime'])
    if status:
        hint = '；无OpenMP时把threads设为1' if config['runtime']['threads'] > 1 and not library.capabilities & 4 else ''
        raise ValueError(f'原生资源查询失败：{status} {support.STATUS.get(status)}{hint}')
    return value, model, library, requirements


def reference_records(config, manifest, model):
    _, frontier, _ = modules()
    records = frontier.source_records(config['source_luts']) if config['source_luts'] else []
    declared = model.profile.get('source_luts_sha256', manifest.get('source_luts_sha256'))
    if records and declared != [row['sha256'] for row in records]:
        raise ValueError('当前四张原LUT SHA与所选模型来源不符；请先fit新模型，不能沿用Cinema或其他旧模型')
    if config.get('threshold') is not None and not records:
        raise ValueError('提供threshold时必须同时提供四张原始参考LUT')
    return records


def init_config(output, *, library=None, manifest=None, profile='max_first', images=None, image_root=None):
    output = Path(output).resolve()
    if output.exists(): raise FileExistsError('配置文件已存在，拒绝覆盖：' + str(output))
    manifest = Path(manifest or ROOT/'data/p16-frontier/models/manifest.json').resolve()
    images = Path(images or ROOT/'assets/photos/eval.txt').resolve()
    sources = []
    if manifest.is_file():
        record = json.loads(manifest.read_text(encoding='utf-8'))
        base = Path(record.get('path_root',manifest.parent))
        if not base.is_absolute(): base = manifest.parent/base
        sources = [resolve(row['path'],base) for row in record.get('original_luts',[])]
    rel = lambda path: Path(os.path.relpath(Path(path).resolve(),output.parent)).as_posix()
    value = {'schema':SCHEMA, 'cpu_only':True, 'dense_format':DENSE_FORMAT,
        'library':rel(library_path(library,Path.cwd(),must_exist=False)), 'manifest':rel(manifest), 'profile':profile,
        'image_list':rel(images), 'image_root':rel(Path(image_root or ROOT)), 'source_luts':[rel(path) for path in sources],
        'runtime':dict(RUNTIME_DEFAULT), 'fit':{'m':[33,33,33,33], 'method':'sample_interp', 'grid':'uniform','alpha':.5,'exponent':.4},
        'threshold':None, 'write_images':True, 'validate_c99':True, 'expected_images':100,
        '_说明':{'输入':'默认是已见Cinema示例；新题四张原表替换source_luts后先fit，不能直接沿用旧manifest。',
            '格式':'四原表各50331648B，uint8[R,G,B,C]，B索引最快；其他正式格式需先显式转换。',
            '路径':'本JSON内路径相对本JSON目录；图片清单内路径相对image_root。',
            '参数':'整批冻结同一profile/runtime；四级m可各不相同且17..33。默认Sparse避免未知LUT的调色板容量失败。',
            '门禁':'把赛方给定T填入threshold；每图全像素RGB欧氏mean必须严格<T。null不宣称过线。',
            '计时':'run默认逐图流式，映射/准备/应用wall分列；不是预载100图吞吐排名。'}}
    save_new(output,value)
    return {'completed':True,'config':str(output),'schema':SCHEMA,'next':'doctor --config '+str(output)}


def doctor(config_path, library=None):
    checks, errors, report = [], [], {'schema':SCHEMA,'mode':'doctor','cpu_only':True,'checks':[]}
    def check(name, function):
        try:
            result = function(); checks.append({'name':name,'passed':True,'detail':result}); return result
        except Exception as error:
            errors.append(name+'：'+str(error)); checks.append({'name':name,'passed':False,'error':str(error)}); return None
    for name in ('numpy','PIL','scipy'):
        check('依赖 '+name, lambda name=name: {'version':getattr(importlib.import_module(name),'__version__','可导入'),
                                             'purpose':'离线fit' if name=='scipy' else '原生FFI/图像'})
    loaded = check('配置与路径',lambda:load_config(config_path,library))
    if loaded:
        raw, config = loaded
        if library: config['library'] = library_path(library,Path.cwd(),must_exist=False)
        checks[-1]['detail'] = {'config':str(config['config_path']),'sha256':digest(config['config_path']),
            'library':str(config['library']),'manifest':str(config['manifest']), 'image_list':str(config['image_list'])}
        actual = check('当前原生库与固定模型',lambda:model_and_library(config))
        if actual:
            manifest, model, engine, requirements = actual
            checks[-1]['detail'] = {'library':engine.record(),'profile':config['profile'],'runtime':config['runtime'],
                'model_records':model.records,'requirements':requirements,'prepare_executed':False,
                'palette_qualification':'direct资格在run完整准备时决定，query通过不代替容量验收'}
            check('四原表来源',lambda:reference_records(config,manifest,model))
        paths = check('图片路径',lambda:image_paths(config))
        if paths:
            missing = [str(path) for path in paths if not path.is_file()]
            expected = config.get('expected_images',100)
            checks[-1]['passed'] = not missing and len(paths)==expected
            checks[-1]['detail'] = {'count':len(paths),'expected':config.get('expected_images',100),'missing':missing,
                'scope':'此处只查文件；run逐张验证1024×768、RGB8及真实容器位深。'}
            if missing: errors.append('图片文件缺失')
            if len(paths)!=expected: errors.append(f'图片清单数量{len(paths)}与expected_images={expected}不一致；请补齐或显式配置调试数量')
        usage = shutil.disk_usage(config['base'])
        checks.append({'name':'配置盘可用空间','passed':usage.free>=16*1024**2,
            'detail':{'free_bytes':usage.free,'minimum_log_reserve_bytes':16*1024**2,'png_per_image_uncompressed_bytes':1024*768*3}})
        if usage.free<16*1024**2: errors.append('可用空间不足16MiB，请更换输出盘')
    report.update(ready=not errors,checks=checks,errors=errors,environment={'platform':platform.platform(),'machine':platform.machine(),'python':sys.version},
        timing_qualified=False,official_score_available=False)
    return report


def fit_event(config_path, output):
    raw, config = load_config(config_path); _,frontier,_ = modules(); output = Path(output).resolve()
    if output.exists(): raise FileExistsError('拟合目录已存在，拒绝覆盖：'+str(output))
    if len(config['source_luts']) != 4: raise ValueError('fit需要四张新的256³原始RGB8 LUT')
    params = dict(m=[33]*4,method='sample_interp',grid='uniform',alpha=.5,exponent=.4); params.update(raw.get('fit',{}))
    started = time.perf_counter_ns()
    try:
        manifest = frontier.fit_candidate(config['source_luts'],params['m'],params['method'],params['grid'],output,
                                           alpha=params['alpha'],exponent=params['exponent'])
        new_config = dict(raw,manifest='source-manifest.json',profile='fitted')
        for name in ('library','image_list','image_root'):
            new_config[name] = Path(os.path.relpath(config[name],output)).as_posix()
        new_config['source_luts'] = [Path(os.path.relpath(path,output)).as_posix() for path in config['source_luts']]
        save_new(output/'run-config.json',new_config)
        result = {'completed':True,'fit_wall_ms':(time.perf_counter_ns()-started)/1e6,'m':params['m'],
            'manifest':str(output/'source-manifest.json'),'run_config':str(output/'run-config.json'),
            'status':'fitted_pending_chain_accuracy_and_runtime_validation','official_score_available':False,
            'next_command':[sys.executable,str(Path(__file__).resolve()),'run','--config',str(output/'run-config.json'),'--output',str(output.with_name(output.name+'-run'))]}
        save_new(output/'event-fit.json',result); return result
    except Exception as error:
        if output.is_dir(): save_new(output/'event-fit-failure.json',{'completed':False,'error':str(error),'scope':'失败及已生成阶段保留，不覆盖重试'})
        raise


def run_event(config_path, output, *, library=None, profile=None, limit=None, threshold=None):
    raw, config = load_config(config_path,library)
    if library: config['library'] = library_path(library,Path.cwd(),must_exist=False)
    if profile: config['profile'] = profile
    if threshold is not None:
        if isinstance(threshold,bool) or not math.isfinite(threshold) or threshold<0: raise ValueError('非法threshold')
        config['threshold'] = threshold
    if limit is not None and (type(limit) is not int or limit<1): raise ValueError('limit须为正整数')
    output = Path(output).resolve()
    if output.exists(): raise FileExistsError('执行目录已存在，拒绝覆盖：'+str(output))
    output.mkdir(parents=True); rows=[]; begin=time.perf_counter_ns()
    try:
        support,frontier,submission = modules()
        support.native.setup(cpus=raw.get('cpus'))
        manifest,model,engine_library,requirements = model_and_library(config)
        sources = reference_records(config,manifest,model)
        paths = image_paths(config); total_available = len(paths)
        expected_images = config.get('expected_images',100)
        competition_size_batch = batch_size_check(total_available,expected_images,limit)
        paths = paths[:limit] if limit else paths
        model_identity = {'path':str(config['manifest']),'sha256':digest(config['manifest']),'profile':config['profile'],'records':model.records}
        identities = {'config':{'path':str(config['config_path']),'sha256':digest(config['config_path'])},
            'image_list':{'path':str(config['image_list']),'sha256':digest(config['image_list'])},'model':model_identity,
            'library':engine_library.record(),'sources':sources,'script':{'path':str(Path(__file__).resolve()),'sha256':digest(__file__)}}
        plan = {'schema':SCHEMA,'mode':'run','cpu_only':True,'runtime':config['runtime'],'identities':identities,
            'threshold':config.get('threshold'),'validation_c99':raw.get('validate_c99',True),'write_images':raw.get('write_images',True),
            'images_available':total_available,'images_requested':len(paths),'expected_images':expected_images,'limit':limit,
            'batch_parameters_fixed':True,'dense_format':DENSE_FORMAT,'environment':support.native.environment(),
            'scope':'逐图流式；非旧图集绑定，不继承预载百图时间；单次观测无稳定排名资格'}
        save_new(output/'executed-plan.json',plan)
        if raw.get('write_images',True): (output/'images').mkdir()
        with ExitStack() as stack, engine_library.create(model,config['runtime']) as runtime:
            import numpy as np
            from PIL import Image
            tables=[]
            for record in sources:
                table=np.memmap(record['path'],np.uint8,'r',shape=(256,256,256,3));stack.callback(table._mmap.close);tables.append(table)
            for index,path in enumerate(paths):
                start=time.perf_counter_ns(); file_sha=digest(path); source=submission._rgb8(path); read_ms=(time.perf_counter_ns()-start)/1e6
                target=np.empty_like(source); apply_ms=runtime.apply(source,target); start=time.perf_counter_ns()
                equal=None
                if raw.get('validate_c99',True):
                    scalar=np.empty_like(source)
                    if engine_library.c_apply(model,source,scalar): raise RuntimeError('独立C99映射失败')
                    equal=bool(np.array_equal(target,scalar))
                    if not equal: raise RuntimeError('原生C++/独立C99字节不一致：'+str(path))
                    del scalar
                quality=None
                if tables:
                    truth=source
                    for table in tables: truth=table[truth[...,0],truth[...,1],truth[...,2]]
                    quality=submission._error_row(target,truth);del truth
                validation_ms=(time.perf_counter_ns()-start)/1e6
                output_sha=support.sha(target); written=None;write_ms=0.
                if raw.get('write_images',True):
                    if shutil.disk_usage(output).free < target.nbytes+16*1024**2: raise OSError('输出盘空间不足，保留已完成结果')
                    start=time.perf_counter_ns();destination=output/'images'/f'{index+1:04d}.png'
                    with destination.open('xb') as stream: Image.fromarray(target).save(stream,format='PNG')
                    write_ms=(time.perf_counter_ns()-start)/1e6;written={'path':str(destination),'sha256':digest(destination)}
                row={'index':index,'input':{'path':str(path),'sha256':file_sha,'pixel_sha256':support.sha(source)},
                    'output_pixel_sha256':output_sha,'written':written,'width':1024,'height':768,'runtime_equal_c99':equal,
                    'read_decode_ms':read_ms,'apply_ms':apply_ms,'validation_ms':validation_ms,'png_write_ms':write_ms,
                    'mapping_image_buffer_bytes':source.nbytes+target.nbytes,'quality':quality}
                rows.append(row)
                with (output/'images.jsonl').open('a',encoding='utf-8',newline='\n') as stream: stream.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
                del source,target
            resources=dict(runtime.info);native_prepare_ms=runtime.prepare_ms;preparation=runtime.preparation
        for record in [identities['config'],identities['image_list'],{'path':model_identity['path'],'sha256':model_identity['sha256']},
                       *model.records,*sources,identities['library'],identities['script'],*(row['input'] for row in rows)]:
            if digest(record['path']) != record['sha256']: raise RuntimeError('运行期间固定文件被修改：'+record['path'])
        quality=submission.accuracy_summary([dict(index=row['index'],**row['quality']) for row in rows],config.get('threshold')) if sources else {'verified':False,'all_image_mean_pass':None,'official_threshold_pass':None,'official_score_available':False}
        result={'schema':SCHEMA,'completed':True,'mode':'run','cpu_only':True,'records':rows,'identities':identities,
            'actual_runtime':dict(config['runtime'],backend={1:'scalar',2:'avx2'}[resources['selected_backend']]),
            'profile':config['profile'],'parameters_fixed_for_entire_batch':True,'resources':resources,'preparation':preparation,
            'quality':quality,'mapping_total_ms':math.fsum(row['apply_ms'] for row in rows),'native_prepare_ms':native_prepare_ms,
            'application_wall_ms':(time.perf_counter_ns()-begin)/1e6,'images_completed':len(rows),'images_available':total_available,
            'full_requested_list_completed':len(rows)==total_available,'competition_size_batch':competition_size_batch,
            'expected_images':expected_images,'debug_subset':limit is not None or expected_images!=100,
            'mapping_controlled_bytes':resources['model_bytes']+resources['arena_bytes']+resources['object_bytes']+max(row['mapping_image_buffer_bytes'] for row in rows),
            'reference_mapping_bytes':len(sources)*DENSE_BYTES,'dense_format':DENSE_FORMAT,'time_stable':False,'official_score_available':False,
            'timing_scope':'mapping_total只含逐图原生FFI；prepare单列；application含配置/模型/原表SHA、逐图解码、校验、可选PNG及末尾身份复查，不等于预载100图速度。',
            'memory_scope':'模型+完整arena+Runtime+最大单图输入输出为受控映射容量；参考、C99、色差、编码、Python和OS另计，非RSS上界。'}
        save_new(output/'results.json',result);return result
    except Exception as error:
        save_new(output/'failure.json',{'schema':SCHEMA,'completed':False,'error':str(error),'completed_images':len(rows),'records':rows,
            'scope':'失败及已写PNG/JSONL保留；修改配置后选新输出目录，不覆盖重试'})
        raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    init=sub.add_parser('init',help='生成独立可编辑的中文说明配置');init.add_argument('--output',type=Path,required=True)
    for flag in ('library','manifest','images','image-root'):init.add_argument('--'+flag,type=Path)
    init.add_argument('--profile',default='max_first')
    for mode in ('doctor','fit','run'):
        command=sub.add_parser(mode);command.add_argument('--config',type=Path,required=True);command.add_argument('--output',type=Path,required=mode in ('fit','run'))
        if mode in ('doctor','run'):command.add_argument('--library',type=Path)
        if mode=='run':
            command.add_argument('--profile');command.add_argument('--limit',type=int);command.add_argument('--threshold',type=float)
    args=parser.parse_args(argv)
    try:
        if args.mode=='init': result=init_config(args.output,library=args.library,manifest=args.manifest,profile=args.profile,images=args.images,image_root=args.image_root)
        elif args.mode=='doctor':
            result=doctor(args.config,args.library)
            if args.output:save_new(args.output,result)
        elif args.mode=='fit':result=fit_event(args.config,args.output)
        else:result=run_event(args.config,args.output,library=args.library,profile=args.profile,limit=args.limit,threshold=args.threshold)
        if args.mode=='run':
            summary={key:result[key] for key in ('completed','images_completed','competition_size_batch','mapping_total_ms','native_prepare_ms','application_wall_ms')}
            summary.update(output=str(args.output.resolve()),expected_images=result['expected_images'],debug_subset=result['debug_subset'],all_image_mean_pass=result['quality'].get('all_image_mean_pass'),official_score_available=False)
        else:summary=result
        print(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
        return 2 if (args.mode=='doctor' and not result['ready']) or (args.mode=='run' and result['quality'].get('all_image_mean_pass') is False) else 0
    except Exception as error:
        print(json.dumps({'completed':False,'error':str(error),'mode':args.mode},ensure_ascii=False),file=sys.stderr)
        return 1


if __name__=='__main__': raise SystemExit(main())
