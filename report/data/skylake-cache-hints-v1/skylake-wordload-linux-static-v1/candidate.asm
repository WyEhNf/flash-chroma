
artifacts/skylake-wordload-linux-build-v1/CMakeFiles/jshc_skylake_wordload.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	55                   	push   %rbp
       5:	48 89 e5             	mov    %rsp,%rbp
       8:	41 57                	push   %r15
       a:	41 56                	push   %r14
       c:	41 55                	push   %r13
       e:	41 54                	push   %r12
      10:	53                   	push   %rbx
      11:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
      15:	48 83 ec 28          	sub    $0x28,%rsp
      19:	4c 89 04 24          	mov    %r8,(%rsp)
      1d:	4d 85 c0             	test   %r8,%r8
      20:	0f 84 dd 00 00 00    	je     103 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x103>
      26:	4f 8d 14 00          	lea    (%r8,%r8,1),%r10
      2a:	b8 00 04 00 00       	mov    $0x400,%eax
      2f:	49 89 cf             	mov    %rcx,%r15
      32:	48 89 f3             	mov    %rsi,%rbx
      35:	4b 8d 0c 02          	lea    (%r10,%r8,1),%rcx
      39:	48 39 c1             	cmp    %rax,%rcx
      3c:	48 0f 47 c8          	cmova  %rax,%rcx
      40:	31 c0                	xor    %eax,%eax
      42:	0f 1f 00             	nopl   (%rax)
      45:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
      4c:	00 00 00 00 
      50:	41 0f 18 04 07       	prefetchnta (%r15,%rax,1)
      55:	48 83 c0 40          	add    $0x40,%rax
      59:	48 39 c8             	cmp    %rcx,%rax
      5c:	72 f2                	jb     50 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x50>
      5e:	4c 8b 0c 24          	mov    (%rsp),%r9
      62:	4d 89 f8             	mov    %r15,%r8
      65:	31 f6                	xor    %esi,%esi
      67:	eb 3b                	jmp    a4 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa4>
      69:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
      70:	83 e1 07             	and    $0x7,%ecx
      73:	8d 4c 49 08          	lea    0x8(%rcx,%rcx,2),%ecx
      77:	d3 e8                	shr    %cl,%eax
      79:	83 e0 07             	and    $0x7,%eax
      7c:	44 01 d8             	add    %r11d,%eax
      7f:	48 8d 0c 82          	lea    (%rdx,%rax,4),%rcx
      83:	48 ff c6             	inc    %rsi
      86:	49 83 c0 03          	add    $0x3,%r8
      8a:	8b 01                	mov    (%rcx),%eax
      8c:	0f b7 09             	movzwl (%rcx),%ecx
      8f:	c1 e8 10             	shr    $0x10,%eax
      92:	66 41 89 48 fd       	mov    %cx,-0x3(%r8)
      97:	41 88 40 ff          	mov    %al,-0x1(%r8)
      9b:	49 39 f1             	cmp    %rsi,%r9
      9e:	0f 84 5c 15 00 00    	je     1600 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1600>
      a4:	41 f6 c0 3f          	test   $0x3f,%r8b
      a8:	74 6e                	je     118 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x118>
      aa:	41 0f b6 08          	movzbl (%r8),%ecx
      ae:	41 0f b6 40 01       	movzbl 0x1(%r8),%eax
      b3:	c1 e1 10             	shl    $0x10,%ecx
      b6:	c1 e0 08             	shl    $0x8,%eax
      b9:	09 c1                	or     %eax,%ecx
      bb:	41 0f b6 40 02       	movzbl 0x2(%r8),%eax
      c0:	09 c1                	or     %eax,%ecx
      c2:	89 c8                	mov    %ecx,%eax
      c4:	c1 e8 03             	shr    $0x3,%eax
      c7:	8b 04 87             	mov    (%rdi,%rax,4),%eax
      ca:	44 0f b6 d8          	movzbl %al,%r11d
      ce:	41 81 fb ff 00 00 00 	cmp    $0xff,%r11d
      d5:	75 99                	jne    70 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x70>
      d7:	41 89 cb             	mov    %ecx,%r11d
      da:	c1 e8 08             	shr    $0x8,%eax
      dd:	83 e1 03             	and    $0x3,%ecx
      e0:	41 c1 eb 02          	shr    $0x2,%r11d
      e4:	c1 e1 03             	shl    $0x3,%ecx
      e7:	41 83 e3 01          	and    $0x1,%r11d
      eb:	44 01 d8             	add    %r11d,%eax
      ee:	89 c0                	mov    %eax,%eax
      f0:	8b 04 83             	mov    (%rbx,%rax,4),%eax
      f3:	d3 e8                	shr    %cl,%eax
      f5:	0f b6 c0             	movzbl %al,%eax
      f8:	eb 85                	jmp    7f <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7f>
      fa:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     100:	c5 f8 77             	vzeroupper
     103:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
     107:	5b                   	pop    %rbx
     108:	41 5c                	pop    %r12
     10a:	41 5d                	pop    %r13
     10c:	41 5e                	pop    %r14
     10e:	41 5f                	pop    %r15
     110:	5d                   	pop    %rbp
     111:	c3                   	ret
     112:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     118:	48 8d 46 48          	lea    0x48(%rsi),%rax
     11c:	48 39 04 24          	cmp    %rax,(%rsp)
     120:	0f 82 f3 14 00 00    	jb     1619 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1619>
     126:	b9 08 00 00 00       	mov    $0x8,%ecx
     12b:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
     12f:	48 8d 04 76          	lea    (%rsi,%rsi,2),%rax
     133:	4c 89 7c 24 f8       	mov    %r15,-0x8(%rsp)
     138:	c5 f9 6e f9          	vmovd  %ecx,%xmm7
     13c:	4c 89 54 24 f0       	mov    %r10,-0x10(%rsp)
     141:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 149 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x149>
     148:	00 
     149:	4c 01 f8             	add    %r15,%rax
     14c:	c4 e2 7d 58 ff       	vpbroadcastd %xmm7,%ymm7
     151:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 159 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x159>
     158:	00 
     159:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 161 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x161>
     160:	00 
     161:	c5 fd 72 d6 18       	vpsrld $0x18,%ymm6,%ymm0
     166:	c5 f5 72 d6 1d       	vpsrld $0x1d,%ymm6,%ymm1
     16b:	c5 fd 7f 7c 24 08    	vmovdqa %ymm7,0x8(%rsp)
     171:	eb 08                	jmp    17b <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x17b>
     173:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     178:	48 89 ce             	mov    %rcx,%rsi
     17b:	48 8d 8e 96 01 00 00 	lea    0x196(%rsi),%rcx
     182:	48 39 0c 24          	cmp    %rcx,(%rsp)
     186:	72 1c                	jb     1a4 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1a4>
     188:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
     18f:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
     196:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     19d:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     1a4:	44 8b 70 12          	mov    0x12(%rax),%r14d
     1a8:	44 8b 60 0c          	mov    0xc(%rax),%r12d
     1ac:	44 8b 68 15          	mov    0x15(%rax),%r13d
     1b0:	44 8b 58 0f          	mov    0xf(%rax),%r11d
     1b4:	41 0f ce             	bswap  %r14d
     1b7:	41 0f cc             	bswap  %r12d
     1ba:	41 c1 ee 0b          	shr    $0xb,%r14d
     1be:	41 c1 ec 0b          	shr    $0xb,%r12d
     1c2:	c4 a1 79 6e 1c b7    	vmovd  (%rdi,%r14,4),%xmm3
     1c8:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     1ce:	41 0f cd             	bswap  %r13d
     1d1:	41 0f cb             	bswap  %r11d
     1d4:	44 8b 50 06          	mov    0x6(%rax),%r10d
     1d8:	44 8b 00             	mov    (%rax),%r8d
     1db:	41 c1 eb 0b          	shr    $0xb,%r11d
     1df:	41 c1 ed 0b          	shr    $0xb,%r13d
     1e3:	c4 a3 61 22 1c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm3,%xmm3
     1ea:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
     1f1:	44 8b 48 09          	mov    0x9(%rax),%r9d
     1f5:	8b 48 03             	mov    0x3(%rax),%ecx
     1f8:	41 0f ca             	bswap  %r10d
     1fb:	41 0f c8             	bswap  %r8d
     1fe:	41 c1 ea 0b          	shr    $0xb,%r10d
     202:	41 c1 e8 0b          	shr    $0xb,%r8d
     206:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     20a:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
     210:	c4 a1 79 6e 1c 87    	vmovd  (%rdi,%r8,4),%xmm3
     216:	41 0f c9             	bswap  %r9d
     219:	0f c9                	bswap  %ecx
     21b:	41 c1 e9 0b          	shr    $0xb,%r9d
     21f:	c1 e9 0b             	shr    $0xb,%ecx
     222:	c4 a3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm7,%xmm7
     229:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
     230:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     234:	c5 fa 7e 78 10       	vmovq  0x10(%rax),%xmm7
     239:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     23f:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     243:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     247:	c4 e3 41 0f fa 0c    	vpalignr $0xc,%xmm2,%xmm7,%xmm7
     24d:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
     253:	c4 e2 6d 00 fc       	vpshufb %ymm4,%ymm2,%ymm7
     258:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
     25c:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
     262:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
     268:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
     26d:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
     272:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     276:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
     27b:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
     27f:	c4 c1 7d d7 c8       	vpmovmskb %ymm8,%ecx
     284:	85 c9                	test   %ecx,%ecx
     286:	74 42                	je     2ca <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2ca>
     288:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
     28d:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
     292:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
     296:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 29e <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x29e>
     29d:	00 
     29e:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     2a3:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     2a8:	c4 62 15 90 0c 9b    	vpgatherdd %ymm13,(%rbx,%ymm3,4),%ymm9
     2ae:	c5 c5 db 1d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm3        # 2b6 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2b6>
     2b5:	00 
     2b6:	c5 e5 72 f3 03       	vpslld $0x3,%ymm3,%ymm3
     2bb:	c4 e2 35 45 db       	vpsrlvd %ymm3,%ymm9,%ymm3
     2c0:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
     2c4:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
     2ca:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
     2ce:	44 8b 70 2a          	mov    0x2a(%rax),%r14d
     2d2:	44 8b 60 24          	mov    0x24(%rax),%r12d
     2d6:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
     2dc:	44 8b 68 2d          	mov    0x2d(%rax),%r13d
     2e0:	44 8b 58 27          	mov    0x27(%rax),%r11d
     2e4:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
     2e9:	41 0f ce             	bswap  %r14d
     2ec:	41 0f cc             	bswap  %r12d
     2ef:	41 c1 ee 0b          	shr    $0xb,%r14d
     2f3:	41 c1 ec 0b          	shr    $0xb,%r12d
     2f7:	c4 a1 79 6e 1c b7    	vmovd  (%rdi,%r14,4),%xmm3
     2fd:	c4 62 05 36 ea       	vpermd %ymm2,%ymm15,%ymm13
     302:	44 8b 50 1e          	mov    0x1e(%rax),%r10d
     306:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     30c:	44 8b 40 18          	mov    0x18(%rax),%r8d
     310:	41 0f cd             	bswap  %r13d
     313:	41 0f cb             	bswap  %r11d
     316:	41 c1 ed 0b          	shr    $0xb,%r13d
     31a:	41 c1 eb 0b          	shr    $0xb,%r11d
     31e:	44 8b 48 21          	mov    0x21(%rax),%r9d
     322:	8b 48 1b             	mov    0x1b(%rax),%ecx
     325:	c4 a3 61 22 1c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm3,%xmm3
     32c:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
     333:	41 0f ca             	bswap  %r10d
     336:	41 0f c8             	bswap  %r8d
     339:	41 c1 ea 0b          	shr    $0xb,%r10d
     33d:	41 c1 e8 0b          	shr    $0xb,%r8d
     341:	41 0f c9             	bswap  %r9d
     344:	0f c9                	bswap  %ecx
     346:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     34a:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
     350:	c4 a1 79 6e 1c 87    	vmovd  (%rdi,%r8,4),%xmm3
     356:	c1 e9 0b             	shr    $0xb,%ecx
     359:	41 c1 e9 0b          	shr    $0xb,%r9d
     35d:	c5 7a 7e 40 28       	vmovq  0x28(%rax),%xmm8
     362:	c4 a3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm7,%xmm7
     369:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
     370:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     374:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     37a:	c5 fa 6f 50 18       	vmovdqu 0x18(%rax),%xmm2
     37f:	c4 63 39 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm8,%xmm8
     385:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     389:	c4 c3 45 38 f8 01    	vinserti128 $0x1,%xmm8,%ymm7,%ymm7
     38f:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     393:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     398:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
     39c:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
     3a2:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
     3a8:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
     3ad:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
     3b2:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     3b6:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
     3bb:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
     3bf:	c4 c1 7d d7 c8       	vpmovmskb %ymm8,%ecx
     3c4:	85 c9                	test   %ecx,%ecx
     3c6:	74 42                	je     40a <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x40a>
     3c8:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
     3cd:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
     3d2:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 3da <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3da>
     3d9:	00 
     3da:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 3e2 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3e2>
     3e1:	00 
     3e2:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     3e7:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
     3eb:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
     3f0:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     3f5:	c4 62 0d 90 0c 9b    	vpgatherdd %ymm14,(%rbx,%ymm3,4),%ymm9
     3fb:	c4 e2 35 45 df       	vpsrlvd %ymm7,%ymm9,%ymm3
     400:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
     404:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
     40a:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
     40e:	44 8b 70 42          	mov    0x42(%rax),%r14d
     412:	44 8b 60 3c          	mov    0x3c(%rax),%r12d
     416:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
     41c:	44 8b 68 45          	mov    0x45(%rax),%r13d
     420:	44 8b 58 3f          	mov    0x3f(%rax),%r11d
     424:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
     429:	41 0f ce             	bswap  %r14d
     42c:	41 0f cc             	bswap  %r12d
     42f:	41 c1 ee 0b          	shr    $0xb,%r14d
     433:	41 c1 ec 0b          	shr    $0xb,%r12d
     437:	c4 a1 79 6e 1c b7    	vmovd  (%rdi,%r14,4),%xmm3
     43d:	c4 62 05 36 f2       	vpermd %ymm2,%ymm15,%ymm14
     442:	44 8b 50 36          	mov    0x36(%rax),%r10d
     446:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     44c:	44 8b 40 30          	mov    0x30(%rax),%r8d
     450:	41 0f cd             	bswap  %r13d
     453:	41 0f cb             	bswap  %r11d
     456:	41 c1 ed 0b          	shr    $0xb,%r13d
     45a:	41 c1 eb 0b          	shr    $0xb,%r11d
     45e:	44 8b 48 39          	mov    0x39(%rax),%r9d
     462:	8b 48 33             	mov    0x33(%rax),%ecx
     465:	c4 a3 61 22 1c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm3,%xmm3
     46c:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
     473:	41 0f ca             	bswap  %r10d
     476:	41 0f c8             	bswap  %r8d
     479:	41 c1 ea 0b          	shr    $0xb,%r10d
     47d:	41 c1 e8 0b          	shr    $0xb,%r8d
     481:	41 0f c9             	bswap  %r9d
     484:	0f c9                	bswap  %ecx
     486:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
     48c:	c1 e9 0b             	shr    $0xb,%ecx
     48f:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     493:	c4 a1 79 6e 1c 87    	vmovd  (%rdi,%r8,4),%xmm3
     499:	41 c1 e9 0b          	shr    $0xb,%r9d
     49d:	c4 a3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm7,%xmm7
     4a4:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
     4ab:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     4af:	c5 fa 6f 78 30       	vmovdqu 0x30(%rax),%xmm7
     4b4:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     4ba:	c5 fa 7e 50 40       	vmovq  0x40(%rax),%xmm2
     4bf:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     4c3:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
     4c9:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
     4cf:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     4d4:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
     4d8:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
     4de:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
     4e4:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
     4e9:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
     4ee:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     4f2:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
     4f7:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
     4fb:	c4 c1 7d d7 c8       	vpmovmskb %ymm8,%ecx
     500:	85 c9                	test   %ecx,%ecx
     502:	74 42                	je     546 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x546>
     504:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
     509:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
     50e:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 516 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x516>
     515:	00 
     516:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 51e <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x51e>
     51d:	00 
     51e:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     523:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
     527:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
     52c:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     531:	c4 62 1d 90 0c 9b    	vpgatherdd %ymm12,(%rbx,%ymm3,4),%ymm9
     537:	c4 e2 35 45 df       	vpsrlvd %ymm7,%ymm9,%ymm3
     53c:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
     540:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
     546:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
     54a:	44 8b 70 5a          	mov    0x5a(%rax),%r14d
     54e:	44 8b 60 54          	mov    0x54(%rax),%r12d
     552:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
     558:	44 8b 68 5d          	mov    0x5d(%rax),%r13d
     55c:	44 8b 58 57          	mov    0x57(%rax),%r11d
     560:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
     565:	41 0f ce             	bswap  %r14d
     568:	41 0f cc             	bswap  %r12d
     56b:	41 c1 ee 0b          	shr    $0xb,%r14d
     56f:	41 c1 ec 0b          	shr    $0xb,%r12d
     573:	c4 e2 05 36 fa       	vpermd %ymm2,%ymm15,%ymm7
     578:	c4 a1 79 6e 1c b7    	vmovd  (%rdi,%r14,4),%xmm3
     57e:	44 8b 50 4e          	mov    0x4e(%rax),%r10d
     582:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     588:	44 8b 40 48          	mov    0x48(%rax),%r8d
     58c:	41 0f cd             	bswap  %r13d
     58f:	41 0f cb             	bswap  %r11d
     592:	41 c1 ed 0b          	shr    $0xb,%r13d
     596:	41 c1 eb 0b          	shr    $0xb,%r11d
     59a:	44 8b 48 51          	mov    0x51(%rax),%r9d
     59e:	8b 48 4b             	mov    0x4b(%rax),%ecx
     5a1:	c4 a3 61 22 1c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm3,%xmm3
     5a8:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
     5af:	41 0f ca             	bswap  %r10d
     5b2:	41 0f c8             	bswap  %r8d
     5b5:	41 c1 ea 0b          	shr    $0xb,%r10d
     5b9:	41 c1 e8 0b          	shr    $0xb,%r8d
     5bd:	c5 fd 7f 7c 24 c8    	vmovdqa %ymm7,-0x38(%rsp)
     5c3:	41 0f c9             	bswap  %r9d
     5c6:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     5ca:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
     5d0:	c4 a1 79 6e 1c 87    	vmovd  (%rdi,%r8,4),%xmm3
     5d6:	41 c1 e9 0b          	shr    $0xb,%r9d
     5da:	0f c9                	bswap  %ecx
     5dc:	c1 e9 0b             	shr    $0xb,%ecx
     5df:	c4 a3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm7,%xmm7
     5e6:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
     5ed:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     5f1:	c5 fa 6f 78 48       	vmovdqu 0x48(%rax),%xmm7
     5f6:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     5fc:	c5 fa 7e 50 58       	vmovq  0x58(%rax),%xmm2
     601:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     605:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
     60b:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
     611:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     616:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
     61a:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
     620:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
     626:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
     62b:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
     630:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     634:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
     639:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
     63d:	c4 c1 7d d7 c8       	vpmovmskb %ymm8,%ecx
     642:	85 c9                	test   %ecx,%ecx
     644:	74 42                	je     688 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x688>
     646:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
     64b:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
     650:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 658 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x658>
     657:	00 
     658:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 660 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x660>
     65f:	00 
     660:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     665:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
     669:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
     66e:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     673:	c4 62 1d 90 0c 9b    	vpgatherdd %ymm12,(%rbx,%ymm3,4),%ymm9
     679:	c4 e2 35 45 df       	vpsrlvd %ymm7,%ymm9,%ymm3
     67e:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
     682:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
     688:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
     68c:	44 8b 78 72          	mov    0x72(%rax),%r15d
     690:	44 8b 60 6c          	mov    0x6c(%rax),%r12d
     694:	4c 8d 68 60          	lea    0x60(%rax),%r13
     698:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
     69e:	44 8b 70 75          	mov    0x75(%rax),%r14d
     6a2:	44 8b 58 6f          	mov    0x6f(%rax),%r11d
     6a6:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
     6ab:	41 0f cf             	bswap  %r15d
     6ae:	41 0f cc             	bswap  %r12d
     6b1:	41 c1 ef 0b          	shr    $0xb,%r15d
     6b5:	41 c1 ec 0b          	shr    $0xb,%r12d
     6b9:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
     6bf:	c4 62 05 36 da       	vpermd %ymm2,%ymm15,%ymm11
     6c4:	44 8b 50 66          	mov    0x66(%rax),%r10d
     6c8:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     6ce:	44 8b 40 60          	mov    0x60(%rax),%r8d
     6d2:	41 0f ce             	bswap  %r14d
     6d5:	41 0f cb             	bswap  %r11d
     6d8:	41 c1 ee 0b          	shr    $0xb,%r14d
     6dc:	41 c1 eb 0b          	shr    $0xb,%r11d
     6e0:	44 8b 48 69          	mov    0x69(%rax),%r9d
     6e4:	8b 48 63             	mov    0x63(%rax),%ecx
     6e7:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
     6ee:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
     6f5:	41 0f ca             	bswap  %r10d
     6f8:	41 0f c8             	bswap  %r8d
     6fb:	41 c1 ea 0b          	shr    $0xb,%r10d
     6ff:	41 c1 e8 0b          	shr    $0xb,%r8d
     703:	41 0f c9             	bswap  %r9d
     706:	0f c9                	bswap  %ecx
     708:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
     70e:	c1 e9 0b             	shr    $0xb,%ecx
     711:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     715:	c4 a1 79 6e 1c 87    	vmovd  (%rdi,%r8,4),%xmm3
     71b:	41 c1 e9 0b          	shr    $0xb,%r9d
     71f:	c4 a3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm7,%xmm7
     726:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
     72d:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     731:	c5 fa 6f 78 60       	vmovdqu 0x60(%rax),%xmm7
     736:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     73c:	c5 fa 7e 50 70       	vmovq  0x70(%rax),%xmm2
     741:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     745:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
     74b:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
     751:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     756:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
     75a:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
     760:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
     766:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
     76b:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
     770:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     774:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
     779:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
     77d:	c4 c1 7d d7 c8       	vpmovmskb %ymm8,%ecx
     782:	85 c9                	test   %ecx,%ecx
     784:	74 42                	je     7c8 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7c8>
     786:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
     78b:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
     790:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 798 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x798>
     797:	00 
     798:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 7a0 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7a0>
     79f:	00 
     7a0:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     7a5:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
     7a9:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
     7ae:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     7b3:	c4 62 1d 90 0c 9b    	vpgatherdd %ymm12,(%rbx,%ymm3,4),%ymm9
     7b9:	c4 62 35 45 cf       	vpsrlvd %ymm7,%ymm9,%ymm9
     7be:	c5 35 db c8          	vpand  %ymm0,%ymm9,%ymm9
     7c2:	c4 c3 6d 4c d1 80    	vpblendvb %ymm8,%ymm9,%ymm2,%ymm2
     7c8:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
     7cc:	44 8b b8 8a 00 00 00 	mov    0x8a(%rax),%r15d
     7d3:	44 8b a0 84 00 00 00 	mov    0x84(%rax),%r12d
     7da:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
     7e0:	44 8b b0 8d 00 00 00 	mov    0x8d(%rax),%r14d
     7e7:	44 8b 98 87 00 00 00 	mov    0x87(%rax),%r11d
     7ee:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
     7f3:	41 0f cf             	bswap  %r15d
     7f6:	41 0f cc             	bswap  %r12d
     7f9:	41 c1 ef 0b          	shr    $0xb,%r15d
     7fd:	41 c1 ec 0b          	shr    $0xb,%r12d
     801:	c4 e2 05 36 fa       	vpermd %ymm2,%ymm15,%ymm7
     806:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
     80c:	44 8b 50 7e          	mov    0x7e(%rax),%r10d
     810:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     816:	44 8b 40 78          	mov    0x78(%rax),%r8d
     81a:	41 0f ce             	bswap  %r14d
     81d:	41 0f cb             	bswap  %r11d
     820:	41 c1 ee 0b          	shr    $0xb,%r14d
     824:	41 c1 eb 0b          	shr    $0xb,%r11d
     828:	44 8b 88 81 00 00 00 	mov    0x81(%rax),%r9d
     82f:	8b 48 7b             	mov    0x7b(%rax),%ecx
     832:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
     839:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
     840:	41 0f ca             	bswap  %r10d
     843:	41 0f c8             	bswap  %r8d
     846:	41 c1 ea 0b          	shr    $0xb,%r10d
     84a:	41 c1 e8 0b          	shr    $0xb,%r8d
     84e:	c5 fd 7f 7c 24 a8    	vmovdqa %ymm7,-0x58(%rsp)
     854:	41 0f c9             	bswap  %r9d
     857:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     85b:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
     861:	c4 a1 79 6e 1c 87    	vmovd  (%rdi,%r8,4),%xmm3
     867:	41 c1 e9 0b          	shr    $0xb,%r9d
     86b:	0f c9                	bswap  %ecx
     86d:	c1 e9 0b             	shr    $0xb,%ecx
     870:	c4 a3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm7,%xmm7
     877:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
     87e:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     882:	c5 fa 6f 78 78       	vmovdqu 0x78(%rax),%xmm7
     887:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     88d:	c5 fa 7e 90 88 00 00 	vmovq  0x88(%rax),%xmm2
     894:	00 
     895:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     899:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
     89f:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
     8a5:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     8aa:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
     8ae:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
     8b4:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
     8ba:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
     8bf:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
     8c4:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     8c8:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
     8cd:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
     8d1:	c4 c1 7d d7 c8       	vpmovmskb %ymm8,%ecx
     8d6:	85 c9                	test   %ecx,%ecx
     8d8:	74 42                	je     91c <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x91c>
     8da:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
     8df:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
     8e4:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 8ec <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8ec>
     8eb:	00 
     8ec:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 8f4 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f4>
     8f3:	00 
     8f4:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     8f9:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
     8fd:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
     902:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     907:	c4 62 1d 90 0c 9b    	vpgatherdd %ymm12,(%rbx,%ymm3,4),%ymm9
     90d:	c4 62 35 45 cf       	vpsrlvd %ymm7,%ymm9,%ymm9
     912:	c5 35 db c8          	vpand  %ymm0,%ymm9,%ymm9
     916:	c4 c3 6d 4c d1 80    	vpblendvb %ymm8,%ymm9,%ymm2,%ymm2
     91c:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
     920:	44 8b b8 a2 00 00 00 	mov    0xa2(%rax),%r15d
     927:	44 8b a0 9c 00 00 00 	mov    0x9c(%rax),%r12d
     92e:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
     934:	44 8b b0 a5 00 00 00 	mov    0xa5(%rax),%r14d
     93b:	44 8b 98 9f 00 00 00 	mov    0x9f(%rax),%r11d
     942:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
     947:	41 0f cf             	bswap  %r15d
     94a:	41 0f cc             	bswap  %r12d
     94d:	41 c1 ef 0b          	shr    $0xb,%r15d
     951:	41 c1 ec 0b          	shr    $0xb,%r12d
     955:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
     95b:	c4 62 05 36 e2       	vpermd %ymm2,%ymm15,%ymm12
     960:	44 8b 90 96 00 00 00 	mov    0x96(%rax),%r10d
     967:	c4 a1 79 6e 14 a7    	vmovd  (%rdi,%r12,4),%xmm2
     96d:	44 8b 80 90 00 00 00 	mov    0x90(%rax),%r8d
     974:	41 0f ce             	bswap  %r14d
     977:	41 0f cb             	bswap  %r11d
     97a:	41 c1 ee 0b          	shr    $0xb,%r14d
     97e:	41 c1 eb 0b          	shr    $0xb,%r11d
     982:	44 8b 88 99 00 00 00 	mov    0x99(%rax),%r9d
     989:	8b 88 93 00 00 00    	mov    0x93(%rax),%ecx
     98f:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
     996:	c4 a3 69 22 14 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm2,%xmm2
     99d:	41 0f ca             	bswap  %r10d
     9a0:	41 0f c8             	bswap  %r8d
     9a3:	41 c1 ea 0b          	shr    $0xb,%r10d
     9a7:	41 c1 e8 0b          	shr    $0xb,%r8d
     9ab:	41 0f c9             	bswap  %r9d
     9ae:	0f c9                	bswap  %ecx
     9b0:	c4 a1 79 6e 3c 97    	vmovd  (%rdi,%r10,4),%xmm7
     9b6:	c1 e9 0b             	shr    $0xb,%ecx
     9b9:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     9bd:	c4 a1 79 6e 1c 87    	vmovd  (%rdi,%r8,4),%xmm3
     9c3:	41 c1 e9 0b          	shr    $0xb,%r9d
     9c7:	c4 a3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm7,%xmm7
     9ce:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
     9d5:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     9d9:	c5 fa 6f b8 90 00 00 	vmovdqu 0x90(%rax),%xmm7
     9e0:	00 
     9e1:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     9e7:	c5 fa 7e 90 a0 00 00 	vmovq  0xa0(%rax),%xmm2
     9ee:	00 
     9ef:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     9f3:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
     9f9:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
     9ff:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     a04:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
     a08:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
     a0e:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
     a14:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
     a19:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
     a1e:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     a22:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
     a27:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
     a2b:	c4 c1 7d d7 c8       	vpmovmskb %ymm8,%ecx
     a30:	85 c9                	test   %ecx,%ecx
     a32:	74 42                	je     a76 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa76>
     a34:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
     a39:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
     a3e:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # a46 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa46>
     a45:	00 
     a46:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # a4e <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa4e>
     a4d:	00 
     a4e:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     a53:	c5 7d 6f d6          	vmovdqa %ymm6,%ymm10
     a57:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
     a5c:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     a61:	c4 62 2d 90 0c 9b    	vpgatherdd %ymm10,(%rbx,%ymm3,4),%ymm9
     a67:	c4 62 35 45 cf       	vpsrlvd %ymm7,%ymm9,%ymm9
     a6c:	c5 35 db c8          	vpand  %ymm0,%ymm9,%ymm9
     a70:	c4 c3 6d 4c d1 80    	vpblendvb %ymm8,%ymm9,%ymm2,%ymm2
     a76:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
     a7a:	44 8b b8 ba 00 00 00 	mov    0xba(%rax),%r15d
     a81:	44 8b a0 b4 00 00 00 	mov    0xb4(%rax),%r12d
     a88:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
     a8e:	44 8b b0 bd 00 00 00 	mov    0xbd(%rax),%r14d
     a95:	44 8b 98 b7 00 00 00 	mov    0xb7(%rax),%r11d
     a9c:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
     aa1:	41 0f cf             	bswap  %r15d
     aa4:	41 0f cc             	bswap  %r12d
     aa7:	41 c1 ef 0b          	shr    $0xb,%r15d
     aab:	c4 e2 05 36 fa       	vpermd %ymm2,%ymm15,%ymm7
     ab0:	41 c1 ec 0b          	shr    $0xb,%r12d
     ab4:	44 8b 90 ae 00 00 00 	mov    0xae(%rax),%r10d
     abb:	44 8b 80 a8 00 00 00 	mov    0xa8(%rax),%r8d
     ac2:	c4 a1 79 6e 1c a7    	vmovd  (%rdi,%r12,4),%xmm3
     ac8:	c5 fd 7f 7c 24 88    	vmovdqa %ymm7,-0x78(%rsp)
     ace:	c4 a1 79 6e 3c bf    	vmovd  (%rdi,%r15,4),%xmm7
     ad4:	41 0f ce             	bswap  %r14d
     ad7:	41 0f cb             	bswap  %r11d
     ada:	41 c1 ee 0b          	shr    $0xb,%r14d
     ade:	41 c1 eb 0b          	shr    $0xb,%r11d
     ae2:	44 8b 88 b1 00 00 00 	mov    0xb1(%rax),%r9d
     ae9:	c4 a3 41 22 3c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm7,%xmm7
     af0:	c4 a3 61 22 1c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm3,%xmm3
     af7:	41 0f ca             	bswap  %r10d
     afa:	41 0f c8             	bswap  %r8d
     afd:	8b 88 ab 00 00 00    	mov    0xab(%rax),%ecx
     b03:	41 c1 e8 0b          	shr    $0xb,%r8d
     b07:	41 c1 ea 0b          	shr    $0xb,%r10d
     b0b:	41 0f c9             	bswap  %r9d
     b0e:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
     b12:	c4 21 79 6e 04 97    	vmovd  (%rdi,%r10,4),%xmm8
     b18:	c4 a1 79 6e 3c 87    	vmovd  (%rdi,%r8,4),%xmm7
     b1e:	41 c1 e9 0b          	shr    $0xb,%r9d
     b22:	0f c9                	bswap  %ecx
     b24:	c1 e9 0b             	shr    $0xb,%ecx
     b27:	c4 23 39 22 04 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm8,%xmm8
     b2e:	c4 e3 41 22 3c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm7,%xmm7
     b35:	c4 c1 41 6c f8       	vpunpcklqdq %xmm8,%xmm7,%xmm7
     b3a:	c5 7a 6f 80 a8 00 00 	vmovdqu 0xa8(%rax),%xmm8
     b41:	00 
     b42:	c4 e3 45 38 fb 01    	vinserti128 $0x1,%xmm3,%ymm7,%ymm7
     b48:	c5 fa 7e 98 b8 00 00 	vmovq  0xb8(%rax),%xmm3
     b4f:	00 
     b50:	c5 45 db c8          	vpand  %ymm0,%ymm7,%ymm9
     b54:	c4 c3 61 0f d8 0c    	vpalignr $0xc,%xmm8,%xmm3,%xmm3
     b5a:	c4 63 3d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm8,%ymm8
     b60:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
     b65:	c4 41 75 db d0       	vpand  %ymm8,%ymm1,%ymm10
     b6a:	c4 c1 65 72 f2 01    	vpslld $0x1,%ymm10,%ymm3
     b70:	c5 e5 fe 5c 24 08    	vpaddd 0x8(%rsp),%ymm3,%ymm3
     b76:	c4 c1 65 fe da       	vpaddd %ymm10,%ymm3,%ymm3
     b7b:	c4 e2 45 45 db       	vpsrlvd %ymm3,%ymm7,%ymm3
     b80:	c5 e5 db d9          	vpand  %ymm1,%ymm3,%ymm3
     b84:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
     b89:	c5 35 76 c8          	vpcmpeqd %ymm0,%ymm9,%ymm9
     b8d:	c4 c1 7d d7 c9       	vpmovmskb %ymm9,%ecx
     b92:	85 c9                	test   %ecx,%ecx
     b94:	74 44                	je     bda <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbda>
     b96:	c4 c1 2d 72 d0 02    	vpsrld $0x2,%ymm8,%ymm10
     b9c:	c5 c5 72 d7 08       	vpsrld $0x8,%ymm7,%ymm7
     ba1:	c5 3d db 05 00 00 00 	vpand  0x0(%rip),%ymm8,%ymm8        # ba9 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xba9>
     ba8:	00 
     ba9:	c5 2d db 15 00 00 00 	vpand  0x0(%rip),%ymm10,%ymm10        # bb1 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xbb1>
     bb0:	00 
     bb1:	c4 c1 45 db f9       	vpand  %ymm9,%ymm7,%ymm7
     bb6:	c5 fd 6f d6          	vmovdqa %ymm6,%ymm2
     bba:	c4 c1 3d 72 f0 03    	vpslld $0x3,%ymm8,%ymm8
     bc0:	c4 c1 45 fe fa       	vpaddd %ymm10,%ymm7,%ymm7
     bc5:	c4 62 6d 90 14 bb    	vpgatherdd %ymm2,(%rbx,%ymm7,4),%ymm10
     bcb:	c4 42 2d 45 d0       	vpsrlvd %ymm8,%ymm10,%ymm10
     bd0:	c5 2d db d0          	vpand  %ymm0,%ymm10,%ymm10
     bd4:	c4 c3 65 4c da 90    	vpblendvb %ymm9,%ymm10,%ymm3,%ymm3
     bda:	c5 7d 6f d6          	vmovdqa %ymm6,%ymm10
     bde:	c4 43 7d 39 e9 01    	vextracti128 $0x1,%ymm13,%xmm9
     be4:	c4 43 7d 39 f0 01    	vextracti128 $0x1,%ymm14,%xmm8
     bea:	48 05 c0 00 00 00    	add    $0xc0,%rax
     bf0:	c4 e2 2d 90 3c 9a    	vpgatherdd %ymm10,(%rdx,%ymm3,4),%ymm7
     bf6:	c4 41 79 6f d5       	vmovdqa %xmm13,%xmm10
     bfb:	c4 41 79 6f ee       	vmovdqa %xmm14,%xmm13
     c00:	c4 e2 45 00 dd       	vpshufb %ymm5,%ymm7,%ymm3
     c05:	c5 fd 6f 7c 24 c8    	vmovdqa -0x38(%rsp),%ymm7
     c0b:	c4 41 79 6f f3       	vmovdqa %xmm11,%xmm14
     c10:	c4 43 7d 39 db 01    	vextracti128 $0x1,%ymm11,%xmm11
     c16:	c4 43 39 0f c5 08    	vpalignr $0x8,%xmm13,%xmm8,%xmm8
     c1c:	c4 41 31 6c cd       	vpunpcklqdq %xmm13,%xmm9,%xmm9
     c21:	c4 e2 05 36 db       	vpermd %ymm3,%ymm15,%ymm3
     c26:	c5 f9 7f 7c 24 c8    	vmovdqa %xmm7,-0x38(%rsp)
     c2c:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     c32:	c4 43 21 0f de 08    	vpalignr $0x8,%xmm14,%xmm11,%xmm11
     c38:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
     c3e:	c4 63 3d 38 44 24 c8 	vinserti128 $0x1,-0x38(%rsp),%ymm8,%ymm8
     c45:	01 
     c46:	c4 c1 41 6c fe       	vpunpcklqdq %xmm14,%xmm7,%xmm7
     c4b:	c5 7d e7 90 40 ff ff 	vmovntdq %ymm10,-0xc0(%rax)
     c52:	ff 
     c53:	c5 79 6f d3          	vmovdqa %xmm3,%xmm10
     c57:	c4 c3 45 38 fb 01    	vinserti128 $0x1,%xmm11,%ymm7,%ymm7
     c5d:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     c63:	c4 41 79 6f dc       	vmovdqa %xmm12,%xmm11
     c68:	c5 7d e7 80 60 ff ff 	vmovntdq %ymm8,-0xa0(%rax)
     c6f:	ff 
     c70:	c5 fd e7 78 80       	vmovntdq %ymm7,-0x80(%rax)
     c75:	c5 fd 6f 7c 24 a8    	vmovdqa -0x58(%rsp),%ymm7
     c7b:	c5 fd 6f 54 24 88    	vmovdqa -0x78(%rsp),%ymm2
     c81:	c4 c3 61 0f da 08    	vpalignr $0x8,%xmm10,%xmm3,%xmm3
     c87:	4c 8d 86 88 00 00 00 	lea    0x88(%rsi),%r8
     c8e:	48 8d 4e 40          	lea    0x40(%rsi),%rcx
     c92:	c5 79 6f c7          	vmovdqa %xmm7,%xmm8
     c96:	c4 c3 7d 39 f9 01    	vextracti128 $0x1,%ymm7,%xmm9
     c9c:	c4 63 7d 39 e7 01    	vextracti128 $0x1,%ymm12,%xmm7
     ca2:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
     ca6:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     cac:	c4 41 31 6c cb       	vpunpcklqdq %xmm11,%xmm9,%xmm9
     cb1:	c4 c3 41 0f fb 08    	vpalignr $0x8,%xmm11,%xmm7,%xmm7
     cb7:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
     cbc:	c4 43 3d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm8,%ymm8
     cc2:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
     cc8:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
     cce:	c4 41 7d e7 45 00    	vmovntdq %ymm8,0x0(%r13)
     cd4:	c5 fd e7 78 c0       	vmovntdq %ymm7,-0x40(%rax)
     cd9:	c5 fd e7 50 e0       	vmovntdq %ymm2,-0x20(%rax)
     cde:	4c 39 04 24          	cmp    %r8,(%rsp)
     ce2:	0f 83 90 f4 ff ff    	jae    178 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x178>
     ce8:	4c 8b 7c 24 f8       	mov    -0x8(%rsp),%r15
     ced:	4c 8b 54 24 f0       	mov    -0x10(%rsp),%r10
     cf2:	48 8d 46 68          	lea    0x68(%rsi),%rax
     cf6:	0f ae f8             	sfence
     cf9:	4c 8b 34 24          	mov    (%rsp),%r14
     cfd:	49 39 c6             	cmp    %rax,%r14
     d00:	0f 82 0b 09 00 00    	jb     1611 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1611>
     d06:	be 08 00 00 00       	mov    $0x8,%esi
     d0b:	c4 41 3d 76 c0       	vpcmpeqd %ymm8,%ymm8,%ymm8
     d10:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     d14:	4c 89 54 24 a8       	mov    %r10,-0x58(%rsp)
     d19:	c5 79 6e d6          	vmovd  %esi,%xmm10
     d1d:	4c 89 7c 24 c8       	mov    %r15,-0x38(%rsp)
     d22:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # d2a <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd2a>
     d29:	00 
     d2a:	4c 01 f8             	add    %r15,%rax
     d2d:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # d35 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd35>
     d34:	00 
     d35:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # d3d <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd3d>
     d3c:	00 
     d3d:	c4 c1 4d 72 d0 18    	vpsrld $0x18,%ymm8,%ymm6
     d43:	c4 c1 45 72 d0 1d    	vpsrld $0x1d,%ymm8,%ymm7
     d49:	c4 42 7d 58 d2       	vpbroadcastd %xmm10,%ymm10
     d4e:	c4 c1 15 72 d0 1f    	vpsrld $0x1f,%ymm8,%ymm13
     d54:	4d 89 f2             	mov    %r14,%r10
     d57:	e9 e3 01 00 00       	jmp    f3f <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf3f>
     d5c:	0f 1f 40 00          	nopl   0x0(%rax)
     d60:	c5 fd 6f c8          	vmovdqa %ymm0,%ymm1
     d64:	44 8b 78 5a          	mov    0x5a(%rax),%r15d
     d68:	44 8b 68 54          	mov    0x54(%rax),%r13d
     d6c:	c5 7d 7f c4          	vmovdqa %ymm8,%ymm4
     d70:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
     d74:	44 8b 60 57          	mov    0x57(%rax),%r12d
     d78:	c4 e2 5d 90 04 8a    	vpgatherdd %ymm4,(%rdx,%ymm1,4),%ymm0
     d7e:	41 0f cf             	bswap  %r15d
     d81:	41 0f cd             	bswap  %r13d
     d84:	41 c1 ef 0b          	shr    $0xb,%r15d
     d88:	41 c1 ed 0b          	shr    $0xb,%r13d
     d8c:	c4 a1 79 6e 14 bf    	vmovd  (%rdi,%r15,4),%xmm2
     d92:	c4 a1 79 6e 0c af    	vmovd  (%rdi,%r13,4),%xmm1
     d98:	41 0f ce             	bswap  %r14d
     d9b:	41 0f cc             	bswap  %r12d
     d9e:	44 8b 58 4e          	mov    0x4e(%rax),%r11d
     da2:	44 8b 40 48          	mov    0x48(%rax),%r8d
     da6:	41 c1 ec 0b          	shr    $0xb,%r12d
     daa:	41 c1 ee 0b          	shr    $0xb,%r14d
     dae:	c4 a3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm2,%xmm2
     db5:	c4 a3 71 22 0c a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm1,%xmm1
     dbc:	44 8b 48 51          	mov    0x51(%rax),%r9d
     dc0:	8b 70 4b             	mov    0x4b(%rax),%esi
     dc3:	41 0f cb             	bswap  %r11d
     dc6:	41 0f c8             	bswap  %r8d
     dc9:	41 c1 eb 0b          	shr    $0xb,%r11d
     dcd:	41 c1 e8 0b          	shr    $0xb,%r8d
     dd1:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     dd5:	c4 a1 79 6e 1c 9f    	vmovd  (%rdi,%r11,4),%xmm3
     ddb:	c4 a1 79 6e 14 87    	vmovd  (%rdi,%r8,4),%xmm2
     de1:	41 0f c9             	bswap  %r9d
     de4:	0f ce                	bswap  %esi
     de6:	41 c1 e9 0b          	shr    $0xb,%r9d
     dea:	c1 ee 0b             	shr    $0xb,%esi
     ded:	c4 a3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm3,%xmm3
     df4:	c4 e3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm2,%xmm2
     dfb:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
     dff:	c5 fa 6f 58 48       	vmovdqu 0x48(%rax),%xmm3
     e04:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
     e0a:	c5 fa 7e 48 58       	vmovq  0x58(%rax),%xmm1
     e0f:	c5 ed db e6          	vpand  %ymm6,%ymm2,%ymm4
     e13:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
     e19:	c4 e3 65 38 d9 01    	vinserti128 $0x1,%xmm1,%ymm3,%ymm3
     e1f:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
     e24:	c5 45 db db          	vpand  %ymm3,%ymm7,%ymm11
     e28:	c4 c1 75 72 f3 01    	vpslld $0x1,%ymm11,%ymm1
     e2e:	c4 c1 75 fe ca       	vpaddd %ymm10,%ymm1,%ymm1
     e33:	c4 c1 75 fe cb       	vpaddd %ymm11,%ymm1,%ymm1
     e38:	c4 e2 6d 45 c9       	vpsrlvd %ymm1,%ymm2,%ymm1
     e3d:	c5 f5 db cf          	vpand  %ymm7,%ymm1,%ymm1
     e41:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
     e45:	c5 dd 76 e6          	vpcmpeqd %ymm6,%ymm4,%ymm4
     e49:	c5 fd d7 f4          	vpmovmskb %ymm4,%esi
     e4d:	85 f6                	test   %esi,%esi
     e4f:	74 3f                	je     e90 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe90>
     e51:	c5 a5 72 d3 02       	vpsrld $0x2,%ymm3,%ymm11
     e56:	c5 ed 72 d2 08       	vpsrld $0x8,%ymm2,%ymm2
     e5b:	c5 e5 db 1d 00 00 00 	vpand  0x0(%rip),%ymm3,%ymm3        # e63 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe63>
     e62:	00 
     e63:	c4 41 25 db dd       	vpand  %ymm13,%ymm11,%ymm11
     e68:	c5 ed db d4          	vpand  %ymm4,%ymm2,%ymm2
     e6c:	c4 41 7d 6f e0       	vmovdqa %ymm8,%ymm12
     e71:	c4 c1 6d fe d3       	vpaddd %ymm11,%ymm2,%ymm2
     e76:	c5 e5 72 f3 03       	vpslld $0x3,%ymm3,%ymm3
     e7b:	c4 62 1d 90 1c 93    	vpgatherdd %ymm12,(%rbx,%ymm2,4),%ymm11
     e81:	c4 62 25 45 db       	vpsrlvd %ymm3,%ymm11,%ymm11
     e86:	c5 25 db de          	vpand  %ymm6,%ymm11,%ymm11
     e8a:	c4 c3 75 4c cb 40    	vpblendvb %ymm4,%ymm11,%ymm1,%ymm1
     e90:	c5 7d 7f c4          	vmovdqa %ymm8,%ymm4
     e94:	c4 c2 0d 00 d9       	vpshufb %ymm9,%ymm14,%ymm3
     e99:	c4 c2 7d 00 c1       	vpshufb %ymm9,%ymm0,%ymm0
     e9e:	48 83 c0 60          	add    $0x60,%rax
     ea2:	c4 e2 5d 90 14 8a    	vpgatherdd %ymm4,(%rdx,%ymm1,4),%ymm2
     ea8:	c5 fd 6f 64 24 08    	vmovdqa 0x8(%rsp),%ymm4
     eae:	c4 e2 05 36 c0       	vpermd %ymm0,%ymm15,%ymm0
     eb3:	c4 e2 05 36 db       	vpermd %ymm3,%ymm15,%ymm3
     eb8:	c4 c2 6d 00 d1       	vpshufb %ymm9,%ymm2,%ymm2
     ebd:	c5 79 6f e0          	vmovdqa %xmm0,%xmm12
     ec1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     ec7:	c4 c2 5d 00 c9       	vpshufb %ymm9,%ymm4,%ymm1
     ecc:	c4 e2 05 36 d2       	vpermd %ymm2,%ymm15,%ymm2
     ed1:	c5 f9 6f e3          	vmovdqa %xmm3,%xmm4
     ed5:	c4 e2 05 36 c9       	vpermd %ymm1,%ymm15,%ymm1
     eda:	c5 79 6f f2          	vmovdqa %xmm2,%xmm14
     ede:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     ee4:	c5 79 6f d9          	vmovdqa %xmm1,%xmm11
     ee8:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     eee:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     ef4:	c4 c1 61 6c db       	vpunpcklqdq %xmm11,%xmm3,%xmm3
     ef9:	c4 c3 71 0f cb 08    	vpalignr $0x8,%xmm11,%xmm1,%xmm1
     eff:	c4 c1 79 6c c6       	vpunpcklqdq %xmm14,%xmm0,%xmm0
     f04:	c4 c3 69 0f d6 08    	vpalignr $0x8,%xmm14,%xmm2,%xmm2
     f0a:	c4 e3 5d 38 e3 01    	vinserti128 $0x1,%xmm3,%ymm4,%ymm4
     f10:	c4 c3 75 38 cc 01    	vinserti128 $0x1,%xmm12,%ymm1,%ymm1
     f16:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     f1c:	48 8d 71 20          	lea    0x20(%rcx),%rsi
     f20:	48 83 c1 48          	add    $0x48,%rcx
     f24:	c5 fe 7f 60 a0       	vmovdqu %ymm4,-0x60(%rax)
     f29:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     f2e:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     f33:	49 39 ca             	cmp    %rcx,%r10
     f36:	0f 82 84 03 00 00    	jb     12c0 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x12c0>
     f3c:	48 89 f1             	mov    %rsi,%rcx
     f3f:	44 8b 78 12          	mov    0x12(%rax),%r15d
     f43:	44 8b 68 0c          	mov    0xc(%rax),%r13d
     f47:	44 8b 70 15          	mov    0x15(%rax),%r14d
     f4b:	44 8b 60 0f          	mov    0xf(%rax),%r12d
     f4f:	41 0f cf             	bswap  %r15d
     f52:	41 0f cd             	bswap  %r13d
     f55:	41 c1 ef 0b          	shr    $0xb,%r15d
     f59:	41 c1 ed 0b          	shr    $0xb,%r13d
     f5d:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
     f63:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
     f69:	41 0f ce             	bswap  %r14d
     f6c:	41 0f cc             	bswap  %r12d
     f6f:	44 8b 58 06          	mov    0x6(%rax),%r11d
     f73:	44 8b 00             	mov    (%rax),%r8d
     f76:	41 c1 ec 0b          	shr    $0xb,%r12d
     f7a:	41 c1 ee 0b          	shr    $0xb,%r14d
     f7e:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
     f85:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
     f8c:	44 8b 48 09          	mov    0x9(%rax),%r9d
     f90:	8b 70 03             	mov    0x3(%rax),%esi
     f93:	41 0f cb             	bswap  %r11d
     f96:	41 0f c8             	bswap  %r8d
     f99:	41 c1 eb 0b          	shr    $0xb,%r11d
     f9d:	41 c1 e8 0b          	shr    $0xb,%r8d
     fa1:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     fa5:	c4 a1 79 6e 14 9f    	vmovd  (%rdi,%r11,4),%xmm2
     fab:	c4 a1 79 6e 0c 87    	vmovd  (%rdi,%r8,4),%xmm1
     fb1:	41 0f c9             	bswap  %r9d
     fb4:	0f ce                	bswap  %esi
     fb6:	41 c1 e9 0b          	shr    $0xb,%r9d
     fba:	c1 ee 0b             	shr    $0xb,%esi
     fbd:	c4 a3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm2,%xmm2
     fc4:	c4 e3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm1,%xmm1
     fcb:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     fcf:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     fd3:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     fd9:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
     fde:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
     fe2:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
     fe8:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     fee:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
     ff3:	c5 c5 db e2          	vpand  %ymm2,%ymm7,%ymm4
     ff7:	c5 fd 72 f4 01       	vpslld $0x1,%ymm4,%ymm0
     ffc:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
    1001:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    1005:	c4 e2 75 45 c0       	vpsrlvd %ymm0,%ymm1,%ymm0
    100a:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
    100e:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
    1012:	c5 e5 76 de          	vpcmpeqd %ymm6,%ymm3,%ymm3
    1016:	c5 fd d7 f3          	vpmovmskb %ymm3,%esi
    101a:	85 f6                	test   %esi,%esi
    101c:	74 3e                	je     105c <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x105c>
    101e:	c5 dd 72 d2 02       	vpsrld $0x2,%ymm2,%ymm4
    1023:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
    1028:	c5 ed db 15 00 00 00 	vpand  0x0(%rip),%ymm2,%ymm2        # 1030 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1030>
    102f:	00 
    1030:	c4 c1 5d db e5       	vpand  %ymm13,%ymm4,%ymm4
    1035:	c5 f5 db cb          	vpand  %ymm3,%ymm1,%ymm1
    1039:	c4 41 7d 6f f0       	vmovdqa %ymm8,%ymm14
    103e:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
    1042:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
    1047:	c4 e2 0d 90 24 8b    	vpgatherdd %ymm14,(%rbx,%ymm1,4),%ymm4
    104d:	c4 e2 5d 45 ca       	vpsrlvd %ymm2,%ymm4,%ymm1
    1052:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
    1056:	c4 e3 7d 4c c1 30    	vpblendvb %ymm3,%ymm1,%ymm0,%ymm0
    105c:	44 8b 78 2a          	mov    0x2a(%rax),%r15d
    1060:	44 8b 68 24          	mov    0x24(%rax),%r13d
    1064:	c5 7d 7f c4          	vmovdqa %ymm8,%ymm4
    1068:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
    106c:	44 8b 60 27          	mov    0x27(%rax),%r12d
    1070:	c4 62 5d 90 34 82    	vpgatherdd %ymm4,(%rdx,%ymm0,4),%ymm14
    1076:	41 0f cf             	bswap  %r15d
    1079:	41 0f cd             	bswap  %r13d
    107c:	41 c1 ef 0b          	shr    $0xb,%r15d
    1080:	41 c1 ed 0b          	shr    $0xb,%r13d
    1084:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    108a:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    1090:	41 0f ce             	bswap  %r14d
    1093:	41 0f cc             	bswap  %r12d
    1096:	44 8b 58 1e          	mov    0x1e(%rax),%r11d
    109a:	44 8b 40 18          	mov    0x18(%rax),%r8d
    109e:	41 c1 ec 0b          	shr    $0xb,%r12d
    10a2:	41 c1 ee 0b          	shr    $0xb,%r14d
    10a6:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    10ad:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    10b4:	44 8b 48 21          	mov    0x21(%rax),%r9d
    10b8:	8b 70 1b             	mov    0x1b(%rax),%esi
    10bb:	41 0f cb             	bswap  %r11d
    10be:	41 0f c8             	bswap  %r8d
    10c1:	41 c1 eb 0b          	shr    $0xb,%r11d
    10c5:	41 c1 e8 0b          	shr    $0xb,%r8d
    10c9:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    10cd:	c4 a1 79 6e 14 9f    	vmovd  (%rdi,%r11,4),%xmm2
    10d3:	c4 a1 79 6e 0c 87    	vmovd  (%rdi,%r8,4),%xmm1
    10d9:	41 0f c9             	bswap  %r9d
    10dc:	0f ce                	bswap  %esi
    10de:	41 c1 e9 0b          	shr    $0xb,%r9d
    10e2:	c1 ee 0b             	shr    $0xb,%esi
    10e5:	c4 a3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm2,%xmm2
    10ec:	c4 e3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm1,%xmm1
    10f3:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    10f7:	c5 fa 6f 50 18       	vmovdqu 0x18(%rax),%xmm2
    10fc:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1102:	c5 fa 7e 40 28       	vmovq  0x28(%rax),%xmm0
    1107:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
    110b:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    1111:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    1117:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
    111c:	c5 c5 db e2          	vpand  %ymm2,%ymm7,%ymm4
    1120:	c5 fd 72 f4 01       	vpslld $0x1,%ymm4,%ymm0
    1125:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
    112a:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    112e:	c4 e2 75 45 c0       	vpsrlvd %ymm0,%ymm1,%ymm0
    1133:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
    1137:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
    113b:	c5 e5 76 de          	vpcmpeqd %ymm6,%ymm3,%ymm3
    113f:	c5 fd d7 f3          	vpmovmskb %ymm3,%esi
    1143:	85 f6                	test   %esi,%esi
    1145:	74 3e                	je     1185 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1185>
    1147:	c5 dd 72 d2 02       	vpsrld $0x2,%ymm2,%ymm4
    114c:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
    1151:	c5 ed db 15 00 00 00 	vpand  0x0(%rip),%ymm2,%ymm2        # 1159 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1159>
    1158:	00 
    1159:	c4 c1 5d db e5       	vpand  %ymm13,%ymm4,%ymm4
    115e:	c5 f5 db cb          	vpand  %ymm3,%ymm1,%ymm1
    1162:	c4 41 7d 6f d8       	vmovdqa %ymm8,%ymm11
    1167:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
    116b:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
    1170:	c4 e2 25 90 24 8b    	vpgatherdd %ymm11,(%rbx,%ymm1,4),%ymm4
    1176:	c4 e2 5d 45 e2       	vpsrlvd %ymm2,%ymm4,%ymm4
    117b:	c5 dd db e6          	vpand  %ymm6,%ymm4,%ymm4
    117f:	c4 e3 7d 4c c4 30    	vpblendvb %ymm3,%ymm4,%ymm0,%ymm0
    1185:	44 8b 78 42          	mov    0x42(%rax),%r15d
    1189:	44 8b 68 3c          	mov    0x3c(%rax),%r13d
    118d:	c5 7d 7f c1          	vmovdqa %ymm8,%ymm1
    1191:	44 8b 70 45          	mov    0x45(%rax),%r14d
    1195:	44 8b 60 3f          	mov    0x3f(%rax),%r12d
    1199:	c4 e2 75 90 24 82    	vpgatherdd %ymm1,(%rdx,%ymm0,4),%ymm4
    119f:	41 0f cf             	bswap  %r15d
    11a2:	41 0f cd             	bswap  %r13d
    11a5:	41 c1 ef 0b          	shr    $0xb,%r15d
    11a9:	41 c1 ed 0b          	shr    $0xb,%r13d
    11ad:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    11b3:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    11b9:	41 0f ce             	bswap  %r14d
    11bc:	41 0f cc             	bswap  %r12d
    11bf:	44 8b 58 36          	mov    0x36(%rax),%r11d
    11c3:	44 8b 40 30          	mov    0x30(%rax),%r8d
    11c7:	41 c1 ec 0b          	shr    $0xb,%r12d
    11cb:	41 c1 ee 0b          	shr    $0xb,%r14d
    11cf:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    11d6:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    11dd:	c5 fd 7f 64 24 08    	vmovdqa %ymm4,0x8(%rsp)
    11e3:	44 8b 48 39          	mov    0x39(%rax),%r9d
    11e7:	8b 70 33             	mov    0x33(%rax),%esi
    11ea:	41 0f cb             	bswap  %r11d
    11ed:	41 0f c8             	bswap  %r8d
    11f0:	41 c1 eb 0b          	shr    $0xb,%r11d
    11f4:	41 c1 e8 0b          	shr    $0xb,%r8d
    11f8:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    11fc:	c4 a1 79 6e 14 9f    	vmovd  (%rdi,%r11,4),%xmm2
    1202:	c4 a1 79 6e 0c 87    	vmovd  (%rdi,%r8,4),%xmm1
    1208:	41 0f c9             	bswap  %r9d
    120b:	0f ce                	bswap  %esi
    120d:	41 c1 e9 0b          	shr    $0xb,%r9d
    1211:	c1 ee 0b             	shr    $0xb,%esi
    1214:	c4 a3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm2,%xmm2
    121b:	c4 e3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm1,%xmm1
    1222:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1226:	c5 fa 6f 50 30       	vmovdqu 0x30(%rax),%xmm2
    122b:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1231:	c5 fa 7e 40 40       	vmovq  0x40(%rax),%xmm0
    1236:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
    123a:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    1240:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    1246:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
    124b:	c5 c5 db e2          	vpand  %ymm2,%ymm7,%ymm4
    124f:	c5 fd 72 f4 01       	vpslld $0x1,%ymm4,%ymm0
    1254:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
    1259:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    125d:	c4 e2 75 45 c0       	vpsrlvd %ymm0,%ymm1,%ymm0
    1262:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
    1266:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
    126a:	c5 e5 76 de          	vpcmpeqd %ymm6,%ymm3,%ymm3
    126e:	c5 fd d7 f3          	vpmovmskb %ymm3,%esi
    1272:	85 f6                	test   %esi,%esi
    1274:	0f 84 e6 fa ff ff    	je     d60 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd60>
    127a:	c5 dd 72 d2 02       	vpsrld $0x2,%ymm2,%ymm4
    127f:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
    1284:	c5 ed db 15 00 00 00 	vpand  0x0(%rip),%ymm2,%ymm2        # 128c <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x128c>
    128b:	00 
    128c:	c4 c1 5d db e5       	vpand  %ymm13,%ymm4,%ymm4
    1291:	c5 f5 db cb          	vpand  %ymm3,%ymm1,%ymm1
    1295:	c4 41 7d 6f d8       	vmovdqa %ymm8,%ymm11
    129a:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
    129e:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
    12a3:	c4 e2 25 90 24 8b    	vpgatherdd %ymm11,(%rbx,%ymm1,4),%ymm4
    12a9:	c4 e2 5d 45 e2       	vpsrlvd %ymm2,%ymm4,%ymm4
    12ae:	c5 dd db e6          	vpand  %ymm6,%ymm4,%ymm4
    12b2:	c4 e3 7d 4c cc 30    	vpblendvb %ymm3,%ymm4,%ymm0,%ymm1
    12b8:	e9 a7 fa ff ff       	jmp    d64 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd64>
    12bd:	0f 1f 00             	nopl   (%rax)
    12c0:	4c 8b 7c 24 c8       	mov    -0x38(%rsp),%r15
    12c5:	4c 8b 54 24 a8       	mov    -0x58(%rsp),%r10
    12ca:	4c 8d 76 08          	lea    0x8(%rsi),%r14
    12ce:	4c 39 34 24          	cmp    %r14,(%rsp)
    12d2:	0f 82 31 03 00 00    	jb     1609 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1609>
    12d8:	b9 08 00 00 00       	mov    $0x8,%ecx
    12dd:	c5 e5 76 db          	vpcmpeqd %ymm3,%ymm3,%ymm3
    12e1:	48 8d 04 76          	lea    (%rsi,%rsi,2),%rax
    12e5:	4c 89 7c 24 08       	mov    %r15,0x8(%rsp)
    12ea:	c5 f9 6e e1          	vmovd  %ecx,%xmm4
    12ee:	4c 89 54 24 c8       	mov    %r10,-0x38(%rsp)
    12f3:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 12fb <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x12fb>
    12fa:	00 
    12fb:	4c 01 f8             	add    %r15,%rax
    12fe:	c5 7d 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm8        # 1306 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1306>
    1305:	00 
    1306:	c5 f5 72 d3 18       	vpsrld $0x18,%ymm3,%ymm1
    130b:	c5 ed 72 d3 1d       	vpsrld $0x1d,%ymm3,%ymm2
    1310:	c4 e2 7d 58 e4       	vpbroadcastd %xmm4,%ymm4
    1315:	c5 cd 72 d3 1f       	vpsrld $0x1f,%ymm3,%ymm6
    131a:	c5 d5 72 d3 1e       	vpsrld $0x1e,%ymm3,%ymm5
    131f:	eb 52                	jmp    1373 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1373>
    1321:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1328:	c5 7d 6f c8          	vmovdqa %ymm0,%ymm9
    132c:	c5 7d 6f eb          	vmovdqa %ymm3,%ymm13
    1330:	49 8d 4e 08          	lea    0x8(%r14),%rcx
    1334:	48 83 c0 18          	add    $0x18,%rax
    1338:	c4 a2 15 90 04 8a    	vpgatherdd %ymm13,(%rdx,%ymm9,4),%ymm0
    133e:	c4 c2 7d 00 c0       	vpshufb %ymm8,%ymm0,%ymm0
    1343:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
    1347:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    134d:	c5 b1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm9
    1352:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1357:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
    135c:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    1361:	c5 7a 7f 48 e8       	vmovdqu %xmm9,-0x18(%rax)
    1366:	48 39 0c 24          	cmp    %rcx,(%rsp)
    136a:	0f 82 e0 01 00 00    	jb     1550 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1550>
    1370:	49 89 ce             	mov    %rcx,%r14
    1373:	0f b6 30             	movzbl (%rax),%esi
    1376:	0f b6 48 01          	movzbl 0x1(%rax),%ecx
    137a:	44 0f b6 40 04       	movzbl 0x4(%rax),%r8d
    137f:	44 0f b6 48 06       	movzbl 0x6(%rax),%r9d
    1384:	c1 e1 08             	shl    $0x8,%ecx
    1387:	c1 e6 10             	shl    $0x10,%esi
    138a:	44 0f b6 50 0a       	movzbl 0xa(%rax),%r10d
    138f:	44 0f b6 58 0c       	movzbl 0xc(%rax),%r11d
    1394:	09 ce                	or     %ecx,%esi
    1396:	0f b6 48 02          	movzbl 0x2(%rax),%ecx
    139a:	41 c1 e0 08          	shl    $0x8,%r8d
    139e:	44 0f b6 60 0f       	movzbl 0xf(%rax),%r12d
    13a3:	41 c1 e1 10          	shl    $0x10,%r9d
    13a7:	41 c1 e2 08          	shl    $0x8,%r10d
    13ab:	44 0f b6 68 13       	movzbl 0x13(%rax),%r13d
    13b0:	44 0f b6 78 15       	movzbl 0x15(%rax),%r15d
    13b5:	41 c1 e3 10          	shl    $0x10,%r11d
    13b9:	09 ce                	or     %ecx,%esi
    13bb:	0f b6 48 03          	movzbl 0x3(%rax),%ecx
    13bf:	41 c1 e4 10          	shl    $0x10,%r12d
    13c3:	41 c1 e5 08          	shl    $0x8,%r13d
    13c7:	c1 ee 03             	shr    $0x3,%esi
    13ca:	c1 e1 10             	shl    $0x10,%ecx
    13cd:	44 09 c1             	or     %r8d,%ecx
    13d0:	44 0f b6 40 05       	movzbl 0x5(%rax),%r8d
    13d5:	44 09 c1             	or     %r8d,%ecx
    13d8:	44 0f b6 40 07       	movzbl 0x7(%rax),%r8d
    13dd:	c1 e9 03             	shr    $0x3,%ecx
    13e0:	41 c1 e0 08          	shl    $0x8,%r8d
    13e4:	45 09 c1             	or     %r8d,%r9d
    13e7:	44 0f b6 40 08       	movzbl 0x8(%rax),%r8d
    13ec:	45 09 c1             	or     %r8d,%r9d
    13ef:	44 0f b6 40 09       	movzbl 0x9(%rax),%r8d
    13f4:	41 c1 e9 03          	shr    $0x3,%r9d
    13f8:	41 c1 e0 10          	shl    $0x10,%r8d
    13fc:	c4 21 79 6e 14 8f    	vmovd  (%rdi,%r9,4),%xmm10
    1402:	45 09 d0             	or     %r10d,%r8d
    1405:	44 0f b6 50 0b       	movzbl 0xb(%rax),%r10d
    140a:	45 09 d0             	or     %r10d,%r8d
    140d:	44 0f b6 50 0d       	movzbl 0xd(%rax),%r10d
    1412:	41 c1 e8 03          	shr    $0x3,%r8d
    1416:	41 c1 e2 08          	shl    $0x8,%r10d
    141a:	c4 23 29 22 14 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm10,%xmm10
    1421:	45 09 d3             	or     %r10d,%r11d
    1424:	44 0f b6 50 0e       	movzbl 0xe(%rax),%r10d
    1429:	45 09 d3             	or     %r10d,%r11d
    142c:	44 0f b6 50 10       	movzbl 0x10(%rax),%r10d
    1431:	41 c1 eb 03          	shr    $0x3,%r11d
    1435:	41 c1 e2 08          	shl    $0x8,%r10d
    1439:	c4 a1 79 6e 04 9f    	vmovd  (%rdi,%r11,4),%xmm0
    143f:	45 09 e2             	or     %r12d,%r10d
    1442:	44 0f b6 60 11       	movzbl 0x11(%rax),%r12d
    1447:	45 09 e2             	or     %r12d,%r10d
    144a:	44 0f b6 60 12       	movzbl 0x12(%rax),%r12d
    144f:	41 c1 ea 03          	shr    $0x3,%r10d
    1453:	41 c1 e4 10          	shl    $0x10,%r12d
    1457:	c4 a3 79 22 04 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm0,%xmm0
    145e:	45 09 e5             	or     %r12d,%r13d
    1461:	44 0f b6 60 14       	movzbl 0x14(%rax),%r12d
    1466:	41 c1 e7 10          	shl    $0x10,%r15d
    146a:	45 09 e5             	or     %r12d,%r13d
    146d:	44 0f b6 60 16       	movzbl 0x16(%rax),%r12d
    1472:	41 c1 ed 03          	shr    $0x3,%r13d
    1476:	41 c1 e4 08          	shl    $0x8,%r12d
    147a:	c4 21 79 6e 0c af    	vmovd  (%rdi,%r13,4),%xmm9
    1480:	45 09 fc             	or     %r15d,%r12d
    1483:	44 0f b6 78 17       	movzbl 0x17(%rax),%r15d
    1488:	45 09 fc             	or     %r15d,%r12d
    148b:	41 c1 ec 03          	shr    $0x3,%r12d
    148f:	c4 23 31 22 0c a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm9,%xmm9
    1496:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    149b:	c5 79 6e 0c b7       	vmovd  (%rdi,%rsi,4),%xmm9
    14a0:	c4 63 31 22 0c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm9,%xmm9
    14a7:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    14ac:	c5 7a 6f 10          	vmovdqu (%rax),%xmm10
    14b0:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    14b6:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    14bb:	c5 35 db d9          	vpand  %ymm1,%ymm9,%ymm11
    14bf:	c4 c3 79 0f c2 0c    	vpalignr $0xc,%xmm10,%xmm0,%xmm0
    14c5:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
    14cb:	c4 62 2d 00 d7       	vpshufb %ymm7,%ymm10,%ymm10
    14d0:	c4 41 6d db e2       	vpand  %ymm10,%ymm2,%ymm12
    14d5:	c4 c1 7d 72 f4 01    	vpslld $0x1,%ymm12,%ymm0
    14db:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    14df:	c4 c1 7d fe c4       	vpaddd %ymm12,%ymm0,%ymm0
    14e4:	c4 e2 35 45 c0       	vpsrlvd %ymm0,%ymm9,%ymm0
    14e9:	c5 fd db c2          	vpand  %ymm2,%ymm0,%ymm0
    14ed:	c4 c1 7d fe c3       	vpaddd %ymm11,%ymm0,%ymm0
    14f2:	c5 25 76 d9          	vpcmpeqd %ymm1,%ymm11,%ymm11
    14f6:	c4 c1 7d d7 cb       	vpmovmskb %ymm11,%ecx
    14fb:	85 c9                	test   %ecx,%ecx
    14fd:	0f 84 25 fe ff ff    	je     1328 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1328>
    1503:	c4 c1 1d 72 d2 02    	vpsrld $0x2,%ymm10,%ymm12
    1509:	c4 c1 35 72 d1 08    	vpsrld $0x8,%ymm9,%ymm9
    150f:	c5 7d 6f fb          	vmovdqa %ymm3,%ymm15
    1513:	c5 1d db e6          	vpand  %ymm6,%ymm12,%ymm12
    1517:	c4 41 35 db cb       	vpand  %ymm11,%ymm9,%ymm9
    151c:	c4 41 55 db d2       	vpand  %ymm10,%ymm5,%ymm10
    1521:	c4 41 35 fe cc       	vpaddd %ymm12,%ymm9,%ymm9
    1526:	c4 c1 2d 72 f2 03    	vpslld $0x3,%ymm10,%ymm10
    152c:	c4 22 05 90 24 8b    	vpgatherdd %ymm15,(%rbx,%ymm9,4),%ymm12
    1532:	c4 42 1d 45 ca       	vpsrlvd %ymm10,%ymm12,%ymm9
    1537:	c5 35 db c9          	vpand  %ymm1,%ymm9,%ymm9
    153b:	c4 43 7d 4c c9 b0    	vpblendvb %ymm11,%ymm9,%ymm0,%ymm9
    1541:	e9 e6 fd ff ff       	jmp    132c <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x132c>
    1546:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    154d:	00 00 00 
    1550:	4c 8b 7c 24 08       	mov    0x8(%rsp),%r15
    1555:	4c 8b 54 24 c8       	mov    -0x38(%rsp),%r10
    155a:	48 8b 34 24          	mov    (%rsp),%rsi
    155e:	49 39 f6             	cmp    %rsi,%r14
    1561:	0f 83 99 eb ff ff    	jae    100 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x100>
    1567:	4b 8d 04 76          	lea    (%r14,%r14,2),%rax
    156b:	4e 8d 04 16          	lea    (%rsi,%r10,1),%r8
    156f:	4c 01 f8             	add    %r15,%rax
    1572:	4d 01 f8             	add    %r15,%r8
    1575:	eb 38                	jmp    15af <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x15af>
    1577:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    157e:	00 00 
    1580:	83 e1 07             	and    $0x7,%ecx
    1583:	8d 4c 49 08          	lea    0x8(%rcx,%rcx,2),%ecx
    1587:	d3 ee                	shr    %cl,%esi
    1589:	83 e6 07             	and    $0x7,%esi
    158c:	44 01 ce             	add    %r9d,%esi
    158f:	48 8d 34 b2          	lea    (%rdx,%rsi,4),%rsi
    1593:	48 83 c0 03          	add    $0x3,%rax
    1597:	8b 0e                	mov    (%rsi),%ecx
    1599:	0f b7 36             	movzwl (%rsi),%esi
    159c:	c1 e9 10             	shr    $0x10,%ecx
    159f:	66 89 70 fd          	mov    %si,-0x3(%rax)
    15a3:	88 48 ff             	mov    %cl,-0x1(%rax)
    15a6:	4c 39 c0             	cmp    %r8,%rax
    15a9:	0f 84 51 eb ff ff    	je     100 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x100>
    15af:	0f b6 08             	movzbl (%rax),%ecx
    15b2:	0f b6 70 01          	movzbl 0x1(%rax),%esi
    15b6:	c1 e1 10             	shl    $0x10,%ecx
    15b9:	c1 e6 08             	shl    $0x8,%esi
    15bc:	09 f1                	or     %esi,%ecx
    15be:	0f b6 70 02          	movzbl 0x2(%rax),%esi
    15c2:	09 f1                	or     %esi,%ecx
    15c4:	89 ce                	mov    %ecx,%esi
    15c6:	c1 ee 03             	shr    $0x3,%esi
    15c9:	8b 34 b7             	mov    (%rdi,%rsi,4),%esi
    15cc:	44 0f b6 ce          	movzbl %sil,%r9d
    15d0:	41 81 f9 ff 00 00 00 	cmp    $0xff,%r9d
    15d7:	75 a7                	jne    1580 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1580>
    15d9:	41 89 c9             	mov    %ecx,%r9d
    15dc:	c1 ee 08             	shr    $0x8,%esi
    15df:	83 e1 03             	and    $0x3,%ecx
    15e2:	41 c1 e9 02          	shr    $0x2,%r9d
    15e6:	c1 e1 03             	shl    $0x3,%ecx
    15e9:	41 83 e1 01          	and    $0x1,%r9d
    15ed:	44 01 ce             	add    %r9d,%esi
    15f0:	89 f6                	mov    %esi,%esi
    15f2:	8b 34 b3             	mov    (%rbx,%rsi,4),%esi
    15f5:	d3 ee                	shr    %cl,%esi
    15f7:	40 0f b6 f6          	movzbl %sil,%esi
    15fb:	eb 92                	jmp    158f <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x158f>
    15fd:	0f 1f 00             	nopl   (%rax)
    1600:	48 8b 34 24          	mov    (%rsp),%rsi
    1604:	e9 c1 fc ff ff       	jmp    12ca <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x12ca>
    1609:	49 89 f6             	mov    %rsi,%r14
    160c:	e9 49 ff ff ff       	jmp    155a <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x155a>
    1611:	48 89 ce             	mov    %rcx,%rsi
    1614:	e9 b1 fc ff ff       	jmp    12ca <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x12ca>
    1619:	48 8d 46 28          	lea    0x28(%rsi),%rax
    161d:	48 89 f1             	mov    %rsi,%rcx
    1620:	e9 d4 f6 ff ff       	jmp    cf9 <jshc_channel::avx2_chain_wordload(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcf9>
    1625:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
    162c:	00 00 00 00 

0000000000001630 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1630:	f3 0f 1e fa          	endbr64
    1634:	55                   	push   %rbp
    1635:	48 89 e5             	mov    %rsp,%rbp
    1638:	41 57                	push   %r15
    163a:	41 56                	push   %r14
    163c:	41 55                	push   %r13
    163e:	41 54                	push   %r12
    1640:	53                   	push   %rbx
    1641:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    1645:	48 83 ec 28          	sub    $0x28,%rsp
    1649:	4c 89 0c 24          	mov    %r9,(%rsp)
    164d:	4d 85 c9             	test   %r9,%r9
    1650:	0f 84 dd 00 00 00    	je     1733 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x103>
    1656:	4b 8d 1c 09          	lea    (%r9,%r9,1),%rbx
    165a:	b8 00 04 00 00       	mov    $0x400,%eax
    165f:	49 89 ca             	mov    %rcx,%r10
    1662:	49 89 f3             	mov    %rsi,%r11
    1665:	4a 8d 0c 0b          	lea    (%rbx,%r9,1),%rcx
    1669:	4d 89 c7             	mov    %r8,%r15
    166c:	48 39 c1             	cmp    %rax,%rcx
    166f:	48 0f 47 c8          	cmova  %rax,%rcx
    1673:	31 c0                	xor    %eax,%eax
    1675:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
    167c:	00 00 00 00 
    1680:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
    1685:	48 83 c0 40          	add    $0x40,%rax
    1689:	48 39 c8             	cmp    %rcx,%rax
    168c:	72 f2                	jb     1680 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x50>
    168e:	4c 8b 24 24          	mov    (%rsp),%r12
    1692:	4d 89 d1             	mov    %r10,%r9
    1695:	4d 89 f8             	mov    %r15,%r8
    1698:	31 f6                	xor    %esi,%esi
    169a:	eb 3c                	jmp    16d8 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa8>
    169c:	0f 1f 40 00          	nopl   0x0(%rax)
    16a0:	83 e1 07             	and    $0x7,%ecx
    16a3:	8d 4c 49 08          	lea    0x8(%rcx,%rcx,2),%ecx
    16a7:	d3 e8                	shr    %cl,%eax
    16a9:	83 e0 07             	and    $0x7,%eax
    16ac:	44 01 e8             	add    %r13d,%eax
    16af:	48 8d 0c 82          	lea    (%rdx,%rax,4),%rcx
    16b3:	48 ff c6             	inc    %rsi
    16b6:	49 83 c0 03          	add    $0x3,%r8
    16ba:	49 83 c1 03          	add    $0x3,%r9
    16be:	8b 01                	mov    (%rcx),%eax
    16c0:	0f b7 09             	movzwl (%rcx),%ecx
    16c3:	c1 e8 10             	shr    $0x10,%eax
    16c6:	66 41 89 48 fd       	mov    %cx,-0x3(%r8)
    16cb:	41 88 40 ff          	mov    %al,-0x1(%r8)
    16cf:	49 39 f4             	cmp    %rsi,%r12
    16d2:	0f 84 18 16 00 00    	je     2cf0 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x16c0>
    16d8:	41 f6 c0 3f          	test   $0x3f,%r8b
    16dc:	74 6a                	je     1748 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x118>
    16de:	41 0f b6 09          	movzbl (%r9),%ecx
    16e2:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
    16e7:	c1 e1 10             	shl    $0x10,%ecx
    16ea:	c1 e0 08             	shl    $0x8,%eax
    16ed:	09 c1                	or     %eax,%ecx
    16ef:	41 0f b6 41 02       	movzbl 0x2(%r9),%eax
    16f4:	09 c1                	or     %eax,%ecx
    16f6:	89 c8                	mov    %ecx,%eax
    16f8:	c1 e8 03             	shr    $0x3,%eax
    16fb:	8b 04 87             	mov    (%rdi,%rax,4),%eax
    16fe:	44 0f b6 e8          	movzbl %al,%r13d
    1702:	41 81 fd ff 00 00 00 	cmp    $0xff,%r13d
    1709:	75 95                	jne    16a0 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x70>
    170b:	41 89 cd             	mov    %ecx,%r13d
    170e:	c1 e8 08             	shr    $0x8,%eax
    1711:	83 e1 03             	and    $0x3,%ecx
    1714:	41 c1 ed 02          	shr    $0x2,%r13d
    1718:	c1 e1 03             	shl    $0x3,%ecx
    171b:	41 83 e5 01          	and    $0x1,%r13d
    171f:	44 01 e8             	add    %r13d,%eax
    1722:	89 c0                	mov    %eax,%eax
    1724:	41 8b 04 83          	mov    (%r11,%rax,4),%eax
    1728:	d3 e8                	shr    %cl,%eax
    172a:	0f b6 c0             	movzbl %al,%eax
    172d:	eb 80                	jmp    16af <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7f>
    172f:	90                   	nop
    1730:	c5 f8 77             	vzeroupper
    1733:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1737:	5b                   	pop    %rbx
    1738:	41 5c                	pop    %r12
    173a:	41 5d                	pop    %r13
    173c:	41 5e                	pop    %r14
    173e:	41 5f                	pop    %r15
    1740:	5d                   	pop    %rbp
    1741:	c3                   	ret
    1742:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1748:	48 8d 46 48          	lea    0x48(%rsi),%rax
    174c:	48 39 04 24          	cmp    %rax,(%rsp)
    1750:	0f 82 b3 15 00 00    	jb     2d09 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x16d9>
    1756:	41 b8 08 00 00 00    	mov    $0x8,%r8d
    175c:	48 8d 04 76          	lea    (%rsi,%rsi,2),%rax
    1760:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
    1764:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1769:	c4 c1 79 6e f8       	vmovd  %r8d,%xmm7
    176e:	49 8d 0c 07          	lea    (%r15,%rax,1),%rcx
    1772:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
    1777:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 177f <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x14f>
    177e:	00 
    177f:	c4 e2 7d 58 ff       	vpbroadcastd %xmm7,%ymm7
    1784:	4c 89 7c 24 e8       	mov    %r15,-0x18(%rsp)
    1789:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1791 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x161>
    1790:	00 
    1791:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
    1798:	00 
    1799:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 17a1 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x171>
    17a0:	00 
    17a1:	c5 fd 72 d6 18       	vpsrld $0x18,%ymm6,%ymm0
    17a6:	c5 f5 72 d6 1d       	vpsrld $0x1d,%ymm6,%ymm1
    17ab:	c5 fd 7f 7c 24 08    	vmovdqa %ymm7,0x8(%rsp)
    17b1:	eb 08                	jmp    17bb <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x18b>
    17b3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    17b8:	4c 89 c6             	mov    %r8,%rsi
    17bb:	4c 8d 86 96 01 00 00 	lea    0x196(%rsi),%r8
    17c2:	4c 39 04 24          	cmp    %r8,(%rsp)
    17c6:	72 15                	jb     17dd <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ad>
    17c8:	0f 18 00             	prefetchnta (%rax)
    17cb:	0f 18 40 40          	prefetchnta 0x40(%rax)
    17cf:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    17d6:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    17dd:	44 8b b8 12 fc ff ff 	mov    -0x3ee(%rax),%r15d
    17e4:	44 8b a8 0c fc ff ff 	mov    -0x3f4(%rax),%r13d
    17eb:	44 8b b0 15 fc ff ff 	mov    -0x3eb(%rax),%r14d
    17f2:	44 8b a0 0f fc ff ff 	mov    -0x3f1(%rax),%r12d
    17f9:	41 0f cf             	bswap  %r15d
    17fc:	41 0f cd             	bswap  %r13d
    17ff:	41 c1 ef 0b          	shr    $0xb,%r15d
    1803:	41 c1 ed 0b          	shr    $0xb,%r13d
    1807:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    180d:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    1813:	41 0f ce             	bswap  %r14d
    1816:	41 0f cc             	bswap  %r12d
    1819:	8b 98 06 fc ff ff    	mov    -0x3fa(%rax),%ebx
    181f:	44 8b 88 00 fc ff ff 	mov    -0x400(%rax),%r9d
    1826:	41 c1 ec 0b          	shr    $0xb,%r12d
    182a:	41 c1 ee 0b          	shr    $0xb,%r14d
    182e:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    1835:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    183c:	44 8b 90 09 fc ff ff 	mov    -0x3f7(%rax),%r10d
    1843:	44 8b 80 03 fc ff ff 	mov    -0x3fd(%rax),%r8d
    184a:	0f cb                	bswap  %ebx
    184c:	41 0f c9             	bswap  %r9d
    184f:	c1 eb 0b             	shr    $0xb,%ebx
    1852:	41 c1 e9 0b          	shr    $0xb,%r9d
    1856:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    185a:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    185f:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
    1865:	41 0f ca             	bswap  %r10d
    1868:	41 0f c8             	bswap  %r8d
    186b:	41 c1 ea 0b          	shr    $0xb,%r10d
    186f:	41 c1 e8 0b          	shr    $0xb,%r8d
    1873:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
    187a:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
    1881:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    1885:	c5 fa 7e b8 10 fc ff 	vmovq  -0x3f0(%rax),%xmm7
    188c:	ff 
    188d:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    1893:	c5 fa 6f 90 00 fc ff 	vmovdqu -0x400(%rax),%xmm2
    189a:	ff 
    189b:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    189f:	c4 e3 41 0f fa 0c    	vpalignr $0xc,%xmm2,%xmm7,%xmm7
    18a5:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
    18ab:	c4 e2 6d 00 fc       	vpshufb %ymm4,%ymm2,%ymm7
    18b0:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
    18b4:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
    18ba:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
    18c0:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
    18c5:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
    18ca:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    18ce:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
    18d3:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
    18d7:	c4 41 7d d7 c0       	vpmovmskb %ymm8,%r8d
    18dc:	45 85 c0             	test   %r8d,%r8d
    18df:	74 42                	je     1923 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2f3>
    18e1:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
    18e6:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
    18eb:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
    18ef:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 18f7 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2c7>
    18f6:	00 
    18f7:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    18fc:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    1901:	c4 42 15 90 0c 9b    	vpgatherdd %ymm13,(%r11,%ymm3,4),%ymm9
    1907:	c5 c5 db 1d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm3        # 190f <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2df>
    190e:	00 
    190f:	c5 e5 72 f3 03       	vpslld $0x3,%ymm3,%ymm3
    1914:	c4 e2 35 45 db       	vpsrlvd %ymm3,%ymm9,%ymm3
    1919:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
    191d:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
    1923:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
    1927:	44 8b b8 2a fc ff ff 	mov    -0x3d6(%rax),%r15d
    192e:	44 8b a8 24 fc ff ff 	mov    -0x3dc(%rax),%r13d
    1935:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
    193b:	44 8b b0 2d fc ff ff 	mov    -0x3d3(%rax),%r14d
    1942:	44 8b a0 27 fc ff ff 	mov    -0x3d9(%rax),%r12d
    1949:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
    194e:	41 0f cf             	bswap  %r15d
    1951:	41 0f cd             	bswap  %r13d
    1954:	41 c1 ef 0b          	shr    $0xb,%r15d
    1958:	41 c1 ed 0b          	shr    $0xb,%r13d
    195c:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    1962:	c4 62 05 36 ea       	vpermd %ymm2,%ymm15,%ymm13
    1967:	8b 98 1e fc ff ff    	mov    -0x3e2(%rax),%ebx
    196d:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    1973:	44 8b 88 18 fc ff ff 	mov    -0x3e8(%rax),%r9d
    197a:	41 0f ce             	bswap  %r14d
    197d:	41 0f cc             	bswap  %r12d
    1980:	41 c1 ee 0b          	shr    $0xb,%r14d
    1984:	41 c1 ec 0b          	shr    $0xb,%r12d
    1988:	44 8b 90 21 fc ff ff 	mov    -0x3df(%rax),%r10d
    198f:	44 8b 80 1b fc ff ff 	mov    -0x3e5(%rax),%r8d
    1996:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    199d:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    19a4:	0f cb                	bswap  %ebx
    19a6:	41 0f c9             	bswap  %r9d
    19a9:	c1 eb 0b             	shr    $0xb,%ebx
    19ac:	41 c1 e9 0b          	shr    $0xb,%r9d
    19b0:	41 0f ca             	bswap  %r10d
    19b3:	41 0f c8             	bswap  %r8d
    19b6:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    19ba:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    19bf:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
    19c5:	41 c1 e8 0b          	shr    $0xb,%r8d
    19c9:	41 c1 ea 0b          	shr    $0xb,%r10d
    19cd:	c5 7a 7e 80 28 fc ff 	vmovq  -0x3d8(%rax),%xmm8
    19d4:	ff 
    19d5:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
    19dc:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
    19e3:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    19e7:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    19ed:	c5 fa 6f 90 18 fc ff 	vmovdqu -0x3e8(%rax),%xmm2
    19f4:	ff 
    19f5:	c4 63 39 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm8,%xmm8
    19fb:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    19ff:	c4 c3 45 38 f8 01    	vinserti128 $0x1,%xmm8,%ymm7,%ymm7
    1a05:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    1a09:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    1a0e:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
    1a12:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
    1a18:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
    1a1e:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
    1a23:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
    1a28:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    1a2c:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
    1a31:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
    1a35:	c4 41 7d d7 c0       	vpmovmskb %ymm8,%r8d
    1a3a:	45 85 c0             	test   %r8d,%r8d
    1a3d:	74 42                	je     1a81 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x451>
    1a3f:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
    1a44:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
    1a49:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 1a51 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x421>
    1a50:	00 
    1a51:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 1a59 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x429>
    1a58:	00 
    1a59:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    1a5e:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
    1a62:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
    1a67:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    1a6c:	c4 42 0d 90 0c 9b    	vpgatherdd %ymm14,(%r11,%ymm3,4),%ymm9
    1a72:	c4 e2 35 45 df       	vpsrlvd %ymm7,%ymm9,%ymm3
    1a77:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
    1a7b:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
    1a81:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
    1a85:	44 8b b8 42 fc ff ff 	mov    -0x3be(%rax),%r15d
    1a8c:	44 8b a8 3c fc ff ff 	mov    -0x3c4(%rax),%r13d
    1a93:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
    1a99:	44 8b b0 45 fc ff ff 	mov    -0x3bb(%rax),%r14d
    1aa0:	44 8b a0 3f fc ff ff 	mov    -0x3c1(%rax),%r12d
    1aa7:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
    1aac:	41 0f cf             	bswap  %r15d
    1aaf:	41 0f cd             	bswap  %r13d
    1ab2:	41 c1 ef 0b          	shr    $0xb,%r15d
    1ab6:	41 c1 ed 0b          	shr    $0xb,%r13d
    1aba:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    1ac0:	c4 62 05 36 f2       	vpermd %ymm2,%ymm15,%ymm14
    1ac5:	8b 98 36 fc ff ff    	mov    -0x3ca(%rax),%ebx
    1acb:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    1ad1:	44 8b 88 30 fc ff ff 	mov    -0x3d0(%rax),%r9d
    1ad8:	41 0f ce             	bswap  %r14d
    1adb:	41 0f cc             	bswap  %r12d
    1ade:	41 c1 ee 0b          	shr    $0xb,%r14d
    1ae2:	41 c1 ec 0b          	shr    $0xb,%r12d
    1ae6:	44 8b 90 39 fc ff ff 	mov    -0x3c7(%rax),%r10d
    1aed:	44 8b 80 33 fc ff ff 	mov    -0x3cd(%rax),%r8d
    1af4:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    1afb:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    1b02:	0f cb                	bswap  %ebx
    1b04:	41 0f c9             	bswap  %r9d
    1b07:	c1 eb 0b             	shr    $0xb,%ebx
    1b0a:	41 c1 e9 0b          	shr    $0xb,%r9d
    1b0e:	41 0f ca             	bswap  %r10d
    1b11:	41 0f c8             	bswap  %r8d
    1b14:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    1b19:	41 c1 e8 0b          	shr    $0xb,%r8d
    1b1d:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    1b21:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
    1b27:	41 c1 ea 0b          	shr    $0xb,%r10d
    1b2b:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
    1b32:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
    1b39:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    1b3d:	c5 fa 6f b8 30 fc ff 	vmovdqu -0x3d0(%rax),%xmm7
    1b44:	ff 
    1b45:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    1b4b:	c5 fa 7e 90 40 fc ff 	vmovq  -0x3c0(%rax),%xmm2
    1b52:	ff 
    1b53:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    1b57:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
    1b5d:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
    1b63:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    1b68:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
    1b6c:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
    1b72:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
    1b78:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
    1b7d:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
    1b82:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    1b86:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
    1b8b:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
    1b8f:	c4 41 7d d7 c0       	vpmovmskb %ymm8,%r8d
    1b94:	45 85 c0             	test   %r8d,%r8d
    1b97:	74 42                	je     1bdb <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x5ab>
    1b99:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
    1b9e:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
    1ba3:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 1bab <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x57b>
    1baa:	00 
    1bab:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 1bb3 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x583>
    1bb2:	00 
    1bb3:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    1bb8:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
    1bbc:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
    1bc1:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    1bc6:	c4 42 1d 90 0c 9b    	vpgatherdd %ymm12,(%r11,%ymm3,4),%ymm9
    1bcc:	c4 e2 35 45 df       	vpsrlvd %ymm7,%ymm9,%ymm3
    1bd1:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
    1bd5:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
    1bdb:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
    1bdf:	44 8b b8 5a fc ff ff 	mov    -0x3a6(%rax),%r15d
    1be6:	44 8b a8 54 fc ff ff 	mov    -0x3ac(%rax),%r13d
    1bed:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
    1bf3:	44 8b b0 5d fc ff ff 	mov    -0x3a3(%rax),%r14d
    1bfa:	44 8b a0 57 fc ff ff 	mov    -0x3a9(%rax),%r12d
    1c01:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
    1c06:	41 0f cf             	bswap  %r15d
    1c09:	41 0f cd             	bswap  %r13d
    1c0c:	41 c1 ef 0b          	shr    $0xb,%r15d
    1c10:	41 c1 ed 0b          	shr    $0xb,%r13d
    1c14:	c4 e2 05 36 fa       	vpermd %ymm2,%ymm15,%ymm7
    1c19:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    1c1f:	8b 98 4e fc ff ff    	mov    -0x3b2(%rax),%ebx
    1c25:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    1c2b:	44 8b 88 48 fc ff ff 	mov    -0x3b8(%rax),%r9d
    1c32:	41 0f ce             	bswap  %r14d
    1c35:	41 0f cc             	bswap  %r12d
    1c38:	41 c1 ee 0b          	shr    $0xb,%r14d
    1c3c:	41 c1 ec 0b          	shr    $0xb,%r12d
    1c40:	44 8b 90 51 fc ff ff 	mov    -0x3af(%rax),%r10d
    1c47:	44 8b 80 4b fc ff ff 	mov    -0x3b5(%rax),%r8d
    1c4e:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    1c55:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    1c5c:	0f cb                	bswap  %ebx
    1c5e:	41 0f c9             	bswap  %r9d
    1c61:	c1 eb 0b             	shr    $0xb,%ebx
    1c64:	41 c1 e9 0b          	shr    $0xb,%r9d
    1c68:	c5 fd 7f 7c 24 c8    	vmovdqa %ymm7,-0x38(%rsp)
    1c6e:	41 0f ca             	bswap  %r10d
    1c71:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    1c75:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    1c7a:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
    1c80:	41 c1 ea 0b          	shr    $0xb,%r10d
    1c84:	41 0f c8             	bswap  %r8d
    1c87:	41 c1 e8 0b          	shr    $0xb,%r8d
    1c8b:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
    1c92:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
    1c99:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    1c9d:	c5 fa 6f b8 48 fc ff 	vmovdqu -0x3b8(%rax),%xmm7
    1ca4:	ff 
    1ca5:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    1cab:	c5 fa 7e 90 58 fc ff 	vmovq  -0x3a8(%rax),%xmm2
    1cb2:	ff 
    1cb3:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    1cb7:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
    1cbd:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
    1cc3:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    1cc8:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
    1ccc:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
    1cd2:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
    1cd8:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
    1cdd:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
    1ce2:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    1ce6:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
    1ceb:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
    1cef:	c4 41 7d d7 c0       	vpmovmskb %ymm8,%r8d
    1cf4:	45 85 c0             	test   %r8d,%r8d
    1cf7:	74 42                	je     1d3b <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x70b>
    1cf9:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
    1cfe:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
    1d03:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 1d0b <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x6db>
    1d0a:	00 
    1d0b:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 1d13 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x6e3>
    1d12:	00 
    1d13:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    1d18:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
    1d1c:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
    1d21:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    1d26:	c4 42 1d 90 0c 9b    	vpgatherdd %ymm12,(%r11,%ymm3,4),%ymm9
    1d2c:	c4 e2 35 45 df       	vpsrlvd %ymm7,%ymm9,%ymm3
    1d31:	c5 e5 db d8          	vpand  %ymm0,%ymm3,%ymm3
    1d35:	c4 e3 6d 4c d3 80    	vpblendvb %ymm8,%ymm3,%ymm2,%ymm2
    1d3b:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
    1d3f:	44 8b b8 72 fc ff ff 	mov    -0x38e(%rax),%r15d
    1d46:	44 8b a8 6c fc ff ff 	mov    -0x394(%rax),%r13d
    1d4d:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
    1d53:	44 8b b0 75 fc ff ff 	mov    -0x38b(%rax),%r14d
    1d5a:	44 8b a0 6f fc ff ff 	mov    -0x391(%rax),%r12d
    1d61:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
    1d66:	41 0f cf             	bswap  %r15d
    1d69:	41 0f cd             	bswap  %r13d
    1d6c:	41 c1 ef 0b          	shr    $0xb,%r15d
    1d70:	41 c1 ed 0b          	shr    $0xb,%r13d
    1d74:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    1d7a:	c4 62 05 36 da       	vpermd %ymm2,%ymm15,%ymm11
    1d7f:	8b 98 66 fc ff ff    	mov    -0x39a(%rax),%ebx
    1d85:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    1d8b:	44 8b 88 60 fc ff ff 	mov    -0x3a0(%rax),%r9d
    1d92:	41 0f ce             	bswap  %r14d
    1d95:	41 0f cc             	bswap  %r12d
    1d98:	41 c1 ee 0b          	shr    $0xb,%r14d
    1d9c:	41 c1 ec 0b          	shr    $0xb,%r12d
    1da0:	44 8b 90 69 fc ff ff 	mov    -0x397(%rax),%r10d
    1da7:	44 8b 80 63 fc ff ff 	mov    -0x39d(%rax),%r8d
    1dae:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    1db5:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    1dbc:	0f cb                	bswap  %ebx
    1dbe:	41 0f c9             	bswap  %r9d
    1dc1:	c1 eb 0b             	shr    $0xb,%ebx
    1dc4:	41 c1 e9 0b          	shr    $0xb,%r9d
    1dc8:	41 0f ca             	bswap  %r10d
    1dcb:	41 0f c8             	bswap  %r8d
    1dce:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    1dd3:	41 c1 e8 0b          	shr    $0xb,%r8d
    1dd7:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    1ddb:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
    1de1:	41 c1 ea 0b          	shr    $0xb,%r10d
    1de5:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
    1dec:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
    1df3:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    1df7:	c5 fa 6f b8 60 fc ff 	vmovdqu -0x3a0(%rax),%xmm7
    1dfe:	ff 
    1dff:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    1e05:	c5 fa 7e 90 70 fc ff 	vmovq  -0x390(%rax),%xmm2
    1e0c:	ff 
    1e0d:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    1e11:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
    1e17:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
    1e1d:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    1e22:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
    1e26:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
    1e2c:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
    1e32:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
    1e37:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
    1e3c:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    1e40:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
    1e45:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
    1e49:	c4 41 7d d7 c0       	vpmovmskb %ymm8,%r8d
    1e4e:	45 85 c0             	test   %r8d,%r8d
    1e51:	74 42                	je     1e95 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x865>
    1e53:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
    1e58:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
    1e5d:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 1e65 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x835>
    1e64:	00 
    1e65:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 1e6d <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x83d>
    1e6c:	00 
    1e6d:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    1e72:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
    1e76:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
    1e7b:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    1e80:	c4 42 1d 90 0c 9b    	vpgatherdd %ymm12,(%r11,%ymm3,4),%ymm9
    1e86:	c4 62 35 45 cf       	vpsrlvd %ymm7,%ymm9,%ymm9
    1e8b:	c5 35 db c8          	vpand  %ymm0,%ymm9,%ymm9
    1e8f:	c4 c3 6d 4c d1 80    	vpblendvb %ymm8,%ymm9,%ymm2,%ymm2
    1e95:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
    1e99:	44 8b b8 8a fc ff ff 	mov    -0x376(%rax),%r15d
    1ea0:	44 8b a8 84 fc ff ff 	mov    -0x37c(%rax),%r13d
    1ea7:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
    1ead:	44 8b b0 8d fc ff ff 	mov    -0x373(%rax),%r14d
    1eb4:	44 8b a0 87 fc ff ff 	mov    -0x379(%rax),%r12d
    1ebb:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
    1ec0:	41 0f cf             	bswap  %r15d
    1ec3:	41 0f cd             	bswap  %r13d
    1ec6:	41 c1 ef 0b          	shr    $0xb,%r15d
    1eca:	41 c1 ed 0b          	shr    $0xb,%r13d
    1ece:	c4 e2 05 36 fa       	vpermd %ymm2,%ymm15,%ymm7
    1ed3:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    1ed9:	8b 98 7e fc ff ff    	mov    -0x382(%rax),%ebx
    1edf:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    1ee5:	44 8b 88 78 fc ff ff 	mov    -0x388(%rax),%r9d
    1eec:	41 0f ce             	bswap  %r14d
    1eef:	41 0f cc             	bswap  %r12d
    1ef2:	41 c1 ee 0b          	shr    $0xb,%r14d
    1ef6:	41 c1 ec 0b          	shr    $0xb,%r12d
    1efa:	44 8b 90 81 fc ff ff 	mov    -0x37f(%rax),%r10d
    1f01:	44 8b 80 7b fc ff ff 	mov    -0x385(%rax),%r8d
    1f08:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    1f0f:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    1f16:	0f cb                	bswap  %ebx
    1f18:	41 0f c9             	bswap  %r9d
    1f1b:	c1 eb 0b             	shr    $0xb,%ebx
    1f1e:	41 c1 e9 0b          	shr    $0xb,%r9d
    1f22:	c5 fd 7f 7c 24 a8    	vmovdqa %ymm7,-0x58(%rsp)
    1f28:	41 0f ca             	bswap  %r10d
    1f2b:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    1f2f:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    1f34:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
    1f3a:	41 c1 ea 0b          	shr    $0xb,%r10d
    1f3e:	41 0f c8             	bswap  %r8d
    1f41:	41 c1 e8 0b          	shr    $0xb,%r8d
    1f45:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
    1f4c:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
    1f53:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    1f57:	c5 fa 6f b8 78 fc ff 	vmovdqu -0x388(%rax),%xmm7
    1f5e:	ff 
    1f5f:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    1f65:	c5 fa 7e 90 88 fc ff 	vmovq  -0x378(%rax),%xmm2
    1f6c:	ff 
    1f6d:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    1f71:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
    1f77:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
    1f7d:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    1f82:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
    1f86:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
    1f8c:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
    1f92:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
    1f97:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
    1f9c:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    1fa0:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
    1fa5:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
    1fa9:	c4 41 7d d7 c0       	vpmovmskb %ymm8,%r8d
    1fae:	45 85 c0             	test   %r8d,%r8d
    1fb1:	74 42                	je     1ff5 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x9c5>
    1fb3:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
    1fb8:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
    1fbd:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 1fc5 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x995>
    1fc4:	00 
    1fc5:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 1fcd <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x99d>
    1fcc:	00 
    1fcd:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    1fd2:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
    1fd6:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
    1fdb:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    1fe0:	c4 42 1d 90 0c 9b    	vpgatherdd %ymm12,(%r11,%ymm3,4),%ymm9
    1fe6:	c4 62 35 45 cf       	vpsrlvd %ymm7,%ymm9,%ymm9
    1feb:	c5 35 db c8          	vpand  %ymm0,%ymm9,%ymm9
    1fef:	c4 c3 6d 4c d1 80    	vpblendvb %ymm8,%ymm9,%ymm2,%ymm2
    1ff5:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
    1ff9:	44 8b b8 a2 fc ff ff 	mov    -0x35e(%rax),%r15d
    2000:	44 8b a8 9c fc ff ff 	mov    -0x364(%rax),%r13d
    2007:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
    200d:	44 8b b0 a5 fc ff ff 	mov    -0x35b(%rax),%r14d
    2014:	44 8b a0 9f fc ff ff 	mov    -0x361(%rax),%r12d
    201b:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
    2020:	41 0f cf             	bswap  %r15d
    2023:	41 0f cd             	bswap  %r13d
    2026:	41 c1 ef 0b          	shr    $0xb,%r15d
    202a:	41 c1 ed 0b          	shr    $0xb,%r13d
    202e:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    2034:	c4 62 05 36 e2       	vpermd %ymm2,%ymm15,%ymm12
    2039:	8b 98 96 fc ff ff    	mov    -0x36a(%rax),%ebx
    203f:	c4 a1 79 6e 14 af    	vmovd  (%rdi,%r13,4),%xmm2
    2045:	44 8b 88 90 fc ff ff 	mov    -0x370(%rax),%r9d
    204c:	41 0f ce             	bswap  %r14d
    204f:	41 0f cc             	bswap  %r12d
    2052:	41 c1 ee 0b          	shr    $0xb,%r14d
    2056:	41 c1 ec 0b          	shr    $0xb,%r12d
    205a:	44 8b 90 99 fc ff ff 	mov    -0x367(%rax),%r10d
    2061:	44 8b 80 93 fc ff ff 	mov    -0x36d(%rax),%r8d
    2068:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    206f:	c4 a3 69 22 14 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm2,%xmm2
    2076:	0f cb                	bswap  %ebx
    2078:	41 0f c9             	bswap  %r9d
    207b:	c1 eb 0b             	shr    $0xb,%ebx
    207e:	41 c1 e9 0b          	shr    $0xb,%r9d
    2082:	41 0f ca             	bswap  %r10d
    2085:	41 0f c8             	bswap  %r8d
    2088:	c5 f9 6e 3c 9f       	vmovd  (%rdi,%rbx,4),%xmm7
    208d:	41 c1 e8 0b          	shr    $0xb,%r8d
    2091:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    2095:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
    209b:	41 c1 ea 0b          	shr    $0xb,%r10d
    209f:	c4 a3 41 22 3c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm7,%xmm7
    20a6:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
    20ad:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    20b1:	c5 fa 6f b8 90 fc ff 	vmovdqu -0x370(%rax),%xmm7
    20b8:	ff 
    20b9:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    20bf:	c5 fa 7e 90 a0 fc ff 	vmovq  -0x360(%rax),%xmm2
    20c6:	ff 
    20c7:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    20cb:	c4 e3 69 0f d7 0c    	vpalignr $0xc,%xmm7,%xmm2,%xmm2
    20d1:	c4 e3 45 38 fa 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm7
    20d7:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    20dc:	c5 75 db cf          	vpand  %ymm7,%ymm1,%ymm9
    20e0:	c4 c1 6d 72 f1 01    	vpslld $0x1,%ymm9,%ymm2
    20e6:	c5 ed fe 54 24 08    	vpaddd 0x8(%rsp),%ymm2,%ymm2
    20ec:	c4 c1 6d fe d1       	vpaddd %ymm9,%ymm2,%ymm2
    20f1:	c4 e2 65 45 d2       	vpsrlvd %ymm2,%ymm3,%ymm2
    20f6:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    20fa:	c4 c1 6d fe d0       	vpaddd %ymm8,%ymm2,%ymm2
    20ff:	c5 3d 76 c0          	vpcmpeqd %ymm0,%ymm8,%ymm8
    2103:	c4 41 7d d7 c0       	vpmovmskb %ymm8,%r8d
    2108:	45 85 c0             	test   %r8d,%r8d
    210b:	74 42                	je     214f <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb1f>
    210d:	c5 b5 72 d7 02       	vpsrld $0x2,%ymm7,%ymm9
    2112:	c5 e5 72 d3 08       	vpsrld $0x8,%ymm3,%ymm3
    2117:	c5 c5 db 3d 00 00 00 	vpand  0x0(%rip),%ymm7,%ymm7        # 211f <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaef>
    211e:	00 
    211f:	c5 35 db 0d 00 00 00 	vpand  0x0(%rip),%ymm9,%ymm9        # 2127 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaf7>
    2126:	00 
    2127:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    212c:	c5 7d 6f d6          	vmovdqa %ymm6,%ymm10
    2130:	c5 c5 72 f7 03       	vpslld $0x3,%ymm7,%ymm7
    2135:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    213a:	c4 42 2d 90 0c 9b    	vpgatherdd %ymm10,(%r11,%ymm3,4),%ymm9
    2140:	c4 62 35 45 cf       	vpsrlvd %ymm7,%ymm9,%ymm9
    2145:	c5 35 db c8          	vpand  %ymm0,%ymm9,%ymm9
    2149:	c4 c3 6d 4c d1 80    	vpblendvb %ymm8,%ymm9,%ymm2,%ymm2
    214f:	c5 fd 6f fe          	vmovdqa %ymm6,%ymm7
    2153:	44 8b b8 ba fc ff ff 	mov    -0x346(%rax),%r15d
    215a:	44 8b a8 b4 fc ff ff 	mov    -0x34c(%rax),%r13d
    2161:	c4 e2 45 90 1c 92    	vpgatherdd %ymm7,(%rdx,%ymm2,4),%ymm3
    2167:	44 8b b0 bd fc ff ff 	mov    -0x343(%rax),%r14d
    216e:	44 8b a0 b7 fc ff ff 	mov    -0x349(%rax),%r12d
    2175:	c4 e2 65 00 d5       	vpshufb %ymm5,%ymm3,%ymm2
    217a:	41 0f cf             	bswap  %r15d
    217d:	41 0f cd             	bswap  %r13d
    2180:	41 c1 ef 0b          	shr    $0xb,%r15d
    2184:	c4 e2 05 36 fa       	vpermd %ymm2,%ymm15,%ymm7
    2189:	41 c1 ed 0b          	shr    $0xb,%r13d
    218d:	8b 98 ae fc ff ff    	mov    -0x352(%rax),%ebx
    2193:	44 8b 88 a8 fc ff ff 	mov    -0x358(%rax),%r9d
    219a:	c4 a1 79 6e 1c af    	vmovd  (%rdi,%r13,4),%xmm3
    21a0:	c5 fd 7f 7c 24 88    	vmovdqa %ymm7,-0x78(%rsp)
    21a6:	c4 a1 79 6e 3c bf    	vmovd  (%rdi,%r15,4),%xmm7
    21ac:	41 0f ce             	bswap  %r14d
    21af:	41 0f cc             	bswap  %r12d
    21b2:	41 c1 ee 0b          	shr    $0xb,%r14d
    21b6:	41 c1 ec 0b          	shr    $0xb,%r12d
    21ba:	44 8b 90 b1 fc ff ff 	mov    -0x34f(%rax),%r10d
    21c1:	c4 a3 41 22 3c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm7,%xmm7
    21c8:	c4 a3 61 22 1c a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm3,%xmm3
    21cf:	0f cb                	bswap  %ebx
    21d1:	41 0f c9             	bswap  %r9d
    21d4:	44 8b 80 ab fc ff ff 	mov    -0x355(%rax),%r8d
    21db:	41 c1 e9 0b          	shr    $0xb,%r9d
    21df:	c1 eb 0b             	shr    $0xb,%ebx
    21e2:	41 0f ca             	bswap  %r10d
    21e5:	c5 e1 6c df          	vpunpcklqdq %xmm7,%xmm3,%xmm3
    21e9:	c5 79 6e 04 9f       	vmovd  (%rdi,%rbx,4),%xmm8
    21ee:	c4 a1 79 6e 3c 8f    	vmovd  (%rdi,%r9,4),%xmm7
    21f4:	41 c1 ea 0b          	shr    $0xb,%r10d
    21f8:	41 0f c8             	bswap  %r8d
    21fb:	41 c1 e8 0b          	shr    $0xb,%r8d
    21ff:	c4 23 39 22 04 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm8,%xmm8
    2206:	c4 a3 41 22 3c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm7,%xmm7
    220d:	c4 c1 41 6c f8       	vpunpcklqdq %xmm8,%xmm7,%xmm7
    2212:	c5 7a 6f 80 a8 fc ff 	vmovdqu -0x358(%rax),%xmm8
    2219:	ff 
    221a:	c4 e3 45 38 fb 01    	vinserti128 $0x1,%xmm3,%ymm7,%ymm7
    2220:	c5 fa 7e 98 b8 fc ff 	vmovq  -0x348(%rax),%xmm3
    2227:	ff 
    2228:	c5 45 db c8          	vpand  %ymm0,%ymm7,%ymm9
    222c:	c4 c3 61 0f d8 0c    	vpalignr $0xc,%xmm8,%xmm3,%xmm3
    2232:	c4 63 3d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm8,%ymm8
    2238:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
    223d:	c4 41 75 db d0       	vpand  %ymm8,%ymm1,%ymm10
    2242:	c4 c1 65 72 f2 01    	vpslld $0x1,%ymm10,%ymm3
    2248:	c5 e5 fe 5c 24 08    	vpaddd 0x8(%rsp),%ymm3,%ymm3
    224e:	c4 c1 65 fe da       	vpaddd %ymm10,%ymm3,%ymm3
    2253:	c4 e2 45 45 db       	vpsrlvd %ymm3,%ymm7,%ymm3
    2258:	c5 e5 db d9          	vpand  %ymm1,%ymm3,%ymm3
    225c:	c4 c1 65 fe d9       	vpaddd %ymm9,%ymm3,%ymm3
    2261:	c5 35 76 c8          	vpcmpeqd %ymm0,%ymm9,%ymm9
    2265:	c4 41 7d d7 c1       	vpmovmskb %ymm9,%r8d
    226a:	45 85 c0             	test   %r8d,%r8d
    226d:	74 44                	je     22b3 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc83>
    226f:	c4 c1 2d 72 d0 02    	vpsrld $0x2,%ymm8,%ymm10
    2275:	c5 c5 72 d7 08       	vpsrld $0x8,%ymm7,%ymm7
    227a:	c5 3d db 05 00 00 00 	vpand  0x0(%rip),%ymm8,%ymm8        # 2282 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc52>
    2281:	00 
    2282:	c5 2d db 15 00 00 00 	vpand  0x0(%rip),%ymm10,%ymm10        # 228a <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc5a>
    2289:	00 
    228a:	c4 c1 45 db f9       	vpand  %ymm9,%ymm7,%ymm7
    228f:	c5 fd 6f d6          	vmovdqa %ymm6,%ymm2
    2293:	c4 c1 3d 72 f0 03    	vpslld $0x3,%ymm8,%ymm8
    2299:	c4 c1 45 fe fa       	vpaddd %ymm10,%ymm7,%ymm7
    229e:	c4 42 6d 90 14 bb    	vpgatherdd %ymm2,(%r11,%ymm7,4),%ymm10
    22a4:	c4 42 2d 45 d0       	vpsrlvd %ymm8,%ymm10,%ymm10
    22a9:	c5 2d db d0          	vpand  %ymm0,%ymm10,%ymm10
    22ad:	c4 c3 65 4c da 90    	vpblendvb %ymm9,%ymm10,%ymm3,%ymm3
    22b3:	c5 7d 6f d6          	vmovdqa %ymm6,%ymm10
    22b7:	c4 43 7d 39 e9 01    	vextracti128 $0x1,%ymm13,%xmm9
    22bd:	c4 43 7d 39 f0 01    	vextracti128 $0x1,%ymm14,%xmm8
    22c3:	48 81 c1 c0 00 00 00 	add    $0xc0,%rcx
    22ca:	c4 e2 2d 90 3c 9a    	vpgatherdd %ymm10,(%rdx,%ymm3,4),%ymm7
    22d0:	c4 41 79 6f d5       	vmovdqa %xmm13,%xmm10
    22d5:	c4 41 79 6f ee       	vmovdqa %xmm14,%xmm13
    22da:	48 05 c0 00 00 00    	add    $0xc0,%rax
    22e0:	c4 e2 45 00 dd       	vpshufb %ymm5,%ymm7,%ymm3
    22e5:	c5 fd 6f 7c 24 c8    	vmovdqa -0x38(%rsp),%ymm7
    22eb:	c4 41 79 6f f3       	vmovdqa %xmm11,%xmm14
    22f0:	c4 43 7d 39 db 01    	vextracti128 $0x1,%ymm11,%xmm11
    22f6:	c4 43 39 0f c5 08    	vpalignr $0x8,%xmm13,%xmm8,%xmm8
    22fc:	c4 41 31 6c cd       	vpunpcklqdq %xmm13,%xmm9,%xmm9
    2301:	c4 e2 05 36 db       	vpermd %ymm3,%ymm15,%ymm3
    2306:	c5 f9 7f 7c 24 c8    	vmovdqa %xmm7,-0x38(%rsp)
    230c:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    2312:	c4 43 21 0f de 08    	vpalignr $0x8,%xmm14,%xmm11,%xmm11
    2318:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
    231e:	c4 63 3d 38 44 24 c8 	vinserti128 $0x1,-0x38(%rsp),%ymm8,%ymm8
    2325:	01 
    2326:	c4 c1 41 6c fe       	vpunpcklqdq %xmm14,%xmm7,%xmm7
    232b:	c5 7d e7 91 40 ff ff 	vmovntdq %ymm10,-0xc0(%rcx)
    2332:	ff 
    2333:	c5 79 6f d3          	vmovdqa %xmm3,%xmm10
    2337:	c4 c3 45 38 fb 01    	vinserti128 $0x1,%xmm11,%ymm7,%ymm7
    233d:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    2343:	c4 41 79 6f dc       	vmovdqa %xmm12,%xmm11
    2348:	c5 7d e7 81 60 ff ff 	vmovntdq %ymm8,-0xa0(%rcx)
    234f:	ff 
    2350:	c5 fd e7 79 80       	vmovntdq %ymm7,-0x80(%rcx)
    2355:	c5 fd 6f 7c 24 a8    	vmovdqa -0x58(%rsp),%ymm7
    235b:	c5 fd 6f 54 24 88    	vmovdqa -0x78(%rsp),%ymm2
    2361:	c4 c3 61 0f da 08    	vpalignr $0x8,%xmm10,%xmm3,%xmm3
    2367:	4c 8d 8e 88 00 00 00 	lea    0x88(%rsi),%r9
    236e:	4c 8d 46 40          	lea    0x40(%rsi),%r8
    2372:	c5 79 6f c7          	vmovdqa %xmm7,%xmm8
    2376:	c4 c3 7d 39 f9 01    	vextracti128 $0x1,%ymm7,%xmm9
    237c:	c4 63 7d 39 e7 01    	vextracti128 $0x1,%ymm12,%xmm7
    2382:	c5 79 6f e2          	vmovdqa %xmm2,%xmm12
    2386:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    238c:	c4 41 31 6c cb       	vpunpcklqdq %xmm11,%xmm9,%xmm9
    2391:	c4 c3 41 0f fb 08    	vpalignr $0x8,%xmm11,%xmm7,%xmm7
    2397:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    239c:	c4 43 3d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm8,%ymm8
    23a2:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
    23a8:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
    23ae:	c5 7d e7 41 a0       	vmovntdq %ymm8,-0x60(%rcx)
    23b3:	c5 fd e7 79 c0       	vmovntdq %ymm7,-0x40(%rcx)
    23b8:	c5 fd e7 51 e0       	vmovntdq %ymm2,-0x20(%rcx)
    23bd:	4c 39 0c 24          	cmp    %r9,(%rsp)
    23c1:	0f 83 f1 f3 ff ff    	jae    17b8 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x188>
    23c7:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    23cc:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
    23d1:	48 8d 46 68          	lea    0x68(%rsi),%rax
    23d5:	4c 8b 7c 24 e8       	mov    -0x18(%rsp),%r15
    23da:	0f ae f8             	sfence
    23dd:	48 39 04 24          	cmp    %rax,(%rsp)
    23e1:	0f 82 1a 09 00 00    	jb     2d01 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x16d1>
    23e7:	b9 08 00 00 00       	mov    $0x8,%ecx
    23ec:	c4 41 3d 76 c0       	vpcmpeqd %ymm8,%ymm8,%ymm8
    23f1:	4f 8d 24 40          	lea    (%r8,%r8,2),%r12
    23f5:	4c 89 54 24 c8       	mov    %r10,-0x38(%rsp)
    23fa:	c5 79 6e d1          	vmovd  %ecx,%xmm10
    23fe:	4b 8d 04 22          	lea    (%r10,%r12,1),%rax
    2402:	48 89 5c 24 a8       	mov    %rbx,-0x58(%rsp)
    2407:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 240f <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xddf>
    240e:	00 
    240f:	4c 89 7c 24 88       	mov    %r15,-0x78(%rsp)
    2414:	c5 7d 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm9        # 241c <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdec>
    241b:	00 
    241c:	4d 01 fc             	add    %r15,%r12
    241f:	c4 c1 4d 72 d0 18    	vpsrld $0x18,%ymm8,%ymm6
    2425:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 242d <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdfd>
    242c:	00 
    242d:	c4 c1 45 72 d0 1d    	vpsrld $0x1d,%ymm8,%ymm7
    2433:	c4 c1 15 72 d0 1f    	vpsrld $0x1f,%ymm8,%ymm13
    2439:	c4 42 7d 58 d2       	vpbroadcastd %xmm10,%ymm10
    243e:	e9 e8 01 00 00       	jmp    262b <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xffb>
    2443:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    2448:	c5 fd 6f c8          	vmovdqa %ymm0,%ymm1
    244c:	44 8b 78 5a          	mov    0x5a(%rax),%r15d
    2450:	44 8b 68 54          	mov    0x54(%rax),%r13d
    2454:	c5 7d 7f c4          	vmovdqa %ymm8,%ymm4
    2458:	44 8b 70 5d          	mov    0x5d(%rax),%r14d
    245c:	8b 58 57             	mov    0x57(%rax),%ebx
    245f:	c4 e2 5d 90 04 8a    	vpgatherdd %ymm4,(%rdx,%ymm1,4),%ymm0
    2465:	41 0f cf             	bswap  %r15d
    2468:	41 0f cd             	bswap  %r13d
    246b:	41 c1 ef 0b          	shr    $0xb,%r15d
    246f:	41 c1 ed 0b          	shr    $0xb,%r13d
    2473:	c4 a1 79 6e 14 bf    	vmovd  (%rdi,%r15,4),%xmm2
    2479:	c4 a1 79 6e 0c af    	vmovd  (%rdi,%r13,4),%xmm1
    247f:	41 0f ce             	bswap  %r14d
    2482:	0f cb                	bswap  %ebx
    2484:	44 8b 50 4e          	mov    0x4e(%rax),%r10d
    2488:	8b 70 48             	mov    0x48(%rax),%esi
    248b:	c1 eb 0b             	shr    $0xb,%ebx
    248e:	41 c1 ee 0b          	shr    $0xb,%r14d
    2492:	c4 a3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm2,%xmm2
    2499:	c4 e3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm1,%xmm1
    24a0:	44 8b 48 51          	mov    0x51(%rax),%r9d
    24a4:	8b 48 4b             	mov    0x4b(%rax),%ecx
    24a7:	41 0f ca             	bswap  %r10d
    24aa:	0f ce                	bswap  %esi
    24ac:	41 c1 ea 0b          	shr    $0xb,%r10d
    24b0:	c1 ee 0b             	shr    $0xb,%esi
    24b3:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    24b7:	c4 a1 79 6e 1c 97    	vmovd  (%rdi,%r10,4),%xmm3
    24bd:	c5 f9 6e 14 b7       	vmovd  (%rdi,%rsi,4),%xmm2
    24c2:	41 0f c9             	bswap  %r9d
    24c5:	0f c9                	bswap  %ecx
    24c7:	41 c1 e9 0b          	shr    $0xb,%r9d
    24cb:	c1 e9 0b             	shr    $0xb,%ecx
    24ce:	c4 a3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm3,%xmm3
    24d5:	c4 e3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm2,%xmm2
    24dc:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    24e0:	c5 fa 6f 58 48       	vmovdqu 0x48(%rax),%xmm3
    24e5:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
    24eb:	c5 fa 7e 48 58       	vmovq  0x58(%rax),%xmm1
    24f0:	c5 ed db e6          	vpand  %ymm6,%ymm2,%ymm4
    24f4:	c4 e3 71 0f cb 0c    	vpalignr $0xc,%xmm3,%xmm1,%xmm1
    24fa:	c4 e3 65 38 d9 01    	vinserti128 $0x1,%xmm1,%ymm3,%ymm3
    2500:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
    2505:	c5 45 db db          	vpand  %ymm3,%ymm7,%ymm11
    2509:	c4 c1 75 72 f3 01    	vpslld $0x1,%ymm11,%ymm1
    250f:	c4 c1 75 fe ca       	vpaddd %ymm10,%ymm1,%ymm1
    2514:	c4 c1 75 fe cb       	vpaddd %ymm11,%ymm1,%ymm1
    2519:	c4 e2 6d 45 c9       	vpsrlvd %ymm1,%ymm2,%ymm1
    251e:	c5 f5 db cf          	vpand  %ymm7,%ymm1,%ymm1
    2522:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
    2526:	c5 dd 76 e6          	vpcmpeqd %ymm6,%ymm4,%ymm4
    252a:	c5 fd d7 cc          	vpmovmskb %ymm4,%ecx
    252e:	85 c9                	test   %ecx,%ecx
    2530:	74 3f                	je     2571 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf41>
    2532:	c5 a5 72 d3 02       	vpsrld $0x2,%ymm3,%ymm11
    2537:	c5 ed 72 d2 08       	vpsrld $0x8,%ymm2,%ymm2
    253c:	c5 e5 db 1d 00 00 00 	vpand  0x0(%rip),%ymm3,%ymm3        # 2544 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf14>
    2543:	00 
    2544:	c4 41 25 db dd       	vpand  %ymm13,%ymm11,%ymm11
    2549:	c5 ed db d4          	vpand  %ymm4,%ymm2,%ymm2
    254d:	c4 41 7d 6f e0       	vmovdqa %ymm8,%ymm12
    2552:	c4 c1 6d fe d3       	vpaddd %ymm11,%ymm2,%ymm2
    2557:	c5 e5 72 f3 03       	vpslld $0x3,%ymm3,%ymm3
    255c:	c4 42 1d 90 1c 93    	vpgatherdd %ymm12,(%r11,%ymm2,4),%ymm11
    2562:	c4 62 25 45 db       	vpsrlvd %ymm3,%ymm11,%ymm11
    2567:	c5 25 db de          	vpand  %ymm6,%ymm11,%ymm11
    256b:	c4 c3 75 4c cb 40    	vpblendvb %ymm4,%ymm11,%ymm1,%ymm1
    2571:	c5 7d 7f c4          	vmovdqa %ymm8,%ymm4
    2575:	c4 c2 0d 00 d9       	vpshufb %ymm9,%ymm14,%ymm3
    257a:	c4 c2 7d 00 c1       	vpshufb %ymm9,%ymm0,%ymm0
    257f:	48 83 c0 60          	add    $0x60,%rax
    2583:	c4 e2 5d 90 14 8a    	vpgatherdd %ymm4,(%rdx,%ymm1,4),%ymm2
    2589:	c5 fd 6f 64 24 08    	vmovdqa 0x8(%rsp),%ymm4
    258f:	c4 e2 05 36 c0       	vpermd %ymm0,%ymm15,%ymm0
    2594:	c4 e2 05 36 db       	vpermd %ymm3,%ymm15,%ymm3
    2599:	c4 c2 6d 00 d1       	vpshufb %ymm9,%ymm2,%ymm2
    259e:	c5 79 6f e0          	vmovdqa %xmm0,%xmm12
    25a2:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    25a8:	49 83 c4 60          	add    $0x60,%r12
    25ac:	c4 c2 5d 00 c9       	vpshufb %ymm9,%ymm4,%ymm1
    25b1:	c4 e2 05 36 d2       	vpermd %ymm2,%ymm15,%ymm2
    25b6:	c5 f9 6f e3          	vmovdqa %xmm3,%xmm4
    25ba:	c4 e2 05 36 c9       	vpermd %ymm1,%ymm15,%ymm1
    25bf:	c5 79 6f f2          	vmovdqa %xmm2,%xmm14
    25c3:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    25c9:	c5 79 6f d9          	vmovdqa %xmm1,%xmm11
    25cd:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    25d3:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    25d9:	c4 c1 61 6c db       	vpunpcklqdq %xmm11,%xmm3,%xmm3
    25de:	c4 c3 71 0f cb 08    	vpalignr $0x8,%xmm11,%xmm1,%xmm1
    25e4:	c4 c1 79 6c c6       	vpunpcklqdq %xmm14,%xmm0,%xmm0
    25e9:	c4 c3 69 0f d6 08    	vpalignr $0x8,%xmm14,%xmm2,%xmm2
    25ef:	c4 e3 5d 38 e3 01    	vinserti128 $0x1,%xmm3,%ymm4,%ymm4
    25f5:	c4 c3 75 38 cc 01    	vinserti128 $0x1,%xmm12,%ymm1,%ymm1
    25fb:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    2601:	49 8d 48 20          	lea    0x20(%r8),%rcx
    2605:	49 83 c0 48          	add    $0x48,%r8
    2609:	c4 c1 7e 7f 64 24 a0 	vmovdqu %ymm4,-0x60(%r12)
    2610:	c4 c1 7e 7f 4c 24 c0 	vmovdqu %ymm1,-0x40(%r12)
    2617:	c4 c1 7e 7f 44 24 e0 	vmovdqu %ymm0,-0x20(%r12)
    261e:	4c 39 04 24          	cmp    %r8,(%rsp)
    2622:	0f 82 70 03 00 00    	jb     2998 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1368>
    2628:	49 89 c8             	mov    %rcx,%r8
    262b:	44 8b 78 12          	mov    0x12(%rax),%r15d
    262f:	44 8b 68 0c          	mov    0xc(%rax),%r13d
    2633:	44 8b 70 15          	mov    0x15(%rax),%r14d
    2637:	8b 58 0f             	mov    0xf(%rax),%ebx
    263a:	41 0f cf             	bswap  %r15d
    263d:	41 0f cd             	bswap  %r13d
    2640:	41 c1 ef 0b          	shr    $0xb,%r15d
    2644:	41 c1 ed 0b          	shr    $0xb,%r13d
    2648:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    264e:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    2654:	41 0f ce             	bswap  %r14d
    2657:	0f cb                	bswap  %ebx
    2659:	44 8b 50 06          	mov    0x6(%rax),%r10d
    265d:	8b 30                	mov    (%rax),%esi
    265f:	c1 eb 0b             	shr    $0xb,%ebx
    2662:	41 c1 ee 0b          	shr    $0xb,%r14d
    2666:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    266d:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
    2674:	44 8b 48 09          	mov    0x9(%rax),%r9d
    2678:	8b 48 03             	mov    0x3(%rax),%ecx
    267b:	41 0f ca             	bswap  %r10d
    267e:	0f ce                	bswap  %esi
    2680:	41 c1 ea 0b          	shr    $0xb,%r10d
    2684:	c1 ee 0b             	shr    $0xb,%esi
    2687:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    268b:	c4 a1 79 6e 14 97    	vmovd  (%rdi,%r10,4),%xmm2
    2691:	c5 f9 6e 0c b7       	vmovd  (%rdi,%rsi,4),%xmm1
    2696:	41 0f c9             	bswap  %r9d
    2699:	0f c9                	bswap  %ecx
    269b:	41 c1 e9 0b          	shr    $0xb,%r9d
    269f:	c1 e9 0b             	shr    $0xb,%ecx
    26a2:	c4 a3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm2,%xmm2
    26a9:	c4 e3 71 22 0c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm1,%xmm1
    26b0:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    26b4:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
    26b8:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    26be:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    26c3:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
    26c7:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    26cd:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    26d3:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
    26d8:	c5 c5 db e2          	vpand  %ymm2,%ymm7,%ymm4
    26dc:	c5 fd 72 f4 01       	vpslld $0x1,%ymm4,%ymm0
    26e1:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
    26e6:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    26ea:	c4 e2 75 45 c0       	vpsrlvd %ymm0,%ymm1,%ymm0
    26ef:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
    26f3:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
    26f7:	c5 e5 76 de          	vpcmpeqd %ymm6,%ymm3,%ymm3
    26fb:	c5 fd d7 cb          	vpmovmskb %ymm3,%ecx
    26ff:	85 c9                	test   %ecx,%ecx
    2701:	74 3e                	je     2741 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1111>
    2703:	c5 dd 72 d2 02       	vpsrld $0x2,%ymm2,%ymm4
    2708:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
    270d:	c5 ed db 15 00 00 00 	vpand  0x0(%rip),%ymm2,%ymm2        # 2715 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10e5>
    2714:	00 
    2715:	c4 c1 5d db e5       	vpand  %ymm13,%ymm4,%ymm4
    271a:	c5 f5 db cb          	vpand  %ymm3,%ymm1,%ymm1
    271e:	c4 41 7d 6f f0       	vmovdqa %ymm8,%ymm14
    2723:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
    2727:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
    272c:	c4 c2 0d 90 24 8b    	vpgatherdd %ymm14,(%r11,%ymm1,4),%ymm4
    2732:	c4 e2 5d 45 ca       	vpsrlvd %ymm2,%ymm4,%ymm1
    2737:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
    273b:	c4 e3 7d 4c c1 30    	vpblendvb %ymm3,%ymm1,%ymm0,%ymm0
    2741:	44 8b 78 2a          	mov    0x2a(%rax),%r15d
    2745:	44 8b 68 24          	mov    0x24(%rax),%r13d
    2749:	c5 7d 7f c4          	vmovdqa %ymm8,%ymm4
    274d:	44 8b 70 2d          	mov    0x2d(%rax),%r14d
    2751:	8b 58 27             	mov    0x27(%rax),%ebx
    2754:	c4 62 5d 90 34 82    	vpgatherdd %ymm4,(%rdx,%ymm0,4),%ymm14
    275a:	41 0f cf             	bswap  %r15d
    275d:	41 0f cd             	bswap  %r13d
    2760:	41 c1 ef 0b          	shr    $0xb,%r15d
    2764:	41 c1 ed 0b          	shr    $0xb,%r13d
    2768:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    276e:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    2774:	41 0f ce             	bswap  %r14d
    2777:	0f cb                	bswap  %ebx
    2779:	44 8b 50 1e          	mov    0x1e(%rax),%r10d
    277d:	8b 70 18             	mov    0x18(%rax),%esi
    2780:	c1 eb 0b             	shr    $0xb,%ebx
    2783:	41 c1 ee 0b          	shr    $0xb,%r14d
    2787:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    278e:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
    2795:	44 8b 48 21          	mov    0x21(%rax),%r9d
    2799:	8b 48 1b             	mov    0x1b(%rax),%ecx
    279c:	41 0f ca             	bswap  %r10d
    279f:	0f ce                	bswap  %esi
    27a1:	41 c1 ea 0b          	shr    $0xb,%r10d
    27a5:	c1 ee 0b             	shr    $0xb,%esi
    27a8:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    27ac:	c4 a1 79 6e 14 97    	vmovd  (%rdi,%r10,4),%xmm2
    27b2:	c5 f9 6e 0c b7       	vmovd  (%rdi,%rsi,4),%xmm1
    27b7:	41 0f c9             	bswap  %r9d
    27ba:	0f c9                	bswap  %ecx
    27bc:	41 c1 e9 0b          	shr    $0xb,%r9d
    27c0:	c1 e9 0b             	shr    $0xb,%ecx
    27c3:	c4 a3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm2,%xmm2
    27ca:	c4 e3 71 22 0c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm1,%xmm1
    27d1:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    27d5:	c5 fa 6f 50 18       	vmovdqu 0x18(%rax),%xmm2
    27da:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    27e0:	c5 fa 7e 40 28       	vmovq  0x28(%rax),%xmm0
    27e5:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
    27e9:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    27ef:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    27f5:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
    27fa:	c5 c5 db e2          	vpand  %ymm2,%ymm7,%ymm4
    27fe:	c5 fd 72 f4 01       	vpslld $0x1,%ymm4,%ymm0
    2803:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
    2808:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    280c:	c4 e2 75 45 c0       	vpsrlvd %ymm0,%ymm1,%ymm0
    2811:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
    2815:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
    2819:	c5 e5 76 de          	vpcmpeqd %ymm6,%ymm3,%ymm3
    281d:	c5 fd d7 cb          	vpmovmskb %ymm3,%ecx
    2821:	85 c9                	test   %ecx,%ecx
    2823:	74 3e                	je     2863 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1233>
    2825:	c5 dd 72 d2 02       	vpsrld $0x2,%ymm2,%ymm4
    282a:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
    282f:	c5 ed db 15 00 00 00 	vpand  0x0(%rip),%ymm2,%ymm2        # 2837 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1207>
    2836:	00 
    2837:	c4 c1 5d db e5       	vpand  %ymm13,%ymm4,%ymm4
    283c:	c5 f5 db cb          	vpand  %ymm3,%ymm1,%ymm1
    2840:	c4 41 7d 6f d8       	vmovdqa %ymm8,%ymm11
    2845:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
    2849:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
    284e:	c4 c2 25 90 24 8b    	vpgatherdd %ymm11,(%r11,%ymm1,4),%ymm4
    2854:	c4 e2 5d 45 e2       	vpsrlvd %ymm2,%ymm4,%ymm4
    2859:	c5 dd db e6          	vpand  %ymm6,%ymm4,%ymm4
    285d:	c4 e3 7d 4c c4 30    	vpblendvb %ymm3,%ymm4,%ymm0,%ymm0
    2863:	44 8b 78 42          	mov    0x42(%rax),%r15d
    2867:	44 8b 68 3c          	mov    0x3c(%rax),%r13d
    286b:	c5 7d 7f c1          	vmovdqa %ymm8,%ymm1
    286f:	44 8b 70 45          	mov    0x45(%rax),%r14d
    2873:	8b 58 3f             	mov    0x3f(%rax),%ebx
    2876:	c4 e2 75 90 24 82    	vpgatherdd %ymm1,(%rdx,%ymm0,4),%ymm4
    287c:	41 0f cf             	bswap  %r15d
    287f:	41 0f cd             	bswap  %r13d
    2882:	41 c1 ef 0b          	shr    $0xb,%r15d
    2886:	41 c1 ed 0b          	shr    $0xb,%r13d
    288a:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    2890:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    2896:	41 0f ce             	bswap  %r14d
    2899:	0f cb                	bswap  %ebx
    289b:	44 8b 50 36          	mov    0x36(%rax),%r10d
    289f:	8b 70 30             	mov    0x30(%rax),%esi
    28a2:	c1 eb 0b             	shr    $0xb,%ebx
    28a5:	41 c1 ee 0b          	shr    $0xb,%r14d
    28a9:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    28b0:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
    28b7:	c5 fd 7f 64 24 08    	vmovdqa %ymm4,0x8(%rsp)
    28bd:	44 8b 48 39          	mov    0x39(%rax),%r9d
    28c1:	8b 48 33             	mov    0x33(%rax),%ecx
    28c4:	41 0f ca             	bswap  %r10d
    28c7:	0f ce                	bswap  %esi
    28c9:	41 c1 ea 0b          	shr    $0xb,%r10d
    28cd:	c1 ee 0b             	shr    $0xb,%esi
    28d0:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    28d4:	c4 a1 79 6e 14 97    	vmovd  (%rdi,%r10,4),%xmm2
    28da:	c5 f9 6e 0c b7       	vmovd  (%rdi,%rsi,4),%xmm1
    28df:	41 0f c9             	bswap  %r9d
    28e2:	0f c9                	bswap  %ecx
    28e4:	41 c1 e9 0b          	shr    $0xb,%r9d
    28e8:	c1 e9 0b             	shr    $0xb,%ecx
    28eb:	c4 a3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%r9,4),%xmm2,%xmm2
    28f2:	c4 e3 71 22 0c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm1,%xmm1
    28f9:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    28fd:	c5 fa 6f 50 30       	vmovdqu 0x30(%rax),%xmm2
    2902:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    2908:	c5 fa 7e 40 40       	vmovq  0x40(%rax),%xmm0
    290d:	c5 f5 db de          	vpand  %ymm6,%ymm1,%ymm3
    2911:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    2917:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    291d:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
    2922:	c5 c5 db e2          	vpand  %ymm2,%ymm7,%ymm4
    2926:	c5 fd 72 f4 01       	vpslld $0x1,%ymm4,%ymm0
    292b:	c4 c1 7d fe c2       	vpaddd %ymm10,%ymm0,%ymm0
    2930:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    2934:	c4 e2 75 45 c0       	vpsrlvd %ymm0,%ymm1,%ymm0
    2939:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
    293d:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
    2941:	c5 e5 76 de          	vpcmpeqd %ymm6,%ymm3,%ymm3
    2945:	c5 fd d7 cb          	vpmovmskb %ymm3,%ecx
    2949:	85 c9                	test   %ecx,%ecx
    294b:	0f 84 f7 fa ff ff    	je     2448 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe18>
    2951:	c5 dd 72 d2 02       	vpsrld $0x2,%ymm2,%ymm4
    2956:	c5 f5 72 d1 08       	vpsrld $0x8,%ymm1,%ymm1
    295b:	c5 ed db 15 00 00 00 	vpand  0x0(%rip),%ymm2,%ymm2        # 2963 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1333>
    2962:	00 
    2963:	c4 c1 5d db e5       	vpand  %ymm13,%ymm4,%ymm4
    2968:	c5 f5 db cb          	vpand  %ymm3,%ymm1,%ymm1
    296c:	c4 41 7d 6f d8       	vmovdqa %ymm8,%ymm11
    2971:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
    2975:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
    297a:	c4 c2 25 90 24 8b    	vpgatherdd %ymm11,(%r11,%ymm1,4),%ymm4
    2980:	c4 e2 5d 45 e2       	vpsrlvd %ymm2,%ymm4,%ymm4
    2985:	c5 dd db e6          	vpand  %ymm6,%ymm4,%ymm4
    2989:	c4 e3 7d 4c cc 30    	vpblendvb %ymm3,%ymm4,%ymm0,%ymm1
    298f:	e9 b8 fa ff ff       	jmp    244c <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe1c>
    2994:	0f 1f 40 00          	nopl   0x0(%rax)
    2998:	4c 8b 54 24 c8       	mov    -0x38(%rsp),%r10
    299d:	48 8b 5c 24 a8       	mov    -0x58(%rsp),%rbx
    29a2:	4c 8b 7c 24 88       	mov    -0x78(%rsp),%r15
    29a7:	4c 8d 71 08          	lea    0x8(%rcx),%r14
    29ab:	4c 39 34 24          	cmp    %r14,(%rsp)
    29af:	0f 82 44 03 00 00    	jb     2cf9 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x16c9>
    29b5:	4c 8d 2c 49          	lea    (%rcx,%rcx,2),%r13
    29b9:	b9 08 00 00 00       	mov    $0x8,%ecx
    29be:	c5 e5 76 db          	vpcmpeqd %ymm3,%ymm3,%ymm3
    29c2:	4c 89 54 24 c8       	mov    %r10,-0x38(%rsp)
    29c7:	c5 f9 6e e1          	vmovd  %ecx,%xmm4
    29cb:	4b 8d 04 2a          	lea    (%r10,%r13,1),%rax
    29cf:	48 89 5c 24 a8       	mov    %rbx,-0x58(%rsp)
    29d4:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 29dc <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x13ac>
    29db:	00 
    29dc:	4c 89 5c 24 08       	mov    %r11,0x8(%rsp)
    29e1:	c5 7d 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm8        # 29e9 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x13b9>
    29e8:	00 
    29e9:	4d 01 fd             	add    %r15,%r13
    29ec:	c5 f5 72 d3 18       	vpsrld $0x18,%ymm3,%ymm1
    29f1:	4c 89 7c 24 88       	mov    %r15,-0x78(%rsp)
    29f6:	c5 ed 72 d3 1d       	vpsrld $0x1d,%ymm3,%ymm2
    29fb:	c5 cd 72 d3 1f       	vpsrld $0x1f,%ymm3,%ymm6
    2a00:	c4 e2 7d 58 e4       	vpbroadcastd %xmm4,%ymm4
    2a05:	c5 d5 72 d3 1e       	vpsrld $0x1e,%ymm3,%ymm5
    2a0a:	eb 55                	jmp    2a61 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1431>
    2a0c:	0f 1f 40 00          	nopl   0x0(%rax)
    2a10:	c5 7d 6f c8          	vmovdqa %ymm0,%ymm9
    2a14:	c5 7d 6f eb          	vmovdqa %ymm3,%ymm13
    2a18:	49 8d 4e 08          	lea    0x8(%r14),%rcx
    2a1c:	48 83 c0 18          	add    $0x18,%rax
    2a20:	49 83 c5 18          	add    $0x18,%r13
    2a24:	c4 a2 15 90 04 8a    	vpgatherdd %ymm13,(%rdx,%ymm9,4),%ymm0
    2a2a:	c4 c2 7d 00 c0       	vpshufb %ymm8,%ymm0,%ymm0
    2a2f:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
    2a33:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    2a39:	c5 b1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm9
    2a3e:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    2a43:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
    2a48:	c4 c1 79 d6 45 f8    	vmovq  %xmm0,-0x8(%r13)
    2a4e:	c4 41 7a 7f 4d e8    	vmovdqu %xmm9,-0x18(%r13)
    2a54:	48 39 0c 24          	cmp    %rcx,(%rsp)
    2a58:	0f 82 d2 01 00 00    	jb     2c30 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1600>
    2a5e:	49 89 ce             	mov    %rcx,%r14
    2a61:	0f b6 30             	movzbl (%rax),%esi
    2a64:	0f b6 48 01          	movzbl 0x1(%rax),%ecx
    2a68:	44 0f b6 40 04       	movzbl 0x4(%rax),%r8d
    2a6d:	44 0f b6 48 06       	movzbl 0x6(%rax),%r9d
    2a72:	c1 e1 08             	shl    $0x8,%ecx
    2a75:	c1 e6 10             	shl    $0x10,%esi
    2a78:	44 0f b6 50 09       	movzbl 0x9(%rax),%r10d
    2a7d:	44 0f b6 58 0d       	movzbl 0xd(%rax),%r11d
    2a82:	09 ce                	or     %ecx,%esi
    2a84:	0f b6 48 02          	movzbl 0x2(%rax),%ecx
    2a88:	41 c1 e0 08          	shl    $0x8,%r8d
    2a8c:	0f b6 58 0f          	movzbl 0xf(%rax),%ebx
    2a90:	41 c1 e1 10          	shl    $0x10,%r9d
    2a94:	41 c1 e2 10          	shl    $0x10,%r10d
    2a98:	44 0f b6 60 13       	movzbl 0x13(%rax),%r12d
    2a9d:	44 0f b6 78 15       	movzbl 0x15(%rax),%r15d
    2aa2:	41 c1 e3 08          	shl    $0x8,%r11d
    2aa6:	09 ce                	or     %ecx,%esi
    2aa8:	0f b6 48 03          	movzbl 0x3(%rax),%ecx
    2aac:	c1 e3 10             	shl    $0x10,%ebx
    2aaf:	41 c1 e4 08          	shl    $0x8,%r12d
    2ab3:	c1 ee 03             	shr    $0x3,%esi
    2ab6:	c1 e1 10             	shl    $0x10,%ecx
    2ab9:	44 09 c1             	or     %r8d,%ecx
    2abc:	44 0f b6 40 05       	movzbl 0x5(%rax),%r8d
    2ac1:	44 09 c1             	or     %r8d,%ecx
    2ac4:	44 0f b6 40 07       	movzbl 0x7(%rax),%r8d
    2ac9:	c1 e9 03             	shr    $0x3,%ecx
    2acc:	41 c1 e0 08          	shl    $0x8,%r8d
    2ad0:	45 09 c1             	or     %r8d,%r9d
    2ad3:	44 0f b6 40 08       	movzbl 0x8(%rax),%r8d
    2ad8:	45 09 c1             	or     %r8d,%r9d
    2adb:	44 0f b6 40 0a       	movzbl 0xa(%rax),%r8d
    2ae0:	41 c1 e9 03          	shr    $0x3,%r9d
    2ae4:	41 c1 e0 08          	shl    $0x8,%r8d
    2ae8:	c4 21 79 6e 14 8f    	vmovd  (%rdi,%r9,4),%xmm10
    2aee:	45 09 d0             	or     %r10d,%r8d
    2af1:	44 0f b6 50 0b       	movzbl 0xb(%rax),%r10d
    2af6:	45 09 d0             	or     %r10d,%r8d
    2af9:	44 0f b6 50 0c       	movzbl 0xc(%rax),%r10d
    2afe:	41 c1 e8 03          	shr    $0x3,%r8d
    2b02:	41 c1 e2 10          	shl    $0x10,%r10d
    2b06:	c4 23 29 22 14 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm10,%xmm10
    2b0d:	45 09 d3             	or     %r10d,%r11d
    2b10:	44 0f b6 50 0e       	movzbl 0xe(%rax),%r10d
    2b15:	45 09 d3             	or     %r10d,%r11d
    2b18:	44 0f b6 50 10       	movzbl 0x10(%rax),%r10d
    2b1d:	41 c1 eb 03          	shr    $0x3,%r11d
    2b21:	41 c1 e2 08          	shl    $0x8,%r10d
    2b25:	c4 a1 79 6e 04 9f    	vmovd  (%rdi,%r11,4),%xmm0
    2b2b:	41 09 da             	or     %ebx,%r10d
    2b2e:	0f b6 58 11          	movzbl 0x11(%rax),%ebx
    2b32:	41 09 da             	or     %ebx,%r10d
    2b35:	0f b6 58 12          	movzbl 0x12(%rax),%ebx
    2b39:	41 c1 ea 03          	shr    $0x3,%r10d
    2b3d:	c1 e3 10             	shl    $0x10,%ebx
    2b40:	c4 a3 79 22 04 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm0,%xmm0
    2b47:	41 09 dc             	or     %ebx,%r12d
    2b4a:	0f b6 58 14          	movzbl 0x14(%rax),%ebx
    2b4e:	41 c1 e7 10          	shl    $0x10,%r15d
    2b52:	41 09 dc             	or     %ebx,%r12d
    2b55:	0f b6 58 16          	movzbl 0x16(%rax),%ebx
    2b59:	41 c1 ec 03          	shr    $0x3,%r12d
    2b5d:	c1 e3 08             	shl    $0x8,%ebx
    2b60:	c4 21 79 6e 0c a7    	vmovd  (%rdi,%r12,4),%xmm9
    2b66:	44 09 fb             	or     %r15d,%ebx
    2b69:	44 0f b6 78 17       	movzbl 0x17(%rax),%r15d
    2b6e:	44 09 fb             	or     %r15d,%ebx
    2b71:	c1 eb 03             	shr    $0x3,%ebx
    2b74:	c4 63 31 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm9,%xmm9
    2b7b:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    2b80:	c5 79 6e 0c b7       	vmovd  (%rdi,%rsi,4),%xmm9
    2b85:	c4 63 31 22 0c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm9,%xmm9
    2b8c:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    2b91:	c5 7a 6f 10          	vmovdqu (%rax),%xmm10
    2b95:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    2b9b:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    2ba0:	c5 35 db d9          	vpand  %ymm1,%ymm9,%ymm11
    2ba4:	c4 c3 79 0f c2 0c    	vpalignr $0xc,%xmm10,%xmm0,%xmm0
    2baa:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
    2bb0:	c4 62 2d 00 d7       	vpshufb %ymm7,%ymm10,%ymm10
    2bb5:	c4 41 6d db e2       	vpand  %ymm10,%ymm2,%ymm12
    2bba:	c4 c1 7d 72 f4 01    	vpslld $0x1,%ymm12,%ymm0
    2bc0:	c5 fd fe c4          	vpaddd %ymm4,%ymm0,%ymm0
    2bc4:	c4 c1 7d fe c4       	vpaddd %ymm12,%ymm0,%ymm0
    2bc9:	c4 e2 35 45 c0       	vpsrlvd %ymm0,%ymm9,%ymm0
    2bce:	c5 fd db c2          	vpand  %ymm2,%ymm0,%ymm0
    2bd2:	c4 c1 7d fe c3       	vpaddd %ymm11,%ymm0,%ymm0
    2bd7:	c5 25 76 d9          	vpcmpeqd %ymm1,%ymm11,%ymm11
    2bdb:	c4 c1 7d d7 cb       	vpmovmskb %ymm11,%ecx
    2be0:	85 c9                	test   %ecx,%ecx
    2be2:	0f 84 28 fe ff ff    	je     2a10 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x13e0>
    2be8:	c4 c1 1d 72 d2 02    	vpsrld $0x2,%ymm10,%ymm12
    2bee:	c4 c1 35 72 d1 08    	vpsrld $0x8,%ymm9,%ymm9
    2bf4:	48 8b 74 24 08       	mov    0x8(%rsp),%rsi
    2bf9:	c5 7d 6f fb          	vmovdqa %ymm3,%ymm15
    2bfd:	c5 1d db e6          	vpand  %ymm6,%ymm12,%ymm12
    2c01:	c4 41 35 db cb       	vpand  %ymm11,%ymm9,%ymm9
    2c06:	c4 41 55 db d2       	vpand  %ymm10,%ymm5,%ymm10
    2c0b:	c4 41 35 fe cc       	vpaddd %ymm12,%ymm9,%ymm9
    2c10:	c4 c1 2d 72 f2 03    	vpslld $0x3,%ymm10,%ymm10
    2c16:	c4 22 05 90 24 8e    	vpgatherdd %ymm15,(%rsi,%ymm9,4),%ymm12
    2c1c:	c4 42 1d 45 ca       	vpsrlvd %ymm10,%ymm12,%ymm9
    2c21:	c5 35 db c9          	vpand  %ymm1,%ymm9,%ymm9
    2c25:	c4 43 7d 4c c9 b0    	vpblendvb %ymm11,%ymm9,%ymm0,%ymm9
    2c2b:	e9 e4 fd ff ff       	jmp    2a14 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x13e4>
    2c30:	4c 8b 54 24 c8       	mov    -0x38(%rsp),%r10
    2c35:	48 8b 5c 24 a8       	mov    -0x58(%rsp),%rbx
    2c3a:	4c 8b 5c 24 08       	mov    0x8(%rsp),%r11
    2c3f:	4c 8b 7c 24 88       	mov    -0x78(%rsp),%r15
    2c44:	48 8b 04 24          	mov    (%rsp),%rax
    2c48:	49 39 c6             	cmp    %rax,%r14
    2c4b:	0f 83 df ea ff ff    	jae    1730 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x100>
    2c51:	4f 8d 04 76          	lea    (%r14,%r14,2),%r8
    2c55:	4c 8d 0c 18          	lea    (%rax,%rbx,1),%r9
    2c59:	4b 8d 34 10          	lea    (%r8,%r10,1),%rsi
    2c5d:	4d 01 d1             	add    %r10,%r9
    2c60:	4d 01 f8             	add    %r15,%r8
    2c63:	eb 38                	jmp    2c9d <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x166d>
    2c65:	0f 1f 00             	nopl   (%rax)
    2c68:	83 e1 07             	and    $0x7,%ecx
    2c6b:	8d 4c 49 08          	lea    0x8(%rcx,%rcx,2),%ecx
    2c6f:	d3 e8                	shr    %cl,%eax
    2c71:	83 e0 07             	and    $0x7,%eax
    2c74:	44 01 d0             	add    %r10d,%eax
    2c77:	48 8d 0c 82          	lea    (%rdx,%rax,4),%rcx
    2c7b:	48 83 c6 03          	add    $0x3,%rsi
    2c7f:	49 83 c0 03          	add    $0x3,%r8
    2c83:	8b 01                	mov    (%rcx),%eax
    2c85:	0f b7 09             	movzwl (%rcx),%ecx
    2c88:	c1 e8 10             	shr    $0x10,%eax
    2c8b:	66 41 89 48 fd       	mov    %cx,-0x3(%r8)
    2c90:	41 88 40 ff          	mov    %al,-0x1(%r8)
    2c94:	4c 39 ce             	cmp    %r9,%rsi
    2c97:	0f 84 93 ea ff ff    	je     1730 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x100>
    2c9d:	0f b6 0e             	movzbl (%rsi),%ecx
    2ca0:	0f b6 46 01          	movzbl 0x1(%rsi),%eax
    2ca4:	c1 e1 10             	shl    $0x10,%ecx
    2ca7:	c1 e0 08             	shl    $0x8,%eax
    2caa:	09 c1                	or     %eax,%ecx
    2cac:	0f b6 46 02          	movzbl 0x2(%rsi),%eax
    2cb0:	09 c1                	or     %eax,%ecx
    2cb2:	89 c8                	mov    %ecx,%eax
    2cb4:	c1 e8 03             	shr    $0x3,%eax
    2cb7:	8b 04 87             	mov    (%rdi,%rax,4),%eax
    2cba:	44 0f b6 d0          	movzbl %al,%r10d
    2cbe:	41 81 fa ff 00 00 00 	cmp    $0xff,%r10d
    2cc5:	75 a1                	jne    2c68 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1638>
    2cc7:	41 89 ca             	mov    %ecx,%r10d
    2cca:	c1 e8 08             	shr    $0x8,%eax
    2ccd:	83 e1 03             	and    $0x3,%ecx
    2cd0:	41 c1 ea 02          	shr    $0x2,%r10d
    2cd4:	c1 e1 03             	shl    $0x3,%ecx
    2cd7:	41 83 e2 01          	and    $0x1,%r10d
    2cdb:	44 01 d0             	add    %r10d,%eax
    2cde:	89 c0                	mov    %eax,%eax
    2ce0:	41 8b 04 83          	mov    (%r11,%rax,4),%eax
    2ce4:	d3 e8                	shr    %cl,%eax
    2ce6:	0f b6 c0             	movzbl %al,%eax
    2ce9:	eb 8c                	jmp    2c77 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1647>
    2ceb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    2cf0:	48 8b 0c 24          	mov    (%rsp),%rcx
    2cf4:	e9 ae fc ff ff       	jmp    29a7 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1377>
    2cf9:	49 89 ce             	mov    %rcx,%r14
    2cfc:	e9 43 ff ff ff       	jmp    2c44 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1614>
    2d01:	4c 89 c1             	mov    %r8,%rcx
    2d04:	e9 9e fc ff ff       	jmp    29a7 <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1377>
    2d09:	48 8d 46 28          	lea    0x28(%rsi),%rax
    2d0d:	49 89 f0             	mov    %rsi,%r8
    2d10:	e9 c8 f6 ff ff       	jmp    23dd <jshc_channel::avx2_chain_wordload_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdad>
