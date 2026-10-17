# Face angle and club path at impact: what Mason's data can and cannot supply

Engineering note. Everything numeric here is a proxy and **unverified** against any club or ball measurement. Machine-readable stub: `data/references/mason_impact_face_path_proxies.json`.

## Short answer

**Face angle, face-to-path, club path, attack angle, dynamic loft and shaft lean are unavailable.** No Mason file contains club or ball data (`mason_impact_geometry_targets.json` lists them all as `unavailable`; the Mason `.npz` files have `club: unknown` and no `club_head` array). They cannot be recovered from what we have.

## Why not from ~30 fps video

- The sources are screen recordings of social-feed playback with ~30 unique fps (60 Hz upsampled). Downswing is ~4-6 source frames, so impact timing is +-~0.05 s, far coarser than the contact interval, which lasts only about a millisecond [general physics, not measured here].
- The pose model tracks the body (wrists, hands), not the club. Hand path is not clubhead path; the shaft and face are never observed.
- Face angle and club path are defined relative to the target line and ball, in 3D, at ~0.1 ms resolution. They need a launch monitor (radar or camera based) or a high-speed club-tracking camera.
- Monocular world landmarks have a model-prior depth axis; the inferred target axis disagrees with the labelled view for most down-the-line clips (only 2-3 clips pass view-axis agreement).
- Several clips are edited, looped or flipped; the feed view mix is mostly down-the-line (one face-on recommended clip, one oblique).

## What proxies do exist

(All from `data/references/mason_impact_geometry_targets.json`; 11 v2 swings unless noted; medians with IQR; units are torso lengths or per-torso-length-second, not metres.)

| Proxy | Median [IQR] | Usable as | Caveat |
|---|---|---|---|
| Hand height at impact | 0.39 [0.34, 0.43] | soft reward band | vertical only, view-robust-ish |
| Hand height at top | 1.25 [1.23, 1.37] | soft reward band | |
| Hand low point minus impact event (s) | +0.067 [0.067, 0.083] | timing band | implies the impact event is early; prefer low-point-relative |
| Peak hand speed (torso/s) | 12.9 [12.0, 15.2] | relative hand-speed band | not mph; cannot give club speed |
| Hand position along target axis at impact | -0.08 [-0.19, 0.00] | diagnostic only | depth-driven |
| Lead-arm lean at impact (deg) | about -58 | diagnostic only | arm line, not shaft; largely depth smear |
| Hand-path direction (target / vertical) | see JSON `hand_path` | vertical + timing only | lateral ("oth") sign is arbitrary per clip: not usable |

A hand-path direction could hint at path (in-to-out vs out-to-in) only for a calibrated face-on or down-the-line view with a known target line; we do not have that, so **no path proxy is offered**. Lateral spread (shot dispersion) has no source at all: ball flight was never observed.

## What would close it

- A launch monitor (club path, face angle, face-to-path, attack angle, dynamic loft, club and ball speed, spin, launch) logged per swing, matched to the video by swing number. See `docs/FILMING_PROTOCOL.md`.
- Optional: 240 fps two-view video with a visible club; even then face angle from video is rough (a few degrees at best) and should be validated against the launch monitor.
- Until then, treat any impact-geometry reward as hand-height/timing shaping only.
