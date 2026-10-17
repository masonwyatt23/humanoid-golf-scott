#!/usr/bin/env python3
"""Generate data/references/humanoid_actuator_specs.json (cited, unverified-flagged).
Every record: value (null if not published), unit, source_id, source_type, confidence, unverified, note.
URDF values were parsed on 2026-10-17 from raw files in github.com/unitreerobotics/unitree_ros (master)."""
import json, os, math
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "references", "humanoid_actuator_specs.json")

S = {}
def src(i, title, url, stype, note=""):
    S[i] = {"title": title, "url": url, "source_type": stype, "note": note, "accessed": "2026-10-17"}

U = "https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/"
src("uni_g1_page", "Unitree G1 product page", "https://www.unitree.com/g1/", "official_spec_sheet")
src("uni_g1_manual", "Unitree G1 user manual (hosted by MYBOTSHOP, reseller copy)", "https://www.docs.mybotshop.de/downloads/G1_User_Manual.pdf", "official_manual_reseller_copy")
src("uni_g1_brochure", "Unitree G1 brochure (Chinese, hosted wrc.cie.org.cn)", "https://wrc.cie.org.cn/profile/robot/download/2025/07/08/%E6%9D%AD%E5%B7%9E%E5%AE%87%E6%A0%91-G1%E5%AE%A3%E4%BC%A0%E5%86%8C_20250708194541A200.pdf", "official_spec_sheet", "Lists standing height 1320 mm; manual/page list 1270 mm. Conflict.")
src("uni_g1_urdf29", "unitree_ros g1_29dof.urdf (effort/velocity/limits)", U+"g1_description/g1_29dof.urdf", "official_model_file", "Parsed <limit effort velocity>. These are model/control limits, not necessarily motor peak or continuous ratings.")
src("uni_g1_urdf23", "unitree_ros g1_23dof.urdf", U+"g1_description/g1_23dof.urdf", "official_model_file")
src("uni_h1_page", "Unitree H1 / H1-2 product page", "https://www.unitree.com/h1/", "official_spec_sheet")
src("uni_h1_brochure", "Unitree H1 / H1-2 brochure (hosted generation-robots.com)", "https://static.generation-robots.com/media/brochure-robot-humanoide-unitree-h1.pdf", "official_spec_sheet_reseller_copy")
src("uni_h12_docs", "Unitree support: About H1-2", "https://support.unitree.com/home/en/H1_developer/About_H1-2", "official_spec_sheet")
src("uni_h1_urdf", "unitree_ros h1.urdf", U+"h1_description/urdf/h1.urdf", "official_model_file")
src("uni_h12_urdf", "unitree_ros h1_2.urdf", U+"h1_2_description/h1_2.urdf", "official_model_file")
src("bd_atlas_sheet", "Boston Dynamics Atlas spec sheet (12/23/2025)", "https://www-bostondynamics.com/wp-content/uploads/2026/01/atlas-spec-sheet.pdf", "official_spec_sheet")
src("bd_atlas_page", "Boston Dynamics Atlas product page", "https://bostondynamics.com/products/atlas/", "official_spec_sheet")
src("bd_ces_pr", "Boston Dynamics CES 2026 press release", "https://bostondynamics.com/blog/boston-dynamics-unveils-new-atlas-robot-to-revolutionize-industry/", "official_press")
src("ieee_playter", "IEEE Spectrum: Playter on the new Atlas (Apr 2024)", "https://spectrum.ieee.org/atlas-humanoid-robot-ceo-interview", "media_interview", "Qualitative only: 'stronger at most joints than a person'. No numbers.")
src("fig02_pr", "Figure 02 press release (PR Newswire, 2024-08-06)", "https://www.prnewswire.com/news-releases/figure-unveils-figure-02-its-second-generation-humanoid-setting-new-standards-in-ai-and-robotics-302214889.html", "official_press")
src("fig03_news", "Figure: Introducing Figure 03 (2025-10-09)", "https://www.figure.ai/news/introducing-figure-03", "official_press")
src("ieee_fig02", "IEEE Spectrum: Figure 02", "https://spectrum.ieee.org/figure-new-humanoid-robot", "media", "Quotes Figure: 2.25 kWh, 5 h run-time target.")
src("fig02_agg", "RoboHuman.org Figure 02 directory", "https://robohuman.org/product/figure-02", "third_party_aggregator", "Height 168 cm, 70 kg, payload 20 kg; 'actuators: details awaiting confirmation'.")
src("fig_order_page", "pay.ai-figure.one 'Order Figure 02/03' page", "https://pay.ai-figure.one/", "third_party_unofficial", "Domain is NOT figure.ai; treat as untrusted. Used only to flag conflicting payload (40 kg) and F03 63 kg claims.")
src("tesla_aiday_summary", "Easy Build Technology summary of Tesla AI Day 2022", "https://easybuildtech.com/optimus-teslabot-tesla-ai-day-2022/", "media_summary", "Confirms 28 actuators, 2.3 kWh, six-actuator portfolio (3 rotary + 3 linear). Torque classes (20/110/180 N*m; 500/3900/8000 N) came from a WebSearch synthesis of AI Day 2022 coverage, not fetched from a primary page.")
src("tesla_aiday_yt", "Tesla AI Day 2022 (video, primary)", "https://www.youtube.com/watch?v=ODSJsviD_SU", "official_video", "Not transcribed by this agent; torque classes unverified against video.")
src("forbes_2022", "Forbes: Tesla Bot Optimus everything we know (2022-10-01)", "https://www.forbes.com/sites/johnkoetsier/2022/10/01/tesla-bot-optimus-everything-we-know-so-far/", "media", "2022 AI Day figures, pre-Gen 2.")
src("newatlas_gen2", "New Atlas: Optimus Gen 2 (Dec 2023)", "https://newatlas.com/robotics/tesla-optimus-gen-2-robot/", "media", "Gen 2: 10 kg lighter, 30% faster walking, 11-DoF hands, 2-DoF neck (relative claims only).")
src("robozaps_g2", "RoboZaps: Optimus Gen 2 review (claim-vs-source audit)", "https://blog.robozaps.com/b/tesla-optimus-gen-2-review", "media_blog", "Explicitly notes 28 actuators/2.3 kWh/73 kg are pre-Gen 2 figures.")
src("teslarati_v3", "Teslarati: Optimus V3 hand/arm patents", "https://www.teslarati.com/tesla-optimus-v3-hand-arm-details-revealed-new-patents/", "media_patents", "Patent-based, 25 actuators per forearm/hand, 22-DoF hand; not confirmed shipping design.")
src("req350", "Repo: docs/research_350yd_profile.md + data/references/power_profile_350yd_targets.json", "repo:docs/research_350yd_profile.md", "repo", "Model needs; derived (D) values there are extrapolations.")

def r(field, value, unit, sid, stype, conf, unver, note="", variant=None):
    d = {"field": field, "value": value, "unit": unit, "source_id": sid, "source_type": stype,
         "confidence": conf, "unverified": unver, "note": note}
    if variant: d["variant"] = variant
    return d
OFF, FILE, MEDIA, AGG, NONE = "official_spec_sheet", "official_model_file", "media", "third_party_aggregator", "none_published"

def unitree_joint(sid, plat, name, eff, vel, lo, hi, note=""):
    return {"joint": name, "peak_torque_nm": eff, "max_speed_rad_s": vel, "max_speed_deg_s": round(vel*180/math.pi),
            "range_deg": [round(lo*180/math.pi,1), round(hi*180/math.pi,1)], "source_id": sid, "source_type": FILE,
            "confidence": "medium", "unverified": False,
            "note": "URDF <limit> value (model/control limit; not a continuous rating; speed is not at-load). " + note}

platforms = {}
# ---------------- Unitree G1
g1 = [
 unitree_joint("uni_g1_urdf29","g1","waist_yaw",88,32,-2.618,2.618,"Our pelvis/thorax-yaw analogue."),
 unitree_joint("uni_g1_urdf29","g1","waist_roll",35,30,-0.52,0.52,"Only on 29-DoF variant."),
 unitree_joint("uni_g1_urdf29","g1","waist_pitch",35,30,-0.52,0.52,"Only on 29-DoF variant."),
 unitree_joint("uni_g1_urdf29","g1","hip_pitch",88,32,-2.5307,2.8798),
 unitree_joint("uni_g1_urdf29","g1","hip_roll",88,32,-0.5236,2.9671),
 unitree_joint("uni_g1_urdf29","g1","hip_yaw",88,32,-2.7576,2.7576),
 unitree_joint("uni_g1_urdf29","g1","knee",139,20,-0.087267,2.8798,"Product page says 90 N*m (G1) / 120 N*m (EDU) max knee torque; URDF says 139. Conflict, spec-sheet number preferred for hardware claims."),
 unitree_joint("uni_g1_urdf29","g1","ankle_pitch",35,30,-0.87267,0.5236),
 unitree_joint("uni_g1_urdf29","g1","ankle_roll",35,30,-0.2618,0.2618),
 unitree_joint("uni_g1_urdf29","g1","shoulder_pitch/roll/yaw",25,37,-3.0892,2.6704,"Same limits all three shoulder axes; pitch range shown."),
 unitree_joint("uni_g1_urdf29","g1","elbow",25,37,-1.0472,2.0944),
 unitree_joint("uni_g1_urdf29","g1","wrist_roll (forearm roll)",25,37,-1.972222054,1.972222054,"Closest to forearm pronation/supination."),
 unitree_joint("uni_g1_urdf29","g1","wrist_pitch",5,22,-1.614429558,1.614429558,"Only on 29-DoF/EDU wrist option. 5 N*m."),
 unitree_joint("uni_g1_urdf29","g1","wrist_yaw",5,22,-1.614429558,1.614429558,"Only on 29-DoF/EDU wrist option. 5 N*m."),
]
platforms["unitree_g1"] = {
 "name": "Unitree G1 (std / EDU)", "maker": "Unitree", "status": "shipping (public price/spec)",
 "general": [
  r("height",1.27,"m","uni_g1_page",OFF,"high",False,"Standing 1270 mm per manual; brochure says 1320 mm (conflict)."),
  r("mass",35,"kg","uni_g1_page",OFF,"high",False,"'About 35 kg' with battery; EDU '35 kg+'."),
  r("dof_total",23,"count","uni_g1_page",OFF,"high",False,"Std 23; EDU 23-43. URDFs exist for 23 and 29 DoF."),
  r("dof_per_arm",5,"count","uni_g1_manual",OFF,"high",False,"Optional +2 wrist DOF (pitch, yaw) on EDU/Dex3-1 option; each Dex3-1 hand 7 DoF."),
  r("dof_per_leg",6,"count","uni_g1_manual",OFF,"high",False),
  r("dof_waist",1,"count","uni_g1_manual",OFF,"high",False,"Optional +2 (roll, pitch) on EDU."),
  r("max_knee_torque_std",90,"N*m","uni_g1_page",OFF,"high",False),
  r("max_knee_torque_edu",120,"N*m","uni_g1_page",OFF,"high",False,"Brochure headline 'max joint torque 120 N*m'. Vendor peak, not continuous."),
  r("arm_max_load",2,"kg","uni_g1_page",OFF,"high",False,"EDU about 3 kg."),
  r("continuous_torque",None,"N*m","uni_g1_page",NONE,"none",True,"No continuous/rated torque published by Unitree for G1."),
  r("gear_ratio",None,"ratio","uni_g1_page",NONE,"none",True,"Not published (quasi-direct-drive/planetary per third-party robotdata.dev, unfetched)."),
  r("battery",None,"kWh","uni_g1_page",NONE,"none",True,"Quick-release battery; 9 Ah/13-cell stated by some retailers, not retrieved here."),
  r("wrist_torque_urdf",25,"N*m","uni_g1_urdf29",FILE,"medium",False,"Roll only; pitch/yaw are 5 N*m."),
 ],
 "joints": g1,
}
# ---------------- Unitree H1
h1 = [
 unitree_joint("uni_h1_urdf","h1","torso (waist yaw)",200,23,-2.35,2.35,"Single torso yaw; our pelvis/thorax-yaw analogue."),
 unitree_joint("uni_h1_urdf","h1","hip_yaw",200,23,-0.43,0.43,"Only +-24.6 deg."),
 unitree_joint("uni_h1_urdf","h1","hip_roll",200,23,-0.43,0.43),
 unitree_joint("uni_h1_urdf","h1","hip_pitch",200,23,-3.14,2.53),
 unitree_joint("uni_h1_urdf","h1","knee",300,14,-0.26,2.05,"Spec sheet says ~360 N*m (M107); URDF 300."),
 unitree_joint("uni_h1_urdf","h1","ankle",40,9,-0.87,0.52,"Spec sheet 59 N*m."),
 unitree_joint("uni_h1_urdf","h1","shoulder_pitch/roll",40,9,-2.87,2.87,"Spec sheet 75 N*m arm joint."),
 unitree_joint("uni_h1_urdf","h1","shoulder_yaw",18,20,-1.3,4.45),
 unitree_joint("uni_h1_urdf","h1","elbow",18,20,-1.25,2.61),
]
platforms["unitree_h1"] = {
 "name": "Unitree H1", "maker": "Unitree", "status": "shipping",
 "general": [
  r("height",1.80,"m","uni_h1_page",OFF,"high",False),
  r("mass",47,"kg","uni_h1_page",OFF,"high",False),
  r("dof_total",19,"count","uni_h1_brochure",OFF,"high",False,"Per H1 user manual: 19 joint motors; no wrist DOF in base arm (4-DoF arm, expandable)."),
  r("max_joint_torque",360,"N*m","uni_h1_page",OFF,"high",False,"M107 motor peak; ~10 kN at 3.5 cm arm. Vendor peak."),
  r("peak_torque_density",189,"N*m/kg","uni_h1_page",OFF,"high",False,"M107 1.9 kg, 360 N*m."),
  r("hip_torque",220,"N*m","uni_h1_page",OFF,"high",False),
  r("ankle_torque",59,"N*m","uni_h1_page",OFF,"high",False),
  r("arm_joint_torque",75,"N*m","uni_h1_page",OFF,"high",False),
  r("wrist_torque",None,"N*m","uni_h1_page",NONE,"none",True,"Base H1 has no wrist joint."),
  r("continuous_torque",None,"N*m","uni_h1_page",NONE,"none",True,"Not published."),
  r("gear_ratio",None,"ratio","uni_h1_page",NONE,"none",True,"Not published."),
  r("battery",None,"kWh","uni_h1_page",NONE,"none",True,"Not retrieved for H1 (H1-2 is 0.864 kWh)."),
 ],
 "joints": h1,
}
h12 = [
 unitree_joint("uni_h12_urdf","h1_2","torso (waist yaw)",200,23,-2.35,2.35,"Spec page: waist ~220 N*m."),
 unitree_joint("uni_h12_urdf","h1_2","hip_yaw",200,23,-0.43,0.43,"Only +-24.6 deg."),
 unitree_joint("uni_h12_urdf","h1_2","hip_pitch",200,23,-3.14,2.5),
 unitree_joint("uni_h12_urdf","h1_2","hip_roll",200,23,-0.43,3.14),
 unitree_joint("uni_h12_urdf","h1_2","knee",300,14,-0.12,2.19,"Spec page ~360 N*m."),
 unitree_joint("uni_h12_urdf","h1_2","ankle_pitch",60,9,-0.897334,0.523598,"Spec: ankle ~75x2 N*m."),
 unitree_joint("uni_h12_urdf","h1_2","ankle_roll",40,9,-0.261799,0.261799),
 unitree_joint("uni_h12_urdf","h1_2","shoulder_pitch/roll",40,9,-3.14,1.57,"Spec page says shoulder ~120 N*m peak. CONFLICT with URDF 40."),
 unitree_joint("uni_h12_urdf","h1_2","shoulder_yaw",18,20,-2.66,3.01),
 unitree_joint("uni_h12_urdf","h1_2","elbow",18,20,-0.95,3.18,"Spec page says elbow ~120 N*m peak. CONFLICT with URDF 18."),
 unitree_joint("uni_h12_urdf","h1_2","wrist_roll",19,31.4,-3.01,2.75,"Spec page wrist ~30 N*m peak."),
 unitree_joint("uni_h12_urdf","h1_2","wrist_pitch",19,31.4,-0.4625,0.4625,"Only +-26.5 deg."),
 unitree_joint("uni_h12_urdf","h1_2","wrist_yaw",19,31.4,-1.27,1.27),
]
platforms["unitree_h1_2"] = {
 "name": "Unitree H1-2", "maker": "Unitree", "status": "shipping",
 "general": [
  r("height",1.78,"m","uni_h1_page",OFF,"high",False),
  r("mass",70,"kg","uni_h12_docs",OFF,"high",False),
  r("dof_total",27,"count","uni_h12_docs",OFF,"high",False,"Per leg 6, per arm 7 (3 shoulder, 1 elbow, 3 wrist), waist 1."),
  r("knee_torque",360,"N*m","uni_h12_docs",OFF,"high",False,"M107 peak."),
  r("hip_torque",220,"N*m","uni_h12_docs",OFF,"high",False),
  r("waist_torque",220,"N*m","uni_h12_docs",OFF,"high",False),
  r("shoulder_torque",120,"N*m","uni_h12_docs",OFF,"medium",False,"Spec page; URDF effort 40 N*m (conflict)."),
  r("elbow_torque",120,"N*m","uni_h12_docs",OFF,"medium",False,"Spec page; URDF effort 18 N*m (conflict)."),
  r("wrist_torque",30,"N*m","uni_h12_docs",OFF,"high",False,"Spec page peak; URDF 19 N*m."),
  r("arm_payload_peak",21,"kg","uni_h12_docs",OFF,"high",False,"Rated about 7 kg."),
  r("battery",0.864,"kWh","uni_h12_docs",OFF,"high",False,"15 Ah, 67.2 V max."),
  r("walking_speed",2,"m/s","uni_h12_docs",OFF,"high",False,"'<2 m/s'."),
  r("continuous_torque",None,"N*m","uni_h12_docs",NONE,"none",True,"Not published."),
  r("gear_ratio",None,"ratio","uni_h12_docs",NONE,"none",True,"Not published."),
 ],
 "joints": h12,
}
# ---------------- Atlas
platforms["boston_dynamics_atlas_electric"] = {
 "name": "Boston Dynamics Atlas (electric, product version)", "maker": "Boston Dynamics (Hyundai)", "status": "product launched CES 2026; 2026 units committed to Hyundai/Google DeepMind (media)",
 "general": [
  r("height",1.9,"m","bd_atlas_sheet",OFF,"high",False),
  r("mass",90,"kg","bd_atlas_sheet",OFF,"high",False),
  r("dof_total",56,"count","bd_atlas_sheet",OFF,"high",False),
  r("payload_instant",50,"kg","bd_atlas_sheet",OFF,"high",False,"Sustained 30 kg, one-handed 20 kg."),
  r("reach",2.3,"m","bd_atlas_sheet",OFF,"high",False),
  r("battery_life",4,"h","bd_atlas_sheet",OFF,"high",False,"2 h with heavy lifting; 3 min self-swap; 1.5 h charge. Capacity (kWh) not published."),
  r("ip_rating","IP67","","bd_atlas_sheet",OFF,"high",False),
  r("joint_range","continuous rotation on several joints","","bd_atlas_page",OFF,"high",False,"Range of Motion: Continuous (marketing)."),
  r("peak_torque_any_joint",None,"N*m","bd_atlas_sheet",NONE,"none",True,"Per-joint torque NOT published."),
  r("continuous_torque",None,"N*m","bd_atlas_sheet",NONE,"none",True,"Not published."),
  r("max_joint_speed",None,"rad/s","bd_atlas_sheet",NONE,"none",True,"Not published."),
  r("gear_ratio",None,"ratio","bd_atlas_sheet",NONE,"none",True,"Not published."),
  r("wrist_forearm_hip_yaw_waist_specs",None,"","bd_atlas_sheet",NONE,"none",True,"Not published. Qualitative only: CEO says 'stronger at most joints than a person, and even an elite athlete' (IEEE Spectrum 2024, prototype-era)."),
 ],
 "joints": [],
}
# ---------------- Tesla
platforms["tesla_optimus"] = {
 "name": "Tesla Optimus (Gen 1 AI Day 2022 / Gen 2 Dec 2023 / V3 in development)", "maker": "Tesla", "status": "not commercially available as of research date (RoboZaps/media); no official full spec sheet",
 "general": [
  r("actuator_count_ai_day_2022",28,"count","tesla_aiday_summary","media_summary","medium",False,"14 rotary + 14 linear; pre-Gen 2. Not confirmed for Gen 2."),
  r("rotary_actuator_torque_classes",[20,110,180],"N*m","tesla_aiday_summary","media_summary","low",True,"From AI Day 2022 coverage (WebSearch synthesis); primary video not transcribed. Gen 2/3 values unknown. Which class drives wrist/hip/waist not retrieved."),
  r("linear_actuator_force_classes",[500,3900,8000],"N","tesla_aiday_summary","media_summary","low",True,"Same caveat."),
  r("battery_ai_day_2022",2.3,"kWh","forbes_2022",MEDIA,"medium",False,"52 V; pre-Gen 2 design figure."),
  r("mass_2022",73,"kg","forbes_2022",MEDIA,"medium",False,"2022 target; Gen 2 stated 10 kg lighter (relative) - absolute Gen 2 mass NOT published."),
  r("mass_gen2",None,"kg","newatlas_gen2",NONE,"none",True,"Do not compute 73-10; unofficial arithmetic."),
  r("hand_dof_gen2",11,"count","newatlas_gen2",MEDIA,"medium",False,"Tesla Dec 2023 post; V3 hand reported 22 DoF via patents/media (unconfirmed, may have changed)."),
  r("hand_dof_v3_patent",22,"count","teslarati_v3","media_patents","low",True,"Patent-derived; Musk reportedly said architecture changed after Apr 2026."),
  r("neck_dof_gen2",2,"count","newatlas_gen2",MEDIA,"medium",False),
  r("walking_speed_gen2","+30% vs previous","","newatlas_gen2",MEDIA,"medium",False,"Relative claim only."),
  r("height",None,"m","robozaps_g2",NONE,"none",True,"1.73 m (5'8\") was a 2021 concept target, not Gen 2 spec."),
  r("peak_torque_wrist_forearm_hip_yaw_waist",None,"N*m","tesla_aiday_summary",NONE,"none",True,"No joint-level specs published."),
  r("continuous_torque",None,"N*m","tesla_aiday_summary",NONE,"none",True,"Not published."),
  r("max_joint_speed",None,"rad/s","tesla_aiday_summary",NONE,"none",True,"Not published."),
  r("gear_ratio",None,"ratio","tesla_aiday_summary",NONE,"none",True,"Harmonic/strain-wave gearing in rotary actuators (media summary); ratios not published."),
 ],
 "joints": [],
}
# ---------------- Figure
platforms["figure_02"] = {
 "name": "Figure 02", "maker": "Figure AI", "status": "deployed at BMW (company claim); not general sale",
 "general": [
  r("hand_dof",16,"count","fig02_pr","official_press","high",False,"'Human-equivalent strength' (no number)."),
  r("battery",2.25,"kWh","fig02_pr","official_press","high",False,"5 h run-time is a target (IEEE Spectrum)."),
  r("height",1.68,"m","fig02_agg",AGG,"low",True,"Third-party; official page 404 at fetch."),
  r("mass",70,"kg","fig02_agg",AGG,"low",True),
  r("payload",20,"kg","fig02_agg",AGG,"low",True,"Conflicting third-party values: 20 / 25 / 40 kg. No official figure retrieved."),
  r("dof_total",None,"count","fig02_pr",NONE,"none",True,"A Chinese broker report estimates ~39; not an official number."),
  r("peak_torque_any_joint",None,"N*m","fig02_pr",NONE,"none",True,"Not published."),
  r("continuous_torque",None,"N*m","fig02_pr",NONE,"none",True,"Not published."),
  r("max_joint_speed",None,"rad/s","fig02_pr",NONE,"none",True,"Not published."),
  r("gear_ratio",None,"ratio","fig02_pr",NONE,"none",True,"Not published."),
  r("wrist_forearm_hip_yaw_waist_specs",None,"","fig02_pr",NONE,"none",True,"Not published."),
 ],
 "joints": [],
}
platforms["figure_03"] = {
 "name": "Figure 03", "maker": "Figure AI", "status": "announced 2025-10-09; home/commercial roll-out claimed",
 "general": [
  r("mass_vs_f02","-9%","","fig03_news","official_press","high",False,"'9% less mass and significantly less volume than Figure 02'."),
  r("actuator_speed_vs_f02","2x faster","","fig03_news","official_press","medium",False,"'actuators can perform at 2x faster speeds with improved torque density'; no absolute numbers."),
  r("wireless_charge_power",2,"kW","fig03_news","official_press","high",False,"Inductive, in feet."),
  r("height",1.73,"m","fig_order_page","third_party_unofficial","low",True,"5'8\" per unofficial domain; not from figure.ai."),
  r("mass",63,"kg","fig_order_page","third_party_unofficial","low",True,"Consistent with 70 kg x 0.91 = 63.7 but unofficial."),
  r("peak_torque_any_joint",None,"N*m","fig03_news",NONE,"none",True,"Not published."),
  r("continuous_torque",None,"N*m","fig03_news",NONE,"none",True,"Not published."),
  r("max_joint_speed",None,"rad/s","fig03_news",NONE,"none",True,"Only relative (2x vs F02)."),
  r("gear_ratio",None,"ratio","fig03_news",NONE,"none",True,"Not published."),
  r("hand_dof",None,"count","fig03_news",NONE,"none",True,"Official post gives no DoF count."),
  r("battery",None,"kWh","fig03_news",NONE,"none",True,"UN38.3 certified; capacity not stated in post."),
 ],
 "joints": [],
}

# ------------- requirements & assessment
req = {
 "source_id": "req350",
 "model": "env/models/humanoid_golf_v3.xml (current wrist 60 N*m, damping 2, no pelvis yaw, chest yaw +-45 deg)",
 "needs": {
  "wrist_peak_torque_nm": {"value": 120, "kind": "recommended in repo doc (derived; assumes model damping 2 for 50% margin at 130 mph)"},
  "wrist_speed_rad_s": {"value": 26.5, "kind": "derived from 130 mph club speed in repo doc"},
  "wrist_torque_if_damping_0p5_nm": {"value": 26.5, "kind": "derived here: tau >= 2*b*w for 50% margin at w=26.5 rad/s, b=0.5. Torque available at speed is below stall peak; treat as optimistic"},
  "pelvis_yaw": {"torque_nm": 150, "speed_deg_s": 500, "range_deg": 60, "kind": "recommended in repo doc (+-60 deg, >=500 deg/s, ~150 N*m)"},
  "chest_yaw_range_deg": {"value": 70, "kind": "repo doc"},
  "club_head_speed_mph": 130,
 }}
def j(p, n): return next(x for x in platforms[p]["joints"] if x["joint"].startswith(n))
assess = [
 {"platform": "unitree_g1", "wrist_120nm": "NO (verified from URDF): 25 N*m roll, 5 N*m pitch/yaw; 21%/4% of target. Speed 37/22 rad/s.",
  "wrist_26nm_if_low_damping": "Roll joint only, marginal: 25 N*m peak at 37 rad/s limit (peak torque not available at speed). Pitch/yaw no.",
  "pelvis_yaw": "PARTIAL (verified URDF): waist yaw 88 N*m (59% of 150), 32 rad/s = 1834 deg/s (>500), +-150 deg (>60). Speed/range OK, torque short.",
  "overall": "Could plausibly meet pelvis-yaw speed/range only; not wrist.", "evidence": "official model file (medium)"},
 {"platform": "unitree_h1", "wrist_120nm": "NO: base H1 has no wrist joint.", "wrist_26nm_if_low_damping": "NO (no wrist).",
  "pelvis_yaw": "YES on URDF numbers: torso 200 N*m, 23 rad/s = 1318 deg/s, +-135 deg.", "overall": "Meets pelvis/waist-yaw need on paper; no wrist.", "evidence": "official model file (medium)"},
 {"platform": "unitree_h1_2", "wrist_120nm": "NO: wrist 19 N*m (URDF) / ~30 N*m (spec page), 16-25% of target.",
  "wrist_26nm_if_low_damping": "CLOSE but short: 19-30 N*m peak at up to 31.4 rad/s limit vs ~26.5 N*m derived; wrist pitch range only +-26 deg (URDF), so cannot do 120 deg uncock arc on that axis.",
  "pelvis_yaw": "YES on URDF numbers: torso 200 N*m (spec 220), 23 rad/s, +-135 deg. Hip yaw only +-25 deg.",
  "overall": "Best verified candidate for waist yaw + 3-DoF wrist; wrist still under-specced. Shoulder/elbow torque specs conflict (120 vs 40/18).", "evidence": "official spec page + model file (medium-high)"},
 {"platform": "boston_dynamics_atlas_electric", "wrist_120nm": "UNKNOWN - no joint torque published.", "wrist_26nm_if_low_damping": "UNKNOWN.",
  "pelvis_yaw": "UNKNOWN numerically; 'continuous rotation' range claimed (marketing).", "overall": "Cannot be assessed from public data. Plausible-but-unverified given 90 kg/56 DoF and CEO strength claim.", "evidence": "none quantitative"},
 {"platform": "tesla_optimus", "wrist_120nm": "UNKNOWN. A 110-180 N*m rotary class existed on AI Day 2022 (unverified, media), but which joint is not retrieved and a wrist at 120 N*m is physically implausible for that class of hand/forearm.",
  "wrist_26nm_if_low_damping": "UNKNOWN; the 20 N*m rotary class (unverified) would be near but under.", "pelvis_yaw": "UNKNOWN; 110/180 N*m class could in principle serve a waist (unverified).",
  "overall": "Cannot be assessed; do not use for requirements.", "evidence": "media only, low"},
 {"platform": "figure_02_03", "wrist_120nm": "UNKNOWN.", "wrist_26nm_if_low_damping": "UNKNOWN.", "pelvis_yaw": "UNKNOWN.",
  "overall": "No joint specs published (only relative F03 2x actuator speed).", "evidence": "none quantitative"},
]
out = {
 "schema_version": 1, "name": "humanoid_actuator_specs", "generated_by": "scripts/gen_humanoid_actuator_specs.py",
 "generated_for": "Trainer/Evaluator: realism bounds for humanoid actuator limits in the MuJoCo golf model",
 "date_researched": "2026-10-17",
 "notes": [
  "unverified=true -> value null or taken from a low-confidence/unofficial source; do not use as a hard constraint.",
  "Vendor 'max/peak torque' numbers are not continuous ratings. URDF effort/velocity are control-model limits and sometimes disagree with spec sheets (flagged per record).",
  "Joint max speeds are limits; real motors cannot deliver peak torque at max speed (torque-speed curve not published for any platform).",
  "No continuous torque, gear ratio or torque-speed curve was found for any platform in primary sources.",
  "Golf-swing needs are model-derived (see req350) and not measured human wrist torque; Nesbit 2005 measured max grip torque 42 N*m for scratch golfers.",
 ],
 "sources": S, "platforms": platforms, "model_requirements": req, "plausibility_assessment": assess,
 "recommendation": [
  "Treat Unitree H1-2 (27 DoF, 3-DoF wrists, 200 N*m waist yaw) as the reference platform for realistic limits: wrist ~19-30 N*m, 31 rad/s, waist yaw 200 N*m @ 23 rad/s.",
  "A 120 N*m wrist is ~4-6x above anything verified (best verified wrist 30 N*m). Prefer lowering wrist damping to <=0.5 and capping wrist torque at ~30 N*m to keep sim-to-real plausible; expect <130 mph club speed unless club/lever or other joints compensate.",
  "Add pelvis/waist yaw with torque <=200 N*m, speed <=23 rad/s, range ~+-135 deg to match H1/H1-2 verified limits.",
  "Mark Atlas/Optimus/Figure comparisons as unverified until vendors publish torque/speed.",
 ],
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print("wrote", OUT)
