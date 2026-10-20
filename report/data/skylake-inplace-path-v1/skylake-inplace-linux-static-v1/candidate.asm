
artifacts/skylake-inplace-linux-build-v1/CMakeFiles/jshc_skylake_inplace.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 f3 0f 00 00    	je     1000 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1000>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
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
      89:	0f 84 61 0f 00 00    	je     ff0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xff0>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 5f 0f 00 00    	jb     1001 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1001>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # ae <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # b6 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	48 8d 84 02 00 04 00 	lea    0x400(%rdx,%rax,1),%rax
      bd:	00 
      be:	eb 03                	jmp    c3 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc3>
      c0:	4d 89 c1             	mov    %r8,%r9
      c3:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      ca:	4c 39 c1             	cmp    %r8,%rcx
      cd:	72 15                	jb     e4 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe4>
      cf:	0f 18 00             	prefetchnta (%rax)
      d2:	0f 18 40 40          	prefetchnta 0x40(%rax)
      d6:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
      dd:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
      e4:	44 8b a0 0c fc ff ff 	mov    -0x3f4(%rax),%r12d
      eb:	44 8b b0 12 fc ff ff 	mov    -0x3ee(%rax),%r14d
      f2:	44 8b 80 00 fc ff ff 	mov    -0x400(%rax),%r8d
      f9:	44 8b 98 06 fc ff ff 	mov    -0x3fa(%rax),%r11d
     100:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     107:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     10e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     113:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     118:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     11f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     126:	44 8b a0 0f fc ff ff 	mov    -0x3f1(%rax),%r12d
     12d:	44 8b b0 15 fc ff ff 	mov    -0x3eb(%rax),%r14d
     134:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     13a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     140:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     147:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     14e:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     153:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     158:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     15d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     162:	44 8b 80 03 fc ff ff 	mov    -0x3fd(%rax),%r8d
     169:	44 8b 98 09 fc ff ff 	mov    -0x3f7(%rax),%r11d
     170:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     177:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     17e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     185:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     18c:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     192:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     197:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     19c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     1a0:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     1a5:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     1ac:	44 8b 80 18 fc ff ff 	mov    -0x3e8(%rax),%r8d
     1b3:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1ba:	44 8b 98 1e fc ff ff 	mov    -0x3e2(%rax),%r11d
     1c1:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1c8:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1cf:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     1d4:	44 8b 80 1b fc ff ff 	mov    -0x3e5(%rax),%r8d
     1db:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     1df:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     1e4:	44 8b 98 21 fc ff ff 	mov    -0x3df(%rax),%r11d
     1eb:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     1f1:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1f8:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     1fd:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     204:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     209:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     20e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     213:	44 8b a0 24 fc ff ff 	mov    -0x3dc(%rax),%r12d
     21a:	44 8b b0 2a fc ff ff 	mov    -0x3d6(%rax),%r14d
     221:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     227:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     22e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     235:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     23a:	44 8b a0 27 fc ff ff 	mov    -0x3d9(%rax),%r12d
     241:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     246:	44 8b b0 2d fc ff ff 	mov    -0x3d3(%rax),%r14d
     24d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     254:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     25a:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     261:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     268:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     26d:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     273:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     278:	44 8b 80 30 fc ff ff 	mov    -0x3d0(%rax),%r8d
     27f:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     286:	44 8b a0 3c fc ff ff 	mov    -0x3c4(%rax),%r12d
     28d:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     294:	44 8b b0 42 fc ff ff 	mov    -0x3be(%rax),%r14d
     29b:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2a2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2a9:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     2ae:	44 8b 80 33 fc ff ff 	mov    -0x3cd(%rax),%r8d
     2b5:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     2b9:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     2be:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2c5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     2ca:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     2cf:	44 8b a0 3f fc ff ff 	mov    -0x3c1(%rax),%r12d
     2d6:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2dd:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     2e4:	44 8b 98 36 fc ff ff 	mov    -0x3ca(%rax),%r11d
     2eb:	44 8b b0 45 fc ff ff 	mov    -0x3bb(%rax),%r14d
     2f2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2f9:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     2fe:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     305:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     309:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     30e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     313:	44 8b 98 39 fc ff ff 	mov    -0x3c7(%rax),%r11d
     31a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     321:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     327:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     32c:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     331:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     338:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     33d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     342:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     348:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     34c:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     352:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     358:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     35e:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     364:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     36b:	44 8b b0 5a fc ff ff 	mov    -0x3a6(%rax),%r14d
     372:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     379:	44 8b a0 54 fc ff ff 	mov    -0x3ac(%rax),%r12d
     380:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     387:	c4 a3 51 22 2c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm5,%xmm5
     38e:	44 8b 80 48 fc ff ff 	mov    -0x3b8(%rax),%r8d
     395:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     399:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     39e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     3a5:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     3aa:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     3af:	44 8b b0 5d fc ff ff 	mov    -0x3a3(%rax),%r14d
     3b6:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3bd:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     3c4:	44 8b a0 57 fc ff ff 	mov    -0x3a9(%rax),%r12d
     3cb:	44 8b 98 4e fc ff ff 	mov    -0x3b2(%rax),%r11d
     3d2:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     3d9:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     3de:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     3e2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     3e9:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     3ee:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     3f4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3f9:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     400:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     406:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     40c:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     411:	44 8b 80 4b fc ff ff 	mov    -0x3b5(%rax),%r8d
     418:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     41d:	44 8b 98 51 fc ff ff 	mov    -0x3af(%rax),%r11d
     424:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     42b:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     430:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     437:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     43e:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     444:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     448:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     44f:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     454:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     45a:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     460:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     465:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     469:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     46e:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     475:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     47c:	44 8b 80 60 fc ff ff 	mov    -0x3a0(%rax),%r8d
     483:	44 8b a0 6c fc ff ff 	mov    -0x394(%rax),%r12d
     48a:	44 8b b0 72 fc ff ff 	mov    -0x38e(%rax),%r14d
     491:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     498:	44 8b 98 66 fc ff ff 	mov    -0x39a(%rax),%r11d
     49f:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     4a3:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     4aa:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     4b1:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     4b7:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     4bc:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     4c1:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     4c6:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     4cd:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     4d2:	44 8b a0 6f fc ff ff 	mov    -0x391(%rax),%r12d
     4d9:	44 8b b0 75 fc ff ff 	mov    -0x38b(%rax),%r14d
     4e0:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     4e5:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     4eb:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     4f1:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     4f8:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     4ff:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     504:	44 8b 80 63 fc ff ff 	mov    -0x39d(%rax),%r8d
     50b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     510:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     515:	44 8b 98 69 fc ff ff 	mov    -0x397(%rax),%r11d
     51c:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     523:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     529:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     530:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     537:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     53e:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     543:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     548:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     54c:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     551:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     558:	44 8b 80 78 fc ff ff 	mov    -0x388(%rax),%r8d
     55f:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     566:	44 8b 98 7e fc ff ff 	mov    -0x382(%rax),%r11d
     56d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     574:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     57b:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     580:	44 8b 80 7b fc ff ff 	mov    -0x385(%rax),%r8d
     587:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     58b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     590:	44 8b 98 81 fc ff ff 	mov    -0x37f(%rax),%r11d
     597:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     59d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     5a4:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     5a9:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     5b0:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     5b5:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     5ba:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     5bf:	44 8b a0 84 fc ff ff 	mov    -0x37c(%rax),%r12d
     5c6:	44 8b b0 8a fc ff ff 	mov    -0x376(%rax),%r14d
     5cd:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     5d2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5d9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5e0:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     5e5:	44 8b a0 87 fc ff ff 	mov    -0x379(%rax),%r12d
     5ec:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     5f1:	44 8b b0 8d fc ff ff 	mov    -0x373(%rax),%r14d
     5f8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5ff:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     605:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     60c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     613:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     618:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     61e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     623:	44 8b 98 96 fc ff ff 	mov    -0x36a(%rax),%r11d
     62a:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     631:	44 8b a0 9c fc ff ff 	mov    -0x364(%rax),%r12d
     638:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     63f:	44 8b b0 a2 fc ff ff 	mov    -0x35e(%rax),%r14d
     646:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     64d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     654:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     659:	44 8b 98 99 fc ff ff 	mov    -0x367(%rax),%r11d
     660:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     664:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     66a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     671:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     676:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     67b:	44 8b a0 9f fc ff ff 	mov    -0x361(%rax),%r12d
     682:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     689:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     690:	44 8b 80 90 fc ff ff 	mov    -0x370(%rax),%r8d
     697:	44 8b b0 a5 fc ff ff 	mov    -0x35b(%rax),%r14d
     69e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     6a5:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     6aa:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     6b1:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     6b5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     6ba:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     6bf:	44 8b 80 93 fc ff ff 	mov    -0x36d(%rax),%r8d
     6c6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     6cd:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     6d3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     6d8:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     6dd:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     6e4:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     6e9:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     6ee:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     6f4:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     6fa:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     6ff:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     706:	44 8b b0 ba fc ff ff 	mov    -0x346(%rax),%r14d
     70d:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     714:	44 8b a0 b4 fc ff ff 	mov    -0x34c(%rax),%r12d
     71b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     722:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     729:	44 8b 98 ae fc ff ff 	mov    -0x352(%rax),%r11d
     730:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     734:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     73a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     741:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     746:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     74b:	44 8b b0 bd fc ff ff 	mov    -0x343(%rax),%r14d
     752:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     759:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     760:	44 8b a0 b7 fc ff ff 	mov    -0x349(%rax),%r12d
     767:	44 8b 80 a8 fc ff ff 	mov    -0x358(%rax),%r8d
     76e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     775:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     77a:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     77f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     786:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     78b:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     791:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     798:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     79d:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     7a3:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     7a9:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     7ae:	44 8b 98 b1 fc ff ff 	mov    -0x34f(%rax),%r11d
     7b5:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     7ba:	44 8b 80 ab fc ff ff 	mov    -0x355(%rax),%r8d
     7c1:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     7c8:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     7cd:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     7d4:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     7db:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     7e0:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     7e7:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     7ec:	48 05 c0 00 00 00    	add    $0xc0,%rax
     7f2:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     7f7:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     7fb:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     801:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     808:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     80f:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     816:	4d 8d 41 40          	lea    0x40(%r9),%r8
     81a:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     81f:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     824:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     82a:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     830:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     835:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     83b:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     841:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     846:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     84b:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     850:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     855:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     85b:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     861:	c5 7d 7f 88 40 fb ff 	vmovdqa %ymm9,-0x4c0(%rax)
     868:	ff 
     869:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     86d:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     871:	c5 fd 7f b0 60 fb ff 	vmovdqa %ymm6,-0x4a0(%rax)
     878:	ff 
     879:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     87f:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     883:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     889:	c5 fd 7f a8 80 fb ff 	vmovdqa %ymm5,-0x480(%rax)
     890:	ff 
     891:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     897:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     89b:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     8a1:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     8a6:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     8ac:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     8b0:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     8b6:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     8bc:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     8c2:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     8c8:	c5 fd 7f a8 a0 fb ff 	vmovdqa %ymm5,-0x460(%rax)
     8cf:	ff 
     8d0:	c5 fd 7f 80 c0 fb ff 	vmovdqa %ymm0,-0x440(%rax)
     8d7:	ff 
     8d8:	c5 fd 7f 88 e0 fb ff 	vmovdqa %ymm1,-0x420(%rax)
     8df:	ff 
     8e0:	4c 39 d1             	cmp    %r10,%rcx
     8e3:	0f 83 d7 f7 ff ff    	jae    c0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc0>
     8e9:	49 8d 41 68          	lea    0x68(%r9),%rax
     8ed:	48 39 c1             	cmp    %rax,%rcx
     8f0:	0f 82 b8 03 00 00    	jb     cae <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcae>
     8f6:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     8fa:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 902 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x902>
     901:	00 
     902:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 90a <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x90a>
     909:	00 
     90a:	48 01 d0             	add    %rdx,%rax
     90d:	0f 1f 00             	nopl   (%rax)
     910:	44 8b 60 54          	mov    0x54(%rax),%r12d
     914:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     918:	44 8b 48 48          	mov    0x48(%rax),%r9d
     91c:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     920:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     927:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     92e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     933:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     938:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     93f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     946:	44 8b 60 57          	mov    0x57(%rax),%r12d
     94a:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     94e:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     954:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     95a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     961:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     968:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     96d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     972:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     977:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     97c:	44 8b 48 4b          	mov    0x4b(%rax),%r9d
     980:	44 8b 58 51          	mov    0x51(%rax),%r11d
     984:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     98b:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     992:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     999:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9a0:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     9a6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     9ab:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     9b0:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     9b4:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     9b9:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
     9c0:	44 8b 48 30          	mov    0x30(%rax),%r9d
     9c4:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     9cb:	44 8b 58 36          	mov    0x36(%rax),%r11d
     9cf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     9d6:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9dd:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     9e2:	44 8b 48 33          	mov    0x33(%rax),%r9d
     9e6:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     9ea:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     9ef:	44 8b 58 39          	mov    0x39(%rax),%r11d
     9f3:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     9f9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     a00:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     a05:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a0c:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a11:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     a16:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a1b:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     a1f:	44 8b 70 42          	mov    0x42(%rax),%r14d
     a23:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     a28:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a2f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a36:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a3b:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     a3f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a44:	44 8b 70 45          	mov    0x45(%rax),%r14d
     a48:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a4f:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     a55:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     a5c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a63:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a68:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     a6e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a73:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     a77:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     a7e:	44 8b 60 24          	mov    0x24(%rax),%r12d
     a82:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     a89:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     a8d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a94:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a9b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     aa0:	44 8b 58 21          	mov    0x21(%rax),%r11d
     aa4:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     aa8:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     aae:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     ab5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     aba:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     abf:	44 8b 60 27          	mov    0x27(%rax),%r12d
     ac3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     aca:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     ad1:	44 8b 48 18          	mov    0x18(%rax),%r9d
     ad5:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
     ad9:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     ae0:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     ae5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     aec:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     af0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     af5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     afa:	44 8b 48 1b          	mov    0x1b(%rax),%r9d
     afe:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b05:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     b0b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b10:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     b15:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b1c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     b21:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     b26:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     b2c:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     b30:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     b36:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     b3c:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     b41:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     b48:	44 8b 70 12          	mov    0x12(%rax),%r14d
     b4c:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     b53:	44 8b 60 0c          	mov    0xc(%rax),%r12d
     b57:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b5e:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     b65:	44 8b 58 06          	mov    0x6(%rax),%r11d
     b69:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     b6d:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     b73:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     b7a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     b7f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     b84:	44 8b 70 15          	mov    0x15(%rax),%r14d
     b88:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     b8f:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     b96:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     b9a:	44 8b 08             	mov    (%rax),%r9d
     b9d:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     ba4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     ba9:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     bad:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     bb4:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     bb9:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     bbf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bc6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     bcb:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     bd1:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     bd7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     bdc:	44 8b 58 09          	mov    0x9(%rax),%r11d
     be0:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     be5:	44 8b 48 03          	mov    0x3(%rax),%r9d
     be9:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     bf0:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     bf5:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
     bfc:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     c03:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     c08:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     c0c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c13:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     c18:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     c1e:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c23:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     c27:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     c2d:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     c33:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     c3a:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     c40:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     c47:	4d 8d 48 48          	lea    0x48(%r8),%r9
     c4b:	49 83 c0 20          	add    $0x20,%r8
     c4f:	48 83 c0 60          	add    $0x60,%rax
     c53:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     c57:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
     c5b:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     c61:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     c67:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
     c6d:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
     c71:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     c76:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
     c7c:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     c81:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     c85:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     c8b:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     c90:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
     c96:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     c9b:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     ca0:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     ca5:	4c 39 c9             	cmp    %r9,%rcx
     ca8:	0f 83 62 fc ff ff    	jae    910 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x910>
     cae:	4d 8d 48 08          	lea    0x8(%r8),%r9
     cb2:	4c 39 c9             	cmp    %r9,%rcx
     cb5:	0f 82 2d 01 00 00    	jb     de8 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xde8>
     cbb:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     cbf:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # cc7 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcc7>
     cc6:	00 
     cc7:	48 01 d0             	add    %rdx,%rax
     cca:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     cd0:	48 8b 18             	mov    (%rax),%rbx
     cd3:	4c 8b 40 08          	mov    0x8(%rax),%r8
     cd7:	48 83 c0 18          	add    $0x18,%rax
     cdb:	4c 8b 68 f8          	mov    -0x8(%rax),%r13
     cdf:	49 89 da             	mov    %rbx,%r10
     ce2:	4d 89 c6             	mov    %r8,%r14
     ce5:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     cec:	45 89 ef             	mov    %r13d,%r15d
     cef:	49 c1 ee 20          	shr    $0x20,%r14
     cf3:	46 0f b6 1c 17       	movzbl (%rdi,%r10,1),%r11d
     cf8:	49 89 da             	mov    %rbx,%r10
     cfb:	48 c1 eb 30          	shr    $0x30,%rbx
     cff:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     d06:	41 c1 e7 08          	shl    $0x8,%r15d
     d0a:	49 89 dc             	mov    %rbx,%r12
     d0d:	44 89 c3             	mov    %r8d,%ebx
     d10:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     d15:	c1 e3 10             	shl    $0x10,%ebx
     d18:	49 c1 ea 18          	shr    $0x18,%r10
     d1c:	44 09 e3             	or     %r12d,%ebx
     d1f:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     d25:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     d2c:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     d32:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     d37:	44 0f b6 24 1f       	movzbl (%rdi,%rbx,1),%r12d
     d3c:	44 89 c3             	mov    %r8d,%ebx
     d3f:	49 c1 e8 38          	shr    $0x38,%r8
     d43:	45 09 f8             	or     %r15d,%r8d
     d46:	4d 89 ef             	mov    %r13,%r15
     d49:	49 c1 ed 28          	shr    $0x28,%r13
     d4d:	49 c1 ef 10          	shr    $0x10,%r15
     d51:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     d58:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     d5d:	c1 eb 08             	shr    $0x8,%ebx
     d60:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     d67:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     d6c:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     d70:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     d75:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
     d7b:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     d82:	4d 89 c8             	mov    %r9,%r8
     d85:	49 83 c1 08          	add    $0x8,%r9
     d89:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     d8f:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
     d96:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     d9d:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     da1:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     da7:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
     dae:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     db2:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     db8:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     dbd:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     dc1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     dc7:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     dcc:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     dd1:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     dd5:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     dda:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     ddf:	4c 39 c9             	cmp    %r9,%rcx
     de2:	0f 83 e8 fe ff ff    	jae    cd0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcd0>
     de8:	49 39 c8             	cmp    %rcx,%r8
     deb:	0f 83 ef 01 00 00    	jae    fe0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
     df1:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     df5:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     df9:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     dfe:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e03:	c1 e0 08             	shl    $0x8,%eax
     e06:	41 c1 e3 10          	shl    $0x10,%r11d
     e0a:	44 09 d8             	or     %r11d,%eax
     e0d:	45 0f b6 1a          	movzbl (%r10),%r11d
     e11:	44 09 d8             	or     %r11d,%eax
     e14:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e18:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e1c:	41 8b 03             	mov    (%r11),%eax
     e1f:	45 0f b7 1b          	movzwl (%r11),%r11d
     e23:	c1 e8 10             	shr    $0x10,%eax
     e26:	66 45 89 1a          	mov    %r11w,(%r10)
     e2a:	41 88 42 02          	mov    %al,0x2(%r10)
     e2e:	49 8d 40 01          	lea    0x1(%r8),%rax
     e32:	48 39 c8             	cmp    %rcx,%rax
     e35:	0f 83 a5 01 00 00    	jae    fe0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
     e3b:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     e40:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     e45:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e4a:	c1 e0 08             	shl    $0x8,%eax
     e4d:	41 c1 e3 10          	shl    $0x10,%r11d
     e51:	44 09 d8             	or     %r11d,%eax
     e54:	45 0f b6 1a          	movzbl (%r10),%r11d
     e58:	44 09 d8             	or     %r11d,%eax
     e5b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e5f:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e63:	41 8b 03             	mov    (%r11),%eax
     e66:	45 0f b7 1b          	movzwl (%r11),%r11d
     e6a:	c1 e8 10             	shr    $0x10,%eax
     e6d:	66 45 89 1a          	mov    %r11w,(%r10)
     e71:	41 88 42 02          	mov    %al,0x2(%r10)
     e75:	49 8d 40 02          	lea    0x2(%r8),%rax
     e79:	48 39 c8             	cmp    %rcx,%rax
     e7c:	0f 83 5e 01 00 00    	jae    fe0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
     e82:	4e 8d 54 0a 06       	lea    0x6(%rdx,%r9,1),%r10
     e87:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     e8c:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e91:	c1 e0 08             	shl    $0x8,%eax
     e94:	41 c1 e3 10          	shl    $0x10,%r11d
     e98:	44 09 d8             	or     %r11d,%eax
     e9b:	45 0f b6 1a          	movzbl (%r10),%r11d
     e9f:	44 09 d8             	or     %r11d,%eax
     ea2:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     ea6:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     eaa:	41 8b 03             	mov    (%r11),%eax
     ead:	45 0f b7 1b          	movzwl (%r11),%r11d
     eb1:	c1 e8 10             	shr    $0x10,%eax
     eb4:	66 45 89 1a          	mov    %r11w,(%r10)
     eb8:	41 88 42 02          	mov    %al,0x2(%r10)
     ebc:	49 8d 40 03          	lea    0x3(%r8),%rax
     ec0:	48 39 c8             	cmp    %rcx,%rax
     ec3:	0f 83 17 01 00 00    	jae    fe0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
     ec9:	4e 8d 54 0a 09       	lea    0x9(%rdx,%r9,1),%r10
     ece:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     ed3:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     ed8:	c1 e0 10             	shl    $0x10,%eax
     edb:	41 c1 e3 08          	shl    $0x8,%r11d
     edf:	44 09 d8             	or     %r11d,%eax
     ee2:	45 0f b6 1a          	movzbl (%r10),%r11d
     ee6:	44 09 d8             	or     %r11d,%eax
     ee9:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     eed:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     ef1:	41 8b 03             	mov    (%r11),%eax
     ef4:	45 0f b7 1b          	movzwl (%r11),%r11d
     ef8:	c1 e8 10             	shr    $0x10,%eax
     efb:	66 45 89 1a          	mov    %r11w,(%r10)
     eff:	41 88 42 02          	mov    %al,0x2(%r10)
     f03:	49 8d 40 04          	lea    0x4(%r8),%rax
     f07:	48 39 c8             	cmp    %rcx,%rax
     f0a:	0f 83 d0 00 00 00    	jae    fe0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
     f10:	4e 8d 54 0a 0c       	lea    0xc(%rdx,%r9,1),%r10
     f15:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     f1a:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     f1f:	c1 e0 10             	shl    $0x10,%eax
     f22:	41 c1 e3 08          	shl    $0x8,%r11d
     f26:	44 09 d8             	or     %r11d,%eax
     f29:	45 0f b6 1a          	movzbl (%r10),%r11d
     f2d:	44 09 d8             	or     %r11d,%eax
     f30:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f34:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f38:	41 8b 03             	mov    (%r11),%eax
     f3b:	45 0f b7 1b          	movzwl (%r11),%r11d
     f3f:	c1 e8 10             	shr    $0x10,%eax
     f42:	66 45 89 1a          	mov    %r11w,(%r10)
     f46:	41 88 42 02          	mov    %al,0x2(%r10)
     f4a:	49 8d 40 05          	lea    0x5(%r8),%rax
     f4e:	48 39 c8             	cmp    %rcx,%rax
     f51:	0f 83 89 00 00 00    	jae    fe0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
     f57:	4e 8d 54 0a 0f       	lea    0xf(%rdx,%r9,1),%r10
     f5c:	49 83 c0 06          	add    $0x6,%r8
     f60:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     f65:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     f6a:	c1 e0 10             	shl    $0x10,%eax
     f6d:	41 c1 e3 08          	shl    $0x8,%r11d
     f71:	44 09 d8             	or     %r11d,%eax
     f74:	45 0f b6 1a          	movzbl (%r10),%r11d
     f78:	44 09 d8             	or     %r11d,%eax
     f7b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f7f:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f83:	41 8b 03             	mov    (%r11),%eax
     f86:	45 0f b7 1b          	movzwl (%r11),%r11d
     f8a:	c1 e8 10             	shr    $0x10,%eax
     f8d:	66 45 89 1a          	mov    %r11w,(%r10)
     f91:	41 88 42 02          	mov    %al,0x2(%r10)
     f95:	49 39 c8             	cmp    %rcx,%r8
     f98:	73 46                	jae    fe0 <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
     f9a:	4a 8d 54 0a 12       	lea    0x12(%rdx,%r9,1),%rdx
     f9f:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     fa3:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     fa7:	c1 e0 08             	shl    $0x8,%eax
     faa:	c1 e1 10             	shl    $0x10,%ecx
     fad:	09 c8                	or     %ecx,%eax
     faf:	0f b6 0a             	movzbl (%rdx),%ecx
     fb2:	09 c8                	or     %ecx,%eax
     fb4:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     fb8:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     fbc:	8b 01                	mov    (%rcx),%eax
     fbe:	0f b7 09             	movzwl (%rcx),%ecx
     fc1:	c1 e8 10             	shr    $0x10,%eax
     fc4:	66 89 0a             	mov    %cx,(%rdx)
     fc7:	88 42 02             	mov    %al,0x2(%rdx)
     fca:	c5 f8 77             	vzeroupper
     fcd:	5b                   	pop    %rbx
     fce:	41 5c                	pop    %r12
     fd0:	41 5d                	pop    %r13
     fd2:	41 5e                	pop    %r14
     fd4:	41 5f                	pop    %r15
     fd6:	5d                   	pop    %rbp
     fd7:	c3                   	ret
     fd8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     fdf:	00 
     fe0:	c5 f8 77             	vzeroupper
     fe3:	5b                   	pop    %rbx
     fe4:	41 5c                	pop    %r12
     fe6:	41 5d                	pop    %r13
     fe8:	41 5e                	pop    %r14
     fea:	41 5f                	pop    %r15
     fec:	5d                   	pop    %rbp
     fed:	c3                   	ret
     fee:	66 90                	xchg   %ax,%ax
     ff0:	49 89 c8             	mov    %rcx,%r8
     ff3:	e9 b6 fc ff ff       	jmp    cae <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcae>
     ff8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     fff:	00 
    1000:	c3                   	ret
    1001:	49 8d 41 28          	lea    0x28(%r9),%rax
    1005:	4d 89 c8             	mov    %r9,%r8
    1008:	e9 e0 f8 ff ff       	jmp    8ed <jshc_channel::avx2_chain_inplace(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8ed>
    100d:	0f 1f 00             	nopl   (%rax)

0000000000001010 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1010:	f3 0f 1e fa          	endbr64
    1014:	4d 85 c0             	test   %r8,%r8
    1017:	0f 84 53 10 00 00    	je     2070 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1060>
    101d:	55                   	push   %rbp
    101e:	b8 00 04 00 00       	mov    $0x400,%eax
    1023:	48 89 e5             	mov    %rsp,%rbp
    1026:	41 57                	push   %r15
    1028:	41 56                	push   %r14
    102a:	41 55                	push   %r13
    102c:	41 54                	push   %r12
    102e:	49 89 cc             	mov    %rcx,%r12
    1031:	53                   	push   %rbx
    1032:	48 89 d3             	mov    %rdx,%rbx
    1035:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    1039:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    103d:	48 39 c2             	cmp    %rax,%rdx
    1040:	48 0f 47 d0          	cmova  %rax,%rdx
    1044:	31 c0                	xor    %eax,%eax
    1046:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    104d:	00 00 00 
    1050:	0f 18 04 03          	prefetchnta (%rbx,%rax,1)
    1054:	48 83 c0 40          	add    $0x40,%rax
    1058:	48 39 d0             	cmp    %rdx,%rax
    105b:	72 f3                	jb     1050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
    105d:	49 89 d9             	mov    %rbx,%r9
    1060:	4c 89 e2             	mov    %r12,%rdx
    1063:	31 c9                	xor    %ecx,%ecx
    1065:	eb 53                	jmp    10ba <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
    1067:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    106e:	00 00 
    1070:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
    1075:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
    107a:	48 ff c1             	inc    %rcx
    107d:	48 83 c2 03          	add    $0x3,%rdx
    1081:	49 83 c1 03          	add    $0x3,%r9
    1085:	41 c1 e2 10          	shl    $0x10,%r10d
    1089:	c1 e0 08             	shl    $0x8,%eax
    108c:	44 09 d0             	or     %r10d,%eax
    108f:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
    1094:	44 09 d0             	or     %r10d,%eax
    1097:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    109b:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
    109f:	41 8b 02             	mov    (%r10),%eax
    10a2:	45 0f b7 12          	movzwl (%r10),%r10d
    10a6:	c1 e8 10             	shr    $0x10,%eax
    10a9:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
    10ae:	88 42 ff             	mov    %al,-0x1(%rdx)
    10b1:	49 39 c8             	cmp    %rcx,%r8
    10b4:	0f 84 ae 0f 00 00    	je     2068 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1058>
    10ba:	f6 c2 3f             	test   $0x3f,%dl
    10bd:	75 b1                	jne    1070 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    10bf:	48 8d 41 48          	lea    0x48(%rcx),%rax
    10c3:	49 39 c0             	cmp    %rax,%r8
    10c6:	0f 82 a5 0f 00 00    	jb     2071 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1061>
    10cc:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    10d0:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 10d8 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc8>
    10d7:	00 
    10d8:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 10e0 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd0>
    10df:	00 
    10e0:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    10e5:	49 8d 14 04          	lea    (%r12,%rax,1),%rdx
    10e9:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    10ee:	48 8d 84 03 00 04 00 	lea    0x400(%rbx,%rax,1),%rax
    10f5:	00 
    10f6:	eb 0b                	jmp    1103 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
    10f8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    10ff:	00 
    1100:	4c 89 c9             	mov    %r9,%rcx
    1103:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    110a:	4d 39 c8             	cmp    %r9,%r8
    110d:	72 15                	jb     1124 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
    110f:	0f 18 00             	prefetchnta (%rax)
    1112:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1116:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    111d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    1124:	44 8b 88 00 fc ff ff 	mov    -0x400(%rax),%r9d
    112b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1132:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1137:	44 8b 88 03 fc ff ff 	mov    -0x3fd(%rax),%r9d
    113e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1145:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
    114b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1150:	44 8b 88 06 fc ff ff 	mov    -0x3fa(%rax),%r9d
    1157:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    115e:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
    1165:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    116a:	44 8b 88 09 fc ff ff 	mov    -0x3f7(%rax),%r9d
    1171:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1178:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    117d:	44 8b 88 0c fc ff ff 	mov    -0x3f4(%rax),%r9d
    1184:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    118b:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1190:	44 8b 88 0f fc ff ff 	mov    -0x3f1(%rax),%r9d
    1197:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    119e:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    11a4:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    11a9:	44 8b 88 12 fc ff ff 	mov    -0x3ee(%rax),%r9d
    11b0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11b7:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    11be:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    11c3:	44 8b 88 15 fc ff ff 	mov    -0x3eb(%rax),%r9d
    11ca:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11d1:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    11d7:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    11dc:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    11e3:	44 8b 88 18 fc ff ff 	mov    -0x3e8(%rax),%r9d
    11ea:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11f1:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    11f5:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    11fb:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1200:	44 8b 88 1b fc ff ff 	mov    -0x3e5(%rax),%r9d
    1207:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    120e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1215:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    121a:	44 8b 88 1e fc ff ff 	mov    -0x3e2(%rax),%r9d
    1221:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    1225:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    122b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1232:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    1237:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    123c:	44 8b 88 21 fc ff ff 	mov    -0x3df(%rax),%r9d
    1243:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
    1248:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    124f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1254:	44 8b 88 24 fc ff ff 	mov    -0x3dc(%rax),%r9d
    125b:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
    1261:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1268:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    126d:	44 8b 88 27 fc ff ff 	mov    -0x3d9(%rax),%r9d
    1274:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
    127b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1282:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1288:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    128d:	44 8b 88 2a fc ff ff 	mov    -0x3d6(%rax),%r9d
    1294:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    129b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    12a2:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    12a7:	44 8b 88 2d fc ff ff 	mov    -0x3d3(%rax),%r9d
    12ae:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12b5:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    12bb:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    12c0:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    12c7:	44 8b 88 30 fc ff ff 	mov    -0x3d0(%rax),%r9d
    12ce:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12d5:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    12d9:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    12df:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    12e4:	44 8b 88 33 fc ff ff 	mov    -0x3cd(%rax),%r9d
    12eb:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    12f2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12f9:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    12fe:	44 8b 88 36 fc ff ff 	mov    -0x3ca(%rax),%r9d
    1305:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    1309:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    130f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1316:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    131b:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1320:	44 8b 88 39 fc ff ff 	mov    -0x3c7(%rax),%r9d
    1327:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    132c:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    1330:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1336:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    133d:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    1343:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1348:	44 8b 88 3c fc ff ff 	mov    -0x3c4(%rax),%r9d
    134f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1356:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    135b:	44 8b 88 3f fc ff ff 	mov    -0x3c1(%rax),%r9d
    1362:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1369:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    136e:	44 8b 88 42 fc ff ff 	mov    -0x3be(%rax),%r9d
    1375:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    137c:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1381:	44 8b 88 45 fc ff ff 	mov    -0x3bb(%rax),%r9d
    1388:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    138f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1394:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    139a:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    13a0:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    13a6:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    13ad:	44 8b 88 48 fc ff ff 	mov    -0x3b8(%rax),%r9d
    13b4:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    13bb:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    13c2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13c9:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    13ce:	44 8b 88 4b fc ff ff 	mov    -0x3b5(%rax),%r9d
    13d5:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    13d9:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    13df:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13e6:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
    13ec:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    13f1:	44 8b 88 4e fc ff ff 	mov    -0x3b2(%rax),%r9d
    13f8:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    13ff:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1406:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
    140d:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1412:	44 8b 88 51 fc ff ff 	mov    -0x3af(%rax),%r9d
    1419:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    141d:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    1423:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    142a:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    142f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1434:	44 8b 88 54 fc ff ff 	mov    -0x3ac(%rax),%r9d
    143b:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1440:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    1444:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    144a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1451:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    1457:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    145c:	44 8b 88 57 fc ff ff 	mov    -0x3a9(%rax),%r9d
    1463:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    146a:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1470:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1475:	44 8b 88 5a fc ff ff 	mov    -0x3a6(%rax),%r9d
    147c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1483:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    148a:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    148f:	44 8b 88 5d fc ff ff 	mov    -0x3a3(%rax),%r9d
    1496:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    149d:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    14a3:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    14a8:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    14af:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    14b3:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    14b9:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    14c0:	44 8b 88 60 fc ff ff 	mov    -0x3a0(%rax),%r9d
    14c7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14ce:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    14d2:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    14d7:	44 8b 88 63 fc ff ff 	mov    -0x39d(%rax),%r9d
    14de:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    14e4:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    14e9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14f0:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
    14f6:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    14fb:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1500:	44 8b 88 66 fc ff ff 	mov    -0x39a(%rax),%r9d
    1507:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    150e:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
    1515:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    151a:	44 8b 88 69 fc ff ff 	mov    -0x397(%rax),%r9d
    1521:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1528:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    152d:	44 8b 88 6c fc ff ff 	mov    -0x394(%rax),%r9d
    1534:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    153b:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1540:	44 8b 88 6f fc ff ff 	mov    -0x391(%rax),%r9d
    1547:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    154e:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1554:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1559:	44 8b 88 72 fc ff ff 	mov    -0x38e(%rax),%r9d
    1560:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1567:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    156e:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1573:	44 8b 88 75 fc ff ff 	mov    -0x38b(%rax),%r9d
    157a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1581:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1587:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    158c:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1593:	44 8b 88 78 fc ff ff 	mov    -0x388(%rax),%r9d
    159a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15a1:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    15a5:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    15ab:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    15b0:	44 8b 88 7b fc ff ff 	mov    -0x385(%rax),%r9d
    15b7:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    15be:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15c5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    15ca:	44 8b 88 7e fc ff ff 	mov    -0x382(%rax),%r9d
    15d1:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    15d5:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    15db:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15e2:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    15e7:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    15ec:	44 8b 88 81 fc ff ff 	mov    -0x37f(%rax),%r9d
    15f3:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    15f8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15ff:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1604:	44 8b 88 84 fc ff ff 	mov    -0x37c(%rax),%r9d
    160b:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1611:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1618:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    161d:	44 8b 88 87 fc ff ff 	mov    -0x379(%rax),%r9d
    1624:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    162b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1632:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1638:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    163d:	44 8b 88 8a fc ff ff 	mov    -0x376(%rax),%r9d
    1644:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    164b:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1652:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1657:	44 8b 88 8d fc ff ff 	mov    -0x373(%rax),%r9d
    165e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1665:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    166b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1670:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    1677:	44 8b 88 90 fc ff ff 	mov    -0x370(%rax),%r9d
    167e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1685:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1689:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    168f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1694:	44 8b 88 93 fc ff ff 	mov    -0x36d(%rax),%r9d
    169b:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    16a2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16a9:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    16ae:	44 8b 88 96 fc ff ff 	mov    -0x36a(%rax),%r9d
    16b5:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    16b9:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    16bf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16c6:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    16cb:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    16d0:	44 8b 88 99 fc ff ff 	mov    -0x367(%rax),%r9d
    16d7:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    16dc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16e3:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    16e8:	44 8b 88 9c fc ff ff 	mov    -0x364(%rax),%r9d
    16ef:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16f6:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    16fb:	44 8b 88 9f fc ff ff 	mov    -0x361(%rax),%r9d
    1702:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1709:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    170e:	44 8b 88 a2 fc ff ff 	mov    -0x35e(%rax),%r9d
    1715:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    171c:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1721:	44 8b 88 a5 fc ff ff 	mov    -0x35b(%rax),%r9d
    1728:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    172f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1734:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    173a:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1740:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1746:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    174d:	44 8b 88 a8 fc ff ff 	mov    -0x358(%rax),%r9d
    1754:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    175b:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1762:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1769:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    176e:	44 8b 88 ab fc ff ff 	mov    -0x355(%rax),%r9d
    1775:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    177a:	c4 21 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm10
    1780:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1787:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    178c:	44 8b 88 ae fc ff ff 	mov    -0x352(%rax),%r9d
    1793:	c4 63 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm10,%xmm10
    179a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17a1:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    17a6:	44 8b 88 b1 fc ff ff 	mov    -0x34f(%rax),%r9d
    17ad:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    17b2:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    17b8:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    17be:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17c5:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    17ca:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    17cf:	44 8b 88 b4 fc ff ff 	mov    -0x34c(%rax),%r9d
    17d6:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    17db:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    17e2:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    17e9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17f0:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    17f5:	44 8b 88 b7 fc ff ff 	mov    -0x349(%rax),%r9d
    17fc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1803:	c4 21 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm10
    1809:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    180e:	44 8b 88 ba fc ff ff 	mov    -0x346(%rax),%r9d
    1815:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    181c:	c4 23 29 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm10,%xmm10
    1823:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1828:	44 8b 88 bd fc ff ff 	mov    -0x343(%rax),%r9d
    182f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1836:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    183c:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    1843:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1848:	c4 23 21 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm11,%xmm11
    184f:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    1853:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1858:	c4 21 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm11
    185e:	c4 63 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm11,%xmm11
    1865:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    186a:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    186f:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    1875:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    187b:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    1880:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    1886:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    188c:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1891:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    1896:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    189b:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    18a0:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    18a6:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    18ac:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
    18b3:	ff 
    18b4:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    18b8:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    18bc:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
    18c3:	ff 
    18c4:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
    18c9:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    18cd:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    18d1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    18d7:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    18dd:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    18e3:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    18e9:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    18ee:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    18f2:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    18f8:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    18fe:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    1904:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    190a:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1910:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
    1915:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    191a:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
    191f:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1925:	4d 39 d0             	cmp    %r10,%r8
    1928:	0f 83 d2 f7 ff ff    	jae    1100 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    192e:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1933:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1938:	48 8d 41 68          	lea    0x68(%rcx),%rax
    193c:	0f ae f8             	sfence
    193f:	49 39 c0             	cmp    %rax,%r8
    1942:	0f 82 90 03 00 00    	jb     1cd8 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    1948:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    194c:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1954 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x944>
    1953:	00 
    1954:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 195c <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x94c>
    195b:	00 
    195c:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1961:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    1966:	48 8d 04 13          	lea    (%rbx,%rdx,1),%rax
    196a:	4c 01 e2             	add    %r12,%rdx
    196d:	0f 1f 00             	nopl   (%rax)
    1970:	8b 48 48             	mov    0x48(%rax),%ecx
    1973:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1979:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    197e:	8b 48 4b             	mov    0x4b(%rax),%ecx
    1981:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1987:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    198d:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1992:	8b 48 4e             	mov    0x4e(%rax),%ecx
    1995:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    199b:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    19a2:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    19a7:	8b 48 51             	mov    0x51(%rax),%ecx
    19aa:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19b0:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    19b4:	8b 48 54             	mov    0x54(%rax),%ecx
    19b7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19bd:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    19c2:	8b 48 57             	mov    0x57(%rax),%ecx
    19c5:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19cb:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    19d1:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    19d6:	8b 48 5a             	mov    0x5a(%rax),%ecx
    19d9:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19df:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    19e6:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    19eb:	8b 48 5d             	mov    0x5d(%rax),%ecx
    19ee:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19f4:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    19fa:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    19fe:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    1a05:	8b 48 30             	mov    0x30(%rax),%ecx
    1a08:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a0e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1a12:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1a18:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1a1d:	8b 48 33             	mov    0x33(%rax),%ecx
    1a20:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1a27:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a2d:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1a32:	8b 48 36             	mov    0x36(%rax),%ecx
    1a35:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    1a39:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    1a3f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a45:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1a4a:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1a4f:	8b 48 39             	mov    0x39(%rax),%ecx
    1a52:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1a57:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a5d:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1a61:	8b 48 3c             	mov    0x3c(%rax),%ecx
    1a64:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1a6a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a70:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1a75:	8b 48 3f             	mov    0x3f(%rax),%ecx
    1a78:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    1a7f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a85:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1a8b:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1a90:	8b 48 42             	mov    0x42(%rax),%ecx
    1a93:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a99:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1aa0:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1aa5:	8b 48 45             	mov    0x45(%rax),%ecx
    1aa8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1aae:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1ab4:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1ab8:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1abf:	8b 48 18             	mov    0x18(%rax),%ecx
    1ac2:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1ac8:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1acc:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1ad2:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1ad7:	8b 48 1b             	mov    0x1b(%rax),%ecx
    1ada:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1ae1:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1ae7:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1aec:	8b 48 1e             	mov    0x1e(%rax),%ecx
    1aef:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1af3:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1af9:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1aff:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1b04:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1b09:	8b 48 21             	mov    0x21(%rax),%ecx
    1b0c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1b11:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    1b15:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1b1b:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b21:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1b25:	8b 48 24             	mov    0x24(%rax),%ecx
    1b28:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b2e:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1b33:	8b 48 27             	mov    0x27(%rax),%ecx
    1b36:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b3c:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1b41:	8b 48 2a             	mov    0x2a(%rax),%ecx
    1b44:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b4a:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1b4f:	8b 48 2d             	mov    0x2d(%rax),%ecx
    1b52:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b58:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1b5c:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1b62:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1b68:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1b6e:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    1b75:	8b 08                	mov    (%rax),%ecx
    1b77:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    1b7e:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1b85:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1b8b:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1b90:	8b 48 03             	mov    0x3(%rax),%ecx
    1b93:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    1b97:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    1b9d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1ba3:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1ba8:	8b 48 06             	mov    0x6(%rax),%ecx
    1bab:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    1bb2:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1bb8:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1bbd:	8b 48 09             	mov    0x9(%rax),%ecx
    1bc0:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1bc4:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1bca:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1bd0:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1bd6:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1bdb:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1bdf:	8b 48 0c             	mov    0xc(%rax),%ecx
    1be2:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1be7:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1bee:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1bf2:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1bf8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1bfe:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1c04:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1c09:	8b 48 0f             	mov    0xf(%rax),%ecx
    1c0c:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1c12:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1c18:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    1c1e:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1c23:	8b 48 12             	mov    0x12(%rax),%ecx
    1c26:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1c2c:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    1c33:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1c38:	8b 48 15             	mov    0x15(%rax),%ecx
    1c3b:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1c41:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    1c47:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1c4b:	c4 e3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm7,%xmm7
    1c52:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1c56:	49 83 c1 20          	add    $0x20,%r9
    1c5a:	48 83 c0 60          	add    $0x60,%rax
    1c5e:	48 83 c2 60          	add    $0x60,%rdx
    1c62:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    1c66:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    1c6c:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    1c73:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    1c77:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    1c7b:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1c81:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    1c87:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    1c8d:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1c91:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1c96:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    1c9c:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1ca1:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1ca5:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1cab:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1cb0:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    1cb6:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1cbb:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1cc0:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1cc5:	49 39 c8             	cmp    %rcx,%r8
    1cc8:	0f 83 a2 fc ff ff    	jae    1970 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x960>
    1cce:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1cd3:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1cd8:	4d 8d 59 08          	lea    0x8(%r9),%r11
    1cdc:	4d 39 d8             	cmp    %r11,%r8
    1cdf:	0f 82 4d 01 00 00    	jb     1e32 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe22>
    1ce5:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1cea:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    1cee:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1cf6 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xce6>
    1cf5:	00 
    1cf6:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    1cfb:	4a 8d 0c 13          	lea    (%rbx,%r10,1),%rcx
    1cff:	4d 01 e2             	add    %r12,%r10
    1d02:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1d08:	4c 8b 21             	mov    (%rcx),%r12
    1d0b:	48 8b 41 08          	mov    0x8(%rcx),%rax
    1d0f:	49 83 c2 18          	add    $0x18,%r10
    1d13:	48 83 c1 18          	add    $0x18,%rcx
    1d17:	48 8b 51 f8          	mov    -0x8(%rcx),%rdx
    1d1b:	4d 89 e1             	mov    %r12,%r9
    1d1e:	4d 89 e5             	mov    %r12,%r13
    1d21:	49 89 c6             	mov    %rax,%r14
    1d24:	49 c1 ed 30          	shr    $0x30,%r13
    1d28:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d2f:	41 89 d7             	mov    %edx,%r15d
    1d32:	49 c1 ee 20          	shr    $0x20,%r14
    1d36:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1d3b:	4d 89 e1             	mov    %r12,%r9
    1d3e:	41 89 c4             	mov    %eax,%r12d
    1d41:	41 c1 e7 08          	shl    $0x8,%r15d
    1d45:	41 c1 e4 10          	shl    $0x10,%r12d
    1d49:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1d50:	49 c1 e9 18          	shr    $0x18,%r9
    1d54:	45 09 ec             	or     %r13d,%r12d
    1d57:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1d5c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d63:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    1d68:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1d6f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1d74:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1d79:	41 89 c4             	mov    %eax,%r12d
    1d7c:	48 c1 e8 38          	shr    $0x38,%rax
    1d80:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1d86:	41 09 c7             	or     %eax,%r15d
    1d89:	41 c1 ec 08          	shr    $0x8,%r12d
    1d8d:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1d94:	4d 89 d9             	mov    %r11,%r9
    1d97:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1d9e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1da3:	49 83 c3 08          	add    $0x8,%r11
    1da7:	42 0f b6 04 3f       	movzbl (%rdi,%r15,1),%eax
    1dac:	49 89 d7             	mov    %rdx,%r15
    1daf:	48 c1 ea 28          	shr    $0x28,%rdx
    1db3:	49 c1 ef 10          	shr    $0x10,%r15
    1db7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1dbb:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1dc2:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
    1dc9:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1dce:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1dd4:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
    1ddb:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1ddf:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1de5:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1dec:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1df0:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1df6:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1dfb:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1dff:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1e05:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1e0a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1e0f:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1e13:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1e19:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    1e1f:	4d 39 d8             	cmp    %r11,%r8
    1e22:	0f 83 e0 fe ff ff    	jae    1d08 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcf8>
    1e28:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1e2d:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1e32:	4d 39 c1             	cmp    %r8,%r9
    1e35:	0f 83 15 02 00 00    	jae    2050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1e3b:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1e3f:	4c 8d 14 03          	lea    (%rbx,%rax,1),%r10
    1e43:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1e48:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1e4d:	45 0f b6 12          	movzbl (%r10),%r10d
    1e51:	c1 e2 08             	shl    $0x8,%edx
    1e54:	41 c1 e3 10          	shl    $0x10,%r11d
    1e58:	44 09 da             	or     %r11d,%edx
    1e5b:	44 09 d2             	or     %r10d,%edx
    1e5e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1e62:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    1e66:	41 8b 12             	mov    (%r10),%edx
    1e69:	45 0f b7 12          	movzwl (%r10),%r10d
    1e6d:	c1 ea 10             	shr    $0x10,%edx
    1e70:	66 45 89 14 04       	mov    %r10w,(%r12,%rax,1)
    1e75:	41 88 54 04 02       	mov    %dl,0x2(%r12,%rax,1)
    1e7a:	49 8d 51 01          	lea    0x1(%r9),%rdx
    1e7e:	4c 39 c2             	cmp    %r8,%rdx
    1e81:	0f 83 c9 01 00 00    	jae    2050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1e87:	4c 8d 54 03 03       	lea    0x3(%rbx,%rax,1),%r10
    1e8c:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1e91:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1e96:	45 0f b6 12          	movzbl (%r10),%r10d
    1e9a:	41 c1 e3 10          	shl    $0x10,%r11d
    1e9e:	c1 e2 08             	shl    $0x8,%edx
    1ea1:	44 09 da             	or     %r11d,%edx
    1ea4:	44 09 d2             	or     %r10d,%edx
    1ea7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1eab:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1eaf:	44 8b 12             	mov    (%rdx),%r10d
    1eb2:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1eb6:	49 8d 51 02          	lea    0x2(%r9),%rdx
    1eba:	44 89 d1             	mov    %r10d,%ecx
    1ebd:	66 45 89 5c 04 03    	mov    %r11w,0x3(%r12,%rax,1)
    1ec3:	c1 e9 10             	shr    $0x10,%ecx
    1ec6:	41 88 4c 04 05       	mov    %cl,0x5(%r12,%rax,1)
    1ecb:	4c 39 c2             	cmp    %r8,%rdx
    1ece:	0f 83 7c 01 00 00    	jae    2050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1ed4:	4c 8d 54 03 06       	lea    0x6(%rbx,%rax,1),%r10
    1ed9:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1ede:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1ee3:	45 0f b6 12          	movzbl (%r10),%r10d
    1ee7:	41 c1 e3 10          	shl    $0x10,%r11d
    1eeb:	c1 e2 08             	shl    $0x8,%edx
    1eee:	44 09 da             	or     %r11d,%edx
    1ef1:	44 09 d2             	or     %r10d,%edx
    1ef4:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1ef8:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1efc:	44 8b 12             	mov    (%rdx),%r10d
    1eff:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1f03:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1f07:	44 89 d1             	mov    %r10d,%ecx
    1f0a:	66 45 89 5c 04 06    	mov    %r11w,0x6(%r12,%rax,1)
    1f10:	c1 e9 10             	shr    $0x10,%ecx
    1f13:	41 88 4c 04 08       	mov    %cl,0x8(%r12,%rax,1)
    1f18:	4c 39 c2             	cmp    %r8,%rdx
    1f1b:	0f 83 2f 01 00 00    	jae    2050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1f21:	4c 8d 54 03 09       	lea    0x9(%rbx,%rax,1),%r10
    1f26:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1f2b:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1f30:	45 0f b6 12          	movzbl (%r10),%r10d
    1f34:	41 c1 e3 08          	shl    $0x8,%r11d
    1f38:	c1 e2 10             	shl    $0x10,%edx
    1f3b:	44 09 da             	or     %r11d,%edx
    1f3e:	44 09 d2             	or     %r10d,%edx
    1f41:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1f45:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1f49:	44 8b 12             	mov    (%rdx),%r10d
    1f4c:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1f50:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1f54:	44 89 d1             	mov    %r10d,%ecx
    1f57:	66 45 89 5c 04 09    	mov    %r11w,0x9(%r12,%rax,1)
    1f5d:	c1 e9 10             	shr    $0x10,%ecx
    1f60:	41 88 4c 04 0b       	mov    %cl,0xb(%r12,%rax,1)
    1f65:	4c 39 c2             	cmp    %r8,%rdx
    1f68:	0f 83 e2 00 00 00    	jae    2050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1f6e:	4c 8d 54 03 0c       	lea    0xc(%rbx,%rax,1),%r10
    1f73:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1f78:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1f7d:	45 0f b6 12          	movzbl (%r10),%r10d
    1f81:	41 c1 e3 08          	shl    $0x8,%r11d
    1f85:	c1 e2 10             	shl    $0x10,%edx
    1f88:	44 09 da             	or     %r11d,%edx
    1f8b:	44 09 d2             	or     %r10d,%edx
    1f8e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1f92:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1f96:	44 8b 12             	mov    (%rdx),%r10d
    1f99:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1f9d:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1fa1:	44 89 d1             	mov    %r10d,%ecx
    1fa4:	66 45 89 5c 04 0c    	mov    %r11w,0xc(%r12,%rax,1)
    1faa:	c1 e9 10             	shr    $0x10,%ecx
    1fad:	41 88 4c 04 0e       	mov    %cl,0xe(%r12,%rax,1)
    1fb2:	4c 39 c2             	cmp    %r8,%rdx
    1fb5:	0f 83 95 00 00 00    	jae    2050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1fbb:	4c 8d 54 03 0f       	lea    0xf(%rbx,%rax,1),%r10
    1fc0:	49 83 c1 06          	add    $0x6,%r9
    1fc4:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1fc9:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1fce:	45 0f b6 12          	movzbl (%r10),%r10d
    1fd2:	41 c1 e3 08          	shl    $0x8,%r11d
    1fd6:	c1 e2 10             	shl    $0x10,%edx
    1fd9:	44 09 da             	or     %r11d,%edx
    1fdc:	44 09 d2             	or     %r10d,%edx
    1fdf:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1fe3:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1fe7:	44 8b 12             	mov    (%rdx),%r10d
    1fea:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1fee:	44 89 d1             	mov    %r10d,%ecx
    1ff1:	66 45 89 5c 04 0f    	mov    %r11w,0xf(%r12,%rax,1)
    1ff7:	c1 e9 10             	shr    $0x10,%ecx
    1ffa:	41 88 4c 04 11       	mov    %cl,0x11(%r12,%rax,1)
    1fff:	4d 39 c1             	cmp    %r8,%r9
    2002:	73 4c                	jae    2050 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    2004:	48 8d 54 03 12       	lea    0x12(%rbx,%rax,1),%rdx
    2009:	4d 8d 44 04 12       	lea    0x12(%r12,%rax,1),%r8
    200e:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    2012:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    2016:	0f b6 12             	movzbl (%rdx),%edx
    2019:	c1 e0 08             	shl    $0x8,%eax
    201c:	c1 e1 10             	shl    $0x10,%ecx
    201f:	09 c8                	or     %ecx,%eax
    2021:	09 d0                	or     %edx,%eax
    2023:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2027:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    202b:	8b 02                	mov    (%rdx),%eax
    202d:	0f b7 12             	movzwl (%rdx),%edx
    2030:	c1 e8 10             	shr    $0x10,%eax
    2033:	66 41 89 10          	mov    %dx,(%r8)
    2037:	41 88 40 02          	mov    %al,0x2(%r8)
    203b:	c5 f8 77             	vzeroupper
    203e:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2042:	5b                   	pop    %rbx
    2043:	41 5c                	pop    %r12
    2045:	41 5d                	pop    %r13
    2047:	41 5e                	pop    %r14
    2049:	41 5f                	pop    %r15
    204b:	5d                   	pop    %rbp
    204c:	c3                   	ret
    204d:	0f 1f 00             	nopl   (%rax)
    2050:	c5 f8 77             	vzeroupper
    2053:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2057:	5b                   	pop    %rbx
    2058:	41 5c                	pop    %r12
    205a:	41 5d                	pop    %r13
    205c:	41 5e                	pop    %r14
    205e:	41 5f                	pop    %r15
    2060:	5d                   	pop    %rbp
    2061:	c3                   	ret
    2062:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    2068:	4d 89 c1             	mov    %r8,%r9
    206b:	e9 68 fc ff ff       	jmp    1cd8 <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    2070:	c3                   	ret
    2071:	48 8d 41 28          	lea    0x28(%rcx),%rax
    2075:	49 89 c9             	mov    %rcx,%r9
    2078:	e9 c2 f8 ff ff       	jmp    193f <jshc_channel::avx2_chain_inplace_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x92f>
