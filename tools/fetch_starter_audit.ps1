param(
    [string]$Cache = (Join-Path $env:TEMP 'ForeverRested-StarterAudit'),
    [int]$BatchSize = 16,
    [int]$DelayMilliseconds = 2000
)
$ErrorActionPreference = 'Stop'
if ($BatchSize -lt 1 -or $DelayMilliseconds -lt 1000) { throw 'Use a positive batch size and at least one second between requests.' }
$starterEntities = Get-Content -LiteralPath (Join-Path $Cache 'entities.json') -Raw | ConvertFrom-Json
$starterFetched = 0
$starterRemaining = 0
foreach ($starterEntity in $starterEntities) {
    if ($starterEntity.kind -notin @('quest','npc','item') -or $starterEntity.id -notmatch '^\d+$') { throw 'Invalid entity manifest' }
    $starterTarget = Join-Path $Cache "$($starterEntity.kind)-$($starterEntity.id).html"
    if (Test-Path -LiteralPath $starterTarget) { continue }
    $starterRemaining++
    if ($starterFetched -ge $BatchSize) { continue }
    Start-Sleep -Milliseconds $DelayMilliseconds
    try {
        Invoke-WebRequest -Uri "https://www.wowhead.com/forever/$($starterEntity.kind)=$($starterEntity.id)" -UserAgent 'Mozilla/5.0' -TimeoutSec 20 -OutFile "$starterTarget.download"
        Move-Item -LiteralPath "$starterTarget.download" -Destination $starterTarget -Force
        $starterFetched++
    } catch {
        Write-Output "Stopped after $starterFetched successful requests: $($starterEntity.kind) $($starterEntity.id): $($_.Exception.Message)"
        exit 1
    }
}
Write-Output "Fetched $starterFetched entity pages; $($starterRemaining - $starterFetched) remain."
