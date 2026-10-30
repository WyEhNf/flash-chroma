
artifacts/skylake-splitpack-linux-build-v1/CMakeFiles/jshc_skylake_splitpack.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 23 0e 00 00    	je     e30 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe30>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
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
      89:	0f 84 91 0d 00 00    	je     e20 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe20>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 8f 0d 00 00    	jb     e31 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe31>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 f9 6f 05 00 00 00 	vmovdqa 0x0(%rip),%xmm0        # ae <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # b6 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # be <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbe>
      bd:	00 
      be:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # c6 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc6>
      c5:	00 
      c6:	48 01 d0             	add    %rdx,%rax
      c9:	c5 7d 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm12        # d1 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd1>
      d0:	00 
      d1:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # d9 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd9>
      d8:	00 
      d9:	eb 08                	jmp    e3 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe3>
      db:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      e0:	4d 89 c1             	mov    %r8,%r9
      e3:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      ea:	4c 39 c1             	cmp    %r8,%rcx
      ed:	72 1c                	jb     10b <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10b>
      ef:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      f6:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      fd:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     104:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     10b:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     10f:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     114:	48 05 c0 00 00 00    	add    $0xc0,%rax
     11a:	c4 e3 71 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm1,%xmm1
     120:	c4 e2 69 00 d0       	vpshufb %xmm0,%xmm2,%xmm2
     125:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     12a:	c4 c1 79 7e d0       	vmovd  %xmm2,%r8d
     12f:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     135:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     13a:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     140:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     145:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     14a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     14f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     154:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     15a:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     160:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     165:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     16a:	c4 c3 79 16 d0 01    	vpextrd $0x1,%xmm2,%r8d
     170:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     176:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     17c:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     182:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     187:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     18c:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     193:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     19a:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     1a0:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     1a4:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     1a9:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     1b0:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     1b7:	c5 39 6c c2          	vpunpcklqdq %xmm2,%xmm8,%xmm8
     1bb:	c5 fa 6f 90 58 ff ff 	vmovdqu -0xa8(%rax),%xmm2
     1c2:	ff 
     1c3:	c4 63 3d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm8,%ymm8
     1c9:	c5 fa 7e 88 68 ff ff 	vmovq  -0x98(%rax),%xmm1
     1d0:	ff 
     1d1:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
     1d6:	c4 e3 71 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm1,%xmm1
     1dc:	c4 e2 69 00 d0       	vpshufb %xmm0,%xmm2,%xmm2
     1e1:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
     1e6:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     1eb:	c4 c1 79 7e d0       	vmovd  %xmm2,%r8d
     1f0:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     1f6:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     1fb:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     201:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     206:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     20b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     210:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     215:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     21b:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     221:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     226:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     22b:	c4 c3 79 16 d0 01    	vpextrd $0x1,%xmm2,%r8d
     231:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     237:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     23d:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     243:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     248:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     24d:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     254:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     25b:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
     260:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     264:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     26a:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
     271:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     278:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     27c:	c5 fa 6f 98 70 ff ff 	vmovdqu -0x90(%rax),%xmm3
     283:	ff 
     284:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
     28a:	c5 fa 7e 48 80       	vmovq  -0x80(%rax),%xmm1
     28f:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     294:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
     29a:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
     29f:	c4 e2 15 36 d2       	vpermd %ymm2,%ymm13,%ymm2
     2a4:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     2a9:	c4 c1 79 7e d8       	vmovd  %xmm3,%r8d
     2ae:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     2b4:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     2b9:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     2bf:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     2c4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     2c9:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     2ce:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     2d3:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     2d9:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     2df:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2e4:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     2e9:	c4 c3 79 16 d8 01    	vpextrd $0x1,%xmm3,%r8d
     2ef:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
     2f5:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     2fb:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     301:	c4 63 3d 02 c2 c0    	vpblendd $0xc0,%ymm2,%ymm8,%ymm8
     307:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     30c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     311:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     318:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     31f:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
     325:	c5 f1 6c cb          	vpunpcklqdq %xmm3,%xmm1,%xmm1
     329:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
     32e:	c4 23 29 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm10,%xmm10
     335:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
     33c:	c5 29 6c d3          	vpunpcklqdq %xmm3,%xmm10,%xmm10
     340:	c5 fa 6f 58 88       	vmovdqu -0x78(%rax),%xmm3
     345:	c4 63 2d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm10,%ymm10
     34b:	c5 fa 7e 48 98       	vmovq  -0x68(%rax),%xmm1
     350:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
     355:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
     35b:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
     360:	c4 42 1d 36 d2       	vpermd %ymm10,%ymm12,%ymm10
     365:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     36a:	c4 c1 79 7e d8       	vmovd  %xmm3,%r8d
     36f:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     375:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     37a:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     380:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     385:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     38a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     38f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     394:	c4 c3 79 16 d8 01    	vpextrd $0x1,%xmm3,%r8d
     39a:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
     3a0:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     3a6:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     3ac:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     3b1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     3b6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3bb:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     3c0:	c4 c3 6d 0c d2 f0    	vblendps $0xf0,%ymm10,%ymm2,%ymm2
     3c6:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     3cc:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     3d2:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     3d8:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     3df:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     3e6:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     3ed:	c5 f1 6c cb          	vpunpcklqdq %xmm3,%xmm1,%xmm1
     3f1:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
     3f6:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
     3fd:	c5 c1 6c fb          	vpunpcklqdq %xmm3,%xmm7,%xmm7
     401:	c5 fa 6f 58 a0       	vmovdqu -0x60(%rax),%xmm3
     406:	c4 e3 45 38 f9 01    	vinserti128 $0x1,%xmm1,%ymm7,%ymm7
     40c:	c5 fa 7e 48 b0       	vmovq  -0x50(%rax),%xmm1
     411:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     416:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
     41c:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
     421:	c4 e2 25 36 ff       	vpermd %ymm7,%ymm11,%ymm7
     426:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     42b:	c4 c1 79 7e d8       	vmovd  %xmm3,%r8d
     430:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     436:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     43b:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     441:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     446:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     44b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     450:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     455:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     45b:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     461:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     466:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     46b:	c4 c3 79 16 d8 01    	vpextrd $0x1,%xmm3,%r8d
     471:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
     477:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     47d:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     483:	c4 c3 45 02 fa 03    	vpblendd $0x3,%ymm10,%ymm7,%ymm7
     489:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     48e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     493:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     49a:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     4a1:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     4a7:	c5 f1 6c cb          	vpunpcklqdq %xmm3,%xmm1,%xmm1
     4ab:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
     4b0:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     4b7:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
     4be:	c5 c9 6c f3          	vpunpcklqdq %xmm3,%xmm6,%xmm6
     4c2:	c5 fa 6f 58 b8       	vmovdqu -0x48(%rax),%xmm3
     4c7:	c4 e3 4d 38 f1 01    	vinserti128 $0x1,%xmm1,%ymm6,%ymm6
     4cd:	c5 fa 7e 48 c8       	vmovq  -0x38(%rax),%xmm1
     4d2:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
     4d7:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
     4dd:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
     4e2:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     4e7:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     4ec:	c4 c1 79 7e d8       	vmovd  %xmm3,%r8d
     4f1:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     4f7:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     4fc:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     501:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     506:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     50c:	c4 c3 79 16 d8 01    	vpextrd $0x1,%xmm3,%r8d
     512:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
     518:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     51d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     522:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     527:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     52c:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     532:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     538:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     53d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     542:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     548:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
     54e:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     553:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     55a:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
     561:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     568:	c5 e1 6c d9          	vpunpcklqdq %xmm1,%xmm3,%xmm3
     56c:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     572:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     579:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
     57e:	c5 7a 6f 48 d0       	vmovdqu -0x30(%rax),%xmm9
     583:	c4 e3 75 38 cb 01    	vinserti128 $0x1,%xmm3,%ymm1,%ymm1
     589:	c5 fa 7e 58 e0       	vmovq  -0x20(%rax),%xmm3
     58e:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     593:	c4 c3 61 0f d9 0c    	vpalignr $0xc,%xmm9,%xmm3,%xmm3
     599:	c4 62 31 00 c8       	vpshufb %xmm0,%xmm9,%xmm9
     59e:	c4 e2 15 36 c9       	vpermd %ymm1,%ymm13,%ymm1
     5a3:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
     5a8:	c4 41 79 7e c8       	vmovd  %xmm9,%r8d
     5ad:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
     5b3:	c4 c1 79 7e dc       	vmovd  %xmm3,%r12d
     5b8:	c4 c3 79 16 de 02    	vpextrd $0x2,%xmm3,%r14d
     5be:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5c3:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     5c8:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     5cd:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     5d2:	c4 c3 79 16 dc 01    	vpextrd $0x1,%xmm3,%r12d
     5d8:	c4 c3 79 16 de 03    	vpextrd $0x3,%xmm3,%r14d
     5de:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5e3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     5e8:	c4 43 79 16 c8 01    	vpextrd $0x1,%xmm9,%r8d
     5ee:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
     5f4:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
     5fa:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
     600:	c4 e3 4d 02 f1 c0    	vpblendd $0xc0,%ymm1,%ymm6,%ymm6
     606:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     60b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     610:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
     617:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
     61e:	c5 79 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm14
     623:	c4 c1 61 6c d9       	vpunpcklqdq %xmm9,%xmm3,%xmm3
     628:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     62e:	c4 23 09 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm14,%xmm14
     635:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     63c:	c4 41 31 6c ce       	vpunpcklqdq %xmm14,%xmm9,%xmm9
     641:	c5 7a 6f 70 e8       	vmovdqu -0x18(%rax),%xmm14
     646:	c4 63 35 38 cb 01    	vinserti128 $0x1,%xmm3,%ymm9,%ymm9
     64c:	c5 fa 7e 58 f8       	vmovq  -0x8(%rax),%xmm3
     651:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
     656:	c4 c3 61 0f de 0c    	vpalignr $0xc,%xmm14,%xmm3,%xmm3
     65c:	c4 62 09 00 f0       	vpshufb %xmm0,%xmm14,%xmm14
     661:	c4 42 1d 36 c9       	vpermd %ymm9,%ymm12,%ymm9
     666:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
     66b:	c4 41 79 7e f0       	vmovd  %xmm14,%r8d
     670:	c4 43 79 16 f3 02    	vpextrd $0x2,%xmm14,%r11d
     676:	c4 c1 79 7e dc       	vmovd  %xmm3,%r12d
     67b:	c4 c3 79 16 de 02    	vpextrd $0x2,%xmm3,%r14d
     681:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     686:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     68b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     690:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     695:	c4 c3 79 16 dc 01    	vpextrd $0x1,%xmm3,%r12d
     69b:	c4 c3 79 16 de 03    	vpextrd $0x3,%xmm3,%r14d
     6a1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     6a6:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     6ab:	c4 43 79 16 f0 01    	vpextrd $0x1,%xmm14,%r8d
     6b1:	c4 43 79 16 f3 03    	vpextrd $0x3,%xmm14,%r11d
     6b7:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     6bd:	c4 21 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm14
     6c3:	c4 c3 75 0c c9 f0    	vblendps $0xf0,%ymm9,%ymm1,%ymm1
     6c9:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     6ce:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     6d3:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     6da:	c4 23 09 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm14,%xmm14
     6e1:	c5 79 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm15
     6e6:	c5 09 6c f3          	vpunpcklqdq %xmm3,%xmm14,%xmm14
     6ea:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     6f0:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     6f7:	c4 23 01 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm15,%xmm15
     6fe:	c4 a3 61 22 1c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm3,%xmm3
     705:	c5 7d e7 80 40 ff ff 	vmovntdq %ymm8,-0xc0(%rax)
     70c:	ff 
     70d:	c5 fd e7 90 60 ff ff 	vmovntdq %ymm2,-0xa0(%rax)
     714:	ff 
     715:	c5 fd e7 78 80       	vmovntdq %ymm7,-0x80(%rax)
     71a:	c5 fd e7 70 a0       	vmovntdq %ymm6,-0x60(%rax)
     71f:	c5 fd e7 48 c0       	vmovntdq %ymm1,-0x40(%rax)
     724:	4d 8d 41 40          	lea    0x40(%r9),%r8
     728:	c4 c1 61 6c df       	vpunpcklqdq %xmm15,%xmm3,%xmm3
     72d:	c4 c3 65 38 de 01    	vinserti128 $0x1,%xmm14,%ymm3,%ymm3
     733:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
     738:	c4 e2 25 36 db       	vpermd %ymm3,%ymm11,%ymm3
     73d:	c4 c3 65 02 d9 03    	vpblendd $0x3,%ymm9,%ymm3,%ymm3
     743:	c5 fd e7 58 e0       	vmovntdq %ymm3,-0x20(%rax)
     748:	4c 39 d1             	cmp    %r10,%rcx
     74b:	0f 83 8f f9 ff ff    	jae    e0 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe0>
     751:	0f ae f8             	sfence
     754:	49 8d 41 68          	lea    0x68(%r9),%rax
     758:	48 39 c1             	cmp    %rax,%rcx
     75b:	0f 82 83 03 00 00    	jb     ae4 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae4>
     761:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     765:	c5 f9 6f 05 00 00 00 	vmovdqa 0x0(%rip),%xmm0        # 76d <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x76d>
     76c:	00 
     76d:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 775 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x775>
     774:	00 
     775:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 77d <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x77d>
     77c:	00 
     77d:	48 01 d0             	add    %rdx,%rax
     780:	c5 7a 6f 50 48       	vmovdqu 0x48(%rax),%xmm10
     785:	c5 fa 7e 70 58       	vmovq  0x58(%rax),%xmm6
     78a:	48 83 c0 60          	add    $0x60,%rax
     78e:	c5 7a 6f 48 d0       	vmovdqu -0x30(%rax),%xmm9
     793:	c5 fa 7e 48 e0       	vmovq  -0x20(%rax),%xmm1
     798:	c4 c3 49 0f f2 0c    	vpalignr $0xc,%xmm10,%xmm6,%xmm6
     79e:	c4 62 29 00 d0       	vpshufb %xmm0,%xmm10,%xmm10
     7a3:	c5 fa 6f 78 a0       	vmovdqu -0x60(%rax),%xmm7
     7a8:	c5 7a 6f 40 b8       	vmovdqu -0x48(%rax),%xmm8
     7ad:	c4 e2 49 00 f0       	vpshufb %xmm0,%xmm6,%xmm6
     7b2:	c4 41 79 7e d1       	vmovd  %xmm10,%r9d
     7b7:	c4 43 79 16 d3 02    	vpextrd $0x2,%xmm10,%r11d
     7bd:	c5 fa 7e 58 b0       	vmovq  -0x50(%rax),%xmm3
     7c2:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     7c7:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     7cd:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     7d2:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     7d7:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     7dc:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     7e1:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
     7e7:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
     7ed:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     7f2:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     7f7:	c4 43 79 16 d1 01    	vpextrd $0x1,%xmm10,%r9d
     7fd:	c4 43 79 16 d3 03    	vpextrd $0x3,%xmm10,%r11d
     803:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
     809:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     80f:	c4 c3 71 0f c9 0c    	vpalignr $0xc,%xmm9,%xmm1,%xmm1
     815:	c4 62 31 00 c8       	vpshufb %xmm0,%xmm9,%xmm9
     81a:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     81f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     824:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     829:	c4 e3 61 0f df 0c    	vpalignr $0xc,%xmm7,%xmm3,%xmm3
     82f:	c4 a3 49 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm6,%xmm6
     836:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     83d:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     843:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     848:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     84d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     852:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     858:	c5 29 6c d6          	vpunpcklqdq %xmm6,%xmm10,%xmm10
     85c:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     862:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     867:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     86d:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     874:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
     87a:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     87f:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
     884:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
     88b:	c4 41 79 7e c9       	vmovd  %xmm9,%r9d
     890:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     895:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
     89b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     8a0:	c4 43 79 16 c9 01    	vpextrd $0x1,%xmm9,%r9d
     8a6:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     8ab:	c4 e2 41 00 f8       	vpshufb %xmm0,%xmm7,%xmm7
     8b0:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     8b5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     8ba:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
     8bf:	c5 fa 7e 50 c8       	vmovq  -0x38(%rax),%xmm2
     8c4:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     8ca:	c4 c3 4d 38 f2 01    	vinserti128 $0x1,%xmm10,%ymm6,%ymm6
     8d0:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     8d6:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     8db:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
     8e0:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     8e7:	c4 c3 69 0f d0 0c    	vpalignr $0xc,%xmm8,%xmm2,%xmm2
     8ed:	c4 62 39 00 c0       	vpshufb %xmm0,%xmm8,%xmm8
     8f2:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     8f9:	c4 e2 69 00 d0       	vpshufb %xmm0,%xmm2,%xmm2
     8fe:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     905:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     90a:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     910:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
     916:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     91a:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     920:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     925:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     92b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     930:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     936:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     93b:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
     941:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     948:	c4 41 79 7e c1       	vmovd  %xmm8,%r9d
     94d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     952:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
     957:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     95c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     961:	c4 43 79 16 c1 01    	vpextrd $0x1,%xmm8,%r9d
     967:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     96d:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
     973:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     978:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     97d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     982:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     988:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     98f:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
     996:	c4 c3 79 16 de 02    	vpextrd $0x2,%xmm3,%r14d
     99c:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     9a1:	c4 c1 79 7e dc       	vmovd  %xmm3,%r12d
     9a6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     9ab:	c4 c3 79 16 de 03    	vpextrd $0x3,%xmm3,%r14d
     9b1:	c5 39 6c c2          	vpunpcklqdq %xmm2,%xmm8,%xmm8
     9b5:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     9bb:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     9c0:	c4 c3 79 16 dc 01    	vpextrd $0x1,%xmm3,%r12d
     9c6:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     9cd:	c4 c3 79 16 fb 02    	vpextrd $0x2,%xmm7,%r11d
     9d3:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     9d8:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     9dd:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     9e4:	c4 c1 79 7e f9       	vmovd  %xmm7,%r9d
     9e9:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     9ee:	c4 c3 79 16 fb 03    	vpextrd $0x3,%xmm7,%r11d
     9f4:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     9f9:	c4 c3 79 16 f9 01    	vpextrd $0x1,%xmm7,%r9d
     9ff:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a04:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
     a09:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a0e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a13:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     a18:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     a1c:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     a22:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     a28:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
     a2e:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     a34:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
     a39:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     a3e:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     a45:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     a4c:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
     a51:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
     a58:	c5 79 6f d2          	vmovdqa %xmm2,%xmm10
     a5c:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     a62:	c5 c1 6c fb          	vpunpcklqdq %xmm3,%xmm7,%xmm7
     a66:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     a6c:	c4 c3 69 0f d2 08    	vpalignr $0x8,%xmm10,%xmm2,%xmm2
     a72:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
     a78:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
     a7f:	4d 8d 48 48          	lea    0x48(%r8),%r9
     a83:	c5 fe 7f 50 c0       	vmovdqu %ymm2,-0x40(%rax)
     a88:	49 83 c0 20          	add    $0x20,%r8
     a8c:	c4 c1 61 6c d8       	vpunpcklqdq %xmm8,%xmm3,%xmm3
     a91:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
     a95:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     a9b:	c4 e3 65 38 df 01    	vinserti128 $0x1,%xmm7,%ymm3,%ymm3
     aa1:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
     aa7:	c4 c1 71 6c c8       	vpunpcklqdq %xmm8,%xmm1,%xmm1
     aac:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
     ab1:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
     ab7:	c4 e2 55 36 db       	vpermd %ymm3,%ymm5,%ymm3
     abc:	c5 fe 7f 48 e0       	vmovdqu %ymm1,-0x20(%rax)
     ac1:	c5 f9 6f fb          	vmovdqa %xmm3,%xmm7
     ac5:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     acb:	c4 c1 61 6c da       	vpunpcklqdq %xmm10,%xmm3,%xmm3
     ad0:	c4 e3 45 38 db 01    	vinserti128 $0x1,%xmm3,%ymm7,%ymm3
     ad6:	c5 fe 7f 58 a0       	vmovdqu %ymm3,-0x60(%rax)
     adb:	4c 39 c9             	cmp    %r9,%rcx
     ade:	0f 83 9c fc ff ff    	jae    780 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x780>
     ae4:	4d 8d 48 08          	lea    0x8(%r8),%r9
     ae8:	4c 39 c9             	cmp    %r9,%rcx
     aeb:	0f 82 27 01 00 00    	jb     c18 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc18>
     af1:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     af5:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # afd <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xafd>
     afc:	00 
     afd:	48 01 d0             	add    %rdx,%rax
     b00:	48 8b 18             	mov    (%rax),%rbx
     b03:	4c 8b 40 08          	mov    0x8(%rax),%r8
     b07:	48 83 c0 18          	add    $0x18,%rax
     b0b:	4c 8b 68 f8          	mov    -0x8(%rax),%r13
     b0f:	49 89 da             	mov    %rbx,%r10
     b12:	4d 89 c6             	mov    %r8,%r14
     b15:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     b1c:	45 89 ef             	mov    %r13d,%r15d
     b1f:	49 c1 ee 20          	shr    $0x20,%r14
     b23:	46 0f b6 1c 17       	movzbl (%rdi,%r10,1),%r11d
     b28:	49 89 da             	mov    %rbx,%r10
     b2b:	48 c1 eb 30          	shr    $0x30,%rbx
     b2f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b36:	41 c1 e7 08          	shl    $0x8,%r15d
     b3a:	49 89 dc             	mov    %rbx,%r12
     b3d:	44 89 c3             	mov    %r8d,%ebx
     b40:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b45:	c1 e3 10             	shl    $0x10,%ebx
     b48:	49 c1 ea 18          	shr    $0x18,%r10
     b4c:	44 09 e3             	or     %r12d,%ebx
     b4f:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     b55:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     b5c:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     b62:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     b67:	44 0f b6 24 1f       	movzbl (%rdi,%rbx,1),%r12d
     b6c:	44 89 c3             	mov    %r8d,%ebx
     b6f:	49 c1 e8 38          	shr    $0x38,%r8
     b73:	45 09 f8             	or     %r15d,%r8d
     b76:	4d 89 ef             	mov    %r13,%r15
     b79:	49 c1 ed 28          	shr    $0x28,%r13
     b7d:	49 c1 ef 10          	shr    $0x10,%r15
     b81:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     b88:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     b8d:	c1 eb 08             	shr    $0x8,%ebx
     b90:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     b97:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     b9c:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     ba0:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     ba5:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
     bab:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     bb2:	4d 89 c8             	mov    %r9,%r8
     bb5:	49 83 c1 08          	add    $0x8,%r9
     bb9:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     bbf:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
     bc6:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     bcd:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     bd1:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     bd7:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
     bde:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     be2:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     be8:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     bed:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     bf1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     bf7:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     bfc:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     c01:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     c05:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     c0a:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     c0f:	4c 39 c9             	cmp    %r9,%rcx
     c12:	0f 83 e8 fe ff ff    	jae    b00 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb00>
     c18:	49 39 c8             	cmp    %rcx,%r8
     c1b:	0f 83 ef 01 00 00    	jae    e10 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe10>
     c21:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     c25:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     c29:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     c2e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     c33:	c1 e0 08             	shl    $0x8,%eax
     c36:	41 c1 e3 10          	shl    $0x10,%r11d
     c3a:	44 09 d8             	or     %r11d,%eax
     c3d:	45 0f b6 1a          	movzbl (%r10),%r11d
     c41:	44 09 d8             	or     %r11d,%eax
     c44:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     c48:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     c4c:	41 8b 03             	mov    (%r11),%eax
     c4f:	45 0f b7 1b          	movzwl (%r11),%r11d
     c53:	c1 e8 10             	shr    $0x10,%eax
     c56:	66 45 89 1a          	mov    %r11w,(%r10)
     c5a:	41 88 42 02          	mov    %al,0x2(%r10)
     c5e:	49 8d 40 01          	lea    0x1(%r8),%rax
     c62:	48 39 c8             	cmp    %rcx,%rax
     c65:	0f 83 a5 01 00 00    	jae    e10 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe10>
     c6b:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     c70:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     c75:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     c7a:	c1 e0 08             	shl    $0x8,%eax
     c7d:	41 c1 e3 10          	shl    $0x10,%r11d
     c81:	44 09 d8             	or     %r11d,%eax
     c84:	45 0f b6 1a          	movzbl (%r10),%r11d
     c88:	44 09 d8             	or     %r11d,%eax
     c8b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     c8f:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     c93:	41 8b 03             	mov    (%r11),%eax
     c96:	45 0f b7 1b          	movzwl (%r11),%r11d
     c9a:	c1 e8 10             	shr    $0x10,%eax
     c9d:	66 45 89 1a          	mov    %r11w,(%r10)
     ca1:	41 88 42 02          	mov    %al,0x2(%r10)
     ca5:	49 8d 40 02          	lea    0x2(%r8),%rax
     ca9:	48 39 c8             	cmp    %rcx,%rax
     cac:	0f 83 5e 01 00 00    	jae    e10 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe10>
     cb2:	4e 8d 54 0a 06       	lea    0x6(%rdx,%r9,1),%r10
     cb7:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     cbc:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     cc1:	c1 e0 08             	shl    $0x8,%eax
     cc4:	41 c1 e3 10          	shl    $0x10,%r11d
     cc8:	44 09 d8             	or     %r11d,%eax
     ccb:	45 0f b6 1a          	movzbl (%r10),%r11d
     ccf:	44 09 d8             	or     %r11d,%eax
     cd2:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     cd6:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     cda:	41 8b 03             	mov    (%r11),%eax
     cdd:	45 0f b7 1b          	movzwl (%r11),%r11d
     ce1:	c1 e8 10             	shr    $0x10,%eax
     ce4:	66 45 89 1a          	mov    %r11w,(%r10)
     ce8:	41 88 42 02          	mov    %al,0x2(%r10)
     cec:	49 8d 40 03          	lea    0x3(%r8),%rax
     cf0:	48 39 c8             	cmp    %rcx,%rax
     cf3:	0f 83 17 01 00 00    	jae    e10 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe10>
     cf9:	4e 8d 54 0a 09       	lea    0x9(%rdx,%r9,1),%r10
     cfe:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     d03:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     d08:	c1 e0 10             	shl    $0x10,%eax
     d0b:	41 c1 e3 08          	shl    $0x8,%r11d
     d0f:	44 09 d8             	or     %r11d,%eax
     d12:	45 0f b6 1a          	movzbl (%r10),%r11d
     d16:	44 09 d8             	or     %r11d,%eax
     d19:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d1d:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d21:	41 8b 03             	mov    (%r11),%eax
     d24:	45 0f b7 1b          	movzwl (%r11),%r11d
     d28:	c1 e8 10             	shr    $0x10,%eax
     d2b:	66 45 89 1a          	mov    %r11w,(%r10)
     d2f:	41 88 42 02          	mov    %al,0x2(%r10)
     d33:	49 8d 40 04          	lea    0x4(%r8),%rax
     d37:	48 39 c8             	cmp    %rcx,%rax
     d3a:	0f 83 d0 00 00 00    	jae    e10 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe10>
     d40:	4e 8d 54 0a 0c       	lea    0xc(%rdx,%r9,1),%r10
     d45:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     d4a:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     d4f:	c1 e0 10             	shl    $0x10,%eax
     d52:	41 c1 e3 08          	shl    $0x8,%r11d
     d56:	44 09 d8             	or     %r11d,%eax
     d59:	45 0f b6 1a          	movzbl (%r10),%r11d
     d5d:	44 09 d8             	or     %r11d,%eax
     d60:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d64:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d68:	41 8b 03             	mov    (%r11),%eax
     d6b:	45 0f b7 1b          	movzwl (%r11),%r11d
     d6f:	c1 e8 10             	shr    $0x10,%eax
     d72:	66 45 89 1a          	mov    %r11w,(%r10)
     d76:	41 88 42 02          	mov    %al,0x2(%r10)
     d7a:	49 8d 40 05          	lea    0x5(%r8),%rax
     d7e:	48 39 c8             	cmp    %rcx,%rax
     d81:	0f 83 89 00 00 00    	jae    e10 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe10>
     d87:	4e 8d 54 0a 0f       	lea    0xf(%rdx,%r9,1),%r10
     d8c:	49 83 c0 06          	add    $0x6,%r8
     d90:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     d95:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
     d9a:	c1 e0 10             	shl    $0x10,%eax
     d9d:	41 c1 e3 08          	shl    $0x8,%r11d
     da1:	44 09 d8             	or     %r11d,%eax
     da4:	45 0f b6 1a          	movzbl (%r10),%r11d
     da8:	44 09 d8             	or     %r11d,%eax
     dab:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     daf:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     db3:	41 8b 03             	mov    (%r11),%eax
     db6:	45 0f b7 1b          	movzwl (%r11),%r11d
     dba:	c1 e8 10             	shr    $0x10,%eax
     dbd:	66 45 89 1a          	mov    %r11w,(%r10)
     dc1:	41 88 42 02          	mov    %al,0x2(%r10)
     dc5:	49 39 c8             	cmp    %rcx,%r8
     dc8:	73 46                	jae    e10 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe10>
     dca:	4a 8d 54 0a 12       	lea    0x12(%rdx,%r9,1),%rdx
     dcf:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     dd3:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     dd7:	c1 e0 08             	shl    $0x8,%eax
     dda:	c1 e1 10             	shl    $0x10,%ecx
     ddd:	09 c8                	or     %ecx,%eax
     ddf:	0f b6 0a             	movzbl (%rdx),%ecx
     de2:	09 c8                	or     %ecx,%eax
     de4:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     de8:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     dec:	8b 01                	mov    (%rcx),%eax
     dee:	0f b7 09             	movzwl (%rcx),%ecx
     df1:	c1 e8 10             	shr    $0x10,%eax
     df4:	66 89 0a             	mov    %cx,(%rdx)
     df7:	88 42 02             	mov    %al,0x2(%rdx)
     dfa:	c5 f8 77             	vzeroupper
     dfd:	5b                   	pop    %rbx
     dfe:	41 5c                	pop    %r12
     e00:	41 5d                	pop    %r13
     e02:	41 5e                	pop    %r14
     e04:	41 5f                	pop    %r15
     e06:	5d                   	pop    %rbp
     e07:	c3                   	ret
     e08:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     e0f:	00 
     e10:	c5 f8 77             	vzeroupper
     e13:	5b                   	pop    %rbx
     e14:	41 5c                	pop    %r12
     e16:	41 5d                	pop    %r13
     e18:	41 5e                	pop    %r14
     e1a:	41 5f                	pop    %r15
     e1c:	5d                   	pop    %rbp
     e1d:	c3                   	ret
     e1e:	66 90                	xchg   %ax,%ax
     e20:	49 89 c8             	mov    %rcx,%r8
     e23:	e9 bc fc ff ff       	jmp    ae4 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae4>
     e28:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     e2f:	00 
     e30:	c3                   	ret
     e31:	49 8d 41 28          	lea    0x28(%r9),%rax
     e35:	4d 89 c8             	mov    %r9,%r8
     e38:	e9 1b f9 ff ff       	jmp    758 <jshc_channel::avx2_chain_splitpack(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x758>
     e3d:	0f 1f 00             	nopl   (%rax)

0000000000000e40 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     e40:	f3 0f 1e fa          	endbr64
     e44:	4d 85 c0             	test   %r8,%r8
     e47:	0f 84 f3 0e 00 00    	je     1d40 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf00>
     e4d:	55                   	push   %rbp
     e4e:	b8 00 04 00 00       	mov    $0x400,%eax
     e53:	48 89 e5             	mov    %rsp,%rbp
     e56:	41 57                	push   %r15
     e58:	41 56                	push   %r14
     e5a:	41 55                	push   %r13
     e5c:	41 54                	push   %r12
     e5e:	49 89 cc             	mov    %rcx,%r12
     e61:	53                   	push   %rbx
     e62:	48 89 d3             	mov    %rdx,%rbx
     e65:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     e69:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     e6d:	48 39 c2             	cmp    %rax,%rdx
     e70:	48 0f 47 d0          	cmova  %rax,%rdx
     e74:	31 c0                	xor    %eax,%eax
     e76:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     e7d:	00 00 00 
     e80:	0f 18 04 03          	prefetchnta (%rbx,%rax,1)
     e84:	48 83 c0 40          	add    $0x40,%rax
     e88:	48 39 d0             	cmp    %rdx,%rax
     e8b:	72 f3                	jb     e80 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     e8d:	49 89 d9             	mov    %rbx,%r9
     e90:	4c 89 e2             	mov    %r12,%rdx
     e93:	31 c9                	xor    %ecx,%ecx
     e95:	eb 53                	jmp    eea <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
     e97:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
     e9e:	00 00 
     ea0:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     ea5:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     eaa:	48 ff c1             	inc    %rcx
     ead:	48 83 c2 03          	add    $0x3,%rdx
     eb1:	49 83 c1 03          	add    $0x3,%r9
     eb5:	41 c1 e2 10          	shl    $0x10,%r10d
     eb9:	c1 e0 08             	shl    $0x8,%eax
     ebc:	44 09 d0             	or     %r10d,%eax
     ebf:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
     ec4:	44 09 d0             	or     %r10d,%eax
     ec7:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     ecb:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
     ecf:	41 8b 02             	mov    (%r10),%eax
     ed2:	45 0f b7 12          	movzwl (%r10),%r10d
     ed6:	c1 e8 10             	shr    $0x10,%eax
     ed9:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
     ede:	88 42 ff             	mov    %al,-0x1(%rdx)
     ee1:	49 39 c8             	cmp    %rcx,%r8
     ee4:	0f 84 46 0e 00 00    	je     1d30 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xef0>
     eea:	f6 c2 3f             	test   $0x3f,%dl
     eed:	75 b1                	jne    ea0 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     eef:	48 8d 41 48          	lea    0x48(%rcx),%rax
     ef3:	49 39 c0             	cmp    %rax,%r8
     ef6:	0f 82 45 0e 00 00    	jb     1d41 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf01>
     efc:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     f00:	c5 f9 6f 05 00 00 00 	vmovdqa 0x0(%rip),%xmm0        # f08 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc8>
     f07:	00 
     f08:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # f10 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd0>
     f0f:	00 
     f10:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
     f15:	49 8d 14 04          	lea    (%r12,%rax,1),%rdx
     f19:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
     f1e:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # f26 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe6>
     f25:	00 
     f26:	48 8d 84 03 00 04 00 	lea    0x400(%rbx,%rax,1),%rax
     f2d:	00 
     f2e:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # f36 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf6>
     f35:	00 
     f36:	c5 7d 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm12        # f3e <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfe>
     f3d:	00 
     f3e:	c5 7d 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm11        # f46 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x106>
     f45:	00 
     f46:	eb 0b                	jmp    f53 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x113>
     f48:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     f4f:	00 
     f50:	4c 89 c9             	mov    %r9,%rcx
     f53:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
     f5a:	4d 39 c8             	cmp    %r9,%r8
     f5d:	72 15                	jb     f74 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x134>
     f5f:	0f 18 00             	prefetchnta (%rax)
     f62:	0f 18 40 40          	prefetchnta 0x40(%rax)
     f66:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
     f6d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
     f74:	c5 fa 6f 90 00 fc ff 	vmovdqu -0x400(%rax),%xmm2
     f7b:	ff 
     f7c:	c5 fa 7e 88 10 fc ff 	vmovq  -0x3f0(%rax),%xmm1
     f83:	ff 
     f84:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
     f8b:	48 05 c0 00 00 00    	add    $0xc0,%rax
     f91:	c4 e3 71 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm1,%xmm1
     f97:	c4 e2 69 00 d0       	vpshufb %xmm0,%xmm2,%xmm2
     f9c:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
     fa1:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
     fa6:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     fac:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     fb1:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     fb7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     fbc:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     fc1:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     fc6:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     fcb:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     fd1:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     fd7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     fdc:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     fe1:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
     fe7:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     fed:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     ff3:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     ff9:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     ffe:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1003:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    100a:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1011:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    1017:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    101b:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
    1020:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    1027:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
    102e:	c5 39 6c c2          	vpunpcklqdq %xmm2,%xmm8,%xmm8
    1032:	c5 fa 6f 90 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm2
    1039:	ff 
    103a:	c4 63 3d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm8,%ymm8
    1040:	c5 fa 7e 88 68 fb ff 	vmovq  -0x498(%rax),%xmm1
    1047:	ff 
    1048:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
    104d:	c4 e3 71 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm1,%xmm1
    1053:	c4 e2 69 00 d0       	vpshufb %xmm0,%xmm2,%xmm2
    1058:	c4 42 55 36 c0       	vpermd %ymm8,%ymm5,%ymm8
    105d:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
    1062:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
    1067:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    106d:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1072:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1078:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    107d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1082:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1087:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    108c:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1092:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1098:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    109d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    10a2:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
    10a8:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    10ae:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
    10b4:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    10ba:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    10bf:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    10c4:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
    10cb:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    10d2:	c5 f1 6c cb          	vpunpcklqdq %xmm3,%xmm1,%xmm1
    10d6:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
    10db:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    10e1:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
    10e8:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    10ef:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    10f3:	c5 fa 6f 98 70 fb ff 	vmovdqu -0x490(%rax),%xmm3
    10fa:	ff 
    10fb:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
    1101:	c5 fa 7e 88 80 fb ff 	vmovq  -0x480(%rax),%xmm1
    1108:	ff 
    1109:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    110e:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
    1114:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
    1119:	c4 e2 15 36 d2       	vpermd %ymm2,%ymm13,%ymm2
    111e:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
    1123:	c4 c1 79 7e d9       	vmovd  %xmm3,%r9d
    1128:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
    112e:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1133:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1139:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    113e:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1143:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1148:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    114d:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1153:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1159:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    115e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1163:	c4 c3 79 16 d9 01    	vpextrd $0x1,%xmm3,%r9d
    1169:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    116f:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1175:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
    117b:	c4 63 3d 02 c2 c0    	vpblendd $0xc0,%ymm2,%ymm8,%ymm8
    1181:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1186:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    118b:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
    1192:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1199:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    119f:	c5 f1 6c cb          	vpunpcklqdq %xmm3,%xmm1,%xmm1
    11a3:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
    11a8:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    11af:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
    11b6:	c5 29 6c d3          	vpunpcklqdq %xmm3,%xmm10,%xmm10
    11ba:	c5 fa 6f 98 88 fb ff 	vmovdqu -0x478(%rax),%xmm3
    11c1:	ff 
    11c2:	c4 63 2d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm10,%ymm10
    11c8:	c5 fa 7e 88 98 fb ff 	vmovq  -0x468(%rax),%xmm1
    11cf:	ff 
    11d0:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
    11d5:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
    11db:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
    11e0:	c4 42 1d 36 d2       	vpermd %ymm10,%ymm12,%ymm10
    11e5:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
    11ea:	c4 c1 79 7e d9       	vmovd  %xmm3,%r9d
    11ef:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
    11f5:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    11fa:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1200:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1205:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    120a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    120f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1214:	c4 c3 79 16 d9 01    	vpextrd $0x1,%xmm3,%r9d
    121a:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    1220:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1226:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    122c:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1231:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1236:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    123b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1240:	c4 c3 6d 0c d2 f0    	vblendps $0xf0,%ymm10,%ymm2,%ymm2
    1246:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
    124c:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1252:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    1258:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
    125f:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1266:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    126d:	c5 f1 6c cb          	vpunpcklqdq %xmm3,%xmm1,%xmm1
    1271:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
    1276:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
    127d:	c5 c1 6c fb          	vpunpcklqdq %xmm3,%xmm7,%xmm7
    1281:	c5 fa 6f 98 a0 fb ff 	vmovdqu -0x460(%rax),%xmm3
    1288:	ff 
    1289:	c4 e3 45 38 f9 01    	vinserti128 $0x1,%xmm1,%ymm7,%ymm7
    128f:	c5 fa 7e 88 b0 fb ff 	vmovq  -0x450(%rax),%xmm1
    1296:	ff 
    1297:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    129c:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
    12a2:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
    12a7:	c4 e2 25 36 ff       	vpermd %ymm7,%ymm11,%ymm7
    12ac:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
    12b1:	c4 c1 79 7e d9       	vmovd  %xmm3,%r9d
    12b6:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
    12bc:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    12c1:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    12c7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    12cc:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    12d1:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    12d6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    12db:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    12e1:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    12e7:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    12ec:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    12f1:	c4 c3 79 16 d9 01    	vpextrd $0x1,%xmm3,%r9d
    12f7:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    12fd:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
    1303:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
    1309:	c4 c3 45 02 fa 03    	vpblendd $0x3,%ymm10,%ymm7,%ymm7
    130f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1314:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1319:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
    1320:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
    1327:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    132d:	c5 f1 6c cb          	vpunpcklqdq %xmm3,%xmm1,%xmm1
    1331:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
    1336:	c4 a3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm6,%xmm6
    133d:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
    1344:	c5 c9 6c f3          	vpunpcklqdq %xmm3,%xmm6,%xmm6
    1348:	c5 fa 6f 98 b8 fb ff 	vmovdqu -0x448(%rax),%xmm3
    134f:	ff 
    1350:	c4 e3 4d 38 f1 01    	vinserti128 $0x1,%xmm1,%ymm6,%ymm6
    1356:	c5 fa 7e 88 c8 fb ff 	vmovq  -0x438(%rax),%xmm1
    135d:	ff 
    135e:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
    1363:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
    1369:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
    136e:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1373:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
    1378:	c4 c1 79 7e d9       	vmovd  %xmm3,%r9d
    137d:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
    1383:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1388:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    138d:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1392:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1398:	c4 c3 79 16 d9 01    	vpextrd $0x1,%xmm3,%r9d
    139e:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    13a4:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    13a9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    13ae:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    13b3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    13b8:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    13be:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    13c4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    13c9:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    13ce:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    13d4:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
    13da:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    13e0:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    13e7:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
    13ee:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    13f5:	c4 c1 61 6c d9       	vpunpcklqdq %xmm9,%xmm3,%xmm3
    13fa:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    13ff:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1406:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
    140b:	c5 7a 6f 88 d0 fb ff 	vmovdqu -0x430(%rax),%xmm9
    1412:	ff 
    1413:	c4 e3 75 38 cb 01    	vinserti128 $0x1,%xmm3,%ymm1,%ymm1
    1419:	c5 fa 7e 98 e0 fb ff 	vmovq  -0x420(%rax),%xmm3
    1420:	ff 
    1421:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    1426:	c4 c3 61 0f d9 0c    	vpalignr $0xc,%xmm9,%xmm3,%xmm3
    142c:	c4 62 31 00 c8       	vpshufb %xmm0,%xmm9,%xmm9
    1431:	c4 e2 15 36 c9       	vpermd %ymm1,%ymm13,%ymm1
    1436:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
    143b:	c4 41 79 7e c9       	vmovd  %xmm9,%r9d
    1440:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
    1446:	c4 c1 79 7e dc       	vmovd  %xmm3,%r12d
    144b:	c4 c3 79 16 de 02    	vpextrd $0x2,%xmm3,%r14d
    1451:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1456:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    145b:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1460:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1465:	c4 c3 79 16 dc 01    	vpextrd $0x1,%xmm3,%r12d
    146b:	c4 c3 79 16 de 03    	vpextrd $0x3,%xmm3,%r14d
    1471:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1476:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    147b:	c4 43 79 16 c9 01    	vpextrd $0x1,%xmm9,%r9d
    1481:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
    1487:	c4 21 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm14
    148d:	c4 a1 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm3
    1493:	c4 e3 4d 02 f1 c0    	vpblendd $0xc0,%ymm1,%ymm6,%ymm6
    1499:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    149e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    14a3:	c4 23 09 22 34 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm14,%xmm14
    14aa:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
    14b1:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    14b7:	c4 c1 61 6c de       	vpunpcklqdq %xmm14,%xmm3,%xmm3
    14bc:	c5 79 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm14
    14c1:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
    14c8:	c4 23 09 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm14,%xmm14
    14cf:	c4 41 31 6c ce       	vpunpcklqdq %xmm14,%xmm9,%xmm9
    14d4:	c5 7a 6f b0 e8 fb ff 	vmovdqu -0x418(%rax),%xmm14
    14db:	ff 
    14dc:	c4 63 35 38 cb 01    	vinserti128 $0x1,%xmm3,%ymm9,%ymm9
    14e2:	c5 fa 7e 98 f8 fb ff 	vmovq  -0x408(%rax),%xmm3
    14e9:	ff 
    14ea:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
    14ef:	c4 c3 61 0f de 0c    	vpalignr $0xc,%xmm14,%xmm3,%xmm3
    14f5:	c4 62 09 00 f0       	vpshufb %xmm0,%xmm14,%xmm14
    14fa:	c4 42 1d 36 c9       	vpermd %ymm9,%ymm12,%ymm9
    14ff:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
    1504:	c4 41 79 7e f1       	vmovd  %xmm14,%r9d
    1509:	c4 43 79 16 f3 02    	vpextrd $0x2,%xmm14,%r11d
    150f:	c4 c1 79 7e dc       	vmovd  %xmm3,%r12d
    1514:	c4 c3 79 16 de 02    	vpextrd $0x2,%xmm3,%r14d
    151a:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    151f:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1524:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1529:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    152e:	c4 c3 79 16 dc 01    	vpextrd $0x1,%xmm3,%r12d
    1534:	c4 c3 79 16 de 03    	vpextrd $0x3,%xmm3,%r14d
    153a:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    153f:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1544:	c4 43 79 16 f1 01    	vpextrd $0x1,%xmm14,%r9d
    154a:	c4 43 79 16 f3 03    	vpextrd $0x3,%xmm14,%r11d
    1550:	c4 21 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm15
    1556:	c4 21 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm14
    155c:	c4 c3 75 0c c9 f0    	vblendps $0xf0,%ymm9,%ymm1,%ymm1
    1562:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1567:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    156d:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1574:	c4 23 01 22 3c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm15,%xmm15
    157b:	c4 23 09 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm14,%xmm14
    1582:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1587:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
    158e:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    1592:	c4 41 09 6c f7       	vpunpcklqdq %xmm15,%xmm14,%xmm14
    1597:	c5 79 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm15
    159c:	c4 23 01 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm15,%xmm15
    15a3:	c5 7d e7 82 40 ff ff 	vmovntdq %ymm8,-0xc0(%rdx)
    15aa:	ff 
    15ab:	c5 fd e7 92 60 ff ff 	vmovntdq %ymm2,-0xa0(%rdx)
    15b2:	ff 
    15b3:	c5 fd e7 7a 80       	vmovntdq %ymm7,-0x80(%rdx)
    15b8:	c5 fd e7 72 a0       	vmovntdq %ymm6,-0x60(%rdx)
    15bd:	c5 fd e7 4a c0       	vmovntdq %ymm1,-0x40(%rdx)
    15c2:	c4 c1 61 6c df       	vpunpcklqdq %xmm15,%xmm3,%xmm3
    15c7:	c4 c3 65 38 de 01    	vinserti128 $0x1,%xmm14,%ymm3,%ymm3
    15cd:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
    15d2:	c4 e2 25 36 db       	vpermd %ymm3,%ymm11,%ymm3
    15d7:	c4 c3 65 02 d9 03    	vpblendd $0x3,%ymm9,%ymm3,%ymm3
    15dd:	c5 fd e7 5a e0       	vmovntdq %ymm3,-0x20(%rdx)
    15e2:	4d 39 d0             	cmp    %r10,%r8
    15e5:	0f 83 65 f9 ff ff    	jae    f50 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x110>
    15eb:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    15f0:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    15f5:	48 8d 41 68          	lea    0x68(%rcx),%rax
    15f9:	0f ae f8             	sfence
    15fc:	49 39 c0             	cmp    %rax,%r8
    15ff:	0f 82 a1 03 00 00    	jb     19a6 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb66>
    1605:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1609:	c5 f9 6f 05 00 00 00 	vmovdqa 0x0(%rip),%xmm0        # 1611 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7d1>
    1610:	00 
    1611:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1619 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7d9>
    1618:	00 
    1619:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    161e:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    1623:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 162b <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7eb>
    162a:	00 
    162b:	48 8d 04 13          	lea    (%rbx,%rdx,1),%rax
    162f:	4c 01 e2             	add    %r12,%rdx
    1632:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1638:	c5 7a 6f 50 48       	vmovdqu 0x48(%rax),%xmm10
    163d:	c5 fa 7e 70 58       	vmovq  0x58(%rax),%xmm6
    1642:	48 83 c2 60          	add    $0x60,%rdx
    1646:	48 83 c0 60          	add    $0x60,%rax
    164a:	c5 7a 6f 48 d0       	vmovdqu -0x30(%rax),%xmm9
    164f:	c5 fa 7e 48 e0       	vmovq  -0x20(%rax),%xmm1
    1654:	c4 c3 49 0f f2 0c    	vpalignr $0xc,%xmm10,%xmm6,%xmm6
    165a:	c4 62 29 00 d0       	vpshufb %xmm0,%xmm10,%xmm10
    165f:	c5 fa 6f 78 a0       	vmovdqu -0x60(%rax),%xmm7
    1664:	c5 7a 6f 40 b8       	vmovdqu -0x48(%rax),%xmm8
    1669:	c4 e2 49 00 f0       	vpshufb %xmm0,%xmm6,%xmm6
    166e:	c5 79 7e d1          	vmovd  %xmm10,%ecx
    1672:	c4 43 79 16 d3 02    	vpextrd $0x2,%xmm10,%r11d
    1678:	c5 fa 7e 58 b0       	vmovq  -0x50(%rax),%xmm3
    167d:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
    1682:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
    1688:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    168d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1692:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1697:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    169c:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    16a2:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    16a8:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    16ad:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    16b2:	c4 63 79 16 d1 01    	vpextrd $0x1,%xmm10,%ecx
    16b8:	c4 43 79 16 d3 03    	vpextrd $0x3,%xmm10,%r11d
    16be:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    16c4:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
    16ca:	c4 c3 71 0f c9 0c    	vpalignr $0xc,%xmm9,%xmm1,%xmm1
    16d0:	c4 62 31 00 c8       	vpshufb %xmm0,%xmm9,%xmm9
    16d5:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    16d9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    16de:	c4 e2 71 00 c8       	vpshufb %xmm0,%xmm1,%xmm1
    16e3:	c4 e3 61 0f df 0c    	vpalignr $0xc,%xmm7,%xmm3,%xmm3
    16e9:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    16f0:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
    16f7:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    16fd:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
    1703:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1708:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    170d:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1713:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1718:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    171d:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1722:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1728:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    172f:	c5 79 7e c9          	vmovd  %xmm9,%ecx
    1733:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1738:	c4 e2 61 00 d8       	vpshufb %xmm0,%xmm3,%xmm3
    173d:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    1744:	c4 43 79 16 cb 02    	vpextrd $0x2,%xmm9,%r11d
    174a:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    174f:	c4 63 79 16 c9 01    	vpextrd $0x1,%xmm9,%ecx
    1755:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    175a:	c4 43 79 16 cb 03    	vpextrd $0x3,%xmm9,%r11d
    1760:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1764:	c4 e2 41 00 f8       	vpshufb %xmm0,%xmm7,%xmm7
    1769:	c4 c1 49 6c f3       	vpunpcklqdq %xmm11,%xmm6,%xmm6
    176e:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1773:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1778:	c5 fa 7e 50 c8       	vmovq  -0x38(%rax),%xmm2
    177d:	c4 c3 4d 38 f2 01    	vinserti128 $0x1,%xmm10,%ymm6,%ymm6
    1783:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1789:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    178f:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1795:	c4 e2 4d 00 f4       	vpshufb %ymm4,%ymm6,%ymm6
    179a:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    17a1:	c4 c3 69 0f d0 0c    	vpalignr $0xc,%xmm8,%xmm2,%xmm2
    17a7:	c4 62 39 00 c0       	vpshufb %xmm0,%xmm8,%xmm8
    17ac:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    17b3:	c4 e2 69 00 d0       	vpshufb %xmm0,%xmm2,%xmm2
    17b8:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    17bf:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    17c4:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    17ca:	c5 79 7e c1          	vmovd  %xmm8,%ecx
    17ce:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    17d3:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    17d8:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    17dd:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    17e3:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    17e8:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    17ee:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    17f3:	c4 63 79 16 c1 01    	vpextrd $0x1,%xmm8,%ecx
    17f9:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    1800:	c4 43 79 16 c3 02    	vpextrd $0x2,%xmm8,%r11d
    1806:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    180b:	c4 e2 55 36 f6       	vpermd %ymm6,%ymm5,%ymm6
    1810:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1815:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    181a:	c4 43 79 16 c3 03    	vpextrd $0x3,%xmm8,%r11d
    1820:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1825:	c4 21 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm8
    182b:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    182f:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1835:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    183b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1840:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    1847:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    184d:	c4 c1 79 7e dc       	vmovd  %xmm3,%r12d
    1852:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    1857:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    185e:	c4 c3 79 16 de 02    	vpextrd $0x2,%xmm3,%r14d
    1864:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1869:	c4 c3 79 16 dc 01    	vpextrd $0x1,%xmm3,%r12d
    186f:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1876:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    187b:	c5 f9 7e f9          	vmovd  %xmm7,%ecx
    187f:	c4 c3 79 16 de 03    	vpextrd $0x3,%xmm3,%r14d
    1885:	c4 41 39 6c c1       	vpunpcklqdq %xmm9,%xmm8,%xmm8
    188a:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    188f:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1894:	c4 e3 79 16 f9 01    	vpextrd $0x1,%xmm7,%ecx
    189a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    189e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    18a3:	c4 e2 55 36 c9       	vpermd %ymm1,%ymm5,%ymm1
    18a8:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    18af:	c4 c3 79 16 fb 02    	vpextrd $0x2,%xmm7,%r11d
    18b5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    18ba:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    18bf:	c4 c3 79 16 fb 03    	vpextrd $0x3,%xmm7,%r11d
    18c5:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    18ca:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    18cf:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    18d3:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    18d9:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
    18df:	c4 21 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm8
    18e5:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    18eb:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    18f1:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    18f6:	c4 23 39 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm8,%xmm8
    18fd:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    1904:	c4 e2 55 36 d2       	vpermd %ymm2,%ymm5,%ymm2
    1909:	c4 e3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm3,%xmm3
    1910:	c5 79 6f d2          	vmovdqa %xmm2,%xmm10
    1914:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    191a:	c4 c1 41 6c f8       	vpunpcklqdq %xmm8,%xmm7,%xmm7
    191f:	c5 79 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm8
    1924:	c4 c3 69 0f d2 08    	vpalignr $0x8,%xmm10,%xmm2,%xmm2
    192a:	49 8d 49 48          	lea    0x48(%r9),%rcx
    192e:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
    1934:	49 83 c1 20          	add    $0x20,%r9
    1938:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
    193f:	c5 fe 7f 52 c0       	vmovdqu %ymm2,-0x40(%rdx)
    1944:	c4 c1 61 6c d8       	vpunpcklqdq %xmm8,%xmm3,%xmm3
    1949:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
    194d:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1953:	c4 e3 65 38 df 01    	vinserti128 $0x1,%xmm7,%ymm3,%ymm3
    1959:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
    195f:	c4 c1 71 6c c8       	vpunpcklqdq %xmm8,%xmm1,%xmm1
    1964:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
    1969:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
    196f:	c4 e2 55 36 db       	vpermd %ymm3,%ymm5,%ymm3
    1974:	c5 fe 7f 4a e0       	vmovdqu %ymm1,-0x20(%rdx)
    1979:	c5 f9 6f fb          	vmovdqa %xmm3,%xmm7
    197d:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    1983:	c4 c1 61 6c da       	vpunpcklqdq %xmm10,%xmm3,%xmm3
    1988:	c4 e3 45 38 db 01    	vinserti128 $0x1,%xmm3,%ymm7,%ymm3
    198e:	c5 fe 7f 5a a0       	vmovdqu %ymm3,-0x60(%rdx)
    1993:	49 39 c8             	cmp    %rcx,%r8
    1996:	0f 83 9c fc ff ff    	jae    1638 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7f8>
    199c:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    19a1:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    19a6:	4d 8d 59 08          	lea    0x8(%r9),%r11
    19aa:	4d 39 d8             	cmp    %r11,%r8
    19ad:	0f 82 47 01 00 00    	jb     1afa <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcba>
    19b3:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    19b8:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    19bc:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 19c4 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb84>
    19c3:	00 
    19c4:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    19c9:	4a 8d 0c 13          	lea    (%rbx,%r10,1),%rcx
    19cd:	4d 01 e2             	add    %r12,%r10
    19d0:	4c 8b 21             	mov    (%rcx),%r12
    19d3:	48 8b 41 08          	mov    0x8(%rcx),%rax
    19d7:	49 83 c2 18          	add    $0x18,%r10
    19db:	48 83 c1 18          	add    $0x18,%rcx
    19df:	48 8b 51 f8          	mov    -0x8(%rcx),%rdx
    19e3:	4d 89 e1             	mov    %r12,%r9
    19e6:	4d 89 e5             	mov    %r12,%r13
    19e9:	49 89 c6             	mov    %rax,%r14
    19ec:	49 c1 ed 30          	shr    $0x30,%r13
    19f0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19f7:	41 89 d7             	mov    %edx,%r15d
    19fa:	49 c1 ee 20          	shr    $0x20,%r14
    19fe:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1a03:	4d 89 e1             	mov    %r12,%r9
    1a06:	41 89 c4             	mov    %eax,%r12d
    1a09:	41 c1 e7 08          	shl    $0x8,%r15d
    1a0d:	41 c1 e4 10          	shl    $0x10,%r12d
    1a11:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1a18:	49 c1 e9 18          	shr    $0x18,%r9
    1a1c:	45 09 ec             	or     %r13d,%r12d
    1a1f:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1a24:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a2b:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    1a30:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1a37:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1a3c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1a41:	41 89 c4             	mov    %eax,%r12d
    1a44:	48 c1 e8 38          	shr    $0x38,%rax
    1a48:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1a4e:	41 09 c7             	or     %eax,%r15d
    1a51:	41 c1 ec 08          	shr    $0x8,%r12d
    1a55:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1a5c:	4d 89 d9             	mov    %r11,%r9
    1a5f:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1a66:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1a6b:	49 83 c3 08          	add    $0x8,%r11
    1a6f:	42 0f b6 04 3f       	movzbl (%rdi,%r15,1),%eax
    1a74:	49 89 d7             	mov    %rdx,%r15
    1a77:	48 c1 ea 28          	shr    $0x28,%rdx
    1a7b:	49 c1 ef 10          	shr    $0x10,%r15
    1a7f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1a83:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1a8a:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
    1a91:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1a96:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1a9c:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
    1aa3:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1aa7:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1aad:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1ab4:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1ab8:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1abe:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1ac3:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    1ac7:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1acd:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1ad2:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1ad7:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1adb:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1ae1:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    1ae7:	4d 39 d8             	cmp    %r11,%r8
    1aea:	0f 83 e0 fe ff ff    	jae    19d0 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb90>
    1af0:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1af5:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1afa:	4d 39 c1             	cmp    %r8,%r9
    1afd:	0f 83 15 02 00 00    	jae    1d18 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1b03:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1b07:	4c 8d 14 03          	lea    (%rbx,%rax,1),%r10
    1b0b:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1b10:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1b15:	45 0f b6 12          	movzbl (%r10),%r10d
    1b19:	c1 e2 08             	shl    $0x8,%edx
    1b1c:	41 c1 e3 10          	shl    $0x10,%r11d
    1b20:	44 09 da             	or     %r11d,%edx
    1b23:	44 09 d2             	or     %r10d,%edx
    1b26:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1b2a:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    1b2e:	41 8b 12             	mov    (%r10),%edx
    1b31:	45 0f b7 12          	movzwl (%r10),%r10d
    1b35:	c1 ea 10             	shr    $0x10,%edx
    1b38:	66 45 89 14 04       	mov    %r10w,(%r12,%rax,1)
    1b3d:	41 88 54 04 02       	mov    %dl,0x2(%r12,%rax,1)
    1b42:	49 8d 51 01          	lea    0x1(%r9),%rdx
    1b46:	4c 39 c2             	cmp    %r8,%rdx
    1b49:	0f 83 c9 01 00 00    	jae    1d18 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1b4f:	4c 8d 54 03 03       	lea    0x3(%rbx,%rax,1),%r10
    1b54:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1b59:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1b5e:	45 0f b6 12          	movzbl (%r10),%r10d
    1b62:	41 c1 e3 10          	shl    $0x10,%r11d
    1b66:	c1 e2 08             	shl    $0x8,%edx
    1b69:	44 09 da             	or     %r11d,%edx
    1b6c:	44 09 d2             	or     %r10d,%edx
    1b6f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1b73:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1b77:	44 8b 12             	mov    (%rdx),%r10d
    1b7a:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1b7e:	49 8d 51 02          	lea    0x2(%r9),%rdx
    1b82:	44 89 d1             	mov    %r10d,%ecx
    1b85:	66 45 89 5c 04 03    	mov    %r11w,0x3(%r12,%rax,1)
    1b8b:	c1 e9 10             	shr    $0x10,%ecx
    1b8e:	41 88 4c 04 05       	mov    %cl,0x5(%r12,%rax,1)
    1b93:	4c 39 c2             	cmp    %r8,%rdx
    1b96:	0f 83 7c 01 00 00    	jae    1d18 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1b9c:	4c 8d 54 03 06       	lea    0x6(%rbx,%rax,1),%r10
    1ba1:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1ba6:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1bab:	45 0f b6 12          	movzbl (%r10),%r10d
    1baf:	41 c1 e3 10          	shl    $0x10,%r11d
    1bb3:	c1 e2 08             	shl    $0x8,%edx
    1bb6:	44 09 da             	or     %r11d,%edx
    1bb9:	44 09 d2             	or     %r10d,%edx
    1bbc:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1bc0:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1bc4:	44 8b 12             	mov    (%rdx),%r10d
    1bc7:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1bcb:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1bcf:	44 89 d1             	mov    %r10d,%ecx
    1bd2:	66 45 89 5c 04 06    	mov    %r11w,0x6(%r12,%rax,1)
    1bd8:	c1 e9 10             	shr    $0x10,%ecx
    1bdb:	41 88 4c 04 08       	mov    %cl,0x8(%r12,%rax,1)
    1be0:	4c 39 c2             	cmp    %r8,%rdx
    1be3:	0f 83 2f 01 00 00    	jae    1d18 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1be9:	4c 8d 54 03 09       	lea    0x9(%rbx,%rax,1),%r10
    1bee:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1bf3:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1bf8:	45 0f b6 12          	movzbl (%r10),%r10d
    1bfc:	41 c1 e3 08          	shl    $0x8,%r11d
    1c00:	c1 e2 10             	shl    $0x10,%edx
    1c03:	44 09 da             	or     %r11d,%edx
    1c06:	44 09 d2             	or     %r10d,%edx
    1c09:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c0d:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1c11:	44 8b 12             	mov    (%rdx),%r10d
    1c14:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1c18:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1c1c:	44 89 d1             	mov    %r10d,%ecx
    1c1f:	66 45 89 5c 04 09    	mov    %r11w,0x9(%r12,%rax,1)
    1c25:	c1 e9 10             	shr    $0x10,%ecx
    1c28:	41 88 4c 04 0b       	mov    %cl,0xb(%r12,%rax,1)
    1c2d:	4c 39 c2             	cmp    %r8,%rdx
    1c30:	0f 83 e2 00 00 00    	jae    1d18 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1c36:	4c 8d 54 03 0c       	lea    0xc(%rbx,%rax,1),%r10
    1c3b:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1c40:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1c45:	45 0f b6 12          	movzbl (%r10),%r10d
    1c49:	41 c1 e3 08          	shl    $0x8,%r11d
    1c4d:	c1 e2 10             	shl    $0x10,%edx
    1c50:	44 09 da             	or     %r11d,%edx
    1c53:	44 09 d2             	or     %r10d,%edx
    1c56:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1c5a:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1c5e:	44 8b 12             	mov    (%rdx),%r10d
    1c61:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1c65:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1c69:	44 89 d1             	mov    %r10d,%ecx
    1c6c:	66 45 89 5c 04 0c    	mov    %r11w,0xc(%r12,%rax,1)
    1c72:	c1 e9 10             	shr    $0x10,%ecx
    1c75:	41 88 4c 04 0e       	mov    %cl,0xe(%r12,%rax,1)
    1c7a:	4c 39 c2             	cmp    %r8,%rdx
    1c7d:	0f 83 95 00 00 00    	jae    1d18 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1c83:	4c 8d 54 03 0f       	lea    0xf(%rbx,%rax,1),%r10
    1c88:	49 83 c1 06          	add    $0x6,%r9
    1c8c:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1c91:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1c96:	45 0f b6 12          	movzbl (%r10),%r10d
    1c9a:	41 c1 e3 08          	shl    $0x8,%r11d
    1c9e:	c1 e2 10             	shl    $0x10,%edx
    1ca1:	44 09 da             	or     %r11d,%edx
    1ca4:	44 09 d2             	or     %r10d,%edx
    1ca7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1cab:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1caf:	44 8b 12             	mov    (%rdx),%r10d
    1cb2:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1cb6:	44 89 d1             	mov    %r10d,%ecx
    1cb9:	66 45 89 5c 04 0f    	mov    %r11w,0xf(%r12,%rax,1)
    1cbf:	c1 e9 10             	shr    $0x10,%ecx
    1cc2:	41 88 4c 04 11       	mov    %cl,0x11(%r12,%rax,1)
    1cc7:	4d 39 c1             	cmp    %r8,%r9
    1cca:	73 4c                	jae    1d18 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xed8>
    1ccc:	48 8d 54 03 12       	lea    0x12(%rbx,%rax,1),%rdx
    1cd1:	4d 8d 44 04 12       	lea    0x12(%r12,%rax,1),%r8
    1cd6:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1cda:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1cde:	0f b6 12             	movzbl (%rdx),%edx
    1ce1:	c1 e0 08             	shl    $0x8,%eax
    1ce4:	c1 e1 10             	shl    $0x10,%ecx
    1ce7:	09 c8                	or     %ecx,%eax
    1ce9:	09 d0                	or     %edx,%eax
    1ceb:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1cef:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1cf3:	8b 02                	mov    (%rdx),%eax
    1cf5:	0f b7 12             	movzwl (%rdx),%edx
    1cf8:	c1 e8 10             	shr    $0x10,%eax
    1cfb:	66 41 89 10          	mov    %dx,(%r8)
    1cff:	41 88 40 02          	mov    %al,0x2(%r8)
    1d03:	c5 f8 77             	vzeroupper
    1d06:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1d0a:	5b                   	pop    %rbx
    1d0b:	41 5c                	pop    %r12
    1d0d:	41 5d                	pop    %r13
    1d0f:	41 5e                	pop    %r14
    1d11:	41 5f                	pop    %r15
    1d13:	5d                   	pop    %rbp
    1d14:	c3                   	ret
    1d15:	0f 1f 00             	nopl   (%rax)
    1d18:	c5 f8 77             	vzeroupper
    1d1b:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1d1f:	5b                   	pop    %rbx
    1d20:	41 5c                	pop    %r12
    1d22:	41 5d                	pop    %r13
    1d24:	41 5e                	pop    %r14
    1d26:	41 5f                	pop    %r15
    1d28:	5d                   	pop    %rbp
    1d29:	c3                   	ret
    1d2a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1d30:	4d 89 c1             	mov    %r8,%r9
    1d33:	e9 6e fc ff ff       	jmp    19a6 <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb66>
    1d38:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    1d3f:	00 
    1d40:	c3                   	ret
    1d41:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1d45:	49 89 c9             	mov    %rcx,%r9
    1d48:	e9 af f8 ff ff       	jmp    15fc <jshc_channel::avx2_chain_splitpack_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7bc>
