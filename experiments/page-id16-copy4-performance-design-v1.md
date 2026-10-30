# P4 copy4独立正式草案：同表示、同编译器、新C99入口

本文是计时前预注册内容；实际冻结与执行状态另存receipt，不能由本文预先授档。9f6b8f22质量源、ROM、40B ABI、core/AVX原对象和已构建copy4 DLL均不再改。

固定五角色依次为ref78、ref80、linear_c99、p4_c99、p4_copy4，四fresh进程按worker编号轮转/奇数反转第一阶段角色顺序，第二阶段严格反转完整role顺序；全部模型驻留，使用同src/dst地址。线程与输出模式镜像顺序沿P4 v2，0x55允许集和逐调用CPU/地址/整数ns/完整百图输出SHA不变。

每cell外围ref80预热1+before2，phase1与phase2的每个五角色分别预热1+timed5，末尾ref80 after2。固定65/cell、260/worker、四worker1040调用，其中800 timed，另五fresh RSS。不得缩轮或新增候选/补跑。每个role自己的phase2五次中位数/phase1五次中位数和外围ref80 after/before均须在闭区间[0.8,1.25]；任一失败则该cell全部role清档，任一worker失效则整个模式全部role不授档。

主分母固定同worker、同phase较快78/80五次中位数，模式最终取全部四worker×两phase的最劣比值，独立Decimal100/90/80/70/60/50判定。新copy4相对旧P4和linear C99的同phase配对只辅助解释此修改，不替代主分母，不合并十样本救线。只有新C99四模式均有效且最劣≥50才给全局50以上档；任何有效低50作为负例保留，控制失效不当有效反例或补跑理由。

只计新apply_copy4_parallel的kernel0，不能误走旧apply或AVX。新旧P4同时借同ROM，旧P4仍使用其原DLL。原linear C99为同场较快的便携源码控制，既有AVX全局50不替新C99背书。精度单列100%，依据新符号完整质量，并非原模型相对数学参考误差为0。

计时前以原只读module observer辅助函数，在每个worker准备前、全部role准备后和模型close后记录实际四GCC依赖模块路径/SHA/数量；每个RSS自身也采实际同进程模块，不从前次单fresh外推。实际模块必须属于本次冻结磁盘输入且每种一份，否则身份STOP。观察/完整输出SHA在计时外，snapshot包含其Python元数据成本；不改变库、环境或加载顺序来追结果。

五fresh RSS无图片，记录同imports/身份预检/实际模块观察条件下准备前/后/关闭后的WS、PrivateUsage和进程峰。capacity仍P4的12,633,164B，不把WS、提交、静态栈混作纯模型或物理RAM收益。新C99质量的120B静态帧不是四线程总栈。

正式冻结必须先绑定25源/23输入质量原件、独立audit、新主DLL/独立C99 DLL、原fast/linear/P4和全部五目录依赖、照片身份和新计时所有源；root明确独占grant后才运行。首次身份/native/输出错误STOP，AA失效照固定余下原轮完整保存。无WASM/新编译/参数扫描；计时结果不能修改机制、门限或样本。
