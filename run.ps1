# OreSight Quick Start Script
# Starts both backend and frontend servers

Write-Host "🚀 Starting OreSight Full Stack Application" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

# Check if dependencies are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Cyan

$backendCheck = python -c "import fastapi, uvicorn; print('ok')" 2>$null
$frontendCheck = Test-Path "frontend/node_modules"

if ($backendCheck -ne "ok") {
    Write-Host "❌ Backend dependencies not installed!" -ForegroundColor Red
    Write-Host "   Run: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

if (-not $frontendCheck) {
    Write-Host "❌ Frontend dependencies not installed!" -ForegroundColor Red
    Write-Host "   Run: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Dependencies OK" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "📊 Starting Backend API Server..." -ForegroundColor Cyan
Write-Host "   Port: 8000" -ForegroundColor Gray
Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '📊 Backend API Server' -ForegroundColor Cyan; Write-Host ''; uvicorn app.main:app --reload --port 8000"

# Wait for backend to start
Write-Host "   Waiting for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Check if backend is up
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 2>$null
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Backend may still be starting..." -ForegroundColor Yellow
}

Write-Host ""

# Start Frontend
Write-Host "🎨 Starting Frontend Dev Server..." -ForegroundColor Cyan
Write-Host "   Port: 5173" -ForegroundColor Gray
Write-Host "   URL: http://localhost:5173" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '🎨 Frontend Dev Server' -ForegroundColor Cyan; Write-Host ''; npm run dev"

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host "✅ OreSight is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "📊 Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop the servers." -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 Ready for demo!" -ForegroundColor Green
