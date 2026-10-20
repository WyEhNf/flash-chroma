
artifacts/skylake-tileindex-linux-build-v1/CMakeFiles/jshc_skylake_tileindex.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	55                   	push   %rbp
   5:	48 89 e5             	mov    %rsp,%rbp
   8:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
   c:	48 83 f9 1f          	cmp    $0x1f,%rcx
  10:	0f 86 b2 04 00 00    	jbe    4c8 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x4c8>
  16:	41 ba 00 00 fc 00    	mov    $0xfc0000,%r10d
  1c:	4c 8d 41 e0          	lea    -0x20(%rcx),%r8
  20:	c5 7d 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm8        # 28 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x28>
  27:	00 
  28:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 30 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
  2f:	00 
  30:	c4 41 79 6e e2       	vmovd  %r10d,%xmm12
  35:	41 ba fc 00 00 00    	mov    $0xfc,%r10d
  3b:	4d 89 c1             	mov    %r8,%r9
  3e:	48 89 d0             	mov    %rdx,%rax
  41:	c4 41 79 6e da       	vmovd  %r10d,%xmm11
  46:	41 ba 00 00 03 00    	mov    $0x30000,%r10d
  4c:	49 c1 e9 05          	shr    $0x5,%r9
  50:	c4 42 7d 58 e4       	vpbroadcastd %xmm12,%ymm12
  55:	c4 41 79 6e d2       	vmovd  %r10d,%xmm10
  5a:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
  5e:	c4 42 7d 58 db       	vpbroadcastd %xmm11,%ymm11
  63:	41 ba 00 03 00 00    	mov    $0x300,%r10d
  69:	c4 41 79 6e ca       	vmovd  %r10d,%xmm9
  6e:	41 ba 00 fc 00 00    	mov    $0xfc00,%r10d
  74:	49 c1 e1 05          	shl    $0x5,%r9
  78:	c4 42 7d 58 d2       	vpbroadcastd %xmm10,%ymm10
  7d:	c4 c1 79 6e d2       	vmovd  %r10d,%xmm2
  82:	4e 8d 4c 0a 60       	lea    0x60(%rdx,%r9,1),%r9
  87:	c4 42 7d 58 c9       	vpbroadcastd %xmm9,%ymm9
  8c:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
  91:	c5 fd 7f 54 24 e0    	vmovdqa %ymm2,-0x20(%rsp)
  97:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  9e:	00 00 
  a0:	c5 fa 6f 20          	vmovdqu (%rax),%xmm4
  a4:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
  a9:	48 83 c0 60          	add    $0x60,%rax
  ad:	c5 fa 6f 58 b8       	vmovdqu -0x48(%rax),%xmm3
  b2:	c5 fa 6f 48 d0       	vmovdqu -0x30(%rax),%xmm1
  b7:	c4 e3 79 0f c4 0c    	vpalignr $0xc,%xmm4,%xmm0,%xmm0
  bd:	c5 fa 7e 68 f8       	vmovq  -0x8(%rax),%xmm5
  c2:	c4 e3 5d 38 e0 01    	vinserti128 $0x1,%xmm0,%ymm4,%ymm4
  c8:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
  cd:	c4 c2 5d 00 e0       	vpshufb %ymm8,%ymm4,%ymm4
  d2:	c4 e3 79 0f c3 0c    	vpalignr $0xc,%xmm3,%xmm0,%xmm0
  d8:	c5 35 db f4          	vpand  %ymm4,%ymm9,%ymm14
  dc:	c5 1d db ec          	vpand  %ymm4,%ymm12,%ymm13
  e0:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
  e6:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
  eb:	c4 c1 0d 72 d6 08    	vpsrld $0x8,%ymm14,%ymm14
  f1:	c5 a5 db f4          	vpand  %ymm4,%ymm11,%ymm6
  f5:	c4 c1 15 72 d5 02    	vpsrld $0x2,%ymm13,%ymm13
  fb:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 100:	c4 c2 65 00 d8       	vpshufb %ymm8,%ymm3,%ymm3
 105:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
 10b:	c4 c1 4d eb f5       	vpor   %ymm13,%ymm6,%ymm6
 110:	c4 41 15 76 ed       	vpcmpeqd %ymm13,%ymm13,%ymm13
 115:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
 11b:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
 120:	c4 c2 75 00 c8       	vpshufb %ymm8,%ymm1,%ymm1
 125:	c4 e3 51 0f e8 0c    	vpalignr $0xc,%xmm0,%xmm5,%xmm5
 12b:	c5 35 db f9          	vpand  %ymm1,%ymm9,%ymm15
 12f:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
 135:	c4 c1 05 72 d7 08    	vpsrld $0x8,%ymm15,%ymm15
 13b:	c5 ad db ec          	vpand  %ymm4,%ymm10,%ymm5
 13f:	c5 d5 72 d5 0e       	vpsrld $0xe,%ymm5,%ymm5
 144:	c4 c2 7d 00 c0       	vpshufb %ymm8,%ymm0,%ymm0
 149:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 14e:	c5 5d db 74 24 e0    	vpand  -0x20(%rsp),%ymm4,%ymm14
 154:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 159:	c5 35 db f3          	vpand  %ymm3,%ymm9,%ymm14
 15d:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 161:	c4 c1 0d 72 d6 08    	vpsrld $0x8,%ymm14,%ymm14
 167:	c4 e2 15 90 34 af    	vpgatherdd %ymm13,(%rdi,%ymm5,4),%ymm6
 16d:	c5 dd db 2d 00 00 00 	vpand  0x0(%rip),%ymm4,%ymm5        # 175 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x175>
 174:	00 
 175:	c5 1d db eb          	vpand  %ymm3,%ymm12,%ymm13
 179:	c4 c1 15 72 d5 02    	vpsrld $0x2,%ymm13,%ymm13
 17f:	c5 d5 72 f5 03       	vpslld $0x3,%ymm5,%ymm5
 184:	c4 e2 4d 45 e5       	vpsrlvd %ymm5,%ymm6,%ymm4
 189:	c5 ad db eb          	vpand  %ymm3,%ymm10,%ymm5
 18d:	c5 a5 db f3          	vpand  %ymm3,%ymm11,%ymm6
 191:	c5 d5 72 d5 0e       	vpsrld $0xe,%ymm5,%ymm5
 196:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 19b:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 1a0:	c5 65 db 74 24 e0    	vpand  -0x20(%rsp),%ymm3,%ymm14
 1a6:	c4 c1 4d eb f5       	vpor   %ymm13,%ymm6,%ymm6
 1ab:	c5 e5 db 1d 00 00 00 	vpand  0x0(%rip),%ymm3,%ymm3        # 1b3 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1b3>
 1b2:	00 
 1b3:	c4 41 15 76 ed       	vpcmpeqd %ymm13,%ymm13,%ymm13
 1b8:	c5 dd db 25 00 00 00 	vpand  0x0(%rip),%ymm4,%ymm4        # 1c0 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1c0>
 1bf:	00 
 1c0:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 1c5:	c5 1d db f1          	vpand  %ymm1,%ymm12,%ymm14
 1c9:	c5 e5 72 f3 03       	vpslld $0x3,%ymm3,%ymm3
 1ce:	c4 c1 0d 72 d6 02    	vpsrld $0x2,%ymm14,%ymm14
 1d4:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 1d8:	c4 e2 15 90 34 af    	vpgatherdd %ymm13,(%rdi,%ymm5,4),%ymm6
 1de:	c5 2d db e9          	vpand  %ymm1,%ymm10,%ymm13
 1e2:	c5 f5 db 6c 24 e0    	vpand  -0x20(%rsp),%ymm1,%ymm5
 1e8:	c4 e2 4d 45 db       	vpsrlvd %ymm3,%ymm6,%ymm3
 1ed:	c4 c1 15 72 d5 0e    	vpsrld $0xe,%ymm13,%ymm13
 1f3:	c5 a5 db f1          	vpand  %ymm1,%ymm11,%ymm6
 1f7:	c4 41 15 eb ef       	vpor   %ymm15,%ymm13,%ymm13
 1fc:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 201:	c5 f5 db 0d 00 00 00 	vpand  0x0(%rip),%ymm1,%ymm1        # 209 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x209>
 208:	00 
 209:	c4 c1 4d eb f6       	vpor   %ymm14,%ymm6,%ymm6
 20e:	c4 c1 55 eb ed       	vpor   %ymm13,%ymm5,%ymm5
 213:	c4 41 0d 76 f6       	vpcmpeqd %ymm14,%ymm14,%ymm14
 218:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 21c:	c5 2d db e8          	vpand  %ymm0,%ymm10,%ymm13
 220:	c5 35 db f8          	vpand  %ymm0,%ymm9,%ymm15
 224:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 229:	c4 c1 05 72 d7 08    	vpsrld $0x8,%ymm15,%ymm15
 22f:	c4 e2 0d 90 34 af    	vpgatherdd %ymm14,(%rdi,%ymm5,4),%ymm6
 235:	c4 e2 4d 45 c9       	vpsrlvd %ymm1,%ymm6,%ymm1
 23a:	c5 fd db 6c 24 e0    	vpand  -0x20(%rsp),%ymm0,%ymm5
 240:	c5 1d db f0          	vpand  %ymm0,%ymm12,%ymm14
 244:	c4 c1 15 72 d5 0e    	vpsrld $0xe,%ymm13,%ymm13
 24a:	c4 c1 0d 72 d6 02    	vpsrld $0x2,%ymm14,%ymm14
 250:	c5 a5 db f0          	vpand  %ymm0,%ymm11,%ymm6
 254:	c4 41 15 eb ef       	vpor   %ymm15,%ymm13,%ymm13
 259:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 25e:	c5 fd db 05 00 00 00 	vpand  0x0(%rip),%ymm0,%ymm0        # 266 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x266>
 265:	00 
 266:	c4 c1 4d eb f6       	vpor   %ymm14,%ymm6,%ymm6
 26b:	c4 c1 55 eb ed       	vpor   %ymm13,%ymm5,%ymm5
 270:	c4 41 05 76 ff       	vpcmpeqd %ymm15,%ymm15,%ymm15
 275:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 279:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 27e:	c4 e2 05 90 34 af    	vpgatherdd %ymm15,(%rdi,%ymm5,4),%ymm6
 284:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 288:	c4 e2 4d 45 c0       	vpsrlvd %ymm0,%ymm6,%ymm0
 28d:	c4 e2 55 90 34 a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm6
 293:	c5 e5 db 25 00 00 00 	vpand  0x0(%rip),%ymm3,%ymm4        # 29b <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x29b>
 29a:	00 
 29b:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 29f:	c4 e2 4d 00 f7       	vpshufb %ymm7,%ymm6,%ymm6
 2a4:	c4 e2 55 90 1c a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm3
 2aa:	c5 f5 db 25 00 00 00 	vpand  0x0(%rip),%ymm1,%ymm4        # 2b2 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2b2>
 2b1:	00 
 2b2:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 2b6:	c4 e2 65 00 df       	vpshufb %ymm7,%ymm3,%ymm3
 2bb:	c4 e2 55 90 0c a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm1
 2c1:	c5 fd db 25 00 00 00 	vpand  0x0(%rip),%ymm0,%ymm4        # 2c9 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2c9>
 2c8:	00 
 2c9:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 2cd:	c4 e2 75 00 cf       	vpshufb %ymm7,%ymm1,%ymm1
 2d2:	c4 e2 55 90 04 a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm0
 2d8:	c5 f9 6f ee          	vmovdqa %xmm6,%xmm5
 2dc:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
 2e2:	c5 d9 73 fe 0c       	vpslldq $0xc,%xmm6,%xmm4
 2e7:	c5 c9 73 de 04       	vpsrldq $0x4,%xmm6,%xmm6
 2ec:	c4 e2 7d 00 c7       	vpshufb %ymm7,%ymm0,%ymm0
 2f1:	c5 d9 eb e5          	vpor   %xmm5,%xmm4,%xmm4
 2f5:	c5 f9 6f eb          	vmovdqa %xmm3,%xmm5
 2f9:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
 2ff:	c5 f9 d6 70 b0       	vmovq  %xmm6,-0x50(%rax)
 304:	c5 fa 7f 60 a0       	vmovdqu %xmm4,-0x60(%rax)
 309:	c5 d9 73 fb 0c       	vpslldq $0xc,%xmm3,%xmm4
 30e:	c5 e1 73 db 04       	vpsrldq $0x4,%xmm3,%xmm3
 313:	c5 d9 eb e5          	vpor   %xmm5,%xmm4,%xmm4
 317:	c5 f9 d6 58 c8       	vmovq  %xmm3,-0x38(%rax)
 31c:	c5 fa 7f 60 b8       	vmovdqu %xmm4,-0x48(%rax)
 321:	c5 f9 6f e1          	vmovdqa %xmm1,%xmm4
 325:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 32b:	c5 e1 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm3
 330:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 335:	c5 e1 eb dc          	vpor   %xmm4,%xmm3,%xmm3
 339:	c5 f9 d6 48 e0       	vmovq  %xmm1,-0x20(%rax)
 33e:	c5 fa 7f 58 d0       	vmovdqu %xmm3,-0x30(%rax)
 343:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
 347:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 34d:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 352:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 357:	c5 f1 eb cb          	vpor   %xmm3,%xmm1,%xmm1
 35b:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 360:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 365:	49 39 c1             	cmp    %rax,%r9
 368:	0f 85 32 fd ff ff    	jne    a0 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa0>
 36e:	49 83 e0 e0          	and    $0xffffffffffffffe0,%r8
 372:	49 83 c0 20          	add    $0x20,%r8
 376:	49 39 c8             	cmp    %rcx,%r8
 379:	0f 83 3f 01 00 00    	jae    4be <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x4be>
 37f:	48 ff c9             	dec    %rcx
 382:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
 386:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
 38a:	c5 7d 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm8        # 392 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x392>
 391:	00 
 392:	4c 29 c1             	sub    %r8,%rcx
 395:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 39d <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x39d>
 39c:	00 
 39d:	c5 ad 72 d1 1e       	vpsrld $0x1e,%ymm1,%ymm10
 3a2:	4a 8d 04 0a          	lea    (%rdx,%r9,1),%rax
 3a6:	48 c1 e9 03          	shr    $0x3,%rcx
 3aa:	c5 b5 72 d1 18       	vpsrld $0x18,%ymm1,%ymm9
 3af:	4a 8d 54 0a 18       	lea    0x18(%rdx,%r9,1),%rdx
 3b4:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
 3b8:	48 8d 14 ca          	lea    (%rdx,%rcx,8),%rdx
 3bc:	b9 00 00 fc 00       	mov    $0xfc0000,%ecx
 3c1:	c5 f9 6e f1          	vmovd  %ecx,%xmm6
 3c5:	b9 fc 00 00 00       	mov    $0xfc,%ecx
 3ca:	c5 f9 6e e9          	vmovd  %ecx,%xmm5
 3ce:	b9 00 00 03 00       	mov    $0x30000,%ecx
 3d3:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
 3d8:	c5 f9 6e e1          	vmovd  %ecx,%xmm4
 3dc:	b9 00 03 00 00       	mov    $0x300,%ecx
 3e1:	c4 e2 7d 58 ed       	vpbroadcastd %xmm5,%ymm5
 3e6:	c5 f9 6e d9          	vmovd  %ecx,%xmm3
 3ea:	b9 00 fc 00 00       	mov    $0xfc00,%ecx
 3ef:	c4 e2 7d 58 e4       	vpbroadcastd %xmm4,%ymm4
 3f4:	c5 f9 6e d1          	vmovd  %ecx,%xmm2
 3f8:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
 3fd:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
 402:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 408:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 40c:	c5 7a 7e 58 10       	vmovq  0x10(%rax),%xmm11
 411:	c5 7d 6f f9          	vmovdqa %ymm1,%ymm15
 415:	48 83 c0 18          	add    $0x18,%rax
 419:	c4 63 21 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm11,%xmm11
 41f:	c4 c3 7d 38 c3 01    	vinserti128 $0x1,%xmm11,%ymm0,%ymm0
 425:	c4 c2 7d 00 c0       	vpshufb %ymm8,%ymm0,%ymm0
 42a:	c5 5d db d8          	vpand  %ymm0,%ymm4,%ymm11
 42e:	c5 65 db f0          	vpand  %ymm0,%ymm3,%ymm14
 432:	c5 4d db e8          	vpand  %ymm0,%ymm6,%ymm13
 436:	c4 c1 0d 72 d6 08    	vpsrld $0x8,%ymm14,%ymm14
 43c:	c4 c1 25 72 d3 0e    	vpsrld $0xe,%ymm11,%ymm11
 442:	c5 55 db e0          	vpand  %ymm0,%ymm5,%ymm12
 446:	c4 c1 15 72 d5 02    	vpsrld $0x2,%ymm13,%ymm13
 44c:	c4 c1 1d 72 f4 02    	vpslld $0x2,%ymm12,%ymm12
 452:	c4 41 25 eb de       	vpor   %ymm14,%ymm11,%ymm11
 457:	c5 6d db f0          	vpand  %ymm0,%ymm2,%ymm14
 45b:	c4 41 1d eb e5       	vpor   %ymm13,%ymm12,%ymm12
 460:	c5 ad db c0          	vpand  %ymm0,%ymm10,%ymm0
 464:	c4 41 25 eb de       	vpor   %ymm14,%ymm11,%ymm11
 469:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 46e:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 473:	c4 22 05 90 24 9f    	vpgatherdd %ymm15,(%rdi,%ymm11,4),%ymm12
 479:	c4 62 1d 45 d8       	vpsrlvd %ymm0,%ymm12,%ymm11
 47e:	c5 7d 6f e1          	vmovdqa %ymm1,%ymm12
 482:	c4 41 25 db d9       	vpand  %ymm9,%ymm11,%ymm11
 487:	c4 a2 1d 90 04 9e    	vpgatherdd %ymm12,(%rsi,%ymm11,4),%ymm0
 48d:	c4 e2 7d 00 c7       	vpshufb %ymm7,%ymm0,%ymm0
 492:	c5 79 6f e0          	vmovdqa %xmm0,%xmm12
 496:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 49c:	c5 a1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm11
 4a1:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 4a6:	c4 41 21 eb dc       	vpor   %xmm12,%xmm11,%xmm11
 4ab:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 4b0:	c5 7a 7f 58 e8       	vmovdqu %xmm11,-0x18(%rax)
 4b5:	48 39 c2             	cmp    %rax,%rdx
 4b8:	0f 85 4a ff ff ff    	jne    408 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x408>
 4be:	c5 f8 77             	vzeroupper
 4c1:	c9                   	leave
 4c2:	c3                   	ret
 4c3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 4c8:	45 31 c0             	xor    %r8d,%r8d
 4cb:	e9 a6 fe ff ff       	jmp    376 <jshc_channel::avx2_chain_tileindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x376>

00000000000004d0 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
 4d0:	f3 0f 1e fa          	endbr64
 4d4:	55                   	push   %rbp
 4d5:	49 89 d1             	mov    %rdx,%r9
 4d8:	48 89 e5             	mov    %rsp,%rbp
 4db:	53                   	push   %rbx
 4dc:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
 4e0:	49 83 f8 1f          	cmp    $0x1f,%r8
 4e4:	0f 86 be 04 00 00    	jbe    9a8 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x4d8>
 4ea:	bb 00 00 fc 00       	mov    $0xfc0000,%ebx
 4ef:	4d 8d 50 e0          	lea    -0x20(%r8),%r10
 4f3:	c5 7d 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm8        # 4fb <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2b>
 4fa:	00 
 4fb:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 503 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x33>
 502:	00 
 503:	c5 79 6e e3          	vmovd  %ebx,%xmm12
 507:	bb fc 00 00 00       	mov    $0xfc,%ebx
 50c:	4d 89 d3             	mov    %r10,%r11
 50f:	48 89 d0             	mov    %rdx,%rax
 512:	c5 79 6e db          	vmovd  %ebx,%xmm11
 516:	bb 00 00 03 00       	mov    $0x30000,%ebx
 51b:	49 c1 eb 05          	shr    $0x5,%r11
 51f:	48 89 ca             	mov    %rcx,%rdx
 522:	c5 79 6e d3          	vmovd  %ebx,%xmm10
 526:	4f 8d 1c 5b          	lea    (%r11,%r11,2),%r11
 52a:	c4 42 7d 58 e4       	vpbroadcastd %xmm12,%ymm12
 52f:	bb 00 03 00 00       	mov    $0x300,%ebx
 534:	c5 79 6e cb          	vmovd  %ebx,%xmm9
 538:	bb 00 fc 00 00       	mov    $0xfc00,%ebx
 53d:	49 c1 e3 05          	shl    $0x5,%r11
 541:	c4 42 7d 58 db       	vpbroadcastd %xmm11,%ymm11
 546:	c5 f9 6e d3          	vmovd  %ebx,%xmm2
 54a:	4f 8d 5c 19 60       	lea    0x60(%r9,%r11,1),%r11
 54f:	c4 42 7d 58 d2       	vpbroadcastd %xmm10,%ymm10
 554:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
 559:	c4 42 7d 58 c9       	vpbroadcastd %xmm9,%ymm9
 55e:	c5 fd 7f 54 24 e0    	vmovdqa %ymm2,-0x20(%rsp)
 564:	0f 1f 40 00          	nopl   0x0(%rax)
 568:	c5 fa 6f 20          	vmovdqu (%rax),%xmm4
 56c:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
 571:	48 83 c0 60          	add    $0x60,%rax
 575:	48 83 c2 60          	add    $0x60,%rdx
 579:	c5 fa 6f 58 b8       	vmovdqu -0x48(%rax),%xmm3
 57e:	c5 fa 6f 48 d0       	vmovdqu -0x30(%rax),%xmm1
 583:	c4 e3 79 0f c4 0c    	vpalignr $0xc,%xmm4,%xmm0,%xmm0
 589:	c5 fa 7e 68 f8       	vmovq  -0x8(%rax),%xmm5
 58e:	c4 e3 5d 38 e0 01    	vinserti128 $0x1,%xmm0,%ymm4,%ymm4
 594:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
 599:	c4 c2 5d 00 e0       	vpshufb %ymm8,%ymm4,%ymm4
 59e:	c4 e3 79 0f c3 0c    	vpalignr $0xc,%xmm3,%xmm0,%xmm0
 5a4:	c5 35 db f4          	vpand  %ymm4,%ymm9,%ymm14
 5a8:	c5 1d db ec          	vpand  %ymm4,%ymm12,%ymm13
 5ac:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
 5b2:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
 5b7:	c4 c1 0d 72 d6 08    	vpsrld $0x8,%ymm14,%ymm14
 5bd:	c5 a5 db f4          	vpand  %ymm4,%ymm11,%ymm6
 5c1:	c4 c1 15 72 d5 02    	vpsrld $0x2,%ymm13,%ymm13
 5c7:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 5cc:	c4 c2 65 00 d8       	vpshufb %ymm8,%ymm3,%ymm3
 5d1:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
 5d7:	c4 c1 4d eb f5       	vpor   %ymm13,%ymm6,%ymm6
 5dc:	c4 41 15 76 ed       	vpcmpeqd %ymm13,%ymm13,%ymm13
 5e1:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
 5e7:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
 5ec:	c4 c2 75 00 c8       	vpshufb %ymm8,%ymm1,%ymm1
 5f1:	c4 e3 51 0f e8 0c    	vpalignr $0xc,%xmm0,%xmm5,%xmm5
 5f7:	c5 35 db f9          	vpand  %ymm1,%ymm9,%ymm15
 5fb:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
 601:	c4 c1 05 72 d7 08    	vpsrld $0x8,%ymm15,%ymm15
 607:	c5 ad db ec          	vpand  %ymm4,%ymm10,%ymm5
 60b:	c5 d5 72 d5 0e       	vpsrld $0xe,%ymm5,%ymm5
 610:	c4 c2 7d 00 c0       	vpshufb %ymm8,%ymm0,%ymm0
 615:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 61a:	c5 5d db 74 24 e0    	vpand  -0x20(%rsp),%ymm4,%ymm14
 620:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 625:	c5 35 db f3          	vpand  %ymm3,%ymm9,%ymm14
 629:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 62d:	c4 c1 0d 72 d6 08    	vpsrld $0x8,%ymm14,%ymm14
 633:	c4 e2 15 90 34 af    	vpgatherdd %ymm13,(%rdi,%ymm5,4),%ymm6
 639:	c5 dd db 2d 00 00 00 	vpand  0x0(%rip),%ymm4,%ymm5        # 641 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x171>
 640:	00 
 641:	c5 1d db eb          	vpand  %ymm3,%ymm12,%ymm13
 645:	c4 c1 15 72 d5 02    	vpsrld $0x2,%ymm13,%ymm13
 64b:	c5 d5 72 f5 03       	vpslld $0x3,%ymm5,%ymm5
 650:	c4 e2 4d 45 e5       	vpsrlvd %ymm5,%ymm6,%ymm4
 655:	c5 ad db eb          	vpand  %ymm3,%ymm10,%ymm5
 659:	c5 a5 db f3          	vpand  %ymm3,%ymm11,%ymm6
 65d:	c5 d5 72 d5 0e       	vpsrld $0xe,%ymm5,%ymm5
 662:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 667:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 66c:	c5 65 db 74 24 e0    	vpand  -0x20(%rsp),%ymm3,%ymm14
 672:	c4 c1 4d eb f5       	vpor   %ymm13,%ymm6,%ymm6
 677:	c5 e5 db 1d 00 00 00 	vpand  0x0(%rip),%ymm3,%ymm3        # 67f <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1af>
 67e:	00 
 67f:	c4 41 15 76 ed       	vpcmpeqd %ymm13,%ymm13,%ymm13
 684:	c5 dd db 25 00 00 00 	vpand  0x0(%rip),%ymm4,%ymm4        # 68c <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1bc>
 68b:	00 
 68c:	c4 c1 55 eb ee       	vpor   %ymm14,%ymm5,%ymm5
 691:	c5 1d db f1          	vpand  %ymm1,%ymm12,%ymm14
 695:	c5 e5 72 f3 03       	vpslld $0x3,%ymm3,%ymm3
 69a:	c4 c1 0d 72 d6 02    	vpsrld $0x2,%ymm14,%ymm14
 6a0:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 6a4:	c4 e2 15 90 34 af    	vpgatherdd %ymm13,(%rdi,%ymm5,4),%ymm6
 6aa:	c5 2d db e9          	vpand  %ymm1,%ymm10,%ymm13
 6ae:	c5 f5 db 6c 24 e0    	vpand  -0x20(%rsp),%ymm1,%ymm5
 6b4:	c4 e2 4d 45 db       	vpsrlvd %ymm3,%ymm6,%ymm3
 6b9:	c4 c1 15 72 d5 0e    	vpsrld $0xe,%ymm13,%ymm13
 6bf:	c5 a5 db f1          	vpand  %ymm1,%ymm11,%ymm6
 6c3:	c4 41 15 eb ef       	vpor   %ymm15,%ymm13,%ymm13
 6c8:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 6cd:	c5 f5 db 0d 00 00 00 	vpand  0x0(%rip),%ymm1,%ymm1        # 6d5 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x205>
 6d4:	00 
 6d5:	c4 c1 4d eb f6       	vpor   %ymm14,%ymm6,%ymm6
 6da:	c4 c1 55 eb ed       	vpor   %ymm13,%ymm5,%ymm5
 6df:	c4 41 0d 76 f6       	vpcmpeqd %ymm14,%ymm14,%ymm14
 6e4:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 6e8:	c5 2d db e8          	vpand  %ymm0,%ymm10,%ymm13
 6ec:	c5 35 db f8          	vpand  %ymm0,%ymm9,%ymm15
 6f0:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 6f5:	c4 c1 05 72 d7 08    	vpsrld $0x8,%ymm15,%ymm15
 6fb:	c4 e2 0d 90 34 af    	vpgatherdd %ymm14,(%rdi,%ymm5,4),%ymm6
 701:	c4 e2 4d 45 c9       	vpsrlvd %ymm1,%ymm6,%ymm1
 706:	c5 fd db 6c 24 e0    	vpand  -0x20(%rsp),%ymm0,%ymm5
 70c:	c5 1d db f0          	vpand  %ymm0,%ymm12,%ymm14
 710:	c4 c1 15 72 d5 0e    	vpsrld $0xe,%ymm13,%ymm13
 716:	c4 c1 0d 72 d6 02    	vpsrld $0x2,%ymm14,%ymm14
 71c:	c5 a5 db f0          	vpand  %ymm0,%ymm11,%ymm6
 720:	c4 41 15 eb ef       	vpor   %ymm15,%ymm13,%ymm13
 725:	c5 cd 72 f6 02       	vpslld $0x2,%ymm6,%ymm6
 72a:	c5 fd db 05 00 00 00 	vpand  0x0(%rip),%ymm0,%ymm0        # 732 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x262>
 731:	00 
 732:	c4 c1 4d eb f6       	vpor   %ymm14,%ymm6,%ymm6
 737:	c4 c1 55 eb ed       	vpor   %ymm13,%ymm5,%ymm5
 73c:	c4 41 05 76 ff       	vpcmpeqd %ymm15,%ymm15,%ymm15
 741:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
 745:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 74a:	c4 e2 05 90 34 af    	vpgatherdd %ymm15,(%rdi,%ymm5,4),%ymm6
 750:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 754:	c4 e2 4d 45 c0       	vpsrlvd %ymm0,%ymm6,%ymm0
 759:	c4 e2 55 90 34 a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm6
 75f:	c5 e5 db 25 00 00 00 	vpand  0x0(%rip),%ymm3,%ymm4        # 767 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x297>
 766:	00 
 767:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 76b:	c4 e2 4d 00 f7       	vpshufb %ymm7,%ymm6,%ymm6
 770:	c4 e2 55 90 1c a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm3
 776:	c5 f5 db 25 00 00 00 	vpand  0x0(%rip),%ymm1,%ymm4        # 77e <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2ae>
 77d:	00 
 77e:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 782:	c4 e2 65 00 df       	vpshufb %ymm7,%ymm3,%ymm3
 787:	c4 e2 55 90 0c a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm1
 78d:	c5 fd db 25 00 00 00 	vpand  0x0(%rip),%ymm0,%ymm4        # 795 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2c5>
 794:	00 
 795:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
 799:	c4 e2 75 00 cf       	vpshufb %ymm7,%ymm1,%ymm1
 79e:	c4 e2 55 90 04 a6    	vpgatherdd %ymm5,(%rsi,%ymm4,4),%ymm0
 7a4:	c5 f9 6f ee          	vmovdqa %xmm6,%xmm5
 7a8:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
 7ae:	c5 d9 73 fe 0c       	vpslldq $0xc,%xmm6,%xmm4
 7b3:	c5 c9 73 de 04       	vpsrldq $0x4,%xmm6,%xmm6
 7b8:	c4 e2 7d 00 c7       	vpshufb %ymm7,%ymm0,%ymm0
 7bd:	c5 d9 eb e5          	vpor   %xmm5,%xmm4,%xmm4
 7c1:	c5 f9 6f eb          	vmovdqa %xmm3,%xmm5
 7c5:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
 7cb:	c5 f9 d6 72 b0       	vmovq  %xmm6,-0x50(%rdx)
 7d0:	c5 fa 7f 62 a0       	vmovdqu %xmm4,-0x60(%rdx)
 7d5:	c5 d9 73 fb 0c       	vpslldq $0xc,%xmm3,%xmm4
 7da:	c5 e1 73 db 04       	vpsrldq $0x4,%xmm3,%xmm3
 7df:	c5 d9 eb e5          	vpor   %xmm5,%xmm4,%xmm4
 7e3:	c5 f9 d6 5a c8       	vmovq  %xmm3,-0x38(%rdx)
 7e8:	c5 fa 7f 62 b8       	vmovdqu %xmm4,-0x48(%rdx)
 7ed:	c5 f9 6f e1          	vmovdqa %xmm1,%xmm4
 7f1:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 7f7:	c5 e1 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm3
 7fc:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 801:	c5 e1 eb dc          	vpor   %xmm4,%xmm3,%xmm3
 805:	c5 f9 d6 4a e0       	vmovq  %xmm1,-0x20(%rdx)
 80a:	c5 fa 7f 5a d0       	vmovdqu %xmm3,-0x30(%rdx)
 80f:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
 813:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 819:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 81e:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 823:	c5 f1 eb cb          	vpor   %xmm3,%xmm1,%xmm1
 827:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
 82c:	c5 fa 7f 4a e8       	vmovdqu %xmm1,-0x18(%rdx)
 831:	49 39 c3             	cmp    %rax,%r11
 834:	0f 85 2e fd ff ff    	jne    568 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x98>
 83a:	49 83 e2 e0          	and    $0xffffffffffffffe0,%r10
 83e:	49 83 c2 20          	add    $0x20,%r10
 842:	4d 39 c2             	cmp    %r8,%r10
 845:	0f 83 4f 01 00 00    	jae    99a <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x4ca>
 84b:	49 ff c8             	dec    %r8
 84e:	4f 8d 1c 52          	lea    (%r10,%r10,2),%r11
 852:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
 856:	c5 7d 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm8        # 85e <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x38e>
 85d:	00 
 85e:	4d 29 d0             	sub    %r10,%r8
 861:	4a 8d 14 19          	lea    (%rcx,%r11,1),%rdx
 865:	4b 8d 4c 19 18       	lea    0x18(%r9,%r11,1),%rcx
 86a:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 872 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x3a2>
 871:	00 
 872:	c5 ad 72 d1 1e       	vpsrld $0x1e,%ymm1,%ymm10
 877:	49 c1 e8 03          	shr    $0x3,%r8
 87b:	c5 b5 72 d1 18       	vpsrld $0x18,%ymm1,%ymm9
 880:	4b 8d 04 19          	lea    (%r9,%r11,1),%rax
 884:	4f 8d 04 40          	lea    (%r8,%r8,2),%r8
 888:	4a 8d 0c c1          	lea    (%rcx,%r8,8),%rcx
 88c:	41 b8 00 00 fc 00    	mov    $0xfc0000,%r8d
 892:	c4 c1 79 6e f0       	vmovd  %r8d,%xmm6
 897:	41 b8 fc 00 00 00    	mov    $0xfc,%r8d
 89d:	c4 c1 79 6e e8       	vmovd  %r8d,%xmm5
 8a2:	41 b8 00 00 03 00    	mov    $0x30000,%r8d
 8a8:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
 8ad:	c4 c1 79 6e e0       	vmovd  %r8d,%xmm4
 8b2:	41 b8 00 03 00 00    	mov    $0x300,%r8d
 8b8:	c4 e2 7d 58 ed       	vpbroadcastd %xmm5,%ymm5
 8bd:	c4 c1 79 6e d8       	vmovd  %r8d,%xmm3
 8c2:	41 b8 00 fc 00 00    	mov    $0xfc00,%r8d
 8c8:	c4 e2 7d 58 e4       	vpbroadcastd %xmm4,%ymm4
 8cd:	c4 c1 79 6e d0       	vmovd  %r8d,%xmm2
 8d2:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
 8d7:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
 8dc:	0f 1f 40 00          	nopl   0x0(%rax)
 8e0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 8e4:	c5 7a 7e 58 10       	vmovq  0x10(%rax),%xmm11
 8e9:	c5 7d 6f f9          	vmovdqa %ymm1,%ymm15
 8ed:	48 83 c0 18          	add    $0x18,%rax
 8f1:	48 83 c2 18          	add    $0x18,%rdx
 8f5:	c4 63 21 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm11,%xmm11
 8fb:	c4 c3 7d 38 c3 01    	vinserti128 $0x1,%xmm11,%ymm0,%ymm0
 901:	c4 c2 7d 00 c0       	vpshufb %ymm8,%ymm0,%ymm0
 906:	c5 5d db d8          	vpand  %ymm0,%ymm4,%ymm11
 90a:	c5 65 db f0          	vpand  %ymm0,%ymm3,%ymm14
 90e:	c5 4d db e8          	vpand  %ymm0,%ymm6,%ymm13
 912:	c4 c1 0d 72 d6 08    	vpsrld $0x8,%ymm14,%ymm14
 918:	c4 c1 25 72 d3 0e    	vpsrld $0xe,%ymm11,%ymm11
 91e:	c5 55 db e0          	vpand  %ymm0,%ymm5,%ymm12
 922:	c4 c1 15 72 d5 02    	vpsrld $0x2,%ymm13,%ymm13
 928:	c4 c1 1d 72 f4 02    	vpslld $0x2,%ymm12,%ymm12
 92e:	c4 41 25 eb de       	vpor   %ymm14,%ymm11,%ymm11
 933:	c5 6d db f0          	vpand  %ymm0,%ymm2,%ymm14
 937:	c4 41 1d eb e5       	vpor   %ymm13,%ymm12,%ymm12
 93c:	c5 ad db c0          	vpand  %ymm0,%ymm10,%ymm0
 940:	c4 41 25 eb de       	vpor   %ymm14,%ymm11,%ymm11
 945:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 94a:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 94f:	c4 22 05 90 24 9f    	vpgatherdd %ymm15,(%rdi,%ymm11,4),%ymm12
 955:	c4 62 1d 45 d8       	vpsrlvd %ymm0,%ymm12,%ymm11
 95a:	c5 7d 6f e1          	vmovdqa %ymm1,%ymm12
 95e:	c4 41 25 db d9       	vpand  %ymm9,%ymm11,%ymm11
 963:	c4 a2 1d 90 04 9e    	vpgatherdd %ymm12,(%rsi,%ymm11,4),%ymm0
 969:	c4 e2 7d 00 c7       	vpshufb %ymm7,%ymm0,%ymm0
 96e:	c5 79 6f e0          	vmovdqa %xmm0,%xmm12
 972:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 978:	c5 a1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm11
 97d:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 982:	c4 41 21 eb dc       	vpor   %xmm12,%xmm11,%xmm11
 987:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
 98c:	c5 7a 7f 5a e8       	vmovdqu %xmm11,-0x18(%rdx)
 991:	48 39 c1             	cmp    %rax,%rcx
 994:	0f 85 46 ff ff ff    	jne    8e0 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x410>
 99a:	c5 f8 77             	vzeroupper
 99d:	48 8b 5d f8          	mov    -0x8(%rbp),%rbx
 9a1:	c9                   	leave
 9a2:	c3                   	ret
 9a3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 9a8:	45 31 d2             	xor    %r10d,%r10d
 9ab:	e9 92 fe ff ff       	jmp    842 <jshc_channel::avx2_chain_tileindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x372>
