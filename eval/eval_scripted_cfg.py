"""Evaluator-protocol (MuJoCo, flight tracker) eval of the ZERO-residual scripted swing for a given address config.
python -m eval.eval_scripted_cfg '{"ball_x":0.422,"ball_x_noise":0.005,"loft_deg":7}' [episodes] [seed]"""
import sys, json
import eval.dispersion_report as dr
base = dict(_env="residual", script=dict(q_back=2.2, t_down=0.12, t_back=0.6), residual_scale=[0.1, 0.08, 0.05, 0.05], model_xml="humanoid_golf_v3.xml", flight_model=True,
            tee_height=0.04, force_scale=2.0, kp=700.0, kd=700.0/30, loft_deg=7.0, curriculum=True, carry_reward=True, forward_reward=True, randomize_reset=True,
            ball_dz=0.008, handedness="left", gate_lo=15.0, gate_hi=35.0, seq_weight=0.0, style_prior=False, yaw_amp=0.1, wrist_amp=0.0, style_lead=0.05)
if __name__ == "__main__":
    base.update(json.loads(sys.argv[1])); n = int(sys.argv[2]) if len(sys.argv) > 2 else 50; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    dr.REFS = []
    d, _ = dr.run("x", base, n, seed, True, scripted=True)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items() if not k.startswith("dtw") and not isinstance(v, (dict, list))})
