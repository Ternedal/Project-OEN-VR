<#
  Fast visual-review loop for Project OEN production art.

  This is deliberately separate from Bootstrap-M0b.ps1. It does not recreate the
  Unity project, touch Packages/, configure XR, import Fusion, or build the M0b APK.
  It syncs current production-art sources/editor builders, rebuilds world prefabs,
  decals, diegetic UI prefabs, the physical-scale UI review scene/audit, then the
  Stormnatten showcase + storm pass + Quest 2 art budget audit.
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
$artEditorDst = Join-Path $ProjectPath "Assets\ProjectOEN\Editor"
if (-not (Test-Path $artSrc)) { throw "Production art mangler i repoet: $artSrc" }

Step "Synkroniserer production art"
New-Item -ItemType Directory -Force -Path $artDst | Out-Null
foreach ($folder in @("Sprites", "Meshes", "Materials", "Decals", "Docs")) {
    $srcFolder = Join-Path $artSrc $folder
    $dstFolder = Join-Path $artDst $folder
    if (-not (Test-Path $srcFolder)) { throw "Production-art mappe mangler: $srcFolder" }
    if (Test-Path $dstFolder) { Remove-Item $dstFolder -Recurse -Force }
    Copy-Item $srcFolder $dstFolder -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $artEditorDst | Out-Null
foreach ($builder in @(
    "ProductionArtPrefabBuilder.cs",
    "ProductionArtDecalBuilder.cs",
    "ProductionArtDiegeticUiBuilder.cs",
    "ProductionArtUiShowcaseBuilder.cs",
    "ProductionArtUiShowcaseAudit.cs",
    "ProductionArtShowcaseBuilder.cs",
    "ProductionArtStormAtmosphereBuilder.cs",
    "ProductionArtShowcaseAudit.cs",
    "ProductionArtReviewMenu.cs"
)) {
    Copy-Item (Join-Path $repo "src\unity\ProjectOen.Art\Editor\$builder") (Join-Path $artEditorDst $builder) -Force
}
Note "Art + world/decal/diegetic-UI/showcase builders er synkroniseret til $ProjectPath"

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

Run-UnityArtStep "Bygger puddle/shoreline ground decals" `
    "ProjectOen.Art.Editor.ProductionArtDecalBuilder.BuildAll" `
    "review-art-decals.log"

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

Run-UnityArtStep "Tilfoejer lokal stormregn" `
    "ProjectOen.Art.Editor.ProductionArtStormAtmosphereBuilder.AddStormAtmosphere" `
    "review-art-storm.log"

Run-UnityArtStep "Auditerer showcase mod Quest 2-budget" `
    "ProjectOen.Art.Editor.ProductionArtShowcaseAudit.AuditShowcase" `
    "review-art-budget.log"

Step "Resultat"
Write-Host "Production-art visual-review er bygget; ground decals, diegetic UI-prefabs og fysisk UI-audit bestod; Stormnatten-budgetauditen bestod." -ForegroundColor Green
Write-Host "World scene: Assets\ProjectOEN\ProductionArt\Scenes\StormnattenArtShowcase.unity" -ForegroundColor Green
Write-Host "UI scene: Assets\ProjectOEN\ProductionArt\Scenes\DiegeticUiArtShowcase.unity" -ForegroundColor Green
Write-Host "UI prefabs: Assets\ProjectOEN\ProductionArt\UiPrefabs" -ForegroundColor Green
Write-Host "M0b CoopGame/build settings er ikke aendret." -ForegroundColor Green

if ($OpenEditor) {
    Step "Aabner Unity visual-review"
    $args = @("-projectPath", $ProjectPath, "-executeMethod", "ProjectOen.Art.Editor.ProductionArtReviewMenu.OpenShowcase")
    Start-Process -FilePath $UnityPath -ArgumentList $args | Out-Null
    Note "Unity starter med Stormnatten-showcase som aktiv scene."
}
