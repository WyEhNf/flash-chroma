"""执行真实 FreeRTOS 固件；退出码和成功标记必须同时通过。"""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu", default="qemu-system-arm")
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    command = [args.qemu, "-M", "mps2-an385", "-cpu", "cortex-m3",
               "-display", "none", "-monitor", "none", "-serial", "none",
               "-semihosting-config", "enable=on,target=native",
               "-kernel", str(args.elf.resolve())]
    try:
        result = subprocess.run(command, capture_output=True, timeout=args.timeout)
    except subprocess.TimeoutExpired as error:
        sys.stdout.buffer.write((error.stdout or b"") + (error.stderr or b""))
        print("QEMU 超时：固件未完成验收", file=sys.stderr)
        return 1
    output = result.stdout + result.stderr
    sys.stdout.buffer.write(output)
    marker = b"PASS: FreeRTOS Cortex-M3 LUT contract"
    return 0 if result.returncode == 0 and marker in output else 1


if __name__ == "__main__":
    raise SystemExit(main())
