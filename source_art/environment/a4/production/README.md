# A4 Camp environment production source pack 001

This pack converts the Camp relationship, ground and storm-state references
into importable, UV-mapped source geometry.

## Contents

- `ENV_CAMP_GROUND_001`: 12 × 10.5 m gently varied base ground, six calm
  interaction zones, explicit primary routes and a sea-facing wet band.
- `ENV_BEACH_CAMP_001`: semantic sockets for all seven landmarks, with the
  fire at the central sightline anchor, the plan-table socket connected to the
  physical camp, a sea-facing signal landmark, jungle exit gate and restrained
  clutter only at the edges.
- `ENV_STORM_CAMP_001`: additive wet-ground/puddle/debris/canvas state geometry
  that preserves fire and signal approach readability under storm pressure.
- Four cropped Camp-ground textures plus their retained 1254 px source atlas.

The landmark sockets intentionally do not duplicate the detailed A2 prop pack.
They define assembly positions and readable relationships; Unity should replace
or parent them with the corresponding production props. Units are metres; Y is
up. Exact runtime scale and layout remain tunable after device evidence.

Regenerate geometry with `python tools/generate_a4_camp_environment_meshes.py`.
Regenerate crops with `python tools/crop_a4_camp_ground_atlas.py`. Validate with
`python tools/validate_a4_camp_environment_meshes.py`.

Unity assembly, navigation, colliders, lighting, shader/tiling adjustment,
storm VFX, occlusion, LOD, headset comfort/readability, performance and release
approval remain separate runtime/device work.
