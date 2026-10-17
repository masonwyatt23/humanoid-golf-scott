import subprocess
from pathlib import Path
import numpy as np
from data import unified_refset as U

ROOT = Path(__file__).resolve().parents[1]
M = U.load_manifest()


def test_files_exist_tracked_and_commercial():
    tracked = set(subprocess.run(["git", "ls-files", "data/references"], cwd=ROOT, capture_output=True, text=True).stdout.split())
    for e in M["entries"]:
        assert (ROOT / e["path"]).exists()
        if tracked:
            assert e["path"] in tracked
        assert e["handedness"] == "left"
        if e["source"] == "multisense":
            # published as CC0 but participants identifiable -> needs counsel, not commercial-eligible
            assert e["license_class"] == "needs_counsel" and e["commercial_ok"] is False
            assert e["license_class_as_published"] == "cc0" and e["counsel_required"] is True
            assert "research_mocap_datasets_licenses" in e["license_note"]
        else:
            assert e["commercial_ok"]
        assert e["on_origin_main"] in (True, None)


def test_split_rules():
    ents = M["entries"]
    mason_val = [e for e in ents if e["source"] == "mason" and e["split"] == "val"]
    assert len(mason_val) >= 2
    for s in ("mason", "multisense", "cmu"):
        assert {e["split"] for e in ents if e["source"] == s} == {"train", "val"}
    groups = {}
    for e in ents:
        groups.setdefault(e["group"], set()).add(e["split"])
    assert all(len(v) == 1 for v in groups.values())  # no group straddles train/val
    # v2 swings that re-cut a v1 swing / v3 re-cuts share a group with the v3 slow-mo window
    slow = [e for e in ents if e["variant"] == "slowmo"]
    assert slow and all(e["weight_train"] == 0 for e in slow)


def test_split_is_deterministic():
    import copy
    ents = copy.deepcopy(M["entries"])
    for e in ents:
        e["split"] = None
    U.assign_splits(ents, U.load_sampling_config())
    assert [e["split"] for e in ents] == [e["split"] for e in M["entries"]]


def test_weights_normalised_and_configurable():
    ents, p = U.weights(M)
    assert abs(p.sum() - 1) < 1e-9
    tot = {}
    for e, pi in zip(ents, p):
        tot[e["source"]] = tot.get(e["source"], 0) + pi
    assert abs(tot["mason"] - 0.6) < 1e-6 and abs(tot["multisense"] - 0.2) < 1e-6 and abs(tot["cmu"] - 0.2) < 1e-6
    cfg = U.load_sampling_config(); cfg["source_weights"] = {"mason": 0.8, "multisense": 0.1, "cmu": 0.1}
    ents2, p2 = U.weights(M, cfg)
    assert abs(sum(pi for e, pi in zip(ents2, p2) if e["source"] == "mason") - 0.8) < 1e-6
    q = [e["quality"] for e in ents if e["source"] == "mason"]
    pm = [pi for e, pi in zip(ents, p) if e["source"] == "mason"]
    assert np.argmax(q) == np.argmax(pm)


def test_sample_and_loader_with_reference_dataset():
    rng = np.random.default_rng(0)
    seen = {U.sample(rng, M)["source"] for _ in range(200)}
    assert seen == {"mason", "multisense", "cmu"}
    ds = U.as_reference_dataset("val", M)
    assert len(ds) == len(U.split_entries(M, "val"))
    r = ds.sample()
    assert r["joints"].shape[1] == 11 and r["handedness"] == "left"
    cmu = next(U.load_ref(e) for e in M["entries"] if e["source"] == "cmu")
    raw = np.load(ROOT / cmu["path"].replace(str(ROOT) + "/", ""))["joints"]
    assert cmu["mirrored"] and not np.allclose(cmu["joints"], raw)
    assert len(list(U.iter_split(M, "val"))) > 0


def test_handedness_unverified_flags_do_not_change_sampling():
    flagged = {e["path"].split("/")[-1]: e for e in M["entries"] if e.get("handedness_unverified")}
    assert set(flagged) == {"mason_v2_p1_s11.npz", "mason_v2_p2_s10.npz"}
    for e in flagged.values():
        assert e["exclude_pending_verification"] is True and "nverified" in e["flag_note"]
    # flag only: flagged train entry keeps its weight, and the manifest rebuild logic still lists it
    assert flagged["mason_v2_p2_s10.npz"]["split"] == "train" and flagged["mason_v2_p2_s10.npz"]["weight_train"] > 0
    assert flagged["mason_v2_p1_s11.npz"]["split"] == "val"
    ents, _ = U.weights()
    assert "data/references/mason_v2_p2_s10.npz" in {e["path"] for e in ents}


def test_licence_flags_in_manifest():
    from data.provenance import commercial_cleared
    man = U.load_manifest()
    by = {}
    for e in man["entries"]:
        by.setdefault(e["source"], []).append(e)
    assert all(e["counsel_required"] for e in by["multisense"])
    assert not any(commercial_cleared(e) for e in by["multisense"])
    assert all(e["no_standalone_resale"] and e["acknowledgment_required"] and e["ack"] for e in by["cmu"])
    assert all(commercial_cleared(e) for e in by["cmu"])
    assert all("license_url" in e and "verification" in e for e in by["cmu"] + by["multisense"])
    s11 = [e for e in by["mason"] if e["path"].endswith("mason_v2_p1_s11.npz")][0]
    assert s11["needs_mason_confirmation"] and not s11["handedness_verified"] and s11["split"] == "val"


def test_face_path_stub_is_unverified():
    import json
    from pathlib import Path
    j = json.load(open(Path(__file__).resolve().parents[1] / "data/references/mason_impact_face_path_proxies.json"))
    assert j["unverified_all"] and "face_angle_deg" in j["unavailable"] and "club_path_deg" in j["unavailable"]
