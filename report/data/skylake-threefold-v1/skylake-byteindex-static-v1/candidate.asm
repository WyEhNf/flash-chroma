
artifacts\skylake-byteindex-build-v1\CMakeFiles\jshc_skylake_byteindex.dir\channel_avx2.cpp.obj:     file format pe-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)>:
   0:	48 83 ec 68          	sub    $0x68,%rsp
   4:	c5 f8 29 34 24       	vmovaps %xmm6,(%rsp)
   9:	c5 f8 29 7c 24 10    	vmovaps %xmm7,0x10(%rsp)
   f:	c5 78 29 44 24 20    	vmovaps %xmm8,0x20(%rsp)
  15:	c5 78 29 4c 24 30    	vmovaps %xmm9,0x30(%rsp)
  1b:	c5 78 29 54 24 40    	vmovaps %xmm10,0x40(%rsp)
  21:	c5 78 29 5c 24 50    	vmovaps %xmm11,0x50(%rsp)
  27:	49 83 f9 1f          	cmp    $0x1f,%r9
  2b:	0f 86 8f 02 00 00    	jbe    2c0 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x2c0>
  31:	4d 8d 51 e0          	lea    -0x20(%r9),%r10
  35:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
  39:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 41 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x41>
  40:	00 
  41:	c5 fd 6f 15 20 00 00 	vmovdqa 0x20(%rip),%ymm2        # 69 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x69>
  48:	00 
  49:	4d 89 d3             	mov    %r10,%r11
  4c:	c5 cd 72 d5 18       	vpsrld $0x18,%ymm5,%ymm6
  51:	4c 89 c0             	mov    %r8,%rax
  54:	49 c1 eb 05          	shr    $0x5,%r11
  58:	4f 8d 1c 5b          	lea    (%r11,%r11,2),%r11
  5c:	49 c1 e3 05          	shl    $0x5,%r11
  60:	4f 8d 5c 18 60       	lea    0x60(%r8,%r11,1),%r11
  65:	0f 1f 00             	nopl   (%rax)
  68:	c5 fa 6f 38          	vmovdqu (%rax),%xmm7
  6c:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
  71:	c5 7d 6f d5          	vmovdqa %ymm5,%ymm10
  75:	48 83 c0 60          	add    $0x60,%rax
  79:	c5 fa 7e 48 c8       	vmovq  -0x38(%rax),%xmm1
  7e:	c5 7a 7e 40 e0       	vmovq  -0x20(%rax),%xmm8
  83:	c4 e3 79 0f c7 0c    	vpalignr $0xc,%xmm7,%xmm0,%xmm0
  89:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
  8f:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
  94:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
  99:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
  9f:	c5 f9 6f e0          	vmovdqa %xmm0,%xmm4
  a3:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
  a8:	c4 62 2d 90 1c 39    	vpgatherdd %ymm10,(%rcx,%ymm7,1),%ymm11
  ae:	c4 e3 5d 38 e1 01    	vinserti128 $0x1,%xmm1,%ymm4,%ymm4
  b4:	c5 fd 6f fd          	vmovdqa %ymm5,%ymm7
  b8:	c4 63 39 0f c0 0c    	vpalignr $0xc,%xmm0,%xmm8,%xmm8
  be:	c5 f9 6f c8          	vmovdqa %xmm0,%xmm1
  c2:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
  c7:	c4 e2 5d 00 e3       	vpshufb %ymm3,%ymm4,%ymm4
  cc:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
  d2:	c5 7a 7e 40 f8       	vmovq  -0x8(%rax),%xmm8
  d7:	c4 62 45 90 14 21    	vpgatherdd %ymm7,(%rcx,%ymm4,1),%ymm10
  dd:	c5 fd 6f e5          	vmovdqa %ymm5,%ymm4
  e1:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
  e6:	c4 63 39 0f c0 0c    	vpalignr $0xc,%xmm0,%xmm8,%xmm8
  ec:	c4 62 5d 90 0c 09    	vpgatherdd %ymm4,(%rcx,%ymm1,1),%ymm9
  f2:	c5 fd 6f e5          	vmovdqa %ymm5,%ymm4
  f6:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
  fc:	c5 fd 6f cd          	vmovdqa %ymm5,%ymm1
 100:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 105:	c4 62 5d 90 04 01    	vpgatherdd %ymm4,(%rcx,%ymm0,1),%ymm8
 10b:	c5 a5 db c6          	vpand  %ymm6,%ymm11,%ymm0
 10f:	c5 fd 6f e5          	vmovdqa %ymm5,%ymm4
 113:	c4 e2 5d 90 3c 82    	vpgatherdd %ymm4,(%rdx,%ymm0,4),%ymm7
 119:	c5 ad db c6          	vpand  %ymm6,%ymm10,%ymm0
 11d:	c5 3d db c6          	vpand  %ymm6,%ymm8,%ymm8
 121:	c4 e2 75 90 24 82    	vpgatherdd %ymm1,(%rdx,%ymm0,4),%ymm4
 127:	c4 e2 45 00 fa       	vpshufb %ymm2,%ymm7,%ymm7
 12c:	c5 b5 db c6          	vpand  %ymm6,%ymm9,%ymm0
 130:	c5 7d 6f dd          	vmovdqa %ymm5,%ymm11
 134:	c5 7d 6f cd          	vmovdqa %ymm5,%ymm9
 138:	c4 e2 5d 00 e2       	vpshufb %ymm2,%ymm4,%ymm4
 13d:	c4 e2 25 90 0c 82    	vpgatherdd %ymm11,(%rdx,%ymm0,4),%ymm1
 143:	c4 a2 35 90 04 82    	vpgatherdd %ymm9,(%rdx,%ymm8,4),%ymm0
 149:	c5 79 6f cf          	vmovdqa %xmm7,%xmm9
 14d:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
 153:	c4 e2 75 00 ca       	vpshufb %ymm2,%ymm1,%ymm1
 158:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 15d:	c5 b9 73 ff 0c       	vpslldq $0xc,%xmm7,%xmm8
 162:	c5 c1 73 df 04       	vpsrldq $0x4,%xmm7,%xmm7
 167:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 16c:	c5 f9 d6 78 b0       	vmovq  %xmm7,-0x50(%rax)
 171:	c5 7a 7f 40 a0       	vmovdqu %xmm8,-0x60(%rax)
 176:	c5 79 6f c4          	vmovdqa %xmm4,%xmm8
 17a:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
 180:	c5 c1 73 fc 0c       	vpslldq $0xc,%xmm4,%xmm7
 185:	c5 d9 73 dc 04       	vpsrldq $0x4,%xmm4,%xmm4
 18a:	c4 c1 41 eb f8       	vpor   %xmm8,%xmm7,%xmm7
 18f:	c5 f9 d6 60 c8       	vmovq  %xmm4,-0x38(%rax)
 194:	c5 fa 7f 78 b8       	vmovdqu %xmm7,-0x48(%rax)
 199:	c5 f9 6f f9          	vmovdqa %xmm1,%xmm7
 19d:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 1a3:	c5 d9 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm4
 1a8:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 1ad:	c5 d9 eb e7          	vpor   %xmm7,%xmm4,%xmm4
 1b1:	c5 f9 d6 48 e0       	vmovq  %xmm1,-0x20(%rax)
 1b6:	c5 fa 7f 60 d0       	vmovdqu %xmm4,-0x30(%rax)
 1bb:	c5 f9 6f e0          	vmovdqa %xmm0,%xmm4
 1bf:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 1c5:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 1ca:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 1cf:	c5 f1 eb cc          	vpor   %xmm4,%xmm1,%xmm1
 1d3:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 1d8:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 1dd:	49 39 c3             	cmp    %rax,%r11
 1e0:	0f 85 82 fe ff ff    	jne    68 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x68>
 1e6:	49 83 e2 e0          	and    $0xffffffffffffffe0,%r10
 1ea:	49 83 c2 20          	add    $0x20,%r10
 1ee:	4d 39 ca             	cmp    %r9,%r10
 1f1:	0f 83 9b 00 00 00    	jae    292 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x292>
 1f7:	49 ff c9             	dec    %r9
 1fa:	4f 8d 1c 52          	lea    (%r10,%r10,2),%r11
 1fe:	c5 dd 76 e4          	vpcmpeqd %ymm4,%ymm4,%ymm4
 202:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 20a <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x20a>
 209:	00 
 20a:	4d 29 d1             	sub    %r10,%r9
 20d:	c5 fd 6f 15 20 00 00 	vmovdqa 0x20(%rip),%ymm2        # 235 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x235>
 214:	00 
 215:	c5 d5 72 d4 18       	vpsrld $0x18,%ymm4,%ymm5
 21a:	4b 8d 04 18          	lea    (%r8,%r11,1),%rax
 21e:	49 c1 e9 03          	shr    $0x3,%r9
 222:	4f 8d 44 18 18       	lea    0x18(%r8,%r11,1),%r8
 227:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
 22b:	4f 8d 04 c8          	lea    (%r8,%r9,8),%r8
 22f:	90                   	nop
 230:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 234:	c5 fa 7e 48 10       	vmovq  0x10(%rax),%xmm1
 239:	c5 fd 6f f4          	vmovdqa %ymm4,%ymm6
 23d:	48 83 c0 18          	add    $0x18,%rax
 241:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
 247:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 24d:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
 252:	c4 e2 4d 90 0c 01    	vpgatherdd %ymm6,(%rcx,%ymm0,1),%ymm1
 258:	c5 fd 6f f4          	vmovdqa %ymm4,%ymm6
 25c:	c5 f5 db cd          	vpand  %ymm5,%ymm1,%ymm1
 260:	c4 e2 4d 90 04 8a    	vpgatherdd %ymm6,(%rdx,%ymm1,4),%ymm0
 266:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 26b:	c5 f9 6f f0          	vmovdqa %xmm0,%xmm6
 26f:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 275:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 27a:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 27f:	c5 f1 eb ce          	vpor   %xmm6,%xmm1,%xmm1
 283:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 288:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 28d:	49 39 c0             	cmp    %rax,%r8
 290:	75 9e                	jne    230 <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x230>
 292:	c5 f8 77             	vzeroupper
 295:	c5 f8 28 34 24       	vmovaps (%rsp),%xmm6
 29a:	c5 f8 28 7c 24 10    	vmovaps 0x10(%rsp),%xmm7
 2a0:	c5 78 28 44 24 20    	vmovaps 0x20(%rsp),%xmm8
 2a6:	c5 78 28 4c 24 30    	vmovaps 0x30(%rsp),%xmm9
 2ac:	c5 78 28 54 24 40    	vmovaps 0x40(%rsp),%xmm10
 2b2:	c5 78 28 5c 24 50    	vmovaps 0x50(%rsp),%xmm11
 2b8:	48 83 c4 68          	add    $0x68,%rsp
 2bc:	c3                   	ret
 2bd:	0f 1f 00             	nopl   (%rax)
 2c0:	45 31 d2             	xor    %r10d,%r10d
 2c3:	e9 26 ff ff ff       	jmp    1ee <jshc_channel::avx2_chain_byteindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x1ee>
 2c8:	90                   	nop
 2c9:	90                   	nop
 2ca:	90                   	nop
 2cb:	90                   	nop
 2cc:	90                   	nop
 2cd:	90                   	nop
 2ce:	90                   	nop
 2cf:	90                   	nop
