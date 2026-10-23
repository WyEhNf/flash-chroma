if __name__=='__main__':
    path=ROOT/'experiments/tagged-block16-native-v1.json';plan=read(path)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同')
    if '--repeats' in sys.argv and int(sys.argv[sys.argv.index('--repeats')+1])!=5:raise AssertionError('只允许完整五轮')
    os.environ['OMP_PROC_BIND']='false';os.environ.pop('OMP_PLACES',None);START_AFFINITY=control_affinity();module=Path(bench.__file__);bench.labels=lambda:['ref78','ref80','old32','old3B','tag_avx','tag_c99'];bench.setup=setup;bench.worker=worker;bench.__file__=__file__;bench.main();output=Path(sys.argv[sys.argv.index('--output')+1]);summary=output/'summary.json'
    if summary.exists():
        data=read(summary)
        for key,control in data['controls'].items():
            if not control['pass_']:data['tiers'][key]={str(t):None for t in (100,90,80,70,60,50)}
        data['native_plan_sha256']=sha(path);data['method']='四进程轮转/反序；六角色每线程/接口预热1+5完整百图，process允许集0x55，OMP_PROC_BIND=false，未逐OMP线程绑定或锁频；全组排他窗口。';save(summary,data)
    save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(path),script_sha256=sha(__file__),benchmark_module_sha256=sha(module),copied_worker_source_sha256=sha(ROOT/'scripts/bench_le16_block1024.py'),affinity_start=START_AFFINITY,scope='六角色、24情形、四worker，共480主要/96预热/80AA=656 native端点。0x55实际允许集，不逐OMP线程绑定或锁频，不拼旧unbound绝对时间或恢复旧3B。'))
