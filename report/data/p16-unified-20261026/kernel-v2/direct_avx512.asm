
artifacts/p16-avx512-ilp64-v2/direct_avx512.o:     file format pe-x86-64


Disassembly of section .text:

0000000000000000 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy>:
   0:	55                   	push   rbp
   1:	57                   	push   rdi
   2:	56                   	push   rsi
   3:	53                   	push   rbx
   4:	48 8b 5c 24 48       	mov    rbx,QWORD PTR [rsp+0x48]
   9:	48 83 fb 3f          	cmp    rbx,0x3f
   d:	0f 86 9d 03 00 00    	jbe    3b0 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x3b0>
  13:	c5 f9 6f 2d 40 00 00 	vmovdqa xmm5,XMMWORD PTR [rip+0x40]        # 5b <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x5b>
  1a:	00 
  1b:	c5 f9 6f 25 50 00 00 	vmovdqa xmm4,XMMWORD PTR [rip+0x50]        # 73 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x73>
  22:	00 
  23:	62 a1 6d 00 ef d2    	vpxord xmm18,xmm18,xmm18
  29:	48 bf ff ff ff ff ff 	movabs rdi,0xffffffffffff
  30:	ff 00 00 
  33:	62 a3 6d 40 25 d2 ff 	vpternlogd zmm18,zmm18,zmm18,0xff
  3a:	62 e1 7d 48 6f 0d 00 	vmovdqa32 zmm17,ZMMWORD PTR [rip+0x0]        # 44 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x44>
  41:	00 00 00 
  44:	62 e1 7d 48 6f 05 80 	vmovdqa32 zmm16,ZMMWORD PTR [rip+0x80]        # ce <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0xce>
  4b:	00 00 00 
  4e:	4d 89 c2             	mov    r10,r8
  51:	62 b1 65 40 72 d2 1e 	vpsrld zmm19,zmm18,0x1e
  58:	4c 89 c8             	mov    rax,r9
  5b:	62 f3 55 48 43 ed 00 	vshufi32x4 zmm5,zmm5,zmm5,0x0
  62:	49 89 db             	mov    r11,rbx
  65:	62 b1 6d 40 72 d2 18 	vpsrld zmm18,zmm18,0x18
  6c:	62 f3 5d 48 43 e4 00 	vshufi32x4 zmm4,zmm4,zmm4,0x0
  73:	c4 e1 fb 92 d7       	kmovq  k2,rdi
  78:	c5 f4 46 c9          	kxnorw k1,k1,k1
  7c:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
  80:	62 d1 7f ca 6f 1a    	vmovdqu8 zmm3{k2}{z},ZMMWORD PTR [r10]
  86:	62 d1 7f ca 6f 92 30 	vmovdqu8 zmm2{k2}{z},ZMMWORD PTR [r10+0x30]
  8d:	00 00 00 
  90:	62 d1 7f ca 6f 8a 60 	vmovdqu8 zmm1{k2}{z},ZMMWORD PTR [r10+0x60]
  97:	00 00 00 
  9a:	62 d1 7f ca 6f 82 90 	vmovdqu8 zmm0{k2}{z},ZMMWORD PTR [r10+0x90]
  a1:	00 00 00 
  a4:	62 f2 75 40 36 db    	vpermd zmm3,zmm17,zmm3
  aa:	62 f2 75 40 36 d2    	vpermd zmm2,zmm17,zmm2
  b0:	62 f2 75 40 36 c9    	vpermd zmm1,zmm17,zmm1
  b6:	62 f2 75 40 36 c0    	vpermd zmm0,zmm17,zmm0
  bc:	62 f2 65 48 00 dd    	vpshufb zmm3,zmm3,zmm5
  c2:	62 f2 6d 48 00 d5    	vpshufb zmm2,zmm2,zmm5
  c8:	62 f2 75 48 00 cd    	vpshufb zmm1,zmm1,zmm5
  ce:	62 f2 7d 48 00 c5    	vpshufb zmm0,zmm0,zmm5
  d4:	62 f1 5d 40 72 d3 02 	vpsrld zmm20,zmm3,0x2
  db:	62 b1 65 48 db db    	vpandd zmm3,zmm3,zmm19
  e1:	c5 f8 90 d9          	kmovw  k3,k1
  e5:	c5 f8 90 e1          	kmovw  k4,k1
  e9:	62 e2 7d 43 90 2c a1 	vpgatherdd zmm21{k3},DWORD PTR [rcx+zmm20*4]
  f0:	62 f1 65 48 72 f3 03 	vpslld zmm3,zmm3,0x3
  f7:	c5 f8 90 e9          	kmovw  k5,k1
  fb:	c5 f8 90 f1          	kmovw  k6,k1
  ff:	62 f1 5d 40 72 d2 02 	vpsrld zmm20,zmm2,0x2
 106:	62 e2 55 40 45 eb    	vpsrlvd zmm21,zmm21,zmm3
 10c:	62 b1 6d 48 db d3    	vpandd zmm2,zmm2,zmm19
 112:	62 f2 7d 44 90 1c a1 	vpgatherdd zmm3{k4},DWORD PTR [rcx+zmm20*4]
 119:	62 f1 6d 48 72 f2 03 	vpslld zmm2,zmm2,0x3
 120:	62 f1 5d 40 72 d1 02 	vpsrld zmm20,zmm1,0x2
 127:	62 b1 75 48 db cb    	vpandd zmm1,zmm1,zmm19
 12d:	62 a1 55 40 db ea    	vpandd zmm21,zmm21,zmm18
 133:	62 f2 65 48 45 da    	vpsrlvd zmm3,zmm3,zmm2
 139:	62 f1 75 48 72 f1 03 	vpslld zmm1,zmm1,0x3
 140:	62 f2 7d 45 90 14 a1 	vpgatherdd zmm2{k5},DWORD PTR [rcx+zmm20*4]
 147:	62 f2 6d 48 45 c9    	vpsrlvd zmm1,zmm2,zmm1
 14d:	62 f1 6d 48 72 d0 02 	vpsrld zmm2,zmm0,0x2
 154:	62 b1 7d 48 db c3    	vpandd zmm0,zmm0,zmm19
 15a:	62 e2 7d 4e 90 24 91 	vpgatherdd zmm20{k6},DWORD PTR [rcx+zmm2*4]
 161:	62 f1 7d 48 72 f0 03 	vpslld zmm0,zmm0,0x3
 168:	62 b1 65 48 db d2    	vpandd zmm2,zmm3,zmm18
 16e:	62 e2 5d 40 45 e0    	vpsrlvd zmm20,zmm20,zmm0
 174:	62 b1 75 48 db c2    	vpandd zmm0,zmm1,zmm18
 17a:	62 f1 fd 48 6f ca    	vmovdqa64 zmm1,zmm2
 180:	62 a1 5d 40 db e2    	vpandd zmm20,zmm20,zmm18
 186:	c5 f8 90 f9          	kmovw  k7,k1
 18a:	c5 f8 90 d9          	kmovw  k3,k1
 18e:	c5 f8 90 e1          	kmovw  k4,k1
 192:	62 f2 7d 4b 90 14 8a 	vpgatherdd zmm2{k3},DWORD PTR [rdx+zmm1*4]
 199:	c5 f8 90 e9          	kmovw  k5,k1
 19d:	62 f2 7d 4c 90 0c 82 	vpgatherdd zmm1{k4},DWORD PTR [rdx+zmm0*4]
 1a4:	62 f2 7d 47 90 1c aa 	vpgatherdd zmm3{k7},DWORD PTR [rdx+zmm21*4]
 1ab:	62 f2 7d 45 90 04 a2 	vpgatherdd zmm0{k5},DWORD PTR [rdx+zmm20*4]
 1b2:	62 f2 65 48 00 dc    	vpshufb zmm3,zmm3,zmm4
 1b8:	62 f2 6d 48 00 d4    	vpshufb zmm2,zmm2,zmm4
 1be:	62 f2 75 48 00 cc    	vpshufb zmm1,zmm1,zmm4
 1c4:	49 83 eb 40          	sub    r11,0x40
 1c8:	62 f2 7d 40 36 db    	vpermd zmm3,zmm16,zmm3
 1ce:	62 f2 7d 40 36 d2    	vpermd zmm2,zmm16,zmm2
 1d4:	62 f2 7d 40 36 c9    	vpermd zmm1,zmm16,zmm1
 1da:	49 81 c2 c0 00 00 00 	add    r10,0xc0
 1e1:	62 f1 7f 4a 7f 18    	vmovdqu8 ZMMWORD PTR [rax]{k2},zmm3
 1e7:	62 f2 7d 48 00 c4    	vpshufb zmm0,zmm0,zmm4
 1ed:	62 f1 7f 4a 7f 90 30 	vmovdqu8 ZMMWORD PTR [rax+0x30]{k2},zmm2
 1f4:	00 00 00 
 1f7:	62 f2 7d 40 36 c0    	vpermd zmm0,zmm16,zmm0
 1fd:	62 f1 7f 4a 7f 88 60 	vmovdqu8 ZMMWORD PTR [rax+0x60]{k2},zmm1
 204:	00 00 00 
 207:	62 f1 7f 4a 7f 80 90 	vmovdqu8 ZMMWORD PTR [rax+0x90]{k2},zmm0
 20e:	00 00 00 
 211:	48 05 c0 00 00 00    	add    rax,0xc0
 217:	49 83 fb 3f          	cmp    r11,0x3f
 21b:	0f 87 5f fe ff ff    	ja     80 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x80>
 221:	4c 8d 5b c0          	lea    r11,[rbx-0x40]
 225:	48 89 d8             	mov    rax,rbx
 228:	49 83 e3 c0          	and    r11,0xffffffffffffffc0
 22c:	83 e0 3f             	and    eax,0x3f
 22f:	49 83 c3 40          	add    r11,0x40
 233:	48 83 f8 0f          	cmp    rax,0xf
 237:	0f 86 03 01 00 00    	jbe    340 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x340>
 23d:	48 8d 7b f0          	lea    rdi,[rbx-0x10]
 241:	4b 8d 34 5b          	lea    rsi,[r11+r11*2]
 245:	c5 f9 6f 2d 40 00 00 	vmovdqa xmm5,XMMWORD PTR [rip+0x40]        # 28d <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x28d>
 24c:	00 
 24d:	c5 f9 6f 25 50 00 00 	vmovdqa xmm4,XMMWORD PTR [rip+0x50]        # 2a5 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x2a5>
 254:	00 
 255:	4c 29 df             	sub    rdi,r11
 258:	c5 e1 ef db          	vpxor  xmm3,xmm3,xmm3
 25c:	4e 8d 14 06          	lea    r10,[rsi+r8*1]
 260:	62 e1 7d 48 6f 0d 00 	vmovdqa32 zmm17,ZMMWORD PTR [rip+0x0]        # 26a <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x26a>
 267:	00 00 00 
 26a:	48 89 fd             	mov    rbp,rdi
 26d:	62 f3 65 48 25 db ff 	vpternlogd zmm3,zmm3,zmm3,0xff
 274:	49 8d 04 31          	lea    rax,[r9+rsi*1]
 278:	62 e1 7d 48 6f 05 80 	vmovdqa32 zmm16,ZMMWORD PTR [rip+0x80]        # 302 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x302>
 27f:	00 00 00 
 282:	49 8d 74 30 30       	lea    rsi,[r8+rsi*1+0x30]
 287:	62 f1 6d 40 72 d3 1e 	vpsrld zmm18,zmm3,0x1e
 28e:	48 c1 ed 04          	shr    rbp,0x4
 292:	62 f3 55 48 43 ed 00 	vshufi32x4 zmm5,zmm5,zmm5,0x0
 299:	48 8d 6c 6d 00       	lea    rbp,[rbp+rbp*2+0x0]
 29e:	62 f1 65 48 72 d3 18 	vpsrld zmm3,zmm3,0x18
 2a5:	62 f3 5d 48 43 e4 00 	vshufi32x4 zmm4,zmm4,zmm4,0x0
 2ac:	c5 f4 46 c9          	kxnorw k1,k1,k1
 2b0:	48 c1 e5 04          	shl    rbp,0x4
 2b4:	48 01 ee             	add    rsi,rbp
 2b7:	48 bd ff ff ff ff ff 	movabs rbp,0xffffffffffff
 2be:	ff 00 00 
 2c1:	c4 e1 fb 92 d5       	kmovq  k2,rbp
 2c6:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
 2cd:	00 00 00 
 2d0:	62 d1 7f ca 6f 02    	vmovdqu8 zmm0{k2}{z},ZMMWORD PTR [r10]
 2d6:	c5 f8 90 f1          	kmovw  k6,k1
 2da:	c5 f8 90 f9          	kmovw  k7,k1
 2de:	49 83 c2 30          	add    r10,0x30
 2e2:	62 f2 75 40 36 c0    	vpermd zmm0,zmm17,zmm0
 2e8:	62 f2 7d 48 00 c5    	vpshufb zmm0,zmm0,zmm5
 2ee:	62 f1 6d 48 72 d0 02 	vpsrld zmm2,zmm0,0x2
 2f5:	62 b1 7d 48 db c2    	vpandd zmm0,zmm0,zmm18
 2fb:	62 f2 7d 4e 90 0c 91 	vpgatherdd zmm1{k6},DWORD PTR [rcx+zmm2*4]
 302:	62 f1 7d 48 72 f0 03 	vpslld zmm0,zmm0,0x3
 309:	62 f2 75 48 45 c8    	vpsrlvd zmm1,zmm1,zmm0
 30f:	62 f1 75 48 db cb    	vpandd zmm1,zmm1,zmm3
 315:	62 f2 7d 4f 90 04 8a 	vpgatherdd zmm0{k7},DWORD PTR [rdx+zmm1*4]
 31c:	62 f2 7d 48 00 c4    	vpshufb zmm0,zmm0,zmm4
 322:	62 f2 7d 40 36 c0    	vpermd zmm0,zmm16,zmm0
 328:	62 f1 7f 4a 7f 00    	vmovdqu8 ZMMWORD PTR [rax]{k2},zmm0
 32e:	48 83 c0 30          	add    rax,0x30
 332:	49 39 f2             	cmp    r10,rsi
 335:	75 99                	jne    2d0 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x2d0>
 337:	48 83 e7 f0          	and    rdi,0xfffffffffffffff0
 33b:	4d 8d 5c 3b 10       	lea    r11,[r11+rdi*1+0x10]
 340:	49 39 db             	cmp    r11,rbx
 343:	73 5f                	jae    3a4 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x3a4>
 345:	4b 8d 04 5b          	lea    rax,[r11+r11*2]
 349:	4d 8d 14 00          	lea    r10,[r8+rax*1]
 34d:	49 01 c1             	add    r9,rax
 350:	48 8d 04 5b          	lea    rax,[rbx+rbx*2]
 354:	49 01 c0             	add    r8,rax
 357:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
 35e:	00 00 
 360:	41 0f b6 42 01       	movzx  eax,BYTE PTR [r10+0x1]
 365:	45 0f b6 5a 02       	movzx  r11d,BYTE PTR [r10+0x2]
 36a:	49 83 c2 03          	add    r10,0x3
 36e:	49 83 c1 03          	add    r9,0x3
 372:	41 c1 e3 10          	shl    r11d,0x10
 376:	c1 e0 08             	shl    eax,0x8
 379:	44 09 d8             	or     eax,r11d
 37c:	45 0f b6 5a fd       	movzx  r11d,BYTE PTR [r10-0x3]
 381:	44 09 d8             	or     eax,r11d
 384:	0f b6 04 01          	movzx  eax,BYTE PTR [rcx+rax*1]
 388:	4c 8d 1c 82          	lea    r11,[rdx+rax*4]
 38c:	41 8b 03             	mov    eax,DWORD PTR [r11]
 38f:	45 0f b7 1b          	movzx  r11d,WORD PTR [r11]
 393:	c1 e8 10             	shr    eax,0x10
 396:	66 45 89 59 fd       	mov    WORD PTR [r9-0x3],r11w
 39b:	41 88 41 ff          	mov    BYTE PTR [r9-0x1],al
 39f:	4d 39 c2             	cmp    r10,r8
 3a2:	75 bc                	jne    360 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x360>
 3a4:	c5 f8 77             	vzeroupper
 3a7:	5b                   	pop    rbx
 3a8:	5e                   	pop    rsi
 3a9:	5f                   	pop    rdi
 3aa:	5d                   	pop    rbp
 3ab:	c3                   	ret
 3ac:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
 3b0:	48 89 d8             	mov    rax,rbx
 3b3:	45 31 db             	xor    r11d,r11d
 3b6:	e9 78 fe ff ff       	jmp    233 <_ZN12jshc_channel16avx512_direct_u8EPKhPKjS1_Phy+0x233>
 3bb:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]

00000000000003c0 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy>:
 3c0:	55                   	push   rbp
 3c1:	57                   	push   rdi
 3c2:	56                   	push   rsi
 3c3:	53                   	push   rbx
 3c4:	48 8b 5c 24 48       	mov    rbx,QWORD PTR [rsp+0x48]
 3c9:	48 83 fb 3f          	cmp    rbx,0x3f
 3cd:	0f 86 fd 02 00 00    	jbe    6d0 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x310>
 3d3:	c5 f9 6f 2d 40 00 00 	vmovdqa xmm5,XMMWORD PTR [rip+0x40]        # 41b <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x5b>
 3da:	00 
 3db:	c5 f9 6f 25 50 00 00 	vmovdqa xmm4,XMMWORD PTR [rip+0x50]        # 433 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x73>
 3e2:	00 
 3e3:	62 a1 6d 00 ef d2    	vpxord xmm18,xmm18,xmm18
 3e9:	48 bf ff ff ff ff ff 	movabs rdi,0xffffffffffff
 3f0:	ff 00 00 
 3f3:	62 a3 6d 40 25 d2 ff 	vpternlogd zmm18,zmm18,zmm18,0xff
 3fa:	62 e1 7d 48 6f 0d 00 	vmovdqa32 zmm17,ZMMWORD PTR [rip+0x0]        # 404 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x44>
 401:	00 00 00 
 404:	62 e1 7d 48 6f 05 80 	vmovdqa32 zmm16,ZMMWORD PTR [rip+0x80]        # 48e <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0xce>
 40b:	00 00 00 
 40e:	4d 89 c2             	mov    r10,r8
 411:	4c 89 c8             	mov    rax,r9
 414:	62 f3 55 48 43 ed 00 	vshufi32x4 zmm5,zmm5,zmm5,0x0
 41b:	62 f3 5d 48 43 e4 00 	vshufi32x4 zmm4,zmm4,zmm4,0x0
 422:	49 89 db             	mov    r11,rbx
 425:	62 b1 6d 40 72 d2 10 	vpsrld zmm18,zmm18,0x10
 42c:	c4 e1 fb 92 d7       	kmovq  k2,rdi
 431:	c5 f4 46 c9          	kxnorw k1,k1,k1
 435:	0f 1f 00             	nop    DWORD PTR [rax]
 438:	62 d1 7f ca 6f 1a    	vmovdqu8 zmm3{k2}{z},ZMMWORD PTR [r10]
 43e:	62 d1 7f ca 6f 92 30 	vmovdqu8 zmm2{k2}{z},ZMMWORD PTR [r10+0x30]
 445:	00 00 00 
 448:	62 d1 7f ca 6f 8a 60 	vmovdqu8 zmm1{k2}{z},ZMMWORD PTR [r10+0x60]
 44f:	00 00 00 
 452:	62 d1 7f ca 6f 82 90 	vmovdqu8 zmm0{k2}{z},ZMMWORD PTR [r10+0x90]
 459:	00 00 00 
 45c:	62 f2 75 40 36 db    	vpermd zmm3,zmm17,zmm3
 462:	62 f2 75 40 36 d2    	vpermd zmm2,zmm17,zmm2
 468:	62 f2 75 40 36 c9    	vpermd zmm1,zmm17,zmm1
 46e:	62 f2 75 40 36 c0    	vpermd zmm0,zmm17,zmm0
 474:	62 f2 65 48 00 dd    	vpshufb zmm3,zmm3,zmm5
 47a:	62 f2 6d 48 00 d5    	vpshufb zmm2,zmm2,zmm5
 480:	62 f2 75 48 00 cd    	vpshufb zmm1,zmm1,zmm5
 486:	62 f2 7d 48 00 c5    	vpshufb zmm0,zmm0,zmm5
 48c:	c5 f8 90 d9          	kmovw  k3,k1
 490:	62 e2 7d 4b 90 24 59 	vpgatherdd zmm20{k3},DWORD PTR [rcx+zmm3*2]
 497:	c5 f8 90 e1          	kmovw  k4,k1
 49b:	c5 f8 90 e9          	kmovw  k5,k1
 49f:	62 f2 7d 4c 90 1c 51 	vpgatherdd zmm3{k4},DWORD PTR [rcx+zmm2*2]
 4a6:	62 a1 5d 40 db e2    	vpandd zmm20,zmm20,zmm18
 4ac:	62 f2 7d 4d 90 14 49 	vpgatherdd zmm2{k5},DWORD PTR [rcx+zmm1*2]
 4b3:	c5 f8 90 f1          	kmovw  k6,k1
 4b7:	62 e2 7d 4e 90 1c 41 	vpgatherdd zmm19{k6},DWORD PTR [rcx+zmm0*2]
 4be:	62 b1 65 48 db ca    	vpandd zmm1,zmm3,zmm18
 4c4:	62 b1 6d 48 db c2    	vpandd zmm0,zmm2,zmm18
 4ca:	62 a1 65 40 db da    	vpandd zmm19,zmm19,zmm18
 4d0:	62 b1 fd 48 6f d4    	vmovdqa64 zmm2,zmm20
 4d6:	c5 f8 90 f9          	kmovw  k7,k1
 4da:	c5 f8 90 d9          	kmovw  k3,k1
 4de:	62 f2 7d 4f 90 1c 92 	vpgatherdd zmm3{k7},DWORD PTR [rdx+zmm2*4]
 4e5:	c5 f8 90 e1          	kmovw  k4,k1
 4e9:	62 f2 7d 4b 90 14 8a 	vpgatherdd zmm2{k3},DWORD PTR [rdx+zmm1*4]
 4f0:	c5 f8 90 e9          	kmovw  k5,k1
 4f4:	62 f2 7d 4c 90 0c 82 	vpgatherdd zmm1{k4},DWORD PTR [rdx+zmm0*4]
 4fb:	62 f2 7d 45 90 04 9a 	vpgatherdd zmm0{k5},DWORD PTR [rdx+zmm19*4]
 502:	62 f2 65 48 00 dc    	vpshufb zmm3,zmm3,zmm4
 508:	62 f2 6d 48 00 d4    	vpshufb zmm2,zmm2,zmm4
 50e:	62 f2 75 48 00 cc    	vpshufb zmm1,zmm1,zmm4
 514:	49 83 eb 40          	sub    r11,0x40
 518:	62 f2 7d 40 36 db    	vpermd zmm3,zmm16,zmm3
 51e:	62 f2 7d 40 36 d2    	vpermd zmm2,zmm16,zmm2
 524:	62 f2 7d 40 36 c9    	vpermd zmm1,zmm16,zmm1
 52a:	49 81 c2 c0 00 00 00 	add    r10,0xc0
 531:	62 f1 7f 4a 7f 18    	vmovdqu8 ZMMWORD PTR [rax]{k2},zmm3
 537:	62 f2 7d 48 00 c4    	vpshufb zmm0,zmm0,zmm4
 53d:	62 f1 7f 4a 7f 90 30 	vmovdqu8 ZMMWORD PTR [rax+0x30]{k2},zmm2
 544:	00 00 00 
 547:	62 f2 7d 40 36 c0    	vpermd zmm0,zmm16,zmm0
 54d:	62 f1 7f 4a 7f 88 60 	vmovdqu8 ZMMWORD PTR [rax+0x60]{k2},zmm1
 554:	00 00 00 
 557:	62 f1 7f 4a 7f 80 90 	vmovdqu8 ZMMWORD PTR [rax+0x90]{k2},zmm0
 55e:	00 00 00 
 561:	48 05 c0 00 00 00    	add    rax,0xc0
 567:	49 83 fb 3f          	cmp    r11,0x3f
 56b:	0f 87 c7 fe ff ff    	ja     438 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x78>
 571:	4c 8d 5b c0          	lea    r11,[rbx-0x40]
 575:	48 89 d8             	mov    rax,rbx
 578:	49 83 e3 c0          	and    r11,0xffffffffffffffc0
 57c:	83 e0 3f             	and    eax,0x3f
 57f:	49 83 c3 40          	add    r11,0x40
 583:	48 83 f8 0f          	cmp    rax,0xf
 587:	0f 86 d9 00 00 00    	jbe    666 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x2a6>
 58d:	48 8d 7b f0          	lea    rdi,[rbx-0x10]
 591:	4b 8d 34 5b          	lea    rsi,[r11+r11*2]
 595:	c5 f9 6f 2d 40 00 00 	vmovdqa xmm5,XMMWORD PTR [rip+0x40]        # 5dd <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x21d>
 59c:	00 
 59d:	c5 f9 6f 25 50 00 00 	vmovdqa xmm4,XMMWORD PTR [rip+0x50]        # 5f5 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x235>
 5a4:	00 
 5a5:	4c 29 df             	sub    rdi,r11
 5a8:	c5 e9 ef d2          	vpxor  xmm2,xmm2,xmm2
 5ac:	4d 8d 14 30          	lea    r10,[r8+rsi*1]
 5b0:	62 e1 7d 48 6f 0d 00 	vmovdqa32 zmm17,ZMMWORD PTR [rip+0x0]        # 5ba <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x1fa>
 5b7:	00 00 00 
 5ba:	48 89 fd             	mov    rbp,rdi
 5bd:	49 8d 04 31          	lea    rax,[r9+rsi*1]
 5c1:	62 f3 6d 48 25 d2 ff 	vpternlogd zmm2,zmm2,zmm2,0xff
 5c8:	62 e1 7d 48 6f 05 80 	vmovdqa32 zmm16,ZMMWORD PTR [rip+0x80]        # 652 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x292>
 5cf:	00 00 00 
 5d2:	49 8d 74 30 30       	lea    rsi,[r8+rsi*1+0x30]
 5d7:	62 f3 55 48 43 ed 00 	vshufi32x4 zmm5,zmm5,zmm5,0x0
 5de:	48 c1 ed 04          	shr    rbp,0x4
 5e2:	62 f3 5d 48 43 e4 00 	vshufi32x4 zmm4,zmm4,zmm4,0x0
 5e9:	48 8d 6c 6d 00       	lea    rbp,[rbp+rbp*2+0x0]
 5ee:	62 f1 6d 48 72 d2 10 	vpsrld zmm2,zmm2,0x10
 5f5:	c5 f4 46 c9          	kxnorw k1,k1,k1
 5f9:	48 c1 e5 04          	shl    rbp,0x4
 5fd:	48 01 ee             	add    rsi,rbp
 600:	48 bd ff ff ff ff ff 	movabs rbp,0xffffffffffff
 607:	ff 00 00 
 60a:	c4 e1 fb 92 d5       	kmovq  k2,rbp
 60f:	90                   	nop
 610:	62 d1 7f ca 6f 02    	vmovdqu8 zmm0{k2}{z},ZMMWORD PTR [r10]
 616:	c5 f8 90 f1          	kmovw  k6,k1
 61a:	c5 f8 90 f9          	kmovw  k7,k1
 61e:	49 83 c2 30          	add    r10,0x30
 622:	62 f2 75 40 36 c0    	vpermd zmm0,zmm17,zmm0
 628:	62 f2 7d 48 00 c5    	vpshufb zmm0,zmm0,zmm5
 62e:	62 f2 7d 4e 90 0c 41 	vpgatherdd zmm1{k6},DWORD PTR [rcx+zmm0*2]
 635:	62 f1 75 48 db ca    	vpandd zmm1,zmm1,zmm2
 63b:	62 f2 7d 4f 90 04 8a 	vpgatherdd zmm0{k7},DWORD PTR [rdx+zmm1*4]
 642:	62 f2 7d 48 00 c4    	vpshufb zmm0,zmm0,zmm4
 648:	62 f2 7d 40 36 c0    	vpermd zmm0,zmm16,zmm0
 64e:	62 f1 7f 4a 7f 00    	vmovdqu8 ZMMWORD PTR [rax]{k2},zmm0
 654:	48 83 c0 30          	add    rax,0x30
 658:	49 39 f2             	cmp    r10,rsi
 65b:	75 b3                	jne    610 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x250>
 65d:	48 83 e7 f0          	and    rdi,0xfffffffffffffff0
 661:	4d 8d 5c 3b 10       	lea    r11,[r11+rdi*1+0x10]
 666:	49 39 db             	cmp    r11,rbx
 669:	73 5d                	jae    6c8 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x308>
 66b:	4b 8d 04 5b          	lea    rax,[r11+r11*2]
 66f:	4d 8d 14 00          	lea    r10,[r8+rax*1]
 673:	49 01 c1             	add    r9,rax
 676:	48 8d 04 5b          	lea    rax,[rbx+rbx*2]
 67a:	49 01 c0             	add    r8,rax
 67d:	0f 1f 00             	nop    DWORD PTR [rax]
 680:	41 0f b6 42 01       	movzx  eax,BYTE PTR [r10+0x1]
 685:	45 0f b6 5a 02       	movzx  r11d,BYTE PTR [r10+0x2]
 68a:	49 83 c2 03          	add    r10,0x3
 68e:	49 83 c1 03          	add    r9,0x3
 692:	41 c1 e3 10          	shl    r11d,0x10
 696:	c1 e0 08             	shl    eax,0x8
 699:	44 09 d8             	or     eax,r11d
 69c:	45 0f b6 5a fd       	movzx  r11d,BYTE PTR [r10-0x3]
 6a1:	44 09 d8             	or     eax,r11d
 6a4:	01 c0                	add    eax,eax
 6a6:	89 c0                	mov    eax,eax
 6a8:	0f b7 04 01          	movzx  eax,WORD PTR [rcx+rax*1]
 6ac:	4c 8d 1c 82          	lea    r11,[rdx+rax*4]
 6b0:	41 8b 03             	mov    eax,DWORD PTR [r11]
 6b3:	45 0f b7 1b          	movzx  r11d,WORD PTR [r11]
 6b7:	c1 e8 10             	shr    eax,0x10
 6ba:	66 45 89 59 fd       	mov    WORD PTR [r9-0x3],r11w
 6bf:	41 88 41 ff          	mov    BYTE PTR [r9-0x1],al
 6c3:	4d 39 c2             	cmp    r10,r8
 6c6:	75 b8                	jne    680 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x2c0>
 6c8:	c5 f8 77             	vzeroupper
 6cb:	5b                   	pop    rbx
 6cc:	5e                   	pop    rsi
 6cd:	5f                   	pop    rdi
 6ce:	5d                   	pop    rbp
 6cf:	c3                   	ret
 6d0:	48 89 d8             	mov    rax,rbx
 6d3:	45 31 db             	xor    r11d,r11d
 6d6:	e9 a8 fe ff ff       	jmp    583 <_ZN12jshc_channel17avx512_direct_u16EPKtPKjPKhPhy+0x1c3>
 6db:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]

00000000000006e0 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy>:
 6e0:	56                   	push   rsi
 6e1:	53                   	push   rbx
 6e2:	48 89 d3             	mov    rbx,rdx
 6e5:	49 83 f9 0f          	cmp    r9,0xf
 6e9:	0f 86 21 01 00 00    	jbe    810 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x130>
 6ef:	4d 8d 59 f0          	lea    r11,[r9-0x10]
 6f3:	62 f1 7d 48 6f 2d 00 	vmovdqa32 zmm5,ZMMWORD PTR [rip+0x0]        # 6fd <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x1d>
 6fa:	00 00 00 
 6fd:	62 f1 7d 48 6f 25 80 	vmovdqa32 zmm4,ZMMWORD PTR [rip+0x80]        # 787 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0xa7>
 704:	00 00 00 
 707:	48 be ff ff ff ff ff 	movabs rsi,0xffffffffffff
 70e:	ff 00 00 
 711:	4d 89 da             	mov    r10,r11
 714:	62 f2 7d 48 5a 1d 40 	vbroadcasti32x4 zmm3,XMMWORD PTR [rip+0x40]        # 75e <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x7e>
 71b:	00 00 00 
 71e:	62 f2 7d 48 5a 15 50 	vbroadcasti32x4 zmm2,XMMWORD PTR [rip+0x50]        # 778 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x98>
 725:	00 00 00 
 728:	4c 89 c0             	mov    rax,r8
 72b:	49 c1 ea 04          	shr    r10,0x4
 72f:	c4 e1 fb 92 ce       	kmovq  k1,rsi
 734:	c5 ec 46 d2          	kxnorw k2,k2,k2
 738:	4f 8d 14 52          	lea    r10,[r10+r10*2]
 73c:	49 c1 e2 04          	shl    r10,0x4
 740:	4e 8d 54 12 30       	lea    r10,[rdx+r10*1+0x30]
 745:	0f 1f 00             	nop    DWORD PTR [rax]
 748:	62 f1 7f c9 6f 02    	vmovdqu8 zmm0{k1}{z},ZMMWORD PTR [rdx]
 74e:	c5 f8 90 da          	kmovw  k3,k2
 752:	48 83 c2 30          	add    rdx,0x30
 756:	62 f2 55 48 36 c0    	vpermd zmm0,zmm5,zmm0
 75c:	62 f2 7d 48 00 c3    	vpshufb zmm0,zmm0,zmm3
 762:	62 f1 75 48 72 f0 01 	vpslld zmm1,zmm0,0x1
 769:	62 f1 75 48 fe c8    	vpaddd zmm1,zmm1,zmm0
 76f:	62 f2 7d 4b 90 04 09 	vpgatherdd zmm0{k3},DWORD PTR [rcx+zmm1*1]
 776:	62 f2 7d 48 00 c2    	vpshufb zmm0,zmm0,zmm2
 77c:	62 f2 5d 48 36 c0    	vpermd zmm0,zmm4,zmm0
 782:	62 f1 7f 49 7f 00    	vmovdqu8 ZMMWORD PTR [rax]{k1},zmm0
 788:	48 83 c0 30          	add    rax,0x30
 78c:	49 39 d2             	cmp    r10,rdx
 78f:	75 b7                	jne    748 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x68>
 791:	49 83 e3 f0          	and    r11,0xfffffffffffffff0
 795:	49 8d 43 10          	lea    rax,[r11+0x10]
 799:	c5 f8 77             	vzeroupper
 79c:	4c 39 c8             	cmp    rax,r9
 79f:	73 67                	jae    808 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0x128>
 7a1:	48 8d 04 40          	lea    rax,[rax+rax*2]
 7a5:	4f 8d 0c 49          	lea    r9,[r9+r9*2]
 7a9:	4c 8d 14 18          	lea    r10,[rax+rbx*1]
 7ad:	49 01 c0             	add    r8,rax
 7b0:	49 01 d9             	add    r9,rbx
 7b3:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
 7b8:	41 0f b6 42 01       	movzx  eax,BYTE PTR [r10+0x1]
 7bd:	41 0f b6 52 02       	movzx  edx,BYTE PTR [r10+0x2]
 7c2:	49 83 c2 03          	add    r10,0x3
 7c6:	49 83 c0 03          	add    r8,0x3
 7ca:	c1 e2 10             	shl    edx,0x10
 7cd:	c1 e0 08             	shl    eax,0x8
 7d0:	09 d0                	or     eax,edx
 7d2:	41 0f b6 52 fd       	movzx  edx,BYTE PTR [r10-0x3]
 7d7:	09 d0                	or     eax,edx
 7d9:	8d 14 40             	lea    edx,[rax+rax*2]
 7dc:	48 01 ca             	add    rdx,rcx
 7df:	0f b6 42 01          	movzx  eax,BYTE PTR [rdx+0x1]
 7e3:	44 0f b6 5a 02       	movzx  r11d,BYTE PTR [rdx+0x2]
 7e8:	0f b6 12             	movzx  edx,BYTE PTR [rdx]
 7eb:	c1 e0 08             	shl    eax,0x8
 7ee:	41 c1 e3 10          	shl    r11d,0x10
 7f2:	44 09 d8             	or     eax,r11d
 7f5:	09 d0                	or     eax,edx
 7f7:	66 41 89 40 fd       	mov    WORD PTR [r8-0x3],ax
 7fc:	c1 e8 10             	shr    eax,0x10
 7ff:	41 88 40 ff          	mov    BYTE PTR [r8-0x1],al
 803:	4d 39 d1             	cmp    r9,r10
 806:	75 b0                	jne    7b8 <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0xd8>
 808:	5b                   	pop    rbx
 809:	5e                   	pop    rsi
 80a:	c3                   	ret
 80b:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
 810:	31 c0                	xor    eax,eax
 812:	eb 88                	jmp    79c <_ZN12jshc_channel19avx512_direct_rgb24EPKhS1_Phy+0xbc>
 814:	90                   	nop
 815:	90                   	nop
 816:	90                   	nop
 817:	90                   	nop
 818:	90                   	nop
 819:	90                   	nop
 81a:	90                   	nop
 81b:	90                   	nop
 81c:	90                   	nop
 81d:	90                   	nop
 81e:	90                   	nop
 81f:	90                   	nop
