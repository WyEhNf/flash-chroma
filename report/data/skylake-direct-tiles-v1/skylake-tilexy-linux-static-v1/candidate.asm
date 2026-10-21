
artifacts/skylake-tilexy-linux-build-v1/CMakeFiles/jshc_skylake_tilexy.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 23 11 00 00    	je     1130 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1130>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d2             	mov    %rdx,%r10
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 62                	jmp    a7 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa7>
      45:	0f 1f 00             	nopl   (%rax)
      48:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
      4d:	45 0f b6 42 02       	movzbl 0x2(%r10),%r8d
      52:	49 ff c1             	inc    %r9
      55:	49 83 c2 03          	add    $0x3,%r10
      59:	41 c1 e0 10          	shl    $0x10,%r8d
      5d:	c1 e0 08             	shl    $0x8,%eax
      60:	44 09 c0             	or     %r8d,%eax
      63:	45 0f b6 42 fd       	movzbl -0x3(%r10),%r8d
      68:	44 09 c0             	or     %r8d,%eax
      6b:	41 89 c0             	mov    %eax,%r8d
      6e:	41 c1 e8 05          	shr    $0x5,%r8d
      72:	41 31 c0             	xor    %eax,%r8d
      75:	41 83 e0 38          	and    $0x38,%r8d
      79:	44 31 c0             	xor    %r8d,%eax
      7c:	41 c1 e0 05          	shl    $0x5,%r8d
      80:	44 31 c0             	xor    %r8d,%eax
      83:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
      87:	4c 8d 04 86          	lea    (%rsi,%rax,4),%r8
      8b:	41 8b 00             	mov    (%r8),%eax
      8e:	45 0f b7 00          	movzwl (%r8),%r8d
      92:	c1 e8 10             	shr    $0x10,%eax
      95:	66 45 89 42 fd       	mov    %r8w,-0x3(%r10)
      9a:	41 88 42 ff          	mov    %al,-0x1(%r10)
      9e:	4c 39 c9             	cmp    %r9,%rcx
      a1:	0f 84 79 10 00 00    	je     1120 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1120>
      a7:	41 f6 c2 3f          	test   $0x3f,%r10b
      ab:	75 9b                	jne    48 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      ad:	49 8d 41 48          	lea    0x48(%r9),%rax
      b1:	48 39 c1             	cmp    %rax,%rcx
      b4:	0f 82 77 10 00 00    	jb     1131 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1131>
      ba:	41 b8 38 00 00 00    	mov    $0x38,%r8d
      c0:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      c4:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # cc <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xcc>
      cb:	00 
      cc:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # d4 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd4>
      d3:	00 
      d4:	c4 41 79 6e d8       	vmovd  %r8d,%xmm11
      d9:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # e1 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe1>
      e0:	00 
      e1:	48 01 d0             	add    %rdx,%rax
      e4:	c4 42 7d 58 db       	vpbroadcastd %xmm11,%ymm11
      e9:	eb 08                	jmp    f3 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf3>
      eb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      f0:	4d 89 c1             	mov    %r8,%r9
      f3:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      fa:	4c 39 c1             	cmp    %r8,%rcx
      fd:	72 1c                	jb     11b <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x11b>
      ff:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
     106:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
     10d:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
     114:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
     11b:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     11f:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
     124:	48 05 c0 00 00 00    	add    $0xc0,%rax
     12a:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     130:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     136:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     13b:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
     140:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
     144:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
     149:	c5 ed 72 f1 05       	vpslld $0x5,%ymm1,%ymm2
     14e:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
     152:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
     156:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     15c:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     161:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     167:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     16c:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     172:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     177:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     17c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     181:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     186:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     18c:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     192:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     197:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     19c:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     1a2:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     1a8:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     1ae:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     1b4:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     1b9:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     1be:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     1c5:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     1cc:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
     1d2:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     1d6:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     1db:	c4 23 29 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm10,%xmm10
     1e2:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     1e9:	c5 29 6c d1          	vpunpcklqdq %xmm1,%xmm10,%xmm10
     1ed:	c5 fa 7e 88 68 ff ff 	vmovq  -0x98(%rax),%xmm1
     1f4:	ff 
     1f5:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
     1fb:	c5 fa 6f 80 58 ff ff 	vmovdqu -0xa8(%rax),%xmm0
     202:	ff 
     203:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
     208:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     20e:	c4 42 4d 36 d2       	vpermd %ymm10,%ymm6,%ymm10
     213:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     219:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     21e:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
     223:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
     227:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
     22c:	c5 ed 72 f1 05       	vpslld $0x5,%ymm1,%ymm2
     231:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
     235:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
     239:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     23f:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     244:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     24a:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     24f:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     255:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     25a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     25f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     264:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     269:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     26f:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     275:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     27a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     27f:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     285:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     28b:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     291:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     297:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     29c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     2a1:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     2a8:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     2af:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     2b3:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     2b8:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     2be:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     2c5:	c4 a3 61 22 1c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm3,%xmm3
     2cc:	c5 e1 6c d9          	vpunpcklqdq %xmm1,%xmm3,%xmm3
     2d0:	c5 fa 7e 48 80       	vmovq  -0x80(%rax),%xmm1
     2d5:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
     2db:	c5 fa 6f 80 70 ff ff 	vmovdqu -0x90(%rax),%xmm0
     2e2:	ff 
     2e3:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
     2e8:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     2ee:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
     2f3:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     2f9:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     2fe:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
     303:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
     307:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
     30c:	c5 ed 72 f1 05       	vpslld $0x5,%ymm1,%ymm2
     311:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
     315:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
     319:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     31f:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     324:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     32a:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     32f:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     335:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     33a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     33f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     344:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     349:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     34f:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     355:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     35a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     35f:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     365:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     36b:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     371:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     377:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     37c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     381:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     388:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     38f:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     395:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     399:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     39e:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     3a5:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     3ac:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     3b0:	c5 fa 7e 48 98       	vmovq  -0x68(%rax),%xmm1
     3b5:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     3bb:	c5 fa 6f 40 88       	vmovdqu -0x78(%rax),%xmm0
     3c0:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     3c5:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     3cb:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
     3d0:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     3d6:	c5 79 6f f2          	vmovdqa %xmm2,%xmm14
     3da:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     3e0:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     3e5:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
     3ea:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
     3ee:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
     3f3:	c5 c5 72 f1 05       	vpslld $0x5,%ymm1,%ymm7
     3f8:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
     3fc:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
     400:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     406:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     40b:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     411:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     416:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     41c:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     421:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     426:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     42b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     430:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     436:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     43c:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     442:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     448:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     44d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     452:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     457:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     45c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     462:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     468:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     46e:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     475:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     47c:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     483:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     487:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     48c:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     493:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     497:	c5 fa 7e 48 b0       	vmovq  -0x50(%rax),%xmm1
     49c:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     4a2:	c5 fa 6f 40 a0       	vmovdqu -0x60(%rax),%xmm0
     4a7:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
     4ac:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     4b2:	c4 42 4d 36 c9       	vpermd %ymm9,%ymm6,%ymm9
     4b7:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     4bd:	c4 41 79 6f f9       	vmovdqa %xmm9,%xmm15
     4c2:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     4c8:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     4cd:	c4 43 31 0f cf 08    	vpalignr $0x8,%xmm15,%xmm9,%xmm9
     4d3:	c4 c1 69 6c d7       	vpunpcklqdq %xmm15,%xmm2,%xmm2
     4d8:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
     4dd:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
     4e3:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
     4e7:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
     4ec:	c5 c5 72 f1 05       	vpslld $0x5,%ymm1,%ymm7
     4f1:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
     4f5:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
     4f9:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     4ff:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     504:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     50a:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     50f:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     515:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     51a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     51f:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     524:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     529:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     52f:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     535:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     53a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     53f:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     545:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     54b:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     551:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     557:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     55c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     561:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     568:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     56f:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     575:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     579:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     57e:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     585:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     58c:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     590:	c5 fa 7e 48 c8       	vmovq  -0x38(%rax),%xmm1
     595:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     59b:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
     5a0:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
     5a5:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
     5ab:	c4 42 4d 36 c0       	vpermd %ymm8,%ymm6,%ymm8
     5b0:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     5b6:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     5bb:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
     5c0:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
     5c4:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
     5c9:	c5 c5 72 f1 05       	vpslld $0x5,%ymm1,%ymm7
     5ce:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
     5d2:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
     5d6:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
     5dc:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     5e1:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     5e7:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     5ec:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     5f1:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
     5f6:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
     5fc:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     602:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     608:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     60d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     612:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     617:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     61c:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
     622:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
     628:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     62d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     632:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     638:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     63e:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
     643:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     64a:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     651:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
     658:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     65c:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     662:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     669:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
     66d:	c5 fa 7e 78 e0       	vmovq  -0x20(%rax),%xmm7
     672:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     678:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
     67d:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     682:	c4 e3 41 0f f8 0c    	vpalignr $0xc,%xmm0,%xmm7,%xmm7
     688:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
     68d:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     693:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     698:	c5 c5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm7
     69d:	c5 fd ef ff          	vpxor  %ymm7,%ymm0,%ymm7
     6a1:	c4 c1 45 db fb       	vpand  %ymm11,%ymm7,%ymm7
     6a6:	c5 9d 72 f7 05       	vpslld $0x5,%ymm7,%ymm12
     6ab:	c4 c1 7d ef c4       	vpxor  %ymm12,%ymm0,%ymm0
     6b0:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
     6b4:	c4 e3 7d 39 c7 01    	vextracti128 $0x1,%ymm0,%xmm7
     6ba:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     6bf:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     6c5:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     6ca:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     6d0:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     6d5:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     6da:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     6df:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     6e4:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     6ea:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     6f0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     6f5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     6fa:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     700:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     706:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     70c:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     712:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     717:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     71c:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     723:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     72a:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     72f:	c5 c1 6c f8          	vpunpcklqdq %xmm0,%xmm7,%xmm7
     733:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     739:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     740:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     747:	c4 c1 79 6c c4       	vpunpcklqdq %xmm12,%xmm0,%xmm0
     74c:	c5 7a 7e 60 f8       	vmovq  -0x8(%rax),%xmm12
     751:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     757:	c5 fa 6f 78 e8       	vmovdqu -0x18(%rax),%xmm7
     75c:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     761:	c4 63 19 0f e7 0c    	vpalignr $0xc,%xmm7,%xmm12,%xmm12
     767:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
     76c:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
     772:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     776:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     77c:	c4 e2 45 00 fd       	vpshufb %ymm5,%ymm7,%ymm7
     781:	c5 9d 72 d7 05       	vpsrld $0x5,%ymm7,%ymm12
     786:	c4 41 45 ef e4       	vpxor  %ymm12,%ymm7,%ymm12
     78b:	c4 41 1d db e3       	vpand  %ymm11,%ymm12,%ymm12
     790:	c4 c1 15 72 f4 05    	vpslld $0x5,%ymm12,%ymm13
     796:	c4 c1 45 ef fd       	vpxor  %ymm13,%ymm7,%ymm7
     79b:	c4 c1 45 ef fc       	vpxor  %ymm12,%ymm7,%ymm7
     7a0:	c4 c3 7d 39 fc 01    	vextracti128 $0x1,%ymm7,%xmm12
     7a6:	c4 c1 79 7e f8       	vmovd  %xmm7,%r8d
     7ab:	c4 c3 79 16 fb 02    	vpextrd $0x2,%xmm7,%r11d
     7b1:	c4 41 79 7e e4       	vmovd  %xmm12,%r12d
     7b6:	c4 43 79 16 e6 02    	vpextrd $0x2,%xmm12,%r14d
     7bc:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     7c1:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     7c6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     7cb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     7d0:	c4 43 79 16 e4 01    	vpextrd $0x1,%xmm12,%r12d
     7d6:	c4 43 79 16 e6 03    	vpextrd $0x3,%xmm12,%r14d
     7dc:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     7e1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     7e6:	c4 c3 79 16 f8 01    	vpextrd $0x1,%xmm7,%r8d
     7ec:	c4 c3 79 16 fb 03    	vpextrd $0x3,%xmm7,%r11d
     7f2:	c4 21 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm12
     7f8:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
     7fe:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     803:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     808:	c4 a3 41 22 3c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm7,%xmm7
     80f:	c4 23 19 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm12,%xmm12
     816:	c5 79 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm13
     81b:	c5 19 6c e7          	vpunpcklqdq %xmm7,%xmm12,%xmm12
     81f:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     825:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     82c:	c4 23 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm13,%xmm13
     833:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     83a:	c5 fd e7 50 80       	vmovntdq %ymm2,-0x80(%rax)
     83f:	c5 79 7f c2          	vmovdqa %xmm8,%xmm2
     843:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     849:	4d 8d 41 40          	lea    0x40(%r9),%r8
     84d:	c4 c1 41 6c fd       	vpunpcklqdq %xmm13,%xmm7,%xmm7
     852:	c5 79 6f eb          	vmovdqa %xmm3,%xmm13
     856:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     85c:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
     862:	c4 c3 61 0f dd 08    	vpalignr $0x8,%xmm13,%xmm3,%xmm3
     868:	c4 41 79 6f e2       	vmovdqa %xmm10,%xmm12
     86d:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
     872:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
     878:	c4 c3 65 38 de 01    	vinserti128 $0x1,%xmm14,%ymm3,%ymm3
     87e:	c4 e2 4d 36 ff       	vpermd %ymm7,%ymm6,%ymm7
     883:	c4 41 29 6c d5       	vpunpcklqdq %xmm13,%xmm10,%xmm10
     888:	c5 fd e7 98 60 ff ff 	vmovntdq %ymm3,-0xa0(%rax)
     88f:	ff 
     890:	c4 43 1d 38 e2 01    	vinserti128 $0x1,%xmm10,%ymm12,%ymm12
     896:	c5 f9 6f df          	vmovdqa %xmm7,%xmm3
     89a:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
     89e:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     8a4:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     8aa:	c4 41 39 6c c2       	vpunpcklqdq %xmm10,%xmm8,%xmm8
     8af:	c5 7d e7 a0 40 ff ff 	vmovntdq %ymm12,-0xc0(%rax)
     8b6:	ff 
     8b7:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
     8bd:	c4 e3 41 0f fb 08    	vpalignr $0x8,%xmm3,%xmm7,%xmm7
     8c3:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
     8c7:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
     8cd:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     8d3:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
     8d9:	c5 fd e7 50 a0       	vmovntdq %ymm2,-0x60(%rax)
     8de:	c5 fd e7 48 c0       	vmovntdq %ymm1,-0x40(%rax)
     8e3:	c5 fd e7 40 e0       	vmovntdq %ymm0,-0x20(%rax)
     8e8:	4c 39 d1             	cmp    %r10,%rcx
     8eb:	0f 83 ff f7 ff ff    	jae    f0 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf0>
     8f1:	0f ae f8             	sfence
     8f4:	49 8d 41 68          	lea    0x68(%r9),%rax
     8f8:	48 39 c1             	cmp    %rax,%rcx
     8fb:	0f 82 1f 04 00 00    	jb     d20 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd20>
     901:	41 b9 38 00 00 00    	mov    $0x38,%r9d
     907:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     90b:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 913 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x913>
     912:	00 
     913:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 91b <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x91b>
     91a:	00 
     91b:	c4 41 79 6e c1       	vmovd  %r9d,%xmm8
     920:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # 928 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x928>
     927:	00 
     928:	48 01 d0             	add    %rdx,%rax
     92b:	c4 42 7d 58 c0       	vpbroadcastd %xmm8,%ymm8
     930:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
     934:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
     939:	48 83 c0 60          	add    $0x60,%rax
     93d:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
     942:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
     948:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
     94e:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
     953:	c5 fd 72 d2 05       	vpsrld $0x5,%ymm2,%ymm0
     958:	c5 ed ef c0          	vpxor  %ymm0,%ymm2,%ymm0
     95c:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
     961:	c5 f5 72 f0 05       	vpslld $0x5,%ymm0,%ymm1
     966:	c5 ed ef d1          	vpxor  %ymm1,%ymm2,%ymm2
     96a:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
     96f:	c5 ed ef d0          	vpxor  %ymm0,%ymm2,%ymm2
     973:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
     978:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
     97e:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
     984:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
     98a:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
     98f:	c5 fd 72 d1 05       	vpsrld $0x5,%ymm1,%ymm0
     994:	c5 f5 ef c0          	vpxor  %ymm0,%ymm1,%ymm0
     998:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
     99d:	c5 e5 72 f0 05       	vpslld $0x5,%ymm0,%ymm3
     9a2:	c5 f5 ef cb          	vpxor  %ymm3,%ymm1,%ymm1
     9a6:	c5 fa 7e 58 e0       	vmovq  -0x20(%rax),%xmm3
     9ab:	c5 f5 ef c8          	vpxor  %ymm0,%ymm1,%ymm1
     9af:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
     9b4:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
     9ba:	c4 e3 61 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm3,%xmm3
     9c0:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
     9c6:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     9cb:	c5 e5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm3
     9d0:	c5 fd ef db          	vpxor  %ymm3,%ymm0,%ymm3
     9d4:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
     9d9:	c5 ad 72 f3 05       	vpslld $0x5,%ymm3,%ymm10
     9de:	c4 c1 7d ef c2       	vpxor  %ymm10,%ymm0,%ymm0
     9e3:	c5 fd ef c3          	vpxor  %ymm3,%ymm0,%ymm0
     9e7:	c5 fa 6f 58 e8       	vmovdqu -0x18(%rax),%xmm3
     9ec:	c4 c3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm10
     9f2:	c4 63 21 0f db 0c    	vpalignr $0xc,%xmm3,%xmm11,%xmm11
     9f8:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
     9fe:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
     a03:	c5 a5 72 d3 05       	vpsrld $0x5,%ymm3,%ymm11
     a08:	c4 41 65 ef db       	vpxor  %ymm11,%ymm3,%ymm11
     a0d:	c4 41 25 db d8       	vpand  %ymm8,%ymm11,%ymm11
     a12:	c4 c1 1d 72 f3 05    	vpslld $0x5,%ymm11,%ymm12
     a18:	c4 c1 65 ef dc       	vpxor  %ymm12,%ymm3,%ymm3
     a1d:	c4 c1 65 ef db       	vpxor  %ymm11,%ymm3,%ymm3
     a22:	c4 c3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm11
     a28:	c4 c1 79 7e d9       	vmovd  %xmm3,%r9d
     a2d:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
     a33:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
     a38:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
     a3e:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     a43:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     a48:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     a4d:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     a52:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
     a58:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
     a5e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a63:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a68:	c4 c3 79 16 d9 01    	vpextrd $0x1,%xmm3,%r9d
     a6e:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
     a74:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
     a7a:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
     a80:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a85:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a8a:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
     a91:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
     a98:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
     a9e:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
     aa3:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
     aa8:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     aad:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
     ab3:	c5 21 6c db          	vpunpcklqdq %xmm3,%xmm11,%xmm11
     ab7:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
     abd:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     ac2:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
     ac8:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
     acf:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     ad5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     ada:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
     ae1:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
     ae6:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     aeb:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     af1:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     af6:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
     afc:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b01:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     b06:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b0b:	c4 c1 61 6c dc       	vpunpcklqdq %xmm12,%xmm3,%xmm3
     b10:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     b16:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     b1c:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
     b22:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     b27:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
     b2c:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     b33:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     b3a:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
     b40:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
     b45:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     b4a:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     b51:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
     b57:	c5 29 6c d0          	vpunpcklqdq %xmm0,%xmm10,%xmm10
     b5b:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     b61:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     b66:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
     b6c:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
     b72:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     b77:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b7c:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
     b82:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     b89:	c4 c1 79 7e c9       	vmovd  %xmm1,%r9d
     b8e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     b93:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
     b98:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     b9d:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
     ba3:	c4 c3 79 16 c9 01    	vpextrd $0x1,%xmm1,%r9d
     ba9:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     baf:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
     bb4:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     bb9:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
     bc0:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     bc5:	c4 c3 7d 38 c2 01    	vinserti128 $0x1,%xmm10,%ymm0,%ymm0
     bcb:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
     bd0:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     bd7:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     bdc:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
     be2:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     be7:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     bec:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     bf1:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
     bf7:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
     bfd:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     c01:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     c07:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     c0e:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
     c14:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     c19:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
     c1f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     c24:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
     c29:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     c30:	c4 c1 79 7e d1       	vmovd  %xmm2,%r9d
     c35:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     c3a:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     c3f:	c4 c3 79 16 d1 01    	vpextrd $0x1,%xmm2,%r9d
     c45:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     c4a:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c4f:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     c55:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     c5a:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
     c5e:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
     c64:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
     c6a:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
     c6f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     c75:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     c7c:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
     c81:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
     c88:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
     c8f:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
     c94:	c5 79 6f d9          	vmovdqa %xmm1,%xmm11
     c98:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     c9e:	c5 c1 6c fa          	vpunpcklqdq %xmm2,%xmm7,%xmm7
     ca2:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     ca8:	c4 c3 71 0f cb 08    	vpalignr $0x8,%xmm11,%xmm1,%xmm1
     cae:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
     cb4:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     cbb:	4d 8d 48 48          	lea    0x48(%r8),%r9
     cbf:	c5 fe 7f 48 c0       	vmovdqu %ymm1,-0x40(%rax)
     cc4:	49 83 c0 20          	add    $0x20,%r8
     cc8:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
     ccd:	c5 79 6f cb          	vmovdqa %xmm3,%xmm9
     cd1:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     cd7:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
     cdd:	c4 c3 61 0f d9 08    	vpalignr $0x8,%xmm9,%xmm3,%xmm3
     ce3:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
     ce8:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
     ced:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
     cf3:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
     cf8:	c5 fe 7f 40 e0       	vmovdqu %ymm0,-0x20(%rax)
     cfd:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
     d01:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     d07:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     d0c:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
     d12:	c5 fe 7f 50 a0       	vmovdqu %ymm2,-0x60(%rax)
     d17:	4c 39 c9             	cmp    %r9,%rcx
     d1a:	0f 83 10 fc ff ff    	jae    930 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x930>
     d20:	4d 8d 48 08          	lea    0x8(%r8),%r9
     d24:	4c 39 c9             	cmp    %r9,%rcx
     d27:	0f 82 37 01 00 00    	jb     e64 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xe64>
     d2d:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     d31:	41 b8 38 00 00 00    	mov    $0x38,%r8d
     d37:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # d3f <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd3f>
     d3e:	00 
     d3f:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # d47 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd47>
     d46:	00 
     d47:	c4 c1 79 6e c8       	vmovd  %r8d,%xmm1
     d4c:	48 01 d0             	add    %rdx,%rax
     d4f:	c4 e2 7d 58 c9       	vpbroadcastd %xmm1,%ymm1
     d54:	0f 1f 40 00          	nopl   0x0(%rax)
     d58:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
     d5c:	c5 fa 7e 50 10       	vmovq  0x10(%rax),%xmm2
     d61:	48 83 c0 18          	add    $0x18,%rax
     d65:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
     d6b:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     d71:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
     d76:	c5 ed 72 d0 05       	vpsrld $0x5,%ymm0,%ymm2
     d7b:	c5 fd ef d2          	vpxor  %ymm2,%ymm0,%ymm2
     d7f:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
     d83:	c5 e5 72 f2 05       	vpslld $0x5,%ymm2,%ymm3
     d88:	c5 fd ef c3          	vpxor  %ymm3,%ymm0,%ymm0
     d8c:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
     d90:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
     d96:	c4 c1 79 7e c0       	vmovd  %xmm0,%r8d
     d9b:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
     da1:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
     da6:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
     dac:	46 0f b6 14 07       	movzbl (%rdi,%r8,1),%r10d
     db1:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
     db6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
     dbb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
     dc0:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
     dc6:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
     dcc:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     dd1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     dd6:	c4 c3 79 16 c0 01    	vpextrd $0x1,%xmm0,%r8d
     ddc:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
     de2:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     de8:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     dee:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     df3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     df8:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     dff:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     e06:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
     e0b:	c5 e9 6c d0          	vpunpcklqdq %xmm0,%xmm2,%xmm2
     e0f:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     e15:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
     e1c:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     e23:	4d 89 c8             	mov    %r9,%r8
     e26:	49 83 c1 08          	add    $0x8,%r9
     e2a:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
     e2e:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
     e34:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
     e39:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
     e3d:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     e43:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
     e48:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     e4d:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
     e51:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
     e56:	c5 fa 7f 50 e8       	vmovdqu %xmm2,-0x18(%rax)
     e5b:	4c 39 c9             	cmp    %r9,%rcx
     e5e:	0f 83 f4 fe ff ff    	jae    d58 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd58>
     e64:	49 39 c8             	cmp    %rcx,%r8
     e67:	0f 83 9b 02 00 00    	jae    1108 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1108>
     e6d:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
     e71:	4e 8d 14 0a          	lea    (%rdx,%r9,1),%r10
     e75:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     e7a:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     e7f:	c1 e0 08             	shl    $0x8,%eax
     e82:	41 c1 e3 10          	shl    $0x10,%r11d
     e86:	44 09 d8             	or     %r11d,%eax
     e89:	45 0f b6 1a          	movzbl (%r10),%r11d
     e8d:	44 09 d8             	or     %r11d,%eax
     e90:	41 89 c3             	mov    %eax,%r11d
     e93:	41 c1 eb 05          	shr    $0x5,%r11d
     e97:	41 31 c3             	xor    %eax,%r11d
     e9a:	41 83 e3 38          	and    $0x38,%r11d
     e9e:	44 31 d8             	xor    %r11d,%eax
     ea1:	41 c1 e3 05          	shl    $0x5,%r11d
     ea5:	44 31 d8             	xor    %r11d,%eax
     ea8:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     eac:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     eb0:	41 8b 03             	mov    (%r11),%eax
     eb3:	45 0f b7 1b          	movzwl (%r11),%r11d
     eb7:	c1 e8 10             	shr    $0x10,%eax
     eba:	66 45 89 1a          	mov    %r11w,(%r10)
     ebe:	41 88 42 02          	mov    %al,0x2(%r10)
     ec2:	49 8d 40 01          	lea    0x1(%r8),%rax
     ec6:	48 39 c8             	cmp    %rcx,%rax
     ec9:	0f 83 39 02 00 00    	jae    1108 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1108>
     ecf:	4e 8d 54 0a 03       	lea    0x3(%rdx,%r9,1),%r10
     ed4:	41 0f b6 42 01       	movzbl 0x1(%r10),%eax
     ed9:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
     ede:	c1 e0 08             	shl    $0x8,%eax
     ee1:	41 c1 e3 10          	shl    $0x10,%r11d
     ee5:	44 09 d8             	or     %r11d,%eax
     ee8:	45 0f b6 1a          	movzbl (%r10),%r11d
     eec:	44 09 d8             	or     %r11d,%eax
     eef:	41 89 c3             	mov    %eax,%r11d
     ef2:	41 c1 eb 05          	shr    $0x5,%r11d
     ef6:	41 31 c3             	xor    %eax,%r11d
     ef9:	41 83 e3 38          	and    $0x38,%r11d
     efd:	44 31 d8             	xor    %r11d,%eax
     f00:	41 c1 e3 05          	shl    $0x5,%r11d
     f04:	44 31 d8             	xor    %r11d,%eax
     f07:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f0b:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f0f:	41 8b 03             	mov    (%r11),%eax
     f12:	45 0f b7 1b          	movzwl (%r11),%r11d
     f16:	c1 e8 10             	shr    $0x10,%eax
     f19:	66 45 89 1a          	mov    %r11w,(%r10)
     f1d:	41 88 42 02          	mov    %al,0x2(%r10)
     f21:	49 8d 40 02          	lea    0x2(%r8),%rax
     f25:	48 39 c8             	cmp    %rcx,%rax
     f28:	0f 83 da 01 00 00    	jae    1108 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1108>
     f2e:	4e 8d 5c 0a 06       	lea    0x6(%rdx,%r9,1),%r11
     f33:	41 0f b6 43 01       	movzbl 0x1(%r11),%eax
     f38:	45 0f b6 53 02       	movzbl 0x2(%r11),%r10d
     f3d:	c1 e0 08             	shl    $0x8,%eax
     f40:	41 c1 e2 10          	shl    $0x10,%r10d
     f44:	44 09 d0             	or     %r10d,%eax
     f47:	45 0f b6 13          	movzbl (%r11),%r10d
     f4b:	44 09 d0             	or     %r10d,%eax
     f4e:	41 89 c2             	mov    %eax,%r10d
     f51:	41 c1 ea 05          	shr    $0x5,%r10d
     f55:	41 31 c2             	xor    %eax,%r10d
     f58:	41 83 e2 38          	and    $0x38,%r10d
     f5c:	44 89 d3             	mov    %r10d,%ebx
     f5f:	44 31 d0             	xor    %r10d,%eax
     f62:	c1 e3 05             	shl    $0x5,%ebx
     f65:	31 d8                	xor    %ebx,%eax
     f67:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f6b:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
     f6f:	41 8b 02             	mov    (%r10),%eax
     f72:	45 0f b7 12          	movzwl (%r10),%r10d
     f76:	c1 e8 10             	shr    $0x10,%eax
     f79:	66 45 89 13          	mov    %r10w,(%r11)
     f7d:	41 88 43 02          	mov    %al,0x2(%r11)
     f81:	49 8d 40 03          	lea    0x3(%r8),%rax
     f85:	48 39 c8             	cmp    %rcx,%rax
     f88:	0f 83 7a 01 00 00    	jae    1108 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1108>
     f8e:	4e 8d 5c 0a 09       	lea    0x9(%rdx,%r9,1),%r11
     f93:	41 0f b6 43 02       	movzbl 0x2(%r11),%eax
     f98:	45 0f b6 53 01       	movzbl 0x1(%r11),%r10d
     f9d:	c1 e0 10             	shl    $0x10,%eax
     fa0:	41 c1 e2 08          	shl    $0x8,%r10d
     fa4:	44 09 d0             	or     %r10d,%eax
     fa7:	45 0f b6 13          	movzbl (%r11),%r10d
     fab:	44 09 d0             	or     %r10d,%eax
     fae:	41 89 c2             	mov    %eax,%r10d
     fb1:	41 c1 ea 05          	shr    $0x5,%r10d
     fb5:	41 31 c2             	xor    %eax,%r10d
     fb8:	41 83 e2 38          	and    $0x38,%r10d
     fbc:	44 89 d3             	mov    %r10d,%ebx
     fbf:	41 31 c2             	xor    %eax,%r10d
     fc2:	c1 e3 05             	shl    $0x5,%ebx
     fc5:	89 d8                	mov    %ebx,%eax
     fc7:	44 31 d0             	xor    %r10d,%eax
     fca:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     fce:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
     fd2:	41 8b 02             	mov    (%r10),%eax
     fd5:	45 0f b7 12          	movzwl (%r10),%r10d
     fd9:	c1 e8 10             	shr    $0x10,%eax
     fdc:	66 45 89 13          	mov    %r10w,(%r11)
     fe0:	41 88 43 02          	mov    %al,0x2(%r11)
     fe4:	49 8d 40 04          	lea    0x4(%r8),%rax
     fe8:	48 39 c8             	cmp    %rcx,%rax
     feb:	0f 83 17 01 00 00    	jae    1108 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1108>
     ff1:	4e 8d 5c 0a 0c       	lea    0xc(%rdx,%r9,1),%r11
     ff6:	41 0f b6 43 02       	movzbl 0x2(%r11),%eax
     ffb:	45 0f b6 53 01       	movzbl 0x1(%r11),%r10d
    1000:	c1 e0 10             	shl    $0x10,%eax
    1003:	41 c1 e2 08          	shl    $0x8,%r10d
    1007:	44 09 d0             	or     %r10d,%eax
    100a:	45 0f b6 13          	movzbl (%r11),%r10d
    100e:	44 09 d0             	or     %r10d,%eax
    1011:	41 89 c2             	mov    %eax,%r10d
    1014:	41 c1 ea 05          	shr    $0x5,%r10d
    1018:	41 31 c2             	xor    %eax,%r10d
    101b:	41 83 e2 38          	and    $0x38,%r10d
    101f:	44 89 d3             	mov    %r10d,%ebx
    1022:	41 31 c2             	xor    %eax,%r10d
    1025:	c1 e3 05             	shl    $0x5,%ebx
    1028:	89 d8                	mov    %ebx,%eax
    102a:	44 31 d0             	xor    %r10d,%eax
    102d:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1031:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
    1035:	41 8b 02             	mov    (%r10),%eax
    1038:	45 0f b7 12          	movzwl (%r10),%r10d
    103c:	c1 e8 10             	shr    $0x10,%eax
    103f:	66 45 89 13          	mov    %r10w,(%r11)
    1043:	41 88 43 02          	mov    %al,0x2(%r11)
    1047:	49 8d 40 05          	lea    0x5(%r8),%rax
    104b:	48 39 c8             	cmp    %rcx,%rax
    104e:	0f 83 b4 00 00 00    	jae    1108 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1108>
    1054:	4e 8d 5c 0a 0f       	lea    0xf(%rdx,%r9,1),%r11
    1059:	49 83 c0 06          	add    $0x6,%r8
    105d:	41 0f b6 43 02       	movzbl 0x2(%r11),%eax
    1062:	45 0f b6 53 01       	movzbl 0x1(%r11),%r10d
    1067:	c1 e0 10             	shl    $0x10,%eax
    106a:	41 c1 e2 08          	shl    $0x8,%r10d
    106e:	44 09 d0             	or     %r10d,%eax
    1071:	45 0f b6 13          	movzbl (%r11),%r10d
    1075:	44 09 d0             	or     %r10d,%eax
    1078:	41 89 c2             	mov    %eax,%r10d
    107b:	41 c1 ea 05          	shr    $0x5,%r10d
    107f:	41 31 c2             	xor    %eax,%r10d
    1082:	41 83 e2 38          	and    $0x38,%r10d
    1086:	44 89 d3             	mov    %r10d,%ebx
    1089:	41 31 c2             	xor    %eax,%r10d
    108c:	c1 e3 05             	shl    $0x5,%ebx
    108f:	89 d8                	mov    %ebx,%eax
    1091:	44 31 d0             	xor    %r10d,%eax
    1094:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1098:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
    109c:	41 8b 02             	mov    (%r10),%eax
    109f:	45 0f b7 12          	movzwl (%r10),%r10d
    10a3:	c1 e8 10             	shr    $0x10,%eax
    10a6:	66 45 89 13          	mov    %r10w,(%r11)
    10aa:	41 88 43 02          	mov    %al,0x2(%r11)
    10ae:	49 39 c8             	cmp    %rcx,%r8
    10b1:	73 55                	jae    1108 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1108>
    10b3:	4a 8d 4c 0a 12       	lea    0x12(%rdx,%r9,1),%rcx
    10b8:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
    10bc:	0f b6 51 02          	movzbl 0x2(%rcx),%edx
    10c0:	c1 e0 08             	shl    $0x8,%eax
    10c3:	c1 e2 10             	shl    $0x10,%edx
    10c6:	09 d0                	or     %edx,%eax
    10c8:	0f b6 11             	movzbl (%rcx),%edx
    10cb:	09 d0                	or     %edx,%eax
    10cd:	89 c2                	mov    %eax,%edx
    10cf:	c1 ea 05             	shr    $0x5,%edx
    10d2:	31 c2                	xor    %eax,%edx
    10d4:	83 e2 38             	and    $0x38,%edx
    10d7:	31 d0                	xor    %edx,%eax
    10d9:	c1 e2 05             	shl    $0x5,%edx
    10dc:	31 d0                	xor    %edx,%eax
    10de:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    10e2:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    10e6:	8b 02                	mov    (%rdx),%eax
    10e8:	0f b7 12             	movzwl (%rdx),%edx
    10eb:	c1 e8 10             	shr    $0x10,%eax
    10ee:	66 89 11             	mov    %dx,(%rcx)
    10f1:	88 41 02             	mov    %al,0x2(%rcx)
    10f4:	c5 f8 77             	vzeroupper
    10f7:	5b                   	pop    %rbx
    10f8:	41 5c                	pop    %r12
    10fa:	41 5d                	pop    %r13
    10fc:	41 5e                	pop    %r14
    10fe:	41 5f                	pop    %r15
    1100:	5d                   	pop    %rbp
    1101:	c3                   	ret
    1102:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1108:	c5 f8 77             	vzeroupper
    110b:	5b                   	pop    %rbx
    110c:	41 5c                	pop    %r12
    110e:	41 5d                	pop    %r13
    1110:	41 5e                	pop    %r14
    1112:	41 5f                	pop    %r15
    1114:	5d                   	pop    %rbp
    1115:	c3                   	ret
    1116:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    111d:	00 00 00 
    1120:	49 89 c8             	mov    %rcx,%r8
    1123:	e9 f8 fb ff ff       	jmp    d20 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd20>
    1128:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    112f:	00 
    1130:	c3                   	ret
    1131:	49 8d 41 28          	lea    0x28(%r9),%rax
    1135:	4d 89 c8             	mov    %r9,%r8
    1138:	e9 bb f7 ff ff       	jmp    8f8 <jshc_channel::avx2_chain_tilexy(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f8>
    113d:	0f 1f 00             	nopl   (%rax)

0000000000001140 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1140:	f3 0f 1e fa          	endbr64
    1144:	4d 85 c0             	test   %r8,%r8
    1147:	0f 84 83 11 00 00    	je     22d0 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1190>
    114d:	55                   	push   %rbp
    114e:	b8 00 04 00 00       	mov    $0x400,%eax
    1153:	49 89 d2             	mov    %rdx,%r10
    1156:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    115a:	49 89 cb             	mov    %rcx,%r11
    115d:	48 89 e5             	mov    %rsp,%rbp
    1160:	41 57                	push   %r15
    1162:	41 56                	push   %r14
    1164:	41 55                	push   %r13
    1166:	41 54                	push   %r12
    1168:	53                   	push   %rbx
    1169:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    116d:	48 39 c2             	cmp    %rax,%rdx
    1170:	48 0f 47 d0          	cmova  %rax,%rdx
    1174:	31 c0                	xor    %eax,%eax
    1176:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
    117d:	00 00 00 
    1180:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
    1185:	48 83 c0 40          	add    $0x40,%rax
    1189:	48 39 d0             	cmp    %rdx,%rax
    118c:	72 f2                	jb     1180 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
    118e:	4d 89 d1             	mov    %r10,%r9
    1191:	4c 89 da             	mov    %r11,%rdx
    1194:	31 c9                	xor    %ecx,%ecx
    1196:	eb 5d                	jmp    11f5 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb5>
    1198:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    119f:	00 
    11a0:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
    11a5:	41 0f b6 59 02       	movzbl 0x2(%r9),%ebx
    11aa:	48 ff c1             	inc    %rcx
    11ad:	48 83 c2 03          	add    $0x3,%rdx
    11b1:	49 83 c1 03          	add    $0x3,%r9
    11b5:	c1 e3 10             	shl    $0x10,%ebx
    11b8:	c1 e0 08             	shl    $0x8,%eax
    11bb:	09 d8                	or     %ebx,%eax
    11bd:	41 0f b6 59 fd       	movzbl -0x3(%r9),%ebx
    11c2:	09 d8                	or     %ebx,%eax
    11c4:	89 c3                	mov    %eax,%ebx
    11c6:	c1 eb 05             	shr    $0x5,%ebx
    11c9:	31 c3                	xor    %eax,%ebx
    11cb:	83 e3 38             	and    $0x38,%ebx
    11ce:	31 d8                	xor    %ebx,%eax
    11d0:	c1 e3 05             	shl    $0x5,%ebx
    11d3:	31 d8                	xor    %ebx,%eax
    11d5:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    11d9:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    11dd:	8b 03                	mov    (%rbx),%eax
    11df:	0f b7 1b             	movzwl (%rbx),%ebx
    11e2:	c1 e8 10             	shr    $0x10,%eax
    11e5:	66 89 5a fd          	mov    %bx,-0x3(%rdx)
    11e9:	88 42 ff             	mov    %al,-0x1(%rdx)
    11ec:	49 39 c8             	cmp    %rcx,%r8
    11ef:	0f 84 cb 10 00 00    	je     22c0 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1180>
    11f5:	f6 c2 3f             	test   $0x3f,%dl
    11f8:	75 a6                	jne    11a0 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    11fa:	48 8d 41 48          	lea    0x48(%rcx),%rax
    11fe:	49 39 c0             	cmp    %rax,%r8
    1201:	0f 82 ca 10 00 00    	jb     22d1 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1191>
    1207:	41 b9 38 00 00 00    	mov    $0x38,%r9d
    120d:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    1211:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1216:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 121e <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xde>
    121d:	00 
    121e:	c4 41 79 6e d9       	vmovd  %r9d,%xmm11
    1223:	49 8d 14 03          	lea    (%r11,%rax,1),%rdx
    1227:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    122c:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1234 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf4>
    1233:	00 
    1234:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # 123c <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xfc>
    123b:	00 
    123c:	49 8d 84 02 00 04 00 	lea    0x400(%r10,%rax,1),%rax
    1243:	00 
    1244:	c4 42 7d 58 db       	vpbroadcastd %xmm11,%ymm11
    1249:	eb 08                	jmp    1253 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x113>
    124b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1250:	4c 89 c9             	mov    %r9,%rcx
    1253:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
    125a:	4d 39 c8             	cmp    %r9,%r8
    125d:	72 15                	jb     1274 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x134>
    125f:	0f 18 00             	prefetchnta (%rax)
    1262:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1266:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    126d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    1274:	c5 fa 6f 80 00 fc ff 	vmovdqu -0x400(%rax),%xmm0
    127b:	ff 
    127c:	c5 fa 7e 88 10 fc ff 	vmovq  -0x3f0(%rax),%xmm1
    1283:	ff 
    1284:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    128b:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1291:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1297:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    129d:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    12a2:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
    12a7:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
    12ab:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
    12b0:	c5 ed 72 f1 05       	vpslld $0x5,%ymm1,%ymm2
    12b5:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
    12b9:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
    12bd:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    12c3:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    12c8:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    12ce:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    12d3:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    12d9:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    12de:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    12e3:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    12e8:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    12ed:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    12f3:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    12f9:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    12fe:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1303:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1309:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    130f:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1315:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    131b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1320:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1325:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    132c:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1333:	c4 21 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm10
    1339:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    133d:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1342:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    1349:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1350:	c5 29 6c d1          	vpunpcklqdq %xmm1,%xmm10,%xmm10
    1354:	c5 fa 7e 88 68 fb ff 	vmovq  -0x498(%rax),%xmm1
    135b:	ff 
    135c:	c4 63 2d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm10,%ymm10
    1362:	c5 fa 6f 80 58 fb ff 	vmovdqu -0x4a8(%rax),%xmm0
    1369:	ff 
    136a:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
    136f:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1375:	c4 42 4d 36 d2       	vpermd %ymm10,%ymm6,%ymm10
    137a:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1380:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1385:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
    138a:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
    138e:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
    1393:	c5 ed 72 f1 05       	vpslld $0x5,%ymm1,%ymm2
    1398:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
    139c:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
    13a0:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    13a6:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    13ab:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    13b1:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    13b6:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    13bc:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    13c1:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    13c6:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    13cb:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    13d0:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    13d6:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    13dc:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    13e1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    13e6:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    13ec:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    13f2:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    13f8:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    13fe:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1403:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1408:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    140f:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    1416:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    141a:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    141f:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    1425:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    142c:	c4 a3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm3,%xmm3
    1433:	c5 e1 6c d9          	vpunpcklqdq %xmm1,%xmm3,%xmm3
    1437:	c5 fa 7e 88 80 fb ff 	vmovq  -0x480(%rax),%xmm1
    143e:	ff 
    143f:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
    1445:	c5 fa 6f 80 70 fb ff 	vmovdqu -0x490(%rax),%xmm0
    144c:	ff 
    144d:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
    1452:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1458:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
    145d:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1463:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1468:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
    146d:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
    1471:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
    1476:	c5 ed 72 f1 05       	vpslld $0x5,%ymm1,%ymm2
    147b:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
    147f:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
    1483:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1489:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    148e:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1494:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1499:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    149f:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    14a4:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    14a9:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    14ae:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    14b3:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    14b9:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    14bf:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    14c4:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    14c9:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    14cf:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    14d5:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    14db:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    14e1:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    14e6:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    14eb:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    14f2:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    14f9:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    14ff:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1503:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    1508:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    150f:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1516:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
    151a:	c5 fa 7e 88 98 fb ff 	vmovq  -0x468(%rax),%xmm1
    1521:	ff 
    1522:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    1528:	c5 fa 6f 80 88 fb ff 	vmovdqu -0x478(%rax),%xmm0
    152f:	ff 
    1530:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    1535:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    153b:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
    1540:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1546:	c5 79 6f f2          	vmovdqa %xmm2,%xmm14
    154a:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1550:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1555:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
    155a:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
    155e:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
    1563:	c5 c5 72 f1 05       	vpslld $0x5,%ymm1,%ymm7
    1568:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
    156c:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
    1570:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1576:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    157b:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1581:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1586:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    158c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1591:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1596:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    159b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    15a0:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    15a6:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    15ac:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    15b2:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    15b8:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    15bd:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    15c2:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    15c7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    15cc:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    15d2:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    15d8:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
    15de:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    15e5:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    15ec:	c4 23 31 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm9,%xmm9
    15f3:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    15f7:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    15fc:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1603:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    1607:	c5 fa 7e 88 b0 fb ff 	vmovq  -0x450(%rax),%xmm1
    160e:	ff 
    160f:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    1615:	c5 fa 6f 80 a0 fb ff 	vmovdqu -0x460(%rax),%xmm0
    161c:	ff 
    161d:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
    1622:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1628:	c4 42 4d 36 c9       	vpermd %ymm9,%ymm6,%ymm9
    162d:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1633:	c4 41 79 6f f9       	vmovdqa %xmm9,%xmm15
    1638:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    163e:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1643:	c4 43 31 0f cf 08    	vpalignr $0x8,%xmm15,%xmm9,%xmm9
    1649:	c4 c1 69 6c d7       	vpunpcklqdq %xmm15,%xmm2,%xmm2
    164e:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
    1653:	c4 c3 6d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm2,%ymm2
    1659:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
    165d:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
    1662:	c5 c5 72 f1 05       	vpslld $0x5,%ymm1,%ymm7
    1667:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
    166b:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
    166f:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1675:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    167a:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1680:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1685:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    168b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1690:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1695:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    169a:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    169f:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    16a5:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    16ab:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    16b0:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    16b5:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    16bb:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    16c1:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    16c7:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    16cd:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    16d2:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    16d7:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
    16de:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    16e5:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
    16eb:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    16ef:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
    16f4:	c4 23 39 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm8,%xmm8
    16fb:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
    1702:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    1706:	c5 fa 7e 88 c8 fb ff 	vmovq  -0x438(%rax),%xmm1
    170d:	ff 
    170e:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    1714:	c5 fa 6f 80 b8 fb ff 	vmovdqu -0x448(%rax),%xmm0
    171b:	ff 
    171c:	c4 62 3d 00 c4       	vpshufb %ymm4,%ymm8,%ymm8
    1721:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
    1727:	c4 42 4d 36 c0       	vpermd %ymm8,%ymm6,%ymm8
    172c:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1732:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1737:	c5 f5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm1
    173c:	c5 fd ef c9          	vpxor  %ymm1,%ymm0,%ymm1
    1740:	c4 c1 75 db cb       	vpand  %ymm11,%ymm1,%ymm1
    1745:	c5 c5 72 f1 05       	vpslld $0x5,%ymm1,%ymm7
    174a:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
    174e:	c5 fd ef c1          	vpxor  %ymm1,%ymm0,%ymm0
    1752:	c4 e3 7d 39 c1 01    	vextracti128 $0x1,%ymm0,%xmm1
    1758:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    175d:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1763:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1768:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    176d:	c4 c1 79 7e cc       	vmovd  %xmm1,%r12d
    1772:	c4 c3 79 16 ce 02    	vpextrd $0x2,%xmm1,%r14d
    1778:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    177e:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1784:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1789:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    178e:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1793:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1798:	c4 c3 79 16 cc 01    	vpextrd $0x1,%xmm1,%r12d
    179e:	c4 c3 79 16 ce 03    	vpextrd $0x3,%xmm1,%r14d
    17a4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    17a9:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    17ae:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    17b4:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
    17ba:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    17c0:	c4 a3 41 22 3c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm7,%xmm7
    17c7:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
    17ce:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    17d5:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    17d9:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    17de:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    17e5:	c5 f1 6c cf          	vpunpcklqdq %xmm7,%xmm1,%xmm1
    17e9:	c5 fa 7e b8 e0 fb ff 	vmovq  -0x420(%rax),%xmm7
    17f0:	ff 
    17f1:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    17f7:	c5 fa 6f 80 d0 fb ff 	vmovdqu -0x430(%rax),%xmm0
    17fe:	ff 
    17ff:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    1804:	c4 e3 41 0f f8 0c    	vpalignr $0xc,%xmm0,%xmm7,%xmm7
    180a:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
    180f:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    1815:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    181a:	c5 c5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm7
    181f:	c5 fd ef ff          	vpxor  %ymm7,%ymm0,%ymm7
    1823:	c4 c1 45 db fb       	vpand  %ymm11,%ymm7,%ymm7
    1828:	c5 9d 72 f7 05       	vpslld $0x5,%ymm7,%ymm12
    182d:	c4 c1 7d ef c4       	vpxor  %ymm12,%ymm0,%ymm0
    1832:	c5 fd ef c7          	vpxor  %ymm7,%ymm0,%ymm0
    1836:	c4 e3 7d 39 c7 01    	vextracti128 $0x1,%ymm0,%xmm7
    183c:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1841:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1847:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    184c:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    1852:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1857:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    185c:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1861:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1866:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    186c:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    1872:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1877:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    187c:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1882:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1888:	c4 21 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm12
    188e:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1894:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1899:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    189e:	c4 23 19 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm12,%xmm12
    18a5:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    18ac:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    18b2:	c4 c1 41 6c fc       	vpunpcklqdq %xmm12,%xmm7,%xmm7
    18b7:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
    18bc:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    18c3:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    18ca:	c4 c1 79 6c c4       	vpunpcklqdq %xmm12,%xmm0,%xmm0
    18cf:	c5 7a 7e a0 f8 fb ff 	vmovq  -0x408(%rax),%xmm12
    18d6:	ff 
    18d7:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    18dd:	c5 fa 6f b8 e8 fb ff 	vmovdqu -0x418(%rax),%xmm7
    18e4:	ff 
    18e5:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    18ea:	c4 63 19 0f e7 0c    	vpalignr $0xc,%xmm7,%xmm12,%xmm12
    18f0:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
    18f5:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
    18fb:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    18ff:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1905:	c4 e2 45 00 fd       	vpshufb %ymm5,%ymm7,%ymm7
    190a:	c5 9d 72 d7 05       	vpsrld $0x5,%ymm7,%ymm12
    190f:	c4 41 45 ef e4       	vpxor  %ymm12,%ymm7,%ymm12
    1914:	c4 41 1d db e3       	vpand  %ymm11,%ymm12,%ymm12
    1919:	c4 c1 15 72 f4 05    	vpslld $0x5,%ymm12,%ymm13
    191f:	c4 c1 45 ef fd       	vpxor  %ymm13,%ymm7,%ymm7
    1924:	c4 c1 45 ef fc       	vpxor  %ymm12,%ymm7,%ymm7
    1929:	c4 c3 7d 39 fc 01    	vextracti128 $0x1,%ymm7,%xmm12
    192f:	c4 c1 79 7e f9       	vmovd  %xmm7,%r9d
    1934:	c4 c3 79 16 fb 02    	vpextrd $0x2,%xmm7,%r11d
    193a:	c4 41 79 7e e4       	vmovd  %xmm12,%r12d
    193f:	c4 43 79 16 e6 02    	vpextrd $0x2,%xmm12,%r14d
    1945:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    194a:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    194f:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1954:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1959:	c4 43 79 16 e4 01    	vpextrd $0x1,%xmm12,%r12d
    195f:	c4 43 79 16 e6 03    	vpextrd $0x3,%xmm12,%r14d
    1965:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    196a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    196f:	c4 c3 79 16 f9 01    	vpextrd $0x1,%xmm7,%r9d
    1975:	c4 c3 79 16 fb 03    	vpextrd $0x3,%xmm7,%r11d
    197b:	c4 21 79 6e 2c be    	vmovd  (%rsi,%r15,4),%xmm13
    1981:	c4 21 79 6e 24 ae    	vmovd  (%rsi,%r13,4),%xmm12
    1987:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    198c:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
    1992:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1999:	c4 23 11 22 2c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm13,%xmm13
    19a0:	c4 23 19 22 24 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm12,%xmm12
    19a7:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    19ac:	c4 a3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm7,%xmm7
    19b3:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    19b7:	c4 41 19 6c e5       	vpunpcklqdq %xmm13,%xmm12,%xmm12
    19bc:	c5 79 6e 2c 9e       	vmovd  (%rsi,%rbx,4),%xmm13
    19c1:	c4 23 11 22 2c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm13,%xmm13
    19c8:	c5 fd e7 52 80       	vmovntdq %ymm2,-0x80(%rdx)
    19cd:	c5 79 7f c2          	vmovdqa %xmm8,%xmm2
    19d1:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    19d7:	c4 c1 41 6c fd       	vpunpcklqdq %xmm13,%xmm7,%xmm7
    19dc:	c5 79 6f eb          	vmovdqa %xmm3,%xmm13
    19e0:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    19e6:	c4 c3 45 38 fc 01    	vinserti128 $0x1,%xmm12,%ymm7,%ymm7
    19ec:	c4 c3 61 0f dd 08    	vpalignr $0x8,%xmm13,%xmm3,%xmm3
    19f2:	c4 41 79 6f e2       	vmovdqa %xmm10,%xmm12
    19f7:	c4 e2 45 00 fc       	vpshufb %ymm4,%ymm7,%ymm7
    19fc:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
    1a02:	c4 c3 65 38 de 01    	vinserti128 $0x1,%xmm14,%ymm3,%ymm3
    1a08:	c4 e2 4d 36 ff       	vpermd %ymm7,%ymm6,%ymm7
    1a0d:	c4 41 29 6c d5       	vpunpcklqdq %xmm13,%xmm10,%xmm10
    1a12:	c5 fd e7 9a 60 ff ff 	vmovntdq %ymm3,-0xa0(%rdx)
    1a19:	ff 
    1a1a:	c4 43 1d 38 e2 01    	vinserti128 $0x1,%xmm10,%ymm12,%ymm12
    1a20:	c5 f9 6f df          	vmovdqa %xmm7,%xmm3
    1a24:	c5 79 6f d1          	vmovdqa %xmm1,%xmm10
    1a28:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1a2e:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1a34:	c4 41 39 6c c2       	vpunpcklqdq %xmm10,%xmm8,%xmm8
    1a39:	c5 7d e7 a2 40 ff ff 	vmovntdq %ymm12,-0xc0(%rdx)
    1a40:	ff 
    1a41:	c4 c3 71 0f ca 08    	vpalignr $0x8,%xmm10,%xmm1,%xmm1
    1a47:	c4 e3 41 0f fb 08    	vpalignr $0x8,%xmm3,%xmm7,%xmm7
    1a4d:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
    1a51:	c4 c3 6d 38 d0 01    	vinserti128 $0x1,%xmm8,%ymm2,%ymm2
    1a57:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1a5d:	c4 e3 7d 38 c7 01    	vinserti128 $0x1,%xmm7,%ymm0,%ymm0
    1a63:	c5 fd e7 52 a0       	vmovntdq %ymm2,-0x60(%rdx)
    1a68:	c5 fd e7 4a c0       	vmovntdq %ymm1,-0x40(%rdx)
    1a6d:	c5 fd e7 42 e0       	vmovntdq %ymm0,-0x20(%rdx)
    1a72:	4d 39 d0             	cmp    %r10,%r8
    1a75:	0f 83 d5 f7 ff ff    	jae    1250 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x110>
    1a7b:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1a80:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1a85:	48 8d 41 68          	lea    0x68(%rcx),%rax
    1a89:	0f ae f8             	sfence
    1a8c:	49 39 c0             	cmp    %rax,%r8
    1a8f:	0f 82 35 04 00 00    	jb     1eca <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd8a>
    1a95:	b9 38 00 00 00       	mov    $0x38,%ecx
    1a9a:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1a9f:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    1aa3:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1aab <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x96b>
    1aaa:	00 
    1aab:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1ab0:	c5 79 6e c1          	vmovd  %ecx,%xmm8
    1ab4:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1abc <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x97c>
    1abb:	00 
    1abc:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
    1ac0:	c5 fd 6f 35 00 00 00 	vmovdqa 0x0(%rip),%ymm6        # 1ac8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x988>
    1ac7:	00 
    1ac8:	4c 01 da             	add    %r11,%rdx
    1acb:	c4 42 7d 58 c0       	vpbroadcastd %xmm8,%ymm8
    1ad0:	c5 fa 6f 10          	vmovdqu (%rax),%xmm2
    1ad4:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
    1ad9:	48 83 c2 60          	add    $0x60,%rdx
    1add:	48 83 c0 60          	add    $0x60,%rax
    1ae1:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
    1ae6:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
    1aec:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
    1af2:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
    1af7:	c5 fd 72 d2 05       	vpsrld $0x5,%ymm2,%ymm0
    1afc:	c5 ed ef c0          	vpxor  %ymm0,%ymm2,%ymm0
    1b00:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
    1b05:	c5 f5 72 f0 05       	vpslld $0x5,%ymm0,%ymm1
    1b0a:	c5 ed ef d1          	vpxor  %ymm1,%ymm2,%ymm2
    1b0e:	c5 fa 6f 48 b8       	vmovdqu -0x48(%rax),%xmm1
    1b13:	c5 ed ef d0          	vpxor  %ymm0,%ymm2,%ymm2
    1b17:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
    1b1c:	c4 e3 7d 39 d7 01    	vextracti128 $0x1,%ymm2,%xmm7
    1b22:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
    1b28:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
    1b2e:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
    1b33:	c5 fd 72 d1 05       	vpsrld $0x5,%ymm1,%ymm0
    1b38:	c5 f5 ef c0          	vpxor  %ymm0,%ymm1,%ymm0
    1b3c:	c4 c1 7d db c0       	vpand  %ymm8,%ymm0,%ymm0
    1b41:	c5 e5 72 f0 05       	vpslld $0x5,%ymm0,%ymm3
    1b46:	c5 f5 ef cb          	vpxor  %ymm3,%ymm1,%ymm1
    1b4a:	c5 fa 7e 58 e0       	vmovq  -0x20(%rax),%xmm3
    1b4f:	c5 f5 ef c8          	vpxor  %ymm0,%ymm1,%ymm1
    1b53:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
    1b58:	c4 c3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm9
    1b5e:	c4 e3 61 0f d8 0c    	vpalignr $0xc,%xmm0,%xmm3,%xmm3
    1b64:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
    1b6a:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1b6f:	c5 e5 72 d0 05       	vpsrld $0x5,%ymm0,%ymm3
    1b74:	c5 fd ef db          	vpxor  %ymm3,%ymm0,%ymm3
    1b78:	c4 c1 65 db d8       	vpand  %ymm8,%ymm3,%ymm3
    1b7d:	c5 ad 72 f3 05       	vpslld $0x5,%ymm3,%ymm10
    1b82:	c4 c1 7d ef c2       	vpxor  %ymm10,%ymm0,%ymm0
    1b87:	c5 fd ef c3          	vpxor  %ymm3,%ymm0,%ymm0
    1b8b:	c5 fa 6f 58 e8       	vmovdqu -0x18(%rax),%xmm3
    1b90:	c4 c3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm10
    1b96:	c4 63 21 0f db 0c    	vpalignr $0xc,%xmm3,%xmm11,%xmm11
    1b9c:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
    1ba2:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
    1ba7:	c5 a5 72 d3 05       	vpsrld $0x5,%ymm3,%ymm11
    1bac:	c4 41 65 ef db       	vpxor  %ymm11,%ymm3,%ymm11
    1bb1:	c4 41 25 db d8       	vpand  %ymm8,%ymm11,%ymm11
    1bb6:	c4 c1 1d 72 f3 05    	vpslld $0x5,%ymm11,%ymm12
    1bbc:	c4 c1 65 ef dc       	vpxor  %ymm12,%ymm3,%ymm3
    1bc1:	c4 c1 65 ef db       	vpxor  %ymm11,%ymm3,%ymm3
    1bc6:	c4 c3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm11
    1bcc:	c5 f9 7e d9          	vmovd  %xmm3,%ecx
    1bd0:	c4 c3 79 16 db 02    	vpextrd $0x2,%xmm3,%r11d
    1bd6:	c4 41 79 7e dc       	vmovd  %xmm11,%r12d
    1bdb:	c4 43 79 16 de 02    	vpextrd $0x2,%xmm11,%r14d
    1be1:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1be6:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1beb:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1bf0:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1bf5:	c4 43 79 16 dc 01    	vpextrd $0x1,%xmm11,%r12d
    1bfb:	c4 43 79 16 de 03    	vpextrd $0x3,%xmm11,%r14d
    1c01:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1c06:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1c0b:	c4 e3 79 16 d9 01    	vpextrd $0x1,%xmm3,%ecx
    1c11:	c4 c3 79 16 db 03    	vpextrd $0x3,%xmm3,%r11d
    1c17:	c4 21 79 6e 24 be    	vmovd  (%rsi,%r15,4),%xmm12
    1c1d:	c4 21 79 6e 1c ae    	vmovd  (%rsi,%r13,4),%xmm11
    1c23:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1c27:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1c2c:	c4 23 19 22 24 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm12,%xmm12
    1c33:	c4 23 21 22 1c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm11,%xmm11
    1c3a:	c4 43 79 16 d6 02    	vpextrd $0x2,%xmm10,%r14d
    1c40:	c4 a1 79 6e 1c 96    	vmovd  (%rsi,%r10,4),%xmm3
    1c46:	c4 41 79 7e d4       	vmovd  %xmm10,%r12d
    1c4b:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1c50:	c4 43 79 16 d6 03    	vpextrd $0x3,%xmm10,%r14d
    1c56:	c4 41 21 6c dc       	vpunpcklqdq %xmm12,%xmm11,%xmm11
    1c5b:	c5 79 6e 24 9e       	vmovd  (%rsi,%rbx,4),%xmm12
    1c60:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1c65:	c4 43 79 16 d4 01    	vpextrd $0x1,%xmm10,%r12d
    1c6b:	c4 e3 61 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm3,%xmm3
    1c72:	c5 f9 7e c1          	vmovd  %xmm0,%ecx
    1c76:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1c7b:	c4 23 19 22 24 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm12,%xmm12
    1c82:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1c88:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1c8d:	c4 e3 79 16 c1 01    	vpextrd $0x1,%xmm0,%ecx
    1c93:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1c98:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1c9e:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1ca2:	c4 c1 61 6c dc       	vpunpcklqdq %xmm12,%xmm3,%xmm3
    1ca7:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1cac:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1cb1:	c4 c3 65 38 db 01    	vinserti128 $0x1,%xmm11,%ymm3,%ymm3
    1cb7:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    1cbd:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
    1cc3:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1cc9:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
    1cce:	c4 23 21 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm11,%xmm11
    1cd5:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
    1cdc:	c4 43 79 16 ce 02    	vpextrd $0x2,%xmm9,%r14d
    1ce2:	c4 e3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm0,%xmm0
    1ce9:	c4 41 79 7e cc       	vmovd  %xmm9,%r12d
    1cee:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1cf3:	c4 43 79 16 ce 03    	vpextrd $0x3,%xmm9,%r14d
    1cf9:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1cfe:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
    1d03:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1d08:	c4 43 79 16 cc 01    	vpextrd $0x1,%xmm9,%r12d
    1d0e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1d13:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1d18:	c5 f9 7e c9          	vmovd  %xmm1,%ecx
    1d1c:	c4 e2 4d 36 db       	vpermd %ymm3,%ymm6,%ymm3
    1d21:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
    1d28:	c4 21 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm9
    1d2e:	c4 c3 79 16 cb 02    	vpextrd $0x2,%xmm1,%r11d
    1d34:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1d39:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1d3e:	c4 e3 79 16 c9 01    	vpextrd $0x1,%xmm1,%ecx
    1d44:	c4 c3 79 16 cb 03    	vpextrd $0x3,%xmm1,%r11d
    1d4a:	c4 c1 79 6c c3       	vpunpcklqdq %xmm11,%xmm0,%xmm0
    1d4f:	c4 23 31 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm9,%xmm9
    1d56:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1d5a:	c4 c1 79 7e fc       	vmovd  %xmm7,%r12d
    1d5f:	c4 c3 7d 38 c2 01    	vinserti128 $0x1,%xmm10,%ymm0,%ymm0
    1d65:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1d6b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1d70:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
    1d76:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1d7b:	c4 c3 79 16 fc 01    	vpextrd $0x1,%xmm7,%r12d
    1d81:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1d86:	c4 23 29 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm10,%xmm10
    1d8d:	c4 c3 79 16 fe 02    	vpextrd $0x2,%xmm7,%r14d
    1d93:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1d98:	c4 e2 4d 36 c0       	vpermd %ymm0,%ymm6,%ymm0
    1d9d:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    1da4:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1da9:	c5 f9 7e d1          	vmovd  %xmm2,%ecx
    1dad:	c4 c3 79 16 fe 03    	vpextrd $0x3,%xmm7,%r14d
    1db3:	c4 41 31 6c ca       	vpunpcklqdq %xmm10,%xmm9,%xmm9
    1db8:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
    1dbd:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1dc2:	c4 e3 79 16 d1 01    	vpextrd $0x1,%xmm2,%ecx
    1dc8:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1dcc:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1dd1:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
    1dd8:	c4 c3 79 16 d3 02    	vpextrd $0x2,%xmm2,%r11d
    1dde:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1de3:	c4 c3 79 16 d3 03    	vpextrd $0x3,%xmm2,%r11d
    1de9:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1dee:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1df3:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
    1df7:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1dfd:	c4 c3 75 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm1,%ymm1
    1e03:	c4 21 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm9
    1e09:	c4 a1 79 6e 3c ae    	vmovd  (%rsi,%r13,4),%xmm7
    1e0f:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    1e15:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
    1e1a:	c4 23 31 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm9,%xmm9
    1e21:	c4 a3 41 22 3c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm7,%xmm7
    1e28:	c4 e2 4d 36 c9       	vpermd %ymm1,%ymm6,%ymm1
    1e2d:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    1e34:	c5 79 6f d9          	vmovdqa %xmm1,%xmm11
    1e38:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1e3e:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    1e43:	c5 79 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm9
    1e48:	c4 c3 71 0f cb 08    	vpalignr $0x8,%xmm11,%xmm1,%xmm1
    1e4e:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1e52:	c4 c3 75 38 ca 01    	vinserti128 $0x1,%xmm10,%ymm1,%ymm1
    1e58:	49 83 c1 20          	add    $0x20,%r9
    1e5c:	c4 23 31 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm9,%xmm9
    1e63:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1e68:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1e6d:	c5 79 6f cb          	vmovdqa %xmm3,%xmm9
    1e71:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    1e77:	c4 e3 6d 38 d7 01    	vinserti128 $0x1,%xmm7,%ymm2,%ymm2
    1e7d:	c4 c3 61 0f d9 08    	vpalignr $0x8,%xmm9,%xmm3,%xmm3
    1e83:	c4 c1 79 6c c1       	vpunpcklqdq %xmm9,%xmm0,%xmm0
    1e88:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
    1e8d:	c4 e3 7d 38 c3 01    	vinserti128 $0x1,%xmm3,%ymm0,%ymm0
    1e93:	c4 e2 4d 36 d2       	vpermd %ymm2,%ymm6,%ymm2
    1e98:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1e9d:	c5 f9 6f fa          	vmovdqa %xmm2,%xmm7
    1ea1:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1ea7:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    1eac:	c4 e3 45 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm7,%ymm2
    1eb2:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    1eb7:	49 39 c8             	cmp    %rcx,%r8
    1eba:	0f 83 10 fc ff ff    	jae    1ad0 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x990>
    1ec0:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    1ec5:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    1eca:	49 8d 51 08          	lea    0x8(%r9),%rdx
    1ece:	49 39 d0             	cmp    %rdx,%r8
    1ed1:	0f 82 53 01 00 00    	jb     202a <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xeea>
    1ed7:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    1edb:	4c 89 54 24 f8       	mov    %r10,-0x8(%rsp)
    1ee0:	41 b9 38 00 00 00    	mov    $0x38,%r9d
    1ee6:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1eee <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdae>
    1eed:	00 
    1eee:	4c 89 5c 24 f0       	mov    %r11,-0x10(%rsp)
    1ef3:	c4 c1 79 6e c9       	vmovd  %r9d,%xmm1
    1ef8:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1f00 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdc0>
    1eff:	00 
    1f00:	49 8d 0c 02          	lea    (%r10,%rax,1),%rcx
    1f04:	c4 e2 7d 58 c9       	vpbroadcastd %xmm1,%ymm1
    1f09:	4c 01 d8             	add    %r11,%rax
    1f0c:	0f 1f 40 00          	nopl   0x0(%rax)
    1f10:	c5 fa 6f 01          	vmovdqu (%rcx),%xmm0
    1f14:	c5 fa 7e 51 10       	vmovq  0x10(%rcx),%xmm2
    1f19:	48 83 c0 18          	add    $0x18,%rax
    1f1d:	48 83 c1 18          	add    $0x18,%rcx
    1f21:	c4 e3 69 0f d0 0c    	vpalignr $0xc,%xmm0,%xmm2,%xmm2
    1f27:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    1f2d:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
    1f32:	c5 ed 72 d0 05       	vpsrld $0x5,%ymm0,%ymm2
    1f37:	c5 fd ef d2          	vpxor  %ymm2,%ymm0,%ymm2
    1f3b:	c5 ed db d1          	vpand  %ymm1,%ymm2,%ymm2
    1f3f:	c5 e5 72 f2 05       	vpslld $0x5,%ymm2,%ymm3
    1f44:	c5 fd ef c3          	vpxor  %ymm3,%ymm0,%ymm0
    1f48:	c5 fd ef c2          	vpxor  %ymm2,%ymm0,%ymm0
    1f4c:	c4 e3 7d 39 c2 01    	vextracti128 $0x1,%ymm0,%xmm2
    1f52:	c4 c1 79 7e c1       	vmovd  %xmm0,%r9d
    1f57:	c4 c3 79 16 c3 02    	vpextrd $0x2,%xmm0,%r11d
    1f5d:	c4 c1 79 7e d4       	vmovd  %xmm2,%r12d
    1f62:	c4 c3 79 16 d6 02    	vpextrd $0x2,%xmm2,%r14d
    1f68:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    1f6d:	42 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%ebx
    1f72:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1f77:	46 0f b6 3c 37       	movzbl (%rdi,%r14,1),%r15d
    1f7c:	c4 c3 79 16 d4 01    	vpextrd $0x1,%xmm2,%r12d
    1f82:	c4 c3 79 16 d6 03    	vpextrd $0x3,%xmm2,%r14d
    1f88:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1f8d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1f92:	c4 c3 79 16 c1 01    	vpextrd $0x1,%xmm0,%r9d
    1f98:	c4 c3 79 16 c3 03    	vpextrd $0x3,%xmm0,%r11d
    1f9e:	c4 a1 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm3
    1fa4:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1faa:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1faf:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1fb4:	c4 a3 61 22 1c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm3,%xmm3
    1fbb:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    1fc2:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
    1fc8:	c5 e9 6c d3          	vpunpcklqdq %xmm3,%xmm2,%xmm2
    1fcc:	c5 f9 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm3
    1fd1:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1fd8:	49 89 d1             	mov    %rdx,%r9
    1fdb:	48 83 c2 08          	add    $0x8,%rdx
    1fdf:	c4 a3 61 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm3,%xmm3
    1fe6:	c5 f9 6c c3          	vpunpcklqdq %xmm3,%xmm0,%xmm0
    1fea:	c4 e3 7d 38 c2 01    	vinserti128 $0x1,%xmm2,%ymm0,%ymm0
    1ff0:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
    1ff5:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
    1ff9:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1fff:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
    2004:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    2009:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
    200d:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
    2012:	c5 fa 7f 50 e8       	vmovdqu %xmm2,-0x18(%rax)
    2017:	49 39 d0             	cmp    %rdx,%r8
    201a:	0f 83 f0 fe ff ff    	jae    1f10 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xdd0>
    2020:	4c 8b 54 24 f8       	mov    -0x8(%rsp),%r10
    2025:	4c 8b 5c 24 f0       	mov    -0x10(%rsp),%r11
    202a:	4d 39 c1             	cmp    %r8,%r9
    202d:	0f 83 75 02 00 00    	jae    22a8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1168>
    2033:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    2037:	49 8d 1c 12          	lea    (%r10,%rdx,1),%rbx
    203b:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    203f:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    2044:	0f b6 1b             	movzbl (%rbx),%ebx
    2047:	c1 e0 08             	shl    $0x8,%eax
    204a:	41 c1 e4 10          	shl    $0x10,%r12d
    204e:	44 09 e0             	or     %r12d,%eax
    2051:	09 d8                	or     %ebx,%eax
    2053:	89 c3                	mov    %eax,%ebx
    2055:	c1 eb 05             	shr    $0x5,%ebx
    2058:	31 c3                	xor    %eax,%ebx
    205a:	83 e3 38             	and    $0x38,%ebx
    205d:	31 d8                	xor    %ebx,%eax
    205f:	c1 e3 05             	shl    $0x5,%ebx
    2062:	31 d8                	xor    %ebx,%eax
    2064:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2068:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    206c:	8b 03                	mov    (%rbx),%eax
    206e:	0f b7 1b             	movzwl (%rbx),%ebx
    2071:	c1 e8 10             	shr    $0x10,%eax
    2074:	66 41 89 1c 13       	mov    %bx,(%r11,%rdx,1)
    2079:	41 88 44 13 02       	mov    %al,0x2(%r11,%rdx,1)
    207e:	49 8d 41 01          	lea    0x1(%r9),%rax
    2082:	4c 39 c0             	cmp    %r8,%rax
    2085:	0f 83 1d 02 00 00    	jae    22a8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1168>
    208b:	49 8d 5c 12 03       	lea    0x3(%r10,%rdx,1),%rbx
    2090:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    2094:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    2099:	0f b6 1b             	movzbl (%rbx),%ebx
    209c:	c1 e0 08             	shl    $0x8,%eax
    209f:	41 c1 e4 10          	shl    $0x10,%r12d
    20a3:	44 09 e0             	or     %r12d,%eax
    20a6:	09 d8                	or     %ebx,%eax
    20a8:	89 c3                	mov    %eax,%ebx
    20aa:	c1 eb 05             	shr    $0x5,%ebx
    20ad:	31 c3                	xor    %eax,%ebx
    20af:	83 e3 38             	and    $0x38,%ebx
    20b2:	31 d8                	xor    %ebx,%eax
    20b4:	c1 e3 05             	shl    $0x5,%ebx
    20b7:	31 d8                	xor    %ebx,%eax
    20b9:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    20bd:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    20c1:	8b 03                	mov    (%rbx),%eax
    20c3:	0f b7 1b             	movzwl (%rbx),%ebx
    20c6:	c1 e8 10             	shr    $0x10,%eax
    20c9:	66 41 89 5c 13 03    	mov    %bx,0x3(%r11,%rdx,1)
    20cf:	41 88 44 13 05       	mov    %al,0x5(%r11,%rdx,1)
    20d4:	49 8d 41 02          	lea    0x2(%r9),%rax
    20d8:	4c 39 c0             	cmp    %r8,%rax
    20db:	0f 83 c7 01 00 00    	jae    22a8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1168>
    20e1:	49 8d 5c 12 06       	lea    0x6(%r10,%rdx,1),%rbx
    20e6:	0f b6 43 01          	movzbl 0x1(%rbx),%eax
    20ea:	44 0f b6 63 02       	movzbl 0x2(%rbx),%r12d
    20ef:	0f b6 1b             	movzbl (%rbx),%ebx
    20f2:	c1 e0 08             	shl    $0x8,%eax
    20f5:	41 c1 e4 10          	shl    $0x10,%r12d
    20f9:	44 09 e0             	or     %r12d,%eax
    20fc:	09 d8                	or     %ebx,%eax
    20fe:	89 c3                	mov    %eax,%ebx
    2100:	c1 eb 05             	shr    $0x5,%ebx
    2103:	31 c3                	xor    %eax,%ebx
    2105:	83 e3 38             	and    $0x38,%ebx
    2108:	31 d8                	xor    %ebx,%eax
    210a:	c1 e3 05             	shl    $0x5,%ebx
    210d:	31 d8                	xor    %ebx,%eax
    210f:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2113:	48 8d 1c 86          	lea    (%rsi,%rax,4),%rbx
    2117:	8b 03                	mov    (%rbx),%eax
    2119:	0f b7 1b             	movzwl (%rbx),%ebx
    211c:	c1 e8 10             	shr    $0x10,%eax
    211f:	66 41 89 5c 13 06    	mov    %bx,0x6(%r11,%rdx,1)
    2125:	41 88 44 13 08       	mov    %al,0x8(%r11,%rdx,1)
    212a:	49 8d 41 03          	lea    0x3(%r9),%rax
    212e:	4c 39 c0             	cmp    %r8,%rax
    2131:	0f 83 71 01 00 00    	jae    22a8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1168>
    2137:	49 8d 4c 12 09       	lea    0x9(%r10,%rdx,1),%rcx
    213c:	0f b6 41 02          	movzbl 0x2(%rcx),%eax
    2140:	44 0f b6 61 01       	movzbl 0x1(%rcx),%r12d
    2145:	0f b6 09             	movzbl (%rcx),%ecx
    2148:	41 c1 e4 08          	shl    $0x8,%r12d
    214c:	c1 e0 10             	shl    $0x10,%eax
    214f:	44 09 e0             	or     %r12d,%eax
    2152:	09 c8                	or     %ecx,%eax
    2154:	89 c1                	mov    %eax,%ecx
    2156:	c1 e9 05             	shr    $0x5,%ecx
    2159:	31 c1                	xor    %eax,%ecx
    215b:	83 e1 38             	and    $0x38,%ecx
    215e:	41 89 cc             	mov    %ecx,%r12d
    2161:	31 c1                	xor    %eax,%ecx
    2163:	41 c1 e4 05          	shl    $0x5,%r12d
    2167:	44 89 e0             	mov    %r12d,%eax
    216a:	31 c8                	xor    %ecx,%eax
    216c:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2170:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
    2174:	8b 01                	mov    (%rcx),%eax
    2176:	0f b7 09             	movzwl (%rcx),%ecx
    2179:	c1 e8 10             	shr    $0x10,%eax
    217c:	66 41 89 4c 13 09    	mov    %cx,0x9(%r11,%rdx,1)
    2182:	41 88 44 13 0b       	mov    %al,0xb(%r11,%rdx,1)
    2187:	49 8d 41 04          	lea    0x4(%r9),%rax
    218b:	4c 39 c0             	cmp    %r8,%rax
    218e:	0f 83 14 01 00 00    	jae    22a8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1168>
    2194:	49 8d 4c 12 0c       	lea    0xc(%r10,%rdx,1),%rcx
    2199:	0f b6 41 02          	movzbl 0x2(%rcx),%eax
    219d:	44 0f b6 61 01       	movzbl 0x1(%rcx),%r12d
    21a2:	0f b6 09             	movzbl (%rcx),%ecx
    21a5:	41 c1 e4 08          	shl    $0x8,%r12d
    21a9:	c1 e0 10             	shl    $0x10,%eax
    21ac:	44 09 e0             	or     %r12d,%eax
    21af:	09 c8                	or     %ecx,%eax
    21b1:	89 c1                	mov    %eax,%ecx
    21b3:	c1 e9 05             	shr    $0x5,%ecx
    21b6:	31 c1                	xor    %eax,%ecx
    21b8:	83 e1 38             	and    $0x38,%ecx
    21bb:	41 89 cc             	mov    %ecx,%r12d
    21be:	31 c1                	xor    %eax,%ecx
    21c0:	41 c1 e4 05          	shl    $0x5,%r12d
    21c4:	44 89 e0             	mov    %r12d,%eax
    21c7:	31 c8                	xor    %ecx,%eax
    21c9:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    21cd:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
    21d1:	8b 01                	mov    (%rcx),%eax
    21d3:	0f b7 09             	movzwl (%rcx),%ecx
    21d6:	c1 e8 10             	shr    $0x10,%eax
    21d9:	66 41 89 4c 13 0c    	mov    %cx,0xc(%r11,%rdx,1)
    21df:	41 88 44 13 0e       	mov    %al,0xe(%r11,%rdx,1)
    21e4:	49 8d 41 05          	lea    0x5(%r9),%rax
    21e8:	4c 39 c0             	cmp    %r8,%rax
    21eb:	0f 83 b7 00 00 00    	jae    22a8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1168>
    21f1:	49 8d 4c 12 0f       	lea    0xf(%r10,%rdx,1),%rcx
    21f6:	49 83 c1 06          	add    $0x6,%r9
    21fa:	0f b6 41 02          	movzbl 0x2(%rcx),%eax
    21fe:	44 0f b6 61 01       	movzbl 0x1(%rcx),%r12d
    2203:	0f b6 09             	movzbl (%rcx),%ecx
    2206:	41 c1 e4 08          	shl    $0x8,%r12d
    220a:	c1 e0 10             	shl    $0x10,%eax
    220d:	44 09 e0             	or     %r12d,%eax
    2210:	09 c8                	or     %ecx,%eax
    2212:	89 c1                	mov    %eax,%ecx
    2214:	c1 e9 05             	shr    $0x5,%ecx
    2217:	31 c1                	xor    %eax,%ecx
    2219:	83 e1 38             	and    $0x38,%ecx
    221c:	41 89 cc             	mov    %ecx,%r12d
    221f:	31 c1                	xor    %eax,%ecx
    2221:	41 c1 e4 05          	shl    $0x5,%r12d
    2225:	44 89 e0             	mov    %r12d,%eax
    2228:	31 c8                	xor    %ecx,%eax
    222a:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    222e:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
    2232:	8b 01                	mov    (%rcx),%eax
    2234:	0f b7 09             	movzwl (%rcx),%ecx
    2237:	c1 e8 10             	shr    $0x10,%eax
    223a:	66 41 89 4c 13 0f    	mov    %cx,0xf(%r11,%rdx,1)
    2240:	41 88 44 13 11       	mov    %al,0x11(%r11,%rdx,1)
    2245:	4d 39 c1             	cmp    %r8,%r9
    2248:	73 5e                	jae    22a8 <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1168>
    224a:	49 8d 4c 13 12       	lea    0x12(%r11,%rdx,1),%rcx
    224f:	49 8d 54 12 12       	lea    0x12(%r10,%rdx,1),%rdx
    2254:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    2258:	44 0f b6 42 02       	movzbl 0x2(%rdx),%r8d
    225d:	0f b6 12             	movzbl (%rdx),%edx
    2260:	c1 e0 08             	shl    $0x8,%eax
    2263:	41 c1 e0 10          	shl    $0x10,%r8d
    2267:	44 09 c0             	or     %r8d,%eax
    226a:	09 d0                	or     %edx,%eax
    226c:	89 c2                	mov    %eax,%edx
    226e:	c1 ea 05             	shr    $0x5,%edx
    2271:	31 c2                	xor    %eax,%edx
    2273:	83 e2 38             	and    $0x38,%edx
    2276:	31 d0                	xor    %edx,%eax
    2278:	c1 e2 05             	shl    $0x5,%edx
    227b:	31 d0                	xor    %edx,%eax
    227d:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    2281:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    2285:	8b 02                	mov    (%rdx),%eax
    2287:	0f b7 12             	movzwl (%rdx),%edx
    228a:	c1 e8 10             	shr    $0x10,%eax
    228d:	66 89 11             	mov    %dx,(%rcx)
    2290:	88 41 02             	mov    %al,0x2(%rcx)
    2293:	c5 f8 77             	vzeroupper
    2296:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    229a:	5b                   	pop    %rbx
    229b:	41 5c                	pop    %r12
    229d:	41 5d                	pop    %r13
    229f:	41 5e                	pop    %r14
    22a1:	41 5f                	pop    %r15
    22a3:	5d                   	pop    %rbp
    22a4:	c3                   	ret
    22a5:	0f 1f 00             	nopl   (%rax)
    22a8:	c5 f8 77             	vzeroupper
    22ab:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    22af:	5b                   	pop    %rbx
    22b0:	41 5c                	pop    %r12
    22b2:	41 5d                	pop    %r13
    22b4:	41 5e                	pop    %r14
    22b6:	41 5f                	pop    %r15
    22b8:	5d                   	pop    %rbp
    22b9:	c3                   	ret
    22ba:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    22c0:	4d 89 c1             	mov    %r8,%r9
    22c3:	e9 02 fc ff ff       	jmp    1eca <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd8a>
    22c8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    22cf:	00 
    22d0:	c3                   	ret
    22d1:	48 8d 41 28          	lea    0x28(%rcx),%rax
    22d5:	49 89 c9             	mov    %rcx,%r9
    22d8:	e9 af f7 ff ff       	jmp    1a8c <jshc_channel::avx2_chain_tilexy_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x94c>
