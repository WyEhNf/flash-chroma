"""Zen4两组发射诊断事件；按Linux v6.18与AMD计数掩码语义解释，不用于Skylake。"""
import ctypes as ct
import fcntl
import os
import struct

from probe_skylake_pmu import Attr


def raw(event, umask=0, cmask=0):
    return (event & 255) | ((event & 0xf00) << 24) | (umask << 8) | (cmask << 24)


EVENT_GROUPS = {
    'dispatch': [('cycles', raw(0x76)), ('instructions', raw(0xc0)),
        ('frontend_unused_slots', raw(0x1a0, 1)), ('backend_unused_slots', raw(0x1a0, 0x1e)),
        ('load_queue_stall_cycles', raw(0xae, 2)), ('store_queue_stall_cycles', raw(0xae, 4))],
    'resources': [('cycles', raw(0x76)), ('integer_prf_stall_cycles', raw(0xae, 1)),
        ('integer_scheduler_any_stall_cycles', raw(0xaf, 15, 1)),
        ('retire_token_stall_cycles', raw(0xaf, 0x20)),
        ('oldest_not_complete', raw(0xd6, 2)), ('oldest_load_not_complete', raw(0xd6, 0xa2))]
}


class ThreadGroup:
    """每个目标TID一组六事件，同时pinned；原始字节在任何解释前返回。"""
    def __init__(self, tid, group_name):
        self.tid, self.group_name, self.fds = tid, group_name, []
        self.events = EVENT_GROUPS[group_name]
        libc = ct.CDLL(None, use_errno=True)
        call = libc.syscall
        call.restype = ct.c_long
        call.argtypes = [ct.c_long, ct.c_void_p, ct.c_int, ct.c_int, ct.c_int, ct.c_ulong]
        try:
            for name, config in self.events:
                attr = Attr()
                attr.type, attr.size, attr.config, attr.read_format = 4, ct.sizeof(attr), config, 11
                attr.flags = 32 | 64 | (5 if not self.fds else 0)
                fd = call(298, ct.byref(attr), tid, -1, self.fds[0] if self.fds else -1, 8)
                if fd < 0:
                    raise OSError(ct.get_errno(), f'TID {tid}事件组不可用：{group_name}/{name}')
                self.fds.append(fd)
        except BaseException:
            self.close()
            raise

    def enable(self):
        fcntl.ioctl(self.fds[0], 0x2403, 1)
        fcntl.ioctl(self.fds[0], 0x2400, 1)

    def disable(self):
        fcntl.ioctl(self.fds[0], 0x2401, 1)

    def read(self):
        data = os.read(self.fds[0], 4096)
        result = {'tid': self.tid, 'group': self.group_name, 'raw_group_read_hex': data.hex()}
        if len(data) != 72:
            result['decode_error'] = '六事件组字节数不是72'
            return result
        values = struct.unpack('<9Q', data)
        if values[0] != 6:
            result['decode_error'] = '事件数不是6'
            return result
        result.update(time_enabled_ns=values[1], time_running_ns=values[2],
            counts=dict(zip([n for n, _ in self.events], values[3:])),
            running_fraction=values[2]/values[1] if values[1] else None)
        return result

    def close(self):
        for fd in self.fds:
            os.close(fd)
        self.fds = []


def metrics(counts, pixels):
    cycles = counts['cycles']
    values = {'per_nominal_pixel': {k: v/pixels for k, v in counts.items()} if pixels else None}
    if 'instructions' in counts:
        values['instructions_per_cycle'] = counts['instructions']/cycles if cycles else None
    for name, count in counts.items():
        if name.endswith('_unused_slots'):
            values[name+'_fraction'] = count/(6*cycles) if cycles else None
        elif name.endswith('_stall_cycles') or name in ('oldest_not_complete', 'oldest_load_not_complete'):
            values[name+'_fraction'] = count/cycles if cycles else None
    return values


def check_units(counts):
    cycles = counts['cycles']
    for name, count in counts.items():
        if name.endswith('_unused_slots') and not 0 <= count <= 6*cycles:
            raise ValueError('槽位事件超过六倍周期：'+name)
        if (name.endswith('_stall_cycles') or name in ('oldest_not_complete', 'oldest_load_not_complete')) and not 0 <= count <= cycles:
            raise ValueError('周期事件超过总周期：'+name)
    if 'oldest_load_not_complete' in counts and counts['oldest_load_not_complete'] > counts['oldest_not_complete']:
        raise ValueError('最老load等待超出最老指令等待')
