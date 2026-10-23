"""验证C99核心可跨目标编译；不替代QEMU/实板执行、链接和资源验收。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--clang',default='C:/Program Files/LLVM/bin/clang.exe')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    core=ROOT/'experiments/memory-rom';support=ROOT/'experiments/memory-rom-wasm/include'
    targets=[('cortex-m3','armv7m-none-eabi',['-mcpu=cortex-m3','-mthumb'],1,1,40),
             ('rv32im','riscv32-none-elf',['-march=rv32im','-mabi=ilp32'],1,1,243),
             ('aarch64-be','aarch64_be-none-elf',[],2,2,183)]
    records=[]
    for label,triple,extra,elf_class,endian,machine in targets:
        obj=out/(label+'.o')
        cmd=[a.clang,'--target='+triple,*extra,'-std=c99','-O3','-ffreestanding','-fno-builtin',
             '-Wall','-Wextra','-Werror','-fstack-usage','-I'+str(support),'-I'+str(core),
             '-c',str(core/'memory_rom.c'),'-o',str(obj)]
        run=subprocess.run(cmd,capture_output=True,text=True)
        (out/(label+'.log')).write_text(run.stdout+run.stderr,encoding='utf-8')
        row={'label':label,'target':triple,'command':cmd,'returncode':run.returncode,
             'scope':'仅编译C99核心到目标ELF对象；无链接/执行/实板/周期结论'}
        records.append(row)
        (out/'results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        run.check_returncode()
        data=obj.read_bytes()
        assert data[:4]==b'\x7fELF' and data[4]==elf_class and data[5]==endian
        actual_machine=struct.unpack_from('<H' if endian==1 else '>H',data,18)[0]
        assert actual_machine==machine
        row.update(object_sha256=sha(obj),object_bytes=len(data),elf_class=elf_class,
                   data_endianness='little' if endian==1 else 'big',elf_machine=actual_machine)
    result={'passed':True,'purpose':__doc__,'python':sys.version,
            'compiler':subprocess.run([a.clang,'--version'],capture_output=True,text=True).stdout,
            'source_sha256':{str(f.relative_to(ROOT)):sha(f) for f in [core/'memory_rom.c',core/'memory_rom.h',support/'string.h',Path(__file__)]},
            'records':records,'limits':'标准函数声明由freestanding夹具提供；对象可能需要目标编译器常规内存拷贝辅助例程。未构建BSP/最终镜像，不把对象编译通过当作部署完成。'}
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('三类目标C99对象与ELF字节序检查通过')
if __name__=='__main__':main()
