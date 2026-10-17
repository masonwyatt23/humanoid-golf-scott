#!/usr/bin/env python3
"""Generate data/references/power_profile_350yd_targets.json (see docs/research_350yd_profile.md).

Literature/statistics values are hand-entered below with the source id they came from; each source's
`verified` field records HOW it was checked on 2026-10-16/17 (fetched page / fetched PDF / search-snippet only).
Derived numbers (humanoid requirements, actuator audit) are computed here from the MuJoCo XML.
Flight totals use env/ball_flight_analytic.py (repo prototype); cached results are embedded so the script is
deterministic and dependency-free.
Usage: python3 scripts/gen_power_profile_350yd.py [--out PATH]
"""
import argparse, json, math, os, re, sys
import xml.etree.ElementTree as ET

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
XML = os.path.join(ROOT, "env", "models", "humanoid_golf_v3.xml")
MPH, DEG = 0.44704, math.pi / 180

SOURCES = {
 "usga_equip_part2": dict(title="USGA/R&A Equipment Rules Part 2 s.1c Length (2019 rules page)", url="https://www.usga.org/equipment-standards/equipment-rules-2019/equipment-rules/part-2-rule-2.html", verified="fetched", terms="USGA web content; quoted figures only, no redistribution of text"),
 "usga_equip_faq": dict(title="USGA Equipment FAQ (48 in. max, optional Local Rule G-10 = 46 in.)", url="https://www.usga.org/equipment-standards/equipment-faq-25852.html", verified="search_snippet", terms="USGA web content; numbers cited only"),
 "randa_longer_clubs": dict(title="R&A Equipment Info for Players (>48 in. only with medical/physical need + Local Committee)", url="https://www.randa.org/en/equipment-info-for-players", verified="search_snippet", terms="R&A web content; numbers cited only"),
 "usga_ball_faq": dict(title="USGA The Golf Ball and Distance FAQ (ODS 317 yd +3 at 120 mph/10 deg/2520 rpm; 125 mph/11 deg/2220 rpm from 2028 cycle)", url="https://www.usga.org/content/usga/home-page/advancing-the-game/distance-insights/golf-ball-revised-testing-guidelines--frequently-asked-questions.html", verified="fetched", terms="USGA web content; numbers cited only"),
 "usga_ct_notice": dict(title="USGA Notice to Manufacturers - spring effect (Characteristic Time 239 us, +18 us tolerance)", url="https://www.usga.org/content/dam/usga/pdf/RSI/distance-insights-2021-docs/Notice%20%20-Spring%20Effect%20Interpretation%201-11-16%20Final.pdf", verified="search_snippet", terms="USGA PDF; numbers cited only"),
 "trackman_tour_avg_pdf": dict(title="TrackMan PGA Tour averages (2023 data, PDF)", url="https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf", verified="fetched_pdf", terms="TrackMan published reference table; cite, do not redistribute the PDF"),
 "trackman_tour_avg_blog": dict(title="TrackMan 'Introducing updated Tour Averages' (method notes: competition + range data, 200+ players)", url="https://www.trackman.com/blog/introducing-updated-tour-averages", verified="fetched", terms="TrackMan web content"),
 "trackman_smash": dict(title="TrackMan 'What is Smash Factor' (tour driver 1.49; ~1.50 hoped for)", url="https://www.trackman.com/blog/smash-factor", verified="fetched", terms="TrackMan web content"),
 "foresight_tables": dict(title="Foresight Sports Ball Launch Data: Performance Reference Tables (optimized driver launch vs club/ball speed)", url="https://help.foresightsports.com/hc/en-us/articles/47208228295187-Ball-Launch-Data-Performance-Reference-Tables", verified="fetched", terms="Foresight help-center content; numbers cited only. Vendor reference table, not peer reviewed"),
 "pgatour_bryson_2024": dict(title="PGA Tour betting profile (ShotLink-derived, machine-generated): DeChambeau avg driving distance 320.9 yd (start of 2024 PGA Championship)", url="https://www.pgatour.com/article/news/betting-profile/2024/pga-championship/bryson-dechambeau-pga-tour-betting-stats-pga-championship-2024", verified="fetched", terms="PGA Tour content; numbers cited only"),
 "golfcom_persimmon": dict(title="GOLF.com 'How far would Bryson DeChambeau hit a persimmon' (secondary: tour avg ball speed 173.64 mph; Bryson 2024 avg ball speed ~172.2 mph derived; 338 yd avg at 2024 US Open)", url="https://golf.com/gear/how-far-bryson-dechambeau-hit-persimmon-open/", verified="fetched", terms="Media article; secondary source, numbers cited only"),
 "thescore_2020": dict(title="theScore 'Win at Winged Foot...' (2020: ~140 mph club, ~190 mph ball, 322.1 yd; tour avg 114.01 mph / 169.71 mph 2019-20)", url="https://www.thescore.com/pga/news/2025658", verified="search_snippet", terms="Media article; low confidence, conflicts with Arccos 'approaching 150 mph'"),
 "arccos_2020": dict(title="Arccos blog on DeChambeau at Winged Foot ('approaching 150 mph club, over 190 mph ball')", url="https://www.arccosgolf.com/blogs/community/the-mathacre-at-winged-foot-dechambeau-strokes-gained-stats", verified="search_snippet", terms="Vendor blog; low confidence"),
 "sportsbox_bryson": dict(title="Sportsbox AI case study (Cheetham): DeChambeau 128 mph avg club speed (video-AI estimate, NOT radar); tour group avg 117 mph", url="https://help.sportsbox.ai/dechambeaus-swing", verified="fetched", terms="Vendor web content; numbers cited only. Measurement is video-based, not TrackMan"),
 "sportsbox_report_pdf": dict(title="Sportsbox 'Swing Score Report' Bryson 14 Jul 2024 (pelvis 506, chest 961, arm 1292, shaft 2495 deg/s; tour ranges)", url="https://moccasin-micheline-88.tiiny.site/Bryson-Driver-Swing-Score-Report-1.pdf", verified="fetched_pdf", terms="Third-party-hosted copy of a vendor PDF; provenance weak -> low confidence; cite numbers only"),
 "cheetham_2008": dict(title="Cheetham, Rose, Neal et al. 'Comparison of Kinematic Sequence Parameters between Amateur and Professional Golfers' (pros: pelvis 477, thorax 727, arm 980, club 2254 deg/s; driver)", url="https://www.academia.edu/5572510/Comparison_of_Kinematic_Sequence_Parameters_between_Amateur_and_Professional_Golfers", verified="search_snippet", terms="Academic paper (Science and Golf V proceedings); numbers cited only"),
 "tinmark_2010": dict(title="Tinmark et al. 2010 Sports Biomech 9(4):236-244, Elite golfers' kinematic sequence", url="https://pubmed.ncbi.nlm.nih.gov/21309298/", doi="10.1080/14763141.2010.535842", verified="search_snippet", terms="PubMed abstract; qualitative (proximal-to-distal sequence)"),
 "bourgain_2019": dict(title="Bourgain et al. 2019 Acta Bioeng Biomech 'methodological effect of angular velocity component on kinematic sequence' (pelvis 480+-82, thorax 605+-87, lead arm 1310+-236, hand 1650+-211 deg/s; club speed 36-52 m/s)", url="https://doi.org/10.5277/abb-01318-2019-02", doi="10.5277/abb-01318-2019-02", verified="search_snippet", terms="Open-access article; numbers cited only"),
 "edwards_2022_lbp": dict(title="Edwards, Dickin, Wang 'Low back pain and golf: a review of biomechanical risk factors' (L4-L5 compression 6.5-8+ BW after impact; PDS pelvis 488 -> hand 945 deg/s)", url="https://pmc.ncbi.nlm.nih.gov/articles/PMC9219256/", verified="fetched", terms="PMC open access (check license on page); numbers cited only"),
 "hume_2005": dict(title="Hume, Keogh, Reid 2005 Sports Med 35(5):429-449 (peak vertical/AP/ML GRF 1.6-2.0/0.4-0.6/0.2-0.3 BW)", url="https://waddengolfacademy.com/biomechanics/Hume%20Keogh%20Role%20of%20golf_biomechanics.pdf", doi="10.2165/00007256-200535050-00005", verified="search_snippet", terms="Journal article; numbers cited only (PDF fetch blocked)"),
 "han_2019_ground": dict(title="Han, Kwon et al. 2019 Sports Biomech 'Effects of the golfer-ground interaction on clubhead speed in skilled male golfers' (n=63, hcp<=3; lead-foot GRF moment and trail-foot pivoting moment correlate with clubhead speed)", url="https://doi.org/10.1080/14763141.2019.1586983", doi="10.1080/14763141.2019.1586983", verified="search_snippet", terms="Abstract only; N*m magnitudes NOT retrieved -> unverified"),
 "nesbit_2005": dict(title="Nesbit & Serrano 2005 J Sports Sci Med 4(4):520-533 'Work and Power Analysis of the Golf Swing'", url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3899668/", verified="fetched", terms="Open access (JSSM); numbers cited only. n=4 amateurs, single swing each"),
 "sell_lbp_speed": dict(title="Is average club head speed a risk factor for lower back injuries in professional golfers? Retrospective case-control (Phys Sportsmed 2020)", url="https://www.tandfonline.com/doi/full/10.1080/00913847.2020.1809968", doi="10.1080/00913847.2020.1809968", verified="search_snippet", terms="Abstract-level only; association not causation"),
 "par4_overspeed": dict(title="Par4Success low-volume overspeed protocol research (randomized 6/8-week; no injury outcomes reported)", url="https://par4success.com/wp-content/uploads/2019/09/Overspeed-Training-Low-Volume-Protocol-Research-1.pdf", verified="search_snippet", terms="Vendor-affiliated research; low confidence"),
 "repo_ball_flight": dict(title="This repo env/ball_flight_analytic.py (drag+Magnus+bounce/roll; calibrated to TrackMan tour avg; our check: 167 mph/10.9 deg/2686 rpm -> 268 yd carry vs TrackMan 251 m = 275 yd)", url="repo:env/ball_flight_analytic.py", verified="run_locally", terms="Project code"),
 "repo_xml_v3": dict(title="This repo env/models/humanoid_golf_v3.xml actuator/joint definitions", url="repo:env/models/humanoid_golf_v3.xml", verified="read_locally", terms="Project code"),
}

# cached results of env.ball_flight_analytic.simulate (dt=0.002), center-face, no wind, fairway roll. (club_mph, ball_mph@smash1.48, [(launch,rpm,carry_yd,total_yd)])
FLIGHT = {
 113: (167.2, [(11, 2500, 270, 297), (12, 2300, 273, 301), (13, 2100, 276, 304), (14, 2000, 279, 307)]),
 120: (177.6, [(11, 2500, 291, 318), (12, 2300, 294, 321), (13, 2100, 297, 325), (14, 2000, 299, 327)]),
 130: (192.4, [(11, 2500, 317, 344), (12, 2300, 321, 348), (13, 2100, 324, 351), (14, 2000, 325, 353)]),
 140: (207.2, [(11, 2500, 342, 369), (12, 2300, 345, 372), (13, 2100, 348, 376), (14, 2000, 349, 377)]),
 150: (222.0, [(11, 2500, 364, 391), (12, 2300, 367, 395), (13, 2100, 370, 398), (14, 2000, 371, 399)]),
}

def metric(unit, mn, tg, mx, src, conf, unverified=False, note="", derived=False):
    return dict(unit=unit, min=mn, target=tg, max=mx, source_ids=src, confidence=conf, unverified=unverified, derived=derived, note=note)

def metrics():
    M = {}
    M["club_head_speed_mph"] = metric("mph", 125, 130, 140, ["foresight_tables", "sportsbox_bryson", "repo_ball_flight"], "medium",
        note="350 yd-class total in the repo flight model needs ~130 mph (smash 1.48, ~13 deg, ~2100 rpm -> 351 yd); Bryson video-AI avg 128 mph (not radar); tour avg 113 (TrackMan).", derived=True)
    M["ball_speed_mph"] = metric("mph", 185, 192, 207, ["trackman_tour_avg_pdf", "foresight_tables", "repo_ball_flight"], "medium",
        note="Foresight: 190 mph ball -> 342-372 yd carry, 378-401 total (optimistic vendor table); repo model: 192 mph -> ~351 total.", derived=True)
    M["smash_factor"] = metric("ratio", 1.46, 1.48, 1.50, ["trackman_tour_avg_pdf", "trackman_smash"], "high",
        note="Tour avg 1.48 (PDF) / 1.49 (blog). Physics cap for center hit: (1+e)/(1+m_ball/m_head) = 1.83/1.23 = 1.49 with e=0.83, 200 g head; CT limit bounds e. The cap is why speed, not smash, must scale.", derived=True)
    M["launch_angle_deg"] = metric("deg", 10.0, 12.5, 14.5, ["foresight_tables", "trackman_tour_avg_pdf"], "medium", note="Foresight optimum 10-14 deg at 190 mph ball speed; tour avg 10.9 deg at 167 mph.")
    M["spin_rate_rpm"] = metric("rpm", 1600, 2200, 2600, ["foresight_tables", "trackman_tour_avg_pdf"], "medium", note="Foresight optimum 1600-2600 rpm at 190 mph ball speed; tour avg 2686 (PDF) / 2545 (blog).")
    M["carry_yd"] = metric("yd", 320, 335, 372, ["foresight_tables", "repo_ball_flight"], "low", derived=True, note="Repo model carry 321-325 yd at 130 mph; Foresight 342-372 (vendor, optimistic). Wind/altitude/turf not modeled.")
    M["total_distance_yd"] = metric("yd", 345, 350, 400, ["foresight_tables", "repo_ball_flight"], "low", derived=True, note="Repo model: 348-353 at 130 mph club; 391-399 at 150. ODS test (317 yd) assumes only 120 mph/10 deg/2520 rpm.")
    M["attack_angle_deg"] = metric("deg", 0, 3, 6, [], "low", unverified=True, note="Positive attack angle is standard long-drive advice; no verified published tour-driver value fetched (TrackMan tour avg is -1.3 deg).")
    M["pelvis_peak_speed_dps"] = metric("deg/s", 440, 500, 590, ["cheetham_2008", "sportsbox_report_pdf", "bourgain_2019"], "medium", note="Pros 477 (Cheetham); Bryson 506 (Sportsbox, 51st pct of tour); tour range 440-543 (Sportsbox); max 590 in Bourgain sample.")
    M["thorax_peak_speed_dps"] = metric("deg/s", 750, 950, 1000, ["cheetham_2008", "sportsbox_report_pdf", "bourgain_2019"], "medium", note="Pros 727 (Cheetham); Bryson 961 (Sportsbox, 95th pct; tour range 754-857).")
    M["lead_arm_peak_speed_dps"] = metric("deg/s", 1050, 1290, 1400, ["cheetham_2008", "sportsbox_report_pdf", "bourgain_2019"], "medium", note="Pros 980 (Cheetham); Bryson 1292 (Sportsbox); tour range 1046-1231; Bourgain 1310+-236.")
    M["club_shaft_peak_speed_dps"] = metric("deg/s", 2250, 2500, 2700, ["cheetham_2008", "sportsbox_report_pdf"], "medium", note="Pros 2254 at 109 mph head speed (Cheetham); Bryson shaft 2495 (Sportsbox); tour range 2054-2356. Upper bound is extrapolation.")
    M["hand_peak_speed_dps"] = metric("deg/s", 945, 1650, 2100, ["edwards_2022_lbp", "bourgain_2019"], "low", note="Hand 945 (Neal 2007 as cited by Edwards 2022) vs 1650+-211 (Bourgain, range 1300-2100): different definitions (linear vs resultant).")
    M["wrist_hinge_uncock_peak_speed_dps"] = metric("deg/s", None, None, None, [], "none", unverified=True, note="No verified isolated wrist-uncock rate fetched. Proxy: arm->club speed gain 1274 deg/s (Cheetham pros, 109 mph) scaled by v: ~1520 deg/s at 130 mph (derived, low).")
    M["seq_peak_time_before_impact_ms"] = dict(unit="ms", pelvis=dict(mean=87, sd=19), thorax=dict(mean=68, sd=14), arm=dict(mean=65, sd=8), source_ids=["cheetham_2008"], confidence="medium", unverified=False, derived=False,
        note="Pros, driver. Lags: pelvis->thorax 19 ms, thorax->arm 3 ms (timing differences between pros and amateurs not significant; amateurs' SDs >=2x). Speed gains pelvis->thorax 250, thorax->arm 253, arm->club 1274 deg/s.")
    M["peak_vertical_grf_bw"] = metric("bodyweights", 1.6, 1.8, 2.0, ["hume_2005"], "medium", note="Driver/5-iron vertical peak 1.6-2.0 BW; AP 0.4-0.6; ML 0.2-0.3 (Hume 2005, from search snippet of the PDF). Likely lower than a 130+ mph swing's needs: extrapolation unverified.")
    M["ground_reaction_torque_nm"] = metric("N*m", None, None, None, [], "none", unverified=True, note="Han 2019 shows lead-foot GRF moment (F/B axis) and trail-foot pivoting moment (vertical axis) correlate with clubhead speed, but N*m magnitudes were not retrieved.")
    M["club_length_in"] = metric("in", 44.0, 45.5, 48.0, ["usga_equip_part2", "usga_equip_faq"], "high", note="48 in. hard limit (verified, fetched). Tour/long-drive typical lengths NOT verified. Optional Local Rule G-10 caps at 46 in. Longer than 48 only with documented need and Local Committee approval (R&A).")
    M["driver_head_mass_g"] = metric("g", None, 200, None, [], "low", unverified=True, note="~200 g is the repo assumption (also model XML); no rule limit on head mass; published driver mass not verified here.")
    M["characteristic_time_us"] = metric("us", None, 239, 257, ["usga_ct_notice"], "medium", note="CT limit 239 us + 18 us test tolerance (search snippet of USGA notice).")
    M["head_volume_cc"] = metric("cc", None, None, 460, [], "low", unverified=True, note="460 cc max is widely stated; only a retail guide surfaced in search - USGA page not fetched.")
    return M

def ladder():
    stages = []
    for cs, (bs, rows) in sorted(FLIGHT.items()):
        best = max(rows, key=lambda r: r[3])
        stages.append(dict(stage=f"{cs}mph", club_head_speed_mph=cs, ball_speed_mph=bs, smash_assumed=1.48,
            best_launch_deg=best[0], best_spin_rpm=best[1], sim_carry_yd=best[2], sim_total_yd=best[3],
            torque_scale_vs_113=round((cs / 113) ** 2, 2), speed_scale_vs_113=round(cs / 113, 2), power_scale_vs_113=round((cs / 113) ** 3, 2),
            source_ids=["repo_ball_flight"], confidence="low",
            note={113: "TrackMan tour average (reference).", 120: "Mason's stated club speed (self-reported, unverified): ~320-327 yd total in model; consistent with his 300+ yd claim.",
                  130: "~350 yd total in model: the '350-class' threshold; ~Bryson avg club speed per Sportsbox video-AI.",
                  140: "~370-377 yd in model; beyond any verified tour average (extrapolation).", 150: "~391-399 yd in model; at/above Bryson's claimed peak (Arccos); unverified, injury-risk regime."}[cs]))
    return stages

def parse_actuators():
    root = ET.parse(XML).getroot()
    d = root.find("default/joint"); dflt = dict(damping=float(d.get("damping")), armature=float(d.get("armature")))
    joints = {}
    for j in root.iter("joint"):
        n = j.get("name")
        if n: joints[n] = dict(damping=float(j.get("damping", dflt["damping"])), armature=float(j.get("armature", dflt["armature"])), range=[float(x) for x in j.get("range", "0 0").split()])
    out = {}
    for m in root.find("actuator"):
        jn = m.get("joint"); gear = float(m.get("gear")); fr = float(m.get("forcerange").split()[1])
        tau = gear * fr; b = joints[jn]["damping"]
        out[jn] = dict(gear=gear, forcerange=fr, peak_torque_nm=round(tau, 1), joint_damping_nm_s_rad=b, armature=joints[jn]["armature"], range_deg=joints[jn]["range"],
                       no_load_speed_rad_s=round(tau / b, 1), no_load_speed_dps=round(tau / b / DEG), peak_power_w=round(tau ** 2 / (4 * b)), speed_at_peak_power_rad_s=round(tau / (2 * b), 1))
    return out

def club_inertia():
    root = ET.parse(XML).getroot()
    sh = [g for g in root.iter("geom") if g.get("name") == "club_shaft"][0]; hd = [g for g in root.iter("geom") if g.get("name") == "club_head"][0]
    L = abs(float(sh.get("fromto").split()[-1])); ms, mh = float(sh.get("mass")), float(hd.get("mass")); rh = abs(float(hd.get("pos").split()[-1]))
    return dict(shaft_len_m=L, head_dist_m=rh, shaft_mass_kg=ms, head_mass_kg=mh, inertia_about_wrist_kg_m2=round(mh * rh ** 2 + ms * L ** 2 / 3, 3), total_club_mass_kg=ms + mh)

def humanoid(act, ci):
    R = {}
    I = ci["inertia_about_wrist_kg_m2"]; mh = ci["head_mass_kg"]
    arm_to_club_113 = 1274.0  # deg/s, Cheetham pros at 109 mph head speed (arm->club speed gain)
    rows = []
    for cs in (113, 120, 130, 140, 150):
        v = cs * MPH
        wrist_w = arm_to_club_113 * (cs / 109) * DEG   # rad/s, scaled by head speed
        w = act["right_wrist"]; b = w["joint_damping_nm_s_rad"]; tau = w["peak_torque_nm"]
        net = tau - b * wrist_w
        rows.append(dict(club_head_speed_mph=cs, head_ke_j=round(0.5 * mh * v * v, 1), wrist_uncock_rate_rad_s=round(wrist_w, 1),
                         wrist_net_torque_at_speed_nm=round(net, 1), wrist_net_torque_frac=round(net / tau, 2),
                         wrist_torque_needed_for_50pct_margin_nm=round(2 * b * wrist_w, 1),
                         wrist_max_damping_for_50pct_margin=round(0.5 * tau / wrist_w, 2),
                         nesbit_scaled_peak_club_power_w=round(3875 * (v / 52.0) ** 3), nesbit_scaled_peak_angular_power_w=round(1150 * (v / 52.0) ** 3),
                         nesbit_scaled_total_body_work_j=round(1452 * (v / 52.0) ** 2), nesbit_scaled_club_ke_j=round(334 * (v / 52.0) ** 2)))
    R["ladder_requirements"] = rows
    R["assumptions"] = ["Wrist uncock rate = Cheetham arm->club gain (1274 deg/s at 109 mph) scaled linearly with head speed (derived, low confidence).",
        "Nesbit & Serrano (n=4, one swing each, scratch golfer 52.0 m/s = 116 mph): peak club power 3875 W, angular power 1150 W, total body work 1452 J, club KE 334 J; scaled by v^3 (power) and v^2 (work/energy) - extrapolation.",
        "Motor model: MuJoCo <motor> is torque-only (no speed-torque curve); joint damping is a passive loss, so net torque at rate w is tau_max - b*w; no-load speed tau_max/b; max mechanical power tau_max^2/(4b).",
        "XML defines no joint velocity limit; 'joint speed' limits here are damping-implied only."]
    R["findings"] = [
        "right_wrist: tau_max 60 N*m but damping 2.0 N*m*s/rad gives no-load speed 30 rad/s (1719 deg/s) and max power 450 W; at the ~130 mph wrist rate (~26.5 rad/s) only ~12% of torque remains. Needs damping <=~1.1 (50% margin) or tau >=~106 N*m, or both.",
        "right_wrist max power 450 W vs Nesbit-scaled angular power ~1.6 kW at 130 mph: ~3.6x short on wrist power alone.",
        "chest_yaw: range +-45 deg (90 deg total) vs real shoulder turn ~94-112 deg back + follow-through (Sportsbox tour range 94-106, Bryson 112); only yaw DOF (no pelvis yaw, so no pelvis/thorax separation or X-factor 59-68 deg). 120 N*m / 3.6 kW is adequate for thorax speed 950 deg/s (16.6 rad/s, drag 17 N*m).",
        "Hip actuators are pitch (sagittal) only: they cannot produce the pelvis rotation (440-590 deg/s) that carries the sequence; ground-reaction torque about the vertical axis is not controllable.",
        "Model club: head 0.20 kg, shaft 0.10 kg, 1.12 m -> inertia about wrist %.3f kg*m^2; real club length limit 48 in = 1.219 m (model 1.12 m ~ 44 in. to head centre)." % I]
    return R

def build():
    act = parse_actuators(); ci = club_inertia()
    return dict(schema_version=1, name="power_profile_350yd_targets", generated_by="scripts/gen_power_profile_350yd.py", generated_for="Mason (left-handed target profile) / Trainer reward shaping",
        units="SI-adjacent: see per-field unit; speeds deg/s, forces in bodyweights, distances yards (flight) or inches (equipment)",
        notes=["Bands: min/target/max are plausibility bands for a 350 yd-class long driver, NOT measured data on Mason.",
               "unverified=true -> no verified published number was retrieved; value fields are null or a stated assumption. Do not use as reward targets without confirming.",
               "confidence: high = fetched primary/standards page; medium = fetched or consistent multi-source; low = single secondary/vendor/derived; none = nothing retrieved.",
               "Bryson numbers come from vendor video-AI (Sportsbox), media and PGA Tour averages - not radar-verified for 128 mph; treat as indicative.",
               "Handedness: all literature values are handedness-agnostic magnitudes; mirror (not re-derive) for a left-handed humanoid."],
        sources=SOURCES, metrics=metrics(), ladder=ladder(),
        mason_gap=dict(mason_club_speed_mph_self_reported=120, mason_total_yd_self_reported=300, handedness="left", verified=False,
                       gap_to_350_class_club_speed_mph=10, note="Self-reported (+3 hcp, 120+ mph, 300+ yd), not independently measured; repo video data cannot measure club speed. A launch monitor session is the first step."),
        humanoid_actuator_audit=dict(model="env/models/humanoid_golf_v3.xml", source_ids=["repo_xml_v3"], actuators=act, club=ci, **humanoid(act, ci)),
        caveats=["Single-view ~30 fps video cannot verify any of these; the profile is a literature-based prior only.",
                 "Repo flight model: center-face, no wind, simplified roll; it under-predicts TrackMan tour-avg carry by ~2.5% (268 vs 275 yd).",
                 "Overspeed/injury: L4-L5 compression 6.5-8+ BW after impact (Edwards 2022); higher club speed associated with back injury in a small PGA case-control (association only); no injury-outcome trials of overspeed protocols were found.",
                 "Rule status: 48 in. max length; 460 cc, CT 239 us and ODS tests bound equipment; USGA 2028 ball test (125 mph/11 deg/2220 rpm) will trim ~13-15 yd for the longest hitters (USGA FAQ)."])

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(ROOT, "data", "references", "power_profile_350yd_targets.json")); a = ap.parse_args()
    with open(a.out, "w") as f:
        json.dump(build(), f, indent=1, sort_keys=False); f.write("\n")
    print("wrote", a.out)
