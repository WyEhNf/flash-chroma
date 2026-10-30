if __name__=='__main__':
    plan=read(PLAN)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同')
    if '--repeats' in sys.argv and int(sys.argv[sys.argv.index('--repeats')+1])!=5:raise AssertionError('完整五轮，不补跑')
    os.environ['OMP_PROC_BIND']='false';os.environ.pop('OMP_PLACES',None);START_AFFINITY=control_affinity();module=Path(bench.__file__);bench.labels=lambda:['ref78','ref80','linear8_avx','linear8_clang_c99','rgb3d7_avx','rgb3d7_c99'];bench.setup=setup;bench.worker=worker;bench.__file__=__file__;bench.main();output=Path(sys.argv[sys.argv.index('--output')+1]);summary=output/'summary.json'
    if summary.exists():
        data=read(summary)
        for key,control in data['controls'].items():
            if not control['pass_']:data['tiers'][key]={str(t):None for t in (100,90,80,70,60,50)}
        data['native_plan_sha256']=sha(PLAN);data['method']='四worker六角色完整五轮百图，process mask0x55、未逐OMP线程绑定/锁频，root排他窗；656调用+6RSS，不重跑。';save(summary,data)
    save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(PLAN),script_sha256=sha(__file__),benchmark_module_sha256=sha(module),affinity_start=START_AFFINITY,scope='精度/速度独立100..50；旧线性仅配对，分母仍每worker较快78/80；AA失效清空全部档位。'))
