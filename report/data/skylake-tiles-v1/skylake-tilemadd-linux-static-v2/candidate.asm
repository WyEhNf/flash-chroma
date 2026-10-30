
artifacts/skylake-tilemadd-linux-build-v1/CMakeFiles/jshc_skylake_tilemadd.dir/channel_tilemadd.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 d3 13 00 00    	je     13e0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13e0>
       d:	55                   	push   %rbp
       e:	b8 00 04 00 00       	mov    $0x400,%eax
      13:	49 89 d0             	mov    %rdx,%r8
      16:	48 8d 14 49          	lea    (%rcx,%rcx,2),%rdx
      1a:	48 89 e5             	mov    %rsp,%rbp
      1d:	41 57                	push   %r15
      1f:	41 56                	push   %r14
      21:	41 55                	push   %r13
      23:	41 54                	push   %r12
      25:	53                   	push   %rbx
      26:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
      2a:	48 83 ec 28          	sub    $0x28,%rsp
      2e:	48 39 c2             	cmp    %rax,%rdx
      31:	48 0f 47 d0          	cmova  %rax,%rdx
      35:	31 c0                	xor    %eax,%eax
      37:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
      3e:	00 00 
      40:	41 0f 18 04 00       	prefetchnta (%r8,%rax,1)
      45:	48 83 c0 40          	add    $0x40,%rax
      49:	48 39 d0             	cmp    %rdx,%rax
      4c:	72 f2                	jb     40 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x40>
      4e:	4d 89 c2             	mov    %r8,%r10
      51:	45 31 c9             	xor    %r9d,%r9d
      54:	e9 89 00 00 00       	jmp    e2 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe2>
      59:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
      60:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
      65:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
      6a:	49 ff c1             	inc    %r9
      6d:	49 83 c2 03          	add    $0x3,%r10
      71:	c1 e2 10             	shl    $0x10,%edx
      74:	c1 e0 08             	shl    $0x8,%eax
      77:	09 d0                	or     %edx,%eax
      79:	41 0f b6 52 fd       	movzbl -0x3(%r10),%edx
      7e:	09 d0                	or     %edx,%eax
      80:	89 c2                	mov    %eax,%edx
      82:	44 8d 1c 85 00 00 00 	lea    0x0(,%rax,4),%r11d
      89:	00 
      8a:	c1 e2 04             	shl    $0x4,%edx
      8d:	41 81 e3 00 f0 03 00 	and    $0x3f000,%r11d
      94:	81 e2 c0 0f 00 00    	and    $0xfc0,%edx
      9a:	44 09 da             	or     %r11d,%edx
      9d:	41 89 c3             	mov    %eax,%r11d
      a0:	41 81 e3 03 00 fc 00 	and    $0xfc0003,%r11d
      a7:	44 09 da             	or     %r11d,%edx
      aa:	41 89 c3             	mov    %eax,%r11d
      ad:	c1 e8 0c             	shr    $0xc,%eax
      b0:	41 c1 eb 06          	shr    $0x6,%r11d
      b4:	83 e0 30             	and    $0x30,%eax
      b7:	41 83 e3 0c          	and    $0xc,%r11d
      bb:	44 09 da             	or     %r11d,%edx
      be:	09 d0                	or     %edx,%eax
      c0:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
      c4:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
      c8:	8b 02                	mov    (%rdx),%eax
      ca:	0f b7 12             	movzwl (%rdx),%edx
      cd:	c1 e8 10             	shr    $0x10,%eax
      d0:	66 41 89 52 fd       	mov    %dx,-0x3(%r10)
      d5:	41 88 42 ff          	mov    %al,-0x1(%r10)
      d9:	4c 39 c9             	cmp    %r9,%rcx
      dc:	0f 84 f6 12 00 00    	je     13d8 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13d8>
      e2:	41 f6 c2 3f          	test   $0x3f,%r10b
      e6:	0f 85 74 ff ff ff    	jne    60 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x60>
      ec:	49 8d 41 48          	lea    0x48(%r9),%rax
      f0:	48 39 c1             	cmp    %rax,%rcx
      f3:	0f 82 e8 12 00 00    	jb     13e1 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13e1>
      f9:	ba 03 03 03 00       	mov    $0x30303,%edx
      fe:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
     102:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     106:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # 10e <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10e>
     10d:	00 
     10e:	c5 f9 6e f2          	vmovd  %edx,%xmm6
     112:	ba 00 00 fc 00       	mov    $0xfc0000,%edx
     117:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # 11f <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x11f>
     11e:	00 
     11f:	c5 fd 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm0        # 127 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x127>
     126:	00 
     127:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
     12c:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 134 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x134>
     133:	00 
     134:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 13c <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c>
     13b:	00 
     13c:	4c 01 c0             	add    %r8,%rax
     13f:	c5 fd 7f 74 24 08    	vmovdqa %ymm6,0x8(%rsp)
     145:	c5 cd 71 d1 0f       	vpsrlw $0xf,%ymm1,%ymm6
     14a:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # 152 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x152>
     151:	00 
     152:	c5 fd 7f 74 24 88    	vmovdqa %ymm6,-0x78(%rsp)
     158:	c5 f9 6e f2          	vmovd  %edx,%xmm6
     15c:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
     161:	c5 fd 7f 74 24 e8    	vmovdqa %ymm6,-0x18(%rsp)
     167:	eb 0a                	jmp    173 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x173>
     169:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     170:	49 89 d1             	mov    %rdx,%r9
     173:	49 8d 91 96 01 00 00 	lea    0x196(%r9),%rdx
     17a:	48 39 d1             	cmp    %rdx,%rcx
     17d:	72 1c                	jb     19b <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x19b>
     17f:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
     186:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
     18d:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     194:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     19b:	c5 fa 6f 08          	vmovdqu (%rax),%xmm1
     19f:	c5 fa 7e 50 10       	vmovq  0x10(%rax),%xmm2
     1a4:	48 05 c0 00 00 00    	add    $0xc0,%rax
     1aa:	c5 fd 6f 74 24 08    	vmovdqa 0x8(%rsp),%ymm6
     1b0:	c5 7d 6f 6c 24 88    	vmovdqa -0x78(%rsp),%ymm13
     1b6:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     1bc:	c5 7d 6f 64 24 e8    	vmovdqa -0x18(%rsp),%ymm12
     1c2:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     1c8:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     1cd:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
     1d1:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
     1d6:	c4 c1 75 db cc       	vpand  %ymm12,%ymm1,%ymm1
     1db:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
     1e0:	c4 c2 65 04 de       	vpmaddubsw %ymm14,%ymm3,%ymm3
     1e5:	c4 c1 65 f5 dd       	vpmaddwd %ymm13,%ymm3,%ymm3
     1ea:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
     1ee:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     1f2:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     1f6:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     1fc:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     200:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     206:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     20b:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     211:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     216:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     21b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     220:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     225:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     22b:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     231:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     236:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     23b:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     241:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     247:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     24d:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     253:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     257:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     25c:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     263:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     26a:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     270:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     274:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     279:	c4 63 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm8,%xmm8
     280:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     287:	c5 39 6c c2          	vpunpcklqdq %xmm2,%xmm8,%xmm8
     28b:	c5 fa 7e 90 68 ff ff 	vmovq  -0x98(%rax),%xmm2
     292:	ff 
     293:	c4 63 3d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm8,%ymm8
     299:	c5 fa 6f 88 58 ff ff 	vmovdqu -0xa8(%rax),%xmm1
     2a0:	ff 
     2a1:	c4 42 3d 00 c7       	vpshufb %ymm15,%ymm8,%ymm8
     2a6:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     2ac:	c4 42 25 36 c0       	vpermd %ymm8,%ymm11,%ymm8
     2b1:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     2b7:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     2bc:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
     2c0:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
     2c5:	c4 c1 75 db cc       	vpand  %ymm12,%ymm1,%ymm1
     2ca:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
     2cf:	c4 c2 65 04 de       	vpmaddubsw %ymm14,%ymm3,%ymm3
     2d4:	c4 c1 65 f5 dd       	vpmaddwd %ymm13,%ymm3,%ymm3
     2d9:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
     2dd:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     2e1:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     2e5:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     2eb:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     2ef:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     2f5:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     2fb:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     300:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     305:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     30a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     30f:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     315:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     31a:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     320:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     325:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     32b:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     331:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     336:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     33c:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     340:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     345:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     34c:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     352:	c4 a1 79 6e 24 96    	vmovd  (%rsi,%r10,4),%xmm4
     358:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     35f:	c4 e3 59 22 24 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm4,%xmm4
     366:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     36a:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     36f:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     376:	c5 d9 6c e2          	vpunpcklqdq %xmm2,%xmm4,%xmm4
     37a:	c5 fa 7e 50 80       	vmovq  -0x80(%rax),%xmm2
     37f:	c4 e3 5d 38 e1 01    	vinserti128 $0x1,%xmm1,%ymm4,%ymm4
     385:	c5 fa 6f 88 70 ff ff 	vmovdqu -0x90(%rax),%xmm1
     38c:	ff 
     38d:	c4 c2 5d 00 e7       	vpshufb %ymm15,%ymm4,%ymm4
     392:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     398:	c4 e2 25 36 e4       	vpermd %ymm4,%ymm11,%ymm4
     39d:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     3a3:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     3a8:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
     3ac:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
     3b1:	c4 c1 75 db cc       	vpand  %ymm12,%ymm1,%ymm1
     3b6:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
     3bb:	c4 c2 65 04 de       	vpmaddubsw %ymm14,%ymm3,%ymm3
     3c0:	c4 c1 65 f5 dd       	vpmaddwd %ymm13,%ymm3,%ymm3
     3c5:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
     3c9:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     3cd:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     3d1:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     3d7:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     3db:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     3e1:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     3e6:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     3ec:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     3f1:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     3f6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     3fb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     400:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     406:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     40c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     411:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     416:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     41c:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     422:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     428:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     42e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     432:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     437:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     43e:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     445:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     44b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     44f:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     454:	c4 e3 61 22 1c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm3,%xmm3
     45b:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     462:	c5 e1 6c da          	vpunpcklqdq %xmm2,%xmm3,%xmm3
     466:	c5 fa 6f 50 88       	vmovdqu -0x78(%rax),%xmm2
     46b:	c4 e3 65 38 d9 01    	vinserti128 $0x1,%xmm1,%ymm3,%ymm3
     471:	c5 fa 7e 48 98       	vmovq  -0x68(%rax),%xmm1
     476:	c4 c2 65 00 df       	vpshufb %ymm15,%ymm3,%ymm3
     47b:	c4 e3 71 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm1,%xmm1
     481:	c4 e2 25 36 db       	vpermd %ymm3,%ymm11,%ymm3
     486:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
     48c:	c4 c2 6d 00 d2       	vpshufb %ymm10,%ymm2,%ymm2
     491:	c5 ed db ee          	vpand  %ymm6,%ymm2,%ymm5
     495:	c4 c2 6d 00 c9       	vpshufb %ymm9,%ymm2,%ymm1
     49a:	c4 c1 6d db d4       	vpand  %ymm12,%ymm2,%ymm2
     49f:	c5 f5 71 d1 02       	vpsrlw $0x2,%ymm1,%ymm1
     4a4:	c4 c2 55 04 ee       	vpmaddubsw %ymm14,%ymm5,%ymm5
     4a9:	c4 c1 55 f5 ed       	vpmaddwd %ymm13,%ymm5,%ymm5
     4ae:	c5 f5 f5 c8          	vpmaddwd %ymm0,%ymm1,%ymm1
     4b2:	c5 f5 eb cd          	vpor   %ymm5,%ymm1,%ymm1
     4b6:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     4ba:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     4c0:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     4c4:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     4ca:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     4cf:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     4d4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     4d9:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     4df:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     4e4:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     4ea:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     4f0:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     4f6:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     4fa:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     4ff:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     504:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     509:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     50f:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     514:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     51a:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     520:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     526:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     52d:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     534:	c4 e3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm7,%xmm7
     53b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     53f:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     544:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     54b:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     54f:	c5 fa 7e 50 b0       	vmovq  -0x50(%rax),%xmm2
     554:	c4 e3 45 38 f9 01    	vinserti128 $0x1,%xmm1,%ymm7,%ymm7
     55a:	c5 fa 6f 48 a0       	vmovdqu -0x60(%rax),%xmm1
     55f:	c4 c2 45 00 ff       	vpshufb %ymm15,%ymm7,%ymm7
     564:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     56a:	c4 e2 25 36 ff       	vpermd %ymm7,%ymm11,%ymm7
     56f:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     575:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     57a:	c5 f5 db 6c 24 08    	vpand  0x8(%rsp),%ymm1,%ymm5
     580:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
     585:	c4 c1 75 db cc       	vpand  %ymm12,%ymm1,%ymm1
     58a:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
     58f:	c4 c2 55 04 ee       	vpmaddubsw %ymm14,%ymm5,%ymm5
     594:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
     598:	c4 c1 55 f5 ed       	vpmaddwd %ymm13,%ymm5,%ymm5
     59d:	c5 ed eb d5          	vpor   %ymm5,%ymm2,%ymm2
     5a1:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     5a5:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     5ab:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     5af:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     5b5:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     5ba:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     5c0:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     5c5:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5ca:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     5cf:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     5d4:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     5da:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     5e0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5e5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5ea:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     5f0:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     5f6:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     5fc:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     602:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     606:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     60b:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     612:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     619:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     61f:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     623:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     628:	c4 e3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm6,%xmm6
     62f:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     636:	c5 c9 6c d2          	vpunpcklqdq %xmm2,%xmm6,%xmm2
     63a:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
     640:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     645:	c4 c2 6d 00 d7       	vpshufb %ymm15,%ymm2,%ymm2
     64a:	c4 e2 25 36 ea       	vpermd %ymm2,%ymm11,%ymm5
     64f:	c5 fd 7f 6c 24 c8    	vmovdqa %ymm5,-0x38(%rsp)
     655:	c5 fa 7e 50 c8       	vmovq  -0x38(%rax),%xmm2
     65a:	c5 fd 6f 74 24 08    	vmovdqa 0x8(%rsp),%ymm6
     660:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     666:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     66c:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     671:	c5 f5 db 6c 24 08    	vpand  0x8(%rsp),%ymm1,%ymm5
     677:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
     67c:	c4 c1 75 db cc       	vpand  %ymm12,%ymm1,%ymm1
     681:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
     686:	c4 c2 55 04 ee       	vpmaddubsw %ymm14,%ymm5,%ymm5
     68b:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
     68f:	c4 c1 55 f5 ed       	vpmaddwd %ymm13,%ymm5,%ymm5
     694:	c5 ed eb d5          	vpor   %ymm5,%ymm2,%ymm2
     698:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     69c:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     6a2:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     6a6:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     6ac:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     6b1:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     6b7:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     6bc:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     6c1:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     6c6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     6cb:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     6d1:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     6d7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     6dc:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     6e1:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     6e7:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     6ed:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     6f3:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     6f9:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6fd:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     702:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     709:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     710:	c5 f9 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm5
     715:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     719:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     71f:	c4 a3 51 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm5,%xmm5
     726:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
     72d:	c5 e9 6c d5          	vpunpcklqdq %xmm5,%xmm2,%xmm2
     731:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
     737:	c5 fa 6f 48 d0       	vmovdqu -0x30(%rax),%xmm1
     73c:	c4 c2 6d 00 d7       	vpshufb %ymm15,%ymm2,%ymm2
     741:	c4 e2 25 36 d2       	vpermd %ymm2,%ymm11,%ymm2
     746:	c5 fd 7f 54 24 a8    	vmovdqa %ymm2,-0x58(%rsp)
     74c:	c5 fa 7e 50 e0       	vmovq  -0x20(%rax),%xmm2
     751:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     757:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     75d:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     762:	c5 f5 db ee          	vpand  %ymm6,%ymm1,%ymm5
     766:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
     76b:	c5 f5 db 4c 24 e8    	vpand  -0x18(%rsp),%ymm1,%ymm1
     771:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
     776:	c4 c2 55 04 ee       	vpmaddubsw %ymm14,%ymm5,%ymm5
     77b:	c4 c1 55 f5 ed       	vpmaddwd %ymm13,%ymm5,%ymm5
     780:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
     784:	c5 ed eb d5          	vpor   %ymm5,%ymm2,%ymm2
     788:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     78c:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     792:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     796:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     79c:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     7a2:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     7a7:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     7ac:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     7b1:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     7b6:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     7bc:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     7c1:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     7c7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     7cc:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     7d2:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     7d8:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     7dc:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     7e2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     7e7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     7ec:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     7f3:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
     7f9:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     7fe:	c5 fa 6f 50 e8       	vmovdqu -0x18(%rax),%xmm2
     803:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
     80a:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     811:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     815:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     81b:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
     822:	c4 c1 71 6c cc       	vpunpcklqdq %xmm12,%xmm1,%xmm1
     827:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
     82d:	c5 fa 7e 68 f8       	vmovq  -0x8(%rax),%xmm5
     832:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
     837:	c4 e3 51 0f ea 0c    	vpalignr $0xc,%xmm2,%xmm5,%xmm5
     83d:	c4 e2 25 36 c9       	vpermd %ymm1,%ymm11,%ymm1
     842:	c4 e3 6d 38 d5 01    	vinserti128 $0x1,%xmm5,%ymm2,%ymm2
     848:	c4 c2 6d 00 d2       	vpshufb %ymm10,%ymm2,%ymm2
     84d:	c4 c2 6d 00 e9       	vpshufb %ymm9,%ymm2,%ymm5
     852:	c5 ed db f6          	vpand  %ymm6,%ymm2,%ymm6
     856:	c5 ed db 54 24 e8    	vpand  -0x18(%rsp),%ymm2,%ymm2
     85c:	c5 d5 71 d5 02       	vpsrlw $0x2,%ymm5,%ymm5
     861:	c4 c2 4d 04 f6       	vpmaddubsw %ymm14,%ymm6,%ymm6
     866:	c4 c1 4d f5 f5       	vpmaddwd %ymm13,%ymm6,%ymm6
     86b:	c5 d5 f5 e8          	vpmaddwd %ymm0,%ymm5,%ymm5
     86f:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
     873:	c5 f9 6f f4          	vmovdqa %xmm4,%xmm6
     877:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
     87d:	c5 ed eb d5          	vpor   %ymm5,%ymm2,%ymm2
     881:	c4 e3 59 0f e6 08    	vpalignr $0x8,%xmm6,%xmm4,%xmm4
     887:	c4 e3 7d 39 d5 01    	vextracti128 $0x1,%ymm2,%xmm5
     88d:	c5 f9 7e d2          	vmovd  %xmm2,%edx
     891:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     897:	c4 c1 79 7e ec       	vmovd  %xmm5,%r12d
     89c:	c4 c3 79 16 ee 02    	vpextrd $0x2,%xmm5,%r14d
     8a2:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     8a7:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     8ac:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     8b1:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     8b6:	c4 c3 79 16 ec 01    	vpextrd $0x1,%xmm5,%r12d
     8bc:	c4 c3 79 16 ee 03    	vpextrd $0x3,%xmm5,%r14d
     8c2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     8c7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     8cc:	c4 e3 79 16 d2 01    	vpextrd $0x1,%xmm2,%edx
     8d2:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     8d8:	c4 a1 79 6e 2c be    	vmovd  (%rsi,%r15,4),%xmm5
     8de:	c4 21 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm12
     8e4:	c5 79 7f c2          	vmovdqa %xmm8,%xmm2
     8e8:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     8ee:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     8f2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     8f7:	c5 39 6c c6          	vpunpcklqdq %xmm6,%xmm8,%xmm8
     8fb:	c4 a3 51 22 2c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm5,%xmm5
     902:	c4 23 19 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm12,%xmm12
     909:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
     90f:	c5 79 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm13
     914:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     918:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     91e:	c5 19 6c e5          	vpunpcklqdq %xmm5,%xmm12,%xmm12
     922:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     928:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     92f:	c4 23 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm13,%xmm13
     936:	c4 e3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm5,%xmm5
     93d:	c5 fd e7 90 40 ff ff 	vmovntdq %ymm2,-0xc0(%rax)
     944:	ff 
     945:	49 8d 51 40          	lea    0x40(%r9),%rdx
     949:	c4 c1 51 6c ed       	vpunpcklqdq %xmm13,%xmm5,%xmm5
     94e:	c5 79 6f ef          	vmovdqa %xmm7,%xmm13
     952:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     958:	c4 c3 55 38 ec 01    	vinserti128 $0x1,%xmm12,%ymm5,%ymm5
     95e:	c4 c3 41 0f fd 08    	vpalignr $0x8,%xmm13,%xmm7,%xmm7
     964:	c5 79 6f e3          	vmovdqa %xmm3,%xmm12
     968:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     96e:	c4 c3 5d 38 e4 01    	vinserti128 $0x1,%xmm12,%ymm4,%ymm4
     974:	c4 c2 55 00 ef       	vpshufb %ymm15,%ymm5,%ymm5
     979:	c4 c1 61 6c dd       	vpunpcklqdq %xmm13,%xmm3,%xmm3
     97e:	c5 fd e7 a0 60 ff ff 	vmovntdq %ymm4,-0xa0(%rax)
     985:	ff 
     986:	c4 e2 25 36 ed       	vpermd %ymm5,%ymm11,%ymm5
     98b:	c4 e3 65 38 df 01    	vinserti128 $0x1,%xmm7,%ymm3,%ymm3
     991:	c5 fd e7 58 80       	vmovntdq %ymm3,-0x80(%rax)
     996:	c5 fd 6f 74 24 a8    	vmovdqa -0x58(%rsp),%ymm6
     99c:	c5 fd 6f 7c 24 c8    	vmovdqa -0x38(%rsp),%ymm7
     9a2:	c5 f9 6f 5c 24 c8    	vmovdqa -0x38(%rsp),%xmm3
     9a8:	c4 e3 7d 39 fc 01    	vextracti128 $0x1,%ymm7,%xmm4
     9ae:	c4 e3 7d 39 f2 01    	vextracti128 $0x1,%ymm6,%xmm2
     9b4:	c5 f9 6f fe          	vmovdqa %xmm6,%xmm7
     9b8:	c5 f9 6f f5          	vmovdqa %xmm5,%xmm6
     9bc:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     9c2:	c5 d9 6c e7          	vpunpcklqdq %xmm7,%xmm4,%xmm4
     9c6:	c4 e3 69 0f d7 08    	vpalignr $0x8,%xmm7,%xmm2,%xmm2
     9cc:	c4 e3 51 0f ee 08    	vpalignr $0x8,%xmm6,%xmm5,%xmm5
     9d2:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     9d6:	c4 e3 65 38 dc 01    	vinserti128 $0x1,%xmm4,%ymm3,%ymm3
     9dc:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
     9e2:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
     9e8:	c5 fd e7 58 a0       	vmovntdq %ymm3,-0x60(%rax)
     9ed:	c5 fd e7 50 c0       	vmovntdq %ymm2,-0x40(%rax)
     9f2:	c5 fd e7 48 e0       	vmovntdq %ymm1,-0x20(%rax)
     9f7:	4c 39 d1             	cmp    %r10,%rcx
     9fa:	0f 83 70 f7 ff ff    	jae    170 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x170>
     a00:	0f ae f8             	sfence
     a03:	49 8d 41 68          	lea    0x68(%r9),%rax
     a07:	48 39 c1             	cmp    %rax,%rcx
     a0a:	0f 82 8f 04 00 00    	jb     e9f <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe9f>
     a10:	41 b9 03 03 03 00    	mov    $0x30303,%r9d
     a16:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
     a1a:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # a22 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa22>
     a21:	00 
     a22:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # a2a <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa2a>
     a29:	00 
     a2a:	c4 c1 79 6e f1       	vmovd  %r9d,%xmm6
     a2f:	41 b9 00 00 fc 00    	mov    $0xfc0000,%r9d
     a35:	c5 fd 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm0        # a3d <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa3d>
     a3c:	00 
     a3d:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # a45 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa45>
     a44:	00 
     a45:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
     a4a:	c4 41 79 6e e9       	vmovd  %r9d,%xmm13
     a4f:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # a57 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa57>
     a56:	00 
     a57:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # a5f <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa5f>
     a5e:	00 
     a5f:	c5 fd 7f 74 24 e8    	vmovdqa %ymm6,-0x18(%rsp)
     a65:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
     a69:	4c 01 c0             	add    %r8,%rax
     a6c:	c4 42 7d 58 ed       	vpbroadcastd %xmm13,%ymm13
     a71:	c5 cd 71 d6 0f       	vpsrlw $0xf,%ymm6,%ymm6
     a76:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     a7d:	00 00 00 
     a80:	c5 fa 6f 08          	vmovdqu (%rax),%xmm1
     a84:	c5 fa 7e 50 10       	vmovq  0x10(%rax),%xmm2
     a89:	48 83 c0 60          	add    $0x60,%rax
     a8d:	c5 fd 6f 64 24 e8    	vmovdqa -0x18(%rsp),%ymm4
     a93:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     a99:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     a9f:	c5 fd 6f fc          	vmovdqa %ymm4,%ymm7
     aa3:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     aa8:	c5 f5 db dc          	vpand  %ymm4,%ymm1,%ymm3
     aac:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
     ab1:	c5 95 db c9          	vpand  %ymm1,%ymm13,%ymm1
     ab5:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
     aba:	c4 c2 65 04 de       	vpmaddubsw %ymm14,%ymm3,%ymm3
     abf:	c5 e5 f5 de          	vpmaddwd %ymm6,%ymm3,%ymm3
     ac3:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
     ac7:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     acb:	c5 fa 7e 58 c8       	vmovq  -0x38(%rax),%xmm3
     ad0:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     ad4:	c5 fa 6f 50 b8       	vmovdqu -0x48(%rax),%xmm2
     ad9:	c4 e3 7d 39 4c 24 08 	vextracti128 $0x1,%ymm1,0x8(%rsp)
     ae0:	01 
     ae1:	c4 e3 61 0f da 0c    	vpalignr $0xc,%xmm2,%xmm3,%xmm3
     ae7:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
     aed:	c4 c2 6d 00 d2       	vpshufb %ymm10,%ymm2,%ymm2
     af2:	c4 c2 6d 00 d9       	vpshufb %ymm9,%ymm2,%ymm3
     af7:	c5 ed db e4          	vpand  %ymm4,%ymm2,%ymm4
     afb:	c5 95 db d2          	vpand  %ymm2,%ymm13,%ymm2
     aff:	c5 e5 71 d3 02       	vpsrlw $0x2,%ymm3,%ymm3
     b04:	c4 c2 5d 04 e6       	vpmaddubsw %ymm14,%ymm4,%ymm4
     b09:	c5 dd f5 e6          	vpmaddwd %ymm6,%ymm4,%ymm4
     b0d:	c5 e5 f5 d8          	vpmaddwd %ymm0,%ymm3,%ymm3
     b11:	c5 e5 eb dc          	vpor   %ymm4,%ymm3,%ymm3
     b15:	c5 fa 6f 60 d0       	vmovdqu -0x30(%rax),%xmm4
     b1a:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     b1e:	c5 fa 7e 58 e0       	vmovq  -0x20(%rax),%xmm3
     b23:	c4 c3 7d 39 d0 01    	vextracti128 $0x1,%ymm2,%xmm8
     b29:	c4 e3 61 0f dc 0c    	vpalignr $0xc,%xmm4,%xmm3,%xmm3
     b2f:	c4 e3 5d 38 e3 01    	vinserti128 $0x1,%xmm3,%ymm4,%ymm4
     b35:	c4 c2 5d 00 e2       	vpshufb %ymm10,%ymm4,%ymm4
     b3a:	c5 dd db ef          	vpand  %ymm7,%ymm4,%ymm5
     b3e:	c4 c2 5d 00 d9       	vpshufb %ymm9,%ymm4,%ymm3
     b43:	c5 95 db e4          	vpand  %ymm4,%ymm13,%ymm4
     b47:	c5 e5 71 d3 02       	vpsrlw $0x2,%ymm3,%ymm3
     b4c:	c4 c2 55 04 ee       	vpmaddubsw %ymm14,%ymm5,%ymm5
     b51:	c5 d5 f5 ee          	vpmaddwd %ymm6,%ymm5,%ymm5
     b55:	c5 e5 f5 d8          	vpmaddwd %ymm0,%ymm3,%ymm3
     b59:	c5 e5 eb dd          	vpor   %ymm5,%ymm3,%ymm3
     b5d:	c5 fa 7e 68 f8       	vmovq  -0x8(%rax),%xmm5
     b62:	c5 e5 eb dc          	vpor   %ymm4,%ymm3,%ymm3
     b66:	c5 fa 6f 60 e8       	vmovdqu -0x18(%rax),%xmm4
     b6b:	c4 c3 7d 39 dc 01    	vextracti128 $0x1,%ymm3,%xmm12
     b71:	c4 e3 51 0f ec 0c    	vpalignr $0xc,%xmm4,%xmm5,%xmm5
     b77:	c4 e3 5d 38 e5 01    	vinserti128 $0x1,%xmm5,%ymm4,%ymm4
     b7d:	c4 c2 5d 00 e2       	vpshufb %ymm10,%ymm4,%ymm4
     b82:	c4 c2 5d 00 e9       	vpshufb %ymm9,%ymm4,%ymm5
     b87:	c5 dd db ff          	vpand  %ymm7,%ymm4,%ymm7
     b8b:	c5 95 db e4          	vpand  %ymm4,%ymm13,%ymm4
     b8f:	c5 d5 71 d5 02       	vpsrlw $0x2,%ymm5,%ymm5
     b94:	c4 c2 45 04 fe       	vpmaddubsw %ymm14,%ymm7,%ymm7
     b99:	c5 c5 f5 fe          	vpmaddwd %ymm6,%ymm7,%ymm7
     b9d:	c5 d5 f5 e8          	vpmaddwd %ymm0,%ymm5,%ymm5
     ba1:	c5 d5 eb ef          	vpor   %ymm7,%ymm5,%ymm5
     ba5:	c5 dd eb e5          	vpor   %ymm5,%ymm4,%ymm4
     ba9:	c4 e3 7d 39 e5 01    	vextracti128 $0x1,%ymm4,%xmm5
     baf:	c4 c1 79 7e e1       	vmovd  %xmm4,%r9d
     bb4:	c4 c3 79 16 e3 02    	vpextrd $0x2,%xmm4,%r11d
     bba:	c4 c1 79 7e ec       	vmovd  %xmm5,%r12d
     bbf:	c4 c3 79 16 ee 02    	vpextrd $0x2,%xmm5,%r14d
     bc5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     bca:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     bcf:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     bd4:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     bd9:	c4 c3 79 16 ec 01    	vpextrd $0x1,%xmm5,%r12d
     bdf:	c4 c3 79 16 ee 03    	vpextrd $0x3,%xmm5,%r14d
     be5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     bea:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     bef:	c4 c3 79 16 e1 01    	vpextrd $0x1,%xmm4,%r9d
     bf5:	c4 c3 79 16 e3 03    	vpextrd $0x3,%xmm4,%r11d
     bfb:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
     c01:	c4 a1 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm4
     c07:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c0c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     c11:	c4 a3 59 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm4,%xmm4
     c18:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
     c1f:	c4 41 79 7e e4       	vmovd  %xmm12,%r12d
     c24:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     c29:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     c2e:	c4 43 79 16 e6 02    	vpextrd $0x2,%xmm12,%r14d
     c34:	c4 43 79 16 e4 01    	vpextrd $0x1,%xmm12,%r12d
     c3a:	c5 d1 6c ec          	vpunpcklqdq %xmm4,%xmm5,%xmm5
     c3e:	c4 a1 79 6e 24 96    	vmovd  (%rsi,%r10,4),%xmm4
     c44:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     c49:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     c50:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     c56:	c4 a3 59 22 24 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm4,%xmm4
     c5d:	c4 c1 79 7e d9       	vmovd  %xmm3,%r9d
     c62:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     c67:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
     c6d:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     c72:	c4 c3 79 16 d9 01    	vpextrd $0x1,%xmm3,%r9d
     c78:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     c7d:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c82:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     c87:	c5 d9 6c e7          	vpunpcklqdq %xmm7,%xmm4,%xmm4
     c8b:	c4 43 79 16 e6 03    	vpextrd $0x3,%xmm12,%r14d
     c91:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     c96:	c4 e3 5d 38 e5 01    	vinserti128 $0x1,%xmm5,%ymm4,%ymm4
     c9c:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
     ca2:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     ca8:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     cad:	c4 c2 5d 00 e7       	vpshufb %ymm15,%ymm4,%ymm4
     cb2:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
     cb9:	c4 41 79 7e c4       	vmovd  %xmm8,%r12d
     cbe:	c4 e2 25 36 e4       	vpermd %ymm4,%ymm11,%ymm4
     cc3:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     cca:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     cd1:	c4 43 79 16 c6 02    	vpextrd $0x2,%xmm8,%r14d
     cd7:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     cdc:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     ce1:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     ce7:	c4 43 79 16 c4 01    	vpextrd $0x1,%xmm8,%r12d
     ced:	c5 d1 6c eb          	vpunpcklqdq %xmm3,%xmm5,%xmm5
     cf1:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     cf7:	c4 43 79 16 c6 03    	vpextrd $0x3,%xmm8,%r14d
     cfd:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     d02:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     d07:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     d0c:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     d12:	c5 79 6f e4          	vmovdqa %xmm4,%xmm12
     d16:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
     d1d:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
     d22:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     d27:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
     d2d:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     d32:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
     d38:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     d3e:	c4 c3 59 0f e4 08    	vpalignr $0x8,%xmm12,%xmm4,%xmm4
     d44:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     d48:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     d4d:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     d52:	c4 e3 65 38 dd 01    	vinserti128 $0x1,%xmm5,%ymm3,%ymm3
     d58:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
     d5e:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     d65:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     d6c:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     d72:	c4 c2 65 00 df       	vpshufb %ymm15,%ymm3,%ymm3
     d77:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
     d7e:	44 8b 64 24 08       	mov    0x8(%rsp),%r12d
     d83:	c4 e2 25 36 db       	vpermd %ymm3,%ymm11,%ymm3
     d88:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     d8d:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     d93:	c5 79 6f c3          	vmovdqa %xmm3,%xmm8
     d97:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     d9d:	c5 d1 6c ea          	vpunpcklqdq %xmm2,%xmm5,%xmm5
     da1:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     da7:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     dac:	c4 c1 61 6c dc       	vpunpcklqdq %xmm12,%xmm3,%xmm3
     db1:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     db6:	c4 e3 65 38 dc 01    	vinserti128 $0x1,%xmm4,%ymm3,%ymm3
     dbc:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     dc3:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
     dc8:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     dcd:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
     dd3:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     dd8:	44 8b 64 24 0c       	mov    0xc(%rsp),%r12d
     ddd:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     de1:	44 8b 74 24 10       	mov    0x10(%rsp),%r14d
     de6:	c4 e3 6d 38 d5 01    	vinserti128 $0x1,%xmm5,%ymm2,%ymm2
     dec:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
     df2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     df7:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     dfc:	c4 c2 6d 00 d7       	vpshufb %ymm15,%ymm2,%ymm2
     e01:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     e06:	44 8b 74 24 14       	mov    0x14(%rsp),%r14d
     e0b:	c4 e2 25 36 d2       	vpermd %ymm2,%ymm11,%ymm2
     e10:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
     e17:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     e1e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     e23:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     e29:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     e30:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     e34:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     e3a:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     e41:	4c 8d 4a 48          	lea    0x48(%rdx),%r9
     e45:	c5 fe 7f 58 e0       	vmovdqu %ymm3,-0x20(%rax)
     e4a:	48 83 c2 20          	add    $0x20,%rdx
     e4e:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
     e52:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     e56:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     e5c:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
     e62:	c4 e3 69 0f d7 08    	vpalignr $0x8,%xmm7,%xmm2,%xmm2
     e68:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
     e6d:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
     e73:	c4 e2 25 36 c9       	vpermd %ymm1,%ymm11,%ymm1
     e78:	c5 fe 7f 50 c0       	vmovdqu %ymm2,-0x40(%rax)
     e7d:	c5 f9 6f e9          	vmovdqa %xmm1,%xmm5
     e81:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     e87:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
     e8b:	c4 e3 55 38 e9 01    	vinserti128 $0x1,%xmm1,%ymm5,%ymm5
     e91:	c5 fe 7f 68 a0       	vmovdqu %ymm5,-0x60(%rax)
     e96:	4c 39 c9             	cmp    %r9,%rcx
     e99:	0f 83 e1 fb ff ff    	jae    a80 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa80>
     e9f:	4c 8d 4a 08          	lea    0x8(%rdx),%r9
     ea3:	4c 39 c9             	cmp    %r9,%rcx
     ea6:	0f 82 6b 01 00 00    	jb     1017 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1017>
     eac:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
     eb0:	ba 03 03 03 00       	mov    $0x30303,%edx
     eb5:	c5 ed 76 d2          	vpcmpeqd %ymm2,%ymm2,%ymm2
     eb9:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # ec1 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec1>
     ec0:	00 
     ec1:	c5 f9 6e e2          	vmovd  %edx,%xmm4
     ec5:	ba 00 00 fc 00       	mov    $0xfc0000,%edx
     eca:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # ed2 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xed2>
     ed1:	00 
     ed2:	c5 fd 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm0        # eda <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeda>
     ed9:	00 
     eda:	c5 f9 6e da          	vmovd  %edx,%xmm3
     ede:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # ee6 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xee6>
     ee5:	00 
     ee6:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # eee <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeee>
     eed:	00 
     eee:	4c 01 c0             	add    %r8,%rax
     ef1:	c4 e2 7d 58 e4       	vpbroadcastd %xmm4,%ymm4
     ef6:	c5 ed 71 d2 0f       	vpsrlw $0xf,%ymm2,%ymm2
     efb:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
     f00:	c5 fa 6f 08          	vmovdqu (%rax),%xmm1
     f04:	c5 fa 7e 68 10       	vmovq  0x10(%rax),%xmm5
     f09:	48 83 c0 18          	add    $0x18,%rax
     f0d:	c4 e3 51 0f e9 0c    	vpalignr $0xc,%xmm1,%xmm5,%xmm5
     f13:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
     f19:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
     f1e:	c4 c2 75 00 e9       	vpshufb %ymm9,%ymm1,%ymm5
     f23:	c5 dd db f1          	vpand  %ymm1,%ymm4,%ymm6
     f27:	c5 e5 db c9          	vpand  %ymm1,%ymm3,%ymm1
     f2b:	c5 d5 71 d5 02       	vpsrlw $0x2,%ymm5,%ymm5
     f30:	c4 c2 4d 04 f6       	vpmaddubsw %ymm14,%ymm6,%ymm6
     f35:	c5 cd f5 f2          	vpmaddwd %ymm2,%ymm6,%ymm6
     f39:	c5 d5 f5 e8          	vpmaddwd %ymm0,%ymm5,%ymm5
     f3d:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
     f41:	c5 f5 eb cd          	vpor   %ymm5,%ymm1,%ymm1
     f45:	c4 e3 7d 39 cd 01    	vextracti128 $0x1,%ymm1,%xmm5
     f4b:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     f4f:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     f55:	c4 c1 79 7e ec       	vmovd  %xmm5,%r12d
     f5a:	c4 c3 79 16 ee 02    	vpextrd $0x2,%xmm5,%r14d
     f60:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     f65:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     f6a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     f6f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     f74:	c4 c3 79 16 ec 01    	vpextrd $0x1,%xmm5,%r12d
     f7a:	c4 c3 79 16 ee 03    	vpextrd $0x3,%xmm5,%r14d
     f80:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     f85:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     f8a:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     f90:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     f96:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
     f9c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     fa2:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     fa6:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     fab:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     fb2:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
     fb9:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     fbe:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     fc2:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     fc8:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     fcf:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
     fd6:	4c 89 ca             	mov    %r9,%rdx
     fd9:	49 83 c1 08          	add    $0x8,%r9
     fdd:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     fe1:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
     fe7:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
     fec:	c5 f9 6f f1          	vmovdqa %xmm1,%xmm6
     ff0:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     ff6:	c5 d1 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm5
     ffb:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
    1000:	c5 d1 eb ee          	vpor   %xmm6,%xmm5,%xmm5
    1004:	c5 f9 d6 48 f8       	vmovq  %xmm1,-0x8(%rax)
    1009:	c5 fa 7f 68 e8       	vmovdqu %xmm5,-0x18(%rax)
    100e:	4c 39 c9             	cmp    %r9,%rcx
    1011:	0f 83 e9 fe ff ff    	jae    f00 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
    1017:	48 39 ca             	cmp    %rcx,%rdx
    101a:	0f 83 a0 03 00 00    	jae    13c0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    1020:	4c 8d 14 52          	lea    (%rdx,%rdx,2),%r10
    1024:	4f 8d 1c 10          	lea    (%r8,%r10,1),%r11
    1028:	41 0f b6 43 01       	movzbl 0x1(%r11),%eax
    102d:	45 0f b6 4b 02       	movzbl 0x2(%r11),%r9d
    1032:	c1 e0 08             	shl    $0x8,%eax
    1035:	41 c1 e1 10          	shl    $0x10,%r9d
    1039:	44 09 c8             	or     %r9d,%eax
    103c:	45 0f b6 0b          	movzbl (%r11),%r9d
    1040:	44 09 c8             	or     %r9d,%eax
    1043:	41 89 c1             	mov    %eax,%r9d
    1046:	8d 1c 85 00 00 00 00 	lea    0x0(,%rax,4),%ebx
    104d:	41 c1 e1 04          	shl    $0x4,%r9d
    1051:	81 e3 00 f0 03 00    	and    $0x3f000,%ebx
    1057:	41 81 e1 c0 0f 00 00 	and    $0xfc0,%r9d
    105e:	41 09 d9             	or     %ebx,%r9d
    1061:	89 c3                	mov    %eax,%ebx
    1063:	81 e3 03 00 fc 00    	and    $0xfc0003,%ebx
    1069:	41 09 d9             	or     %ebx,%r9d
    106c:	89 c3                	mov    %eax,%ebx
    106e:	c1 e8 0c             	shr    $0xc,%eax
    1071:	c1 eb 06             	shr    $0x6,%ebx
    1074:	83 e0 30             	and    $0x30,%eax
    1077:	83 e3 0c             	and    $0xc,%ebx
    107a:	41 09 d9             	or     %ebx,%r9d
    107d:	44 09 c8             	or     %r9d,%eax
    1080:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1084:	4c 8d 0c 86          	lea    (%rsi,%rax,4),%r9
    1088:	41 8b 01             	mov    (%r9),%eax
    108b:	45 0f b7 09          	movzwl (%r9),%r9d
    108f:	c1 e8 10             	shr    $0x10,%eax
    1092:	66 45 89 0b          	mov    %r9w,(%r11)
    1096:	41 88 43 02          	mov    %al,0x2(%r11)
    109a:	48 8d 42 01          	lea    0x1(%rdx),%rax
    109e:	48 39 c8             	cmp    %rcx,%rax
    10a1:	0f 83 19 03 00 00    	jae    13c0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    10a7:	4f 8d 5c 10 03       	lea    0x3(%r8,%r10,1),%r11
    10ac:	41 0f b6 43 01       	movzbl 0x1(%r11),%eax
    10b1:	45 0f b6 4b 02       	movzbl 0x2(%r11),%r9d
    10b6:	c1 e0 08             	shl    $0x8,%eax
    10b9:	41 c1 e1 10          	shl    $0x10,%r9d
    10bd:	44 09 c8             	or     %r9d,%eax
    10c0:	45 0f b6 0b          	movzbl (%r11),%r9d
    10c4:	44 09 c8             	or     %r9d,%eax
    10c7:	41 89 c1             	mov    %eax,%r9d
    10ca:	8d 1c 85 00 00 00 00 	lea    0x0(,%rax,4),%ebx
    10d1:	41 c1 e1 04          	shl    $0x4,%r9d
    10d5:	81 e3 00 f0 03 00    	and    $0x3f000,%ebx
    10db:	41 81 e1 c0 0f 00 00 	and    $0xfc0,%r9d
    10e2:	41 09 d9             	or     %ebx,%r9d
    10e5:	89 c3                	mov    %eax,%ebx
    10e7:	81 e3 03 00 fc 00    	and    $0xfc0003,%ebx
    10ed:	41 09 d9             	or     %ebx,%r9d
    10f0:	89 c3                	mov    %eax,%ebx
    10f2:	c1 e8 0c             	shr    $0xc,%eax
    10f5:	c1 eb 06             	shr    $0x6,%ebx
    10f8:	83 e0 30             	and    $0x30,%eax
    10fb:	83 e3 0c             	and    $0xc,%ebx
    10fe:	41 09 d9             	or     %ebx,%r9d
    1101:	44 09 c8             	or     %r9d,%eax
    1104:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1108:	4c 8d 0c 86          	lea    (%rsi,%rax,4),%r9
    110c:	41 8b 01             	mov    (%r9),%eax
    110f:	45 0f b7 09          	movzwl (%r9),%r9d
    1113:	c1 e8 10             	shr    $0x10,%eax
    1116:	66 45 89 0b          	mov    %r9w,(%r11)
    111a:	41 88 43 02          	mov    %al,0x2(%r11)
    111e:	48 8d 42 02          	lea    0x2(%rdx),%rax
    1122:	48 39 c8             	cmp    %rcx,%rax
    1125:	0f 83 95 02 00 00    	jae    13c0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    112b:	4f 8d 5c 10 06       	lea    0x6(%r8,%r10,1),%r11
    1130:	41 0f b6 43 01       	movzbl 0x1(%r11),%eax
    1135:	45 0f b6 4b 02       	movzbl 0x2(%r11),%r9d
    113a:	c1 e0 08             	shl    $0x8,%eax
    113d:	41 c1 e1 10          	shl    $0x10,%r9d
    1141:	44 09 c8             	or     %r9d,%eax
    1144:	45 0f b6 0b          	movzbl (%r11),%r9d
    1148:	44 09 c8             	or     %r9d,%eax
    114b:	89 c3                	mov    %eax,%ebx
    114d:	44 8d 0c 85 00 00 00 	lea    0x0(,%rax,4),%r9d
    1154:	00 
    1155:	c1 e3 04             	shl    $0x4,%ebx
    1158:	41 81 e1 00 f0 03 00 	and    $0x3f000,%r9d
    115f:	81 e3 c0 0f 00 00    	and    $0xfc0,%ebx
    1165:	41 09 d9             	or     %ebx,%r9d
    1168:	89 c3                	mov    %eax,%ebx
    116a:	81 e3 03 00 fc 00    	and    $0xfc0003,%ebx
    1170:	41 09 d9             	or     %ebx,%r9d
    1173:	89 c3                	mov    %eax,%ebx
    1175:	c1 e8 0c             	shr    $0xc,%eax
    1178:	c1 eb 06             	shr    $0x6,%ebx
    117b:	83 e0 30             	and    $0x30,%eax
    117e:	83 e3 0c             	and    $0xc,%ebx
    1181:	41 09 d9             	or     %ebx,%r9d
    1184:	44 09 c8             	or     %r9d,%eax
    1187:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    118b:	4c 8d 0c 86          	lea    (%rsi,%rax,4),%r9
    118f:	41 8b 01             	mov    (%r9),%eax
    1192:	45 0f b7 09          	movzwl (%r9),%r9d
    1196:	c1 e8 10             	shr    $0x10,%eax
    1199:	66 45 89 0b          	mov    %r9w,(%r11)
    119d:	41 88 43 02          	mov    %al,0x2(%r11)
    11a1:	48 8d 42 03          	lea    0x3(%rdx),%rax
    11a5:	48 39 c8             	cmp    %rcx,%rax
    11a8:	0f 83 12 02 00 00    	jae    13c0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    11ae:	4f 8d 5c 10 09       	lea    0x9(%r8,%r10,1),%r11
    11b3:	41 0f b6 43 02       	movzbl 0x2(%r11),%eax
    11b8:	45 0f b6 4b 01       	movzbl 0x1(%r11),%r9d
    11bd:	c1 e0 10             	shl    $0x10,%eax
    11c0:	41 c1 e1 08          	shl    $0x8,%r9d
    11c4:	44 09 c8             	or     %r9d,%eax
    11c7:	45 0f b6 0b          	movzbl (%r11),%r9d
    11cb:	44 09 c8             	or     %r9d,%eax
    11ce:	89 c3                	mov    %eax,%ebx
    11d0:	44 8d 0c 85 00 00 00 	lea    0x0(,%rax,4),%r9d
    11d7:	00 
    11d8:	c1 e3 04             	shl    $0x4,%ebx
    11db:	41 81 e1 00 f0 03 00 	and    $0x3f000,%r9d
    11e2:	81 e3 c0 0f 00 00    	and    $0xfc0,%ebx
    11e8:	41 09 d9             	or     %ebx,%r9d
    11eb:	89 c3                	mov    %eax,%ebx
    11ed:	81 e3 03 00 fc 00    	and    $0xfc0003,%ebx
    11f3:	41 09 d9             	or     %ebx,%r9d
    11f6:	89 c3                	mov    %eax,%ebx
    11f8:	c1 e8 0c             	shr    $0xc,%eax
    11fb:	c1 eb 06             	shr    $0x6,%ebx
    11fe:	83 e0 30             	and    $0x30,%eax
    1201:	83 e3 0c             	and    $0xc,%ebx
    1204:	41 09 d9             	or     %ebx,%r9d
    1207:	44 09 c8             	or     %r9d,%eax
    120a:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    120e:	4c 8d 0c 86          	lea    (%rsi,%rax,4),%r9
    1212:	41 8b 01             	mov    (%r9),%eax
    1215:	45 0f b7 09          	movzwl (%r9),%r9d
    1219:	c1 e8 10             	shr    $0x10,%eax
    121c:	66 45 89 0b          	mov    %r9w,(%r11)
    1220:	41 88 43 02          	mov    %al,0x2(%r11)
    1224:	48 8d 42 04          	lea    0x4(%rdx),%rax
    1228:	48 39 c8             	cmp    %rcx,%rax
    122b:	0f 83 8f 01 00 00    	jae    13c0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    1231:	4f 8d 5c 10 0c       	lea    0xc(%r8,%r10,1),%r11
    1236:	41 0f b6 43 02       	movzbl 0x2(%r11),%eax
    123b:	45 0f b6 4b 01       	movzbl 0x1(%r11),%r9d
    1240:	c1 e0 10             	shl    $0x10,%eax
    1243:	41 c1 e1 08          	shl    $0x8,%r9d
    1247:	44 09 c8             	or     %r9d,%eax
    124a:	45 0f b6 0b          	movzbl (%r11),%r9d
    124e:	44 09 c8             	or     %r9d,%eax
    1251:	89 c3                	mov    %eax,%ebx
    1253:	44 8d 0c 85 00 00 00 	lea    0x0(,%rax,4),%r9d
    125a:	00 
    125b:	c1 e3 04             	shl    $0x4,%ebx
    125e:	41 81 e1 00 f0 03 00 	and    $0x3f000,%r9d
    1265:	81 e3 c0 0f 00 00    	and    $0xfc0,%ebx
    126b:	41 09 d9             	or     %ebx,%r9d
    126e:	89 c3                	mov    %eax,%ebx
    1270:	81 e3 03 00 fc 00    	and    $0xfc0003,%ebx
    1276:	41 09 d9             	or     %ebx,%r9d
    1279:	89 c3                	mov    %eax,%ebx
    127b:	c1 e8 0c             	shr    $0xc,%eax
    127e:	c1 eb 06             	shr    $0x6,%ebx
    1281:	83 e0 30             	and    $0x30,%eax
    1284:	83 e3 0c             	and    $0xc,%ebx
    1287:	41 09 d9             	or     %ebx,%r9d
    128a:	44 09 c8             	or     %r9d,%eax
    128d:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1291:	4c 8d 0c 86          	lea    (%rsi,%rax,4),%r9
    1295:	41 8b 01             	mov    (%r9),%eax
    1298:	45 0f b7 09          	movzwl (%r9),%r9d
    129c:	c1 e8 10             	shr    $0x10,%eax
    129f:	66 45 89 0b          	mov    %r9w,(%r11)
    12a3:	41 88 43 02          	mov    %al,0x2(%r11)
    12a7:	48 8d 42 05          	lea    0x5(%rdx),%rax
    12ab:	48 39 c8             	cmp    %rcx,%rax
    12ae:	0f 83 0c 01 00 00    	jae    13c0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    12b4:	4f 8d 5c 10 0f       	lea    0xf(%r8,%r10,1),%r11
    12b9:	41 0f b6 43 02       	movzbl 0x2(%r11),%eax
    12be:	45 0f b6 4b 01       	movzbl 0x1(%r11),%r9d
    12c3:	c1 e0 10             	shl    $0x10,%eax
    12c6:	41 c1 e1 08          	shl    $0x8,%r9d
    12ca:	44 09 c8             	or     %r9d,%eax
    12cd:	45 0f b6 0b          	movzbl (%r11),%r9d
    12d1:	44 09 c8             	or     %r9d,%eax
    12d4:	89 c3                	mov    %eax,%ebx
    12d6:	44 8d 0c 85 00 00 00 	lea    0x0(,%rax,4),%r9d
    12dd:	00 
    12de:	c1 e3 04             	shl    $0x4,%ebx
    12e1:	41 81 e1 00 f0 03 00 	and    $0x3f000,%r9d
    12e8:	81 e3 c0 0f 00 00    	and    $0xfc0,%ebx
    12ee:	41 09 d9             	or     %ebx,%r9d
    12f1:	89 c3                	mov    %eax,%ebx
    12f3:	81 e3 03 00 fc 00    	and    $0xfc0003,%ebx
    12f9:	41 09 d9             	or     %ebx,%r9d
    12fc:	89 c3                	mov    %eax,%ebx
    12fe:	c1 e8 0c             	shr    $0xc,%eax
    1301:	c1 eb 06             	shr    $0x6,%ebx
    1304:	83 e0 30             	and    $0x30,%eax
    1307:	83 e3 0c             	and    $0xc,%ebx
    130a:	41 09 d9             	or     %ebx,%r9d
    130d:	44 09 c8             	or     %r9d,%eax
    1310:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1314:	4c 8d 0c 86          	lea    (%rsi,%rax,4),%r9
    1318:	41 8b 01             	mov    (%r9),%eax
    131b:	45 0f b7 09          	movzwl (%r9),%r9d
    131f:	c1 e8 10             	shr    $0x10,%eax
    1322:	66 45 89 0b          	mov    %r9w,(%r11)
    1326:	41 88 43 02          	mov    %al,0x2(%r11)
    132a:	48 8d 42 06          	lea    0x6(%rdx),%rax
    132e:	48 39 c8             	cmp    %rcx,%rax
    1331:	0f 83 89 00 00 00    	jae    13c0 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    1337:	4b 8d 4c 10 12       	lea    0x12(%r8,%r10,1),%rcx
    133c:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
    1340:	0f b6 51 02          	movzbl 0x2(%rcx),%edx
    1344:	c1 e0 08             	shl    $0x8,%eax
    1347:	c1 e2 10             	shl    $0x10,%edx
    134a:	09 d0                	or     %edx,%eax
    134c:	0f b6 11             	movzbl (%rcx),%edx
    134f:	09 d0                	or     %edx,%eax
    1351:	89 c2                	mov    %eax,%edx
    1353:	44 8d 04 85 00 00 00 	lea    0x0(,%rax,4),%r8d
    135a:	00 
    135b:	c1 e2 04             	shl    $0x4,%edx
    135e:	41 81 e0 00 f0 03 00 	and    $0x3f000,%r8d
    1365:	81 e2 c0 0f 00 00    	and    $0xfc0,%edx
    136b:	44 09 c2             	or     %r8d,%edx
    136e:	41 89 c0             	mov    %eax,%r8d
    1371:	41 81 e0 03 00 fc 00 	and    $0xfc0003,%r8d
    1378:	44 09 c2             	or     %r8d,%edx
    137b:	41 89 c0             	mov    %eax,%r8d
    137e:	c1 e8 0c             	shr    $0xc,%eax
    1381:	41 c1 e8 06          	shr    $0x6,%r8d
    1385:	83 e0 30             	and    $0x30,%eax
    1388:	41 83 e0 0c          	and    $0xc,%r8d
    138c:	44 09 c2             	or     %r8d,%edx
    138f:	09 d0                	or     %edx,%eax
    1391:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1395:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1399:	8b 02                	mov    (%rdx),%eax
    139b:	0f b7 12             	movzwl (%rdx),%edx
    139e:	c1 e8 10             	shr    $0x10,%eax
    13a1:	66 89 11             	mov    %dx,(%rcx)
    13a4:	88 41 02             	mov    %al,0x2(%rcx)
    13a7:	c5 f8 77             	vzeroupper
    13aa:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    13ae:	5b                   	pop    %rbx
    13af:	41 5c                	pop    %r12
    13b1:	41 5d                	pop    %r13
    13b3:	41 5e                	pop    %r14
    13b5:	41 5f                	pop    %r15
    13b7:	5d                   	pop    %rbp
    13b8:	c3                   	ret
    13b9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    13c0:	c5 f8 77             	vzeroupper
    13c3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    13c7:	5b                   	pop    %rbx
    13c8:	41 5c                	pop    %r12
    13ca:	41 5d                	pop    %r13
    13cc:	41 5e                	pop    %r14
    13ce:	41 5f                	pop    %r15
    13d0:	5d                   	pop    %rbp
    13d1:	c3                   	ret
    13d2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    13d8:	48 89 ca             	mov    %rcx,%rdx
    13db:	e9 bf fa ff ff       	jmp    e9f <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe9f>
    13e0:	c3                   	ret
    13e1:	49 8d 41 28          	lea    0x28(%r9),%rax
    13e5:	4c 89 ca             	mov    %r9,%rdx
    13e8:	e9 1a f6 ff ff       	jmp    a07 <jshc_channel::avx2_chain_tilemadd(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa07>
    13ed:	0f 1f 00             	nopl   (%rax)

00000000000013f0 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    13f0:	f3 0f 1e fa          	endbr64
    13f4:	4d 85 c0             	test   %r8,%r8
    13f7:	0f 84 63 14 00 00    	je     2860 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1470>
    13fd:	55                   	push   %rbp
    13fe:	b8 00 04 00 00       	mov    $0x400,%eax
    1403:	49 89 d2             	mov    %rdx,%r10
    1406:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    140a:	49 89 cb             	mov    %rcx,%r11
    140d:	48 89 e5             	mov    %rsp,%rbp
    1410:	41 57                	push   %r15
    1412:	41 56                	push   %r14
    1414:	41 55                	push   %r13
    1416:	41 54                	push   %r12
    1418:	53                   	push   %rbx
    1419:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    141d:	48 83 ec 28          	sub    $0x28,%rsp
    1421:	48 39 c2             	cmp    %rax,%rdx
    1424:	48 0f 47 d0          	cmova  %rax,%rdx
    1428:	31 c0                	xor    %eax,%eax
    142a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1430:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
    1435:	48 83 c0 40          	add    $0x40,%rax
    1439:	48 39 d0             	cmp    %rdx,%rax
    143c:	72 f2                	jb     1430 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
    143e:	4c 89 d3             	mov    %r10,%rbx
    1441:	4d 89 d9             	mov    %r11,%r9
    1444:	31 c9                	xor    %ecx,%ecx
    1446:	e9 88 00 00 00       	jmp    14d3 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe3>
    144b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1450:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    1454:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1458:	48 ff c1             	inc    %rcx
    145b:	49 83 c1 03          	add    $0x3,%r9
    145f:	48 83 c3 03          	add    $0x3,%rbx
    1463:	c1 e2 10             	shl    $0x10,%edx
    1466:	c1 e0 08             	shl    $0x8,%eax
    1469:	09 d0                	or     %edx,%eax
    146b:	0f b6 53 fd          	movzbl -0x3(%rbx),%edx
    146f:	09 d0                	or     %edx,%eax
    1471:	89 c2                	mov    %eax,%edx
    1473:	44 8d 24 85 00 00 00 	lea    0x0(,%rax,4),%r12d
    147a:	00 
    147b:	c1 e2 04             	shl    $0x4,%edx
    147e:	41 81 e4 00 f0 03 00 	and    $0x3f000,%r12d
    1485:	81 e2 c0 0f 00 00    	and    $0xfc0,%edx
    148b:	44 09 e2             	or     %r12d,%edx
    148e:	41 89 c4             	mov    %eax,%r12d
    1491:	41 81 e4 03 00 fc 00 	and    $0xfc0003,%r12d
    1498:	44 09 e2             	or     %r12d,%edx
    149b:	41 89 c4             	mov    %eax,%r12d
    149e:	c1 e8 0c             	shr    $0xc,%eax
    14a1:	41 c1 ec 06          	shr    $0x6,%r12d
    14a5:	83 e0 30             	and    $0x30,%eax
    14a8:	41 83 e4 0c          	and    $0xc,%r12d
    14ac:	44 09 e2             	or     %r12d,%edx
    14af:	09 d0                	or     %edx,%eax
    14b1:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    14b5:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    14b9:	8b 02                	mov    (%rdx),%eax
    14bb:	0f b7 12             	movzwl (%rdx),%edx
    14be:	c1 e8 10             	shr    $0x10,%eax
    14c1:	66 41 89 51 fd       	mov    %dx,-0x3(%r9)
    14c6:	41 88 41 ff          	mov    %al,-0x1(%r9)
    14ca:	49 39 c8             	cmp    %rcx,%r8
    14cd:	0f 84 7d 13 00 00    	je     2850 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1460>
    14d3:	41 f6 c1 3f          	test   $0x3f,%r9b
    14d7:	0f 85 73 ff ff ff    	jne    1450 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    14dd:	48 8d 41 48          	lea    0x48(%rcx),%rax
    14e1:	49 39 c0             	cmp    %rax,%r8
    14e4:	0f 82 77 13 00 00    	jb     2861 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1471>
    14ea:	41 b9 03 03 03 00    	mov    $0x30303,%r9d
    14f0:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
    14f4:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    14f8:	4c 89 54 24 a0       	mov    %r10,-0x60(%rsp)
    14fd:	c4 c1 79 6e f1       	vmovd  %r9d,%xmm6
    1502:	41 b9 00 00 fc 00    	mov    $0xfc0000,%r9d
    1508:	49 8d 14 03          	lea    (%r11,%rax,1),%rdx
    150c:	4c 89 5c 24 98       	mov    %r11,-0x68(%rsp)
    1511:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
    1516:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # 151e <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12e>
    151d:	00 
    151e:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # 1526 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x136>
    1525:	00 
    1526:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
    152d:	00 
    152e:	c5 fd 7f 74 24 08    	vmovdqa %ymm6,0x8(%rsp)
    1534:	c5 cd 71 d1 0f       	vpsrlw $0xf,%ymm1,%ymm6
    1539:	c5 fd 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm0        # 1541 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x151>
    1540:	00 
    1541:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 1549 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x159>
    1548:	00 
    1549:	c5 fd 7f 74 24 c8    	vmovdqa %ymm6,-0x38(%rsp)
    154f:	c4 c1 79 6e f1       	vmovd  %r9d,%xmm6
    1554:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 155c <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x16c>
    155b:	00 
    155c:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # 1564 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x174>
    1563:	00 
    1564:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
    1569:	c5 fd 7f 74 24 e8    	vmovdqa %ymm6,-0x18(%rsp)
    156f:	eb 0a                	jmp    157b <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x18b>
    1571:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1578:	4c 89 c9             	mov    %r9,%rcx
    157b:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    1582:	4d 39 c8             	cmp    %r9,%r8
    1585:	72 15                	jb     159c <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac>
    1587:	0f 18 00             	prefetchnta (%rax)
    158a:	0f 18 40 40          	prefetchnta 0x40(%rax)
    158e:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    1595:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    159c:	c5 fa 6f 88 00 fc ff 	vmovdqu -0x400(%rax),%xmm1
    15a3:	ff 
    15a4:	c5 fa 7e 90 10 fc ff 	vmovq  -0x3f0(%rax),%xmm2
    15ab:	ff 
    15ac:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    15b3:	48 05 c0 00 00 00    	add    $0xc0,%rax
    15b9:	c5 7d 6f 64 24 08    	vmovdqa 0x8(%rsp),%ymm12
    15bf:	c5 7d 6f 6c 24 e8    	vmovdqa -0x18(%rsp),%ymm13
    15c5:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
    15cb:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    15d1:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    15d6:	c4 c1 75 db dc       	vpand  %ymm12,%ymm1,%ymm3
    15db:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
    15e0:	c4 c1 75 db cd       	vpand  %ymm13,%ymm1,%ymm1
    15e5:	c4 c2 65 04 de       	vpmaddubsw %ymm14,%ymm3,%ymm3
    15ea:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
    15ef:	c5 e5 f5 5c 24 c8    	vpmaddwd -0x38(%rsp),%ymm3,%ymm3
    15f5:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
    15f9:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
    15fd:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1601:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
    1607:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    160c:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1612:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    1617:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    161d:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1622:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1627:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    162c:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1631:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1637:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    163d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1642:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1647:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    164d:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1653:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1659:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    165f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1664:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1669:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1670:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1677:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    167d:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1681:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1686:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
    168d:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    1694:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
    1698:	c5 fa 7e 90 68 fb ff 	vmovq  -0x498(%rax),%xmm2
    169f:	ff 
    16a0:	c4 e3 4d 38 f1 01    	vinserti128 $0x1,%xmm1,%ymm6,%ymm6
    16a6:	c5 fa 6f 88 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm1
    16ad:	ff 
    16ae:	c4 c2 4d 00 f7       	vpshufb %ymm15,%ymm6,%ymm6
    16b3:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
    16b9:	c4 e2 25 36 f6       	vpermd %ymm6,%ymm11,%ymm6
    16be:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    16c4:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    16c9:	c4 c1 75 db dc       	vpand  %ymm12,%ymm1,%ymm3
    16ce:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
    16d3:	c4 c1 75 db cd       	vpand  %ymm13,%ymm1,%ymm1
    16d8:	c4 c2 65 04 de       	vpmaddubsw %ymm14,%ymm3,%ymm3
    16dd:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
    16e2:	c5 e5 f5 5c 24 c8    	vpmaddwd -0x38(%rsp),%ymm3,%ymm3
    16e8:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
    16ec:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
    16f0:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    16f4:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
    16fa:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    16ff:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1705:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    170a:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    170f:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1714:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    171a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    171f:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    1725:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    172b:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1731:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1736:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    173b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1740:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1745:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    174b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1750:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1756:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    175c:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    1762:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1769:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1770:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
    1777:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    177b:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1780:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    1787:	c5 e1 6c da          	vpunpcklqdq %xmm2,%xmm3,%xmm3
    178b:	c5 fa 7e 90 80 fb ff 	vmovq  -0x480(%rax),%xmm2
    1792:	ff 
    1793:	c4 e3 65 38 d9 01    	vinserti128 $0x1,%xmm1,%ymm3,%ymm3
    1799:	c5 fa 6f 88 70 fb ff 	vmovdqu -0x490(%rax),%xmm1
    17a0:	ff 
    17a1:	c4 c2 65 00 df       	vpshufb %ymm15,%ymm3,%ymm3
    17a6:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
    17ac:	c4 e2 25 36 db       	vpermd %ymm3,%ymm11,%ymm3
    17b1:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    17b7:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    17bc:	c4 c1 75 db e4       	vpand  %ymm12,%ymm1,%ymm4
    17c1:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
    17c6:	c4 c1 75 db cd       	vpand  %ymm13,%ymm1,%ymm1
    17cb:	c4 c2 5d 04 e6       	vpmaddubsw %ymm14,%ymm4,%ymm4
    17d0:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
    17d5:	c5 dd f5 64 24 c8    	vpmaddwd -0x38(%rsp),%ymm4,%ymm4
    17db:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
    17df:	c5 ed eb d4          	vpor   %ymm4,%ymm2,%ymm2
    17e3:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    17e7:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
    17ed:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    17f2:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    17f8:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    17fd:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    1803:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1808:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    180d:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1812:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1817:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    181d:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    1823:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1828:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    182d:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    1833:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1839:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    183f:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1845:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    184a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    184f:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1856:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    185d:	c5 f9 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm4
    1862:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1866:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    186c:	c4 a3 59 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm4,%xmm4
    1873:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    187a:	c5 e9 6c d4          	vpunpcklqdq %xmm4,%xmm2,%xmm2
    187e:	c5 fa 6f a0 88 fb ff 	vmovdqu -0x478(%rax),%xmm4
    1885:	ff 
    1886:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
    188c:	c5 fa 7e 88 98 fb ff 	vmovq  -0x468(%rax),%xmm1
    1893:	ff 
    1894:	c4 c2 6d 00 d7       	vpshufb %ymm15,%ymm2,%ymm2
    1899:	c4 e3 71 0f cc 0c    	vpalignr $0xc,%xmm4,%xmm1,%xmm1
    189f:	c4 e2 25 36 d2       	vpermd %ymm2,%ymm11,%ymm2
    18a4:	c4 e3 5d 38 e1 01    	vinserti128 $0x1,%xmm1,%ymm4,%ymm4
    18aa:	c4 c2 5d 00 e2       	vpshufb %ymm10,%ymm4,%ymm4
    18af:	c4 c1 5d db ec       	vpand  %ymm12,%ymm4,%ymm5
    18b4:	c4 c2 5d 00 c9       	vpshufb %ymm9,%ymm4,%ymm1
    18b9:	c4 c1 5d db e5       	vpand  %ymm13,%ymm4,%ymm4
    18be:	c4 c2 55 04 ee       	vpmaddubsw %ymm14,%ymm5,%ymm5
    18c3:	c5 f5 71 d1 02       	vpsrlw $0x2,%ymm1,%ymm1
    18c8:	c5 d5 f5 6c 24 c8    	vpmaddwd -0x38(%rsp),%ymm5,%ymm5
    18ce:	c5 f5 f5 c8          	vpmaddwd %ymm0,%ymm1,%ymm1
    18d2:	c5 f5 eb cd          	vpor   %ymm5,%ymm1,%ymm1
    18d6:	c5 f5 eb cc          	vpor   %ymm4,%ymm1,%ymm1
    18da:	c4 e3 7d 39 cc 01    	vextracti128 $0x1,%ymm1,%xmm4
    18e0:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    18e5:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    18eb:	c4 c1 79 7e e4       	vmovd  %xmm4,%r12d
    18f0:	c4 c3 79 16 e6 02    	vpextrd $0x2,%xmm4,%r14d
    18f6:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    18fb:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1900:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1905:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    190a:	c4 c3 79 16 e4 01    	vpextrd $0x1,%xmm4,%r12d
    1910:	c4 c3 79 16 e6 03    	vpextrd $0x3,%xmm4,%r14d
    1916:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    191b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1920:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    1926:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    192c:	c4 a1 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm4
    1932:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1938:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    193d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1942:	c4 a3 59 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm4,%xmm4
    1949:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1950:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
    1956:	c5 f1 6c cc          	vpunpcklqdq %xmm4,%xmm1,%xmm1
    195a:	c5 f9 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm4
    195f:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
    1966:	c4 a3 59 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm4,%xmm4
    196d:	c5 d1 6c ec          	vpunpcklqdq %xmm4,%xmm5,%xmm5
    1971:	c5 fa 7e a0 b0 fb ff 	vmovq  -0x450(%rax),%xmm4
    1978:	ff 
    1979:	c4 e3 55 38 e9 01    	vinserti128 $0x1,%xmm1,%ymm5,%ymm5
    197f:	c5 fa 6f 88 a0 fb ff 	vmovdqu -0x460(%rax),%xmm1
    1986:	ff 
    1987:	c4 c2 55 00 ef       	vpshufb %ymm15,%ymm5,%ymm5
    198c:	c4 e3 59 0f e1 0c    	vpalignr $0xc,%xmm1,%xmm4,%xmm4
    1992:	c4 e2 25 36 ed       	vpermd %ymm5,%ymm11,%ymm5
    1997:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    199d:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    19a2:	c5 f5 db 7c 24 08    	vpand  0x8(%rsp),%ymm1,%ymm7
    19a8:	c4 c2 75 00 e1       	vpshufb %ymm9,%ymm1,%ymm4
    19ad:	c4 c1 75 db cd       	vpand  %ymm13,%ymm1,%ymm1
    19b2:	c5 dd 71 d4 02       	vpsrlw $0x2,%ymm4,%ymm4
    19b7:	c4 c2 45 04 fe       	vpmaddubsw %ymm14,%ymm7,%ymm7
    19bc:	c5 dd f5 e0          	vpmaddwd %ymm0,%ymm4,%ymm4
    19c0:	c5 c5 f5 7c 24 c8    	vpmaddwd -0x38(%rsp),%ymm7,%ymm7
    19c6:	c5 dd eb e7          	vpor   %ymm7,%ymm4,%ymm4
    19ca:	c5 f5 eb cc          	vpor   %ymm4,%ymm1,%ymm1
    19ce:	c4 e3 7d 39 cc 01    	vextracti128 $0x1,%ymm1,%xmm4
    19d4:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    19d9:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    19df:	c4 c3 79 16 e6 02    	vpextrd $0x2,%xmm4,%r14d
    19e5:	c4 c1 79 7e e4       	vmovd  %xmm4,%r12d
    19ea:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    19ef:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    19f4:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    19f9:	c4 c3 79 16 e6 03    	vpextrd $0x3,%xmm4,%r14d
    19ff:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1a04:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    1a0a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1a0f:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1a15:	c4 c3 79 16 e4 01    	vpextrd $0x1,%xmm4,%r12d
    1a1b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1a20:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1a26:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1a2b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1a30:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1a37:	c4 a1 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm4
    1a3d:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    1a42:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
    1a49:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    1a50:	c5 d9 6c e1          	vpunpcklqdq %xmm1,%xmm4,%xmm4
    1a54:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1a5a:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1a61:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
    1a65:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    1a6b:	c5 fa 7e a0 c8 fb ff 	vmovq  -0x438(%rax),%xmm4
    1a72:	ff 
    1a73:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
    1a78:	c4 62 25 36 e1       	vpermd %ymm1,%ymm11,%ymm12
    1a7d:	c5 fa 6f 88 b8 fb ff 	vmovdqu -0x448(%rax),%xmm1
    1a84:	ff 
    1a85:	c4 e3 59 0f e1 0c    	vpalignr $0xc,%xmm1,%xmm4,%xmm4
    1a8b:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    1a91:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    1a96:	c5 f5 db 7c 24 08    	vpand  0x8(%rsp),%ymm1,%ymm7
    1a9c:	c4 c2 75 00 e1       	vpshufb %ymm9,%ymm1,%ymm4
    1aa1:	c5 f5 db 4c 24 e8    	vpand  -0x18(%rsp),%ymm1,%ymm1
    1aa7:	c5 dd 71 d4 02       	vpsrlw $0x2,%ymm4,%ymm4
    1aac:	c4 c2 45 04 fe       	vpmaddubsw %ymm14,%ymm7,%ymm7
    1ab1:	c5 dd f5 e0          	vpmaddwd %ymm0,%ymm4,%ymm4
    1ab5:	c5 c5 f5 7c 24 c8    	vpmaddwd -0x38(%rsp),%ymm7,%ymm7
    1abb:	c5 dd eb e7          	vpor   %ymm7,%ymm4,%ymm4
    1abf:	c5 f5 eb cc          	vpor   %ymm4,%ymm1,%ymm1
    1ac3:	c4 e3 7d 39 cc 01    	vextracti128 $0x1,%ymm1,%xmm4
    1ac9:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    1ace:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1ad4:	c4 c1 79 7e e4       	vmovd  %xmm4,%r12d
    1ad9:	c4 c3 79 16 e6 02    	vpextrd $0x2,%xmm4,%r14d
    1adf:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1ae4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1ae9:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1aee:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1af3:	c4 c3 79 16 e4 01    	vpextrd $0x1,%xmm4,%r12d
    1af9:	c4 c3 79 16 e6 03    	vpextrd $0x3,%xmm4,%r14d
    1aff:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1b04:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1b09:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    1b0f:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1b15:	c4 a1 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm4
    1b1b:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1b21:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1b26:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1b2b:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1b32:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
    1b39:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    1b3e:	c5 d9 6c e1          	vpunpcklqdq %xmm1,%xmm4,%xmm4
    1b42:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1b48:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    1b4f:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1b56:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
    1b5a:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    1b60:	c5 fa 7e a0 e0 fb ff 	vmovq  -0x420(%rax),%xmm4
    1b67:	ff 
    1b68:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
    1b6d:	c4 62 25 36 e9       	vpermd %ymm1,%ymm11,%ymm13
    1b72:	c5 fa 6f 88 d0 fb ff 	vmovdqu -0x430(%rax),%xmm1
    1b79:	ff 
    1b7a:	c4 e3 59 0f e1 0c    	vpalignr $0xc,%xmm1,%xmm4,%xmm4
    1b80:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    1b86:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    1b8b:	c5 f5 db 7c 24 08    	vpand  0x8(%rsp),%ymm1,%ymm7
    1b91:	c4 c2 75 00 e1       	vpshufb %ymm9,%ymm1,%ymm4
    1b96:	c5 dd 71 d4 02       	vpsrlw $0x2,%ymm4,%ymm4
    1b9b:	c4 c2 45 04 fe       	vpmaddubsw %ymm14,%ymm7,%ymm7
    1ba0:	c5 dd f5 e0          	vpmaddwd %ymm0,%ymm4,%ymm4
    1ba4:	c5 c5 f5 7c 24 c8    	vpmaddwd -0x38(%rsp),%ymm7,%ymm7
    1baa:	c5 f5 db 4c 24 e8    	vpand  -0x18(%rsp),%ymm1,%ymm1
    1bb0:	c5 dd eb e7          	vpor   %ymm7,%ymm4,%ymm4
    1bb4:	c5 f5 eb cc          	vpor   %ymm4,%ymm1,%ymm1
    1bb8:	c4 e3 7d 39 cc 01    	vextracti128 $0x1,%ymm1,%xmm4
    1bbe:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    1bc3:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1bc9:	c4 c1 79 7e e4       	vmovd  %xmm4,%r12d
    1bce:	c4 c3 79 16 e6 02    	vpextrd $0x2,%xmm4,%r14d
    1bd4:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1bd9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1bde:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1be3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1be8:	c4 c3 79 16 e4 01    	vpextrd $0x1,%xmm4,%r12d
    1bee:	c4 c3 79 16 e6 03    	vpextrd $0x3,%xmm4,%r14d
    1bf4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1bf9:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1bfe:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    1c04:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1c0a:	c4 a1 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm4
    1c10:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1c16:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1c1b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1c20:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1c27:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
    1c2e:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    1c33:	c5 d9 6c e1          	vpunpcklqdq %xmm1,%xmm4,%xmm4
    1c37:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1c3d:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    1c44:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1c4b:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
    1c4f:	c5 fa 7e b8 f8 fb ff 	vmovq  -0x408(%rax),%xmm7
    1c56:	ff 
    1c57:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    1c5d:	c5 fa 6f a0 e8 fb ff 	vmovdqu -0x418(%rax),%xmm4
    1c64:	ff 
    1c65:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
    1c6a:	c4 e3 41 0f fc 0c    	vpalignr $0xc,%xmm4,%xmm7,%xmm7
    1c70:	c4 e2 25 36 c9       	vpermd %ymm1,%ymm11,%ymm1
    1c75:	c4 e3 5d 38 e7 01    	vinserti128 $0x1,%xmm7,%ymm4,%ymm4
    1c7b:	c4 c2 5d 00 e2       	vpshufb %ymm10,%ymm4,%ymm4
    1c80:	c5 5d db 44 24 08    	vpand  0x8(%rsp),%ymm4,%ymm8
    1c86:	c4 c2 5d 00 f9       	vpshufb %ymm9,%ymm4,%ymm7
    1c8b:	c5 dd db 64 24 e8    	vpand  -0x18(%rsp),%ymm4,%ymm4
    1c91:	c5 c5 71 d7 02       	vpsrlw $0x2,%ymm7,%ymm7
    1c96:	c4 42 3d 04 c6       	vpmaddubsw %ymm14,%ymm8,%ymm8
    1c9b:	c5 c5 f5 f8          	vpmaddwd %ymm0,%ymm7,%ymm7
    1c9f:	c5 3d f5 44 24 c8    	vpmaddwd -0x38(%rsp),%ymm8,%ymm8
    1ca5:	c4 c1 45 eb f8       	vpor   %ymm8,%ymm7,%ymm7
    1caa:	c5 dd eb e7          	vpor   %ymm7,%ymm4,%ymm4
    1cae:	c4 e3 7d 39 e7 01    	vextracti128 $0x1,%ymm4,%xmm7
    1cb4:	c4 c1 79 7e e1       	vmovd  %xmm4,%r9d
    1cb9:	c4 c3 79 16 e3 02    	vpextrd $0x2,%xmm4,%r11d
    1cbf:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    1cc4:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    1cca:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1ccf:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1cd4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1cd9:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1cde:	c4 c3 79 16 e1 01    	vpextrd $0x1,%xmm4,%r9d
    1ce4:	c4 c3 79 16 e3 03    	vpextrd $0x3,%xmm4,%r11d
    1cea:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    1cf0:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    1cf6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1cfb:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1d00:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1d05:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1d0a:	c5 f9 7f 5c 24 b8    	vmovdqa %xmm3,-0x48(%rsp)
    1d10:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    1d16:	c4 a1 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm4
    1d1c:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1d22:	c5 f9 7f 54 24 a8    	vmovdqa %xmm2,-0x58(%rsp)
    1d28:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1d2e:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
    1d33:	c4 e3 61 0f 5c 24 b8 	vpalignr $0x8,-0x48(%rsp),%xmm3,%xmm3
    1d3a:	08 
    1d3b:	c4 a3 59 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm4,%xmm4
    1d42:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    1d49:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
    1d50:	c4 e3 65 38 5c 24 a8 	vinserti128 $0x1,-0x58(%rsp),%ymm3,%ymm3
    1d57:	01 
    1d58:	c5 c1 6c fc          	vpunpcklqdq %xmm4,%xmm7,%xmm7
    1d5c:	c4 a1 79 6e 24 96    	vmovd  (%rsi,%r10,4),%xmm4
    1d62:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1d69:	c4 a3 59 22 24 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm4,%xmm4
    1d70:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    1d74:	c4 c1 59 6c e0       	vpunpcklqdq %xmm8,%xmm4,%xmm4
    1d79:	c5 79 6f c5          	vmovdqa %xmm5,%xmm8
    1d7d:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1d83:	c4 e3 5d 38 e7 01    	vinserti128 $0x1,%xmm7,%ymm4,%ymm4
    1d89:	c5 f9 6f fe          	vmovdqa %xmm6,%xmm7
    1d8d:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1d93:	c5 c9 6c 74 24 b8    	vpunpcklqdq -0x48(%rsp),%xmm6,%xmm6
    1d99:	c4 c3 51 0f e8 08    	vpalignr $0x8,%xmm8,%xmm5,%xmm5
    1d9f:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
    1da4:	c5 fd e7 9a 60 ff ff 	vmovntdq %ymm3,-0xa0(%rdx)
    1dab:	ff 
    1dac:	c4 c2 5d 00 e7       	vpshufb %ymm15,%ymm4,%ymm4
    1db1:	c4 e3 6d 38 d5 01    	vinserti128 $0x1,%xmm5,%ymm2,%ymm2
    1db7:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    1dbb:	c4 e2 25 36 e4       	vpermd %ymm4,%ymm11,%ymm4
    1dc0:	c4 e3 45 38 fe 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm7
    1dc6:	c5 fd e7 52 80       	vmovntdq %ymm2,-0x80(%rdx)
    1dcb:	c4 63 7d 39 e5 01    	vextracti128 $0x1,%ymm12,%xmm5
    1dd1:	c5 f9 6f f4          	vmovdqa %xmm4,%xmm6
    1dd5:	c4 63 7d 39 ea 01    	vextracti128 $0x1,%ymm13,%xmm2
    1ddb:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1de1:	c5 fd e7 ba 40 ff ff 	vmovntdq %ymm7,-0xc0(%rdx)
    1de8:	ff 
    1de9:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
    1def:	c5 79 7f e3          	vmovdqa %xmm12,%xmm3
    1df3:	c4 c1 51 6c ed       	vpunpcklqdq %xmm13,%xmm5,%xmm5
    1df8:	c4 c3 69 0f d5 08    	vpalignr $0x8,%xmm13,%xmm2,%xmm2
    1dfe:	c4 e3 59 0f e6 08    	vpalignr $0x8,%xmm6,%xmm4,%xmm4
    1e04:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1e08:	c4 e3 65 38 dd 01    	vinserti128 $0x1,%xmm5,%ymm3,%ymm3
    1e0e:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
    1e14:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    1e1a:	c5 fd e7 5a a0       	vmovntdq %ymm3,-0x60(%rdx)
    1e1f:	c5 fd e7 52 c0       	vmovntdq %ymm2,-0x40(%rdx)
    1e24:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
    1e29:	4d 39 d0             	cmp    %r10,%r8
    1e2c:	0f 83 46 f7 ff ff    	jae    1578 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x188>
    1e32:	4c 8b 54 24 a0       	mov    -0x60(%rsp),%r10
    1e37:	4c 8b 5c 24 98       	mov    -0x68(%rsp),%r11
    1e3c:	48 8d 41 68          	lea    0x68(%rcx),%rax
    1e40:	0f ae f8             	sfence
    1e43:	49 39 c0             	cmp    %rax,%r8
    1e46:	0f 82 99 04 00 00    	jb     22e5 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xef5>
    1e4c:	b9 03 03 03 00       	mov    $0x30303,%ecx
    1e51:	4c 89 54 24 c8       	mov    %r10,-0x38(%rsp)
    1e56:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1e5a:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # 1e62 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa72>
    1e61:	00 
    1e62:	c5 f9 6e f1          	vmovd  %ecx,%xmm6
    1e66:	4c 89 5c 24 b8       	mov    %r11,-0x48(%rsp)
    1e6b:	b9 00 00 fc 00       	mov    $0xfc0000,%ecx
    1e70:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # 1e78 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa88>
    1e77:	00 
    1e78:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
    1e7d:	c5 79 6e e9          	vmovd  %ecx,%xmm13
    1e81:	c5 fd 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm0        # 1e89 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa99>
    1e88:	00 
    1e89:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 1e91 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa1>
    1e90:	00 
    1e91:	c5 fd 7f 74 24 e8    	vmovdqa %ymm6,-0x18(%rsp)
    1e97:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 1e9f <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaaf>
    1e9e:	00 
    1e9f:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
    1ea3:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # 1eab <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xabb>
    1eaa:	00 
    1eab:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
    1eaf:	c5 cd 71 d6 0f       	vpsrlw $0xf,%ymm6,%ymm6
    1eb4:	c4 42 7d 58 ed       	vpbroadcastd %xmm13,%ymm13
    1eb9:	4c 01 da             	add    %r11,%rdx
    1ebc:	0f 1f 40 00          	nopl   0x0(%rax)
    1ec0:	c5 fa 6f 08          	vmovdqu (%rax),%xmm1
    1ec4:	c5 fa 7e 50 10       	vmovq  0x10(%rax),%xmm2
    1ec9:	48 83 c2 60          	add    $0x60,%rdx
    1ecd:	48 83 c0 60          	add    $0x60,%rax
    1ed1:	c5 fd 6f 6c 24 e8    	vmovdqa -0x18(%rsp),%ymm5
    1ed7:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
    1edd:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1ee3:	c5 fd 6f fd          	vmovdqa %ymm5,%ymm7
    1ee7:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    1eec:	c5 f5 db dd          	vpand  %ymm5,%ymm1,%ymm3
    1ef0:	c4 c2 75 00 d1       	vpshufb %ymm9,%ymm1,%ymm2
    1ef5:	c5 95 db c9          	vpand  %ymm1,%ymm13,%ymm1
    1ef9:	c5 ed 71 d2 02       	vpsrlw $0x2,%ymm2,%ymm2
    1efe:	c4 c2 65 04 de       	vpmaddubsw %ymm14,%ymm3,%ymm3
    1f03:	c5 e5 f5 de          	vpmaddwd %ymm6,%ymm3,%ymm3
    1f07:	c5 ed f5 d0          	vpmaddwd %ymm0,%ymm2,%ymm2
    1f0b:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
    1f0f:	c5 fa 7e 58 c8       	vmovq  -0x38(%rax),%xmm3
    1f14:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1f18:	c5 fa 6f 50 b8       	vmovdqu -0x48(%rax),%xmm2
    1f1d:	c4 e3 7d 39 4c 24 08 	vextracti128 $0x1,%ymm1,0x8(%rsp)
    1f24:	01 
    1f25:	c4 e3 61 0f da 0c    	vpalignr $0xc,%xmm2,%xmm3,%xmm3
    1f2b:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
    1f31:	c4 c2 6d 00 d2       	vpshufb %ymm10,%ymm2,%ymm2
    1f36:	c5 ed db e5          	vpand  %ymm5,%ymm2,%ymm4
    1f3a:	c4 c2 6d 00 d9       	vpshufb %ymm9,%ymm2,%ymm3
    1f3f:	c5 95 db d2          	vpand  %ymm2,%ymm13,%ymm2
    1f43:	c5 e5 71 d3 02       	vpsrlw $0x2,%ymm3,%ymm3
    1f48:	c4 c2 5d 04 e6       	vpmaddubsw %ymm14,%ymm4,%ymm4
    1f4d:	c5 dd f5 e6          	vpmaddwd %ymm6,%ymm4,%ymm4
    1f51:	c5 e5 f5 d8          	vpmaddwd %ymm0,%ymm3,%ymm3
    1f55:	c5 e5 eb dc          	vpor   %ymm4,%ymm3,%ymm3
    1f59:	c5 fa 7e 60 e0       	vmovq  -0x20(%rax),%xmm4
    1f5e:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
    1f62:	c5 fa 6f 58 d0       	vmovdqu -0x30(%rax),%xmm3
    1f67:	c4 c3 7d 39 d0 01    	vextracti128 $0x1,%ymm2,%xmm8
    1f6d:	c4 e3 59 0f e3 0c    	vpalignr $0xc,%xmm3,%xmm4,%xmm4
    1f73:	c4 e3 65 38 dc 01    	vinserti128 $0x1,%xmm4,%ymm3,%ymm3
    1f79:	c4 c2 65 00 da       	vpshufb %ymm10,%ymm3,%ymm3
    1f7e:	c4 c2 65 00 e1       	vpshufb %ymm9,%ymm3,%ymm4
    1f83:	c5 e5 db ed          	vpand  %ymm5,%ymm3,%ymm5
    1f87:	c5 95 db db          	vpand  %ymm3,%ymm13,%ymm3
    1f8b:	c5 dd 71 d4 02       	vpsrlw $0x2,%ymm4,%ymm4
    1f90:	c4 c2 55 04 ee       	vpmaddubsw %ymm14,%ymm5,%ymm5
    1f95:	c5 d5 f5 ee          	vpmaddwd %ymm6,%ymm5,%ymm5
    1f99:	c5 dd f5 e0          	vpmaddwd %ymm0,%ymm4,%ymm4
    1f9d:	c5 dd eb e5          	vpor   %ymm5,%ymm4,%ymm4
    1fa1:	c5 fa 7e 68 f8       	vmovq  -0x8(%rax),%xmm5
    1fa6:	c5 dd eb e3          	vpor   %ymm3,%ymm4,%ymm4
    1faa:	c5 fa 6f 58 e8       	vmovdqu -0x18(%rax),%xmm3
    1faf:	c4 c3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm12
    1fb5:	c4 e3 51 0f eb 0c    	vpalignr $0xc,%xmm3,%xmm5,%xmm5
    1fbb:	c4 e3 65 38 dd 01    	vinserti128 $0x1,%xmm5,%ymm3,%ymm3
    1fc1:	c4 c2 65 00 da       	vpshufb %ymm10,%ymm3,%ymm3
    1fc6:	c4 c2 65 00 e9       	vpshufb %ymm9,%ymm3,%ymm5
    1fcb:	c5 e5 db ff          	vpand  %ymm7,%ymm3,%ymm7
    1fcf:	c5 95 db db          	vpand  %ymm3,%ymm13,%ymm3
    1fd3:	c5 d5 71 d5 02       	vpsrlw $0x2,%ymm5,%ymm5
    1fd8:	c4 c2 45 04 fe       	vpmaddubsw %ymm14,%ymm7,%ymm7
    1fdd:	c5 c5 f5 fe          	vpmaddwd %ymm6,%ymm7,%ymm7
    1fe1:	c5 d5 f5 e8          	vpmaddwd %ymm0,%ymm5,%ymm5
    1fe5:	c5 d5 eb ef          	vpor   %ymm7,%ymm5,%ymm5
    1fe9:	c5 e5 eb dd          	vpor   %ymm5,%ymm3,%ymm3
    1fed:	c4 e3 7d 39 df 01    	vextracti128 $0x1,%ymm3,%xmm7
    1ff3:	c5 f9 7e d9          	vmovd  %xmm3,%ecx
    1ff7:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
    1ffd:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    2002:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    2008:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    200d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    2012:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    2017:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    201c:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    2022:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    2028:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    202d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    2032:	c4 e3 79 16 d9 01    	vpextrd $0x1,%xmm3,%ecx
    2038:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    203e:	c4 a1 79 6e 2c be    	vmovd  (%rsi,%r15,4),%xmm5
    2044:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
    204a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    204e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    2053:	c4 a3 51 22 2c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm5,%xmm5
    205a:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
    2061:	c4 41 79 7e e4       	vmovd  %xmm12,%r12d
    2066:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    206b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    2070:	c4 43 79 16 e6 02    	vpextrd $0x2,%xmm12,%r14d
    2076:	c4 43 79 16 e4 01    	vpextrd $0x1,%xmm12,%r12d
    207c:	c5 e1 6c dd          	vpunpcklqdq %xmm5,%xmm3,%xmm3
    2080:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
    2086:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    208b:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    2092:	c4 c3 79 16 e3 02    	vpextrd $0x2,%xmm4,%r11d
    2098:	c4 e3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm5,%xmm5
    209f:	c5 f9 7e e1          	vmovd  %xmm4,%ecx
    20a3:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    20a8:	c4 c3 79 16 e3 03    	vpextrd $0x3,%xmm4,%r11d
    20ae:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    20b3:	c4 e3 79 16 e1 01    	vpextrd $0x1,%xmm4,%ecx
    20b9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    20be:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    20c2:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    20c7:	c5 d1 6c ef          	vpunpcklqdq %xmm7,%xmm5,%xmm5
    20cb:	c4 43 79 16 e6 03    	vpextrd $0x3,%xmm12,%r14d
    20d1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    20d6:	c4 a1 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm4
    20dc:	c4 e3 55 38 eb 01    	vinserti128 $0x1,%xmm3,%ymm5,%ymm5
    20e2:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
    20e8:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    20ed:	c4 c2 55 00 ef       	vpshufb %ymm15,%ymm5,%ymm5
    20f2:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
    20f9:	c4 41 79 7e c4       	vmovd  %xmm8,%r12d
    20fe:	c4 e2 25 36 ed       	vpermd %ymm5,%ymm11,%ymm5
    2103:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
    210a:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    2111:	c4 43 79 16 c6 02    	vpextrd $0x2,%xmm8,%r14d
    2117:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    211c:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    2121:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    2127:	c4 43 79 16 c4 01    	vpextrd $0x1,%xmm8,%r12d
    212d:	c5 d9 6c e3          	vpunpcklqdq %xmm3,%xmm4,%xmm4
    2131:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    2137:	c4 43 79 16 c6 03    	vpextrd $0x3,%xmm8,%r14d
    213d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    2142:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    2147:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    214c:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    2152:	c5 79 6f e5          	vmovdqa %xmm5,%xmm12
    2156:	c4 e3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm3,%xmm3
    215d:	c5 f9 7e d1          	vmovd  %xmm2,%ecx
    2161:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    2166:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    216c:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    2171:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    2177:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    217d:	c4 c3 51 0f ec 08    	vpalignr $0x8,%xmm12,%xmm5,%xmm5
    2183:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    2187:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    218b:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    2190:	c4 e3 65 38 dc 01    	vinserti128 $0x1,%xmm4,%ymm3,%ymm3
    2196:	c4 a1 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm4
    219c:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    21a3:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    21aa:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    21b0:	c4 c2 65 00 df       	vpshufb %ymm15,%ymm3,%ymm3
    21b5:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
    21bc:	44 8b 64 24 08       	mov    0x8(%rsp),%r12d
    21c1:	c4 e2 25 36 db       	vpermd %ymm3,%ymm11,%ymm3
    21c6:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    21cb:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    21d1:	c5 79 6f c3          	vmovdqa %xmm3,%xmm8
    21d5:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    21db:	c5 d9 6c e2          	vpunpcklqdq %xmm2,%xmm4,%xmm4
    21df:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    21e5:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    21ea:	c4 c1 61 6c dc       	vpunpcklqdq %xmm12,%xmm3,%xmm3
    21ef:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    21f4:	c4 e3 65 38 dd 01    	vinserti128 $0x1,%xmm5,%ymm3,%ymm3
    21fa:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    2201:	c5 f9 7e c9          	vmovd  %xmm1,%ecx
    2205:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    220a:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    2210:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    2214:	44 8b 64 24 0c       	mov    0xc(%rsp),%r12d
    2219:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    221d:	44 8b 74 24 10       	mov    0x10(%rsp),%r14d
    2222:	c4 e3 6d 38 d4 01    	vinserti128 $0x1,%xmm4,%ymm2,%ymm2
    2228:	c4 a1 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm4
    222e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    2233:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    2238:	c4 c2 6d 00 d7       	vpshufb %ymm15,%ymm2,%ymm2
    223d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    2242:	44 8b 74 24 14       	mov    0x14(%rsp),%r14d
    2247:	c4 e2 25 36 d2       	vpermd %ymm2,%ymm11,%ymm2
    224c:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
    2253:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    225a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    225f:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    2265:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    226c:	c5 d9 6c e1          	vpunpcklqdq %xmm1,%xmm4,%xmm4
    2270:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    2276:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    227d:	49 8d 49 48          	lea    0x48(%r9),%rcx
    2281:	c5 fe 7f 5a e0       	vmovdqu %ymm3,-0x20(%rdx)
    2286:	49 83 c1 20          	add    $0x20,%r9
    228a:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
    228e:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    2292:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    2298:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
    229e:	c4 e3 69 0f d7 08    	vpalignr $0x8,%xmm7,%xmm2,%xmm2
    22a4:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
    22a9:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
    22af:	c4 e2 25 36 c9       	vpermd %ymm1,%ymm11,%ymm1
    22b4:	c5 fe 7f 52 c0       	vmovdqu %ymm2,-0x40(%rdx)
    22b9:	c5 f9 6f e1          	vmovdqa %xmm1,%xmm4
    22bd:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    22c3:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
    22c7:	c4 e3 5d 38 e1 01    	vinserti128 $0x1,%xmm1,%ymm4,%ymm4
    22cd:	c5 fe 7f 62 a0       	vmovdqu %ymm4,-0x60(%rdx)
    22d2:	49 39 c8             	cmp    %rcx,%r8
    22d5:	0f 83 e5 fb ff ff    	jae    1ec0 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xad0>
    22db:	4c 8b 54 24 c8       	mov    -0x38(%rsp),%r10
    22e0:	4c 8b 5c 24 b8       	mov    -0x48(%rsp),%r11
    22e5:	49 8d 51 08          	lea    0x8(%r9),%rdx
    22e9:	49 39 d0             	cmp    %rdx,%r8
    22ec:	0f 82 95 01 00 00    	jb     2487 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1097>
    22f2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    22f6:	41 b9 03 03 03 00    	mov    $0x30303,%r9d
    22fc:	4c 89 54 24 08       	mov    %r10,0x8(%rsp)
    2301:	c5 ed 76 d2          	vpcmpeqd %ymm2,%ymm2,%ymm2
    2305:	c4 c1 79 6e e1       	vmovd  %r9d,%xmm4
    230a:	4c 89 5c 24 e8       	mov    %r11,-0x18(%rsp)
    230f:	41 b9 00 00 fc 00    	mov    $0xfc0000,%r9d
    2315:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # 231d <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf2d>
    231c:	00 
    231d:	c4 c1 79 6e d9       	vmovd  %r9d,%xmm3
    2322:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # 232a <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3a>
    2329:	00 
    232a:	c5 fd 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm0        # 2332 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf42>
    2331:	00 
    2332:	49 8d 0c 02          	lea    (%r10,%rax,1),%rcx
    2336:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 233e <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf4e>
    233d:	00 
    233e:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 2346 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf56>
    2345:	00 
    2346:	4c 01 d8             	add    %r11,%rax
    2349:	c4 e2 7d 58 e4       	vpbroadcastd %xmm4,%ymm4
    234e:	c5 ed 71 d2 0f       	vpsrlw $0xf,%ymm2,%ymm2
    2353:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
    2358:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    235f:	00 
    2360:	c5 fa 6f 09          	vmovdqu (%rcx),%xmm1
    2364:	c5 fa 7e 69 10       	vmovq  0x10(%rcx),%xmm5
    2369:	48 83 c0 18          	add    $0x18,%rax
    236d:	48 83 c1 18          	add    $0x18,%rcx
    2371:	c4 e3 51 0f e9 0c    	vpalignr $0xc,%xmm1,%xmm5,%xmm5
    2377:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
    237d:	c4 c2 75 00 ca       	vpshufb %ymm10,%ymm1,%ymm1
    2382:	c4 c2 75 00 e9       	vpshufb %ymm9,%ymm1,%ymm5
    2387:	c5 dd db f1          	vpand  %ymm1,%ymm4,%ymm6
    238b:	c5 e5 db c9          	vpand  %ymm1,%ymm3,%ymm1
    238f:	c5 d5 71 d5 02       	vpsrlw $0x2,%ymm5,%ymm5
    2394:	c4 c2 4d 04 f6       	vpmaddubsw %ymm14,%ymm6,%ymm6
    2399:	c5 cd f5 f2          	vpmaddwd %ymm2,%ymm6,%ymm6
    239d:	c5 d5 f5 e8          	vpmaddwd %ymm0,%ymm5,%ymm5
    23a1:	c5 d5 eb ee          	vpor   %ymm6,%ymm5,%ymm5
    23a5:	c5 f5 eb cd          	vpor   %ymm5,%ymm1,%ymm1
    23a9:	c4 e3 7d 39 cd 01    	vextracti128 $0x1,%ymm1,%xmm5
    23af:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
    23b4:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    23ba:	c4 c1 79 7e ec       	vmovd  %xmm5,%r12d
    23bf:	c4 c3 79 16 ee 02    	vpextrd $0x2,%xmm5,%r14d
    23c5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    23ca:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    23cf:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    23d4:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    23d9:	c4 c3 79 16 ec 01    	vpextrd $0x1,%xmm5,%r12d
    23df:	c4 c3 79 16 ee 03    	vpextrd $0x3,%xmm5,%r14d
    23e5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    23ea:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    23ef:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
    23f5:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    23fb:	c4 a1 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm5
    2401:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    2407:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    240c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    2411:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    2418:	c4 a3 51 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm5,%xmm5
    241f:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    2424:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    2428:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    242e:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    2435:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    243c:	49 89 d1             	mov    %rdx,%r9
    243f:	48 83 c2 08          	add    $0x8,%rdx
    2443:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    2447:	c4 e3 75 38 cd 01    	vinserti128 $0x1,%xmm5,%ymm1,%ymm1
    244d:	c4 c2 75 00 cf       	vpshufb %ymm15,%ymm1,%ymm1
    2452:	c5 f9 6f f1          	vmovdqa %xmm1,%xmm6
    2456:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    245c:	c5 d1 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm5
    2461:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
    2466:	c5 d1 eb ee          	vpor   %xmm6,%xmm5,%xmm5
    246a:	c5 f9 d6 48 f8       	vmovq  %xmm1,-0x8(%rax)
    246f:	c5 fa 7f 68 e8       	vmovdqu %xmm5,-0x18(%rax)
    2474:	49 39 d0             	cmp    %rdx,%r8
    2477:	0f 83 e3 fe ff ff    	jae    2360 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf70>
    247d:	4c 8b 54 24 08       	mov    0x8(%rsp),%r10
    2482:	4c 8b 5c 24 e8       	mov    -0x18(%rsp),%r11
    2487:	4d 39 c1             	cmp    %r8,%r9
    248a:	0f 83 a8 03 00 00    	jae    2838 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1448>
    2490:	4b 8d 0c 49          	lea    (%r9,%r9,2),%rcx
    2494:	49 8d 14 0a          	lea    (%r10,%rcx,1),%rdx
    2498:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    249c:	44 0f b6 62 02       	movzbl 0x2(%rdx),%r12d
    24a1:	0f b6 12             	movzbl (%rdx),%edx
    24a4:	41 c1 e4 10          	shl    $0x10,%r12d
    24a8:	c1 e0 08             	shl    $0x8,%eax
    24ab:	44 09 e0             	or     %r12d,%eax
    24ae:	09 d0                	or     %edx,%eax
    24b0:	89 c2                	mov    %eax,%edx
    24b2:	44 8d 24 85 00 00 00 	lea    0x0(,%rax,4),%r12d
    24b9:	00 
    24ba:	c1 e2 04             	shl    $0x4,%edx
    24bd:	41 81 e4 00 f0 03 00 	and    $0x3f000,%r12d
    24c4:	81 e2 c0 0f 00 00    	and    $0xfc0,%edx
    24ca:	44 09 e2             	or     %r12d,%edx
    24cd:	41 89 c4             	mov    %eax,%r12d
    24d0:	41 81 e4 03 00 fc 00 	and    $0xfc0003,%r12d
    24d7:	44 09 e2             	or     %r12d,%edx
    24da:	41 89 c4             	mov    %eax,%r12d
    24dd:	c1 e8 0c             	shr    $0xc,%eax
    24e0:	41 c1 ec 06          	shr    $0x6,%r12d
    24e4:	83 e0 30             	and    $0x30,%eax
    24e7:	41 83 e4 0c          	and    $0xc,%r12d
    24eb:	44 09 e2             	or     %r12d,%edx
    24ee:	09 d0                	or     %edx,%eax
    24f0:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    24f4:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    24f8:	8b 02                	mov    (%rdx),%eax
    24fa:	0f b7 12             	movzwl (%rdx),%edx
    24fd:	c1 e8 10             	shr    $0x10,%eax
    2500:	66 41 89 14 0b       	mov    %dx,(%r11,%rcx,1)
    2505:	41 88 44 0b 02       	mov    %al,0x2(%r11,%rcx,1)
    250a:	49 8d 41 01          	lea    0x1(%r9),%rax
    250e:	4c 39 c0             	cmp    %r8,%rax
    2511:	0f 83 21 03 00 00    	jae    2838 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1448>
    2517:	49 8d 54 0a 03       	lea    0x3(%r10,%rcx,1),%rdx
    251c:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    2520:	44 0f b6 62 02       	movzbl 0x2(%rdx),%r12d
    2525:	0f b6 12             	movzbl (%rdx),%edx
    2528:	41 c1 e4 10          	shl    $0x10,%r12d
    252c:	c1 e0 08             	shl    $0x8,%eax
    252f:	44 09 e0             	or     %r12d,%eax
    2532:	09 d0                	or     %edx,%eax
    2534:	89 c2                	mov    %eax,%edx
    2536:	44 8d 24 85 00 00 00 	lea    0x0(,%rax,4),%r12d
    253d:	00 
    253e:	c1 e2 04             	shl    $0x4,%edx
    2541:	41 81 e4 00 f0 03 00 	and    $0x3f000,%r12d
    2548:	81 e2 c0 0f 00 00    	and    $0xfc0,%edx
    254e:	44 09 e2             	or     %r12d,%edx
    2551:	41 89 c4             	mov    %eax,%r12d
    2554:	41 81 e4 03 00 fc 00 	and    $0xfc0003,%r12d
    255b:	44 09 e2             	or     %r12d,%edx
    255e:	41 89 c4             	mov    %eax,%r12d
    2561:	c1 e8 0c             	shr    $0xc,%eax
    2564:	41 c1 ec 06          	shr    $0x6,%r12d
    2568:	83 e0 30             	and    $0x30,%eax
    256b:	41 83 e4 0c          	and    $0xc,%r12d
    256f:	44 09 e2             	or     %r12d,%edx
    2572:	09 d0                	or     %edx,%eax
    2574:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2578:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    257c:	8b 02                	mov    (%rdx),%eax
    257e:	0f b7 12             	movzwl (%rdx),%edx
    2581:	c1 e8 10             	shr    $0x10,%eax
    2584:	66 41 89 54 0b 03    	mov    %dx,0x3(%r11,%rcx,1)
    258a:	41 88 44 0b 05       	mov    %al,0x5(%r11,%rcx,1)
    258f:	49 8d 41 02          	lea    0x2(%r9),%rax
    2593:	4c 39 c0             	cmp    %r8,%rax
    2596:	0f 83 9c 02 00 00    	jae    2838 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1448>
    259c:	49 8d 54 0a 06       	lea    0x6(%r10,%rcx,1),%rdx
    25a1:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    25a5:	44 0f b6 62 01       	movzbl 0x1(%rdx),%r12d
    25aa:	0f b6 12             	movzbl (%rdx),%edx
    25ad:	41 c1 e4 08          	shl    $0x8,%r12d
    25b1:	c1 e0 10             	shl    $0x10,%eax
    25b4:	44 09 e0             	or     %r12d,%eax
    25b7:	09 d0                	or     %edx,%eax
    25b9:	41 89 c4             	mov    %eax,%r12d
    25bc:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    25c3:	41 c1 e4 04          	shl    $0x4,%r12d
    25c7:	81 e2 00 f0 03 00    	and    $0x3f000,%edx
    25cd:	41 81 e4 c0 0f 00 00 	and    $0xfc0,%r12d
    25d4:	44 09 e2             	or     %r12d,%edx
    25d7:	41 89 c4             	mov    %eax,%r12d
    25da:	41 81 e4 03 00 fc 00 	and    $0xfc0003,%r12d
    25e1:	44 09 e2             	or     %r12d,%edx
    25e4:	41 89 c4             	mov    %eax,%r12d
    25e7:	c1 e8 0c             	shr    $0xc,%eax
    25ea:	41 c1 ec 06          	shr    $0x6,%r12d
    25ee:	83 e0 30             	and    $0x30,%eax
    25f1:	41 83 e4 0c          	and    $0xc,%r12d
    25f5:	44 09 e2             	or     %r12d,%edx
    25f8:	09 d0                	or     %edx,%eax
    25fa:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    25fe:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    2602:	8b 02                	mov    (%rdx),%eax
    2604:	0f b7 12             	movzwl (%rdx),%edx
    2607:	c1 e8 10             	shr    $0x10,%eax
    260a:	66 41 89 54 0b 06    	mov    %dx,0x6(%r11,%rcx,1)
    2610:	41 88 44 0b 08       	mov    %al,0x8(%r11,%rcx,1)
    2615:	49 8d 41 03          	lea    0x3(%r9),%rax
    2619:	4c 39 c0             	cmp    %r8,%rax
    261c:	0f 83 16 02 00 00    	jae    2838 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1448>
    2622:	49 8d 54 0a 09       	lea    0x9(%r10,%rcx,1),%rdx
    2627:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    262b:	44 0f b6 62 01       	movzbl 0x1(%rdx),%r12d
    2630:	0f b6 12             	movzbl (%rdx),%edx
    2633:	41 c1 e4 08          	shl    $0x8,%r12d
    2637:	c1 e0 10             	shl    $0x10,%eax
    263a:	44 09 e0             	or     %r12d,%eax
    263d:	09 d0                	or     %edx,%eax
    263f:	41 89 c4             	mov    %eax,%r12d
    2642:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    2649:	41 c1 e4 04          	shl    $0x4,%r12d
    264d:	81 e2 00 f0 03 00    	and    $0x3f000,%edx
    2653:	41 81 e4 c0 0f 00 00 	and    $0xfc0,%r12d
    265a:	44 09 e2             	or     %r12d,%edx
    265d:	41 89 c4             	mov    %eax,%r12d
    2660:	41 81 e4 03 00 fc 00 	and    $0xfc0003,%r12d
    2667:	44 09 e2             	or     %r12d,%edx
    266a:	41 89 c4             	mov    %eax,%r12d
    266d:	c1 e8 0c             	shr    $0xc,%eax
    2670:	41 c1 ec 06          	shr    $0x6,%r12d
    2674:	83 e0 30             	and    $0x30,%eax
    2677:	41 83 e4 0c          	and    $0xc,%r12d
    267b:	44 09 e2             	or     %r12d,%edx
    267e:	09 d0                	or     %edx,%eax
    2680:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2684:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    2688:	8b 02                	mov    (%rdx),%eax
    268a:	0f b7 12             	movzwl (%rdx),%edx
    268d:	c1 e8 10             	shr    $0x10,%eax
    2690:	66 41 89 54 0b 09    	mov    %dx,0x9(%r11,%rcx,1)
    2696:	41 88 44 0b 0b       	mov    %al,0xb(%r11,%rcx,1)
    269b:	49 8d 41 04          	lea    0x4(%r9),%rax
    269f:	4c 39 c0             	cmp    %r8,%rax
    26a2:	0f 83 90 01 00 00    	jae    2838 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1448>
    26a8:	49 8d 54 0a 0c       	lea    0xc(%r10,%rcx,1),%rdx
    26ad:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    26b1:	44 0f b6 62 01       	movzbl 0x1(%rdx),%r12d
    26b6:	0f b6 12             	movzbl (%rdx),%edx
    26b9:	41 c1 e4 08          	shl    $0x8,%r12d
    26bd:	c1 e0 10             	shl    $0x10,%eax
    26c0:	44 09 e0             	or     %r12d,%eax
    26c3:	09 d0                	or     %edx,%eax
    26c5:	41 89 c4             	mov    %eax,%r12d
    26c8:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    26cf:	41 c1 e4 04          	shl    $0x4,%r12d
    26d3:	81 e2 00 f0 03 00    	and    $0x3f000,%edx
    26d9:	41 81 e4 c0 0f 00 00 	and    $0xfc0,%r12d
    26e0:	44 09 e2             	or     %r12d,%edx
    26e3:	41 89 c4             	mov    %eax,%r12d
    26e6:	41 81 e4 03 00 fc 00 	and    $0xfc0003,%r12d
    26ed:	44 09 e2             	or     %r12d,%edx
    26f0:	41 89 c4             	mov    %eax,%r12d
    26f3:	c1 e8 0c             	shr    $0xc,%eax
    26f6:	41 c1 ec 06          	shr    $0x6,%r12d
    26fa:	83 e0 30             	and    $0x30,%eax
    26fd:	41 83 e4 0c          	and    $0xc,%r12d
    2701:	44 09 e2             	or     %r12d,%edx
    2704:	09 d0                	or     %edx,%eax
    2706:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    270a:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    270e:	8b 02                	mov    (%rdx),%eax
    2710:	0f b7 12             	movzwl (%rdx),%edx
    2713:	c1 e8 10             	shr    $0x10,%eax
    2716:	66 41 89 54 0b 0c    	mov    %dx,0xc(%r11,%rcx,1)
    271c:	41 88 44 0b 0e       	mov    %al,0xe(%r11,%rcx,1)
    2721:	49 8d 41 05          	lea    0x5(%r9),%rax
    2725:	4c 39 c0             	cmp    %r8,%rax
    2728:	0f 83 0a 01 00 00    	jae    2838 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1448>
    272e:	49 8d 54 0a 0f       	lea    0xf(%r10,%rcx,1),%rdx
    2733:	49 83 c1 06          	add    $0x6,%r9
    2737:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    273b:	44 0f b6 62 01       	movzbl 0x1(%rdx),%r12d
    2740:	0f b6 12             	movzbl (%rdx),%edx
    2743:	41 c1 e4 08          	shl    $0x8,%r12d
    2747:	c1 e0 10             	shl    $0x10,%eax
    274a:	44 09 e0             	or     %r12d,%eax
    274d:	09 d0                	or     %edx,%eax
    274f:	41 89 c4             	mov    %eax,%r12d
    2752:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    2759:	41 c1 e4 04          	shl    $0x4,%r12d
    275d:	81 e2 00 f0 03 00    	and    $0x3f000,%edx
    2763:	41 81 e4 c0 0f 00 00 	and    $0xfc0,%r12d
    276a:	44 09 e2             	or     %r12d,%edx
    276d:	41 89 c4             	mov    %eax,%r12d
    2770:	41 81 e4 03 00 fc 00 	and    $0xfc0003,%r12d
    2777:	44 09 e2             	or     %r12d,%edx
    277a:	41 89 c4             	mov    %eax,%r12d
    277d:	c1 e8 0c             	shr    $0xc,%eax
    2780:	41 c1 ec 06          	shr    $0x6,%r12d
    2784:	83 e0 30             	and    $0x30,%eax
    2787:	41 83 e4 0c          	and    $0xc,%r12d
    278b:	44 09 e2             	or     %r12d,%edx
    278e:	09 d0                	or     %edx,%eax
    2790:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2794:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    2798:	8b 02                	mov    (%rdx),%eax
    279a:	0f b7 12             	movzwl (%rdx),%edx
    279d:	c1 e8 10             	shr    $0x10,%eax
    27a0:	66 41 89 54 0b 0f    	mov    %dx,0xf(%r11,%rcx,1)
    27a6:	41 88 44 0b 11       	mov    %al,0x11(%r11,%rcx,1)
    27ab:	4d 39 c1             	cmp    %r8,%r9
    27ae:	0f 83 84 00 00 00    	jae    2838 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1448>
    27b4:	49 8d 54 0a 12       	lea    0x12(%r10,%rcx,1),%rdx
    27b9:	4d 8d 44 0b 12       	lea    0x12(%r11,%rcx,1),%r8
    27be:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    27c2:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    27c6:	0f b6 12             	movzbl (%rdx),%edx
    27c9:	c1 e1 10             	shl    $0x10,%ecx
    27cc:	c1 e0 08             	shl    $0x8,%eax
    27cf:	09 c8                	or     %ecx,%eax
    27d1:	09 d0                	or     %edx,%eax
    27d3:	89 c2                	mov    %eax,%edx
    27d5:	8d 0c 85 00 00 00 00 	lea    0x0(,%rax,4),%ecx
    27dc:	c1 e2 04             	shl    $0x4,%edx
    27df:	81 e1 00 f0 03 00    	and    $0x3f000,%ecx
    27e5:	81 e2 c0 0f 00 00    	and    $0xfc0,%edx
    27eb:	09 ca                	or     %ecx,%edx
    27ed:	89 c1                	mov    %eax,%ecx
    27ef:	81 e1 03 00 fc 00    	and    $0xfc0003,%ecx
    27f5:	09 ca                	or     %ecx,%edx
    27f7:	89 c1                	mov    %eax,%ecx
    27f9:	c1 e8 0c             	shr    $0xc,%eax
    27fc:	c1 e9 06             	shr    $0x6,%ecx
    27ff:	83 e0 30             	and    $0x30,%eax
    2802:	83 e1 0c             	and    $0xc,%ecx
    2805:	09 ca                	or     %ecx,%edx
    2807:	09 d0                	or     %edx,%eax
    2809:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    280d:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    2811:	8b 02                	mov    (%rdx),%eax
    2813:	0f b7 12             	movzwl (%rdx),%edx
    2816:	c1 e8 10             	shr    $0x10,%eax
    2819:	66 41 89 10          	mov    %dx,(%r8)
    281d:	41 88 40 02          	mov    %al,0x2(%r8)
    2821:	c5 f8 77             	vzeroupper
    2824:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2828:	5b                   	pop    %rbx
    2829:	41 5c                	pop    %r12
    282b:	41 5d                	pop    %r13
    282d:	41 5e                	pop    %r14
    282f:	41 5f                	pop    %r15
    2831:	5d                   	pop    %rbp
    2832:	c3                   	ret
    2833:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    2838:	c5 f8 77             	vzeroupper
    283b:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    283f:	5b                   	pop    %rbx
    2840:	41 5c                	pop    %r12
    2842:	41 5d                	pop    %r13
    2844:	41 5e                	pop    %r14
    2846:	41 5f                	pop    %r15
    2848:	5d                   	pop    %rbp
    2849:	c3                   	ret
    284a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    2850:	4d 89 c1             	mov    %r8,%r9
    2853:	e9 8d fa ff ff       	jmp    22e5 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xef5>
    2858:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    285f:	00 
    2860:	c3                   	ret
    2861:	48 8d 41 28          	lea    0x28(%rcx),%rax
    2865:	49 89 c9             	mov    %rcx,%r9
    2868:	e9 d6 f5 ff ff       	jmp    1e43 <jshc_channel::avx2_chain_tilemadd_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa53>
