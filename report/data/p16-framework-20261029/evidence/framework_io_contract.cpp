#include "framework_io.hpp"
#include <iostream>
#include <functional>
using namespace fc_framework_io;
int main(){unsigned n=0;auto rejected=[&](auto f){try{f();return false;}catch(const std::exception&){++n;return true;}};
 std::vector<uint8_t> text{'#','x','\n','0',' ','4','0','9','5',' ','4','0','9','6','\n','6','5','5','3','5',' ','1','6',' ','+','3','2','\n'};
 write_rgb_file_new("values.3dl",text);std::vector<uint16_t> v;read_3dl("values.3dl",v,6);
 if(v!=std::vector<uint16_t>{0,4095,4096,65535,16,32})return 1;++n;
 write_u16_cache_new("values.u16le",v);std::vector<uint16_t>w;read_u16_cache("values.u16le",w,6);if(w!=v)return 2;++n;
 if(!rejected([&]{write_u16_cache_new("values.u16le",v);}))return 3;
 if(!rejected([&]{read_3dl("values.3dl",w,3);}))return 4;
 if(!rejected([&]{read_3dl("values.3dl",w,9);}))return 5;
 for(const auto& bad:{"-1 0 0\n","65536 0 0\n","1 2\n","1 2 3 4\n","1x 2 3\n"}){std::string p="bad-"+std::to_string(n)+".3dl";std::string s(bad);write_rgb_file_new(p,{s.begin(),s.end()});if(!rejected([&]{read_3dl(p,w,3);}))return 6;}
 std::cout<<"{\"passed\":true,\"cases\":"<<n<<",\"scope\":\"small parser/cache contract; no image benchmark\"}\n";return 0;}
