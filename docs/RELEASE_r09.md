# SRT r09 - increased low-RPM torque test

Full car update for original PC Assetto Corsa. Requires Custom Shaders Patch 0.2.11: https://acstuff.club/patch/. Back up content/cars/srt27_prototype, install this ZIP through Content Manager or merge its content folder, then fully restart the driving session. Same car ID as r08. CSP itself is not included.

Compared with r08, torque is increased 10% from 4000 through 8000 rpm. A smooth ramp begins above 2500 rpm and reaches 10% at 4000; above 8000 it tapers smoothly to the original curve at 11000. Idle/low RPM through 2500 and the curve at/above 11000 are unchanged. At 8000 rpm, 29.14 -> 32.05 Nm.

All other car physics are unchanged: engine inertia 0.03, gearing/final drive, brake torque 1142 Nm, FFB multiplier 0.5, steering assist 0.8, tires/differential/aero and 8000 rpm second-gear two-step. The previous gearing proposal was NOT applied.

This is a provisional driver-test curve, not measured SRT dyno data. User reported the initial test might feel good; no timed 4.3-second result, resolved launch bog or physical wheel validation is claimed. Reduced FFB still needs driver retest after the earlier excessive-force report. Historical r08/r07 notes remain background; this note supersedes their power-curve description.

The optional separate acceleration-track ZIP is unchanged v0.3.0, with separate start/finish at 75 m and FINISH 75 M banner. It includes the SRT Acceleration app; enable that Python app for recorded fixed-gate timing.

Validation: released r08 baseline hash checked; installed candidate matches the approved test; all other data files match r08; ZIP contents checked against a per-file checksum manifest. Restore r08 for comparison/rollback: https://github.com/Alexcoster010/srt-assetto-corsa/releases/tag/v0.8.0-prototype.

Original team CAD model and reference audio retained. Temporary MAD audio/driver and Kunos dependencies remain; this release grants no third-party asset rights. No game executable or CSP binary is redistributed.
