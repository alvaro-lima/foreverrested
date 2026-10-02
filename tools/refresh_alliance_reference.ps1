param(
    [string]$Python = 'python',
    [switch]$UseCache
)
$ErrorActionPreference = 'Stop'
$addonRoot = Split-Path -Parent $PSScriptRoot
$referencePath = Join-Path $addonRoot 'Data/alliance-reference.json'
$reference = Get-Content -LiteralPath $referencePath -Raw | ConvertFrom-Json
$referenceCache = Join-Path $env:TEMP 'ForeverRested-RouteResearch'
New-Item -ItemType Directory -Path $referenceCache -Force | Out-Null
$fetches = @()
foreach ($property in $reference.quests.PSObject.Properties) {
    if ($property.Name -notmatch '^\d+$') { throw 'Invalid quest key in reference file' }
    $fetches += @{name="$($property.Name).html"; url="https://www.wowhead.com/forever/quest=$($property.Name)"}
}
foreach ($className in @('warrior','paladin','hunter','rogue','priest','shaman','mage','warlock','druid')) {
    $fetches += @{name="$className-list.html"; url="https://www.wowhead.com/forever/quests/classes/$className"}
}
$fetches += @(
    @{name='quests.html';url='https://www.wowhead.com/forever/quests/eastern-kingdoms/dun-morogh'},
    @{name='elwynn-list.html';url='https://www.wowhead.com/forever/quests/eastern-kingdoms/elwynn-forest'},
    @{name='teldrassil-list.html';url='https://www.wowhead.com/forever/quests/kalimdor/teldrassil'},
    @{name='zephras-list.html';url='https://www.wowhead.com/forever/zone=16593/zephras-isle'},
    @{name='westfall-list.html';url='https://www.wowhead.com/forever/quests/eastern-kingdoms/westfall'},
    @{name='loch-modan-list.html';url='https://www.wowhead.com/forever/quests/eastern-kingdoms/loch-modan'},
    @{name='darkshore-list.html';url='https://www.wowhead.com/forever/quests/kalimdor/darkshore'},
    @{name='redridge-mountains-list.html';url='https://www.wowhead.com/forever/quests/eastern-kingdoms/redridge-mountains'}
)
$index = 0
foreach ($fetch in $fetches) {
    $index++
    Write-Progress -Activity 'Refreshing public Forever references' -Status "$index / $($fetches.Count)" -PercentComplete ($index * 100 / $fetches.Count)
    $target = Join-Path $referenceCache $fetch.name
    if ($UseCache) { continue }
    # Failed fetches leave the loaded addon reference unchanged: compile only after every fetch succeeds.
    Invoke-WebRequest -Uri $fetch.url -OutFile "$target.download"
    Move-Item -LiteralPath "$target.download" -Destination $target -Force
}
Write-Progress -Activity 'Refreshing public Forever references' -Completed
& $Python (Join-Path $PSScriptRoot 'build_alliance_reference.py') --cache $referenceCache
if ($LASTEXITCODE -ne 0) { throw 'Reference compilation failed' }
Write-Output 'Reference refreshed. /reload in WoW to load it. Authored step IDs/order are preserved.'
