
artifacts/skylake-loadindex-linux-build-v1/CMakeFiles/jshc_skylake_loadindex.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	55                   	push   %rbp
   5:	49 89 d3             	mov    %rdx,%r11
   8:	48 89 e5             	mov    %rsp,%rbp
   b:	41 57                	push   %r15
   d:	41 56                	push   %r14
   f:	41 55                	push   %r13
  11:	41 54                	push   %r12
  13:	53                   	push   %rbx
  14:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
  18:	48 83 f9 1f          	cmp    $0x1f,%rcx
  1c:	0f 86 e6 05 00 00    	jbe    608 <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x608>
  22:	48 8d 59 e0          	lea    -0x20(%rcx),%rbx
  26:	48 89 54 24 e8       	mov    %rdx,-0x18(%rsp)
  2b:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 33 <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x33>
  32:	00 
  33:	49 89 d2             	mov    %rdx,%r10
  36:	48 89 d8             	mov    %rbx,%rax
  39:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
  3e:	48 c1 e8 05          	shr    $0x5,%rax
  42:	48 89 4c 24 e0       	mov    %rcx,-0x20(%rsp)
  47:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
  4b:	48 c1 e0 05          	shl    $0x5,%rax
  4f:	48 8d 44 02 60       	lea    0x60(%rdx,%rax,1),%rax
  54:	48 89 44 24 f8       	mov    %rax,-0x8(%rsp)
  59:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  60:	4d 8b 62 18          	mov    0x18(%r10),%r12
  64:	4d 8b 6a 20          	mov    0x20(%r10),%r13
  68:	4d 8b 4a 28          	mov    0x28(%r10),%r9
  6c:	49 8b 02             	mov    (%r10),%rax
  6f:	49 0f cc             	bswap  %r12
  72:	4d 89 e3             	mov    %r12,%r11
  75:	4c 89 e9             	mov    %r13,%rcx
  78:	45 0f b6 ed          	movzbl %r13b,%r13d
  7c:	49 c1 eb 28          	shr    $0x28,%r11
  80:	48 0f c9             	bswap  %rcx
  83:	49 0f c9             	bswap  %r9
  86:	41 89 ce             	mov    %ecx,%r14d
  89:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
  8e:	4d 89 e3             	mov    %r12,%r11
  91:	41 c1 e4 08          	shl    $0x8,%r12d
  95:	4d 89 cf             	mov    %r9,%r15
  98:	41 81 e4 00 ff ff 00 	and    $0xffff00,%r12d
  9f:	49 c1 ef 30          	shr    $0x30,%r15
  a3:	49 8b 52 08          	mov    0x8(%r10),%rdx
  a7:	4d 8b 42 10          	mov    0x10(%r10),%r8
  ab:	41 c1 ee 08          	shr    $0x8,%r14d
  af:	4d 09 ec             	or     %r13,%r12
  b2:	49 c1 eb 10          	shr    $0x10,%r11
  b6:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
  bb:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
  c0:	49 89 cc             	mov    %rcx,%r12
  c3:	c1 e1 10             	shl    $0x10,%ecx
  c6:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
  cb:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
  d1:	49 c1 ec 20          	shr    $0x20,%r12
  d5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
  dc:	48 0f c8             	bswap  %rax
  df:	4c 09 f9             	or     %r15,%rcx
  e2:	4d 89 cf             	mov    %r9,%r15
  e5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
  ec:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
  f2:	49 c1 ef 18          	shr    $0x18,%r15
  f6:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
  fa:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
  ff:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 106:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 10d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 112:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
 117:	48 0f ca             	bswap  %rdx
 11a:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
 11f:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
 126:	49 0f c8             	bswap  %r8
 129:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
 130:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
 136:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
 13d:	4d 8b 4a 40          	mov    0x40(%r10),%r9
 141:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
 145:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
 14b:	4d 8b 6a 38          	mov    0x38(%r10),%r13
 14f:	49 0f c9             	bswap  %r9
 152:	4d 89 cf             	mov    %r9,%r15
 155:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
 15c:	4d 8b 62 30          	mov    0x30(%r10),%r12
 160:	4c 89 e9             	mov    %r13,%rcx
 163:	45 0f b6 ed          	movzbl %r13b,%r13d
 167:	48 0f c9             	bswap  %rcx
 16a:	41 89 ce             	mov    %ecx,%r14d
 16d:	49 c1 ef 30          	shr    $0x30,%r15
 171:	49 0f cc             	bswap  %r12
 174:	4d 89 e3             	mov    %r12,%r11
 177:	41 c1 ee 08          	shr    $0x8,%r14d
 17b:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
 17f:	49 c1 eb 28          	shr    $0x28,%r11
 183:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
 188:	c4 e3 7d 38 e2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm4
 18e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
 193:	4d 89 e3             	mov    %r12,%r11
 196:	41 c1 e4 08          	shl    $0x8,%r12d
 19a:	41 81 e4 00 ff ff 00 	and    $0xffff00,%r12d
 1a1:	49 c1 eb 10          	shr    $0x10,%r11
 1a5:	4d 09 ec             	or     %r13,%r12
 1a8:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 1af:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
 1b4:	49 89 cc             	mov    %rcx,%r12
 1b7:	c1 e1 10             	shl    $0x10,%ecx
 1ba:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
 1bf:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 1c5:	49 c1 ec 20          	shr    $0x20,%r12
 1c9:	4c 09 f9             	or     %r15,%rcx
 1cc:	4d 89 cf             	mov    %r9,%r15
 1cf:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 1d6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
 1dd:	49 c1 ef 18          	shr    $0x18,%r15
 1e1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 1e6:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 1ea:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 1f1:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
 1f6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
 1fb:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
 201:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
 206:	c4 a1 79 6e 2c be    	vmovd  (%rsi,%r15,4),%xmm5
 20c:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
 213:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
 21a:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
 221:	4d 8b 4a 58          	mov    0x58(%r10),%r9
 225:	c5 e9 6c d5          	vpunpcklqdq %xmm5,%xmm2,%xmm2
 229:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
 22f:	4d 8b 6a 50          	mov    0x50(%r10),%r13
 233:	49 0f c9             	bswap  %r9
 236:	4d 89 cf             	mov    %r9,%r15
 239:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
 240:	4d 8b 62 48          	mov    0x48(%r10),%r12
 244:	4c 89 e9             	mov    %r13,%rcx
 247:	45 0f b6 ed          	movzbl %r13b,%r13d
 24b:	48 0f c9             	bswap  %rcx
 24e:	41 89 ce             	mov    %ecx,%r14d
 251:	49 0f cc             	bswap  %r12
 254:	4d 89 e3             	mov    %r12,%r11
 257:	c5 f9 6c c5          	vpunpcklqdq %xmm5,%xmm0,%xmm0
 25b:	49 c1 eb 28          	shr    $0x28,%r11
 25f:	49 c1 ef 30          	shr    $0x30,%r15
 263:	c4 e3 7d 38 da 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm3
 269:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
 26e:	4d 89 e3             	mov    %r12,%r11
 271:	41 c1 e4 08          	shl    $0x8,%r12d
 275:	41 c1 ee 08          	shr    $0x8,%r14d
 279:	41 81 e4 00 ff ff 00 	and    $0xffff00,%r12d
 280:	49 c1 eb 10          	shr    $0x10,%r11
 284:	4d 09 ec             	or     %r13,%r12
 287:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
 28c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 293:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
 298:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
 29d:	49 89 cc             	mov    %rcx,%r12
 2a0:	c1 e1 10             	shl    $0x10,%ecx
 2a3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
 2a8:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 2ae:	c4 a1 79 6e 2c b6    	vmovd  (%rsi,%r14,4),%xmm5
 2b4:	49 c1 ec 20          	shr    $0x20,%r12
 2b8:	89 d3                	mov    %edx,%ebx
 2ba:	4c 09 f9             	or     %r15,%rcx
 2bd:	4d 89 cf             	mov    %r9,%r15
 2c0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
 2c7:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 2ce:	49 c1 ef 18          	shr    $0x18,%r15
 2d2:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 2d6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
 2db:	c1 eb 08             	shr    $0x8,%ebx
 2de:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 2e5:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
 2ec:	45 0f b6 5a 08       	movzbl 0x8(%r10),%r11d
 2f1:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
 2f6:	c4 e3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm5,%xmm5
 2fd:	48 89 c1             	mov    %rax,%rcx
 300:	48 c1 e9 28          	shr    $0x28,%rcx
 304:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 309:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
 30f:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
 316:	44 0f b6 0c 0f       	movzbl (%rdi,%rcx,1),%r9d
 31b:	48 89 c1             	mov    %rax,%rcx
 31e:	c1 e0 08             	shl    $0x8,%eax
 321:	25 00 ff ff 00       	and    $0xffff00,%eax
 326:	48 c1 e9 10          	shr    $0x10,%rcx
 32a:	c5 d1 6c ee          	vpunpcklqdq %xmm6,%xmm5,%xmm5
 32e:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
 334:	4c 09 d8             	or     %r11,%rax
 337:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 33d:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
 342:	48 89 d0             	mov    %rdx,%rax
 345:	c1 e2 10             	shl    $0x10,%edx
 348:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 34c:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
 353:	4d 89 c4             	mov    %r8,%r12
 356:	81 e2 00 00 ff 00    	and    $0xff0000,%edx
 35c:	48 c1 e8 20          	shr    $0x20,%rax
 360:	49 c1 ec 30          	shr    $0x30,%r12
 364:	25 ff ff ff 00       	and    $0xffffff,%eax
 369:	4c 09 e2             	or     %r12,%rdx
 36c:	4d 89 c4             	mov    %r8,%r12
 36f:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
 373:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
 377:	49 c1 ec 18          	shr    $0x18,%r12
 37b:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
 37f:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 386:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 38a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 391:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
 396:	c4 e3 7d 38 d5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm2
 39c:	c5 f9 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm5
 3a1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 3a6:	c4 a1 79 6e 04 8e    	vmovd  (%rsi,%r9,4),%xmm0
 3ac:	49 83 c2 60          	add    $0x60,%r10
 3b0:	c4 e3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm5,%xmm5
 3b7:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
 3bd:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
 3c4:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
 3cb:	c5 d1 6c ee          	vpunpcklqdq %xmm6,%xmm5,%xmm5
 3cf:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
 3d5:	c4 e3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm6,%xmm6
 3dc:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
 3e0:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
 3e6:	c4 e2 7d 00 c1       	vpshufb %ymm1,%ymm0,%ymm0
 3eb:	c5 f9 6f f0          	vmovdqa %xmm0,%xmm6
 3ef:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 3f5:	c5 d1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm5
 3fa:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 3ff:	c5 d1 eb ee          	vpor   %xmm6,%xmm5,%xmm5
 403:	c4 c1 79 d6 42 b0    	vmovq  %xmm0,-0x50(%r10)
 409:	c4 e2 5d 00 c1       	vpshufb %ymm1,%ymm4,%ymm0
 40e:	c4 c1 7a 7f 6a a0    	vmovdqu %xmm5,-0x60(%r10)
 414:	c5 f9 6f e8          	vmovdqa %xmm0,%xmm5
 418:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 41e:	c5 d9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm4
 423:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 428:	c5 d9 eb e5          	vpor   %xmm5,%xmm4,%xmm4
 42c:	c4 c1 79 d6 42 c8    	vmovq  %xmm0,-0x38(%r10)
 432:	c4 e2 65 00 c1       	vpshufb %ymm1,%ymm3,%ymm0
 437:	c4 c1 7a 7f 62 b8    	vmovdqu %xmm4,-0x48(%r10)
 43d:	c5 f9 6f e0          	vmovdqa %xmm0,%xmm4
 441:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 447:	c5 e1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm3
 44c:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 451:	c5 e1 eb dc          	vpor   %xmm4,%xmm3,%xmm3
 455:	c4 c1 79 d6 42 e0    	vmovq  %xmm0,-0x20(%r10)
 45b:	c4 e2 6d 00 c1       	vpshufb %ymm1,%ymm2,%ymm0
 460:	c4 c1 7a 7f 5a d0    	vmovdqu %xmm3,-0x30(%r10)
 466:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
 46a:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 470:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
 475:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 47a:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
 47e:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
 484:	c4 c1 7a 7f 52 e8    	vmovdqu %xmm2,-0x18(%r10)
 48a:	4c 3b 54 24 f8       	cmp    -0x8(%rsp),%r10
 48f:	0f 85 cb fb ff ff    	jne    60 <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x60>
 495:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
 49a:	4c 8b 5c 24 e8       	mov    -0x18(%rsp),%r11
 49f:	48 8b 4c 24 e0       	mov    -0x20(%rsp),%rcx
 4a4:	48 83 e3 e0          	and    $0xffffffffffffffe0,%rbx
 4a8:	48 83 c3 20          	add    $0x20,%rbx
 4ac:	48 39 cb             	cmp    %rcx,%rbx
 4af:	0f 83 3c 01 00 00    	jae    5f1 <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x5f1>
 4b5:	48 ff c9             	dec    %rcx
 4b8:	48 8d 04 5b          	lea    (%rbx,%rbx,2),%rax
 4bc:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 4c4 <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x4c4>
 4c3:	00 
 4c4:	48 29 d9             	sub    %rbx,%rcx
 4c7:	4d 8d 04 03          	lea    (%r11,%rax,1),%r8
 4cb:	49 8d 44 03 18       	lea    0x18(%r11,%rax,1),%rax
 4d0:	48 c1 e9 03          	shr    $0x3,%rcx
 4d4:	48 8d 14 49          	lea    (%rcx,%rcx,2),%rdx
 4d8:	48 8d 0c d0          	lea    (%rax,%rdx,8),%rcx
 4dc:	0f 1f 40 00          	nopl   0x0(%rax)
 4e0:	49 8b 00             	mov    (%r8),%rax
 4e3:	49 8b 58 08          	mov    0x8(%r8),%rbx
 4e7:	49 83 c0 18          	add    $0x18,%r8
 4eb:	4d 8b 48 f8          	mov    -0x8(%r8),%r9
 4ef:	48 0f c8             	bswap  %rax
 4f2:	49 89 c2             	mov    %rax,%r10
 4f5:	48 89 da             	mov    %rbx,%rdx
 4f8:	0f b6 db             	movzbl %bl,%ebx
 4fb:	49 c1 ea 28          	shr    $0x28,%r10
 4ff:	48 0f ca             	bswap  %rdx
 502:	49 0f c9             	bswap  %r9
 505:	41 89 d4             	mov    %edx,%r12d
 508:	46 0f b6 1c 17       	movzbl (%rdi,%r10,1),%r11d
 50d:	49 89 c2             	mov    %rax,%r10
 510:	c1 e0 08             	shl    $0x8,%eax
 513:	4d 89 cd             	mov    %r9,%r13
 516:	49 c1 ed 30          	shr    $0x30,%r13
 51a:	25 00 ff ff 00       	and    $0xffff00,%eax
 51f:	41 c1 ec 08          	shr    $0x8,%r12d
 523:	48 09 d8             	or     %rbx,%rax
 526:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 52b:	49 c1 ea 10          	shr    $0x10,%r10
 52f:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
 535:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
 539:	48 89 d0             	mov    %rdx,%rax
 53c:	c1 e2 10             	shl    $0x10,%edx
 53f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 546:	81 e2 00 00 ff 00    	and    $0xff0000,%edx
 54c:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
 552:	48 c1 e8 20          	shr    $0x20,%rax
 556:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
 55b:	4c 09 ea             	or     %r13,%rdx
 55e:	4d 89 cd             	mov    %r9,%r13
 561:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
 568:	25 ff ff ff 00       	and    $0xffffff,%eax
 56d:	49 c1 ed 18          	shr    $0x18,%r13
 571:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 575:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
 57a:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 581:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
 585:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
 58c:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
 591:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
 598:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
 59e:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
 5a5:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
 5a9:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
 5ae:	c4 e3 61 22 1c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm3,%xmm3
 5b5:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
 5b9:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
 5bf:	c4 e2 7d 00 c1       	vpshufb %ymm1,%ymm0,%ymm0
 5c4:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
 5c8:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 5ce:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
 5d3:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 5d8:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
 5dc:	c4 c1 79 d6 40 f8    	vmovq  %xmm0,-0x8(%r8)
 5e2:	c4 c1 7a 7f 50 e8    	vmovdqu %xmm2,-0x18(%r8)
 5e8:	49 39 c8             	cmp    %rcx,%r8
 5eb:	0f 85 ef fe ff ff    	jne    4e0 <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x4e0>
 5f1:	c5 f8 77             	vzeroupper
 5f4:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
 5f8:	5b                   	pop    %rbx
 5f9:	41 5c                	pop    %r12
 5fb:	41 5d                	pop    %r13
 5fd:	41 5e                	pop    %r14
 5ff:	41 5f                	pop    %r15
 601:	5d                   	pop    %rbp
 602:	c3                   	ret
 603:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 608:	31 db                	xor    %ebx,%ebx
 60a:	e9 9d fe ff ff       	jmp    4ac <jshc_channel::avx2_chain_loadindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x4ac>
 60f:	90                   	nop

0000000000000610 <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
 610:	f3 0f 1e fa          	endbr64
 614:	55                   	push   %rbp
 615:	49 89 d3             	mov    %rdx,%r11
 618:	48 89 e5             	mov    %rsp,%rbp
 61b:	41 57                	push   %r15
 61d:	41 56                	push   %r14
 61f:	41 55                	push   %r13
 621:	41 54                	push   %r12
 623:	53                   	push   %rbx
 624:	48 89 cb             	mov    %rcx,%rbx
 627:	4c 89 c1             	mov    %r8,%rcx
 62a:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
 62e:	49 83 f8 1f          	cmp    $0x1f,%r8
 632:	0f 86 18 06 00 00    	jbe    c50 <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x640>
 638:	49 89 d2             	mov    %rdx,%r10
 63b:	49 8d 50 e0          	lea    -0x20(%r8),%rdx
 63f:	4c 89 5c 24 e0       	mov    %r11,-0x20(%rsp)
 644:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 64c <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x3c>
 64b:	00 
 64c:	48 89 d0             	mov    %rdx,%rax
 64f:	48 89 54 24 e8       	mov    %rdx,-0x18(%rsp)
 654:	49 89 d9             	mov    %rbx,%r9
 657:	48 c1 e8 05          	shr    $0x5,%rax
 65b:	48 89 5c 24 d8       	mov    %rbx,-0x28(%rsp)
 660:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
 664:	4c 89 44 24 d0       	mov    %r8,-0x30(%rsp)
 669:	48 c1 e0 05          	shl    $0x5,%rax
 66d:	49 8d 44 03 60       	lea    0x60(%r11,%rax,1),%rax
 672:	48 89 44 24 f0       	mov    %rax,-0x10(%rsp)
 677:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 67e:	00 00 
 680:	4d 8b 62 18          	mov    0x18(%r10),%r12
 684:	4d 8b 6a 20          	mov    0x20(%r10),%r13
 688:	49 8b 4a 10          	mov    0x10(%r10),%rcx
 68c:	4d 8b 42 28          	mov    0x28(%r10),%r8
 690:	49 0f cc             	bswap  %r12
 693:	4d 89 e3             	mov    %r12,%r11
 696:	4c 89 eb             	mov    %r13,%rbx
 699:	45 0f b6 ed          	movzbl %r13b,%r13d
 69d:	49 c1 eb 28          	shr    $0x28,%r11
 6a1:	48 0f c9             	bswap  %rcx
 6a4:	48 0f cb             	bswap  %rbx
 6a7:	49 0f c8             	bswap  %r8
 6aa:	49 8b 02             	mov    (%r10),%rax
 6ad:	49 8b 52 08          	mov    0x8(%r10),%rdx
 6b1:	48 89 4c 24 f8       	mov    %rcx,-0x8(%rsp)
 6b6:	48 89 d9             	mov    %rbx,%rcx
 6b9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
 6be:	4d 89 e3             	mov    %r12,%r11
 6c1:	41 c1 e4 08          	shl    $0x8,%r12d
 6c5:	41 89 cf             	mov    %ecx,%r15d
 6c8:	41 c1 ef 08          	shr    $0x8,%r15d
 6cc:	41 81 e4 00 ff ff 00 	and    $0xffff00,%r12d
 6d3:	49 c1 eb 10          	shr    $0x10,%r11
 6d7:	48 0f c8             	bswap  %rax
 6da:	4d 09 ec             	or     %r13,%r12
 6dd:	46 0f b6 34 3f       	movzbl (%rdi,%r15,1),%r14d
 6e2:	4d 89 c7             	mov    %r8,%r15
 6e5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 6ec:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
 6f1:	49 89 cc             	mov    %rcx,%r12
 6f4:	c1 e1 10             	shl    $0x10,%ecx
 6f7:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
 6fc:	49 c1 ef 30          	shr    $0x30,%r15
 700:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 706:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
 70c:	49 c1 ec 20          	shr    $0x20,%r12
 710:	4c 09 f9             	or     %r15,%rcx
 713:	4d 89 c7             	mov    %r8,%r15
 716:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 71d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 724:	49 c1 ef 18          	shr    $0x18,%r15
 728:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 72c:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
 731:	48 0f ca             	bswap  %rdx
 734:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 73b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 740:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
 745:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
 74a:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
 751:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
 758:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
 75e:	c4 a3 61 22 1c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm3,%xmm3
 765:	4d 8b 42 40          	mov    0x40(%r10),%r8
 769:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
 76d:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
 773:	4d 8b 6a 38          	mov    0x38(%r10),%r13
 777:	49 0f c8             	bswap  %r8
 77a:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
 781:	4d 8b 62 30          	mov    0x30(%r10),%r12
 785:	4c 89 eb             	mov    %r13,%rbx
 788:	45 0f b6 ed          	movzbl %r13b,%r13d
 78c:	48 0f cb             	bswap  %rbx
 78f:	48 89 d9             	mov    %rbx,%rcx
 792:	49 0f cc             	bswap  %r12
 795:	4d 89 e3             	mov    %r12,%r11
 798:	41 89 cf             	mov    %ecx,%r15d
 79b:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
 79f:	49 c1 eb 28          	shr    $0x28,%r11
 7a3:	41 c1 ef 08          	shr    $0x8,%r15d
 7a7:	c4 e3 7d 38 e2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm4
 7ad:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
 7b2:	4d 89 e3             	mov    %r12,%r11
 7b5:	41 c1 e4 08          	shl    $0x8,%r12d
 7b9:	46 0f b6 34 3f       	movzbl (%rdi,%r15,1),%r14d
 7be:	41 81 e4 00 ff ff 00 	and    $0xffff00,%r12d
 7c5:	4d 89 c7             	mov    %r8,%r15
 7c8:	49 c1 eb 10          	shr    $0x10,%r11
 7cc:	4d 09 ec             	or     %r13,%r12
 7cf:	49 c1 ef 30          	shr    $0x30,%r15
 7d3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 7da:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
 7df:	49 89 cc             	mov    %rcx,%r12
 7e2:	c1 e1 10             	shl    $0x10,%ecx
 7e5:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
 7ea:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 7f0:	49 c1 ec 20          	shr    $0x20,%r12
 7f4:	4c 09 f9             	or     %r15,%rcx
 7f7:	4d 89 c7             	mov    %r8,%r15
 7fa:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 801:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 808:	49 c1 ef 18          	shr    $0x18,%r15
 80c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 811:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 815:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 81c:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
 821:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
 826:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
 82c:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
 831:	c4 a1 79 6e 2c be    	vmovd  (%rsi,%r15,4),%xmm5
 837:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
 83e:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
 845:	c4 a3 51 22 2c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm5,%xmm5
 84c:	4d 8b 42 58          	mov    0x58(%r10),%r8
 850:	c5 e9 6c d5          	vpunpcklqdq %xmm5,%xmm2,%xmm2
 854:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
 85a:	4d 8b 6a 50          	mov    0x50(%r10),%r13
 85e:	49 0f c8             	bswap  %r8
 861:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
 868:	4d 8b 62 48          	mov    0x48(%r10),%r12
 86c:	4c 89 eb             	mov    %r13,%rbx
 86f:	45 0f b6 ed          	movzbl %r13b,%r13d
 873:	48 0f cb             	bswap  %rbx
 876:	48 89 d9             	mov    %rbx,%rcx
 879:	49 0f cc             	bswap  %r12
 87c:	4d 89 e3             	mov    %r12,%r11
 87f:	41 89 cf             	mov    %ecx,%r15d
 882:	c5 f9 6c c5          	vpunpcklqdq %xmm5,%xmm0,%xmm0
 886:	49 c1 eb 28          	shr    $0x28,%r11
 88a:	41 c1 ef 08          	shr    $0x8,%r15d
 88e:	c4 e3 7d 38 da 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm3
 894:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
 899:	4d 89 e3             	mov    %r12,%r11
 89c:	41 c1 e4 08          	shl    $0x8,%r12d
 8a0:	46 0f b6 34 3f       	movzbl (%rdi,%r15,1),%r14d
 8a5:	41 81 e4 00 ff ff 00 	and    $0xffff00,%r12d
 8ac:	4d 89 c7             	mov    %r8,%r15
 8af:	49 c1 eb 10          	shr    $0x10,%r11
 8b3:	4d 09 ec             	or     %r13,%r12
 8b6:	49 c1 ef 30          	shr    $0x30,%r15
 8ba:	c4 a1 79 6e 2c b6    	vmovd  (%rsi,%r14,4),%xmm5
 8c0:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
 8c5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
 8ca:	49 89 cc             	mov    %rcx,%r12
 8cd:	c1 e1 10             	shl    $0x10,%ecx
 8d0:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 8d7:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 8dd:	48 89 c3             	mov    %rax,%rbx
 8e0:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
 8e5:	49 c1 ec 20          	shr    $0x20,%r12
 8e9:	4c 09 f9             	or     %r15,%rcx
 8ec:	4d 89 c7             	mov    %r8,%r15
 8ef:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 8f6:	48 c1 eb 28          	shr    $0x28,%rbx
 8fa:	49 c1 ef 18          	shr    $0x18,%r15
 8fe:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 902:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
 907:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 90e:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 915:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
 91c:	45 0f b6 5a 08       	movzbl 0x8(%r10),%r11d
 921:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
 926:	c4 e3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm5,%xmm5
 92d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 932:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
 938:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
 93f:	44 0f b6 04 1f       	movzbl (%rdi,%rbx,1),%r8d
 944:	48 89 c3             	mov    %rax,%rbx
 947:	c1 e0 08             	shl    $0x8,%eax
 94a:	48 c1 eb 10          	shr    $0x10,%rbx
 94e:	25 00 ff ff 00       	and    $0xffff00,%eax
 953:	c5 d1 6c ee          	vpunpcklqdq %xmm6,%xmm5,%xmm5
 957:	48 89 d9             	mov    %rbx,%rcx
 95a:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
 960:	4c 09 d8             	or     %r11,%rax
 963:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 969:	89 d3                	mov    %edx,%ebx
 96b:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
 972:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 976:	c1 eb 08             	shr    $0x8,%ebx
 979:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
 97e:	4c 8b 74 24 f8       	mov    -0x8(%rsp),%r14
 983:	48 89 d0             	mov    %rdx,%rax
 986:	c1 e2 10             	shl    $0x10,%edx
 989:	81 e2 00 00 ff 00    	and    $0xff0000,%edx
 98f:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
 993:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
 997:	48 c1 e8 20          	shr    $0x20,%rax
 99b:	4d 89 f4             	mov    %r14,%r12
 99e:	c4 e3 7d 38 d5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm2
 9a4:	25 ff ff ff 00       	and    $0xffffff,%eax
 9a9:	c4 a1 79 6e 04 86    	vmovd  (%rsi,%r8,4),%xmm0
 9af:	49 c1 ec 30          	shr    $0x30,%r12
 9b3:	c5 f9 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm5
 9b8:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
 9bc:	4c 09 e2             	or     %r12,%rdx
 9bf:	4d 89 f4             	mov    %r14,%r12
 9c2:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
 9c9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
 9d0:	49 c1 ec 18          	shr    $0x18,%r12
 9d4:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 9d8:	46 0f b6 2c 37       	movzbl (%rdi,%r14,1),%r13d
 9dd:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 9e4:	49 83 c2 60          	add    $0x60,%r10
 9e8:	49 83 c1 60          	add    $0x60,%r9
 9ec:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 9f1:	c4 e3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm5,%xmm5
 9f8:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
 9fe:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
 a05:	c5 d1 6c ee          	vpunpcklqdq %xmm6,%xmm5,%xmm5
 a09:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
 a0f:	c4 e3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm6,%xmm6
 a16:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
 a1a:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
 a20:	c4 e2 7d 00 c1       	vpshufb %ymm1,%ymm0,%ymm0
 a25:	c5 f9 6f f0          	vmovdqa %xmm0,%xmm6
 a29:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 a2f:	c5 d1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm5
 a34:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 a39:	c5 d1 eb ee          	vpor   %xmm6,%xmm5,%xmm5
 a3d:	c4 c1 79 d6 41 b0    	vmovq  %xmm0,-0x50(%r9)
 a43:	c4 e2 5d 00 c1       	vpshufb %ymm1,%ymm4,%ymm0
 a48:	c4 c1 7a 7f 69 a0    	vmovdqu %xmm5,-0x60(%r9)
 a4e:	c5 f9 6f e8          	vmovdqa %xmm0,%xmm5
 a52:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 a58:	c5 d9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm4
 a5d:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 a62:	c5 d9 eb e5          	vpor   %xmm5,%xmm4,%xmm4
 a66:	c4 c1 79 d6 41 c8    	vmovq  %xmm0,-0x38(%r9)
 a6c:	c4 e2 65 00 c1       	vpshufb %ymm1,%ymm3,%ymm0
 a71:	c4 c1 7a 7f 61 b8    	vmovdqu %xmm4,-0x48(%r9)
 a77:	c5 f9 6f e0          	vmovdqa %xmm0,%xmm4
 a7b:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 a81:	c5 e1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm3
 a86:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 a8b:	c5 e1 eb dc          	vpor   %xmm4,%xmm3,%xmm3
 a8f:	c4 c1 79 d6 41 e0    	vmovq  %xmm0,-0x20(%r9)
 a95:	c4 e2 6d 00 c1       	vpshufb %ymm1,%ymm2,%ymm0
 a9a:	c4 c1 7a 7f 59 d0    	vmovdqu %xmm3,-0x30(%r9)
 aa0:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
 aa4:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 aaa:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
 aaf:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 ab4:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
 ab8:	c4 c1 79 d6 41 f8    	vmovq  %xmm0,-0x8(%r9)
 abe:	c4 c1 7a 7f 51 e8    	vmovdqu %xmm2,-0x18(%r9)
 ac4:	4c 3b 54 24 f0       	cmp    -0x10(%rsp),%r10
 ac9:	0f 85 b1 fb ff ff    	jne    680 <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x70>
 acf:	48 8b 54 24 e8       	mov    -0x18(%rsp),%rdx
 ad4:	4c 8b 5c 24 e0       	mov    -0x20(%rsp),%r11
 ad9:	48 8b 5c 24 d8       	mov    -0x28(%rsp),%rbx
 ade:	48 8b 4c 24 d0       	mov    -0x30(%rsp),%rcx
 ae3:	48 83 e2 e0          	and    $0xffffffffffffffe0,%rdx
 ae7:	4c 8d 52 20          	lea    0x20(%rdx),%r10
 aeb:	49 39 ca             	cmp    %rcx,%r10
 aee:	0f 83 43 01 00 00    	jae    c37 <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x627>
 af4:	48 ff c9             	dec    %rcx
 af7:	4b 8d 04 52          	lea    (%r10,%r10,2),%rax
 afb:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # b03 <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x4f3>
 b02:	00 
 b03:	4c 29 d1             	sub    %r10,%rcx
 b06:	4d 8d 04 03          	lea    (%r11,%rax,1),%r8
 b0a:	4c 8d 0c 03          	lea    (%rbx,%rax,1),%r9
 b0e:	48 c1 e9 03          	shr    $0x3,%rcx
 b12:	49 8d 44 03 18       	lea    0x18(%r11,%rax,1),%rax
 b17:	48 8d 14 49          	lea    (%rcx,%rcx,2),%rdx
 b1b:	4c 8d 14 d0          	lea    (%rax,%rdx,8),%r10
 b1f:	90                   	nop
 b20:	49 8b 00             	mov    (%r8),%rax
 b23:	4d 8b 60 08          	mov    0x8(%r8),%r12
 b27:	49 83 c0 18          	add    $0x18,%r8
 b2b:	49 83 c1 18          	add    $0x18,%r9
 b2f:	49 8b 48 f8          	mov    -0x8(%r8),%rcx
 b33:	48 0f c8             	bswap  %rax
 b36:	48 89 c2             	mov    %rax,%rdx
 b39:	4d 89 e6             	mov    %r12,%r14
 b3c:	45 0f b6 e4          	movzbl %r12b,%r12d
 b40:	48 c1 ea 28          	shr    $0x28,%rdx
 b44:	49 0f ce             	bswap  %r14
 b47:	48 0f c9             	bswap  %rcx
 b4a:	0f b6 1c 17          	movzbl (%rdi,%rdx,1),%ebx
 b4e:	48 89 c2             	mov    %rax,%rdx
 b51:	48 c1 ea 10          	shr    $0x10,%rdx
 b55:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 b5b:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
 b60:	44 0f b6 1c 17       	movzbl (%rdi,%rdx,1),%r11d
 b65:	89 c2                	mov    %eax,%edx
 b67:	4c 89 f0             	mov    %r14,%rax
 b6a:	c1 e2 08             	shl    $0x8,%edx
 b6d:	48 c1 e8 20          	shr    $0x20,%rax
 b71:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
 b77:	25 ff ff ff 00       	and    $0xffffff,%eax
 b7c:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
 b83:	4c 09 e2             	or     %r12,%rdx
 b86:	44 0f b6 24 17       	movzbl (%rdi,%rdx,1),%r12d
 b8b:	0f b6 14 07          	movzbl (%rdi,%rax,1),%edx
 b8f:	44 89 f0             	mov    %r14d,%eax
 b92:	c1 e8 08             	shr    $0x8,%eax
 b95:	44 0f b6 2c 07       	movzbl (%rdi,%rax,1),%r13d
 b9a:	44 89 f0             	mov    %r14d,%eax
 b9d:	49 89 ce             	mov    %rcx,%r14
 ba0:	c1 e0 10             	shl    $0x10,%eax
 ba3:	49 c1 ee 30          	shr    $0x30,%r14
 ba7:	25 00 00 ff 00       	and    $0xff0000,%eax
 bac:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
 bb2:	4c 09 f0             	or     %r14,%rax
 bb5:	49 89 ce             	mov    %rcx,%r14
 bb8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 bbe:	49 c1 ee 18          	shr    $0x18,%r14
 bc2:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
 bc6:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 bca:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
 bd1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
 bd6:	c4 e3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm2,%xmm2
 bdd:	c4 a1 79 6e 1c b6    	vmovd  (%rsi,%r14,4),%xmm3
 be3:	c4 e3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm3,%xmm3
 bea:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
 bee:	c4 a1 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm3
 bf4:	c4 e3 61 22 1c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm3,%xmm3
 bfb:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
 bff:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
 c05:	c4 e2 7d 00 c1       	vpshufb %ymm1,%ymm0,%ymm0
 c0a:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
 c0e:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 c14:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
 c19:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 c1e:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
 c22:	c4 c1 79 d6 41 f8    	vmovq  %xmm0,-0x8(%r9)
 c28:	c4 c1 7a 7f 51 e8    	vmovdqu %xmm2,-0x18(%r9)
 c2e:	4d 39 d0             	cmp    %r10,%r8
 c31:	0f 85 e9 fe ff ff    	jne    b20 <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x510>
 c37:	c5 f8 77             	vzeroupper
 c3a:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
 c3e:	5b                   	pop    %rbx
 c3f:	41 5c                	pop    %r12
 c41:	41 5d                	pop    %r13
 c43:	41 5e                	pop    %r14
 c45:	41 5f                	pop    %r15
 c47:	5d                   	pop    %rbp
 c48:	c3                   	ret
 c49:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 c50:	45 31 d2             	xor    %r10d,%r10d
 c53:	e9 93 fe ff ff       	jmp    aeb <jshc_channel::avx2_chain_loadindex_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x4db>
