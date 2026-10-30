
artifacts/skylake-vectorinput-linux-build-v1/CMakeFiles/jshc_skylake_vectorinput.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 c3 0e 00 00    	je     ed0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xed0>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
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
      89:	0f 84 31 0e 00 00    	je     ec0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xec0>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 2f 0e 00 00    	jb     ed1 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xed1>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # ae <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # b6 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # be <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbe>
      bd:	00 
      be:	48 01 d0             	add    %rdx,%rax
      c1:	eb 08                	jmp    cb <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcb>
      c3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      c8:	4d 89 c1             	mov    %r8,%r9
      cb:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      d2:	4c 39 c1             	cmp    %r8,%rcx
      d5:	72 1c                	jb     f3 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf3>
      d7:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      de:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      e5:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
      ec:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
      f3:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
      f7:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
      fc:	48 05 c0 00 00 00    	add    $0xc0,%rax
     102:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     108:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     10e:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     113:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     119:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     11e:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     124:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     129:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     12f:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     134:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     139:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     13e:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     143:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     149:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     14f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     154:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     159:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     15f:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     165:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     16b:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     171:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     176:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     17b:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     182:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     189:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     18f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     193:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     198:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     19f:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1a6:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     1aa:	c5 fa 7e 88 68 ff ff 	vmovq  -0x98(%rax),%xmm1
     1b1:	ff 
     1b2:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     1b8:	c5 fa 6f 80 58 ff ff 	vmovdqu -0xa8(%rax),%xmm0
     1bf:	ff 
     1c0:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     1c5:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     1cb:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
     1d0:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     1d6:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     1db:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     1e1:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     1e6:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     1ec:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     1f1:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     1f7:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     1fc:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     201:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     206:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     20b:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     211:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     217:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     21c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     221:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     227:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     22d:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     233:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     239:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     23e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     243:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     24a:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     251:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     255:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     25a:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     260:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     267:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     26e:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     272:	c5 fa 7e 48 80       	vmovq  -0x80(%rax),%xmm1
     277:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     27d:	c5 fa 6f 80 70 ff ff 	vmovdqu -0x90(%rax),%xmm0
     284:	ff 
     285:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     28a:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     290:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     295:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     29b:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     2a0:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     2a6:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     2ab:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     2b1:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     2b6:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     2bc:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     2c1:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     2c6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     2cb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     2d0:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     2d6:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     2dc:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2e1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     2e6:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     2ec:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     2f2:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     2f8:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     2fe:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     303:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     308:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     30f:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     316:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     31b:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     31f:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     325:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     32c:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     333:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     337:	c5 fa 7e 70 98       	vmovq  -0x68(%rax),%xmm6
     33c:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     342:	c5 fa 6f 40 88       	vmovdqu -0x78(%rax),%xmm0
     347:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     34c:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     352:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     357:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     35d:	c5 79 6f e9          	vmovdqa %xmm1,%xmm13
     361:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     367:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     36c:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     372:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     377:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     37d:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     382:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     388:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     38d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     392:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     397:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     39c:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     3a2:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     3a8:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     3ae:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     3b4:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     3b9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     3be:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3c3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     3c8:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     3ce:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     3d4:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     3da:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     3e1:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     3e8:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     3ef:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     3f3:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     3f8:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     3ff:	c5 c1 6c fe          	vpunpcklqdq %xmm6,%xmm7,%xmm7
     403:	c5 fa 7e 70 b0       	vmovq  -0x50(%rax),%xmm6
     408:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     40e:	c5 fa 6f 40 a0       	vmovdqu -0x60(%rax),%xmm0
     413:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     418:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     41e:	c4 e2 55 36 ff       	vpermd %ymm7,%ymm5,%ymm7
     423:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     429:	c5 79 6f f7          	vmovdqa %xmm7,%xmm14
     42d:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     433:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     438:	c4 c3 41 0f fe 08    	vpalignr $0x8,%xmm14,%xmm7,%xmm7
     43e:	c4 c1 71 6c ce       	vpunpcklqdq %xmm14,%xmm1,%xmm1
     443:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     449:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     44e:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     454:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     459:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     45f:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     464:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     469:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     46e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     473:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     479:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     47f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     484:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     489:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     48f:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     495:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     49b:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     4a1:	c4 e3 75 38 cf 01    	vinserti128 $0x1,%xmm7,%ymm1,%ymm1
     4a7:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     4ac:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     4b1:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     4b8:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     4bf:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     4c4:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     4c8:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     4ce:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     4d5:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     4dc:	c4 c1 49 6c f1       	vpunpcklqdq %xmm9,%xmm6,%xmm6
     4e1:	c5 7a 7e 48 c8       	vmovq  -0x38(%rax),%xmm9
     4e6:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     4ec:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
     4f1:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     4f6:	c4 63 31 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm9,%xmm9
     4fc:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     501:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
     507:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     50c:	c4 c3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm9
     512:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     517:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     51d:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     522:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     527:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     52c:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     532:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     538:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     53e:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     543:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     548:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     54d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     552:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     558:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     55e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     563:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     568:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     56e:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     574:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     579:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     580:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     587:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     58e:	c5 31 6c c8          	vpunpcklqdq %xmm0,%xmm9,%xmm9
     592:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     598:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     59f:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
     5a4:	c5 7a 7e 50 e0       	vmovq  -0x20(%rax),%xmm10
     5a9:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
     5af:	c5 7a 6f 48 d0       	vmovdqu -0x30(%rax),%xmm9
     5b4:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     5b9:	c4 43 29 0f d1 0c    	vpalignr $0xc,%xmm9,%xmm10,%xmm10
     5bf:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
     5c4:	c4 43 35 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm9,%ymm9
     5ca:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
     5cf:	c4 43 7d 39 ca 01    	vextracti128 $0x1,%ymm9,%xmm10
     5d5:	c4 41 79 7e c8       	vmovd  %xmm9,%r8d
     5da:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
     5e0:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     5e5:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     5eb:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5f0:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     5f5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     5fa:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     5ff:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     605:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     60b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     610:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     615:	c4 43 79 16 c8 01    	vpextrd $0x1,%xmm9,%r8d
     61b:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
     621:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
     627:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     62d:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     632:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     637:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
     63e:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     645:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     64a:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
     64f:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
     655:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     65c:	c4 23 29 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm10,%xmm10
     663:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
     668:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
     66d:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
     673:	c5 7a 6f 48 e8       	vmovdqu -0x18(%rax),%xmm9
     678:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
     67d:	c4 43 21 0f d9 0c    	vpalignr $0xc,%xmm9,%xmm11,%xmm11
     683:	c4 42 55 36 d2       	vpermd %ymm10,%ymm5,%ymm10
     688:	c4 43 35 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm9
     68e:	c5 79 7f d7          	vmovdqa %xmm10,%xmm7
     692:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
     698:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
     69d:	c4 43 7d 39 cb 01    	vextracti128 $0x1,%ymm9,%xmm11
     6a3:	c4 41 79 7e c8       	vmovd  %xmm9,%r8d
     6a8:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
     6ae:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
     6b3:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
     6b9:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     6be:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     6c3:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     6c8:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     6cd:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
     6d3:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
     6d9:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     6de:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     6e3:	c4 43 79 16 c8 01    	vpextrd $0x1,%xmm9,%r8d
     6e9:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
     6ef:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
     6f5:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
     6fb:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     700:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     705:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
     70c:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
     713:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     718:	c4 41 21 6c d9       	vpunpcklqdq %xmm9,%xmm11,%xmm11
     71d:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     723:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     72a:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     731:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     738:	c5 fd e7 48 80       	vmovntdq %ymm1,-0x80(%rax)
     73d:	c5 f9 6f ce          	vmovdqa %xmm6,%xmm1
     741:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     747:	4d 8d 41 40          	lea    0x40(%r9),%r8
     74b:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     750:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
     754:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     75a:	c4 43 35 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm9
     760:	c4 c3 69 0f d4 08    	vpalignr $0x8,%xmm12,%xmm2,%xmm2
     766:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     76b:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     771:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     776:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
     77c:	c4 41 39 6c c4       	vpunpcklqdq %xmm12,%xmm8,%xmm8
     781:	c4 42 55 36 c9       	vpermd %ymm9,%ymm5,%ymm9
     786:	c5 fd e7 90 60 ff ff 	vmovntdq %ymm2,-0xa0(%rax)
     78d:	ff 
     78e:	c4 43 25 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm11,%ymm8
     794:	c5 79 7f ca          	vmovdqa %xmm9,%xmm2
     798:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     79e:	c5 7d e7 80 40 ff ff 	vmovntdq %ymm8,-0xc0(%rax)
     7a5:	ff 
     7a6:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     7aa:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     7b0:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     7b4:	c4 c3 79 0f c0 08    	vpalignr $0x8,%xmm8,%xmm0,%xmm0
     7ba:	c4 63 31 0f ca 08    	vpalignr $0x8,%xmm2,%xmm9,%xmm9
     7c0:	c4 c1 49 6c f0       	vpunpcklqdq %xmm8,%xmm6,%xmm6
     7c5:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
     7cb:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     7d1:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
     7d7:	c5 fd e7 48 a0       	vmovntdq %ymm1,-0x60(%rax)
     7dc:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     7e1:	c5 7d e7 50 e0       	vmovntdq %ymm10,-0x20(%rax)
     7e6:	4c 39 d1             	cmp    %r10,%rcx
     7e9:	0f 83 d9 f8 ff ff    	jae    c8 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc8>
     7ef:	0f ae f8             	sfence
     7f2:	49 8d 41 68          	lea    0x68(%r9),%rax
     7f6:	48 39 c1             	cmp    %rax,%rcx
     7f9:	0f 82 a0 03 00 00    	jb     b9f <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb9f>
     7ff:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     803:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 80b <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x80b>
     80a:	00 
     80b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 813 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x813>
     812:	00 
     813:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 81b <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x81b>
     81a:	00 
     81b:	48 01 d0             	add    %rdx,%rax
     81e:	66 90                	xchg   %ax,%ax
     820:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     824:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
     829:	48 83 c0 60          	add    $0x60,%rax
     82d:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     832:	c5 7a 6f 40 d0       	vmovdqu -0x30(%rax),%xmm8
     837:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
     83d:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
     842:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     848:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
     84d:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     852:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
     858:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
     85e:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     864:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
     869:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     86e:	c4 c3 79 0f c0 0c    	vpalignr $0xc,%xmm8,%xmm0,%xmm0
     874:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
     87a:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     880:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
     885:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
     88a:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
     890:	c4 43 7d 39 c2 01    	vextracti128 $0x1,%ymm8,%xmm10
     896:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     89c:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     8a1:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
     8a7:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     8ac:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     8b2:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     8b7:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     8bd:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     8c2:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     8c7:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     8cc:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     8d1:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     8d7:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     8dd:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     8e2:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     8e7:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     8ed:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     8f3:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     8f9:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     8ff:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     904:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     909:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     910:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     917:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     91d:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     922:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     927:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     92c:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     932:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
     936:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     93c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     941:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     947:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     94e:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
     954:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     959:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
     960:	c4 41 79 7e c1       	vmovd  %xmm8,%r9d
     965:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     96a:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
     970:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     975:	c4 43 79 16 c1 01    	vpextrd $0x1,%xmm8,%r9d
     97b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     980:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
     985:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     98a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     98f:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     995:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     99b:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     9a1:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     9a6:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     9ab:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     9b2:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     9b9:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     9bf:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     9c6:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     9cb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9d0:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     9d6:	c5 39 6c c0          	vpunpcklqdq %xmm0,%xmm8,%xmm8
     9da:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     9e0:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     9e5:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     9eb:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     9f1:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     9f6:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     9fb:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     a01:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     a08:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
     a0d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a12:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     a17:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     a1c:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
     a22:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     a28:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
     a2d:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a32:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a37:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     a3d:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     a43:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     a4a:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     a50:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     a55:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a5a:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     a60:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     a65:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     a6c:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     a71:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a76:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
     a7b:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     a82:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a87:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     a8d:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     a93:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     a97:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     a9d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     aa2:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     aa8:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     aad:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     ab2:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     ab9:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
     abe:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     ac3:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
     ac9:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     ace:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     ad4:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
     ad9:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     add:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     ae3:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     ae9:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
     aee:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     af4:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     afb:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     b00:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     b07:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
     b0e:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     b13:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
     b17:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     b1d:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     b21:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     b27:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
     b2d:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     b33:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     b3a:	4d 8d 48 48          	lea    0x48(%r8),%r9
     b3e:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     b43:	49 83 c0 20          	add    $0x20,%r8
     b47:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
     b4c:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
     b50:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     b56:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
     b5c:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
     b62:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
     b67:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     b6c:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     b72:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     b77:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     b7c:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     b80:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     b86:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
     b8b:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
     b91:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     b96:	4c 39 c9             	cmp    %r9,%rcx
     b99:	0f 83 81 fc ff ff    	jae    820 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x820>
     b9f:	4d 8d 48 08          	lea    0x8(%r8),%r9
     ba3:	4c 39 c9             	cmp    %r9,%rcx
     ba6:	0f 82 0e 01 00 00    	jb     cba <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcba>
     bac:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     bb0:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # bb8 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbb8>
     bb7:	00 
     bb8:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # bc0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbc0>
     bbf:	00 
     bc0:	48 01 d0             	add    %rdx,%rax
     bc3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     bc8:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     bcc:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     bd1:	48 83 c0 18          	add    $0x18,%rax
     bd5:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     bdb:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     be1:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     be6:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     bec:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     bf1:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     bf7:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     bfc:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     c02:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     c07:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     c0c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     c11:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     c16:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     c1c:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     c22:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     c27:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     c2c:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     c32:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     c38:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     c3e:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     c44:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     c49:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     c4e:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     c55:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     c5c:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     c61:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     c65:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     c6b:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     c72:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     c79:	4d 89 c8             	mov    %r9,%r8
     c7c:	49 83 c1 08          	add    $0x8,%r9
     c80:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     c84:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     c8a:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     c8f:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     c93:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     c99:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     c9e:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     ca3:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     ca7:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     cac:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     cb1:	4c 39 c9             	cmp    %r9,%rcx
     cb4:	0f 83 0e ff ff ff    	jae    bc8 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbc8>
     cba:	49 39 c8             	cmp    %rcx,%r8
     cbd:	0f 83 ed 01 00 00    	jae    eb0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb0>
     cc3:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     cc7:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     ccb:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     cd0:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     cd5:	c1 e0 08             	shl    $0x8,%eax
     cd8:	41 c1 e3 10          	shl    $0x10,%r11d
     cdc:	44 09 d8             	or     %r11d,%eax
     cdf:	45 0f b6 1a          	movzbl (%r10),%r11d
     ce3:	44 09 d8             	or     %r11d,%eax
     ce6:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     cea:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     cee:	41 8b 03             	mov    (%r11),%eax
     cf1:	45 0f b7 1b          	movzwl (%r11),%r11d
     cf5:	c1 e8 10             	shr    $0x10,%eax
     cf8:	66 45 89 1a          	mov    %r11w,(%r10)
     cfc:	41 88 42 02          	mov    %al,0x2(%r10)
     d00:	49 8d 40 01          	lea    0x1(%r8),%rax
     d04:	48 39 c8             	cmp    %rcx,%rax
     d07:	0f 83 a3 01 00 00    	jae    eb0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb0>
     d0d:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     d12:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d17:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d1c:	c1 e0 08             	shl    $0x8,%eax
     d1f:	41 c1 e3 10          	shl    $0x10,%r11d
     d23:	44 09 d8             	or     %r11d,%eax
     d26:	45 0f b6 1a          	movzbl (%r10),%r11d
     d2a:	44 09 d8             	or     %r11d,%eax
     d2d:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d31:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d35:	41 8b 03             	mov    (%r11),%eax
     d38:	45 0f b7 1b          	movzwl (%r11),%r11d
     d3c:	c1 e8 10             	shr    $0x10,%eax
     d3f:	66 45 89 1a          	mov    %r11w,(%r10)
     d43:	41 88 42 02          	mov    %al,0x2(%r10)
     d47:	49 8d 40 02          	lea    0x2(%r8),%rax
     d4b:	48 39 c8             	cmp    %rcx,%rax
     d4e:	0f 83 5c 01 00 00    	jae    eb0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb0>
     d54:	4e 8d 54 0a 06       	lea    0x6(%rdx,%r9,1),%r10
     d59:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     d5e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     d63:	c1 e0 08             	shl    $0x8,%eax
     d66:	41 c1 e3 10          	shl    $0x10,%r11d
     d6a:	44 09 d8             	or     %r11d,%eax
     d6d:	45 0f b6 1a          	movzbl (%r10),%r11d
     d71:	44 09 d8             	or     %r11d,%eax
     d74:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d78:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d7c:	41 8b 03             	mov    (%r11),%eax
     d7f:	45 0f b7 1b          	movzwl (%r11),%r11d
     d83:	c1 e8 10             	shr    $0x10,%eax
     d86:	66 45 89 1a          	mov    %r11w,(%r10)
     d8a:	41 88 42 02          	mov    %al,0x2(%r10)
     d8e:	49 8d 40 03          	lea    0x3(%r8),%rax
     d92:	48 39 c8             	cmp    %rcx,%rax
     d95:	0f 83 15 01 00 00    	jae    eb0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb0>
     d9b:	4e 8d 54 0a 09       	lea    0x9(%rdx,%r9,1),%r10
     da0:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     da5:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     daa:	c1 e0 10             	shl    $0x10,%eax
     dad:	41 c1 e3 08          	shl    $0x8,%r11d
     db1:	44 09 d8             	or     %r11d,%eax
     db4:	45 0f b6 1a          	movzbl (%r10),%r11d
     db8:	44 09 d8             	or     %r11d,%eax
     dbb:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     dbf:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     dc3:	41 8b 03             	mov    (%r11),%eax
     dc6:	45 0f b7 1b          	movzwl (%r11),%r11d
     dca:	c1 e8 10             	shr    $0x10,%eax
     dcd:	66 45 89 1a          	mov    %r11w,(%r10)
     dd1:	41 88 42 02          	mov    %al,0x2(%r10)
     dd5:	49 8d 40 04          	lea    0x4(%r8),%rax
     dd9:	48 39 c8             	cmp    %rcx,%rax
     ddc:	0f 83 ce 00 00 00    	jae    eb0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb0>
     de2:	4e 8d 54 0a 0c       	lea    0xc(%rdx,%r9,1),%r10
     de7:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     dec:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     df1:	c1 e0 10             	shl    $0x10,%eax
     df4:	41 c1 e3 08          	shl    $0x8,%r11d
     df8:	44 09 d8             	or     %r11d,%eax
     dfb:	45 0f b6 1a          	movzbl (%r10),%r11d
     dff:	44 09 d8             	or     %r11d,%eax
     e02:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e06:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e0a:	41 8b 03             	mov    (%r11),%eax
     e0d:	45 0f b7 1b          	movzwl (%r11),%r11d
     e11:	c1 e8 10             	shr    $0x10,%eax
     e14:	66 45 89 1a          	mov    %r11w,(%r10)
     e18:	41 88 42 02          	mov    %al,0x2(%r10)
     e1c:	49 8d 40 05          	lea    0x5(%r8),%rax
     e20:	48 39 c8             	cmp    %rcx,%rax
     e23:	0f 83 87 00 00 00    	jae    eb0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb0>
     e29:	4e 8d 54 0a 0f       	lea    0xf(%rdx,%r9,1),%r10
     e2e:	49 83 c0 06          	add    $0x6,%r8
     e32:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     e37:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     e3c:	c1 e0 10             	shl    $0x10,%eax
     e3f:	41 c1 e3 08          	shl    $0x8,%r11d
     e43:	44 09 d8             	or     %r11d,%eax
     e46:	45 0f b6 1a          	movzbl (%r10),%r11d
     e4a:	44 09 d8             	or     %r11d,%eax
     e4d:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e51:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e55:	41 8b 03             	mov    (%r11),%eax
     e58:	45 0f b7 1b          	movzwl (%r11),%r11d
     e5c:	c1 e8 10             	shr    $0x10,%eax
     e5f:	66 45 89 1a          	mov    %r11w,(%r10)
     e63:	41 88 42 02          	mov    %al,0x2(%r10)
     e67:	49 39 c8             	cmp    %rcx,%r8
     e6a:	73 44                	jae    eb0 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb0>
     e6c:	4a 8d 54 0a 12       	lea    0x12(%rdx,%r9,1),%rdx
     e71:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     e75:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     e79:	c1 e0 08             	shl    $0x8,%eax
     e7c:	c1 e1 10             	shl    $0x10,%ecx
     e7f:	09 c8                	or     %ecx,%eax
     e81:	0f b6 0a             	movzbl (%rdx),%ecx
     e84:	09 c8                	or     %ecx,%eax
     e86:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e8a:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     e8e:	8b 01                	mov    (%rcx),%eax
     e90:	0f b7 09             	movzwl (%rcx),%ecx
     e93:	c1 e8 10             	shr    $0x10,%eax
     e96:	66 89 0a             	mov    %cx,(%rdx)
     e99:	88 42 02             	mov    %al,0x2(%rdx)
     e9c:	c5 f8 77             	vzeroupper
     e9f:	5b                   	pop    %rbx
     ea0:	41 5c                	pop    %r12
     ea2:	41 5d                	pop    %r13
     ea4:	41 5e                	pop    %r14
     ea6:	41 5f                	pop    %r15
     ea8:	5d                   	pop    %rbp
     ea9:	c3                   	ret
     eaa:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     eb0:	c5 f8 77             	vzeroupper
     eb3:	5b                   	pop    %rbx
     eb4:	41 5c                	pop    %r12
     eb6:	41 5d                	pop    %r13
     eb8:	41 5e                	pop    %r14
     eba:	41 5f                	pop    %r15
     ebc:	5d                   	pop    %rbp
     ebd:	c3                   	ret
     ebe:	66 90                	xchg   %ax,%ax
     ec0:	49 89 c8             	mov    %rcx,%r8
     ec3:	e9 d7 fc ff ff       	jmp    b9f <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb9f>
     ec8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     ecf:	00 
     ed0:	c3                   	ret
     ed1:	49 8d 41 28          	lea    0x28(%r9),%rax
     ed5:	4d 89 c8             	mov    %r9,%r8
     ed8:	e9 19 f9 ff ff       	jmp    7f6 <jshc_channel::avx2_chain_vectorinput(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7f6>
     edd:	0f 1f 00             	nopl   (%rax)

0000000000000ee0 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     ee0:	f3 0f 1e fa          	endbr64
     ee4:	4d 85 c0             	test   %r8,%r8
     ee7:	0f 84 63 0f 00 00    	je     1e50 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf70>
     eed:	55                   	push   %rbp
     eee:	b8 00 04 00 00       	mov    $0x400,%eax
     ef3:	49 89 d2             	mov    %rdx,%r10
     ef6:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     efa:	49 89 cb             	mov    %rcx,%r11
     efd:	48 89 e5             	mov    %rsp,%rbp
     f00:	41 57                	push   %r15
     f02:	41 56                	push   %r14
     f04:	41 55                	push   %r13
     f06:	41 54                	push   %r12
     f08:	53                   	push   %rbx
     f09:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     f0d:	48 39 c2             	cmp    %rax,%rdx
     f10:	48 0f 47 d0          	cmova  %rax,%rdx
     f14:	31 c0                	xor    %eax,%eax
     f16:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     f1d:	00 00 00 
     f20:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
     f25:	48 83 c0 40          	add    $0x40,%rax
     f29:	48 39 d0             	cmp    %rdx,%rax
     f2c:	72 f2                	jb     f20 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     f2e:	4d 89 d1             	mov    %r10,%r9
     f31:	4c 89 da             	mov    %r11,%rdx
     f34:	31 c9                	xor    %ecx,%ecx
     f36:	eb 4c                	jmp    f84 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa4>
     f38:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     f3f:	00 
     f40:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     f45:	41 0f b6 59 02       	movzbl 0x2(%r9),%ebx
     f4a:	48 ff c1             	inc    %rcx
     f4d:	48 83 c2 03          	add    $0x3,%rdx
     f51:	49 83 c1 03          	add    $0x3,%r9
     f55:	c1 e3 10             	shl    $0x10,%ebx
     f58:	c1 e0 08             	shl    $0x8,%eax
     f5b:	09 d8                	or     %ebx,%eax
     f5d:	41 0f b6 59 fd       	movzbl -0x3(%r9),%ebx
     f62:	09 d8                	or     %ebx,%eax
     f64:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f68:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
     f6c:	8b 03                	mov    (%rbx),%eax
     f6e:	0f b7 1b             	movzwl (%rbx),%ebx
     f71:	c1 e8 10             	shr    $0x10,%eax
     f74:	66 89 5a fd          	mov    %bx,-0x3(%rdx)
     f78:	88 42 ff             	mov    %al,-0x1(%rdx)
     f7b:	49 39 c8             	cmp    %rcx,%r8
     f7e:	0f 84 c4 0e 00 00    	je     1e48 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf68>
     f84:	f6 c2 3f             	test   $0x3f,%dl
     f87:	75 b7                	jne    f40 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     f89:	48 8d 41 48          	lea    0x48(%rcx),%rax
     f8d:	49 39 c0             	cmp    %rax,%r8
     f90:	0f 82 bb 0e 00 00    	jb     1e51 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf71>
     f96:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     f9a:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # fa2 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc2>
     fa1:	00 
     fa2:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # faa <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xca>
     fa9:	00 
     faa:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
     faf:	49 8d 14 03          	lea    (%r11,%rax,1),%rdx
     fb3:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
     fb8:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # fc0 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe0>
     fbf:	00 
     fc0:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
     fc7:	00 
     fc8:	eb 09                	jmp    fd3 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
     fca:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     fd0:	4c 89 c9             	mov    %r9,%rcx
     fd3:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
     fda:	4d 39 c8             	cmp    %r9,%r8
     fdd:	72 15                	jb     ff4 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
     fdf:	0f 18 00             	prefetchnta (%rax)
     fe2:	0f 18 40 40          	prefetchnta 0x40(%rax)
     fe6:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
     fed:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
     ff4:	c5 fa 6f 80 00 fc ff 	vmovdqu -0x400(%rax),%xmm0
     ffb:	ff 
     ffc:	c5 fa 7e 88 10 fc ff 	vmovq  -0x3f0(%rax),%xmm1
    1003:	ff 
    1004:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    100b:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1011:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1017:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    101d:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1022:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1028:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    102d:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1033:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1038:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    103e:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1043:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1048:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    104d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1052:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1058:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    105e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1063:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1068:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    106e:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1074:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    107a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1080:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1085:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    108a:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1091:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1098:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    109e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    10a2:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    10a7:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    10ae:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    10b5:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    10b9:	c5 fa 7e 88 68 fb ff 	vmovq  -0x498(%rax),%xmm1
    10c0:	ff 
    10c1:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    10c7:	c5 fa 6f 80 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm0
    10ce:	ff 
    10cf:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    10d4:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    10da:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
    10df:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    10e5:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    10ea:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    10f0:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    10f5:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    10fb:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1100:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1106:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    110b:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1110:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1115:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    111a:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1120:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1126:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    112b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1130:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1136:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    113c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1142:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1148:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    114d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1152:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    1159:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1160:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1164:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1169:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    116f:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1176:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    117d:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
    1181:	c5 fa 7e 88 80 fb ff 	vmovq  -0x480(%rax),%xmm1
    1188:	ff 
    1189:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    118f:	c5 fa 6f 80 70 fb ff 	vmovdqu -0x490(%rax),%xmm0
    1196:	ff 
    1197:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    119c:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    11a2:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    11a7:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    11ad:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    11b2:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    11b8:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    11bd:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    11c3:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    11c8:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    11ce:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    11d3:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    11d8:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    11dd:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    11e2:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    11e8:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    11ee:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    11f3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    11f8:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    11fe:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1204:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    120a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1210:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1215:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    121a:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
    1221:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1228:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    122e:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
    1232:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    1237:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    123e:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    1245:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1249:	c5 fa 7e b0 98 fb ff 	vmovq  -0x468(%rax),%xmm6
    1250:	ff 
    1251:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1257:	c5 fa 6f 80 88 fb ff 	vmovdqu -0x478(%rax),%xmm0
    125e:	ff 
    125f:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1264:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    126a:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    126f:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1275:	c5 79 6f e9          	vmovdqa %xmm1,%xmm13
    1279:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    127f:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1284:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    128a:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    128f:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1295:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    129a:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    12a0:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    12a5:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    12aa:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    12af:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    12b4:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    12ba:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    12c0:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    12c6:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    12cc:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    12d1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    12d6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    12db:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    12e0:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    12e6:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    12ec:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    12f2:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
    12f9:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1300:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    1307:	c5 f9 6c c6          	vpunpcklqdq %xmm6,%xmm0,%xmm0
    130b:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
    1310:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
    1317:	c5 c1 6c fe          	vpunpcklqdq %xmm6,%xmm7,%xmm7
    131b:	c5 fa 7e b0 b0 fb ff 	vmovq  -0x450(%rax),%xmm6
    1322:	ff 
    1323:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    1329:	c5 fa 6f 80 a0 fb ff 	vmovdqu -0x460(%rax),%xmm0
    1330:	ff 
    1331:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    1336:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    133c:	c4 e2 55 36 ff       	vpermd %ymm7,%ymm5,%ymm7
    1341:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1347:	c5 79 6f f7          	vmovdqa %xmm7,%xmm14
    134b:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1351:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1356:	c4 c3 41 0f fe 08    	vpalignr $0x8,%xmm14,%xmm7,%xmm7
    135c:	c4 c1 71 6c ce       	vpunpcklqdq %xmm14,%xmm1,%xmm1
    1361:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    1367:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    136c:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1372:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    1377:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    137d:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1382:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1387:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    138c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1391:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1397:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    139d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    13a2:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    13a7:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    13ad:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    13b3:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    13b9:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    13bf:	c4 e3 75 38 cf 01    	vinserti128 $0x1,%xmm7,%ymm1,%ymm1
    13c5:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    13ca:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    13cf:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    13d6:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    13dd:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    13e3:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    13e8:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    13ed:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
    13f4:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    13fb:	c4 c1 49 6c f1       	vpunpcklqdq %xmm9,%xmm6,%xmm6
    1400:	c5 7a 7e 88 c8 fb ff 	vmovq  -0x438(%rax),%xmm9
    1407:	ff 
    1408:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    140e:	c5 fa 6f 80 b8 fb ff 	vmovdqu -0x448(%rax),%xmm0
    1415:	ff 
    1416:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    141b:	c4 63 31 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm9,%xmm9
    1421:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1426:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
    142c:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1431:	c4 c3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm9
    1437:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    143c:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1442:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1447:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    144c:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    1451:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    1457:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    145d:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1463:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1468:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    146d:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1472:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1477:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    147d:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    1483:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1488:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    148d:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1493:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    1499:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    149f:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    14a6:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    14ad:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    14b4:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    14b9:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    14be:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    14c5:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
    14ca:	c5 7a 7e 90 e0 fb ff 	vmovq  -0x420(%rax),%xmm10
    14d1:	ff 
    14d2:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
    14d8:	c5 7a 6f 88 d0 fb ff 	vmovdqu -0x430(%rax),%xmm9
    14df:	ff 
    14e0:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    14e5:	c4 43 29 0f d1 0c    	vpalignr $0xc,%xmm9,%xmm10,%xmm10
    14eb:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
    14f0:	c4 43 35 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm9,%ymm9
    14f6:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
    14fb:	c4 43 7d 39 ca 01    	vextracti128 $0x1,%ymm9,%xmm10
    1501:	c4 41 79 7e c9       	vmovd  %xmm9,%r9d
    1506:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
    150c:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    1511:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    1517:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    151c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1521:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1526:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    152b:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    1531:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    1537:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    153c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1541:	c4 43 79 16 c9 01    	vpextrd $0x1,%xmm9,%r9d
    1547:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
    154d:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1553:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    1559:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    155e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1563:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    156a:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    1571:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    1577:	c4 41 31 6c cb       	vpunpcklqdq %xmm11,%xmm9,%xmm9
    157c:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    1581:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    1588:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    158f:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1594:	c5 7a 7e 98 f8 fb ff 	vmovq  -0x408(%rax),%xmm11
    159b:	ff 
    159c:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
    15a2:	c5 7a 6f 88 e8 fb ff 	vmovdqu -0x418(%rax),%xmm9
    15a9:	ff 
    15aa:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
    15af:	c4 43 21 0f d9 0c    	vpalignr $0xc,%xmm9,%xmm11,%xmm11
    15b5:	c4 42 55 36 d2       	vpermd %ymm10,%ymm5,%ymm10
    15ba:	c4 43 35 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm9
    15c0:	c5 79 7f d7          	vmovdqa %xmm10,%xmm7
    15c4:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
    15ca:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
    15cf:	c4 43 7d 39 cb 01    	vextracti128 $0x1,%ymm9,%xmm11
    15d5:	c4 41 79 7e c9       	vmovd  %xmm9,%r9d
    15da:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
    15e0:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
    15e5:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
    15eb:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    15f0:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    15f5:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    15fa:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    15ff:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
    1605:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
    160b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1610:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1615:	c4 43 79 16 c9 01    	vpextrd $0x1,%xmm9,%r9d
    161b:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
    1621:	c4 21 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm12
    1627:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
    162d:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1632:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    1638:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    163f:	c4 23 19 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm12,%xmm12
    1646:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
    164d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1652:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
    1659:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    165d:	c4 41 21 6c dc       	vpunpcklqdq %xmm12,%xmm11,%xmm11
    1662:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
    1667:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    166e:	c5 fd e7 4a 80       	vmovntdq %ymm1,-0x80(%rdx)
    1673:	c5 f9 6f ce          	vmovdqa %xmm6,%xmm1
    1677:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    167d:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    1682:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
    1686:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    168c:	c4 43 35 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm9
    1692:	c4 c3 69 0f d4 08    	vpalignr $0x8,%xmm12,%xmm2,%xmm2
    1698:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    169d:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    16a3:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    16a8:	c4 c3 6d 38 d5 01    	vinserti128 $0x1,%xmm13,%ymm2,%ymm2
    16ae:	c4 41 39 6c c4       	vpunpcklqdq %xmm12,%xmm8,%xmm8
    16b3:	c4 42 55 36 c9       	vpermd %ymm9,%ymm5,%ymm9
    16b8:	c5 fd e7 92 60 ff ff 	vmovntdq %ymm2,-0xa0(%rdx)
    16bf:	ff 
    16c0:	c4 43 25 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm11,%ymm8
    16c6:	c5 79 7f ca          	vmovdqa %xmm9,%xmm2
    16ca:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    16d0:	c5 7d e7 82 40 ff ff 	vmovntdq %ymm8,-0xc0(%rdx)
    16d7:	ff 
    16d8:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    16dc:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    16e2:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
    16e6:	c4 c3 79 0f c0 08    	vpalignr $0x8,%xmm8,%xmm0,%xmm0
    16ec:	c4 63 31 0f ca 08    	vpalignr $0x8,%xmm2,%xmm9,%xmm9
    16f2:	c4 c1 49 6c f0       	vpunpcklqdq %xmm8,%xmm6,%xmm6
    16f7:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
    16fd:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    1703:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
    1709:	c5 fd e7 4a a0       	vmovntdq %ymm1,-0x60(%rdx)
    170e:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    1713:	c5 7d e7 52 e0       	vmovntdq %ymm10,-0x20(%rdx)
    1718:	4d 39 d0             	cmp    %r10,%r8
    171b:	0f 83 af f8 ff ff    	jae    fd0 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    1721:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1726:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    172b:	48 8d 41 68          	lea    0x68(%rcx),%rax
    172f:	0f ae f8             	sfence
    1732:	49 39 c0             	cmp    %rax,%r8
    1735:	0f 82 be 03 00 00    	jb     1af9 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc19>
    173b:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    173f:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1747 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x867>
    1746:	00 
    1747:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 174f <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x86f>
    174e:	00 
    174f:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1754:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1759:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1761 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x881>
    1760:	00 
    1761:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
    1765:	4c 01 da             	add    %r11,%rdx
    1768:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    176f:	00 
    1770:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
    1774:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    1779:	48 83 c2 60          	add    $0x60,%rdx
    177d:	48 83 c0 60          	add    $0x60,%rax
    1781:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
    1786:	c5 7a 6f 40 d0       	vmovdqu -0x30(%rax),%xmm8
    178b:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    1791:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
    1796:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    179c:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
    17a1:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    17a6:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
    17ac:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
    17b2:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    17b8:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
    17bd:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    17c2:	c4 c3 79 0f c0 0c    	vpalignr $0xc,%xmm8,%xmm0,%xmm0
    17c8:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
    17ce:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    17d4:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
    17d9:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
    17de:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
    17e4:	c4 43 7d 39 c2 01    	vextracti128 $0x1,%ymm8,%xmm10
    17ea:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    17f0:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    17f5:	c4 e3 7d 39 c6 01    	vextracti128 $0x1,%ymm0,%xmm6
    17fb:	c5 f9 7e c1          	vmovd  %xmm0,%ecx
    17ff:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1805:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    180a:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    1810:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1815:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    181a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    181f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1824:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    182a:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1830:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1835:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    183a:	c4 e3 79 16 c1 01    	vpextrd $0x1,%xmm0,%ecx
    1840:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1846:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    184c:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    1852:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1856:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    185b:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    1862:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1869:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    186f:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    1875:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    187a:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    187f:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    1885:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
    188a:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    188f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1894:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    189a:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    18a1:	c5 79 7e c1          	vmovd  %xmm8,%ecx
    18a5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    18aa:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    18b1:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
    18b7:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    18bc:	c4 63 79 16 c1 01    	vpextrd $0x1,%xmm8,%ecx
    18c2:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    18c7:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
    18cd:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    18d1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    18d6:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    18db:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
    18e0:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    18e6:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    18ec:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    18f2:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    18f8:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    18fd:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    1904:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    190b:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    1911:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
    1918:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    191d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1922:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    1928:	c4 41 39 6c c2       	vpunpcklqdq %xmm10,%xmm8,%xmm8
    192d:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    1932:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1937:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    193d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1942:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1947:	c5 f9 7e c9          	vmovd  %xmm1,%ecx
    194b:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1950:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    1957:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    195d:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1963:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1968:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    196d:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    1973:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1979:	c4 c1 79 6c c2       	vpunpcklqdq %xmm10,%xmm0,%xmm0
    197e:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    1985:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1989:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    198f:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    1995:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    199b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    19a0:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    19a6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    19ab:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    19b1:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    19b6:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    19bd:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    19c2:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    19c7:	c4 e2 55 36 c0       	vpermd %ymm0,%ymm5,%ymm0
    19cc:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    19d3:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    19d8:	c5 f9 7e d1          	vmovd  %xmm2,%ecx
    19dc:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    19e2:	c4 41 39 6c c1       	vpunpcklqdq %xmm9,%xmm8,%xmm8
    19e7:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    19ec:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    19f1:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    19f7:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    19fb:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1a00:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1a07:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    1a0d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1a12:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    1a18:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
    1a1d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1a22:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    1a26:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1a2c:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1a32:	c4 21 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm8
    1a38:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1a3e:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    1a44:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1a49:	c4 23 39 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm8,%xmm8
    1a50:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    1a57:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    1a5c:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1a63:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
    1a67:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1a6d:	c4 c1 41 6c f8       	vpunpcklqdq %xmm8,%xmm7,%xmm7
    1a72:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
    1a77:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
    1a7d:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1a81:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1a87:	49 83 c1 20          	add    $0x20,%r9
    1a8b:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
    1a92:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1a97:	c4 c1 69 6c d0       	vpunpcklqdq %xmm8,%xmm2,%xmm2
    1a9c:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
    1aa0:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1aa6:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
    1aac:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
    1ab2:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
    1ab7:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1abc:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1ac2:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    1ac7:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1acc:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    1ad0:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1ad6:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    1adb:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
    1ae1:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1ae6:	49 39 c8             	cmp    %rcx,%r8
    1ae9:	0f 83 81 fc ff ff    	jae    1770 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x890>
    1aef:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1af4:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1af9:	49 8d 51 08          	lea    0x8(%r9),%rdx
    1afd:	49 39 d0             	cmp    %rdx,%r8
    1b00:	0f 82 2a 01 00 00    	jb     1c30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd50>
    1b06:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1b0a:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1b12 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc32>
    1b11:	00 
    1b12:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1b1a <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc3a>
    1b19:	00 
    1b1a:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1b1f:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1b24:	49 8d 0c 02          	lea    (%r10,%rax,1),%rcx
    1b28:	4c 01 d8             	add    %r11,%rax
    1b2b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1b30:	c5 fa 6f 01          	vmovdqu (%rcx),%xmm0
    1b34:	c5 fa 7e 49 10       	vmovq  0x10(%rcx),%xmm1
    1b39:	48 83 c0 18          	add    $0x18,%rax
    1b3d:	48 83 c1 18          	add    $0x18,%rcx
    1b41:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1b47:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1b4d:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1b52:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1b58:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1b5d:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1b63:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1b68:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1b6e:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1b73:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1b78:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1b7d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1b82:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1b88:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1b8e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1b93:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1b98:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1b9e:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1ba4:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1baa:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1bb0:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1bb5:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1bba:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1bc1:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1bc8:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1bce:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1bd2:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1bd7:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1bde:	49 89 d1             	mov    %rdx,%r9
    1be1:	48 83 c2 08          	add    $0x8,%rdx
    1be5:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    1bec:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1bf0:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1bf6:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1bfb:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1bff:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1c05:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1c0a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1c0f:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1c13:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    1c18:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
    1c1d:	49 39 d0             	cmp    %rdx,%r8
    1c20:	0f 83 0a ff ff ff    	jae    1b30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc50>
    1c26:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1c2b:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1c30:	4d 39 c1             	cmp    %r8,%r9
    1c33:	0f 83 f7 01 00 00    	jae    1e30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf50>
    1c39:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1c3d:	49 8d 1c 02          	lea    (%r10,%rax,1),%rbx
    1c41:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1c45:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1c4a:	0f b6 1b             	movzbl (%rbx),%ebx
    1c4d:	c1 e2 08             	shl    $0x8,%edx
    1c50:	41 c1 e4 10          	shl    $0x10,%r12d
    1c54:	44 09 e2             	or     %r12d,%edx
    1c57:	09 da                	or     %ebx,%edx
    1c59:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c5d:	48 8d 1c 96          	lea    (%rsi,%rdx,4),%rbx
    1c61:	8b 13                	mov    (%rbx),%edx
    1c63:	0f b7 1b             	movzwl (%rbx),%ebx
    1c66:	c1 ea 10             	shr    $0x10,%edx
    1c69:	66 41 89 1c 03       	mov    %bx,(%r11,%rax,1)
    1c6e:	41 88 54 03 02       	mov    %dl,0x2(%r11,%rax,1)
    1c73:	49 8d 51 01          	lea    0x1(%r9),%rdx
    1c77:	4c 39 c2             	cmp    %r8,%rdx
    1c7a:	0f 83 b0 01 00 00    	jae    1e30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf50>
    1c80:	49 8d 5c 02 03       	lea    0x3(%r10,%rax,1),%rbx
    1c85:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1c89:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1c8e:	0f b6 1b             	movzbl (%rbx),%ebx
    1c91:	41 c1 e4 10          	shl    $0x10,%r12d
    1c95:	c1 e2 08             	shl    $0x8,%edx
    1c98:	44 09 e2             	or     %r12d,%edx
    1c9b:	09 da                	or     %ebx,%edx
    1c9d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1ca1:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1ca5:	8b 1a                	mov    (%rdx),%ebx
    1ca7:	44 0f b7 22          	movzwl (%rdx),%r12d
    1cab:	49 8d 51 02          	lea    0x2(%r9),%rdx
    1caf:	89 d9                	mov    %ebx,%ecx
    1cb1:	66 45 89 64 03 03    	mov    %r12w,0x3(%r11,%rax,1)
    1cb7:	c1 e9 10             	shr    $0x10,%ecx
    1cba:	41 88 4c 03 05       	mov    %cl,0x5(%r11,%rax,1)
    1cbf:	4c 39 c2             	cmp    %r8,%rdx
    1cc2:	0f 83 68 01 00 00    	jae    1e30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf50>
    1cc8:	49 8d 5c 02 06       	lea    0x6(%r10,%rax,1),%rbx
    1ccd:	0f b6 53 01          	movzbl 0x1(%rbx),%edx
    1cd1:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    1cd6:	0f b6 1b             	movzbl (%rbx),%ebx
    1cd9:	41 c1 e4 10          	shl    $0x10,%r12d
    1cdd:	c1 e2 08             	shl    $0x8,%edx
    1ce0:	44 09 e2             	or     %r12d,%edx
    1ce3:	09 da                	or     %ebx,%edx
    1ce5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1ce9:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1ced:	8b 1a                	mov    (%rdx),%ebx
    1cef:	44 0f b7 22          	movzwl (%rdx),%r12d
    1cf3:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1cf7:	89 d9                	mov    %ebx,%ecx
    1cf9:	66 45 89 64 03 06    	mov    %r12w,0x6(%r11,%rax,1)
    1cff:	c1 e9 10             	shr    $0x10,%ecx
    1d02:	41 88 4c 03 08       	mov    %cl,0x8(%r11,%rax,1)
    1d07:	4c 39 c2             	cmp    %r8,%rdx
    1d0a:	0f 83 20 01 00 00    	jae    1e30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf50>
    1d10:	49 8d 5c 02 09       	lea    0x9(%r10,%rax,1),%rbx
    1d15:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1d19:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1d1e:	0f b6 1b             	movzbl (%rbx),%ebx
    1d21:	41 c1 e4 08          	shl    $0x8,%r12d
    1d25:	c1 e2 10             	shl    $0x10,%edx
    1d28:	44 09 e2             	or     %r12d,%edx
    1d2b:	09 da                	or     %ebx,%edx
    1d2d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1d31:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1d35:	8b 1a                	mov    (%rdx),%ebx
    1d37:	44 0f b7 22          	movzwl (%rdx),%r12d
    1d3b:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1d3f:	89 d9                	mov    %ebx,%ecx
    1d41:	66 45 89 64 03 09    	mov    %r12w,0x9(%r11,%rax,1)
    1d47:	c1 e9 10             	shr    $0x10,%ecx
    1d4a:	41 88 4c 03 0b       	mov    %cl,0xb(%r11,%rax,1)
    1d4f:	4c 39 c2             	cmp    %r8,%rdx
    1d52:	0f 83 d8 00 00 00    	jae    1e30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf50>
    1d58:	49 8d 5c 02 0c       	lea    0xc(%r10,%rax,1),%rbx
    1d5d:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1d61:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1d66:	0f b6 1b             	movzbl (%rbx),%ebx
    1d69:	41 c1 e4 08          	shl    $0x8,%r12d
    1d6d:	c1 e2 10             	shl    $0x10,%edx
    1d70:	44 09 e2             	or     %r12d,%edx
    1d73:	09 da                	or     %ebx,%edx
    1d75:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1d79:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1d7d:	8b 1a                	mov    (%rdx),%ebx
    1d7f:	44 0f b7 22          	movzwl (%rdx),%r12d
    1d83:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1d87:	c1 eb 10             	shr    $0x10,%ebx
    1d8a:	66 45 89 64 03 0c    	mov    %r12w,0xc(%r11,%rax,1)
    1d90:	41 88 5c 03 0e       	mov    %bl,0xe(%r11,%rax,1)
    1d95:	4c 39 c2             	cmp    %r8,%rdx
    1d98:	0f 83 92 00 00 00    	jae    1e30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf50>
    1d9e:	49 8d 5c 02 0f       	lea    0xf(%r10,%rax,1),%rbx
    1da3:	49 83 c1 06          	add    $0x6,%r9
    1da7:	0f b6 53 02          	movzbl 0x2(%rbx),%edx
    1dab:	44 0f b6 63 01       	movzbl 0x1(%rbx),%r12d
    1db0:	0f b6 1b             	movzbl (%rbx),%ebx
    1db3:	41 c1 e4 08          	shl    $0x8,%r12d
    1db7:	c1 e2 10             	shl    $0x10,%edx
    1dba:	44 09 e2             	or     %r12d,%edx
    1dbd:	09 da                	or     %ebx,%edx
    1dbf:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1dc3:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1dc7:	8b 1a                	mov    (%rdx),%ebx
    1dc9:	44 0f b7 22          	movzwl (%rdx),%r12d
    1dcd:	89 d9                	mov    %ebx,%ecx
    1dcf:	66 45 89 64 03 0f    	mov    %r12w,0xf(%r11,%rax,1)
    1dd5:	c1 e9 10             	shr    $0x10,%ecx
    1dd8:	41 88 4c 03 11       	mov    %cl,0x11(%r11,%rax,1)
    1ddd:	4d 39 c1             	cmp    %r8,%r9
    1de0:	73 4e                	jae    1e30 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf50>
    1de2:	49 8d 54 02 12       	lea    0x12(%r10,%rax,1),%rdx
    1de7:	4d 8d 44 03 12       	lea    0x12(%r11,%rax,1),%r8
    1dec:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1df0:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1df4:	0f b6 12             	movzbl (%rdx),%edx
    1df7:	c1 e0 08             	shl    $0x8,%eax
    1dfa:	c1 e1 10             	shl    $0x10,%ecx
    1dfd:	09 c8                	or     %ecx,%eax
    1dff:	09 d0                	or     %edx,%eax
    1e01:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1e05:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1e09:	8b 02                	mov    (%rdx),%eax
    1e0b:	0f b7 12             	movzwl (%rdx),%edx
    1e0e:	c1 e8 10             	shr    $0x10,%eax
    1e11:	66 41 89 10          	mov    %dx,(%r8)
    1e15:	41 88 40 02          	mov    %al,0x2(%r8)
    1e19:	c5 f8 77             	vzeroupper
    1e1c:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1e20:	5b                   	pop    %rbx
    1e21:	41 5c                	pop    %r12
    1e23:	41 5d                	pop    %r13
    1e25:	41 5e                	pop    %r14
    1e27:	41 5f                	pop    %r15
    1e29:	5d                   	pop    %rbp
    1e2a:	c3                   	ret
    1e2b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1e30:	c5 f8 77             	vzeroupper
    1e33:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1e37:	5b                   	pop    %rbx
    1e38:	41 5c                	pop    %r12
    1e3a:	41 5d                	pop    %r13
    1e3c:	41 5e                	pop    %r14
    1e3e:	41 5f                	pop    %r15
    1e40:	5d                   	pop    %rbp
    1e41:	c3                   	ret
    1e42:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1e48:	4d 89 c1             	mov    %r8,%r9
    1e4b:	e9 a9 fc ff ff       	jmp    1af9 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc19>
    1e50:	c3                   	ret
    1e51:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1e55:	49 89 c9             	mov    %rcx,%r9
    1e58:	e9 d5 f8 ff ff       	jmp    1732 <jshc_channel::avx2_chain_vectorinput_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x852>
