
artifacts/skylake-batchspan-linux-build-v1/CMakeFiles/jshc_skylake_batchspan.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 73 0f 00 00    	je     f80 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf80>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
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
      89:	0f 84 e1 0e 00 00    	je     f70 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf70>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 df 0e 00 00    	jb     f81 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf81>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # ae <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # b6 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	48 01 d0             	add    %rdx,%rax
      b9:	eb 08                	jmp    c3 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc3>
      bb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      c0:	4d 89 c1             	mov    %r8,%r9
      c3:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      ca:	4c 39 c1             	cmp    %r8,%rcx
      cd:	72 1c                	jb     eb <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb>
      cf:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      d6:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      dd:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
      e4:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
      eb:	44 8b 60 0c          	mov    0xc(%rax),%r12d
      ef:	44 8b 70 12          	mov    0x12(%rax),%r14d
      f3:	44 8b 00             	mov    (%rax),%r8d
      f6:	44 8b 58 06          	mov    0x6(%rax),%r11d
      fa:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     101:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     108:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     10d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     112:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     119:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     120:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     124:	44 8b 70 15          	mov    0x15(%rax),%r14d
     128:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     12e:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     134:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     13b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     142:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     147:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     14c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     151:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     156:	44 8b 40 03          	mov    0x3(%rax),%r8d
     15a:	44 8b 58 09          	mov    0x9(%rax),%r11d
     15e:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     165:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     16c:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     173:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     17a:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     180:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     185:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     18a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     18e:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     193:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     19a:	44 8b 40 18          	mov    0x18(%rax),%r8d
     19e:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1a5:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     1a9:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1b0:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1b7:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     1bc:	44 8b 40 1b          	mov    0x1b(%rax),%r8d
     1c0:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     1c4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     1c9:	44 8b 58 21          	mov    0x21(%rax),%r11d
     1cd:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     1d3:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1da:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     1df:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1e6:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     1eb:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     1f0:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     1f5:	44 8b 60 24          	mov    0x24(%rax),%r12d
     1f9:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     1fd:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     203:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     20a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     211:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     216:	44 8b 60 27          	mov    0x27(%rax),%r12d
     21a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     21f:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
     223:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     22a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     230:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     237:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     23e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     243:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     249:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     24e:	44 8b 40 30          	mov    0x30(%rax),%r8d
     252:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     259:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     25d:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     264:	44 8b 70 42          	mov    0x42(%rax),%r14d
     268:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     26f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     276:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     27b:	44 8b 40 33          	mov    0x33(%rax),%r8d
     27f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     283:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     288:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     28f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     294:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     299:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     29d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2a4:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     2ab:	44 8b 58 36          	mov    0x36(%rax),%r11d
     2af:	44 8b 70 45          	mov    0x45(%rax),%r14d
     2b3:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2ba:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     2bf:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     2c6:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     2ca:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2cf:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     2d4:	44 8b 58 39          	mov    0x39(%rax),%r11d
     2d8:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2df:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     2e5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     2ea:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     2ef:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     2f6:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     2fb:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     300:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     306:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     30a:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     310:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     316:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     31c:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     322:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     329:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     32d:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     334:	44 8b 60 54          	mov    0x54(%rax),%r12d
     338:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     33f:	c4 a3 51 22 2c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm5,%xmm5
     346:	44 8b 40 48          	mov    0x48(%rax),%r8d
     34a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     34e:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     353:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     35a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     35f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     364:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     368:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     36f:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     376:	44 8b 60 57          	mov    0x57(%rax),%r12d
     37a:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     37e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     385:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     38a:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     38e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     395:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     39a:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     3a0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3a5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     3ac:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     3b2:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     3b8:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     3bd:	44 8b 40 4b          	mov    0x4b(%rax),%r8d
     3c1:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     3c6:	44 8b 58 51          	mov    0x51(%rax),%r11d
     3ca:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     3d1:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     3d6:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     3dd:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3e4:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     3ea:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     3ee:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     3f5:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     3fa:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     400:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     406:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     40b:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     40f:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     414:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     41b:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     422:	44 8b 40 60          	mov    0x60(%rax),%r8d
     426:	44 8b 60 6c          	mov    0x6c(%rax),%r12d
     42a:	44 8b 70 72          	mov    0x72(%rax),%r14d
     42e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     435:	44 8b 58 66          	mov    0x66(%rax),%r11d
     439:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     43d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     444:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     44b:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     451:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     456:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     45b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     460:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     467:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     46c:	44 8b 60 6f          	mov    0x6f(%rax),%r12d
     470:	44 8b 70 75          	mov    0x75(%rax),%r14d
     474:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     479:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     47f:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     485:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     48c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     493:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     498:	44 8b 40 63          	mov    0x63(%rax),%r8d
     49c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     4a1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     4a6:	44 8b 58 69          	mov    0x69(%rax),%r11d
     4aa:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4b1:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     4b7:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     4be:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     4c5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     4cc:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     4d1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     4d6:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     4da:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     4df:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     4e6:	44 8b 40 78          	mov    0x78(%rax),%r8d
     4ea:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     4f1:	44 8b 58 7e          	mov    0x7e(%rax),%r11d
     4f5:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4fc:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     503:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     508:	44 8b 40 7b          	mov    0x7b(%rax),%r8d
     50c:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     510:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     515:	44 8b 98 81 00 00 00 	mov    0x81(%rax),%r11d
     51c:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     522:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     529:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     52e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     535:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     53a:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     53f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     544:	44 8b a0 84 00 00 00 	mov    0x84(%rax),%r12d
     54b:	44 8b b0 8a 00 00 00 	mov    0x8a(%rax),%r14d
     552:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     557:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     55e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     565:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     56a:	44 8b a0 87 00 00 00 	mov    0x87(%rax),%r12d
     571:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     576:	44 8b b0 8d 00 00 00 	mov    0x8d(%rax),%r14d
     57d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     584:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     58a:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     591:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     598:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     59d:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     5a3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5a8:	44 8b 98 96 00 00 00 	mov    0x96(%rax),%r11d
     5af:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     5b6:	44 8b a0 9c 00 00 00 	mov    0x9c(%rax),%r12d
     5bd:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     5c4:	44 8b b0 a2 00 00 00 	mov    0xa2(%rax),%r14d
     5cb:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     5d2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5d9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5de:	44 8b 98 99 00 00 00 	mov    0x99(%rax),%r11d
     5e5:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     5e9:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     5ef:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5f6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     5fb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     600:	44 8b a0 9f 00 00 00 	mov    0x9f(%rax),%r12d
     607:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     60e:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     615:	44 8b 80 90 00 00 00 	mov    0x90(%rax),%r8d
     61c:	44 8b b0 a5 00 00 00 	mov    0xa5(%rax),%r14d
     623:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     62a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     62f:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     636:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     63a:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     63f:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     644:	44 8b 80 93 00 00 00 	mov    0x93(%rax),%r8d
     64b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     652:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     658:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     65d:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     662:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     669:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     66e:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     673:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     679:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     67f:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     684:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     68b:	44 8b b0 ba 00 00 00 	mov    0xba(%rax),%r14d
     692:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     699:	44 8b a0 b4 00 00 00 	mov    0xb4(%rax),%r12d
     6a0:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     6a7:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     6ae:	44 8b 98 ae 00 00 00 	mov    0xae(%rax),%r11d
     6b5:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     6b9:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     6bf:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     6c6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     6cb:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     6d0:	44 8b b0 bd 00 00 00 	mov    0xbd(%rax),%r14d
     6d7:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     6de:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     6e5:	44 8b a0 b7 00 00 00 	mov    0xb7(%rax),%r12d
     6ec:	44 8b 80 a8 00 00 00 	mov    0xa8(%rax),%r8d
     6f3:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     6fa:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     6ff:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     704:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     70b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     710:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     716:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     71d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     722:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     728:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     72e:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     733:	44 8b 98 b1 00 00 00 	mov    0xb1(%rax),%r11d
     73a:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     73f:	44 8b 80 ab 00 00 00 	mov    0xab(%rax),%r8d
     746:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     74d:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     752:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     759:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     760:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     765:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     76c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     771:	48 05 c0 00 00 00    	add    $0xc0,%rax
     777:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     77c:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     780:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     786:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     78d:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     794:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     79b:	4d 8d 41 40          	lea    0x40(%r9),%r8
     79f:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     7a4:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     7a9:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     7af:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     7b5:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     7ba:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     7c0:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     7c6:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     7cb:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     7d0:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     7d5:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     7da:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     7e0:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     7e6:	c5 7d e7 88 40 ff ff 	vmovntdq %ymm9,-0xc0(%rax)
     7ed:	ff 
     7ee:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     7f2:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     7f6:	c5 fd e7 b0 60 ff ff 	vmovntdq %ymm6,-0xa0(%rax)
     7fd:	ff 
     7fe:	c5 fd e7 68 80       	vmovntdq %ymm5,-0x80(%rax)
     803:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     807:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     80b:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     811:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     817:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     81d:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     823:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     828:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     82c:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     832:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     838:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     83e:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     844:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     84a:	c5 fd e7 68 a0       	vmovntdq %ymm5,-0x60(%rax)
     84f:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     854:	c5 fd e7 48 e0       	vmovntdq %ymm1,-0x20(%rax)
     859:	4c 39 d1             	cmp    %r10,%rcx
     85c:	0f 83 5e f8 ff ff    	jae    c0 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc0>
     862:	0f ae f8             	sfence
     865:	49 8d 41 68          	lea    0x68(%r9),%rax
     869:	48 39 c1             	cmp    %rax,%rcx
     86c:	0f 82 bc 03 00 00    	jb     c2e <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc2e>
     872:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     876:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 87e <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x87e>
     87d:	00 
     87e:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 886 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x886>
     885:	00 
     886:	48 01 d0             	add    %rdx,%rax
     889:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     890:	44 8b 60 54          	mov    0x54(%rax),%r12d
     894:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     898:	44 8b 48 48          	mov    0x48(%rax),%r9d
     89c:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     8a0:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     8a7:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     8ae:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     8b3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     8b8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     8bf:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     8c6:	44 8b 60 57          	mov    0x57(%rax),%r12d
     8ca:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     8ce:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     8d4:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     8da:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     8e1:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     8e8:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     8ed:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     8f2:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     8f7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     8fc:	44 8b 48 4b          	mov    0x4b(%rax),%r9d
     900:	44 8b 58 51          	mov    0x51(%rax),%r11d
     904:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     90b:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     912:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     919:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     920:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     926:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     92b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     930:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     934:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     939:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
     940:	44 8b 48 30          	mov    0x30(%rax),%r9d
     944:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     94b:	44 8b 58 36          	mov    0x36(%rax),%r11d
     94f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     956:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     95d:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     962:	44 8b 48 33          	mov    0x33(%rax),%r9d
     966:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     96a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     96f:	44 8b 58 39          	mov    0x39(%rax),%r11d
     973:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     979:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     980:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     985:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     98c:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     991:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     996:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     99b:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     99f:	44 8b 70 42          	mov    0x42(%rax),%r14d
     9a3:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     9a8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     9af:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     9b6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     9bb:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     9bf:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9c4:	44 8b 70 45          	mov    0x45(%rax),%r14d
     9c8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     9cf:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     9d5:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     9dc:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     9e3:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     9e8:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     9ee:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     9f3:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     9f7:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     9fe:	44 8b 60 24          	mov    0x24(%rax),%r12d
     a02:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     a09:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     a0d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a14:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a1b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     a20:	44 8b 58 21          	mov    0x21(%rax),%r11d
     a24:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     a28:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     a2e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a35:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a3a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a3f:	44 8b 60 27          	mov    0x27(%rax),%r12d
     a43:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a4a:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     a51:	44 8b 48 18          	mov    0x18(%rax),%r9d
     a55:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
     a59:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a60:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a65:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     a6c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     a70:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a75:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     a7a:	44 8b 48 1b          	mov    0x1b(%rax),%r9d
     a7e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a85:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     a8b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a90:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     a95:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     a9c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     aa1:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     aa6:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     aac:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     ab0:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     ab6:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     abc:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     ac1:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     ac8:	44 8b 70 12          	mov    0x12(%rax),%r14d
     acc:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     ad3:	44 8b 60 0c          	mov    0xc(%rax),%r12d
     ad7:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     ade:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     ae5:	44 8b 58 06          	mov    0x6(%rax),%r11d
     ae9:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     aed:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     af3:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     afa:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     aff:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     b04:	44 8b 70 15          	mov    0x15(%rax),%r14d
     b08:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     b0f:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     b16:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     b1a:	44 8b 08             	mov    (%rax),%r9d
     b1d:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b24:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     b29:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     b2d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     b34:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b39:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     b3f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b46:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     b4b:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     b51:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     b57:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     b5c:	44 8b 58 09          	mov    0x9(%rax),%r11d
     b60:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     b65:	44 8b 48 03          	mov    0x3(%rax),%r9d
     b69:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     b70:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     b75:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
     b7c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     b83:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     b88:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     b8c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b93:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b98:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     b9e:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     ba3:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     ba7:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     bad:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     bb3:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     bba:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     bc0:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     bc7:	4d 8d 48 48          	lea    0x48(%r8),%r9
     bcb:	49 83 c0 20          	add    $0x20,%r8
     bcf:	48 83 c0 60          	add    $0x60,%rax
     bd3:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     bd7:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
     bdb:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     be1:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     be7:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
     bed:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
     bf1:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     bf6:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
     bfc:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     c01:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     c05:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     c0b:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     c10:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
     c16:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     c1b:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     c20:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     c25:	4c 39 c9             	cmp    %r9,%rcx
     c28:	0f 83 62 fc ff ff    	jae    890 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x890>
     c2e:	4d 8d 48 08          	lea    0x8(%r8),%r9
     c32:	4c 39 c9             	cmp    %r9,%rcx
     c35:	0f 82 2d 01 00 00    	jb     d68 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd68>
     c3b:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     c3f:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # c47 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc47>
     c46:	00 
     c47:	48 01 d0             	add    %rdx,%rax
     c4a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     c50:	48 8b 18             	mov    (%rax),%rbx
     c53:	4c 8b 40 08          	mov    0x8(%rax),%r8
     c57:	48 83 c0 18          	add    $0x18,%rax
     c5b:	4c 8b 68 f8          	mov    -0x8(%rax),%r13
     c5f:	49 89 da             	mov    %rbx,%r10
     c62:	4d 89 c6             	mov    %r8,%r14
     c65:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     c6c:	45 89 ef             	mov    %r13d,%r15d
     c6f:	49 c1 ee 20          	shr    $0x20,%r14
     c73:	46 0f b6 1c 17       	movzbl (%rdi,%r10,1),%r11d
     c78:	49 89 da             	mov    %rbx,%r10
     c7b:	48 c1 eb 30          	shr    $0x30,%rbx
     c7f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     c86:	41 c1 e7 08          	shl    $0x8,%r15d
     c8a:	49 89 dc             	mov    %rbx,%r12
     c8d:	44 89 c3             	mov    %r8d,%ebx
     c90:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     c95:	c1 e3 10             	shl    $0x10,%ebx
     c98:	49 c1 ea 18          	shr    $0x18,%r10
     c9c:	44 09 e3             	or     %r12d,%ebx
     c9f:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     ca5:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     cac:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     cb2:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     cb7:	44 0f b6 24 1f       	movzbl (%rdi,%rbx,1),%r12d
     cbc:	44 89 c3             	mov    %r8d,%ebx
     cbf:	49 c1 e8 38          	shr    $0x38,%r8
     cc3:	45 09 f8             	or     %r15d,%r8d
     cc6:	4d 89 ef             	mov    %r13,%r15
     cc9:	49 c1 ed 28          	shr    $0x28,%r13
     ccd:	49 c1 ef 10          	shr    $0x10,%r15
     cd1:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     cd8:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     cdd:	c1 eb 08             	shr    $0x8,%ebx
     ce0:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     ce7:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     cec:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     cf0:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     cf5:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
     cfb:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     d02:	4d 89 c8             	mov    %r9,%r8
     d05:	49 83 c1 08          	add    $0x8,%r9
     d09:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     d0f:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
     d16:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     d1d:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     d21:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     d27:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
     d2e:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     d32:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     d38:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     d3d:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     d41:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     d47:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     d4c:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     d51:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     d55:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     d5a:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     d5f:	4c 39 c9             	cmp    %r9,%rcx
     d62:	0f 83 e8 fe ff ff    	jae    c50 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc50>
     d68:	49 39 c8             	cmp    %rcx,%r8
     d6b:	0f 83 ef 01 00 00    	jae    f60 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     d71:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     d75:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     d79:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d7e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d83:	c1 e0 08             	shl    $0x8,%eax
     d86:	41 c1 e3 10          	shl    $0x10,%r11d
     d8a:	44 09 d8             	or     %r11d,%eax
     d8d:	45 0f b6 1a          	movzbl (%r10),%r11d
     d91:	44 09 d8             	or     %r11d,%eax
     d94:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d98:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d9c:	41 8b 03             	mov    (%r11),%eax
     d9f:	45 0f b7 1b          	movzwl (%r11),%r11d
     da3:	c1 e8 10             	shr    $0x10,%eax
     da6:	66 45 89 1a          	mov    %r11w,(%r10)
     daa:	41 88 42 02          	mov    %al,0x2(%r10)
     dae:	49 8d 40 01          	lea    0x1(%r8),%rax
     db2:	48 39 c8             	cmp    %rcx,%rax
     db5:	0f 83 a5 01 00 00    	jae    f60 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     dbb:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     dc0:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     dc5:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     dca:	c1 e0 08             	shl    $0x8,%eax
     dcd:	41 c1 e3 10          	shl    $0x10,%r11d
     dd1:	44 09 d8             	or     %r11d,%eax
     dd4:	45 0f b6 1a          	movzbl (%r10),%r11d
     dd8:	44 09 d8             	or     %r11d,%eax
     ddb:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     ddf:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     de3:	41 8b 03             	mov    (%r11),%eax
     de6:	45 0f b7 1b          	movzwl (%r11),%r11d
     dea:	c1 e8 10             	shr    $0x10,%eax
     ded:	66 45 89 1a          	mov    %r11w,(%r10)
     df1:	41 88 42 02          	mov    %al,0x2(%r10)
     df5:	49 8d 40 02          	lea    0x2(%r8),%rax
     df9:	48 39 c8             	cmp    %rcx,%rax
     dfc:	0f 83 5e 01 00 00    	jae    f60 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     e02:	4e 8d 54 0a 06       	lea    0x6(%rdx,%r9,1),%r10
     e07:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     e0c:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e11:	c1 e0 08             	shl    $0x8,%eax
     e14:	41 c1 e3 10          	shl    $0x10,%r11d
     e18:	44 09 d8             	or     %r11d,%eax
     e1b:	45 0f b6 1a          	movzbl (%r10),%r11d
     e1f:	44 09 d8             	or     %r11d,%eax
     e22:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e26:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e2a:	41 8b 03             	mov    (%r11),%eax
     e2d:	45 0f b7 1b          	movzwl (%r11),%r11d
     e31:	c1 e8 10             	shr    $0x10,%eax
     e34:	66 45 89 1a          	mov    %r11w,(%r10)
     e38:	41 88 42 02          	mov    %al,0x2(%r10)
     e3c:	49 8d 40 03          	lea    0x3(%r8),%rax
     e40:	48 39 c8             	cmp    %rcx,%rax
     e43:	0f 83 17 01 00 00    	jae    f60 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     e49:	4e 8d 54 0a 09       	lea    0x9(%rdx,%r9,1),%r10
     e4e:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e53:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e58:	c1 e0 10             	shl    $0x10,%eax
     e5b:	41 c1 e3 08          	shl    $0x8,%r11d
     e5f:	44 09 d8             	or     %r11d,%eax
     e62:	45 0f b6 1a          	movzbl (%r10),%r11d
     e66:	44 09 d8             	or     %r11d,%eax
     e69:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e6d:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e71:	41 8b 03             	mov    (%r11),%eax
     e74:	45 0f b7 1b          	movzwl (%r11),%r11d
     e78:	c1 e8 10             	shr    $0x10,%eax
     e7b:	66 45 89 1a          	mov    %r11w,(%r10)
     e7f:	41 88 42 02          	mov    %al,0x2(%r10)
     e83:	49 8d 40 04          	lea    0x4(%r8),%rax
     e87:	48 39 c8             	cmp    %rcx,%rax
     e8a:	0f 83 d0 00 00 00    	jae    f60 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     e90:	4e 8d 54 0a 0c       	lea    0xc(%rdx,%r9,1),%r10
     e95:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e9a:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e9f:	c1 e0 10             	shl    $0x10,%eax
     ea2:	41 c1 e3 08          	shl    $0x8,%r11d
     ea6:	44 09 d8             	or     %r11d,%eax
     ea9:	45 0f b6 1a          	movzbl (%r10),%r11d
     ead:	44 09 d8             	or     %r11d,%eax
     eb0:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     eb4:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     eb8:	41 8b 03             	mov    (%r11),%eax
     ebb:	45 0f b7 1b          	movzwl (%r11),%r11d
     ebf:	c1 e8 10             	shr    $0x10,%eax
     ec2:	66 45 89 1a          	mov    %r11w,(%r10)
     ec6:	41 88 42 02          	mov    %al,0x2(%r10)
     eca:	49 8d 40 05          	lea    0x5(%r8),%rax
     ece:	48 39 c8             	cmp    %rcx,%rax
     ed1:	0f 83 89 00 00 00    	jae    f60 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     ed7:	4e 8d 54 0a 0f       	lea    0xf(%rdx,%r9,1),%r10
     edc:	49 83 c0 06          	add    $0x6,%r8
     ee0:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     ee5:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     eea:	c1 e0 10             	shl    $0x10,%eax
     eed:	41 c1 e3 08          	shl    $0x8,%r11d
     ef1:	44 09 d8             	or     %r11d,%eax
     ef4:	45 0f b6 1a          	movzbl (%r10),%r11d
     ef8:	44 09 d8             	or     %r11d,%eax
     efb:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     eff:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f03:	41 8b 03             	mov    (%r11),%eax
     f06:	45 0f b7 1b          	movzwl (%r11),%r11d
     f0a:	c1 e8 10             	shr    $0x10,%eax
     f0d:	66 45 89 1a          	mov    %r11w,(%r10)
     f11:	41 88 42 02          	mov    %al,0x2(%r10)
     f15:	49 39 c8             	cmp    %rcx,%r8
     f18:	73 46                	jae    f60 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     f1a:	4a 8d 54 0a 12       	lea    0x12(%rdx,%r9,1),%rdx
     f1f:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     f23:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     f27:	c1 e0 08             	shl    $0x8,%eax
     f2a:	c1 e1 10             	shl    $0x10,%ecx
     f2d:	09 c8                	or     %ecx,%eax
     f2f:	0f b6 0a             	movzbl (%rdx),%ecx
     f32:	09 c8                	or     %ecx,%eax
     f34:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f38:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     f3c:	8b 01                	mov    (%rcx),%eax
     f3e:	0f b7 09             	movzwl (%rcx),%ecx
     f41:	c1 e8 10             	shr    $0x10,%eax
     f44:	66 89 0a             	mov    %cx,(%rdx)
     f47:	88 42 02             	mov    %al,0x2(%rdx)
     f4a:	c5 f8 77             	vzeroupper
     f4d:	5b                   	pop    %rbx
     f4e:	41 5c                	pop    %r12
     f50:	41 5d                	pop    %r13
     f52:	41 5e                	pop    %r14
     f54:	41 5f                	pop    %r15
     f56:	5d                   	pop    %rbp
     f57:	c3                   	ret
     f58:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     f5f:	00 
     f60:	c5 f8 77             	vzeroupper
     f63:	5b                   	pop    %rbx
     f64:	41 5c                	pop    %r12
     f66:	41 5d                	pop    %r13
     f68:	41 5e                	pop    %r14
     f6a:	41 5f                	pop    %r15
     f6c:	5d                   	pop    %rbp
     f6d:	c3                   	ret
     f6e:	66 90                	xchg   %ax,%ax
     f70:	49 89 c8             	mov    %rcx,%r8
     f73:	e9 b6 fc ff ff       	jmp    c2e <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc2e>
     f78:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     f7f:	00 
     f80:	c3                   	ret
     f81:	49 8d 41 28          	lea    0x28(%r9),%rax
     f85:	4d 89 c8             	mov    %r9,%r8
     f88:	e9 dc f8 ff ff       	jmp    869 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x869>
     f8d:	0f 1f 00             	nopl   (%rax)

0000000000000f90 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     f90:	f3 0f 1e fa          	endbr64
     f94:	4d 85 c0             	test   %r8,%r8
     f97:	0f 84 53 10 00 00    	je     1ff0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1060>
     f9d:	55                   	push   %rbp
     f9e:	b8 00 04 00 00       	mov    $0x400,%eax
     fa3:	48 89 e5             	mov    %rsp,%rbp
     fa6:	41 57                	push   %r15
     fa8:	41 56                	push   %r14
     faa:	41 55                	push   %r13
     fac:	41 54                	push   %r12
     fae:	49 89 cc             	mov    %rcx,%r12
     fb1:	53                   	push   %rbx
     fb2:	48 89 d3             	mov    %rdx,%rbx
     fb5:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     fb9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     fbd:	48 39 c2             	cmp    %rax,%rdx
     fc0:	48 0f 47 d0          	cmova  %rax,%rdx
     fc4:	31 c0                	xor    %eax,%eax
     fc6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     fcd:	00 00 00 
     fd0:	0f 18 04 03          	prefetchnta (%rbx,%rax,1)
     fd4:	48 83 c0 40          	add    $0x40,%rax
     fd8:	48 39 d0             	cmp    %rdx,%rax
     fdb:	72 f3                	jb     fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     fdd:	49 89 d9             	mov    %rbx,%r9
     fe0:	4c 89 e2             	mov    %r12,%rdx
     fe3:	31 c9                	xor    %ecx,%ecx
     fe5:	eb 53                	jmp    103a <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
     fe7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
     fee:	00 00 
     ff0:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     ff5:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     ffa:	48 ff c1             	inc    %rcx
     ffd:	48 83 c2 03          	add    $0x3,%rdx
    1001:	49 83 c1 03          	add    $0x3,%r9
    1005:	41 c1 e2 10          	shl    $0x10,%r10d
    1009:	c1 e0 08             	shl    $0x8,%eax
    100c:	44 09 d0             	or     %r10d,%eax
    100f:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
    1014:	44 09 d0             	or     %r10d,%eax
    1017:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    101b:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
    101f:	41 8b 02             	mov    (%r10),%eax
    1022:	45 0f b7 12          	movzwl (%r10),%r10d
    1026:	c1 e8 10             	shr    $0x10,%eax
    1029:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
    102e:	88 42 ff             	mov    %al,-0x1(%rdx)
    1031:	49 39 c8             	cmp    %rcx,%r8
    1034:	0f 84 ae 0f 00 00    	je     1fe8 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1058>
    103a:	f6 c2 3f             	test   $0x3f,%dl
    103d:	75 b1                	jne    ff0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    103f:	48 8d 41 48          	lea    0x48(%rcx),%rax
    1043:	49 39 c0             	cmp    %rax,%r8
    1046:	0f 82 a5 0f 00 00    	jb     1ff1 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1061>
    104c:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    1050:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1058 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc8>
    1057:	00 
    1058:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1060 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd0>
    105f:	00 
    1060:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1065:	49 8d 14 04          	lea    (%r12,%rax,1),%rdx
    1069:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    106e:	48 8d 84 03 00 04 00 	lea    0x400(%rbx,%rax,1),%rax
    1075:	00 
    1076:	eb 0b                	jmp    1083 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
    1078:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    107f:	00 
    1080:	4c 89 c9             	mov    %r9,%rcx
    1083:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    108a:	4d 39 c8             	cmp    %r9,%r8
    108d:	72 15                	jb     10a4 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
    108f:	0f 18 00             	prefetchnta (%rax)
    1092:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1096:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    109d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    10a4:	44 8b 88 00 fc ff ff 	mov    -0x400(%rax),%r9d
    10ab:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10b2:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    10b7:	44 8b 88 03 fc ff ff 	mov    -0x3fd(%rax),%r9d
    10be:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10c5:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
    10cb:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    10d0:	44 8b 88 06 fc ff ff 	mov    -0x3fa(%rax),%r9d
    10d7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10de:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
    10e5:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    10ea:	44 8b 88 09 fc ff ff 	mov    -0x3f7(%rax),%r9d
    10f1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10f8:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    10fd:	44 8b 88 0c fc ff ff 	mov    -0x3f4(%rax),%r9d
    1104:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    110b:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1110:	44 8b 88 0f fc ff ff 	mov    -0x3f1(%rax),%r9d
    1117:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    111e:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1124:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1129:	44 8b 88 12 fc ff ff 	mov    -0x3ee(%rax),%r9d
    1130:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1137:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    113e:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1143:	44 8b 88 15 fc ff ff 	mov    -0x3eb(%rax),%r9d
    114a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1151:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1157:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    115c:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1163:	44 8b 88 18 fc ff ff 	mov    -0x3e8(%rax),%r9d
    116a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1171:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1175:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    117b:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1180:	44 8b 88 1b fc ff ff 	mov    -0x3e5(%rax),%r9d
    1187:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    118e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1195:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    119a:	44 8b 88 1e fc ff ff 	mov    -0x3e2(%rax),%r9d
    11a1:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    11a5:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    11ab:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11b2:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    11b7:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    11bc:	44 8b 88 21 fc ff ff 	mov    -0x3df(%rax),%r9d
    11c3:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
    11c8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11cf:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    11d4:	44 8b 88 24 fc ff ff 	mov    -0x3dc(%rax),%r9d
    11db:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
    11e1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11e8:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    11ed:	44 8b 88 27 fc ff ff 	mov    -0x3d9(%rax),%r9d
    11f4:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
    11fb:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1202:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1208:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    120d:	44 8b 88 2a fc ff ff 	mov    -0x3d6(%rax),%r9d
    1214:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    121b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1222:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1227:	44 8b 88 2d fc ff ff 	mov    -0x3d3(%rax),%r9d
    122e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1235:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    123b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1240:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1247:	44 8b 88 30 fc ff ff 	mov    -0x3d0(%rax),%r9d
    124e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1255:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1259:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    125f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1264:	44 8b 88 33 fc ff ff 	mov    -0x3cd(%rax),%r9d
    126b:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1272:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1279:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    127e:	44 8b 88 36 fc ff ff 	mov    -0x3ca(%rax),%r9d
    1285:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    1289:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    128f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1296:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    129b:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    12a0:	44 8b 88 39 fc ff ff 	mov    -0x3c7(%rax),%r9d
    12a7:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    12ac:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    12b0:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    12b6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12bd:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    12c3:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    12c8:	44 8b 88 3c fc ff ff 	mov    -0x3c4(%rax),%r9d
    12cf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12d6:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    12db:	44 8b 88 3f fc ff ff 	mov    -0x3c1(%rax),%r9d
    12e2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12e9:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    12ee:	44 8b 88 42 fc ff ff 	mov    -0x3be(%rax),%r9d
    12f5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12fc:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1301:	44 8b 88 45 fc ff ff 	mov    -0x3bb(%rax),%r9d
    1308:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    130f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1314:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    131a:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    1320:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1326:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    132d:	44 8b 88 48 fc ff ff 	mov    -0x3b8(%rax),%r9d
    1334:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    133b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1342:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1349:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    134e:	44 8b 88 4b fc ff ff 	mov    -0x3b5(%rax),%r9d
    1355:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1359:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    135f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1366:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
    136c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1371:	44 8b 88 4e fc ff ff 	mov    -0x3b2(%rax),%r9d
    1378:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    137f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1386:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
    138d:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1392:	44 8b 88 51 fc ff ff 	mov    -0x3af(%rax),%r9d
    1399:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    139d:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    13a3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13aa:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    13af:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    13b4:	44 8b 88 54 fc ff ff 	mov    -0x3ac(%rax),%r9d
    13bb:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    13c0:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    13c4:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    13ca:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13d1:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    13d7:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    13dc:	44 8b 88 57 fc ff ff 	mov    -0x3a9(%rax),%r9d
    13e3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13ea:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    13f0:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    13f5:	44 8b 88 5a fc ff ff 	mov    -0x3a6(%rax),%r9d
    13fc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1403:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    140a:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    140f:	44 8b 88 5d fc ff ff 	mov    -0x3a3(%rax),%r9d
    1416:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    141d:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1423:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1428:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    142f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1433:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1439:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1440:	44 8b 88 60 fc ff ff 	mov    -0x3a0(%rax),%r9d
    1447:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    144e:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    1452:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1457:	44 8b 88 63 fc ff ff 	mov    -0x39d(%rax),%r9d
    145e:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    1464:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    1469:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1470:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
    1476:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    147b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1480:	44 8b 88 66 fc ff ff 	mov    -0x39a(%rax),%r9d
    1487:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    148e:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
    1495:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    149a:	44 8b 88 69 fc ff ff 	mov    -0x397(%rax),%r9d
    14a1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14a8:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    14ad:	44 8b 88 6c fc ff ff 	mov    -0x394(%rax),%r9d
    14b4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14bb:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    14c0:	44 8b 88 6f fc ff ff 	mov    -0x391(%rax),%r9d
    14c7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14ce:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    14d4:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    14d9:	44 8b 88 72 fc ff ff 	mov    -0x38e(%rax),%r9d
    14e0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14e7:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    14ee:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    14f3:	44 8b 88 75 fc ff ff 	mov    -0x38b(%rax),%r9d
    14fa:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1501:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1507:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    150c:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1513:	44 8b 88 78 fc ff ff 	mov    -0x388(%rax),%r9d
    151a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1521:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1525:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    152b:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1530:	44 8b 88 7b fc ff ff 	mov    -0x385(%rax),%r9d
    1537:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    153e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1545:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    154a:	44 8b 88 7e fc ff ff 	mov    -0x382(%rax),%r9d
    1551:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    1555:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    155b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1562:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    1567:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    156c:	44 8b 88 81 fc ff ff 	mov    -0x37f(%rax),%r9d
    1573:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    1578:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    157f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1584:	44 8b 88 84 fc ff ff 	mov    -0x37c(%rax),%r9d
    158b:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1591:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1598:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    159d:	44 8b 88 87 fc ff ff 	mov    -0x379(%rax),%r9d
    15a4:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    15ab:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15b2:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    15b8:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    15bd:	44 8b 88 8a fc ff ff 	mov    -0x376(%rax),%r9d
    15c4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15cb:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    15d2:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    15d7:	44 8b 88 8d fc ff ff 	mov    -0x373(%rax),%r9d
    15de:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15e5:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    15eb:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    15f0:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    15f7:	44 8b 88 90 fc ff ff 	mov    -0x370(%rax),%r9d
    15fe:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1605:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1609:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    160f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1614:	44 8b 88 93 fc ff ff 	mov    -0x36d(%rax),%r9d
    161b:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1622:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1629:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    162e:	44 8b 88 96 fc ff ff 	mov    -0x36a(%rax),%r9d
    1635:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1639:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    163f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1646:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    164b:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1650:	44 8b 88 99 fc ff ff 	mov    -0x367(%rax),%r9d
    1657:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    165c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1663:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1668:	44 8b 88 9c fc ff ff 	mov    -0x364(%rax),%r9d
    166f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1676:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    167b:	44 8b 88 9f fc ff ff 	mov    -0x361(%rax),%r9d
    1682:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1689:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    168e:	44 8b 88 a2 fc ff ff 	mov    -0x35e(%rax),%r9d
    1695:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    169c:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    16a1:	44 8b 88 a5 fc ff ff 	mov    -0x35b(%rax),%r9d
    16a8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16af:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    16b4:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    16ba:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    16c0:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    16c6:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    16cd:	44 8b 88 a8 fc ff ff 	mov    -0x358(%rax),%r9d
    16d4:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    16db:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    16e2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16e9:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    16ee:	44 8b 88 ab fc ff ff 	mov    -0x355(%rax),%r9d
    16f5:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    16fa:	c4 21 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm10
    1700:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1707:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    170c:	44 8b 88 ae fc ff ff 	mov    -0x352(%rax),%r9d
    1713:	c4 63 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm10,%xmm10
    171a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1721:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1726:	44 8b 88 b1 fc ff ff 	mov    -0x34f(%rax),%r9d
    172d:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1732:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1738:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    173e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1745:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    174a:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    174f:	44 8b 88 b4 fc ff ff 	mov    -0x34c(%rax),%r9d
    1756:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    175b:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1762:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1769:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1770:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1775:	44 8b 88 b7 fc ff ff 	mov    -0x349(%rax),%r9d
    177c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1783:	c4 21 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm10
    1789:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    178e:	44 8b 88 ba fc ff ff 	mov    -0x346(%rax),%r9d
    1795:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    179c:	c4 23 29 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm10,%xmm10
    17a3:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    17a8:	44 8b 88 bd fc ff ff 	mov    -0x343(%rax),%r9d
    17af:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17b6:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    17bc:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    17c3:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    17c8:	c4 23 21 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm11,%xmm11
    17cf:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    17d3:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    17d8:	c4 21 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm11
    17de:	c4 63 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm11,%xmm11
    17e5:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    17ea:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    17ef:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    17f5:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    17fb:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    1800:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    1806:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    180c:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1811:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    1816:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    181b:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1820:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    1826:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    182c:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
    1833:	ff 
    1834:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    1838:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    183c:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
    1843:	ff 
    1844:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
    1849:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    184d:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    1851:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1857:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    185d:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1863:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1869:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    186e:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1872:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    1878:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    187e:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    1884:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    188a:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1890:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
    1895:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    189a:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
    189f:	48 05 c0 00 00 00    	add    $0xc0,%rax
    18a5:	4d 39 d0             	cmp    %r10,%r8
    18a8:	0f 83 d2 f7 ff ff    	jae    1080 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    18ae:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    18b3:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    18b8:	48 8d 41 68          	lea    0x68(%rcx),%rax
    18bc:	0f ae f8             	sfence
    18bf:	49 39 c0             	cmp    %rax,%r8
    18c2:	0f 82 90 03 00 00    	jb     1c58 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    18c8:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    18cc:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 18d4 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x944>
    18d3:	00 
    18d4:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 18dc <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x94c>
    18db:	00 
    18dc:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    18e1:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    18e6:	48 8d 04 13          	lea    (%rbx,%rdx,1),%rax
    18ea:	4c 01 e2             	add    %r12,%rdx
    18ed:	0f 1f 00             	nopl   (%rax)
    18f0:	8b 48 48             	mov    0x48(%rax),%ecx
    18f3:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    18f9:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    18fe:	8b 48 4b             	mov    0x4b(%rax),%ecx
    1901:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1907:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    190d:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1912:	8b 48 4e             	mov    0x4e(%rax),%ecx
    1915:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    191b:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    1922:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1927:	8b 48 51             	mov    0x51(%rax),%ecx
    192a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1930:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1934:	8b 48 54             	mov    0x54(%rax),%ecx
    1937:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    193d:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1942:	8b 48 57             	mov    0x57(%rax),%ecx
    1945:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    194b:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1951:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1956:	8b 48 5a             	mov    0x5a(%rax),%ecx
    1959:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    195f:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1966:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    196b:	8b 48 5d             	mov    0x5d(%rax),%ecx
    196e:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1974:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    197a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    197e:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    1985:	8b 48 30             	mov    0x30(%rax),%ecx
    1988:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    198e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1992:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1998:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    199d:	8b 48 33             	mov    0x33(%rax),%ecx
    19a0:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    19a7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19ad:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    19b2:	8b 48 36             	mov    0x36(%rax),%ecx
    19b5:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    19b9:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    19bf:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19c5:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    19ca:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    19cf:	8b 48 39             	mov    0x39(%rax),%ecx
    19d2:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    19d7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19dd:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    19e1:	8b 48 3c             	mov    0x3c(%rax),%ecx
    19e4:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    19ea:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19f0:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    19f5:	8b 48 3f             	mov    0x3f(%rax),%ecx
    19f8:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    19ff:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a05:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1a0b:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1a10:	8b 48 42             	mov    0x42(%rax),%ecx
    1a13:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a19:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1a20:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1a25:	8b 48 45             	mov    0x45(%rax),%ecx
    1a28:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a2e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1a34:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1a38:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1a3f:	8b 48 18             	mov    0x18(%rax),%ecx
    1a42:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a48:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1a4c:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1a52:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1a57:	8b 48 1b             	mov    0x1b(%rax),%ecx
    1a5a:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1a61:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a67:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1a6c:	8b 48 1e             	mov    0x1e(%rax),%ecx
    1a6f:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1a73:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1a79:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a7f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1a84:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1a89:	8b 48 21             	mov    0x21(%rax),%ecx
    1a8c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1a91:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    1a95:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1a9b:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1aa1:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1aa5:	8b 48 24             	mov    0x24(%rax),%ecx
    1aa8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1aae:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1ab3:	8b 48 27             	mov    0x27(%rax),%ecx
    1ab6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1abc:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1ac1:	8b 48 2a             	mov    0x2a(%rax),%ecx
    1ac4:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1aca:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1acf:	8b 48 2d             	mov    0x2d(%rax),%ecx
    1ad2:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1ad8:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1adc:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1ae2:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1ae8:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1aee:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    1af5:	8b 08                	mov    (%rax),%ecx
    1af7:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    1afe:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1b05:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b0b:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1b10:	8b 48 03             	mov    0x3(%rax),%ecx
    1b13:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    1b17:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    1b1d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b23:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1b28:	8b 48 06             	mov    0x6(%rax),%ecx
    1b2b:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    1b32:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b38:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1b3d:	8b 48 09             	mov    0x9(%rax),%ecx
    1b40:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1b44:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1b4a:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1b50:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b56:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1b5b:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1b5f:	8b 48 0c             	mov    0xc(%rax),%ecx
    1b62:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1b67:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1b6e:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1b72:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1b78:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b7e:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1b84:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1b89:	8b 48 0f             	mov    0xf(%rax),%ecx
    1b8c:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1b92:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b98:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    1b9e:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1ba3:	8b 48 12             	mov    0x12(%rax),%ecx
    1ba6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1bac:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    1bb3:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1bb8:	8b 48 15             	mov    0x15(%rax),%ecx
    1bbb:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1bc1:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    1bc7:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1bcb:	c4 e3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm7,%xmm7
    1bd2:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1bd6:	49 83 c1 20          	add    $0x20,%r9
    1bda:	48 83 c0 60          	add    $0x60,%rax
    1bde:	48 83 c2 60          	add    $0x60,%rdx
    1be2:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    1be6:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    1bec:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    1bf3:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    1bf7:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    1bfb:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1c01:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    1c07:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    1c0d:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1c11:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1c16:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    1c1c:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1c21:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1c25:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1c2b:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1c30:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    1c36:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1c3b:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1c40:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1c45:	49 39 c8             	cmp    %rcx,%r8
    1c48:	0f 83 a2 fc ff ff    	jae    18f0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x960>
    1c4e:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1c53:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1c58:	4d 8d 59 08          	lea    0x8(%r9),%r11
    1c5c:	4d 39 d8             	cmp    %r11,%r8
    1c5f:	0f 82 4d 01 00 00    	jb     1db2 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe22>
    1c65:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1c6a:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    1c6e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1c76 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xce6>
    1c75:	00 
    1c76:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    1c7b:	4a 8d 0c 13          	lea    (%rbx,%r10,1),%rcx
    1c7f:	4d 01 e2             	add    %r12,%r10
    1c82:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1c88:	4c 8b 21             	mov    (%rcx),%r12
    1c8b:	48 8b 41 08          	mov    0x8(%rcx),%rax
    1c8f:	49 83 c2 18          	add    $0x18,%r10
    1c93:	48 83 c1 18          	add    $0x18,%rcx
    1c97:	48 8b 51 f8          	mov    -0x8(%rcx),%rdx
    1c9b:	4d 89 e1             	mov    %r12,%r9
    1c9e:	4d 89 e5             	mov    %r12,%r13
    1ca1:	49 89 c6             	mov    %rax,%r14
    1ca4:	49 c1 ed 30          	shr    $0x30,%r13
    1ca8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1caf:	41 89 d7             	mov    %edx,%r15d
    1cb2:	49 c1 ee 20          	shr    $0x20,%r14
    1cb6:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1cbb:	4d 89 e1             	mov    %r12,%r9
    1cbe:	41 89 c4             	mov    %eax,%r12d
    1cc1:	41 c1 e7 08          	shl    $0x8,%r15d
    1cc5:	41 c1 e4 10          	shl    $0x10,%r12d
    1cc9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1cd0:	49 c1 e9 18          	shr    $0x18,%r9
    1cd4:	45 09 ec             	or     %r13d,%r12d
    1cd7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1cdc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ce3:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    1ce8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1cef:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1cf4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1cf9:	41 89 c4             	mov    %eax,%r12d
    1cfc:	48 c1 e8 38          	shr    $0x38,%rax
    1d00:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1d06:	41 09 c7             	or     %eax,%r15d
    1d09:	41 c1 ec 08          	shr    $0x8,%r12d
    1d0d:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1d14:	4d 89 d9             	mov    %r11,%r9
    1d17:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1d1e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1d23:	49 83 c3 08          	add    $0x8,%r11
    1d27:	42 0f b6 04 3f       	movzbl (%rdi,%r15,1),%eax
    1d2c:	49 89 d7             	mov    %rdx,%r15
    1d2f:	48 c1 ea 28          	shr    $0x28,%rdx
    1d33:	49 c1 ef 10          	shr    $0x10,%r15
    1d37:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1d3b:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1d42:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
    1d49:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1d4e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1d54:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
    1d5b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1d5f:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1d65:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1d6c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1d70:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1d76:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1d7b:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1d7f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1d85:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1d8a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1d8f:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1d93:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1d99:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    1d9f:	4d 39 d8             	cmp    %r11,%r8
    1da2:	0f 83 e0 fe ff ff    	jae    1c88 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcf8>
    1da8:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1dad:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1db2:	4d 39 c1             	cmp    %r8,%r9
    1db5:	0f 83 15 02 00 00    	jae    1fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1dbb:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1dbf:	4c 8d 14 03          	lea    (%rbx,%rax,1),%r10
    1dc3:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1dc8:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1dcd:	45 0f b6 12          	movzbl (%r10),%r10d
    1dd1:	c1 e2 08             	shl    $0x8,%edx
    1dd4:	41 c1 e3 10          	shl    $0x10,%r11d
    1dd8:	44 09 da             	or     %r11d,%edx
    1ddb:	44 09 d2             	or     %r10d,%edx
    1dde:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1de2:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    1de6:	41 8b 12             	mov    (%r10),%edx
    1de9:	45 0f b7 12          	movzwl (%r10),%r10d
    1ded:	c1 ea 10             	shr    $0x10,%edx
    1df0:	66 45 89 14 04       	mov    %r10w,(%r12,%rax,1)
    1df5:	41 88 54 04 02       	mov    %dl,0x2(%r12,%rax,1)
    1dfa:	49 8d 51 01          	lea    0x1(%r9),%rdx
    1dfe:	4c 39 c2             	cmp    %r8,%rdx
    1e01:	0f 83 c9 01 00 00    	jae    1fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1e07:	4c 8d 54 03 03       	lea    0x3(%rbx,%rax,1),%r10
    1e0c:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1e11:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1e16:	45 0f b6 12          	movzbl (%r10),%r10d
    1e1a:	41 c1 e3 10          	shl    $0x10,%r11d
    1e1e:	c1 e2 08             	shl    $0x8,%edx
    1e21:	44 09 da             	or     %r11d,%edx
    1e24:	44 09 d2             	or     %r10d,%edx
    1e27:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1e2b:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1e2f:	44 8b 12             	mov    (%rdx),%r10d
    1e32:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1e36:	49 8d 51 02          	lea    0x2(%r9),%rdx
    1e3a:	44 89 d1             	mov    %r10d,%ecx
    1e3d:	66 45 89 5c 04 03    	mov    %r11w,0x3(%r12,%rax,1)
    1e43:	c1 e9 10             	shr    $0x10,%ecx
    1e46:	41 88 4c 04 05       	mov    %cl,0x5(%r12,%rax,1)
    1e4b:	4c 39 c2             	cmp    %r8,%rdx
    1e4e:	0f 83 7c 01 00 00    	jae    1fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1e54:	4c 8d 54 03 06       	lea    0x6(%rbx,%rax,1),%r10
    1e59:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1e5e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1e63:	45 0f b6 12          	movzbl (%r10),%r10d
    1e67:	41 c1 e3 10          	shl    $0x10,%r11d
    1e6b:	c1 e2 08             	shl    $0x8,%edx
    1e6e:	44 09 da             	or     %r11d,%edx
    1e71:	44 09 d2             	or     %r10d,%edx
    1e74:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1e78:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1e7c:	44 8b 12             	mov    (%rdx),%r10d
    1e7f:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1e83:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1e87:	44 89 d1             	mov    %r10d,%ecx
    1e8a:	66 45 89 5c 04 06    	mov    %r11w,0x6(%r12,%rax,1)
    1e90:	c1 e9 10             	shr    $0x10,%ecx
    1e93:	41 88 4c 04 08       	mov    %cl,0x8(%r12,%rax,1)
    1e98:	4c 39 c2             	cmp    %r8,%rdx
    1e9b:	0f 83 2f 01 00 00    	jae    1fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1ea1:	4c 8d 54 03 09       	lea    0x9(%rbx,%rax,1),%r10
    1ea6:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1eab:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1eb0:	45 0f b6 12          	movzbl (%r10),%r10d
    1eb4:	41 c1 e3 08          	shl    $0x8,%r11d
    1eb8:	c1 e2 10             	shl    $0x10,%edx
    1ebb:	44 09 da             	or     %r11d,%edx
    1ebe:	44 09 d2             	or     %r10d,%edx
    1ec1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1ec5:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1ec9:	44 8b 12             	mov    (%rdx),%r10d
    1ecc:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1ed0:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1ed4:	44 89 d1             	mov    %r10d,%ecx
    1ed7:	66 45 89 5c 04 09    	mov    %r11w,0x9(%r12,%rax,1)
    1edd:	c1 e9 10             	shr    $0x10,%ecx
    1ee0:	41 88 4c 04 0b       	mov    %cl,0xb(%r12,%rax,1)
    1ee5:	4c 39 c2             	cmp    %r8,%rdx
    1ee8:	0f 83 e2 00 00 00    	jae    1fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1eee:	4c 8d 54 03 0c       	lea    0xc(%rbx,%rax,1),%r10
    1ef3:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1ef8:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1efd:	45 0f b6 12          	movzbl (%r10),%r10d
    1f01:	41 c1 e3 08          	shl    $0x8,%r11d
    1f05:	c1 e2 10             	shl    $0x10,%edx
    1f08:	44 09 da             	or     %r11d,%edx
    1f0b:	44 09 d2             	or     %r10d,%edx
    1f0e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1f12:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1f16:	44 8b 12             	mov    (%rdx),%r10d
    1f19:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1f1d:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1f21:	44 89 d1             	mov    %r10d,%ecx
    1f24:	66 45 89 5c 04 0c    	mov    %r11w,0xc(%r12,%rax,1)
    1f2a:	c1 e9 10             	shr    $0x10,%ecx
    1f2d:	41 88 4c 04 0e       	mov    %cl,0xe(%r12,%rax,1)
    1f32:	4c 39 c2             	cmp    %r8,%rdx
    1f35:	0f 83 95 00 00 00    	jae    1fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1f3b:	4c 8d 54 03 0f       	lea    0xf(%rbx,%rax,1),%r10
    1f40:	49 83 c1 06          	add    $0x6,%r9
    1f44:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1f49:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1f4e:	45 0f b6 12          	movzbl (%r10),%r10d
    1f52:	41 c1 e3 08          	shl    $0x8,%r11d
    1f56:	c1 e2 10             	shl    $0x10,%edx
    1f59:	44 09 da             	or     %r11d,%edx
    1f5c:	44 09 d2             	or     %r10d,%edx
    1f5f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1f63:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1f67:	44 8b 12             	mov    (%rdx),%r10d
    1f6a:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1f6e:	44 89 d1             	mov    %r10d,%ecx
    1f71:	66 45 89 5c 04 0f    	mov    %r11w,0xf(%r12,%rax,1)
    1f77:	c1 e9 10             	shr    $0x10,%ecx
    1f7a:	41 88 4c 04 11       	mov    %cl,0x11(%r12,%rax,1)
    1f7f:	4d 39 c1             	cmp    %r8,%r9
    1f82:	73 4c                	jae    1fd0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1f84:	48 8d 54 03 12       	lea    0x12(%rbx,%rax,1),%rdx
    1f89:	4d 8d 44 04 12       	lea    0x12(%r12,%rax,1),%r8
    1f8e:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1f92:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1f96:	0f b6 12             	movzbl (%rdx),%edx
    1f99:	c1 e0 08             	shl    $0x8,%eax
    1f9c:	c1 e1 10             	shl    $0x10,%ecx
    1f9f:	09 c8                	or     %ecx,%eax
    1fa1:	09 d0                	or     %edx,%eax
    1fa3:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1fa7:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1fab:	8b 02                	mov    (%rdx),%eax
    1fad:	0f b7 12             	movzwl (%rdx),%edx
    1fb0:	c1 e8 10             	shr    $0x10,%eax
    1fb3:	66 41 89 10          	mov    %dx,(%r8)
    1fb7:	41 88 40 02          	mov    %al,0x2(%r8)
    1fbb:	c5 f8 77             	vzeroupper
    1fbe:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1fc2:	5b                   	pop    %rbx
    1fc3:	41 5c                	pop    %r12
    1fc5:	41 5d                	pop    %r13
    1fc7:	41 5e                	pop    %r14
    1fc9:	41 5f                	pop    %r15
    1fcb:	5d                   	pop    %rbp
    1fcc:	c3                   	ret
    1fcd:	0f 1f 00             	nopl   (%rax)
    1fd0:	c5 f8 77             	vzeroupper
    1fd3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1fd7:	5b                   	pop    %rbx
    1fd8:	41 5c                	pop    %r12
    1fda:	41 5d                	pop    %r13
    1fdc:	41 5e                	pop    %r14
    1fde:	41 5f                	pop    %r15
    1fe0:	5d                   	pop    %rbp
    1fe1:	c3                   	ret
    1fe2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1fe8:	4d 89 c1             	mov    %r8,%r9
    1feb:	e9 68 fc ff ff       	jmp    1c58 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    1ff0:	c3                   	ret
    1ff1:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1ff5:	49 89 c9             	mov    %rcx,%r9
    1ff8:	e9 c2 f8 ff ff       	jmp    18bf <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x92f>
