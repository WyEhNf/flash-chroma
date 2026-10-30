# 缓存布局双库服务器验收

本包比较原缓存修订4与R连续缓存修订13。模型、范围、表值及容量相同，Windows本机唯一比较因一个四线程进程回退超2%而未通过；本包不升级默认，不改旧四方案包，不把本机结果当Skylake成绩。照片用途限制保留在assets/photos/manifest.json。

目标Linux x86_64需Python3.11及以上标准库、CMake3.24及以上、GNU C/C++和OpenMP，无需NumPy/Pillow。解包后运行：

```sh
python3 scripts/run_skylake_layout_server.py --bundle bundle-manifest.json --output artifacts/layout-server-v1 --compiler /usr/bin/g++ --c-compiler /usr/bin/gcc
```

默认只构建和集中正确性，不运行性能比较。正式Skylake验收需先记录真实SKU、系统、微码/GDS和允许CPU集合；可加--expected-cpu完整型号及--cpus四个同L3/NUMA不同物理核。确认后显式加--measure，执行唯一固定四串行新进程AB/BA/BA/AB、1/4线程、整批/逐图、每配置5轮，共160组100图。每轮完整输出SHA在原生计时之外核验，源、库、团队落点及容量均记录。该逐轮校验协议不同于旧内部bench，不混用绝对时间。

先验13个固定边界/窄带布局的3432次偏移/尾部比较，完整物理缓存与独立表、12组完整256³、两种调度的8个配置各两轮百图和计时器拒绝契约。调度验证经过计时器但时长不用于性能结论。所有场景须同时满足apply配对中位改善至少3%、任一进程回退不超过2%、copy+apply及准备+已预热首100图不退化，才可通过本次机器门槛。没有自动重试、扫描、安装依赖、改安全缓解或改频。输出必须新目录；失败日志保留。

生成端使用NumPy导出少量独立预期，服务器只读冻结字节。原始100图/完整流只放本地传输包，不入Git。AMD/WSL验证不是Skylake实测，官方数据/Threshold和派生表许可仍待确认。
