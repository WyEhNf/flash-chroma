# Reproducible Ubuntu 24.04 container for Hackathon 2026 Problem 16 (极速焕彩)
# Usage:
#   docker build -t jisu-huancai:latest .
#   docker run --rm -it -v "$PWD":/workspace jisu-huancai:latest pixi run test
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH="/root/.pixi/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    build-essential \
    cmake \
    ninja-build \
    python3 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://pixi.sh/install.sh | bash

WORKDIR /workspace
COPY pixi.toml pixi.lock ./
RUN pixi install -a

COPY . .
RUN pixi run build

CMD ["pixi", "run", "test"]
