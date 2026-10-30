# 固定4KiB输入页覆盖率证据

Agent：Codex /root/speed；Operator：当前用户。2026-10-24在Windows11 x64、Ryzen9 8945HX、Python3.12.14/NumPy1.26.4/Pillow10.4只读运行；没有DLL加载、原生候选、性能计时或后台工作。[阶段说明](../../../docs/stages/2026-10-24-p16-lazy-pages-lifecycle.md)解释逻辑预算和生命周期候选。

`executed-plan.json`记录事前单粒度方案、源与脚本身份。`results.json`保存全部200个逐图/分辨率计数、固定首1/10/100和固定十图组，未挑选最好起点。`present-pages.bin`按scale1、scale2各100张manifest图序，每图512 B低位优先位图，总计102,400 B。其精确页号由GB半字公式与完整RGB地址公式逐像素一致验证。标准100图已覆盖95.34%/92.21%，不是按需建表加速数据。

独立复算只读位图，不读照片、不加载DLL：

```powershell
python -X utf8 scripts/audit_p16_lazy_pages.py report/data/p16-lazy-pages-profile-v1
```

从照片复现需创建新目录，流式读取100照片并核验输入SHA：

```powershell
python -X utf8 scripts/profile_p16_lazy_pages.py --plan experiments/p16-lazy-pages-profile-v1.json --output artifacts/p16-lazy-pages-profile-new
```

`offline-audit.json`为只读独立复算，`manifest.json`绑定本目录除清单自身的原始字节。snapshot共享与compiled artifact是文档静态比较，未在本阶段实施或给出速度结果。
