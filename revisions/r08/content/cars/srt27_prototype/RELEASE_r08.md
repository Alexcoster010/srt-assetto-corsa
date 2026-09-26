# SRT r08 — driver tuning and two-step prototype

Requires original PC Assetto Corsa and **Custom Shaders Patch 0.2.11**. Install CSP first from https://acstuff.club/patch/. This car uses extended physics and is not compatible with stock AC alone. CSP itself is not included.

Back up content/cars/srt27_prototype, then install the full r08 car ZIP through Content Manager or merge its content folder into the game. This updates the existing car ID. Fully restart the driving session. Restore the prior complete car folder for rollback.

Changes from r07: engine inertia 0.12 -> 0.03 kg m2; maximum brake torque 571 -> 1142 Nm, front share remains 75%; added 8000 rpm two-step. Stop, select second, fully depress clutch and apply throttle. Limiter arms below 0.5 km/h with clutch depressed over 95%; release below 80% restores normal 16000 rpm limit. Driver must control clutch; keyboard automatic clutch does not reproduce that procedure.

Force feedback correction: multiplier reduced 2.5 -> 0.5 (80% reduction), steering assist 1.0 -> 0.8 matching the inspected MAD MFT02 reference. MAD uses FFMULT 9.721 with different steering geometry/tires, so its multiplier was NOT transplanted. SRT steering ratio/lock/linkages and global wheel settings remain unchanged. Driver reported violent/excessive forces on Logitech; this reduced-gain candidate has NOT been verified on a physical wheel. Stop the old session before testing the revision.

Power curve, gear ratios, differential, aero, tires, sound and CAD model are unchanged. No added low-end torque or launch-clutch fix is included. Driver reports RPM drops and recovers slowly at launch; this is unresolved. 4.3 s acceleration target has NOT been demonstrated.

The separate acceleration ZIP includes a 75 m track and timer: green start at 0 m, native separate finish gate and visible checkered leading edge/FINISH 75 M banner at 75 m, 150 m braking space. Enable SRT Acceleration in Python apps and open its HUD. Timer starts/stops at fixed-line forward crossings; it uses car position, not physical timing-beam geometry. Native gate crossings and the new finish banner still require driven/visual validation.

Verified: installed car loads/idles on acceleration track; CSP physics script reports loaded; Lua two-step state logic and fixed-gate timer tests pass; track geometry gates/paint alignment pass binary/coordinate checks. Actual limiter holding behavior and the latest finish banner have not been visually verified. More engine torque is not claimed necessary or added.

Earlier DRIVER_FEEDBACK.md / DRIVER_TUNING_r071.md describe historical baselines; this document supersedes their inertia/brake values. Optional SRT Diagnostics app retained. Temporary MAD audio/driver and Kunos dependencies remain; no third-party asset rights are granted. No game executable or CSP binary is redistributed.
