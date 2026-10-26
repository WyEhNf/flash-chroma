"""发布预冻结512调用原因诊断，保留全部原件与只作观察的时间序列图。"""
import argparse
from pathlib import Path
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);parent=ROOT/'experiments/dictionary-drift-diagnostic-v1.json';analysis=ROOT/'experiments/dictionary-drift-analysis-v1.json';plan=read(parent)
    (a.output/'diagnosis.json').write_bytes((a.input/'summary.json').read_bytes())
    package(a.output/'raw-observations.zip',{file.relative_to(a.input).as_posix():file for file in a.input.rglob('*.json') if file.name not in ('partial.json','summary.json')})
    sources={name:ROOT/name for name in plan['source_sha256']}
    for file in (parent,analysis,ROOT/'scripts/analyze_dictionary_drift.py',ROOT/'scripts/archive_dictionary_drift.py',ROOT/'scripts/archive_compact_sparse.py'):sources[file.relative_to(ROOT).as_posix()]=file
    package(a.output/'measured-source.zip',sources)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False,'svg.hashsalt':'p16-dictionary-drift-v1'})
    fig,axes=plt.subplots(2,4,figsize=(16,6),constrained_layout=True)
    summary=read(a.input/'summary.json')
    for index in range(4):
        worker=read(a.input/f'worker-{index}/results.json');rows=worker['rows'];upper=axes[0,index];lower=axes[1,index]
        for label,color,title in [('ref80','#1768ac','80'),('avx2_24','#d1495b','旧3B')]:
            points=[row for row in rows if row['label']==label];upper.plot([row['index'] for row in points],[row['wall_ns']/1e6 for row in points],'.-',ms=3,lw=.6,color=color,label=title)
        moved=[row for row in rows if row['cpu_endpoint_changed']]
        if moved:upper.scatter([row['index'] for row in moved],[row['wall_ns']/1e6 for row in moved],s=20,facecolors='none',edgecolors='black',label='端点CPU变化')
        upper.axvline(63.5,color='gray',ls='--',lw=.7);upper.set_title('worker '+str(index));upper.set_xlabel('全部调用序号');upper.set_ylabel('百图壁钟 ms');upper.legend(fontsize=7);upper.grid(alpha=.2)
        local=summary['workers'][index]['local_groups'];lower.plot(range(32),[row['b_over_a'] for row in local],'.-',color='#4b644a',ms=4,lw=.8);lower.axvline(15.5,color='gray',ls='--',lw=.7);lower.axhline(1,color='gray',lw=.5);lower.set_xlabel('全部四调用组序号');lower.set_ylabel('局部旧3B / 80壁钟比');lower.grid(alpha=.2)
    fig.suptitle('固定ABBA/BAAB诊断：全部512调用，虚线为预定序列块边界；不是速度资格或因果证明',fontsize=12)
    fig.savefig(a.output/'trace.svg',metadata={'Date':None});fig.savefig(a.output/'trace.png',dpi=120);plt.close(fig)
    save(a.output/'manifest.json',dict(purpose=__doc__,files={file.name:dict(bytes=file.stat().st_size,sha256=sha(file)) for file in a.output.iterdir() if file.is_file()},references='未重编译或复制原二进制。实际78/80与原32bit及MinGW依赖见p16-memory-rom-v1；原3B/17bit见p16-compact-dictionary-v1；全驻留4bank模型见p16-banked-dictionary-v1。原始实际路径/SHA/地址和affinity逐worker保留。',scope='全部组/核心/调用保留；图只按调用次序显示全部壁钟和局部比值，不把周期当指令/频率，不恢复原3B推荐。'))
    print(a.output)
if __name__=='__main__':main()
