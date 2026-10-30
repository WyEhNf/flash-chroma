'use strict';
// 在Node的wasm32执行环境重放完整RGB域；时间仅作日志，不作性能比较。
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const assert=require('node:assert/strict');
const [wasmPath,romRoot,cubePath,resultPath]=process.argv.slice(2);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
async function main(){
  const moduleBytes=fs.readFileSync(wasmPath);
  const module=await WebAssembly.compile(moduleBytes);
  assert.deepEqual(WebAssembly.Module.imports(module),[]);
  const {exports:e}=await WebAssembly.instantiate(module,{});
  const memory=new Uint8Array(e.memory.buffer);
  const input=e.input_address(), output=e.output_address(), rom=e.rom_address();
  const cube=fs.readFileSync(cubePath);
  assert.equal(hash(cube),'3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22');
  const records=[];
  for(const bits of [0,4,6,8,10]){
    const blob=fs.readFileSync(path.join(romRoot,`rom-${bits}.bin`));
    memory.set(blob,rom+1);
    assert.equal(e.prepare_rom(blob.length,1),0);
    const sha=crypto.createHash('sha256');
    for(let start=0;start<16777216;start+=65536){
      for(let p=0;p<65536;++p){
        const code=start+p, at=input+3*p;
        memory[at]=code>>>16;memory[at+1]=(code>>>8)&255;memory[at+2]=code&255;
      }
      assert.equal(e.apply_pixels(65536,0,0),0);
      const got=Buffer.from(memory.buffer,output,196608);
      assert.equal(Buffer.compare(got,cube.subarray(start*3,(start+65536)*3)),0);
      sha.update(got);
    }
    let cases=0;
    for(const n of [0,1,7,8,9,255,4097,65536]) for(const off of [0,1,7,15]){
      memory.fill(0xa5,input,input+196640);memory.fill(0x5a,output,output+196640);
      const expected=Buffer.alloc(n*3);
      for(let p=0;p<n;++p){
        const r=(p*17+off)&255,g=(p*31+9)&255,b=(p*73+7)&255;
        memory[input+off+3*p]=r;memory[input+off+3*p+1]=g;memory[input+off+3*p+2]=b;
        const code=(r<<16)|(g<<8)|b;
        cube.copy(expected,p*3,code*3,code*3+3);
      }
      assert.equal(e.apply_pixels(n,off,15-off),0);
      assert.equal(Buffer.compare(Buffer.from(memory.buffer,output+15-off,n*3),expected),0);
      assert(memory.subarray(output,output+15-off).every(v=>v===0x5a));
      assert(memory.subarray(output+15-off+n*3,output+196640).every(v=>v===0x5a));
      assert.equal(e.apply_inplace(n,off),0);
      assert.equal(Buffer.compare(Buffer.from(memory.buffer,input+off,n*3),expected),0);
      cases+=2;
    }
    const inputBefore=hash(Buffer.from(memory.buffer,input,196640));
    assert.equal(e.reject_partial_overlap(),1);assert.equal(e.reject_rom_output(),1);
    assert.equal(e.reject_null_output(),1);assert.equal(e.empty_null(),0);
    assert.equal(hash(Buffer.from(memory.buffer,input,196640)),inputBefore);
    assert.equal(hash(Buffer.from(memory.buffer,rom+1,blob.length)),hash(blob));
    const prediction=sha.digest('hex');assert.equal(prediction,hash(cube));
    records.push({bits,rom_bytes:blob.length,rom_sha256:hash(blob),prediction_sha256:prediction,
      full_rgb_colors:16777216,byte_mismatches:0,finite_cases:cases,negative_cases:3,empty_null:true,rom_address_unaligned:true});
  }
  fs.writeFileSync(resultPath,JSON.stringify({passed:true,engine:process.versions,module_sha256:hash(moduleBytes),
    imports:WebAssembly.Module.imports(module),memory_bytes:e.memory.buffer.byteLength,
    model_view_bytes:e.jshc_mem_model_size(),records,
    limits:'wasm32实际执行；不是ARM/RISC-V实板、移动端吞吐、ROM闪存等待或功耗测量。静态测试缓冲独立列明，不能当核心RAM需求。'},null,2)+'\n');
  process.stdout.write('wasm32五格式完整RGB域及边界一致性通过\n');
}
main().catch(err=>{console.error(err);process.exitCode=1;});
