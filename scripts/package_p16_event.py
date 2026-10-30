"""构建并只读验证本机离线调试包；不下载资产，不覆盖旧包。"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'flash_chroma_local_packet_v1'
RUNTIME_PATTERN = re.compile(r'^(libgcc_s_.+|libstdc\+\+-\d+|libgomp-\d+|libwinpthread-\d+|libssp-\d+|libquadmath-\d+)\.dll$', re.I)


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')


def safe_relative(value):
    name=Path(value)
    if name.anchor or '..' in name.parts or ':' in str(name):raise ValueError('包内路径非法：'+str(value))
    return name


def package_files(directory):
    return sorted(path for path in Path(directory).rglob('*') if path.is_file() and path.name!='MANIFEST.json')


def verify(directory,archive=None):
    directory=Path(directory).resolve();manifest=read(directory/'MANIFEST.json')
    if manifest.get('schema')!=SCHEMA:raise ValueError('不支持的离线包清单')
    members=manifest['members']
    for name,record in members.items():
        path=(directory/safe_relative(name)).resolve()
        if not path.is_relative_to(directory) or not path.is_file() or path.stat().st_size!=record['bytes'] or digest(path)!=record['sha256']:
            raise ValueError('包成员身份不符：'+name)
    archive=Path(archive).resolve() if archive else None
    if archive:
        prefix=manifest['package_name']+'/'
        with zipfile.ZipFile(archive) as zipped:
            wanted={prefix+name for name in members}|{prefix+'MANIFEST.json'}
            if set(zipped.namelist())!=wanted or len(zipped.namelist())!=len(wanted):raise ValueError('ZIP成员缺失、多余或重复')
            if zipped.read(prefix+'MANIFEST.json')!=(directory/'MANIFEST.json').read_bytes():raise ValueError('ZIP清单字节不符')
            for name,record in members.items():
                payload=zipped.read(prefix+name)
                if len(payload)!=record['bytes'] or hashlib.sha256(payload).hexdigest()!=record['sha256']:
                    raise ValueError('ZIP成员身份不符：'+name)
    return {'passed':True,'schema':SCHEMA,'directory':str(directory),'members':len(members),
            'member_bytes':sum(r['bytes'] for r in members.values()),'manifest_sha256':digest(directory/'MANIFEST.json'),
            'archive':str(archive) if archive else None,'archive_sha256':digest(archive) if archive else None,
            'scope':'只读核对原包成员；不重写、不重新映射或测速。用户后续输出不并入原始成员清单。'}


def runtime_dependencies(binary,mingw_bin,objdump):
    dependencies={};system=set();queue=[Path(binary).resolve()];seen=set()
    system_folder=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32'
    while queue:
        path=queue.pop(0)
        if path.name.lower() in seen:continue
        seen.add(path.name.lower())
        output=subprocess.check_output([str(objdump),'-p',str(path)]).decode('utf-8','replace')
        for name in re.findall(r'DLL Name:\s*([^\s]+)',output):
            if RUNTIME_PATTERN.fullmatch(name):
                source=next((folder/name for folder in (path.parent,Path(mingw_bin)) if (folder/name).is_file()),None)
                if source is None:raise FileNotFoundError('缺少MinGW运行依赖：'+name)
                if name.lower() not in dependencies:
                    dependencies[name.lower()]=source.resolve();queue.append(source.resolve())
            elif name.lower().startswith(('api-ms-win-','ext-ms-win-')) or (system_folder/name).is_file():
                system.add(name)
            else:raise ValueError('未确认来源的非系统依赖，不静默省略：'+name)
    return list(dependencies.values()),sorted(system)


def probe_python(python):
    code='''import json,sys,platform,numpy,PIL
try:
 import scipy; scipy_version=scipy.__version__
except ImportError:scipy_version=None
print(json.dumps(dict(python=sys.version,executable=sys.executable,numpy=numpy.__version__,pillow=PIL.__version__,scipy=scipy_version,platform=platform.platform(),machine=platform.machine())))'''
    value=json.loads(subprocess.check_output([str(python),'-X','utf8','-c',code],text=True,encoding='utf-8'))
    value.update(executable_sha256=digest(python),python_bundled=False,
        scope='复用本机已安装Python及NumPy/Pillow；fit另需SciPy。路径仅作本机定位，可用FLASH_CHROMA_PYTHON替换；不宣称跨机免依赖。')
    return value


def build(output,python,library,cpp_runner,mingw_bin):
    output=Path(output).resolve();archive=output.with_suffix('.zip');receipt_path=archive.with_name(archive.name+'.sha256.json')
    if output.exists() or archive.exists() or receipt_path.exists():raise FileExistsError('包目录、ZIP或回执已存在，拒绝覆盖')
    python=Path(python).resolve();library=Path(library).resolve();cpp_runner=Path(cpp_runner).resolve();mingw_bin=Path(mingw_bin).resolve()
    if os.name!='nt' or library.suffix.lower()!='.dll' or cpp_runner.suffix.lower()!='.exe':raise ValueError('当前打包入口仅验收Windows同机离线包；不伪称跨机/跨平台成品')
    objdump=mingw_bin/'objdump.exe'
    for path in (python,library,cpp_runner,objdump):
        if not path.is_file():raise FileNotFoundError(str(path))
    library_receipt=read(str(library)+'.build.json')
    if library_receipt['library_sha256']!=digest(library):raise ValueError('DLL与链接来源回执不符')
    for name,sha in library_receipt['headers'].items():
        if digest(ROOT/name)!=sha:raise ValueError('当前交付头与DLL不符：'+name)
    environment=probe_python(python);catalog=read(ROOT/'gui/studio_catalog.json');photos_manifest=read(ROOT/'assets/photos/manifest.json')
    photo_records={row['evaluation']['path']:row['evaluation'] for row in photos_manifest['images']}
    photo_list=[line.strip() for line in (ROOT/'assets/photos/eval.txt').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if len(photo_list)!=100 or len(set(photo_list))!=100:raise ValueError('本机样例包必须明确含100个已有独立评测路径')
    if len(catalog['photos'])<16 or len(catalog['luts'])<18 or len(catalog['presets'])<12:raise ValueError('Studio素材目录不足')
    bridge_deps,bridge_system=runtime_dependencies(library,mingw_bin,objdump)
    cpp_deps,cpp_system=runtime_dependencies(cpp_runner,mingw_bin,objdump)
    output.mkdir(parents=True);copied={};started=time.perf_counter()
    def copy(source,relative=None,expected=None):
        source=Path(source).resolve();relative=safe_relative(relative or source.relative_to(ROOT));name=relative.as_posix()
        actual=digest(source)
        if expected and actual!=expected:raise ValueError('来源SHA不符：'+str(source))
        destination=output/relative
        if destination.exists():
            if digest(destination)!=actual:raise ValueError('包路径冲突：'+name)
            return
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)
        if digest(destination)!=actual:raise ValueError('落盘SHA不符：'+name)
        copied[name]={'source':str(source),'sha256':actual,'bytes':source.stat().st_size}
    try:
        # 明确允许的源文件树，不枚举.git、缓存、密钥或用户配置。
        for folder in ('include','src','single_header','python/lutlab','experiments/camera-raw-workflow'):
            for source in sorted((ROOT/folder).rglob('*')):
                if source.is_file() and (source.suffix in ('.hpp','.h','.inc','.cpp','.c','.cmake','.py') or source.name=='CMakeLists.txt'):
                    copy(source)
        for source in sorted((ROOT/'tests').glob('single_header*')):
            if source.is_file():copy(source)
        for source in sorted((ROOT/'tests').glob('*event*.py')):copy(source)
        for name in ('start-gui.ps1','start-event.ps1','pixi.toml','pixi.lock','PROBLEM.md','docs/event-quickstart.md','docs/single-header-runtime.md',
                     'gui/server.py','gui/studio.py','gui/worker.py','gui/studio_smoke_test.py','gui/README.md',
                     'report/data/p16-frontier-header-20261027/results.json',
                     'experiments/camera-raw-workflow-v1.json','report/data/camera-raw-workflow-v1/summary.json'):
            if (ROOT/name).is_file():copy(ROOT/name)
        for source in sorted((ROOT/'gui/static').rglob('*')):
            if source.is_file():copy(source)
        # FFI、固定模型/拟合、独立参考及重建目录的直接本地模块闭包。
        seeds={'p16_event','p16_frontier','flash_chroma_support','p16_submission','p16_unified_support',
               'prepare_studio_catalog','generate_flash_chroma_header','package_p16_event'}
        pending=list(seeds);seen=set()
        while pending:
            name=pending.pop()
            if name in seen:continue
            seen.add(name);source=ROOT/'scripts'/(name+'.py')
            if not source.is_file():continue
            copy(source)
            for node in ast.walk(ast.parse(source.read_text(encoding='utf-8-sig'))):
                names=[a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else ([node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else [])
                for child in names:
                    if (ROOT/'scripts'/(child+'.py')).is_file():pending.append(child)
        for name in ('assets/photos/README.md','assets/photos/manifest.json','assets/photos/eval.txt','assets/photos/kodak/README.md',
                     'assets/LUT/README.md','assets/LUT/manifest.json','assets/LUT/source-lock.json',
                     'assets/LUT/sources/stripedpurple/LICENSE','assets/LUT/sources/stripedpurple/UPSTREAM_README.md'):
            copy(ROOT/name)
        for name in photo_list:
            if name not in photo_records:raise ValueError('评测图没有来源回执：'+name)
            copy(ROOT/name,expected=photo_records[name]['sha256'])
        for row in catalog['photos']:
            if row['path'] not in photo_list:raise ValueError('代表图不在本包100图内：'+row['id'])
            if digest(output/row['path'])!=row['sha256']:raise ValueError('代表图SHA不符')
        for row in catalog['luts']:copy(ROOT/row['path'],expected=row['sha256'])
        for source in sorted((ROOT/'assets/photos/previews').glob('*.jpg')):copy(source)
        original_model=ROOT/'data/p16-frontier/models/manifest.json';model=read(original_model)
        copy(original_model,'provenance/model-manifest.original.json')
        for profile in model['profiles'].values():
            for row in profile['models']+[r for r in profile['sidecars'] if r]:
                relative=safe_relative(row['path']);copy(original_model.parent/relative,Path('data/p16-frontier/models')/relative,row['sha256'])
        for row in model.get('licenses',[]):
            relative=safe_relative(row['path']);copy(original_model.parent/relative,Path('data/p16-frontier/models')/relative,row['sha256'])
        omitted=model.pop('original_luts',[])
        model['original_luts']=[];model['packet_source_manifest_sha256']=digest(original_model)
        model['packet_note']='本机样例包未包含四张50MiB密集原LUT，已移除原工作树绝对路径；各稀疏对象/sidecar/许可SHA保留。不能据样例声明新输入精度。'
        save(output/'data/p16-frontier/models/manifest.json',model)
        copy(ROOT/'gui/studio_catalog.json','provenance/studio-catalog.original.json')
        for choice in catalog['presets']:
            if choice.get('mode')=='native':choice['native_manifest_sha256']=digest(output/choice['native_manifest'])
        save(output/'gui/studio_catalog.json',catalog)
        library_relative=Path('artifacts/single-header-perf-build')/library.name
        copy(library,library_relative);copy(Path(str(library)+'.build.json'),str(library_relative)+'.build.json')
        dependency_records=[]
        for binary,relative,deps,system in ((library,library_relative,bridge_deps,bridge_system),(cpp_runner,Path('bin/flash_chroma_run.exe'),cpp_deps,cpp_system)):
            if binary==cpp_runner:copy(binary,relative)
            records=[]
            for source in deps:
                destination=relative.parent/source.name;copy(source,destination)
                records.append({'path':destination.as_posix(),'sha256':digest(source),'bytes':source.stat().st_size})
            dependency_records.append({'binary':relative.as_posix(),'tool':'objdump -p','runtime_dlls':records,'system_dlls_not_copied':system})
        for folder in ('gcc','mingw-w64'):
            for source in sorted((mingw_bin.parent/'licenses'/folder).rglob('*')):
                if source.is_file():copy(source,Path('licenses/mingw')/folder/source.relative_to(mingw_bin.parent/'licenses'/folder))
        if (ROOT/'artifacts/event-cpp-build/compile_commands.json').is_file():copy(ROOT/'artifacts/event-cpp-build/compile_commands.json','provenance/cpp-compile-commands.json')
        save(output/'DEPENDENCIES.json',{'records':dependency_records,'scope':'递归核对MinGW PE依赖；复制编译器运行DLL及其许可，不复制Windows系统DLL。'})
        save(output/'LOCAL-RUNTIME.json',environment)
        demo={'schema':'flash_chroma_event_v1','cpu_only':True,'dense_format':'rgb8-r-g-b-c-bfast',
            'library':library_relative.as_posix(),'manifest':'data/p16-frontier/models/manifest.json','profile':'max_first',
            'image_list':'assets/photos/eval.txt','image_root':'.','source_luts':[],
            'runtime':{'target':'desktop','backend':'auto','representation':'sparse','threads':4,'block_pixels':65536,'max_workspace_bytes':48*1024**2},
            'fit':{'m':[33,33,33,33],'method':'sample_interp','grid':'uniform','alpha':.5,'exponent':.4},
            'threshold':None,'write_images':True,'validate_c99':True,'expected_images':100,
            '_说明':{'用途':'仅本机Cinema样例，非明日正式四LUT；threshold=null，未提供原密集参考，不声明质量过线或正式分数。',
                '正式输入':'先init新配置，显式提供四张256³RGB8原表并fit；格式/位深/轴序不符时先适配，不将创意UI组合当正式输入。',
                '路径':'均相对此JSON；正式4原表未包含在包中；只保留稀疏模型对象与原始来源摘要。'}}
        save(output/'event-demo.json',demo)
        launcher='''param(
    [ValidateSet('studio','doctor','init','fit','run')][string]$Mode = 'studio',
    [string]$Config = 'event-demo.json', [string]$Output, [string]$Library,
    [string]$Manifest, [string]$Images, [string]$ImageRoot,
    [Alias('Profile')][string]$ModelProfile, [int]$Limit, [double]$Threshold,
    [ValidateRange(0,65535)][int]$Port = 8765, [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
$packetRoot = $PSScriptRoot
if (-not $env:FLASH_CHROMA_PYTHON) {
    $runtime = Get-Content -LiteralPath (Join-Path $packetRoot 'LOCAL-RUNTIME.json') -Raw | ConvertFrom-Json
    if (-not (Test-Path -LiteralPath $runtime.executable -PathType Leaf)) {
        throw '记录的本机Python不存在，请先设置FLASH_CHROMA_PYTHON为已安装NumPy/Pillow的Python完整路径。'
    }
    $env:FLASH_CHROMA_PYTHON = $runtime.executable
}
$arguments = @{}
foreach ($key in $PSBoundParameters.Keys) { $arguments[$key] = $PSBoundParameters[$key] }
$arguments['Mode'] = $Mode
$arguments['Config'] = $Config
Push-Location -LiteralPath $packetRoot
try { & (Join-Path $packetRoot 'start-event.ps1') @arguments }
finally { Pop-Location }
'''
        (output/'start-local.ps1').write_text(launcher,encoding='utf-8',newline='\r\n')
        readme='''# Flash Chroma 本机离线调试包

本包包含当前独立hpp/h、维护源码、CMake/bridge/C++连续RGB8入口、照片工作台、17套组合、18份原始CUBE及许可、7套模型对象、100张1024×768真实PNG及来源。只复制明确清单中的公开项目文件，不包含Git、私密配置、RAW大素材、厂商解码工具或四张密集原LUT。

## 在同一电脑搬目录后运行

```powershell
.\\start-local.ps1
.\\start-local.ps1 -Mode doctor -Config event-demo.json
.\\start-local.ps1 -Mode run -Config event-demo.json -Output my-debug-run -Limit 1
.\\bin\\flash_chroma_run.exe --help
```

默认打开Studio，只监听127.0.0.1。若端口占用会选新端口。图片和处理结果留在本机。RAW入口仅保留源代码和元数据；它所需的原素材、厂商解码器、WSL/OCIO/OpenEXR没有打入本包，不宣称RAW流程离线可用。

Python环境没有打包。LOCAL-RUNTIME.json记录本机实际Python/NumPy/Pillow和可选SciPy；默认复用该Python。搬到另一电脑应安装依赖并设置：

```powershell
$env:FLASH_CHROMA_PYTHON = '你已准备好的Python完整路径'
.\\start-local.ps1 -Mode doctor -Config event-demo.json
```

原生DLL与C++exe附有递归核对的MinGW运行DLL及许可，不复制Windows系统DLL。此包是已测Windows同机包，不承诺跨系统、跨ABI或无依赖运行。需改C++时用single_header目录重新构建；原.hpp/.h及测试源都在包中。

## 明日正式数据

1. 用init新建配置，替换正式图片列表/image_root和四个source_luts。
2. 当前适配格式是每份50331648B、uint8[R,G,B,C]且B索引最快。正式文件位深、格式或轴序不同必须先显式适配，不能只改扩展名。
3. fit四原表生成新source-manifest.json及run-config.json，再用新配置run。四级m可不同，均17..33，整批固定。未知LUT默认Sparse；direct的容量资格由实际prepare决定。
4. 把赛方T填threshold，每图全像素mean RGB欧氏差严格<T；图数须符合expected_images。显式-Limit只用于调试，不能标成正式百图。没有密集参考/T就不声明质量过线。

```powershell
.\\start-local.ps1 -Mode init -Output event-new.json
# 编辑event-new.json，填正式四原表及图片；不要沿用示例Cinema的manifest。
.\\start-local.ps1 -Mode fit -Config event-new.json -Output fitted-new
.\\start-local.ps1 -Mode run -Config fitted-new/run-config.json -Output official-debug
```

所有输出拒绝覆盖。GUI导出的创意组合JSON会被正式入口明确拒绝。逐图流式耗时与预载百图基准分列，不估算官方分数。更多实际参数见docs/event-quickstart.md。

event-demo.json是已见Cinema样例，source_luts为空、threshold=null，质量未验；独立C99只核对本图实现一致性。SELF-CHECK保存构建时从包目录实际doctor及限1图运行的原始回执、PNG和像素SHA；绝对路径仅反映那次运行，不是搬目录后的路径要求。

## 素材和只读核验

照片保留Kodak/DPED/DIV2K来源，其中DIV2K限学术研究；不能把本包或这些图片自动改授代码许可证。CUBE来自Striped Purple，保留MIT许可。各原说明在assets/photos与assets/LUT，模型许可在data/p16-frontier/models，MinGW许可在licenses/mingw。

```powershell
& $env:FLASH_CHROMA_PYTHON scripts/package_p16_event.py verify --package .
# 可额外 --zip 旁边的ZIP，核对全部ZIP成员原字节。
```

MANIFEST.json逐成员记录SHA256与尺寸，ZIP另有外部SHA回执。verify只读，不重写包或重新测速。用户后续运行生成的新输出不属于原包成员；原成员改动会被发现。PNG/资产没有上传到任何外部服务。
'''
        (output/'README-LOCAL.md').write_text(readme,encoding='utf-8',newline='\n')
        (output/'SELF-CHECK').mkdir()
        commands=[('cpp-help',[str(output/'bin/flash_chroma_run.exe'),'--help']),
                  ('catalog',[str(python),'-B','-X','utf8','scripts/prepare_studio_catalog.py','--check']),
                  ('doctor',[str(python),'-B','-X','utf8','scripts/p16_event.py','doctor','--config','event-demo.json','--output','SELF-CHECK/doctor.json']),
                  ('run',[str(python),'-B','-X','utf8','scripts/p16_event.py','run','--config','event-demo.json','--output','SELF-CHECK/run','--limit','1'])]
        smoke_code='''import hashlib,json
from pathlib import Path
from PIL import Image
from gui.studio import StudioService
root=Path.cwd().resolve()
run=json.loads((root/'SELF-CHECK/run/results.json').read_text(encoding='utf-8'))
record=run['records'][0]
with Image.open(record['written']['path']) as image:
 image.load()
 assert image.mode=='RGB' and image.size==(1024,768)
 assert hashlib.sha256(image.tobytes()).hexdigest()==record['output_pixel_sha256']
service=StudioService(root=root,library=root/'artifacts/single-header-perf-build/libflash_chroma_bridge.dll')
renders=[]
try:
 assert service.library.path.resolve().is_relative_to(root)
 for preset in ('native-default','native-max-first','natural-clear'):
  response,pixels=service.render({'preset':preset,'threads':1},preview_size=192,keep=False)
  assert response['metrics']['runtime_equal'] is True
  assert hashlib.sha256(pixels.tobytes()).hexdigest()==response['metrics']['output_sha256']
  renders.append(response)
 assert service.native_manifest[1].is_relative_to(root)
finally:service.close()
print(json.dumps({'passed':True,'png_pixel_sha256':record['output_pixel_sha256'],'studio_renders':renders},ensure_ascii=False))
'''
        commands.append(('png-studio',[str(python),'-B','-X','utf8','-c',smoke_code]))
        invocations=[]
        for name,command in commands:
            completed=subprocess.run(command,cwd=output,capture_output=True,text=True,encoding='utf-8',errors='replace')
            (output/'SELF-CHECK'/(name+'-stdout.log')).write_text(completed.stdout,encoding='utf-8')
            (output/'SELF-CHECK'/(name+'-stderr.log')).write_text(completed.stderr,encoding='utf-8')
            invocations.append({'name':name,'command':command,'cwd':str(output),'returncode':completed.returncode})
            if completed.returncode:raise RuntimeError('包内实际'+name+'失败：'+completed.stderr[-1000:])
        run=read(output/'SELF-CHECK/run/results.json')
        if run['images_completed']!=1 or run['competition_size_batch'] or run['quality'].get('verified') is not False or run['records'][0]['runtime_equal_c99'] is not True:
            raise ValueError('包内样例运行的资格/一致性回执不符合约定')
        studio_check=read(output/'SELF-CHECK/png-studio-stdout.log')
        save(output/'SELF-CHECK/verification.json',{'passed':True,'invocations':invocations,'image_and_studio':studio_check,
             'scope':'从包目录实际目录检查、doctor及限1图原生/C99映射，PNG像素SHA回读及两个native和一个creative渲染；没有正式百图或性能排名。'})
        if any(path.name=='__pycache__' or path.suffix=='.pyc' for path in output.rglob('*')):raise ValueError('包中出现Python缓存，拒绝发布')
        manifest={'schema':SCHEMA,'package_name':output.name,'cpu_only':True,'photos':100,'curated_photos':len(catalog['photos']),
             'cube_luts':len(catalog['luts']),'presets':len(catalog['presets']),'model_profiles':len(model['profiles']),
             'dense_luts_included':False,'python_bundled':False,'library_sha256':digest(library),
             'cpp_runner_sha256':digest(cpp_runner),'source_manifest_sha256':digest(original_model),
             'source_records':copied,'omitted_dense_sources':[{'sha256':row.get('sha256'),'bytes':50331648} for row in omitted],
             'members':{path.relative_to(output).as_posix():{'sha256':digest(path),'bytes':path.stat().st_size} for path in package_files(output)},
             'scope':'本机离线调试；原包全成员SHA/尺寸，不含MANIFEST自身；当前Python外置，不声明跨机免依赖或赛事分数。'}
        save(output/'MANIFEST.json',manifest);verify(output)
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as zipped:
            for path in sorted(p for p in output.rglob('*') if p.is_file()):zipped.write(path,output.name+'/'+path.relative_to(output).as_posix())
        result=verify(output,archive)
        result.update(archive_bytes=archive.stat().st_size,build_wall_seconds=time.perf_counter()-started,python_environment=environment,
                      photos=100,cube_luts=len(catalog['luts']),presets=len(catalog['presets']),model_profiles=len(model['profiles']))
        save(receipt_path,result);return result
    except Exception as error:
        if not (output/'PACKAGE-FAILURE.json').exists():save(output/'PACKAGE-FAILURE.json',{'completed':False,'error':str(error),'scope':'部分文件保留，不覆盖重试；使用新输出目录'})
        raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='mode',required=True)
    command=commands.add_parser('build');command.add_argument('--output',type=Path,required=True);command.add_argument('--python',type=Path,default=Path(sys.executable))
    command.add_argument('--library',type=Path,default=ROOT/'artifacts/single-header-perf-build/libflash_chroma_bridge.dll')
    command.add_argument('--cpp-runner',type=Path,default=ROOT/'artifacts/event-cpp-build/flash_chroma_run.exe');command.add_argument('--mingw-bin',type=Path,default=Path('E:/mingw64/bin'))
    command=commands.add_parser('verify');command.add_argument('--package',type=Path,required=True);command.add_argument('--zip',type=Path)
    args=parser.parse_args(argv)
    try:
        result=verify(args.package,args.zip) if args.mode=='verify' else build(args.output,args.python,args.library,args.cpp_runner,args.mingw_bin)
        print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));return 0
    except Exception as error:
        print(json.dumps({'completed':False,'error':str(error)},ensure_ascii=False),file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
