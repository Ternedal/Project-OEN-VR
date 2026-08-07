# M0a — byg og installer smoke-APK'en
#
# Bygger IKKE selv (det kræver Unity Editor). Den tager en APK, du allerede har
# bygget fra File > Build Profiles, og installerer + logger den.
#
# Brug:
#   .\build_and_install.ps1 -Apk .\OenM0aSmoke.apk
#   .\build_and_install.ps1 -Apk .\OenM0aSmoke.apk -Serial 1WMHH000X00000

param(
    [Parameter(Mandatory = $true)][string]$Apk,
    [string]$Serial = "",
    [string]$Adb = "adb"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Apk)) { throw "APK ikke fundet: $Apk" }

$target = @()
if ($Serial -ne "") { $target = @("-s", $Serial) }

Write-Host "== Tilsluttede enheder ==" -ForegroundColor Cyan
& $Adb devices -l

Write-Host "`n== Enhed ==" -ForegroundColor Cyan
$model = (& $Adb @target shell getprop ro.product.model) -join ""
$device = (& $Adb @target shell getprop ro.product.device) -join ""
$os = (& $Adb @target shell getprop ro.build.version.release) -join ""
Write-Host "model=$model device=$device android=$os"
# Til reference: Quest 1 = 'Quest', Quest 2 = 'Quest 2', Quest 3 = 'Quest 3'

Write-Host "`n== Installerer ==" -ForegroundColor Cyan
& $Adb @target install -r $Apk
if ($LASTEXITCODE -ne 0) { throw "adb install fejlede med kode $LASTEXITCODE - noter fejlteksten ordret i RESULTAT.md" }

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$safe = ($model -replace '[^\w]', '_')
$log = "m0a-$safe-$stamp.log"

Write-Host "`n== Rydder log. Tag headsettet paa og start appen fra 'Ukendte kilder'. ==" -ForegroundColor Yellow
& $Adb @target logcat -c

Write-Host "Logger til $log. Ctrl+C naar du har aflaest HUD'en (giv den ca. 30 sek)." -ForegroundColor Yellow
& $Adb @target logcat -s Unity:V OenM0a:V CRASH:V AndroidRuntime:E | Tee-Object -FilePath $log

Write-Host "`nLog gemt: $log - vedhaeft den i RESULTAT.md" -ForegroundColor Green
