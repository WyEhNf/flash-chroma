
artifacts/skylake-overlap16-linux-build-v1/CMakeFiles/jshc_skylake_overlap16.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 53 09 00 00    	je     960 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x960>
       d:	41 57                	push   %r15
       f:	b8 00 04 00 00       	mov    $0x400,%eax
      14:	49 89 c9             	mov    %rcx,%r9
      17:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
      1b:	48 39 c1             	cmp    %rax,%rcx
      1e:	49 89 d2             	mov    %rdx,%r10
      21:	48 0f 47 c8          	cmova  %rax,%rcx
      25:	31 c0                	xor    %eax,%eax
      27:	41 56                	push   %r14
      29:	41 55                	push   %r13
      2b:	41 54                	push   %r12
      2d:	55                   	push   %rbp
      2e:	53                   	push   %rbx
      2f:	0f b6 12             	movzbl (%rdx),%edx
      32:	0f 1f 00             	nopl   (%rax)
      35:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
      3c:	00 00 00 00 
      40:	41 0f 18 04 02       	prefetchnta (%r10,%rax,1)
      45:	48 83 c0 40          	add    $0x40,%rax
      49:	48 39 c8             	cmp    %rcx,%rax
      4c:	72 f2                	jb     40 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x40>
      4e:	49 83 f9 40          	cmp    $0x40,%r9
      52:	0f 86 10 09 00 00    	jbe    968 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x968>
      58:	49 8d 59 bf          	lea    -0x41(%r9),%rbx
      5c:	49 8d 82 40 04 00 00 	lea    0x440(%r10),%rax
      63:	41 b8 96 01 00 00    	mov    $0x196,%r8d
      69:	89 d5                	mov    %edx,%ebp
      6b:	48 83 e3 c0          	and    $0xffffffffffffffc0,%rbx
      6f:	4c 8d 9b d6 01 00 00 	lea    0x1d6(%rbx),%r11
      76:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
      7d:	00 00 00 
      80:	4d 39 c1             	cmp    %r8,%r9
      83:	72 0f                	jb     94 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x94>
      85:	0f 18 40 c0          	prefetchnta -0x40(%rax)
      89:	0f 18 00             	prefetchnta (%rax)
      8c:	0f 18 40 40          	prefetchnta 0x40(%rax)
      90:	0f 18 40 7f          	prefetchnta 0x7f(%rax)
      94:	0f b7 90 c1 fb ff ff 	movzwl -0x43f(%rax),%edx
      9b:	40 0f b6 ed          	movzbl %bpl,%ebp
      9f:	8b 88 c9 fb ff ff    	mov    -0x437(%rax),%ecx
      a5:	c1 e2 08             	shl    $0x8,%edx
      a8:	09 ea                	or     %ebp,%edx
      aa:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      ae:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
      b1:	8b 90 c3 fb ff ff    	mov    -0x43d(%rax),%edx
      b7:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
      bd:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      c1:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
      c5:	8b 90 c6 fb ff ff    	mov    -0x43a(%rax),%edx
      cb:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
      d1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      d5:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
      d9:	89 ca                	mov    %ecx,%edx
      db:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
      e1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      e5:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
      e8:	89 a8 c0 fb ff ff    	mov    %ebp,-0x440(%rax)
      ee:	0f b7 a8 cd fb ff ff 	movzwl -0x433(%rax),%ebp
      f5:	44 89 a8 c3 fb ff ff 	mov    %r13d,-0x43d(%rax)
      fc:	44 89 a0 c6 fb ff ff 	mov    %r12d,-0x43a(%rax)
     103:	89 90 c9 fb ff ff    	mov    %edx,-0x437(%rax)
     109:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     10d:	8b 90 d5 fb ff ff    	mov    -0x42b(%rax),%edx
     113:	89 c9                	mov    %ecx,%ecx
     115:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     119:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     11c:	8b 88 cf fb ff ff    	mov    -0x431(%rax),%ecx
     122:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     128:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     12c:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     130:	8b 88 d2 fb ff ff    	mov    -0x42e(%rax),%ecx
     136:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     13c:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     140:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     144:	89 d1                	mov    %edx,%ecx
     146:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     14c:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     150:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     153:	89 a8 cc fb ff ff    	mov    %ebp,-0x434(%rax)
     159:	44 89 a8 cf fb ff ff 	mov    %r13d,-0x431(%rax)
     160:	44 89 a0 d2 fb ff ff 	mov    %r12d,-0x42e(%rax)
     167:	89 88 d5 fb ff ff    	mov    %ecx,-0x42b(%rax)
     16d:	8b 88 e1 fb ff ff    	mov    -0x41f(%rax),%ecx
     173:	0f b7 a8 d9 fb ff ff 	movzwl -0x427(%rax),%ebp
     17a:	0f ac ea 18          	shrd   $0x18,%ebp,%edx
     17e:	89 d2                	mov    %edx,%edx
     180:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     184:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     187:	8b 90 db fb ff ff    	mov    -0x425(%rax),%edx
     18d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     193:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     197:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     19b:	8b 90 de fb ff ff    	mov    -0x422(%rax),%edx
     1a1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     1a7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     1ab:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     1af:	89 ca                	mov    %ecx,%edx
     1b1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     1b7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     1bb:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     1be:	89 a8 d8 fb ff ff    	mov    %ebp,-0x428(%rax)
     1c4:	0f b7 a8 e5 fb ff ff 	movzwl -0x41b(%rax),%ebp
     1cb:	44 89 a8 db fb ff ff 	mov    %r13d,-0x425(%rax)
     1d2:	44 89 a0 de fb ff ff 	mov    %r12d,-0x422(%rax)
     1d9:	89 90 e1 fb ff ff    	mov    %edx,-0x41f(%rax)
     1df:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     1e3:	8b 90 ed fb ff ff    	mov    -0x413(%rax),%edx
     1e9:	89 c9                	mov    %ecx,%ecx
     1eb:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     1ef:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     1f2:	8b 88 e7 fb ff ff    	mov    -0x419(%rax),%ecx
     1f8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     1fe:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     202:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     206:	8b 88 ea fb ff ff    	mov    -0x416(%rax),%ecx
     20c:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     212:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     216:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     21a:	89 d1                	mov    %edx,%ecx
     21c:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     222:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     226:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     229:	89 a8 e4 fb ff ff    	mov    %ebp,-0x41c(%rax)
     22f:	44 89 a8 e7 fb ff ff 	mov    %r13d,-0x419(%rax)
     236:	44 89 a0 ea fb ff ff 	mov    %r12d,-0x416(%rax)
     23d:	89 88 ed fb ff ff    	mov    %ecx,-0x413(%rax)
     243:	8b 88 f9 fb ff ff    	mov    -0x407(%rax),%ecx
     249:	0f b7 a8 f1 fb ff ff 	movzwl -0x40f(%rax),%ebp
     250:	0f ac ea 18          	shrd   $0x18,%ebp,%edx
     254:	89 d2                	mov    %edx,%edx
     256:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     25a:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     25d:	8b 90 f3 fb ff ff    	mov    -0x40d(%rax),%edx
     263:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     269:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     26d:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     271:	8b 90 f6 fb ff ff    	mov    -0x40a(%rax),%edx
     277:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     27d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     281:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     285:	89 ca                	mov    %ecx,%edx
     287:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     28d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     291:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     294:	89 a8 f0 fb ff ff    	mov    %ebp,-0x410(%rax)
     29a:	0f b7 a8 fd fb ff ff 	movzwl -0x403(%rax),%ebp
     2a1:	44 89 a8 f3 fb ff ff 	mov    %r13d,-0x40d(%rax)
     2a8:	44 89 a0 f6 fb ff ff 	mov    %r12d,-0x40a(%rax)
     2af:	89 90 f9 fb ff ff    	mov    %edx,-0x407(%rax)
     2b5:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     2b9:	8b 90 05 fc ff ff    	mov    -0x3fb(%rax),%edx
     2bf:	89 c9                	mov    %ecx,%ecx
     2c1:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     2c5:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     2c8:	8b 88 ff fb ff ff    	mov    -0x401(%rax),%ecx
     2ce:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     2d4:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     2d8:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     2dc:	8b 88 02 fc ff ff    	mov    -0x3fe(%rax),%ecx
     2e2:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     2e8:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     2ec:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     2f0:	89 d1                	mov    %edx,%ecx
     2f2:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     2f8:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     2fc:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     2ff:	89 a8 fc fb ff ff    	mov    %ebp,-0x404(%rax)
     305:	44 89 a8 ff fb ff ff 	mov    %r13d,-0x401(%rax)
     30c:	44 89 a0 02 fc ff ff 	mov    %r12d,-0x3fe(%rax)
     313:	89 88 05 fc ff ff    	mov    %ecx,-0x3fb(%rax)
     319:	8b 88 11 fc ff ff    	mov    -0x3ef(%rax),%ecx
     31f:	0f b7 a8 09 fc ff ff 	movzwl -0x3f7(%rax),%ebp
     326:	0f ac ea 18          	shrd   $0x18,%ebp,%edx
     32a:	89 d2                	mov    %edx,%edx
     32c:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     330:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     333:	8b 90 0b fc ff ff    	mov    -0x3f5(%rax),%edx
     339:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     33f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     343:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     347:	8b 90 0e fc ff ff    	mov    -0x3f2(%rax),%edx
     34d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     353:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     357:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     35b:	89 ca                	mov    %ecx,%edx
     35d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     363:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     367:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     36a:	89 a8 08 fc ff ff    	mov    %ebp,-0x3f8(%rax)
     370:	0f b7 a8 15 fc ff ff 	movzwl -0x3eb(%rax),%ebp
     377:	44 89 a8 0b fc ff ff 	mov    %r13d,-0x3f5(%rax)
     37e:	44 89 a0 0e fc ff ff 	mov    %r12d,-0x3f2(%rax)
     385:	89 90 11 fc ff ff    	mov    %edx,-0x3ef(%rax)
     38b:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     38f:	8b 90 1d fc ff ff    	mov    -0x3e3(%rax),%edx
     395:	89 c9                	mov    %ecx,%ecx
     397:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     39b:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     39e:	8b 88 17 fc ff ff    	mov    -0x3e9(%rax),%ecx
     3a4:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     3aa:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     3ae:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     3b2:	8b 88 1a fc ff ff    	mov    -0x3e6(%rax),%ecx
     3b8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     3be:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     3c2:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     3c6:	89 d1                	mov    %edx,%ecx
     3c8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     3ce:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     3d2:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     3d5:	89 a8 14 fc ff ff    	mov    %ebp,-0x3ec(%rax)
     3db:	44 89 a8 17 fc ff ff 	mov    %r13d,-0x3e9(%rax)
     3e2:	44 89 a0 1a fc ff ff 	mov    %r12d,-0x3e6(%rax)
     3e9:	89 88 1d fc ff ff    	mov    %ecx,-0x3e3(%rax)
     3ef:	8b 88 29 fc ff ff    	mov    -0x3d7(%rax),%ecx
     3f5:	0f b7 a8 21 fc ff ff 	movzwl -0x3df(%rax),%ebp
     3fc:	0f ac ea 18          	shrd   $0x18,%ebp,%edx
     400:	89 d2                	mov    %edx,%edx
     402:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     406:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     409:	8b 90 23 fc ff ff    	mov    -0x3dd(%rax),%edx
     40f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     415:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     419:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     41d:	8b 90 26 fc ff ff    	mov    -0x3da(%rax),%edx
     423:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     429:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     42d:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     431:	89 ca                	mov    %ecx,%edx
     433:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     439:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     43d:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     440:	89 a8 20 fc ff ff    	mov    %ebp,-0x3e0(%rax)
     446:	0f b7 a8 2d fc ff ff 	movzwl -0x3d3(%rax),%ebp
     44d:	44 89 a8 23 fc ff ff 	mov    %r13d,-0x3dd(%rax)
     454:	44 89 a0 26 fc ff ff 	mov    %r12d,-0x3da(%rax)
     45b:	89 90 29 fc ff ff    	mov    %edx,-0x3d7(%rax)
     461:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     465:	8b 90 35 fc ff ff    	mov    -0x3cb(%rax),%edx
     46b:	89 c9                	mov    %ecx,%ecx
     46d:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     471:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     474:	8b 88 2f fc ff ff    	mov    -0x3d1(%rax),%ecx
     47a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     480:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     484:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     488:	8b 88 32 fc ff ff    	mov    -0x3ce(%rax),%ecx
     48e:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     494:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     498:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     49c:	89 d1                	mov    %edx,%ecx
     49e:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     4a4:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     4a8:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     4ab:	89 a8 2c fc ff ff    	mov    %ebp,-0x3d4(%rax)
     4b1:	44 89 a8 2f fc ff ff 	mov    %r13d,-0x3d1(%rax)
     4b8:	44 89 a0 32 fc ff ff 	mov    %r12d,-0x3ce(%rax)
     4bf:	89 88 35 fc ff ff    	mov    %ecx,-0x3cb(%rax)
     4c5:	8b 88 41 fc ff ff    	mov    -0x3bf(%rax),%ecx
     4cb:	0f b7 a8 39 fc ff ff 	movzwl -0x3c7(%rax),%ebp
     4d2:	0f ac ea 18          	shrd   $0x18,%ebp,%edx
     4d6:	89 d2                	mov    %edx,%edx
     4d8:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     4dc:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     4df:	8b 90 3b fc ff ff    	mov    -0x3c5(%rax),%edx
     4e5:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     4eb:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     4ef:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     4f3:	8b 90 3e fc ff ff    	mov    -0x3c2(%rax),%edx
     4f9:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     4ff:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     503:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     507:	89 ca                	mov    %ecx,%edx
     509:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     50f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     513:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     516:	89 a8 38 fc ff ff    	mov    %ebp,-0x3c8(%rax)
     51c:	0f b7 a8 45 fc ff ff 	movzwl -0x3bb(%rax),%ebp
     523:	44 89 a8 3b fc ff ff 	mov    %r13d,-0x3c5(%rax)
     52a:	44 89 a0 3e fc ff ff 	mov    %r12d,-0x3c2(%rax)
     531:	89 90 41 fc ff ff    	mov    %edx,-0x3bf(%rax)
     537:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     53b:	8b 90 4d fc ff ff    	mov    -0x3b3(%rax),%edx
     541:	89 c9                	mov    %ecx,%ecx
     543:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     547:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     54a:	8b 88 47 fc ff ff    	mov    -0x3b9(%rax),%ecx
     550:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     556:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     55a:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     55e:	8b 88 4a fc ff ff    	mov    -0x3b6(%rax),%ecx
     564:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     56a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     56e:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     572:	89 d1                	mov    %edx,%ecx
     574:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     57a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     57e:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     581:	89 a8 44 fc ff ff    	mov    %ebp,-0x3bc(%rax)
     587:	44 89 a8 47 fc ff ff 	mov    %r13d,-0x3b9(%rax)
     58e:	44 89 a0 4a fc ff ff 	mov    %r12d,-0x3b6(%rax)
     595:	89 88 4d fc ff ff    	mov    %ecx,-0x3b3(%rax)
     59b:	8b 88 59 fc ff ff    	mov    -0x3a7(%rax),%ecx
     5a1:	0f b7 a8 51 fc ff ff 	movzwl -0x3af(%rax),%ebp
     5a8:	0f ac ea 18          	shrd   $0x18,%ebp,%edx
     5ac:	89 d2                	mov    %edx,%edx
     5ae:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5b2:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     5b5:	8b 90 53 fc ff ff    	mov    -0x3ad(%rax),%edx
     5bb:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     5c1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5c5:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     5c9:	8b 90 56 fc ff ff    	mov    -0x3aa(%rax),%edx
     5cf:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     5d5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5d9:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     5dd:	89 ca                	mov    %ecx,%edx
     5df:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     5e5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5e9:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     5ec:	89 a8 50 fc ff ff    	mov    %ebp,-0x3b0(%rax)
     5f2:	0f b7 a8 5d fc ff ff 	movzwl -0x3a3(%rax),%ebp
     5f9:	44 89 a8 53 fc ff ff 	mov    %r13d,-0x3ad(%rax)
     600:	44 89 a0 56 fc ff ff 	mov    %r12d,-0x3aa(%rax)
     607:	89 90 59 fc ff ff    	mov    %edx,-0x3a7(%rax)
     60d:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     611:	8b 90 65 fc ff ff    	mov    -0x39b(%rax),%edx
     617:	89 c9                	mov    %ecx,%ecx
     619:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     61d:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     620:	8b 88 5f fc ff ff    	mov    -0x3a1(%rax),%ecx
     626:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     62c:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     630:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     634:	8b 88 62 fc ff ff    	mov    -0x39e(%rax),%ecx
     63a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     640:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     644:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     648:	89 d1                	mov    %edx,%ecx
     64a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     650:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     654:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     657:	89 a8 5c fc ff ff    	mov    %ebp,-0x3a4(%rax)
     65d:	44 89 a8 5f fc ff ff 	mov    %r13d,-0x3a1(%rax)
     664:	44 89 a0 62 fc ff ff 	mov    %r12d,-0x39e(%rax)
     66b:	89 88 65 fc ff ff    	mov    %ecx,-0x39b(%rax)
     671:	8b 88 71 fc ff ff    	mov    -0x38f(%rax),%ecx
     677:	0f b7 a8 69 fc ff ff 	movzwl -0x397(%rax),%ebp
     67e:	0f ac ea 18          	shrd   $0x18,%ebp,%edx
     682:	89 d2                	mov    %edx,%edx
     684:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     688:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     68b:	8b 90 6b fc ff ff    	mov    -0x395(%rax),%edx
     691:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     697:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     69b:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     69f:	8b 90 6e fc ff ff    	mov    -0x392(%rax),%edx
     6a5:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     6ab:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6af:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     6b3:	89 ca                	mov    %ecx,%edx
     6b5:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     6bb:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6bf:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     6c2:	89 a8 68 fc ff ff    	mov    %ebp,-0x398(%rax)
     6c8:	0f b7 a8 75 fc ff ff 	movzwl -0x38b(%rax),%ebp
     6cf:	44 89 a8 6b fc ff ff 	mov    %r13d,-0x395(%rax)
     6d6:	44 89 a0 6e fc ff ff 	mov    %r12d,-0x392(%rax)
     6dd:	89 90 71 fc ff ff    	mov    %edx,-0x38f(%rax)
     6e3:	0f ac e9 18          	shrd   $0x18,%ebp,%ecx
     6e7:	8b 90 7d fc ff ff    	mov    -0x383(%rax),%edx
     6ed:	89 c9                	mov    %ecx,%ecx
     6ef:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     6f3:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     6f7:	8b 88 77 fc ff ff    	mov    -0x389(%rax),%ecx
     6fd:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     703:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     707:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     70b:	8b 88 7a fc ff ff    	mov    -0x386(%rax),%ecx
     711:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     717:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     71b:	44 8b 34 8e          	mov    (%rsi,%rcx,4),%r14d
     71f:	89 d1                	mov    %edx,%ecx
     721:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     727:	c1 ea 18             	shr    $0x18,%edx
     72a:	49 83 c0 40          	add    $0x40,%r8
     72e:	48 05 c0 00 00 00    	add    $0xc0,%rax
     734:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     738:	89 d5                	mov    %edx,%ebp
     73a:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
     73d:	44 89 a0 b4 fb ff ff 	mov    %r12d,-0x44c(%rax)
     744:	44 89 a8 b7 fb ff ff 	mov    %r13d,-0x449(%rax)
     74b:	44 89 b0 ba fb ff ff 	mov    %r14d,-0x446(%rax)
     752:	89 88 bd fb ff ff    	mov    %ecx,-0x443(%rax)
     758:	4d 39 d8             	cmp    %r11,%r8
     75b:	0f 85 1f f9 ff ff    	jne    80 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x80>
     761:	4c 8d 43 40          	lea    0x40(%rbx),%r8
     765:	48 83 c3 45          	add    $0x45,%rbx
     769:	0f b6 d2             	movzbl %dl,%edx
     76c:	49 39 d9             	cmp    %rbx,%r9
     76f:	0f 82 7c 00 00 00    	jb     7f1 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7f1>
     775:	4b 8d 04 40          	lea    (%r8,%r8,2),%rax
     779:	89 d1                	mov    %edx,%ecx
     77b:	4c 01 d0             	add    %r10,%rax
     77e:	66 90                	xchg   %ax,%ax
     780:	0f b7 50 01          	movzwl 0x1(%rax),%edx
     784:	0f b6 c9             	movzbl %cl,%ecx
     787:	44 8b 58 09          	mov    0x9(%rax),%r11d
     78b:	48 83 c0 0c          	add    $0xc,%rax
     78f:	c1 e2 08             	shl    $0x8,%edx
     792:	09 ca                	or     %ecx,%edx
     794:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     798:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     79b:	8b 50 f7             	mov    -0x9(%rax),%edx
     79e:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     7a4:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     7a8:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     7ac:	8b 50 fa             	mov    -0x6(%rax),%edx
     7af:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     7b5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     7b9:	8b 1c 96             	mov    (%rsi,%rdx,4),%ebx
     7bc:	44 89 da             	mov    %r11d,%edx
     7bf:	41 c1 eb 18          	shr    $0x18,%r11d
     7c3:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     7c9:	44 89 d9             	mov    %r11d,%ecx
     7cc:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     7d0:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     7d3:	89 68 f4             	mov    %ebp,-0xc(%rax)
     7d6:	44 89 60 f7          	mov    %r12d,-0x9(%rax)
     7da:	89 58 fa             	mov    %ebx,-0x6(%rax)
     7dd:	89 50 fd             	mov    %edx,-0x3(%rax)
     7e0:	49 8d 50 09          	lea    0x9(%r8),%rdx
     7e4:	49 83 c0 04          	add    $0x4,%r8
     7e8:	49 39 d1             	cmp    %rdx,%r9
     7eb:	73 93                	jae    780 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x780>
     7ed:	41 0f b6 d3          	movzbl %r11b,%edx
     7f1:	4d 39 c8             	cmp    %r9,%r8
     7f4:	73 61                	jae    857 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x857>
     7f6:	4b 8d 0c 40          	lea    (%r8,%r8,2),%rcx
     7fa:	49 8d 68 01          	lea    0x1(%r8),%rbp
     7fe:	4d 8d 5c 0a 02       	lea    0x2(%r10,%rcx,1),%r11
     803:	41 0f b6 44 0a 01    	movzbl 0x1(%r10,%rcx,1),%eax
     809:	41 0f b6 1b          	movzbl (%r11),%ebx
     80d:	c1 e0 08             	shl    $0x8,%eax
     810:	c1 e3 10             	shl    $0x10,%ebx
     813:	09 d8                	or     %ebx,%eax
     815:	09 d0                	or     %edx,%eax
     817:	49 8d 14 0a          	lea    (%r10,%rcx,1),%rdx
     81b:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     81f:	48 8d 04 86          	lea    (%rsi,%rax,4),%rax
     823:	8b 18                	mov    (%rax),%ebx
     825:	44 0f b7 30          	movzwl (%rax),%r14d
     829:	41 89 dd             	mov    %ebx,%r13d
     82c:	0f b6 c7             	movzbl %bh,%eax
     82f:	c1 eb 10             	shr    $0x10,%ebx
     832:	41 89 c4             	mov    %eax,%r12d
     835:	89 d8                	mov    %ebx,%eax
     837:	4c 39 cd             	cmp    %r9,%rbp
     83a:	72 2c                	jb     868 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x868>
     83c:	49 ff c9             	dec    %r9
     83f:	41 0f b6 cd          	movzbl %r13b,%ecx
     843:	44 89 e3             	mov    %r12d,%ebx
     846:	4d 29 c1             	sub    %r8,%r9
     849:	88 dd                	mov    %bl,%ch
     84b:	4b 8d 34 49          	lea    (%r9,%r9,2),%rsi
     84f:	66 89 0c 32          	mov    %cx,(%rdx,%rsi,1)
     853:	41 88 04 33          	mov    %al,(%r11,%rsi,1)
     857:	5b                   	pop    %rbx
     858:	5d                   	pop    %rbp
     859:	41 5c                	pop    %r12
     85b:	41 5d                	pop    %r13
     85d:	41 5e                	pop    %r14
     85f:	41 5f                	pop    %r15
     861:	c3                   	ret
     862:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
     868:	49 8d 6c 0a 03       	lea    0x3(%r10,%rcx,1),%rbp
     86d:	44 0f b6 65 00       	movzbl 0x0(%rbp),%r12d
     872:	66 44 89 32          	mov    %r14w,(%rdx)
     876:	41 88 1b             	mov    %bl,(%r11)
     879:	41 0f b6 44 0a 04    	movzbl 0x4(%r10,%rcx,1),%eax
     87f:	45 0f b6 6c 0a 05    	movzbl 0x5(%r10,%rcx,1),%r13d
     885:	c1 e0 08             	shl    $0x8,%eax
     888:	41 c1 e5 10          	shl    $0x10,%r13d
     88c:	44 09 e8             	or     %r13d,%eax
     88f:	44 09 e0             	or     %r12d,%eax
     892:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     896:	48 8d 04 86          	lea    (%rsi,%rax,4),%rax
     89a:	c5 f9 c4 00 00       	vpinsrw $0x0,(%rax),%xmm0,%xmm0
     89f:	8b 00                	mov    (%rax),%eax
     8a1:	0f b6 dc             	movzbl %ah,%ebx
     8a4:	41 89 c5             	mov    %eax,%r13d
     8a7:	c1 e8 10             	shr    $0x10,%eax
     8aa:	41 89 dc             	mov    %ebx,%r12d
     8ad:	49 8d 58 02          	lea    0x2(%r8),%rbx
     8b1:	41 89 c6             	mov    %eax,%r14d
     8b4:	4c 39 cb             	cmp    %r9,%rbx
     8b7:	73 83                	jae    83c <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x83c>
     8b9:	49 8d 44 0a 06       	lea    0x6(%r10,%rcx,1),%rax
     8be:	44 0f b6 20          	movzbl (%rax),%r12d
     8c2:	48 89 44 24 f8       	mov    %rax,-0x8(%rsp)
     8c7:	c4 e3 79 15 45 00 00 	vpextrw $0x0,%xmm0,0x0(%rbp)
     8ce:	41 0f b6 44 0a 07    	movzbl 0x7(%r10,%rcx,1),%eax
     8d4:	41 0f b6 6c 0a 08    	movzbl 0x8(%r10,%rcx,1),%ebp
     8da:	45 88 74 0a 05       	mov    %r14b,0x5(%r10,%rcx,1)
     8df:	4d 8d 70 03          	lea    0x3(%r8),%r14
     8e3:	c1 e5 10             	shl    $0x10,%ebp
     8e6:	c1 e0 08             	shl    $0x8,%eax
     8e9:	09 e8                	or     %ebp,%eax
     8eb:	44 09 e0             	or     %r12d,%eax
     8ee:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     8f2:	48 8d 04 86          	lea    (%rsi,%rax,4),%rax
     8f6:	c5 f9 c4 00 00       	vpinsrw $0x0,(%rax),%xmm0,%xmm0
     8fb:	8b 00                	mov    (%rax),%eax
     8fd:	0f b6 ec             	movzbl %ah,%ebp
     900:	41 89 c5             	mov    %eax,%r13d
     903:	c1 e8 10             	shr    $0x10,%eax
     906:	41 89 ec             	mov    %ebp,%r12d
     909:	89 c5                	mov    %eax,%ebp
     90b:	4d 39 ce             	cmp    %r9,%r14
     90e:	0f 83 28 ff ff ff    	jae    83c <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x83c>
     914:	48 8b 44 24 f8       	mov    -0x8(%rsp),%rax
     919:	45 0f b6 64 0a 09    	movzbl 0x9(%r10,%rcx,1),%r12d
     91f:	c4 e3 79 15 00 00    	vpextrw $0x0,%xmm0,(%rax)
     925:	41 88 6c 0a 08       	mov    %bpl,0x8(%r10,%rcx,1)
     92a:	41 0f b6 44 0a 0a    	movzbl 0xa(%r10,%rcx,1),%eax
     930:	41 0f b6 4c 0a 0b    	movzbl 0xb(%r10,%rcx,1),%ecx
     936:	c1 e0 08             	shl    $0x8,%eax
     939:	c1 e1 10             	shl    $0x10,%ecx
     93c:	09 c8                	or     %ecx,%eax
     93e:	41 0f b6 cc          	movzbl %r12b,%ecx
     942:	09 c8                	or     %ecx,%eax
     944:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     948:	8b 04 86             	mov    (%rsi,%rax,4),%eax
     94b:	0f b6 dc             	movzbl %ah,%ebx
     94e:	41 89 c5             	mov    %eax,%r13d
     951:	c1 e8 10             	shr    $0x10,%eax
     954:	41 89 dc             	mov    %ebx,%r12d
     957:	e9 e0 fe ff ff       	jmp    83c <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x83c>
     95c:	0f 1f 40 00          	nopl   0x0(%rax)
     960:	c3                   	ret
     961:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     968:	45 31 c0             	xor    %r8d,%r8d
     96b:	49 83 f9 04          	cmp    $0x4,%r9
     96f:	0f 87 00 fe ff ff    	ja     775 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x775>
     975:	e9 7c fe ff ff       	jmp    7f6 <jshc_channel::avx2_chain_overlap16(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7f6>
     97a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)

0000000000000980 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     980:	f3 0f 1e fa          	endbr64
     984:	4d 85 c0             	test   %r8,%r8
     987:	0f 84 53 10 00 00    	je     19e0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1060>
     98d:	55                   	push   %rbp
     98e:	b8 00 04 00 00       	mov    $0x400,%eax
     993:	48 89 e5             	mov    %rsp,%rbp
     996:	41 57                	push   %r15
     998:	41 56                	push   %r14
     99a:	41 55                	push   %r13
     99c:	41 54                	push   %r12
     99e:	49 89 cc             	mov    %rcx,%r12
     9a1:	53                   	push   %rbx
     9a2:	48 89 d3             	mov    %rdx,%rbx
     9a5:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     9a9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     9ad:	48 39 c2             	cmp    %rax,%rdx
     9b0:	48 0f 47 d0          	cmova  %rax,%rdx
     9b4:	31 c0                	xor    %eax,%eax
     9b6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     9bd:	00 00 00 
     9c0:	0f 18 04 03          	prefetchnta (%rbx,%rax,1)
     9c4:	48 83 c0 40          	add    $0x40,%rax
     9c8:	48 39 d0             	cmp    %rdx,%rax
     9cb:	72 f3                	jb     9c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     9cd:	49 89 d9             	mov    %rbx,%r9
     9d0:	4c 89 e2             	mov    %r12,%rdx
     9d3:	31 c9                	xor    %ecx,%ecx
     9d5:	eb 53                	jmp    a2a <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
     9d7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
     9de:	00 00 
     9e0:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     9e5:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     9ea:	48 ff c1             	inc    %rcx
     9ed:	48 83 c2 03          	add    $0x3,%rdx
     9f1:	49 83 c1 03          	add    $0x3,%r9
     9f5:	41 c1 e2 10          	shl    $0x10,%r10d
     9f9:	c1 e0 08             	shl    $0x8,%eax
     9fc:	44 09 d0             	or     %r10d,%eax
     9ff:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
     a04:	44 09 d0             	or     %r10d,%eax
     a07:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     a0b:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
     a0f:	41 8b 02             	mov    (%r10),%eax
     a12:	45 0f b7 12          	movzwl (%r10),%r10d
     a16:	c1 e8 10             	shr    $0x10,%eax
     a19:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
     a1e:	88 42 ff             	mov    %al,-0x1(%rdx)
     a21:	49 39 c8             	cmp    %rcx,%r8
     a24:	0f 84 ae 0f 00 00    	je     19d8 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1058>
     a2a:	f6 c2 3f             	test   $0x3f,%dl
     a2d:	75 b1                	jne    9e0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     a2f:	48 8d 41 48          	lea    0x48(%rcx),%rax
     a33:	49 39 c0             	cmp    %rax,%r8
     a36:	0f 82 a5 0f 00 00    	jb     19e1 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1061>
     a3c:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     a40:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # a48 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc8>
     a47:	00 
     a48:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # a50 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd0>
     a4f:	00 
     a50:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
     a55:	49 8d 14 04          	lea    (%r12,%rax,1),%rdx
     a59:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
     a5e:	48 8d 84 03 00 04 00 	lea    0x400(%rbx,%rax,1),%rax
     a65:	00 
     a66:	eb 0b                	jmp    a73 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
     a68:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     a6f:	00 
     a70:	4c 89 c9             	mov    %r9,%rcx
     a73:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
     a7a:	4d 39 c8             	cmp    %r9,%r8
     a7d:	72 15                	jb     a94 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
     a7f:	0f 18 00             	prefetchnta (%rax)
     a82:	0f 18 40 40          	prefetchnta 0x40(%rax)
     a86:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
     a8d:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
     a94:	44 8b 88 00 fc ff ff 	mov    -0x400(%rax),%r9d
     a9b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     aa2:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     aa7:	44 8b 88 03 fc ff ff 	mov    -0x3fd(%rax),%r9d
     aae:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ab5:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
     abb:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     ac0:	44 8b 88 06 fc ff ff 	mov    -0x3fa(%rax),%r9d
     ac7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ace:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
     ad5:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     ada:	44 8b 88 09 fc ff ff 	mov    -0x3f7(%rax),%r9d
     ae1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ae8:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     aed:	44 8b 88 0c fc ff ff 	mov    -0x3f4(%rax),%r9d
     af4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     afb:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     b00:	44 8b 88 0f fc ff ff 	mov    -0x3f1(%rax),%r9d
     b07:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b0e:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     b14:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     b19:	44 8b 88 12 fc ff ff 	mov    -0x3ee(%rax),%r9d
     b20:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b27:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     b2e:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     b33:	44 8b 88 15 fc ff ff 	mov    -0x3eb(%rax),%r9d
     b3a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b41:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     b47:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     b4c:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     b53:	44 8b 88 18 fc ff ff 	mov    -0x3e8(%rax),%r9d
     b5a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b61:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     b65:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     b6b:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     b70:	44 8b 88 1b fc ff ff 	mov    -0x3e5(%rax),%r9d
     b77:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     b7e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b85:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     b8a:	44 8b 88 1e fc ff ff 	mov    -0x3e2(%rax),%r9d
     b91:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     b95:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     b9b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ba2:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     ba7:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     bac:	44 8b 88 21 fc ff ff 	mov    -0x3df(%rax),%r9d
     bb3:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     bb8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bbf:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     bc4:	44 8b 88 24 fc ff ff 	mov    -0x3dc(%rax),%r9d
     bcb:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
     bd1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bd8:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     bdd:	44 8b 88 27 fc ff ff 	mov    -0x3d9(%rax),%r9d
     be4:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
     beb:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bf2:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     bf8:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     bfd:	44 8b 88 2a fc ff ff 	mov    -0x3d6(%rax),%r9d
     c04:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c0b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     c12:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     c17:	44 8b 88 2d fc ff ff 	mov    -0x3d3(%rax),%r9d
     c1e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c25:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     c2b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c30:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     c37:	44 8b 88 30 fc ff ff 	mov    -0x3d0(%rax),%r9d
     c3e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c45:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     c49:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     c4f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     c54:	44 8b 88 33 fc ff ff 	mov    -0x3cd(%rax),%r9d
     c5b:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     c62:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c69:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     c6e:	44 8b 88 36 fc ff ff 	mov    -0x3ca(%rax),%r9d
     c75:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     c79:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     c7f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c86:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     c8b:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     c90:	44 8b 88 39 fc ff ff 	mov    -0x3c7(%rax),%r9d
     c97:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     c9c:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     ca0:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     ca6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     cad:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     cb3:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     cb8:	44 8b 88 3c fc ff ff 	mov    -0x3c4(%rax),%r9d
     cbf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     cc6:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     ccb:	44 8b 88 3f fc ff ff 	mov    -0x3c1(%rax),%r9d
     cd2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     cd9:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     cde:	44 8b 88 42 fc ff ff 	mov    -0x3be(%rax),%r9d
     ce5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     cec:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     cf1:	44 8b 88 45 fc ff ff 	mov    -0x3bb(%rax),%r9d
     cf8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     cff:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     d04:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     d0a:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
     d10:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     d16:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     d1d:	44 8b 88 48 fc ff ff 	mov    -0x3b8(%rax),%r9d
     d24:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
     d2b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     d32:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d39:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     d3e:	44 8b 88 4b fc ff ff 	mov    -0x3b5(%rax),%r9d
     d45:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     d49:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     d4f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d56:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
     d5c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     d61:	44 8b 88 4e fc ff ff 	mov    -0x3b2(%rax),%r9d
     d68:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     d6f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d76:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
     d7d:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     d82:	44 8b 88 51 fc ff ff 	mov    -0x3af(%rax),%r9d
     d89:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     d8d:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     d93:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d9a:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     d9f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     da4:	44 8b 88 54 fc ff ff 	mov    -0x3ac(%rax),%r9d
     dab:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     db0:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     db4:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     dba:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     dc1:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     dc7:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     dcc:	44 8b 88 57 fc ff ff 	mov    -0x3a9(%rax),%r9d
     dd3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     dda:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     de0:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     de5:	44 8b 88 5a fc ff ff 	mov    -0x3a6(%rax),%r9d
     dec:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     df3:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     dfa:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     dff:	44 8b 88 5d fc ff ff 	mov    -0x3a3(%rax),%r9d
     e06:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e0d:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     e13:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     e18:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     e1f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     e23:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     e29:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     e30:	44 8b 88 60 fc ff ff 	mov    -0x3a0(%rax),%r9d
     e37:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e3e:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     e42:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     e47:	44 8b 88 63 fc ff ff 	mov    -0x39d(%rax),%r9d
     e4e:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     e54:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     e59:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e60:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
     e66:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     e6b:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     e70:	44 8b 88 66 fc ff ff 	mov    -0x39a(%rax),%r9d
     e77:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e7e:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
     e85:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     e8a:	44 8b 88 69 fc ff ff 	mov    -0x397(%rax),%r9d
     e91:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e98:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     e9d:	44 8b 88 6c fc ff ff 	mov    -0x394(%rax),%r9d
     ea4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     eab:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     eb0:	44 8b 88 6f fc ff ff 	mov    -0x391(%rax),%r9d
     eb7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ebe:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     ec4:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     ec9:	44 8b 88 72 fc ff ff 	mov    -0x38e(%rax),%r9d
     ed0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ed7:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     ede:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     ee3:	44 8b 88 75 fc ff ff 	mov    -0x38b(%rax),%r9d
     eea:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ef1:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     ef7:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     efc:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     f03:	44 8b 88 78 fc ff ff 	mov    -0x388(%rax),%r9d
     f0a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f11:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     f15:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     f1b:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     f20:	44 8b 88 7b fc ff ff 	mov    -0x385(%rax),%r9d
     f27:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     f2e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f35:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     f3a:	44 8b 88 7e fc ff ff 	mov    -0x382(%rax),%r9d
     f41:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     f45:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     f4b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f52:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     f57:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     f5c:	44 8b 88 81 fc ff ff 	mov    -0x37f(%rax),%r9d
     f63:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     f68:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f6f:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     f74:	44 8b 88 84 fc ff ff 	mov    -0x37c(%rax),%r9d
     f7b:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     f81:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f88:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     f8d:	44 8b 88 87 fc ff ff 	mov    -0x379(%rax),%r9d
     f94:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
     f9b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fa2:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     fa8:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     fad:	44 8b 88 8a fc ff ff 	mov    -0x376(%rax),%r9d
     fb4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fbb:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
     fc2:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     fc7:	44 8b 88 8d fc ff ff 	mov    -0x373(%rax),%r9d
     fce:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fd5:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
     fdb:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     fe0:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
     fe7:	44 8b 88 90 fc ff ff 	mov    -0x370(%rax),%r9d
     fee:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ff5:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     ff9:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
     fff:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1004:	44 8b 88 93 fc ff ff 	mov    -0x36d(%rax),%r9d
    100b:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1012:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1019:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    101e:	44 8b 88 96 fc ff ff 	mov    -0x36a(%rax),%r9d
    1025:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1029:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    102f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1036:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    103b:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1040:	44 8b 88 99 fc ff ff 	mov    -0x367(%rax),%r9d
    1047:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    104c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1053:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1058:	44 8b 88 9c fc ff ff 	mov    -0x364(%rax),%r9d
    105f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1066:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    106b:	44 8b 88 9f fc ff ff 	mov    -0x361(%rax),%r9d
    1072:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1079:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    107e:	44 8b 88 a2 fc ff ff 	mov    -0x35e(%rax),%r9d
    1085:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    108c:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1091:	44 8b 88 a5 fc ff ff 	mov    -0x35b(%rax),%r9d
    1098:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    109f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    10a4:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    10aa:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    10b0:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    10b6:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    10bd:	44 8b 88 a8 fc ff ff 	mov    -0x358(%rax),%r9d
    10c4:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    10cb:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    10d2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10d9:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    10de:	44 8b 88 ab fc ff ff 	mov    -0x355(%rax),%r9d
    10e5:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    10ea:	c4 21 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm10
    10f0:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10f7:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    10fc:	44 8b 88 ae fc ff ff 	mov    -0x352(%rax),%r9d
    1103:	c4 63 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm10,%xmm10
    110a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1111:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1116:	44 8b 88 b1 fc ff ff 	mov    -0x34f(%rax),%r9d
    111d:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1122:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1128:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    112e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1135:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    113a:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    113f:	44 8b 88 b4 fc ff ff 	mov    -0x34c(%rax),%r9d
    1146:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    114b:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1152:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1159:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1160:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    1165:	44 8b 88 b7 fc ff ff 	mov    -0x349(%rax),%r9d
    116c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1173:	c4 21 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm10
    1179:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    117e:	44 8b 88 ba fc ff ff 	mov    -0x346(%rax),%r9d
    1185:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    118c:	c4 23 29 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm10,%xmm10
    1193:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1198:	44 8b 88 bd fc ff ff 	mov    -0x343(%rax),%r9d
    119f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11a6:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    11ac:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    11b3:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    11b8:	c4 23 21 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm11,%xmm11
    11bf:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    11c3:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    11c8:	c4 21 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm11
    11ce:	c4 63 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm11,%xmm11
    11d5:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    11da:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    11df:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    11e5:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    11eb:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    11f0:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    11f6:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    11fc:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1201:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    1206:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    120b:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1210:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    1216:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    121c:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
    1223:	ff 
    1224:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    1228:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    122c:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
    1233:	ff 
    1234:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
    1239:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    123d:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    1241:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1247:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    124d:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1253:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1259:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    125e:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1262:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    1268:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    126e:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    1274:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    127a:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1280:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
    1285:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    128a:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
    128f:	48 05 c0 00 00 00    	add    $0xc0,%rax
    1295:	4d 39 d0             	cmp    %r10,%r8
    1298:	0f 83 d2 f7 ff ff    	jae    a70 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    129e:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    12a3:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    12a8:	48 8d 41 68          	lea    0x68(%rcx),%rax
    12ac:	0f ae f8             	sfence
    12af:	49 39 c0             	cmp    %rax,%r8
    12b2:	0f 82 90 03 00 00    	jb     1648 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    12b8:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    12bc:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 12c4 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x944>
    12c3:	00 
    12c4:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 12cc <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x94c>
    12cb:	00 
    12cc:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    12d1:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    12d6:	48 8d 04 13          	lea    (%rbx,%rdx,1),%rax
    12da:	4c 01 e2             	add    %r12,%rdx
    12dd:	0f 1f 00             	nopl   (%rax)
    12e0:	8b 48 48             	mov    0x48(%rax),%ecx
    12e3:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    12e9:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    12ee:	8b 48 4b             	mov    0x4b(%rax),%ecx
    12f1:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    12f7:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    12fd:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1302:	8b 48 4e             	mov    0x4e(%rax),%ecx
    1305:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    130b:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    1312:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1317:	8b 48 51             	mov    0x51(%rax),%ecx
    131a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1320:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1324:	8b 48 54             	mov    0x54(%rax),%ecx
    1327:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    132d:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1332:	8b 48 57             	mov    0x57(%rax),%ecx
    1335:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    133b:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1341:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1346:	8b 48 5a             	mov    0x5a(%rax),%ecx
    1349:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    134f:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1356:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    135b:	8b 48 5d             	mov    0x5d(%rax),%ecx
    135e:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1364:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    136a:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    136e:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    1375:	8b 48 30             	mov    0x30(%rax),%ecx
    1378:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    137e:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1382:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    1388:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    138d:	8b 48 33             	mov    0x33(%rax),%ecx
    1390:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    1397:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    139d:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    13a2:	8b 48 36             	mov    0x36(%rax),%ecx
    13a5:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    13a9:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    13af:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13b5:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    13ba:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    13bf:	8b 48 39             	mov    0x39(%rax),%ecx
    13c2:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    13c7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13cd:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    13d1:	8b 48 3c             	mov    0x3c(%rax),%ecx
    13d4:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    13da:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13e0:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    13e5:	8b 48 3f             	mov    0x3f(%rax),%ecx
    13e8:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    13ef:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13f5:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    13fb:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1400:	8b 48 42             	mov    0x42(%rax),%ecx
    1403:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1409:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1410:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1415:	8b 48 45             	mov    0x45(%rax),%ecx
    1418:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    141e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1424:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1428:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    142f:	8b 48 18             	mov    0x18(%rax),%ecx
    1432:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1438:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    143c:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1442:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1447:	8b 48 1b             	mov    0x1b(%rax),%ecx
    144a:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1451:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1457:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    145c:	8b 48 1e             	mov    0x1e(%rax),%ecx
    145f:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1463:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1469:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    146f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    1474:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1479:	8b 48 21             	mov    0x21(%rax),%ecx
    147c:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1481:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    1485:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    148b:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1491:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1495:	8b 48 24             	mov    0x24(%rax),%ecx
    1498:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    149e:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    14a3:	8b 48 27             	mov    0x27(%rax),%ecx
    14a6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14ac:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    14b1:	8b 48 2a             	mov    0x2a(%rax),%ecx
    14b4:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14ba:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    14bf:	8b 48 2d             	mov    0x2d(%rax),%ecx
    14c2:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14c8:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    14cc:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    14d2:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    14d8:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    14de:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    14e5:	8b 08                	mov    (%rax),%ecx
    14e7:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    14ee:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    14f5:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14fb:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1500:	8b 48 03             	mov    0x3(%rax),%ecx
    1503:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    1507:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    150d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1513:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1518:	8b 48 06             	mov    0x6(%rax),%ecx
    151b:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    1522:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1528:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    152d:	8b 48 09             	mov    0x9(%rax),%ecx
    1530:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1534:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    153a:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1540:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1546:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    154b:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    154f:	8b 48 0c             	mov    0xc(%rax),%ecx
    1552:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1557:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    155e:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    1562:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1568:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    156e:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1574:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1579:	8b 48 0f             	mov    0xf(%rax),%ecx
    157c:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    1582:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1588:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    158e:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1593:	8b 48 12             	mov    0x12(%rax),%ecx
    1596:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    159c:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    15a3:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    15a8:	8b 48 15             	mov    0x15(%rax),%ecx
    15ab:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    15b1:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    15b7:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    15bb:	c4 e3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm7,%xmm7
    15c2:	49 8d 49 48          	lea    0x48(%r9),%rcx
    15c6:	49 83 c1 20          	add    $0x20,%r9
    15ca:	48 83 c0 60          	add    $0x60,%rax
    15ce:	48 83 c2 60          	add    $0x60,%rdx
    15d2:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    15d6:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    15dc:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    15e3:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    15e7:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    15eb:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    15f1:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    15f7:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    15fd:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1601:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1606:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    160c:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1611:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1615:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    161b:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1620:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    1626:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    162b:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1630:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1635:	49 39 c8             	cmp    %rcx,%r8
    1638:	0f 83 a2 fc ff ff    	jae    12e0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x960>
    163e:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1643:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1648:	4d 8d 59 08          	lea    0x8(%r9),%r11
    164c:	4d 39 d8             	cmp    %r11,%r8
    164f:	0f 82 4d 01 00 00    	jb     17a2 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe22>
    1655:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    165a:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    165e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1666 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xce6>
    1665:	00 
    1666:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    166b:	4a 8d 0c 13          	lea    (%rbx,%r10,1),%rcx
    166f:	4d 01 e2             	add    %r12,%r10
    1672:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1678:	4c 8b 21             	mov    (%rcx),%r12
    167b:	48 8b 41 08          	mov    0x8(%rcx),%rax
    167f:	49 83 c2 18          	add    $0x18,%r10
    1683:	48 83 c1 18          	add    $0x18,%rcx
    1687:	48 8b 51 f8          	mov    -0x8(%rcx),%rdx
    168b:	4d 89 e1             	mov    %r12,%r9
    168e:	4d 89 e5             	mov    %r12,%r13
    1691:	49 89 c6             	mov    %rax,%r14
    1694:	49 c1 ed 30          	shr    $0x30,%r13
    1698:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    169f:	41 89 d7             	mov    %edx,%r15d
    16a2:	49 c1 ee 20          	shr    $0x20,%r14
    16a6:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    16ab:	4d 89 e1             	mov    %r12,%r9
    16ae:	41 89 c4             	mov    %eax,%r12d
    16b1:	41 c1 e7 08          	shl    $0x8,%r15d
    16b5:	41 c1 e4 10          	shl    $0x10,%r12d
    16b9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    16c0:	49 c1 e9 18          	shr    $0x18,%r9
    16c4:	45 09 ec             	or     %r13d,%r12d
    16c7:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    16cc:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16d3:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    16d8:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    16df:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    16e4:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    16e9:	41 89 c4             	mov    %eax,%r12d
    16ec:	48 c1 e8 38          	shr    $0x38,%rax
    16f0:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    16f6:	41 09 c7             	or     %eax,%r15d
    16f9:	41 c1 ec 08          	shr    $0x8,%r12d
    16fd:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1704:	4d 89 d9             	mov    %r11,%r9
    1707:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    170e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1713:	49 83 c3 08          	add    $0x8,%r11
    1717:	42 0f b6 04 3f       	movzbl (%rdi,%r15,1),%eax
    171c:	49 89 d7             	mov    %rdx,%r15
    171f:	48 c1 ea 28          	shr    $0x28,%rdx
    1723:	49 c1 ef 10          	shr    $0x10,%r15
    1727:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    172b:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1732:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
    1739:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    173e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1744:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
    174b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    174f:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1755:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    175c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1760:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1766:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    176b:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    176f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1775:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    177a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    177f:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    1783:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1789:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    178f:	4d 39 d8             	cmp    %r11,%r8
    1792:	0f 83 e0 fe ff ff    	jae    1678 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcf8>
    1798:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    179d:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    17a2:	4d 39 c1             	cmp    %r8,%r9
    17a5:	0f 83 15 02 00 00    	jae    19c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    17ab:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    17af:	4c 8d 14 03          	lea    (%rbx,%rax,1),%r10
    17b3:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    17b8:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    17bd:	45 0f b6 12          	movzbl (%r10),%r10d
    17c1:	c1 e2 08             	shl    $0x8,%edx
    17c4:	41 c1 e3 10          	shl    $0x10,%r11d
    17c8:	44 09 da             	or     %r11d,%edx
    17cb:	44 09 d2             	or     %r10d,%edx
    17ce:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    17d2:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    17d6:	41 8b 12             	mov    (%r10),%edx
    17d9:	45 0f b7 12          	movzwl (%r10),%r10d
    17dd:	c1 ea 10             	shr    $0x10,%edx
    17e0:	66 45 89 14 04       	mov    %r10w,(%r12,%rax,1)
    17e5:	41 88 54 04 02       	mov    %dl,0x2(%r12,%rax,1)
    17ea:	49 8d 51 01          	lea    0x1(%r9),%rdx
    17ee:	4c 39 c2             	cmp    %r8,%rdx
    17f1:	0f 83 c9 01 00 00    	jae    19c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    17f7:	4c 8d 54 03 03       	lea    0x3(%rbx,%rax,1),%r10
    17fc:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1801:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1806:	45 0f b6 12          	movzbl (%r10),%r10d
    180a:	41 c1 e3 10          	shl    $0x10,%r11d
    180e:	c1 e2 08             	shl    $0x8,%edx
    1811:	44 09 da             	or     %r11d,%edx
    1814:	44 09 d2             	or     %r10d,%edx
    1817:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    181b:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    181f:	44 8b 12             	mov    (%rdx),%r10d
    1822:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1826:	49 8d 51 02          	lea    0x2(%r9),%rdx
    182a:	44 89 d1             	mov    %r10d,%ecx
    182d:	66 45 89 5c 04 03    	mov    %r11w,0x3(%r12,%rax,1)
    1833:	c1 e9 10             	shr    $0x10,%ecx
    1836:	41 88 4c 04 05       	mov    %cl,0x5(%r12,%rax,1)
    183b:	4c 39 c2             	cmp    %r8,%rdx
    183e:	0f 83 7c 01 00 00    	jae    19c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1844:	4c 8d 54 03 06       	lea    0x6(%rbx,%rax,1),%r10
    1849:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    184e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1853:	45 0f b6 12          	movzbl (%r10),%r10d
    1857:	41 c1 e3 10          	shl    $0x10,%r11d
    185b:	c1 e2 08             	shl    $0x8,%edx
    185e:	44 09 da             	or     %r11d,%edx
    1861:	44 09 d2             	or     %r10d,%edx
    1864:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1868:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    186c:	44 8b 12             	mov    (%rdx),%r10d
    186f:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1873:	49 8d 51 03          	lea    0x3(%r9),%rdx
    1877:	44 89 d1             	mov    %r10d,%ecx
    187a:	66 45 89 5c 04 06    	mov    %r11w,0x6(%r12,%rax,1)
    1880:	c1 e9 10             	shr    $0x10,%ecx
    1883:	41 88 4c 04 08       	mov    %cl,0x8(%r12,%rax,1)
    1888:	4c 39 c2             	cmp    %r8,%rdx
    188b:	0f 83 2f 01 00 00    	jae    19c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1891:	4c 8d 54 03 09       	lea    0x9(%rbx,%rax,1),%r10
    1896:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    189b:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    18a0:	45 0f b6 12          	movzbl (%r10),%r10d
    18a4:	41 c1 e3 08          	shl    $0x8,%r11d
    18a8:	c1 e2 10             	shl    $0x10,%edx
    18ab:	44 09 da             	or     %r11d,%edx
    18ae:	44 09 d2             	or     %r10d,%edx
    18b1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    18b5:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    18b9:	44 8b 12             	mov    (%rdx),%r10d
    18bc:	44 0f b7 1a          	movzwl (%rdx),%r11d
    18c0:	49 8d 51 04          	lea    0x4(%r9),%rdx
    18c4:	44 89 d1             	mov    %r10d,%ecx
    18c7:	66 45 89 5c 04 09    	mov    %r11w,0x9(%r12,%rax,1)
    18cd:	c1 e9 10             	shr    $0x10,%ecx
    18d0:	41 88 4c 04 0b       	mov    %cl,0xb(%r12,%rax,1)
    18d5:	4c 39 c2             	cmp    %r8,%rdx
    18d8:	0f 83 e2 00 00 00    	jae    19c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    18de:	4c 8d 54 03 0c       	lea    0xc(%rbx,%rax,1),%r10
    18e3:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    18e8:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    18ed:	45 0f b6 12          	movzbl (%r10),%r10d
    18f1:	41 c1 e3 08          	shl    $0x8,%r11d
    18f5:	c1 e2 10             	shl    $0x10,%edx
    18f8:	44 09 da             	or     %r11d,%edx
    18fb:	44 09 d2             	or     %r10d,%edx
    18fe:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1902:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1906:	44 8b 12             	mov    (%rdx),%r10d
    1909:	44 0f b7 1a          	movzwl (%rdx),%r11d
    190d:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1911:	44 89 d1             	mov    %r10d,%ecx
    1914:	66 45 89 5c 04 0c    	mov    %r11w,0xc(%r12,%rax,1)
    191a:	c1 e9 10             	shr    $0x10,%ecx
    191d:	41 88 4c 04 0e       	mov    %cl,0xe(%r12,%rax,1)
    1922:	4c 39 c2             	cmp    %r8,%rdx
    1925:	0f 83 95 00 00 00    	jae    19c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    192b:	4c 8d 54 03 0f       	lea    0xf(%rbx,%rax,1),%r10
    1930:	49 83 c1 06          	add    $0x6,%r9
    1934:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1939:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    193e:	45 0f b6 12          	movzbl (%r10),%r10d
    1942:	41 c1 e3 08          	shl    $0x8,%r11d
    1946:	c1 e2 10             	shl    $0x10,%edx
    1949:	44 09 da             	or     %r11d,%edx
    194c:	44 09 d2             	or     %r10d,%edx
    194f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1953:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1957:	44 8b 12             	mov    (%rdx),%r10d
    195a:	44 0f b7 1a          	movzwl (%rdx),%r11d
    195e:	44 89 d1             	mov    %r10d,%ecx
    1961:	66 45 89 5c 04 0f    	mov    %r11w,0xf(%r12,%rax,1)
    1967:	c1 e9 10             	shr    $0x10,%ecx
    196a:	41 88 4c 04 11       	mov    %cl,0x11(%r12,%rax,1)
    196f:	4d 39 c1             	cmp    %r8,%r9
    1972:	73 4c                	jae    19c0 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1974:	48 8d 54 03 12       	lea    0x12(%rbx,%rax,1),%rdx
    1979:	4d 8d 44 04 12       	lea    0x12(%r12,%rax,1),%r8
    197e:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1982:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1986:	0f b6 12             	movzbl (%rdx),%edx
    1989:	c1 e0 08             	shl    $0x8,%eax
    198c:	c1 e1 10             	shl    $0x10,%ecx
    198f:	09 c8                	or     %ecx,%eax
    1991:	09 d0                	or     %edx,%eax
    1993:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    1997:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    199b:	8b 02                	mov    (%rdx),%eax
    199d:	0f b7 12             	movzwl (%rdx),%edx
    19a0:	c1 e8 10             	shr    $0x10,%eax
    19a3:	66 41 89 10          	mov    %dx,(%r8)
    19a7:	41 88 40 02          	mov    %al,0x2(%r8)
    19ab:	c5 f8 77             	vzeroupper
    19ae:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    19b2:	5b                   	pop    %rbx
    19b3:	41 5c                	pop    %r12
    19b5:	41 5d                	pop    %r13
    19b7:	41 5e                	pop    %r14
    19b9:	41 5f                	pop    %r15
    19bb:	5d                   	pop    %rbp
    19bc:	c3                   	ret
    19bd:	0f 1f 00             	nopl   (%rax)
    19c0:	c5 f8 77             	vzeroupper
    19c3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    19c7:	5b                   	pop    %rbx
    19c8:	41 5c                	pop    %r12
    19ca:	41 5d                	pop    %r13
    19cc:	41 5e                	pop    %r14
    19ce:	41 5f                	pop    %r15
    19d0:	5d                   	pop    %rbp
    19d1:	c3                   	ret
    19d2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    19d8:	4d 89 c1             	mov    %r8,%r9
    19db:	e9 68 fc ff ff       	jmp    1648 <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    19e0:	c3                   	ret
    19e1:	48 8d 41 28          	lea    0x28(%rcx),%rax
    19e5:	49 89 c9             	mov    %rcx,%r9
    19e8:	e9 c2 f8 ff ff       	jmp    12af <jshc_channel::avx2_chain_overlap16_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x92f>
