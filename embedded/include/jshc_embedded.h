/* 无堆分配的 RGB8/Q16 运行时；可用于 C99、C++ 和 RTOS。 */
#ifndef JSHC_EMBEDDED_H
#define JSHC_EMBEDDED_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    JSHC_EMBEDDED_OK = 0,
    JSHC_EMBEDDED_ARGUMENT = 1,
    JSHC_EMBEDDED_FORMAT = 2
} jshc_embedded_status;

/* 借用只读 .slut v1 字节，不复制节点。仅由 init 填充，不得手工修改字段。
 * 模型字节须在所有调用期间保持有效且不变；无需对齐，无浮点元数据转换。
 * 同一模型可由多任务共享；各任务须使用互不重叠的 RGB 缓冲区。 */
typedef struct {
    uint32_t m;
    const uint8_t *idx;
    const uint8_t *frac;
    const uint8_t *nodes;
} jshc_embedded_lut;

/* 严格核验长度、头部、索引和 Q16 分数；失败时使 out 失效。
 * 网格 f32 元数据与桌面运行时一样不参与映射，idx/frac 才是实际权重。
 * out 不得与输入模型字节重叠。 */
jshc_embedded_status jshc_embedded_init(jshc_embedded_lut *out,
                                     const void *data, size_t bytes);

/* 原地映射 0..4 级，每级独立执行 (sum + 32768) / 65536 取整。
 * 0 级为恒等映射；0 像素允许 rgb=NULL。参数错误不修改 RGB。
 * chain 及其视图不得与可写 RGB 区域重叠；RGB 不得覆盖任何模型字节。
 * 调用者负责缓冲区容量；函数不访问环境变量、文件系统或 RTOS API。
 * 除固定大小的局部变量外无工作区，不分配内存，无全局可变状态。 */
jshc_embedded_status jshc_embedded_apply(const jshc_embedded_lut *const *chain,
                                      size_t stages, uint8_t *rgb, size_t pixels);

#ifdef __cplusplus
}
#endif
#endif
