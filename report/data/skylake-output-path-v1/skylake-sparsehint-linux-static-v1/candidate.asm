
artifacts/skylake-sparsehint-linux-build-v1/CMakeFiles/jshc_skylake_sparsehint.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 d3 0f 00 00    	je     fe0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe0>
       d:	55                   	push   %rbp
       e:	4c 8d 04 49          	lea    (%rcx,%rcx,2),%r8
      12:	48 89 f8             	mov    %rdi,%rax
      15:	48 89 d7             	mov    %rdx,%rdi
      18:	ba 00 04 00 00       	mov    $0x400,%edx
      1d:	49 39 d0             	cmp    %rdx,%r8
      20:	48 89 e5             	mov    %rsp,%rbp
      23:	41 57                	push   %r15
      25:	4c 0f 47 c2          	cmova  %rdx,%r8
      29:	31 d2                	xor    %edx,%edx
      2b:	41 56                	push   %r14
      2d:	41 55                	push   %r13
      2f:	41 54                	push   %r12
      31:	53                   	push   %rbx
      32:	0f 1f 00             	nopl   (%rax)
      35:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
      3c:	00 00 00 00 
      40:	0f 18 04 17          	prefetchnta (%rdi,%rdx,1)
      44:	48 83 c2 40          	add    $0x40,%rdx
      48:	4c 39 c2             	cmp    %r8,%rdx
      4b:	72 f3                	jb     40 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x40>
      4d:	49 89 f8             	mov    %rdi,%r8
      50:	45 31 c9             	xor    %r9d,%r9d
      53:	eb 4a                	jmp    9f <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x9f>
      55:	0f 1f 00             	nopl   (%rax)
      58:	41 0f b6 50 01       	movzbl 0x1(%r8),%edx
      5d:	45 0f b6 50 02       	movzbl 0x2(%r8),%r10d
      62:	49 ff c1             	inc    %r9
      65:	49 83 c0 03          	add    $0x3,%r8
      69:	41 c1 e2 10          	shl    $0x10,%r10d
      6d:	c1 e2 08             	shl    $0x8,%edx
      70:	44 09 d2             	or     %r10d,%edx
      73:	45 0f b6 50 fd       	movzbl -0x3(%r8),%r10d
      78:	44 09 d2             	or     %r10d,%edx
      7b:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
      7f:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
      83:	41 8b 12             	mov    (%r10),%edx
      86:	45 0f b7 12          	movzwl (%r10),%r10d
      8a:	c1 ea 10             	shr    $0x10,%edx
      8d:	66 45 89 50 fd       	mov    %r10w,-0x3(%r8)
      92:	41 88 50 ff          	mov    %dl,-0x1(%r8)
      96:	4c 39 c9             	cmp    %r9,%rcx
      99:	0f 84 31 0f 00 00    	je     fd0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfd0>
      9f:	41 f6 c0 3f          	test   $0x3f,%r8b
      a3:	75 b3                	jne    58 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x58>
      a5:	49 8d 51 48          	lea    0x48(%r9),%rdx
      a9:	48 39 d1             	cmp    %rdx,%rcx
      ac:	0f 82 2f 0f 00 00    	jb     fe1 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfe1>
      b2:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
      b6:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # be <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbe>
      bd:	00 
      be:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # c6 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc6>
      c5:	00 
      c6:	48 01 fa             	add    %rdi,%rdx
      c9:	eb 08                	jmp    d3 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd3>
      cb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      d0:	4d 89 c1             	mov    %r8,%r9
      d3:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      da:	4c 39 c1             	cmp    %r8,%rcx
      dd:	72 1c                	jb     fb <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfb>
      df:	0f 18 82 00 04 00 00 	prefetchnta 0x400(%rdx)
      e6:	0f 18 82 40 04 00 00 	prefetchnta 0x440(%rdx)
      ed:	0f 18 82 80 04 00 00 	prefetchnta 0x480(%rdx)
      f4:	0f 18 82 bf 04 00 00 	prefetchnta 0x4bf(%rdx)
      fb:	4d 8d 81 b2 00 00 00 	lea    0xb2(%r9),%r8
     102:	4c 39 c1             	cmp    %r8,%rcx
     105:	72 4c                	jb     153 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x153>
     107:	44 8b 82 80 01 00 00 	mov    0x180(%rdx),%r8d
     10e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     115:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     11a:	44 8b 82 b0 01 00 00 	mov    0x1b0(%rdx),%r8d
     121:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     128:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     12d:	44 8b 82 e0 01 00 00 	mov    0x1e0(%rdx),%r8d
     134:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     13b:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     140:	44 8b 82 10 02 00 00 	mov    0x210(%rdx),%r8d
     147:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     14e:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     153:	44 8b 62 0c          	mov    0xc(%rdx),%r12d
     157:	44 8b 72 12          	mov    0x12(%rdx),%r14d
     15b:	44 8b 02             	mov    (%rdx),%r8d
     15e:	44 8b 5a 06          	mov    0x6(%rdx),%r11d
     162:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     169:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     170:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     175:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     17a:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     181:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     188:	44 8b 62 0f          	mov    0xf(%rdx),%r12d
     18c:	44 8b 72 15          	mov    0x15(%rdx),%r14d
     190:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     196:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     19c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     1a3:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     1aa:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     1af:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     1b4:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     1b9:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     1be:	44 8b 42 03          	mov    0x3(%rdx),%r8d
     1c2:	44 8b 5a 09          	mov    0x9(%rdx),%r11d
     1c6:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     1cd:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     1d4:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1db:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1e2:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     1e8:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     1ed:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     1f2:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     1f6:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     1fb:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     202:	44 8b 42 18          	mov    0x18(%rdx),%r8d
     206:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     20d:	44 8b 5a 1e          	mov    0x1e(%rdx),%r11d
     211:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     218:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     21f:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     224:	44 8b 42 1b          	mov    0x1b(%rdx),%r8d
     228:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     22c:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     231:	44 8b 5a 21          	mov    0x21(%rdx),%r11d
     235:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     23b:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     242:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     247:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     24e:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     253:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     258:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     25d:	44 8b 62 24          	mov    0x24(%rdx),%r12d
     261:	44 8b 72 2a          	mov    0x2a(%rdx),%r14d
     265:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     26b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     272:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     279:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     27e:	44 8b 62 27          	mov    0x27(%rdx),%r12d
     282:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     287:	44 8b 72 2d          	mov    0x2d(%rdx),%r14d
     28b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     292:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     298:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     29f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2a6:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     2ab:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     2b1:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     2b6:	44 8b 42 30          	mov    0x30(%rdx),%r8d
     2ba:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     2c1:	44 8b 62 3c          	mov    0x3c(%rdx),%r12d
     2c5:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     2cc:	44 8b 72 42          	mov    0x42(%rdx),%r14d
     2d0:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2d7:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2de:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     2e3:	44 8b 42 33          	mov    0x33(%rdx),%r8d
     2e7:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     2eb:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     2f0:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2f7:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     2fc:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     301:	44 8b 62 3f          	mov    0x3f(%rdx),%r12d
     305:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     30c:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     313:	44 8b 5a 36          	mov    0x36(%rdx),%r11d
     317:	44 8b 72 45          	mov    0x45(%rdx),%r14d
     31b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     322:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     327:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     32e:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     332:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     337:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     33c:	44 8b 5a 39          	mov    0x39(%rdx),%r11d
     340:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     347:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     34d:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     352:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     357:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     35e:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     363:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     368:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     36e:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     372:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     378:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     37e:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     384:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     38a:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     391:	44 8b 72 5a          	mov    0x5a(%rdx),%r14d
     395:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     39c:	44 8b 62 54          	mov    0x54(%rdx),%r12d
     3a0:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     3a7:	c4 a3 51 22 2c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm5,%xmm5
     3ae:	44 8b 42 48          	mov    0x48(%rdx),%r8d
     3b2:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     3b6:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     3bb:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     3c2:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     3c7:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     3cc:	44 8b 72 5d          	mov    0x5d(%rdx),%r14d
     3d0:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3d7:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     3de:	44 8b 62 57          	mov    0x57(%rdx),%r12d
     3e2:	44 8b 5a 4e          	mov    0x4e(%rdx),%r11d
     3e6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     3ed:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     3f2:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     3f6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     3fd:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     402:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     408:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     40d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     414:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     41a:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     420:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     425:	44 8b 42 4b          	mov    0x4b(%rdx),%r8d
     429:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     42e:	44 8b 5a 51          	mov    0x51(%rdx),%r11d
     432:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     439:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     43e:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     445:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     44c:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     452:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     456:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     45d:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     462:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     468:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     46e:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     473:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     477:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     47c:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     483:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     48a:	44 8b 42 60          	mov    0x60(%rdx),%r8d
     48e:	44 8b 62 6c          	mov    0x6c(%rdx),%r12d
     492:	44 8b 72 72          	mov    0x72(%rdx),%r14d
     496:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     49d:	44 8b 5a 66          	mov    0x66(%rdx),%r11d
     4a1:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     4a5:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     4ac:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     4b3:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     4b9:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     4be:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     4c3:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     4c8:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     4cf:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     4d4:	44 8b 62 6f          	mov    0x6f(%rdx),%r12d
     4d8:	44 8b 72 75          	mov    0x75(%rdx),%r14d
     4dc:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     4e1:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     4e7:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     4ed:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     4f4:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     4fb:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     500:	44 8b 42 63          	mov    0x63(%rdx),%r8d
     504:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     509:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     50e:	44 8b 5a 69          	mov    0x69(%rdx),%r11d
     512:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     519:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     51f:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     526:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     52d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     534:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     539:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     53e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     542:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     547:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     54e:	44 8b 42 78          	mov    0x78(%rdx),%r8d
     552:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     559:	44 8b 5a 7e          	mov    0x7e(%rdx),%r11d
     55d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     564:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     56b:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     570:	44 8b 42 7b          	mov    0x7b(%rdx),%r8d
     574:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     578:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     57d:	44 8b 9a 81 00 00 00 	mov    0x81(%rdx),%r11d
     584:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     58a:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     591:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     596:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     59d:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     5a2:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     5a7:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     5ac:	44 8b a2 84 00 00 00 	mov    0x84(%rdx),%r12d
     5b3:	44 8b b2 8a 00 00 00 	mov    0x8a(%rdx),%r14d
     5ba:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     5bf:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5c6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5cd:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     5d2:	44 8b a2 87 00 00 00 	mov    0x87(%rdx),%r12d
     5d9:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     5de:	44 8b b2 8d 00 00 00 	mov    0x8d(%rdx),%r14d
     5e5:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5ec:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     5f2:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     5f9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     600:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     605:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     60b:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     610:	44 8b 9a 96 00 00 00 	mov    0x96(%rdx),%r11d
     617:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     61e:	44 8b a2 9c 00 00 00 	mov    0x9c(%rdx),%r12d
     625:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     62c:	44 8b b2 a2 00 00 00 	mov    0xa2(%rdx),%r14d
     633:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     63a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     641:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     646:	44 8b 9a 99 00 00 00 	mov    0x99(%rdx),%r11d
     64d:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     651:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     657:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     65e:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     663:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     668:	44 8b a2 9f 00 00 00 	mov    0x9f(%rdx),%r12d
     66f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     676:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     67d:	44 8b 82 90 00 00 00 	mov    0x90(%rdx),%r8d
     684:	44 8b b2 a5 00 00 00 	mov    0xa5(%rdx),%r14d
     68b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     692:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     697:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     69e:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     6a2:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     6a7:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     6ac:	44 8b 82 93 00 00 00 	mov    0x93(%rdx),%r8d
     6b3:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     6ba:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     6c0:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     6c5:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     6ca:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     6d1:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     6d6:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     6db:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     6e1:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     6e7:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     6ec:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     6f3:	44 8b b2 ba 00 00 00 	mov    0xba(%rdx),%r14d
     6fa:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     701:	44 8b a2 b4 00 00 00 	mov    0xb4(%rdx),%r12d
     708:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     70f:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     716:	44 8b 9a ae 00 00 00 	mov    0xae(%rdx),%r11d
     71d:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     721:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     727:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     72e:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     733:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     738:	44 8b b2 bd 00 00 00 	mov    0xbd(%rdx),%r14d
     73f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     746:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     74d:	44 8b a2 b7 00 00 00 	mov    0xb7(%rdx),%r12d
     754:	44 8b 82 a8 00 00 00 	mov    0xa8(%rdx),%r8d
     75b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     762:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     767:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     76c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     773:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     778:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     77e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     785:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     78a:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     790:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     796:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     79b:	44 8b 9a b1 00 00 00 	mov    0xb1(%rdx),%r11d
     7a2:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     7a7:	44 8b 82 ab 00 00 00 	mov    0xab(%rdx),%r8d
     7ae:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     7b5:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     7ba:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     7c1:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     7c8:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     7cd:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     7d4:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     7d9:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
     7e0:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     7e5:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     7e9:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     7ef:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     7f6:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     7fd:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     804:	4d 8d 41 40          	lea    0x40(%r9),%r8
     808:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     80d:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     812:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     818:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     81e:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     823:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     829:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     82f:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     834:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     839:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     83e:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     843:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     849:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     84f:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
     856:	ff 
     857:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     85b:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     85f:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
     866:	ff 
     867:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
     86c:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     870:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     874:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     87a:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     880:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     886:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     88c:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     891:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     895:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     89b:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     8a1:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     8a7:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     8ad:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     8b3:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
     8b8:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
     8bd:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
     8c2:	4c 39 d1             	cmp    %r10,%rcx
     8c5:	0f 83 05 f8 ff ff    	jae    d0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd0>
     8cb:	0f ae f8             	sfence
     8ce:	49 8d 51 68          	lea    0x68(%r9),%rdx
     8d2:	48 39 d1             	cmp    %rdx,%rcx
     8d5:	0f 82 bb 03 00 00    	jb     c96 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc96>
     8db:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     8df:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 8e7 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8e7>
     8e6:	00 
     8e7:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 8ef <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8ef>
     8ee:	00 
     8ef:	48 01 fa             	add    %rdi,%rdx
     8f2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     8f8:	44 8b 62 54          	mov    0x54(%rdx),%r12d
     8fc:	44 8b 72 5a          	mov    0x5a(%rdx),%r14d
     900:	44 8b 4a 48          	mov    0x48(%rdx),%r9d
     904:	44 8b 5a 4e          	mov    0x4e(%rdx),%r11d
     908:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     90f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     916:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     91b:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     920:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     927:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     92e:	44 8b 62 57          	mov    0x57(%rdx),%r12d
     932:	44 8b 72 5d          	mov    0x5d(%rdx),%r14d
     936:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     93c:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     942:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     949:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     950:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     955:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     95a:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     95f:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     964:	44 8b 4a 4b          	mov    0x4b(%rdx),%r9d
     968:	44 8b 5a 51          	mov    0x51(%rdx),%r11d
     96c:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     973:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     97a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     981:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     988:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     98e:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
     993:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     998:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     99c:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     9a1:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
     9a8:	44 8b 4a 30          	mov    0x30(%rdx),%r9d
     9ac:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     9b3:	44 8b 5a 36          	mov    0x36(%rdx),%r11d
     9b7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     9be:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9c5:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     9ca:	44 8b 4a 33          	mov    0x33(%rdx),%r9d
     9ce:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     9d2:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     9d7:	44 8b 5a 39          	mov    0x39(%rdx),%r11d
     9db:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     9e1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     9e8:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     9ed:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9f4:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
     9f9:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     9fe:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     a03:	44 8b 62 3c          	mov    0x3c(%rdx),%r12d
     a07:	44 8b 72 42          	mov    0x42(%rdx),%r14d
     a0b:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     a10:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a17:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a1e:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     a23:	44 8b 62 3f          	mov    0x3f(%rdx),%r12d
     a27:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     a2c:	44 8b 72 45          	mov    0x45(%rdx),%r14d
     a30:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a37:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     a3d:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     a44:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a4b:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     a50:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     a56:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     a5b:	44 8b 5a 1e          	mov    0x1e(%rdx),%r11d
     a5f:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     a66:	44 8b 62 24          	mov    0x24(%rdx),%r12d
     a6a:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     a71:	44 8b 72 2a          	mov    0x2a(%rdx),%r14d
     a75:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a7c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a83:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     a88:	44 8b 5a 21          	mov    0x21(%rdx),%r11d
     a8c:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     a90:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     a96:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a9d:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     aa2:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     aa7:	44 8b 62 27          	mov    0x27(%rdx),%r12d
     aab:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     ab2:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     ab9:	44 8b 4a 18          	mov    0x18(%rdx),%r9d
     abd:	44 8b 72 2d          	mov    0x2d(%rdx),%r14d
     ac1:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     ac8:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     acd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ad4:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     ad8:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     add:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     ae2:	44 8b 4a 1b          	mov    0x1b(%rdx),%r9d
     ae6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     aed:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     af3:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     af8:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     afd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b04:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     b09:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
     b0e:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     b14:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     b18:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     b1e:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     b24:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     b29:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     b30:	44 8b 72 12          	mov    0x12(%rdx),%r14d
     b34:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     b3b:	44 8b 62 0c          	mov    0xc(%rdx),%r12d
     b3f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b46:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     b4d:	44 8b 5a 06          	mov    0x6(%rdx),%r11d
     b51:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     b55:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     b5b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     b62:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     b67:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     b6c:	44 8b 72 15          	mov    0x15(%rdx),%r14d
     b70:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     b77:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     b7e:	44 8b 62 0f          	mov    0xf(%rdx),%r12d
     b82:	44 8b 0a             	mov    (%rdx),%r9d
     b85:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b8c:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     b91:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     b95:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     b9c:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     ba1:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     ba7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bae:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     bb3:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     bb9:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     bbf:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     bc4:	44 8b 5a 09          	mov    0x9(%rdx),%r11d
     bc8:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     bcd:	44 8b 4a 03          	mov    0x3(%rdx),%r9d
     bd1:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     bd8:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     bdd:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
     be4:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     beb:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     bf0:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     bf4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bfb:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     c00:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     c06:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
     c0b:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     c0f:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     c15:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     c1b:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     c22:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     c28:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     c2f:	4d 8d 48 48          	lea    0x48(%r8),%r9
     c33:	49 83 c0 20          	add    $0x20,%r8
     c37:	48 83 c2 60          	add    $0x60,%rdx
     c3b:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     c3f:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
     c43:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     c49:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     c4f:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
     c55:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
     c59:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     c5e:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
     c64:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     c69:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     c6d:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     c73:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     c78:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
     c7e:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
     c83:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
     c88:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
     c8d:	4c 39 c9             	cmp    %r9,%rcx
     c90:	0f 83 62 fc ff ff    	jae    8f8 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f8>
     c96:	4d 8d 48 08          	lea    0x8(%r8),%r9
     c9a:	4c 39 c9             	cmp    %r9,%rcx
     c9d:	0f 82 2d 01 00 00    	jb     dd0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xdd0>
     ca3:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     ca7:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # caf <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcaf>
     cae:	00 
     caf:	48 01 fa             	add    %rdi,%rdx
     cb2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     cb8:	48 8b 1a             	mov    (%rdx),%rbx
     cbb:	4c 8b 42 08          	mov    0x8(%rdx),%r8
     cbf:	48 83 c2 18          	add    $0x18,%rdx
     cc3:	4c 8b 6a f8          	mov    -0x8(%rdx),%r13
     cc7:	49 89 da             	mov    %rbx,%r10
     cca:	4d 89 c6             	mov    %r8,%r14
     ccd:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     cd4:	45 89 ef             	mov    %r13d,%r15d
     cd7:	49 c1 ee 20          	shr    $0x20,%r14
     cdb:	46 0f b6 1c 10       	movzbl (%rax,%r10,1),%r11d
     ce0:	49 89 da             	mov    %rbx,%r10
     ce3:	48 c1 eb 30          	shr    $0x30,%rbx
     ce7:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     cee:	41 c1 e7 08          	shl    $0x8,%r15d
     cf2:	49 89 dc             	mov    %rbx,%r12
     cf5:	44 89 c3             	mov    %r8d,%ebx
     cf8:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     cfd:	c1 e3 10             	shl    $0x10,%ebx
     d00:	49 c1 ea 18          	shr    $0x18,%r10
     d04:	44 09 e3             	or     %r12d,%ebx
     d07:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     d0d:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     d14:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     d1a:	46 0f b6 14 10       	movzbl (%rax,%r10,1),%r10d
     d1f:	44 0f b6 24 18       	movzbl (%rax,%rbx,1),%r12d
     d24:	44 89 c3             	mov    %r8d,%ebx
     d27:	49 c1 e8 38          	shr    $0x38,%r8
     d2b:	45 09 f8             	or     %r15d,%r8d
     d2e:	4d 89 ef             	mov    %r13,%r15
     d31:	49 c1 ed 28          	shr    $0x28,%r13
     d35:	49 c1 ef 10          	shr    $0x10,%r15
     d39:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     d40:	46 0f b6 2c 28       	movzbl (%rax,%r13,1),%r13d
     d45:	c1 eb 08             	shr    $0x8,%ebx
     d48:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     d4f:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     d54:	0f b6 1c 18          	movzbl (%rax,%rbx,1),%ebx
     d58:	46 0f b6 3c 38       	movzbl (%rax,%r15,1),%r15d
     d5d:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
     d63:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     d6a:	4d 89 c8             	mov    %r9,%r8
     d6d:	49 83 c1 08          	add    $0x8,%r9
     d71:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     d77:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
     d7e:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     d85:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     d89:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     d8f:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
     d96:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     d9a:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     da0:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     da5:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     da9:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     daf:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     db4:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     db9:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     dbd:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
     dc2:	c5 fa 7f 4a e8       	vmovdqu %xmm1,-0x18(%rdx)
     dc7:	4c 39 c9             	cmp    %r9,%rcx
     dca:	0f 83 e8 fe ff ff    	jae    cb8 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcb8>
     dd0:	49 39 c8             	cmp    %rcx,%r8
     dd3:	0f 83 e7 01 00 00    	jae    fc0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfc0>
     dd9:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     ddd:	4e 8d 14 0f          	lea    (%rdi,%r9,1),%r10
     de1:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
     de6:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     deb:	c1 e2 08             	shl    $0x8,%edx
     dee:	41 c1 e3 10          	shl    $0x10,%r11d
     df2:	44 09 da             	or     %r11d,%edx
     df5:	45 0f b6 1a          	movzbl (%r10),%r11d
     df9:	44 09 da             	or     %r11d,%edx
     dfc:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
     e00:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
     e04:	41 8b 13             	mov    (%r11),%edx
     e07:	45 0f b7 1b          	movzwl (%r11),%r11d
     e0b:	c1 ea 10             	shr    $0x10,%edx
     e0e:	66 45 89 1a          	mov    %r11w,(%r10)
     e12:	41 88 52 02          	mov    %dl,0x2(%r10)
     e16:	49 8d 50 01          	lea    0x1(%r8),%rdx
     e1a:	48 39 ca             	cmp    %rcx,%rdx
     e1d:	0f 83 9d 01 00 00    	jae    fc0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfc0>
     e23:	4e 8d 54 0f 03       	lea    0x3(%rdi,%r9,1),%r10
     e28:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
     e2d:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e32:	c1 e2 08             	shl    $0x8,%edx
     e35:	41 c1 e3 10          	shl    $0x10,%r11d
     e39:	44 09 da             	or     %r11d,%edx
     e3c:	45 0f b6 1a          	movzbl (%r10),%r11d
     e40:	44 09 da             	or     %r11d,%edx
     e43:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
     e47:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
     e4b:	41 8b 13             	mov    (%r11),%edx
     e4e:	45 0f b7 1b          	movzwl (%r11),%r11d
     e52:	c1 ea 10             	shr    $0x10,%edx
     e55:	66 45 89 1a          	mov    %r11w,(%r10)
     e59:	41 88 52 02          	mov    %dl,0x2(%r10)
     e5d:	49 8d 50 02          	lea    0x2(%r8),%rdx
     e61:	48 39 ca             	cmp    %rcx,%rdx
     e64:	0f 83 56 01 00 00    	jae    fc0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfc0>
     e6a:	4e 8d 54 0f 06       	lea    0x6(%rdi,%r9,1),%r10
     e6f:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
     e74:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e79:	c1 e2 08             	shl    $0x8,%edx
     e7c:	41 c1 e3 10          	shl    $0x10,%r11d
     e80:	44 09 da             	or     %r11d,%edx
     e83:	45 0f b6 1a          	movzbl (%r10),%r11d
     e87:	44 09 da             	or     %r11d,%edx
     e8a:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
     e8e:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
     e92:	41 8b 13             	mov    (%r11),%edx
     e95:	45 0f b7 1b          	movzwl (%r11),%r11d
     e99:	c1 ea 10             	shr    $0x10,%edx
     e9c:	66 45 89 1a          	mov    %r11w,(%r10)
     ea0:	41 88 52 02          	mov    %dl,0x2(%r10)
     ea4:	49 8d 50 03          	lea    0x3(%r8),%rdx
     ea8:	48 39 ca             	cmp    %rcx,%rdx
     eab:	0f 83 0f 01 00 00    	jae    fc0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfc0>
     eb1:	4e 8d 54 0f 09       	lea    0x9(%rdi,%r9,1),%r10
     eb6:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
     ebb:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     ec0:	c1 e2 10             	shl    $0x10,%edx
     ec3:	41 c1 e3 08          	shl    $0x8,%r11d
     ec7:	44 09 da             	or     %r11d,%edx
     eca:	45 0f b6 1a          	movzbl (%r10),%r11d
     ece:	44 09 da             	or     %r11d,%edx
     ed1:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
     ed5:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
     ed9:	41 8b 13             	mov    (%r11),%edx
     edc:	45 0f b7 1b          	movzwl (%r11),%r11d
     ee0:	c1 ea 10             	shr    $0x10,%edx
     ee3:	66 45 89 1a          	mov    %r11w,(%r10)
     ee7:	41 88 52 02          	mov    %dl,0x2(%r10)
     eeb:	49 8d 50 04          	lea    0x4(%r8),%rdx
     eef:	48 39 ca             	cmp    %rcx,%rdx
     ef2:	0f 83 c8 00 00 00    	jae    fc0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfc0>
     ef8:	4e 8d 54 0f 0c       	lea    0xc(%rdi,%r9,1),%r10
     efd:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
     f02:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     f07:	c1 e2 10             	shl    $0x10,%edx
     f0a:	41 c1 e3 08          	shl    $0x8,%r11d
     f0e:	44 09 da             	or     %r11d,%edx
     f11:	45 0f b6 1a          	movzbl (%r10),%r11d
     f15:	44 09 da             	or     %r11d,%edx
     f18:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
     f1c:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
     f20:	41 8b 13             	mov    (%r11),%edx
     f23:	45 0f b7 1b          	movzwl (%r11),%r11d
     f27:	c1 ea 10             	shr    $0x10,%edx
     f2a:	66 45 89 1a          	mov    %r11w,(%r10)
     f2e:	41 88 52 02          	mov    %dl,0x2(%r10)
     f32:	49 8d 50 05          	lea    0x5(%r8),%rdx
     f36:	48 39 ca             	cmp    %rcx,%rdx
     f39:	0f 83 81 00 00 00    	jae    fc0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfc0>
     f3f:	4e 8d 54 0f 0f       	lea    0xf(%rdi,%r9,1),%r10
     f44:	49 83 c0 06          	add    $0x6,%r8
     f48:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
     f4d:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     f52:	c1 e2 10             	shl    $0x10,%edx
     f55:	41 c1 e3 08          	shl    $0x8,%r11d
     f59:	44 09 da             	or     %r11d,%edx
     f5c:	45 0f b6 1a          	movzbl (%r10),%r11d
     f60:	44 09 da             	or     %r11d,%edx
     f63:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
     f67:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
     f6b:	41 8b 13             	mov    (%r11),%edx
     f6e:	45 0f b7 1b          	movzwl (%r11),%r11d
     f72:	c1 ea 10             	shr    $0x10,%edx
     f75:	66 45 89 1a          	mov    %r11w,(%r10)
     f79:	41 88 52 02          	mov    %dl,0x2(%r10)
     f7d:	49 39 c8             	cmp    %rcx,%r8
     f80:	73 3e                	jae    fc0 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfc0>
     f82:	4a 8d 4c 0f 12       	lea    0x12(%rdi,%r9,1),%rcx
     f87:	0f b6 51 01          	movzbl 0x1(%rcx),%edx
     f8b:	0f b6 79 02          	movzbl 0x2(%rcx),%edi
     f8f:	c1 e2 08             	shl    $0x8,%edx
     f92:	c1 e7 10             	shl    $0x10,%edi
     f95:	09 fa                	or     %edi,%edx
     f97:	0f b6 39             	movzbl (%rcx),%edi
     f9a:	09 fa                	or     %edi,%edx
     f9c:	0f b6 04 10          	movzbl (%rax,%rdx,1),%eax
     fa0:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
     fa4:	8b 02                	mov    (%rdx),%eax
     fa6:	0f b7 12             	movzwl (%rdx),%edx
     fa9:	c1 e8 10             	shr    $0x10,%eax
     fac:	66 89 11             	mov    %dx,(%rcx)
     faf:	88 41 02             	mov    %al,0x2(%rcx)
     fb2:	c5 f8 77             	vzeroupper
     fb5:	5b                   	pop    %rbx
     fb6:	41 5c                	pop    %r12
     fb8:	41 5d                	pop    %r13
     fba:	41 5e                	pop    %r14
     fbc:	41 5f                	pop    %r15
     fbe:	5d                   	pop    %rbp
     fbf:	c3                   	ret
     fc0:	c5 f8 77             	vzeroupper
     fc3:	5b                   	pop    %rbx
     fc4:	41 5c                	pop    %r12
     fc6:	41 5d                	pop    %r13
     fc8:	41 5e                	pop    %r14
     fca:	41 5f                	pop    %r15
     fcc:	5d                   	pop    %rbp
     fcd:	c3                   	ret
     fce:	66 90                	xchg   %ax,%ax
     fd0:	49 89 c8             	mov    %rcx,%r8
     fd3:	e9 be fc ff ff       	jmp    c96 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc96>
     fd8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     fdf:	00 
     fe0:	c3                   	ret
     fe1:	49 8d 51 28          	lea    0x28(%r9),%rdx
     fe5:	4d 89 c8             	mov    %r9,%r8
     fe8:	e9 e5 f8 ff ff       	jmp    8d2 <jshc_channel::avx2_chain_sparsehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8d2>
     fed:	0f 1f 00             	nopl   (%rax)

0000000000000ff0 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     ff0:	f3 0f 1e fa          	endbr64
     ff4:	4d 85 c0             	test   %r8,%r8
     ff7:	0f 84 b3 10 00 00    	je     20b0 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c0>
     ffd:	55                   	push   %rbp
     ffe:	48 89 f8             	mov    %rdi,%rax
    1001:	48 89 e5             	mov    %rsp,%rbp
    1004:	41 57                	push   %r15
    1006:	41 56                	push   %r14
    1008:	41 55                	push   %r13
    100a:	41 54                	push   %r12
    100c:	49 89 cc             	mov    %rcx,%r12
    100f:	4b 8d 0c 40          	lea    (%r8,%r8,2),%rcx
    1013:	53                   	push   %rbx
    1014:	48 89 d3             	mov    %rdx,%rbx
    1017:	ba 00 04 00 00       	mov    $0x400,%edx
    101c:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    1020:	48 39 d1             	cmp    %rdx,%rcx
    1023:	48 0f 47 ca          	cmova  %rdx,%rcx
    1027:	31 d2                	xor    %edx,%edx
    1029:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1030:	0f 18 04 13          	prefetchnta (%rbx,%rdx,1)
    1034:	48 83 c2 40          	add    $0x40,%rdx
    1038:	48 39 ca             	cmp    %rcx,%rdx
    103b:	72 f3                	jb     1030 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
    103d:	49 89 d9             	mov    %rbx,%r9
    1040:	4c 89 e7             	mov    %r12,%rdi
    1043:	31 c9                	xor    %ecx,%ecx
    1045:	eb 53                	jmp    109a <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
    1047:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    104e:	00 00 
    1050:	41 0f b6 51 01       	movzbl 0x1(%r9),%edx
    1055:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
    105a:	48 ff c1             	inc    %rcx
    105d:	48 83 c7 03          	add    $0x3,%rdi
    1061:	49 83 c1 03          	add    $0x3,%r9
    1065:	41 c1 e2 10          	shl    $0x10,%r10d
    1069:	c1 e2 08             	shl    $0x8,%edx
    106c:	44 09 d2             	or     %r10d,%edx
    106f:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
    1074:	44 09 d2             	or     %r10d,%edx
    1077:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    107b:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    107f:	41 8b 12             	mov    (%r10),%edx
    1082:	45 0f b7 12          	movzwl (%r10),%r10d
    1086:	c1 ea 10             	shr    $0x10,%edx
    1089:	66 44 89 57 fd       	mov    %r10w,-0x3(%rdi)
    108e:	88 57 ff             	mov    %dl,-0x1(%rdi)
    1091:	49 39 c8             	cmp    %rcx,%r8
    1094:	0f 84 0e 10 00 00    	je     20a8 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10b8>
    109a:	40 f6 c7 3f          	test   $0x3f,%dil
    109e:	75 b0                	jne    1050 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    10a0:	48 8d 51 48          	lea    0x48(%rcx),%rdx
    10a4:	49 39 d0             	cmp    %rdx,%r8
    10a7:	0f 82 04 10 00 00    	jb     20b1 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c1>
    10ad:	48 8d 14 49          	lea    (%rcx,%rcx,2),%rdx
    10b1:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 10b9 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc9>
    10b8:	00 
    10b9:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 10c1 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd1>
    10c0:	00 
    10c1:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    10c6:	49 8d 3c 14          	lea    (%r12,%rdx,1),%rdi
    10ca:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    10cf:	48 8d 94 13 00 04 00 	lea    0x400(%rbx,%rdx,1),%rdx
    10d6:	00 
    10d7:	eb 0a                	jmp    10e3 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
    10d9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    10e0:	4c 89 c9             	mov    %r9,%rcx
    10e3:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    10ea:	4d 39 c8             	cmp    %r9,%r8
    10ed:	72 15                	jb     1104 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
    10ef:	0f 18 02             	prefetchnta (%rdx)
    10f2:	0f 18 42 40          	prefetchnta 0x40(%rdx)
    10f6:	0f 18 82 80 00 00 00 	prefetchnta 0x80(%rdx)
    10fd:	0f 18 82 bf 00 00 00 	prefetchnta 0xbf(%rdx)
    1104:	4c 8d 89 b2 00 00 00 	lea    0xb2(%rcx),%r9
    110b:	4d 39 c8             	cmp    %r9,%r8
    110e:	72 4c                	jb     115c <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x16c>
    1110:	44 8b 8a 80 fd ff ff 	mov    -0x280(%rdx),%r9d
    1117:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    111e:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1123:	44 8b 8a b0 fd ff ff 	mov    -0x250(%rdx),%r9d
    112a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1131:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1136:	44 8b 8a e0 fd ff ff 	mov    -0x220(%rdx),%r9d
    113d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1144:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1149:	44 8b 8a 10 fe ff ff 	mov    -0x1f0(%rdx),%r9d
    1150:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1157:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    115c:	44 8b 8a 00 fc ff ff 	mov    -0x400(%rdx),%r9d
    1163:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    116a:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    116f:	44 8b 8a 03 fc ff ff 	mov    -0x3fd(%rdx),%r9d
    1176:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    117d:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
    1183:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1188:	44 8b 8a 06 fc ff ff 	mov    -0x3fa(%rdx),%r9d
    118f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1196:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
    119d:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    11a2:	44 8b 8a 09 fc ff ff 	mov    -0x3f7(%rdx),%r9d
    11a9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11b0:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    11b5:	44 8b 8a 0c fc ff ff 	mov    -0x3f4(%rdx),%r9d
    11bc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11c3:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    11c8:	44 8b 8a 0f fc ff ff 	mov    -0x3f1(%rdx),%r9d
    11cf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11d6:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    11dc:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    11e1:	44 8b 8a 12 fc ff ff 	mov    -0x3ee(%rdx),%r9d
    11e8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11ef:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    11f6:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    11fb:	44 8b 8a 15 fc ff ff 	mov    -0x3eb(%rdx),%r9d
    1202:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1209:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    120f:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1214:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    121b:	44 8b 8a 18 fc ff ff 	mov    -0x3e8(%rdx),%r9d
    1222:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1229:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    122d:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1233:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1238:	44 8b 8a 1b fc ff ff 	mov    -0x3e5(%rdx),%r9d
    123f:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1246:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    124d:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1252:	44 8b 8a 1e fc ff ff 	mov    -0x3e2(%rdx),%r9d
    1259:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    125d:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    1263:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    126a:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    126f:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1274:	44 8b 8a 21 fc ff ff 	mov    -0x3df(%rdx),%r9d
    127b:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
    1280:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1287:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    128c:	44 8b 8a 24 fc ff ff 	mov    -0x3dc(%rdx),%r9d
    1293:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
    1299:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12a0:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    12a5:	44 8b 8a 27 fc ff ff 	mov    -0x3d9(%rdx),%r9d
    12ac:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
    12b3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12ba:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    12c0:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    12c5:	44 8b 8a 2a fc ff ff 	mov    -0x3d6(%rdx),%r9d
    12cc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12d3:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    12da:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    12df:	44 8b 8a 2d fc ff ff 	mov    -0x3d3(%rdx),%r9d
    12e6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    12ed:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    12f3:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    12f8:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    12ff:	44 8b 8a 30 fc ff ff 	mov    -0x3d0(%rdx),%r9d
    1306:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    130d:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1311:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1317:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    131c:	44 8b 8a 33 fc ff ff 	mov    -0x3cd(%rdx),%r9d
    1323:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    132a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1331:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1336:	44 8b 8a 36 fc ff ff 	mov    -0x3ca(%rdx),%r9d
    133d:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    1341:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    1347:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    134e:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1353:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1358:	44 8b 8a 39 fc ff ff 	mov    -0x3c7(%rdx),%r9d
    135f:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    1364:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    1368:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    136e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1375:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    137b:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1380:	44 8b 8a 3c fc ff ff 	mov    -0x3c4(%rdx),%r9d
    1387:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    138e:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1393:	44 8b 8a 3f fc ff ff 	mov    -0x3c1(%rdx),%r9d
    139a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13a1:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    13a6:	44 8b 8a 42 fc ff ff 	mov    -0x3be(%rdx),%r9d
    13ad:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13b4:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    13b9:	44 8b 8a 45 fc ff ff 	mov    -0x3bb(%rdx),%r9d
    13c0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    13c7:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    13cc:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    13d2:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    13d8:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    13de:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    13e5:	44 8b 8a 48 fc ff ff 	mov    -0x3b8(%rdx),%r9d
    13ec:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    13f3:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    13fa:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1401:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1406:	44 8b 8a 4b fc ff ff 	mov    -0x3b5(%rdx),%r9d
    140d:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1411:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1417:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    141e:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
    1424:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1429:	44 8b 8a 4e fc ff ff 	mov    -0x3b2(%rdx),%r9d
    1430:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1437:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    143e:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
    1445:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    144a:	44 8b 8a 51 fc ff ff 	mov    -0x3af(%rdx),%r9d
    1451:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    1455:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    145b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1462:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1467:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    146c:	44 8b 8a 54 fc ff ff 	mov    -0x3ac(%rdx),%r9d
    1473:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1478:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    147c:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1482:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1489:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    148f:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1494:	44 8b 8a 57 fc ff ff 	mov    -0x3a9(%rdx),%r9d
    149b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14a2:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    14a8:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    14ad:	44 8b 8a 5a fc ff ff 	mov    -0x3a6(%rdx),%r9d
    14b4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14bb:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    14c2:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    14c7:	44 8b 8a 5d fc ff ff 	mov    -0x3a3(%rdx),%r9d
    14ce:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14d5:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    14db:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    14e0:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    14e7:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    14eb:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    14f1:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    14f8:	44 8b 8a 60 fc ff ff 	mov    -0x3a0(%rdx),%r9d
    14ff:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1506:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    150a:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    150f:	44 8b 8a 63 fc ff ff 	mov    -0x39d(%rdx),%r9d
    1516:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    151c:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    1521:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1528:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
    152e:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    1533:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1538:	44 8b 8a 66 fc ff ff 	mov    -0x39a(%rdx),%r9d
    153f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1546:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
    154d:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1552:	44 8b 8a 69 fc ff ff 	mov    -0x397(%rdx),%r9d
    1559:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1560:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1565:	44 8b 8a 6c fc ff ff 	mov    -0x394(%rdx),%r9d
    156c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1573:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1578:	44 8b 8a 6f fc ff ff 	mov    -0x391(%rdx),%r9d
    157f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1586:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    158c:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1591:	44 8b 8a 72 fc ff ff 	mov    -0x38e(%rdx),%r9d
    1598:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    159f:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    15a6:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    15ab:	44 8b 8a 75 fc ff ff 	mov    -0x38b(%rdx),%r9d
    15b2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15b9:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    15bf:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    15c4:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    15cb:	44 8b 8a 78 fc ff ff 	mov    -0x388(%rdx),%r9d
    15d2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15d9:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    15dd:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    15e3:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    15e8:	44 8b 8a 7b fc ff ff 	mov    -0x385(%rdx),%r9d
    15ef:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    15f6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15fd:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1602:	44 8b 8a 7e fc ff ff 	mov    -0x382(%rdx),%r9d
    1609:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    160d:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    1613:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    161a:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    161f:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1624:	44 8b 8a 81 fc ff ff 	mov    -0x37f(%rdx),%r9d
    162b:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    1630:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1637:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    163c:	44 8b 8a 84 fc ff ff 	mov    -0x37c(%rdx),%r9d
    1643:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1649:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1650:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1655:	44 8b 8a 87 fc ff ff 	mov    -0x379(%rdx),%r9d
    165c:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    1663:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    166a:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1670:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1675:	44 8b 8a 8a fc ff ff 	mov    -0x376(%rdx),%r9d
    167c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1683:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    168a:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    168f:	44 8b 8a 8d fc ff ff 	mov    -0x373(%rdx),%r9d
    1696:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    169d:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    16a3:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    16a8:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    16af:	44 8b 8a 90 fc ff ff 	mov    -0x370(%rdx),%r9d
    16b6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16bd:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    16c1:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    16c7:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    16cc:	44 8b 8a 93 fc ff ff 	mov    -0x36d(%rdx),%r9d
    16d3:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    16da:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16e1:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    16e6:	44 8b 8a 96 fc ff ff 	mov    -0x36a(%rdx),%r9d
    16ed:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    16f1:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    16f7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16fe:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1703:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1708:	44 8b 8a 99 fc ff ff 	mov    -0x367(%rdx),%r9d
    170f:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1714:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    171b:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1720:	44 8b 8a 9c fc ff ff 	mov    -0x364(%rdx),%r9d
    1727:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    172e:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1733:	44 8b 8a 9f fc ff ff 	mov    -0x361(%rdx),%r9d
    173a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1741:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1746:	44 8b 8a a2 fc ff ff 	mov    -0x35e(%rdx),%r9d
    174d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1754:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1759:	44 8b 8a a5 fc ff ff 	mov    -0x35b(%rdx),%r9d
    1760:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1767:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    176c:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1772:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1778:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    177e:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    1785:	44 8b 8a a8 fc ff ff 	mov    -0x358(%rdx),%r9d
    178c:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    1793:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    179a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17a1:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    17a6:	44 8b 8a ab fc ff ff 	mov    -0x355(%rdx),%r9d
    17ad:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    17b2:	c4 21 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm10
    17b8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17bf:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    17c4:	44 8b 8a ae fc ff ff 	mov    -0x352(%rdx),%r9d
    17cb:	c4 63 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm10,%xmm10
    17d2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17d9:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    17de:	44 8b 8a b1 fc ff ff 	mov    -0x34f(%rdx),%r9d
    17e5:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    17ea:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    17f0:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    17f6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17fd:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1802:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1807:	44 8b 8a b4 fc ff ff 	mov    -0x34c(%rdx),%r9d
    180e:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1813:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    181a:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1821:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1828:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    182d:	44 8b 8a b7 fc ff ff 	mov    -0x349(%rdx),%r9d
    1834:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    183b:	c4 21 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm10
    1841:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1846:	44 8b 8a ba fc ff ff 	mov    -0x346(%rdx),%r9d
    184d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1854:	c4 23 29 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm10,%xmm10
    185b:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1860:	44 8b 8a bd fc ff ff 	mov    -0x343(%rdx),%r9d
    1867:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    186e:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1874:	48 81 c7 c0 00 00 00 	add    $0xc0,%rdi
    187b:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1880:	c4 23 21 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm11,%xmm11
    1887:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    188b:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1890:	c4 21 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm11
    1896:	c4 63 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm11,%xmm11
    189d:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    18a2:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    18a7:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    18ad:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    18b3:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    18b8:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    18be:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    18c4:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    18c9:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    18ce:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    18d3:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    18d8:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    18de:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    18e4:	c5 7d e7 8f 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdi)
    18eb:	ff 
    18ec:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    18f0:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    18f4:	c5 fd e7 b7 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdi)
    18fb:	ff 
    18fc:	c5 fd e7 6f 80       	vmovntdq %ymm5,-0x80(%rdi)
    1901:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1905:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    1909:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    190f:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1915:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    191b:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1921:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    1926:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    192a:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    1930:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    1936:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    193c:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    1942:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1948:	c5 fd e7 6f a0       	vmovntdq %ymm5,-0x60(%rdi)
    194d:	c5 fd e7 47 c0       	vmovntdq %ymm0,-0x40(%rdi)
    1952:	c5 fd e7 4f e0       	vmovntdq %ymm1,-0x20(%rdi)
    1957:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    195e:	4d 39 d0             	cmp    %r10,%r8
    1961:	0f 83 79 f7 ff ff    	jae    10e0 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    1967:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    196c:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1971:	48 8d 51 68          	lea    0x68(%rcx),%rdx
    1975:	0f ae f8             	sfence
    1978:	49 39 d0             	cmp    %rdx,%r8
    197b:	0f 82 97 03 00 00    	jb     1d18 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd28>
    1981:	4b 8d 0c 49          	lea    (%r9,%r9,2),%rcx
    1985:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 198d <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x99d>
    198c:	00 
    198d:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1995 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x9a5>
    1994:	00 
    1995:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    199a:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    199f:	48 8d 14 0b          	lea    (%rbx,%rcx,1),%rdx
    19a3:	4c 01 e1             	add    %r12,%rcx
    19a6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    19ad:	00 00 00 
    19b0:	8b 7a 48             	mov    0x48(%rdx),%edi
    19b3:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    19b9:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    19be:	8b 7a 4b             	mov    0x4b(%rdx),%edi
    19c1:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    19c7:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    19cd:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    19d2:	8b 7a 4e             	mov    0x4e(%rdx),%edi
    19d5:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    19db:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    19e2:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    19e7:	8b 7a 51             	mov    0x51(%rdx),%edi
    19ea:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    19f0:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    19f4:	8b 7a 54             	mov    0x54(%rdx),%edi
    19f7:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    19fd:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    1a02:	8b 7a 57             	mov    0x57(%rdx),%edi
    1a05:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1a0b:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1a11:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    1a16:	8b 7a 5a             	mov    0x5a(%rdx),%edi
    1a19:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1a1f:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1a26:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    1a2b:	8b 7a 5d             	mov    0x5d(%rdx),%edi
    1a2e:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1a34:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1a3a:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    1a3e:	c4 e3 71 22 0c be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm1,%xmm1
    1a45:	8b 7a 30             	mov    0x30(%rdx),%edi
    1a48:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1a4e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1a52:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1a58:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    1a5d:	8b 7a 33             	mov    0x33(%rdx),%edi
    1a60:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1a67:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1a6d:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    1a72:	8b 7a 36             	mov    0x36(%rdx),%edi
    1a75:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    1a79:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    1a7f:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1a85:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1a8a:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    1a8f:	8b 7a 39             	mov    0x39(%rdx),%edi
    1a92:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1a97:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1a9d:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    1aa1:	8b 7a 3c             	mov    0x3c(%rdx),%edi
    1aa4:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1aaa:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1ab0:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    1ab5:	8b 7a 3f             	mov    0x3f(%rdx),%edi
    1ab8:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    1abf:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1ac5:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1acb:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    1ad0:	8b 7a 42             	mov    0x42(%rdx),%edi
    1ad3:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1ad9:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1ae0:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    1ae5:	8b 7a 45             	mov    0x45(%rdx),%edi
    1ae8:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1aee:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1af4:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    1af8:	c4 e3 69 22 14 be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm2,%xmm2
    1aff:	8b 7a 18             	mov    0x18(%rdx),%edi
    1b02:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b08:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1b0c:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1b12:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    1b17:	8b 7a 1b             	mov    0x1b(%rdx),%edi
    1b1a:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1b21:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b27:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    1b2c:	8b 7a 1e             	mov    0x1e(%rdx),%edi
    1b2f:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1b33:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1b39:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b3f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1b44:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    1b49:	8b 7a 21             	mov    0x21(%rdx),%edi
    1b4c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1b51:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    1b55:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1b5b:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b61:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    1b65:	8b 7a 24             	mov    0x24(%rdx),%edi
    1b68:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b6e:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    1b73:	8b 7a 27             	mov    0x27(%rdx),%edi
    1b76:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b7c:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    1b81:	8b 7a 2a             	mov    0x2a(%rdx),%edi
    1b84:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b8a:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    1b8f:	8b 7a 2d             	mov    0x2d(%rdx),%edi
    1b92:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1b98:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    1b9c:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1ba2:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1ba8:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1bae:	c4 e3 49 22 34 be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm6,%xmm6
    1bb5:	8b 3a                	mov    (%rdx),%edi
    1bb7:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    1bbe:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1bc5:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1bcb:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    1bd0:	8b 7a 03             	mov    0x3(%rdx),%edi
    1bd3:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    1bd7:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    1bdd:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1be3:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    1be8:	8b 7a 06             	mov    0x6(%rdx),%edi
    1beb:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    1bf2:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1bf8:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    1bfd:	8b 7a 09             	mov    0x9(%rdx),%edi
    1c00:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1c04:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1c0a:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1c10:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1c16:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1c1b:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    1c1f:	8b 7a 0c             	mov    0xc(%rdx),%edi
    1c22:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1c27:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1c2e:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1c32:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1c38:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1c3e:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1c44:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    1c49:	8b 7a 0f             	mov    0xf(%rdx),%edi
    1c4c:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1c52:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1c58:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    1c5e:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    1c63:	8b 7a 12             	mov    0x12(%rdx),%edi
    1c66:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1c6c:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    1c73:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    1c78:	8b 7a 15             	mov    0x15(%rdx),%edi
    1c7b:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1c81:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    1c87:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    1c8b:	c4 e3 41 22 3c be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm7,%xmm7
    1c92:	49 8d 79 48          	lea    0x48(%r9),%rdi
    1c96:	49 83 c1 20          	add    $0x20,%r9
    1c9a:	48 83 c2 60          	add    $0x60,%rdx
    1c9e:	48 83 c1 60          	add    $0x60,%rcx
    1ca2:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    1ca6:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    1cac:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    1cb3:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    1cb7:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    1cbb:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1cc1:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    1cc7:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    1ccd:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1cd1:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1cd6:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    1cdc:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1ce1:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1ce5:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1ceb:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1cf0:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    1cf6:	c5 fe 7f 51 a0       	vmovdqu %ymm2,-0x60(%rcx)
    1cfb:	c5 fe 7f 49 c0       	vmovdqu %ymm1,-0x40(%rcx)
    1d00:	c5 fe 7f 41 e0       	vmovdqu %ymm0,-0x20(%rcx)
    1d05:	49 39 f8             	cmp    %rdi,%r8
    1d08:	0f 83 a2 fc ff ff    	jae    19b0 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x9c0>
    1d0e:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1d13:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1d18:	4d 8d 59 08          	lea    0x8(%r9),%r11
    1d1c:	4d 39 d8             	cmp    %r11,%r8
    1d1f:	0f 82 4d 01 00 00    	jb     1e72 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe82>
    1d25:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1d2a:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    1d2e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1d36 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd46>
    1d35:	00 
    1d36:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    1d3b:	4a 8d 3c 13          	lea    (%rbx,%r10,1),%rdi
    1d3f:	4d 01 e2             	add    %r12,%r10
    1d42:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1d48:	4c 8b 27             	mov    (%rdi),%r12
    1d4b:	48 8b 57 08          	mov    0x8(%rdi),%rdx
    1d4f:	49 83 c2 18          	add    $0x18,%r10
    1d53:	48 83 c7 18          	add    $0x18,%rdi
    1d57:	48 8b 4f f8          	mov    -0x8(%rdi),%rcx
    1d5b:	4d 89 e1             	mov    %r12,%r9
    1d5e:	4d 89 e5             	mov    %r12,%r13
    1d61:	49 89 d6             	mov    %rdx,%r14
    1d64:	49 c1 ed 30          	shr    $0x30,%r13
    1d68:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d6f:	41 89 cf             	mov    %ecx,%r15d
    1d72:	49 c1 ee 20          	shr    $0x20,%r14
    1d76:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1d7b:	4d 89 e1             	mov    %r12,%r9
    1d7e:	41 89 d4             	mov    %edx,%r12d
    1d81:	41 c1 e7 08          	shl    $0x8,%r15d
    1d85:	41 c1 e4 10          	shl    $0x10,%r12d
    1d89:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1d90:	49 c1 e9 18          	shr    $0x18,%r9
    1d94:	45 09 ec             	or     %r13d,%r12d
    1d97:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
    1d9c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1da3:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    1da8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1daf:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1db4:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
    1db9:	41 89 d4             	mov    %edx,%r12d
    1dbc:	48 c1 ea 38          	shr    $0x38,%rdx
    1dc0:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1dc6:	41 09 d7             	or     %edx,%r15d
    1dc9:	41 c1 ec 08          	shr    $0x8,%r12d
    1dcd:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1dd4:	4d 89 d9             	mov    %r11,%r9
    1dd7:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1dde:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
    1de3:	49 83 c3 08          	add    $0x8,%r11
    1de7:	42 0f b6 14 38       	movzbl (%rax,%r15,1),%edx
    1dec:	49 89 cf             	mov    %rcx,%r15
    1def:	48 c1 e9 28          	shr    $0x28,%rcx
    1df3:	49 c1 ef 10          	shr    $0x10,%r15
    1df7:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    1dfb:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1e02:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
    1e09:	46 0f b6 3c 38       	movzbl (%rax,%r15,1),%r15d
    1e0e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1e14:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1e1b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1e1f:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1e25:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1e2c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1e30:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1e36:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1e3b:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1e3f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1e45:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1e4a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1e4f:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1e53:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1e59:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    1e5f:	4d 39 d8             	cmp    %r11,%r8
    1e62:	0f 83 e0 fe ff ff    	jae    1d48 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd58>
    1e68:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1e6d:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1e72:	4d 39 c1             	cmp    %r8,%r9
    1e75:	0f 83 15 02 00 00    	jae    2090 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10a0>
    1e7b:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1e7f:	4c 8d 14 13          	lea    (%rbx,%rdx,1),%r10
    1e83:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    1e88:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1e8d:	45 0f b6 12          	movzbl (%r10),%r10d
    1e91:	c1 e1 08             	shl    $0x8,%ecx
    1e94:	41 c1 e3 10          	shl    $0x10,%r11d
    1e98:	44 09 d9             	or     %r11d,%ecx
    1e9b:	44 09 d1             	or     %r10d,%ecx
    1e9e:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    1ea2:	4c 8d 14 8e          	lea    (%rsi,%rcx,4),%r10
    1ea6:	41 8b 0a             	mov    (%r10),%ecx
    1ea9:	45 0f b7 12          	movzwl (%r10),%r10d
    1ead:	c1 e9 10             	shr    $0x10,%ecx
    1eb0:	66 45 89 14 14       	mov    %r10w,(%r12,%rdx,1)
    1eb5:	41 88 4c 14 02       	mov    %cl,0x2(%r12,%rdx,1)
    1eba:	49 8d 49 01          	lea    0x1(%r9),%rcx
    1ebe:	4c 39 c1             	cmp    %r8,%rcx
    1ec1:	0f 83 c9 01 00 00    	jae    2090 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10a0>
    1ec7:	4c 8d 54 13 03       	lea    0x3(%rbx,%rdx,1),%r10
    1ecc:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    1ed1:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1ed6:	45 0f b6 12          	movzbl (%r10),%r10d
    1eda:	41 c1 e3 10          	shl    $0x10,%r11d
    1ede:	c1 e1 08             	shl    $0x8,%ecx
    1ee1:	44 09 d9             	or     %r11d,%ecx
    1ee4:	44 09 d1             	or     %r10d,%ecx
    1ee7:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    1eeb:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1eef:	44 8b 11             	mov    (%rcx),%r10d
    1ef2:	44 0f b7 19          	movzwl (%rcx),%r11d
    1ef6:	49 8d 49 02          	lea    0x2(%r9),%rcx
    1efa:	44 89 d7             	mov    %r10d,%edi
    1efd:	66 45 89 5c 14 03    	mov    %r11w,0x3(%r12,%rdx,1)
    1f03:	c1 ef 10             	shr    $0x10,%edi
    1f06:	41 88 7c 14 05       	mov    %dil,0x5(%r12,%rdx,1)
    1f0b:	4c 39 c1             	cmp    %r8,%rcx
    1f0e:	0f 83 7c 01 00 00    	jae    2090 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10a0>
    1f14:	4c 8d 54 13 06       	lea    0x6(%rbx,%rdx,1),%r10
    1f19:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    1f1e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1f23:	45 0f b6 12          	movzbl (%r10),%r10d
    1f27:	41 c1 e3 10          	shl    $0x10,%r11d
    1f2b:	c1 e1 08             	shl    $0x8,%ecx
    1f2e:	44 09 d9             	or     %r11d,%ecx
    1f31:	44 09 d1             	or     %r10d,%ecx
    1f34:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    1f38:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1f3c:	44 8b 11             	mov    (%rcx),%r10d
    1f3f:	44 0f b7 19          	movzwl (%rcx),%r11d
    1f43:	49 8d 49 03          	lea    0x3(%r9),%rcx
    1f47:	44 89 d7             	mov    %r10d,%edi
    1f4a:	66 45 89 5c 14 06    	mov    %r11w,0x6(%r12,%rdx,1)
    1f50:	c1 ef 10             	shr    $0x10,%edi
    1f53:	41 88 7c 14 08       	mov    %dil,0x8(%r12,%rdx,1)
    1f58:	4c 39 c1             	cmp    %r8,%rcx
    1f5b:	0f 83 2f 01 00 00    	jae    2090 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10a0>
    1f61:	4c 8d 54 13 09       	lea    0x9(%rbx,%rdx,1),%r10
    1f66:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    1f6b:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1f70:	45 0f b6 12          	movzbl (%r10),%r10d
    1f74:	41 c1 e3 08          	shl    $0x8,%r11d
    1f78:	c1 e1 10             	shl    $0x10,%ecx
    1f7b:	44 09 d9             	or     %r11d,%ecx
    1f7e:	44 09 d1             	or     %r10d,%ecx
    1f81:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    1f85:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1f89:	44 8b 11             	mov    (%rcx),%r10d
    1f8c:	44 0f b7 19          	movzwl (%rcx),%r11d
    1f90:	49 8d 49 04          	lea    0x4(%r9),%rcx
    1f94:	44 89 d7             	mov    %r10d,%edi
    1f97:	66 45 89 5c 14 09    	mov    %r11w,0x9(%r12,%rdx,1)
    1f9d:	c1 ef 10             	shr    $0x10,%edi
    1fa0:	41 88 7c 14 0b       	mov    %dil,0xb(%r12,%rdx,1)
    1fa5:	4c 39 c1             	cmp    %r8,%rcx
    1fa8:	0f 83 e2 00 00 00    	jae    2090 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10a0>
    1fae:	4c 8d 54 13 0c       	lea    0xc(%rbx,%rdx,1),%r10
    1fb3:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    1fb8:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1fbd:	45 0f b6 12          	movzbl (%r10),%r10d
    1fc1:	41 c1 e3 08          	shl    $0x8,%r11d
    1fc5:	c1 e1 10             	shl    $0x10,%ecx
    1fc8:	44 09 d9             	or     %r11d,%ecx
    1fcb:	44 09 d1             	or     %r10d,%ecx
    1fce:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    1fd2:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    1fd6:	44 8b 11             	mov    (%rcx),%r10d
    1fd9:	44 0f b7 19          	movzwl (%rcx),%r11d
    1fdd:	49 8d 49 05          	lea    0x5(%r9),%rcx
    1fe1:	44 89 d7             	mov    %r10d,%edi
    1fe4:	66 45 89 5c 14 0c    	mov    %r11w,0xc(%r12,%rdx,1)
    1fea:	c1 ef 10             	shr    $0x10,%edi
    1fed:	41 88 7c 14 0e       	mov    %dil,0xe(%r12,%rdx,1)
    1ff2:	4c 39 c1             	cmp    %r8,%rcx
    1ff5:	0f 83 95 00 00 00    	jae    2090 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10a0>
    1ffb:	4c 8d 54 13 0f       	lea    0xf(%rbx,%rdx,1),%r10
    2000:	49 83 c1 06          	add    $0x6,%r9
    2004:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    2009:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    200e:	45 0f b6 12          	movzbl (%r10),%r10d
    2012:	41 c1 e3 08          	shl    $0x8,%r11d
    2016:	c1 e1 10             	shl    $0x10,%ecx
    2019:	44 09 d9             	or     %r11d,%ecx
    201c:	44 09 d1             	or     %r10d,%ecx
    201f:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    2023:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    2027:	44 8b 11             	mov    (%rcx),%r10d
    202a:	44 0f b7 19          	movzwl (%rcx),%r11d
    202e:	44 89 d7             	mov    %r10d,%edi
    2031:	66 45 89 5c 14 0f    	mov    %r11w,0xf(%r12,%rdx,1)
    2037:	c1 ef 10             	shr    $0x10,%edi
    203a:	41 88 7c 14 11       	mov    %dil,0x11(%r12,%rdx,1)
    203f:	4d 39 c1             	cmp    %r8,%r9
    2042:	73 4c                	jae    2090 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10a0>
    2044:	48 8d 4c 13 12       	lea    0x12(%rbx,%rdx,1),%rcx
    2049:	4d 8d 44 14 12       	lea    0x12(%r12,%rdx,1),%r8
    204e:	0f b6 79 02          	movzbl 0x2(%rcx),%edi
    2052:	0f b6 51 01          	movzbl 0x1(%rcx),%edx
    2056:	0f b6 09             	movzbl (%rcx),%ecx
    2059:	c1 e2 08             	shl    $0x8,%edx
    205c:	c1 e7 10             	shl    $0x10,%edi
    205f:	09 fa                	or     %edi,%edx
    2061:	09 ca                	or     %ecx,%edx
    2063:	0f b6 04 10          	movzbl (%rax,%rdx,1),%eax
    2067:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    206b:	8b 02                	mov    (%rdx),%eax
    206d:	0f b7 12             	movzwl (%rdx),%edx
    2070:	c1 e8 10             	shr    $0x10,%eax
    2073:	66 41 89 10          	mov    %dx,(%r8)
    2077:	41 88 40 02          	mov    %al,0x2(%r8)
    207b:	c5 f8 77             	vzeroupper
    207e:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2082:	5b                   	pop    %rbx
    2083:	41 5c                	pop    %r12
    2085:	41 5d                	pop    %r13
    2087:	41 5e                	pop    %r14
    2089:	41 5f                	pop    %r15
    208b:	5d                   	pop    %rbp
    208c:	c3                   	ret
    208d:	0f 1f 00             	nopl   (%rax)
    2090:	c5 f8 77             	vzeroupper
    2093:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2097:	5b                   	pop    %rbx
    2098:	41 5c                	pop    %r12
    209a:	41 5d                	pop    %r13
    209c:	41 5e                	pop    %r14
    209e:	41 5f                	pop    %r15
    20a0:	5d                   	pop    %rbp
    20a1:	c3                   	ret
    20a2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    20a8:	4d 89 c1             	mov    %r8,%r9
    20ab:	e9 68 fc ff ff       	jmp    1d18 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd28>
    20b0:	c3                   	ret
    20b1:	48 8d 51 28          	lea    0x28(%rcx),%rdx
    20b5:	49 89 c9             	mov    %rcx,%r9
    20b8:	e9 bb f8 ff ff       	jmp    1978 <jshc_channel::avx2_chain_sparsehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x988>
