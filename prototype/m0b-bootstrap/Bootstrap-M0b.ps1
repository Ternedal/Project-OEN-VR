<#
  M0b Fase 1 - opret det rigtige Projekt Oeen Unity-projekt (Photon-uafhaengigt).

  Bygger paa det, M0a beviste: ASCII-manifest (ingen BOM), direkte XR-API, Configure
  i sin egen Unity-session. Efter denne koerer: projektet findes, pakkerne er laast,
  HELE Core-laget kompilerer som en Unity-assembly, OpenXR er sat op for Android,
  og den genererede Project OEN production-art pakke er installeret i Unity-projektet.

  Production-art-delen bygger world-prefabs, canonical damaged/wet state appearance,
  en isoleret dry/mid/storm materialekalibrering, runtime art state catalogs, en 6x3
  state-transition matrix med runtime SetState-audit, en 1:1 hero-prop/world-anchor
  readability scene med physical-scale audit, ground decals, Quest-venlige VFX,
  isoleret VFX review/audit, diegetiske VR UI-prefabs, fysisk UI review/audit,
  Stormnatten art-showcase, lokal stormregn, vaade overflader, vind/regnsplash/fjernt lyn,
  renderer-culled vindrespons paa dug/reb/vegetation og Quest 2 art-budgetaudit.
  Review-scenerne er IKKE M0b's CoopGame performance/netvaerksgate.

  Fusion/netvaerk (src/unity) kommer i Fase 2 EFTER Photon-SDK'en er importeret.
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

Step "Opretter projekt"
if (Test-Path $ProjectPath) { Note "findes allerede: $ProjectPath (genbruges)" }
else {
    & $UnityPath -batchmode -quit -nographics -createProject $ProjectPath -logFile - | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Unity kunne ikke oprette projektet (exit $LASTEXITCODE)" }
}
$ProjectPath = (Resolve-Path $ProjectPath).Path

Step "Skriver pakkeliste"
$manifestSrc = Join-Path $PSScriptRoot "templates\manifest.json"
$manifestDst = Join-Path $ProjectPath "Packages\manifest.json"
[System.IO.File]::WriteAllText($manifestDst, [System.IO.File]::ReadAllText($manifestSrc), (New-Object System.Text.ASCIIEncoding))
Note "skrevet: $manifestDst (OpenXR + XRI + Input System)"

Step "Kopierer Core-laget + asmdef"
$coreDst = Join-Path $ProjectPath "Assets\ProjectOen\Core"
New-Item -ItemType Directory -Force -Path $coreDst | Out-Null
Copy-Item "$repo\src\ProjectOen.Core\*" $coreDst -Recurse -Force
Get-ChildItem $coreDst -Recurse -Directory | Where-Object { $_.Name -in @("bin","obj") } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $coreDst -Recurse -File | Where-Object { $_.Extension -in @(".csproj",".dll",".pdb") } | Remove-Item -Force -ErrorAction SilentlyContinue
Copy-Item "$PSScriptRoot\templates\ProjectOen.Core.asmdef" (Join-Path $coreDst "ProjectOen.Core.asmdef") -Force
Note "Core -> Assets\ProjectOen\Core"

Step "Installerer Project OEN production art"
$artSrc = Join-Path $repo "Assets\ProjectOEN\ProductionArt"
if (-not (Test-Path $artSrc)) { throw "Production art mangler i repoet: $artSrc. Koer generated-art workflowet foerst." }
$artDst = Join-Path $ProjectPath "Assets\ProjectOEN\ProductionArt"
$artRuntimeDst = Join-Path $ProjectPath "Assets\ProjectOEN\ArtRuntime"
$artEditorDst = Join-Path $ProjectPath "Assets\ProjectOEN\Editor"
New-Item -ItemType Directory -Force -Path $artDst | Out-Null
foreach ($folder in @("Sprites", "Meshes", "Materials", "Decals", "Docs")) {
    $srcFolder = Join-Path $artSrc $folder
    $dstFolder = Join-Path $artDst $folder
    if (Test-Path $dstFolder) { Remove-Item $dstFolder -Recurse -Force }
    Copy-Item $srcFolder $dstFolder -Recurse -Force
}

Step "Installerer production-art runtime state controllers"
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
    "ProductionArtStateTransitionShowcaseBuilder.cs",
    "ProductionArtStateTransitionShowcaseAudit.cs",
    "ProductionArtHeroReadabilityShowcaseBuilder.cs",
    "ProductionArtHeroReadabilityShowcaseAudit.cs",
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
    "ProductionArtShowcaseAudit.cs"
)) {
    Copy-Item (Join-Path $repo "src\unity\ProjectOen.Art\Editor\$builder") (Join-Path $artEditorDst $builder) -Force
}
Note "ProductionArt + runtime state controllers + state appearance + state-transition/hero/material/world/state/decal/VFX/UI/showcase builders -> ProjektOenApp"

Step "Kopierer XR-config editor"
$editorDst = Join-Path $ProjectPath "Assets\Editor"
New-Item -ItemType Directory -Force -Path $editorDst | Out-Null
Copy-Item "$PSScriptRoot\Editor\M0bConfigure.cs" (Join-Path $editorDst "M0bConfigure.cs") -Force

function Run-UnityStep([string]$Label, [string]$Method, [string]$LogName, [string]$Pattern = "\[ProjectOEN.Art|error CS|Exception:") {
    Step $Label
    $stepLog = Join-Path $PSScriptRoot $LogName
    & $UnityPath -batchmode -quit -nographics `
        -projectPath $ProjectPath `
        -buildTarget Android `
        -executeMethod $Method `
        -logFile $stepLog
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n$Label fejlede (Unity exit $LASTEXITCODE)." -ForegroundColor Red
        if (Test-Path $stepLog) {
            Select-String -Path $stepLog -Pattern $Pattern | Select-Object -First 40 | ForEach-Object { Write-Host "   $($_.Line.Trim())" -ForegroundColor Red }
        }
        exit 1
    }
    if (Test-Path $stepLog) { Select-String -Path $stepLog -Pattern "\[ProjectOEN.Art" | ForEach-Object { Note $_.Line.Trim() } }
    return $stepLog
}

Step "Koerer Unity (M0bConfigure.Configure)"
$log = Join-Path $PSScriptRoot "m0b-configure.log"
& $UnityPath -batchmode -quit -nographics `
    -projectPath $ProjectPath `
    -buildTarget Android `
    -executeMethod M0bConfigure.Configure `
    -logFile $log
if ($LASTEXITCODE -ne 0) {
    if (Test-Path $log) { Select-String -Path $log -Pattern "\[M0B-SETUP\]|error CS|Exception:" | Select-Object -First 30 | ForEach-Object { Write-Host "   $($_.Line.Trim())" -ForegroundColor Red } }
    exit 1
}

$artLog = Run-UnityStep "Bygger production-art prefabs" `
    "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll" `
    "production-art-prefabs.log"

$stateAppearanceLog = Run-UnityStep "Profilerer canonical damaged/wet states" `
    "ProjectOen.Art.Editor.ProductionArtStateAppearanceBuilder.BuildAll" `
    "production-art-state-appearance.log"

$stateAppearanceAuditLog = Run-UnityStep "Auditerer state-specifik storm appearance" `
    "ProjectOen.Art.Editor.ProductionArtStateAppearanceAudit.AuditAll" `
    "production-art-state-appearance-audit.log"

$materialCalibrationLog = Run-UnityStep "Bygger dry/mid/storm materialekalibrering" `
    "ProjectOen.Art.Editor.ProductionArtMaterialCalibrationBuilder.BuildShowcase" `
    "production-art-material-calibration.log"

$materialCalibrationAuditLog = Run-UnityStep "Auditerer materialekalibrering og scoped vaadhed" `
    "ProjectOen.Art.Editor.ProductionArtMaterialCalibrationAudit.AuditShowcase" `
    "production-art-material-calibration-audit.log"

$stateCatalogLog = Run-UnityStep "Bygger runtime art state catalogs" `
    "ProjectOen.Art.Editor.ProductionArtStateCatalogBuilder.BuildAll" `
    "production-art-state-catalog.log"

$stateTransitionLog = Run-UnityStep "Bygger 6x3 state-transition review matrix" `
    "ProjectOen.Art.Editor.ProductionArtStateTransitionShowcaseBuilder.BuildShowcase" `
    "production-art-state-transition.log"

$stateTransitionAuditLog = Run-UnityStep "Auditerer runtime state-skift og appearance-profiler" `
    "ProjectOen.Art.Editor.ProductionArtStateTransitionShowcaseAudit.AuditShowcase" `
    "production-art-state-transition-audit.log"

$heroReadabilityLog = Run-UnityStep "Bygger 1:1 hero-prop readability review" `
    "ProjectOen.Art.Editor.ProductionArtHeroReadabilityShowcaseBuilder.BuildShowcase" `
    "production-art-hero-readability.log"

$heroReadabilityAuditLog = Run-UnityStep "Auditerer hero props og world anchors i fysisk VR-skala" `
    "ProjectOen.Art.Editor.ProductionArtHeroReadabilityShowcaseAudit.AuditShowcase" `
    "production-art-hero-readability-audit.log"

$decalLog = Run-UnityStep "Bygger ground decals" `
    "ProjectOen.Art.Editor.ProductionArtDecalBuilder.BuildAll" `
    "production-art-decals.log"

$vfxLog = Run-UnityStep "Bygger Quest-venlige production VFX" `
    "ProjectOen.Art.Editor.ProductionArtVfxBuilder.BuildAll" `
    "production-art-vfx.log"

$vfxShowcaseLog = Run-UnityStep "Bygger isoleret VFX review-scene" `
    "ProjectOen.Art.Editor.ProductionArtVfxShowcaseBuilder.BuildShowcase" `
    "production-art-vfx-showcase.log"

$vfxAuditLog = Run-UnityStep "Auditerer isoleret VFX review-scene" `
    "ProjectOen.Art.Editor.ProductionArtVfxShowcaseAudit.AuditShowcase" `
    "production-art-vfx-audit.log"

$uiLog = Run-UnityStep "Bygger diegetiske VR UI-prefabs" `
    "ProjectOen.Art.Editor.ProductionArtDiegeticUiBuilder.BuildAll" `
    "production-art-diegetic-ui.log"

$uiShowcaseLog = Run-UnityStep "Bygger fysisk diegetic-UI review-scene" `
    "ProjectOen.Art.Editor.ProductionArtUiShowcaseBuilder.BuildShowcase" `
    "production-art-ui-showcase.log"

$uiAuditLog = Run-UnityStep "Auditerer diegetic UI i fysisk VR-skala" `
    "ProjectOen.Art.Editor.ProductionArtUiShowcaseAudit.AuditShowcase" `
    "production-art-ui-audit.log"

$showcaseLog = Run-UnityStep "Bygger Stormnatten art showcase" `
    "ProjectOen.Art.Editor.ProductionArtShowcaseBuilder.BuildShowcase" `
    "production-art-showcase.log"

$stormLog = Run-UnityStep "Tilfoejer stormatmosfaere og vaade overflader" `
    "ProjectOen.Art.Editor.ProductionArtStormAtmosphereBuilder.AddStormAtmosphere" `
    "production-art-storm.log"

$stormMotionLog = Run-UnityStep "Tilfoejer vind, regnsplash og fjernt lyn" `
    "ProjectOen.Art.Editor.ProductionArtStormFxBuilder.AddStormMotionFx" `
    "production-art-storm-motion.log"

$windResponseLog = Run-UnityStep "Tilfoejer vindrespons til dug, reb og vegetation" `
    "ProjectOen.Art.Editor.ProductionArtWindResponseBuilder.AddWindResponse" `
    "production-art-wind-response.log"

$budgetLog = Run-UnityStep "Auditerer Stormnatten showcase mod Quest 2-budget" `
    "ProjectOen.Art.Editor.ProductionArtShowcaseAudit.AuditShowcase" `
    "production-art-budget.log" `
    "\[ProjectOEN.Art.Budget\]|error CS|Exception:"

Step "Resultat"
if (Test-Path $log) { Select-String -Path $log -Pattern "\[M0B-SETUP\]" | ForEach-Object { Note $_.Line.Trim() } }
Write-Host "`nFase 1 faerdig. Projekt: $ProjectPath" -ForegroundColor Green
Write-Host "World meshes/prefabs, canonical damaged/wet state appearance, dry/mid/storm materialekalibrering, runtime state catalogs, 6x3 state-transition review, 1:1 hero-readability review, ground decals, production VFX og diegetic UI-prefabs er bygget." -ForegroundColor Green
Write-Host "State-transition auditten kalder runtime SetState gennem shelter, campfire, beacon, tarp, groundsheet og signal cloth og validerer de forventede appearance-profiler." -ForegroundColor Green
Write-Host "Hero-readability auditten maaler canonical hand props, heavy/co-op props og world anchors i meter-space uden root scaling." -ForegroundColor Green
Write-Host "Stormnatten review har state-specifik damage/wetness, regn, vaade overflader, vindblaest debris, campsplash, animeret fjernt lyn og renderer-culled vindrespons paa dug/reb/vegetation." -ForegroundColor Green
Write-Host "State catalogs: Assets\ProjectOEN\ProductionArt\StateSets" -ForegroundColor Green
Write-Host "State transition audit: Assets\ProjectOEN\ProductionArt\Scenes\StateTransitionShowcase.unity" -ForegroundColor Green
Write-Host "Hero readability audit: Assets\ProjectOEN\ProductionArt\Scenes\HeroReadabilityShowcase.unity" -ForegroundColor Green
Write-Host "Material audit: Assets\ProjectOEN\ProductionArt\Scenes\MaterialCalibrationShowcase.unity" -ForegroundColor Green
Write-Host "VFX audit: Assets\ProjectOEN\ProductionArt\Scenes\ProductionVfxShowcase.unity" -ForegroundColor Green
Write-Host "UI audit: Assets\ProjectOEN\ProductionArt\Scenes\DiegeticUiArtShowcase.unity" -ForegroundColor Green
Write-Host "Stormnatten art audit: Assets\ProjectOEN\ProductionArt\Scenes\StormnattenArtShowcase.unity" -ForegroundColor Green
Write-Host "Alle tre review-scener er visual review: VFX, diegetic UI og Stormnatten; materialekalibrering, state-transition og hero-readability er tre yderligere isolerede visual-reviewscener. Ingen af de seks er M0b's 72 Hz CoopGame-gate." -ForegroundColor Green
Write-Host "Naeste: importer Photon Fusion 2 (App ID), koer saa Fase 2 i RUNBOOK.md." -ForegroundColor Green
