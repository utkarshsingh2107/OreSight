# 🚀 Start OreSight - Full Stack Application

This guide will help you start both the backend and frontend servers to run the complete OreSight application.

---

## ✅ Prerequisites Check

Before starting, ensure you have:

- [x] Python 3.10+ installed
- [x] Node.js 18+ installed
- [x] Git repository cloned
- [x] All dependencies installed

---

## 📦 Installation (First Time Only)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

**Key Dependencies**:
- FastAPI, Uvicorn (API server)
- SQLAlchemy, Psycopg2 (Database)
- Pandas, NumPy, Scikit-learn (Data processing)
- LightGBM, SHAP (ML models)
- Rasterio, GeoPandas (Geospatial)

### Frontend Setup

```bash
cd frontend
npm install
```

**Key Dependencies**:
- React 19, TypeScript
- Vite (dev server)
- Tailwind CSS 4
- Axios (API client)
- ECharts (charts)
- MapLibre GL (maps)

---

## 🚀 Quick Start (Recommended)

### Option 1: Run Both Servers (Separate Terminals)

**Terminal 1 - Backend**:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

Then open: **http://localhost:5173**

---

### Option 2: PowerShell Script (Windows)

Create `start-oresight.ps1`:

```powershell
# Start OreSight - Backend + Frontend

Write-Host "🚀 Starting OreSight..." -ForegroundColor Green

# Start Backend in background
Write-Host "`n📊 Starting Backend API..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --reload --port 8000"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Frontend in background
Write-Host "`n🎨 Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`n✅ OreSight is starting!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend UI: http://localhost:5173" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C in each terminal to stop." -ForegroundColor Gray
```

Run: `.\start-oresight.ps1`

---

## 🔍 Verify Everything is Working

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

### 2. Check API Endpoints

```bash
# Get all mines
curl http://localhost:8000/api/mines

# Get prospectivity targets
curl http://localhost:8000/api/prospectivity/targets

# Get EAR breakdown
curl http://localhost:8000/api/mines/1/ear/breakdown
```

### 3. Check Frontend

Open http://localhost:5173 in your browser

You should see:
- ✅ OreSight dashboard with mine selector
- ✅ KPI cards (Today's Production, MTD, Target, Risk)
- ✅ Map with mine location
- ✅ Production chart
- ✅ Reserve panel (block model + curve)
- ✅ Forecast panel
- ✅ Actions panel

---

## 📊 API Documentation

Once backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

This provides interactive API documentation with:
- All endpoints listed
- Request/response schemas
- "Try it out" functionality

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

---

**Error**: `Address already in use: 8000`

**Solution**: Kill existing process or use different port
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Update frontend vite.config.ts proxy:
# '/api': 'http://127.0.0.1:8001'
```

---

**Error**: `No mines seeded yet`

**Solution**: Seed the database
```bash
cd backend
python scripts/seed.py
```

---

### Frontend Won't Start

**Error**: `Cannot find module 'axios'`

**Solution**:
```bash
cd frontend
npm install
```

---

**Error**: `Port 5173 is already in use`

**Solution**: Vite will auto-increment to 5174, or specify port:
```bash
npm run dev -- --port 3000
```

---

**Error**: `CORS error` in browser console

**Solution**: Ensure backend is running and proxy is configured in `vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': 'http://127.0.0.1:8000',
  },
}
```

---

### API Errors

**Error**: `404 Not Found` for prospectivity endpoints

**Solution**: Ensure data files exist:
```bash
# Check files
ls data/processed/top_10_targets.geojson
ls data/processed/reserve_summary_balaghat.json
ls reports/prospectivity_metrics.json

# Regenerate if missing
python ml/prism/prospectivity.py
```

---

**Error**: `500 Internal Server Error`

**Solution**: Check backend terminal for error logs. Common issues:
- Missing data files
- Database not seeded
- Import errors

---

## 🎯 Testing the Full Application

### Test Checklist

**Dashboard**:
- [ ] KPI cards display correct numbers
- [ ] Map shows mine marker at correct location
- [ ] Production chart displays historical data

**Reserve Panel**:
- [ ] Block model image loads
- [ ] Total geological reserve shows 22.0M tonnes
- [ ] EAR shows ~11.9M tonnes (54.1% accessibility)
- [ ] Grade-tonnage curve displays correctly

**Forecast Panel**:
- [ ] Fan chart shows P10/P50/P90 curves
- [ ] Top drivers list appears with categories
- [ ] Rainfall slider changes forecast
- [ ] Shortfall probability displays

**Actions Panel**:
- [ ] "Suggest actions" button generates suggestions
- [ ] Actions can be applied
- [ ] Audit log updates after applying actions

---

## 📱 Production Build

When ready for production:

### Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
npm run preview
```

This creates an optimized production build in `frontend/dist/`.

---

## 🔧 Development Tips

### Hot Reload

Both servers support hot reload:
- **Backend**: Auto-reloads on Python file changes (via `--reload`)
- **Frontend**: Auto-reloads on TypeScript/React changes (via Vite HMR)

### Debugging

**Backend**:
- Add `print()` or `logger.debug()` statements
- Check terminal output for errors
- Use FastAPI's built-in validation errors

**Frontend**:
- Use browser DevTools (F12)
- Check Console for errors
- Check Network tab for API calls
- Use React DevTools extension

---

## 🌐 Ports Used

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Frontend Dev | 5173 | http://localhost:5173 |
| Frontend Prod | 4173 | http://localhost:4173 |

---

## 📚 Additional Resources

- **API Contract**: See `API_CONTRACT.md` for detailed endpoint specs
- **Person B Guide**: See `PERSON_B_API_GUIDE.md` for integration details
- **Completion Summary**: See `PERSON_A_COMPLETION_SUMMARY.md` for sprint overview
- **Data Sources**: See `DATA_SOURCES.md` for data documentation

---

## ✅ Ready to Demo!

Once both servers are running and tests pass:

1. **Open**: http://localhost:5173
2. **Select**: Balaghat mine (default)
3. **Explore**: All panels and features
4. **Test**: Rainfall slider, what-if scenarios
5. **Present**: Ready for judges! 🎯

---

**Good luck with your demo! 🚀**

*Questions? Check the troubleshooting section or review the API docs at /docs*
