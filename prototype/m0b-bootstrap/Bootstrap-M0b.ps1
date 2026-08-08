<#
  M0b Fase 1 — opret det rigtige Projekt Øen Unity-projekt (Photon-uafhængigt).

  Bygger på det, M0a beviste: ASCII-manifest (ingen BOM), direkte XR-API, Configure
  i sin egen Unity-session. Efter denne kører: projektet findes, pakkerne er låst,
  HELE Core-laget kompilerer som en Unity-assembly, og OpenXR er sat op for Android.

  Fusion/netværk (src/unity) kommer i Fase 2 EFTER Photon-SDK'en er importeret —
  ellers kan projektet ikke kompilere. Se RUNBOOK.md.

  Anders koerer:
    .\Bootstrap-M0b.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe"

  UNVERIFIED-IN-SANDBOX: scriptet er ikke koert (ingen Unity i skrivemiljoeet), men
  hvert trin bygger paa den verificerede M0a-vej og logger sit resultat.
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

# --- 2. Pakker (ASCII, ingen BOM — M0a-lektien: Unity afviser BOM i manifest.json) ---
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

# --- 4. XR-configure-editor ---
Step "Kopierer XR-config editor"
$editorDst = Join-Path $ProjectPath "Assets\Editor"
New-Item -ItemType Directory -Force -Path $editorDst | Out-Null
Copy-Item "$PSScriptRoot\Editor\M0bConfigure.cs" (Join-Path $editorDst "M0bConfigure.cs") -Force

# --- 5. Unity: konfigurer i egen session (importerer pakker foerst, 5-15 min) ---
Step "Koerer Unity (M0bConfigure.Configure)"
Note "Foerste koersel importerer OpenXR + XRI og kan tage 5-15 minutter."
$log = Join-Path $PSScriptRoot "m0b-configure.log"
& $UnityPath -batchmode -quit -nographics `
    -projectPath $ProjectPath `
    -buildTarget Android `
    -executeMethod M0bConfigure.Configure `
    -logFile $log
$exit = $LASTEXITCODE

Step "Resultat"
if (Test-Path $log) {
    Select-String -Path $log -Pattern "\[M0B-SETUP\]" | ForEach-Object { Note $_.Line.Trim() }
    $errs = Select-String -Path $log -Pattern "error CS|Exception:" | Select-Object -First 15
    if ($errs) { Write-Host "`nFejl fra Unity:" -ForegroundColor Red; $errs | ForEach-Object { Write-Host "   $($_.Line.Trim())" -ForegroundColor Red } }
}
if ($exit -eq 0) {
    Write-Host "`nFase 1 faerdig. Projekt: $ProjectPath" -ForegroundColor Green
    Write-Host "Naeste: importer Photon Fusion 2 (App ID), koer saa Fase 2 i RUNBOOK.md." -ForegroundColor Green
} else {
    Write-Host "`nUnity exit $exit. Se $log — send de foerste fejllinjer." -ForegroundColor Red
    exit 1
}
