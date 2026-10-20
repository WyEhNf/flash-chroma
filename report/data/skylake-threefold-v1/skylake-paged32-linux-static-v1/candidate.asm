
artifacts/skylake-paged32-linux-build-v1/CMakeFiles/jshc_skylake_paged32.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	48 83 fa 1f          	cmp    $0x1f,%rdx
   8:	0f 86 22 02 00 00    	jbe    230 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x230>
   e:	48 8d 4a e0          	lea    -0x20(%rdx),%rcx
  12:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1a <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x1a>
  19:	00 
  1a:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 22 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x22>
  21:	00 
  22:	48 89 f0             	mov    %rsi,%rax
  25:	49 89 c8             	mov    %rcx,%r8
  28:	49 c1 e8 05          	shr    $0x5,%r8
  2c:	4f 8d 04 40          	lea    (%r8,%r8,2),%r8
  30:	49 c1 e0 05          	shl    $0x5,%r8
  34:	4e 8d 44 06 60       	lea    0x60(%rsi,%r8,1),%r8
  39:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  40:	c5 fa 6f 20          	vmovdqu (%rax),%xmm4
  44:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
  49:	c4 41 35 76 c9       	vpcmpeqd %ymm9,%ymm9,%ymm9
  4e:	48 83 c0 60          	add    $0x60,%rax
  52:	c5 fa 7e 70 c8       	vmovq  -0x38(%rax),%xmm6
  57:	c4 e3 79 0f c4 0c    	vpalignr $0xc,%xmm4,%xmm0,%xmm0
  5d:	c4 e3 5d 38 e0 01    	vinserti128 $0x1,%xmm0,%ymm4,%ymm4
  63:	c5 fa 6f 40 b8       	vmovdqu -0x48(%rax),%xmm0
  68:	c4 e2 5d 00 e3       	vpshufb %ymm3,%ymm4,%ymm4
  6d:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
  73:	c5 f9 6f c8          	vmovdqa %xmm0,%xmm1
  77:	c5 fa 6f 40 d0       	vmovdqu -0x30(%rax),%xmm0
  7c:	c4 e3 75 38 ce 01    	vinserti128 $0x1,%xmm6,%ymm1,%ymm1
  82:	c5 fa 7e 70 e0       	vmovq  -0x20(%rax),%xmm6
  87:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
  8b:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
  90:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
  96:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
  9b:	c4 63 3d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm8,%ymm8
  a1:	c5 fa 7e 70 f8       	vmovq  -0x8(%rax),%xmm6
  a6:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
  aa:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
  af:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
  b5:	c5 fd 76 c0          	vpcmpeqd %ymm0,%ymm0,%ymm0
  b9:	c4 e3 45 38 fe 01    	vinserti128 $0x1,%xmm6,%ymm7,%ymm7
  bf:	c4 e2 7d 90 34 a7    	vpgatherdd %ymm0,(%rdi,%ymm4,4),%ymm6
  c5:	c5 fd 76 c0          	vpcmpeqd %ymm0,%ymm0,%ymm0
  c9:	c4 e2 7d 90 24 8f    	vpgatherdd %ymm0,(%rdi,%ymm1,4),%ymm4
  cf:	c4 e2 4d 00 f2       	vpshufb %ymm2,%ymm6,%ymm6
  d4:	c5 fd 76 c0          	vpcmpeqd %ymm0,%ymm0,%ymm0
  d8:	c4 a2 7d 90 0c 87    	vpgatherdd %ymm0,(%rdi,%ymm8,4),%ymm1
  de:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
  e3:	c5 79 6f c6          	vmovdqa %xmm6,%xmm8
  e7:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
  ed:	c4 e2 35 90 04 bf    	vpgatherdd %ymm9,(%rdi,%ymm7,4),%ymm0
  f3:	c4 e2 5d 00 e2       	vpshufb %ymm2,%ymm4,%ymm4
  f8:	c5 c1 73 fe 0c       	vpslldq $0xc,%xmm6,%xmm7
  fd:	c5 c9 73 de 04       	vpsrldq $0x4,%xmm6,%xmm6
 102:	c4 e2 75 00 ca       	vpshufb %ymm2,%ymm1,%ymm1
 107:	c4 c1 41 eb f8       	vpor   %xmm8,%xmm7,%xmm7
 10c:	c5 f9 d6 70 b0       	vmovq  %xmm6,-0x50(%rax)
 111:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 116:	c5 fa 7f 78 a0       	vmovdqu %xmm7,-0x60(%rax)
 11b:	c5 f9 6f fc          	vmovdqa %xmm4,%xmm7
 11f:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
 125:	c5 c9 73 fc 0c       	vpslldq $0xc,%xmm4,%xmm6
 12a:	c5 d9 73 dc 04       	vpsrldq $0x4,%xmm4,%xmm4
 12f:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 133:	c5 f9 d6 60 c8       	vmovq  %xmm4,-0x38(%rax)
 138:	c5 fa 7f 70 b8       	vmovdqu %xmm6,-0x48(%rax)
 13d:	c5 f9 6f f1          	vmovdqa %xmm1,%xmm6
 141:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
 147:	c5 d9 73 f9 0c       	vpslldq $0xc,%xmm1,%xmm4
 14c:	c5 f1 73 d9 04       	vpsrldq $0x4,%xmm1,%xmm1
 151:	c5 d9 eb e6          	vpor   %xmm6,%xmm4,%xmm4
 155:	c5 f9 d6 48 e0       	vmovq  %xmm1,-0x20(%rax)
 15a:	c5 fa 7f 60 d0       	vmovdqu %xmm4,-0x30(%rax)
 15f:	c5 f9 6f e0          	vmovdqa %xmm0,%xmm4
 163:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 169:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 16e:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 173:	c5 f1 eb cc          	vpor   %xmm4,%xmm1,%xmm1
 177:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 17c:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 181:	49 39 c0             	cmp    %rax,%r8
 184:	0f 85 b6 fe ff ff    	jne    40 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x40>
 18a:	48 83 e1 e0          	and    $0xffffffffffffffe0,%rcx
 18e:	48 83 c1 20          	add    $0x20,%rcx
 192:	48 39 d1             	cmp    %rdx,%rcx
 195:	0f 83 8d 00 00 00    	jae    228 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x228>
 19b:	48 ff ca             	dec    %rdx
 19e:	4c 8d 04 49          	lea    (%rcx,%rcx,2),%r8
 1a2:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1aa <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x1aa>
 1a9:	00 
 1aa:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 1b2 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x1b2>
 1b1:	00 
 1b2:	48 29 ca             	sub    %rcx,%rdx
 1b5:	4a 8d 04 06          	lea    (%rsi,%r8,1),%rax
 1b9:	48 c1 ea 03          	shr    $0x3,%rdx
 1bd:	48 8d 0c 52          	lea    (%rdx,%rdx,2),%rcx
 1c1:	4a 8d 54 06 18       	lea    0x18(%rsi,%r8,1),%rdx
 1c6:	48 8d 14 ca          	lea    (%rdx,%rcx,8),%rdx
 1ca:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 1d0:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 1d4:	c5 fa 7e 60 10       	vmovq  0x10(%rax),%xmm4
 1d9:	c5 c5 76 ff          	vpcmpeqd %ymm7,%ymm7,%ymm7
 1dd:	48 83 c0 18          	add    $0x18,%rax
 1e1:	c4 e3 59 0f e0 0c    	vpalignr $0xc,%xmm0,%xmm4,%xmm4
 1e7:	c5 f9 6f c8          	vmovdqa %xmm0,%xmm1
 1eb:	c4 e3 75 38 cc 01    	vinserti128 $0x1,%xmm4,%ymm1,%ymm1
 1f1:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
 1f6:	c4 e2 45 90 04 8f    	vpgatherdd %ymm7,(%rdi,%ymm1,4),%ymm0
 1fc:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 201:	c5 f9 6f e0          	vmovdqa %xmm0,%xmm4
 205:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 20b:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
 210:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 215:	c5 f1 eb cc          	vpor   %xmm4,%xmm1,%xmm1
 219:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 21e:	c5 fa 7f 48 e8       	vmovdqu %xmm1,-0x18(%rax)
 223:	48 39 c2             	cmp    %rax,%rdx
 226:	75 a8                	jne    1d0 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x1d0>
 228:	c5 f8 77             	vzeroupper
 22b:	c3                   	ret
 22c:	0f 1f 40 00          	nopl   0x0(%rax)
 230:	31 c9                	xor    %ecx,%ecx
 232:	e9 5b ff ff ff       	jmp    192 <jshc_channel::avx2_chain_paged32(unsigned int const*, unsigned char*, unsigned long)+0x192>
