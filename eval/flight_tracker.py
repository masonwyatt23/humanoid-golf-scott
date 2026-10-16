"""
Track ball flight metrics over time: distance, lateral dispersion, launch direction.
Supports analysis of 300-yard potential, left/right misses, and consistency.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class FlightTracker:
    def __init__(self, log_dir: str = "results"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.shots: List[Dict] = []
    
    def record_shot(self, info: Dict, style: str = "scott"):
        shot = {
            "timestamp": datetime.utcnow().isoformat(),
            "style": style,
            "distance": info.get("ball_distance", 0.0),
            "lateral": info.get("ball_lateral", 0.0),
            "contacted": info.get("contacted", False),
            "ball_speed": info.get("ball_speed", 0.0),
            "launch_direction_rad": info.get("launch_direction", 0.0),
        }
        self.shots.append(shot)
    
    def summary(self) -> Dict:
        if not self.shots:
            return {"shots": 0}
        contacted = [s for s in self.shots if s["contacted"]]
        distances = [s["distance"] for s in contacted]
        laterals = [s["lateral"] for s in contacted]
        return {
            "total_shots": len(self.shots),
            "contact_rate": len(contacted) / len(self.shots),
            "mean_distance": float(np.mean(distances)) if distances else 0.0,
            "max_distance": float(np.max(distances)) if distances else 0.0,
            "mean_lateral": float(np.mean(laterals)) if laterals else 0.0,
            "lateral_std": float(np.std(laterals)) if laterals else 0.0,
            "left_miss_rate": float(np.mean([l < -0.5 for l in laterals])) if laterals else 0.0,
            "right_miss_rate": float(np.mean([l > 0.5 for l in laterals])) if laterals else 0.0,
        }
    
    def save(self, name: str = "flight_log"):
        path = self.log_dir / f"{name}.json"
        with open(path, "w") as f:
            json.dump({"shots": self.shots, "summary": self.summary()}, f, indent=2)
        print(f"Saved {len(self.shots)} shots to {path}")
        return path


if __name__ == "__main__":
    tracker = FlightTracker()
    tracker.record_shot({"ball_distance": 0.5, "ball_lateral": 0.1, "contacted": True, "ball_speed": 5.0})
    tracker.record_shot({"ball_distance": 0.3, "ball_lateral": -0.2, "contacted": True, "ball_speed": 4.0})
    print(tracker.summary())
    tracker.save()
