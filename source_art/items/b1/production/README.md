# B1 shared world-item production source pack 001

This pack replaces the five SVG-only B1 resource silhouettes with modeled,
UV-mapped source geometry intended for shared co-op handling.

## Contents

- `ITM_WOOD_BUNDLE_001`: five individually readable logs, held by two broad bindings.
- `ITM_FIBER_BUNDLE_001`: a layered braided mass with a distinct loose strand and tie.
- `ITM_HERB_BUNDLE_001`: five stems, ten broad leaves, a readable tie and simple label plate.
- `ITM_FOOD_PARCEL_001`: one sealed parcel silhouette with folded top, cross-straps and seal.
- `ITM_GENERAL_SUPPLIES_001`: one shared kit with large handle, pockets and two bulk categories.

All geometry is original procedural authoring. OBJ object names expose large
semantic parts for downstream collider, grip and state setup. Units are metres;
Y is up. The pack intentionally reuses the A2 mobile-VR diffuse textures rather
than introducing redundant material files.

Unity import, prefabs, grip poses, colliders, networking, headset readability,
performance and release approval remain separate runtime work. Regenerate the
pack with `python tools/generate_b1_source_meshes.py` and validate it with
`python tools/validate_b1_source_meshes.py`.
