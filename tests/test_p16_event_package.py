"""离线包只读身份验证与拒绝覆盖；不复制大素材或运行性能矩阵。"""
from pathlib import Path
import json
import sys
import zipfile
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import package_p16_event as packet


def fixture(tmp_path):
    root=tmp_path/'packet';root.mkdir()
    payload=root/'source.py';payload.write_text('print(1)\n',encoding='utf-8')
    packet.save(root/'MANIFEST.json',{'schema':packet.SCHEMA,'package_name':root.name,
        'members':{'source.py':{'sha256':packet.digest(payload),'bytes':payload.stat().st_size}}})
    archive=tmp_path/'packet.zip'
    with zipfile.ZipFile(archive,'x') as zipped:
        for path in root.iterdir():zipped.write(path,root.name+'/'+path.name)
    return root,archive


def test_verify_is_readonly_and_accepts_new_user_outputs(tmp_path):
    root,archive=fixture(tmp_path)
    before={path:path.read_bytes() for path in root.iterdir()}
    (root/'user-run.json').write_text('{}')
    assert packet.verify(root,archive)['passed'] is True
    assert all(path.read_bytes()==payload for path,payload in before.items())


def test_tampered_member_and_zip_are_rejected(tmp_path):
    root,archive=fixture(tmp_path)
    (root/'source.py').write_text('print(2)\n')
    with pytest.raises(ValueError,match='身份不符'):packet.verify(root,archive)


@pytest.mark.parametrize('name',['../outside','F:/outside','/outside'])
def test_manifest_path_cannot_escape(tmp_path,name):
    with pytest.raises(ValueError,match='非法'):packet.safe_relative(name)


def test_build_refuses_existing_output_before_touching_environment(tmp_path):
    root=tmp_path/'existing';root.mkdir();marker=root/'keep';marker.write_text('preserve')
    with pytest.raises(FileExistsError):packet.build(root,'missing-python','missing-library','missing-runner','missing-mingw')
    assert marker.read_text()=='preserve'


def test_zip_extra_member_rejected(tmp_path):
    root,archive=fixture(tmp_path)
    with zipfile.ZipFile(archive,'a') as zipped:zipped.writestr('packet/extra','extra')
    with pytest.raises(ValueError,match='ZIP成员'):packet.verify(root,archive)
