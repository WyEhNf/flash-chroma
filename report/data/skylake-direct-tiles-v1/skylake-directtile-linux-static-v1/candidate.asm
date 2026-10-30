
artifacts/skylake-directtile-linux-build-v1/CMakeFiles/jshc_skylake_directtile.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 63 12 00 00    	je     1270 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1270>
       d:	55                   	push   %rbp
       e:	b8 00 04 00 00       	mov    $0x400,%eax
      13:	48 89 d6             	mov    %rdx,%rsi
      16:	48 8d 14 49          	lea    (%rcx,%rcx,2),%rdx
      1a:	48 89 e5             	mov    %rsp,%rbp
      1d:	41 56                	push   %r14
      1f:	41 55                	push   %r13
      21:	41 54                	push   %r12
      23:	53                   	push   %rbx
      24:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
      28:	48 81 ec 88 00 00 00 	sub    $0x88,%rsp
      2f:	48 39 c2             	cmp    %rax,%rdx
      32:	48 0f 47 d0          	cmova  %rax,%rdx
      36:	31 c0                	xor    %eax,%eax
      38:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
      3f:	00 
      40:	0f 18 04 06          	prefetchnta (%rsi,%rax,1)
      44:	48 83 c0 40          	add    $0x40,%rax
      48:	48 39 d0             	cmp    %rdx,%rax
      4b:	72 f3                	jb     40 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x40>
      4d:	49 89 f1             	mov    %rsi,%r9
      50:	45 31 c0             	xor    %r8d,%r8d
      53:	eb 7f                	jmp    d4 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd4>
      55:	0f 1f 00             	nopl   (%rax)
      58:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
      5d:	41 0f b6 51 02       	movzbl 0x2(%r9),%edx
      62:	49 ff c0             	inc    %r8
      65:	49 83 c1 03          	add    $0x3,%r9
      69:	c1 e2 10             	shl    $0x10,%edx
      6c:	c1 e0 08             	shl    $0x8,%eax
      6f:	09 d0                	or     %edx,%eax
      71:	41 0f b6 51 fd       	movzbl -0x3(%r9),%edx
      76:	09 d0                	or     %edx,%eax
      78:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
      7f:	44 8d 14 00          	lea    (%rax,%rax,1),%r10d
      83:	41 81 e2 00 fc 01 00 	and    $0x1fc00,%r10d
      8a:	81 e2 f0 03 00 00    	and    $0x3f0,%edx
      90:	44 09 d2             	or     %r10d,%edx
      93:	41 89 c2             	mov    %eax,%r10d
      96:	41 81 e2 03 00 fe 00 	and    $0xfe0003,%r10d
      9d:	44 09 d2             	or     %r10d,%edx
      a0:	41 89 c2             	mov    %eax,%r10d
      a3:	c1 e8 0d             	shr    $0xd,%eax
      a6:	41 c1 ea 06          	shr    $0x6,%r10d
      aa:	83 e0 08             	and    $0x8,%eax
      ad:	41 83 e2 04          	and    $0x4,%r10d
      b1:	44 09 d2             	or     %r10d,%edx
      b4:	09 d0                	or     %edx,%eax
      b6:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
      ba:	8b 02                	mov    (%rdx),%eax
      bc:	0f b7 12             	movzwl (%rdx),%edx
      bf:	c1 e8 10             	shr    $0x10,%eax
      c2:	66 41 89 51 fd       	mov    %dx,-0x3(%r9)
      c7:	41 88 41 ff          	mov    %al,-0x1(%r9)
      cb:	4c 39 c1             	cmp    %r8,%rcx
      ce:	0f 84 8c 11 00 00    	je     1260 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1260>
      d4:	41 f6 c1 3f          	test   $0x3f,%r9b
      d8:	0f 85 7a ff ff ff    	jne    58 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x58>
      de:	49 8d 40 48          	lea    0x48(%r8),%rax
      e2:	48 39 c1             	cmp    %rax,%rcx
      e5:	0f 82 86 11 00 00    	jb     1271 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1271>
      eb:	ba fc 00 fe 00       	mov    $0xfe00fc,%edx
      f0:	c5 fd 76 c0          	vpcmpeqd %ymm0,%ymm0,%ymm0
      f4:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
      f8:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 100 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x100>
      ff:	00 
     100:	c5 f9 6e da          	vmovd  %edx,%xmm3
     104:	ba 03 01 01 00       	mov    $0x10103,%edx
     109:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 111 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x111>
     110:	00 
     111:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 119 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x119>
     118:	00 
     119:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
     11e:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # 126 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x126>
     125:	00 
     126:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 12e <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x12e>
     12d:	00 
     12e:	48 01 f0             	add    %rsi,%rax
     131:	c5 fd 7f 5c 24 68    	vmovdqa %ymm3,0x68(%rsp)
     137:	c5 f9 6e da          	vmovd  %edx,%xmm3
     13b:	ba 00 00 fe 00       	mov    $0xfe0000,%edx
     140:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 148 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x148>
     147:	00 
     148:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
     14d:	c5 fd 7f 5c 24 48    	vmovdqa %ymm3,0x48(%rsp)
     153:	c5 e5 71 d0 0f       	vpsrlw $0xf,%ymm0,%ymm3
     158:	c5 fd 7f 5c 24 a8    	vmovdqa %ymm3,-0x58(%rsp)
     15e:	c5 f9 6e da          	vmovd  %edx,%xmm3
     162:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
     167:	c5 fd 7f 5c 24 88    	vmovdqa %ymm3,-0x78(%rsp)
     16d:	eb 04                	jmp    173 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x173>
     16f:	90                   	nop
     170:	49 89 d0             	mov    %rdx,%r8
     173:	49 8d 90 96 01 00 00 	lea    0x196(%r8),%rdx
     17a:	48 39 d1             	cmp    %rdx,%rcx
     17d:	72 1c                	jb     19b <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x19b>
     17f:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
     186:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
     18d:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     194:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     19b:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     19f:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     1a4:	48 05 c0 00 00 00    	add    $0xc0,%rax
     1aa:	c5 7d 6f 5c 24 48    	vmovdqa 0x48(%rsp),%ymm11
     1b0:	c5 7d 6f 44 24 68    	vmovdqa 0x68(%rsp),%ymm8
     1b6:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     1bc:	c5 7d 6f 64 24 88    	vmovdqa -0x78(%rsp),%ymm12
     1c2:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     1c8:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     1cd:	c5 7d 7f e6          	vmovdqa %ymm12,%ymm6
     1d1:	c4 c1 7d db d3       	vpand  %ymm11,%ymm0,%ymm2
     1d6:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
     1db:	c4 c1 7d db c4       	vpand  %ymm12,%ymm0,%ymm0
     1e0:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     1e5:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
     1ea:	c5 ed f5 54 24 a8    	vpmaddwd -0x58(%rsp),%ymm2,%ymm2
     1f0:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
     1f5:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     1f9:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     1fd:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     203:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     208:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     20e:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     213:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     219:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     21f:	c4 21 79 6e 14 8f    	vmovd  (%rdi,%r9,4),%xmm10
     225:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     22b:	c4 e3 79 16 cb 01    	vpextrd $0x1,%xmm1,%ebx
     231:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     237:	c4 c3 79 16 cd 03    	vpextrd $0x3,%xmm1,%r13d
     23d:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     243:	c4 63 29 22 14 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm10,%xmm10
     24a:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     251:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     258:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     25c:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     262:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     269:	c5 a9 6c c9          	vpunpcklqdq %xmm1,%xmm10,%xmm1
     26d:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     273:	c5 fa 6f 80 58 ff ff 	vmovdqu -0xa8(%rax),%xmm0
     27a:	ff 
     27b:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
     280:	c4 62 45 36 d1       	vpermd %ymm1,%ymm7,%ymm10
     285:	c5 fa 7e 88 68 ff ff 	vmovq  -0x98(%rax),%xmm1
     28c:	ff 
     28d:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     293:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     299:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     29e:	c4 c1 7d db d3       	vpand  %ymm11,%ymm0,%ymm2
     2a3:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
     2a8:	c4 c1 7d db c4       	vpand  %ymm12,%ymm0,%ymm0
     2ad:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     2b2:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
     2b7:	c5 ed f5 54 24 a8    	vpmaddwd -0x58(%rsp),%ymm2,%ymm2
     2bd:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
     2c2:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     2c6:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     2ca:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     2d0:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     2d5:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     2db:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     2e0:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     2e6:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     2ec:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
     2f2:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     2f8:	c4 e3 79 16 cb 01    	vpextrd $0x1,%xmm1,%ebx
     2fe:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     304:	c4 c3 79 16 cd 03    	vpextrd $0x3,%xmm1,%r13d
     30a:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     310:	c4 e3 61 22 1c 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm3,%xmm3
     317:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     31e:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     325:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     329:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     32f:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     336:	c5 e1 6c c9          	vpunpcklqdq %xmm1,%xmm3,%xmm1
     33a:	c5 fd 6f 5c 24 a8    	vmovdqa -0x58(%rsp),%ymm3
     340:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     346:	c5 fa 6f 80 70 ff ff 	vmovdqu -0x90(%rax),%xmm0
     34d:	ff 
     34e:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
     353:	c4 e2 45 36 d1       	vpermd %ymm1,%ymm7,%ymm2
     358:	c5 fa 7e 48 80       	vmovq  -0x80(%rax),%xmm1
     35d:	c5 fd 7f 54 24 28    	vmovdqa %ymm2,0x28(%rsp)
     363:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     369:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     36f:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     374:	c4 c1 7d db d3       	vpand  %ymm11,%ymm0,%ymm2
     379:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
     37e:	c4 c1 7d db c4       	vpand  %ymm12,%ymm0,%ymm0
     383:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
     388:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     38d:	c4 41 7d 6f e3       	vmovdqa %ymm11,%ymm12
     392:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
     396:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
     39b:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     39f:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     3a3:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     3a9:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     3ae:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     3b4:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     3ba:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     3bf:	c4 e3 79 16 cb 01    	vpextrd $0x1,%xmm1,%ebx
     3c5:	c4 c3 79 16 cd 03    	vpextrd $0x3,%xmm1,%r13d
     3cb:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     3d1:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     3d7:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     3dd:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     3e4:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     3ea:	c4 a1 79 6e 14 8f    	vmovd  (%rdi,%r9,4),%xmm2
     3f0:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     3f7:	c4 e3 69 22 14 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm2,%xmm2
     3fe:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     402:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     408:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     40f:	c5 e9 6c c9          	vpunpcklqdq %xmm1,%xmm2,%xmm1
     413:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     419:	c5 fa 7e 40 98       	vmovq  -0x68(%rax),%xmm0
     41e:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
     423:	c4 e2 45 36 c9       	vpermd %ymm1,%ymm7,%ymm1
     428:	c5 fd 7f 4c 24 08    	vmovdqa %ymm1,0x8(%rsp)
     42e:	c5 fa 6f 48 88       	vmovdqu -0x78(%rax),%xmm1
     433:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
     439:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     43f:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
     444:	c4 c1 75 db d3       	vpand  %ymm11,%ymm1,%ymm2
     449:	c4 e2 75 00 c4       	vpshufb %ymm4,%ymm1,%ymm0
     44e:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
     452:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
     457:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     45c:	c5 7d 6f de          	vmovdqa %ymm6,%ymm11
     460:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
     464:	c4 c1 7d f5 c7       	vpmaddwd %ymm15,%ymm0,%ymm0
     469:	c5 7d 7f c6          	vmovdqa %ymm8,%ymm6
     46d:	c5 fd eb c2          	vpor   %ymm2,%ymm0,%ymm0
     471:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     475:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     47b:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     480:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     486:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     48b:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     491:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     497:	c4 21 79 6e 0c 8f    	vmovd  (%rdi,%r9,4),%xmm9
     49d:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     4a3:	c4 e3 79 16 cb 01    	vpextrd $0x1,%xmm1,%ebx
     4a9:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     4af:	c4 c3 79 16 cd 03    	vpextrd $0x3,%xmm1,%r13d
     4b5:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     4bb:	c4 63 31 22 0c 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm9,%xmm9
     4c2:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     4c9:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     4d0:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     4d4:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     4da:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     4e1:	c5 b1 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm1
     4e5:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     4eb:	c5 fa 6f 40 a0       	vmovdqu -0x60(%rax),%xmm0
     4f0:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
     4f5:	c4 62 45 36 c9       	vpermd %ymm1,%ymm7,%ymm9
     4fa:	c5 fa 7e 48 b0       	vmovq  -0x50(%rax),%xmm1
     4ff:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     505:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     50b:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     510:	c4 c1 7d db d4       	vpand  %ymm12,%ymm0,%ymm2
     515:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
     51a:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     51f:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
     524:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     529:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
     52d:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
     532:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     536:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     53a:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     540:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     545:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     54b:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     550:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     556:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     55c:	c4 21 79 6e 04 8f    	vmovd  (%rdi,%r9,4),%xmm8
     562:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     568:	c4 e3 79 16 cb 01    	vpextrd $0x1,%xmm1,%ebx
     56e:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     574:	c4 c3 79 16 cd 03    	vpextrd $0x3,%xmm1,%r13d
     57a:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     580:	c4 63 39 22 04 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm8,%xmm8
     587:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     58e:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     595:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     599:	c4 a1 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm1
     59f:	c4 a3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm1,%xmm1
     5a6:	c5 b9 6c c9          	vpunpcklqdq %xmm1,%xmm8,%xmm1
     5aa:	c4 41 7d 6f c3       	vmovdqa %ymm11,%ymm8
     5af:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     5b5:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
     5ba:	c4 e2 45 36 c1       	vpermd %ymm1,%ymm7,%ymm0
     5bf:	c5 fa 7e 48 c8       	vmovq  -0x38(%rax),%xmm1
     5c4:	c5 fd 7f 44 24 e8    	vmovdqa %ymm0,-0x18(%rsp)
     5ca:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
     5cf:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     5d5:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     5db:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     5e0:	c4 c1 7d db d4       	vpand  %ymm12,%ymm0,%ymm2
     5e5:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
     5ea:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     5ef:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
     5f3:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     5f8:	c5 7d 6f e3          	vmovdqa %ymm3,%ymm12
     5fc:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
     600:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
     605:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     609:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     60d:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     613:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     618:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     61e:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     624:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     629:	c4 e3 79 16 cb 01    	vpextrd $0x1,%xmm1,%ebx
     62f:	c4 c3 79 16 cd 03    	vpextrd $0x3,%xmm1,%r13d
     635:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     63b:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     641:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     647:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     64e:	c4 a1 79 6e 04 a7    	vmovd  (%rdi,%r12,4),%xmm0
     654:	c4 a1 79 6e 34 9f    	vmovd  (%rdi,%r11,4),%xmm6
     65a:	c4 e3 79 22 04 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm0,%xmm0
     661:	c4 a3 49 22 34 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm6,%xmm6
     668:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     66c:	c4 a1 79 6e 0c 8f    	vmovd  (%rdi,%r9,4),%xmm1
     672:	c4 e3 71 22 0c 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm1,%xmm1
     679:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     67d:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     683:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
     688:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
     68d:	c4 e2 45 36 f1       	vpermd %ymm1,%ymm7,%ymm6
     692:	c5 fa 7e 48 e0       	vmovq  -0x20(%rax),%xmm1
     697:	c5 fd 7f 74 24 c8    	vmovdqa %ymm6,-0x38(%rsp)
     69d:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     6a3:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     6a9:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     6ae:	c5 fd db 54 24 48    	vpand  0x48(%rsp),%ymm0,%ymm2
     6b4:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
     6b9:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
     6be:	c5 f5 db 4c 24 68    	vpand  0x68(%rsp),%ymm1,%ymm1
     6c4:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     6c9:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
     6cd:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
     6d2:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     6d6:	c5 fa 7e 50 f8       	vmovq  -0x8(%rax),%xmm2
     6db:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     6df:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     6e5:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     6ea:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     6f0:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     6f5:	c4 e3 79 16 cb 01    	vpextrd $0x1,%xmm1,%ebx
     6fb:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     701:	c4 c3 79 16 cd 03    	vpextrd $0x3,%xmm1,%r13d
     707:	c5 fa 6f 48 e8       	vmovdqu -0x18(%rax),%xmm1
     70c:	c4 a1 79 6e 34 a7    	vmovd  (%rdi,%r12,4),%xmm6
     712:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     718:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     71e:	c4 a1 79 6e 04 b7    	vmovd  (%rdi,%r14,4),%xmm0
     724:	c4 21 79 6e 1c 9f    	vmovd  (%rdi,%r11,4),%xmm11
     72a:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     730:	c4 e3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm6,%xmm6
     737:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     73d:	c4 a3 79 22 04 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm0,%xmm0
     744:	c4 23 21 22 1c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm11,%xmm11
     74b:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
     750:	c5 f5 db 5c 24 48    	vpand  0x48(%rsp),%ymm1,%ymm3
     756:	c4 e2 75 00 d4       	vpshufb %ymm4,%ymm1,%ymm2
     75b:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
     75f:	c4 a1 79 6e 04 8f    	vmovd  (%rdi,%r9,4),%xmm0
     765:	c5 ed db 54 24 68    	vpand  0x68(%rsp),%ymm2,%ymm2
     76b:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
     770:	c4 41 79 6f c2       	vmovdqa %xmm10,%xmm8
     775:	c4 c2 65 04 dd       	vpmaddubsw %ymm13,%ymm3,%ymm3
     77a:	c4 e3 79 22 04 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm0,%xmm0
     781:	c4 c1 65 f5 dc       	vpmaddwd %ymm12,%ymm3,%ymm3
     786:	c4 c1 6d f5 d7       	vpmaddwd %ymm15,%ymm2,%ymm2
     78b:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     78f:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
     794:	c4 63 7d 39 d3 01    	vextracti128 $0x1,%ymm10,%xmm3
     79a:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     79e:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     7a4:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
     7aa:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
     7af:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     7b5:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     7ba:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     7c0:	c4 e3 79 16 d3 01    	vpextrd $0x1,%xmm2,%ebx
     7c6:	c4 21 79 6e 24 9f    	vmovd  (%rdi,%r11,4),%xmm12
     7cc:	c4 a1 79 6e 34 b7    	vmovd  (%rdi,%r14,4),%xmm6
     7d2:	c4 21 79 6e 1c a7    	vmovd  (%rdi,%r12,4),%xmm11
     7d8:	c4 c3 79 16 d5 03    	vpextrd $0x3,%xmm2,%r13d
     7de:	c4 e3 79 16 ca 01    	vpextrd $0x1,%xmm1,%edx
     7e4:	c4 c3 79 16 ca 03    	vpextrd $0x3,%xmm1,%r10d
     7ea:	c4 c2 7d 00 c6       	vpshufb %ymm14,%ymm0,%ymm0
     7ef:	c4 a3 49 22 34 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm6,%xmm6
     7f6:	c4 63 21 22 1c 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm11,%xmm11
     7fd:	c4 e2 45 36 c0       	vpermd %ymm0,%ymm7,%ymm0
     802:	c4 23 19 22 24 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm12,%xmm12
     809:	c5 21 6c de          	vpunpcklqdq %xmm6,%xmm11,%xmm11
     80d:	c4 a1 79 6e 34 8f    	vmovd  (%rdi,%r9,4),%xmm6
     813:	4d 8d 88 88 00 00 00 	lea    0x88(%r8),%r9
     81a:	c4 e3 49 22 34 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm6,%xmm6
     821:	c5 fd 6f 54 24 28    	vmovdqa 0x28(%rsp),%ymm2
     827:	49 8d 50 40          	lea    0x40(%r8),%rdx
     82b:	c5 7d 6f 54 24 08    	vmovdqa 0x8(%rsp),%ymm10
     831:	c4 c1 49 6c f4       	vpunpcklqdq %xmm12,%xmm6,%xmm6
     836:	c5 79 6f 64 24 08    	vmovdqa 0x8(%rsp),%xmm12
     83c:	c4 c3 4d 38 f3 01    	vinserti128 $0x1,%xmm11,%ymm6,%ymm6
     842:	c4 63 7d 39 d1 01    	vextracti128 $0x1,%ymm10,%xmm1
     848:	c5 79 6f da          	vmovdqa %xmm2,%xmm11
     84c:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     851:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     857:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     85d:	c4 43 31 0f ca 08    	vpalignr $0x8,%xmm10,%xmm9,%xmm9
     863:	c4 c1 61 6c db       	vpunpcklqdq %xmm11,%xmm3,%xmm3
     868:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     86d:	c4 c3 69 0f d3 08    	vpalignr $0x8,%xmm11,%xmm2,%xmm2
     873:	c4 63 3d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm8,%ymm8
     879:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     87f:	c4 c3 6d 38 d4 01    	vinserti128 $0x1,%xmm12,%ymm2,%ymm2
     885:	c5 7d e7 80 40 ff ff 	vmovntdq %ymm8,-0xc0(%rax)
     88c:	ff 
     88d:	c5 fd e7 48 80       	vmovntdq %ymm1,-0x80(%rax)
     892:	c4 c2 4d 00 f6       	vpshufb %ymm14,%ymm6,%ymm6
     897:	c5 fd e7 90 60 ff ff 	vmovntdq %ymm2,-0xa0(%rax)
     89e:	ff 
     89f:	c5 fd 6f 5c 24 e8    	vmovdqa -0x18(%rsp),%ymm3
     8a5:	c5 fd 6f 4c 24 c8    	vmovdqa -0x38(%rsp),%ymm1
     8ab:	c4 e2 45 36 f6       	vpermd %ymm6,%ymm7,%ymm6
     8b0:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
     8b4:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
     8b8:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     8be:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     8c2:	c5 f9 6f d3          	vmovdqa %xmm3,%xmm2
     8c6:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     8cc:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     8d2:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     8d8:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     8de:	c4 c1 61 6c d9       	vpunpcklqdq %xmm9,%xmm3,%xmm3
     8e3:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
     8e9:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
     8ee:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
     8f4:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
     8fa:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     900:	c5 fd e7 50 a0       	vmovntdq %ymm2,-0x60(%rax)
     905:	c5 fd e7 48 c0       	vmovntdq %ymm1,-0x40(%rax)
     90a:	c5 fd e7 40 e0       	vmovntdq %ymm0,-0x20(%rax)
     90f:	4c 39 c9             	cmp    %r9,%rcx
     912:	0f 83 58 f8 ff ff    	jae    170 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x170>
     918:	0f ae f8             	sfence
     91b:	49 8d 40 68          	lea    0x68(%r8),%rax
     91f:	48 39 c1             	cmp    %rax,%rcx
     922:	0f 82 20 04 00 00    	jb     d48 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd48>
     928:	41 b8 fc 00 fe 00    	mov    $0xfe00fc,%r8d
     92e:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
     932:	c4 41 3d 76 c0       	vpcmpeqd %ymm8,%ymm8,%ymm8
     937:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 93f <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x93f>
     93e:	00 
     93f:	c4 c1 79 6e d8       	vmovd  %r8d,%xmm3
     944:	41 b8 03 01 01 00    	mov    $0x10103,%r8d
     94a:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 952 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x952>
     951:	00 
     952:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 95a <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x95a>
     959:	00 
     95a:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
     95f:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # 967 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x967>
     966:	00 
     967:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 96f <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x96f>
     96e:	00 
     96f:	48 01 f0             	add    %rsi,%rax
     972:	c5 fd 7f 5c 24 68    	vmovdqa %ymm3,0x68(%rsp)
     978:	c4 c1 79 6e d8       	vmovd  %r8d,%xmm3
     97d:	41 b8 00 00 fe 00    	mov    $0xfe0000,%r8d
     983:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 98b <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x98b>
     98a:	00 
     98b:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
     990:	c4 c1 3d 71 d0 0f    	vpsrlw $0xf,%ymm8,%ymm8
     996:	c4 41 79 6e e0       	vmovd  %r8d,%xmm12
     99b:	c5 fd 7f 5c 24 28    	vmovdqa %ymm3,0x28(%rsp)
     9a1:	c4 42 7d 58 e4       	vpbroadcastd %xmm12,%ymm12
     9a6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     9ad:	00 00 00 
     9b0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     9b4:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     9b9:	48 83 c0 60          	add    $0x60,%rax
     9bd:	c5 7d 6f 4c 24 28    	vmovdqa 0x28(%rsp),%ymm9
     9c3:	c5 7d 6f 5c 24 68    	vmovdqa 0x68(%rsp),%ymm11
     9c9:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     9cf:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     9d5:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     9da:	c4 c1 7d db d1       	vpand  %ymm9,%ymm0,%ymm2
     9df:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
     9e4:	c5 9d db c0          	vpand  %ymm0,%ymm12,%ymm0
     9e8:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
     9ed:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
     9f2:	c4 c1 6d f5 d0       	vpmaddwd %ymm8,%ymm2,%ymm2
     9f7:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
     9fc:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     a00:	c5 fa 7e 50 c8       	vmovq  -0x38(%rax),%xmm2
     a05:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
     a09:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     a0e:	c4 e3 7d 39 44 24 48 	vextracti128 $0x1,%ymm0,0x48(%rsp)
     a15:	01 
     a16:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
     a1c:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     a22:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
     a27:	c4 c1 75 db d9       	vpand  %ymm9,%ymm1,%ymm3
     a2c:	c4 e2 75 00 d4       	vpshufb %ymm4,%ymm1,%ymm2
     a31:	c5 9d db c9          	vpand  %ymm1,%ymm12,%ymm1
     a35:	c4 c1 6d db d3       	vpand  %ymm11,%ymm2,%ymm2
     a3a:	c4 c2 65 04 dd       	vpmaddubsw %ymm13,%ymm3,%ymm3
     a3f:	c4 c1 65 f5 d8       	vpmaddwd %ymm8,%ymm3,%ymm3
     a44:	c4 c1 6d f5 d7       	vpmaddwd %ymm15,%ymm2,%ymm2
     a49:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     a4d:	c5 fa 6f 58 d0       	vmovdqu -0x30(%rax),%xmm3
     a52:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
     a56:	c5 fa 7e 50 e0       	vmovq  -0x20(%rax),%xmm2
     a5b:	c4 c3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm10
     a61:	c4 e3 69 0f d3 0c    	vpalignr $0xc,%xmm3,%xmm2,%xmm2
     a67:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
     a6d:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
     a72:	c4 e2 65 00 d4       	vpshufb %ymm4,%ymm3,%ymm2
     a77:	c4 c1 65 db f1       	vpand  %ymm9,%ymm3,%ymm6
     a7c:	c5 9d db db          	vpand  %ymm3,%ymm12,%ymm3
     a80:	c5 ed db 54 24 68    	vpand  0x68(%rsp),%ymm2,%ymm2
     a86:	c4 c2 4d 04 f5       	vpmaddubsw %ymm13,%ymm6,%ymm6
     a8b:	c4 c1 4d f5 f0       	vpmaddwd %ymm8,%ymm6,%ymm6
     a90:	c4 c1 6d f5 d7       	vpmaddwd %ymm15,%ymm2,%ymm2
     a95:	c5 ed eb d6          	vpor   %ymm6,%ymm2,%ymm2
     a99:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
     a9e:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
     aa2:	c5 fa 6f 58 e8       	vmovdqu -0x18(%rax),%xmm3
     aa7:	c4 c3 7d 39 d3 01    	vextracti128 $0x1,%ymm2,%xmm11
     aad:	c4 e3 49 0f f3 0c    	vpalignr $0xc,%xmm3,%xmm6,%xmm6
     ab3:	c4 e3 65 38 de 01    	vinserti128 $0x1,%xmm6,%ymm3,%ymm3
     ab9:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
     abe:	c4 e2 65 00 f4       	vpshufb %ymm4,%ymm3,%ymm6
     ac3:	c4 41 65 db c9       	vpand  %ymm9,%ymm3,%ymm9
     ac8:	c5 9d db db          	vpand  %ymm3,%ymm12,%ymm3
     acc:	c5 cd db 74 24 68    	vpand  0x68(%rsp),%ymm6,%ymm6
     ad2:	c4 42 35 04 cd       	vpmaddubsw %ymm13,%ymm9,%ymm9
     ad7:	c4 41 35 f5 c8       	vpmaddwd %ymm8,%ymm9,%ymm9
     adc:	c4 c1 4d f5 f7       	vpmaddwd %ymm15,%ymm6,%ymm6
     ae1:	c4 c1 4d eb f1       	vpor   %ymm9,%ymm6,%ymm6
     ae6:	c5 e5 eb de          	vpor   %ymm6,%ymm3,%ymm3
     aea:	c4 e3 7d 39 de 01    	vextracti128 $0x1,%ymm3,%xmm6
     af0:	c4 c1 79 7e d9       	vmovd  %xmm3,%r9d
     af5:	c4 c3 79 16 d8 01    	vpextrd $0x1,%xmm3,%r8d
     afb:	c4 c3 79 16 f6 02    	vpextrd $0x2,%xmm6,%r14d
     b01:	c4 c1 79 7e f4       	vmovd  %xmm6,%r12d
     b06:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     b0c:	c4 c3 79 16 da 03    	vpextrd $0x3,%xmm3,%r10d
     b12:	c4 e3 79 16 f3 01    	vpextrd $0x1,%xmm6,%ebx
     b18:	c4 a1 79 6e 1c b7    	vmovd  (%rdi,%r14,4),%xmm3
     b1e:	c4 c3 79 16 f5 03    	vpextrd $0x3,%xmm6,%r13d
     b24:	c4 a1 79 6e 34 a7    	vmovd  (%rdi,%r12,4),%xmm6
     b2a:	c4 21 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm9
     b30:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
     b35:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
     b3b:	c4 a3 61 22 1c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm3,%xmm3
     b42:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     b48:	c4 43 79 16 dd 03    	vpextrd $0x3,%xmm11,%r13d
     b4e:	c4 e3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm6,%xmm6
     b55:	c4 23 31 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm9,%xmm9
     b5c:	c4 c3 79 16 d2 03    	vpextrd $0x3,%xmm2,%r10d
     b62:	c4 63 79 16 db 01    	vpextrd $0x1,%xmm11,%ebx
     b68:	c5 c9 6c f3          	vpunpcklqdq %xmm3,%xmm6,%xmm6
     b6c:	c4 a1 79 6e 1c 8f    	vmovd  (%rdi,%r9,4),%xmm3
     b72:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
     b77:	c4 a3 61 22 1c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm3,%xmm3
     b7e:	c4 c3 79 16 d0 01    	vpextrd $0x1,%xmm2,%r8d
     b84:	c4 a1 79 6e 14 b7    	vmovd  (%rdi,%r14,4),%xmm2
     b8a:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     b90:	c4 c1 61 6c d9       	vpunpcklqdq %xmm9,%xmm3,%xmm3
     b95:	c4 a3 69 22 14 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm2,%xmm2
     b9c:	c4 21 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm9
     ba2:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     ba8:	c4 e3 65 38 de 01    	vinserti128 $0x1,%xmm6,%ymm3,%ymm3
     bae:	c4 a1 79 6e 34 a7    	vmovd  (%rdi,%r12,4),%xmm6
     bb4:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     bb9:	c4 43 79 16 d5 03    	vpextrd $0x3,%xmm10,%r13d
     bbf:	c4 23 31 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm9,%xmm9
     bc6:	c4 c3 79 16 ca 03    	vpextrd $0x3,%xmm1,%r10d
     bcc:	c4 c2 65 00 de       	vpshufb %ymm14,%ymm3,%ymm3
     bd1:	c4 e3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm6,%xmm6
     bd8:	c4 63 79 16 d3 01    	vpextrd $0x1,%xmm10,%ebx
     bde:	c4 e2 45 36 db       	vpermd %ymm3,%ymm7,%ymm3
     be3:	c5 79 6f db          	vmovdqa %xmm3,%xmm11
     be7:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     bed:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
     bf1:	c4 a1 79 6e 14 8f    	vmovd  (%rdi,%r9,4),%xmm2
     bf7:	c4 c3 61 0f db 08    	vpalignr $0x8,%xmm11,%xmm3,%xmm3
     bfd:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
     c02:	c4 a3 69 22 14 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm2,%xmm2
     c09:	c4 c3 79 16 c8 01    	vpextrd $0x1,%xmm1,%r8d
     c0f:	c4 a1 79 6e 0c b7    	vmovd  (%rdi,%r14,4),%xmm1
     c15:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     c1a:	c4 a3 71 22 0c af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm1,%xmm1
     c21:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
     c27:	c4 a1 79 6e 34 a7    	vmovd  (%rdi,%r12,4),%xmm6
     c2d:	c4 c2 6d 00 d6       	vpshufb %ymm14,%ymm2,%ymm2
     c32:	c4 e3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm6,%xmm6
     c39:	c4 21 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm9
     c3f:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     c45:	c4 e2 45 36 d2       	vpermd %ymm2,%ymm7,%ymm2
     c4a:	44 8b 64 24 48       	mov    0x48(%rsp),%r12d
     c4f:	44 8b 74 24 50       	mov    0x50(%rsp),%r14d
     c54:	c5 79 6f d2          	vmovdqa %xmm2,%xmm10
     c58:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     c5e:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     c62:	c4 a1 79 6e 0c 8f    	vmovd  (%rdi,%r9,4),%xmm1
     c68:	c4 23 31 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm9,%xmm9
     c6f:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     c74:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     c7a:	8b 5c 24 4c          	mov    0x4c(%rsp),%ebx
     c7e:	44 8b 6c 24 54       	mov    0x54(%rsp),%r13d
     c83:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     c88:	c4 a3 71 22 0c 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm1,%xmm1
     c8f:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     c95:	c4 a1 79 6e 04 b7    	vmovd  (%rdi,%r14,4),%xmm0
     c9b:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
     ca1:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
     ca6:	c4 a3 79 22 04 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm0,%xmm0
     cad:	c4 21 79 6e 0c 9f    	vmovd  (%rdi,%r11,4),%xmm9
     cb3:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
     cb9:	c4 a1 79 6e 34 a7    	vmovd  (%rdi,%r12,4),%xmm6
     cbf:	c4 23 31 22 0c 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm9,%xmm9
     cc6:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
     ccb:	c4 e3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm6,%xmm6
     cd2:	c4 e2 45 36 c9       	vpermd %ymm1,%ymm7,%ymm1
     cd7:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
     cdb:	c4 a1 79 6e 04 8f    	vmovd  (%rdi,%r9,4),%xmm0
     ce1:	c4 a3 79 22 04 87 01 	vpinsrd $0x1,(%rdi,%r8,4),%xmm0,%xmm0
     ce8:	4c 8d 42 48          	lea    0x48(%rdx),%r8
     cec:	c5 fe 7f 50 e0       	vmovdqu %ymm2,-0x20(%rax)
     cf1:	48 83 c2 20          	add    $0x20,%rdx
     cf5:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
     cfa:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
     cfe:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     d04:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     d0a:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
     d10:	c4 c2 7d 00 c6       	vpshufb %ymm14,%ymm0,%ymm0
     d15:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
     d1b:	c4 e2 45 36 c0       	vpermd %ymm0,%ymm7,%ymm0
     d20:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     d25:	c5 f9 6f f0          	vmovdqa %xmm0,%xmm6
     d29:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     d2f:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
     d34:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     d3a:	c5 fe 7f 70 a0       	vmovdqu %ymm6,-0x60(%rax)
     d3f:	4c 39 c1             	cmp    %r8,%rcx
     d42:	0f 83 68 fc ff ff    	jae    9b0 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x9b0>
     d48:	4c 8d 42 08          	lea    0x8(%rdx),%r8
     d4c:	4c 39 c1             	cmp    %r8,%rcx
     d4f:	0f 82 60 01 00 00    	jb     eb5 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb5>
     d55:	48 8d 04 52          	lea    (%rdx,%rdx,2),%rax
     d59:	ba fc 00 fe 00       	mov    $0xfe00fc,%edx
     d5e:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
     d62:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # d6a <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd6a>
     d69:	00 
     d6a:	c5 f9 6e f2          	vmovd  %edx,%xmm6
     d6e:	ba 03 01 01 00       	mov    $0x10103,%edx
     d73:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # d7b <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd7b>
     d7a:	00 
     d7b:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # d83 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd83>
     d82:	00 
     d83:	c5 f9 6e da          	vmovd  %edx,%xmm3
     d87:	ba 00 00 fe 00       	mov    $0xfe0000,%edx
     d8c:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # d94 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd94>
     d93:	00 
     d94:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # d9c <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd9c>
     d9b:	00 
     d9c:	c5 f9 6e d2          	vmovd  %edx,%xmm2
     da0:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
     da5:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
     daa:	48 01 f0             	add    %rsi,%rax
     dad:	c5 f5 71 d1 0f       	vpsrlw $0xf,%ymm1,%ymm1
     db2:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
     db7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
     dbe:	00 00 
     dc0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     dc4:	c5 fa 7e 78 10       	vmovq  0x10(%rax),%xmm7
     dc9:	48 83 c0 18          	add    $0x18,%rax
     dcd:	c4 e3 41 0f f8 0c    	vpalignr $0xc,%xmm0,%xmm7,%xmm7
     dd3:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     dd9:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     dde:	c4 e2 7d 00 fc       	vpshufb %ymm4,%ymm0,%ymm7
     de3:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
     de7:	c5 ed db c0          	vpand  %ymm0,%ymm2,%ymm0
     deb:	c5 c5 db fe          	vpand  %ymm6,%ymm7,%ymm7
     def:	c4 42 3d 04 c5       	vpmaddubsw %ymm13,%ymm8,%ymm8
     df4:	c5 3d f5 c1          	vpmaddwd %ymm1,%ymm8,%ymm8
     df8:	c4 c1 45 f5 ff       	vpmaddwd %ymm15,%ymm7,%ymm7
     dfd:	c4 c1 45 eb f8       	vpor   %ymm8,%ymm7,%ymm7
     e02:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
     e06:	c4 e3 7d 39 c7 01    	vextracti128 $0x1,%ymm0,%xmm7
     e0c:	c4 e3 79 16 c2 01    	vpextrd $0x1,%xmm0,%edx
     e12:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     e17:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     e1d:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     e22:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     e28:	c4 c3 79 16 c2 03    	vpextrd $0x3,%xmm0,%r10d
     e2e:	c4 e3 79 16 fb 01    	vpextrd $0x1,%xmm7,%ebx
     e34:	c4 a1 79 6e 04 b7    	vmovd  (%rdi,%r14,4),%xmm0
     e3a:	c4 c3 79 16 fd 03    	vpextrd $0x3,%xmm7,%r13d
     e40:	c4 a1 79 6e 3c a7    	vmovd  (%rdi,%r12,4),%xmm7
     e46:	c4 21 79 6e 04 9f    	vmovd  (%rdi,%r11,4),%xmm8
     e4c:	c4 a3 79 22 04 af 01 	vpinsrd $0x1,(%rdi,%r13,4),%xmm0,%xmm0
     e53:	c4 e3 41 22 3c 9f 01 	vpinsrd $0x1,(%rdi,%rbx,4),%xmm7,%xmm7
     e5a:	c4 23 39 22 04 97 01 	vpinsrd $0x1,(%rdi,%r10,4),%xmm8,%xmm8
     e61:	c5 c1 6c f8          	vpunpcklqdq %xmm0,%xmm7,%xmm7
     e65:	c4 a1 79 6e 04 8f    	vmovd  (%rdi,%r9,4),%xmm0
     e6b:	c4 e3 79 22 04 97 01 	vpinsrd $0x1,(%rdi,%rdx,4),%xmm0,%xmm0
     e72:	4c 89 c2             	mov    %r8,%rdx
     e75:	49 83 c0 08          	add    $0x8,%r8
     e79:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
     e7e:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     e84:	c4 c2 7d 00 c6       	vpshufb %ymm14,%ymm0,%ymm0
     e89:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     e8d:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     e93:	c5 c1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm7
     e98:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     e9d:	c4 c1 41 eb f8       	vpor   %xmm8,%xmm7,%xmm7
     ea2:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     ea7:	c5 fa 7f 78 e8       	vmovdqu %xmm7,-0x18(%rax)
     eac:	4c 39 c1             	cmp    %r8,%rcx
     eaf:	0f 83 0b ff ff ff    	jae    dc0 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xdc0>
     eb5:	48 39 ca             	cmp    %rcx,%rdx
     eb8:	0f 83 8a 03 00 00    	jae    1248 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1248>
     ebe:	4c 8d 0c 52          	lea    (%rdx,%rdx,2),%r9
     ec2:	4e 8d 14 0e          	lea    (%rsi,%r9,1),%r10
     ec6:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     ecb:	45 0f b6 42 02       	movzbl 0x2(%r10),%r8d
     ed0:	c1 e0 08             	shl    $0x8,%eax
     ed3:	41 c1 e0 10          	shl    $0x10,%r8d
     ed7:	44 09 c0             	or     %r8d,%eax
     eda:	45 0f b6 02          	movzbl (%r10),%r8d
     ede:	44 09 c0             	or     %r8d,%eax
     ee1:	44 8d 04 85 00 00 00 	lea    0x0(,%rax,4),%r8d
     ee8:	00 
     ee9:	44 8d 1c 00          	lea    (%rax,%rax,1),%r11d
     eed:	41 81 e3 00 fc 01 00 	and    $0x1fc00,%r11d
     ef4:	41 81 e0 f0 03 00 00 	and    $0x3f0,%r8d
     efb:	45 09 d8             	or     %r11d,%r8d
     efe:	41 89 c3             	mov    %eax,%r11d
     f01:	41 81 e3 03 00 fe 00 	and    $0xfe0003,%r11d
     f08:	45 09 d8             	or     %r11d,%r8d
     f0b:	41 89 c3             	mov    %eax,%r11d
     f0e:	c1 e8 0d             	shr    $0xd,%eax
     f11:	41 c1 eb 06          	shr    $0x6,%r11d
     f15:	83 e0 08             	and    $0x8,%eax
     f18:	41 83 e3 04          	and    $0x4,%r11d
     f1c:	45 09 d8             	or     %r11d,%r8d
     f1f:	44 09 c0             	or     %r8d,%eax
     f22:	4c 8d 04 87          	lea    (%rdi,%rax,4),%r8
     f26:	41 8b 00             	mov    (%r8),%eax
     f29:	45 0f b7 00          	movzwl (%r8),%r8d
     f2d:	c1 e8 10             	shr    $0x10,%eax
     f30:	66 45 89 02          	mov    %r8w,(%r10)
     f34:	41 88 42 02          	mov    %al,0x2(%r10)
     f38:	48 8d 42 01          	lea    0x1(%rdx),%rax
     f3c:	48 39 c8             	cmp    %rcx,%rax
     f3f:	0f 83 03 03 00 00    	jae    1248 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1248>
     f45:	4e 8d 54 0e 03       	lea    0x3(%rsi,%r9,1),%r10
     f4a:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     f4f:	45 0f b6 42 02       	movzbl 0x2(%r10),%r8d
     f54:	c1 e0 08             	shl    $0x8,%eax
     f57:	41 c1 e0 10          	shl    $0x10,%r8d
     f5b:	44 09 c0             	or     %r8d,%eax
     f5e:	45 0f b6 02          	movzbl (%r10),%r8d
     f62:	44 09 c0             	or     %r8d,%eax
     f65:	44 8d 04 85 00 00 00 	lea    0x0(,%rax,4),%r8d
     f6c:	00 
     f6d:	44 8d 1c 00          	lea    (%rax,%rax,1),%r11d
     f71:	41 81 e3 00 fc 01 00 	and    $0x1fc00,%r11d
     f78:	41 81 e0 f0 03 00 00 	and    $0x3f0,%r8d
     f7f:	45 09 d8             	or     %r11d,%r8d
     f82:	41 89 c3             	mov    %eax,%r11d
     f85:	41 81 e3 03 00 fe 00 	and    $0xfe0003,%r11d
     f8c:	45 09 d8             	or     %r11d,%r8d
     f8f:	41 89 c3             	mov    %eax,%r11d
     f92:	c1 e8 0d             	shr    $0xd,%eax
     f95:	41 c1 eb 06          	shr    $0x6,%r11d
     f99:	83 e0 08             	and    $0x8,%eax
     f9c:	41 83 e3 04          	and    $0x4,%r11d
     fa0:	45 09 d8             	or     %r11d,%r8d
     fa3:	44 09 c0             	or     %r8d,%eax
     fa6:	4c 8d 04 87          	lea    (%rdi,%rax,4),%r8
     faa:	41 8b 00             	mov    (%r8),%eax
     fad:	45 0f b7 00          	movzwl (%r8),%r8d
     fb1:	c1 e8 10             	shr    $0x10,%eax
     fb4:	66 45 89 02          	mov    %r8w,(%r10)
     fb8:	41 88 42 02          	mov    %al,0x2(%r10)
     fbc:	48 8d 42 02          	lea    0x2(%rdx),%rax
     fc0:	48 39 c8             	cmp    %rcx,%rax
     fc3:	0f 83 7f 02 00 00    	jae    1248 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1248>
     fc9:	4e 8d 54 0e 06       	lea    0x6(%rsi,%r9,1),%r10
     fce:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
     fd3:	45 0f b6 42 01       	movzbl 0x1(%r10),%r8d
     fd8:	c1 e0 10             	shl    $0x10,%eax
     fdb:	41 c1 e0 08          	shl    $0x8,%r8d
     fdf:	44 09 c0             	or     %r8d,%eax
     fe2:	45 0f b6 02          	movzbl (%r10),%r8d
     fe6:	44 09 c0             	or     %r8d,%eax
     fe9:	44 8d 04 00          	lea    (%rax,%rax,1),%r8d
     fed:	44 8d 1c 85 00 00 00 	lea    0x0(,%rax,4),%r11d
     ff4:	00 
     ff5:	41 81 e3 f0 03 00 00 	and    $0x3f0,%r11d
     ffc:	41 81 e0 00 fc 01 00 	and    $0x1fc00,%r8d
    1003:	45 09 d8             	or     %r11d,%r8d
    1006:	41 89 c3             	mov    %eax,%r11d
    1009:	41 81 e3 03 00 fe 00 	and    $0xfe0003,%r11d
    1010:	45 09 d8             	or     %r11d,%r8d
    1013:	41 89 c3             	mov    %eax,%r11d
    1016:	c1 e8 0d             	shr    $0xd,%eax
    1019:	41 c1 eb 06          	shr    $0x6,%r11d
    101d:	83 e0 08             	and    $0x8,%eax
    1020:	41 83 e3 04          	and    $0x4,%r11d
    1024:	45 09 d8             	or     %r11d,%r8d
    1027:	44 09 c0             	or     %r8d,%eax
    102a:	4c 8d 04 87          	lea    (%rdi,%rax,4),%r8
    102e:	41 8b 00             	mov    (%r8),%eax
    1031:	45 0f b7 00          	movzwl (%r8),%r8d
    1035:	c1 e8 10             	shr    $0x10,%eax
    1038:	66 45 89 02          	mov    %r8w,(%r10)
    103c:	41 88 42 02          	mov    %al,0x2(%r10)
    1040:	48 8d 42 03          	lea    0x3(%rdx),%rax
    1044:	48 39 c8             	cmp    %rcx,%rax
    1047:	0f 83 fb 01 00 00    	jae    1248 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1248>
    104d:	4e 8d 54 0e 09       	lea    0x9(%rsi,%r9,1),%r10
    1052:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
    1057:	45 0f b6 42 01       	movzbl 0x1(%r10),%r8d
    105c:	c1 e0 10             	shl    $0x10,%eax
    105f:	41 c1 e0 08          	shl    $0x8,%r8d
    1063:	44 09 c0             	or     %r8d,%eax
    1066:	45 0f b6 02          	movzbl (%r10),%r8d
    106a:	44 09 c0             	or     %r8d,%eax
    106d:	44 8d 04 00          	lea    (%rax,%rax,1),%r8d
    1071:	44 8d 1c 85 00 00 00 	lea    0x0(,%rax,4),%r11d
    1078:	00 
    1079:	41 81 e3 f0 03 00 00 	and    $0x3f0,%r11d
    1080:	41 81 e0 00 fc 01 00 	and    $0x1fc00,%r8d
    1087:	45 09 d8             	or     %r11d,%r8d
    108a:	41 89 c3             	mov    %eax,%r11d
    108d:	41 81 e3 03 00 fe 00 	and    $0xfe0003,%r11d
    1094:	45 09 d8             	or     %r11d,%r8d
    1097:	41 89 c3             	mov    %eax,%r11d
    109a:	c1 e8 0d             	shr    $0xd,%eax
    109d:	41 c1 eb 06          	shr    $0x6,%r11d
    10a1:	83 e0 08             	and    $0x8,%eax
    10a4:	41 83 e3 04          	and    $0x4,%r11d
    10a8:	45 09 d8             	or     %r11d,%r8d
    10ab:	44 09 c0             	or     %r8d,%eax
    10ae:	4c 8d 04 87          	lea    (%rdi,%rax,4),%r8
    10b2:	41 8b 00             	mov    (%r8),%eax
    10b5:	45 0f b7 00          	movzwl (%r8),%r8d
    10b9:	c1 e8 10             	shr    $0x10,%eax
    10bc:	66 45 89 02          	mov    %r8w,(%r10)
    10c0:	41 88 42 02          	mov    %al,0x2(%r10)
    10c4:	48 8d 42 04          	lea    0x4(%rdx),%rax
    10c8:	48 39 c8             	cmp    %rcx,%rax
    10cb:	0f 83 77 01 00 00    	jae    1248 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1248>
    10d1:	4e 8d 54 0e 0c       	lea    0xc(%rsi,%r9,1),%r10
    10d6:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
    10db:	45 0f b6 42 01       	movzbl 0x1(%r10),%r8d
    10e0:	c1 e0 10             	shl    $0x10,%eax
    10e3:	41 c1 e0 08          	shl    $0x8,%r8d
    10e7:	44 09 c0             	or     %r8d,%eax
    10ea:	45 0f b6 02          	movzbl (%r10),%r8d
    10ee:	44 09 c0             	or     %r8d,%eax
    10f1:	44 8d 04 00          	lea    (%rax,%rax,1),%r8d
    10f5:	44 8d 1c 85 00 00 00 	lea    0x0(,%rax,4),%r11d
    10fc:	00 
    10fd:	41 81 e3 f0 03 00 00 	and    $0x3f0,%r11d
    1104:	41 81 e0 00 fc 01 00 	and    $0x1fc00,%r8d
    110b:	45 09 d8             	or     %r11d,%r8d
    110e:	41 89 c3             	mov    %eax,%r11d
    1111:	41 81 e3 03 00 fe 00 	and    $0xfe0003,%r11d
    1118:	45 09 d8             	or     %r11d,%r8d
    111b:	41 89 c3             	mov    %eax,%r11d
    111e:	c1 e8 0d             	shr    $0xd,%eax
    1121:	41 c1 eb 06          	shr    $0x6,%r11d
    1125:	83 e0 08             	and    $0x8,%eax
    1128:	41 83 e3 04          	and    $0x4,%r11d
    112c:	45 09 d8             	or     %r11d,%r8d
    112f:	44 09 c0             	or     %r8d,%eax
    1132:	4c 8d 04 87          	lea    (%rdi,%rax,4),%r8
    1136:	41 8b 00             	mov    (%r8),%eax
    1139:	45 0f b7 00          	movzwl (%r8),%r8d
    113d:	c1 e8 10             	shr    $0x10,%eax
    1140:	66 45 89 02          	mov    %r8w,(%r10)
    1144:	41 88 42 02          	mov    %al,0x2(%r10)
    1148:	48 8d 42 05          	lea    0x5(%rdx),%rax
    114c:	48 39 c8             	cmp    %rcx,%rax
    114f:	0f 83 f3 00 00 00    	jae    1248 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1248>
    1155:	4e 8d 54 0e 0f       	lea    0xf(%rsi,%r9,1),%r10
    115a:	48 83 c2 06          	add    $0x6,%rdx
    115e:	41 0f b6 42 02       	movzbl 0x2(%r10),%eax
    1163:	45 0f b6 42 01       	movzbl 0x1(%r10),%r8d
    1168:	c1 e0 10             	shl    $0x10,%eax
    116b:	41 c1 e0 08          	shl    $0x8,%r8d
    116f:	44 09 c0             	or     %r8d,%eax
    1172:	45 0f b6 02          	movzbl (%r10),%r8d
    1176:	44 09 c0             	or     %r8d,%eax
    1179:	44 8d 04 00          	lea    (%rax,%rax,1),%r8d
    117d:	44 8d 1c 85 00 00 00 	lea    0x0(,%rax,4),%r11d
    1184:	00 
    1185:	41 81 e3 f0 03 00 00 	and    $0x3f0,%r11d
    118c:	41 81 e0 00 fc 01 00 	and    $0x1fc00,%r8d
    1193:	45 09 d8             	or     %r11d,%r8d
    1196:	41 89 c3             	mov    %eax,%r11d
    1199:	41 81 e3 03 00 fe 00 	and    $0xfe0003,%r11d
    11a0:	45 09 d8             	or     %r11d,%r8d
    11a3:	41 89 c3             	mov    %eax,%r11d
    11a6:	c1 e8 0d             	shr    $0xd,%eax
    11a9:	41 c1 eb 06          	shr    $0x6,%r11d
    11ad:	83 e0 08             	and    $0x8,%eax
    11b0:	41 83 e3 04          	and    $0x4,%r11d
    11b4:	45 09 d8             	or     %r11d,%r8d
    11b7:	44 09 c0             	or     %r8d,%eax
    11ba:	4c 8d 04 87          	lea    (%rdi,%rax,4),%r8
    11be:	41 8b 00             	mov    (%r8),%eax
    11c1:	45 0f b7 00          	movzwl (%r8),%r8d
    11c5:	c1 e8 10             	shr    $0x10,%eax
    11c8:	66 45 89 02          	mov    %r8w,(%r10)
    11cc:	41 88 42 02          	mov    %al,0x2(%r10)
    11d0:	48 39 ca             	cmp    %rcx,%rdx
    11d3:	73 73                	jae    1248 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1248>
    11d5:	4a 8d 4c 0e 12       	lea    0x12(%rsi,%r9,1),%rcx
    11da:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
    11de:	0f b6 51 02          	movzbl 0x2(%rcx),%edx
    11e2:	c1 e0 08             	shl    $0x8,%eax
    11e5:	c1 e2 10             	shl    $0x10,%edx
    11e8:	09 d0                	or     %edx,%eax
    11ea:	0f b6 11             	movzbl (%rcx),%edx
    11ed:	09 d0                	or     %edx,%eax
    11ef:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    11f6:	8d 34 00             	lea    (%rax,%rax,1),%esi
    11f9:	81 e6 00 fc 01 00    	and    $0x1fc00,%esi
    11ff:	81 e2 f0 03 00 00    	and    $0x3f0,%edx
    1205:	09 f2                	or     %esi,%edx
    1207:	89 c6                	mov    %eax,%esi
    1209:	81 e6 03 00 fe 00    	and    $0xfe0003,%esi
    120f:	09 f2                	or     %esi,%edx
    1211:	89 c6                	mov    %eax,%esi
    1213:	c1 e8 0d             	shr    $0xd,%eax
    1216:	c1 ee 06             	shr    $0x6,%esi
    1219:	83 e0 08             	and    $0x8,%eax
    121c:	83 e6 04             	and    $0x4,%esi
    121f:	09 f2                	or     %esi,%edx
    1221:	09 d0                	or     %edx,%eax
    1223:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    1227:	8b 02                	mov    (%rdx),%eax
    1229:	0f b7 12             	movzwl (%rdx),%edx
    122c:	c1 e8 10             	shr    $0x10,%eax
    122f:	66 89 11             	mov    %dx,(%rcx)
    1232:	88 41 02             	mov    %al,0x2(%rcx)
    1235:	c5 f8 77             	vzeroupper
    1238:	48 8d 65 e0          	lea    -0x20(%rbp),%rsp
    123c:	5b                   	pop    %rbx
    123d:	41 5c                	pop    %r12
    123f:	41 5d                	pop    %r13
    1241:	41 5e                	pop    %r14
    1243:	5d                   	pop    %rbp
    1244:	c3                   	ret
    1245:	0f 1f 00             	nopl   (%rax)
    1248:	c5 f8 77             	vzeroupper
    124b:	48 8d 65 e0          	lea    -0x20(%rbp),%rsp
    124f:	5b                   	pop    %rbx
    1250:	41 5c                	pop    %r12
    1252:	41 5d                	pop    %r13
    1254:	41 5e                	pop    %r14
    1256:	5d                   	pop    %rbp
    1257:	c3                   	ret
    1258:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    125f:	00 
    1260:	48 89 ca             	mov    %rcx,%rdx
    1263:	e9 e0 fa ff ff       	jmp    d48 <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd48>
    1268:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    126f:	00 
    1270:	c3                   	ret
    1271:	49 8d 40 28          	lea    0x28(%r8),%rax
    1275:	4c 89 c2             	mov    %r8,%rdx
    1278:	e9 a2 f6 ff ff       	jmp    91f <jshc_channel::avx2_chain_directtile(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x91f>
    127d:	0f 1f 00             	nopl   (%rax)

0000000000001280 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1280:	f3 0f 1e fa          	endbr64
    1284:	4d 85 c0             	test   %r8,%r8
    1287:	0f 84 d3 12 00 00    	je     2560 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12e0>
    128d:	55                   	push   %rbp
    128e:	b8 00 04 00 00       	mov    $0x400,%eax
    1293:	49 89 d1             	mov    %rdx,%r9
    1296:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    129a:	49 89 ca             	mov    %rcx,%r10
    129d:	48 89 e5             	mov    %rsp,%rbp
    12a0:	41 57                	push   %r15
    12a2:	41 56                	push   %r14
    12a4:	41 55                	push   %r13
    12a6:	41 54                	push   %r12
    12a8:	53                   	push   %rbx
    12a9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    12ad:	48 81 ec a8 00 00 00 	sub    $0xa8,%rsp
    12b4:	48 39 c2             	cmp    %rax,%rdx
    12b7:	48 0f 47 d0          	cmova  %rax,%rdx
    12bb:	31 c0                	xor    %eax,%eax
    12bd:	0f 1f 00             	nopl   (%rax)
    12c0:	41 0f 18 04 01       	prefetchnta (%r9,%rax,1)
    12c5:	48 83 c0 40          	add    $0x40,%rax
    12c9:	48 39 d0             	cmp    %rdx,%rax
    12cc:	72 f2                	jb     12c0 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
    12ce:	4d 89 cb             	mov    %r9,%r11
    12d1:	4c 89 d6             	mov    %r10,%rsi
    12d4:	31 c9                	xor    %ecx,%ecx
    12d6:	eb 7c                	jmp    1354 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd4>
    12d8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    12df:	00 
    12e0:	41 0f b6 43 01       	movzbl 0x1(%r11),%eax
    12e5:	41 0f b6 53 02       	movzbl 0x2(%r11),%edx
    12ea:	48 ff c1             	inc    %rcx
    12ed:	48 83 c6 03          	add    $0x3,%rsi
    12f1:	49 83 c3 03          	add    $0x3,%r11
    12f5:	c1 e2 10             	shl    $0x10,%edx
    12f8:	c1 e0 08             	shl    $0x8,%eax
    12fb:	09 d0                	or     %edx,%eax
    12fd:	41 0f b6 53 fd       	movzbl -0x3(%r11),%edx
    1302:	09 d0                	or     %edx,%eax
    1304:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    130b:	8d 1c 00             	lea    (%rax,%rax,1),%ebx
    130e:	81 e3 00 fc 01 00    	and    $0x1fc00,%ebx
    1314:	81 e2 f0 03 00 00    	and    $0x3f0,%edx
    131a:	09 da                	or     %ebx,%edx
    131c:	89 c3                	mov    %eax,%ebx
    131e:	81 e3 03 00 fe 00    	and    $0xfe0003,%ebx
    1324:	09 da                	or     %ebx,%edx
    1326:	89 c3                	mov    %eax,%ebx
    1328:	c1 e8 0d             	shr    $0xd,%eax
    132b:	c1 eb 06             	shr    $0x6,%ebx
    132e:	83 e0 08             	and    $0x8,%eax
    1331:	83 e3 04             	and    $0x4,%ebx
    1334:	09 da                	or     %ebx,%edx
    1336:	09 d0                	or     %edx,%eax
    1338:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    133c:	8b 02                	mov    (%rdx),%eax
    133e:	0f b7 12             	movzwl (%rdx),%edx
    1341:	c1 e8 10             	shr    $0x10,%eax
    1344:	66 89 56 fd          	mov    %dx,-0x3(%rsi)
    1348:	88 46 ff             	mov    %al,-0x1(%rsi)
    134b:	49 39 c8             	cmp    %rcx,%r8
    134e:	0f 84 04 12 00 00    	je     2558 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12d8>
    1354:	40 f6 c6 3f          	test   $0x3f,%sil
    1358:	75 86                	jne    12e0 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    135a:	48 8d 41 48          	lea    0x48(%rcx),%rax
    135e:	49 39 c0             	cmp    %rax,%r8
    1361:	0f 82 fa 11 00 00    	jb     2561 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12e1>
    1367:	be fc 00 fe 00       	mov    $0xfe00fc,%esi
    136c:	c5 fd 76 c0          	vpcmpeqd %ymm0,%ymm0,%ymm0
    1370:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    1374:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 137c <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfc>
    137b:	00 
    137c:	c5 f9 6e de          	vmovd  %esi,%xmm3
    1380:	be 03 01 01 00       	mov    $0x10103,%esi
    1385:	49 8d 14 02          	lea    (%r10,%rax,1),%rdx
    1389:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1391 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x111>
    1390:	00 
    1391:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
    1396:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 139e <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x11e>
    139d:	00 
    139e:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # 13a6 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x126>
    13a5:	00 
    13a6:	49 8d 84 01 00 04 00 	lea    0x400(%r9,%rax,1),%rax
    13ad:	00 
    13ae:	c5 fd 7f 9c 24 88 00 	vmovdqa %ymm3,0x88(%rsp)
    13b5:	00 00 
    13b7:	c5 f9 6e de          	vmovd  %esi,%xmm3
    13bb:	be 00 00 fe 00       	mov    $0xfe0000,%esi
    13c0:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 13c8 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x148>
    13c7:	00 
    13c8:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
    13cd:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 13d5 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x155>
    13d4:	00 
    13d5:	c5 fd 7f 5c 24 68    	vmovdqa %ymm3,0x68(%rsp)
    13db:	c5 e5 71 d0 0f       	vpsrlw $0xf,%ymm0,%ymm3
    13e0:	c5 fd 7f 5c 24 a8    	vmovdqa %ymm3,-0x58(%rsp)
    13e6:	c5 f9 6e de          	vmovd  %esi,%xmm3
    13ea:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
    13ef:	c5 fd 7f 5c 24 88    	vmovdqa %ymm3,-0x78(%rsp)
    13f5:	eb 0c                	jmp    1403 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x183>
    13f7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    13fe:	00 00 
    1400:	48 89 f1             	mov    %rsi,%rcx
    1403:	48 8d b1 96 01 00 00 	lea    0x196(%rcx),%rsi
    140a:	49 39 f0             	cmp    %rsi,%r8
    140d:	72 15                	jb     1424 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1a4>
    140f:	0f 18 00             	prefetchnta (%rax)
    1412:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1416:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    141d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    1424:	c5 fa 6f 80 00 fc ff 	vmovdqu -0x400(%rax),%xmm0
    142b:	ff 
    142c:	c5 fa 7e 88 10 fc ff 	vmovq  -0x3f0(%rax),%xmm1
    1433:	ff 
    1434:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    143b:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1441:	c5 7d 6f 5c 24 68    	vmovdqa 0x68(%rsp),%ymm11
    1447:	c5 7d 6f 84 24 88 00 	vmovdqa 0x88(%rsp),%ymm8
    144e:	00 00 
    1450:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1456:	c5 fd 6f 74 24 a8    	vmovdqa -0x58(%rsp),%ymm6
    145c:	c5 7d 6f 64 24 88    	vmovdqa -0x78(%rsp),%ymm12
    1462:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1468:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    146d:	c4 c1 7d db d3       	vpand  %ymm11,%ymm0,%ymm2
    1472:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
    1477:	c4 c1 7d db c4       	vpand  %ymm12,%ymm0,%ymm0
    147c:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
    1481:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    1486:	c5 ed f5 d6          	vpmaddwd %ymm6,%ymm2,%ymm2
    148a:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
    148f:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1493:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    1497:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    149d:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    14a1:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    14a7:	c4 c1 79 7e cd       	vmovd  %xmm1,%r13d
    14ac:	c4 c3 79 16 cf 02    	vpextrd $0x2,%xmm1,%r15d
    14b2:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
    14b9:	00 
    14ba:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    14c0:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    14c6:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    14cc:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    14d2:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    14d8:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    14de:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    14e5:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    14ec:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    14f0:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    14f5:	48 8b 9c 24 88 00 00 	mov    0x88(%rsp),%rbx
    14fc:	00 
    14fd:	c5 79 6e 14 9f       	vmovd  (%rdi,%rbx,4),%xmm10
    1502:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    1509:	c4 63 29 22 14 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm10,%xmm10
    1510:	c5 a9 6c c9          	vpunpcklqdq %xmm1,%xmm10,%xmm1
    1514:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    151a:	c5 fa 6f 80 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm0
    1521:	ff 
    1522:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
    1527:	c4 62 45 36 d1       	vpermd %ymm1,%ymm7,%ymm10
    152c:	c5 fa 7e 88 68 fb ff 	vmovq  -0x498(%rax),%xmm1
    1533:	ff 
    1534:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    153a:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1540:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1545:	c4 c1 7d db d3       	vpand  %ymm11,%ymm0,%ymm2
    154a:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
    154f:	c4 c1 7d db c4       	vpand  %ymm12,%ymm0,%ymm0
    1554:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
    1559:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    155e:	c5 ed f5 d6          	vpmaddwd %ymm6,%ymm2,%ymm2
    1562:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
    1567:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    156b:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    156f:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1575:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    1579:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    157f:	c4 c1 79 7e cd       	vmovd  %xmm1,%r13d
    1584:	c4 c3 79 16 cf 02    	vpextrd $0x2,%xmm1,%r15d
    158a:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
    1591:	00 
    1592:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1598:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    159e:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    15a4:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    15aa:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    15b0:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    15b6:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    15bd:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    15c4:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    15c8:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    15cd:	48 8b 9c 24 88 00 00 	mov    0x88(%rsp),%rbx
    15d4:	00 
    15d5:	c5 f9 6e 1c 9f       	vmovd  (%rdi,%rbx,4),%xmm3
    15da:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    15e1:	c4 e3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm3,%xmm3
    15e8:	c5 e1 6c c9          	vpunpcklqdq %xmm1,%xmm3,%xmm1
    15ec:	c5 fd 6f de          	vmovdqa %ymm6,%ymm3
    15f0:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    15f6:	c5 fa 6f 80 70 fb ff 	vmovdqu -0x490(%rax),%xmm0
    15fd:	ff 
    15fe:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
    1603:	c4 e2 45 36 d1       	vpermd %ymm1,%ymm7,%ymm2
    1608:	c5 fa 7e 88 80 fb ff 	vmovq  -0x480(%rax),%xmm1
    160f:	ff 
    1610:	c5 fd 7f 54 24 48    	vmovdqa %ymm2,0x48(%rsp)
    1616:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    161c:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1622:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1627:	c4 c1 7d db d3       	vpand  %ymm11,%ymm0,%ymm2
    162c:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
    1631:	c4 c1 7d db c4       	vpand  %ymm12,%ymm0,%ymm0
    1636:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
    163b:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    1640:	c5 ed f5 d6          	vpmaddwd %ymm6,%ymm2,%ymm2
    1644:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
    1649:	c5 7d 7f e6          	vmovdqa %ymm12,%ymm6
    164d:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1651:	c4 41 7d 6f e3       	vmovdqa %ymm11,%ymm12
    1656:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    165a:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1660:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    1664:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    166a:	c4 c1 79 7e cd       	vmovd  %xmm1,%r13d
    166f:	c4 c3 79 16 cf 02    	vpextrd $0x2,%xmm1,%r15d
    1675:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    167b:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
    1682:	00 
    1683:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1689:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    168f:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1695:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    169b:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    16a1:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    16a8:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    16af:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    16b3:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    16b8:	48 8b 9c 24 88 00 00 	mov    0x88(%rsp),%rbx
    16bf:	00 
    16c0:	c5 f9 6e 14 9f       	vmovd  (%rdi,%rbx,4),%xmm2
    16c5:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    16cc:	c4 e3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm2,%xmm2
    16d3:	c5 e9 6c c9          	vpunpcklqdq %xmm1,%xmm2,%xmm1
    16d7:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    16dd:	c5 fa 7e 80 98 fb ff 	vmovq  -0x468(%rax),%xmm0
    16e4:	ff 
    16e5:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
    16ea:	c4 e2 45 36 c9       	vpermd %ymm1,%ymm7,%ymm1
    16ef:	c5 fd 7f 4c 24 28    	vmovdqa %ymm1,0x28(%rsp)
    16f5:	c5 fa 6f 88 88 fb ff 	vmovdqu -0x478(%rax),%xmm1
    16fc:	ff 
    16fd:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
    1703:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1709:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
    170e:	c4 c1 75 db d3       	vpand  %ymm11,%ymm1,%ymm2
    1713:	c4 e2 75 00 c4       	vpshufb %ymm4,%ymm1,%ymm0
    1718:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
    171c:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
    1721:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    1726:	c5 7d 6f de          	vmovdqa %ymm6,%ymm11
    172a:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
    172e:	c4 c1 7d f5 c7       	vpmaddwd %ymm15,%ymm0,%ymm0
    1733:	c5 7d 7f c6          	vmovdqa %ymm8,%ymm6
    1737:	c5 fd eb c2          	vpor   %ymm2,%ymm0,%ymm0
    173b:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    173f:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1745:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    1749:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    174f:	c4 c1 79 7e cd       	vmovd  %xmm1,%r13d
    1754:	c4 c3 79 16 cf 02    	vpextrd $0x2,%xmm1,%r15d
    175a:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
    1761:	00 
    1762:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1768:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    176e:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1774:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    177a:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1780:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    1786:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    178d:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    1794:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1798:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    179d:	48 8b 9c 24 88 00 00 	mov    0x88(%rsp),%rbx
    17a4:	00 
    17a5:	c5 79 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm9
    17aa:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    17b1:	c4 63 31 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm9,%xmm9
    17b8:	c5 b1 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm1
    17bc:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    17c2:	c5 fa 6f 80 a0 fb ff 	vmovdqu -0x460(%rax),%xmm0
    17c9:	ff 
    17ca:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
    17cf:	c4 62 45 36 c9       	vpermd %ymm1,%ymm7,%ymm9
    17d4:	c5 fa 7e 88 b0 fb ff 	vmovq  -0x450(%rax),%xmm1
    17db:	ff 
    17dc:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    17e2:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    17e8:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    17ed:	c4 c1 7d db d4       	vpand  %ymm12,%ymm0,%ymm2
    17f2:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
    17f7:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    17fc:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
    1801:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    1806:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
    180a:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
    180f:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1813:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    1817:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    181d:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    1821:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    1827:	c4 c1 79 7e cd       	vmovd  %xmm1,%r13d
    182c:	c4 c3 79 16 cf 02    	vpextrd $0x2,%xmm1,%r15d
    1832:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
    1839:	00 
    183a:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1840:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    1846:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    184c:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    1852:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1858:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    185e:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    1865:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    186c:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1870:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    1875:	48 8b 9c 24 88 00 00 	mov    0x88(%rsp),%rbx
    187c:	00 
    187d:	c4 a3 71 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm1,%xmm1
    1884:	c5 79 6e 04 9f       	vmovd  (%rdi,%rbx,4),%xmm8
    1889:	c4 63 39 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm8,%xmm8
    1890:	c5 b9 6c c9          	vpunpcklqdq %xmm1,%xmm8,%xmm1
    1894:	c5 7d 6f c6          	vmovdqa %ymm6,%ymm8
    1898:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    189e:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
    18a3:	c4 e2 45 36 c1       	vpermd %ymm1,%ymm7,%ymm0
    18a8:	c5 fa 7e 88 c8 fb ff 	vmovq  -0x438(%rax),%xmm1
    18af:	ff 
    18b0:	c5 fd 7f 44 24 08    	vmovdqa %ymm0,0x8(%rsp)
    18b6:	c5 fa 6f 80 b8 fb ff 	vmovdqu -0x448(%rax),%xmm0
    18bd:	ff 
    18be:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    18c4:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    18ca:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    18cf:	c4 c1 7d db d4       	vpand  %ymm12,%ymm0,%ymm2
    18d4:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
    18d9:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    18de:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
    18e2:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    18e7:	c5 7d 6f e3          	vmovdqa %ymm3,%ymm12
    18eb:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
    18ef:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
    18f4:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    18f8:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    18fc:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1902:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    1906:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    190c:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
    1913:	00 
    1914:	c4 c1 79 7e cd       	vmovd  %xmm1,%r13d
    1919:	c4 c3 79 16 cf 02    	vpextrd $0x2,%xmm1,%r15d
    191f:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    1925:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    192b:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1931:	c4 a1 79 6e 04 af    	vmovd  (%rdi,%r13,4),%xmm0
    1937:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    193d:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    1943:	c5 f9 6e 34 9f       	vmovd  (%rdi,%rbx,4),%xmm6
    1948:	c4 a3 79 22 04 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm0,%xmm0
    194f:	48 8b 9c 24 88 00 00 	mov    0x88(%rsp),%rbx
    1956:	00 
    1957:	c5 7d 7f 84 24 88 00 	vmovdqa %ymm8,0x88(%rsp)
    195e:	00 00 
    1960:	c4 41 7d 6f c3       	vmovdqa %ymm11,%ymm8
    1965:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    196c:	c4 a3 49 22 34 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm6,%xmm6
    1973:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1977:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    197c:	c4 e3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm1,%xmm1
    1983:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1987:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    198d:	c5 fa 6f 80 d0 fb ff 	vmovdqu -0x430(%rax),%xmm0
    1994:	ff 
    1995:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
    199a:	c4 e2 45 36 f1       	vpermd %ymm1,%ymm7,%ymm6
    199f:	c5 fa 7e 88 e0 fb ff 	vmovq  -0x420(%rax),%xmm1
    19a6:	ff 
    19a7:	c5 fd 7f 74 24 e8    	vmovdqa %ymm6,-0x18(%rsp)
    19ad:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    19b3:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    19b9:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    19be:	c5 fd db 54 24 68    	vpand  0x68(%rsp),%ymm0,%ymm2
    19c4:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
    19c9:	c4 c1 7d db c3       	vpand  %ymm11,%ymm0,%ymm0
    19ce:	c5 f5 db 8c 24 88 00 	vpand  0x88(%rsp),%ymm1,%ymm1
    19d5:	00 00 
    19d7:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    19dc:	c5 ed f5 d3          	vpmaddwd %ymm3,%ymm2,%ymm2
    19e0:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
    19e5:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    19e9:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    19ed:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    19f3:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    19f7:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    19fd:	48 89 5c 24 e0       	mov    %rbx,-0x20(%rsp)
    1a02:	c4 c1 79 7e cd       	vmovd  %xmm1,%r13d
    1a07:	c4 c3 79 16 cf 02    	vpextrd $0x2,%xmm1,%r15d
    1a0d:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    1a13:	c4 a1 79 6e 34 af    	vmovd  (%rdi,%r13,4),%xmm6
    1a19:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1a1f:	c4 a1 79 6e 04 bf    	vmovd  (%rdi,%r15,4),%xmm0
    1a25:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    1a2b:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    1a31:	c5 79 6e 1c 9f       	vmovd  (%rdi,%rbx,4),%xmm11
    1a36:	c5 fa 6f 88 e8 fb ff 	vmovdqu -0x418(%rax),%xmm1
    1a3d:	ff 
    1a3e:	c4 a3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm0,%xmm0
    1a45:	c4 a3 49 22 34 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm6,%xmm6
    1a4c:	48 8b 5c 24 e0       	mov    -0x20(%rsp),%rbx
    1a51:	c4 23 21 22 1c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm11,%xmm11
    1a58:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
    1a5c:	c5 f9 6e 04 9f       	vmovd  (%rdi,%rbx,4),%xmm0
    1a61:	c4 e3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm0,%xmm0
    1a68:	c5 fa 7e 90 f8 fb ff 	vmovq  -0x408(%rax),%xmm2
    1a6f:	ff 
    1a70:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
    1a76:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
    1a7b:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1a81:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1a87:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
    1a8c:	c4 c2 7d 00 c6       	vpshufb %ymm14,%ymm0,%ymm0
    1a91:	c5 f5 db 5c 24 68    	vpand  0x68(%rsp),%ymm1,%ymm3
    1a97:	c4 e2 75 00 d4       	vpshufb %ymm4,%ymm1,%ymm2
    1a9c:	c4 c1 75 db c8       	vpand  %ymm8,%ymm1,%ymm1
    1aa1:	c5 ed db 94 24 88 00 	vpand  0x88(%rsp),%ymm2,%ymm2
    1aa8:	00 00 
    1aaa:	c4 41 79 6f c2       	vmovdqa %xmm10,%xmm8
    1aaf:	c4 e2 45 36 c0       	vpermd %ymm0,%ymm7,%ymm0
    1ab4:	c4 c2 65 04 dd       	vpmaddubsw %ymm13,%ymm3,%ymm3
    1ab9:	c4 c1 65 f5 dc       	vpmaddwd %ymm12,%ymm3,%ymm3
    1abe:	c4 c1 6d f5 d7       	vpmaddwd %ymm15,%ymm2,%ymm2
    1ac3:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
    1ac7:	c4 63 7d 39 d3 01    	vextracti128 $0x1,%ymm10,%xmm3
    1acd:	c5 7d 6f 54 24 28    	vmovdqa 0x28(%rsp),%ymm10
    1ad3:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1ad7:	c4 e3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm2
    1add:	c5 f9 7e cb          	vmovd  %xmm1,%ebx
    1ae1:	c4 e3 79 16 ce 01    	vpextrd $0x1,%xmm1,%esi
    1ae7:	48 89 5c 24 e0       	mov    %rbx,-0x20(%rsp)
    1aec:	c4 c1 79 7e d5       	vmovd  %xmm2,%r13d
    1af1:	c4 c3 79 16 d7 02    	vpextrd $0x2,%xmm2,%r15d
    1af7:	c4 e3 79 16 cb 02    	vpextrd $0x2,%xmm1,%ebx
    1afd:	c4 a1 79 6e 34 bf    	vmovd  (%rdi,%r15,4),%xmm6
    1b03:	c4 21 79 6e 1c af    	vmovd  (%rdi,%r13,4),%xmm11
    1b09:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1b0f:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    1b15:	c5 79 6e 24 9f       	vmovd  (%rdi,%rbx,4),%xmm12
    1b1a:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1b20:	c5 fd 6f 54 24 48    	vmovdqa 0x48(%rsp),%ymm2
    1b26:	c4 63 7d 39 d1 01    	vextracti128 $0x1,%ymm10,%xmm1
    1b2c:	c4 a3 49 22 34 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm6,%xmm6
    1b33:	c4 23 21 22 1c a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm11,%xmm11
    1b3a:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    1b3f:	48 8b 5c 24 e0       	mov    -0x20(%rsp),%rbx
    1b44:	c4 23 19 22 24 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm12,%xmm12
    1b4b:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    1b51:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1b56:	c5 21 6c de          	vpunpcklqdq %xmm6,%xmm11,%xmm11
    1b5a:	c4 43 31 0f ca 08    	vpalignr $0x8,%xmm10,%xmm9,%xmm9
    1b60:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
    1b64:	c5 f9 6e 34 9f       	vmovd  (%rdi,%rbx,4),%xmm6
    1b69:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1b6f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1b75:	4c 8d 99 88 00 00 00 	lea    0x88(%rcx),%r11
    1b7c:	c4 e3 49 22 34 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm6,%xmm6
    1b83:	48 8d 71 40          	lea    0x40(%rcx),%rsi
    1b87:	c4 c1 49 6c f4       	vpunpcklqdq %xmm12,%xmm6,%xmm6
    1b8c:	c5 79 6f 64 24 28    	vmovdqa 0x28(%rsp),%xmm12
    1b92:	c5 fd e7 4a 80       	vmovntdq %ymm1,-0x80(%rdx)
    1b97:	c4 c3 4d 38 f3 01    	vinserti128 $0x1,%xmm11,%ymm6,%ymm6
    1b9d:	c5 79 6f da          	vmovdqa %xmm2,%xmm11
    1ba1:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1ba7:	c4 c1 61 6c db       	vpunpcklqdq %xmm11,%xmm3,%xmm3
    1bac:	c4 c3 69 0f d3 08    	vpalignr $0x8,%xmm11,%xmm2,%xmm2
    1bb2:	c4 c2 4d 00 f6       	vpshufb %ymm14,%ymm6,%ymm6
    1bb7:	c4 63 3d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm8,%ymm8
    1bbd:	c4 c3 6d 38 d4 01    	vinserti128 $0x1,%xmm12,%ymm2,%ymm2
    1bc3:	c4 e2 45 36 f6       	vpermd %ymm6,%ymm7,%ymm6
    1bc8:	c5 7d e7 82 40 ff ff 	vmovntdq %ymm8,-0xc0(%rdx)
    1bcf:	ff 
    1bd0:	c5 fd e7 92 60 ff ff 	vmovntdq %ymm2,-0xa0(%rdx)
    1bd7:	ff 
    1bd8:	c5 fd 6f 5c 24 08    	vmovdqa 0x8(%rsp),%ymm3
    1bde:	c5 fd 6f 4c 24 e8    	vmovdqa -0x18(%rsp),%ymm1
    1be4:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
    1be8:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1bee:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1bf2:	c5 f9 6f d3          	vmovdqa %xmm3,%xmm2
    1bf6:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1bfc:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    1c02:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1c08:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
    1c0d:	c4 c1 61 6c d9       	vpunpcklqdq %xmm9,%xmm3,%xmm3
    1c12:	c4 c3 49 0f f0 08    	vpalignr $0x8,%xmm8,%xmm6,%xmm6
    1c18:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
    1c1e:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
    1c24:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    1c2a:	c5 fd e7 4a c0       	vmovntdq %ymm1,-0x40(%rdx)
    1c2f:	c5 fd e7 52 a0       	vmovntdq %ymm2,-0x60(%rdx)
    1c34:	c5 fd e7 42 e0       	vmovntdq %ymm0,-0x20(%rdx)
    1c39:	4d 39 d8             	cmp    %r11,%r8
    1c3c:	0f 83 be f7 ff ff    	jae    1400 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x180>
    1c42:	0f ae f8             	sfence
    1c45:	48 8d 41 68          	lea    0x68(%rcx),%rax
    1c49:	49 39 c0             	cmp    %rax,%r8
    1c4c:	0f 82 48 04 00 00    	jb     209a <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe1a>
    1c52:	b9 fc 00 fe 00       	mov    $0xfe00fc,%ecx
    1c57:	48 8d 14 76          	lea    (%rsi,%rsi,2),%rdx
    1c5b:	c4 41 3d 76 c0       	vpcmpeqd %ymm8,%ymm8,%ymm8
    1c60:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1c68 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x9e8>
    1c67:	00 
    1c68:	c5 f9 6e d9          	vmovd  %ecx,%xmm3
    1c6c:	b9 03 01 01 00       	mov    $0x10103,%ecx
    1c71:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1c79 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x9f9>
    1c78:	00 
    1c79:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 1c81 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa01>
    1c80:	00 
    1c81:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
    1c86:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # 1c8e <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa0e>
    1c8d:	00 
    1c8e:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 1c96 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa16>
    1c95:	00 
    1c96:	49 8d 04 11          	lea    (%r9,%rdx,1),%rax
    1c9a:	c5 fd 7f 9c 24 88 00 	vmovdqa %ymm3,0x88(%rsp)
    1ca1:	00 00 
    1ca3:	c5 f9 6e d9          	vmovd  %ecx,%xmm3
    1ca7:	b9 00 00 fe 00       	mov    $0xfe0000,%ecx
    1cac:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 1cb4 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa34>
    1cb3:	00 
    1cb4:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
    1cb9:	c4 c1 3d 71 d0 0f    	vpsrlw $0xf,%ymm8,%ymm8
    1cbf:	c5 79 6e e1          	vmovd  %ecx,%xmm12
    1cc3:	4c 01 d2             	add    %r10,%rdx
    1cc6:	c5 fd 7f 5c 24 28    	vmovdqa %ymm3,0x28(%rsp)
    1ccc:	c4 42 7d 58 e4       	vpbroadcastd %xmm12,%ymm12
    1cd1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1cd8:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
    1cdc:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
    1ce1:	48 83 c2 60          	add    $0x60,%rdx
    1ce5:	48 83 c0 60          	add    $0x60,%rax
    1ce9:	c5 7d 6f 4c 24 28    	vmovdqa 0x28(%rsp),%ymm9
    1cef:	c5 7d 6f 9c 24 88 00 	vmovdqa 0x88(%rsp),%ymm11
    1cf6:	00 00 
    1cf8:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1cfe:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1d04:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1d09:	c4 c1 7d db d1       	vpand  %ymm9,%ymm0,%ymm2
    1d0e:	c4 e2 7d 00 cc       	vpshufb %ymm4,%ymm0,%ymm1
    1d13:	c5 9d db c0          	vpand  %ymm0,%ymm12,%ymm0
    1d17:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
    1d1c:	c4 c2 6d 04 d5       	vpmaddubsw %ymm13,%ymm2,%ymm2
    1d21:	c4 c1 6d f5 d0       	vpmaddwd %ymm8,%ymm2,%ymm2
    1d26:	c4 c1 75 f5 cf       	vpmaddwd %ymm15,%ymm1,%ymm1
    1d2b:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1d2f:	c5 fa 7e 50 c8       	vmovq  -0x38(%rax),%xmm2
    1d34:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
    1d38:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
    1d3d:	c4 e3 7d 39 44 24 68 	vextracti128 $0x1,%ymm0,0x68(%rsp)
    1d44:	01 
    1d45:	c4 e3 69 0f d1 0c    	vpalignr $0xc,%xmm1,%xmm2,%xmm2
    1d4b:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1d51:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
    1d56:	c4 c1 75 db d9       	vpand  %ymm9,%ymm1,%ymm3
    1d5b:	c4 e2 75 00 d4       	vpshufb %ymm4,%ymm1,%ymm2
    1d60:	c5 9d db c9          	vpand  %ymm1,%ymm12,%ymm1
    1d64:	c4 c1 6d db d3       	vpand  %ymm11,%ymm2,%ymm2
    1d69:	c4 c2 65 04 dd       	vpmaddubsw %ymm13,%ymm3,%ymm3
    1d6e:	c4 c1 65 f5 d8       	vpmaddwd %ymm8,%ymm3,%ymm3
    1d73:	c4 c1 6d f5 d7       	vpmaddwd %ymm15,%ymm2,%ymm2
    1d78:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
    1d7c:	c5 fa 6f 58 d0       	vmovdqu -0x30(%rax),%xmm3
    1d81:	c5 f5 eb ca          	vpor   %ymm2,%ymm1,%ymm1
    1d85:	c5 fa 7e 50 e0       	vmovq  -0x20(%rax),%xmm2
    1d8a:	c4 c3 7d 39 ca 01    	vextracti128 $0x1,%ymm1,%xmm10
    1d90:	c4 e3 69 0f d3 0c    	vpalignr $0xc,%xmm3,%xmm2,%xmm2
    1d96:	c4 e3 65 38 da 01    	vinserti128 $0x1,%xmm2,%ymm3,%ymm3
    1d9c:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
    1da1:	c4 e2 65 00 d4       	vpshufb %ymm4,%ymm3,%ymm2
    1da6:	c4 c1 65 db f1       	vpand  %ymm9,%ymm3,%ymm6
    1dab:	c5 9d db db          	vpand  %ymm3,%ymm12,%ymm3
    1daf:	c5 ed db 94 24 88 00 	vpand  0x88(%rsp),%ymm2,%ymm2
    1db6:	00 00 
    1db8:	c4 c2 4d 04 f5       	vpmaddubsw %ymm13,%ymm6,%ymm6
    1dbd:	c4 c1 4d f5 f0       	vpmaddwd %ymm8,%ymm6,%ymm6
    1dc2:	c4 c1 6d f5 d7       	vpmaddwd %ymm15,%ymm2,%ymm2
    1dc7:	c5 ed eb d6          	vpor   %ymm6,%ymm2,%ymm2
    1dcb:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
    1dd0:	c5 ed eb d3          	vpor   %ymm3,%ymm2,%ymm2
    1dd4:	c5 fa 6f 58 e8       	vmovdqu -0x18(%rax),%xmm3
    1dd9:	c4 c3 7d 39 d3 01    	vextracti128 $0x1,%ymm2,%xmm11
    1ddf:	c4 e3 49 0f f3 0c    	vpalignr $0xc,%xmm3,%xmm6,%xmm6
    1de5:	c4 e3 65 38 de 01    	vinserti128 $0x1,%xmm6,%ymm3,%ymm3
    1deb:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
    1df0:	c4 e2 65 00 f4       	vpshufb %ymm4,%ymm3,%ymm6
    1df5:	c4 41 65 db c9       	vpand  %ymm9,%ymm3,%ymm9
    1dfa:	c5 9d db db          	vpand  %ymm3,%ymm12,%ymm3
    1dfe:	c5 cd db b4 24 88 00 	vpand  0x88(%rsp),%ymm6,%ymm6
    1e05:	00 00 
    1e07:	c4 42 35 04 cd       	vpmaddubsw %ymm13,%ymm9,%ymm9
    1e0c:	c4 41 35 f5 c8       	vpmaddwd %ymm8,%ymm9,%ymm9
    1e11:	c4 c1 4d f5 f7       	vpmaddwd %ymm15,%ymm6,%ymm6
    1e16:	c4 c1 4d eb f1       	vpor   %ymm9,%ymm6,%ymm6
    1e1b:	c5 e5 eb de          	vpor   %ymm6,%ymm3,%ymm3
    1e1f:	c4 e3 7d 39 de 01    	vextracti128 $0x1,%ymm3,%xmm6
    1e25:	c5 f9 7e db          	vmovd  %xmm3,%ebx
    1e29:	c4 e3 79 16 d9 01    	vpextrd $0x1,%xmm3,%ecx
    1e2f:	48 89 5c 24 48       	mov    %rbx,0x48(%rsp)
    1e34:	c4 c3 79 16 f7 02    	vpextrd $0x2,%xmm6,%r15d
    1e3a:	c4 c1 79 7e f5       	vmovd  %xmm6,%r13d
    1e3f:	c4 e3 79 16 db 02    	vpextrd $0x2,%xmm3,%ebx
    1e45:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    1e4b:	c4 c3 79 16 f4 01    	vpextrd $0x1,%xmm6,%r12d
    1e51:	c4 a1 79 6e 1c bf    	vmovd  (%rdi,%r15,4),%xmm3
    1e57:	c4 c3 79 16 f6 03    	vpextrd $0x3,%xmm6,%r14d
    1e5d:	c4 a1 79 6e 34 af    	vmovd  (%rdi,%r13,4),%xmm6
    1e63:	c5 79 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm9
    1e68:	c4 41 79 7e dd       	vmovd  %xmm11,%r13d
    1e6d:	c4 43 79 16 df 02    	vpextrd $0x2,%xmm11,%r15d
    1e73:	c4 a3 61 22 1c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm3,%xmm3
    1e7a:	48 8b 5c 24 48       	mov    0x48(%rsp),%rbx
    1e7f:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
    1e85:	c4 a3 49 22 34 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm6,%xmm6
    1e8c:	c4 23 31 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm9,%xmm9
    1e93:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    1e99:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
    1e9f:	c5 c9 6c f3          	vpunpcklqdq %xmm3,%xmm6,%xmm6
    1ea3:	c5 f9 6e 1c 9f       	vmovd  (%rdi,%rbx,4),%xmm3
    1ea8:	c5 f9 7e d3          	vmovd  %xmm2,%ebx
    1eac:	48 89 5c 24 48       	mov    %rbx,0x48(%rsp)
    1eb1:	c4 e3 79 16 d3 02    	vpextrd $0x2,%xmm2,%ebx
    1eb7:	c4 e3 61 22 1c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm3,%xmm3
    1ebe:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    1ec4:	c4 a1 79 6e 14 bf    	vmovd  (%rdi,%r15,4),%xmm2
    1eca:	c4 43 79 16 d7 02    	vpextrd $0x2,%xmm10,%r15d
    1ed0:	c4 c1 61 6c d9       	vpunpcklqdq %xmm9,%xmm3,%xmm3
    1ed5:	c4 a3 69 22 14 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm2,%xmm2
    1edc:	c5 79 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm9
    1ee1:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    1ee7:	c4 e3 65 38 de 01    	vinserti128 $0x1,%xmm6,%ymm3,%ymm3
    1eed:	c4 a1 79 6e 34 af    	vmovd  (%rdi,%r13,4),%xmm6
    1ef3:	48 8b 5c 24 48       	mov    0x48(%rsp),%rbx
    1ef8:	c4 41 79 7e d5       	vmovd  %xmm10,%r13d
    1efd:	c4 23 31 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm9,%xmm9
    1f04:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1f0a:	c4 c2 65 00 de       	vpshufb %ymm14,%ymm3,%ymm3
    1f0f:	c4 a3 49 22 34 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm6,%xmm6
    1f16:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    1f1c:	c4 e2 45 36 db       	vpermd %ymm3,%ymm7,%ymm3
    1f21:	c5 79 6f db          	vmovdqa %xmm3,%xmm11
    1f25:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    1f2b:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
    1f2f:	c5 f9 6e 14 9f       	vmovd  (%rdi,%rbx,4),%xmm2
    1f34:	c4 c3 61 0f db 08    	vpalignr $0x8,%xmm11,%xmm3,%xmm3
    1f3a:	c5 f9 7e cb          	vmovd  %xmm1,%ebx
    1f3e:	c4 e3 69 22 14 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm2,%xmm2
    1f45:	48 89 5c 24 48       	mov    %rbx,0x48(%rsp)
    1f4a:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    1f50:	c4 e3 79 16 cb 02    	vpextrd $0x2,%xmm1,%ebx
    1f56:	c4 a1 79 6e 0c bf    	vmovd  (%rdi,%r15,4),%xmm1
    1f5c:	44 8b 7c 24 70       	mov    0x70(%rsp),%r15d
    1f61:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1f66:	c5 79 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm9
    1f6b:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    1f71:	c4 a1 79 6e 34 af    	vmovd  (%rdi,%r13,4),%xmm6
    1f77:	c4 a3 71 22 0c b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm1,%xmm1
    1f7e:	48 8b 5c 24 48       	mov    0x48(%rsp),%rbx
    1f83:	c4 23 31 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm9,%xmm9
    1f8a:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1f90:	c4 c2 6d 00 d6       	vpshufb %ymm14,%ymm2,%ymm2
    1f95:	c4 a3 49 22 34 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm6,%xmm6
    1f9c:	44 8b 6c 24 68       	mov    0x68(%rsp),%r13d
    1fa1:	c4 e2 45 36 d2       	vpermd %ymm2,%ymm7,%ymm2
    1fa6:	44 8b 64 24 6c       	mov    0x6c(%rsp),%r12d
    1fab:	44 8b 74 24 74       	mov    0x74(%rsp),%r14d
    1fb0:	c5 79 6f d2          	vmovdqa %xmm2,%xmm10
    1fb4:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1fba:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    1fbe:	c5 f9 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm1
    1fc3:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    1fc7:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    1fcc:	48 89 5c 24 48       	mov    %rbx,0x48(%rsp)
    1fd1:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    1fd7:	c4 e3 6d 38 d3 01    	vinserti128 $0x1,%xmm3,%ymm2,%ymm2
    1fdd:	c4 e3 71 22 0c 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm1,%xmm1
    1fe4:	c4 e3 79 16 c1 01    	vpextrd $0x1,%xmm0,%ecx
    1fea:	c4 a1 79 6e 04 bf    	vmovd  (%rdi,%r15,4),%xmm0
    1ff0:	c4 c1 71 6c c9       	vpunpcklqdq %xmm9,%xmm1,%xmm1
    1ff5:	c4 a3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm0,%xmm0
    1ffc:	c5 79 6e 0c 9f       	vmovd  (%rdi,%rbx,4),%xmm9
    2001:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
    2007:	c4 a1 79 6e 34 af    	vmovd  (%rdi,%r13,4),%xmm6
    200d:	48 8b 5c 24 48       	mov    0x48(%rsp),%rbx
    2012:	c4 23 31 22 0c 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm9,%xmm9
    2019:	c4 c2 75 00 ce       	vpshufb %ymm14,%ymm1,%ymm1
    201e:	c4 a3 49 22 34 a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm6,%xmm6
    2025:	c4 e2 45 36 c9       	vpermd %ymm1,%ymm7,%ymm1
    202a:	c5 c9 6c f0          	vpunpcklqdq %xmm0,%xmm6,%xmm6
    202e:	c5 f9 6e 04 9f       	vmovd  (%rdi,%rbx,4),%xmm0
    2033:	c4 e3 79 22 04 8f 01 	vpinsrd $0x1,(%rdi,%rcx,4),%xmm0,%xmm0
    203a:	48 8d 4e 48          	lea    0x48(%rsi),%rcx
    203e:	c5 fe 7f 52 e0       	vmovdqu %ymm2,-0x20(%rdx)
    2043:	48 83 c6 20          	add    $0x20,%rsi
    2047:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    204c:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    2050:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    2056:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    205c:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    2062:	c4 c2 7d 00 c6       	vpshufb %ymm14,%ymm0,%ymm0
    2067:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
    206d:	c4 e2 45 36 c0       	vpermd %ymm0,%ymm7,%ymm0
    2072:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    2077:	c5 f9 6f f0          	vmovdqa %xmm0,%xmm6
    207b:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    2081:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    2086:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    208c:	c5 fe 7f 72 a0       	vmovdqu %ymm6,-0x60(%rdx)
    2091:	49 39 c8             	cmp    %rcx,%r8
    2094:	0f 83 3e fc ff ff    	jae    1cd8 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa58>
    209a:	48 8d 56 08          	lea    0x8(%rsi),%rdx
    209e:	49 39 d0             	cmp    %rdx,%r8
    20a1:	0f 82 6f 01 00 00    	jb     2216 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf96>
    20a7:	48 8d 04 76          	lea    (%rsi,%rsi,2),%rax
    20ab:	be fc 00 fe 00       	mov    $0xfe00fc,%esi
    20b0:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
    20b4:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 20bc <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe3c>
    20bb:	00 
    20bc:	c5 f9 6e f6          	vmovd  %esi,%xmm6
    20c0:	be 03 01 01 00       	mov    $0x10103,%esi
    20c5:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 20cd <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe4d>
    20cc:	00 
    20cd:	c5 7d 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm15        # 20d5 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe55>
    20d4:	00 
    20d5:	c5 f9 6e de          	vmovd  %esi,%xmm3
    20d9:	be 00 00 fe 00       	mov    $0xfe0000,%esi
    20de:	c5 7d 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm13        # 20e6 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe66>
    20e5:	00 
    20e6:	c5 7d 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm14        # 20ee <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe6e>
    20ed:	00 
    20ee:	c5 f9 6e d6          	vmovd  %esi,%xmm2
    20f2:	49 8d 0c 01          	lea    (%r9,%rax,1),%rcx
    20f6:	c4 e2 7d 58 f6       	vpbroadcastd %xmm6,%ymm6
    20fb:	4c 01 d0             	add    %r10,%rax
    20fe:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
    2103:	c5 f5 71 d1 0f       	vpsrlw $0xf,%ymm1,%ymm1
    2108:	c4 e2 7d 58 d2       	vpbroadcastd %xmm2,%ymm2
    210d:	0f 1f 00             	nopl   (%rax)
    2110:	c5 fa 6f 01          	vmovdqu (%rcx),%xmm0
    2114:	c5 fa 7e 79 10       	vmovq  0x10(%rcx),%xmm7
    2119:	48 83 c0 18          	add    $0x18,%rax
    211d:	48 83 c1 18          	add    $0x18,%rcx
    2121:	c4 e3 41 0f f8 0c    	vpalignr $0xc,%xmm0,%xmm7,%xmm7
    2127:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    212d:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    2132:	c4 e2 7d 00 fc       	vpshufb %ymm4,%ymm0,%ymm7
    2137:	c5 65 db c0          	vpand  %ymm0,%ymm3,%ymm8
    213b:	c5 ed db c0          	vpand  %ymm0,%ymm2,%ymm0
    213f:	c5 c5 db fe          	vpand  %ymm6,%ymm7,%ymm7
    2143:	c4 42 3d 04 c5       	vpmaddubsw %ymm13,%ymm8,%ymm8
    2148:	c5 3d f5 c1          	vpmaddwd %ymm1,%ymm8,%ymm8
    214c:	c4 c1 45 f5 ff       	vpmaddwd %ymm15,%ymm7,%ymm7
    2151:	c4 c1 45 eb f8       	vpor   %ymm8,%ymm7,%ymm7
    2156:	c5 fd eb c7          	vpor   %ymm7,%ymm0,%ymm0
    215a:	c4 e3 7d 39 c7 01    	vextracti128 $0x1,%ymm0,%xmm7
    2160:	c5 f9 7e c3          	vmovd  %xmm0,%ebx
    2164:	c4 e3 79 16 c6 01    	vpextrd $0x1,%xmm0,%esi
    216a:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
    2171:	00 
    2172:	c4 c3 79 16 ff 02    	vpextrd $0x2,%xmm7,%r15d
    2178:	c4 c1 79 7e fd       	vmovd  %xmm7,%r13d
    217d:	c4 e3 79 16 c3 02    	vpextrd $0x2,%xmm0,%ebx
    2183:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    2189:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    218f:	c4 a1 79 6e 04 bf    	vmovd  (%rdi,%r15,4),%xmm0
    2195:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    219b:	c4 a1 79 6e 3c af    	vmovd  (%rdi,%r13,4),%xmm7
    21a1:	c5 79 6e 04 9f       	vmovd  (%rdi,%rbx,4),%xmm8
    21a6:	c4 a3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%r14,4),%xmm0,%xmm0
    21ad:	48 8b 9c 24 88 00 00 	mov    0x88(%rsp),%rbx
    21b4:	00 
    21b5:	c4 a3 41 22 3c a7 01 	vpinsrd $0x1,(%rdi,%r12,4),%xmm7,%xmm7
    21bc:	c4 23 39 22 04 9f 01 	vpinsrd $0x1,(%rdi,%r11,4),%xmm8,%xmm8
    21c3:	c5 c1 6c f8          	vpunpcklqdq %xmm0,%xmm7,%xmm7
    21c7:	c5 f9 6e 04 9f       	vmovd  (%rdi,%rbx,4),%xmm0
    21cc:	c4 e3 79 22 04 b7 01 	vpinsrd $0x1,(%rdi,%rsi,4),%xmm0,%xmm0
    21d3:	48 89 d6             	mov    %rdx,%rsi
    21d6:	48 83 c2 08          	add    $0x8,%rdx
    21da:	c4 c1 79 6c c0       	vpunpcklqdq %xmm8,%xmm0,%xmm0
    21df:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    21e5:	c4 c2 7d 00 c6       	vpshufb %ymm14,%ymm0,%ymm0
    21ea:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    21ee:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    21f4:	c5 c1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm7
    21f9:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    21fe:	c4 c1 41 eb f8       	vpor   %xmm8,%xmm7,%xmm7
    2203:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    2208:	c5 fa 7f 78 e8       	vmovdqu %xmm7,-0x18(%rax)
    220d:	49 39 d0             	cmp    %rdx,%r8
    2210:	0f 83 fa fe ff ff    	jae    2110 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe90>
    2216:	4c 39 c6             	cmp    %r8,%rsi
    2219:	0f 83 21 03 00 00    	jae    2540 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c0>
    221f:	48 8d 0c 76          	lea    (%rsi,%rsi,2),%rcx
    2223:	49 8d 14 09          	lea    (%r9,%rcx,1),%rdx
    2227:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    222b:	0f b6 5a 02          	movzbl 0x2(%rdx),%ebx
    222f:	0f b6 12             	movzbl (%rdx),%edx
    2232:	c1 e3 10             	shl    $0x10,%ebx
    2235:	c1 e0 08             	shl    $0x8,%eax
    2238:	09 d8                	or     %ebx,%eax
    223a:	09 d0                	or     %edx,%eax
    223c:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    2243:	8d 1c 00             	lea    (%rax,%rax,1),%ebx
    2246:	81 e3 00 fc 01 00    	and    $0x1fc00,%ebx
    224c:	81 e2 f0 03 00 00    	and    $0x3f0,%edx
    2252:	09 da                	or     %ebx,%edx
    2254:	89 c3                	mov    %eax,%ebx
    2256:	81 e3 03 00 fe 00    	and    $0xfe0003,%ebx
    225c:	09 da                	or     %ebx,%edx
    225e:	89 c3                	mov    %eax,%ebx
    2260:	c1 e8 0d             	shr    $0xd,%eax
    2263:	c1 eb 06             	shr    $0x6,%ebx
    2266:	83 e0 08             	and    $0x8,%eax
    2269:	83 e3 04             	and    $0x4,%ebx
    226c:	09 da                	or     %ebx,%edx
    226e:	09 d0                	or     %edx,%eax
    2270:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    2274:	8b 02                	mov    (%rdx),%eax
    2276:	0f b7 12             	movzwl (%rdx),%edx
    2279:	c1 e8 10             	shr    $0x10,%eax
    227c:	66 41 89 14 0a       	mov    %dx,(%r10,%rcx,1)
    2281:	41 88 44 0a 02       	mov    %al,0x2(%r10,%rcx,1)
    2286:	48 8d 46 01          	lea    0x1(%rsi),%rax
    228a:	4c 39 c0             	cmp    %r8,%rax
    228d:	0f 83 ad 02 00 00    	jae    2540 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c0>
    2293:	49 8d 54 09 03       	lea    0x3(%r9,%rcx,1),%rdx
    2298:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    229c:	0f b6 5a 02          	movzbl 0x2(%rdx),%ebx
    22a0:	0f b6 12             	movzbl (%rdx),%edx
    22a3:	c1 e3 10             	shl    $0x10,%ebx
    22a6:	c1 e0 08             	shl    $0x8,%eax
    22a9:	09 d8                	or     %ebx,%eax
    22ab:	09 d0                	or     %edx,%eax
    22ad:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    22b4:	8d 1c 00             	lea    (%rax,%rax,1),%ebx
    22b7:	81 e3 00 fc 01 00    	and    $0x1fc00,%ebx
    22bd:	81 e2 f0 03 00 00    	and    $0x3f0,%edx
    22c3:	09 da                	or     %ebx,%edx
    22c5:	89 c3                	mov    %eax,%ebx
    22c7:	81 e3 03 00 fe 00    	and    $0xfe0003,%ebx
    22cd:	09 da                	or     %ebx,%edx
    22cf:	89 c3                	mov    %eax,%ebx
    22d1:	c1 e8 0d             	shr    $0xd,%eax
    22d4:	c1 eb 06             	shr    $0x6,%ebx
    22d7:	83 e0 08             	and    $0x8,%eax
    22da:	83 e3 04             	and    $0x4,%ebx
    22dd:	09 da                	or     %ebx,%edx
    22df:	09 d0                	or     %edx,%eax
    22e1:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    22e5:	8b 02                	mov    (%rdx),%eax
    22e7:	0f b7 12             	movzwl (%rdx),%edx
    22ea:	c1 e8 10             	shr    $0x10,%eax
    22ed:	66 41 89 54 0a 03    	mov    %dx,0x3(%r10,%rcx,1)
    22f3:	41 88 44 0a 05       	mov    %al,0x5(%r10,%rcx,1)
    22f8:	48 8d 46 02          	lea    0x2(%rsi),%rax
    22fc:	4c 39 c0             	cmp    %r8,%rax
    22ff:	0f 83 3b 02 00 00    	jae    2540 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c0>
    2305:	49 8d 54 09 06       	lea    0x6(%r9,%rcx,1),%rdx
    230a:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    230e:	0f b6 5a 01          	movzbl 0x1(%rdx),%ebx
    2312:	0f b6 12             	movzbl (%rdx),%edx
    2315:	c1 e3 08             	shl    $0x8,%ebx
    2318:	c1 e0 10             	shl    $0x10,%eax
    231b:	09 d8                	or     %ebx,%eax
    231d:	09 d0                	or     %edx,%eax
    231f:	8d 14 00             	lea    (%rax,%rax,1),%edx
    2322:	8d 1c 85 00 00 00 00 	lea    0x0(,%rax,4),%ebx
    2329:	81 e3 f0 03 00 00    	and    $0x3f0,%ebx
    232f:	81 e2 00 fc 01 00    	and    $0x1fc00,%edx
    2335:	09 da                	or     %ebx,%edx
    2337:	89 c3                	mov    %eax,%ebx
    2339:	81 e3 03 00 fe 00    	and    $0xfe0003,%ebx
    233f:	09 da                	or     %ebx,%edx
    2341:	89 c3                	mov    %eax,%ebx
    2343:	c1 e8 0d             	shr    $0xd,%eax
    2346:	c1 eb 06             	shr    $0x6,%ebx
    2349:	83 e0 08             	and    $0x8,%eax
    234c:	83 e3 04             	and    $0x4,%ebx
    234f:	09 da                	or     %ebx,%edx
    2351:	09 d0                	or     %edx,%eax
    2353:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    2357:	8b 02                	mov    (%rdx),%eax
    2359:	0f b7 12             	movzwl (%rdx),%edx
    235c:	c1 e8 10             	shr    $0x10,%eax
    235f:	66 41 89 54 0a 06    	mov    %dx,0x6(%r10,%rcx,1)
    2365:	41 88 44 0a 08       	mov    %al,0x8(%r10,%rcx,1)
    236a:	48 8d 46 03          	lea    0x3(%rsi),%rax
    236e:	4c 39 c0             	cmp    %r8,%rax
    2371:	0f 83 c9 01 00 00    	jae    2540 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c0>
    2377:	49 8d 54 09 09       	lea    0x9(%r9,%rcx,1),%rdx
    237c:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    2380:	0f b6 5a 01          	movzbl 0x1(%rdx),%ebx
    2384:	0f b6 12             	movzbl (%rdx),%edx
    2387:	c1 e3 08             	shl    $0x8,%ebx
    238a:	c1 e0 10             	shl    $0x10,%eax
    238d:	09 d8                	or     %ebx,%eax
    238f:	09 d0                	or     %edx,%eax
    2391:	8d 14 00             	lea    (%rax,%rax,1),%edx
    2394:	8d 1c 85 00 00 00 00 	lea    0x0(,%rax,4),%ebx
    239b:	81 e3 f0 03 00 00    	and    $0x3f0,%ebx
    23a1:	81 e2 00 fc 01 00    	and    $0x1fc00,%edx
    23a7:	09 da                	or     %ebx,%edx
    23a9:	89 c3                	mov    %eax,%ebx
    23ab:	81 e3 03 00 fe 00    	and    $0xfe0003,%ebx
    23b1:	09 da                	or     %ebx,%edx
    23b3:	89 c3                	mov    %eax,%ebx
    23b5:	c1 e8 0d             	shr    $0xd,%eax
    23b8:	c1 eb 06             	shr    $0x6,%ebx
    23bb:	83 e0 08             	and    $0x8,%eax
    23be:	83 e3 04             	and    $0x4,%ebx
    23c1:	09 da                	or     %ebx,%edx
    23c3:	09 d0                	or     %edx,%eax
    23c5:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    23c9:	8b 02                	mov    (%rdx),%eax
    23cb:	0f b7 12             	movzwl (%rdx),%edx
    23ce:	c1 e8 10             	shr    $0x10,%eax
    23d1:	66 41 89 54 0a 09    	mov    %dx,0x9(%r10,%rcx,1)
    23d7:	41 88 44 0a 0b       	mov    %al,0xb(%r10,%rcx,1)
    23dc:	48 8d 46 04          	lea    0x4(%rsi),%rax
    23e0:	4c 39 c0             	cmp    %r8,%rax
    23e3:	0f 83 57 01 00 00    	jae    2540 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c0>
    23e9:	49 8d 54 09 0c       	lea    0xc(%r9,%rcx,1),%rdx
    23ee:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    23f2:	0f b6 5a 01          	movzbl 0x1(%rdx),%ebx
    23f6:	0f b6 12             	movzbl (%rdx),%edx
    23f9:	c1 e3 08             	shl    $0x8,%ebx
    23fc:	c1 e0 10             	shl    $0x10,%eax
    23ff:	09 d8                	or     %ebx,%eax
    2401:	09 d0                	or     %edx,%eax
    2403:	8d 14 00             	lea    (%rax,%rax,1),%edx
    2406:	8d 1c 85 00 00 00 00 	lea    0x0(,%rax,4),%ebx
    240d:	81 e3 f0 03 00 00    	and    $0x3f0,%ebx
    2413:	81 e2 00 fc 01 00    	and    $0x1fc00,%edx
    2419:	09 da                	or     %ebx,%edx
    241b:	89 c3                	mov    %eax,%ebx
    241d:	81 e3 03 00 fe 00    	and    $0xfe0003,%ebx
    2423:	09 da                	or     %ebx,%edx
    2425:	89 c3                	mov    %eax,%ebx
    2427:	c1 e8 0d             	shr    $0xd,%eax
    242a:	c1 eb 06             	shr    $0x6,%ebx
    242d:	83 e0 08             	and    $0x8,%eax
    2430:	83 e3 04             	and    $0x4,%ebx
    2433:	09 da                	or     %ebx,%edx
    2435:	09 d0                	or     %edx,%eax
    2437:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    243b:	8b 02                	mov    (%rdx),%eax
    243d:	0f b7 12             	movzwl (%rdx),%edx
    2440:	c1 e8 10             	shr    $0x10,%eax
    2443:	66 41 89 54 0a 0c    	mov    %dx,0xc(%r10,%rcx,1)
    2449:	41 88 44 0a 0e       	mov    %al,0xe(%r10,%rcx,1)
    244e:	48 8d 46 05          	lea    0x5(%rsi),%rax
    2452:	4c 39 c0             	cmp    %r8,%rax
    2455:	0f 83 e5 00 00 00    	jae    2540 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c0>
    245b:	49 8d 54 09 0f       	lea    0xf(%r9,%rcx,1),%rdx
    2460:	48 83 c6 06          	add    $0x6,%rsi
    2464:	0f b6 42 02          	movzbl 0x2(%rdx),%eax
    2468:	0f b6 5a 01          	movzbl 0x1(%rdx),%ebx
    246c:	0f b6 12             	movzbl (%rdx),%edx
    246f:	c1 e3 08             	shl    $0x8,%ebx
    2472:	c1 e0 10             	shl    $0x10,%eax
    2475:	09 d8                	or     %ebx,%eax
    2477:	09 d0                	or     %edx,%eax
    2479:	8d 14 00             	lea    (%rax,%rax,1),%edx
    247c:	8d 1c 85 00 00 00 00 	lea    0x0(,%rax,4),%ebx
    2483:	81 e3 f0 03 00 00    	and    $0x3f0,%ebx
    2489:	81 e2 00 fc 01 00    	and    $0x1fc00,%edx
    248f:	09 da                	or     %ebx,%edx
    2491:	89 c3                	mov    %eax,%ebx
    2493:	81 e3 03 00 fe 00    	and    $0xfe0003,%ebx
    2499:	09 da                	or     %ebx,%edx
    249b:	89 c3                	mov    %eax,%ebx
    249d:	c1 e8 0d             	shr    $0xd,%eax
    24a0:	c1 eb 06             	shr    $0x6,%ebx
    24a3:	83 e0 08             	and    $0x8,%eax
    24a6:	83 e3 04             	and    $0x4,%ebx
    24a9:	09 da                	or     %ebx,%edx
    24ab:	09 d0                	or     %edx,%eax
    24ad:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    24b1:	8b 02                	mov    (%rdx),%eax
    24b3:	0f b7 12             	movzwl (%rdx),%edx
    24b6:	c1 e8 10             	shr    $0x10,%eax
    24b9:	66 41 89 54 0a 0f    	mov    %dx,0xf(%r10,%rcx,1)
    24bf:	41 88 44 0a 11       	mov    %al,0x11(%r10,%rcx,1)
    24c4:	4c 39 c6             	cmp    %r8,%rsi
    24c7:	73 77                	jae    2540 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x12c0>
    24c9:	49 8d 54 09 12       	lea    0x12(%r9,%rcx,1),%rdx
    24ce:	49 8d 74 0a 12       	lea    0x12(%r10,%rcx,1),%rsi
    24d3:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    24d7:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    24db:	0f b6 12             	movzbl (%rdx),%edx
    24de:	c1 e1 10             	shl    $0x10,%ecx
    24e1:	c1 e0 08             	shl    $0x8,%eax
    24e4:	09 c8                	or     %ecx,%eax
    24e6:	09 d0                	or     %edx,%eax
    24e8:	8d 14 85 00 00 00 00 	lea    0x0(,%rax,4),%edx
    24ef:	8d 0c 00             	lea    (%rax,%rax,1),%ecx
    24f2:	81 e1 00 fc 01 00    	and    $0x1fc00,%ecx
    24f8:	81 e2 f0 03 00 00    	and    $0x3f0,%edx
    24fe:	09 ca                	or     %ecx,%edx
    2500:	89 c1                	mov    %eax,%ecx
    2502:	81 e1 03 00 fe 00    	and    $0xfe0003,%ecx
    2508:	09 ca                	or     %ecx,%edx
    250a:	89 c1                	mov    %eax,%ecx
    250c:	c1 e8 0d             	shr    $0xd,%eax
    250f:	c1 e9 06             	shr    $0x6,%ecx
    2512:	83 e0 08             	and    $0x8,%eax
    2515:	83 e1 04             	and    $0x4,%ecx
    2518:	09 ca                	or     %ecx,%edx
    251a:	09 d0                	or     %edx,%eax
    251c:	48 8d 14 87          	lea    (%rdi,%rax,4),%rdx
    2520:	8b 02                	mov    (%rdx),%eax
    2522:	0f b7 12             	movzwl (%rdx),%edx
    2525:	c1 e8 10             	shr    $0x10,%eax
    2528:	66 89 16             	mov    %dx,(%rsi)
    252b:	88 46 02             	mov    %al,0x2(%rsi)
    252e:	c5 f8 77             	vzeroupper
    2531:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2535:	5b                   	pop    %rbx
    2536:	41 5c                	pop    %r12
    2538:	41 5d                	pop    %r13
    253a:	41 5e                	pop    %r14
    253c:	41 5f                	pop    %r15
    253e:	5d                   	pop    %rbp
    253f:	c3                   	ret
    2540:	c5 f8 77             	vzeroupper
    2543:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2547:	5b                   	pop    %rbx
    2548:	41 5c                	pop    %r12
    254a:	41 5d                	pop    %r13
    254c:	41 5e                	pop    %r14
    254e:	41 5f                	pop    %r15
    2550:	5d                   	pop    %rbp
    2551:	c3                   	ret
    2552:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    2558:	4c 89 c6             	mov    %r8,%rsi
    255b:	e9 3a fb ff ff       	jmp    209a <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe1a>
    2560:	c3                   	ret
    2561:	48 8d 41 28          	lea    0x28(%rcx),%rax
    2565:	48 89 ce             	mov    %rcx,%rsi
    2568:	e9 dc f6 ff ff       	jmp    1c49 <jshc_channel::avx2_chain_directtile_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x9c9>
