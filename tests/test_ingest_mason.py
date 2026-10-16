import json
from pathlib import Path

import numpy as np
import pytest

from data import ingest_mason_swings as ing
from data import process_video as pv

cv2 = pytest.importorskip("cv2")


def _video(path: Path, n=60, fps=30, size=(480, 640)):
    h, w = size
    ext = path.suffix.lower()
    fourcc = cv2.VideoWriter_fourcc(*("MJPG" if ext == ".avi" else "mp4v"))
    wr = cv2.VideoWriter(str(path), fourcc, fps, (w, h))
    for i in range(n):
        wr.write(np.full((h, w, 3), i % 255, np.uint8))
    wr.release()


def _lm():
    rng = np.random.default_rng(0)
    base = rng.normal(size=(pv.N_LM, 3)) * 0.3
    return np.concatenate([base, np.full((pv.N_LM, 1), 0.99)], axis=1)


def _backend_factory(kind="ok"):
    state = {"i": 0, "calls": 0}
    lm = _lm()

    def backend(frame):
        state["calls"] += 1
        state["i"] += 1
        if kind == "none":
            return None
        if kind == "half" and state["i"] % 2:
            return None
        l = lm.copy()
        l[:, 0] += 0.01 * np.sin(state["i"] / 5)
        l[:, 1] += 0.01 * state["i"] / 10
        return l
    return (lambda model=None: (backend, lambda: None)), state


def _run(tmp, extra=(), kind="ok", files=None):
    vids, out = tmp / "v", tmp / "out"
    vids.mkdir(exist_ok=True)
    factory, state = _backend_factory(kind)
    rc = ing.main(["--videos", str(vids), "--out", str(out), *extra], backend_factory=factory)
    rep = out / "mason_ingest_report.json"
    return rc, (json.loads(rep.read_text()) if rep.exists() else None), state, out


def test_success_labels_real_not_synthetic(tmp_path):
    (tmp_path / "v").mkdir()
    _video(tmp_path / "v" / "mason_20261016_driver_dtl_001.mp4")
    rc, rep, _, out = _run(tmp_path)
    assert rc == 0 and rep["counts"]["ok"] == 1 and rep["is_synthetic"] is False
    d = np.load(out / "mason_mason_20261016_driver_dtl_001.npz")
    assert str(d["source"]) == "mason_self_filmed" and not bool(d["is_synthetic"])
    assert str(d["club"]) == "driver" and str(d["view"]) == "dtl"
    assert d["joints"].shape[1] == 11 and np.isfinite(d["joints"]).all() and float(d["dt"]) == 0.01


def test_capture_fps_sets_real_time_and_sidecar_csv(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    _video(v / "a.mp4", n=240, fps=30)  # 240 frames at 30fps header
    (v / "metadata.csv").write_text("filename,club,view,handedness,capture_fps\na.mp4,iron,fo,left,240\n")
    rc, rep, _, out = _run(tmp_path)
    assert rc == 0
    d = np.load(out / "mason_a.npz")
    assert abs(float(d["time"][-1]) - 0.99) < 0.02  # 240 frames @240fps = 1 s real
    assert str(d["club"]) == "iron" and str(d["handedness"]) == "left" and float(d["capture_fps"]) == 240


def test_cli_capture_fps_overrides_sidecar(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    _video(v / "a.mp4", n=240, fps=30)
    (v / "a.json").write_text(json.dumps({"capture_fps": 120}))
    rc, rep, _, out = _run(tmp_path, ["--capture-fps", "240"])
    assert rc == 0 and float(np.load(out / "mason_a.npz")["capture_fps"]) == 240


@pytest.mark.parametrize("make,code", [
    (lambda p: p.write_bytes(b"junk"), "unreadable"),
    (lambda p: p.write_bytes(b""), "empty_file"),
    (lambda p: _video(p, size=(120, 90)), "low_resolution"),
    (lambda p: _video(p, n=10), "too_short"),
    (lambda p: _video(p, n=700, fps=30), "too_long"),
])
def test_file_errors(tmp_path, make, code):
    v = tmp_path / "v"; v.mkdir()
    make(v / "bad.mp4")
    _video(v / "good.mp4")
    rc, rep, _, out = _run(tmp_path)
    by = {r["file"]: r for r in rep["files"]}
    assert rc == 3 and by["bad.mp4"]["error_code"] == code and by["bad.mp4"]["error"]
    assert by["good.mp4"]["status"] == "ok" and (out / "mason_good.npz").exists()  # isolation


def test_bad_extension_and_non_video_ignored_sidecar(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    (v / "notes.txt").write_text("hi")
    (v / "README.md").write_text("x")
    rc, rep, _, _ = _run(tmp_path)
    assert rep["files"][0]["error_code"] == "bad_extension" and len(rep["files"]) == 1


def test_no_person_and_intermittent(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    _video(v / "a.mp4")
    rc, rep, _, out = _run(tmp_path, kind="none")
    assert rep["files"][0]["error_code"] == "no_person" and not (out / "mason_a.npz").exists()
    rc, rep, _, _ = _run(tmp_path, kind="half", extra=["--force"])
    assert rep["files"][0]["error_code"] == "person_intermittent"


def test_capture_fps_below_header_rejected(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    _video(v / "a.mp4", fps=60)
    rc, rep, _, _ = _run(tmp_path, ["--capture-fps", "30"])
    assert rep["files"][0]["error_code"] == "bad_fps"


def test_bad_metadata(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    _video(v / "a.mp4")
    (v / "metadata.csv").write_text("filename,handedness\na.mp4,ambidextrous\n")
    rc, rep, _, _ = _run(tmp_path)
    assert rep["files"][0]["error_code"] == "bad_metadata"
    (v / "metadata.json").write_text("{not json")
    rc, rep, _, _ = _run(tmp_path)
    assert rc == 2


def test_resume_skips_then_reprocesses_on_change(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    _video(v / "a.mp4")
    _, _, s1, _ = _run(tmp_path)
    rc, rep, s2, out = _run(tmp_path)
    assert rep["files"][0]["status"] == "skipped" and s2["calls"] == 0
    rc, rep, s3, _ = _run(tmp_path, ["--force"])
    assert rep["files"][0]["status"] == "ok" and s3["calls"] > 0
    rc, rep, s4, _ = _run(tmp_path, ["--handedness", "left", "--force"])
    _, rep, s5, _ = _run(tmp_path, ["--handedness", "right"])  # settings changed -> redo
    assert rep["files"][0]["status"] == "ok"


def test_dry_run_and_empty_folder(tmp_path):
    v = tmp_path / "v"; v.mkdir()
    rc, rep, _, out = _run(tmp_path)
    assert rc == 0 and rep is None  # nothing to do
    _video(v / "a.mp4")
    rc, rep, st, out = _run(tmp_path, ["--dry-run"])
    assert rc == 0 and st["calls"] == 0 and not list(out.glob("mason_*.npz"))


def test_missing_folder_and_left_handed_mirrors(tmp_path):
    assert ing.main(["--videos", str(tmp_path / "nope"), "--out", str(tmp_path / "o")]) == 2
    v = tmp_path / "v"; v.mkdir()
    _video(v / "a.mp4")
    _, _, _, out = _run(tmp_path)
    right = np.load(out / "mason_a.npz")["joints"].copy()
    _run(tmp_path, ["--handedness", "left", "--force"])
    left = np.load(out / "mason_a.npz")["joints"]
    assert right.shape == left.shape and not np.allclose(right, left)
