Write-Host "Pine Time Admin Setup Script" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

# Clean install directory
Write-Host "Cleaning node_modules..." -ForegroundColor Yellow
if (Test-Path node_modules) {
    Remove-Item -Recurse -Force node_modules
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install --legacy-peer-deps

# Verify Vite installation
Write-Host "Verifying Vite installation..." -ForegroundColor Yellow
$vitePath = Join-Path -Path (Get-Location) -ChildPath "node_modules\.bin\vite.cmd"
if (-not (Test-Path $vitePath)) {
    Write-Host "Vite not found in node_modules\.bin - installing globally..." -ForegroundColor Red
    npm install -g vite@4.5.2
}

# Create .env file if it doesn't exist
Write-Host "Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env file from .env.example" -ForegroundColor Green
}

# Start development server
Write-Host "Starting development server..." -ForegroundColor Green
npm run dev

# This command will only run if npm run dev fails
if ($LASTEXITCODE -ne 0) {
    Write-Host "Attempting to start with global Vite..." -ForegroundColor Yellow
    vite
}
