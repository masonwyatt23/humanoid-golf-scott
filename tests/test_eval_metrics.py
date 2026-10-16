"""Metric unit tests on SYNTHETIC data (no sim / no trained models)."""
import math
import numpy as np
from eval.evaluate import compute_metrics, club_path_dispersion
from eval.compare_styles import make_table, best


def test_identical_paths_zero_dispersion():
    p = np.cumsum(np.ones((30, 3)) * 0.01, axis=0)
    assert club_path_dispersion([p, p.copy(), p.copy()]) < 1e-12


def test_dispersion_different_lengths_and_offset():
    p = np.linspace(0, 1, 30)[:, None] * np.ones(3)
    q = np.linspace(0, 1, 60)[:, None] * np.ones(3)  # same shape, different T
    assert club_path_dispersion([p, q]) < 1e-9
    off = p + np.array([0.1, 0, 0])
    assert abs(club_path_dispersion([p, off]) - 0.05) < 1e-9  # std of two points 0.1 apart


def test_metrics_basic():
    m = compute_metrics([1.0, 3.0], [True, False])
    assert m["contact_rate"] == 0.5 and m["mean_distance"] == 2.0
    assert math.isclose(m["cv_distance"], 0.5) and m["mean_distance_contact"] == 1.0
    assert math.isnan(m["path_dispersion"])


def test_zero_mean_cv_nan_and_no_contact():
    m = compute_metrics([0.0, 0.0], [False, False])
    assert math.isnan(m["cv_distance"]) and math.isnan(m["mean_distance_contact"])


def test_table_handles_missing_and_nan():
    r = [{"style": "rory", "status": "no_model"}, dict(compute_metrics([1, 2], [True, True]), style="scott")]
    assert "no model" in make_table(r) and "n/a" in make_table(r)
    assert "scott" in best(r)
