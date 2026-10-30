"""补测混合网格大小、非均匀曲率网格和整数最小二乘；仅本地审查。"""
from review_pr95_generalization import *

CASES = [
    ('mixed_tail', [17, 25, 33, 17], 'sample_interp', 'uniform'),
    ('mixed_hdr', [33, 17, 25, 33], 'sample_interp', 'curvature'),
    ('mixed_tail', [33]*4, 'ls_tetra_int', 'curvature'),
    ('mixed_hdr', [33]*4, 'ls_tetra_int', 'curvature'),
]

def main():
    numba.set_num_threads(4)
    dllpath = os.add_dll_directory('D:/codeblocks/MinGW/bin')
    library = native.Library(OUT/'review.dll')
    plan = json.loads((OUT/'plan.json').read_text(encoding='utf8'))
    save('supplement-plan.json', {'cases': CASES, 'seed': 20261029,
        'environment': plan['environment'], 'library': library.record(),
        'scope': '四个预先固定补充模型；独立探针、六张完整照片、跨后端一致性；不测稳定性能'})
    frames = []
    for p in plan['photos']:
        path = ROOT/p['evaluation']['path']
        assert native.digest(path) == p['evaluation']['sha256']
        frames.append(np.asarray(Image.open(path).convert('RGB')).reshape(-1,3).copy())
    photos = np.concatenate(frames)
    probes = np.random.default_rng(20261029).integers(0,256,(65536,3),dtype=np.uint8)
    results = []
    for index,(name,sizes,method,grid) in enumerate(CASES):
        print('开始补测', index, name, sizes, method, grid, flush=True)
        paths = [OUT/'tables'/f'{i}.lut256' for i in CHAINS[name]]
        folder = OUT/f'supplement-{index}'
        start = time.perf_counter()
        manifest = frontier.fit_candidate(paths,sizes,method,grid,folder)
        fit_s = time.perf_counter()-start
        model = native.Model(manifest['profiles']['fitted'],folder)
        stages = [io.load_sparse(folder/f'stage{i}.slut') for i in range(1,5)]
        expected = probes.copy()
        for stage in stages: expected = oracle(stage,expected)
        # 在各级坐标表切换点附近补充对照，包含Q16端点与并列权重。
        boundary = np.array(list(__import__('itertools').product((0,1,7,8,15,16,127,128,239,240,254,255),repeat=3)),np.uint8)
        boundary_expected = boundary.copy()
        for stage in stages: boundary_expected = oracle(stage,boundary_expected)
        configs = []
        baseline = None
        for rep,backend in [('sparse','scalar'),('sparse','avx2'),('direct_u8','avx2'),('direct_u16','avx2'),('direct_rgb24','avx2')]:
            config = native.configuration(rep,backend,threads=1 if backend=='scalar' else 4)
            try: engine = library.create(model,config)
            except RuntimeError as error:
                if '10 调色板容量不足' not in str(error): raise
                configs.append({'config':config,'status':'capacity'})
                continue
            with engine:
                actual=np.empty_like(probes); engine.apply(probes,actual)
                np.testing.assert_array_equal(actual,expected)
                actual_boundary=np.empty_like(boundary); engine.apply(boundary,actual_boundary)
                np.testing.assert_array_equal(actual_boundary,boundary_expected)
                image_result=np.empty_like(photos); engine.apply(photos,image_result)
                if baseline is None: baseline=image_result.copy()
                else: np.testing.assert_array_equal(image_result,baseline)
                configs.append({'config':config,'status':'ok','probe_mismatches':0,
                    'boundary_mismatches':0,'photo_mismatches':0,'output_sha256':native.sha(image_result),
                    'resources':engine.info,'prepare':engine.preparation})
        c_result=np.empty_like(probes)
        assert library.c_apply(model,probes,c_result)==0
        np.testing.assert_array_equal(c_result,expected)
        references=[io.load_full(path,mmap=True) for path in paths]
        truth=refmap(references,photos)
        per_image=[]; offset=0
        for p,frame in zip(plan['photos'],frames):
            end=offset+len(frame)
            per_image.append({'id':p['id'],**metric(baseline[offset:end],truth[offset:end])})
            offset=end
        row={'case':index,'chain':name,'sizes':sizes,'method':method,'grid':grid,
            'fit_s':fit_s,'models':model.records,'configs':configs,'c99_probe_mismatches':0,
            'photo_accuracy':metric(baseline,truth),'per_image':per_image,
            'probe_accuracy':metric(expected,refmap(references,probes)),
            'diagnostics':manifest['diagnostics']}
        results.append(row); save('supplement-results.json',results)
        print('补测完成',index,row['photo_accuracy'],flush=True)
    save('supplement-completed.json',{'passed':True,'models':len(results)})

if __name__=='__main__':main()
