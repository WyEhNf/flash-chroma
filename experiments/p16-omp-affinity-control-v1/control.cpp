// 独立基准控制helper；只改变当前测试进程的OpenMP team，不改变模型。
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0601
#endif
#include <windows.h>
#include <omp.h>
#include <cstdint>
#include <cstddef>
#include <cstring>

struct P16AffinityRecord {
  uint32_t version,omp_tid,team_size,os_tid,cpu_before,cpu_after;
  uint32_t group_before,group_after,query_before_ok,set_attempted,set_error,query_after_ok;
  uint64_t mask_before,previous_mask,mask_after;
};
static_assert(sizeof(P16AffinityRecord)==72,"线程诊断ABI固定72B");

extern "C" __declspec(dllexport)
int p16_omp_affinity(P16AffinityRecord* output,size_t entries,size_t stride,
                     uint32_t action,const P16AffinityRecord* saved) noexcept {
  // action0只读，1固定，2恢复；参数拒绝不写调用者缓冲。
  if(!output || entries!=4 || stride!=sizeof(P16AffinityRecord) || action>2 || (action==2 && !saved))return 1;
  DWORD_PTR process_mask=0,system_mask=0;
  if(!GetProcessAffinityMask(GetCurrentProcess(),&process_mask,&system_mask) || process_mask!=0x55 || GetActiveProcessorGroupCount()!=1)return 2;
  P16AffinityRecord previous[4]{};
  if(action==2)std::memcpy(previous,saved,sizeof(previous));
  std::memset(output,0,4*sizeof(P16AffinityRecord));
  int failures=0;
#pragma omp parallel num_threads(4) reduction(+:failures)
  {
    const unsigned t=unsigned(omp_get_thread_num());
    const unsigned n=unsigned(omp_get_num_threads());
    P16AffinityRecord row{};row.version=1;row.omp_tid=t;row.team_size=n;
    row.os_tid=GetCurrentThreadId();row.cpu_before=GetCurrentProcessorNumber();
    GROUP_AFFINITY before{},after{};
    row.query_before_ok=GetThreadGroupAffinity(GetCurrentThread(),&before)!=0;
    row.group_before=before.Group;row.mask_before=before.Mask;
    bool legal=n==4 && t<4 && row.query_before_ok && before.Group==0;
    if(action==2)legal=legal && previous[t].version==1 && previous[t].omp_tid==t &&
        previous[t].os_tid==row.os_tid && previous[t].previous_mask &&
        !(previous[t].previous_mask & ~uint64_t(process_mask));
    if(legal && action) {
      row.set_attempted=1;
      const DWORD_PTR desired=action==1?(DWORD_PTR{1}<<(2*t)):DWORD_PTR(previous[t].previous_mask);
      row.previous_mask=SetThreadAffinityMask(GetCurrentThread(),desired);
      if(!row.previous_mask)row.set_error=GetLastError();
      legal=row.previous_mask!=0;
    }
    row.query_after_ok=GetThreadGroupAffinity(GetCurrentThread(),&after)!=0;
    row.group_after=after.Group;row.mask_after=after.Mask;row.cpu_after=GetCurrentProcessorNumber();
    legal=legal && row.query_after_ok && after.Group==0;
    if(legal && action==1)legal=after.Mask==(DWORD_PTR{1}<<(2*t)) && row.cpu_after==2*t;
    if(legal && action==2)legal=after.Mask==previous[t].previous_mask;
    failures+=!legal;
    if(t<4)output[t]=row;
  }
  return failures?3:0;
}
