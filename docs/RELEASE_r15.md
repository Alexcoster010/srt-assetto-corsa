# SRT r15 â€” torque curve and upshift feel test

Built November 7, 2026 from checksum-verified public r14.

- Peak torque moves 13250 -> 12250 RPM, keeping peak36.218352Nm.
- Smooth low/mid-RPM increase, compensated with greater upper-end drop-off. Average torque is preserved as the trapezoidal area under the piecewise-linear torque-vs-RPM LUT divided by the RPM span, not the unweighted average of unequal-spaced samples. Full0-16000rpm and operating1400-16000rpm integrals preserved because0-2500rpm remains unchanged. This does not preserve power, shift-optimal RPM, or acceleration time.
- Upshift duration80 ->100ms, automatic torque cut80 ->100ms; autoclutch reaches disengaged at10ms, starts engagement100ms, finishes180ms. AI cutoff0.08 ->0.10s. USE_ON_CHANGES=1 retained. Synthetic clutch profile is a shift-feel approximation, not a claim of the real car's clutch actuation. No measured torque-return trace is available.
- Engine inertia0.03, clutch capacity100Nm, downshift timing/autoblip, rev limiter16000, auto-shift threshold14500rpm, differential and all handling settings remain unchanged. Retains r14 rear springs30% softer and prior nominal9in CG.

Install: back up your existing srt27_prototype folder, extract the full ZIP into the Assetto Corsa root and overwrite. Restart session; Content Manager should show0.15.0. Requires CSP0.2.11. The small patch ZIP is for r14 only. Reinstall r14 for rollback.

Validation: exact serialized LUT integration, peak location, positivity, profile ordering, changed-file allowlist and full package hashes checked. No runtime/driver test performed. Test moderate then full-throttle upshifts across gears for kick, RPM flare/bog, and clutch slip. Report shift RPM and gear pair. The changed torque curve can change the best shift point;14500rpm automatic threshold is retained pending testing. Do not treat this curve as measured dyno data.

Local primary parameter reference: installed Kunos SDK dev/content/cars/formula_k/data/drivetrain.ini, gearbox and autoclutch comments. Baseline and result hashes, torque samples and plots accompany the source revision.
