# 双像素64位输入读取

Agent：Codex /root、/root/direct_tile_audit；Operator：WyEhNf；Task：完整RGB8精度不降、通用AVX2、相对23至少三倍吞吐；Status：Failed（79四线程纯apply）/ Draft，整体In Progress。基于Draft [PR72](https://github.com/WyEhNf/flash-chroma/pull/72)的`91b7c7359f938876d22fc7fc12fa7b2b0e02ebe0`，本阶段研究新修订79，不重测78或拼接历史结果。

[源码](../../experiments/skylake-pair48-runtime/andn_inplace/channel_avx2.cpp)仅把两个独立BMI1像素TU的`read_wide`改为每两像素一次8字节ANDN，掩码`0xffff000000000000`保留低48位，再用低24位和右移24位分别查ID。两对仍形成原四ID屏障。原地和分离各唯一入口分别编译，保持78的循环计数方式、64/32全部读取后才输出、NTA/NT/SFENCE、64B目的对齐和原始精确24B尾部。主线性回退原字节保持，泛型runtime仅改pair48身份和revision79；构造一次检测BMI1，不支持时精确回退，无新表、句柄成员或内容特判。GNU `%q`完整寄存器及精确memory/cc约束依据[GCC15官方说明](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/Extended-Asm.html#x86-Operand-Modifiers)；未成功读取64位ANDN的uops网页，不引用其吞吐或端口。

此前78照片诊断LQ受阻约71%/73%、FE空槽约0.8%/2.4%，仅支持“用额外整数指令换更少输入load”的有限假设，不证明输入load是主因。宽主体输入请求仍4B/像素、ID和palette仍各一次；输入加载指令1降至0.5，合计这三类加载3降至2.5，而不是输入/DRAM流量减半。原地64/32像素最大读取194/98B，原guard72/40像素分别提供216/120B；精确8像素尾部仍仅24B。

[计划](../../experiments/skylake-pair48-v1.json)SHA`a31c77dc7fc966c3314b5e1eda585fd1d11e840050314a78e9eb689b6c85c180`，71项源码身份，冻结时未编译或执行像素。预期每对增加MOV/AND/SHR，所以事前静态门槛是32/16条mem64 ANDN、W1/完整掩码、逐条拆位到每个正确ID、无热区栈访问、四ID先行、先读后写及ISA隔离，不能沿用78的少机器指令门槛；实际三倍吞吐门槛不变。

实际构建环境Ryzen9 8945HX / Windows11宿主WSL2 Ubuntu Linux6.18.33.2 / GCC15.2 / Python3.14.4标准库；GNU Release，像素TU为`-mavx2 -mtune=skylake -ffp-contract=off`，仅两独立TU加`-mbmi`。build SHA`f5af259f501547e11a5ab8b4c870fb462fd78410850e3973ed5cd7b204162375`，候选库SHA`7b05455cc6611d83e2ecd9b8fadbebbe45bd90c8495b7d7a73ab328cb9ad3644`，参考库仍为23的`b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e`。不是Skylake实测。

| 区段 | 79机器指令 | 78机器指令 | mem64输入 | ID / palette | 热区栈访问 |
| --- | ---: | ---: | ---: | ---: | --- |
| 原地64循环 | 321 | 257 | 32 | 64 / 64 | 无 |
| 原地32循环 | 170 | 138 | 16 | 32 / 32 | 无 |
| 分离64循环 | 319 | 255 | 32 | 64 / 64 | 无 |
| 分离32直线尾 | 168 | 136 | 16 | 32 / 32 | 无 |

静态v2 SHA`f081ad5e9fd3772c27a1b8900fdfc99d5524108e1947da39361e66fe94010efd`通过四个宽区段、ELF真实字节、输入偏移和逐条ANDN48→MOV截断/AND24或SHR64→ID索引、mask消费活跃期、四ID、先读后写和编译选项范围。热区无栈不表示全函数无栈。初次Linux执行因脚本`inspect.py`遮蔽Python3.14标准库而在argparse阶段失败，保留回执，使用`python3 -P`使标准库正确解析，源码未改。正式初件唯一误报是分离32最后ANDN后死mask寄存器用于SHR结果；v2逐条确认所有消费前掩码正确、后续无ANDN，允许最后消费后的结果处理，旧检查器/结果保留，候选/对象/事前门槛未改。

独立静态回执SHA`d56c26f6bb43869d0073103b18ff3bf591e98df7292386b22652ddb40323f917`通过四个区段及dispatcher全部可执行字节覆盖/逐字节一致、无AVX/BMI/BMI2/EVEX/AVX512分派器泄漏、71项源身份和验证胶水归一比较。该只读复核不执行像素或性能。

完整精度结果SHA`41628bf768a3673a3f83afef75879315ea080465aa9ddd40d53e6688d93c108f`通过：独立16,777,216色物理表、24组完整RGB8原地/分离接口、2208有限后端/偏移、4416分离/同缓冲比较、736保护页、1280对齐、44分离拒绝及9直表拒绝、null特征1项；byte/sentinel零差。实际pair48为single0/chain1，物理表SHA仍`a020c67a0e8ce77e668e6c6d85206af53005923316b4778194637182b4cfaea0`。资源记账single272859、chain28046644字节，相对23分别+24和+24+16MiB；不是RSS或官方预算结论。

完整域后冻结[验证身份](../../experiments/skylake-pair48-validation-v1.json)SHA`2208a1713865bd7f859cacdb18b95e165928ea4e8eacbbf709078302c9c3ee72`、[首次性能策略](../../experiments/skylake-pair48-long-perf-v1.json)SHA`1fed7dae806c2350e345f36306df2e60fb67dea64d5fba6825b1064d309145ab`。对78策略的只读比较确认，除新计划/构建/全域/验证/脚本身份、说明和确认目录外，全部门槛、ABBA/线程顺序、同句柄A/A、16/64内轮、绑定/THP/空闲及唯一条件确认不变；两个胶水归一身份后完全相同。

首次四进程长批次已完成，结果SHA`2d00684c0a0eea66e37227318be3a972ea2e4bae34333c98a42a0eefba1b4db4`。每角色每进程一个句柄复用两档线程，纯apply/旧copy+apply与真实分离分别计量；单线程每批16内轮、四线程64内轮，合计1920轮，48次预热及48次批末独立SHA，不是每内轮独立SHA。批内均值形成四个worker配对比，再取中位数：

| 接口 | 1线程耗时比 / 吞吐 | 4线程耗时比 / 吞吐 |
| --- | ---: | ---: |
| 纯apply | 0.324159 / **3.084902倍** | 0.424973 / **2.353089倍** |
| 真实分离输出 | 0.254476 / 3.929639倍 | 0.214304 / 4.666262倍 |
| 旧copy+apply | 0.481664 / 2.076136倍 | 0.744982 / 1.342315倍 |
| 准备+首组分离输出 | 0.603949 | 0.798798 |

纯apply进程比1线程为`[0.362047,0.326896,0.299886,0.321422]`，4线程为`[0.484452,0.404787,0.445160,0.392332]`。同库A/A中位B/A为1.024342/1.006215，四对范围分别1.017585—1.039637、0.962263—1.014867，均满足冻结控制。全部批次输出、输入/保护区、实际团队/TID绑定、前后16MiB精确VMA及全THP通过。唯一失败门槛是四线程纯apply中位大于1/3；按冻结规则跳过唯一确认，新增确认系列及原生调用0，不重跑择优或采用默认。该轮不是79对78的同场直接配对，不能用跨场数值证明成对加载独立提速或退化。

[档案与复算](../../report/data/skylake-pair48-v1/README.md)保存124份原件及清单，从1920轮原始数组独立复算比值/中位/A/A/判定通过。Windows11/Anaconda Python3.13.12标准库只读交付辅助入口首次因默认GBK读取UTF-8失败，随后归档因决定文件尚未生成而停止，二者发生于任何复制前；记录缺口后显式UTF-8生成决定，未改或重测原生结果。独立对象审计的实际解释器另见其回执，不混作Linux验证。

两个额外方向仅做轻量历史/静态评估，未实现或跑性能：三次u64精确24B加四ID组合未找到直接重复，但79现有尾部需约28条输入提取指令/8像素，成对宽读为16条，仅少一次load却多跨词依赖，暂止；旧8MiB三位格式加四ID标量palette也未直接测过，42为向量解码/gather且62为五位格式，不能拿旧失败直接否证。但其普通路径多约8—12条/像素的标量解码量级、异常额外依赖及字节序转换未消除，尚无补足四线程缺口的依据。旧6.43%是全域异常块率，21.42%是照片八像素包至少一异常的比例，均不能冒充本方案新像素异常率。

实际Skylake、无BMI1硬件、官方派生表许可/预算/Threshold仍未验证；未锁频控温或证明宿主独占。精度证明只对冻结模型，不是新拟合精度改善，整体三倍目标未完成。

交付前124份清单/71项源码及构建/全域/静态身份、145份暂存实验/脚本/档案blob与原字节核对通过；Python语法通过。unified diff原件的空上下文行含协议前缀空格，仅对该冻结`.patch`设置空白规则，不改其原字节；随后空白检查通过。创建前fetch GitHub，完整读取66份PR正文与前65份比较仅新增72，其余一致；72完整意见刷新为空，最终updated检索无新PR/issue。issue7修复及main b19c5a0/337a3dd/876e15b8/397cc367均包含；issue8接口/预算/实板待办继续跟踪。Discussion无法读取的缺口保留，不合并或关闭事项。

复现需恢复PR71固定模型、大流和独立oracle流并核对SHA，使用新目录：

```sh
python3 scripts/build_skylake_runtime.py --plan experiments/skylake-pair48-v1.json --output artifacts/skylake-pair48-linux-build-v1
python3 -P artifacts/skylake-pair48-static-v1/inspect-v2.py
python3 scripts/verify_skylake_pair48_linux.py --plan experiments/skylake-pair48-v1.json --build artifacts/skylake-pair48-linux-build-v1 --single-oracle-stream artifacts/skylake-domain-isolated-full-v1/first-stage.rgb --output artifacts/skylake-pair48-linux-full-v1 --affinity-cpus 0,2,4,6
python3 artifacts/skylake-pair48-preflight-v1/prepare-performance.py
python3 scripts/bench_skylake_pair48_long_linux.py --policy experiments/skylake-pair48-long-perf-v1.json --output artifacts/skylake-pair48-long-perf-v1
```
