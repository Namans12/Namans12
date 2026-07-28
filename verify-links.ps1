<#
.SYNOPSIS
    Checks every remote asset referenced by README.md actually loads.

.DESCRIPTION
    A profile README is mostly third-party image services. When one of them
    goes down - and they do; the official github-readme-stats instance is
    paused as of this writing - your profile silently fills with broken-image
    icons and you are the last person to find out.

    This script pulls every https:// URL out of README.md, requests each one,
    and reports anything that is not a healthy image response.

.EXAMPLE
    .\verify-links.ps1
    .\verify-links.ps1 -Path .\README.md -TimeoutSec 40
#>

[CmdletBinding()]
param(
    [string] $Path       = (Join-Path $PSScriptRoot 'README.md'),
    # 60s, not 30: streak-stats.demolab.com regularly takes 15-20 seconds and
    # sometimes longer. A short timeout reports a working service as broken.
    [int]    $TimeoutSec = 60
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Error "No README found at $Path"
    exit 2
}

$content = Get-Content -LiteralPath $Path -Raw

# Strip HTML comments first. Disabled modules and their placeholder URLs
# (YOUR_WAKATIME_USER, the paused trophy service, and so on) live in comments
# and are not rendered by GitHub, so checking them only produces noise.
$live = [regex]::Replace($content, '(?s)<!--.*?-->', '')

# Pull URLs out of markdown images, HTML src/srcset/href, and bare links.
# Trailing markdown punctuation is trimmed so ")" and "," don't poison the URL.
$urls = [regex]::Matches($live, 'https://[^\s"''<>)\]]+') |
    ForEach-Object { $_.Value.TrimEnd('.', ',', ';', ':') } |
    Select-Object -Unique |
    Sort-Object

# Sites that answer automated requests with a refusal but load perfectly in a
# browser. A non-200 from these proves nothing, so report rather than fail.
$botBlocked = @(
    @{ Pattern = 'linkedin\.com';  Codes = @(999, 403, 429) }
    @{ Pattern = 'codepen\.io';    Codes = @(403, 503) }
    @{ Pattern = 'twitter\.com|x\.com'; Codes = @(403, 400) }
    @{ Pattern = 'discord\.com';   Codes = @(403) }
    @{ Pattern = 'vercel\.app';    Codes = @(429) }
)

function Test-ValidXml {
    param([string] $Content)
    if ([string]::IsNullOrWhiteSpace($Content)) { return $false }
    try {
        $settings = New-Object System.Xml.XmlReaderSettings
        $settings.DtdProcessing = [System.Xml.DtdProcessing]::Ignore
        $settings.XmlResolver = $null
        $reader = [System.Xml.XmlReader]::Create(
            (New-Object System.IO.StringReader $Content), $settings)
        while ($reader.Read()) { }
        $reader.Close()
        return $true
    }
    catch { return $false }
}

function Test-BotBlocked {
    param([string] $Url, [string] $Message)
    foreach ($rule in $botBlocked) {
        if ($Url -match $rule.Pattern) {
            foreach ($code in $rule.Codes) {
                if ($Message -match "\b$code\b") { return $true }
            }
        }
    }
    return $false
}

Write-Host ""
Write-Host "Checking $($urls.Count) unique URLs from $Path" -ForegroundColor Cyan
Write-Host ("-" * 78)

$failures = New-Object System.Collections.Generic.List[object]
$warnings = New-Object System.Collections.Generic.List[object]

foreach ($url in $urls) {
    $short = if ($url.Length -gt 68) { $url.Substring(0, 65) + '...' } else { $url }

    try {
        # GET rather than HEAD: several of these services (shields.io,
        # skillicons) answer HEAD inconsistently or not at all.
        $resp = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec $TimeoutSec -ErrorAction Stop
        $type = ($resp.Headers.'Content-Type' -join ',')
        $size = $resp.RawContentLength

        if ($resp.StatusCode -ne 200) {
            $failures.Add([pscustomobject]@{ Url = $url; Reason = "HTTP $($resp.StatusCode)" })
            Write-Host ("  [{0}] {1}" -f $resp.StatusCode, $short) -ForegroundColor Red
        }
        elseif ($size -lt 200) {
            # A 200 with almost no body usually means the service returned an
            # error card rather than a real image.
            $warnings.Add([pscustomobject]@{ Url = $url; Reason = "suspiciously small ($size bytes)" })
            Write-Host ("  [thin] {0}  ({1} bytes)" -f $short, $size) -ForegroundColor Yellow
        }
        elseif ($type -match 'svg' -and -not (Test-ValidXml $resp.Content)) {
            # An SVG that isn't well-formed XML still returns 200, but browsers
            # refuse to draw it - the image silently disappears. This bites when a
            # badge service interpolates your text without escaping it: a literal
            # "&" in a title or description is enough to kill the whole graphic.
            $failures.Add([pscustomobject]@{
                Url    = $url
                Reason = 'SVG is not well-formed XML - browsers will not render it (usually an unescaped "&" in your text)'
            })
            Write-Host ("  [XML!] {0}" -f $short) -ForegroundColor Red
        }
        else {
            Write-Host ("  [ ok ] {0}" -f $short) -ForegroundColor DarkGray
        }
    }
    catch {
        $msg = $_.Exception.Message
        # raw.githubusercontent 404s are expected before the snake workflow
        # has run for the first time, so flag them separately.
        if ($url -match 'raw\.githubusercontent\.com/.+/output/') {
            $warnings.Add([pscustomobject]@{ Url = $url; Reason = 'snake output branch not built yet - run the workflow' })
            Write-Host ("  [pend] {0}" -f $short) -ForegroundColor Yellow
        }
        elseif ($url -match 'raw\.githubusercontent\.com/Namans12/Namans12/|github\.com/Namans12/Namans12/blob/') {
            # Files committed locally but not pushed yet. These 404 until the
            # push lands, which is expected rather than broken.
            $warnings.Add([pscustomobject]@{ Url = $url; Reason = 'repo asset not pushed yet - will resolve after git push' })
            Write-Host ("  [pend] {0}" -f $short) -ForegroundColor Yellow
        }
        elseif ($msg -match '\b429\b') {
            # Too Many Requests never means broken - it means this checker has
            # been hitting the host too fast. Report it, don't fail on it.
            $warnings.Add([pscustomobject]@{ Url = $url; Reason = 'rate limited (HTTP 429) - re-check later or open it in a browser' })
            Write-Host ("  [429 ] {0}" -f $short) -ForegroundColor DarkYellow
        }
        elseif (Test-BotBlocked -Url $url -Message $msg) {
            $warnings.Add([pscustomobject]@{ Url = $url; Reason = 'site refuses bots - verify manually in a browser' })
            Write-Host ("  [bot ] {0}" -f $short) -ForegroundColor DarkYellow
        }
        else {
            $failures.Add([pscustomobject]@{ Url = $url; Reason = $msg })
            Write-Host ("  [FAIL] {0}" -f $short) -ForegroundColor Red
            Write-Host ("         {0}" -f $msg) -ForegroundColor DarkRed
        }
    }
}

Write-Host ("-" * 78)

if ($warnings.Count) {
    Write-Host ""
    Write-Host "$($warnings.Count) warning(s):" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host ("  - {0}`n      {1}" -f $_.Reason, $_.Url) -ForegroundColor Yellow }
}

if ($failures.Count) {
    Write-Host ""
    Write-Host "$($failures.Count) broken link(s):" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host ("  - {0}`n      {1}" -f $_.Reason, $_.Url) -ForegroundColor Red }
    Write-Host ""
    Write-Host "See SETUP.md -> 'When a card stops rendering' for the fix." -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "All $($urls.Count) links healthy." -ForegroundColor Green
exit 0
