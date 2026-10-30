
artifacts\skylake-direct16-build-v1\CMakeFiles\jshc_skylake_direct16.dir\channel_avx2.cpp.obj:     file format pe-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)>:
   0:	48 81 ec 88 00 00 00 	sub    $0x88,%rsp
   7:	c5 f8 29 34 24       	vmovaps %xmm6,(%rsp)
   c:	c5 f8 29 7c 24 10    	vmovaps %xmm7,0x10(%rsp)
  12:	c5 78 29 44 24 20    	vmovaps %xmm8,0x20(%rsp)
  18:	c5 78 29 4c 24 30    	vmovaps %xmm9,0x30(%rsp)
  1e:	c5 78 29 54 24 40    	vmovaps %xmm10,0x40(%rsp)
  24:	c5 78 29 5c 24 50    	vmovaps %xmm11,0x50(%rsp)
  2a:	c5 78 29 64 24 60    	vmovaps %xmm12,0x60(%rsp)
  30:	c5 78 29 6c 24 70    	vmovaps %xmm13,0x70(%rsp)
  36:	4c 8b 94 24 b0 00 00 	mov    0xb0(%rsp),%r10
  3d:	00 
  3e:	c5 f9 6e da          	vmovd  %edx,%xmm3
  42:	c4 c1 79 6e e0       	vmovd  %r8d,%xmm4
  47:	c4 e2 7d 58 db       	vpbroadcastd %xmm3,%ymm3
  4c:	c4 e2 7d 58 e4       	vpbroadcastd %xmm4,%ymm4
  51:	49 83 fa 0f          	cmp    $0xf,%r10
  55:	0f 86 9d 02 00 00    	jbe    2f8 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0x2f8>
  5b:	4d 8d 42 f0          	lea    -0x10(%r10),%r8
  5f:	c5 ed 76 d2          	vpcmpeqd %ymm2,%ymm2,%ymm2
  63:	c5 7d 6f 05 00 00 00 	vmovdqa 0x0(%rip),%ymm8        # 6b <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0x6b>
  6a:	00 
  6b:	c5 fd 6f 3d 20 00 00 	vmovdqa 0x20(%rip),%ymm7        # 93 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0x93>
  72:	00 
  73:	c5 cd 72 d2 1f       	vpsrld $0x1f,%ymm2,%ymm6
  78:	c5 d5 72 d2 18       	vpsrld $0x18,%ymm2,%ymm5
  7d:	4c 89 c2             	mov    %r8,%rdx
  80:	4c 89 c8             	mov    %r9,%rax
  83:	48 c1 ea 04          	shr    $0x4,%rdx
  87:	c5 f5 72 d2 1c       	vpsrld $0x1c,%ymm2,%ymm1
  8c:	48 8d 14 52          	lea    (%rdx,%rdx,2),%rdx
  90:	48 c1 e2 04          	shl    $0x4,%rdx
  94:	49 8d 54 11 30       	lea    0x30(%r9,%rdx,1),%rdx
  99:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  a0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
  a4:	c5 7a 7e 48 10       	vmovq  0x10(%rax),%xmm9
  a9:	c5 7d 6f ea          	vmovdqa %ymm2,%ymm13
  ad:	48 83 c0 30          	add    $0x30,%rax
  b1:	c5 7a 6f 50 e8       	vmovdqu -0x18(%rax),%xmm10
  b6:	c4 63 31 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm9,%xmm9
  bc:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
  c2:	c5 7a 7e 48 f8       	vmovq  -0x8(%rax),%xmm9
  c7:	c4 c2 7d 00 c0       	vpshufb %ymm8,%ymm0,%ymm0
  cc:	c4 43 31 0f ca 0c    	vpalignr $0xc,%xmm10,%xmm9,%xmm9
  d2:	c4 43 2d 38 d1 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm10
  d8:	c5 b5 72 d0 01       	vpsrld $0x1,%ymm0,%ymm9
  dd:	c5 fd db c6          	vpand  %ymm6,%ymm0,%ymm0
  e1:	c4 22 15 90 24 89    	vpgatherdd %ymm13,(%rcx,%ymm9,4),%ymm12
  e7:	c5 fd 72 f0 04       	vpslld $0x4,%ymm0,%ymm0
  ec:	c4 42 2d 00 d0       	vpshufb %ymm8,%ymm10,%ymm10
  f1:	c4 62 1d 45 e0       	vpsrlvd %ymm0,%ymm12,%ymm12
  f6:	c4 c1 25 72 d2 01    	vpsrld $0x1,%ymm10,%ymm11
  fc:	c5 7d 6f ea          	vmovdqa %ymm2,%ymm13
 100:	c4 22 15 90 0c 99    	vpgatherdd %ymm13,(%rcx,%ymm11,4),%ymm9
 106:	c5 2d db d6          	vpand  %ymm6,%ymm10,%ymm10
 10a:	c4 c1 7d 72 d4 08    	vpsrld $0x8,%ymm12,%ymm0
 110:	c4 c1 2d 72 f2 04    	vpslld $0x4,%ymm10,%ymm10
 116:	c5 1d db dd          	vpand  %ymm5,%ymm12,%ymm11
 11a:	c4 c1 1d 72 d4 0c    	vpsrld $0xc,%ymm12,%ymm12
 120:	c4 42 35 45 ca       	vpsrlvd %ymm10,%ymm9,%ymm9
 125:	c5 fd db c1          	vpand  %ymm1,%ymm0,%ymm0
 129:	c5 1d db e1          	vpand  %ymm1,%ymm12,%ymm12
 12d:	c5 a5 fe c0          	vpaddd %ymm0,%ymm11,%ymm0
 131:	c4 41 25 fe e4       	vpaddd %ymm12,%ymm11,%ymm12
 136:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
 13a:	c5 35 db d5          	vpand  %ymm5,%ymm9,%ymm10
 13e:	c5 1d fe e4          	vpaddd %ymm4,%ymm12,%ymm12
 142:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 147:	c4 c1 1d 72 f4 10    	vpslld $0x10,%ymm12,%ymm12
 14d:	c4 c1 7d eb c4       	vpor   %ymm12,%ymm0,%ymm0
 152:	c4 c1 7d eb c3       	vpor   %ymm11,%ymm0,%ymm0
 157:	c4 e2 7d 00 c7       	vpshufb %ymm7,%ymm0,%ymm0
 15c:	c5 79 6f e0          	vmovdqa %xmm0,%xmm12
 160:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 166:	c5 a1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm11
 16b:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 170:	c5 f9 d6 40 e0       	vmovq  %xmm0,-0x20(%rax)
 175:	c4 c1 7d 72 d1 08    	vpsrld $0x8,%ymm9,%ymm0
 17b:	c4 c1 35 72 d1 0c    	vpsrld $0xc,%ymm9,%ymm9
 181:	c4 41 21 eb dc       	vpor   %xmm12,%xmm11,%xmm11
 186:	c5 35 db c9          	vpand  %ymm1,%ymm9,%ymm9
 18a:	c5 fd db c1          	vpand  %ymm1,%ymm0,%ymm0
 18e:	c5 7a 7f 58 d0       	vmovdqu %xmm11,-0x30(%rax)
 193:	c4 41 2d fe c9       	vpaddd %ymm9,%ymm10,%ymm9
 198:	c5 ad fe c0          	vpaddd %ymm0,%ymm10,%ymm0
 19c:	c5 35 fe cc          	vpaddd %ymm4,%ymm9,%ymm9
 1a0:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
 1a4:	c4 c1 35 72 f1 10    	vpslld $0x10,%ymm9,%ymm9
 1aa:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 1af:	c4 c1 7d eb c1       	vpor   %ymm9,%ymm0,%ymm0
 1b4:	c4 c1 7d eb c2       	vpor   %ymm10,%ymm0,%ymm0
 1b9:	c4 e2 7d 00 c7       	vpshufb %ymm7,%ymm0,%ymm0
 1be:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
 1c2:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 1c8:	c5 b1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm9
 1cd:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 1d2:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 1d7:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 1dc:	c5 7a 7f 48 e8       	vmovdqu %xmm9,-0x18(%rax)
 1e1:	48 39 c2             	cmp    %rax,%rdx
 1e4:	0f 85 b6 fe ff ff    	jne    a0 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0xa0>
 1ea:	49 83 e0 f0          	and    $0xfffffffffffffff0,%r8
 1ee:	49 8d 40 10          	lea    0x10(%r8),%rax
 1f2:	4c 39 d0             	cmp    %r10,%rax
 1f5:	0f 83 bc 00 00 00    	jae    2b7 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0x2b7>
 1fb:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
 1ff:	c5 ed 76 d2          	vpcmpeqd %ymm2,%ymm2,%ymm2
 203:	c4 c1 7a 6f 04 01    	vmovdqu (%r9,%rax,1),%xmm0
 209:	c4 c1 7a 7e 4c 01 10 	vmovq  0x10(%r9,%rax,1),%xmm1
 210:	c5 fd 6f f2          	vmovdqa %ymm2,%ymm6
 214:	c4 e3 71 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm1,%xmm1
 21a:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
 220:	c4 e2 7d 00 05 00 00 	vpshufb 0x0(%rip),%ymm0,%ymm0        # 229 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0x229>
 227:	00 00 
 229:	c5 d5 72 d0 01       	vpsrld $0x1,%ymm0,%ymm5
 22e:	c4 e2 4d 90 0c a9    	vpgatherdd %ymm6,(%rcx,%ymm5,4),%ymm1
 234:	c5 d5 72 d2 1f       	vpsrld $0x1f,%ymm2,%ymm5
 239:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 23d:	c5 d5 72 d2 18       	vpsrld $0x18,%ymm2,%ymm5
 242:	c5 fd 72 f0 04       	vpslld $0x4,%ymm0,%ymm0
 247:	c5 ed 72 d2 1c       	vpsrld $0x1c,%ymm2,%ymm2
 24c:	c4 e2 75 45 c8       	vpsrlvd %ymm0,%ymm1,%ymm1
 251:	c5 f5 db ed          	vpand  %ymm5,%ymm1,%ymm5
 255:	c5 fd 72 d1 08       	vpsrld $0x8,%ymm1,%ymm0
 25a:	c5 f5 72 d1 0c       	vpsrld $0xc,%ymm1,%ymm1
 25f:	c5 fd db c2          	vpand  %ymm2,%ymm0,%ymm0
 263:	c5 f5 db ca          	vpand  %ymm2,%ymm1,%ymm1
 267:	c5 d5 fe c0          	vpaddd %ymm0,%ymm5,%ymm0
 26b:	c5 d5 fe c9          	vpaddd %ymm1,%ymm5,%ymm1
 26f:	c5 fd fe c3          	vpaddd %ymm3,%ymm0,%ymm0
 273:	c5 f5 fe cc          	vpaddd %ymm4,%ymm1,%ymm1
 277:	c5 fd 72 f0 08       	vpslld $0x8,%ymm0,%ymm0
 27c:	c5 f5 72 f1 10       	vpslld $0x10,%ymm1,%ymm1
 281:	c5 fd eb c1          	vpor   %ymm1,%ymm0,%ymm0
 285:	c5 fd eb c5          	vpor   %ymm5,%ymm0,%ymm0
 289:	c4 e2 7d 00 05 20 00 	vpshufb 0x20(%rip),%ymm0,%ymm0        # 2b2 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0x2b2>
 290:	00 00 
 292:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
 296:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 29c:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 2a1:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 2a6:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
 2aa:	c4 c1 79 d6 44 01 10 	vmovq  %xmm0,0x10(%r9,%rax,1)
 2b1:	c4 c1 7a 7f 0c 01    	vmovdqu %xmm1,(%r9,%rax,1)
 2b7:	c5 f8 77             	vzeroupper
 2ba:	c5 f8 28 34 24       	vmovaps (%rsp),%xmm6
 2bf:	c5 f8 28 7c 24 10    	vmovaps 0x10(%rsp),%xmm7
 2c5:	c5 78 28 44 24 20    	vmovaps 0x20(%rsp),%xmm8
 2cb:	c5 78 28 4c 24 30    	vmovaps 0x30(%rsp),%xmm9
 2d1:	c5 78 28 54 24 40    	vmovaps 0x40(%rsp),%xmm10
 2d7:	c5 78 28 5c 24 50    	vmovaps 0x50(%rsp),%xmm11
 2dd:	c5 78 28 64 24 60    	vmovaps 0x60(%rsp),%xmm12
 2e3:	c5 78 28 6c 24 70    	vmovaps 0x70(%rsp),%xmm13
 2e9:	48 81 c4 88 00 00 00 	add    $0x88,%rsp
 2f0:	c3                   	ret
 2f1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 2f8:	31 c0                	xor    %eax,%eax
 2fa:	e9 f3 fe ff ff       	jmp    1f2 <jshc_channel::avx2_chain_direct16(unsigned int const*, int, int, unsigned char*, unsigned long long)+0x1f2>
 2ff:	90                   	nop
