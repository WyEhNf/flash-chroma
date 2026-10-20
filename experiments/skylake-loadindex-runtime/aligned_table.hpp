#pragma once
#include <cstdlib>
#include <cstdint>
#include <cstddef>
#include <new>
#if defined(__linux__)
#include <sys/mman.h>
#elif defined(_WIN32)
#include <malloc.h>
#endif
namespace jshc_channel {
// 只建议本对象拥有的完整2MiB对齐区域，不调整任何系统设置或权限。
class AlignedTable {
  uint32_t* data_=nullptr;
  size_t words_=0;
  int advice_=-1;
public:
  AlignedTable()=default;
  AlignedTable(const AlignedTable&)=delete;
  AlignedTable& operator=(const AlignedTable&)=delete;
  ~AlignedTable() {
#if defined(_WIN32)
    _aligned_free(data_);
#else
    std::free(data_);
#endif
  }
  void allocate(size_t words) {
    if(data_)throw std::bad_alloc();
    const size_t bytes=words*sizeof(uint32_t);
#if defined(_WIN32)
    data_=static_cast<uint32_t*>(_aligned_malloc(bytes,size_t{2}<<20));
    if(!data_)throw std::bad_alloc();
#else
    void* pointer=nullptr;
    if(posix_memalign(&pointer,size_t{2}<<20,bytes)!=0)throw std::bad_alloc();
    data_=static_cast<uint32_t*>(pointer);
#endif
    words_=words;
#if defined(__linux__)
    advice_=madvise(data_,bytes,MADV_HUGEPAGE);
#endif
  }
  uint32_t* data() noexcept {return data_;}
  const uint32_t* data() const noexcept {return data_;}
  size_t size() const noexcept {return words_;}
  size_t bytes() const noexcept {return words_*sizeof(uint32_t);}
  bool empty() const noexcept {return !data_;}
  int advice() const noexcept {return advice_;}
};
}
