
artifacts/skylake-clangload-linux-build-v1/CMakeFiles/jshc_skylake_clangload.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	41 57                	push   %r15
       2:	41 56                	push   %r14
       4:	41 55                	push   %r13
       6:	41 54                	push   %r12
       8:	53                   	push   %rbx
       9:	4c 8d 04 49          	lea    (%rcx,%rcx,2),%r8
       d:	49 81 f8 00 04 00 00 	cmp    $0x400,%r8
      14:	b8 00 04 00 00       	mov    $0x400,%eax
      19:	49 0f 42 c0          	cmovb  %r8,%rax
      1d:	48 85 c9             	test   %rcx,%rcx
      20:	0f 84 26 04 00 00    	je     44c <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x44c>
      26:	45 31 c0             	xor    %r8d,%r8d
      29:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
      30:	42 0f 18 04 02       	prefetchnta (%rdx,%r8,1)
      35:	49 83 c0 40          	add    $0x40,%r8
      39:	49 39 c0             	cmp    %rax,%r8
      3c:	72 f2                	jb     30 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3e:	8d 04 92             	lea    (%rdx,%rdx,4),%eax
      41:	44 8d 34 82          	lea    (%rdx,%rax,4),%r14d
      45:	41 83 e6 3f          	and    $0x3f,%r14d
      49:	48 8d 5a 02          	lea    0x2(%rdx),%rbx
      4d:	45 31 c0             	xor    %r8d,%r8d
      50:	4d 39 c6             	cmp    %r8,%r14
      53:	74 3f                	je     94 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x94>
      55:	44 0f b6 4b fe       	movzbl -0x2(%rbx),%r9d
      5a:	44 0f b6 53 ff       	movzbl -0x1(%rbx),%r10d
      5f:	41 c1 e2 08          	shl    $0x8,%r10d
      63:	44 0f b6 1b          	movzbl (%rbx),%r11d
      67:	41 c1 e3 10          	shl    $0x10,%r11d
      6b:	49 01 f9             	add    %rdi,%r9
      6e:	4d 01 d1             	add    %r10,%r9
      71:	47 0f b6 0c 0b       	movzbl (%r11,%r9,1),%r9d
      76:	42 8b 04 8e          	mov    (%rsi,%r9,4),%eax
      7a:	88 43 fe             	mov    %al,-0x2(%rbx)
      7d:	88 63 ff             	mov    %ah,-0x1(%rbx)
      80:	c1 e8 10             	shr    $0x10,%eax
      83:	88 03                	mov    %al,(%rbx)
      85:	49 ff c0             	inc    %r8
      88:	48 83 c3 03          	add    $0x3,%rbx
      8c:	4c 39 c1             	cmp    %r8,%rcx
      8f:	75 bf                	jne    50 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x50>
      91:	49 89 ce             	mov    %rcx,%r14
      94:	49 8d 46 48          	lea    0x48(%r14),%rax
      98:	48 39 c8             	cmp    %rcx,%rax
      9b:	0f 86 bb 03 00 00    	jbe    45c <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x45c>
      a1:	4d 89 f1             	mov    %r14,%r9
      a4:	49 8d 41 28          	lea    0x28(%r9),%rax
      a8:	48 39 c8             	cmp    %rcx,%rax
      ab:	0f 87 c0 0a 00 00    	ja     b71 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb71>
      b1:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      b5:	48 01 d0             	add    %rdx,%rax
      b8:	c4 e2 7d 5a 05 00 00 	vbroadcasti128 0x0(%rip),%ymm0        # c1 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc1>
      bf:	00 00 
      c1:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # c9 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc9>
      c8:	00 
      c9:	c5 f9 6f 15 00 00 00 	vmovdqa 0x0(%rip),%xmm2        # d1 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd1>
      d0:	00 
      d1:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
      d8:	0f 1f 84 00 00 00 00 
      df:	00 
      e0:	44 8b 00             	mov    (%rax),%r8d
      e3:	44 8b 50 03          	mov    0x3(%rax),%r10d
      e7:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
      ee:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
      f3:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
      fa:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
      ff:	44 8b 58 06          	mov    0x6(%rax),%r11d
     103:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     10a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     10f:	8b 58 09             	mov    0x9(%rax),%ebx
     112:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     118:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     11c:	44 8b 70 0c          	mov    0xc(%rax),%r14d
     120:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     127:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     12c:	44 8b 78 0f          	mov    0xf(%rax),%r15d
     130:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     137:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     13c:	44 8b 60 12          	mov    0x12(%rax),%r12d
     140:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     147:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     14c:	44 8b 68 15          	mov    0x15(%rax),%r13d
     150:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     157:	c4 a1 79 6e 1c b6    	vmovd  (%rsi,%r14,4),%xmm3
     15d:	c4 a3 61 22 1c be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm3,%xmm3
     164:	46 0f b6 34 2f       	movzbl (%rdi,%r13,1),%r14d
     169:	c4 a3 61 22 1c a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm3,%xmm3
     170:	c4 a3 61 22 1c b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm3,%xmm3
     177:	c4 a1 79 6e 24 86    	vmovd  (%rsi,%r8,4),%xmm4
     17d:	c4 a3 59 22 24 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm4,%xmm4
     184:	c4 a3 59 22 24 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm4,%xmm4
     18b:	c4 e3 59 22 24 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm4,%xmm4
     192:	c4 e3 5d 38 db 01    	vinserti128 $0x1,%xmm3,%ymm4,%ymm3
     198:	44 8b 40 18          	mov    0x18(%rax),%r8d
     19c:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1a3:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     1a8:	44 8b 50 1b          	mov    0x1b(%rax),%r10d
     1ac:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     1b3:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     1b8:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
     1bc:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     1c3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     1c8:	8b 58 21             	mov    0x21(%rax),%ebx
     1cb:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     1d1:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     1d5:	44 8b 70 24          	mov    0x24(%rax),%r14d
     1d9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     1e0:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     1e5:	44 8b 78 27          	mov    0x27(%rax),%r15d
     1e9:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     1f0:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     1f5:	44 8b 60 2a          	mov    0x2a(%rax),%r12d
     1f9:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     200:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     205:	44 8b 68 2d          	mov    0x2d(%rax),%r13d
     209:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     210:	c4 a1 79 6e 24 b6    	vmovd  (%rsi,%r14,4),%xmm4
     216:	c4 a3 59 22 24 be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm4,%xmm4
     21d:	c4 a3 59 22 24 a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm4,%xmm4
     224:	46 0f b6 34 2f       	movzbl (%rdi,%r13,1),%r14d
     229:	c4 a3 59 22 24 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm4,%xmm4
     230:	c4 a1 79 6e 2c 86    	vmovd  (%rsi,%r8,4),%xmm5
     236:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
     23d:	c4 a3 51 22 2c 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm5,%xmm5
     244:	c4 e3 51 22 2c 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm5,%xmm5
     24b:	44 8b 40 30          	mov    0x30(%rax),%r8d
     24f:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     256:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     25b:	44 8b 50 33          	mov    0x33(%rax),%r10d
     25f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     266:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     26b:	44 8b 58 36          	mov    0x36(%rax),%r11d
     26f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     276:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     27b:	8b 58 39             	mov    0x39(%rax),%ebx
     27e:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     284:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     288:	44 8b 70 3c          	mov    0x3c(%rax),%r14d
     28c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     293:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     298:	44 8b 78 3f          	mov    0x3f(%rax),%r15d
     29c:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     2a3:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     2a8:	44 8b 60 42          	mov    0x42(%rax),%r12d
     2ac:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     2b3:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2b8:	44 8b 68 45          	mov    0x45(%rax),%r13d
     2bc:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     2c3:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
     2c9:	c4 a3 49 22 34 be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm6,%xmm6
     2d0:	46 0f b6 34 2f       	movzbl (%rdi,%r13,1),%r14d
     2d5:	c4 a3 49 22 34 a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm6,%xmm6
     2dc:	c4 a3 49 22 34 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm6,%xmm6
     2e3:	c4 a1 79 6e 3c 86    	vmovd  (%rsi,%r8,4),%xmm7
     2e9:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
     2f0:	c4 a3 41 22 3c 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm7,%xmm7
     2f7:	c4 e3 41 22 3c 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm7,%xmm7
     2fe:	c4 e3 55 38 e4 01    	vinserti128 $0x1,%xmm4,%ymm5,%ymm4
     304:	c4 e3 45 38 ee 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm5
     30a:	44 8b 40 48          	mov    0x48(%rax),%r8d
     30e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     315:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     31a:	44 8b 50 4b          	mov    0x4b(%rax),%r10d
     31e:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     325:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     32a:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     32e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     335:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     33a:	8b 58 51             	mov    0x51(%rax),%ebx
     33d:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     343:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     347:	44 8b 70 54          	mov    0x54(%rax),%r14d
     34b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     352:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     357:	44 8b 78 57          	mov    0x57(%rax),%r15d
     35b:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     362:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     367:	44 8b 60 5a          	mov    0x5a(%rax),%r12d
     36b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     372:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     377:	44 8b 68 5d          	mov    0x5d(%rax),%r13d
     37b:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     382:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
     388:	c4 a3 49 22 34 be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm6,%xmm6
     38f:	c4 a3 49 22 34 a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm6,%xmm6
     396:	46 0f b6 34 2f       	movzbl (%rdi,%r13,1),%r14d
     39b:	c4 a3 49 22 34 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm6,%xmm6
     3a2:	c4 a1 79 6e 3c 86    	vmovd  (%rsi,%r8,4),%xmm7
     3a8:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
     3af:	c4 a3 41 22 3c 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm7,%xmm7
     3b6:	c4 e3 41 22 3c 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm7,%xmm7
     3bd:	c4 e3 45 38 f6 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm6
     3c3:	c4 e2 65 00 d8       	vpshufb %ymm0,%ymm3,%ymm3
     3c8:	c4 e2 75 36 db       	vpermd %ymm3,%ymm1,%ymm3
     3cd:	c4 e2 5d 00 e0       	vpshufb %ymm0,%ymm4,%ymm4
     3d2:	c4 e2 6d 36 fc       	vpermd %ymm4,%ymm2,%ymm7
     3d7:	c4 e2 55 00 e8       	vpshufb %ymm0,%ymm5,%ymm5
     3dc:	c4 e2 75 36 ed       	vpermd %ymm5,%ymm1,%ymm5
     3e1:	c4 e2 4d 00 f0       	vpshufb %ymm0,%ymm6,%ymm6
     3e6:	c4 e2 75 36 f6       	vpermd %ymm6,%ymm1,%ymm6
     3eb:	c4 c3 7d 39 d8 01    	vextracti128 $0x1,%ymm3,%xmm8
     3f1:	c5 b9 6c e4          	vpunpcklqdq %xmm4,%xmm8,%xmm4
     3f5:	c4 e3 65 38 dc 01    	vinserti128 $0x1,%xmm4,%ymm3,%ymm3
     3fb:	c4 e3 45 38 e5 01    	vinserti128 $0x1,%xmm5,%ymm7,%ymm4
     401:	c4 e3 55 46 ee 21    	vperm2i128 $0x21,%ymm6,%ymm5,%ymm5
     407:	c4 e3 fd 00 ed f4    	vpermq $0xf4,%ymm5,%ymm5
     40d:	c5 d5 6c ee          	vpunpcklqdq %ymm6,%ymm5,%ymm5
     411:	c5 fe 7f 18          	vmovdqu %ymm3,(%rax)
     415:	c5 fe 7f 60 20       	vmovdqu %ymm4,0x20(%rax)
     41a:	c5 fe 7f 68 40       	vmovdqu %ymm5,0x40(%rax)
     41f:	4d 8d 41 20          	lea    0x20(%r9),%r8
     423:	49 83 c1 48          	add    $0x48,%r9
     427:	48 83 c0 60          	add    $0x60,%rax
     42b:	49 39 c9             	cmp    %rcx,%r9
     42e:	4d 89 c1             	mov    %r8,%r9
     431:	0f 86 a9 fc ff ff    	jbe    e0 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe0>
     437:	49 8d 40 08          	lea    0x8(%r8),%rax
     43b:	48 39 c8             	cmp    %rcx,%rax
     43e:	0f 86 3d 07 00 00    	jbe    b81 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb81>
     444:	4d 89 c1             	mov    %r8,%r9
     447:	e9 52 08 00 00       	jmp    c9e <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc9e>
     44c:	45 31 f6             	xor    %r14d,%r14d
     44f:	49 8d 46 48          	lea    0x48(%r14),%rax
     453:	48 39 c8             	cmp    %rcx,%rax
     456:	0f 87 45 fc ff ff    	ja     a1 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa1>
     45c:	4f 8d 04 76          	lea    (%r14,%r14,2),%r8
     460:	49 01 d0             	add    %rdx,%r8
     463:	c4 e2 7d 5a 05 00 00 	vbroadcasti128 0x0(%rip),%ymm0        # 46c <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x46c>
     46a:	00 00 
     46c:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 474 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x474>
     473:	00 
     474:	c5 f9 6f 15 00 00 00 	vmovdqa 0x0(%rip),%xmm2        # 47c <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x47c>
     47b:	00 
     47c:	e9 ab 06 00 00       	jmp    b2c <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb2c>
     481:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
     488:	0f 1f 84 00 00 00 00 
     48f:	00 
     490:	41 8b 00             	mov    (%r8),%eax
     493:	45 8b 50 03          	mov    0x3(%r8),%r10d
     497:	25 ff ff ff 00       	and    $0xffffff,%eax
     49c:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     4a1:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     4a8:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     4ad:	41 8b 40 06          	mov    0x6(%r8),%eax
     4b1:	25 ff ff ff 00       	and    $0xffffff,%eax
     4b6:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     4bb:	41 8b 40 09          	mov    0x9(%r8),%eax
     4bf:	25 ff ff ff 00       	and    $0xffffff,%eax
     4c4:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
     4c8:	41 8b 40 0c          	mov    0xc(%r8),%eax
     4cc:	25 ff ff ff 00       	and    $0xffffff,%eax
     4d1:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     4d5:	45 8b 78 0f          	mov    0xf(%r8),%r15d
     4d9:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     4e0:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     4e5:	45 8b 60 12          	mov    0x12(%r8),%r12d
     4e9:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     4f0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     4f5:	45 8b 68 15          	mov    0x15(%r8),%r13d
     4f9:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     500:	c5 f9 6e 1c 86       	vmovd  (%rsi,%rax,4),%xmm3
     505:	c4 a3 61 22 1c be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm3,%xmm3
     50c:	c4 a3 61 22 1c a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm3,%xmm3
     513:	42 0f b6 04 2f       	movzbl (%rdi,%r13,1),%eax
     518:	c4 e3 61 22 1c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm3,%xmm3
     51f:	c4 a1 79 6e 24 8e    	vmovd  (%rsi,%r9,4),%xmm4
     525:	c4 a3 59 22 24 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm4,%xmm4
     52c:	c4 a3 59 22 24 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm4,%xmm4
     533:	c4 e3 59 22 24 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm4,%xmm4
     53a:	c4 e3 5d 38 db 01    	vinserti128 $0x1,%xmm3,%ymm4,%ymm3
     540:	c4 e2 65 00 d8       	vpshufb %ymm0,%ymm3,%ymm3
     545:	c4 e2 75 36 db       	vpermd %ymm3,%ymm1,%ymm3
     54a:	41 8b 40 18          	mov    0x18(%r8),%eax
     54e:	25 ff ff ff 00       	and    $0xffffff,%eax
     553:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     558:	41 8b 40 1b          	mov    0x1b(%r8),%eax
     55c:	25 ff ff ff 00       	and    $0xffffff,%eax
     561:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
     566:	41 8b 40 1e          	mov    0x1e(%r8),%eax
     56a:	25 ff ff ff 00       	and    $0xffffff,%eax
     56f:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     574:	41 8b 58 21          	mov    0x21(%r8),%ebx
     578:	41 8b 40 24          	mov    0x24(%r8),%eax
     57c:	25 ff ff ff 00       	and    $0xffffff,%eax
     581:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     585:	45 8b 78 27          	mov    0x27(%r8),%r15d
     589:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     590:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     595:	45 8b 60 2a          	mov    0x2a(%r8),%r12d
     599:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5a0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     5a5:	45 8b 68 2d          	mov    0x2d(%r8),%r13d
     5a9:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     5b0:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     5b5:	c5 f9 6e 24 86       	vmovd  (%rsi,%rax,4),%xmm4
     5ba:	c4 a3 59 22 24 be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm4,%xmm4
     5c1:	c4 a3 59 22 24 a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm4,%xmm4
     5c8:	c4 a3 59 22 24 ae 03 	vpinsrd $0x3,(%rsi,%r13,4),%xmm4,%xmm4
     5cf:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     5d5:	c4 a1 79 6e 2c 8e    	vmovd  (%rsi,%r9,4),%xmm5
     5db:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
     5e2:	c4 a3 51 22 2c 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm5,%xmm5
     5e9:	0f b6 04 1f          	movzbl (%rdi,%rbx,1),%eax
     5ed:	c4 e3 51 22 2c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm5,%xmm5
     5f4:	c4 e3 55 38 e4 01    	vinserti128 $0x1,%xmm4,%ymm5,%ymm4
     5fa:	c4 e2 5d 00 e8       	vpshufb %ymm0,%ymm4,%ymm5
     5ff:	c4 e2 6d 36 e5       	vpermd %ymm5,%ymm2,%ymm4
     604:	41 8b 40 30          	mov    0x30(%r8),%eax
     608:	25 ff ff ff 00       	and    $0xffffff,%eax
     60d:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     612:	41 8b 40 33          	mov    0x33(%r8),%eax
     616:	25 ff ff ff 00       	and    $0xffffff,%eax
     61b:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
     620:	41 8b 40 36          	mov    0x36(%r8),%eax
     624:	25 ff ff ff 00       	and    $0xffffff,%eax
     629:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     62e:	41 8b 58 39          	mov    0x39(%r8),%ebx
     632:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     638:	41 8b 40 3c          	mov    0x3c(%r8),%eax
     63c:	25 ff ff ff 00       	and    $0xffffff,%eax
     641:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     645:	45 8b 78 3f          	mov    0x3f(%r8),%r15d
     649:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     650:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     655:	45 8b 60 42          	mov    0x42(%r8),%r12d
     659:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     660:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     665:	45 8b 68 45          	mov    0x45(%r8),%r13d
     669:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     670:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     675:	c5 f9 6e 34 86       	vmovd  (%rsi,%rax,4),%xmm6
     67a:	c4 a3 49 22 34 be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm6,%xmm6
     681:	c4 a3 49 22 34 a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm6,%xmm6
     688:	c4 a3 49 22 34 ae 03 	vpinsrd $0x3,(%rsi,%r13,4),%xmm6,%xmm6
     68f:	0f b6 04 1f          	movzbl (%rdi,%rbx,1),%eax
     693:	c4 a1 79 6e 3c 8e    	vmovd  (%rsi,%r9,4),%xmm7
     699:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
     6a0:	c4 a3 41 22 3c 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm7,%xmm7
     6a7:	c4 e3 41 22 3c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm7,%xmm7
     6ae:	c4 e3 45 38 f6 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm6
     6b4:	c4 e2 4d 00 f0       	vpshufb %ymm0,%ymm6,%ymm6
     6b9:	41 8b 40 48          	mov    0x48(%r8),%eax
     6bd:	25 ff ff ff 00       	and    $0xffffff,%eax
     6c2:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     6c7:	41 8b 40 4b          	mov    0x4b(%r8),%eax
     6cb:	25 ff ff ff 00       	and    $0xffffff,%eax
     6d0:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
     6d5:	41 8b 40 4e          	mov    0x4e(%r8),%eax
     6d9:	25 ff ff ff 00       	and    $0xffffff,%eax
     6de:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     6e3:	41 8b 40 51          	mov    0x51(%r8),%eax
     6e7:	25 ff ff ff 00       	and    $0xffffff,%eax
     6ec:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
     6f0:	41 8b 40 54          	mov    0x54(%r8),%eax
     6f4:	25 ff ff ff 00       	and    $0xffffff,%eax
     6f9:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     6fd:	45 8b 78 57          	mov    0x57(%r8),%r15d
     701:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     708:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     70d:	45 8b 60 5a          	mov    0x5a(%r8),%r12d
     711:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     718:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     71d:	45 8b 68 5d          	mov    0x5d(%r8),%r13d
     721:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     728:	c5 f9 6e 3c 86       	vmovd  (%rsi,%rax,4),%xmm7
     72d:	c4 a3 41 22 3c be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm7,%xmm7
     734:	42 0f b6 04 2f       	movzbl (%rdi,%r13,1),%eax
     739:	c4 a3 41 22 3c a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm7,%xmm7
     740:	c4 e3 41 22 3c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm7,%xmm7
     747:	c4 21 79 6e 04 8e    	vmovd  (%rsi,%r9,4),%xmm8
     74d:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
     754:	c4 23 39 22 04 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm8,%xmm8
     75b:	c4 63 39 22 04 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm8,%xmm8
     762:	c4 e2 75 36 f6       	vpermd %ymm6,%ymm1,%ymm6
     767:	c4 e3 3d 38 ff 01    	vinserti128 $0x1,%xmm7,%ymm8,%ymm7
     76d:	c4 e2 45 00 f8       	vpshufb %ymm0,%ymm7,%ymm7
     772:	c4 e2 75 36 ff       	vpermd %ymm7,%ymm1,%ymm7
     777:	41 8b 40 60          	mov    0x60(%r8),%eax
     77b:	25 ff ff ff 00       	and    $0xffffff,%eax
     780:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     785:	41 8b 40 63          	mov    0x63(%r8),%eax
     789:	25 ff ff ff 00       	and    $0xffffff,%eax
     78e:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
     793:	41 8b 40 66          	mov    0x66(%r8),%eax
     797:	25 ff ff ff 00       	and    $0xffffff,%eax
     79c:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     7a1:	41 8b 40 69          	mov    0x69(%r8),%eax
     7a5:	25 ff ff ff 00       	and    $0xffffff,%eax
     7aa:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
     7ae:	41 8b 40 6c          	mov    0x6c(%r8),%eax
     7b2:	25 ff ff ff 00       	and    $0xffffff,%eax
     7b7:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     7bb:	45 8b 78 6f          	mov    0x6f(%r8),%r15d
     7bf:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     7c6:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     7cb:	45 8b 60 72          	mov    0x72(%r8),%r12d
     7cf:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     7d6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     7db:	45 8b 68 75          	mov    0x75(%r8),%r13d
     7df:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     7e6:	c5 79 6e 04 86       	vmovd  (%rsi,%rax,4),%xmm8
     7eb:	c4 23 39 22 04 be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm8,%xmm8
     7f2:	42 0f b6 04 2f       	movzbl (%rdi,%r13,1),%eax
     7f7:	c4 23 39 22 04 a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm8,%xmm8
     7fe:	c4 63 39 22 04 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm8,%xmm8
     805:	c4 21 79 6e 0c 8e    	vmovd  (%rsi,%r9,4),%xmm9
     80b:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
     812:	c4 23 31 22 0c 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm9,%xmm9
     819:	c4 63 31 22 0c 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm9,%xmm9
     820:	c4 43 35 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm9,%ymm8
     826:	c4 62 3d 00 c0       	vpshufb %ymm0,%ymm8,%ymm8
     82b:	c4 42 75 36 c0       	vpermd %ymm8,%ymm1,%ymm8
     830:	41 8b 40 78          	mov    0x78(%r8),%eax
     834:	25 ff ff ff 00       	and    $0xffffff,%eax
     839:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     83e:	41 8b 40 7b          	mov    0x7b(%r8),%eax
     842:	25 ff ff ff 00       	and    $0xffffff,%eax
     847:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
     84c:	41 8b 40 7e          	mov    0x7e(%r8),%eax
     850:	25 ff ff ff 00       	and    $0xffffff,%eax
     855:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     85a:	41 8b 98 81 00 00 00 	mov    0x81(%r8),%ebx
     861:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     867:	41 8b 80 84 00 00 00 	mov    0x84(%r8),%eax
     86e:	25 ff ff ff 00       	and    $0xffffff,%eax
     873:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     877:	45 8b b8 87 00 00 00 	mov    0x87(%r8),%r15d
     87e:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     885:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     88a:	45 8b a0 8a 00 00 00 	mov    0x8a(%r8),%r12d
     891:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     898:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     89d:	45 8b a8 8d 00 00 00 	mov    0x8d(%r8),%r13d
     8a4:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     8ab:	c5 79 6e 0c 86       	vmovd  (%rsi,%rax,4),%xmm9
     8b0:	c4 23 31 22 0c be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm9,%xmm9
     8b7:	c4 23 31 22 0c a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm9,%xmm9
     8be:	42 0f b6 04 2f       	movzbl (%rdi,%r13,1),%eax
     8c3:	c4 63 31 22 0c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm9,%xmm9
     8ca:	c4 21 79 6e 14 8e    	vmovd  (%rsi,%r9,4),%xmm10
     8d0:	c4 23 29 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm10,%xmm10
     8d7:	0f b6 04 1f          	movzbl (%rdi,%rbx,1),%eax
     8db:	c4 23 29 22 14 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm10,%xmm10
     8e2:	c4 63 29 22 14 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm10,%xmm10
     8e9:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     8ef:	c4 62 35 00 d0       	vpshufb %ymm0,%ymm9,%ymm10
     8f4:	c4 42 6d 36 ca       	vpermd %ymm10,%ymm2,%ymm9
     8f9:	41 8b 80 90 00 00 00 	mov    0x90(%r8),%eax
     900:	25 ff ff ff 00       	and    $0xffffff,%eax
     905:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     90a:	41 8b 80 93 00 00 00 	mov    0x93(%r8),%eax
     911:	25 ff ff ff 00       	and    $0xffffff,%eax
     916:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
     91b:	41 8b 80 96 00 00 00 	mov    0x96(%r8),%eax
     922:	25 ff ff ff 00       	and    $0xffffff,%eax
     927:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     92c:	41 8b 80 99 00 00 00 	mov    0x99(%r8),%eax
     933:	25 ff ff ff 00       	and    $0xffffff,%eax
     938:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
     93c:	41 8b 80 9c 00 00 00 	mov    0x9c(%r8),%eax
     943:	25 ff ff ff 00       	and    $0xffffff,%eax
     948:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     94c:	45 8b b8 9f 00 00 00 	mov    0x9f(%r8),%r15d
     953:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     95a:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     95f:	45 8b a0 a2 00 00 00 	mov    0xa2(%r8),%r12d
     966:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     96d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     972:	45 8b a8 a5 00 00 00 	mov    0xa5(%r8),%r13d
     979:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     980:	c5 79 6e 1c 86       	vmovd  (%rsi,%rax,4),%xmm11
     985:	c4 23 21 22 1c be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm11,%xmm11
     98c:	c4 23 21 22 1c a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm11,%xmm11
     993:	42 0f b6 04 2f       	movzbl (%rdi,%r13,1),%eax
     998:	c4 63 21 22 1c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm11,%xmm11
     99f:	c4 21 79 6e 24 8e    	vmovd  (%rsi,%r9,4),%xmm12
     9a5:	c4 23 19 22 24 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm12,%xmm12
     9ac:	c4 23 19 22 24 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm12,%xmm12
     9b3:	c4 63 19 22 24 9e 03 	vpinsrd $0x3,(%rsi,%rbx,4),%xmm12,%xmm12
     9ba:	c4 43 1d 38 db 01    	vinserti128 $0x1,%xmm11,%ymm12,%ymm11
     9c0:	c4 62 25 00 d8       	vpshufb %ymm0,%ymm11,%ymm11
     9c5:	c4 42 75 36 db       	vpermd %ymm11,%ymm1,%ymm11
     9ca:	41 8b 80 a8 00 00 00 	mov    0xa8(%r8),%eax
     9d1:	25 ff ff ff 00       	and    $0xffffff,%eax
     9d6:	44 0f b6 0c 07       	movzbl (%rdi,%rax,1),%r9d
     9db:	41 8b 80 ab 00 00 00 	mov    0xab(%r8),%eax
     9e2:	25 ff ff ff 00       	and    $0xffffff,%eax
     9e7:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
     9ec:	41 8b 80 ae 00 00 00 	mov    0xae(%r8),%eax
     9f3:	25 ff ff ff 00       	and    $0xffffff,%eax
     9f8:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
     9fd:	41 8b 98 b1 00 00 00 	mov    0xb1(%r8),%ebx
     a04:	41 8b 80 b4 00 00 00 	mov    0xb4(%r8),%eax
     a0b:	25 ff ff ff 00       	and    $0xffffff,%eax
     a10:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     a14:	45 8b b8 b7 00 00 00 	mov    0xb7(%r8),%r15d
     a1b:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     a22:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     a27:	45 8b a0 ba 00 00 00 	mov    0xba(%r8),%r12d
     a2e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a35:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a3a:	45 8b a8 bd 00 00 00 	mov    0xbd(%r8),%r13d
     a41:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     a48:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     a4d:	c5 79 6e 24 86       	vmovd  (%rsi,%rax,4),%xmm12
     a52:	c4 23 19 22 24 be 01 	vpinsrd $0x1,(%rsi,%r15,4),%xmm12,%xmm12
     a59:	c4 23 19 22 24 a6 02 	vpinsrd $0x2,(%rsi,%r12,4),%xmm12,%xmm12
     a60:	c4 23 19 22 24 ae 03 	vpinsrd $0x3,(%rsi,%r13,4),%xmm12,%xmm12
     a67:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     a6d:	c4 21 79 6e 2c 8e    	vmovd  (%rsi,%r9,4),%xmm13
     a73:	c4 23 11 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm13,%xmm13
     a7a:	c4 23 11 22 2c 9e 02 	vpinsrd $0x2,(%rsi,%r11,4),%xmm13,%xmm13
     a81:	0f b6 04 1f          	movzbl (%rdi,%rbx,1),%eax
     a85:	c4 63 11 22 2c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm13,%xmm13
     a8c:	c4 43 15 38 e4 01    	vinserti128 $0x1,%xmm12,%ymm13,%ymm12
     a92:	c4 62 1d 00 e0       	vpshufb %ymm0,%ymm12,%ymm12
     a97:	c4 c3 7d 39 dd 01    	vextracti128 $0x1,%ymm3,%xmm13
     a9d:	c5 91 6c ed          	vpunpcklqdq %xmm5,%xmm13,%xmm5
     aa1:	c4 e3 65 38 dd 01    	vinserti128 $0x1,%xmm5,%ymm3,%ymm3
     aa7:	c4 e3 5d 38 e6 01    	vinserti128 $0x1,%xmm6,%ymm4,%ymm4
     aad:	c4 e3 4d 46 ef 21    	vperm2i128 $0x21,%ymm7,%ymm6,%ymm5
     ab3:	c4 e3 fd 00 ed f4    	vpermq $0xf4,%ymm5,%ymm5
     ab9:	c5 d5 6c ef          	vpunpcklqdq %ymm7,%ymm5,%ymm5
     abd:	c4 c1 7d e7 18       	vmovntdq %ymm3,(%r8)
     ac2:	c4 c1 7d e7 60 20    	vmovntdq %ymm4,0x20(%r8)
     ac8:	c4 c1 7d e7 68 40    	vmovntdq %ymm5,0x40(%r8)
     ace:	c4 c2 75 36 dc       	vpermd %ymm12,%ymm1,%ymm3
     ad3:	c4 63 7d 39 c4 01    	vextracti128 $0x1,%ymm8,%xmm4
     ad9:	c4 c1 59 6c e2       	vpunpcklqdq %xmm10,%xmm4,%xmm4
     ade:	c4 e3 3d 38 e4 01    	vinserti128 $0x1,%xmm4,%ymm8,%ymm4
     ae4:	c4 c3 35 38 eb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm5
     aea:	c4 e3 25 46 f3 21    	vperm2i128 $0x21,%ymm3,%ymm11,%ymm6
     af0:	c4 e3 fd 00 f6 f4    	vpermq $0xf4,%ymm6,%ymm6
     af6:	c5 cd 6c db          	vpunpcklqdq %ymm3,%ymm6,%ymm3
     afa:	c4 c1 7d e7 60 60    	vmovntdq %ymm4,0x60(%r8)
     b00:	c4 c1 7d e7 a8 80 00 	vmovntdq %ymm5,0x80(%r8)
     b07:	00 00 
     b09:	c4 c1 7d e7 98 a0 00 	vmovntdq %ymm3,0xa0(%r8)
     b10:	00 00 
     b12:	4d 8d 4e 40          	lea    0x40(%r14),%r9
     b16:	49 81 c0 c0 00 00 00 	add    $0xc0,%r8
     b1d:	49 81 c6 88 00 00 00 	add    $0x88,%r14
     b24:	49 39 ce             	cmp    %rcx,%r14
     b27:	4d 89 ce             	mov    %r9,%r14
     b2a:	77 35                	ja     b61 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb61>
     b2c:	49 8d 86 96 01 00 00 	lea    0x196(%r14),%rax
     b33:	48 39 c8             	cmp    %rcx,%rax
     b36:	0f 87 54 f9 ff ff    	ja     490 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x490>
     b3c:	41 0f 18 80 00 04 00 	prefetchnta 0x400(%r8)
     b43:	00 
     b44:	41 0f 18 80 40 04 00 	prefetchnta 0x440(%r8)
     b4b:	00 
     b4c:	41 0f 18 80 80 04 00 	prefetchnta 0x480(%r8)
     b53:	00 
     b54:	41 0f 18 80 bf 04 00 	prefetchnta 0x4bf(%r8)
     b5b:	00 
     b5c:	e9 2f f9 ff ff       	jmp    490 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x490>
     b61:	0f ae f8             	sfence
     b64:	49 8d 41 28          	lea    0x28(%r9),%rax
     b68:	48 39 c8             	cmp    %rcx,%rax
     b6b:	0f 86 40 f5 ff ff    	jbe    b1 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb1>
     b71:	4d 89 c8             	mov    %r9,%r8
     b74:	49 8d 40 08          	lea    0x8(%r8),%rax
     b78:	48 39 c8             	cmp    %rcx,%rax
     b7b:	0f 87 c3 f8 ff ff    	ja     444 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x444>
     b81:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     b85:	48 01 d0             	add    %rdx,%rax
     b88:	48 83 c0 10          	add    $0x10,%rax
     b8c:	c4 e2 7d 5a 05 00 00 	vbroadcasti128 0x0(%rip),%ymm0        # b95 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb95>
     b93:	00 00 
     b95:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
     b9c:	00 00 00 00 
     ba0:	4c 8b 58 f0          	mov    -0x10(%rax),%r11
     ba4:	4c 8b 78 f8          	mov    -0x8(%rax),%r15
     ba8:	4c 8b 08             	mov    (%rax),%r9
     bab:	45 89 da             	mov    %r11d,%r10d
     bae:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     bb5:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     bba:	4c 89 fb             	mov    %r15,%rbx
     bbd:	4c 0f a4 db 10       	shld   $0x10,%r11,%rbx
     bc2:	49 c1 eb 18          	shr    $0x18,%r11
     bc6:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     bcd:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     bd2:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     bd8:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     bdc:	45 89 fe             	mov    %r15d,%r14d
     bdf:	41 c1 ee 08          	shr    $0x8,%r14d
     be3:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     be8:	4d 89 cc             	mov    %r9,%r12
     beb:	4d 0f a4 fc 08       	shld   $0x8,%r15,%r12
     bf0:	49 c1 ef 20          	shr    $0x20,%r15
     bf4:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     bfb:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     c00:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     c07:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     c0c:	4d 89 cd             	mov    %r9,%r13
     c0f:	49 c1 ed 10          	shr    $0x10,%r13
     c13:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     c1a:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     c1f:	49 c1 e9 28          	shr    $0x28,%r9
     c23:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     c29:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     c30:	c4 a3 71 22 0c ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm1,%xmm1
     c37:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c3c:	c4 a3 71 22 0c 8e 03 	vpinsrd $0x3,(%rsi,%r9,4),%xmm1,%xmm1
     c43:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     c49:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     c50:	c4 e3 69 22 14 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm2,%xmm2
     c57:	c4 a3 69 22 14 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm2,%xmm2
     c5e:	c4 e3 6d 38 c9 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm1
     c64:	c4 e2 75 00 c8       	vpshufb %ymm0,%ymm1,%ymm1
     c69:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     c6f:	c5 e1 73 fa 0c       	vpslldq $0xc,%xmm2,%xmm3
     c74:	c5 f1 eb cb          	vpor   %xmm3,%xmm1,%xmm1
     c78:	c5 fa 7f 48 f0       	vmovdqu %xmm1,-0x10(%rax)
     c7d:	c5 f9 70 ca e9       	vpshufd $0xe9,%xmm2,%xmm1
     c82:	c5 f9 d6 08          	vmovq  %xmm1,(%rax)
     c86:	4d 8d 48 08          	lea    0x8(%r8),%r9
     c8a:	48 83 c0 18          	add    $0x18,%rax
     c8e:	49 83 c0 10          	add    $0x10,%r8
     c92:	49 39 c8             	cmp    %rcx,%r8
     c95:	4d 89 c8             	mov    %r9,%r8
     c98:	0f 86 02 ff ff ff    	jbe    ba0 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xba0>
     c9e:	4c 39 c9             	cmp    %r9,%rcx
     ca1:	0f 86 d1 00 00 00    	jbe    d78 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd78>
     ca7:	41 89 c8             	mov    %ecx,%r8d
     caa:	45 29 c8             	sub    %r9d,%r8d
     cad:	4d 8d 59 01          	lea    0x1(%r9),%r11
     cb1:	41 f6 c0 01          	test   $0x1,%r8b
     cb5:	74 3d                	je     cf4 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcf4>
     cb7:	4b 8d 1c 49          	lea    (%r9,%r9,2),%rbx
     cbb:	44 0f b6 04 1a       	movzbl (%rdx,%rbx,1),%r8d
     cc0:	44 0f b6 4c 1a 01    	movzbl 0x1(%rdx,%rbx,1),%r9d
     cc6:	41 c1 e1 08          	shl    $0x8,%r9d
     cca:	44 0f b6 54 1a 02    	movzbl 0x2(%rdx,%rbx,1),%r10d
     cd0:	41 c1 e2 10          	shl    $0x10,%r10d
     cd4:	49 01 f8             	add    %rdi,%r8
     cd7:	4d 01 c8             	add    %r9,%r8
     cda:	47 0f b6 04 02       	movzbl (%r10,%r8,1),%r8d
     cdf:	42 8b 04 86          	mov    (%rsi,%r8,4),%eax
     ce3:	88 04 1a             	mov    %al,(%rdx,%rbx,1)
     ce6:	88 64 1a 01          	mov    %ah,0x1(%rdx,%rbx,1)
     cea:	c1 e8 10             	shr    $0x10,%eax
     ced:	88 44 1a 02          	mov    %al,0x2(%rdx,%rbx,1)
     cf1:	4d 89 d9             	mov    %r11,%r9
     cf4:	4c 39 d9             	cmp    %r11,%rcx
     cf7:	74 7f                	je     d78 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd78>
     cf9:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
     cfd:	48 01 d0             	add    %rdx,%rax
     d00:	48 83 c0 05          	add    $0x5,%rax
     d04:	4c 29 c9             	sub    %r9,%rcx
     d07:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
     d0e:	00 00 
     d10:	0f b6 50 fb          	movzbl -0x5(%rax),%edx
     d14:	44 0f b6 40 fc       	movzbl -0x4(%rax),%r8d
     d19:	41 c1 e0 08          	shl    $0x8,%r8d
     d1d:	44 0f b6 48 fd       	movzbl -0x3(%rax),%r9d
     d22:	41 c1 e1 10          	shl    $0x10,%r9d
     d26:	48 01 fa             	add    %rdi,%rdx
     d29:	4c 01 c2             	add    %r8,%rdx
     d2c:	41 0f b6 14 11       	movzbl (%r9,%rdx,1),%edx
     d31:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     d34:	88 50 fb             	mov    %dl,-0x5(%rax)
     d37:	88 70 fc             	mov    %dh,-0x4(%rax)
     d3a:	c1 ea 10             	shr    $0x10,%edx
     d3d:	88 50 fd             	mov    %dl,-0x3(%rax)
     d40:	0f b6 50 fe          	movzbl -0x2(%rax),%edx
     d44:	44 0f b6 40 ff       	movzbl -0x1(%rax),%r8d
     d49:	41 c1 e0 08          	shl    $0x8,%r8d
     d4d:	44 0f b6 08          	movzbl (%rax),%r9d
     d51:	41 c1 e1 10          	shl    $0x10,%r9d
     d55:	48 01 fa             	add    %rdi,%rdx
     d58:	4c 01 c2             	add    %r8,%rdx
     d5b:	41 0f b6 14 11       	movzbl (%r9,%rdx,1),%edx
     d60:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     d63:	88 50 fe             	mov    %dl,-0x2(%rax)
     d66:	88 70 ff             	mov    %dh,-0x1(%rax)
     d69:	c1 ea 10             	shr    $0x10,%edx
     d6c:	88 10                	mov    %dl,(%rax)
     d6e:	48 83 c0 06          	add    $0x6,%rax
     d72:	48 83 c1 fe          	add    $0xfffffffffffffffe,%rcx
     d76:	75 98                	jne    d10 <jshc_channel::avx2_chain_batchspan(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd10>
     d78:	5b                   	pop    %rbx
     d79:	41 5c                	pop    %r12
     d7b:	41 5d                	pop    %r13
     d7d:	41 5e                	pop    %r14
     d7f:	41 5f                	pop    %r15
     d81:	c5 f8 77             	vzeroupper
     d84:	c3                   	ret
     d85:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
     d8c:	00 00 00 00 

0000000000000d90 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     d90:	55                   	push   %rbp
     d91:	41 57                	push   %r15
     d93:	41 56                	push   %r14
     d95:	41 55                	push   %r13
     d97:	41 54                	push   %r12
     d99:	53                   	push   %rbx
     d9a:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     d9e:	49 81 f9 00 04 00 00 	cmp    $0x400,%r9
     da5:	b8 00 04 00 00       	mov    $0x400,%eax
     daa:	49 0f 42 c1          	cmovb  %r9,%rax
     dae:	4d 85 c0             	test   %r8,%r8
     db1:	0f 84 50 04 00 00    	je     1207 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x477>
     db7:	45 31 c9             	xor    %r9d,%r9d
     dba:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     dc0:	42 0f 18 04 0a       	prefetchnta (%rdx,%r9,1)
     dc5:	49 83 c1 40          	add    $0x40,%r9
     dc9:	49 39 c1             	cmp    %rax,%r9
     dcc:	72 f2                	jb     dc0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x30>
     dce:	8d 04 89             	lea    (%rcx,%rcx,4),%eax
     dd1:	44 8d 3c 81          	lea    (%rcx,%rax,4),%r15d
     dd5:	41 83 e7 3f          	and    $0x3f,%r15d
     dd9:	bb 02 00 00 00       	mov    $0x2,%ebx
     dde:	45 31 c9             	xor    %r9d,%r9d
     de1:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
     de8:	0f 1f 84 00 00 00 00 
     def:	00 
     df0:	4d 39 cf             	cmp    %r9,%r15
     df3:	74 45                	je     e3a <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
     df5:	44 0f b6 54 1a fe    	movzbl -0x2(%rdx,%rbx,1),%r10d
     dfb:	44 0f b6 5c 1a ff    	movzbl -0x1(%rdx,%rbx,1),%r11d
     e01:	41 c1 e3 08          	shl    $0x8,%r11d
     e05:	44 0f b6 34 1a       	movzbl (%rdx,%rbx,1),%r14d
     e0a:	41 c1 e6 10          	shl    $0x10,%r14d
     e0e:	49 01 fa             	add    %rdi,%r10
     e11:	4d 01 da             	add    %r11,%r10
     e14:	47 0f b6 14 16       	movzbl (%r14,%r10,1),%r10d
     e19:	42 8b 04 96          	mov    (%rsi,%r10,4),%eax
     e1d:	88 44 19 fe          	mov    %al,-0x2(%rcx,%rbx,1)
     e21:	88 64 19 ff          	mov    %ah,-0x1(%rcx,%rbx,1)
     e25:	c1 e8 10             	shr    $0x10,%eax
     e28:	88 04 19             	mov    %al,(%rcx,%rbx,1)
     e2b:	49 ff c1             	inc    %r9
     e2e:	48 83 c3 03          	add    $0x3,%rbx
     e32:	4d 39 c8             	cmp    %r9,%r8
     e35:	75 b9                	jne    df0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     e37:	4d 89 c7             	mov    %r8,%r15
     e3a:	49 8d 47 48          	lea    0x48(%r15),%rax
     e3e:	4c 39 c0             	cmp    %r8,%rax
     e41:	0f 86 d0 03 00 00    	jbe    1217 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x487>
     e47:	4d 89 fa             	mov    %r15,%r10
     e4a:	49 8d 42 28          	lea    0x28(%r10),%rax
     e4e:	4c 39 c0             	cmp    %r8,%rax
     e51:	0f 87 08 0b 00 00    	ja     195f <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbcf>
     e57:	4b 8d 04 52          	lea    (%r10,%r10,2),%rax
     e5b:	c4 e2 7d 5a 05 00 00 	vbroadcasti128 0x0(%rip),%ymm0        # e64 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd4>
     e62:	00 00 
     e64:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # e6c <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdc>
     e6b:	00 
     e6c:	c5 f9 6f 15 00 00 00 	vmovdqa 0x0(%rip),%xmm2        # e74 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe4>
     e73:	00 
     e74:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
     e7b:	00 00 00 00 00 
     e80:	44 8b 0c 02          	mov    (%rdx,%rax,1),%r9d
     e84:	44 8b 5c 02 03       	mov    0x3(%rdx,%rax,1),%r11d
     e89:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e90:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     e95:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     e9c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     ea1:	8b 5c 02 06          	mov    0x6(%rdx,%rax,1),%ebx
     ea5:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     eab:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     eaf:	44 8b 74 02 09       	mov    0x9(%rdx,%rax,1),%r14d
     eb4:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     ebb:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     ec0:	44 8b 7c 02 0c       	mov    0xc(%rdx,%rax,1),%r15d
     ec5:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     ecc:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     ed1:	44 8b 64 02 0f       	mov    0xf(%rdx,%rax,1),%r12d
     ed6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     edd:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     ee2:	44 8b 6c 02 12       	mov    0x12(%rdx,%rax,1),%r13d
     ee7:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     eee:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     ef3:	8b 6c 02 15          	mov    0x15(%rdx,%rax,1),%ebp
     ef7:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
     efd:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     f03:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
     f0a:	44 0f b6 3c 2f       	movzbl (%rdi,%rbp,1),%r15d
     f0f:	c4 a3 61 22 1c ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm3,%xmm3
     f16:	c4 a3 61 22 1c be 03 	vpinsrd $0x3,(%rsi,%r15,4),%xmm3,%xmm3
     f1d:	c4 a1 79 6e 24 8e    	vmovd  (%rsi,%r9,4),%xmm4
     f23:	c4 a3 59 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm4,%xmm4
     f2a:	c4 e3 59 22 24 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm4,%xmm4
     f31:	c4 a3 59 22 24 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm4,%xmm4
     f38:	c4 e3 5d 38 db 01    	vinserti128 $0x1,%xmm3,%ymm4,%ymm3
     f3e:	44 8b 4c 02 18       	mov    0x18(%rdx,%rax,1),%r9d
     f43:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f4a:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     f4f:	44 8b 5c 02 1b       	mov    0x1b(%rdx,%rax,1),%r11d
     f54:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     f5b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     f60:	8b 5c 02 1e          	mov    0x1e(%rdx,%rax,1),%ebx
     f64:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     f6a:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     f6e:	44 8b 74 02 21       	mov    0x21(%rdx,%rax,1),%r14d
     f73:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     f7a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     f7f:	44 8b 7c 02 24       	mov    0x24(%rdx,%rax,1),%r15d
     f84:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     f8b:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     f90:	44 8b 64 02 27       	mov    0x27(%rdx,%rax,1),%r12d
     f95:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     f9c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     fa1:	44 8b 6c 02 2a       	mov    0x2a(%rdx,%rax,1),%r13d
     fa6:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     fad:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     fb2:	8b 6c 02 2d          	mov    0x2d(%rdx,%rax,1),%ebp
     fb6:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
     fbc:	c4 a1 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm4
     fc2:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
     fc9:	c4 a3 59 22 24 ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm4,%xmm4
     fd0:	44 0f b6 3c 2f       	movzbl (%rdi,%rbp,1),%r15d
     fd5:	c4 a3 59 22 24 be 03 	vpinsrd $0x3,(%rsi,%r15,4),%xmm4,%xmm4
     fdc:	c4 a1 79 6e 2c 8e    	vmovd  (%rsi,%r9,4),%xmm5
     fe2:	c4 a3 51 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm5,%xmm5
     fe9:	c4 e3 51 22 2c 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm5,%xmm5
     ff0:	c4 a3 51 22 2c b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm5,%xmm5
     ff7:	44 8b 4c 02 30       	mov    0x30(%rdx,%rax,1),%r9d
     ffc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1003:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1008:	44 8b 5c 02 33       	mov    0x33(%rdx,%rax,1),%r11d
    100d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1014:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1019:	8b 5c 02 36          	mov    0x36(%rdx,%rax,1),%ebx
    101d:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1023:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    1027:	44 8b 74 02 39       	mov    0x39(%rdx,%rax,1),%r14d
    102c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1033:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1038:	44 8b 7c 02 3c       	mov    0x3c(%rdx,%rax,1),%r15d
    103d:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1044:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1049:	44 8b 64 02 3f       	mov    0x3f(%rdx,%rax,1),%r12d
    104e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1055:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    105a:	44 8b 6c 02 42       	mov    0x42(%rdx,%rax,1),%r13d
    105f:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1066:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    106b:	8b 6c 02 45          	mov    0x45(%rdx,%rax,1),%ebp
    106f:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    1075:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    107b:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
    1082:	44 0f b6 3c 2f       	movzbl (%rdi,%rbp,1),%r15d
    1087:	c4 a3 49 22 34 ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm6,%xmm6
    108e:	c4 a3 49 22 34 be 03 	vpinsrd $0x3,(%rsi,%r15,4),%xmm6,%xmm6
    1095:	c4 a1 79 6e 3c 8e    	vmovd  (%rsi,%r9,4),%xmm7
    109b:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    10a2:	c4 e3 41 22 3c 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm7,%xmm7
    10a9:	c4 a3 41 22 3c b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm7,%xmm7
    10b0:	c4 e3 55 38 e4 01    	vinserti128 $0x1,%xmm4,%ymm5,%ymm4
    10b6:	c4 e3 45 38 ee 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm5
    10bc:	44 8b 4c 02 48       	mov    0x48(%rdx,%rax,1),%r9d
    10c1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10c8:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    10cd:	44 8b 5c 02 4b       	mov    0x4b(%rdx,%rax,1),%r11d
    10d2:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    10d9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    10de:	8b 5c 02 4e          	mov    0x4e(%rdx,%rax,1),%ebx
    10e2:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    10e8:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    10ec:	44 8b 74 02 51       	mov    0x51(%rdx,%rax,1),%r14d
    10f1:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    10f8:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    10fd:	44 8b 7c 02 54       	mov    0x54(%rdx,%rax,1),%r15d
    1102:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1109:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    110e:	44 8b 64 02 57       	mov    0x57(%rdx,%rax,1),%r12d
    1113:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    111a:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    111f:	44 8b 6c 02 5a       	mov    0x5a(%rdx,%rax,1),%r13d
    1124:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    112b:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1130:	8b 6c 02 5d          	mov    0x5d(%rdx,%rax,1),%ebp
    1134:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    113a:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1140:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
    1147:	c4 a3 49 22 34 ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm6,%xmm6
    114e:	44 0f b6 3c 2f       	movzbl (%rdi,%rbp,1),%r15d
    1153:	c4 a3 49 22 34 be 03 	vpinsrd $0x3,(%rsi,%r15,4),%xmm6,%xmm6
    115a:	c4 a1 79 6e 3c 8e    	vmovd  (%rsi,%r9,4),%xmm7
    1160:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    1167:	c4 e3 41 22 3c 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm7,%xmm7
    116e:	c4 a3 41 22 3c b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm7,%xmm7
    1175:	c4 e3 45 38 f6 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm6
    117b:	c4 e2 65 00 d8       	vpshufb %ymm0,%ymm3,%ymm3
    1180:	c4 e2 75 36 db       	vpermd %ymm3,%ymm1,%ymm3
    1185:	c4 e2 5d 00 e0       	vpshufb %ymm0,%ymm4,%ymm4
    118a:	c4 e2 6d 36 fc       	vpermd %ymm4,%ymm2,%ymm7
    118f:	c4 e2 55 00 e8       	vpshufb %ymm0,%ymm5,%ymm5
    1194:	c4 e2 75 36 ed       	vpermd %ymm5,%ymm1,%ymm5
    1199:	c4 e2 4d 00 f0       	vpshufb %ymm0,%ymm6,%ymm6
    119e:	c4 e2 75 36 f6       	vpermd %ymm6,%ymm1,%ymm6
    11a3:	c4 c3 7d 39 d8 01    	vextracti128 $0x1,%ymm3,%xmm8
    11a9:	c5 b9 6c e4          	vpunpcklqdq %xmm4,%xmm8,%xmm4
    11ad:	c4 e3 65 38 dc 01    	vinserti128 $0x1,%xmm4,%ymm3,%ymm3
    11b3:	c4 e3 45 38 e5 01    	vinserti128 $0x1,%xmm5,%ymm7,%ymm4
    11b9:	c4 e3 55 46 ee 21    	vperm2i128 $0x21,%ymm6,%ymm5,%ymm5
    11bf:	c4 e3 fd 00 ed f4    	vpermq $0xf4,%ymm5,%ymm5
    11c5:	c5 d5 6c ee          	vpunpcklqdq %ymm6,%ymm5,%ymm5
    11c9:	c5 fe 7f 1c 01       	vmovdqu %ymm3,(%rcx,%rax,1)
    11ce:	c5 fe 7f 64 01 20    	vmovdqu %ymm4,0x20(%rcx,%rax,1)
    11d4:	c5 fe 7f 6c 01 40    	vmovdqu %ymm5,0x40(%rcx,%rax,1)
    11da:	4d 8d 4a 20          	lea    0x20(%r10),%r9
    11de:	49 83 c2 48          	add    $0x48,%r10
    11e2:	48 83 c0 60          	add    $0x60,%rax
    11e6:	4d 39 c2             	cmp    %r8,%r10
    11e9:	4d 89 ca             	mov    %r9,%r10
    11ec:	0f 86 8e fc ff ff    	jbe    e80 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    11f2:	49 8d 41 08          	lea    0x8(%r9),%rax
    11f6:	4c 39 c0             	cmp    %r8,%rax
    11f9:	0f 86 70 07 00 00    	jbe    196f <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbdf>
    11ff:	4d 89 ca             	mov    %r9,%r10
    1202:	e9 7a 08 00 00       	jmp    1a81 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcf1>
    1207:	45 31 ff             	xor    %r15d,%r15d
    120a:	49 8d 47 48          	lea    0x48(%r15),%rax
    120e:	4c 39 c0             	cmp    %r8,%rax
    1211:	0f 87 30 fc ff ff    	ja     e47 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb7>
    1217:	4f 8d 0c 7f          	lea    (%r15,%r15,2),%r9
    121b:	c4 e2 7d 5a 05 00 00 	vbroadcasti128 0x0(%rip),%ymm0        # 1224 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x494>
    1222:	00 00 
    1224:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 122c <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x49c>
    122b:	00 
    122c:	c5 f9 6f 15 00 00 00 	vmovdqa 0x0(%rip),%xmm2        # 1234 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x4a4>
    1233:	00 
    1234:	e9 dd 06 00 00       	jmp    1916 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb86>
    1239:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1240:	42 8b 04 0a          	mov    (%rdx,%r9,1),%eax
    1244:	46 8b 5c 0a 03       	mov    0x3(%rdx,%r9,1),%r11d
    1249:	25 ff ff ff 00       	and    $0xffffff,%eax
    124e:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    1253:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    125a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    125f:	42 8b 44 0a 06       	mov    0x6(%rdx,%r9,1),%eax
    1264:	25 ff ff ff 00       	and    $0xffffff,%eax
    1269:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    126d:	42 8b 44 0a 09       	mov    0x9(%rdx,%r9,1),%eax
    1272:	25 ff ff ff 00       	and    $0xffffff,%eax
    1277:	44 0f b6 34 07       	movzbl (%rdi,%rax,1),%r14d
    127c:	42 8b 44 0a 0c       	mov    0xc(%rdx,%r9,1),%eax
    1281:	25 ff ff ff 00       	and    $0xffffff,%eax
    1286:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    128a:	46 8b 64 0a 0f       	mov    0xf(%rdx,%r9,1),%r12d
    128f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1296:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    129b:	46 8b 6c 0a 12       	mov    0x12(%rdx,%r9,1),%r13d
    12a0:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    12a7:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    12ac:	42 8b 6c 0a 15       	mov    0x15(%rdx,%r9,1),%ebp
    12b1:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    12b7:	c5 f9 6e 1c 86       	vmovd  (%rsi,%rax,4),%xmm3
    12bc:	c4 a3 61 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm3,%xmm3
    12c3:	c4 a3 61 22 1c ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm3,%xmm3
    12ca:	0f b6 04 2f          	movzbl (%rdi,%rbp,1),%eax
    12ce:	c4 e3 61 22 1c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm3,%xmm3
    12d5:	c4 a1 79 6e 24 96    	vmovd  (%rsi,%r10,4),%xmm4
    12db:	c4 a3 59 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm4,%xmm4
    12e2:	c4 e3 59 22 24 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm4,%xmm4
    12e9:	c4 a3 59 22 24 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm4,%xmm4
    12f0:	c4 e3 5d 38 db 01    	vinserti128 $0x1,%xmm3,%ymm4,%ymm3
    12f6:	c4 e2 65 00 d8       	vpshufb %ymm0,%ymm3,%ymm3
    12fb:	c4 e2 75 36 db       	vpermd %ymm3,%ymm1,%ymm3
    1300:	42 8b 44 0a 18       	mov    0x18(%rdx,%r9,1),%eax
    1305:	25 ff ff ff 00       	and    $0xffffff,%eax
    130a:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    130f:	42 8b 44 0a 1b       	mov    0x1b(%rdx,%r9,1),%eax
    1314:	25 ff ff ff 00       	and    $0xffffff,%eax
    1319:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
    131e:	42 8b 44 0a 1e       	mov    0x1e(%rdx,%r9,1),%eax
    1323:	25 ff ff ff 00       	and    $0xffffff,%eax
    1328:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    132c:	46 8b 74 0a 21       	mov    0x21(%rdx,%r9,1),%r14d
    1331:	42 8b 44 0a 24       	mov    0x24(%rdx,%r9,1),%eax
    1336:	25 ff ff ff 00       	and    $0xffffff,%eax
    133b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    133f:	46 8b 64 0a 27       	mov    0x27(%rdx,%r9,1),%r12d
    1344:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    134b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1350:	46 8b 6c 0a 2a       	mov    0x2a(%rdx,%r9,1),%r13d
    1355:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    135c:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1361:	42 8b 6c 0a 2d       	mov    0x2d(%rdx,%r9,1),%ebp
    1366:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    136c:	0f b6 2c 2f          	movzbl (%rdi,%rbp,1),%ebp
    1370:	c5 f9 6e 24 86       	vmovd  (%rsi,%rax,4),%xmm4
    1375:	c4 a3 59 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm4,%xmm4
    137c:	c4 a3 59 22 24 ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm4,%xmm4
    1383:	c4 e3 59 22 24 ae 03 	vpinsrd $0x3,(%rsi,%rbp,4),%xmm4,%xmm4
    138a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1391:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
    1397:	c4 a3 51 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm5,%xmm5
    139e:	c4 e3 51 22 2c 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm5,%xmm5
    13a5:	42 0f b6 04 37       	movzbl (%rdi,%r14,1),%eax
    13aa:	c4 e3 51 22 2c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm5,%xmm5
    13b1:	c4 e3 55 38 e4 01    	vinserti128 $0x1,%xmm4,%ymm5,%ymm4
    13b7:	c4 e2 5d 00 e8       	vpshufb %ymm0,%ymm4,%ymm5
    13bc:	c4 e2 6d 36 e5       	vpermd %ymm5,%ymm2,%ymm4
    13c1:	42 8b 44 0a 30       	mov    0x30(%rdx,%r9,1),%eax
    13c6:	25 ff ff ff 00       	and    $0xffffff,%eax
    13cb:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    13d0:	42 8b 44 0a 33       	mov    0x33(%rdx,%r9,1),%eax
    13d5:	25 ff ff ff 00       	and    $0xffffff,%eax
    13da:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
    13df:	42 8b 44 0a 36       	mov    0x36(%rdx,%r9,1),%eax
    13e4:	25 ff ff ff 00       	and    $0xffffff,%eax
    13e9:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    13ed:	46 8b 74 0a 39       	mov    0x39(%rdx,%r9,1),%r14d
    13f2:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    13f9:	42 8b 44 0a 3c       	mov    0x3c(%rdx,%r9,1),%eax
    13fe:	25 ff ff ff 00       	and    $0xffffff,%eax
    1403:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1407:	46 8b 64 0a 3f       	mov    0x3f(%rdx,%r9,1),%r12d
    140c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1413:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1418:	46 8b 6c 0a 42       	mov    0x42(%rdx,%r9,1),%r13d
    141d:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1424:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1429:	42 8b 6c 0a 45       	mov    0x45(%rdx,%r9,1),%ebp
    142e:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    1434:	0f b6 2c 2f          	movzbl (%rdi,%rbp,1),%ebp
    1438:	c5 f9 6e 34 86       	vmovd  (%rsi,%rax,4),%xmm6
    143d:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
    1444:	c4 a3 49 22 34 ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm6,%xmm6
    144b:	c4 e3 49 22 34 ae 03 	vpinsrd $0x3,(%rsi,%rbp,4),%xmm6,%xmm6
    1452:	42 0f b6 04 37       	movzbl (%rdi,%r14,1),%eax
    1457:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    145d:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    1464:	c4 e3 41 22 3c 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm7,%xmm7
    146b:	c4 e3 41 22 3c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm7,%xmm7
    1472:	c4 e3 45 38 f6 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm6
    1478:	c4 e2 4d 00 f0       	vpshufb %ymm0,%ymm6,%ymm6
    147d:	42 8b 44 0a 48       	mov    0x48(%rdx,%r9,1),%eax
    1482:	25 ff ff ff 00       	and    $0xffffff,%eax
    1487:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    148c:	42 8b 44 0a 4b       	mov    0x4b(%rdx,%r9,1),%eax
    1491:	25 ff ff ff 00       	and    $0xffffff,%eax
    1496:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
    149b:	42 8b 44 0a 4e       	mov    0x4e(%rdx,%r9,1),%eax
    14a0:	25 ff ff ff 00       	and    $0xffffff,%eax
    14a5:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    14a9:	42 8b 44 0a 51       	mov    0x51(%rdx,%r9,1),%eax
    14ae:	25 ff ff ff 00       	and    $0xffffff,%eax
    14b3:	44 0f b6 34 07       	movzbl (%rdi,%rax,1),%r14d
    14b8:	42 8b 44 0a 54       	mov    0x54(%rdx,%r9,1),%eax
    14bd:	25 ff ff ff 00       	and    $0xffffff,%eax
    14c2:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    14c6:	46 8b 64 0a 57       	mov    0x57(%rdx,%r9,1),%r12d
    14cb:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    14d2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    14d7:	46 8b 6c 0a 5a       	mov    0x5a(%rdx,%r9,1),%r13d
    14dc:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    14e3:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    14e8:	42 8b 6c 0a 5d       	mov    0x5d(%rdx,%r9,1),%ebp
    14ed:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    14f3:	c5 f9 6e 3c 86       	vmovd  (%rsi,%rax,4),%xmm7
    14f8:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    14ff:	0f b6 04 2f          	movzbl (%rdi,%rbp,1),%eax
    1503:	c4 a3 41 22 3c ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm7,%xmm7
    150a:	c4 e3 41 22 3c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm7,%xmm7
    1511:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    1517:	c4 23 39 22 04 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm8,%xmm8
    151e:	c4 63 39 22 04 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm8,%xmm8
    1525:	c4 23 39 22 04 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm8,%xmm8
    152c:	c4 e2 75 36 f6       	vpermd %ymm6,%ymm1,%ymm6
    1531:	c4 e3 3d 38 ff 01    	vinserti128 $0x1,%xmm7,%ymm8,%ymm7
    1537:	c4 e2 45 00 f8       	vpshufb %ymm0,%ymm7,%ymm7
    153c:	c4 e2 75 36 ff       	vpermd %ymm7,%ymm1,%ymm7
    1541:	42 8b 44 0a 60       	mov    0x60(%rdx,%r9,1),%eax
    1546:	25 ff ff ff 00       	and    $0xffffff,%eax
    154b:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    1550:	42 8b 44 0a 63       	mov    0x63(%rdx,%r9,1),%eax
    1555:	25 ff ff ff 00       	and    $0xffffff,%eax
    155a:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
    155f:	42 8b 44 0a 66       	mov    0x66(%rdx,%r9,1),%eax
    1564:	25 ff ff ff 00       	and    $0xffffff,%eax
    1569:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    156d:	42 8b 44 0a 69       	mov    0x69(%rdx,%r9,1),%eax
    1572:	25 ff ff ff 00       	and    $0xffffff,%eax
    1577:	44 0f b6 34 07       	movzbl (%rdi,%rax,1),%r14d
    157c:	42 8b 44 0a 6c       	mov    0x6c(%rdx,%r9,1),%eax
    1581:	25 ff ff ff 00       	and    $0xffffff,%eax
    1586:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    158a:	46 8b 64 0a 6f       	mov    0x6f(%rdx,%r9,1),%r12d
    158f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1596:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    159b:	46 8b 6c 0a 72       	mov    0x72(%rdx,%r9,1),%r13d
    15a0:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    15a7:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    15ac:	42 8b 6c 0a 75       	mov    0x75(%rdx,%r9,1),%ebp
    15b1:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    15b7:	c5 79 6e 04 86       	vmovd  (%rsi,%rax,4),%xmm8
    15bc:	c4 23 39 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm8,%xmm8
    15c3:	0f b6 04 2f          	movzbl (%rdi,%rbp,1),%eax
    15c7:	c4 23 39 22 04 ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm8,%xmm8
    15ce:	c4 63 39 22 04 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm8,%xmm8
    15d5:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    15db:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    15e2:	c4 63 31 22 0c 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm9,%xmm9
    15e9:	c4 23 31 22 0c b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm9,%xmm9
    15f0:	c4 43 35 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm9,%ymm8
    15f6:	c4 62 3d 00 c0       	vpshufb %ymm0,%ymm8,%ymm8
    15fb:	c4 42 75 36 c0       	vpermd %ymm8,%ymm1,%ymm8
    1600:	42 8b 44 0a 78       	mov    0x78(%rdx,%r9,1),%eax
    1605:	25 ff ff ff 00       	and    $0xffffff,%eax
    160a:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    160f:	42 8b 44 0a 7b       	mov    0x7b(%rdx,%r9,1),%eax
    1614:	25 ff ff ff 00       	and    $0xffffff,%eax
    1619:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
    161e:	42 8b 44 0a 7e       	mov    0x7e(%rdx,%r9,1),%eax
    1623:	25 ff ff ff 00       	and    $0xffffff,%eax
    1628:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    162c:	46 8b b4 0a 81 00 00 	mov    0x81(%rdx,%r9,1),%r14d
    1633:	00 
    1634:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    163b:	42 8b 84 0a 84 00 00 	mov    0x84(%rdx,%r9,1),%eax
    1642:	00 
    1643:	25 ff ff ff 00       	and    $0xffffff,%eax
    1648:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    164c:	46 8b a4 0a 87 00 00 	mov    0x87(%rdx,%r9,1),%r12d
    1653:	00 
    1654:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    165b:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1660:	46 8b ac 0a 8a 00 00 	mov    0x8a(%rdx,%r9,1),%r13d
    1667:	00 
    1668:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    166f:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1674:	42 8b ac 0a 8d 00 00 	mov    0x8d(%rdx,%r9,1),%ebp
    167b:	00 
    167c:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    1682:	c5 79 6e 0c 86       	vmovd  (%rsi,%rax,4),%xmm9
    1687:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    168e:	c4 23 31 22 0c ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm9,%xmm9
    1695:	0f b6 04 2f          	movzbl (%rdi,%rbp,1),%eax
    1699:	c4 63 31 22 0c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm9,%xmm9
    16a0:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    16a6:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    16ad:	42 0f b6 04 37       	movzbl (%rdi,%r14,1),%eax
    16b2:	c4 63 29 22 14 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm10,%xmm10
    16b9:	c4 63 29 22 14 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm10,%xmm10
    16c0:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    16c6:	c4 62 35 00 d0       	vpshufb %ymm0,%ymm9,%ymm10
    16cb:	c4 42 6d 36 ca       	vpermd %ymm10,%ymm2,%ymm9
    16d0:	42 8b 84 0a 90 00 00 	mov    0x90(%rdx,%r9,1),%eax
    16d7:	00 
    16d8:	25 ff ff ff 00       	and    $0xffffff,%eax
    16dd:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    16e2:	42 8b 84 0a 93 00 00 	mov    0x93(%rdx,%r9,1),%eax
    16e9:	00 
    16ea:	25 ff ff ff 00       	and    $0xffffff,%eax
    16ef:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
    16f4:	42 8b 84 0a 96 00 00 	mov    0x96(%rdx,%r9,1),%eax
    16fb:	00 
    16fc:	25 ff ff ff 00       	and    $0xffffff,%eax
    1701:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    1705:	42 8b 84 0a 99 00 00 	mov    0x99(%rdx,%r9,1),%eax
    170c:	00 
    170d:	25 ff ff ff 00       	and    $0xffffff,%eax
    1712:	44 0f b6 34 07       	movzbl (%rdi,%rax,1),%r14d
    1717:	42 8b 84 0a 9c 00 00 	mov    0x9c(%rdx,%r9,1),%eax
    171e:	00 
    171f:	25 ff ff ff 00       	and    $0xffffff,%eax
    1724:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1728:	46 8b a4 0a 9f 00 00 	mov    0x9f(%rdx,%r9,1),%r12d
    172f:	00 
    1730:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1737:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    173c:	46 8b ac 0a a2 00 00 	mov    0xa2(%rdx,%r9,1),%r13d
    1743:	00 
    1744:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    174b:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1750:	42 8b ac 0a a5 00 00 	mov    0xa5(%rdx,%r9,1),%ebp
    1757:	00 
    1758:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    175e:	c5 79 6e 1c 86       	vmovd  (%rsi,%rax,4),%xmm11
    1763:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
    176a:	c4 23 21 22 1c ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm11,%xmm11
    1771:	0f b6 04 2f          	movzbl (%rdi,%rbp,1),%eax
    1775:	c4 63 21 22 1c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm11,%xmm11
    177c:	c4 21 79 6e 24 96    	vmovd  (%rsi,%r10,4),%xmm12
    1782:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    1789:	c4 63 19 22 24 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm12,%xmm12
    1790:	c4 23 19 22 24 b6 03 	vpinsrd $0x3,(%rsi,%r14,4),%xmm12,%xmm12
    1797:	c4 43 1d 38 db 01    	vinserti128 $0x1,%xmm11,%ymm12,%ymm11
    179d:	c4 62 25 00 d8       	vpshufb %ymm0,%ymm11,%ymm11
    17a2:	c4 42 75 36 db       	vpermd %ymm11,%ymm1,%ymm11
    17a7:	42 8b 84 0a a8 00 00 	mov    0xa8(%rdx,%r9,1),%eax
    17ae:	00 
    17af:	25 ff ff ff 00       	and    $0xffffff,%eax
    17b4:	44 0f b6 14 07       	movzbl (%rdi,%rax,1),%r10d
    17b9:	42 8b 84 0a ab 00 00 	mov    0xab(%rdx,%r9,1),%eax
    17c0:	00 
    17c1:	25 ff ff ff 00       	and    $0xffffff,%eax
    17c6:	44 0f b6 1c 07       	movzbl (%rdi,%rax,1),%r11d
    17cb:	42 8b 84 0a ae 00 00 	mov    0xae(%rdx,%r9,1),%eax
    17d2:	00 
    17d3:	25 ff ff ff 00       	and    $0xffffff,%eax
    17d8:	0f b6 1c 07          	movzbl (%rdi,%rax,1),%ebx
    17dc:	46 8b b4 0a b1 00 00 	mov    0xb1(%rdx,%r9,1),%r14d
    17e3:	00 
    17e4:	42 8b 84 0a b4 00 00 	mov    0xb4(%rdx,%r9,1),%eax
    17eb:	00 
    17ec:	25 ff ff ff 00       	and    $0xffffff,%eax
    17f1:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    17f5:	46 8b a4 0a b7 00 00 	mov    0xb7(%rdx,%r9,1),%r12d
    17fc:	00 
    17fd:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1804:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1809:	46 8b ac 0a ba 00 00 	mov    0xba(%rdx,%r9,1),%r13d
    1810:	00 
    1811:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1818:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    181d:	42 8b ac 0a bd 00 00 	mov    0xbd(%rdx,%r9,1),%ebp
    1824:	00 
    1825:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    182b:	0f b6 2c 2f          	movzbl (%rdi,%rbp,1),%ebp
    182f:	c5 79 6e 24 86       	vmovd  (%rsi,%rax,4),%xmm12
    1834:	c4 23 19 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm12,%xmm12
    183b:	c4 23 19 22 24 ae 02 	vpinsrd $0x2,(%rsi,%r13,4),%xmm12,%xmm12
    1842:	c4 63 19 22 24 ae 03 	vpinsrd $0x3,(%rsi,%rbp,4),%xmm12,%xmm12
    1849:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1850:	c4 21 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm13
    1856:	c4 23 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm13,%xmm13
    185d:	c4 63 11 22 2c 9e 02 	vpinsrd $0x2,(%rsi,%rbx,4),%xmm13,%xmm13
    1864:	42 0f b6 04 37       	movzbl (%rdi,%r14,1),%eax
    1869:	c4 63 11 22 2c 86 03 	vpinsrd $0x3,(%rsi,%rax,4),%xmm13,%xmm13
    1870:	c4 43 15 38 e4 01    	vinserti128 $0x1,%xmm12,%ymm13,%ymm12
    1876:	c4 62 1d 00 e0       	vpshufb %ymm0,%ymm12,%ymm12
    187b:	c4 c3 7d 39 dd 01    	vextracti128 $0x1,%ymm3,%xmm13
    1881:	c5 91 6c ed          	vpunpcklqdq %xmm5,%xmm13,%xmm5
    1885:	c4 e3 65 38 dd 01    	vinserti128 $0x1,%xmm5,%ymm3,%ymm3
    188b:	c4 e3 5d 38 e6 01    	vinserti128 $0x1,%xmm6,%ymm4,%ymm4
    1891:	c4 e3 4d 46 ef 21    	vperm2i128 $0x21,%ymm7,%ymm6,%ymm5
    1897:	c4 e3 fd 00 ed f4    	vpermq $0xf4,%ymm5,%ymm5
    189d:	c5 d5 6c ef          	vpunpcklqdq %ymm7,%ymm5,%ymm5
    18a1:	c4 a1 7d e7 1c 09    	vmovntdq %ymm3,(%rcx,%r9,1)
    18a7:	c4 a1 7d e7 64 09 20 	vmovntdq %ymm4,0x20(%rcx,%r9,1)
    18ae:	c4 a1 7d e7 6c 09 40 	vmovntdq %ymm5,0x40(%rcx,%r9,1)
    18b5:	c4 c2 75 36 dc       	vpermd %ymm12,%ymm1,%ymm3
    18ba:	c4 63 7d 39 c4 01    	vextracti128 $0x1,%ymm8,%xmm4
    18c0:	c4 c1 59 6c e2       	vpunpcklqdq %xmm10,%xmm4,%xmm4
    18c5:	c4 e3 3d 38 e4 01    	vinserti128 $0x1,%xmm4,%ymm8,%ymm4
    18cb:	c4 c3 35 38 eb 01    	vinserti128 $0x1,%xmm11,%ymm9,%ymm5
    18d1:	c4 e3 25 46 f3 21    	vperm2i128 $0x21,%ymm3,%ymm11,%ymm6
    18d7:	c4 e3 fd 00 f6 f4    	vpermq $0xf4,%ymm6,%ymm6
    18dd:	c5 cd 6c db          	vpunpcklqdq %ymm3,%ymm6,%ymm3
    18e1:	c4 a1 7d e7 64 09 60 	vmovntdq %ymm4,0x60(%rcx,%r9,1)
    18e8:	c4 a1 7d e7 ac 09 80 	vmovntdq %ymm5,0x80(%rcx,%r9,1)
    18ef:	00 00 00 
    18f2:	c4 a1 7d e7 9c 09 a0 	vmovntdq %ymm3,0xa0(%rcx,%r9,1)
    18f9:	00 00 00 
    18fc:	4d 8d 57 40          	lea    0x40(%r15),%r10
    1900:	49 81 c1 c0 00 00 00 	add    $0xc0,%r9
    1907:	49 81 c7 88 00 00 00 	add    $0x88,%r15
    190e:	4d 39 c7             	cmp    %r8,%r15
    1911:	4d 89 d7             	mov    %r10,%r15
    1914:	77 39                	ja     194f <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbbf>
    1916:	49 8d 87 96 01 00 00 	lea    0x196(%r15),%rax
    191d:	4c 39 c0             	cmp    %r8,%rax
    1920:	0f 87 1a f9 ff ff    	ja     1240 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x4b0>
    1926:	42 0f 18 84 0a 00 04 	prefetchnta 0x400(%rdx,%r9,1)
    192d:	00 00 
    192f:	42 0f 18 84 0a 40 04 	prefetchnta 0x440(%rdx,%r9,1)
    1936:	00 00 
    1938:	42 0f 18 84 0a 80 04 	prefetchnta 0x480(%rdx,%r9,1)
    193f:	00 00 
    1941:	42 0f 18 84 0a bf 04 	prefetchnta 0x4bf(%rdx,%r9,1)
    1948:	00 00 
    194a:	e9 f1 f8 ff ff       	jmp    1240 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x4b0>
    194f:	0f ae f8             	sfence
    1952:	49 8d 42 28          	lea    0x28(%r10),%rax
    1956:	4c 39 c0             	cmp    %r8,%rax
    1959:	0f 86 f8 f4 ff ff    	jbe    e57 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc7>
    195f:	4d 89 d1             	mov    %r10,%r9
    1962:	49 8d 41 08          	lea    0x8(%r9),%rax
    1966:	4c 39 c0             	cmp    %r8,%rax
    1969:	0f 87 90 f8 ff ff    	ja     11ff <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x46f>
    196f:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1973:	48 83 c0 10          	add    $0x10,%rax
    1977:	c4 e2 7d 5a 05 00 00 	vbroadcasti128 0x0(%rip),%ymm0        # 1980 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbf0>
    197e:	00 00 
    1980:	48 8b 5c 02 f0       	mov    -0x10(%rdx,%rax,1),%rbx
    1985:	4c 8b 64 02 f8       	mov    -0x8(%rdx,%rax,1),%r12
    198a:	4c 8b 14 02          	mov    (%rdx,%rax,1),%r10
    198e:	41 89 db             	mov    %ebx,%r11d
    1991:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1998:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    199d:	4d 89 e6             	mov    %r12,%r14
    19a0:	49 0f a4 de 10       	shld   $0x10,%rbx,%r14
    19a5:	48 c1 eb 18          	shr    $0x18,%rbx
    19a9:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    19af:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    19b3:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    19ba:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    19bf:	45 89 e7             	mov    %r12d,%r15d
    19c2:	41 c1 ef 08          	shr    $0x8,%r15d
    19c6:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    19cb:	4d 89 d5             	mov    %r10,%r13
    19ce:	4d 0f a4 e5 08       	shld   $0x8,%r12,%r13
    19d3:	49 c1 ec 20          	shr    $0x20,%r12
    19d7:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    19de:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    19e3:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    19ea:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    19ef:	4c 89 d5             	mov    %r10,%rbp
    19f2:	48 c1 ed 10          	shr    $0x10,%rbp
    19f6:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
    19fc:	0f b6 2c 2f          	movzbl (%rdi,%rbp,1),%ebp
    1a00:	49 c1 ea 28          	shr    $0x28,%r10
    1a04:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1a0a:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1a11:	c4 e3 71 22 0c ae 02 	vpinsrd $0x2,(%rsi,%rbp,4),%xmm1,%xmm1
    1a18:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
    1a1d:	c4 a3 71 22 0c 96 03 	vpinsrd $0x3,(%rsi,%r10,4),%xmm1,%xmm1
    1a24:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1a2a:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1a31:	c4 a3 69 22 14 b6 02 	vpinsrd $0x2,(%rsi,%r14,4),%xmm2,%xmm2
    1a38:	c4 a3 69 22 14 be 03 	vpinsrd $0x3,(%rsi,%r15,4),%xmm2,%xmm2
    1a3f:	c4 e3 6d 38 c9 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm1
    1a45:	c4 e2 75 00 c8       	vpshufb %ymm0,%ymm1,%ymm1
    1a4a:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
    1a50:	c5 e1 73 fa 0c       	vpslldq $0xc,%xmm2,%xmm3
    1a55:	c5 f1 eb cb          	vpor   %xmm3,%xmm1,%xmm1
    1a59:	c5 fa 7f 4c 01 f0    	vmovdqu %xmm1,-0x10(%rcx,%rax,1)
    1a5f:	c5 f9 70 ca e9       	vpshufd $0xe9,%xmm2,%xmm1
    1a64:	c5 f9 d6 0c 01       	vmovq  %xmm1,(%rcx,%rax,1)
    1a69:	4d 8d 51 08          	lea    0x8(%r9),%r10
    1a6d:	48 83 c0 18          	add    $0x18,%rax
    1a71:	49 83 c1 10          	add    $0x10,%r9
    1a75:	4d 39 c1             	cmp    %r8,%r9
    1a78:	4d 89 d1             	mov    %r10,%r9
    1a7b:	0f 86 ff fe ff ff    	jbe    1980 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbf0>
    1a81:	4d 39 d0             	cmp    %r10,%r8
    1a84:	0f 86 de 00 00 00    	jbe    1b68 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdd8>
    1a8a:	45 89 c1             	mov    %r8d,%r9d
    1a8d:	45 29 d1             	sub    %r10d,%r9d
    1a90:	4d 8d 72 01          	lea    0x1(%r10),%r14
    1a94:	41 f6 c1 01          	test   $0x1,%r9b
    1a98:	74 3d                	je     1ad7 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd47>
    1a9a:	4b 8d 1c 52          	lea    (%r10,%r10,2),%rbx
    1a9e:	44 0f b6 0c 1a       	movzbl (%rdx,%rbx,1),%r9d
    1aa3:	44 0f b6 54 1a 01    	movzbl 0x1(%rdx,%rbx,1),%r10d
    1aa9:	41 c1 e2 08          	shl    $0x8,%r10d
    1aad:	44 0f b6 5c 1a 02    	movzbl 0x2(%rdx,%rbx,1),%r11d
    1ab3:	41 c1 e3 10          	shl    $0x10,%r11d
    1ab7:	49 01 f9             	add    %rdi,%r9
    1aba:	4d 01 d1             	add    %r10,%r9
    1abd:	47 0f b6 0c 0b       	movzbl (%r11,%r9,1),%r9d
    1ac2:	42 8b 04 8e          	mov    (%rsi,%r9,4),%eax
    1ac6:	88 04 19             	mov    %al,(%rcx,%rbx,1)
    1ac9:	88 64 19 01          	mov    %ah,0x1(%rcx,%rbx,1)
    1acd:	c1 e8 10             	shr    $0x10,%eax
    1ad0:	88 44 19 02          	mov    %al,0x2(%rcx,%rbx,1)
    1ad4:	4d 89 f2             	mov    %r14,%r10
    1ad7:	4d 39 f0             	cmp    %r14,%r8
    1ada:	0f 84 88 00 00 00    	je     1b68 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdd8>
    1ae0:	4b 8d 04 52          	lea    (%r10,%r10,2),%rax
    1ae4:	48 83 c0 05          	add    $0x5,%rax
    1ae8:	4d 29 d0             	sub    %r10,%r8
    1aeb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1af0:	44 0f b6 4c 02 fb    	movzbl -0x5(%rdx,%rax,1),%r9d
    1af6:	44 0f b6 54 02 fc    	movzbl -0x4(%rdx,%rax,1),%r10d
    1afc:	41 c1 e2 08          	shl    $0x8,%r10d
    1b00:	44 0f b6 5c 02 fd    	movzbl -0x3(%rdx,%rax,1),%r11d
    1b06:	41 c1 e3 10          	shl    $0x10,%r11d
    1b0a:	49 01 f9             	add    %rdi,%r9
    1b0d:	4d 01 d1             	add    %r10,%r9
    1b10:	47 0f b6 0c 0b       	movzbl (%r11,%r9,1),%r9d
    1b15:	42 8b 1c 8e          	mov    (%rsi,%r9,4),%ebx
    1b19:	88 5c 01 fb          	mov    %bl,-0x5(%rcx,%rax,1)
    1b1d:	88 7c 01 fc          	mov    %bh,-0x4(%rcx,%rax,1)
    1b21:	c1 eb 10             	shr    $0x10,%ebx
    1b24:	88 5c 01 fd          	mov    %bl,-0x3(%rcx,%rax,1)
    1b28:	44 0f b6 4c 02 fe    	movzbl -0x2(%rdx,%rax,1),%r9d
    1b2e:	44 0f b6 54 02 ff    	movzbl -0x1(%rdx,%rax,1),%r10d
    1b34:	41 c1 e2 08          	shl    $0x8,%r10d
    1b38:	44 0f b6 1c 02       	movzbl (%rdx,%rax,1),%r11d
    1b3d:	41 c1 e3 10          	shl    $0x10,%r11d
    1b41:	49 01 f9             	add    %rdi,%r9
    1b44:	4d 01 d1             	add    %r10,%r9
    1b47:	47 0f b6 0c 0b       	movzbl (%r11,%r9,1),%r9d
    1b4c:	42 8b 1c 8e          	mov    (%rsi,%r9,4),%ebx
    1b50:	88 5c 01 fe          	mov    %bl,-0x2(%rcx,%rax,1)
    1b54:	88 7c 01 ff          	mov    %bh,-0x1(%rcx,%rax,1)
    1b58:	c1 eb 10             	shr    $0x10,%ebx
    1b5b:	88 1c 01             	mov    %bl,(%rcx,%rax,1)
    1b5e:	48 83 c0 06          	add    $0x6,%rax
    1b62:	49 83 c0 fe          	add    $0xfffffffffffffffe,%r8
    1b66:	75 88                	jne    1af0 <jshc_channel::avx2_chain_batchspan_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd60>
    1b68:	5b                   	pop    %rbx
    1b69:	41 5c                	pop    %r12
    1b6b:	41 5d                	pop    %r13
    1b6d:	41 5e                	pop    %r14
    1b6f:	41 5f                	pop    %r15
    1b71:	5d                   	pop    %rbp
    1b72:	c5 f8 77             	vzeroupper
    1b75:	c3                   	ret
