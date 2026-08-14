# Provenance — B1 environment production source pack 001

## Geometry

The five OBJ/MTL assets are original procedural authoring for PROJECT ØEN,
derived from `docs/60_B1_ENVIRONMENT_SOURCE_SPECS.md` and the corresponding SVG
references. Generator: `tools/generate_b1_environment_meshes.py`. Shared mesh
helpers come from `tools/generate_camp_source_meshes.py`. No third-party mesh is
embedded.

## Raster materials

Generated with the Codex built-in ImageGen tool on 2026-08-14 as one 2×2
diffuse atlas, then deterministically cropped by
`tools/crop_b1_environment_atlas.py`. The original atlas is retained as
`textures/MAT_B1_ENVIRONMENT_ATLAS_SOURCE_001.png`.

Final prompt:

> Use case: stylized-concept. Asset type: game environment texture atlas for a
> standalone Unity/Meta Quest VR project. A single square 2×2 atlas of four
> seamless tileable tropical-survival diffuse materials: broad matte jungle
> leaves, cool gray ravine rock, wind-combed muted ridge grass and dark soil,
> and weathered high-contrast expedition marker paint on rough canvas. Exactly
> four equal edge-to-edge quadrants; orthographic surface view; hand-painted
> stylized realism; broad mobile-VR detail; neutral flat diffuse albedo. No
> objects, text, letters, numbers, icons, logos, watermark, perspective,
> borders, baked directional light, shadows, specular highlights or tiny noise.

The environment MTLs also reuse the original A2 wood/canvas raster materials,
whose provenance is documented in
`source_art/props/a2/production/PROVENANCE.md`.

No human art approval, seamless-wrap inspection, Unity integration, headset
readability/comfort, performance or release approval is claimed here.
