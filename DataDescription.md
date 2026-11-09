# Data description
Version: P1-v8-release1. Counts refer to episodes. Generate training observations locally and download the fixed Test observations from the competition Data tab.

## Files

| File or directory | Where to get it | Purpose |
|---|---|---|
| Train.csv | Zindi Data tab | Reference sample: 864 episode IDs, paths and nine labels |
| TrainMetadata.csv | Zindi Data tab | Reference training metadata for analysis and stratification |
| Test.csv | Zindi Data tab | Index of 2,160 Test episodes, with ID and relative sequence path |
| TestInputs.zip | Zindi Data tab | Test RGB-D packets for inference only |
| SampleSubmission.csv | Zindi Data tab | Exact Test ID order and nine prediction columns |
| GenerateTrain.ipynb, simulator/, TRAIN_GENERATION.json | Phase1TrainGenerator.zip | Setup check and recipe for generating training data |
| starter_baseline.py | Phase1TrainGenerator.zip | CPU baseline that trains on generated data and writes a submission |
| generated/Train.csv, generated/inputs/ and generated/annotations/ | Your simulator workspace | Generated labels and matching observations, with training-only auxiliary annotations |

Extract `TestInputs.zip` beside `Test.csv`, keeping the `TestInputs/` folder. For training, use the generator's `generated/Train.csv` with the NPZs it writes. Load NPZ files with `np.load(path, allow_pickle=False)`. See `README.md` for a baseline command.

## One inference packet

| Key | Shape | Type | Meaning |
|---|---|---|---|
| rgb | 9 x 192 x 256 x 3 | uint8 | RGB, values 0-255 |
| depth | 9 x 192 x 256 | float32 | Raw optical-axis depth in metres; zero may mean no return; far values can exceed 8 m |
| camera_to_episode | 9 x 4 x 4 | float32 | Homogeneous camera-to-episode transform |
| intrinsics | 3 x 3 | float32 | Pinhole intrinsic matrix; 80-degree horizontal field of view |
| timestamps_relative | 9 | float32 | -0.8, -0.7, ..., 0 seconds at 10 Hz |
| telemetry | 9 x 9 | float32 | Robot state, as listed below |
| angular_velocity | 9 | float32 | Pending robot yaw-rate command, radians/second |

Depth is stored without clipping. The configured 8 m normalization range is not a hard cap when native depth normalization is disabled. Positive far-field values above 8 m are retained; use an explicit mask when a method needs the generator's near-field working band. The figures saturate their colour scale at 8 m for readability.

Telemetry columns, in order: robot x, y, z in episode coordinates (metres); relative heading (radians); pending linear velocity command (m/s); reference speed (m/s); goal displacement in the current robot frame x, y, z (metres). The pending velocity is a command, not measured ground-truth speed.

The episode frame is anchored at the scenario's initial robot position; +x is its initial forward direction and +y is up. Camera poses use Habitat/OpenGL camera convention: +x right, +y up and -z forward. To back-project pixel (u,v) with depth d, use camera point `[(u-cx)*d/fx, -(v-cy)*d/fy, -d, 1]`, then multiply by camera_to_episode. Pixel row zero is the top row. Heading follows the simulator's yaw convention; a positive relative yaw gives forward ground direction `[cos(yaw), -sin(yaw)]` in episode x/z. Goal-relative z uses the ground-plane side vector `[-forward_z, 0, forward_x]`, rather than an optical camera axis.

No world map, simulator state, future seed, case ID, avatar ID, human ground truth or label appears inside inference packets. TrainMetadata.csv is separate and has no corresponding Test metadata file.

## Targets
The columns are in this exact order:

```
risk_forward_1s, risk_forward_2s, risk_forward_3s,
risk_slow_1s, risk_slow_2s, risk_slow_3s,
risk_stop_1s, risk_stop_2s, risk_stop_3s
```

Each target is the fraction of **64 independently seeded stochastic future branches** in which an event occurs before the relevant horizon. Values lie in [0,1] on a 1/64 grid. They estimate simulation risk under the organizer's latent scenario state; they are not an analytic probability or a single realised future's binary label. The three action alternatives share the same future draws to make comparisons less noisy.

At each 0.1-second simulation tick, an event is a native robot-human/prop contact OR protective clearance below 0.20 m. Human clearance is the minimum ground-plane distance from the person's root to robot footprint samples, minus 0.55 m (0.25 m robot margin + 0.30 m person margin). Static crates/carts use a box-distance envelope minus a 0.25 m robot margin. This is a benchmark definition, not a physical collision/injury guarantee. Contacts here are with the person and inserted props; generic wall contacts are not an additional target category. Native navigation constrains movement through the furnished geometry.

Events accumulate across the horizon; a previous event remains positive. Evaluation of the event trajectory ends on first goal arrival (within 0.25 m of the goal). Forward holds reference speed, slow holds 0.35 times reference speed and stop commands zero speed. The already pending linear and angular command is applied for one initial tick before the new command takes effect; future yaw is then zero. No instantaneous braking or further replanning is assumed.

Risks must therefore be nondecreasing from 1 to 3 seconds within an action. There is no required ordering between actions: stopping is not universally safe. The scorer does not project inconsistent predictions or round them to the target grid.

## Population and sampling
There are three furnished indoor buildings and three humanoid avatars. The 12 encounter families are crossing_left, crossing_right, merging, passing, following, moving_away, delayed_crossing, turning_away, sustained_crossing, late_crossing, hesitant_crossing and weaving_merge. The harder four families include repeated crossings, long hidden delays, hesitation and merge-direction changes. Props are static crates or carts; they add geometry and clutter, not object manipulation.

Family sampling weights in this order are 2,2,1,1,1,1,2,1,4,3,3,3. Train uses a base of 4 episodes per building/avatar/family cell times that weight; Test uses a base of 10. This produces 864 Train and 2,160 Test episodes. Buildings and avatar identities are shared across splits; this is episode generalisation, not unseen-building generalisation. One person is active per episode. People follow stochastic, non-reactive native motion; they do not adapt to the robot's decision.

Ten prefix behaviors provide moving, braking, waiting, intermittent, reverse and turning histories. Each accepted example supplies nine safe causal frames: no current contact/envelope event/goal arrival, final clearance over 0.30 m, remaining route over 0.70 m, at least 95% finite depth pixels in the working band (0.03, 8.001] metres in every frame, and limited black pixels. At least three frames must contain 500 visible human foreground pixels under the generator's depth-difference quality test. The generator first checks native route feasibility and prescribed start/terminal clearances using the sampled planned routes. It then selects one admissible nine-frame window from a simulated prefix, restores that cutoff state and branches 64 new future draws. Admission does not use those labelled futures or model error. Sensors are synthetic and robot poses/commands are exact. The population excludes fully invisible-human prefixes and therefore does not cover every possible robotics hazard.

Train and Test use independent seed domains and motion keys. No episode contributes frames to more than one split. Test labels, split membership and reconstruction state are organizer-only. The public starter can generate new episodes from the same published population, but it is not supplied with Test's latent state or future randomness.

## Auxiliary Train annotations
Each generated training annotation contains `human_position_episode` (9 x 3, float32; human root position in metres) and `human_mask` (9 x 192 x 256, bool). The mask is an automatically derived foreground mask from human-present vs human-removed depth (difference over 0.12 m, observed depth between 0.08 and 7.8 m), not manual pixel annotation. Static background depth is not distributed. Neither annotation is available at Test inference; a model must estimate any required human state from its permitted inputs.

## Provenance and rights
Generated using Habitat-Lab/Sim 0.3.3, the Habitat v0.3.x benchmark scene assets, Habitat Humanoids, the Habitat Spot + Arm model and YCB scene assets. See `THIRD_PARTY_NOTICES.md`, `simulator/asset_lock.json` and the upstream dataset cards. Source assets are fetched from their public repositories rather than redistributed in this package. The competition dataset licence will accompany the data when it is released.
