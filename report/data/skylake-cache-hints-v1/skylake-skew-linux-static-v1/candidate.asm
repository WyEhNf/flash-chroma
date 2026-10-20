
artifacts/skylake-skew-linux-build-v1/CMakeFiles/jshc_skylake_skew.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	55                   	push   %rbp
       5:	48 89 e5             	mov    %rsp,%rbp
       8:	41 57                	push   %r15
       a:	41 56                	push   %r14
       c:	41 55                	push   %r13
       e:	41 54                	push   %r12
      10:	53                   	push   %rbx
      11:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
      15:	48 83 ec 08          	sub    $0x8,%rsp
      19:	48 89 0c 24          	mov    %rcx,(%rsp)
      1d:	48 85 c9             	test   %rcx,%rcx
      20:	0f 84 9d 13 00 00    	je     13c3 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c3>
      26:	b8 00 04 00 00       	mov    $0x400,%eax
      2b:	49 89 fe             	mov    %rdi,%r14
      2e:	48 89 d7             	mov    %rdx,%rdi
      31:	49 89 f7             	mov    %rsi,%r15
      34:	48 8d 14 49          	lea    (%rcx,%rcx,2),%rdx
      38:	48 39 c2             	cmp    %rax,%rdx
      3b:	48 0f 47 d0          	cmova  %rax,%rdx
      3f:	31 c0                	xor    %eax,%eax
      41:	0f 1f 40 00          	nopl   0x0(%rax)
      45:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
      4c:	00 00 00 00 
      50:	0f 18 04 07          	prefetchnta (%rdi,%rax,1)
      54:	48 83 c0 40          	add    $0x40,%rax
      58:	48 39 d0             	cmp    %rdx,%rax
      5b:	72 f3                	jb     50 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x50>
      5d:	48 8b 34 24          	mov    (%rsp),%rsi
      61:	48 89 f9             	mov    %rdi,%rcx
      64:	31 d2                	xor    %edx,%edx
      66:	eb 54                	jmp    bc <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbc>
      68:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
      6f:	00 
      70:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
      74:	44 0f b6 41 02       	movzbl 0x2(%rcx),%r8d
      79:	48 ff c2             	inc    %rdx
      7c:	48 83 c1 03          	add    $0x3,%rcx
      80:	41 c1 e0 10          	shl    $0x10,%r8d
      84:	c1 e0 08             	shl    $0x8,%eax
      87:	44 09 c0             	or     %r8d,%eax
      8a:	44 0f b6 41 fd       	movzbl -0x3(%rcx),%r8d
      8f:	41 09 c0             	or     %eax,%r8d
      92:	c1 e8 0a             	shr    $0xa,%eax
      95:	44 31 c0             	xor    %r8d,%eax
      98:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
      9d:	4d 8d 04 87          	lea    (%r15,%rax,4),%r8
      a1:	41 8b 00             	mov    (%r8),%eax
      a4:	45 0f b7 00          	movzwl (%r8),%r8d
      a8:	c1 e8 10             	shr    $0x10,%eax
      ab:	66 44 89 41 fd       	mov    %r8w,-0x3(%rcx)
      b0:	88 41 ff             	mov    %al,-0x1(%rcx)
      b3:	48 39 d6             	cmp    %rdx,%rsi
      b6:	0f 84 1c 13 00 00    	je     13d8 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13d8>
      bc:	f6 c1 3f             	test   $0x3f,%cl
      bf:	75 af                	jne    70 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x70>
      c1:	48 8d 42 48          	lea    0x48(%rdx),%rax
      c5:	48 39 04 24          	cmp    %rax,(%rsp)
      c9:	0f 82 17 13 00 00    	jb     13e6 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13e6>
      cf:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
      d3:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # db <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xdb>
      da:	00 
      db:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # e3 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe3>
      e2:	00 
      e3:	48 89 7c 24 f0       	mov    %rdi,-0x10(%rsp)
      e8:	4c 8b 04 24          	mov    (%rsp),%r8
      ec:	48 01 f8             	add    %rdi,%rax
      ef:	eb 0a                	jmp    fb <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xfb>
      f1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
      f8:	48 89 f2             	mov    %rsi,%rdx
      fb:	48 8d 8a 96 01 00 00 	lea    0x196(%rdx),%rcx
     102:	49 39 c8             	cmp    %rcx,%r8
     105:	72 1c                	jb     123 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x123>
     107:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
     10e:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
     115:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     11c:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     123:	44 8b 10             	mov    (%rax),%r10d
     126:	44 8b 48 03          	mov    0x3(%rax),%r9d
     12a:	8b 58 06             	mov    0x6(%rax),%ebx
     12d:	44 8b 58 09          	mov    0x9(%rax),%r11d
     131:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     138:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     13f:	44 8b 68 0c          	mov    0xc(%rax),%r13d
     143:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     147:	44 89 d6             	mov    %r10d,%esi
     14a:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     150:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     157:	8b 48 12             	mov    0x12(%rax),%ecx
     15a:	c1 ee 0a             	shr    $0xa,%esi
     15d:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     164:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     16b:	8b 78 15             	mov    0x15(%rax),%edi
     16e:	44 31 d6             	xor    %r10d,%esi
     171:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     177:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     17c:	44 89 ce             	mov    %r9d,%esi
     17f:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     185:	c1 ee 0a             	shr    $0xa,%esi
     188:	44 31 ce             	xor    %r9d,%esi
     18b:	c4 01 79 6e 0c 97    	vmovd  (%r15,%r10,4),%xmm9
     191:	44 8b 50 18          	mov    0x18(%rax),%r10d
     195:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     19a:	89 de                	mov    %ebx,%esi
     19c:	c1 ee 0a             	shr    $0xa,%esi
     19f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     1a6:	31 de                	xor    %ebx,%esi
     1a8:	c4 03 31 22 0c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm9,%xmm9
     1af:	44 8b 48 1b          	mov    0x1b(%rax),%r9d
     1b3:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     1b8:	44 89 de             	mov    %r11d,%esi
     1bb:	c1 ee 0a             	shr    $0xa,%esi
     1be:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     1c5:	44 31 de             	xor    %r11d,%esi
     1c8:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     1cd:	44 89 ee             	mov    %r13d,%esi
     1d0:	c1 ee 0a             	shr    $0xa,%esi
     1d3:	44 31 ee             	xor    %r13d,%esi
     1d6:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     1db:	44 89 e6             	mov    %r12d,%esi
     1de:	c1 ee 0a             	shr    $0xa,%esi
     1e1:	44 31 e6             	xor    %r12d,%esi
     1e4:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
     1ea:	44 8b 68 24          	mov    0x24(%rax),%r13d
     1ee:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     1f3:	89 ce                	mov    %ecx,%esi
     1f5:	c1 ee 0a             	shr    $0xa,%esi
     1f8:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     1ff:	31 ce                	xor    %ecx,%esi
     201:	89 f9                	mov    %edi,%ecx
     203:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
     20a:	44 8b 60 27          	mov    0x27(%rax),%r12d
     20e:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     213:	c1 e9 0a             	shr    $0xa,%ecx
     216:	31 f9                	xor    %edi,%ecx
     218:	8b 78 2d             	mov    0x2d(%rax),%edi
     21b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     222:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     227:	c4 c1 79 6e 0c b7    	vmovd  (%r15,%rsi,4),%xmm1
     22d:	44 89 d6             	mov    %r10d,%esi
     230:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     236:	c4 c3 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm1,%xmm1
     23d:	8b 48 2a             	mov    0x2a(%rax),%ecx
     240:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     244:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
     24a:	8b 58 1e             	mov    0x1e(%rax),%ebx
     24d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     253:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
     25a:	44 8b 58 21          	mov    0x21(%rax),%r11d
     25e:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     264:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     26b:	c1 ee 0a             	shr    $0xa,%esi
     26e:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     272:	44 31 d6             	xor    %r10d,%esi
     275:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     27b:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     280:	44 89 ce             	mov    %r9d,%esi
     283:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     288:	c1 ee 0a             	shr    $0xa,%esi
     28b:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     290:	44 31 ce             	xor    %r9d,%esi
     293:	c4 81 79 6e 34 97    	vmovd  (%r15,%r10,4),%xmm6
     299:	44 8b 50 30          	mov    0x30(%rax),%r10d
     29d:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     2a2:	89 de                	mov    %ebx,%esi
     2a4:	c1 ee 0a             	shr    $0xa,%esi
     2a7:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     2ae:	31 de                	xor    %ebx,%esi
     2b0:	c4 83 49 22 34 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm6,%xmm6
     2b7:	44 8b 48 33          	mov    0x33(%rax),%r9d
     2bb:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     2c0:	44 89 de             	mov    %r11d,%esi
     2c3:	c1 ee 0a             	shr    $0xa,%esi
     2c6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     2cd:	44 31 de             	xor    %r11d,%esi
     2d0:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     2d5:	44 89 ee             	mov    %r13d,%esi
     2d8:	c1 ee 0a             	shr    $0xa,%esi
     2db:	44 31 ee             	xor    %r13d,%esi
     2de:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     2e3:	44 89 e6             	mov    %r12d,%esi
     2e6:	c1 ee 0a             	shr    $0xa,%esi
     2e9:	44 31 e6             	xor    %r12d,%esi
     2ec:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
     2f2:	44 8b 68 3c          	mov    0x3c(%rax),%r13d
     2f6:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     2fb:	89 ce                	mov    %ecx,%esi
     2fd:	c1 ee 0a             	shr    $0xa,%esi
     300:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     307:	31 ce                	xor    %ecx,%esi
     309:	89 f9                	mov    %edi,%ecx
     30b:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
     312:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
     316:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     31b:	c1 e9 0a             	shr    $0xa,%ecx
     31e:	31 f9                	xor    %edi,%ecx
     320:	8b 78 45             	mov    0x45(%rax),%edi
     323:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     32a:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     32f:	c4 c1 79 6e 0c b7    	vmovd  (%r15,%rsi,4),%xmm1
     335:	44 89 d6             	mov    %r10d,%esi
     338:	c1 ee 0a             	shr    $0xa,%esi
     33b:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     341:	c4 c3 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm1,%xmm1
     348:	44 31 d6             	xor    %r10d,%esi
     34b:	8b 48 42             	mov    0x42(%rax),%ecx
     34e:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     353:	44 89 ce             	mov    %r9d,%esi
     356:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     35a:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
     360:	8b 58 36             	mov    0x36(%rax),%ebx
     363:	c1 ee 0a             	shr    $0xa,%esi
     366:	44 31 ce             	xor    %r9d,%esi
     369:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     36f:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     375:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     37a:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
     381:	89 de                	mov    %ebx,%esi
     383:	44 8b 58 39          	mov    0x39(%rax),%r11d
     387:	c1 ee 0a             	shr    $0xa,%esi
     38a:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     38e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     395:	31 de                	xor    %ebx,%esi
     397:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     39d:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     3a2:	44 89 de             	mov    %r11d,%esi
     3a5:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     3aa:	c1 ee 0a             	shr    $0xa,%esi
     3ad:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     3b2:	44 31 de             	xor    %r11d,%esi
     3b5:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     3b9:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     3bf:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     3c4:	44 89 ee             	mov    %r13d,%esi
     3c7:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     3cd:	c1 ee 0a             	shr    $0xa,%esi
     3d0:	44 31 ee             	xor    %r13d,%esi
     3d3:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     3d8:	44 89 e6             	mov    %r12d,%esi
     3db:	c1 ee 0a             	shr    $0xa,%esi
     3de:	44 31 e6             	xor    %r12d,%esi
     3e1:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     3e6:	89 ce                	mov    %ecx,%esi
     3e8:	c1 ee 0a             	shr    $0xa,%esi
     3eb:	31 ce                	xor    %ecx,%esi
     3ed:	89 f9                	mov    %edi,%ecx
     3ef:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     3f4:	c1 e9 0a             	shr    $0xa,%ecx
     3f7:	31 f9                	xor    %edi,%ecx
     3f9:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     3fe:	c4 c1 79 6e 0c b7    	vmovd  (%r15,%rsi,4),%xmm1
     404:	c4 81 79 6e 2c 97    	vmovd  (%r15,%r10,4),%xmm5
     40a:	44 8b 50 48          	mov    0x48(%rax),%r10d
     40e:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
     414:	c4 c3 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm1,%xmm1
     41b:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     422:	c4 83 51 22 2c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm5,%xmm5
     429:	44 8b 48 4b          	mov    0x4b(%rax),%r9d
     42d:	44 89 d6             	mov    %r10d,%esi
     430:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
     437:	44 8b 68 54          	mov    0x54(%rax),%r13d
     43b:	c1 ee 0a             	shr    $0xa,%esi
     43e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     445:	44 8b 60 57          	mov    0x57(%rax),%r12d
     449:	8b 48 5a             	mov    0x5a(%rax),%ecx
     44c:	44 31 d6             	xor    %r10d,%esi
     44f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     453:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
     459:	8b 58 4e             	mov    0x4e(%rax),%ebx
     45c:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     461:	44 89 ce             	mov    %r9d,%esi
     464:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     46b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     472:	c1 ee 0a             	shr    $0xa,%esi
     475:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     47b:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
     482:	44 8b 58 51          	mov    0x51(%rax),%r11d
     486:	44 31 ce             	xor    %r9d,%esi
     489:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     48f:	8b 78 5d             	mov    0x5d(%rax),%edi
     492:	c4 01 79 6e 04 97    	vmovd  (%r15,%r10,4),%xmm8
     498:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     49d:	89 de                	mov    %ebx,%esi
     49f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     4a6:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     4aa:	c1 ee 0a             	shr    $0xa,%esi
     4ad:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     4b3:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     4b9:	31 de                	xor    %ebx,%esi
     4bb:	c4 03 39 22 04 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm8,%xmm8
     4c2:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     4c7:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     4cc:	44 89 de             	mov    %r11d,%esi
     4cf:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     4d4:	c1 ee 0a             	shr    $0xa,%esi
     4d7:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     4db:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     4e1:	44 31 de             	xor    %r11d,%esi
     4e4:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     4ea:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     4ef:	44 89 ee             	mov    %r13d,%esi
     4f2:	c1 ee 0a             	shr    $0xa,%esi
     4f5:	44 31 ee             	xor    %r13d,%esi
     4f8:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     4fd:	44 89 e6             	mov    %r12d,%esi
     500:	c1 ee 0a             	shr    $0xa,%esi
     503:	44 31 e6             	xor    %r12d,%esi
     506:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
     50c:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     511:	89 ce                	mov    %ecx,%esi
     513:	c1 ee 0a             	shr    $0xa,%esi
     516:	31 ce                	xor    %ecx,%esi
     518:	89 f9                	mov    %edi,%ecx
     51a:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
     521:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     526:	c1 e9 0a             	shr    $0xa,%ecx
     529:	31 f9                	xor    %edi,%ecx
     52b:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     530:	c4 c1 79 6e 0c b7    	vmovd  (%r15,%rsi,4),%xmm1
     536:	c4 c3 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm1,%xmm1
     53d:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     541:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
     547:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
     54e:	8b 78 75             	mov    0x75(%rax),%edi
     551:	44 8b 50 60          	mov    0x60(%rax),%r10d
     555:	44 8b 48 63          	mov    0x63(%rax),%r9d
     559:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     55f:	8b 58 66             	mov    0x66(%rax),%ebx
     562:	44 8b 58 69          	mov    0x69(%rax),%r11d
     566:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     56a:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     571:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     578:	44 8b 68 6c          	mov    0x6c(%rax),%r13d
     57c:	44 8b 60 6f          	mov    0x6f(%rax),%r12d
     580:	44 89 d6             	mov    %r10d,%esi
     583:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     589:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     590:	8b 48 72             	mov    0x72(%rax),%ecx
     593:	c1 ee 0a             	shr    $0xa,%esi
     596:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     59d:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     5a3:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5aa:	44 31 d6             	xor    %r10d,%esi
     5ad:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     5b3:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     5b8:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     5bd:	44 89 ce             	mov    %r9d,%esi
     5c0:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     5c5:	c1 ee 0a             	shr    $0xa,%esi
     5c8:	44 31 ce             	xor    %r9d,%esi
     5cb:	c4 81 79 6e 3c 97    	vmovd  (%r15,%r10,4),%xmm7
     5d1:	44 8b 50 78          	mov    0x78(%rax),%r10d
     5d5:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     5da:	89 de                	mov    %ebx,%esi
     5dc:	c1 ee 0a             	shr    $0xa,%esi
     5df:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     5e6:	31 de                	xor    %ebx,%esi
     5e8:	c4 83 41 22 3c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm7,%xmm7
     5ef:	44 8b 48 7b          	mov    0x7b(%rax),%r9d
     5f3:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     5f8:	44 89 de             	mov    %r11d,%esi
     5fb:	c1 ee 0a             	shr    $0xa,%esi
     5fe:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     605:	44 31 de             	xor    %r11d,%esi
     608:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     60d:	44 89 ee             	mov    %r13d,%esi
     610:	c1 ee 0a             	shr    $0xa,%esi
     613:	44 31 ee             	xor    %r13d,%esi
     616:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     61b:	44 89 e6             	mov    %r12d,%esi
     61e:	c1 ee 0a             	shr    $0xa,%esi
     621:	44 31 e6             	xor    %r12d,%esi
     624:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
     62a:	44 8b a8 84 00 00 00 	mov    0x84(%rax),%r13d
     631:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     636:	89 ce                	mov    %ecx,%esi
     638:	c1 ee 0a             	shr    $0xa,%esi
     63b:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     642:	31 ce                	xor    %ecx,%esi
     644:	89 f9                	mov    %edi,%ecx
     646:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
     64d:	44 8b a0 87 00 00 00 	mov    0x87(%rax),%r12d
     654:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     659:	c1 e9 0a             	shr    $0xa,%ecx
     65c:	31 f9                	xor    %edi,%ecx
     65e:	8b b8 8d 00 00 00    	mov    0x8d(%rax),%edi
     664:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     66b:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     670:	c4 c1 79 6e 0c b7    	vmovd  (%r15,%rsi,4),%xmm1
     676:	44 89 d6             	mov    %r10d,%esi
     679:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     67f:	c4 c3 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm1,%xmm1
     686:	8b 88 8a 00 00 00    	mov    0x8a(%rax),%ecx
     68c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     690:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
     696:	8b 58 7e             	mov    0x7e(%rax),%ebx
     699:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     69f:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
     6a6:	44 8b 98 81 00 00 00 	mov    0x81(%rax),%r11d
     6ad:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     6b3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     6ba:	c1 ee 0a             	shr    $0xa,%esi
     6bd:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     6c1:	44 31 d6             	xor    %r10d,%esi
     6c4:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     6ca:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     6cf:	44 89 ce             	mov    %r9d,%esi
     6d2:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     6d7:	c1 ee 0a             	shr    $0xa,%esi
     6da:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     6df:	44 31 ce             	xor    %r9d,%esi
     6e2:	c4 81 79 6e 04 97    	vmovd  (%r15,%r10,4),%xmm0
     6e8:	44 8b 90 90 00 00 00 	mov    0x90(%rax),%r10d
     6ef:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     6f4:	89 de                	mov    %ebx,%esi
     6f6:	c1 ee 0a             	shr    $0xa,%esi
     6f9:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     700:	31 de                	xor    %ebx,%esi
     702:	c4 83 79 22 04 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm0,%xmm0
     709:	44 8b 88 93 00 00 00 	mov    0x93(%rax),%r9d
     710:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     715:	44 89 de             	mov    %r11d,%esi
     718:	c1 ee 0a             	shr    $0xa,%esi
     71b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     722:	44 31 de             	xor    %r11d,%esi
     725:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     72a:	44 89 ee             	mov    %r13d,%esi
     72d:	c1 ee 0a             	shr    $0xa,%esi
     730:	44 31 ee             	xor    %r13d,%esi
     733:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     738:	44 89 e6             	mov    %r12d,%esi
     73b:	c1 ee 0a             	shr    $0xa,%esi
     73e:	44 31 e6             	xor    %r12d,%esi
     741:	c4 81 79 6e 0c af    	vmovd  (%r15,%r13,4),%xmm1
     747:	44 8b a8 9c 00 00 00 	mov    0x9c(%rax),%r13d
     74e:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     753:	89 ce                	mov    %ecx,%esi
     755:	c1 ee 0a             	shr    $0xa,%esi
     758:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     75f:	31 ce                	xor    %ecx,%esi
     761:	89 f9                	mov    %edi,%ecx
     763:	c4 83 71 22 0c a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm1,%xmm1
     76a:	44 8b a0 9f 00 00 00 	mov    0x9f(%rax),%r12d
     771:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     776:	c1 e9 0a             	shr    $0xa,%ecx
     779:	31 f9                	xor    %edi,%ecx
     77b:	8b b8 a5 00 00 00    	mov    0xa5(%rax),%edi
     781:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     788:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     78d:	c4 c1 79 6e 14 b7    	vmovd  (%r15,%rsi,4),%xmm2
     793:	44 89 d6             	mov    %r10d,%esi
     796:	c1 ee 0a             	shr    $0xa,%esi
     799:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     79f:	c4 c3 69 22 14 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm2,%xmm2
     7a6:	44 31 d6             	xor    %r10d,%esi
     7a9:	8b 88 a2 00 00 00    	mov    0xa2(%rax),%ecx
     7af:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     7b4:	44 89 ce             	mov    %r9d,%esi
     7b7:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     7bb:	c4 c1 79 6e 14 9f    	vmovd  (%r15,%rbx,4),%xmm2
     7c1:	8b 98 96 00 00 00    	mov    0x96(%rax),%ebx
     7c7:	c1 ee 0a             	shr    $0xa,%esi
     7ca:	44 31 ce             	xor    %r9d,%esi
     7cd:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     7d3:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     7d9:	c4 83 69 22 14 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm2,%xmm2
     7e0:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     7e5:	44 8b 98 99 00 00 00 	mov    0x99(%rax),%r11d
     7ec:	89 de                	mov    %ebx,%esi
     7ee:	c1 ee 0a             	shr    $0xa,%esi
     7f1:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     7f5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     7fc:	31 de                	xor    %ebx,%esi
     7fe:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     804:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     809:	44 89 de             	mov    %r11d,%esi
     80c:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     811:	c1 ee 0a             	shr    $0xa,%esi
     814:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     819:	44 31 de             	xor    %r11d,%esi
     81c:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     821:	44 89 ee             	mov    %r13d,%esi
     824:	c1 ee 0a             	shr    $0xa,%esi
     827:	44 31 ee             	xor    %r13d,%esi
     82a:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     82f:	44 89 e6             	mov    %r12d,%esi
     832:	c1 ee 0a             	shr    $0xa,%esi
     835:	44 31 e6             	xor    %r12d,%esi
     838:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     83d:	89 ce                	mov    %ecx,%esi
     83f:	c1 ee 0a             	shr    $0xa,%esi
     842:	31 ce                	xor    %ecx,%esi
     844:	89 f9                	mov    %edi,%ecx
     846:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     84b:	c1 e9 0a             	shr    $0xa,%ecx
     84e:	31 f9                	xor    %edi,%ecx
     850:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     855:	c4 41 79 6e 14 b7    	vmovd  (%r15,%rsi,4),%xmm10
     85b:	c4 81 79 6e 0c 97    	vmovd  (%r15,%r10,4),%xmm1
     861:	44 8b 90 a8 00 00 00 	mov    0xa8(%rax),%r10d
     868:	c4 81 79 6e 14 af    	vmovd  (%r15,%r13,4),%xmm2
     86e:	c4 43 29 22 14 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm10,%xmm10
     875:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     87c:	c4 83 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm1,%xmm1
     883:	44 8b 88 ab 00 00 00 	mov    0xab(%rax),%r9d
     88a:	44 89 d6             	mov    %r10d,%esi
     88d:	c4 83 69 22 14 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm2,%xmm2
     894:	44 8b a8 b4 00 00 00 	mov    0xb4(%rax),%r13d
     89b:	c1 ee 0a             	shr    $0xa,%esi
     89e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     8a5:	44 8b a0 b7 00 00 00 	mov    0xb7(%rax),%r12d
     8ac:	8b 88 ba 00 00 00    	mov    0xba(%rax),%ecx
     8b2:	44 31 d6             	xor    %r10d,%esi
     8b5:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
     8ba:	c4 41 79 6e 14 9f    	vmovd  (%r15,%rbx,4),%xmm10
     8c0:	8b 98 ae 00 00 00    	mov    0xae(%rax),%ebx
     8c6:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
     8cb:	44 89 ce             	mov    %r9d,%esi
     8ce:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     8d5:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     8dc:	c1 ee 0a             	shr    $0xa,%esi
     8df:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     8e5:	c4 03 29 22 14 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm10,%xmm10
     8ec:	44 8b 98 b1 00 00 00 	mov    0xb1(%rax),%r11d
     8f3:	44 31 ce             	xor    %r9d,%esi
     8f6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     8fc:	8b b8 bd 00 00 00    	mov    0xbd(%rax),%edi
     902:	45 0f b6 0c 36       	movzbl (%r14,%rsi,1),%r9d
     907:	89 de                	mov    %ebx,%esi
     909:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     910:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     915:	c1 ee 0a             	shr    $0xa,%esi
     918:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     91e:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     924:	c4 81 79 6e 14 97    	vmovd  (%r15,%r10,4),%xmm2
     92a:	31 de                	xor    %ebx,%esi
     92c:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     931:	41 0f b6 1c 36       	movzbl (%r14,%rsi,1),%ebx
     936:	44 89 de             	mov    %r11d,%esi
     939:	c4 83 69 22 14 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm2,%xmm2
     940:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     945:	c1 ee 0a             	shr    $0xa,%esi
     948:	44 31 de             	xor    %r11d,%esi
     94b:	45 0f b6 1c 36       	movzbl (%r14,%rsi,1),%r11d
     950:	44 89 ee             	mov    %r13d,%esi
     953:	c1 ee 0a             	shr    $0xa,%esi
     956:	44 31 ee             	xor    %r13d,%esi
     959:	45 0f b6 2c 36       	movzbl (%r14,%rsi,1),%r13d
     95e:	44 89 e6             	mov    %r12d,%esi
     961:	c1 ee 0a             	shr    $0xa,%esi
     964:	44 31 e6             	xor    %r12d,%esi
     967:	c4 01 79 6e 14 af    	vmovd  (%r15,%r13,4),%xmm10
     96d:	45 0f b6 24 36       	movzbl (%r14,%rsi,1),%r12d
     972:	89 ce                	mov    %ecx,%esi
     974:	c1 ee 0a             	shr    $0xa,%esi
     977:	31 ce                	xor    %ecx,%esi
     979:	89 f9                	mov    %edi,%ecx
     97b:	c4 03 29 22 14 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm10,%xmm10
     982:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
     987:	c1 e9 0a             	shr    $0xa,%ecx
     98a:	31 f9                	xor    %edi,%ecx
     98c:	48 05 c0 00 00 00    	add    $0xc0,%rax
     992:	41 0f b6 0c 0e       	movzbl (%r14,%rcx,1),%ecx
     997:	c4 41 79 6e 1c b7    	vmovd  (%r15,%rsi,4),%xmm11
     99d:	48 8d 72 40          	lea    0x40(%rdx),%rsi
     9a1:	c4 43 21 22 1c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm11,%xmm11
     9a8:	48 8d 8a 88 00 00 00 	lea    0x88(%rdx),%rcx
     9af:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
     9b4:	c4 41 79 6e 1c 9f    	vmovd  (%r15,%rbx,4),%xmm11
     9ba:	c4 03 21 22 1c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm11,%xmm11
     9c1:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     9c6:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     9cb:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     9d1:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     9d7:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     9dc:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     9e2:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     9e8:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     9ed:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     9f2:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     9f7:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     9fc:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     a02:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     a08:	c5 7d e7 88 40 ff ff 	vmovntdq %ymm9,-0xc0(%rax)
     a0f:	ff 
     a10:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     a14:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     a18:	c5 fd e7 b0 60 ff ff 	vmovntdq %ymm6,-0xa0(%rax)
     a1f:	ff 
     a20:	c5 fd e7 68 80       	vmovntdq %ymm5,-0x80(%rax)
     a25:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     a29:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     a2d:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     a33:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     a39:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     a3f:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     a45:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     a4a:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     a4e:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     a54:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     a5a:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     a60:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     a66:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     a6c:	c5 fd e7 68 a0       	vmovntdq %ymm5,-0x60(%rax)
     a71:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     a76:	c5 fd e7 48 e0       	vmovntdq %ymm1,-0x20(%rax)
     a7b:	49 39 c8             	cmp    %rcx,%r8
     a7e:	0f 83 74 f6 ff ff    	jae    f8 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf8>
     a84:	48 89 74 24 f8       	mov    %rsi,-0x8(%rsp)
     a89:	48 8b 7c 24 f0       	mov    -0x10(%rsp),%rdi
     a8e:	48 8d 42 68          	lea    0x68(%rdx),%rax
     a92:	0f ae f8             	sfence
     a95:	48 39 04 24          	cmp    %rax,(%rsp)
     a99:	0f 82 93 05 00 00    	jb     1032 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1032>
     a9f:	48 8b 44 24 f8       	mov    -0x8(%rsp),%rax
     aa4:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # aac <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xaac>
     aab:	00 
     aac:	48 89 7c 24 90       	mov    %rdi,-0x70(%rsp)
     ab1:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # ab9 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xab9>
     ab8:	00 
     ab9:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
     abd:	4c 8d 1c 07          	lea    (%rdi,%rax,1),%r11
     ac1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     ac8:	41 8b 7b 09          	mov    0x9(%r11),%edi
     acc:	41 8b 73 06          	mov    0x6(%r11),%esi
     ad0:	41 8b 4b 03          	mov    0x3(%r11),%ecx
     ad4:	41 8b 13             	mov    (%r11),%edx
     ad7:	41 8b 43 27          	mov    0x27(%r11),%eax
     adb:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     ae1:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     ae7:	41 8b 5b 15          	mov    0x15(%r11),%ebx
     aeb:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     af1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     af7:	45 8b 53 12          	mov    0x12(%r11),%r10d
     afb:	45 8b 4b 0f          	mov    0xf(%r11),%r9d
     aff:	25 ff ff ff 00       	and    $0xffffff,%eax
     b04:	45 8b 43 0c          	mov    0xc(%r11),%r8d
     b08:	45 8b 63 2d          	mov    0x2d(%r11),%r12d
     b0c:	89 7c 24 e0          	mov    %edi,-0x20(%rsp)
     b10:	45 8b 6b 2a          	mov    0x2a(%r11),%r13d
     b14:	41 8b 7b 21          	mov    0x21(%r11),%edi
     b18:	89 74 24 dc          	mov    %esi,-0x24(%rsp)
     b1c:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     b22:	41 8b 73 1e          	mov    0x1e(%r11),%esi
     b26:	89 4c 24 d8          	mov    %ecx,-0x28(%rsp)
     b2a:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     b31:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b38:	41 8b 4b 1b          	mov    0x1b(%r11),%ecx
     b3c:	89 54 24 d4          	mov    %edx,-0x2c(%rsp)
     b40:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     b47:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     b4e:	41 8b 53 18          	mov    0x18(%r11),%edx
     b52:	89 44 24 c8          	mov    %eax,-0x38(%rsp)
     b56:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     b5d:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
     b63:	41 8b 43 24          	mov    0x24(%r11),%eax
     b67:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
     b6d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     b73:	89 5c 24 f0          	mov    %ebx,-0x10(%rsp)
     b77:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     b7d:	44 89 54 24 ec       	mov    %r10d,-0x14(%rsp)
     b82:	25 ff ff ff 00       	and    $0xffffff,%eax
     b87:	44 89 4c 24 e8       	mov    %r9d,-0x18(%rsp)
     b8c:	44 89 44 24 e4       	mov    %r8d,-0x1c(%rsp)
     b91:	44 89 6c 24 cc       	mov    %r13d,-0x34(%rsp)
     b96:	89 44 24 c4          	mov    %eax,-0x3c(%rsp)
     b9a:	89 7c 24 c0          	mov    %edi,-0x40(%rsp)
     b9e:	89 74 24 bc          	mov    %esi,-0x44(%rsp)
     ba2:	89 4c 24 b8          	mov    %ecx,-0x48(%rsp)
     ba6:	89 54 24 b4          	mov    %edx,-0x4c(%rsp)
     baa:	44 89 64 24 d0       	mov    %r12d,-0x30(%rsp)
     baf:	45 8b 63 45          	mov    0x45(%r11),%r12d
     bb3:	41 8b 43 39          	mov    0x39(%r11),%eax
     bb7:	45 8b 4b 3f          	mov    0x3f(%r11),%r9d
     bbb:	45 8b 53 42          	mov    0x42(%r11),%r10d
     bbf:	45 8b 6b 3c          	mov    0x3c(%r11),%r13d
     bc3:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     bca:	25 ff ff ff 00       	and    $0xffffff,%eax
     bcf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bd6:	45 8b 43 36          	mov    0x36(%r11),%r8d
     bda:	41 8b 53 4b          	mov    0x4b(%r11),%edx
     bde:	89 44 24 a0          	mov    %eax,-0x60(%rsp)
     be2:	41 8b 43 33          	mov    0x33(%r11),%eax
     be6:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     bed:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     bf4:	44 89 4c 24 a8       	mov    %r9d,-0x58(%rsp)
     bf9:	45 8b 4b 48          	mov    0x48(%r11),%r9d
     bfd:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     c04:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     c0a:	25 ff ff ff 00       	and    $0xffffff,%eax
     c0f:	41 8b 5b 4e          	mov    0x4e(%r11),%ebx
     c13:	44 89 64 24 b0       	mov    %r12d,-0x50(%rsp)
     c18:	89 c1                	mov    %eax,%ecx
     c1a:	41 8b 43 30          	mov    0x30(%r11),%eax
     c1e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c25:	45 8b 63 57          	mov    0x57(%r11),%r12d
     c29:	44 89 54 24 ac       	mov    %r10d,-0x54(%rsp)
     c2e:	45 8b 53 51          	mov    0x51(%r11),%r10d
     c32:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     c38:	25 ff ff ff 00       	and    $0xffffff,%eax
     c3d:	44 89 6c 24 a4       	mov    %r13d,-0x5c(%rsp)
     c42:	45 8b 6b 54          	mov    0x54(%r11),%r13d
     c46:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     c4d:	89 c6                	mov    %eax,%esi
     c4f:	41 8b 43 5d          	mov    0x5d(%r11),%eax
     c53:	44 89 44 24 9c       	mov    %r8d,-0x64(%rsp)
     c58:	41 89 d0             	mov    %edx,%r8d
     c5b:	44 89 ca             	mov    %r9d,%edx
     c5e:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     c65:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     c6c:	25 ff ff ff 00       	and    $0xffffff,%eax
     c71:	89 c7                	mov    %eax,%edi
     c73:	41 8b 43 5a          	mov    0x5a(%r11),%eax
     c77:	25 ff ff ff 00       	and    $0xffffff,%eax
     c7c:	c1 ea 0a             	shr    $0xa,%edx
     c7f:	44 31 ca             	xor    %r9d,%edx
     c82:	45 0f b6 0c 16       	movzbl (%r14,%rdx,1),%r9d
     c87:	44 89 c2             	mov    %r8d,%edx
     c8a:	c1 ea 0a             	shr    $0xa,%edx
     c8d:	44 31 c2             	xor    %r8d,%edx
     c90:	45 0f b6 04 16       	movzbl (%r14,%rdx,1),%r8d
     c95:	89 da                	mov    %ebx,%edx
     c97:	c1 ea 0a             	shr    $0xa,%edx
     c9a:	31 da                	xor    %ebx,%edx
     c9c:	41 0f b6 1c 16       	movzbl (%r14,%rdx,1),%ebx
     ca1:	44 89 d2             	mov    %r10d,%edx
     ca4:	c1 ea 0a             	shr    $0xa,%edx
     ca7:	44 31 d2             	xor    %r10d,%edx
     caa:	45 0f b6 14 16       	movzbl (%r14,%rdx,1),%r10d
     caf:	44 89 ea             	mov    %r13d,%edx
     cb2:	c1 ea 0a             	shr    $0xa,%edx
     cb5:	44 31 ea             	xor    %r13d,%edx
     cb8:	45 0f b6 2c 16       	movzbl (%r14,%rdx,1),%r13d
     cbd:	44 89 e2             	mov    %r12d,%edx
     cc0:	c1 ea 0a             	shr    $0xa,%edx
     cc3:	44 31 e2             	xor    %r12d,%edx
     cc6:	45 0f b6 24 16       	movzbl (%r14,%rdx,1),%r12d
     ccb:	89 c2                	mov    %eax,%edx
     ccd:	c1 ea 0a             	shr    $0xa,%edx
     cd0:	31 c2                	xor    %eax,%edx
     cd2:	89 f8                	mov    %edi,%eax
     cd4:	41 0f b6 14 16       	movzbl (%r14,%rdx,1),%edx
     cd9:	c1 e8 0a             	shr    $0xa,%eax
     cdc:	31 f8                	xor    %edi,%eax
     cde:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
     ce3:	c4 c1 79 6e 0c 97    	vmovd  (%r15,%rdx,4),%xmm1
     ce9:	c4 c3 71 22 0c 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm1,%xmm1
     cf0:	89 f0                	mov    %esi,%eax
     cf2:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
     cf8:	c1 e8 0a             	shr    $0xa,%eax
     cfb:	c4 81 79 6e 2c 8f    	vmovd  (%r15,%r9,4),%xmm5
     d01:	44 8b 6c 24 a4       	mov    -0x5c(%rsp),%r13d
     d06:	31 f0                	xor    %esi,%eax
     d08:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
     d0f:	44 8b 4c 24 a8       	mov    -0x58(%rsp),%r9d
     d14:	41 0f b6 14 06       	movzbl (%r14,%rax,1),%edx
     d19:	89 c8                	mov    %ecx,%eax
     d1b:	c4 83 51 22 2c 87 01 	vpinsrd $0x1,(%r15,%r8,4),%xmm5,%xmm5
     d22:	c1 e8 0a             	shr    $0xa,%eax
     d25:	44 8b 44 24 9c       	mov    -0x64(%rsp),%r8d
     d2a:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     d2e:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
     d34:	31 c8                	xor    %ecx,%eax
     d36:	8b 5c 24 a0          	mov    -0x60(%rsp),%ebx
     d3a:	44 8b 64 24 b0       	mov    -0x50(%rsp),%r12d
     d3f:	41 0f b6 0c 06       	movzbl (%r14,%rax,1),%ecx
     d44:	44 89 c0             	mov    %r8d,%eax
     d47:	c4 83 71 22 0c 97 01 	vpinsrd $0x1,(%r15,%r10,4),%xmm1,%xmm1
     d4e:	c1 e8 0a             	shr    $0xa,%eax
     d51:	44 8b 54 24 ac       	mov    -0x54(%rsp),%r10d
     d56:	44 31 c0             	xor    %r8d,%eax
     d59:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     d5d:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
     d62:	89 d8                	mov    %ebx,%eax
     d64:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     d6a:	c4 c1 79 6e 04 97    	vmovd  (%r15,%rdx,4),%xmm0
     d70:	c1 e8 0a             	shr    $0xa,%eax
     d73:	8b 54 24 b4          	mov    -0x4c(%rsp),%edx
     d77:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     d7c:	31 d8                	xor    %ebx,%eax
     d7e:	c4 c3 79 22 04 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm0,%xmm0
     d85:	8b 4c 24 b8          	mov    -0x48(%rsp),%ecx
     d89:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     d8e:	41 0f b6 3c 06       	movzbl (%r14,%rax,1),%edi
     d93:	44 89 e8             	mov    %r13d,%eax
     d96:	c1 e8 0a             	shr    $0xa,%eax
     d99:	44 31 e8             	xor    %r13d,%eax
     d9c:	45 0f b6 04 06       	movzbl (%r14,%rax,1),%r8d
     da1:	44 89 c8             	mov    %r9d,%eax
     da4:	c1 e8 0a             	shr    $0xa,%eax
     da7:	44 31 c8             	xor    %r9d,%eax
     daa:	c4 81 79 6e 0c 87    	vmovd  (%r15,%r8,4),%xmm1
     db0:	45 0f b6 0c 06       	movzbl (%r14,%rax,1),%r9d
     db5:	44 89 d0             	mov    %r10d,%eax
     db8:	c1 e8 0a             	shr    $0xa,%eax
     dbb:	44 31 d0             	xor    %r10d,%eax
     dbe:	c4 83 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm1,%xmm1
     dc5:	45 0f b6 14 06       	movzbl (%r14,%rax,1),%r10d
     dca:	44 89 e0             	mov    %r12d,%eax
     dcd:	c1 e8 0a             	shr    $0xa,%eax
     dd0:	44 31 e0             	xor    %r12d,%eax
     dd3:	c4 81 79 6e 14 97    	vmovd  (%r15,%r10,4),%xmm2
     dd9:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
     dde:	c4 c3 69 22 14 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm2,%xmm2
     de5:	89 d0                	mov    %edx,%eax
     de7:	c1 e8 0a             	shr    $0xa,%eax
     dea:	31 d0                	xor    %edx,%eax
     dec:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     df0:	c4 c1 79 6e 14 b7    	vmovd  (%r15,%rsi,4),%xmm2
     df6:	41 0f b6 14 06       	movzbl (%r14,%rax,1),%edx
     dfb:	89 c8                	mov    %ecx,%eax
     dfd:	c1 e8 0a             	shr    $0xa,%eax
     e00:	c4 c3 69 22 14 bf 01 	vpinsrd $0x1,(%r15,%rdi,4),%xmm2,%xmm2
     e07:	31 c8                	xor    %ecx,%eax
     e09:	41 0f b6 0c 06       	movzbl (%r14,%rax,1),%ecx
     e0e:	8b 74 24 bc          	mov    -0x44(%rsp),%esi
     e12:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     e16:	8b 7c 24 c0          	mov    -0x40(%rsp),%edi
     e1a:	44 8b 44 24 c4       	mov    -0x3c(%rsp),%r8d
     e1f:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     e25:	89 f0                	mov    %esi,%eax
     e27:	8b 5c 24 c8          	mov    -0x38(%rsp),%ebx
     e2b:	44 8b 6c 24 cc       	mov    -0x34(%rsp),%r13d
     e30:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     e35:	c1 e8 0a             	shr    $0xa,%eax
     e38:	44 8b 64 24 d0       	mov    -0x30(%rsp),%r12d
     e3d:	c4 c1 79 6e 0c 97    	vmovd  (%r15,%rdx,4),%xmm1
     e43:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     e48:	31 f0                	xor    %esi,%eax
     e4a:	8b 54 24 d4          	mov    -0x2c(%rsp),%edx
     e4e:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     e52:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     e58:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
     e5d:	89 f8                	mov    %edi,%eax
     e5f:	c4 c3 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm1,%xmm1
     e66:	c1 e8 0a             	shr    $0xa,%eax
     e69:	8b 4c 24 d8          	mov    -0x28(%rsp),%ecx
     e6d:	31 f8                	xor    %edi,%eax
     e6f:	41 0f b6 3c 06       	movzbl (%r14,%rax,1),%edi
     e74:	44 89 c0             	mov    %r8d,%eax
     e77:	c1 e8 0a             	shr    $0xa,%eax
     e7a:	44 31 c0             	xor    %r8d,%eax
     e7d:	45 0f b6 04 06       	movzbl (%r14,%rax,1),%r8d
     e82:	89 d8                	mov    %ebx,%eax
     e84:	c1 e8 0a             	shr    $0xa,%eax
     e87:	31 d8                	xor    %ebx,%eax
     e89:	c4 81 79 6e 14 87    	vmovd  (%r15,%r8,4),%xmm2
     e8f:	44 8b 44 24 e4       	mov    -0x1c(%rsp),%r8d
     e94:	45 0f b6 0c 06       	movzbl (%r14,%rax,1),%r9d
     e99:	44 89 e8             	mov    %r13d,%eax
     e9c:	c1 e8 0a             	shr    $0xa,%eax
     e9f:	44 31 e8             	xor    %r13d,%eax
     ea2:	c4 83 69 22 14 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm2,%xmm2
     ea9:	44 8b 4c 24 e8       	mov    -0x18(%rsp),%r9d
     eae:	45 0f b6 14 06       	movzbl (%r14,%rax,1),%r10d
     eb3:	44 89 e0             	mov    %r12d,%eax
     eb6:	c1 e8 0a             	shr    $0xa,%eax
     eb9:	44 31 e0             	xor    %r12d,%eax
     ebc:	c4 81 79 6e 34 97    	vmovd  (%r15,%r10,4),%xmm6
     ec2:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
     ec7:	c4 c3 49 22 34 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm6,%xmm6
     ece:	89 d0                	mov    %edx,%eax
     ed0:	c1 e8 0a             	shr    $0xa,%eax
     ed3:	31 d0                	xor    %edx,%eax
     ed5:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
     ed9:	c4 c1 79 6e 34 b7    	vmovd  (%r15,%rsi,4),%xmm6
     edf:	8b 74 24 dc          	mov    -0x24(%rsp),%esi
     ee3:	41 0f b6 14 06       	movzbl (%r14,%rax,1),%edx
     ee8:	89 c8                	mov    %ecx,%eax
     eea:	c1 e8 0a             	shr    $0xa,%eax
     eed:	c4 c3 49 22 34 bf 01 	vpinsrd $0x1,(%r15,%rdi,4),%xmm6,%xmm6
     ef4:	8b 7c 24 e0          	mov    -0x20(%rsp),%edi
     ef8:	31 c8                	xor    %ecx,%eax
     efa:	41 0f b6 0c 06       	movzbl (%r14,%rax,1),%ecx
     eff:	89 f0                	mov    %esi,%eax
     f01:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     f05:	c1 e8 0a             	shr    $0xa,%eax
     f08:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     f0e:	31 f0                	xor    %esi,%eax
     f10:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     f15:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
     f1a:	89 f8                	mov    %edi,%eax
     f1c:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     f21:	c1 e8 0a             	shr    $0xa,%eax
     f24:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     f28:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     f2e:	31 f8                	xor    %edi,%eax
     f30:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     f36:	41 0f b6 3c 06       	movzbl (%r14,%rax,1),%edi
     f3b:	44 89 c0             	mov    %r8d,%eax
     f3e:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
     f44:	c1 e8 0a             	shr    $0xa,%eax
     f47:	44 31 c0             	xor    %r8d,%eax
     f4a:	45 0f b6 04 06       	movzbl (%r14,%rax,1),%r8d
     f4f:	44 89 c8             	mov    %r9d,%eax
     f52:	c1 e8 0a             	shr    $0xa,%eax
     f55:	44 31 c8             	xor    %r9d,%eax
     f58:	45 0f b6 0c 06       	movzbl (%r14,%rax,1),%r9d
     f5d:	44 8b 54 24 ec       	mov    -0x14(%rsp),%r10d
     f62:	8b 5c 24 f0          	mov    -0x10(%rsp),%ebx
     f66:	c4 81 79 6e 34 87    	vmovd  (%r15,%r8,4),%xmm6
     f6c:	44 89 d0             	mov    %r10d,%eax
     f6f:	c4 c1 79 6e 14 97    	vmovd  (%r15,%rdx,4),%xmm2
     f75:	c1 e8 0a             	shr    $0xa,%eax
     f78:	c4 83 49 22 34 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm6,%xmm6
     f7f:	44 31 d0             	xor    %r10d,%eax
     f82:	c4 c3 69 22 14 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm2,%xmm2
     f89:	45 0f b6 14 06       	movzbl (%r14,%rax,1),%r10d
     f8e:	89 d8                	mov    %ebx,%eax
     f90:	c1 e8 0a             	shr    $0xa,%eax
     f93:	31 d8                	xor    %ebx,%eax
     f95:	c4 81 79 6e 3c 97    	vmovd  (%r15,%r10,4),%xmm7
     f9b:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
     fa0:	c4 c3 41 22 3c 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm7,%xmm7
     fa7:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
     fab:	c4 c1 79 6e 3c b7    	vmovd  (%r15,%rsi,4),%xmm7
     fb1:	c4 c3 41 22 3c bf 01 	vpinsrd $0x1,(%r15,%rdi,4),%xmm7,%xmm7
     fb8:	48 8b 7c 24 f8       	mov    -0x8(%rsp),%rdi
     fbd:	c4 c1 7e 7f 4b 20    	vmovdqu %ymm1,0x20(%r11)
     fc3:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
     fc7:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
     fcb:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     fd1:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     fd7:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
     fdd:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
     fe1:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     fe6:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
     fec:	48 8d 47 48          	lea    0x48(%rdi),%rax
     ff0:	48 83 c7 20          	add    $0x20,%rdi
     ff4:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     ff9:	c4 c1 7e 7f 43 40    	vmovdqu %ymm0,0x40(%r11)
     fff:	49 83 c3 60          	add    $0x60,%r11
    1003:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1007:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    100d:	48 89 7c 24 f8       	mov    %rdi,-0x8(%rsp)
    1012:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1017:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    101d:	c4 c1 7e 7f 53 a0    	vmovdqu %ymm2,-0x60(%r11)
    1023:	48 39 04 24          	cmp    %rax,(%rsp)
    1027:	0f 83 9b fa ff ff    	jae    ac8 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xac8>
    102d:	48 8b 7c 24 90       	mov    -0x70(%rsp),%rdi
    1032:	48 8b 44 24 f8       	mov    -0x8(%rsp),%rax
    1037:	48 8d 58 08          	lea    0x8(%rax),%rbx
    103b:	48 39 1c 24          	cmp    %rbx,(%rsp)
    103f:	0f 82 8c 01 00 00    	jb     11d1 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x11d1>
    1045:	48 89 7c 24 f0       	mov    %rdi,-0x10(%rsp)
    104a:	48 8d 0c 40          	lea    (%rax,%rax,2),%rcx
    104e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1056 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1056>
    1055:	00 
    1056:	48 01 f9             	add    %rdi,%rcx
    1059:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1060:	48 8b 51 10          	mov    0x10(%rcx),%rdx
    1064:	48 8b 41 08          	mov    0x8(%rcx),%rax
    1068:	4c 8b 01             	mov    (%rcx),%r8
    106b:	48 89 d7             	mov    %rdx,%rdi
    106e:	48 89 d6             	mov    %rdx,%rsi
    1071:	49 89 c2             	mov    %rax,%r10
    1074:	41 89 c4             	mov    %eax,%r12d
    1077:	48 c1 ef 28          	shr    $0x28,%rdi
    107b:	48 c1 ee 10          	shr    $0x10,%rsi
    107f:	4d 89 c3             	mov    %r8,%r11
    1082:	48 89 7c 24 f8       	mov    %rdi,-0x8(%rsp)
    1087:	49 89 f1             	mov    %rsi,%r9
    108a:	48 89 c7             	mov    %rax,%rdi
    108d:	89 d6                	mov    %edx,%esi
    108f:	48 c1 ef 38          	shr    $0x38,%rdi
    1093:	c1 e6 08             	shl    $0x8,%esi
    1096:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    109d:	49 c1 eb 30          	shr    $0x30,%r11
    10a1:	09 fe                	or     %edi,%esi
    10a3:	89 c7                	mov    %eax,%edi
    10a5:	49 c1 ea 20          	shr    $0x20,%r10
    10a9:	c1 e7 10             	shl    $0x10,%edi
    10ac:	41 c1 ec 08          	shr    $0x8,%r12d
    10b0:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    10b7:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    10bd:	c1 e8 12             	shr    $0x12,%eax
    10c0:	44 09 df             	or     %r11d,%edi
    10c3:	4d 89 c3             	mov    %r8,%r11
    10c6:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    10cd:	49 c1 eb 18          	shr    $0x18,%r11
    10d1:	45 89 c5             	mov    %r8d,%r13d
    10d4:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    10da:	44 31 e0             	xor    %r12d,%eax
    10dd:	41 c1 ed 0a          	shr    $0xa,%r13d
    10e1:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    10e8:	48 c1 ea 32          	shr    $0x32,%rdx
    10ec:	45 31 c5             	xor    %r8d,%r13d
    10ef:	45 89 d8             	mov    %r11d,%r8d
    10f2:	41 c1 e8 0a          	shr    $0xa,%r8d
    10f6:	47 0f b6 2c 2e       	movzbl (%r14,%r13,1),%r13d
    10fb:	45 31 d8             	xor    %r11d,%r8d
    10fe:	47 0f b6 1c 06       	movzbl (%r14,%r8,1),%r11d
    1103:	41 89 f8             	mov    %edi,%r8d
    1106:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    110c:	41 c1 e8 0a          	shr    $0xa,%r8d
    1110:	41 31 f8             	xor    %edi,%r8d
    1113:	c4 83 79 22 04 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm0,%xmm0
    111a:	43 0f b6 3c 06       	movzbl (%r14,%r8,1),%edi
    111f:	45 0f b6 04 06       	movzbl (%r14,%rax,1),%r8d
    1124:	44 89 d0             	mov    %r10d,%eax
    1127:	c1 e8 0a             	shr    $0xa,%eax
    112a:	44 31 d0             	xor    %r10d,%eax
    112d:	45 0f b6 14 06       	movzbl (%r14,%rax,1),%r10d
    1132:	89 f0                	mov    %esi,%eax
    1134:	c1 e8 0a             	shr    $0xa,%eax
    1137:	31 f0                	xor    %esi,%eax
    1139:	c4 81 79 6e 0c 97    	vmovd  (%r15,%r10,4),%xmm1
    113f:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
    1144:	44 89 c8             	mov    %r9d,%eax
    1147:	c1 e8 0a             	shr    $0xa,%eax
    114a:	44 31 c8             	xor    %r9d,%eax
    114d:	48 33 54 24 f8       	xor    -0x8(%rsp),%rdx
    1152:	c4 c3 71 22 0c b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm1,%xmm1
    1159:	48 83 c1 18          	add    $0x18,%rcx
    115d:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    1162:	41 0f b6 14 16       	movzbl (%r14,%rdx,1),%edx
    1167:	c4 c1 79 6e 14 87    	vmovd  (%r15,%rax,4),%xmm2
    116d:	48 89 d8             	mov    %rbx,%rax
    1170:	48 83 c3 08          	add    $0x8,%rbx
    1174:	c4 c3 69 22 14 97 01 	vpinsrd $0x1,(%r15,%rdx,4),%xmm2,%xmm2
    117b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    117f:	c4 c1 79 6e 14 bf    	vmovd  (%r15,%rdi,4),%xmm2
    1185:	c4 83 69 22 14 87 01 	vpinsrd $0x1,(%r15,%r8,4),%xmm2,%xmm2
    118c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1190:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1196:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    119b:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    119f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    11a5:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    11aa:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    11af:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    11b3:	c5 f9 d6 41 f8       	vmovq  %xmm0,-0x8(%rcx)
    11b8:	c5 fa 7f 49 e8       	vmovdqu %xmm1,-0x18(%rcx)
    11bd:	48 39 1c 24          	cmp    %rbx,(%rsp)
    11c1:	0f 83 99 fe ff ff    	jae    1060 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1060>
    11c7:	48 89 44 24 f8       	mov    %rax,-0x8(%rsp)
    11cc:	48 8b 7c 24 f0       	mov    -0x10(%rsp),%rdi
    11d1:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    11d6:	4c 8b 04 24          	mov    (%rsp),%r8
    11da:	4c 39 c3             	cmp    %r8,%rbx
    11dd:	0f 83 dd 01 00 00    	jae    13c0 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    11e3:	48 8d 14 5b          	lea    (%rbx,%rbx,2),%rdx
    11e7:	48 8d 0c 17          	lea    (%rdi,%rdx,1),%rcx
    11eb:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
    11ef:	0f b6 71 02          	movzbl 0x2(%rcx),%esi
    11f3:	c1 e0 08             	shl    $0x8,%eax
    11f6:	c1 e6 10             	shl    $0x10,%esi
    11f9:	09 f0                	or     %esi,%eax
    11fb:	0f b6 31             	movzbl (%rcx),%esi
    11fe:	09 c6                	or     %eax,%esi
    1200:	c1 e8 0a             	shr    $0xa,%eax
    1203:	31 f0                	xor    %esi,%eax
    1205:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    120a:	49 8d 34 87          	lea    (%r15,%rax,4),%rsi
    120e:	8b 06                	mov    (%rsi),%eax
    1210:	0f b7 36             	movzwl (%rsi),%esi
    1213:	c1 e8 10             	shr    $0x10,%eax
    1216:	66 89 31             	mov    %si,(%rcx)
    1219:	88 41 02             	mov    %al,0x2(%rcx)
    121c:	48 8d 43 01          	lea    0x1(%rbx),%rax
    1220:	4c 39 c0             	cmp    %r8,%rax
    1223:	0f 83 97 01 00 00    	jae    13c0 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    1229:	48 8d 4c 17 03       	lea    0x3(%rdi,%rdx,1),%rcx
    122e:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
    1232:	0f b6 71 02          	movzbl 0x2(%rcx),%esi
    1236:	c1 e0 08             	shl    $0x8,%eax
    1239:	c1 e6 10             	shl    $0x10,%esi
    123c:	09 f0                	or     %esi,%eax
    123e:	0f b6 31             	movzbl (%rcx),%esi
    1241:	09 c6                	or     %eax,%esi
    1243:	c1 e8 0a             	shr    $0xa,%eax
    1246:	31 f0                	xor    %esi,%eax
    1248:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    124d:	49 8d 34 87          	lea    (%r15,%rax,4),%rsi
    1251:	8b 06                	mov    (%rsi),%eax
    1253:	0f b7 36             	movzwl (%rsi),%esi
    1256:	c1 e8 10             	shr    $0x10,%eax
    1259:	66 89 31             	mov    %si,(%rcx)
    125c:	88 41 02             	mov    %al,0x2(%rcx)
    125f:	48 8d 43 02          	lea    0x2(%rbx),%rax
    1263:	4c 39 c0             	cmp    %r8,%rax
    1266:	0f 83 54 01 00 00    	jae    13c0 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    126c:	48 8d 4c 17 06       	lea    0x6(%rdi,%rdx,1),%rcx
    1271:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
    1275:	0f b6 71 02          	movzbl 0x2(%rcx),%esi
    1279:	c1 e0 08             	shl    $0x8,%eax
    127c:	c1 e6 10             	shl    $0x10,%esi
    127f:	09 f0                	or     %esi,%eax
    1281:	0f b6 31             	movzbl (%rcx),%esi
    1284:	09 c6                	or     %eax,%esi
    1286:	c1 e8 0a             	shr    $0xa,%eax
    1289:	31 f0                	xor    %esi,%eax
    128b:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    1290:	49 8d 34 87          	lea    (%r15,%rax,4),%rsi
    1294:	8b 06                	mov    (%rsi),%eax
    1296:	0f b7 36             	movzwl (%rsi),%esi
    1299:	c1 e8 10             	shr    $0x10,%eax
    129c:	66 89 31             	mov    %si,(%rcx)
    129f:	88 41 02             	mov    %al,0x2(%rcx)
    12a2:	48 8d 43 03          	lea    0x3(%rbx),%rax
    12a6:	4c 39 c0             	cmp    %r8,%rax
    12a9:	0f 83 11 01 00 00    	jae    13c0 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    12af:	48 8d 4c 17 09       	lea    0x9(%rdi,%rdx,1),%rcx
    12b4:	0f b6 41 02          	movzbl 0x2(%rcx),%eax
    12b8:	0f b6 71 01          	movzbl 0x1(%rcx),%esi
    12bc:	c1 e0 10             	shl    $0x10,%eax
    12bf:	c1 e6 08             	shl    $0x8,%esi
    12c2:	09 f0                	or     %esi,%eax
    12c4:	0f b6 31             	movzbl (%rcx),%esi
    12c7:	09 c6                	or     %eax,%esi
    12c9:	c1 e8 0a             	shr    $0xa,%eax
    12cc:	31 f0                	xor    %esi,%eax
    12ce:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    12d3:	49 8d 34 87          	lea    (%r15,%rax,4),%rsi
    12d7:	8b 06                	mov    (%rsi),%eax
    12d9:	0f b7 36             	movzwl (%rsi),%esi
    12dc:	c1 e8 10             	shr    $0x10,%eax
    12df:	66 89 31             	mov    %si,(%rcx)
    12e2:	88 41 02             	mov    %al,0x2(%rcx)
    12e5:	48 8d 43 04          	lea    0x4(%rbx),%rax
    12e9:	4c 39 c0             	cmp    %r8,%rax
    12ec:	0f 83 ce 00 00 00    	jae    13c0 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    12f2:	48 8d 4c 17 0c       	lea    0xc(%rdi,%rdx,1),%rcx
    12f7:	0f b6 41 02          	movzbl 0x2(%rcx),%eax
    12fb:	0f b6 71 01          	movzbl 0x1(%rcx),%esi
    12ff:	c1 e0 10             	shl    $0x10,%eax
    1302:	c1 e6 08             	shl    $0x8,%esi
    1305:	09 f0                	or     %esi,%eax
    1307:	0f b6 31             	movzbl (%rcx),%esi
    130a:	09 c6                	or     %eax,%esi
    130c:	c1 e8 0a             	shr    $0xa,%eax
    130f:	31 f0                	xor    %esi,%eax
    1311:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    1316:	49 8d 34 87          	lea    (%r15,%rax,4),%rsi
    131a:	8b 06                	mov    (%rsi),%eax
    131c:	0f b7 36             	movzwl (%rsi),%esi
    131f:	c1 e8 10             	shr    $0x10,%eax
    1322:	66 89 31             	mov    %si,(%rcx)
    1325:	88 41 02             	mov    %al,0x2(%rcx)
    1328:	48 8d 43 05          	lea    0x5(%rbx),%rax
    132c:	4c 39 c0             	cmp    %r8,%rax
    132f:	0f 83 8b 00 00 00    	jae    13c0 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    1335:	48 8d 4c 17 0f       	lea    0xf(%rdi,%rdx,1),%rcx
    133a:	0f b6 41 02          	movzbl 0x2(%rcx),%eax
    133e:	0f b6 71 01          	movzbl 0x1(%rcx),%esi
    1342:	c1 e0 10             	shl    $0x10,%eax
    1345:	c1 e6 08             	shl    $0x8,%esi
    1348:	09 f0                	or     %esi,%eax
    134a:	0f b6 31             	movzbl (%rcx),%esi
    134d:	09 c6                	or     %eax,%esi
    134f:	c1 e8 0a             	shr    $0xa,%eax
    1352:	31 f0                	xor    %esi,%eax
    1354:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    1359:	49 8d 34 87          	lea    (%r15,%rax,4),%rsi
    135d:	8b 06                	mov    (%rsi),%eax
    135f:	0f b7 36             	movzwl (%rsi),%esi
    1362:	c1 e8 10             	shr    $0x10,%eax
    1365:	66 89 31             	mov    %si,(%rcx)
    1368:	88 41 02             	mov    %al,0x2(%rcx)
    136b:	48 8d 43 06          	lea    0x6(%rbx),%rax
    136f:	4c 39 c0             	cmp    %r8,%rax
    1372:	73 4c                	jae    13c0 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13c0>
    1374:	48 8d 54 17 12       	lea    0x12(%rdi,%rdx,1),%rdx
    1379:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    137d:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1381:	c1 e0 08             	shl    $0x8,%eax
    1384:	c1 e1 10             	shl    $0x10,%ecx
    1387:	09 c8                	or     %ecx,%eax
    1389:	0f b6 0a             	movzbl (%rdx),%ecx
    138c:	09 c1                	or     %eax,%ecx
    138e:	c1 e8 0a             	shr    $0xa,%eax
    1391:	31 c8                	xor    %ecx,%eax
    1393:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    1398:	49 8d 0c 87          	lea    (%r15,%rax,4),%rcx
    139c:	8b 01                	mov    (%rcx),%eax
    139e:	0f b7 09             	movzwl (%rcx),%ecx
    13a1:	c1 e8 10             	shr    $0x10,%eax
    13a4:	66 89 0a             	mov    %cx,(%rdx)
    13a7:	88 42 02             	mov    %al,0x2(%rdx)
    13aa:	c5 f8 77             	vzeroupper
    13ad:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    13b1:	5b                   	pop    %rbx
    13b2:	41 5c                	pop    %r12
    13b4:	41 5d                	pop    %r13
    13b6:	41 5e                	pop    %r14
    13b8:	41 5f                	pop    %r15
    13ba:	5d                   	pop    %rbp
    13bb:	c3                   	ret
    13bc:	0f 1f 40 00          	nopl   0x0(%rax)
    13c0:	c5 f8 77             	vzeroupper
    13c3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    13c7:	5b                   	pop    %rbx
    13c8:	41 5c                	pop    %r12
    13ca:	41 5d                	pop    %r13
    13cc:	41 5e                	pop    %r14
    13ce:	41 5f                	pop    %r15
    13d0:	5d                   	pop    %rbp
    13d1:	c3                   	ret
    13d2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    13d8:	48 8b 04 24          	mov    (%rsp),%rax
    13dc:	48 89 44 24 f8       	mov    %rax,-0x8(%rsp)
    13e1:	e9 4c fc ff ff       	jmp    1032 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1032>
    13e6:	48 89 54 24 f8       	mov    %rdx,-0x8(%rsp)
    13eb:	48 8d 42 28          	lea    0x28(%rdx),%rax
    13ef:	e9 a1 f6 ff ff       	jmp    a95 <jshc_channel::avx2_chain_skew(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa95>
    13f4:	90                   	nop
    13f5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
    13fc:	00 00 00 00 

0000000000001400 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1400:	f3 0f 1e fa          	endbr64
    1404:	55                   	push   %rbp
    1405:	48 89 e5             	mov    %rsp,%rbp
    1408:	41 57                	push   %r15
    140a:	41 56                	push   %r14
    140c:	41 55                	push   %r13
    140e:	41 54                	push   %r12
    1410:	53                   	push   %rbx
    1411:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    1415:	48 83 ec 28          	sub    $0x28,%rsp
    1419:	4c 89 44 24 20       	mov    %r8,0x20(%rsp)
    141e:	4d 85 c0             	test   %r8,%r8
    1421:	0f 84 e4 14 00 00    	je     290b <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x150b>
    1427:	b8 00 04 00 00       	mov    $0x400,%eax
    142c:	49 89 f7             	mov    %rsi,%r15
    142f:	48 89 d6             	mov    %rdx,%rsi
    1432:	49 89 fe             	mov    %rdi,%r14
    1435:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    1439:	48 89 cf             	mov    %rcx,%rdi
    143c:	48 39 c2             	cmp    %rax,%rdx
    143f:	48 0f 47 d0          	cmova  %rax,%rdx
    1443:	31 c0                	xor    %eax,%eax
    1445:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
    144c:	00 00 00 00 
    1450:	0f 18 04 06          	prefetchnta (%rsi,%rax,1)
    1454:	48 83 c0 40          	add    $0x40,%rax
    1458:	48 39 d0             	cmp    %rdx,%rax
    145b:	72 f3                	jb     1450 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x50>
    145d:	4c 8b 4c 24 20       	mov    0x20(%rsp),%r9
    1462:	49 89 f0             	mov    %rsi,%r8
    1465:	48 89 fa             	mov    %rdi,%rdx
    1468:	31 c9                	xor    %ecx,%ecx
    146a:	eb 55                	jmp    14c1 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc1>
    146c:	0f 1f 40 00          	nopl   0x0(%rax)
    1470:	41 0f b6 40 01       	movzbl 0x1(%r8),%eax
    1475:	45 0f b6 50 02       	movzbl 0x2(%r8),%r10d
    147a:	48 ff c1             	inc    %rcx
    147d:	48 83 c2 03          	add    $0x3,%rdx
    1481:	49 83 c0 03          	add    $0x3,%r8
    1485:	41 c1 e2 10          	shl    $0x10,%r10d
    1489:	c1 e0 08             	shl    $0x8,%eax
    148c:	44 09 d0             	or     %r10d,%eax
    148f:	45 0f b6 50 fd       	movzbl -0x3(%r8),%r10d
    1494:	41 09 c2             	or     %eax,%r10d
    1497:	c1 e8 0a             	shr    $0xa,%eax
    149a:	44 31 d0             	xor    %r10d,%eax
    149d:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    14a2:	4d 8d 14 87          	lea    (%r15,%rax,4),%r10
    14a6:	41 8b 02             	mov    (%r10),%eax
    14a9:	45 0f b7 12          	movzwl (%r10),%r10d
    14ad:	c1 e8 10             	shr    $0x10,%eax
    14b0:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
    14b5:	88 42 ff             	mov    %al,-0x1(%rdx)
    14b8:	49 39 c9             	cmp    %rcx,%r9
    14bb:	0f 84 5f 14 00 00    	je     2920 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1520>
    14c1:	f6 c2 3f             	test   $0x3f,%dl
    14c4:	75 aa                	jne    1470 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x70>
    14c6:	48 8d 41 48          	lea    0x48(%rcx),%rax
    14ca:	48 39 44 24 20       	cmp    %rax,0x20(%rsp)
    14cf:	0f 82 5a 14 00 00    	jb     292f <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x152f>
    14d5:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    14d9:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 14e1 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe1>
    14e0:	00 
    14e1:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 14e9 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe9>
    14e8:	00 
    14e9:	48 89 74 24 10       	mov    %rsi,0x10(%rsp)
    14ee:	48 8d 14 07          	lea    (%rdi,%rax,1),%rdx
    14f2:	48 89 7c 24 08       	mov    %rdi,0x8(%rsp)
    14f7:	48 8d 84 06 00 04 00 	lea    0x400(%rsi,%rax,1),%rax
    14fe:	00 
    14ff:	eb 0a                	jmp    150b <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10b>
    1501:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1508:	48 89 f9             	mov    %rdi,%rcx
    150b:	48 8d b1 96 01 00 00 	lea    0x196(%rcx),%rsi
    1512:	48 39 74 24 20       	cmp    %rsi,0x20(%rsp)
    1517:	72 15                	jb     152e <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12e>
    1519:	0f 18 00             	prefetchnta (%rax)
    151c:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1520:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    1527:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    152e:	44 8b 90 00 fc ff ff 	mov    -0x400(%rax),%r10d
    1535:	44 8b 88 03 fc ff ff 	mov    -0x3fd(%rax),%r9d
    153c:	8b 98 06 fc ff ff    	mov    -0x3fa(%rax),%ebx
    1542:	44 8b 98 09 fc ff ff 	mov    -0x3f7(%rax),%r11d
    1549:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1550:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1557:	44 8b a8 0c fc ff ff 	mov    -0x3f4(%rax),%r13d
    155e:	44 8b a0 0f fc ff ff 	mov    -0x3f1(%rax),%r12d
    1565:	44 89 d7             	mov    %r10d,%edi
    1568:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    156e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1575:	8b b0 12 fc ff ff    	mov    -0x3ee(%rax),%esi
    157b:	c1 ef 0a             	shr    $0xa,%edi
    157e:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1585:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    158c:	44 8b 80 15 fc ff ff 	mov    -0x3eb(%rax),%r8d
    1593:	44 31 d7             	xor    %r10d,%edi
    1596:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    159c:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    15a1:	44 89 cf             	mov    %r9d,%edi
    15a4:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    15ab:	c1 ef 0a             	shr    $0xa,%edi
    15ae:	44 31 cf             	xor    %r9d,%edi
    15b1:	c4 01 79 6e 0c 97    	vmovd  (%r15,%r10,4),%xmm9
    15b7:	44 8b 90 18 fc ff ff 	mov    -0x3e8(%rax),%r10d
    15be:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    15c3:	89 df                	mov    %ebx,%edi
    15c5:	c1 ef 0a             	shr    $0xa,%edi
    15c8:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    15cf:	31 df                	xor    %ebx,%edi
    15d1:	c4 03 31 22 0c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm9,%xmm9
    15d8:	44 8b 88 1b fc ff ff 	mov    -0x3e5(%rax),%r9d
    15df:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    15e4:	44 89 df             	mov    %r11d,%edi
    15e7:	c1 ef 0a             	shr    $0xa,%edi
    15ea:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15f1:	44 31 df             	xor    %r11d,%edi
    15f4:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    15f9:	44 89 ef             	mov    %r13d,%edi
    15fc:	c1 ef 0a             	shr    $0xa,%edi
    15ff:	44 31 ef             	xor    %r13d,%edi
    1602:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    1607:	44 89 e7             	mov    %r12d,%edi
    160a:	c1 ef 0a             	shr    $0xa,%edi
    160d:	44 31 e7             	xor    %r12d,%edi
    1610:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    1616:	44 8b a8 24 fc ff ff 	mov    -0x3dc(%rax),%r13d
    161d:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    1622:	89 f7                	mov    %esi,%edi
    1624:	c1 ef 0a             	shr    $0xa,%edi
    1627:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    162e:	31 f7                	xor    %esi,%edi
    1630:	44 89 c6             	mov    %r8d,%esi
    1633:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
    163a:	44 8b a0 27 fc ff ff 	mov    -0x3d9(%rax),%r12d
    1641:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    1646:	c1 ee 0a             	shr    $0xa,%esi
    1649:	44 31 c6             	xor    %r8d,%esi
    164c:	44 8b 80 2d fc ff ff 	mov    -0x3d3(%rax),%r8d
    1653:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    165a:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    165f:	c4 c1 79 6e 0c bf    	vmovd  (%r15,%rdi,4),%xmm1
    1665:	44 89 d7             	mov    %r10d,%edi
    1668:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    166f:	c4 c3 71 22 0c b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm1,%xmm1
    1676:	8b b0 2a fc ff ff    	mov    -0x3d6(%rax),%esi
    167c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1680:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
    1686:	8b 98 1e fc ff ff    	mov    -0x3e2(%rax),%ebx
    168c:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1692:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
    1699:	44 8b 98 21 fc ff ff 	mov    -0x3df(%rax),%r11d
    16a0:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    16a6:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    16ad:	c1 ef 0a             	shr    $0xa,%edi
    16b0:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    16b4:	44 31 d7             	xor    %r10d,%edi
    16b7:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    16bd:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    16c2:	44 89 cf             	mov    %r9d,%edi
    16c5:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    16ca:	c1 ef 0a             	shr    $0xa,%edi
    16cd:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
    16d2:	44 31 cf             	xor    %r9d,%edi
    16d5:	c4 81 79 6e 34 97    	vmovd  (%r15,%r10,4),%xmm6
    16db:	44 8b 90 30 fc ff ff 	mov    -0x3d0(%rax),%r10d
    16e2:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    16e7:	89 df                	mov    %ebx,%edi
    16e9:	c1 ef 0a             	shr    $0xa,%edi
    16ec:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    16f3:	31 df                	xor    %ebx,%edi
    16f5:	c4 83 49 22 34 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm6,%xmm6
    16fc:	44 8b 88 33 fc ff ff 	mov    -0x3cd(%rax),%r9d
    1703:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    1708:	44 89 df             	mov    %r11d,%edi
    170b:	c1 ef 0a             	shr    $0xa,%edi
    170e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1715:	44 31 df             	xor    %r11d,%edi
    1718:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    171d:	44 89 ef             	mov    %r13d,%edi
    1720:	c1 ef 0a             	shr    $0xa,%edi
    1723:	44 31 ef             	xor    %r13d,%edi
    1726:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    172b:	44 89 e7             	mov    %r12d,%edi
    172e:	c1 ef 0a             	shr    $0xa,%edi
    1731:	44 31 e7             	xor    %r12d,%edi
    1734:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    173a:	44 8b a8 3c fc ff ff 	mov    -0x3c4(%rax),%r13d
    1741:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    1746:	89 f7                	mov    %esi,%edi
    1748:	c1 ef 0a             	shr    $0xa,%edi
    174b:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1752:	31 f7                	xor    %esi,%edi
    1754:	44 89 c6             	mov    %r8d,%esi
    1757:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
    175e:	44 8b a0 3f fc ff ff 	mov    -0x3c1(%rax),%r12d
    1765:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    176a:	c1 ee 0a             	shr    $0xa,%esi
    176d:	44 31 c6             	xor    %r8d,%esi
    1770:	44 8b 80 45 fc ff ff 	mov    -0x3bb(%rax),%r8d
    1777:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    177e:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    1783:	c4 c1 79 6e 0c bf    	vmovd  (%r15,%rdi,4),%xmm1
    1789:	44 89 d7             	mov    %r10d,%edi
    178c:	c1 ef 0a             	shr    $0xa,%edi
    178f:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    1796:	c4 c3 71 22 0c b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm1,%xmm1
    179d:	44 31 d7             	xor    %r10d,%edi
    17a0:	8b b0 42 fc ff ff    	mov    -0x3be(%rax),%esi
    17a6:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    17ab:	44 89 cf             	mov    %r9d,%edi
    17ae:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    17b2:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
    17b8:	8b 98 36 fc ff ff    	mov    -0x3ca(%rax),%ebx
    17be:	c1 ef 0a             	shr    $0xa,%edi
    17c1:	44 31 cf             	xor    %r9d,%edi
    17c4:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    17ca:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    17d0:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    17d5:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
    17dc:	89 df                	mov    %ebx,%edi
    17de:	44 8b 98 39 fc ff ff 	mov    -0x3c7(%rax),%r11d
    17e5:	c1 ef 0a             	shr    $0xa,%edi
    17e8:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    17ec:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    17f3:	31 df                	xor    %ebx,%edi
    17f5:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    17fb:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    1800:	44 89 df             	mov    %r11d,%edi
    1803:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1808:	c1 ef 0a             	shr    $0xa,%edi
    180b:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    1810:	44 31 df             	xor    %r11d,%edi
    1813:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    1817:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    181d:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    1822:	44 89 ef             	mov    %r13d,%edi
    1825:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    182b:	c1 ef 0a             	shr    $0xa,%edi
    182e:	44 31 ef             	xor    %r13d,%edi
    1831:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    1836:	44 89 e7             	mov    %r12d,%edi
    1839:	c1 ef 0a             	shr    $0xa,%edi
    183c:	44 31 e7             	xor    %r12d,%edi
    183f:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    1844:	89 f7                	mov    %esi,%edi
    1846:	c1 ef 0a             	shr    $0xa,%edi
    1849:	31 f7                	xor    %esi,%edi
    184b:	44 89 c6             	mov    %r8d,%esi
    184e:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    1853:	c1 ee 0a             	shr    $0xa,%esi
    1856:	44 31 c6             	xor    %r8d,%esi
    1859:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    185e:	c4 c1 79 6e 0c bf    	vmovd  (%r15,%rdi,4),%xmm1
    1864:	c4 81 79 6e 2c 97    	vmovd  (%r15,%r10,4),%xmm5
    186a:	44 8b 90 48 fc ff ff 	mov    -0x3b8(%rax),%r10d
    1871:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    1877:	c4 c3 71 22 0c b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm1,%xmm1
    187e:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1885:	c4 83 51 22 2c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm5,%xmm5
    188c:	44 8b 88 4b fc ff ff 	mov    -0x3b5(%rax),%r9d
    1893:	44 89 d7             	mov    %r10d,%edi
    1896:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
    189d:	44 8b a8 54 fc ff ff 	mov    -0x3ac(%rax),%r13d
    18a4:	c1 ef 0a             	shr    $0xa,%edi
    18a7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18ae:	44 8b a0 57 fc ff ff 	mov    -0x3a9(%rax),%r12d
    18b5:	8b b0 5a fc ff ff    	mov    -0x3a6(%rax),%esi
    18bb:	44 31 d7             	xor    %r10d,%edi
    18be:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    18c2:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
    18c8:	8b 98 4e fc ff ff    	mov    -0x3b2(%rax),%ebx
    18ce:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    18d3:	44 89 cf             	mov    %r9d,%edi
    18d6:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    18dd:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    18e4:	c1 ef 0a             	shr    $0xa,%edi
    18e7:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    18ed:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
    18f4:	44 8b 98 51 fc ff ff 	mov    -0x3af(%rax),%r11d
    18fb:	44 31 cf             	xor    %r9d,%edi
    18fe:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1904:	44 8b 80 5d fc ff ff 	mov    -0x3a3(%rax),%r8d
    190b:	c4 01 79 6e 04 97    	vmovd  (%r15,%r10,4),%xmm8
    1911:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    1916:	89 df                	mov    %ebx,%edi
    1918:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    191f:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    1923:	c1 ef 0a             	shr    $0xa,%edi
    1926:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    192d:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    1933:	31 df                	xor    %ebx,%edi
    1935:	c4 03 39 22 04 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm8,%xmm8
    193c:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1941:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    1946:	44 89 df             	mov    %r11d,%edi
    1949:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    194e:	c1 ef 0a             	shr    $0xa,%edi
    1951:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    1955:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    195b:	44 31 df             	xor    %r11d,%edi
    195e:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    1964:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    1969:	44 89 ef             	mov    %r13d,%edi
    196c:	c1 ef 0a             	shr    $0xa,%edi
    196f:	44 31 ef             	xor    %r13d,%edi
    1972:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    1977:	44 89 e7             	mov    %r12d,%edi
    197a:	c1 ef 0a             	shr    $0xa,%edi
    197d:	44 31 e7             	xor    %r12d,%edi
    1980:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    1986:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    198b:	89 f7                	mov    %esi,%edi
    198d:	c1 ef 0a             	shr    $0xa,%edi
    1990:	31 f7                	xor    %esi,%edi
    1992:	44 89 c6             	mov    %r8d,%esi
    1995:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
    199c:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    19a1:	c1 ee 0a             	shr    $0xa,%esi
    19a4:	44 31 c6             	xor    %r8d,%esi
    19a7:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    19ac:	c4 c1 79 6e 0c bf    	vmovd  (%r15,%rdi,4),%xmm1
    19b2:	c4 c3 71 22 0c b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm1,%xmm1
    19b9:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    19bd:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
    19c3:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
    19ca:	44 8b 80 75 fc ff ff 	mov    -0x38b(%rax),%r8d
    19d1:	44 8b 90 60 fc ff ff 	mov    -0x3a0(%rax),%r10d
    19d8:	44 8b 88 63 fc ff ff 	mov    -0x39d(%rax),%r9d
    19df:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    19e6:	8b 98 66 fc ff ff    	mov    -0x39a(%rax),%ebx
    19ec:	44 8b 98 69 fc ff ff 	mov    -0x397(%rax),%r11d
    19f3:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    19f7:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    19fe:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a05:	44 8b a8 6c fc ff ff 	mov    -0x394(%rax),%r13d
    1a0c:	44 8b a0 6f fc ff ff 	mov    -0x391(%rax),%r12d
    1a13:	44 89 d7             	mov    %r10d,%edi
    1a16:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1a1c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1a23:	8b b0 72 fc ff ff    	mov    -0x38e(%rax),%esi
    1a29:	c1 ef 0a             	shr    $0xa,%edi
    1a2c:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1a33:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    1a39:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1a40:	44 31 d7             	xor    %r10d,%edi
    1a43:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1a49:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    1a4e:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    1a53:	44 89 cf             	mov    %r9d,%edi
    1a56:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    1a5b:	c1 ef 0a             	shr    $0xa,%edi
    1a5e:	44 31 cf             	xor    %r9d,%edi
    1a61:	c4 81 79 6e 3c 97    	vmovd  (%r15,%r10,4),%xmm7
    1a67:	44 8b 90 78 fc ff ff 	mov    -0x388(%rax),%r10d
    1a6e:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    1a73:	89 df                	mov    %ebx,%edi
    1a75:	c1 ef 0a             	shr    $0xa,%edi
    1a78:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1a7f:	31 df                	xor    %ebx,%edi
    1a81:	c4 83 41 22 3c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm7,%xmm7
    1a88:	44 8b 88 7b fc ff ff 	mov    -0x385(%rax),%r9d
    1a8f:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    1a94:	44 89 df             	mov    %r11d,%edi
    1a97:	c1 ef 0a             	shr    $0xa,%edi
    1a9a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1aa1:	44 31 df             	xor    %r11d,%edi
    1aa4:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    1aa9:	44 89 ef             	mov    %r13d,%edi
    1aac:	c1 ef 0a             	shr    $0xa,%edi
    1aaf:	44 31 ef             	xor    %r13d,%edi
    1ab2:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    1ab7:	44 89 e7             	mov    %r12d,%edi
    1aba:	c1 ef 0a             	shr    $0xa,%edi
    1abd:	44 31 e7             	xor    %r12d,%edi
    1ac0:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    1ac6:	44 8b a8 84 fc ff ff 	mov    -0x37c(%rax),%r13d
    1acd:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    1ad2:	89 f7                	mov    %esi,%edi
    1ad4:	c1 ef 0a             	shr    $0xa,%edi
    1ad7:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1ade:	31 f7                	xor    %esi,%edi
    1ae0:	44 89 c6             	mov    %r8d,%esi
    1ae3:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
    1aea:	44 8b a0 87 fc ff ff 	mov    -0x379(%rax),%r12d
    1af1:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    1af6:	c1 ee 0a             	shr    $0xa,%esi
    1af9:	44 31 c6             	xor    %r8d,%esi
    1afc:	44 8b 80 8d fc ff ff 	mov    -0x373(%rax),%r8d
    1b03:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1b0a:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    1b0f:	c4 c1 79 6e 0c bf    	vmovd  (%r15,%rdi,4),%xmm1
    1b15:	44 89 d7             	mov    %r10d,%edi
    1b18:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    1b1f:	c4 c3 71 22 0c b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm1,%xmm1
    1b26:	8b b0 8a fc ff ff    	mov    -0x376(%rax),%esi
    1b2c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1b30:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
    1b36:	8b 98 7e fc ff ff    	mov    -0x382(%rax),%ebx
    1b3c:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1b42:	c4 83 71 22 0c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm1,%xmm1
    1b49:	44 8b 98 81 fc ff ff 	mov    -0x37f(%rax),%r11d
    1b50:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1b56:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1b5d:	c1 ef 0a             	shr    $0xa,%edi
    1b60:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    1b64:	44 31 d7             	xor    %r10d,%edi
    1b67:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    1b6d:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    1b72:	44 89 cf             	mov    %r9d,%edi
    1b75:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    1b7a:	c1 ef 0a             	shr    $0xa,%edi
    1b7d:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    1b82:	44 31 cf             	xor    %r9d,%edi
    1b85:	c4 81 79 6e 04 97    	vmovd  (%r15,%r10,4),%xmm0
    1b8b:	44 8b 90 90 fc ff ff 	mov    -0x370(%rax),%r10d
    1b92:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    1b97:	89 df                	mov    %ebx,%edi
    1b99:	c1 ef 0a             	shr    $0xa,%edi
    1b9c:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1ba3:	31 df                	xor    %ebx,%edi
    1ba5:	c4 83 79 22 04 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm0,%xmm0
    1bac:	44 8b 88 93 fc ff ff 	mov    -0x36d(%rax),%r9d
    1bb3:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    1bb8:	44 89 df             	mov    %r11d,%edi
    1bbb:	c1 ef 0a             	shr    $0xa,%edi
    1bbe:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1bc5:	44 31 df             	xor    %r11d,%edi
    1bc8:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    1bcd:	44 89 ef             	mov    %r13d,%edi
    1bd0:	c1 ef 0a             	shr    $0xa,%edi
    1bd3:	44 31 ef             	xor    %r13d,%edi
    1bd6:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    1bdb:	44 89 e7             	mov    %r12d,%edi
    1bde:	c1 ef 0a             	shr    $0xa,%edi
    1be1:	44 31 e7             	xor    %r12d,%edi
    1be4:	c4 81 79 6e 0c af    	vmovd  (%r15,%r13,4),%xmm1
    1bea:	44 8b a8 9c fc ff ff 	mov    -0x364(%rax),%r13d
    1bf1:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    1bf6:	89 f7                	mov    %esi,%edi
    1bf8:	c1 ef 0a             	shr    $0xa,%edi
    1bfb:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1c02:	31 f7                	xor    %esi,%edi
    1c04:	44 89 c6             	mov    %r8d,%esi
    1c07:	c4 83 71 22 0c a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm1,%xmm1
    1c0e:	44 8b a0 9f fc ff ff 	mov    -0x361(%rax),%r12d
    1c15:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    1c1a:	c1 ee 0a             	shr    $0xa,%esi
    1c1d:	44 31 c6             	xor    %r8d,%esi
    1c20:	44 8b 80 a5 fc ff ff 	mov    -0x35b(%rax),%r8d
    1c27:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1c2e:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    1c33:	c4 c1 79 6e 14 bf    	vmovd  (%r15,%rdi,4),%xmm2
    1c39:	44 89 d7             	mov    %r10d,%edi
    1c3c:	c1 ef 0a             	shr    $0xa,%edi
    1c3f:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    1c46:	c4 c3 69 22 14 b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm2,%xmm2
    1c4d:	44 31 d7             	xor    %r10d,%edi
    1c50:	8b b0 a2 fc ff ff    	mov    -0x35e(%rax),%esi
    1c56:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    1c5b:	44 89 cf             	mov    %r9d,%edi
    1c5e:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1c62:	c4 c1 79 6e 14 9f    	vmovd  (%r15,%rbx,4),%xmm2
    1c68:	8b 98 96 fc ff ff    	mov    -0x36a(%rax),%ebx
    1c6e:	c1 ef 0a             	shr    $0xa,%edi
    1c71:	44 31 cf             	xor    %r9d,%edi
    1c74:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1c7a:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1c80:	c4 83 69 22 14 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm2,%xmm2
    1c87:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    1c8c:	44 8b 98 99 fc ff ff 	mov    -0x367(%rax),%r11d
    1c93:	89 df                	mov    %ebx,%edi
    1c95:	c1 ef 0a             	shr    $0xa,%edi
    1c98:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1c9c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1ca3:	31 df                	xor    %ebx,%edi
    1ca5:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1cab:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    1cb0:	44 89 df             	mov    %r11d,%edi
    1cb3:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1cb8:	c1 ef 0a             	shr    $0xa,%edi
    1cbb:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1cc0:	44 31 df             	xor    %r11d,%edi
    1cc3:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    1cc8:	44 89 ef             	mov    %r13d,%edi
    1ccb:	c1 ef 0a             	shr    $0xa,%edi
    1cce:	44 31 ef             	xor    %r13d,%edi
    1cd1:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    1cd6:	44 89 e7             	mov    %r12d,%edi
    1cd9:	c1 ef 0a             	shr    $0xa,%edi
    1cdc:	44 31 e7             	xor    %r12d,%edi
    1cdf:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    1ce4:	89 f7                	mov    %esi,%edi
    1ce6:	c1 ef 0a             	shr    $0xa,%edi
    1ce9:	31 f7                	xor    %esi,%edi
    1ceb:	44 89 c6             	mov    %r8d,%esi
    1cee:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    1cf3:	c1 ee 0a             	shr    $0xa,%esi
    1cf6:	44 31 c6             	xor    %r8d,%esi
    1cf9:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    1cfe:	c4 41 79 6e 14 bf    	vmovd  (%r15,%rdi,4),%xmm10
    1d04:	c4 81 79 6e 0c 97    	vmovd  (%r15,%r10,4),%xmm1
    1d0a:	44 8b 90 a8 fc ff ff 	mov    -0x358(%rax),%r10d
    1d11:	c4 81 79 6e 14 af    	vmovd  (%r15,%r13,4),%xmm2
    1d17:	c4 43 29 22 14 b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm10,%xmm10
    1d1e:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1d25:	c4 83 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm1,%xmm1
    1d2c:	44 8b 88 ab fc ff ff 	mov    -0x355(%rax),%r9d
    1d33:	44 89 d7             	mov    %r10d,%edi
    1d36:	c4 83 69 22 14 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm2,%xmm2
    1d3d:	44 8b a8 b4 fc ff ff 	mov    -0x34c(%rax),%r13d
    1d44:	c1 ef 0a             	shr    $0xa,%edi
    1d47:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d4e:	44 8b a0 b7 fc ff ff 	mov    -0x349(%rax),%r12d
    1d55:	8b b0 ba fc ff ff    	mov    -0x346(%rax),%esi
    1d5b:	44 31 d7             	xor    %r10d,%edi
    1d5e:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    1d63:	c4 41 79 6e 14 9f    	vmovd  (%r15,%rbx,4),%xmm10
    1d69:	8b 98 ae fc ff ff    	mov    -0x352(%rax),%ebx
    1d6f:	45 0f b6 14 3e       	movzbl (%r14,%rdi,1),%r10d
    1d74:	44 89 cf             	mov    %r9d,%edi
    1d77:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1d7e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1d85:	c1 ef 0a             	shr    $0xa,%edi
    1d88:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1d8e:	c4 03 29 22 14 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm10,%xmm10
    1d95:	44 8b 98 b1 fc ff ff 	mov    -0x34f(%rax),%r11d
    1d9c:	44 31 cf             	xor    %r9d,%edi
    1d9f:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1da5:	44 8b 80 bd fc ff ff 	mov    -0x343(%rax),%r8d
    1dac:	45 0f b6 0c 3e       	movzbl (%r14,%rdi,1),%r9d
    1db1:	89 df                	mov    %ebx,%edi
    1db3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1dba:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1dbf:	c1 ef 0a             	shr    $0xa,%edi
    1dc2:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    1dc9:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1dcf:	c4 81 79 6e 14 97    	vmovd  (%r15,%r10,4),%xmm2
    1dd5:	31 df                	xor    %ebx,%edi
    1dd7:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1ddc:	41 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%ebx
    1de1:	44 89 df             	mov    %r11d,%edi
    1de4:	c4 83 69 22 14 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm2,%xmm2
    1deb:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1df0:	c1 ef 0a             	shr    $0xa,%edi
    1df3:	44 31 df             	xor    %r11d,%edi
    1df6:	45 0f b6 1c 3e       	movzbl (%r14,%rdi,1),%r11d
    1dfb:	44 89 ef             	mov    %r13d,%edi
    1dfe:	c1 ef 0a             	shr    $0xa,%edi
    1e01:	44 31 ef             	xor    %r13d,%edi
    1e04:	45 0f b6 2c 3e       	movzbl (%r14,%rdi,1),%r13d
    1e09:	44 89 e7             	mov    %r12d,%edi
    1e0c:	c1 ef 0a             	shr    $0xa,%edi
    1e0f:	44 31 e7             	xor    %r12d,%edi
    1e12:	c4 01 79 6e 14 af    	vmovd  (%r15,%r13,4),%xmm10
    1e18:	45 0f b6 24 3e       	movzbl (%r14,%rdi,1),%r12d
    1e1d:	89 f7                	mov    %esi,%edi
    1e1f:	c1 ef 0a             	shr    $0xa,%edi
    1e22:	31 f7                	xor    %esi,%edi
    1e24:	44 89 c6             	mov    %r8d,%esi
    1e27:	c4 03 29 22 14 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm10,%xmm10
    1e2e:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    1e33:	c1 ee 0a             	shr    $0xa,%esi
    1e36:	44 31 c6             	xor    %r8d,%esi
    1e39:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    1e40:	41 0f b6 34 36       	movzbl (%r14,%rsi,1),%esi
    1e45:	c4 41 79 6e 1c bf    	vmovd  (%r15,%rdi,4),%xmm11
    1e4b:	48 8d 79 40          	lea    0x40(%rcx),%rdi
    1e4f:	c4 43 21 22 1c b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm11,%xmm11
    1e56:	48 8d b1 88 00 00 00 	lea    0x88(%rcx),%rsi
    1e5d:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1e62:	c4 41 79 6e 1c 9f    	vmovd  (%r15,%rbx,4),%xmm11
    1e68:	c4 03 21 22 1c 9f 01 	vpinsrd $0x1,(%r15,%r11,4),%xmm11,%xmm11
    1e6f:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    1e74:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    1e79:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    1e7f:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    1e85:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    1e8a:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    1e90:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    1e96:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1e9b:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    1ea0:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    1ea5:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1eaa:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    1eb0:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    1eb6:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
    1ebd:	ff 
    1ebe:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    1ec2:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    1ec6:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
    1ecd:	ff 
    1ece:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
    1ed3:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1ed7:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    1edb:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1ee1:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1ee7:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1eed:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1ef3:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    1ef8:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1efc:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    1f02:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    1f08:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    1f0e:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    1f14:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1f1a:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
    1f1f:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    1f24:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
    1f29:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1f2f:	48 39 74 24 20       	cmp    %rsi,0x20(%rsp)
    1f34:	0f 83 ce f5 ff ff    	jae    1508 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x108>
    1f3a:	48 89 7c 24 18       	mov    %rdi,0x18(%rsp)
    1f3f:	48 8b 74 24 10       	mov    0x10(%rsp),%rsi
    1f44:	48 8d 41 68          	lea    0x68(%rcx),%rax
    1f48:	48 8b 7c 24 08       	mov    0x8(%rsp),%rdi
    1f4d:	0f ae f8             	sfence
    1f50:	48 39 44 24 20       	cmp    %rax,0x20(%rsp)
    1f55:	0f 82 ae 05 00 00    	jb     2509 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1109>
    1f5b:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
    1f60:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1f68 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb68>
    1f67:	00 
    1f68:	48 89 74 24 a8       	mov    %rsi,-0x58(%rsp)
    1f6d:	48 89 7c 24 a0       	mov    %rdi,-0x60(%rsp)
    1f72:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1f7a <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb7a>
    1f79:	00 
    1f7a:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
    1f7e:	4c 8d 1c 06          	lea    (%rsi,%rax,1),%r11
    1f82:	48 01 f8             	add    %rdi,%rax
    1f85:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
    1f8a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1f90:	41 8b 7b 09          	mov    0x9(%r11),%edi
    1f94:	41 8b 73 06          	mov    0x6(%r11),%esi
    1f98:	41 8b 4b 03          	mov    0x3(%r11),%ecx
    1f9c:	41 8b 13             	mov    (%r11),%edx
    1f9f:	41 8b 43 27          	mov    0x27(%r11),%eax
    1fa3:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    1fa9:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1faf:	41 8b 5b 15          	mov    0x15(%r11),%ebx
    1fb3:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1fb9:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    1fbf:	45 8b 53 12          	mov    0x12(%r11),%r10d
    1fc3:	45 8b 4b 0f          	mov    0xf(%r11),%r9d
    1fc7:	25 ff ff ff 00       	and    $0xffffff,%eax
    1fcc:	45 8b 43 0c          	mov    0xc(%r11),%r8d
    1fd0:	45 8b 63 2d          	mov    0x2d(%r11),%r12d
    1fd4:	89 7c 24 f8          	mov    %edi,-0x8(%rsp)
    1fd8:	45 8b 6b 2a          	mov    0x2a(%r11),%r13d
    1fdc:	41 8b 7b 21          	mov    0x21(%r11),%edi
    1fe0:	89 74 24 f4          	mov    %esi,-0xc(%rsp)
    1fe4:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1fea:	41 8b 73 1e          	mov    0x1e(%r11),%esi
    1fee:	89 4c 24 f0          	mov    %ecx,-0x10(%rsp)
    1ff2:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1ff9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    2000:	41 8b 4b 1b          	mov    0x1b(%r11),%ecx
    2004:	89 54 24 ec          	mov    %edx,-0x14(%rsp)
    2008:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    200f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    2016:	41 8b 53 18          	mov    0x18(%r11),%edx
    201a:	89 44 24 e0          	mov    %eax,-0x20(%rsp)
    201e:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    2025:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    202b:	41 8b 43 24          	mov    0x24(%r11),%eax
    202f:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    2035:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    203b:	89 5c 24 08          	mov    %ebx,0x8(%rsp)
    203f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    2045:	44 89 54 24 04       	mov    %r10d,0x4(%rsp)
    204a:	25 ff ff ff 00       	and    $0xffffff,%eax
    204f:	44 89 0c 24          	mov    %r9d,(%rsp)
    2053:	44 89 44 24 fc       	mov    %r8d,-0x4(%rsp)
    2058:	44 89 6c 24 e4       	mov    %r13d,-0x1c(%rsp)
    205d:	89 44 24 dc          	mov    %eax,-0x24(%rsp)
    2061:	89 7c 24 d8          	mov    %edi,-0x28(%rsp)
    2065:	89 74 24 d4          	mov    %esi,-0x2c(%rsp)
    2069:	89 4c 24 d0          	mov    %ecx,-0x30(%rsp)
    206d:	89 54 24 cc          	mov    %edx,-0x34(%rsp)
    2071:	44 89 64 24 e8       	mov    %r12d,-0x18(%rsp)
    2076:	45 8b 63 45          	mov    0x45(%r11),%r12d
    207a:	41 8b 43 39          	mov    0x39(%r11),%eax
    207e:	45 8b 4b 3f          	mov    0x3f(%r11),%r9d
    2082:	45 8b 53 42          	mov    0x42(%r11),%r10d
    2086:	45 8b 6b 3c          	mov    0x3c(%r11),%r13d
    208a:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    2091:	25 ff ff ff 00       	and    $0xffffff,%eax
    2096:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    209d:	45 8b 43 36          	mov    0x36(%r11),%r8d
    20a1:	41 8b 53 4b          	mov    0x4b(%r11),%edx
    20a5:	89 44 24 b8          	mov    %eax,-0x48(%rsp)
    20a9:	41 8b 43 33          	mov    0x33(%r11),%eax
    20ad:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    20b4:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    20bb:	44 89 4c 24 c0       	mov    %r9d,-0x40(%rsp)
    20c0:	45 8b 4b 48          	mov    0x48(%r11),%r9d
    20c4:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    20cb:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    20d1:	25 ff ff ff 00       	and    $0xffffff,%eax
    20d6:	41 8b 5b 4e          	mov    0x4e(%r11),%ebx
    20da:	44 89 64 24 c8       	mov    %r12d,-0x38(%rsp)
    20df:	89 c1                	mov    %eax,%ecx
    20e1:	41 8b 43 30          	mov    0x30(%r11),%eax
    20e5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    20ec:	45 8b 63 57          	mov    0x57(%r11),%r12d
    20f0:	44 89 54 24 c4       	mov    %r10d,-0x3c(%rsp)
    20f5:	45 8b 53 51          	mov    0x51(%r11),%r10d
    20f9:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    20ff:	25 ff ff ff 00       	and    $0xffffff,%eax
    2104:	44 89 6c 24 bc       	mov    %r13d,-0x44(%rsp)
    2109:	45 8b 6b 54          	mov    0x54(%r11),%r13d
    210d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    2114:	89 c6                	mov    %eax,%esi
    2116:	41 8b 43 5d          	mov    0x5d(%r11),%eax
    211a:	44 89 44 24 b4       	mov    %r8d,-0x4c(%rsp)
    211f:	41 89 d0             	mov    %edx,%r8d
    2122:	44 89 ca             	mov    %r9d,%edx
    2125:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    212c:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    2133:	25 ff ff ff 00       	and    $0xffffff,%eax
    2138:	89 c7                	mov    %eax,%edi
    213a:	41 8b 43 5a          	mov    0x5a(%r11),%eax
    213e:	25 ff ff ff 00       	and    $0xffffff,%eax
    2143:	c1 ea 0a             	shr    $0xa,%edx
    2146:	44 31 ca             	xor    %r9d,%edx
    2149:	45 0f b6 0c 16       	movzbl (%r14,%rdx,1),%r9d
    214e:	44 89 c2             	mov    %r8d,%edx
    2151:	c1 ea 0a             	shr    $0xa,%edx
    2154:	44 31 c2             	xor    %r8d,%edx
    2157:	45 0f b6 04 16       	movzbl (%r14,%rdx,1),%r8d
    215c:	89 da                	mov    %ebx,%edx
    215e:	c1 ea 0a             	shr    $0xa,%edx
    2161:	31 da                	xor    %ebx,%edx
    2163:	41 0f b6 1c 16       	movzbl (%r14,%rdx,1),%ebx
    2168:	44 89 d2             	mov    %r10d,%edx
    216b:	c1 ea 0a             	shr    $0xa,%edx
    216e:	44 31 d2             	xor    %r10d,%edx
    2171:	45 0f b6 14 16       	movzbl (%r14,%rdx,1),%r10d
    2176:	44 89 ea             	mov    %r13d,%edx
    2179:	c1 ea 0a             	shr    $0xa,%edx
    217c:	44 31 ea             	xor    %r13d,%edx
    217f:	45 0f b6 2c 16       	movzbl (%r14,%rdx,1),%r13d
    2184:	44 89 e2             	mov    %r12d,%edx
    2187:	c1 ea 0a             	shr    $0xa,%edx
    218a:	44 31 e2             	xor    %r12d,%edx
    218d:	45 0f b6 24 16       	movzbl (%r14,%rdx,1),%r12d
    2192:	89 c2                	mov    %eax,%edx
    2194:	c1 ea 0a             	shr    $0xa,%edx
    2197:	31 c2                	xor    %eax,%edx
    2199:	89 f8                	mov    %edi,%eax
    219b:	41 0f b6 14 16       	movzbl (%r14,%rdx,1),%edx
    21a0:	c1 e8 0a             	shr    $0xa,%eax
    21a3:	31 f8                	xor    %edi,%eax
    21a5:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    21aa:	c4 c1 79 6e 0c 97    	vmovd  (%r15,%rdx,4),%xmm1
    21b0:	c4 c3 71 22 0c 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm1,%xmm1
    21b7:	89 f0                	mov    %esi,%eax
    21b9:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    21bf:	c1 e8 0a             	shr    $0xa,%eax
    21c2:	c4 81 79 6e 2c 8f    	vmovd  (%r15,%r9,4),%xmm5
    21c8:	44 8b 6c 24 bc       	mov    -0x44(%rsp),%r13d
    21cd:	31 f0                	xor    %esi,%eax
    21cf:	c4 83 79 22 04 a7 01 	vpinsrd $0x1,(%r15,%r12,4),%xmm0,%xmm0
    21d6:	44 8b 4c 24 c0       	mov    -0x40(%rsp),%r9d
    21db:	41 0f b6 14 06       	movzbl (%r14,%rax,1),%edx
    21e0:	89 c8                	mov    %ecx,%eax
    21e2:	c4 83 51 22 2c 87 01 	vpinsrd $0x1,(%r15,%r8,4),%xmm5,%xmm5
    21e9:	c1 e8 0a             	shr    $0xa,%eax
    21ec:	44 8b 44 24 b4       	mov    -0x4c(%rsp),%r8d
    21f1:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    21f5:	c4 c1 79 6e 0c 9f    	vmovd  (%r15,%rbx,4),%xmm1
    21fb:	31 c8                	xor    %ecx,%eax
    21fd:	8b 5c 24 b8          	mov    -0x48(%rsp),%ebx
    2201:	44 8b 64 24 c8       	mov    -0x38(%rsp),%r12d
    2206:	41 0f b6 0c 06       	movzbl (%r14,%rax,1),%ecx
    220b:	44 89 c0             	mov    %r8d,%eax
    220e:	c4 83 71 22 0c 97 01 	vpinsrd $0x1,(%r15,%r10,4),%xmm1,%xmm1
    2215:	c1 e8 0a             	shr    $0xa,%eax
    2218:	44 8b 54 24 c4       	mov    -0x3c(%rsp),%r10d
    221d:	44 31 c0             	xor    %r8d,%eax
    2220:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    2224:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
    2229:	89 d8                	mov    %ebx,%eax
    222b:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    2231:	c4 c1 79 6e 04 97    	vmovd  (%r15,%rdx,4),%xmm0
    2237:	c1 e8 0a             	shr    $0xa,%eax
    223a:	8b 54 24 cc          	mov    -0x34(%rsp),%edx
    223e:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    2243:	31 d8                	xor    %ebx,%eax
    2245:	c4 c3 79 22 04 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm0,%xmm0
    224c:	8b 4c 24 d0          	mov    -0x30(%rsp),%ecx
    2250:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    2255:	41 0f b6 3c 06       	movzbl (%r14,%rax,1),%edi
    225a:	44 89 e8             	mov    %r13d,%eax
    225d:	c1 e8 0a             	shr    $0xa,%eax
    2260:	44 31 e8             	xor    %r13d,%eax
    2263:	45 0f b6 04 06       	movzbl (%r14,%rax,1),%r8d
    2268:	44 89 c8             	mov    %r9d,%eax
    226b:	c1 e8 0a             	shr    $0xa,%eax
    226e:	44 31 c8             	xor    %r9d,%eax
    2271:	c4 81 79 6e 0c 87    	vmovd  (%r15,%r8,4),%xmm1
    2277:	45 0f b6 0c 06       	movzbl (%r14,%rax,1),%r9d
    227c:	44 89 d0             	mov    %r10d,%eax
    227f:	c1 e8 0a             	shr    $0xa,%eax
    2282:	44 31 d0             	xor    %r10d,%eax
    2285:	c4 83 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm1,%xmm1
    228c:	45 0f b6 14 06       	movzbl (%r14,%rax,1),%r10d
    2291:	44 89 e0             	mov    %r12d,%eax
    2294:	c1 e8 0a             	shr    $0xa,%eax
    2297:	44 31 e0             	xor    %r12d,%eax
    229a:	c4 81 79 6e 14 97    	vmovd  (%r15,%r10,4),%xmm2
    22a0:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    22a5:	c4 c3 69 22 14 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm2,%xmm2
    22ac:	89 d0                	mov    %edx,%eax
    22ae:	c1 e8 0a             	shr    $0xa,%eax
    22b1:	31 d0                	xor    %edx,%eax
    22b3:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    22b7:	c4 c1 79 6e 14 b7    	vmovd  (%r15,%rsi,4),%xmm2
    22bd:	41 0f b6 14 06       	movzbl (%r14,%rax,1),%edx
    22c2:	89 c8                	mov    %ecx,%eax
    22c4:	c1 e8 0a             	shr    $0xa,%eax
    22c7:	c4 c3 69 22 14 bf 01 	vpinsrd $0x1,(%r15,%rdi,4),%xmm2,%xmm2
    22ce:	31 c8                	xor    %ecx,%eax
    22d0:	41 0f b6 0c 06       	movzbl (%r14,%rax,1),%ecx
    22d5:	8b 74 24 d4          	mov    -0x2c(%rsp),%esi
    22d9:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    22dd:	8b 7c 24 d8          	mov    -0x28(%rsp),%edi
    22e1:	44 8b 44 24 dc       	mov    -0x24(%rsp),%r8d
    22e6:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    22ec:	89 f0                	mov    %esi,%eax
    22ee:	8b 5c 24 e0          	mov    -0x20(%rsp),%ebx
    22f2:	44 8b 6c 24 e4       	mov    -0x1c(%rsp),%r13d
    22f7:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    22fc:	c1 e8 0a             	shr    $0xa,%eax
    22ff:	44 8b 64 24 e8       	mov    -0x18(%rsp),%r12d
    2304:	c4 c1 79 6e 0c 97    	vmovd  (%r15,%rdx,4),%xmm1
    230a:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    230f:	31 f0                	xor    %esi,%eax
    2311:	8b 54 24 ec          	mov    -0x14(%rsp),%edx
    2315:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    2319:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    231f:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
    2324:	89 f8                	mov    %edi,%eax
    2326:	c4 c3 71 22 0c 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm1,%xmm1
    232d:	c1 e8 0a             	shr    $0xa,%eax
    2330:	8b 4c 24 f0          	mov    -0x10(%rsp),%ecx
    2334:	31 f8                	xor    %edi,%eax
    2336:	41 0f b6 3c 06       	movzbl (%r14,%rax,1),%edi
    233b:	44 89 c0             	mov    %r8d,%eax
    233e:	c1 e8 0a             	shr    $0xa,%eax
    2341:	44 31 c0             	xor    %r8d,%eax
    2344:	45 0f b6 04 06       	movzbl (%r14,%rax,1),%r8d
    2349:	89 d8                	mov    %ebx,%eax
    234b:	c1 e8 0a             	shr    $0xa,%eax
    234e:	31 d8                	xor    %ebx,%eax
    2350:	c4 81 79 6e 14 87    	vmovd  (%r15,%r8,4),%xmm2
    2356:	44 8b 44 24 fc       	mov    -0x4(%rsp),%r8d
    235b:	45 0f b6 0c 06       	movzbl (%r14,%rax,1),%r9d
    2360:	44 89 e8             	mov    %r13d,%eax
    2363:	c1 e8 0a             	shr    $0xa,%eax
    2366:	44 31 e8             	xor    %r13d,%eax
    2369:	c4 83 69 22 14 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm2,%xmm2
    2370:	44 8b 0c 24          	mov    (%rsp),%r9d
    2374:	45 0f b6 14 06       	movzbl (%r14,%rax,1),%r10d
    2379:	44 89 e0             	mov    %r12d,%eax
    237c:	c1 e8 0a             	shr    $0xa,%eax
    237f:	44 31 e0             	xor    %r12d,%eax
    2382:	c4 81 79 6e 34 97    	vmovd  (%r15,%r10,4),%xmm6
    2388:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    238d:	c4 c3 49 22 34 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm6,%xmm6
    2394:	89 d0                	mov    %edx,%eax
    2396:	c1 e8 0a             	shr    $0xa,%eax
    2399:	31 d0                	xor    %edx,%eax
    239b:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    239f:	c4 c1 79 6e 34 b7    	vmovd  (%r15,%rsi,4),%xmm6
    23a5:	8b 74 24 f4          	mov    -0xc(%rsp),%esi
    23a9:	41 0f b6 14 06       	movzbl (%r14,%rax,1),%edx
    23ae:	89 c8                	mov    %ecx,%eax
    23b0:	c1 e8 0a             	shr    $0xa,%eax
    23b3:	c4 c3 49 22 34 bf 01 	vpinsrd $0x1,(%r15,%rdi,4),%xmm6,%xmm6
    23ba:	8b 7c 24 f8          	mov    -0x8(%rsp),%edi
    23be:	31 c8                	xor    %ecx,%eax
    23c0:	41 0f b6 0c 06       	movzbl (%r14,%rax,1),%ecx
    23c5:	89 f0                	mov    %esi,%eax
    23c7:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    23cb:	c1 e8 0a             	shr    $0xa,%eax
    23ce:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    23d4:	31 f0                	xor    %esi,%eax
    23d6:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    23db:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
    23e0:	89 f8                	mov    %edi,%eax
    23e2:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    23e7:	c1 e8 0a             	shr    $0xa,%eax
    23ea:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    23ee:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    23f4:	31 f8                	xor    %edi,%eax
    23f6:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    23fc:	41 0f b6 3c 06       	movzbl (%r14,%rax,1),%edi
    2401:	44 89 c0             	mov    %r8d,%eax
    2404:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    240a:	c1 e8 0a             	shr    $0xa,%eax
    240d:	44 31 c0             	xor    %r8d,%eax
    2410:	45 0f b6 04 06       	movzbl (%r14,%rax,1),%r8d
    2415:	44 89 c8             	mov    %r9d,%eax
    2418:	c1 e8 0a             	shr    $0xa,%eax
    241b:	44 31 c8             	xor    %r9d,%eax
    241e:	45 0f b6 0c 06       	movzbl (%r14,%rax,1),%r9d
    2423:	44 8b 54 24 04       	mov    0x4(%rsp),%r10d
    2428:	8b 5c 24 08          	mov    0x8(%rsp),%ebx
    242c:	c4 81 79 6e 34 87    	vmovd  (%r15,%r8,4),%xmm6
    2432:	44 89 d0             	mov    %r10d,%eax
    2435:	c4 c1 79 6e 14 97    	vmovd  (%r15,%rdx,4),%xmm2
    243b:	c1 e8 0a             	shr    $0xa,%eax
    243e:	c4 83 49 22 34 8f 01 	vpinsrd $0x1,(%r15,%r9,4),%xmm6,%xmm6
    2445:	44 31 d0             	xor    %r10d,%eax
    2448:	c4 c3 69 22 14 8f 01 	vpinsrd $0x1,(%r15,%rcx,4),%xmm2,%xmm2
    244f:	48 8b 4c 24 10       	mov    0x10(%rsp),%rcx
    2454:	45 0f b6 14 06       	movzbl (%r14,%rax,1),%r10d
    2459:	89 d8                	mov    %ebx,%eax
    245b:	c1 e8 0a             	shr    $0xa,%eax
    245e:	31 d8                	xor    %ebx,%eax
    2460:	c4 81 79 6e 3c 97    	vmovd  (%r15,%r10,4),%xmm7
    2466:	48 8b 5c 24 18       	mov    0x18(%rsp),%rbx
    246b:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    2470:	c4 c3 41 22 3c 87 01 	vpinsrd $0x1,(%r15,%rax,4),%xmm7,%xmm7
    2477:	48 8d 43 48          	lea    0x48(%rbx),%rax
    247b:	48 83 c3 20          	add    $0x20,%rbx
    247f:	48 83 c1 60          	add    $0x60,%rcx
    2483:	48 89 5c 24 18       	mov    %rbx,0x18(%rsp)
    2488:	49 83 c3 60          	add    $0x60,%r11
    248c:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    2490:	c4 c1 79 6e 3c b7    	vmovd  (%r15,%rsi,4),%xmm7
    2496:	c4 c3 41 22 3c bf 01 	vpinsrd $0x1,(%r15,%rdi,4),%xmm7,%xmm7
    249d:	c5 fe 7f 49 c0       	vmovdqu %ymm1,-0x40(%rcx)
    24a2:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    24a6:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    24aa:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    24b0:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    24b6:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    24bc:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    24c0:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    24c5:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    24cb:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    24d0:	c5 fe 7f 41 e0       	vmovdqu %ymm0,-0x20(%rcx)
    24d5:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    24d9:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    24df:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    24e4:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    24ea:	c5 fe 7f 51 a0       	vmovdqu %ymm2,-0x60(%rcx)
    24ef:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
    24f4:	48 39 44 24 20       	cmp    %rax,0x20(%rsp)
    24f9:	0f 83 91 fa ff ff    	jae    1f90 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb90>
    24ff:	48 8b 74 24 a8       	mov    -0x58(%rsp),%rsi
    2504:	48 8b 7c 24 a0       	mov    -0x60(%rsp),%rdi
    2509:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
    250e:	4c 8d 60 08          	lea    0x8(%rax),%r12
    2512:	4c 39 64 24 20       	cmp    %r12,0x20(%rsp)
    2517:	0f 82 97 01 00 00    	jb     26b4 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12b4>
    251d:	48 89 74 24 10       	mov    %rsi,0x10(%rsp)
    2522:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
    2526:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 252e <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x112e>
    252d:	00 
    252e:	48 89 7c 24 08       	mov    %rdi,0x8(%rsp)
    2533:	4c 8d 04 06          	lea    (%rsi,%rax,1),%r8
    2537:	48 8d 1c 07          	lea    (%rdi,%rax,1),%rbx
    253b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    2540:	49 8b 48 10          	mov    0x10(%r8),%rcx
    2544:	49 8b 40 08          	mov    0x8(%r8),%rax
    2548:	41 8b 50 10          	mov    0x10(%r8),%edx
    254c:	49 8b 30             	mov    (%r8),%rsi
    254f:	48 c1 e9 28          	shr    $0x28,%rcx
    2553:	49 89 c1             	mov    %rax,%r9
    2556:	41 89 c3             	mov    %eax,%r11d
    2559:	49 8b 78 10          	mov    0x10(%r8),%rdi
    255d:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
    2562:	48 89 c1             	mov    %rax,%rcx
    2565:	c1 e2 08             	shl    $0x8,%edx
    2568:	49 89 f2             	mov    %rsi,%r10
    256b:	48 c1 e9 38          	shr    $0x38,%rcx
    256f:	49 c1 ea 30          	shr    $0x30,%r10
    2573:	49 c1 e9 20          	shr    $0x20,%r9
    2577:	09 ca                	or     %ecx,%edx
    2579:	89 c1                	mov    %eax,%ecx
    257b:	41 c1 eb 08          	shr    $0x8,%r11d
    257f:	c1 e1 10             	shl    $0x10,%ecx
    2582:	c1 e8 12             	shr    $0x12,%eax
    2585:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    258c:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    2592:	44 09 d1             	or     %r10d,%ecx
    2595:	49 89 f2             	mov    %rsi,%r10
    2598:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    259e:	44 31 d8             	xor    %r11d,%eax
    25a1:	49 c1 ea 18          	shr    $0x18,%r10
    25a5:	41 89 f5             	mov    %esi,%r13d
    25a8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    25ae:	48 c1 ef 10          	shr    $0x10,%rdi
    25b2:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    25b9:	41 c1 ed 0a          	shr    $0xa,%r13d
    25bd:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    25c3:	41 31 f5             	xor    %esi,%r13d
    25c6:	44 89 d6             	mov    %r10d,%esi
    25c9:	c1 ee 0a             	shr    $0xa,%esi
    25cc:	47 0f b6 2c 2e       	movzbl (%r14,%r13,1),%r13d
    25d1:	44 31 d6             	xor    %r10d,%esi
    25d4:	45 0f b6 14 36       	movzbl (%r14,%rsi,1),%r10d
    25d9:	89 ce                	mov    %ecx,%esi
    25db:	c4 81 79 6e 04 af    	vmovd  (%r15,%r13,4),%xmm0
    25e1:	c1 ee 0a             	shr    $0xa,%esi
    25e4:	31 ce                	xor    %ecx,%esi
    25e6:	c4 83 79 22 04 97 01 	vpinsrd $0x1,(%r15,%r10,4),%xmm0,%xmm0
    25ed:	41 0f b6 0c 36       	movzbl (%r14,%rsi,1),%ecx
    25f2:	41 0f b6 34 06       	movzbl (%r14,%rax,1),%esi
    25f7:	44 89 c8             	mov    %r9d,%eax
    25fa:	c1 e8 0a             	shr    $0xa,%eax
    25fd:	44 31 c8             	xor    %r9d,%eax
    2600:	45 0f b6 0c 06       	movzbl (%r14,%rax,1),%r9d
    2605:	89 d0                	mov    %edx,%eax
    2607:	c1 e8 0a             	shr    $0xa,%eax
    260a:	31 d0                	xor    %edx,%eax
    260c:	c4 81 79 6e 0c 8f    	vmovd  (%r15,%r9,4),%xmm1
    2612:	41 0f b6 14 06       	movzbl (%r14,%rax,1),%edx
    2617:	89 f8                	mov    %edi,%eax
    2619:	c1 e8 0a             	shr    $0xa,%eax
    261c:	31 f8                	xor    %edi,%eax
    261e:	49 8b 78 10          	mov    0x10(%r8),%rdi
    2622:	c4 c3 71 22 0c 97 01 	vpinsrd $0x1,(%r15,%rdx,4),%xmm1,%xmm1
    2629:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    262e:	48 c1 ef 32          	shr    $0x32,%rdi
    2632:	48 33 7c 24 18       	xor    0x18(%rsp),%rdi
    2637:	c4 c1 79 6e 14 87    	vmovd  (%r15,%rax,4),%xmm2
    263d:	4c 89 e0             	mov    %r12,%rax
    2640:	49 83 c4 08          	add    $0x8,%r12
    2644:	41 0f b6 3c 3e       	movzbl (%r14,%rdi,1),%edi
    2649:	49 83 c0 18          	add    $0x18,%r8
    264d:	48 83 c3 18          	add    $0x18,%rbx
    2651:	c4 c3 69 22 14 bf 01 	vpinsrd $0x1,(%r15,%rdi,4),%xmm2,%xmm2
    2658:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    265c:	c4 c1 79 6e 14 8f    	vmovd  (%r15,%rcx,4),%xmm2
    2662:	c4 c3 69 22 14 b7 01 	vpinsrd $0x1,(%r15,%rsi,4),%xmm2,%xmm2
    2669:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    266d:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    2673:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    2678:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    267c:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    2682:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    2687:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    268c:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    2690:	c5 f9 d6 43 f8       	vmovq  %xmm0,-0x8(%rbx)
    2695:	c5 fa 7f 4b e8       	vmovdqu %xmm1,-0x18(%rbx)
    269a:	4c 39 64 24 20       	cmp    %r12,0x20(%rsp)
    269f:	0f 83 9b fe ff ff    	jae    2540 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1140>
    26a5:	48 8b 74 24 10       	mov    0x10(%rsp),%rsi
    26aa:	48 8b 7c 24 08       	mov    0x8(%rsp),%rdi
    26af:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
    26b4:	48 8b 5c 24 18       	mov    0x18(%rsp),%rbx
    26b9:	4c 8b 5c 24 20       	mov    0x20(%rsp),%r11
    26be:	4c 39 db             	cmp    %r11,%rbx
    26c1:	0f 83 41 02 00 00    	jae    2908 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1508>
    26c7:	48 8d 14 5b          	lea    (%rbx,%rbx,2),%rdx
    26cb:	4c 8d 04 16          	lea    (%rsi,%rdx,1),%r8
    26cf:	41 0f b6 40 01       	movzbl 0x1(%r8),%eax
    26d4:	45 0f b6 48 02       	movzbl 0x2(%r8),%r9d
    26d9:	45 0f b6 00          	movzbl (%r8),%r8d
    26dd:	c1 e0 08             	shl    $0x8,%eax
    26e0:	41 c1 e1 10          	shl    $0x10,%r9d
    26e4:	44 09 c8             	or     %r9d,%eax
    26e7:	41 09 c0             	or     %eax,%r8d
    26ea:	c1 e8 0a             	shr    $0xa,%eax
    26ed:	44 31 c0             	xor    %r8d,%eax
    26f0:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    26f5:	4d 8d 04 87          	lea    (%r15,%rax,4),%r8
    26f9:	41 8b 00             	mov    (%r8),%eax
    26fc:	45 0f b7 00          	movzwl (%r8),%r8d
    2700:	c1 e8 10             	shr    $0x10,%eax
    2703:	66 44 89 04 17       	mov    %r8w,(%rdi,%rdx,1)
    2708:	88 44 17 02          	mov    %al,0x2(%rdi,%rdx,1)
    270c:	48 8d 43 01          	lea    0x1(%rbx),%rax
    2710:	4c 39 d8             	cmp    %r11,%rax
    2713:	0f 83 ef 01 00 00    	jae    2908 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1508>
    2719:	4c 8d 44 16 03       	lea    0x3(%rsi,%rdx,1),%r8
    271e:	41 0f b6 40 01       	movzbl 0x1(%r8),%eax
    2723:	45 0f b6 48 02       	movzbl 0x2(%r8),%r9d
    2728:	45 0f b6 00          	movzbl (%r8),%r8d
    272c:	41 c1 e1 10          	shl    $0x10,%r9d
    2730:	c1 e0 08             	shl    $0x8,%eax
    2733:	44 09 c8             	or     %r9d,%eax
    2736:	41 09 c0             	or     %eax,%r8d
    2739:	c1 e8 0a             	shr    $0xa,%eax
    273c:	44 31 c0             	xor    %r8d,%eax
    273f:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    2744:	49 8d 04 87          	lea    (%r15,%rax,4),%rax
    2748:	44 8b 00             	mov    (%rax),%r8d
    274b:	44 0f b7 08          	movzwl (%rax),%r9d
    274f:	48 8d 43 02          	lea    0x2(%rbx),%rax
    2753:	44 89 c1             	mov    %r8d,%ecx
    2756:	66 44 89 4c 17 03    	mov    %r9w,0x3(%rdi,%rdx,1)
    275c:	c1 e9 10             	shr    $0x10,%ecx
    275f:	88 4c 17 05          	mov    %cl,0x5(%rdi,%rdx,1)
    2763:	4c 39 d8             	cmp    %r11,%rax
    2766:	0f 83 9c 01 00 00    	jae    2908 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1508>
    276c:	4c 8d 44 16 06       	lea    0x6(%rsi,%rdx,1),%r8
    2771:	41 0f b6 40 01       	movzbl 0x1(%r8),%eax
    2776:	45 0f b6 48 02       	movzbl 0x2(%r8),%r9d
    277b:	45 0f b6 00          	movzbl (%r8),%r8d
    277f:	41 c1 e1 10          	shl    $0x10,%r9d
    2783:	c1 e0 08             	shl    $0x8,%eax
    2786:	44 09 c8             	or     %r9d,%eax
    2789:	41 09 c0             	or     %eax,%r8d
    278c:	c1 e8 0a             	shr    $0xa,%eax
    278f:	44 31 c0             	xor    %r8d,%eax
    2792:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    2797:	49 8d 04 87          	lea    (%r15,%rax,4),%rax
    279b:	44 8b 00             	mov    (%rax),%r8d
    279e:	44 0f b7 08          	movzwl (%rax),%r9d
    27a2:	48 8d 43 03          	lea    0x3(%rbx),%rax
    27a6:	44 89 c1             	mov    %r8d,%ecx
    27a9:	66 44 89 4c 17 06    	mov    %r9w,0x6(%rdi,%rdx,1)
    27af:	c1 e9 10             	shr    $0x10,%ecx
    27b2:	88 4c 17 08          	mov    %cl,0x8(%rdi,%rdx,1)
    27b6:	4c 39 d8             	cmp    %r11,%rax
    27b9:	0f 83 49 01 00 00    	jae    2908 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1508>
    27bf:	4c 8d 44 16 09       	lea    0x9(%rsi,%rdx,1),%r8
    27c4:	41 0f b6 40 02       	movzbl 0x2(%r8),%eax
    27c9:	45 0f b6 48 01       	movzbl 0x1(%r8),%r9d
    27ce:	45 0f b6 00          	movzbl (%r8),%r8d
    27d2:	41 c1 e1 08          	shl    $0x8,%r9d
    27d6:	c1 e0 10             	shl    $0x10,%eax
    27d9:	44 09 c8             	or     %r9d,%eax
    27dc:	41 09 c0             	or     %eax,%r8d
    27df:	c1 e8 0a             	shr    $0xa,%eax
    27e2:	44 31 c0             	xor    %r8d,%eax
    27e5:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    27ea:	49 8d 04 87          	lea    (%r15,%rax,4),%rax
    27ee:	44 8b 00             	mov    (%rax),%r8d
    27f1:	44 0f b7 08          	movzwl (%rax),%r9d
    27f5:	48 8d 43 04          	lea    0x4(%rbx),%rax
    27f9:	44 89 c1             	mov    %r8d,%ecx
    27fc:	66 44 89 4c 17 09    	mov    %r9w,0x9(%rdi,%rdx,1)
    2802:	c1 e9 10             	shr    $0x10,%ecx
    2805:	88 4c 17 0b          	mov    %cl,0xb(%rdi,%rdx,1)
    2809:	4c 39 d8             	cmp    %r11,%rax
    280c:	0f 83 f6 00 00 00    	jae    2908 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1508>
    2812:	4c 8d 44 16 0c       	lea    0xc(%rsi,%rdx,1),%r8
    2817:	41 0f b6 40 02       	movzbl 0x2(%r8),%eax
    281c:	45 0f b6 48 01       	movzbl 0x1(%r8),%r9d
    2821:	45 0f b6 00          	movzbl (%r8),%r8d
    2825:	41 c1 e1 08          	shl    $0x8,%r9d
    2829:	c1 e0 10             	shl    $0x10,%eax
    282c:	44 09 c8             	or     %r9d,%eax
    282f:	41 09 c0             	or     %eax,%r8d
    2832:	c1 e8 0a             	shr    $0xa,%eax
    2835:	44 31 c0             	xor    %r8d,%eax
    2838:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    283d:	49 8d 04 87          	lea    (%r15,%rax,4),%rax
    2841:	44 8b 00             	mov    (%rax),%r8d
    2844:	44 0f b7 08          	movzwl (%rax),%r9d
    2848:	48 8d 43 05          	lea    0x5(%rbx),%rax
    284c:	44 89 c1             	mov    %r8d,%ecx
    284f:	66 44 89 4c 17 0c    	mov    %r9w,0xc(%rdi,%rdx,1)
    2855:	c1 e9 10             	shr    $0x10,%ecx
    2858:	88 4c 17 0e          	mov    %cl,0xe(%rdi,%rdx,1)
    285c:	4c 39 d8             	cmp    %r11,%rax
    285f:	0f 83 a3 00 00 00    	jae    2908 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1508>
    2865:	4c 8d 44 16 0f       	lea    0xf(%rsi,%rdx,1),%r8
    286a:	41 0f b6 40 02       	movzbl 0x2(%r8),%eax
    286f:	45 0f b6 48 01       	movzbl 0x1(%r8),%r9d
    2874:	45 0f b6 00          	movzbl (%r8),%r8d
    2878:	41 c1 e1 08          	shl    $0x8,%r9d
    287c:	c1 e0 10             	shl    $0x10,%eax
    287f:	44 09 c8             	or     %r9d,%eax
    2882:	41 09 c0             	or     %eax,%r8d
    2885:	c1 e8 0a             	shr    $0xa,%eax
    2888:	44 31 c0             	xor    %r8d,%eax
    288b:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    2890:	49 8d 04 87          	lea    (%r15,%rax,4),%rax
    2894:	44 8b 00             	mov    (%rax),%r8d
    2897:	44 0f b7 08          	movzwl (%rax),%r9d
    289b:	48 8d 43 06          	lea    0x6(%rbx),%rax
    289f:	44 89 c1             	mov    %r8d,%ecx
    28a2:	66 44 89 4c 17 0f    	mov    %r9w,0xf(%rdi,%rdx,1)
    28a8:	c1 e9 10             	shr    $0x10,%ecx
    28ab:	88 4c 17 11          	mov    %cl,0x11(%rdi,%rdx,1)
    28af:	4c 39 d8             	cmp    %r11,%rax
    28b2:	73 54                	jae    2908 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1508>
    28b4:	48 8d 4c 17 12       	lea    0x12(%rdi,%rdx,1),%rcx
    28b9:	48 8d 54 16 12       	lea    0x12(%rsi,%rdx,1),%rdx
    28be:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    28c2:	0f b6 72 02          	movzbl 0x2(%rdx),%esi
    28c6:	0f b6 12             	movzbl (%rdx),%edx
    28c9:	c1 e0 08             	shl    $0x8,%eax
    28cc:	c1 e6 10             	shl    $0x10,%esi
    28cf:	09 f0                	or     %esi,%eax
    28d1:	09 c2                	or     %eax,%edx
    28d3:	c1 e8 0a             	shr    $0xa,%eax
    28d6:	31 d0                	xor    %edx,%eax
    28d8:	41 0f b6 04 06       	movzbl (%r14,%rax,1),%eax
    28dd:	49 8d 14 87          	lea    (%r15,%rax,4),%rdx
    28e1:	8b 02                	mov    (%rdx),%eax
    28e3:	0f b7 12             	movzwl (%rdx),%edx
    28e6:	c1 e8 10             	shr    $0x10,%eax
    28e9:	66 89 11             	mov    %dx,(%rcx)
    28ec:	88 41 02             	mov    %al,0x2(%rcx)
    28ef:	c5 f8 77             	vzeroupper
    28f2:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    28f6:	5b                   	pop    %rbx
    28f7:	41 5c                	pop    %r12
    28f9:	41 5d                	pop    %r13
    28fb:	41 5e                	pop    %r14
    28fd:	41 5f                	pop    %r15
    28ff:	5d                   	pop    %rbp
    2900:	c3                   	ret
    2901:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    2908:	c5 f8 77             	vzeroupper
    290b:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    290f:	5b                   	pop    %rbx
    2910:	41 5c                	pop    %r12
    2912:	41 5d                	pop    %r13
    2914:	41 5e                	pop    %r14
    2916:	41 5f                	pop    %r15
    2918:	5d                   	pop    %rbp
    2919:	c3                   	ret
    291a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    2920:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
    2925:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
    292a:	e9 da fb ff ff       	jmp    2509 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1109>
    292f:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
    2934:	48 8d 41 28          	lea    0x28(%rcx),%rax
    2938:	e9 13 f6 ff ff       	jmp    1f50 <jshc_channel::avx2_chain_skew_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb50>
