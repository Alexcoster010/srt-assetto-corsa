# SRT r07 driver-feedback prototype

This revision implements the team's feedback where the available evidence permits it. It is a test candidate, not a validated digital twin. The 2025-2026 CAD appearance and 18 x 6 inch tire envelope remain intact.

## Changes and evidence

| Feedback | r07 change | Verification and remaining limit |
|---|---|---|
| Cannot see gear | Original fixed dash: large gear, RPM, speed; 8 shift lamps from 11,000 to 14,500 RPM, flashing at 14,500 | All model bindings/fonts loaded in AC; 9 analytical sightlines clear. Driver animation and live screen readability not visually verified. |
| Revs climb too quickly | Engine inertia 0.08 -> 0.12 kg m2 | 50% increase. Free-engine acceleration at equal net torque becomes 2/3 of r06; loaded acceleration is not reduced by this same factor. Value is a tuning assumption, not measured SRT inertia. |
| Sound stops distinguishing revs | MAD MFT02 reference sound replaces Tatuus reference sound | FMOD 1.08.18 metadata: old cockpit RPM parameter 0-15,000; new cockpit/exterior 0-20,000. Car limiter remains 16,000. Sample/pitch behavior still needs listening; this is not an SRT Kawasaki recording. |
| Short-feeling gears | Keep documented six ratios, 1.9 primary and 47/14 final chain ratio | At 14,500 RPM, theoretical speeds are 68.8, 89.0, 105.9, 122.4, 137.9, 150.7 km/h. Loaded radius, slip, drag and rev drop affect actual speed. |
| No force feedback | Standard AC FFB path; linear STEER_ASSIST=1, provisional car gain 1 -> 2.5; optional diagnostic | No wheel-specific bindings, LUTs, or drivers. Stronger gain cannot fix a disabled device or zero upstream forces. Physical wheel response unverified. |
| Needs aero | Preliminary equivalent axle forces: CL*A=2.60 m2, CD*A=1.00 m2, 40% front | Load tables initialized in AC. Anchored to partial CFD forces, with substantial assumptions below. Not validated on track. |
| Brake feedback | Preserve team-derived torque baseline; expose 60-85% front-bias adjustment, default 75% | Existing MAX_TORQUE=571 retained. Driver clarified steering FFB but did not specify a braking symptom. No unsupported brake-torque retune. |
| Grass feels like pavement | Read-only surface audit and tire/slip logging | Exact Sazuka FS mod is absent locally. No track or road-tire grip changes made; issue remains open. |

## Preliminary aero assumptions

Source: team `SRT_26/5 - Aerodynamics/3 - CFD/Individual component results.xlsx`, rear-wing sheet row 6, GEB-RW-1.2*: 38.58 downforce, 23.88 drag at 30 mph. Units are inferred as lbf from the template row. The earlier starred row explicitly says “with headreast, body”; the same meaning for row 6's star is an inference. The source's CL/CD reference areas are inconsistent across rows, so its coefficients were not copied into the car.

At assumed density 1.225 kg/m3, 38.58 lbf is 171.6 N and corresponds to CL*A about 1.56 m2. This supplies the rear effective-load anchor. Choosing 40% front load implies total CL*A=2.60 m2. **The front balance and total are assumptions**, since front-wing results are missing. CD*A=1.00 m2 is a rounded provisional closure near the starred rear/body drag of 106.2 N at 30 mph; it is not a full-car drag measurement. Undertray forces were not added because combining isolated component results would risk double counting interaction effects.

Equivalent force locations are at the physics axles relative to the center of gravity. This preserves the selected static aero balance. Drag acts at CG height as a simplifying assumption. Angle response is a bounded cosine-squared lift / sine-squared drag approximation, without measured stall, yaw, ground-height or pitch data. Wing shapes in the visual model do not establish their aerodynamic performance.

| Speed | Downforce | Drag |
|---|---:|---:|
| 48.3 km/h (30 mph) | 286 N | 110 N |
| 60 km/h | 442 N | 170 N |
| 80 km/h | 786 N | 302 N |
| 100 km/h | 1,229 N | 473 N |
| 120 km/h | 1,769 N | 681 N |

Do not use these numbers for real-car design decisions. A full-car CFD result or coastdown/downforce measurement should replace the provisional closure.

## Wheel-independent force feedback

The car uses Assetto Corsa's normal force-feedback output, suitable for AC-supported force-feedback wheels. Actual device configuration is still required for each wheel. No G920-specific customization was installed, and the host's global keyboard/wheel selection was not changed. This host currently uses keyboard input; it cannot prove the driver's G920 response.

The front steering-axis geometry has positive caster and finite mechanical trail; car FFMULT is nonzero. The provisional 2.5 gain is a normalization candidate, not a proven repair. Test on the driver's normal settings, reducing per-car gain if forces saturate. If a known-working Kunos car also has no forces, investigate that wheel's game/device setup first. If only SRT has no forces, collect the diagnostic log. Stock G920 pedals do not provide active brake-pedal force feedback; steering feedback and pedal feel are separate.

## Optional diagnostic app

The download includes `apps/python/SRT_Diagnostics`. Enable **SRT Diagnostics** in Assetto Corsa's Python apps settings, then select it from the in-session app bar. The app displays gear/RPM and game FFB. It logs at about 10 Hz to `Documents/Assetto Corsa/logs/srt_driver_YYYYMMDD_HHMMSS.jsonl`, capped at 90 minutes per session. Disable it after testing if no log is needed. It only reads telemetry and never changes controls or forces.

Log a short paved lap with several medium-speed corners and straight-line braking, then a controlled grass excursion on Sazuka FS. `LastFF` is normalized game output, not measured wheel torque. Tire-surface information may be unavailable (`-1`); contact behavior and the track's actual collision/surface mapping still need inspection. The source repository includes a log summarizer that refuses to call an idle run an FFB pass, and a read-only surface configuration auditor.

## Brakes and surfaces

At the baseline 75% split, the retained torque parameter corresponds to 428.25 Nm front and 142.75 Nm rear per wheel under the existing AC model convention, matching the project's pedal-force gains at 533.79 N. Hardware measurements, actual pedal calibration and lock sequence remain unverified. Bias adjustment allows a controlled comparison without inventing a new master-cylinder or caliper model. Change one setting at a time.

Magione's grass entries use friction 0.60, versus roughly 0.97-1.0 on asphalt. That comparison is a local example, not proof about Sazuka FS. The car's approximate high-grip slick model may also contribute to excessive off-road grip. The correct fix needs the actual track surface definitions, collision assignments, any CSP overrides, and a driving trace.

## Validation scope

Passed: exact KN5 binary readback; unique mesh names; four tires at 0.4572 m OD / 0.1524 m width; dash parent/LED bindings and installed fonts; nine unobstructed car-body sightlines to the screen; forward road rays; unchanged torque map, ratios, suspension, tire and brake files; AC load at Magione with 1,400 RPM idle; diagnostics execute in AC's Python runtime.

Not passed or claimed: a driven lap, observed live cockpit text, shift-light timing seen on screen, audio listening/pitch sweep, physical wheel force/FFB clipping, braking distance/lock sequence, aero force response in motion, Sazuka FS grass behavior, or calibrated real-car equivalence. The game log contains a pre-existing missing optional acnotify app warning.

SDK references: installed Kunos `sdk/dev/content/cars/formula_k/data` examples for digital instruments, setup, controls and aero; installed `apps/python/system/acsys.py` for telemetry. FMOD API metadata inspected using the game's own 1.08.18 runtime; parameter layout from Firelight's header mirrored at https://github.com/JoshParnell/libphx/blob/master/ext/include/fmod/fmod_studio_common.h. Physics conventions cross-checked against the modder-authored https://github.com/archibaldmilton/Girellu/wiki/Physics-Pipeline/686faddc31d1ae226258ba28a0cdc1be11f2e4a2.
