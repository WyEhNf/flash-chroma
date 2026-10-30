"""生成独立 final1，不覆盖历史包或原 C++ 模板。"""
import pathlib,re,hashlib,json,difflib
root=pathlib.Path(__file__).resolve().parent
out=root/'final1';out.mkdir(exist_ok=True)
search=[root,root/'prefix_joint',root/'common/framework',root/'common/include']
seen=set();origins={}
def expand(p):
 p=p.resolve()
 if p in seen:return '// 已在前文内嵌：'+p.name+'\n'
 seen.add(p);origins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 source=p.read_text(encoding='utf-8-sig')
 def nested(m):
  name=m.group(1)
  for folder in [p.parent]+search:
   q=folder/name
   if q.is_file():return expand(q)
  raise RuntimeError('缺少本地头文件：'+name)
 return '// 来源：'+p.name+'\n'+re.sub(r'^\s*#\s*include\s+"([^"]+)"\s*$',nested,source,flags=re.M)
header=expand(root/'final_pipeline.hpp')
(out/'flash_chroma_framework.hpp').write_text(header,encoding='utf-8',newline='\n')
base=pathlib.Path(r'F:\Hackathon\极速焕彩测试框架\FlashChroma-delivery-20261030\main.cpp')
source=base.read_text(encoding='utf-8-sig')
assert source.count('lut_sparse(luts_raw[i], 17,  lut17[i])')==1
source=source.replace('lut_sparse(luts_raw[i], 17,  lut17[i])','lut_sparse(luts_raw[i], 33,  lut17[i])')
source=source.replace('std::string data_dir = "../data";','std::string data_dir = "data";')
source=source.replace('if (argc >= 2) data_dir = argv[1];','if (argc >= 2) data_dir = argv[1];\n    const int image_count = argc >= 3 ? std::atoi(argv[2]) : 4;\n    if (image_count < 1 || image_count > MAX_IMAGES) return 1;')
source=source.replace('for (int i = 1; i <= 4; i++) {','for (int i = 1; i <= image_count; i++) {')
(out/'main.cpp').write_text(source,encoding='utf-8',newline='\n')
(root/'main-vs-delivery.diff').write_text(''.join(difflib.unified_diff(base.read_text(encoding='utf-8-sig').splitlines(True),source.splitlines(True),fromfile=str(base),tofile='final1/main.cpp')),encoding='utf-8')
manifest=dict(profile='final1',algorithm='FrameworkStep m33 chain_ls + prefix_nodes(32 nodes,1 sweep,stage3 then2)',
 mapping='DirectRGB24 + 自动AVX2 pair32；不支持时Scalar/Sparse降级',
 source_files=origins,base_main_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),
 output_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.suffix in ('.hpp','.cpp')},
 production_main_modified=False,original_reference_and_delta_and_timecost_unchanged=True,
 main_changes=['17改为33，作为本独立版本的显式尺寸','默认数据目录data','新增可选图片数量参数，默认4且上限100'])
(root/'package-source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(package=str(out),header_bytes=len(header.encode()),source_files=len(seen)),ensure_ascii=False))
