# SRT Michigan Autocross - MATLAB Loop

An Assetto Corsa training track converted from the project's latest MATLAB autocross course. Select **SRT Michigan Autocross - MATLAB Loop**, use Practice with one car, and choose the SRT car or another installed car.

## Preserved layout

- All 137 modeled cones: 93 upright and 44 fallen pointers. Positions, roles, dimensions and pointer directions come from the r25b course; none were moved to fit the game.
- The 744.61 m original route and existing 198.67 m synthetic return, totaling 943.28 m per complete loop.
- The original timed portion is 699.87 m. AC timing gates are arranged so this portion is Sector 1; a full AC lap also includes the return. Timing crossings still require a driven test.
- White guides retain the MATLAB 4 m guide width. Cyan guides identify the synthetic return. Paint is guidance, not a course boundary.
- Flat open asphalt, with lower-grip grass outside the training pad. Pad size, surrounding grass and replay cameras are added simulation scenery, not a site survey.

Cones remain visual-only, as in the MATLAB driving scene: there are no physical cone impacts or cone penalties. Source cone locations are video-informed estimates registered to map scale, not a photogrammetric survey. The return section is synthetic and is not part of the real event course.

## Install

Back up an existing `content/tracks/srt_michigan_autocross` folder if replacing an earlier build. Drag the track ZIP into Content Manager and install it, or extract its `content` folder into the Assetto Corsa game folder. This does not replace or modify the SRT car. No CSP extension is required by this track.

There is one pit/start slot. Use Practice or solo driving; opponent AI, pit routing, race starts and hotlap scoring are not validated. The included reference AI line supports route/track initialization; it is not a recorded or optimized racing line. Use the visible guides while learning the course.

## Verification and limits

Independent binary readback checks the KN5 meshes, collision surfaces, helpers and AI file. The proper coordinate rotation is native MATLAB `[X,Y,Z]` to Assetto Corsa `[-Z,Y,X]`, in meters. Original route points round-trip exactly, and cone centers have zero coordinate change before float32 mesh serialization. The loop length agrees with the saved MATLAB closed-course validation to better than 1e-7 m. Fallen pointers use the MATLAB base-to-tip geometry, with added original white bands.

The SRT car loaded on the new track, settled at the intended start, and showed positive load on all four tires with a running engine. Game logs confirm the 4,364-point reference spline loaded. No driven lap, visual cockpit inspection, lap/sector trigger crossing, AI driving, or full-route surface traversal has been performed. Those remain driver checks. The original MATLAB source and car configuration were preserved.

## Rebuild

Python with NumPy and Pillow is required. Run `scripts/build_track.py`, then `scripts/validate_track.py`. The default project root is the folder above `scripts`; it can be overridden with `SRT_TRACK_PROJECT`. All necessary layout inputs are preserved in `reference-copies`; MATLAB is not required for a rebuild. Output is `release-r01/content/tracks/srt_michigan_autocross`.

The builder implements the existing MATLAB return-connector equations directly and checks against its saved 943.27862342756634 m result. It creates original meshes and textures; no track or car meshes from another mod are included. The course overview is a generated map, not an in-game screenshot.

## Sources

Project inputs: `course-r25b.json`, `srt27_human_course_r26.m`, `srt27_closed_course_connector_r26.m`, `closed-course-validation.json`, and the original `srt27_cone_meshes_r26.m` implementation. The latter is preserved with the build evidence.

Track logical-node and collision naming: https://site.hagn.io/assettocorsa/modding/tracks/track-kn5. AI binary layout: Content Manager's own AcTools source at https://github.com/gro-ove/actools/tree/master/AcTools/AiFile. Surface, camera and groove schemas were checked against the locally installed Kunos track files; none of their meshes/textures were copied. Shared-memory heading layout: https://github.com/ac-custom-shaders-patch/acc-extension-apps/blob/master/apps/python/AccExtHelper/sim_info.py.
