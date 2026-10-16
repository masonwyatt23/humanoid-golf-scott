import numpy as np
import pytest

from data import swing_segmentation as ss

TORSO = 100.0


def synth_track(swing_starts, back=0.9, down=0.3, T=12.0, fps=30.0, jitter_fps=False, seed=0,
                top_height=1.0):
    """Hands (px) for a golfer: still at address (y=420), slow backswing to a top 40px above
    the shoulder line (y=300), fast downswing, follow-through, settle.  Smooth (PCHIP) so
    speeds are physical.  top_height=0 gives a low 'partial' top."""
    from scipy.interpolate import PchipInterpolator
    rng = np.random.default_rng(seed)
    t = np.arange(1, int(T * fps) + 1) / fps
    if jitter_fps:  # variable frame rate: drop ~15% of frames
        keep = rng.random(len(t)) > 0.15
        keep[0] = True
        t = t[keep]
    addr = (500.0, 420.0)
    top = (380.0, 260.0 if top_height else 380.0)
    kt, kx, ky = [0.0], [addr[0]], [addr[1]]
    for s0 in swing_starts:
        imp = s0 + back + down
        pts = [(s0 - 0.6, addr), (s0, addr), (s0 + back * 0.5, (450.0, 340.0 if top_height else 400.0)),
               (s0 + back, top), (s0 + back + down * 0.6, (430.0, 380.0)),
               (imp, (520.0, 440.0)), (imp + 0.25, (600.0, 360.0)), (imp + 0.6, (640.0, 270.0)),
               (imp + 1.3, (640.0, 270.0)), (imp + 2.0, addr)]
        for tt, (x, y) in pts:
            if tt > kt[-1] + 1e-6:
                kt.append(tt); kx.append(x); ky.append(y)
    kt.append(max(T, kt[-1] + 1)); kx.append(addr[0]); ky.append(addr[1])
    x = PchipInterpolator(kt, kx)(t)
    y = PchipInterpolator(kt, ky)(t)
    return t, np.column_stack([x, y]), np.full(len(t), 300.0)


def test_detects_three_swings_and_tempo():
    t, hands, sh = synth_track([1.0, 5.0, 9.0], back=0.9, down=0.3)
    swings, rej = ss.detect_swings(t, hands, sh, TORSO)
    assert len(swings) == 3
    for s, s0 in zip(swings, [1.0, 5.0, 9.0]):
        assert abs(s.top_t - (s0 + 0.9)) < 0.15
        assert 2.2 < s.tempo < 4.0           # truth 3.0, 30 fps source
        assert s.start_t < s.takeaway_t < s.top_t < s.impact_t < s.end_t
        assert s.peak_speed > 5


def test_variable_fps_timestamps_respected():
    t, hands, sh = synth_track([1.0, 6.0], back=0.9, down=0.3, jitter_fps=True)
    swings, _ = ss.detect_swings(t, hands, sh, TORSO)
    assert len(swings) == 2
    assert all(2.3 < s.tempo < 5.5 for s in swings)  # 15% dropped frames: tempo is noisy


def test_tempo_distinguishes_fast_and_slow():
    t, h, sh = synth_track([1.0], back=0.75, down=0.30)
    fast = ss.detect_swings(t, h, sh, TORSO)[0][0].tempo
    t, h, sh = synth_track([1.0], back=1.2, down=0.30)
    slow = ss.detect_swings(t, h, sh, TORSO)[0][0].tempo
    assert slow > fast + 0.8


def test_still_golfer_has_no_swings():
    t = np.arange(0, 6, 1 / 30)
    hands = np.column_stack([np.full(len(t), 500.0), np.full(len(t), 420.0)])
    assert ss.detect_swings(t, hands, np.full(len(t), 300.0), TORSO) == ([], [])


def test_partial_swing_is_rejected_with_reason():
    # hands never rise above the shoulder line (chip / waggle): peak speed is high but rejected
    t, hands, sh = synth_track([1.0], top_height=0)
    swings, rej = ss.detect_swings(t, hands, sh, TORSO)
    assert swings == []
    assert rej and "not_above_shoulder" in rej[0]["reason"]


def test_nan_gaps_do_not_crash_and_long_gap_blocks_detection():
    t, hands, sh = synth_track([1.0, 6.0])
    hands[(t > 5.8) & (t < 7.8)] = np.nan   # 1.6 s tracking loss covers swing 2
    swings, _ = ss.detect_swings(t, hands, sh, TORSO)
    assert len(swings) == 1 and swings[0].impact_t < 3


def test_bad_inputs():
    assert ss.detect_swings(np.arange(3.0), np.zeros((3, 2)), np.zeros(3), TORSO) == ([], [])
    t = np.array([0, 1, 1, 2, 3, 4, 5, 6, 7.0])
    with pytest.raises(ValueError):
        ss.detect_swings(t, np.zeros((9, 2)), np.zeros(9), TORSO)


def test_windows_do_not_overlap_between_swings():
    t, hands, sh = synth_track([1.0, 4.0], back=0.9, down=0.3)
    swings, _ = ss.detect_swings(t, hands, sh, TORSO)
    assert len(swings) == 2 and swings[0].end_t <= swings[1].start_t


# ---------------------------------------------------------------- layout
def _frame(h=256, w=118, tile=(80, 200)):
    f = np.full((h, w, 3), 15, np.uint8)
    f[tile[0]:tile[1] + 1] = 120
    return f


def test_find_video_rows_basic_and_dark_gap_bridged():
    assert ss.find_video_rows(_frame()) == (80, 200)
    f = _frame()
    f[130:136] = 10                      # dark sky/night rows inside the tile
    assert ss.find_video_rows(f) == (80, 200)


def test_find_video_rows_rejects_ui_only_fullscreen_and_tiny():
    assert ss.find_video_rows(np.full((256, 118, 3), 12, np.uint8)) is None
    assert ss.find_video_rows(np.full((256, 118, 3), 240, np.uint8)) is None  # white app screen
    assert ss.find_video_rows(_frame(tile=(100, 120))) is None


def test_stable_spans_split_on_scroll_cut_and_short():
    t = np.arange(300) / 60.0
    rows = [(80, 200)] * 100 + [(80 + i, 200 + i) for i in range(1, 30)] + [None] * 10 \
        + [(60, 180)] * 161
    cut = np.zeros(300, bool)
    cut[250] = True
    spans = ss.stable_spans(rows, t, cut_flags=cut)
    # scroll frames (tile moves each frame) and the 0.8 s tail after the cut are dropped
    assert [(s.start, s.end) for s in spans] == [(0, 101), (139, 249)]
    assert all(t[s.end] - t[s.start] >= 1.0 for s in spans)
    assert spans[0].top == 80 and spans[1].top == 60


def test_frame_changes_dup_and_cut():
    g = np.zeros((5, 8, 8), np.uint8)
    g[1] = g[0]                      # duplicate
    g[2] = g[1] + 5                  # small change
    g[3] = 200                       # hard cut
    g[4] = g[3]
    dup, cut = ss.frame_changes(g)
    assert dup.tolist() == [True, True, False, False, True]
    assert cut.tolist() == [False, False, False, True, False]


def test_duplicate_signature():
    t, h, sh = synth_track([1.0], seed=1)
    ctr = np.column_stack([np.full(len(t), 500.0), np.full(len(t), 520.0)])
    a = ss.trajectory_signature(h, ctr, TORSO)
    b = ss.trajectory_signature(h + 0.5, ctr, TORSO)
    assert ss.is_duplicate(a, b)
    t2, h2, _ = synth_track([1.0], back=1.4, down=0.5)
    c = ss.trajectory_signature(h2, ctr[:len(t2)], TORSO)
    assert ss.is_duplicate(a, a) and not np.isnan(c).any()
    assert not ss.is_duplicate(a, np.full_like(a, np.nan))


def test_pose_jump_cuts_finds_loop_restart_not_fast_swing():
    t, hands, _ = synth_track([1.0])
    n = len(t)
    xy = np.stack([hands, hands + [20, 50], hands + [-10, 90]], axis=1)   # (n,3,2) landmarks
    assert ss.pose_jump_cuts(xy, TORSO).size == 0                         # real motion: no cut
    xy2 = xy.copy()
    xy2[200:] += np.array([180.0, -60.0])                                 # teleport at frame 200
    assert ss.pose_jump_cuts(xy2, TORSO).tolist() == [200]
    xy2[50, :, :] = np.nan                                                # NaN rows are ignored
    assert 50 not in ss.pose_jump_cuts(xy2, TORSO)
    assert ss.pose_jump_cuts(xy[:1], TORSO).size == 0
