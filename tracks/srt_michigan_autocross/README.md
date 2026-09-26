# SRT MATLAB Autocross v0.2 - event-only timing

Separate native point-to-point start and finish gates now use the original MATLAB timing positions (14.997459 m and 714.868087 m along the source route). Timed distance: 699.870627 m. The physical return loop remains driveable but is outside the timed event. Removed the return-loop sector gate. Added a checkered stripe whose leading edge is at the finish plane.

All 137 cone positions, the original route, return geometry, surfaces and vehicle physics are preserved. This remains an estimated, flat training reconstruction, not a surveyed course. Cones are visual only.

Independent KN5 checks confirm the gates match source positions, no return timing gates remain, and all cones are unchanged. An actual driven start/finish crossing is still pending. Exit and relaunch the driving session to load the update. Single-car practice recommended.

Back up the existing srt_michigan_autocross track before installing this ZIP through Content Manager or merging its content folder. Same track ID as v0.1. Restore the previous track folder for rollback. No car files included.

[Download v0.2.0](https://github.com/Alexcoster010/srt-assetto-corsa/releases/tag/autocross-v0.2.0). Rebuild with Python, NumPy and Pillow: run scripts/build_track.py then scripts/validate_track.py from this track source.
