"""赛前入口的配置绑定、严格门禁与失败保留，不把schema夹具当数值验收。"""
from pathlib import Path
from types import SimpleNamespace
import json
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import p16_event as event


def config(tmp_path, **changes):
    value={'schema':event.SCHEMA,'cpu_only':True,'dense_format':event.DENSE_FORMAT,
        'library':'native/bridge.dll','manifest':'models/source-manifest.json','profile':'fitted',
        'image_list':'input/list.txt','image_root':'input','source_luts':[], 'runtime':dict(event.RUNTIME_DEFAULT),
        'fit':{'m':[17,25,25,33],'method':'sample_interp','grid':'uniform','alpha':.5,'exponent':.4},
        'threshold':None,'write_images':False,'validate_c99':True,'expected_images':100}
    value.update(changes);path=tmp_path/'session.json';path.write_text(json.dumps(value),encoding='utf-8')
    return path,value


def test_config_paths_resolve_from_config_directory(tmp_path):
    path,_=config(tmp_path)
    _,resolved=event.load_config(path)
    assert resolved['manifest']==tmp_path/'models/source-manifest.json'
    assert resolved['image_list']==tmp_path/'input/list.txt'
    assert resolved['image_root']==tmp_path/'input'
    assert resolved['library']==tmp_path/'native/bridge.dll'
    assert resolved['runtime']['representation']=='sparse'


def test_explicit_library_override_replaces_missing_config_path(tmp_path):
    path,_=config(tmp_path)
    replacement=tmp_path/'another.dll'
    _,resolved=event.load_config(path,replacement)
    assert resolved['library']==replacement


@pytest.mark.parametrize('value',[{'photo':'x','stages':[]},{'preset':'film','native_profile':'default'}])
def test_rejects_creative_workbench_json(tmp_path,value):
    path=tmp_path/'creative.json';path.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='创意配置'):
        event.load_config(path)


@pytest.mark.parametrize('changes',[{'dense_format':'rgb16'}, {'cpu_only':False}, {'profile':None},
    {'threshold':True}, {'threshold':float('nan')}, {'threshold':-1}, {'source_luts':['one']},
    {'runtime':{'threads':True}}, {'runtime':{'threads':0}}, {'runtime':{'block_pixels':0}},
    {'runtime':{'unknown_option':1}}, {'runtime':{'max_workspace_bytes':-1}}, {'expected_images':0}])
def test_rejects_ambiguous_or_illegal_config(tmp_path,changes):
    path,_=config(tmp_path,**changes)
    with pytest.raises(ValueError):event.load_config(path)


def test_init_refuses_overwrite_and_does_not_require_existing_dll(tmp_path):
    output=tmp_path/'event.json';missing=tmp_path/'future.dll';manifest=tmp_path/'models.json'
    manifest.write_text(json.dumps({'original_luts':[],'profiles':{}}))
    event.init_config(output,library=missing,manifest=manifest,images=tmp_path/'list.txt',image_root=tmp_path)
    first=output.read_bytes()
    assert json.loads(first)['library']=='future.dll'
    with pytest.raises(FileExistsError):event.init_config(output,library=missing)
    assert output.read_bytes()==first


def test_per_image_threshold_is_strict_and_not_batch_only():
    _,_,submission=event.modules()
    rows=[{'pixels':1,'delta_e_sum':0.,'mean_delta_e':0.,'max_delta_e':0.,'p99_delta_e':0.},
          {'pixels':1,'delta_e_sum':2.,'mean_delta_e':2.,'max_delta_e':2.,'p99_delta_e':2.}]
    result=submission.accuracy_summary(rows,2.)
    assert result['aggregate_mean_pass'] is True
    assert result['all_image_mean_pass'] is False


def test_failed_run_preserves_plan_directory_and_failure(tmp_path,monkeypatch):
    path,_=config(tmp_path)
    def fail(config):raise RuntimeError('模型加载失败')
    monkeypatch.setattr(event,'model_and_library',fail)
    output=tmp_path/'run'
    with pytest.raises(RuntimeError,match='模型加载失败'):event.run_event(path,output)
    record=json.loads((output/'failure.json').read_text())
    assert record['completed'] is False and record['completed_images']==0
    assert record['error']=='模型加载失败'
    with pytest.raises(FileExistsError):event.run_event(path,output)
    assert json.loads((output/'failure.json').read_text())==record


def test_missing_dependency_is_preserved_as_failed_run(tmp_path,monkeypatch):
    path,_=config(tmp_path)
    def fail():raise ImportError('missing numpy')
    monkeypatch.setattr(event,'modules',fail)
    output=tmp_path/'run'
    with pytest.raises(ImportError):event.run_event(path,output)
    assert json.loads((output/'failure.json').read_text())['completed'] is False


def test_source_mismatch_cannot_reuse_old_cinema(tmp_path,monkeypatch):
    _,frontier,_=event.modules()
    monkeypatch.setattr(frontier,'source_records',lambda paths:[{'path':str(i),'sha256':str(i)*64} for i in range(4)])
    model=SimpleNamespace(profile={'source_luts_sha256':['a'*64]*4})
    with pytest.raises(ValueError,match='旧模型'):
        event.reference_records({'source_luts':[Path(str(i)) for i in range(4)],'threshold':None},{},model)


def test_fit_relocates_run_config_without_changing_original(tmp_path,monkeypatch):
    path,value=config(tmp_path,source_luts=['a','b','c','d'])
    before=path.read_bytes();_,frontier,_=event.modules()
    def fake_fit(paths,sizes,method,grid,output,**kwargs):
        # 只验证编排与路径重定位，不模拟数值拟合。
        output.mkdir();event.save_new(output/'source-manifest.json',{'fixture':True});return {'fixture':True}
    monkeypatch.setattr(frontier,'fit_candidate',fake_fit)
    output=tmp_path/'fit';result=event.fit_event(path,output)
    saved=json.loads((output/'run-config.json').read_text())
    assert saved['manifest']=='source-manifest.json' and saved['profile']=='fitted'
    assert saved['source_luts']==['../a','../b','../c','../d']
    assert saved['runtime']==value['runtime'] and path.read_bytes()==before
    assert result['status']=='fitted_pending_chain_accuracy_and_runtime_validation'


@pytest.mark.parametrize('actual,expected,limit,formal', [(100,100,None,True),(99,100,1,False),(100,100,100,False),(2,2,None,False)])
def test_explicit_limit_and_nonhundred_batches_are_debug(actual,expected,limit,formal):
    assert event.batch_size_check(actual,expected,limit) is formal


def test_wrong_full_batch_is_refused_with_failure_preserved(tmp_path,monkeypatch):
    path,_=config(tmp_path)
    (tmp_path/'input').mkdir();(tmp_path/'input/list.txt').write_text('missing.png\n'*99)
    monkeypatch.setattr(event,'model_and_library',lambda config: ({},SimpleNamespace(profile={}),None,{}))
    with pytest.raises(ValueError,match='expected_images=100'):
        event.run_event(path,tmp_path/'wrong-count')
    failure=json.loads((tmp_path/'wrong-count/failure.json').read_text())
    assert failure['completed_images']==0 and '99' in failure['error']


def test_doctor_is_not_ready_for_wrong_expected_count(tmp_path,monkeypatch):
    path,_=config(tmp_path)
    (tmp_path/'input').mkdir();(tmp_path/'input/present.png').write_bytes(b'path-fixture')
    (tmp_path/'input/list.txt').write_text('present.png\n'*99)
    model=SimpleNamespace(profile={},records=[])
    monkeypatch.setattr(event,'model_and_library',lambda config: ({},model,SimpleNamespace(record=lambda:{}),{}))
    report=event.doctor(path)
    assert report['ready'] is False
    assert any('expected_images=100' in message for message in report['errors'])
