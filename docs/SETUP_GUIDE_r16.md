# SRT r16 setup guide

In the session pits, open Setup (wrench). Adjust AERO, SUSPENSION, ALIGNMENT and DAMPERS, save a named setup, and drive another run. These are pit setup controls, not an on-wheel live tuning app. Use Reset/Default for the r15 starting setup; avoid loading an older custom setup when comparing defaults.

## AERO
One slider: **Aero balance - front %**,30-50 in1 percentage-point steps; default40. Rear share is100 minus front. Higher values shift load forward; lower values shift it rearward. The script scales the existing front/rear lift gains, with nominal total CL*A2.60m2 and unchanged drag gains. Default40 produces unity gains, retaining the r15 aero. Local flow at each wing can differ in motion, so the displayed percentage is nominal, not measured instantaneous axle loading. This is still the preliminary aero model, not a measured aero map. Visual wing angles do not move.

## SUSPENSION
Four wheel-rate sliders (N/mm); front default27.235425, rear36.593879. Front range17.235425-47.235425, rear20.593879-56.593879; steps1N/mm. Decimal offsets keep the exact r15 rates on the adjustment grid. Front/rear anti-roll bars0-15000 in500 steps, default0; experimental tuning range, not verified real hardware. Ride-height adjustment uses suspension rod length, +/-10mm about each baseline; rod-length change is not equal to actual chassis ride-height change. Check the live car height/travel values. Front rod baseline21.359331mm, rear12.180235mm.

## ALIGNMENT AND DAMPERS
Four camber sliders -4 to+1deg in0.1 steps, default0. Toe controls -10 to+10 native adjustment units, default0: these are steering-link offsets, NOT degrees of wheel toe. Check the resulting alignment readout. Slow bump800-3200 (default1800), fast bump300-1800 (default900), rebound1000-4000 (default2400), fast rebound400-2400 (default1200), in100N*s/m steps. Match left and right when testing basic balance. Native setups may allow asymmetric tuning; there is no automatic axle linking.

Start by changing aero one or two points, or one axle's spring rate one step on both sides. Save each comparison separately. R15 engine curve, upshift settings, tires, FFB, brakes, differential, CG and suspension default values are retained. Existing brake-bias/differential controls remain available.

Requires CSP0.2.11 (same as prior car) with extended physics enabled; car.ini already uses extended-1. If AERO control is absent or nonfunctional, check CSP and report it; without physics scripting the base aero remains40/60. A normal Lua app checkbox is not needed: data/script.lua is the car physics script.

Validation: Lua executed with mocked CSP calls across all21 aero settings, default, out-of-range inputs, missing setup ref and delayed ref availability. Lift sum/drag gains checked; all native control defaults lie within range and on their grids. Existing physics files remain byte-identical to r15 except setup.ini and script.lua; the original launch-limiter script is preserved with an appended aero wrapper. This does NOT prove menu rendering, native setup scaling, save/reload behavior, or in-game load; these require sim testing. No car reinstalled on the laptop.
