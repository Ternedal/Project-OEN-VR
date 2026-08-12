<#
  Fast visual-review loop for Project OEN production art.

  This is deliberately separate from Bootstrap-M0b.ps1. It does not recreate the
  Unity project, touch Packages/, configure XR, import Fusion, or build the M0b APK.
  It only syncs the current production-art sources/editor builders into an existing
  ProjektOenApp, rebuilds the art prefabs/showcase, adds storm rain, runs the imported-
  scene Quest 2 budget audit, and optionally launches Unity on the showcase.

  Example:
    .\Review-ProductionArt.ps1 `
      -UnityPath "C:\Program Files\Unity\Hub\Editor\6000.4.10f1\Editor\Unity.exe" `
      -OpenEditor
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
if (-not (Test-Path $ProjectPath)) {
    throw "Unity-projekt ikke fundet: $ProjectPath. Koer Bootstrap-M0b.ps1 foerst."
}

$repo = (Resolve-Path "$PSScriptRoot\..\..").Path
$ProjectPath = (Resolve-Path $ProjectPath).Path
$artSrc = Join-Path $repo "Assets\ProjectOEN\ProductionArt"
$artDst = Join-Path $ProjectPath "Assets\ProjectOEN\ProductionArt"
$artEditorDst = Join-Path $ProjectPath "Assets\ProjectOEN\Editor"

if (-not (Test-Path $artSrc)) {
    throw "Production art mangler i repoet: $artSrc"
}

Step "Synkroniserer production art"
New-Item -ItemType Directory -Force -Path $artDst | Out-Null
foreach ($folder in @("Sprites", "Meshes", "Materials", "Docs")) {
    $srcFolder = Join-Path $artSrc $folder
    $dstFolder = Join-Path $artDst $folder
    if (-not (Test-Path $srcFolder)) { throw "Production-art mappe mangler: $srcFolder" }
    if (Test-Path $dstFolder) { Remove-Item $dstFolder -Recurse -Force }
    Copy-Item $srcFolder $dstFolder -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $artEditorDst | Out-Null
foreach ($builder in @(
    "ProductionArtPrefabBuilder.cs",
    "ProductionArtShowcaseBuilder.cs",
    "ProductionArtStormAtmosphereBuilder.cs",
    "ProductionArtShowcaseAudit.cs",
    "ProductionArtReviewMenu.cs"
)) {
    Copy-Item (Join-Path $repo "src\unity\ProjectOen.Art\Editor\$builder") (Join-Path $artEditorDst $builder) -Force
}
Note "Art + editor-builders er synkroniseret til $ProjectPath"

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
    if (Test-Path $log) {
        Select-String -Path $log -Pattern "\[ProjectOEN.Art" | ForEach-Object { Note $_.Line.Trim() }
    }
}

Run-UnityArtStep "Bygger production-art prefabs" `
    "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll" `
    "review-art-prefabs.log"

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
Write-Host "Production-art visual-review er bygget og Unity-budgetauditen bestod." -ForegroundColor Green
Write-Host "Scene: Assets\ProjectOEN\ProductionArt\Scenes\StormnattenArtShowcase.unity" -ForegroundColor Green
Write-Host "M0b CoopGame/build settings er ikke aendret." -ForegroundColor Green

if ($OpenEditor) {
    Step "Aabner Unity visual-review"
    $args = @(
        "-projectPath", $ProjectPath,
        "-executeMethod", "ProjectOen.Art.Editor.ProductionArtReviewMenu.OpenShowcase"
    )
    Start-Process -FilePath $UnityPath -ArgumentList $args | Out-Null
    Note "Unity starter med Stormnatten-showcase som aktiv scene."
}
