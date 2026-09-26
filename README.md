# Sooner Racing Team — Assetto Corsa prototype

Private development source for an SRT physics prototype with 2025–2026 visual references.

## Current state

- r03 loaded at Magione, with live shared-memory car identity and 1,400 rpm idle verified.
- Windows 0xc000007b was repaired by replacing app-local x86 VC120 loading with the official VC2013 x64 runtime.
- r05 uses native SRT Nose 25 and SRT25 front/rear wing tessellation, placed from the saved SRT26 CFD assembly.
- MAD standard IC MFT02 remains a temporary source for cockpit, running gear, and remaining body details.
- Full handling validation, cockpit visual confirmation, and replacement of remaining donor geometry are unfinished.

## Repository contents

`scripts/`: native CAD export and local r05 visual-build code.
`physics/`: SRT effective engine curve, gearing, and provisional differential setup.
`cad/`: SRT-owned native tessellation in meters and placement/source evidence.
`evidence/`: build and observed runtime records.
`docs/`: parameter assumptions and source provenance.

## Build prerequisites

Original Assetto Corsa installation and SDK; the existing SRT project r03 baseline; an independently downloaded official MAD MFT02 archive; Python with NumPy and Pillow. Native re-export additionally requires SOLIDWORKS and the configured local SolidPilot bridge.

The current build is an integration script for the existing engineering project, not yet a standalone installer. Set `SRT_AC_PROJECT` to `engineering/srt-assetto-corsa` and `MAD_MFT02_DIR` to the extracted standard `madformulateam_mft02` folder, then run `scripts/srt_visual_r05.py`. Preserve the working r03 baseline and `cad-r05` evidence in that project. Outputs are written to `release-r05`.

## Accuracy boundaries

The r35 curve is a loss-inclusive effective torque calibration, not measured crank torque. Differential .60/.42/25 is a provisional AC mapping; preload is unmeasured. Tires are an approximation. Nose and wings are real SRT CAD, but the SRT25 wings were suppressed in the CFD study; selected-year/as-built appearance still requires comparison. No claim of a validated digital twin.

## Asset provenance

No MAD/Kunos KN5 models, sound banks, packed physics, download archives, or downloaded photographs are committed. The build uses local assets. MAD model credit: Ofitus21 / MAD Formula Team. Reference photos: https://www.linkedin.com/company/sooner-racing-team . Official donor: https://www.overtake.gg/downloads/mad-formula-team-mft02.58653/ .

This repository is private; no public asset redistribution or open-source license is asserted.

## Tire dimensions
All four visual tire envelopes are normalized to 18 in outside diameter (0.4572 m) and 6 in width (0.1524 m). Physics front/rear radius is 0.2286 m. Nominal rims remain 10 in. Run normalization after every donor visual rebuild; the r05 script now includes it. Updated r05 visuals are installed locally, but the currently running session still needs reloading and r05 game-load/visual checks remain pending.
