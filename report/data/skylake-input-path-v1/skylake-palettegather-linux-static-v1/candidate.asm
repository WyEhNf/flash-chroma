
artifacts/skylake-palettegather-linux-build-v1/CMakeFiles/jshc_skylake_palettegather.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 73 0f 00 00    	je     f80 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf80>
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
      3b:	72 f3                	jb     30 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      3d:	49 89 d0             	mov    %rdx,%r8
      40:	45 31 c9             	xor    %r9d,%r9d
      43:	eb 4a                	jmp    8f <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8f>
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
      89:	0f 84 e1 0e 00 00    	je     f70 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf70>
      8f:	41 f6 c0 3f          	test   $0x3f,%r8b
      93:	75 b3                	jne    48 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x48>
      95:	49 8d 41 48          	lea    0x48(%r9),%rax
      99:	48 39 c1             	cmp    %rax,%rcx
      9c:	0f 82 df 0e 00 00    	jb     f81 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf81>
      a2:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
      a6:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # ae <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xae>
      ad:	00 
      ae:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # b6 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xb6>
      b5:	00 
      b6:	48 01 d0             	add    %rdx,%rax
      b9:	eb 08                	jmp    c3 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc3>
      bb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      c0:	4d 89 d1             	mov    %r10,%r9
      c3:	4d 8d 81 96 01 00 00 	lea    0x196(%r9),%r8
      ca:	4c 39 c1             	cmp    %r8,%rcx
      cd:	72 1c                	jb     eb <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xeb>
      cf:	0f 18 80 00 04 00 00 	prefetchnta 0x400(%rax)
      d6:	0f 18 80 40 04 00 00 	prefetchnta 0x440(%rax)
      dd:	0f 18 80 80 04 00 00 	prefetchnta 0x480(%rax)
      e4:	0f 18 80 bf 04 00 00 	prefetchnta 0x4bf(%rax)
      eb:	44 8b 40 15          	mov    0x15(%rax),%r8d
      ef:	44 8b 78 12          	mov    0x12(%rax),%r15d
      f3:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
      f7:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
      fb:	44 8b 70 0f          	mov    0xf(%rax),%r14d
      ff:	44 8b 68 0c          	mov    0xc(%rax),%r13d
     103:	c4 41 05 76 ff       	vpcmpeqd %ymm15,%ymm15,%ymm15
     108:	c4 41 15 76 ed       	vpcmpeqd %ymm13,%ymm13,%ymm13
     10d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     114:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     11b:	44 8b 60 09          	mov    0x9(%rax),%r12d
     11f:	8b 58 06             	mov    0x6(%rax),%ebx
     122:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     127:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     12c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     133:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     13a:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     13f:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     144:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     14b:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     151:	49 c1 e0 08          	shl    $0x8,%r8
     155:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     15a:	44 8b 58 03          	mov    0x3(%rax),%r11d
     15e:	4d 09 f8             	or     %r15,%r8
     161:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     165:	44 8b 10             	mov    (%rax),%r10d
     168:	49 c1 e0 08          	shl    $0x8,%r8
     16c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     173:	44 8b 78 2a          	mov    0x2a(%rax),%r15d
     177:	4d 09 f0             	or     %r14,%r8
     17a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     17f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     186:	44 8b 70 27          	mov    0x27(%rax),%r14d
     18a:	49 c1 e0 08          	shl    $0x8,%r8
     18e:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     193:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     19a:	4d 09 e8             	or     %r13,%r8
     19d:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     1a2:	44 8b 68 24          	mov    0x24(%rax),%r13d
     1a6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     1ad:	49 c1 e0 08          	shl    $0x8,%r8
     1b1:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     1b6:	4d 09 e0             	or     %r12,%r8
     1b9:	44 8b 60 21          	mov    0x21(%rax),%r12d
     1bd:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     1c4:	49 c1 e0 08          	shl    $0x8,%r8
     1c8:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     1cd:	49 09 d8             	or     %rbx,%r8
     1d0:	8b 58 1e             	mov    0x1e(%rax),%ebx
     1d3:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     1da:	49 c1 e0 08          	shl    $0x8,%r8
     1de:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     1e3:	4d 09 d8             	or     %r11,%r8
     1e6:	44 8b 58 1b          	mov    0x1b(%rax),%r11d
     1ea:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     1f0:	49 c1 e0 08          	shl    $0x8,%r8
     1f4:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     1f8:	4d 09 d0             	or     %r10,%r8
     1fb:	44 8b 50 18          	mov    0x18(%rax),%r10d
     1ff:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     206:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     20b:	44 8b 40 2d          	mov    0x2d(%rax),%r8d
     20f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     216:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     21b:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     222:	c4 e2 4d 90 24 86    	vpgatherdd %ymm6,(%rsi,%ymm0,4),%ymm4
     228:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     22d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     232:	c4 e2 5d 00 e1       	vpshufb %ymm1,%ymm4,%ymm4
     237:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     23c:	c4 e2 6d 36 e4       	vpermd %ymm4,%ymm2,%ymm4
     241:	49 c1 e0 08          	shl    $0x8,%r8
     245:	4d 09 f8             	or     %r15,%r8
     248:	44 8b 78 42          	mov    0x42(%rax),%r15d
     24c:	49 c1 e0 08          	shl    $0x8,%r8
     250:	4d 09 f0             	or     %r14,%r8
     253:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     25a:	44 8b 70 3f          	mov    0x3f(%rax),%r14d
     25e:	49 c1 e0 08          	shl    $0x8,%r8
     262:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     267:	4d 09 e8             	or     %r13,%r8
     26a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     271:	44 8b 68 3c          	mov    0x3c(%rax),%r13d
     275:	49 c1 e0 08          	shl    $0x8,%r8
     279:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     27e:	4d 09 e0             	or     %r12,%r8
     281:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     288:	44 8b 60 39          	mov    0x39(%rax),%r12d
     28c:	49 c1 e0 08          	shl    $0x8,%r8
     290:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     295:	49 09 d8             	or     %rbx,%r8
     298:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     29f:	8b 58 36             	mov    0x36(%rax),%ebx
     2a2:	49 c1 e0 08          	shl    $0x8,%r8
     2a6:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     2ab:	4d 09 d8             	or     %r11,%r8
     2ae:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     2b4:	44 8b 58 33          	mov    0x33(%rax),%r11d
     2b8:	49 c1 e0 08          	shl    $0x8,%r8
     2bc:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     2c0:	4d 09 d0             	or     %r10,%r8
     2c3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     2ca:	44 8b 50 30          	mov    0x30(%rax),%r10d
     2ce:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     2d3:	44 8b 40 45          	mov    0x45(%rax),%r8d
     2d7:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     2dc:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     2e3:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     2e8:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2ef:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     2f4:	c4 e2 45 90 1c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm3
     2fa:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
     2fe:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     303:	c4 e2 65 00 d9       	vpshufb %ymm1,%ymm3,%ymm3
     308:	c4 e2 6d 36 db       	vpermd %ymm3,%ymm2,%ymm3
     30d:	49 c1 e0 08          	shl    $0x8,%r8
     311:	c5 79 6f e3          	vmovdqa %xmm3,%xmm12
     315:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
     31b:	4d 09 f8             	or     %r15,%r8
     31e:	44 8b 78 5a          	mov    0x5a(%rax),%r15d
     322:	c4 c3 61 0f dc 08    	vpalignr $0x8,%xmm12,%xmm3,%xmm3
     328:	49 c1 e0 08          	shl    $0x8,%r8
     32c:	4d 09 f0             	or     %r14,%r8
     32f:	44 8b 70 57          	mov    0x57(%rax),%r14d
     333:	49 c1 e0 08          	shl    $0x8,%r8
     337:	4d 09 e8             	or     %r13,%r8
     33a:	44 8b 68 54          	mov    0x54(%rax),%r13d
     33e:	49 c1 e0 08          	shl    $0x8,%r8
     342:	4d 09 e0             	or     %r12,%r8
     345:	44 8b 60 51          	mov    0x51(%rax),%r12d
     349:	49 c1 e0 08          	shl    $0x8,%r8
     34d:	49 09 d8             	or     %rbx,%r8
     350:	8b 58 4e             	mov    0x4e(%rax),%ebx
     353:	49 c1 e0 08          	shl    $0x8,%r8
     357:	4d 09 d8             	or     %r11,%r8
     35a:	44 8b 58 4b          	mov    0x4b(%rax),%r11d
     35e:	49 c1 e0 08          	shl    $0x8,%r8
     362:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     369:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     370:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     377:	4d 09 d0             	or     %r10,%r8
     37a:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     37f:	44 8b 50 48          	mov    0x48(%rax),%r10d
     383:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     38a:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     38f:	44 8b 40 5d          	mov    0x5d(%rax),%r8d
     393:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     399:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     3a0:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     3a5:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     3ac:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3b3:	c4 e2 45 90 34 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm6
     3b9:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
     3bd:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     3c2:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     3c7:	c4 e2 4d 00 f1       	vpshufb %ymm1,%ymm6,%ymm6
     3cc:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     3d1:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     3d6:	c4 e2 6d 36 f6       	vpermd %ymm6,%ymm2,%ymm6
     3db:	49 c1 e0 08          	shl    $0x8,%r8
     3df:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     3e3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     3e8:	4d 09 f8             	or     %r15,%r8
     3eb:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     3f0:	44 8b 78 72          	mov    0x72(%rax),%r15d
     3f4:	49 c1 e0 08          	shl    $0x8,%r8
     3f8:	4d 09 f0             	or     %r14,%r8
     3fb:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     402:	44 8b 70 6f          	mov    0x6f(%rax),%r14d
     406:	49 c1 e0 08          	shl    $0x8,%r8
     40a:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     40f:	4d 09 e8             	or     %r13,%r8
     412:	44 8b 68 6c          	mov    0x6c(%rax),%r13d
     416:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     41d:	49 c1 e0 08          	shl    $0x8,%r8
     421:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     426:	4d 09 e0             	or     %r12,%r8
     429:	44 8b 60 69          	mov    0x69(%rax),%r12d
     42d:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     434:	49 c1 e0 08          	shl    $0x8,%r8
     438:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     43d:	49 09 d8             	or     %rbx,%r8
     440:	8b 58 66             	mov    0x66(%rax),%ebx
     443:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     44a:	49 c1 e0 08          	shl    $0x8,%r8
     44e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     453:	4d 09 d8             	or     %r11,%r8
     456:	44 8b 58 63          	mov    0x63(%rax),%r11d
     45a:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     460:	49 c1 e0 08          	shl    $0x8,%r8
     464:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     468:	4d 09 d0             	or     %r10,%r8
     46b:	44 8b 50 60          	mov    0x60(%rax),%r10d
     46f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     476:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     47b:	44 8b 40 75          	mov    0x75(%rax),%r8d
     47f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     484:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     48b:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     490:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     497:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     49c:	c4 62 45 90 04 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm8
     4a2:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
     4a6:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     4ab:	c4 62 3d 00 c1       	vpshufb %ymm1,%ymm8,%ymm8
     4b0:	c4 42 6d 36 c0       	vpermd %ymm8,%ymm2,%ymm8
     4b5:	49 c1 e0 08          	shl    $0x8,%r8
     4b9:	c4 41 79 6f f0       	vmovdqa %xmm8,%xmm14
     4be:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     4c4:	4d 09 f8             	or     %r15,%r8
     4c7:	c4 43 39 0f c6 08    	vpalignr $0x8,%xmm14,%xmm8,%xmm8
     4cd:	49 c1 e0 08          	shl    $0x8,%r8
     4d1:	4d 09 f0             	or     %r14,%r8
     4d4:	44 8b b0 87 00 00 00 	mov    0x87(%rax),%r14d
     4db:	49 c1 e0 08          	shl    $0x8,%r8
     4df:	4d 09 e8             	or     %r13,%r8
     4e2:	44 8b a8 84 00 00 00 	mov    0x84(%rax),%r13d
     4e9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     4f0:	49 c1 e0 08          	shl    $0x8,%r8
     4f4:	4d 09 e0             	or     %r12,%r8
     4f7:	44 8b a0 81 00 00 00 	mov    0x81(%rax),%r12d
     4fe:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     505:	49 c1 e0 08          	shl    $0x8,%r8
     509:	49 09 d8             	or     %rbx,%r8
     50c:	8b 58 7e             	mov    0x7e(%rax),%ebx
     50f:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     516:	49 c1 e0 08          	shl    $0x8,%r8
     51a:	4d 09 d8             	or     %r11,%r8
     51d:	44 8b 58 7b          	mov    0x7b(%rax),%r11d
     521:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     527:	49 c1 e0 08          	shl    $0x8,%r8
     52b:	4d 09 d0             	or     %r10,%r8
     52e:	44 8b 50 78          	mov    0x78(%rax),%r10d
     532:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     539:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     53e:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     543:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     54a:	c4 62 45 90 14 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm10
     550:	44 8b b8 8a 00 00 00 	mov    0x8a(%rax),%r15d
     557:	44 8b 80 8d 00 00 00 	mov    0x8d(%rax),%r8d
     55e:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
     562:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     567:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     56c:	c4 62 2d 00 d1       	vpshufb %ymm1,%ymm10,%ymm10
     571:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     578:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     57f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     584:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     588:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     58d:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     592:	c4 42 6d 36 d2       	vpermd %ymm10,%ymm2,%ymm10
     597:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     59c:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     5a1:	49 c1 e0 08          	shl    $0x8,%r8
     5a5:	4d 09 f8             	or     %r15,%r8
     5a8:	44 8b b8 a2 00 00 00 	mov    0xa2(%rax),%r15d
     5af:	49 c1 e0 08          	shl    $0x8,%r8
     5b3:	4d 09 f0             	or     %r14,%r8
     5b6:	44 8b b0 9f 00 00 00 	mov    0x9f(%rax),%r14d
     5bd:	49 c1 e0 08          	shl    $0x8,%r8
     5c1:	4d 09 e8             	or     %r13,%r8
     5c4:	44 8b a8 9c 00 00 00 	mov    0x9c(%rax),%r13d
     5cb:	49 c1 e0 08          	shl    $0x8,%r8
     5cf:	4d 09 e0             	or     %r12,%r8
     5d2:	44 8b a0 99 00 00 00 	mov    0x99(%rax),%r12d
     5d9:	49 c1 e0 08          	shl    $0x8,%r8
     5dd:	49 09 d8             	or     %rbx,%r8
     5e0:	8b 98 96 00 00 00    	mov    0x96(%rax),%ebx
     5e6:	49 c1 e0 08          	shl    $0x8,%r8
     5ea:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     5f1:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5f8:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     5ff:	4d 09 d8             	or     %r11,%r8
     602:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     607:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     60c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     613:	49 c1 e0 08          	shl    $0x8,%r8
     617:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     61c:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     621:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     627:	4d 09 d0             	or     %r10,%r8
     62a:	44 8b 98 93 00 00 00 	mov    0x93(%rax),%r11d
     631:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     635:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     63a:	44 8b 80 a5 00 00 00 	mov    0xa5(%rax),%r8d
     641:	44 8b 90 90 00 00 00 	mov    0x90(%rax),%r10d
     648:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     64f:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     654:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     65b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     660:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     667:	c4 62 45 90 1c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm11
     66d:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     672:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     677:	c4 e2 25 00 c1       	vpshufb %ymm1,%ymm11,%ymm0
     67c:	c4 62 6d 36 d8       	vpermd %ymm0,%ymm2,%ymm11
     681:	49 c1 e0 08          	shl    $0x8,%r8
     685:	4d 09 f8             	or     %r15,%r8
     688:	49 c1 e0 08          	shl    $0x8,%r8
     68c:	4d 09 f0             	or     %r14,%r8
     68f:	49 c1 e0 08          	shl    $0x8,%r8
     693:	4d 09 e8             	or     %r13,%r8
     696:	49 c1 e0 08          	shl    $0x8,%r8
     69a:	4d 09 e0             	or     %r12,%r8
     69d:	49 c1 e0 08          	shl    $0x8,%r8
     6a1:	49 09 d8             	or     %rbx,%r8
     6a4:	49 c1 e0 08          	shl    $0x8,%r8
     6a8:	4d 09 d8             	or     %r11,%r8
     6ab:	44 8b 98 ab 00 00 00 	mov    0xab(%rax),%r11d
     6b2:	49 c1 e0 08          	shl    $0x8,%r8
     6b6:	4d 09 d0             	or     %r10,%r8
     6b9:	44 8b 90 a8 00 00 00 	mov    0xa8(%rax),%r10d
     6c0:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     6c7:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     6cc:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     6d1:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     6d8:	c4 e2 05 90 3c 86    	vpgatherdd %ymm15,(%rsi,%ymm0,4),%ymm7
     6de:	8b 98 ae 00 00 00    	mov    0xae(%rax),%ebx
     6e4:	44 8b a0 b1 00 00 00 	mov    0xb1(%rax),%r12d
     6eb:	44 8b a8 b4 00 00 00 	mov    0xb4(%rax),%r13d
     6f2:	44 8b b0 b7 00 00 00 	mov    0xb7(%rax),%r14d
     6f9:	c4 e2 45 00 f9       	vpshufb %ymm1,%ymm7,%ymm7
     6fe:	44 8b b8 ba 00 00 00 	mov    0xba(%rax),%r15d
     705:	44 8b 80 bd 00 00 00 	mov    0xbd(%rax),%r8d
     70c:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     712:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     719:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     720:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     727:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     72c:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     730:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     737:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     73e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     743:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     748:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     74d:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     752:	c4 e2 6d 36 ff       	vpermd %ymm7,%ymm2,%ymm7
     757:	48 05 c0 00 00 00    	add    $0xc0,%rax
     75d:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     762:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     767:	49 c1 e0 08          	shl    $0x8,%r8
     76b:	4d 09 f8             	or     %r15,%r8
     76e:	49 c1 e0 08          	shl    $0x8,%r8
     772:	4d 09 f0             	or     %r14,%r8
     775:	49 c1 e0 08          	shl    $0x8,%r8
     779:	4d 09 e8             	or     %r13,%r8
     77c:	49 c1 e0 08          	shl    $0x8,%r8
     780:	4d 09 e0             	or     %r12,%r8
     783:	49 c1 e0 08          	shl    $0x8,%r8
     787:	49 09 d8             	or     %rbx,%r8
     78a:	49 c1 e0 08          	shl    $0x8,%r8
     78e:	4d 09 d8             	or     %r11,%r8
     791:	49 c1 e0 08          	shl    $0x8,%r8
     795:	4d 09 d0             	or     %r10,%r8
     798:	4d 8d 51 40          	lea    0x40(%r9),%r10
     79c:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     7a1:	4d 8d 81 88 00 00 00 	lea    0x88(%r9),%r8
     7a8:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     7ad:	c4 62 15 90 0c 86    	vpgatherdd %ymm13,(%rsi,%ymm0,4),%ymm9
     7b3:	c5 f9 6f c4          	vmovdqa %xmm4,%xmm0
     7b7:	c5 79 6f ee          	vmovdqa %xmm6,%xmm13
     7bb:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
     7c1:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     7c7:	c4 62 35 00 c9       	vpshufb %ymm1,%ymm9,%ymm9
     7cc:	c4 c1 59 6c e4       	vpunpcklqdq %xmm12,%xmm4,%xmm4
     7d1:	c4 c1 49 6c f6       	vpunpcklqdq %xmm14,%xmm6,%xmm6
     7d6:	c4 42 6d 36 c9       	vpermd %ymm9,%ymm2,%ymm9
     7db:	c4 e3 7d 38 c4 01    	vinserti128 $0x1,%xmm4,%ymm0,%ymm0
     7e1:	c4 c3 65 38 dd 01    	vinserti128 $0x1,%xmm13,%ymm3,%ymm3
     7e7:	c4 c3 4d 38 f0 01    	vinserti128 $0x1,%xmm8,%ymm6,%ymm6
     7ed:	c5 79 7f cc          	vmovdqa %xmm9,%xmm4
     7f1:	c5 fd e7 80 40 ff ff 	vmovntdq %ymm0,-0xc0(%rax)
     7f8:	ff 
     7f9:	c5 fd e7 98 60 ff ff 	vmovntdq %ymm3,-0xa0(%rax)
     800:	ff 
     801:	c5 fd e7 70 80       	vmovntdq %ymm6,-0x80(%rax)
     806:	c5 79 7f d3          	vmovdqa %xmm10,%xmm3
     80a:	c5 f9 6f f7          	vmovdqa %xmm7,%xmm6
     80e:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
     814:	c4 63 7d 39 d8 01    	vextracti128 $0x1,%ymm11,%xmm0
     81a:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     820:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     826:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
     82b:	c4 c3 79 0f c3 08    	vpalignr $0x8,%xmm11,%xmm0,%xmm0
     831:	c5 c1 6c fc          	vpunpcklqdq %xmm4,%xmm7,%xmm7
     835:	c4 63 31 0f cc 08    	vpalignr $0x8,%xmm4,%xmm9,%xmm9
     83b:	c4 c3 65 38 da 01    	vinserti128 $0x1,%xmm10,%ymm3,%ymm3
     841:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
     847:	c4 c3 45 38 f9 01    	vinserti128 $0x1,%xmm9,%ymm7,%ymm7
     84d:	c5 fd e7 58 a0       	vmovntdq %ymm3,-0x60(%rax)
     852:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
     857:	c5 fd e7 78 e0       	vmovntdq %ymm7,-0x20(%rax)
     85c:	4c 39 c1             	cmp    %r8,%rcx
     85f:	0f 83 5b f8 ff ff    	jae    c0 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc0>
     865:	0f ae f8             	sfence
     868:	49 8d 41 68          	lea    0x68(%r9),%rax
     86c:	48 39 c1             	cmp    %rax,%rcx
     86f:	0f 82 bf 03 00 00    	jb     c34 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc34>
     875:	4b 8d 04 52          	lea    (%r10,%r10,2),%rax
     879:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 881 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x881>
     880:	00 
     881:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 889 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x889>
     888:	00 
     889:	48 01 d0             	add    %rdx,%rax
     88c:	0f 1f 40 00          	nopl   0x0(%rax)
     890:	44 8b 40 15          	mov    0x15(%rax),%r8d
     894:	44 8b 78 12          	mov    0x12(%rax),%r15d
     898:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
     89c:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
     8a0:	44 8b 70 0f          	mov    0xf(%rax),%r14d
     8a4:	44 8b 68 0c          	mov    0xc(%rax),%r13d
     8a8:	c4 41 05 76 ff       	vpcmpeqd %ymm15,%ymm15,%ymm15
     8ad:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     8b4:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     8bb:	44 8b 60 09          	mov    0x9(%rax),%r12d
     8bf:	8b 58 06             	mov    0x6(%rax),%ebx
     8c2:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     8c7:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     8cc:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     8d3:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     8da:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     8df:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     8e4:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     8eb:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     8f1:	49 c1 e0 08          	shl    $0x8,%r8
     8f5:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     8fa:	44 8b 58 03          	mov    0x3(%rax),%r11d
     8fe:	4d 09 f8             	or     %r15,%r8
     901:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     905:	44 8b 08             	mov    (%rax),%r9d
     908:	49 c1 e0 08          	shl    $0x8,%r8
     90c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     913:	44 8b 78 2a          	mov    0x2a(%rax),%r15d
     917:	4d 09 f0             	or     %r14,%r8
     91a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     91f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     926:	44 8b 70 27          	mov    0x27(%rax),%r14d
     92a:	49 c1 e0 08          	shl    $0x8,%r8
     92e:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     933:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     93a:	4d 09 e8             	or     %r13,%r8
     93d:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     942:	44 8b 68 24          	mov    0x24(%rax),%r13d
     946:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     94d:	49 c1 e0 08          	shl    $0x8,%r8
     951:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     956:	4d 09 e0             	or     %r12,%r8
     959:	44 8b 60 21          	mov    0x21(%rax),%r12d
     95d:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     964:	49 c1 e0 08          	shl    $0x8,%r8
     968:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     96d:	49 09 d8             	or     %rbx,%r8
     970:	8b 58 1e             	mov    0x1e(%rax),%ebx
     973:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     97a:	49 c1 e0 08          	shl    $0x8,%r8
     97e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     983:	4d 09 d8             	or     %r11,%r8
     986:	44 8b 58 1b          	mov    0x1b(%rax),%r11d
     98a:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     990:	49 c1 e0 08          	shl    $0x8,%r8
     994:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     998:	4d 09 c8             	or     %r9,%r8
     99b:	44 8b 48 18          	mov    0x18(%rax),%r9d
     99f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9a6:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     9ab:	44 8b 40 2d          	mov    0x2d(%rax),%r8d
     9af:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     9b6:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     9bb:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     9c2:	c4 e2 55 90 34 86    	vpgatherdd %ymm5,(%rsi,%ymm0,4),%ymm6
     9c8:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
     9cc:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     9d1:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     9d6:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     9db:	49 c1 e0 08          	shl    $0x8,%r8
     9df:	4d 09 f8             	or     %r15,%r8
     9e2:	44 8b 78 42          	mov    0x42(%rax),%r15d
     9e6:	49 c1 e0 08          	shl    $0x8,%r8
     9ea:	4d 09 f0             	or     %r14,%r8
     9ed:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     9f4:	44 8b 70 3f          	mov    0x3f(%rax),%r14d
     9f8:	49 c1 e0 08          	shl    $0x8,%r8
     9fc:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     a01:	4d 09 e8             	or     %r13,%r8
     a04:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a0b:	44 8b 68 3c          	mov    0x3c(%rax),%r13d
     a0f:	49 c1 e0 08          	shl    $0x8,%r8
     a13:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     a18:	4d 09 e0             	or     %r12,%r8
     a1b:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     a22:	44 8b 60 39          	mov    0x39(%rax),%r12d
     a26:	49 c1 e0 08          	shl    $0x8,%r8
     a2a:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     a2f:	49 09 d8             	or     %rbx,%r8
     a32:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a39:	8b 58 36             	mov    0x36(%rax),%ebx
     a3c:	49 c1 e0 08          	shl    $0x8,%r8
     a40:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     a45:	4d 09 d8             	or     %r11,%r8
     a48:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     a4e:	44 8b 58 33          	mov    0x33(%rax),%r11d
     a52:	49 c1 e0 08          	shl    $0x8,%r8
     a56:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     a5a:	4d 09 c8             	or     %r9,%r8
     a5d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a64:	44 8b 48 30          	mov    0x30(%rax),%r9d
     a68:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     a6d:	44 8b 40 45          	mov    0x45(%rax),%r8d
     a71:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     a76:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     a7d:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     a82:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     a89:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     a8e:	c4 e2 55 90 24 86    	vpgatherdd %ymm5,(%rsi,%ymm0,4),%ymm4
     a94:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     a99:	49 c1 e0 08          	shl    $0x8,%r8
     a9d:	4d 09 f8             	or     %r15,%r8
     aa0:	44 8b 78 5a          	mov    0x5a(%rax),%r15d
     aa4:	49 c1 e0 08          	shl    $0x8,%r8
     aa8:	4d 09 f0             	or     %r14,%r8
     aab:	44 8b 70 57          	mov    0x57(%rax),%r14d
     aaf:	49 c1 e0 08          	shl    $0x8,%r8
     ab3:	4d 09 e8             	or     %r13,%r8
     ab6:	44 8b 68 54          	mov    0x54(%rax),%r13d
     aba:	49 c1 e0 08          	shl    $0x8,%r8
     abe:	4d 09 e0             	or     %r12,%r8
     ac1:	44 8b 60 51          	mov    0x51(%rax),%r12d
     ac5:	49 c1 e0 08          	shl    $0x8,%r8
     ac9:	49 09 d8             	or     %rbx,%r8
     acc:	8b 58 4e             	mov    0x4e(%rax),%ebx
     acf:	49 c1 e0 08          	shl    $0x8,%r8
     ad3:	4d 09 d8             	or     %r11,%r8
     ad6:	44 8b 58 4b          	mov    0x4b(%rax),%r11d
     ada:	49 c1 e0 08          	shl    $0x8,%r8
     ade:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     ae5:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     aec:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     af3:	4d 09 c8             	or     %r9,%r8
     af6:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     afb:	44 8b 48 48          	mov    0x48(%rax),%r9d
     aff:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     b06:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     b0b:	44 8b 40 5d          	mov    0x5d(%rax),%r8d
     b0f:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     b15:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     b1c:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     b21:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b28:	48 83 c0 60          	add    $0x60,%rax
     b2c:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     b33:	c4 e2 45 90 2c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm5
     b39:	46 0f b6 04 07       	movzbl (%rdi,%r8,1),%r8d
     b3e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     b43:	c4 e2 55 00 e9       	vpshufb %ymm1,%ymm5,%ymm5
     b48:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     b4d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     b52:	c4 e2 6d 36 ed       	vpermd %ymm5,%ymm2,%ymm5
     b57:	49 c1 e0 08          	shl    $0x8,%r8
     b5b:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     b5f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     b64:	c5 79 6f cd          	vmovdqa %xmm5,%xmm9
     b68:	4d 09 f8             	or     %r15,%r8
     b6b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     b70:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     b76:	49 c1 e0 08          	shl    $0x8,%r8
     b7a:	4d 09 f0             	or     %r14,%r8
     b7d:	49 c1 e0 08          	shl    $0x8,%r8
     b81:	4d 09 e8             	or     %r13,%r8
     b84:	49 c1 e0 08          	shl    $0x8,%r8
     b88:	4d 09 e0             	or     %r12,%r8
     b8b:	49 c1 e0 08          	shl    $0x8,%r8
     b8f:	49 09 d8             	or     %rbx,%r8
     b92:	49 c1 e0 08          	shl    $0x8,%r8
     b96:	4d 09 d8             	or     %r11,%r8
     b99:	49 c1 e0 08          	shl    $0x8,%r8
     b9d:	4d 09 c8             	or     %r9,%r8
     ba0:	c4 c1 f9 6e c0       	vmovq  %r8,%xmm0
     ba5:	4d 8d 42 48          	lea    0x48(%r10),%r8
     ba9:	49 83 c2 20          	add    $0x20,%r10
     bad:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     bb2:	c4 e2 05 90 3c 86    	vpgatherdd %ymm15,(%rsi,%ymm0,4),%ymm7
     bb8:	c4 e2 5d 00 c1       	vpshufb %ymm1,%ymm4,%ymm0
     bbd:	c4 e2 4d 00 e1       	vpshufb %ymm1,%ymm6,%ymm4
     bc2:	c4 e2 6d 36 c0       	vpermd %ymm0,%ymm2,%ymm0
     bc7:	c4 e2 6d 36 e4       	vpermd %ymm4,%ymm2,%ymm4
     bcc:	c4 e2 45 00 f9       	vpshufb %ymm1,%ymm7,%ymm7
     bd1:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
     bd5:	c4 e2 6d 36 ff       	vpermd %ymm7,%ymm2,%ymm7
     bda:	c5 f9 6f f4          	vmovdqa %xmm4,%xmm6
     bde:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
     be4:	c5 79 6f c7          	vmovdqa %xmm7,%xmm8
     be8:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     bee:	c4 c1 59 6c e2       	vpunpcklqdq %xmm10,%xmm4,%xmm4
     bf3:	c4 c3 79 0f c2 08    	vpalignr $0x8,%xmm10,%xmm0,%xmm0
     bf9:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     bff:	c4 e3 4d 38 f4 01    	vinserti128 $0x1,%xmm4,%ymm6,%ymm6
     c05:	c4 c3 41 0f f8 08    	vpalignr $0x8,%xmm8,%xmm7,%xmm7
     c0b:	c4 c1 51 6c e0       	vpunpcklqdq %xmm8,%xmm5,%xmm4
     c10:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
     c16:	c4 e3 5d 38 e7 01    	vinserti128 $0x1,%xmm7,%ymm4,%ymm4
     c1c:	c5 fe 7f 70 a0       	vmovdqu %ymm6,-0x60(%rax)
     c21:	c5 fe 7f 40 c0       	vmovdqu %ymm0,-0x40(%rax)
     c26:	c5 fe 7f 60 e0       	vmovdqu %ymm4,-0x20(%rax)
     c2b:	4c 39 c1             	cmp    %r8,%rcx
     c2e:	0f 83 5c fc ff ff    	jae    890 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x890>
     c34:	4d 8d 4a 08          	lea    0x8(%r10),%r9
     c38:	4c 39 c9             	cmp    %r9,%rcx
     c3b:	0f 82 2a 01 00 00    	jb     d6b <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd6b>
     c41:	4f 8d 04 52          	lea    (%r10,%r10,2),%r8
     c45:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # c4d <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc4d>
     c4c:	00 
     c4d:	49 01 d0             	add    %rdx,%r8
     c50:	4d 8b 78 08          	mov    0x8(%r8),%r15
     c54:	49 8b 18             	mov    (%r8),%rbx
     c57:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
     c5b:	49 8b 40 10          	mov    0x10(%r8),%rax
     c5f:	45 89 fc             	mov    %r15d,%r12d
     c62:	49 89 da             	mov    %rbx,%r10
     c65:	49 89 db             	mov    %rbx,%r11
     c68:	48 c1 eb 30          	shr    $0x30,%rbx
     c6c:	41 c1 e4 10          	shl    $0x10,%r12d
     c70:	41 89 c6             	mov    %eax,%r14d
     c73:	4d 89 fd             	mov    %r15,%r13
     c76:	49 c1 eb 18          	shr    $0x18,%r11
     c7a:	44 09 e3             	or     %r12d,%ebx
     c7d:	41 c1 e6 08          	shl    $0x8,%r14d
     c81:	45 89 fc             	mov    %r15d,%r12d
     c84:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     c8b:	49 c1 ef 38          	shr    $0x38,%r15
     c8f:	49 c1 ed 20          	shr    $0x20,%r13
     c93:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
     c99:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
     c9e:	45 09 fe             	or     %r15d,%r14d
     ca1:	49 89 c7             	mov    %rax,%r15
     ca4:	48 c1 e8 28          	shr    $0x28,%rax
     ca8:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
     caf:	49 c1 ef 10          	shr    $0x10,%r15
     cb3:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     cb7:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     cbe:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
     cc3:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
     cca:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
     ccf:	41 c1 ec 08          	shr    $0x8,%r12d
     cd3:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
     cd7:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
     cdc:	48 c1 e0 08          	shl    $0x8,%rax
     ce0:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
     ce5:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
     cec:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
     cf1:	4c 09 f8             	or     %r15,%rax
     cf4:	48 c1 e0 08          	shl    $0x8,%rax
     cf8:	4c 09 f0             	or     %r14,%rax
     cfb:	48 c1 e0 08          	shl    $0x8,%rax
     cff:	4c 09 e8             	or     %r13,%rax
     d02:	48 c1 e0 08          	shl    $0x8,%rax
     d06:	4c 09 e0             	or     %r12,%rax
     d09:	48 c1 e0 08          	shl    $0x8,%rax
     d0d:	48 09 d8             	or     %rbx,%rax
     d10:	48 c1 e0 08          	shl    $0x8,%rax
     d14:	4c 09 d8             	or     %r11,%rax
     d17:	48 c1 e0 08          	shl    $0x8,%rax
     d1b:	4c 09 d0             	or     %r10,%rax
     d1e:	4d 89 ca             	mov    %r9,%r10
     d21:	49 83 c1 08          	add    $0x8,%r9
     d25:	49 83 c0 18          	add    $0x18,%r8
     d29:	c4 e1 f9 6e c0       	vmovq  %rax,%xmm0
     d2e:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
     d33:	c4 e2 55 90 14 86    	vpgatherdd %ymm5,(%rsi,%ymm0,4),%ymm2
     d39:	c4 e2 6d 00 c1       	vpshufb %ymm1,%ymm2,%ymm0
     d3e:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
     d42:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     d48:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
     d4d:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
     d52:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
     d56:	c4 c1 79 d6 40 f8    	vmovq  %xmm0,-0x8(%r8)
     d5c:	c4 c1 7a 7f 50 e8    	vmovdqu %xmm2,-0x18(%r8)
     d62:	4c 39 c9             	cmp    %r9,%rcx
     d65:	0f 83 e5 fe ff ff    	jae    c50 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc50>
     d6b:	49 39 ca             	cmp    %rcx,%r10
     d6e:	0f 83 ec 01 00 00    	jae    f60 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     d74:	4f 8d 04 52          	lea    (%r10,%r10,2),%r8
     d78:	4e 8d 0c 02          	lea    (%rdx,%r8,1),%r9
     d7c:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     d81:	45 0f b6 59 02       	movzbl 0x2(%r9),%r11d
     d86:	c1 e0 08             	shl    $0x8,%eax
     d89:	41 c1 e3 10          	shl    $0x10,%r11d
     d8d:	44 09 d8             	or     %r11d,%eax
     d90:	45 0f b6 19          	movzbl (%r9),%r11d
     d94:	44 09 d8             	or     %r11d,%eax
     d97:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     d9b:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     d9f:	41 8b 03             	mov    (%r11),%eax
     da2:	45 0f b7 1b          	movzwl (%r11),%r11d
     da6:	c1 e8 10             	shr    $0x10,%eax
     da9:	66 45 89 19          	mov    %r11w,(%r9)
     dad:	41 88 41 02          	mov    %al,0x2(%r9)
     db1:	49 8d 42 01          	lea    0x1(%r10),%rax
     db5:	48 39 c8             	cmp    %rcx,%rax
     db8:	0f 83 a2 01 00 00    	jae    f60 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     dbe:	4e 8d 4c 02 03       	lea    0x3(%rdx,%r8,1),%r9
     dc3:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     dc8:	45 0f b6 59 02       	movzbl 0x2(%r9),%r11d
     dcd:	c1 e0 08             	shl    $0x8,%eax
     dd0:	41 c1 e3 10          	shl    $0x10,%r11d
     dd4:	44 09 d8             	or     %r11d,%eax
     dd7:	45 0f b6 19          	movzbl (%r9),%r11d
     ddb:	44 09 d8             	or     %r11d,%eax
     dde:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     de2:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     de6:	41 8b 03             	mov    (%r11),%eax
     de9:	45 0f b7 1b          	movzwl (%r11),%r11d
     ded:	c1 e8 10             	shr    $0x10,%eax
     df0:	66 45 89 19          	mov    %r11w,(%r9)
     df4:	41 88 41 02          	mov    %al,0x2(%r9)
     df8:	49 8d 42 02          	lea    0x2(%r10),%rax
     dfc:	48 39 c8             	cmp    %rcx,%rax
     dff:	0f 83 5b 01 00 00    	jae    f60 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     e05:	4e 8d 4c 02 06       	lea    0x6(%rdx,%r8,1),%r9
     e0a:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     e0f:	45 0f b6 59 02       	movzbl 0x2(%r9),%r11d
     e14:	c1 e0 08             	shl    $0x8,%eax
     e17:	41 c1 e3 10          	shl    $0x10,%r11d
     e1b:	44 09 d8             	or     %r11d,%eax
     e1e:	45 0f b6 19          	movzbl (%r9),%r11d
     e22:	44 09 d8             	or     %r11d,%eax
     e25:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e29:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e2d:	41 8b 03             	mov    (%r11),%eax
     e30:	45 0f b7 1b          	movzwl (%r11),%r11d
     e34:	c1 e8 10             	shr    $0x10,%eax
     e37:	66 45 89 19          	mov    %r11w,(%r9)
     e3b:	41 88 41 02          	mov    %al,0x2(%r9)
     e3f:	49 8d 42 03          	lea    0x3(%r10),%rax
     e43:	48 39 c8             	cmp    %rcx,%rax
     e46:	0f 83 14 01 00 00    	jae    f60 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     e4c:	4e 8d 4c 02 09       	lea    0x9(%rdx,%r8,1),%r9
     e51:	41 0f b6 41 02       	movzbl 0x2(%r9),%eax
     e56:	45 0f b6 59 01       	movzbl 0x1(%r9),%r11d
     e5b:	c1 e0 10             	shl    $0x10,%eax
     e5e:	41 c1 e3 08          	shl    $0x8,%r11d
     e62:	44 09 d8             	or     %r11d,%eax
     e65:	45 0f b6 19          	movzbl (%r9),%r11d
     e69:	44 09 d8             	or     %r11d,%eax
     e6c:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     e70:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     e74:	41 8b 03             	mov    (%r11),%eax
     e77:	45 0f b7 1b          	movzwl (%r11),%r11d
     e7b:	c1 e8 10             	shr    $0x10,%eax
     e7e:	66 45 89 19          	mov    %r11w,(%r9)
     e82:	41 88 41 02          	mov    %al,0x2(%r9)
     e86:	49 8d 42 04          	lea    0x4(%r10),%rax
     e8a:	48 39 c8             	cmp    %rcx,%rax
     e8d:	0f 83 cd 00 00 00    	jae    f60 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     e93:	4e 8d 4c 02 0c       	lea    0xc(%rdx,%r8,1),%r9
     e98:	41 0f b6 41 02       	movzbl 0x2(%r9),%eax
     e9d:	45 0f b6 59 01       	movzbl 0x1(%r9),%r11d
     ea2:	c1 e0 10             	shl    $0x10,%eax
     ea5:	41 c1 e3 08          	shl    $0x8,%r11d
     ea9:	44 09 d8             	or     %r11d,%eax
     eac:	45 0f b6 19          	movzbl (%r9),%r11d
     eb0:	44 09 d8             	or     %r11d,%eax
     eb3:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     eb7:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     ebb:	41 8b 03             	mov    (%r11),%eax
     ebe:	45 0f b7 1b          	movzwl (%r11),%r11d
     ec2:	c1 e8 10             	shr    $0x10,%eax
     ec5:	66 45 89 19          	mov    %r11w,(%r9)
     ec9:	41 88 41 02          	mov    %al,0x2(%r9)
     ecd:	49 8d 42 05          	lea    0x5(%r10),%rax
     ed1:	48 39 c8             	cmp    %rcx,%rax
     ed4:	0f 83 86 00 00 00    	jae    f60 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     eda:	4e 8d 4c 02 0f       	lea    0xf(%rdx,%r8,1),%r9
     edf:	49 83 c2 06          	add    $0x6,%r10
     ee3:	41 0f b6 41 02       	movzbl 0x2(%r9),%eax
     ee8:	45 0f b6 59 01       	movzbl 0x1(%r9),%r11d
     eed:	c1 e0 10             	shl    $0x10,%eax
     ef0:	41 c1 e3 08          	shl    $0x8,%r11d
     ef4:	44 09 d8             	or     %r11d,%eax
     ef7:	45 0f b6 19          	movzbl (%r9),%r11d
     efb:	44 09 d8             	or     %r11d,%eax
     efe:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f02:	4c 8d 1c 86          	lea    (%rsi,%rax,4),%r11
     f06:	41 8b 03             	mov    (%r11),%eax
     f09:	45 0f b7 1b          	movzwl (%r11),%r11d
     f0d:	c1 e8 10             	shr    $0x10,%eax
     f10:	66 45 89 19          	mov    %r11w,(%r9)
     f14:	41 88 41 02          	mov    %al,0x2(%r9)
     f18:	49 39 ca             	cmp    %rcx,%r10
     f1b:	73 43                	jae    f60 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xf60>
     f1d:	4a 8d 54 02 12       	lea    0x12(%rdx,%r8,1),%rdx
     f22:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
     f26:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
     f2a:	c1 e0 08             	shl    $0x8,%eax
     f2d:	c1 e1 10             	shl    $0x10,%ecx
     f30:	09 c8                	or     %ecx,%eax
     f32:	0f b6 0a             	movzbl (%rdx),%ecx
     f35:	09 c8                	or     %ecx,%eax
     f37:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     f3b:	48 8d 0c 86          	lea    (%rsi,%rax,4),%rcx
     f3f:	8b 01                	mov    (%rcx),%eax
     f41:	0f b7 09             	movzwl (%rcx),%ecx
     f44:	c1 e8 10             	shr    $0x10,%eax
     f47:	66 89 0a             	mov    %cx,(%rdx)
     f4a:	88 42 02             	mov    %al,0x2(%rdx)
     f4d:	c5 f8 77             	vzeroupper
     f50:	5b                   	pop    %rbx
     f51:	41 5c                	pop    %r12
     f53:	41 5d                	pop    %r13
     f55:	41 5e                	pop    %r14
     f57:	41 5f                	pop    %r15
     f59:	5d                   	pop    %rbp
     f5a:	c3                   	ret
     f5b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     f60:	c5 f8 77             	vzeroupper
     f63:	5b                   	pop    %rbx
     f64:	41 5c                	pop    %r12
     f66:	41 5d                	pop    %r13
     f68:	41 5e                	pop    %r14
     f6a:	41 5f                	pop    %r15
     f6c:	5d                   	pop    %rbp
     f6d:	c3                   	ret
     f6e:	66 90                	xchg   %ax,%ax
     f70:	49 89 ca             	mov    %rcx,%r10
     f73:	e9 bc fc ff ff       	jmp    c34 <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xc34>
     f78:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     f7f:	00 
     f80:	c3                   	ret
     f81:	49 8d 41 28          	lea    0x28(%r9),%rax
     f85:	4d 89 ca             	mov    %r9,%r10
     f88:	e9 df f8 ff ff       	jmp    86c <jshc_channel::avx2_chain_palettegather(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x86c>
     f8d:	0f 1f 00             	nopl   (%rax)

0000000000000f90 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     f90:	f3 0f 1e fa          	endbr64
     f94:	4d 85 c0             	test   %r8,%r8
     f97:	0f 84 63 10 00 00    	je     2000 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1070>
     f9d:	55                   	push   %rbp
     f9e:	b8 00 04 00 00       	mov    $0x400,%eax
     fa3:	48 89 e5             	mov    %rsp,%rbp
     fa6:	41 57                	push   %r15
     fa8:	49 89 cf             	mov    %rcx,%r15
     fab:	41 56                	push   %r14
     fad:	41 55                	push   %r13
     faf:	41 54                	push   %r12
     fb1:	53                   	push   %rbx
     fb2:	48 89 d3             	mov    %rdx,%rbx
     fb5:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     fb9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     fbd:	48 39 c2             	cmp    %rax,%rdx
     fc0:	48 0f 47 d0          	cmova  %rax,%rdx
     fc4:	31 c0                	xor    %eax,%eax
     fc6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     fcd:	00 00 00 
     fd0:	0f 18 04 03          	prefetchnta (%rbx,%rax,1)
     fd4:	48 83 c0 40          	add    $0x40,%rax
     fd8:	48 39 d0             	cmp    %rdx,%rax
     fdb:	72 f3                	jb     fd0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     fdd:	48 89 d9             	mov    %rbx,%rcx
     fe0:	4c 89 fa             	mov    %r15,%rdx
     fe3:	45 31 d2             	xor    %r10d,%r10d
     fe6:	eb 51                	jmp    1039 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa9>
     fe8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     fef:	00 
     ff0:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
     ff4:	44 0f b6 49 02       	movzbl 0x2(%rcx),%r9d
     ff9:	49 ff c2             	inc    %r10
     ffc:	48 83 c2 03          	add    $0x3,%rdx
    1000:	48 83 c1 03          	add    $0x3,%rcx
    1004:	41 c1 e1 10          	shl    $0x10,%r9d
    1008:	c1 e0 08             	shl    $0x8,%eax
    100b:	44 09 c8             	or     %r9d,%eax
    100e:	44 0f b6 49 fd       	movzbl -0x3(%rcx),%r9d
    1013:	44 09 c8             	or     %r9d,%eax
    1016:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    101a:	4c 8d 0c 86          	lea    (%rsi,%rax,4),%r9
    101e:	41 8b 01             	mov    (%r9),%eax
    1021:	45 0f b7 09          	movzwl (%r9),%r9d
    1025:	c1 e8 10             	shr    $0x10,%eax
    1028:	66 44 89 4a fd       	mov    %r9w,-0x3(%rdx)
    102d:	88 42 ff             	mov    %al,-0x1(%rdx)
    1030:	4d 39 d0             	cmp    %r10,%r8
    1033:	0f 84 bf 0f 00 00    	je     1ff8 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1068>
    1039:	f6 c2 3f             	test   $0x3f,%dl
    103c:	75 b2                	jne    ff0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
    103e:	49 8d 42 48          	lea    0x48(%r10),%rax
    1042:	49 39 c0             	cmp    %rax,%r8
    1045:	0f 82 b6 0f 00 00    	jb     2001 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1071>
    104b:	4b 8d 04 52          	lea    (%r10,%r10,2),%rax
    104f:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 1057 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc7>
    1056:	00 
    1057:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 105f <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcf>
    105e:	00 
    105f:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1064:	4d 8d 0c 07          	lea    (%r15,%rax,1),%r9
    1068:	4c 89 7c 24 f0       	mov    %r15,-0x10(%rsp)
    106d:	48 8d 84 03 00 04 00 	lea    0x400(%rbx,%rax,1),%rax
    1074:	00 
    1075:	eb 0c                	jmp    1083 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
    1077:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    107e:	00 00 
    1080:	49 89 ca             	mov    %rcx,%r10
    1083:	49 8d 92 96 01 00 00 	lea    0x196(%r10),%rdx
    108a:	49 39 d0             	cmp    %rdx,%r8
    108d:	72 15                	jb     10a4 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
    108f:	0f 18 00             	prefetchnta (%rax)
    1092:	0f 18 40 40          	prefetchnta 0x40(%rax)
    1096:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
    109d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
    10a4:	8b 90 15 fc ff ff    	mov    -0x3eb(%rax),%edx
    10aa:	44 8b b8 12 fc ff ff 	mov    -0x3ee(%rax),%r15d
    10b1:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
    10b5:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
    10b9:	44 8b b0 0f fc ff ff 	mov    -0x3f1(%rax),%r14d
    10c0:	44 8b a8 0c fc ff ff 	mov    -0x3f4(%rax),%r13d
    10c7:	c4 41 05 76 ff       	vpcmpeqd %ymm15,%ymm15,%ymm15
    10cc:	c4 41 15 76 ed       	vpcmpeqd %ymm13,%ymm13,%ymm13
    10d1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    10d7:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    10de:	44 8b a0 09 fc ff ff 	mov    -0x3f7(%rax),%r12d
    10e5:	8b 98 06 fc ff ff    	mov    -0x3fa(%rax),%ebx
    10eb:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    10ef:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    10f4:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    10fb:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1102:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1107:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    110c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1113:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1119:	48 c1 e2 08          	shl    $0x8,%rdx
    111d:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1122:	44 8b 98 03 fc ff ff 	mov    -0x3fd(%rax),%r11d
    1129:	4c 09 fa             	or     %r15,%rdx
    112c:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    1130:	8b 88 00 fc ff ff    	mov    -0x400(%rax),%ecx
    1136:	48 c1 e2 08          	shl    $0x8,%rdx
    113a:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1141:	44 8b b8 2a fc ff ff 	mov    -0x3d6(%rax),%r15d
    1148:	4c 09 f2             	or     %r14,%rdx
    114b:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1150:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1156:	44 8b b0 27 fc ff ff 	mov    -0x3d9(%rax),%r14d
    115d:	48 c1 e2 08          	shl    $0x8,%rdx
    1161:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1165:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    116c:	4c 09 ea             	or     %r13,%rdx
    116f:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1174:	44 8b a8 24 fc ff ff 	mov    -0x3dc(%rax),%r13d
    117b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1182:	48 c1 e2 08          	shl    $0x8,%rdx
    1186:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    118b:	4c 09 e2             	or     %r12,%rdx
    118e:	44 8b a0 21 fc ff ff 	mov    -0x3df(%rax),%r12d
    1195:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    119c:	48 c1 e2 08          	shl    $0x8,%rdx
    11a0:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    11a5:	48 09 da             	or     %rbx,%rdx
    11a8:	8b 98 1e fc ff ff    	mov    -0x3e2(%rax),%ebx
    11ae:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    11b5:	48 c1 e2 08          	shl    $0x8,%rdx
    11b9:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    11be:	4c 09 da             	or     %r11,%rdx
    11c1:	44 8b 98 1b fc ff ff 	mov    -0x3e5(%rax),%r11d
    11c8:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    11ce:	48 c1 e2 08          	shl    $0x8,%rdx
    11d2:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    11d6:	48 09 ca             	or     %rcx,%rdx
    11d9:	8b 88 18 fc ff ff    	mov    -0x3e8(%rax),%ecx
    11df:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    11e6:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    11eb:	8b 90 2d fc ff ff    	mov    -0x3d3(%rax),%edx
    11f1:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    11f7:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    11fc:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    1202:	c4 e2 4d 90 24 86    	vpgatherdd %ymm6,(%rsi,%ymm0,4),%ymm4
    1208:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    120c:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1211:	c4 e2 5d 00 e1       	vpshufb %ymm1,%ymm4,%ymm4
    1216:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    121a:	c4 e2 6d 36 e4       	vpermd %ymm4,%ymm2,%ymm4
    121f:	48 c1 e2 08          	shl    $0x8,%rdx
    1223:	4c 09 fa             	or     %r15,%rdx
    1226:	44 8b b8 42 fc ff ff 	mov    -0x3be(%rax),%r15d
    122d:	48 c1 e2 08          	shl    $0x8,%rdx
    1231:	4c 09 f2             	or     %r14,%rdx
    1234:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    123b:	44 8b b0 3f fc ff ff 	mov    -0x3c1(%rax),%r14d
    1242:	48 c1 e2 08          	shl    $0x8,%rdx
    1246:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    124b:	4c 09 ea             	or     %r13,%rdx
    124e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1255:	44 8b a8 3c fc ff ff 	mov    -0x3c4(%rax),%r13d
    125c:	48 c1 e2 08          	shl    $0x8,%rdx
    1260:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1265:	4c 09 e2             	or     %r12,%rdx
    1268:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    126f:	44 8b a0 39 fc ff ff 	mov    -0x3c7(%rax),%r12d
    1276:	48 c1 e2 08          	shl    $0x8,%rdx
    127a:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    127f:	48 09 da             	or     %rbx,%rdx
    1282:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1289:	8b 98 36 fc ff ff    	mov    -0x3ca(%rax),%ebx
    128f:	48 c1 e2 08          	shl    $0x8,%rdx
    1293:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1298:	4c 09 da             	or     %r11,%rdx
    129b:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    12a1:	44 8b 98 33 fc ff ff 	mov    -0x3cd(%rax),%r11d
    12a8:	48 c1 e2 08          	shl    $0x8,%rdx
    12ac:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    12b0:	48 09 ca             	or     %rcx,%rdx
    12b3:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    12ba:	8b 88 30 fc ff ff    	mov    -0x3d0(%rax),%ecx
    12c0:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    12c5:	8b 90 45 fc ff ff    	mov    -0x3bb(%rax),%edx
    12cb:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    12d0:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    12d6:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    12db:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    12e1:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    12e5:	c4 e2 45 90 1c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm3
    12eb:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
    12ef:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    12f3:	c4 e2 65 00 d9       	vpshufb %ymm1,%ymm3,%ymm3
    12f8:	c4 e2 6d 36 db       	vpermd %ymm3,%ymm2,%ymm3
    12fd:	48 c1 e2 08          	shl    $0x8,%rdx
    1301:	c5 79 6f e3          	vmovdqa %xmm3,%xmm12
    1305:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
    130b:	4c 09 fa             	or     %r15,%rdx
    130e:	44 8b b8 5a fc ff ff 	mov    -0x3a6(%rax),%r15d
    1315:	c4 c3 61 0f dc 08    	vpalignr $0x8,%xmm12,%xmm3,%xmm3
    131b:	48 c1 e2 08          	shl    $0x8,%rdx
    131f:	4c 09 f2             	or     %r14,%rdx
    1322:	44 8b b0 57 fc ff ff 	mov    -0x3a9(%rax),%r14d
    1329:	48 c1 e2 08          	shl    $0x8,%rdx
    132d:	4c 09 ea             	or     %r13,%rdx
    1330:	44 8b a8 54 fc ff ff 	mov    -0x3ac(%rax),%r13d
    1337:	48 c1 e2 08          	shl    $0x8,%rdx
    133b:	4c 09 e2             	or     %r12,%rdx
    133e:	44 8b a0 51 fc ff ff 	mov    -0x3af(%rax),%r12d
    1345:	48 c1 e2 08          	shl    $0x8,%rdx
    1349:	48 09 da             	or     %rbx,%rdx
    134c:	8b 98 4e fc ff ff    	mov    -0x3b2(%rax),%ebx
    1352:	48 c1 e2 08          	shl    $0x8,%rdx
    1356:	4c 09 da             	or     %r11,%rdx
    1359:	44 8b 98 4b fc ff ff 	mov    -0x3b5(%rax),%r11d
    1360:	48 c1 e2 08          	shl    $0x8,%rdx
    1364:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    136b:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1372:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1379:	48 09 ca             	or     %rcx,%rdx
    137c:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1381:	8b 88 48 fc ff ff    	mov    -0x3b8(%rax),%ecx
    1387:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    138e:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    1393:	8b 90 5d fc ff ff    	mov    -0x3a3(%rax),%edx
    1399:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    139f:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    13a6:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    13ab:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13b1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    13b7:	c4 e2 45 90 34 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm6
    13bd:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
    13c1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    13c5:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    13ca:	c4 e2 4d 00 f1       	vpshufb %ymm1,%ymm6,%ymm6
    13cf:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    13d4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    13d9:	c4 e2 6d 36 f6       	vpermd %ymm6,%ymm2,%ymm6
    13de:	48 c1 e2 08          	shl    $0x8,%rdx
    13e2:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    13e6:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    13eb:	4c 09 fa             	or     %r15,%rdx
    13ee:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    13f2:	44 8b b8 72 fc ff ff 	mov    -0x38e(%rax),%r15d
    13f9:	48 c1 e2 08          	shl    $0x8,%rdx
    13fd:	4c 09 f2             	or     %r14,%rdx
    1400:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1407:	44 8b b0 6f fc ff ff 	mov    -0x391(%rax),%r14d
    140e:	48 c1 e2 08          	shl    $0x8,%rdx
    1412:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1417:	4c 09 ea             	or     %r13,%rdx
    141a:	44 8b a8 6c fc ff ff 	mov    -0x394(%rax),%r13d
    1421:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1428:	48 c1 e2 08          	shl    $0x8,%rdx
    142c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1431:	4c 09 e2             	or     %r12,%rdx
    1434:	44 8b a0 69 fc ff ff 	mov    -0x397(%rax),%r12d
    143b:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1442:	48 c1 e2 08          	shl    $0x8,%rdx
    1446:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    144b:	48 09 da             	or     %rbx,%rdx
    144e:	8b 98 66 fc ff ff    	mov    -0x39a(%rax),%ebx
    1454:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    145b:	48 c1 e2 08          	shl    $0x8,%rdx
    145f:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1464:	4c 09 da             	or     %r11,%rdx
    1467:	44 8b 98 63 fc ff ff 	mov    -0x39d(%rax),%r11d
    146e:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1474:	48 c1 e2 08          	shl    $0x8,%rdx
    1478:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    147c:	48 09 ca             	or     %rcx,%rdx
    147f:	8b 88 60 fc ff ff    	mov    -0x3a0(%rax),%ecx
    1485:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    148c:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    1491:	8b 90 75 fc ff ff    	mov    -0x38b(%rax),%edx
    1497:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    149c:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14a2:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    14a7:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    14ad:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    14b1:	c4 62 45 90 04 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm8
    14b7:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
    14bb:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    14bf:	c4 62 3d 00 c1       	vpshufb %ymm1,%ymm8,%ymm8
    14c4:	c4 42 6d 36 c0       	vpermd %ymm8,%ymm2,%ymm8
    14c9:	48 c1 e2 08          	shl    $0x8,%rdx
    14cd:	c4 41 79 6f f0       	vmovdqa %xmm8,%xmm14
    14d2:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    14d8:	4c 09 fa             	or     %r15,%rdx
    14db:	c4 43 39 0f c6 08    	vpalignr $0x8,%xmm14,%xmm8,%xmm8
    14e1:	48 c1 e2 08          	shl    $0x8,%rdx
    14e5:	4c 09 f2             	or     %r14,%rdx
    14e8:	44 8b b0 87 fc ff ff 	mov    -0x379(%rax),%r14d
    14ef:	48 c1 e2 08          	shl    $0x8,%rdx
    14f3:	4c 09 ea             	or     %r13,%rdx
    14f6:	44 8b a8 84 fc ff ff 	mov    -0x37c(%rax),%r13d
    14fd:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1504:	48 c1 e2 08          	shl    $0x8,%rdx
    1508:	4c 09 e2             	or     %r12,%rdx
    150b:	44 8b a0 81 fc ff ff 	mov    -0x37f(%rax),%r12d
    1512:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1519:	48 c1 e2 08          	shl    $0x8,%rdx
    151d:	48 09 da             	or     %rbx,%rdx
    1520:	8b 98 7e fc ff ff    	mov    -0x382(%rax),%ebx
    1526:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    152d:	48 c1 e2 08          	shl    $0x8,%rdx
    1531:	4c 09 da             	or     %r11,%rdx
    1534:	44 8b 98 7b fc ff ff 	mov    -0x385(%rax),%r11d
    153b:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1541:	48 c1 e2 08          	shl    $0x8,%rdx
    1545:	48 09 ca             	or     %rcx,%rdx
    1548:	8b 88 78 fc ff ff    	mov    -0x388(%rax),%ecx
    154e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1555:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    155a:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    155f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1565:	c4 62 45 90 14 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm10
    156b:	44 8b b8 8a fc ff ff 	mov    -0x376(%rax),%r15d
    1572:	8b 90 8d fc ff ff    	mov    -0x373(%rax),%edx
    1578:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
    157c:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1581:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1586:	c4 62 2d 00 d1       	vpshufb %ymm1,%ymm10,%ymm10
    158b:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    1591:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1598:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    159d:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    15a1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    15a5:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    15aa:	c4 42 6d 36 d2       	vpermd %ymm10,%ymm2,%ymm10
    15af:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    15b4:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    15b8:	48 c1 e2 08          	shl    $0x8,%rdx
    15bc:	4c 09 fa             	or     %r15,%rdx
    15bf:	44 8b b8 a2 fc ff ff 	mov    -0x35e(%rax),%r15d
    15c6:	48 c1 e2 08          	shl    $0x8,%rdx
    15ca:	4c 09 f2             	or     %r14,%rdx
    15cd:	44 8b b0 9f fc ff ff 	mov    -0x361(%rax),%r14d
    15d4:	48 c1 e2 08          	shl    $0x8,%rdx
    15d8:	4c 09 ea             	or     %r13,%rdx
    15db:	44 8b a8 9c fc ff ff 	mov    -0x364(%rax),%r13d
    15e2:	48 c1 e2 08          	shl    $0x8,%rdx
    15e6:	4c 09 e2             	or     %r12,%rdx
    15e9:	44 8b a0 99 fc ff ff 	mov    -0x367(%rax),%r12d
    15f0:	48 c1 e2 08          	shl    $0x8,%rdx
    15f4:	48 09 da             	or     %rbx,%rdx
    15f7:	8b 98 96 fc ff ff    	mov    -0x36a(%rax),%ebx
    15fd:	48 c1 e2 08          	shl    $0x8,%rdx
    1601:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1608:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    160f:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1616:	4c 09 da             	or     %r11,%rdx
    1619:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    161e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1623:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    162a:	48 c1 e2 08          	shl    $0x8,%rdx
    162e:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1633:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1638:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    163e:	48 09 ca             	or     %rcx,%rdx
    1641:	44 8b 98 93 fc ff ff 	mov    -0x36d(%rax),%r11d
    1648:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    164c:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    1651:	8b 90 a5 fc ff ff    	mov    -0x35b(%rax),%edx
    1657:	8b 88 90 fc ff ff    	mov    -0x370(%rax),%ecx
    165d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1664:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    1669:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    166f:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1674:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    167a:	c4 62 45 90 1c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm11
    1680:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1684:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1688:	c4 e2 25 00 c1       	vpshufb %ymm1,%ymm11,%ymm0
    168d:	c4 62 6d 36 d8       	vpermd %ymm0,%ymm2,%ymm11
    1692:	48 c1 e2 08          	shl    $0x8,%rdx
    1696:	4c 09 fa             	or     %r15,%rdx
    1699:	48 c1 e2 08          	shl    $0x8,%rdx
    169d:	4c 09 f2             	or     %r14,%rdx
    16a0:	48 c1 e2 08          	shl    $0x8,%rdx
    16a4:	4c 09 ea             	or     %r13,%rdx
    16a7:	48 c1 e2 08          	shl    $0x8,%rdx
    16ab:	4c 09 e2             	or     %r12,%rdx
    16ae:	48 c1 e2 08          	shl    $0x8,%rdx
    16b2:	48 09 da             	or     %rbx,%rdx
    16b5:	48 c1 e2 08          	shl    $0x8,%rdx
    16b9:	4c 09 da             	or     %r11,%rdx
    16bc:	44 8b 98 ab fc ff ff 	mov    -0x355(%rax),%r11d
    16c3:	48 c1 e2 08          	shl    $0x8,%rdx
    16c7:	48 09 ca             	or     %rcx,%rdx
    16ca:	8b 88 a8 fc ff ff    	mov    -0x358(%rax),%ecx
    16d0:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    16d7:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    16dc:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    16e1:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    16e7:	c4 e2 05 90 3c 86    	vpgatherdd %ymm15,(%rsi,%ymm0,4),%ymm7
    16ed:	8b 98 ae fc ff ff    	mov    -0x352(%rax),%ebx
    16f3:	44 8b a0 b1 fc ff ff 	mov    -0x34f(%rax),%r12d
    16fa:	44 8b a8 b4 fc ff ff 	mov    -0x34c(%rax),%r13d
    1701:	44 8b b0 b7 fc ff ff 	mov    -0x349(%rax),%r14d
    1708:	c4 e2 45 00 f9       	vpshufb %ymm1,%ymm7,%ymm7
    170d:	44 8b b8 ba fc ff ff 	mov    -0x346(%rax),%r15d
    1714:	8b 90 bd fc ff ff    	mov    -0x343(%rax),%edx
    171a:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1720:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1727:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    172e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1735:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    173a:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    173e:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1745:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    174b:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1750:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1755:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1759:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    175e:	c4 e2 6d 36 ff       	vpermd %ymm7,%ymm2,%ymm7
    1763:	49 81 c1 c0 00 00 00 	add    $0xc0,%r9
    176a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    176f:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1773:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1779:	48 c1 e2 08          	shl    $0x8,%rdx
    177d:	4c 09 fa             	or     %r15,%rdx
    1780:	48 c1 e2 08          	shl    $0x8,%rdx
    1784:	4c 09 f2             	or     %r14,%rdx
    1787:	48 c1 e2 08          	shl    $0x8,%rdx
    178b:	4c 09 ea             	or     %r13,%rdx
    178e:	48 c1 e2 08          	shl    $0x8,%rdx
    1792:	4c 09 e2             	or     %r12,%rdx
    1795:	48 c1 e2 08          	shl    $0x8,%rdx
    1799:	48 09 da             	or     %rbx,%rdx
    179c:	48 c1 e2 08          	shl    $0x8,%rdx
    17a0:	4c 09 da             	or     %r11,%rdx
    17a3:	48 c1 e2 08          	shl    $0x8,%rdx
    17a7:	48 09 ca             	or     %rcx,%rdx
    17aa:	49 8d 4a 40          	lea    0x40(%r10),%rcx
    17ae:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    17b3:	49 8d 92 88 00 00 00 	lea    0x88(%r10),%rdx
    17ba:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    17bf:	c4 62 15 90 0c 86    	vpgatherdd %ymm13,(%rsi,%ymm0,4),%ymm9
    17c5:	c5 f9 6f c4          	vmovdqa %xmm4,%xmm0
    17c9:	c5 79 6f ee          	vmovdqa %xmm6,%xmm13
    17cd:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
    17d3:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    17d9:	c4 62 35 00 c9       	vpshufb %ymm1,%ymm9,%ymm9
    17de:	c4 c1 59 6c e4       	vpunpcklqdq %xmm12,%xmm4,%xmm4
    17e3:	c4 c1 49 6c f6       	vpunpcklqdq %xmm14,%xmm6,%xmm6
    17e8:	c4 42 6d 36 c9       	vpermd %ymm9,%ymm2,%ymm9
    17ed:	c4 e3 7d 38 c4 01    	vinserti128 $0x1,%xmm4,%ymm0,%ymm0
    17f3:	c4 c3 65 38 dd 01    	vinserti128 $0x1,%xmm13,%ymm3,%ymm3
    17f9:	c4 c3 4d 38 f0 01    	vinserti128 $0x1,%xmm8,%ymm6,%ymm6
    17ff:	c5 79 7f cc          	vmovdqa %xmm9,%xmm4
    1803:	c4 c1 7d e7 81 40 ff 	vmovntdq %ymm0,-0xc0(%r9)
    180a:	ff ff 
    180c:	c4 c1 7d e7 99 60 ff 	vmovntdq %ymm3,-0xa0(%r9)
    1813:	ff ff 
    1815:	c4 c1 7d e7 71 80    	vmovntdq %ymm6,-0x80(%r9)
    181b:	c5 79 7f d3          	vmovdqa %xmm10,%xmm3
    181f:	c5 f9 6f f7          	vmovdqa %xmm7,%xmm6
    1823:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
    1829:	c4 63 7d 39 d8 01    	vextracti128 $0x1,%ymm11,%xmm0
    182f:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1835:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    183b:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1840:	c4 c3 79 0f c3 08    	vpalignr $0x8,%xmm11,%xmm0,%xmm0
    1846:	c5 c1 6c fc          	vpunpcklqdq %xmm4,%xmm7,%xmm7
    184a:	c4 63 31 0f cc 08    	vpalignr $0x8,%xmm4,%xmm9,%xmm9
    1850:	c4 c3 65 38 da 01    	vinserti128 $0x1,%xmm10,%ymm3,%ymm3
    1856:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
    185c:	c4 c3 45 38 f9 01    	vinserti128 $0x1,%xmm9,%ymm7,%ymm7
    1862:	c4 c1 7d e7 59 a0    	vmovntdq %ymm3,-0x60(%r9)
    1868:	c4 c1 7d e7 41 c0    	vmovntdq %ymm0,-0x40(%r9)
    186e:	c4 c1 7d e7 79 e0    	vmovntdq %ymm7,-0x20(%r9)
    1874:	49 39 d0             	cmp    %rdx,%r8
    1877:	0f 83 03 f8 ff ff    	jae    1080 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    187d:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1882:	4c 8b 7c 24 f0       	mov    -0x10(%rsp),%r15
    1887:	49 8d 42 68          	lea    0x68(%r10),%rax
    188b:	0f ae f8             	sfence
    188e:	49 39 c0             	cmp    %rax,%r8
    1891:	0f 82 d2 03 00 00    	jb     1c69 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcd9>
    1897:	4c 8d 0c 49          	lea    (%rcx,%rcx,2),%r9
    189b:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 18a3 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x913>
    18a2:	00 
    18a3:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 18ab <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x91b>
    18aa:	00 
    18ab:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    18b0:	4c 89 7c 24 f0       	mov    %r15,-0x10(%rsp)
    18b5:	4a 8d 04 0b          	lea    (%rbx,%r9,1),%rax
    18b9:	4d 01 f9             	add    %r15,%r9
    18bc:	0f 1f 40 00          	nopl   0x0(%rax)
    18c0:	8b 50 15             	mov    0x15(%rax),%edx
    18c3:	44 8b 78 12          	mov    0x12(%rax),%r15d
    18c7:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
    18cb:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
    18cf:	44 8b 70 0f          	mov    0xf(%rax),%r14d
    18d3:	44 8b 68 0c          	mov    0xc(%rax),%r13d
    18d7:	c4 41 05 76 ff       	vpcmpeqd %ymm15,%ymm15,%ymm15
    18dc:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    18e2:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    18e9:	44 8b 60 09          	mov    0x9(%rax),%r12d
    18ed:	8b 58 06             	mov    0x6(%rax),%ebx
    18f0:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    18f4:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    18f9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1900:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1907:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    190c:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1911:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1918:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    191e:	48 c1 e2 08          	shl    $0x8,%rdx
    1922:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1927:	44 8b 58 03          	mov    0x3(%rax),%r11d
    192b:	4c 09 fa             	or     %r15,%rdx
    192e:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    1932:	44 8b 10             	mov    (%rax),%r10d
    1935:	48 c1 e2 08          	shl    $0x8,%rdx
    1939:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1940:	44 8b 78 2a          	mov    0x2a(%rax),%r15d
    1944:	4c 09 f2             	or     %r14,%rdx
    1947:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    194c:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1953:	44 8b 70 27          	mov    0x27(%rax),%r14d
    1957:	48 c1 e2 08          	shl    $0x8,%rdx
    195b:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
    1960:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1967:	4c 09 ea             	or     %r13,%rdx
    196a:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    196f:	44 8b 68 24          	mov    0x24(%rax),%r13d
    1973:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    197a:	48 c1 e2 08          	shl    $0x8,%rdx
    197e:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1983:	4c 09 e2             	or     %r12,%rdx
    1986:	44 8b 60 21          	mov    0x21(%rax),%r12d
    198a:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1991:	48 c1 e2 08          	shl    $0x8,%rdx
    1995:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    199a:	48 09 da             	or     %rbx,%rdx
    199d:	8b 58 1e             	mov    0x1e(%rax),%ebx
    19a0:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    19a7:	48 c1 e2 08          	shl    $0x8,%rdx
    19ab:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    19b0:	4c 09 da             	or     %r11,%rdx
    19b3:	44 8b 58 1b          	mov    0x1b(%rax),%r11d
    19b7:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    19bd:	48 c1 e2 08          	shl    $0x8,%rdx
    19c1:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    19c5:	4c 09 d2             	or     %r10,%rdx
    19c8:	44 8b 50 18          	mov    0x18(%rax),%r10d
    19cc:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    19d3:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    19d8:	8b 50 2d             	mov    0x2d(%rax),%edx
    19db:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    19e2:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    19e7:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    19ed:	c4 e2 55 90 34 86    	vpgatherdd %ymm5,(%rsi,%ymm0,4),%ymm6
    19f3:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
    19f7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    19fb:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1a00:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
    1a05:	48 c1 e2 08          	shl    $0x8,%rdx
    1a09:	4c 09 fa             	or     %r15,%rdx
    1a0c:	44 8b 78 42          	mov    0x42(%rax),%r15d
    1a10:	48 c1 e2 08          	shl    $0x8,%rdx
    1a14:	4c 09 f2             	or     %r14,%rdx
    1a17:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1a1e:	44 8b 70 3f          	mov    0x3f(%rax),%r14d
    1a22:	48 c1 e2 08          	shl    $0x8,%rdx
    1a26:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1a2b:	4c 09 ea             	or     %r13,%rdx
    1a2e:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1a35:	44 8b 68 3c          	mov    0x3c(%rax),%r13d
    1a39:	48 c1 e2 08          	shl    $0x8,%rdx
    1a3d:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1a42:	4c 09 e2             	or     %r12,%rdx
    1a45:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1a4c:	44 8b 60 39          	mov    0x39(%rax),%r12d
    1a50:	48 c1 e2 08          	shl    $0x8,%rdx
    1a54:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1a59:	48 09 da             	or     %rbx,%rdx
    1a5c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1a63:	8b 58 36             	mov    0x36(%rax),%ebx
    1a66:	48 c1 e2 08          	shl    $0x8,%rdx
    1a6a:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1a6f:	4c 09 da             	or     %r11,%rdx
    1a72:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1a78:	44 8b 58 33          	mov    0x33(%rax),%r11d
    1a7c:	48 c1 e2 08          	shl    $0x8,%rdx
    1a80:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    1a84:	4c 09 d2             	or     %r10,%rdx
    1a87:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1a8e:	44 8b 50 30          	mov    0x30(%rax),%r10d
    1a92:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    1a97:	8b 50 45             	mov    0x45(%rax),%edx
    1a9a:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1a9f:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1aa6:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    1aab:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    1ab1:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
    1ab6:	c4 e2 55 90 24 86    	vpgatherdd %ymm5,(%rsi,%ymm0,4),%ymm4
    1abc:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1ac0:	48 c1 e2 08          	shl    $0x8,%rdx
    1ac4:	4c 09 fa             	or     %r15,%rdx
    1ac7:	44 8b 78 5a          	mov    0x5a(%rax),%r15d
    1acb:	48 c1 e2 08          	shl    $0x8,%rdx
    1acf:	4c 09 f2             	or     %r14,%rdx
    1ad2:	44 8b 70 57          	mov    0x57(%rax),%r14d
    1ad6:	48 c1 e2 08          	shl    $0x8,%rdx
    1ada:	4c 09 ea             	or     %r13,%rdx
    1add:	44 8b 68 54          	mov    0x54(%rax),%r13d
    1ae1:	48 c1 e2 08          	shl    $0x8,%rdx
    1ae5:	4c 09 e2             	or     %r12,%rdx
    1ae8:	44 8b 60 51          	mov    0x51(%rax),%r12d
    1aec:	48 c1 e2 08          	shl    $0x8,%rdx
    1af0:	48 09 da             	or     %rbx,%rdx
    1af3:	8b 58 4e             	mov    0x4e(%rax),%ebx
    1af6:	48 c1 e2 08          	shl    $0x8,%rdx
    1afa:	4c 09 da             	or     %r11,%rdx
    1afd:	44 8b 58 4b          	mov    0x4b(%rax),%r11d
    1b01:	48 c1 e2 08          	shl    $0x8,%rdx
    1b05:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1b0c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1b13:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1b1a:	4c 09 d2             	or     %r10,%rdx
    1b1d:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1b22:	44 8b 50 48          	mov    0x48(%rax),%r10d
    1b26:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1b2d:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    1b32:	8b 50 5d             	mov    0x5d(%rax),%edx
    1b35:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1b3b:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    1b42:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    1b47:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1b4e:	48 83 c0 60          	add    $0x60,%rax
    1b52:	49 83 c1 60          	add    $0x60,%r9
    1b56:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    1b5c:	c4 e2 45 90 2c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm5
    1b62:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1b66:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    1b6b:	c4 e2 55 00 e9       	vpshufb %ymm1,%ymm5,%ymm5
    1b70:	46 0f b6 2c 2f       	movzbl (%rdi,%r13,1),%r13d
    1b75:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1b7a:	c4 e2 6d 36 ed       	vpermd %ymm5,%ymm2,%ymm5
    1b7f:	48 c1 e2 08          	shl    $0x8,%rdx
    1b83:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
    1b87:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
    1b8c:	c5 79 6f cd          	vmovdqa %xmm5,%xmm9
    1b90:	4c 09 fa             	or     %r15,%rdx
    1b93:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
    1b98:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1b9e:	48 c1 e2 08          	shl    $0x8,%rdx
    1ba2:	4c 09 f2             	or     %r14,%rdx
    1ba5:	48 c1 e2 08          	shl    $0x8,%rdx
    1ba9:	4c 09 ea             	or     %r13,%rdx
    1bac:	48 c1 e2 08          	shl    $0x8,%rdx
    1bb0:	4c 09 e2             	or     %r12,%rdx
    1bb3:	48 c1 e2 08          	shl    $0x8,%rdx
    1bb7:	48 09 da             	or     %rbx,%rdx
    1bba:	48 c1 e2 08          	shl    $0x8,%rdx
    1bbe:	4c 09 da             	or     %r11,%rdx
    1bc1:	48 c1 e2 08          	shl    $0x8,%rdx
    1bc5:	4c 09 d2             	or     %r10,%rdx
    1bc8:	c4 e1 f9 6e c2       	vmovq  %rdx,%xmm0
    1bcd:	48 8d 51 48          	lea    0x48(%rcx),%rdx
    1bd1:	48 83 c1 20          	add    $0x20,%rcx
    1bd5:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    1bda:	c4 e2 05 90 3c 86    	vpgatherdd %ymm15,(%rsi,%ymm0,4),%ymm7
    1be0:	c4 e2 5d 00 c1       	vpshufb %ymm1,%ymm4,%ymm0
    1be5:	c4 e2 4d 00 e1       	vpshufb %ymm1,%ymm6,%ymm4
    1bea:	c4 e2 6d 36 c0       	vpermd %ymm0,%ymm2,%ymm0
    1bef:	c4 e2 6d 36 e4       	vpermd %ymm4,%ymm2,%ymm4
    1bf4:	c4 e2 45 00 f9       	vpshufb %ymm1,%ymm7,%ymm7
    1bf9:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
    1bfd:	c4 e2 6d 36 ff       	vpermd %ymm7,%ymm2,%ymm7
    1c02:	c5 f9 6f f4          	vmovdqa %xmm4,%xmm6
    1c06:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
    1c0c:	c5 79 6f c7          	vmovdqa %xmm7,%xmm8
    1c10:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1c16:	c4 c1 59 6c e2       	vpunpcklqdq %xmm10,%xmm4,%xmm4
    1c1b:	c4 c3 79 0f c2 08    	vpalignr $0x8,%xmm10,%xmm0,%xmm0
    1c21:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    1c27:	c4 e3 4d 38 f4 01    	vinserti128 $0x1,%xmm4,%ymm6,%ymm6
    1c2d:	c4 c3 41 0f f8 08    	vpalignr $0x8,%xmm8,%xmm7,%xmm7
    1c33:	c4 c1 51 6c e0       	vpunpcklqdq %xmm8,%xmm5,%xmm4
    1c38:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
    1c3e:	c4 e3 5d 38 e7 01    	vinserti128 $0x1,%xmm7,%ymm4,%ymm4
    1c44:	c4 c1 7e 7f 71 a0    	vmovdqu %ymm6,-0x60(%r9)
    1c4a:	c4 c1 7e 7f 41 c0    	vmovdqu %ymm0,-0x40(%r9)
    1c50:	c4 c1 7e 7f 61 e0    	vmovdqu %ymm4,-0x20(%r9)
    1c56:	49 39 d0             	cmp    %rdx,%r8
    1c59:	0f 83 61 fc ff ff    	jae    18c0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x930>
    1c5f:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1c64:	4c 8b 7c 24 f0       	mov    -0x10(%rsp),%r15
    1c69:	4c 8d 59 08          	lea    0x8(%rcx),%r11
    1c6d:	4d 39 d8             	cmp    %r11,%r8
    1c70:	0f 82 43 01 00 00    	jb     1db9 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe29>
    1c76:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1c7b:	4c 8d 14 49          	lea    (%rcx,%rcx,2),%r10
    1c7f:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 1c87 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcf7>
    1c86:	00 
    1c87:	4c 89 7c 24 f0       	mov    %r15,-0x10(%rsp)
    1c8c:	4e 8d 0c 13          	lea    (%rbx,%r10,1),%r9
    1c90:	4d 01 fa             	add    %r15,%r10
    1c93:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    1c98:	4d 8b 79 08          	mov    0x8(%r9),%r15
    1c9c:	49 8b 11             	mov    (%r9),%rdx
    1c9f:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
    1ca3:	49 8b 41 10          	mov    0x10(%r9),%rax
    1ca7:	44 89 f9             	mov    %r15d,%ecx
    1caa:	49 89 d5             	mov    %rdx,%r13
    1cad:	48 89 d3             	mov    %rdx,%rbx
    1cb0:	48 c1 ea 30          	shr    $0x30,%rdx
    1cb4:	c1 e1 10             	shl    $0x10,%ecx
    1cb7:	45 89 fe             	mov    %r15d,%r14d
    1cba:	4d 89 fc             	mov    %r15,%r12
    1cbd:	49 c1 ef 38          	shr    $0x38,%r15
    1cc1:	49 c1 ec 20          	shr    $0x20,%r12
    1cc5:	09 ca                	or     %ecx,%edx
    1cc7:	89 c1                	mov    %eax,%ecx
    1cc9:	41 c1 ee 08          	shr    $0x8,%r14d
    1ccd:	c1 e1 08             	shl    $0x8,%ecx
    1cd0:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    1cd7:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    1cdd:	48 c1 eb 18          	shr    $0x18,%rbx
    1ce1:	44 09 f9             	or     %r15d,%ecx
    1ce4:	49 89 c7             	mov    %rax,%r15
    1ce7:	48 c1 e8 28          	shr    $0x28,%rax
    1ceb:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1cef:	49 c1 ef 10          	shr    $0x10,%r15
    1cf3:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1cf7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1cfd:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    1d03:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1d0a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1d0e:	41 81 e5 ff ff ff 00 	and    $0xffffff,%r13d
    1d15:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    1d1a:	48 c1 e0 08          	shl    $0x8,%rax
    1d1e:	4c 09 f8             	or     %r15,%rax
    1d21:	48 c1 e0 08          	shl    $0x8,%rax
    1d25:	48 09 c8             	or     %rcx,%rax
    1d28:	42 0f b6 0c 27       	movzbl (%rdi,%r12,1),%ecx
    1d2d:	48 c1 e0 08          	shl    $0x8,%rax
    1d31:	48 09 c8             	or     %rcx,%rax
    1d34:	42 0f b6 0c 37       	movzbl (%rdi,%r14,1),%ecx
    1d39:	48 c1 e0 08          	shl    $0x8,%rax
    1d3d:	48 09 c8             	or     %rcx,%rax
    1d40:	4c 89 d9             	mov    %r11,%rcx
    1d43:	49 83 c3 08          	add    $0x8,%r11
    1d47:	48 c1 e0 08          	shl    $0x8,%rax
    1d4b:	48 09 d0             	or     %rdx,%rax
    1d4e:	0f b6 14 1f          	movzbl (%rdi,%rbx,1),%edx
    1d52:	48 c1 e0 08          	shl    $0x8,%rax
    1d56:	48 09 d0             	or     %rdx,%rax
    1d59:	42 0f b6 14 2f       	movzbl (%rdi,%r13,1),%edx
    1d5e:	48 c1 e0 08          	shl    $0x8,%rax
    1d62:	48 09 d0             	or     %rdx,%rax
    1d65:	49 83 c1 18          	add    $0x18,%r9
    1d69:	49 83 c2 18          	add    $0x18,%r10
    1d6d:	c4 e1 f9 6e c0       	vmovq  %rax,%xmm0
    1d72:	c4 e2 7d 31 c0       	vpmovzxbd %xmm0,%ymm0
    1d77:	c4 e2 55 90 14 86    	vpgatherdd %ymm5,(%rsi,%ymm0,4),%ymm2
    1d7d:	c4 e2 6d 00 c1       	vpshufb %ymm1,%ymm2,%ymm0
    1d82:	c5 f9 6f d8          	vmovdqa %xmm0,%xmm3
    1d86:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1d8c:	c5 e9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm2
    1d91:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    1d96:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
    1d9a:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1da0:	c4 c1 7a 7f 52 e8    	vmovdqu %xmm2,-0x18(%r10)
    1da6:	4d 39 d8             	cmp    %r11,%r8
    1da9:	0f 83 e9 fe ff ff    	jae    1c98 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd08>
    1daf:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1db4:	4c 8b 7c 24 f0       	mov    -0x10(%rsp),%r15
    1db9:	4c 39 c1             	cmp    %r8,%rcx
    1dbc:	0f 83 1e 02 00 00    	jae    1fe0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1050>
    1dc2:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
    1dc6:	4c 8d 14 03          	lea    (%rbx,%rax,1),%r10
    1dca:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1dcf:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1dd4:	45 0f b6 12          	movzbl (%r10),%r10d
    1dd8:	c1 e2 08             	shl    $0x8,%edx
    1ddb:	41 c1 e3 10          	shl    $0x10,%r11d
    1ddf:	44 09 da             	or     %r11d,%edx
    1de2:	44 09 d2             	or     %r10d,%edx
    1de5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1de9:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    1ded:	41 8b 12             	mov    (%r10),%edx
    1df0:	45 0f b7 12          	movzwl (%r10),%r10d
    1df4:	c1 ea 10             	shr    $0x10,%edx
    1df7:	66 45 89 14 07       	mov    %r10w,(%r15,%rax,1)
    1dfc:	41 88 54 07 02       	mov    %dl,0x2(%r15,%rax,1)
    1e01:	48 8d 51 01          	lea    0x1(%rcx),%rdx
    1e05:	4c 39 c2             	cmp    %r8,%rdx
    1e08:	0f 83 d2 01 00 00    	jae    1fe0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1050>
    1e0e:	4c 8d 54 03 03       	lea    0x3(%rbx,%rax,1),%r10
    1e13:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1e18:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1e1d:	45 0f b6 12          	movzbl (%r10),%r10d
    1e21:	41 c1 e3 10          	shl    $0x10,%r11d
    1e25:	c1 e2 08             	shl    $0x8,%edx
    1e28:	44 09 da             	or     %r11d,%edx
    1e2b:	44 09 d2             	or     %r10d,%edx
    1e2e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1e32:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1e36:	44 8b 12             	mov    (%rdx),%r10d
    1e39:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1e3d:	48 8d 51 02          	lea    0x2(%rcx),%rdx
    1e41:	45 89 d1             	mov    %r10d,%r9d
    1e44:	66 45 89 5c 07 03    	mov    %r11w,0x3(%r15,%rax,1)
    1e4a:	41 c1 e9 10          	shr    $0x10,%r9d
    1e4e:	45 88 4c 07 05       	mov    %r9b,0x5(%r15,%rax,1)
    1e53:	4c 39 c2             	cmp    %r8,%rdx
    1e56:	0f 83 84 01 00 00    	jae    1fe0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1050>
    1e5c:	4c 8d 54 03 06       	lea    0x6(%rbx,%rax,1),%r10
    1e61:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1e66:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1e6b:	45 0f b6 12          	movzbl (%r10),%r10d
    1e6f:	41 c1 e3 10          	shl    $0x10,%r11d
    1e73:	c1 e2 08             	shl    $0x8,%edx
    1e76:	44 09 da             	or     %r11d,%edx
    1e79:	44 09 d2             	or     %r10d,%edx
    1e7c:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1e80:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1e84:	44 8b 12             	mov    (%rdx),%r10d
    1e87:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1e8b:	48 8d 51 03          	lea    0x3(%rcx),%rdx
    1e8f:	45 89 d1             	mov    %r10d,%r9d
    1e92:	66 45 89 5c 07 06    	mov    %r11w,0x6(%r15,%rax,1)
    1e98:	41 c1 e9 10          	shr    $0x10,%r9d
    1e9c:	45 88 4c 07 08       	mov    %r9b,0x8(%r15,%rax,1)
    1ea1:	4c 39 c2             	cmp    %r8,%rdx
    1ea4:	0f 83 36 01 00 00    	jae    1fe0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1050>
    1eaa:	4c 8d 54 03 09       	lea    0x9(%rbx,%rax,1),%r10
    1eaf:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1eb4:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1eb9:	45 0f b6 12          	movzbl (%r10),%r10d
    1ebd:	41 c1 e3 08          	shl    $0x8,%r11d
    1ec1:	c1 e2 10             	shl    $0x10,%edx
    1ec4:	44 09 da             	or     %r11d,%edx
    1ec7:	44 09 d2             	or     %r10d,%edx
    1eca:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1ece:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1ed2:	44 8b 12             	mov    (%rdx),%r10d
    1ed5:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1ed9:	48 8d 51 04          	lea    0x4(%rcx),%rdx
    1edd:	45 89 d1             	mov    %r10d,%r9d
    1ee0:	66 45 89 5c 07 09    	mov    %r11w,0x9(%r15,%rax,1)
    1ee6:	41 c1 e9 10          	shr    $0x10,%r9d
    1eea:	45 88 4c 07 0b       	mov    %r9b,0xb(%r15,%rax,1)
    1eef:	4c 39 c2             	cmp    %r8,%rdx
    1ef2:	0f 83 e8 00 00 00    	jae    1fe0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1050>
    1ef8:	4c 8d 54 03 0c       	lea    0xc(%rbx,%rax,1),%r10
    1efd:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1f02:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1f07:	45 0f b6 12          	movzbl (%r10),%r10d
    1f0b:	41 c1 e3 08          	shl    $0x8,%r11d
    1f0f:	c1 e2 10             	shl    $0x10,%edx
    1f12:	44 09 da             	or     %r11d,%edx
    1f15:	44 09 d2             	or     %r10d,%edx
    1f18:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1f1c:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1f20:	44 8b 12             	mov    (%rdx),%r10d
    1f23:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1f27:	48 8d 51 05          	lea    0x5(%rcx),%rdx
    1f2b:	45 89 d1             	mov    %r10d,%r9d
    1f2e:	66 45 89 5c 07 0c    	mov    %r11w,0xc(%r15,%rax,1)
    1f34:	41 c1 e9 10          	shr    $0x10,%r9d
    1f38:	45 88 4c 07 0e       	mov    %r9b,0xe(%r15,%rax,1)
    1f3d:	4c 39 c2             	cmp    %r8,%rdx
    1f40:	0f 83 9a 00 00 00    	jae    1fe0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1050>
    1f46:	4c 8d 54 03 0f       	lea    0xf(%rbx,%rax,1),%r10
    1f4b:	48 83 c1 06          	add    $0x6,%rcx
    1f4f:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1f54:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1f59:	45 0f b6 12          	movzbl (%r10),%r10d
    1f5d:	41 c1 e3 08          	shl    $0x8,%r11d
    1f61:	c1 e2 10             	shl    $0x10,%edx
    1f64:	44 09 da             	or     %r11d,%edx
    1f67:	44 09 d2             	or     %r10d,%edx
    1f6a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1f6e:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1f72:	44 8b 12             	mov    (%rdx),%r10d
    1f75:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1f79:	45 89 d1             	mov    %r10d,%r9d
    1f7c:	66 45 89 5c 07 0f    	mov    %r11w,0xf(%r15,%rax,1)
    1f82:	41 c1 e9 10          	shr    $0x10,%r9d
    1f86:	45 88 4c 07 11       	mov    %r9b,0x11(%r15,%rax,1)
    1f8b:	4c 39 c1             	cmp    %r8,%rcx
    1f8e:	73 50                	jae    1fe0 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1050>
    1f90:	48 8d 54 03 12       	lea    0x12(%rbx,%rax,1),%rdx
    1f95:	4d 8d 44 07 12       	lea    0x12(%r15,%rax,1),%r8
    1f9a:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1f9e:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1fa2:	0f b6 12             	movzbl (%rdx),%edx
    1fa5:	c1 e0 08             	shl    $0x8,%eax
    1fa8:	c1 e1 10             	shl    $0x10,%ecx
    1fab:	09 c8                	or     %ecx,%eax
    1fad:	09 d0                	or     %edx,%eax
    1faf:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1fb3:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    1fb7:	8b 02                	mov    (%rdx),%eax
    1fb9:	0f b7 12             	movzwl (%rdx),%edx
    1fbc:	c1 e8 10             	shr    $0x10,%eax
    1fbf:	66 41 89 10          	mov    %dx,(%r8)
    1fc3:	41 88 40 02          	mov    %al,0x2(%r8)
    1fc7:	c5 f8 77             	vzeroupper
    1fca:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1fce:	5b                   	pop    %rbx
    1fcf:	41 5c                	pop    %r12
    1fd1:	41 5d                	pop    %r13
    1fd3:	41 5e                	pop    %r14
    1fd5:	41 5f                	pop    %r15
    1fd7:	5d                   	pop    %rbp
    1fd8:	c3                   	ret
    1fd9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    1fe0:	c5 f8 77             	vzeroupper
    1fe3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1fe7:	5b                   	pop    %rbx
    1fe8:	41 5c                	pop    %r12
    1fea:	41 5d                	pop    %r13
    1fec:	41 5e                	pop    %r14
    1fee:	41 5f                	pop    %r15
    1ff0:	5d                   	pop    %rbp
    1ff1:	c3                   	ret
    1ff2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1ff8:	4c 89 c1             	mov    %r8,%rcx
    1ffb:	e9 69 fc ff ff       	jmp    1c69 <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcd9>
    2000:	c3                   	ret
    2001:	49 8d 42 28          	lea    0x28(%r10),%rax
    2005:	4c 89 d1             	mov    %r10,%rcx
    2008:	e9 81 f8 ff ff       	jmp    188e <jshc_channel::avx2_chain_palettegather_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x8fe>
