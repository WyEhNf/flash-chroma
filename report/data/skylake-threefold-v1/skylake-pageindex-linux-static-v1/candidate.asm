
artifacts/skylake-pageindex-linux-build-v1/CMakeFiles/jshc_skylake_pageindex.dir/channel_avx2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
   0:	f3 0f 1e fa          	endbr64
   4:	48 83 f9 1f          	cmp    $0x1f,%rcx
   8:	0f 86 e2 02 00 00    	jbe    2f0 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2f0>
   e:	4c 8d 41 e0          	lea    -0x20(%rcx),%r8
  12:	c5 d5 76 ed          	vpcmpeqd %ymm5,%ymm5,%ymm5
  16:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 1e <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1e>
  1d:	00 
  1e:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 26 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x26>
  25:	00 
  26:	c5 c5 72 d5 1e       	vpsrld $0x1e,%ymm5,%ymm7
  2b:	c5 cd 72 d5 18       	vpsrld $0x18,%ymm5,%ymm6
  30:	4d 89 c1             	mov    %r8,%r9
  33:	48 89 d0             	mov    %rdx,%rax
  36:	49 c1 e9 05          	shr    $0x5,%r9
  3a:	4f 8d 0c 49          	lea    (%r9,%r9,2),%r9
  3e:	49 c1 e1 05          	shl    $0x5,%r9
  42:	4e 8d 4c 0a 60       	lea    0x60(%rdx,%r9,1),%r9
  47:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  4e:	00 00 
  50:	c5 7a 6f 00          	vmovdqu (%rax),%xmm8
  54:	c5 fa 7e 40 10       	vmovq  0x10(%rax),%xmm0
  59:	c5 7d 6f dd          	vmovdqa %ymm5,%ymm11
  5d:	c5 7d 6f e5          	vmovdqa %ymm5,%ymm12
  61:	c5 fa 6f 60 18       	vmovdqu 0x18(%rax),%xmm4
  66:	c5 fa 6f 58 30       	vmovdqu 0x30(%rax),%xmm3
  6b:	c5 7d 6f ed          	vmovdqa %ymm5,%ymm13
  6f:	c5 7d 6f f5          	vmovdqa %ymm5,%ymm14
  73:	c4 c3 79 0f c0 0c    	vpalignr $0xc,%xmm8,%xmm0,%xmm0
  79:	c5 7a 7e 48 58       	vmovq  0x58(%rax),%xmm9
  7e:	c5 7d 6f fd          	vmovdqa %ymm5,%ymm15
  82:	48 83 c0 60          	add    $0x60,%rax
  86:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
  8c:	c5 fa 7e 40 c8       	vmovq  -0x38(%rax),%xmm0
  91:	c4 62 3d 00 c2       	vpshufb %ymm2,%ymm8,%ymm8
  96:	c4 e3 79 0f c4 0c    	vpalignr $0xc,%xmm4,%xmm0,%xmm0
  9c:	c4 c1 2d 72 d0 02    	vpsrld $0x2,%ymm8,%ymm10
  a2:	c5 3d db c7          	vpand  %ymm7,%ymm8,%ymm8
  a6:	c4 e3 5d 38 e0 01    	vinserti128 $0x1,%xmm0,%ymm4,%ymm4
  ac:	c5 fa 7e 40 e0       	vmovq  -0x20(%rax),%xmm0
  b1:	c4 c1 3d 72 f0 03    	vpslld $0x3,%ymm8,%ymm8
  b7:	c4 e2 5d 00 e2       	vpshufb %ymm2,%ymm4,%ymm4
  bc:	c4 e3 79 0f c3 0c    	vpalignr $0xc,%xmm3,%xmm0,%xmm0
  c2:	c4 e3 65 38 d8 01    	vinserti128 $0x1,%xmm0,%ymm3,%ymm3
  c8:	c5 fa 6f 40 e8       	vmovdqu -0x18(%rax),%xmm0
  cd:	c4 e2 65 00 da       	vpshufb %ymm2,%ymm3,%ymm3
  d2:	c4 63 31 0f c8 0c    	vpalignr $0xc,%xmm0,%xmm9,%xmm9
  d8:	c4 c3 7d 38 c1 01    	vinserti128 $0x1,%xmm9,%ymm0,%ymm0
  de:	c4 22 25 90 0c 97    	vpgatherdd %ymm11,(%rdi,%ymm10,4),%ymm9
  e4:	c5 7d 6f dd          	vmovdqa %ymm5,%ymm11
  e8:	c5 ad 72 d4 02       	vpsrld $0x2,%ymm4,%ymm10
  ed:	c5 dd db e7          	vpand  %ymm7,%ymm4,%ymm4
  f1:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
  f6:	c4 42 35 45 c0       	vpsrlvd %ymm8,%ymm9,%ymm8
  fb:	c5 dd 72 f4 03       	vpslld $0x3,%ymm4,%ymm4
 100:	c4 22 1d 90 0c 97    	vpgatherdd %ymm12,(%rdi,%ymm10,4),%ymm9
 106:	c5 ad 72 d3 02       	vpsrld $0x2,%ymm3,%ymm10
 10b:	c5 e5 db df          	vpand  %ymm7,%ymm3,%ymm3
 10f:	c5 7d 6f e5          	vmovdqa %ymm5,%ymm12
 113:	c4 e2 35 45 e4       	vpsrlvd %ymm4,%ymm9,%ymm4
 118:	c5 e5 72 f3 03       	vpslld $0x3,%ymm3,%ymm3
 11d:	c4 22 15 90 0c 97    	vpgatherdd %ymm13,(%rdi,%ymm10,4),%ymm9
 123:	c5 ad 72 d0 02       	vpsrld $0x2,%ymm0,%ymm10
 128:	c5 fd db c7          	vpand  %ymm7,%ymm0,%ymm0
 12c:	c5 7d 6f ed          	vmovdqa %ymm5,%ymm13
 130:	c4 e2 35 45 db       	vpsrlvd %ymm3,%ymm9,%ymm3
 135:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 13a:	c4 22 0d 90 0c 97    	vpgatherdd %ymm14,(%rdi,%ymm10,4),%ymm9
 140:	c4 62 35 45 c8       	vpsrlvd %ymm0,%ymm9,%ymm9
 145:	c5 bd db c6          	vpand  %ymm6,%ymm8,%ymm0
 149:	c4 62 05 90 04 86    	vpgatherdd %ymm15,(%rsi,%ymm0,4),%ymm8
 14f:	c5 dd db c6          	vpand  %ymm6,%ymm4,%ymm0
 153:	c4 62 3d 00 c1       	vpshufb %ymm1,%ymm8,%ymm8
 158:	c4 e2 25 90 24 86    	vpgatherdd %ymm11,(%rsi,%ymm0,4),%ymm4
 15e:	c5 35 db ce          	vpand  %ymm6,%ymm9,%ymm9
 162:	c5 e5 db c6          	vpand  %ymm6,%ymm3,%ymm0
 166:	c4 41 79 6f d0       	vmovdqa %xmm8,%xmm10
 16b:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
 171:	c4 e2 1d 90 1c 86    	vpgatherdd %ymm12,(%rsi,%ymm0,4),%ymm3
 177:	c4 a2 15 90 04 8e    	vpgatherdd %ymm13,(%rsi,%ymm9,4),%ymm0
 17d:	c4 e2 5d 00 e1       	vpshufb %ymm1,%ymm4,%ymm4
 182:	c4 c1 31 73 f8 0c    	vpslldq $0xc,%xmm8,%xmm9
 188:	c4 c1 39 73 d8 04    	vpsrldq $0x4,%xmm8,%xmm8
 18e:	c4 e2 65 00 d9       	vpshufb %ymm1,%ymm3,%ymm3
 193:	c4 41 31 eb ca       	vpor   %xmm10,%xmm9,%xmm9
 198:	c5 79 d6 40 b0       	vmovq  %xmm8,-0x50(%rax)
 19d:	c4 e2 7d 00 c1       	vpshufb %ymm1,%ymm0,%ymm0
 1a2:	c5 7a 7f 48 a0       	vmovdqu %xmm9,-0x60(%rax)
 1a7:	c5 79 6f cc          	vmovdqa %xmm4,%xmm9
 1ab:	c4 e3 7d 39 e4 01    	vextracti128 $0x1,%ymm4,%xmm4
 1b1:	c5 b9 73 fc 0c       	vpslldq $0xc,%xmm4,%xmm8
 1b6:	c5 d9 73 dc 04       	vpsrldq $0x4,%xmm4,%xmm4
 1bb:	c4 41 39 eb c1       	vpor   %xmm9,%xmm8,%xmm8
 1c0:	c5 f9 d6 60 c8       	vmovq  %xmm4,-0x38(%rax)
 1c5:	c5 7a 7f 40 b8       	vmovdqu %xmm8,-0x48(%rax)
 1ca:	c5 79 6f c3          	vmovdqa %xmm3,%xmm8
 1ce:	c4 e3 7d 39 db 01    	vextracti128 $0x1,%ymm3,%xmm3
 1d4:	c5 d9 73 fb 0c       	vpslldq $0xc,%xmm3,%xmm4
 1d9:	c5 e1 73 db 04       	vpsrldq $0x4,%xmm3,%xmm3
 1de:	c4 c1 59 eb e0       	vpor   %xmm8,%xmm4,%xmm4
 1e3:	c5 f9 d6 58 e0       	vmovq  %xmm3,-0x20(%rax)
 1e8:	c5 fa 7f 60 d0       	vmovdqu %xmm4,-0x30(%rax)
 1ed:	c5 f9 6f e0          	vmovdqa %xmm0,%xmm4
 1f1:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 1f7:	c5 e1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm3
 1fc:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 201:	c5 e1 eb dc          	vpor   %xmm4,%xmm3,%xmm3
 205:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 20a:	c5 fa 7f 58 e8       	vmovdqu %xmm3,-0x18(%rax)
 20f:	49 39 c1             	cmp    %rax,%r9
 212:	0f 85 38 fe ff ff    	jne    50 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x50>
 218:	49 83 e0 e0          	and    $0xffffffffffffffe0,%r8
 21c:	49 83 c0 20          	add    $0x20,%r8
 220:	49 39 c8             	cmp    %rcx,%r8
 223:	0f 83 bc 00 00 00    	jae    2e5 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x2e5>
 229:	48 ff c9             	dec    %rcx
 22c:	4f 8d 0c 40          	lea    (%r8,%r8,2),%r9
 230:	c5 e5 76 db          	vpcmpeqd %ymm3,%ymm3,%ymm3
 234:	c5 fd 6f 15 00 00 00 	vmovdqa 0x0(%rip),%ymm2        # 23c <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x23c>
 23b:	00 
 23c:	4c 29 c1             	sub    %r8,%rcx
 23f:	c5 fd 6f 0d 00 00 00 	vmovdqa 0x0(%rip),%ymm1        # 247 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x247>
 246:	00 
 247:	c5 d5 72 d3 1e       	vpsrld $0x1e,%ymm3,%ymm5
 24c:	4a 8d 04 0a          	lea    (%rdx,%r9,1),%rax
 250:	48 c1 e9 03          	shr    $0x3,%rcx
 254:	c5 dd 72 d3 18       	vpsrld $0x18,%ymm3,%ymm4
 259:	4a 8d 54 0a 18       	lea    0x18(%rdx,%r9,1),%rdx
 25e:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
 262:	48 8d 14 ca          	lea    (%rdx,%rcx,8),%rdx
 266:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 26d:	00 00 00 
 270:	c5 fa 6f 00          	vmovdqu (%rax),%xmm0
 274:	c5 fa 7e 70 10       	vmovq  0x10(%rax),%xmm6
 279:	c5 7d 6f f3          	vmovdqa %ymm3,%ymm14
 27d:	48 83 c0 18          	add    $0x18,%rax
 281:	c4 e3 49 0f f0 0c    	vpalignr $0xc,%xmm0,%xmm6,%xmm6
 287:	c4 e3 7d 38 c6 01    	vinserti128 $0x1,%xmm6,%ymm0,%ymm0
 28d:	c4 e2 7d 00 c2       	vpshufb %ymm2,%ymm0,%ymm0
 292:	c5 c5 72 d0 02       	vpsrld $0x2,%ymm0,%ymm7
 297:	c5 fd db c5          	vpand  %ymm5,%ymm0,%ymm0
 29b:	c4 e2 0d 90 34 bf    	vpgatherdd %ymm14,(%rdi,%ymm7,4),%ymm6
 2a1:	c5 fd 72 f0 03       	vpslld $0x3,%ymm0,%ymm0
 2a6:	c5 fd 6f fb          	vmovdqa %ymm3,%ymm7
 2aa:	c4 e2 4d 45 f0       	vpsrlvd %ymm0,%ymm6,%ymm6
 2af:	c5 cd db f4          	vpand  %ymm4,%ymm6,%ymm6
 2b3:	c4 e2 45 90 04 b6    	vpgatherdd %ymm7,(%rsi,%ymm6,4),%ymm0
 2b9:	c4 e2 7d 00 c1       	vpshufb %ymm1,%ymm0,%ymm0
 2be:	c5 f9 6f f8          	vmovdqa %xmm0,%xmm7
 2c2:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
 2c8:	c5 c9 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm6
 2cd:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
 2d2:	c5 c9 eb f7          	vpor   %xmm7,%xmm6,%xmm6
 2d6:	c5 f9 d6 40 f8       	vmovq  %xmm0,-0x8(%rax)
 2db:	c5 fa 7f 70 e8       	vmovdqu %xmm6,-0x18(%rax)
 2e0:	48 39 c2             	cmp    %rax,%rdx
 2e3:	75 8b                	jne    270 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x270>
 2e5:	c5 f8 77             	vzeroupper
 2e8:	c3                   	ret
 2e9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 2f0:	45 31 c0             	xor    %r8d,%r8d
 2f3:	e9 28 ff ff ff       	jmp    220 <jshc_channel::avx2_chain_pageindex(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x220>
