/* 可选OMP只调新纯C99核；不链接旧AVX对象作为新视图路径。 */
#include "page_native_pages.h"
#include <algorithm>
#if defined(_OPENMP)
#include <omp.h>
#endif
int jshc_p4_pages_apply_parallel(const jshc_p4_pages_view *view,
                                 const unsigned char *source,
                                 unsigned char *target, size_t pixels,
                                 int threads) {
    if (threads < 1 || threads > 256 ||
        jshc_p4_pages_validate_io(view, source, target, pixels)) return 1;
    const size_t blocks = pixels / 65536 + (pixels % 65536 != 0);
    if (!blocks) return 0;
#if defined(_OPENMP)
    const int workers = omp_in_parallel() ? 1 : int(std::min(blocks, size_t(threads)));
#pragma omp parallel for schedule(static) num_threads(workers)
#endif
    for (long long block = 0; block < static_cast<long long>(blocks); ++block) {
        const size_t start = size_t(block) * 65536;
        const size_t count = std::min(size_t(65536), pixels - start);
        jshc_p4_pages_apply(view, source + 3 * start, target + 3 * start, count);
    }
    return 0;
}
