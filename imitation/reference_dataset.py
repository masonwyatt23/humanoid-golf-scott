"""
Multi-swing reference loader for PureGolf / Adam Scott style content.

Supports:
- Multiple .npz reference files (from synthetic or processed video)
- Random sampling of swings during training
- Style tagging
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Optional


class ReferenceDataset:
    def __init__(self, reference_dir: Path, styles: Optional[List[str]] = None):
        self.references: List[Dict] = []
        ref_dir = Path(reference_dir)
        
        patterns = ["*.npz"]
        if styles:
            patterns = [f"{s}_swing.npz" for s in styles] + ["*_processed.npz"]
        
        for pattern in patterns:
            for path in ref_dir.glob(pattern):
                try:
                    data = np.load(path)
                    self.references.append({
                        "path": str(path),
                        "joints": data["joints"],
                        "club_head": data["club_head"] if "club_head" in data else None,
                        "dt": float(data["dt"]) if "dt" in data else 0.01,
                        "name": path.stem,
                    })
                    print(f"Loaded reference: {path.name} ({len(data['joints'])} frames)")
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
        
        if not self.references:
            raise ValueError(f"No references found in {ref_dir}")
    
    def sample(self) -> Dict:
        """Return a random reference motion."""
        return self.references[np.random.randint(len(self.references))]
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        for ref in self.references:
            if name in ref["name"]:
                return ref
        return None
    
    def __len__(self):
        return len(self.references)
