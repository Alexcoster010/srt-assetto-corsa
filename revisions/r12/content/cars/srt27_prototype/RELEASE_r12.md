# SRT r12 — tire g targets and MFTC3-based FFB

Full car update for original PC Assetto Corsa; requires CSP 0.2.11. No previous SRT installation or separate test patches required. Updates srt27_prototype, UI version 0.12.0.

Changes from public r11:
- FFMULT 1.5 -> 7.8; STEER_ASSIST 0.8 -> 1.0. Includes private test002's MFTC3-based FFB candidate.
- Front/rear lateral reference coefficients reduced another 7% from r11, to 75.33% of the original coefficients.
- Front/rear longitudinal reference coefficients reduced 30% from r11.
- Retains 18-inch tire OD, engine curve, engine inertia, gearing, differential, brake hardware settings, aero and visuals.

Local automated tests measured peak 0.25-second means of 1.798 g lateral and 1.178 g braking, targeting 1.8/1.2 g. Flat autocross asphalt, surface grip0.98, 2 L starting fuel; lateral target55 km/h, braking ramp from approximately75 km/h. Braking includes front-wheel lock. These are individual maneuver checks, not a validated full combined-slip g-g envelope or universal g cap: speed, aero, surface and driving inputs change attainable limits.

The accepted approximately1.04 g acceleration figure is an ideal torque/gearing upper bound before losses and rotational inertia, NOT measured acceleration. The automated first-gear pull measured approximately0.473 g, essentially unchanged by the tire tune. Engine and gearing were preserved as requested. No confirmed4.3-second acceleration run is claimed.

FFB was compared with standard MAD MFTC3 v1.8. Before this additional tire change, force per lateral g was within about8–9% of the reference in two moderate-load tests. Physical-wheel feel, stationary resistance and full-envelope clipping remain unverified; changing tires can affect FFB feel. Begin the first wheel test with reduced wheelbase strength. No MAD reference car or automated test mode is included.

Installation: back up the existing SRT car if installed, install the full car ZIP through Content Manager or merge its content and apps folders into the game, then restart the driving session. Optional unchanged track ZIPs contain autocross v0.2.0 (separate start/finish with visible markings and untimed return loop) and acceleration v0.3.0. SHA256SUMS.txt covers all three ZIPs.

Status: experimental prototype published at the user's request; driver validation pending. Existing provisional aero, flat tire temperature-performance curve, audio and other model limitations remain. Historical notes inside the car describe prior releases; this note supersedes their grip and FFB settings. Temporary third-party audio/driver dependencies remain; no third-party asset rights are granted.

Rollback: reinstall the full public r11 package from https://github.com/Alexcoster010/srt-assetto-corsa/releases/tag/v0.11.0-prototype . Private test002 and earlier releases remain unchanged.
