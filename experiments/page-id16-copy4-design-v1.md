# P4 C99四字节原样复制：独立单版静态假设

状态：仅静态预案。589f9d1的P4唯一质量和双阶段正式原件保持；本文件没有新构建、导出、质量或速度。执行仍须root明确授窗。

## 现有机器码证据

本地既有P4的`artifacts/p16-page-id16-runtime-v1/build/page_core.o`由Clang21.1.0、严格C99、generic x64无AVX/BMI目标生成，SHA`4c6b215a054708a6803628bbfa9ea419a262b9447a18ddec658be53b45260216`。`objdump -d -Mintel`显示`jshc_p4_apply`每8像素主组中第一palette项0x53f为WORD读、0x544为BYTE读，随后shl16/or；其它前7项相同。它未把`color[0..2]`和常量0合为一个DWORD读。末项0x6de/6e3是1B+2B，只需末3B写。

旧合格linear C99的`experiments/memory-rom/memory_rom_store.c`则在emit8中对前7项直接memcpy4，末项memcpy3。既有`artifacts/p16-memory-clang-store-build-v1/clang-store-assembly.txt`的0x329/332/33c/346/350/35a/364均为单DWORD palette load加DWORD组内重叠写，末项仍是BYTE+WORD。这是同编译器已有机器码能力证据，尚不能证明新P4一定会得到相同优化或提高到50%。

## 唯一代码变更与边界

另建独立C99 apply入口，不编辑已冻结page_id16.c、头、ROM或DLL。保持8输入code先全部读入、8项colors全部求值、前7次memcpy4/最后memcpy3、短尾3B写和相同IO验证；唯一替换为`memcpy(colors[lane], color, 4)`，取代逐3B读并写第4B为0。保持原Clang版本、generic x64参数和旧prepare/validate/AVX对象；不添加restrict、预取、循环展开、ISA或第二种格式。

格式中每项palette实际完整占4B；prepare已逐项验证高字节0，即使ID255最后合法项也有完整4B可读，不依赖guard或外部padding。复制的是[R,G,B,0]原字节，大小端与非对齐均不依赖host uint32解释。Model和ROM不可变生命周期合同不放宽，用户src/dst尾部仍不得多读写1B。同址安全仍由先读完整8输入、再执行组内重叠写保证。

假设H是前7项palette字节组装的额外读/移位/合并没有被原Clang消除；新源码可能让其变为单DWORD读。减少指令和读操作不保证减少页ID→pool→palette依赖总延迟，也不保证本机C99从37.65%提高到50%；现有C99负例不能删除或改判。

## 预定门与停止条件

1. 实施前另冻结新执行源、旧P4/linear/78/80对象和输入SHA。只编译这一个源版本，无优化参数扫描；若新前7项仍逐RGB组装，则按机制未实现停止，不开始吞吐。
2. 质量必须明确调用新符号及新OMP适配器中的C99分支，记录实际地址/库/对象SHA，不能误测仍在DLL里的旧入口。沿原独立u64、完整域、100逐图、全256palette/最后map与pool/非对齐/短尾及src/dst/ROM guard、IO与格式拒绝完整覆盖；首次失败保存STOP，不修后重采原阶段。
3. 质量通过才另冻结正式性能。预定同场至少fast78/80、原linear C99、旧P4 C99、新P4 C99；主分母仍同phase最快78/80，旧P4仅辅助比值。四fresh0x55、两phase各5次、全角色镜像顺序，外围ref80及全部角色自身两阶段[.8,1.25]门保持；任何cell控制失效所有角色清档，全部phase/worker取最劣，不合并样本救线。
4. 新C99必须四模式均有效且最劣≥50才进入50以上档；若有效低50，保存本单版负例并停止该替换，不扩变体或WASM。失效模式不以raw低值冒充有效反例，也不补跑恢复。AVX原53.8961%不替新C99授档。

没有新的导出、census、输入分区或ROM变更，真实capacity仍12,633,164B；这是已有表示下的C99依赖末端实现研究，不声称进一步压缩。实际栈、新DLL大小及fresh进程开销需新阶段实测，不能沿用136B旧帧作新实现结论。
