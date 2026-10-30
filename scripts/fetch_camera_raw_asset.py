"""下载公开摄影机素材或工具，保留来源、原字节哈希与失败记录。"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-bytes", type=int, default=800_000_000)
    args = parser.parse_args()
    target = args.output.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    record = target.with_name(target.name + ".download.json")
    partial = target.with_name(target.name + ".partial")
    if target.exists() or partial.exists() or record.exists():
        raise FileExistsError("保留已有下载及原始失败记录，请使用新目录")
    info = {"source_url": args.url, "output": str(target), "status": "started"}
    start = time.perf_counter()
    try:
        with requests.get(args.url, stream=True, timeout=(15, 45)) as response:
            info.update(http_status=response.status_code, headers=dict(response.headers))
            response.raise_for_status()
            length = int(response.headers.get("Content-Length", 0))
            if length > args.max_bytes:
                raise ValueError("远端文件超过本次下载上限")
            digest, size = hashlib.sha256(), 0
            with partial.open("xb") as stream:
                for chunk in response.iter_content(1024 * 1024):
                    size += len(chunk)
                    if size > args.max_bytes:
                        raise ValueError("接收字节超过本次下载上限")
                    stream.write(chunk)
                    digest.update(chunk)
            if length and size != length:
                raise ValueError("实际长度与HTTP长度不符")
            partial.rename(target)
            info.update(status="downloaded", bytes=size, sha256=digest.hexdigest())
    except Exception as exc:
        info.update(status="failed", error=repr(exc))
        raise
    finally:
        info["elapsed_seconds"] = time.perf_counter() - start
        record.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in info.items() if k not in ("headers", "source_url")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
