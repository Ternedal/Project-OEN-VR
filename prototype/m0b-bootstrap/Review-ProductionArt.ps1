<#
  Fast visual-review loop for Project OEN production art.

  Default mode keeps the established one-Unity-process-per-step flow for debugging.
  -OneShot runs the same build/audit chain through ProductionArtBatchVerification
  inside one real Unity Editor process and writes a machine-readable JSON report.
#>

param(
    [Parameter(Mandatory = $true)][string]$UnityPath,
    [string]$ProjectPath = "$PSScriptRoot\..\..\..\ProjektOenApp",
    [switch]$OneShot,
    [switch]$OpenEditor
)

$ErrorActionPreference = "Stop"
function Step($m) { Write-Host "`n== $m ==" -ForegroundColor Cyan }
function Note($m) { Write-Host "   $m" -ForegroundColor DarkGray }

function Invoke-UnityBatch([string[]]$Arguments) {
    $quotedArguments = @($Arguments | ForEach-Object {
        if ($_.Contains('"')) { throw "Unity-argument maa ikke indeholde citationstegn: $_" }
        if ($_ -match '\s') { '"' + $_ + '"' } else { $_ }
    })
    $process = Start-Process -FilePath $UnityPath `
        -ArgumentList $quotedArguments `
        -PassThru `
        -WindowStyle Hidden
    $process.WaitForExit()
    return [int]$process.ExitCode
}

if (-not (Test-Path $UnityPath)) { throw "Unity ikke fundet: $UnityPath" }
if (-not (Test-Path $ProjectPath)) { throw "Unity-projekt ikke fundet: $ProjectPath. Koer Bootstrap-M0b.ps1 foerst." }

$repo = (Resolve-Path "$PSScriptRoot\..\..").Path
$ProjectPath = (Resolve-Path $ProjectPath).Path
$artSrc = Join-Path $repo "Assets\ProductionArt"
$artDst = Join-Path $ProjectPath "Assets\ProductionArt"
$artCodeDst = Join-Path $ProjectPath "Assets\ProjectOen\Unity\ProjectOen.Art"
if (-not (Test-Path $artSrc)) { throw "Production art mangler i repoet: $artSrc" }

Step "Synkroniserer production art"
New-Item -ItemType Directory -Force -Path $artDst | Out-Null
foreach ($folder in @("Sprites", "Meshes", "Materials", "Decals", "Docs")) {
    $srcFolder = Join-Path $artSrc $folder
    $dstFolder = Join-Path $ProjectPath "Assets\ProductionArt\$folder"
    if (-not (Test-Path $srcFolder)) { throw "Production-art mappe mangler: $srcFolder" }
    if (Test-Path $dstFolder) { Remove-Item $dstFolder -Recurse -Force }
    Copy-Item $srcFolder $dstFolder -Recurse -Force
}

Step "Synkroniserer production-art assemblies"
$artRuntimeSource = Join-Path $repo "src\unity\ProjectOen.Art\Runtime\*.cs"
$requiredArtEditorSources = @(
    "ProductionArtBatchVerification.cs",
    "ProductionArtDecalBuilder.cs",
    "ProductionArtDiegeticUiBuilder.cs",
    "ProductionArtHeroReadabilityShowcaseAudit.cs",
    "ProductionArtHeroReadabilityShowcaseBuilder.cs",
    "ProductionArtMaterialCalibrationAudit.cs",
    "ProductionArtMaterialCalibrationBuilder.cs",
    "ProductionArtModelImporter.cs",
    "ProductionArtPrefabBuilder.cs",
    "ProductionArtReviewMenu.cs",
    "ProductionArtShowcaseAudit.cs",
    "ProductionArtShowcaseBuilder.cs",
    "ProductionArtSignalFinaleStoryBuilder.cs",
    "ProductionArtStateAppearanceAudit.cs",
    "ProductionArtStateAppearanceBuilder.cs",
    "ProductionArtStateBindingBuilder.cs",
    "ProductionArtStateCatalogAudit.cs",
    "ProductionArtStateCatalogBuilder.cs",
    "ProductionArtStateTransitionShowcaseAudit.cs",
    "ProductionArtStateTransitionShowcaseBuilder.cs",
    "ProductionArtStormAtmosphereBuilder.cs",
    "ProductionArtStormCampStoryBuilder.cs",
    "ProductionArtStormFxBuilder.cs",
    "ProductionArtUiShowcaseAudit.cs",
    "ProductionArtUiShowcaseBuilder.cs",
    "ProductionArtVfxBuilder.cs",
    "ProductionArtVfxShowcaseAudit.cs",
    "ProductionArtVfxShowcaseBuilder.cs",
    "ProductionArtWindResponseBuilder.cs"
)
if ((Get-ChildItem $artRuntimeSource -ErrorAction SilentlyContinue).Count -eq 0) {
    throw "ProjectOen.Art runtime-kilder mangler."
}
foreach ($sourceName in $requiredArtEditorSources) {
    if (-not (Test-Path (Join-Path $repo "src\unity\ProjectOen.Art\Editor\$sourceName"))) {
        throw "ProjectOen.Art editor-kilde mangler: $sourceName"
    }
}
if (Test-Path $artCodeDst) { Remove-Item $artCodeDst -Recurse -Force }
New-Item -ItemType Directory -Force -Path $artCodeDst | Out-Null
Copy-Item (Join-Path $repo "src\unity\ProjectOen.Art\*") $artCodeDst -Recurse -Force
Note "Art + runtime/editor assemblies + import contract er synkroniseret til $ProjectPath"

function Run-UnityArtStep([string]$Label, [string]$Method, [string]$LogName) {
    Step $Label
    $log = Join-Path $PSScriptRoot $LogName
    $exit = Invoke-UnityBatch -Arguments @(
        "-batchmode", "-quit", "-nographics",
        "-projectPath", $ProjectPath,
        "-buildTarget", "Android",
        "-executeMethod", $Method,
        "-logFile", $log
    )
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

function Open-ShowcaseEditor {
    Step "Aabner Unity visual-review"
    $args = @("-projectPath", $ProjectPath, "-executeMethod", "ProjectOen.Art.Editor.ProductionArtReviewMenu.OpenShowcase")
    Start-Process -FilePath $UnityPath -ArgumentList $args | Out-Null
    Note "Unity starter med Stormnatten-showcase som aktiv scene."
}

if ($OneShot) {
    Step "Koerer samlet on-machine Unity art verification"
    $batchLog = Join-Path $PSScriptRoot "review-art-one-shot.log"
    $projectReport = Join-Path $ProjectPath "ProjectOEN-ArtVerification.json"
    $reviewReport = Join-Path $PSScriptRoot "review-art-verification.json"
    Remove-Item $projectReport -Force -ErrorAction SilentlyContinue
    Remove-Item $reviewReport -Force -ErrorAction SilentlyContinue

    $exit = Invoke-UnityBatch -Arguments @(
        "-batchmode", "-quit", "-nographics",
        "-projectPath", $ProjectPath,
        "-buildTarget", "Android",
        "-executeMethod", "ProjectOen.Art.Editor.ProductionArtBatchVerification.RunAll",
        "-logFile", $batchLog
    )

    if (Test-Path $batchLog) {
        Select-String -Path $batchLog -Pattern "\[ProjectOEN.Art.Batch\]|error CS|Exception:" | ForEach-Object {
            if ($_.Line -match "FAIL|error CS|Exception:") { Write-Host "   $($_.Line.Trim())" -ForegroundColor Red }
            else { Note $_.Line.Trim() }
        }
    }

    if ($exit -ne 0) {
        Write-Host "`nSamlet Unity art verification fejlede (Unity exit $exit)." -ForegroundColor Red
        exit 1
    }
    if (-not (Test-Path $projectReport)) {
        throw "Unity afsluttede uden verification-rapport: $projectReport"
    }

    $report = Get-Content $projectReport -Raw | ConvertFrom-Json
    if ($report.status -ne "PASS" -or [int]$report.failed -ne 0) {
        Write-Host "Unity verification-rapport er ikke groen: status=$($report.status), failed=$($report.failed)" -ForegroundColor Red
        $report.steps | Where-Object { $_.status -ne "PASS" } | ForEach-Object {
            Write-Host "   FAIL $($_.name): $($_.error)" -ForegroundColor Red
        }
        exit 1
    }

    Copy-Item $projectReport $reviewReport -Force
    Step "One-shot resultat"
    Write-Host "PASS: $($report.passed) Unity build/audit-trin i Unity $($report.unityVersion)." -ForegroundColor Green
    $report.steps | ForEach-Object { Note ("PASS {0} ({1} ms)" -f $_.name, $_.durationMs) }
    Write-Host "Maskinrapport: $reviewReport" -ForegroundColor Green
    Write-Host "Unity-log: $batchLog" -ForegroundColor Green
    Write-Host "M0b CoopGame/build settings er ikke aendret; de seks review-scener forbliver build-isolerede." -ForegroundColor Green

    if ($OpenEditor) { Open-ShowcaseEditor }
    return
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

Run-UnityArtStep "Bygger 6x3 state-transition review matrix" `
    "ProjectOen.Art.Editor.ProductionArtStateTransitionShowcaseBuilder.BuildShowcase" `
    "review-art-state-transition.log"

Run-UnityArtStep "Auditerer runtime state-skift og appearance-profiler" `
    "ProjectOen.Art.Editor.ProductionArtStateTransitionShowcaseAudit.AuditShowcase" `
    "review-art-state-transition-audit.log"

Run-UnityArtStep "Bygger 1:1 hero-prop readability review" `
    "ProjectOen.Art.Editor.ProductionArtHeroReadabilityShowcaseBuilder.BuildShowcase" `
    "review-art-hero-readability.log"

Run-UnityArtStep "Auditerer hero props og world anchors i fysisk VR-skala" `
    "ProjectOen.Art.Editor.ProductionArtHeroReadabilityShowcaseAudit.AuditShowcase" `
    "review-art-hero-readability-audit.log"

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

Run-UnityArtStep "Tilfoejer camp/finale historier, lokal stormregn og vaade overflader" `
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
Write-Host "Production-art review er bygget; canonical damaged/wet states har state-specifik appearance; 6x3 transition-matrix og runtime SetState-audit bestod; hero props/world anchors er samlet i 1:1 physical-scale review; material/world assets, runtime state catalogs, decals, VFX og UI er wired; Stormnatten har camp + signal-finale consequence stories, regn, vaadhed, vind/splash/lyn og vindrespons." -ForegroundColor Green
Write-Host "State catalogs: Assets\ProductionArt\StateSets" -ForegroundColor Green
Write-Host "State transition scene: Assets\ProductionArt\Scenes\StateTransitionShowcase.unity" -ForegroundColor Green
Write-Host "Hero readability scene: Assets\ProductionArt\Scenes\HeroReadabilityShowcase.unity" -ForegroundColor Green
Write-Host "Material scene: Assets\ProductionArt\Scenes\MaterialCalibrationShowcase.unity" -ForegroundColor Green
Write-Host "VFX scene: Assets\ProductionArt\Scenes\ProductionVfxShowcase.unity" -ForegroundColor Green
Write-Host "UI scene: Assets\ProductionArt\Scenes\DiegeticUiArtShowcase.unity" -ForegroundColor Green
Write-Host "World scene: Assets\ProductionArt\Scenes\StormnattenArtShowcase.unity" -ForegroundColor Green
Write-Host "VFX prefabs: Assets\ProductionArt\VfxPrefabs" -ForegroundColor Green
Write-Host "UI prefabs: Assets\ProductionArt\UiPrefabs" -ForegroundColor Green
Write-Host "M0b CoopGame/build settings er ikke aendret." -ForegroundColor Green

if ($OpenEditor) { Open-ShowcaseEditor }
