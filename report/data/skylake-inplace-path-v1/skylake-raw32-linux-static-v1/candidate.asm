
artifacts/skylake-raw32-linux-build-v1/CMakeFiles/jshc_skylake_raw32.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 23 0d 00 00    	je     d30 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd30>
       d:	55                   	push   %rbp
       e:	b8 00 04 00 00       	mov    $0x400,%eax
      13:	48 8d 34 49          	lea    (%rcx,%rcx,2),%rsi
      17:	48 39 c6             	cmp    %rax,%rsi
      1a:	48 0f 47 f0          	cmova  %rax,%rsi
      1e:	31 c0                	xor    %eax,%eax
      20:	48 89 e5             	mov    %rsp,%rbp
      23:	41 56                	push   %r14
      25:	41 55                	push   %r13
      27:	41 54                	push   %r12
      29:	53                   	push   %rbx
      2a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
      30:	0f 18 04 02          	prefetchnta (%rdx,%rax,1)
      34:	48 83 c0 40          	add    $0x40,%rax
      38:	48 39 f0             	cmp    %rsi,%rax
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	48 89 d6             	mov    %rdx,%rsi
      40:	45 31 c0             	xor    %r8d,%r8d
      43:	eb 44                	jmp    89 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x89>
      45:	0f 1f 00             	nopl   (%rax)
      48:	0f b6 46 01          	movzbl 0x1(%rsi),%eax
      4c:	44 0f b6 4e 02       	movzbl 0x2(%rsi),%r9d
      51:	49 ff c0             	inc    %r8
      54:	48 83 c6 03          	add    $0x3,%rsi
      58:	41 c1 e1 10          	shl    $0x10,%r9d
      5c:	c1 e0 08             	shl    $0x8,%eax
      5f:	44 09 c8             	or     %r9d,%eax
      62:	44 0f b6 4e fd       	movzbl -0x3(%rsi),%r9d
      67:	44 09 c8             	or     %r9d,%eax
      6a:	4c 8d 0c 87          	lea    (%rdi,%rax,4),%r9
      6e:	41 8b 01             	mov    (%r9),%eax
      71:	45 0f b7 09          	movzwl (%r9),%r9d
      75:	c1 e8 10             	shr    $0x10,%eax
      78:	66 44 89 4e fd       	mov    %r9w,-0x3(%rsi)
      7d:	88 46 ff             	mov    %al,-0x1(%rsi)
      80:	4c 39 c1             	cmp    %r8,%rcx
      83:	0f 84 97 0c 00 00    	je     d20 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd20>
      89:	40 f6 c6 3f          	test   $0x3f,%sil
      8d:	75 b9                	jne    48 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      8f:	49 8d 40 48          	lea    0x48(%r8),%rax
      93:	48 39 c1             	cmp    %rax,%rcx
      96:	0f 82 95 0c 00 00    	jb     d31 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd31>
      9c:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
      a0:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # a8 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa8>
      a7:	00 
      a8:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # b0 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb0>
      af:	00 
      b0:	48 01 d0             	add    %rdx,%rax
      b3:	eb 06                	jmp    bb <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbb>
      b5:	0f 1f 00             	nopl   (%rax)
      b8:	49 89 f0             	mov    %rsi,%r8
      bb:	49 8d b0 96 01 00 00 	lea    0x196(%r8),%rsi
      c2:	48 39 f1             	cmp    %rsi,%rcx
      c5:	72 1c                	jb     e3 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe3>
      c7:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      ce:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      d5:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
      dc:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
      e3:	44 8b 60 0c          	mov    0xc(%rax),%r12d
      e7:	44 8b 70 12          	mov    0x12(%rax),%r14d
      eb:	8b 58 0f             	mov    0xf(%rax),%ebx
      ee:	44 8b 68 15          	mov    0x15(%rax),%r13d
      f2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
      f9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     100:	44 8b 08             	mov    (%rax),%r9d
     103:	44 8b 58 06          	mov    0x6(%rax),%r11d
     107:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     10d:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     113:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     119:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     120:	8b 70 03             	mov    0x3(%rax),%esi
     123:	44 8b 50 09          	mov    0x9(%rax),%r10d
     127:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     12e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     135:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     13c:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     143:	c4 21 79 6e 0c 8f    	vmovd  (%rdi,%r9,4),%xmm9
     149:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     14f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     156:	44 8b 60 24          	mov    0x24(%rax),%r12d
     15a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     15e:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     164:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     168:	c4 63 31 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm9,%xmm9
     16f:	8b 58 27             	mov    0x27(%rax),%ebx
     172:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     179:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     180:	44 8b 68 2d          	mov    0x2d(%rax),%r13d
     184:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     18b:	44 8b 48 18          	mov    0x18(%rax),%r9d
     18f:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     193:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     199:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     19d:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     1a3:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     1aa:	8b 70 1b             	mov    0x1b(%rax),%esi
     1ad:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     1b3:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     1b9:	44 8b 50 21          	mov    0x21(%rax),%r10d
     1bd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     1c4:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     1cb:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1d2:	c4 a1 79 6e 34 8f    	vmovd  (%rdi,%r9,4),%xmm6
     1d8:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     1de:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     1e5:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     1ec:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     1f1:	c4 e3 49 22 34 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm6,%xmm6
     1f8:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     1fd:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     201:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     207:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     20e:	44 8b 48 30          	mov    0x30(%rax),%r9d
     212:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     216:	44 8b 70 42          	mov    0x42(%rax),%r14d
     21a:	8b 58 3f             	mov    0x3f(%rax),%ebx
     21d:	44 8b 68 45          	mov    0x45(%rax),%r13d
     221:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     225:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     22c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     233:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     23a:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     240:	44 8b 58 36          	mov    0x36(%rax),%r11d
     244:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     24a:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     250:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     256:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     25d:	8b 70 33             	mov    0x33(%rax),%esi
     260:	44 8b 50 39          	mov    0x39(%rax),%r10d
     264:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     26b:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     270:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     277:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     27e:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     283:	c4 a1 79 6e 2c 8f    	vmovd  (%rdi,%r9,4),%xmm5
     289:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     28f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     296:	44 8b 60 54          	mov    0x54(%rax),%r12d
     29a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     29e:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     2a4:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     2a8:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     2ac:	c4 e3 51 22 2c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm5,%xmm5
     2b3:	8b 58 57             	mov    0x57(%rax),%ebx
     2b6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2bd:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     2c3:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     2ca:	44 8b 68 5d          	mov    0x5d(%rax),%r13d
     2ce:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     2d4:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     2db:	44 8b 48 48          	mov    0x48(%rax),%r9d
     2df:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     2e3:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     2e9:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     2ed:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     2f3:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     2fa:	8b 70 4b             	mov    0x4b(%rax),%esi
     2fd:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     303:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     309:	44 8b 50 51          	mov    0x51(%rax),%r10d
     30d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     314:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     31b:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     322:	c4 21 79 6e 04 8f    	vmovd  (%rdi,%r9,4),%xmm8
     328:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     32e:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     335:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     33c:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     341:	c4 63 39 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm8,%xmm8
     348:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     34d:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     351:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     357:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     35b:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     361:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     367:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     36e:	44 8b 48 60          	mov    0x60(%rax),%r9d
     372:	44 8b 60 6c          	mov    0x6c(%rax),%r12d
     376:	44 8b 70 72          	mov    0x72(%rax),%r14d
     37a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     381:	8b 58 6f             	mov    0x6f(%rax),%ebx
     384:	44 8b 68 75          	mov    0x75(%rax),%r13d
     388:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     38c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     393:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     39a:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     3a0:	44 8b 58 66          	mov    0x66(%rax),%r11d
     3a4:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     3aa:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     3b0:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     3b6:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     3bd:	8b 70 63             	mov    0x63(%rax),%esi
     3c0:	44 8b 50 69          	mov    0x69(%rax),%r10d
     3c4:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     3cb:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     3d0:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     3d7:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     3de:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     3e3:	c4 a1 79 6e 3c 8f    	vmovd  (%rdi,%r9,4),%xmm7
     3e9:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     3ef:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     3f6:	44 8b a0 84 00 00 00 	mov    0x84(%rax),%r12d
     3fd:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     401:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     407:	44 8b b0 8a 00 00 00 	mov    0x8a(%rax),%r14d
     40e:	c4 e3 41 22 3c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm7,%xmm7
     415:	8b 98 87 00 00 00    	mov    0x87(%rax),%ebx
     41b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     422:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     429:	44 8b a8 8d 00 00 00 	mov    0x8d(%rax),%r13d
     430:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     437:	44 8b 48 78          	mov    0x78(%rax),%r9d
     43b:	44 8b 58 7e          	mov    0x7e(%rax),%r11d
     43f:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     445:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     449:	c4 a1 79 6e 0c a7    	vmovd  (%rdi,%r12,4),%xmm1
     44f:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     456:	8b 70 7b             	mov    0x7b(%rax),%esi
     459:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     45f:	c4 a1 79 6e 04 b7    	vmovd  (%rdi,%r14,4),%xmm0
     465:	44 8b 90 81 00 00 00 	mov    0x81(%rax),%r10d
     46c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     473:	c4 e3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm1,%xmm1
     47a:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     481:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     486:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     48c:	c4 a3 79 22 04 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm0,%xmm0
     493:	c4 a1 79 6e 14 9f    	vmovd  (%rdi,%r11,4),%xmm2
     499:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     4a0:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     4a5:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     4a9:	c4 a1 79 6e 04 8f    	vmovd  (%rdi,%r9,4),%xmm0
     4af:	c4 a3 69 22 14 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm2,%xmm2
     4b6:	c4 e3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm0,%xmm0
     4bd:	44 8b 88 90 00 00 00 	mov    0x90(%rax),%r9d
     4c4:	44 8b a0 9c 00 00 00 	mov    0x9c(%rax),%r12d
     4cb:	44 8b b0 a2 00 00 00 	mov    0xa2(%rax),%r14d
     4d2:	8b 98 9f 00 00 00    	mov    0x9f(%rax),%ebx
     4d8:	44 8b a8 a5 00 00 00 	mov    0xa5(%rax),%r13d
     4df:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     4e3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     4ea:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     4f1:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     4f8:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     4fe:	44 8b 98 96 00 00 00 	mov    0x96(%rax),%r11d
     505:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     50b:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     511:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     517:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     51e:	8b b0 93 00 00 00    	mov    0x93(%rax),%esi
     524:	44 8b 90 99 00 00 00 	mov    0x99(%rax),%r10d
     52b:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     532:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     537:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     53e:	c4 e3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm2,%xmm2
     545:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     54a:	c4 21 79 6e 14 9f    	vmovd  (%rdi,%r11,4),%xmm10
     550:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     556:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     55d:	44 8b a0 b4 00 00 00 	mov    0xb4(%rax),%r12d
     564:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     568:	c4 a1 79 6e 0c 8f    	vmovd  (%rdi,%r9,4),%xmm1
     56e:	44 8b b0 ba 00 00 00 	mov    0xba(%rax),%r14d
     575:	c4 23 29 22 14 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm10,%xmm10
     57c:	8b 98 b7 00 00 00    	mov    0xb7(%rax),%ebx
     582:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     589:	c4 e3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm1,%xmm1
     590:	44 8b a8 bd 00 00 00 	mov    0xbd(%rax),%r13d
     597:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     59e:	44 8b 88 a8 00 00 00 	mov    0xa8(%rax),%r9d
     5a5:	44 8b 98 ae 00 00 00 	mov    0xae(%rax),%r11d
     5ac:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     5b2:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     5b7:	c4 21 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm10
     5bd:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     5c4:	8b b0 ab 00 00 00    	mov    0xab(%rax),%esi
     5ca:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     5d0:	c4 a1 79 6e 14 b7    	vmovd  (%rdi,%r14,4),%xmm2
     5d6:	44 8b 90 b1 00 00 00 	mov    0xb1(%rax),%r10d
     5dd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     5e4:	c4 63 29 22 14 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm10,%xmm10
     5eb:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     5f2:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     5f7:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     5fd:	c4 a3 69 22 14 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm2,%xmm2
     604:	c4 21 79 6e 1c 9f    	vmovd  (%rdi,%r11,4),%xmm11
     60a:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     611:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     616:	48 05 c0 00 00 00    	add    $0xc0,%rax
     61c:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     620:	c4 a1 79 6e 14 8f    	vmovd  (%rdi,%r9,4),%xmm2
     626:	c4 23 21 22 1c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm11,%xmm11
     62d:	4d 8d 88 88 00 00 00 	lea    0x88(%r8),%r9
     634:	c4 e3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm2,%xmm2
     63b:	49 8d 70 40          	lea    0x40(%r8),%rsi
     63f:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     644:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     649:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     64f:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     655:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     65a:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     660:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     666:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     66b:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     670:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     675:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     67a:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     680:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     686:	c5 7d e7 88 40 ff ff 	vmovntdq %ymm9,-0xc0(%rax)
     68d:	ff 
     68e:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     692:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     696:	c5 fd e7 b0 60 ff ff 	vmovntdq %ymm6,-0xa0(%rax)
     69d:	ff 
     69e:	c5 fd e7 68 80       	vmovntdq %ymm5,-0x80(%rax)
     6a3:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     6a7:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     6ab:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     6b1:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     6b7:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     6bd:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     6c3:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     6c8:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     6cc:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     6d2:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     6d8:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     6de:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     6e4:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     6ea:	c5 fd e7 68 a0       	vmovntdq %ymm5,-0x60(%rax)
     6ef:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     6f4:	c5 fd e7 48 e0       	vmovntdq %ymm1,-0x20(%rax)
     6f9:	4c 39 c9             	cmp    %r9,%rcx
     6fc:	0f 83 b6 f9 ff ff    	jae    b8 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb8>
     702:	0f ae f8             	sfence
     705:	49 8d 40 68          	lea    0x68(%r8),%rax
     709:	48 39 c1             	cmp    %rax,%rcx
     70c:	0f 82 18 03 00 00    	jb     a2a <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa2a>
     712:	48 8d 04 76          	lea    (%rsi,%rsi,2),%rax
     716:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 71e <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x71e>
     71d:	00 
     71e:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 726 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x726>
     725:	00 
     726:	48 01 d0             	add    %rdx,%rax
     729:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     730:	44 8b 60 54          	mov    0x54(%rax),%r12d
     734:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     738:	8b 58 57             	mov    0x57(%rax),%ebx
     73b:	44 8b 68 5d          	mov    0x5d(%rax),%r13d
     73f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     746:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     74d:	44 8b 48 48          	mov    0x48(%rax),%r9d
     751:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     755:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     75b:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     761:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     767:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     76e:	44 8b 40 4b          	mov    0x4b(%rax),%r8d
     772:	44 8b 50 51          	mov    0x51(%rax),%r10d
     776:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     77d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     784:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     78b:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     792:	c4 a1 79 6e 2c 8f    	vmovd  (%rdi,%r9,4),%xmm5
     798:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     79f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     7a6:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     7aa:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     7ae:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     7b4:	44 8b 70 42          	mov    0x42(%rax),%r14d
     7b8:	c4 a3 51 22 2c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm5,%xmm5
     7bf:	8b 58 3f             	mov    0x3f(%rax),%ebx
     7c2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     7c9:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     7d0:	44 8b 68 45          	mov    0x45(%rax),%r13d
     7d4:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     7db:	44 8b 48 30          	mov    0x30(%rax),%r9d
     7df:	44 8b 58 36          	mov    0x36(%rax),%r11d
     7e3:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     7e9:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     7ed:	c4 a1 79 6e 0c a7    	vmovd  (%rdi,%r12,4),%xmm1
     7f3:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     7fa:	44 8b 40 33          	mov    0x33(%rax),%r8d
     7fe:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     804:	c4 a1 79 6e 04 b7    	vmovd  (%rdi,%r14,4),%xmm0
     80a:	44 8b 50 39          	mov    0x39(%rax),%r10d
     80e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     815:	c4 e3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm1,%xmm1
     81c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     823:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     828:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     82f:	c4 a3 79 22 04 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm0,%xmm0
     836:	c4 a1 79 6e 14 9f    	vmovd  (%rdi,%r11,4),%xmm2
     83c:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     843:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     848:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     84c:	c4 a1 79 6e 04 8f    	vmovd  (%rdi,%r9,4),%xmm0
     852:	c4 a3 69 22 14 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm2,%xmm2
     859:	c4 a3 79 22 04 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm0,%xmm0
     860:	44 8b 48 18          	mov    0x18(%rax),%r9d
     864:	44 8b 60 24          	mov    0x24(%rax),%r12d
     868:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     86c:	8b 58 27             	mov    0x27(%rax),%ebx
     86f:	44 8b 68 2d          	mov    0x2d(%rax),%r13d
     873:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     877:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     87e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     885:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     88c:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     892:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     896:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     89c:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     8a2:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     8a8:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     8af:	44 8b 40 1b          	mov    0x1b(%rax),%r8d
     8b3:	44 8b 50 21          	mov    0x21(%rax),%r10d
     8b7:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     8be:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     8c3:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     8ca:	c4 e3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm2,%xmm2
     8d1:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     8d6:	c4 a1 79 6e 34 9f    	vmovd  (%rdi,%r11,4),%xmm6
     8dc:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     8e3:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     8ea:	44 8b 60 0c          	mov    0xc(%rax),%r12d
     8ee:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     8f2:	c4 a1 79 6e 0c 8f    	vmovd  (%rdi,%r9,4),%xmm1
     8f8:	44 8b 70 12          	mov    0x12(%rax),%r14d
     8fc:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     900:	c4 a3 49 22 34 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm6,%xmm6
     907:	8b 58 0f             	mov    0xf(%rax),%ebx
     90a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     911:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     917:	c4 a3 71 22 0c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm1,%xmm1
     91e:	44 8b 68 15          	mov    0x15(%rax),%r13d
     922:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     929:	44 8b 08             	mov    (%rax),%r9d
     92c:	44 8b 58 06          	mov    0x6(%rax),%r11d
     930:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     936:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     93a:	c4 a1 79 6e 34 a7    	vmovd  (%rdi,%r12,4),%xmm6
     940:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     947:	44 8b 40 03          	mov    0x3(%rax),%r8d
     94b:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     951:	c4 a1 79 6e 14 b7    	vmovd  (%rdi,%r14,4),%xmm2
     957:	44 8b 50 09          	mov    0x9(%rax),%r10d
     95b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     962:	c4 e3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm6,%xmm6
     969:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     970:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     975:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     97c:	c4 a3 69 22 14 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm2,%xmm2
     983:	c4 a1 79 6e 3c 9f    	vmovd  (%rdi,%r11,4),%xmm7
     989:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     990:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     995:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     999:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     99f:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     9a3:	c4 a1 79 6e 14 8f    	vmovd  (%rdi,%r9,4),%xmm2
     9a9:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     9af:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
     9b6:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     9bc:	c4 a3 69 22 14 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm2,%xmm2
     9c3:	4c 8d 46 48          	lea    0x48(%rsi),%r8
     9c7:	48 83 c6 20          	add    $0x20,%rsi
     9cb:	48 83 c0 60          	add    $0x60,%rax
     9cf:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     9d3:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
     9d7:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     9dd:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     9e3:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
     9e9:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
     9ed:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     9f2:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
     9f8:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     9fd:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     a01:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     a07:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     a0c:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
     a12:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     a17:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     a1c:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     a21:	4c 39 c1             	cmp    %r8,%rcx
     a24:	0f 83 06 fd ff ff    	jae    730 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x730>
     a2a:	4c 8d 4e 08          	lea    0x8(%rsi),%r9
     a2e:	4c 39 c9             	cmp    %r9,%rcx
     a31:	0f 82 05 01 00 00    	jb     b3c <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb3c>
     a37:	48 8d 04 76          	lea    (%rsi,%rsi,2),%rax
     a3b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # a43 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa43>
     a42:	00 
     a43:	48 01 d0             	add    %rdx,%rax
     a46:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     a4d:	00 00 00 
     a50:	48 8b 70 08          	mov    0x8(%rax),%rsi
     a54:	4c 8b 00             	mov    (%rax),%r8
     a57:	48 83 c0 18          	add    $0x18,%rax
     a5b:	4c 8b 60 f8          	mov    -0x8(%rax),%r12
     a5f:	89 f3                	mov    %esi,%ebx
     a61:	4d 89 c3             	mov    %r8,%r11
     a64:	4d 89 c2             	mov    %r8,%r10
     a67:	49 c1 e8 30          	shr    $0x30,%r8
     a6b:	c1 e3 10             	shl    $0x10,%ebx
     a6e:	45 89 e6             	mov    %r12d,%r14d
     a71:	49 89 f5             	mov    %rsi,%r13
     a74:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a7b:	41 c1 e6 08          	shl    $0x8,%r14d
     a7f:	41 09 d8             	or     %ebx,%r8d
     a82:	89 f3                	mov    %esi,%ebx
     a84:	48 c1 ee 38          	shr    $0x38,%rsi
     a88:	49 c1 ed 20          	shr    $0x20,%r13
     a8c:	44 09 f6             	or     %r14d,%esi
     a8f:	4d 89 e6             	mov    %r12,%r14
     a92:	49 c1 ec 28          	shr    $0x28,%r12
     a96:	49 c1 ee 10          	shr    $0x10,%r14
     a9a:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     aa1:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     aa7:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     aae:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     ab5:	c4 a1 79 6e 0c af    	vmovd  (%rdi,%r13,4),%xmm1
     abb:	c4 a1 79 6e 14 87    	vmovd  (%rdi,%r8,4),%xmm2
     ac1:	49 c1 ea 18          	shr    $0x18,%r10
     ac5:	c4 a1 79 6e 04 b7    	vmovd  (%rdi,%r14,4),%xmm0
     acb:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     ad2:	c1 eb 08             	shr    $0x8,%ebx
     ad5:	c4 e3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm1,%xmm1
     adc:	c4 e3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm2,%xmm2
     ae3:	4c 89 ce             	mov    %r9,%rsi
     ae6:	49 83 c1 08          	add    $0x8,%r9
     aea:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
     af1:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     af5:	c4 a1 79 6e 04 9f    	vmovd  (%rdi,%r11,4),%xmm0
     afb:	c4 a3 79 22 04 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm0,%xmm0
     b02:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     b06:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     b0c:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     b11:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
     b15:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     b1b:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
     b20:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     b25:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
     b29:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     b2e:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
     b33:	4c 39 c9             	cmp    %r9,%rcx
     b36:	0f 83 14 ff ff ff    	jae    a50 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa50>
     b3c:	48 39 ce             	cmp    %rcx,%rsi
     b3f:	0f 83 cb 01 00 00    	jae    d10 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     b45:	4c 8d 04 76          	lea    (%rsi,%rsi,2),%r8
     b49:	4e 8d 0c 02          	lea    (%rdx,%r8,1),%r9
     b4d:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     b52:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     b57:	c1 e0 08             	shl    $0x8,%eax
     b5a:	41 c1 e2 10          	shl    $0x10,%r10d
     b5e:	44 09 d0             	or     %r10d,%eax
     b61:	45 0f b6 11          	movzbl (%r9),%r10d
     b65:	44 09 d0             	or     %r10d,%eax
     b68:	4c 8d 14 87          	lea    (%rdi,%rax,4),%r10
     b6c:	41 8b 02             	mov    (%r10),%eax
     b6f:	45 0f b7 12          	movzwl (%r10),%r10d
     b73:	c1 e8 10             	shr    $0x10,%eax
     b76:	66 45 89 11          	mov    %r10w,(%r9)
     b7a:	41 88 41 02          	mov    %al,0x2(%r9)
     b7e:	48 8d 46 01          	lea    0x1(%rsi),%rax
     b82:	48 39 c8             	cmp    %rcx,%rax
     b85:	0f 83 85 01 00 00    	jae    d10 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     b8b:	4e 8d 4c 02 03       	lea    0x3(%rdx,%r8,1),%r9
     b90:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     b95:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     b9a:	c1 e0 08             	shl    $0x8,%eax
     b9d:	41 c1 e2 10          	shl    $0x10,%r10d
     ba1:	44 09 d0             	or     %r10d,%eax
     ba4:	45 0f b6 11          	movzbl (%r9),%r10d
     ba8:	44 09 d0             	or     %r10d,%eax
     bab:	4c 8d 14 87          	lea    (%rdi,%rax,4),%r10
     baf:	41 8b 02             	mov    (%r10),%eax
     bb2:	45 0f b7 12          	movzwl (%r10),%r10d
     bb6:	c1 e8 10             	shr    $0x10,%eax
     bb9:	66 45 89 11          	mov    %r10w,(%r9)
     bbd:	41 88 41 02          	mov    %al,0x2(%r9)
     bc1:	48 8d 46 02          	lea    0x2(%rsi),%rax
     bc5:	48 39 c8             	cmp    %rcx,%rax
     bc8:	0f 83 42 01 00 00    	jae    d10 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     bce:	4e 8d 4c 02 06       	lea    0x6(%rdx,%r8,1),%r9
     bd3:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     bd8:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     bdd:	c1 e0 08             	shl    $0x8,%eax
     be0:	41 c1 e2 10          	shl    $0x10,%r10d
     be4:	44 09 d0             	or     %r10d,%eax
     be7:	45 0f b6 11          	movzbl (%r9),%r10d
     beb:	44 09 d0             	or     %r10d,%eax
     bee:	4c 8d 14 87          	lea    (%rdi,%rax,4),%r10
     bf2:	41 8b 02             	mov    (%r10),%eax
     bf5:	45 0f b7 12          	movzwl (%r10),%r10d
     bf9:	c1 e8 10             	shr    $0x10,%eax
     bfc:	66 45 89 11          	mov    %r10w,(%r9)
     c00:	41 88 41 02          	mov    %al,0x2(%r9)
     c04:	48 8d 46 03          	lea    0x3(%rsi),%rax
     c08:	48 39 c8             	cmp    %rcx,%rax
     c0b:	0f 83 ff 00 00 00    	jae    d10 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     c11:	4e 8d 4c 02 09       	lea    0x9(%rdx,%r8,1),%r9
     c16:	41 0f b6 41 02       	movzbl 0x2(%r9),%eax
     c1b:	45 0f b6 51 01       	movzbl 0x1(%r9),%r10d
     c20:	c1 e0 10             	shl    $0x10,%eax
     c23:	41 c1 e2 08          	shl    $0x8,%r10d
     c27:	44 09 d0             	or     %r10d,%eax
     c2a:	45 0f b6 11          	movzbl (%r9),%r10d
     c2e:	44 09 d0             	or     %r10d,%eax
     c31:	4c 8d 14 87          	lea    (%rdi,%rax,4),%r10
     c35:	41 8b 02             	mov    (%r10),%eax
     c38:	45 0f b7 12          	movzwl (%r10),%r10d
     c3c:	c1 e8 10             	shr    $0x10,%eax
     c3f:	66 45 89 11          	mov    %r10w,(%r9)
     c43:	41 88 41 02          	mov    %al,0x2(%r9)
     c47:	48 8d 46 04          	lea    0x4(%rsi),%rax
     c4b:	48 39 c8             	cmp    %rcx,%rax
     c4e:	0f 83 bc 00 00 00    	jae    d10 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     c54:	4e 8d 4c 02 0c       	lea    0xc(%rdx,%r8,1),%r9
     c59:	41 0f b6 41 02       	movzbl 0x2(%r9),%eax
     c5e:	45 0f b6 51 01       	movzbl 0x1(%r9),%r10d
     c63:	c1 e0 10             	shl    $0x10,%eax
     c66:	41 c1 e2 08          	shl    $0x8,%r10d
     c6a:	44 09 d0             	or     %r10d,%eax
     c6d:	45 0f b6 11          	movzbl (%r9),%r10d
     c71:	44 09 d0             	or     %r10d,%eax
     c74:	4c 8d 14 87          	lea    (%rdi,%rax,4),%r10
     c78:	41 8b 02             	mov    (%r10),%eax
     c7b:	45 0f b7 12          	movzwl (%r10),%r10d
     c7f:	c1 e8 10             	shr    $0x10,%eax
     c82:	66 45 89 11          	mov    %r10w,(%r9)
     c86:	41 88 41 02          	mov    %al,0x2(%r9)
     c8a:	48 8d 46 05          	lea    0x5(%rsi),%rax
     c8e:	48 39 c8             	cmp    %rcx,%rax
     c91:	73 7d                	jae    d10 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     c93:	4e 8d 4c 02 0f       	lea    0xf(%rdx,%r8,1),%r9
     c98:	48 83 c6 06          	add    $0x6,%rsi
     c9c:	41 0f b6 41 02       	movzbl 0x2(%r9),%eax
     ca1:	45 0f b6 51 01       	movzbl 0x1(%r9),%r10d
     ca6:	c1 e0 10             	shl    $0x10,%eax
     ca9:	41 c1 e2 08          	shl    $0x8,%r10d
     cad:	44 09 d0             	or     %r10d,%eax
     cb0:	45 0f b6 11          	movzbl (%r9),%r10d
     cb4:	44 09 d0             	or     %r10d,%eax
     cb7:	4c 8d 14 87          	lea    (%rdi,%rax,4),%r10
     cbb:	41 8b 02             	mov    (%r10),%eax
     cbe:	45 0f b7 12          	movzwl (%r10),%r10d
     cc2:	c1 e8 10             	shr    $0x10,%eax
     cc5:	66 45 89 11          	mov    %r10w,(%r9)
     cc9:	41 88 41 02          	mov    %al,0x2(%r9)
     ccd:	48 39 ce             	cmp    %rcx,%rsi
     cd0:	73 3e                	jae    d10 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     cd2:	4a 8d 54 02 12       	lea    0x12(%rdx,%r8,1),%rdx
     cd7:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     cdb:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     cdf:	c1 e0 08             	shl    $0x8,%eax
     ce2:	c1 e1 10             	shl    $0x10,%ecx
     ce5:	09 c8                	or     %ecx,%eax
     ce7:	0f b6 0a             	movzbl (%rdx),%ecx
     cea:	09 c8                	or     %ecx,%eax
     cec:	48 8d 0c 87          	lea    (%rdi,%rax,4),%rcx
     cf0:	8b 01                	mov    (%rcx),%eax
     cf2:	0f b7 09             	movzwl (%rcx),%ecx
     cf5:	c1 e8 10             	shr    $0x10,%eax
     cf8:	66 89 0a             	mov    %cx,(%rdx)
     cfb:	88 42 02             	mov    %al,0x2(%rdx)
     cfe:	c5 f8 77             	vzeroupper
     d01:	5b                   	pop    %rbx
     d02:	41 5c                	pop    %r12
     d04:	41 5d                	pop    %r13
     d06:	41 5e                	pop    %r14
     d08:	5d                   	pop    %rbp
     d09:	c3                   	ret
     d0a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     d10:	c5 f8 77             	vzeroupper
     d13:	5b                   	pop    %rbx
     d14:	41 5c                	pop    %r12
     d16:	41 5d                	pop    %r13
     d18:	41 5e                	pop    %r14
     d1a:	5d                   	pop    %rbp
     d1b:	c3                   	ret
     d1c:	0f 1f 40 00          	nopl   0x0(%rax)
     d20:	48 89 ce             	mov    %rcx,%rsi
     d23:	e9 02 fd ff ff       	jmp    a2a <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa2a>
     d28:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     d2f:	00 
     d30:	c3                   	ret
     d31:	49 8d 40 28          	lea    0x28(%r8),%rax
     d35:	4c 89 c6             	mov    %r8,%rsi
     d38:	e9 cc f9 ff ff       	jmp    709 <jshc_channel::avx2_chain_raw32(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x709>
     d3d:	0f 1f 00             	nopl   (%rax)

0000000000000d40 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     d40:	f3 0f 1e fa          	endbr64
     d44:	55                   	push   %rbp
     d45:	48 89 e5             	mov    %rsp,%rbp
     d48:	41 57                	push   %r15
     d4a:	41 56                	push   %r14
     d4c:	41 55                	push   %r13
     d4e:	41 54                	push   %r12
     d50:	53                   	push   %rbx
     d51:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     d55:	48 89 4c 24 f8       	mov    %rcx,-0x8(%rsp)
     d5a:	4d 85 c0             	test   %r8,%r8
     d5d:	0f 84 c0 0d 00 00    	je     1b23 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde3>
     d63:	b8 00 04 00 00       	mov    $0x400,%eax
     d68:	49 89 d1             	mov    %rdx,%r9
     d6b:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     d6f:	48 39 c2             	cmp    %rax,%rdx
     d72:	48 0f 47 d0          	cmova  %rax,%rdx
     d76:	31 c0                	xor    %eax,%eax
     d78:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     d7f:	00 
     d80:	41 0f 18 04 01       	prefetchnta (%r9,%rax,1)
     d85:	48 83 c0 40          	add    $0x40,%rax
     d89:	48 39 d0             	cmp    %rdx,%rax
     d8c:	72 f2                	jb     d80 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     d8e:	48 8b 54 24 f8       	mov    -0x8(%rsp),%rdx
     d93:	4c 89 ce             	mov    %r9,%rsi
     d96:	31 c9                	xor    %ecx,%ecx
     d98:	eb 4b                	jmp    de5 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa5>
     d9a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     da0:	0f b6 46 01          	movzbl 0x1(%rsi),%eax
     da4:	44 0f b6 56 02       	movzbl 0x2(%rsi),%r10d
     da9:	48 ff c1             	inc    %rcx
     dac:	48 83 c2 03          	add    $0x3,%rdx
     db0:	48 83 c6 03          	add    $0x3,%rsi
     db4:	41 c1 e2 10          	shl    $0x10,%r10d
     db8:	c1 e0 08             	shl    $0x8,%eax
     dbb:	44 09 d0             	or     %r10d,%eax
     dbe:	44 0f b6 56 fd       	movzbl -0x3(%rsi),%r10d
     dc3:	44 09 d0             	or     %r10d,%eax
     dc6:	4c 8d 14 87          	lea    (%rdi,%rax,4),%r10
     dca:	41 8b 02             	mov    (%r10),%eax
     dcd:	45 0f b7 12          	movzwl (%r10),%r10d
     dd1:	c1 e8 10             	shr    $0x10,%eax
     dd4:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
     dd9:	88 42 ff             	mov    %al,-0x1(%rdx)
     ddc:	49 39 c8             	cmp    %rcx,%r8
     ddf:	0f 84 53 0d 00 00    	je     1b38 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdf8>
     de5:	f6 c2 3f             	test   $0x3f,%dl
     de8:	75 b6                	jne    da0 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     dea:	48 8d 41 48          	lea    0x48(%rcx),%rax
     dee:	49 39 c0             	cmp    %rax,%r8
     df1:	0f 82 49 0d 00 00    	jb     1b40 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe00>
     df7:	48 8b 54 24 f8       	mov    -0x8(%rsp),%rdx
     dfc:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     e00:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # e08 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc8>
     e07:	00 
     e08:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # e10 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd0>
     e0f:	00 
     e10:	48 01 c2             	add    %rax,%rdx
     e13:	49 8d 84 01 00 04 00 	lea    0x400(%r9,%rax,1),%rax
     e1a:	00 
     e1b:	eb 06                	jmp    e23 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe3>
     e1d:	0f 1f 00             	nopl   (%rax)
     e20:	48 89 f1             	mov    %rsi,%rcx
     e23:	48 8d b1 96 01 00 00 	lea    0x196(%rcx),%rsi
     e2a:	49 39 f0             	cmp    %rsi,%r8
     e2d:	72 15                	jb     e44 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x104>
     e2f:	0f 18 00             	prefetchnta (%rax)
     e32:	0f 18 40 40          	prefetchnta 0x40(%rax)
     e36:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
     e3d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
     e44:	44 8b a8 0c fc ff ff 	mov    -0x3f4(%rax),%r13d
     e4b:	44 8b b8 12 fc ff ff 	mov    -0x3ee(%rax),%r15d
     e52:	44 8b a0 0f fc ff ff 	mov    -0x3f1(%rax),%r12d
     e59:	44 8b b0 15 fc ff ff 	mov    -0x3eb(%rax),%r14d
     e60:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     e67:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     e6e:	44 8b 90 00 fc ff ff 	mov    -0x400(%rax),%r10d
     e75:	8b 98 06 fc ff ff    	mov    -0x3fa(%rax),%ebx
     e7b:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
     e81:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
     e87:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     e8e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     e95:	8b b0 03 fc ff ff    	mov    -0x3fd(%rax),%esi
     e9b:	44 8b 98 09 fc ff ff 	mov    -0x3f7(%rax),%r11d
     ea2:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     ea9:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     eaf:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
     eb6:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
     ebd:	c4 21 79 6e 0c 97    	vmovd  (%rdi,%r10,4),%xmm9
     ec3:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     ec9:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     ed0:	44 8b a8 24 fc ff ff 	mov    -0x3dc(%rax),%r13d
     ed7:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     edb:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
     ee0:	44 8b b8 2a fc ff ff 	mov    -0x3d6(%rax),%r15d
     ee7:	c4 63 31 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm9,%xmm9
     eee:	44 8b a0 27 fc ff ff 	mov    -0x3d9(%rax),%r12d
     ef5:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     efc:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
     f03:	44 8b b0 2d fc ff ff 	mov    -0x3d3(%rax),%r14d
     f0a:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     f11:	44 8b 90 18 fc ff ff 	mov    -0x3e8(%rax),%r10d
     f18:	8b 98 1e fc ff ff    	mov    -0x3e2(%rax),%ebx
     f1e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     f25:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     f29:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
     f2f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     f36:	8b b0 1b fc ff ff    	mov    -0x3e5(%rax),%esi
     f3c:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     f42:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
     f48:	44 8b 98 21 fc ff ff 	mov    -0x3df(%rax),%r11d
     f4f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     f56:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
     f5d:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     f63:	c4 a1 79 6e 34 97    	vmovd  (%rdi,%r10,4),%xmm6
     f69:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     f6f:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
     f76:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     f7d:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     f82:	c4 e3 49 22 34 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm6,%xmm6
     f89:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     f8e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     f92:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
     f97:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
     f9e:	44 8b 90 30 fc ff ff 	mov    -0x3d0(%rax),%r10d
     fa5:	44 8b a8 3c fc ff ff 	mov    -0x3c4(%rax),%r13d
     fac:	44 8b b8 42 fc ff ff 	mov    -0x3be(%rax),%r15d
     fb3:	44 8b a0 3f fc ff ff 	mov    -0x3c1(%rax),%r12d
     fba:	44 8b b0 45 fc ff ff 	mov    -0x3bb(%rax),%r14d
     fc1:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     fc5:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     fcc:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     fd3:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     fda:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     fe0:	8b 98 36 fc ff ff    	mov    -0x3ca(%rax),%ebx
     fe6:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
     fec:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
     ff2:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     ff9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1000:	8b b0 33 fc ff ff    	mov    -0x3cd(%rax),%esi
    1006:	44 8b 98 39 fc ff ff 	mov    -0x3c7(%rax),%r11d
    100d:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1013:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1018:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    101f:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    1026:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    102b:	c4 a1 79 6e 2c 97    	vmovd  (%rdi,%r10,4),%xmm5
    1031:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1037:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    103e:	44 8b a8 54 fc ff ff 	mov    -0x3ac(%rax),%r13d
    1045:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1049:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    104e:	44 8b b8 5a fc ff ff 	mov    -0x3a6(%rax),%r15d
    1055:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    1059:	c4 e3 51 22 2c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm5,%xmm5
    1060:	44 8b a0 57 fc ff ff 	mov    -0x3a9(%rax),%r12d
    1067:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    106e:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1074:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    107b:	44 8b b0 5d fc ff ff 	mov    -0x3a3(%rax),%r14d
    1082:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    1088:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    108f:	44 8b 90 48 fc ff ff 	mov    -0x3b8(%rax),%r10d
    1096:	8b 98 4e fc ff ff    	mov    -0x3b2(%rax),%ebx
    109c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    10a3:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    10a7:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    10ad:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    10b4:	8b b0 4b fc ff ff    	mov    -0x3b5(%rax),%esi
    10ba:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    10c0:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    10c6:	44 8b 98 51 fc ff ff 	mov    -0x3af(%rax),%r11d
    10cd:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    10d4:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    10db:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    10e1:	c4 21 79 6e 04 97    	vmovd  (%rdi,%r10,4),%xmm8
    10e7:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    10ed:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    10f4:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    10fb:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1100:	c4 63 39 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm8,%xmm8
    1107:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    110c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1110:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    1115:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    1119:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    111f:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    1125:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    112c:	44 8b 90 60 fc ff ff 	mov    -0x3a0(%rax),%r10d
    1133:	44 8b a8 6c fc ff ff 	mov    -0x394(%rax),%r13d
    113a:	44 8b b8 72 fc ff ff 	mov    -0x38e(%rax),%r15d
    1141:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1148:	44 8b a0 6f fc ff ff 	mov    -0x391(%rax),%r12d
    114f:	44 8b b0 75 fc ff ff 	mov    -0x38b(%rax),%r14d
    1156:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    115a:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1161:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1168:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    116e:	8b 98 66 fc ff ff    	mov    -0x39a(%rax),%ebx
    1174:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    117a:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    1180:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1187:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    118e:	8b b0 63 fc ff ff    	mov    -0x39d(%rax),%esi
    1194:	44 8b 98 69 fc ff ff 	mov    -0x397(%rax),%r11d
    119b:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    11a1:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    11a6:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    11ad:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    11b4:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    11b9:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
    11bf:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    11c5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    11cc:	44 8b a8 84 fc ff ff 	mov    -0x37c(%rax),%r13d
    11d3:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    11d7:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    11dc:	44 8b b8 8a fc ff ff 	mov    -0x376(%rax),%r15d
    11e3:	c4 e3 41 22 3c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm7,%xmm7
    11ea:	44 8b a0 87 fc ff ff 	mov    -0x379(%rax),%r12d
    11f1:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    11f8:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    11ff:	44 8b b0 8d fc ff ff 	mov    -0x373(%rax),%r14d
    1206:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    120d:	44 8b 90 78 fc ff ff 	mov    -0x388(%rax),%r10d
    1214:	8b 98 7e fc ff ff    	mov    -0x382(%rax),%ebx
    121a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1221:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    1225:	c4 a1 79 6e 0c af    	vmovd  (%rdi,%r13,4),%xmm1
    122b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1232:	8b b0 7b fc ff ff    	mov    -0x385(%rax),%esi
    1238:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    123e:	c4 a1 79 6e 04 bf    	vmovd  (%rdi,%r15,4),%xmm0
    1244:	44 8b 98 81 fc ff ff 	mov    -0x37f(%rax),%r11d
    124b:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1252:	c4 a3 71 22 0c a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm1,%xmm1
    1259:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    125f:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    1264:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    126a:	c4 a3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm0,%xmm0
    1271:	c5 f9 6e 14 9f       	vmovd  (%rdi,%rbx,4),%xmm2
    1276:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    127d:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    1282:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
    1286:	c4 a1 79 6e 04 97    	vmovd  (%rdi,%r10,4),%xmm0
    128c:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
    1293:	c4 e3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm0,%xmm0
    129a:	44 8b 90 90 fc ff ff 	mov    -0x370(%rax),%r10d
    12a1:	44 8b a8 9c fc ff ff 	mov    -0x364(%rax),%r13d
    12a8:	44 8b b8 a2 fc ff ff 	mov    -0x35e(%rax),%r15d
    12af:	44 8b a0 9f fc ff ff 	mov    -0x361(%rax),%r12d
    12b6:	44 8b b0 a5 fc ff ff 	mov    -0x35b(%rax),%r14d
    12bd:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    12c1:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    12c8:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    12cf:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    12d6:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    12dc:	8b 98 96 fc ff ff    	mov    -0x36a(%rax),%ebx
    12e2:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    12e8:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    12ee:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    12f5:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    12fc:	8b b0 93 fc ff ff    	mov    -0x36d(%rax),%esi
    1302:	44 8b 98 99 fc ff ff 	mov    -0x367(%rax),%r11d
    1309:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    130f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1314:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    131b:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    1322:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1327:	c5 79 6e 14 9f       	vmovd  (%rdi,%rbx,4),%xmm10
    132c:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1332:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1339:	44 8b a8 b4 fc ff ff 	mov    -0x34c(%rax),%r13d
    1340:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
    1344:	c4 a1 79 6e 0c 97    	vmovd  (%rdi,%r10,4),%xmm1
    134a:	44 8b b8 ba fc ff ff 	mov    -0x346(%rax),%r15d
    1351:	c4 23 29 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm10,%xmm10
    1358:	44 8b a0 b7 fc ff ff 	mov    -0x349(%rax),%r12d
    135f:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1366:	c4 e3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm1,%xmm1
    136d:	44 8b b0 bd fc ff ff 	mov    -0x343(%rax),%r14d
    1374:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    137b:	44 8b 90 a8 fc ff ff 	mov    -0x358(%rax),%r10d
    1382:	8b 98 ae fc ff ff    	mov    -0x352(%rax),%ebx
    1388:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    138f:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1394:	c4 21 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm10
    139a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    13a1:	8b b0 ab fc ff ff    	mov    -0x355(%rax),%esi
    13a7:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    13ad:	c4 a1 79 6e 14 bf    	vmovd  (%rdi,%r15,4),%xmm2
    13b3:	44 8b 98 b1 fc ff ff 	mov    -0x34f(%rax),%r11d
    13ba:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    13c1:	c4 23 29 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm10,%xmm10
    13c8:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    13ce:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    13d3:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    13d9:	c4 a3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm2,%xmm2
    13e0:	c5 79 6e 1c 9f       	vmovd  (%rdi,%rbx,4),%xmm11
    13e5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    13ec:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    13f1:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    13f8:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
    13fc:	c4 a1 79 6e 14 97    	vmovd  (%rdi,%r10,4),%xmm2
    1402:	c4 23 21 22 1c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm11,%xmm11
    1409:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1410:	c4 e3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm2,%xmm2
    1417:	48 8d 71 40          	lea    0x40(%rcx),%rsi
    141b:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    1420:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    1425:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    142b:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    1431:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    1436:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    143c:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    1442:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1447:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    144c:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    1451:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1456:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    145c:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    1462:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
    1469:	ff 
    146a:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    146e:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    1472:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
    1479:	ff 
    147a:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
    147f:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1483:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    1487:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    148d:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1493:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1499:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    149f:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    14a4:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    14a8:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    14ae:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    14b4:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    14ba:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    14c0:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    14c6:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
    14cb:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    14d0:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
    14d5:	48 05 c0 00 00 00    	add    $0xc0,%rax
    14db:	4d 39 d0             	cmp    %r10,%r8
    14de:	0f 83 3c f9 ff ff    	jae    e20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe0>
    14e4:	0f ae f8             	sfence
    14e7:	48 8d 41 68          	lea    0x68(%rcx),%rax
    14eb:	49 39 c0             	cmp    %rax,%r8
    14ee:	0f 82 16 03 00 00    	jb     180a <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaca>
    14f4:	48 8d 14 76          	lea    (%rsi,%rsi,2),%rdx
    14f8:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1500 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7c0>
    14ff:	00 
    1500:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1508 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7c8>
    1507:	00 
    1508:	49 8d 04 11          	lea    (%r9,%rdx,1),%rax
    150c:	48 03 54 24 f8       	add    -0x8(%rsp),%rdx
    1511:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1518:	44 8b 68 54          	mov    0x54(%rax),%r13d
    151c:	44 8b 78 5a          	mov    0x5a(%rax),%r15d
    1520:	44 8b 60 57          	mov    0x57(%rax),%r12d
    1524:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
    1528:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    152f:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1536:	44 8b 50 48          	mov    0x48(%rax),%r10d
    153a:	8b 58 4e             	mov    0x4e(%rax),%ebx
    153d:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    1543:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    1549:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1550:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1557:	8b 48 4b             	mov    0x4b(%rax),%ecx
    155a:	44 8b 58 51          	mov    0x51(%rax),%r11d
    155e:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1565:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    156b:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    1572:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    1579:	c4 a1 79 6e 2c 97    	vmovd  (%rdi,%r10,4),%xmm5
    157f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1585:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    158c:	44 8b 68 3c          	mov    0x3c(%rax),%r13d
    1590:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1594:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    1599:	44 8b 78 42          	mov    0x42(%rax),%r15d
    159d:	c4 e3 51 22 2c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm5,%xmm5
    15a4:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
    15a8:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    15af:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    15b6:	44 8b 70 45          	mov    0x45(%rax),%r14d
    15ba:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    15c1:	44 8b 50 30          	mov    0x30(%rax),%r10d
    15c5:	8b 58 36             	mov    0x36(%rax),%ebx
    15c8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    15cf:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    15d3:	c4 a1 79 6e 0c af    	vmovd  (%rdi,%r13,4),%xmm1
    15d9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    15e0:	8b 48 33             	mov    0x33(%rax),%ecx
    15e3:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    15e9:	c4 a1 79 6e 04 bf    	vmovd  (%rdi,%r15,4),%xmm0
    15ef:	44 8b 58 39          	mov    0x39(%rax),%r11d
    15f3:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    15fa:	c4 a3 71 22 0c a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm1,%xmm1
    1601:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1607:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    160c:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1612:	c4 a3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm0,%xmm0
    1619:	c5 f9 6e 14 9f       	vmovd  (%rdi,%rbx,4),%xmm2
    161e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1625:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    162a:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
    162e:	c4 a1 79 6e 04 97    	vmovd  (%rdi,%r10,4),%xmm0
    1634:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
    163b:	c4 e3 79 22 04 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm0,%xmm0
    1642:	44 8b 50 18          	mov    0x18(%rax),%r10d
    1646:	44 8b 68 24          	mov    0x24(%rax),%r13d
    164a:	44 8b 78 2a          	mov    0x2a(%rax),%r15d
    164e:	44 8b 60 27          	mov    0x27(%rax),%r12d
    1652:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
    1656:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    165a:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1661:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1668:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    166f:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1675:	8b 58 1e             	mov    0x1e(%rax),%ebx
    1678:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    167e:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    1684:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    168b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1692:	8b 48 1b             	mov    0x1b(%rax),%ecx
    1695:	44 8b 58 21          	mov    0x21(%rax),%r11d
    1699:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    169f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    16a4:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    16ab:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    16b2:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    16b7:	c5 f9 6e 34 9f       	vmovd  (%rdi,%rbx,4),%xmm6
    16bc:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    16c2:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    16c9:	44 8b 68 0c          	mov    0xc(%rax),%r13d
    16cd:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
    16d1:	c4 a1 79 6e 0c 97    	vmovd  (%rdi,%r10,4),%xmm1
    16d7:	44 8b 78 12          	mov    0x12(%rax),%r15d
    16db:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    16df:	c4 a3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm6,%xmm6
    16e6:	44 8b 60 0f          	mov    0xf(%rax),%r12d
    16ea:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    16f1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    16f7:	c4 e3 71 22 0c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm1,%xmm1
    16fe:	44 8b 70 15          	mov    0x15(%rax),%r14d
    1702:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1709:	44 8b 10             	mov    (%rax),%r10d
    170c:	8b 58 06             	mov    0x6(%rax),%ebx
    170f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1716:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    171a:	c4 a1 79 6e 34 af    	vmovd  (%rdi,%r13,4),%xmm6
    1720:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1727:	8b 48 03             	mov    0x3(%rax),%ecx
    172a:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1730:	c4 a1 79 6e 14 bf    	vmovd  (%rdi,%r15,4),%xmm2
    1736:	44 8b 58 09          	mov    0x9(%rax),%r11d
    173a:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1741:	c4 a3 49 22 34 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm6,%xmm6
    1748:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    174e:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1753:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1759:	c4 a3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm2,%xmm2
    1760:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    1765:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    176c:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1771:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1775:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    177b:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
    177f:	c4 a1 79 6e 14 97    	vmovd  (%rdi,%r10,4),%xmm2
    1785:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    178b:	c4 a3 41 22 3c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm7,%xmm7
    1792:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1798:	c4 e3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm2,%xmm2
    179f:	48 8d 4e 48          	lea    0x48(%rsi),%rcx
    17a3:	48 83 c6 20          	add    $0x20,%rsi
    17a7:	48 83 c0 60          	add    $0x60,%rax
    17ab:	48 83 c2 60          	add    $0x60,%rdx
    17af:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    17b3:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    17b7:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    17bd:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    17c3:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    17c9:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    17cd:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    17d2:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    17d8:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    17dd:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    17e1:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    17e7:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    17ec:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    17f2:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    17f7:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    17fc:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1801:	49 39 c8             	cmp    %rcx,%r8
    1804:	0f 83 0e fd ff ff    	jae    1518 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7d8>
    180a:	48 8d 5e 08          	lea    0x8(%rsi),%rbx
    180e:	49 39 d8             	cmp    %rbx,%r8
    1811:	0f 82 0b 01 00 00    	jb     1922 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbe2>
    1817:	4c 8d 1c 76          	lea    (%rsi,%rsi,2),%r11
    181b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1823 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xae3>
    1822:	00 
    1823:	4f 8d 14 19          	lea    (%r9,%r11,1),%r10
    1827:	4c 03 5c 24 f8       	add    -0x8(%rsp),%r11
    182c:	0f 1f 40 00          	nopl   0x0(%rax)
    1830:	49 8b 42 08          	mov    0x8(%r10),%rax
    1834:	49 8b 12             	mov    (%r10),%rdx
    1837:	49 83 c3 18          	add    $0x18,%r11
    183b:	49 83 c2 18          	add    $0x18,%r10
    183f:	49 8b 4a f8          	mov    -0x8(%r10),%rcx
    1843:	41 89 c4             	mov    %eax,%r12d
    1846:	49 89 d5             	mov    %rdx,%r13
    1849:	48 89 d6             	mov    %rdx,%rsi
    184c:	48 c1 ea 30          	shr    $0x30,%rdx
    1850:	41 c1 e4 10          	shl    $0x10,%r12d
    1854:	41 89 cf             	mov    %ecx,%r15d
    1857:	41 89 c6             	mov    %eax,%r14d
    185a:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1861:	41 c1 e7 08          	shl    $0x8,%r15d
    1865:	44 09 e2             	or     %r12d,%edx
    1868:	49 89 c4             	mov    %rax,%r12
    186b:	48 c1 e8 38          	shr    $0x38,%rax
    186f:	49 c1 ec 20          	shr    $0x20,%r12
    1873:	44 09 f8             	or     %r15d,%eax
    1876:	49 89 cf             	mov    %rcx,%r15
    1879:	48 c1 e9 28          	shr    $0x28,%rcx
    187d:	49 c1 ef 10          	shr    $0x10,%r15
    1881:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1888:	25 ff ff ff 00       	and    $0xffffff,%eax
    188d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    1893:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    189a:	c4 a1 79 6e 0c a7    	vmovd  (%rdi,%r12,4),%xmm1
    18a0:	c5 f9 6e 14 97       	vmovd  (%rdi,%rdx,4),%xmm2
    18a5:	48 c1 ee 18          	shr    $0x18,%rsi
    18a9:	c4 a1 79 6e 04 bf    	vmovd  (%rdi,%r15,4),%xmm0
    18af:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    18b5:	41 c1 ee 08          	shr    $0x8,%r14d
    18b9:	c4 e3 71 22 0c 87 01 	vpinsrd $0x1,(%rdi,%rax,4),%xmm1,%xmm1
    18c0:	c4 a3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm2,%xmm2
    18c7:	c4 e3 79 22 04 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm0,%xmm0
    18ce:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
    18d2:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    18d8:	c4 e3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm0,%xmm0
    18df:	48 89 de             	mov    %rbx,%rsi
    18e2:	48 83 c3 08          	add    $0x8,%rbx
    18e6:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    18ea:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    18f0:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    18f5:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    18f9:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    18ff:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    1904:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1909:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    190d:	c4 c1 79 d6 43 f8    	vmovq  %xmm0,-0x8(%r11)
    1913:	c4 c1 7a 7f 4b e8    	vmovdqu %xmm1,-0x18(%r11)
    1919:	49 39 d8             	cmp    %rbx,%r8
    191c:	0f 83 0e ff ff ff    	jae    1830 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaf0>
    1922:	4c 39 c6             	cmp    %r8,%rsi
    1925:	0f 83 f5 01 00 00    	jae    1b20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde0>
    192b:	48 8d 04 76          	lea    (%rsi,%rsi,2),%rax
    192f:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1934:	4d 8d 14 01          	lea    (%r9,%rax,1),%r10
    1938:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    193d:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1942:	45 0f b6 12          	movzbl (%r10),%r10d
    1946:	c1 e2 08             	shl    $0x8,%edx
    1949:	41 c1 e3 10          	shl    $0x10,%r11d
    194d:	44 09 da             	or     %r11d,%edx
    1950:	44 09 d2             	or     %r10d,%edx
    1953:	4c 8d 14 97          	lea    (%rdi,%rdx,4),%r10
    1957:	41 8b 12             	mov    (%r10),%edx
    195a:	45 0f b7 12          	movzwl (%r10),%r10d
    195e:	c1 ea 10             	shr    $0x10,%edx
    1961:	66 44 89 14 03       	mov    %r10w,(%rbx,%rax,1)
    1966:	88 54 03 02          	mov    %dl,0x2(%rbx,%rax,1)
    196a:	48 8d 56 01          	lea    0x1(%rsi),%rdx
    196e:	4c 39 c2             	cmp    %r8,%rdx
    1971:	0f 83 a9 01 00 00    	jae    1b20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde0>
    1977:	4d 8d 54 01 03       	lea    0x3(%r9,%rax,1),%r10
    197c:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1981:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1986:	45 0f b6 12          	movzbl (%r10),%r10d
    198a:	41 c1 e3 10          	shl    $0x10,%r11d
    198e:	c1 e2 08             	shl    $0x8,%edx
    1991:	44 09 da             	or     %r11d,%edx
    1994:	44 09 d2             	or     %r10d,%edx
    1997:	48 8d 14 97          	lea    (%rdi,%rdx,4),%rdx
    199b:	44 8b 12             	mov    (%rdx),%r10d
    199e:	44 0f b7 1a          	movzwl (%rdx),%r11d
    19a2:	48 8d 56 02          	lea    0x2(%rsi),%rdx
    19a6:	44 89 d1             	mov    %r10d,%ecx
    19a9:	66 44 89 5c 03 03    	mov    %r11w,0x3(%rbx,%rax,1)
    19af:	c1 e9 10             	shr    $0x10,%ecx
    19b2:	88 4c 03 05          	mov    %cl,0x5(%rbx,%rax,1)
    19b6:	4c 39 c2             	cmp    %r8,%rdx
    19b9:	0f 83 61 01 00 00    	jae    1b20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde0>
    19bf:	4d 8d 54 01 06       	lea    0x6(%r9,%rax,1),%r10
    19c4:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    19c9:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    19ce:	45 0f b6 12          	movzbl (%r10),%r10d
    19d2:	41 c1 e3 10          	shl    $0x10,%r11d
    19d6:	c1 e2 08             	shl    $0x8,%edx
    19d9:	44 09 da             	or     %r11d,%edx
    19dc:	44 09 d2             	or     %r10d,%edx
    19df:	48 8d 14 97          	lea    (%rdi,%rdx,4),%rdx
    19e3:	44 8b 12             	mov    (%rdx),%r10d
    19e6:	44 0f b7 1a          	movzwl (%rdx),%r11d
    19ea:	48 8d 56 03          	lea    0x3(%rsi),%rdx
    19ee:	44 89 d1             	mov    %r10d,%ecx
    19f1:	66 44 89 5c 03 06    	mov    %r11w,0x6(%rbx,%rax,1)
    19f7:	c1 e9 10             	shr    $0x10,%ecx
    19fa:	88 4c 03 08          	mov    %cl,0x8(%rbx,%rax,1)
    19fe:	4c 39 c2             	cmp    %r8,%rdx
    1a01:	0f 83 19 01 00 00    	jae    1b20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde0>
    1a07:	4d 8d 54 01 09       	lea    0x9(%r9,%rax,1),%r10
    1a0c:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1a11:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1a16:	45 0f b6 12          	movzbl (%r10),%r10d
    1a1a:	41 c1 e3 08          	shl    $0x8,%r11d
    1a1e:	c1 e2 10             	shl    $0x10,%edx
    1a21:	44 09 da             	or     %r11d,%edx
    1a24:	44 09 d2             	or     %r10d,%edx
    1a27:	48 8d 14 97          	lea    (%rdi,%rdx,4),%rdx
    1a2b:	44 8b 12             	mov    (%rdx),%r10d
    1a2e:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1a32:	48 8d 56 04          	lea    0x4(%rsi),%rdx
    1a36:	44 89 d1             	mov    %r10d,%ecx
    1a39:	66 44 89 5c 03 09    	mov    %r11w,0x9(%rbx,%rax,1)
    1a3f:	c1 e9 10             	shr    $0x10,%ecx
    1a42:	88 4c 03 0b          	mov    %cl,0xb(%rbx,%rax,1)
    1a46:	4c 39 c2             	cmp    %r8,%rdx
    1a49:	0f 83 d1 00 00 00    	jae    1b20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde0>
    1a4f:	4d 8d 54 01 0c       	lea    0xc(%r9,%rax,1),%r10
    1a54:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1a59:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1a5e:	45 0f b6 12          	movzbl (%r10),%r10d
    1a62:	41 c1 e3 08          	shl    $0x8,%r11d
    1a66:	c1 e2 10             	shl    $0x10,%edx
    1a69:	44 09 da             	or     %r11d,%edx
    1a6c:	44 09 d2             	or     %r10d,%edx
    1a6f:	48 8d 14 97          	lea    (%rdi,%rdx,4),%rdx
    1a73:	44 8b 12             	mov    (%rdx),%r10d
    1a76:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1a7a:	48 8d 56 05          	lea    0x5(%rsi),%rdx
    1a7e:	44 89 d1             	mov    %r10d,%ecx
    1a81:	66 44 89 5c 03 0c    	mov    %r11w,0xc(%rbx,%rax,1)
    1a87:	c1 e9 10             	shr    $0x10,%ecx
    1a8a:	88 4c 03 0e          	mov    %cl,0xe(%rbx,%rax,1)
    1a8e:	4c 39 c2             	cmp    %r8,%rdx
    1a91:	0f 83 89 00 00 00    	jae    1b20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde0>
    1a97:	4d 8d 54 01 0f       	lea    0xf(%r9,%rax,1),%r10
    1a9c:	48 83 c6 06          	add    $0x6,%rsi
    1aa0:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1aa5:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1aaa:	45 0f b6 12          	movzbl (%r10),%r10d
    1aae:	41 c1 e3 08          	shl    $0x8,%r11d
    1ab2:	c1 e2 10             	shl    $0x10,%edx
    1ab5:	44 09 da             	or     %r11d,%edx
    1ab8:	44 09 d2             	or     %r10d,%edx
    1abb:	48 8d 14 97          	lea    (%rdi,%rdx,4),%rdx
    1abf:	44 8b 12             	mov    (%rdx),%r10d
    1ac2:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1ac6:	44 89 d1             	mov    %r10d,%ecx
    1ac9:	66 44 89 5c 03 0f    	mov    %r11w,0xf(%rbx,%rax,1)
    1acf:	c1 e9 10             	shr    $0x10,%ecx
    1ad2:	88 4c 03 11          	mov    %cl,0x11(%rbx,%rax,1)
    1ad6:	4c 39 c6             	cmp    %r8,%rsi
    1ad9:	73 45                	jae    1b20 <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde0>
    1adb:	49 8d 54 01 12       	lea    0x12(%r9,%rax,1),%rdx
    1ae0:	48 8d 74 03 12       	lea    0x12(%rbx,%rax,1),%rsi
    1ae5:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1ae9:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1aed:	0f b6 12             	movzbl (%rdx),%edx
    1af0:	c1 e0 08             	shl    $0x8,%eax
    1af3:	c1 e1 10             	shl    $0x10,%ecx
    1af6:	09 c8                	or     %ecx,%eax
    1af8:	09 d0                	or     %edx,%eax
    1afa:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    1afe:	8b 02                	mov    (%rdx),%eax
    1b00:	0f b7 12             	movzwl (%rdx),%edx
    1b03:	c1 e8 10             	shr    $0x10,%eax
    1b06:	66 89 16             	mov    %dx,(%rsi)
    1b09:	88 46 02             	mov    %al,0x2(%rsi)
    1b0c:	c5 f8 77             	vzeroupper
    1b0f:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1b13:	5b                   	pop    %rbx
    1b14:	41 5c                	pop    %r12
    1b16:	41 5d                	pop    %r13
    1b18:	41 5e                	pop    %r14
    1b1a:	41 5f                	pop    %r15
    1b1c:	5d                   	pop    %rbp
    1b1d:	c3                   	ret
    1b1e:	66 90                	xchg   %ax,%ax
    1b20:	c5 f8 77             	vzeroupper
    1b23:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1b27:	5b                   	pop    %rbx
    1b28:	41 5c                	pop    %r12
    1b2a:	41 5d                	pop    %r13
    1b2c:	41 5e                	pop    %r14
    1b2e:	41 5f                	pop    %r15
    1b30:	5d                   	pop    %rbp
    1b31:	c3                   	ret
    1b32:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1b38:	4c 89 c6             	mov    %r8,%rsi
    1b3b:	e9 ca fc ff ff       	jmp    180a <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaca>
    1b40:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1b44:	48 89 ce             	mov    %rcx,%rsi
    1b47:	e9 9f f9 ff ff       	jmp    14eb <jshc_channel::avx2_chain_raw32_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7ab>
