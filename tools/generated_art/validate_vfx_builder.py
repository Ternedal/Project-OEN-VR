#!/usr/bin/env python3
"""Static contract for Project ØEN Unity VFX materials/prefabs."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILDER=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"/"ProductionArtVfxBuilder.cs"
BOOT=ROOT/"prototype"/"m0b-bootstrap"/"Bootstrap-M0b.ps1"
REVIEW=ROOT/"prototype"/"m0b-bootstrap"/"Review-ProductionArt.ps1"

REQUIRED=(
 'SpriteRoot = "Assets/ProductionArt/Sprites/vfx_support_graphics"',
 'MaterialRoot = "Assets/ProductionArt/VfxMaterials"',
 'PrefabRoot = "Assets/ProductionArt/VfxPrefabs"',
 'Universal Render Pipeline/Particles/Unlit',
 'Particles/Standard Unlit',
 'Unlit/Transparent',
 'new VfxSpec("fx-001_", "small", "smoke")',
 'new VfxSpec("fx-001_", "medium", "smoke")',
 'new VfxSpec("fx-002_", "small", "ember", true)',
 'new VfxSpec("fx-003_", "single", "ash")',
 'new VfxSpec("fx-004_", "medium", "rain_splash")',
 'new VfxSpec("fx-005_", "single", "wet_sheen")',
 'new VfxSpec("fx-006_", "near", "lightning", true)',
 'new VfxSpec("fx-007_", "fire", "glow", true)',
 'new VfxSpec("fx-008_", "medium", "objective_pulse", true)',
 'sheet.numTilesX = 4', 'sheet.numTilesY = 4', 'sheet.cycleCount = 1',
 'main.playOnAwake = false', 'renderer.shadowCastingMode = ShadowCastingMode.Off',
 'renderer.receiveShadows = false', 'material.renderQueue = (int)RenderQueue.Transparent',
 'spec.Kind == "wet_sheen"',
)
FORBIDDEN=('AddComponent<Light>','AddComponent<BoxCollider>','AddComponent<MeshCollider>',
           'ParticleSystemCollision','BuildPipeline.BuildPlayer','EditorBuildSettings.scenes')


def main():
    errors=[]
    if not BUILDER.exists(): errors.append(f"Missing VFX builder: {BUILDER.relative_to(ROOT)}"); text=""
    else:
        text=BUILDER.read_text(encoding="utf-8")
        for t in REQUIRED:
            if t not in text: errors.append(f"VFX builder missing contract token: {t}")
        for t in FORBIDDEN:
            if t in text: errors.append(f"VFX builder must not contain expensive/unsafe feature: {t}")
        if text.count("new VfxSpec(")!=14: errors.append(f"Expected exactly 14 VFX state specs, found {text.count('new VfxSpec(')}")
        if "main.maxParticles = MaxParticles" not in text: errors.append("VFX builder must use bounded per-effect maxParticles")

    for path,label,logname in ((BOOT,"bootstrap","production-art-vfx.log"),(REVIEW,"review","review-art-vfx.log")):
        if not path.exists(): errors.append(f"Missing {label}: {path.relative_to(ROOT)}"); continue
        s=path.read_text(encoding="utf-8")
        for t in ("ProductionArtVfxBuilder.cs","ProjectOen.Art.Editor.ProductionArtVfxBuilder.BuildAll",logname):
            if t not in s: errors.append(f"{label} missing VFX integration token: {t}")
        world=s.find("ProductionArtPrefabBuilder.BuildAll")
        vfx=s.find("ProductionArtVfxBuilder.BuildAll")
        ui=s.find("ProductionArtDiegeticUiBuilder.BuildAll")
        if min(world,vfx,ui)<0 or not (world < vfx < ui): errors.append(f"{label} must build world prefabs -> VFX -> diegetic UI")

    print("Project ØEN Unity VFX integration QA")
    print("  canonical VFX states : 14")
    print("  smoke flipbooks      : 4x4 texture-sheet animation")
    print("  realtime lights      : 0")
    print("  colliders/collision  : 0")
    print("  particle counts      : bounded per effect")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: Quest-conscious VFX material/prefab integration contract is intact.")
    return 0

if __name__=="__main__": sys.exit(main())
