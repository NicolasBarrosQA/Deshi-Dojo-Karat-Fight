$ErrorActionPreference = 'Stop'
$gameRootPath = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path)
$gamePrefix = $gameRootPath.TrimEnd('\') + '\'
$backup = Get-Content -Raw -LiteralPath (Join-Path $gameRootPath 'docs/avatar-set-v3/legacy-art-backup.json') | ConvertFrom-Json
if (-not $gameRootPath.Equals([IO.Path]::GetFullPath($backup.game_root), [StringComparison]::OrdinalIgnoreCase)) { throw 'Backup belongs to a different checkout.' }
if (-not (Test-Path -LiteralPath $backup.archive)) { throw 'Recoverable backup missing.' }
$keepNames = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
function Keep-Part($part) { [void]$keepNames.Add($part.right + '.png'); [void]$keepNames.Add($part.left + '.png') }
$base = Get-Content -Raw -LiteralPath (Join-Path $gameRootPath 'assets/character-assets.json') | ConvertFrom-Json
foreach ($body in $base.PSObject.Properties) { foreach ($layer in $body.Value.parts.PSObject.Properties) { foreach ($variant in $layer.Value.PSObject.Properties) { Keep-Part $variant.Value } } }
$special = Get-Content -Raw -LiteralPath (Join-Path $gameRootPath 'assets/special-assets.json') | ConvertFrom-Json
foreach ($body in $special.PSObject.Properties) { foreach ($group in $body.Value.PSObject.Properties) { Keep-Part $group.Value.body; foreach ($belt in $group.Value.belts.PSObject.Properties) { Keep-Part $belt.Value } } }
$removed = @(); $changed = @(); $parents = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($entry in $backup.files) {
    if (-not $entry.cleanup_candidate -or -not (Test-Path -LiteralPath $entry.path -PathType Leaf)) { continue }
    $resolved = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $entry.path).Path)
    if (-not $resolved.StartsWith($gamePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw "Cleanup escaped game directory: $resolved" }
    if ($resolved.StartsWith((Join-Path $gameRootPath 'src/assets') + '\', [StringComparison]::OrdinalIgnoreCase) -and $keepNames.Contains([IO.Path]::GetFileName($resolved))) { continue }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash -ne $entry.sha256) { $changed += $resolved; continue }
    Remove-Item -LiteralPath $resolved
    $removed += $resolved
    [void]$parents.Add([IO.Path]::GetDirectoryName($resolved))
}
foreach ($directory in ($parents | Sort-Object Length -Descending)) {
    if ($directory.StartsWith($gamePrefix, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $directory -PathType Container) -and @(Get-ChildItem -LiteralPath $directory -Force).Count -eq 0) { Remove-Item -LiteralPath $directory }
}
@{ removed_files = $removed; retained_changed_files = $changed; archive = $backup.archive; root_verified = $gameRootPath } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $gameRootPath 'docs/avatar-set-v3/legacy-cleanup.json') -Encoding utf8
Write-Output "Removed $($removed.Count) unchanged legacy files; preserved new referenced images and modified files. Backup: $($backup.archive)"
