import shutil
from pathlib import Path

import numpy as np

from data import provenance as P
from data import tag_provenance as T
from imitation.reference_dataset import ReferenceDataset


def _mk(path, **extra):
    np.savez(path, joints=np.zeros((5, 11)), dt=np.array(0.01), **extra)


def test_tag_and_filter(tmp_path):
    _mk(tmp_path / "scott_swing.npz", style=np.array("scott"))
    _mk(tmp_path / "cmu_64_01.npz", source=np.array("cmu_mocap"))
    _mk(tmp_path / "mason_a.npz", source=np.array("mason_self_filmed"))
    _mk(tmp_path / "golfdb_x.npz")
    _mk(tmp_path / "mystery.npz")
    T.main(["--dir", str(tmp_path)])
    cls = {p.stem: P.read_tags(p)["license_class"] for p in tmp_path.glob("*.npz")}
    assert cls == {"scott_swing": "synthetic", "cmu_64_01": "needs_counsel", "mason_a": "self_owned",
                   "golfdb_x": "noncommercial", "mystery": "unknown"}
    ok = {Path(p).stem for p in P.include_commercial_only(sorted(tmp_path.glob("*.npz")))}
    assert ok == {"scott_swing", "mason_a"}  # CMU retagged counsel_required 2026-10
    assert P.read_tags(tmp_path / "cmu_64_01.npz")["acknowledgment_required"] is True
    assert P.read_tags(tmp_path / "cmu_64_01.npz")["commercial_ok"] is False and P.read_tags(tmp_path / "cmu_64_01.npz")["counsel_required"] is True
    assert "mocap.cs.cmu.edu" in P.read_tags(tmp_path / "cmu_64_01.npz")["acknowledgment_text"]
    assert len(ReferenceDataset(tmp_path)) == 5
    assert len(ReferenceDataset(tmp_path, commercial_only=True)) == 2


def test_idempotent_preserves_arrays(tmp_path):
    f = tmp_path / "scott_swing.npz"
    _mk(f, style=np.array("scott"), extra=np.arange(3))
    T.tag_file(f)
    b1 = f.read_bytes()
    assert T.tag_file(f) == "skipped" and f.read_bytes() == b1
    d = np.load(f)
    assert np.array_equal(d["extra"], np.arange(3)) and d["joints"].shape == (5, 11)
    assert not list(tmp_path.glob("*.tagtmp.npz"))


def test_untagged_excluded_and_bad_kind(tmp_path):
    _mk(tmp_path / "x.npz")
    assert P.include_commercial_only([tmp_path / "x.npz", tmp_path / "missing.npz"]) == []
    try:
        P.preset("bogus"); assert False
    except ValueError:
        pass


def test_generator_tags(tmp_path):
    from data import generate_synthetic_scott as G
    import inspect
    assert "_prov.tag" in inspect.getsource(G)
