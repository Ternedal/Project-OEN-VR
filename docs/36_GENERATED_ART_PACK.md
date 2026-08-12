# Project ØEN — generated Unity art pack

This branch adds a deterministic runtime/preview graphics pack driven by the Project ØEN asset master list.

## What is generated

- 148 separate transparent PNG sprites, one for every asset-master entry.
- Stable paths under `Assets/ProjectOEN/GeneratedArtRuntime256/`.
- Unity `.meta` files with deterministic GUIDs and Sprite import settings.
- CSV/JSON manifest under `Assets/ProjectOEN/GeneratedArtRuntime256Docs/`.
- 256×256 power-of-two runtime/preview tier, suitable for Quest-oriented UI/prototyping.

## Important scope note

World objects such as shelter pieces, crates, tarp, rocks, radio and signal structures should ultimately be implemented as optimized 3D prefabs. The generated PNGs are runtime UI/sprite/reference assets and stable placeholders; they are intentionally replaceable one-by-one without changing references.

## Regeneration

Run:

```bash
python -m pip install Pillow==11.3.0
python tools/generated_art/generate_runtime_sprites.py
```

The branch workflow regenerates and commits the PNGs automatically whenever the asset master or generator changes.
