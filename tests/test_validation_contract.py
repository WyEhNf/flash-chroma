"""One end-to-end acceptance of validation scope and Windows mapping lifetime."""
from pathlib import Path

import numpy as np
import pytest

from lutlab import io, runtime, validation


def test_real_cube_scope_and_mapping_cleanup(tmp_path: Path, monkeypatch, rgb16_png):
    models = []
    for stage in range(4):
        path = tmp_path / f"stage{stage + 1}.slut"
        io.save_sparse(path, io.SparseLut(io.uniform_grid(18), np.zeros((18, 18, 18, 3), np.uint8)))
        models.append(path)
    full_path = tmp_path / "identity.lut256"
    full = np.memmap(full_path, dtype=np.uint8, mode="w+", shape=io.FULL_SHAPE)
    for red in range(256):
        full[red, ..., 0] = red
        full[red, ..., 1] = np.arange(256, dtype=np.uint8)[:, None]
        full[red, ..., 2] = np.arange(256, dtype=np.uint8)[None, :]
    full.flush()
    full._mmap.close()
    image = tmp_path / "black.png"
    io.save_image(image, np.zeros((768, 1024, 3), np.uint8))
    listing = tmp_path / "eval.txt"
    listing.write_text(str(image) + "\n")
    monkeypatch.setattr(validation.tempfile, "tempdir", str(tmp_path))
    result = validation.validate(models, full_path, listing, kernel="auto", threads=4,
                                 threshold=1, metric="max", constraint_scope="both", competition=True)
    assert result["image_set_pass"] is True
    assert result["cube_constraint_pass"] is False
    assert result["submission_contract_pass"] is True
    assert result["pass"] is False
    assert result["image_execution_verified"] is True
    assert result["image_execution"]["runtime"]["command"][1] == "verify"
    assert len(result["mapped_images_sha256"]) == 64
    assert result["cube"]["max"] == np.sqrt(3 * 255 ** 2)
    assert not list(tmp_path.glob("jshc-validate-*"))

    # Source-depth validation must consume the actual decoder path. Pillow's
    # mode alone would otherwise accept this container as ordinary RGB8.
    listing.write_text(str(rgb16_png) + "\n")
    with pytest.raises(runtime.BackendError, match="competition image"):
        validation.validate(models, full_path, listing, kernel="auto", threads=4,
                            threshold=1, metric="max", competition=True)
    assert not list(tmp_path.glob("jshc-validate-*"))
    listing.write_text(str(image) + "\n")

    # A successful process and valid cube must not hide a corrupt image path.
    # This also interrupts after both mappings open, exercising Windows cleanup.
    original_verify = runtime.verify
    def corrupt_image_output(*args, **kwargs):
        result = original_verify(*args, **kwargs)
        with Path(kwargs["output"]).open("r+b") as stream:
            stream.write(b"\x01")
        return result
    monkeypatch.setattr(runtime, "verify", corrupt_image_output)
    with pytest.raises(RuntimeError, match="native image output differs"):
        validation.validate(models, full_path, listing, kernel="auto", threads=4,
                            threshold=1, metric="max")
    assert not list(tmp_path.glob("jshc-validate-*"))
