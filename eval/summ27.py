import json,sys,glob
for f in sys.argv[1:]:
    d=json.load(open(f))
    for k in ("policy_det","policy_stoch"):
        p=d[k]; print(f.split('/')[-1][:40],k,"carry %.1f lat %.2f contact %.2f launch %.1f smash %.3f spin %.0f club %.1f pass %s"%(p["mean_carry"],p["lateral_std"],p["contact_rate"],p["launch_elev_mean_deg"],p["smash_factor_median"],p["backspin_rpm_mean"],p["peak_club_mph_mean"],d["gate_pass"]))
