
artifacts/skylake-vectorpack-linux-build-v1/CMakeFiles/jshc_skylake_vectorpack.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 63 0e 00 00    	je     e70 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe70>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
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
      89:	0f 84 d1 0d 00 00    	je     e60 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe60>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 cf 0d 00 00    	jb     e71 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe71>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # ae <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # b6 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # be <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbe>
      bd:	00 
      be:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # c6 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc6>
      c5:	00 
      c6:	48 01 d0             	add    %rdx,%rax
      c9:	c5 7d 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm12        # d1 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd1>
      d0:	00 
      d1:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # d9 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd9>
      d8:	00 
      d9:	eb 08                	jmp    e3 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe3>
      db:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      e0:	4d 89 c1             	mov    %r8,%r9
      e3:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      ea:	4c 39 c1             	cmp    %r8,%rcx
      ed:	72 1c                	jb     10b <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10b>
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
     12b:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     131:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     136:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     13c:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     141:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     147:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     14c:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     151:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     156:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     15b:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     161:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     167:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     16c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     171:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     177:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     17d:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     183:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     189:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     18e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     193:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     19a:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     1a1:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     1a7:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     1ab:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     1b0:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     1b7:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1be:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     1c2:	c5 fa 7e 88 68 ff ff 	vmovq  -0x98(%rax),%xmm1
     1c9:	ff 
     1ca:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     1d0:	c5 fa 6f 80 58 ff ff 	vmovdqu -0xa8(%rax),%xmm0
     1d7:	ff 
     1d8:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     1dd:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     1e3:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
     1e8:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     1ee:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     1f3:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     1f9:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     1fe:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     204:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     209:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     20f:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     214:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     219:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     21e:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     223:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     229:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     22f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     234:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     239:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     23f:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     245:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     24b:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     251:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     256:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     25b:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     262:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     269:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     26e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     272:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     278:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     27f:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     286:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     28a:	c5 fa 7e 50 80       	vmovq  -0x80(%rax),%xmm2
     28f:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     295:	c5 fa 6f 80 70 ff ff 	vmovdqu -0x90(%rax),%xmm0
     29c:	ff 
     29d:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     2a2:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
     2a8:	c4 e2 15 36 c9       	vpermd %ymm1,%ymm13,%ymm1
     2ad:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     2b3:	c4 63 3d 02 c1 c0    	vpblendd $0xc0,%ymm1,%ymm8,%ymm8
     2b9:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     2be:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
     2c4:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     2c9:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     2cf:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     2d4:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     2da:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     2df:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     2e4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     2e9:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     2ee:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     2f4:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     2fa:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2ff:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     304:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     30a:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     310:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     316:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     31c:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     321:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     326:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     32d:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     334:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
     33a:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     33e:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     343:	c4 23 29 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm10,%xmm10
     34a:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     351:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     355:	c5 fa 7e 50 98       	vmovq  -0x68(%rax),%xmm2
     35a:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
     360:	c5 fa 6f 40 88       	vmovdqu -0x78(%rax),%xmm0
     365:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
     36a:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
     370:	c4 42 1d 36 d2       	vpermd %ymm10,%ymm12,%ymm10
     375:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     37b:	c4 c3 75 0c ca f0    	vblendps $0xf0,%ymm10,%ymm1,%ymm1
     381:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     386:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
     38c:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     391:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     397:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     39c:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     3a2:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     3a7:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     3ac:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     3b1:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     3b6:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     3bc:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     3c2:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     3c8:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     3ce:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     3d3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     3d8:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3dd:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     3e2:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     3e8:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     3ee:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     3f4:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     3fb:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     402:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     409:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     40d:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     412:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     419:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     41d:	c5 fa 7e 50 b0       	vmovq  -0x50(%rax),%xmm2
     422:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     428:	c5 fa 6f 40 a0       	vmovdqu -0x60(%rax),%xmm0
     42d:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     432:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
     438:	c4 e2 25 36 ff       	vpermd %ymm7,%ymm11,%ymm7
     43d:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     443:	c4 c3 45 02 fa 03    	vpblendd $0x3,%ymm10,%ymm7,%ymm7
     449:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     44e:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
     454:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     459:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     45f:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     464:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     46a:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     46f:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     474:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     479:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     47e:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     484:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     48a:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     48f:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     494:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     49a:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     4a0:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     4a6:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     4ac:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     4b1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     4b6:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     4bd:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     4c4:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     4ca:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     4ce:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     4d3:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     4da:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     4e1:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     4e5:	c5 fa 7e 50 c8       	vmovq  -0x38(%rax),%xmm2
     4ea:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     4f0:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
     4f5:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     4fa:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
     500:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     505:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     50b:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     510:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
     516:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     51b:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     521:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     526:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     52b:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     530:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     536:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     53c:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     542:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     547:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     54c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     551:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     556:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     55c:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     562:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     567:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     56c:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     572:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     578:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     57d:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     584:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     58b:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     592:	c5 e9 6c d0          	vpunpcklqdq %xmm0,%xmm2,%xmm2
     596:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     59c:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     5a3:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
     5a8:	c5 7a 7e 48 e0       	vmovq  -0x20(%rax),%xmm9
     5ad:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     5b3:	c5 fa 6f 50 d0       	vmovdqu -0x30(%rax),%xmm2
     5b8:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     5bd:	c4 63 31 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm9,%xmm9
     5c3:	c4 e2 15 36 c0       	vpermd %ymm0,%ymm13,%ymm0
     5c8:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
     5ce:	c4 e3 4d 02 f0 c0    	vpblendd $0xc0,%ymm0,%ymm6,%ymm6
     5d4:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     5d9:	c4 c3 7d 39 d1 01    	vextracti128 $0x1,%ymm2,%xmm9
     5df:	c4 c1 79 7e d0       	vmovd  %xmm2,%r8d
     5e4:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     5ea:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     5ef:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     5f5:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5fa:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     5ff:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     604:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     609:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     60f:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     615:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     61a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     61f:	c4 c3 79 16 d0 01    	vpextrd $0x1,%xmm2,%r8d
     625:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     62b:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
     631:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     637:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     63c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     641:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
     648:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     64f:	c5 79 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm14
     654:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     659:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     65f:	c4 23 09 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm14,%xmm14
     666:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     66d:	c4 41 31 6c ce       	vpunpcklqdq %xmm14,%xmm9,%xmm9
     672:	c5 7a 7e 70 f8       	vmovq  -0x8(%rax),%xmm14
     677:	c4 63 35 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm9,%ymm9
     67d:	c5 fa 6f 50 e8       	vmovdqu -0x18(%rax),%xmm2
     682:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     687:	c4 63 09 0f f2 0c    	vpalignr $0xc,%xmm2,%xmm14,%xmm14
     68d:	c4 42 1d 36 c9       	vpermd %ymm9,%ymm12,%ymm9
     692:	c4 c3 6d 38 d6 01    	vinserti128 $0x1,%xmm14,%ymm2,%ymm2
     698:	c4 c3 7d 0c c1 f0    	vblendps $0xf0,%ymm9,%ymm0,%ymm0
     69e:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     6a3:	c4 c3 7d 39 d6 01    	vextracti128 $0x1,%ymm2,%xmm14
     6a9:	c4 c1 79 7e d0       	vmovd  %xmm2,%r8d
     6ae:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     6b4:	c4 41 79 7e f4       	vmovd  %xmm14,%r12d
     6b9:	c4 43 79 16 f6 02    	vpextrd $0x2,%xmm14,%r14d
     6bf:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     6c4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     6c9:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     6ce:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     6d3:	c4 43 79 16 f4 01    	vpextrd $0x1,%xmm14,%r12d
     6d9:	c4 43 79 16 f6 03    	vpextrd $0x3,%xmm14,%r14d
     6df:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     6e4:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     6e9:	c4 c3 79 16 d0 01    	vpextrd $0x1,%xmm2,%r8d
     6ef:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     6f5:	c4 21 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm14
     6fb:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     701:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     706:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     70b:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     712:	c4 23 09 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm14,%xmm14
     719:	c5 79 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm15
     71e:	c5 09 6c f2          	vpunpcklqdq %xmm2,%xmm14,%xmm14
     722:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     728:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     72f:	c4 23 01 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm15,%xmm15
     736:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     73d:	c5 7d e7 80 40 ff ff 	vmovntdq %ymm8,-0xc0(%rax)
     744:	ff 
     745:	c5 fd e7 88 60 ff ff 	vmovntdq %ymm1,-0xa0(%rax)
     74c:	ff 
     74d:	c5 fd e7 78 80       	vmovntdq %ymm7,-0x80(%rax)
     752:	c5 fd e7 70 a0       	vmovntdq %ymm6,-0x60(%rax)
     757:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     75c:	4d 8d 41 40          	lea    0x40(%r9),%r8
     760:	c4 c1 69 6c d7       	vpunpcklqdq %xmm15,%xmm2,%xmm2
     765:	c4 c3 6d 38 d6 01    	vinserti128 $0x1,%xmm14,%ymm2,%ymm2
     76b:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     770:	c4 e2 25 36 d2       	vpermd %ymm2,%ymm11,%ymm2
     775:	c4 c3 6d 02 d1 03    	vpblendd $0x3,%ymm9,%ymm2,%ymm2
     77b:	c5 fd e7 50 e0       	vmovntdq %ymm2,-0x20(%rax)
     780:	4c 39 d1             	cmp    %r10,%rcx
     783:	0f 83 57 f9 ff ff    	jae    e0 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe0>
     789:	0f ae f8             	sfence
     78c:	49 8d 41 68          	lea    0x68(%r9),%rax
     790:	48 39 c1             	cmp    %rax,%rcx
     793:	0f 82 a6 03 00 00    	jb     b3f <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb3f>
     799:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     79d:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 7a5 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7a5>
     7a4:	00 
     7a5:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 7ad <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7ad>
     7ac:	00 
     7ad:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 7b5 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7b5>
     7b4:	00 
     7b5:	48 01 d0             	add    %rdx,%rax
     7b8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     7bf:	00 
     7c0:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     7c4:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
     7c9:	48 83 c0 60          	add    $0x60,%rax
     7cd:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     7d2:	c5 7a 6f 40 d0       	vmovdqu -0x30(%rax),%xmm8
     7d7:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
     7dd:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
     7e2:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     7e8:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
     7ed:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     7f2:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
     7f8:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
     7fe:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     804:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
     809:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     80e:	c4 c3 79 0f c0 0c    	vpalignr $0xc,%xmm8,%xmm0,%xmm0
     814:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
     81a:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     820:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
     825:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
     82a:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     830:	c4 43 7d 39 c2 01    	vextracti128 $0x1,%ymm8,%xmm10
     836:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     83c:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     841:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     847:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     84c:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     852:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     857:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     85d:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     862:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     867:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     86c:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     871:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     877:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     87d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     882:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     887:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     88d:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     893:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     899:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     89f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     8a4:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     8a9:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     8b0:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     8b7:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     8bd:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     8c2:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     8c7:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     8cc:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     8d2:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     8d6:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     8dc:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     8e1:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     8e7:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     8ee:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
     8f4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     8f9:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
     900:	c4 41 79 7e c1       	vmovd  %xmm8,%r9d
     905:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     90a:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
     910:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     915:	c4 43 79 16 c1 01    	vpextrd $0x1,%xmm8,%r9d
     91b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     920:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
     925:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     92a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     92f:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     935:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     93b:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     941:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     946:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     94b:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     952:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     959:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     95f:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     966:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     96b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     970:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     976:	c5 39 6c c0          	vpunpcklqdq %xmm0,%xmm8,%xmm8
     97a:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     980:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     985:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     98b:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     991:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     996:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     99b:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     9a1:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     9a8:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
     9ad:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     9b2:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     9b7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     9bc:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
     9c2:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     9c8:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
     9cd:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     9d2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     9d7:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     9dd:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     9e3:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     9ea:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     9f0:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     9f5:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9fa:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     a00:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     a05:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     a0c:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     a11:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a16:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
     a1b:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     a22:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a27:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     a2d:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     a33:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     a37:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     a3d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     a42:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     a48:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a4d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a52:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     a59:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
     a5e:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     a63:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
     a69:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a6e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     a74:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
     a79:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     a7d:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     a83:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     a89:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
     a8e:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     a94:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     a9b:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     aa0:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     aa7:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
     aae:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     ab3:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
     ab7:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     abd:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     ac1:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     ac7:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
     acd:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     ad3:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     ada:	4d 8d 48 48          	lea    0x48(%r8),%r9
     ade:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     ae3:	49 83 c0 20          	add    $0x20,%r8
     ae7:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
     aec:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
     af0:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     af6:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
     afc:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
     b02:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
     b07:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     b0c:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     b12:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     b17:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     b1c:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     b20:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     b26:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
     b2b:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
     b31:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     b36:	4c 39 c9             	cmp    %r9,%rcx
     b39:	0f 83 81 fc ff ff    	jae    7c0 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7c0>
     b3f:	4d 8d 48 08          	lea    0x8(%r8),%r9
     b43:	4c 39 c9             	cmp    %r9,%rcx
     b46:	0f 82 0e 01 00 00    	jb     c5a <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc5a>
     b4c:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     b50:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # b58 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb58>
     b57:	00 
     b58:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # b60 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb60>
     b5f:	00 
     b60:	48 01 d0             	add    %rdx,%rax
     b63:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     b68:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     b6c:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     b71:	48 83 c0 18          	add    $0x18,%rax
     b75:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     b7b:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     b81:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     b86:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     b8c:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     b91:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     b97:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     b9c:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     ba2:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     ba7:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     bac:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     bb1:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     bb6:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     bbc:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     bc2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     bc7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     bcc:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     bd2:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     bd8:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     bde:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     be4:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     be9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     bee:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     bf5:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     bfc:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     c01:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     c05:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     c0b:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     c12:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     c19:	4d 89 c8             	mov    %r9,%r8
     c1c:	49 83 c1 08          	add    $0x8,%r9
     c20:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     c24:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     c2a:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     c2f:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     c33:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     c39:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     c3e:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     c43:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     c47:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     c4c:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     c51:	4c 39 c9             	cmp    %r9,%rcx
     c54:	0f 83 0e ff ff ff    	jae    b68 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb68>
     c5a:	49 39 c8             	cmp    %rcx,%r8
     c5d:	0f 83 ed 01 00 00    	jae    e50 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
     c63:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     c67:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     c6b:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     c70:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     c75:	c1 e0 08             	shl    $0x8,%eax
     c78:	41 c1 e3 10          	shl    $0x10,%r11d
     c7c:	44 09 d8             	or     %r11d,%eax
     c7f:	45 0f b6 1a          	movzbl (%r10),%r11d
     c83:	44 09 d8             	or     %r11d,%eax
     c86:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     c8a:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     c8e:	41 8b 03             	mov    (%r11),%eax
     c91:	45 0f b7 1b          	movzwl (%r11),%r11d
     c95:	c1 e8 10             	shr    $0x10,%eax
     c98:	66 45 89 1a          	mov    %r11w,(%r10)
     c9c:	41 88 42 02          	mov    %al,0x2(%r10)
     ca0:	49 8d 40 01          	lea    0x1(%r8),%rax
     ca4:	48 39 c8             	cmp    %rcx,%rax
     ca7:	0f 83 a3 01 00 00    	jae    e50 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
     cad:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     cb2:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     cb7:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     cbc:	c1 e0 08             	shl    $0x8,%eax
     cbf:	41 c1 e3 10          	shl    $0x10,%r11d
     cc3:	44 09 d8             	or     %r11d,%eax
     cc6:	45 0f b6 1a          	movzbl (%r10),%r11d
     cca:	44 09 d8             	or     %r11d,%eax
     ccd:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     cd1:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     cd5:	41 8b 03             	mov    (%r11),%eax
     cd8:	45 0f b7 1b          	movzwl (%r11),%r11d
     cdc:	c1 e8 10             	shr    $0x10,%eax
     cdf:	66 45 89 1a          	mov    %r11w,(%r10)
     ce3:	41 88 42 02          	mov    %al,0x2(%r10)
     ce7:	49 8d 40 02          	lea    0x2(%r8),%rax
     ceb:	48 39 c8             	cmp    %rcx,%rax
     cee:	0f 83 5c 01 00 00    	jae    e50 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
     cf4:	4e 8d 54 0a 06       	lea    0x6(%rdx,%r9,1),%r10
     cf9:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     cfe:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d03:	c1 e0 08             	shl    $0x8,%eax
     d06:	41 c1 e3 10          	shl    $0x10,%r11d
     d0a:	44 09 d8             	or     %r11d,%eax
     d0d:	45 0f b6 1a          	movzbl (%r10),%r11d
     d11:	44 09 d8             	or     %r11d,%eax
     d14:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d18:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d1c:	41 8b 03             	mov    (%r11),%eax
     d1f:	45 0f b7 1b          	movzwl (%r11),%r11d
     d23:	c1 e8 10             	shr    $0x10,%eax
     d26:	66 45 89 1a          	mov    %r11w,(%r10)
     d2a:	41 88 42 02          	mov    %al,0x2(%r10)
     d2e:	49 8d 40 03          	lea    0x3(%r8),%rax
     d32:	48 39 c8             	cmp    %rcx,%rax
     d35:	0f 83 15 01 00 00    	jae    e50 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
     d3b:	4e 8d 54 0a 09       	lea    0x9(%rdx,%r9,1),%r10
     d40:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     d45:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     d4a:	c1 e0 10             	shl    $0x10,%eax
     d4d:	41 c1 e3 08          	shl    $0x8,%r11d
     d51:	44 09 d8             	or     %r11d,%eax
     d54:	45 0f b6 1a          	movzbl (%r10),%r11d
     d58:	44 09 d8             	or     %r11d,%eax
     d5b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d5f:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d63:	41 8b 03             	mov    (%r11),%eax
     d66:	45 0f b7 1b          	movzwl (%r11),%r11d
     d6a:	c1 e8 10             	shr    $0x10,%eax
     d6d:	66 45 89 1a          	mov    %r11w,(%r10)
     d71:	41 88 42 02          	mov    %al,0x2(%r10)
     d75:	49 8d 40 04          	lea    0x4(%r8),%rax
     d79:	48 39 c8             	cmp    %rcx,%rax
     d7c:	0f 83 ce 00 00 00    	jae    e50 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
     d82:	4e 8d 54 0a 0c       	lea    0xc(%rdx,%r9,1),%r10
     d87:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     d8c:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     d91:	c1 e0 10             	shl    $0x10,%eax
     d94:	41 c1 e3 08          	shl    $0x8,%r11d
     d98:	44 09 d8             	or     %r11d,%eax
     d9b:	45 0f b6 1a          	movzbl (%r10),%r11d
     d9f:	44 09 d8             	or     %r11d,%eax
     da2:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     da6:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     daa:	41 8b 03             	mov    (%r11),%eax
     dad:	45 0f b7 1b          	movzwl (%r11),%r11d
     db1:	c1 e8 10             	shr    $0x10,%eax
     db4:	66 45 89 1a          	mov    %r11w,(%r10)
     db8:	41 88 42 02          	mov    %al,0x2(%r10)
     dbc:	49 8d 40 05          	lea    0x5(%r8),%rax
     dc0:	48 39 c8             	cmp    %rcx,%rax
     dc3:	0f 83 87 00 00 00    	jae    e50 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
     dc9:	4e 8d 54 0a 0f       	lea    0xf(%rdx,%r9,1),%r10
     dce:	49 83 c0 06          	add    $0x6,%r8
     dd2:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     dd7:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     ddc:	c1 e0 10             	shl    $0x10,%eax
     ddf:	41 c1 e3 08          	shl    $0x8,%r11d
     de3:	44 09 d8             	or     %r11d,%eax
     de6:	45 0f b6 1a          	movzbl (%r10),%r11d
     dea:	44 09 d8             	or     %r11d,%eax
     ded:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     df1:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     df5:	41 8b 03             	mov    (%r11),%eax
     df8:	45 0f b7 1b          	movzwl (%r11),%r11d
     dfc:	c1 e8 10             	shr    $0x10,%eax
     dff:	66 45 89 1a          	mov    %r11w,(%r10)
     e03:	41 88 42 02          	mov    %al,0x2(%r10)
     e07:	49 39 c8             	cmp    %rcx,%r8
     e0a:	73 44                	jae    e50 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe50>
     e0c:	4a 8d 54 0a 12       	lea    0x12(%rdx,%r9,1),%rdx
     e11:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     e15:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     e19:	c1 e0 08             	shl    $0x8,%eax
     e1c:	c1 e1 10             	shl    $0x10,%ecx
     e1f:	09 c8                	or     %ecx,%eax
     e21:	0f b6 0a             	movzbl (%rdx),%ecx
     e24:	09 c8                	or     %ecx,%eax
     e26:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e2a:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     e2e:	8b 01                	mov    (%rcx),%eax
     e30:	0f b7 09             	movzwl (%rcx),%ecx
     e33:	c1 e8 10             	shr    $0x10,%eax
     e36:	66 89 0a             	mov    %cx,(%rdx)
     e39:	88 42 02             	mov    %al,0x2(%rdx)
     e3c:	c5 f8 77             	vzeroupper
     e3f:	5b                   	pop    %rbx
     e40:	41 5c                	pop    %r12
     e42:	41 5d                	pop    %r13
     e44:	41 5e                	pop    %r14
     e46:	41 5f                	pop    %r15
     e48:	5d                   	pop    %rbp
     e49:	c3                   	ret
     e4a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     e50:	c5 f8 77             	vzeroupper
     e53:	5b                   	pop    %rbx
     e54:	41 5c                	pop    %r12
     e56:	41 5d                	pop    %r13
     e58:	41 5e                	pop    %r14
     e5a:	41 5f                	pop    %r15
     e5c:	5d                   	pop    %rbp
     e5d:	c3                   	ret
     e5e:	66 90                	xchg   %ax,%ax
     e60:	49 89 c8             	mov    %rcx,%r8
     e63:	e9 d7 fc ff ff       	jmp    b3f <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb3f>
     e68:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     e6f:	00 
     e70:	c3                   	ret
     e71:	49 8d 41 28          	lea    0x28(%r9),%rax
     e75:	4d 89 c8             	mov    %r9,%r8
     e78:	e9 13 f9 ff ff       	jmp    790 <jshc_channel::avx2_chain_vectorpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x790>
     e7d:	0f 1f 00             	nopl   (%rax)

0000000000000e80 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     e80:	f3 0f 1e fa          	endbr64
     e84:	4d 85 c0             	test   %r8,%r8
     e87:	0f 84 03 0f 00 00    	je     1d90 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf10>
     e8d:	55                   	push   %rbp
     e8e:	b8 00 04 00 00       	mov    $0x400,%eax
     e93:	49 89 d2             	mov    %rdx,%r10
     e96:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     e9a:	49 89 cb             	mov    %rcx,%r11
     e9d:	48 89 e5             	mov    %rsp,%rbp
     ea0:	41 57                	push   %r15
     ea2:	41 56                	push   %r14
     ea4:	41 55                	push   %r13
     ea6:	41 54                	push   %r12
     ea8:	53                   	push   %rbx
     ea9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     ead:	48 39 c2             	cmp    %rax,%rdx
     eb0:	48 0f 47 d0          	cmova  %rax,%rdx
     eb4:	31 c0                	xor    %eax,%eax
     eb6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     ebd:	00 00 00 
     ec0:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
     ec5:	48 83 c0 40          	add    $0x40,%rax
     ec9:	48 39 d0             	cmp    %rdx,%rax
     ecc:	72 f2                	jb     ec0 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     ece:	4d 89 d1             	mov    %r10,%r9
     ed1:	4c 89 da             	mov    %r11,%rdx
     ed4:	31 c9                	xor    %ecx,%ecx
     ed6:	eb 4c                	jmp    f24 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa4>
     ed8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     edf:	00 
     ee0:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     ee5:	41 0f b6 59 02       	movzbl 0x2(%r9),%ebx
     eea:	48 ff c1             	inc    %rcx
     eed:	48 83 c2 03          	add    $0x3,%rdx
     ef1:	49 83 c1 03          	add    $0x3,%r9
     ef5:	c1 e3 10             	shl    $0x10,%ebx
     ef8:	c1 e0 08             	shl    $0x8,%eax
     efb:	09 d8                	or     %ebx,%eax
     efd:	41 0f b6 59 fd       	movzbl -0x3(%r9),%ebx
     f02:	09 d8                	or     %ebx,%eax
     f04:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f08:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
     f0c:	8b 03                	mov    (%rbx),%eax
     f0e:	0f b7 1b             	movzwl (%rbx),%ebx
     f11:	c1 e8 10             	shr    $0x10,%eax
     f14:	66 89 5a fd          	mov    %bx,-0x3(%rdx)
     f18:	88 42 ff             	mov    %al,-0x1(%rdx)
     f1b:	49 39 c8             	cmp    %rcx,%r8
     f1e:	0f 84 5c 0e 00 00    	je     1d80 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf00>
     f24:	f6 c2 3f             	test   $0x3f,%dl
     f27:	75 b7                	jne    ee0 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     f29:	48 8d 41 48          	lea    0x48(%rcx),%rax
     f2d:	49 39 c0             	cmp    %rax,%r8
     f30:	0f 82 5b 0e 00 00    	jb     1d91 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf11>
     f36:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     f3a:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # f42 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc2>
     f41:	00 
     f42:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # f4a <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xca>
     f49:	00 
     f4a:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
     f4f:	49 8d 14 03          	lea    (%r11,%rax,1),%rdx
     f53:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
     f58:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # f60 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe0>
     f5f:	00 
     f60:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
     f67:	00 
     f68:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # f70 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
     f6f:	00 
     f70:	c5 7d 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm12        # f78 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf8>
     f77:	00 
     f78:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # f80 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x100>
     f7f:	00 
     f80:	eb 09                	jmp    f8b <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10b>
     f82:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     f88:	4c 89 c9             	mov    %r9,%rcx
     f8b:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
     f92:	4d 39 c8             	cmp    %r9,%r8
     f95:	72 15                	jb     fac <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c>
     f97:	0f 18 00             	prefetchnta (%rax)
     f9a:	0f 18 40 40          	prefetchnta 0x40(%rax)
     f9e:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
     fa5:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
     fac:	c5 fa 6f 80 00 fc ff 	vmovdqu -0x400(%rax),%xmm0
     fb3:	ff 
     fb4:	c5 fa 7e 88 10 fc ff 	vmovq  -0x3f0(%rax),%xmm1
     fbb:	ff 
     fbc:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
     fc3:	48 05 c0 00 00 00    	add    $0xc0,%rax
     fc9:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     fcf:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     fd5:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     fda:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     fe0:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     fe5:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     feb:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     ff0:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     ff6:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     ffb:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1000:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1005:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    100a:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1010:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1016:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    101b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1020:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1026:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    102c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1032:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1038:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    103d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1042:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1049:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1050:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    1056:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    105a:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    105f:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    1066:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    106d:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    1071:	c5 fa 7e 88 68 fb ff 	vmovq  -0x498(%rax),%xmm1
    1078:	ff 
    1079:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    107f:	c5 fa 6f 80 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm0
    1086:	ff 
    1087:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    108c:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1092:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
    1097:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    109d:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    10a2:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    10a8:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    10ad:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    10b3:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    10b8:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    10be:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    10c3:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    10c8:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    10cd:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    10d2:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    10d8:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    10de:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    10e3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    10e8:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    10ee:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    10f4:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    10fa:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1100:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1105:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    110a:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1111:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1118:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    111c:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1121:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1127:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    112e:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1135:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1139:	c5 fa 7e 90 80 fb ff 	vmovq  -0x480(%rax),%xmm2
    1140:	ff 
    1141:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1147:	c5 fa 6f 80 70 fb ff 	vmovdqu -0x490(%rax),%xmm0
    114e:	ff 
    114f:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1154:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
    115a:	c4 e2 15 36 c9       	vpermd %ymm1,%ymm13,%ymm1
    115f:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    1165:	c4 63 3d 02 c1 c0    	vpblendd $0xc0,%ymm1,%ymm8,%ymm8
    116b:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1170:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
    1176:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    117b:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1181:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    1186:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    118c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1191:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1196:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    119b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    11a0:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    11a6:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    11ac:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    11b1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    11b6:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    11bc:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    11c2:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    11c8:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    11ce:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    11d3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    11d8:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    11df:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    11e6:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    11ec:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    11f0:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    11f5:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    11fc:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    1203:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
    1207:	c5 fa 7e 90 98 fb ff 	vmovq  -0x468(%rax),%xmm2
    120e:	ff 
    120f:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
    1215:	c5 fa 6f 80 88 fb ff 	vmovdqu -0x478(%rax),%xmm0
    121c:	ff 
    121d:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
    1222:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
    1228:	c4 42 1d 36 d2       	vpermd %ymm10,%ymm12,%ymm10
    122d:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    1233:	c4 c3 75 0c ca f0    	vblendps $0xf0,%ymm10,%ymm1,%ymm1
    1239:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    123e:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
    1244:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1249:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    124f:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    1254:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    125a:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    125f:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1264:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1269:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    126e:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1274:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    127a:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1280:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    1286:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    128b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1290:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1295:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    129a:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    12a0:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    12a6:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    12ac:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    12b3:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    12ba:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    12c1:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    12c5:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    12ca:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    12d1:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
    12d5:	c5 fa 7e 90 b0 fb ff 	vmovq  -0x450(%rax),%xmm2
    12dc:	ff 
    12dd:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    12e3:	c5 fa 6f 80 a0 fb ff 	vmovdqu -0x460(%rax),%xmm0
    12ea:	ff 
    12eb:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    12f0:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
    12f6:	c4 e2 25 36 ff       	vpermd %ymm7,%ymm11,%ymm7
    12fb:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    1301:	c4 c3 45 02 fa 03    	vpblendd $0x3,%ymm10,%ymm7,%ymm7
    1307:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    130c:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
    1312:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1317:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    131d:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    1322:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    1328:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    132d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1332:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1337:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    133c:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    1342:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1348:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    134d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1352:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1358:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    135e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1364:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    136a:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    136f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1374:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    137b:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1382:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    1388:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    138c:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1391:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
    1398:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    139f:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
    13a3:	c5 fa 7e 90 c8 fb ff 	vmovq  -0x438(%rax),%xmm2
    13aa:	ff 
    13ab:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    13b1:	c5 fa 6f 80 b8 fb ff 	vmovdqu -0x448(%rax),%xmm0
    13b8:	ff 
    13b9:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    13be:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
    13c4:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    13c9:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    13cf:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    13d4:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
    13da:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    13df:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    13e5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    13ea:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    13ef:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    13f4:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    13fa:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1400:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1406:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    140b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1410:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1415:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    141a:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1420:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    1426:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    142b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1430:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    1436:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    143c:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1442:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    1449:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1450:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1457:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    145c:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    1461:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1468:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    146d:	c5 7a 7e 88 e0 fb ff 	vmovq  -0x420(%rax),%xmm9
    1474:	ff 
    1475:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    147b:	c5 fa 6f 90 d0 fb ff 	vmovdqu -0x430(%rax),%xmm2
    1482:	ff 
    1483:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1488:	c4 63 31 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm9,%xmm9
    148e:	c4 e2 15 36 c0       	vpermd %ymm0,%ymm13,%ymm0
    1493:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
    1499:	c4 e3 4d 02 f0 c0    	vpblendd $0xc0,%ymm0,%ymm6,%ymm6
    149f:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    14a4:	c4 c3 7d 39 d1 01    	vextracti128 $0x1,%ymm2,%xmm9
    14aa:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
    14af:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    14b5:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    14ba:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    14c0:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    14c5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    14ca:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    14cf:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    14d4:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    14da:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    14e0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    14e5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    14ea:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
    14f0:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    14f6:	c4 21 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm14
    14fc:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1502:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1507:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    150c:	c4 23 09 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm14,%xmm14
    1513:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    151a:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    1520:	c4 c1 69 6c d6       	vpunpcklqdq %xmm14,%xmm2,%xmm2
    1525:	c5 79 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm14
    152a:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
    1531:	c4 23 09 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm14,%xmm14
    1538:	c4 41 31 6c ce       	vpunpcklqdq %xmm14,%xmm9,%xmm9
    153d:	c5 7a 7e b0 f8 fb ff 	vmovq  -0x408(%rax),%xmm14
    1544:	ff 
    1545:	c4 63 35 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm9,%ymm9
    154b:	c5 fa 6f 90 e8 fb ff 	vmovdqu -0x418(%rax),%xmm2
    1552:	ff 
    1553:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    1558:	c4 63 09 0f f2 0c    	vpalignr $0xc,%xmm2,%xmm14,%xmm14
    155e:	c4 42 1d 36 c9       	vpermd %ymm9,%ymm12,%ymm9
    1563:	c4 c3 6d 38 d6 01    	vinserti128 $0x1,%xmm14,%ymm2,%ymm2
    1569:	c4 c3 7d 0c c1 f0    	vblendps $0xf0,%ymm9,%ymm0,%ymm0
    156f:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    1574:	c4 c3 7d 39 d6 01    	vextracti128 $0x1,%ymm2,%xmm14
    157a:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
    157f:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    1585:	c4 41 79 7e f4       	vmovd  %xmm14,%r12d
    158a:	c4 43 79 16 f6 02    	vpextrd $0x2,%xmm14,%r14d
    1590:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1595:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    159a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    159f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    15a4:	c4 43 79 16 f4 01    	vpextrd $0x1,%xmm14,%r12d
    15aa:	c4 43 79 16 f6 03    	vpextrd $0x3,%xmm14,%r14d
    15b0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    15b5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    15ba:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
    15c0:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    15c6:	c4 21 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm15
    15cc:	c4 21 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm14
    15d2:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    15d7:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    15dd:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    15e4:	c4 23 01 22 3c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm15,%xmm15
    15eb:	c4 23 09 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm14,%xmm14
    15f2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    15f7:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    15fe:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    1602:	c4 41 09 6c f7       	vpunpcklqdq %xmm15,%xmm14,%xmm14
    1607:	c5 79 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm15
    160c:	c4 23 01 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm15,%xmm15
    1613:	c5 7d e7 82 40 ff ff 	vmovntdq %ymm8,-0xc0(%rdx)
    161a:	ff 
    161b:	c5 fd e7 8a 60 ff ff 	vmovntdq %ymm1,-0xa0(%rdx)
    1622:	ff 
    1623:	c5 fd e7 7a 80       	vmovntdq %ymm7,-0x80(%rdx)
    1628:	c5 fd e7 72 a0       	vmovntdq %ymm6,-0x60(%rdx)
    162d:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    1632:	c4 c1 69 6c d7       	vpunpcklqdq %xmm15,%xmm2,%xmm2
    1637:	c4 c3 6d 38 d6 01    	vinserti128 $0x1,%xmm14,%ymm2,%ymm2
    163d:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1642:	c4 e2 25 36 d2       	vpermd %ymm2,%ymm11,%ymm2
    1647:	c4 c3 6d 02 d1 03    	vpblendd $0x3,%ymm9,%ymm2,%ymm2
    164d:	c5 fd e7 52 e0       	vmovntdq %ymm2,-0x20(%rdx)
    1652:	4d 39 d0             	cmp    %r10,%r8
    1655:	0f 83 2d f9 ff ff    	jae    f88 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x108>
    165b:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1660:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1665:	48 8d 41 68          	lea    0x68(%rcx),%rax
    1669:	0f ae f8             	sfence
    166c:	49 39 c0             	cmp    %rax,%r8
    166f:	0f 82 bc 03 00 00    	jb     1a31 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbb1>
    1675:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1679:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1681 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x801>
    1680:	00 
    1681:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1689 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x809>
    1688:	00 
    1689:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    168e:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1693:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 169b <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x81b>
    169a:	00 
    169b:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
    169f:	4c 01 da             	add    %r11,%rdx
    16a2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    16a8:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
    16ac:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    16b1:	48 83 c2 60          	add    $0x60,%rdx
    16b5:	48 83 c0 60          	add    $0x60,%rax
    16b9:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
    16be:	c5 7a 6f 40 d0       	vmovdqu -0x30(%rax),%xmm8
    16c3:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    16c9:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
    16ce:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    16d4:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
    16d9:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    16de:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
    16e4:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
    16ea:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    16f0:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
    16f5:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    16fa:	c4 c3 79 0f c0 0c    	vpalignr $0xc,%xmm8,%xmm0,%xmm0
    1700:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
    1706:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    170c:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
    1711:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
    1716:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    171c:	c4 43 7d 39 c2 01    	vextracti128 $0x1,%ymm8,%xmm10
    1722:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1728:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    172d:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    1733:	c5 f9 7e c1          	vmovd  %xmm0,%ecx
    1737:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    173d:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    1742:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    1748:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    174d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1752:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1757:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    175c:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    1762:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1768:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    176d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1772:	c4 e3 79 16 c1 01    	vpextrd $0x1,%xmm0,%ecx
    1778:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    177e:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1784:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    178a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    178e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1793:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    179a:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    17a1:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    17a7:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    17ad:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    17b2:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    17b7:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    17bd:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
    17c2:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    17c7:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    17cc:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    17d2:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    17d9:	c5 79 7e c1          	vmovd  %xmm8,%ecx
    17dd:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    17e2:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    17e9:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
    17ef:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    17f4:	c4 63 79 16 c1 01    	vpextrd $0x1,%xmm8,%ecx
    17fa:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    17ff:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
    1805:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1809:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    180e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1813:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
    1818:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    181e:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    1824:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    182a:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1830:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1835:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    183c:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    1843:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    1849:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
    1850:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    1855:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    185a:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    1860:	c4 41 39 6c c2       	vpunpcklqdq %xmm10,%xmm8,%xmm8
    1865:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    186a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    186f:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    1875:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    187a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    187f:	c5 f9 7e c9          	vmovd  %xmm1,%ecx
    1883:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1888:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    188f:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    1895:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    189b:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    18a0:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    18a5:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    18ab:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    18b1:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
    18b6:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    18bd:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    18c1:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    18c7:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    18cd:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    18d3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    18d8:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    18de:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    18e3:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    18e9:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    18ee:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    18f5:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    18fa:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    18ff:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
    1904:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    190b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1910:	c5 f9 7e d1          	vmovd  %xmm2,%ecx
    1914:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    191a:	c4 41 39 6c c1       	vpunpcklqdq %xmm9,%xmm8,%xmm8
    191f:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    1924:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1929:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    192f:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1933:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1938:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    193f:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    1945:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    194a:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    1950:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
    1955:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    195a:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    195e:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1964:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    196a:	c4 21 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm8
    1970:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1976:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    197c:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1981:	c4 23 39 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm8,%xmm8
    1988:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    198f:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    1994:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    199b:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
    199f:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    19a5:	c4 c1 41 6c f8       	vpunpcklqdq %xmm8,%xmm7,%xmm7
    19aa:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
    19af:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
    19b5:	49 8d 49 48          	lea    0x48(%r9),%rcx
    19b9:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    19bf:	49 83 c1 20          	add    $0x20,%r9
    19c3:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
    19ca:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    19cf:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
    19d4:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
    19d8:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    19de:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
    19e4:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
    19ea:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
    19ef:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    19f4:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    19fa:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    19ff:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1a04:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    1a08:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1a0e:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    1a13:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
    1a19:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1a1e:	49 39 c8             	cmp    %rcx,%r8
    1a21:	0f 83 81 fc ff ff    	jae    16a8 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x828>
    1a27:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1a2c:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1a31:	49 8d 51 08          	lea    0x8(%r9),%rdx
    1a35:	49 39 d0             	cmp    %rdx,%r8
    1a38:	0f 82 2a 01 00 00    	jb     1b68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xce8>
    1a3e:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1a42:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1a4a <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbca>
    1a49:	00 
    1a4a:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1a52 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbd2>
    1a51:	00 
    1a52:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1a57:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1a5c:	49 8d 0c 02          	lea    (%r10,%rax,1),%rcx
    1a60:	4c 01 d8             	add    %r11,%rax
    1a63:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1a68:	c5 fa 6f 01          	vmovdqu (%rcx),%xmm0
    1a6c:	c5 fa 7e 49 10       	vmovq  0x10(%rcx),%xmm1
    1a71:	48 83 c0 18          	add    $0x18,%rax
    1a75:	48 83 c1 18          	add    $0x18,%rcx
    1a79:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1a7f:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1a85:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1a8a:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1a90:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1a95:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1a9b:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1aa0:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1aa6:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1aab:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1ab0:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1ab5:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1aba:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1ac0:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1ac6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1acb:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1ad0:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1ad6:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1adc:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1ae2:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1ae8:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1aed:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1af2:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1af9:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1b00:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1b06:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1b0a:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1b0f:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1b16:	49 89 d1             	mov    %rdx,%r9
    1b19:	48 83 c2 08          	add    $0x8,%rdx
    1b1d:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    1b24:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1b28:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1b2e:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1b33:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1b37:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1b3d:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1b42:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1b47:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1b4b:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    1b50:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
    1b55:	49 39 d0             	cmp    %rdx,%r8
    1b58:	0f 83 0a ff ff ff    	jae    1a68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbe8>
    1b5e:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1b63:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1b68:	4d 39 c1             	cmp    %r8,%r9
    1b6b:	0f 83 f7 01 00 00    	jae    1d68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee8>
    1b71:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1b75:	49 8d 1c 02          	lea    (%r10,%rax,1),%rbx
    1b79:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1b7d:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1b82:	0f b6 1b             	movzbl (%rbx),%ebx
    1b85:	c1 e2 08             	shl    $0x8,%edx
    1b88:	41 c1 e4 10          	shl    $0x10,%r12d
    1b8c:	44 09 e2             	or     %r12d,%edx
    1b8f:	09 da                	or     %ebx,%edx
    1b91:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1b95:	48 8d 1c 96          	lea    (%rsi,%rdx,4),%rbx
    1b99:	8b 13                	mov    (%rbx),%edx
    1b9b:	0f b7 1b             	movzwl (%rbx),%ebx
    1b9e:	c1 ea 10             	shr    $0x10,%edx
    1ba1:	66 41 89 1c 03       	mov    %bx,(%r11,%rax,1)
    1ba6:	41 88 54 03 02       	mov    %dl,0x2(%r11,%rax,1)
    1bab:	49 8d 51 01          	lea    0x1(%r9),%rdx
    1baf:	4c 39 c2             	cmp    %r8,%rdx
    1bb2:	0f 83 b0 01 00 00    	jae    1d68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee8>
    1bb8:	49 8d 5c 02 03       	lea    0x3(%r10,%rax,1),%rbx
    1bbd:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1bc1:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1bc6:	0f b6 1b             	movzbl (%rbx),%ebx
    1bc9:	41 c1 e4 10          	shl    $0x10,%r12d
    1bcd:	c1 e2 08             	shl    $0x8,%edx
    1bd0:	44 09 e2             	or     %r12d,%edx
    1bd3:	09 da                	or     %ebx,%edx
    1bd5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1bd9:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1bdd:	8b 1a                	mov    (%rdx),%ebx
    1bdf:	44 0f b7 22          	movzwl (%rdx),%r12d
    1be3:	49 8d 51 02          	lea    0x2(%r9),%rdx
    1be7:	89 d9                	mov    %ebx,%ecx
    1be9:	66 45 89 64 03 03    	mov    %r12w,0x3(%r11,%rax,1)
    1bef:	c1 e9 10             	shr    $0x10,%ecx
    1bf2:	41 88 4c 03 05       	mov    %cl,0x5(%r11,%rax,1)
    1bf7:	4c 39 c2             	cmp    %r8,%rdx
    1bfa:	0f 83 68 01 00 00    	jae    1d68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee8>
    1c00:	49 8d 5c 02 06       	lea    0x6(%r10,%rax,1),%rbx
    1c05:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1c09:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1c0e:	0f b6 1b             	movzbl (%rbx),%ebx
    1c11:	41 c1 e4 10          	shl    $0x10,%r12d
    1c15:	c1 e2 08             	shl    $0x8,%edx
    1c18:	44 09 e2             	or     %r12d,%edx
    1c1b:	09 da                	or     %ebx,%edx
    1c1d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c21:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1c25:	8b 1a                	mov    (%rdx),%ebx
    1c27:	44 0f b7 22          	movzwl (%rdx),%r12d
    1c2b:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1c2f:	89 d9                	mov    %ebx,%ecx
    1c31:	66 45 89 64 03 06    	mov    %r12w,0x6(%r11,%rax,1)
    1c37:	c1 e9 10             	shr    $0x10,%ecx
    1c3a:	41 88 4c 03 08       	mov    %cl,0x8(%r11,%rax,1)
    1c3f:	4c 39 c2             	cmp    %r8,%rdx
    1c42:	0f 83 20 01 00 00    	jae    1d68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee8>
    1c48:	49 8d 5c 02 09       	lea    0x9(%r10,%rax,1),%rbx
    1c4d:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1c51:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1c56:	0f b6 1b             	movzbl (%rbx),%ebx
    1c59:	41 c1 e4 08          	shl    $0x8,%r12d
    1c5d:	c1 e2 10             	shl    $0x10,%edx
    1c60:	44 09 e2             	or     %r12d,%edx
    1c63:	09 da                	or     %ebx,%edx
    1c65:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c69:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1c6d:	8b 1a                	mov    (%rdx),%ebx
    1c6f:	44 0f b7 22          	movzwl (%rdx),%r12d
    1c73:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1c77:	89 d9                	mov    %ebx,%ecx
    1c79:	66 45 89 64 03 09    	mov    %r12w,0x9(%r11,%rax,1)
    1c7f:	c1 e9 10             	shr    $0x10,%ecx
    1c82:	41 88 4c 03 0b       	mov    %cl,0xb(%r11,%rax,1)
    1c87:	4c 39 c2             	cmp    %r8,%rdx
    1c8a:	0f 83 d8 00 00 00    	jae    1d68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee8>
    1c90:	49 8d 5c 02 0c       	lea    0xc(%r10,%rax,1),%rbx
    1c95:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1c99:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1c9e:	0f b6 1b             	movzbl (%rbx),%ebx
    1ca1:	41 c1 e4 08          	shl    $0x8,%r12d
    1ca5:	c1 e2 10             	shl    $0x10,%edx
    1ca8:	44 09 e2             	or     %r12d,%edx
    1cab:	09 da                	or     %ebx,%edx
    1cad:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1cb1:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1cb5:	8b 1a                	mov    (%rdx),%ebx
    1cb7:	44 0f b7 22          	movzwl (%rdx),%r12d
    1cbb:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1cbf:	c1 eb 10             	shr    $0x10,%ebx
    1cc2:	66 45 89 64 03 0c    	mov    %r12w,0xc(%r11,%rax,1)
    1cc8:	41 88 5c 03 0e       	mov    %bl,0xe(%r11,%rax,1)
    1ccd:	4c 39 c2             	cmp    %r8,%rdx
    1cd0:	0f 83 92 00 00 00    	jae    1d68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee8>
    1cd6:	49 8d 5c 02 0f       	lea    0xf(%r10,%rax,1),%rbx
    1cdb:	49 83 c1 06          	add    $0x6,%r9
    1cdf:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1ce3:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1ce8:	0f b6 1b             	movzbl (%rbx),%ebx
    1ceb:	41 c1 e4 08          	shl    $0x8,%r12d
    1cef:	c1 e2 10             	shl    $0x10,%edx
    1cf2:	44 09 e2             	or     %r12d,%edx
    1cf5:	09 da                	or     %ebx,%edx
    1cf7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1cfb:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1cff:	8b 1a                	mov    (%rdx),%ebx
    1d01:	44 0f b7 22          	movzwl (%rdx),%r12d
    1d05:	89 d9                	mov    %ebx,%ecx
    1d07:	66 45 89 64 03 0f    	mov    %r12w,0xf(%r11,%rax,1)
    1d0d:	c1 e9 10             	shr    $0x10,%ecx
    1d10:	41 88 4c 03 11       	mov    %cl,0x11(%r11,%rax,1)
    1d15:	4d 39 c1             	cmp    %r8,%r9
    1d18:	73 4e                	jae    1d68 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xee8>
    1d1a:	49 8d 54 02 12       	lea    0x12(%r10,%rax,1),%rdx
    1d1f:	4d 8d 44 03 12       	lea    0x12(%r11,%rax,1),%r8
    1d24:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1d28:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1d2c:	0f b6 12             	movzbl (%rdx),%edx
    1d2f:	c1 e0 08             	shl    $0x8,%eax
    1d32:	c1 e1 10             	shl    $0x10,%ecx
    1d35:	09 c8                	or     %ecx,%eax
    1d37:	09 d0                	or     %edx,%eax
    1d39:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1d3d:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1d41:	8b 02                	mov    (%rdx),%eax
    1d43:	0f b7 12             	movzwl (%rdx),%edx
    1d46:	c1 e8 10             	shr    $0x10,%eax
    1d49:	66 41 89 10          	mov    %dx,(%r8)
    1d4d:	41 88 40 02          	mov    %al,0x2(%r8)
    1d51:	c5 f8 77             	vzeroupper
    1d54:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1d58:	5b                   	pop    %rbx
    1d59:	41 5c                	pop    %r12
    1d5b:	41 5d                	pop    %r13
    1d5d:	41 5e                	pop    %r14
    1d5f:	41 5f                	pop    %r15
    1d61:	5d                   	pop    %rbp
    1d62:	c3                   	ret
    1d63:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1d68:	c5 f8 77             	vzeroupper
    1d6b:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1d6f:	5b                   	pop    %rbx
    1d70:	41 5c                	pop    %r12
    1d72:	41 5d                	pop    %r13
    1d74:	41 5e                	pop    %r14
    1d76:	41 5f                	pop    %r15
    1d78:	5d                   	pop    %rbp
    1d79:	c3                   	ret
    1d7a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1d80:	4d 89 c1             	mov    %r8,%r9
    1d83:	e9 a9 fc ff ff       	jmp    1a31 <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbb1>
    1d88:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    1d8f:	00 
    1d90:	c3                   	ret
    1d91:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1d95:	49 89 c9             	mov    %rcx,%r9
    1d98:	e9 cf f8 ff ff       	jmp    166c <jshc_channel::avx2_chain_vectorpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7ec>
