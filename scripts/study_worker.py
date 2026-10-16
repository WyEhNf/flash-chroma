"""为Windows检查点写入注入有限重试；不改变算法、模型或误差计算。"""
import importlib
import json
from pathlib import Path
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import compatibility

original_write = compatibility.write_json


def reliable_write(path, value):
    for attempt in range(30):
        try:
            return original_write(path, value)
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(.05 * (1 + attempt))


compatibility.write_json = reliable_write
module_name = sys.argv.pop(1)
module = importlib.import_module(module_name)
module.main()
