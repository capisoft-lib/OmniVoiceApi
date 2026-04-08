# Deploy pre-built image to a remote Linux host over SSH.
# Requires: OpenSSH client, SSH access (key recommended), Docker + NVIDIA Container Toolkit on the host.
#
# Usage:
#   pwsh -File infra/docker/deploy-remote.ps1 -SshTarget 'user@10.1.200.10'
#
# The remote user must run Docker (member of group `docker`) or have passwordless sudo for docker.

param(
    [Parameter(Mandatory = $true)]
    [string] $SshTarget
)

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot "remote-docker-run.sh"

if (-not (Test-Path $scriptPath)) {
    throw "Missing $scriptPath"
}

Write-Host "Copying remote-docker-run.sh to ${SshTarget}:/tmp/ ..."
scp $scriptPath "${SshTarget}:/tmp/omnivoice-remote-docker-run.sh"

Write-Host "Running install on remote ..."
ssh $SshTarget "chmod +x /tmp/omnivoice-remote-docker-run.sh && sudo bash /tmp/omnivoice-remote-docker-run.sh"
