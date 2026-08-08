<#
  M0a — installerer, koerer og AFLAESER resultatet automatisk.

  Anders koerer:   .\Run-M0a.ps1 -Apk .\OenM0aSmoke.apk
  ...tager headsettet paa, starter appen fra "Ukendte kilder", venter 30 sek.

  Scriptet parser SmokeTestHud'ens logcat-linjer og skriver et udfyldt afsnit
  til RESULTAT.md. Du skal ikke aflaese en HUD og fortolke - tallet staar der.
#>

param(
    [Parameter(Mandatory = $true)][string]$Apk,
    [string]$Serial = "",
    [string]$Adb = "adb",
    [int]$CaptureSeconds = 40
)

$ErrorActionPreference = "Stop"
function Step($m) { Write-Host "`n== $m ==" -ForegroundColor Cyan }

if (-not (Test-Path $Apk)) { throw "APK ikke fundet: $Apk" }
$target = if ($Serial) { @("-s", $Serial) } else { @() }

Step "Enhed"
$model = (& $Adb @target shell getprop ro.product.model) -join "" -replace "\s",""
$os    = (& $Adb @target shell getprop ro.build.version.release) -join "" -replace "\s",""
$inc   = (& $Adb @target shell getprop ro.build.version.incremental) -join "" -replace "\s",""
Write-Host "   model=$model  android=$os  build=$inc"
if (-not $model) { throw "Ingen enhed. Er headsettet taendt, tilsluttet og USB-debugging godkendt i headsettet?" }

Step "Installerer"
& $Adb @target install -r $Apk
if ($LASTEXITCODE -ne 0) { throw "adb install fejlede (exit $LASTEXITCODE). Noter fejlteksten ordret." }

Step "Starter appen"
& $Adb @target shell am start -n com.projectoen.m0asmoke/com.unity3d.player.UnityPlayerActivity 2>$null | Out-Null
& $Adb @target logcat -c

Write-Host "`n   TAG HEADSETTET PAA NU." -ForegroundColor Yellow
Write-Host "   Gaa et skridt til siden, drej hovedet, bevaeg haenderne." -ForegroundColor Yellow
Write-Host "   Optager i $CaptureSeconds sekunder...`n" -ForegroundColor Yellow

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$safe  = ($model -replace '[^\w]', '_')
$log   = Join-Path $PSScriptRoot "m0a-$safe-$stamp.log"

$job = Start-Job -ScriptBlock {
    param($adb, $t, $out)
    & $adb @t logcat -s Unity:V OenM0a:V CRASH:V AndroidRuntime:E | Set-Content $out
} -ArgumentList $Adb, $target, $log
Start-Sleep -Seconds $CaptureSeconds
Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue

Step "Aflaeser"
if (-not (Test-Path $log)) { throw "Ingen log opsamlet: $log" }
$lines = Get-Content $log

$hud = $lines | Where-Object { $_ -match "OenM0a.*device:" } | Select-Object -Last 1
$startup = $lines | Where-Object { $_ -match "BuildInfo:" } | Select-Object -Last 1
$xrErrors = $lines | Where-Object { $_ -match "XR_ERROR|openxr.*fail|LoaderNotFound|Failed to load" }
$crash = $lines | Where-Object { $_ -match "AndroidRuntime|FATAL|CRASH" }

$started  = [bool]$startup
$tracking = ($hud -match "TRACKING: JA") -or ($lines -match "TRACKING: JA")
$fps = if ($hud -match "fps:\s*([\d.]+)") { $Matches[1] } else { "?" }
$gfx = if ($lines -match "gfx:\s*(\w+)") { $Matches[1] } else { "?" }

function Mark($b) { if ($b) { "ja" } else { "NEJ" } }
Write-Host "   appen startede: $(Mark $started)"
Write-Host "   hovedtracking:  $(Mark $tracking)"
Write-Host "   fps:            $fps"
Write-Host "   graphics API:   $gfx"
if ($xrErrors) { Write-Host "`n   XR-fejl fundet:" -ForegroundColor Red; $xrErrors | Select-Object -First 5 | ForEach-Object { Write-Host "     $_" -ForegroundColor Red } }
if ($crash)    { Write-Host "`n   Crash:" -ForegroundColor Red; $crash | Select-Object -First 5 | ForEach-Object { Write-Host "     $_" -ForegroundColor Red } }

$verdict = if (-not $started) { "STARTER IKKE" } elseif (-not $tracking) { "STARTER, TRACKER IKKE" } else { "OK" }
Write-Host "`n   => $model : $verdict" -ForegroundColor $(if ($verdict -eq "OK") { "Green" } else { "Red" })

$out = Join-Path $PSScriptRoot "RESULTAT-$safe-$stamp.md"
@"
# M0a-maaling — $model

- Dato: $(Get-Date -Format "yyyy-MM-dd HH:mm")
- Enhed: ``$model`` | Android $os | build ``$inc``
- Graphics API: $gfx
- APK: ``$Apk``

| Punkt | Resultat |
|---|---|
| Installerer | ja |
| Appen starter | $(Mark $started) |
| Hovedtracking | $(Mark $tracking) |
| FPS | $fps |
| XR-fejl i log | $(if ($xrErrors) { "JA - se nedenfor" } else { "nej" }) |
| Crash | $(if ($crash) { "JA - se nedenfor" } else { "nej" }) |

**Automatisk vurdering: $verdict**

Dette er maskinens aflaesning af logcat. **Bekraeft selv i headsettet:** startede
den immersivt og ikke som fladt panel, og blev den graa kube staaende, da du gik?
Kuben er den egentlige trackingtest - loggen kan kun se, om der kom positionsdata.

## Logcat (relevante linjer)

``````
$(($lines | Where-Object { $_ -match "OenM0a|XR_ERROR|AndroidRuntime|FATAL" } | Select-Object -First 40) -join "`n")
``````

Fuld log: ``$log``
"@ | Set-Content $out -Encoding UTF8

Write-Host "`nSkrevet: $out" -ForegroundColor Green
Write-Host "Send den fil - saa udfylder jeg RESULTAT.md og ADR-019." -ForegroundColor Green
