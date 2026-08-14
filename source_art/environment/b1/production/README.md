# B1 environment production source pack 001

This pack converts the jungle, ravine and ridge readability references into
modeled, UV-mapped source geometry while preserving runtime freedom.

## Contents

- `ENV_JUNGLE_PATH_001`: 10.5 m sample route with four readable primary
  segments, a short visibly reconnecting detour, twelve two-mass trees, camp
  return/ridge exit arches and a bounded resource pocket.
- `ENV_RAVINE_001`: materially distinct belayer and recovery stations, four
  bounded progression points, route-order markers and a separate fail-forward
  return path.
- `ENV_RIDGE_001`: arrival/return route, central safe overlook, comfort edge
  barrier, wind cue and signal-direction landmark.
- `PRP_RAVINE_ANCHOR_001`: large rock-mounted ring with two readable rope exits.
- `PRP_RAVINE_GUIDE_MARKERS_001`: circle, square and diamond route markers with
  separate center dots; shape and order do not rely on color.
- Four cropped environment textures plus their retained 1254 px source atlas.

The environment meshes are source layouts and modular semantic parts, not a
mandated final navmesh. Unity may simplify, rearrange or split them while
preserving the readability and comfort contract. Units are metres; Y is up.

Regenerate geometry with `python tools/generate_b1_environment_meshes.py`.
Regenerate texture crops with `python tools/crop_b1_environment_atlas.py`.
Validate with `python tools/validate_b1_environment_meshes.py`.

Unity scene integration, navigation, interaction reach, colliders, occlusion,
LOD, shader/tiling adjustment, headset comfort/readability, performance and
release approval remain separate runtime/device work.
