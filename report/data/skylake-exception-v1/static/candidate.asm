
artifacts\skylake-exception-build-v1\CMakeFiles\jshc_skylake_exception.dir\channel_avx2.cpp.obj:     file format pe-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_exception(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)>:
   0:	48 81 ec 88 00 00 00 	sub    $0x88,%rsp
   7:	c5 f8 29 34 24       	vmovaps %xmm6,(%rsp)
   c:	c5 f8 29 7c 24 10    	vmovaps %xmm7,0x10(%rsp)
  12:	c5 78 29 44 24 20    	vmovaps %xmm8,0x20(%rsp)
  18:	c5 78 29 4c 24 30    	vmovaps %xmm9,0x30(%rsp)
  1e:	c5 78 29 54 24 40    	vmovaps %xmm10,0x40(%rsp)
  24:	c5 78 29 5c 24 50    	vmovaps %xmm11,0x50(%rsp)
  2a:	c5 78 29 64 24 60    	vmovaps %xmm12,0x60(%rsp)
  30:	c5 78 29 6c 24 70    	vmovaps %xmm13,0x70(%rsp)
  36:	48 8b 84 24 b0 00 00 	mov    0xb0(%rsp),%rax
  3d:	00 
  3e:	49 89 d2             	mov    %rdx,%r10
  41:	48 85 c0             	test   %rax,%rax
  44:	0f 84 23 01 00 00    	je     16d <jshc_channel::avx2_chain_exception(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x16d>
  4a:	48 ff c8             	dec    %rax
  4d:	c5 ed 76 d2          	vpcmpeqd %ymm2,%ymm2,%ymm2
  51:	c5 fd 6f 3d 00 00 00 	vmovdqa 0x0(%rip),%ymm7        # 59 <jshc_channel::avx2_chain_exception(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x59>
  58:	00 
  59:	c5 fd 6f 35 20 00 00 	vmovdqa 0x20(%rip),%ymm6        # 81 <jshc_channel::avx2_chain_exception(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x81>
  60:	00 
  61:	c5 e5 72 d2 18       	vpsrld $0x18,%ymm2,%ymm3
  66:	48 c1 e8 03          	shr    $0x3,%rax
  6a:	c5 dd 72 d2 1d       	vpsrld $0x1d,%ymm2,%ymm4
  6f:	c5 b5 72 d2 1f       	vpsrld $0x1f,%ymm2,%ymm9
  74:	c5 bd 72 d2 1e       	vpsrld $0x1e,%ymm2,%ymm8
  79:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
  7d:	49 8d 54 c1 18       	lea    0x18(%r9,%rax,8),%rdx
  82:	b8 08 00 00 00       	mov    $0x8,%eax
  87:	c5 f9 6e e8          	vmovd  %eax,%xmm5
  8b:	c4 e2 7d 58 ed       	vpbroadcastd %xmm5,%ymm5
  90:	c4 c1 7a 6f 09       	vmovdqu (%r9),%xmm1
  95:	c4 c1 7a 7e 41 10    	vmovq  0x10(%r9),%xmm0
  9b:	c5 7d 6f ea          	vmovdqa %ymm2,%ymm13
  9f:	c4 e3 79 0f c1 0c    	vpalignr $0xc,%xmm1,%xmm0,%xmm0
  a5:	c4 e3 75 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm1,%ymm1
  ab:	c4 e2 75 00 cf       	vpshufb %ymm7,%ymm1,%ymm1
  b0:	c5 fd 72 d1 03       	vpsrld $0x3,%ymm1,%ymm0
  b5:	c5 5d db e1          	vpand  %ymm1,%ymm4,%ymm12
  b9:	c4 62 15 90 14 81    	vpgatherdd %ymm13,(%rcx,%ymm0,4),%ymm10
  bf:	c4 c1 7d 72 f4 01    	vpslld $0x1,%ymm12,%ymm0
  c5:	c5 fd fe c5          	vpaddd %ymm5,%ymm0,%ymm0
  c9:	c5 2d db db          	vpand  %ymm3,%ymm10,%ymm11
  cd:	c4 c1 7d fe c4       	vpaddd %ymm12,%ymm0,%ymm0
  d2:	c4 e2 2d 45 c0       	vpsrlvd %ymm0,%ymm10,%ymm0
  d7:	c5 fd db c4          	vpand  %ymm4,%ymm0,%ymm0
  db:	c4 c1 7d fe c3       	vpaddd %ymm11,%ymm0,%ymm0
  e0:	c5 25 76 db          	vpcmpeqd %ymm3,%ymm11,%ymm11
  e4:	c4 c1 7d d7 c3       	vpmovmskb %ymm11,%eax
  e9:	85 c0                	test   %eax,%eax
  eb:	74 3c                	je     129 <jshc_channel::avx2_chain_exception(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x129>
  ed:	c5 9d 72 d1 02       	vpsrld $0x2,%ymm1,%ymm12
  f2:	c4 c1 2d 72 d2 08    	vpsrld $0x8,%ymm10,%ymm10
  f8:	c5 7d 6f ea          	vmovdqa %ymm2,%ymm13
  fc:	c4 41 1d db e1       	vpand  %ymm9,%ymm12,%ymm12
 101:	c4 41 2d db d3       	vpand  %ymm11,%ymm10,%ymm10
 106:	c5 bd db c9          	vpand  %ymm1,%ymm8,%ymm1
 10a:	c4 41 2d fe d4       	vpaddd %ymm12,%ymm10,%ymm10
 10f:	c5 f5 72 f1 03       	vpslld $0x3,%ymm1,%ymm1
 114:	c4 02 15 90 24 92    	vpgatherdd %ymm13,(%r10,%ymm10,4),%ymm12
 11a:	c4 e2 1d 45 c9       	vpsrlvd %ymm1,%ymm12,%ymm1
 11f:	c5 f5 db cb          	vpand  %ymm3,%ymm1,%ymm1
 123:	c4 e3 7d 4c c1 b0    	vpblendvb %ymm11,%ymm1,%ymm0,%ymm0
 129:	c5 7d 6f ea          	vmovdqa %ymm2,%ymm13
 12d:	49 83 c1 18          	add    $0x18,%r9
 131:	c4 c2 15 90 0c 80    	vpgatherdd %ymm13,(%r8,%ymm0,4),%ymm1
 137:	c4 e2 75 00 c6       	vpshufb %ymm6,%ymm1,%ymm0
 13c:	c5 79 6f d0          	vmovdqa %xmm0,%xmm10
 140:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 146:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 14b:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 150:	c4 c1 71 eb ca       	vpor   %xmm10,%xmm1,%xmm1
 155:	c4 c1 79 d6 41 f8    	vmovq  %xmm0,-0x8(%r9)
 15b:	c4 c1 7a 7f 49 e8    	vmovdqu %xmm1,-0x18(%r9)
 161:	49 39 d1             	cmp    %rdx,%r9
 164:	0f 85 26 ff ff ff    	jne    90 <jshc_channel::avx2_chain_exception(unsigned int const*, unsigned int const*, unsigned int const*, unsigned char*, unsigned long long)+0x90>
 16a:	c5 f8 77             	vzeroupper
 16d:	c5 f8 28 34 24       	vmovaps (%rsp),%xmm6
 172:	c5 f8 28 7c 24 10    	vmovaps 0x10(%rsp),%xmm7
 178:	c5 78 28 44 24 20    	vmovaps 0x20(%rsp),%xmm8
 17e:	c5 78 28 4c 24 30    	vmovaps 0x30(%rsp),%xmm9
 184:	c5 78 28 54 24 40    	vmovaps 0x40(%rsp),%xmm10
 18a:	c5 78 28 5c 24 50    	vmovaps 0x50(%rsp),%xmm11
 190:	c5 78 28 64 24 60    	vmovaps 0x60(%rsp),%xmm12
 196:	c5 78 28 6c 24 70    	vmovaps 0x70(%rsp),%xmm13
 19c:	48 81 c4 88 00 00 00 	add    $0x88,%rsp
 1a3:	c3                   	ret
 1a4:	90                   	nop
 1a5:	90                   	nop
 1a6:	90                   	nop
 1a7:	90                   	nop
 1a8:	90                   	nop
 1a9:	90                   	nop
 1aa:	90                   	nop
 1ab:	90                   	nop
 1ac:	90                   	nop
 1ad:	90                   	nop
 1ae:	90                   	nop
 1af:	90                   	nop
