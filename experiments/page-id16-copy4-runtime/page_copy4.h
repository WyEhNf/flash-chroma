/* 独立C99四字节复制入口；沿用原P4借用ABI和prepare合同。 */
#ifndef JSHC_P4_COPY4_H
#define JSHC_P4_COPY4_H
#include "../page-id16-runtime/page_id16.h"
#ifdef __cplusplus
extern "C" {
#endif
P4_API int jshc_p4_apply_copy4(const jshc_p4_model *model,
                             const unsigned char *source,
                             unsigned char *target, size_t pixels);
P4_API int jshc_p4_apply_copy4_parallel(const jshc_p4_model *model,
                                      const unsigned char *source,
                                      unsigned char *target, size_t pixels,
                                      int kernel, int threads);
#ifdef __cplusplus
}
#endif
#endif
