"""293/294 V2静态支撑草稿；仅显式入口加载native，不在import设置策略。"""
import ctypes as ct
import hashlib
import json
from pathlib import Path
import os

ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def pixel_sha(array):return hashlib.sha256(memoryview(array).cast('B')).hexdigest()

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def verify(plan):
    for name,expected in plan['sources_sha256'].items():assert digest(ROOT/name)==expected,name
    for name,expected in plan['inputs_sha256'].items():assert digest(name)==expected,name

def bootstrap(plan):
    # psutil是系统控制入口；模型DLL、NumPy和OpenMP均在设置进程允许集后导入。
    import psutil
    os.environ.update(plan['required_environment'])
    psutil.Process().cpu_affinity(plan['allowed_cpus'])
    assert psutil.Process().cpu_affinity()==plan['allowed_cpus']

class Record(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','omp_tid','team_size','os_tid','cpu_before','cpu_after',
        'group_before','group_after','query_before_ok','set_attempted','set_error','query_after_ok')]
    _fields_ += [(n,ct.c_uint64) for n in ('mask_before','previous_mask','mask_after')]

class Pool:
    def __init__(self,plan,profile):
        self.profile=profile;self.snapshots=[];self.tids=None;self.saved=None;self.healthy=True
        assert ct.sizeof(Record)==72
        self.helper=ct.CDLL(plan['helper']['path'])
        self.fn=self.helper.p16_omp_affinity
        self.fn.argtypes=[ct.POINTER(Record),ct.c_size_t,ct.c_size_t,ct.c_uint32,ct.POINTER(Record)]
        self.fn.restype=ct.c_int

    def call(self,action,label,policy,saved=None):
        values=(Record*4)();code=self.fn(values,4,72,action,saved)
        row={'label':label,'action':action,'policy':policy,'return_code':int(code),
            'members':[{name:int(getattr(v,name)) for name,_ in Record._fields_} for v in values]}
        self.snapshots.append(row)
        try:
            assert code==0,'helper返回非零，立即STOP'
            tids=[v.os_tid for v in values]
            assert len(set(tids))==4 and (self.tids is None or tids==self.tids),'四成员OS TID改变'
            for t,v in enumerate(values):
                assert v.version==1 and v.omp_tid==t and v.team_size==4
                assert v.query_before_ok and v.query_after_ok and v.group_before==v.group_after==0
                expected=(1<<(2*t)) if policy=='P' else 0x55
                assert v.mask_after==expected and v.cpu_after in (0,2,4,6)
                if action==0:
                    assert not v.set_attempted and v.mask_before==expected
                    if policy=='P':assert v.cpu_before==v.cpu_after==2*t
                elif action==1:
                    assert v.set_attempted and not v.set_error and v.previous_mask==0x55 and v.cpu_after==2*t
                else:
                    assert v.set_attempted and not v.set_error and v.mask_before==(1<<(2*t))
            return values
        except BaseException:
            self.healthy=False
            raise

    def initialize(self):
        values=self.call(0,'initial_unpinned_pool','U');self.tids=[v.os_tid for v in values]
        if self.profile=='P':
            self.saved=self.call(1,'pin_original_previous55','P')
            self.endpoint('pinned_pool_verified')

    def endpoint(self,label):
        index=len(self.snapshots);self.call(0,label,self.profile);return index

    def finish(self):
        self.endpoint('end_before_restore')
        if self.profile=='P':
            self.call(2,'restore_original55','U',self.saved)
            self.call(0,'restored55_verified','U')

def modules(plan,allow_absent=False):
    # 枚举真实HMODULE实例；不以文件存在或memory_maps聚合项替代模块数量。
    kernel=ct.WinDLL('kernel32',use_last_error=True);api=ct.WinDLL('psapi',use_last_error=True)
    kernel.GetCurrentProcess.restype=ct.c_void_p;process=kernel.GetCurrentProcess()
    api.EnumProcessModulesEx.argtypes=[ct.c_void_p,ct.POINTER(ct.c_void_p),ct.c_uint32,ct.POINTER(ct.c_uint32),ct.c_uint32]
    api.EnumProcessModulesEx.restype=ct.c_int
    api.GetModuleFileNameExW.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_wchar_p,ct.c_uint32]
    api.GetModuleFileNameExW.restype=ct.c_uint32
    handles=(ct.c_void_p*4096)();needed=ct.c_uint32()
    assert api.EnumProcessModulesEx(process,handles,ct.sizeof(handles),ct.byref(needed),3)
    assert needed.value<=ct.sizeof(handles) and needed.value%ct.sizeof(ct.c_void_p)==0
    found={name:[] for name in plan['gcc_dependencies']}
    for handle in handles[:needed.value//ct.sizeof(ct.c_void_p)]:
        buffer=ct.create_unicode_buffer(32768);length=api.GetModuleFileNameExW(process,handle,buffer,len(buffer))
        assert length and length<len(buffer)
        path=Path(buffer.value).resolve();name=path.name.lower()
        if name in found:found[name].append({'path':str(path),'base':int(handle),'sha256':digest(path)})
    for name,rows in found.items():
        expected=plan['gcc_dependencies'][name]
        assert len(rows) in ((0,1) if allow_absent else (1,)),(name,rows)
        for row in rows:assert Path(row['path']).resolve()==Path(expected['path']).resolve() and row['sha256']==expected['sha256']
    return found

class Memory(ct.Structure):
    _fields_=[('cb',ct.c_uint32),('PageFaultCount',ct.c_uint32)]
    _fields_ += [(name,ct.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage',
        'QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]

def memory():
    assert ct.sizeof(Memory)==80
    kernel=ct.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=ct.c_void_p
    api=ct.WinDLL('psapi',use_last_error=True)
    api.GetProcessMemoryInfo.argtypes=[ct.c_void_p,ct.POINTER(Memory),ct.c_uint32];api.GetProcessMemoryInfo.restype=ct.c_int
    value=Memory();value.cb=ct.sizeof(value)
    assert api.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ct.byref(value),ct.sizeof(value))
    return {name:int(getattr(value,name)) for name,_ in value._fields_}

def load_libraries(plan):
    import sys
    assert sys.version==plan['expected_python']
    sys.path[:0]=[str(ROOT/'experiments/channel-runtime'),str(ROOT/'scripts')]
    directories=[os.add_dll_directory('E:/mingw64/bin')]
    directories += [os.add_dll_directory(str(Path(row['path']).parent)) for row in plan['libraries'].values()]
    order=['libwinpthread-1.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libgomp-1.dll']
    assert plan['dependency_load_order']==order
    retained=list(directories)
    # 先逐个完整路径预载；AddDllDirectory的搜索次序不承担依赖身份保证。
    for name in order:
        expected=plan['gcc_dependencies'][name];path=Path(expected['path']).resolve()
        assert path==Path('E:/mingw64/bin',name).resolve() and digest(path)==expected['sha256']
        retained.append(ct.CDLL(str(path)))
    # channel_native会导入NumPy；先核版本，再装载任何目标产品DLL。
    from channel_native import Library
    assert sys.modules['numpy'].__version__==plan['expected_numpy']
    libraries={}
    u8=ct.POINTER(ct.c_uint8);doubles=ct.POINTER(ct.c_double);text=ct.POINTER(ct.c_char)
    for key,row in plan['libraries'].items():
        library=Library(row['path'],row['sha256']);assert library.revision==row['revision']
        library.dll.jshc_cc_bench_to.argtypes=[ct.c_void_p,u8,u8,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,doubles,text,ct.c_size_t]
        library.dll.jshc_cc_bench_to.restype=ct.c_int;libraries[key]=library
    return libraries,retained

def path_arrays(spec):
    paths=(ct.c_char_p*4)(*(str(Path(p).resolve()).encode('utf-8') for p in spec['models']))
    sides=(ct.c_char_p*4)(*(str(Path(p).resolve()).encode('utf-8') if p else None for p in spec['sidecars']))
    return paths,sides

def create(library,arrays):
    handle=ct.c_void_p();error=ct.create_string_buffer(1024)
    code=library.dll.jshc_cc_create(arrays[0],arrays[1],4,ct.byref(handle),error,len(error))
    if code:raise RuntimeError(error.value.decode('utf-8','replace'))
    return handle

class CheckedHandle:
    """只供调用方仍持有所有权、尚未destroy的诊断句柄；不承担关闭所有权。"""
    def __init__(self,library,handle):
        self.library=library;self.handle=handle;self._check()

    def _check(self):
        if not isinstance(self.handle,ct.c_void_p) or not self.handle.value:
            raise ValueError('诊断要求尚未关闭的非空原生句柄')

    @property
    def model_bytes(self):
        self._check();value=int(self.library.dll.jshc_cc_model_bytes(self.handle))
        if value<=0:raise ValueError('有效四级句柄的模型容量必须为正')
        return value

def stable_state(value):
    # 构造耗时与allocator地址模64不是表示身份；原始值仍完整保存。
    return {key:({name:item for name,item in row.items() if name not in ('prepare_seconds','data_mod_64')}
        if isinstance(row,dict) else row) for key,row in value.items()}

def check_state(plan,role,value,reference=None):
    assert value['cache']['enabled']==value['domain']['eligible']==value['direct']['enabled']==1
    assert value['domain']['cache_enabled']==1 and value['domain']['unproven_cells']==0
    stable=stable_state(value)
    assert stable==plan['expected_states'][role],(role,stable)
    if reference is not None:assert stable==stable_state(reference),role

def state(library,handle):
    from suffix_cache_support import cache_info
    from domain_cache_support import info as domain_info
    from palette_support import info as palette_info
    from direct16_support import info as direct_info
    class Wide(ct.Structure):
        _fields_=[(n,ct.c_uint32) for n in ('version','enabled','format','reason','palette_size','id_bytes','guard_bytes','reserved')]
        _fields_ += [(n,ct.c_uint64) for n in ('input_entries','raw_words','table_capacity_bytes','palette_capacity_bytes','temporary_peak_bytes','guaranteed_alignment','data_mod_64')]
        _fields_ += [('prepare_seconds',ct.c_double)]
    view=CheckedHandle(library,handle)
    value={'cache':cache_info(view),'domain':domain_info(view),'palette':palette_info(view),'direct':direct_info(view),
        'model_bytes':view.model_bytes,'wide':None}
    if library.revision in (293,294):
        suffix='u16' if library.revision==293 else 'rgb24';function=getattr(library.dll,'p16_cc_get_direct_'+suffix+'_info')
        function.argtypes=[ct.c_void_p,ct.POINTER(Wide),ct.c_size_t];function.restype=ct.c_int
        wide=Wide();assert ct.sizeof(wide)==96 and function(handle,ct.byref(wide),96)==0
        value['wide']={name:getattr(wide,name) for name,_ in wide._fields_}
    return value
