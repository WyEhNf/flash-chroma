"""用版本化小包和已有数据流恢复完整服务器目录，逐文件校验SHA；不构建、映射或测速。"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path,PurePosixPath
import platform
import stat
import sys
import zipfile


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def destination(root,name):
    relative=PurePosixPath(name)
    if (relative.is_absolute() or relative.as_posix()!=name or any(p in ('..','.') for p in relative.parts)
            or '\\' in name or ':' in name or not relative.parts):
        raise ValueError('包内路径不是规范相对路径：'+name)
    path=(root/Path(*relative.parts)).resolve()
    if root not in path.parents:
        raise ValueError('包内路径越过输出目录：'+name)
    return path


def copy_stream(stream,path,spec):
    path.parent.mkdir(parents=True,exist_ok=True)
    value=hashlib.sha256();count=0
    with path.open('xb') as output:
        while chunk:=stream.read(1024*1024):
            count+=len(chunk)
            if count>spec['bytes']:
                raise ValueError('文件超出冻结大小：'+str(path))
            output.write(chunk);value.update(chunk)
    if count!=spec['bytes'] or value.hexdigest()!=spec['sha256']:
        raise ValueError('恢复文件与冻结字节不同：'+str(path))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True,help='包含server-packet-small.zip及delivery-packet.json的版本化证据目录')
    parser.add_argument('--data-root',type=Path,required=True,help='已有完整服务器包的根目录，按同一相对路径查找三个大流')
    parser.add_argument('--output',type=Path,required=True,help='新建的完整服务器目录；拒绝覆盖或自动重试')
    args=parser.parse_args();archive=args.archive.resolve();data_root=args.data_root.resolve();out=args.output.resolve()
    receipt=out.with_name(out.name+'.restore.json')
    if out.exists() or receipt.exists():
        raise ValueError('输出目录或恢复回执已存在，请使用新的输出名称')
    metadata=read(archive/'delivery-packet.json');small=archive/'server-packet-small.zip'
    if digest(small)!=metadata['small_packet_sha256']:
        raise ValueError('小包SHA不同')
    omitted=metadata['large_files_omitted_from_small']
    record={'purpose':__doc__,'started_at_utc':datetime.now(timezone.utc).isoformat(),
        'environment':{'platform':platform.platform(),'python':sys.version,'backend_threads':'不适用：仅标准库文件复制及SHA'},
        'script_sha256':digest(__file__),'metadata_sha256':digest(archive/'delivery-packet.json'),
        'small_packet_sha256':digest(small),'data_root':str(data_root),'output':str(out),
        'native_calls':0,'performance_calls':0,'new_pixel_mappings':0,'new_fits':0}
    try:
        with zipfile.ZipFile(small) as package:
            raw=package.read('bundle-manifest.json')
            if hashlib.sha256(raw).hexdigest()!=metadata['bundle_manifest_sha256']:
                raise ValueError('小包中的manifest与版本化交付回执不同')
            bundle=json.loads(raw);files=bundle['files']
            if not omitted or not set(omitted)<=set(files):
                raise ValueError('省略流清单不属于完整包')
            for name,spec in omitted.items():
                if spec!=files[name]:raise ValueError('省略流规格与完整包不同')
                source=destination(data_root,name)
                if not source.is_file() or source.stat().st_size!=spec['bytes']:
                    raise ValueError('缺少正确大小的原数据流：'+str(source))
            entries=package.infolist();names=[entry.filename for entry in entries]
            expected=(set(files)-set(omitted))|{'bundle-manifest.json'}
            if len(names)!=len(set(names)) or set(names)!=expected:
                raise ValueError('小包成员有重名、缺失或清单外文件')
            for entry in entries:
                destination(out,entry.filename)
                kind=stat.S_IFMT(entry.external_attr>>16)
                if entry.is_dir() or kind not in (0,stat.S_IFREG):
                    raise ValueError('小包成员必须是普通文件')
                spec={'bytes':len(raw),'sha256':metadata['bundle_manifest_sha256']} if entry.filename=='bundle-manifest.json' else files[entry.filename]
                if entry.file_size!=spec['bytes']:raise ValueError('ZIP成员大小不同')
            out.mkdir(parents=True)
            for entry in entries:
                spec={'bytes':len(raw),'sha256':metadata['bundle_manifest_sha256']} if entry.filename=='bundle-manifest.json' else files[entry.filename]
                with package.open(entry) as stream:
                    copy_stream(stream,destination(out,entry.filename),spec)
            for name,spec in omitted.items():
                with destination(data_root,name).open('rb') as stream:
                    copy_stream(stream,destination(out,name),spec)
        verified=[]
        for name,spec in files.items():
            path=destination(out,name)
            if path.stat().st_size!=spec['bytes'] or digest(path)!=spec['sha256']:
                raise ValueError('落盘后的完整文件校验失败：'+name)
            verified.append({'path':name,'sha256':spec['sha256'],'bytes':spec['bytes']})
        if digest(out/'bundle-manifest.json')!=metadata['bundle_manifest_sha256']:
            raise ValueError('落盘manifest变化')
        record.update(pass_=True,verified_file_count=len(verified),verified_payload_bytes=sum(x['bytes'] for x in verified),
            bundle_manifest_sha256=metadata['bundle_manifest_sha256'],large_files_restored=len(omitted),files=verified,
            scope='只证明完整目录与既有已验包原字节一致；不新增运行时/性能或Skylake资格')
        record['pass']=record.pop('pass_')
    except Exception as error:
        record.update({'pass':False,'error':repr(error),'scope':'保留失败目录/回执，不覆盖或自动重试'})
        receipt.parent.mkdir(parents=True,exist_ok=True)
        receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        raise
    record['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:record[k] for k in ('pass','verified_file_count','verified_payload_bytes','large_files_restored','bundle_manifest_sha256')},ensure_ascii=False))
    print('恢复回执：'+str(receipt),flush=True)


if __name__=='__main__':
    main()
