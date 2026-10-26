"""Native页指针唯一构建的冻结身份；不执行prepare或图像API。"""
from pathlib import Path
from study_memory_rom import ROOT, read, save, sha

PLAN = ROOT / 'experiments/page-id16-native-pages-build-v1.json'


def checked_plan():
    value = read(PLAN)
    for name, expected in value['source_sha256'].items():
        if sha(ROOT / name) != expected:
            raise AssertionError('native-pages冻结源改变：' + name)
    for name, expected in value['input_sha256'].items():
        if sha(name) != expected:
            raise AssertionError('native-pages冻结输入改变：' + name)
    return value
