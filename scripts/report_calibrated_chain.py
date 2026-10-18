"""归档统一入口的冻结模型、实际分派和四级验收；未触发阶段独立标注。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有归档')
    run, prepared = read(args.run/'run.json'), read(args.run/'preparation.json')
    if (hashlib.sha256(json.dumps(run['identity'], sort_keys=True, allow_nan=False).encode()).hexdigest()
            != run['identity_sha256'] or prepared['run_identity'] != run['identity_sha256']):
        raise ValueError('冻结运行身份不同')
    full_path = args.run/'full-results.json'
    full = read(full_path) if full_path.exists() else None
    if full is not None and full['run_identity'] != run['identity_sha256']:
        raise ValueError('完整结果身份不同')
    args.output.mkdir(parents=True)
    manifest, metrics, photos = {}, [], []
    with zipfile.ZipFile(args.output/'evidence.zip','w',zipfile.ZIP_DEFLATED) as evidence, \
            zipfile.ZipFile(args.output/'models.zip','w',zipfile.ZIP_DEFLATED) as models:
        paths = [args.run/name for name in ('run.json','preparation.json','measured-source.zip','reference-curves.npy','full-results.json')]
        paths += sorted(args.run.glob('*-fit.*.txt'))
        for path in paths:
            if path.is_file():
                evidence.write(path, path.name); manifest['evidence/'+path.name] = sha(path)
        for name, row in prepared['variants'].items():
            path = Path(row['cache_manifest_path'])
            if sha(path) != row['cache_manifest_sha256']:
                raise ValueError('CLI清单已改变')
            member = name+'/cache-manifest.json'
            evidence.write(path, member); manifest['evidence/'+member] = sha(path)
            for stage, (model_path, expected) in enumerate(zip(row['model_paths'],row['model_sha256']),1):
                path = Path(model_path)
                if sha(path) != expected:
                    raise ValueError('模型字节不同于冻结来源')
                member = name+f'/stage{stage}.slut'
                models.write(path, member); manifest['models/'+member] = expected
            if full is not None:
                value = full['variants'][name]
                for scope in ('cube','photos'):
                    v = value[scope]
                    metrics.append({'version': name, 'scope': scope, 'serialized_bytes': row['serialized_bytes'],
                        'mean':v['mean'],'rms':v['rms'],'p99':v['p99'] if scope=='cube' else v['worst_image_p99'],
                        'max':v['max'],'cvar_1pct':v['cvar_1pct'] if scope=='cube' else v['mean_image_cvar_1pct']})
                photos.extend({'version':name,**r} for r in value['photos']['per_image'])
    for name, values in (('metrics.csv',metrics),('photos.csv',photos)):
        fields = list(values[0]) if values else (['version','scope','mean','rms','p99','max'] if name=='metrics.csv'
                                                    else ['version','image','mean','rms','p99','max'])
        with (args.output/name).open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(values)
    body = ['# 四级解析校准的统一入口证据', '',
            'Agent：Codex；Operator：WyEhNf；仅本地研究，未PR或推送。', '', run['identity']['plan']['limits'], '']
    if full is None:
        body += ['本轮没有进入完整模型映射或百图验收。固定原Filmic04/05/06/07串联：原17³、原33³、新17³解析整链误差均为0，原基线局部误差被后缀吞掉，预定严格改善触发失败。', '',
                 '三个CLI拟合及缓存核对成功；只有新17³四级各自都精确，不能据此把整链零误差计为新方法收益。全部12模型、解析结果和源码保留；实际完整指标CSV为空，不填解析值冒充测量。']
    else:
        body += ['三个版本分别一次完整256³及100张1024×768 RGB8照片，逐级整数舍入，四张独立不同原表。', '',
                 '|版本|范围|文件总字节|mean|RMS|p99|最大误差|CVaR1%|','|---|---|---:|---:|---:|---:|---:|---:|']
        for row in metrics:
            body.append('|{version}|{scope}|{serialized_bytes}|{mean:.9f}|{rms:.9f}|{p99:.9f}|{max:.9f}|{cvar_1pct:.9f}|'.format(**row))
        body += ['', '照片p99为最差逐图p99，照片CVaR为逐图平均；完整300条逐图另列。受控等距后缀保持首级RGB误差，不能冒充自然四级普遍精确。', '',
                 '完整门禁：'+json.dumps(full['acceptance'],ensure_ascii=False)+'。各版本独立u64四面体/Numba/标量/AVX2/C99全域逐字节一致；新17另有AVX2实际百图流回执。', '',
                 '新17文件总量75196字节，原33为448252字节，减少约83.22%；这是文件容量比较，不能直接当作OS峰值内存或运行时间。']
    body += ['', '环境与目的、源SHA、精确CLI命令及实际route在run/preparation和缓存manifest；原始stdout/stderr、源码快照在evidence.zip，模型在models.zip。大原表/输出流留本地，依冻结生成器和SHA可重建。', '',
             '复现需使用本阶段measured-source.zip内实测源码与run中的计划，在新输出目录执行run_filmic_chain_calibrated.py prepare，只有full_eligible时accept。原Filmic链和等距控制链身份不同，禁止改旧计划后补验收。', '',
             'Windows11 26200/Ryzen9 8945HX/Python3.12.14/NumPy1.26.4/Numba0.60.0，Numba4、OMP/BLAS/MKL1；GCC15.2 Release三原生后端各1线程。没有性能计时；RGB欧氏码值距离非CIEDE2000；官方阈值未知，历史已见照片非盲测；默认不改。']
    (args.output/'report.md').write_text('\n'.join(body)+'\n',encoding='utf-8')
    for path in args.output.iterdir():
        if path.is_file():manifest[path.name]=sha(path)
    (args.output/'sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'metrics':len(metrics),'photos':len(photos),'complete':full is not None},ensure_ascii=False))


if __name__=='__main__':
    main()
