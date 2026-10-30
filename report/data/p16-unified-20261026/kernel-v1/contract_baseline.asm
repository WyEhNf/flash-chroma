
artifacts/p16-unified-avx512-kernel/direct_avx512_contract.o:     file format pe-x86-64


Disassembly of section .text:

0000000000000000 <_ZN12_GLOBAL__N_17GuardedC1Ey>:
       0:	55                   	push   rbp
       1:	57                   	push   rdi
       2:	56                   	push   rsi
       3:	53                   	push   rbx
       4:	48 83 ec 68          	sub    rsp,0x68
       8:	31 c0                	xor    eax,eax
       a:	66 48 0f 6e c2       	movq   xmm0,rdx
       f:	48 89 ce             	mov    rsi,rcx
      12:	48 89 d5             	mov    rbp,rdx
      15:	0f 11 01             	movups XMMWORD PTR [rcx],xmm0
      18:	48 8d 7c 24 30       	lea    rdi,[rsp+0x30]
      1d:	66 0f ef c0          	pxor   xmm0,xmm0
      21:	0f 11 41 10          	movups XMMWORD PTR [rcx+0x10],xmm0
      25:	b9 06 00 00 00       	mov    ecx,0x6
      2a:	f3 48 ab             	rep stos QWORD PTR [rdi],rax
      2d:	48 8d 4c 24 30       	lea    rcx,[rsp+0x30]
      32:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 38 <_ZN12_GLOBAL__N_17GuardedC1Ey+0x38>
      38:	8b 5c 24 34          	mov    ebx,DWORD PTR [rsp+0x34]
      3c:	31 d2                	xor    edx,edx
      3e:	31 c9                	xor    ecx,ecx
      40:	41 b9 01 00 00 00    	mov    r9d,0x1
      46:	41 b8 00 30 00 00    	mov    r8d,0x3000
      4c:	48 8d 7c 2b 3f       	lea    rdi,[rbx+rbp*1+0x3f]
      51:	48 89 f8             	mov    rax,rdi
      54:	48 f7 f3             	div    rbx
      57:	48 29 d7             	sub    rdi,rdx
      5a:	48 8d 14 5f          	lea    rdx,[rdi+rbx*2]
      5e:	48 89 56 08          	mov    QWORD PTR [rsi+0x8],rdx
      62:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 68 <_ZN12_GLOBAL__N_17GuardedC1Ey+0x68>
      68:	c7 44 24 2c 00 00 00 	mov    DWORD PTR [rsp+0x2c],0x0
      6f:	00 
      70:	48 85 c0             	test   rax,rax
      73:	48 89 46 10          	mov    QWORD PTR [rsi+0x10],rax
      77:	74 5e                	je     d7 <_ZN12_GLOBAL__N_17GuardedC1Ey+0xd7>
      79:	48 8d 0c 18          	lea    rcx,[rax+rbx*1]
      7d:	41 b8 04 00 00 00    	mov    r8d,0x4
      83:	48 89 fa             	mov    rdx,rdi
      86:	4c 8d 4c 24 2c       	lea    r9,[rsp+0x2c]
      8b:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 91 <_ZN12_GLOBAL__N_17GuardedC1Ey+0x91>
      91:	85 c0                	test   eax,eax
      93:	74 42                	je     d7 <_ZN12_GLOBAL__N_17GuardedC1Ey+0xd7>
      95:	48 ba a5 a5 a5 a5 a5 	movabs rdx,0xa5a5a5a5a5a5a5a5
      9c:	a5 a5 a5 
      9f:	48 29 eb             	sub    rbx,rbp
      a2:	48 8d 04 3b          	lea    rax,[rbx+rdi*1]
      a6:	48 03 46 10          	add    rax,QWORD PTR [rsi+0x10]
      aa:	48 89 46 18          	mov    QWORD PTR [rsi+0x18],rax
      ae:	48 89 50 c0          	mov    QWORD PTR [rax-0x40],rdx
      b2:	48 89 50 c8          	mov    QWORD PTR [rax-0x38],rdx
      b6:	48 89 50 d0          	mov    QWORD PTR [rax-0x30],rdx
      ba:	48 89 50 d8          	mov    QWORD PTR [rax-0x28],rdx
      be:	48 89 50 e0          	mov    QWORD PTR [rax-0x20],rdx
      c2:	48 89 50 e8          	mov    QWORD PTR [rax-0x18],rdx
      c6:	48 89 50 f0          	mov    QWORD PTR [rax-0x10],rdx
      ca:	48 89 50 f8          	mov    QWORD PTR [rax-0x8],rdx
      ce:	48 83 c4 68          	add    rsp,0x68
      d2:	5b                   	pop    rbx
      d3:	5e                   	pop    rsi
      d4:	5f                   	pop    rdi
      d5:	5d                   	pop    rbp
      d6:	c3                   	ret
      d7:	b9 10 00 00 00       	mov    ecx,0x10
      dc:	e8 00 00 00 00       	call   e1 <_ZN12_GLOBAL__N_17GuardedC1Ey+0xe1>
      e1:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # e8 <_ZN12_GLOBAL__N_17GuardedC1Ey+0xe8>
      e8:	48 89 c1             	mov    rcx,rax
      eb:	48 89 c3             	mov    rbx,rax
      ee:	e8 00 00 00 00       	call   f3 <_ZN12_GLOBAL__N_17GuardedC1Ey+0xf3>
      f3:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # fa <_ZN12_GLOBAL__N_17GuardedC1Ey+0xfa>
      fa:	48 89 d9             	mov    rcx,rbx
      fd:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # 104 <_ZN12_GLOBAL__N_17GuardedC1Ey+0x104>
     104:	e8 00 00 00 00       	call   109 <_ZN12_GLOBAL__N_17GuardedC1Ey+0x109>
     109:	48 89 c6             	mov    rsi,rax
     10c:	48 89 d9             	mov    rcx,rbx
     10f:	e8 00 00 00 00       	call   114 <_ZN12_GLOBAL__N_17GuardedC1Ey+0x114>
     114:	48 89 f1             	mov    rcx,rsi
     117:	e8 00 00 00 00       	call   11c <_ZN12_GLOBAL__N_17GuardedC1Ey+0x11c>
     11c:	90                   	nop
     11d:	90                   	nop
     11e:	66 90                	xchg   ax,ax

0000000000000120 <_ZNSt12_Vector_baseIjSaIjEED2Ev.isra.0>:
     120:	48 85 c9             	test   rcx,rcx
     123:	74 08                	je     12d <_ZNSt12_Vector_baseIjSaIjEED2Ev.isra.0+0xd>
     125:	48 29 ca             	sub    rdx,rcx
     128:	e9 00 00 00 00       	jmp    12d <_ZNSt12_Vector_baseIjSaIjEED2Ev.isra.0+0xd>
     12d:	c3                   	ret
     12e:	66 90                	xchg   ax,ax

0000000000000130 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0>:
     130:	56                   	push   rsi
     131:	53                   	push   rbx
     132:	48 83 ec 28          	sub    rsp,0x28
     136:	4d 29 c1             	sub    r9,r8
     139:	41 89 cb             	mov    r11d,ecx
     13c:	74 65                	je     1a3 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x73>
     13e:	4c 89 cb             	mov    rbx,r9
     141:	49 89 d2             	mov    r10,rdx
     144:	45 31 c9             	xor    r9d,r9d
     147:	48 c1 fb 02          	sar    rbx,0x2
     14b:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
     150:	41 83 fb 08          	cmp    r11d,0x8
     154:	43 8b 04 88          	mov    eax,DWORD PTR [r8+r9*4]
     158:	74 56                	je     1b0 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x80>
     15a:	41 83 fb 10          	cmp    r11d,0x10
     15e:	0f 84 8c 00 00 00    	je     1f0 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0xc0>
     164:	69 d0 f5 9c 8e 6c    	imul   edx,eax,0x6c8e9cf5
     16a:	c1 e8 05             	shr    eax,0x5
     16d:	31 c2                	xor    edx,eax
     16f:	81 f2 9b 48 12 00    	xor    edx,0x12489b
     175:	31 c0                	xor    eax,eax
     177:	8d 0c c5 00 00 00 00 	lea    ecx,[rax*8+0x0]
     17e:	89 d6                	mov    esi,edx
     180:	d3 ee                	shr    esi,cl
     182:	41 38 34 02          	cmp    BYTE PTR [r10+rax*1],sil
     186:	0f 85 96 00 00 00    	jne    222 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0xf2>
     18c:	48 83 c0 01          	add    rax,0x1
     190:	48 83 f8 03          	cmp    rax,0x3
     194:	75 e1                	jne    177 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x47>
     196:	49 83 c1 01          	add    r9,0x1
     19a:	49 83 c2 03          	add    r10,0x3
     19e:	49 39 d9             	cmp    r9,rbx
     1a1:	72 ad                	jb     150 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x20>
     1a3:	48 83 c4 28          	add    rsp,0x28
     1a7:	5b                   	pop    rbx
     1a8:	5e                   	pop    rsi
     1a9:	c3                   	ret
     1aa:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
     1b0:	89 c1                	mov    ecx,eax
     1b2:	89 c6                	mov    esi,eax
     1b4:	c1 e9 08             	shr    ecx,0x8
     1b7:	c1 ee 10             	shr    esi,0x10
     1ba:	8d 14 cd 00 00 00 00 	lea    edx,[rcx*8+0x0]
     1c1:	29 ca                	sub    edx,ecx
     1c3:	89 f1                	mov    ecx,esi
     1c5:	c1 e1 05             	shl    ecx,0x5
     1c8:	29 f1                	sub    ecx,esi
     1ca:	01 ca                	add    edx,ecx
     1cc:	8d 0c 40             	lea    ecx,[rax+rax*2]
     1cf:	8d 04 88             	lea    eax,[rax+rcx*4]
     1d2:	01 d0                	add    eax,edx
     1d4:	0f b6 c0             	movzx  eax,al
     1d7:	69 d0 b1 79 37 9e    	imul   edx,eax,0x9e3779b1
     1dd:	c1 e0 0d             	shl    eax,0xd
     1e0:	31 c2                	xor    edx,eax
     1e2:	81 f2 39 5a a5 00    	xor    edx,0xa55a39
     1e8:	eb 8b                	jmp    175 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x45>
     1ea:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
     1f0:	69 d0 fb 00 00 00    	imul   edx,eax,0xfb
     1f6:	89 c1                	mov    ecx,eax
     1f8:	c1 e8 07             	shr    eax,0x7
     1fb:	c1 e9 0f             	shr    ecx,0xf
     1fe:	01 ca                	add    edx,ecx
     200:	89 c1                	mov    ecx,eax
     202:	c1 e1 04             	shl    ecx,0x4
     205:	01 c8                	add    eax,ecx
     207:	01 d0                	add    eax,edx
     209:	0f b7 c0             	movzx  eax,ax
     20c:	69 d0 b1 79 37 9e    	imul   edx,eax,0x9e3779b1
     212:	c1 e0 0d             	shl    eax,0xd
     215:	31 c2                	xor    edx,eax
     217:	81 f2 39 5a a5 00    	xor    edx,0xa55a39
     21d:	e9 53 ff ff ff       	jmp    175 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x45>
     222:	b9 10 00 00 00       	mov    ecx,0x10
     227:	e8 00 00 00 00       	call   22c <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0xfc>
     22c:	48 8d 15 16 00 00 00 	lea    rdx,[rip+0x16]        # 249 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x119>
     233:	48 89 c1             	mov    rcx,rax
     236:	48 89 c3             	mov    rbx,rax
     239:	e8 00 00 00 00       	call   23e <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x10e>
     23e:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # 245 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x115>
     245:	48 89 d9             	mov    rcx,rbx
     248:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # 24f <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x11f>
     24f:	e8 00 00 00 00       	call   254 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x124>
     254:	48 89 c6             	mov    rsi,rax
     257:	48 89 d9             	mov    rcx,rbx
     25a:	e8 00 00 00 00       	call   25f <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x12f>
     25f:	48 89 f1             	mov    rcx,rsi
     262:	e8 00 00 00 00       	call   267 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x137>
     267:	90                   	nop
     268:	0f 1f 84 00 00 00 00 	nop    DWORD PTR [rax+rax*1+0x0]
     26f:	00 

0000000000000270 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0>:
     270:	56                   	push   rsi
     271:	53                   	push   rbx
     272:	48 83 ec 28          	sub    rsp,0x28
     276:	48 8d 41 ff          	lea    rax,[rcx-0x1]
     27a:	48 8d 51 bf          	lea    rdx,[rcx-0x41]
     27e:	66 90                	xchg   ax,ax
     280:	80 38 a5             	cmp    BYTE PTR [rax],0xa5
     283:	75 10                	jne    295 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x25>
     285:	48 83 e8 01          	sub    rax,0x1
     289:	48 39 d0             	cmp    rax,rdx
     28c:	75 f2                	jne    280 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x10>
     28e:	48 83 c4 28          	add    rsp,0x28
     292:	5b                   	pop    rbx
     293:	5e                   	pop    rsi
     294:	c3                   	ret
     295:	b9 10 00 00 00       	mov    ecx,0x10
     29a:	e8 00 00 00 00       	call   29f <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x2f>
     29f:	48 8d 15 32 00 00 00 	lea    rdx,[rip+0x32]        # 2d8 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x68>
     2a6:	48 89 c1             	mov    rcx,rax
     2a9:	48 89 c6             	mov    rsi,rax
     2ac:	e8 00 00 00 00       	call   2b1 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x41>
     2b1:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # 2b8 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x48>
     2b8:	48 89 f1             	mov    rcx,rsi
     2bb:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # 2c2 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x52>
     2c2:	e8 00 00 00 00       	call   2c7 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x57>
     2c7:	48 89 c3             	mov    rbx,rax
     2ca:	48 89 f1             	mov    rcx,rsi
     2cd:	e8 00 00 00 00       	call   2d2 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x62>
     2d2:	48 89 d9             	mov    rcx,rbx
     2d5:	e8 00 00 00 00       	call   2da <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0+0x6a>
     2da:	90                   	nop
     2db:	90                   	nop
     2dc:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]

00000000000002e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>:
     2e0:	48 83 ec 28          	sub    rsp,0x28
     2e4:	48 85 c9             	test   rcx,rcx
     2e7:	74 0f                	je     2f8 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0+0x18>
     2e9:	41 b8 00 80 00 00    	mov    r8d,0x8000
     2ef:	31 d2                	xor    edx,edx
     2f1:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 2f7 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0+0x17>
     2f7:	90                   	nop
     2f8:	48 83 c4 28          	add    rsp,0x28
     2fc:	c3                   	ret
     2fd:	0f 1f 00             	nop    DWORD PTR [rax]

0000000000000300 <_ZN12_GLOBAL__N_1L3runEj>:
     300:	41 57                	push   r15
     302:	41 56                	push   r14
     304:	41 55                	push   r13
     306:	41 54                	push   r12
     308:	55                   	push   rbp
     309:	57                   	push   rdi
     30a:	56                   	push   rsi
     30b:	53                   	push   rbx
     30c:	48 81 ec 58 01 00 00 	sub    rsp,0x158
     313:	83 f9 08             	cmp    ecx,0x8
     316:	89 8c 24 a0 01 00 00 	mov    DWORD PTR [rsp+0x1a0],ecx
     31d:	48 8d 8c 24 a0 00 00 	lea    rcx,[rsp+0xa0]
     324:	00 
     325:	74 5a                	je     381 <_ZN12_GLOBAL__N_1L3runEj+0x81>
     327:	83 bc 24 a0 01 00 00 	cmp    DWORD PTR [rsp+0x1a0],0x10
     32e:	10 
     32f:	0f 84 40 0a 00 00    	je     d75 <_ZN12_GLOBAL__N_1L3runEj+0xa75>
     335:	ba 04 00 00 03       	mov    edx,0x3000004
     33a:	e8 c1 fc ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     33f:	48 c7 84 24 90 00 00 	mov    QWORD PTR [rsp+0x90],0x3000000
     346:	00 00 00 00 03 
     34b:	48 8d 8c 24 c0 00 00 	lea    rcx,[rsp+0xc0]
     352:	00 
     353:	ba 00 00 04 00       	mov    edx,0x40000
     358:	e8 a3 fc ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     35d:	48 8b 84 24 d8 00 00 	mov    rax,QWORD PTR [rsp+0xd8]
     364:	00 
     365:	41 b8 00 00 01 00    	mov    r8d,0x10000
     36b:	48 c7 84 24 98 00 00 	mov    QWORD PTR [rsp+0x98],0x4
     372:	00 04 00 00 00 
     377:	48 89 84 24 88 00 00 	mov    QWORD PTR [rsp+0x88],rax
     37e:	00 
     37f:	eb 48                	jmp    3c9 <_ZN12_GLOBAL__N_1L3runEj+0xc9>
     381:	ba 00 00 00 01       	mov    edx,0x1000000
     386:	e8 75 fc ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     38b:	48 8d 8c 24 c0 00 00 	lea    rcx,[rsp+0xc0]
     392:	00 
     393:	ba 00 04 00 00       	mov    edx,0x400
     398:	e8 63 fc ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     39d:	48 8b 84 24 d8 00 00 	mov    rax,QWORD PTR [rsp+0xd8]
     3a4:	00 
     3a5:	31 c9                	xor    ecx,ecx
     3a7:	41 b8 00 01 00 00    	mov    r8d,0x100
     3ad:	48 c7 84 24 90 00 00 	mov    QWORD PTR [rsp+0x90],0x1000000
     3b4:	00 00 00 00 01 
     3b9:	48 89 8c 24 98 00 00 	mov    QWORD PTR [rsp+0x98],rcx
     3c0:	00 
     3c1:	48 89 84 24 88 00 00 	mov    QWORD PTR [rsp+0x88],rax
     3c8:	00 
     3c9:	31 c9                	xor    ecx,ecx
     3cb:	31 c0                	xor    eax,eax
     3cd:	89 c2                	mov    edx,eax
     3cf:	48 8b bc 24 88 00 00 	mov    rdi,QWORD PTR [rsp+0x88]
     3d6:	00 
     3d7:	c1 e2 0d             	shl    edx,0xd
     3da:	31 ca                	xor    edx,ecx
     3dc:	81 e9 4f 86 c8 61    	sub    ecx,0x61c8864f
     3e2:	81 f2 39 5a a5 00    	xor    edx,0xa55a39
     3e8:	89 14 87             	mov    DWORD PTR [rdi+rax*4],edx
     3eb:	48 83 c0 01          	add    rax,0x1
     3ef:	49 39 c0             	cmp    r8,rax
     3f2:	75 d9                	jne    3cd <_ZN12_GLOBAL__N_1L3runEj+0xcd>
     3f4:	8b 9c 24 a0 01 00 00 	mov    ebx,DWORD PTR [rsp+0x1a0]
     3fb:	45 31 c9             	xor    r9d,r9d
     3fe:	45 31 c0             	xor    r8d,r8d
     401:	45 31 db             	xor    r11d,r11d
     404:	45 31 d2             	xor    r10d,r10d
     407:	31 c0                	xor    eax,eax
     409:	eb 42                	jmp    44d <_ZN12_GLOBAL__N_1L3runEj+0x14d>
     40b:	83 fb 10             	cmp    ebx,0x10
     40e:	74 6a                	je     47a <_ZN12_GLOBAL__N_1L3runEj+0x17a>
     410:	48 8d 34 40          	lea    rsi,[rax+rax*2]
     414:	c1 ea 05             	shr    edx,0x5
     417:	44 31 ca             	xor    edx,r9d
     41a:	81 f2 9b 48 12 00    	xor    edx,0x12489b
     420:	66 89 14 31          	mov    WORD PTR [rcx+rsi*1],dx
     424:	c1 ea 10             	shr    edx,0x10
     427:	88 54 31 02          	mov    BYTE PTR [rcx+rsi*1+0x2],dl
     42b:	48 83 c0 01          	add    rax,0x1
     42f:	41 83 c2 0d          	add    r10d,0xd
     433:	49 83 c0 02          	add    r8,0x2
     437:	41 81 c3 fb 00 00 00 	add    r11d,0xfb
     43e:	41 81 c1 f5 9c 8e 6c 	add    r9d,0x6c8e9cf5
     445:	48 3d 00 00 00 01    	cmp    rax,0x1000000
     44b:	74 59                	je     4a6 <_ZN12_GLOBAL__N_1L3runEj+0x1a6>
     44d:	83 fb 08             	cmp    ebx,0x8
     450:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     457:	00 
     458:	89 c2                	mov    edx,eax
     45a:	75 af                	jne    40b <_ZN12_GLOBAL__N_1L3runEj+0x10b>
     45c:	89 c6                	mov    esi,eax
     45e:	c1 ee 10             	shr    esi,0x10
     461:	89 f2                	mov    edx,esi
     463:	c1 e2 05             	shl    edx,0x5
     466:	29 f2                	sub    edx,esi
     468:	89 c6                	mov    esi,eax
     46a:	c1 ee 08             	shr    esi,0x8
     46d:	8d 14 f2             	lea    edx,[rdx+rsi*8]
     470:	29 f2                	sub    edx,esi
     472:	44 01 d2             	add    edx,r10d
     475:	88 14 01             	mov    BYTE PTR [rcx+rax*1],dl
     478:	eb b1                	jmp    42b <_ZN12_GLOBAL__N_1L3runEj+0x12b>
     47a:	89 c7                	mov    edi,eax
     47c:	c1 ea 0f             	shr    edx,0xf
     47f:	c1 ef 07             	shr    edi,0x7
     482:	44 01 da             	add    edx,r11d
     485:	89 fe                	mov    esi,edi
     487:	c1 e6 04             	shl    esi,0x4
     48a:	01 fe                	add    esi,edi
     48c:	4c 89 c7             	mov    rdi,r8
     48f:	01 f2                	add    edx,esi
     491:	0f b7 d2             	movzx  edx,dx
     494:	42 88 14 01          	mov    BYTE PTR [rcx+r8*1],dl
     498:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     49f:	00 
     4a0:	88 74 39 01          	mov    BYTE PTR [rcx+rdi*1+0x1],dh
     4a4:	eb 85                	jmp    42b <_ZN12_GLOBAL__N_1L3runEj+0x12b>
     4a6:	48 83 bc 24 98 00 00 	cmp    QWORD PTR [rsp+0x98],0x0
     4ad:	00 00 
     4af:	0f 85 a5 08 00 00    	jne    d5a <_ZN12_GLOBAL__N_1L3runEj+0xa5a>
     4b5:	83 bc 24 a0 01 00 00 	cmp    DWORD PTR [rsp+0x1a0],0x8
     4bc:	08 
     4bd:	0f 84 7c 08 00 00    	je     d3f <_ZN12_GLOBAL__N_1L3runEj+0xa3f>
     4c3:	83 bc 24 a0 01 00 00 	cmp    DWORD PTR [rsp+0x1a0],0x10
     4ca:	10 
     4cb:	0f 84 53 08 00 00    	je     d24 <_ZN12_GLOBAL__N_1L3runEj+0xa24>
     4d1:	45 31 c9             	xor    r9d,r9d
     4d4:	45 31 c0             	xor    r8d,r8d
     4d7:	31 d2                	xor    edx,edx
     4d9:	31 c9                	xor    ecx,ecx
     4db:	e8 00 00 00 00       	call   4e0 <_ZN12_GLOBAL__N_1L3runEj+0x1e0>
     4e0:	48 8d 84 24 20 01 00 	lea    rax,[rsp+0x120]
     4e7:	00 
     4e8:	41 be 01 00 00 00    	mov    r14d,0x1
     4ee:	bb 26 12 a5 16       	mov    ebx,0x16a51226
     4f3:	49 bd a5 a5 a5 a5 a5 	movabs r13,0xa5a5a5a5a5a5a5a5
     4fa:	a5 a5 a5 
     4fd:	48 89 44 24 78       	mov    QWORD PTR [rsp+0x78],rax
     502:	48 89 44 24 40       	mov    QWORD PTR [rsp+0x40],rax
     507:	48 8b 7c 24 78       	mov    rdi,QWORD PTR [rsp+0x78]
     50c:	4b 8d 34 76          	lea    rsi,[r14+r14*2]
     510:	b9 06 00 00 00       	mov    ecx,0x6
     515:	31 c0                	xor    eax,eax
     517:	48 89 74 24 38       	mov    QWORD PTR [rsp+0x38],rsi
     51c:	f3 48 ab             	rep stos QWORD PTR [rdi],rax
     51f:	48 8b 4c 24 40       	mov    rcx,QWORD PTR [rsp+0x40]
     524:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 52a <_ZN12_GLOBAL__N_1L3runEj+0x22a>
     52a:	8b bc 24 24 01 00 00 	mov    edi,DWORD PTR [rsp+0x124]
     531:	31 d2                	xor    edx,edx
     533:	41 b9 01 00 00 00    	mov    r9d,0x1
     539:	31 c9                	xor    ecx,ecx
     53b:	41 b8 00 30 00 00    	mov    r8d,0x3000
     541:	48 8d 74 37 3f       	lea    rsi,[rdi+rsi*1+0x3f]
     546:	48 89 f0             	mov    rax,rsi
     549:	48 f7 f7             	div    rdi
     54c:	48 29 d6             	sub    rsi,rdx
     54f:	48 8d 14 7e          	lea    rdx,[rsi+rdi*2]
     553:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 559 <_ZN12_GLOBAL__N_1L3runEj+0x259>
     559:	48 85 c0             	test   rax,rax
     55c:	48 89 44 24 58       	mov    QWORD PTR [rsp+0x58],rax
     561:	c7 84 24 00 01 00 00 	mov    DWORD PTR [rsp+0x100],0x0
     568:	00 00 00 00 
     56c:	0f 84 48 08 00 00    	je     dba <_ZN12_GLOBAL__N_1L3runEj+0xaba>
     572:	4c 8b 7c 24 58       	mov    r15,QWORD PTR [rsp+0x58]
     577:	4c 8d 8c 24 00 01 00 	lea    r9,[rsp+0x100]
     57e:	00 
     57f:	41 b8 04 00 00 00    	mov    r8d,0x4
     585:	48 89 f2             	mov    rdx,rsi
     588:	4c 89 4c 24 50       	mov    QWORD PTR [rsp+0x50],r9
     58d:	49 8d 0c 3f          	lea    rcx,[r15+rdi*1]
     591:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 597 <_ZN12_GLOBAL__N_1L3runEj+0x297>
     597:	85 c0                	test   eax,eax
     599:	0f 84 1b 08 00 00    	je     dba <_ZN12_GLOBAL__N_1L3runEj+0xaba>
     59f:	48 2b 7c 24 38       	sub    rdi,QWORD PTR [rsp+0x38]
     5a4:	b9 06 00 00 00       	mov    ecx,0x6
     5a9:	31 c0                	xor    eax,eax
     5ab:	48 8d 2c 37          	lea    rbp,[rdi+rsi*1]
     5af:	48 8b 7c 24 40       	mov    rdi,QWORD PTR [rsp+0x40]
     5b4:	4c 01 fd             	add    rbp,r15
     5b7:	4c 89 6d c0          	mov    QWORD PTR [rbp-0x40],r13
     5bb:	4c 89 6d c8          	mov    QWORD PTR [rbp-0x38],r13
     5bf:	4c 89 6d d0          	mov    QWORD PTR [rbp-0x30],r13
     5c3:	4c 89 6d d8          	mov    QWORD PTR [rbp-0x28],r13
     5c7:	4c 89 6d e0          	mov    QWORD PTR [rbp-0x20],r13
     5cb:	4c 89 6d e8          	mov    QWORD PTR [rbp-0x18],r13
     5cf:	4c 89 6d f0          	mov    QWORD PTR [rbp-0x10],r13
     5d3:	4c 89 6d f8          	mov    QWORD PTR [rbp-0x8],r13
     5d7:	f3 48 ab             	rep stos QWORD PTR [rdi],rax
     5da:	48 8b 4c 24 40       	mov    rcx,QWORD PTR [rsp+0x40]
     5df:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 5e5 <_ZN12_GLOBAL__N_1L3runEj+0x2e5>
     5e5:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
     5ea:	31 d2                	xor    edx,edx
     5ec:	41 b9 01 00 00 00    	mov    r9d,0x1
     5f2:	31 c9                	xor    ecx,ecx
     5f4:	8b bc 24 24 01 00 00 	mov    edi,DWORD PTR [rsp+0x124]
     5fb:	41 b8 00 30 00 00    	mov    r8d,0x3000
     601:	48 8d 74 07 3f       	lea    rsi,[rdi+rax*1+0x3f]
     606:	48 89 f0             	mov    rax,rsi
     609:	48 f7 f7             	div    rdi
     60c:	48 29 d6             	sub    rsi,rdx
     60f:	48 8d 14 7e          	lea    rdx,[rsi+rdi*2]
     613:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 619 <_ZN12_GLOBAL__N_1L3runEj+0x319>
     619:	48 85 c0             	test   rax,rax
     61c:	48 89 44 24 60       	mov    QWORD PTR [rsp+0x60],rax
     621:	c7 84 24 00 01 00 00 	mov    DWORD PTR [rsp+0x100],0x0
     628:	00 00 00 00 
     62c:	0f 84 d6 07 00 00    	je     e08 <_ZN12_GLOBAL__N_1L3runEj+0xb08>
     632:	4c 8b 7c 24 60       	mov    r15,QWORD PTR [rsp+0x60]
     637:	41 b8 04 00 00 00    	mov    r8d,0x4
     63d:	48 89 f2             	mov    rdx,rsi
     640:	4c 8b 4c 24 50       	mov    r9,QWORD PTR [rsp+0x50]
     645:	49 8d 0c 3f          	lea    rcx,[r15+rdi*1]
     649:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 64f <_ZN12_GLOBAL__N_1L3runEj+0x34f>
     64f:	85 c0                	test   eax,eax
     651:	0f 84 b1 07 00 00    	je     e08 <_ZN12_GLOBAL__N_1L3runEj+0xb08>
     657:	48 2b 7c 24 38       	sub    rdi,QWORD PTR [rsp+0x38]
     65c:	b9 06 00 00 00       	mov    ecx,0x6
     661:	31 c0                	xor    eax,eax
     663:	4c 8d 24 37          	lea    r12,[rdi+rsi*1]
     667:	48 8b 7c 24 40       	mov    rdi,QWORD PTR [rsp+0x40]
     66c:	4d 01 fc             	add    r12,r15
     66f:	4d 89 6c 24 c0       	mov    QWORD PTR [r12-0x40],r13
     674:	4d 89 6c 24 c8       	mov    QWORD PTR [r12-0x38],r13
     679:	4d 89 6c 24 d0       	mov    QWORD PTR [r12-0x30],r13
     67e:	4d 89 6c 24 d8       	mov    QWORD PTR [r12-0x28],r13
     683:	4d 89 6c 24 e0       	mov    QWORD PTR [r12-0x20],r13
     688:	4d 89 6c 24 e8       	mov    QWORD PTR [r12-0x18],r13
     68d:	4d 89 6c 24 f0       	mov    QWORD PTR [r12-0x10],r13
     692:	4d 89 6c 24 f8       	mov    QWORD PTR [r12-0x8],r13
     697:	f3 48 ab             	rep stos QWORD PTR [rdi],rax
     69a:	48 8b 4c 24 40       	mov    rcx,QWORD PTR [rsp+0x40]
     69f:	48 89 4c 24 78       	mov    QWORD PTR [rsp+0x78],rcx
     6a4:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 6aa <_ZN12_GLOBAL__N_1L3runEj+0x3aa>
     6aa:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
     6af:	31 d2                	xor    edx,edx
     6b1:	41 b9 01 00 00 00    	mov    r9d,0x1
     6b7:	31 c9                	xor    ecx,ecx
     6b9:	8b bc 24 24 01 00 00 	mov    edi,DWORD PTR [rsp+0x124]
     6c0:	41 b8 00 30 00 00    	mov    r8d,0x3000
     6c6:	48 8d 74 07 3f       	lea    rsi,[rdi+rax*1+0x3f]
     6cb:	48 89 f0             	mov    rax,rsi
     6ce:	48 f7 f7             	div    rdi
     6d1:	48 29 d6             	sub    rsi,rdx
     6d4:	48 8d 14 7e          	lea    rdx,[rsi+rdi*2]
     6d8:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 6de <_ZN12_GLOBAL__N_1L3runEj+0x3de>
     6de:	48 85 c0             	test   rax,rax
     6e1:	48 89 44 24 68       	mov    QWORD PTR [rsp+0x68],rax
     6e6:	c7 84 24 00 01 00 00 	mov    DWORD PTR [rsp+0x100],0x0
     6ed:	00 00 00 00 
     6f1:	0f 84 5f 07 00 00    	je     e56 <_ZN12_GLOBAL__N_1L3runEj+0xb56>
     6f7:	4c 8b 7c 24 68       	mov    r15,QWORD PTR [rsp+0x68]
     6fc:	41 b8 04 00 00 00    	mov    r8d,0x4
     702:	48 89 f2             	mov    rdx,rsi
     705:	4c 8b 4c 24 50       	mov    r9,QWORD PTR [rsp+0x50]
     70a:	49 8d 0c 3f          	lea    rcx,[r15+rdi*1]
     70e:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 714 <_ZN12_GLOBAL__N_1L3runEj+0x414>
     714:	85 c0                	test   eax,eax
     716:	0f 84 3a 07 00 00    	je     e56 <_ZN12_GLOBAL__N_1L3runEj+0xb56>
     71c:	48 2b 7c 24 38       	sub    rdi,QWORD PTR [rsp+0x38]
     721:	48 01 fe             	add    rsi,rdi
     724:	4a 8d 3c b5 00 00 00 	lea    rdi,[r14*4+0x0]
     72b:	00 
     72c:	4c 01 fe             	add    rsi,r15
     72f:	4c 89 6e c0          	mov    QWORD PTR [rsi-0x40],r13
     733:	48 89 f9             	mov    rcx,rdi
     736:	4c 89 6e c8          	mov    QWORD PTR [rsi-0x38],r13
     73a:	4c 89 6e d0          	mov    QWORD PTR [rsi-0x30],r13
     73e:	4c 89 6e d8          	mov    QWORD PTR [rsi-0x28],r13
     742:	4c 89 6e e0          	mov    QWORD PTR [rsi-0x20],r13
     746:	4c 89 6e e8          	mov    QWORD PTR [rsi-0x18],r13
     74a:	4c 89 6e f0          	mov    QWORD PTR [rsi-0x10],r13
     74e:	4c 89 6e f8          	mov    QWORD PTR [rsi-0x8],r13
     752:	48 89 7c 24 70       	mov    QWORD PTR [rsp+0x70],rdi
     757:	e8 00 00 00 00       	call   75c <_ZN12_GLOBAL__N_1L3runEj+0x45c>
     75c:	49 89 c7             	mov    r15,rax
     75f:	49 83 fe 01          	cmp    r14,0x1
     763:	48 8d 04 38          	lea    rax,[rax+rdi*1]
     767:	41 c7 07 00 00 00 00 	mov    DWORD PTR [r15],0x0
     76e:	48 89 84 24 80 00 00 	mov    QWORD PTR [rsp+0x80],rax
     775:	00 
     776:	49 8d 47 04          	lea    rax,[r15+0x4]
     77a:	48 89 44 24 48       	mov    QWORD PTR [rsp+0x48],rax
     77f:	74 3d                	je     7be <_ZN12_GLOBAL__N_1L3runEj+0x4be>
     781:	48 8b 44 24 70       	mov    rax,QWORD PTR [rsp+0x70]
     786:	48 83 e8 04          	sub    rax,0x4
     78a:	83 f8 08             	cmp    eax,0x8
     78d:	0f 83 4b 04 00 00    	jae    bde <_ZN12_GLOBAL__N_1L3runEj+0x8de>
     793:	a8 04                	test   al,0x4
     795:	0f 85 6d 05 00 00    	jne    d08 <_ZN12_GLOBAL__N_1L3runEj+0xa08>
     79b:	85 c0                	test   eax,eax
     79d:	74 05                	je     7a4 <_ZN12_GLOBAL__N_1L3runEj+0x4a4>
     79f:	41 c6 47 04 00       	mov    BYTE PTR [r15+0x4],0x0
     7a4:	48 8b 7c 24 48       	mov    rdi,QWORD PTR [rsp+0x48]
     7a9:	48 8b 84 24 80 00 00 	mov    rax,QWORD PTR [rsp+0x80]
     7b0:	00 
     7b1:	48 8d 44 38 fc       	lea    rax,[rax+rdi*1-0x4]
     7b6:	4c 29 f8             	sub    rax,r15
     7b9:	48 89 44 24 48       	mov    QWORD PTR [rsp+0x48],rax
     7be:	48 89 e9             	mov    rcx,rbp
     7c1:	31 d2                	xor    edx,edx
     7c3:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
     7c8:	89 d8                	mov    eax,ebx
     7ca:	c1 e0 0d             	shl    eax,0xd
     7cd:	31 d8                	xor    eax,ebx
     7cf:	41 89 c1             	mov    r9d,eax
     7d2:	41 c1 e9 11          	shr    r9d,0x11
     7d6:	44 31 c8             	xor    eax,r9d
     7d9:	41 b9 ff ff ff 00    	mov    r9d,0xffffff
     7df:	89 c3                	mov    ebx,eax
     7e1:	c1 e3 05             	shl    ebx,0x5
     7e4:	31 c3                	xor    ebx,eax
     7e6:	89 d0                	mov    eax,edx
     7e8:	83 e0 0f             	and    eax,0xf
     7eb:	41 29 c1             	sub    r9d,eax
     7ee:	89 d8                	mov    eax,ebx
     7f0:	25 ff ff ff 00       	and    eax,0xffffff
     7f5:	f6 c2 03             	test   dl,0x3
     7f8:	41 0f 44 c1          	cmove  eax,r9d
     7fc:	48 83 c1 03          	add    rcx,0x3
     800:	41 89 04 97          	mov    DWORD PTR [r15+rdx*4],eax
     804:	48 83 c2 01          	add    rdx,0x1
     808:	66 89 41 fd          	mov    WORD PTR [rcx-0x3],ax
     80c:	c1 e8 10             	shr    eax,0x10
     80f:	88 41 ff             	mov    BYTE PTR [rcx-0x1],al
     812:	4c 39 f2             	cmp    rdx,r14
     815:	75 b1                	jne    7c8 <_ZN12_GLOBAL__N_1L3runEj+0x4c8>
     817:	48 8b 4c 24 38       	mov    rcx,QWORD PTR [rsp+0x38]
     81c:	e8 00 00 00 00       	call   821 <_ZN12_GLOBAL__N_1L3runEj+0x521>
     821:	4c 8b 44 24 38       	mov    r8,QWORD PTR [rsp+0x38]
     826:	48 89 ea             	mov    rdx,rbp
     829:	48 89 c1             	mov    rcx,rax
     82c:	48 89 c7             	mov    rdi,rax
     82f:	e8 00 00 00 00       	call   834 <_ZN12_GLOBAL__N_1L3runEj+0x534>
     834:	4c 8b 44 24 38       	mov    r8,QWORD PTR [rsp+0x38]
     839:	48 89 f1             	mov    rcx,rsi
     83c:	48 89 ea             	mov    rdx,rbp
     83f:	e8 00 00 00 00       	call   844 <_ZN12_GLOBAL__N_1L3runEj+0x544>
     844:	83 bc 24 a0 01 00 00 	cmp    DWORD PTR [rsp+0x1a0],0x8
     84b:	08 
     84c:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     853:	00 
     854:	0f 84 71 04 00 00    	je     ccb <_ZN12_GLOBAL__N_1L3runEj+0x9cb>
     85a:	83 bc 24 a0 01 00 00 	cmp    DWORD PTR [rsp+0x1a0],0x10
     861:	10 
     862:	0f 84 de 03 00 00    	je     c46 <_ZN12_GLOBAL__N_1L3runEj+0x946>
     868:	4d 89 f1             	mov    r9,r14
     86b:	4d 89 e0             	mov    r8,r12
     86e:	48 89 ea             	mov    rdx,rbp
     871:	e8 00 00 00 00       	call   876 <_ZN12_GLOBAL__N_1L3runEj+0x576>
     876:	4d 89 f1             	mov    r9,r14
     879:	49 89 f0             	mov    r8,rsi
     87c:	48 89 f2             	mov    rdx,rsi
     87f:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     886:	00 
     887:	e8 00 00 00 00       	call   88c <_ZN12_GLOBAL__N_1L3runEj+0x58c>
     88c:	4c 8b 4c 24 48       	mov    r9,QWORD PTR [rsp+0x48]
     891:	4d 89 f8             	mov    r8,r15
     894:	4c 89 e2             	mov    rdx,r12
     897:	8b 8c 24 a0 01 00 00 	mov    ecx,DWORD PTR [rsp+0x1a0]
     89e:	e8 8d f8 ff ff       	call   130 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0>
     8a3:	4c 8b 4c 24 48       	mov    r9,QWORD PTR [rsp+0x48]
     8a8:	4d 89 f8             	mov    r8,r15
     8ab:	48 89 f2             	mov    rdx,rsi
     8ae:	8b 8c 24 a0 01 00 00 	mov    ecx,DWORD PTR [rsp+0x1a0]
     8b5:	e8 76 f8 ff ff       	call   130 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0>
     8ba:	4c 8b 44 24 38       	mov    r8,QWORD PTR [rsp+0x38]
     8bf:	48 89 ea             	mov    rdx,rbp
     8c2:	48 89 f9             	mov    rcx,rdi
     8c5:	e8 00 00 00 00       	call   8ca <_ZN12_GLOBAL__N_1L3runEj+0x5ca>
     8ca:	85 c0                	test   eax,eax
     8cc:	0f 85 f9 05 00 00    	jne    ecb <_ZN12_GLOBAL__N_1L3runEj+0xbcb>
     8d2:	48 8d 45 ff          	lea    rax,[rbp-0x1]
     8d6:	48 83 ed 41          	sub    rbp,0x41
     8da:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
     8e0:	80 38 a5             	cmp    BYTE PTR [rax],0xa5
     8e3:	0f 85 21 06 00 00    	jne    f0a <_ZN12_GLOBAL__N_1L3runEj+0xc0a>
     8e9:	48 83 e8 01          	sub    rax,0x1
     8ed:	48 39 c5             	cmp    rbp,rax
     8f0:	75 ee                	jne    8e0 <_ZN12_GLOBAL__N_1L3runEj+0x5e0>
     8f2:	49 8d 44 24 ff       	lea    rax,[r12-0x1]
     8f7:	49 83 ec 41          	sub    r12,0x41
     8fb:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
     900:	80 38 a5             	cmp    BYTE PTR [rax],0xa5
     903:	0f 85 a7 06 00 00    	jne    fb0 <_ZN12_GLOBAL__N_1L3runEj+0xcb0>
     909:	48 83 e8 01          	sub    rax,0x1
     90d:	4c 39 e0             	cmp    rax,r12
     910:	75 ee                	jne    900 <_ZN12_GLOBAL__N_1L3runEj+0x600>
     912:	48 8d 46 ff          	lea    rax,[rsi-0x1]
     916:	48 83 ee 41          	sub    rsi,0x41
     91a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
     920:	80 38 a5             	cmp    BYTE PTR [rax],0xa5
     923:	0f 85 35 06 00 00    	jne    f5e <_ZN12_GLOBAL__N_1L3runEj+0xc5e>
     929:	48 83 e8 01          	sub    rax,0x1
     92d:	48 39 f0             	cmp    rax,rsi
     930:	75 ee                	jne    920 <_ZN12_GLOBAL__N_1L3runEj+0x620>
     932:	48 8b 54 24 38       	mov    rdx,QWORD PTR [rsp+0x38]
     937:	48 89 f9             	mov    rcx,rdi
     93a:	49 83 c6 01          	add    r14,0x1
     93e:	e8 00 00 00 00       	call   943 <_ZN12_GLOBAL__N_1L3runEj+0x643>
     943:	48 8b 54 24 70       	mov    rdx,QWORD PTR [rsp+0x70]
     948:	4c 89 f9             	mov    rcx,r15
     94b:	e8 00 00 00 00       	call   950 <_ZN12_GLOBAL__N_1L3runEj+0x650>
     950:	31 d2                	xor    edx,edx
     952:	48 8b 4c 24 68       	mov    rcx,QWORD PTR [rsp+0x68]
     957:	41 b8 00 80 00 00    	mov    r8d,0x8000
     95d:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 963 <_ZN12_GLOBAL__N_1L3runEj+0x663>
     963:	31 d2                	xor    edx,edx
     965:	48 8b 4c 24 60       	mov    rcx,QWORD PTR [rsp+0x60]
     96a:	41 b8 00 80 00 00    	mov    r8d,0x8000
     970:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 976 <_ZN12_GLOBAL__N_1L3runEj+0x676>
     976:	31 d2                	xor    edx,edx
     978:	48 8b 4c 24 58       	mov    rcx,QWORD PTR [rsp+0x58]
     97d:	41 b8 00 80 00 00    	mov    r8d,0x8000
     983:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # 989 <_ZN12_GLOBAL__N_1L3runEj+0x689>
     989:	49 83 fe 61          	cmp    r14,0x61
     98d:	0f 85 74 fb ff ff    	jne    507 <_ZN12_GLOBAL__N_1L3runEj+0x207>
     993:	48 8d 8c 24 e0 00 00 	lea    rcx,[rsp+0xe0]
     99a:	00 
     99b:	ba 00 30 00 00       	mov    edx,0x3000
     9a0:	e8 5b f6 ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     9a5:	48 8b 4c 24 50       	mov    rcx,QWORD PTR [rsp+0x50]
     9aa:	ba 00 30 00 00       	mov    edx,0x3000
     9af:	e8 4c f6 ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     9b4:	48 8b 4c 24 40       	mov    rcx,QWORD PTR [rsp+0x40]
     9b9:	ba 00 30 00 00       	mov    edx,0x3000
     9be:	e8 3d f6 ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     9c3:	b9 00 40 00 00       	mov    ecx,0x4000
     9c8:	e8 00 00 00 00       	call   9cd <_ZN12_GLOBAL__N_1L3runEj+0x6cd>
     9cd:	c7 00 00 00 00 00    	mov    DWORD PTR [rax],0x0
     9d3:	48 8d 48 04          	lea    rcx,[rax+0x4]
     9d7:	31 d2                	xor    edx,edx
     9d9:	48 89 c3             	mov    rbx,rax
     9dc:	48 8d a8 00 40 00 00 	lea    rbp,[rax+0x4000]
     9e3:	41 b8 fc 3f 00 00    	mov    r8d,0x3ffc
     9e9:	31 f6                	xor    esi,esi
     9eb:	e8 00 00 00 00       	call   9f0 <_ZN12_GLOBAL__N_1L3runEj+0x6f0>
     9f0:	89 f2                	mov    edx,esi
     9f2:	31 c0                	xor    eax,eax
     9f4:	90                   	nop
     9f5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
     9fc:	00 00 00 00 
     a00:	48 8d 0c 40          	lea    rcx,[rax+rax*2]
     a04:	48 03 8c 24 f8 00 00 	add    rcx,QWORD PTR [rsp+0xf8]
     a0b:	00 
     a0c:	89 14 83             	mov    DWORD PTR [rbx+rax*4],edx
     a0f:	41 89 d0             	mov    r8d,edx
     a12:	48 83 c0 01          	add    rax,0x1
     a16:	41 c1 e8 10          	shr    r8d,0x10
     a1a:	66 89 11             	mov    WORD PTR [rcx],dx
     a1d:	83 c2 01             	add    edx,0x1
     a20:	48 3d 00 10 00 00    	cmp    rax,0x1000
     a26:	44 88 41 02          	mov    BYTE PTR [rcx+0x2],r8b
     a2a:	75 d4                	jne    a00 <_ZN12_GLOBAL__N_1L3runEj+0x700>
     a2c:	48 8b 94 24 f8 00 00 	mov    rdx,QWORD PTR [rsp+0xf8]
     a33:	00 
     a34:	41 b8 00 30 00 00    	mov    r8d,0x3000
     a3a:	48 8b 8c 24 38 01 00 	mov    rcx,QWORD PTR [rsp+0x138]
     a41:	00 
     a42:	e8 00 00 00 00       	call   a47 <_ZN12_GLOBAL__N_1L3runEj+0x747>
     a47:	83 bc 24 a0 01 00 00 	cmp    DWORD PTR [rsp+0x1a0],0x8
     a4e:	08 
     a4f:	4c 8b 84 24 18 01 00 	mov    r8,QWORD PTR [rsp+0x118]
     a56:	00 
     a57:	48 8b 94 24 f8 00 00 	mov    rdx,QWORD PTR [rsp+0xf8]
     a5e:	00 
     a5f:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     a66:	00 
     a67:	0f 84 16 02 00 00    	je     c83 <_ZN12_GLOBAL__N_1L3runEj+0x983>
     a6d:	83 bc 24 a0 01 00 00 	cmp    DWORD PTR [rsp+0x1a0],0x10
     a74:	10 
     a75:	0f 84 83 01 00 00    	je     bfe <_ZN12_GLOBAL__N_1L3runEj+0x8fe>
     a7b:	41 b9 00 10 00 00    	mov    r9d,0x1000
     a81:	e8 00 00 00 00       	call   a86 <_ZN12_GLOBAL__N_1L3runEj+0x786>
     a86:	48 8b 94 24 38 01 00 	mov    rdx,QWORD PTR [rsp+0x138]
     a8d:	00 
     a8e:	41 b9 00 10 00 00    	mov    r9d,0x1000
     a94:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     a9b:	00 
     a9c:	49 89 d0             	mov    r8,rdx
     a9f:	e8 00 00 00 00       	call   aa4 <_ZN12_GLOBAL__N_1L3runEj+0x7a4>
     aa4:	48 8b 94 24 18 01 00 	mov    rdx,QWORD PTR [rsp+0x118]
     aab:	00 
     aac:	49 89 e9             	mov    r9,rbp
     aaf:	49 89 d8             	mov    r8,rbx
     ab2:	8b 8c 24 a0 01 00 00 	mov    ecx,DWORD PTR [rsp+0x1a0]
     ab9:	e8 72 f6 ff ff       	call   130 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0>
     abe:	48 8b 94 24 38 01 00 	mov    rdx,QWORD PTR [rsp+0x138]
     ac5:	00 
     ac6:	49 89 e9             	mov    r9,rbp
     ac9:	49 89 d8             	mov    r8,rbx
     acc:	8b 8c 24 a0 01 00 00 	mov    ecx,DWORD PTR [rsp+0x1a0]
     ad3:	e8 58 f6 ff ff       	call   130 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0>
     ad8:	48 81 c6 00 10 00 00 	add    rsi,0x1000
     adf:	48 81 fe 00 00 00 01 	cmp    rsi,0x1000000
     ae6:	0f 85 04 ff ff ff    	jne    9f0 <_ZN12_GLOBAL__N_1L3runEj+0x6f0>
     aec:	48 8b 8c 24 f8 00 00 	mov    rcx,QWORD PTR [rsp+0xf8]
     af3:	00 
     af4:	e8 77 f7 ff ff       	call   270 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0>
     af9:	48 8b 8c 24 18 01 00 	mov    rcx,QWORD PTR [rsp+0x118]
     b00:	00 
     b01:	e8 6a f7 ff ff       	call   270 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0>
     b06:	48 8b 8c 24 38 01 00 	mov    rcx,QWORD PTR [rsp+0x138]
     b0d:	00 
     b0e:	e8 5d f7 ff ff       	call   270 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0>
     b13:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     b1a:	00 
     b1b:	e8 50 f7 ff ff       	call   270 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0>
     b20:	48 8b 8c 24 d8 00 00 	mov    rcx,QWORD PTR [rsp+0xd8]
     b27:	00 
     b28:	e8 43 f7 ff ff       	call   270 <_ZNK12_GLOBAL__N_17Guarded5checkEv.isra.0>
     b2d:	48 83 bc 24 98 00 00 	cmp    QWORD PTR [rsp+0x98],0x0
     b34:	00 00 
     b36:	74 26                	je     b5e <_ZN12_GLOBAL__N_1L3runEj+0x85e>
     b38:	48 8b 84 24 90 00 00 	mov    rax,QWORD PTR [rsp+0x90]
     b3f:	00 
     b40:	31 d2                	xor    edx,edx
     b42:	48 03 84 24 b8 00 00 	add    rax,QWORD PTR [rsp+0xb8]
     b49:	00 
     b4a:	80 3c 10 5a          	cmp    BYTE PTR [rax+rdx*1],0x5a
     b4e:	0f 85 9b 04 00 00    	jne    fef <_ZN12_GLOBAL__N_1L3runEj+0xcef>
     b54:	48 83 c2 01          	add    rdx,0x1
     b58:	48 83 fa 04          	cmp    rdx,0x4
     b5c:	75 ec                	jne    b4a <_ZN12_GLOBAL__N_1L3runEj+0x84a>
     b5e:	8b 94 24 a0 01 00 00 	mov    edx,DWORD PTR [rsp+0x1a0]
     b65:	41 b9 00 00 00 02    	mov    r9d,0x2000000
     b6b:	41 b8 c1 00 00 00    	mov    r8d,0xc1
     b71:	48 8d 0d 70 00 00 00 	lea    rcx,[rip+0x70]        # be8 <_ZN12_GLOBAL__N_1L3runEj+0x8e8>
     b78:	e8 00 00 00 00       	call   b7d <_ZN12_GLOBAL__N_1L3runEj+0x87d>
     b7d:	48 89 ea             	mov    rdx,rbp
     b80:	48 89 d9             	mov    rcx,rbx
     b83:	e8 98 f5 ff ff       	call   120 <_ZNSt12_Vector_baseIjSaIjEED2Ev.isra.0>
     b88:	48 8b 8c 24 30 01 00 	mov    rcx,QWORD PTR [rsp+0x130]
     b8f:	00 
     b90:	e8 4b f7 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     b95:	48 8b 8c 24 10 01 00 	mov    rcx,QWORD PTR [rsp+0x110]
     b9c:	00 
     b9d:	e8 3e f7 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     ba2:	48 8b 8c 24 f0 00 00 	mov    rcx,QWORD PTR [rsp+0xf0]
     ba9:	00 
     baa:	e8 31 f7 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     baf:	48 8b 8c 24 d0 00 00 	mov    rcx,QWORD PTR [rsp+0xd0]
     bb6:	00 
     bb7:	e8 24 f7 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     bbc:	48 8b 8c 24 b0 00 00 	mov    rcx,QWORD PTR [rsp+0xb0]
     bc3:	00 
     bc4:	e8 17 f7 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     bc9:	90                   	nop
     bca:	48 81 c4 58 01 00 00 	add    rsp,0x158
     bd1:	5b                   	pop    rbx
     bd2:	5e                   	pop    rsi
     bd3:	5f                   	pop    rdi
     bd4:	5d                   	pop    rbp
     bd5:	41 5c                	pop    r12
     bd7:	41 5d                	pop    r13
     bd9:	41 5e                	pop    r14
     bdb:	41 5f                	pop    r15
     bdd:	c3                   	ret
     bde:	48 8b 7c 24 48       	mov    rdi,QWORD PTR [rsp+0x48]
     be3:	8d 48 ff             	lea    ecx,[rax-0x1]
     be6:	89 c2                	mov    edx,eax
     be8:	31 c0                	xor    eax,eax
     bea:	c1 e9 03             	shr    ecx,0x3
     bed:	48 c7 44 17 f8 00 00 	mov    QWORD PTR [rdi+rdx*1-0x8],0x0
     bf4:	00 00 
     bf6:	f3 48 ab             	rep stos QWORD PTR [rdi],rax
     bf9:	e9 a6 fb ff ff       	jmp    7a4 <_ZN12_GLOBAL__N_1L3runEj+0x4a4>
     bfe:	48 8b bc 24 88 00 00 	mov    rdi,QWORD PTR [rsp+0x88]
     c05:	00 
     c06:	4d 89 c1             	mov    r9,r8
     c09:	49 89 d0             	mov    r8,rdx
     c0c:	48 c7 44 24 20 00 10 	mov    QWORD PTR [rsp+0x20],0x1000
     c13:	00 00 
     c15:	48 89 fa             	mov    rdx,rdi
     c18:	e8 00 00 00 00       	call   c1d <_ZN12_GLOBAL__N_1L3runEj+0x91d>
     c1d:	4c 8b 84 24 38 01 00 	mov    r8,QWORD PTR [rsp+0x138]
     c24:	00 
     c25:	48 89 fa             	mov    rdx,rdi
     c28:	48 c7 44 24 20 00 10 	mov    QWORD PTR [rsp+0x20],0x1000
     c2f:	00 00 
     c31:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     c38:	00 
     c39:	4d 89 c1             	mov    r9,r8
     c3c:	e8 00 00 00 00       	call   c41 <_ZN12_GLOBAL__N_1L3runEj+0x941>
     c41:	e9 5e fe ff ff       	jmp    aa4 <_ZN12_GLOBAL__N_1L3runEj+0x7a4>
     c46:	48 8b 94 24 88 00 00 	mov    rdx,QWORD PTR [rsp+0x88]
     c4d:	00 
     c4e:	4d 89 e1             	mov    r9,r12
     c51:	49 89 e8             	mov    r8,rbp
     c54:	4c 89 74 24 20       	mov    QWORD PTR [rsp+0x20],r14
     c59:	e8 00 00 00 00       	call   c5e <_ZN12_GLOBAL__N_1L3runEj+0x95e>
     c5e:	4c 89 74 24 20       	mov    QWORD PTR [rsp+0x20],r14
     c63:	49 89 f1             	mov    r9,rsi
     c66:	49 89 f0             	mov    r8,rsi
     c69:	48 8b 94 24 88 00 00 	mov    rdx,QWORD PTR [rsp+0x88]
     c70:	00 
     c71:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     c78:	00 
     c79:	e8 00 00 00 00       	call   c7e <_ZN12_GLOBAL__N_1L3runEj+0x97e>
     c7e:	e9 09 fc ff ff       	jmp    88c <_ZN12_GLOBAL__N_1L3runEj+0x58c>
     c83:	48 8b bc 24 88 00 00 	mov    rdi,QWORD PTR [rsp+0x88]
     c8a:	00 
     c8b:	4d 89 c1             	mov    r9,r8
     c8e:	49 89 d0             	mov    r8,rdx
     c91:	48 c7 44 24 20 00 10 	mov    QWORD PTR [rsp+0x20],0x1000
     c98:	00 00 
     c9a:	48 89 fa             	mov    rdx,rdi
     c9d:	e8 00 00 00 00       	call   ca2 <_ZN12_GLOBAL__N_1L3runEj+0x9a2>
     ca2:	4c 8b 84 24 38 01 00 	mov    r8,QWORD PTR [rsp+0x138]
     ca9:	00 
     caa:	48 89 fa             	mov    rdx,rdi
     cad:	48 c7 44 24 20 00 10 	mov    QWORD PTR [rsp+0x20],0x1000
     cb4:	00 00 
     cb6:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     cbd:	00 
     cbe:	4d 89 c1             	mov    r9,r8
     cc1:	e8 00 00 00 00       	call   cc6 <_ZN12_GLOBAL__N_1L3runEj+0x9c6>
     cc6:	e9 d9 fd ff ff       	jmp    aa4 <_ZN12_GLOBAL__N_1L3runEj+0x7a4>
     ccb:	48 8b 94 24 88 00 00 	mov    rdx,QWORD PTR [rsp+0x88]
     cd2:	00 
     cd3:	4d 89 e1             	mov    r9,r12
     cd6:	49 89 e8             	mov    r8,rbp
     cd9:	4c 89 74 24 20       	mov    QWORD PTR [rsp+0x20],r14
     cde:	e8 00 00 00 00       	call   ce3 <_ZN12_GLOBAL__N_1L3runEj+0x9e3>
     ce3:	4c 89 74 24 20       	mov    QWORD PTR [rsp+0x20],r14
     ce8:	49 89 f1             	mov    r9,rsi
     ceb:	49 89 f0             	mov    r8,rsi
     cee:	48 8b 94 24 88 00 00 	mov    rdx,QWORD PTR [rsp+0x88]
     cf5:	00 
     cf6:	48 8b 8c 24 b8 00 00 	mov    rcx,QWORD PTR [rsp+0xb8]
     cfd:	00 
     cfe:	e8 00 00 00 00       	call   d03 <_ZN12_GLOBAL__N_1L3runEj+0xa03>
     d03:	e9 84 fb ff ff       	jmp    88c <_ZN12_GLOBAL__N_1L3runEj+0x58c>
     d08:	41 c7 47 04 00 00 00 	mov    DWORD PTR [r15+0x4],0x0
     d0f:	00 
     d10:	48 8b 7c 24 48       	mov    rdi,QWORD PTR [rsp+0x48]
     d15:	89 c0                	mov    eax,eax
     d17:	c7 44 07 fc 00 00 00 	mov    DWORD PTR [rdi+rax*1-0x4],0x0
     d1e:	00 
     d1f:	e9 80 fa ff ff       	jmp    7a4 <_ZN12_GLOBAL__N_1L3runEj+0x4a4>
     d24:	31 c0                	xor    eax,eax
     d26:	45 31 c9             	xor    r9d,r9d
     d29:	45 31 c0             	xor    r8d,r8d
     d2c:	48 89 44 24 20       	mov    QWORD PTR [rsp+0x20],rax
     d31:	31 d2                	xor    edx,edx
     d33:	31 c9                	xor    ecx,ecx
     d35:	e8 00 00 00 00       	call   d3a <_ZN12_GLOBAL__N_1L3runEj+0xa3a>
     d3a:	e9 a1 f7 ff ff       	jmp    4e0 <_ZN12_GLOBAL__N_1L3runEj+0x1e0>
     d3f:	31 d2                	xor    edx,edx
     d41:	45 31 c9             	xor    r9d,r9d
     d44:	45 31 c0             	xor    r8d,r8d
     d47:	48 89 54 24 20       	mov    QWORD PTR [rsp+0x20],rdx
     d4c:	31 c9                	xor    ecx,ecx
     d4e:	31 d2                	xor    edx,edx
     d50:	e8 00 00 00 00       	call   d55 <_ZN12_GLOBAL__N_1L3runEj+0xa55>
     d55:	e9 86 f7 ff ff       	jmp    4e0 <_ZN12_GLOBAL__N_1L3runEj+0x1e0>
     d5a:	48 8b 84 24 90 00 00 	mov    rax,QWORD PTR [rsp+0x90]
     d61:	00 
     d62:	48 03 84 24 b8 00 00 	add    rax,QWORD PTR [rsp+0xb8]
     d69:	00 
     d6a:	c7 00 5a 5a 5a 5a    	mov    DWORD PTR [rax],0x5a5a5a5a
     d70:	e9 40 f7 ff ff       	jmp    4b5 <_ZN12_GLOBAL__N_1L3runEj+0x1b5>
     d75:	ba 04 00 00 02       	mov    edx,0x2000004
     d7a:	e8 81 f2 ff ff       	call   0 <_ZN12_GLOBAL__N_17GuardedC1Ey>
     d7f:	48 c7 84 24 90 00 00 	mov    QWORD PTR [rsp+0x90],0x2000000
     d86:	00 00 00 00 02 
     d8b:	e9 bb f5 ff ff       	jmp    34b <_ZN12_GLOBAL__N_1L3runEj+0x4b>
     d90:	48 89 c3             	mov    rbx,rax
     d93:	48 8b 8c 24 b0 00 00 	mov    rcx,QWORD PTR [rsp+0xb0]
     d9a:	00 
     d9b:	e8 40 f5 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     da0:	48 89 d9             	mov    rcx,rbx
     da3:	e8 00 00 00 00       	call   da8 <_ZN12_GLOBAL__N_1L3runEj+0xaa8>
     da8:	48 89 c3             	mov    rbx,rax
     dab:	48 8b 8c 24 d0 00 00 	mov    rcx,QWORD PTR [rsp+0xd0]
     db2:	00 
     db3:	e8 28 f5 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     db8:	eb d9                	jmp    d93 <_ZN12_GLOBAL__N_1L3runEj+0xa93>
     dba:	b9 10 00 00 00       	mov    ecx,0x10
     dbf:	e8 00 00 00 00       	call   dc4 <_ZN12_GLOBAL__N_1L3runEj+0xac4>
     dc4:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # dcb <_ZN12_GLOBAL__N_1L3runEj+0xacb>
     dcb:	48 89 c1             	mov    rcx,rax
     dce:	48 89 c6             	mov    rsi,rax
     dd1:	e8 00 00 00 00       	call   dd6 <_ZN12_GLOBAL__N_1L3runEj+0xad6>
     dd6:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # ddd <_ZN12_GLOBAL__N_1L3runEj+0xadd>
     ddd:	48 89 f1             	mov    rcx,rsi
     de0:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # de7 <_ZN12_GLOBAL__N_1L3runEj+0xae7>
     de7:	e8 00 00 00 00       	call   dec <_ZN12_GLOBAL__N_1L3runEj+0xaec>
     dec:	48 89 f1             	mov    rcx,rsi
     def:	48 89 c3             	mov    rbx,rax
     df2:	e8 00 00 00 00       	call   df7 <_ZN12_GLOBAL__N_1L3runEj+0xaf7>
     df7:	eb b2                	jmp    dab <_ZN12_GLOBAL__N_1L3runEj+0xaab>
     df9:	48 89 c3             	mov    rbx,rax
     dfc:	48 8b 4c 24 58       	mov    rcx,QWORD PTR [rsp+0x58]
     e01:	e8 da f4 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     e06:	eb a3                	jmp    dab <_ZN12_GLOBAL__N_1L3runEj+0xaab>
     e08:	b9 10 00 00 00       	mov    ecx,0x10
     e0d:	e8 00 00 00 00       	call   e12 <_ZN12_GLOBAL__N_1L3runEj+0xb12>
     e12:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # e19 <_ZN12_GLOBAL__N_1L3runEj+0xb19>
     e19:	48 89 c1             	mov    rcx,rax
     e1c:	48 89 c6             	mov    rsi,rax
     e1f:	e8 00 00 00 00       	call   e24 <_ZN12_GLOBAL__N_1L3runEj+0xb24>
     e24:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # e2b <_ZN12_GLOBAL__N_1L3runEj+0xb2b>
     e2b:	48 89 f1             	mov    rcx,rsi
     e2e:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # e35 <_ZN12_GLOBAL__N_1L3runEj+0xb35>
     e35:	e8 00 00 00 00       	call   e3a <_ZN12_GLOBAL__N_1L3runEj+0xb3a>
     e3a:	48 89 f1             	mov    rcx,rsi
     e3d:	48 89 c3             	mov    rbx,rax
     e40:	e8 00 00 00 00       	call   e45 <_ZN12_GLOBAL__N_1L3runEj+0xb45>
     e45:	eb b5                	jmp    dfc <_ZN12_GLOBAL__N_1L3runEj+0xafc>
     e47:	48 89 c3             	mov    rbx,rax
     e4a:	48 8b 4c 24 60       	mov    rcx,QWORD PTR [rsp+0x60]
     e4f:	e8 8c f4 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     e54:	eb a6                	jmp    dfc <_ZN12_GLOBAL__N_1L3runEj+0xafc>
     e56:	b9 10 00 00 00       	mov    ecx,0x10
     e5b:	e8 00 00 00 00       	call   e60 <_ZN12_GLOBAL__N_1L3runEj+0xb60>
     e60:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # e67 <_ZN12_GLOBAL__N_1L3runEj+0xb67>
     e67:	48 89 c1             	mov    rcx,rax
     e6a:	48 89 c6             	mov    rsi,rax
     e6d:	e8 00 00 00 00       	call   e72 <_ZN12_GLOBAL__N_1L3runEj+0xb72>
     e72:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # e79 <_ZN12_GLOBAL__N_1L3runEj+0xb79>
     e79:	48 89 f1             	mov    rcx,rsi
     e7c:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # e83 <_ZN12_GLOBAL__N_1L3runEj+0xb83>
     e83:	e8 00 00 00 00       	call   e88 <_ZN12_GLOBAL__N_1L3runEj+0xb88>
     e88:	48 89 f1             	mov    rcx,rsi
     e8b:	48 89 c3             	mov    rbx,rax
     e8e:	e8 00 00 00 00       	call   e93 <_ZN12_GLOBAL__N_1L3runEj+0xb93>
     e93:	eb b5                	jmp    e4a <_ZN12_GLOBAL__N_1L3runEj+0xb4a>
     e95:	48 89 c3             	mov    rbx,rax
     e98:	48 8b 4c 24 68       	mov    rcx,QWORD PTR [rsp+0x68]
     e9d:	e8 3e f4 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     ea2:	eb a6                	jmp    e4a <_ZN12_GLOBAL__N_1L3runEj+0xb4a>
     ea4:	48 89 c3             	mov    rbx,rax
     ea7:	48 8b 94 24 80 00 00 	mov    rdx,QWORD PTR [rsp+0x80]
     eae:	00 
     eaf:	4c 89 f9             	mov    rcx,r15
     eb2:	e8 69 f2 ff ff       	call   120 <_ZNSt12_Vector_baseIjSaIjEED2Ev.isra.0>
     eb7:	eb df                	jmp    e98 <_ZN12_GLOBAL__N_1L3runEj+0xb98>
     eb9:	48 89 c3             	mov    rbx,rax
     ebc:	48 8b 54 24 38       	mov    rdx,QWORD PTR [rsp+0x38]
     ec1:	48 89 f9             	mov    rcx,rdi
     ec4:	e8 00 00 00 00       	call   ec9 <_ZN12_GLOBAL__N_1L3runEj+0xbc9>
     ec9:	eb dc                	jmp    ea7 <_ZN12_GLOBAL__N_1L3runEj+0xba7>
     ecb:	b9 10 00 00 00       	mov    ecx,0x10
     ed0:	e8 00 00 00 00       	call   ed5 <_ZN12_GLOBAL__N_1L3runEj+0xbd5>
     ed5:	48 8d 15 42 00 00 00 	lea    rdx,[rip+0x42]        # f1e <_ZN12_GLOBAL__N_1L3runEj+0xc1e>
     edc:	48 89 c1             	mov    rcx,rax
     edf:	48 89 c6             	mov    rsi,rax
     ee2:	e8 00 00 00 00       	call   ee7 <_ZN12_GLOBAL__N_1L3runEj+0xbe7>
     ee7:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # eee <_ZN12_GLOBAL__N_1L3runEj+0xbee>
     eee:	48 89 f1             	mov    rcx,rsi
     ef1:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # ef8 <_ZN12_GLOBAL__N_1L3runEj+0xbf8>
     ef8:	e8 00 00 00 00       	call   efd <_ZN12_GLOBAL__N_1L3runEj+0xbfd>
     efd:	48 89 f1             	mov    rcx,rsi
     f00:	48 89 c3             	mov    rbx,rax
     f03:	e8 00 00 00 00       	call   f08 <_ZN12_GLOBAL__N_1L3runEj+0xc08>
     f08:	eb b2                	jmp    ebc <_ZN12_GLOBAL__N_1L3runEj+0xbbc>
     f0a:	b9 10 00 00 00       	mov    ecx,0x10
     f0f:	e8 00 00 00 00       	call   f14 <_ZN12_GLOBAL__N_1L3runEj+0xc14>
     f14:	48 8d 15 32 00 00 00 	lea    rdx,[rip+0x32]        # f4d <_ZN12_GLOBAL__N_1L3runEj+0xc4d>
     f1b:	48 89 c1             	mov    rcx,rax
     f1e:	48 89 c6             	mov    rsi,rax
     f21:	e8 00 00 00 00       	call   f26 <_ZN12_GLOBAL__N_1L3runEj+0xc26>
     f26:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # f2d <_ZN12_GLOBAL__N_1L3runEj+0xc2d>
     f2d:	48 89 f1             	mov    rcx,rsi
     f30:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # f37 <_ZN12_GLOBAL__N_1L3runEj+0xc37>
     f37:	e8 00 00 00 00       	call   f3c <_ZN12_GLOBAL__N_1L3runEj+0xc3c>
     f3c:	48 89 c3             	mov    rbx,rax
     f3f:	48 8b 8c 24 10 01 00 	mov    rcx,QWORD PTR [rsp+0x110]
     f46:	00 
     f47:	e8 94 f3 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     f4c:	48 8b 8c 24 f0 00 00 	mov    rcx,QWORD PTR [rsp+0xf0]
     f53:	00 
     f54:	e8 87 f3 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     f59:	e9 4d fe ff ff       	jmp    dab <_ZN12_GLOBAL__N_1L3runEj+0xaab>
     f5e:	b9 10 00 00 00       	mov    ecx,0x10
     f63:	e8 00 00 00 00       	call   f68 <_ZN12_GLOBAL__N_1L3runEj+0xc68>
     f68:	48 8d 15 32 00 00 00 	lea    rdx,[rip+0x32]        # fa1 <_ZN12_GLOBAL__N_1L3runEj+0xca1>
     f6f:	48 89 c1             	mov    rcx,rax
     f72:	48 89 c6             	mov    rsi,rax
     f75:	e8 00 00 00 00       	call   f7a <_ZN12_GLOBAL__N_1L3runEj+0xc7a>
     f7a:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # f81 <_ZN12_GLOBAL__N_1L3runEj+0xc81>
     f81:	48 89 f1             	mov    rcx,rsi
     f84:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # f8b <_ZN12_GLOBAL__N_1L3runEj+0xc8b>
     f8b:	e8 00 00 00 00       	call   f90 <_ZN12_GLOBAL__N_1L3runEj+0xc90>
     f90:	48 89 c6             	mov    rsi,rax
     f93:	48 89 d9             	mov    rcx,rbx
     f96:	48 89 ea             	mov    rdx,rbp
     f99:	48 89 f3             	mov    rbx,rsi
     f9c:	e8 7f f1 ff ff       	call   120 <_ZNSt12_Vector_baseIjSaIjEED2Ev.isra.0>
     fa1:	48 8b 8c 24 30 01 00 	mov    rcx,QWORD PTR [rsp+0x130]
     fa8:	00 
     fa9:	e8 32 f3 ff ff       	call   2e0 <_ZN12_GLOBAL__N_17GuardedD2Ev.isra.0>
     fae:	eb 8f                	jmp    f3f <_ZN12_GLOBAL__N_1L3runEj+0xc3f>
     fb0:	b9 10 00 00 00       	mov    ecx,0x10
     fb5:	e8 00 00 00 00       	call   fba <_ZN12_GLOBAL__N_1L3runEj+0xcba>
     fba:	48 8d 15 32 00 00 00 	lea    rdx,[rip+0x32]        # ff3 <_ZN12_GLOBAL__N_1L3runEj+0xcf3>
     fc1:	48 89 c1             	mov    rcx,rax
     fc4:	48 89 c6             	mov    rsi,rax
     fc7:	e8 00 00 00 00       	call   fcc <_ZN12_GLOBAL__N_1L3runEj+0xccc>
     fcc:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # fd3 <_ZN12_GLOBAL__N_1L3runEj+0xcd3>
     fd3:	48 89 f1             	mov    rcx,rsi
     fd6:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # fdd <_ZN12_GLOBAL__N_1L3runEj+0xcdd>
     fdd:	e8 00 00 00 00       	call   fe2 <_ZN12_GLOBAL__N_1L3runEj+0xce2>
     fe2:	48 89 c3             	mov    rbx,rax
     fe5:	eb ba                	jmp    fa1 <_ZN12_GLOBAL__N_1L3runEj+0xca1>
     fe7:	48 89 c3             	mov    rbx,rax
     fea:	e9 5d ff ff ff       	jmp    f4c <_ZN12_GLOBAL__N_1L3runEj+0xc4c>
     fef:	b9 10 00 00 00       	mov    ecx,0x10
     ff4:	e8 00 00 00 00       	call   ff9 <_ZN12_GLOBAL__N_1L3runEj+0xcf9>
     ff9:	48 8d 15 58 00 00 00 	lea    rdx,[rip+0x58]        # 1058 <_ZN12_GLOBAL__N_1L3runEj+0xd58>
    1000:	48 89 c1             	mov    rcx,rax
    1003:	48 89 c7             	mov    rdi,rax
    1006:	e8 00 00 00 00       	call   100b <_ZN12_GLOBAL__N_1L3runEj+0xd0b>
    100b:	4c 8d 05 00 00 00 00 	lea    r8,[rip+0x0]        # 1012 <_ZN12_GLOBAL__N_1L3runEj+0xd12>
    1012:	48 89 f9             	mov    rcx,rdi
    1015:	48 8d 15 00 00 00 00 	lea    rdx,[rip+0x0]        # 101c <_ZN12_GLOBAL__N_1L3runEj+0xd1c>
    101c:	e8 00 00 00 00       	call   1021 <_ZN12_GLOBAL__N_1L3runEj+0xd21>
    1021:	e9 d7 fe ff ff       	jmp    efd <_ZN12_GLOBAL__N_1L3runEj+0xbfd>
    1026:	e9 d2 fe ff ff       	jmp    efd <_ZN12_GLOBAL__N_1L3runEj+0xbfd>
    102b:	e9 cd fe ff ff       	jmp    efd <_ZN12_GLOBAL__N_1L3runEj+0xbfd>
    1030:	48 89 f9             	mov    rcx,rdi
    1033:	48 89 c6             	mov    rsi,rax
    1036:	e8 00 00 00 00       	call   103b <_ZN12_GLOBAL__N_1L3runEj+0xd3b>
    103b:	e9 53 ff ff ff       	jmp    f93 <_ZN12_GLOBAL__N_1L3runEj+0xc93>

Disassembly of section .text.startup:

0000000000000000 <main>:
   0:	53                   	push   rbx
   1:	48 83 ec 30          	sub    rsp,0x30
   5:	e8 00 00 00 00       	call   a <main+0xa>
   a:	31 c0                	xor    eax,eax
   c:	0f a2                	cpuid
   e:	83 f8 06             	cmp    eax,0x6
  11:	76 13                	jbe    26 <main+0x26>
  13:	b8 01 00 00 00       	mov    eax,0x1
  18:	31 c9                	xor    ecx,ecx
  1a:	0f a2                	cpuid
  1c:	f7 d1                	not    ecx
  1e:	81 e1 00 00 00 1c    	and    ecx,0x1c000000
  24:	74 25                	je     4b <main+0x4b>
  26:	48 8d 0d b9 00 00 00 	lea    rcx,[rip+0xb9]        # e6 <main+0xe6>
  2d:	31 d2                	xor    edx,edx
  2f:	e8 00 00 00 00       	call   34 <main+0x34>
  34:	48 8d 0d d8 00 00 00 	lea    rcx,[rip+0xd8]        # 113 <main+0x113>
  3b:	e8 00 00 00 00       	call   40 <main+0x40>
  40:	b8 4d 00 00 00       	mov    eax,0x4d
  45:	48 83 c4 30          	add    rsp,0x30
  49:	5b                   	pop    rbx
  4a:	c3                   	ret
  4b:	31 c9                	xor    ecx,ecx
  4d:	0f 01 d0             	xgetbv
  50:	f7 d0                	not    eax
  52:	a8 e6                	test   al,0xe6
  54:	75 d0                	jne    26 <main+0x26>
  56:	b8 07 00 00 00       	mov    eax,0x7
  5b:	0f a2                	cpuid
  5d:	48 8d 0d b9 00 00 00 	lea    rcx,[rip+0xb9]        # 11d <main+0x11d>
  64:	41 89 d8             	mov    r8d,ebx
  67:	41 81 e0 20 00 03 c0 	and    r8d,0xc0030020
  6e:	41 81 f8 20 00 03 c0 	cmp    r8d,0xc0030020
  75:	44 89 44 24 28       	mov    DWORD PTR [rsp+0x28],r8d
  7a:	0f 94 c2             	sete   dl
  7d:	0f b6 d2             	movzx  edx,dl
  80:	e8 00 00 00 00       	call   85 <main+0x85>
  85:	81 7c 24 28 20 00 03 	cmp    DWORD PTR [rsp+0x28],0xc0030020
  8c:	c0 
  8d:	75 a5                	jne    34 <main+0x34>
  8f:	b9 08 00 00 00       	mov    ecx,0x8
  94:	e8 00 03 00 00       	call   399 <_ZN12_GLOBAL__N_1L3runEj+0x99>
  99:	b9 10 00 00 00       	mov    ecx,0x10
  9e:	e8 00 03 00 00       	call   3a3 <_ZN12_GLOBAL__N_1L3runEj+0xa3>
  a3:	b9 18 00 00 00       	mov    ecx,0x18
  a8:	e8 00 03 00 00       	call   3ad <_ZN12_GLOBAL__N_1L3runEj+0xad>
  ad:	48 8d 0d 08 01 00 00 	lea    rcx,[rip+0x108]        # 1bc <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x8c>
  b4:	e8 00 00 00 00       	call   b9 <main+0xb9>
  b9:	31 c0                	xor    eax,eax
  bb:	48 83 c4 30          	add    rsp,0x30
  bf:	5b                   	pop    rbx
  c0:	c3                   	ret
  c1:	48 83 ea 01          	sub    rdx,0x1
  c5:	48 89 c1             	mov    rcx,rax
  c8:	75 4c                	jne    116 <main+0x116>
  ca:	e8 00 00 00 00       	call   cf <main+0xcf>
  cf:	48 8b 10             	mov    rdx,QWORD PTR [rax]
  d2:	48 89 c1             	mov    rcx,rax
  d5:	ff 52 10             	call   QWORD PTR [rdx+0x10]
  d8:	b9 02 00 00 00       	mov    ecx,0x2
  dd:	48 89 44 24 28       	mov    QWORD PTR [rsp+0x28],rax
  e2:	ff 15 00 00 00 00    	call   QWORD PTR [rip+0x0]        # e8 <main+0xe8>
  e8:	4c 8b 44 24 28       	mov    r8,QWORD PTR [rsp+0x28]
  ed:	48 8d 15 4d 01 00 00 	lea    rdx,[rip+0x14d]        # 241 <_ZN12_GLOBAL__N_1L6verifyEjPKhRKSt6vectorIjSaIjEE.isra.0+0x111>
  f4:	48 89 c1             	mov    rcx,rax
  f7:	e8 00 00 00 00       	call   fc <main+0xfc>
  fc:	e8 00 00 00 00       	call   101 <main+0x101>
 101:	b8 01 00 00 00       	mov    eax,0x1
 106:	e9 3a ff ff ff       	jmp    45 <main+0x45>
 10b:	48 89 c3             	mov    rbx,rax
 10e:	e8 00 00 00 00       	call   113 <main+0x113>
 113:	48 89 d9             	mov    rcx,rbx
 116:	e8 00 00 00 00       	call   11b <main+0x11b>
 11b:	90                   	nop
 11c:	90                   	nop
 11d:	90                   	nop
 11e:	90                   	nop
 11f:	90                   	nop
