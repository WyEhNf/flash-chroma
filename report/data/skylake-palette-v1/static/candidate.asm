
artifacts\skylake-palette-build-v1\CMakeFiles\jshc_skylake_palette.dir\channel_avx2.cpp.obj:     file format pe-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)>:
   0:	56                   	push   %rsi
   1:	53                   	push   %rbx
   2:	48 81 ec c8 01 00 00 	sub    $0x1c8,%rsp
   9:	c5 f8 29 b4 24 20 01 	vmovaps %xmm6,0x120(%rsp)
  10:	00 00 
  12:	c5 f8 29 bc 24 30 01 	vmovaps %xmm7,0x130(%rsp)
  19:	00 00 
  1b:	c5 78 29 84 24 40 01 	vmovaps %xmm8,0x140(%rsp)
  22:	00 00 
  24:	c5 78 29 8c 24 50 01 	vmovaps %xmm9,0x150(%rsp)
  2b:	00 00 
  2d:	c5 78 29 94 24 60 01 	vmovaps %xmm10,0x160(%rsp)
  34:	00 00 
  36:	c5 78 29 9c 24 70 01 	vmovaps %xmm11,0x170(%rsp)
  3d:	00 00 
  3f:	c5 78 29 a4 24 80 01 	vmovaps %xmm12,0x180(%rsp)
  46:	00 00 
  48:	c5 78 29 ac 24 90 01 	vmovaps %xmm13,0x190(%rsp)
  4f:	00 00 
  51:	c5 78 29 b4 24 a0 01 	vmovaps %xmm14,0x1a0(%rsp)
  58:	00 00 
  5a:	c5 78 29 bc 24 b0 01 	vmovaps %xmm15,0x1b0(%rsp)
  61:	00 00 
  63:	49 89 d2             	mov    %rdx,%r10
  66:	48 8b 94 24 08 02 00 	mov    0x208(%rsp),%rdx
  6d:	00 
  6e:	4c 89 c3             	mov    %r8,%rbx
  71:	4c 89 ce             	mov    %r9,%rsi
  74:	48 85 d2             	test   %rdx,%rdx
  77:	0f 84 d6 05 00 00    	je     653 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x653>
  7d:	48 ff ca             	dec    %rdx
  80:	48 8b 84 24 00 02 00 	mov    0x200(%rsp),%rax
  87:	00 
  88:	c4 41 0d 76 f6       	vpcmpeqd %ymm14,%ymm14,%ymm14
  8d:	48 c1 ea 03          	shr    $0x3,%rdx
  91:	c4 c1 4d 72 d6 18    	vpsrld $0x18,%ymm14,%ymm6
  97:	48 8d 14 52          	lea    (%rdx,%rdx,2),%rdx
  9b:	4c 8d 4c d0 18       	lea    0x18(%rax,%rdx,8),%r9
  a0:	ba 08 00 00 00       	mov    $0x8,%edx
  a5:	c5 f9 6e fa          	vmovd  %edx,%xmm7
  a9:	ba 00 80 00 00       	mov    $0x8000,%edx
  ae:	c4 e2 7d 58 ff       	vpbroadcastd %xmm7,%ymm7
  b3:	c5 fe 7f bc 24 00 01 	vmovdqu %ymm7,0x100(%rsp)
  ba:	00 00 
  bc:	c5 f9 6e fa          	vmovd  %edx,%xmm7
  c0:	c4 e2 7d 58 ff       	vpbroadcastd %xmm7,%ymm7
  c5:	c5 fe 7f bc 24 a0 00 	vmovdqu %ymm7,0xa0(%rsp)
  cc:	00 00 
  ce:	e9 01 05 00 00       	jmp    5d4 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x5d4>
  d3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  d8:	c4 e2 7d 00 05 20 00 	vpshufb 0x20(%rip),%ymm0,%ymm0        # 101 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x101>
  df:	00 00 
  e1:	48 8b 11             	mov    (%rcx),%rdx
  e4:	c5 7d 7f f3          	vmovdqa %ymm14,%ymm3
  e8:	44 8b 59 50          	mov    0x50(%rcx),%r11d
  ec:	c5 fd db ee          	vpand  %ymm6,%ymm0,%ymm5
  f0:	c5 f5 72 d0 08       	vpsrld $0x8,%ymm0,%ymm1
  f5:	44 8b 41 54          	mov    0x54(%rcx),%r8d
  f9:	c4 41 7d 6f de       	vmovdqa %ymm14,%ymm11
  fe:	c5 fe 7f 2c 24       	vmovdqu %ymm5,(%rsp)
 103:	c5 c5 72 d0 10       	vpsrld $0x10,%ymm0,%ymm7
 108:	c5 f5 db d6          	vpand  %ymm6,%ymm1,%ymm2
 10c:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 110:	c4 e2 65 90 04 aa    	vpgatherdd %ymm3,(%rdx,%ymm5,4),%ymm0
 116:	48 8b 51 08          	mov    0x8(%rcx),%rdx
 11a:	c5 fe 7f 54 24 20    	vmovdqu %ymm2,0x20(%rsp)
 120:	c4 41 79 6e c0       	vmovd  %r8d,%xmm8
 125:	c4 42 7d 58 c0       	vpbroadcastd %xmm8,%ymm8
 12a:	c5 dd 72 d0 11       	vpsrld $0x11,%ymm0,%ymm4
 12f:	47 8d 44 18 01       	lea    0x1(%r8,%r11,1),%r8d
 134:	c4 e2 75 90 2c 92    	vpgatherdd %ymm1,(%rdx,%ymm2,4),%ymm5
 13a:	48 8b 51 10          	mov    0x10(%rcx),%rdx
 13e:	c5 fe 7f bc 24 80 00 	vmovdqu %ymm7,0x80(%rsp)
 145:	00 00 
 147:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 14b:	c4 c1 79 6e d3       	vmovd  %r11d,%xmm2
 150:	c5 fd db 05 a0 00 00 	vpand  0xa0(%rip),%ymm0,%ymm0        # 1f8 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x1f8>
 157:	00 
 158:	c4 41 7d 6f d6       	vmovdqa %ymm14,%ymm10
 15d:	c4 e2 75 90 1c ba    	vpgatherdd %ymm1,(%rdx,%ymm7,4),%ymm3
 163:	c5 f5 72 d5 11       	vpsrld $0x11,%ymm5,%ymm1
 168:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
 16d:	48 8b 51 48          	mov    0x48(%rcx),%rdx
 171:	c4 e2 5d 40 e2       	vpmulld %ymm2,%ymm4,%ymm4
 176:	c4 c2 75 40 c8       	vpmulld %ymm8,%ymm1,%ymm1
 17b:	c5 d5 db 2d a0 00 00 	vpand  0xa0(%rip),%ymm5,%ymm5        # 223 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x223>
 182:	00 
 183:	c5 c5 72 d3 11       	vpsrld $0x11,%ymm3,%ymm7
 188:	c5 e5 db 1d a0 00 00 	vpand  0xa0(%rip),%ymm3,%ymm3        # 230 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x230>
 18f:	00 
 190:	c4 62 7d 39 cd       	vpminsd %ymm5,%ymm0,%ymm9
 195:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
 199:	c5 75 fe ef          	vpaddd %ymm7,%ymm1,%ymm13
 19d:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 1a1:	c4 e2 7d 3d fd       	vpmaxsd %ymm5,%ymm0,%ymm7
 1a6:	c4 22 75 90 24 aa    	vpgatherdd %ymm1,(%rdx,%ymm13,4),%ymm12
 1ac:	c5 e5 66 e7          	vpcmpgtd %ymm7,%ymm3,%ymm4
 1b0:	c4 c1 79 6e c8       	vmovd  %r8d,%xmm1
 1b5:	c4 e2 7d 58 c9       	vpbroadcastd %xmm1,%ymm1
 1ba:	c4 e2 45 3d fb       	vpmaxsd %ymm3,%ymm7,%ymm7
 1bf:	c4 41 75 fe fd       	vpaddd %ymm13,%ymm1,%ymm15
 1c4:	c4 a2 25 90 0c ba    	vpgatherdd %ymm11,(%rdx,%ymm15,4),%ymm1
 1ca:	c4 62 35 39 db       	vpminsd %ymm3,%ymm9,%ymm11
 1cf:	c5 fe 7f 4c 24 60    	vmovdqu %ymm1,0x60(%rsp)
 1d5:	c5 d5 66 c8          	vpcmpgtd %ymm0,%ymm5,%ymm1
 1d9:	c5 35 66 cb          	vpcmpgtd %ymm3,%ymm9,%ymm9
 1dd:	c4 c3 6d 4c c8 10    	vpblendvb %ymm1,%ymm8,%ymm2,%ymm1
 1e3:	c4 e3 75 4c 0d 3f 00 	vpblendvb %ymm4,0x3f(%rip),%ymm1,%ymm1        # 22c <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x22c>
 1ea:	00 00 40 
 1ed:	c5 95 fe c9          	vpaddd %ymm1,%ymm13,%ymm1
 1f1:	c4 e2 2d 90 24 8a    	vpgatherdd %ymm10,(%rdx,%ymm1,4),%ymm4
 1f7:	c5 fd 66 cd          	vpcmpgtd %ymm5,%ymm0,%ymm1
 1fb:	c4 41 7d 6f d6       	vmovdqa %ymm14,%ymm10
 200:	c5 dd db e6          	vpand  %ymm6,%ymm4,%ymm4
 204:	c5 fd fe c5          	vpaddd %ymm5,%ymm0,%ymm0
 208:	c4 c3 6d 4c c8 10    	vpblendvb %ymm1,%ymm8,%ymm2,%ymm1
 20e:	c4 e3 75 4c 0d 3f 00 	vpblendvb %ymm9,0x3f(%rip),%ymm1,%ymm1        # 257 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x257>
 215:	00 00 90 
 218:	c5 85 fa c9          	vpsubd %ymm1,%ymm15,%ymm1
 21c:	c4 62 2d 90 0c 8a    	vpgatherdd %ymm10,(%rdx,%ymm1,4),%ymm9
 222:	c5 7e 7f 64 24 40    	vmovdqu %ymm12,0x40(%rsp)
 228:	c4 41 45 fe e3       	vpaddd %ymm11,%ymm7,%ymm12
 22d:	c5 4d db 54 24 40    	vpand  0x40(%rsp),%ymm6,%ymm10
 233:	c5 35 db ce          	vpand  %ymm6,%ymm9,%ymm9
 237:	c4 c1 65 fa dc       	vpsubd %ymm12,%ymm3,%ymm3
 23c:	c5 e5 fe c0          	vpaddd %ymm0,%ymm3,%ymm0
 240:	c5 b5 fa dc          	vpsubd %ymm4,%ymm9,%ymm3
 244:	c4 41 7d 6f e6       	vmovdqa %ymm14,%ymm12
 249:	c4 c1 75 72 f2 10    	vpslld $0x10,%ymm10,%ymm1
 24f:	c4 e2 7d 40 db       	vpmulld %ymm3,%ymm0,%ymm3
 254:	c4 c1 5d fa e2       	vpsubd %ymm10,%ymm4,%ymm4
 259:	c5 f5 fe 8c 24 a0 00 	vpaddd 0xa0(%rsp),%ymm1,%ymm1
 260:	00 00 
 262:	c5 cd db 44 24 60    	vpand  0x60(%rsp),%ymm6,%ymm0
 268:	c4 41 7d 6f d6       	vmovdqa %ymm14,%ymm10
 26d:	c4 e2 5d 40 e7       	vpmulld %ymm7,%ymm4,%ymm4
 272:	4c 8b 41 28          	mov    0x28(%rcx),%r8
 276:	c5 fe 6f ac 24 80 00 	vmovdqu 0x80(%rsp),%ymm5
 27d:	00 00 
 27f:	c4 c1 7d fa c1       	vpsubd %ymm9,%ymm0,%ymm0
 284:	c4 c2 7d 40 c3       	vpmulld %ymm11,%ymm0,%ymm0
 289:	c4 41 7d 6f de       	vmovdqa %ymm14,%ymm11
 28e:	c5 e5 fe c9          	vpaddd %ymm1,%ymm3,%ymm1
 292:	c5 fe 6f 5c 24 20    	vmovdqu 0x20(%rsp),%ymm3
 298:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
 29c:	c5 fe 6f 24 24       	vmovdqu (%rsp),%ymm4
 2a1:	c5 f5 fe c8          	vpaddd %ymm0,%ymm1,%ymm1
 2a5:	c5 c5 72 d1 10       	vpsrld $0x10,%ymm1,%ymm7
 2aa:	c5 fe 7f bc 24 e0 00 	vmovdqu %ymm7,0xe0(%rsp)
 2b1:	00 00 
 2b3:	c4 c2 25 90 3c a8    	vpgatherdd %ymm11,(%r8,%ymm5,4),%ymm7
 2b9:	4c 8b 41 20          	mov    0x20(%rcx),%r8
 2bd:	c4 41 7d 6f de       	vmovdqa %ymm14,%ymm11
 2c2:	c5 c5 db 3d a0 00 00 	vpand  0xa0(%rip),%ymm7,%ymm7        # 36a <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x36a>
 2c9:	00 
 2ca:	c4 42 25 90 0c 98    	vpgatherdd %ymm11,(%r8,%ymm3,4),%ymm9
 2d0:	4c 8b 41 18          	mov    0x18(%rcx),%r8
 2d4:	c5 35 db 0d a0 00 00 	vpand  0xa0(%rip),%ymm9,%ymm9        # 37c <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x37c>
 2db:	00 
 2dc:	c4 c2 2d 90 1c a0    	vpgatherdd %ymm10,(%r8,%ymm4,4),%ymm3
 2e2:	c4 41 7d 6f d6       	vmovdqa %ymm14,%ymm10
 2e7:	4c 8b 41 40          	mov    0x40(%rcx),%r8
 2eb:	c5 e5 db 1d a0 00 00 	vpand  0xa0(%rip),%ymm3,%ymm3        # 393 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x393>
 2f2:	00 
 2f3:	c4 42 65 3d d9       	vpmaxsd %ymm9,%ymm3,%ymm11
 2f8:	c5 b5 66 c3          	vpcmpgtd %ymm3,%ymm9,%ymm0
 2fc:	c4 c2 65 39 e9       	vpminsd %ymm9,%ymm3,%ymm5
 301:	c4 c1 45 66 e3       	vpcmpgtd %ymm11,%ymm7,%ymm4
 306:	c4 e2 55 39 cf       	vpminsd %ymm7,%ymm5,%ymm1
 30b:	c4 62 25 3d df       	vpmaxsd %ymm7,%ymm11,%ymm11
 310:	c5 d5 66 ef          	vpcmpgtd %ymm7,%ymm5,%ymm5
 314:	c4 c3 6d 4c c0 00    	vpblendvb %ymm0,%ymm8,%ymm2,%ymm0
 31a:	c4 e3 7d 4c 05 3f 00 	vpblendvb %ymm4,0x3f(%rip),%ymm0,%ymm0        # 363 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x363>
 321:	00 00 40 
 324:	c5 95 fe c0          	vpaddd %ymm0,%ymm13,%ymm0
 328:	c4 e2 2d 90 24 82    	vpgatherdd %ymm10,(%rdx,%ymm0,4),%ymm4
 32e:	c4 c1 65 66 c1       	vpcmpgtd %ymm9,%ymm3,%ymm0
 333:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
 338:	c5 dd 72 d4 08       	vpsrld $0x8,%ymm4,%ymm4
 33d:	c5 dd db e6          	vpand  %ymm6,%ymm4,%ymm4
 341:	c4 c3 6d 4c c0 00    	vpblendvb %ymm0,%ymm8,%ymm2,%ymm0
 347:	c4 e3 7d 4c 05 3f 00 	vpblendvb %ymm5,0x3f(%rip),%ymm0,%ymm0        # 390 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x390>
 34e:	00 00 50 
 351:	c5 85 fa c0          	vpsubd %ymm0,%ymm15,%ymm0
 355:	c4 62 1d 90 14 82    	vpgatherdd %ymm12,(%rdx,%ymm0,4),%ymm10
 35b:	c5 fe 6f 44 24 40    	vmovdqu 0x40(%rsp),%ymm0
 361:	c5 fe 7f 8c 24 c0 00 	vmovdqu %ymm1,0xc0(%rsp)
 368:	00 00 
 36a:	c5 a5 fe c9          	vpaddd %ymm1,%ymm11,%ymm1
 36e:	c4 c1 2d 72 d2 08    	vpsrld $0x8,%ymm10,%ymm10
 374:	c5 c5 fa f9          	vpsubd %ymm1,%ymm7,%ymm7
 378:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 37c:	c5 9d 72 d0 08       	vpsrld $0x8,%ymm0,%ymm12
 381:	c5 2d db d6          	vpand  %ymm6,%ymm10,%ymm10
 385:	c5 c5 fe db          	vpaddd %ymm3,%ymm7,%ymm3
 389:	c5 fe 6f 44 24 60    	vmovdqu 0x60(%rsp),%ymm0
 38f:	c5 1d db e6          	vpand  %ymm6,%ymm12,%ymm12
 393:	c5 ad fa fc          	vpsubd %ymm4,%ymm10,%ymm7
 397:	c4 e2 65 40 ff       	vpmulld %ymm7,%ymm3,%ymm7
 39c:	c5 d5 72 d0 08       	vpsrld $0x8,%ymm0,%ymm5
 3a1:	c4 c1 5d fa e4       	vpsubd %ymm12,%ymm4,%ymm4
 3a6:	c4 c2 5d 40 e3       	vpmulld %ymm11,%ymm4,%ymm4
 3ab:	c4 c1 7d 72 f4 10    	vpslld $0x10,%ymm12,%ymm0
 3b1:	c5 d5 db ee          	vpand  %ymm6,%ymm5,%ymm5
 3b5:	c5 fd fe 84 24 a0 00 	vpaddd 0xa0(%rsp),%ymm0,%ymm0
 3bc:	00 00 
 3be:	c4 c1 55 fa ea       	vpsubd %ymm10,%ymm5,%ymm5
 3c3:	c4 e2 55 40 ac 24 c0 	vpmulld 0xc0(%rsp),%ymm5,%ymm5
 3ca:	00 00 00 
 3cd:	c5 c5 fe c0          	vpaddd %ymm0,%ymm7,%ymm0
 3d1:	c5 d5 fe ec          	vpaddd %ymm4,%ymm5,%ymm5
 3d5:	c5 fd fe c5          	vpaddd %ymm5,%ymm0,%ymm0
 3d9:	c5 fe 6f ac 24 80 00 	vmovdqu 0x80(%rsp),%ymm5
 3e0:	00 00 
 3e2:	c5 fd 72 d0 10       	vpsrld $0x10,%ymm0,%ymm0
 3e7:	c4 c2 75 90 1c a8    	vpgatherdd %ymm1,(%r8,%ymm5,4),%ymm3
 3ed:	4c 8b 41 38          	mov    0x38(%rcx),%r8
 3f1:	c5 7e 6f 64 24 20    	vmovdqu 0x20(%rsp),%ymm12
 3f7:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 3fb:	c5 fe 6f 24 24       	vmovdqu (%rsp),%ymm4
 400:	c5 e5 db 1d a0 00 00 	vpand  0xa0(%rip),%ymm3,%ymm3        # 4a8 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x4a8>
 407:	00 
 408:	c4 82 75 90 3c a0    	vpgatherdd %ymm1,(%r8,%ymm12,4),%ymm7
 40e:	4c 8b 41 30          	mov    0x30(%rcx),%r8
 412:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 416:	45 8b 5a 20          	mov    0x20(%r10),%r11d
 41a:	c5 c5 db 3d a0 00 00 	vpand  0xa0(%rip),%ymm7,%ymm7        # 4c2 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x4c2>
 421:	00 
 422:	c4 c2 75 90 2c a0    	vpgatherdd %ymm1,(%r8,%ymm4,4),%ymm5
 428:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 42c:	c5 d5 db 2d a0 00 00 	vpand  0xa0(%rip),%ymm5,%ymm5        # 4d4 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x4d4>
 433:	00 
 434:	c4 62 55 3d d7       	vpmaxsd %ymm7,%ymm5,%ymm10
 439:	c5 45 66 cd          	vpcmpgtd %ymm5,%ymm7,%ymm9
 43d:	c4 62 55 39 df       	vpminsd %ymm7,%ymm5,%ymm11
 442:	c4 c1 65 66 e2       	vpcmpgtd %ymm10,%ymm3,%ymm4
 447:	c4 62 25 39 e3       	vpminsd %ymm3,%ymm11,%ymm12
 44c:	c4 62 2d 3d d3       	vpmaxsd %ymm3,%ymm10,%ymm10
 451:	c5 25 66 db          	vpcmpgtd %ymm3,%ymm11,%ymm11
 455:	c4 43 6d 4c c8 90    	vpblendvb %ymm9,%ymm8,%ymm2,%ymm9
 45b:	c4 63 35 4c 0d 3f 00 	vpblendvb %ymm4,0x3f(%rip),%ymm9,%ymm9        # 4a4 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x4a4>
 462:	00 00 40 
 465:	c4 41 15 fe c9       	vpaddd %ymm9,%ymm13,%ymm9
 46a:	c4 41 2d fe ec       	vpaddd %ymm12,%ymm10,%ymm13
 46f:	c4 a2 75 90 24 8a    	vpgatherdd %ymm1,(%rdx,%ymm9,4),%ymm4
 475:	c5 55 66 cf          	vpcmpgtd %ymm7,%ymm5,%ymm9
 479:	c5 7d 7f f1          	vmovdqa %ymm14,%ymm1
 47d:	c5 dd 72 d4 10       	vpsrld $0x10,%ymm4,%ymm4
 482:	c5 d5 fe ef          	vpaddd %ymm7,%ymm5,%ymm5
 486:	c4 c1 65 fa dd       	vpsubd %ymm13,%ymm3,%ymm3
 48b:	c5 fe 6f bc 24 e0 00 	vmovdqu 0xe0(%rsp),%ymm7
 492:	00 00 
 494:	c5 dd db e6          	vpand  %ymm6,%ymm4,%ymm4
 498:	c5 e5 fe dd          	vpaddd %ymm5,%ymm3,%ymm3
 49c:	c4 c3 6d 4c d0 90    	vpblendvb %ymm9,%ymm8,%ymm2,%ymm2
 4a2:	c4 e3 6d 4c 15 3f 00 	vpblendvb %ymm11,0x3f(%rip),%ymm2,%ymm2        # 4eb <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x4eb>
 4a9:	00 00 b0 
 4ac:	c5 85 fa d2          	vpsubd %ymm2,%ymm15,%ymm2
 4b0:	c4 62 75 90 0c 92    	vpgatherdd %ymm1,(%rdx,%ymm2,4),%ymm9
 4b6:	c5 fe 6f 54 24 40    	vmovdqu 0x40(%rsp),%ymm2
 4bc:	41 8b 52 24          	mov    0x24(%r10),%edx
 4c0:	c4 c1 35 72 d1 10    	vpsrld $0x10,%ymm9,%ymm9
 4c6:	c5 bd 72 d2 10       	vpsrld $0x10,%ymm2,%ymm8
 4cb:	c5 fe 6f 54 24 60    	vmovdqu 0x60(%rsp),%ymm2
 4d1:	44 0f af da          	imul   %edx,%r11d
 4d5:	c5 35 db ce          	vpand  %ymm6,%ymm9,%ymm9
 4d9:	c5 3d db c6          	vpand  %ymm6,%ymm8,%ymm8
 4dd:	c5 b5 fa ec          	vpsubd %ymm4,%ymm9,%ymm5
 4e1:	c5 ed 72 d2 10       	vpsrld $0x10,%ymm2,%ymm2
 4e6:	c4 e2 65 40 dd       	vpmulld %ymm5,%ymm3,%ymm3
 4eb:	c4 c1 5d fa e0       	vpsubd %ymm8,%ymm4,%ymm4
 4f0:	c4 c2 5d 40 e2       	vpmulld %ymm10,%ymm4,%ymm4
 4f5:	c4 c1 25 72 f0 10    	vpslld $0x10,%ymm8,%ymm11
 4fb:	c5 ed db d6          	vpand  %ymm6,%ymm2,%ymm2
 4ff:	c4 c1 6d fa d1       	vpsubd %ymm9,%ymm2,%ymm2
 504:	c5 25 fe 9c 24 a0 00 	vpaddd 0xa0(%rsp),%ymm11,%ymm11
 50b:	00 00 
 50d:	c4 c2 6d 40 d4       	vpmulld %ymm12,%ymm2,%ymm2
 512:	c4 c1 65 fe db       	vpaddd %ymm11,%ymm3,%ymm3
 517:	c5 ed fe d4          	vpaddd %ymm4,%ymm2,%ymm2
 51b:	c5 e5 fe da          	vpaddd %ymm2,%ymm3,%ymm3
 51f:	c4 c2 7d 58 52 10    	vpbroadcastd 0x10(%r10),%ymm2
 525:	c5 e5 72 d3 10       	vpsrld $0x10,%ymm3,%ymm3
 52a:	c5 fd fa c2          	vpsubd %ymm2,%ymm0,%ymm0
 52e:	c5 f9 6e d2          	vmovd  %edx,%xmm2
 532:	49 8b 12             	mov    (%r10),%rdx
 535:	c5 fd fa c7          	vpsubd %ymm7,%ymm0,%ymm0
 539:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
 53e:	c4 e2 7d 40 c2       	vpmulld %ymm2,%ymm0,%ymm0
 543:	c4 c2 7d 58 52 18    	vpbroadcastd 0x18(%r10),%ymm2
 549:	c5 e5 fa da          	vpsubd %ymm2,%ymm3,%ymm3
 54d:	c4 c2 7d 58 52 08    	vpbroadcastd 0x8(%r10),%ymm2
 553:	c5 c5 fa d2          	vpsubd %ymm2,%ymm7,%ymm2
 557:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
 55b:	c4 c1 79 6e db       	vmovd  %r11d,%xmm3
 560:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
 565:	c4 e2 6d 40 d3       	vpmulld %ymm3,%ymm2,%ymm2
 56a:	c5 ed fa cf          	vpsubd %ymm7,%ymm2,%ymm1
 56e:	c5 7d 7f f7          	vmovdqa %ymm14,%ymm7
 572:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 576:	c4 e2 45 90 0c 82    	vpgatherdd %ymm7,(%rdx,%ymm0,4),%ymm1
 57c:	c5 ed 72 d1 08       	vpsrld $0x8,%ymm1,%ymm2
 581:	c5 fd 72 d1 10       	vpsrld $0x10,%ymm1,%ymm0
 586:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
 58a:	c5 ed db d6          	vpand  %ymm6,%ymm2,%ymm2
 58e:	c5 fd 72 f0 10       	vpslld $0x10,%ymm0,%ymm0
 593:	c5 ed 72 f2 08       	vpslld $0x8,%ymm2,%ymm2
 598:	c5 fd eb c2          	vpor   %ymm2,%ymm0,%ymm0
 59c:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
 5a0:	c4 e2 7d 00 05 60 00 	vpshufb 0x60(%rip),%ymm0,%ymm0        # 609 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x609>
 5a7:	00 00 
 5a9:	48 83 c0 18          	add    $0x18,%rax
 5ad:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
 5b1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 5b7:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 5bc:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 5c1:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
 5c5:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 5ca:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 5cf:	4c 39 c8             	cmp    %r9,%rax
 5d2:	74 7c                	je     650 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x650>
 5d4:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 5d8:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
 5dd:	c5 7d 7f f7          	vmovdqa %ymm14,%ymm7
 5e1:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
 5e7:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 5ed:	c4 e2 7d 00 0d 00 00 	vpshufb 0x0(%rip),%ymm0,%ymm1        # 5f6 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x5f6>
 5f4:	00 00 
 5f6:	c5 e5 72 d1 03       	vpsrld $0x3,%ymm1,%ymm3
 5fb:	c4 e2 45 90 14 9b    	vpgatherdd %ymm7,(%rbx,%ymm3,4),%ymm2
 601:	c5 ed db de          	vpand  %ymm6,%ymm2,%ymm3
 605:	c5 e5 76 e6          	vpcmpeqd %ymm6,%ymm3,%ymm4
 609:	c5 fd d7 d4          	vpmovmskb %ymm4,%edx
 60d:	85 d2                	test   %edx,%edx
 60f:	0f 85 c3 fa ff ff    	jne    d8 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0xd8>
 615:	c5 f5 db 0d 80 00 00 	vpand  0x80(%rip),%ymm1,%ymm1        # 69d <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x69d>
 61c:	00 
 61d:	c5 7d 7f f5          	vmovdqa %ymm14,%ymm5
 621:	c5 fd 72 f1 01       	vpslld $0x1,%ymm1,%ymm0
 626:	c5 f5 fe 8c 24 00 01 	vpaddd 0x100(%rsp),%ymm1,%ymm1
 62d:	00 00 
 62f:	c5 f5 fe c8          	vpaddd %ymm0,%ymm1,%ymm1
 633:	c4 e2 6d 45 d1       	vpsrlvd %ymm1,%ymm2,%ymm2
 638:	c5 ed db 15 80 00 00 	vpand  0x80(%rip),%ymm2,%ymm2        # 6c0 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x6c0>
 63f:	00 
 640:	c5 ed fe d3          	vpaddd %ymm3,%ymm2,%ymm2
 644:	c4 e2 55 90 04 96    	vpgatherdd %ymm5,(%rsi,%ymm2,4),%ymm0
 64a:	e9 51 ff ff ff       	jmp    5a0 <jshc_channel::avx2_chain_palette(jshc_channel::View const*, jshc_channel::SuffixCacheView const&, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x5a0>
 64f:	90                   	nop
 650:	c5 f8 77             	vzeroupper
 653:	c5 f8 28 b4 24 20 01 	vmovaps 0x120(%rsp),%xmm6
 65a:	00 00 
 65c:	c5 f8 28 bc 24 30 01 	vmovaps 0x130(%rsp),%xmm7
 663:	00 00 
 665:	c5 78 28 84 24 40 01 	vmovaps 0x140(%rsp),%xmm8
 66c:	00 00 
 66e:	c5 78 28 8c 24 50 01 	vmovaps 0x150(%rsp),%xmm9
 675:	00 00 
 677:	c5 78 28 94 24 60 01 	vmovaps 0x160(%rsp),%xmm10
 67e:	00 00 
 680:	c5 78 28 9c 24 70 01 	vmovaps 0x170(%rsp),%xmm11
 687:	00 00 
 689:	c5 78 28 a4 24 80 01 	vmovaps 0x180(%rsp),%xmm12
 690:	00 00 
 692:	c5 78 28 ac 24 90 01 	vmovaps 0x190(%rsp),%xmm13
 699:	00 00 
 69b:	c5 78 28 b4 24 a0 01 	vmovaps 0x1a0(%rsp),%xmm14
 6a2:	00 00 
 6a4:	c5 78 28 bc 24 b0 01 	vmovaps 0x1b0(%rsp),%xmm15
 6ab:	00 00 
 6ad:	48 81 c4 c8 01 00 00 	add    $0x1c8,%rsp
 6b4:	5b                   	pop    %rbx
 6b5:	5e                   	pop    %rsi
 6b6:	c3                   	ret
 6b7:	90                   	nop
 6b8:	90                   	nop
 6b9:	90                   	nop
 6ba:	90                   	nop
 6bb:	90                   	nop
 6bc:	90                   	nop
 6bd:	90                   	nop
 6be:	90                   	nop
 6bf:	90                   	nop
