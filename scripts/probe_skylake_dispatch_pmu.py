"""仅探测两组Zen4原始事件能否同时调度；不加载候选库或执行候选像素。"""
import argparse
import os
import platform
from pathlib import Path

from skylake_server_support import save, digest
from zen4_dispatch_pmu_support import EVENT_GROUPS, ThreadGroup, check_units, metrics


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError('不得覆盖事件探测或自动重试')
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise ValueError('仅Linux x86_64')
    os.sched_setaffinity(0, {0})
    cpu = Path('/proc/cpuinfo').read_text().split('\n\n')[0]
    if 'cpu family\t: 25' not in cpu or 'model\t\t: 97' not in cpu:
        raise ValueError('仅冻结Zen4 family25/model97')
    result = {'purpose': __doc__, 'available': False, 'records': [], 'events': EVENT_GROUPS,
        'cpuinfo': cpu, 'platform': platform.platform(), 'candidate_pixel_calls': 0,
        'candidate_timing_calls': 0, 'source_sha256': {Path(__file__).name: digest(__file__),
            **{name: digest(Path(__file__).with_name(name)) for name in
                ('zen4_dispatch_pmu_support.py', 'probe_skylake_pmu.py', 'skylake_server_support.py')}},
        'limitation': '可调度和计数范围检查不等于宿主已校准全部虚拟PMU语义；零计数不自动表示没有瓶颈'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        for name in EVENT_GROUPS:
            group = ThreadGroup(os.getpid(), name)
            try:
                group.enable()
                value = sum(range(200000))
                group.disable()
                record = group.read()
                result['records'].append(record)
                save(a.output, result)
                if value != 19999900000 or 'decode_error' in record:
                    raise ValueError('探测校验或解码不同')
                if record['running_fraction'] is None or record['running_fraction'] < .99:
                    raise ValueError('六事件未同时运行至少99%')
                check_units(record['counts'])
                if record['counts']['cycles'] <= 0 or ('instructions' in record['counts'] and record['counts']['instructions'] <= 0):
                    raise ValueError('基本周期或退休事件为空')
                record.update(metrics(record['counts'], 0))
            finally:
                group.close()
        result['available'] = True
    except BaseException as exc:
        result['failure'] = {'type': type(exc).__name__, 'message': str(exc)}
    save(a.output, result)
    print({'available': result['available'], 'failure': result.get('failure')}, flush=True)


if __name__ == '__main__':
    main()
