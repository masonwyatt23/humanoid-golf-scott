"""
Render slow-motion showcase + reel of the CURRENT BEST checkpoint (per results/leaderboard.json).

    python -m eval.render_showcase [--swings 12] [--seed 5000] [--model NAME] [--reel-top 4]

Outputs: results/videos/showcase_latest.mp4 (best swing, side-on | down-the-line, slow motion)
         results/videos/reel_latest.mp4    (top swings of N, best first)
         results/videos/showcase_latest.json (the measured numbers shown in the overlay)

* GL backend: tries EGL, then OSMesa; if neither loads it re-executes itself under xvfb-run with
  MUJOCO_GL=glfw (needs `pip install glfw` + Xvfb). On this box EGL/OSMesa libs are missing, so glfw+Xvfb is used.
* Swings = deterministic policy, seeds seed..seed+N-1 (reset randomization gives variety). Swings are ranked by
  (true club-ball contact, carry, final ball x); the top one is the showcase. The chosen swing is re-run for rendering
  and the replay is checked against the selection pass.
* Overlay shows MEASURED sim values for that swing only, live-so-far: impact club speed (club_head geom speed at first
  contact), peak ball speed so far, carry (n/a until the ball lands after being airborne; n/a if 0), ball lateral y (+left).
* Slow motion: one frame every K physics steps; factor = (1/fps) / (K * timestep), printed in the overlay.
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30


def ensure_gl():
    if os.environ.get("_RS_GL"):
        return
    for be in ("egl", "osmesa"):
        r = subprocess.run([sys.executable, "-c", "import mujoco;"
                            "from env.humanoid_golf_env import HumanoidGolfEnv as E;"
                            "e=E();mujoco.Renderer(e.model,64,64)"], cwd=ROOT, env={**os.environ, "MUJOCO_GL": be},
                           capture_output=True)
        if r.returncode == 0:
            os.environ["MUJOCO_GL"] = be; os.environ["_RS_GL"] = be; return
    if not shutil.which("xvfb-run"):
        raise SystemExit("no usable GL backend (EGL/OSMesa failed, xvfb-run missing)")
    env = {**os.environ, "MUJOCO_GL": "glfw", "_RS_GL": "glfw"}
    os.execvpe("xvfb-run", ["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", sys.executable, "-m", "eval.render_showcase", *sys.argv[1:]], env)


def pick_model(name, pick="best"):
    lb = json.loads((ROOT / "results/leaderboard.json").read_text())
    ms = lb["models"]
    if name:
        m = next(m for m in ms if name in m["names"])
    else:
        best = {"best": lb["best_model"], "best_left": lb.get("best_left"), "best_qualifying": lb.get("best_qualifying")}[pick]
        if best is None:
            raise SystemExit(f"no model for pick={pick} (none meets the leaderboard criterion)")   # best TRAINED checkpoint (scripted baseline excluded)
        m = next(m for m in ms if m["names"] == best)
    return m, lb


def rollout(env, model, seed, frame_cb=None):
    obs, _ = env.reset(seed=seed); done = False; info = {}
    if frame_cb: frame_cb(env, None)
    while not done:
        a, _ = model.predict(obs, deterministic=True)
        obs, _, te, tr, info = env.step(a); done = te or tr
        if frame_cb: frame_cb(env, info)
    return info


def score(info):
    return (bool(info.get("true_contact")), float(info.get("carry", 0)), float(info["ball_distance"]))


class Recorder:
    def __init__(self, env, K, label, writer):
        import mujoco, cv2
        self.mj, self.cv2, self.env, self.K, self.label, self.w = mujoco, cv2, env, K, label, writer
        self.r = mujoco.Renderer(env.model, 480, 640)
        self.cams = []
        for name, az in (("SIDE-ON", 90), ("DOWN-THE-LINE", 0)):
            c = mujoco.MjvCamera(); c.type = mujoco.mjtCamera.mjCAMERA_FREE
            c.lookat[:] = (0.9, 0.0, 0.45); c.distance = 3.4; c.azimuth = az; c.elevation = -8
            self.cams.append((name, c))
        self.trail, self.n, self.last = [], 0, None
        self.slow = (1.0 / FPS) / (K * env.model.opt.timestep)
        self.orig = None
        self.peak_club = 0.0
        self.banner = None   # compare mode: list of header lines (drawn top strip)
        self.ft = None       # compare mode: FlightTracker (launch elevation after contact)

    def install(self):
        self.orig = self.mj.mj_step
        def wrapped(m, d, *a, **k):
            self.orig(m, d, *a, **k)
            v = self.env._club_speed()   # every physics substep; non-physical (>100 m/s / non-finite) samples ignored
            if v == v and v <= 100.0: self.peak_club = max(self.peak_club, v)
            self.n += 1
            if self.n % self.K == 0: self.frame()
        self.mj.mj_step = wrapped

    def uninstall(self):
        self.mj.mj_step = self.orig

    def frame(self, hold=1):
        e = self.env
        bp = e.data.xpos[e._ball_id].copy()
        if not self.trail or (abs(bp - self.trail[0]).max() > 0.01 and abs(bp - self.trail[-1]).max() > 0.02):
            if self.trail or abs(bp[0] - 0.0) > 0: self.trail.append(bp)
        stats = dict(club=e.impact_club_speed if e.true_contact else None, ball=e.peak_ball_speed,
                     carry=e.carry if e._landed else 0.0, y=float(bp[1]))
        panels = []
        for name, cam in self.cams:
            # follow the ball when it travels far (residual models fly tens of metres)
            cam.lookat[0] = 0.9 + 0.5 * max(0.0, bp[0] - 0.9); cam.distance = min(3.4 + 0.5 * max(0.0, bp[0] - 0.9), 60.0)
            self.r.update_scene(e.data, camera=cam)
            sc = self.r.scene
            for p in self.trail:
                if sc.ngeom >= sc.maxgeom: break
                g = sc.geoms[sc.ngeom]
                self.mj.mjv_initGeom(g, self.mj.mjtGeom.mjGEOM_SPHERE, [0.014, 0, 0], p, [1, 0, 0, 0, 1, 0, 0, 0, 1], [1, 0.85, 0, 1])
                sc.ngeom += 1
            img = self.r.render().copy()
            self.cv2.putText(img, name, (10, 24), self.cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            panels.append(img)
        import numpy as np
        img = np.concatenate(panels, axis=1)
        f = lambda v, u: "n/a" if v is None else f"{v:.2f} {u}"
        lines = [self.label,
                 f"Club speed @impact: {f(stats['club'], 'm/s')}   Ball speed (peak so far): {f(stats['ball'] if e.true_contact else None, 'm/s')}",
                 f"Carry: {'n/a' if stats['carry'] <= 0 else format(stats['carry'], '.2f') + ' m'}   Lateral y (+left): {stats['y']:+.2f} m   Slow-mo {self.slow:.1f}x",
                 "Measured in simulation (single swing); yellow dots = ball path"]
        if self.ft is not None:
            le = self.ft.launch_elev_deg() if e.true_contact else float("nan")
            lines[3] = f"Launch elevation (ball velocity after contact): {'n/a' if le != le else format(le, '.1f') + ' deg'}   Left-handed setup   (measured; yellow = ball path)"
        pk_mph = self.peak_club * 2.23694; pct = min(100.0, self.peak_club / 53.64 * 100)
        ov = img.copy(); self.cv2.rectangle(ov, (0, 480 - 92), (1280, 480), (0, 0, 0), -1)
        img = self.cv2.addWeighted(ov, 0.6, img, 0.4, 0)
        for i, t in enumerate(lines):
            self.cv2.putText(img, t, (10, 480 - 70 + 21 * i), self.cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, self.cv2.LINE_AA)
        # peak club-head speed progress bar toward 120 mph (measured so far this swing)
        x0, x1, y0 = 700, 1260, 480 - 80
        self.cv2.putText(img, f"Peak club-head speed: {pk_mph:.1f} mph ({self.peak_club:.2f} m/s)", (x0, y0 - 6), self.cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, self.cv2.LINE_AA)
        self.cv2.rectangle(img, (x0, y0), (x1, y0 + 18), (200, 200, 200), 1)
        self.cv2.rectangle(img, (x0, y0), (x0 + int((x1 - x0) * pct / 100), y0 + 18), (60, 200, 60), -1)
        self.cv2.putText(img, f"{pct:.1f}% of 120 mph target (53.64 m/s)", (x0, y0 + 38), self.cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, self.cv2.LINE_AA)
        if self.banner:
            ov = img.copy(); self.cv2.rectangle(ov, (0, 30), (1280, 30 + 24 * len(self.banner) + 6), (0, 0, 0), -1)
            img = self.cv2.addWeighted(ov, 0.65, img, 0.35, 0)
            for i, t in enumerate(self.banner):
                self.cv2.putText(img, t, (10, 50 + 24 * i), self.cv2.FONT_HERSHEY_SIMPLEX, 0.6, (getattr(self, 'banner_color', None) or (0, 220, 255)) if i == 0 else (255, 255, 255), 2 if i == 0 else 1, self.cv2.LINE_AA)
        for _ in range(hold): self.w.write(img)
        self.last = img


class Writer:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x480",
                                   "-r", str(FPS), "-i", "-", "-an", "-vcodec", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(path)],
                                  stdin=subprocess.PIPE)
        self.frames = 0
    def write(self, img):
        self.p.stdin.write(img.tobytes()); self.frames += 1
    def close(self):
        self.p.stdin.close(); self.p.wait()


def render_swing(env, model, seed, K, label, writer, tail_s=1.5):
    rec = Recorder(env, K, label, writer); rec.install()
    try:
        info = rollout(env, model, seed)
    finally:
        rec.uninstall()
    rec.frame(hold=int(tail_s * FPS))
    return info, rec


class ZeroPolicy:
    """Zero-residual action = the pure scripted swing (same as eval.dispersion_report scripted=True)."""
    def __init__(self, env):
        import numpy as np; self.z = np.zeros(env.action_space.shape, dtype=np.float32)
    def predict(self, obs, deterministic=True):
        return self.z, None


def compare(a):
    """Back-to-back reel: LEARNED (an3_s1) then SCRIPTED (trainer cfg). Swing = median-by-carry of N deterministic swings (all contacted+landed)."""
    from stable_baselines3 import PPO
    from eval.env_factory import make_env
    from eval.flight_tracker import FlightTracker
    import numpy as np
    lb = json.loads((ROOT / "results/leaderboard.json").read_text())
    vd = ROOT / "results/videos"; w = Writer(vd / "showcase_compare.mp4"); meta = {}
    specs = [("LEARNED (an3_s1)", "ppo_resid_v3_left_an3_s1", False), ("SCRIPTED (not learned)", "scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm]", True)]
    for title, mname, scripted in specs:
        m = next(x for x in lb["models"] if x["names"][0] == mname); d = m["modes"]["deterministic"]
        env = make_env(m["env_kwargs"]); pol = ZeroPolicy(env) if scripted else PPO.load(str(ROOT / "models" / mname))
        prev = json.loads((vd / "showcase_compare.json").read_text()) if (a.reuse and (vd / "showcase_compare.json").exists()) else {}
        if title in prev:   # reuse swing/selection from a previous full pass (selection pass is slow)
            res = [(x["seed"], dict(carry=x["carry"], final_y=x["y"], launch_elev_deg=x["launch"], true_contact=x["contact"])) for x in prev[title]["all_swings"]]
            seed, sh = prev[title]["swing_seed"], next(r[1] for r in res if r[0] == prev[title]["swing_seed"])
        else:
            res = []
            for i in range(a.swings):
                ft = FlightTracker(env).install(); rec = Recorder(env, a.K, "", type("NullW", (), {"write": lambda self, img: None})()); rec.install()
                try:
                    obs, _ = env.reset(seed=a.seed + i); ft.reset(); done = False; info = {}
                    while not done:
                        obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); done = te or tr
                finally:
                    rec.uninstall(); ft.close(); rec.r.close()
                res.append((a.seed + i, ft.summary(info)))
            ok = sorted([r for r in res if r[1]["true_contact"] and r[1]["carry"] > 0], key=lambda r: r[1]["carry"])
            seed, sh = ok[(len(ok) - 1) // 2]   # lower median by carry
        board = (f"Leaderboard (det, 50 eps): carry {d['mean_carry']:.1f} m mean | lat std {d['lateral_std']:.2f} m | miss L/R {d['left_miss_rate']*100:.0f}%/{d['right_miss_rate']*100:.0f}% | "
                 f"landed {d['landed_fraction']*100:.0f}% | peak club {d['peak_club_mph_mean']:.1f} mph | launch {d['launch_elev_mean_deg']:.1f} deg")
        ban = [f"{title}  -  ONE swing (det., seed {seed}, median-by-carry of {a.swings}); overlay below = this swing; line 2 = all-episode stats", board]
        ft = FlightTracker(env).install()
        try:
            rec = Recorder(env, a.K, "", w); rec.banner = ban; rec.ft = ft; rec.install()
            try:
                obs, _ = env.reset(seed=seed); ft.reset(); done = False; info = {}
                while not done:
                    obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); done = te or tr
            finally:
                rec.uninstall()
            rec.frame(hold=int(3.0 * FPS)); rec.r.close()   # free GL context: a 2nd live Renderer on another model rendered garbage
        finally:
            ft.close()
        sw = ft.summary(info)
        meta[title] = dict(model=mname, swing_seed=seed, selection="lower median by carry among true-contact+landed swings of %d, seeds %d.." % (a.swings, a.seed),
                           swing_carry=sw["carry"], swing_final_y=sw["final_y"], swing_launch_deg=sw["launch_elev_deg"], swing_peak_club_mph=rec.peak_club * 2.23694,
                           swing_impact_club_speed=sw["impact_club_speed"], replay_carry_matches_selection=abs(sw["carry"] - sh["carry"]) < 1e-6,
                           all_swings=[dict(seed=s_, carry=x["carry"], y=x["final_y"], launch=x["launch_elev_deg"], contact=x["true_contact"]) for s_, x in res],
                           leaderboard_det={k: d[k] for k in ("mean_carry", "lateral_std", "left_miss_rate", "right_miss_rate", "landed_fraction", "peak_club_mph_mean", "launch_elev_mean_deg")})
    w.close(); meta["frames"] = w.frames; meta["fps"] = FPS; meta["duration_s"] = w.frames / FPS; meta["slowdown"] = rec.slow
    (vd / "showcase_compare.json").write_text(json.dumps(meta, indent=1)); print(json.dumps(meta, indent=1)[:3500])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reuse", action="store_true", help="compare mode: reuse swing seeds from existing showcase_compare.json"); ap.add_argument("--compare", action="store_true", help="write results/videos/showcase_compare.mp4 (learned an3_s1 vs scripted bx0.422)")
    ap.add_argument("--swings", type=int, default=12); ap.add_argument("--seed", type=int, default=5000)
    ap.add_argument("--model", default=None); ap.add_argument("--pick", default="best", choices=["best", "best_left", "best_qualifying"]); ap.add_argument("--reel-top", type=int, default=4)
    ap.add_argument("--K", type=int, default=5, help="physics steps per frame (showcase)")
    a = ap.parse_args()
    ensure_gl()
    if a.compare:
        return compare(a)
    from stable_baselines3 import PPO
    from env.humanoid_golf_env import HumanoidGolfEnv
    m, lb = pick_model(a.model, a.pick)
    name = m["names"][0]
    from eval.env_factory import make_env
    env = make_env(m["env_kwargs"])
    pol = PPO.load(str(ROOT / "models" / name))
    sel = []
    for i in range(a.swings):
        info = rollout(env, pol, a.seed + i); sel.append((score(info), a.seed + i, info))
    sel.sort(key=lambda t: t[0], reverse=True)
    vd = ROOT / "results/videos"
    tag = f"{name} ({m['steps']//1000}k steps)"
    w = Writer(vd / "showcase_latest.mp4")
    sc, seed, info0 = sel[0]
    info, rec = render_swing(env, pol, seed, a.K, f"{tag}  seed {seed}  best of {a.swings}", w)
    w.close()
    replay_ok = abs(info["ball_distance"] - info0["ball_distance"]) < 1e-6
    meas = dict(model=name, md5=m["md5"], steps=m["steps"], seed=seed, best_of=a.swings, replay_matches_selection=replay_ok,
                true_contact=bool(info["true_contact"]), peak_club_speed=rec.peak_club, peak_club_mph=rec.peak_club * 2.23694, peak_club_pct_of_120mph=rec.peak_club / 53.64 * 100, impact_club_speed=info["impact_club_speed"],
                peak_ball_speed=info["peak_ball_speed"], carry=info["carry"], carry_landed=bool(info["carry"] > 0),
                final_ball_x=info["ball_distance"], slowdown=rec.slow, frames=w.frames,
                env_fingerprint=lb.get("env_fingerprint"), selection=[dict(seed=s, true_contact=t[0], carry=t[1], final_x=t[2]) for t, s, _ in sel])
    w = Writer(vd / "reel_latest.mp4")
    for rank, (sc_, sd, _) in enumerate(sel[:a.reel_top], 1):
        render_swing(env, pol, sd, a.K * 2, f"{tag}  #{rank} of {a.swings} swings (seed {sd})", w, tail_s=1.0)
    w.close()
    meas["reel_frames"] = w.frames; meas["reel_seeds"] = [sd for _, sd, _ in sel[:a.reel_top]]
    (vd / "showcase_latest.json").write_text(json.dumps(meas, indent=1))
    print(json.dumps({k: v for k, v in meas.items() if k != "selection"}, indent=1))


if __name__ == "__main__":
    main()
