
artifacts/skylake-load16-linux-build-v1/CMakeFiles/jshc_skylake_load16.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	55                   	push   %rbp
   5:	c5 f9 6e ce          	vmovd  %esi,%xmm1
   9:	c5 f9 6e d2          	vmovd  %edx,%xmm2
   d:	48 89 ce             	mov    %rcx,%rsi
  10:	c4 e2 7d 58 c9       	vpbroadcastd %xmm1,%ymm1
  15:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
  1a:	48 89 e5             	mov    %rsp,%rbp
  1d:	41 57                	push   %r15
  1f:	41 56                	push   %r14
  21:	41 55                	push   %r13
  23:	41 54                	push   %r12
  25:	53                   	push   %rbx
  26:	49 83 f8 1f          	cmp    $0x1f,%r8
  2a:	0f 86 98 06 00 00    	jbe    6c8 <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x6c8>
  30:	48 89 c8             	mov    %rcx,%rax
  33:	49 8d 48 e0          	lea    -0x20(%r8),%rcx
  37:	c5 dd 76 e4          	vpcmpeqd %ymm4,%ymm4,%ymm4
  3b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 43 <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x43>
  42:	00 
  43:	48 89 ca             	mov    %rcx,%rdx
  46:	c5 d5 72 d4 18       	vpsrld $0x18,%ymm4,%ymm5
  4b:	48 c1 ea 05          	shr    $0x5,%rdx
  4f:	c5 dd 72 d4 1c       	vpsrld $0x1c,%ymm4,%ymm4
  54:	48 8d 14 52          	lea    (%rdx,%rdx,2),%rdx
  58:	48 c1 e2 05          	shl    $0x5,%rdx
  5c:	4c 8d 4c 16 60       	lea    0x60(%rsi,%rdx,1),%r9
  61:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  68:	48 8b 10             	mov    (%rax),%rdx
  6b:	4c 8b 60 08          	mov    0x8(%rax),%r12
  6f:	48 8b 58 10          	mov    0x10(%rax),%rbx
  73:	48 0f ca             	bswap  %rdx
  76:	49 89 d2             	mov    %rdx,%r10
  79:	49 89 d6             	mov    %rdx,%r14
  7c:	c1 e2 08             	shl    $0x8,%edx
  7f:	48 0f cb             	bswap  %rbx
  82:	49 c1 ea 28          	shr    $0x28,%r10
  86:	4d 89 e3             	mov    %r12,%r11
  89:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
  8f:	45 0f b6 e4          	movzbl %r12b,%r12d
  93:	49 0f cb             	bswap  %r11
  96:	4d 89 dd             	mov    %r11,%r13
  99:	45 89 df             	mov    %r11d,%r15d
  9c:	41 c1 e3 10          	shl    $0x10,%r11d
  a0:	4c 09 e2             	or     %r12,%rdx
  a3:	49 89 dc             	mov    %rbx,%r12
  a6:	41 c1 ef 08          	shr    $0x8,%r15d
  aa:	0f b7 14 57          	movzwl (%rdi,%rdx,2),%edx
  ae:	49 c1 ec 30          	shr    $0x30,%r12
  b2:	41 81 e3 00 00 ff 00 	and    $0xff0000,%r11d
  b9:	46 0f b7 14 57       	movzwl (%rdi,%r10,2),%r10d
  be:	49 c1 ee 10          	shr    $0x10,%r14
  c2:	4d 09 e3             	or     %r12,%r11
  c5:	49 89 dc             	mov    %rbx,%r12
  c8:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
  ce:	49 c1 ec 18          	shr    $0x18,%r12
  d2:	c5 f9 6e fa          	vmovd  %edx,%xmm7
  d6:	42 0f b7 14 7f       	movzwl (%rdi,%r15,2),%edx
  db:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
  e2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
  e9:	c4 41 79 6e ca       	vmovd  %r10d,%xmm9
  ee:	49 c1 ed 20          	shr    $0x20,%r13
  f2:	c5 f9 6e c2          	vmovd  %edx,%xmm0
  f6:	42 0f b7 14 67       	movzwl (%rdi,%r12,2),%edx
  fb:	4c 8b 60 20          	mov    0x20(%rax),%r12
  ff:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 106:	c4 21 31 c4 0c 77 01 	vpinsrw $0x1,(%rdi,%r14,2),%xmm9,%xmm9
 10d:	c4 a1 79 c4 04 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm0,%xmm0
 114:	c5 f9 6e f2          	vmovd  %edx,%xmm6
 118:	48 8b 50 18          	mov    0x18(%rax),%rdx
 11c:	4d 89 e3             	mov    %r12,%r11
 11f:	45 0f b6 e4          	movzbl %r12b,%r12d
 123:	c5 c9 c4 34 5f 01    	vpinsrw $0x1,(%rdi,%rbx,2),%xmm6,%xmm6
 129:	48 8b 58 28          	mov    0x28(%rax),%rbx
 12d:	49 0f cb             	bswap  %r11
 130:	45 89 df             	mov    %r11d,%r15d
 133:	48 0f ca             	bswap  %rdx
 136:	49 89 d2             	mov    %rdx,%r10
 139:	49 89 d6             	mov    %rdx,%r14
 13c:	c1 e2 08             	shl    $0x8,%edx
 13f:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
 145:	c4 a1 41 c4 3c 6f 01 	vpinsrw $0x1,(%rdi,%r13,2),%xmm7,%xmm7
 14c:	48 0f cb             	bswap  %rbx
 14f:	4d 89 dd             	mov    %r11,%r13
 152:	41 c1 e3 10          	shl    $0x10,%r11d
 156:	4c 09 e2             	or     %r12,%rdx
 159:	49 89 dc             	mov    %rbx,%r12
 15c:	41 c1 ef 08          	shr    $0x8,%r15d
 160:	0f b7 14 57          	movzwl (%rdi,%rdx,2),%edx
 164:	49 c1 ec 30          	shr    $0x30,%r12
 168:	41 81 e3 00 00 ff 00 	and    $0xff0000,%r11d
 16f:	c5 31 62 cf          	vpunpckldq %xmm7,%xmm9,%xmm9
 173:	49 c1 ea 28          	shr    $0x28,%r10
 177:	4d 09 e3             	or     %r12,%r11
 17a:	49 89 dc             	mov    %rbx,%r12
 17d:	49 c1 ee 10          	shr    $0x10,%r14
 181:	49 c1 ec 18          	shr    $0x18,%r12
 185:	c5 f9 6e fa          	vmovd  %edx,%xmm7
 189:	42 0f b7 14 7f       	movzwl (%rdi,%r15,2),%edx
 18e:	c5 f9 62 c6          	vpunpckldq %xmm6,%xmm0,%xmm0
 192:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 199:	c5 31 6c c8          	vpunpcklqdq %xmm0,%xmm9,%xmm9
 19d:	46 0f b7 14 57       	movzwl (%rdi,%r10,2),%r10d
 1a2:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
 1a9:	c5 f9 6e c2          	vmovd  %edx,%xmm0
 1ad:	42 0f b7 14 67       	movzwl (%rdi,%r12,2),%edx
 1b2:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
 1b8:	4c 8b 60 38          	mov    0x38(%rax),%r12
 1bc:	c4 41 79 6e c2       	vmovd  %r10d,%xmm8
 1c1:	49 c1 ed 20          	shr    $0x20,%r13
 1c5:	c4 a1 79 c4 04 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm0,%xmm0
 1cc:	c4 42 7d 33 c9       	vpmovzxwd %xmm9,%ymm9
 1d1:	c5 f9 6e f2          	vmovd  %edx,%xmm6
 1d5:	48 8b 50 30          	mov    0x30(%rax),%rdx
 1d9:	c4 21 39 c4 04 77 01 	vpinsrw $0x1,(%rdi,%r14,2),%xmm8,%xmm8
 1e0:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 1e7:	c5 c9 c4 34 5f 01    	vpinsrw $0x1,(%rdi,%rbx,2),%xmm6,%xmm6
 1ed:	48 8b 58 40          	mov    0x40(%rax),%rbx
 1f1:	4d 89 e3             	mov    %r12,%r11
 1f4:	45 0f b6 e4          	movzbl %r12b,%r12d
 1f8:	48 0f ca             	bswap  %rdx
 1fb:	49 89 d2             	mov    %rdx,%r10
 1fe:	49 89 d6             	mov    %rdx,%r14
 201:	c4 a1 41 c4 3c 6f 01 	vpinsrw $0x1,(%rdi,%r13,2),%xmm7,%xmm7
 208:	49 c1 ea 28          	shr    $0x28,%r10
 20c:	c1 e2 08             	shl    $0x8,%edx
 20f:	49 0f cb             	bswap  %r11
 212:	48 0f cb             	bswap  %rbx
 215:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
 21b:	4d 89 dd             	mov    %r11,%r13
 21e:	45 89 df             	mov    %r11d,%r15d
 221:	41 c1 e3 10          	shl    $0x10,%r11d
 225:	4c 09 e2             	or     %r12,%rdx
 228:	49 89 dc             	mov    %rbx,%r12
 22b:	41 81 e3 00 00 ff 00 	and    $0xff0000,%r11d
 232:	41 c1 ef 08          	shr    $0x8,%r15d
 236:	0f b7 14 57          	movzwl (%rdi,%rdx,2),%edx
 23a:	49 c1 ec 30          	shr    $0x30,%r12
 23e:	c5 f9 62 c6          	vpunpckldq %xmm6,%xmm0,%xmm0
 242:	c5 39 62 c7          	vpunpckldq %xmm7,%xmm8,%xmm8
 246:	4d 09 e3             	or     %r12,%r11
 249:	49 89 dc             	mov    %rbx,%r12
 24c:	46 0f b7 14 57       	movzwl (%rdi,%r10,2),%r10d
 251:	c5 39 6c c0          	vpunpcklqdq %xmm0,%xmm8,%xmm8
 255:	49 c1 ec 18          	shr    $0x18,%r12
 259:	c5 79 6e d2          	vmovd  %edx,%xmm10
 25d:	42 0f b7 14 7f       	movzwl (%rdi,%r15,2),%edx
 262:	49 c1 ee 10          	shr    $0x10,%r14
 266:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 26d:	49 c1 ed 20          	shr    $0x20,%r13
 271:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
 278:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
 27e:	c5 f9 6e c2          	vmovd  %edx,%xmm0
 282:	42 0f b7 14 67       	movzwl (%rdi,%r12,2),%edx
 287:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 28e:	c4 c1 79 6e fa       	vmovd  %r10d,%xmm7
 293:	c4 21 29 c4 14 6f 01 	vpinsrw $0x1,(%rdi,%r13,2),%xmm10,%xmm10
 29a:	c4 a1 41 c4 3c 77 01 	vpinsrw $0x1,(%rdi,%r14,2),%xmm7,%xmm7
 2a1:	c4 42 7d 33 c0       	vpmovzxwd %xmm8,%ymm8
 2a6:	c5 f9 6e f2          	vmovd  %edx,%xmm6
 2aa:	c4 a1 79 c4 04 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm0,%xmm0
 2b1:	c5 c9 c4 34 5f 01    	vpinsrw $0x1,(%rdi,%rbx,2),%xmm6,%xmm6
 2b7:	48 8b 50 48          	mov    0x48(%rax),%rdx
 2bb:	c4 c1 41 62 fa       	vpunpckldq %xmm10,%xmm7,%xmm7
 2c0:	4c 8b 60 50          	mov    0x50(%rax),%r12
 2c4:	48 8b 58 58          	mov    0x58(%rax),%rbx
 2c8:	48 0f ca             	bswap  %rdx
 2cb:	49 89 d2             	mov    %rdx,%r10
 2ce:	49 89 d6             	mov    %rdx,%r14
 2d1:	c1 e2 08             	shl    $0x8,%edx
 2d4:	4d 89 e3             	mov    %r12,%r11
 2d7:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
 2dd:	45 0f b6 e4          	movzbl %r12b,%r12d
 2e1:	48 0f cb             	bswap  %rbx
 2e4:	49 0f cb             	bswap  %r11
 2e7:	4c 09 e2             	or     %r12,%rdx
 2ea:	4d 89 dd             	mov    %r11,%r13
 2ed:	45 89 df             	mov    %r11d,%r15d
 2f0:	49 89 dc             	mov    %rbx,%r12
 2f3:	41 c1 e3 10          	shl    $0x10,%r11d
 2f7:	0f b7 14 57          	movzwl (%rdi,%rdx,2),%edx
 2fb:	c5 f9 62 c6          	vpunpckldq %xmm6,%xmm0,%xmm0
 2ff:	49 c1 ec 30          	shr    $0x30,%r12
 303:	41 81 e3 00 00 ff 00 	and    $0xff0000,%r11d
 30a:	41 c1 ef 08          	shr    $0x8,%r15d
 30e:	c5 c1 6c f8          	vpunpcklqdq %xmm0,%xmm7,%xmm7
 312:	4d 09 e3             	or     %r12,%r11
 315:	49 89 dc             	mov    %rbx,%r12
 318:	c5 79 6e da          	vmovd  %edx,%xmm11
 31c:	42 0f b7 14 7f       	movzwl (%rdi,%r15,2),%edx
 321:	49 c1 ec 18          	shr    $0x18,%r12
 325:	49 c1 ea 28          	shr    $0x28,%r10
 329:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
 32f:	c4 e2 7d 33 ff       	vpmovzxwd %xmm7,%ymm7
 334:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 33b:	46 0f b7 14 57       	movzwl (%rdi,%r10,2),%r10d
 340:	c5 f9 6e c2          	vmovd  %edx,%xmm0
 344:	49 c1 ee 10          	shr    $0x10,%r14
 348:	42 0f b7 14 67       	movzwl (%rdi,%r12,2),%edx
 34d:	49 c1 ed 20          	shr    $0x20,%r13
 351:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
 358:	c4 a1 79 c4 04 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm0,%xmm0
 35f:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 366:	c4 c1 79 6e f2       	vmovd  %r10d,%xmm6
 36b:	48 83 c0 60          	add    $0x60,%rax
 36f:	c5 79 6e d2          	vmovd  %edx,%xmm10
 373:	c4 a1 49 c4 34 77 01 	vpinsrw $0x1,(%rdi,%r14,2),%xmm6,%xmm6
 37a:	c4 21 21 c4 1c 6f 01 	vpinsrw $0x1,(%rdi,%r13,2),%xmm11,%xmm11
 381:	c5 29 c4 14 5f 01    	vpinsrw $0x1,(%rdi,%rbx,2),%xmm10,%xmm10
 387:	c4 c1 49 62 f3       	vpunpckldq %xmm11,%xmm6,%xmm6
 38c:	c4 c1 79 62 c2       	vpunpckldq %xmm10,%xmm0,%xmm0
 391:	c5 35 db d5          	vpand  %ymm5,%ymm9,%ymm10
 395:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
 399:	c4 c1 7d 72 d1 08    	vpsrld $0x8,%ymm9,%ymm0
 39f:	c4 c1 35 72 d1 0c    	vpsrld $0xc,%ymm9,%ymm9
 3a5:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 3a9:	c4 e2 7d 33 f6       	vpmovzxwd %xmm6,%ymm6
 3ae:	c5 35 db cc          	vpand  %ymm4,%ymm9,%ymm9
 3b2:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 3b6:	c4 41 6d fe c9       	vpaddd %ymm9,%ymm2,%ymm9
 3bb:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
 3c0:	c4 41 35 fe ca       	vpaddd %ymm10,%ymm9,%ymm9
 3c5:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 3ca:	c4 c1 35 72 f1 10    	vpslld $0x10,%ymm9,%ymm9
 3d0:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 3d5:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 3da:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 3df:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
 3e3:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 3e9:	c5 b1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm9
 3ee:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 3f3:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 3f8:	c5 f9 d6 40 b0       	vmovq  %xmm0,-0x50(%rax)
 3fd:	c4 c1 7d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm0
 403:	c5 7a 7f 48 a0       	vmovdqu %xmm9,-0x60(%rax)
 408:	c5 3d db cd          	vpand  %ymm5,%ymm8,%ymm9
 40c:	c4 c1 3d 72 d0 0c    	vpsrld $0xc,%ymm8,%ymm8
 412:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 416:	c5 3d db c4          	vpand  %ymm4,%ymm8,%ymm8
 41a:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 41e:	c4 41 6d fe c0       	vpaddd %ymm8,%ymm2,%ymm8
 423:	c4 c1 7d fe c1       	vpaddd %ymm9,%ymm0,%ymm0
 428:	c4 41 3d fe c1       	vpaddd %ymm9,%ymm8,%ymm8
 42d:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 432:	c4 c1 3d 72 f0 10    	vpslld $0x10,%ymm8,%ymm8
 438:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 43d:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 442:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 447:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 44b:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 451:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 456:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 45b:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 460:	c5 f9 d6 40 c8       	vmovq  %xmm0,-0x38(%rax)
 465:	c5 fd 72 d7 08       	vpsrld $0x8,%ymm7,%ymm0
 46a:	c5 7a 7f 40 b8       	vmovdqu %xmm8,-0x48(%rax)
 46f:	c5 45 db c5          	vpand  %ymm5,%ymm7,%ymm8
 473:	c5 c5 72 d7 0c       	vpsrld $0xc,%ymm7,%ymm7
 478:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 47c:	c5 c5 db fc          	vpand  %ymm4,%ymm7,%ymm7
 480:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 484:	c5 ed fe ff          	vpaddd %ymm7,%ymm2,%ymm7
 488:	c4 c1 7d fe c0       	vpaddd %ymm8,%ymm0,%ymm0
 48d:	c4 c1 45 fe f8       	vpaddd %ymm8,%ymm7,%ymm7
 492:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 497:	c5 c5 72 f7 10       	vpslld $0x10,%ymm7,%ymm7
 49c:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
 4a0:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 4a5:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 4aa:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
 4ae:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 4b4:	c5 c1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm7
 4b9:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 4be:	c4 c1 41 eb f8       	vpor   %xmm8,%xmm7,%xmm7
 4c3:	c5 f9 d6 40 e0       	vmovq  %xmm0,-0x20(%rax)
 4c8:	c5 fd 72 d6 08       	vpsrld $0x8,%ymm6,%ymm0
 4cd:	c5 fa 7f 78 d0       	vmovdqu %xmm7,-0x30(%rax)
 4d2:	c5 cd db fd          	vpand  %ymm5,%ymm6,%ymm7
 4d6:	c5 cd 72 d6 0c       	vpsrld $0xc,%ymm6,%ymm6
 4db:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 4df:	c5 cd db f4          	vpand  %ymm4,%ymm6,%ymm6
 4e3:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 4e7:	c5 ed fe f6          	vpaddd %ymm6,%ymm2,%ymm6
 4eb:	c5 fd fe c7          	vpaddd %ymm7,%ymm0,%ymm0
 4ef:	c5 cd fe f7          	vpaddd %ymm7,%ymm6,%ymm6
 4f3:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 4f8:	c5 cd 72 f6 10       	vpslld $0x10,%ymm6,%ymm6
 4fd:	c5 fd eb c6          	vpor   %ymm6,%ymm0,%ymm0
 501:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
 505:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 50a:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 50e:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 514:	c5 c9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm6
 519:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 51e:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 522:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 527:	c5 fa 7f 70 e8       	vmovdqu %xmm6,-0x18(%rax)
 52c:	4c 39 c8             	cmp    %r9,%rax
 52f:	0f 85 33 fb ff ff    	jne    68 <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x68>
 535:	48 83 e1 e0          	and    $0xffffffffffffffe0,%rcx
 539:	48 83 c1 20          	add    $0x20,%rcx
 53d:	4c 39 c1             	cmp    %r8,%rcx
 540:	0f 83 70 01 00 00    	jae    6b6 <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x6b6>
 546:	49 ff c8             	dec    %r8
 549:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
 54d:	c5 dd 76 e4          	vpcmpeqd %ymm4,%ymm4,%ymm4
 551:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 559 <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x559>
 558:	00 
 559:	49 29 c8             	sub    %rcx,%r8
 55c:	c5 d5 72 d4 18       	vpsrld $0x18,%ymm4,%ymm5
 561:	4c 8d 0c 06          	lea    (%rsi,%rax,1),%r9
 565:	49 c1 e8 03          	shr    $0x3,%r8
 569:	c5 dd 72 d4 1c       	vpsrld $0x1c,%ymm4,%ymm4
 56e:	48 8d 44 06 18       	lea    0x18(%rsi,%rax,1),%rax
 573:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
 577:	48 8d 34 d0          	lea    (%rax,%rdx,8),%rsi
 57b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 580:	49 8b 01             	mov    (%r9),%rax
 583:	49 8b 59 08          	mov    0x8(%r9),%rbx
 587:	49 83 c1 18          	add    $0x18,%r9
 58b:	4d 8b 41 f8          	mov    -0x8(%r9),%r8
 58f:	48 0f c8             	bswap  %rax
 592:	89 c2                	mov    %eax,%edx
 594:	48 89 d9             	mov    %rbx,%rcx
 597:	0f b6 db             	movzbl %bl,%ebx
 59a:	c1 e2 08             	shl    $0x8,%edx
 59d:	48 0f c9             	bswap  %rcx
 5a0:	49 0f c8             	bswap  %r8
 5a3:	49 89 c3             	mov    %rax,%r11
 5a6:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
 5ac:	49 89 c2             	mov    %rax,%r10
 5af:	41 89 cc             	mov    %ecx,%r12d
 5b2:	4c 89 c0             	mov    %r8,%rax
 5b5:	48 c1 e8 30          	shr    $0x30,%rax
 5b9:	48 09 da             	or     %rbx,%rdx
 5bc:	48 89 cb             	mov    %rcx,%rbx
 5bf:	c1 e1 10             	shl    $0x10,%ecx
 5c2:	49 c1 eb 28          	shr    $0x28,%r11
 5c6:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 5cc:	4d 89 c5             	mov    %r8,%r13
 5cf:	41 c1 ec 08          	shr    $0x8,%r12d
 5d3:	49 c1 ed 18          	shr    $0x18,%r13
 5d7:	48 09 c1             	or     %rax,%rcx
 5da:	42 0f b7 04 5f       	movzwl (%rdi,%r11,2),%eax
 5df:	49 c1 ea 10          	shr    $0x10,%r10
 5e3:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 5ea:	48 c1 eb 20          	shr    $0x20,%rbx
 5ee:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 5f5:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
 5fc:	c5 f9 6e f0          	vmovd  %eax,%xmm6
 600:	0f b7 04 57          	movzwl (%rdi,%rdx,2),%eax
 604:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
 60a:	c4 a1 49 c4 34 57 01 	vpinsrw $0x1,(%rdi,%r10,2),%xmm6,%xmm6
 611:	c5 79 6e c0          	vmovd  %eax,%xmm8
 615:	42 0f b7 04 67       	movzwl (%rdi,%r12,2),%eax
 61a:	c5 39 c4 04 5f 01    	vpinsrw $0x1,(%rdi,%rbx,2),%xmm8,%xmm8
 620:	c5 f9 6e c0          	vmovd  %eax,%xmm0
 624:	42 0f b7 04 6f       	movzwl (%rdi,%r13,2),%eax
 629:	c5 f9 c4 04 4f 01    	vpinsrw $0x1,(%rdi,%rcx,2),%xmm0,%xmm0
 62f:	c4 c1 49 62 f0       	vpunpckldq %xmm8,%xmm6,%xmm6
 634:	c5 f9 6e f8          	vmovd  %eax,%xmm7
 638:	c4 a1 41 c4 3c 47 01 	vpinsrw $0x1,(%rdi,%r8,2),%xmm7,%xmm7
 63f:	c5 f9 62 c7          	vpunpckldq %xmm7,%xmm0,%xmm0
 643:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
 647:	c4 e2 7d 33 f6       	vpmovzxwd %xmm6,%ymm6
 64c:	c5 cd db fd          	vpand  %ymm5,%ymm6,%ymm7
 650:	c5 fd 72 d6 08       	vpsrld $0x8,%ymm6,%ymm0
 655:	c5 cd 72 d6 0c       	vpsrld $0xc,%ymm6,%ymm6
 65a:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 65e:	c5 cd db f4          	vpand  %ymm4,%ymm6,%ymm6
 662:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 666:	c5 ed fe f6          	vpaddd %ymm6,%ymm2,%ymm6
 66a:	c5 fd fe c7          	vpaddd %ymm7,%ymm0,%ymm0
 66e:	c5 cd fe f7          	vpaddd %ymm7,%ymm6,%ymm6
 672:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 677:	c5 cd 72 f6 10       	vpslld $0x10,%ymm6,%ymm6
 67c:	c5 fd eb c6          	vpor   %ymm6,%ymm0,%ymm0
 680:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
 684:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 689:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 68d:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 693:	c5 c9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm6
 698:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 69d:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 6a1:	c4 c1 79 d6 41 f8    	vmovq  %xmm0,-0x8(%r9)
 6a7:	c4 c1 7a 7f 71 e8    	vmovdqu %xmm6,-0x18(%r9)
 6ad:	49 39 f1             	cmp    %rsi,%r9
 6b0:	0f 85 ca fe ff ff    	jne    580 <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x580>
 6b6:	c5 f8 77             	vzeroupper
 6b9:	5b                   	pop    %rbx
 6ba:	41 5c                	pop    %r12
 6bc:	41 5d                	pop    %r13
 6be:	41 5e                	pop    %r14
 6c0:	41 5f                	pop    %r15
 6c2:	5d                   	pop    %rbp
 6c3:	c3                   	ret
 6c4:	0f 1f 40 00          	nopl   0x0(%rax)
 6c8:	31 c9                	xor    %ecx,%ecx
 6ca:	e9 6e fe ff ff       	jmp    53d <jshc_channel::avx2_chain_load16(unsigned int const*, int, int, unsigned char*, unsigned long)+0x53d>
 6cf:	90                   	nop

00000000000006d0 <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)>:
 6d0:	f3 0f 1e fa          	endbr64
 6d4:	55                   	push   %rbp
 6d5:	c5 f9 6e ce          	vmovd  %esi,%xmm1
 6d9:	c5 f9 6e d2          	vmovd  %edx,%xmm2
 6dd:	48 89 c8             	mov    %rcx,%rax
 6e0:	c4 e2 7d 58 c9       	vpbroadcastd %xmm1,%ymm1
 6e5:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
 6ea:	48 89 e5             	mov    %rsp,%rbp
 6ed:	41 57                	push   %r15
 6ef:	41 56                	push   %r14
 6f1:	41 55                	push   %r13
 6f3:	41 54                	push   %r12
 6f5:	53                   	push   %rbx
 6f6:	4c 89 c3             	mov    %r8,%rbx
 6f9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
 6fd:	49 83 f9 1f          	cmp    $0x1f,%r9
 701:	0f 86 a9 06 00 00    	jbe    db0 <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x6e0>
 707:	4d 8d 51 e0          	lea    -0x20(%r9),%r10
 70b:	48 89 ca             	mov    %rcx,%rdx
 70e:	48 89 44 24 f0       	mov    %rax,-0x10(%rsp)
 713:	c5 dd 76 e4          	vpcmpeqd %ymm4,%ymm4,%ymm4
 717:	4c 89 d1             	mov    %r10,%rcx
 71a:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
 71f:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 727 <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x57>
 726:	00 
 727:	4c 89 c6             	mov    %r8,%rsi
 72a:	48 c1 e9 05          	shr    $0x5,%rcx
 72e:	c5 d5 72 d4 18       	vpsrld $0x18,%ymm4,%ymm5
 733:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
 737:	c5 dd 72 d4 1c       	vpsrld $0x1c,%ymm4,%ymm4
 73c:	48 c1 e1 05          	shl    $0x5,%rcx
 740:	4c 8d 44 08 60       	lea    0x60(%rax,%rcx,1),%r8
 745:	0f 1f 00             	nopl   (%rax)
 748:	48 8b 02             	mov    (%rdx),%rax
 74b:	4c 8b 5a 08          	mov    0x8(%rdx),%r11
 74f:	4c 8b 52 10          	mov    0x10(%rdx),%r10
 753:	48 0f c8             	bswap  %rax
 756:	49 89 c6             	mov    %rax,%r14
 759:	49 89 c4             	mov    %rax,%r12
 75c:	c1 e0 08             	shl    $0x8,%eax
 75f:	49 0f ca             	bswap  %r10
 762:	4c 89 d9             	mov    %r11,%rcx
 765:	25 00 ff ff 00       	and    $0xffff00,%eax
 76a:	45 0f b6 db          	movzbl %r11b,%r11d
 76e:	48 0f c9             	bswap  %rcx
 771:	4c 09 d8             	or     %r11,%rax
 774:	41 89 cd             	mov    %ecx,%r13d
 777:	49 89 cb             	mov    %rcx,%r11
 77a:	c1 e1 10             	shl    $0x10,%ecx
 77d:	4d 89 d7             	mov    %r10,%r15
 780:	0f b7 04 47          	movzwl (%rdi,%rax,2),%eax
 784:	41 c1 ed 08          	shr    $0x8,%r13d
 788:	49 c1 ef 30          	shr    $0x30,%r15
 78c:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 792:	49 c1 ee 28          	shr    $0x28,%r14
 796:	4c 09 f9             	or     %r15,%rcx
 799:	4d 89 d7             	mov    %r10,%r15
 79c:	c5 f9 6e f8          	vmovd  %eax,%xmm7
 7a0:	42 0f b7 04 6f       	movzwl (%rdi,%r13,2),%eax
 7a5:	49 c1 ef 18          	shr    $0x18,%r15
 7a9:	46 0f b7 34 77       	movzwl (%rdi,%r14,2),%r14d
 7ae:	49 c1 eb 20          	shr    $0x20,%r11
 7b2:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 7b9:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 7c0:	c5 f9 6e c0          	vmovd  %eax,%xmm0
 7c4:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 7cb:	49 c1 ec 10          	shr    $0x10,%r12
 7cf:	42 0f b7 04 7f       	movzwl (%rdi,%r15,2),%eax
 7d4:	c4 a1 41 c4 3c 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm7,%xmm7
 7db:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 7e2:	c4 41 79 6e ce       	vmovd  %r14d,%xmm9
 7e7:	4c 8b 5a 20          	mov    0x20(%rdx),%r11
 7eb:	c4 21 31 c4 0c 67 01 	vpinsrw $0x1,(%rdi,%r12,2),%xmm9,%xmm9
 7f2:	c5 f9 6e f0          	vmovd  %eax,%xmm6
 7f6:	48 8b 42 18          	mov    0x18(%rdx),%rax
 7fa:	c5 f9 c4 04 4f 01    	vpinsrw $0x1,(%rdi,%rcx,2),%xmm0,%xmm0
 800:	c4 a1 49 c4 34 57 01 	vpinsrw $0x1,(%rdi,%r10,2),%xmm6,%xmm6
 807:	4c 8b 52 28          	mov    0x28(%rdx),%r10
 80b:	4c 89 d9             	mov    %r11,%rcx
 80e:	45 0f b6 db          	movzbl %r11b,%r11d
 812:	48 0f c8             	bswap  %rax
 815:	49 89 c6             	mov    %rax,%r14
 818:	49 89 c4             	mov    %rax,%r12
 81b:	c1 e0 08             	shl    $0x8,%eax
 81e:	25 00 ff ff 00       	and    $0xffff00,%eax
 823:	48 0f c9             	bswap  %rcx
 826:	49 0f ca             	bswap  %r10
 829:	41 89 cd             	mov    %ecx,%r13d
 82c:	4c 09 d8             	or     %r11,%rax
 82f:	4d 89 d7             	mov    %r10,%r15
 832:	49 89 cb             	mov    %rcx,%r11
 835:	c1 e1 10             	shl    $0x10,%ecx
 838:	0f b7 04 47          	movzwl (%rdi,%rax,2),%eax
 83c:	49 c1 ef 30          	shr    $0x30,%r15
 840:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 846:	41 c1 ed 08          	shr    $0x8,%r13d
 84a:	4c 09 f9             	or     %r15,%rcx
 84d:	4d 89 d7             	mov    %r10,%r15
 850:	c5 31 62 cf          	vpunpckldq %xmm7,%xmm9,%xmm9
 854:	49 c1 ee 28          	shr    $0x28,%r14
 858:	49 c1 ef 18          	shr    $0x18,%r15
 85c:	c5 f9 6e f8          	vmovd  %eax,%xmm7
 860:	42 0f b7 04 6f       	movzwl (%rdi,%r13,2),%eax
 865:	c5 f9 62 c6          	vpunpckldq %xmm6,%xmm0,%xmm0
 869:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 870:	c5 31 6c c8          	vpunpcklqdq %xmm0,%xmm9,%xmm9
 874:	46 0f b7 34 77       	movzwl (%rdi,%r14,2),%r14d
 879:	49 c1 eb 20          	shr    $0x20,%r11
 87d:	c5 f9 6e c0          	vmovd  %eax,%xmm0
 881:	42 0f b7 04 7f       	movzwl (%rdi,%r15,2),%eax
 886:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 88d:	49 c1 ec 10          	shr    $0x10,%r12
 891:	c4 a1 41 c4 3c 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm7,%xmm7
 898:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 89f:	4c 8b 5a 38          	mov    0x38(%rdx),%r11
 8a3:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 8aa:	c5 f9 6e f0          	vmovd  %eax,%xmm6
 8ae:	48 8b 42 30          	mov    0x30(%rdx),%rax
 8b2:	c4 41 79 6e c6       	vmovd  %r14d,%xmm8
 8b7:	c5 f9 c4 04 4f 01    	vpinsrw $0x1,(%rdi,%rcx,2),%xmm0,%xmm0
 8bd:	c4 a1 49 c4 34 57 01 	vpinsrw $0x1,(%rdi,%r10,2),%xmm6,%xmm6
 8c4:	c4 21 39 c4 04 67 01 	vpinsrw $0x1,(%rdi,%r12,2),%xmm8,%xmm8
 8cb:	c4 42 7d 33 c9       	vpmovzxwd %xmm9,%ymm9
 8d0:	4c 89 d9             	mov    %r11,%rcx
 8d3:	48 0f c8             	bswap  %rax
 8d6:	49 89 c6             	mov    %rax,%r14
 8d9:	4c 8b 52 40          	mov    0x40(%rdx),%r10
 8dd:	49 89 c4             	mov    %rax,%r12
 8e0:	49 c1 ee 28          	shr    $0x28,%r14
 8e4:	c1 e0 08             	shl    $0x8,%eax
 8e7:	45 0f b6 db          	movzbl %r11b,%r11d
 8eb:	48 0f c9             	bswap  %rcx
 8ee:	25 00 ff ff 00       	and    $0xffff00,%eax
 8f3:	49 0f ca             	bswap  %r10
 8f6:	41 89 cd             	mov    %ecx,%r13d
 8f9:	4d 89 d7             	mov    %r10,%r15
 8fc:	4c 09 d8             	or     %r11,%rax
 8ff:	49 89 cb             	mov    %rcx,%r11
 902:	c1 e1 10             	shl    $0x10,%ecx
 905:	c5 f9 62 c6          	vpunpckldq %xmm6,%xmm0,%xmm0
 909:	0f b7 04 47          	movzwl (%rdi,%rax,2),%eax
 90d:	49 c1 ef 30          	shr    $0x30,%r15
 911:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 917:	41 c1 ed 08          	shr    $0x8,%r13d
 91b:	4c 09 f9             	or     %r15,%rcx
 91e:	4d 89 d7             	mov    %r10,%r15
 921:	c5 39 62 c7          	vpunpckldq %xmm7,%xmm8,%xmm8
 925:	46 0f b7 34 77       	movzwl (%rdi,%r14,2),%r14d
 92a:	49 c1 ef 18          	shr    $0x18,%r15
 92e:	c5 79 6e d0          	vmovd  %eax,%xmm10
 932:	42 0f b7 04 6f       	movzwl (%rdi,%r13,2),%eax
 937:	c5 39 6c c0          	vpunpcklqdq %xmm0,%xmm8,%xmm8
 93b:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 942:	49 c1 ec 10          	shr    $0x10,%r12
 946:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 94d:	c4 c1 79 6e fe       	vmovd  %r14d,%xmm7
 952:	c5 f9 6e c0          	vmovd  %eax,%xmm0
 956:	42 0f b7 04 7f       	movzwl (%rdi,%r15,2),%eax
 95b:	49 c1 eb 20          	shr    $0x20,%r11
 95f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 966:	c4 a1 41 c4 3c 67 01 	vpinsrw $0x1,(%rdi,%r12,2),%xmm7,%xmm7
 96d:	c5 f9 c4 04 4f 01    	vpinsrw $0x1,(%rdi,%rcx,2),%xmm0,%xmm0
 973:	c4 42 7d 33 c0       	vpmovzxwd %xmm8,%ymm8
 978:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 97f:	c5 f9 6e f0          	vmovd  %eax,%xmm6
 983:	c4 21 29 c4 14 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm10,%xmm10
 98a:	c4 a1 49 c4 34 57 01 	vpinsrw $0x1,(%rdi,%r10,2),%xmm6,%xmm6
 991:	48 8b 42 48          	mov    0x48(%rdx),%rax
 995:	4c 8b 5a 50          	mov    0x50(%rdx),%r11
 999:	4c 8b 52 58          	mov    0x58(%rdx),%r10
 99d:	c4 c1 41 62 fa       	vpunpckldq %xmm10,%xmm7,%xmm7
 9a2:	48 0f c8             	bswap  %rax
 9a5:	49 89 c6             	mov    %rax,%r14
 9a8:	49 89 c4             	mov    %rax,%r12
 9ab:	c1 e0 08             	shl    $0x8,%eax
 9ae:	4c 89 d9             	mov    %r11,%rcx
 9b1:	25 00 ff ff 00       	and    $0xffff00,%eax
 9b6:	45 0f b6 db          	movzbl %r11b,%r11d
 9ba:	49 0f ca             	bswap  %r10
 9bd:	4c 09 d8             	or     %r11,%rax
 9c0:	48 0f c9             	bswap  %rcx
 9c3:	4d 89 d7             	mov    %r10,%r15
 9c6:	49 89 cb             	mov    %rcx,%r11
 9c9:	41 89 cd             	mov    %ecx,%r13d
 9cc:	c1 e1 10             	shl    $0x10,%ecx
 9cf:	0f b7 04 47          	movzwl (%rdi,%rax,2),%eax
 9d3:	c5 f9 62 c6          	vpunpckldq %xmm6,%xmm0,%xmm0
 9d7:	49 c1 ef 30          	shr    $0x30,%r15
 9db:	81 e1 00 00 ff 00    	and    $0xff0000,%ecx
 9e1:	41 c1 ed 08          	shr    $0x8,%r13d
 9e5:	c5 c1 6c f8          	vpunpcklqdq %xmm0,%xmm7,%xmm7
 9e9:	4c 09 f9             	or     %r15,%rcx
 9ec:	4d 89 d7             	mov    %r10,%r15
 9ef:	c5 79 6e d8          	vmovd  %eax,%xmm11
 9f3:	42 0f b7 04 6f       	movzwl (%rdi,%r13,2),%eax
 9f8:	49 c1 ef 18          	shr    $0x18,%r15
 9fc:	49 c1 ee 28          	shr    $0x28,%r14
 a00:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 a07:	c4 e2 7d 33 ff       	vpmovzxwd %xmm7,%ymm7
 a0c:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
 a13:	46 0f b7 34 77       	movzwl (%rdi,%r14,2),%r14d
 a18:	c5 f9 6e c0          	vmovd  %eax,%xmm0
 a1c:	49 c1 ec 10          	shr    $0x10,%r12
 a20:	42 0f b7 04 7f       	movzwl (%rdi,%r15,2),%eax
 a25:	49 c1 eb 20          	shr    $0x20,%r11
 a29:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 a30:	c5 f9 c4 04 4f 01    	vpinsrw $0x1,(%rdi,%rcx,2),%xmm0,%xmm0
 a36:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
 a3d:	c4 c1 79 6e f6       	vmovd  %r14d,%xmm6
 a42:	48 83 c2 60          	add    $0x60,%rdx
 a46:	48 83 c6 60          	add    $0x60,%rsi
 a4a:	c5 79 6e d0          	vmovd  %eax,%xmm10
 a4e:	c4 a1 49 c4 34 67 01 	vpinsrw $0x1,(%rdi,%r12,2),%xmm6,%xmm6
 a55:	c4 21 21 c4 1c 5f 01 	vpinsrw $0x1,(%rdi,%r11,2),%xmm11,%xmm11
 a5c:	c4 21 29 c4 14 57 01 	vpinsrw $0x1,(%rdi,%r10,2),%xmm10,%xmm10
 a63:	c4 c1 49 62 f3       	vpunpckldq %xmm11,%xmm6,%xmm6
 a68:	c4 c1 79 62 c2       	vpunpckldq %xmm10,%xmm0,%xmm0
 a6d:	c5 35 db d5          	vpand  %ymm5,%ymm9,%ymm10
 a71:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
 a75:	c4 c1 7d 72 d1 08    	vpsrld $0x8,%ymm9,%ymm0
 a7b:	c4 c1 35 72 d1 0c    	vpsrld $0xc,%ymm9,%ymm9
 a81:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 a85:	c4 e2 7d 33 f6       	vpmovzxwd %xmm6,%ymm6
 a8a:	c5 35 db cc          	vpand  %ymm4,%ymm9,%ymm9
 a8e:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 a92:	c4 41 6d fe c9       	vpaddd %ymm9,%ymm2,%ymm9
 a97:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
 a9c:	c4 41 35 fe ca       	vpaddd %ymm10,%ymm9,%ymm9
 aa1:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 aa6:	c4 c1 35 72 f1 10    	vpslld $0x10,%ymm9,%ymm9
 aac:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 ab1:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 ab6:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 abb:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
 abf:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 ac5:	c5 b1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm9
 aca:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 acf:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 ad4:	c5 f9 d6 46 b0       	vmovq  %xmm0,-0x50(%rsi)
 ad9:	c4 c1 7d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm0
 adf:	c5 7a 7f 4e a0       	vmovdqu %xmm9,-0x60(%rsi)
 ae4:	c5 3d db cd          	vpand  %ymm5,%ymm8,%ymm9
 ae8:	c4 c1 3d 72 d0 0c    	vpsrld $0xc,%ymm8,%ymm8
 aee:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 af2:	c5 3d db c4          	vpand  %ymm4,%ymm8,%ymm8
 af6:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 afa:	c4 41 6d fe c0       	vpaddd %ymm8,%ymm2,%ymm8
 aff:	c4 c1 7d fe c1       	vpaddd %ymm9,%ymm0,%ymm0
 b04:	c4 41 3d fe c1       	vpaddd %ymm9,%ymm8,%ymm8
 b09:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 b0e:	c4 c1 3d 72 f0 10    	vpslld $0x10,%ymm8,%ymm8
 b14:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 b19:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 b1e:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 b23:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 b27:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 b2d:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 b32:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 b37:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 b3c:	c5 f9 d6 46 c8       	vmovq  %xmm0,-0x38(%rsi)
 b41:	c5 fd 72 d7 08       	vpsrld $0x8,%ymm7,%ymm0
 b46:	c5 7a 7f 46 b8       	vmovdqu %xmm8,-0x48(%rsi)
 b4b:	c5 45 db c5          	vpand  %ymm5,%ymm7,%ymm8
 b4f:	c5 c5 72 d7 0c       	vpsrld $0xc,%ymm7,%ymm7
 b54:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 b58:	c5 c5 db fc          	vpand  %ymm4,%ymm7,%ymm7
 b5c:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 b60:	c5 ed fe ff          	vpaddd %ymm7,%ymm2,%ymm7
 b64:	c4 c1 7d fe c0       	vpaddd %ymm8,%ymm0,%ymm0
 b69:	c4 c1 45 fe f8       	vpaddd %ymm8,%ymm7,%ymm7
 b6e:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 b73:	c5 c5 72 f7 10       	vpslld $0x10,%ymm7,%ymm7
 b78:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
 b7c:	c4 c1 7d eb c0       	vpor   %ymm8,%ymm0,%ymm0
 b81:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 b86:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
 b8a:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 b90:	c5 c1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm7
 b95:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 b9a:	c4 c1 41 eb f8       	vpor   %xmm8,%xmm7,%xmm7
 b9f:	c5 f9 d6 46 e0       	vmovq  %xmm0,-0x20(%rsi)
 ba4:	c5 fd 72 d6 08       	vpsrld $0x8,%ymm6,%ymm0
 ba9:	c5 fa 7f 7e d0       	vmovdqu %xmm7,-0x30(%rsi)
 bae:	c5 cd db fd          	vpand  %ymm5,%ymm6,%ymm7
 bb2:	c5 cd 72 d6 0c       	vpsrld $0xc,%ymm6,%ymm6
 bb7:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 bbb:	c5 cd db f4          	vpand  %ymm4,%ymm6,%ymm6
 bbf:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 bc3:	c5 ed fe f6          	vpaddd %ymm6,%ymm2,%ymm6
 bc7:	c5 fd fe c7          	vpaddd %ymm7,%ymm0,%ymm0
 bcb:	c5 cd fe f7          	vpaddd %ymm7,%ymm6,%ymm6
 bcf:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 bd4:	c5 cd 72 f6 10       	vpslld $0x10,%ymm6,%ymm6
 bd9:	c5 fd eb c6          	vpor   %ymm6,%ymm0,%ymm0
 bdd:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
 be1:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 be6:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 bea:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 bf0:	c5 c9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm6
 bf5:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 bfa:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 bfe:	c5 f9 d6 46 f8       	vmovq  %xmm0,-0x8(%rsi)
 c03:	c5 fa 7f 76 e8       	vmovdqu %xmm6,-0x18(%rsi)
 c08:	4c 39 c2             	cmp    %r8,%rdx
 c0b:	0f 85 37 fb ff ff    	jne    748 <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x78>
 c11:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
 c16:	48 8b 44 24 f0       	mov    -0x10(%rsp),%rax
 c1b:	49 83 e2 e0          	and    $0xffffffffffffffe0,%r10
 c1f:	49 83 c2 20          	add    $0x20,%r10
 c23:	4d 39 ca             	cmp    %r9,%r10
 c26:	0f 83 72 01 00 00    	jae    d9e <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x6ce>
 c2c:	49 ff c9             	dec    %r9
 c2f:	4b 8d 14 52          	lea    (%r10,%r10,2),%rdx
 c33:	c5 dd 76 e4          	vpcmpeqd %ymm4,%ymm4,%ymm4
 c37:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # c3f <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x56f>
 c3e:	00 
 c3f:	48 8d 34 10          	lea    (%rax,%rdx,1),%rsi
 c43:	48 8d 44 10 18       	lea    0x18(%rax,%rdx,1),%rax
 c48:	c5 d5 72 d4 18       	vpsrld $0x18,%ymm4,%ymm5
 c4d:	4d 29 d1             	sub    %r10,%r9
 c50:	49 c1 e9 03          	shr    $0x3,%r9
 c54:	c5 dd 72 d4 1c       	vpsrld $0x1c,%ymm4,%ymm4
 c59:	4c 8d 04 13          	lea    (%rbx,%rdx,1),%r8
 c5d:	4b 8d 0c 49          	lea    (%r9,%r9,2),%rcx
 c61:	4c 8d 0c c8          	lea    (%rax,%rcx,8),%r9
 c65:	0f 1f 00             	nopl   (%rax)
 c68:	48 8b 16             	mov    (%rsi),%rdx
 c6b:	48 8b 5e 08          	mov    0x8(%rsi),%rbx
 c6f:	48 83 c6 18          	add    $0x18,%rsi
 c73:	49 83 c0 18          	add    $0x18,%r8
 c77:	48 8b 4e f8          	mov    -0x8(%rsi),%rcx
 c7b:	48 0f ca             	bswap  %rdx
 c7e:	49 89 d3             	mov    %rdx,%r11
 c81:	49 89 d2             	mov    %rdx,%r10
 c84:	c1 e2 08             	shl    $0x8,%edx
 c87:	48 0f c9             	bswap  %rcx
 c8a:	48 89 d8             	mov    %rbx,%rax
 c8d:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
 c93:	0f b6 db             	movzbl %bl,%ebx
 c96:	48 0f c8             	bswap  %rax
 c99:	48 09 da             	or     %rbx,%rdx
 c9c:	41 89 c4             	mov    %eax,%r12d
 c9f:	48 89 c3             	mov    %rax,%rbx
 ca2:	0f b7 14 57          	movzwl (%rdi,%rdx,2),%edx
 ca6:	c1 e0 10             	shl    $0x10,%eax
 ca9:	49 89 cd             	mov    %rcx,%r13
 cac:	41 c1 ec 08          	shr    $0x8,%r12d
 cb0:	49 c1 ed 30          	shr    $0x30,%r13
 cb4:	25 00 00 ff 00       	and    $0xff0000,%eax
 cb9:	49 c1 eb 28          	shr    $0x28,%r11
 cbd:	4c 09 e8             	or     %r13,%rax
 cc0:	c5 79 6e c2          	vmovd  %edx,%xmm8
 cc4:	49 89 cd             	mov    %rcx,%r13
 cc7:	42 0f b7 14 67       	movzwl (%rdi,%r12,2),%edx
 ccc:	49 c1 ed 18          	shr    $0x18,%r13
 cd0:	46 0f b7 1c 5f       	movzwl (%rdi,%r11,2),%r11d
 cd5:	49 c1 ea 10          	shr    $0x10,%r10
 cd9:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 cdf:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
 ce6:	c5 f9 6e c2          	vmovd  %edx,%xmm0
 cea:	48 c1 eb 20          	shr    $0x20,%rbx
 cee:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 cf5:	c5 f9 c4 04 47 01    	vpinsrw $0x1,(%rdi,%rax,2),%xmm0,%xmm0
 cfb:	42 0f b7 04 6f       	movzwl (%rdi,%r13,2),%eax
 d00:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
 d06:	c4 c1 79 6e f3       	vmovd  %r11d,%xmm6
 d0b:	c4 a1 49 c4 34 57 01 	vpinsrw $0x1,(%rdi,%r10,2),%xmm6,%xmm6
 d12:	c5 39 c4 04 5f 01    	vpinsrw $0x1,(%rdi,%rbx,2),%xmm8,%xmm8
 d18:	c5 f9 6e f8          	vmovd  %eax,%xmm7
 d1c:	c5 c1 c4 3c 4f 01    	vpinsrw $0x1,(%rdi,%rcx,2),%xmm7,%xmm7
 d22:	c4 c1 49 62 f0       	vpunpckldq %xmm8,%xmm6,%xmm6
 d27:	c5 f9 62 c7          	vpunpckldq %xmm7,%xmm0,%xmm0
 d2b:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
 d2f:	c4 e2 7d 33 f6       	vpmovzxwd %xmm6,%ymm6
 d34:	c5 cd db fd          	vpand  %ymm5,%ymm6,%ymm7
 d38:	c5 fd 72 d6 08       	vpsrld $0x8,%ymm6,%ymm0
 d3d:	c5 cd 72 d6 0c       	vpsrld $0xc,%ymm6,%ymm6
 d42:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
 d46:	c5 cd db f4          	vpand  %ymm4,%ymm6,%ymm6
 d4a:	c5 f5 fe c0          	vpaddd %ymm0,%ymm1,%ymm0
 d4e:	c5 ed fe f6          	vpaddd %ymm6,%ymm2,%ymm6
 d52:	c5 fd fe c7          	vpaddd %ymm7,%ymm0,%ymm0
 d56:	c5 cd fe f7          	vpaddd %ymm7,%ymm6,%ymm6
 d5a:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 d5f:	c5 cd 72 f6 10       	vpslld $0x10,%ymm6,%ymm6
 d64:	c5 fd eb c6          	vpor   %ymm6,%ymm0,%ymm0
 d68:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
 d6c:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 d71:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 d75:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 d7b:	c5 c9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm6
 d80:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 d85:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 d89:	c4 c1 79 d6 40 f8    	vmovq  %xmm0,-0x8(%r8)
 d8f:	c4 c1 7a 7f 70 e8    	vmovdqu %xmm6,-0x18(%r8)
 d95:	4c 39 ce             	cmp    %r9,%rsi
 d98:	0f 85 ca fe ff ff    	jne    c68 <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x598>
 d9e:	c5 f8 77             	vzeroupper
 da1:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
 da5:	5b                   	pop    %rbx
 da6:	41 5c                	pop    %r12
 da8:	41 5d                	pop    %r13
 daa:	41 5e                	pop    %r14
 dac:	41 5f                	pop    %r15
 dae:	5d                   	pop    %rbp
 daf:	c3                   	ret
 db0:	45 31 d2             	xor    %r10d,%r10d
 db3:	e9 6b fe ff ff       	jmp    c23 <jshc_channel::avx2_chain_load16_to(unsigned int const*, int, int, unsigned char const*, unsigned char*, unsigned long)+0x553>
