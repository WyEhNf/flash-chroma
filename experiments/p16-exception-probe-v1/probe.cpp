// 只观察本进程首次访问异常的寄存器，不吞掉异常、不修改运行时或线程上下文。
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstring>

struct ProbeRecord {
  uint32_t version,seen;
  uint64_t code,rip,rsp,rbp,address,rax,rbx,rcx,rdx,rsi,rdi,r8,r9,r10,r11,r12,r13,r14,r15;
};
static_assert(sizeof(ProbeRecord)==160,"异常观察ABI须为160B");
namespace {
ProbeRecord record{};
volatile LONG recorded=0;
void* cookie=nullptr;
LONG CALLBACK observe(EXCEPTION_POINTERS* info) {
  if(info->ExceptionRecord->ExceptionCode!=EXCEPTION_ACCESS_VIOLATION)return EXCEPTION_CONTINUE_SEARCH;
  if(InterlockedCompareExchange(&recorded,1,0)!=0)return EXCEPTION_CONTINUE_SEARCH;
  const auto& c=*info->ContextRecord;
  record={1,1,info->ExceptionRecord->ExceptionCode,c.Rip,c.Rsp,c.Rbp,
    info->ExceptionRecord->NumberParameters>=2?info->ExceptionRecord->ExceptionInformation[1]:0,
    c.Rax,c.Rbx,c.Rcx,c.Rdx,c.Rsi,c.Rdi,c.R8,c.R9,c.R10,c.R11,c.R12,c.R13,c.R14,c.R15};
  return EXCEPTION_CONTINUE_SEARCH;
}
}
extern "C" {
__declspec(dllexport) int p16_probe_install() {
  if(cookie)return 1;
  record={};InterlockedExchange(&recorded,0);cookie=AddVectoredExceptionHandler(1,observe);return cookie?0:2;
}
__declspec(dllexport) int p16_probe_clear() {
  if(!cookie)return 1;
  record={};InterlockedExchange(&recorded,0);return 0;
}
__declspec(dllexport) int p16_probe_read(ProbeRecord* out,size_t bytes) {
  if(!out || bytes!=sizeof(ProbeRecord))return 1;
  std::memcpy(out,&record,sizeof(record));return 0;
}
__declspec(dllexport) int p16_probe_uninstall() {
  if(!cookie)return 0;
  if(!RemoveVectoredExceptionHandler(cookie))return 1;
  cookie=nullptr;return 0;
}
}
