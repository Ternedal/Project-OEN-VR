# Avatar production source pack 001

This pack replaces the former eight-vertex torso box and SVG-only handwear with
three modeled, UV-mapped source assets:

- `CHR_TORSO_BASE_001`: tapered grounding shell, separate vest panels, broad
  shoulder straps, hem band, back plate and open collar. It deliberately has no
  arms or head because those tracking and IK decisions remain runtime-owned.
- `CHR_HAND_P1_001`: paired left/right semantic mesh objects with round amber
  wrist badges.
- `CHR_HAND_P2_001`: the same neutral glove family with square green wrist
  badges, keeping player identity readable after desaturation.

The paired left/right parts in each handwear OBJ share an origin so Unity can
split them by semantic object name without inheriting an arbitrary source-pose
offset. Units are metres and Z is up.

Regenerate with `python tools/generate_avatar_source_meshes.py`. Validate with
`python tools/validate_avatar_torso_source.py`. Unity rigging, tracking poses,
IK, networking, colliders, runtime shader adaptation, LODs, headset readability,
performance and release approval remain separate work.
