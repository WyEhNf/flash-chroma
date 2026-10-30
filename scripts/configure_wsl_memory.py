"""为本机CPU工作流配置WSL内存预算；默认预览，--apply会备份并重启WSL。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def merge(text, section, values):
    """仅替换目标键，保留其他节、设置和注释；重复键拒绝自动处理。"""
    lines = text.splitlines()
    headings = [(i, m.group(1).strip().lower()) for i, line in enumerate(lines)
                if (m := re.fullmatch(r"\s*\[([^]]+)\]\s*", line))]
    starts = [i for i, name in headings if name == section.lower()]
    if len(starts) > 1:
        raise ValueError("配置存在重复节：" + section)
    if not starts:
        lines += ["", "[" + section + "]"] + [f"{key}={value}" for key, value in values.items()]
    else:
        start = starts[0]
        end = next((i for i, _ in headings if i > start), len(lines))
        pending = dict(values)
        seen = set()
        for i in range(start + 1, end):
            match = re.match(r"^\s*([^#;=]+?)\s*=", lines[i])
            if not match:
                continue
            name = match.group(1).strip().lower()
            key = next((key for key in values if key.lower() == name), None)
            if key is not None:
                if key in seen:
                    raise ValueError("配置存在重复键：" + key)
                seen.add(key)
                lines[i] = f"{key}={values[key]}"
                pending.pop(key, None)
        lines[end:end] = [f"{key}={value}" for key, value in pending.items()]
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--memory", choices=("1GB", "1536MB", "2GB"), default="1GB")
    parser.add_argument("--directory", type=Path, default=ROOT / "artifacts/wsl-memory-budget-v1")
    args = parser.parse_args()
    if os.name != "nt":
        raise SystemExit("需要在Windows中运行")
    directory = args.directory.resolve()
    swap = directory / "swap.vhdx"
    config = Path.home() / ".wslconfig"
    original = config.read_bytes() if config.exists() else b""
    text = original.decode("utf-8-sig")
    values = {"memory": args.memory, "processors": "4", "swap": "2GB",
              "swapFile": str(swap).replace("\\", "\\\\"), "guiApplications": "false",
              "gpuSupport": "false", "nestedVirtualization": "false", "vmIdleTimeout": "30000"}
    proposed = merge(merge(text, "wsl2", values), "experimental", {"autoMemoryReclaim": "dropCache"})
    if not args.apply:
        print(proposed)
        return
    # 单次本地维护不打断正在处理的GUI任务。
    try:
        state = json.load(urllib.request.urlopen("http://127.0.0.1:8765/api/state", timeout=3))
    except OSError as error:
        raise SystemExit("无法检查本机GUI任务，请先启动GUI服务：" + str(error))
    if any(job["status"] in ("queued", "running") for job in state["jobs"]):
        raise SystemExit("GUI有任务正在运行，请在任务结束后应用配置")
    directory.mkdir(parents=True, exist_ok=True)
    backup = directory / ("wslconfig-before-" + time.strftime("%Y%m%d-%H%M%S") + ".bin")
    with backup.open("xb") as stream:
        stream.write(original)
    environment = dict(os.environ, WSL_UTF8="1")
    stopped = subprocess.run(["wsl.exe", "--shutdown"], capture_output=True, timeout=30, env=environment)
    if stopped.returncode:
        raise SystemExit("WSL未能正常关闭，没有改写配置")
    config.write_text(proposed, encoding="utf-8", newline="\n")
    record = {"purpose": "本机CPU工作流WSL内存预算，不是性能或精度验收", "backup": str(backup),
              "before_sha256": hashlib.sha256(original).hexdigest(),
              "after_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
              "config": proposed, "auto_reclaim_already_default": True,
              "notes": "dropCache为当前WSL文档默认值，显式设置不单独计作内存降低；保留其他网络设置和原交换文件"}
    (directory / "configuration.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
