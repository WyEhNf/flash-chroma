"""固定三fresh提交观察先行；有真实收益才执行唯一RO完整质量，不计性能。"""
import argparse
from pathlib import Path
import subprocess
import sys
from win_readonly_rom import ROOT,PLAN,checked_plan,sha,read,save,env
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=checked_plan();a.output.mkdir(parents=True,exist_ok=False)
    run=dict(purpose=__doc__,environment=env(),plan_sha256=sha(PLAN),commands=[],status='running');save(a.output/'execution.json',run)
    def execute(script,output,extra=()):
        command=[sys.executable,'-X','utf8',str(ROOT/'scripts'/script),*extra,'--output',str(output)]
        value=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');run['commands'].append(dict(command=command,returncode=value.returncode,stdout=value.stdout,stderr=value.stderr));save(a.output/'execution.json',run)
        if value.returncode:run['status']='failed';save(a.output/'execution.json',run);raise RuntimeError('预冻结执行失败，不补跑：'+script)
    records={}
    for mode in ('original_cow','cow','readonly'):
        output=a.output/mode;execute('measure_readonly_rom.py',output,('--mode',mode));records[mode]=read(output/'results.json')
    deltas={mode:{phase:data['phases'][phase]['PrivateUsage']-data['phases']['before']['PrivateUsage'] for phase in ('mapped_untouched','prepared','all_pages_read','closed')} for mode,data in records.items()}
    gains={phase:min(deltas['original_cow'][phase],deltas['cow'][phase])-deltas['readonly'][phase] for phase in ('mapped_untouched','prepared','all_pages_read')}
    # 单次观察预定至少1MiB且映射/prepare/逐页读取三个时点全部满足，防小分配噪声冒充整视图收益。
    passed=all(value>=(1<<20) for value in gains.values())
    save(a.output/'commit-summary.json',dict(passed=passed,purpose='三角色同import新进程，PrivateUsage相对自身before；两个COW对照均须优于RO至少1MiB。',deltas=deltas,conservative_gain_bytes=gains,minimum_gain_bytes=1<<20,scope='系统commit仅辅助，不把commit差称为capacity或WS差；只有单次微实验，不宣称跨环境稳定性或速度。'))
    if not passed:run['status']='stopped-no-commit-benefit';save(a.output/'execution.json',run);print(run['status']);return
    execute('verify_readonly_rom.py',a.output/'quality')
    run['status']='quality-passed-performance-not-run';save(a.output/'execution.json',run);print(run['status'])
if __name__=='__main__':main()
