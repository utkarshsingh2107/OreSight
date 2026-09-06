# OreSight — खनिज दृष्टि

A complete reserve-to-production digital twin for MOIL's manganese mining operations,
built for Smart India Hackathon 2026. Covers a single mine (Balaghat) end-to-end:
satellite-enhanced prospectivity mapping, probabilistic production forecasting, dynamic
reserve accessibility modeling (EAR), data-driven action recommendations, and PDF report generation.

**Quick reference:**
- `QUICK_START_GUIDE.md` — comprehensive setup and feature walkthrough
- `API_CONTRACT.md` — complete API reference with TypeScript types
- `DATA_SOURCES.md` — data provenance
- `docs/domain-glossary.md` — mining terminology and sourced domain facts
- `docs/minimum-working-demo.md` — feature specifications
- `OreSight_SIH_Blueprint.md` — full original research and design document

---

## Features

### Prospectivity Mapping
- Random Forest model trained on Sentinel-2 satellite data — **AUC 0.936**
- Top-10 exploration targets ranked by mineral potential, exported as GeoJSON
- Feature importance: distance to known mines (78%), SWIR ratio (8%), clay index (5%)
- Interactive map panel with target details and satellite feature breakdown

### Satellite-Enhanced Production Forecasting
- LightGBM quantile regression with **17 features** including live Earth Observation data
- P10 / P50 / P90 probabilistic output with confidence fan chart
- SHAP driver attribution — separates weather, equipment, and operational contributions
- Rainfall what-if slider for instant scenario testing

### Dynamic Reserve Accessibility (EAR)
- Converts geological reserves to operationally accessible tonnage
- **4 adjustment factors:** depth, equipment capability, climate, infrastructure
- Baseline: 22 M t geological → 11.9 M t EAR (54.1% accessible)
- What-if scenarios: +1 LHD (+1.3 M t), heavier monsoon (+827 K t), longer haul (+343 K t)

### Data-Driven Recommendations
- Greedy optimization ranking corrective actions by expected shortfall reduction
- Covers equipment, workforce, operational, and planning categories
- Full audit trail: applied actions logged with timestamp and projected impact
- One-click PDF monthly report generation

### Dashboard
- Leaflet map with mine locations and prospectivity targets
- KPI cards: MTD actual vs target, shortfall probability
- Production history chart with rainfall overlay (3 166 daily records)
- Live weather widget, validation metrics, and methodology modal
- Data honesty badge — always visible, discloses what is real vs synthetic

---

## What is real vs synthetic

| Data | Status |
|---|---|
| Balaghat coordinates, depth, strike length, mine type | ✅ Real — MOIL / GSI public sources |
| Daily rainfall 2018 → present | ✅ Real — Open-Meteo / ERA5 reanalysis |
| Sentinel-2 spectral indices (NDVI, SWIR, clay, iron oxide) | ✅ Real — calculated from ESA Copernicus imagery |
| SRTM digital elevation model | ✅ Real — NASA |
| MOIL company-level annual production totals | ✅ Real — public disclosures (see `docs/domain-glossary.md`) |
| Balaghat's daily production series | 🔶 Synthetic — calibrated to illustrative monthly figures |
| 3D block model / reserve tonnage | 🔶 Synthetic — geometry calibrated to real facts, **not a MOIL reserve statement** |
| Equipment events and maintenance logs | 🔶 Synthetic — follows realistic operational patterns |

The dashboard's data honesty badge restates this at all times.

---

## Prerequisites

- Python 3.11+ (tested on 3.13)
- Node.js 18+ and npm (tested on Node 24)
- No Docker, no PostgreSQL — SQLite and local files only
- Internet only needed for initial dependency install and optional data refresh

---

## One-time setup

### 1. Backend

**Windows (PowerShell):**
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cd ..
```

### 2. Frontend

```bash
cd frontend
npm install
cd ..
```

### 3. Seed the database

Pre-generated data is already committed in `data/processed/` and `data/synthetic/`,
so you can go straight to step 3d unless you want to regenerate from scratch.

**Windows:**
```powershell
# 3a. (optional, needs internet) Re-fetch real rainfall
py scripts\prepare_rainfall.py

# 3b. (optional) Regenerate synthetic production/equipment data
py scripts\generate_synthetic.py

# 3c. (optional) Regenerate 3D block model and grade-tonnage curve
.\backend\.venv\Scripts\python.exe ml\prism\blockmodel.py

# 3d. Required — load everything into SQLite
.\backend\.venv\Scripts\python.exe scripts\seed.py
```

**macOS / Linux:**
```bash
python3 scripts/prepare_rainfall.py   # optional
python3 scripts/generate_synthetic.py # optional
./backend/.venv/bin/python ml/prism/blockmodel.py  # optional
./backend/.venv/bin/python scripts/seed.py          # required
```

`seed.py` is idempotent — safe to re-run. It also powers the in-app **Reset demo** button.

---

## Running the app

Open two terminals.

**Terminal 1 — backend:**

```bash
# Windows
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000

# macOS / Linux
cd backend
./.venv/bin/python -m uvicorn app.main:app --port 8000
```

Verify: `http://127.0.0.1:8000/health` → `{"status":"ok"}`
Interactive API docs: `http://127.0.0.1:8000/docs`

**Terminal 2 — frontend:**

```bash
cd frontend
npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`). Vite proxies `/api/*` to the backend.

---

## Quick API test

```bash
# List mines
curl http://127.0.0.1:8000/api/mines

# KPI
curl http://127.0.0.1:8000/api/mines/1/kpi

# Forecast
curl -X POST http://127.0.0.1:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{"mine_id":1,"horizon_days":30}'

# Prospectivity targets
curl "http://127.0.0.1:8000/api/prospectivity/targets?mine_id=1"

# EAR breakdown
curl "http://127.0.0.1:8000/api/ear/breakdown?mine_id=1"
```

All should return JSON without errors.

---

## Resetting to clean state

Click **Reset demo** in the app header, or:

```bash
curl -X POST http://127.0.0.1:8000/api/admin/reset-demo
```

This reloads all production, equipment, and audit data from the source CSVs.

---

## Project structure

```
OreSight/
├── README.md
├── QUICK_START_GUIDE.md                # Setup + feature walkthrough
├── API_CONTRACT.md                     # Full API reference with TypeScript types
├── DATA_SOURCES.md                     # Data provenance and attribution
├── OreSight_SIH_Blueprint.md           # Original research and design document
├── docs/
│   ├── domain-glossary.md              # Mining terminology and domain facts
│   └── minimum-working-demo.md         # Feature specifications
├── data/
│   ├── processed/                      # Rainfall CSV, reserve JSON, prospectivity data
│   ├── synthetic/                      # Generated production & equipment CSVs
│   ├── satellite/                      # Sentinel-2, DEM, geological indices (GeoTIFF)
│   ├── geology/                        # Mine locations, training labels (GeoJSON)
│   └── eo_constraints/                 # Earth observation constraints and forecasts
├── ml/
│   ├── prism/
│   │   ├── prospectivity.py            # Random Forest prospectivity model (AUC 0.936)
│   │   ├── blockmodel.py               # 3D block model and grade-tonnage curves
│   │   └── features.py                 # Satellite feature extraction
│   ├── pulse/
│   │   └── forecast.py                 # LightGBM quantile regression + SHAP
│   ├── reserves/
│   │   └── ear_calculator.py           # Dynamic EAR modelling
│   └── earth_observation/
│       └── constraints.py              # NDVI, temperature, soil moisture pipeline
├── scripts/
│   ├── prepare_rainfall.py             # Download and convert ERA5 rainfall
│   ├── generate_synthetic.py           # Generate production/equipment data
│   └── seed.py                         # Load everything into SQLite (= reset)
├── backend/
│   ├── requirements.txt
│   ├── oresight.db                     # SQLite database
│   └── app/
│       ├── main.py                     # FastAPI app + CORS + router registration
│       ├── database.py                 # SQLAlchemy engine/session
│       ├── models.py                   # ORM models
│       ├── schemas.py                  # Pydantic schemas
│       └── routers/
│           ├── mines.py                # Mine metadata and KPIs
│           ├── production.py           # Historical production data
│           ├── forecast.py             # Probabilistic forecasting
│           ├── prospectivity.py        # Exploration targets
│           ├── reserve.py              # Reserve and EAR analysis
│           ├── actions.py              # Action suggestions and audit trail
│           ├── reports.py              # PDF report generation
│           ├── weather.py              # Live weather data
│           └── admin.py                # Reset demo endpoint
└── frontend/
    ├── package.json
    ├── vite.config.ts                  # API proxy to backend
    └── src/
        ├── api/client.ts               # Typed Axios API client
        ├── pages/Dashboard.tsx         # Main dashboard
        └── components/
            ├── MapView.tsx             # Leaflet map — mines and targets
            ├── KpiCards.tsx            # KPI display
            ├── ProductionChart.tsx     # Production + rainfall overlay
            ├── ForecastPanel.tsx       # Fan chart + what-if slider
            ├── ProspectivityPanel.tsx  # Exploration targets
            ├── ReservePanel.tsx        # EAR breakdown + scenarios
            ├── ActionsPanel.tsx        # Action suggestions and application
            ├── LiveWeatherWidget.tsx   # Current conditions
            ├── EOConstraintsPanel.tsx  # Satellite constraints
            ├── DataHonestyBadge.tsx    # Data disclosure
            ├── ValidationMetrics.tsx   # Model metrics
            └── MethodologyModal.tsx    # Technical methodology
```

---

## API reference

Full interactive docs at `http://127.0.0.1:8000/docs`. For complete schemas and TypeScript types see `API_CONTRACT.md`.

### Mines
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/mines` | List all mines |
| GET | `/api/mines/{id}` | Mine metadata |
| GET | `/api/mines/{id}/kpi` | MTD actual vs target, shortfall probability |
| GET | `/api/mines/{id}/production?days=N` | Daily production history |

### Forecasting
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/forecast` | P10/P50/P90 forecast + SHAP drivers — body: `{mine_id, horizon_days, rainfall_override_mm?}` |

### Prospectivity
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/prospectivity/targets?mine_id={id}` | Top-10 exploration targets |
| GET | `/api/prospectivity/features/{target_id}` | Feature breakdown for one target |
| GET | `/api/prospectivity/features` | All targets with features |

### Reserve / EAR
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/mines/{id}/reserve` | EAR, grade-tonnage curve, block model image URL |
| GET | `/api/ear/breakdown?mine_id={id}` | EAR breakdown by accessibility factor |
| POST | `/api/ear/what-if` | Test equipment / climate / infrastructure scenarios |

### Actions
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/mines/{id}/suggest-actions` | Ranked corrective actions |
| POST | `/api/mines/{id}/apply-action` | Apply action — creates audit log entry |
| GET | `/api/mines/{id}/audit-log` | Applied actions history |

### Reports & Admin
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/mines/{id}/report.pdf` | Generate PDF monthly report |
| POST | `/api/admin/reset-demo` | Wipe and reload demo data |
| GET | `/api/health` | Health check |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'ml'`**
Run uvicorn with the venv Python (`./backend/.venv/...`), not system Python. The routers add the repo root to `sys.path` on import.

**numpy / lightgbm build errors on install**
Upgrade to Python 3.11+ to get prebuilt wheels. Let pip resolve versions — don't pin old packages.

**"No mines seeded yet"**
Run `scripts/seed.py` with the backend venv Python. Verify `backend/oresight.db` exists.

**Forecast returns 400 "Not enough production history"**
Database not seeded or was wiped. Run `scripts/seed.py`.

**First forecast call takes ~2 s**
Models are trained on first call per mine. Subsequent calls use the cached model and respond in under 1 s.

**Frontend "Could not reach API"**
Backend must be running. Test directly: `curl http://127.0.0.1:8000/api/mines`. Check Vite proxy in `frontend/vite.config.ts`.

**Map tiles not loading**
Requires internet (tiles served by OpenStreetMap). Mine geometry and targets come from local GeoJSON files.

---

## Tech stack

| Layer | Libraries |
|-------|-----------|
| API | FastAPI 0.115+, Uvicorn |
| ORM / DB | SQLAlchemy 2.0+, SQLite 3 |
| ML | LightGBM 4.5+, scikit-learn 1.5+, SHAP 0.46+ |
| Geo / Raster | rasterio 1.4+, geopandas 1.0+, shapely |
| Reports | ReportLab 4.2+ |
| Frontend | React 19, TypeScript 5.6+, Vite 8.2+ |
| Charts / Map | Recharts 2.15+, Leaflet 1.9+ |
| HTTP | Axios 1.7+ |
| Styles | Tailwind CSS 4.0+ |

---

## Acknowledgments

- **MOIL** — public mine data and domain context
- **Geological Survey of India (GSI)** — geological data
- **ESA Copernicus** — Sentinel-2 satellite imagery
- **NASA** — SRTM elevation data
- **Open-Meteo / ERA5** — historical rainfall
- **Smart India Hackathon 2026** — problem statement
