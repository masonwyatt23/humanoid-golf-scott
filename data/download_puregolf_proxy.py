"""
Catalog + (opt-in) downloader of public Adam Scott swing footage used as *proxy* data.

LICENSING POLICY (read first)
-----------------------------
* Nothing here is openly licensed unless the entry says so. As of 2026-10 a search of
  Wikimedia Commons found NO video of Adam Scott (16 files, all still images), so every
  slow-motion source below is COPYRIGHTED by its publisher.
* Each entry carries a `license` field:
    - "open"        : CC / public domain; safe to redistribute (none currently).
    - "official"    : published by the tour/player on an official channel; viewing and
                      personal research use is normal, but redistribution of the video or
                      derived datasets is NOT cleared -> needs ToS review / permission.
    - "third_party" : independent creator / coaching site / aggregator. Needs the owner's
                      permission before training use or sharing. Contact the owner.
* The downloader is plain `yt-dlp` on public URLs. It does not bypass logins, DRM, geo
  blocks, or rate limits and must not be extended to. If yt-dlp cannot fetch a URL, stop
  and get the footage legitimately (ask the owner / license it).
* By default the script only LISTS sources (dry run). Downloading non-"open" entries
  needs `--download --i-have-reviewed-tos`. Keep downloaded videos out of git
  (data/raw_videos/ is gitignored) and do not redistribute them or trained-model
  derivatives without clearance.
* Derived keypoints/poses are still derivative of the footage; treat their licensing
  like the source until a lawyer says otherwise.

URLs below were returned by web search on 2026-10-15; verify each is live before use.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

RAW_DIR = Path(__file__).parent / "raw_videos"

SOURCES: List[Dict] = [
    {
        "id": "dpwt_scott_slowmo_2025",
        "url": "https://www.youtube.com/watch?v=EXxiza0Nz08",
        "desc": "DP World Tour official: Adam Scott's golf swing in slow motion, 2025 Hero Dubai Desert Classic (3:25)",
        "license": "official",
        "view": "mixed",
        "note": "Official channel, broadcast cameras; copyrighted. Review YouTube ToS + DP World Tour terms.",
    },
    {
        "id": "golfloopy_scott_2014_fo_iron_300fps",
        "url": "http://www.golfloopy.com/adam-scott-2014-fo-300fps-slow-motion-iron/",
        "desc": "Golf Loopy: Adam Scott 2014 face-on, iron, 300 fps 1080p (page embeds the video)",
        "license": "third_party",
        "view": "face_on",
        "note": "COPYRIGHTED (Golf Loopy). Highest fps but commercial site: ask for permission. Page URL, not a direct video link.",
    },
    {
        "id": "golfjapan_scott_driver_2019_ausopen",
        "url": "https://www.golftweet.com/499432/",
        "desc": "GOLF JAPAN / Michael: Scott drivers DTL+FO, Emirates Australian Open Pro-Am, Dec 2019, Sony RX10 IV 250 fps",
        "license": "third_party",
        "view": "dtl+face_on",
        "note": "COPYRIGHTED (individual creator). 250 fps, clean fixed angles = best for pose; requires permission. Page URL.",
    },
    {
        "id": "golfjapan_scott_irons_2021_wentworth",
        "url": "https://www.golftweet.com/480856/",
        "desc": "GOLF JAPAN / Michael: Scott mid & short iron DTL+FO, BMW PGA Pro-Am, Sep 2021, 250 fps",
        "license": "third_party",
        "view": "dtl+face_on",
        "note": "COPYRIGHTED (individual creator). Requires permission. Page URL.",
    },
    {
        "id": "puregolf_ig_reels",
        "url": "https://www.instagram.com/puregolf__/",
        "desc": "@puregolf__ Instagram reels (original target of this project)",
        "license": "third_party",
        "view": "mixed",
        "note": "COPYRIGHTED. Instagram ToS prohibits automated scraping; do NOT bulk-download. "
                "Only use clips with written permission from the account owner (DM / partnership).",
        "auto_download": False,
    },
]


def list_sources() -> None:
    for s in SOURCES:
        print(f"[{s['license']:11}] {s['id']}\n    {s['desc']}\n    {s['url']}\n    NOTE: {s['note']}")


def write_manifest(entries: List[Dict]) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / "sources_manifest.json"
    path.write_text(json.dumps(entries, indent=2))
    return path


def download(source: Dict) -> bool:
    if source.get("auto_download") is False:
        print(f"SKIP {source['id']}: manual/permissioned acquisition only.")
        return False
    out = RAW_DIR / f"{source['id']}.%(ext)s"
    if list(RAW_DIR.glob(f"{source['id']}.*")):
        print(f"SKIP {source['id']}: already downloaded.")
        return True
    cmd = ["yt-dlp", "--no-playlist", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
           "-o", str(out), source["url"]]
    print("RUN", " ".join(cmd))
    try:
        r = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print("yt-dlp not installed (pip install yt-dlp)")
        return False
    if r.returncode != 0:
        print(f"FAILED {source['id']} (exit {r.returncode}). Do not work around; obtain footage legitimately.")
    return r.returncode == 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--download", action="store_true", help="actually download (default: list only)")
    ap.add_argument("--i-have-reviewed-tos", action="store_true",
                    help="required to download any non-open source")
    ap.add_argument("--only", nargs="*", help="restrict to these ids")
    args = ap.parse_args(argv)

    chosen = [s for s in SOURCES if not args.only or s["id"] in args.only]
    if not args.download:
        list_sources()
        print("\n(dry run; pass --download --i-have-reviewed-tos to fetch)")
        return 0
    if not args.i_have_reviewed_tos and any(s["license"] != "open" for s in chosen):
        print("Refusing: non-open sources selected. Review licensing/ToS, then pass --i-have-reviewed-tos.")
        return 2
    ok = {s["id"]: download(s) for s in chosen}
    print("manifest:", write_manifest([dict(s, downloaded=ok[s["id"]]) for s in chosen]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
