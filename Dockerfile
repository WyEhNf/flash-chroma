# 固定 Pixi 版本；数值依赖由 pixi.lock 决定，仅安装默认环境。
FROM ghcr.io/prefix-dev/pixi:0.81.0

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

WORKDIR /workspace
COPY pixi.toml pixi.lock ./
RUN pixi install --locked -e default

COPY . .
RUN pixi run --locked build

CMD ["pixi", "run", "--locked", "test"]
