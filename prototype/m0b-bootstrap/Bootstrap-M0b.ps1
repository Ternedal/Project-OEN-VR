<#
  M0b Fase 1 - opret det rigtige Projekt Oeen Unity-projekt (Photon-uafhaengigt).

  Bygger paa det, M0a beviste: ASCII-manifest (ingen BOM), direkte XR-API, Configure
  i sin egen Unity-session. Efter denne koerer: projektet findes, pakkerne er laast,
  HELE Core-laget kompilerer som en Unity-assembly, OpenXR er sat op for Android,
  og den genererede Project OEN production-art pakke er installeret i Unity-projektet.

  Production-art-delen bygger Unity-prefabs, en separat Stormnatten art-showcase-scene
  og en billig lokal stormregn-pass. Showcase-scenen er IKKE M0b's CoopGame
  performance/netvaerksgate.

  Fusion/netvaerk (src/unity) kommer i Fase 2 EFTER Photon-SDK'en er importeret -
  ellers kan projektet ikke kompilere. Se RUNBOOK.md.

  Anders koerer:
    .\Bootstrap-M0b.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe"

  UNVERIFIED-IN-SANDBOX: scriptet er ikke koert her (ingen Unity i skrivemiljoeet), men
  alle filkopier og generated-art CI valideres i repoets GitHub Actions.
#>

param(
    [Parameter(Mandatory = $true)][string]$UnityPath,
    [string]$ProjectPath = "$PSScriptRoot\..\..\..\ProjektOenApp"
)

$ErrorActionPreference = "Stop"
function Step($m) { Write-Host "`n== $m ==" -ForegroundColor Cyan }
function Note($m) { Write-Host "   $m" -ForegroundColor DarkGray }

if (-not (Test-Path $UnityPath)) { throw "Unity ikke fundet: $UnityPath" }
$repo = (Resolve-Path "$PSScriptRoot\..\..").Path
Note "repo: $repo"

# --- 1. Projekt ---
Step "Opretter projekt"
if (Test-Path $ProjectPath) {
    Note "findes allerede: $ProjectPath (genbruges)"
} else {
    & $UnityPath -batchmode -quit -nographics -createProject $ProjectPath -logFile - | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Unity kunne ikke oprette projektet (exit $LASTEXITCODE)" }
}
$ProjectPath = (Resolve-Path $ProjectPath).Path

# --- 2. Pakker (ASCII, ingen BOM - M0a-lektien: Unity afviser BOM i manifest.json) ---
Step "Skriver pakkeliste"
$manifestSrc = Join-Path $PSScriptRoot "templates\manifest.json"
$manifestDst = Join-Path $ProjectPath "Packages\manifest.json"
[System.IO.File]::WriteAllText($manifestDst, [System.IO.File]::ReadAllText($manifestSrc), (New-Object System.Text.ASCIIEncoding))
Note "skrevet: $manifestDst (OpenXR + XRI + Input System)"

# --- 3. Core-laget ind som Unity-assembly ---
Step "Kopierer Core-laget + asmdef"
$coreDst = Join-Path $ProjectPath "Assets\ProjectOen\Core"
New-Item -ItemType Directory -Force -Path $coreDst | Out-Null
Copy-Item "$repo\src\ProjectOen.Core\*" $coreDst -Recurse -Force
# -Exclude paa Copy-Item -Recurse ekskluderer ikke mapper paalideligt; repoet har en
# committet bin\ProjectOen.Core.dll. Fjern build-artefakter EFTER kopiering, ellers ser
# Unity baade en precompiled DLL og .cs-filerne -> dublette typer -> compile-fejl.
Get-ChildItem $coreDst -Recurse -Directory | Where-Object { $_.Name -in @("bin","obj") } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $coreDst -Recurse -File | Where-Object { $_.Extension -in @(".csproj",".dll",".pdb") } | Remove-Item -Force -ErrorAction SilentlyContinue
Copy-Item "$PSScriptRoot\templates\ProjectOen.Core.asmdef" (Join-Path $coreDst "ProjectOen.Core.asmdef") -Force
Note "Core -> Assets\ProjectOen\Core (kompilerer uden Unity/Fusion-referencer)"

# --- 4. Production art ind i det RIGTIGE Unity-projekt ---
Step "Installerer Project OEN production art"
$artSrc = Join-Path $repo "Assets\ProjectOEN\ProductionArt"
if (-not (Test-Path $artSrc)) {
    throw "Production art mangler i repoet: $artSrc. Koer generated-art workflowet foerst."
}
$artDst = Join-Path $ProjectPath "Assets\ProjectOEN\ProductionArt"
New-Item -ItemType Directory -Force -Path $artDst | Out-Null

# Kun generatorens source-of-truth mapper spejles. Prefabs/scenes bevares indtil de
# genbygges i Unity-trinnene nedenfor, saa reruns ikke efterlader projektet uden dem ved fejl.
foreach ($folder in @("Sprites", "Meshes", "Materials", "Docs")) {
    $srcFolder = Join-Path $artSrc $folder
    $dstFolder = Join-Path $artDst $folder
    if (Test-Path $dstFolder) { Remove-Item $dstFolder -Recurse -Force }
    Copy-Item $srcFolder $dstFolder -Recurse -Force
}

$artEditorDst = Join-Path $ProjectPath "Assets\ProjectOEN\Editor"
New-Item -ItemType Directory -Force -Path $artEditorDst | Out-Null
Copy-Item "$repo\src\unity\ProjectOen.Art\Editor\ProductionArtPrefabBuilder.cs" (Join-Path $artEditorDst "ProductionArtPrefabBuilder.cs") -Force
Copy-Item "$repo\src\unity\ProjectOen.Art\Editor\ProductionArtShowcaseBuilder.cs" (Join-Path $artEditorDst "ProductionArtShowcaseBuilder.cs") -Force
Copy-Item "$repo\src\unity\ProjectOen.Art\Editor\ProductionArtStormAtmosphereBuilder.cs" (Join-Path $artEditorDst "ProductionArtStormAtmosphereBuilder.cs") -Force
Note "ProductionArt -> Assets\ProjectOEN\ProductionArt (sprites, meshes, materials, docs)"
Note "Prefab + showcase + storm-atmosphere builders -> Assets\ProjectOEN\Editor"

# --- 5. XR-configure-editor ---
Step "Kopierer XR-config editor"
$editorDst = Join-Path $ProjectPath "Assets\Editor"
New-Item -ItemType Directory -Force -Path $editorDst | Out-Null
Copy-Item "$PSScriptRoot\Editor\M0bConfigure.cs" (Join-Path $editorDst "M0bConfigure.cs") -Force

# --- 6. Unity: konfigurer i egen session (importerer pakker + production art foerst) ---
Step "Koerer Unity (M0bConfigure.Configure)"
Note "Foerste koersel importerer OpenXR + XRI + production art og kan tage flere minutter."
$log = Join-Path $PSScriptRoot "m0b-configure.log"
& $UnityPath -batchmode -quit -nographics `
    -projectPath $ProjectPath `
    -buildTarget Android `
    -executeMethod M0bConfigure.Configure `
    -logFile $log
$exit = $LASTEXITCODE

if ($exit -ne 0) {
    Step "Resultat"
    if (Test-Path $log) {
        Select-String -Path $log -Pattern "\[M0B-SETUP\]" | ForEach-Object { Note $_.Line.Trim() }
        $errs = Select-String -Path $log -Pattern "error CS|Exception:" | Select-Object -First 15
        if ($errs) { Write-Host "`nFejl fra Unity:" -ForegroundColor Red; $errs | ForEach-Object { Write-Host "   $($_.Line.Trim())" -ForegroundColor Red } }
    }
    Write-Host "`nUnity exit $exit. Se $log - send de foerste fejllinjer." -ForegroundColor Red
    exit 1
}

# --- 7. Byg alle genererede world meshes til Unity-prefabs ---
Step "Bygger production-art prefabs"
$artLog = Join-Path $PSScriptRoot "production-art-prefabs.log"
& $UnityPath -batchmode -quit -nographics `
    -projectPath $ProjectPath `
    -buildTarget Android `
    -executeMethod ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll `
    -logFile $artLog
$artExit = $LASTEXITCODE
if ($artExit -ne 0) {
    Write-Host "`nPrefab-build fejlede (Unity exit $artExit)." -ForegroundColor Red
    if (Test-Path $artLog) {
        Select-String -Path $artLog -Pattern "\[ProjectOEN.Art\]|error CS|Exception:" | Select-Object -First 30 | ForEach-Object {
            Write-Host "   $($_.Line.Trim())" -ForegroundColor Red
        }
    }
    exit 1
}

# --- 8. Byg separat Stormnatten visual-review scene ---
Step "Bygger Stormnatten art showcase"
$showcaseLog = Join-Path $PSScriptRoot "production-art-showcase.log"
& $UnityPath -batchmode -quit -nographics `
    -projectPath $ProjectPath `
    -buildTarget Android `
    -executeMethod ProjectOen.Art.Editor.ProductionArtShowcaseBuilder.BuildShowcase `
    -logFile $showcaseLog
$showcaseExit = $LASTEXITCODE
if ($showcaseExit -ne 0) {
    Write-Host "`nShowcase-build fejlede (Unity exit $showcaseExit)." -ForegroundColor Red
    if (Test-Path $showcaseLog) {
        Select-String -Path $showcaseLog -Pattern "\[ProjectOEN.Art\]|error CS|Exception:" | Select-Object -First 30 | ForEach-Object {
            Write-Host "   $($_.Line.Trim())" -ForegroundColor Red
        }
    }
    exit 1
}

# --- 9. Tilfoej billig lokal stormregn til visual-review-scenen ---
Step "Tilfoejer stormatmosfaere"
$stormLog = Join-Path $PSScriptRoot "production-art-storm.log"
& $UnityPath -batchmode -quit -nographics `
    -projectPath $ProjectPath `
    -buildTarget Android `
    -executeMethod ProjectOen.Art.Editor.ProductionArtStormAtmosphereBuilder.AddStormAtmosphere `
    -logFile $stormLog
$stormExit = $LASTEXITCODE
if ($stormExit -ne 0) {
    Write-Host "`nStorm-atmosfaere fejlede (Unity exit $stormExit)." -ForegroundColor Red
    if (Test-Path $stormLog) {
        Select-String -Path $stormLog -Pattern "\[ProjectOEN.Art\]|error CS|Exception:" | Select-Object -First 30 | ForEach-Object {
            Write-Host "   $($_.Line.Trim())" -ForegroundColor Red
        }
    }
    exit 1
}

Step "Resultat"
if (Test-Path $log) {
    Select-String -Path $log -Pattern "\[M0B-SETUP\]" | ForEach-Object { Note $_.Line.Trim() }
}
foreach ($artResultLog in @($artLog, $showcaseLog, $stormLog)) {
    if (Test-Path $artResultLog) {
        Select-String -Path $artResultLog -Pattern "\[ProjectOEN.Art\]" | ForEach-Object { Note $_.Line.Trim() }
    }
}
Write-Host "`nFase 1 faerdig. Projekt: $ProjectPath" -ForegroundColor Green
Write-Host "Production art er installeret, world meshes er bygget til prefabs, og StormnattenArtShowcase.unity er genereret med lokal stormregn." -ForegroundColor Green
Write-Host "Showcase-scenen er kun visual review og er ikke M0b's 72 Hz CoopGame-gate." -ForegroundColor Green
Write-Host "Naeste: importer Photon Fusion 2 (App ID), koer saa Fase 2 i RUNBOOK.md." -ForegroundColor Green
