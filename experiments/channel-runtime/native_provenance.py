"""实验原生库的依赖字节及Windows实际已载模块来源，不改变数值路径。"""
from __future__ import annotations
import ctypes as ct
from pathlib import Path
from channel_native import digest

def verify_dependencies(library,build,*,loaded=False):
    library=Path(library).resolve();records=[]
    for name,expected in build['files'].items():
        if not name.endswith('.dll'):continue
        path=library.parent/name
        if digest(path)!=expected:raise ValueError(f'构建依赖字节不同：{name}')
        entry={'name':name,'adjacent_path':str(path),'sha256':expected}
        if loaded:
            kernel=ct.WinDLL('kernel32',use_last_error=True)
            get_module=kernel.GetModuleHandleW;get_module.argtypes=[ct.c_wchar_p];get_module.restype=ct.c_void_p
            get_name=kernel.GetModuleFileNameW;get_name.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];get_name.restype=ct.c_uint32
            handle=get_module(name)
            if not handle:raise OSError(f'预期DLL未载入：{name}')
            buffer=ct.create_unicode_buffer(32768);length=get_name(handle,buffer,len(buffer))
            if not length or length>=len(buffer):raise OSError('实际DLL模块路径读取失败')
            actual=Path(buffer.value)
            if digest(actual)!=expected:raise ValueError(f'实际已载模块与冻结构建不同：{name}')
            entry['loaded_module_path']=str(actual)
        records.append(entry)
    if len(records)!=5:raise ValueError('本轮预期主库与四个GCC依赖DLL')
    return records
