import numpy as np
from eval.style_match import dtw_distance


def _swing(T=100, D=11, phase=0.0):
    t = np.linspace(0, 1, T)
    return np.stack([np.sin(2 * np.pi * (t + phase) * (k + 1) / 3) for k in range(D)], axis=1)


def test_identical_is_zero():
    a = _swing()
    assert dtw_distance(a, a) < 1e-12


def test_tempo_invariance_beats_offset():
    a = _swing(100); b = _swing(140)          # same shape, different tempo
    c = _swing(100) + 0.5                      # different style (offset)
    assert dtw_distance(a, b) < 0.1 * dtw_distance(a, c)


def test_symmetric_and_constant_offset():
    a = np.zeros((60, 11)); b = a + 0.2       # constant sequences: warping cannot help
    assert abs(dtw_distance(a, b) - dtw_distance(b, a)) < 1e-9
    assert abs(dtw_distance(a, b) - 0.2 * np.sqrt(11)) < 1e-9
