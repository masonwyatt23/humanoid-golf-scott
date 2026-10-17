"""Generate data/references/pro_swing_profiles.json (published style-profile stats, cited).

Run: python scripts/gen_pro_swing_profiles.py
All numbers are copied from the cited public sources (fetched 2026-10-17, America/New_York) or
marked unverified. STYLE PROFILES ONLY: not models/simulations of real persons.
Deterministic: no timestamps in output.
"""
import json, os

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "data", "references", "pro_swing_profiles.json")

S = {  # id -> (title, url, how retrieved, terms)
 "trackman_guide": ("TrackMan Pro quick-user-guide terms (tour avg driver CHS 113, ball 167, smash 1.48; notes Tiger Woods CHS ~124, ball ~184)", "https://hankhaney.com/app/uploads/2019/01/TrackmanTERMS.pdf", "search_snippet", "Third-party hosted vendor PDF; cite numbers only"),
 "trackman_tour_avg_pdf": ("TrackMan PGA Tour averages PDF (reused from power_profile_350yd)", "https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf", "fetched_pdf", "TrackMan reference table; numbers cited only"),
 "golfdigest_tiger_tempo": ("Golf Digest: Tiger's Tour Tempo 27/9 frames (to 1997) -> 24/8 (2002 on); 3:1", "https://www.golfdigest.com/story/tiger-woods-tempo-golf-swing", "search_snippet", "Media; numbers cited only"),
 "golfweek_tiger_2018": ("Golfweek 2018: Tiger TrackMan rounds, CHS 118-120, ball 178-181, smash 1.51, launch 11-16, spin 1.9-3.0k", "https://golfweek.usatoday.com/story/sports/golf/2018/02/20/deciphering-golf-speak-is-a-key-to-custom-fitting-for-drivers/76627487007/", "search_snippet", "Media; numbers cited only"),
 "golfwrx_tiger_forum": ("GolfWRX forum: Tiger 125 mph/185 mph/1.48/11 deg/2200 rpm (undated forum post quoting a third-party page)", "https://forums.golfwrx.com/topic/887262-tiger-woods-trackman/", "search_snippet", "Forum post; LOW reliability"),
 "chroniclelive_xfactor": ("Chronicle Live 'Tips from the Tour': Tiger ~95 deg shoulders vs ~25 deg hips (X-factor ~70) -- secondary, undated, unsourced", "https://www.chroniclelive.co.uk/sport/other-sport/tips-from-the-tour-1614259", "search_snippet", "Media; LOW reliability"),
 "golfloopy_tempo": ("Golf Loopy: Scott 2014 swings (30 fps video) 0.8 s back / 0.27 s down, 3:1, same for iron & driver; notes Tiger/Rory/others similar", "http://www.golfloopy.com/adam-scott-golf-swing-tempo/", "search_snippet", "Blog; numbers cited only"),
 "golfaustralia_scott": ("Golf Australia: Scott CHS ~120-122 mph, tempo ~56 BPM", "https://www.golfaustralia.com.au/news/breaking-80-tick-tick-tempo-for-consistency-427970", "search_snippet", "Media; numbers cited only"),
 "golfdigest_minna_scott": ("Golf Digest Japan (minna): Scott TrackMan 53.9 m/s CHS (~120.6 mph), attack angle -1.1 deg, near-square face-to-path, path ~on-plane (one measured shot)", "https://www.golfdigest-minna.jp/_ct/17311277", "search_snippet", "Media (Japanese); numbers cited only; single measured driver shot, year unclear (circa 2019)"),
 "sportsbox_scott": ("Sportsbox: Adam Scott smooth swing (benchmarks: chest turn ~100 deg great / >90 good; pelvis sway ~0 in at top; sway 3-6 in & sway gap -4 to -8 in at impact for tour players)", "https://help.sportsbox.ai/adam-scotts-smooth-swing-achieving-tempo-power", "search_snippet", "Vendor help page; numbers cited only. Benchmarks are generic tour checkpoints, not clearly Scott's measured values"),
 "sportsbox_bryson": ("Sportsbox: DeChambeau case study (CHS 128 mph 96th pct vs tour group avg 117; chest/pelvis turn max 97th pct; X-factor max 84th pct; pelvis speed 51st, chest speed 95th, arm/hand speed 92nd pct)", "https://help.sportsbox.ai/dechambeaus-swing", "fetched", "Vendor page (Sportsbox partner content); numbers cited only; video-AI derived, not radar"),
 "sportsbox_report_pdf": ("Sportsbox Bryson driver report PDF (pelvis 506, thorax 961, arm 1292 deg/s; reused from power_profile_350yd, unofficial host)", "https://moccasin-micheline-88.tiiny.site/Bryson-Driver-Swing-Score-Report-1.pdf", "fetched_pdf", "Unofficial host of vendor report; numbers cited only; treat as indicative"),
 "golfcom_bryson_setup": ("GOLF.com Apr 2025: Bryson driver 5.5 deg / 59 deg lie / 45 in / Krank Formula Fire LD / jumbo grip; coach Dahlquist: path ~4-5 deg in-to-out, attack angle +4-5 deg, square face when swinging well", "https://golf.com/gear/drivers/bryson-dechambeaus-driver-setup-liv-miami/", "fetched", "Media; numbers cited only"),
 "golfcom_bryson_manzella": ("GOLF.com Jun 2025 (Manzella): Bryson high hands, oversize grips, small left-wrist hinge, wide arc, weak lead-hand grip, across-the-line top", "https://golf.com/instruction/driving/six-steps-crush-ball-like-bryson-dechambeau/", "fetched", "Media instruction opinion; qualitative"),
 "golfcom_persimmon": ("GOLF.com: Bryson 2024 avg ball speed ~172.2 mph (derived), tour avg 173.64 (reused from power_profile_350yd)", "https://golf.com/gear/how-far-bryson-dechambeau-hit-persimmon-open/", "fetched", "Media; secondary"),
 "yahoo_bryson_146": ("Yahoo Sports (via search snippet): Bryson driver CHS has reached 146.9 mph (peak, context unclear)", "https://sports.yahoo.com/article/bryson-dechambeaus-driver-distance-u-033739908.html", "search_snippet", "Media; peak not average; unverified context"),
 "swingman_chs_2025": ("Swing Man Golf: 2025 PGA Tour avg driver club-head speed ranking (Gotterup 124.7, Rory 123.33, Scott 120.19, Scheffler 120.03; 180 players) -- third-party transcription of PGA Tour stats", "https://swingmangolf.com/2025-pga-tour-club-head-speed-rankings/", "fetched", "Third-party blog transcription of PGA Tour data; numbers cited only; not independently checked against pgatour.com"),
 "golfcom_gotterup": ("GOLF.com: Gotterup 2025 CHS avg 124.52 mph (5th), ball speed 184.16 mph (11th), driving distance 317 yd; says he has pushed ball speed >200 mph (self-reported)", "https://golf.com/news/chris-gotterup-heater-3m-open/", "search_snippet", "Media; numbers cited only"),
 "golfdigest_gotterup_keys": ("Golf Digest: Gotterup 'big turn, let it rip'; straightens trail leg, weight to trail heel, hard lead-foot push, spins out lead foot", "https://www.golfdigest.com/story/learn-chris-gotterup-keys-to-exceeding-speed-limit", "search_snippet", "Media; qualitative"),
 "golfdigest_gotterup_steep": ("Golf Digest 2-minute clinic: Gotterup driver ball forward, head behind ball, head turns slightly away, trail leg straightens, flatter backswing", "https://www.golfdigest.com/how-to/2-minute-clinic/three-ways-to-fix-a-steep-swing-chris-gotterup", "search_snippet", "Media; qualitative"),
 "aus_golfdigest_gotterup": ("Australian Golf Digest: Gotterup natural fade, weak trail-hand grip, shoulder alignment not too open, steepness watch", "https://www.australiangolfdigest.com.au/chris-gotterup-put-my-game-to-work-for-you/", "search_snippet", "Media; qualitative"),
 "yt_gotterup_coach": ("YouTube coach analysis of Gotterup (transcript): ball slightly further back than 'traditional', some forward shaft lean, little lateral sway -- one coach's opinion, conflicts with Golf Digest 'ball forward'", "https://www.youtube.com/watch?v=FGIvPaTBQOI", "search_snippet", "Video commentary (only the text snippet was read; NO video downloaded); LOW reliability"),
 "cheetham_2008": ("Cheetham et al., Science and Golf V: kinematic sequence, 19 pros (CHS 109 mph) 3-D EM: peak pelvis 477+-53, thorax 727+-61, arm 980+-68, club 2254+-68 deg/s; peak times before impact pelvis 87, thorax 68, arm 65 ms", "http://www.waddengolfacademy.com/biomechanics/Cheetham%20Rose%20Neal%20Comparison_of_Kinematic_Sequence.pdf", "fetched", "Published proceedings chapter hosted by academy; numbers cited only"),
 "diva_elite_driver": ("DiVA thesis 'Relationships between golf swing kinematics and driver performance in elite golfers' (CHS 46.0+-4.3 m/s ~103 mph; pelvis 475+-75, thorax 708+-70, arm 1055+-149 deg/s; X-factor 54.9+-7.9 deg; pelvis TOB -39+-8.9, thorax TOB -92.4+-25.3 deg)", "https://www.diva-portal.org/smash/get/diva2:1242118/FULLTEXT01.pdf", "search_snippet", "Open-access thesis; numbers cited only"),
 "grober_tempo": ("Grober et al. 'Towards a Biomechanical Understanding of Tempo' (12 pros: backswing:downswing ratio ~2.5-3.5, mean ~3.0; 30 Hz video quantizes ratios)", "https://www.tourtempoforce.com/wp-content/uploads/2020/07/Towards_a_Biomechanical_Understanding_of_Tempo_in_the_Golf_Swing.pdf", "search_snippet", "Preprint hosted by Tour Tempo; numbers cited only"),
 "pebble_tempo": ("Pebble Swing summary: PGA pro accelerometer 724+-23 ms back / 248+-4 ms down (~2.9:1); other pros 1.9-3.4:1", "https://useswingiq.com/learn/golf-swing-tempo/", "search_snippet", "Secondary summary; numbers cited only"),
 "repo_synth_styles": ("Repo synthetic style parameters (data/generate_synthetic_scott.py): public-range APPROXIMATIONS written by the project, not measurements", "repo:data/generate_synthetic_scott.py", "read_locally", "Project-internal"),
 "power350": ("Repo power_profile_350yd_targets.json (commit 5b71460): tour/long-drive bands and sources", "repo:data/references/power_profile_350yd_targets.json", "read_locally", "Project-internal"),
}

def f(unit, target=None, mn=None, mx=None, src=(), conf="low", unv=False, note=""):
    if target is None and mn is None and mx is None:
        unv = True
    return {"unit": unit, "min": mn, "target": target, "max": mx, "source_ids": list(src),
            "confidence": conf, "unverified": unv, "note": note}

U = lambda unit, note: f(unit, unv=True, conf="none", note=note)

P = {}

P["tour_average"] = {
 "label": "PGA Tour / elite-golfer reference (population, not a person)", "kind": "population",
 "features": {
  "tempo_ratio": f("ratio", 3.0, 2.5, 3.5, ["grober_tempo", "golfloopy_tempo", "pebble_tempo"], "medium", note="Tour Tempo 3:1 (30 fps frame counts quantize it); high-rate measurement 2.5-3.5."),
  "backswing_s": f("s", 0.75, 0.70, 0.80, ["golfloopy_tempo", "pebble_tempo"], "medium", note="0.72-0.80 s takeaway->top."),
  "downswing_s": f("s", 0.26, 0.25, 0.27, ["golfloopy_tempo", "pebble_tempo"], "medium", note="~0.25-0.27 s top->impact."),
  "x_factor_top_deg": f("deg", 54.9, 47.0, 62.8, ["diva_elite_driver"], "medium", note="Elite-golfer mean+-SD 54.9+-7.9 (min/max = +-1 SD); other sources cite 32-45 deg: definitions vary."),
  "pelvis_turn_top_deg": f("deg", 39.0, 30.1, 47.9, ["diva_elite_driver"], "medium", note="mean +-1 SD (abs value)."),
  "thorax_turn_top_deg": f("deg", 92.4, 67.1, 117.7, ["diva_elite_driver"], "medium", note="mean +-1 SD (abs value)."),
  "pelvis_peak_speed_dps": f("deg/s", 477, 424, 530, ["cheetham_2008"], "medium", note="+-1 SD; DiVA elite: 475+-75."),
  "thorax_peak_speed_dps": f("deg/s", 727, 666, 788, ["cheetham_2008"], "medium", note="+-1 SD; DiVA elite: 708+-70."),
  "arm_peak_speed_dps": f("deg/s", 980, 912, 1048, ["cheetham_2008"], "medium", note="lead upper arm, +-1 SD; DiVA elite arm 1055+-149."),
  "club_head_speed_mph": f("mph", 113, None, None, ["trackman_guide", "trackman_tour_avg_pdf"], "high", note="TrackMan tour driver average."),
  "ball_speed_mph": f("mph", 167, None, None, ["trackman_guide", "trackman_tour_avg_pdf"], "high", note="TrackMan tour average (GOLF.com cites 173.6 for a later year)."),
  "smash_factor": f("ratio", 1.48, None, None, ["trackman_guide", "trackman_tour_avg_pdf"], "high"),
  "launch_angle_deg": f("deg", 10.9, None, None, ["trackman_tour_avg_pdf", "power350"], "medium"),
  "spin_rate_rpm": f("rpm", 2686, None, None, ["trackman_tour_avg_pdf", "power350"], "medium"),
  "attack_angle_deg": f("deg", -1.3, None, None, ["trackman_tour_avg_pdf", "power350"], "medium"),
 },
 "setup": {"note": "No numeric tour-average stance/ball-position values were retrieved; do not infer."},
}

P["tiger_woods_style"] = {
 "label": "Tiger Woods-style profile (published-stat style profile; NOT a model of the person)", "kind": "style_profile",
 "features": {
  "tempo_ratio": f("ratio", 3.0, 2.9, 3.1, ["golfdigest_tiger_tempo"], "medium", note="27/9 frames until 1997, 24/8 from ~2002 (both exactly 3:1 by 30 fps frame counting; real ratio likely 2.8-3.2)."),
  "backswing_s": f("s", 0.80, None, None, ["golfdigest_tiger_tempo", "golfloopy_tempo"], "low", note="24 frames/30 fps = 0.80 s; Golf Loopy says Tiger at his best ~0.8 s."),
  "downswing_s": f("s", 0.267, None, None, ["golfdigest_tiger_tempo", "golfloopy_tempo"], "low", note="8 frames/30 fps (+-1 frame = +-0.033 s)."),
  "x_factor_top_deg": f("deg", None, None, None, ["chroniclelive_xfactor"], "low", True, "Unsourced media claim ~70 deg (95 shoulders - 25 hips); not usable as a target."),
  "club_head_speed_mph": f("mph", 120, 118, 125, ["trackman_guide", "golfweek_tiger_2018", "golfwrx_tiger_forum"], "low", note="Era/club dependent: 118 (2012), 118-120 (2018), ~124-125 (older guide/forum). Target = midpoint, not a measurement."),
  "ball_speed_mph": f("mph", 180, 175, 185, ["trackman_guide", "golfweek_tiger_2018", "golfwrx_tiger_forum"], "low"),
  "smash_factor": f("ratio", 1.49, 1.47, 1.51, ["golfweek_tiger_2018", "golfwrx_tiger_forum"], "low"),
  "launch_angle_deg": f("deg", 11.3, 10.9, 16.5, ["golfweek_tiger_2018", "golfwrx_tiger_forum"], "low", note="11 typical; 16.5 outlier shot."),
  "spin_rate_rpm": f("rpm", 2300, 1900, 3000, ["golfweek_tiger_2018", "golfwrx_tiger_forum"], "low"),
  "pelvis_peak_speed_dps": U("deg/s", "No published per-player value retrieved."),
  "thorax_peak_speed_dps": U("deg/s", "No published per-player value retrieved."),
  "arm_peak_speed_dps": U("deg/s", "No published per-player value retrieved."),
  "attack_angle_deg": U("deg", "Not retrieved."),
 },
 "setup": {"notes": "Not retrieved for Tiger: stance width, ball position, shaft lean. Left unverified (no fabricated values)."},
}

P["adam_scott_style"] = {
 "label": "Adam Scott-style profile (published-stat style profile; NOT a model of the person)", "kind": "style_profile",
 "features": {
  "tempo_ratio": f("ratio", 3.0, 2.8, 3.2, ["golfloopy_tempo", "golfaustralia_scott"], "medium", note="3:1 from 30 fps video (quantized)."),
  "backswing_s": f("s", 0.80, None, None, ["golfloopy_tempo"], "low", note="2014 video, 30 fps."),
  "downswing_s": f("s", 0.27, None, None, ["golfloopy_tempo"], "low"),
  "thorax_turn_top_deg": f("deg", 100, 90, 100, ["sportsbox_scott"], "low", True, "Sportsbox: ~100 deg 'excellent', >90 good. Appears to be a benchmark, not confirmed Scott measurement -> unverified."),
  "pelvis_sway_top_in": f("in", 0, None, 0, ["sportsbox_scott"], "low", True, "~0 in at top (Sportsbox benchmark, Scott-attributed in the article, not confirmed measurement)."),
  "pelvis_sway_impact_in": f("in", 4.5, 3, 6, ["sportsbox_scott"], "low", True, "generic tour checkpoint 3-6 in; sway gap -4 to -8 in."),
  "club_head_speed_mph": f("mph", 120.2, 120.0, 122.0, ["swingman_chs_2025", "golfaustralia_scott", "golfdigest_minna_scott"], "medium", note="2025 avg 120.19; Golf Australia 120-122; one TrackMan shot 53.9 m/s = 120.6."),
  "attack_angle_deg": f("deg", -1.1, None, None, ["golfdigest_minna_scott"], "low", note="One TrackMan driver shot (circa 2019)."),
  "ball_speed_mph": U("mph", "Not retrieved (a TrackMan report with 157.6 mph was anonymous; NOT attributed to Scott)."),
  "smash_factor": U("ratio", "Not retrieved."),
  "launch_angle_deg": U("deg", "Not retrieved."),
  "spin_rate_rpm": U("rpm", "Not retrieved."),
  "x_factor_top_deg": U("deg", "Not retrieved. Repo synthetic style uses ~55 as an assumption (repo_synth_styles)."),
  "pelvis_peak_speed_dps": U("deg/s", "Not retrieved."),
  "thorax_peak_speed_dps": U("deg/s", "Not retrieved."),
  "arm_peak_speed_dps": U("deg/s", "Not retrieved."),
 },
 "setup": {"notes": "Quiet pelvis / stable head (Sportsbox qualitative). Stance width, ball position unverified."},
}

P["bryson_dechambeau_style"] = {
 "label": "Bryson DeChambeau-style profile (published-stat style profile; NOT a model of the person)", "kind": "style_profile",
 "features": {
  "tempo_ratio": U("ratio", "No published value retrieved."),
  "club_head_speed_mph": f("mph", 128, 125, 140, ["sportsbox_bryson", "yahoo_bryson_146", "power350"], "medium", note="Video-AI avg 128 (vendor, not radar); 146.9 reported as a peak (context unverified)."),
  "ball_speed_mph": f("mph", 172.2, 172.2, 195, ["golfcom_persimmon", "power350"], "low", note="2024 season avg ~172.2 (derived); '195+ ball speed' seen in equipment testing (reporter)."),
  "smash_factor": U("ratio", "No Bryson-specific value retrieved."),
  "launch_angle_deg": U("deg", "No Bryson-specific value retrieved."),
  "spin_rate_rpm": U("rpm", "No Bryson-specific value retrieved."),
  "attack_angle_deg": f("deg", 4.5, 4.0, 5.0, ["golfcom_bryson_setup"], "medium", note="Coach quote (Dahlquist), working number when swinging well; path ~4-5 deg in-to-out."),
  "x_factor_top_deg": f("deg", None, None, None, ["sportsbox_bryson"], "low", True, "Only percentile (84th pct of tour sample); value not published."),
  "pelvis_turn_top_deg": f("deg", None, None, None, ["sportsbox_bryson"], "low", True, "Only percentile (97th pct)."),
  "thorax_turn_top_deg": f("deg", None, None, None, ["sportsbox_bryson"], "low", True, "Only percentile (97th pct)."),
  "pelvis_peak_speed_dps": f("deg/s", 506, 440, 590, ["sportsbox_report_pdf", "sportsbox_bryson", "cheetham_2008"], "medium", note="51st pct of tour; same as tour-typical."),
  "thorax_peak_speed_dps": f("deg/s", 961, 750, 1000, ["sportsbox_report_pdf", "sportsbox_bryson"], "medium", note="95th pct; tour range 754-857 per vendor report."),
  "arm_peak_speed_dps": f("deg/s", 1292, 1050, 1400, ["sportsbox_report_pdf", "sportsbox_bryson"], "medium", note="92nd pct."),
 },
 "setup": {
  "driver_length_in": f("in", 45.0, 45.0, 48.0, ["golfcom_bryson_setup"], "high", note="45 in EOG (Krank, 5.5 deg loft, 59 deg lie); 48 in rule max."),
  "driver_loft_deg": f("deg", 5.5, 4.0, 5.5, ["golfcom_bryson_setup"], "high", note="LA Golf prototype 4 deg seen in testing."),
  "grip": "Oversize/jumbo grip; weak lead-hand grip (GOLF.com Manzella, qualitative)",
  "posture_hands": "High hands at address, small left-wrist hinge, toe-up at takeaway, wide arc, across-the-line top (qualitative, golfcom_bryson_manzella)",
  "stance_width": U("in", "Not retrieved."),
  "ball_position": U("", "Not retrieved."),
  "shaft_lean": U("deg", "Not retrieved."),
 },
}

P["chris_gotterup_style"] = {
 "label": "Chris Gotterup-style profile (published-stat style profile; NOT a model of the person)", "kind": "style_profile",
 "features": {
  "tempo_ratio": U("ratio", "Described as fast/aggressive; no timing published."),
  "club_head_speed_mph": f("mph", 124.6, 124.5, 125.2, ["swingman_chs_2025", "golfcom_gotterup"], "medium", note="2025 avg 124.52 (GOLF.com) / 124.7 (third-party); a 2022-23 article cites 125.21 (SIM2)."),
  "ball_speed_mph": f("mph", 184.2, None, 200, ["golfcom_gotterup"], "medium", note="2025 avg 184.16 (11th on Tour); >200 mph max is self-reported."),
  "smash_factor": f("ratio", 1.48, None, None, ["golfcom_gotterup"], "low", True, "Derived 184.16/124.52 = 1.479; mixes two sources' averages (not same-shot)."),
  "driving_distance_yd": f("yd", 317, None, None, ["golfcom_gotterup"], "medium", note="PGA Tour driving distance avg 317 yd (8th)."),
  "launch_angle_deg": U("deg", "Not retrieved."),
  "spin_rate_rpm": U("rpm", "Not retrieved."),
  "attack_angle_deg": U("deg", "Not retrieved."),
  "x_factor_top_deg": U("deg", "Not retrieved (qualitatively 'as big a turn as I can')."),
  "pelvis_peak_speed_dps": U("deg/s", "Not retrieved."),
  "thorax_peak_speed_dps": U("deg/s", "Not retrieved."),
  "arm_peak_speed_dps": U("deg/s", "Not retrieved."),
 },
 "setup": {
  "ball_position": "Forward in stance per Golf Digest; one YouTube coach calls it a bit back of 'traditional' with some forward shaft lean -> sources conflict, unverified",
  "head_and_turn": "Head slightly behind ball and turns slightly away on takeaway; trail leg straightens; weight to trail heel (Golf Digest, qualitative)",
  "downswing": "Hard push off lead foot, lead foot may spin out (Golf Digest, qualitative)",
  "grip": "Fairly weak trail-hand grip, natural fade (Australian Golf Digest)",
  "stance_width": U("in", "Not retrieved."),
  "shaft_lean": U("deg", "Not retrieved numerically."),
 },
}

P["scottie_scheffler_style"] = {
 "label": "Scheffler-style profile (published CHS + repo synthetic approximation; NOT a model of the person)", "kind": "style_profile",
 "features": {
  "club_head_speed_mph": f("mph", 120.0, None, None, ["swingman_chs_2025"], "medium", note="2025 avg 120.03."),
  "tempo_ratio": f("ratio", 2.4, None, None, ["repo_synth_styles"], "low", True, "REPO ASSUMPTION for synthetic generator, not a measurement."),
  "x_factor_top_deg": f("deg", 54, None, None, ["repo_synth_styles"], "low", True, "Repo assumption (92 thorax - 38 pelvis)."),
 },
 "setup": {},
}

P["rory_mcilroy_style"] = {
 "label": "Rory-style profile (published CHS + repo synthetic approximation; NOT a model of the person)", "kind": "style_profile",
 "features": {
  "club_head_speed_mph": f("mph", 123.3, None, None, ["swingman_chs_2025"], "medium", note="2025 avg 123.33."),
  "tempo_ratio": f("ratio", 2.8, None, None, ["repo_synth_styles"], "low", True, "REPO ASSUMPTION, not a measurement."),
  "x_factor_top_deg": f("deg", 48, None, None, ["repo_synth_styles"], "low", True, "Repo assumption (100 thorax - 52 pelvis)."),
 },
 "setup": {},
}

doc = {
 "schema": "pro_swing_profiles/v1",
 "generated_by": "scripts/gen_pro_swing_profiles.py",
 "purpose": "Internal reference for Mason-vs-profile comparison. STYLE PROFILES from published stats; not simulations of real persons.",
 "notes": [
  "Each feature: unit, min/target/max (plausibility band, NOT a measurement of the person), source_ids, confidence (high/medium/low/none), unverified.",
  "unverified=true -> no verified published value, or value is an assumption/derived from mixed sources; do not use as a target without confirming.",
  "source 'verified' field: fetched = page text read; fetched_pdf = PDF read; search_snippet = only a search-result excerpt was read (weaker); read_locally = repo file.",
  "Handedness: all values are magnitudes; mirror for a left-handed golfer. Frame-count tempo values come from ~30 fps video and are quantized (+-1 frame).",
  "No player video was downloaded or scraped. Quoted facts are short numeric citations only.",
 ],
 "sources": {k: {"title": v[0], "url": v[1], "verified": v[2], "terms": v[3]} for k, v in S.items()},
 "profiles": P,
 "legal_likeness_cautions": [
  "Use 'style profile' language only. These are statistical summaries of published numbers, not simulations, avatars or endorsements of real persons.",
  "Do not use any player's name, image or likeness in commercial product marketing, UI, model names or app-store copy without written permission; names are for internal reference/file labels only.",
  "Do not redistribute vendor/media content (Sportsbox, TrackMan, GOLF.com etc.): numbers with citations only, no copied text, images or reports.",
  "Real-person biometric-like data (swing kinematics) may carry right-of-publicity / privacy issues in some jurisdictions; the repo uses only published aggregate numbers.",
  "Recommend counsel review before any external release, training-data licensing statement or marketing claim ('swings like X').",
 ],
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as fh:
    json.dump(doc, fh, indent=1, sort_keys=True)
    fh.write("\n")
print("wrote", OUT)
