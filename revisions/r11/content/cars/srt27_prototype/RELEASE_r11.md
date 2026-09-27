# SRT r11 - reduced cornering grip and FFB 1.5

Full car for original PC Assetto Corsa. Requires Custom Shaders Patch 0.2.11. Updates the existing srt27_prototype car.

Changes from public r10:
- FFB multiplier increased from 0.5 to 1.5; steering assist stays at 0.8. This is three times r10's gain, or 50% above private test001.
- Front and rear lateral tire reference grip scaled to81% of the original: two successive10% reductions. Longitudinal grip parameters unchanged. Tire outside diameter stays18 inches.

Retains r10's low-RPM torque increase, 0.03 engine inertia, stronger off-throttle engine braking, 1142 Nm brakes, gearing, differential, aero and visual model.

Install: back up content/cars/srt27_prototype, install the full car ZIP through Content Manager or merge its content and apps folders into the game, and restart the driving session. Car UI version is0.11.0. CSP and game binaries are not bundled.

Optional separate ZIPs contain the fixed MATLAB autocross v0.2.0 (separate start/finish, visible ground markings, return loop untimed) and acceleration v0.3.0. These track packages are unchanged from their existing releases. SHA256SUMS.txt covers all three ZIPs.

Status: experimental prototype, published at the user's request. The user liked the first10% grip reduction but requested another10%; the latest reduction has not received driver validation. Physical-wheel FFB validation remains open: the user reports SRT is heavier stationary but weaker moving than MAD MFTC3 on a CSL DD. Earlier excessive Logitech force feedback was also reported. FFB1.5 is a test setting, not a validated fix or wheel-independent calibration.

Local automated measurements were collected against MAD MFT02 before the user clarified their reference is MFTC3. That mismatched comparison does not establish a fix; the SRT60km/h section was incomplete. No automated test harness or MAD reference car is included in this release. No measured real-car tire calibration or confirmed4.3s acceleration time is claimed.

Rollback: https://github.com/Alexcoster010/srt-assetto-corsa/releases/tag/v0.10.0-prototype . r10 and private test001 remain available unchanged. Historical notes included in the car describe earlier settings; this note supersedes their FFB and lateral grip values. Existing temporary MAD audio/driver and Kunos dependencies remain; no third-party asset rights are granted.
