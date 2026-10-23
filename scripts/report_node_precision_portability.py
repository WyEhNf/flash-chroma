"""仅由冻结位宽/wasm32/跨目标结果生成报告、图及原字节归档，不重跑数值或性能。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('screen','full','wasm','cross','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    full=read(a.full/'results.json');rows=full['results'];base=rows[0]
    assert base['name']=='baseline' and abs(base['metrics']['mean']-.9811105967231599)<1e-14
    assert len(rows)==8 and all(r['decompressed_native']['byte_mismatches']==0 and r['decompressed_native']['avx2_full_domain'] for r in rows)
    assert read(a.wasm/'results.json')['passed'] and read(a.cross/'results.json')['passed']
    summary=[]
    for r in rows:
        summary.append({'name':r['name'],'cube':{k:r['metrics'][k] for k in ('mean','p99','max')},
                        'photo_merged':{k:r['photos']['merged'][k] for k in ('mean','p99','max')},
                        'cube_retention':r.get('accuracy_retention',{'minimum':1})['minimum'],
                        'photo_retention':r.get('photo_accuracy_retention',{'minimum':1})['minimum'],
                        'worst_image_retention':r.get('worst_per_image_retention',1),
                        'logical_node_bitstream_bytes':r['logical_node_bitstream_bytes'],
                        'runtime_model_bytes':r['decompressed_native']['model_bytes']})
    save(out/'summary.json',{'purpose':__doc__,'rows':summary,
         'retention_definition':'mean/p99/max逐项取基线误差÷候选误差，最低者为该范围保留率；逐图再取最劣。非官方得分。',
         'accuracy_only':True,'compressed_native_decoder_implemented':False,'performance_comparison_performed':False,
         'screen_provenance':'原262144色筛查后脚本增加完整域/原生/照片支持；旧源码SHA保留，粗筛不单独授予验收资格。完整终验测时源码按SHA归档。',
         'wasm':read(a.wasm/'results.json'),'cross_compile':read(a.cross/'results.json')})
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
    labels=[r['name'].replace('_first','\n仅首级').replace('_all','\n四级') for r in summary]
    fig,axes=plt.subplots(1,3,figsize=(14,5.4),sharey=True)
    for ax,key,title in zip(axes,('cube_retention','photo_retention','worst_image_retention'),('完整RGB色域','100图合并','最劣单图')):
        values=[100*r[key] for r in summary]
        ax.bar(range(len(values)),values,color=['#447eaa' if v>=50 else '#bd5c57' for v in values])
        for level in (50,60,70,80,90,100):ax.axhline(level,color='#b3b9c2',lw=.6,ls='--',zorder=0)
        ax.set_ylim(0,108);ax.set_xticks(range(len(labels)),labels,rotation=55,ha='right',fontproperties=font,fontsize=8)
        ax.set_title(title,fontproperties=font);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('精度保留率（%）',fontproperties=font)
    fig.suptitle('固定a399：同一位宽在全域与照片上的退化不同',fontproperties=font,fontsize=15)
    fig.text(.5,.015,'精度定义为mean/p99/max误差比的最小值；仅为质量研究，未实现压缩运行时。',ha='center',fontproperties=font,fontsize=10)
    fig.tight_layout(rect=(0,.075,1,.94))
    fig.savefig(out/'accuracy-retention.png',dpi=170);fig.savefig(out/'accuracy-retention.svg');plt.close(fig)
    members=[]
    def append(path,name):members.append((Path(path),name))
    for label,directory in [('screen',a.screen),('full',a.full),('wasm',a.wasm),('cross',a.cross)]:
        for f in sorted(directory.rglob('*')):
            if f.is_file() and f.suffix not in ('.rgb',) and f.name!='probe.rgb':append(f,label+'/'+f.relative_to(directory).as_posix())
    sources=['scripts/scan_node_precision_tiers.py','scripts/verify_memory_rom_wasm.py','scripts/compile_memory_rom_targets.py',
             'scripts/report_node_precision_portability.py','python/lutlab/channel_coordinates.py','python/lutlab/io.py',
             'scripts/accept_channel_coordinates.py','scripts/run_channel_coordinates.py','python/lutlab/study_provenance.py',
             'experiments/memory-rom/memory_rom.c','experiments/memory-rom/memory_rom.h']
    sources += [f.relative_to(ROOT).as_posix() for f in (ROOT/'experiments/memory-rom-wasm').rglob('*') if f.is_file()]
    for f in sources:append(ROOT/f,'measured-source/'+f)
    # 完整终验与WASM记录的测时源码必须仍按原SHA匹配。
    for run_path in [a.full/'run.json',a.wasm/'run.json',a.cross/'results.json']:
        for name,h in read(run_path)['source_sha256'].items():assert sha(ROOT/name)==h,(run_path,name)
    manifest=[{'path':n,'bytes':f.stat().st_size,'sha256':sha(f)} for f,n in members]
    with zipfile.ZipFile(out/'evidence.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f,n in members:z.write(f,n)
    save(out/'manifest.json',{'files':manifest,'zip_sha256':sha(out/'evidence.zip'),
         'excluded':'完整RGB输出流、照片像素、可重建ROM及原完整LUT不重复纳入；其SHA/输入来源由run及results记录。'})
    (out/'README.md').write_text('# 位宽曲线与C99跨目标核验\n\n本目录由冻结结果只读生成，不重新拟合/计时。质量原始逐图结果、模型、直方图、wasm32执行及三类ELF对象、源码均在evidence.zip，manifest逐项绑定原始字节。\n\n质量表见summary.json，完整说明见[阶段报告](../../../docs/stages/2026-10-24-node-precision-portability.md)。模型位宽只代表潜在bitstream容量，现有RGB8重建运行时仍1,058,292B；本阶段没有宣称压缩decoder的速度。wasm32已实际执行，三类ARM/RISC-V对象仅编译，不冒充实板。\n',encoding='utf-8')
    print(json.dumps({'files':len(members),'evidence_bytes':(out/'evidence.zip').stat().st_size,'output':str(out)},ensure_ascii=False))
if __name__=='__main__':main()
