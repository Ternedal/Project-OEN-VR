<#
  M0a — bygger smoke-APK'en headless.

  Anders koerer:   .\Build-M0a.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe"

  Scriptet opretter projektet, skriver pakkelisten, kopierer kildefilerne ind,
  koerer Unity i batchmode og lander en APK. Ingen klik.

  UNVERIFIED-IN-SANDBOX: hverken dette script eller Editor-scriptet er koert.
  Hvert trin skriver hvad det gjorde, saa en fejl kan isoleres uden at gaette.
#>

param(
    [Parameter(Mandatory = $true)][string]$UnityPath,
    [string]$ProjectPath = "$PSScriptRoot\..\..\..\..\OenM0aSmoke",
    [switch]$ConfigureOnly
)

$ErrorActionPreference = "Stop"
function Step($m) { Write-Host "`n== $m ==" -ForegroundColor Cyan }
function Note($m) { Write-Host "   $m" -ForegroundColor DarkGray }

if (-not (Test-Path $UnityPath)) { throw "Unity ikke fundet: $UnityPath" }
$repo = Resolve-Path "$PSScriptRoot\..\..\.."
Note "repo: $repo"

# --- 1. Projekt ---
Step "Opretter projekt"
if (Test-Path $ProjectPath) {
    Note "findes allerede: $ProjectPath (genbruges)"
} else {
    & $UnityPath -batchmode -quit -nographics -createProject $ProjectPath -logFile - | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Unity kunne ikke oprette projektet (exit $LASTEXITCODE)" }
    Note "oprettet: $ProjectPath"
}
$ProjectPath = (Resolve-Path $ProjectPath).Path

# --- 2. Pakker ---
# Bevidst minimalt. XR Interaction Toolkit er IKKE med: M0a skal svare paa ét
# spoergsmaal, og hver ekstra pakke er en variabel mere i fejlsoegningen.
# Oculus XR Plugin er ikke med med vilje - den er deprecated, og hele pointen
# med M0a er at afgoere om Quest 1 kan undvaere den.
Step "Skriver pakkeliste"
$manifest = @{
    dependencies = [ordered]@{
        "com.unity.xr.openxr"    = "1.14.3"
        "com.unity.inputsystem"  = "1.11.2"
        "com.unity.xr.management" = "4.5.0"
        "com.unity.modules.xr"   = "1.0.0"
        "com.unity.modules.androidjni" = "1.0.0"
        "com.unity.modules.ui"   = "1.0.0"
        "com.unity.modules.imgui" = "1.0.0"
        "com.unity.modules.physics" = "1.0.0"
    }
}
$manifestPath = Join-Path $ProjectPath "Packages\manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Set-Content $manifestPath -Encoding Ascii
Note "skrevet: $manifestPath"
Note "Versionsnumrene er BEDSTE GAET. Klager Unity, saa fjern versionen og lad Package Manager vaelge."

# --- 3. Kildefiler ---
Step "Kopierer kildefiler"
$scripts = Join-Path $ProjectPath "Assets\Scripts"
$editor  = Join-Path $ProjectPath "Assets\Editor"
New-Item -ItemType Directory -Force -Path $scripts, $editor | Out-Null
Copy-Item "$PSScriptRoot\..\files\SmokeTestHud.cs" $scripts -Force
Copy-Item "$PSScriptRoot\..\files\BuildInfo.cs"    $scripts -Force
Copy-Item "$PSScriptRoot\Editor\M0aBuild.cs"       $editor  -Force
Note "SmokeTestHud.cs, BuildInfo.cs -> Assets\Scripts"
Note "M0aBuild.cs -> Assets\Editor"

# --- 4. Unity ---
$method = if ($ConfigureOnly) { "M0aBuild.Configure" } else { "M0aBuild.ConfigureAndBuild" }
Step "Koerer Unity ($method)"
Note "Foerste koersel importerer pakker og kan tage 5-15 minutter. Log foelger nedenfor."

$log = Join-Path $PSScriptRoot "m0a-build.log"
& $UnityPath -batchmode -quit -nographics `
    -projectPath $ProjectPath `
    -buildTarget Android `
    -executeMethod $method `
    -logFile $log
$unityExit = $LASTEXITCODE

Step "Resultat"
if (Test-Path $log) {
    Select-String -Path $log -Pattern "\[M0A-SETUP\]" | ForEach-Object { Note $_.Line.Trim() }
    $errors = Select-String -Path $log -Pattern "error CS|BuildFailedException|Exception:" | Select-Object -First 15
    if ($errors) {
        Write-Host "`nFejl fra Unity:" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "   $($_.Line.Trim())" -ForegroundColor Red }
    }
}

$apk = Join-Path $ProjectPath "Build\OenM0aSmoke.apk"
if (Test-Path $apk) {
    $mb = [math]::Round((Get-Item $apk).Length / 1MB, 1)
    Write-Host "`nAPK klar: $apk ($mb MB)" -ForegroundColor Green
    Write-Host "Naeste:   .\Run-M0a.ps1 -Apk `"$apk`"" -ForegroundColor Green
} elseif (-not $ConfigureOnly) {
    Write-Host "`nIngen APK. Fuld log: $log" -ForegroundColor Red
    Write-Host "Send de foerste fejllinjer - de haenger typisk sammen." -ForegroundColor Yellow
    exit 1
}
