$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDirectory = Split-Path -Parent $ScriptDirectory
$ProjectFile = Join-Path $ProjectDirectory "Sources/EstellePet.Windows/EstellePet.Windows.csproj"
$InstallGuide = Join-Path $ProjectDirectory "INSTALL.md"
$PublishDirectory = Join-Path $ProjectDirectory "dist/windows-x64"
$ReleaseDirectory = Join-Path $ProjectDirectory "release"
$ArchivePath = Join-Path $ReleaseDirectory "EstellePet-Windows-x64.zip"

if (Test-Path $PublishDirectory) {
    Remove-Item -Recurse -Force $PublishDirectory
}
New-Item -ItemType Directory -Force -Path $PublishDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $ReleaseDirectory | Out-Null

dotnet publish $ProjectFile `
    --configuration Release `
    --runtime win-x64 `
    --self-contained true `
    --output $PublishDirectory `
    -p:PublishSingleFile=true `
    -p:IncludeNativeLibrariesForSelfExtract=true `
    -p:DebugType=None `
    -p:DebugSymbols=false

Copy-Item $InstallGuide (Join-Path $PublishDirectory "INSTALL.md")

if (Test-Path $ArchivePath) {
    Remove-Item -Force $ArchivePath
}
Compress-Archive -Path (Join-Path $PublishDirectory "*") -DestinationPath $ArchivePath -CompressionLevel Optimal
Write-Output $ArchivePath
