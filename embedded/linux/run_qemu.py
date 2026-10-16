"""校验锁定内核，启动真正的 AArch64 Linux，并要求客户机契约通过。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import zlib


def kernel_image(cache: Path) -> Path:
    lock = json.loads(Path(__file__).with_name("kernel-lock.json").read_text())
    cache.mkdir(parents=True, exist_ok=True)
    source = cache / "vmlinuz-virt"
    if not source.exists():
        with urllib.request.urlopen(lock["url"], timeout=60) as response:
            data = response.read()
    else:
        data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != lock["sha256"]:
        raise ValueError("Linux 内核 SHA-256 与锁文件不符")
    source.write_bytes(data)
    # 锁定文件为 EFI zboot：提取 gzip，校验解压后的 ARM64 Image 头。
    image = zlib.decompress(data[data.index(b"\x1f\x8b\x08"):], wbits=31)
    if image[56:60] != b"ARM\x64":
        raise ValueError("解压结果不是 ARM64 Linux Image")
    output = cache / "Image"
    output.write_bytes(image)
    print(f"内核：{lock['release']}，SHA-256={lock['sha256']}", flush=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu", default="qemu-system-aarch64")
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--initramfs", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    image = kernel_image(args.cache)
    command = [args.qemu, "-M", "virt", "-cpu", "cortex-a53", "-smp", "1", "-m", "256M",
               "-display", "none", "-monitor", "none", "-serial", "stdio", "-nic", "none",
               "-kernel", str(image), "-initrd", str(args.initramfs),
               "-append", "console=ttyAMA0 rdinit=/init panic=-1 quiet"]
    try:
        result = subprocess.run(command, capture_output=True, timeout=args.timeout)
    except subprocess.TimeoutExpired as error:
        sys.stdout.buffer.write((error.stdout or b"") + (error.stderr or b""))
        print("QEMU 超时：Linux 客户机未完成验收", file=sys.stderr)
        return 1
    output = result.stdout + result.stderr
    sys.stdout.buffer.write(output)
    return 0 if result.returncode == 0 and b"PASS: Linux Cortex-A53 LUT contract" in output else 1


if __name__ == "__main__":
    raise SystemExit(main())
