"""独立只读观察P4 v2同加载顺序的实际依赖模块；不改正式源/环境，不计时。"""
import argparse
import ast
import ctypes as ct
import hashlib
import json
from pathlib import Path
import bench_page_id16_v2 as bench

ROOT=bench.ROOT
PERFORMANCE=ROOT/'experiments/page-id16-performance-v2.json'
PLAN=ROOT/'experiments/page-id16-module-observer-v1.json'
NAMES=('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll')
ENUM=bench.base.K32.K32EnumProcessModulesEx
ENUM.argtypes=[ct.c_void_p,ct.POINTER(ct.c_void_p),ct.c_uint32,ct.POINTER(ct.c_uint32),ct.c_uint32]
ENUM.restype=ct.c_int
FILENAME=bench.base.K32.GetModuleFileNameW
FILENAME.argtypes=[ct.c_void_p,ct.POINTER(ct.c_wchar),ct.c_uint32]
FILENAME.restype=ct.c_uint32

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def snapshot(label):
    capacity=4096
    while True:
        handles=(ct.c_void_p*capacity)()
        required=ct.c_uint32()
        if not ENUM(bench.base.API.process(),handles,ct.sizeof(handles),ct.byref(required),3):raise ct.WinError(ct.get_last_error())
        if required.value<=ct.sizeof(handles):break
        capacity=(required.value+ct.sizeof(ct.c_void_p)-1)//ct.sizeof(ct.c_void_p)
        if capacity>65536:raise RuntimeError('模块枚举需要异常大小，STOP')
    if required.value%ct.sizeof(ct.c_void_p):raise AssertionError('模块枚举字节数不完整')
    modules=[]
    dependencies={name:[] for name in NAMES}
    for index in range(required.value//ct.sizeof(ct.c_void_p)):
        buffer=ct.create_unicode_buffer(32768)
        length=int(FILENAME(handles[index],buffer,len(buffer)))
        if not length or length>=len(buffer)-1:raise ct.WinError(ct.get_last_error())
        path=Path(buffer.value)
        record=dict(path=str(path),basename=path.name,module_address=int(handles[index]))
        modules.append(record)
        if path.name.lower() in dependencies:
            dependencies[path.name.lower()].append(dict(**record,sha256=sha(path),bytes=path.stat().st_size))
    return dict(label=label,module_count=len(modules),modules=modules,dependency_counts={name:len(records) for name,records in dependencies.items()},dependencies=dependencies)

def freeze():
    if PLAN.exists():raise FileExistsError('观察协议不能覆盖')
    source='scripts/observe_page_id16_modules.py'
    ast.parse((ROOT/source).read_text(encoding='utf-8'),filename=source)
    if sha(PERFORMANCE)!='b54be80781190763245429eb8743433063ccf3d04bb448f5afd0f8a2999f2608':raise AssertionError('P4 v2正式协议不同')
    value=dict(purpose=__doc__,source_sha256={source:sha(ROOT/source)},performance_plan=str(PERFORMANCE),performance_plan_sha256=sha(PERFORMANCE),roles=['ref78','ref80','linear_avx','linear_c99','p4_avx','p4_c99'],process_allowed_mask=85,dependency_names=list(NAMES),protocol='同v2 imports和0x55；按正式六角色原顺序prepare，准备前/每个角色后/全部关闭后用K32EnumProcessModulesEx LIST_MODULES_ALL+GetModuleFileNameW只读枚举实际加载绝对路径/地址；四依赖记录SHA/字节/数量。未分配照片，不调用像素或计时。',scope='磁盘四目录的冻结SHA不是实际加载证明；不选择/更换DLL或环境、不通过此观察授速度/稳定性资格。仅一个fresh，首次失败保存STOP。API返回HMODULE为借用快照，不CloseHandle。',primary_sources=['https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-enumprocessmodulesex','https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulefilenamew'])
    write(PLAN,value)
    print(dict(plan=str(PLAN),sha256=sha(PLAN)),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.freeze:
        if args.output:raise ValueError('冻结不执行观察')
        freeze()
        return
    if args.output is None:raise ValueError('观察必须指定新输出目录')
    protocol=read(PLAN)
    if sha(PERFORMANCE)!=protocol['performance_plan_sha256'] or any(sha(ROOT/name)!=value for name,value in protocol['source_sha256'].items()):raise AssertionError('观察源/正式计划不同')
    performance=bench.base.checked()
    if performance['roles']!=protocol['roles']:raise AssertionError('正式模型顺序不同')
    args.output.mkdir(parents=True,exist_ok=False)
    observations=[]
    operators={}
    failure=None
    control=bench.base.affinity()
    try:
        observations.append(snapshot('same-imports-before-setup'))
        for role in protocol['roles']:
            operators[role]=bench.base.setup(role,performance)
            observations.append(snapshot('after-'+role))
    except BaseException as error:failure=error
    finally:
        for role,value in reversed(list(operators.items())):value[1]()
    try:observations.append(snapshot('after-all-close'))
    except BaseException as error:
        if failure is None:failure=error
    result=dict(passed=failure is None,plan_sha256=sha(PLAN),performance_plan_sha256=sha(PERFORMANCE),affinity=control,roles=protocol['roles'],identities={role:value[2] for role,value in operators.items()},observations=observations,environment=bench.base.env(),scope=protocol['scope'])
    if failure:result['failure']=dict(type=type(failure).__name__,message=str(failure))
    write(args.output/'results.json',result)
    print(dict(passed=result['passed'],observations=len(observations),final_dependencies=observations[-1]['dependencies'] if observations else {}),flush=True)
    if failure:raise failure

if __name__=='__main__':main()
