
F:\Hackathon\projects\16-lut-color\artifacts\skylake-qwordpack-linux-build-v1\CMakeFiles\jshc_skylake_qwordpack.dir\channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 13 0f 00 00    	je     f20 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf20>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
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
      89:	0f 84 81 0e 00 00    	je     f10 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf10>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 7f 0e 00 00    	jb     f21 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf21>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # ae <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # b6 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	c5 7d 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm12        # be <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbe>
      bd:	00 
      be:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # c6 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc6>
      c5:	00 
      c6:	48 01 d0             	add    %rdx,%rax
      c9:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # d1 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd1>
      d0:	00 
      d1:	eb 08                	jmp    db <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xdb>
      d3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      d8:	4d 89 c1             	mov    %r8,%r9
      db:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      e2:	4c 39 c1             	cmp    %r8,%rcx
      e5:	72 1c                	jb     103 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x103>
      e7:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      ee:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      f5:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
      fc:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     103:	44 8b 60 0c          	mov    0xc(%rax),%r12d
     107:	44 8b 70 12          	mov    0x12(%rax),%r14d
     10b:	44 8b 00             	mov    (%rax),%r8d
     10e:	44 8b 58 06          	mov    0x6(%rax),%r11d
     112:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     119:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     120:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     125:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     12a:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     131:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     138:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     13c:	44 8b 70 15          	mov    0x15(%rax),%r14d
     140:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     146:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     14c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     153:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     15a:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     15f:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     164:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     169:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     16e:	44 8b 40 03          	mov    0x3(%rax),%r8d
     172:	44 8b 58 09          	mov    0x9(%rax),%r11d
     176:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     17d:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     184:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     18b:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     192:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     198:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     19d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     1a2:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     1a6:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     1ab:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     1b2:	44 8b 40 18          	mov    0x18(%rax),%r8d
     1b6:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1bd:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     1c1:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1c8:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1cf:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     1d4:	44 8b 40 1b          	mov    0x1b(%rax),%r8d
     1d8:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     1dc:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     1e1:	44 8b 58 21          	mov    0x21(%rax),%r11d
     1e5:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     1eb:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1f2:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     1f7:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1fe:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     203:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     208:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     20d:	44 8b 60 24          	mov    0x24(%rax),%r12d
     211:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     215:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     21a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     221:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     228:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     22d:	44 8b 60 27          	mov    0x27(%rax),%r12d
     231:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     236:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
     23a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     241:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     247:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     24e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     255:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     25a:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     260:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     265:	44 8b 58 36          	mov    0x36(%rax),%r11d
     269:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     270:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     274:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     27b:	44 8b 70 42          	mov    0x42(%rax),%r14d
     27f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     286:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     28d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     292:	44 8b 58 39          	mov    0x39(%rax),%r11d
     296:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     29a:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     2a0:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2a7:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     2ac:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     2b1:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     2b5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     2bc:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     2c3:	44 8b 40 30          	mov    0x30(%rax),%r8d
     2c7:	44 8b 70 45          	mov    0x45(%rax),%r14d
     2cb:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2d2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     2d7:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2de:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     2e2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2e7:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     2ec:	44 8b 40 33          	mov    0x33(%rax),%r8d
     2f0:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2f7:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     2fd:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     302:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     307:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     30e:	c4 e2 1d 36 c9       	vpermd %ymm1,%ymm12,%ymm1
     313:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     318:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     31e:	c4 e3 45 02 f9 c0    	vpblendd $0xc0,%ymm1,%ymm7,%ymm7
     324:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     32a:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     330:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     337:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     33b:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     342:	44 8b 60 54          	mov    0x54(%rax),%r12d
     346:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     34d:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     354:	44 8b 40 48          	mov    0x48(%rax),%r8d
     358:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     35c:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     361:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     368:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     36d:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     372:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     376:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     37d:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     384:	44 8b 60 57          	mov    0x57(%rax),%r12d
     388:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     38c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     393:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     398:	c5 31 6c ca          	vpunpcklqdq %xmm2,%xmm9,%xmm9
     39c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     3a3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     3a8:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     3ae:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3b3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     3ba:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     3c0:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     3c6:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     3cb:	44 8b 40 4b          	mov    0x4b(%rax),%r8d
     3cf:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     3d4:	44 8b 58 51          	mov    0x51(%rax),%r11d
     3d8:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     3df:	c4 42 25 36 c9       	vpermd %ymm9,%ymm11,%ymm9
     3e4:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     3eb:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3f2:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     3f8:	c4 c3 75 0c c9 f0    	vblendps $0xf0,%ymm9,%ymm1,%ymm1
     3fe:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     405:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     40a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     40f:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     413:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     418:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     41f:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     426:	44 8b 40 60          	mov    0x60(%rax),%r8d
     42a:	44 8b 60 6c          	mov    0x6c(%rax),%r12d
     42e:	44 8b 70 72          	mov    0x72(%rax),%r14d
     432:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     439:	44 8b 58 66          	mov    0x66(%rax),%r11d
     43d:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     441:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     448:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     44f:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     455:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     45a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     45f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     464:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     46b:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     470:	44 8b 60 6f          	mov    0x6f(%rax),%r12d
     474:	44 8b 70 75          	mov    0x75(%rax),%r14d
     478:	c4 e2 2d 36 f6       	vpermd %ymm6,%ymm10,%ymm6
     47d:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     483:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     489:	c4 c3 4d 02 f1 03    	vpblendd $0x3,%ymm9,%ymm6,%ymm6
     48f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     496:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     49d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     4a2:	44 8b 40 63          	mov    0x63(%rax),%r8d
     4a6:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     4ab:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     4b0:	44 8b 58 69          	mov    0x69(%rax),%r11d
     4b4:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4bb:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     4c1:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     4c8:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     4cf:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     4d6:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     4db:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     4e0:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     4e4:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     4e9:	c4 a3 51 22 2c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm5,%xmm5
     4f0:	44 8b 40 78          	mov    0x78(%rax),%r8d
     4f4:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     4fb:	44 8b 58 7e          	mov    0x7e(%rax),%r11d
     4ff:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     506:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     50d:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     512:	44 8b 40 7b          	mov    0x7b(%rax),%r8d
     516:	c5 d1 6c ea          	vpunpcklqdq %xmm2,%xmm5,%xmm5
     51a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     51f:	44 8b 98 81 00 00 00 	mov    0x81(%rax),%r11d
     526:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     52c:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     533:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     538:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     53f:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     544:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     549:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     54e:	44 8b a0 84 00 00 00 	mov    0x84(%rax),%r12d
     555:	44 8b b0 8a 00 00 00 	mov    0x8a(%rax),%r14d
     55c:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
     561:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     568:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     56f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     574:	44 8b a0 87 00 00 00 	mov    0x87(%rax),%r12d
     57b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     580:	44 8b b0 8d 00 00 00 	mov    0x8d(%rax),%r14d
     587:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     58e:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     594:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
     59b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5a2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5a7:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     5ad:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5b2:	44 8b 98 96 00 00 00 	mov    0x96(%rax),%r11d
     5b9:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     5c0:	44 8b a0 9c 00 00 00 	mov    0x9c(%rax),%r12d
     5c7:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     5ce:	44 8b b0 a2 00 00 00 	mov    0xa2(%rax),%r14d
     5d5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     5dc:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5e3:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5e8:	44 8b 98 99 00 00 00 	mov    0x99(%rax),%r11d
     5ef:	c5 e9 6c d0          	vpunpcklqdq %xmm0,%xmm2,%xmm2
     5f3:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     5f9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     600:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     605:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     60a:	44 8b a0 9f 00 00 00 	mov    0x9f(%rax),%r12d
     611:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     618:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     61f:	44 8b 80 90 00 00 00 	mov    0x90(%rax),%r8d
     626:	44 8b b0 a5 00 00 00 	mov    0xa5(%rax),%r14d
     62d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     634:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     639:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     640:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
     645:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     64a:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     64f:	44 8b 80 93 00 00 00 	mov    0x93(%rax),%r8d
     656:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     65d:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     663:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     668:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     66d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     674:	c4 e2 1d 36 c0       	vpermd %ymm0,%ymm12,%ymm0
     679:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     67e:	c4 21 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm8
     684:	c4 e3 55 02 e8 c0    	vpblendd $0xc0,%ymm0,%ymm5,%ymm5
     68a:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     690:	c5 79 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm13
     695:	c4 23 39 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm8,%xmm8
     69c:	44 8b b0 ba 00 00 00 	mov    0xba(%rax),%r14d
     6a3:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     6aa:	44 8b a0 b4 00 00 00 	mov    0xb4(%rax),%r12d
     6b1:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     6b8:	c4 23 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm13,%xmm13
     6bf:	44 8b 98 ae 00 00 00 	mov    0xae(%rax),%r11d
     6c6:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
     6cb:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     6d1:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     6d8:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     6dd:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     6e2:	44 8b b0 bd 00 00 00 	mov    0xbd(%rax),%r14d
     6e9:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     6f0:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     6f7:	44 8b a0 b7 00 00 00 	mov    0xb7(%rax),%r12d
     6fe:	44 8b 80 a8 00 00 00 	mov    0xa8(%rax),%r8d
     705:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     70c:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     711:	c4 41 39 6c c5       	vpunpcklqdq %xmm13,%xmm8,%xmm8
     716:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     71d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     722:	c4 21 79 6e 2c ae    	vmovd  (%rsi,%r13,4),%xmm13
     728:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     72f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     734:	c4 63 3d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm8,%ymm8
     73a:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     740:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     745:	44 8b 98 b1 00 00 00 	mov    0xb1(%rax),%r11d
     74c:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     751:	44 8b 80 ab 00 00 00 	mov    0xab(%rax),%r8d
     758:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     75f:	c4 42 25 36 c0       	vpermd %ymm8,%ymm11,%ymm8
     764:	c4 23 11 22 2c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm13,%xmm13
     76b:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     772:	c5 79 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm14
     777:	c4 c3 7d 0c c0 f0    	vblendps $0xf0,%ymm8,%ymm0,%ymm0
     77d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     784:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     789:	48 05 c0 00 00 00    	add    $0xc0,%rax
     78f:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     794:	c5 11 6c ea          	vpunpcklqdq %xmm2,%xmm13,%xmm13
     798:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     79e:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     7a5:	c4 23 09 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm14,%xmm14
     7ac:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     7b3:	c5 fd e7 b8 40 ff ff 	vmovntdq %ymm7,-0xc0(%rax)
     7ba:	ff 
     7bb:	4d 8d 41 40          	lea    0x40(%r9),%r8
     7bf:	c5 fd e7 88 60 ff ff 	vmovntdq %ymm1,-0xa0(%rax)
     7c6:	ff 
     7c7:	c5 fd e7 70 80       	vmovntdq %ymm6,-0x80(%rax)
     7cc:	c5 fd e7 68 a0       	vmovntdq %ymm5,-0x60(%rax)
     7d1:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     7d6:	c4 c1 69 6c d6       	vpunpcklqdq %xmm14,%xmm2,%xmm2
     7db:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
     7e1:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     7e6:	c4 e2 2d 36 d2       	vpermd %ymm2,%ymm10,%ymm2
     7eb:	c4 c3 6d 02 d0 03    	vpblendd $0x3,%ymm8,%ymm2,%ymm2
     7f1:	c5 fd e7 50 e0       	vmovntdq %ymm2,-0x20(%rax)
     7f6:	4c 39 d1             	cmp    %r10,%rcx
     7f9:	0f 83 d9 f8 ff ff    	jae    d8 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd8>
     7ff:	0f ae f8             	sfence
     802:	49 8d 41 68          	lea    0x68(%r9),%rax
     806:	48 39 c1             	cmp    %rax,%rcx
     809:	0f 82 bf 03 00 00    	jb     bce <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbce>
     80f:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     813:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 81b <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x81b>
     81a:	00 
     81b:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 823 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x823>
     822:	00 
     823:	48 01 d0             	add    %rdx,%rax
     826:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     82d:	00 00 00 
     830:	44 8b 60 54          	mov    0x54(%rax),%r12d
     834:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     838:	44 8b 48 48          	mov    0x48(%rax),%r9d
     83c:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     840:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     847:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     84e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     853:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     858:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     85f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     866:	44 8b 60 57          	mov    0x57(%rax),%r12d
     86a:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     86e:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     874:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     87a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     881:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     888:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     88d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     892:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     897:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     89c:	44 8b 48 4b          	mov    0x4b(%rax),%r9d
     8a0:	44 8b 58 51          	mov    0x51(%rax),%r11d
     8a4:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     8ab:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     8b2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     8b9:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     8c0:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     8c6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     8cb:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     8d0:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     8d4:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     8d9:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
     8e0:	44 8b 48 30          	mov    0x30(%rax),%r9d
     8e4:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     8eb:	44 8b 58 36          	mov    0x36(%rax),%r11d
     8ef:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     8f6:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     8fd:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     902:	44 8b 48 33          	mov    0x33(%rax),%r9d
     906:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     90a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     90f:	44 8b 58 39          	mov    0x39(%rax),%r11d
     913:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     919:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     920:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     925:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     92c:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     931:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     936:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     93b:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     93f:	44 8b 70 42          	mov    0x42(%rax),%r14d
     943:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     948:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     94f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     956:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     95b:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     95f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     964:	44 8b 70 45          	mov    0x45(%rax),%r14d
     968:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     96f:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     975:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     97c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     983:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     988:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     98e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     993:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     997:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     99e:	44 8b 60 24          	mov    0x24(%rax),%r12d
     9a2:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     9a9:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     9ad:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9b4:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     9bb:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     9c0:	44 8b 58 21          	mov    0x21(%rax),%r11d
     9c4:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     9c8:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     9ce:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     9d5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     9da:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9df:	44 8b 60 27          	mov    0x27(%rax),%r12d
     9e3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9ea:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     9f1:	44 8b 48 18          	mov    0x18(%rax),%r9d
     9f5:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
     9f9:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a00:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a05:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     a0c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     a10:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a15:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     a1a:	44 8b 48 1b          	mov    0x1b(%rax),%r9d
     a1e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a25:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     a2b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a30:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     a35:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     a3c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     a41:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a46:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     a4c:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     a50:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     a56:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     a5c:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     a61:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     a68:	44 8b 70 12          	mov    0x12(%rax),%r14d
     a6c:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     a73:	44 8b 60 0c          	mov    0xc(%rax),%r12d
     a77:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a7e:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     a85:	44 8b 58 06          	mov    0x6(%rax),%r11d
     a89:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     a8d:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     a93:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a9a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a9f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     aa4:	44 8b 70 15          	mov    0x15(%rax),%r14d
     aa8:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     aaf:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     ab6:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     aba:	44 8b 08             	mov    (%rax),%r9d
     abd:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     ac4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     ac9:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     acd:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     ad4:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     ad9:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     adf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ae6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     aeb:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     af1:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     af7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     afc:	44 8b 58 09          	mov    0x9(%rax),%r11d
     b00:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     b05:	44 8b 48 03          	mov    0x3(%rax),%r9d
     b09:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     b10:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     b15:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
     b1c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     b23:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     b28:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     b2c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b33:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b38:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     b3e:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     b43:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     b47:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     b4d:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     b53:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     b5a:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     b60:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     b67:	4d 8d 48 48          	lea    0x48(%r8),%r9
     b6b:	49 83 c0 20          	add    $0x20,%r8
     b6f:	48 83 c0 60          	add    $0x60,%rax
     b73:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     b77:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
     b7b:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     b81:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     b87:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
     b8d:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
     b91:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     b96:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
     b9c:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     ba1:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     ba5:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     bab:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     bb0:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
     bb6:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     bbb:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     bc0:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     bc5:	4c 39 c9             	cmp    %r9,%rcx
     bc8:	0f 83 62 fc ff ff    	jae    830 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x830>
     bce:	4d 8d 48 08          	lea    0x8(%r8),%r9
     bd2:	4c 39 c9             	cmp    %r9,%rcx
     bd5:	0f 82 2d 01 00 00    	jb     d08 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd08>
     bdb:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     bdf:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # be7 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbe7>
     be6:	00 
     be7:	48 01 d0             	add    %rdx,%rax
     bea:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     bf0:	48 8b 18             	mov    (%rax),%rbx
     bf3:	4c 8b 40 08          	mov    0x8(%rax),%r8
     bf7:	48 83 c0 18          	add    $0x18,%rax
     bfb:	4c 8b 68 f8          	mov    -0x8(%rax),%r13
     bff:	49 89 da             	mov    %rbx,%r10
     c02:	4d 89 c6             	mov    %r8,%r14
     c05:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     c0c:	45 89 ef             	mov    %r13d,%r15d
     c0f:	49 c1 ee 20          	shr    $0x20,%r14
     c13:	46 0f b6 1c 17       	movzbl (%rdi,%r10,1),%r11d
     c18:	49 89 da             	mov    %rbx,%r10
     c1b:	48 c1 eb 30          	shr    $0x30,%rbx
     c1f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     c26:	41 c1 e7 08          	shl    $0x8,%r15d
     c2a:	49 89 dc             	mov    %rbx,%r12
     c2d:	44 89 c3             	mov    %r8d,%ebx
     c30:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     c35:	c1 e3 10             	shl    $0x10,%ebx
     c38:	49 c1 ea 18          	shr    $0x18,%r10
     c3c:	44 09 e3             	or     %r12d,%ebx
     c3f:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     c45:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     c4c:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     c52:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     c57:	44 0f b6 24 1f       	movzbl (%rdi,%rbx,1),%r12d
     c5c:	44 89 c3             	mov    %r8d,%ebx
     c5f:	49 c1 e8 38          	shr    $0x38,%r8
     c63:	45 09 f8             	or     %r15d,%r8d
     c66:	4d 89 ef             	mov    %r13,%r15
     c69:	49 c1 ed 28          	shr    $0x28,%r13
     c6d:	49 c1 ef 10          	shr    $0x10,%r15
     c71:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     c78:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     c7d:	c1 eb 08             	shr    $0x8,%ebx
     c80:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     c87:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     c8c:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     c90:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     c95:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
     c9b:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     ca2:	4d 89 c8             	mov    %r9,%r8
     ca5:	49 83 c1 08          	add    $0x8,%r9
     ca9:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     caf:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
     cb6:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     cbd:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     cc1:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     cc7:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
     cce:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     cd2:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     cd8:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     cdd:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     ce1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     ce7:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     cec:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     cf1:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     cf5:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     cfa:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     cff:	4c 39 c9             	cmp    %r9,%rcx
     d02:	0f 83 e8 fe ff ff    	jae    bf0 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbf0>
     d08:	49 39 c8             	cmp    %rcx,%r8
     d0b:	0f 83 ef 01 00 00    	jae    f00 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
     d11:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     d15:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     d19:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d1e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d23:	c1 e0 08             	shl    $0x8,%eax
     d26:	41 c1 e3 10          	shl    $0x10,%r11d
     d2a:	44 09 d8             	or     %r11d,%eax
     d2d:	45 0f b6 1a          	movzbl (%r10),%r11d
     d31:	44 09 d8             	or     %r11d,%eax
     d34:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d38:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d3c:	41 8b 03             	mov    (%r11),%eax
     d3f:	45 0f b7 1b          	movzwl (%r11),%r11d
     d43:	c1 e8 10             	shr    $0x10,%eax
     d46:	66 45 89 1a          	mov    %r11w,(%r10)
     d4a:	41 88 42 02          	mov    %al,0x2(%r10)
     d4e:	49 8d 40 01          	lea    0x1(%r8),%rax
     d52:	48 39 c8             	cmp    %rcx,%rax
     d55:	0f 83 a5 01 00 00    	jae    f00 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
     d5b:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     d60:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d65:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d6a:	c1 e0 08             	shl    $0x8,%eax
     d6d:	41 c1 e3 10          	shl    $0x10,%r11d
     d71:	44 09 d8             	or     %r11d,%eax
     d74:	45 0f b6 1a          	movzbl (%r10),%r11d
     d78:	44 09 d8             	or     %r11d,%eax
     d7b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d7f:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d83:	41 8b 03             	mov    (%r11),%eax
     d86:	45 0f b7 1b          	movzwl (%r11),%r11d
     d8a:	c1 e8 10             	shr    $0x10,%eax
     d8d:	66 45 89 1a          	mov    %r11w,(%r10)
     d91:	41 88 42 02          	mov    %al,0x2(%r10)
     d95:	49 8d 40 02          	lea    0x2(%r8),%rax
     d99:	48 39 c8             	cmp    %rcx,%rax
     d9c:	0f 83 5e 01 00 00    	jae    f00 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
     da2:	4e 8d 54 0a 06       	lea    0x6(%rdx,%r9,1),%r10
     da7:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     dac:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     db1:	c1 e0 08             	shl    $0x8,%eax
     db4:	41 c1 e3 10          	shl    $0x10,%r11d
     db8:	44 09 d8             	or     %r11d,%eax
     dbb:	45 0f b6 1a          	movzbl (%r10),%r11d
     dbf:	44 09 d8             	or     %r11d,%eax
     dc2:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     dc6:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     dca:	41 8b 03             	mov    (%r11),%eax
     dcd:	45 0f b7 1b          	movzwl (%r11),%r11d
     dd1:	c1 e8 10             	shr    $0x10,%eax
     dd4:	66 45 89 1a          	mov    %r11w,(%r10)
     dd8:	41 88 42 02          	mov    %al,0x2(%r10)
     ddc:	49 8d 40 03          	lea    0x3(%r8),%rax
     de0:	48 39 c8             	cmp    %rcx,%rax
     de3:	0f 83 17 01 00 00    	jae    f00 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
     de9:	4e 8d 54 0a 09       	lea    0x9(%rdx,%r9,1),%r10
     dee:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     df3:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     df8:	c1 e0 10             	shl    $0x10,%eax
     dfb:	41 c1 e3 08          	shl    $0x8,%r11d
     dff:	44 09 d8             	or     %r11d,%eax
     e02:	45 0f b6 1a          	movzbl (%r10),%r11d
     e06:	44 09 d8             	or     %r11d,%eax
     e09:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e0d:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e11:	41 8b 03             	mov    (%r11),%eax
     e14:	45 0f b7 1b          	movzwl (%r11),%r11d
     e18:	c1 e8 10             	shr    $0x10,%eax
     e1b:	66 45 89 1a          	mov    %r11w,(%r10)
     e1f:	41 88 42 02          	mov    %al,0x2(%r10)
     e23:	49 8d 40 04          	lea    0x4(%r8),%rax
     e27:	48 39 c8             	cmp    %rcx,%rax
     e2a:	0f 83 d0 00 00 00    	jae    f00 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
     e30:	4e 8d 54 0a 0c       	lea    0xc(%rdx,%r9,1),%r10
     e35:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e3a:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e3f:	c1 e0 10             	shl    $0x10,%eax
     e42:	41 c1 e3 08          	shl    $0x8,%r11d
     e46:	44 09 d8             	or     %r11d,%eax
     e49:	45 0f b6 1a          	movzbl (%r10),%r11d
     e4d:	44 09 d8             	or     %r11d,%eax
     e50:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e54:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e58:	41 8b 03             	mov    (%r11),%eax
     e5b:	45 0f b7 1b          	movzwl (%r11),%r11d
     e5f:	c1 e8 10             	shr    $0x10,%eax
     e62:	66 45 89 1a          	mov    %r11w,(%r10)
     e66:	41 88 42 02          	mov    %al,0x2(%r10)
     e6a:	49 8d 40 05          	lea    0x5(%r8),%rax
     e6e:	48 39 c8             	cmp    %rcx,%rax
     e71:	0f 83 89 00 00 00    	jae    f00 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
     e77:	4e 8d 54 0a 0f       	lea    0xf(%rdx,%r9,1),%r10
     e7c:	49 83 c0 06          	add    $0x6,%r8
     e80:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e85:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e8a:	c1 e0 10             	shl    $0x10,%eax
     e8d:	41 c1 e3 08          	shl    $0x8,%r11d
     e91:	44 09 d8             	or     %r11d,%eax
     e94:	45 0f b6 1a          	movzbl (%r10),%r11d
     e98:	44 09 d8             	or     %r11d,%eax
     e9b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e9f:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     ea3:	41 8b 03             	mov    (%r11),%eax
     ea6:	45 0f b7 1b          	movzwl (%r11),%r11d
     eaa:	c1 e8 10             	shr    $0x10,%eax
     ead:	66 45 89 1a          	mov    %r11w,(%r10)
     eb1:	41 88 42 02          	mov    %al,0x2(%r10)
     eb5:	49 39 c8             	cmp    %rcx,%r8
     eb8:	73 46                	jae    f00 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf00>
     eba:	4a 8d 54 0a 12       	lea    0x12(%rdx,%r9,1),%rdx
     ebf:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     ec3:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     ec7:	c1 e0 08             	shl    $0x8,%eax
     eca:	c1 e1 10             	shl    $0x10,%ecx
     ecd:	09 c8                	or     %ecx,%eax
     ecf:	0f b6 0a             	movzbl (%rdx),%ecx
     ed2:	09 c8                	or     %ecx,%eax
     ed4:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     ed8:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     edc:	8b 01                	mov    (%rcx),%eax
     ede:	0f b7 09             	movzwl (%rcx),%ecx
     ee1:	c1 e8 10             	shr    $0x10,%eax
     ee4:	66 89 0a             	mov    %cx,(%rdx)
     ee7:	88 42 02             	mov    %al,0x2(%rdx)
     eea:	c5 f8 77             	vzeroupper
     eed:	5b                   	pop    %rbx
     eee:	41 5c                	pop    %r12
     ef0:	41 5d                	pop    %r13
     ef2:	41 5e                	pop    %r14
     ef4:	41 5f                	pop    %r15
     ef6:	5d                   	pop    %rbp
     ef7:	c3                   	ret
     ef8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     eff:	00 
     f00:	c5 f8 77             	vzeroupper
     f03:	5b                   	pop    %rbx
     f04:	41 5c                	pop    %r12
     f06:	41 5d                	pop    %r13
     f08:	41 5e                	pop    %r14
     f0a:	41 5f                	pop    %r15
     f0c:	5d                   	pop    %rbp
     f0d:	c3                   	ret
     f0e:	66 90                	xchg   %ax,%ax
     f10:	49 89 c8             	mov    %rcx,%r8
     f13:	e9 b6 fc ff ff       	jmp    bce <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbce>
     f18:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     f1f:	00 
     f20:	c3                   	ret
     f21:	49 8d 41 28          	lea    0x28(%r9),%rax
     f25:	4d 89 c8             	mov    %r9,%r8
     f28:	e9 d9 f8 ff ff       	jmp    806 <jshc_channel::avx2_chain_qwordpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x806>
     f2d:	0f 1f 00             	nopl   (%rax)

0000000000000f30 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     f30:	f3 0f 1e fa          	endbr64
     f34:	4d 85 c0             	test   %r8,%r8
     f37:	0f 84 f3 0f 00 00    	je     1f30 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1000>
     f3d:	55                   	push   %rbp
     f3e:	b8 00 04 00 00       	mov    $0x400,%eax
     f43:	48 89 e5             	mov    %rsp,%rbp
     f46:	41 57                	push   %r15
     f48:	41 56                	push   %r14
     f4a:	41 55                	push   %r13
     f4c:	41 54                	push   %r12
     f4e:	49 89 cc             	mov    %rcx,%r12
     f51:	53                   	push   %rbx
     f52:	48 89 d3             	mov    %rdx,%rbx
     f55:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     f59:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     f5d:	48 39 c2             	cmp    %rax,%rdx
     f60:	48 0f 47 d0          	cmova  %rax,%rdx
     f64:	31 c0                	xor    %eax,%eax
     f66:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     f6d:	00 00 00 
     f70:	0f 18 04 03          	prefetchnta (%rbx,%rax,1)
     f74:	48 83 c0 40          	add    $0x40,%rax
     f78:	48 39 d0             	cmp    %rdx,%rax
     f7b:	72 f3                	jb     f70 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     f7d:	49 89 d9             	mov    %rbx,%r9
     f80:	4c 89 e2             	mov    %r12,%rdx
     f83:	31 c9                	xor    %ecx,%ecx
     f85:	eb 53                	jmp    fda <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
     f87:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
     f8e:	00 00 
     f90:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     f95:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     f9a:	48 ff c1             	inc    %rcx
     f9d:	48 83 c2 03          	add    $0x3,%rdx
     fa1:	49 83 c1 03          	add    $0x3,%r9
     fa5:	41 c1 e2 10          	shl    $0x10,%r10d
     fa9:	c1 e0 08             	shl    $0x8,%eax
     fac:	44 09 d0             	or     %r10d,%eax
     faf:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
     fb4:	44 09 d0             	or     %r10d,%eax
     fb7:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     fbb:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
     fbf:	41 8b 02             	mov    (%r10),%eax
     fc2:	45 0f b7 12          	movzwl (%r10),%r10d
     fc6:	c1 e8 10             	shr    $0x10,%eax
     fc9:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
     fce:	88 42 ff             	mov    %al,-0x1(%rdx)
     fd1:	49 39 c8             	cmp    %rcx,%r8
     fd4:	0f 84 46 0f 00 00    	je     1f20 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xff0>
     fda:	f6 c2 3f             	test   $0x3f,%dl
     fdd:	75 b1                	jne    f90 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     fdf:	48 8d 41 48          	lea    0x48(%rcx),%rax
     fe3:	49 39 c0             	cmp    %rax,%r8
     fe6:	0f 82 45 0f 00 00    	jb     1f31 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1001>
     fec:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     ff0:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # ff8 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc8>
     ff7:	00 
     ff8:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1000 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd0>
     fff:	00 
    1000:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1005:	49 8d 14 04          	lea    (%r12,%rax,1),%rdx
    1009:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    100e:	c5 7d 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm12        # 1016 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe6>
    1015:	00 
    1016:	48 8d 84 03 00 04 00 	lea    0x400(%rbx,%rax,1),%rax
    101d:	00 
    101e:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # 1026 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf6>
    1025:	00 
    1026:	c5 7d 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm10        # 102e <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfe>
    102d:	00 
    102e:	eb 03                	jmp    1033 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x103>
    1030:	4c 89 c9             	mov    %r9,%rcx
    1033:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    103a:	4d 39 c8             	cmp    %r9,%r8
    103d:	72 15                	jb     1054 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x124>
    103f:	0f 18 00             	prefetchnta (%rax)
    1042:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1046:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    104d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    1054:	44 8b 88 00 fc ff ff 	mov    -0x400(%rax),%r9d
    105b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1062:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1067:	44 8b 88 03 fc ff ff 	mov    -0x3fd(%rax),%r9d
    106e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1075:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
    107b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1080:	44 8b 88 06 fc ff ff 	mov    -0x3fa(%rax),%r9d
    1087:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    108e:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
    1095:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    109a:	44 8b 88 09 fc ff ff 	mov    -0x3f7(%rax),%r9d
    10a1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10a8:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    10ad:	44 8b 88 0c fc ff ff 	mov    -0x3f4(%rax),%r9d
    10b4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10bb:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    10c0:	44 8b 88 0f fc ff ff 	mov    -0x3f1(%rax),%r9d
    10c7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10ce:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    10d4:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    10d9:	44 8b 88 12 fc ff ff 	mov    -0x3ee(%rax),%r9d
    10e0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10e7:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    10ee:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    10f3:	44 8b 88 15 fc ff ff 	mov    -0x3eb(%rax),%r9d
    10fa:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1101:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1107:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    110c:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1113:	44 8b 88 18 fc ff ff 	mov    -0x3e8(%rax),%r9d
    111a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1121:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1125:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    112b:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1130:	44 8b 88 1b fc ff ff 	mov    -0x3e5(%rax),%r9d
    1137:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    113e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1145:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    114a:	44 8b 88 1e fc ff ff 	mov    -0x3e2(%rax),%r9d
    1151:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    1155:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    115b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1162:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    1167:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    116c:	44 8b 88 21 fc ff ff 	mov    -0x3df(%rax),%r9d
    1173:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    1178:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    117f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1184:	44 8b 88 24 fc ff ff 	mov    -0x3dc(%rax),%r9d
    118b:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1191:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1198:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    119d:	44 8b 88 27 fc ff ff 	mov    -0x3d9(%rax),%r9d
    11a4:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    11ab:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11b2:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    11b8:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    11bd:	44 8b 88 2a fc ff ff 	mov    -0x3d6(%rax),%r9d
    11c4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11cb:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    11d2:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    11d7:	44 8b 88 2d fc ff ff 	mov    -0x3d3(%rax),%r9d
    11de:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11e5:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    11eb:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    11f0:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    11f7:	44 8b 88 30 fc ff ff 	mov    -0x3d0(%rax),%r9d
    11fe:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1205:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1209:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    120f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1214:	44 8b 88 33 fc ff ff 	mov    -0x3cd(%rax),%r9d
    121b:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1222:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1229:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    122e:	44 8b 88 36 fc ff ff 	mov    -0x3ca(%rax),%r9d
    1235:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1239:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    123f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1246:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    124b:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1250:	44 8b 88 39 fc ff ff 	mov    -0x3c7(%rax),%r9d
    1257:	c4 e2 1d 36 c9       	vpermd %ymm1,%ymm12,%ymm1
    125c:	c4 e3 45 02 f9 c0    	vpblendd $0xc0,%ymm1,%ymm7,%ymm7
    1262:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1269:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    126e:	44 8b 88 3c fc ff ff 	mov    -0x3c4(%rax),%r9d
    1275:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    127c:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1281:	44 8b 88 3f fc ff ff 	mov    -0x3c1(%rax),%r9d
    1288:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    128f:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1294:	44 8b 88 42 fc ff ff 	mov    -0x3be(%rax),%r9d
    129b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12a2:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    12a7:	44 8b 88 45 fc ff ff 	mov    -0x3bb(%rax),%r9d
    12ae:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12b5:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    12ba:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    12c0:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
    12c6:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    12cc:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    12d3:	44 8b 88 48 fc ff ff 	mov    -0x3b8(%rax),%r9d
    12da:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
    12e1:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    12e8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12ef:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    12f4:	44 8b 88 4b fc ff ff 	mov    -0x3b5(%rax),%r9d
    12fb:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    12ff:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1305:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    130c:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
    1312:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1317:	44 8b 88 4e fc ff ff 	mov    -0x3b2(%rax),%r9d
    131e:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1325:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    132c:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
    1333:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1338:	44 8b 88 51 fc ff ff 	mov    -0x3af(%rax),%r9d
    133f:	c5 31 6c ca          	vpunpcklqdq %xmm2,%xmm9,%xmm9
    1343:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    1349:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1350:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    1355:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    135a:	44 8b 88 54 fc ff ff 	mov    -0x3ac(%rax),%r9d
    1361:	c4 42 25 36 c9       	vpermd %ymm9,%ymm11,%ymm9
    1366:	c4 c3 75 0c c9 f0    	vblendps $0xf0,%ymm9,%ymm1,%ymm1
    136c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1373:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1378:	44 8b 88 57 fc ff ff 	mov    -0x3a9(%rax),%r9d
    137f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1386:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    138c:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1391:	44 8b 88 5a fc ff ff 	mov    -0x3a6(%rax),%r9d
    1398:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    139f:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    13a6:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    13ab:	44 8b 88 5d fc ff ff 	mov    -0x3a3(%rax),%r9d
    13b2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13b9:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    13bf:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    13c4:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    13cb:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    13cf:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    13d5:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    13dc:	44 8b 88 60 fc ff ff 	mov    -0x3a0(%rax),%r9d
    13e3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13ea:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
    13ee:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    13f3:	44 8b 88 63 fc ff ff 	mov    -0x39d(%rax),%r9d
    13fa:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    1400:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1405:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    140c:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    1412:	c4 e2 2d 36 f6       	vpermd %ymm6,%ymm10,%ymm6
    1417:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    141c:	44 8b 88 66 fc ff ff 	mov    -0x39a(%rax),%r9d
    1423:	c4 c3 4d 02 f1 03    	vpblendd $0x3,%ymm9,%ymm6,%ymm6
    1429:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1430:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    1437:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    143c:	44 8b 88 69 fc ff ff 	mov    -0x397(%rax),%r9d
    1443:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    144a:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    144f:	44 8b 88 6c fc ff ff 	mov    -0x394(%rax),%r9d
    1456:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    145d:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1462:	44 8b 88 6f fc ff ff 	mov    -0x391(%rax),%r9d
    1469:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1470:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1476:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    147b:	44 8b 88 72 fc ff ff 	mov    -0x38e(%rax),%r9d
    1482:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1489:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1490:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1495:	44 8b 88 75 fc ff ff 	mov    -0x38b(%rax),%r9d
    149c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14a3:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    14a9:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    14ae:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    14b5:	44 8b 88 78 fc ff ff 	mov    -0x388(%rax),%r9d
    14bc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14c3:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    14c7:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    14cd:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    14d2:	44 8b 88 7b fc ff ff 	mov    -0x385(%rax),%r9d
    14d9:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    14e0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14e7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    14ec:	44 8b 88 7e fc ff ff 	mov    -0x382(%rax),%r9d
    14f3:	c5 d1 6c ea          	vpunpcklqdq %xmm2,%xmm5,%xmm5
    14f7:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    14fd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1504:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1509:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    150e:	44 8b 88 81 fc ff ff 	mov    -0x37f(%rax),%r9d
    1515:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    151a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1521:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1526:	44 8b 88 84 fc ff ff 	mov    -0x37c(%rax),%r9d
    152d:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1533:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    153a:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    153f:	44 8b 88 87 fc ff ff 	mov    -0x379(%rax),%r9d
    1546:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    154d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1554:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    155a:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    155f:	44 8b 88 8a fc ff ff 	mov    -0x376(%rax),%r9d
    1566:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    156d:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1574:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1579:	44 8b 88 8d fc ff ff 	mov    -0x373(%rax),%r9d
    1580:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1587:	c4 21 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm8
    158d:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1592:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    1599:	44 8b 88 90 fc ff ff 	mov    -0x370(%rax),%r9d
    15a0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15a7:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
    15ac:	c4 21 79 6e 04 a6    	vmovd  (%rsi,%r12,4),%xmm8
    15b2:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    15b7:	44 8b 88 93 fc ff ff 	mov    -0x36d(%rax),%r9d
    15be:	c4 63 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm8,%xmm8
    15c5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15cc:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    15d1:	44 8b 88 96 fc ff ff 	mov    -0x36a(%rax),%r9d
    15d8:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
    15dd:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    15e3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15ea:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    15ef:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    15f4:	44 8b 88 99 fc ff ff 	mov    -0x367(%rax),%r9d
    15fb:	c4 e2 1d 36 c0       	vpermd %ymm0,%ymm12,%ymm0
    1600:	c4 e3 55 02 e8 c0    	vpblendd $0xc0,%ymm0,%ymm5,%ymm5
    1606:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    160d:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1612:	44 8b 88 9c fc ff ff 	mov    -0x364(%rax),%r9d
    1619:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1620:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1625:	44 8b 88 9f fc ff ff 	mov    -0x361(%rax),%r9d
    162c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1633:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    1638:	44 8b 88 a2 fc ff ff 	mov    -0x35e(%rax),%r9d
    163f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1646:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    164b:	44 8b 88 a5 fc ff ff 	mov    -0x35b(%rax),%r9d
    1652:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1659:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    165e:	c4 21 79 6e 2c be    	vmovd  (%rsi,%r15,4),%xmm13
    1664:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
    166a:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1670:	c4 23 11 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm13,%xmm13
    1677:	44 8b 88 a8 fc ff ff 	mov    -0x358(%rax),%r9d
    167e:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
    1685:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    168c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1693:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1698:	44 8b 88 ab fc ff ff 	mov    -0x355(%rax),%r9d
    169f:	c4 c1 69 6c d5       	vpunpcklqdq %xmm13,%xmm2,%xmm2
    16a4:	c4 21 79 6e 2c a6    	vmovd  (%rsi,%r12,4),%xmm13
    16aa:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16b1:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    16b6:	44 8b 88 ae fc ff ff 	mov    -0x352(%rax),%r9d
    16bd:	c4 63 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm13,%xmm13
    16c4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16cb:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    16d0:	44 8b 88 b1 fc ff ff 	mov    -0x34f(%rax),%r9d
    16d7:	c4 41 39 6c c5       	vpunpcklqdq %xmm13,%xmm8,%xmm8
    16dc:	c4 63 3d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm8,%ymm8
    16e2:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    16e8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16ef:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    16f4:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    16f9:	44 8b 88 b4 fc ff ff 	mov    -0x34c(%rax),%r9d
    1700:	c4 42 25 36 c0       	vpermd %ymm8,%ymm11,%ymm8
    1705:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    170c:	c4 c3 7d 0c c0 f0    	vblendps $0xf0,%ymm8,%ymm0,%ymm0
    1712:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1719:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1720:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1725:	44 8b 88 b7 fc ff ff 	mov    -0x349(%rax),%r9d
    172c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1733:	c4 21 79 6e 2c b6    	vmovd  (%rsi,%r14,4),%xmm13
    1739:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    173e:	44 8b 88 ba fc ff ff 	mov    -0x346(%rax),%r9d
    1745:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    174c:	c4 23 11 22 2c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm13,%xmm13
    1753:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1758:	44 8b 88 bd fc ff ff 	mov    -0x343(%rax),%r9d
    175f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1766:	c4 21 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm14
    176c:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    1773:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1778:	c4 23 09 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm14,%xmm14
    177f:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    1783:	c4 41 11 6c ee       	vpunpcklqdq %xmm14,%xmm13,%xmm13
    1788:	c4 21 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm14
    178e:	c4 63 09 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm14,%xmm14
    1795:	c5 fd e7 ba 40 ff ff 	vmovntdq %ymm7,-0xc0(%rdx)
    179c:	ff 
    179d:	c5 fd e7 8a 60 ff ff 	vmovntdq %ymm1,-0xa0(%rdx)
    17a4:	ff 
    17a5:	c5 fd e7 72 80       	vmovntdq %ymm6,-0x80(%rdx)
    17aa:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
    17af:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    17b4:	c4 c1 69 6c d6       	vpunpcklqdq %xmm14,%xmm2,%xmm2
    17b9:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
    17bf:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    17c4:	c4 e2 2d 36 d2       	vpermd %ymm2,%ymm10,%ymm2
    17c9:	c4 c3 6d 02 d0 03    	vpblendd $0x3,%ymm8,%ymm2,%ymm2
    17cf:	c5 fd e7 52 e0       	vmovntdq %ymm2,-0x20(%rdx)
    17d4:	48 05 c0 00 00 00    	add    $0xc0,%rax
    17da:	4d 39 d0             	cmp    %r10,%r8
    17dd:	0f 83 4d f8 ff ff    	jae    1030 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x100>
    17e3:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    17e8:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    17ed:	48 8d 41 68          	lea    0x68(%rcx),%rax
    17f1:	0f ae f8             	sfence
    17f4:	49 39 c0             	cmp    %rax,%r8
    17f7:	0f 82 93 03 00 00    	jb     1b90 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc60>
    17fd:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1801:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1809 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8d9>
    1808:	00 
    1809:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1811 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8e1>
    1810:	00 
    1811:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1816:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    181b:	48 8d 04 13          	lea    (%rbx,%rdx,1),%rax
    181f:	4c 01 e2             	add    %r12,%rdx
    1822:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1828:	8b 48 48             	mov    0x48(%rax),%ecx
    182b:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1831:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1836:	8b 48 4b             	mov    0x4b(%rax),%ecx
    1839:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    183f:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    1845:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    184a:	8b 48 4e             	mov    0x4e(%rax),%ecx
    184d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1853:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    185a:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    185f:	8b 48 51             	mov    0x51(%rax),%ecx
    1862:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1868:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    186c:	8b 48 54             	mov    0x54(%rax),%ecx
    186f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1875:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    187a:	8b 48 57             	mov    0x57(%rax),%ecx
    187d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1883:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1889:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    188e:	8b 48 5a             	mov    0x5a(%rax),%ecx
    1891:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1897:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    189e:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    18a3:	8b 48 5d             	mov    0x5d(%rax),%ecx
    18a6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    18ac:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    18b2:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    18b6:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    18bd:	8b 48 30             	mov    0x30(%rax),%ecx
    18c0:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    18c6:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    18ca:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    18d0:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    18d5:	8b 48 33             	mov    0x33(%rax),%ecx
    18d8:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    18df:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    18e5:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    18ea:	8b 48 36             	mov    0x36(%rax),%ecx
    18ed:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    18f1:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    18f7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    18fd:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1902:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1907:	8b 48 39             	mov    0x39(%rax),%ecx
    190a:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    190f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1915:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1919:	8b 48 3c             	mov    0x3c(%rax),%ecx
    191c:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1922:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1928:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    192d:	8b 48 3f             	mov    0x3f(%rax),%ecx
    1930:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    1937:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    193d:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1943:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1948:	8b 48 42             	mov    0x42(%rax),%ecx
    194b:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1951:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1958:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    195d:	8b 48 45             	mov    0x45(%rax),%ecx
    1960:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1966:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    196c:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1970:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1977:	8b 48 18             	mov    0x18(%rax),%ecx
    197a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1980:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1984:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    198a:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    198f:	8b 48 1b             	mov    0x1b(%rax),%ecx
    1992:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1999:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    199f:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    19a4:	8b 48 1e             	mov    0x1e(%rax),%ecx
    19a7:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    19ab:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    19b1:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19b7:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    19bc:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    19c1:	8b 48 21             	mov    0x21(%rax),%ecx
    19c4:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    19c9:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    19cd:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    19d3:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19d9:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    19dd:	8b 48 24             	mov    0x24(%rax),%ecx
    19e0:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19e6:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    19eb:	8b 48 27             	mov    0x27(%rax),%ecx
    19ee:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    19f4:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    19f9:	8b 48 2a             	mov    0x2a(%rax),%ecx
    19fc:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a02:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1a07:	8b 48 2d             	mov    0x2d(%rax),%ecx
    1a0a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a10:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1a14:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1a1a:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1a20:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1a26:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    1a2d:	8b 08                	mov    (%rax),%ecx
    1a2f:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    1a36:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1a3d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a43:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1a48:	8b 48 03             	mov    0x3(%rax),%ecx
    1a4b:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    1a4f:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    1a55:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a5b:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1a60:	8b 48 06             	mov    0x6(%rax),%ecx
    1a63:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    1a6a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a70:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1a75:	8b 48 09             	mov    0x9(%rax),%ecx
    1a78:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1a7c:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1a82:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1a88:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1a8e:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1a93:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1a97:	8b 48 0c             	mov    0xc(%rax),%ecx
    1a9a:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1a9f:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1aa6:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1aaa:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1ab0:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1ab6:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1abc:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1ac1:	8b 48 0f             	mov    0xf(%rax),%ecx
    1ac4:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1aca:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1ad0:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    1ad6:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1adb:	8b 48 12             	mov    0x12(%rax),%ecx
    1ade:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1ae4:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    1aeb:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1af0:	8b 48 15             	mov    0x15(%rax),%ecx
    1af3:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1af9:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    1aff:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1b03:	c4 e3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm7,%xmm7
    1b0a:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1b0e:	49 83 c1 20          	add    $0x20,%r9
    1b12:	48 83 c0 60          	add    $0x60,%rax
    1b16:	48 83 c2 60          	add    $0x60,%rdx
    1b1a:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    1b1e:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    1b24:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    1b2b:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    1b2f:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    1b33:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1b39:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    1b3f:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    1b45:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1b49:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1b4e:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    1b54:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1b59:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1b5d:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1b63:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1b68:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    1b6e:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1b73:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1b78:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1b7d:	49 39 c8             	cmp    %rcx,%r8
    1b80:	0f 83 a2 fc ff ff    	jae    1828 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8f8>
    1b86:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1b8b:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1b90:	4d 8d 59 08          	lea    0x8(%r9),%r11
    1b94:	4d 39 d8             	cmp    %r11,%r8
    1b97:	0f 82 4d 01 00 00    	jb     1cea <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdba>
    1b9d:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1ba2:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    1ba6:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1bae <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc7e>
    1bad:	00 
    1bae:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    1bb3:	4a 8d 0c 13          	lea    (%rbx,%r10,1),%rcx
    1bb7:	4d 01 e2             	add    %r12,%r10
    1bba:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1bc0:	4c 8b 21             	mov    (%rcx),%r12
    1bc3:	48 8b 41 08          	mov    0x8(%rcx),%rax
    1bc7:	49 83 c2 18          	add    $0x18,%r10
    1bcb:	48 83 c1 18          	add    $0x18,%rcx
    1bcf:	48 8b 51 f8          	mov    -0x8(%rcx),%rdx
    1bd3:	4d 89 e1             	mov    %r12,%r9
    1bd6:	4d 89 e5             	mov    %r12,%r13
    1bd9:	49 89 c6             	mov    %rax,%r14
    1bdc:	49 c1 ed 30          	shr    $0x30,%r13
    1be0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1be7:	41 89 d7             	mov    %edx,%r15d
    1bea:	49 c1 ee 20          	shr    $0x20,%r14
    1bee:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1bf3:	4d 89 e1             	mov    %r12,%r9
    1bf6:	41 89 c4             	mov    %eax,%r12d
    1bf9:	41 c1 e7 08          	shl    $0x8,%r15d
    1bfd:	41 c1 e4 10          	shl    $0x10,%r12d
    1c01:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1c08:	49 c1 e9 18          	shr    $0x18,%r9
    1c0c:	45 09 ec             	or     %r13d,%r12d
    1c0f:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1c14:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1c1b:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    1c20:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1c27:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1c2c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1c31:	41 89 c4             	mov    %eax,%r12d
    1c34:	48 c1 e8 38          	shr    $0x38,%rax
    1c38:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1c3e:	41 09 c7             	or     %eax,%r15d
    1c41:	41 c1 ec 08          	shr    $0x8,%r12d
    1c45:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1c4c:	4d 89 d9             	mov    %r11,%r9
    1c4f:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1c56:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1c5b:	49 83 c3 08          	add    $0x8,%r11
    1c5f:	42 0f b6 04 3f       	movzbl (%rdi,%r15,1),%eax
    1c64:	49 89 d7             	mov    %rdx,%r15
    1c67:	48 c1 ea 28          	shr    $0x28,%rdx
    1c6b:	49 c1 ef 10          	shr    $0x10,%r15
    1c6f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c73:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1c7a:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
    1c81:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1c86:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1c8c:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
    1c93:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1c97:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1c9d:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1ca4:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1ca8:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1cae:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1cb3:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1cb7:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1cbd:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1cc2:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1cc7:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1ccb:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1cd1:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    1cd7:	4d 39 d8             	cmp    %r11,%r8
    1cda:	0f 83 e0 fe ff ff    	jae    1bc0 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc90>
    1ce0:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1ce5:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1cea:	4d 39 c1             	cmp    %r8,%r9
    1ced:	0f 83 15 02 00 00    	jae    1f08 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfd8>
    1cf3:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1cf7:	4c 8d 14 03          	lea    (%rbx,%rax,1),%r10
    1cfb:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1d00:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1d05:	45 0f b6 12          	movzbl (%r10),%r10d
    1d09:	c1 e2 08             	shl    $0x8,%edx
    1d0c:	41 c1 e3 10          	shl    $0x10,%r11d
    1d10:	44 09 da             	or     %r11d,%edx
    1d13:	44 09 d2             	or     %r10d,%edx
    1d16:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1d1a:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    1d1e:	41 8b 12             	mov    (%r10),%edx
    1d21:	45 0f b7 12          	movzwl (%r10),%r10d
    1d25:	c1 ea 10             	shr    $0x10,%edx
    1d28:	66 45 89 14 04       	mov    %r10w,(%r12,%rax,1)
    1d2d:	41 88 54 04 02       	mov    %dl,0x2(%r12,%rax,1)
    1d32:	49 8d 51 01          	lea    0x1(%r9),%rdx
    1d36:	4c 39 c2             	cmp    %r8,%rdx
    1d39:	0f 83 c9 01 00 00    	jae    1f08 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfd8>
    1d3f:	4c 8d 54 03 03       	lea    0x3(%rbx,%rax,1),%r10
    1d44:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1d49:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1d4e:	45 0f b6 12          	movzbl (%r10),%r10d
    1d52:	41 c1 e3 10          	shl    $0x10,%r11d
    1d56:	c1 e2 08             	shl    $0x8,%edx
    1d59:	44 09 da             	or     %r11d,%edx
    1d5c:	44 09 d2             	or     %r10d,%edx
    1d5f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1d63:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1d67:	44 8b 12             	mov    (%rdx),%r10d
    1d6a:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1d6e:	49 8d 51 02          	lea    0x2(%r9),%rdx
    1d72:	44 89 d1             	mov    %r10d,%ecx
    1d75:	66 45 89 5c 04 03    	mov    %r11w,0x3(%r12,%rax,1)
    1d7b:	c1 e9 10             	shr    $0x10,%ecx
    1d7e:	41 88 4c 04 05       	mov    %cl,0x5(%r12,%rax,1)
    1d83:	4c 39 c2             	cmp    %r8,%rdx
    1d86:	0f 83 7c 01 00 00    	jae    1f08 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfd8>
    1d8c:	4c 8d 54 03 06       	lea    0x6(%rbx,%rax,1),%r10
    1d91:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1d96:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1d9b:	45 0f b6 12          	movzbl (%r10),%r10d
    1d9f:	41 c1 e3 10          	shl    $0x10,%r11d
    1da3:	c1 e2 08             	shl    $0x8,%edx
    1da6:	44 09 da             	or     %r11d,%edx
    1da9:	44 09 d2             	or     %r10d,%edx
    1dac:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1db0:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1db4:	44 8b 12             	mov    (%rdx),%r10d
    1db7:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1dbb:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1dbf:	44 89 d1             	mov    %r10d,%ecx
    1dc2:	66 45 89 5c 04 06    	mov    %r11w,0x6(%r12,%rax,1)
    1dc8:	c1 e9 10             	shr    $0x10,%ecx
    1dcb:	41 88 4c 04 08       	mov    %cl,0x8(%r12,%rax,1)
    1dd0:	4c 39 c2             	cmp    %r8,%rdx
    1dd3:	0f 83 2f 01 00 00    	jae    1f08 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfd8>
    1dd9:	4c 8d 54 03 09       	lea    0x9(%rbx,%rax,1),%r10
    1dde:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1de3:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1de8:	45 0f b6 12          	movzbl (%r10),%r10d
    1dec:	41 c1 e3 08          	shl    $0x8,%r11d
    1df0:	c1 e2 10             	shl    $0x10,%edx
    1df3:	44 09 da             	or     %r11d,%edx
    1df6:	44 09 d2             	or     %r10d,%edx
    1df9:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1dfd:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1e01:	44 8b 12             	mov    (%rdx),%r10d
    1e04:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1e08:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1e0c:	44 89 d1             	mov    %r10d,%ecx
    1e0f:	66 45 89 5c 04 09    	mov    %r11w,0x9(%r12,%rax,1)
    1e15:	c1 e9 10             	shr    $0x10,%ecx
    1e18:	41 88 4c 04 0b       	mov    %cl,0xb(%r12,%rax,1)
    1e1d:	4c 39 c2             	cmp    %r8,%rdx
    1e20:	0f 83 e2 00 00 00    	jae    1f08 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfd8>
    1e26:	4c 8d 54 03 0c       	lea    0xc(%rbx,%rax,1),%r10
    1e2b:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1e30:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1e35:	45 0f b6 12          	movzbl (%r10),%r10d
    1e39:	41 c1 e3 08          	shl    $0x8,%r11d
    1e3d:	c1 e2 10             	shl    $0x10,%edx
    1e40:	44 09 da             	or     %r11d,%edx
    1e43:	44 09 d2             	or     %r10d,%edx
    1e46:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1e4a:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1e4e:	44 8b 12             	mov    (%rdx),%r10d
    1e51:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1e55:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1e59:	44 89 d1             	mov    %r10d,%ecx
    1e5c:	66 45 89 5c 04 0c    	mov    %r11w,0xc(%r12,%rax,1)
    1e62:	c1 e9 10             	shr    $0x10,%ecx
    1e65:	41 88 4c 04 0e       	mov    %cl,0xe(%r12,%rax,1)
    1e6a:	4c 39 c2             	cmp    %r8,%rdx
    1e6d:	0f 83 95 00 00 00    	jae    1f08 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfd8>
    1e73:	4c 8d 54 03 0f       	lea    0xf(%rbx,%rax,1),%r10
    1e78:	49 83 c1 06          	add    $0x6,%r9
    1e7c:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1e81:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1e86:	45 0f b6 12          	movzbl (%r10),%r10d
    1e8a:	41 c1 e3 08          	shl    $0x8,%r11d
    1e8e:	c1 e2 10             	shl    $0x10,%edx
    1e91:	44 09 da             	or     %r11d,%edx
    1e94:	44 09 d2             	or     %r10d,%edx
    1e97:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1e9b:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1e9f:	44 8b 12             	mov    (%rdx),%r10d
    1ea2:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1ea6:	44 89 d1             	mov    %r10d,%ecx
    1ea9:	66 45 89 5c 04 0f    	mov    %r11w,0xf(%r12,%rax,1)
    1eaf:	c1 e9 10             	shr    $0x10,%ecx
    1eb2:	41 88 4c 04 11       	mov    %cl,0x11(%r12,%rax,1)
    1eb7:	4d 39 c1             	cmp    %r8,%r9
    1eba:	73 4c                	jae    1f08 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfd8>
    1ebc:	48 8d 54 03 12       	lea    0x12(%rbx,%rax,1),%rdx
    1ec1:	4d 8d 44 04 12       	lea    0x12(%r12,%rax,1),%r8
    1ec6:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1eca:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1ece:	0f b6 12             	movzbl (%rdx),%edx
    1ed1:	c1 e0 08             	shl    $0x8,%eax
    1ed4:	c1 e1 10             	shl    $0x10,%ecx
    1ed7:	09 c8                	or     %ecx,%eax
    1ed9:	09 d0                	or     %edx,%eax
    1edb:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1edf:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1ee3:	8b 02                	mov    (%rdx),%eax
    1ee5:	0f b7 12             	movzwl (%rdx),%edx
    1ee8:	c1 e8 10             	shr    $0x10,%eax
    1eeb:	66 41 89 10          	mov    %dx,(%r8)
    1eef:	41 88 40 02          	mov    %al,0x2(%r8)
    1ef3:	c5 f8 77             	vzeroupper
    1ef6:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1efa:	5b                   	pop    %rbx
    1efb:	41 5c                	pop    %r12
    1efd:	41 5d                	pop    %r13
    1eff:	41 5e                	pop    %r14
    1f01:	41 5f                	pop    %r15
    1f03:	5d                   	pop    %rbp
    1f04:	c3                   	ret
    1f05:	0f 1f 00             	nopl   (%rax)
    1f08:	c5 f8 77             	vzeroupper
    1f0b:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1f0f:	5b                   	pop    %rbx
    1f10:	41 5c                	pop    %r12
    1f12:	41 5d                	pop    %r13
    1f14:	41 5e                	pop    %r14
    1f16:	41 5f                	pop    %r15
    1f18:	5d                   	pop    %rbp
    1f19:	c3                   	ret
    1f1a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1f20:	4d 89 c1             	mov    %r8,%r9
    1f23:	e9 68 fc ff ff       	jmp    1b90 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc60>
    1f28:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    1f2f:	00 
    1f30:	c3                   	ret
    1f31:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1f35:	49 89 c9             	mov    %rcx,%r9
    1f38:	e9 b7 f8 ff ff       	jmp    17f4 <jshc_channel::avx2_chain_qwordpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8c4>
