---
name: Data contribution
about: Propose new swing data, mocap or references
labels: data
---

**What data** (type, number of swings/clips, handedness, capture fps, camera view, club/ball measurements if any)

**Source and licence** (URL, licence name and version, link to terms)

## Licensing and consent checklist (all must be ticked before any data is committed)

- [ ] I own the data, or the licence explicitly permits redistribution of derived data in an open repository.
- [ ] Commercial use status is known: commercial OK / non-commercial only / unknown (unknown is treated as not commercial).
- [ ] Any required attribution or acknowledgement text is written down.
- [ ] Every identifiable person in the footage gave informed consent for their motion to be used and published as derived data, or is me.
- [ ] The data does not depict or imitate a named third-party player without their permission.
- [ ] No platform terms are violated (e.g. scraping, or redistributing re-encoded social-media video).
- [ ] I will commit only small derived files (`.npz` / JSON), **no raw video**.
- [ ] I will tag files via `data/provenance.py` and add them to `docs/REFERENCE_PATHS.md`.

**Anything uncertain** (list it; maintainers will not merge until resolved)
