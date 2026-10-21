"""首次静态执行前补齐dispatcher多ELF节字节核对，初版未执行且保留。"""
from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE/'check.py').read_text(encoding='utf-8')
function='''
def dispatcher_bytes_verified(path, assembly):
    # ET_REL各可执行节分别按节内地址解析，不能把cold/startup偏移套入主.text。
    import struct
    data=path.read_bytes()
    assert data[:6]==b'\\x7fELF\\x02\\x01'
    section_offset=struct.unpack_from('<Q',data,40)[0]
    stride,count,names_index=struct.unpack_from('<HHH',data,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',data,section_offset+i*stride) for i in range(count)]
    names=sections[names_index]
    strings=data[names[4]:names[4]+names[5]]
    payload={strings[s[0]:].split(b'\\0',1)[0].decode():data[s[4]:s[4]+s[5]] for s in sections if s[2]&4}
    current=None
    comparisons=0
    for line in assembly.read_text(encoding='utf-8').splitlines():
        section=re.match(r'Disassembly of section (.+):',line)
        if section:
            current=section[1]
        op=re.match(r'\\s*([0-9a-f]+):\\s+((?:[0-9a-f]{2}\\s+)+)',line)
        if op:
            encoded=bytes.fromhex(op[2])
            offset=int(op[1],16)
            if current not in payload or payload[current][offset:offset+len(encoded)]!=encoded:
                return False
            comparisons+=1
    return comparisons>0

'''
marker='def main():'
assert text.count(marker)==1
text=text.replace(marker,function+'\n'+marker)
old="dispatch_bytes=all(dispatch_raw[o['offset']:o['offset']+len(o['bytes'])]==bytes.fromhex(' '.join(o['bytes'])) for o in dispatch_ops)"
assert text.count(old)==1
text=text.replace(old,'dispatch_bytes=dispatcher_bytes_verified(dispatcher,target)')
text=text.replace("HERE/'results.json'","HERE/'results-v2.json'")
marker="    with (HERE/'results-v2.json').open('x',encoding='utf-8') as stream:"
assert text.count(marker)==1
text=text.replace(marker,"    result['unexecuted_initial_checker_sha256']=sha(HERE/'check.py')\n"
    "    result['preflight_correction']='初版未执行；dispatcher按各可执行节验证字节，cold/startup不误套主.text，源/对象/门槛未改。'\n"+marker)
with (HERE/'check-v2.py').open('x',encoding='utf-8') as stream:
    stream.write(text)
