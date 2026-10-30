
artifacts/skylake-pack32-linux-build-v1/CMakeFiles/jshc_skylake_pack32.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	49 89 d1             	mov    %rdx,%r9
   7:	48 83 f9 27          	cmp    $0x27,%rcx
   b:	0f 86 97 02 00 00    	jbe    2a8 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2a8>
  11:	48 89 d0             	mov    %rdx,%rax
  14:	48 8d 51 d8          	lea    -0x28(%rcx),%rdx
  18:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
  1c:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # 24 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x24>
  23:	00 
  24:	49 89 d0             	mov    %rdx,%r8
  27:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2f <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2f>
  2e:	00 
  2f:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 37 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x37>
  36:	00 
  37:	c5 bd 72 d6 1e       	vpsrld $0x1e,%ymm6,%ymm8
  3c:	49 c1 e8 05          	shr    $0x5,%r8
  40:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # 48 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
  47:	00 
  48:	c5 c5 72 d6 18       	vpsrld $0x18,%ymm6,%ymm7
  4d:	4f 8d 04 40          	lea    (%r8,%r8,2),%r8
  51:	49 c1 e0 05          	shl    $0x5,%r8
  55:	4f 8d 44 01 60       	lea    0x60(%r9,%r8,1),%r8
  5a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  60:	c4 e2 2d 36 28       	vpermd (%rax),%ymm10,%ymm5
  65:	c4 e2 2d 36 60 18    	vpermd 0x18(%rax),%ymm10,%ymm4
  6b:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
  6f:	48 83 c0 60          	add    $0x60,%rax
  73:	c4 e2 2d 36 48 d0    	vpermd -0x30(%rax),%ymm10,%ymm1
  79:	c4 e2 2d 36 40 e8    	vpermd -0x18(%rax),%ymm10,%ymm0
  7f:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
  83:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
  88:	c4 e2 5d 00 e3       	vpshufb %ymm3,%ymm4,%ymm4
  8d:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
  91:	c5 a5 72 d5 02       	vpsrld $0x2,%ymm5,%ymm11
  96:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
  9b:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
  a0:	c4 22 0d 90 24 9f    	vpgatherdd %ymm14,(%rdi,%ymm11,4),%ymm12
  a6:	c4 41 55 db d8       	vpand  %ymm8,%ymm5,%ymm11
  ab:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
  af:	c4 c1 25 72 f3 03    	vpslld $0x3,%ymm11,%ymm11
  b5:	c4 c2 1d 45 eb       	vpsrlvd %ymm11,%ymm12,%ymm5
  ba:	c5 9d 72 d4 02       	vpsrld $0x2,%ymm4,%ymm12
  bf:	c4 c1 5d db e0       	vpand  %ymm8,%ymm4,%ymm4
  c4:	c4 22 05 90 1c a7    	vpgatherdd %ymm15,(%rdi,%ymm12,4),%ymm11
  ca:	c5 dd 72 f4 03       	vpslld $0x3,%ymm4,%ymm4
  cf:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
  d3:	c5 9d 72 d1 02       	vpsrld $0x2,%ymm1,%ymm12
  d8:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
  dd:	c5 d5 db ef          	vpand  %ymm7,%ymm5,%ymm5
  e1:	c4 e2 25 45 e4       	vpsrlvd %ymm4,%ymm11,%ymm4
  e6:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
  eb:	c4 22 15 90 1c a7    	vpgatherdd %ymm13,(%rdi,%ymm12,4),%ymm11
  f1:	c5 9d 72 d0 02       	vpsrld $0x2,%ymm0,%ymm12
  f6:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
  fb:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
  ff:	c4 e2 25 45 c9       	vpsrlvd %ymm1,%ymm11,%ymm1
 104:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 109:	c4 22 0d 90 1c a7    	vpgatherdd %ymm14,(%rdi,%ymm12,4),%ymm11
 10f:	c4 62 25 45 d8       	vpsrlvd %ymm0,%ymm11,%ymm11
 114:	c4 e2 05 90 04 ae    	vpgatherdd %ymm15,(%rsi,%ymm5,4),%ymm0
 11a:	c5 dd db ef          	vpand  %ymm7,%ymm4,%ymm5
 11e:	c4 e2 15 90 24 ae    	vpgatherdd %ymm13,(%rsi,%ymm5,4),%ymm4
 124:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 128:	c5 f5 db ef          	vpand  %ymm7,%ymm1,%ymm5
 12c:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 130:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
 134:	c4 e2 0d 90 0c ae    	vpgatherdd %ymm14,(%rsi,%ymm5,4),%ymm1
 13a:	c4 a2 05 90 2c 9e    	vpgatherdd %ymm15,(%rsi,%ymm11,4),%ymm5
 140:	c4 e2 75 00 ca       	vpshufb %ymm2,%ymm1,%ymm1
 145:	c4 e2 5d 00 e2       	vpshufb %ymm2,%ymm4,%ymm4
 14a:	c4 e2 55 00 ea       	vpshufb %ymm2,%ymm5,%ymm5
 14f:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 154:	c4 e2 35 36 c9       	vpermd %ymm1,%ymm9,%ymm1
 159:	c4 e2 35 36 ed       	vpermd %ymm5,%ymm9,%ymm5
 15e:	c4 e2 35 36 e4       	vpermd %ymm4,%ymm9,%ymm4
 163:	c4 e2 35 36 c0       	vpermd %ymm0,%ymm9,%ymm0
 168:	c5 79 6f ec          	vmovdqa %xmm4,%xmm13
 16c:	c5 79 6f dd          	vmovdqa %xmm5,%xmm11
 170:	c5 79 6f f0          	vmovdqa %xmm0,%xmm14
 174:	c5 79 6f e1          	vmovdqa %xmm1,%xmm12
 178:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 17e:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
 184:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 18a:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
 190:	c4 41 79 6c fd       	vpunpcklqdq %xmm13,%xmm0,%xmm15
 195:	c4 c3 59 0f e5 08    	vpalignr $0x8,%xmm13,%xmm4,%xmm4
 19b:	c5 79 7f f0          	vmovdqa %xmm14,%xmm0
 19f:	c4 c1 71 6c cb       	vpunpcklqdq %xmm11,%xmm1,%xmm1
 1a4:	c4 c3 51 0f eb 08    	vpalignr $0x8,%xmm11,%xmm5,%xmm5
 1aa:	c4 c3 7d 38 c7 01    	vinserti128 $0x1,%xmm15,%ymm0,%ymm0
 1b0:	c4 c3 5d 38 e4 01    	vinserti128 $0x1,%xmm12,%ymm4,%ymm4
 1b6:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
 1bc:	c5 fe 7f 40 a0       	vmovdqu %ymm0,-0x60(%rax)
 1c1:	c5 fe 7f 60 c0       	vmovdqu %ymm4,-0x40(%rax)
 1c6:	c5 fe 7f 48 e0       	vmovdqu %ymm1,-0x20(%rax)
 1cb:	49 39 c0             	cmp    %rax,%r8
 1ce:	0f 85 8c fe ff ff    	jne    60 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x60>
 1d4:	48 83 e2 e0          	and    $0xffffffffffffffe0,%rdx
 1d8:	48 83 c2 20          	add    $0x20,%rdx
 1dc:	48 39 ca             	cmp    %rcx,%rdx
 1df:	0f 83 b8 00 00 00    	jae    29d <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x29d>
 1e5:	48 ff c9             	dec    %rcx
 1e8:	4c 8d 04 52          	lea    (%rdx,%rdx,2),%r8
 1ec:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
 1f0:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1f8 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1f8>
 1f7:	00 
 1f8:	48 29 d1             	sub    %rdx,%rcx
 1fb:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 203 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x203>
 202:	00 
 203:	4b 8d 54 01 18       	lea    0x18(%r9,%r8,1),%rdx
 208:	4b 8d 04 01          	lea    (%r9,%r8,1),%rax
 20c:	c5 d5 72 d1 1e       	vpsrld $0x1e,%ymm1,%ymm5
 211:	48 c1 e9 03          	shr    $0x3,%rcx
 215:	c5 dd 72 d1 18       	vpsrld $0x18,%ymm1,%ymm4
 21a:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
 21e:	48 8d 14 ca          	lea    (%rdx,%rcx,8),%rdx
 222:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 228:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 22c:	c5 fa 7e 70 10       	vmovq  0x10(%rax),%xmm6
 231:	c5 7d 6f c1          	vmovdqa %ymm1,%ymm8
 235:	48 83 c0 18          	add    $0x18,%rax
 239:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
 23f:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
 245:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 24a:	c5 c5 72 d0 02       	vpsrld $0x2,%ymm0,%ymm7
 24f:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 253:	c4 e2 3d 90 34 bf    	vpgatherdd %ymm8,(%rdi,%ymm7,4),%ymm6
 259:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 25e:	c5 fd 6f f9          	vmovdqa %ymm1,%ymm7
 262:	c4 e2 4d 45 f0       	vpsrlvd %ymm0,%ymm6,%ymm6
 267:	c5 cd db f4          	vpand  %ymm4,%ymm6,%ymm6
 26b:	c4 e2 45 90 04 b6    	vpgatherdd %ymm7,(%rsi,%ymm6,4),%ymm0
 271:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 276:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 27a:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 280:	c5 c9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm6
 285:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 28a:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 28e:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 293:	c5 fa 7f 70 e8       	vmovdqu %xmm6,-0x18(%rax)
 298:	48 39 c2             	cmp    %rax,%rdx
 29b:	75 8b                	jne    228 <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x228>
 29d:	c5 f8 77             	vzeroupper
 2a0:	c3                   	ret
 2a1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 2a8:	31 d2                	xor    %edx,%edx
 2aa:	e9 2d ff ff ff       	jmp    1dc <jshc_channel::avx2_chain_pack32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1dc>
 2af:	90                   	nop

00000000000002b0 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
 2b0:	f3 0f 1e fa          	endbr64
 2b4:	49 89 d1             	mov    %rdx,%r9
 2b7:	49 83 f8 27          	cmp    $0x27,%r8
 2bb:	0f 86 9f 02 00 00    	jbe    560 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2b0>
 2c1:	4d 8d 50 d8          	lea    -0x28(%r8),%r10
 2c5:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
 2c9:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # 2d1 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x21>
 2d0:	00 
 2d1:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2d9 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x29>
 2d8:	00 
 2d9:	4d 89 d3             	mov    %r10,%r11
 2dc:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 2e4 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x34>
 2e3:	00 
 2e4:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # 2ec <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x3c>
 2eb:	00 
 2ec:	48 89 d0             	mov    %rdx,%rax
 2ef:	c5 bd 72 d6 1e       	vpsrld $0x1e,%ymm6,%ymm8
 2f4:	49 c1 eb 05          	shr    $0x5,%r11
 2f8:	c5 c5 72 d6 18       	vpsrld $0x18,%ymm6,%ymm7
 2fd:	48 89 ca             	mov    %rcx,%rdx
 300:	4f 8d 1c 5b          	lea    (%r11,%r11,2),%r11
 304:	49 c1 e3 05          	shl    $0x5,%r11
 308:	4f 8d 5c 19 60       	lea    0x60(%r9,%r11,1),%r11
 30d:	0f 1f 00             	nopl   (%rax)
 310:	c4 e2 2d 36 28       	vpermd (%rax),%ymm10,%ymm5
 315:	c4 e2 2d 36 60 18    	vpermd 0x18(%rax),%ymm10,%ymm4
 31b:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 31f:	48 83 c0 60          	add    $0x60,%rax
 323:	c4 e2 2d 36 48 d0    	vpermd -0x30(%rax),%ymm10,%ymm1
 329:	c4 e2 2d 36 40 e8    	vpermd -0x18(%rax),%ymm10,%ymm0
 32f:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
 333:	48 83 c2 60          	add    $0x60,%rdx
 337:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
 33c:	c4 e2 5d 00 e3       	vpshufb %ymm3,%ymm4,%ymm4
 341:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
 345:	c5 a5 72 d5 02       	vpsrld $0x2,%ymm5,%ymm11
 34a:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
 34f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 354:	c4 22 0d 90 24 9f    	vpgatherdd %ymm14,(%rdi,%ymm11,4),%ymm12
 35a:	c4 41 55 db d8       	vpand  %ymm8,%ymm5,%ymm11
 35f:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 363:	c4 c1 25 72 f3 03    	vpslld $0x3,%ymm11,%ymm11
 369:	c4 c2 1d 45 eb       	vpsrlvd %ymm11,%ymm12,%ymm5
 36e:	c5 9d 72 d4 02       	vpsrld $0x2,%ymm4,%ymm12
 373:	c4 c1 5d db e0       	vpand  %ymm8,%ymm4,%ymm4
 378:	c4 22 05 90 1c a7    	vpgatherdd %ymm15,(%rdi,%ymm12,4),%ymm11
 37e:	c5 dd 72 f4 03       	vpslld $0x3,%ymm4,%ymm4
 383:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
 387:	c5 9d 72 d1 02       	vpsrld $0x2,%ymm1,%ymm12
 38c:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
 391:	c5 d5 db ef          	vpand  %ymm7,%ymm5,%ymm5
 395:	c4 e2 25 45 e4       	vpsrlvd %ymm4,%ymm11,%ymm4
 39a:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 39f:	c4 22 15 90 1c a7    	vpgatherdd %ymm13,(%rdi,%ymm12,4),%ymm11
 3a5:	c5 9d 72 d0 02       	vpsrld $0x2,%ymm0,%ymm12
 3aa:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
 3af:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
 3b3:	c4 e2 25 45 c9       	vpsrlvd %ymm1,%ymm11,%ymm1
 3b8:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 3bd:	c4 22 0d 90 1c a7    	vpgatherdd %ymm14,(%rdi,%ymm12,4),%ymm11
 3c3:	c4 62 25 45 d8       	vpsrlvd %ymm0,%ymm11,%ymm11
 3c8:	c4 e2 05 90 04 ae    	vpgatherdd %ymm15,(%rsi,%ymm5,4),%ymm0
 3ce:	c5 dd db ef          	vpand  %ymm7,%ymm4,%ymm5
 3d2:	c4 e2 15 90 24 ae    	vpgatherdd %ymm13,(%rsi,%ymm5,4),%ymm4
 3d8:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 3dc:	c5 f5 db ef          	vpand  %ymm7,%ymm1,%ymm5
 3e0:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 3e4:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
 3e8:	c4 e2 0d 90 0c ae    	vpgatherdd %ymm14,(%rsi,%ymm5,4),%ymm1
 3ee:	c4 a2 05 90 2c 9e    	vpgatherdd %ymm15,(%rsi,%ymm11,4),%ymm5
 3f4:	c4 e2 75 00 ca       	vpshufb %ymm2,%ymm1,%ymm1
 3f9:	c4 e2 5d 00 e2       	vpshufb %ymm2,%ymm4,%ymm4
 3fe:	c4 e2 55 00 ea       	vpshufb %ymm2,%ymm5,%ymm5
 403:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 408:	c4 e2 35 36 c9       	vpermd %ymm1,%ymm9,%ymm1
 40d:	c4 e2 35 36 ed       	vpermd %ymm5,%ymm9,%ymm5
 412:	c4 e2 35 36 e4       	vpermd %ymm4,%ymm9,%ymm4
 417:	c4 e2 35 36 c0       	vpermd %ymm0,%ymm9,%ymm0
 41c:	c5 79 6f ec          	vmovdqa %xmm4,%xmm13
 420:	c5 79 6f dd          	vmovdqa %xmm5,%xmm11
 424:	c5 79 6f f0          	vmovdqa %xmm0,%xmm14
 428:	c5 79 6f e1          	vmovdqa %xmm1,%xmm12
 42c:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 432:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
 438:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 43e:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
 444:	c4 41 79 6c fd       	vpunpcklqdq %xmm13,%xmm0,%xmm15
 449:	c4 c3 59 0f e5 08    	vpalignr $0x8,%xmm13,%xmm4,%xmm4
 44f:	c5 79 7f f0          	vmovdqa %xmm14,%xmm0
 453:	c4 c1 71 6c cb       	vpunpcklqdq %xmm11,%xmm1,%xmm1
 458:	c4 c3 51 0f eb 08    	vpalignr $0x8,%xmm11,%xmm5,%xmm5
 45e:	c4 c3 7d 38 c7 01    	vinserti128 $0x1,%xmm15,%ymm0,%ymm0
 464:	c4 c3 5d 38 e4 01    	vinserti128 $0x1,%xmm12,%ymm4,%ymm4
 46a:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
 470:	c5 fe 7f 42 a0       	vmovdqu %ymm0,-0x60(%rdx)
 475:	c5 fe 7f 62 c0       	vmovdqu %ymm4,-0x40(%rdx)
 47a:	c5 fe 7f 4a e0       	vmovdqu %ymm1,-0x20(%rdx)
 47f:	49 39 c3             	cmp    %rax,%r11
 482:	0f 85 88 fe ff ff    	jne    310 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
 488:	49 83 e2 e0          	and    $0xffffffffffffffe0,%r10
 48c:	49 83 c2 20          	add    $0x20,%r10
 490:	4d 39 c2             	cmp    %r8,%r10
 493:	0f 83 c0 00 00 00    	jae    559 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2a9>
 499:	49 ff c8             	dec    %r8
 49c:	4f 8d 1c 52          	lea    (%r10,%r10,2),%r11
 4a0:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
 4a4:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 4ac <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1fc>
 4ab:	00 
 4ac:	4d 29 d0             	sub    %r10,%r8
 4af:	4a 8d 14 19          	lea    (%rcx,%r11,1),%rdx
 4b3:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 4bb <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x20b>
 4ba:	00 
 4bb:	4b 8d 4c 19 18       	lea    0x18(%r9,%r11,1),%rcx
 4c0:	c5 d5 72 d1 1e       	vpsrld $0x1e,%ymm1,%ymm5
 4c5:	49 c1 e8 03          	shr    $0x3,%r8
 4c9:	c5 dd 72 d1 18       	vpsrld $0x18,%ymm1,%ymm4
 4ce:	4b 8d 04 19          	lea    (%r9,%r11,1),%rax
 4d2:	4f 8d 04 40          	lea    (%r8,%r8,2),%r8
 4d6:	4a 8d 0c c1          	lea    (%rcx,%r8,8),%rcx
 4da:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 4e0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 4e4:	c5 fa 7e 70 10       	vmovq  0x10(%rax),%xmm6
 4e9:	c5 7d 6f c1          	vmovdqa %ymm1,%ymm8
 4ed:	48 83 c0 18          	add    $0x18,%rax
 4f1:	48 83 c2 18          	add    $0x18,%rdx
 4f5:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
 4fb:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
 501:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 506:	c5 c5 72 d0 02       	vpsrld $0x2,%ymm0,%ymm7
 50b:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 50f:	c4 e2 3d 90 34 bf    	vpgatherdd %ymm8,(%rdi,%ymm7,4),%ymm6
 515:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 51a:	c5 fd 6f f9          	vmovdqa %ymm1,%ymm7
 51e:	c4 e2 4d 45 f0       	vpsrlvd %ymm0,%ymm6,%ymm6
 523:	c5 cd db f4          	vpand  %ymm4,%ymm6,%ymm6
 527:	c4 e2 45 90 04 b6    	vpgatherdd %ymm7,(%rsi,%ymm6,4),%ymm0
 52d:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 532:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 536:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 53c:	c5 c9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm6
 541:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 546:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 54a:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
 54f:	c5 fa 7f 72 e8       	vmovdqu %xmm6,-0x18(%rdx)
 554:	48 39 c1             	cmp    %rax,%rcx
 557:	75 87                	jne    4e0 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x230>
 559:	c5 f8 77             	vzeroupper
 55c:	c3                   	ret
 55d:	0f 1f 00             	nopl   (%rax)
 560:	45 31 d2             	xor    %r10d,%r10d
 563:	e9 28 ff ff ff       	jmp    490 <jshc_channel::avx2_chain_pack32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1e0>
