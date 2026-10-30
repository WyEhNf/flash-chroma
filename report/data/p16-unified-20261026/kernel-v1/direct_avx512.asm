
artifacts/p16-unified-avx512-kernel/direct_avx512.o:     file format pe-x86-64


Disassembly of section .text:

0000000000000000 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy>:
   0:	57                   	push   rdi
   1:	56                   	push   rsi
   2:	53                   	push   rbx
   3:	48 8b 74 24 40       	mov    rsi,QWORD PTR [rsp+0x40]
   8:	49 89 d2             	mov    r10,rdx
   b:	4c 89 c3             	mov    rbx,r8
   e:	48 83 fe 0f          	cmp    rsi,0xf
  12:	0f 86 58 01 00 00    	jbe    170 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x170>
  18:	4c 89 c2             	mov    rdx,r8
  1b:	4c 8d 46 f0          	lea    r8,[rsi-0x10]
  1f:	c5 e1 ef db          	vpxor  xmm3,xmm3,xmm3
  23:	62 e1 7d 48 6f 15 00 	vmovdqa32 zmm18,ZMMWORD PTR [rip+0x0]        # 2d <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x2d>
  2a:	00 00 00 
  2d:	4d 89 c3             	mov    r11,r8
  30:	62 f3 65 48 25 db ff 	vpternlogd zmm3,zmm3,zmm3,0xff
  37:	62 e1 7d 48 6f 0d 80 	vmovdqa32 zmm17,ZMMWORD PTR [rip+0x80]        # c1 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0xc1>
  3e:	00 00 00 
  41:	62 e2 7d 48 5a 05 40 	vbroadcasti32x4 zmm16,XMMWORD PTR [rip+0x40]        # 8b <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x8b>
  48:	00 00 00 
  4b:	49 c1 eb 04          	shr    r11,0x4
  4f:	62 f2 7d 48 5a 25 50 	vbroadcasti32x4 zmm4,XMMWORD PTR [rip+0x50]        # a9 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0xa9>
  56:	00 00 00 
  59:	48 bf ff ff ff ff ff 	movabs rdi,0xffffffffffff
  60:	ff 00 00 
  63:	4c 89 c8             	mov    rax,r9
  66:	4f 8d 1c 5b          	lea    r11,[r11+r11*2]
  6a:	62 f1 55 48 72 d3 1e 	vpsrld zmm5,zmm3,0x1e
  71:	c4 e1 fb 92 d7       	kmovq  k2,rdi
  76:	c5 f4 46 c9          	kxnorw k1,k1,k1
  7a:	49 c1 e3 04          	shl    r11,0x4
  7e:	62 f1 65 48 72 d3 18 	vpsrld zmm3,zmm3,0x18
  85:	4e 8d 5c 1b 30       	lea    r11,[rbx+r11*1+0x30]
  8a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  90:	62 f1 7f ca 6f 02    	vmovdqu8 zmm0{k2}{z},ZMMWORD PTR [rdx]
  96:	c5 f8 90 d9          	kmovw  k3,k1
  9a:	c5 f8 90 e1          	kmovw  k4,k1
  9e:	48 83 c2 30          	add    rdx,0x30
  a2:	62 f2 6d 40 36 c0    	vpermd zmm0,zmm18,zmm0
  a8:	62 b2 7d 48 00 c0    	vpshufb zmm0,zmm0,zmm16
  ae:	62 f1 6d 48 72 d0 02 	vpsrld zmm2,zmm0,0x2
  b5:	62 f1 7d 48 db c5    	vpandd zmm0,zmm0,zmm5
  bb:	62 f2 7d 4b 90 0c 91 	vpgatherdd zmm1{k3},DWORD PTR [rcx+zmm2*4]
  c2:	62 f1 7d 48 72 f0 03 	vpslld zmm0,zmm0,0x3
  c9:	62 f2 75 48 45 c8    	vpsrlvd zmm1,zmm1,zmm0
  cf:	62 f1 75 48 db cb    	vpandd zmm1,zmm1,zmm3
  d5:	62 d2 7d 4c 90 04 8a 	vpgatherdd zmm0{k4},DWORD PTR [r10+zmm1*4]
  dc:	62 f2 7d 48 00 c4    	vpshufb zmm0,zmm0,zmm4
  e2:	62 f2 75 40 36 c0    	vpermd zmm0,zmm17,zmm0
  e8:	62 f1 7f 4a 7f 00    	vmovdqu8 ZMMWORD PTR [rax]{k2},zmm0
  ee:	48 83 c0 30          	add    rax,0x30
  f2:	4c 39 da             	cmp    rdx,r11
  f5:	75 99                	jne    90 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x90>
  f7:	49 83 e0 f0          	and    r8,0xfffffffffffffff0
  fb:	49 8d 40 10          	lea    rax,[r8+0x10]
  ff:	c5 f8 77             	vzeroupper
 102:	48 39 f0             	cmp    rax,rsi
 105:	73 5c                	jae    163 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x163>
 107:	48 8d 04 40          	lea    rax,[rax+rax*2]
 10b:	4c 8d 04 76          	lea    r8,[rsi+rsi*2]
 10f:	48 8d 14 03          	lea    rdx,[rbx+rax*1]
 113:	49 01 c1             	add    r9,rax
 116:	49 01 d8             	add    r8,rbx
 119:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
 120:	0f b6 42 01          	movzx  eax,BYTE PTR [rdx+0x1]
 124:	44 0f b6 5a 02       	movzx  r11d,BYTE PTR [rdx+0x2]
 129:	48 83 c2 03          	add    rdx,0x3
 12d:	49 83 c1 03          	add    r9,0x3
 131:	41 c1 e3 10          	shl    r11d,0x10
 135:	c1 e0 08             	shl    eax,0x8
 138:	44 09 d8             	or     eax,r11d
 13b:	44 0f b6 5a fd       	movzx  r11d,BYTE PTR [rdx-0x3]
 140:	44 09 d8             	or     eax,r11d
 143:	0f b6 04 01          	movzx  eax,BYTE PTR [rcx+rax*1]
 147:	4d 8d 1c 82          	lea    r11,[r10+rax*4]
 14b:	41 8b 03             	mov    eax,DWORD PTR [r11]
 14e:	45 0f b7 1b          	movzx  r11d,WORD PTR [r11]
 152:	c1 e8 10             	shr    eax,0x10
 155:	66 45 89 59 fd       	mov    WORD PTR [r9-0x3],r11w
 15a:	41 88 41 ff          	mov    BYTE PTR [r9-0x1],al
 15e:	4c 39 c2             	cmp    rdx,r8
 161:	75 bd                	jne    120 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x120>
 163:	5b                   	pop    rbx
 164:	5e                   	pop    rsi
 165:	5f                   	pop    rdi
 166:	c3                   	ret
 167:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
 16e:	00 00 
 170:	31 c0                	xor    eax,eax
 172:	eb 8e                	jmp    102 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x102>
 174:	90                   	nop
 175:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 17c:	00 00 00 00 

0000000000000180 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy>:
 180:	57                   	push   rdi
 181:	56                   	push   rsi
 182:	53                   	push   rbx
 183:	48 8b 74 24 40       	mov    rsi,QWORD PTR [rsp+0x40]
 188:	49 89 ca             	mov    r10,rcx
 18b:	49 89 d3             	mov    r11,rdx
 18e:	4c 89 c3             	mov    rbx,r8
 191:	48 83 fe 0f          	cmp    rsi,0xf
 195:	0f 86 2d 01 00 00    	jbe    2c8 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x148>
 19b:	4c 89 c2             	mov    rdx,r8
 19e:	4c 8d 46 f0          	lea    r8,[rsi-0x10]
 1a2:	c5 e9 ef d2          	vpxor  xmm2,xmm2,xmm2
 1a6:	62 e1 7d 48 6f 05 00 	vmovdqa32 zmm16,ZMMWORD PTR [rip+0x0]        # 1b0 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x30>
 1ad:	00 00 00 
 1b0:	4c 89 c1             	mov    rcx,r8
 1b3:	62 f3 6d 48 25 d2 ff 	vpternlogd zmm2,zmm2,zmm2,0xff
 1ba:	62 f1 7d 48 6f 2d 80 	vmovdqa32 zmm5,ZMMWORD PTR [rip+0x80]        # 244 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0xc4>
 1c1:	00 00 00 
 1c4:	62 f2 7d 48 5a 25 40 	vbroadcasti32x4 zmm4,XMMWORD PTR [rip+0x40]        # 20e <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x8e>
 1cb:	00 00 00 
 1ce:	48 c1 e9 04          	shr    rcx,0x4
 1d2:	62 f2 7d 48 5a 1d 50 	vbroadcasti32x4 zmm3,XMMWORD PTR [rip+0x50]        # 22c <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0xac>
 1d9:	00 00 00 
 1dc:	48 bf ff ff ff ff ff 	movabs rdi,0xffffffffffff
 1e3:	ff 00 00 
 1e6:	4c 89 c8             	mov    rax,r9
 1e9:	48 8d 0c 49          	lea    rcx,[rcx+rcx*2]
 1ed:	62 f1 6d 48 72 d2 10 	vpsrld zmm2,zmm2,0x10
 1f4:	c4 e1 fb 92 d7       	kmovq  k2,rdi
 1f9:	c5 f4 46 c9          	kxnorw k1,k1,k1
 1fd:	48 c1 e1 04          	shl    rcx,0x4
 201:	48 8d 4c 0b 30       	lea    rcx,[rbx+rcx*1+0x30]
 206:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
 20d:	00 00 00 
 210:	62 f1 7f ca 6f 02    	vmovdqu8 zmm0{k2}{z},ZMMWORD PTR [rdx]
 216:	c5 f8 90 d9          	kmovw  k3,k1
 21a:	c5 f8 90 e1          	kmovw  k4,k1
 21e:	48 83 c2 30          	add    rdx,0x30
 222:	62 f2 7d 40 36 c0    	vpermd zmm0,zmm16,zmm0
 228:	62 f2 7d 48 00 c4    	vpshufb zmm0,zmm0,zmm4
 22e:	62 d2 7d 4b 90 0c 42 	vpgatherdd zmm1{k3},DWORD PTR [r10+zmm0*2]
 235:	62 f1 75 48 db ca    	vpandd zmm1,zmm1,zmm2
 23b:	62 d2 7d 4c 90 04 8b 	vpgatherdd zmm0{k4},DWORD PTR [r11+zmm1*4]
 242:	62 f2 7d 48 00 c3    	vpshufb zmm0,zmm0,zmm3
 248:	62 f2 55 48 36 c0    	vpermd zmm0,zmm5,zmm0
 24e:	62 f1 7f 4a 7f 00    	vmovdqu8 ZMMWORD PTR [rax]{k2},zmm0
 254:	48 83 c0 30          	add    rax,0x30
 258:	48 39 ca             	cmp    rdx,rcx
 25b:	75 b3                	jne    210 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x90>
 25d:	49 83 e0 f0          	and    r8,0xfffffffffffffff0
 261:	49 8d 40 10          	lea    rax,[r8+0x10]
 265:	c5 f8 77             	vzeroupper
 268:	48 39 f0             	cmp    rax,rsi
 26b:	73 54                	jae    2c1 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x141>
 26d:	48 8d 04 40          	lea    rax,[rax+rax*2]
 271:	4c 8d 04 76          	lea    r8,[rsi+rsi*2]
 275:	48 8d 14 03          	lea    rdx,[rbx+rax*1]
 279:	49 01 c1             	add    r9,rax
 27c:	49 01 d8             	add    r8,rbx
 27f:	90                   	nop
 280:	0f b6 42 01          	movzx  eax,BYTE PTR [rdx+0x1]
 284:	0f b6 4a 02          	movzx  ecx,BYTE PTR [rdx+0x2]
 288:	48 83 c2 03          	add    rdx,0x3
 28c:	49 83 c1 03          	add    r9,0x3
 290:	c1 e1 10             	shl    ecx,0x10
 293:	c1 e0 08             	shl    eax,0x8
 296:	09 c8                	or     eax,ecx
 298:	0f b6 4a fd          	movzx  ecx,BYTE PTR [rdx-0x3]
 29c:	09 c8                	or     eax,ecx
 29e:	01 c0                	add    eax,eax
 2a0:	89 c0                	mov    eax,eax
 2a2:	41 0f b7 04 02       	movzx  eax,WORD PTR [r10+rax*1]
 2a7:	49 8d 0c 83          	lea    rcx,[r11+rax*4]
 2ab:	8b 01                	mov    eax,DWORD PTR [rcx]
 2ad:	0f b7 09             	movzx  ecx,WORD PTR [rcx]
 2b0:	c1 e8 10             	shr    eax,0x10
 2b3:	66 41 89 49 fd       	mov    WORD PTR [r9-0x3],cx
 2b8:	41 88 41 ff          	mov    BYTE PTR [r9-0x1],al
 2bc:	4c 39 c2             	cmp    rdx,r8
 2bf:	75 bf                	jne    280 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x100>
 2c1:	5b                   	pop    rbx
 2c2:	5e                   	pop    rsi
 2c3:	5f                   	pop    rdi
 2c4:	c3                   	ret
 2c5:	0f 1f 00             	nop    DWORD PTR [rax]
 2c8:	31 c0                	xor    eax,eax
 2ca:	eb 9c                	jmp    268 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0xe8>
 2cc:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]

00000000000002d0 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy>:
 2d0:	56                   	push   rsi
 2d1:	53                   	push   rbx
 2d2:	48 89 d3             	mov    rbx,rdx
 2d5:	49 83 f9 0f          	cmp    r9,0xf
 2d9:	0f 86 21 01 00 00    	jbe    400 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x130>
 2df:	4d 8d 59 f0          	lea    r11,[r9-0x10]
 2e3:	62 f1 7d 48 6f 2d 00 	vmovdqa32 zmm5,ZMMWORD PTR [rip+0x0]        # 2ed <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x1d>
 2ea:	00 00 00 
 2ed:	62 f1 7d 48 6f 25 80 	vmovdqa32 zmm4,ZMMWORD PTR [rip+0x80]        # 377 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0xa7>
 2f4:	00 00 00 
 2f7:	48 be ff ff ff ff ff 	movabs rsi,0xffffffffffff
 2fe:	ff 00 00 
 301:	4d 89 da             	mov    r10,r11
 304:	62 f2 7d 48 5a 1d 40 	vbroadcasti32x4 zmm3,XMMWORD PTR [rip+0x40]        # 34e <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x7e>
 30b:	00 00 00 
 30e:	62 f2 7d 48 5a 15 50 	vbroadcasti32x4 zmm2,XMMWORD PTR [rip+0x50]        # 368 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x98>
 315:	00 00 00 
 318:	4c 89 c0             	mov    rax,r8
 31b:	49 c1 ea 04          	shr    r10,0x4
 31f:	c4 e1 fb 92 ce       	kmovq  k1,rsi
 324:	c5 ec 46 d2          	kxnorw k2,k2,k2
 328:	4f 8d 14 52          	lea    r10,[r10+r10*2]
 32c:	49 c1 e2 04          	shl    r10,0x4
 330:	4e 8d 54 12 30       	lea    r10,[rdx+r10*1+0x30]
 335:	0f 1f 00             	nop    DWORD PTR [rax]
 338:	62 f1 7f c9 6f 02    	vmovdqu8 zmm0{k1}{z},ZMMWORD PTR [rdx]
 33e:	c5 f8 90 da          	kmovw  k3,k2
 342:	48 83 c2 30          	add    rdx,0x30
 346:	62 f2 55 48 36 c0    	vpermd zmm0,zmm5,zmm0
 34c:	62 f2 7d 48 00 c3    	vpshufb zmm0,zmm0,zmm3
 352:	62 f1 75 48 72 f0 01 	vpslld zmm1,zmm0,0x1
 359:	62 f1 75 48 fe c8    	vpaddd zmm1,zmm1,zmm0
 35f:	62 f2 7d 4b 90 04 09 	vpgatherdd zmm0{k3},DWORD PTR [rcx+zmm1*1]
 366:	62 f2 7d 48 00 c2    	vpshufb zmm0,zmm0,zmm2
 36c:	62 f2 5d 48 36 c0    	vpermd zmm0,zmm4,zmm0
 372:	62 f1 7f 49 7f 00    	vmovdqu8 ZMMWORD PTR [rax]{k1},zmm0
 378:	48 83 c0 30          	add    rax,0x30
 37c:	49 39 d2             	cmp    r10,rdx
 37f:	75 b7                	jne    338 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x68>
 381:	49 83 e3 f0          	and    r11,0xfffffffffffffff0
 385:	49 8d 43 10          	lea    rax,[r11+0x10]
 389:	c5 f8 77             	vzeroupper
 38c:	4c 39 c8             	cmp    rax,r9
 38f:	73 67                	jae    3f8 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x128>
 391:	48 8d 04 40          	lea    rax,[rax+rax*2]
 395:	4f 8d 0c 49          	lea    r9,[r9+r9*2]
 399:	4c 8d 14 18          	lea    r10,[rax+rbx*1]
 39d:	49 01 c0             	add    r8,rax
 3a0:	49 01 d9             	add    r9,rbx
 3a3:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
 3a8:	41 0f b6 42 01       	movzx  eax,BYTE PTR [r10+0x1]
 3ad:	41 0f b6 52 02       	movzx  edx,BYTE PTR [r10+0x2]
 3b2:	49 83 c2 03          	add    r10,0x3
 3b6:	49 83 c0 03          	add    r8,0x3
 3ba:	c1 e2 10             	shl    edx,0x10
 3bd:	c1 e0 08             	shl    eax,0x8
 3c0:	09 d0                	or     eax,edx
 3c2:	41 0f b6 52 fd       	movzx  edx,BYTE PTR [r10-0x3]
 3c7:	09 d0                	or     eax,edx
 3c9:	8d 14 40             	lea    edx,[rax+rax*2]
 3cc:	48 01 ca             	add    rdx,rcx
 3cf:	0f b6 42 01          	movzx  eax,BYTE PTR [rdx+0x1]
 3d3:	44 0f b6 5a 02       	movzx  r11d,BYTE PTR [rdx+0x2]
 3d8:	0f b6 12             	movzx  edx,BYTE PTR [rdx]
 3db:	c1 e0 08             	shl    eax,0x8
 3de:	41 c1 e3 10          	shl    r11d,0x10
 3e2:	44 09 d8             	or     eax,r11d
 3e5:	09 d0                	or     eax,edx
 3e7:	66 41 89 40 fd       	mov    WORD PTR [r8-0x3],ax
 3ec:	c1 e8 10             	shr    eax,0x10
 3ef:	41 88 40 ff          	mov    BYTE PTR [r8-0x1],al
 3f3:	4d 39 d1             	cmp    r9,r10
 3f6:	75 b0                	jne    3a8 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0xd8>
 3f8:	5b                   	pop    rbx
 3f9:	5e                   	pop    rsi
 3fa:	c3                   	ret
 3fb:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
 400:	31 c0                	xor    eax,eax
 402:	eb 88                	jmp    38c <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0xbc>
 404:	90                   	nop
 405:	90                   	nop
 406:	90                   	nop
 407:	90                   	nop
 408:	90                   	nop
 409:	90                   	nop
 40a:	90                   	nop
 40b:	90                   	nop
 40c:	90                   	nop
 40d:	90                   	nop
 40e:	90                   	nop
 40f:	90                   	nop
