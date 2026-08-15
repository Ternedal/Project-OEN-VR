<#
  Authoritative on-machine production-art verification wrapper.

  Guarantees that a green review-art-verification.json identifies the exact named
  Git branch and clean commit whose production-art files were copied into Unity.
#>

param(
    [Parameter(Mandatory = $true)][string]$UnityPath,
    [string]$ProjectPath = "$PSScriptRoot\..\..\..\ProjektOenApp",
    [switch]$OpenEditor
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git er paakraevet for en sporbar Unity-verifikation."
}

$repo = (Resolve-Path "$PSScriptRoot\..\..").Path
$reviewScript = Join-Path $PSScriptRoot "Review-ProductionArt.ps1"
if (-not (Test-Path $reviewScript)) { throw "Review-script mangler: $reviewScript" }

$sourceSha = (& git -C $repo rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $sourceSha -notmatch '^[0-9a-fA-F]{40}$') {
    throw "Kunne ikke fastslaa en gyldig 40-tegns Git SHA for $repo."
}

$sourceBranch = (& git -C $repo rev-parse --abbrev-ref HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($sourceBranch) -or $sourceBranch -eq "HEAD") {
    throw "On-machine art-verifikation skal koeres fra en navngivet Git branch."
}

$trackedScope = @(
    "Assets/ProductionArt",
    "src/unity/ProjectOen.Art",
    "prototype/m0b-bootstrap/Review-ProductionArt.ps1",
    "prototype/m0b-bootstrap/Verify-ProductionArt.ps1"
)
$dirty = @(& git -C $repo status --porcelain -- @trackedScope)
if ($LASTEXITCODE -ne 0) { throw "git status fejlede for production-art verification scope." }
if ($dirty.Count -gt 0) {
    Write-Host "Production-art verification afvist: source scope er ikke clean." -ForegroundColor Red
    $dirty | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
    throw "Commit eller ryd production-art aendringer foer fysisk Unity-verifikation, saa rapportens SHA er autoritativ."
}

Write-Host "`n== Source identity ==" -ForegroundColor Cyan
Write-Host "Branch: $sourceBranch" -ForegroundColor Green
Write-Host "SHA:    $sourceSha" -ForegroundColor Green

& $reviewScript -UnityPath $UnityPath -ProjectPath $ProjectPath -OneShot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$reportPath = Join-Path $PSScriptRoot "review-art-verification.json"
$projectReportPath = Join-Path (Resolve-Path $ProjectPath).Path "ProjectOEN-ArtVerification.json"
if (-not (Test-Path $reportPath)) { throw "One-shot rapport mangler efter groen Unity-koersel: $reportPath" }

$report = Get-Content $reportPath -Raw | ConvertFrom-Json
if ($report.status -ne "PASS" -or [int]$report.failed -ne 0) {
    throw "Kun PASS/0-fail Unity-rapporter maa source-stemples."
}

$report | Add-Member -NotePropertyName sourceBranch -NotePropertyValue $sourceBranch -Force
$report | Add-Member -NotePropertyName sourceSha -NotePropertyValue $sourceSha.ToLowerInvariant() -Force
$report | Add-Member -NotePropertyName sourceWorktreeClean -NotePropertyValue $true -Force
$report | Add-Member -NotePropertyName sourceStampedUtc -NotePropertyValue ([DateTime]::UtcNow.ToString("O")) -Force
$report | Add-Member -NotePropertyName sourceStampTool -NotePropertyValue "Verify-ProductionArt.ps1" -Force

$json = $report | ConvertTo-Json -Depth 10
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($reportPath, $json, $utf8NoBom)
[System.IO.File]::WriteAllText($projectReportPath, $json, $utf8NoBom)

$roundTrip = Get-Content $reportPath -Raw | ConvertFrom-Json
if ($roundTrip.sourceSha -ne $sourceSha.ToLowerInvariant() -or $roundTrip.sourceBranch -ne $sourceBranch -or -not $roundTrip.sourceWorktreeClean) {
    throw "Source-stemplet verification-rapport bestod ikke round-trip kontrol."
}

Write-Host "`nPASS: Unity-art rapport er bundet til $sourceBranch@$sourceSha" -ForegroundColor Green
Write-Host "Rapport: $reportPath" -ForegroundColor Green

if ($OpenEditor) {
    $args = @("-projectPath", (Resolve-Path $ProjectPath).Path, "-executeMethod", "ProjectOen.Art.Editor.ProductionArtReviewMenu.OpenShowcase")
    Start-Process -FilePath $UnityPath -ArgumentList $args | Out-Null
}
