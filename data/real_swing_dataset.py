"""
GolfDB-style data integration scaffolding.

GolfDB: ~1,400 professional golf swing videos with event labels,
player names, club type, and view type (McNally et al., CVPR 2019).

This module provides the interface for loading real pro swing data
once videos are obtained. For now it falls back to high-quality
synthetic references calibrated to pro swing characteristics.
"""

from pathlib import Path
from typing import List, Dict, Optional
import numpy as np


class RealSwingDataset:
    """Interface for real pro swing data (GolfDB or equivalent)."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("data/real_swings")
        self.swings: List[Dict] = []
        self._load_available()
    
    def _load_available(self):
        if not self.data_dir.exists():
            return
        for path in self.data_dir.glob("*.npz"):
            try:
                data = np.load(path)
                self.swings.append({
                    "path": str(path),
                    "joints": data["joints"],
                    "player": str(data.get("player", "unknown")),
                    "club": str(data.get("club", "driver")),
                    "source": "real",
                })
            except Exception as e:
                print(f"Failed to load {path}: {e}")
    
    def has_real_data(self) -> bool:
        return len(self.swings) > 0
    
    def sample(self) -> Optional[Dict]:
        if not self.swings:
            return None
        return self.swings[np.random.randint(len(self.swings))]
    
    def stats(self) -> Dict:
        return {
            "real_swings": len(self.swings),
            "players": list(set(s["player"] for s in self.swings)),
        }


def get_training_references(prefer_real: bool = True) -> List[Path]:
    real = RealSwingDataset()
    if prefer_real and real.has_real_data():
        return [Path(s["path"]) for s in real.swings]
    ref_dir = Path("data/references")
    return list(ref_dir.glob("*_swing.npz"))


if __name__ == "__main__":
    ds = RealSwingDataset()
    print(f"Real swings available: {ds.stats()}")
    refs = get_training_references()
    print(f"Training references: {[p.name for p in refs]}")
