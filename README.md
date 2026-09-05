# OreSight — खनिज दृष्टि

A reserve-to-production digital twin prototype for MOIL's manganese mining
operations, built for Smart India Hackathon. Single-mine (Balaghat) working
demo: real rainfall + real mine geometry facts, synthetic-but-calibrated
production, a real trained forecast model, a reserve/EAR panel, prescriptive
actions, and a generated PDF report.

**Read this first if you're picking this project back up:**
- `EXECUTION_PLAN.md` — the solo/36-hour build plan and what's actually done
- `docs/minimum-working-demo.md` — the exact demo target and its 8-point definition of done
- `docs/domain-glossary.md` — terms and facts for Q&A confidence
- `OreSight_SIH_Blueprint.md` — the full original research/design document

---

## What's real vs synthetic (say this out loud in the demo)

| Data | Status |
|---|---|
| Balaghat coordinates, depth, strike length, mine type | ✅ Real (public MOIL/GSI sources) |
| Daily rainfall, 2018 → present | ✅ Real (Open-Meteo / ERA5 reanalysis) |
| MOIL company-level annual production totals | ✅ Real (public disclosures, see `docs/domain-glossary.md`) |
| Balaghat's daily production series | 🔶 Synthetic, calibrated to the blueprint's illustrative monthly figures |
| The 3D block model / reserve tonnage | 🔶 Synthetic geometry calibrated to real facts, tonnage rescaled to a believable order of magnitude — **not a real MOIL reserve statement** |

The running app shows a badge with this disclosure. Don't remove it.

---

## Prerequisites

- **Python 3.11+** (built and tested on 3.13). On Windows, the `py` launcher is used.
- **Node.js 18+** and npm (built and tested on Node 24).
- No Docker, no Postgres, no external services required — SQLite + local files only.
- Internet access is only needed once, to install dependencies and (optionally) to re-fetch rainfall data.

---

## One-time setup

Run these once after cloning/starting fresh.

### 1. Backend — create the virtualenv and install dependencies

```sh
cd backend
py -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -r requirements.txt
cd ..
```

(On macOS/Linux, replace `py` with `python3` and `./.venv/Scripts/python.exe` with `./.venv/bin/python`.)

### 2. Frontend — install npm dependencies

```sh
cd frontend
npm install
cd ..
```

### 3. Generate the data and seed the database

The repo already ships with the generated CSVs and reserve model committed
(`data/processed/`, `data/synthetic/`), so **you can skip straight to step
3d (seeding)** unless you want to regenerate everything from scratch.

```sh
# 3a. (optional, needs internet) Re-fetch real rainfall for Balaghat
py scripts/prepare_rainfall.py

# 3b. (optional) Regenerate the synthetic production/equipment series
py scripts/generate_synthetic.py

# 3c. (optional) Regenerate the synthetic 3D block model + grade-tonnage curve
./backend/.venv/Scripts/python.exe ml/prism/blockmodel.py

# 3d. Required: load everything into the SQLite database
./backend/.venv/Scripts/python.exe scripts/seed.py
```

`scripts/seed.py` is idempotent — it wipes and reloads Balaghat's data every
time, so it's safe to re-run. This is also the "reset demo" logic exposed
via the in-app **Reset demo** button.

---

## Running the app

You need two terminals running at the same time.

**Terminal 1 — backend (from the `backend/` directory):**

```sh
cd backend
./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
```

Verify: open `http://127.0.0.1:8000/health` → should return `{"status":"ok"}`.
API docs are auto-generated at `http://127.0.0.1:8000/docs`.

**Terminal 2 — frontend (from the `frontend/` directory):**

```sh
cd frontend
npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`). The Vite dev
server proxies `/api/*` to `http://127.0.0.1:8000`, so the backend must
already be running.

That's it — the dashboard should load with the map, KPIs, production
history, reserve panel, forecast + what-if slider, and actions panel all
populated with data.

---

## Quick smoke test (no browser needed)

If you just want to confirm the backend works after setup, from the
`backend/` directory with the server running:

```sh
curl http://127.0.0.1:8000/api/mines
curl http://127.0.0.1:8000/api/mines/1/kpi
curl -X POST http://127.0.0.1:8000/api/forecast -H "Content-Type: application/json" -d "{\"mine_id\":1,\"horizon_days\":30}"
```

You should get real JSON back, not errors, for all three.

---

## Resetting to a clean demo state

Either click **Reset demo** in the app header, or run:

```sh
curl -X POST http://127.0.0.1:8000/api/admin/reset-demo
```

Both call the same logic as `scripts/seed.py`: wipe and reload Balaghat's
production, equipment, and audit-log data from the checked-in CSVs.

---

## Project structure

```
SIH/
├── README.md                    # this file
├── EXECUTION_PLAN.md            # solo/36h build plan and progress tracker
├── OreSight_SIH_Blueprint.md    # full original research/design document
├── docs/
│   ├── domain-glossary.md       # terms + 20 sourced domain facts
│   └── minimum-working-demo.md  # the exact demo target
├── data/
│   ├── raw/                     # raw downloaded rainfall JSON (gitignored)
│   ├── processed/               # rainfall CSV, reserve/grade-tonnage JSON
│   └── synthetic/               # generated production & equipment CSVs
├── ml/
│   ├── prism/blockmodel.py      # synthetic 3D block model, EAR, grade-tonnage curve
│   └── pulse/forecast.py        # LightGBM quantile forecast + SHAP drivers
├── scripts/
│   ├── prepare_rainfall.py      # downloads/converts real rainfall data
│   ├── generate_synthetic.py    # generates synthetic production/equipment data
│   └── seed.py                  # loads everything into SQLite (also = reset-demo)
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI app + router registration
│   │   ├── database.py          # SQLAlchemy engine/session (SQLite)
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── routers/             # mines, production, forecast, actions, reserve, reports, admin
│   └── oresight.db              # SQLite database (created on first run)
└── frontend/
    ├── src/
    │   ├── api/client.ts        # typed API client
    │   ├── components/          # MapView, KpiCards, charts, ForecastPanel, ReservePanel, ActionsPanel
    │   └── pages/Dashboard.tsx  # composes the whole screen
    └── public/block-model-balaghat.png  # precomputed 3D reserve image
```

---

## API reference (all under `/api`)

| Method | Path | Purpose |
|---|---|---|
| GET | `/mines` | List mines (currently just Balaghat) |
| GET | `/mines/{id}` | Mine metadata |
| GET | `/mines/{id}/kpi` | Latest/MTD actuals vs monthly target |
| GET | `/mines/{id}/production?days=N` | Daily production history |
| GET | `/mines/{id}/reserve` | EAR, grade-tonnage curve, block model image URL |
| POST | `/forecast` | `{mine_id, horizon_days, rainfall_override_mm?}` → P10/P50/P90, shortfall probability, SHAP drivers |
| GET | `/mines/{id}/suggest-actions` | Ranked greedy corrective actions |
| POST | `/mines/{id}/apply-action` | Apply an action → writes an audit log row |
| GET | `/mines/{id}/audit-log` | Applied-actions history |
| GET | `/mines/{id}/report.pdf` | Generated PDF report |
| POST | `/admin/reset-demo` | Wipe and reload demo data |

Full interactive docs: `http://127.0.0.1:8000/docs` while the backend is running.

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'ml'`** — make sure you're running
  uvicorn with the backend's own venv Python (`./.venv/Scripts/python.exe -m uvicorn ...`),
  not a system Python. The routers add the repo root to `sys.path` at import
  time; running from the wrong interpreter or wrong working directory can
  surface this.
- **`numpy`/`lightgbm` build errors on install** — this repo intentionally
  leaves `requirements.txt` unpinned so pip can resolve versions with
  prebuilt wheels for your Python version. If you see a source build
  failure (e.g. "NumPy requires GCC >= 8.4"), your Python version likely
  predates available wheels — upgrade Python rather than pinning older
  package versions.
- **Frontend shows "No mines seeded yet"** — run `scripts/seed.py` (see
  step 3d above) with the backend's venv Python.
- **Forecast endpoint returns 400 "Not enough production history"** — the
  database wasn't seeded, or was wiped without reseeding. Run `scripts/seed.py`.
- **What-if slider feels slow on the very first move** — the first
  `/forecast` call per mine trains the models (~2 seconds); every call
  after that reuses the cached model and responds in well under a second.

---

## Demo script

See `EXECUTION_PLAN.md` → "Demo Script" section for the rehearsed 9-step
walkthrough (map → EAR → forecast → drivers → what-if slider → suggest
actions → apply → PDF → data-honesty close).
