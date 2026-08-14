# Provenance — A4 Camp environment production source pack 001

## Geometry

The three OBJ/MTL assets are original procedural authoring for PROJECT ØEN,
derived from `docs/61_A4_CAMP_ENVIRONMENT_SOURCE_SPEC.md` and the A4 SVG source
references. Generator: `tools/generate_a4_camp_environment_meshes.py`. Shared
mesh helpers come from the Camp and B1 environment generators. No third-party
mesh is embedded.

## Raster materials

Generated with the Codex built-in ImageGen tool on 2026-08-14 as one 2×2
diffuse atlas, then deterministically cropped by
`tools/crop_a4_camp_ground_atlas.py`. The original is retained as
`textures/MAT_A4_CAMP_GROUND_ATLAS_SOURCE_001.png`.

Final prompt:

> Use case: stylized-concept. Asset type: game environment texture atlas for a
> standalone Unity/Meta Quest VR tropical survival camp. A single square 2×2
> atlas of four seamless tileable diffuse materials: warm dry tropical beach
> sand with broad wind ripples and sparse smooth pebbles; darker wet compacted
> sand; shallow storm puddle and saturated sand; weathered driftwood and coarse
> beach debris. Exactly four equal edge-to-edge quadrants; orthographic surface
> view; hand-painted stylized realism; broad mobile-VR detail; neutral flat
> diffuse albedo. No discrete objects, footprints, text, letters, numbers,
> icons, logos, watermark, perspective, borders, baked light, cast shadows,
> specular highlights or tiny noisy grains.

The MTLs also reuse original B1 rock/marker and A2 canvas textures, documented
in their respective production provenance records.

No human art approval, seamless-wrap inspection, Unity integration, headset
readability/comfort, performance or release approval is claimed here.
