"""96独立进程控制；不修改产品DLL，失败不继续计时。"""
import ctypes as ct
from pathlib import Path
import psutil
from bench_p16_model_pair import checked


class Record(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ('version', 'omp_tid', 'team_size', 'os_tid', 'cpu_before', 'cpu_after',
        'group_before', 'group_after', 'query_before_ok', 'set_attempted', 'set_error', 'query_after_ok')]
    _fields_ += [(n, ct.c_uint64) for n in ('mask_before', 'previous_mask', 'mask_after')]


class Group(ct.Structure):
    _fields_ = [('Mask', ct.c_size_t), ('Group', ct.c_ushort), ('Reserved', ct.c_ushort * 3)]


class ControlFailure(RuntimeError):
    pass


class Control:
    def __init__(self, plan, threads):
        assert threads in (1, 4) and ct.sizeof(Record) == 72
        self.plan, self.threads = plan, threads
        self.snapshots, self.tids, self.saved, self.saved_index = [], [], None, None
        self.healthy, self.policy = True, 'U'
        self.kernel = ct.WinDLL('kernel32', use_last_error=True)
        k = self.kernel
        k.GetCurrentThread.restype = ct.c_void_p
        k.GetCurrentThreadId.restype = ct.c_uint32
        k.GetCurrentProcessorNumber.restype = ct.c_uint32
        k.GetThreadGroupAffinity.argtypes = [ct.c_void_p, ct.POINTER(Group)]
        k.GetThreadGroupAffinity.restype = ct.c_int
        k.SetThreadAffinityMask.argtypes = [ct.c_void_p, ct.c_size_t]
        k.SetThreadAffinityMask.restype = ct.c_size_t
        self.set_main(0x55, 'initial_main55')
        if threads == 1:
            self.tids = [int(k.GetCurrentThreadId())]
        else:
            self.helper = ct.CDLL(str(checked(plan['affinity_helper'])))
            self.fn = self.helper.p16_omp_affinity
            self.fn.argtypes = [ct.POINTER(Record), ct.c_size_t, ct.c_size_t, ct.c_uint32, ct.POINTER(Record)]
            self.fn.restype = ct.c_int

    def require(self, good, message):
        if not good:
            self.healthy = False
            raise ControlFailure(message)

    def query_main(self):
        g = Group()
        ok = self.kernel.GetThreadGroupAffinity(self.kernel.GetCurrentThread(), ct.byref(g))
        self.require(ok != 0, '主线程group查询失败')
        return {'os_tid': int(self.kernel.GetCurrentThreadId()), 'group': int(g.Group),
            'mask': int(g.Mask), 'cpu': int(self.kernel.GetCurrentProcessorNumber())}

    def set_main(self, mask, context):
        a = self.query_main()
        previous = int(self.kernel.SetThreadAffinityMask(self.kernel.GetCurrentThread(), mask))
        error = ct.get_last_error() if not previous else 0
        self.require(previous != 0, '主线程设置mask失败：' + str(error))
        b = self.query_main()
        row = {'version': 1, 'omp_tid': 0, 'team_size': 1, 'os_tid': b['os_tid'],
            'cpu_before': a['cpu'], 'cpu_after': b['cpu'], 'group_before': a['group'], 'group_after': b['group'],
            'query_before_ok': 1, 'set_attempted': 1, 'set_error': error, 'query_after_ok': 1,
            'mask_before': a['mask'], 'previous_mask': previous, 'mask_after': b['mask']}
        self.snapshots.append({'context': context, 'scope': 'main_setup' if self.threads == 4 else 'main',
            'action': 1 if mask == 1 else 2, 'return_code': 0, 'desired_mask': mask, 'team': [row]})
        self.require(a['os_tid'] == b['os_tid'] and a['group'] == b['group'] == 0 and b['mask'] == mask,
            '主线程身份/group/mask不符')
        self.require(mask != 1 or b['cpu'] == 0, '固定主线程CPU不符')

    def call(self, action, context, saved=None):
        values = (Record * 4)()
        code = self.fn(values, 4, 72, action, saved)
        row = {'context': context, 'scope': 'team', 'action': action, 'return_code': int(code),
            'team': [{n: int(getattr(v, n)) for n, _ in Record._fields_} for v in values]}
        self.snapshots.append(row)
        # helper可能已经部分设置；不重试、恢复新pool或继续计时。
        self.require(code == 0, '四线程helper失败：' + str(code))
        self.require(all(v['version'] == 1 and v['omp_tid'] == t and v['team_size'] == 4
            and v['query_before_ok'] and v['query_after_ok'] and v['group_before'] == v['group_after'] == 0
            for t, v in enumerate(row['team'])), '四线程ABI/group不符')
        tids = [v['os_tid'] for v in row['team']]
        self.require(len(set(tids)) == 4 and (not self.tids or tids == self.tids), '四线程pool身份改变')
        return values

    def initialize_pool(self):
        if self.threads == 1:
            return self.endpoint('main_initialized')
        values = self.call(0, 'initial_team55')
        self.tids = [int(v.os_tid) for v in values]
        self.require(all(v.mask_before == v.mask_after == 0x55 for v in values), '初始team未完全55')
        self.saved = self.call(1, 'original_pin_previous55')
        self.saved_index = len(self.snapshots) - 1
        self.require(all(v.previous_mask == 0x55 for v in self.saved), '恢复凭证不是原始55')
        self.call(2, 'initial_restore55', self.saved)
        return self.endpoint('pool_initialized')

    def apply_policy(self, policy, context):
        self.require(policy in ('U', 'P'), '未知policy')
        if self.threads == 1:
            self.set_main(1 if policy == 'P' else 0x55, context)
        else:
            self.require(self.saved is not None, '没有原始55恢复凭证')
            if policy == 'P':
                self.call(1, context)  # 不覆盖saved，P→P的previous可为单bit。
            else:
                self.call(2, context, self.saved)
        self.policy = policy
        return self.endpoint(context + '_verified')

    def endpoint(self, context):
        if self.threads == 4:
            values = self.call(0, context)
            team = self.snapshots[-1]['team']
        else:
            value = self.query_main()
            team = [{'version': 1, 'omp_tid': 0, 'team_size': 1, 'os_tid': value['os_tid'],
                'cpu_before': value['cpu'], 'cpu_after': value['cpu'], 'group_before': value['group'],
                'group_after': value['group'], 'query_before_ok': 1, 'query_after_ok': 1,
                'set_attempted': 0, 'set_error': 0, 'previous_mask': 0,
                'mask_before': value['mask'], 'mask_after': value['mask']}]
            self.snapshots.append({'context': context, 'scope': 'main', 'action': 0, 'return_code': 0, 'team': team})
        self.require([r['os_tid'] for r in team] == self.tids, '组端点OS TID变化')
        for t, row in enumerate(team):
            wanted = (1 << (2 * t)) if self.policy == 'P' else 0x55
            self.require(row['group_before'] == row['group_after'] == 0 and row['mask_before'] == row['mask_after'] == wanted,
                '组端点实际mask不符')
            self.require(self.policy != 'P' or row['cpu_after'] == 2 * t, '固定CPU端点不符')
        return len(self.snapshots) - 1

    def modules(self):
        paths = {str(Path(v.path).resolve()) for v in psutil.Process().memory_maps()
            if Path(v.path).name.lower() == 'libgomp-1.dll'}
        expected = checked(self.plan['libgomp'])
        self.require(len(paths) == 1 and next(iter(paths)).lower() == str(expected).lower(), '实际libgomp实例/路径不符')
        return sorted(paths)

    def export(self):
        return {'threads': self.threads, 'tids': self.tids, 'saved_pin_snapshot': self.saved_index,
            'healthy': self.healthy, 'policy': self.policy, 'snapshots': self.snapshots}
