# Mason Swing Pipeline

Drop your Instagram swing videos from @masonwgolf into `data/mason_swings/`.

## Quick Start
```bash
# 1. Export swings from Instagram (or screen-record)
# 2. Place .mp4/.mov files in data/mason_swings/
# 3. Process them
python -m data.process_mason_swings

# 4. Train on your own swings
python -m train.train_ppo --style mason --timesteps 50000
```

## Why This Is Clean
- You own the content
- No licensing risk for a commercial product
- Consistent subject for reliable style matching
- Easy to scale by filming more swings

## Current System Status
- 100% contact reliability
- Forward direction reward active
- Ball flight tracking (distance, lateral, speed)
- Synthetic Scott/Scheffler/Rory references available
- Ready for your real swing data
