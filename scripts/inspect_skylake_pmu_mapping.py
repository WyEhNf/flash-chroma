"""只读保存本机sysfs泛化cache事件映射，不创建事件或修改权限。"""
from pathlib import Path
import argparse,json,platform
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise ValueError('不得覆盖旧回执')
names=['/sys/bus/event_source/devices/cpu/events/cache-references','/sys/bus/event_source/devices/cpu/events/cache-misses','/sys/bus/event_source/devices/cpu/caps/max_precise','/proc/sys/kernel/perf_event_paranoid']
values={name:Path(name).read_text().strip() if Path(name).is_file() else None for name in names}
result={'purpose':__doc__,'platform':platform.platform(),'values':values,'new_event_calls':0,'new_native_calls':0,'new_performance_calls':0,'limitation':'此主机的generic事件编码，不代表Skylake、不保证等于L3命中/未命中；不与其他阶段的绝对周期相除'}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
