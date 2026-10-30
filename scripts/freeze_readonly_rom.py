"""在三fresh与完整质量前冻结RO部署loader，原ROM/计算对象绝不重建。"""
import ast
from pathlib import Path
from study_memory_rom import ROOT,sha,save
def main():
    path=ROOT/'experiments/memory-rom-readonly-v1.json'
    if path.exists():raise FileExistsError('不得覆写已冻结计划')
    names=['scripts/win_readonly_rom.py','scripts/measure_readonly_rom.py','scripts/verify_readonly_rom.py','scripts/run_readonly_rom_quality.py','scripts/freeze_readonly_rom.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py','experiments/memory-rom/memory_rom.h','experiments/memory-rom/memory_rom.c','experiments/memory-rom/memory_rom_store.c']
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    library=ROOT/'artifacts/p16-memory-clang-store-build-v1/jshc_memory_clang_store.dll';rom=ROOT/'artifacts/p16-memory-rom-v2/rom-0.bin';photos=Path('F:/Hackathon/projects/16-lut-color/artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb');inputs={str(library):sha(library),str(rom):sha(rom),str(photos):sha(photos)}
    if inputs[str(library)]!='442bc4243920280480807e4e291dff3aa2ffbdb87a0edd4407affad90578c723' or inputs[str(rom)]!='146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5' or inputs[str(photos)]!='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd':raise AssertionError('既有合格线性实例/照片身份不同')
    save(path,dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256=inputs,library=str(library),rom=str(rom),photos=str(photos),photos_sha256=inputs[str(photos)],model_bytes=1056,rom_bytes=16778272,resident_bytes=16779328,protocol='原study.loadrom ACCESS_COPY、相同WinAPI owner COW、RO各唯一fresh进程；同imports，DLL与流式SHA在before前。记录before/mapped_untouched/prepared/all_pages_read/closed，原构造器仅观察地址与状态后立刻还原。页触碰不复制ROM。',commit_gate='三个打开后时点各要求min(两个COW各自PrivateUsage增量)-RO增量>=1MiB；否则STOP不做完整质量；系统commit仅辅助。',quality='通过提交门槛后RO C99/AVX各1/4线程原地/分离共8完整256³与100图；580有限、IO拒绝、双图像guard、actual/count1/count256 ROM字节精确NOACCESS另夹具、WinAPI四失败位置清理、真实无效文件/共享写拒绝/close幂等和model清零。',performance='尚未授权、不执行、不授100..50速度档；质量精确不代表部署速度保持旧成绩。',scope='Windows专属loader；ROM与计算库/ISA未改，capacity保持16779328B，不称物理WS/跨平台改进；新进程微实验与旧RSS口径独立。',references=['https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile','https://docs.python.org/3.12/library/mmap.html','https://docs.python.org/3.12/library/ctypes.html']))
    print(dict(plan=str(path),sha256=sha(path)))
if __name__=='__main__':main()
