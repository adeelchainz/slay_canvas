param(
    [string]$name = "mediaboard-backend",
    [string]$private = "true",
    [string]$org = ""
)

# Requires gh CLI to be installed and authenticated
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI 'gh' not found in PATH. Install and authenticate before running this script."
    exit 1
}

$repoArgs = @($name)
if ($private -eq 'true') { $repoArgs += '--private' } else { $repoArgs += '--public' }
if ($org -ne '') { $repoArgs += '--org'; $repoArgs += $org }

gh repo create @repoArgs --confirm

git remote add origin "https://github.com/$(gh repo view --json owner -q .owner.login)/$name.git"

git branch -M main

git push -u origin main
