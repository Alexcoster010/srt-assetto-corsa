# SRT r10 - stronger off-throttle engine braking

Full car update for original PC Assetto Corsa. Requires Custom Shaders Patch 0.2.11 (https://acstuff.club/patch/). Back up content/cars/srt27_prototype, install the full ZIP through Content Manager or merge its content folder into the game, then restart the driving session. Same car ID; no CSP or game binaries included.

Change from r09: engine-braking reference torque increased 25%, from 23.75 to 29.6875 Nm at the unchanged 14500 rpm reference. FROM_COAST_REF mode and nonlinearity 0 retained. This increases engine braking; it does not imply a 25% increase in total vehicle deceleration.

Retains r09's provisional +10% torque at 4000-8000 rpm with smooth ramps from 2500 and back to baseline at 11000. Inertia 0.03, gearing/final drive, pedal brakes 1142 Nm, FFB multiplier 0.5/steering assist 0.8, two-step, differential, aero, tires, sound and geometry are unchanged.

The user tested the new session and reported liking the off-throttle behavior. That is subjective acceptance, not measured engine/coast-down calibration. No confirmed 4.3 s acceleration result or physical-wheel FFB validation is claimed. The earlier excessive Logitech force report still warrants driver retesting of the reduced FFB settings.

Validation: installed candidate differs from r09 engine.ini only in the intended coast-reference torque; all other data files match r09. Full car ZIP has a verified per-file checksum manifest. Historical release notes remain for background; this note supersedes their coast-torque value.

Optional acceleration track v0.3.0 remains unchanged: distinct start and finish 75 m apart, finish banner and timing app. Rollback/comparison: https://github.com/Alexcoster010/srt-assetto-corsa/releases/tag/v0.9.0-prototype.

Temporary MAD audio/driver and Kunos dependencies remain; no third-party asset rights are granted. The torque curve and engine braking are tuning candidates, not measured SRT engine data.
