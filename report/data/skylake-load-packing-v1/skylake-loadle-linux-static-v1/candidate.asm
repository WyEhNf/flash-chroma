
artifacts/skylake-loadle-linux-build-v1/CMakeFiles/jshc_skylake_loadle.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	55                   	push   %rbp
   5:	48 89 e5             	mov    %rsp,%rbp
   8:	41 57                	push   %r15
   a:	41 56                	push   %r14
   c:	49 89 d6             	mov    %rdx,%r14
   f:	41 55                	push   %r13
  11:	49 89 cd             	mov    %rcx,%r13
  14:	41 54                	push   %r12
  16:	53                   	push   %rbx
  17:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
  1b:	48 83 f9 27          	cmp    $0x27,%rcx
  1f:	0f 86 e3 04 00 00    	jbe    508 <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x508>
  25:	48 8d 59 d8          	lea    -0x28(%rcx),%rbx
  29:	48 89 d0             	mov    %rdx,%rax
  2c:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 34 <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x34>
  33:	00 
  34:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 3c <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3c>
  3b:	00 
  3c:	48 89 da             	mov    %rbx,%rdx
  3f:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
  44:	48 c1 ea 05          	shr    $0x5,%rdx
  48:	48 8d 14 52          	lea    (%rdx,%rdx,2),%rdx
  4c:	48 c1 e2 05          	shl    $0x5,%rdx
  50:	4d 8d 7c 16 60       	lea    0x60(%r14,%rdx,1),%r15
  55:	0f 1f 00             	nopl   (%rax)
  58:	8b 50 48             	mov    0x48(%rax),%edx
  5b:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  61:	44 0f b6 04 17       	movzbl (%rdi,%rdx,1),%r8d
  66:	8b 50 4b             	mov    0x4b(%rax),%edx
  69:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  6f:	c4 a1 79 6e 2c 86    	vmovd  (%rsi,%r8,4),%xmm5
  75:	0f b6 0c 17          	movzbl (%rdi,%rdx,1),%ecx
  79:	8b 50 4e             	mov    0x4e(%rax),%edx
  7c:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  82:	c4 e3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm5,%xmm5
  89:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
  8e:	8b 50 51             	mov    0x51(%rax),%edx
  91:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  97:	44 0f b6 0c 17       	movzbl (%rdi,%rdx,1),%r9d
  9c:	8b 50 54             	mov    0x54(%rax),%edx
  9f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  a5:	0f b6 1c 17          	movzbl (%rdi,%rdx,1),%ebx
  a9:	8b 50 57             	mov    0x57(%rax),%edx
  ac:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  b2:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
  b7:	44 0f b6 1c 17       	movzbl (%rdi,%rdx,1),%r11d
  bc:	8b 50 5a             	mov    0x5a(%rax),%edx
  bf:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  c5:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
  cc:	44 0f b6 24 17       	movzbl (%rdi,%rdx,1),%r12d
  d1:	8b 50 5d             	mov    0x5d(%rax),%edx
  d4:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  da:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
  e0:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
  e4:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
  eb:	8b 50 30             	mov    0x30(%rax),%edx
  ee:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  f4:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
  f8:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
  fe:	44 0f b6 04 17       	movzbl (%rdi,%rdx,1),%r8d
 103:	8b 50 33             	mov    0x33(%rax),%edx
 106:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
 10d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 113:	0f b6 0c 17          	movzbl (%rdi,%rdx,1),%ecx
 117:	8b 50 36             	mov    0x36(%rax),%edx
 11a:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
 11e:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
 124:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 12a:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
 12f:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
 134:	8b 50 39             	mov    0x39(%rax),%edx
 137:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
 13c:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 142:	44 0f b6 0c 17       	movzbl (%rdi,%rdx,1),%r9d
 147:	8b 50 3c             	mov    0x3c(%rax),%edx
 14a:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
 150:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 156:	0f b6 1c 17          	movzbl (%rdi,%rdx,1),%ebx
 15a:	8b 50 3f             	mov    0x3f(%rax),%edx
 15d:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
 164:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 16a:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
 16f:	44 0f b6 1c 17       	movzbl (%rdi,%rdx,1),%r11d
 174:	8b 50 42             	mov    0x42(%rax),%edx
 177:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 17d:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
 184:	44 0f b6 24 17       	movzbl (%rdi,%rdx,1),%r12d
 189:	8b 50 45             	mov    0x45(%rax),%edx
 18c:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 192:	c4 a1 79 6e 04 a6    	vmovd  (%rsi,%r12,4),%xmm0
 198:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 19c:	c4 e3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm0,%xmm0
 1a3:	8b 50 18             	mov    0x18(%rax),%edx
 1a6:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 1ac:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
 1b0:	c4 a1 79 6e 04 86    	vmovd  (%rsi,%r8,4),%xmm0
 1b6:	44 0f b6 04 17       	movzbl (%rdi,%rdx,1),%r8d
 1bb:	8b 50 1b             	mov    0x1b(%rax),%edx
 1be:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
 1c5:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 1cb:	0f b6 0c 17          	movzbl (%rdi,%rdx,1),%ecx
 1cf:	8b 50 1e             	mov    0x1e(%rax),%edx
 1d2:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
 1d6:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 1dc:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 1e2:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 1e7:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
 1ec:	8b 50 21             	mov    0x21(%rax),%edx
 1ef:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
 1f4:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
 1f8:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 1fe:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 204:	44 0f b6 0c 17       	movzbl (%rdi,%rdx,1),%r9d
 209:	8b 50 24             	mov    0x24(%rax),%edx
 20c:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 212:	0f b6 1c 17          	movzbl (%rdi,%rdx,1),%ebx
 216:	8b 50 27             	mov    0x27(%rax),%edx
 219:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 21f:	44 0f b6 1c 17       	movzbl (%rdi,%rdx,1),%r11d
 224:	8b 50 2a             	mov    0x2a(%rax),%edx
 227:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 22d:	44 0f b6 24 17       	movzbl (%rdi,%rdx,1),%r12d
 232:	8b 50 2d             	mov    0x2d(%rax),%edx
 235:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 23b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 23f:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
 245:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
 24a:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
 250:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
 257:	8b 10                	mov    (%rax),%edx
 259:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
 260:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
 267:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 26d:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
 271:	c4 a1 79 6e 0c 86    	vmovd  (%rsi,%r8,4),%xmm1
 277:	44 0f b6 04 17       	movzbl (%rdi,%rdx,1),%r8d
 27c:	8b 50 03             	mov    0x3(%rax),%edx
 27f:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
 286:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 28c:	0f b6 0c 17          	movzbl (%rdi,%rdx,1),%ecx
 290:	8b 50 06             	mov    0x6(%rax),%edx
 293:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
 297:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
 29d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 2a3:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
 2a8:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
 2ad:	8b 50 09             	mov    0x9(%rax),%edx
 2b0:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
 2b5:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
 2b9:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 2bf:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 2c5:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
 2cb:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
 2d1:	44 0f b6 0c 17       	movzbl (%rdi,%rdx,1),%r9d
 2d6:	8b 50 0c             	mov    0xc(%rax),%edx
 2d9:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
 2df:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 2e5:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
 2ec:	0f b6 1c 17          	movzbl (%rdi,%rdx,1),%ebx
 2f0:	8b 50 0f             	mov    0xf(%rax),%edx
 2f3:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 2f9:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
 2fe:	44 0f b6 1c 17       	movzbl (%rdi,%rdx,1),%r11d
 303:	8b 50 12             	mov    0x12(%rax),%edx
 306:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 30c:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
 313:	44 0f b6 24 17       	movzbl (%rdi,%rdx,1),%r12d
 318:	8b 50 15             	mov    0x15(%rax),%edx
 31b:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 321:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
 327:	48 83 c0 60          	add    $0x60,%rax
 32b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 32f:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
 336:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
 33a:	c4 a1 79 6e 14 86    	vmovd  (%rsi,%r8,4),%xmm2
 340:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
 347:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
 34b:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
 34f:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
 355:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
 35b:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
 361:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
 365:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
 36a:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
 370:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
 375:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
 379:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
 37f:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
 384:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
 38a:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
 38f:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
 394:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
 399:	4c 39 f8             	cmp    %r15,%rax
 39c:	0f 85 b6 fc ff ff    	jne    58 <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x58>
 3a2:	48 8b 54 24 f8       	mov    -0x8(%rsp),%rdx
 3a7:	48 83 e2 e0          	and    $0xffffffffffffffe0,%rdx
 3ab:	48 83 c2 20          	add    $0x20,%rdx
 3af:	4c 39 ea             	cmp    %r13,%rdx
 3b2:	0f 83 39 01 00 00    	jae    4f1 <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x4f1>
 3b8:	49 ff cd             	dec    %r13
 3bb:	48 8d 0c 52          	lea    (%rdx,%rdx,2),%rcx
 3bf:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 3c7 <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3c7>
 3c6:	00 
 3c7:	49 29 d5             	sub    %rdx,%r13
 3ca:	49 8d 54 0e 18       	lea    0x18(%r14,%rcx,1),%rdx
 3cf:	49 8d 04 0e          	lea    (%r14,%rcx,1),%rax
 3d3:	49 c1 ed 03          	shr    $0x3,%r13
 3d7:	4f 8d 44 6d 00       	lea    0x0(%r13,%r13,2),%r8
 3dc:	4e 8d 0c c2          	lea    (%rdx,%r8,8),%r9
 3e0:	4c 8b 18             	mov    (%rax),%r11
 3e3:	48 8b 50 08          	mov    0x8(%rax),%rdx
 3e7:	48 83 c0 18          	add    $0x18,%rax
 3eb:	48 8b 48 f8          	mov    -0x8(%rax),%rcx
 3ef:	4d 89 d8             	mov    %r11,%r8
 3f2:	4c 89 db             	mov    %r11,%rbx
 3f5:	49 89 d4             	mov    %rdx,%r12
 3f8:	48 c1 eb 30          	shr    $0x30,%rbx
 3fc:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 403:	41 89 cd             	mov    %ecx,%r13d
 406:	49 c1 ec 20          	shr    $0x20,%r12
 40a:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
 40f:	4d 89 d8             	mov    %r11,%r8
 412:	41 89 d3             	mov    %edx,%r11d
 415:	41 c1 e5 08          	shl    $0x8,%r13d
 419:	41 c1 e3 10          	shl    $0x10,%r11d
 41d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 424:	49 c1 e8 18          	shr    $0x18,%r8
 428:	41 09 db             	or     %ebx,%r11d
 42b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 430:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 437:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 43e:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
 443:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
 448:	41 89 d3             	mov    %edx,%r11d
 44b:	48 c1 ea 38          	shr    $0x38,%rdx
 44f:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
 455:	44 09 ea             	or     %r13d,%edx
 458:	49 89 cd             	mov    %rcx,%r13
 45b:	48 c1 e9 28          	shr    $0x28,%rcx
 45f:	49 c1 ed 10          	shr    $0x10,%r13
 463:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 469:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 46d:	41 c1 eb 08          	shr    $0x8,%r11d
 471:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 478:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 47c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
 481:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
 486:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
 48b:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
 492:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
 498:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
 49f:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
 4a6:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
 4aa:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
 4b0:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
 4b7:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
 4bb:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 4c1:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 4c6:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
 4ca:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 4d0:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 4d5:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 4da:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
 4de:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 4e3:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 4e8:	4c 39 c8             	cmp    %r9,%rax
 4eb:	0f 85 ef fe ff ff    	jne    3e0 <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3e0>
 4f1:	c5 f8 77             	vzeroupper
 4f4:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
 4f8:	5b                   	pop    %rbx
 4f9:	41 5c                	pop    %r12
 4fb:	41 5d                	pop    %r13
 4fd:	41 5e                	pop    %r14
 4ff:	41 5f                	pop    %r15
 501:	5d                   	pop    %rbp
 502:	c3                   	ret
 503:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 508:	31 d2                	xor    %edx,%edx
 50a:	e9 a0 fe ff ff       	jmp    3af <jshc_channel::avx2_chain_loadle(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3af>
 50f:	90                   	nop

0000000000000510 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
 510:	f3 0f 1e fa          	endbr64
 514:	55                   	push   %rbp
 515:	49 89 d2             	mov    %rdx,%r10
 518:	48 89 e5             	mov    %rsp,%rbp
 51b:	41 57                	push   %r15
 51d:	41 56                	push   %r14
 51f:	41 55                	push   %r13
 521:	41 54                	push   %r12
 523:	53                   	push   %rbx
 524:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
 528:	49 83 f8 27          	cmp    $0x27,%r8
 52c:	0f 86 06 05 00 00    	jbe    a38 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x528>
 532:	4d 8d 58 d8          	lea    -0x28(%r8),%r11
 536:	4c 89 54 24 f0       	mov    %r10,-0x10(%rsp)
 53b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 543 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x33>
 542:	00 
 543:	48 89 d0             	mov    %rdx,%rax
 546:	4d 89 d9             	mov    %r11,%r9
 549:	4c 89 5c 24 f8       	mov    %r11,-0x8(%rsp)
 54e:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 556 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x46>
 555:	00 
 556:	48 89 ca             	mov    %rcx,%rdx
 559:	49 c1 e9 05          	shr    $0x5,%r9
 55d:	48 89 4c 24 e8       	mov    %rcx,-0x18(%rsp)
 562:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
 566:	49 c1 e1 05          	shl    $0x5,%r9
 56a:	4f 8d 74 0a 60       	lea    0x60(%r10,%r9,1),%r14
 56f:	90                   	nop
 570:	8b 48 48             	mov    0x48(%rax),%ecx
 573:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 579:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
 57e:	8b 48 4b             	mov    0x4b(%rax),%ecx
 581:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 587:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
 58d:	44 0f b6 0c 0f       	movzbl (%rdi,%rcx,1),%r9d
 592:	8b 48 4e             	mov    0x4e(%rax),%ecx
 595:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 59b:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
 5a2:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
 5a6:	8b 48 51             	mov    0x51(%rax),%ecx
 5a9:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 5af:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
 5b4:	8b 48 54             	mov    0x54(%rax),%ecx
 5b7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 5bd:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
 5c2:	8b 48 57             	mov    0x57(%rax),%ecx
 5c5:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 5cb:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
 5d1:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
 5d6:	8b 48 5a             	mov    0x5a(%rax),%ecx
 5d9:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 5df:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
 5e6:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
 5eb:	8b 48 5d             	mov    0x5d(%rax),%ecx
 5ee:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 5f4:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
 5fa:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 5fe:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
 605:	8b 48 30             	mov    0x30(%rax),%ecx
 608:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 60e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
 612:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
 617:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
 61c:	8b 48 33             	mov    0x33(%rax),%ecx
 61f:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
 626:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 62c:	44 0f b6 0c 0f       	movzbl (%rdi,%rcx,1),%r9d
 631:	8b 48 36             	mov    0x36(%rax),%ecx
 634:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
 638:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
 63e:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 644:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
 649:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
 64d:	8b 48 39             	mov    0x39(%rax),%ecx
 650:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
 655:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 65b:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
 660:	8b 48 3c             	mov    0x3c(%rax),%ecx
 663:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
 669:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 66f:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
 674:	8b 48 3f             	mov    0x3f(%rax),%ecx
 677:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
 67e:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 684:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
 68a:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
 68f:	8b 48 42             	mov    0x42(%rax),%ecx
 692:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 698:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
 69f:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
 6a4:	8b 48 45             	mov    0x45(%rax),%ecx
 6a7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 6ad:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
 6b3:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 6b7:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
 6be:	8b 48 18             	mov    0x18(%rax),%ecx
 6c1:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 6c7:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
 6cb:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
 6d0:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
 6d5:	8b 48 1b             	mov    0x1b(%rax),%ecx
 6d8:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
 6df:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 6e5:	44 0f b6 0c 0f       	movzbl (%rdi,%rcx,1),%r9d
 6ea:	8b 48 1e             	mov    0x1e(%rax),%ecx
 6ed:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
 6f1:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 6f7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 6fd:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 702:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
 706:	8b 48 21             	mov    0x21(%rax),%ecx
 709:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
 70e:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
 712:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 718:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 71e:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
 723:	8b 48 24             	mov    0x24(%rax),%ecx
 726:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 72c:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
 731:	8b 48 27             	mov    0x27(%rax),%ecx
 734:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 73a:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
 73f:	8b 48 2a             	mov    0x2a(%rax),%ecx
 742:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 748:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
 74d:	8b 48 2d             	mov    0x2d(%rax),%ecx
 750:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 756:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 75a:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
 760:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
 766:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
 76c:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
 773:	8b 08                	mov    (%rax),%ecx
 775:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
 77c:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
 783:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 789:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
 78e:	8b 48 03             	mov    0x3(%rax),%ecx
 791:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
 795:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
 79a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 7a0:	44 0f b6 0c 0f       	movzbl (%rdi,%rcx,1),%r9d
 7a5:	8b 48 06             	mov    0x6(%rax),%ecx
 7a8:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
 7af:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 7b5:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
 7b9:	8b 48 09             	mov    0x9(%rax),%ecx
 7bc:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
 7c0:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
 7c6:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
 7cc:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 7d2:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
 7d7:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
 7dc:	8b 48 0c             	mov    0xc(%rax),%ecx
 7df:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
 7e4:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
 7eb:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
 7ef:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 7f5:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 7fb:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
 801:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
 806:	8b 48 0f             	mov    0xf(%rax),%ecx
 809:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
 80f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 815:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
 81b:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
 820:	8b 48 12             	mov    0x12(%rax),%ecx
 823:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 829:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
 830:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
 835:	8b 48 15             	mov    0x15(%rax),%ecx
 838:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 83e:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
 844:	48 83 c0 60          	add    $0x60,%rax
 848:	48 83 c2 60          	add    $0x60,%rdx
 84c:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 850:	c4 e3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm7,%xmm7
 857:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
 85b:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
 860:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
 867:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
 86b:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
 86f:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
 875:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
 87b:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
 881:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
 885:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
 88a:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
 890:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
 895:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
 899:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
 89f:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
 8a4:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
 8aa:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
 8af:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
 8b4:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
 8b9:	4c 39 f0             	cmp    %r14,%rax
 8bc:	0f 85 ae fc ff ff    	jne    570 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
 8c2:	4c 8b 5c 24 f8       	mov    -0x8(%rsp),%r11
 8c7:	4c 8b 54 24 f0       	mov    -0x10(%rsp),%r10
 8cc:	48 8b 4c 24 e8       	mov    -0x18(%rsp),%rcx
 8d1:	49 83 e3 e0          	and    $0xffffffffffffffe0,%r11
 8d5:	49 83 c3 20          	add    $0x20,%r11
 8d9:	4d 39 c3             	cmp    %r8,%r11
 8dc:	0f 83 3f 01 00 00    	jae    a21 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x511>
 8e2:	49 ff c8             	dec    %r8
 8e5:	4b 8d 04 5b          	lea    (%r11,%r11,2),%rax
 8e9:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 8f1 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x3e1>
 8f0:	00 
 8f1:	4d 29 d8             	sub    %r11,%r8
 8f4:	49 8d 14 02          	lea    (%r10,%rax,1),%rdx
 8f8:	4c 8d 0c 01          	lea    (%rcx,%rax,1),%r9
 8fc:	49 c1 e8 03          	shr    $0x3,%r8
 900:	49 8d 44 02 18       	lea    0x18(%r10,%rax,1),%rax
 905:	4b 8d 0c 40          	lea    (%r8,%r8,2),%rcx
 909:	4c 8d 14 c8          	lea    (%rax,%rcx,8),%r10
 90d:	0f 1f 00             	nopl   (%rax)
 910:	48 8b 1a             	mov    (%rdx),%rbx
 913:	48 8b 42 08          	mov    0x8(%rdx),%rax
 917:	48 83 c2 18          	add    $0x18,%rdx
 91b:	49 83 c1 18          	add    $0x18,%r9
 91f:	48 8b 4a f8          	mov    -0x8(%rdx),%rcx
 923:	49 89 d8             	mov    %rbx,%r8
 926:	49 89 c5             	mov    %rax,%r13
 929:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 930:	41 89 ce             	mov    %ecx,%r14d
 933:	49 c1 ed 20          	shr    $0x20,%r13
 937:	46 0f b6 1c 07       	movzbl (%rdi,%r8,1),%r11d
 93c:	49 89 d8             	mov    %rbx,%r8
 93f:	48 c1 eb 30          	shr    $0x30,%rbx
 943:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 94a:	41 c1 e6 08          	shl    $0x8,%r14d
 94e:	49 89 dc             	mov    %rbx,%r12
 951:	89 c3                	mov    %eax,%ebx
 953:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
 958:	c1 e3 10             	shl    $0x10,%ebx
 95b:	49 c1 e8 18          	shr    $0x18,%r8
 95f:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
 965:	44 09 e3             	or     %r12d,%ebx
 968:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
 96e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 975:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
 97b:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
 980:	44 0f b6 24 1f       	movzbl (%rdi,%rbx,1),%r12d
 985:	89 c3                	mov    %eax,%ebx
 987:	48 c1 e8 38          	shr    $0x38,%rax
 98b:	44 09 f0             	or     %r14d,%eax
 98e:	49 89 ce             	mov    %rcx,%r14
 991:	48 c1 e9 28          	shr    $0x28,%rcx
 995:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
 99c:	49 c1 ee 10          	shr    $0x10,%r14
 9a0:	25 ff ff ff 00       	and    $0xffffff,%eax
 9a5:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 9a9:	c1 eb 08             	shr    $0x8,%ebx
 9ac:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
 9b3:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
 9b7:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
 9bb:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
 9c0:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
 9c7:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
 9cd:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
 9d4:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
 9d8:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
 9de:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
 9e5:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
 9e9:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 9ef:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 9f4:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
 9f8:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 9fe:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 a03:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 a08:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
 a0c:	c4 c1 79 d6 41 f8    	vmovq  %xmm0,-0x8(%r9)
 a12:	c4 c1 7a 7f 49 e8    	vmovdqu %xmm1,-0x18(%r9)
 a18:	4c 39 d2             	cmp    %r10,%rdx
 a1b:	0f 85 ef fe ff ff    	jne    910 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x400>
 a21:	c5 f8 77             	vzeroupper
 a24:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
 a28:	5b                   	pop    %rbx
 a29:	41 5c                	pop    %r12
 a2b:	41 5d                	pop    %r13
 a2d:	41 5e                	pop    %r14
 a2f:	41 5f                	pop    %r15
 a31:	5d                   	pop    %rbp
 a32:	c3                   	ret
 a33:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 a38:	45 31 db             	xor    %r11d,%r11d
 a3b:	e9 99 fe ff ff       	jmp    8d9 <jshc_channel::avx2_chain_loadle_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x3c9>
