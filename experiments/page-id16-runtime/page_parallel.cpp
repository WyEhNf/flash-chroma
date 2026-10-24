/* OMP只是可选桌面适配层，纯C99对象不依赖它。 */
#include "page_id16_internal.h"
#include <algorithm>
#if defined(_OPENMP)
#include <omp.h>
#endif
int jshc_p4_apply_parallel(const jshc_p4_model *model, const unsigned char *source,
                           unsigned char *target, size_t pixels, int kernel,
                           int threads) {
    if ((kernel != 0 && kernel != 1) || threads < 1 || threads > 256 ||
        (kernel == 1 && !__builtin_cpu_supports("avx2")) ||
        jshc_p4_validate_io(model, source, target, pixels)) return 1;
    const size_t blocks = pixels / 65536 + (pixels % 65536 != 0);
    if (!blocks) return 0;
#if defined(_OPENMP)
    const int workers = omp_in_parallel() ? 1 : int(std::min(blocks, size_t(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
    for (long long block = 0; block < static_cast<long long>(blocks); ++block) {
        const size_t start = size_t(block) * 65536;
        const size_t count = std::min(size_t(65536), pixels - start);
        if (kernel == 1) jshc_p4_avx2_unchecked(model, source + 3 * start,
                                               target + 3 * start, count);
        else jshc_p4_apply(model, source + 3 * start, target + 3 * start, count);
    }
    return 0;
}
