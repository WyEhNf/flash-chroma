# 独立512bank/7bit本地palette：消费既有频数的静态实现方案

Agent：`/root/memory`；Operator：当前16题用户；Status：Proposed，仅静态立项。没有新census、ROM导出、C99/AVX源码实现、构建、质量或性能。待root明确grant才实施单版；本文件不改先前512bank/6bit的54失败/最大95结论，也不改默认。

## 已有证明与固定选择

依据已提交`5dbd1858d6a55c9445ab0ad3e38ec014ded17237`的完整512×230频数：固定`bank=(R>>5)|((G>>5)<<3)|((B>>5)<<6)`全部bank最多95个RGB。6bit容量64不足，故原协议失败。对于相同key的**统一位宽**，`64<95<=128`直接证明最少7bit；这是消费已封存证据，不是重扫完整模型/照片或在旧6bit协议改门槛。

原普查计划SHA17a12d05…，频数支持SHA`6d51134d1abbb8e6bfde3e9d16d4ad65566a085d3f2ecf5afef680511232403a`，包含原件的ZIP SHA`63366451b76ffcf2d4039b7358b038758f530282f93561793a8076cd11fab0e7`。新export将先校这些身份，只用其正频数globalID集合，逐bank按**原globalID数值升序**编号。RGB本身不变、不按照片或频率重排，不扫描位宽/排序/局部分区/例外路径。

原230合法palette与实际221命中色仍区分；新格式是完整可验证的本地codebook，不再以230作为运行时限制，可合法使用每bank全部128槽。a399实际最多95只是当前模型证据，不能把格式硬写死95。

## 固定格式、ABI与真实账本计划

`C7BK v1`：header32B、512项LE16 count共1024B、原R低/G中/B高code顺序的7bit直表14680064B、4B自有零guard、512×128 LE RGB32 palette共262144B。总ROM投影 **14943268B**；不可变借用model四字段（blob、size_t bytes、table、palettes），Windows x64预期 **32B**，常驻投影 **14943300B**。没有原global palette副本或被漏算的本地palette副本；这些均未实测。

table起点1056，guard起点14681120，palette起点14681124，最后palette词结束于ROM末端14943268。每bank count1..128、有效RGB<=ffffff，unused槽清零；prepare核所有header/长度/guard/count/palette及**全部16M所属bank的ID<count**，不能仅检查7bit天然<128。borrow生命周期、失败清零、out/ROM重叠无写拒绝、IO部分重叠/指针和size溢出等沿原严格契约，独立32B ABI不能传旧1056B ctypes对象。

相对旧线性ROM实际16779328B，此布局投影省1836028B；这个差值不是已经实现的收益。离线映射预计需要512×256的128KiB临时global→local表、palette/count、分块打包数组与约14.9MiB输出；导出、prepare栈、核心scratch、loader和fresh进程RSS都单列，ZIP不当RAM。

## 单版C99和AVX2路径

核心查找：`bit=7*code; local=(LE16(table+(bit>>3))>>(bit&7))&127; index=128*bank+local; RGB=LE32(palettes+4*index)`。bank由输入位段计算，可与bitstream读取并行，但仍增加索引/移位和256KiB palette工作集；两层读取不代表缓存命中或必然过50。

C99采用此前已有合格证据的8像素store结构：先读取全部8×3B输入，算出8个bank/local palette索引，然后前7像素`memcpy4`、最后像素`memcpy3`，短尾逐像素完整读3B后写3B。palette源是序列化LE字节，不用裸uint32 store，保证同址安全、无外部padding/对齐或端序要求。不会在尚未读完当前8输入时覆盖后续输入。

唯一C99编译器选此前已验证的Clang21 generic x64：`--target=x86_64-w64-windows-gnu --sysroot=E:/mingw64 -std=c99 -pedantic-errors -O3 -march=x86-64 -mtune=generic -mno-avx -mno-avx2 -mno-avx512f`，另核对象无AVX/BMI。GCC15.2仅链接桌面OMP适配器及AVX TU，不在此阶段重新扫描GCC/Clang或调优C99算法。纯C99 DLL单独保留，不依赖OMP/AVX；桌面C99四线程需可选OMP包装。

AVX2只改精确lookup为最终RGB，沿用已验3B/M16T的输入读取、64像素先读后写、NTA/NT/SFENCE、OMP65536粒度、输出和尾部。helper使用byte pointers与`memcpy2/memcpy4`，不将未对齐ROM强转并解引用uint32指针；palette不再假定是model内对齐数组。仅独立TU `-mavx2 -mtune=skylake -ffp-contract=off`，dispatcher不泄漏ISA，无native/AVX512或新增BMI。不会把旧M16T/3B好场用作新速度分母。

## 实际质量必须先行

7bit的byte内起始位置是**0..7共8种**。最后code=ffffff从最后byte bit1起，占到bit7；LE16需要明确guard的一字节，4B零guard计入文件。真实ROM尾NOACCESS检验最后palette词；源/目标双保护页另覆盖输入和短尾边界，不能用“有guard”放宽图像读写。

正向count128夹具固定localID=`(R&31)|((G&3)<<5)`，使每bank实际覆盖0..127，ffffff命中bank511/local127/最后palette词；再有count1全ID0。覆盖全部512bank、各轴31/32等边界、0/255、7bit全部8种起点、最大RGBffffff、非对齐、零长、同址/分离、部分重叠、ROM/model目标重叠、非法count0/129/ffff、RGB高字节、unused palette、guard、截断、key/保留位和某bank越count等拒绝。生命周期和不可变借用同样验证。

导出后按实际序列化字节独立重建全RGB，不调用候选helper自证；纯C99、desktop scalar、AVX1/4各原地/分离8完整256³及100图输出SHA，绑定原a3993c9c…/f3c0…，精度100%指继承原误差，不是相对原滤镜零误差。任何质量失败停止性能、保留原件；真实ABI、文件长度、栈、RSS未验证前不宣称实际容量或可移植成绩。

## 同场四模式与六档，等另授性能窗

六角色：fast78/80、旧线性8bit AVX（原ANDN）、旧线性8bit Clang C99、新3D7 AVX、新3D7 C99。两个旧线性角色使用Clang store既有同DLL的kernel1/0及原8bit ROM，保留其1056B ABI，容量16779328B；新角色为独立32B ABI。实际旧DLL绝对路径、SHA/实际载入模块和所有依赖在新freeze中核定，不按同名库猜身份。

四新worker全部process允许集0/2/4/6（0x55），OMP_PROC_BIND=false且无OMP_PLACES，记录实际mask与native wall外caller前后CPU；不逐OMP线程绑定或锁频，不作旧unbound因果解释。每worker六角色×双接口×1/4线程，轮转/反序，预热1+5完整百图，共480正式+96预热+80AA=656次native调用，另6个同import群独立进程RSS；原始秒数、全SHA、worker和无效场全留，不补跑。

速度仅用同worker较快78/80耗时除以候选，取四worker最劣；旧线性仅作配对，不作慢分母。精度和速度100/90/80/70/60/50两轴独立；A/A逐对0.8..1.25且中位1/1.1..1.1，失败对应全部档位清空。任何有效模式<50则拒绝整体，保留其它有明确条件的模式结果；不能取平均、中位、历史最好或通过质量覆盖速度失败。无额外确认/编译器/bit/loop参数扫描；后续新假设必须另立协议。

当前仅凭既有频数证明7bit可表示，源码实现/导出/构建/完整质量和正式性能均须root明确grant。此前6bit失败、其它字典有效失败、官方研究派生表许可及真实目标实板限制保持。
