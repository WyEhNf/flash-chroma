
artifacts/skylake-overlap-linux-build-v1/CMakeFiles/jshc_skylake_overlap.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	48 85 c9             	test   %rcx,%rcx
       7:	0f 84 93 09 00 00    	je     9a0 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x9a0>
       d:	41 57                	push   %r15
       f:	b8 00 04 00 00       	mov    $0x400,%eax
      14:	49 89 c9             	mov    %rcx,%r9
      17:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
      1b:	48 39 c1             	cmp    %rax,%rcx
      1e:	49 89 d0             	mov    %rdx,%r8
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
      40:	41 0f 18 04 00       	prefetchnta (%r8,%rax,1)
      45:	48 83 c0 40          	add    $0x40,%rax
      49:	48 39 c8             	cmp    %rcx,%rax
      4c:	72 f2                	jb     40 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x40>
      4e:	49 83 f9 40          	cmp    $0x40,%r9
      52:	0f 86 50 09 00 00    	jbe    9a8 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x9a8>
      58:	49 8d 59 bf          	lea    -0x41(%r9),%rbx
      5c:	49 8d 80 40 04 00 00 	lea    0x440(%r8),%rax
      63:	41 ba 96 01 00 00    	mov    $0x196,%r10d
      69:	89 d1                	mov    %edx,%ecx
      6b:	48 83 e3 c0          	and    $0xffffffffffffffc0,%rbx
      6f:	4c 8d 9b d6 01 00 00 	lea    0x1d6(%rbx),%r11
      76:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
      7d:	00 00 00 
      80:	4d 39 d1             	cmp    %r10,%r9
      83:	72 0f                	jb     94 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x94>
      85:	0f 18 40 c0          	prefetchnta -0x40(%rax)
      89:	0f 18 00             	prefetchnta (%rax)
      8c:	0f 18 40 40          	prefetchnta 0x40(%rax)
      90:	0f 18 40 7f          	prefetchnta 0x7f(%rax)
      94:	8b 90 c0 fb ff ff    	mov    -0x440(%rax),%edx
      9a:	0f b6 c9             	movzbl %cl,%ecx
      9d:	8b a8 c9 fb ff ff    	mov    -0x437(%rax),%ebp
      a3:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
      a9:	09 ca                	or     %ecx,%edx
      ab:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      af:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
      b2:	8b 90 c3 fb ff ff    	mov    -0x43d(%rax),%edx
      b8:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
      be:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      c2:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
      c6:	8b 90 c6 fb ff ff    	mov    -0x43a(%rax),%edx
      cc:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
      d2:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      d6:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
      da:	89 ea                	mov    %ebp,%edx
      dc:	c1 ed 18             	shr    $0x18,%ebp
      df:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
      e5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
      e9:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
      ec:	89 88 c0 fb ff ff    	mov    %ecx,-0x440(%rax)
      f2:	44 89 a8 c3 fb ff ff 	mov    %r13d,-0x43d(%rax)
      f9:	8b 88 d5 fb ff ff    	mov    -0x42b(%rax),%ecx
      ff:	44 89 a0 c6 fb ff ff 	mov    %r12d,-0x43a(%rax)
     106:	89 90 c9 fb ff ff    	mov    %edx,-0x437(%rax)
     10c:	8b 90 cc fb ff ff    	mov    -0x434(%rax),%edx
     112:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     118:	09 ea                	or     %ebp,%edx
     11a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     11e:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     121:	8b 90 cf fb ff ff    	mov    -0x431(%rax),%edx
     127:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     12d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     131:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     135:	8b 90 d2 fb ff ff    	mov    -0x42e(%rax),%edx
     13b:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     141:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     145:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     149:	89 ca                	mov    %ecx,%edx
     14b:	c1 e9 18             	shr    $0x18,%ecx
     14e:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     154:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     158:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     15b:	89 a8 cc fb ff ff    	mov    %ebp,-0x434(%rax)
     161:	44 89 a8 cf fb ff ff 	mov    %r13d,-0x431(%rax)
     168:	44 89 a0 d2 fb ff ff 	mov    %r12d,-0x42e(%rax)
     16f:	89 90 d5 fb ff ff    	mov    %edx,-0x42b(%rax)
     175:	8b a8 e1 fb ff ff    	mov    -0x41f(%rax),%ebp
     17b:	8b 90 d8 fb ff ff    	mov    -0x428(%rax),%edx
     181:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     187:	09 ca                	or     %ecx,%edx
     189:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     18d:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
     190:	8b 90 db fb ff ff    	mov    -0x425(%rax),%edx
     196:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     19c:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     1a0:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     1a4:	8b 90 de fb ff ff    	mov    -0x422(%rax),%edx
     1aa:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     1b0:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     1b4:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     1b8:	89 ea                	mov    %ebp,%edx
     1ba:	c1 ed 18             	shr    $0x18,%ebp
     1bd:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     1c3:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     1c7:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     1ca:	89 88 d8 fb ff ff    	mov    %ecx,-0x428(%rax)
     1d0:	44 89 a8 db fb ff ff 	mov    %r13d,-0x425(%rax)
     1d7:	8b 88 ed fb ff ff    	mov    -0x413(%rax),%ecx
     1dd:	44 89 a0 de fb ff ff 	mov    %r12d,-0x422(%rax)
     1e4:	89 90 e1 fb ff ff    	mov    %edx,-0x41f(%rax)
     1ea:	8b 90 e4 fb ff ff    	mov    -0x41c(%rax),%edx
     1f0:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     1f6:	09 ea                	or     %ebp,%edx
     1f8:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     1fc:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     1ff:	8b 90 e7 fb ff ff    	mov    -0x419(%rax),%edx
     205:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     20b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     20f:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     213:	8b 90 ea fb ff ff    	mov    -0x416(%rax),%edx
     219:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     21f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     223:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     227:	89 ca                	mov    %ecx,%edx
     229:	c1 e9 18             	shr    $0x18,%ecx
     22c:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     232:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     236:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     239:	89 a8 e4 fb ff ff    	mov    %ebp,-0x41c(%rax)
     23f:	44 89 a8 e7 fb ff ff 	mov    %r13d,-0x419(%rax)
     246:	44 89 a0 ea fb ff ff 	mov    %r12d,-0x416(%rax)
     24d:	89 90 ed fb ff ff    	mov    %edx,-0x413(%rax)
     253:	8b a8 f9 fb ff ff    	mov    -0x407(%rax),%ebp
     259:	8b 90 f0 fb ff ff    	mov    -0x410(%rax),%edx
     25f:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     265:	09 ca                	or     %ecx,%edx
     267:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     26b:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
     26e:	8b 90 f3 fb ff ff    	mov    -0x40d(%rax),%edx
     274:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     27a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     27e:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     282:	8b 90 f6 fb ff ff    	mov    -0x40a(%rax),%edx
     288:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     28e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     292:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     296:	89 ea                	mov    %ebp,%edx
     298:	c1 ed 18             	shr    $0x18,%ebp
     29b:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     2a1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     2a5:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     2a8:	89 88 f0 fb ff ff    	mov    %ecx,-0x410(%rax)
     2ae:	44 89 a8 f3 fb ff ff 	mov    %r13d,-0x40d(%rax)
     2b5:	8b 88 05 fc ff ff    	mov    -0x3fb(%rax),%ecx
     2bb:	44 89 a0 f6 fb ff ff 	mov    %r12d,-0x40a(%rax)
     2c2:	89 90 f9 fb ff ff    	mov    %edx,-0x407(%rax)
     2c8:	8b 90 fc fb ff ff    	mov    -0x404(%rax),%edx
     2ce:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     2d4:	09 ea                	or     %ebp,%edx
     2d6:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     2da:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     2dd:	8b 90 ff fb ff ff    	mov    -0x401(%rax),%edx
     2e3:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     2e9:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     2ed:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     2f1:	8b 90 02 fc ff ff    	mov    -0x3fe(%rax),%edx
     2f7:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     2fd:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     301:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     305:	89 ca                	mov    %ecx,%edx
     307:	c1 e9 18             	shr    $0x18,%ecx
     30a:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     310:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     314:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     317:	89 a8 fc fb ff ff    	mov    %ebp,-0x404(%rax)
     31d:	44 89 a8 ff fb ff ff 	mov    %r13d,-0x401(%rax)
     324:	44 89 a0 02 fc ff ff 	mov    %r12d,-0x3fe(%rax)
     32b:	89 90 05 fc ff ff    	mov    %edx,-0x3fb(%rax)
     331:	8b a8 11 fc ff ff    	mov    -0x3ef(%rax),%ebp
     337:	8b 90 08 fc ff ff    	mov    -0x3f8(%rax),%edx
     33d:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     343:	09 ca                	or     %ecx,%edx
     345:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     349:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
     34c:	8b 90 0b fc ff ff    	mov    -0x3f5(%rax),%edx
     352:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     358:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     35c:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     360:	8b 90 0e fc ff ff    	mov    -0x3f2(%rax),%edx
     366:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     36c:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     370:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     374:	89 ea                	mov    %ebp,%edx
     376:	c1 ed 18             	shr    $0x18,%ebp
     379:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     37f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     383:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     386:	89 88 08 fc ff ff    	mov    %ecx,-0x3f8(%rax)
     38c:	44 89 a8 0b fc ff ff 	mov    %r13d,-0x3f5(%rax)
     393:	8b 88 1d fc ff ff    	mov    -0x3e3(%rax),%ecx
     399:	44 89 a0 0e fc ff ff 	mov    %r12d,-0x3f2(%rax)
     3a0:	89 90 11 fc ff ff    	mov    %edx,-0x3ef(%rax)
     3a6:	8b 90 14 fc ff ff    	mov    -0x3ec(%rax),%edx
     3ac:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     3b2:	09 ea                	or     %ebp,%edx
     3b4:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     3b8:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     3bb:	8b 90 17 fc ff ff    	mov    -0x3e9(%rax),%edx
     3c1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     3c7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     3cb:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     3cf:	8b 90 1a fc ff ff    	mov    -0x3e6(%rax),%edx
     3d5:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     3db:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     3df:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     3e3:	89 ca                	mov    %ecx,%edx
     3e5:	c1 e9 18             	shr    $0x18,%ecx
     3e8:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     3ee:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     3f2:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     3f5:	89 a8 14 fc ff ff    	mov    %ebp,-0x3ec(%rax)
     3fb:	44 89 a8 17 fc ff ff 	mov    %r13d,-0x3e9(%rax)
     402:	44 89 a0 1a fc ff ff 	mov    %r12d,-0x3e6(%rax)
     409:	89 90 1d fc ff ff    	mov    %edx,-0x3e3(%rax)
     40f:	8b a8 29 fc ff ff    	mov    -0x3d7(%rax),%ebp
     415:	8b 90 20 fc ff ff    	mov    -0x3e0(%rax),%edx
     41b:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     421:	09 ca                	or     %ecx,%edx
     423:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     427:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
     42a:	8b 90 23 fc ff ff    	mov    -0x3dd(%rax),%edx
     430:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     436:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     43a:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     43e:	8b 90 26 fc ff ff    	mov    -0x3da(%rax),%edx
     444:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     44a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     44e:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     452:	89 ea                	mov    %ebp,%edx
     454:	c1 ed 18             	shr    $0x18,%ebp
     457:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     45d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     461:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     464:	89 88 20 fc ff ff    	mov    %ecx,-0x3e0(%rax)
     46a:	44 89 a8 23 fc ff ff 	mov    %r13d,-0x3dd(%rax)
     471:	8b 88 35 fc ff ff    	mov    -0x3cb(%rax),%ecx
     477:	44 89 a0 26 fc ff ff 	mov    %r12d,-0x3da(%rax)
     47e:	89 90 29 fc ff ff    	mov    %edx,-0x3d7(%rax)
     484:	8b 90 2c fc ff ff    	mov    -0x3d4(%rax),%edx
     48a:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     490:	09 ea                	or     %ebp,%edx
     492:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     496:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     499:	8b 90 2f fc ff ff    	mov    -0x3d1(%rax),%edx
     49f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     4a5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     4a9:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     4ad:	8b 90 32 fc ff ff    	mov    -0x3ce(%rax),%edx
     4b3:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     4b9:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     4bd:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     4c1:	89 ca                	mov    %ecx,%edx
     4c3:	c1 e9 18             	shr    $0x18,%ecx
     4c6:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     4cc:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     4d0:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     4d3:	89 a8 2c fc ff ff    	mov    %ebp,-0x3d4(%rax)
     4d9:	44 89 a8 2f fc ff ff 	mov    %r13d,-0x3d1(%rax)
     4e0:	44 89 a0 32 fc ff ff 	mov    %r12d,-0x3ce(%rax)
     4e7:	89 90 35 fc ff ff    	mov    %edx,-0x3cb(%rax)
     4ed:	8b a8 41 fc ff ff    	mov    -0x3bf(%rax),%ebp
     4f3:	8b 90 38 fc ff ff    	mov    -0x3c8(%rax),%edx
     4f9:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     4ff:	09 ca                	or     %ecx,%edx
     501:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     505:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
     508:	8b 90 3b fc ff ff    	mov    -0x3c5(%rax),%edx
     50e:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     514:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     518:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     51c:	8b 90 3e fc ff ff    	mov    -0x3c2(%rax),%edx
     522:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     528:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     52c:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     530:	89 ea                	mov    %ebp,%edx
     532:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     538:	c1 ed 18             	shr    $0x18,%ebp
     53b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     53f:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     542:	89 88 38 fc ff ff    	mov    %ecx,-0x3c8(%rax)
     548:	44 89 a8 3b fc ff ff 	mov    %r13d,-0x3c5(%rax)
     54f:	8b 88 4d fc ff ff    	mov    -0x3b3(%rax),%ecx
     555:	44 89 a0 3e fc ff ff 	mov    %r12d,-0x3c2(%rax)
     55c:	89 90 41 fc ff ff    	mov    %edx,-0x3bf(%rax)
     562:	8b 90 44 fc ff ff    	mov    -0x3bc(%rax),%edx
     568:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     56e:	09 ea                	or     %ebp,%edx
     570:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     574:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     577:	8b 90 47 fc ff ff    	mov    -0x3b9(%rax),%edx
     57d:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     583:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     587:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     58b:	8b 90 4a fc ff ff    	mov    -0x3b6(%rax),%edx
     591:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     597:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     59b:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     59f:	89 ca                	mov    %ecx,%edx
     5a1:	c1 e9 18             	shr    $0x18,%ecx
     5a4:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     5aa:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5ae:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     5b1:	89 a8 44 fc ff ff    	mov    %ebp,-0x3bc(%rax)
     5b7:	44 89 a8 47 fc ff ff 	mov    %r13d,-0x3b9(%rax)
     5be:	44 89 a0 4a fc ff ff 	mov    %r12d,-0x3b6(%rax)
     5c5:	89 90 4d fc ff ff    	mov    %edx,-0x3b3(%rax)
     5cb:	8b a8 59 fc ff ff    	mov    -0x3a7(%rax),%ebp
     5d1:	8b 90 50 fc ff ff    	mov    -0x3b0(%rax),%edx
     5d7:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     5dd:	09 ca                	or     %ecx,%edx
     5df:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5e3:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
     5e6:	8b 90 53 fc ff ff    	mov    -0x3ad(%rax),%edx
     5ec:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     5f2:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     5f6:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     5fa:	8b 90 56 fc ff ff    	mov    -0x3aa(%rax),%edx
     600:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     606:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     60a:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     60e:	89 ea                	mov    %ebp,%edx
     610:	c1 ed 18             	shr    $0x18,%ebp
     613:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     619:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     61d:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     620:	89 88 50 fc ff ff    	mov    %ecx,-0x3b0(%rax)
     626:	44 89 a8 53 fc ff ff 	mov    %r13d,-0x3ad(%rax)
     62d:	8b 88 65 fc ff ff    	mov    -0x39b(%rax),%ecx
     633:	44 89 a0 56 fc ff ff 	mov    %r12d,-0x3aa(%rax)
     63a:	89 90 59 fc ff ff    	mov    %edx,-0x3a7(%rax)
     640:	8b 90 5c fc ff ff    	mov    -0x3a4(%rax),%edx
     646:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     64c:	09 ea                	or     %ebp,%edx
     64e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     652:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     655:	8b 90 5f fc ff ff    	mov    -0x3a1(%rax),%edx
     65b:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     661:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     665:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     669:	8b 90 62 fc ff ff    	mov    -0x39e(%rax),%edx
     66f:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     675:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     679:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     67d:	89 ca                	mov    %ecx,%edx
     67f:	c1 e9 18             	shr    $0x18,%ecx
     682:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     688:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     68c:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     68f:	89 a8 5c fc ff ff    	mov    %ebp,-0x3a4(%rax)
     695:	44 89 a8 5f fc ff ff 	mov    %r13d,-0x3a1(%rax)
     69c:	44 89 a0 62 fc ff ff 	mov    %r12d,-0x39e(%rax)
     6a3:	89 90 65 fc ff ff    	mov    %edx,-0x39b(%rax)
     6a9:	8b a8 71 fc ff ff    	mov    -0x38f(%rax),%ebp
     6af:	8b 90 68 fc ff ff    	mov    -0x398(%rax),%edx
     6b5:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     6bb:	09 ca                	or     %ecx,%edx
     6bd:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6c1:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
     6c4:	8b 90 6b fc ff ff    	mov    -0x395(%rax),%edx
     6ca:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     6d0:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6d4:	44 8b 2c 96          	mov    (%rsi,%rdx,4),%r13d
     6d8:	8b 90 6e fc ff ff    	mov    -0x392(%rax),%edx
     6de:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     6e4:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6e8:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     6ec:	89 ea                	mov    %ebp,%edx
     6ee:	c1 ed 18             	shr    $0x18,%ebp
     6f1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     6f7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     6fb:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     6fe:	89 88 68 fc ff ff    	mov    %ecx,-0x398(%rax)
     704:	44 89 a8 6b fc ff ff 	mov    %r13d,-0x395(%rax)
     70b:	44 89 a0 6e fc ff ff 	mov    %r12d,-0x392(%rax)
     712:	89 90 71 fc ff ff    	mov    %edx,-0x38f(%rax)
     718:	8b 90 7d fc ff ff    	mov    -0x383(%rax),%edx
     71e:	8b 88 74 fc ff ff    	mov    -0x38c(%rax),%ecx
     724:	81 e1 00 ff ff 00    	and    $0xffff00,%ecx
     72a:	09 e9                	or     %ebp,%ecx
     72c:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     730:	8b 2c 8e             	mov    (%rsi,%rcx,4),%ebp
     733:	8b 88 77 fc ff ff    	mov    -0x389(%rax),%ecx
     739:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     73f:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     743:	44 8b 2c 8e          	mov    (%rsi,%rcx,4),%r13d
     747:	8b 88 7a fc ff ff    	mov    -0x386(%rax),%ecx
     74d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     753:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     757:	44 8b 34 8e          	mov    (%rsi,%rcx,4),%r14d
     75b:	89 d1                	mov    %edx,%ecx
     75d:	c1 ea 18             	shr    $0x18,%edx
     760:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
     766:	49 83 c2 40          	add    $0x40,%r10
     76a:	48 05 c0 00 00 00    	add    $0xc0,%rax
     770:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
     774:	44 8b 24 8e          	mov    (%rsi,%rcx,4),%r12d
     778:	89 a8 b4 fb ff ff    	mov    %ebp,-0x44c(%rax)
     77e:	89 d1                	mov    %edx,%ecx
     780:	44 89 a8 b7 fb ff ff 	mov    %r13d,-0x449(%rax)
     787:	44 89 b0 ba fb ff ff 	mov    %r14d,-0x446(%rax)
     78e:	44 89 a0 bd fb ff ff 	mov    %r12d,-0x443(%rax)
     795:	4d 39 da             	cmp    %r11,%r10
     798:	0f 85 e2 f8 ff ff    	jne    80 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x80>
     79e:	4c 8d 53 40          	lea    0x40(%rbx),%r10
     7a2:	48 83 c3 45          	add    $0x45,%rbx
     7a6:	0f b6 d2             	movzbl %dl,%edx
     7a9:	49 39 d9             	cmp    %rbx,%r9
     7ac:	0f 82 80 00 00 00    	jb     832 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x832>
     7b2:	4b 8d 04 52          	lea    (%r10,%r10,2),%rax
     7b6:	89 d1                	mov    %edx,%ecx
     7b8:	4c 01 c0             	add    %r8,%rax
     7bb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     7c0:	8b 10                	mov    (%rax),%edx
     7c2:	0f b6 c9             	movzbl %cl,%ecx
     7c5:	44 8b 58 09          	mov    0x9(%rax),%r11d
     7c9:	48 83 c0 0c          	add    $0xc,%rax
     7cd:	81 e2 00 ff ff 00    	and    $0xffff00,%edx
     7d3:	09 ca                	or     %ecx,%edx
     7d5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     7d9:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
     7dc:	8b 50 f7             	mov    -0x9(%rax),%edx
     7df:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     7e5:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     7e9:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
     7ed:	8b 50 fa             	mov    -0x6(%rax),%edx
     7f0:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     7f6:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     7fa:	8b 1c 96             	mov    (%rsi,%rdx,4),%ebx
     7fd:	44 89 da             	mov    %r11d,%edx
     800:	41 c1 eb 18          	shr    $0x18,%r11d
     804:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
     80a:	44 89 d9             	mov    %r11d,%ecx
     80d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
     811:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
     814:	89 68 f4             	mov    %ebp,-0xc(%rax)
     817:	44 89 60 f7          	mov    %r12d,-0x9(%rax)
     81b:	89 58 fa             	mov    %ebx,-0x6(%rax)
     81e:	89 50 fd             	mov    %edx,-0x3(%rax)
     821:	49 8d 52 09          	lea    0x9(%r10),%rdx
     825:	49 83 c2 04          	add    $0x4,%r10
     829:	49 39 d1             	cmp    %rdx,%r9
     82c:	73 92                	jae    7c0 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7c0>
     82e:	41 0f b6 d3          	movzbl %r11b,%edx
     832:	4d 39 ca             	cmp    %r9,%r10
     835:	73 61                	jae    898 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x898>
     837:	4b 8d 0c 52          	lea    (%r10,%r10,2),%rcx
     83b:	49 8d 6a 01          	lea    0x1(%r10),%rbp
     83f:	4d 8d 5c 08 02       	lea    0x2(%r8,%rcx,1),%r11
     844:	41 0f b6 44 08 01    	movzbl 0x1(%r8,%rcx,1),%eax
     84a:	41 0f b6 1b          	movzbl (%r11),%ebx
     84e:	c1 e0 08             	shl    $0x8,%eax
     851:	c1 e3 10             	shl    $0x10,%ebx
     854:	09 d8                	or     %ebx,%eax
     856:	09 d0                	or     %edx,%eax
     858:	49 8d 14 08          	lea    (%r8,%rcx,1),%rdx
     85c:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     860:	48 8d 04 86          	lea    (%rsi,%rax,4),%rax
     864:	8b 18                	mov    (%rax),%ebx
     866:	44 0f b7 30          	movzwl (%rax),%r14d
     86a:	41 89 dd             	mov    %ebx,%r13d
     86d:	0f b6 c7             	movzbl %bh,%eax
     870:	c1 eb 10             	shr    $0x10,%ebx
     873:	41 89 c4             	mov    %eax,%r12d
     876:	89 d8                	mov    %ebx,%eax
     878:	4c 39 cd             	cmp    %r9,%rbp
     87b:	72 2b                	jb     8a8 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x8a8>
     87d:	49 ff c9             	dec    %r9
     880:	41 0f b6 cd          	movzbl %r13b,%ecx
     884:	44 89 e3             	mov    %r12d,%ebx
     887:	4d 29 d1             	sub    %r10,%r9
     88a:	88 dd                	mov    %bl,%ch
     88c:	4b 8d 34 49          	lea    (%r9,%r9,2),%rsi
     890:	66 89 0c 32          	mov    %cx,(%rdx,%rsi,1)
     894:	41 88 04 33          	mov    %al,(%r11,%rsi,1)
     898:	5b                   	pop    %rbx
     899:	5d                   	pop    %rbp
     89a:	41 5c                	pop    %r12
     89c:	41 5d                	pop    %r13
     89e:	41 5e                	pop    %r14
     8a0:	41 5f                	pop    %r15
     8a2:	c3                   	ret
     8a3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
     8a8:	49 8d 6c 08 03       	lea    0x3(%r8,%rcx,1),%rbp
     8ad:	44 0f b6 65 00       	movzbl 0x0(%rbp),%r12d
     8b2:	66 44 89 32          	mov    %r14w,(%rdx)
     8b6:	41 88 1b             	mov    %bl,(%r11)
     8b9:	41 0f b6 44 08 04    	movzbl 0x4(%r8,%rcx,1),%eax
     8bf:	45 0f b6 6c 08 05    	movzbl 0x5(%r8,%rcx,1),%r13d
     8c5:	c1 e0 08             	shl    $0x8,%eax
     8c8:	41 c1 e5 10          	shl    $0x10,%r13d
     8cc:	44 09 e8             	or     %r13d,%eax
     8cf:	44 09 e0             	or     %r12d,%eax
     8d2:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     8d6:	48 8d 04 86          	lea    (%rsi,%rax,4),%rax
     8da:	c5 f9 c4 00 00       	vpinsrw $0x0,(%rax),%xmm0,%xmm0
     8df:	8b 00                	mov    (%rax),%eax
     8e1:	0f b6 dc             	movzbl %ah,%ebx
     8e4:	41 89 c5             	mov    %eax,%r13d
     8e7:	c1 e8 10             	shr    $0x10,%eax
     8ea:	41 89 dc             	mov    %ebx,%r12d
     8ed:	49 8d 5a 02          	lea    0x2(%r10),%rbx
     8f1:	41 89 c6             	mov    %eax,%r14d
     8f4:	4c 39 cb             	cmp    %r9,%rbx
     8f7:	73 84                	jae    87d <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x87d>
     8f9:	49 8d 44 08 06       	lea    0x6(%r8,%rcx,1),%rax
     8fe:	44 0f b6 20          	movzbl (%rax),%r12d
     902:	48 89 44 24 f8       	mov    %rax,-0x8(%rsp)
     907:	c4 e3 79 15 45 00 00 	vpextrw $0x0,%xmm0,0x0(%rbp)
     90e:	41 0f b6 44 08 07    	movzbl 0x7(%r8,%rcx,1),%eax
     914:	41 0f b6 6c 08 08    	movzbl 0x8(%r8,%rcx,1),%ebp
     91a:	45 88 74 08 05       	mov    %r14b,0x5(%r8,%rcx,1)
     91f:	4d 8d 72 03          	lea    0x3(%r10),%r14
     923:	c1 e5 10             	shl    $0x10,%ebp
     926:	c1 e0 08             	shl    $0x8,%eax
     929:	09 e8                	or     %ebp,%eax
     92b:	44 09 e0             	or     %r12d,%eax
     92e:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     932:	48 8d 04 86          	lea    (%rsi,%rax,4),%rax
     936:	c5 f9 c4 00 00       	vpinsrw $0x0,(%rax),%xmm0,%xmm0
     93b:	8b 00                	mov    (%rax),%eax
     93d:	0f b6 ec             	movzbl %ah,%ebp
     940:	41 89 c5             	mov    %eax,%r13d
     943:	c1 e8 10             	shr    $0x10,%eax
     946:	41 89 ec             	mov    %ebp,%r12d
     949:	89 c5                	mov    %eax,%ebp
     94b:	4d 39 ce             	cmp    %r9,%r14
     94e:	0f 83 29 ff ff ff    	jae    87d <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x87d>
     954:	48 8b 44 24 f8       	mov    -0x8(%rsp),%rax
     959:	45 0f b6 64 08 09    	movzbl 0x9(%r8,%rcx,1),%r12d
     95f:	c4 e3 79 15 00 00    	vpextrw $0x0,%xmm0,(%rax)
     965:	41 88 6c 08 08       	mov    %bpl,0x8(%r8,%rcx,1)
     96a:	41 0f b6 44 08 0a    	movzbl 0xa(%r8,%rcx,1),%eax
     970:	41 0f b6 4c 08 0b    	movzbl 0xb(%r8,%rcx,1),%ecx
     976:	c1 e0 08             	shl    $0x8,%eax
     979:	c1 e1 10             	shl    $0x10,%ecx
     97c:	09 c8                	or     %ecx,%eax
     97e:	41 0f b6 cc          	movzbl %r12b,%ecx
     982:	09 c8                	or     %ecx,%eax
     984:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     988:	8b 04 86             	mov    (%rsi,%rax,4),%eax
     98b:	0f b6 dc             	movzbl %ah,%ebx
     98e:	41 89 c5             	mov    %eax,%r13d
     991:	c1 e8 10             	shr    $0x10,%eax
     994:	41 89 dc             	mov    %ebx,%r12d
     997:	e9 e1 fe ff ff       	jmp    87d <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x87d>
     99c:	0f 1f 40 00          	nopl   0x0(%rax)
     9a0:	c3                   	ret
     9a1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
     9a8:	45 31 d2             	xor    %r10d,%r10d
     9ab:	49 83 f9 04          	cmp    $0x4,%r9
     9af:	0f 87 fd fd ff ff    	ja     7b2 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x7b2>
     9b5:	e9 7d fe ff ff       	jmp    837 <jshc_channel::avx2_chain_overlap(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x837>
     9ba:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)

00000000000009c0 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
     9c0:	f3 0f 1e fa          	endbr64
     9c4:	4d 85 c0             	test   %r8,%r8
     9c7:	0f 84 53 10 00 00    	je     1a20 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1060>
     9cd:	55                   	push   %rbp
     9ce:	b8 00 04 00 00       	mov    $0x400,%eax
     9d3:	48 89 e5             	mov    %rsp,%rbp
     9d6:	41 57                	push   %r15
     9d8:	41 56                	push   %r14
     9da:	41 55                	push   %r13
     9dc:	41 54                	push   %r12
     9de:	49 89 cc             	mov    %rcx,%r12
     9e1:	53                   	push   %rbx
     9e2:	48 89 d3             	mov    %rdx,%rbx
     9e5:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
     9e9:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
     9ed:	48 39 c2             	cmp    %rax,%rdx
     9f0:	48 0f 47 d0          	cmova  %rax,%rdx
     9f4:	31 c0                	xor    %eax,%eax
     9f6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
     9fd:	00 00 00 
     a00:	0f 18 04 03          	prefetchnta (%rbx,%rax,1)
     a04:	48 83 c0 40          	add    $0x40,%rax
     a08:	48 39 d0             	cmp    %rdx,%rax
     a0b:	72 f3                	jb     a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x40>
     a0d:	49 89 d9             	mov    %rbx,%r9
     a10:	4c 89 e2             	mov    %r12,%rdx
     a13:	31 c9                	xor    %ecx,%ecx
     a15:	eb 53                	jmp    a6a <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xaa>
     a17:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
     a1e:	00 00 
     a20:	41 0f b6 41 01       	movzbl 0x1(%r9),%eax
     a25:	45 0f b6 51 02       	movzbl 0x2(%r9),%r10d
     a2a:	48 ff c1             	inc    %rcx
     a2d:	48 83 c2 03          	add    $0x3,%rdx
     a31:	49 83 c1 03          	add    $0x3,%r9
     a35:	41 c1 e2 10          	shl    $0x10,%r10d
     a39:	c1 e0 08             	shl    $0x8,%eax
     a3c:	44 09 d0             	or     %r10d,%eax
     a3f:	45 0f b6 51 fd       	movzbl -0x3(%r9),%r10d
     a44:	44 09 d0             	or     %r10d,%eax
     a47:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
     a4b:	4c 8d 14 86          	lea    (%rsi,%rax,4),%r10
     a4f:	41 8b 02             	mov    (%r10),%eax
     a52:	45 0f b7 12          	movzwl (%r10),%r10d
     a56:	c1 e8 10             	shr    $0x10,%eax
     a59:	66 44 89 52 fd       	mov    %r10w,-0x3(%rdx)
     a5e:	88 42 ff             	mov    %al,-0x1(%rdx)
     a61:	49 39 c8             	cmp    %rcx,%r8
     a64:	0f 84 ae 0f 00 00    	je     1a18 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1058>
     a6a:	f6 c2 3f             	test   $0x3f,%dl
     a6d:	75 b1                	jne    a20 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
     a6f:	48 8d 41 48          	lea    0x48(%rcx),%rax
     a73:	49 39 c0             	cmp    %rax,%r8
     a76:	0f 82 a5 0f 00 00    	jb     1a21 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1061>
     a7c:	48 8d 04 49          	lea    (%rcx,%rcx,2),%rax
     a80:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # a88 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xc8>
     a87:	00 
     a88:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # a90 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd0>
     a8f:	00 
     a90:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
     a95:	49 8d 14 04          	lea    (%r12,%rax,1),%rdx
     a99:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
     a9e:	48 8d 84 03 00 04 00 	lea    0x400(%rbx,%rax,1),%rax
     aa5:	00 
     aa6:	eb 0b                	jmp    ab3 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf3>
     aa8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
     aaf:	00 
     ab0:	4c 89 c9             	mov    %r9,%rcx
     ab3:	4c 8d 89 96 01 00 00 	lea    0x196(%rcx),%r9
     aba:	4d 39 c8             	cmp    %r9,%r8
     abd:	72 15                	jb     ad4 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x114>
     abf:	0f 18 00             	prefetchnta (%rax)
     ac2:	0f 18 40 40          	prefetchnta 0x40(%rax)
     ac6:	0f 18 80 80 00 00 00 	prefetchnta 0x80(%rax)
     acd:	0f 18 80 bf 00 00 00 	prefetchnta 0xbf(%rax)
     ad4:	44 8b 88 00 fc ff ff 	mov    -0x400(%rax),%r9d
     adb:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ae2:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     ae7:	44 8b 88 03 fc ff ff 	mov    -0x3fd(%rax),%r9d
     aee:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     af5:	c4 21 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm9
     afb:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     b00:	44 8b 88 06 fc ff ff 	mov    -0x3fa(%rax),%r9d
     b07:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b0e:	c4 23 31 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm9,%xmm9
     b15:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     b1a:	44 8b 88 09 fc ff ff 	mov    -0x3f7(%rax),%r9d
     b21:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b28:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     b2d:	44 8b 88 0c fc ff ff 	mov    -0x3f4(%rax),%r9d
     b34:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b3b:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     b40:	44 8b 88 0f fc ff ff 	mov    -0x3f1(%rax),%r9d
     b47:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b4e:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     b54:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     b59:	44 8b 88 12 fc ff ff 	mov    -0x3ee(%rax),%r9d
     b60:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b67:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     b6e:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     b73:	44 8b 88 15 fc ff ff 	mov    -0x3eb(%rax),%r9d
     b7a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     b81:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     b87:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     b8c:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     b93:	44 8b 88 18 fc ff ff 	mov    -0x3e8(%rax),%r9d
     b9a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ba1:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     ba5:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     bab:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     bb0:	44 8b 88 1b fc ff ff 	mov    -0x3e5(%rax),%r9d
     bb7:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     bbe:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bc5:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     bca:	44 8b 88 1e fc ff ff 	mov    -0x3e2(%rax),%r9d
     bd1:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     bd5:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     bdb:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     be2:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     be7:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     bec:	44 8b 88 21 fc ff ff 	mov    -0x3df(%rax),%r9d
     bf3:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     bf8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     bff:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     c04:	44 8b 88 24 fc ff ff 	mov    -0x3dc(%rax),%r9d
     c0b:	c4 a1 79 6e 34 9e    	vmovd  (%rsi,%r11,4),%xmm6
     c11:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c18:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     c1d:	44 8b 88 27 fc ff ff 	mov    -0x3d9(%rax),%r9d
     c24:	c4 a3 49 22 34 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm6,%xmm6
     c2b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c32:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     c38:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     c3d:	44 8b 88 2a fc ff ff 	mov    -0x3d6(%rax),%r9d
     c44:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c4b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     c52:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     c57:	44 8b 88 2d fc ff ff 	mov    -0x3d3(%rax),%r9d
     c5e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c65:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     c6b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     c70:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     c77:	44 8b 88 30 fc ff ff 	mov    -0x3d0(%rax),%r9d
     c7e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     c85:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     c89:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     c8f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     c94:	44 8b 88 33 fc ff ff 	mov    -0x3cd(%rax),%r9d
     c9b:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     ca2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ca9:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     cae:	44 8b 88 36 fc ff ff 	mov    -0x3ca(%rax),%r9d
     cb5:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     cb9:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     cbf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     cc6:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     ccb:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     cd0:	44 8b 88 39 fc ff ff 	mov    -0x3c7(%rax),%r9d
     cd7:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     cdc:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     ce0:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     ce6:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ced:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     cf3:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     cf8:	44 8b 88 3c fc ff ff 	mov    -0x3c4(%rax),%r9d
     cff:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d06:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     d0b:	44 8b 88 3f fc ff ff 	mov    -0x3c1(%rax),%r9d
     d12:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d19:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     d1e:	44 8b 88 42 fc ff ff 	mov    -0x3be(%rax),%r9d
     d25:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d2c:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     d31:	44 8b 88 45 fc ff ff 	mov    -0x3bb(%rax),%r9d
     d38:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d3f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     d44:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     d4a:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
     d50:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     d56:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     d5d:	44 8b 88 48 fc ff ff 	mov    -0x3b8(%rax),%r9d
     d64:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
     d6b:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     d72:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d79:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     d7e:	44 8b 88 4b fc ff ff 	mov    -0x3b5(%rax),%r9d
     d85:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     d89:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     d8f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     d96:	c4 21 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm8
     d9c:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     da1:	44 8b 88 4e fc ff ff 	mov    -0x3b2(%rax),%r9d
     da8:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     daf:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     db6:	c4 23 39 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm8,%xmm8
     dbd:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     dc2:	44 8b 88 51 fc ff ff 	mov    -0x3af(%rax),%r9d
     dc9:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     dcd:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     dd3:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     dda:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     ddf:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     de4:	44 8b 88 54 fc ff ff 	mov    -0x3ac(%rax),%r9d
     deb:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     df0:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     df4:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     dfa:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e01:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     e07:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     e0c:	44 8b 88 57 fc ff ff 	mov    -0x3a9(%rax),%r9d
     e13:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e1a:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     e20:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     e25:	44 8b 88 5a fc ff ff 	mov    -0x3a6(%rax),%r9d
     e2c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e33:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     e3a:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     e3f:	44 8b 88 5d fc ff ff 	mov    -0x3a3(%rax),%r9d
     e46:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e4d:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     e53:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     e58:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     e5f:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     e63:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     e69:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     e70:	44 8b 88 60 fc ff ff 	mov    -0x3a0(%rax),%r9d
     e77:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     e7e:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     e82:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     e87:	44 8b 88 63 fc ff ff 	mov    -0x39d(%rax),%r9d
     e8e:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     e94:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     e99:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ea0:	c4 a1 79 6e 3c 9e    	vmovd  (%rsi,%r11,4),%xmm7
     ea6:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     eab:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     eb0:	44 8b 88 66 fc ff ff 	mov    -0x39a(%rax),%r9d
     eb7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ebe:	c4 a3 41 22 3c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm7,%xmm7
     ec5:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     eca:	44 8b 88 69 fc ff ff 	mov    -0x397(%rax),%r9d
     ed1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ed8:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     edd:	44 8b 88 6c fc ff ff 	mov    -0x394(%rax),%r9d
     ee4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     eeb:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     ef0:	44 8b 88 6f fc ff ff 	mov    -0x391(%rax),%r9d
     ef7:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     efe:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
     f04:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     f09:	44 8b 88 72 fc ff ff 	mov    -0x38e(%rax),%r9d
     f10:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f17:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
     f1e:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
     f23:	44 8b 88 75 fc ff ff 	mov    -0x38b(%rax),%r9d
     f2a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f31:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
     f37:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
     f3c:	c4 a3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm1,%xmm1
     f43:	44 8b 88 78 fc ff ff 	mov    -0x388(%rax),%r9d
     f4a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f51:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     f55:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
     f5b:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
     f60:	44 8b 88 7b fc ff ff 	mov    -0x385(%rax),%r9d
     f67:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
     f6e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f75:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
     f7a:	44 8b 88 7e fc ff ff 	mov    -0x382(%rax),%r9d
     f81:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     f85:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     f8b:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     f92:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     f97:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
     f9c:	44 8b 88 81 fc ff ff 	mov    -0x37f(%rax),%r9d
     fa3:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     fa8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     faf:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
     fb4:	44 8b 88 84 fc ff ff 	mov    -0x37c(%rax),%r9d
     fbb:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
     fc1:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fc8:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
     fcd:	44 8b 88 87 fc ff ff 	mov    -0x379(%rax),%r9d
     fd4:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
     fdb:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     fe2:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
     fe8:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
     fed:	44 8b 88 8a fc ff ff 	mov    -0x376(%rax),%r9d
     ff4:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
     ffb:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1002:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    1007:	44 8b 88 8d fc ff ff 	mov    -0x373(%rax),%r9d
    100e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1015:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    101b:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1020:	c4 a3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm2,%xmm2
    1027:	44 8b 88 90 fc ff ff 	mov    -0x370(%rax),%r9d
    102e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1035:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    1039:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    103f:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    1044:	44 8b 88 93 fc ff ff 	mov    -0x36d(%rax),%r9d
    104b:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1052:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1059:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    105e:	44 8b 88 96 fc ff ff 	mov    -0x36a(%rax),%r9d
    1065:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    1069:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    106f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1076:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    107b:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1080:	44 8b 88 99 fc ff ff 	mov    -0x367(%rax),%r9d
    1087:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    108c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1093:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    1098:	44 8b 88 9c fc ff ff 	mov    -0x364(%rax),%r9d
    109f:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10a6:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    10ab:	44 8b 88 9f fc ff ff 	mov    -0x361(%rax),%r9d
    10b2:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10b9:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    10be:	44 8b 88 a2 fc ff ff 	mov    -0x35e(%rax),%r9d
    10c5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10cc:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    10d1:	44 8b 88 a5 fc ff ff 	mov    -0x35b(%rax),%r9d
    10d8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    10df:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    10e4:	c4 21 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm10
    10ea:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    10f0:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    10f6:	c4 23 29 22 14 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm10,%xmm10
    10fd:	44 8b 88 a8 fc ff ff 	mov    -0x358(%rax),%r9d
    1104:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    110b:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1112:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1119:	46 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%r11d
    111e:	44 8b 88 ab fc ff ff 	mov    -0x355(%rax),%r9d
    1125:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    112a:	c4 21 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm10
    1130:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1137:	46 0f b6 14 0f       	movzbl (%rdi,%r9,1),%r10d
    113c:	44 8b 88 ae fc ff ff 	mov    -0x352(%rax),%r9d
    1143:	c4 63 29 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm10,%xmm10
    114a:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1151:	46 0f b6 24 0f       	movzbl (%rdi,%r9,1),%r12d
    1156:	44 8b 88 b1 fc ff ff 	mov    -0x34f(%rax),%r9d
    115d:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    1162:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    1168:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    116e:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1175:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    117a:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    117f:	44 8b 88 b4 fc ff ff 	mov    -0x34c(%rax),%r9d
    1186:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    118b:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    1192:	4c 8d 91 88 00 00 00 	lea    0x88(%rcx),%r10
    1199:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11a0:	46 0f b6 34 0f       	movzbl (%rdi,%r9,1),%r14d
    11a5:	44 8b 88 b7 fc ff ff 	mov    -0x349(%rax),%r9d
    11ac:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11b3:	c4 21 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm10
    11b9:	46 0f b6 2c 0f       	movzbl (%rdi,%r9,1),%r13d
    11be:	44 8b 88 ba fc ff ff 	mov    -0x346(%rax),%r9d
    11c5:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11cc:	c4 23 29 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm10,%xmm10
    11d3:	46 0f b6 3c 0f       	movzbl (%rdi,%r9,1),%r15d
    11d8:	44 8b 88 bd fc ff ff 	mov    -0x343(%rax),%r9d
    11df:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    11e6:	c4 21 79 6e 1c be    	vmovd  (%rsi,%r15,4),%xmm11
    11ec:	48 81 c2 c0 00 00 00 	add    $0xc0,%rdx
    11f3:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    11f8:	c4 23 21 22 1c 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm11,%xmm11
    11ff:	4c 8d 49 40          	lea    0x40(%rcx),%r9
    1203:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    1208:	c4 21 79 6e 1c a6    	vmovd  (%rsi,%r12,4),%xmm11
    120e:	c4 63 21 22 1c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm11,%xmm11
    1215:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    121a:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    121f:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    1225:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    122b:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    1230:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    1236:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    123c:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1241:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    1246:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    124b:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1250:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    1256:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    125c:	c5 7d e7 8a 40 ff ff 	vmovntdq %ymm9,-0xc0(%rdx)
    1263:	ff 
    1264:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    1268:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    126c:	c5 fd e7 b2 60 ff ff 	vmovntdq %ymm6,-0xa0(%rdx)
    1273:	ff 
    1274:	c5 fd e7 6a 80       	vmovntdq %ymm5,-0x80(%rdx)
    1279:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    127d:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    1281:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    1287:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    128d:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    1293:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    1299:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    129e:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    12a2:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    12a8:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    12ae:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    12b4:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    12ba:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    12c0:	c5 fd e7 6a a0       	vmovntdq %ymm5,-0x60(%rdx)
    12c5:	c5 fd e7 42 c0       	vmovntdq %ymm0,-0x40(%rdx)
    12ca:	c5 fd e7 4a e0       	vmovntdq %ymm1,-0x20(%rdx)
    12cf:	48 05 c0 00 00 00    	add    $0xc0,%rax
    12d5:	4d 39 d0             	cmp    %r10,%r8
    12d8:	0f 83 d2 f7 ff ff    	jae    ab0 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xf0>
    12de:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    12e3:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    12e8:	48 8d 41 68          	lea    0x68(%rcx),%rax
    12ec:	0f ae f8             	sfence
    12ef:	49 39 c0             	cmp    %rax,%r8
    12f2:	0f 82 90 03 00 00    	jb     1688 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    12f8:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
    12fc:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1304 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x944>
    1303:	00 
    1304:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 130c <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x94c>
    130b:	00 
    130c:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    1311:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    1316:	48 8d 04 13          	lea    (%rbx,%rdx,1),%rax
    131a:	4c 01 e2             	add    %r12,%rdx
    131d:	0f 1f 00             	nopl   (%rax)
    1320:	8b 48 48             	mov    0x48(%rax),%ecx
    1323:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1329:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    132e:	8b 48 4b             	mov    0x4b(%rax),%ecx
    1331:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1337:	c4 a1 79 6e 2c 9e    	vmovd  (%rsi,%r11,4),%xmm5
    133d:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1342:	8b 48 4e             	mov    0x4e(%rax),%ecx
    1345:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    134b:	c4 a3 51 22 2c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm5,%xmm5
    1352:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    1357:	8b 48 51             	mov    0x51(%rax),%ecx
    135a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1360:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1364:	8b 48 54             	mov    0x54(%rax),%ecx
    1367:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    136d:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1372:	8b 48 57             	mov    0x57(%rax),%ecx
    1375:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    137b:	c4 a1 79 6e 04 b6    	vmovd  (%rsi,%r14,4),%xmm0
    1381:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1386:	8b 48 5a             	mov    0x5a(%rax),%ecx
    1389:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    138f:	c4 a3 79 22 04 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm0,%xmm0
    1396:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    139b:	8b 48 5d             	mov    0x5d(%rax),%ecx
    139e:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13a4:	c4 a1 79 6e 0c be    	vmovd  (%rsi,%r15,4),%xmm1
    13aa:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    13ae:	c4 e3 71 22 0c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm1,%xmm1
    13b5:	8b 48 30             	mov    0x30(%rax),%ecx
    13b8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13be:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    13c2:	c4 a1 79 6e 0c a6    	vmovd  (%rsi,%r12,4),%xmm1
    13c8:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    13cd:	8b 48 33             	mov    0x33(%rax),%ecx
    13d0:	c4 e3 71 22 0c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm1,%xmm1
    13d7:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13dd:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    13e2:	8b 48 36             	mov    0x36(%rax),%ecx
    13e5:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    13e9:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    13ef:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    13f5:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    13fa:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    13ff:	8b 48 39             	mov    0x39(%rax),%ecx
    1402:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1407:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    140d:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    1411:	8b 48 3c             	mov    0x3c(%rax),%ecx
    1414:	c4 a1 79 6e 04 9e    	vmovd  (%rsi,%r11,4),%xmm0
    141a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1420:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    1425:	8b 48 3f             	mov    0x3f(%rax),%ecx
    1428:	c4 a3 79 22 04 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm0,%xmm0
    142f:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1435:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    143b:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    1440:	8b 48 42             	mov    0x42(%rax),%ecx
    1443:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1449:	c4 a3 71 22 0c ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm1,%xmm1
    1450:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    1455:	8b 48 45             	mov    0x45(%rax),%ecx
    1458:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    145e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1464:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    1468:	c4 e3 69 22 14 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm2,%xmm2
    146f:	8b 48 18             	mov    0x18(%rax),%ecx
    1472:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1478:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    147c:	c4 a1 79 6e 14 a6    	vmovd  (%rsi,%r12,4),%xmm2
    1482:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1487:	8b 48 1b             	mov    0x1b(%rax),%ecx
    148a:	c4 e3 69 22 14 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm2,%xmm2
    1491:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1497:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    149c:	8b 48 1e             	mov    0x1e(%rax),%ecx
    149f:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    14a3:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    14a9:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14af:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    14b4:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    14b9:	8b 48 21             	mov    0x21(%rax),%ecx
    14bc:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    14c1:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    14c5:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    14cb:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14d1:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    14d5:	8b 48 24             	mov    0x24(%rax),%ecx
    14d8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14de:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    14e3:	8b 48 27             	mov    0x27(%rax),%ecx
    14e6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14ec:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    14f1:	8b 48 2a             	mov    0x2a(%rax),%ecx
    14f4:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14fa:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    14ff:	8b 48 2d             	mov    0x2d(%rax),%ecx
    1502:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1508:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    150c:	c4 a1 79 6e 34 be    	vmovd  (%rsi,%r15,4),%xmm6
    1512:	c4 a1 79 6e 0c 9e    	vmovd  (%rsi,%r11,4),%xmm1
    1518:	c4 a1 79 6e 14 b6    	vmovd  (%rsi,%r14,4),%xmm2
    151e:	c4 e3 49 22 34 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm6,%xmm6
    1525:	8b 08                	mov    (%rax),%ecx
    1527:	c4 a3 71 22 0c 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm1,%xmm1
    152e:	c4 a3 69 22 14 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm2,%xmm2
    1535:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    153b:	44 0f b6 1c 0f       	movzbl (%rdi,%rcx,1),%r11d
    1540:	8b 48 03             	mov    0x3(%rax),%ecx
    1543:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    1547:	c4 a1 79 6e 34 a6    	vmovd  (%rsi,%r12,4),%xmm6
    154d:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1553:	44 0f b6 14 0f       	movzbl (%rdi,%rcx,1),%r10d
    1558:	8b 48 06             	mov    0x6(%rax),%ecx
    155b:	c4 e3 49 22 34 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm6,%xmm6
    1562:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1568:	44 0f b6 24 0f       	movzbl (%rdi,%rcx,1),%r12d
    156d:	8b 48 09             	mov    0x9(%rax),%ecx
    1570:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    1574:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    157a:	c4 a1 79 6e 14 9e    	vmovd  (%rsi,%r11,4),%xmm2
    1580:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1586:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    158b:	0f b6 1c 0f          	movzbl (%rdi,%rcx,1),%ebx
    158f:	8b 48 0c             	mov    0xc(%rax),%ecx
    1592:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    1597:	c4 a3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%r10,4),%xmm2,%xmm2
    159e:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    15a2:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    15a8:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    15ae:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    15b4:	44 0f b6 34 0f       	movzbl (%rdi,%rcx,1),%r14d
    15b9:	8b 48 0f             	mov    0xf(%rax),%ecx
    15bc:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    15c2:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    15c8:	c4 a1 79 6e 34 b6    	vmovd  (%rsi,%r14,4),%xmm6
    15ce:	44 0f b6 2c 0f       	movzbl (%rdi,%rcx,1),%r13d
    15d3:	8b 48 12             	mov    0x12(%rax),%ecx
    15d6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    15dc:	c4 a3 49 22 34 ae 01 	vpinsrd $0x1,(%rsi,%r13,4),%xmm6,%xmm6
    15e3:	44 0f b6 3c 0f       	movzbl (%rdi,%rcx,1),%r15d
    15e8:	8b 48 15             	mov    0x15(%rax),%ecx
    15eb:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    15f1:	c4 a1 79 6e 3c be    	vmovd  (%rsi,%r15,4),%xmm7
    15f7:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
    15fb:	c4 e3 41 22 3c 8e 01 	vpinsrd $0x1,(%rsi,%rcx,4),%xmm7,%xmm7
    1602:	49 8d 49 48          	lea    0x48(%r9),%rcx
    1606:	49 83 c1 20          	add    $0x20,%r9
    160a:	48 83 c0 60          	add    $0x60,%rax
    160e:	48 83 c2 60          	add    $0x60,%rdx
    1612:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    1616:	c4 a1 79 6e 3c a6    	vmovd  (%rsi,%r12,4),%xmm7
    161c:	c4 e3 41 22 3c 9e 01 	vpinsrd $0x1,(%rsi,%rbx,4),%xmm7,%xmm7
    1623:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    1627:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    162b:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1631:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    1637:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    163d:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    1641:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    1646:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    164c:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    1651:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    1655:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    165b:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    1660:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    1666:	c5 fe 7f 52 a0       	vmovdqu %ymm2,-0x60(%rdx)
    166b:	c5 fe 7f 4a c0       	vmovdqu %ymm1,-0x40(%rdx)
    1670:	c5 fe 7f 42 e0       	vmovdqu %ymm0,-0x20(%rdx)
    1675:	49 39 c8             	cmp    %rcx,%r8
    1678:	0f 83 a2 fc ff ff    	jae    1320 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x960>
    167e:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    1683:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    1688:	4d 8d 59 08          	lea    0x8(%r9),%r11
    168c:	4d 39 d8             	cmp    %r11,%r8
    168f:	0f 82 4d 01 00 00    	jb     17e2 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe22>
    1695:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
    169a:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
    169e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 16a6 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xce6>
    16a5:	00 
    16a6:	4c 89 64 24 f0       	mov    %r12,-0x10(%rsp)
    16ab:	4a 8d 0c 13          	lea    (%rbx,%r10,1),%rcx
    16af:	4d 01 e2             	add    %r12,%r10
    16b2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    16b8:	4c 8b 21             	mov    (%rcx),%r12
    16bb:	48 8b 41 08          	mov    0x8(%rcx),%rax
    16bf:	49 83 c2 18          	add    $0x18,%r10
    16c3:	48 83 c1 18          	add    $0x18,%rcx
    16c7:	48 8b 51 f8          	mov    -0x8(%rcx),%rdx
    16cb:	4d 89 e1             	mov    %r12,%r9
    16ce:	4d 89 e5             	mov    %r12,%r13
    16d1:	49 89 c6             	mov    %rax,%r14
    16d4:	49 c1 ed 30          	shr    $0x30,%r13
    16d8:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    16df:	41 89 d7             	mov    %edx,%r15d
    16e2:	49 c1 ee 20          	shr    $0x20,%r14
    16e6:	42 0f b6 1c 0f       	movzbl (%rdi,%r9,1),%ebx
    16eb:	4d 89 e1             	mov    %r12,%r9
    16ee:	41 89 c4             	mov    %eax,%r12d
    16f1:	41 c1 e7 08          	shl    $0x8,%r15d
    16f5:	41 c1 e4 10          	shl    $0x10,%r12d
    16f9:	41 81 e6 ff ff ff 00 	and    $0xffffff,%r14d
    1700:	49 c1 e9 18          	shr    $0x18,%r9
    1704:	45 09 ec             	or     %r13d,%r12d
    1707:	46 0f b6 34 37       	movzbl (%rdi,%r14,1),%r14d
    170c:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
    1713:	c5 f9 6e 04 9e       	vmovd  (%rsi,%rbx,4),%xmm0
    1718:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
    171f:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
    1724:	46 0f b6 2c 27       	movzbl (%rdi,%r12,1),%r13d
    1729:	41 89 c4             	mov    %eax,%r12d
    172c:	48 c1 e8 38          	shr    $0x38,%rax
    1730:	c4 a1 79 6e 0c b6    	vmovd  (%rsi,%r14,4),%xmm1
    1736:	41 09 c7             	or     %eax,%r15d
    1739:	41 c1 ec 08          	shr    $0x8,%r12d
    173d:	c4 a3 79 22 04 8e 01 	vpinsrd $0x1,(%rsi,%r9,4),%xmm0,%xmm0
    1744:	4d 89 d9             	mov    %r11,%r9
    1747:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    174e:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
    1753:	49 83 c3 08          	add    $0x8,%r11
    1757:	42 0f b6 04 3f       	movzbl (%rdi,%r15,1),%eax
    175c:	49 89 d7             	mov    %rdx,%r15
    175f:	48 c1 ea 28          	shr    $0x28,%rdx
    1763:	49 c1 ef 10          	shr    $0x10,%r15
    1767:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    176b:	41 81 e7 ff ff ff 00 	and    $0xffffff,%r15d
    1772:	c4 e3 71 22 0c 86 01 	vpinsrd $0x1,(%rsi,%rax,4),%xmm1,%xmm1
    1779:	46 0f b6 3c 3f       	movzbl (%rdi,%r15,1),%r15d
    177e:	c4 a1 79 6e 14 be    	vmovd  (%rsi,%r15,4),%xmm2
    1784:	c4 e3 69 22 14 96 01 	vpinsrd $0x1,(%rsi,%rdx,4),%xmm2,%xmm2
    178b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    178f:	c4 a1 79 6e 14 ae    	vmovd  (%rsi,%r13,4),%xmm2
    1795:	c4 a3 69 22 14 a6 01 	vpinsrd $0x1,(%rsi,%r12,4),%xmm2,%xmm2
    179c:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    17a0:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    17a6:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    17ab:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    17af:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    17b5:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    17ba:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    17bf:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    17c3:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    17c9:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    17cf:	4d 39 d8             	cmp    %r11,%r8
    17d2:	0f 83 e0 fe ff ff    	jae    16b8 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcf8>
    17d8:	48 8b 5c 24 f8       	mov    -0x8(%rsp),%rbx
    17dd:	4c 8b 64 24 f0       	mov    -0x10(%rsp),%r12
    17e2:	4d 39 c1             	cmp    %r8,%r9
    17e5:	0f 83 15 02 00 00    	jae    1a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    17eb:	4b 8d 04 49          	lea    (%r9,%r9,2),%rax
    17ef:	4c 8d 14 03          	lea    (%rbx,%rax,1),%r10
    17f3:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    17f8:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    17fd:	45 0f b6 12          	movzbl (%r10),%r10d
    1801:	c1 e2 08             	shl    $0x8,%edx
    1804:	41 c1 e3 10          	shl    $0x10,%r11d
    1808:	44 09 da             	or     %r11d,%edx
    180b:	44 09 d2             	or     %r10d,%edx
    180e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1812:	4c 8d 14 96          	lea    (%rsi,%rdx,4),%r10
    1816:	41 8b 12             	mov    (%r10),%edx
    1819:	45 0f b7 12          	movzwl (%r10),%r10d
    181d:	c1 ea 10             	shr    $0x10,%edx
    1820:	66 45 89 14 04       	mov    %r10w,(%r12,%rax,1)
    1825:	41 88 54 04 02       	mov    %dl,0x2(%r12,%rax,1)
    182a:	49 8d 51 01          	lea    0x1(%r9),%rdx
    182e:	4c 39 c2             	cmp    %r8,%rdx
    1831:	0f 83 c9 01 00 00    	jae    1a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1837:	4c 8d 54 03 03       	lea    0x3(%rbx,%rax,1),%r10
    183c:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    1841:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1846:	45 0f b6 12          	movzbl (%r10),%r10d
    184a:	41 c1 e3 10          	shl    $0x10,%r11d
    184e:	c1 e2 08             	shl    $0x8,%edx
    1851:	44 09 da             	or     %r11d,%edx
    1854:	44 09 d2             	or     %r10d,%edx
    1857:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    185b:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    185f:	44 8b 12             	mov    (%rdx),%r10d
    1862:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1866:	49 8d 51 02          	lea    0x2(%r9),%rdx
    186a:	44 89 d1             	mov    %r10d,%ecx
    186d:	66 45 89 5c 04 03    	mov    %r11w,0x3(%r12,%rax,1)
    1873:	c1 e9 10             	shr    $0x10,%ecx
    1876:	41 88 4c 04 05       	mov    %cl,0x5(%r12,%rax,1)
    187b:	4c 39 c2             	cmp    %r8,%rdx
    187e:	0f 83 7c 01 00 00    	jae    1a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    1884:	4c 8d 54 03 06       	lea    0x6(%rbx,%rax,1),%r10
    1889:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    188e:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    1893:	45 0f b6 12          	movzbl (%r10),%r10d
    1897:	41 c1 e3 10          	shl    $0x10,%r11d
    189b:	c1 e2 08             	shl    $0x8,%edx
    189e:	44 09 da             	or     %r11d,%edx
    18a1:	44 09 d2             	or     %r10d,%edx
    18a4:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    18a8:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    18ac:	44 8b 12             	mov    (%rdx),%r10d
    18af:	44 0f b7 1a          	movzwl (%rdx),%r11d
    18b3:	49 8d 51 03          	lea    0x3(%r9),%rdx
    18b7:	44 89 d1             	mov    %r10d,%ecx
    18ba:	66 45 89 5c 04 06    	mov    %r11w,0x6(%r12,%rax,1)
    18c0:	c1 e9 10             	shr    $0x10,%ecx
    18c3:	41 88 4c 04 08       	mov    %cl,0x8(%r12,%rax,1)
    18c8:	4c 39 c2             	cmp    %r8,%rdx
    18cb:	0f 83 2f 01 00 00    	jae    1a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    18d1:	4c 8d 54 03 09       	lea    0x9(%rbx,%rax,1),%r10
    18d6:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    18db:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    18e0:	45 0f b6 12          	movzbl (%r10),%r10d
    18e4:	41 c1 e3 08          	shl    $0x8,%r11d
    18e8:	c1 e2 10             	shl    $0x10,%edx
    18eb:	44 09 da             	or     %r11d,%edx
    18ee:	44 09 d2             	or     %r10d,%edx
    18f1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    18f5:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    18f9:	44 8b 12             	mov    (%rdx),%r10d
    18fc:	44 0f b7 1a          	movzwl (%rdx),%r11d
    1900:	49 8d 51 04          	lea    0x4(%r9),%rdx
    1904:	44 89 d1             	mov    %r10d,%ecx
    1907:	66 45 89 5c 04 09    	mov    %r11w,0x9(%r12,%rax,1)
    190d:	c1 e9 10             	shr    $0x10,%ecx
    1910:	41 88 4c 04 0b       	mov    %cl,0xb(%r12,%rax,1)
    1915:	4c 39 c2             	cmp    %r8,%rdx
    1918:	0f 83 e2 00 00 00    	jae    1a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    191e:	4c 8d 54 03 0c       	lea    0xc(%rbx,%rax,1),%r10
    1923:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1928:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    192d:	45 0f b6 12          	movzbl (%r10),%r10d
    1931:	41 c1 e3 08          	shl    $0x8,%r11d
    1935:	c1 e2 10             	shl    $0x10,%edx
    1938:	44 09 da             	or     %r11d,%edx
    193b:	44 09 d2             	or     %r10d,%edx
    193e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1942:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1946:	44 8b 12             	mov    (%rdx),%r10d
    1949:	44 0f b7 1a          	movzwl (%rdx),%r11d
    194d:	49 8d 51 05          	lea    0x5(%r9),%rdx
    1951:	44 89 d1             	mov    %r10d,%ecx
    1954:	66 45 89 5c 04 0c    	mov    %r11w,0xc(%r12,%rax,1)
    195a:	c1 e9 10             	shr    $0x10,%ecx
    195d:	41 88 4c 04 0e       	mov    %cl,0xe(%r12,%rax,1)
    1962:	4c 39 c2             	cmp    %r8,%rdx
    1965:	0f 83 95 00 00 00    	jae    1a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    196b:	4c 8d 54 03 0f       	lea    0xf(%rbx,%rax,1),%r10
    1970:	49 83 c1 06          	add    $0x6,%r9
    1974:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    1979:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    197e:	45 0f b6 12          	movzbl (%r10),%r10d
    1982:	41 c1 e3 08          	shl    $0x8,%r11d
    1986:	c1 e2 10             	shl    $0x10,%edx
    1989:	44 09 da             	or     %r11d,%edx
    198c:	44 09 d2             	or     %r10d,%edx
    198f:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
    1993:	48 8d 14 96          	lea    (%rsi,%rdx,4),%rdx
    1997:	44 8b 12             	mov    (%rdx),%r10d
    199a:	44 0f b7 1a          	movzwl (%rdx),%r11d
    199e:	44 89 d1             	mov    %r10d,%ecx
    19a1:	66 45 89 5c 04 0f    	mov    %r11w,0xf(%r12,%rax,1)
    19a7:	c1 e9 10             	shr    $0x10,%ecx
    19aa:	41 88 4c 04 11       	mov    %cl,0x11(%r12,%rax,1)
    19af:	4d 39 c1             	cmp    %r8,%r9
    19b2:	73 4c                	jae    1a00 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1040>
    19b4:	48 8d 54 03 12       	lea    0x12(%rbx,%rax,1),%rdx
    19b9:	4d 8d 44 04 12       	lea    0x12(%r12,%rax,1),%r8
    19be:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    19c2:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    19c6:	0f b6 12             	movzbl (%rdx),%edx
    19c9:	c1 e0 08             	shl    $0x8,%eax
    19cc:	c1 e1 10             	shl    $0x10,%ecx
    19cf:	09 c8                	or     %ecx,%eax
    19d1:	09 d0                	or     %edx,%eax
    19d3:	0f b6 04 07          	movzbl (%rdi,%rax,1),%eax
    19d7:	48 8d 14 86          	lea    (%rsi,%rax,4),%rdx
    19db:	8b 02                	mov    (%rdx),%eax
    19dd:	0f b7 12             	movzwl (%rdx),%edx
    19e0:	c1 e8 10             	shr    $0x10,%eax
    19e3:	66 41 89 10          	mov    %dx,(%r8)
    19e7:	41 88 40 02          	mov    %al,0x2(%r8)
    19eb:	c5 f8 77             	vzeroupper
    19ee:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    19f2:	5b                   	pop    %rbx
    19f3:	41 5c                	pop    %r12
    19f5:	41 5d                	pop    %r13
    19f7:	41 5e                	pop    %r14
    19f9:	41 5f                	pop    %r15
    19fb:	5d                   	pop    %rbp
    19fc:	c3                   	ret
    19fd:	0f 1f 00             	nopl   (%rax)
    1a00:	c5 f8 77             	vzeroupper
    1a03:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    1a07:	5b                   	pop    %rbx
    1a08:	41 5c                	pop    %r12
    1a0a:	41 5d                	pop    %r13
    1a0c:	41 5e                	pop    %r14
    1a0e:	41 5f                	pop    %r15
    1a10:	5d                   	pop    %rbp
    1a11:	c3                   	ret
    1a12:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    1a18:	4d 89 c1             	mov    %r8,%r9
    1a1b:	e9 68 fc ff ff       	jmp    1688 <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xcc8>
    1a20:	c3                   	ret
    1a21:	48 8d 41 28          	lea    0x28(%rcx),%rax
    1a25:	49 89 c9             	mov    %rcx,%r9
    1a28:	e9 c2 f8 ff ff       	jmp    12ef <jshc_channel::avx2_chain_overlap_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x92f>
