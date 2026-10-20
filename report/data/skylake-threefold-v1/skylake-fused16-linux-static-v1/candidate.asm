
artifacts/skylake-fused16-linux-build-v1/CMakeFiles/jshc_skylake_fused16.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	c5 f9 6e ce          	vmovd  %esi,%xmm1
   8:	c5 f9 6e d2          	vmovd  %edx,%xmm2
   c:	c4 e2 7d 58 c9       	vpbroadcastd %xmm1,%ymm1
  11:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
  16:	49 83 f8 1f          	cmp    $0x1f,%r8
  1a:	0f 86 70 03 00 00    	jbe    390 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x390>
  20:	49 8d 50 e0          	lea    -0x20(%r8),%rdx
  24:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
  28:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 30 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x30>
  2f:	00 
  30:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 38 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x38>
  37:	00 
  38:	c5 c5 72 d6 18       	vpsrld $0x18,%ymm6,%ymm7
  3d:	c5 d5 72 d6 1c       	vpsrld $0x1c,%ymm6,%ymm5
  42:	48 89 d6             	mov    %rdx,%rsi
  45:	48 89 c8             	mov    %rcx,%rax
  48:	48 c1 ee 05          	shr    $0x5,%rsi
  4c:	48 8d 34 76          	lea    (%rsi,%rsi,2),%rsi
  50:	48 c1 e6 05          	shl    $0x5,%rsi
  54:	48 8d 74 31 60       	lea    0x60(%rcx,%rsi,1),%rsi
  59:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  60:	c5 7a 6f 10          	vmovdqu (%rax),%xmm10
  64:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
  69:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
  6d:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
  71:	c5 7a 6f 48 18       	vmovdqu 0x18(%rax),%xmm9
  76:	c5 7a 6f 40 30       	vmovdqu 0x30(%rax),%xmm8
  7b:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
  7f:	48 83 c0 60          	add    $0x60,%rax
  83:	c4 c3 79 0f c2 0c    	vpalignr $0xc,%xmm10,%xmm0,%xmm0
  89:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
  8e:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
  94:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
  99:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
  9e:	c4 c3 79 0f c1 0c    	vpalignr $0xc,%xmm9,%xmm0,%xmm0
  a4:	c4 22 15 90 24 57    	vpgatherdd %ymm13,(%rdi,%ymm10,2),%ymm12
  aa:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
  ae:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
  b4:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
  b9:	c5 1d db d7          	vpand  %ymm7,%ymm12,%ymm10
  bd:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
  c2:	c4 c3 79 0f c0 0c    	vpalignr $0xc,%xmm8,%xmm0,%xmm0
  c8:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
  ce:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
  d3:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
  d8:	c4 63 21 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm11,%xmm11
  de:	c4 c3 7d 38 c3 01    	vinserti128 $0x1,%xmm11,%ymm0,%ymm0
  e4:	c4 22 0d 90 1c 4f    	vpgatherdd %ymm14,(%rdi,%ymm9,2),%ymm11
  ea:	c4 22 05 90 0c 47    	vpgatherdd %ymm15,(%rdi,%ymm8,2),%ymm9
  f0:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
  f5:	c4 62 15 90 04 47    	vpgatherdd %ymm13,(%rdi,%ymm0,2),%ymm8
  fb:	c4 c1 7d 72 d4 08    	vpsrld $0x8,%ymm12,%ymm0
 101:	c4 c1 1d 72 d4 0c    	vpsrld $0xc,%ymm12,%ymm12
 107:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 10b:	c5 1d db e5          	vpand  %ymm5,%ymm12,%ymm12
 10f:	c5 ad fe c0          	vpaddd %ymm0,%ymm10,%ymm0
 113:	c4 41 2d fe e4       	vpaddd %ymm12,%ymm10,%ymm12
 118:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 11c:	c5 1d fe e2          	vpaddd %ymm2,%ymm12,%ymm12
 120:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 125:	c4 c1 1d 72 f4 10    	vpslld $0x10,%ymm12,%ymm12
 12b:	c4 c1 7d eb c4       	vpor   %ymm12,%ymm0,%ymm0
 130:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 135:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 13a:	c5 79 6f e0          	vmovdqa %xmm0,%xmm12
 13e:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 144:	c5 a9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm10
 149:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 14e:	c4 41 29 eb d4       	vpor   %xmm12,%xmm10,%xmm10
 153:	c5 f9 d6 40 b0       	vmovq  %xmm0,-0x50(%rax)
 158:	c4 c1 7d 72 d3 08    	vpsrld $0x8,%ymm11,%ymm0
 15e:	c5 7a 7f 50 a0       	vmovdqu %xmm10,-0x60(%rax)
 163:	c5 25 db d7          	vpand  %ymm7,%ymm11,%ymm10
 167:	c4 c1 25 72 d3 0c    	vpsrld $0xc,%ymm11,%ymm11
 16d:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 171:	c5 25 db dd          	vpand  %ymm5,%ymm11,%ymm11
 175:	c5 ad fe c0          	vpaddd %ymm0,%ymm10,%ymm0
 179:	c4 41 2d fe db       	vpaddd %ymm11,%ymm10,%ymm11
 17e:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 182:	c5 25 fe da          	vpaddd %ymm2,%ymm11,%ymm11
 186:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 18b:	c4 c1 25 72 f3 10    	vpslld $0x10,%ymm11,%ymm11
 191:	c4 c1 7d eb c3       	vpor   %ymm11,%ymm0,%ymm0
 196:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 19b:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 1a0:	c5 79 6f d8          	vmovdqa %xmm0,%xmm11
 1a4:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 1aa:	c5 a9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm10
 1af:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 1b4:	c4 41 29 eb d3       	vpor   %xmm11,%xmm10,%xmm10
 1b9:	c5 f9 d6 40 c8       	vmovq  %xmm0,-0x38(%rax)
 1be:	c4 c1 7d 72 d1 08    	vpsrld $0x8,%ymm9,%ymm0
 1c4:	c5 7a 7f 50 b8       	vmovdqu %xmm10,-0x48(%rax)
 1c9:	c5 35 db d7          	vpand  %ymm7,%ymm9,%ymm10
 1cd:	c4 c1 35 72 d1 0c    	vpsrld $0xc,%ymm9,%ymm9
 1d3:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 1d7:	c5 35 db cd          	vpand  %ymm5,%ymm9,%ymm9
 1db:	c5 ad fe c0          	vpaddd %ymm0,%ymm10,%ymm0
 1df:	c4 41 2d fe c9       	vpaddd %ymm9,%ymm10,%ymm9
 1e4:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 1e8:	c5 35 fe ca          	vpaddd %ymm2,%ymm9,%ymm9
 1ec:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 1f1:	c4 c1 35 72 f1 10    	vpslld $0x10,%ymm9,%ymm9
 1f7:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 1fc:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 201:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 206:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
 20a:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 210:	c5 b1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm9
 215:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 21a:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 21f:	c5 f9 d6 40 e0       	vmovq  %xmm0,-0x20(%rax)
 224:	c4 c1 7d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm0
 22a:	c5 7a 7f 48 d0       	vmovdqu %xmm9,-0x30(%rax)
 22f:	c5 3d db cf          	vpand  %ymm7,%ymm8,%ymm9
 233:	c4 c1 3d 72 d0 0c    	vpsrld $0xc,%ymm8,%ymm8
 239:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 23d:	c5 3d db c5          	vpand  %ymm5,%ymm8,%ymm8
 241:	c5 b5 fe c0          	vpaddd %ymm0,%ymm9,%ymm0
 245:	c4 41 35 fe c0       	vpaddd %ymm8,%ymm9,%ymm8
 24a:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 24e:	c5 3d fe c2          	vpaddd %ymm2,%ymm8,%ymm8
 252:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 257:	c4 c1 3d 72 f0 10    	vpslld $0x10,%ymm8,%ymm8
 25d:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 262:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 267:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 26c:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 270:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 276:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 27b:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 280:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 285:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 28a:	c5 7a 7f 40 e8       	vmovdqu %xmm8,-0x18(%rax)
 28f:	48 39 c6             	cmp    %rax,%rsi
 292:	0f 85 c8 fd ff ff    	jne    60 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x60>
 298:	48 83 e2 e0          	and    $0xffffffffffffffe0,%rdx
 29c:	48 83 c2 20          	add    $0x20,%rdx
 2a0:	4c 39 c2             	cmp    %r8,%rdx
 2a3:	0f 83 de 00 00 00    	jae    387 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x387>
 2a9:	49 ff c8             	dec    %r8
 2ac:	48 8d 34 52          	lea    (%rdx,%rdx,2),%rsi
 2b0:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
 2b4:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 2bc <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x2bc>
 2bb:	00 
 2bc:	49 29 d0             	sub    %rdx,%r8
 2bf:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2c7 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x2c7>
 2c6:	00 
 2c7:	48 8d 54 31 18       	lea    0x18(%rcx,%rsi,1),%rdx
 2cc:	48 8d 04 31          	lea    (%rcx,%rsi,1),%rax
 2d0:	c5 c5 72 d6 18       	vpsrld $0x18,%ymm6,%ymm7
 2d5:	49 c1 e8 03          	shr    $0x3,%r8
 2d9:	c5 d5 72 d6 1c       	vpsrld $0x1c,%ymm6,%ymm5
 2de:	4f 8d 04 40          	lea    (%r8,%r8,2),%r8
 2e2:	4a 8d 14 c2          	lea    (%rdx,%r8,8),%rdx
 2e6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 2ed:	00 00 00 
 2f0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 2f4:	c5 7a 7e 40 10       	vmovq  0x10(%rax),%xmm8
 2f9:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 2fd:	48 83 c0 18          	add    $0x18,%rax
 301:	c4 63 39 0f c0 0c    	vpalignr $0xc,%xmm0,%xmm8,%xmm8
 307:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
 30d:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
 312:	c4 62 0d 90 04 47    	vpgatherdd %ymm14,(%rdi,%ymm0,2),%ymm8
 318:	c5 3d db cf          	vpand  %ymm7,%ymm8,%ymm9
 31c:	c4 c1 7d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm0
 322:	c4 c1 3d 72 d0 0c    	vpsrld $0xc,%ymm8,%ymm8
 328:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 32c:	c5 3d db c5          	vpand  %ymm5,%ymm8,%ymm8
 330:	c5 b5 fe c0          	vpaddd %ymm0,%ymm9,%ymm0
 334:	c4 41 35 fe c0       	vpaddd %ymm8,%ymm9,%ymm8
 339:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 33d:	c5 3d fe c2          	vpaddd %ymm2,%ymm8,%ymm8
 341:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 346:	c4 c1 3d 72 f0 10    	vpslld $0x10,%ymm8,%ymm8
 34c:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 351:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 356:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 35b:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 35f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 365:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 36a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 36f:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 374:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 379:	c5 7a 7f 40 e8       	vmovdqu %xmm8,-0x18(%rax)
 37e:	48 39 c2             	cmp    %rax,%rdx
 381:	0f 85 69 ff ff ff    	jne    2f0 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x2f0>
 387:	c5 f8 77             	vzeroupper
 38a:	c3                   	ret
 38b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 390:	31 d2                	xor    %edx,%edx
 392:	e9 09 ff ff ff       	jmp    2a0 <jshc_channel::avx2_chain_fused16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x2a0>
 397:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 39e:	00 00 

00000000000003a0 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)>:
 3a0:	f3 0f 1e fa          	endbr64
 3a4:	c5 f9 6e ce          	vmovd  %esi,%xmm1
 3a8:	c5 f9 6e d2          	vmovd  %edx,%xmm2
 3ac:	c4 e2 7d 58 c9       	vpbroadcastd %xmm1,%ymm1
 3b1:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
 3b6:	49 83 f9 1f          	cmp    $0x1f,%r9
 3ba:	0f 86 78 03 00 00    	jbe    738 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x398>
 3c0:	49 8d 71 e0          	lea    -0x20(%r9),%rsi
 3c4:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
 3c8:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 3d0 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x30>
 3cf:	00 
 3d0:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 3d8 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x38>
 3d7:	00 
 3d8:	49 89 f2             	mov    %rsi,%r10
 3db:	c5 c5 72 d6 18       	vpsrld $0x18,%ymm6,%ymm7
 3e0:	48 89 c8             	mov    %rcx,%rax
 3e3:	4c 89 c2             	mov    %r8,%rdx
 3e6:	49 c1 ea 05          	shr    $0x5,%r10
 3ea:	c5 d5 72 d6 1c       	vpsrld $0x1c,%ymm6,%ymm5
 3ef:	4f 8d 14 52          	lea    (%r10,%r10,2),%r10
 3f3:	49 c1 e2 05          	shl    $0x5,%r10
 3f7:	4e 8d 54 11 60       	lea    0x60(%rcx,%r10,1),%r10
 3fc:	0f 1f 40 00          	nopl   0x0(%rax)
 400:	c5 7a 6f 10          	vmovdqu (%rax),%xmm10
 404:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
 409:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
 40d:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 411:	c5 7a 6f 48 18       	vmovdqu 0x18(%rax),%xmm9
 416:	c5 7a 6f 40 30       	vmovdqu 0x30(%rax),%xmm8
 41b:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
 41f:	48 83 c0 60          	add    $0x60,%rax
 423:	c4 c3 79 0f c2 0c    	vpalignr $0xc,%xmm10,%xmm0,%xmm0
 429:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
 42e:	48 83 c2 60          	add    $0x60,%rdx
 432:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
 438:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
 43d:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
 442:	c4 c3 79 0f c1 0c    	vpalignr $0xc,%xmm9,%xmm0,%xmm0
 448:	c4 22 15 90 24 57    	vpgatherdd %ymm13,(%rdi,%ymm10,2),%ymm12
 44e:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
 452:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
 458:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
 45d:	c5 1d db d7          	vpand  %ymm7,%ymm12,%ymm10
 461:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
 466:	c4 c3 79 0f c0 0c    	vpalignr $0xc,%xmm8,%xmm0,%xmm0
 46c:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
 472:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
 477:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
 47c:	c4 63 21 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm11,%xmm11
 482:	c4 c3 7d 38 c3 01    	vinserti128 $0x1,%xmm11,%ymm0,%ymm0
 488:	c4 22 0d 90 1c 4f    	vpgatherdd %ymm14,(%rdi,%ymm9,2),%ymm11
 48e:	c4 22 05 90 0c 47    	vpgatherdd %ymm15,(%rdi,%ymm8,2),%ymm9
 494:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
 499:	c4 62 15 90 04 47    	vpgatherdd %ymm13,(%rdi,%ymm0,2),%ymm8
 49f:	c4 c1 7d 72 d4 08    	vpsrld $0x8,%ymm12,%ymm0
 4a5:	c4 c1 1d 72 d4 0c    	vpsrld $0xc,%ymm12,%ymm12
 4ab:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 4af:	c5 1d db e5          	vpand  %ymm5,%ymm12,%ymm12
 4b3:	c5 ad fe c0          	vpaddd %ymm0,%ymm10,%ymm0
 4b7:	c4 41 2d fe e4       	vpaddd %ymm12,%ymm10,%ymm12
 4bc:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 4c0:	c5 1d fe e2          	vpaddd %ymm2,%ymm12,%ymm12
 4c4:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 4c9:	c4 c1 1d 72 f4 10    	vpslld $0x10,%ymm12,%ymm12
 4cf:	c4 c1 7d eb c4       	vpor   %ymm12,%ymm0,%ymm0
 4d4:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 4d9:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 4de:	c5 79 6f e0          	vmovdqa %xmm0,%xmm12
 4e2:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 4e8:	c5 a9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm10
 4ed:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 4f2:	c4 41 29 eb d4       	vpor   %xmm12,%xmm10,%xmm10
 4f7:	c5 f9 d6 42 b0       	vmovq  %xmm0,-0x50(%rdx)
 4fc:	c4 c1 7d 72 d3 08    	vpsrld $0x8,%ymm11,%ymm0
 502:	c5 7a 7f 52 a0       	vmovdqu %xmm10,-0x60(%rdx)
 507:	c5 25 db d7          	vpand  %ymm7,%ymm11,%ymm10
 50b:	c4 c1 25 72 d3 0c    	vpsrld $0xc,%ymm11,%ymm11
 511:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 515:	c5 25 db dd          	vpand  %ymm5,%ymm11,%ymm11
 519:	c5 ad fe c0          	vpaddd %ymm0,%ymm10,%ymm0
 51d:	c4 41 2d fe db       	vpaddd %ymm11,%ymm10,%ymm11
 522:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 526:	c5 25 fe da          	vpaddd %ymm2,%ymm11,%ymm11
 52a:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 52f:	c4 c1 25 72 f3 10    	vpslld $0x10,%ymm11,%ymm11
 535:	c4 c1 7d eb c3       	vpor   %ymm11,%ymm0,%ymm0
 53a:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 53f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 544:	c5 79 6f d8          	vmovdqa %xmm0,%xmm11
 548:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 54e:	c5 a9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm10
 553:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 558:	c4 41 29 eb d3       	vpor   %xmm11,%xmm10,%xmm10
 55d:	c5 f9 d6 42 c8       	vmovq  %xmm0,-0x38(%rdx)
 562:	c4 c1 7d 72 d1 08    	vpsrld $0x8,%ymm9,%ymm0
 568:	c5 7a 7f 52 b8       	vmovdqu %xmm10,-0x48(%rdx)
 56d:	c5 35 db d7          	vpand  %ymm7,%ymm9,%ymm10
 571:	c4 c1 35 72 d1 0c    	vpsrld $0xc,%ymm9,%ymm9
 577:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 57b:	c5 35 db cd          	vpand  %ymm5,%ymm9,%ymm9
 57f:	c5 ad fe c0          	vpaddd %ymm0,%ymm10,%ymm0
 583:	c4 41 2d fe c9       	vpaddd %ymm9,%ymm10,%ymm9
 588:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 58c:	c5 35 fe ca          	vpaddd %ymm2,%ymm9,%ymm9
 590:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 595:	c4 c1 35 72 f1 10    	vpslld $0x10,%ymm9,%ymm9
 59b:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 5a0:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 5a5:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 5aa:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
 5ae:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 5b4:	c5 b1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm9
 5b9:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 5be:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 5c3:	c5 f9 d6 42 e0       	vmovq  %xmm0,-0x20(%rdx)
 5c8:	c4 c1 7d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm0
 5ce:	c5 7a 7f 4a d0       	vmovdqu %xmm9,-0x30(%rdx)
 5d3:	c5 3d db cf          	vpand  %ymm7,%ymm8,%ymm9
 5d7:	c4 c1 3d 72 d0 0c    	vpsrld $0xc,%ymm8,%ymm8
 5dd:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 5e1:	c5 3d db c5          	vpand  %ymm5,%ymm8,%ymm8
 5e5:	c5 b5 fe c0          	vpaddd %ymm0,%ymm9,%ymm0
 5e9:	c4 41 35 fe c0       	vpaddd %ymm8,%ymm9,%ymm8
 5ee:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 5f2:	c5 3d fe c2          	vpaddd %ymm2,%ymm8,%ymm8
 5f6:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 5fb:	c4 c1 3d 72 f0 10    	vpslld $0x10,%ymm8,%ymm8
 601:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 606:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 60b:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 610:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 614:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 61a:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 61f:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 624:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 629:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
 62e:	c5 7a 7f 42 e8       	vmovdqu %xmm8,-0x18(%rdx)
 633:	49 39 c2             	cmp    %rax,%r10
 636:	0f 85 c4 fd ff ff    	jne    400 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x60>
 63c:	48 83 e6 e0          	and    $0xffffffffffffffe0,%rsi
 640:	48 8d 56 20          	lea    0x20(%rsi),%rdx
 644:	4c 39 ca             	cmp    %r9,%rdx
 647:	0f 83 e0 00 00 00    	jae    72d <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x38d>
 64d:	49 ff c9             	dec    %r9
 650:	48 8d 34 52          	lea    (%rdx,%rdx,2),%rsi
 654:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
 658:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 660 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x2c0>
 65f:	00 
 660:	49 29 d1             	sub    %rdx,%r9
 663:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 66b <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x2cb>
 66a:	00 
 66b:	48 8d 54 31 18       	lea    0x18(%rcx,%rsi,1),%rdx
 670:	48 8d 04 31          	lea    (%rcx,%rsi,1),%rax
 674:	c5 c5 72 d6 18       	vpsrld $0x18,%ymm6,%ymm7
 679:	49 c1 e9 03          	shr    $0x3,%r9
 67d:	c5 d5 72 d6 1c       	vpsrld $0x1c,%ymm6,%ymm5
 682:	49 01 f0             	add    %rsi,%r8
 685:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
 689:	4a 8d 14 ca          	lea    (%rdx,%r9,8),%rdx
 68d:	0f 1f 00             	nopl   (%rax)
 690:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 694:	c5 7a 7e 40 10       	vmovq  0x10(%rax),%xmm8
 699:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 69d:	48 83 c0 18          	add    $0x18,%rax
 6a1:	49 83 c0 18          	add    $0x18,%r8
 6a5:	c4 63 39 0f c0 0c    	vpalignr $0xc,%xmm0,%xmm8,%xmm8
 6ab:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
 6b1:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
 6b6:	c4 62 0d 90 04 47    	vpgatherdd %ymm14,(%rdi,%ymm0,2),%ymm8
 6bc:	c5 3d db cf          	vpand  %ymm7,%ymm8,%ymm9
 6c0:	c4 c1 7d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm0
 6c6:	c4 c1 3d 72 d0 0c    	vpsrld $0xc,%ymm8,%ymm8
 6cc:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 6d0:	c5 3d db c5          	vpand  %ymm5,%ymm8,%ymm8
 6d4:	c5 b5 fe c0          	vpaddd %ymm0,%ymm9,%ymm0
 6d8:	c4 41 35 fe c0       	vpaddd %ymm8,%ymm9,%ymm8
 6dd:	c5 fd fe c1          	vpaddd %ymm1,%ymm0,%ymm0
 6e1:	c5 3d fe c2          	vpaddd %ymm2,%ymm8,%ymm8
 6e5:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 6ea:	c4 c1 3d 72 f0 10    	vpslld $0x10,%ymm8,%ymm8
 6f0:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 6f5:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 6fa:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 6ff:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 703:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 709:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 70e:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 713:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 718:	c4 c1 79 d6 40 f8    	vmovq  %xmm0,-0x8(%r8)
 71e:	c4 41 7a 7f 40 e8    	vmovdqu %xmm8,-0x18(%r8)
 724:	48 39 c2             	cmp    %rax,%rdx
 727:	0f 85 63 ff ff ff    	jne    690 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x2f0>
 72d:	c5 f8 77             	vzeroupper
 730:	c3                   	ret
 731:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 738:	31 d2                	xor    %edx,%edx
 73a:	e9 05 ff ff ff       	jmp    644 <jshc_channel::avx2_chain_fused16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x2a4>
