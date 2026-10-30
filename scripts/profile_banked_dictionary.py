"""预冻结2/4/8/16连续bank的精确局部LE16字典容量，只读原M16D，不读gold/照片。"""
import argparse
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,read,save,sha,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--freeze',action='store_true');a=p.parse_args();path=ROOT/'experiments/banked-dictionary-profile-v1.json';old=read(ROOT/'experiments/compact-dictionary-v1.json');source=Path(old['input_rom_path'])
    if a.freeze:
        if path.exists():raise FileExistsError(path)
        save(path,dict(purpose=__doc__,script_sha256=sha(__file__),source_rom_path=str(source),source_rom_sha256=sha(source),banks=[2,4,8,16],block_bytes=16,source_blocks=1048576,header_palette_bytes=1056,model_bytes=1056,map_bytes=2097152,bank_metadata_bytes='4*bank_count：LE32绝对payload pool base，每bank一项；末bank结束由header length给出。',threshold_resident_bytes=4871152,protocol='按源RGB24地址高位连续均分原1048576项16B块map；只用原M16D global block ID分组unique，不重新训练、量化或用gold/照片挑选。每bank unique<=65536才可LE16。重建每档全部16MiB逻辑ID，并核固定SHA。只在可行且实际常驻严格小于3B已合格4871152B的档中选唯一最小容量；并列按较少bank；其它bank不进入native。',capacity='ROM=1056头/palette+2097152 map+4*bank_count metadata+16*sum(bank_unique)；resident=ROM+1056 model。1056 ROM元数据与1056 model均明确计入；不把ZIP大小当RAM。',scope='本轮仅离线剖析，不构建native/不测吞吐，不读gold/照片。失败/溢出及重复pool代价全部保留。'))
        print(path,sha(path));return
    plan=read(path)
    if plan['script_sha256']!=sha(__file__) or sha(source)!=plan['source_rom_sha256']:raise AssertionError('冻结身份变化')
    a.output.mkdir(parents=True,exist_ok=False);before=memory();raw=source.read_bytes();oldmaps=4194304;payload=raw[1056:]
    if raw[:4]!=b'M16D' or struct.unpack_from('<I',raw,8)[0]!=4:raise ValueError('必须为原16B字典')
    offsets=np.frombuffer(payload,dtype='<u4',count=1048576);pool=np.frombuffer(payload,dtype=np.uint8,offset=oldmaps).reshape(-1,16);ids=((offsets-oldmaps)//16).astype(np.uint32)
    if np.any(offsets<oldmaps) or np.any((offsets-oldmaps)%16) or int(ids.max())>=len(pool):raise ValueError('原块ID非法')
    count=len(pool);records=[]
    for banks in plan['banks']:
        per=1048576//banks;uniques=[];logical=hashlib.sha256();maximum=-1
        for bank in range(banks):
            section=ids[bank*per:(bank+1)*per];unique,inverse=np.unique(section,return_inverse=True);uniques.append(len(unique));maximum=max(maximum,int(inverse.max()))
            logical.update(pool[unique[inverse]].reshape(-1))
            del section,unique,inverse
        digest=logical.hexdigest()
        if digest!='a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0':raise AssertionError('重建全部逻辑ID不同')
        total=sum(uniques);pool_bytes=16*total;metadata=1056+4*banks;rom_bytes=2097152+metadata+pool_bytes;resident=rom_bytes+1056;eligible=max(uniques)<=65536
        records.append(dict(banks=banks,bank_unique=uniques,max_local_id=maximum,local16_feasible=eligible,sum_unique=total,global_unique=count,duplicated_blocks=total-count,cross_bank_duplicate_bytes=16*(total-count),duplicate_pool_ratio=total/count,map_bytes=2097152,bank_metadata_bytes=4*banks,header_palette_bytes=1056,pool_bytes=pool_bytes,rom_bytes=rom_bytes,resident_bytes=resident,below_qualified_3b=eligible and resident<plan['threshold_resident_bytes'],logical_sha256=digest))
    accepted=[r for r in records if r['below_qualified_3b']];selected=min(accepted,key=lambda r:(r['resident_bytes'],r['banks'])) if accepted else None
    save(a.output/'results.json',dict(purpose=__doc__,environment=env(),plan_sha256=sha(path),script_sha256=sha(__file__),source_rom_sha256=sha(source),records=records,selected=selected,before=before,after=memory(),scope=plan['scope'],decision='仅selected的唯一bank数可进入下一native冻结；其它档只作离线容量证据，不扫描其它bank数。' if selected else '四档均不能胜过已合格3B或LE16溢出，本机制停止，不构建native。'))
    print(records);print('唯一选择',selected)
if __name__=='__main__':main()
