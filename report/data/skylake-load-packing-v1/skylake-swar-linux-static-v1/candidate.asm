
artifacts/skylake-swar-linux-build-v1/CMakeFiles/jshc_skylake_swar.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_swar(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	53                   	push   %rbx
   5:	49 89 d0             	mov    %rdx,%r8
   8:	48 83 f9 0f          	cmp    $0xf,%rcx
   c:	0f 86 16 02 00 00    	jbe    228 <jshc_channel::avx2_chain_swar(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x228>
  12:	4c 8d 49 f0          	lea    -0x10(%rcx),%r9
  16:	48 89 d0             	mov    %rdx,%rax
  19:	4c 89 ca             	mov    %r9,%rdx
  1c:	48 c1 ea 03          	shr    $0x3,%rdx
  20:	48 8d 14 52          	lea    (%rdx,%rdx,2),%rdx
  24:	4d 8d 54 d0 18       	lea    0x18(%r8,%rdx,8),%r10
  29:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  30:	8b 50 06             	mov    0x6(%rax),%edx
  33:	48 83 c0 18          	add    $0x18,%rax
  37:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  3d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
  41:	8b 1c 96             	mov    (%rsi,%rdx,4),%ebx
  44:	8b 50 eb             	mov    -0x15(%rax),%edx
  47:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  4d:	49 89 db             	mov    %rbx,%r11
  50:	c1 eb 10             	shr    $0x10,%ebx
  53:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
  57:	49 c1 e3 30          	shl    $0x30,%r11
  5b:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
  5e:	48 c1 e2 18          	shl    $0x18,%rdx
  62:	4c 09 da             	or     %r11,%rdx
  65:	44 8b 58 e8          	mov    -0x18(%rax),%r11d
  69:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
  70:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
  75:	46 8b 1c 9e          	mov    (%rsi,%r11,4),%r11d
  79:	4c 09 da             	or     %r11,%rdx
  7c:	48 89 50 e8          	mov    %rdx,-0x18(%rax)
  80:	8b 50 f7             	mov    -0x9(%rax),%edx
  83:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  89:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
  8d:	44 8b 1c 96          	mov    (%rsi,%rdx,4),%r11d
  91:	8b 50 f1             	mov    -0xf(%rax),%edx
  94:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  9a:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
  9e:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
  a1:	48 c1 e2 08          	shl    $0x8,%rdx
  a5:	48 09 da             	or     %rbx,%rdx
  a8:	8b 58 f4             	mov    -0xc(%rax),%ebx
  ab:	81 e3 ff ff ff 00    	and    $0xffffff,%ebx
  b1:	0f b6 1c 1f          	movzbl (%rdi,%rbx,1),%ebx
  b5:	8b 1c 9e             	mov    (%rsi,%rbx,4),%ebx
  b8:	48 c1 e3 20          	shl    $0x20,%rbx
  bc:	48 09 da             	or     %rbx,%rdx
  bf:	4c 89 db             	mov    %r11,%rbx
  c2:	41 c1 eb 08          	shr    $0x8,%r11d
  c6:	48 c1 e3 38          	shl    $0x38,%rbx
  ca:	48 09 da             	or     %rbx,%rdx
  cd:	48 89 50 f0          	mov    %rdx,-0x10(%rax)
  d1:	8b 50 fa             	mov    -0x6(%rax),%edx
  d4:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
  da:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
  de:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
  e1:	48 c1 e2 10          	shl    $0x10,%rdx
  e5:	4c 09 da             	or     %r11,%rdx
  e8:	44 8b 58 fd          	mov    -0x3(%rax),%r11d
  ec:	41 81 e3 ff ff ff 00 	and    $0xffffff,%r11d
  f3:	46 0f b6 1c 1f       	movzbl (%rdi,%r11,1),%r11d
  f8:	46 8b 1c 9e          	mov    (%rsi,%r11,4),%r11d
  fc:	49 c1 e3 28          	shl    $0x28,%r11
 100:	4c 09 da             	or     %r11,%rdx
 103:	48 89 50 f8          	mov    %rdx,-0x8(%rax)
 107:	49 39 c2             	cmp    %rax,%r10
 10a:	0f 85 20 ff ff ff    	jne    30 <jshc_channel::avx2_chain_swar(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x30>
 110:	49 83 e1 f8          	and    $0xfffffffffffffff8,%r9
 114:	49 83 c1 08          	add    $0x8,%r9
 118:	49 39 c9             	cmp    %rcx,%r9
 11b:	0f 83 01 01 00 00    	jae    222 <jshc_channel::avx2_chain_swar(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x222>
 121:	48 ff c9             	dec    %rcx
 124:	4b 8d 14 49          	lea    (%r9,%r9,2),%rdx
 128:	4c 29 c9             	sub    %r9,%rcx
 12b:	49 8d 04 10          	lea    (%r8,%rdx,1),%rax
 12f:	49 8d 54 10 18       	lea    0x18(%r8,%rdx,1),%rdx
 134:	48 c1 e9 03          	shr    $0x3,%rcx
 138:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
 13c:	4c 8d 04 ca          	lea    (%rdx,%rcx,8),%r8
 140:	8b 50 06             	mov    0x6(%rax),%edx
 143:	48 83 c0 18          	add    $0x18,%rax
 147:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 14d:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 151:	44 8b 0c 96          	mov    (%rsi,%rdx,4),%r9d
 155:	8b 50 eb             	mov    -0x15(%rax),%edx
 158:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 15e:	4c 89 c9             	mov    %r9,%rcx
 161:	41 c1 e9 10          	shr    $0x10,%r9d
 165:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 169:	48 c1 e1 30          	shl    $0x30,%rcx
 16d:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 170:	48 c1 e2 18          	shl    $0x18,%rdx
 174:	48 09 ca             	or     %rcx,%rdx
 177:	8b 48 e8             	mov    -0x18(%rax),%ecx
 17a:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 180:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 184:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
 187:	48 09 ca             	or     %rcx,%rdx
 18a:	48 89 50 e8          	mov    %rdx,-0x18(%rax)
 18e:	8b 50 f7             	mov    -0x9(%rax),%edx
 191:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 197:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 19b:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
 19e:	8b 50 f1             	mov    -0xf(%rax),%edx
 1a1:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 1a7:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 1ab:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 1ae:	48 c1 e2 08          	shl    $0x8,%rdx
 1b2:	4c 09 ca             	or     %r9,%rdx
 1b5:	44 8b 48 f4          	mov    -0xc(%rax),%r9d
 1b9:	41 81 e1 ff ff ff 00 	and    $0xffffff,%r9d
 1c0:	46 0f b6 0c 0f       	movzbl (%rdi,%r9,1),%r9d
 1c5:	46 8b 0c 8e          	mov    (%rsi,%r9,4),%r9d
 1c9:	49 c1 e1 20          	shl    $0x20,%r9
 1cd:	4c 09 ca             	or     %r9,%rdx
 1d0:	49 89 c9             	mov    %rcx,%r9
 1d3:	c1 e9 08             	shr    $0x8,%ecx
 1d6:	49 c1 e1 38          	shl    $0x38,%r9
 1da:	4c 09 ca             	or     %r9,%rdx
 1dd:	44 0f b7 48 fd       	movzwl -0x3(%rax),%r9d
 1e2:	48 89 50 f0          	mov    %rdx,-0x10(%rax)
 1e6:	8b 50 fa             	mov    -0x6(%rax),%edx
 1e9:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 1ef:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 1f3:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 1f6:	48 c1 e2 10          	shl    $0x10,%rdx
 1fa:	48 09 ca             	or     %rcx,%rdx
 1fd:	0f b6 48 ff          	movzbl -0x1(%rax),%ecx
 201:	c1 e1 10             	shl    $0x10,%ecx
 204:	44 09 c9             	or     %r9d,%ecx
 207:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 20b:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
 20e:	48 c1 e1 28          	shl    $0x28,%rcx
 212:	48 09 ca             	or     %rcx,%rdx
 215:	48 89 50 f8          	mov    %rdx,-0x8(%rax)
 219:	49 39 c0             	cmp    %rax,%r8
 21c:	0f 85 1e ff ff ff    	jne    140 <jshc_channel::avx2_chain_swar(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x140>
 222:	5b                   	pop    %rbx
 223:	c3                   	ret
 224:	0f 1f 40 00          	nopl   0x0(%rax)
 228:	45 31 c9             	xor    %r9d,%r9d
 22b:	e9 e8 fe ff ff       	jmp    118 <jshc_channel::avx2_chain_swar(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x118>

0000000000000230 <jshc_channel::avx2_chain_swar_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
 230:	f3 0f 1e fa          	endbr64
 234:	41 54                	push   %r12
 236:	49 89 d2             	mov    %rdx,%r10
 239:	49 89 c9             	mov    %rcx,%r9
 23c:	55                   	push   %rbp
 23d:	53                   	push   %rbx
 23e:	49 83 f8 0f          	cmp    $0xf,%r8
 242:	0f 86 20 02 00 00    	jbe    468 <jshc_channel::avx2_chain_swar_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x238>
 248:	4d 8d 58 f0          	lea    -0x10(%r8),%r11
 24c:	48 89 d0             	mov    %rdx,%rax
 24f:	4c 89 da             	mov    %r11,%rdx
 252:	48 c1 ea 03          	shr    $0x3,%rdx
 256:	48 8d 14 52          	lea    (%rdx,%rdx,2),%rdx
 25a:	49 8d 5c d2 18       	lea    0x18(%r10,%rdx,8),%rbx
 25f:	90                   	nop
 260:	8b 50 06             	mov    0x6(%rax),%edx
 263:	48 83 c0 18          	add    $0x18,%rax
 267:	48 83 c1 18          	add    $0x18,%rcx
 26b:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 271:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 275:	44 8b 24 96          	mov    (%rsi,%rdx,4),%r12d
 279:	8b 50 eb             	mov    -0x15(%rax),%edx
 27c:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 282:	4c 89 e5             	mov    %r12,%rbp
 285:	41 c1 ec 10          	shr    $0x10,%r12d
 289:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 28d:	48 c1 e5 30          	shl    $0x30,%rbp
 291:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 294:	48 c1 e2 18          	shl    $0x18,%rdx
 298:	48 09 ea             	or     %rbp,%rdx
 29b:	8b 68 e8             	mov    -0x18(%rax),%ebp
 29e:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
 2a4:	0f b6 2c 2f          	movzbl (%rdi,%rbp,1),%ebp
 2a8:	8b 2c ae             	mov    (%rsi,%rbp,4),%ebp
 2ab:	48 09 ea             	or     %rbp,%rdx
 2ae:	48 89 51 e8          	mov    %rdx,-0x18(%rcx)
 2b2:	8b 50 f7             	mov    -0x9(%rax),%edx
 2b5:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 2bb:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 2bf:	8b 2c 96             	mov    (%rsi,%rdx,4),%ebp
 2c2:	8b 50 f1             	mov    -0xf(%rax),%edx
 2c5:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 2cb:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 2cf:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 2d2:	48 c1 e2 08          	shl    $0x8,%rdx
 2d6:	4c 09 e2             	or     %r12,%rdx
 2d9:	44 8b 60 f4          	mov    -0xc(%rax),%r12d
 2dd:	41 81 e4 ff ff ff 00 	and    $0xffffff,%r12d
 2e4:	46 0f b6 24 27       	movzbl (%rdi,%r12,1),%r12d
 2e9:	46 8b 24 a6          	mov    (%rsi,%r12,4),%r12d
 2ed:	49 c1 e4 20          	shl    $0x20,%r12
 2f1:	4c 09 e2             	or     %r12,%rdx
 2f4:	49 89 ec             	mov    %rbp,%r12
 2f7:	c1 ed 08             	shr    $0x8,%ebp
 2fa:	49 c1 e4 38          	shl    $0x38,%r12
 2fe:	4c 09 e2             	or     %r12,%rdx
 301:	48 89 51 f0          	mov    %rdx,-0x10(%rcx)
 305:	8b 50 fa             	mov    -0x6(%rax),%edx
 308:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 30e:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 312:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 315:	48 c1 e2 10          	shl    $0x10,%rdx
 319:	48 09 ea             	or     %rbp,%rdx
 31c:	8b 68 fd             	mov    -0x3(%rax),%ebp
 31f:	81 e5 ff ff ff 00    	and    $0xffffff,%ebp
 325:	0f b6 2c 2f          	movzbl (%rdi,%rbp,1),%ebp
 329:	8b 2c ae             	mov    (%rsi,%rbp,4),%ebp
 32c:	48 c1 e5 28          	shl    $0x28,%rbp
 330:	48 09 ea             	or     %rbp,%rdx
 333:	48 89 51 f8          	mov    %rdx,-0x8(%rcx)
 337:	48 39 c3             	cmp    %rax,%rbx
 33a:	0f 85 20 ff ff ff    	jne    260 <jshc_channel::avx2_chain_swar_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x30>
 340:	49 83 e3 f8          	and    $0xfffffffffffffff8,%r11
 344:	49 83 c3 08          	add    $0x8,%r11
 348:	4d 39 c3             	cmp    %r8,%r11
 34b:	0f 83 0d 01 00 00    	jae    45e <jshc_channel::avx2_chain_swar_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x22e>
 351:	49 ff c8             	dec    %r8
 354:	4b 8d 14 5b          	lea    (%r11,%r11,2),%rdx
 358:	4d 29 d8             	sub    %r11,%r8
 35b:	49 8d 04 12          	lea    (%r10,%rdx,1),%rax
 35f:	49 01 d1             	add    %rdx,%r9
 362:	49 c1 e8 03          	shr    $0x3,%r8
 366:	49 8d 54 12 18       	lea    0x18(%r10,%rdx,1),%rdx
 36b:	4b 8d 0c 40          	lea    (%r8,%r8,2),%rcx
 36f:	4c 8d 04 ca          	lea    (%rdx,%rcx,8),%r8
 373:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 378:	8b 50 06             	mov    0x6(%rax),%edx
 37b:	48 83 c0 18          	add    $0x18,%rax
 37f:	49 83 c1 18          	add    $0x18,%r9
 383:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 389:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 38d:	44 8b 14 96          	mov    (%rsi,%rdx,4),%r10d
 391:	8b 50 eb             	mov    -0x15(%rax),%edx
 394:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 39a:	4c 89 d1             	mov    %r10,%rcx
 39d:	41 c1 ea 10          	shr    $0x10,%r10d
 3a1:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 3a5:	48 c1 e1 30          	shl    $0x30,%rcx
 3a9:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 3ac:	48 c1 e2 18          	shl    $0x18,%rdx
 3b0:	48 09 ca             	or     %rcx,%rdx
 3b3:	8b 48 e8             	mov    -0x18(%rax),%ecx
 3b6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
 3bc:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 3c0:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
 3c3:	48 09 ca             	or     %rcx,%rdx
 3c6:	49 89 51 e8          	mov    %rdx,-0x18(%r9)
 3ca:	8b 50 f7             	mov    -0x9(%rax),%edx
 3cd:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 3d3:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 3d7:	8b 0c 96             	mov    (%rsi,%rdx,4),%ecx
 3da:	8b 50 f1             	mov    -0xf(%rax),%edx
 3dd:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 3e3:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 3e7:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 3ea:	48 c1 e2 08          	shl    $0x8,%rdx
 3ee:	4c 09 d2             	or     %r10,%rdx
 3f1:	44 8b 50 f4          	mov    -0xc(%rax),%r10d
 3f5:	41 81 e2 ff ff ff 00 	and    $0xffffff,%r10d
 3fc:	46 0f b6 14 17       	movzbl (%rdi,%r10,1),%r10d
 401:	46 8b 14 96          	mov    (%rsi,%r10,4),%r10d
 405:	49 c1 e2 20          	shl    $0x20,%r10
 409:	4c 09 d2             	or     %r10,%rdx
 40c:	49 89 ca             	mov    %rcx,%r10
 40f:	c1 e9 08             	shr    $0x8,%ecx
 412:	49 c1 e2 38          	shl    $0x38,%r10
 416:	4c 09 d2             	or     %r10,%rdx
 419:	49 89 51 f0          	mov    %rdx,-0x10(%r9)
 41d:	8b 50 fa             	mov    -0x6(%rax),%edx
 420:	44 0f b7 50 fd       	movzwl -0x3(%rax),%r10d
 425:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
 42b:	0f b6 14 17          	movzbl (%rdi,%rdx,1),%edx
 42f:	8b 14 96             	mov    (%rsi,%rdx,4),%edx
 432:	48 c1 e2 10          	shl    $0x10,%rdx
 436:	48 09 ca             	or     %rcx,%rdx
 439:	0f b6 48 ff          	movzbl -0x1(%rax),%ecx
 43d:	c1 e1 10             	shl    $0x10,%ecx
 440:	44 09 d1             	or     %r10d,%ecx
 443:	0f b6 0c 0f          	movzbl (%rdi,%rcx,1),%ecx
 447:	8b 0c 8e             	mov    (%rsi,%rcx,4),%ecx
 44a:	48 c1 e1 28          	shl    $0x28,%rcx
 44e:	48 09 ca             	or     %rcx,%rdx
 451:	49 89 51 f8          	mov    %rdx,-0x8(%r9)
 455:	49 39 c0             	cmp    %rax,%r8
 458:	0f 85 1a ff ff ff    	jne    378 <jshc_channel::avx2_chain_swar_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x148>
 45e:	5b                   	pop    %rbx
 45f:	5d                   	pop    %rbp
 460:	41 5c                	pop    %r12
 462:	c3                   	ret
 463:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 468:	45 31 db             	xor    %r11d,%r11d
 46b:	e9 d8 fe ff ff       	jmp    348 <jshc_channel::avx2_chain_swar_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x118>
