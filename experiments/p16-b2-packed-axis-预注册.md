# 修订99：唯一packed-axis B2符号与有限合同

只执行一次纯整数合同，不构建原生库，不读取gold/照片/16M输出，不与原idx算式同时择优。以修订98的ordinary af974首级和既有17/25夹具为固定输入；旧模型、轴、域证明和95/97证据不改。

原Q16四项重心权为`F-high, high-middle, middle-low, low`，F=65536。某坐标等于F时，原cell该轴为0的角权为0；换到下一cell的0面，所有非零权所在逻辑节点不变。多个端点逐轴应用。并列只改变零权项。物理不等距grid已包含于原idx/frac，不重新量化。以仿射系数（常数与最多三个内部变量）按logical node合并核等式，不能仅比较几个代入颜色值。

三个坐标至多三个不同内部值，代表集0/1/2/3/F穷举并按符号变量重命名去重，完整覆盖严格序、任意并列、单/多端点。每个cell的六个合法old排列都核对；new first/last精确重述现有四次比较tie语义，不假设它们总不同。对全部32³cell逐项比较old/new logical-node系数，不用哈希指纹代替等式。

新布局固定B=2/T=17，private axis低16存正规化fraction，高16存该轴tilebase贡献。原768项全部逐值解码；原idx必须0..31、frac0..F，F变为idx+1/0。r/g/b contribution分别为`floor(idx/2)*8*T*T+4*(idx%2)`、`floor(idx/2)*8*T+2*(idx%2)`、`floor(idx/2)*8+(idx%2)`；三轴先分别提取高16再相加，禁止低位fraction加法进位。动态stride分别是`4+parity*(8*T*T-8)`、`2+parity*(8*T-4)`、`1+6*parity`。

padded34³表的全部39304地址做双射、反解、实际uint32节点clamp身份核对。正规化后idx32的未用+1角坐标33必须填clamp32节点，零权加载也必须合法。所有cell/符号模式的新四角都核实际物理索引、独立坐标增量、clamp后系数和实际word。表不是98的未用sentinel填充版本；原98结果保留。

资格纯参考合同仅当m33/shared/domain-proven/direct-empty/compiled-empty全成立；48种组合和真实17/25夹具拒绝，不冒称原生分派已验证。坏轴idx负/32、frac负/65537、非整数、坏形状必须拒绝。实际不等距grid用IEEE32原bits解成精确有理数核验，只解释输入，不生成新idx/frac。

额外axis3072B+node逻辑157216B，node最小64对齐roundup157248B，最低新增payload160320B；原轴/packed必须保留，实际owner/allocator/RSS/prepare尚待实现另核。通过后只报告合同SHA和计数，再申请唯一runtime实现；本合同不给任何速度档，不替代native全域/尾部/canary/拒绝/回退/并发资格。
