"""Frames -> mp4 with HUD (ffmpeg drawtext). python render_blender/assemble.py FRAMES_DIR OUT.mp4 [--fps 24] [--clip test]
HUD numbers are from swing_v3.json (REAL sim measurements of the rendered seed). Labels the body as a generic humanoid and the swing as scripted (not learned)."""
import sys, json, subprocess, argparse, os
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("frames"); ap.add_argument("out"); ap.add_argument("--fps", type=int, default=24); ap.add_argument("--clip", default="test"); a = ap.parse_args()
J = json.loads((Path(__file__).parent / "swing_v3.json").read_text()); S = J["summary"]
mph = S["impact_club_speed"] * 2.23694; launch = S["launch_elev_deg"]; carry = S["carry"]
imp_t = {"test": 7.0, "test2": 7.0}.get(a.clip, 10.0)   # video time when impact slow-mo begins
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT):
    import glob; g = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True); FONT = g[0] if g else ""
def dt(text, x, y, size, color="white", en=None):
    e = f":enable='{en}'" if en else ""
    return f"drawtext=fontfile={FONT}:text='{text}':x={x}:y={y}:fontsize={size}:fontcolor={color}:box=1:boxcolor=black@0.45:boxborderw=10{e}"
f = [dt("LEFT-HANDED DRIVER  |  MuJoCo sim + Blender", 30, 24, 26),
     dt("Generic humanoid, Figure/Optimus-like proportions (not an official model)  -  scripted swing, not learned", 30, "h-44", 18, "0xcccccc"),
     dt(f"CLUB SPEED {mph:.1f} mph", 30, 70, 32, "0x66ccff", f"gte(t,{imp_t+1.0})"),
     dt(f"LAUNCH {launch:.1f} deg", 30, 118, 32, "0x66ccff", f"gte(t,{imp_t+1.6})"),
     dt(f"CARRY {carry:.1f} m", 30, 166, 32, "0xffdd66", f"gte(t,{imp_t+3.0})")]
cmd = ["ffmpeg", "-y", "-framerate", str(a.fps), "-i", os.path.join(a.frames, "f%05d.png"), "-vf", ",".join(f), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", a.out]
print(" ".join(cmd[:6])); subprocess.run(cmd, check=True)
