
artifacts/skylake-tilebmi2-linux-build-v1/CMakeFiles/jshc_skylake_tilebmi2.dir/channel_bmi2.cpp.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)>:
       0:	f3 0f 1e fa          	endbr64
       4:	55                   	push   %rbp
       5:	48 89 e5             	mov    %rsp,%rbp
       8:	41 57                	push   %r15
       a:	41 56                	push   %r14
       c:	41 55                	push   %r13
       e:	41 54                	push   %r12
      10:	53                   	push   %rbx
      11:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
      15:	48 81 ec 88 00 00 00 	sub    $0x88,%rsp
      1c:	48 89 8c 24 80 00 00 	mov    %rcx,0x80(%rsp)
      23:	00 
      24:	48 85 c9             	test   %rcx,%rcx
      27:	0f 84 76 18 00 00    	je     18a3 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a3>
      2d:	48 8d 0c 49          	lea    (%rcx,%rcx,2),%rcx
      31:	48 89 d0             	mov    %rdx,%rax
      34:	ba 00 04 00 00       	mov    $0x400,%edx
      39:	49 89 ff             	mov    %rdi,%r15
      3c:	48 39 d1             	cmp    %rdx,%rcx
      3f:	49 89 f6             	mov    %rsi,%r14
      42:	48 0f 47 ca          	cmova  %rdx,%rcx
      46:	31 d2                	xor    %edx,%edx
      48:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
      4f:	00 
      50:	0f 18 04 10          	prefetchnta (%rax,%rdx,1)
      54:	48 83 c2 40          	add    $0x40,%rdx
      58:	48 39 ca             	cmp    %rcx,%rdx
      5b:	72 f3                	jb     50 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x50>
      5d:	4c 8b 8c 24 80 00 00 	mov    0x80(%rsp),%r9
      64:	00 
      65:	48 89 c1             	mov    %rax,%rcx
      68:	45 31 c0             	xor    %r8d,%r8d
      6b:	bf fc fc fc 00       	mov    $0xfcfcfc,%edi
      70:	be 03 03 03 00       	mov    $0x30303,%esi
      75:	eb 60                	jmp    d7 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd7>
      77:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
      7e:	00 00 
      80:	0f b6 51 01          	movzbl 0x1(%rcx),%edx
      84:	44 0f b6 51 02       	movzbl 0x2(%rcx),%r10d
      89:	49 ff c0             	inc    %r8
      8c:	48 83 c1 03          	add    $0x3,%rcx
      90:	41 c1 e2 10          	shl    $0x10,%r10d
      94:	c1 e2 08             	shl    $0x8,%edx
      97:	44 09 d2             	or     %r10d,%edx
      9a:	44 0f b6 51 fd       	movzbl -0x3(%rcx),%r10d
      9f:	44 09 d2             	or     %r10d,%edx
      a2:	c4 62 6a f5 d7       	pext   %edi,%edx,%r10d
      a7:	41 c1 e2 06          	shl    $0x6,%r10d
      ab:	c4 e2 6a f5 d6       	pext   %esi,%edx,%edx
      b0:	44 09 d2             	or     %r10d,%edx
      b3:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
      b8:	4d 8d 14 96          	lea    (%r14,%rdx,4),%r10
      bc:	41 8b 12             	mov    (%r10),%edx
      bf:	45 0f b7 12          	movzwl (%r10),%r10d
      c3:	c1 ea 10             	shr    $0x10,%edx
      c6:	66 44 89 51 fd       	mov    %r10w,-0x3(%rcx)
      cb:	88 51 ff             	mov    %dl,-0x1(%rcx)
      ce:	4d 39 c1             	cmp    %r8,%r9
      d1:	0f 84 e1 17 00 00    	je     18b8 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18b8>
      d7:	f6 c1 3f             	test   $0x3f,%cl
      da:	75 a4                	jne    80 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x80>
      dc:	49 8d 50 48          	lea    0x48(%r8),%rdx
      e0:	4c 89 44 24 78       	mov    %r8,0x78(%rsp)
      e5:	48 39 94 24 80 00 00 	cmp    %rdx,0x80(%rsp)
      ec:	00 
      ed:	0f 82 d2 17 00 00    	jb     18c5 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18c5>
      f3:	4b 8d 14 40          	lea    (%r8,%r8,2),%rdx
      f7:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
      fc:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 104 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x104>
     103:	00 
     104:	41 bc fc fc fc 00    	mov    $0xfcfcfc,%r12d
     10a:	4c 8d 2c 10          	lea    (%rax,%rdx,1),%r13
     10e:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 116 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x116>
     115:	00 
     116:	bb 03 03 03 00       	mov    $0x30303,%ebx
     11b:	4c 89 c0             	mov    %r8,%rax
     11e:	eb 08                	jmp    128 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x128>
     120:	4c 89 5c 24 78       	mov    %r11,0x78(%rsp)
     125:	4c 89 d8             	mov    %r11,%rax
     128:	48 05 96 01 00 00    	add    $0x196,%rax
     12e:	48 39 84 24 80 00 00 	cmp    %rax,0x80(%rsp)
     135:	00 
     136:	72 20                	jb     158 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x158>
     138:	41 0f 18 85 00 04 00 	prefetchnta 0x400(%r13)
     13f:	00 
     140:	41 0f 18 85 40 04 00 	prefetchnta 0x440(%r13)
     147:	00 
     148:	41 0f 18 85 80 04 00 	prefetchnta 0x480(%r13)
     14f:	00 
     150:	41 0f 18 85 bf 04 00 	prefetchnta 0x4bf(%r13)
     157:	00 
     158:	41 8b 45 15          	mov    0x15(%r13),%eax
     15c:	45 8b 5d 00          	mov    0x0(%r13),%r11d
     160:	45 8b 4d 06          	mov    0x6(%r13),%r9d
     164:	45 8b 45 09          	mov    0x9(%r13),%r8d
     168:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     16d:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     172:	89 44 24 70          	mov    %eax,0x70(%rsp)
     176:	41 8b 45 12          	mov    0x12(%r13),%eax
     17a:	89 74 24 74          	mov    %esi,0x74(%rsp)
     17e:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     183:	c1 e6 06             	shl    $0x6,%esi
     186:	45 8b 55 03          	mov    0x3(%r13),%r10d
     18a:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     18f:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     194:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     198:	41 8b 45 0f          	mov    0xf(%r13),%eax
     19c:	41 8b 7d 0c          	mov    0xc(%r13),%edi
     1a0:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     1a4:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     1a9:	44 09 de             	or     %r11d,%esi
     1ac:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     1b1:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     1b6:	89 54 24 60          	mov    %edx,0x60(%rsp)
     1ba:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     1bf:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     1c4:	89 44 24 58          	mov    %eax,0x58(%rsp)
     1c8:	c1 e2 06             	shl    $0x6,%edx
     1cb:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     1d0:	44 09 ca             	or     %r9d,%edx
     1d3:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     1d8:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     1dd:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     1e1:	c1 e0 06             	shl    $0x6,%eax
     1e4:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     1e9:	c1 e1 06             	shl    $0x6,%ecx
     1ec:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     1f1:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     1f6:	44 09 c0             	or     %r8d,%eax
     1f9:	41 c1 e1 06          	shl    $0x6,%r9d
     1fd:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     202:	44 09 d1             	or     %r10d,%ecx
     205:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     20a:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     20f:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     214:	41 c1 e3 06          	shl    $0x6,%r11d
     218:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     21d:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     222:	45 89 d8             	mov    %r11d,%r8d
     225:	41 c1 e2 06          	shl    $0x6,%r10d
     229:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     22e:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     233:	41 09 f8             	or     %edi,%r8d
     236:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     23b:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
     241:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     246:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     24b:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     250:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     255:	41 c1 e0 06          	shl    $0x6,%r8d
     259:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     25e:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
     265:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     26a:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
     270:	c4 41 79 6e 0c b6    	vmovd  (%r14,%rsi,4),%xmm9
     276:	45 8b 5d 18          	mov    0x18(%r13),%r11d
     27a:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
     281:	45 8b 45 21          	mov    0x21(%r13),%r8d
     285:	c4 43 31 22 0c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm9,%xmm9
     28c:	45 8b 4d 1e          	mov    0x1e(%r13),%r9d
     290:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     294:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
     29a:	45 8b 55 1b          	mov    0x1b(%r13),%r10d
     29e:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
     2a5:	41 8b 45 2d          	mov    0x2d(%r13),%eax
     2a9:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     2ae:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     2b3:	89 44 24 70          	mov    %eax,0x70(%rsp)
     2b7:	41 8b 45 2a          	mov    0x2a(%r13),%eax
     2bb:	89 74 24 74          	mov    %esi,0x74(%rsp)
     2bf:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     2c4:	c1 e6 06             	shl    $0x6,%esi
     2c7:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     2cc:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     2d1:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     2d6:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     2da:	41 8b 45 27          	mov    0x27(%r13),%eax
     2de:	41 8b 7d 24          	mov    0x24(%r13),%edi
     2e2:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     2e6:	44 09 de             	or     %r11d,%esi
     2e9:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
     2ed:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     2f2:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     2f7:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     2fb:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     300:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     305:	89 44 24 58          	mov    %eax,0x58(%rsp)
     309:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     30e:	c1 e0 06             	shl    $0x6,%eax
     311:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     316:	44 09 c0             	or     %r8d,%eax
     319:	89 54 24 60          	mov    %edx,0x60(%rsp)
     31d:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     322:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     327:	c1 e2 06             	shl    $0x6,%edx
     32a:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     32f:	c1 e1 06             	shl    $0x6,%ecx
     332:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     337:	44 09 ca             	or     %r9d,%edx
     33a:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     33f:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     344:	44 09 d1             	or     %r10d,%ecx
     347:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     34c:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     351:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
     357:	41 c1 e3 06          	shl    $0x6,%r11d
     35b:	41 c1 e1 06          	shl    $0x6,%r9d
     35f:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     364:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     369:	45 89 d8             	mov    %r11d,%r8d
     36c:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     371:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
     376:	41 09 f8             	or     %edi,%r8d
     379:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
     37e:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     383:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     388:	41 c1 e0 06          	shl    $0x6,%r8d
     38c:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     391:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     396:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     39b:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     3a0:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
     3a6:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
     3ac:	c4 c1 79 6e 34 b6    	vmovd  (%r14,%rsi,4),%xmm6
     3b2:	41 c1 e2 06          	shl    $0x6,%r10d
     3b6:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
     3bd:	45 8b 5d 30          	mov    0x30(%r13),%r11d
     3c1:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     3c6:	c4 c3 49 22 34 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm6,%xmm6
     3cd:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     3d2:	45 8b 45 39          	mov    0x39(%r13),%r8d
     3d6:	45 8b 4d 36          	mov    0x36(%r13),%r9d
     3da:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
     3e1:	45 8b 55 33          	mov    0x33(%r13),%r10d
     3e5:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     3e9:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
     3ef:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
     3f6:	41 8b 45 45          	mov    0x45(%r13),%eax
     3fa:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     3ff:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     404:	89 44 24 70          	mov    %eax,0x70(%rsp)
     408:	41 8b 45 42          	mov    0x42(%r13),%eax
     40c:	89 74 24 74          	mov    %esi,0x74(%rsp)
     410:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     415:	c1 e6 06             	shl    $0x6,%esi
     418:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     41d:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     422:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     427:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     42b:	41 8b 45 3f          	mov    0x3f(%r13),%eax
     42f:	41 8b 7d 3c          	mov    0x3c(%r13),%edi
     433:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     437:	44 09 de             	or     %r11d,%esi
     43a:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
     43e:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     443:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     448:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     44c:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     451:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     456:	89 44 24 58          	mov    %eax,0x58(%rsp)
     45a:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     45f:	c1 e0 06             	shl    $0x6,%eax
     462:	89 54 24 60          	mov    %edx,0x60(%rsp)
     466:	c1 e1 06             	shl    $0x6,%ecx
     469:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     46e:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     473:	44 09 c0             	or     %r8d,%eax
     476:	c1 e2 06             	shl    $0x6,%edx
     479:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     47e:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     483:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     488:	44 09 ca             	or     %r9d,%edx
     48b:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     490:	44 09 d1             	or     %r10d,%ecx
     493:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     498:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     49d:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
     4a3:	41 c1 e3 06          	shl    $0x6,%r11d
     4a7:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     4ac:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     4b1:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
     4b6:	45 89 d8             	mov    %r11d,%r8d
     4b9:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
     4be:	41 09 f8             	or     %edi,%r8d
     4c1:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
     4c5:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
     4cb:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     4d0:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     4d5:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
     4db:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     4e0:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     4e5:	41 c1 e1 06          	shl    $0x6,%r9d
     4e9:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
     4ef:	c4 c1 79 6e 2c b6    	vmovd  (%r14,%rsi,4),%xmm5
     4f5:	41 c1 e0 06          	shl    $0x6,%r8d
     4f9:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     4fe:	41 c1 e2 06          	shl    $0x6,%r10d
     502:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     507:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     50c:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     511:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     516:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     51b:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
     521:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
     528:	c4 c3 51 22 2c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm5,%xmm5
     52f:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
     536:	45 8b 45 51          	mov    0x51(%r13),%r8d
     53a:	45 8b 4d 4e          	mov    0x4e(%r13),%r9d
     53e:	45 8b 55 4b          	mov    0x4b(%r13),%r10d
     542:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     546:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
     54c:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
     553:	41 8b 45 5d          	mov    0x5d(%r13),%eax
     557:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     55c:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     561:	89 44 24 70          	mov    %eax,0x70(%rsp)
     565:	41 8b 45 5a          	mov    0x5a(%r13),%eax
     569:	89 74 24 74          	mov    %esi,0x74(%rsp)
     56d:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
     571:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     576:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     57b:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     57f:	41 8b 45 57          	mov    0x57(%r13),%eax
     583:	41 8b 7d 54          	mov    0x54(%r13),%edi
     587:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     58b:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
     591:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     596:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     59b:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     59f:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     5a4:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     5a9:	89 54 24 60          	mov    %edx,0x60(%rsp)
     5ad:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     5b2:	c1 e2 06             	shl    $0x6,%edx
     5b5:	89 44 24 58          	mov    %eax,0x58(%rsp)
     5b9:	45 8b 5d 48          	mov    0x48(%r13),%r11d
     5bd:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     5c2:	c1 e0 06             	shl    $0x6,%eax
     5c5:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     5ca:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     5cf:	44 09 c0             	or     %r8d,%eax
     5d2:	44 09 ca             	or     %r9d,%edx
     5d5:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     5da:	c1 e6 06             	shl    $0x6,%esi
     5dd:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     5e2:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     5e7:	44 09 de             	or     %r11d,%esi
     5ea:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     5ef:	c1 e1 06             	shl    $0x6,%ecx
     5f2:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     5f7:	41 c1 e1 06          	shl    $0x6,%r9d
     5fb:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     600:	44 09 d1             	or     %r10d,%ecx
     603:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     608:	41 c1 e3 06          	shl    $0x6,%r11d
     60c:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     611:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     616:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
     61b:	45 89 d8             	mov    %r11d,%r8d
     61e:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     623:	41 c1 e2 06          	shl    $0x6,%r10d
     627:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     62c:	41 09 f8             	or     %edi,%r8d
     62f:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     634:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     639:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
     63e:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     643:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     648:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
     64c:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
     652:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     657:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
     65d:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
     663:	41 c1 e0 06          	shl    $0x6,%r8d
     667:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
     66d:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     672:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     677:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
     67e:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     683:	c4 41 79 6e 04 b6    	vmovd  (%r14,%rsi,4),%xmm8
     689:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
     690:	c4 43 39 22 04 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm8,%xmm8
     697:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     69b:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
     6a1:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
     6a8:	41 8b 45 75          	mov    0x75(%r13),%eax
     6ac:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     6b1:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     6b6:	89 44 24 70          	mov    %eax,0x70(%rsp)
     6ba:	41 8b 45 72          	mov    0x72(%r13),%eax
     6be:	89 74 24 74          	mov    %esi,0x74(%rsp)
     6c2:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
     6c6:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     6cb:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     6d0:	41 8b 45 6f          	mov    0x6f(%r13),%eax
     6d4:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     6d8:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     6dc:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
     6e2:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     6e7:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     6ec:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     6f0:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
     6f5:	89 54 24 60          	mov    %edx,0x60(%rsp)
     6f9:	41 8b 7d 6c          	mov    0x6c(%r13),%edi
     6fd:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
     702:	45 8b 5d 60          	mov    0x60(%r13),%r11d
     706:	45 8b 45 69          	mov    0x69(%r13),%r8d
     70a:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     70f:	45 8b 4d 66          	mov    0x66(%r13),%r9d
     713:	45 8b 55 63          	mov    0x63(%r13),%r10d
     717:	89 44 24 58          	mov    %eax,0x58(%rsp)
     71b:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     720:	c1 e6 06             	shl    $0x6,%esi
     723:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     728:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     72d:	44 09 de             	or     %r11d,%esi
     730:	c1 e0 06             	shl    $0x6,%eax
     733:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     738:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     73d:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     742:	c1 e2 06             	shl    $0x6,%edx
     745:	44 09 c0             	or     %r8d,%eax
     748:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     74d:	44 09 ca             	or     %r9d,%edx
     750:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     755:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     75a:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     75f:	41 c1 e3 06          	shl    $0x6,%r11d
     763:	c1 e1 06             	shl    $0x6,%ecx
     766:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     76b:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     770:	45 89 d8             	mov    %r11d,%r8d
     773:	44 09 d1             	or     %r10d,%ecx
     776:	41 c1 e1 06          	shl    $0x6,%r9d
     77a:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     77f:	41 09 f8             	or     %edi,%r8d
     782:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     787:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     78c:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     791:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     796:	41 c1 e2 06          	shl    $0x6,%r10d
     79a:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     79f:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     7a4:	41 c1 e0 06          	shl    $0x6,%r8d
     7a8:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     7ad:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
     7b3:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     7b8:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
     7be:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     7c3:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     7c8:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
     7cf:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     7d4:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
     7db:	c4 c1 79 6e 3c b6    	vmovd  (%r14,%rsi,4),%xmm7
     7e1:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
     7e5:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
     7eb:	c4 c3 41 22 3c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm7,%xmm7
     7f2:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
     7f9:	41 8b 85 8d 00 00 00 	mov    0x8d(%r13),%eax
     800:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     805:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     80a:	89 74 24 74          	mov    %esi,0x74(%rsp)
     80e:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
     812:	89 44 24 70          	mov    %eax,0x70(%rsp)
     816:	41 8b 85 8a 00 00 00 	mov    0x8a(%r13),%eax
     81d:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
     823:	45 8b 5d 78          	mov    0x78(%r13),%r11d
     827:	45 8b 85 81 00 00 00 	mov    0x81(%r13),%r8d
     82e:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
     833:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     838:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     83d:	41 8b 85 87 00 00 00 	mov    0x87(%r13),%eax
     844:	45 8b 4d 7e          	mov    0x7e(%r13),%r9d
     848:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     84c:	41 8b bd 84 00 00 00 	mov    0x84(%r13),%edi
     853:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     858:	c1 e6 06             	shl    $0x6,%esi
     85b:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     85f:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     864:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     869:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     86e:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     873:	89 44 24 58          	mov    %eax,0x58(%rsp)
     877:	44 09 de             	or     %r11d,%esi
     87a:	45 8b 55 7b          	mov    0x7b(%r13),%r10d
     87e:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     882:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     887:	c1 e0 06             	shl    $0x6,%eax
     88a:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     88f:	89 54 24 60          	mov    %edx,0x60(%rsp)
     893:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     898:	c1 e2 06             	shl    $0x6,%edx
     89b:	44 09 c0             	or     %r8d,%eax
     89e:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     8a3:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     8a8:	44 09 ca             	or     %r9d,%edx
     8ab:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     8b0:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     8b5:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     8ba:	c1 e1 06             	shl    $0x6,%ecx
     8bd:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     8c2:	41 c1 e3 06          	shl    $0x6,%r11d
     8c6:	44 09 d1             	or     %r10d,%ecx
     8c9:	41 c1 e1 06          	shl    $0x6,%r9d
     8cd:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     8d2:	45 89 d8             	mov    %r11d,%r8d
     8d5:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     8da:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     8df:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
     8e4:	41 09 f8             	or     %edi,%r8d
     8e7:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     8ec:	41 c1 e2 06          	shl    $0x6,%r10d
     8f0:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     8f5:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     8fa:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     8ff:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     904:	c4 81 79 6e 14 8e    	vmovd  (%r14,%r9,4),%xmm2
     90a:	41 c1 e0 06          	shl    $0x6,%r8d
     90e:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     913:	c4 c1 79 6e 0c be    	vmovd  (%r14,%rdi,4),%xmm1
     919:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     91e:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     923:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     928:	c4 83 69 22 14 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm2,%xmm2
     92f:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     934:	c4 83 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm1,%xmm1
     93b:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
     93f:	c4 c1 79 6e 14 96    	vmovd  (%r14,%rdx,4),%xmm2
     945:	c4 c3 69 22 14 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm2,%xmm2
     94c:	41 8b 85 a5 00 00 00 	mov    0xa5(%r13),%eax
     953:	c4 c1 79 6e 04 b6    	vmovd  (%r14,%rsi,4),%xmm0
     959:	45 8b 9d 90 00 00 00 	mov    0x90(%r13),%r11d
     960:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     965:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     96a:	45 8b 85 99 00 00 00 	mov    0x99(%r13),%r8d
     971:	45 8b 8d 96 00 00 00 	mov    0x96(%r13),%r9d
     978:	c4 c3 79 22 04 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm0,%xmm0
     97f:	45 8b 95 93 00 00 00 	mov    0x93(%r13),%r10d
     986:	89 44 24 70          	mov    %eax,0x70(%rsp)
     98a:	41 8b 85 a2 00 00 00 	mov    0xa2(%r13),%eax
     991:	89 74 24 74          	mov    %esi,0x74(%rsp)
     995:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     99a:	c1 e6 06             	shl    $0x6,%esi
     99d:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     9a2:	44 09 de             	or     %r11d,%esi
     9a5:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
     9a9:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     9ae:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     9b3:	41 8b 85 9f 00 00 00 	mov    0x9f(%r13),%eax
     9ba:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     9bf:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     9c3:	41 8b bd 9c 00 00 00 	mov    0x9c(%r13),%edi
     9ca:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
     9d0:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     9d4:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     9d9:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     9de:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
     9e3:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     9e8:	89 44 24 58          	mov    %eax,0x58(%rsp)
     9ec:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     9f1:	c1 e0 06             	shl    $0x6,%eax
     9f4:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     9f8:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     9fd:	44 09 c0             	or     %r8d,%eax
     a00:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     a05:	89 54 24 60          	mov    %edx,0x60(%rsp)
     a09:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     a0e:	c1 e2 06             	shl    $0x6,%edx
     a11:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     a16:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     a1b:	44 09 ca             	or     %r9d,%edx
     a1e:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     a23:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     a28:	c1 e1 06             	shl    $0x6,%ecx
     a2b:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     a30:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     a35:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     a3a:	41 c1 e3 06          	shl    $0x6,%r11d
     a3e:	44 09 d1             	or     %r10d,%ecx
     a41:	41 c1 e1 06          	shl    $0x6,%r9d
     a45:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     a4a:	45 89 d8             	mov    %r11d,%r8d
     a4d:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     a52:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     a57:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
     a5c:	41 09 f8             	or     %edi,%r8d
     a5f:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     a64:	41 c1 e2 06          	shl    $0x6,%r10d
     a68:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     a6d:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     a72:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     a77:	41 c1 e0 06          	shl    $0x6,%r8d
     a7b:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     a80:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     a85:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     a8a:	c4 01 79 6e 14 8e    	vmovd  (%r14,%r9,4),%xmm10
     a90:	c4 c1 79 6e 14 be    	vmovd  (%r14,%rdi,4),%xmm2
     a96:	c4 c1 79 6e 0c b6    	vmovd  (%r14,%rsi,4),%xmm1
     a9c:	45 8b 9d a8 00 00 00 	mov    0xa8(%r13),%r11d
     aa3:	c4 03 29 22 14 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm10,%xmm10
     aaa:	c4 83 69 22 14 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm2,%xmm2
     ab1:	c4 c3 71 22 0c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm1,%xmm1
     ab8:	45 8b 85 b1 00 00 00 	mov    0xb1(%r13),%r8d
     abf:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
     ac4:	c4 41 79 6e 14 96    	vmovd  (%r14,%rdx,4),%xmm10
     aca:	45 8b 8d ae 00 00 00 	mov    0xae(%r13),%r9d
     ad1:	45 8b 95 ab 00 00 00 	mov    0xab(%r13),%r10d
     ad8:	c4 43 29 22 14 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm10,%xmm10
     adf:	41 8b 85 bd 00 00 00 	mov    0xbd(%r13),%eax
     ae6:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     aeb:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     af0:	89 44 24 70          	mov    %eax,0x70(%rsp)
     af4:	41 8b 85 ba 00 00 00 	mov    0xba(%r13),%eax
     afb:	89 74 24 74          	mov    %esi,0x74(%rsp)
     aff:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     b04:	c1 e6 06             	shl    $0x6,%esi
     b07:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
     b0c:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     b11:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     b16:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     b1a:	41 8b 85 b7 00 00 00 	mov    0xb7(%r13),%eax
     b21:	41 8b bd b4 00 00 00 	mov    0xb4(%r13),%edi
     b28:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     b2c:	44 09 de             	or     %r11d,%esi
     b2f:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
     b34:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     b39:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     b3e:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     b42:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     b47:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     b4c:	89 44 24 58          	mov    %eax,0x58(%rsp)
     b50:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
     b55:	c1 e0 06             	shl    $0x6,%eax
     b58:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
     b5d:	44 09 c0             	or     %r8d,%eax
     b60:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     b65:	89 54 24 60          	mov    %edx,0x60(%rsp)
     b69:	c1 e1 06             	shl    $0x6,%ecx
     b6c:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
     b71:	c1 e2 06             	shl    $0x6,%edx
     b74:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
     b79:	44 8b 5c 24 58       	mov    0x58(%rsp),%r11d
     b7e:	44 09 ca             	or     %r9d,%edx
     b81:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     b86:	44 09 d1             	or     %r10d,%ecx
     b89:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
     b8e:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
     b93:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     b99:	41 c1 e3 06          	shl    $0x6,%r11d
     b9d:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
     ba2:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
     ba7:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
     bac:	45 89 d8             	mov    %r11d,%r8d
     baf:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
     bb4:	41 09 f8             	or     %edi,%r8d
     bb7:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
     bbc:	44 8b 44 24 64       	mov    0x64(%rsp),%r8d
     bc1:	41 c1 e0 06          	shl    $0x6,%r8d
     bc5:	44 0b 44 24 60       	or     0x60(%rsp),%r8d
     bca:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
     bcf:	44 8b 4c 24 6c       	mov    0x6c(%rsp),%r9d
     bd4:	44 8b 54 24 74       	mov    0x74(%rsp),%r10d
     bd9:	c4 41 79 6e 14 be    	vmovd  (%r14,%rdi,4),%xmm10
     bdf:	41 c1 e1 06          	shl    $0x6,%r9d
     be3:	c4 c1 79 6e 14 b6    	vmovd  (%r14,%rsi,4),%xmm2
     be9:	44 0b 4c 24 68       	or     0x68(%rsp),%r9d
     bee:	41 c1 e2 06          	shl    $0x6,%r10d
     bf2:	c4 03 29 22 14 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm10,%xmm10
     bf9:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
     bfe:	44 0b 54 24 70       	or     0x70(%rsp),%r10d
     c03:	49 81 c5 c0 00 00 00 	add    $0xc0,%r13
     c0a:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
     c0f:	c4 c3 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm2,%xmm2
     c16:	c4 01 79 6e 1c 8e    	vmovd  (%r14,%r9,4),%xmm11
     c1c:	c4 03 21 22 1c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm11,%xmm11
     c23:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
     c28:	c4 41 79 6e 1c 96    	vmovd  (%r14,%rdx,4),%xmm11
     c2e:	c4 43 21 22 1c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm11,%xmm11
     c35:	c4 c1 7d e7 b5 60 ff 	vmovntdq %ymm6,-0xa0(%r13)
     c3c:	ff ff 
     c3e:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
     c43:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
     c48:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
     c4e:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
     c54:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
     c59:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
     c5f:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
     c65:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
     c6a:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
     c6f:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
     c74:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
     c79:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
     c7f:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
     c85:	c4 41 7d e7 8d 40 ff 	vmovntdq %ymm9,-0xc0(%r13)
     c8c:	ff ff 
     c8e:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
     c92:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
     c96:	c4 c1 7d e7 6d 80    	vmovntdq %ymm5,-0x80(%r13)
     c9c:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
     ca0:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
     ca4:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
     caa:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
     cb0:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
     cb6:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
     cbc:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
     cc1:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
     cc7:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
     ccb:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
     cd1:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
     cd7:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
     cdd:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
     ce3:	c4 c1 7d e7 6d a0    	vmovntdq %ymm5,-0x60(%r13)
     ce9:	c4 c1 7d e7 45 c0    	vmovntdq %ymm0,-0x40(%r13)
     cef:	c4 c1 7d e7 4d e0    	vmovntdq %ymm1,-0x20(%r13)
     cf5:	48 8b 44 24 78       	mov    0x78(%rsp),%rax
     cfa:	4c 8d 58 40          	lea    0x40(%rax),%r11
     cfe:	48 05 88 00 00 00    	add    $0x88,%rax
     d04:	48 39 84 24 80 00 00 	cmp    %rax,0x80(%rsp)
     d0b:	00 
     d0c:	0f 83 0e f4 ff ff    	jae    120 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x120>
     d12:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
     d17:	0f ae f8             	sfence
     d1a:	48 8b 54 24 78       	mov    0x78(%rsp),%rdx
     d1f:	48 83 c2 68          	add    $0x68,%rdx
     d23:	48 39 94 24 80 00 00 	cmp    %rdx,0x80(%rsp)
     d2a:	00 
     d2b:	0f 82 cf 06 00 00    	jb     1400 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1400>
     d31:	4c 89 5c 24 78       	mov    %r11,0x78(%rsp)
     d36:	4b 8d 14 5b          	lea    (%r11,%r11,2),%rdx
     d3a:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # d42 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd42>
     d41:	00 
     d42:	41 bc fc fc fc 00    	mov    $0xfcfcfc,%r12d
     d48:	48 89 44 24 88       	mov    %rax,-0x78(%rsp)
     d4d:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # d55 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd55>
     d54:	00 
     d55:	4c 8d 2c 10          	lea    (%rax,%rdx,1),%r13
     d59:	bb 03 03 03 00       	mov    $0x30303,%ebx
     d5e:	66 90                	xchg   %ax,%ax
     d60:	41 8b 45 15          	mov    0x15(%r13),%eax
     d64:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     d69:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     d6e:	89 44 24 70          	mov    %eax,0x70(%rsp)
     d72:	41 8b 45 12          	mov    0x12(%r13),%eax
     d76:	89 74 24 74          	mov    %esi,0x74(%rsp)
     d7a:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     d7f:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     d84:	41 8b 45 0f          	mov    0xf(%r13),%eax
     d88:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
     d8c:	89 7c 24 6c          	mov    %edi,0x6c(%rsp)
     d90:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     d95:	c4 62 7a f5 cb       	pext   %ebx,%eax,%r9d
     d9a:	41 8b 45 0c          	mov    0xc(%r13),%eax
     d9e:	44 89 4c 24 60       	mov    %r9d,0x60(%rsp)
     da3:	89 4c 24 64          	mov    %ecx,0x64(%rsp)
     da7:	c4 42 7a f5 cc       	pext   %r12d,%eax,%r9d
     dac:	c4 62 7a f5 c3       	pext   %ebx,%eax,%r8d
     db1:	41 8b 45 09          	mov    0x9(%r13),%eax
     db5:	44 89 44 24 50       	mov    %r8d,0x50(%rsp)
     dba:	44 89 4c 24 58       	mov    %r9d,0x58(%rsp)
     dbf:	c4 42 7a f5 d4       	pext   %r12d,%eax,%r10d
     dc4:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     dc9:	89 44 24 48          	mov    %eax,0x48(%rsp)
     dcd:	41 8b 45 06          	mov    0x6(%r13),%eax
     dd1:	44 89 54 24 4c       	mov    %r10d,0x4c(%rsp)
     dd6:	c4 42 7a f5 c4       	pext   %r12d,%eax,%r8d
     ddb:	c4 e2 7a f5 f3       	pext   %ebx,%eax,%esi
     de0:	41 8b 45 03          	mov    0x3(%r13),%eax
     de4:	89 74 24 40          	mov    %esi,0x40(%rsp)
     de8:	44 89 44 24 44       	mov    %r8d,0x44(%rsp)
     ded:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     df2:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     df7:	89 44 24 38          	mov    %eax,0x38(%rsp)
     dfb:	41 8b 45 00          	mov    0x0(%r13),%eax
     dff:	89 74 24 3c          	mov    %esi,0x3c(%rsp)
     e03:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     e08:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     e0d:	41 8b 45 2d          	mov    0x2d(%r13),%eax
     e11:	89 4c 24 30          	mov    %ecx,0x30(%rsp)
     e15:	89 7c 24 34          	mov    %edi,0x34(%rsp)
     e19:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     e1e:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     e23:	41 8b 45 2a          	mov    0x2a(%r13),%eax
     e27:	89 54 24 28          	mov    %edx,0x28(%rsp)
     e2b:	89 4c 24 2c          	mov    %ecx,0x2c(%rsp)
     e2f:	c4 42 7a f5 dc       	pext   %r12d,%eax,%r11d
     e34:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     e39:	41 8b 45 27          	mov    0x27(%r13),%eax
     e3d:	44 89 5c 24 24       	mov    %r11d,0x24(%rsp)
     e42:	89 54 24 20          	mov    %edx,0x20(%rsp)
     e46:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     e4b:	c4 62 7a f5 d3       	pext   %ebx,%eax,%r10d
     e50:	89 4c 24 1c          	mov    %ecx,0x1c(%rsp)
     e54:	44 89 54 24 18       	mov    %r10d,0x18(%rsp)
     e59:	41 8b 45 24          	mov    0x24(%r13),%eax
     e5d:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
     e62:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     e67:	89 44 24 10          	mov    %eax,0x10(%rsp)
     e6b:	41 8b 45 21          	mov    0x21(%r13),%eax
     e6f:	89 54 24 14          	mov    %edx,0x14(%rsp)
     e73:	c4 42 7a f5 d4       	pext   %r12d,%eax,%r10d
     e78:	c4 62 7a f5 c3       	pext   %ebx,%eax,%r8d
     e7d:	41 8b 45 1e          	mov    0x1e(%r13),%eax
     e81:	44 89 44 24 08       	mov    %r8d,0x8(%rsp)
     e86:	44 89 54 24 0c       	mov    %r10d,0xc(%rsp)
     e8b:	c4 42 7a f5 c4       	pext   %r12d,%eax,%r8d
     e90:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     e95:	89 04 24             	mov    %eax,(%rsp)
     e98:	41 8b 45 1b          	mov    0x1b(%r13),%eax
     e9c:	44 89 44 24 04       	mov    %r8d,0x4(%rsp)
     ea1:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     ea6:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     eab:	89 44 24 f8          	mov    %eax,-0x8(%rsp)
     eaf:	41 8b 45 18          	mov    0x18(%r13),%eax
     eb3:	89 74 24 fc          	mov    %esi,-0x4(%rsp)
     eb7:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     ebc:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     ec1:	41 8b 45 45          	mov    0x45(%r13),%eax
     ec5:	89 4c 24 f4          	mov    %ecx,-0xc(%rsp)
     ec9:	89 54 24 f0          	mov    %edx,-0x10(%rsp)
     ecd:	c4 42 7a f5 dc       	pext   %r12d,%eax,%r11d
     ed2:	c4 62 7a f5 cb       	pext   %ebx,%eax,%r9d
     ed7:	41 8b 45 42          	mov    0x42(%r13),%eax
     edb:	44 89 4c 24 e8       	mov    %r9d,-0x18(%rsp)
     ee0:	44 89 5c 24 ec       	mov    %r11d,-0x14(%rsp)
     ee5:	c4 42 7a f5 cc       	pext   %r12d,%eax,%r9d
     eea:	c4 e2 7a f5 fb       	pext   %ebx,%eax,%edi
     eef:	41 8b 45 3f          	mov    0x3f(%r13),%eax
     ef3:	89 7c 24 e0          	mov    %edi,-0x20(%rsp)
     ef7:	44 89 4c 24 e4       	mov    %r9d,-0x1c(%rsp)
     efc:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
     f01:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     f06:	41 8b 45 3c          	mov    0x3c(%r13),%eax
     f0a:	89 4c 24 d8          	mov    %ecx,-0x28(%rsp)
     f0e:	89 74 24 dc          	mov    %esi,-0x24(%rsp)
     f12:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
     f17:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     f1c:	89 44 24 d0          	mov    %eax,-0x30(%rsp)
     f20:	41 8b 45 39          	mov    0x39(%r13),%eax
     f24:	89 7c 24 d4          	mov    %edi,-0x2c(%rsp)
     f28:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
     f2d:	c4 e2 7a f5 d3       	pext   %ebx,%eax,%edx
     f32:	41 8b 45 36          	mov    0x36(%r13),%eax
     f36:	89 4c 24 cc          	mov    %ecx,-0x34(%rsp)
     f3a:	89 54 24 c8          	mov    %edx,-0x38(%rsp)
     f3e:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
     f43:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     f48:	89 54 24 c4          	mov    %edx,-0x3c(%rsp)
     f4c:	89 44 24 c0          	mov    %eax,-0x40(%rsp)
     f50:	41 8b 45 33          	mov    0x33(%r13),%eax
     f54:	c4 42 7a f5 d4       	pext   %r12d,%eax,%r10d
     f59:	c4 62 7a f5 c3       	pext   %ebx,%eax,%r8d
     f5e:	41 8b 45 30          	mov    0x30(%r13),%eax
     f62:	44 89 54 24 bc       	mov    %r10d,-0x44(%rsp)
     f67:	44 89 44 24 b8       	mov    %r8d,-0x48(%rsp)
     f6c:	45 8b 55 4b          	mov    0x4b(%r13),%r10d
     f70:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
     f75:	c4 e2 7a f5 fb       	pext   %ebx,%eax,%edi
     f7a:	41 8b 45 5d          	mov    0x5d(%r13),%eax
     f7e:	89 7c 24 b0          	mov    %edi,-0x50(%rsp)
     f82:	41 8b 7d 54          	mov    0x54(%r13),%edi
     f86:	89 54 24 b4          	mov    %edx,-0x4c(%rsp)
     f8a:	c4 42 7a f5 dc       	pext   %r12d,%eax,%r11d
     f8f:	c4 e2 7a f5 f3       	pext   %ebx,%eax,%esi
     f94:	41 8b 45 5a          	mov    0x5a(%r13),%eax
     f98:	44 89 5c 24 ac       	mov    %r11d,-0x54(%rsp)
     f9d:	45 8b 5d 48          	mov    0x48(%r13),%r11d
     fa1:	89 74 24 a8          	mov    %esi,-0x58(%rsp)
     fa5:	c4 42 7a f5 cc       	pext   %r12d,%eax,%r9d
     faa:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
     faf:	41 8b 45 57          	mov    0x57(%r13),%eax
     fb3:	89 4c 24 a0          	mov    %ecx,-0x60(%rsp)
     fb7:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
     fbc:	c1 e1 06             	shl    $0x6,%ecx
     fbf:	c4 62 2a f5 d3       	pext   %ebx,%r10d,%r10d
     fc4:	44 89 4c 24 a4       	mov    %r9d,-0x5c(%rsp)
     fc9:	c4 42 7a f5 c4       	pext   %r12d,%eax,%r8d
     fce:	c4 e2 7a f5 c3       	pext   %ebx,%eax,%eax
     fd3:	89 44 24 98          	mov    %eax,-0x68(%rsp)
     fd7:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
     fdc:	89 44 24 94          	mov    %eax,-0x6c(%rsp)
     fe0:	44 09 d1             	or     %r10d,%ecx
     fe3:	45 8b 4d 4e          	mov    0x4e(%r13),%r9d
     fe7:	c4 e2 42 f5 fb       	pext   %ebx,%edi,%edi
     fec:	44 89 44 24 9c       	mov    %r8d,-0x64(%rsp)
     ff1:	45 8b 45 51          	mov    0x51(%r13),%r8d
     ff5:	c4 c2 22 f5 f4       	pext   %r12d,%r11d,%esi
     ffa:	c1 e6 06             	shl    $0x6,%esi
     ffd:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
    1002:	c1 e2 06             	shl    $0x6,%edx
    1005:	c4 62 32 f5 cb       	pext   %ebx,%r9d,%r9d
    100a:	c4 62 22 f5 db       	pext   %ebx,%r11d,%r11d
    100f:	44 8b 54 24 94       	mov    -0x6c(%rsp),%r10d
    1014:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
    1019:	c1 e0 06             	shl    $0x6,%eax
    101c:	c4 62 3a f5 c3       	pext   %ebx,%r8d,%r8d
    1021:	44 09 c0             	or     %r8d,%eax
    1024:	44 09 ca             	or     %r9d,%edx
    1027:	44 8b 4c 24 a4       	mov    -0x5c(%rsp),%r9d
    102c:	44 09 de             	or     %r11d,%esi
    102f:	41 c1 e2 06          	shl    $0x6,%r10d
    1033:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    1038:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    103d:	45 89 d0             	mov    %r10d,%r8d
    1040:	41 c1 e1 06          	shl    $0x6,%r9d
    1044:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1049:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    104e:	41 09 f8             	or     %edi,%r8d
    1051:	44 0b 4c 24 a0       	or     -0x60(%rsp),%r9d
    1056:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    105b:	44 8b 44 24 9c       	mov    -0x64(%rsp),%r8d
    1060:	41 c1 e0 06          	shl    $0x6,%r8d
    1064:	44 0b 44 24 98       	or     -0x68(%rsp),%r8d
    1069:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    106e:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    1073:	44 8b 5c 24 ac       	mov    -0x54(%rsp),%r11d
    1078:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
    107e:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
    1084:	c4 c1 79 6e 2c b6    	vmovd  (%r14,%rsi,4),%xmm5
    108a:	41 c1 e3 06          	shl    $0x6,%r11d
    108e:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
    1095:	8b 74 24 cc          	mov    -0x34(%rsp),%esi
    1099:	45 89 da             	mov    %r11d,%r10d
    109c:	c4 c3 51 22 2c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm5,%xmm5
    10a3:	8b 7c 24 d4          	mov    -0x2c(%rsp),%edi
    10a7:	44 0b 54 24 a8       	or     -0x58(%rsp),%r10d
    10ac:	8b 4c 24 c4          	mov    -0x3c(%rsp),%ecx
    10b0:	c1 e6 06             	shl    $0x6,%esi
    10b3:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    10b8:	44 8b 44 24 dc       	mov    -0x24(%rsp),%r8d
    10bd:	c1 e7 06             	shl    $0x6,%edi
    10c0:	44 8b 4c 24 e4       	mov    -0x1c(%rsp),%r9d
    10c5:	c1 e1 06             	shl    $0x6,%ecx
    10c8:	0b 74 24 c8          	or     -0x38(%rsp),%esi
    10cc:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
    10d3:	44 8b 54 24 bc       	mov    -0x44(%rsp),%r10d
    10d8:	41 c1 e0 06          	shl    $0x6,%r8d
    10dc:	41 c1 e1 06          	shl    $0x6,%r9d
    10e0:	0b 4c 24 c0          	or     -0x40(%rsp),%ecx
    10e4:	0b 7c 24 d0          	or     -0x30(%rsp),%edi
    10e8:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    10ec:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
    10f2:	41 c1 e2 06          	shl    $0x6,%r10d
    10f6:	44 0b 44 24 d8       	or     -0x28(%rsp),%r8d
    10fb:	44 89 d2             	mov    %r10d,%edx
    10fe:	44 0b 4c 24 e0       	or     -0x20(%rsp),%r9d
    1103:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    1108:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
    110f:	8b 44 24 b4          	mov    -0x4c(%rsp),%eax
    1113:	0b 54 24 b8          	or     -0x48(%rsp),%edx
    1117:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    111c:	c1 e0 06             	shl    $0x6,%eax
    111f:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1124:	41 0f b6 3c 3f       	movzbl (%r15,%rdi,1),%edi
    1129:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    112d:	0b 44 24 b0          	or     -0x50(%rsp),%eax
    1131:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    1136:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    113c:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    1141:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    1146:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    114b:	44 8b 5c 24 ec       	mov    -0x14(%rsp),%r11d
    1150:	c4 c1 79 6e 0c be    	vmovd  (%r14,%rdi,4),%xmm1
    1156:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    115b:	c4 81 79 6e 14 8e    	vmovd  (%r14,%r9,4),%xmm2
    1161:	c4 c1 79 6e 04 86    	vmovd  (%r14,%rax,4),%xmm0
    1167:	41 c1 e3 06          	shl    $0x6,%r11d
    116b:	8b 44 24 f4          	mov    -0xc(%rsp),%eax
    116f:	44 8b 4c 24 14       	mov    0x14(%rsp),%r9d
    1174:	45 89 da             	mov    %r11d,%r10d
    1177:	c4 83 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm1,%xmm1
    117e:	44 8b 44 24 04       	mov    0x4(%rsp),%r8d
    1183:	44 0b 54 24 e8       	or     -0x18(%rsp),%r10d
    1188:	c1 e0 06             	shl    $0x6,%eax
    118b:	44 8b 5c 24 24       	mov    0x24(%rsp),%r11d
    1190:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    1195:	41 c1 e1 06          	shl    $0x6,%r9d
    1199:	41 c1 e0 06          	shl    $0x6,%r8d
    119d:	c4 c3 79 22 04 96 01 	vpinsrd $0x1,(%r14,%rdx,4),%xmm0,%xmm0
    11a4:	44 89 cf             	mov    %r9d,%edi
    11a7:	8b 54 24 fc          	mov    -0x4(%rsp),%edx
    11ab:	41 c1 e3 06          	shl    $0x6,%r11d
    11af:	0b 44 24 f0          	or     -0x10(%rsp),%eax
    11b3:	c4 83 69 22 14 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm2,%xmm2
    11ba:	0b 7c 24 10          	or     0x10(%rsp),%edi
    11be:	44 8b 54 24 0c       	mov    0xc(%rsp),%r10d
    11c3:	c1 e2 06             	shl    $0x6,%edx
    11c6:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    11cb:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    11cf:	c4 c1 79 6e 14 8e    	vmovd  (%r14,%rcx,4),%xmm2
    11d5:	44 89 c1             	mov    %r8d,%ecx
    11d8:	45 0f b6 04 3f       	movzbl (%r15,%rdi,1),%r8d
    11dd:	8b 7c 24 1c          	mov    0x1c(%rsp),%edi
    11e1:	41 c1 e2 06          	shl    $0x6,%r10d
    11e5:	0b 54 24 f8          	or     -0x8(%rsp),%edx
    11e9:	c4 c3 69 22 14 b6 01 	vpinsrd $0x1,(%r14,%rsi,4),%xmm2,%xmm2
    11f0:	44 89 d6             	mov    %r10d,%esi
    11f3:	0b 0c 24             	or     (%rsp),%ecx
    11f6:	c1 e7 06             	shl    $0x6,%edi
    11f9:	0b 74 24 08          	or     0x8(%rsp),%esi
    11fd:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1202:	0b 7c 24 18          	or     0x18(%rsp),%edi
    1206:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    120b:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    120f:	45 0f b6 0c 3f       	movzbl (%r15,%rdi,1),%r9d
    1214:	44 89 df             	mov    %r11d,%edi
    1217:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    121c:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    1222:	0b 7c 24 20          	or     0x20(%rsp),%edi
    1226:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    122b:	45 0f b6 14 3f       	movzbl (%r15,%rdi,1),%r10d
    1230:	8b 7c 24 2c          	mov    0x2c(%rsp),%edi
    1234:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    1239:	c4 81 79 6e 14 86    	vmovd  (%r14,%r8,4),%xmm2
    123f:	c4 c1 79 6e 0c 86    	vmovd  (%r14,%rax,4),%xmm1
    1245:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    1249:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    124f:	c1 e7 06             	shl    $0x6,%edi
    1252:	c4 81 79 6e 34 96    	vmovd  (%r14,%r10,4),%xmm6
    1258:	44 8b 44 24 44       	mov    0x44(%rsp),%r8d
    125d:	0b 7c 24 28          	or     0x28(%rsp),%edi
    1261:	c4 83 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%r9,4),%xmm2,%xmm2
    1268:	41 0f b6 3c 3f       	movzbl (%r15,%rdi,1),%edi
    126d:	c4 c3 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%rdx,4),%xmm1,%xmm1
    1274:	41 c1 e0 06          	shl    $0x6,%r8d
    1278:	44 8b 54 24 4c       	mov    0x4c(%rsp),%r10d
    127d:	44 8b 4c 24 58       	mov    0x58(%rsp),%r9d
    1282:	c4 c3 49 22 34 be 01 	vpinsrd $0x1,(%r14,%rdi,4),%xmm6,%xmm6
    1289:	44 8b 5c 24 64       	mov    0x64(%rsp),%r11d
    128e:	41 c1 e2 06          	shl    $0x6,%r10d
    1292:	41 c1 e1 06          	shl    $0x6,%r9d
    1296:	8b 44 24 34          	mov    0x34(%rsp),%eax
    129a:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    129e:	c4 c1 79 6e 34 8e    	vmovd  (%r14,%rcx,4),%xmm6
    12a4:	41 c1 e3 06          	shl    $0x6,%r11d
    12a8:	c1 e0 06             	shl    $0x6,%eax
    12ab:	c4 c3 49 22 34 b6 01 	vpinsrd $0x1,(%r14,%rsi,4),%xmm6,%xmm6
    12b2:	8b 74 24 3c          	mov    0x3c(%rsp),%esi
    12b6:	0b 44 24 30          	or     0x30(%rsp),%eax
    12ba:	c1 e6 06             	shl    $0x6,%esi
    12bd:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    12c2:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    12c6:	89 f2                	mov    %esi,%edx
    12c8:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    12ce:	0b 54 24 38          	or     0x38(%rsp),%edx
    12d2:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    12d7:	41 0f b6 0c 17       	movzbl (%r15,%rdx,1),%ecx
    12dc:	44 89 c2             	mov    %r8d,%edx
    12df:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    12e4:	0b 54 24 40          	or     0x40(%rsp),%edx
    12e8:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    12ec:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    12f2:	41 0f b6 34 17       	movzbl (%r15,%rdx,1),%esi
    12f7:	44 89 d2             	mov    %r10d,%edx
    12fa:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    1300:	0b 54 24 48          	or     0x48(%rsp),%edx
    1304:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    130a:	41 0f b6 3c 17       	movzbl (%r15,%rdx,1),%edi
    130f:	44 89 ca             	mov    %r9d,%edx
    1312:	0b 54 24 50          	or     0x50(%rsp),%edx
    1316:	45 0f b6 04 17       	movzbl (%r15,%rdx,1),%r8d
    131b:	44 89 da             	mov    %r11d,%edx
    131e:	0b 54 24 60          	or     0x60(%rsp),%edx
    1322:	45 0f b6 0c 17       	movzbl (%r15,%rdx,1),%r9d
    1327:	8b 54 24 6c          	mov    0x6c(%rsp),%edx
    132b:	c1 e2 06             	shl    $0x6,%edx
    132e:	0b 54 24 68          	or     0x68(%rsp),%edx
    1332:	45 0f b6 14 17       	movzbl (%r15,%rdx,1),%r10d
    1337:	8b 54 24 74          	mov    0x74(%rsp),%edx
    133b:	c4 81 79 6e 34 86    	vmovd  (%r14,%r8,4),%xmm6
    1341:	c4 c1 79 6e 14 86    	vmovd  (%r14,%rax,4),%xmm2
    1347:	c1 e2 06             	shl    $0x6,%edx
    134a:	c4 81 79 6e 3c 96    	vmovd  (%r14,%r10,4),%xmm7
    1350:	0b 54 24 70          	or     0x70(%rsp),%edx
    1354:	c4 83 49 22 34 8e 01 	vpinsrd $0x1,(%r14,%r9,4),%xmm6,%xmm6
    135b:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1360:	c4 c3 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm2,%xmm2
    1367:	c4 c3 41 22 3c 96 01 	vpinsrd $0x1,(%r14,%rdx,4),%xmm7,%xmm7
    136e:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    1372:	c4 c1 79 6e 3c b6    	vmovd  (%r14,%rsi,4),%xmm7
    1378:	48 8b 74 24 78       	mov    0x78(%rsp),%rsi
    137d:	c4 c3 41 22 3c be 01 	vpinsrd $0x1,(%r14,%rdi,4),%xmm7,%xmm7
    1384:	48 8d 46 48          	lea    0x48(%rsi),%rax
    1388:	48 83 c6 20          	add    $0x20,%rsi
    138c:	c4 c1 7e 7f 4d 20    	vmovdqu %ymm1,0x20(%r13)
    1392:	48 89 74 24 78       	mov    %rsi,0x78(%rsp)
    1397:	49 83 c5 60          	add    $0x60,%r13
    139b:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    139f:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    13a3:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    13a9:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    13af:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    13b5:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    13b9:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    13be:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    13c4:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    13c9:	c4 c1 7e 7f 45 e0    	vmovdqu %ymm0,-0x20(%r13)
    13cf:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    13d3:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    13d9:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    13de:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    13e4:	c4 c1 7e 7f 55 a0    	vmovdqu %ymm2,-0x60(%r13)
    13ea:	48 39 84 24 80 00 00 	cmp    %rax,0x80(%rsp)
    13f1:	00 
    13f2:	0f 83 68 f9 ff ff    	jae    d60 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd60>
    13f8:	48 8b 44 24 88       	mov    -0x78(%rsp),%rax
    13fd:	49 89 f3             	mov    %rsi,%r11
    1400:	4d 8d 6b 08          	lea    0x8(%r11),%r13
    1404:	4c 39 ac 24 80 00 00 	cmp    %r13,0x80(%rsp)
    140b:	00 
    140c:	0f 82 08 02 00 00    	jb     161a <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x161a>
    1412:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
    1417:	4b 8d 14 5b          	lea    (%r11,%r11,2),%rdx
    141b:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 1423 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1423>
    1422:	00 
    1423:	4c 8d 14 10          	lea    (%rax,%rdx,1),%r10
    1427:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    142e:	00 00 
    1430:	49 8b 42 10          	mov    0x10(%r10),%rax
    1434:	bb fc fc fc 00       	mov    $0xfcfcfc,%ebx
    1439:	49 8b 72 08          	mov    0x8(%r10),%rsi
    143d:	49 8b 12             	mov    (%r10),%rdx
    1440:	48 89 c1             	mov    %rax,%rcx
    1443:	41 89 f4             	mov    %esi,%r12d
    1446:	48 c1 e9 28          	shr    $0x28,%rcx
    144a:	41 c1 ec 08          	shr    $0x8,%r12d
    144e:	c4 e2 72 f5 fb       	pext   %ebx,%ecx,%edi
    1453:	89 7c 24 78          	mov    %edi,0x78(%rsp)
    1457:	bf 03 03 03 00       	mov    $0x30303,%edi
    145c:	c4 e2 72 f5 cf       	pext   %edi,%ecx,%ecx
    1461:	89 4c 24 74          	mov    %ecx,0x74(%rsp)
    1465:	48 89 c1             	mov    %rax,%rcx
    1468:	c1 e0 08             	shl    $0x8,%eax
    146b:	48 c1 e9 10          	shr    $0x10,%rcx
    146f:	41 89 fb             	mov    %edi,%r11d
    1472:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    1478:	c4 62 72 f5 cb       	pext   %ebx,%ecx,%r9d
    147d:	c4 62 72 f5 c7       	pext   %edi,%ecx,%r8d
    1482:	48 89 f1             	mov    %rsi,%rcx
    1485:	44 89 4c 24 70       	mov    %r9d,0x70(%rsp)
    148a:	48 c1 e9 38          	shr    $0x38,%rcx
    148e:	44 89 44 24 6c       	mov    %r8d,0x6c(%rsp)
    1493:	c4 62 1a f5 c3       	pext   %ebx,%r12d,%r8d
    1498:	c4 42 1a f5 e3       	pext   %r11d,%r12d,%r12d
    149d:	09 c8                	or     %ecx,%eax
    149f:	41 c1 e0 06          	shl    $0x6,%r8d
    14a3:	25 ff ff ff 00       	and    $0xffffff,%eax
    14a8:	45 09 e0             	or     %r12d,%r8d
    14ab:	c4 e2 7a f5 cb       	pext   %ebx,%eax,%ecx
    14b0:	c4 e2 7a f5 c7       	pext   %edi,%eax,%eax
    14b5:	89 44 24 64          	mov    %eax,0x64(%rsp)
    14b9:	48 89 f0             	mov    %rsi,%rax
    14bc:	48 c1 e8 20          	shr    $0x20,%rax
    14c0:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
    14c4:	c1 e6 10             	shl    $0x10,%esi
    14c7:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    14cc:	48 89 c1             	mov    %rax,%rcx
    14cf:	48 89 d0             	mov    %rdx,%rax
    14d2:	48 c1 e8 30          	shr    $0x30,%rax
    14d6:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    14dc:	49 89 c1             	mov    %rax,%r9
    14df:	89 f0                	mov    %esi,%eax
    14e1:	48 89 d6             	mov    %rdx,%rsi
    14e4:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    14ea:	44 09 c8             	or     %r9d,%eax
    14ed:	48 c1 ee 18          	shr    $0x18,%rsi
    14f1:	c4 e2 72 f5 fb       	pext   %ebx,%ecx,%edi
    14f6:	c4 c2 72 f5 cb       	pext   %r11d,%ecx,%ecx
    14fb:	25 ff ff ff 00       	and    $0xffffff,%eax
    1500:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    1506:	c1 e7 06             	shl    $0x6,%edi
    1509:	c4 62 7a f5 cb       	pext   %ebx,%eax,%r9d
    150e:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    1513:	89 44 24 60          	mov    %eax,0x60(%rsp)
    1517:	41 c1 e1 06          	shl    $0x6,%r9d
    151b:	c4 e2 4a f5 c3       	pext   %ebx,%esi,%eax
    1520:	c4 c2 4a f5 f3       	pext   %r11d,%esi,%esi
    1525:	c4 e2 6a f5 db       	pext   %ebx,%edx,%ebx
    152a:	c4 c2 6a f5 d3       	pext   %r11d,%edx,%edx
    152f:	c1 e3 06             	shl    $0x6,%ebx
    1532:	41 89 c3             	mov    %eax,%r11d
    1535:	09 cf                	or     %ecx,%edi
    1537:	44 0b 4c 24 60       	or     0x60(%rsp),%r9d
    153c:	09 d3                	or     %edx,%ebx
    153e:	41 c1 e3 06          	shl    $0x6,%r11d
    1542:	41 0f b6 0c 3f       	movzbl (%r15,%rdi,1),%ecx
    1547:	43 0f b6 04 0f       	movzbl (%r15,%r9,1),%eax
    154c:	44 8b 4c 24 70       	mov    0x70(%rsp),%r9d
    1551:	41 09 f3             	or     %esi,%r11d
    1554:	41 0f b6 14 1f       	movzbl (%r15,%rbx,1),%edx
    1559:	8b 5c 24 68          	mov    0x68(%rsp),%ebx
    155d:	43 0f b6 34 1f       	movzbl (%r15,%r11,1),%esi
    1562:	41 c1 e1 06          	shl    $0x6,%r9d
    1566:	44 8b 5c 24 78       	mov    0x78(%rsp),%r11d
    156b:	44 0b 4c 24 6c       	or     0x6c(%rsp),%r9d
    1570:	c1 e3 06             	shl    $0x6,%ebx
    1573:	c4 c1 79 6e 0c 8e    	vmovd  (%r14,%rcx,4),%xmm1
    1579:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    157e:	89 df                	mov    %ebx,%edi
    1580:	41 c1 e3 06          	shl    $0x6,%r11d
    1584:	c4 c1 79 6e 04 96    	vmovd  (%r14,%rdx,4),%xmm0
    158a:	0b 7c 24 64          	or     0x64(%rsp),%edi
    158e:	44 0b 5c 24 74       	or     0x74(%rsp),%r11d
    1593:	49 83 c2 18          	add    $0x18,%r10
    1597:	47 0f b6 1c 1f       	movzbl (%r15,%r11,1),%r11d
    159c:	41 0f b6 3c 3f       	movzbl (%r15,%rdi,1),%edi
    15a1:	c4 81 79 6e 14 8e    	vmovd  (%r14,%r9,4),%xmm2
    15a7:	c4 c3 71 22 0c be 01 	vpinsrd $0x1,(%r14,%rdi,4),%xmm1,%xmm1
    15ae:	c4 83 69 22 14 9e 01 	vpinsrd $0x1,(%r14,%r11,4),%xmm2,%xmm2
    15b5:	4d 89 eb             	mov    %r13,%r11
    15b8:	49 83 c5 08          	add    $0x8,%r13
    15bc:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    15c0:	c4 c1 79 6e 14 86    	vmovd  (%r14,%rax,4),%xmm2
    15c6:	c4 83 69 22 14 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm2,%xmm2
    15cd:	c4 c3 79 22 04 b6 01 	vpinsrd $0x1,(%r14,%rsi,4),%xmm0,%xmm0
    15d4:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    15d8:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    15de:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    15e3:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    15e7:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    15ed:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    15f2:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    15f7:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    15fb:	c4 c1 79 d6 42 f8    	vmovq  %xmm0,-0x8(%r10)
    1601:	c4 c1 7a 7f 4a e8    	vmovdqu %xmm1,-0x18(%r10)
    1607:	4c 39 ac 24 80 00 00 	cmp    %r13,0x80(%rsp)
    160e:	00 
    160f:	0f 83 1b fe ff ff    	jae    1430 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1430>
    1615:	48 8b 44 24 58       	mov    0x58(%rsp),%rax
    161a:	48 8b 9c 24 80 00 00 	mov    0x80(%rsp),%rbx
    1621:	00 
    1622:	49 39 db             	cmp    %rbx,%r11
    1625:	0f 83 75 02 00 00    	jae    18a0 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a0>
    162b:	4b 8d 0c 5b          	lea    (%r11,%r11,2),%rcx
    162f:	bf 03 03 03 00       	mov    $0x30303,%edi
    1634:	4c 8d 04 08          	lea    (%rax,%rcx,1),%r8
    1638:	41 0f b6 50 01       	movzbl 0x1(%r8),%edx
    163d:	41 0f b6 70 02       	movzbl 0x2(%r8),%esi
    1642:	c1 e2 08             	shl    $0x8,%edx
    1645:	c1 e6 10             	shl    $0x10,%esi
    1648:	09 f2                	or     %esi,%edx
    164a:	41 0f b6 30          	movzbl (%r8),%esi
    164e:	09 f2                	or     %esi,%edx
    1650:	be fc fc fc 00       	mov    $0xfcfcfc,%esi
    1655:	c4 62 6a f5 ce       	pext   %esi,%edx,%r9d
    165a:	41 c1 e1 06          	shl    $0x6,%r9d
    165e:	c4 e2 6a f5 d7       	pext   %edi,%edx,%edx
    1663:	44 09 ca             	or     %r9d,%edx
    1666:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    166b:	4d 8d 0c 96          	lea    (%r14,%rdx,4),%r9
    166f:	41 8b 11             	mov    (%r9),%edx
    1672:	45 0f b7 09          	movzwl (%r9),%r9d
    1676:	c1 ea 10             	shr    $0x10,%edx
    1679:	66 45 89 08          	mov    %r9w,(%r8)
    167d:	41 88 50 02          	mov    %dl,0x2(%r8)
    1681:	49 8d 53 01          	lea    0x1(%r11),%rdx
    1685:	48 39 da             	cmp    %rbx,%rdx
    1688:	0f 83 12 02 00 00    	jae    18a0 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a0>
    168e:	4c 8d 44 08 03       	lea    0x3(%rax,%rcx,1),%r8
    1693:	41 0f b6 50 01       	movzbl 0x1(%r8),%edx
    1698:	45 0f b6 48 02       	movzbl 0x2(%r8),%r9d
    169d:	c1 e2 08             	shl    $0x8,%edx
    16a0:	41 c1 e1 10          	shl    $0x10,%r9d
    16a4:	44 09 ca             	or     %r9d,%edx
    16a7:	45 0f b6 08          	movzbl (%r8),%r9d
    16ab:	44 09 ca             	or     %r9d,%edx
    16ae:	c4 62 6a f5 ce       	pext   %esi,%edx,%r9d
    16b3:	41 c1 e1 06          	shl    $0x6,%r9d
    16b7:	c4 e2 6a f5 d7       	pext   %edi,%edx,%edx
    16bc:	44 09 ca             	or     %r9d,%edx
    16bf:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    16c4:	4d 8d 0c 96          	lea    (%r14,%rdx,4),%r9
    16c8:	41 8b 11             	mov    (%r9),%edx
    16cb:	45 0f b7 09          	movzwl (%r9),%r9d
    16cf:	c1 ea 10             	shr    $0x10,%edx
    16d2:	66 45 89 08          	mov    %r9w,(%r8)
    16d6:	41 88 50 02          	mov    %dl,0x2(%r8)
    16da:	49 8d 53 02          	lea    0x2(%r11),%rdx
    16de:	48 39 da             	cmp    %rbx,%rdx
    16e1:	0f 83 b9 01 00 00    	jae    18a0 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a0>
    16e7:	4c 8d 44 08 06       	lea    0x6(%rax,%rcx,1),%r8
    16ec:	41 0f b6 50 01       	movzbl 0x1(%r8),%edx
    16f1:	45 0f b6 48 02       	movzbl 0x2(%r8),%r9d
    16f6:	c1 e2 08             	shl    $0x8,%edx
    16f9:	41 c1 e1 10          	shl    $0x10,%r9d
    16fd:	44 09 ca             	or     %r9d,%edx
    1700:	45 0f b6 08          	movzbl (%r8),%r9d
    1704:	44 09 ca             	or     %r9d,%edx
    1707:	c4 62 6a f5 ce       	pext   %esi,%edx,%r9d
    170c:	41 c1 e1 06          	shl    $0x6,%r9d
    1710:	c4 e2 6a f5 d7       	pext   %edi,%edx,%edx
    1715:	44 09 ca             	or     %r9d,%edx
    1718:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    171d:	4d 8d 0c 96          	lea    (%r14,%rdx,4),%r9
    1721:	41 8b 11             	mov    (%r9),%edx
    1724:	45 0f b7 09          	movzwl (%r9),%r9d
    1728:	c1 ea 10             	shr    $0x10,%edx
    172b:	66 45 89 08          	mov    %r9w,(%r8)
    172f:	41 88 50 02          	mov    %dl,0x2(%r8)
    1733:	49 8d 53 03          	lea    0x3(%r11),%rdx
    1737:	48 39 da             	cmp    %rbx,%rdx
    173a:	0f 83 60 01 00 00    	jae    18a0 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a0>
    1740:	4c 8d 44 08 09       	lea    0x9(%rax,%rcx,1),%r8
    1745:	41 0f b6 50 02       	movzbl 0x2(%r8),%edx
    174a:	45 0f b6 48 01       	movzbl 0x1(%r8),%r9d
    174f:	c1 e2 10             	shl    $0x10,%edx
    1752:	41 c1 e1 08          	shl    $0x8,%r9d
    1756:	44 09 ca             	or     %r9d,%edx
    1759:	45 0f b6 08          	movzbl (%r8),%r9d
    175d:	44 09 ca             	or     %r9d,%edx
    1760:	c4 62 6a f5 ce       	pext   %esi,%edx,%r9d
    1765:	41 c1 e1 06          	shl    $0x6,%r9d
    1769:	c4 e2 6a f5 d7       	pext   %edi,%edx,%edx
    176e:	44 09 ca             	or     %r9d,%edx
    1771:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1776:	4d 8d 0c 96          	lea    (%r14,%rdx,4),%r9
    177a:	41 8b 11             	mov    (%r9),%edx
    177d:	45 0f b7 09          	movzwl (%r9),%r9d
    1781:	c1 ea 10             	shr    $0x10,%edx
    1784:	66 45 89 08          	mov    %r9w,(%r8)
    1788:	41 88 50 02          	mov    %dl,0x2(%r8)
    178c:	49 8d 53 04          	lea    0x4(%r11),%rdx
    1790:	48 39 da             	cmp    %rbx,%rdx
    1793:	0f 83 07 01 00 00    	jae    18a0 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a0>
    1799:	4c 8d 44 08 0c       	lea    0xc(%rax,%rcx,1),%r8
    179e:	41 0f b6 50 02       	movzbl 0x2(%r8),%edx
    17a3:	45 0f b6 48 01       	movzbl 0x1(%r8),%r9d
    17a8:	c1 e2 10             	shl    $0x10,%edx
    17ab:	41 c1 e1 08          	shl    $0x8,%r9d
    17af:	44 09 ca             	or     %r9d,%edx
    17b2:	45 0f b6 08          	movzbl (%r8),%r9d
    17b6:	44 09 ca             	or     %r9d,%edx
    17b9:	c4 62 6a f5 ce       	pext   %esi,%edx,%r9d
    17be:	41 c1 e1 06          	shl    $0x6,%r9d
    17c2:	c4 e2 6a f5 d7       	pext   %edi,%edx,%edx
    17c7:	44 09 ca             	or     %r9d,%edx
    17ca:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    17cf:	4d 8d 0c 96          	lea    (%r14,%rdx,4),%r9
    17d3:	41 8b 11             	mov    (%r9),%edx
    17d6:	45 0f b7 09          	movzwl (%r9),%r9d
    17da:	c1 ea 10             	shr    $0x10,%edx
    17dd:	66 45 89 08          	mov    %r9w,(%r8)
    17e1:	41 88 50 02          	mov    %dl,0x2(%r8)
    17e5:	49 8d 53 05          	lea    0x5(%r11),%rdx
    17e9:	48 39 da             	cmp    %rbx,%rdx
    17ec:	0f 83 ae 00 00 00    	jae    18a0 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a0>
    17f2:	4c 8d 44 08 0f       	lea    0xf(%rax,%rcx,1),%r8
    17f7:	41 0f b6 50 02       	movzbl 0x2(%r8),%edx
    17fc:	45 0f b6 48 01       	movzbl 0x1(%r8),%r9d
    1801:	c1 e2 10             	shl    $0x10,%edx
    1804:	41 c1 e1 08          	shl    $0x8,%r9d
    1808:	44 09 ca             	or     %r9d,%edx
    180b:	45 0f b6 08          	movzbl (%r8),%r9d
    180f:	44 09 ca             	or     %r9d,%edx
    1812:	c4 62 6a f5 ce       	pext   %esi,%edx,%r9d
    1817:	41 c1 e1 06          	shl    $0x6,%r9d
    181b:	c4 e2 6a f5 d7       	pext   %edi,%edx,%edx
    1820:	44 09 ca             	or     %r9d,%edx
    1823:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1828:	4d 8d 0c 96          	lea    (%r14,%rdx,4),%r9
    182c:	41 8b 11             	mov    (%r9),%edx
    182f:	45 0f b7 09          	movzwl (%r9),%r9d
    1833:	c1 ea 10             	shr    $0x10,%edx
    1836:	66 45 89 08          	mov    %r9w,(%r8)
    183a:	41 88 50 02          	mov    %dl,0x2(%r8)
    183e:	49 8d 53 06          	lea    0x6(%r11),%rdx
    1842:	48 39 da             	cmp    %rbx,%rdx
    1845:	73 59                	jae    18a0 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x18a0>
    1847:	48 8d 54 08 12       	lea    0x12(%rax,%rcx,1),%rdx
    184c:	0f b6 42 01          	movzbl 0x1(%rdx),%eax
    1850:	0f b6 4a 02          	movzbl 0x2(%rdx),%ecx
    1854:	c1 e0 08             	shl    $0x8,%eax
    1857:	c1 e1 10             	shl    $0x10,%ecx
    185a:	09 c8                	or     %ecx,%eax
    185c:	0f b6 0a             	movzbl (%rdx),%ecx
    185f:	09 c8                	or     %ecx,%eax
    1861:	c4 e2 7a f5 f6       	pext   %esi,%eax,%esi
    1866:	c1 e6 06             	shl    $0x6,%esi
    1869:	c4 e2 7a f5 c7       	pext   %edi,%eax,%eax
    186e:	09 c6                	or     %eax,%esi
    1870:	41 0f b6 04 37       	movzbl (%r15,%rsi,1),%eax
    1875:	49 8d 0c 86          	lea    (%r14,%rax,4),%rcx
    1879:	8b 01                	mov    (%rcx),%eax
    187b:	0f b7 09             	movzwl (%rcx),%ecx
    187e:	c1 e8 10             	shr    $0x10,%eax
    1881:	66 89 0a             	mov    %cx,(%rdx)
    1884:	88 42 02             	mov    %al,0x2(%rdx)
    1887:	c5 f8 77             	vzeroupper
    188a:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    188e:	5b                   	pop    %rbx
    188f:	41 5c                	pop    %r12
    1891:	41 5d                	pop    %r13
    1893:	41 5e                	pop    %r14
    1895:	41 5f                	pop    %r15
    1897:	5d                   	pop    %rbp
    1898:	c3                   	ret
    1899:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
    18a0:	c5 f8 77             	vzeroupper
    18a3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    18a7:	5b                   	pop    %rbx
    18a8:	41 5c                	pop    %r12
    18aa:	41 5d                	pop    %r13
    18ac:	41 5e                	pop    %r14
    18ae:	41 5f                	pop    %r15
    18b0:	5d                   	pop    %rbp
    18b1:	c3                   	ret
    18b2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    18b8:	4c 8b 9c 24 80 00 00 	mov    0x80(%rsp),%r11
    18bf:	00 
    18c0:	e9 3b fb ff ff       	jmp    1400 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0x1400>
    18c5:	4d 89 c3             	mov    %r8,%r11
    18c8:	49 8d 50 28          	lea    0x28(%r8),%rdx
    18cc:	e9 52 f4 ff ff       	jmp    d23 <jshc_channel::avx2_chain_tilebmi2(unsigned int const*, unsigned int const*, unsigned char*, unsigned long)+0xd23>
    18d1:	0f 1f 40 00          	nopl   0x0(%rax)
    18d5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
    18dc:	00 00 00 00 

00000000000018e0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)>:
    18e0:	f3 0f 1e fa          	endbr64
    18e4:	55                   	push   %rbp
    18e5:	48 89 e5             	mov    %rsp,%rbp
    18e8:	41 57                	push   %r15
    18ea:	41 56                	push   %r14
    18ec:	41 55                	push   %r13
    18ee:	41 54                	push   %r12
    18f0:	53                   	push   %rbx
    18f1:	48 83 e4 e0          	and    $0xffffffffffffffe0,%rsp
    18f5:	48 81 ec a8 00 00 00 	sub    $0xa8,%rsp
    18fc:	4c 89 84 24 a0 00 00 	mov    %r8,0xa0(%rsp)
    1903:	00 
    1904:	4d 85 c0             	test   %r8,%r8
    1907:	0f 84 96 1a 00 00    	je     33a3 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac3>
    190d:	49 89 f6             	mov    %rsi,%r14
    1910:	48 89 d0             	mov    %rdx,%rax
    1913:	4b 8d 34 40          	lea    (%r8,%r8,2),%rsi
    1917:	ba 00 04 00 00       	mov    $0x400,%edx
    191c:	48 39 d6             	cmp    %rdx,%rsi
    191f:	49 89 ff             	mov    %rdi,%r15
    1922:	48 0f 47 f2          	cmova  %rdx,%rsi
    1926:	31 d2                	xor    %edx,%edx
    1928:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
    192f:	00 
    1930:	0f 18 04 10          	prefetchnta (%rax,%rdx,1)
    1934:	48 83 c2 40          	add    $0x40,%rdx
    1938:	48 39 f2             	cmp    %rsi,%rdx
    193b:	72 f3                	jb     1930 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x50>
    193d:	4c 8b 9c 24 a0 00 00 	mov    0xa0(%rsp),%r11
    1944:	00 
    1945:	48 89 c7             	mov    %rax,%rdi
    1948:	48 89 ce             	mov    %rcx,%rsi
    194b:	45 31 d2             	xor    %r10d,%r10d
    194e:	41 b9 fc fc fc 00    	mov    $0xfcfcfc,%r9d
    1954:	41 b8 03 03 03 00    	mov    $0x30303,%r8d
    195a:	eb 55                	jmp    19b1 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xd1>
    195c:	0f 1f 40 00          	nopl   0x0(%rax)
    1960:	0f b6 57 01          	movzbl 0x1(%rdi),%edx
    1964:	0f b6 5f 02          	movzbl 0x2(%rdi),%ebx
    1968:	49 ff c2             	inc    %r10
    196b:	48 83 c6 03          	add    $0x3,%rsi
    196f:	48 83 c7 03          	add    $0x3,%rdi
    1973:	c1 e3 10             	shl    $0x10,%ebx
    1976:	c1 e2 08             	shl    $0x8,%edx
    1979:	09 da                	or     %ebx,%edx
    197b:	0f b6 5f fd          	movzbl -0x3(%rdi),%ebx
    197f:	09 da                	or     %ebx,%edx
    1981:	c4 c2 6a f5 d9       	pext   %r9d,%edx,%ebx
    1986:	c1 e3 06             	shl    $0x6,%ebx
    1989:	c4 c2 6a f5 d0       	pext   %r8d,%edx,%edx
    198e:	09 da                	or     %ebx,%edx
    1990:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1995:	49 8d 1c 96          	lea    (%r14,%rdx,4),%rbx
    1999:	8b 13                	mov    (%rbx),%edx
    199b:	0f b7 1b             	movzwl (%rbx),%ebx
    199e:	c1 ea 10             	shr    $0x10,%edx
    19a1:	66 89 5e fd          	mov    %bx,-0x3(%rsi)
    19a5:	88 56 ff             	mov    %dl,-0x1(%rsi)
    19a8:	4d 39 d3             	cmp    %r10,%r11
    19ab:	0f 84 07 1a 00 00    	je     33b8 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ad8>
    19b1:	40 f6 c6 3f          	test   $0x3f,%sil
    19b5:	75 a9                	jne    1960 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x80>
    19b7:	49 8d 52 48          	lea    0x48(%r10),%rdx
    19bb:	4c 89 94 24 98 00 00 	mov    %r10,0x98(%rsp)
    19c2:	00 
    19c3:	48 39 94 24 a0 00 00 	cmp    %rdx,0xa0(%rsp)
    19ca:	00 
    19cb:	0f 82 fc 19 00 00    	jb     33cd <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1aed>
    19d1:	4b 8d 14 52          	lea    (%r10,%r10,2),%rdx
    19d5:	48 89 44 24 68       	mov    %rax,0x68(%rsp)
    19da:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 19e2 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x102>
    19e1:	00 
    19e2:	41 bd fc fc fc 00    	mov    $0xfcfcfc,%r13d
    19e8:	48 8d 1c 11          	lea    (%rcx,%rdx,1),%rbx
    19ec:	48 89 4c 24 60       	mov    %rcx,0x60(%rsp)
    19f1:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 19f9 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x119>
    19f8:	00 
    19f9:	41 bc 03 03 03 00    	mov    $0x30303,%r12d
    19ff:	48 89 9c 24 90 00 00 	mov    %rbx,0x90(%rsp)
    1a06:	00 
    1a07:	48 8d 9c 10 00 04 00 	lea    0x400(%rax,%rdx,1),%rbx
    1a0e:	00 
    1a0f:	4c 89 d0             	mov    %r10,%rax
    1a12:	eb 0f                	jmp    1a23 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x143>
    1a14:	0f 1f 40 00          	nopl   0x0(%rax)
    1a18:	48 89 94 24 98 00 00 	mov    %rdx,0x98(%rsp)
    1a1f:	00 
    1a20:	48 89 d0             	mov    %rdx,%rax
    1a23:	48 05 96 01 00 00    	add    $0x196,%rax
    1a29:	48 39 84 24 a0 00 00 	cmp    %rax,0xa0(%rsp)
    1a30:	00 
    1a31:	72 15                	jb     1a48 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x168>
    1a33:	0f 18 03             	prefetchnta (%rbx)
    1a36:	0f 18 43 40          	prefetchnta 0x40(%rbx)
    1a3a:	0f 18 83 80 00 00 00 	prefetchnta 0x80(%rbx)
    1a41:	0f 18 83 bf 00 00 00 	prefetchnta 0xbf(%rbx)
    1a48:	8b 83 15 fc ff ff    	mov    -0x3eb(%rbx),%eax
    1a4e:	44 8b 9b 00 fc ff ff 	mov    -0x400(%rbx),%r11d
    1a55:	44 8b 8b 06 fc ff ff 	mov    -0x3fa(%rbx),%r9d
    1a5c:	44 8b 83 09 fc ff ff 	mov    -0x3f7(%rbx),%r8d
    1a63:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    1a68:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    1a6d:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    1a74:	8b 83 12 fc ff ff    	mov    -0x3ee(%rbx),%eax
    1a7a:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    1a81:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    1a86:	c1 e6 06             	shl    $0x6,%esi
    1a89:	44 8b 93 03 fc ff ff 	mov    -0x3fd(%rbx),%r10d
    1a90:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    1a95:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    1a9a:	8b 83 0f fc ff ff    	mov    -0x3f1(%rbx),%eax
    1aa0:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    1aa7:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    1aae:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    1ab3:	44 09 de             	or     %r11d,%esi
    1ab6:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    1abb:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    1ac0:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    1ac4:	8b bb 0c fc ff ff    	mov    -0x3f4(%rbx),%edi
    1aca:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    1acf:	89 54 24 78          	mov    %edx,0x78(%rsp)
    1ad3:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    1ad8:	c1 e2 06             	shl    $0x6,%edx
    1adb:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    1ae0:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    1ae5:	89 44 24 70          	mov    %eax,0x70(%rsp)
    1ae9:	44 09 ca             	or     %r9d,%edx
    1aec:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    1af3:	00 
    1af4:	c1 e1 06             	shl    $0x6,%ecx
    1af7:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    1afc:	c1 e0 06             	shl    $0x6,%eax
    1aff:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    1b04:	41 c1 e1 06          	shl    $0x6,%r9d
    1b08:	44 09 c0             	or     %r8d,%eax
    1b0b:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    1b10:	44 09 d1             	or     %r10d,%ecx
    1b13:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    1b18:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    1b1f:	00 
    1b20:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    1b25:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    1b2c:	00 
    1b2d:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    1b32:	41 c1 e3 06          	shl    $0x6,%r11d
    1b36:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    1b3b:	41 c1 e2 06          	shl    $0x6,%r10d
    1b3f:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    1b44:	45 89 d8             	mov    %r11d,%r8d
    1b47:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    1b4e:	00 
    1b4f:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1b54:	41 09 f8             	or     %edi,%r8d
    1b57:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    1b5c:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
    1b62:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    1b67:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    1b6c:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
    1b73:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    1b78:	41 c1 e0 06          	shl    $0x6,%r8d
    1b7c:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    1b81:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    1b86:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
    1b8c:	c4 41 79 6e 0c b6    	vmovd  (%r14,%rsi,4),%xmm9
    1b92:	44 8b 9b 18 fc ff ff 	mov    -0x3e8(%rbx),%r11d
    1b99:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
    1ba0:	44 8b 83 21 fc ff ff 	mov    -0x3df(%rbx),%r8d
    1ba7:	c4 43 31 22 0c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm9,%xmm9
    1bae:	44 8b 8b 1e fc ff ff 	mov    -0x3e2(%rbx),%r9d
    1bb5:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1bb9:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
    1bbf:	44 8b 93 1b fc ff ff 	mov    -0x3e5(%rbx),%r10d
    1bc6:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
    1bcd:	8b 83 2d fc ff ff    	mov    -0x3d3(%rbx),%eax
    1bd3:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    1bd8:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    1bdd:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    1be4:	8b 83 2a fc ff ff    	mov    -0x3d6(%rbx),%eax
    1bea:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    1bf1:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    1bf6:	c1 e6 06             	shl    $0x6,%esi
    1bf9:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    1bfe:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    1c03:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    1c08:	8b 83 27 fc ff ff    	mov    -0x3d9(%rbx),%eax
    1c0e:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    1c15:	44 09 de             	or     %r11d,%esi
    1c18:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    1c1f:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    1c24:	c1 e1 06             	shl    $0x6,%ecx
    1c27:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    1c2c:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    1c30:	8b bb 24 fc ff ff    	mov    -0x3dc(%rbx),%edi
    1c36:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    1c3b:	89 54 24 78          	mov    %edx,0x78(%rsp)
    1c3f:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    1c44:	c1 e2 06             	shl    $0x6,%edx
    1c47:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    1c4c:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    1c51:	89 44 24 70          	mov    %eax,0x70(%rsp)
    1c55:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    1c5a:	c1 e0 06             	shl    $0x6,%eax
    1c5d:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    1c62:	44 09 c0             	or     %r8d,%eax
    1c65:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    1c6a:	44 09 ca             	or     %r9d,%edx
    1c6d:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    1c74:	00 
    1c75:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    1c7a:	44 09 d1             	or     %r10d,%ecx
    1c7d:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    1c82:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    1c87:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    1c8c:	c5 31 6c c9          	vpunpcklqdq %xmm1,%xmm9,%xmm9
    1c90:	41 c1 e1 06          	shl    $0x6,%r9d
    1c94:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1c99:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    1c9e:	c4 63 35 38 c8 01    	vinserti128 $0x1,%xmm0,%ymm9,%ymm9
    1ca4:	41 c1 e3 06          	shl    $0x6,%r11d
    1ca8:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    1caf:	00 
    1cb0:	c4 62 35 00 cb       	vpshufb %ymm3,%ymm9,%ymm9
    1cb5:	45 89 d8             	mov    %r11d,%r8d
    1cb8:	c4 42 5d 36 c9       	vpermd %ymm9,%ymm4,%ymm9
    1cbd:	41 09 f8             	or     %edi,%r8d
    1cc0:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    1cc5:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    1cca:	41 c1 e0 06          	shl    $0x6,%r8d
    1cce:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    1cd3:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    1cd8:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    1cdd:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    1ce4:	00 
    1ce5:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
    1ceb:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
    1cf1:	c4 c1 79 6e 34 b6    	vmovd  (%r14,%rsi,4),%xmm6
    1cf7:	41 c1 e2 06          	shl    $0x6,%r10d
    1cfb:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
    1d02:	44 8b 9b 30 fc ff ff 	mov    -0x3d0(%rbx),%r11d
    1d09:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    1d10:	00 
    1d11:	c4 c3 49 22 34 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm6,%xmm6
    1d18:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    1d1d:	44 8b 83 39 fc ff ff 	mov    -0x3c7(%rbx),%r8d
    1d24:	44 8b 8b 36 fc ff ff 	mov    -0x3ca(%rbx),%r9d
    1d2b:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
    1d32:	44 8b 93 33 fc ff ff 	mov    -0x3cd(%rbx),%r10d
    1d39:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1d3d:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
    1d43:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
    1d4a:	8b 83 45 fc ff ff    	mov    -0x3bb(%rbx),%eax
    1d50:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    1d55:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    1d5a:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    1d61:	8b 83 42 fc ff ff    	mov    -0x3be(%rbx),%eax
    1d67:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    1d6e:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    1d73:	c1 e6 06             	shl    $0x6,%esi
    1d76:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    1d7b:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    1d80:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    1d85:	8b 83 3f fc ff ff    	mov    -0x3c1(%rbx),%eax
    1d8b:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    1d92:	44 09 de             	or     %r11d,%esi
    1d95:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    1d9c:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    1da1:	c1 e1 06             	shl    $0x6,%ecx
    1da4:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    1da9:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    1dad:	8b bb 3c fc ff ff    	mov    -0x3c4(%rbx),%edi
    1db3:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    1db8:	89 54 24 78          	mov    %edx,0x78(%rsp)
    1dbc:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    1dc1:	c1 e2 06             	shl    $0x6,%edx
    1dc4:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    1dc9:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    1dce:	89 44 24 70          	mov    %eax,0x70(%rsp)
    1dd2:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    1dd7:	c1 e0 06             	shl    $0x6,%eax
    1dda:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    1ddf:	44 09 c0             	or     %r8d,%eax
    1de2:	44 09 ca             	or     %r9d,%edx
    1de5:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    1dea:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    1def:	44 09 d1             	or     %r10d,%ecx
    1df2:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    1df7:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1dfc:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    1e01:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    1e06:	c5 c9 6c f1          	vpunpcklqdq %xmm1,%xmm6,%xmm6
    1e0a:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    1e0f:	c4 e3 4d 38 f0 01    	vinserti128 $0x1,%xmm0,%ymm6,%ymm6
    1e15:	41 c1 e3 06          	shl    $0x6,%r11d
    1e19:	c4 e2 4d 00 f3       	vpshufb %ymm3,%ymm6,%ymm6
    1e1e:	45 89 d8             	mov    %r11d,%r8d
    1e21:	c4 e2 5d 36 f6       	vpermd %ymm6,%ymm4,%ymm6
    1e26:	41 09 f8             	or     %edi,%r8d
    1e29:	c5 79 6f e6          	vmovdqa %xmm6,%xmm12
    1e2d:	c4 e3 7d 39 f6 01    	vextracti128 $0x1,%ymm6,%xmm6
    1e33:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    1e38:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    1e3f:	00 
    1e40:	c4 c3 49 0f f4 08    	vpalignr $0x8,%xmm12,%xmm6,%xmm6
    1e46:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    1e4b:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    1e52:	00 
    1e53:	41 c1 e1 06          	shl    $0x6,%r9d
    1e57:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
    1e5d:	c4 c1 79 6e 2c b6    	vmovd  (%r14,%rsi,4),%xmm5
    1e63:	41 c1 e0 06          	shl    $0x6,%r8d
    1e67:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    1e6e:	00 
    1e6f:	41 c1 e2 06          	shl    $0x6,%r10d
    1e73:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    1e78:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    1e7d:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    1e84:	00 
    1e85:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    1e8a:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    1e8f:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
    1e95:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
    1e9c:	c4 c3 51 22 2c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm5,%xmm5
    1ea3:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
    1eaa:	44 8b 83 51 fc ff ff 	mov    -0x3af(%rbx),%r8d
    1eb1:	44 8b 8b 4e fc ff ff 	mov    -0x3b2(%rbx),%r9d
    1eb8:	44 8b 93 4b fc ff ff 	mov    -0x3b5(%rbx),%r10d
    1ebf:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    1ec3:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
    1ec9:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
    1ed0:	8b 83 5d fc ff ff    	mov    -0x3a3(%rbx),%eax
    1ed6:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    1edb:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    1ee0:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    1ee7:	8b 83 5a fc ff ff    	mov    -0x3a6(%rbx),%eax
    1eed:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    1ef4:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    1ef8:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    1efd:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    1f02:	8b 83 57 fc ff ff    	mov    -0x3a9(%rbx),%eax
    1f08:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    1f0f:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    1f16:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    1f1b:	c1 e1 06             	shl    $0x6,%ecx
    1f1e:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    1f23:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    1f28:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    1f2c:	8b bb 54 fc ff ff    	mov    -0x3ac(%rbx),%edi
    1f32:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    1f37:	89 54 24 78          	mov    %edx,0x78(%rsp)
    1f3b:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    1f40:	c1 e2 06             	shl    $0x6,%edx
    1f43:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    1f48:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    1f4d:	89 44 24 70          	mov    %eax,0x70(%rsp)
    1f51:	44 8b 9b 48 fc ff ff 	mov    -0x3b8(%rbx),%r11d
    1f58:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    1f5d:	c1 e0 06             	shl    $0x6,%eax
    1f60:	44 09 ca             	or     %r9d,%edx
    1f63:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    1f68:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    1f6f:	00 
    1f70:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    1f75:	c1 e6 06             	shl    $0x6,%esi
    1f78:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    1f7d:	44 09 c0             	or     %r8d,%eax
    1f80:	44 09 de             	or     %r11d,%esi
    1f83:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    1f88:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    1f8d:	44 09 d1             	or     %r10d,%ecx
    1f90:	41 c1 e1 06          	shl    $0x6,%r9d
    1f94:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    1f9b:	00 
    1f9c:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    1fa2:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    1fa7:	41 c1 e3 06          	shl    $0x6,%r11d
    1fab:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    1fb2:	00 
    1fb3:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    1fb8:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    1fbd:	45 89 d8             	mov    %r11d,%r8d
    1fc0:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    1fc5:	41 c1 e2 06          	shl    $0x6,%r10d
    1fc9:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    1fce:	41 09 f8             	or     %edi,%r8d
    1fd1:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    1fd8:	00 
    1fd9:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    1fde:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    1fe3:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    1fe8:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    1fed:	c5 79 6f ed          	vmovdqa %xmm5,%xmm13
    1ff1:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    1ff7:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    1ffc:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
    2002:	c4 c3 4d 38 f5 01    	vinserti128 $0x1,%xmm13,%ymm6,%ymm6
    2008:	41 c1 e0 06          	shl    $0x6,%r8d
    200c:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
    2012:	c4 41 79 6e 04 b6    	vmovd  (%r14,%rsi,4),%xmm8
    2018:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    201d:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
    2024:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    2029:	c4 43 39 22 04 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm8,%xmm8
    2030:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
    2037:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    203b:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
    2041:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
    2048:	8b 83 75 fc ff ff    	mov    -0x38b(%rbx),%eax
    204e:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    2053:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    2058:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    205f:	8b 83 72 fc ff ff    	mov    -0x38e(%rbx),%eax
    2065:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    206c:	c5 39 6c c1          	vpunpcklqdq %xmm1,%xmm8,%xmm8
    2070:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    2075:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    207a:	8b 83 6f fc ff ff    	mov    -0x391(%rbx),%eax
    2080:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    2087:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    208e:	c4 63 3d 38 c0 01    	vinserti128 $0x1,%xmm0,%ymm8,%ymm8
    2094:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    2099:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    209e:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    20a2:	c4 62 3d 00 c3       	vpshufb %ymm3,%ymm8,%ymm8
    20a7:	89 54 24 78          	mov    %edx,0x78(%rsp)
    20ab:	8b bb 6c fc ff ff    	mov    -0x394(%rbx),%edi
    20b1:	c4 42 5d 36 c0       	vpermd %ymm8,%ymm4,%ymm8
    20b6:	44 8b 9b 60 fc ff ff 	mov    -0x3a0(%rbx),%r11d
    20bd:	44 8b 83 69 fc ff ff 	mov    -0x397(%rbx),%r8d
    20c4:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    20c9:	44 8b 8b 66 fc ff ff 	mov    -0x39a(%rbx),%r9d
    20d0:	44 8b 93 63 fc ff ff 	mov    -0x39d(%rbx),%r10d
    20d7:	89 44 24 70          	mov    %eax,0x70(%rsp)
    20db:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    20e0:	c1 e6 06             	shl    $0x6,%esi
    20e3:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    20e8:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    20ed:	44 09 de             	or     %r11d,%esi
    20f0:	c1 e0 06             	shl    $0x6,%eax
    20f3:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    20f8:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    20fd:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    2102:	c1 e2 06             	shl    $0x6,%edx
    2105:	44 09 c0             	or     %r8d,%eax
    2108:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    210d:	44 09 ca             	or     %r9d,%edx
    2110:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    2117:	00 
    2118:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    211d:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    2122:	41 c1 e3 06          	shl    $0x6,%r11d
    2126:	c1 e1 06             	shl    $0x6,%ecx
    2129:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    212e:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    2133:	45 89 d8             	mov    %r11d,%r8d
    2136:	44 09 d1             	or     %r10d,%ecx
    2139:	41 c1 e1 06          	shl    $0x6,%r9d
    213d:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    2144:	00 
    2145:	41 09 f8             	or     %edi,%r8d
    2148:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    214f:	00 
    2150:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    2155:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    215a:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    215f:	41 c1 e2 06          	shl    $0x6,%r10d
    2163:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    2168:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    216f:	00 
    2170:	41 c1 e0 06          	shl    $0x6,%r8d
    2174:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    2179:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
    217f:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    2184:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
    218a:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    218f:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    2194:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
    219b:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    21a0:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
    21a7:	c4 c1 79 6e 3c b6    	vmovd  (%r14,%rsi,4),%xmm7
    21ad:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    21b1:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
    21b7:	c4 c3 41 22 3c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm7,%xmm7
    21be:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
    21c5:	8b 83 8d fc ff ff    	mov    -0x373(%rbx),%eax
    21cb:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    21d0:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    21d5:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    21dc:	c5 c1 6c f9          	vpunpcklqdq %xmm1,%xmm7,%xmm7
    21e0:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    21e7:	8b 83 8a fc ff ff    	mov    -0x376(%rbx),%eax
    21ed:	c4 e3 45 38 f8 01    	vinserti128 $0x1,%xmm0,%ymm7,%ymm7
    21f3:	44 8b 9b 78 fc ff ff 	mov    -0x388(%rbx),%r11d
    21fa:	44 8b 83 81 fc ff ff 	mov    -0x37f(%rbx),%r8d
    2201:	c4 e2 45 00 fb       	vpshufb %ymm3,%ymm7,%ymm7
    2206:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    220b:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    2210:	8b 83 87 fc ff ff    	mov    -0x379(%rbx),%eax
    2216:	44 8b 8b 7e fc ff ff 	mov    -0x382(%rbx),%r9d
    221d:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    2224:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    2229:	c1 e6 06             	shl    $0x6,%esi
    222c:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    2231:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    2236:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    223a:	8b bb 84 fc ff ff    	mov    -0x37c(%rbx),%edi
    2240:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    2245:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    224c:	44 09 de             	or     %r11d,%esi
    224f:	44 8b 93 7b fc ff ff 	mov    -0x385(%rbx),%r10d
    2256:	c4 e2 5d 36 ff       	vpermd %ymm7,%ymm4,%ymm7
    225b:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    2260:	89 44 24 70          	mov    %eax,0x70(%rsp)
    2264:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    2269:	c1 e0 06             	shl    $0x6,%eax
    226c:	89 54 24 78          	mov    %edx,0x78(%rsp)
    2270:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    2275:	c1 e2 06             	shl    $0x6,%edx
    2278:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    227d:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    2282:	44 09 c0             	or     %r8d,%eax
    2285:	44 09 ca             	or     %r9d,%edx
    2288:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    228f:	00 
    2290:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    2295:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    229a:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    229f:	c1 e1 06             	shl    $0x6,%ecx
    22a2:	41 c1 e1 06          	shl    $0x6,%r9d
    22a6:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    22ab:	44 09 d1             	or     %r10d,%ecx
    22ae:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    22b5:	00 
    22b6:	41 c1 e3 06          	shl    $0x6,%r11d
    22ba:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    22c1:	00 
    22c2:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    22c7:	45 89 d8             	mov    %r11d,%r8d
    22ca:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    22cf:	41 c1 e2 06          	shl    $0x6,%r10d
    22d3:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    22d8:	41 09 f8             	or     %edi,%r8d
    22db:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    22e2:	00 
    22e3:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    22e8:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    22ed:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    22f2:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    22f7:	c4 81 79 6e 14 8e    	vmovd  (%r14,%r9,4),%xmm2
    22fd:	41 c1 e0 06          	shl    $0x6,%r8d
    2301:	c4 c1 79 6e 0c be    	vmovd  (%r14,%rdi,4),%xmm1
    2307:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    230c:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    2311:	c4 83 69 22 14 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm2,%xmm2
    2318:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    231d:	c4 83 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm1,%xmm1
    2324:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    2328:	c4 c1 79 6e 14 96    	vmovd  (%r14,%rdx,4),%xmm2
    232e:	c4 c3 69 22 14 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm2,%xmm2
    2335:	8b 83 a5 fc ff ff    	mov    -0x35b(%rbx),%eax
    233b:	c4 c1 79 6e 04 b6    	vmovd  (%r14,%rsi,4),%xmm0
    2341:	44 8b 9b 90 fc ff ff 	mov    -0x370(%rbx),%r11d
    2348:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    234d:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    2352:	44 8b 83 99 fc ff ff 	mov    -0x367(%rbx),%r8d
    2359:	44 8b 8b 96 fc ff ff 	mov    -0x36a(%rbx),%r9d
    2360:	c4 c3 79 22 04 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm0,%xmm0
    2367:	44 8b 93 93 fc ff ff 	mov    -0x36d(%rbx),%r10d
    236e:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    2375:	8b 83 a2 fc ff ff    	mov    -0x35e(%rbx),%eax
    237b:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    2382:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    2387:	c1 e6 06             	shl    $0x6,%esi
    238a:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    238f:	44 09 de             	or     %r11d,%esi
    2392:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    2396:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    239b:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    23a0:	8b 83 9f fc ff ff    	mov    -0x361(%rbx),%eax
    23a6:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    23ab:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    23b2:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    23b8:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    23bd:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    23c1:	8b bb 9c fc ff ff    	mov    -0x364(%rbx),%edi
    23c7:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    23cc:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    23d3:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    23d8:	c1 e1 06             	shl    $0x6,%ecx
    23db:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    23e0:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    23e5:	89 44 24 70          	mov    %eax,0x70(%rsp)
    23e9:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    23ee:	c1 e0 06             	shl    $0x6,%eax
    23f1:	89 54 24 78          	mov    %edx,0x78(%rsp)
    23f5:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    23fa:	c1 e2 06             	shl    $0x6,%edx
    23fd:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    2402:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    2407:	44 09 c0             	or     %r8d,%eax
    240a:	44 09 ca             	or     %r9d,%edx
    240d:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    2414:	00 
    2415:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    241a:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    241f:	44 09 d1             	or     %r10d,%ecx
    2422:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    2429:	00 
    242a:	41 c1 e1 06          	shl    $0x6,%r9d
    242e:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    2433:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    2438:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    243d:	41 c1 e3 06          	shl    $0x6,%r11d
    2441:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    2448:	00 
    2449:	41 c1 e2 06          	shl    $0x6,%r10d
    244d:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    2452:	45 89 d8             	mov    %r11d,%r8d
    2455:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    245a:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    2461:	00 
    2462:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    2467:	41 09 f8             	or     %edi,%r8d
    246a:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    246f:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    2474:	41 c1 e0 06          	shl    $0x6,%r8d
    2478:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    247d:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    2482:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    2487:	c4 01 79 6e 14 8e    	vmovd  (%r14,%r9,4),%xmm10
    248d:	c4 c1 79 6e 14 be    	vmovd  (%r14,%rdi,4),%xmm2
    2493:	c4 c1 79 6e 0c b6    	vmovd  (%r14,%rsi,4),%xmm1
    2499:	44 8b 9b a8 fc ff ff 	mov    -0x358(%rbx),%r11d
    24a0:	c4 03 29 22 14 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm10,%xmm10
    24a7:	c4 83 69 22 14 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm2,%xmm2
    24ae:	c4 c3 71 22 0c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm1,%xmm1
    24b5:	44 8b 83 b1 fc ff ff 	mov    -0x34f(%rbx),%r8d
    24bc:	c4 c1 69 6c d2       	vpunpcklqdq %xmm10,%xmm2,%xmm2
    24c1:	c4 41 79 6e 14 96    	vmovd  (%r14,%rdx,4),%xmm10
    24c7:	44 8b 8b ae fc ff ff 	mov    -0x352(%rbx),%r9d
    24ce:	44 8b 93 ab fc ff ff 	mov    -0x355(%rbx),%r10d
    24d5:	c4 43 29 22 14 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm10,%xmm10
    24dc:	8b 83 bd fc ff ff    	mov    -0x343(%rbx),%eax
    24e2:	c4 c2 7a f5 f5       	pext   %r13d,%eax,%esi
    24e7:	c4 c2 7a f5 c4       	pext   %r12d,%eax,%eax
    24ec:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    24f3:	8b 83 ba fc ff ff    	mov    -0x346(%rbx),%eax
    24f9:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    2500:	c4 c2 22 f5 f5       	pext   %r13d,%r11d,%esi
    2505:	c1 e6 06             	shl    $0x6,%esi
    2508:	c4 42 22 f5 dc       	pext   %r12d,%r11d,%r11d
    250d:	c4 c2 7a f5 cd       	pext   %r13d,%eax,%ecx
    2512:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    2517:	8b 83 b7 fc ff ff    	mov    -0x349(%rbx),%eax
    251d:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    2524:	44 09 de             	or     %r11d,%esi
    2527:	89 8c 24 84 00 00 00 	mov    %ecx,0x84(%rsp)
    252e:	c4 c2 2a f5 cd       	pext   %r13d,%r10d,%ecx
    2533:	c1 e1 06             	shl    $0x6,%ecx
    2536:	c4 c2 7a f5 fd       	pext   %r13d,%eax,%edi
    253b:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    253f:	8b bb b4 fc ff ff    	mov    -0x34c(%rbx),%edi
    2545:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    254a:	89 54 24 78          	mov    %edx,0x78(%rsp)
    254e:	c4 c2 32 f5 d5       	pext   %r13d,%r9d,%edx
    2553:	c1 e2 06             	shl    $0x6,%edx
    2556:	c4 42 32 f5 cc       	pext   %r12d,%r9d,%r9d
    255b:	c4 c2 42 f5 c5       	pext   %r13d,%edi,%eax
    2560:	89 44 24 70          	mov    %eax,0x70(%rsp)
    2564:	c4 c2 3a f5 c5       	pext   %r13d,%r8d,%eax
    2569:	c1 e0 06             	shl    $0x6,%eax
    256c:	c4 42 3a f5 c4       	pext   %r12d,%r8d,%r8d
    2571:	44 09 c0             	or     %r8d,%eax
    2574:	c4 c2 42 f5 fc       	pext   %r12d,%edi,%edi
    2579:	44 09 ca             	or     %r9d,%edx
    257c:	c4 42 2a f5 d4       	pext   %r12d,%r10d,%r10d
    2581:	44 09 d1             	or     %r10d,%ecx
    2584:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    2589:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    258e:	44 8b 5c 24 70       	mov    0x70(%rsp),%r11d
    2593:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    2598:	c4 c1 71 6c ca       	vpunpcklqdq %xmm10,%xmm1,%xmm1
    259d:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    25a2:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    25a8:	41 c1 e3 06          	shl    $0x6,%r11d
    25ac:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    25b1:	45 89 d8             	mov    %r11d,%r8d
    25b4:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    25b9:	41 09 f8             	or     %edi,%r8d
    25bc:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    25c1:	44 8b 44 24 7c       	mov    0x7c(%rsp),%r8d
    25c6:	41 c1 e0 06          	shl    $0x6,%r8d
    25ca:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    25cf:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    25d4:	44 8b 8c 24 84 00 00 	mov    0x84(%rsp),%r9d
    25db:	00 
    25dc:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    25e3:	00 
    25e4:	c4 41 79 6e 14 be    	vmovd  (%r14,%rdi,4),%xmm10
    25ea:	41 c1 e1 06          	shl    $0x6,%r9d
    25ee:	c4 c1 79 6e 14 b6    	vmovd  (%r14,%rsi,4),%xmm2
    25f4:	44 0b 8c 24 80 00 00 	or     0x80(%rsp),%r9d
    25fb:	00 
    25fc:	41 c1 e2 06          	shl    $0x6,%r10d
    2600:	c4 03 29 22 14 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm10,%xmm10
    2607:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    260c:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    2613:	00 
    2614:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    2619:	c4 c3 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm2,%xmm2
    2620:	c4 01 79 6e 1c 8e    	vmovd  (%r14,%r9,4),%xmm11
    2626:	c4 03 21 22 1c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm11,%xmm11
    262d:	c4 41 29 6c d3       	vpunpcklqdq %xmm11,%xmm10,%xmm10
    2632:	c4 41 79 6e 1c 96    	vmovd  (%r14,%rdx,4),%xmm11
    2638:	c4 43 21 22 1c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm11,%xmm11
    263f:	48 8b 84 24 90 00 00 	mov    0x90(%rsp),%rax
    2646:	00 
    2647:	c4 c1 69 6c d3       	vpunpcklqdq %xmm11,%xmm2,%xmm2
    264c:	c4 41 79 6f d8       	vmovdqa %xmm8,%xmm11
    2651:	c4 43 7d 39 c0 01    	vextracti128 $0x1,%ymm8,%xmm8
    2657:	c5 fd e7 70 20       	vmovntdq %ymm6,0x20(%rax)
    265c:	c4 c3 6d 38 d2 01    	vinserti128 $0x1,%xmm10,%ymm2,%ymm2
    2662:	c4 41 79 6f d1       	vmovdqa %xmm9,%xmm10
    2667:	c4 43 7d 39 c9 01    	vextracti128 $0x1,%ymm9,%xmm9
    266d:	48 05 c0 00 00 00    	add    $0xc0,%rax
    2673:	c4 43 39 0f c3 08    	vpalignr $0x8,%xmm11,%xmm8,%xmm8
    2679:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    267e:	c4 41 31 6c cc       	vpunpcklqdq %xmm12,%xmm9,%xmm9
    2683:	c4 c1 51 6c eb       	vpunpcklqdq %xmm11,%xmm5,%xmm5
    2688:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    268d:	c4 43 2d 38 c9 01    	vinserti128 $0x1,%xmm9,%ymm10,%ymm9
    2693:	c4 c3 55 38 e8 01    	vinserti128 $0x1,%xmm8,%ymm5,%ymm5
    2699:	c5 7d e7 88 40 ff ff 	vmovntdq %ymm9,-0xc0(%rax)
    26a0:	ff 
    26a1:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    26a5:	c5 79 6f c8          	vmovdqa %xmm0,%xmm9
    26a9:	c5 fd e7 68 80       	vmovntdq %ymm5,-0x80(%rax)
    26ae:	c5 79 6f c1          	vmovdqa %xmm1,%xmm8
    26b2:	c5 f9 6f ef          	vmovdqa %xmm7,%xmm5
    26b6:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    26bc:	c4 e3 7d 39 ff 01    	vextracti128 $0x1,%ymm7,%xmm7
    26c2:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    26c8:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    26ce:	c4 c1 41 6c f9       	vpunpcklqdq %xmm9,%xmm7,%xmm7
    26d3:	c4 c3 79 0f c1 08    	vpalignr $0x8,%xmm9,%xmm0,%xmm0
    26d9:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    26dd:	c4 e3 69 0f d6 08    	vpalignr $0x8,%xmm6,%xmm2,%xmm2
    26e3:	c4 e3 55 38 ef 01    	vinserti128 $0x1,%xmm7,%ymm5,%ymm5
    26e9:	c4 c3 7d 38 c0 01    	vinserti128 $0x1,%xmm8,%ymm0,%ymm0
    26ef:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    26f5:	c5 fd e7 68 a0       	vmovntdq %ymm5,-0x60(%rax)
    26fa:	c5 fd e7 40 c0       	vmovntdq %ymm0,-0x40(%rax)
    26ff:	c5 fd e7 48 e0       	vmovntdq %ymm1,-0x20(%rax)
    2704:	48 8b b4 24 98 00 00 	mov    0x98(%rsp),%rsi
    270b:	00 
    270c:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
    2713:	00 
    2714:	48 81 c3 c0 00 00 00 	add    $0xc0,%rbx
    271b:	48 8d 86 88 00 00 00 	lea    0x88(%rsi),%rax
    2722:	48 8d 56 40          	lea    0x40(%rsi),%rdx
    2726:	48 39 84 24 a0 00 00 	cmp    %rax,0xa0(%rsp)
    272d:	00 
    272e:	0f 83 e4 f2 ff ff    	jae    1a18 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x138>
    2734:	48 8b 44 24 68       	mov    0x68(%rsp),%rax
    2739:	48 8b 4c 24 60       	mov    0x60(%rsp),%rcx
    273e:	48 89 94 24 90 00 00 	mov    %rdx,0x90(%rsp)
    2745:	00 
    2746:	0f ae f8             	sfence
    2749:	48 8b 94 24 98 00 00 	mov    0x98(%rsp),%rdx
    2750:	00 
    2751:	48 83 c2 68          	add    $0x68,%rdx
    2755:	48 39 94 24 a0 00 00 	cmp    %rdx,0xa0(%rsp)
    275c:	00 
    275d:	0f 82 0c 07 00 00    	jb     2e6f <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x158f>
    2763:	48 8b 9c 24 90 00 00 	mov    0x90(%rsp),%rbx
    276a:	00 
    276b:	48 89 44 24 a0       	mov    %rax,-0x60(%rsp)
    2770:	41 bc fc fc fc 00    	mov    $0xfcfcfc,%r12d
    2776:	41 bb 03 03 03 00    	mov    $0x30303,%r11d
    277c:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2784 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xea4>
    2783:	00 
    2784:	c5 fd 6f 25 00 00 00 	vmovdqa 0x0(%rip),%ymm4        # 278c <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xeac>
    278b:	00 
    278c:	48 89 4c 24 98       	mov    %rcx,-0x68(%rsp)
    2791:	48 8d 14 5b          	lea    (%rbx,%rbx,2),%rdx
    2795:	48 8d 1c 11          	lea    (%rcx,%rdx,1),%rbx
    2799:	4c 8d 2c 10          	lea    (%rax,%rdx,1),%r13
    279d:	48 89 9c 24 98 00 00 	mov    %rbx,0x98(%rsp)
    27a4:	00 
    27a5:	0f 1f 00             	nopl   (%rax)
    27a8:	41 8b 45 15          	mov    0x15(%r13),%eax
    27ac:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
    27b1:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    27b6:	89 84 24 88 00 00 00 	mov    %eax,0x88(%rsp)
    27bd:	41 8b 45 12          	mov    0x12(%r13),%eax
    27c1:	89 8c 24 8c 00 00 00 	mov    %ecx,0x8c(%rsp)
    27c8:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
    27cd:	c4 c2 7a f5 fb       	pext   %r11d,%eax,%edi
    27d2:	41 8b 45 0f          	mov    0xf(%r13),%eax
    27d6:	89 bc 24 80 00 00 00 	mov    %edi,0x80(%rsp)
    27dd:	89 b4 24 84 00 00 00 	mov    %esi,0x84(%rsp)
    27e4:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    27e9:	c4 42 7a f5 c3       	pext   %r11d,%eax,%r8d
    27ee:	41 8b 45 0c          	mov    0xc(%r13),%eax
    27f2:	44 89 44 24 78       	mov    %r8d,0x78(%rsp)
    27f7:	89 7c 24 7c          	mov    %edi,0x7c(%rsp)
    27fb:	c4 42 7a f5 d4       	pext   %r12d,%eax,%r10d
    2800:	c4 c2 7a f5 cb       	pext   %r11d,%eax,%ecx
    2805:	41 8b 45 09          	mov    0x9(%r13),%eax
    2809:	89 4c 24 68          	mov    %ecx,0x68(%rsp)
    280d:	44 89 54 24 70       	mov    %r10d,0x70(%rsp)
    2812:	c4 42 7a f5 c4       	pext   %r12d,%eax,%r8d
    2817:	c4 c2 7a f5 f3       	pext   %r11d,%eax,%esi
    281c:	41 8b 45 06          	mov    0x6(%r13),%eax
    2820:	89 74 24 5c          	mov    %esi,0x5c(%rsp)
    2824:	44 89 44 24 60       	mov    %r8d,0x60(%rsp)
    2829:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
    282e:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    2833:	89 44 24 54          	mov    %eax,0x54(%rsp)
    2837:	41 8b 45 03          	mov    0x3(%r13),%eax
    283b:	89 4c 24 58          	mov    %ecx,0x58(%rsp)
    283f:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    2844:	c4 c2 7a f5 d3       	pext   %r11d,%eax,%edx
    2849:	41 8b 45 00          	mov    0x0(%r13),%eax
    284d:	89 7c 24 50          	mov    %edi,0x50(%rsp)
    2851:	89 54 24 4c          	mov    %edx,0x4c(%rsp)
    2855:	c4 42 7a f5 cc       	pext   %r12d,%eax,%r9d
    285a:	c4 c2 7a f5 cb       	pext   %r11d,%eax,%ecx
    285f:	41 8b 45 2d          	mov    0x2d(%r13),%eax
    2863:	89 4c 24 44          	mov    %ecx,0x44(%rsp)
    2867:	44 89 4c 24 48       	mov    %r9d,0x48(%rsp)
    286c:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
    2871:	c4 c2 7a f5 f3       	pext   %r11d,%eax,%esi
    2876:	41 8b 45 2a          	mov    0x2a(%r13),%eax
    287a:	89 74 24 3c          	mov    %esi,0x3c(%rsp)
    287e:	89 4c 24 40          	mov    %ecx,0x40(%rsp)
    2882:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
    2887:	c4 c2 7a f5 db       	pext   %r11d,%eax,%ebx
    288c:	41 8b 45 27          	mov    0x27(%r13),%eax
    2890:	89 74 24 38          	mov    %esi,0x38(%rsp)
    2894:	89 5c 24 34          	mov    %ebx,0x34(%rsp)
    2898:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    289d:	89 54 24 30          	mov    %edx,0x30(%rsp)
    28a1:	c4 c2 7a f5 d3       	pext   %r11d,%eax,%edx
    28a6:	89 54 24 2c          	mov    %edx,0x2c(%rsp)
    28aa:	41 8b 45 24          	mov    0x24(%r13),%eax
    28ae:	c4 42 7a f5 c4       	pext   %r12d,%eax,%r8d
    28b3:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    28b8:	89 44 24 24          	mov    %eax,0x24(%rsp)
    28bc:	41 8b 45 21          	mov    0x21(%r13),%eax
    28c0:	44 89 44 24 28       	mov    %r8d,0x28(%rsp)
    28c5:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
    28ca:	c4 c2 7a f5 d3       	pext   %r11d,%eax,%edx
    28cf:	41 8b 45 1e          	mov    0x1e(%r13),%eax
    28d3:	89 54 24 1c          	mov    %edx,0x1c(%rsp)
    28d7:	89 4c 24 20          	mov    %ecx,0x20(%rsp)
    28db:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    28e0:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    28e5:	89 44 24 14          	mov    %eax,0x14(%rsp)
    28e9:	41 8b 45 1b          	mov    0x1b(%r13),%eax
    28ed:	89 54 24 18          	mov    %edx,0x18(%rsp)
    28f1:	c4 42 7a f5 cc       	pext   %r12d,%eax,%r9d
    28f6:	c4 c2 7a f5 fb       	pext   %r11d,%eax,%edi
    28fb:	41 8b 45 18          	mov    0x18(%r13),%eax
    28ff:	89 7c 24 0c          	mov    %edi,0xc(%rsp)
    2903:	44 89 4c 24 10       	mov    %r9d,0x10(%rsp)
    2908:	c4 42 7a f5 d4       	pext   %r12d,%eax,%r10d
    290d:	c4 c2 7a f5 cb       	pext   %r11d,%eax,%ecx
    2912:	41 8b 45 45          	mov    0x45(%r13),%eax
    2916:	89 4c 24 04          	mov    %ecx,0x4(%rsp)
    291a:	44 89 54 24 08       	mov    %r10d,0x8(%rsp)
    291f:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
    2924:	c4 c2 7a f5 d3       	pext   %r11d,%eax,%edx
    2929:	41 8b 45 42          	mov    0x42(%r13),%eax
    292d:	89 54 24 fc          	mov    %edx,-0x4(%rsp)
    2931:	89 34 24             	mov    %esi,(%rsp)
    2934:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    2939:	c4 c2 7a f5 db       	pext   %r11d,%eax,%ebx
    293e:	41 8b 45 3f          	mov    0x3f(%r13),%eax
    2942:	89 7c 24 f8          	mov    %edi,-0x8(%rsp)
    2946:	89 5c 24 f4          	mov    %ebx,-0xc(%rsp)
    294a:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    294f:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    2954:	89 44 24 ec          	mov    %eax,-0x14(%rsp)
    2958:	41 8b 45 3c          	mov    0x3c(%r13),%eax
    295c:	89 54 24 f0          	mov    %edx,-0x10(%rsp)
    2960:	c4 c2 7a f5 cc       	pext   %r12d,%eax,%ecx
    2965:	c4 c2 7a f5 f3       	pext   %r11d,%eax,%esi
    296a:	41 8b 45 39          	mov    0x39(%r13),%eax
    296e:	89 74 24 e4          	mov    %esi,-0x1c(%rsp)
    2972:	89 4c 24 e8          	mov    %ecx,-0x18(%rsp)
    2976:	c4 c2 7a f5 f4       	pext   %r12d,%eax,%esi
    297b:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    2980:	89 44 24 dc          	mov    %eax,-0x24(%rsp)
    2984:	41 8b 45 36          	mov    0x36(%r13),%eax
    2988:	89 74 24 e0          	mov    %esi,-0x20(%rsp)
    298c:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    2991:	c4 42 7a f5 c3       	pext   %r11d,%eax,%r8d
    2996:	89 54 24 d8          	mov    %edx,-0x28(%rsp)
    299a:	44 89 44 24 d4       	mov    %r8d,-0x2c(%rsp)
    299f:	41 8b 45 33          	mov    0x33(%r13),%eax
    29a3:	45 8b 4d 4e          	mov    0x4e(%r13),%r9d
    29a7:	41 8b 75 48          	mov    0x48(%r13),%esi
    29ab:	c4 42 7a f5 d4       	pext   %r12d,%eax,%r10d
    29b0:	c4 c2 7a f5 c3       	pext   %r11d,%eax,%eax
    29b5:	89 44 24 cc          	mov    %eax,-0x34(%rsp)
    29b9:	41 8b 45 30          	mov    0x30(%r13),%eax
    29bd:	44 89 54 24 d0       	mov    %r10d,-0x30(%rsp)
    29c2:	45 8b 55 4b          	mov    0x4b(%r13),%r10d
    29c6:	c4 c2 4a f5 f4       	pext   %r12d,%esi,%esi
    29cb:	c1 e6 06             	shl    $0x6,%esi
    29ce:	c4 42 7a f5 c4       	pext   %r12d,%eax,%r8d
    29d3:	c4 c2 7a f5 fb       	pext   %r11d,%eax,%edi
    29d8:	41 8b 45 5d          	mov    0x5d(%r13),%eax
    29dc:	89 7c 24 c4          	mov    %edi,-0x3c(%rsp)
    29e0:	44 89 44 24 c8       	mov    %r8d,-0x38(%rsp)
    29e5:	c4 c2 7a f5 fc       	pext   %r12d,%eax,%edi
    29ea:	c4 c2 7a f5 d3       	pext   %r11d,%eax,%edx
    29ef:	41 8b 45 5a          	mov    0x5a(%r13),%eax
    29f3:	89 7c 24 c0          	mov    %edi,-0x40(%rsp)
    29f7:	89 54 24 bc          	mov    %edx,-0x44(%rsp)
    29fb:	41 8b 7d 54          	mov    0x54(%r13),%edi
    29ff:	c4 c2 7a f5 d4       	pext   %r12d,%eax,%edx
    2a04:	c4 c2 7a f5 db       	pext   %r11d,%eax,%ebx
    2a09:	41 8b 45 57          	mov    0x57(%r13),%eax
    2a0d:	89 54 24 b8          	mov    %edx,-0x48(%rsp)
    2a11:	c4 c2 32 f5 d4       	pext   %r12d,%r9d,%edx
    2a16:	c1 e2 06             	shl    $0x6,%edx
    2a19:	c4 42 32 f5 cb       	pext   %r11d,%r9d,%r9d
    2a1e:	89 5c 24 b4          	mov    %ebx,-0x4c(%rsp)
    2a22:	c4 42 7a f5 c4       	pext   %r12d,%eax,%r8d
    2a27:	c4 c2 7a f5 cb       	pext   %r11d,%eax,%ecx
    2a2c:	c4 c2 42 f5 c4       	pext   %r12d,%edi,%eax
    2a31:	89 44 24 a8          	mov    %eax,-0x58(%rsp)
    2a35:	44 89 44 24 b0       	mov    %r8d,-0x50(%rsp)
    2a3a:	44 09 ca             	or     %r9d,%edx
    2a3d:	45 8b 45 51          	mov    0x51(%r13),%r8d
    2a41:	c4 c2 42 f5 fb       	pext   %r11d,%edi,%edi
    2a46:	41 8b 5d 48          	mov    0x48(%r13),%ebx
    2a4a:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    2a4f:	89 4c 24 ac          	mov    %ecx,-0x54(%rsp)
    2a53:	c4 c2 2a f5 cc       	pext   %r12d,%r10d,%ecx
    2a58:	44 8b 4c 24 a8       	mov    -0x58(%rsp),%r9d
    2a5d:	c4 c2 3a f5 c4       	pext   %r12d,%r8d,%eax
    2a62:	c1 e0 06             	shl    $0x6,%eax
    2a65:	c4 42 3a f5 c3       	pext   %r11d,%r8d,%r8d
    2a6a:	44 09 c0             	or     %r8d,%eax
    2a6d:	c1 e1 06             	shl    $0x6,%ecx
    2a70:	c4 42 2a f5 d3       	pext   %r11d,%r10d,%r10d
    2a75:	c4 c2 62 f5 db       	pext   %r11d,%ebx,%ebx
    2a7a:	41 c1 e1 06          	shl    $0x6,%r9d
    2a7e:	09 de                	or     %ebx,%esi
    2a80:	44 09 d1             	or     %r10d,%ecx
    2a83:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    2a88:	45 89 c8             	mov    %r9d,%r8d
    2a8b:	44 8b 4c 24 b8       	mov    -0x48(%rsp),%r9d
    2a90:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    2a95:	41 09 f8             	or     %edi,%r8d
    2a98:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    2a9d:	43 0f b6 3c 07       	movzbl (%r15,%r8,1),%edi
    2aa2:	44 8b 44 24 b0       	mov    -0x50(%rsp),%r8d
    2aa7:	41 c1 e1 06          	shl    $0x6,%r9d
    2aab:	41 c1 e0 06          	shl    $0x6,%r8d
    2aaf:	44 0b 44 24 ac       	or     -0x54(%rsp),%r8d
    2ab4:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    2ab9:	44 0b 4c 24 b4       	or     -0x4c(%rsp),%r9d
    2abe:	44 8b 54 24 c0       	mov    -0x40(%rsp),%r10d
    2ac3:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    2ac8:	c4 c1 79 6e 04 be    	vmovd  (%r14,%rdi,4),%xmm0
    2ace:	c4 c1 79 6e 2c b6    	vmovd  (%r14,%rsi,4),%xmm5
    2ad4:	41 c1 e2 06          	shl    $0x6,%r10d
    2ad8:	c4 81 79 6e 0c 8e    	vmovd  (%r14,%r9,4),%xmm1
    2ade:	8b 74 24 e0          	mov    -0x20(%rsp),%esi
    2ae2:	44 0b 54 24 bc       	or     -0x44(%rsp),%r10d
    2ae7:	c4 83 79 22 04 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm0,%xmm0
    2aee:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    2af3:	c4 c3 51 22 2c 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm5,%xmm5
    2afa:	c1 e6 06             	shl    $0x6,%esi
    2afd:	8b 4c 24 d8          	mov    -0x28(%rsp),%ecx
    2b01:	8b 7c 24 e8          	mov    -0x18(%rsp),%edi
    2b05:	c4 83 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm1,%xmm1
    2b0c:	44 8b 54 24 d0       	mov    -0x30(%rsp),%r10d
    2b11:	44 8b 44 24 f0       	mov    -0x10(%rsp),%r8d
    2b16:	c1 e1 06             	shl    $0x6,%ecx
    2b19:	c1 e7 06             	shl    $0x6,%edi
    2b1c:	0b 74 24 dc          	or     -0x24(%rsp),%esi
    2b20:	c5 f9 6c c1          	vpunpcklqdq %xmm1,%xmm0,%xmm0
    2b24:	c4 c1 79 6e 0c 96    	vmovd  (%r14,%rdx,4),%xmm1
    2b2a:	41 c1 e2 06          	shl    $0x6,%r10d
    2b2e:	0b 4c 24 d4          	or     -0x2c(%rsp),%ecx
    2b32:	44 89 d2             	mov    %r10d,%edx
    2b35:	44 8b 54 24 f8       	mov    -0x8(%rsp),%r10d
    2b3a:	41 c1 e0 06          	shl    $0x6,%r8d
    2b3e:	0b 7c 24 e4          	or     -0x1c(%rsp),%edi
    2b42:	c4 c3 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%rax,4),%xmm1,%xmm1
    2b49:	8b 44 24 c8          	mov    -0x38(%rsp),%eax
    2b4d:	41 c1 e2 06          	shl    $0x6,%r10d
    2b51:	0b 54 24 cc          	or     -0x34(%rsp),%edx
    2b55:	44 0b 44 24 ec       	or     -0x14(%rsp),%r8d
    2b5a:	c1 e0 06             	shl    $0x6,%eax
    2b5d:	45 89 d1             	mov    %r10d,%r9d
    2b60:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    2b65:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    2b6a:	0b 44 24 c4          	or     -0x3c(%rsp),%eax
    2b6e:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    2b73:	c5 d1 6c e9          	vpunpcklqdq %xmm1,%xmm5,%xmm5
    2b77:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    2b7c:	41 0f b6 3c 3f       	movzbl (%r15,%rdi,1),%edi
    2b81:	c4 e3 55 38 e8 01    	vinserti128 $0x1,%xmm0,%ymm5,%ymm5
    2b87:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    2b8c:	44 0b 4c 24 f4       	or     -0xc(%rsp),%r9d
    2b91:	c4 e2 55 00 eb       	vpshufb %ymm3,%ymm5,%ymm5
    2b96:	47 0f b6 14 0f       	movzbl (%r15,%r9,1),%r10d
    2b9b:	44 8b 0c 24          	mov    (%rsp),%r9d
    2b9f:	c4 e2 5d 36 ed       	vpermd %ymm5,%ymm4,%ymm5
    2ba4:	c4 c1 79 6e 0c be    	vmovd  (%r14,%rdi,4),%xmm1
    2baa:	c4 c1 79 6e 04 86    	vmovd  (%r14,%rax,4),%xmm0
    2bb0:	41 c1 e1 06          	shl    $0x6,%r9d
    2bb4:	c4 81 79 6e 14 96    	vmovd  (%r14,%r10,4),%xmm2
    2bba:	8b 44 24 08          	mov    0x8(%rsp),%eax
    2bbe:	44 0b 4c 24 fc       	or     -0x4(%rsp),%r9d
    2bc3:	c4 83 71 22 0c 86 01 	vpinsrd $0x1,(%r14,%r8,4),%xmm1,%xmm1
    2bca:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    2bcf:	44 8b 44 24 28       	mov    0x28(%rsp),%r8d
    2bd4:	c1 e0 06             	shl    $0x6,%eax
    2bd7:	c4 c3 79 22 04 96 01 	vpinsrd $0x1,(%r14,%rdx,4),%xmm0,%xmm0
    2bde:	44 8b 54 24 38       	mov    0x38(%rsp),%r10d
    2be3:	c4 83 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%r9,4),%xmm2,%xmm2
    2bea:	44 8b 4c 24 10       	mov    0x10(%rsp),%r9d
    2bef:	41 c1 e0 06          	shl    $0x6,%r8d
    2bf3:	44 89 c7             	mov    %r8d,%edi
    2bf6:	41 c1 e2 06          	shl    $0x6,%r10d
    2bfa:	0b 44 24 04          	or     0x4(%rsp),%eax
    2bfe:	41 c1 e1 06          	shl    $0x6,%r9d
    2c02:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    2c06:	c4 c1 79 6e 14 8e    	vmovd  (%r14,%rcx,4),%xmm2
    2c0c:	0b 7c 24 24          	or     0x24(%rsp),%edi
    2c10:	44 89 ca             	mov    %r9d,%edx
    2c13:	44 8b 4c 24 30       	mov    0x30(%rsp),%r9d
    2c18:	8b 4c 24 18          	mov    0x18(%rsp),%ecx
    2c1c:	c4 c3 69 22 14 b6 01 	vpinsrd $0x1,(%r14,%rsi,4),%xmm2,%xmm2
    2c23:	8b 74 24 20          	mov    0x20(%rsp),%esi
    2c27:	41 c1 e1 06          	shl    $0x6,%r9d
    2c2b:	45 0f b6 04 3f       	movzbl (%r15,%rdi,1),%r8d
    2c30:	c1 e1 06             	shl    $0x6,%ecx
    2c33:	0b 54 24 0c          	or     0xc(%rsp),%edx
    2c37:	44 89 cf             	mov    %r9d,%edi
    2c3a:	c1 e6 06             	shl    $0x6,%esi
    2c3d:	0b 4c 24 14          	or     0x14(%rsp),%ecx
    2c41:	41 0f b6 04 07       	movzbl (%r15,%rax,1),%eax
    2c46:	0b 7c 24 2c          	or     0x2c(%rsp),%edi
    2c4a:	0b 74 24 1c          	or     0x1c(%rsp),%esi
    2c4e:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    2c52:	45 0f b6 0c 3f       	movzbl (%r15,%rdi,1),%r9d
    2c57:	44 89 d7             	mov    %r10d,%edi
    2c5a:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    2c5f:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    2c65:	41 0f b6 0c 0f       	movzbl (%r15,%rcx,1),%ecx
    2c6a:	41 0f b6 34 37       	movzbl (%r15,%rsi,1),%esi
    2c6f:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    2c74:	0b 7c 24 34          	or     0x34(%rsp),%edi
    2c78:	c4 81 79 6e 14 86    	vmovd  (%r14,%r8,4),%xmm2
    2c7e:	c4 e2 5d 36 c0       	vpermd %ymm0,%ymm4,%ymm0
    2c83:	45 0f b6 14 3f       	movzbl (%r15,%rdi,1),%r10d
    2c88:	8b 7c 24 40          	mov    0x40(%rsp),%edi
    2c8c:	c5 79 6f c0          	vmovdqa %xmm0,%xmm8
    2c90:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    2c96:	c4 83 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%r9,4),%xmm2,%xmm2
    2c9d:	c4 c1 79 6e 0c 86    	vmovd  (%r14,%rax,4),%xmm1
    2ca3:	c1 e7 06             	shl    $0x6,%edi
    2ca6:	c4 81 79 6e 34 96    	vmovd  (%r14,%r10,4),%xmm6
    2cac:	44 8b 44 24 60       	mov    0x60(%rsp),%r8d
    2cb1:	0b 7c 24 3c          	or     0x3c(%rsp),%edi
    2cb5:	c4 c3 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%rdx,4),%xmm1,%xmm1
    2cbc:	41 0f b6 3c 3f       	movzbl (%r15,%rdi,1),%edi
    2cc1:	41 c1 e0 06          	shl    $0x6,%r8d
    2cc5:	44 8b 54 24 70       	mov    0x70(%rsp),%r10d
    2cca:	44 8b 4c 24 7c       	mov    0x7c(%rsp),%r9d
    2ccf:	8b 44 24 48          	mov    0x48(%rsp),%eax
    2cd3:	c4 c3 49 22 34 be 01 	vpinsrd $0x1,(%r14,%rdi,4),%xmm6,%xmm6
    2cda:	8b 7c 24 50          	mov    0x50(%rsp),%edi
    2cde:	41 c1 e2 06          	shl    $0x6,%r10d
    2ce2:	41 c1 e1 06          	shl    $0x6,%r9d
    2ce6:	c1 e0 06             	shl    $0x6,%eax
    2ce9:	c5 e9 6c d6          	vpunpcklqdq %xmm6,%xmm2,%xmm2
    2ced:	c4 c1 79 6e 34 8e    	vmovd  (%r14,%rcx,4),%xmm6
    2cf3:	c1 e7 06             	shl    $0x6,%edi
    2cf6:	0b 44 24 44          	or     0x44(%rsp),%eax
    2cfa:	89 fa                	mov    %edi,%edx
    2cfc:	41 0f b6 1c 07       	movzbl (%r15,%rax,1),%ebx
    2d01:	c4 c3 49 22 34 b6 01 	vpinsrd $0x1,(%r14,%rsi,4),%xmm6,%xmm6
    2d08:	8b 74 24 58          	mov    0x58(%rsp),%esi
    2d0c:	0b 54 24 4c          	or     0x4c(%rsp),%edx
    2d10:	c1 e6 06             	shl    $0x6,%esi
    2d13:	41 0f b6 0c 17       	movzbl (%r15,%rdx,1),%ecx
    2d18:	c5 f1 6c ce          	vpunpcklqdq %xmm6,%xmm1,%xmm1
    2d1c:	89 f2                	mov    %esi,%edx
    2d1e:	c4 e3 75 38 ca 01    	vinserti128 $0x1,%xmm2,%ymm1,%ymm1
    2d24:	0b 54 24 54          	or     0x54(%rsp),%edx
    2d28:	c4 e2 75 00 cb       	vpshufb %ymm3,%ymm1,%ymm1
    2d2d:	41 0f b6 34 17       	movzbl (%r15,%rdx,1),%esi
    2d32:	44 89 c2             	mov    %r8d,%edx
    2d35:	c4 e2 5d 36 c9       	vpermd %ymm1,%ymm4,%ymm1
    2d3a:	0b 54 24 5c          	or     0x5c(%rsp),%edx
    2d3e:	c5 79 6f c9          	vmovdqa %xmm1,%xmm9
    2d42:	c4 e3 7d 39 c9 01    	vextracti128 $0x1,%ymm1,%xmm1
    2d48:	41 0f b6 3c 17       	movzbl (%r15,%rdx,1),%edi
    2d4d:	44 89 d2             	mov    %r10d,%edx
    2d50:	c4 c3 71 0f c9 08    	vpalignr $0x8,%xmm9,%xmm1,%xmm1
    2d56:	0b 54 24 68          	or     0x68(%rsp),%edx
    2d5a:	c4 c3 75 38 c8 01    	vinserti128 $0x1,%xmm8,%ymm1,%ymm1
    2d60:	45 0f b6 04 17       	movzbl (%r15,%rdx,1),%r8d
    2d65:	44 89 ca             	mov    %r9d,%edx
    2d68:	0b 54 24 78          	or     0x78(%rsp),%edx
    2d6c:	45 0f b6 0c 17       	movzbl (%r15,%rdx,1),%r9d
    2d71:	8b 94 24 84 00 00 00 	mov    0x84(%rsp),%edx
    2d78:	c1 e2 06             	shl    $0x6,%edx
    2d7b:	0b 94 24 80 00 00 00 	or     0x80(%rsp),%edx
    2d82:	c4 81 79 6e 34 86    	vmovd  (%r14,%r8,4),%xmm6
    2d88:	45 0f b6 14 17       	movzbl (%r15,%rdx,1),%r10d
    2d8d:	8b 94 24 8c 00 00 00 	mov    0x8c(%rsp),%edx
    2d94:	c4 83 49 22 34 8e 01 	vpinsrd $0x1,(%r14,%r9,4),%xmm6,%xmm6
    2d9b:	c4 c1 79 6e 14 9e    	vmovd  (%r14,%rbx,4),%xmm2
    2da1:	c1 e2 06             	shl    $0x6,%edx
    2da4:	c4 81 79 6e 3c 96    	vmovd  (%r14,%r10,4),%xmm7
    2daa:	48 8b 9c 24 98 00 00 	mov    0x98(%rsp),%rbx
    2db1:	00 
    2db2:	0b 94 24 88 00 00 00 	or     0x88(%rsp),%edx
    2db9:	c4 c3 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%rcx,4),%xmm2,%xmm2
    2dc0:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    2dc5:	48 8b 8c 24 90 00 00 	mov    0x90(%rsp),%rcx
    2dcc:	00 
    2dcd:	c4 c3 41 22 3c 96 01 	vpinsrd $0x1,(%r14,%rdx,4),%xmm7,%xmm7
    2dd4:	48 8d 41 48          	lea    0x48(%rcx),%rax
    2dd8:	48 83 c1 20          	add    $0x20,%rcx
    2ddc:	48 83 c3 60          	add    $0x60,%rbx
    2de0:	48 89 8c 24 90 00 00 	mov    %rcx,0x90(%rsp)
    2de7:	00 
    2de8:	49 83 c5 60          	add    $0x60,%r13
    2dec:	c5 c9 6c f7          	vpunpcklqdq %xmm7,%xmm6,%xmm6
    2df0:	c4 c1 79 6e 3c b6    	vmovd  (%r14,%rsi,4),%xmm7
    2df6:	c4 c3 41 22 3c be 01 	vpinsrd $0x1,(%r14,%rdi,4),%xmm7,%xmm7
    2dfd:	c5 fe 7f 4b c0       	vmovdqu %ymm1,-0x40(%rbx)
    2e02:	c5 e9 6c d7          	vpunpcklqdq %xmm7,%xmm2,%xmm2
    2e06:	c5 f9 6f fd          	vmovdqa %xmm5,%xmm7
    2e0a:	c4 e3 7d 39 ed 01    	vextracti128 $0x1,%ymm5,%xmm5
    2e10:	c4 e3 6d 38 d6 01    	vinserti128 $0x1,%xmm6,%ymm2,%ymm2
    2e16:	c4 e3 51 0f ef 08    	vpalignr $0x8,%xmm7,%xmm5,%xmm5
    2e1c:	c5 f9 6c c7          	vpunpcklqdq %xmm7,%xmm0,%xmm0
    2e20:	c4 e2 6d 00 d3       	vpshufb %ymm3,%ymm2,%ymm2
    2e25:	c4 e3 7d 38 c5 01    	vinserti128 $0x1,%xmm5,%ymm0,%ymm0
    2e2b:	c4 e2 5d 36 d2       	vpermd %ymm2,%ymm4,%ymm2
    2e30:	c5 fe 7f 43 e0       	vmovdqu %ymm0,-0x20(%rbx)
    2e35:	c5 f9 6f f2          	vmovdqa %xmm2,%xmm6
    2e39:	c4 e3 7d 39 d2 01    	vextracti128 $0x1,%ymm2,%xmm2
    2e3f:	c4 c1 69 6c d1       	vpunpcklqdq %xmm9,%xmm2,%xmm2
    2e44:	c4 e3 4d 38 d2 01    	vinserti128 $0x1,%xmm2,%ymm6,%ymm2
    2e4a:	c5 fe 7f 53 a0       	vmovdqu %ymm2,-0x60(%rbx)
    2e4f:	48 89 9c 24 98 00 00 	mov    %rbx,0x98(%rsp)
    2e56:	00 
    2e57:	48 39 84 24 a0 00 00 	cmp    %rax,0xa0(%rsp)
    2e5e:	00 
    2e5f:	0f 83 43 f9 ff ff    	jae    27a8 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xec8>
    2e65:	48 8b 44 24 a0       	mov    -0x60(%rsp),%rax
    2e6a:	48 8b 4c 24 98       	mov    -0x68(%rsp),%rcx
    2e6f:	48 8b b4 24 90 00 00 	mov    0x90(%rsp),%rsi
    2e76:	00 
    2e77:	48 8d 5e 08          	lea    0x8(%rsi),%rbx
    2e7b:	48 89 9c 24 98 00 00 	mov    %rbx,0x98(%rsp)
    2e82:	00 
    2e83:	48 39 9c 24 a0 00 00 	cmp    %rbx,0xa0(%rsp)
    2e8a:	00 
    2e8b:	0f 82 6e 02 00 00    	jb     30ff <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x181f>
    2e91:	48 8d 14 76          	lea    (%rsi,%rsi,2),%rdx
    2e95:	48 89 44 24 70       	mov    %rax,0x70(%rsp)
    2e9a:	c5 fd 6f 1d 00 00 00 	vmovdqa 0x0(%rip),%ymm3        # 2ea2 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x15c2>
    2ea1:	00 
    2ea2:	48 8d 1c 11          	lea    (%rcx,%rdx,1),%rbx
    2ea6:	48 89 4c 24 68       	mov    %rcx,0x68(%rsp)
    2eab:	4c 8d 24 10          	lea    (%rax,%rdx,1),%r12
    2eaf:	48 89 9c 24 90 00 00 	mov    %rbx,0x90(%rsp)
    2eb6:	00 
    2eb7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    2ebe:	00 00 
    2ec0:	49 8b 44 24 10       	mov    0x10(%r12),%rax
    2ec5:	49 8b 4c 24 08       	mov    0x8(%r12),%rcx
    2eca:	bf fc fc fc 00       	mov    $0xfcfcfc,%edi
    2ecf:	41 bb 03 03 03 00    	mov    $0x30303,%r11d
    2ed5:	49 8b 1c 24          	mov    (%r12),%rbx
    2ed9:	48 89 c2             	mov    %rax,%rdx
    2edc:	48 c1 ea 28          	shr    $0x28,%rdx
    2ee0:	c4 e2 6a f5 f7       	pext   %edi,%edx,%esi
    2ee5:	c4 c2 6a f5 d3       	pext   %r11d,%edx,%edx
    2eea:	89 b4 24 8c 00 00 00 	mov    %esi,0x8c(%rsp)
    2ef1:	48 89 ce             	mov    %rcx,%rsi
    2ef4:	89 94 24 88 00 00 00 	mov    %edx,0x88(%rsp)
    2efb:	48 89 c2             	mov    %rax,%rdx
    2efe:	48 c1 ee 38          	shr    $0x38,%rsi
    2f02:	48 c1 ea 10          	shr    $0x10,%rdx
    2f06:	c1 e0 08             	shl    $0x8,%eax
    2f09:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    2f0f:	09 f0                	or     %esi,%eax
    2f11:	48 89 ce             	mov    %rcx,%rsi
    2f14:	c4 62 6a f5 cf       	pext   %edi,%edx,%r9d
    2f19:	c4 42 6a f5 eb       	pext   %r11d,%edx,%r13d
    2f1e:	48 c1 ee 20          	shr    $0x20,%rsi
    2f22:	44 89 ac 24 80 00 00 	mov    %r13d,0x80(%rsp)
    2f29:	00 
    2f2a:	89 c2                	mov    %eax,%edx
    2f2c:	41 89 cd             	mov    %ecx,%r13d
    2f2f:	81 e6 ff ff ff 00    	and    $0xffffff,%esi
    2f35:	44 89 8c 24 84 00 00 	mov    %r9d,0x84(%rsp)
    2f3c:	00 
    2f3d:	41 c1 ed 08          	shr    $0x8,%r13d
    2f41:	81 e2 ff ff ff 00    	and    $0xffffff,%edx
    2f47:	c1 e1 10             	shl    $0x10,%ecx
    2f4a:	c4 62 4a f5 c7       	pext   %edi,%esi,%r8d
    2f4f:	c4 e2 6a f5 c7       	pext   %edi,%edx,%eax
    2f54:	c4 c2 4a f5 f3       	pext   %r11d,%esi,%esi
    2f59:	89 44 24 7c          	mov    %eax,0x7c(%rsp)
    2f5d:	c4 62 12 f5 cf       	pext   %edi,%r13d,%r9d
    2f62:	c4 c2 6a f5 c3       	pext   %r11d,%edx,%eax
    2f67:	89 44 24 78          	mov    %eax,0x78(%rsp)
    2f6b:	44 89 d8             	mov    %r11d,%eax
    2f6e:	41 89 fb             	mov    %edi,%r11d
    2f71:	c4 62 12 f5 e8       	pext   %eax,%r13d,%r13d
    2f76:	41 c1 e0 06          	shl    $0x6,%r8d
    2f7a:	48 89 df             	mov    %rbx,%rdi
    2f7d:	89 ca                	mov    %ecx,%edx
    2f7f:	48 c1 ef 30          	shr    $0x30,%rdi
    2f83:	b9 03 03 03 00       	mov    $0x30303,%ecx
    2f88:	41 09 f0             	or     %esi,%r8d
    2f8b:	41 c1 e1 06          	shl    $0x6,%r9d
    2f8f:	09 fa                	or     %edi,%edx
    2f91:	48 89 df             	mov    %rbx,%rdi
    2f94:	43 0f b6 34 07       	movzbl (%r15,%r8,1),%esi
    2f99:	45 09 e9             	or     %r13d,%r9d
    2f9c:	89 d0                	mov    %edx,%eax
    2f9e:	48 c1 ef 18          	shr    $0x18,%rdi
    2fa2:	89 ca                	mov    %ecx,%edx
    2fa4:	47 0f b6 0c 0f       	movzbl (%r15,%r9,1),%r9d
    2fa9:	25 ff ff ff 00       	and    $0xffffff,%eax
    2fae:	81 e7 ff ff ff 00    	and    $0xffffff,%edi
    2fb4:	c4 c1 79 6e 0c b6    	vmovd  (%r14,%rsi,4),%xmm1
    2fba:	c4 42 7a f5 d3       	pext   %r11d,%eax,%r10d
    2fbf:	c4 e2 7a f5 c1       	pext   %ecx,%eax,%eax
    2fc4:	c4 42 42 f5 db       	pext   %r11d,%edi,%r11d
    2fc9:	c4 e2 42 f5 f9       	pext   %ecx,%edi,%edi
    2fce:	41 c1 e2 06          	shl    $0x6,%r10d
    2fd2:	89 d9                	mov    %ebx,%ecx
    2fd4:	bb fc fc fc 00       	mov    $0xfcfcfc,%ebx
    2fd9:	41 c1 e3 06          	shl    $0x6,%r11d
    2fdd:	81 e1 ff ff ff 00    	and    $0xffffff,%ecx
    2fe3:	41 09 c2             	or     %eax,%r10d
    2fe6:	41 09 fb             	or     %edi,%r11d
    2fe9:	c4 e2 72 f5 db       	pext   %ebx,%ecx,%ebx
    2fee:	c1 e3 06             	shl    $0x6,%ebx
    2ff1:	c4 e2 72 f5 ca       	pext   %edx,%ecx,%ecx
    2ff6:	43 0f b6 04 17       	movzbl (%r15,%r10,1),%eax
    2ffb:	09 cb                	or     %ecx,%ebx
    2ffd:	44 8b 94 24 8c 00 00 	mov    0x8c(%rsp),%r10d
    3004:	00 
    3005:	43 0f b6 3c 1f       	movzbl (%r15,%r11,1),%edi
    300a:	41 0f b6 0c 1f       	movzbl (%r15,%rbx,1),%ecx
    300f:	8b 5c 24 7c          	mov    0x7c(%rsp),%ebx
    3013:	41 c1 e2 06          	shl    $0x6,%r10d
    3017:	c1 e3 06             	shl    $0x6,%ebx
    301a:	c4 c1 79 6e 04 8e    	vmovd  (%r14,%rcx,4),%xmm0
    3020:	41 89 d8             	mov    %ebx,%r8d
    3023:	48 8b 9c 24 90 00 00 	mov    0x90(%rsp),%rbx
    302a:	00 
    302b:	44 0b 44 24 78       	or     0x78(%rsp),%r8d
    3030:	c4 c3 79 22 04 be 01 	vpinsrd $0x1,(%r14,%rdi,4),%xmm0,%xmm0
    3037:	43 0f b6 14 07       	movzbl (%r15,%r8,1),%edx
    303c:	44 8b 84 24 84 00 00 	mov    0x84(%rsp),%r8d
    3043:	00 
    3044:	41 c1 e0 06          	shl    $0x6,%r8d
    3048:	c4 c3 71 22 0c 96 01 	vpinsrd $0x1,(%r14,%rdx,4),%xmm1,%xmm1
    304f:	44 0b 84 24 80 00 00 	or     0x80(%rsp),%r8d
    3056:	00 
    3057:	44 0b 94 24 88 00 00 	or     0x88(%rsp),%r10d
    305e:	00 
    305f:	48 83 c3 18          	add    $0x18,%rbx
    3063:	49 83 c4 18          	add    $0x18,%r12
    3067:	47 0f b6 04 07       	movzbl (%r15,%r8,1),%r8d
    306c:	47 0f b6 14 17       	movzbl (%r15,%r10,1),%r10d
    3071:	c4 81 79 6e 14 86    	vmovd  (%r14,%r8,4),%xmm2
    3077:	c4 83 69 22 14 96 01 	vpinsrd $0x1,(%r14,%r10,4),%xmm2,%xmm2
    307e:	c5 f1 6c ca          	vpunpcklqdq %xmm2,%xmm1,%xmm1
    3082:	c4 c1 79 6e 14 86    	vmovd  (%r14,%rax,4),%xmm2
    3088:	c4 83 69 22 14 8e 01 	vpinsrd $0x1,(%r14,%r9,4),%xmm2,%xmm2
    308f:	c5 f9 6c c2          	vpunpcklqdq %xmm2,%xmm0,%xmm0
    3093:	c4 e3 7d 38 c1 01    	vinserti128 $0x1,%xmm1,%ymm0,%ymm0
    3099:	c4 e2 7d 00 c3       	vpshufb %ymm3,%ymm0,%ymm0
    309e:	c5 f9 6f d0          	vmovdqa %xmm0,%xmm2
    30a2:	c4 e3 7d 39 c0 01    	vextracti128 $0x1,%ymm0,%xmm0
    30a8:	c5 f1 73 f8 0c       	vpslldq $0xc,%xmm0,%xmm1
    30ad:	c5 f9 73 d8 04       	vpsrldq $0x4,%xmm0,%xmm0
    30b2:	c5 f1 eb ca          	vpor   %xmm2,%xmm1,%xmm1
    30b6:	c5 fa 7f 4b e8       	vmovdqu %xmm1,-0x18(%rbx)
    30bb:	48 8b b4 24 98 00 00 	mov    0x98(%rsp),%rsi
    30c2:	00 
    30c3:	c5 f9 d6 43 f8       	vmovq  %xmm0,-0x8(%rbx)
    30c8:	48 89 f0             	mov    %rsi,%rax
    30cb:	48 83 c6 08          	add    $0x8,%rsi
    30cf:	48 89 9c 24 90 00 00 	mov    %rbx,0x90(%rsp)
    30d6:	00 
    30d7:	48 89 b4 24 98 00 00 	mov    %rsi,0x98(%rsp)
    30de:	00 
    30df:	48 39 b4 24 a0 00 00 	cmp    %rsi,0xa0(%rsp)
    30e6:	00 
    30e7:	0f 83 d3 fd ff ff    	jae    2ec0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x15e0>
    30ed:	48 89 84 24 90 00 00 	mov    %rax,0x90(%rsp)
    30f4:	00 
    30f5:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
    30fa:	48 8b 44 24 70       	mov    0x70(%rsp),%rax
    30ff:	48 8b 9c 24 90 00 00 	mov    0x90(%rsp),%rbx
    3106:	00 
    3107:	4c 8b a4 24 a0 00 00 	mov    0xa0(%rsp),%r12
    310e:	00 
    310f:	4c 39 e3             	cmp    %r12,%rbx
    3112:	0f 83 88 02 00 00    	jae    33a0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac0>
    3118:	48 8d 34 5b          	lea    (%rbx,%rbx,2),%rsi
    311c:	48 8d 3c 30          	lea    (%rax,%rsi,1),%rdi
    3120:	0f b6 57 01          	movzbl 0x1(%rdi),%edx
    3124:	44 0f b6 4f 02       	movzbl 0x2(%rdi),%r9d
    3129:	0f b6 3f             	movzbl (%rdi),%edi
    312c:	41 c1 e1 10          	shl    $0x10,%r9d
    3130:	c1 e2 08             	shl    $0x8,%edx
    3133:	44 09 ca             	or     %r9d,%edx
    3136:	41 b9 03 03 03 00    	mov    $0x30303,%r9d
    313c:	09 fa                	or     %edi,%edx
    313e:	bf fc fc fc 00       	mov    $0xfcfcfc,%edi
    3143:	c4 62 6a f5 d7       	pext   %edi,%edx,%r10d
    3148:	41 c1 e2 06          	shl    $0x6,%r10d
    314c:	c4 c2 6a f5 d1       	pext   %r9d,%edx,%edx
    3151:	44 09 d2             	or     %r10d,%edx
    3154:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    3159:	4d 8d 14 96          	lea    (%r14,%rdx,4),%r10
    315d:	41 8b 12             	mov    (%r10),%edx
    3160:	45 0f b7 12          	movzwl (%r10),%r10d
    3164:	c1 ea 10             	shr    $0x10,%edx
    3167:	66 44 89 14 31       	mov    %r10w,(%rcx,%rsi,1)
    316c:	88 54 31 02          	mov    %dl,0x2(%rcx,%rsi,1)
    3170:	48 8d 53 01          	lea    0x1(%rbx),%rdx
    3174:	4c 39 e2             	cmp    %r12,%rdx
    3177:	0f 83 23 02 00 00    	jae    33a0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac0>
    317d:	4c 8d 54 30 03       	lea    0x3(%rax,%rsi,1),%r10
    3182:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    3187:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    318c:	45 0f b6 12          	movzbl (%r10),%r10d
    3190:	c1 e2 08             	shl    $0x8,%edx
    3193:	41 c1 e3 10          	shl    $0x10,%r11d
    3197:	44 09 da             	or     %r11d,%edx
    319a:	44 09 d2             	or     %r10d,%edx
    319d:	c4 62 6a f5 d7       	pext   %edi,%edx,%r10d
    31a2:	41 c1 e2 06          	shl    $0x6,%r10d
    31a6:	c4 c2 6a f5 d1       	pext   %r9d,%edx,%edx
    31ab:	44 09 d2             	or     %r10d,%edx
    31ae:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    31b3:	4d 8d 14 96          	lea    (%r14,%rdx,4),%r10
    31b7:	41 8b 12             	mov    (%r10),%edx
    31ba:	45 0f b7 12          	movzwl (%r10),%r10d
    31be:	c1 ea 10             	shr    $0x10,%edx
    31c1:	66 44 89 54 31 03    	mov    %r10w,0x3(%rcx,%rsi,1)
    31c7:	88 54 31 05          	mov    %dl,0x5(%rcx,%rsi,1)
    31cb:	48 8d 53 02          	lea    0x2(%rbx),%rdx
    31cf:	4c 39 e2             	cmp    %r12,%rdx
    31d2:	0f 83 c8 01 00 00    	jae    33a0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac0>
    31d8:	4c 8d 54 30 06       	lea    0x6(%rax,%rsi,1),%r10
    31dd:	41 0f b6 52 01       	movzbl 0x1(%r10),%edx
    31e2:	45 0f b6 5a 02       	movzbl 0x2(%r10),%r11d
    31e7:	45 0f b6 12          	movzbl (%r10),%r10d
    31eb:	c1 e2 08             	shl    $0x8,%edx
    31ee:	41 c1 e3 10          	shl    $0x10,%r11d
    31f2:	44 09 da             	or     %r11d,%edx
    31f5:	44 09 d2             	or     %r10d,%edx
    31f8:	c4 62 6a f5 d7       	pext   %edi,%edx,%r10d
    31fd:	41 c1 e2 06          	shl    $0x6,%r10d
    3201:	c4 c2 6a f5 d1       	pext   %r9d,%edx,%edx
    3206:	44 09 d2             	or     %r10d,%edx
    3209:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    320e:	4d 8d 14 96          	lea    (%r14,%rdx,4),%r10
    3212:	41 8b 12             	mov    (%r10),%edx
    3215:	45 0f b7 12          	movzwl (%r10),%r10d
    3219:	c1 ea 10             	shr    $0x10,%edx
    321c:	66 44 89 54 31 06    	mov    %r10w,0x6(%rcx,%rsi,1)
    3222:	88 54 31 08          	mov    %dl,0x8(%rcx,%rsi,1)
    3226:	48 8d 53 03          	lea    0x3(%rbx),%rdx
    322a:	4c 39 e2             	cmp    %r12,%rdx
    322d:	0f 83 6d 01 00 00    	jae    33a0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac0>
    3233:	4c 8d 54 30 09       	lea    0x9(%rax,%rsi,1),%r10
    3238:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    323d:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    3242:	45 0f b6 12          	movzbl (%r10),%r10d
    3246:	c1 e2 10             	shl    $0x10,%edx
    3249:	41 c1 e3 08          	shl    $0x8,%r11d
    324d:	44 09 da             	or     %r11d,%edx
    3250:	44 09 d2             	or     %r10d,%edx
    3253:	c4 62 6a f5 d7       	pext   %edi,%edx,%r10d
    3258:	41 c1 e2 06          	shl    $0x6,%r10d
    325c:	c4 c2 6a f5 d1       	pext   %r9d,%edx,%edx
    3261:	44 09 d2             	or     %r10d,%edx
    3264:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    3269:	4d 8d 14 96          	lea    (%r14,%rdx,4),%r10
    326d:	41 8b 12             	mov    (%r10),%edx
    3270:	45 0f b7 12          	movzwl (%r10),%r10d
    3274:	c1 ea 10             	shr    $0x10,%edx
    3277:	66 44 89 54 31 09    	mov    %r10w,0x9(%rcx,%rsi,1)
    327d:	88 54 31 0b          	mov    %dl,0xb(%rcx,%rsi,1)
    3281:	48 8d 53 04          	lea    0x4(%rbx),%rdx
    3285:	4c 39 e2             	cmp    %r12,%rdx
    3288:	0f 83 12 01 00 00    	jae    33a0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac0>
    328e:	4c 8d 54 30 0c       	lea    0xc(%rax,%rsi,1),%r10
    3293:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    3298:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    329d:	45 0f b6 12          	movzbl (%r10),%r10d
    32a1:	c1 e2 10             	shl    $0x10,%edx
    32a4:	41 c1 e3 08          	shl    $0x8,%r11d
    32a8:	44 09 da             	or     %r11d,%edx
    32ab:	44 09 d2             	or     %r10d,%edx
    32ae:	c4 62 6a f5 d7       	pext   %edi,%edx,%r10d
    32b3:	41 c1 e2 06          	shl    $0x6,%r10d
    32b7:	c4 c2 6a f5 d1       	pext   %r9d,%edx,%edx
    32bc:	44 09 d2             	or     %r10d,%edx
    32bf:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    32c4:	4d 8d 14 96          	lea    (%r14,%rdx,4),%r10
    32c8:	41 8b 12             	mov    (%r10),%edx
    32cb:	45 0f b7 12          	movzwl (%r10),%r10d
    32cf:	c1 ea 10             	shr    $0x10,%edx
    32d2:	66 44 89 54 31 0c    	mov    %r10w,0xc(%rcx,%rsi,1)
    32d8:	88 54 31 0e          	mov    %dl,0xe(%rcx,%rsi,1)
    32dc:	48 8d 53 05          	lea    0x5(%rbx),%rdx
    32e0:	4c 39 e2             	cmp    %r12,%rdx
    32e3:	0f 83 b7 00 00 00    	jae    33a0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac0>
    32e9:	4c 8d 54 30 0f       	lea    0xf(%rax,%rsi,1),%r10
    32ee:	41 0f b6 52 02       	movzbl 0x2(%r10),%edx
    32f3:	45 0f b6 5a 01       	movzbl 0x1(%r10),%r11d
    32f8:	45 0f b6 12          	movzbl (%r10),%r10d
    32fc:	c1 e2 10             	shl    $0x10,%edx
    32ff:	41 c1 e3 08          	shl    $0x8,%r11d
    3303:	44 09 da             	or     %r11d,%edx
    3306:	44 09 d2             	or     %r10d,%edx
    3309:	c4 62 6a f5 d7       	pext   %edi,%edx,%r10d
    330e:	41 c1 e2 06          	shl    $0x6,%r10d
    3312:	c4 c2 6a f5 d1       	pext   %r9d,%edx,%edx
    3317:	44 09 d2             	or     %r10d,%edx
    331a:	41 0f b6 14 17       	movzbl (%r15,%rdx,1),%edx
    331f:	4d 8d 14 96          	lea    (%r14,%rdx,4),%r10
    3323:	41 8b 12             	mov    (%r10),%edx
    3326:	45 0f b7 12          	movzwl (%r10),%r10d
    332a:	c1 ea 10             	shr    $0x10,%edx
    332d:	66 44 89 54 31 0f    	mov    %r10w,0xf(%rcx,%rsi,1)
    3333:	88 54 31 11          	mov    %dl,0x11(%rcx,%rsi,1)
    3337:	48 8d 53 06          	lea    0x6(%rbx),%rdx
    333b:	4c 39 e2             	cmp    %r12,%rdx
    333e:	73 60                	jae    33a0 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x1ac0>
    3340:	48 8d 54 31 12       	lea    0x12(%rcx,%rsi,1),%rdx
    3345:	48 8d 4c 30 12       	lea    0x12(%rax,%rsi,1),%rcx
    334a:	0f b6 41 01          	movzbl 0x1(%rcx),%eax
    334e:	0f b6 71 02          	movzbl 0x2(%rcx),%esi
    3352:	0f b6 09             	movzbl (%rcx),%ecx
    3355:	c1 e0 08             	shl    $0x8,%eax
    3358:	c1 e6 10             	shl    $0x10,%esi
    335b:	09 f0                	or     %esi,%eax
    335d:	09 c8                	or     %ecx,%eax
    335f:	c4 e2 7a f5 ff       	pext   %edi,%eax,%edi
    3364:	c1 e7 06             	shl    $0x6,%edi
    3367:	c4 c2 7a f5 c1       	pext   %r9d,%eax,%eax
    336c:	09 c7                	or     %eax,%edi
    336e:	41 0f b6 04 3f       	movzbl (%r15,%rdi,1),%eax
    3373:	49 8d 0c 86          	lea    (%r14,%rax,4),%rcx
    3377:	8b 01                	mov    (%rcx),%eax
    3379:	0f b7 09             	movzwl (%rcx),%ecx
    337c:	c1 e8 10             	shr    $0x10,%eax
    337f:	66 89 0a             	mov    %cx,(%rdx)
    3382:	88 42 02             	mov    %al,0x2(%rdx)
    3385:	c5 f8 77             	vzeroupper
    3388:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    338c:	5b                   	pop    %rbx
    338d:	41 5c                	pop    %r12
    338f:	41 5d                	pop    %r13
    3391:	41 5e                	pop    %r14
    3393:	41 5f                	pop    %r15
    3395:	5d                   	pop    %rbp
    3396:	c3                   	ret
    3397:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
    339e:	00 00 
    33a0:	c5 f8 77             	vzeroupper
    33a3:	48 8d 65 d8          	lea    -0x28(%rbp),%rsp
    33a7:	5b                   	pop    %rbx
    33a8:	41 5c                	pop    %r12
    33aa:	41 5d                	pop    %r13
    33ac:	41 5e                	pop    %r14
    33ae:	41 5f                	pop    %r15
    33b0:	5d                   	pop    %rbp
    33b1:	c3                   	ret
    33b2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
    33b8:	48 8b 9c 24 a0 00 00 	mov    0xa0(%rsp),%rbx
    33bf:	00 
    33c0:	48 89 9c 24 90 00 00 	mov    %rbx,0x90(%rsp)
    33c7:	00 
    33c8:	e9 a2 fa ff ff       	jmp    2e6f <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0x158f>
    33cd:	4c 89 94 24 90 00 00 	mov    %r10,0x90(%rsp)
    33d4:	00 
    33d5:	49 8d 52 28          	lea    0x28(%r10),%rdx
    33d9:	e9 77 f3 ff ff       	jmp    2755 <jshc_channel::avx2_chain_tilebmi2_to(unsigned int const*, unsigned int const*, unsigned char const*, unsigned char*, unsigned long)+0xe75>
