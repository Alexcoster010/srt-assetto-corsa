# Sooner Racing Team Assetto Corsa car

## Download

[**Download the installable SRT r06 ZIP (56 MB)**](https://github.com/Alexcoster010/srt-assetto-corsa/releases/download/v0.6.0-prototype/SRT_2025-2026_r06_Assetto_Corsa.zip) · [Release notes](https://github.com/Alexcoster010/srt-assetto-corsa/releases/tag/v0.6.0-prototype)

Sign in to GitHub with access to this private repository. Drag the ZIP into Content Manager to install; back up an existing `srt27_prototype` car before updating. This is a development prerelease.

Current revision: r06. Installed as **Sooner Racing Team 2025-2026 No.31**, internal car ID `srt27_prototype`.

The car has loaded successfully at Magione, with its identity and running engine confirmed through live telemetry. Driving and on-screen cockpit visibility are still awaiting user confirmation; this is not a calibrated digital twin.

## What changed

- Native team CAD now supplies frame, nose, wings, cockpit, steering wheel, wheels, and mechanical details. No MAD vehicle mesh remains.
- White/black number31 appearance follows the public 2026 unveiling photos. Sidepod shells are inferred from photos because matching native sidepod CAD was not found.
- Tires measure18in outside diameter and6in width; nominal rims remain10in.
- Engine, power curve, drivetrain, suspension, tire, brake and aero files are unchanged from r05. Automatic shifts now use the engine's RPM range.
- Camera position is clear of car-body geometry in forward ray tests. Animated driver placement requires an in-game visual check.
- The0xc000007b startup fault was repaired earlier with the correct VC2013 x64 runtime.

## Use

In Content Manager or the game's car selector, choose **Sooner Racing Team 2025-2026 No.31**, skin **SRT No.31 White / Black**. The current practice session is set to Magione. Content Manager is downloaded in the parent engineering project's `tools/content-manager/app` folder.

## Source and rebuild

The private repository contains native CAD tessellation, saved component transforms, original build tools, physics configuration and validation records. Python with NumPy and Pillow is required. Native re-export additionally requires SOLIDWORKS. Dimensions at the CAD boundary are meters.

In a repository clone, set `SRT_AC_PROJECT` to the clone and `SRT_BASE_CAR` to the existing private installed car folder. Run `scripts/srt_build_r06.py`, followed by `scripts/srt_finish_r06.py`. The output is `release-r06/content/cars/srt27_prototype`. Back up the installed car before copying this output into the game. The baseline supplies local driver/audio assets; these are deliberately not committed. This is a local integration build, not a clean-room redistributable mod installer.

## Known limits

Sidepods and material boundaries are photo interpretations. The native master has design alternatives and a slightly different rear axle position from the selected physics; wheel pivots follow the physics. One outlying axle occurrence was replaced with a mirrored valid native axle. Suspension linkages are static visual meshes. Driver pose/animation, sound, unmeasured differential mapping/preload, tires and disabled aero remain provisional. Current mesh is a detailed single LOD; frame-rate and handling validation are pending.

## Evidence

`evidence/r06/` contains the build manifest, tire/camera checks, native geometry preview and runtime telemetry. The preview is a software geometry render, not an in-game screenshot. The engineering project retains rollback folders for prior installed revisions.

## Provenance

Vehicle meshes derive from team CAD supplied by the user. Photos were used as references and are not redistributed. Local temporary MAD driver pose/animation and Kunos driver/audio assets are excluded from Git. No public redistribution permission or open-source license is asserted.
