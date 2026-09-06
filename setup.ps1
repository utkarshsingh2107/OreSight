# OreSight Setup Script
# Installs all dependencies for backend and frontend

Write-Host "🚀 OreSight Setup - Installing Dependencies" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Backend Setup
Write-Host "📊 Installing Backend Dependencies..." -ForegroundColor Cyan
Set-Location backend
Write-Host "   Using pip to install Python packages..." -ForegroundColor Gray
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Backend dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Backend installation failed. Check Python version (need 3.10+)" -ForegroundColor Red
}
Set-Location ..
Write-Host ""

# Frontend Setup
Write-Host "🎨 Installing Frontend Dependencies..." -ForegroundColor Cyan
Set-Location frontend
Write-Host "   Using npm to install Node packages..." -ForegroundColor Gray
npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Frontend dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Frontend installation failed. Check Node version (need 18+)" -ForegroundColor Red
}
Set-Location ..
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Seed the database: cd backend; python scripts/seed.py" -ForegroundColor Gray
Write-Host "2. Start backend: cd backend; uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "3. Start frontend: cd frontend; npm run dev" -ForegroundColor Gray
Write-Host "4. Open http://localhost:5173" -ForegroundColor Gray
Write-Host ""
Write-Host "Or use the quick start script: .\run.ps1" -ForegroundColor Cyan

