
artifacts/skylake-dictionary-linux-build-v1/CMakeFiles/jshc_skylake_dictionary.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	49 83 f8 1f          	cmp    $0x1f,%r8
   8:	0f 86 a2 03 00 00    	jbe    3b0 <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3b0>
   e:	4d 8d 48 e0          	lea    -0x20(%r8),%r9
  12:	c5 fd 76 c0          	vpcmpeqd %ymm0,%ymm0,%ymm0
  16:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 1e <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1e>
  1d:	00 
  1e:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 26 <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x26>
  25:	00 
  26:	c5 bd 72 d0 10       	vpsrld $0x10,%ymm0,%ymm8
  2b:	c5 c5 72 d0 1f       	vpsrld $0x1f,%ymm0,%ymm7
  30:	4d 89 ca             	mov    %r9,%r10
  33:	48 89 c8             	mov    %rcx,%rax
  36:	c5 cd 72 d0 1e       	vpsrld $0x1e,%ymm0,%ymm6
  3b:	49 c1 ea 05          	shr    $0x5,%r10
  3f:	c5 d5 72 d0 18       	vpsrld $0x18,%ymm0,%ymm5
  44:	4f 8d 14 52          	lea    (%r10,%r10,2),%r10
  48:	49 c1 e2 05          	shl    $0x5,%r10
  4c:	4e 8d 54 11 60       	lea    0x60(%rcx,%r10,1),%r10
  51:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  58:	c5 7a 6f 10          	vmovdqu (%rax),%xmm10
  5c:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
  61:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
  65:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
  69:	c5 7a 6f 48 18       	vmovdqu 0x18(%rax),%xmm9
  6e:	c5 fa 6f 50 30       	vmovdqu 0x30(%rax),%xmm2
  73:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
  77:	48 83 c0 60          	add    $0x60,%rax
  7b:	c4 c3 71 0f ca 0c    	vpalignr $0xc,%xmm10,%xmm1,%xmm1
  81:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
  86:	c4 63 2d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm10,%ymm10
  8c:	c5 fa 7e 48 c8       	vmovq  -0x38(%rax),%xmm1
  91:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
  96:	c4 c3 71 0f c9 0c    	vpalignr $0xc,%xmm9,%xmm1,%xmm1
  9c:	c4 63 35 38 c9 01    	vinserti128 $0x1,%xmm1,%ymm9,%ymm9
  a2:	c5 fa 7e 48 e0       	vmovq  -0x20(%rax),%xmm1
  a7:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
  ac:	c4 e3 71 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm1,%xmm1
  b2:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
  b8:	c5 fa 6f 48 e8       	vmovdqu -0x18(%rax),%xmm1
  bd:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
  c2:	c4 63 21 0f d9 0c    	vpalignr $0xc,%xmm1,%xmm11,%xmm11
  c8:	c4 c3 75 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm1,%ymm1
  ce:	c4 c1 25 72 d2 03    	vpsrld $0x3,%ymm10,%ymm11
  d4:	c4 22 15 90 24 5f    	vpgatherdd %ymm13,(%rdi,%ymm11,2),%ymm12
  da:	c4 c1 25 72 d2 02    	vpsrld $0x2,%ymm10,%ymm11
  e0:	c5 2d db d6          	vpand  %ymm6,%ymm10,%ymm10
  e4:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
  e9:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
  ed:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
  f1:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
  f7:	c4 c1 2d 72 f2 03    	vpslld $0x3,%ymm10,%ymm10
  fd:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
 102:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 107:	c4 22 0d 90 24 9e    	vpgatherdd %ymm14,(%rsi,%ymm11,4),%ymm12
 10d:	c4 c1 25 72 d1 03    	vpsrld $0x3,%ymm9,%ymm11
 113:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
 117:	c4 42 1d 45 d2       	vpsrlvd %ymm10,%ymm12,%ymm10
 11c:	c4 22 05 90 24 5f    	vpgatherdd %ymm15,(%rdi,%ymm11,2),%ymm12
 122:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
 126:	c4 c1 25 72 d1 02    	vpsrld $0x2,%ymm9,%ymm11
 12c:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
 131:	c5 35 db ce          	vpand  %ymm6,%ymm9,%ymm9
 135:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
 13b:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 141:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 145:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 14a:	c4 22 15 90 24 9e    	vpgatherdd %ymm13,(%rsi,%ymm11,4),%ymm12
 150:	c5 a5 72 d2 03       	vpsrld $0x3,%ymm2,%ymm11
 155:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
 159:	c4 42 1d 45 c9       	vpsrlvd %ymm9,%ymm12,%ymm9
 15e:	c4 22 0d 90 24 5f    	vpgatherdd %ymm14,(%rdi,%ymm11,2),%ymm12
 164:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
 168:	c5 a5 72 d2 02       	vpsrld $0x2,%ymm2,%ymm11
 16d:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
 172:	c5 ed db d6          	vpand  %ymm6,%ymm2,%ymm2
 176:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
 17c:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
 181:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 185:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 18a:	c4 22 05 90 24 9e    	vpgatherdd %ymm15,(%rsi,%ymm11,4),%ymm12
 190:	c5 a5 72 d1 03       	vpsrld $0x3,%ymm1,%ymm11
 195:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
 199:	c4 e2 1d 45 d2       	vpsrlvd %ymm2,%ymm12,%ymm2
 19e:	c4 22 15 90 24 5f    	vpgatherdd %ymm13,(%rdi,%ymm11,2),%ymm12
 1a4:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
 1a8:	c5 a5 72 d1 02       	vpsrld $0x2,%ymm1,%ymm11
 1ad:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
 1b2:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
 1b6:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
 1bc:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 1c1:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 1c5:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 1ca:	c4 22 0d 90 24 9e    	vpgatherdd %ymm14,(%rsi,%ymm11,4),%ymm12
 1d0:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
 1d4:	c4 62 1d 45 d9       	vpsrlvd %ymm1,%ymm12,%ymm11
 1d9:	c5 ad db cd          	vpand  %ymm5,%ymm10,%ymm1
 1dd:	c4 62 05 90 14 8a    	vpgatherdd %ymm15,(%rdx,%ymm1,4),%ymm10
 1e3:	c5 b5 db cd          	vpand  %ymm5,%ymm9,%ymm1
 1e7:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
 1eb:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
 1f0:	c4 62 15 90 0c 8a    	vpgatherdd %ymm13,(%rdx,%ymm1,4),%ymm9
 1f6:	c5 25 db dd          	vpand  %ymm5,%ymm11,%ymm11
 1fa:	c5 ed db cd          	vpand  %ymm5,%ymm2,%ymm1
 1fe:	c4 41 79 6f e2       	vmovdqa %xmm10,%xmm12
 203:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
 209:	c4 e2 0d 90 14 8a    	vpgatherdd %ymm14,(%rdx,%ymm1,4),%ymm2
 20f:	c4 a2 05 90 0c 9a    	vpgatherdd %ymm15,(%rdx,%ymm11,4),%ymm1
 215:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
 21a:	c4 c1 21 73 fa 0c    	vpslldq $0xc,%xmm10,%xmm11
 220:	c4 c1 29 73 da 04    	vpsrldq $0x4,%xmm10,%xmm10
 226:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
 22b:	c4 41 21 eb dc       	vpor   %xmm12,%xmm11,%xmm11
 230:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
 235:	c5 7a 7f 58 a0       	vmovdqu %xmm11,-0x60(%rax)
 23a:	c4 41 79 6f d9       	vmovdqa %xmm9,%xmm11
 23f:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
 245:	c5 79 d6 50 b0       	vmovq  %xmm10,-0x50(%rax)
 24a:	c4 c1 29 73 f9 0c    	vpslldq $0xc,%xmm9,%xmm10
 250:	c4 c1 31 73 d9 04    	vpsrldq $0x4,%xmm9,%xmm9
 256:	c4 41 29 eb d3       	vpor   %xmm11,%xmm10,%xmm10
 25b:	c5 79 d6 48 c8       	vmovq  %xmm9,-0x38(%rax)
 260:	c5 7a 7f 50 b8       	vmovdqu %xmm10,-0x48(%rax)
 265:	c5 79 6f d2          	vmovdqa %xmm2,%xmm10
 269:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
 26f:	c5 b1 73 fa 0c       	vpslldq $0xc,%xmm2,%xmm9
 274:	c5 e9 73 da 04       	vpsrldq $0x4,%xmm2,%xmm2
 279:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 27e:	c5 f9 d6 50 e0       	vmovq  %xmm2,-0x20(%rax)
 283:	c5 7a 7f 48 d0       	vmovdqu %xmm9,-0x30(%rax)
 288:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
 28c:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 292:	c5 e9 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm2
 297:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 29c:	c4 c1 69 eb d1       	vpor   %xmm9,%xmm2,%xmm2
 2a1:	c5 f9 d6 48 f8       	vmovq  %xmm1,-0x8(%rax)
 2a6:	c5 fa 7f 50 e8       	vmovdqu %xmm2,-0x18(%rax)
 2ab:	49 39 c2             	cmp    %rax,%r10
 2ae:	0f 85 a4 fd ff ff    	jne    58 <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x58>
 2b4:	49 83 e1 e0          	and    $0xffffffffffffffe0,%r9
 2b8:	49 83 c1 20          	add    $0x20,%r9
 2bc:	4d 39 c1             	cmp    %r8,%r9
 2bf:	0f 83 e7 00 00 00    	jae    3ac <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x3ac>
 2c5:	49 ff c8             	dec    %r8
 2c8:	4f 8d 14 49          	lea    (%r9,%r9,2),%r10
 2cc:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
 2d0:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 2d8 <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2d8>
 2d7:	00 
 2d8:	4d 29 c8             	sub    %r9,%r8
 2db:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2e3 <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2e3>
 2e2:	00 
 2e3:	c5 c5 72 d1 10       	vpsrld $0x10,%ymm1,%ymm7
 2e8:	4a 8d 04 11          	lea    (%rcx,%r10,1),%rax
 2ec:	c5 cd 72 d1 1f       	vpsrld $0x1f,%ymm1,%ymm6
 2f1:	49 c1 e8 03          	shr    $0x3,%r8
 2f5:	c5 d5 72 d1 1e       	vpsrld $0x1e,%ymm1,%ymm5
 2fa:	4a 8d 4c 11 18       	lea    0x18(%rcx,%r10,1),%rcx
 2ff:	4f 8d 04 40          	lea    (%r8,%r8,2),%r8
 303:	c5 ed 72 d1 18       	vpsrld $0x18,%ymm1,%ymm2
 308:	4a 8d 0c c1          	lea    (%rcx,%r8,8),%rcx
 30c:	0f 1f 40 00          	nopl   0x0(%rax)
 310:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 314:	c5 7a 7e 40 10       	vmovq  0x10(%rax),%xmm8
 319:	c5 7d 6f e9          	vmovdqa %ymm1,%ymm13
 31d:	c5 7d 6f f1          	vmovdqa %ymm1,%ymm14
 321:	c5 7d 6f f9          	vmovdqa %ymm1,%ymm15
 325:	48 83 c0 18          	add    $0x18,%rax
 329:	c4 63 39 0f c0 0c    	vpalignr $0xc,%xmm0,%xmm8,%xmm8
 32f:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
 335:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
 33a:	c5 b5 72 d0 03       	vpsrld $0x3,%ymm0,%ymm9
 33f:	c4 22 15 90 04 4f    	vpgatherdd %ymm13,(%rdi,%ymm9,2),%ymm8
 345:	c5 b5 72 d0 02       	vpsrld $0x2,%ymm0,%ymm9
 34a:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 34e:	c5 3d db c7          	vpand  %ymm7,%ymm8,%ymm8
 352:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 357:	c5 35 db ce          	vpand  %ymm6,%ymm9,%ymm9
 35b:	c4 c1 3d 72 f0 01    	vpslld $0x1,%ymm8,%ymm8
 361:	c4 41 35 eb c8       	vpor   %ymm8,%ymm9,%ymm9
 366:	c4 22 0d 90 04 8e    	vpgatherdd %ymm14,(%rsi,%ymm9,4),%ymm8
 36c:	c4 62 3d 45 c0       	vpsrlvd %ymm0,%ymm8,%ymm8
 371:	c5 3d db c2          	vpand  %ymm2,%ymm8,%ymm8
 375:	c4 a2 05 90 04 82    	vpgatherdd %ymm15,(%rdx,%ymm8,4),%ymm0
 37b:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 380:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 384:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 38a:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 38f:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 394:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 399:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 39e:	c5 7a 7f 40 e8       	vmovdqu %xmm8,-0x18(%rax)
 3a3:	48 39 c1             	cmp    %rax,%rcx
 3a6:	0f 85 64 ff ff ff    	jne    310 <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x310>
 3ac:	c5 f8 77             	vzeroupper
 3af:	c3                   	ret
 3b0:	45 31 c9             	xor    %r9d,%r9d
 3b3:	e9 04 ff ff ff       	jmp    2bc <jshc_channel::avx2_chain_dictionary(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2bc>
 3b8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 3bf:	00 

00000000000003c0 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
 3c0:	f3 0f 1e fa          	endbr64
 3c4:	55                   	push   %rbp
 3c5:	49 89 d2             	mov    %rdx,%r10
 3c8:	48 89 e5             	mov    %rsp,%rbp
 3cb:	53                   	push   %rbx
 3cc:	49 83 f9 1f          	cmp    $0x1f,%r9
 3d0:	0f 86 ba 03 00 00    	jbe    790 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x3d0>
 3d6:	4d 8d 59 e0          	lea    -0x20(%r9),%r11
 3da:	c5 fd 76 c0          	vpcmpeqd %ymm0,%ymm0,%ymm0
 3de:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 3e6 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x26>
 3e5:	00 
 3e6:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 3ee <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2e>
 3ed:	00 
 3ee:	4c 89 db             	mov    %r11,%rbx
 3f1:	c5 bd 72 d0 10       	vpsrld $0x10,%ymm0,%ymm8
 3f6:	48 89 c8             	mov    %rcx,%rax
 3f9:	4c 89 c2             	mov    %r8,%rdx
 3fc:	c5 c5 72 d0 1f       	vpsrld $0x1f,%ymm0,%ymm7
 401:	48 c1 eb 05          	shr    $0x5,%rbx
 405:	c5 cd 72 d0 1e       	vpsrld $0x1e,%ymm0,%ymm6
 40a:	48 8d 1c 5b          	lea    (%rbx,%rbx,2),%rbx
 40e:	c5 d5 72 d0 18       	vpsrld $0x18,%ymm0,%ymm5
 413:	48 c1 e3 05          	shl    $0x5,%rbx
 417:	48 8d 5c 19 60       	lea    0x60(%rcx,%rbx,1),%rbx
 41c:	0f 1f 40 00          	nopl   0x0(%rax)
 420:	c5 7a 6f 10          	vmovdqu (%rax),%xmm10
 424:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
 429:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
 42d:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
 431:	c5 7a 6f 48 18       	vmovdqu 0x18(%rax),%xmm9
 436:	c5 fa 6f 50 30       	vmovdqu 0x30(%rax),%xmm2
 43b:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
 43f:	48 83 c0 60          	add    $0x60,%rax
 443:	c4 c3 71 0f ca 0c    	vpalignr $0xc,%xmm10,%xmm1,%xmm1
 449:	c5 7a 7e 58 f8       	vmovq  -0x8(%rax),%xmm11
 44e:	48 83 c2 60          	add    $0x60,%rdx
 452:	c4 63 2d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm10,%ymm10
 458:	c5 fa 7e 48 c8       	vmovq  -0x38(%rax),%xmm1
 45d:	c4 62 2d 00 d4       	vpshufb %ymm4,%ymm10,%ymm10
 462:	c4 c3 71 0f c9 0c    	vpalignr $0xc,%xmm9,%xmm1,%xmm1
 468:	c4 63 35 38 c9 01    	vinserti128 $0x1,%xmm1,%ymm9,%ymm9
 46e:	c5 fa 7e 48 e0       	vmovq  -0x20(%rax),%xmm1
 473:	c4 62 35 00 cc       	vpshufb %ymm4,%ymm9,%ymm9
 478:	c4 e3 71 0f ca 0c    	vpalignr $0xc,%xmm2,%xmm1,%xmm1
 47e:	c4 e3 6d 38 d1 01    	vinserti128 $0x1,%xmm1,%ymm2,%ymm2
 484:	c5 fa 6f 48 e8       	vmovdqu -0x18(%rax),%xmm1
 489:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
 48e:	c4 63 21 0f d9 0c    	vpalignr $0xc,%xmm1,%xmm11,%xmm11
 494:	c4 c3 75 38 cb 01    	vinserti128 $0x1,%xmm11,%ymm1,%ymm1
 49a:	c4 c1 25 72 d2 03    	vpsrld $0x3,%ymm10,%ymm11
 4a0:	c4 22 15 90 24 5f    	vpgatherdd %ymm13,(%rdi,%ymm11,2),%ymm12
 4a6:	c4 c1 25 72 d2 02    	vpsrld $0x2,%ymm10,%ymm11
 4ac:	c5 2d db d6          	vpand  %ymm6,%ymm10,%ymm10
 4b0:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
 4b5:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 4b9:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
 4bd:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
 4c3:	c4 c1 2d 72 f2 03    	vpslld $0x3,%ymm10,%ymm10
 4c9:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
 4ce:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 4d3:	c4 22 0d 90 24 9e    	vpgatherdd %ymm14,(%rsi,%ymm11,4),%ymm12
 4d9:	c4 c1 25 72 d1 03    	vpsrld $0x3,%ymm9,%ymm11
 4df:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
 4e3:	c4 42 1d 45 d2       	vpsrlvd %ymm10,%ymm12,%ymm10
 4e8:	c4 22 05 90 24 5f    	vpgatherdd %ymm15,(%rdi,%ymm11,2),%ymm12
 4ee:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
 4f2:	c4 c1 25 72 d1 02    	vpsrld $0x2,%ymm9,%ymm11
 4f8:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
 4fd:	c5 35 db ce          	vpand  %ymm6,%ymm9,%ymm9
 501:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
 507:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 50d:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 511:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 516:	c4 22 15 90 24 9e    	vpgatherdd %ymm13,(%rsi,%ymm11,4),%ymm12
 51c:	c5 a5 72 d2 03       	vpsrld $0x3,%ymm2,%ymm11
 521:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
 525:	c4 42 1d 45 c9       	vpsrlvd %ymm9,%ymm12,%ymm9
 52a:	c4 22 0d 90 24 5f    	vpgatherdd %ymm14,(%rdi,%ymm11,2),%ymm12
 530:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
 534:	c5 a5 72 d2 02       	vpsrld $0x2,%ymm2,%ymm11
 539:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
 53e:	c5 ed db d6          	vpand  %ymm6,%ymm2,%ymm2
 542:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
 548:	c5 ed 72 f2 03       	vpslld $0x3,%ymm2,%ymm2
 54d:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 551:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 556:	c4 22 05 90 24 9e    	vpgatherdd %ymm15,(%rsi,%ymm11,4),%ymm12
 55c:	c5 a5 72 d1 03       	vpsrld $0x3,%ymm1,%ymm11
 561:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
 565:	c4 e2 1d 45 d2       	vpsrlvd %ymm2,%ymm12,%ymm2
 56a:	c4 22 15 90 24 5f    	vpgatherdd %ymm13,(%rdi,%ymm11,2),%ymm12
 570:	c5 7d 6f e8          	vmovdqa %ymm0,%ymm13
 574:	c5 a5 72 d1 02       	vpsrld $0x2,%ymm1,%ymm11
 579:	c4 41 1d db e0       	vpand  %ymm8,%ymm12,%ymm12
 57e:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
 582:	c4 c1 1d 72 f4 01    	vpslld $0x1,%ymm12,%ymm12
 588:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 58d:	c5 25 db df          	vpand  %ymm7,%ymm11,%ymm11
 591:	c4 41 25 eb dc       	vpor   %ymm12,%ymm11,%ymm11
 596:	c4 22 0d 90 24 9e    	vpgatherdd %ymm14,(%rsi,%ymm11,4),%ymm12
 59c:	c5 7d 6f f0          	vmovdqa %ymm0,%ymm14
 5a0:	c4 62 1d 45 d9       	vpsrlvd %ymm1,%ymm12,%ymm11
 5a5:	c5 ad db cd          	vpand  %ymm5,%ymm10,%ymm1
 5a9:	c4 42 05 90 14 8a    	vpgatherdd %ymm15,(%r10,%ymm1,4),%ymm10
 5af:	c5 b5 db cd          	vpand  %ymm5,%ymm9,%ymm1
 5b3:	c5 7d 6f f8          	vmovdqa %ymm0,%ymm15
 5b7:	c4 62 2d 00 d3       	vpshufb %ymm3,%ymm10,%ymm10
 5bc:	c4 42 15 90 0c 8a    	vpgatherdd %ymm13,(%r10,%ymm1,4),%ymm9
 5c2:	c5 25 db dd          	vpand  %ymm5,%ymm11,%ymm11
 5c6:	c5 ed db cd          	vpand  %ymm5,%ymm2,%ymm1
 5ca:	c4 41 79 6f e2       	vmovdqa %xmm10,%xmm12
 5cf:	c4 43 7d 39 d2 01    	vextracti128 $0x1,%ymm10,%xmm10
 5d5:	c4 c2 0d 90 14 8a    	vpgatherdd %ymm14,(%r10,%ymm1,4),%ymm2
 5db:	c4 82 05 90 0c 9a    	vpgatherdd %ymm15,(%r10,%ymm11,4),%ymm1
 5e1:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
 5e6:	c4 c1 21 73 fa 0c    	vpslldq $0xc,%xmm10,%xmm11
 5ec:	c4 c1 29 73 da 04    	vpsrldq $0x4,%xmm10,%xmm10
 5f2:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
 5f7:	c4 41 21 eb dc       	vpor   %xmm12,%xmm11,%xmm11
 5fc:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
 601:	c5 7a 7f 5a a0       	vmovdqu %xmm11,-0x60(%rdx)
 606:	c4 41 79 6f d9       	vmovdqa %xmm9,%xmm11
 60b:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
 611:	c5 79 d6 52 b0       	vmovq  %xmm10,-0x50(%rdx)
 616:	c4 c1 29 73 f9 0c    	vpslldq $0xc,%xmm9,%xmm10
 61c:	c4 c1 31 73 d9 04    	vpsrldq $0x4,%xmm9,%xmm9
 622:	c4 41 29 eb d3       	vpor   %xmm11,%xmm10,%xmm10
 627:	c5 79 d6 4a c8       	vmovq  %xmm9,-0x38(%rdx)
 62c:	c5 7a 7f 52 b8       	vmovdqu %xmm10,-0x48(%rdx)
 631:	c5 79 6f d2          	vmovdqa %xmm2,%xmm10
 635:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
 63b:	c5 b1 73 fa 0c       	vpslldq $0xc,%xmm2,%xmm9
 640:	c5 e9 73 da 04       	vpsrldq $0x4,%xmm2,%xmm2
 645:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 64a:	c5 f9 d6 52 e0       	vmovq  %xmm2,-0x20(%rdx)
 64f:	c5 7a 7f 4a d0       	vmovdqu %xmm9,-0x30(%rdx)
 654:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
 658:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 65e:	c5 e9 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm2
 663:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 668:	c4 c1 69 eb d1       	vpor   %xmm9,%xmm2,%xmm2
 66d:	c5 f9 d6 4a f8       	vmovq  %xmm1,-0x8(%rdx)
 672:	c5 fa 7f 52 e8       	vmovdqu %xmm2,-0x18(%rdx)
 677:	48 39 c3             	cmp    %rax,%rbx
 67a:	0f 85 a0 fd ff ff    	jne    420 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x60>
 680:	49 83 e3 e0          	and    $0xffffffffffffffe0,%r11
 684:	49 8d 53 20          	lea    0x20(%r11),%rdx
 688:	4c 39 ca             	cmp    %r9,%rdx
 68b:	0f 83 f1 00 00 00    	jae    782 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x3c2>
 691:	49 ff c9             	dec    %r9
 694:	4c 8d 1c 52          	lea    (%rdx,%rdx,2),%r11
 698:	c5 f5 76 c9          	vpcmpeqd %ymm1,%ymm1,%ymm1
 69c:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 6a4 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2e4>
 6a3:	00 
 6a4:	49 29 d1             	sub    %rdx,%r9
 6a7:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 6af <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2ef>
 6ae:	00 
 6af:	4a 8d 54 19 18       	lea    0x18(%rcx,%r11,1),%rdx
 6b4:	4a 8d 04 19          	lea    (%rcx,%r11,1),%rax
 6b8:	c5 c5 72 d1 10       	vpsrld $0x10,%ymm1,%ymm7
 6bd:	49 c1 e9 03          	shr    $0x3,%r9
 6c1:	c5 cd 72 d1 1f       	vpsrld $0x1f,%ymm1,%ymm6
 6c6:	4d 01 d8             	add    %r11,%r8
 6c9:	c5 d5 72 d1 1e       	vpsrld $0x1e,%ymm1,%ymm5
 6ce:	c5 ed 72 d1 18       	vpsrld $0x18,%ymm1,%ymm2
 6d3:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
 6d7:	4a 8d 14 ca          	lea    (%rdx,%r9,8),%rdx
 6db:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 6e0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 6e4:	c5 7a 7e 40 10       	vmovq  0x10(%rax),%xmm8
 6e9:	c5 7d 6f e9          	vmovdqa %ymm1,%ymm13
 6ed:	c5 7d 6f f1          	vmovdqa %ymm1,%ymm14
 6f1:	c5 7d 6f f9          	vmovdqa %ymm1,%ymm15
 6f5:	48 83 c0 18          	add    $0x18,%rax
 6f9:	49 83 c0 18          	add    $0x18,%r8
 6fd:	c4 63 39 0f c0 0c    	vpalignr $0xc,%xmm0,%xmm8,%xmm8
 703:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
 709:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
 70e:	c5 b5 72 d0 03       	vpsrld $0x3,%ymm0,%ymm9
 713:	c4 22 15 90 04 4f    	vpgatherdd %ymm13,(%rdi,%ymm9,2),%ymm8
 719:	c5 b5 72 d0 02       	vpsrld $0x2,%ymm0,%ymm9
 71e:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 722:	c5 3d db c7          	vpand  %ymm7,%ymm8,%ymm8
 726:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 72b:	c5 35 db ce          	vpand  %ymm6,%ymm9,%ymm9
 72f:	c4 c1 3d 72 f0 01    	vpslld $0x1,%ymm8,%ymm8
 735:	c4 41 35 eb c8       	vpor   %ymm8,%ymm9,%ymm9
 73a:	c4 22 0d 90 04 8e    	vpgatherdd %ymm14,(%rsi,%ymm9,4),%ymm8
 740:	c4 62 3d 45 c0       	vpsrlvd %ymm0,%ymm8,%ymm8
 745:	c5 3d db c2          	vpand  %ymm2,%ymm8,%ymm8
 749:	c4 82 05 90 04 82    	vpgatherdd %ymm15,(%r10,%ymm8,4),%ymm0
 74f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 754:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
 758:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 75e:	c5 b9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm8
 763:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 768:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 76d:	c4 c1 79 d6 40 f8    	vmovq  %xmm0,-0x8(%r8)
 773:	c4 41 7a 7f 40 e8    	vmovdqu %xmm8,-0x18(%r8)
 779:	48 39 c2             	cmp    %rax,%rdx
 77c:	0f 85 5e ff ff ff    	jne    6e0 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x320>
 782:	c5 f8 77             	vzeroupper
 785:	48 8b 5d f8          	mov    -0x8(%rbp),%rbx
 789:	c9                   	leave
 78a:	c3                   	ret
 78b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 790:	31 d2                	xor    %edx,%edx
 792:	e9 f1 fe ff ff       	jmp    688 <jshc_channel::avx2_chain_dictionary_to(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2c8>
