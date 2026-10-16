"""执行真实 FreeRTOS 固件；退出码和成功标记必须同时通过。"""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu")
    parser.add_argument("--target", choices=("cortex-m3", "riscv32"), default="cortex-m3")
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    if args.target == "cortex-m3":
        command = [args.qemu or "qemu-system-arm", "-M", "mps2-an385", "-cpu", "cortex-m3",
                   "-display", "none", "-monitor", "none", "-serial", "none",
                   "-semihosting-config", "enable=on,target=native"]
        marker = b"PASS: FreeRTOS Cortex-M3 LUT contract"
    else:
        command = [args.qemu or "qemu-system-riscv32", "-M", "virt", "-cpu", "rv32",
                   "-m", "16M", "-smp", "1", "-bios", "none",
                   "-display", "none", "-monitor", "none", "-serial", "stdio"]
        marker = b"PASS: FreeRTOS RV32 LUT contract"
    command += ["-kernel", str(args.elf.resolve())]
    try:
        result = subprocess.run(command, capture_output=True, timeout=args.timeout)
    except subprocess.TimeoutExpired as error:
        sys.stdout.buffer.write((error.stdout or b"") + (error.stderr or b""))
        print("QEMU 超时：固件未完成验收", file=sys.stderr)
        return 1
    output = result.stdout + result.stderr
    sys.stdout.buffer.write(output)
    return 0 if result.returncode == 0 and marker in output else 1


if __name__ == "__main__":
    raise SystemExit(main())
