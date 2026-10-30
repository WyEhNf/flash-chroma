
artifacts/skylake-stream-linux-build-v1/CMakeFiles/jshc_skylake_stream.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 c9 0e 00 00    	je     ed6 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xed6>
       d:	55                   	push   %rbp
       e:	49 89 d0             	mov    %rdx,%r8
      11:	48 89 d0             	mov    %rdx,%rax
      14:	45 31 c9             	xor    %r9d,%r9d
      17:	48 89 e5             	mov    %rsp,%rbp
      1a:	41 57                	push   %r15
      1c:	41 56                	push   %r14
      1e:	41 55                	push   %r13
      20:	41 54                	push   %r12
      22:	53                   	push   %rbx
      23:	eb 48                	jmp    6d <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x6d>
      25:	0f 1f 00             	nopl   (%rax)
      28:	0f b6 50 01          	movzbl 0x1(%rax),%edx
      2c:	44 0f b6 50 02       	movzbl 0x2(%rax),%r10d
      31:	49 ff c1             	inc    %r9
      34:	48 83 c0 03          	add    $0x3,%rax
      38:	41 c1 e2 10          	shl    $0x10,%r10d
      3c:	c1 e2 08             	shl    $0x8,%edx
      3f:	44 09 d2             	or     %r10d,%edx
      42:	44 0f b6 50 fd       	movzbl -0x3(%rax),%r10d
      47:	44 09 d2             	or     %r10d,%edx
      4a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      4e:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
      52:	41 8b 12             	mov    (%r10),%edx
      55:	45 0f b7 12          	movzwl (%r10),%r10d
      59:	c1 ea 10             	shr    $0x10,%edx
      5c:	66 44 89 50 fd       	mov    %r10w,-0x3(%rax)
      61:	88 50 ff             	mov    %dl,-0x1(%rax)
      64:	4c 39 c9             	cmp    %r9,%rcx
      67:	0f 84 35 0b 00 00    	je     ba2 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xba2>
      6d:	a8 3f                	test   $0x3f,%al
      6f:	75 b7                	jne    28 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x28>
      71:	49 8d 41 48          	lea    0x48(%r9),%rax
      75:	48 39 c1             	cmp    %rax,%rcx
      78:	0f 82 59 0e 00 00    	jb     ed7 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xed7>
      7e:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      82:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 8a <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8a>
      89:	00 
      8a:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 92 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x92>
      91:	00 
      92:	4c 01 c0             	add    %r8,%rax
      95:	0f 1f 00             	nopl   (%rax)
      98:	44 8b 60 0c          	mov    0xc(%rax),%r12d
      9c:	44 8b 70 12          	mov    0x12(%rax),%r14d
      a0:	8b 10                	mov    (%rax),%edx
      a2:	44 8b 58 06          	mov    0x6(%rax),%r11d
      a6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
      ad:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
      b4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
      b9:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
      be:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
      c4:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
      cb:	44 8b 60 0f          	mov    0xf(%rax),%r12d
      cf:	44 8b 70 15          	mov    0x15(%rax),%r14d
      d3:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
      d9:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
      df:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
      e6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
      ed:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
      f2:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
      f7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
      fc:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     101:	8b 50 03             	mov    0x3(%rax),%edx
     104:	44 8b 58 09          	mov    0x9(%rax),%r11d
     108:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     10f:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     116:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     11c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     123:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     129:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     12d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     132:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     136:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     13b:	c4 63 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm9,%xmm9
     142:	8b 50 18             	mov    0x18(%rax),%edx
     145:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     14c:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     150:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     156:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     15d:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     162:	8b 50 1b             	mov    0x1b(%rax),%edx
     165:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     169:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     16e:	44 8b 58 21          	mov    0x21(%rax),%r11d
     172:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     178:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     17e:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     183:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     18a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     18e:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     193:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     198:	44 8b 60 24          	mov    0x24(%rax),%r12d
     19c:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     1a0:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     1a6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     1ad:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     1b4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     1b9:	44 8b 60 27          	mov    0x27(%rax),%r12d
     1bd:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     1c2:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
     1c6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     1cd:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     1d3:	c4 e3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm6,%xmm6
     1da:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     1e1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     1e6:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     1ec:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     1f1:	8b 50 30             	mov    0x30(%rax),%edx
     1f4:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     1fb:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     1ff:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     206:	44 8b 70 42          	mov    0x42(%rax),%r14d
     20a:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     210:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     217:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     21c:	8b 50 33             	mov    0x33(%rax),%edx
     21f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     223:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     228:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     22f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     234:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     239:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     23d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     243:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     24a:	44 8b 58 36          	mov    0x36(%rax),%r11d
     24e:	44 8b 70 45          	mov    0x45(%rax),%r14d
     252:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     259:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     25d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     264:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     268:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     26d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     272:	44 8b 58 39          	mov    0x39(%rax),%r11d
     276:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     27d:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     283:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     288:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     28d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     294:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     299:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     29e:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     2a4:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     2a8:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     2ae:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     2b4:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     2ba:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     2c0:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     2c7:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     2cb:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     2d2:	44 8b 60 54          	mov    0x54(%rax),%r12d
     2d6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2dd:	c4 e3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm5,%xmm5
     2e4:	8b 50 48             	mov    0x48(%rax),%edx
     2e7:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     2eb:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     2f0:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2f7:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     2fc:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     301:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     305:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     30b:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     312:	44 8b 60 57          	mov    0x57(%rax),%r12d
     316:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     31a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     321:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     326:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     32a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     331:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     336:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     33c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     341:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     348:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     34e:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     354:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     359:	8b 50 4b             	mov    0x4b(%rax),%edx
     35c:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     361:	44 8b 58 51          	mov    0x51(%rax),%r11d
     365:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     36c:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     371:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     378:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     37e:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     384:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     388:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     38f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     393:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     399:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     39f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     3a4:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     3a8:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     3ad:	c4 63 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm8,%xmm8
     3b4:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     3bb:	8b 50 60             	mov    0x60(%rax),%edx
     3be:	44 8b 60 6c          	mov    0x6c(%rax),%r12d
     3c2:	44 8b 70 72          	mov    0x72(%rax),%r14d
     3c6:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     3cc:	44 8b 58 66          	mov    0x66(%rax),%r11d
     3d0:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     3d4:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     3db:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     3e2:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     3e8:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     3ed:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     3f2:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     3f7:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     3fe:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     403:	44 8b 60 6f          	mov    0x6f(%rax),%r12d
     407:	44 8b 70 75          	mov    0x75(%rax),%r14d
     40b:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     410:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     416:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     41c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     423:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     42a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     42f:	8b 50 63             	mov    0x63(%rax),%edx
     432:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     437:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     43c:	44 8b 58 69          	mov    0x69(%rax),%r11d
     440:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     446:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     44c:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     453:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     45a:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     461:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     465:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     46a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     46e:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     473:	c4 e3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm7,%xmm7
     47a:	8b 50 78             	mov    0x78(%rax),%edx
     47d:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     484:	44 8b 58 7e          	mov    0x7e(%rax),%r11d
     488:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     48e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     495:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     49a:	8b 50 7b             	mov    0x7b(%rax),%edx
     49d:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     4a1:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     4a6:	44 8b 98 81 00 00 00 	mov    0x81(%rax),%r11d
     4ad:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     4b3:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     4b9:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     4be:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     4c5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     4c9:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     4ce:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     4d3:	44 8b a0 84 00 00 00 	mov    0x84(%rax),%r12d
     4da:	44 8b b0 8a 00 00 00 	mov    0x8a(%rax),%r14d
     4e1:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     4e6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     4ed:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     4f4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     4f9:	44 8b a0 87 00 00 00 	mov    0x87(%rax),%r12d
     500:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     505:	44 8b b0 8d 00 00 00 	mov    0x8d(%rax),%r14d
     50c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     513:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     519:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     520:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     527:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     52c:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     532:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     537:	44 8b 98 96 00 00 00 	mov    0x96(%rax),%r11d
     53e:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     545:	44 8b a0 9c 00 00 00 	mov    0x9c(%rax),%r12d
     54c:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     553:	44 8b b0 a2 00 00 00 	mov    0xa2(%rax),%r14d
     55a:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     561:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     568:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     56d:	44 8b 98 99 00 00 00 	mov    0x99(%rax),%r11d
     574:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     578:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     57e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     585:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     58a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     58f:	44 8b a0 9f 00 00 00 	mov    0x9f(%rax),%r12d
     596:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     59d:	c4 e3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm0,%xmm0
     5a4:	8b 90 90 00 00 00    	mov    0x90(%rax),%edx
     5aa:	44 8b b0 a5 00 00 00 	mov    0xa5(%rax),%r14d
     5b1:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5b8:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     5bd:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     5c3:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     5c7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5cc:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     5d1:	8b 90 93 00 00 00    	mov    0x93(%rax),%edx
     5d7:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5de:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     5e4:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5e9:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     5ee:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     5f4:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     5f9:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5fd:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     603:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     609:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     60e:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     615:	44 8b b0 ba 00 00 00 	mov    0xba(%rax),%r14d
     61c:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     623:	44 8b a0 b4 00 00 00 	mov    0xb4(%rax),%r12d
     62a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     631:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     638:	44 8b 98 ae 00 00 00 	mov    0xae(%rax),%r11d
     63f:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     643:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     649:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     650:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     655:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     65a:	44 8b b0 bd 00 00 00 	mov    0xbd(%rax),%r14d
     661:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     668:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
     66f:	44 8b a0 b7 00 00 00 	mov    0xb7(%rax),%r12d
     676:	8b 90 a8 00 00 00    	mov    0xa8(%rax),%edx
     67c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     683:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     688:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     68d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     694:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     699:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     69f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     6a5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     6aa:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     6b0:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     6b6:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     6bb:	44 8b 98 b1 00 00 00 	mov    0xb1(%rax),%r11d
     6c2:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     6c7:	8b 90 ab 00 00 00    	mov    0xab(%rax),%edx
     6cd:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     6d4:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     6d9:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     6e0:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     6e7:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     6ec:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     6f2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     6f7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6fb:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     6ff:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     705:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     70c:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
     713:	4c 89 ca             	mov    %r9,%rdx
     716:	49 83 c1 40          	add    $0x40,%r9
     71a:	48 05 c0 00 00 00    	add    $0xc0,%rax
     720:	4c 8d 92 88 00 00 00 	lea    0x88(%rdx),%r10
     727:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     72c:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     731:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     737:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     73d:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     742:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     748:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     74e:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     753:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     758:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     75d:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     762:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     768:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     76e:	c5 7d e7 88 40 ff ff 	vmovntdq %ymm9,-0xc0(%rax)
     775:	ff 
     776:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     77a:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     77e:	c5 fd e7 b0 60 ff ff 	vmovntdq %ymm6,-0xa0(%rax)
     785:	ff 
     786:	c5 fd e7 68 80       	vmovntdq %ymm5,-0x80(%rax)
     78b:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     78f:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     793:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     799:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     79f:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     7a5:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     7ab:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     7b0:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     7b4:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     7ba:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     7c0:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     7c6:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     7cc:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     7d2:	c5 fd e7 68 a0       	vmovntdq %ymm5,-0x60(%rax)
     7d7:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     7dc:	c5 fd e7 48 e0       	vmovntdq %ymm1,-0x20(%rax)
     7e1:	4c 39 d1             	cmp    %r10,%rcx
     7e4:	0f 83 ae f8 ff ff    	jae    98 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x98>
     7ea:	0f ae f8             	sfence
     7ed:	48 83 c2 68          	add    $0x68,%rdx
     7f1:	48 39 d1             	cmp    %rdx,%rcx
     7f4:	0f 82 a8 03 00 00    	jb     ba2 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xba2>
     7fa:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     7fe:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 806 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x806>
     805:	00 
     806:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 80e <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x80e>
     80d:	00 
     80e:	4c 01 c0             	add    %r8,%rax
     811:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     818:	44 8b 60 54          	mov    0x54(%rax),%r12d
     81c:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     820:	8b 50 48             	mov    0x48(%rax),%edx
     823:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     827:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     82e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     835:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     83a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     83f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     845:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     84c:	44 8b 60 57          	mov    0x57(%rax),%r12d
     850:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     854:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     85a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     860:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     867:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     86e:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     873:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     878:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     87d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     882:	8b 50 4b             	mov    0x4b(%rax),%edx
     885:	44 8b 58 51          	mov    0x51(%rax),%r11d
     889:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     890:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     897:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     89d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     8a4:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     8aa:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     8ae:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     8b3:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     8b7:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     8bc:	c4 e3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm5,%xmm5
     8c3:	8b 50 30             	mov    0x30(%rax),%edx
     8c6:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     8cd:	44 8b 58 36          	mov    0x36(%rax),%r11d
     8d1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     8d7:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     8de:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     8e3:	8b 50 33             	mov    0x33(%rax),%edx
     8e6:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     8ea:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     8ef:	44 8b 58 39          	mov    0x39(%rax),%r11d
     8f3:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     8f9:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     8ff:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     904:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     90b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     90f:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     914:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     919:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     91d:	44 8b 70 42          	mov    0x42(%rax),%r14d
     921:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     926:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     92d:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     934:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     939:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     93d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     942:	44 8b 70 45          	mov    0x45(%rax),%r14d
     946:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     94d:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     953:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     95a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     961:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     966:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     96c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     971:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     975:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     97c:	44 8b 60 24          	mov    0x24(%rax),%r12d
     980:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     987:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     98b:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     992:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     999:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     99e:	44 8b 58 21          	mov    0x21(%rax),%r11d
     9a2:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     9a6:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     9ac:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     9b3:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     9b8:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9bd:	44 8b 60 27          	mov    0x27(%rax),%r12d
     9c1:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9c8:	c4 e3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm0,%xmm0
     9cf:	8b 50 18             	mov    0x18(%rax),%edx
     9d2:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
     9d6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     9dd:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     9e2:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     9e8:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     9ec:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     9f1:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     9f6:	8b 50 1b             	mov    0x1b(%rax),%edx
     9f9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a00:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     a06:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a0b:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     a10:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     a16:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     a1b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     a1f:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     a25:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     a29:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     a2f:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     a35:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     a3a:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     a41:	44 8b 70 12          	mov    0x12(%rax),%r14d
     a45:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     a4c:	44 8b 60 0c          	mov    0xc(%rax),%r12d
     a50:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a57:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     a5e:	44 8b 58 06          	mov    0x6(%rax),%r11d
     a62:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     a66:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     a6c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a73:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a78:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a7d:	44 8b 70 15          	mov    0x15(%rax),%r14d
     a81:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a88:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
     a8f:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     a93:	8b 10                	mov    (%rax),%edx
     a95:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a9c:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     aa1:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     aa5:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     aac:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     ab1:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     ab7:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     abd:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     ac2:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     ac8:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     ace:	44 0f b6 14 17       	movzbl (%rdi,%rdx,1),%r10d
     ad3:	44 8b 58 09          	mov    0x9(%rax),%r11d
     ad7:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     adc:	8b 50 03             	mov    0x3(%rax),%edx
     adf:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     ae6:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     aeb:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
     af2:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     af9:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     afe:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     b02:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     b08:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b0d:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     b13:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     b17:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     b1b:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     b21:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     b27:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     b2e:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     b34:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
     b3b:	49 8d 51 48          	lea    0x48(%r9),%rdx
     b3f:	49 83 c1 20          	add    $0x20,%r9
     b43:	48 83 c0 60          	add    $0x60,%rax
     b47:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     b4b:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
     b4f:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     b55:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     b5b:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
     b61:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
     b65:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     b6a:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
     b70:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     b75:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     b79:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     b7f:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     b84:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
     b8a:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     b8f:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     b94:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     b99:	48 39 d1             	cmp    %rdx,%rcx
     b9c:	0f 83 76 fc ff ff    	jae    818 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x818>
     ba2:	4d 8d 51 08          	lea    0x8(%r9),%r10
     ba6:	4c 39 d1             	cmp    %r10,%rcx
     ba9:	0f 82 25 01 00 00    	jb     cd4 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcd4>
     baf:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     bb3:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # bbb <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbbb>
     bba:	00 
     bbb:	4c 01 c0             	add    %r8,%rax
     bbe:	66 90                	xchg   %ax,%ax
     bc0:	48 8b 18             	mov    (%rax),%rbx
     bc3:	48 8b 50 08          	mov    0x8(%rax),%rdx
     bc7:	48 83 c0 18          	add    $0x18,%rax
     bcb:	4c 8b 68 f8          	mov    -0x8(%rax),%r13
     bcf:	49 89 d9             	mov    %rbx,%r9
     bd2:	49 89 d6             	mov    %rdx,%r14
     bd5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bdc:	45 89 ef             	mov    %r13d,%r15d
     bdf:	49 c1 ee 20          	shr    $0x20,%r14
     be3:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     be8:	49 89 d9             	mov    %rbx,%r9
     beb:	48 c1 eb 30          	shr    $0x30,%rbx
     bef:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     bf6:	41 c1 e7 08          	shl    $0x8,%r15d
     bfa:	49 89 dc             	mov    %rbx,%r12
     bfd:	89 d3                	mov    %edx,%ebx
     bff:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     c04:	c1 e3 10             	shl    $0x10,%ebx
     c07:	49 c1 e9 18          	shr    $0x18,%r9
     c0b:	44 09 e3             	or     %r12d,%ebx
     c0e:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     c14:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c1b:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     c21:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c26:	44 0f b6 24 1f       	movzbl (%rdi,%rbx,1),%r12d
     c2b:	89 d3                	mov    %edx,%ebx
     c2d:	48 c1 ea 38          	shr    $0x38,%rdx
     c31:	44 09 fa             	or     %r15d,%edx
     c34:	4d 89 ef             	mov    %r13,%r15
     c37:	49 c1 ed 28          	shr    $0x28,%r13
     c3b:	49 c1 ef 10          	shr    $0x10,%r15
     c3f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     c45:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     c4a:	c1 eb 08             	shr    $0x8,%ebx
     c4d:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     c54:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     c58:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     c5c:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     c61:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
     c67:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
     c6e:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     c74:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
     c7b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     c82:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     c86:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     c8c:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     c93:	4d 89 d1             	mov    %r10,%r9
     c96:	49 83 c2 08          	add    $0x8,%r10
     c9a:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     c9e:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     ca4:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     ca9:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     cad:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     cb3:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     cb8:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     cbd:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     cc1:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     cc6:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     ccb:	4c 39 d1             	cmp    %r10,%rcx
     cce:	0f 83 ec fe ff ff    	jae    bc0 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbc0>
     cd4:	49 39 c9             	cmp    %rcx,%r9
     cd7:	0f 83 eb 01 00 00    	jae    ec8 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec8>
     cdd:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
     ce1:	4d 8d 14 10          	lea    (%r8,%rdx,1),%r10
     ce5:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     cea:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     cef:	c1 e0 08             	shl    $0x8,%eax
     cf2:	41 c1 e3 10          	shl    $0x10,%r11d
     cf6:	44 09 d8             	or     %r11d,%eax
     cf9:	45 0f b6 1a          	movzbl (%r10),%r11d
     cfd:	44 09 d8             	or     %r11d,%eax
     d00:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d04:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d08:	41 8b 03             	mov    (%r11),%eax
     d0b:	45 0f b7 1b          	movzwl (%r11),%r11d
     d0f:	c1 e8 10             	shr    $0x10,%eax
     d12:	66 45 89 1a          	mov    %r11w,(%r10)
     d16:	41 88 42 02          	mov    %al,0x2(%r10)
     d1a:	49 8d 41 01          	lea    0x1(%r9),%rax
     d1e:	48 39 c8             	cmp    %rcx,%rax
     d21:	0f 83 a1 01 00 00    	jae    ec8 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec8>
     d27:	4d 8d 54 10 03       	lea    0x3(%r8,%rdx,1),%r10
     d2c:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d31:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d36:	c1 e0 08             	shl    $0x8,%eax
     d39:	41 c1 e3 10          	shl    $0x10,%r11d
     d3d:	44 09 d8             	or     %r11d,%eax
     d40:	45 0f b6 1a          	movzbl (%r10),%r11d
     d44:	44 09 d8             	or     %r11d,%eax
     d47:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d4b:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d4f:	41 8b 03             	mov    (%r11),%eax
     d52:	45 0f b7 1b          	movzwl (%r11),%r11d
     d56:	c1 e8 10             	shr    $0x10,%eax
     d59:	66 45 89 1a          	mov    %r11w,(%r10)
     d5d:	41 88 42 02          	mov    %al,0x2(%r10)
     d61:	49 8d 41 02          	lea    0x2(%r9),%rax
     d65:	48 39 c8             	cmp    %rcx,%rax
     d68:	0f 83 5a 01 00 00    	jae    ec8 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec8>
     d6e:	4d 8d 54 10 06       	lea    0x6(%r8,%rdx,1),%r10
     d73:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d78:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d7d:	c1 e0 08             	shl    $0x8,%eax
     d80:	41 c1 e3 10          	shl    $0x10,%r11d
     d84:	44 09 d8             	or     %r11d,%eax
     d87:	45 0f b6 1a          	movzbl (%r10),%r11d
     d8b:	44 09 d8             	or     %r11d,%eax
     d8e:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d92:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d96:	41 8b 03             	mov    (%r11),%eax
     d99:	45 0f b7 1b          	movzwl (%r11),%r11d
     d9d:	c1 e8 10             	shr    $0x10,%eax
     da0:	66 45 89 1a          	mov    %r11w,(%r10)
     da4:	41 88 42 02          	mov    %al,0x2(%r10)
     da8:	49 8d 41 03          	lea    0x3(%r9),%rax
     dac:	48 39 c8             	cmp    %rcx,%rax
     daf:	0f 83 13 01 00 00    	jae    ec8 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec8>
     db5:	4d 8d 54 10 09       	lea    0x9(%r8,%rdx,1),%r10
     dba:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     dbf:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     dc4:	c1 e0 10             	shl    $0x10,%eax
     dc7:	41 c1 e3 08          	shl    $0x8,%r11d
     dcb:	44 09 d8             	or     %r11d,%eax
     dce:	45 0f b6 1a          	movzbl (%r10),%r11d
     dd2:	44 09 d8             	or     %r11d,%eax
     dd5:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     dd9:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     ddd:	41 8b 03             	mov    (%r11),%eax
     de0:	45 0f b7 1b          	movzwl (%r11),%r11d
     de4:	c1 e8 10             	shr    $0x10,%eax
     de7:	66 45 89 1a          	mov    %r11w,(%r10)
     deb:	41 88 42 02          	mov    %al,0x2(%r10)
     def:	49 8d 41 04          	lea    0x4(%r9),%rax
     df3:	48 39 c8             	cmp    %rcx,%rax
     df6:	0f 83 cc 00 00 00    	jae    ec8 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec8>
     dfc:	4d 8d 54 10 0c       	lea    0xc(%r8,%rdx,1),%r10
     e01:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e06:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e0b:	c1 e0 10             	shl    $0x10,%eax
     e0e:	41 c1 e3 08          	shl    $0x8,%r11d
     e12:	44 09 d8             	or     %r11d,%eax
     e15:	45 0f b6 1a          	movzbl (%r10),%r11d
     e19:	44 09 d8             	or     %r11d,%eax
     e1c:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e20:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e24:	41 8b 03             	mov    (%r11),%eax
     e27:	45 0f b7 1b          	movzwl (%r11),%r11d
     e2b:	c1 e8 10             	shr    $0x10,%eax
     e2e:	66 45 89 1a          	mov    %r11w,(%r10)
     e32:	41 88 42 02          	mov    %al,0x2(%r10)
     e36:	49 8d 41 05          	lea    0x5(%r9),%rax
     e3a:	48 39 c8             	cmp    %rcx,%rax
     e3d:	0f 83 85 00 00 00    	jae    ec8 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec8>
     e43:	4d 8d 54 10 0f       	lea    0xf(%r8,%rdx,1),%r10
     e48:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e4d:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e52:	c1 e0 10             	shl    $0x10,%eax
     e55:	41 c1 e3 08          	shl    $0x8,%r11d
     e59:	44 09 d8             	or     %r11d,%eax
     e5c:	45 0f b6 1a          	movzbl (%r10),%r11d
     e60:	44 09 d8             	or     %r11d,%eax
     e63:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e67:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e6b:	41 8b 03             	mov    (%r11),%eax
     e6e:	45 0f b7 1b          	movzwl (%r11),%r11d
     e72:	c1 e8 10             	shr    $0x10,%eax
     e75:	66 45 89 1a          	mov    %r11w,(%r10)
     e79:	41 88 42 02          	mov    %al,0x2(%r10)
     e7d:	49 8d 41 06          	lea    0x6(%r9),%rax
     e81:	48 39 c8             	cmp    %rcx,%rax
     e84:	73 42                	jae    ec8 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec8>
     e86:	49 8d 54 10 12       	lea    0x12(%r8,%rdx,1),%rdx
     e8b:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     e8f:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     e93:	c1 e0 08             	shl    $0x8,%eax
     e96:	c1 e1 10             	shl    $0x10,%ecx
     e99:	09 c8                	or     %ecx,%eax
     e9b:	0f b6 0a             	movzbl (%rdx),%ecx
     e9e:	09 c8                	or     %ecx,%eax
     ea0:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     ea4:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     ea8:	8b 01                	mov    (%rcx),%eax
     eaa:	0f b7 09             	movzwl (%rcx),%ecx
     ead:	c1 e8 10             	shr    $0x10,%eax
     eb0:	66 89 0a             	mov    %cx,(%rdx)
     eb3:	88 42 02             	mov    %al,0x2(%rdx)
     eb6:	c5 f8 77             	vzeroupper
     eb9:	5b                   	pop    %rbx
     eba:	41 5c                	pop    %r12
     ebc:	41 5d                	pop    %r13
     ebe:	41 5e                	pop    %r14
     ec0:	41 5f                	pop    %r15
     ec2:	5d                   	pop    %rbp
     ec3:	c3                   	ret
     ec4:	0f 1f 40 00          	nopl   0x0(%rax)
     ec8:	c5 f8 77             	vzeroupper
     ecb:	5b                   	pop    %rbx
     ecc:	41 5c                	pop    %r12
     ece:	41 5d                	pop    %r13
     ed0:	41 5e                	pop    %r14
     ed2:	41 5f                	pop    %r15
     ed4:	5d                   	pop    %rbp
     ed5:	c3                   	ret
     ed6:	c3                   	ret
     ed7:	49 8d 51 28          	lea    0x28(%r9),%rdx
     edb:	e9 11 f9 ff ff       	jmp    7f1 <jshc_channel::avx2_chain_stream(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7f1>

0000000000000ee0 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     ee0:	f3 0f 1e fa          	endbr64
     ee4:	4d 85 c0             	test   %r8,%r8
     ee7:	0f 84 ad 0f 00 00    	je     1e9a <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfba>
     eed:	55                   	push   %rbp
     eee:	49 89 d1             	mov    %rdx,%r9
     ef1:	48 89 e5             	mov    %rsp,%rbp
     ef4:	41 57                	push   %r15
     ef6:	41 56                	push   %r14
     ef8:	41 55                	push   %r13
     efa:	41 54                	push   %r12
     efc:	49 89 d4             	mov    %rdx,%r12
     eff:	31 d2                	xor    %edx,%edx
     f01:	53                   	push   %rbx
     f02:	48 89 cb             	mov    %rcx,%rbx
     f05:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     f09:	eb 4f                	jmp    f5a <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7a>
     f0b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     f10:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     f15:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     f1a:	48 ff c2             	inc    %rdx
     f1d:	48 83 c1 03          	add    $0x3,%rcx
     f21:	49 83 c1 03          	add    $0x3,%r9
     f25:	41 c1 e2 10          	shl    $0x10,%r10d
     f29:	c1 e0 08             	shl    $0x8,%eax
     f2c:	44 09 d0             	or     %r10d,%eax
     f2f:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
     f34:	44 09 d0             	or     %r10d,%eax
     f37:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f3b:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
     f3f:	41 8b 02             	mov    (%r10),%eax
     f42:	45 0f b7 12          	movzwl (%r10),%r10d
     f46:	c1 e8 10             	shr    $0x10,%eax
     f49:	66 44 89 51 fd       	mov    %r10w,-0x3(%rcx)
     f4e:	88 41 ff             	mov    %al,-0x1(%rcx)
     f51:	49 39 d0             	cmp    %rdx,%r8
     f54:	0f 84 be 0b 00 00    	je     1b18 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc38>
     f5a:	f6 c1 3f             	test   $0x3f,%cl
     f5d:	75 b1                	jne    f10 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x30>
     f5f:	48 8d 42 48          	lea    0x48(%rdx),%rax
     f63:	49 39 c0             	cmp    %rax,%r8
     f66:	0f 82 2f 0f 00 00    	jb     1e9b <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfbb>
     f6c:	48 8d 0c 52          	lea    (%rdx,%rdx,2),%rcx
     f70:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # f78 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x98>
     f77:	00 
     f78:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # f80 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa0>
     f7f:	00 
     f80:	4c 89 64 24 f8       	mov    %r12,-0x8(%rsp)
     f85:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
     f8a:	49 8d 04 0c          	lea    (%r12,%rcx,1),%rax
     f8e:	48 01 d9             	add    %rbx,%rcx
     f91:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     f98:	44 8b 08             	mov    (%rax),%r9d
     f9b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fa2:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     fa7:	44 8b 48 03          	mov    0x3(%rax),%r9d
     fab:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fb2:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
     fb8:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     fbd:	44 8b 48 06          	mov    0x6(%rax),%r9d
     fc1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fc8:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
     fcf:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     fd4:	44 8b 48 09          	mov    0x9(%rax),%r9d
     fd8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fdf:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     fe4:	44 8b 48 0c          	mov    0xc(%rax),%r9d
     fe8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fef:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     ff4:	44 8b 48 0f          	mov    0xf(%rax),%r9d
     ff8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fff:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1005:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    100a:	44 8b 48 12          	mov    0x12(%rax),%r9d
    100e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1015:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    101c:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1021:	44 8b 48 15          	mov    0x15(%rax),%r9d
    1025:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    102c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1032:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1037:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    103e:	44 8b 48 18          	mov    0x18(%rax),%r9d
    1042:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1049:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    104d:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1053:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1058:	44 8b 48 1b          	mov    0x1b(%rax),%r9d
    105c:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1063:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    106a:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    106f:	44 8b 48 1e          	mov    0x1e(%rax),%r9d
    1073:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    1077:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    107d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1084:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    1089:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    108e:	44 8b 48 21          	mov    0x21(%rax),%r9d
    1092:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
    1097:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    109e:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    10a3:	44 8b 48 24          	mov    0x24(%rax),%r9d
    10a7:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
    10ad:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10b4:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    10b9:	44 8b 48 27          	mov    0x27(%rax),%r9d
    10bd:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
    10c4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10cb:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    10d1:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    10d6:	44 8b 48 2a          	mov    0x2a(%rax),%r9d
    10da:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10e1:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    10e8:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    10ed:	44 8b 48 2d          	mov    0x2d(%rax),%r9d
    10f1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10f8:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    10fe:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1103:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    110a:	44 8b 48 30          	mov    0x30(%rax),%r9d
    110e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1115:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1119:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    111f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1124:	44 8b 48 33          	mov    0x33(%rax),%r9d
    1128:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    112f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1136:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    113b:	44 8b 48 36          	mov    0x36(%rax),%r9d
    113f:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    1143:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    1149:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1150:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1155:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    115a:	44 8b 48 39          	mov    0x39(%rax),%r9d
    115e:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    1163:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    1167:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    116d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1174:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    117a:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    117f:	44 8b 48 3c          	mov    0x3c(%rax),%r9d
    1183:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    118a:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    118f:	44 8b 48 3f          	mov    0x3f(%rax),%r9d
    1193:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    119a:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    119f:	44 8b 48 42          	mov    0x42(%rax),%r9d
    11a3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11aa:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    11af:	44 8b 48 45          	mov    0x45(%rax),%r9d
    11b3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11ba:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    11bf:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    11c5:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    11cb:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    11d1:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    11d8:	44 8b 48 48          	mov    0x48(%rax),%r9d
    11dc:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    11e3:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    11ea:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11f1:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    11f6:	44 8b 48 4b          	mov    0x4b(%rax),%r9d
    11fa:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    11fe:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1204:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    120b:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
    1211:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1216:	44 8b 48 4e          	mov    0x4e(%rax),%r9d
    121a:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1221:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1228:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
    122f:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1234:	44 8b 48 51          	mov    0x51(%rax),%r9d
    1238:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    123c:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    1242:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1249:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    124e:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1253:	44 8b 48 54          	mov    0x54(%rax),%r9d
    1257:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    125c:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    1260:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1266:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    126d:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    1273:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1278:	44 8b 48 57          	mov    0x57(%rax),%r9d
    127c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1283:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1289:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    128e:	44 8b 48 5a          	mov    0x5a(%rax),%r9d
    1292:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1299:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    12a0:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    12a5:	44 8b 48 5d          	mov    0x5d(%rax),%r9d
    12a9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12b0:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    12b6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    12bb:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    12c2:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    12c6:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    12cc:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    12d3:	44 8b 48 60          	mov    0x60(%rax),%r9d
    12d7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12de:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    12e2:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    12e7:	44 8b 48 63          	mov    0x63(%rax),%r9d
    12eb:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    12f1:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    12f6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12fd:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
    1303:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    1308:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    130d:	44 8b 48 66          	mov    0x66(%rax),%r9d
    1311:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1318:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
    131f:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1324:	44 8b 48 69          	mov    0x69(%rax),%r9d
    1328:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    132f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1334:	44 8b 48 6c          	mov    0x6c(%rax),%r9d
    1338:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    133f:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1344:	44 8b 48 6f          	mov    0x6f(%rax),%r9d
    1348:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    134f:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1355:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    135a:	44 8b 48 72          	mov    0x72(%rax),%r9d
    135e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1365:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    136c:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1371:	44 8b 48 75          	mov    0x75(%rax),%r9d
    1375:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    137c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1382:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1387:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    138e:	44 8b 48 78          	mov    0x78(%rax),%r9d
    1392:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1399:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    139d:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    13a3:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    13a8:	44 8b 48 7b          	mov    0x7b(%rax),%r9d
    13ac:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    13b3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13ba:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    13bf:	44 8b 48 7e          	mov    0x7e(%rax),%r9d
    13c3:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    13c7:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    13cd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13d4:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    13d9:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    13de:	44 8b 88 81 00 00 00 	mov    0x81(%rax),%r9d
    13e5:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    13ea:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13f1:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    13f6:	44 8b 88 84 00 00 00 	mov    0x84(%rax),%r9d
    13fd:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1403:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    140a:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    140f:	44 8b 88 87 00 00 00 	mov    0x87(%rax),%r9d
    1416:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    141d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1424:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    142a:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    142f:	44 8b 88 8a 00 00 00 	mov    0x8a(%rax),%r9d
    1436:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    143d:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1444:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1449:	44 8b 88 8d 00 00 00 	mov    0x8d(%rax),%r9d
    1450:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1457:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    145d:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1462:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    1469:	44 8b 88 90 00 00 00 	mov    0x90(%rax),%r9d
    1470:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1477:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    147b:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1481:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1486:	44 8b 88 93 00 00 00 	mov    0x93(%rax),%r9d
    148d:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1494:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    149b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    14a0:	44 8b 88 96 00 00 00 	mov    0x96(%rax),%r9d
    14a7:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    14ab:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    14b1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14b8:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    14bd:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    14c2:	44 8b 88 99 00 00 00 	mov    0x99(%rax),%r9d
    14c9:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    14ce:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14d5:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    14da:	44 8b 88 9c 00 00 00 	mov    0x9c(%rax),%r9d
    14e1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14e8:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    14ed:	44 8b 88 9f 00 00 00 	mov    0x9f(%rax),%r9d
    14f4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14fb:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1500:	44 8b 88 a2 00 00 00 	mov    0xa2(%rax),%r9d
    1507:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    150e:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1513:	44 8b 88 a5 00 00 00 	mov    0xa5(%rax),%r9d
    151a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1521:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1526:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    152c:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1532:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1538:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    153f:	44 8b 88 a8 00 00 00 	mov    0xa8(%rax),%r9d
    1546:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    154d:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1554:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    155b:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1560:	44 8b 88 ab 00 00 00 	mov    0xab(%rax),%r9d
    1567:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    156c:	c4 21 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm10
    1572:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1579:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    157e:	44 8b 88 ae 00 00 00 	mov    0xae(%rax),%r9d
    1585:	c4 63 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm10,%xmm10
    158c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1593:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1598:	44 8b 88 b1 00 00 00 	mov    0xb1(%rax),%r9d
    159f:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    15a4:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    15aa:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    15b0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15b7:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    15bc:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    15c1:	44 8b 88 b4 00 00 00 	mov    0xb4(%rax),%r9d
    15c8:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    15cd:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    15d4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15db:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    15e0:	44 8b 88 b7 00 00 00 	mov    0xb7(%rax),%r9d
    15e7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15ee:	c4 21 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm10
    15f4:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    15f9:	44 8b 88 ba 00 00 00 	mov    0xba(%rax),%r9d
    1600:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1607:	c4 23 29 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm10,%xmm10
    160e:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1613:	44 8b 88 bd 00 00 00 	mov    0xbd(%rax),%r9d
    161a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1621:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1627:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    162c:	c4 23 21 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm11,%xmm11
    1633:	49 89 d1             	mov    %rdx,%r9
    1636:	48 83 c2 40          	add    $0x40,%rdx
    163a:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1640:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
    1647:	48 81 c1 c0 00 00 00 	add    $0xc0,%rcx
    164e:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1653:	c4 21 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm11
    1659:	c4 63 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm11,%xmm11
    1660:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    1665:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    166a:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    1670:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    1676:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    167b:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    1681:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    1687:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    168c:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    1691:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    1696:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    169b:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    16a1:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    16a7:	c5 7d e7 89 40 ff ff 	vmovntdq %ymm9,-0xc0(%rcx)
    16ae:	ff 
    16af:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    16b3:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    16b7:	c5 fd e7 b1 60 ff ff 	vmovntdq %ymm6,-0xa0(%rcx)
    16be:	ff 
    16bf:	c5 fd e7 69 80       	vmovntdq %ymm5,-0x80(%rcx)
    16c4:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    16c8:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    16cc:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    16d2:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    16d8:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    16de:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    16e4:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    16e9:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    16ed:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    16f3:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    16f9:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    16ff:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    1705:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    170b:	c5 fd e7 69 a0       	vmovntdq %ymm5,-0x60(%rcx)
    1710:	c5 fd e7 41 c0       	vmovntdq %ymm0,-0x40(%rcx)
    1715:	c5 fd e7 49 e0       	vmovntdq %ymm1,-0x20(%rcx)
    171a:	4d 39 d0             	cmp    %r10,%r8
    171d:	0f 83 75 f8 ff ff    	jae    f98 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb8>
    1723:	4c 8b 64 24 f8       	mov    -0x8(%rsp),%r12
    1728:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
    172d:	49 83 c1 68          	add    $0x68,%r9
    1731:	0f ae f8             	sfence
    1734:	4d 39 c8             	cmp    %r9,%r8
    1737:	0f 82 db 03 00 00    	jb     1b18 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc38>
    173d:	48 8d 0c 52          	lea    (%rdx,%rdx,2),%rcx
    1741:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1749 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x869>
    1748:	00 
    1749:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1751 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x871>
    1750:	00 
    1751:	4c 89 64 24 f8       	mov    %r12,-0x8(%rsp)
    1756:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
    175b:	49 8d 04 0c          	lea    (%r12,%rcx,1),%rax
    175f:	48 01 d9             	add    %rbx,%rcx
    1762:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1768:	44 8b 48 48          	mov    0x48(%rax),%r9d
    176c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1773:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1778:	44 8b 48 4b          	mov    0x4b(%rax),%r9d
    177c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1783:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    1789:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    178e:	44 8b 48 4e          	mov    0x4e(%rax),%r9d
    1792:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1799:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    17a0:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    17a5:	44 8b 48 51          	mov    0x51(%rax),%r9d
    17a9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17b0:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    17b5:	44 8b 48 54          	mov    0x54(%rax),%r9d
    17b9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17c0:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    17c5:	44 8b 48 57          	mov    0x57(%rax),%r9d
    17c9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17d0:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    17d6:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    17db:	44 8b 48 5a          	mov    0x5a(%rax),%r9d
    17df:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17e6:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    17ed:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    17f2:	44 8b 48 5d          	mov    0x5d(%rax),%r9d
    17f6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17fd:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1803:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1808:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    180f:	44 8b 48 30          	mov    0x30(%rax),%r9d
    1813:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    181a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    181e:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1824:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1829:	44 8b 48 33          	mov    0x33(%rax),%r9d
    182d:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1834:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    183b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1840:	44 8b 48 36          	mov    0x36(%rax),%r9d
    1844:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    1848:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    184e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1855:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    185a:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    185f:	44 8b 48 39          	mov    0x39(%rax),%r9d
    1863:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1868:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    186f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1874:	44 8b 48 3c          	mov    0x3c(%rax),%r9d
    1878:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    187e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1885:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    188a:	44 8b 48 3f          	mov    0x3f(%rax),%r9d
    188e:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    1895:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    189c:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    18a2:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    18a7:	44 8b 48 42          	mov    0x42(%rax),%r9d
    18ab:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18b2:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    18b9:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    18be:	44 8b 48 45          	mov    0x45(%rax),%r9d
    18c2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18c9:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    18cf:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    18d4:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    18db:	44 8b 48 18          	mov    0x18(%rax),%r9d
    18df:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18e6:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    18ea:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    18f0:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    18f5:	44 8b 48 1b          	mov    0x1b(%rax),%r9d
    18f9:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1900:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1907:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    190c:	44 8b 48 1e          	mov    0x1e(%rax),%r9d
    1910:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1914:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    191a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1921:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1926:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    192b:	44 8b 48 21          	mov    0x21(%rax),%r9d
    192f:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1934:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    1938:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    193e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1945:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    194a:	44 8b 48 24          	mov    0x24(%rax),%r9d
    194e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1955:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    195a:	44 8b 48 27          	mov    0x27(%rax),%r9d
    195e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1965:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    196a:	44 8b 48 2a          	mov    0x2a(%rax),%r9d
    196e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1975:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    197a:	44 8b 48 2d          	mov    0x2d(%rax),%r9d
    197e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1985:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    198a:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1990:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1996:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    199c:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
    19a3:	44 8b 08             	mov    (%rax),%r9d
    19a6:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    19ad:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    19b4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19bb:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    19c0:	44 8b 48 03          	mov    0x3(%rax),%r9d
    19c4:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    19c8:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    19ce:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19d5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    19da:	44 8b 48 06          	mov    0x6(%rax),%r9d
    19de:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    19e5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19ec:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    19f1:	44 8b 48 09          	mov    0x9(%rax),%r9d
    19f5:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    19f9:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    19ff:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1a05:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a0c:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1a11:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1a16:	44 8b 48 0c          	mov    0xc(%rax),%r9d
    1a1a:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1a1f:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1a26:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1a2a:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1a30:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a37:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1a3d:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1a42:	44 8b 48 0f          	mov    0xf(%rax),%r9d
    1a46:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1a4c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a53:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    1a59:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1a5e:	44 8b 48 12          	mov    0x12(%rax),%r9d
    1a62:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a69:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    1a70:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1a75:	44 8b 48 15          	mov    0x15(%rax),%r9d
    1a79:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a80:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    1a86:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1a8b:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    1a92:	4c 8d 4a 48          	lea    0x48(%rdx),%r9
    1a96:	48 83 c2 20          	add    $0x20,%rdx
    1a9a:	48 83 c0 60          	add    $0x60,%rax
    1a9e:	48 83 c1 60          	add    $0x60,%rcx
    1aa2:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    1aa6:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    1aac:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    1ab3:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    1ab7:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    1abb:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1ac1:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    1ac7:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    1acd:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1ad1:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1ad6:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    1adc:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1ae1:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1ae5:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1aeb:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1af0:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    1af6:	c5 fe 7f 51 a0       	vmovdqu %ymm2,-0x60(%rcx)
    1afb:	c5 fe 7f 49 c0       	vmovdqu %ymm1,-0x40(%rcx)
    1b00:	c5 fe 7f 41 e0       	vmovdqu %ymm0,-0x20(%rcx)
    1b05:	4d 39 c8             	cmp    %r9,%r8
    1b08:	0f 83 5a fc ff ff    	jae    1768 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x888>
    1b0e:	4c 8b 64 24 f8       	mov    -0x8(%rsp),%r12
    1b13:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
    1b18:	4c 8d 52 08          	lea    0x8(%rdx),%r10
    1b1c:	4d 39 d0             	cmp    %r10,%r8
    1b1f:	0f 82 4d 01 00 00    	jb     1c72 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd92>
    1b25:	4c 89 64 24 f8       	mov    %r12,-0x8(%rsp)
    1b2a:	4c 8d 0c 52          	lea    (%rdx,%rdx,2),%r9
    1b2e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1b36 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc56>
    1b35:	00 
    1b36:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
    1b3b:	4b 8d 0c 0c          	lea    (%r12,%r9,1),%rcx
    1b3f:	49 01 d9             	add    %rbx,%r9
    1b42:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1b48:	4c 8b 21             	mov    (%rcx),%r12
    1b4b:	48 8b 41 08          	mov    0x8(%rcx),%rax
    1b4f:	49 83 c1 18          	add    $0x18,%r9
    1b53:	48 83 c1 18          	add    $0x18,%rcx
    1b57:	48 8b 51 f8          	mov    -0x8(%rcx),%rdx
    1b5b:	4d 89 e3             	mov    %r12,%r11
    1b5e:	4d 89 e5             	mov    %r12,%r13
    1b61:	49 89 c6             	mov    %rax,%r14
    1b64:	49 c1 ed 30          	shr    $0x30,%r13
    1b68:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1b6f:	41 89 d7             	mov    %edx,%r15d
    1b72:	49 c1 ee 20          	shr    $0x20,%r14
    1b76:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1b7b:	4d 89 e3             	mov    %r12,%r11
    1b7e:	41 89 c4             	mov    %eax,%r12d
    1b81:	41 c1 e7 08          	shl    $0x8,%r15d
    1b85:	41 c1 e4 10          	shl    $0x10,%r12d
    1b89:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1b90:	49 c1 eb 18          	shr    $0x18,%r11
    1b94:	45 09 ec             	or     %r13d,%r12d
    1b97:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1b9c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1ba3:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    1ba8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1baf:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1bb4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1bb9:	41 89 c4             	mov    %eax,%r12d
    1bbc:	48 c1 e8 38          	shr    $0x38,%rax
    1bc0:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1bc6:	41 09 c7             	or     %eax,%r15d
    1bc9:	41 c1 ec 08          	shr    $0x8,%r12d
    1bcd:	c4 a3 79 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm0,%xmm0
    1bd4:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1bdb:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1be0:	42 0f b6 04 3f       	movzbl (%rdi,%r15,1),%eax
    1be5:	49 89 d7             	mov    %rdx,%r15
    1be8:	48 c1 ea 28          	shr    $0x28,%rdx
    1bec:	49 c1 ef 10          	shr    $0x10,%r15
    1bf0:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1bf4:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1bfb:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
    1c02:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1c07:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1c0d:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
    1c14:	4c 89 d2             	mov    %r10,%rdx
    1c17:	49 83 c2 08          	add    $0x8,%r10
    1c1b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1c1f:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1c25:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1c2c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1c30:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1c36:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1c3b:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1c3f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1c45:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1c4a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1c4f:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1c53:	c4 c1 79 d6 41 f8    	vmovq  %xmm0,-0x8(%r9)
    1c59:	c4 c1 7a 7f 49 e8    	vmovdqu %xmm1,-0x18(%r9)
    1c5f:	4d 39 d0             	cmp    %r10,%r8
    1c62:	0f 83 e0 fe ff ff    	jae    1b48 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc68>
    1c68:	4c 8b 64 24 f8       	mov    -0x8(%rsp),%r12
    1c6d:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
    1c72:	4c 39 c2             	cmp    %r8,%rdx
    1c75:	0f 83 0d 02 00 00    	jae    1e88 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfa8>
    1c7b:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
    1c7f:	4d 8d 14 04          	lea    (%r12,%rax,1),%r10
    1c83:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    1c88:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1c8d:	45 0f b6 12          	movzbl (%r10),%r10d
    1c91:	c1 e1 08             	shl    $0x8,%ecx
    1c94:	41 c1 e3 10          	shl    $0x10,%r11d
    1c98:	44 09 d9             	or     %r11d,%ecx
    1c9b:	44 09 d1             	or     %r10d,%ecx
    1c9e:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1ca2:	4c 8d 14 8e          	lea    (%rsi,%rcx,4),%r10
    1ca6:	41 8b 0a             	mov    (%r10),%ecx
    1ca9:	45 0f b7 12          	movzwl (%r10),%r10d
    1cad:	c1 e9 10             	shr    $0x10,%ecx
    1cb0:	66 44 89 14 03       	mov    %r10w,(%rbx,%rax,1)
    1cb5:	88 4c 03 02          	mov    %cl,0x2(%rbx,%rax,1)
    1cb9:	48 8d 4a 01          	lea    0x1(%rdx),%rcx
    1cbd:	4c 39 c1             	cmp    %r8,%rcx
    1cc0:	0f 83 c2 01 00 00    	jae    1e88 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfa8>
    1cc6:	4d 8d 54 04 03       	lea    0x3(%r12,%rax,1),%r10
    1ccb:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    1cd0:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1cd5:	45 0f b6 12          	movzbl (%r10),%r10d
    1cd9:	41 c1 e3 10          	shl    $0x10,%r11d
    1cdd:	c1 e1 08             	shl    $0x8,%ecx
    1ce0:	44 09 d9             	or     %r11d,%ecx
    1ce3:	44 09 d1             	or     %r10d,%ecx
    1ce6:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1cea:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1cee:	44 8b 11             	mov    (%rcx),%r10d
    1cf1:	44 0f b7 19          	movzwl (%rcx),%r11d
    1cf5:	48 8d 4a 02          	lea    0x2(%rdx),%rcx
    1cf9:	41 c1 ea 10          	shr    $0x10,%r10d
    1cfd:	66 44 89 5c 03 03    	mov    %r11w,0x3(%rbx,%rax,1)
    1d03:	44 88 54 03 05       	mov    %r10b,0x5(%rbx,%rax,1)
    1d08:	4c 39 c1             	cmp    %r8,%rcx
    1d0b:	0f 83 77 01 00 00    	jae    1e88 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfa8>
    1d11:	4d 8d 54 04 06       	lea    0x6(%r12,%rax,1),%r10
    1d16:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    1d1b:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1d20:	45 0f b6 12          	movzbl (%r10),%r10d
    1d24:	41 c1 e3 10          	shl    $0x10,%r11d
    1d28:	c1 e1 08             	shl    $0x8,%ecx
    1d2b:	44 09 d9             	or     %r11d,%ecx
    1d2e:	44 09 d1             	or     %r10d,%ecx
    1d31:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1d35:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1d39:	44 8b 11             	mov    (%rcx),%r10d
    1d3c:	44 0f b7 19          	movzwl (%rcx),%r11d
    1d40:	48 8d 4a 03          	lea    0x3(%rdx),%rcx
    1d44:	41 c1 ea 10          	shr    $0x10,%r10d
    1d48:	66 44 89 5c 03 06    	mov    %r11w,0x6(%rbx,%rax,1)
    1d4e:	44 88 54 03 08       	mov    %r10b,0x8(%rbx,%rax,1)
    1d53:	4c 39 c1             	cmp    %r8,%rcx
    1d56:	0f 83 2c 01 00 00    	jae    1e88 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfa8>
    1d5c:	4d 8d 54 04 09       	lea    0x9(%r12,%rax,1),%r10
    1d61:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    1d66:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1d6b:	45 0f b6 12          	movzbl (%r10),%r10d
    1d6f:	41 c1 e3 08          	shl    $0x8,%r11d
    1d73:	c1 e1 10             	shl    $0x10,%ecx
    1d76:	44 09 d9             	or     %r11d,%ecx
    1d79:	44 09 d1             	or     %r10d,%ecx
    1d7c:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1d80:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1d84:	44 8b 11             	mov    (%rcx),%r10d
    1d87:	44 0f b7 19          	movzwl (%rcx),%r11d
    1d8b:	48 8d 4a 04          	lea    0x4(%rdx),%rcx
    1d8f:	41 c1 ea 10          	shr    $0x10,%r10d
    1d93:	66 44 89 5c 03 09    	mov    %r11w,0x9(%rbx,%rax,1)
    1d99:	44 88 54 03 0b       	mov    %r10b,0xb(%rbx,%rax,1)
    1d9e:	4c 39 c1             	cmp    %r8,%rcx
    1da1:	0f 83 e1 00 00 00    	jae    1e88 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfa8>
    1da7:	4d 8d 54 04 0c       	lea    0xc(%r12,%rax,1),%r10
    1dac:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    1db1:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1db6:	45 0f b6 12          	movzbl (%r10),%r10d
    1dba:	41 c1 e3 08          	shl    $0x8,%r11d
    1dbe:	c1 e1 10             	shl    $0x10,%ecx
    1dc1:	44 09 d9             	or     %r11d,%ecx
    1dc4:	44 09 d1             	or     %r10d,%ecx
    1dc7:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1dcb:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1dcf:	44 8b 11             	mov    (%rcx),%r10d
    1dd2:	44 0f b7 19          	movzwl (%rcx),%r11d
    1dd6:	48 8d 4a 05          	lea    0x5(%rdx),%rcx
    1dda:	41 c1 ea 10          	shr    $0x10,%r10d
    1dde:	66 44 89 5c 03 0c    	mov    %r11w,0xc(%rbx,%rax,1)
    1de4:	44 88 54 03 0e       	mov    %r10b,0xe(%rbx,%rax,1)
    1de9:	4c 39 c1             	cmp    %r8,%rcx
    1dec:	0f 83 96 00 00 00    	jae    1e88 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfa8>
    1df2:	4d 8d 54 04 0f       	lea    0xf(%r12,%rax,1),%r10
    1df7:	48 83 c2 06          	add    $0x6,%rdx
    1dfb:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    1e00:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1e05:	45 0f b6 12          	movzbl (%r10),%r10d
    1e09:	41 c1 e3 08          	shl    $0x8,%r11d
    1e0d:	c1 e1 10             	shl    $0x10,%ecx
    1e10:	44 09 d9             	or     %r11d,%ecx
    1e13:	44 09 d1             	or     %r10d,%ecx
    1e16:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1e1a:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1e1e:	44 8b 11             	mov    (%rcx),%r10d
    1e21:	44 0f b7 19          	movzwl (%rcx),%r11d
    1e25:	41 c1 ea 10          	shr    $0x10,%r10d
    1e29:	66 44 89 5c 03 0f    	mov    %r11w,0xf(%rbx,%rax,1)
    1e2f:	44 88 54 03 11       	mov    %r10b,0x11(%rbx,%rax,1)
    1e34:	4c 39 c2             	cmp    %r8,%rdx
    1e37:	73 4f                	jae    1e88 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfa8>
    1e39:	49 8d 54 04 12       	lea    0x12(%r12,%rax,1),%rdx
    1e3e:	4c 8d 44 03 12       	lea    0x12(%rbx,%rax,1),%r8
    1e43:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1e47:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1e4b:	0f b6 12             	movzbl (%rdx),%edx
    1e4e:	c1 e0 08             	shl    $0x8,%eax
    1e51:	c1 e1 10             	shl    $0x10,%ecx
    1e54:	09 c8                	or     %ecx,%eax
    1e56:	09 d0                	or     %edx,%eax
    1e58:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1e5c:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1e60:	8b 02                	mov    (%rdx),%eax
    1e62:	0f b7 12             	movzwl (%rdx),%edx
    1e65:	c1 e8 10             	shr    $0x10,%eax
    1e68:	66 41 89 10          	mov    %dx,(%r8)
    1e6c:	41 88 40 02          	mov    %al,0x2(%r8)
    1e70:	c5 f8 77             	vzeroupper
    1e73:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1e77:	5b                   	pop    %rbx
    1e78:	41 5c                	pop    %r12
    1e7a:	41 5d                	pop    %r13
    1e7c:	41 5e                	pop    %r14
    1e7e:	41 5f                	pop    %r15
    1e80:	5d                   	pop    %rbp
    1e81:	c3                   	ret
    1e82:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1e88:	c5 f8 77             	vzeroupper
    1e8b:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1e8f:	5b                   	pop    %rbx
    1e90:	41 5c                	pop    %r12
    1e92:	41 5d                	pop    %r13
    1e94:	41 5e                	pop    %r14
    1e96:	41 5f                	pop    %r15
    1e98:	5d                   	pop    %rbp
    1e99:	c3                   	ret
    1e9a:	c3                   	ret
    1e9b:	4c 8d 4a 28          	lea    0x28(%rdx),%r9
    1e9f:	e9 90 f8 ff ff       	jmp    1734 <jshc_channel::avx2_chain_stream_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x854>
