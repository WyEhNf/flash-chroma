"""本地 GUI 的 HTTP、整数模型接入与误差口径阶段验收。"""
import io as bytes_io
import json
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import zipfile

import numpy as np
from PIL import Image
import pytest

from lutlab import gui, io


@pytest.fixture
def workbench(tmp_path):
    app = gui.Workbench(tmp_path)
    server = gui.make_server(app, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    address = f"http://127.0.0.1:{server.server_port}"

    def request(path, value=None, *, raw=None, token=True, origin=None):
        data = raw if raw is not None else (json.dumps(value).encode() if value is not None else None)
        headers = {"X-Lutlab-Token": app.token} if token else {}
        if origin:
            headers["Origin"] = origin
        with urlopen(Request(address + path, data=data, headers=headers), timeout=10) as response:
            payload = response.read()
            return json.loads(payload) if response.headers["Content-Type"].startswith("application/json") else payload

    yield app, request
    server.shutdown()
    server.server_close()
    thread.join()


def image_upload(request):
    pixels = np.array([[[0, 73, 255], [49, 50, 51], [255, 129, 1]],
                       [[125, 14, 61], [29, 221, 71], [255, 255, 255]]], np.uint8)
    stream = bytes_io.BytesIO()
    Image.fromarray(pixels).save(stream, format="PNG")
    return request("/api/upload?kind=image&name=example.png", raw=stream.getvalue()), pixels


def wait(request, key):
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        record = request("/api/job/" + key)
        if record["status"] != "running":
            assert record["status"] == "done", record
            return record["result"]
        time.sleep(.02)
    raise AssertionError("GUI 任务未在限时内结束")


def parameters(image, sources):
    return dict(image=image, sources=sources, m=17, method="sample", grid="uniform", backend="numpy", threshold=3)


def scalar_oracle(model, rgb):
    """独立标量整数四面体，直接读取权威轴表，不调用生产插值。"""
    idx, frac = model.idx, model.frac
    strides = [model.m ** 2, model.m, 1]
    base = sum(int(idx[c, int(rgb[c])]) * strides[c] for c in range(3))
    order = sorted(range(3), key=lambda c: (-int(frac[c, int(rgb[c])]), c))
    values = [int(frac[c, int(rgb[c])]) for c in order]
    weights = [65536 - values[0], values[0] - values[1], values[1] - values[2], values[2]]
    indices = [base, base + strides[order[0]], base + strides[order[0]] + strides[order[1]], base + sum(strides)]
    nodes = model.nodes.reshape(-1, 3)
    return [(sum(w * int(nodes[i, c]) for w, i in zip(weights, indices)) + 32768) // 65536 for c in range(3)]


def test_gui_sparse_chain_http_and_export_preserve_tables(workbench, tmp_path):
    app, request = workbench
    image, pixels = image_upload(request)
    rng = np.random.default_rng(16039)
    ids, models = [], []
    for stage, m in enumerate((17, 18, 25, 33)):
        grid = np.stack([np.linspace(0, 1, m) ** p * 255 for p in (1.15, 1., .91)])
        path = tmp_path / f"stage{stage}.slut"
        io.save_sparse(path, io.SparseLut(grid, rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)))
        models.append(io.load_sparse(path))
        ids.append(request(f"/api/upload?kind=lut&name=stage{stage}.slut", raw=path.read_bytes())["id"])
    result = wait(request, request("/api/run", parameters(image["id"], ids))["id"])
    restored = request("/api/bootstrap")
    assert restored["history"][0]["result"]["parameters"]["sources"] == ids
    assert {a["id"] for a in restored["uploads"]} == {image["id"], *ids}
    expected = pixels.copy()
    for model in models:
        expected = np.array([scalar_oracle(model, p) for p in expected.reshape(-1, 3)], np.uint8).reshape(pixels.shape)
    actual = np.asarray(Image.open(bytes_io.BytesIO(request(result["urls"]["output.png"]))))
    np.testing.assert_array_equal(actual, expected)
    assert result["metrics"] is None and "heatmap.png" not in result["urls"]
    assert [s["m"] for s in result["stages"]] == [17, 18, 25, 33]
    with zipfile.ZipFile(bytes_io.BytesIO(request(result["urls"]["results.zip"]))) as archive:
        assert "result.json" in archive.namelist() and "reference.png" not in archive.namelist()
        for i, model in enumerate(models, 1):
            path = tmp_path / f"export{i}.slut"
            path.write_bytes(archive.read(f"stage-{i}.slut"))
            loaded = io.load_sparse(path)
            np.testing.assert_array_equal(loaded.frac, model.frac)
            np.testing.assert_array_equal(loaded.idx, model.idx)
    assert not (app.directory / "stage0.slut").exists()


def test_gui_full_source_reference_and_metrics(workbench, tmp_path):
    app, request = workbench
    image, pixels = image_upload(request)
    # 常量完整源使四级参考和四面体恢复均可解析核验，无需生成拟合矩阵。
    table = tmp_path / "constant.lut256"
    with table.open("wb") as output:
        block = np.tile(np.array([17, 89, 204], np.uint8), 256 * 256)
        for _ in range(256):
            output.write(block)
    with table.open("rb") as stream:
        source = app.upload(stream, table.stat().st_size, table.name, "lut")
    result = wait(request, request("/api/run", parameters(image["id"], [source["id"]] * 4))["id"])
    assert all(result["metrics"][k] == 0 for k in ("mean", "rms", "p99", "max", "cvar_1pct", "fraction_ge_threshold"))
    expected = np.broadcast_to(np.array([17, 89, 204], np.uint8), pixels.shape)
    reference = np.asarray(Image.open(bytes_io.BytesIO(request(result["urls"]["reference.png"]))))
    np.testing.assert_array_equal(reference, expected)
    assert result["image"]["competition_size"] is False


def test_gui_session_and_input_guards(workbench):
    app, request = workbench
    assert "色彩工作台".encode() in request("/")
    for kwargs in ({"token": False}, {"origin": "https://example.invalid"}):
        with pytest.raises(HTTPError) as error:
            request("/api/run", {}, **kwargs)
        assert error.value.code == 403
    for url, payload in [("/api/upload?kind=lut&name=wrong.slut", b"SLUT"),
                         ("/api/upload?kind=lut&name=wrong.lut256", b"bad")]:
        with pytest.raises(HTTPError) as error:
            request(url, raw=payload)
        assert error.value.code == 400
    image, _ = image_upload(request)
    p = parameters(image["id"], ["demo:warm:0"] * 4)
    for change in ({"m": 16}, {"m": True}, {"threshold": float("nan")}, {"sources": ["../../AGENTS.md"] * 4}, {"backend": "cuda"}):
        with pytest.raises(HTTPError) as error:
            request("/api/run", p | change)
        assert error.value.code == 400
    with pytest.raises(HTTPError):
        request("/result/../../AGENTS.md")
    assert len(app.jobs) == 0
    # 输出目录不可写时也必须回报失败，不能永久停留在“正在运行”。
    failed_directory = app.directory / "blocked"
    failed_directory.write_bytes(b"not a directory")
    app.directory = failed_directory
    key = request("/api/run", p)["id"]
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        job = request("/api/job/" + key)
        if job["status"] != "running":
            assert job["status"] == "failed" and job["message"]
            break
        time.sleep(.02)
    else:
        raise AssertionError("后台失败后任务没有结束")
