
artifacts/skylake-rgbdictionary-linux-build-v1/CMakeFiles/jshc_skylake_rgbdictionary.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	48 83 f9 1f          	cmp    $0x1f,%rcx
   8:	0f 86 e2 02 00 00    	jbe    2f0 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2f0>
   e:	4c 8d 41 e0          	lea    -0x20(%rcx),%r8
  12:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
  16:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 1e <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1e>
  1d:	00 
  1e:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 26 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x26>
  25:	00 
  26:	c5 bd 72 d6 10       	vpsrld $0x10,%ymm6,%ymm8
  2b:	c5 c5 72 d6 1d       	vpsrld $0x1d,%ymm6,%ymm7
  30:	4d 89 c1             	mov    %r8,%r9
  33:	48 89 d0             	mov    %rdx,%rax
  36:	49 c1 e9 05          	shr    $0x5,%r9
  3a:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
  3e:	49 c1 e1 05          	shl    $0x5,%r9
  42:	4e 8d 4c 0a 60       	lea    0x60(%rdx,%r9,1),%r9
  47:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  4e:	00 00 
  50:	c5 fa 6f 18          	vmovdqu (%rax),%xmm3
  54:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
  59:	c5 7d 6f de          	vmovdqa %ymm6,%ymm11
  5d:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
  61:	c5 fa 6f 50 18       	vmovdqu 0x18(%rax),%xmm2
  66:	c5 fa 6f 48 30       	vmovdqu 0x30(%rax),%xmm1
  6b:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
  6f:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
  73:	c4 e3 79 0f c3 0c    	vpalignr $0xc,%xmm3,%xmm0,%xmm0
  79:	c5 7a 7e 48 58       	vmovq  0x58(%rax),%xmm9
  7e:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
  82:	48 83 c0 60          	add    $0x60,%rax
  86:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
  8c:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
  91:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
  96:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
  9c:	c5 ad 72 d3 03       	vpsrld $0x3,%ymm3,%ymm10
  a1:	c5 e5 db df          	vpand  %ymm7,%ymm3,%ymm3
  a5:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
  ab:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
  b0:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
  b5:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
  bb:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
  c1:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
  c6:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
  cb:	c4 63 31 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm9,%xmm9
  d1:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
  d7:	c4 22 25 90 0c 57    	vpgatherdd %ymm11,(%rdi,%ymm10,2),%ymm9
  dd:	c5 7d 6f de          	vmovdqa %ymm6,%ymm11
  e1:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
  e6:	c5 ad 72 d2 03       	vpsrld $0x3,%ymm2,%ymm10
  eb:	c5 ed db d7          	vpand  %ymm7,%ymm2,%ymm2
  ef:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
  f5:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
  fa:	c4 41 65 eb c9       	vpor   %ymm9,%ymm3,%ymm9
  ff:	c4 a2 1d 90 1c 8e    	vpgatherdd %ymm12,(%rsi,%ymm9,4),%ymm3
 105:	c4 22 15 90 0c 57    	vpgatherdd %ymm13,(%rdi,%ymm10,2),%ymm9
 10b:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
 10f:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
 114:	c5 ad 72 d1 03       	vpsrld $0x3,%ymm1,%ymm10
 119:	c5 f5 db cf          	vpand  %ymm7,%ymm1,%ymm1
 11d:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 123:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
 128:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
 12c:	c4 41 6d eb c9       	vpor   %ymm9,%ymm2,%ymm9
 131:	c4 a2 0d 90 14 8e    	vpgatherdd %ymm14,(%rsi,%ymm9,4),%ymm2
 137:	c4 22 05 90 0c 57    	vpgatherdd %ymm15,(%rdi,%ymm10,2),%ymm9
 13d:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
 142:	c5 ad 72 d0 03       	vpsrld $0x3,%ymm0,%ymm10
 147:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
 14b:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 151:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
 156:	c4 41 75 eb c9       	vpor   %ymm9,%ymm1,%ymm9
 15b:	c4 a2 25 90 0c 8e    	vpgatherdd %ymm11,(%rsi,%ymm9,4),%ymm1
 161:	c4 22 1d 90 0c 57    	vpgatherdd %ymm12,(%rdi,%ymm10,2),%ymm9
 167:	c5 79 6f d3          	vmovdqa %xmm3,%xmm10
 16b:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
 170:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
 176:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
 17b:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 181:	c4 41 7d eb c9       	vpor   %ymm9,%ymm0,%ymm9
 186:	c4 a2 15 90 04 8e    	vpgatherdd %ymm13,(%rsi,%ymm9,4),%ymm0
 18c:	c5 b1 73 fb 0c       	vpslldq $0xc,%xmm3,%xmm9
 191:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 196:	c5 e1 73 db 04       	vpsrldq $0x4,%xmm3,%xmm3
 19b:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
 1a0:	c5 7a 7f 48 a0       	vmovdqu %xmm9,-0x60(%rax)
 1a5:	c5 79 6f ca          	vmovdqa %xmm2,%xmm9
 1a9:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
 1af:	c5 f9 d6 58 b0       	vmovq  %xmm3,-0x50(%rax)
 1b4:	c5 e1 73 fa 0c       	vpslldq $0xc,%xmm2,%xmm3
 1b9:	c5 e9 73 da 04       	vpsrldq $0x4,%xmm2,%xmm2
 1be:	c4 c1 61 eb d9       	vpor   %xmm9,%xmm3,%xmm3
 1c3:	c5 f9 d6 50 c8       	vmovq  %xmm2,-0x38(%rax)
 1c8:	c5 fa 7f 58 b8       	vmovdqu %xmm3,-0x48(%rax)
 1cd:	c5 f9 6f d9          	vmovdqa %xmm1,%xmm3
 1d1:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 1d7:	c5 e9 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm2
 1dc:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 1e1:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
 1e5:	c5 f9 d6 48 e0       	vmovq  %xmm1,-0x20(%rax)
 1ea:	c5 fa 7f 50 d0       	vmovdqu %xmm2,-0x30(%rax)
 1ef:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
 1f3:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 1f9:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 1fe:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 203:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
 207:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 20c:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 211:	49 39 c1             	cmp    %rax,%r9
 214:	0f 85 36 fe ff ff    	jne    50 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x50>
 21a:	49 83 e0 e0          	and    $0xffffffffffffffe0,%r8
 21e:	49 83 c0 20          	add    $0x20,%r8
 222:	49 39 c8             	cmp    %rcx,%r8
 225:	0f 83 b9 00 00 00    	jae    2e4 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2e4>
 22b:	48 ff c9             	dec    %rcx
 22e:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
 232:	c5 ed 76 d2          	vpcmpeqd %ymm2,%ymm2,%ymm2
 236:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 23e <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x23e>
 23d:	00 
 23e:	4c 29 c1             	sub    %r8,%rcx
 241:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 249 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x249>
 248:	00 
 249:	c5 cd 72 d2 10       	vpsrld $0x10,%ymm2,%ymm6
 24e:	4a 8d 04 0a          	lea    (%rdx,%r9,1),%rax
 252:	48 c1 e9 03          	shr    $0x3,%rcx
 256:	c5 e5 72 d2 1d       	vpsrld $0x1d,%ymm2,%ymm3
 25b:	4a 8d 54 0a 18       	lea    0x18(%rdx,%r9,1),%rdx
 260:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
 264:	48 8d 14 ca          	lea    (%rdx,%rcx,8),%rdx
 268:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 26f:	00 
 270:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 274:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
 279:	c5 7d 6f f2          	vmovdqa %ymm2,%ymm14
 27d:	48 83 c0 18          	add    $0x18,%rax
 281:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
 287:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 28d:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
 292:	c5 c5 72 d0 03       	vpsrld $0x3,%ymm0,%ymm7
 297:	c5 fd db c3          	vpand  %ymm3,%ymm0,%ymm0
 29b:	c4 e2 0d 90 0c 7f    	vpgatherdd %ymm14,(%rdi,%ymm7,2),%ymm1
 2a1:	c5 fd 6f fa          	vmovdqa %ymm2,%ymm7
 2a5:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
 2a9:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 2ae:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
 2b2:	c4 e2 45 90 0c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm1
 2b8:	c4 e2 75 00 c4       	vpshufb %ymm4,%ymm1,%ymm0
 2bd:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 2c1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 2c7:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 2cc:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 2d1:	c5 f1 eb cf          	vpor   %xmm7,%xmm1,%xmm1
 2d5:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 2da:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 2df:	48 39 c2             	cmp    %rax,%rdx
 2e2:	75 8c                	jne    270 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x270>
 2e4:	c5 f8 77             	vzeroupper
 2e7:	c3                   	ret
 2e8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 2ef:	00 
 2f0:	45 31 c0             	xor    %r8d,%r8d
 2f3:	e9 2a ff ff ff       	jmp    222 <jshc_channel::avx2_chain_rgbdictionary(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x222>
 2f8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 2ff:	00 

0000000000000300 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
 300:	f3 0f 1e fa          	endbr64
 304:	49 89 d1             	mov    %rdx,%r9
 307:	49 83 f8 1f          	cmp    $0x1f,%r8
 30b:	0f 86 df 02 00 00    	jbe    5f0 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2f0>
 311:	4d 8d 50 e0          	lea    -0x20(%r8),%r10
 315:	c5 cd 76 f6          	vpcmpeqd %ymm6,%ymm6,%ymm6
 319:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 321 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x21>
 320:	00 
 321:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 329 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x29>
 328:	00 
 329:	c5 bd 72 d6 10       	vpsrld $0x10,%ymm6,%ymm8
 32e:	c5 c5 72 d6 1d       	vpsrld $0x1d,%ymm6,%ymm7
 333:	4d 89 d3             	mov    %r10,%r11
 336:	48 89 d0             	mov    %rdx,%rax
 339:	49 c1 eb 05          	shr    $0x5,%r11
 33d:	48 89 ca             	mov    %rcx,%rdx
 340:	4f 8d 1c 5b          	lea    (%r11,%r11,2),%r11
 344:	49 c1 e3 05          	shl    $0x5,%r11
 348:	4f 8d 5c 19 60       	lea    0x60(%r9,%r11,1),%r11
 34d:	0f 1f 00             	nopl   (%rax)
 350:	c5 fa 6f 18          	vmovdqu (%rax),%xmm3
 354:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
 359:	c5 7d 6f de          	vmovdqa %ymm6,%ymm11
 35d:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
 361:	c5 fa 6f 50 18       	vmovdqu 0x18(%rax),%xmm2
 366:	c5 fa 6f 48 30       	vmovdqu 0x30(%rax),%xmm1
 36b:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
 36f:	c5 7d 6f f6          	vmovdqa %ymm6,%ymm14
 373:	c4 e3 79 0f c3 0c    	vpalignr $0xc,%xmm3,%xmm0,%xmm0
 379:	c5 7a 7e 48 58       	vmovq  0x58(%rax),%xmm9
 37e:	c5 7d 6f fe          	vmovdqa %ymm6,%ymm15
 382:	48 83 c0 60          	add    $0x60,%rax
 386:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
 38c:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
 391:	48 83 c2 60          	add    $0x60,%rdx
 395:	c4 e2 65 00 dd       	vpshufb %ymm5,%ymm3,%ymm3
 39a:	c4 e3 79 0f c2 0c    	vpalignr $0xc,%xmm2,%xmm0,%xmm0
 3a0:	c5 ad 72 d3 03       	vpsrld $0x3,%ymm3,%ymm10
 3a5:	c5 e5 db df          	vpand  %ymm7,%ymm3,%ymm3
 3a9:	c4 e3 6d 38 d0 01    	vinserti128 $0x1,%xmm0,%ymm2,%ymm2
 3af:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
 3b4:	c4 e2 6d 00 d5       	vpshufb %ymm5,%ymm2,%ymm2
 3b9:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
 3bf:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
 3c5:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
 3ca:	c4 e2 75 00 cd       	vpshufb %ymm5,%ymm1,%ymm1
 3cf:	c4 63 31 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm9,%xmm9
 3d5:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
 3db:	c4 22 25 90 0c 57    	vpgatherdd %ymm11,(%rdi,%ymm10,2),%ymm9
 3e1:	c5 7d 6f de          	vmovdqa %ymm6,%ymm11
 3e5:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
 3ea:	c5 ad 72 d2 03       	vpsrld $0x3,%ymm2,%ymm10
 3ef:	c5 ed db d7          	vpand  %ymm7,%ymm2,%ymm2
 3f3:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 3f9:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
 3fe:	c4 41 65 eb c9       	vpor   %ymm9,%ymm3,%ymm9
 403:	c4 a2 1d 90 1c 8e    	vpgatherdd %ymm12,(%rsi,%ymm9,4),%ymm3
 409:	c4 22 15 90 0c 57    	vpgatherdd %ymm13,(%rdi,%ymm10,2),%ymm9
 40f:	c5 7d 6f e6          	vmovdqa %ymm6,%ymm12
 413:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
 418:	c5 ad 72 d1 03       	vpsrld $0x3,%ymm1,%ymm10
 41d:	c5 f5 db cf          	vpand  %ymm7,%ymm1,%ymm1
 421:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 427:	c4 e2 65 00 dc       	vpshufb %ymm4,%ymm3,%ymm3
 42c:	c5 7d 6f ee          	vmovdqa %ymm6,%ymm13
 430:	c4 41 6d eb c9       	vpor   %ymm9,%ymm2,%ymm9
 435:	c4 a2 0d 90 14 8e    	vpgatherdd %ymm14,(%rsi,%ymm9,4),%ymm2
 43b:	c4 22 05 90 0c 57    	vpgatherdd %ymm15,(%rdi,%ymm10,2),%ymm9
 441:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
 446:	c5 ad 72 d0 03       	vpsrld $0x3,%ymm0,%ymm10
 44b:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
 44f:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 455:	c4 e2 6d 00 d4       	vpshufb %ymm4,%ymm2,%ymm2
 45a:	c4 41 75 eb c9       	vpor   %ymm9,%ymm1,%ymm9
 45f:	c4 a2 25 90 0c 8e    	vpgatherdd %ymm11,(%rsi,%ymm9,4),%ymm1
 465:	c4 22 1d 90 0c 57    	vpgatherdd %ymm12,(%rdi,%ymm10,2),%ymm9
 46b:	c5 79 6f d3          	vmovdqa %xmm3,%xmm10
 46f:	c4 41 35 db c8       	vpand  %ymm8,%ymm9,%ymm9
 474:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
 47a:	c4 e2 75 00 cc       	vpshufb %ymm4,%ymm1,%ymm1
 47f:	c4 c1 35 72 f1 03    	vpslld $0x3,%ymm9,%ymm9
 485:	c4 41 7d eb c9       	vpor   %ymm9,%ymm0,%ymm9
 48a:	c4 a2 15 90 04 8e    	vpgatherdd %ymm13,(%rsi,%ymm9,4),%ymm0
 490:	c5 b1 73 fb 0c       	vpslldq $0xc,%xmm3,%xmm9
 495:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 49a:	c5 e1 73 db 04       	vpsrldq $0x4,%xmm3,%xmm3
 49f:	c4 e2 7d 00 c4       	vpshufb %ymm4,%ymm0,%ymm0
 4a4:	c5 7a 7f 4a a0       	vmovdqu %xmm9,-0x60(%rdx)
 4a9:	c5 79 6f ca          	vmovdqa %xmm2,%xmm9
 4ad:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
 4b3:	c5 f9 d6 5a b0       	vmovq  %xmm3,-0x50(%rdx)
 4b8:	c5 e1 73 fa 0c       	vpslldq $0xc,%xmm2,%xmm3
 4bd:	c5 e9 73 da 04       	vpsrldq $0x4,%xmm2,%xmm2
 4c2:	c4 c1 61 eb d9       	vpor   %xmm9,%xmm3,%xmm3
 4c7:	c5 f9 d6 52 c8       	vmovq  %xmm2,-0x38(%rdx)
 4cc:	c5 fa 7f 5a b8       	vmovdqu %xmm3,-0x48(%rdx)
 4d1:	c5 f9 6f d9          	vmovdqa %xmm1,%xmm3
 4d5:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 4db:	c5 e9 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm2
 4e0:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 4e5:	c5 e9 eb d3          	vpor   %xmm3,%xmm2,%xmm2
 4e9:	c5 f9 d6 4a e0       	vmovq  %xmm1,-0x20(%rdx)
 4ee:	c5 fa 7f 52 d0       	vmovdqu %xmm2,-0x30(%rdx)
 4f3:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
 4f7:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 4fd:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 502:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 507:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
 50b:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
 510:	c5 fa 7f 4a e8       	vmovdqu %xmm1,-0x18(%rdx)
 515:	49 39 c3             	cmp    %rax,%r11
 518:	0f 85 32 fe ff ff    	jne    350 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x50>
 51e:	49 83 e2 e0          	and    $0xffffffffffffffe0,%r10
 522:	49 83 c2 20          	add    $0x20,%r10
 526:	4d 39 c2             	cmp    %r8,%r10
 529:	0f 83 b9 00 00 00    	jae    5e8 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x2e8>
 52f:	49 ff c8             	dec    %r8
 532:	4f 8d 1c 52          	lea    (%r10,%r10,2),%r11
 536:	c5 ed 76 d2          	vpcmpeqd %ymm2,%ymm2,%ymm2
 53a:	c5 fd 6f 2d 00 00 00 	vmovdqa 0x0(%rip),%ymm5        # 542 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x242>
 541:	00 
 542:	4d 29 d0             	sub    %r10,%r8
 545:	4a 8d 14 19          	lea    (%rcx,%r11,1),%rdx
 549:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 551 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x251>
 550:	00 
 551:	4b 8d 4c 19 18       	lea    0x18(%r9,%r11,1),%rcx
 556:	c5 cd 72 d2 10       	vpsrld $0x10,%ymm2,%ymm6
 55b:	49 c1 e8 03          	shr    $0x3,%r8
 55f:	c5 e5 72 d2 1d       	vpsrld $0x1d,%ymm2,%ymm3
 564:	4b 8d 04 19          	lea    (%r9,%r11,1),%rax
 568:	4f 8d 04 40          	lea    (%r8,%r8,2),%r8
 56c:	4a 8d 0c c1          	lea    (%rcx,%r8,8),%rcx
 570:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 574:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
 579:	c5 7d 6f f2          	vmovdqa %ymm2,%ymm14
 57d:	48 83 c0 18          	add    $0x18,%rax
 581:	48 83 c2 18          	add    $0x18,%rdx
 585:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
 58b:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 591:	c4 e2 7d 00 c5       	vpshufb %ymm5,%ymm0,%ymm0
 596:	c5 c5 72 d0 03       	vpsrld $0x3,%ymm0,%ymm7
 59b:	c5 fd db c3          	vpand  %ymm3,%ymm0,%ymm0
 59f:	c4 e2 0d 90 0c 7f    	vpgatherdd %ymm14,(%rdi,%ymm7,2),%ymm1
 5a5:	c5 fd 6f fa          	vmovdqa %ymm2,%ymm7
 5a9:	c5 f5 db ce          	vpand  %ymm6,%ymm1,%ymm1
 5ad:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 5b2:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
 5b6:	c4 e2 45 90 0c 86    	vpgatherdd %ymm7,(%rsi,%ymm0,4),%ymm1
 5bc:	c4 e2 75 00 c4       	vpshufb %ymm4,%ymm1,%ymm0
 5c1:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 5c5:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 5cb:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 5d0:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 5d5:	c5 f1 eb cf          	vpor   %xmm7,%xmm1,%xmm1
 5d9:	c5 f9 d6 42 f8       	vmovq  %xmm0,-0x8(%rdx)
 5de:	c5 fa 7f 4a e8       	vmovdqu %xmm1,-0x18(%rdx)
 5e3:	48 39 c1             	cmp    %rax,%rcx
 5e6:	75 88                	jne    570 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x270>
 5e8:	c5 f8 77             	vzeroupper
 5eb:	c3                   	ret
 5ec:	0f 1f 40 00          	nopl   0x0(%rax)
 5f0:	45 31 d2             	xor    %r10d,%r10d
 5f3:	e9 2e ff ff ff       	jmp    526 <jshc_channel::avx2_chain_rgbdictionary_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x226>
