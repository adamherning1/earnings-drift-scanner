$src = 'C:\Users\adamh\.openclaw\workspace'
$dst = 'C:\Users\adamh\.openclaw\workspace\backtester\workspace'
New-Item -ItemType Directory -Force -Path $dst | Out-Null
New-Item -ItemType Directory -Force -Path "$dst\memory" | Out-Null

$files = @('SOUL.md','USER.md','IDENTITY.md','AGENTS.md','MEMORY.md','TOOLS.md','HEARTBEAT.md')
foreach ($f in $files) {
    $p = Join-Path $src $f
    if (Test-Path $p) { Copy-Item $p $dst -Force; Write-Host "Copied $f" }
}

$memSrc = Join-Path $src 'memory'
if (Test-Path $memSrc) {
    Get-ChildItem $memSrc -Filter '*.md' | ForEach-Object {
        Copy-Item $_.FullName "$dst\memory" -Force
        Write-Host "Copied memory/$($_.Name)"
    }
}

Set-Location 'C:\Users\adamh\.openclaw\workspace\backtester'
git add .
git commit -m 'daily backup' 2>&1
git push 2>&1
