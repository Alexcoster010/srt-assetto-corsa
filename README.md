# Sooner Racing Team Assetto Corsa car

[**Download SRT r09 - increased torque**](https://github.com/Alexcoster010/srt-assetto-corsa/releases/download/v0.9.0-prototype/SRT_2025-2026_r09_Assetto_Corsa.zip) | [r09 release notes](docs/RELEASE_r09.md)

**Requires CSP 0.2.11.** Provisional +10% torque at 4000-8000 rpm, smoothly back to baseline by 11000. All other r08 physics unchanged, including 0.03 inertia and reduced FFB. This is a driver-test curve, not measured dyno data. No confirmed 4.3 s result or wheel validation. Restart the driving session after installation.

Build r08 as below, then run scripts/srt_build_r09.py for the r09 overlay. r08 remains available for comparison and rollback.

## Previous r08 version and baseline documentation

[**Download SRT r08**](https://github.com/Alexcoster010/srt-assetto-corsa/releases/download/v0.8.0-prototype/SRT_2025-2026_r08_Assetto_Corsa.zip) | [Release notes](docs/RELEASE_r08.md)

**Requires Custom Shaders Patch 0.2.11.** Install [official CSP](https://acstuff.club/patch/) before the car. Back up your existing srt27_prototype folder, then install the full ZIP through Content Manager and restart the session.

r08 reduces engine inertia to **0.03**, doubles brake torque to **1142 Nm**, and adds a clutch-triggered **8000 rpm second-gear two-step**. FFB multiplier reduced from 2.5 to 0.5 after excessive-force feedback, with MAD-reference steering assist 0.8. Wheel testing remains pending. Power curve and gearing are unchanged. **Launch bogging remains unresolved; the 4.3-second target is unverified.**

[Download the separate 75 m acceleration course and timer](https://github.com/Alexcoster010/srt-assetto-corsa/releases/download/v0.8.0-prototype/SRT_Acceleration_75m_v0.3.0.zip). Distinct green start and checkered finish with FINISH 75 M banner. [Track notes](tracks/srt_acceleration_75m/README.md).

For an r08 source rebuild, complete the r07 build below, then run scripts/srt_build_r08.py. The explicit r08 overlay is in revisions/r08/. Historical r07 values below describe the earlier release.

## Historical r07 baseline
## r07 changes

- Native gear/RPM/speed dash and eight shift lights.
- Engine inertia increased from 0.08 to 0.12 kg m2; documented ratios and torque map preserved.
- MAD high-rev reference audio with 20,000-RPM parameter range replaces the previous sound.
- Preliminary aero using partial team CFD as a force anchor, with explicit balance/drag assumptions.
- Wheel-independent AC force-feedback gain candidate and adjustable brake bias.
- Optional SRT Diagnostics app records game FFB, controls, wheel loads and tire behavior. Copy the ZIP's `apps` folder into the game and enable SRT Diagnostics in Python apps settings to use it.

The car loads at Magione with a running engine; AC initialized the dash fonts, shift LEDs, sound bank and aero tables. Driving, live cockpit readability, audio character, physical wheel response, braking and Sazuka FS grass behavior remain unverified. **No zero-FFB or grass-grip fix is claimed.** Read [the driver notes](DRIVER_FEEDBACK.md) before comparing behavior.

## Vehicle and limits

Native team CAD supplies frame, nose, wings, cockpit, steering wheel, 10-inch rims and mechanical details. Tires measure 18-inch outside diameter and 6-inch width. White/black No.31 appearance follows 2026 photos. Sidepod shells and material boundaries are inferred. No MAD vehicle mesh remains.

The saved CAD master contains design alternatives and a slightly different rear axle position from the selected physics. Visual wheel pivots follow physics. Suspension linkages are static. Driver pose, tire/differential calibration and aero are provisional. The detailed single-LOD model still needs performance testing.

## Source and rebuild

Python with NumPy and Pillow is required. CAD tessellation and saved assembly transforms are included; native re-export additionally requires SOLIDWORKS. Dimensions are in meters.

Set `SRT_AC_PROJECT` to the clone, `SRT_BASE_CAR` to an existing r06/r07 installed SRT car (for ancillary files), and `SRT_MAD_CAR` to your extracted `madformulateam_mft02` car folder. Run `scripts/srt_build_r07.py`, `scripts/srt_finish_r07.py`, `scripts/srt_feedback_r07.py`, then `scripts/srt_validate_kn5_r07.py`, in that order. The output is `release-r07/content/cars/srt27_prototype`. The feedback script must run last among the build steps; it applies the r07 physics and sound changes. Copy `DRIVER_FEEDBACK.md` into the result. Diagnostic app source is in `apps/python/SRT_Diagnostics`.

`evidence/r07/` contains validation records. The cockpit preview is a software geometry render; runtime digits are not rendered there and it is not an in-game screenshot. Tests do not establish calibrated real-car behavior.

## Provenance

Vehicle geometry derives from team CAD supplied by the user; livery/dashboard are original procedural assets. Temporary MAD driver pose/animations and high-rev audio, plus Kunos driver/ancillary dependencies, remain in the integration package and are not committed as source assets. The sound is not a recording of the SRT Kawasaki engine. No open-source license or rights to third-party assets are asserted.


## MATLAB autocross track

[Download the separate SRT MATLAB autocross track](https://github.com/Alexcoster010/srt-assetto-corsa/releases/tag/autocross-v0.1.0). The 943.28 m training loop preserves all 137 modeled cones and the existing synthetic return. It installs alongside other tracks and does not change the car. [Track guide and source](tracks/srt_michigan_autocross/README.md). Load/spawn verified; driving and timing checks remain pending.
