# A2 Camp production source pack 001

This is the first actual modeled source pack for the Camp scene. It replaces
the previous brief-only status for the central Priority A prop set.

## Contents

- `PRP_HEAVY_CRATE_001`: 1.02 m broad two-person crate, closed lid, broad opposed handles.
- `PRP_PLAN_TABLE_001`: 1.20 m shared surface, five card meshes and four effort markers.
- `PRP_SIGNAL_FRAME_001`: 2.05 m landmark with reachable 1.15 m crossbar and state-ready named parts.
- `PRP_FIREPIT_001`: 0.84 m stone ring, charred crossed logs and separate ember bed.
- `PRP_SHELTER_BEAM_001`: intact and silhouette-broken stressed beam components.
- `PRP_SHELTER_ROPE_001`: chunky 34 cm coil, readable loose end and oversized binding loops.
- `PRP_SHELTER_TARP_001_*`: taut, wet-sag and silhouette-torn state meshes.
- `PRP_SHELTER_FRAME_001`: complete A-frame, ridge/side/cross braces and large repair nodes.
- `ENV_WRECKAGE_001`: asymmetric 3.3 m landmark with broken hull crescent, ribs and tilted mast.
- `PRP_RADIO_001`: diegetic radio with speaker, oversized dials, state display, keyed socket and antenna.
- `PRP_SUPPLY_CRATE_001`: compact shared-resource crate with broad handles and readable latch.
- `PRP_WIND_SHIELD_001`: curved 0.5 m one-hand shield with obvious protected side.
- Four 1024 px material textures plus retained 2048 px generation atlas.

OBJ object names intentionally expose parts for downstream collider, material,
and state setup. Units are metres; Y is up. The meshes are source handoffs.
Unity import, prefab/state wiring, shaders, colliders, LODs and device approval
remain separate work and must not be inferred from this pack.

Regenerate all geometry with `tools/generate_camp_source_meshes.py`.
