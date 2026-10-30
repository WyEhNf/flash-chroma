/* 单版仅改变主组palette读取；旧P4核心与短尾不编辑。 */
#include "page_copy4.h"
#include "../page-id16-runtime/page_id16_internal.h"
#include <string.h>
int jshc_p4_apply_copy4(const jshc_p4_model *m, const unsigned char *source,
                      unsigned char *target, size_t pixels) {
    size_t i = 0, lane;
    if (jshc_p4_validate_io(m, source, target, pixels)) return 1;
    while (pixels - i >= 8) {
        uint32_t codes[8];
        unsigned char colors[8][4];
        /* 先读完整组输入；之后前7次4B写只能覆盖组内下一像素。 */
        for (lane = 0; lane < 8; ++lane) {
            const unsigned char *s = source + 3 * (i + lane);
            codes[lane] = (uint32_t)s[0] | ((uint32_t)s[1] << 8) |
                          ((uint32_t)s[2] << 16);
        }
        for (lane = 0; lane < 8; ++lane) {
            const unsigned char *color = p4_rgb(m, codes[lane]);
            /* prepare已验证每项完整4B且第4B为0；原字节复制无端序假设。 */
            memcpy(colors[lane], color, 4);
        }
        for (lane = 0; lane < 7; ++lane)
            memcpy(target + 3 * (i + lane), colors[lane], 4);
        memcpy(target + 3 * (i + 7), colors[7], 3);
        i += 8;
    }
    for (; i < pixels; ++i) {
        const unsigned char *s = source + 3 * i;
        uint32_t code = (uint32_t)s[0] | ((uint32_t)s[1] << 8) |
                        ((uint32_t)s[2] << 16);
        const unsigned char *color = p4_rgb(m, code);
        target[3 * i] = color[0];
        target[3 * i + 1] = color[1];
        target[3 * i + 2] = color[2];
    }
    return 0;
}
