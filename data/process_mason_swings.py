"""
Process Mason's own swing videos from data/mason_swings/ into training references.

Drop Instagram exports or screen recordings into data/mason_swings/
and run this script. Clean IP — these are Mason's own swings.
"""

from pathlib import Path
import sys

def main():
    swing_dir = Path("data/mason_swings")
    swing_dir.mkdir(parents=True, exist_ok=True)
    
    videos = list(swing_dir.glob("*.mp4")) + list(swing_dir.glob("*.mov"))
    if not videos:
        print(f"No videos found in {swing_dir}")
        print("Export swings from @masonwgolf Instagram and drop them here.")
        print("Then re-run: python -m data.process_mason_swings")
        return
    
    print(f"Found {len(videos)} videos. Processing...")
    from data.process_video import process_video_batch
    try:
        process_video_batch(swing_dir, output_dir="data/references/mason")
        print("Processing complete. References saved to data/references/mason/")
    except ImportError:
        print("process_video module not fully ready. Videos are staged.")
        print("Manual step: run MediaPipe pose on each video and save joints to .npz")

if __name__ == "__main__":
    main()
