<#
  M0b Fase 1 - opret det rigtige Projekt Oeen Unity-projekt (Photon-uafhaengigt).

  Bygger paa det, M0a beviste: ASCII-manifest (ingen BOM), direkte XR-API, Configure
  i sin egen Unity-session. Efter denne koerer: projektet findes, pakkerne er laast,
  HELE Core-laget kompilerer som en Unity-assembly, OpenXR er sat op for Android,
  og den genererede Project OEN production-art pakke er installeret i Unity-projektet.

  Production-art-delen bygger world-prefabs, ground decals, diegetiske VR UI-prefabs,
  en fysisk UI-review-scene med Unity-side skala/struktur-audit, en separat Stormnatten
  art-showcase, lokal stormregn og Quest 2 art-budgetaudit. Review-scenerne er IKKE
  M0b's CoopGame performance/netvaerksgate.

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
if (Test-Path $ProjectPath) {
    Note "findes allerede: $ProjectPath (genbruges)"
} else {
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
New-Item -ItemType Directory -Force -Path $artDst | Out-Null
foreach ($folder in @("Sprites", "Meshes", "Materials", "Decals", "Docs")) {
    $srcFolder = Join-Path $artSrc $folder
    $dstFolder = Join-Path $artDst $folder
    if (Test-Path $dstFolder) { Remove-Item $dstFolder -Recurse -Force }
    Copy-Item $srcFolder $dstFolder -Recurse -Force
}

$artEditorDst = Join-Path $ProjectPath "Assets\ProjectOEN\Editor"
New-Item -ItemType Directory -Force -Path $artEditorDst | Out-Null
foreach ($builder in @(
    "ProductionArtPrefabBuilder.cs",
    "ProductionArtDecalBuilder.cs",
    "ProductionArtDiegeticUiBuilder.cs",
    "ProductionArtUiShowcaseBuilder.cs",
    "ProductionArtUiShowcaseAudit.cs",
    "ProductionArtShowcaseBuilder.cs",
    "ProductionArtStormAtmosphereBuilder.cs",
    "ProductionArtShowcaseAudit.cs"
)) {
    Copy-Item (Join-Path $repo "src\unity\ProjectOen.Art\Editor\$builder") (Join-Path $artEditorDst $builder) -Force
}
Note "ProductionArt + world/decal/UI/showcase builders -> ProjektOenApp"

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
    if (Test-Path $log) {
        Select-String -Path $log -Pattern "\[M0B-SETUP\]|error CS|Exception:" | Select-Object -First 30 | ForEach-Object { Write-Host "   $($_.Line.Trim())" -ForegroundColor Red }
    }
    exit 1
}

$artLog = Run-UnityStep "Bygger production-art prefabs" `
    "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll" `
    "production-art-prefabs.log"

$decalLog = Run-UnityStep "Bygger ground decals" `
    "ProjectOen.Art.Editor.ProductionArtDecalBuilder.BuildAll" `
    "production-art-decals.log"

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

$stormLog = Run-UnityStep "Tilfoejer stormatmosfaere" `
    "ProjectOen.Art.Editor.ProductionArtStormAtmosphereBuilder.AddStormAtmosphere" `
    "production-art-storm.log"

$budgetLog = Run-UnityStep "Auditerer Stormnatten showcase mod Quest 2-budget" `
    "ProjectOen.Art.Editor.ProductionArtShowcaseAudit.AuditShowcase" `
    "production-art-budget.log" `
    "\[ProjectOEN.Art.Budget\]|error CS|Exception:"

Step "Resultat"
if (Test-Path $log) { Select-String -Path $log -Pattern "\[M0B-SETUP\]" | ForEach-Object { Note $_.Line.Trim() } }
Write-Host "`nFase 1 faerdig. Projekt: $ProjectPath" -ForegroundColor Green
Write-Host "World meshes/prefabs, ground decals og diegetic UI-prefabs er bygget." -ForegroundColor Green
Write-Host "UI physical-scale audit: Assets\ProjectOEN\ProductionArt\Scenes\DiegeticUiArtShowcase.unity" -ForegroundColor Green
Write-Host "Stormnatten art audit: Assets\ProjectOEN\ProductionArt\Scenes\StormnattenArtShowcase.unity" -ForegroundColor Green
Write-Host "Begge review-scener er visual review og ikke M0b's 72 Hz CoopGame-gate." -ForegroundColor Green
Write-Host "Naeste: importer Photon Fusion 2 (App ID), koer saa Fase 2 i RUNBOOK.md." -ForegroundColor Green
