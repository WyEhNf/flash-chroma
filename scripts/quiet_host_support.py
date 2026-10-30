"""冻结Linux来宾空闲前置条件；只读CPU/启动状态，不更改频率、服务或系统配置。"""
import json,os,time
from pathlib import Path
def snapshot(cpus):
    values={}
    for line in Path('/proc/stat').read_text().splitlines():
        parts=line.split()
        if parts and (parts[0]=='cpu' or parts[0] in {'cpu'+str(x) for x in cpus}):
            # I/O等待也视作非空闲；不把来宾I/O阻塞误当成计时前的安静状态。
            raw_ticks=[int(x) for x in parts[1:]];ticks=raw_ticks[:8];values[parts[0]]={'total':sum(ticks),'idle':ticks[3],'raw_ticks':raw_ticks}
    if set(values)!={'cpu',*('cpu'+str(x) for x in cpus)}:raise ValueError('缺少指定CPU计数')
    uptime=float(Path('/proc/uptime').read_text().split()[0]);stat=Path('/proc/1/stat').read_text().rsplit(')',1)[1].split()
    start_ticks=int(stat[19]);hz=os.sysconf('SC_CLK_TCK');age=uptime-start_ticks/hz
    return {'monotonic':time.monotonic(),'uptime_seconds':uptime,'pid1_start_ticks':start_ticks,'ticks_per_second':hz,'pid1_age_seconds':age,'cpu_ticks':values}
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def require_quiet(policy,cpus,output,phase,settle):
    start=time.monotonic();samples=[];intervals=[];good=0;previous=None
    try:
        while True:
            current=snapshot(cpus);samples.append(current);elapsed=time.monotonic()-start
            settled=elapsed>=settle and current['pid1_age_seconds']>=policy['minimum_pid1_age_seconds']
            if previous is not None:
                busy={}
                for key,row in current['cpu_ticks'].items():
                    old=previous['cpu_ticks'][key];total=row['total']-old['total'];idle=row['idle']-old['idle']
                    if total<=0 or not 0<=idle<=total:raise ValueError('CPU计数间隔非法')
                    busy[key]=100*(total-idle)/total
                passed=settled and all(x<=policy['busy_percent_max'] for x in busy.values())
                intervals.append({'elapsed_seconds':elapsed,'busy_percent':busy,'settled':settled,'pass':passed});good=good+1 if passed else 0
            progress={'purpose':__doc__,'phase':phase,'policy':policy,'elapsed_seconds':elapsed,'consecutive_good_intervals':good,'last_snapshot':current,'last_interval':intervals[-1] if intervals else None,'new_native_calls':0,'new_performance_calls':0}
            save(Path(output)/(phase+'-progress.json'),progress)
            if good>=policy['consecutive_good_intervals']:
                result={'pass':True,'purpose':__doc__,'phase':phase,'policy':policy,'start_monotonic':start,'actual_settle_min_seconds':settle,'elapsed_seconds':elapsed,'samples':samples,'intervals':intervals,'limitation':'只证明来宾CPU计数前置空闲；宿主竞争、频率和温度未锁定，不代表独占服务器','new_native_calls':0,'new_performance_calls':0}
                save(Path(output)/(phase+'.json'),result);return result
            if elapsed>=policy['timeout_seconds']:raise RuntimeError('来宾空闲前置条件超时，保留所有数据，不启动后续性能进程')
            previous=current;time.sleep(policy['sample_interval_seconds'])
    except BaseException as exc:
        save(Path(output)/(phase+'-failure.json'),{'pass':False,'purpose':__doc__,'phase':phase,'policy':policy,'samples':samples,'intervals':intervals,'exception':str(exc),'new_native_calls':0,'new_performance_calls':0});raise
