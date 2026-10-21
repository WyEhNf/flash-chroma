
artifacts/skylake-vectorwide-linux-build-v1/CMakeFiles/jshc_skylake_vectorwide.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 53 0e 00 00    	je     e60 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe60>
       d:	55                   	push   %rbp
       e:	b8 00 04 00 00       	mov    $0x400,%eax
      13:	4c 8d 04 49          	lea    (%rcx,%rcx,2),%r8
      17:	49 39 c0             	cmp    %rax,%r8
      1a:	4c 0f 47 c0          	cmova  %rax,%r8
      1e:	31 c0                	xor    %eax,%eax
      20:	48 89 e5             	mov    %rsp,%rbp
      23:	41 57                	push   %r15
      25:	41 56                	push   %r14
      27:	41 55                	push   %r13
      29:	41 54                	push   %r12
      2b:	53                   	push   %rbx
      2c:	0f 1f 40 00          	nopl   0x0(%rax)
      30:	0f 18 04 02          	prefetchnta (%rdx,%rax,1)
      34:	48 83 c0 40          	add    $0x40,%rax
      38:	4c 39 c0             	cmp    %r8,%rax
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
      45:	0f 1f 00             	nopl   (%rax)
      48:	41 0f b6 40 01       	movzbl 0x1(%r8),%eax
      4d:	45 0f b6 50 02       	movzbl 0x2(%r8),%r10d
      52:	49 ff c1             	inc    %r9
      55:	49 83 c0 03          	add    $0x3,%r8
      59:	41 c1 e2 10          	shl    $0x10,%r10d
      5d:	c1 e0 08             	shl    $0x8,%eax
      60:	44 09 d0             	or     %r10d,%eax
      63:	45 0f b6 50 fd       	movzbl -0x3(%r8),%r10d
      68:	44 09 d0             	or     %r10d,%eax
      6b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
      6f:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
      73:	41 8b 02             	mov    (%r10),%eax
      76:	45 0f b7 12          	movzwl (%r10),%r10d
      7a:	c1 e8 10             	shr    $0x10,%eax
      7d:	66 45 89 50 fd       	mov    %r10w,-0x3(%r8)
      82:	41 88 40 ff          	mov    %al,-0x1(%r8)
      86:	4c 39 c9             	cmp    %r9,%rcx
      89:	0f 84 c1 0d 00 00    	je     e50 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 bf 0d 00 00    	jb     e61 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe61>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # ae <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # b6 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # be <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbe>
      bd:	00 
      be:	48 01 d0             	add    %rdx,%rax
      c1:	eb 08                	jmp    cb <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcb>
      c3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      c8:	4d 89 c1             	mov    %r8,%r9
      cb:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      d2:	4c 39 c1             	cmp    %r8,%rcx
      d5:	72 1c                	jb     f3 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf3>
      d7:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      de:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      e5:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
      ec:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
      f3:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
      f7:	48 05 c0 00 00 00    	add    $0xc0,%rax
      fd:	c4 e3 7d 38 80 4c ff 	vinserti128 $0x1,-0xb4(%rax),%ymm0,%ymm0
     104:	ff ff 01 
     107:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     10c:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     112:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     117:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     11d:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     122:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     128:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     12d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     132:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     137:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     13c:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     142:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     148:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     14d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     152:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     158:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     15e:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     164:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     16a:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     16f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     174:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     17b:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     182:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     188:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     18c:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     191:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     198:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     19f:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     1a3:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     1a9:	c5 fa 6f 80 58 ff ff 	vmovdqu -0xa8(%rax),%xmm0
     1b0:	ff 
     1b1:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     1b6:	c4 e3 7d 38 80 64 ff 	vinserti128 $0x1,-0x9c(%rax),%ymm0,%ymm0
     1bd:	ff ff 01 
     1c0:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
     1c5:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     1ca:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     1d0:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     1d5:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     1db:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     1e0:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     1e6:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     1eb:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     1f0:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     1f5:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     1fa:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     200:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     206:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     20b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     210:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     216:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     21c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     222:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     228:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     22d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     232:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     239:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     240:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     244:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     249:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     24f:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     256:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     25d:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     261:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     267:	c5 fa 6f 80 70 ff ff 	vmovdqu -0x90(%rax),%xmm0
     26e:	ff 
     26f:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     274:	c4 e3 7d 38 80 7c ff 	vinserti128 $0x1,-0x84(%rax),%ymm0,%ymm0
     27b:	ff ff 01 
     27e:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     283:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     288:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     28e:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     293:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     299:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     29e:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     2a4:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     2a9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     2ae:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     2b3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     2b8:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     2be:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     2c4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2c9:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     2ce:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     2d4:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     2da:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     2e0:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     2e6:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     2eb:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     2f0:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     2f7:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     2fe:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     303:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     307:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     30d:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     314:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     31b:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     31f:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     325:	c5 fa 6f 40 88       	vmovdqu -0x78(%rax),%xmm0
     32a:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     32f:	c4 e3 7d 38 40 94 01 	vinserti128 $0x1,-0x6c(%rax),%ymm0,%ymm0
     336:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     33b:	c5 79 6f e9          	vmovdqa %xmm1,%xmm13
     33f:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     345:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     34a:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     350:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     355:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     35b:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     360:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     366:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     36b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     370:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     375:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     37a:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     380:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     386:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     38c:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     392:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     397:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     39c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3a1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     3a6:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     3ac:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     3b2:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     3b8:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     3bf:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     3c6:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     3cd:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     3d1:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     3d6:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     3dd:	c5 c1 6c fe          	vpunpcklqdq %xmm6,%xmm7,%xmm7
     3e1:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     3e7:	c5 fa 6f 40 a0       	vmovdqu -0x60(%rax),%xmm0
     3ec:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     3f1:	c4 e3 7d 38 40 ac 01 	vinserti128 $0x1,-0x54(%rax),%ymm0,%ymm0
     3f8:	c4 e2 55 36 ff       	vpermd %ymm7,%ymm5,%ymm7
     3fd:	c5 79 6f f7          	vmovdqa %xmm7,%xmm14
     401:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     407:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     40c:	c4 c3 41 0f fe 08    	vpalignr $0x8,%xmm14,%xmm7,%xmm7
     412:	c4 c1 71 6c ce       	vpunpcklqdq %xmm14,%xmm1,%xmm1
     417:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     41d:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     422:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     428:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     42d:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     433:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     438:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     43d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     442:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     447:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     44d:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     453:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     458:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     45d:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     463:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     469:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     46f:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     475:	c4 e3 75 38 cf 01    	vinserti128 $0x1,%xmm7,%ymm1,%ymm1
     47b:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     480:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     485:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     48c:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     493:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     498:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     49c:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     4a2:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     4a9:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     4b0:	c4 c1 49 6c f1       	vpunpcklqdq %xmm9,%xmm6,%xmm6
     4b5:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     4bb:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
     4c0:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     4c5:	c4 e3 7d 38 40 c4 01 	vinserti128 $0x1,-0x3c(%rax),%ymm0,%ymm0
     4cc:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     4d1:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     4d6:	c4 c3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm9
     4dc:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     4e1:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     4e7:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     4ec:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     4f1:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     4f6:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     4fc:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     502:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     508:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     50d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     512:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     517:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     51c:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     522:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     528:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     52d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     532:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     538:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     53e:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     543:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     54a:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     551:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     558:	c5 31 6c c8          	vpunpcklqdq %xmm0,%xmm9,%xmm9
     55c:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     562:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     569:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
     56e:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
     574:	c5 7a 6f 48 d0       	vmovdqu -0x30(%rax),%xmm9
     579:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     57e:	c4 63 35 38 48 dc 01 	vinserti128 $0x1,-0x24(%rax),%ymm9,%ymm9
     585:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
     58a:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
     58f:	c4 43 7d 39 ca 01    	vextracti128 $0x1,%ymm9,%xmm10
     595:	c4 41 79 7e c8       	vmovd  %xmm9,%r8d
     59a:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
     5a0:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     5a5:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     5ab:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5b0:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     5b5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     5ba:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     5bf:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     5c5:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     5cb:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5d0:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5d5:	c4 43 79 16 c8 01    	vpextrd $0x1,%xmm9,%r8d
     5db:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
     5e1:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
     5e7:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     5ed:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     5f2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     5f7:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
     5fe:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     605:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     60a:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
     60f:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
     615:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     61c:	c4 23 29 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm10,%xmm10
     623:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
     628:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
     62e:	c5 7a 6f 48 e8       	vmovdqu -0x18(%rax),%xmm9
     633:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
     638:	c4 63 35 38 48 f4 01 	vinserti128 $0x1,-0xc(%rax),%ymm9,%ymm9
     63f:	c4 42 55 36 d2       	vpermd %ymm10,%ymm5,%ymm10
     644:	c5 79 7f d7          	vmovdqa %xmm10,%xmm7
     648:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
     64e:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
     653:	c4 43 7d 39 cb 01    	vextracti128 $0x1,%ymm9,%xmm11
     659:	c4 41 79 7e c8       	vmovd  %xmm9,%r8d
     65e:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
     664:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
     669:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
     66f:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     674:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     679:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     67e:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     683:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
     689:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
     68f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     694:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     699:	c4 43 79 16 c8 01    	vpextrd $0x1,%xmm9,%r8d
     69f:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
     6a5:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
     6ab:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
     6b1:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     6b6:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     6bb:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
     6c2:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
     6c9:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     6ce:	c4 41 21 6c d9       	vpunpcklqdq %xmm9,%xmm11,%xmm11
     6d3:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     6d9:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     6e0:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     6e7:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     6ee:	c5 fd e7 48 80       	vmovntdq %ymm1,-0x80(%rax)
     6f3:	c5 f9 6f ce          	vmovdqa %xmm6,%xmm1
     6f7:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     6fd:	4d 8d 41 40          	lea    0x40(%r9),%r8
     701:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     706:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
     70a:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     710:	c4 43 35 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm9
     716:	c4 c3 69 0f d4 08    	vpalignr $0x8,%xmm12,%xmm2,%xmm2
     71c:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     721:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     727:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     72c:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
     732:	c4 41 39 6c c4       	vpunpcklqdq %xmm12,%xmm8,%xmm8
     737:	c4 42 55 36 c9       	vpermd %ymm9,%ymm5,%ymm9
     73c:	c5 fd e7 90 60 ff ff 	vmovntdq %ymm2,-0xa0(%rax)
     743:	ff 
     744:	c4 43 25 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm11,%ymm8
     74a:	c5 79 7f ca          	vmovdqa %xmm9,%xmm2
     74e:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     754:	c5 7d e7 80 40 ff ff 	vmovntdq %ymm8,-0xc0(%rax)
     75b:	ff 
     75c:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     760:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     766:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     76a:	c4 c3 79 0f c0 08    	vpalignr $0x8,%xmm8,%xmm0,%xmm0
     770:	c4 63 31 0f ca 08    	vpalignr $0x8,%xmm2,%xmm9,%xmm9
     776:	c4 c1 49 6c f0       	vpunpcklqdq %xmm8,%xmm6,%xmm6
     77b:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
     781:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     787:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
     78d:	c5 fd e7 48 a0       	vmovntdq %ymm1,-0x60(%rax)
     792:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     797:	c5 7d e7 50 e0       	vmovntdq %ymm10,-0x20(%rax)
     79c:	4c 39 d1             	cmp    %r10,%rcx
     79f:	0f 83 23 f9 ff ff    	jae    c8 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc8>
     7a5:	0f ae f8             	sfence
     7a8:	49 8d 41 68          	lea    0x68(%r9),%rax
     7ac:	48 39 c1             	cmp    %rax,%rcx
     7af:	0f 82 7b 03 00 00    	jb     b30 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb30>
     7b5:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     7b9:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 7c1 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7c1>
     7c0:	00 
     7c1:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 7c9 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7c9>
     7c8:	00 
     7c9:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 7d1 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7d1>
     7d0:	00 
     7d1:	48 01 d0             	add    %rdx,%rax
     7d4:	0f 1f 40 00          	nopl   0x0(%rax)
     7d8:	c5 fa 6f 40 48       	vmovdqu 0x48(%rax),%xmm0
     7dd:	c5 7a 6f 40 30       	vmovdqu 0x30(%rax),%xmm8
     7e2:	48 83 c0 60          	add    $0x60,%rax
     7e6:	c5 fa 6f 50 a0       	vmovdqu -0x60(%rax),%xmm2
     7eb:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     7f0:	c4 e3 7d 38 40 f4 01 	vinserti128 $0x1,-0xc(%rax),%ymm0,%ymm0
     7f7:	c4 63 3d 38 40 dc 01 	vinserti128 $0x1,-0x24(%rax),%ymm8,%ymm8
     7fe:	c4 e3 6d 38 50 ac 01 	vinserti128 $0x1,-0x54(%rax),%ymm2,%ymm2
     805:	c4 e3 75 38 48 c4 01 	vinserti128 $0x1,-0x3c(%rax),%ymm1,%ymm1
     80c:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     811:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
     816:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     81c:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     821:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     827:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     82c:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     832:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     837:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     83c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     841:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     846:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     84c:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     852:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     857:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     85c:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     862:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     868:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     86e:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     874:	c4 43 7d 39 c2 01    	vextracti128 $0x1,%ymm8,%xmm10
     87a:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     87f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     884:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     889:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
     88f:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     894:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     89b:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     8a2:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     8a8:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     8ad:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     8b2:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     8b7:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     8bd:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     8c1:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     8c7:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     8cc:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     8d2:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     8d9:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
     8df:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     8e4:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
     8ea:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
     8f1:	c4 41 79 7e c1       	vmovd  %xmm8,%r9d
     8f6:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     8fb:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
     901:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     906:	c4 43 79 16 c1 01    	vpextrd $0x1,%xmm8,%r9d
     90c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     911:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
     916:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     91b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     920:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     926:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     92c:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     932:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     937:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     93c:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     943:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     94a:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     950:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     957:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     95c:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     961:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     967:	c5 39 6c c0          	vpunpcklqdq %xmm0,%xmm8,%xmm8
     96b:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     971:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     976:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     97c:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     982:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     987:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     98c:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     992:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     999:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
     99e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     9a3:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     9a8:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     9ad:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
     9b3:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     9b9:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
     9be:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     9c3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     9c8:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     9ce:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     9d4:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     9db:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     9e1:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     9e6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9eb:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     9f1:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     9f6:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     9fd:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     a02:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a07:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
     a0c:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     a13:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a18:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     a1e:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     a24:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     a28:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     a2e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     a33:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     a39:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a3e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a43:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     a4a:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
     a4f:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     a54:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
     a5a:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a5f:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     a65:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
     a6a:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     a6e:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     a74:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     a7a:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
     a7f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     a85:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     a8c:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     a91:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     a98:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
     a9f:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     aa4:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
     aa8:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     aae:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     ab2:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     ab8:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
     abe:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     ac4:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     acb:	4d 8d 48 48          	lea    0x48(%r8),%r9
     acf:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     ad4:	49 83 c0 20          	add    $0x20,%r8
     ad8:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
     add:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
     ae1:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     ae7:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
     aed:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
     af3:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
     af8:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     afd:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     b03:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     b08:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     b0d:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     b11:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     b17:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
     b1c:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
     b22:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     b27:	4c 39 c9             	cmp    %r9,%rcx
     b2a:	0f 83 a8 fc ff ff    	jae    7d8 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7d8>
     b30:	4d 8d 48 08          	lea    0x8(%r8),%r9
     b34:	4c 39 c9             	cmp    %r9,%rcx
     b37:	0f 82 0d 01 00 00    	jb     c4a <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc4a>
     b3d:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     b41:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # b49 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb49>
     b48:	00 
     b49:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # b51 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb51>
     b50:	00 
     b51:	48 01 d0             	add    %rdx,%rax
     b54:	0f 1f 40 00          	nopl   0x0(%rax)
     b58:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     b5c:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     b61:	48 83 c0 18          	add    $0x18,%rax
     b65:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     b6b:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     b71:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     b76:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     b7c:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     b81:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     b87:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     b8c:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     b92:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     b97:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     b9c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     ba1:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     ba6:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     bac:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     bb2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     bb7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     bbc:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     bc2:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     bc8:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     bce:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     bd4:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     bd9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     bde:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     be5:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     bec:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     bf1:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     bf5:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     bfb:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     c02:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     c09:	4d 89 c8             	mov    %r9,%r8
     c0c:	49 83 c1 08          	add    $0x8,%r9
     c10:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     c14:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     c1a:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     c1f:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     c23:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     c29:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     c2e:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     c33:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     c37:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     c3c:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     c41:	4c 39 c9             	cmp    %r9,%rcx
     c44:	0f 83 0e ff ff ff    	jae    b58 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb58>
     c4a:	49 39 c8             	cmp    %rcx,%r8
     c4d:	0f 83 ed 01 00 00    	jae    e40 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe40>
     c53:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     c57:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     c5b:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     c60:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     c65:	c1 e0 08             	shl    $0x8,%eax
     c68:	41 c1 e3 10          	shl    $0x10,%r11d
     c6c:	44 09 d8             	or     %r11d,%eax
     c6f:	45 0f b6 1a          	movzbl (%r10),%r11d
     c73:	44 09 d8             	or     %r11d,%eax
     c76:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     c7a:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     c7e:	41 8b 03             	mov    (%r11),%eax
     c81:	45 0f b7 1b          	movzwl (%r11),%r11d
     c85:	c1 e8 10             	shr    $0x10,%eax
     c88:	66 45 89 1a          	mov    %r11w,(%r10)
     c8c:	41 88 42 02          	mov    %al,0x2(%r10)
     c90:	49 8d 40 01          	lea    0x1(%r8),%rax
     c94:	48 39 c8             	cmp    %rcx,%rax
     c97:	0f 83 a3 01 00 00    	jae    e40 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe40>
     c9d:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     ca2:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     ca7:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     cac:	c1 e0 08             	shl    $0x8,%eax
     caf:	41 c1 e3 10          	shl    $0x10,%r11d
     cb3:	44 09 d8             	or     %r11d,%eax
     cb6:	45 0f b6 1a          	movzbl (%r10),%r11d
     cba:	44 09 d8             	or     %r11d,%eax
     cbd:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     cc1:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     cc5:	41 8b 03             	mov    (%r11),%eax
     cc8:	45 0f b7 1b          	movzwl (%r11),%r11d
     ccc:	c1 e8 10             	shr    $0x10,%eax
     ccf:	66 45 89 1a          	mov    %r11w,(%r10)
     cd3:	41 88 42 02          	mov    %al,0x2(%r10)
     cd7:	49 8d 40 02          	lea    0x2(%r8),%rax
     cdb:	48 39 c8             	cmp    %rcx,%rax
     cde:	0f 83 5c 01 00 00    	jae    e40 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe40>
     ce4:	4e 8d 54 0a 06       	lea    0x6(%rdx,%r9,1),%r10
     ce9:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     cee:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     cf3:	c1 e0 08             	shl    $0x8,%eax
     cf6:	41 c1 e3 10          	shl    $0x10,%r11d
     cfa:	44 09 d8             	or     %r11d,%eax
     cfd:	45 0f b6 1a          	movzbl (%r10),%r11d
     d01:	44 09 d8             	or     %r11d,%eax
     d04:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d08:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d0c:	41 8b 03             	mov    (%r11),%eax
     d0f:	45 0f b7 1b          	movzwl (%r11),%r11d
     d13:	c1 e8 10             	shr    $0x10,%eax
     d16:	66 45 89 1a          	mov    %r11w,(%r10)
     d1a:	41 88 42 02          	mov    %al,0x2(%r10)
     d1e:	49 8d 40 03          	lea    0x3(%r8),%rax
     d22:	48 39 c8             	cmp    %rcx,%rax
     d25:	0f 83 15 01 00 00    	jae    e40 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe40>
     d2b:	4e 8d 54 0a 09       	lea    0x9(%rdx,%r9,1),%r10
     d30:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     d35:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     d3a:	c1 e0 10             	shl    $0x10,%eax
     d3d:	41 c1 e3 08          	shl    $0x8,%r11d
     d41:	44 09 d8             	or     %r11d,%eax
     d44:	45 0f b6 1a          	movzbl (%r10),%r11d
     d48:	44 09 d8             	or     %r11d,%eax
     d4b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d4f:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d53:	41 8b 03             	mov    (%r11),%eax
     d56:	45 0f b7 1b          	movzwl (%r11),%r11d
     d5a:	c1 e8 10             	shr    $0x10,%eax
     d5d:	66 45 89 1a          	mov    %r11w,(%r10)
     d61:	41 88 42 02          	mov    %al,0x2(%r10)
     d65:	49 8d 40 04          	lea    0x4(%r8),%rax
     d69:	48 39 c8             	cmp    %rcx,%rax
     d6c:	0f 83 ce 00 00 00    	jae    e40 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe40>
     d72:	4e 8d 54 0a 0c       	lea    0xc(%rdx,%r9,1),%r10
     d77:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     d7c:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     d81:	c1 e0 10             	shl    $0x10,%eax
     d84:	41 c1 e3 08          	shl    $0x8,%r11d
     d88:	44 09 d8             	or     %r11d,%eax
     d8b:	45 0f b6 1a          	movzbl (%r10),%r11d
     d8f:	44 09 d8             	or     %r11d,%eax
     d92:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d96:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d9a:	41 8b 03             	mov    (%r11),%eax
     d9d:	45 0f b7 1b          	movzwl (%r11),%r11d
     da1:	c1 e8 10             	shr    $0x10,%eax
     da4:	66 45 89 1a          	mov    %r11w,(%r10)
     da8:	41 88 42 02          	mov    %al,0x2(%r10)
     dac:	49 8d 40 05          	lea    0x5(%r8),%rax
     db0:	48 39 c8             	cmp    %rcx,%rax
     db3:	0f 83 87 00 00 00    	jae    e40 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe40>
     db9:	4e 8d 54 0a 0f       	lea    0xf(%rdx,%r9,1),%r10
     dbe:	49 83 c0 06          	add    $0x6,%r8
     dc2:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     dc7:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     dcc:	c1 e0 10             	shl    $0x10,%eax
     dcf:	41 c1 e3 08          	shl    $0x8,%r11d
     dd3:	44 09 d8             	or     %r11d,%eax
     dd6:	45 0f b6 1a          	movzbl (%r10),%r11d
     dda:	44 09 d8             	or     %r11d,%eax
     ddd:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     de1:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     de5:	41 8b 03             	mov    (%r11),%eax
     de8:	45 0f b7 1b          	movzwl (%r11),%r11d
     dec:	c1 e8 10             	shr    $0x10,%eax
     def:	66 45 89 1a          	mov    %r11w,(%r10)
     df3:	41 88 42 02          	mov    %al,0x2(%r10)
     df7:	49 39 c8             	cmp    %rcx,%r8
     dfa:	73 44                	jae    e40 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe40>
     dfc:	4a 8d 54 0a 12       	lea    0x12(%rdx,%r9,1),%rdx
     e01:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     e05:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     e09:	c1 e0 08             	shl    $0x8,%eax
     e0c:	c1 e1 10             	shl    $0x10,%ecx
     e0f:	09 c8                	or     %ecx,%eax
     e11:	0f b6 0a             	movzbl (%rdx),%ecx
     e14:	09 c8                	or     %ecx,%eax
     e16:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e1a:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     e1e:	8b 01                	mov    (%rcx),%eax
     e20:	0f b7 09             	movzwl (%rcx),%ecx
     e23:	c1 e8 10             	shr    $0x10,%eax
     e26:	66 89 0a             	mov    %cx,(%rdx)
     e29:	88 42 02             	mov    %al,0x2(%rdx)
     e2c:	c5 f8 77             	vzeroupper
     e2f:	5b                   	pop    %rbx
     e30:	41 5c                	pop    %r12
     e32:	41 5d                	pop    %r13
     e34:	41 5e                	pop    %r14
     e36:	41 5f                	pop    %r15
     e38:	5d                   	pop    %rbp
     e39:	c3                   	ret
     e3a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     e40:	c5 f8 77             	vzeroupper
     e43:	5b                   	pop    %rbx
     e44:	41 5c                	pop    %r12
     e46:	41 5d                	pop    %r13
     e48:	41 5e                	pop    %r14
     e4a:	41 5f                	pop    %r15
     e4c:	5d                   	pop    %rbp
     e4d:	c3                   	ret
     e4e:	66 90                	xchg   %ax,%ax
     e50:	49 89 c8             	mov    %rcx,%r8
     e53:	e9 d8 fc ff ff       	jmp    b30 <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb30>
     e58:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     e5f:	00 
     e60:	c3                   	ret
     e61:	49 8d 41 28          	lea    0x28(%r9),%rax
     e65:	4d 89 c8             	mov    %r9,%r8
     e68:	e9 3f f9 ff ff       	jmp    7ac <jshc_channel::avx2_chain_vectorwide(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7ac>
     e6d:	0f 1f 00             	nopl   (%rax)

0000000000000e70 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     e70:	f3 0f 1e fa          	endbr64
     e74:	4d 85 c0             	test   %r8,%r8
     e77:	0f 84 f3 0e 00 00    	je     1d70 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf00>
     e7d:	55                   	push   %rbp
     e7e:	b8 00 04 00 00       	mov    $0x400,%eax
     e83:	49 89 d2             	mov    %rdx,%r10
     e86:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     e8a:	49 89 cb             	mov    %rcx,%r11
     e8d:	48 89 e5             	mov    %rsp,%rbp
     e90:	41 57                	push   %r15
     e92:	41 56                	push   %r14
     e94:	41 55                	push   %r13
     e96:	41 54                	push   %r12
     e98:	53                   	push   %rbx
     e99:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     e9d:	48 39 c2             	cmp    %rax,%rdx
     ea0:	48 0f 47 d0          	cmova  %rax,%rdx
     ea4:	31 c0                	xor    %eax,%eax
     ea6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     ead:	00 00 00 
     eb0:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
     eb5:	48 83 c0 40          	add    $0x40,%rax
     eb9:	48 39 d0             	cmp    %rdx,%rax
     ebc:	72 f2                	jb     eb0 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     ebe:	4d 89 d1             	mov    %r10,%r9
     ec1:	4c 89 da             	mov    %r11,%rdx
     ec4:	31 c9                	xor    %ecx,%ecx
     ec6:	eb 4c                	jmp    f14 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa4>
     ec8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     ecf:	00 
     ed0:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     ed5:	41 0f b6 59 02       	movzbl 0x2(%r9),%ebx
     eda:	48 ff c1             	inc    %rcx
     edd:	48 83 c2 03          	add    $0x3,%rdx
     ee1:	49 83 c1 03          	add    $0x3,%r9
     ee5:	c1 e3 10             	shl    $0x10,%ebx
     ee8:	c1 e0 08             	shl    $0x8,%eax
     eeb:	09 d8                	or     %ebx,%eax
     eed:	41 0f b6 59 fd       	movzbl -0x3(%r9),%ebx
     ef2:	09 d8                	or     %ebx,%eax
     ef4:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     ef8:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
     efc:	8b 03                	mov    (%rbx),%eax
     efe:	0f b7 1b             	movzwl (%rbx),%ebx
     f01:	c1 e8 10             	shr    $0x10,%eax
     f04:	66 89 5a fd          	mov    %bx,-0x3(%rdx)
     f08:	88 42 ff             	mov    %al,-0x1(%rdx)
     f0b:	49 39 c8             	cmp    %rcx,%r8
     f0e:	0f 84 4c 0e 00 00    	je     1d60 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xef0>
     f14:	f6 c2 3f             	test   $0x3f,%dl
     f17:	75 b7                	jne    ed0 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     f19:	48 8d 41 48          	lea    0x48(%rcx),%rax
     f1d:	49 39 c0             	cmp    %rax,%r8
     f20:	0f 82 4b 0e 00 00    	jb     1d71 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf01>
     f26:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     f2a:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # f32 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc2>
     f31:	00 
     f32:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # f3a <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xca>
     f39:	00 
     f3a:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
     f3f:	49 8d 14 03          	lea    (%r11,%rax,1),%rdx
     f43:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
     f48:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # f50 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe0>
     f4f:	00 
     f50:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
     f57:	00 
     f58:	eb 09                	jmp    f63 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
     f5a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     f60:	4c 89 c9             	mov    %r9,%rcx
     f63:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
     f6a:	4d 39 c8             	cmp    %r9,%r8
     f6d:	72 15                	jb     f84 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
     f6f:	0f 18 00             	prefetchnta (%rax)
     f72:	0f 18 40 40          	prefetchnta 0x40(%rax)
     f76:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
     f7d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
     f84:	c5 fa 6f 80 00 fc ff 	vmovdqu -0x400(%rax),%xmm0
     f8b:	ff 
     f8c:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
     f93:	48 05 c0 00 00 00    	add    $0xc0,%rax
     f99:	c4 e3 7d 38 80 4c fb 	vinserti128 $0x1,-0x4b4(%rax),%ymm0,%ymm0
     fa0:	ff ff 01 
     fa3:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     fa8:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     fae:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     fb3:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     fb9:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     fbe:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     fc4:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     fc9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     fce:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     fd3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     fd8:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     fde:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     fe4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     fe9:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     fee:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     ff4:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     ffa:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1000:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1006:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    100b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1010:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1017:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    101e:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    1024:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1028:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    102d:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    1034:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    103b:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    103f:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    1045:	c5 fa 6f 80 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm0
    104c:	ff 
    104d:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    1052:	c4 e3 7d 38 80 64 fb 	vinserti128 $0x1,-0x49c(%rax),%ymm0,%ymm0
    1059:	ff ff 01 
    105c:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
    1061:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1066:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    106c:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1071:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1077:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    107c:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1082:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1087:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    108c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1091:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1096:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    109c:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    10a2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    10a7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    10ac:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    10b2:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    10b8:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    10be:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    10c4:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    10c9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    10ce:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    10d5:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    10dc:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    10e0:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    10e5:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    10eb:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    10f2:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    10f9:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
    10fd:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    1103:	c5 fa 6f 80 70 fb ff 	vmovdqu -0x490(%rax),%xmm0
    110a:	ff 
    110b:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1110:	c4 e3 7d 38 80 7c fb 	vinserti128 $0x1,-0x484(%rax),%ymm0,%ymm0
    1117:	ff ff 01 
    111a:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    111f:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1124:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    112a:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    112f:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1135:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    113a:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1140:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1145:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    114a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    114f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1154:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    115a:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1160:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1165:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    116a:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1170:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1176:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    117c:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1182:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1187:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    118c:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
    1193:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    119a:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    11a0:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
    11a4:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    11a9:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    11b0:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    11b7:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    11bb:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    11c1:	c5 fa 6f 80 88 fb ff 	vmovdqu -0x478(%rax),%xmm0
    11c8:	ff 
    11c9:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    11ce:	c4 e3 7d 38 80 94 fb 	vinserti128 $0x1,-0x46c(%rax),%ymm0,%ymm0
    11d5:	ff ff 01 
    11d8:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    11dd:	c5 79 6f e9          	vmovdqa %xmm1,%xmm13
    11e1:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    11e7:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    11ec:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    11f2:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    11f7:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    11fd:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    1202:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    1208:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    120d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1212:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1217:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    121c:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1222:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1228:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    122e:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1234:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1239:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    123e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1243:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1248:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    124e:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1254:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    125a:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
    1261:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1268:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    126f:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
    1273:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    1278:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    127f:	c5 c1 6c fe          	vpunpcklqdq %xmm6,%xmm7,%xmm7
    1283:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    1289:	c5 fa 6f 80 a0 fb ff 	vmovdqu -0x460(%rax),%xmm0
    1290:	ff 
    1291:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    1296:	c4 e3 7d 38 80 ac fb 	vinserti128 $0x1,-0x454(%rax),%ymm0,%ymm0
    129d:	ff ff 01 
    12a0:	c4 e2 55 36 ff       	vpermd %ymm7,%ymm5,%ymm7
    12a5:	c5 79 6f f7          	vmovdqa %xmm7,%xmm14
    12a9:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    12af:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    12b4:	c4 c3 41 0f fe 08    	vpalignr $0x8,%xmm14,%xmm7,%xmm7
    12ba:	c4 c1 71 6c ce       	vpunpcklqdq %xmm14,%xmm1,%xmm1
    12bf:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    12c5:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    12ca:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    12d0:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    12d5:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    12db:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    12e0:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    12e5:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    12ea:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    12ef:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    12f5:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    12fb:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1300:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1305:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    130b:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1311:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    1317:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    131d:	c4 e3 75 38 cf 01    	vinserti128 $0x1,%xmm7,%ymm1,%ymm1
    1323:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1328:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    132d:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    1334:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    133b:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    1341:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    1346:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    134b:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
    1352:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1359:	c4 c1 49 6c f1       	vpunpcklqdq %xmm9,%xmm6,%xmm6
    135e:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    1364:	c5 fa 6f 80 b8 fb ff 	vmovdqu -0x448(%rax),%xmm0
    136b:	ff 
    136c:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1371:	c4 e3 7d 38 80 c4 fb 	vinserti128 $0x1,-0x43c(%rax),%ymm0,%ymm0
    1378:	ff ff 01 
    137b:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1380:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1385:	c4 c3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm9
    138b:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1390:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1396:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    139b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    13a0:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    13a5:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    13ab:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    13b1:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    13b7:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    13bc:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    13c1:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    13c6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    13cb:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    13d1:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    13d7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    13dc:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    13e1:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    13e7:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    13ed:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    13f3:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    13fa:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    1401:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1408:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    140d:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    1412:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    1419:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
    141e:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
    1424:	c5 7a 6f 88 d0 fb ff 	vmovdqu -0x430(%rax),%xmm9
    142b:	ff 
    142c:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1431:	c4 63 35 38 88 dc fb 	vinserti128 $0x1,-0x424(%rax),%ymm9,%ymm9
    1438:	ff ff 01 
    143b:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
    1440:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
    1445:	c4 43 7d 39 ca 01    	vextracti128 $0x1,%ymm9,%xmm10
    144b:	c4 41 79 7e c9       	vmovd  %xmm9,%r9d
    1450:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
    1456:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    145b:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    1461:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1466:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    146b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1470:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1475:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    147b:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    1481:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1486:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    148b:	c4 43 79 16 c9 01    	vpextrd $0x1,%xmm9,%r9d
    1491:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
    1497:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    149d:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    14a3:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    14a8:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    14ad:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    14b4:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    14bb:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    14c1:	c4 41 31 6c cb       	vpunpcklqdq %xmm11,%xmm9,%xmm9
    14c6:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    14cb:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    14d2:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    14d9:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    14de:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
    14e4:	c5 7a 6f 88 e8 fb ff 	vmovdqu -0x418(%rax),%xmm9
    14eb:	ff 
    14ec:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
    14f1:	c4 63 35 38 88 f4 fb 	vinserti128 $0x1,-0x40c(%rax),%ymm9,%ymm9
    14f8:	ff ff 01 
    14fb:	c4 42 55 36 d2       	vpermd %ymm10,%ymm5,%ymm10
    1500:	c5 79 7f d7          	vmovdqa %xmm10,%xmm7
    1504:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
    150a:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
    150f:	c4 43 7d 39 cb 01    	vextracti128 $0x1,%ymm9,%xmm11
    1515:	c4 41 79 7e c9       	vmovd  %xmm9,%r9d
    151a:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
    1520:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
    1525:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
    152b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1530:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1535:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    153a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    153f:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
    1545:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
    154b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1550:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1555:	c4 43 79 16 c9 01    	vpextrd $0x1,%xmm9,%r9d
    155b:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
    1561:	c4 21 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm12
    1567:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
    156d:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1572:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    1578:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    157f:	c4 23 19 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm12,%xmm12
    1586:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
    158d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1592:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
    1599:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    159d:	c4 41 21 6c dc       	vpunpcklqdq %xmm12,%xmm11,%xmm11
    15a2:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
    15a7:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    15ae:	c5 fd e7 4a 80       	vmovntdq %ymm1,-0x80(%rdx)
    15b3:	c5 f9 6f ce          	vmovdqa %xmm6,%xmm1
    15b7:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    15bd:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    15c2:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
    15c6:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    15cc:	c4 43 35 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm9
    15d2:	c4 c3 69 0f d4 08    	vpalignr $0x8,%xmm12,%xmm2,%xmm2
    15d8:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    15dd:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    15e3:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    15e8:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
    15ee:	c4 41 39 6c c4       	vpunpcklqdq %xmm12,%xmm8,%xmm8
    15f3:	c4 42 55 36 c9       	vpermd %ymm9,%ymm5,%ymm9
    15f8:	c5 fd e7 92 60 ff ff 	vmovntdq %ymm2,-0xa0(%rdx)
    15ff:	ff 
    1600:	c4 43 25 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm11,%ymm8
    1606:	c5 79 7f ca          	vmovdqa %xmm9,%xmm2
    160a:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    1610:	c5 7d e7 82 40 ff ff 	vmovntdq %ymm8,-0xc0(%rdx)
    1617:	ff 
    1618:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    161c:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1622:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
    1626:	c4 c3 79 0f c0 08    	vpalignr $0x8,%xmm8,%xmm0,%xmm0
    162c:	c4 63 31 0f ca 08    	vpalignr $0x8,%xmm2,%xmm9,%xmm9
    1632:	c4 c1 49 6c f0       	vpunpcklqdq %xmm8,%xmm6,%xmm6
    1637:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
    163d:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    1643:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
    1649:	c5 fd e7 4a a0       	vmovntdq %ymm1,-0x60(%rdx)
    164e:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    1653:	c5 7d e7 52 e0       	vmovntdq %ymm10,-0x20(%rdx)
    1658:	4d 39 d0             	cmp    %r10,%r8
    165b:	0f 83 ff f8 ff ff    	jae    f60 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    1661:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1666:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    166b:	48 8d 41 68          	lea    0x68(%rcx),%rax
    166f:	0f ae f8             	sfence
    1672:	49 39 c0             	cmp    %rax,%r8
    1675:	0f 82 97 03 00 00    	jb     1a12 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xba2>
    167b:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    167f:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1687 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x817>
    1686:	00 
    1687:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 168f <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x81f>
    168e:	00 
    168f:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1694:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1699:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 16a1 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x831>
    16a0:	00 
    16a1:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
    16a5:	4c 01 da             	add    %r11,%rdx
    16a8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    16af:	00 
    16b0:	c5 fa 6f 40 48       	vmovdqu 0x48(%rax),%xmm0
    16b5:	c5 7a 6f 40 30       	vmovdqu 0x30(%rax),%xmm8
    16ba:	48 83 c2 60          	add    $0x60,%rdx
    16be:	48 83 c0 60          	add    $0x60,%rax
    16c2:	c5 fa 6f 50 a0       	vmovdqu -0x60(%rax),%xmm2
    16c7:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
    16cc:	c4 e3 7d 38 40 f4 01 	vinserti128 $0x1,-0xc(%rax),%ymm0,%ymm0
    16d3:	c4 63 3d 38 40 dc 01 	vinserti128 $0x1,-0x24(%rax),%ymm8,%ymm8
    16da:	c4 e3 6d 38 50 ac 01 	vinserti128 $0x1,-0x54(%rax),%ymm2,%ymm2
    16e1:	c4 e3 75 38 48 c4 01 	vinserti128 $0x1,-0x3c(%rax),%ymm1,%ymm1
    16e8:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    16ed:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
    16f2:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    16f8:	c5 f9 7e c1          	vmovd  %xmm0,%ecx
    16fc:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1702:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    1707:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    170d:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1712:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1717:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    171c:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1721:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    1727:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    172d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1732:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1737:	c4 e3 79 16 c1 01    	vpextrd $0x1,%xmm0,%ecx
    173d:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1743:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1749:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    174f:	c4 43 7d 39 c2 01    	vextracti128 $0x1,%ymm8,%xmm10
    1755:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    175a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    175e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1763:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
    1769:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    176e:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    1775:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    177c:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    1782:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    1788:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    178d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1792:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    1798:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
    179d:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    17a2:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    17a7:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    17ad:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    17b4:	c5 79 7e c1          	vmovd  %xmm8,%ecx
    17b8:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    17bd:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
    17c3:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    17ca:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
    17d0:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    17d5:	c4 63 79 16 c1 01    	vpextrd $0x1,%xmm8,%ecx
    17db:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    17e0:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
    17e6:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    17ea:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    17ef:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    17f4:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
    17f9:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    17ff:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    1805:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    180b:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1811:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1816:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    181d:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    1824:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    182a:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
    1831:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    1836:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    183b:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    1841:	c4 41 39 6c c2       	vpunpcklqdq %xmm10,%xmm8,%xmm8
    1846:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    184b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1850:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    1856:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    185b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1860:	c5 f9 7e c9          	vmovd  %xmm1,%ecx
    1864:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1869:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    1870:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    1876:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    187c:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1881:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1886:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    188c:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1892:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
    1897:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    189e:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    18a2:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    18a8:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    18ae:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    18b4:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    18b9:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    18bf:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    18c4:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    18ca:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    18cf:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    18d6:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    18db:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    18e0:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
    18e5:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    18ec:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    18f1:	c5 f9 7e d1          	vmovd  %xmm2,%ecx
    18f5:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    18fb:	c4 41 39 6c c1       	vpunpcklqdq %xmm9,%xmm8,%xmm8
    1900:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    1905:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    190a:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    1910:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1914:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1919:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1920:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    1926:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    192b:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    1931:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
    1936:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    193b:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    193f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1945:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    194b:	c4 21 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm8
    1951:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1957:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    195d:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1962:	c4 23 39 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm8,%xmm8
    1969:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    1970:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    1975:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    197c:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
    1980:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1986:	c4 c1 41 6c f8       	vpunpcklqdq %xmm8,%xmm7,%xmm7
    198b:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
    1990:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
    1996:	49 8d 49 48          	lea    0x48(%r9),%rcx
    199a:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    19a0:	49 83 c1 20          	add    $0x20,%r9
    19a4:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
    19ab:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    19b0:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
    19b5:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
    19b9:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    19bf:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
    19c5:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
    19cb:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
    19d0:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    19d5:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    19db:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    19e0:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    19e5:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    19e9:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    19ef:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    19f4:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
    19fa:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    19ff:	49 39 c8             	cmp    %rcx,%r8
    1a02:	0f 83 a8 fc ff ff    	jae    16b0 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x840>
    1a08:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1a0d:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1a12:	49 8d 51 08          	lea    0x8(%r9),%rdx
    1a16:	49 39 d0             	cmp    %rdx,%r8
    1a19:	0f 82 29 01 00 00    	jb     1b48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcd8>
    1a1f:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1a23:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1a2b <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbbb>
    1a2a:	00 
    1a2b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1a33 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbc3>
    1a32:	00 
    1a33:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1a38:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1a3d:	49 8d 0c 02          	lea    (%r10,%rax,1),%rcx
    1a41:	4c 01 d8             	add    %r11,%rax
    1a44:	0f 1f 40 00          	nopl   0x0(%rax)
    1a48:	c5 fa 6f 01          	vmovdqu (%rcx),%xmm0
    1a4c:	c5 fa 7e 49 10       	vmovq  0x10(%rcx),%xmm1
    1a51:	48 83 c0 18          	add    $0x18,%rax
    1a55:	48 83 c1 18          	add    $0x18,%rcx
    1a59:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1a5f:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1a65:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1a6a:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1a70:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1a75:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1a7b:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1a80:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1a86:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1a8b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1a90:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1a95:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1a9a:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1aa0:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1aa6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1aab:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1ab0:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1ab6:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1abc:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1ac2:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1ac8:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1acd:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1ad2:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1ad9:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1ae0:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1ae6:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1aea:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1aef:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1af6:	49 89 d1             	mov    %rdx,%r9
    1af9:	48 83 c2 08          	add    $0x8,%rdx
    1afd:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    1b04:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1b08:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1b0e:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1b13:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1b17:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1b1d:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1b22:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1b27:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1b2b:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    1b30:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
    1b35:	49 39 d0             	cmp    %rdx,%r8
    1b38:	0f 83 0a ff ff ff    	jae    1a48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbd8>
    1b3e:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1b43:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1b48:	4d 39 c1             	cmp    %r8,%r9
    1b4b:	0f 83 f7 01 00 00    	jae    1d48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1b51:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1b55:	49 8d 1c 02          	lea    (%r10,%rax,1),%rbx
    1b59:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1b5d:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1b62:	0f b6 1b             	movzbl (%rbx),%ebx
    1b65:	c1 e2 08             	shl    $0x8,%edx
    1b68:	41 c1 e4 10          	shl    $0x10,%r12d
    1b6c:	44 09 e2             	or     %r12d,%edx
    1b6f:	09 da                	or     %ebx,%edx
    1b71:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1b75:	48 8d 1c 96          	lea    (%rsi,%rdx,4),%rbx
    1b79:	8b 13                	mov    (%rbx),%edx
    1b7b:	0f b7 1b             	movzwl (%rbx),%ebx
    1b7e:	c1 ea 10             	shr    $0x10,%edx
    1b81:	66 41 89 1c 03       	mov    %bx,(%r11,%rax,1)
    1b86:	41 88 54 03 02       	mov    %dl,0x2(%r11,%rax,1)
    1b8b:	49 8d 51 01          	lea    0x1(%r9),%rdx
    1b8f:	4c 39 c2             	cmp    %r8,%rdx
    1b92:	0f 83 b0 01 00 00    	jae    1d48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1b98:	49 8d 5c 02 03       	lea    0x3(%r10,%rax,1),%rbx
    1b9d:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1ba1:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1ba6:	0f b6 1b             	movzbl (%rbx),%ebx
    1ba9:	41 c1 e4 10          	shl    $0x10,%r12d
    1bad:	c1 e2 08             	shl    $0x8,%edx
    1bb0:	44 09 e2             	or     %r12d,%edx
    1bb3:	09 da                	or     %ebx,%edx
    1bb5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1bb9:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1bbd:	8b 1a                	mov    (%rdx),%ebx
    1bbf:	44 0f b7 22          	movzwl (%rdx),%r12d
    1bc3:	49 8d 51 02          	lea    0x2(%r9),%rdx
    1bc7:	89 d9                	mov    %ebx,%ecx
    1bc9:	66 45 89 64 03 03    	mov    %r12w,0x3(%r11,%rax,1)
    1bcf:	c1 e9 10             	shr    $0x10,%ecx
    1bd2:	41 88 4c 03 05       	mov    %cl,0x5(%r11,%rax,1)
    1bd7:	4c 39 c2             	cmp    %r8,%rdx
    1bda:	0f 83 68 01 00 00    	jae    1d48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1be0:	49 8d 5c 02 06       	lea    0x6(%r10,%rax,1),%rbx
    1be5:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1be9:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1bee:	0f b6 1b             	movzbl (%rbx),%ebx
    1bf1:	41 c1 e4 10          	shl    $0x10,%r12d
    1bf5:	c1 e2 08             	shl    $0x8,%edx
    1bf8:	44 09 e2             	or     %r12d,%edx
    1bfb:	09 da                	or     %ebx,%edx
    1bfd:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c01:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1c05:	8b 1a                	mov    (%rdx),%ebx
    1c07:	44 0f b7 22          	movzwl (%rdx),%r12d
    1c0b:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1c0f:	89 d9                	mov    %ebx,%ecx
    1c11:	66 45 89 64 03 06    	mov    %r12w,0x6(%r11,%rax,1)
    1c17:	c1 e9 10             	shr    $0x10,%ecx
    1c1a:	41 88 4c 03 08       	mov    %cl,0x8(%r11,%rax,1)
    1c1f:	4c 39 c2             	cmp    %r8,%rdx
    1c22:	0f 83 20 01 00 00    	jae    1d48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1c28:	49 8d 5c 02 09       	lea    0x9(%r10,%rax,1),%rbx
    1c2d:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1c31:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1c36:	0f b6 1b             	movzbl (%rbx),%ebx
    1c39:	41 c1 e4 08          	shl    $0x8,%r12d
    1c3d:	c1 e2 10             	shl    $0x10,%edx
    1c40:	44 09 e2             	or     %r12d,%edx
    1c43:	09 da                	or     %ebx,%edx
    1c45:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c49:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1c4d:	8b 1a                	mov    (%rdx),%ebx
    1c4f:	44 0f b7 22          	movzwl (%rdx),%r12d
    1c53:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1c57:	89 d9                	mov    %ebx,%ecx
    1c59:	66 45 89 64 03 09    	mov    %r12w,0x9(%r11,%rax,1)
    1c5f:	c1 e9 10             	shr    $0x10,%ecx
    1c62:	41 88 4c 03 0b       	mov    %cl,0xb(%r11,%rax,1)
    1c67:	4c 39 c2             	cmp    %r8,%rdx
    1c6a:	0f 83 d8 00 00 00    	jae    1d48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1c70:	49 8d 5c 02 0c       	lea    0xc(%r10,%rax,1),%rbx
    1c75:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1c79:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1c7e:	0f b6 1b             	movzbl (%rbx),%ebx
    1c81:	41 c1 e4 08          	shl    $0x8,%r12d
    1c85:	c1 e2 10             	shl    $0x10,%edx
    1c88:	44 09 e2             	or     %r12d,%edx
    1c8b:	09 da                	or     %ebx,%edx
    1c8d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c91:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1c95:	8b 1a                	mov    (%rdx),%ebx
    1c97:	44 0f b7 22          	movzwl (%rdx),%r12d
    1c9b:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1c9f:	c1 eb 10             	shr    $0x10,%ebx
    1ca2:	66 45 89 64 03 0c    	mov    %r12w,0xc(%r11,%rax,1)
    1ca8:	41 88 5c 03 0e       	mov    %bl,0xe(%r11,%rax,1)
    1cad:	4c 39 c2             	cmp    %r8,%rdx
    1cb0:	0f 83 92 00 00 00    	jae    1d48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1cb6:	49 8d 5c 02 0f       	lea    0xf(%r10,%rax,1),%rbx
    1cbb:	49 83 c1 06          	add    $0x6,%r9
    1cbf:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1cc3:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1cc8:	0f b6 1b             	movzbl (%rbx),%ebx
    1ccb:	41 c1 e4 08          	shl    $0x8,%r12d
    1ccf:	c1 e2 10             	shl    $0x10,%edx
    1cd2:	44 09 e2             	or     %r12d,%edx
    1cd5:	09 da                	or     %ebx,%edx
    1cd7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1cdb:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1cdf:	8b 1a                	mov    (%rdx),%ebx
    1ce1:	44 0f b7 22          	movzwl (%rdx),%r12d
    1ce5:	89 d9                	mov    %ebx,%ecx
    1ce7:	66 45 89 64 03 0f    	mov    %r12w,0xf(%r11,%rax,1)
    1ced:	c1 e9 10             	shr    $0x10,%ecx
    1cf0:	41 88 4c 03 11       	mov    %cl,0x11(%r11,%rax,1)
    1cf5:	4d 39 c1             	cmp    %r8,%r9
    1cf8:	73 4e                	jae    1d48 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1cfa:	49 8d 54 02 12       	lea    0x12(%r10,%rax,1),%rdx
    1cff:	4d 8d 44 03 12       	lea    0x12(%r11,%rax,1),%r8
    1d04:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1d08:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1d0c:	0f b6 12             	movzbl (%rdx),%edx
    1d0f:	c1 e0 08             	shl    $0x8,%eax
    1d12:	c1 e1 10             	shl    $0x10,%ecx
    1d15:	09 c8                	or     %ecx,%eax
    1d17:	09 d0                	or     %edx,%eax
    1d19:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1d1d:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1d21:	8b 02                	mov    (%rdx),%eax
    1d23:	0f b7 12             	movzwl (%rdx),%edx
    1d26:	c1 e8 10             	shr    $0x10,%eax
    1d29:	66 41 89 10          	mov    %dx,(%r8)
    1d2d:	41 88 40 02          	mov    %al,0x2(%r8)
    1d31:	c5 f8 77             	vzeroupper
    1d34:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1d38:	5b                   	pop    %rbx
    1d39:	41 5c                	pop    %r12
    1d3b:	41 5d                	pop    %r13
    1d3d:	41 5e                	pop    %r14
    1d3f:	41 5f                	pop    %r15
    1d41:	5d                   	pop    %rbp
    1d42:	c3                   	ret
    1d43:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1d48:	c5 f8 77             	vzeroupper
    1d4b:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1d4f:	5b                   	pop    %rbx
    1d50:	41 5c                	pop    %r12
    1d52:	41 5d                	pop    %r13
    1d54:	41 5e                	pop    %r14
    1d56:	41 5f                	pop    %r15
    1d58:	5d                   	pop    %rbp
    1d59:	c3                   	ret
    1d5a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1d60:	4d 89 c1             	mov    %r8,%r9
    1d63:	e9 aa fc ff ff       	jmp    1a12 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xba2>
    1d68:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    1d6f:	00 
    1d70:	c3                   	ret
    1d71:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1d75:	49 89 c9             	mov    %rcx,%r9
    1d78:	e9 f5 f8 ff ff       	jmp    1672 <jshc_channel::avx2_chain_vectorwide_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x802>
