# r07.1 driver tuning

Driver feedback: r07 engine inertia is much too high and brakes need substantially more power.

- Engine inertia: 0.12 -> 0.06 kg m2 (halved).
- Maximum brake torque: 571 -> 1142 Nm (doubled).
- Default front bias remains 75%; gearing, power curve and engine braking are unchanged.

These are deliberate driver-test adjustments, not measured real-car values. Stronger brakes reach lockup with less pedal input. Exit the current driving session and launch a fresh session to load the new physics; an in-session restart may retain the old data.

The prior r07 release remains available for rollback. Driving validation of this adjustment is pending. The older DRIVER_FEEDBACK.md describes the r07 baseline; this note supersedes its inertia and maximum-brake-torque values.
