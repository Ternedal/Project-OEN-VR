# A3 storm VFX production source pack 001

This directory contains seven deterministic 512×512 PNG sources derived from
the project-original A3 SVG direction:

- `VFX_RAIN_001.png`: four directional streak cells.
- `VFX_WIND_DEBRIS_001.png`: leaf, fiber strip, twig and sparse fleck cells.
- `VFX_FIRE_EMBERS_001.png`: four larger readable ember/glow cells.
- `VFX_FIRE_SMOKE_001.png`: four smoke cells; lower row is denser wet/smothered intent.
- `VFX_IMPACT_001.png`: four short dust/fiber punctuation cells.
- `VFX_ROPE_STRAIN_001.png`: four restrained fiber-accent cells; never primary tension feedback.
- `VFX_WETNESS_REFERENCE_001.png`: opaque stylized wetness/mask reference.

Cell geometry and alpha intent are recorded in
`VFX_SPRITE_LAYOUT.source.json`. Regenerate with
`python tools/generate_a3_vfx_sprites.py`; validate dimensions, RGBA encoding,
metadata and byte reproducibility with `python tools/validate_a3_vfx_sprites.py`.

Unity particle systems, blending, shaders, timing, density, phase binding,
pooling, overdraw/performance tuning and headset readability remain
runtime/device work. These PNGs are production source sprites, not a claim that
storm VFX are Unity-integrated or release-approved.
