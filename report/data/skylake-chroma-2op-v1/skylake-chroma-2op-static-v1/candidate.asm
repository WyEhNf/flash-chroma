
artifacts/skylake-chroma-2op-linux-build-v1/CMakeFiles/jshc_skylake_chroma_2op.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 13 10 00 00    	je     1020 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1020>
       d:	55                   	push   %rbp
       e:	b8 00 04 00 00       	mov    $0x400,%eax
      13:	49 89 d0             	mov    %rdx,%r8
      16:	48 8d 14 49          	lea    (%rcx,%rcx,2),%rdx
      1a:	48 39 c2             	cmp    %rax,%rdx
      1d:	48 0f 47 d0          	cmova  %rax,%rdx
      21:	31 c0                	xor    %eax,%eax
      23:	48 89 e5             	mov    %rsp,%rbp
      26:	41 57                	push   %r15
      28:	41 56                	push   %r14
      2a:	41 55                	push   %r13
      2c:	41 54                	push   %r12
      2e:	53                   	push   %rbx
      2f:	90                   	nop
      30:	41 0f 18 04 00       	prefetchnta (%r8,%rax,1)
      35:	48 83 c0 40          	add    $0x40,%rax
      39:	48 39 d0             	cmp    %rdx,%rax
      3c:	72 f2                	jb     30 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3e:	4d 89 c1             	mov    %r8,%r9
      41:	31 d2                	xor    %edx,%edx
      43:	eb 65                	jmp    aa <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xaa>
      45:	0f 1f 00             	nopl   (%rax)
      48:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
      4d:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
      52:	48 ff c2             	inc    %rdx
      55:	49 83 c1 03          	add    $0x3,%r9
      59:	41 c1 e2 10          	shl    $0x10,%r10d
      5d:	c1 e0 08             	shl    $0x8,%eax
      60:	44 09 d0             	or     %r10d,%eax
      63:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
      68:	0f b6 dc             	movzbl %ah,%ebx
      6b:	c1 e8 10             	shr    $0x10,%eax
      6e:	29 d8                	sub    %ebx,%eax
      70:	44 29 d3             	sub    %r10d,%ebx
      73:	c1 e0 10             	shl    $0x10,%eax
      76:	c1 e3 08             	shl    $0x8,%ebx
      79:	25 00 00 ff 00       	and    $0xff0000,%eax
      7e:	0f b7 db             	movzwl %bx,%ebx
      81:	09 d8                	or     %ebx,%eax
      83:	44 09 d0             	or     %r10d,%eax
      86:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
      8a:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
      8e:	41 8b 02             	mov    (%r10),%eax
      91:	45 0f b7 12          	movzwl (%r10),%r10d
      95:	c1 e8 10             	shr    $0x10,%eax
      98:	66 45 89 51 fd       	mov    %r10w,-0x3(%r9)
      9d:	41 88 41 ff          	mov    %al,-0x1(%r9)
      a1:	48 39 d1             	cmp    %rdx,%rcx
      a4:	0f 84 66 0f 00 00    	je     1010 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1010>
      aa:	41 f6 c1 3f          	test   $0x3f,%r9b
      ae:	75 98                	jne    48 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      b0:	48 8d 42 48          	lea    0x48(%rdx),%rax
      b4:	48 39 c1             	cmp    %rax,%rcx
      b7:	0f 82 64 0f 00 00    	jb     1021 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1021>
      bd:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
      c1:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # c9 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc9>
      c8:	00 
      c9:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # d1 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd1>
      d0:	00 
      d1:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # d9 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd9>
      d8:	00 
      d9:	4c 01 c0             	add    %r8,%rax
      dc:	eb 05                	jmp    e3 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe3>
      de:	66 90                	xchg   %ax,%ax
      e0:	4c 89 ca             	mov    %r9,%rdx
      e3:	4c 8d 8a 96 01 00 00 	lea    0x196(%rdx),%r9
      ea:	4c 39 c9             	cmp    %r9,%rcx
      ed:	72 1c                	jb     10b <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10b>
      ef:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      f6:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      fd:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     104:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     10b:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     10f:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     114:	48 05 c0 00 00 00    	add    $0xc0,%rax
     11a:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     120:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     126:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     12b:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     130:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     134:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     13a:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     13f:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     145:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     14a:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     150:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     155:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     15a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     15f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     164:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     16a:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     170:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     175:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     17a:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     180:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     186:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     18c:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     192:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     197:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     19c:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     1a3:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     1aa:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     1b0:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     1b4:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     1b9:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
     1c0:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1c7:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     1cb:	c5 fa 7e 88 68 ff ff 	vmovq  -0x98(%rax),%xmm1
     1d2:	ff 
     1d3:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     1d9:	c5 fa 6f 80 58 ff ff 	vmovdqu -0xa8(%rax),%xmm0
     1e0:	ff 
     1e1:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     1e6:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     1ec:	c4 42 55 36 c9       	vpermd %ymm9,%ymm5,%ymm9
     1f1:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     1f7:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     1fc:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     201:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     205:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     20b:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     210:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     216:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     21b:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     221:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     226:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     22b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     230:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     235:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     23b:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     241:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     246:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     24b:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     251:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     257:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     25d:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     263:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     268:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     26d:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     274:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     27b:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     27f:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     284:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     28a:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     291:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     298:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     29c:	c5 fa 7e 48 80       	vmovq  -0x80(%rax),%xmm1
     2a1:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     2a7:	c5 fa 6f 80 70 ff ff 	vmovdqu -0x90(%rax),%xmm0
     2ae:	ff 
     2af:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     2b4:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     2ba:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     2bf:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     2c5:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     2ca:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     2cf:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     2d3:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     2d9:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     2de:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     2e4:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     2e9:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     2ef:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     2f4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     2f9:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     2fe:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     303:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     309:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     30f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     314:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     319:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     31f:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     325:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     32b:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     331:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     336:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     33b:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     342:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     349:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     34e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     352:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     358:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     35f:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     366:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     36a:	c5 fa 7e 70 98       	vmovq  -0x68(%rax),%xmm6
     36f:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     375:	c5 fa 6f 40 88       	vmovdqu -0x78(%rax),%xmm0
     37a:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     37f:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     385:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     38a:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     390:	c5 79 6f e9          	vmovdqa %xmm1,%xmm13
     394:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     39a:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     39f:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
     3a4:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
     3a8:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     3ae:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     3b3:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     3b9:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     3be:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     3c4:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     3c9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     3ce:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     3d3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     3d8:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     3de:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     3e4:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     3ea:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     3f0:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     3f5:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     3fa:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3ff:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     404:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     40a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     410:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     416:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     41d:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     424:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
     42b:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     42f:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     434:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     43b:	c5 39 6c c6          	vpunpcklqdq %xmm6,%xmm8,%xmm8
     43f:	c5 fa 7e 70 b0       	vmovq  -0x50(%rax),%xmm6
     444:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     44a:	c5 fa 6f 40 a0       	vmovdqu -0x60(%rax),%xmm0
     44f:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     454:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     45a:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
     45f:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     465:	c4 41 79 6f f0       	vmovdqa %xmm8,%xmm14
     46a:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     470:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     475:	c4 43 39 0f c6 08    	vpalignr $0x8,%xmm14,%xmm8,%xmm8
     47b:	c4 c1 71 6c ce       	vpunpcklqdq %xmm14,%xmm1,%xmm1
     480:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
     485:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     48b:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
     48f:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     495:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     49a:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     4a0:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     4a5:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     4ab:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     4b0:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     4b5:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     4ba:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     4bf:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     4c5:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     4cb:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     4d0:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     4d5:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     4db:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     4e1:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     4e7:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     4ed:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     4f2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     4f7:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     4fe:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     505:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     50b:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     50f:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     514:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
     51b:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     522:	c5 c1 6c fe          	vpunpcklqdq %xmm6,%xmm7,%xmm7
     526:	c5 fa 7e 70 c8       	vmovq  -0x38(%rax),%xmm6
     52b:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     531:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
     536:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     53b:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     541:	c4 e2 55 36 ff       	vpermd %ymm7,%ymm5,%ymm7
     546:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     54c:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     551:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
     556:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
     55a:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     560:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     565:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     56b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     570:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     575:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     57a:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     580:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     586:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     58c:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     591:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     596:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     59b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     5a0:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     5a6:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     5ac:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5b1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5b6:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     5bc:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     5c2:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     5c7:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     5ce:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
     5d5:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     5dc:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
     5e0:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     5e6:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     5ed:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
     5f2:	c5 7a 7e 50 e0       	vmovq  -0x20(%rax),%xmm10
     5f7:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     5fd:	c5 fa 6f 70 d0       	vmovdqu -0x30(%rax),%xmm6
     602:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     607:	c4 63 29 0f d6 0c    	vpalignr $0xc,%xmm6,%xmm10,%xmm10
     60d:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
     612:	c4 c3 4d 38 f2 01    	vinserti128 $0x1,%xmm10,%ymm6,%ymm6
     618:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
     61d:	c5 ad 72 f6 08       	vpslld $0x8,%ymm6,%ymm10
     622:	c4 c1 4d f8 f2       	vpsubb %ymm10,%ymm6,%ymm6
     627:	c4 c3 7d 39 f2 01    	vextracti128 $0x1,%ymm6,%xmm10
     62d:	c4 c1 79 7e f1       	vmovd  %xmm6,%r9d
     632:	c4 c3 79 16 f3 02    	vpextrd $0x2,%xmm6,%r11d
     638:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     63d:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     643:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     648:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     64d:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     652:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     657:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     65d:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     663:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     668:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     66d:	c4 c3 79 16 f1 01    	vpextrd $0x1,%xmm6,%r9d
     673:	c4 c3 79 16 f3 03    	vpextrd $0x3,%xmm6,%r11d
     679:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
     67f:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     685:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     68a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     68f:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
     696:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
     69d:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     6a2:	c4 c1 49 6c f2       	vpunpcklqdq %xmm10,%xmm6,%xmm6
     6a7:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
     6ad:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     6b4:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
     6bb:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
     6c0:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
     6c5:	c4 63 2d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm10,%ymm10
     6cb:	c5 fa 6f 70 e8       	vmovdqu -0x18(%rax),%xmm6
     6d0:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
     6d5:	c4 63 21 0f de 0c    	vpalignr $0xc,%xmm6,%xmm11,%xmm11
     6db:	c4 42 55 36 d2       	vpermd %ymm10,%ymm5,%ymm10
     6e0:	c4 c3 4d 38 f3 01    	vinserti128 $0x1,%xmm11,%ymm6,%ymm6
     6e6:	c4 41 79 6f c2       	vmovdqa %xmm10,%xmm8
     6eb:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
     6f1:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
     6f6:	c5 a5 72 f6 08       	vpslld $0x8,%ymm6,%ymm11
     6fb:	c4 c1 4d f8 f3       	vpsubb %ymm11,%ymm6,%ymm6
     700:	c4 c3 7d 39 f3 01    	vextracti128 $0x1,%ymm6,%xmm11
     706:	c4 c1 79 7e f1       	vmovd  %xmm6,%r9d
     70b:	c4 c3 79 16 f3 02    	vpextrd $0x2,%xmm6,%r11d
     711:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
     716:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
     71c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     721:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     726:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     72b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     730:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
     736:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
     73c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     741:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     746:	c4 c3 79 16 f1 01    	vpextrd $0x1,%xmm6,%r9d
     74c:	c4 c3 79 16 f3 03    	vpextrd $0x3,%xmm6,%r11d
     752:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
     758:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     75e:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     763:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     768:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     76f:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
     776:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     77b:	c5 21 6c de          	vpunpcklqdq %xmm6,%xmm11,%xmm11
     77f:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     785:	4c 8d 92 88 00 00 00 	lea    0x88(%rdx),%r10
     78c:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     793:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
     79a:	c5 fd e7 48 80       	vmovntdq %ymm1,-0x80(%rax)
     79f:	c5 f9 6f cf          	vmovdqa %xmm7,%xmm1
     7a3:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     7a9:	4c 8d 4a 40          	lea    0x40(%rdx),%r9
     7ad:	c4 c1 49 6c f4       	vpunpcklqdq %xmm12,%xmm6,%xmm6
     7b2:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
     7b6:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     7bc:	c4 c3 4d 38 f3 01    	vinserti128 $0x1,%xmm11,%ymm6,%ymm6
     7c2:	c4 c3 69 0f d4 08    	vpalignr $0x8,%xmm12,%xmm2,%xmm2
     7c8:	c4 41 79 6f d9       	vmovdqa %xmm9,%xmm11
     7cd:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     7d3:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     7d8:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
     7de:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     7e3:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     7e8:	c5 fd e7 90 60 ff ff 	vmovntdq %ymm2,-0xa0(%rax)
     7ef:	ff 
     7f0:	c4 43 25 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm11,%ymm9
     7f6:	c5 f9 6f d6          	vmovdqa %xmm6,%xmm2
     7fa:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     800:	c5 7d e7 88 40 ff ff 	vmovntdq %ymm9,-0xc0(%rax)
     807:	ff 
     808:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     80c:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     812:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     816:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     81c:	c4 e3 49 0f f2 08    	vpalignr $0x8,%xmm2,%xmm6,%xmm6
     822:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     827:	c4 e3 75 38 cf 01    	vinserti128 $0x1,%xmm7,%ymm1,%ymm1
     82d:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     833:	c4 63 2d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm10,%ymm10
     839:	c5 fd e7 48 a0       	vmovntdq %ymm1,-0x60(%rax)
     83e:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     843:	c5 7d e7 50 e0       	vmovntdq %ymm10,-0x20(%rax)
     848:	4c 39 d1             	cmp    %r10,%rcx
     84b:	0f 83 8f f8 ff ff    	jae    e0 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe0>
     851:	0f ae f8             	sfence
     854:	48 8d 42 68          	lea    0x68(%rdx),%rax
     858:	48 39 c1             	cmp    %rax,%rcx
     85b:	0f 82 be 03 00 00    	jb     c1f <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc1f>
     861:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     865:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 86d <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x86d>
     86c:	00 
     86d:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 875 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x875>
     874:	00 
     875:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 87d <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x87d>
     87c:	00 
     87d:	4c 01 c0             	add    %r8,%rax
     880:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     884:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
     889:	48 83 c0 60          	add    $0x60,%rax
     88d:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     892:	c5 fa 7e 70 e0       	vmovq  -0x20(%rax),%xmm6
     897:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
     89d:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     8a3:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     8a8:	c5 fd 72 f2 08       	vpslld $0x8,%ymm2,%ymm0
     8ad:	c5 ed f8 d0          	vpsubb %ymm0,%ymm2,%ymm2
     8b1:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
     8b6:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
     8bc:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
     8c2:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     8c8:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     8cd:	c5 fd 72 f1 08       	vpslld $0x8,%ymm1,%ymm0
     8d2:	c5 f5 f8 c8          	vpsubb %ymm0,%ymm1,%ymm1
     8d6:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
     8db:	c4 c3 7d 39 c8 01    	vextracti128 $0x1,%ymm1,%xmm8
     8e1:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     8e7:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     8ed:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     8f2:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
     8f7:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
     8fb:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
     900:	c4 c3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm9
     906:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
     90a:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
     90f:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     915:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     91b:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     920:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
     925:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
     929:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     92f:	c5 f9 7e c2          	vmovd  %xmm0,%edx
     933:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     939:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     93e:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     944:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     949:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     94e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     953:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     958:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     95e:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     964:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     969:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     96e:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     974:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     97a:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     980:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     986:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     98a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     98f:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     996:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     99d:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     9a3:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     9a8:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     9ad:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9b2:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     9b8:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     9bc:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     9c2:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     9c7:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     9cd:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     9d4:	c4 43 79 16 d3 02    	vpextrd $0x2,%xmm10,%r11d
     9da:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     9df:	c4 e3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm6,%xmm6
     9e6:	c5 79 7e d2          	vmovd  %xmm10,%edx
     9ea:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     9ef:	c4 43 79 16 d3 03    	vpextrd $0x3,%xmm10,%r11d
     9f5:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     9fa:	c4 63 79 16 d2 01    	vpextrd $0x1,%xmm10,%edx
     a00:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a05:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
     a0a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     a0e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a13:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     a19:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     a1f:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     a25:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     a2a:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     a2f:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     a36:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     a3d:	c4 43 79 16 c6 02    	vpextrd $0x2,%xmm8,%r14d
     a43:	c4 41 79 7e c4       	vmovd  %xmm8,%r12d
     a48:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a4d:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     a54:	c4 43 79 16 c6 03    	vpextrd $0x3,%xmm8,%r14d
     a5a:	c5 31 6c c8          	vpunpcklqdq %xmm0,%xmm9,%xmm9
     a5e:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     a64:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a69:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     a6f:	c4 43 79 16 c4 01    	vpextrd $0x1,%xmm8,%r12d
     a75:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     a7a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a7f:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     a85:	c4 e3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm0,%xmm0
     a8c:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     a90:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a95:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     a9a:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     a9f:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     aa5:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     aab:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     ab1:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
     ab6:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     aba:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     ac1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     ac6:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
     acc:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     ad1:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     ad8:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     add:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     ae3:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     ae8:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     aed:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     af2:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     af8:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     afe:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     b02:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     b08:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     b0f:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     b15:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     b1a:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     b20:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     b25:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
     b2a:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
     b31:	c5 f9 7e d2          	vmovd  %xmm2,%edx
     b35:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b3a:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     b3f:	c4 e3 79 16 d2 01    	vpextrd $0x1,%xmm2,%edx
     b45:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b4a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     b4e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     b54:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
     b59:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     b5d:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     b63:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     b69:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
     b6e:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     b74:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     b7b:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     b80:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     b87:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
     b8e:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     b93:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
     b97:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     b9d:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     ba1:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     ba7:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
     bad:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     bb3:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
     bba:	49 8d 51 48          	lea    0x48(%r9),%rdx
     bbe:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     bc3:	49 83 c1 20          	add    $0x20,%r9
     bc7:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
     bcc:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
     bd0:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     bd6:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
     bdc:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
     be2:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
     be7:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     bec:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     bf2:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     bf7:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     bfc:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     c00:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     c06:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
     c0b:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
     c11:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     c16:	48 39 d1             	cmp    %rdx,%rcx
     c19:	0f 83 61 fc ff ff    	jae    880 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x880>
     c1f:	49 8d 51 08          	lea    0x8(%r9),%rdx
     c23:	48 39 d1             	cmp    %rdx,%rcx
     c26:	0f 82 17 01 00 00    	jb     d43 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd43>
     c2c:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     c30:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # c38 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc38>
     c37:	00 
     c38:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # c40 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc40>
     c3f:	00 
     c40:	4c 01 c0             	add    %r8,%rax
     c43:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     c48:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     c4c:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     c51:	48 83 c0 18          	add    $0x18,%rax
     c55:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     c5b:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     c61:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     c66:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     c6b:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     c6f:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     c75:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     c7a:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     c80:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     c85:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     c8b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     c90:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     c95:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     c9a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     c9f:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     ca5:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     cab:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     cb0:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     cb5:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     cbb:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     cc1:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     cc7:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     ccd:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     cd2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     cd7:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     cde:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     ce5:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     cea:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     cee:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     cf4:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     cfb:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     d02:	49 89 d1             	mov    %rdx,%r9
     d05:	48 83 c2 08          	add    $0x8,%rdx
     d09:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     d0d:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     d13:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     d18:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     d1c:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     d22:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     d27:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     d2c:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     d30:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     d35:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     d3a:	48 39 d1             	cmp    %rdx,%rcx
     d3d:	0f 83 05 ff ff ff    	jae    c48 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc48>
     d43:	49 39 c9             	cmp    %rcx,%r9
     d46:	0f 83 ac 02 00 00    	jae    ff8 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff8>
     d4c:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
     d50:	4d 8d 14 10          	lea    (%r8,%rdx,1),%r10
     d54:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d59:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d5e:	c1 e0 08             	shl    $0x8,%eax
     d61:	41 c1 e3 10          	shl    $0x10,%r11d
     d65:	44 09 d8             	or     %r11d,%eax
     d68:	45 0f b6 1a          	movzbl (%r10),%r11d
     d6c:	0f b6 dc             	movzbl %ah,%ebx
     d6f:	c1 e8 10             	shr    $0x10,%eax
     d72:	29 d8                	sub    %ebx,%eax
     d74:	44 29 db             	sub    %r11d,%ebx
     d77:	c1 e0 10             	shl    $0x10,%eax
     d7a:	c1 e3 08             	shl    $0x8,%ebx
     d7d:	25 00 00 ff 00       	and    $0xff0000,%eax
     d82:	0f b7 db             	movzwl %bx,%ebx
     d85:	09 d8                	or     %ebx,%eax
     d87:	44 09 d8             	or     %r11d,%eax
     d8a:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d8e:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d92:	41 8b 03             	mov    (%r11),%eax
     d95:	45 0f b7 1b          	movzwl (%r11),%r11d
     d99:	c1 e8 10             	shr    $0x10,%eax
     d9c:	66 45 89 1a          	mov    %r11w,(%r10)
     da0:	41 88 42 02          	mov    %al,0x2(%r10)
     da4:	49 8d 41 01          	lea    0x1(%r9),%rax
     da8:	48 39 c8             	cmp    %rcx,%rax
     dab:	0f 83 47 02 00 00    	jae    ff8 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff8>
     db1:	4d 8d 54 10 03       	lea    0x3(%r8,%rdx,1),%r10
     db6:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     dbb:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     dc0:	c1 e0 08             	shl    $0x8,%eax
     dc3:	41 c1 e3 10          	shl    $0x10,%r11d
     dc7:	44 09 d8             	or     %r11d,%eax
     dca:	45 0f b6 1a          	movzbl (%r10),%r11d
     dce:	0f b6 dc             	movzbl %ah,%ebx
     dd1:	c1 e8 10             	shr    $0x10,%eax
     dd4:	29 d8                	sub    %ebx,%eax
     dd6:	44 29 db             	sub    %r11d,%ebx
     dd9:	c1 e0 10             	shl    $0x10,%eax
     ddc:	c1 e3 08             	shl    $0x8,%ebx
     ddf:	25 00 00 ff 00       	and    $0xff0000,%eax
     de4:	0f b7 db             	movzwl %bx,%ebx
     de7:	09 d8                	or     %ebx,%eax
     de9:	44 09 d8             	or     %r11d,%eax
     dec:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     df0:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     df4:	41 8b 03             	mov    (%r11),%eax
     df7:	45 0f b7 1b          	movzwl (%r11),%r11d
     dfb:	c1 e8 10             	shr    $0x10,%eax
     dfe:	66 45 89 1a          	mov    %r11w,(%r10)
     e02:	41 88 42 02          	mov    %al,0x2(%r10)
     e06:	49 8d 41 02          	lea    0x2(%r9),%rax
     e0a:	48 39 c8             	cmp    %rcx,%rax
     e0d:	0f 83 e5 01 00 00    	jae    ff8 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff8>
     e13:	4d 8d 54 10 06       	lea    0x6(%r8,%rdx,1),%r10
     e18:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     e1d:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e22:	c1 e0 08             	shl    $0x8,%eax
     e25:	41 c1 e3 10          	shl    $0x10,%r11d
     e29:	44 09 d8             	or     %r11d,%eax
     e2c:	45 0f b6 1a          	movzbl (%r10),%r11d
     e30:	0f b6 dc             	movzbl %ah,%ebx
     e33:	c1 e8 10             	shr    $0x10,%eax
     e36:	29 d8                	sub    %ebx,%eax
     e38:	44 29 db             	sub    %r11d,%ebx
     e3b:	c1 e0 10             	shl    $0x10,%eax
     e3e:	c1 e3 08             	shl    $0x8,%ebx
     e41:	25 00 00 ff 00       	and    $0xff0000,%eax
     e46:	0f b7 db             	movzwl %bx,%ebx
     e49:	09 d8                	or     %ebx,%eax
     e4b:	44 09 d8             	or     %r11d,%eax
     e4e:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e52:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e56:	41 8b 03             	mov    (%r11),%eax
     e59:	45 0f b7 1b          	movzwl (%r11),%r11d
     e5d:	c1 e8 10             	shr    $0x10,%eax
     e60:	66 45 89 1a          	mov    %r11w,(%r10)
     e64:	41 88 42 02          	mov    %al,0x2(%r10)
     e68:	49 8d 41 03          	lea    0x3(%r9),%rax
     e6c:	48 39 c8             	cmp    %rcx,%rax
     e6f:	0f 83 83 01 00 00    	jae    ff8 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff8>
     e75:	4d 8d 54 10 09       	lea    0x9(%r8,%rdx,1),%r10
     e7a:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e7f:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e84:	c1 e0 10             	shl    $0x10,%eax
     e87:	41 c1 e3 08          	shl    $0x8,%r11d
     e8b:	44 09 d8             	or     %r11d,%eax
     e8e:	45 0f b6 1a          	movzbl (%r10),%r11d
     e92:	0f b6 dc             	movzbl %ah,%ebx
     e95:	c1 e8 10             	shr    $0x10,%eax
     e98:	29 d8                	sub    %ebx,%eax
     e9a:	44 29 db             	sub    %r11d,%ebx
     e9d:	c1 e0 10             	shl    $0x10,%eax
     ea0:	c1 e3 08             	shl    $0x8,%ebx
     ea3:	25 00 00 ff 00       	and    $0xff0000,%eax
     ea8:	0f b7 db             	movzwl %bx,%ebx
     eab:	09 d8                	or     %ebx,%eax
     ead:	44 09 d8             	or     %r11d,%eax
     eb0:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     eb4:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     eb8:	41 8b 03             	mov    (%r11),%eax
     ebb:	45 0f b7 1b          	movzwl (%r11),%r11d
     ebf:	c1 e8 10             	shr    $0x10,%eax
     ec2:	66 45 89 1a          	mov    %r11w,(%r10)
     ec6:	41 88 42 02          	mov    %al,0x2(%r10)
     eca:	49 8d 41 04          	lea    0x4(%r9),%rax
     ece:	48 39 c8             	cmp    %rcx,%rax
     ed1:	0f 83 21 01 00 00    	jae    ff8 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff8>
     ed7:	4d 8d 54 10 0c       	lea    0xc(%r8,%rdx,1),%r10
     edc:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     ee1:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     ee6:	c1 e0 10             	shl    $0x10,%eax
     ee9:	41 c1 e3 08          	shl    $0x8,%r11d
     eed:	44 09 d8             	or     %r11d,%eax
     ef0:	45 0f b6 1a          	movzbl (%r10),%r11d
     ef4:	0f b6 dc             	movzbl %ah,%ebx
     ef7:	c1 e8 10             	shr    $0x10,%eax
     efa:	29 d8                	sub    %ebx,%eax
     efc:	44 29 db             	sub    %r11d,%ebx
     eff:	c1 e0 10             	shl    $0x10,%eax
     f02:	c1 e3 08             	shl    $0x8,%ebx
     f05:	25 00 00 ff 00       	and    $0xff0000,%eax
     f0a:	0f b7 db             	movzwl %bx,%ebx
     f0d:	09 d8                	or     %ebx,%eax
     f0f:	44 09 d8             	or     %r11d,%eax
     f12:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f16:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f1a:	41 8b 03             	mov    (%r11),%eax
     f1d:	45 0f b7 1b          	movzwl (%r11),%r11d
     f21:	c1 e8 10             	shr    $0x10,%eax
     f24:	66 45 89 1a          	mov    %r11w,(%r10)
     f28:	41 88 42 02          	mov    %al,0x2(%r10)
     f2c:	49 8d 41 05          	lea    0x5(%r9),%rax
     f30:	48 39 c8             	cmp    %rcx,%rax
     f33:	0f 83 bf 00 00 00    	jae    ff8 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff8>
     f39:	4d 8d 54 10 0f       	lea    0xf(%r8,%rdx,1),%r10
     f3e:	49 83 c1 06          	add    $0x6,%r9
     f42:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     f47:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     f4c:	c1 e0 10             	shl    $0x10,%eax
     f4f:	41 c1 e3 08          	shl    $0x8,%r11d
     f53:	44 09 d8             	or     %r11d,%eax
     f56:	45 0f b6 1a          	movzbl (%r10),%r11d
     f5a:	0f b6 dc             	movzbl %ah,%ebx
     f5d:	c1 e8 10             	shr    $0x10,%eax
     f60:	29 d8                	sub    %ebx,%eax
     f62:	44 29 db             	sub    %r11d,%ebx
     f65:	c1 e0 10             	shl    $0x10,%eax
     f68:	c1 e3 08             	shl    $0x8,%ebx
     f6b:	25 00 00 ff 00       	and    $0xff0000,%eax
     f70:	0f b7 db             	movzwl %bx,%ebx
     f73:	09 d8                	or     %ebx,%eax
     f75:	44 09 d8             	or     %r11d,%eax
     f78:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f7c:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f80:	41 8b 03             	mov    (%r11),%eax
     f83:	45 0f b7 1b          	movzwl (%r11),%r11d
     f87:	c1 e8 10             	shr    $0x10,%eax
     f8a:	66 45 89 1a          	mov    %r11w,(%r10)
     f8e:	41 88 42 02          	mov    %al,0x2(%r10)
     f92:	49 39 c9             	cmp    %rcx,%r9
     f95:	73 61                	jae    ff8 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff8>
     f97:	49 8d 4c 10 12       	lea    0x12(%r8,%rdx,1),%rcx
     f9c:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
     fa0:	0f b6 51 02          	movzbl 0x2(%rcx),%edx
     fa4:	44 0f b6 01          	movzbl (%rcx),%r8d
     fa8:	c1 e2 10             	shl    $0x10,%edx
     fab:	c1 e0 08             	shl    $0x8,%eax
     fae:	09 d0                	or     %edx,%eax
     fb0:	0f b6 d4             	movzbl %ah,%edx
     fb3:	c1 e8 10             	shr    $0x10,%eax
     fb6:	29 d0                	sub    %edx,%eax
     fb8:	44 29 c2             	sub    %r8d,%edx
     fbb:	c1 e0 10             	shl    $0x10,%eax
     fbe:	c1 e2 08             	shl    $0x8,%edx
     fc1:	25 00 00 ff 00       	and    $0xff0000,%eax
     fc6:	0f b7 d2             	movzwl %dx,%edx
     fc9:	09 d0                	or     %edx,%eax
     fcb:	44 09 c0             	or     %r8d,%eax
     fce:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     fd2:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
     fd6:	8b 02                	mov    (%rdx),%eax
     fd8:	0f b7 12             	movzwl (%rdx),%edx
     fdb:	c1 e8 10             	shr    $0x10,%eax
     fde:	66 89 11             	mov    %dx,(%rcx)
     fe1:	88 41 02             	mov    %al,0x2(%rcx)
     fe4:	c5 f8 77             	vzeroupper
     fe7:	5b                   	pop    %rbx
     fe8:	41 5c                	pop    %r12
     fea:	41 5d                	pop    %r13
     fec:	41 5e                	pop    %r14
     fee:	41 5f                	pop    %r15
     ff0:	5d                   	pop    %rbp
     ff1:	c3                   	ret
     ff2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     ff8:	c5 f8 77             	vzeroupper
     ffb:	5b                   	pop    %rbx
     ffc:	41 5c                	pop    %r12
     ffe:	41 5d                	pop    %r13
    1000:	41 5e                	pop    %r14
    1002:	41 5f                	pop    %r15
    1004:	5d                   	pop    %rbp
    1005:	c3                   	ret
    1006:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    100d:	00 00 00 
    1010:	49 89 c9             	mov    %rcx,%r9
    1013:	e9 07 fc ff ff       	jmp    c1f <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc1f>
    1018:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    101f:	00 
    1020:	c3                   	ret
    1021:	48 8d 42 28          	lea    0x28(%rdx),%rax
    1025:	49 89 d1             	mov    %rdx,%r9
    1028:	e9 2b f8 ff ff       	jmp    858 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x858>
    102d:	0f 1f 00             	nopl   (%rax)

0000000000001030 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1030:	f3 0f 1e fa          	endbr64
    1034:	4d 85 c0             	test   %r8,%r8
    1037:	0f 84 db 10 00 00    	je     2118 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10e8>
    103d:	55                   	push   %rbp
    103e:	b8 00 04 00 00       	mov    $0x400,%eax
    1043:	49 89 d2             	mov    %rdx,%r10
    1046:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    104a:	49 89 cb             	mov    %rcx,%r11
    104d:	48 89 e5             	mov    %rsp,%rbp
    1050:	41 57                	push   %r15
    1052:	41 56                	push   %r14
    1054:	41 55                	push   %r13
    1056:	41 54                	push   %r12
    1058:	53                   	push   %rbx
    1059:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    105d:	48 39 c2             	cmp    %rax,%rdx
    1060:	48 0f 47 d0          	cmova  %rax,%rdx
    1064:	31 c0                	xor    %eax,%eax
    1066:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    106d:	00 00 00 
    1070:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
    1075:	48 83 c0 40          	add    $0x40,%rax
    1079:	48 39 d0             	cmp    %rdx,%rax
    107c:	72 f2                	jb     1070 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
    107e:	4d 89 d1             	mov    %r10,%r9
    1081:	4c 89 da             	mov    %r11,%rdx
    1084:	31 c9                	xor    %ecx,%ecx
    1086:	49 89 f7             	mov    %rsi,%r15
    1089:	eb 6a                	jmp    10f5 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc5>
    108b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1090:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
    1095:	41 0f b6 59 02       	movzbl 0x2(%r9),%ebx
    109a:	48 ff c1             	inc    %rcx
    109d:	48 83 c2 03          	add    $0x3,%rdx
    10a1:	49 83 c1 03          	add    $0x3,%r9
    10a5:	c1 e3 10             	shl    $0x10,%ebx
    10a8:	c1 e0 08             	shl    $0x8,%eax
    10ab:	09 d8                	or     %ebx,%eax
    10ad:	41 0f b6 59 fd       	movzbl -0x3(%r9),%ebx
    10b2:	0f b6 f4             	movzbl %ah,%esi
    10b5:	c1 e8 10             	shr    $0x10,%eax
    10b8:	41 89 f4             	mov    %esi,%r12d
    10bb:	29 f0                	sub    %esi,%eax
    10bd:	41 29 dc             	sub    %ebx,%r12d
    10c0:	c1 e0 10             	shl    $0x10,%eax
    10c3:	41 c1 e4 08          	shl    $0x8,%r12d
    10c7:	25 00 00 ff 00       	and    $0xff0000,%eax
    10cc:	45 0f b7 e4          	movzwl %r12w,%r12d
    10d0:	44 09 e0             	or     %r12d,%eax
    10d3:	09 d8                	or     %ebx,%eax
    10d5:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    10d9:	49 8d 1c 87          	lea    (%r15,%rax,4),%rbx
    10dd:	8b 03                	mov    (%rbx),%eax
    10df:	0f b7 1b             	movzwl (%rbx),%ebx
    10e2:	c1 e8 10             	shr    $0x10,%eax
    10e5:	66 89 5a fd          	mov    %bx,-0x3(%rdx)
    10e9:	88 42 ff             	mov    %al,-0x1(%rdx)
    10ec:	49 39 c8             	cmp    %rcx,%r8
    10ef:	0f 84 13 10 00 00    	je     2108 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10d8>
    10f5:	f6 c2 3f             	test   $0x3f,%dl
    10f8:	75 96                	jne    1090 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    10fa:	48 8d 41 48          	lea    0x48(%rcx),%rax
    10fe:	4c 89 fe             	mov    %r15,%rsi
    1101:	49 39 c0             	cmp    %rax,%r8
    1104:	0f 82 0f 10 00 00    	jb     2119 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10e9>
    110a:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    110e:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1116 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe6>
    1115:	00 
    1116:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 111e <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee>
    111d:	00 
    111e:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1123:	49 8d 14 03          	lea    (%r11,%rax,1),%rdx
    1127:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    112c:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1134 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x104>
    1133:	00 
    1134:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
    113b:	00 
    113c:	eb 05                	jmp    1143 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x113>
    113e:	66 90                	xchg   %ax,%ax
    1140:	4c 89 c9             	mov    %r9,%rcx
    1143:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    114a:	4d 39 c8             	cmp    %r9,%r8
    114d:	72 15                	jb     1164 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x134>
    114f:	0f 18 00             	prefetchnta (%rax)
    1152:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1156:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    115d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    1164:	c5 fa 6f 80 00 fc ff 	vmovdqu -0x400(%rax),%xmm0
    116b:	ff 
    116c:	c5 fa 7e 88 10 fc ff 	vmovq  -0x3f0(%rax),%xmm1
    1173:	ff 
    1174:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    117b:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1181:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1187:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    118d:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1192:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    1197:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    119b:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    11a1:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    11a6:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    11ac:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    11b1:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    11b7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    11bc:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    11c1:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    11c6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    11cb:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    11d1:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    11d7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    11dc:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    11e1:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    11e7:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    11ed:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    11f3:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    11f9:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    11fe:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1203:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    120a:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1211:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    1217:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    121b:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1220:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
    1227:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    122e:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    1232:	c5 fa 7e 88 68 fb ff 	vmovq  -0x498(%rax),%xmm1
    1239:	ff 
    123a:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    1240:	c5 fa 6f 80 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm0
    1247:	ff 
    1248:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    124d:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1253:	c4 42 55 36 c9       	vpermd %ymm9,%ymm5,%ymm9
    1258:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    125e:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1263:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    1268:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    126c:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1272:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1277:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    127d:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1282:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1288:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    128d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1292:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1297:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    129c:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    12a2:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    12a8:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    12ad:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    12b2:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    12b8:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    12be:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    12c4:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    12ca:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    12cf:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    12d4:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    12db:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    12e2:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    12e6:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    12eb:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    12f1:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    12f8:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    12ff:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
    1303:	c5 fa 7e 88 80 fb ff 	vmovq  -0x480(%rax),%xmm1
    130a:	ff 
    130b:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    1311:	c5 fa 6f 80 70 fb ff 	vmovdqu -0x490(%rax),%xmm0
    1318:	ff 
    1319:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    131e:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1324:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    1329:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    132f:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1334:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    1339:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    133d:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1343:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1348:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    134e:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1353:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1359:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    135e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1363:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1368:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    136d:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1373:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1379:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    137e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1383:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1389:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    138f:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1395:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    139b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    13a0:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    13a5:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
    13ac:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    13b3:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    13b9:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
    13bd:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    13c2:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    13c9:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    13d0:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    13d4:	c5 fa 7e b0 98 fb ff 	vmovq  -0x468(%rax),%xmm6
    13db:	ff 
    13dc:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    13e2:	c5 fa 6f 80 88 fb ff 	vmovdqu -0x478(%rax),%xmm0
    13e9:	ff 
    13ea:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    13ef:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    13f5:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    13fa:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1400:	c5 79 6f e9          	vmovdqa %xmm1,%xmm13
    1404:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    140a:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    140f:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
    1414:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
    1418:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    141e:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1423:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1429:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    142e:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    1434:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1439:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    143e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1443:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1448:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    144e:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1454:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    145a:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1460:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1465:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    146a:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    146f:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1474:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    147a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1480:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    1486:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
    148d:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1494:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    149b:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
    149f:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    14a4:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    14ab:	c5 39 6c c6          	vpunpcklqdq %xmm6,%xmm8,%xmm8
    14af:	c5 fa 7e b0 b0 fb ff 	vmovq  -0x450(%rax),%xmm6
    14b6:	ff 
    14b7:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    14bd:	c5 fa 6f 80 a0 fb ff 	vmovdqu -0x460(%rax),%xmm0
    14c4:	ff 
    14c5:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    14ca:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    14d0:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
    14d5:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    14db:	c4 41 79 6f f0       	vmovdqa %xmm8,%xmm14
    14e0:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    14e6:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    14eb:	c4 43 39 0f c6 08    	vpalignr $0x8,%xmm14,%xmm8,%xmm8
    14f1:	c4 c1 71 6c ce       	vpunpcklqdq %xmm14,%xmm1,%xmm1
    14f6:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
    14fb:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1501:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
    1505:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    150b:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1510:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1516:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    151b:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    1521:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1526:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    152b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1530:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1535:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    153b:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    1541:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1546:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    154b:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1551:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1557:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    155d:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1563:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1568:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    156d:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
    1574:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    157b:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    1581:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
    1585:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    158a:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    1591:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    1598:	c5 c1 6c fe          	vpunpcklqdq %xmm6,%xmm7,%xmm7
    159c:	c5 fa 7e b0 c8 fb ff 	vmovq  -0x438(%rax),%xmm6
    15a3:	ff 
    15a4:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    15aa:	c5 fa 6f 80 b8 fb ff 	vmovdqu -0x448(%rax),%xmm0
    15b1:	ff 
    15b2:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    15b7:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    15bd:	c4 e2 55 36 ff       	vpermd %ymm7,%ymm5,%ymm7
    15c2:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    15c8:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    15cd:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
    15d2:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
    15d6:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    15dc:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    15e1:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    15e7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    15ec:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    15f1:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    15f6:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    15fc:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1602:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1608:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    160d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1612:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1617:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    161c:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    1622:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1628:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    162d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1632:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1638:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
    163e:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1644:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    164b:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
    1652:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1659:	c4 c1 49 6c f2       	vpunpcklqdq %xmm10,%xmm6,%xmm6
    165e:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    1663:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    166a:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
    166f:	c5 7a 7e 90 e0 fb ff 	vmovq  -0x420(%rax),%xmm10
    1676:	ff 
    1677:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    167d:	c5 fa 6f b0 d0 fb ff 	vmovdqu -0x430(%rax),%xmm6
    1684:	ff 
    1685:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    168a:	c4 63 29 0f d6 0c    	vpalignr $0xc,%xmm6,%xmm10,%xmm10
    1690:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
    1695:	c4 c3 4d 38 f2 01    	vinserti128 $0x1,%xmm10,%ymm6,%ymm6
    169b:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
    16a0:	c5 ad 72 f6 08       	vpslld $0x8,%ymm6,%ymm10
    16a5:	c4 c1 4d f8 f2       	vpsubb %ymm10,%ymm6,%ymm6
    16aa:	c4 c3 7d 39 f2 01    	vextracti128 $0x1,%ymm6,%xmm10
    16b0:	c4 c1 79 7e f1       	vmovd  %xmm6,%r9d
    16b5:	c4 c3 79 16 f3 02    	vpextrd $0x2,%xmm6,%r11d
    16bb:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    16c0:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    16c6:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    16cb:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    16d0:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    16d5:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    16da:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    16e0:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    16e6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    16eb:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    16f0:	c4 c3 79 16 f1 01    	vpextrd $0x1,%xmm6,%r9d
    16f6:	c4 c3 79 16 f3 03    	vpextrd $0x3,%xmm6,%r11d
    16fc:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1702:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
    1708:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    170d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1712:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    1719:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
    1720:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    1726:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
    172b:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    1730:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    1737:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    173e:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1743:	c5 7a 7e 98 f8 fb ff 	vmovq  -0x408(%rax),%xmm11
    174a:	ff 
    174b:	c4 63 2d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm10,%ymm10
    1751:	c5 fa 6f b0 e8 fb ff 	vmovdqu -0x418(%rax),%xmm6
    1758:	ff 
    1759:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
    175e:	c4 63 21 0f de 0c    	vpalignr $0xc,%xmm6,%xmm11,%xmm11
    1764:	c4 42 55 36 d2       	vpermd %ymm10,%ymm5,%ymm10
    1769:	c4 c3 4d 38 f3 01    	vinserti128 $0x1,%xmm11,%ymm6,%ymm6
    176f:	c4 41 79 6f c2       	vmovdqa %xmm10,%xmm8
    1774:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
    177a:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
    177f:	c5 a5 72 f6 08       	vpslld $0x8,%ymm6,%ymm11
    1784:	c4 c1 4d f8 f3       	vpsubb %ymm11,%ymm6,%ymm6
    1789:	c4 c3 7d 39 f3 01    	vextracti128 $0x1,%ymm6,%xmm11
    178f:	c4 c1 79 7e f1       	vmovd  %xmm6,%r9d
    1794:	c4 c3 79 16 f3 02    	vpextrd $0x2,%xmm6,%r11d
    179a:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
    179f:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
    17a5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    17aa:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    17af:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    17b4:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    17b9:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
    17bf:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
    17c5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    17ca:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    17cf:	c4 c3 79 16 f1 01    	vpextrd $0x1,%xmm6,%r9d
    17d5:	c4 c3 79 16 f3 03    	vpextrd $0x3,%xmm6,%r11d
    17db:	c4 21 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm12
    17e1:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
    17e7:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    17ec:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    17f2:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    17f9:	c4 23 19 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm12,%xmm12
    1800:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
    1807:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    180c:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
    1813:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    1817:	c4 41 21 6c dc       	vpunpcklqdq %xmm12,%xmm11,%xmm11
    181c:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
    1821:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    1828:	c5 fd e7 4a 80       	vmovntdq %ymm1,-0x80(%rdx)
    182d:	c5 f9 6f cf          	vmovdqa %xmm7,%xmm1
    1831:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1837:	c4 c1 49 6c f4       	vpunpcklqdq %xmm12,%xmm6,%xmm6
    183c:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
    1840:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1846:	c4 c3 4d 38 f3 01    	vinserti128 $0x1,%xmm11,%ymm6,%ymm6
    184c:	c4 c3 69 0f d4 08    	vpalignr $0x8,%xmm12,%xmm2,%xmm2
    1852:	c4 41 79 6f d9       	vmovdqa %xmm9,%xmm11
    1857:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    185d:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1862:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
    1868:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    186d:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1872:	c5 fd e7 92 60 ff ff 	vmovntdq %ymm2,-0xa0(%rdx)
    1879:	ff 
    187a:	c4 43 25 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm11,%ymm9
    1880:	c5 f9 6f d6          	vmovdqa %xmm6,%xmm2
    1884:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    188a:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
    1891:	ff 
    1892:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    1896:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    189c:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
    18a0:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    18a6:	c4 e3 49 0f f2 08    	vpalignr $0x8,%xmm2,%xmm6,%xmm6
    18ac:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    18b1:	c4 e3 75 38 cf 01    	vinserti128 $0x1,%xmm7,%ymm1,%ymm1
    18b7:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    18bd:	c4 63 2d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm10,%ymm10
    18c3:	c5 fd e7 4a a0       	vmovntdq %ymm1,-0x60(%rdx)
    18c8:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    18cd:	c5 7d e7 52 e0       	vmovntdq %ymm10,-0x20(%rdx)
    18d2:	4d 39 d0             	cmp    %r10,%r8
    18d5:	0f 83 65 f8 ff ff    	jae    1140 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x110>
    18db:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    18e0:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    18e5:	48 8d 41 68          	lea    0x68(%rcx),%rax
    18e9:	0f ae f8             	sfence
    18ec:	49 39 c0             	cmp    %rax,%r8
    18ef:	0f 82 e4 03 00 00    	jb     1cd9 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xca9>
    18f5:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    18f9:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1901 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8d1>
    1900:	00 
    1901:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1909 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8d9>
    1908:	00 
    1909:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    190e:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1913:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 191b <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8eb>
    191a:	00 
    191b:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
    191f:	4c 01 da             	add    %r11,%rdx
    1922:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1928:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
    192c:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    1931:	48 83 c2 60          	add    $0x60,%rdx
    1935:	48 83 c0 60          	add    $0x60,%rax
    1939:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
    193e:	c5 fa 7e 70 e0       	vmovq  -0x20(%rax),%xmm6
    1943:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    1949:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    194f:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    1954:	c5 fd 72 f2 08       	vpslld $0x8,%ymm2,%ymm0
    1959:	c5 ed f8 d0          	vpsubb %ymm0,%ymm2,%ymm2
    195d:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
    1962:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
    1968:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
    196e:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1974:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    1979:	c5 fd 72 f1 08       	vpslld $0x8,%ymm1,%ymm0
    197e:	c5 f5 f8 c8          	vpsubb %ymm0,%ymm1,%ymm1
    1982:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
    1987:	c4 c3 7d 39 c8 01    	vextracti128 $0x1,%ymm1,%xmm8
    198d:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    1993:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1999:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    199e:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
    19a3:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
    19a7:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
    19ac:	c4 c3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm9
    19b2:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
    19b6:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
    19bb:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    19c1:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    19c7:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    19cc:	c5 cd 72 f0 08       	vpslld $0x8,%ymm0,%ymm6
    19d1:	c5 fd f8 c6          	vpsubb %ymm6,%ymm0,%ymm0
    19d5:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    19db:	c5 f9 7e c1          	vmovd  %xmm0,%ecx
    19df:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    19e5:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    19ea:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    19f0:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    19f5:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    19fa:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    19ff:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1a04:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    1a0a:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1a10:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1a15:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1a1a:	c4 e3 79 16 c1 01    	vpextrd $0x1,%xmm0,%ecx
    1a20:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1a26:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1a2c:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1a32:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1a36:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1a3b:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    1a42:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1a49:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    1a4f:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    1a55:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    1a5a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1a5f:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    1a65:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
    1a6a:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    1a6f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1a74:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    1a7a:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    1a81:	c5 79 7e d1          	vmovd  %xmm10,%ecx
    1a85:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1a8a:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    1a91:	c4 43 79 16 d3 02    	vpextrd $0x2,%xmm10,%r11d
    1a97:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1a9c:	c4 63 79 16 d1 01    	vpextrd $0x1,%xmm10,%ecx
    1aa2:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1aa7:	c4 43 79 16 d3 03    	vpextrd $0x3,%xmm10,%r11d
    1aad:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1ab1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1ab6:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1abb:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
    1ac0:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1ac6:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    1acc:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    1ad2:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1ad8:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1add:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    1ae4:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    1aeb:	c4 43 79 16 c6 02    	vpextrd $0x2,%xmm8,%r14d
    1af1:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
    1af8:	c4 41 79 7e c4       	vmovd  %xmm8,%r12d
    1afd:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1b02:	c4 43 79 16 c6 03    	vpextrd $0x3,%xmm8,%r14d
    1b08:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    1b0d:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    1b12:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1b17:	c4 43 79 16 c4 01    	vpextrd $0x1,%xmm8,%r12d
    1b1d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1b22:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1b27:	c5 f9 7e c9          	vmovd  %xmm1,%ecx
    1b2b:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1b30:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    1b37:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    1b3d:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1b43:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1b48:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1b4d:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    1b53:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1b59:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
    1b5e:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    1b65:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1b69:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    1b6e:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
    1b74:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    1b7a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1b7f:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1b85:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1b8a:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    1b90:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1b95:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    1b9c:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    1ba2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1ba7:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
    1bac:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    1bb3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1bb8:	c5 f9 7e d1          	vmovd  %xmm2,%ecx
    1bbc:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    1bc2:	c4 41 39 6c c1       	vpunpcklqdq %xmm9,%xmm8,%xmm8
    1bc7:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    1bcc:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1bd1:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    1bd7:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1bdb:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1be0:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1be7:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    1bed:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1bf2:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    1bf8:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
    1bfd:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1c02:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    1c06:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1c0c:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1c12:	c4 21 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm8
    1c18:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1c1e:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    1c24:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1c29:	c4 23 39 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm8,%xmm8
    1c30:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    1c37:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    1c3c:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1c43:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
    1c47:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1c4d:	c4 c1 41 6c f8       	vpunpcklqdq %xmm8,%xmm7,%xmm7
    1c52:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
    1c57:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
    1c5d:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1c61:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1c67:	49 83 c1 20          	add    $0x20,%r9
    1c6b:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
    1c72:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1c77:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
    1c7c:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
    1c80:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1c86:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
    1c8c:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
    1c92:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
    1c97:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1c9c:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1ca2:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    1ca7:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1cac:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    1cb0:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1cb6:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    1cbb:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
    1cc1:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1cc6:	49 39 c8             	cmp    %rcx,%r8
    1cc9:	0f 83 59 fc ff ff    	jae    1928 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8f8>
    1ccf:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1cd4:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1cd9:	49 8d 51 08          	lea    0x8(%r9),%rdx
    1cdd:	49 39 d0             	cmp    %rdx,%r8
    1ce0:	0f 82 33 01 00 00    	jb     1e19 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde9>
    1ce6:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1cea:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1cf2 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc2>
    1cf1:	00 
    1cf2:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1cfa <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcca>
    1cf9:	00 
    1cfa:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1cff:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1d04:	49 8d 0c 02          	lea    (%r10,%rax,1),%rcx
    1d08:	4c 01 d8             	add    %r11,%rax
    1d0b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1d10:	c5 fa 6f 01          	vmovdqu (%rcx),%xmm0
    1d14:	c5 fa 7e 49 10       	vmovq  0x10(%rcx),%xmm1
    1d19:	48 83 c0 18          	add    $0x18,%rax
    1d1d:	48 83 c1 18          	add    $0x18,%rcx
    1d21:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1d27:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1d2d:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1d32:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    1d37:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    1d3b:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1d41:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1d46:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1d4c:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1d51:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1d57:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1d5c:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1d61:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1d66:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1d6b:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1d71:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1d77:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1d7c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1d81:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1d87:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1d8d:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1d93:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1d99:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1d9e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1da3:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1daa:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1db1:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1db7:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1dbb:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1dc0:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1dc7:	49 89 d1             	mov    %rdx,%r9
    1dca:	48 83 c2 08          	add    $0x8,%rdx
    1dce:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    1dd5:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1dd9:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1ddf:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1de4:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1de8:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1dee:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1df3:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1df8:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1dfc:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    1e01:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
    1e06:	49 39 d0             	cmp    %rdx,%r8
    1e09:	0f 83 01 ff ff ff    	jae    1d10 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xce0>
    1e0f:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1e14:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1e19:	4d 39 c1             	cmp    %r8,%r9
    1e1c:	0f 83 ce 02 00 00    	jae    20f0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
    1e22:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1e26:	49 8d 1c 12          	lea    (%r10,%rdx,1),%rbx
    1e2a:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    1e2e:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1e33:	0f b6 1b             	movzbl (%rbx),%ebx
    1e36:	41 c1 e4 10          	shl    $0x10,%r12d
    1e3a:	c1 e0 08             	shl    $0x8,%eax
    1e3d:	44 09 e0             	or     %r12d,%eax
    1e40:	0f b6 cc             	movzbl %ah,%ecx
    1e43:	c1 e8 10             	shr    $0x10,%eax
    1e46:	41 89 cc             	mov    %ecx,%r12d
    1e49:	29 c8                	sub    %ecx,%eax
    1e4b:	41 29 dc             	sub    %ebx,%r12d
    1e4e:	c1 e0 10             	shl    $0x10,%eax
    1e51:	41 c1 e4 08          	shl    $0x8,%r12d
    1e55:	25 00 00 ff 00       	and    $0xff0000,%eax
    1e5a:	45 0f b7 e4          	movzwl %r12w,%r12d
    1e5e:	44 09 e0             	or     %r12d,%eax
    1e61:	09 d8                	or     %ebx,%eax
    1e63:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1e67:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    1e6b:	8b 03                	mov    (%rbx),%eax
    1e6d:	0f b7 1b             	movzwl (%rbx),%ebx
    1e70:	c1 e8 10             	shr    $0x10,%eax
    1e73:	66 41 89 1c 13       	mov    %bx,(%r11,%rdx,1)
    1e78:	41 88 44 13 02       	mov    %al,0x2(%r11,%rdx,1)
    1e7d:	49 8d 41 01          	lea    0x1(%r9),%rax
    1e81:	4c 39 c0             	cmp    %r8,%rax
    1e84:	0f 83 66 02 00 00    	jae    20f0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
    1e8a:	49 8d 5c 12 03       	lea    0x3(%r10,%rdx,1),%rbx
    1e8f:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    1e93:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1e98:	0f b6 1b             	movzbl (%rbx),%ebx
    1e9b:	41 c1 e4 10          	shl    $0x10,%r12d
    1e9f:	c1 e0 08             	shl    $0x8,%eax
    1ea2:	44 09 e0             	or     %r12d,%eax
    1ea5:	0f b6 cc             	movzbl %ah,%ecx
    1ea8:	c1 e8 10             	shr    $0x10,%eax
    1eab:	41 89 cc             	mov    %ecx,%r12d
    1eae:	29 c8                	sub    %ecx,%eax
    1eb0:	41 29 dc             	sub    %ebx,%r12d
    1eb3:	c1 e0 10             	shl    $0x10,%eax
    1eb6:	41 c1 e4 08          	shl    $0x8,%r12d
    1eba:	25 00 00 ff 00       	and    $0xff0000,%eax
    1ebf:	45 0f b7 e4          	movzwl %r12w,%r12d
    1ec3:	44 09 e0             	or     %r12d,%eax
    1ec6:	09 d8                	or     %ebx,%eax
    1ec8:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1ecc:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    1ed0:	8b 03                	mov    (%rbx),%eax
    1ed2:	0f b7 1b             	movzwl (%rbx),%ebx
    1ed5:	c1 e8 10             	shr    $0x10,%eax
    1ed8:	66 41 89 5c 13 03    	mov    %bx,0x3(%r11,%rdx,1)
    1ede:	41 88 44 13 05       	mov    %al,0x5(%r11,%rdx,1)
    1ee3:	49 8d 41 02          	lea    0x2(%r9),%rax
    1ee7:	4c 39 c0             	cmp    %r8,%rax
    1eea:	0f 83 00 02 00 00    	jae    20f0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
    1ef0:	49 8d 5c 12 06       	lea    0x6(%r10,%rdx,1),%rbx
    1ef5:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    1ef9:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1efe:	0f b6 1b             	movzbl (%rbx),%ebx
    1f01:	41 c1 e4 08          	shl    $0x8,%r12d
    1f05:	c1 e0 10             	shl    $0x10,%eax
    1f08:	44 09 e0             	or     %r12d,%eax
    1f0b:	0f b6 cc             	movzbl %ah,%ecx
    1f0e:	c1 e8 10             	shr    $0x10,%eax
    1f11:	41 89 cc             	mov    %ecx,%r12d
    1f14:	29 c8                	sub    %ecx,%eax
    1f16:	41 29 dc             	sub    %ebx,%r12d
    1f19:	c1 e0 10             	shl    $0x10,%eax
    1f1c:	41 c1 e4 08          	shl    $0x8,%r12d
    1f20:	25 00 00 ff 00       	and    $0xff0000,%eax
    1f25:	45 0f b7 e4          	movzwl %r12w,%r12d
    1f29:	44 09 e0             	or     %r12d,%eax
    1f2c:	09 d8                	or     %ebx,%eax
    1f2e:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1f32:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    1f36:	8b 03                	mov    (%rbx),%eax
    1f38:	0f b7 1b             	movzwl (%rbx),%ebx
    1f3b:	c1 e8 10             	shr    $0x10,%eax
    1f3e:	66 41 89 5c 13 06    	mov    %bx,0x6(%r11,%rdx,1)
    1f44:	41 88 44 13 08       	mov    %al,0x8(%r11,%rdx,1)
    1f49:	49 8d 41 03          	lea    0x3(%r9),%rax
    1f4d:	4c 39 c0             	cmp    %r8,%rax
    1f50:	0f 83 9a 01 00 00    	jae    20f0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
    1f56:	49 8d 5c 12 09       	lea    0x9(%r10,%rdx,1),%rbx
    1f5b:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    1f5f:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1f64:	0f b6 1b             	movzbl (%rbx),%ebx
    1f67:	41 c1 e4 08          	shl    $0x8,%r12d
    1f6b:	c1 e0 10             	shl    $0x10,%eax
    1f6e:	44 09 e0             	or     %r12d,%eax
    1f71:	0f b6 cc             	movzbl %ah,%ecx
    1f74:	c1 e8 10             	shr    $0x10,%eax
    1f77:	41 89 cc             	mov    %ecx,%r12d
    1f7a:	29 c8                	sub    %ecx,%eax
    1f7c:	41 29 dc             	sub    %ebx,%r12d
    1f7f:	c1 e0 10             	shl    $0x10,%eax
    1f82:	41 c1 e4 08          	shl    $0x8,%r12d
    1f86:	25 00 00 ff 00       	and    $0xff0000,%eax
    1f8b:	45 0f b7 e4          	movzwl %r12w,%r12d
    1f8f:	44 09 e0             	or     %r12d,%eax
    1f92:	09 d8                	or     %ebx,%eax
    1f94:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1f98:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    1f9c:	8b 03                	mov    (%rbx),%eax
    1f9e:	0f b7 1b             	movzwl (%rbx),%ebx
    1fa1:	c1 e8 10             	shr    $0x10,%eax
    1fa4:	66 41 89 5c 13 09    	mov    %bx,0x9(%r11,%rdx,1)
    1faa:	41 88 44 13 0b       	mov    %al,0xb(%r11,%rdx,1)
    1faf:	49 8d 41 04          	lea    0x4(%r9),%rax
    1fb3:	4c 39 c0             	cmp    %r8,%rax
    1fb6:	0f 83 34 01 00 00    	jae    20f0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
    1fbc:	49 8d 5c 12 0c       	lea    0xc(%r10,%rdx,1),%rbx
    1fc1:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    1fc5:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1fca:	0f b6 1b             	movzbl (%rbx),%ebx
    1fcd:	41 c1 e4 08          	shl    $0x8,%r12d
    1fd1:	c1 e0 10             	shl    $0x10,%eax
    1fd4:	44 09 e0             	or     %r12d,%eax
    1fd7:	0f b6 cc             	movzbl %ah,%ecx
    1fda:	c1 e8 10             	shr    $0x10,%eax
    1fdd:	41 89 cc             	mov    %ecx,%r12d
    1fe0:	29 c8                	sub    %ecx,%eax
    1fe2:	41 29 dc             	sub    %ebx,%r12d
    1fe5:	c1 e0 10             	shl    $0x10,%eax
    1fe8:	41 c1 e4 08          	shl    $0x8,%r12d
    1fec:	25 00 00 ff 00       	and    $0xff0000,%eax
    1ff1:	45 0f b7 e4          	movzwl %r12w,%r12d
    1ff5:	44 09 e0             	or     %r12d,%eax
    1ff8:	09 d8                	or     %ebx,%eax
    1ffa:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1ffe:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    2002:	8b 03                	mov    (%rbx),%eax
    2004:	0f b7 1b             	movzwl (%rbx),%ebx
    2007:	c1 e8 10             	shr    $0x10,%eax
    200a:	66 41 89 5c 13 0c    	mov    %bx,0xc(%r11,%rdx,1)
    2010:	41 88 44 13 0e       	mov    %al,0xe(%r11,%rdx,1)
    2015:	49 8d 41 05          	lea    0x5(%r9),%rax
    2019:	4c 39 c0             	cmp    %r8,%rax
    201c:	0f 83 ce 00 00 00    	jae    20f0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
    2022:	49 8d 5c 12 0f       	lea    0xf(%r10,%rdx,1),%rbx
    2027:	49 83 c1 06          	add    $0x6,%r9
    202b:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    202f:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    2034:	0f b6 1b             	movzbl (%rbx),%ebx
    2037:	41 c1 e4 08          	shl    $0x8,%r12d
    203b:	c1 e0 10             	shl    $0x10,%eax
    203e:	44 09 e0             	or     %r12d,%eax
    2041:	0f b6 cc             	movzbl %ah,%ecx
    2044:	c1 e8 10             	shr    $0x10,%eax
    2047:	41 89 cc             	mov    %ecx,%r12d
    204a:	29 c8                	sub    %ecx,%eax
    204c:	41 29 dc             	sub    %ebx,%r12d
    204f:	c1 e0 10             	shl    $0x10,%eax
    2052:	41 c1 e4 08          	shl    $0x8,%r12d
    2056:	25 00 00 ff 00       	and    $0xff0000,%eax
    205b:	45 0f b7 e4          	movzwl %r12w,%r12d
    205f:	44 09 e0             	or     %r12d,%eax
    2062:	09 d8                	or     %ebx,%eax
    2064:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2068:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    206c:	8b 03                	mov    (%rbx),%eax
    206e:	0f b7 1b             	movzwl (%rbx),%ebx
    2071:	c1 e8 10             	shr    $0x10,%eax
    2074:	66 41 89 5c 13 0f    	mov    %bx,0xf(%r11,%rdx,1)
    207a:	41 88 44 13 11       	mov    %al,0x11(%r11,%rdx,1)
    207f:	4d 39 c1             	cmp    %r8,%r9
    2082:	73 6c                	jae    20f0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
    2084:	49 8d 4c 13 12       	lea    0x12(%r11,%rdx,1),%rcx
    2089:	49 8d 54 12 12       	lea    0x12(%r10,%rdx,1),%rdx
    208e:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    2092:	44 0f b6 42 02       	movzbl 0x2(%rdx),%r8d
    2097:	c1 e0 08             	shl    $0x8,%eax
    209a:	41 c1 e0 10          	shl    $0x10,%r8d
    209e:	44 09 c0             	or     %r8d,%eax
    20a1:	44 0f b6 02          	movzbl (%rdx),%r8d
    20a5:	0f b6 d4             	movzbl %ah,%edx
    20a8:	c1 e8 10             	shr    $0x10,%eax
    20ab:	29 d0                	sub    %edx,%eax
    20ad:	44 29 c2             	sub    %r8d,%edx
    20b0:	c1 e0 10             	shl    $0x10,%eax
    20b3:	c1 e2 08             	shl    $0x8,%edx
    20b6:	25 00 00 ff 00       	and    $0xff0000,%eax
    20bb:	0f b7 d2             	movzwl %dx,%edx
    20be:	09 d0                	or     %edx,%eax
    20c0:	44 09 c0             	or     %r8d,%eax
    20c3:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    20c7:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    20cb:	8b 02                	mov    (%rdx),%eax
    20cd:	0f b7 12             	movzwl (%rdx),%edx
    20d0:	c1 e8 10             	shr    $0x10,%eax
    20d3:	66 89 11             	mov    %dx,(%rcx)
    20d6:	88 41 02             	mov    %al,0x2(%rcx)
    20d9:	c5 f8 77             	vzeroupper
    20dc:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    20e0:	5b                   	pop    %rbx
    20e1:	41 5c                	pop    %r12
    20e3:	41 5d                	pop    %r13
    20e5:	41 5e                	pop    %r14
    20e7:	41 5f                	pop    %r15
    20e9:	5d                   	pop    %rbp
    20ea:	c3                   	ret
    20eb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    20f0:	c5 f8 77             	vzeroupper
    20f3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    20f7:	5b                   	pop    %rbx
    20f8:	41 5c                	pop    %r12
    20fa:	41 5d                	pop    %r13
    20fc:	41 5e                	pop    %r14
    20fe:	41 5f                	pop    %r15
    2100:	5d                   	pop    %rbp
    2101:	c3                   	ret
    2102:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    2108:	4c 89 fe             	mov    %r15,%rsi
    210b:	4d 89 c1             	mov    %r8,%r9
    210e:	e9 c6 fb ff ff       	jmp    1cd9 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xca9>
    2113:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    2118:	c3                   	ret
    2119:	48 8d 41 28          	lea    0x28(%rcx),%rax
    211d:	49 89 c9             	mov    %rcx,%r9
    2120:	e9 c7 f7 ff ff       	jmp    18ec <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8bc>
