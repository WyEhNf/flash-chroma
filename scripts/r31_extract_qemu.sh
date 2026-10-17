#!/bin/sh
# Local extraction only; never installs packages or registers binfmt handlers.
set -eu
cd /mnt/f/Hackathon/projects/16-lut-color/artifacts/r31-arm-tools
package=$(find . -maxdepth 1 -name 'qemu-user*.deb' -print -quit)
test -n "$package"
actual=$(sha256sum "$package" | cut -d ' ' -f1)
test "$actual" = f0585a9676a039f46607f185b3657c1e78c1ba4187595724cc567fcc1ae0d1b9
dpkg-deb --extract "$package" package
package/usr/bin/qemu-aarch64 --version
package/usr/bin/qemu-aarch64_be --version
