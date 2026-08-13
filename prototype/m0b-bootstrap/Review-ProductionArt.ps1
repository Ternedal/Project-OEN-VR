<#
  Fast visual-review loop for Project OEN production art.

  This is deliberately separate from Bootstrap-M0b.ps1. It does not recreate the
  Unity project, touch Packages/, configure XR, import Fusion, or build the M0b APK.
  It syncs production art + lightweight runtime state controllers, rebuilds world
  prefabs, canonical damaged/wet state appearance, dry/mid/storm material calibration,
  state catalogs, decals, VFX and UI, runs isolated material/VFX/physical-UI audits,
  then the Stormnatten showcase with rain, wetness, bounded motion FX,
  renderer-culled wind-responsive dressing and the Quest 2 art audit.
#>

param(
    [Parameter(Mandatory = $true)][string]$UnityPath,
    [string]$ProjectPath = "$PSScriptRoot\..\..\..\ProjektOenApp",
    [switch]$OpenEditor
)

$ErrorActionPreference = "Stop"
function Step($m) { Write-Host "`n== $m ==" -ForegroundColor Cyan }
function Note($m) { Write-Host "   $m" -ForegroundColor DarkGray }

if (-not (Test-Path $UnityPath)) { throw "Unity ikke fundet: $UnityPath" }
if (-not (Test-Path $ProjectPath)) { throw "Unity-projekt ikke fundet: $ProjectPath. Koer Bootstrap-M0b.ps1 foerst." }

$repo = (Resolve-Path "$PSScriptRoot\..\..").Path
$ProjectPath = (Resolve-Path $ProjectPath).Path
$artSrc = Join-Path $repo "Assets\ProjectOEN\ProductionArt"
$artDst = Join-Path $ProjectPath "Assets\ProjectOEN\ProductionArt"
$artRuntimeDst = Join-Path $ProjectPath "Assets\ProjectOEN\ArtRuntime"
$artEditorDst = Join-Path $ProjectPath "Assets\ProjectOEN\Editor"
if (-not (Test-Path $artSrc)) { throw "Production art mangler i repoet: $artSrc" }

Step "Synkroniserer production art"
New-Item -ItemType Directory -Force -Path $artDst | Out-Null
foreach ($folder in @("Sprites", "Meshes", "Materials", "Decals", "Docs")) {
    $srcFolder = Join-Path $artSrc $folder
    $dstFolder = Join-Path $ProjectPath "Assets\ProjectOEN\ProductionArt\$folder"
    if (-not (Test-Path $srcFolder)) { throw "Production-art mappe mangler: $srcFolder" }
    if (Test-Path $dstFolder) { Remove-Item $dstFolder -Recurse -Force }
    Copy-Item $srcFolder $dstFolder -Recurse -Force
}

Step "Synkroniserer production-art runtime state controllers"
New-Item -ItemType Directory -Force -Path $artRuntimeDst | Out-Null
Copy-Item (Join-Path $repo "src\unity\ProjectOen.Art\Runtime\*.cs") $artRuntimeDst -Force

New-Item -ItemType Directory -Force -Path $artEditorDst | Out-Null
foreach ($builder in @(
    "ProductionArtPrefabBuilder.cs",
    "ProductionArtStateAppearanceBuilder.cs",
    "ProductionArtStateAppearanceAudit.cs",
    "ProductionArtMaterialCalibrationBuilder.cs",
    "ProductionArtMaterialCalibrationAudit.cs",
    "ProductionArtStateCatalogBuilder.cs",
    "ProductionArtDecalBuilder.cs",
    "ProductionArtVfxBuilder.cs",
    "ProductionArtVfxShowcaseBuilder.cs",
    "ProductionArtVfxShowcaseAudit.cs",
    "ProductionArtDiegeticUiBuilder.cs",
    "ProductionArtUiShowcaseBuilder.cs",
    "ProductionArtUiShowcaseAudit.cs",
    "ProductionArtShowcaseBuilder.cs",
    "ProductionArtStormAtmosphereBuilder.cs",
    "ProductionArtStormFxBuilder.cs",
    "ProductionArtWindResponseBuilder.cs",
    "ProductionArtShowcaseAudit.cs",
    "ProductionArtReviewMenu.cs"
)) {
    Copy-Item (Join-Path $repo "src\unity\ProjectOen.Art\Editor\$builder") (Join-Path $artEditorDst $builder) -Force
}
Note "Art + runtime state controllers + state appearance + material/world/state/decal/VFX/UI/showcase builders er synkroniseret til $ProjectPath"

function Run-UnityArtStep([string]$Label, [string]$Method, [string]$LogName) {
    Step $Label
    $log = Join-Path $PSScriptRoot $LogName
    & $UnityPath -batchmode -quit -nographics `
        -projectPath $ProjectPath `
        -buildTarget Android `
        -executeMethod $Method `
        -logFile $log
    $exit = $LASTEXITCODE
    if ($exit -ne 0) {
        Write-Host "`n$Label fejlede (Unity exit $exit)." -ForegroundColor Red
        if (Test-Path $log) {
            Select-String -Path $log -Pattern "\[ProjectOEN.Art|error CS|Exception:" | Select-Object -First 50 | ForEach-Object {
                Write-Host "   $($_.Line.Trim())" -ForegroundColor Red
            }
        }
        exit 1
    }
    if (Test-Path $log) { Select-String -Path $log -Pattern "\[ProjectOEN.Art" | ForEach-Object { Note $_.Line.Trim() } }
}

Run-UnityArtStep "Bygger production-art prefabs" `
    "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll" `
    "review-art-prefabs.log"

Run-UnityArtStep "Profilerer canonical damaged/wet states" `
    "ProjectOen.Art.Editor.ProductionArtStateAppearanceBuilder.BuildAll" `
    "review-art-state-appearance.log"

Run-UnityArtStep "Auditerer state-specifik storm appearance" `
    "ProjectOen.Art.Editor.ProductionArtStateAppearanceAudit.AuditAll" `
    "review-art-state-appearance-audit.log"

Run-UnityArtStep "Bygger dry/mid/storm materialekalibrering" `
    "ProjectOen.Art.Editor.ProductionArtMaterialCalibrationBuilder.BuildShowcase" `
    "review-art-material-calibration.log"

Run-UnityArtStep "Auditerer materialekalibrering og scoped vaadhed" `
    "ProjectOen.Art.Editor.ProductionArtMaterialCalibrationAudit.AuditShowcase" `
    "review-art-material-calibration-audit.log"

Run-UnityArtStep "Bygger runtime art state catalogs" `
    "ProjectOen.Art.Editor.ProductionArtStateCatalogBuilder.BuildAll" `
    "review-art-state-catalog.log"

Run-UnityArtStep "Bygger puddle/shoreline ground decals" `
    "ProjectOen.Art.Editor.ProductionArtDecalBuilder.BuildAll" `
    "review-art-decals.log"

Run-UnityArtStep "Bygger Quest-venlige production VFX" `
    "ProjectOen.Art.Editor.ProductionArtVfxBuilder.BuildAll" `
    "review-art-vfx.log"

Run-UnityArtStep "Bygger isoleret VFX review-scene" `
    "ProjectOen.Art.Editor.ProductionArtVfxShowcaseBuilder.BuildShowcase" `
    "review-art-vfx-showcase.log"

Run-UnityArtStep "Auditerer isoleret VFX review-scene" `
    "ProjectOen.Art.Editor.ProductionArtVfxShowcaseAudit.AuditShowcase" `
    "review-art-vfx-audit.log"

Run-UnityArtStep "Bygger diegetiske VR UI-prefabs" `
    "ProjectOen.Art.Editor.ProductionArtDiegeticUiBuilder.BuildAll" `
    "review-art-diegetic-ui.log"

Run-UnityArtStep "Bygger fysisk diegetic-UI review-scene" `
    "ProjectOen.Art.Editor.ProductionArtUiShowcaseBuilder.BuildShowcase" `
    "review-art-ui-showcase.log"

Run-UnityArtStep "Auditerer diegetic UI i fysisk VR-skala" `
    "ProjectOen.Art.Editor.ProductionArtUiShowcaseAudit.AuditShowcase" `
    "review-art-ui-audit.log"

Run-UnityArtStep "Bygger Stormnatten showcase" `
    "ProjectOen.Art.Editor.ProductionArtShowcaseBuilder.BuildShowcase" `
    "review-art-showcase.log"

Run-UnityArtStep "Tilfoejer lokal stormregn og vaade overflader" `
    "ProjectOen.Art.Editor.ProductionArtStormAtmosphereBuilder.AddStormAtmosphere" `
    "review-art-storm.log"

Run-UnityArtStep "Tilfoejer vind, regnsplash og fjernt lyn" `
    "ProjectOen.Art.Editor.ProductionArtStormFxBuilder.AddStormMotionFx" `
    "review-art-storm-motion.log"

Run-UnityArtStep "Tilfoejer vindrespons til dug, reb og vegetation" `
    "ProjectOen.Art.Editor.ProductionArtWindResponseBuilder.AddWindResponse" `
    "review-art-wind-response.log"

Run-UnityArtStep "Auditerer showcase mod Quest 2-budget" `
    "ProjectOen.Art.Editor.ProductionArtShowcaseAudit.AuditShowcase" `
    "review-art-budget.log"

Step "Resultat"
Write-Host "Production-art review er bygget; canonical damaged/wet states har state-specifik appearance; material/world assets, runtime state catalogs, decals, VFX og UI er wired; dry/mid/storm materialekalibrering samt state/material/VFX/UI/Stormnatten audits bestod; Stormnatten har regn, vaadhed, vind/splash/lyn og vindrespons paa dug/reb/vegetation." -ForegroundColor Green
Write-Host "State catalogs: Assets\ProjectOEN\ProductionArt\StateSets" -ForegroundColor Green
Write-Host "Material scene: Assets\ProjectOEN\ProductionArt\Scenes\MaterialCalibrationShowcase.unity" -ForegroundColor Green
Write-Host "VFX scene: Assets\ProjectOEN\ProductionArt\Scenes\ProductionVfxShowcase.unity" -ForegroundColor Green
Write-Host "UI scene: Assets\ProjectOEN\ProductionArt\Scenes\DiegeticUiArtShowcase.unity" -ForegroundColor Green
Write-Host "World scene: Assets\ProjectOEN\ProductionArt\Scenes\StormnattenArtShowcase.unity" -ForegroundColor Green
Write-Host "VFX prefabs: Assets\ProjectOEN\ProductionArt\VfxPrefabs" -ForegroundColor Green
Write-Host "UI prefabs: Assets\ProjectOEN\ProductionArt\UiPrefabs" -ForegroundColor Green
Write-Host "M0b CoopGame/build settings er ikke aendret." -ForegroundColor Green

if ($OpenEditor) {
    Step "Aabner Unity visual-review"
    $args = @("-projectPath", $ProjectPath, "-executeMethod", "ProjectOen.Art.Editor.ProductionArtReviewMenu.OpenShowcase")
    Start-Process -FilePath $UnityPath -ArgumentList $args | Out-Null
    Note "Unity starter med Stormnatten-showcase som aktiv scene."
}
