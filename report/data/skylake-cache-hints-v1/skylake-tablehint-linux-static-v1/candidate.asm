
artifacts/skylake-tablehint-linux-build-v1/CMakeFiles/jshc_skylake_tablehint.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 fb 13 00 00    	je     1408 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1408>
       d:	55                   	push   %rbp
       e:	48 89 f8             	mov    %rdi,%rax
      11:	49 89 d0             	mov    %rdx,%r8
      14:	48 89 d7             	mov    %rdx,%rdi
      17:	45 31 c9             	xor    %r9d,%r9d
      1a:	48 89 e5             	mov    %rsp,%rbp
      1d:	41 57                	push   %r15
      1f:	41 56                	push   %r14
      21:	41 55                	push   %r13
      23:	41 54                	push   %r12
      25:	53                   	push   %rbx
      26:	eb 4f                	jmp    77 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x77>
      28:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
      2f:	00 
      30:	41 0f b6 50 01       	movzbl 0x1(%r8),%edx
      35:	45 0f b6 50 02       	movzbl 0x2(%r8),%r10d
      3a:	49 ff c1             	inc    %r9
      3d:	49 83 c0 03          	add    $0x3,%r8
      41:	41 c1 e2 10          	shl    $0x10,%r10d
      45:	c1 e2 08             	shl    $0x8,%edx
      48:	44 09 d2             	or     %r10d,%edx
      4b:	45 0f b6 50 fd       	movzbl -0x3(%r8),%r10d
      50:	44 09 d2             	or     %r10d,%edx
      53:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
      57:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
      5b:	41 8b 12             	mov    (%r10),%edx
      5e:	45 0f b7 12          	movzwl (%r10),%r10d
      62:	c1 ea 10             	shr    $0x10,%edx
      65:	66 45 89 50 fd       	mov    %r10w,-0x3(%r8)
      6a:	41 88 50 ff          	mov    %dl,-0x1(%r8)
      6e:	4c 39 c9             	cmp    %r9,%rcx
      71:	0f 84 89 13 00 00    	je     1400 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1400>
      77:	41 f6 c0 3f          	test   $0x3f,%r8b
      7b:	75 b3                	jne    30 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
      7d:	49 8d 51 48          	lea    0x48(%r9),%rdx
      81:	48 39 d1             	cmp    %rdx,%rcx
      84:	0f 82 7f 13 00 00    	jb     1409 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1409>
      8a:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
      8e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 96 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x96>
      95:	00 
      96:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 9e <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x9e>
      9d:	00 
      9e:	48 01 fa             	add    %rdi,%rdx
      a1:	eb 08                	jmp    ab <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xab>
      a3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
      a8:	4d 89 c1             	mov    %r8,%r9
      ab:	4d 8d 81 80 00 00 00 	lea    0x80(%r9),%r8
      b2:	4c 39 c1             	cmp    %r8,%rcx
      b5:	0f 82 c9 04 00 00    	jb     584 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x584>
      bb:	44 8b 82 c0 00 00 00 	mov    0xc0(%rdx),%r8d
      c2:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
      c9:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
      ce:	44 8b 82 c3 00 00 00 	mov    0xc3(%rdx),%r8d
      d5:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
      dc:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
      e1:	44 8b 82 c6 00 00 00 	mov    0xc6(%rdx),%r8d
      e8:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
      ef:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
      f4:	44 8b 82 c9 00 00 00 	mov    0xc9(%rdx),%r8d
      fb:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     102:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     107:	44 8b 82 cc 00 00 00 	mov    0xcc(%rdx),%r8d
     10e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     115:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     11a:	44 8b 82 cf 00 00 00 	mov    0xcf(%rdx),%r8d
     121:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     128:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     12d:	44 8b 82 d2 00 00 00 	mov    0xd2(%rdx),%r8d
     134:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     13b:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     140:	44 8b 82 d5 00 00 00 	mov    0xd5(%rdx),%r8d
     147:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     14e:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     153:	44 8b 82 d8 00 00 00 	mov    0xd8(%rdx),%r8d
     15a:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     161:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     166:	44 8b 82 db 00 00 00 	mov    0xdb(%rdx),%r8d
     16d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     174:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     179:	44 8b 82 de 00 00 00 	mov    0xde(%rdx),%r8d
     180:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     187:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     18c:	44 8b 82 e1 00 00 00 	mov    0xe1(%rdx),%r8d
     193:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     19a:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     19f:	44 8b 82 e4 00 00 00 	mov    0xe4(%rdx),%r8d
     1a6:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1ad:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     1b2:	44 8b 82 e7 00 00 00 	mov    0xe7(%rdx),%r8d
     1b9:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1c0:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     1c5:	44 8b 82 ea 00 00 00 	mov    0xea(%rdx),%r8d
     1cc:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1d3:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     1d8:	44 8b 82 ed 00 00 00 	mov    0xed(%rdx),%r8d
     1df:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1e6:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     1eb:	44 8b 82 f0 00 00 00 	mov    0xf0(%rdx),%r8d
     1f2:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     1f9:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     1fe:	44 8b 82 f3 00 00 00 	mov    0xf3(%rdx),%r8d
     205:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     20c:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     211:	44 8b 82 f6 00 00 00 	mov    0xf6(%rdx),%r8d
     218:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     21f:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     224:	44 8b 82 f9 00 00 00 	mov    0xf9(%rdx),%r8d
     22b:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     232:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     237:	44 8b 82 fc 00 00 00 	mov    0xfc(%rdx),%r8d
     23e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     245:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     24a:	44 8b 82 ff 00 00 00 	mov    0xff(%rdx),%r8d
     251:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     258:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     25d:	44 8b 82 02 01 00 00 	mov    0x102(%rdx),%r8d
     264:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     26b:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     270:	44 8b 82 05 01 00 00 	mov    0x105(%rdx),%r8d
     277:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     27e:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     283:	44 8b 82 08 01 00 00 	mov    0x108(%rdx),%r8d
     28a:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     291:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     296:	44 8b 82 0b 01 00 00 	mov    0x10b(%rdx),%r8d
     29d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2a4:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     2a9:	44 8b 82 0e 01 00 00 	mov    0x10e(%rdx),%r8d
     2b0:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2b7:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     2bc:	44 8b 82 11 01 00 00 	mov    0x111(%rdx),%r8d
     2c3:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2ca:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     2cf:	44 8b 82 14 01 00 00 	mov    0x114(%rdx),%r8d
     2d6:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2dd:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     2e2:	44 8b 82 17 01 00 00 	mov    0x117(%rdx),%r8d
     2e9:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     2f0:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     2f5:	44 8b 82 1a 01 00 00 	mov    0x11a(%rdx),%r8d
     2fc:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     303:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     308:	44 8b 82 1d 01 00 00 	mov    0x11d(%rdx),%r8d
     30f:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     316:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     31b:	44 8b 82 20 01 00 00 	mov    0x120(%rdx),%r8d
     322:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     329:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     32e:	44 8b 82 23 01 00 00 	mov    0x123(%rdx),%r8d
     335:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     33c:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     341:	44 8b 82 26 01 00 00 	mov    0x126(%rdx),%r8d
     348:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     34f:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     354:	44 8b 82 29 01 00 00 	mov    0x129(%rdx),%r8d
     35b:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     362:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     367:	44 8b 82 2c 01 00 00 	mov    0x12c(%rdx),%r8d
     36e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     375:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     37a:	44 8b 82 2f 01 00 00 	mov    0x12f(%rdx),%r8d
     381:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     388:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     38d:	44 8b 82 32 01 00 00 	mov    0x132(%rdx),%r8d
     394:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     39b:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     3a0:	44 8b 82 35 01 00 00 	mov    0x135(%rdx),%r8d
     3a7:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3ae:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     3b3:	44 8b 82 38 01 00 00 	mov    0x138(%rdx),%r8d
     3ba:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3c1:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     3c6:	44 8b 82 3b 01 00 00 	mov    0x13b(%rdx),%r8d
     3cd:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3d4:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     3d9:	44 8b 82 3e 01 00 00 	mov    0x13e(%rdx),%r8d
     3e0:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3e7:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     3ec:	44 8b 82 41 01 00 00 	mov    0x141(%rdx),%r8d
     3f3:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     3fa:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     3ff:	44 8b 82 44 01 00 00 	mov    0x144(%rdx),%r8d
     406:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     40d:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     412:	44 8b 82 47 01 00 00 	mov    0x147(%rdx),%r8d
     419:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     420:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     425:	44 8b 82 4a 01 00 00 	mov    0x14a(%rdx),%r8d
     42c:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     433:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     438:	44 8b 82 4d 01 00 00 	mov    0x14d(%rdx),%r8d
     43f:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     446:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     44b:	44 8b 82 50 01 00 00 	mov    0x150(%rdx),%r8d
     452:	44 0f b7 92 7d 01 00 	movzwl 0x17d(%rdx),%r10d
     459:	00 
     45a:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     461:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     466:	44 8b 82 53 01 00 00 	mov    0x153(%rdx),%r8d
     46d:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     474:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     479:	44 8b 82 56 01 00 00 	mov    0x156(%rdx),%r8d
     480:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     487:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     48c:	44 8b 82 59 01 00 00 	mov    0x159(%rdx),%r8d
     493:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     49a:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     49f:	44 8b 82 5c 01 00 00 	mov    0x15c(%rdx),%r8d
     4a6:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4ad:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     4b2:	44 8b 82 5f 01 00 00 	mov    0x15f(%rdx),%r8d
     4b9:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4c0:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     4c5:	44 8b 82 62 01 00 00 	mov    0x162(%rdx),%r8d
     4cc:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4d3:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     4d8:	44 8b 82 65 01 00 00 	mov    0x165(%rdx),%r8d
     4df:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4e6:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     4eb:	44 8b 82 68 01 00 00 	mov    0x168(%rdx),%r8d
     4f2:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     4f9:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     4fe:	44 8b 82 6b 01 00 00 	mov    0x16b(%rdx),%r8d
     505:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     50c:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     511:	44 8b 82 6e 01 00 00 	mov    0x16e(%rdx),%r8d
     518:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     51f:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     524:	44 8b 82 71 01 00 00 	mov    0x171(%rdx),%r8d
     52b:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     532:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     537:	44 8b 82 74 01 00 00 	mov    0x174(%rdx),%r8d
     53e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     545:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     54a:	44 8b 82 77 01 00 00 	mov    0x177(%rdx),%r8d
     551:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     558:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     55d:	44 8b 82 7a 01 00 00 	mov    0x17a(%rdx),%r8d
     564:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     56b:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     570:	44 0f b6 82 7f 01 00 	movzbl 0x17f(%rdx),%r8d
     577:	00 
     578:	41 c1 e0 10          	shl    $0x10,%r8d
     57c:	45 09 d0             	or     %r10d,%r8d
     57f:	42 0f 18 0c 00       	prefetcht0 (%rax,%r8,1)
     584:	44 8b 62 0c          	mov    0xc(%rdx),%r12d
     588:	44 8b 72 12          	mov    0x12(%rdx),%r14d
     58c:	44 8b 02             	mov    (%rdx),%r8d
     58f:	44 8b 5a 06          	mov    0x6(%rdx),%r11d
     593:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     59a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5a1:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     5a6:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     5ab:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     5b2:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     5b9:	44 8b 62 0f          	mov    0xf(%rdx),%r12d
     5bd:	44 8b 72 15          	mov    0x15(%rdx),%r14d
     5c1:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     5c7:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     5cd:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     5d4:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     5db:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     5e0:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     5e5:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     5ea:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     5ef:	44 8b 42 03          	mov    0x3(%rdx),%r8d
     5f3:	44 8b 5a 09          	mov    0x9(%rdx),%r11d
     5f7:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     5fe:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     605:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     60c:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     613:	c4 21 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm9
     619:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     61e:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     623:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     627:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     62c:	c4 23 31 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm9,%xmm9
     633:	44 8b 42 18          	mov    0x18(%rdx),%r8d
     637:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     63e:	44 8b 5a 1e          	mov    0x1e(%rdx),%r11d
     642:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     649:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     650:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     655:	44 8b 42 1b          	mov    0x1b(%rdx),%r8d
     659:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     65d:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     662:	44 8b 5a 21          	mov    0x21(%rdx),%r11d
     666:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     66c:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     673:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     678:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     67f:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     684:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     689:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     68e:	44 8b 62 24          	mov    0x24(%rdx),%r12d
     692:	44 8b 72 2a          	mov    0x2a(%rdx),%r14d
     696:	c4 a1 79 6e 34 96    	vmovd  (%rsi,%r10,4),%xmm6
     69c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     6a3:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     6aa:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     6af:	44 8b 62 27          	mov    0x27(%rdx),%r12d
     6b3:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     6b8:	44 8b 72 2d          	mov    0x2d(%rdx),%r14d
     6bc:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     6c3:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     6c9:	c4 a3 49 22 34 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm6,%xmm6
     6d0:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     6d7:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     6dc:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     6e2:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     6e7:	44 8b 42 30          	mov    0x30(%rdx),%r8d
     6eb:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     6f2:	44 8b 62 3c          	mov    0x3c(%rdx),%r12d
     6f6:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     6fd:	44 8b 72 42          	mov    0x42(%rdx),%r14d
     701:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     708:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     70f:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     714:	44 8b 42 33          	mov    0x33(%rdx),%r8d
     718:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     71c:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     721:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     728:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     72d:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     732:	44 8b 62 3f          	mov    0x3f(%rdx),%r12d
     736:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     73d:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     744:	44 8b 5a 36          	mov    0x36(%rdx),%r11d
     748:	44 8b 72 45          	mov    0x45(%rdx),%r14d
     74c:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     753:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     758:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     75f:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     763:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     768:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     76d:	44 8b 5a 39          	mov    0x39(%rdx),%r11d
     771:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     778:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     77e:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     783:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     788:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     78f:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     794:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     799:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     79f:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     7a3:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     7a9:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     7af:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     7b5:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     7bb:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     7c2:	44 8b 72 5a          	mov    0x5a(%rdx),%r14d
     7c6:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     7cd:	44 8b 62 54          	mov    0x54(%rdx),%r12d
     7d1:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     7d8:	c4 a3 51 22 2c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm5,%xmm5
     7df:	44 8b 42 48          	mov    0x48(%rdx),%r8d
     7e3:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     7e7:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     7ec:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     7f3:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     7f8:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     7fd:	44 8b 72 5d          	mov    0x5d(%rdx),%r14d
     801:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     808:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     80f:	44 8b 62 57          	mov    0x57(%rdx),%r12d
     813:	44 8b 5a 4e          	mov    0x4e(%rdx),%r11d
     817:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     81e:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     823:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     827:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     82e:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     833:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     839:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     83e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     845:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     84b:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     851:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     856:	44 8b 42 4b          	mov    0x4b(%rdx),%r8d
     85a:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     85f:	44 8b 5a 51          	mov    0x51(%rdx),%r11d
     863:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     86a:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     86f:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     876:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     87d:	c4 21 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm8
     883:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     887:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     88e:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     893:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     899:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     89f:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     8a4:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     8a8:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     8ad:	c4 23 39 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm8,%xmm8
     8b4:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     8bb:	44 8b 42 60          	mov    0x60(%rdx),%r8d
     8bf:	44 8b 62 6c          	mov    0x6c(%rdx),%r12d
     8c3:	44 8b 72 72          	mov    0x72(%rdx),%r14d
     8c7:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     8ce:	44 8b 5a 66          	mov    0x66(%rdx),%r11d
     8d2:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     8d6:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     8dd:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     8e4:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     8ea:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     8ef:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     8f4:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     8f9:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     900:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     905:	44 8b 62 6f          	mov    0x6f(%rdx),%r12d
     909:	44 8b 72 75          	mov    0x75(%rdx),%r14d
     90d:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     912:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     918:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     91e:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     925:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     92c:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     931:	44 8b 42 63          	mov    0x63(%rdx),%r8d
     935:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     93a:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     93f:	44 8b 5a 69          	mov    0x69(%rdx),%r11d
     943:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     94a:	c4 a1 79 6e 3c 96    	vmovd  (%rsi,%r10,4),%xmm7
     950:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     957:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     95e:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     965:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     96a:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     96f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     973:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     978:	c4 a3 41 22 3c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm7,%xmm7
     97f:	44 8b 42 78          	mov    0x78(%rdx),%r8d
     983:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     98a:	44 8b 5a 7e          	mov    0x7e(%rdx),%r11d
     98e:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     995:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     99c:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     9a1:	44 8b 42 7b          	mov    0x7b(%rdx),%r8d
     9a5:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     9a9:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     9ae:	44 8b 9a 81 00 00 00 	mov    0x81(%rdx),%r11d
     9b5:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     9bb:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     9c2:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     9c7:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     9ce:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     9d3:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     9d8:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     9dd:	44 8b a2 84 00 00 00 	mov    0x84(%rdx),%r12d
     9e4:	44 8b b2 8a 00 00 00 	mov    0x8a(%rdx),%r14d
     9eb:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     9f0:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     9f7:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     9fe:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     a03:	44 8b a2 87 00 00 00 	mov    0x87(%rdx),%r12d
     a0a:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     a0f:	44 8b b2 8d 00 00 00 	mov    0x8d(%rdx),%r14d
     a16:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a1d:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     a23:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     a2a:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a31:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     a36:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     a3c:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     a41:	44 8b 9a 96 00 00 00 	mov    0x96(%rdx),%r11d
     a48:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     a4f:	44 8b a2 9c 00 00 00 	mov    0x9c(%rdx),%r12d
     a56:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     a5d:	44 8b b2 a2 00 00 00 	mov    0xa2(%rdx),%r14d
     a64:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     a6b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     a72:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     a77:	44 8b 9a 99 00 00 00 	mov    0x99(%rdx),%r11d
     a7e:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     a82:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     a88:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     a8f:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     a94:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     a99:	44 8b a2 9f 00 00 00 	mov    0x9f(%rdx),%r12d
     aa0:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     aa7:	c4 a3 79 22 04 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm0,%xmm0
     aae:	44 8b 82 90 00 00 00 	mov    0x90(%rdx),%r8d
     ab5:	44 8b b2 a5 00 00 00 	mov    0xa5(%rdx),%r14d
     abc:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     ac3:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     ac8:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     acf:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     ad3:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     ad8:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     add:	44 8b 82 93 00 00 00 	mov    0x93(%rdx),%r8d
     ae4:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     aeb:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     af1:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     af6:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     afb:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     b02:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     b07:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     b0c:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     b12:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     b18:	c5 79 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm10
     b1d:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     b24:	44 8b b2 ba 00 00 00 	mov    0xba(%rdx),%r14d
     b2b:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     b32:	44 8b a2 b4 00 00 00 	mov    0xb4(%rdx),%r12d
     b39:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b40:	c4 23 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm10,%xmm10
     b47:	44 8b 9a ae 00 00 00 	mov    0xae(%rdx),%r11d
     b4e:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     b52:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     b58:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     b5f:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     b64:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     b69:	44 8b b2 bd 00 00 00 	mov    0xbd(%rdx),%r14d
     b70:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     b77:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
     b7e:	44 8b a2 b7 00 00 00 	mov    0xb7(%rdx),%r12d
     b85:	44 8b 82 a8 00 00 00 	mov    0xa8(%rdx),%r8d
     b8c:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     b93:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     b98:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     b9d:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     ba4:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     ba9:	c4 21 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm10
     baf:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     bb6:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     bbb:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     bc1:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     bc7:	46 0f b6 14 00       	movzbl (%rax,%r8,1),%r10d
     bcc:	44 8b 9a b1 00 00 00 	mov    0xb1(%rdx),%r11d
     bd3:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     bd8:	44 8b 82 ab 00 00 00 	mov    0xab(%rdx),%r8d
     bdf:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
     be6:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     beb:	c4 23 29 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm10,%xmm10
     bf2:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     bf9:	c5 79 6e 1c 9e       	vmovd  (%rsi,%rbx,4),%xmm11
     bfe:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
     c05:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     c0a:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
     c11:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
     c16:	c5 29 6c d2          	vpunpcklqdq %xmm2,%xmm10,%xmm10
     c1a:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
     c20:	4d 8d 91 88 00 00 00 	lea    0x88(%r9),%r10
     c27:	c4 23 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm11,%xmm11
     c2e:	c4 a3 69 22 14 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm2,%xmm2
     c35:	4d 8d 41 40          	lea    0x40(%r9),%r8
     c39:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     c3e:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     c43:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     c49:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     c4f:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     c54:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     c5a:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     c60:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     c65:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     c6a:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     c6f:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     c74:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     c7a:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     c80:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
     c87:	ff 
     c88:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     c8c:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     c90:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
     c97:	ff 
     c98:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
     c9d:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     ca1:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     ca5:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     cab:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     cb1:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     cb7:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     cbd:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     cc2:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     cc6:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     ccc:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     cd2:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     cd8:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     cde:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     ce4:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
     ce9:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
     cee:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
     cf3:	4c 39 d1             	cmp    %r10,%rcx
     cf6:	0f 83 ac f3 ff ff    	jae    a8 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xa8>
     cfc:	0f ae f8             	sfence
     cff:	49 8d 51 68          	lea    0x68(%r9),%rdx
     d03:	48 39 d1             	cmp    %rdx,%rcx
     d06:	0f 82 ba 03 00 00    	jb     10c6 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10c6>
     d0c:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     d10:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # d18 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd18>
     d17:	00 
     d18:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # d20 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd20>
     d1f:	00 
     d20:	48 01 fa             	add    %rdi,%rdx
     d23:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     d28:	44 8b 62 54          	mov    0x54(%rdx),%r12d
     d2c:	44 8b 72 5a          	mov    0x5a(%rdx),%r14d
     d30:	44 8b 4a 48          	mov    0x48(%rdx),%r9d
     d34:	44 8b 5a 4e          	mov    0x4e(%rdx),%r11d
     d38:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     d3f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     d46:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     d4b:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     d50:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d57:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     d5e:	44 8b 62 57          	mov    0x57(%rdx),%r12d
     d62:	44 8b 72 5d          	mov    0x5d(%rdx),%r14d
     d66:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     d6c:	c4 a1 79 6e 04 ae    	vmovd  (%rsi,%r13,4),%xmm0
     d72:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     d79:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     d80:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     d85:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     d8a:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     d8f:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     d94:	44 8b 4a 4b          	mov    0x4b(%rdx),%r9d
     d98:	44 8b 5a 51          	mov    0x51(%rdx),%r11d
     d9c:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     da3:	c4 a3 79 22 04 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm0,%xmm0
     daa:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     db1:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     db8:	c4 a1 79 6e 2c 96    	vmovd  (%rsi,%r10,4),%xmm5
     dbe:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
     dc3:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     dc8:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     dcc:	c5 f9 6e 0c 9e       	vmovd  (%rsi,%rbx,4),%xmm1
     dd1:	c4 a3 51 22 2c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm5,%xmm5
     dd8:	44 8b 4a 30          	mov    0x30(%rdx),%r9d
     ddc:	c4 a3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm1,%xmm1
     de3:	44 8b 5a 36          	mov    0x36(%rdx),%r11d
     de7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     dee:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     df5:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     dfa:	44 8b 4a 33          	mov    0x33(%rdx),%r9d
     dfe:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     e02:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     e07:	44 8b 5a 39          	mov    0x39(%rdx),%r11d
     e0b:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     e11:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e18:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     e1d:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     e24:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
     e29:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     e2e:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     e33:	44 8b 62 3c          	mov    0x3c(%rdx),%r12d
     e37:	44 8b 72 42          	mov    0x42(%rdx),%r14d
     e3b:	c5 f9 6e 14 9e       	vmovd  (%rsi,%rbx,4),%xmm2
     e40:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     e47:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     e4e:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     e53:	44 8b 62 3f          	mov    0x3f(%rdx),%r12d
     e57:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     e5c:	44 8b 72 45          	mov    0x45(%rdx),%r14d
     e60:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     e67:	c4 a1 79 6e 0c ae    	vmovd  (%rsi,%r13,4),%xmm1
     e6d:	c4 a3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm2,%xmm2
     e74:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     e7b:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     e80:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
     e86:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     e8b:	44 8b 5a 1e          	mov    0x1e(%rdx),%r11d
     e8f:	c4 a3 71 22 0c a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm1,%xmm1
     e96:	44 8b 62 24          	mov    0x24(%rdx),%r12d
     e9a:	c4 a3 79 22 04 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm0,%xmm0
     ea1:	44 8b 72 2a          	mov    0x2a(%rdx),%r14d
     ea5:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     eac:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     eb3:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     eb8:	44 8b 5a 21          	mov    0x21(%rdx),%r11d
     ebc:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
     ec0:	c4 a1 79 6e 04 96    	vmovd  (%rsi,%r10,4),%xmm0
     ec6:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     ecd:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     ed2:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     ed7:	44 8b 62 27          	mov    0x27(%rdx),%r12d
     edb:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     ee2:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
     ee9:	44 8b 4a 18          	mov    0x18(%rdx),%r9d
     eed:	44 8b 72 2d          	mov    0x2d(%rdx),%r14d
     ef1:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     ef8:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
     efd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f04:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     f08:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     f0d:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     f12:	44 8b 4a 1b          	mov    0x1b(%rdx),%r9d
     f16:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     f1d:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     f23:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     f28:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     f2d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f34:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     f39:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
     f3e:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     f44:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
     f48:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     f4e:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
     f54:	c5 f9 6e 34 9e       	vmovd  (%rsi,%rbx,4),%xmm6
     f59:	c4 a3 71 22 0c b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm1,%xmm1
     f60:	44 8b 72 12          	mov    0x12(%rdx),%r14d
     f64:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
     f6b:	44 8b 62 0c          	mov    0xc(%rdx),%r12d
     f6f:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     f76:	c4 a3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm6,%xmm6
     f7d:	44 8b 5a 06          	mov    0x6(%rdx),%r11d
     f81:	c5 e9 6c d1          	vpunpcklqdq %xmm1,%xmm2,%xmm2
     f85:	c4 a1 79 6e 0c 96    	vmovd  (%rsi,%r10,4),%xmm1
     f8b:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     f92:	46 0f b6 3c 30       	movzbl (%rax,%r14,1),%r15d
     f97:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
     f9c:	44 8b 72 15          	mov    0x15(%rdx),%r14d
     fa0:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
     fa7:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     fae:	44 8b 62 0f          	mov    0xf(%rdx),%r12d
     fb2:	44 8b 0a             	mov    (%rdx),%r9d
     fb5:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
     fbc:	42 0f b6 1c 18       	movzbl (%rax,%r11,1),%ebx
     fc1:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     fc5:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
     fcc:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
     fd1:	c4 a1 79 6e 34 ae    	vmovd  (%rsi,%r13,4),%xmm6
     fd7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fde:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
     fe3:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     fe9:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     fef:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
     ff4:	44 8b 5a 09          	mov    0x9(%rdx),%r11d
     ff8:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     ffd:	44 8b 4a 03          	mov    0x3(%rdx),%r9d
    1001:	c4 a3 69 22 14 b6 01 	vpinsrd $0x1,(%rsi,%r14,4),%xmm2,%xmm2
    1008:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    100d:	c4 a3 49 22 34 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm6,%xmm6
    1014:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
    101b:	c5 f9 6e 3c 9e       	vmovd  (%rsi,%rbx,4),%xmm7
    1020:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1024:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    102b:	46 0f b6 1c 18       	movzbl (%rax,%r11,1),%r11d
    1030:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1036:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    103b:	c5 c9 6c f2          	vpunpcklqdq %xmm2,%xmm6,%xmm6
    103f:	c4 a1 79 6e 14 96    	vmovd  (%rsi,%r10,4),%xmm2
    1045:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    104b:	c4 a3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%r11,4),%xmm7,%xmm7
    1052:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1058:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    105f:	4d 8d 48 48          	lea    0x48(%r8),%r9
    1063:	49 83 c0 20          	add    $0x20,%r8
    1067:	48 83 c2 60          	add    $0x60,%rdx
    106b:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    106f:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    1073:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1079:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    107f:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    1085:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1089:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    108e:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    1094:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1099:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    109d:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    10a3:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    10a8:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    10ae:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    10b3:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    10b8:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    10bd:	4c 39 c9             	cmp    %r9,%rcx
    10c0:	0f 83 62 fc ff ff    	jae    d28 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd28>
    10c6:	4d 8d 48 08          	lea    0x8(%r8),%r9
    10ca:	4c 39 c9             	cmp    %r9,%rcx
    10cd:	0f 82 2d 01 00 00    	jb     1200 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1200>
    10d3:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
    10d7:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 10df <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10df>
    10de:	00 
    10df:	48 01 fa             	add    %rdi,%rdx
    10e2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    10e8:	48 8b 1a             	mov    (%rdx),%rbx
    10eb:	4c 8b 42 08          	mov    0x8(%rdx),%r8
    10ef:	48 83 c2 18          	add    $0x18,%rdx
    10f3:	4c 8b 6a f8          	mov    -0x8(%rdx),%r13
    10f7:	49 89 da             	mov    %rbx,%r10
    10fa:	4d 89 c6             	mov    %r8,%r14
    10fd:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1104:	45 89 ef             	mov    %r13d,%r15d
    1107:	49 c1 ee 20          	shr    $0x20,%r14
    110b:	46 0f b6 1c 10       	movzbl (%rax,%r10,1),%r11d
    1110:	49 89 da             	mov    %rbx,%r10
    1113:	48 c1 eb 30          	shr    $0x30,%rbx
    1117:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    111e:	41 c1 e7 08          	shl    $0x8,%r15d
    1122:	49 89 dc             	mov    %rbx,%r12
    1125:	44 89 c3             	mov    %r8d,%ebx
    1128:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
    112d:	c1 e3 10             	shl    $0x10,%ebx
    1130:	49 c1 ea 18          	shr    $0x18,%r10
    1134:	44 09 e3             	or     %r12d,%ebx
    1137:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    113d:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
    1144:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
    114a:	46 0f b6 14 10       	movzbl (%rax,%r10,1),%r10d
    114f:	44 0f b6 24 18       	movzbl (%rax,%rbx,1),%r12d
    1154:	44 89 c3             	mov    %r8d,%ebx
    1157:	49 c1 e8 38          	shr    $0x38,%r8
    115b:	45 09 f8             	or     %r15d,%r8d
    115e:	4d 89 ef             	mov    %r13,%r15
    1161:	49 c1 ed 28          	shr    $0x28,%r13
    1165:	49 c1 ef 10          	shr    $0x10,%r15
    1169:	41 81 e0 ff ff ff 00 	and    $0xffffff,%r8d
    1170:	46 0f b6 2c 28       	movzbl (%rax,%r13,1),%r13d
    1175:	c1 eb 08             	shr    $0x8,%ebx
    1178:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    117f:	46 0f b6 04 00       	movzbl (%rax,%r8,1),%r8d
    1184:	0f b6 1c 18          	movzbl (%rax,%rbx,1),%ebx
    1188:	46 0f b6 3c 38       	movzbl (%rax,%r15,1),%r15d
    118d:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1193:	c4 a3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%r8,4),%xmm1,%xmm1
    119a:	4d 89 c8             	mov    %r9,%r8
    119d:	49 83 c1 08          	add    $0x8,%r9
    11a1:	c4 a1 79 6e 04 be    	vmovd  (%rsi,%r15,4),%xmm0
    11a7:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    11ae:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    11b5:	c5 f1 6c c8          	vpunpcklqdq %xmm0,%xmm1,%xmm1
    11b9:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    11bf:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    11c6:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    11ca:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    11d0:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    11d5:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    11d9:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    11df:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    11e4:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    11e9:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    11ed:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
    11f2:	c5 fa 7f 4a e8       	vmovdqu %xmm1,-0x18(%rdx)
    11f7:	4c 39 c9             	cmp    %r9,%rcx
    11fa:	0f 83 e8 fe ff ff    	jae    10e8 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10e8>
    1200:	49 39 c8             	cmp    %rcx,%r8
    1203:	0f 83 e7 01 00 00    	jae    13f0 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13f0>
    1209:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
    120d:	4e 8d 14 0f          	lea    (%rdi,%r9,1),%r10
    1211:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1216:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    121b:	c1 e2 08             	shl    $0x8,%edx
    121e:	41 c1 e3 10          	shl    $0x10,%r11d
    1222:	44 09 da             	or     %r11d,%edx
    1225:	45 0f b6 1a          	movzbl (%r10),%r11d
    1229:	44 09 da             	or     %r11d,%edx
    122c:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    1230:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
    1234:	41 8b 13             	mov    (%r11),%edx
    1237:	45 0f b7 1b          	movzwl (%r11),%r11d
    123b:	c1 ea 10             	shr    $0x10,%edx
    123e:	66 45 89 1a          	mov    %r11w,(%r10)
    1242:	41 88 52 02          	mov    %dl,0x2(%r10)
    1246:	49 8d 50 01          	lea    0x1(%r8),%rdx
    124a:	48 39 ca             	cmp    %rcx,%rdx
    124d:	0f 83 9d 01 00 00    	jae    13f0 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13f0>
    1253:	4e 8d 54 0f 03       	lea    0x3(%rdi,%r9,1),%r10
    1258:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    125d:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1262:	c1 e2 08             	shl    $0x8,%edx
    1265:	41 c1 e3 10          	shl    $0x10,%r11d
    1269:	44 09 da             	or     %r11d,%edx
    126c:	45 0f b6 1a          	movzbl (%r10),%r11d
    1270:	44 09 da             	or     %r11d,%edx
    1273:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    1277:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
    127b:	41 8b 13             	mov    (%r11),%edx
    127e:	45 0f b7 1b          	movzwl (%r11),%r11d
    1282:	c1 ea 10             	shr    $0x10,%edx
    1285:	66 45 89 1a          	mov    %r11w,(%r10)
    1289:	41 88 52 02          	mov    %dl,0x2(%r10)
    128d:	49 8d 50 02          	lea    0x2(%r8),%rdx
    1291:	48 39 ca             	cmp    %rcx,%rdx
    1294:	0f 83 56 01 00 00    	jae    13f0 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13f0>
    129a:	4e 8d 54 0f 06       	lea    0x6(%rdi,%r9,1),%r10
    129f:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    12a4:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    12a9:	c1 e2 08             	shl    $0x8,%edx
    12ac:	41 c1 e3 10          	shl    $0x10,%r11d
    12b0:	44 09 da             	or     %r11d,%edx
    12b3:	45 0f b6 1a          	movzbl (%r10),%r11d
    12b7:	44 09 da             	or     %r11d,%edx
    12ba:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    12be:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
    12c2:	41 8b 13             	mov    (%r11),%edx
    12c5:	45 0f b7 1b          	movzwl (%r11),%r11d
    12c9:	c1 ea 10             	shr    $0x10,%edx
    12cc:	66 45 89 1a          	mov    %r11w,(%r10)
    12d0:	41 88 52 02          	mov    %dl,0x2(%r10)
    12d4:	49 8d 50 03          	lea    0x3(%r8),%rdx
    12d8:	48 39 ca             	cmp    %rcx,%rdx
    12db:	0f 83 0f 01 00 00    	jae    13f0 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13f0>
    12e1:	4e 8d 54 0f 09       	lea    0x9(%rdi,%r9,1),%r10
    12e6:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    12eb:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    12f0:	c1 e2 10             	shl    $0x10,%edx
    12f3:	41 c1 e3 08          	shl    $0x8,%r11d
    12f7:	44 09 da             	or     %r11d,%edx
    12fa:	45 0f b6 1a          	movzbl (%r10),%r11d
    12fe:	44 09 da             	or     %r11d,%edx
    1301:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    1305:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
    1309:	41 8b 13             	mov    (%r11),%edx
    130c:	45 0f b7 1b          	movzwl (%r11),%r11d
    1310:	c1 ea 10             	shr    $0x10,%edx
    1313:	66 45 89 1a          	mov    %r11w,(%r10)
    1317:	41 88 52 02          	mov    %dl,0x2(%r10)
    131b:	49 8d 50 04          	lea    0x4(%r8),%rdx
    131f:	48 39 ca             	cmp    %rcx,%rdx
    1322:	0f 83 c8 00 00 00    	jae    13f0 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13f0>
    1328:	4e 8d 54 0f 0c       	lea    0xc(%rdi,%r9,1),%r10
    132d:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1332:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1337:	c1 e2 10             	shl    $0x10,%edx
    133a:	41 c1 e3 08          	shl    $0x8,%r11d
    133e:	44 09 da             	or     %r11d,%edx
    1341:	45 0f b6 1a          	movzbl (%r10),%r11d
    1345:	44 09 da             	or     %r11d,%edx
    1348:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    134c:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
    1350:	41 8b 13             	mov    (%r11),%edx
    1353:	45 0f b7 1b          	movzwl (%r11),%r11d
    1357:	c1 ea 10             	shr    $0x10,%edx
    135a:	66 45 89 1a          	mov    %r11w,(%r10)
    135e:	41 88 52 02          	mov    %dl,0x2(%r10)
    1362:	49 8d 50 05          	lea    0x5(%r8),%rdx
    1366:	48 39 ca             	cmp    %rcx,%rdx
    1369:	0f 83 81 00 00 00    	jae    13f0 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13f0>
    136f:	4e 8d 54 0f 0f       	lea    0xf(%rdi,%r9,1),%r10
    1374:	49 83 c0 06          	add    $0x6,%r8
    1378:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    137d:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    1382:	c1 e2 10             	shl    $0x10,%edx
    1385:	41 c1 e3 08          	shl    $0x8,%r11d
    1389:	44 09 da             	or     %r11d,%edx
    138c:	45 0f b6 1a          	movzbl (%r10),%r11d
    1390:	44 09 da             	or     %r11d,%edx
    1393:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    1397:	4c 8d 1c 96          	lea    (%rsi,%rdx,4),%r11
    139b:	41 8b 13             	mov    (%r11),%edx
    139e:	45 0f b7 1b          	movzwl (%r11),%r11d
    13a2:	c1 ea 10             	shr    $0x10,%edx
    13a5:	66 45 89 1a          	mov    %r11w,(%r10)
    13a9:	41 88 52 02          	mov    %dl,0x2(%r10)
    13ad:	49 39 c8             	cmp    %rcx,%r8
    13b0:	73 3e                	jae    13f0 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x13f0>
    13b2:	4a 8d 4c 0f 12       	lea    0x12(%rdi,%r9,1),%rcx
    13b7:	0f b6 51 01          	movzbl 0x1(%rcx),%edx
    13bb:	0f b6 79 02          	movzbl 0x2(%rcx),%edi
    13bf:	c1 e2 08             	shl    $0x8,%edx
    13c2:	c1 e7 10             	shl    $0x10,%edi
    13c5:	09 fa                	or     %edi,%edx
    13c7:	0f b6 39             	movzbl (%rcx),%edi
    13ca:	09 fa                	or     %edi,%edx
    13cc:	0f b6 04 10          	movzbl (%rax,%rdx,1),%eax
    13d0:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    13d4:	8b 02                	mov    (%rdx),%eax
    13d6:	0f b7 12             	movzwl (%rdx),%edx
    13d9:	c1 e8 10             	shr    $0x10,%eax
    13dc:	66 89 11             	mov    %dx,(%rcx)
    13df:	88 41 02             	mov    %al,0x2(%rcx)
    13e2:	c5 f8 77             	vzeroupper
    13e5:	5b                   	pop    %rbx
    13e6:	41 5c                	pop    %r12
    13e8:	41 5d                	pop    %r13
    13ea:	41 5e                	pop    %r14
    13ec:	41 5f                	pop    %r15
    13ee:	5d                   	pop    %rbp
    13ef:	c3                   	ret
    13f0:	c5 f8 77             	vzeroupper
    13f3:	5b                   	pop    %rbx
    13f4:	41 5c                	pop    %r12
    13f6:	41 5d                	pop    %r13
    13f8:	41 5e                	pop    %r14
    13fa:	41 5f                	pop    %r15
    13fc:	5d                   	pop    %rbp
    13fd:	c3                   	ret
    13fe:	66 90                	xchg   %ax,%ax
    1400:	49 89 c8             	mov    %rcx,%r8
    1403:	e9 be fc ff ff       	jmp    10c6 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x10c6>
    1408:	c3                   	ret
    1409:	49 8d 51 28          	lea    0x28(%r9),%rdx
    140d:	4d 89 c8             	mov    %r9,%r8
    1410:	e9 ee f8 ff ff       	jmp    d03 <jshc_channel::avx2_chain_tablehint(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd03>
    1415:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
    141c:	00 00 00 00 

0000000000001420 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    1420:	f3 0f 1e fa          	endbr64
    1424:	4d 85 c0             	test   %r8,%r8
    1427:	0f 84 53 14 00 00    	je     2880 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1460>
    142d:	55                   	push   %rbp
    142e:	48 89 f8             	mov    %rdi,%rax
    1431:	49 89 d1             	mov    %rdx,%r9
    1434:	31 ff                	xor    %edi,%edi
    1436:	48 89 e5             	mov    %rsp,%rbp
    1439:	41 57                	push   %r15
    143b:	41 56                	push   %r14
    143d:	41 55                	push   %r13
    143f:	41 54                	push   %r12
    1441:	49 89 d4             	mov    %rdx,%r12
    1444:	53                   	push   %rbx
    1445:	48 89 cb             	mov    %rcx,%rbx
    1448:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    144c:	eb 4c                	jmp    149a <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x7a>
    144e:	66 90                	xchg   %ax,%ax
    1450:	41 0f b6 51 01       	movzbl 0x1(%r9),%edx
    1455:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
    145a:	48 ff c7             	inc    %rdi
    145d:	48 83 c1 03          	add    $0x3,%rcx
    1461:	49 83 c1 03          	add    $0x3,%r9
    1465:	41 c1 e2 10          	shl    $0x10,%r10d
    1469:	c1 e2 08             	shl    $0x8,%edx
    146c:	44 09 d2             	or     %r10d,%edx
    146f:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
    1474:	44 09 d2             	or     %r10d,%edx
    1477:	0f b6 14 10          	movzbl (%rax,%rdx,1),%edx
    147b:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    147f:	41 8b 12             	mov    (%r10),%edx
    1482:	45 0f b7 12          	movzwl (%r10),%r10d
    1486:	c1 ea 10             	shr    $0x10,%edx
    1489:	66 44 89 51 fd       	mov    %r10w,-0x3(%rcx)
    148e:	88 51 ff             	mov    %dl,-0x1(%rcx)
    1491:	49 39 f8             	cmp    %rdi,%r8
    1494:	0f 84 de 13 00 00    	je     2878 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1458>
    149a:	f6 c1 3f             	test   $0x3f,%cl
    149d:	75 b1                	jne    1450 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x30>
    149f:	48 8d 57 48          	lea    0x48(%rdi),%rdx
    14a3:	49 39 d0             	cmp    %rdx,%r8
    14a6:	0f 82 d5 13 00 00    	jb     2881 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1461>
    14ac:	48 8d 0c 7f          	lea    (%rdi,%rdi,2),%rcx
    14b0:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 14b8 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x98>
    14b7:	00 
    14b8:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 14c0 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xa0>
    14bf:	00 
    14c0:	4c 89 64 24 f8       	mov    %r12,-0x8(%rsp)
    14c5:	49 8d 14 0c          	lea    (%r12,%rcx,1),%rdx
    14c9:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
    14ce:	48 01 d9             	add    %rbx,%rcx
    14d1:	eb 08                	jmp    14db <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xbb>
    14d3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    14d8:	4c 89 cf             	mov    %r9,%rdi
    14db:	4c 8d 8f 80 00 00 00 	lea    0x80(%rdi),%r9
    14e2:	4d 39 c8             	cmp    %r9,%r8
    14e5:	0f 82 c9 04 00 00    	jb     19b4 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x594>
    14eb:	44 8b 8a c0 00 00 00 	mov    0xc0(%rdx),%r9d
    14f2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    14f9:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    14fe:	44 8b 8a c3 00 00 00 	mov    0xc3(%rdx),%r9d
    1505:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    150c:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1511:	44 8b 8a c6 00 00 00 	mov    0xc6(%rdx),%r9d
    1518:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    151f:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1524:	44 8b 8a c9 00 00 00 	mov    0xc9(%rdx),%r9d
    152b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1532:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1537:	44 8b 8a cc 00 00 00 	mov    0xcc(%rdx),%r9d
    153e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1545:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    154a:	44 8b 8a cf 00 00 00 	mov    0xcf(%rdx),%r9d
    1551:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1558:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    155d:	44 8b 8a d2 00 00 00 	mov    0xd2(%rdx),%r9d
    1564:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    156b:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1570:	44 8b 8a d5 00 00 00 	mov    0xd5(%rdx),%r9d
    1577:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    157e:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1583:	44 8b 8a d8 00 00 00 	mov    0xd8(%rdx),%r9d
    158a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1591:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1596:	44 8b 8a db 00 00 00 	mov    0xdb(%rdx),%r9d
    159d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15a4:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    15a9:	44 8b 8a de 00 00 00 	mov    0xde(%rdx),%r9d
    15b0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15b7:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    15bc:	44 8b 8a e1 00 00 00 	mov    0xe1(%rdx),%r9d
    15c3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15ca:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    15cf:	44 8b 8a e4 00 00 00 	mov    0xe4(%rdx),%r9d
    15d6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15dd:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    15e2:	44 8b 8a e7 00 00 00 	mov    0xe7(%rdx),%r9d
    15e9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    15f0:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    15f5:	44 8b 8a ea 00 00 00 	mov    0xea(%rdx),%r9d
    15fc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1603:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1608:	44 8b 8a ed 00 00 00 	mov    0xed(%rdx),%r9d
    160f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1616:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    161b:	44 8b 8a f0 00 00 00 	mov    0xf0(%rdx),%r9d
    1622:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1629:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    162e:	44 8b 8a f3 00 00 00 	mov    0xf3(%rdx),%r9d
    1635:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    163c:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1641:	44 8b 8a f6 00 00 00 	mov    0xf6(%rdx),%r9d
    1648:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    164f:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1654:	44 8b 8a f9 00 00 00 	mov    0xf9(%rdx),%r9d
    165b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1662:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1667:	44 8b 8a fc 00 00 00 	mov    0xfc(%rdx),%r9d
    166e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1675:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    167a:	44 8b 8a ff 00 00 00 	mov    0xff(%rdx),%r9d
    1681:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1688:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    168d:	44 8b 8a 02 01 00 00 	mov    0x102(%rdx),%r9d
    1694:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    169b:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    16a0:	44 8b 8a 05 01 00 00 	mov    0x105(%rdx),%r9d
    16a7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16ae:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    16b3:	44 8b 8a 08 01 00 00 	mov    0x108(%rdx),%r9d
    16ba:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16c1:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    16c6:	44 8b 8a 0b 01 00 00 	mov    0x10b(%rdx),%r9d
    16cd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16d4:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    16d9:	44 8b 8a 0e 01 00 00 	mov    0x10e(%rdx),%r9d
    16e0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16e7:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    16ec:	44 8b 8a 11 01 00 00 	mov    0x111(%rdx),%r9d
    16f3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16fa:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    16ff:	44 8b 8a 14 01 00 00 	mov    0x114(%rdx),%r9d
    1706:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    170d:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1712:	44 8b 8a 17 01 00 00 	mov    0x117(%rdx),%r9d
    1719:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1720:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1725:	44 8b 8a 1a 01 00 00 	mov    0x11a(%rdx),%r9d
    172c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1733:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1738:	44 8b 8a 1d 01 00 00 	mov    0x11d(%rdx),%r9d
    173f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1746:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    174b:	44 8b 8a 20 01 00 00 	mov    0x120(%rdx),%r9d
    1752:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1759:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    175e:	44 8b 8a 23 01 00 00 	mov    0x123(%rdx),%r9d
    1765:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    176c:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1771:	44 8b 8a 26 01 00 00 	mov    0x126(%rdx),%r9d
    1778:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    177f:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1784:	44 8b 8a 29 01 00 00 	mov    0x129(%rdx),%r9d
    178b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1792:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1797:	44 8b 8a 2c 01 00 00 	mov    0x12c(%rdx),%r9d
    179e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17a5:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    17aa:	44 8b 8a 2f 01 00 00 	mov    0x12f(%rdx),%r9d
    17b1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17b8:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    17bd:	44 8b 8a 32 01 00 00 	mov    0x132(%rdx),%r9d
    17c4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17cb:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    17d0:	44 8b 8a 35 01 00 00 	mov    0x135(%rdx),%r9d
    17d7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17de:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    17e3:	44 8b 8a 38 01 00 00 	mov    0x138(%rdx),%r9d
    17ea:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    17f1:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    17f6:	44 8b 8a 3b 01 00 00 	mov    0x13b(%rdx),%r9d
    17fd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1804:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1809:	44 8b 8a 3e 01 00 00 	mov    0x13e(%rdx),%r9d
    1810:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1817:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    181c:	44 8b 8a 41 01 00 00 	mov    0x141(%rdx),%r9d
    1823:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    182a:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    182f:	44 8b 8a 44 01 00 00 	mov    0x144(%rdx),%r9d
    1836:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    183d:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1842:	44 8b 8a 47 01 00 00 	mov    0x147(%rdx),%r9d
    1849:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1850:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1855:	44 8b 8a 4a 01 00 00 	mov    0x14a(%rdx),%r9d
    185c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1863:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1868:	44 8b 8a 4d 01 00 00 	mov    0x14d(%rdx),%r9d
    186f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1876:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    187b:	44 8b 8a 50 01 00 00 	mov    0x150(%rdx),%r9d
    1882:	44 0f b7 92 7d 01 00 	movzwl 0x17d(%rdx),%r10d
    1889:	00 
    188a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1891:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1896:	44 8b 8a 53 01 00 00 	mov    0x153(%rdx),%r9d
    189d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18a4:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    18a9:	44 8b 8a 56 01 00 00 	mov    0x156(%rdx),%r9d
    18b0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18b7:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    18bc:	44 8b 8a 59 01 00 00 	mov    0x159(%rdx),%r9d
    18c3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18ca:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    18cf:	44 8b 8a 5c 01 00 00 	mov    0x15c(%rdx),%r9d
    18d6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18dd:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    18e2:	44 8b 8a 5f 01 00 00 	mov    0x15f(%rdx),%r9d
    18e9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    18f0:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    18f5:	44 8b 8a 62 01 00 00 	mov    0x162(%rdx),%r9d
    18fc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1903:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1908:	44 8b 8a 65 01 00 00 	mov    0x165(%rdx),%r9d
    190f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1916:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    191b:	44 8b 8a 68 01 00 00 	mov    0x168(%rdx),%r9d
    1922:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1929:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    192e:	44 8b 8a 6b 01 00 00 	mov    0x16b(%rdx),%r9d
    1935:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    193c:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1941:	44 8b 8a 6e 01 00 00 	mov    0x16e(%rdx),%r9d
    1948:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    194f:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1954:	44 8b 8a 71 01 00 00 	mov    0x171(%rdx),%r9d
    195b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1962:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    1967:	44 8b 8a 74 01 00 00 	mov    0x174(%rdx),%r9d
    196e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1975:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    197a:	44 8b 8a 77 01 00 00 	mov    0x177(%rdx),%r9d
    1981:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1988:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    198d:	44 8b 8a 7a 01 00 00 	mov    0x17a(%rdx),%r9d
    1994:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    199b:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    19a0:	44 0f b6 8a 7f 01 00 	movzbl 0x17f(%rdx),%r9d
    19a7:	00 
    19a8:	41 c1 e1 10          	shl    $0x10,%r9d
    19ac:	45 09 d1             	or     %r10d,%r9d
    19af:	42 0f 18 0c 08       	prefetcht0 (%rax,%r9,1)
    19b4:	44 8b 0a             	mov    (%rdx),%r9d
    19b7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19be:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    19c3:	44 8b 4a 03          	mov    0x3(%rdx),%r9d
    19c7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19ce:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
    19d4:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    19d9:	44 8b 4a 06          	mov    0x6(%rdx),%r9d
    19dd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19e4:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
    19eb:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    19f0:	44 8b 4a 09          	mov    0x9(%rdx),%r9d
    19f4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    19fb:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1a00:	44 8b 4a 0c          	mov    0xc(%rdx),%r9d
    1a04:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a0b:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1a10:	44 8b 4a 0f          	mov    0xf(%rdx),%r9d
    1a14:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a1b:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1a21:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1a26:	44 8b 4a 12          	mov    0x12(%rdx),%r9d
    1a2a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a31:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1a38:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1a3d:	44 8b 4a 15          	mov    0x15(%rdx),%r9d
    1a41:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a48:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1a4e:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1a53:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1a5a:	44 8b 4a 18          	mov    0x18(%rdx),%r9d
    1a5e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a65:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1a69:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1a6f:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1a74:	44 8b 4a 1b          	mov    0x1b(%rdx),%r9d
    1a78:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1a7f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1a86:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1a8b:	44 8b 4a 1e          	mov    0x1e(%rdx),%r9d
    1a8f:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    1a93:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    1a99:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1aa0:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    1aa5:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1aaa:	44 8b 4a 21          	mov    0x21(%rdx),%r9d
    1aae:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
    1ab3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1aba:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1abf:	44 8b 4a 24          	mov    0x24(%rdx),%r9d
    1ac3:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
    1ac9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ad0:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1ad5:	44 8b 4a 27          	mov    0x27(%rdx),%r9d
    1ad9:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
    1ae0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ae7:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1aed:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1af2:	44 8b 4a 2a          	mov    0x2a(%rdx),%r9d
    1af6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1afd:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1b04:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1b09:	44 8b 4a 2d          	mov    0x2d(%rdx),%r9d
    1b0d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1b14:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1b1a:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1b1f:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1b26:	44 8b 4a 30          	mov    0x30(%rdx),%r9d
    1b2a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1b31:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1b35:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1b3b:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1b40:	44 8b 4a 33          	mov    0x33(%rdx),%r9d
    1b44:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1b4b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1b52:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1b57:	44 8b 4a 36          	mov    0x36(%rdx),%r9d
    1b5b:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    1b5f:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    1b65:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1b6c:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1b71:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1b76:	44 8b 4a 39          	mov    0x39(%rdx),%r9d
    1b7a:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    1b7f:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    1b83:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1b89:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1b90:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    1b96:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1b9b:	44 8b 4a 3c          	mov    0x3c(%rdx),%r9d
    1b9f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ba6:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1bab:	44 8b 4a 3f          	mov    0x3f(%rdx),%r9d
    1baf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1bb6:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1bbb:	44 8b 4a 42          	mov    0x42(%rdx),%r9d
    1bbf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1bc6:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1bcb:	44 8b 4a 45          	mov    0x45(%rdx),%r9d
    1bcf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1bd6:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1bdb:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1be1:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    1be7:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1bed:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1bf4:	44 8b 4a 48          	mov    0x48(%rdx),%r9d
    1bf8:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    1bff:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1c06:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1c0d:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1c12:	44 8b 4a 4b          	mov    0x4b(%rdx),%r9d
    1c16:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1c1a:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1c20:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1c27:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
    1c2d:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1c32:	44 8b 4a 4e          	mov    0x4e(%rdx),%r9d
    1c36:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1c3d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1c44:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
    1c4b:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1c50:	44 8b 4a 51          	mov    0x51(%rdx),%r9d
    1c54:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    1c58:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    1c5e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1c65:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1c6a:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1c6f:	44 8b 4a 54          	mov    0x54(%rdx),%r9d
    1c73:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1c78:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    1c7c:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1c82:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1c89:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    1c8f:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1c94:	44 8b 4a 57          	mov    0x57(%rdx),%r9d
    1c98:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1c9f:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1ca5:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1caa:	44 8b 4a 5a          	mov    0x5a(%rdx),%r9d
    1cae:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1cb5:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1cbc:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1cc1:	44 8b 4a 5d          	mov    0x5d(%rdx),%r9d
    1cc5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ccc:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1cd2:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1cd7:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1cde:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1ce2:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1ce8:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1cef:	44 8b 4a 60          	mov    0x60(%rdx),%r9d
    1cf3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1cfa:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    1cfe:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1d03:	44 8b 4a 63          	mov    0x63(%rdx),%r9d
    1d07:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    1d0d:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    1d12:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d19:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
    1d1f:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    1d24:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1d29:	44 8b 4a 66          	mov    0x66(%rdx),%r9d
    1d2d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d34:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
    1d3b:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1d40:	44 8b 4a 69          	mov    0x69(%rdx),%r9d
    1d44:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d4b:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1d50:	44 8b 4a 6c          	mov    0x6c(%rdx),%r9d
    1d54:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d5b:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1d60:	44 8b 4a 6f          	mov    0x6f(%rdx),%r9d
    1d64:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d6b:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1d71:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1d76:	44 8b 4a 72          	mov    0x72(%rdx),%r9d
    1d7a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d81:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1d88:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1d8d:	44 8b 4a 75          	mov    0x75(%rdx),%r9d
    1d91:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1d98:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    1d9e:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1da3:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
    1daa:	44 8b 4a 78          	mov    0x78(%rdx),%r9d
    1dae:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1db5:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1db9:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1dbf:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1dc4:	44 8b 4a 7b          	mov    0x7b(%rdx),%r9d
    1dc8:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1dcf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1dd6:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1ddb:	44 8b 4a 7e          	mov    0x7e(%rdx),%r9d
    1ddf:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    1de3:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    1de9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1df0:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    1df5:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1dfa:	44 8b 8a 81 00 00 00 	mov    0x81(%rdx),%r9d
    1e01:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    1e06:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1e0d:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1e12:	44 8b 8a 84 00 00 00 	mov    0x84(%rdx),%r9d
    1e19:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    1e1f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1e26:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1e2b:	44 8b 8a 87 00 00 00 	mov    0x87(%rdx),%r9d
    1e32:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    1e39:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1e40:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1e46:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1e4b:	44 8b 8a 8a 00 00 00 	mov    0x8a(%rdx),%r9d
    1e52:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1e59:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1e60:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1e65:	44 8b 8a 8d 00 00 00 	mov    0x8d(%rdx),%r9d
    1e6c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1e73:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1e79:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1e7e:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    1e85:	44 8b 8a 90 00 00 00 	mov    0x90(%rdx),%r9d
    1e8c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1e93:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1e97:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1e9d:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1ea2:	44 8b 8a 93 00 00 00 	mov    0x93(%rdx),%r9d
    1ea9:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1eb0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1eb7:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1ebc:	44 8b 8a 96 00 00 00 	mov    0x96(%rdx),%r9d
    1ec3:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1ec7:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1ecd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ed4:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1ed9:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1ede:	44 8b 8a 99 00 00 00 	mov    0x99(%rdx),%r9d
    1ee5:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1eea:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ef1:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1ef6:	44 8b 8a 9c 00 00 00 	mov    0x9c(%rdx),%r9d
    1efd:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1f04:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    1f09:	44 8b 8a 9f 00 00 00 	mov    0x9f(%rdx),%r9d
    1f10:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1f17:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    1f1c:	44 8b 8a a2 00 00 00 	mov    0xa2(%rdx),%r9d
    1f23:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1f2a:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    1f2f:	44 8b 8a a5 00 00 00 	mov    0xa5(%rdx),%r9d
    1f36:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1f3d:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    1f42:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    1f48:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1f4e:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    1f54:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    1f5b:	44 8b 8a a8 00 00 00 	mov    0xa8(%rdx),%r9d
    1f62:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    1f69:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1f70:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1f77:	46 0f b6 1c 08       	movzbl (%rax,%r9,1),%r11d
    1f7c:	44 8b 8a ab 00 00 00 	mov    0xab(%rdx),%r9d
    1f83:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    1f88:	c4 21 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm10
    1f8e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1f95:	46 0f b6 14 08       	movzbl (%rax,%r9,1),%r10d
    1f9a:	44 8b 8a ae 00 00 00 	mov    0xae(%rdx),%r9d
    1fa1:	c4 63 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm10,%xmm10
    1fa8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1faf:	46 0f b6 24 08       	movzbl (%rax,%r9,1),%r12d
    1fb4:	44 8b 8a b1 00 00 00 	mov    0xb1(%rdx),%r9d
    1fbb:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1fc0:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1fc6:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1fcc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1fd3:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    1fd8:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    1fdd:	44 8b 8a b4 00 00 00 	mov    0xb4(%rdx),%r9d
    1fe4:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1fe9:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1ff0:	4c 8d 97 88 00 00 00 	lea    0x88(%rdi),%r10
    1ff7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1ffe:	46 0f b6 34 08       	movzbl (%rax,%r9,1),%r14d
    2003:	44 8b 8a b7 00 00 00 	mov    0xb7(%rdx),%r9d
    200a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    2011:	c4 21 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm10
    2017:	46 0f b6 2c 08       	movzbl (%rax,%r9,1),%r13d
    201c:	44 8b 8a ba 00 00 00 	mov    0xba(%rdx),%r9d
    2023:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    202a:	c4 23 29 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm10,%xmm10
    2031:	46 0f b6 3c 08       	movzbl (%rax,%r9,1),%r15d
    2036:	44 8b 8a bd 00 00 00 	mov    0xbd(%rdx),%r9d
    203d:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    2044:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    204a:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    2051:	48 81 c1 c0 00 00 00 	add    $0xc0,%rcx
    2058:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    205d:	c4 23 21 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm11,%xmm11
    2064:	4c 8d 4f 40          	lea    0x40(%rdi),%r9
    2068:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    206d:	c4 21 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm11
    2073:	c4 63 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm11,%xmm11
    207a:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    207f:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    2084:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    208a:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    2090:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    2095:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    209b:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    20a1:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    20a6:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    20ab:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    20b0:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    20b5:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    20bb:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    20c1:	c5 7d e7 89 40 ff ff 	vmovntdq %ymm9,-0xc0(%rcx)
    20c8:	ff 
    20c9:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    20cd:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    20d1:	c5 fd e7 b1 60 ff ff 	vmovntdq %ymm6,-0xa0(%rcx)
    20d8:	ff 
    20d9:	c5 fd e7 69 80       	vmovntdq %ymm5,-0x80(%rcx)
    20de:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    20e2:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    20e6:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    20ec:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    20f2:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    20f8:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    20fe:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    2103:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    2107:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    210d:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    2113:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    2119:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    211f:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    2125:	c5 fd e7 69 a0       	vmovntdq %ymm5,-0x60(%rcx)
    212a:	c5 fd e7 41 c0       	vmovntdq %ymm0,-0x40(%rcx)
    212f:	c5 fd e7 49 e0       	vmovntdq %ymm1,-0x20(%rcx)
    2134:	4d 39 d0             	cmp    %r10,%r8
    2137:	0f 83 9b f3 ff ff    	jae    14d8 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xb8>
    213d:	4c 8b 64 24 f8       	mov    -0x8(%rsp),%r12
    2142:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
    2147:	48 8d 57 68          	lea    0x68(%rdi),%rdx
    214b:	0f ae f8             	sfence
    214e:	49 39 d0             	cmp    %rdx,%r8
    2151:	0f 82 91 03 00 00    	jb     24e8 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c8>
    2157:	4b 8d 0c 49          	lea    (%r9,%r9,2),%rcx
    215b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2163 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd43>
    2162:	00 
    2163:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 216b <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd4b>
    216a:	00 
    216b:	4c 89 64 24 f8       	mov    %r12,-0x8(%rsp)
    2170:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
    2175:	49 8d 14 0c          	lea    (%r12,%rcx,1),%rdx
    2179:	48 01 d9             	add    %rbx,%rcx
    217c:	0f 1f 40 00          	nopl   0x0(%rax)
    2180:	8b 7a 48             	mov    0x48(%rdx),%edi
    2183:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2189:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    218e:	8b 7a 4b             	mov    0x4b(%rdx),%edi
    2191:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2197:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    219d:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    21a2:	8b 7a 4e             	mov    0x4e(%rdx),%edi
    21a5:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    21ab:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    21b2:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    21b7:	8b 7a 51             	mov    0x51(%rdx),%edi
    21ba:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    21c0:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    21c4:	8b 7a 54             	mov    0x54(%rdx),%edi
    21c7:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    21cd:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    21d2:	8b 7a 57             	mov    0x57(%rdx),%edi
    21d5:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    21db:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    21e1:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    21e6:	8b 7a 5a             	mov    0x5a(%rdx),%edi
    21e9:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    21ef:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    21f6:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    21fb:	8b 7a 5d             	mov    0x5d(%rdx),%edi
    21fe:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2204:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    220a:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    220e:	c4 e3 71 22 0c be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm1,%xmm1
    2215:	8b 7a 30             	mov    0x30(%rdx),%edi
    2218:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    221e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    2222:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    2228:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    222d:	8b 7a 33             	mov    0x33(%rdx),%edi
    2230:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    2237:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    223d:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    2242:	8b 7a 36             	mov    0x36(%rdx),%edi
    2245:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    2249:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    224f:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2255:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    225a:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    225f:	8b 7a 39             	mov    0x39(%rdx),%edi
    2262:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    2267:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    226d:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    2271:	8b 7a 3c             	mov    0x3c(%rdx),%edi
    2274:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    227a:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2280:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    2285:	8b 7a 3f             	mov    0x3f(%rdx),%edi
    2288:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    228f:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2295:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    229b:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    22a0:	8b 7a 42             	mov    0x42(%rdx),%edi
    22a3:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    22a9:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    22b0:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    22b5:	8b 7a 45             	mov    0x45(%rdx),%edi
    22b8:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    22be:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    22c4:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    22c8:	c4 e3 69 22 14 be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm2,%xmm2
    22cf:	8b 7a 18             	mov    0x18(%rdx),%edi
    22d2:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    22d8:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    22dc:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    22e2:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    22e7:	8b 7a 1b             	mov    0x1b(%rdx),%edi
    22ea:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    22f1:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    22f7:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    22fc:	8b 7a 1e             	mov    0x1e(%rdx),%edi
    22ff:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    2303:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    2309:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    230f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    2314:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    2319:	8b 7a 21             	mov    0x21(%rdx),%edi
    231c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    2321:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    2325:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    232b:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2331:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    2335:	8b 7a 24             	mov    0x24(%rdx),%edi
    2338:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    233e:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    2343:	8b 7a 27             	mov    0x27(%rdx),%edi
    2346:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    234c:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    2351:	8b 7a 2a             	mov    0x2a(%rdx),%edi
    2354:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    235a:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    235f:	8b 7a 2d             	mov    0x2d(%rdx),%edi
    2362:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2368:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    236c:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    2372:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    2378:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    237e:	c4 e3 49 22 34 be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm6,%xmm6
    2385:	8b 3a                	mov    (%rdx),%edi
    2387:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    238e:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    2395:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    239b:	44 0f b6 1c 38       	movzbl (%rax,%rdi,1),%r11d
    23a0:	8b 7a 03             	mov    0x3(%rdx),%edi
    23a3:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    23a7:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    23ad:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    23b3:	44 0f b6 14 38       	movzbl (%rax,%rdi,1),%r10d
    23b8:	8b 7a 06             	mov    0x6(%rdx),%edi
    23bb:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    23c2:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    23c8:	44 0f b6 24 38       	movzbl (%rax,%rdi,1),%r12d
    23cd:	8b 7a 09             	mov    0x9(%rdx),%edi
    23d0:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    23d4:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    23da:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    23e0:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    23e6:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    23eb:	0f b6 1c 38          	movzbl (%rax,%rdi,1),%ebx
    23ef:	8b 7a 0c             	mov    0xc(%rdx),%edi
    23f2:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    23f7:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    23fe:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    2402:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    2408:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    240e:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    2414:	44 0f b6 34 38       	movzbl (%rax,%rdi,1),%r14d
    2419:	8b 7a 0f             	mov    0xf(%rdx),%edi
    241c:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    2422:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2428:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    242e:	44 0f b6 2c 38       	movzbl (%rax,%rdi,1),%r13d
    2433:	8b 7a 12             	mov    0x12(%rdx),%edi
    2436:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    243c:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    2443:	44 0f b6 3c 38       	movzbl (%rax,%rdi,1),%r15d
    2448:	8b 7a 15             	mov    0x15(%rdx),%edi
    244b:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2451:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    2457:	0f b6 3c 38          	movzbl (%rax,%rdi,1),%edi
    245b:	c4 e3 41 22 3c be 01 	vpinsrd $0x1,(%rsi,%rdi,4),%xmm7,%xmm7
    2462:	49 8d 79 48          	lea    0x48(%r9),%rdi
    2466:	49 83 c1 20          	add    $0x20,%r9
    246a:	48 83 c2 60          	add    $0x60,%rdx
    246e:	48 83 c1 60          	add    $0x60,%rcx
    2472:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    2476:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    247c:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    2483:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    2487:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    248b:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    2491:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    2497:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    249d:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    24a1:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    24a6:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    24ac:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    24b1:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    24b5:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    24bb:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    24c0:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    24c6:	c5 fe 7f 51 a0       	vmovdqu %ymm2,-0x60(%rcx)
    24cb:	c5 fe 7f 49 c0       	vmovdqu %ymm1,-0x40(%rcx)
    24d0:	c5 fe 7f 41 e0       	vmovdqu %ymm0,-0x20(%rcx)
    24d5:	49 39 f8             	cmp    %rdi,%r8
    24d8:	0f 83 a2 fc ff ff    	jae    2180 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd60>
    24de:	4c 8b 64 24 f8       	mov    -0x8(%rsp),%r12
    24e3:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
    24e8:	4d 8d 59 08          	lea    0x8(%r9),%r11
    24ec:	4d 39 d8             	cmp    %r11,%r8
    24ef:	0f 82 4d 01 00 00    	jb     2642 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1222>
    24f5:	4c 89 64 24 f8       	mov    %r12,-0x8(%rsp)
    24fa:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    24fe:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2506 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10e6>
    2505:	00 
    2506:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
    250b:	4b 8d 3c 14          	lea    (%r12,%r10,1),%rdi
    250f:	49 01 da             	add    %rbx,%r10
    2512:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    2518:	4c 8b 27             	mov    (%rdi),%r12
    251b:	48 8b 57 08          	mov    0x8(%rdi),%rdx
    251f:	49 83 c2 18          	add    $0x18,%r10
    2523:	48 83 c7 18          	add    $0x18,%rdi
    2527:	48 8b 4f f8          	mov    -0x8(%rdi),%rcx
    252b:	4d 89 e1             	mov    %r12,%r9
    252e:	4d 89 e5             	mov    %r12,%r13
    2531:	49 89 d6             	mov    %rdx,%r14
    2534:	49 c1 ed 30          	shr    $0x30,%r13
    2538:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    253f:	41 89 cf             	mov    %ecx,%r15d
    2542:	49 c1 ee 20          	shr    $0x20,%r14
    2546:	42 0f b6 1c 08       	movzbl (%rax,%r9,1),%ebx
    254b:	4d 89 e1             	mov    %r12,%r9
    254e:	41 89 d4             	mov    %edx,%r12d
    2551:	41 c1 e7 08          	shl    $0x8,%r15d
    2555:	41 c1 e4 10          	shl    $0x10,%r12d
    2559:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    2560:	49 c1 e9 18          	shr    $0x18,%r9
    2564:	45 09 ec             	or     %r13d,%r12d
    2567:	46 0f b6 34 30       	movzbl (%rax,%r14,1),%r14d
    256c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    2573:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    2578:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    257f:	46 0f b6 0c 08       	movzbl (%rax,%r9,1),%r9d
    2584:	46 0f b6 2c 20       	movzbl (%rax,%r12,1),%r13d
    2589:	41 89 d4             	mov    %edx,%r12d
    258c:	48 c1 ea 38          	shr    $0x38,%rdx
    2590:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    2596:	41 09 d7             	or     %edx,%r15d
    2599:	41 c1 ec 08          	shr    $0x8,%r12d
    259d:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    25a4:	4d 89 d9             	mov    %r11,%r9
    25a7:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    25ae:	46 0f b6 24 20       	movzbl (%rax,%r12,1),%r12d
    25b3:	49 83 c3 08          	add    $0x8,%r11
    25b7:	42 0f b6 14 38       	movzbl (%rax,%r15,1),%edx
    25bc:	49 89 cf             	mov    %rcx,%r15
    25bf:	48 c1 e9 28          	shr    $0x28,%rcx
    25c3:	49 c1 ef 10          	shr    $0x10,%r15
    25c7:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    25cb:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    25d2:	c4 e3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm1,%xmm1
    25d9:	46 0f b6 3c 38       	movzbl (%rax,%r15,1),%r15d
    25de:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    25e4:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    25eb:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    25ef:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    25f5:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    25fc:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    2600:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    2606:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    260b:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    260f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    2615:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    261a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    261f:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    2623:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    2629:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    262f:	4d 39 d8             	cmp    %r11,%r8
    2632:	0f 83 e0 fe ff ff    	jae    2518 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10f8>
    2638:	4c 8b 64 24 f8       	mov    -0x8(%rsp),%r12
    263d:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
    2642:	4d 39 c1             	cmp    %r8,%r9
    2645:	0f 83 15 02 00 00    	jae    2860 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1440>
    264b:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    264f:	4d 8d 14 14          	lea    (%r12,%rdx,1),%r10
    2653:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    2658:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    265d:	45 0f b6 12          	movzbl (%r10),%r10d
    2661:	c1 e1 08             	shl    $0x8,%ecx
    2664:	41 c1 e3 10          	shl    $0x10,%r11d
    2668:	44 09 d9             	or     %r11d,%ecx
    266b:	44 09 d1             	or     %r10d,%ecx
    266e:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    2672:	4c 8d 14 8e          	lea    (%rsi,%rcx,4),%r10
    2676:	41 8b 0a             	mov    (%r10),%ecx
    2679:	45 0f b7 12          	movzwl (%r10),%r10d
    267d:	c1 e9 10             	shr    $0x10,%ecx
    2680:	66 44 89 14 13       	mov    %r10w,(%rbx,%rdx,1)
    2685:	88 4c 13 02          	mov    %cl,0x2(%rbx,%rdx,1)
    2689:	49 8d 49 01          	lea    0x1(%r9),%rcx
    268d:	4c 39 c1             	cmp    %r8,%rcx
    2690:	0f 83 ca 01 00 00    	jae    2860 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1440>
    2696:	4d 8d 54 14 03       	lea    0x3(%r12,%rdx,1),%r10
    269b:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    26a0:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    26a5:	45 0f b6 12          	movzbl (%r10),%r10d
    26a9:	41 c1 e3 10          	shl    $0x10,%r11d
    26ad:	c1 e1 08             	shl    $0x8,%ecx
    26b0:	44 09 d9             	or     %r11d,%ecx
    26b3:	44 09 d1             	or     %r10d,%ecx
    26b6:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    26ba:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    26be:	44 8b 11             	mov    (%rcx),%r10d
    26c1:	44 0f b7 19          	movzwl (%rcx),%r11d
    26c5:	49 8d 49 02          	lea    0x2(%r9),%rcx
    26c9:	44 89 d7             	mov    %r10d,%edi
    26cc:	66 44 89 5c 13 03    	mov    %r11w,0x3(%rbx,%rdx,1)
    26d2:	c1 ef 10             	shr    $0x10,%edi
    26d5:	40 88 7c 13 05       	mov    %dil,0x5(%rbx,%rdx,1)
    26da:	4c 39 c1             	cmp    %r8,%rcx
    26dd:	0f 83 7d 01 00 00    	jae    2860 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1440>
    26e3:	4d 8d 54 14 06       	lea    0x6(%r12,%rdx,1),%r10
    26e8:	41 0f b6 4a 01       	movzbl 0x1(%r10),%ecx
    26ed:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    26f2:	45 0f b6 12          	movzbl (%r10),%r10d
    26f6:	41 c1 e3 10          	shl    $0x10,%r11d
    26fa:	c1 e1 08             	shl    $0x8,%ecx
    26fd:	44 09 d9             	or     %r11d,%ecx
    2700:	44 09 d1             	or     %r10d,%ecx
    2703:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    2707:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    270b:	44 8b 11             	mov    (%rcx),%r10d
    270e:	44 0f b7 19          	movzwl (%rcx),%r11d
    2712:	49 8d 49 03          	lea    0x3(%r9),%rcx
    2716:	44 89 d7             	mov    %r10d,%edi
    2719:	66 44 89 5c 13 06    	mov    %r11w,0x6(%rbx,%rdx,1)
    271f:	c1 ef 10             	shr    $0x10,%edi
    2722:	40 88 7c 13 08       	mov    %dil,0x8(%rbx,%rdx,1)
    2727:	4c 39 c1             	cmp    %r8,%rcx
    272a:	0f 83 30 01 00 00    	jae    2860 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1440>
    2730:	4d 8d 54 14 09       	lea    0x9(%r12,%rdx,1),%r10
    2735:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    273a:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    273f:	45 0f b6 12          	movzbl (%r10),%r10d
    2743:	41 c1 e3 08          	shl    $0x8,%r11d
    2747:	c1 e1 10             	shl    $0x10,%ecx
    274a:	44 09 d9             	or     %r11d,%ecx
    274d:	44 09 d1             	or     %r10d,%ecx
    2750:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    2754:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    2758:	44 8b 11             	mov    (%rcx),%r10d
    275b:	44 0f b7 19          	movzwl (%rcx),%r11d
    275f:	49 8d 49 04          	lea    0x4(%r9),%rcx
    2763:	44 89 d7             	mov    %r10d,%edi
    2766:	66 44 89 5c 13 09    	mov    %r11w,0x9(%rbx,%rdx,1)
    276c:	c1 ef 10             	shr    $0x10,%edi
    276f:	40 88 7c 13 0b       	mov    %dil,0xb(%rbx,%rdx,1)
    2774:	4c 39 c1             	cmp    %r8,%rcx
    2777:	0f 83 e3 00 00 00    	jae    2860 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1440>
    277d:	4d 8d 54 14 0c       	lea    0xc(%r12,%rdx,1),%r10
    2782:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    2787:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    278c:	45 0f b6 12          	movzbl (%r10),%r10d
    2790:	41 c1 e3 08          	shl    $0x8,%r11d
    2794:	c1 e1 10             	shl    $0x10,%ecx
    2797:	44 09 d9             	or     %r11d,%ecx
    279a:	44 09 d1             	or     %r10d,%ecx
    279d:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    27a1:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    27a5:	44 8b 11             	mov    (%rcx),%r10d
    27a8:	44 0f b7 19          	movzwl (%rcx),%r11d
    27ac:	49 8d 49 05          	lea    0x5(%r9),%rcx
    27b0:	44 89 d7             	mov    %r10d,%edi
    27b3:	66 44 89 5c 13 0c    	mov    %r11w,0xc(%rbx,%rdx,1)
    27b9:	c1 ef 10             	shr    $0x10,%edi
    27bc:	40 88 7c 13 0e       	mov    %dil,0xe(%rbx,%rdx,1)
    27c1:	4c 39 c1             	cmp    %r8,%rcx
    27c4:	0f 83 96 00 00 00    	jae    2860 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1440>
    27ca:	4d 8d 54 14 0f       	lea    0xf(%r12,%rdx,1),%r10
    27cf:	49 83 c1 06          	add    $0x6,%r9
    27d3:	41 0f b6 4a 02       	movzbl 0x2(%r10),%ecx
    27d8:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    27dd:	45 0f b6 12          	movzbl (%r10),%r10d
    27e1:	41 c1 e3 08          	shl    $0x8,%r11d
    27e5:	c1 e1 10             	shl    $0x10,%ecx
    27e8:	44 09 d9             	or     %r11d,%ecx
    27eb:	44 09 d1             	or     %r10d,%ecx
    27ee:	0f b6 0c 08          	movzbl (%rax,%rcx,1),%ecx
    27f2:	48 8d 0c 8e          	lea    (%rsi,%rcx,4),%rcx
    27f6:	44 8b 11             	mov    (%rcx),%r10d
    27f9:	44 0f b7 19          	movzwl (%rcx),%r11d
    27fd:	44 89 d7             	mov    %r10d,%edi
    2800:	66 44 89 5c 13 0f    	mov    %r11w,0xf(%rbx,%rdx,1)
    2806:	c1 ef 10             	shr    $0x10,%edi
    2809:	40 88 7c 13 11       	mov    %dil,0x11(%rbx,%rdx,1)
    280e:	4d 39 c1             	cmp    %r8,%r9
    2811:	73 4d                	jae    2860 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1440>
    2813:	49 8d 4c 14 12       	lea    0x12(%r12,%rdx,1),%rcx
    2818:	4c 8d 44 13 12       	lea    0x12(%rbx,%rdx,1),%r8
    281d:	0f b6 79 02          	movzbl 0x2(%rcx),%edi
    2821:	0f b6 51 01          	movzbl 0x1(%rcx),%edx
    2825:	0f b6 09             	movzbl (%rcx),%ecx
    2828:	c1 e2 08             	shl    $0x8,%edx
    282b:	c1 e7 10             	shl    $0x10,%edi
    282e:	09 fa                	or     %edi,%edx
    2830:	09 ca                	or     %ecx,%edx
    2832:	0f b6 04 10          	movzbl (%rax,%rdx,1),%eax
    2836:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    283a:	8b 02                	mov    (%rdx),%eax
    283c:	0f b7 12             	movzwl (%rdx),%edx
    283f:	c1 e8 10             	shr    $0x10,%eax
    2842:	66 41 89 10          	mov    %dx,(%r8)
    2846:	41 88 40 02          	mov    %al,0x2(%r8)
    284a:	c5 f8 77             	vzeroupper
    284d:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2851:	5b                   	pop    %rbx
    2852:	41 5c                	pop    %r12
    2854:	41 5d                	pop    %r13
    2856:	41 5e                	pop    %r14
    2858:	41 5f                	pop    %r15
    285a:	5d                   	pop    %rbp
    285b:	c3                   	ret
    285c:	0f 1f 40 00          	nopl   0x0(%rax)
    2860:	c5 f8 77             	vzeroupper
    2863:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    2867:	5b                   	pop    %rbx
    2868:	41 5c                	pop    %r12
    286a:	41 5d                	pop    %r13
    286c:	41 5e                	pop    %r14
    286e:	41 5f                	pop    %r15
    2870:	5d                   	pop    %rbp
    2871:	c3                   	ret
    2872:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    2878:	4d 89 c1             	mov    %r8,%r9
    287b:	e9 68 fc ff ff       	jmp    24e8 <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x10c8>
    2880:	c3                   	ret
    2881:	48 8d 57 28          	lea    0x28(%rdi),%rdx
    2885:	49 89 f9             	mov    %rdi,%r9
    2888:	e9 c1 f8 ff ff       	jmp    214e <jshc_channel::avx2_chain_tablehint_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd2e>
