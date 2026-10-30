
artifacts/skylake-chroma-delta-linux-build-v1/CMakeFiles/jshc_skylake_chroma_delta.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 63 10 00 00    	je     1070 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1070>
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
      a4:	0f 84 b6 0f 00 00    	je     1060 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1060>
      aa:	41 f6 c1 3f          	test   $0x3f,%r9b
      ae:	75 98                	jne    48 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      b0:	48 8d 42 48          	lea    0x48(%rdx),%rax
      b4:	48 39 c1             	cmp    %rax,%rcx
      b7:	0f 82 b4 0f 00 00    	jb     1071 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1071>
      bd:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
      c1:	c4 41 25 76 db       	vpcmpeqd %ymm11,%ymm11,%ymm11
      c6:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # ce <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xce>
      cd:	00 
      ce:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # d6 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd6>
      d5:	00 
      d6:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # de <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xde>
      dd:	00 
      de:	4c 01 c0             	add    %r8,%rax
      e1:	c4 c1 25 72 d3 08    	vpsrld $0x8,%ymm11,%ymm11
      e7:	eb 0a                	jmp    f3 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf3>
      e9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
      f0:	4c 89 ca             	mov    %r9,%rdx
      f3:	4c 8d 8a 96 01 00 00 	lea    0x196(%rdx),%r9
      fa:	4c 39 c9             	cmp    %r9,%rcx
      fd:	72 1c                	jb     11b <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x11b>
      ff:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
     106:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
     10d:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     114:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     11b:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     11f:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     124:	48 05 c0 00 00 00    	add    $0xc0,%rax
     12a:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     130:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     136:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     13b:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     140:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     144:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     149:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     14f:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     154:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     15a:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     15f:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     165:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     16a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     16f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     174:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     179:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     17f:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     185:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     18a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     18f:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     195:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     19b:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     1a1:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     1a7:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     1ac:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     1b1:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     1b8:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     1bf:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
     1c5:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     1c9:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     1ce:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
     1d5:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1dc:	c5 29 6c d1          	vpunpcklqdq %xmm1,%xmm10,%xmm10
     1e0:	c5 fa 7e 88 68 ff ff 	vmovq  -0x98(%rax),%xmm1
     1e7:	ff 
     1e8:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
     1ee:	c5 fa 6f 80 58 ff ff 	vmovdqu -0xa8(%rax),%xmm0
     1f5:	ff 
     1f6:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
     1fb:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     201:	c4 42 4d 36 d2       	vpermd %ymm10,%ymm6,%ymm10
     206:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     20c:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     211:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     216:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     21a:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     21f:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     225:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     22a:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     230:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     235:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     23b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     240:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     245:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     24a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     24f:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     255:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     25b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     260:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     265:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     26b:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     271:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     277:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     27d:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     282:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     287:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     28e:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     295:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     299:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     29e:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     2a4:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     2ab:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
     2b2:	c5 e1 6c d9          	vpunpcklqdq %xmm1,%xmm3,%xmm3
     2b6:	c5 fa 7e 48 80       	vmovq  -0x80(%rax),%xmm1
     2bb:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
     2c1:	c5 fa 6f 80 70 ff ff 	vmovdqu -0x90(%rax),%xmm0
     2c8:	ff 
     2c9:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
     2ce:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     2d4:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
     2d9:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     2df:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     2e4:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     2e9:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     2ed:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     2f2:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     2f8:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     2fd:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     303:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     308:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     30e:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     313:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     318:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     31d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     322:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     328:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     32e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     333:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     338:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     33e:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     344:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     34a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     350:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     355:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     35a:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     361:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     368:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     36e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     372:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     377:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     37e:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     385:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     389:	c5 fa 7e 48 98       	vmovq  -0x68(%rax),%xmm1
     38e:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     394:	c5 fa 6f 40 88       	vmovdqu -0x78(%rax),%xmm0
     399:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     39e:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     3a4:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
     3a9:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     3af:	c5 79 6f f2          	vmovdqa %xmm2,%xmm14
     3b3:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     3b9:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     3be:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     3c3:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     3c7:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     3cc:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     3d2:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     3d7:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     3dd:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     3e2:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     3e8:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     3ed:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     3f2:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     3f7:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     3fc:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     402:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     408:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     40e:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     414:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     419:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     41e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     423:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     428:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     42e:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     434:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     43a:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     441:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     448:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
     44f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     453:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     458:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     45f:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     463:	c5 fa 7e 48 b0       	vmovq  -0x50(%rax),%xmm1
     468:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     46e:	c5 fa 6f 40 a0       	vmovdqu -0x60(%rax),%xmm0
     473:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
     478:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     47e:	c4 42 4d 36 c9       	vpermd %ymm9,%ymm6,%ymm9
     483:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     489:	c4 41 79 6f f9       	vmovdqa %xmm9,%xmm15
     48e:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     494:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     499:	c4 43 31 0f cf 08    	vpalignr $0x8,%xmm15,%xmm9,%xmm9
     49f:	c4 c1 69 6c d7       	vpunpcklqdq %xmm15,%xmm2,%xmm2
     4a4:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     4a9:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
     4af:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     4b3:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     4b8:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     4be:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     4c3:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     4c9:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     4ce:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     4d4:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     4d9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     4de:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     4e3:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     4e8:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     4ee:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     4f4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     4f9:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     4fe:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     504:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     50a:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     510:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     516:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     51b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     520:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     527:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     52e:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     534:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     538:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     53d:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
     544:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     54b:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     54f:	c5 fa 7e 48 c8       	vmovq  -0x38(%rax),%xmm1
     554:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     55a:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
     55f:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
     564:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     56a:	c4 42 4d 36 c0       	vpermd %ymm8,%ymm6,%ymm8
     56f:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     575:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     57a:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
     57f:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
     583:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     588:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     58e:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     593:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     599:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     59e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5a3:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     5a8:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     5ae:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     5b4:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     5ba:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     5bf:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     5c4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     5c9:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     5ce:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     5d4:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     5da:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5df:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5e4:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     5ea:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     5f0:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     5f5:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     5fc:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     603:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     60a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     60e:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     614:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     61b:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
     61f:	c5 fa 7e 78 e0       	vmovq  -0x20(%rax),%xmm7
     624:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     62a:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
     62f:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     634:	c4 e3 41 0f f8 0c    	vpalignr $0xc,%xmm0,%xmm7,%xmm7
     63a:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
     63f:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     645:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     64a:	c5 c5 72 f0 08       	vpslld $0x8,%ymm0,%ymm7
     64f:	c5 fd f8 c7          	vpsubb %ymm7,%ymm0,%ymm0
     653:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     658:	c4 e3 7d 39 c7 01    	vextracti128 $0x1,%ymm0,%xmm7
     65e:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     663:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     669:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     66e:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     674:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     679:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     67e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     683:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     688:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     68e:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     694:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     699:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     69e:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     6a4:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     6aa:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     6b0:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     6b6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     6bb:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     6c0:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     6c7:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     6ce:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     6d3:	c5 c1 6c f8          	vpunpcklqdq %xmm0,%xmm7,%xmm7
     6d7:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     6dd:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     6e4:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     6eb:	c4 c1 79 6c c4       	vpunpcklqdq %xmm12,%xmm0,%xmm0
     6f0:	c5 7a 7e 60 f8       	vmovq  -0x8(%rax),%xmm12
     6f5:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     6fb:	c5 fa 6f 78 e8       	vmovdqu -0x18(%rax),%xmm7
     700:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     705:	c4 63 19 0f e7 0c    	vpalignr $0xc,%xmm7,%xmm12,%xmm12
     70b:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
     710:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
     716:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     71a:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     720:	c4 e2 45 00 fd       	vpshufb %ymm5,%ymm7,%ymm7
     725:	c5 9d 72 f7 08       	vpslld $0x8,%ymm7,%ymm12
     72a:	c4 c1 45 f8 fc       	vpsubb %ymm12,%ymm7,%ymm7
     72f:	c4 c1 45 db fb       	vpand  %ymm11,%ymm7,%ymm7
     734:	c4 c3 7d 39 fc 01    	vextracti128 $0x1,%ymm7,%xmm12
     73a:	c4 c1 79 7e f9       	vmovd  %xmm7,%r9d
     73f:	c4 c3 79 16 fb 02    	vpextrd $0x2,%xmm7,%r11d
     745:	c4 41 79 7e e4       	vmovd  %xmm12,%r12d
     74a:	c4 43 79 16 e6 02    	vpextrd $0x2,%xmm12,%r14d
     750:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     755:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     75a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     75f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     764:	c4 43 79 16 e4 01    	vpextrd $0x1,%xmm12,%r12d
     76a:	c4 43 79 16 e6 03    	vpextrd $0x3,%xmm12,%r14d
     770:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     775:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     77a:	c4 c3 79 16 f9 01    	vpextrd $0x1,%xmm7,%r9d
     780:	c4 c3 79 16 fb 03    	vpextrd $0x3,%xmm7,%r11d
     786:	c4 21 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm12
     78c:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
     792:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     797:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     79c:	c4 a3 41 22 3c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm7,%xmm7
     7a3:	c4 23 19 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm12,%xmm12
     7aa:	c5 79 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm13
     7af:	c5 19 6c e7          	vpunpcklqdq %xmm7,%xmm12,%xmm12
     7b3:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     7b9:	4c 8d 92 88 00 00 00 	lea    0x88(%rdx),%r10
     7c0:	c4 23 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm13,%xmm13
     7c7:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
     7ce:	c5 fd e7 50 80       	vmovntdq %ymm2,-0x80(%rax)
     7d3:	c5 79 7f c2          	vmovdqa %xmm8,%xmm2
     7d7:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     7dd:	4c 8d 4a 40          	lea    0x40(%rdx),%r9
     7e1:	c4 c1 41 6c fd       	vpunpcklqdq %xmm13,%xmm7,%xmm7
     7e6:	c5 79 6f eb          	vmovdqa %xmm3,%xmm13
     7ea:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     7f0:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
     7f6:	c4 c3 61 0f dd 08    	vpalignr $0x8,%xmm13,%xmm3,%xmm3
     7fc:	c4 41 79 6f e2       	vmovdqa %xmm10,%xmm12
     801:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     806:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
     80c:	c4 c3 65 38 de 01    	vinserti128 $0x1,%xmm14,%ymm3,%ymm3
     812:	c4 e2 4d 36 ff       	vpermd %ymm7,%ymm6,%ymm7
     817:	c4 41 29 6c d5       	vpunpcklqdq %xmm13,%xmm10,%xmm10
     81c:	c5 fd e7 98 60 ff ff 	vmovntdq %ymm3,-0xa0(%rax)
     823:	ff 
     824:	c4 43 1d 38 e2 01    	vinserti128 $0x1,%xmm10,%ymm12,%ymm12
     82a:	c5 f9 6f df          	vmovdqa %xmm7,%xmm3
     82e:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
     832:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     838:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     83e:	c4 41 39 6c c2       	vpunpcklqdq %xmm10,%xmm8,%xmm8
     843:	c5 7d e7 a0 40 ff ff 	vmovntdq %ymm12,-0xc0(%rax)
     84a:	ff 
     84b:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
     851:	c4 e3 41 0f fb 08    	vpalignr $0x8,%xmm3,%xmm7,%xmm7
     857:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
     85b:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
     861:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     867:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     86d:	c5 fd e7 50 a0       	vmovntdq %ymm2,-0x60(%rax)
     872:	c5 fd e7 48 c0       	vmovntdq %ymm1,-0x40(%rax)
     877:	c5 fd e7 40 e0       	vmovntdq %ymm0,-0x20(%rax)
     87c:	4c 39 d1             	cmp    %r10,%rcx
     87f:	0f 83 6b f8 ff ff    	jae    f0 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf0>
     885:	0f ae f8             	sfence
     888:	48 8d 42 68          	lea    0x68(%rdx),%rax
     88c:	48 39 c1             	cmp    %rax,%rcx
     88f:	0f 82 db 03 00 00    	jb     c70 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc70>
     895:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     899:	c4 41 3d 76 c0       	vpcmpeqd %ymm8,%ymm8,%ymm8
     89e:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 8a6 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8a6>
     8a5:	00 
     8a6:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 8ae <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8ae>
     8ad:	00 
     8ae:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # 8b6 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8b6>
     8b5:	00 
     8b6:	4c 01 c0             	add    %r8,%rax
     8b9:	c4 c1 3d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm8
     8bf:	90                   	nop
     8c0:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     8c4:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
     8c9:	48 83 c0 60          	add    $0x60,%rax
     8cd:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     8d2:	c5 fa 7e 58 e0       	vmovq  -0x20(%rax),%xmm3
     8d7:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
     8dd:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
     8e2:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     8e8:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
     8ed:	c5 fd 72 f2 08       	vpslld $0x8,%ymm2,%ymm0
     8f2:	c5 ed f8 d0          	vpsubb %ymm0,%ymm2,%ymm2
     8f6:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
     8fb:	c4 c1 6d db d0       	vpand  %ymm8,%ymm2,%ymm2
     900:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
     906:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
     90c:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     912:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
     917:	c5 fd 72 f1 08       	vpslld $0x8,%ymm1,%ymm0
     91c:	c5 f5 f8 c8          	vpsubb %ymm0,%ymm1,%ymm1
     920:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
     925:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
     92a:	c4 e3 61 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm3,%xmm3
     930:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
     936:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
     93c:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     941:	c5 e5 72 f0 08       	vpslld $0x8,%ymm0,%ymm3
     946:	c5 fd f8 c3          	vpsubb %ymm3,%ymm0,%ymm0
     94a:	c5 fa 6f 58 e8       	vmovdqu -0x18(%rax),%xmm3
     94f:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
     954:	c4 63 21 0f db 0c    	vpalignr $0xc,%xmm3,%xmm11,%xmm11
     95a:	c4 c3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm10
     960:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
     966:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
     96b:	c5 a5 72 f3 08       	vpslld $0x8,%ymm3,%ymm11
     970:	c4 c1 65 f8 db       	vpsubb %ymm11,%ymm3,%ymm3
     975:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     97a:	c4 c3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm11
     980:	c5 f9 7e da          	vmovd  %xmm3,%edx
     984:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     98a:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
     98f:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
     995:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     99a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     99f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     9a4:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9a9:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
     9af:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
     9b5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     9ba:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     9bf:	c4 e3 79 16 da 01    	vpextrd $0x1,%xmm3,%edx
     9c5:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
     9cb:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
     9d1:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     9d7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     9db:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     9e0:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     9e7:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
     9ee:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     9f4:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     9f9:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     9fe:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a03:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     a09:	c5 21 6c db          	vpunpcklqdq %xmm3,%xmm11,%xmm11
     a0d:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     a13:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a18:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     a1e:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     a25:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     a2b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a30:	c4 e3 61 22 1c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm3,%xmm3
     a37:	c5 f9 7e c2          	vmovd  %xmm0,%edx
     a3b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     a40:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     a46:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     a4b:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     a51:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a56:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     a5a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a5f:	c4 c1 61 6c dc       	vpunpcklqdq %xmm12,%xmm3,%xmm3
     a64:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     a6a:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     a70:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
     a76:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     a7b:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
     a80:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     a87:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     a8e:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     a94:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     a99:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a9e:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     aa5:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     aab:	c5 29 6c d0          	vpunpcklqdq %xmm0,%xmm10,%xmm10
     aaf:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     ab5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     aba:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     ac0:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     ac6:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     acb:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     ad0:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     ad6:	c4 e3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm0,%xmm0
     add:	c5 f9 7e ca          	vmovd  %xmm1,%edx
     ae1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     ae6:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
     aeb:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     af0:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     af6:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     afc:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     b02:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
     b07:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     b0b:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     b12:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b17:	c4 c3 7d 38 c2 01    	vinserti128 $0x1,%xmm10,%ymm0,%ymm0
     b1d:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     b22:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     b29:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     b2e:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     b34:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     b39:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     b3e:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     b43:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     b49:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     b4f:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     b53:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     b59:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     b60:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     b66:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     b6b:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     b71:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     b76:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
     b7b:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
     b82:	c5 f9 7e d2          	vmovd  %xmm2,%edx
     b86:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b8b:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     b90:	c4 e3 79 16 d2 01    	vpextrd $0x1,%xmm2,%edx
     b96:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b9b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     b9f:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     ba5:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     baa:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
     bae:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     bb4:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     bba:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     bbf:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     bc5:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     bcc:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     bd1:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     bd8:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     bdf:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
     be4:	c5 79 6f d9          	vmovdqa %xmm1,%xmm11
     be8:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     bee:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     bf2:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     bf8:	c4 c3 71 0f cb 08    	vpalignr $0x8,%xmm11,%xmm1,%xmm1
     bfe:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
     c04:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
     c0b:	49 8d 51 48          	lea    0x48(%r9),%rdx
     c0f:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     c14:	49 83 c1 20          	add    $0x20,%r9
     c18:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     c1d:	c5 79 6f cb          	vmovdqa %xmm3,%xmm9
     c21:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     c27:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
     c2d:	c4 c3 61 0f d9 08    	vpalignr $0x8,%xmm9,%xmm3,%xmm3
     c33:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
     c38:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     c3d:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
     c43:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
     c48:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     c4d:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     c51:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     c57:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     c5c:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
     c62:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     c67:	48 39 d1             	cmp    %rdx,%rcx
     c6a:	0f 83 50 fc ff ff    	jae    8c0 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8c0>
     c70:	49 8d 51 08          	lea    0x8(%r9),%rdx
     c74:	48 39 d1             	cmp    %rdx,%rcx
     c77:	0f 82 22 01 00 00    	jb     d9f <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd9f>
     c7d:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     c81:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
     c85:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # c8d <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc8d>
     c8c:	00 
     c8d:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # c95 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc95>
     c94:	00 
     c95:	4c 01 c0             	add    %r8,%rax
     c98:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
     c9d:	0f 1f 00             	nopl   (%rax)
     ca0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     ca4:	c5 fa 7e 50 10       	vmovq  0x10(%rax),%xmm2
     ca9:	48 83 c0 18          	add    $0x18,%rax
     cad:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
     cb3:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     cb9:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     cbe:	c5 ed 72 f0 08       	vpslld $0x8,%ymm0,%ymm2
     cc3:	c5 fd f8 c2          	vpsubb %ymm2,%ymm0,%ymm0
     cc7:	c5 fd db c1          	vpand  %ymm1,%ymm0,%ymm0
     ccb:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
     cd1:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     cd6:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     cdc:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     ce1:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     ce7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     cec:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     cf1:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     cf6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     cfb:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     d01:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     d07:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     d0c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     d11:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     d17:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     d1d:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     d23:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     d29:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     d2e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     d33:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     d3a:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     d41:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
     d46:	c5 e9 6c d0          	vpunpcklqdq %xmm0,%xmm2,%xmm2
     d4a:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     d50:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
     d57:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     d5e:	49 89 d1             	mov    %rdx,%r9
     d61:	48 83 c2 08          	add    $0x8,%rdx
     d65:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
     d69:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     d6f:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     d74:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
     d78:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     d7e:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
     d83:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     d88:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
     d8c:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     d91:	c5 fa 7f 50 e8       	vmovdqu %xmm2,-0x18(%rax)
     d96:	48 39 d1             	cmp    %rdx,%rcx
     d99:	0f 83 01 ff ff ff    	jae    ca0 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xca0>
     d9f:	49 39 c9             	cmp    %rcx,%r9
     da2:	0f 83 a8 02 00 00    	jae    1050 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1050>
     da8:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
     dac:	4d 8d 14 10          	lea    (%r8,%rdx,1),%r10
     db0:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     db5:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     dba:	c1 e0 08             	shl    $0x8,%eax
     dbd:	41 c1 e3 10          	shl    $0x10,%r11d
     dc1:	44 09 d8             	or     %r11d,%eax
     dc4:	45 0f b6 1a          	movzbl (%r10),%r11d
     dc8:	0f b6 dc             	movzbl %ah,%ebx
     dcb:	c1 e8 10             	shr    $0x10,%eax
     dce:	29 d8                	sub    %ebx,%eax
     dd0:	44 29 db             	sub    %r11d,%ebx
     dd3:	c1 e0 10             	shl    $0x10,%eax
     dd6:	c1 e3 08             	shl    $0x8,%ebx
     dd9:	25 00 00 ff 00       	and    $0xff0000,%eax
     dde:	0f b7 db             	movzwl %bx,%ebx
     de1:	09 d8                	or     %ebx,%eax
     de3:	44 09 d8             	or     %r11d,%eax
     de6:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     dea:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     dee:	41 8b 03             	mov    (%r11),%eax
     df1:	45 0f b7 1b          	movzwl (%r11),%r11d
     df5:	c1 e8 10             	shr    $0x10,%eax
     df8:	66 45 89 1a          	mov    %r11w,(%r10)
     dfc:	41 88 42 02          	mov    %al,0x2(%r10)
     e00:	49 8d 41 01          	lea    0x1(%r9),%rax
     e04:	48 39 c8             	cmp    %rcx,%rax
     e07:	0f 83 43 02 00 00    	jae    1050 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1050>
     e0d:	4d 8d 54 10 03       	lea    0x3(%r8,%rdx,1),%r10
     e12:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     e17:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e1c:	c1 e0 08             	shl    $0x8,%eax
     e1f:	41 c1 e3 10          	shl    $0x10,%r11d
     e23:	44 09 d8             	or     %r11d,%eax
     e26:	45 0f b6 1a          	movzbl (%r10),%r11d
     e2a:	0f b6 dc             	movzbl %ah,%ebx
     e2d:	c1 e8 10             	shr    $0x10,%eax
     e30:	29 d8                	sub    %ebx,%eax
     e32:	44 29 db             	sub    %r11d,%ebx
     e35:	c1 e0 10             	shl    $0x10,%eax
     e38:	c1 e3 08             	shl    $0x8,%ebx
     e3b:	25 00 00 ff 00       	and    $0xff0000,%eax
     e40:	0f b7 db             	movzwl %bx,%ebx
     e43:	09 d8                	or     %ebx,%eax
     e45:	44 09 d8             	or     %r11d,%eax
     e48:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e4c:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e50:	41 8b 03             	mov    (%r11),%eax
     e53:	45 0f b7 1b          	movzwl (%r11),%r11d
     e57:	c1 e8 10             	shr    $0x10,%eax
     e5a:	66 45 89 1a          	mov    %r11w,(%r10)
     e5e:	41 88 42 02          	mov    %al,0x2(%r10)
     e62:	49 8d 41 02          	lea    0x2(%r9),%rax
     e66:	48 39 c8             	cmp    %rcx,%rax
     e69:	0f 83 e1 01 00 00    	jae    1050 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1050>
     e6f:	4d 8d 54 10 06       	lea    0x6(%r8,%rdx,1),%r10
     e74:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     e79:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e7e:	c1 e0 08             	shl    $0x8,%eax
     e81:	41 c1 e3 10          	shl    $0x10,%r11d
     e85:	44 09 d8             	or     %r11d,%eax
     e88:	45 0f b6 1a          	movzbl (%r10),%r11d
     e8c:	0f b6 dc             	movzbl %ah,%ebx
     e8f:	c1 e8 10             	shr    $0x10,%eax
     e92:	29 d8                	sub    %ebx,%eax
     e94:	44 29 db             	sub    %r11d,%ebx
     e97:	c1 e0 10             	shl    $0x10,%eax
     e9a:	c1 e3 08             	shl    $0x8,%ebx
     e9d:	25 00 00 ff 00       	and    $0xff0000,%eax
     ea2:	0f b7 db             	movzwl %bx,%ebx
     ea5:	09 d8                	or     %ebx,%eax
     ea7:	44 09 d8             	or     %r11d,%eax
     eaa:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     eae:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     eb2:	41 8b 03             	mov    (%r11),%eax
     eb5:	45 0f b7 1b          	movzwl (%r11),%r11d
     eb9:	c1 e8 10             	shr    $0x10,%eax
     ebc:	66 45 89 1a          	mov    %r11w,(%r10)
     ec0:	41 88 42 02          	mov    %al,0x2(%r10)
     ec4:	49 8d 41 03          	lea    0x3(%r9),%rax
     ec8:	48 39 c8             	cmp    %rcx,%rax
     ecb:	0f 83 7f 01 00 00    	jae    1050 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1050>
     ed1:	4d 8d 54 10 09       	lea    0x9(%r8,%rdx,1),%r10
     ed6:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     edb:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     ee0:	c1 e0 10             	shl    $0x10,%eax
     ee3:	41 c1 e3 08          	shl    $0x8,%r11d
     ee7:	44 09 d8             	or     %r11d,%eax
     eea:	45 0f b6 1a          	movzbl (%r10),%r11d
     eee:	0f b6 dc             	movzbl %ah,%ebx
     ef1:	c1 e8 10             	shr    $0x10,%eax
     ef4:	29 d8                	sub    %ebx,%eax
     ef6:	44 29 db             	sub    %r11d,%ebx
     ef9:	c1 e0 10             	shl    $0x10,%eax
     efc:	c1 e3 08             	shl    $0x8,%ebx
     eff:	25 00 00 ff 00       	and    $0xff0000,%eax
     f04:	0f b7 db             	movzwl %bx,%ebx
     f07:	09 d8                	or     %ebx,%eax
     f09:	44 09 d8             	or     %r11d,%eax
     f0c:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f10:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f14:	41 8b 03             	mov    (%r11),%eax
     f17:	45 0f b7 1b          	movzwl (%r11),%r11d
     f1b:	c1 e8 10             	shr    $0x10,%eax
     f1e:	66 45 89 1a          	mov    %r11w,(%r10)
     f22:	41 88 42 02          	mov    %al,0x2(%r10)
     f26:	49 8d 41 04          	lea    0x4(%r9),%rax
     f2a:	48 39 c8             	cmp    %rcx,%rax
     f2d:	0f 83 1d 01 00 00    	jae    1050 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1050>
     f33:	4d 8d 54 10 0c       	lea    0xc(%r8,%rdx,1),%r10
     f38:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     f3d:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     f42:	c1 e0 10             	shl    $0x10,%eax
     f45:	41 c1 e3 08          	shl    $0x8,%r11d
     f49:	44 09 d8             	or     %r11d,%eax
     f4c:	45 0f b6 1a          	movzbl (%r10),%r11d
     f50:	0f b6 dc             	movzbl %ah,%ebx
     f53:	c1 e8 10             	shr    $0x10,%eax
     f56:	29 d8                	sub    %ebx,%eax
     f58:	44 29 db             	sub    %r11d,%ebx
     f5b:	c1 e0 10             	shl    $0x10,%eax
     f5e:	c1 e3 08             	shl    $0x8,%ebx
     f61:	25 00 00 ff 00       	and    $0xff0000,%eax
     f66:	0f b7 db             	movzwl %bx,%ebx
     f69:	09 d8                	or     %ebx,%eax
     f6b:	44 09 d8             	or     %r11d,%eax
     f6e:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f72:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f76:	41 8b 03             	mov    (%r11),%eax
     f79:	45 0f b7 1b          	movzwl (%r11),%r11d
     f7d:	c1 e8 10             	shr    $0x10,%eax
     f80:	66 45 89 1a          	mov    %r11w,(%r10)
     f84:	41 88 42 02          	mov    %al,0x2(%r10)
     f88:	49 8d 41 05          	lea    0x5(%r9),%rax
     f8c:	48 39 c8             	cmp    %rcx,%rax
     f8f:	0f 83 bb 00 00 00    	jae    1050 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1050>
     f95:	4d 8d 54 10 0f       	lea    0xf(%r8,%rdx,1),%r10
     f9a:	49 83 c1 06          	add    $0x6,%r9
     f9e:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     fa3:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     fa8:	c1 e0 10             	shl    $0x10,%eax
     fab:	41 c1 e3 08          	shl    $0x8,%r11d
     faf:	44 09 d8             	or     %r11d,%eax
     fb2:	45 0f b6 1a          	movzbl (%r10),%r11d
     fb6:	0f b6 dc             	movzbl %ah,%ebx
     fb9:	c1 e8 10             	shr    $0x10,%eax
     fbc:	29 d8                	sub    %ebx,%eax
     fbe:	44 29 db             	sub    %r11d,%ebx
     fc1:	c1 e0 10             	shl    $0x10,%eax
     fc4:	c1 e3 08             	shl    $0x8,%ebx
     fc7:	25 00 00 ff 00       	and    $0xff0000,%eax
     fcc:	0f b7 db             	movzwl %bx,%ebx
     fcf:	09 d8                	or     %ebx,%eax
     fd1:	44 09 d8             	or     %r11d,%eax
     fd4:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     fd8:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     fdc:	41 8b 03             	mov    (%r11),%eax
     fdf:	45 0f b7 1b          	movzwl (%r11),%r11d
     fe3:	c1 e8 10             	shr    $0x10,%eax
     fe6:	66 45 89 1a          	mov    %r11w,(%r10)
     fea:	41 88 42 02          	mov    %al,0x2(%r10)
     fee:	49 39 c9             	cmp    %rcx,%r9
     ff1:	73 5d                	jae    1050 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1050>
     ff3:	49 8d 4c 10 12       	lea    0x12(%r8,%rdx,1),%rcx
     ff8:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
     ffc:	0f b6 51 02          	movzbl 0x2(%rcx),%edx
    1000:	44 0f b6 01          	movzbl (%rcx),%r8d
    1004:	c1 e2 10             	shl    $0x10,%edx
    1007:	c1 e0 08             	shl    $0x8,%eax
    100a:	09 d0                	or     %edx,%eax
    100c:	0f b6 d4             	movzbl %ah,%edx
    100f:	c1 e8 10             	shr    $0x10,%eax
    1012:	29 d0                	sub    %edx,%eax
    1014:	44 29 c2             	sub    %r8d,%edx
    1017:	c1 e0 10             	shl    $0x10,%eax
    101a:	c1 e2 08             	shl    $0x8,%edx
    101d:	25 00 00 ff 00       	and    $0xff0000,%eax
    1022:	0f b7 d2             	movzwl %dx,%edx
    1025:	09 d0                	or     %edx,%eax
    1027:	44 09 c0             	or     %r8d,%eax
    102a:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    102e:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1032:	8b 02                	mov    (%rdx),%eax
    1034:	0f b7 12             	movzwl (%rdx),%edx
    1037:	c1 e8 10             	shr    $0x10,%eax
    103a:	66 89 11             	mov    %dx,(%rcx)
    103d:	88 41 02             	mov    %al,0x2(%rcx)
    1040:	c5 f8 77             	vzeroupper
    1043:	5b                   	pop    %rbx
    1044:	41 5c                	pop    %r12
    1046:	41 5d                	pop    %r13
    1048:	41 5e                	pop    %r14
    104a:	41 5f                	pop    %r15
    104c:	5d                   	pop    %rbp
    104d:	c3                   	ret
    104e:	66 90                	xchg   %ax,%ax
    1050:	c5 f8 77             	vzeroupper
    1053:	5b                   	pop    %rbx
    1054:	41 5c                	pop    %r12
    1056:	41 5d                	pop    %r13
    1058:	41 5e                	pop    %r14
    105a:	41 5f                	pop    %r15
    105c:	5d                   	pop    %rbp
    105d:	c3                   	ret
    105e:	66 90                	xchg   %ax,%ax
    1060:	49 89 c9             	mov    %rcx,%r9
    1063:	e9 08 fc ff ff       	jmp    c70 <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc70>
    1068:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    106f:	00 
    1070:	c3                   	ret
    1071:	48 8d 42 28          	lea    0x28(%rdx),%rax
    1075:	49 89 d1             	mov    %rdx,%r9
    1078:	e9 0f f8 ff ff       	jmp    88c <jshc_channel::avx2_chain_chroma_delta(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x88c>
    107d:	0f 1f 00             	nopl   (%rax)

0000000000001080 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1080:	f3 0f 1e fa          	endbr64
    1084:	4d 85 c0             	test   %r8,%r8
    1087:	0f 84 3b 11 00 00    	je     21c8 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1148>
    108d:	55                   	push   %rbp
    108e:	b8 00 04 00 00       	mov    $0x400,%eax
    1093:	49 89 d2             	mov    %rdx,%r10
    1096:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    109a:	49 89 cb             	mov    %rcx,%r11
    109d:	48 89 e5             	mov    %rsp,%rbp
    10a0:	41 57                	push   %r15
    10a2:	41 56                	push   %r14
    10a4:	41 55                	push   %r13
    10a6:	41 54                	push   %r12
    10a8:	53                   	push   %rbx
    10a9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    10ad:	48 39 c2             	cmp    %rax,%rdx
    10b0:	48 0f 47 d0          	cmova  %rax,%rdx
    10b4:	31 c0                	xor    %eax,%eax
    10b6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    10bd:	00 00 00 
    10c0:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
    10c5:	48 83 c0 40          	add    $0x40,%rax
    10c9:	48 39 d0             	cmp    %rdx,%rax
    10cc:	72 f2                	jb     10c0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
    10ce:	4d 89 d1             	mov    %r10,%r9
    10d1:	4c 89 da             	mov    %r11,%rdx
    10d4:	31 c9                	xor    %ecx,%ecx
    10d6:	49 89 f7             	mov    %rsi,%r15
    10d9:	eb 6a                	jmp    1145 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc5>
    10db:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    10e0:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
    10e5:	41 0f b6 59 02       	movzbl 0x2(%r9),%ebx
    10ea:	48 ff c1             	inc    %rcx
    10ed:	48 83 c2 03          	add    $0x3,%rdx
    10f1:	49 83 c1 03          	add    $0x3,%r9
    10f5:	c1 e3 10             	shl    $0x10,%ebx
    10f8:	c1 e0 08             	shl    $0x8,%eax
    10fb:	09 d8                	or     %ebx,%eax
    10fd:	41 0f b6 59 fd       	movzbl -0x3(%r9),%ebx
    1102:	0f b6 f4             	movzbl %ah,%esi
    1105:	c1 e8 10             	shr    $0x10,%eax
    1108:	41 89 f4             	mov    %esi,%r12d
    110b:	29 f0                	sub    %esi,%eax
    110d:	41 29 dc             	sub    %ebx,%r12d
    1110:	c1 e0 10             	shl    $0x10,%eax
    1113:	41 c1 e4 08          	shl    $0x8,%r12d
    1117:	25 00 00 ff 00       	and    $0xff0000,%eax
    111c:	45 0f b7 e4          	movzwl %r12w,%r12d
    1120:	44 09 e0             	or     %r12d,%eax
    1123:	09 d8                	or     %ebx,%eax
    1125:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1129:	49 8d 1c 87          	lea    (%r15,%rax,4),%rbx
    112d:	8b 03                	mov    (%rbx),%eax
    112f:	0f b7 1b             	movzwl (%rbx),%ebx
    1132:	c1 e8 10             	shr    $0x10,%eax
    1135:	66 89 5a fd          	mov    %bx,-0x3(%rdx)
    1139:	88 42 ff             	mov    %al,-0x1(%rdx)
    113c:	49 39 c8             	cmp    %rcx,%r8
    113f:	0f 84 73 10 00 00    	je     21b8 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1138>
    1145:	f6 c2 3f             	test   $0x3f,%dl
    1148:	75 96                	jne    10e0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    114a:	48 8d 41 48          	lea    0x48(%rcx),%rax
    114e:	4c 89 fe             	mov    %r15,%rsi
    1151:	49 39 c0             	cmp    %rax,%r8
    1154:	0f 82 6f 10 00 00    	jb     21c9 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1149>
    115a:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    115e:	c4 41 25 76 db       	vpcmpeqd %ymm11,%ymm11,%ymm11
    1163:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1168:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1170 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    116f:	00 
    1170:	49 8d 14 03          	lea    (%r11,%rax,1),%rdx
    1174:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1179:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1181 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x101>
    1180:	00 
    1181:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
    1188:	00 
    1189:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # 1191 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x111>
    1190:	00 
    1191:	c4 c1 25 72 d3 08    	vpsrld $0x8,%ymm11,%ymm11
    1197:	eb 0a                	jmp    11a3 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x123>
    1199:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    11a0:	4c 89 c9             	mov    %r9,%rcx
    11a3:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    11aa:	4d 39 c8             	cmp    %r9,%r8
    11ad:	72 15                	jb     11c4 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x144>
    11af:	0f 18 00             	prefetchnta (%rax)
    11b2:	0f 18 40 40          	prefetchnta 0x40(%rax)
    11b6:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    11bd:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    11c4:	c5 fa 6f 80 00 fc ff 	vmovdqu -0x400(%rax),%xmm0
    11cb:	ff 
    11cc:	c5 fa 7e 88 10 fc ff 	vmovq  -0x3f0(%rax),%xmm1
    11d3:	ff 
    11d4:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    11db:	48 05 c0 00 00 00    	add    $0xc0,%rax
    11e1:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    11e7:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    11ed:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    11f2:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    11f7:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    11fb:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    1200:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1206:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    120b:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1211:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1216:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    121c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1221:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1226:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    122b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1230:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1236:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    123c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1241:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1246:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    124c:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1252:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1258:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    125e:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1263:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1268:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    126f:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1276:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    127c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1280:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1285:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    128c:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1293:	c5 29 6c d1          	vpunpcklqdq %xmm1,%xmm10,%xmm10
    1297:	c5 fa 7e 88 68 fb ff 	vmovq  -0x498(%rax),%xmm1
    129e:	ff 
    129f:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
    12a5:	c5 fa 6f 80 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm0
    12ac:	ff 
    12ad:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
    12b2:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    12b8:	c4 42 4d 36 d2       	vpermd %ymm10,%ymm6,%ymm10
    12bd:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    12c3:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    12c8:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    12cd:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    12d1:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    12d6:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    12dc:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    12e1:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    12e7:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    12ec:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    12f2:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    12f7:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    12fc:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1301:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1306:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    130c:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1312:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1317:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    131c:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1322:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1328:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    132e:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1334:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1339:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    133e:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1345:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    134c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1350:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1355:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    135b:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1362:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
    1369:	c5 e1 6c d9          	vpunpcklqdq %xmm1,%xmm3,%xmm3
    136d:	c5 fa 7e 88 80 fb ff 	vmovq  -0x480(%rax),%xmm1
    1374:	ff 
    1375:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
    137b:	c5 fa 6f 80 70 fb ff 	vmovdqu -0x490(%rax),%xmm0
    1382:	ff 
    1383:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
    1388:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    138e:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
    1393:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1399:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    139e:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    13a3:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    13a7:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    13ac:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    13b2:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    13b7:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    13bd:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    13c2:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    13c8:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    13cd:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    13d2:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    13d7:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    13dc:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    13e2:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    13e8:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    13ed:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    13f2:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    13f8:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    13fe:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1404:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    140a:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    140f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1414:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    141b:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1422:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    1428:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    142c:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1431:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    1438:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    143f:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
    1443:	c5 fa 7e 88 98 fb ff 	vmovq  -0x468(%rax),%xmm1
    144a:	ff 
    144b:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    1451:	c5 fa 6f 80 88 fb ff 	vmovdqu -0x478(%rax),%xmm0
    1458:	ff 
    1459:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    145e:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1464:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
    1469:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    146f:	c5 79 6f f2          	vmovdqa %xmm2,%xmm14
    1473:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1479:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    147e:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    1483:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    1487:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    148c:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1492:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1497:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    149d:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    14a2:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    14a8:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    14ad:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    14b2:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    14b7:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    14bc:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    14c2:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    14c8:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    14ce:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    14d4:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    14d9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    14de:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    14e3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    14e8:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    14ee:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    14f4:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    14fa:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1501:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1508:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
    150f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1513:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1518:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    151f:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    1523:	c5 fa 7e 88 b0 fb ff 	vmovq  -0x450(%rax),%xmm1
    152a:	ff 
    152b:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    1531:	c5 fa 6f 80 a0 fb ff 	vmovdqu -0x460(%rax),%xmm0
    1538:	ff 
    1539:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
    153e:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1544:	c4 42 4d 36 c9       	vpermd %ymm9,%ymm6,%ymm9
    1549:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    154f:	c4 41 79 6f f9       	vmovdqa %xmm9,%xmm15
    1554:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    155a:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    155f:	c4 43 31 0f cf 08    	vpalignr $0x8,%xmm15,%xmm9,%xmm9
    1565:	c4 c1 69 6c d7       	vpunpcklqdq %xmm15,%xmm2,%xmm2
    156a:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    156f:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
    1575:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    1579:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    157e:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1584:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1589:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    158f:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1594:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    159a:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    159f:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    15a4:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    15a9:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    15ae:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    15b4:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    15ba:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    15bf:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    15c4:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    15ca:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    15d0:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    15d6:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    15dc:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    15e1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    15e6:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    15ed:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    15f4:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    15fa:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    15fe:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1603:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    160a:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1611:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    1615:	c5 fa 7e 88 c8 fb ff 	vmovq  -0x438(%rax),%xmm1
    161c:	ff 
    161d:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    1623:	c5 fa 6f 80 b8 fb ff 	vmovdqu -0x448(%rax),%xmm0
    162a:	ff 
    162b:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
    1630:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1636:	c4 42 4d 36 c0       	vpermd %ymm8,%ymm6,%ymm8
    163b:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1641:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1646:	c5 f5 72 f0 08       	vpslld $0x8,%ymm0,%ymm1
    164b:	c5 fd f8 c1          	vpsubb %ymm1,%ymm0,%ymm0
    164f:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    1654:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    165a:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    165f:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1665:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    166a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    166f:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1674:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    167a:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1680:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1686:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    168b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1690:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1695:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    169a:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    16a0:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    16a6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    16ab:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    16b0:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    16b6:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    16bc:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    16c2:	c4 a3 41 22 3c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm7,%xmm7
    16c9:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    16d0:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    16d7:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    16db:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    16e0:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    16e7:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
    16eb:	c5 fa 7e b8 e0 fb ff 	vmovq  -0x420(%rax),%xmm7
    16f2:	ff 
    16f3:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    16f9:	c5 fa 6f 80 d0 fb ff 	vmovdqu -0x430(%rax),%xmm0
    1700:	ff 
    1701:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    1706:	c4 e3 41 0f f8 0c    	vpalignr $0xc,%xmm0,%xmm7,%xmm7
    170c:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
    1711:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    1717:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    171c:	c5 c5 72 f0 08       	vpslld $0x8,%ymm0,%ymm7
    1721:	c5 fd f8 c7          	vpsubb %ymm7,%ymm0,%ymm0
    1725:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    172a:	c4 e3 7d 39 c7 01    	vextracti128 $0x1,%ymm0,%xmm7
    1730:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1735:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    173b:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    1740:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    1746:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    174b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1750:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1755:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    175a:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    1760:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    1766:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    176b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1770:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1776:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    177c:	c4 21 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm12
    1782:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1788:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    178d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1792:	c4 23 19 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm12,%xmm12
    1799:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    17a0:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    17a6:	c4 c1 41 6c fc       	vpunpcklqdq %xmm12,%xmm7,%xmm7
    17ab:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
    17b0:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    17b7:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    17be:	c4 c1 79 6c c4       	vpunpcklqdq %xmm12,%xmm0,%xmm0
    17c3:	c5 7a 7e a0 f8 fb ff 	vmovq  -0x408(%rax),%xmm12
    17ca:	ff 
    17cb:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    17d1:	c5 fa 6f b8 e8 fb ff 	vmovdqu -0x418(%rax),%xmm7
    17d8:	ff 
    17d9:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    17de:	c4 63 19 0f e7 0c    	vpalignr $0xc,%xmm7,%xmm12,%xmm12
    17e4:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
    17e9:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
    17ef:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    17f3:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    17f9:	c4 e2 45 00 fd       	vpshufb %ymm5,%ymm7,%ymm7
    17fe:	c5 9d 72 f7 08       	vpslld $0x8,%ymm7,%ymm12
    1803:	c4 c1 45 f8 fc       	vpsubb %ymm12,%ymm7,%ymm7
    1808:	c4 c1 45 db fb       	vpand  %ymm11,%ymm7,%ymm7
    180d:	c4 c3 7d 39 fc 01    	vextracti128 $0x1,%ymm7,%xmm12
    1813:	c4 c1 79 7e f9       	vmovd  %xmm7,%r9d
    1818:	c4 c3 79 16 fb 02    	vpextrd $0x2,%xmm7,%r11d
    181e:	c4 41 79 7e e4       	vmovd  %xmm12,%r12d
    1823:	c4 43 79 16 e6 02    	vpextrd $0x2,%xmm12,%r14d
    1829:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    182e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1833:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1838:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    183d:	c4 43 79 16 e4 01    	vpextrd $0x1,%xmm12,%r12d
    1843:	c4 43 79 16 e6 03    	vpextrd $0x3,%xmm12,%r14d
    1849:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    184e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1853:	c4 c3 79 16 f9 01    	vpextrd $0x1,%xmm7,%r9d
    1859:	c4 c3 79 16 fb 03    	vpextrd $0x3,%xmm7,%r11d
    185f:	c4 21 79 6e 2c be    	vmovd  (%rsi,%r15,4),%xmm13
    1865:	c4 21 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm12
    186b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1870:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    1876:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    187d:	c4 23 11 22 2c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm13,%xmm13
    1884:	c4 23 19 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm12,%xmm12
    188b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1890:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    1897:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    189b:	c4 41 19 6c e5       	vpunpcklqdq %xmm13,%xmm12,%xmm12
    18a0:	c5 79 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm13
    18a5:	c4 23 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm13,%xmm13
    18ac:	c5 fd e7 52 80       	vmovntdq %ymm2,-0x80(%rdx)
    18b1:	c5 79 7f c2          	vmovdqa %xmm8,%xmm2
    18b5:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    18bb:	c4 c1 41 6c fd       	vpunpcklqdq %xmm13,%xmm7,%xmm7
    18c0:	c5 79 6f eb          	vmovdqa %xmm3,%xmm13
    18c4:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    18ca:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
    18d0:	c4 c3 61 0f dd 08    	vpalignr $0x8,%xmm13,%xmm3,%xmm3
    18d6:	c4 41 79 6f e2       	vmovdqa %xmm10,%xmm12
    18db:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    18e0:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
    18e6:	c4 c3 65 38 de 01    	vinserti128 $0x1,%xmm14,%ymm3,%ymm3
    18ec:	c4 e2 4d 36 ff       	vpermd %ymm7,%ymm6,%ymm7
    18f1:	c4 41 29 6c d5       	vpunpcklqdq %xmm13,%xmm10,%xmm10
    18f6:	c5 fd e7 9a 60 ff ff 	vmovntdq %ymm3,-0xa0(%rdx)
    18fd:	ff 
    18fe:	c4 43 1d 38 e2 01    	vinserti128 $0x1,%xmm10,%ymm12,%ymm12
    1904:	c5 f9 6f df          	vmovdqa %xmm7,%xmm3
    1908:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
    190c:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1912:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1918:	c4 41 39 6c c2       	vpunpcklqdq %xmm10,%xmm8,%xmm8
    191d:	c5 7d e7 a2 40 ff ff 	vmovntdq %ymm12,-0xc0(%rdx)
    1924:	ff 
    1925:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
    192b:	c4 e3 41 0f fb 08    	vpalignr $0x8,%xmm3,%xmm7,%xmm7
    1931:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
    1935:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
    193b:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1941:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    1947:	c5 fd e7 52 a0       	vmovntdq %ymm2,-0x60(%rdx)
    194c:	c5 fd e7 4a c0       	vmovntdq %ymm1,-0x40(%rdx)
    1951:	c5 fd e7 42 e0       	vmovntdq %ymm0,-0x20(%rdx)
    1956:	4d 39 d0             	cmp    %r10,%r8
    1959:	0f 83 41 f8 ff ff    	jae    11a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x120>
    195f:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1964:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1969:	48 8d 41 68          	lea    0x68(%rcx),%rax
    196d:	0f ae f8             	sfence
    1970:	49 39 c0             	cmp    %rax,%r8
    1973:	0f 82 01 04 00 00    	jb     1d7a <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcfa>
    1979:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    197e:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1982:	c4 41 3d 76 c0       	vpcmpeqd %ymm8,%ymm8,%ymm8
    1987:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 198f <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x90f>
    198e:	00 
    198f:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1994:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 199c <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x91c>
    199b:	00 
    199c:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
    19a0:	c4 c1 3d 72 d0 08    	vpsrld $0x8,%ymm8,%ymm8
    19a6:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # 19ae <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x92e>
    19ad:	00 
    19ae:	4c 01 da             	add    %r11,%rdx
    19b1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    19b8:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
    19bc:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    19c1:	48 83 c2 60          	add    $0x60,%rdx
    19c5:	48 83 c0 60          	add    $0x60,%rax
    19c9:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
    19ce:	c5 fa 7e 58 e0       	vmovq  -0x20(%rax),%xmm3
    19d3:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    19d9:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
    19de:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    19e4:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
    19e9:	c5 fd 72 f2 08       	vpslld $0x8,%ymm2,%ymm0
    19ee:	c5 ed f8 d0          	vpsubb %ymm0,%ymm2,%ymm2
    19f2:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
    19f7:	c4 c1 6d db d0       	vpand  %ymm8,%ymm2,%ymm2
    19fc:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
    1a02:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
    1a08:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1a0e:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
    1a13:	c5 fd 72 f1 08       	vpslld $0x8,%ymm1,%ymm0
    1a18:	c5 f5 f8 c8          	vpsubb %ymm0,%ymm1,%ymm1
    1a1c:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
    1a21:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
    1a26:	c4 e3 61 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm3,%xmm3
    1a2c:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
    1a32:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
    1a38:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1a3d:	c5 e5 72 f0 08       	vpslld $0x8,%ymm0,%ymm3
    1a42:	c5 fd f8 c3          	vpsubb %ymm3,%ymm0,%ymm0
    1a46:	c5 fa 6f 58 e8       	vmovdqu -0x18(%rax),%xmm3
    1a4b:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
    1a50:	c4 63 21 0f db 0c    	vpalignr $0xc,%xmm3,%xmm11,%xmm11
    1a56:	c4 c3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm10
    1a5c:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
    1a62:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
    1a67:	c5 a5 72 f3 08       	vpslld $0x8,%ymm3,%ymm11
    1a6c:	c4 c1 65 f8 db       	vpsubb %ymm11,%ymm3,%ymm3
    1a71:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    1a76:	c4 c3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm11
    1a7c:	c5 f9 7e d9          	vmovd  %xmm3,%ecx
    1a80:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
    1a86:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
    1a8b:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
    1a91:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1a96:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1a9b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1aa0:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1aa5:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
    1aab:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
    1ab1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1ab6:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1abb:	c4 e3 79 16 d9 01    	vpextrd $0x1,%xmm3,%ecx
    1ac1:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    1ac7:	c4 21 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm12
    1acd:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
    1ad3:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1ad7:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1adc:	c4 23 19 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm12,%xmm12
    1ae3:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
    1aea:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    1af0:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    1af6:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    1afb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1b00:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    1b06:	c4 41 21 6c dc       	vpunpcklqdq %xmm12,%xmm11,%xmm11
    1b0b:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
    1b10:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1b15:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    1b1b:	c4 e3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm3,%xmm3
    1b22:	c5 f9 7e c1          	vmovd  %xmm0,%ecx
    1b26:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1b2b:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    1b32:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1b38:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1b3d:	c4 e3 79 16 c1 01    	vpextrd $0x1,%xmm0,%ecx
    1b43:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1b48:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1b4e:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1b52:	c4 c1 61 6c dc       	vpunpcklqdq %xmm12,%xmm3,%xmm3
    1b57:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1b5c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1b61:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
    1b67:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1b6d:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
    1b73:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1b79:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
    1b7e:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    1b85:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
    1b8c:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    1b92:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
    1b99:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    1b9e:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1ba3:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    1ba9:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1bae:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    1bb3:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1bb8:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    1bbe:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1bc3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1bc8:	c5 f9 7e c9          	vmovd  %xmm1,%ecx
    1bcc:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
    1bd1:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    1bd8:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    1bde:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1be4:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1be9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1bee:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    1bf4:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1bfa:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
    1bff:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    1c06:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1c0a:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    1c0f:	c4 c3 7d 38 c2 01    	vinserti128 $0x1,%xmm10,%ymm0,%ymm0
    1c15:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1c1b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1c20:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1c26:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1c2b:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    1c31:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1c36:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    1c3d:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    1c43:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1c48:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
    1c4d:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    1c54:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1c59:	c5 f9 7e d1          	vmovd  %xmm2,%ecx
    1c5d:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    1c63:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    1c68:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    1c6d:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1c72:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    1c78:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1c7c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1c81:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    1c88:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    1c8e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1c93:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    1c99:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1c9e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1ca3:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
    1ca7:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1cad:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1cb3:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    1cb9:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1cbf:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    1cc5:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    1cca:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    1cd1:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    1cd8:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
    1cdd:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1ce4:	c5 79 6f d9          	vmovdqa %xmm1,%xmm11
    1ce8:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1cee:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    1cf3:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    1cf8:	c4 c3 71 0f cb 08    	vpalignr $0x8,%xmm11,%xmm1,%xmm1
    1cfe:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1d02:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
    1d08:	49 83 c1 20          	add    $0x20,%r9
    1d0c:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1d13:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1d18:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1d1d:	c5 79 6f cb          	vmovdqa %xmm3,%xmm9
    1d21:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    1d27:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
    1d2d:	c4 c3 61 0f d9 08    	vpalignr $0x8,%xmm9,%xmm3,%xmm3
    1d33:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    1d38:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    1d3d:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
    1d43:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
    1d48:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1d4d:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    1d51:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1d57:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    1d5c:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
    1d62:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1d67:	49 39 c8             	cmp    %rcx,%r8
    1d6a:	0f 83 48 fc ff ff    	jae    19b8 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x938>
    1d70:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1d75:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1d7a:	49 8d 51 08          	lea    0x8(%r9),%rdx
    1d7e:	49 39 d0             	cmp    %rdx,%r8
    1d81:	0f 82 3e 01 00 00    	jb     1ec5 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe45>
    1d87:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1d8c:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1d90:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
    1d94:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1d9c <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd1c>
    1d9b:	00 
    1d9c:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1da1:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1da9 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd29>
    1da8:	00 
    1da9:	49 8d 0c 02          	lea    (%r10,%rax,1),%rcx
    1dad:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
    1db2:	4c 01 d8             	add    %r11,%rax
    1db5:	0f 1f 00             	nopl   (%rax)
    1db8:	c5 fa 6f 01          	vmovdqu (%rcx),%xmm0
    1dbc:	c5 fa 7e 51 10       	vmovq  0x10(%rcx),%xmm2
    1dc1:	48 83 c0 18          	add    $0x18,%rax
    1dc5:	48 83 c1 18          	add    $0x18,%rcx
    1dc9:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
    1dcf:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    1dd5:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1dda:	c5 ed 72 f0 08       	vpslld $0x8,%ymm0,%ymm2
    1ddf:	c5 fd f8 c2          	vpsubb %ymm2,%ymm0,%ymm0
    1de3:	c5 fd db c1          	vpand  %ymm1,%ymm0,%ymm0
    1de7:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
    1ded:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1df2:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1df8:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    1dfd:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    1e03:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1e08:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1e0d:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1e12:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1e17:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1e1d:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    1e23:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1e28:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1e2d:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1e33:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1e39:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
    1e3f:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1e45:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1e4a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1e4f:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
    1e56:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1e5d:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1e63:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    1e67:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
    1e6c:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1e73:	49 89 d1             	mov    %rdx,%r9
    1e76:	48 83 c2 08          	add    $0x8,%rdx
    1e7a:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
    1e81:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
    1e85:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    1e8b:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1e90:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
    1e94:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1e9a:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
    1e9f:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1ea4:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
    1ea8:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    1ead:	c5 fa 7f 50 e8       	vmovdqu %xmm2,-0x18(%rax)
    1eb2:	49 39 d0             	cmp    %rdx,%r8
    1eb5:	0f 83 fd fe ff ff    	jae    1db8 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd38>
    1ebb:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1ec0:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1ec5:	4d 39 c1             	cmp    %r8,%r9
    1ec8:	0f 83 d2 02 00 00    	jae    21a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1120>
    1ece:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1ed2:	49 8d 1c 12          	lea    (%r10,%rdx,1),%rbx
    1ed6:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    1eda:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1edf:	0f b6 1b             	movzbl (%rbx),%ebx
    1ee2:	41 c1 e4 10          	shl    $0x10,%r12d
    1ee6:	c1 e0 08             	shl    $0x8,%eax
    1ee9:	44 09 e0             	or     %r12d,%eax
    1eec:	0f b6 cc             	movzbl %ah,%ecx
    1eef:	c1 e8 10             	shr    $0x10,%eax
    1ef2:	41 89 cc             	mov    %ecx,%r12d
    1ef5:	29 c8                	sub    %ecx,%eax
    1ef7:	41 29 dc             	sub    %ebx,%r12d
    1efa:	c1 e0 10             	shl    $0x10,%eax
    1efd:	41 c1 e4 08          	shl    $0x8,%r12d
    1f01:	25 00 00 ff 00       	and    $0xff0000,%eax
    1f06:	45 0f b7 e4          	movzwl %r12w,%r12d
    1f0a:	44 09 e0             	or     %r12d,%eax
    1f0d:	09 d8                	or     %ebx,%eax
    1f0f:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1f13:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    1f17:	8b 03                	mov    (%rbx),%eax
    1f19:	0f b7 1b             	movzwl (%rbx),%ebx
    1f1c:	c1 e8 10             	shr    $0x10,%eax
    1f1f:	66 41 89 1c 13       	mov    %bx,(%r11,%rdx,1)
    1f24:	41 88 44 13 02       	mov    %al,0x2(%r11,%rdx,1)
    1f29:	49 8d 41 01          	lea    0x1(%r9),%rax
    1f2d:	4c 39 c0             	cmp    %r8,%rax
    1f30:	0f 83 6a 02 00 00    	jae    21a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1120>
    1f36:	49 8d 5c 12 03       	lea    0x3(%r10,%rdx,1),%rbx
    1f3b:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    1f3f:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1f44:	0f b6 1b             	movzbl (%rbx),%ebx
    1f47:	41 c1 e4 10          	shl    $0x10,%r12d
    1f4b:	c1 e0 08             	shl    $0x8,%eax
    1f4e:	44 09 e0             	or     %r12d,%eax
    1f51:	0f b6 cc             	movzbl %ah,%ecx
    1f54:	c1 e8 10             	shr    $0x10,%eax
    1f57:	41 89 cc             	mov    %ecx,%r12d
    1f5a:	29 c8                	sub    %ecx,%eax
    1f5c:	41 29 dc             	sub    %ebx,%r12d
    1f5f:	c1 e0 10             	shl    $0x10,%eax
    1f62:	41 c1 e4 08          	shl    $0x8,%r12d
    1f66:	25 00 00 ff 00       	and    $0xff0000,%eax
    1f6b:	45 0f b7 e4          	movzwl %r12w,%r12d
    1f6f:	44 09 e0             	or     %r12d,%eax
    1f72:	09 d8                	or     %ebx,%eax
    1f74:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1f78:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    1f7c:	8b 03                	mov    (%rbx),%eax
    1f7e:	0f b7 1b             	movzwl (%rbx),%ebx
    1f81:	c1 e8 10             	shr    $0x10,%eax
    1f84:	66 41 89 5c 13 03    	mov    %bx,0x3(%r11,%rdx,1)
    1f8a:	41 88 44 13 05       	mov    %al,0x5(%r11,%rdx,1)
    1f8f:	49 8d 41 02          	lea    0x2(%r9),%rax
    1f93:	4c 39 c0             	cmp    %r8,%rax
    1f96:	0f 83 04 02 00 00    	jae    21a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1120>
    1f9c:	49 8d 5c 12 06       	lea    0x6(%r10,%rdx,1),%rbx
    1fa1:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    1fa5:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1faa:	0f b6 1b             	movzbl (%rbx),%ebx
    1fad:	41 c1 e4 08          	shl    $0x8,%r12d
    1fb1:	c1 e0 10             	shl    $0x10,%eax
    1fb4:	44 09 e0             	or     %r12d,%eax
    1fb7:	0f b6 cc             	movzbl %ah,%ecx
    1fba:	c1 e8 10             	shr    $0x10,%eax
    1fbd:	41 89 cc             	mov    %ecx,%r12d
    1fc0:	29 c8                	sub    %ecx,%eax
    1fc2:	41 29 dc             	sub    %ebx,%r12d
    1fc5:	c1 e0 10             	shl    $0x10,%eax
    1fc8:	41 c1 e4 08          	shl    $0x8,%r12d
    1fcc:	25 00 00 ff 00       	and    $0xff0000,%eax
    1fd1:	45 0f b7 e4          	movzwl %r12w,%r12d
    1fd5:	44 09 e0             	or     %r12d,%eax
    1fd8:	09 d8                	or     %ebx,%eax
    1fda:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1fde:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    1fe2:	8b 03                	mov    (%rbx),%eax
    1fe4:	0f b7 1b             	movzwl (%rbx),%ebx
    1fe7:	c1 e8 10             	shr    $0x10,%eax
    1fea:	66 41 89 5c 13 06    	mov    %bx,0x6(%r11,%rdx,1)
    1ff0:	41 88 44 13 08       	mov    %al,0x8(%r11,%rdx,1)
    1ff5:	49 8d 41 03          	lea    0x3(%r9),%rax
    1ff9:	4c 39 c0             	cmp    %r8,%rax
    1ffc:	0f 83 9e 01 00 00    	jae    21a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1120>
    2002:	49 8d 5c 12 09       	lea    0x9(%r10,%rdx,1),%rbx
    2007:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    200b:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    2010:	0f b6 1b             	movzbl (%rbx),%ebx
    2013:	41 c1 e4 08          	shl    $0x8,%r12d
    2017:	c1 e0 10             	shl    $0x10,%eax
    201a:	44 09 e0             	or     %r12d,%eax
    201d:	0f b6 cc             	movzbl %ah,%ecx
    2020:	c1 e8 10             	shr    $0x10,%eax
    2023:	41 89 cc             	mov    %ecx,%r12d
    2026:	29 c8                	sub    %ecx,%eax
    2028:	41 29 dc             	sub    %ebx,%r12d
    202b:	c1 e0 10             	shl    $0x10,%eax
    202e:	41 c1 e4 08          	shl    $0x8,%r12d
    2032:	25 00 00 ff 00       	and    $0xff0000,%eax
    2037:	45 0f b7 e4          	movzwl %r12w,%r12d
    203b:	44 09 e0             	or     %r12d,%eax
    203e:	09 d8                	or     %ebx,%eax
    2040:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2044:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    2048:	8b 03                	mov    (%rbx),%eax
    204a:	0f b7 1b             	movzwl (%rbx),%ebx
    204d:	c1 e8 10             	shr    $0x10,%eax
    2050:	66 41 89 5c 13 09    	mov    %bx,0x9(%r11,%rdx,1)
    2056:	41 88 44 13 0b       	mov    %al,0xb(%r11,%rdx,1)
    205b:	49 8d 41 04          	lea    0x4(%r9),%rax
    205f:	4c 39 c0             	cmp    %r8,%rax
    2062:	0f 83 38 01 00 00    	jae    21a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1120>
    2068:	49 8d 5c 12 0c       	lea    0xc(%r10,%rdx,1),%rbx
    206d:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    2071:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    2076:	0f b6 1b             	movzbl (%rbx),%ebx
    2079:	41 c1 e4 08          	shl    $0x8,%r12d
    207d:	c1 e0 10             	shl    $0x10,%eax
    2080:	44 09 e0             	or     %r12d,%eax
    2083:	0f b6 cc             	movzbl %ah,%ecx
    2086:	c1 e8 10             	shr    $0x10,%eax
    2089:	41 89 cc             	mov    %ecx,%r12d
    208c:	29 c8                	sub    %ecx,%eax
    208e:	41 29 dc             	sub    %ebx,%r12d
    2091:	c1 e0 10             	shl    $0x10,%eax
    2094:	41 c1 e4 08          	shl    $0x8,%r12d
    2098:	25 00 00 ff 00       	and    $0xff0000,%eax
    209d:	45 0f b7 e4          	movzwl %r12w,%r12d
    20a1:	44 09 e0             	or     %r12d,%eax
    20a4:	09 d8                	or     %ebx,%eax
    20a6:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    20aa:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    20ae:	8b 03                	mov    (%rbx),%eax
    20b0:	0f b7 1b             	movzwl (%rbx),%ebx
    20b3:	c1 e8 10             	shr    $0x10,%eax
    20b6:	66 41 89 5c 13 0c    	mov    %bx,0xc(%r11,%rdx,1)
    20bc:	41 88 44 13 0e       	mov    %al,0xe(%r11,%rdx,1)
    20c1:	49 8d 41 05          	lea    0x5(%r9),%rax
    20c5:	4c 39 c0             	cmp    %r8,%rax
    20c8:	0f 83 d2 00 00 00    	jae    21a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1120>
    20ce:	49 8d 5c 12 0f       	lea    0xf(%r10,%rdx,1),%rbx
    20d3:	49 83 c1 06          	add    $0x6,%r9
    20d7:	0f b6 43 02          	movzbl 0x2(%rbx),%eax
    20db:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    20e0:	0f b6 1b             	movzbl (%rbx),%ebx
    20e3:	41 c1 e4 08          	shl    $0x8,%r12d
    20e7:	c1 e0 10             	shl    $0x10,%eax
    20ea:	44 09 e0             	or     %r12d,%eax
    20ed:	0f b6 cc             	movzbl %ah,%ecx
    20f0:	c1 e8 10             	shr    $0x10,%eax
    20f3:	41 89 cc             	mov    %ecx,%r12d
    20f6:	29 c8                	sub    %ecx,%eax
    20f8:	41 29 dc             	sub    %ebx,%r12d
    20fb:	c1 e0 10             	shl    $0x10,%eax
    20fe:	41 c1 e4 08          	shl    $0x8,%r12d
    2102:	25 00 00 ff 00       	and    $0xff0000,%eax
    2107:	45 0f b7 e4          	movzwl %r12w,%r12d
    210b:	44 09 e0             	or     %r12d,%eax
    210e:	09 d8                	or     %ebx,%eax
    2110:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2114:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    2118:	8b 03                	mov    (%rbx),%eax
    211a:	0f b7 1b             	movzwl (%rbx),%ebx
    211d:	c1 e8 10             	shr    $0x10,%eax
    2120:	66 41 89 5c 13 0f    	mov    %bx,0xf(%r11,%rdx,1)
    2126:	41 88 44 13 11       	mov    %al,0x11(%r11,%rdx,1)
    212b:	4d 39 c1             	cmp    %r8,%r9
    212e:	73 70                	jae    21a0 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1120>
    2130:	49 8d 4c 13 12       	lea    0x12(%r11,%rdx,1),%rcx
    2135:	49 8d 54 12 12       	lea    0x12(%r10,%rdx,1),%rdx
    213a:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    213e:	44 0f b6 42 02       	movzbl 0x2(%rdx),%r8d
    2143:	c1 e0 08             	shl    $0x8,%eax
    2146:	41 c1 e0 10          	shl    $0x10,%r8d
    214a:	44 09 c0             	or     %r8d,%eax
    214d:	44 0f b6 02          	movzbl (%rdx),%r8d
    2151:	0f b6 d4             	movzbl %ah,%edx
    2154:	c1 e8 10             	shr    $0x10,%eax
    2157:	29 d0                	sub    %edx,%eax
    2159:	44 29 c2             	sub    %r8d,%edx
    215c:	c1 e0 10             	shl    $0x10,%eax
    215f:	c1 e2 08             	shl    $0x8,%edx
    2162:	25 00 00 ff 00       	and    $0xff0000,%eax
    2167:	0f b7 d2             	movzwl %dx,%edx
    216a:	09 d0                	or     %edx,%eax
    216c:	44 09 c0             	or     %r8d,%eax
    216f:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2173:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    2177:	8b 02                	mov    (%rdx),%eax
    2179:	0f b7 12             	movzwl (%rdx),%edx
    217c:	c1 e8 10             	shr    $0x10,%eax
    217f:	66 89 11             	mov    %dx,(%rcx)
    2182:	88 41 02             	mov    %al,0x2(%rcx)
    2185:	c5 f8 77             	vzeroupper
    2188:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    218c:	5b                   	pop    %rbx
    218d:	41 5c                	pop    %r12
    218f:	41 5d                	pop    %r13
    2191:	41 5e                	pop    %r14
    2193:	41 5f                	pop    %r15
    2195:	5d                   	pop    %rbp
    2196:	c3                   	ret
    2197:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    219e:	00 00 
    21a0:	c5 f8 77             	vzeroupper
    21a3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    21a7:	5b                   	pop    %rbx
    21a8:	41 5c                	pop    %r12
    21aa:	41 5d                	pop    %r13
    21ac:	41 5e                	pop    %r14
    21ae:	41 5f                	pop    %r15
    21b0:	5d                   	pop    %rbp
    21b1:	c3                   	ret
    21b2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    21b8:	4c 89 fe             	mov    %r15,%rsi
    21bb:	4d 89 c1             	mov    %r8,%r9
    21be:	e9 b7 fb ff ff       	jmp    1d7a <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcfa>
    21c3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    21c8:	c3                   	ret
    21c9:	48 8d 41 28          	lea    0x28(%rcx),%rax
    21cd:	49 89 c9             	mov    %rcx,%r9
    21d0:	e9 9b f7 ff ff       	jmp    1970 <jshc_channel::avx2_chain_chroma_delta_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8f0>
