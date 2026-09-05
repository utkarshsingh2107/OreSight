# OreSight — Solo, 36-Hour Execution Plan

**Reality check:** this is a solo build. Other "team members" are nominal.
Total available time is **36 hours**, start to finish — no separate multi-week
prep runway. Every phase from the original blueprint (§14.1's 3-week prep,
§15's 6-person team) is therefore compressed or cut. This file replaces the
original team-based plan as the one to actually follow. The blueprint
(`OreSight_SIH_Blueprint.md`) is still the reference for *why* — this file is
the *what, in what order*.

**Governing principle (from blueprint §13.6): build the Minimum Working
Demo first, end-to-end, before touching anything else.** See
`docs/minimum-working-demo.md` for the exact 8-point definition of done. That
document is the target for hours 0–29 below. Everything after is stretch,
attempted only if ahead of schedule.

## Non-negotiable scope decisions (already made for you)

To make this solo-feasible, the following blueprint features are **cut from
the base plan** and only attempted as stretch goals if time allows:

| Cut from base plan | Why | Stretch tier |
|---|---|---|
| Multi-mine map (11 mines) | One mine tells the whole story; 10 extra mines is 0 extra narrative value | Tier 3 |
| Interactive 3D block viewer (react-three-fiber) | High effort, high risk for one person; a static rendered image conveys 80% of the impact | Tier 2 |
| Real Ordinary Kriging / SGS | Nice-to-have rigor; a precomputed/plausible synthetic block model image is enough for the demo | Tier 3 |
| Regional prospectivity ML (M4) | Second reserve "scale" — valuable but the shortfall-prediction half (40% of PS weight per §1.6) matters more | Tier 3 |
| MILP optimiser (OR-Tools) | A ranked greedy heuristic gives the same demo beat ("suggest actions") for a fraction of the effort/debugging risk | Tier 2 |
| Docker Compose / Postgres+PostGIS+TimescaleDB / Celery+Redis+MinIO / Keycloak | Infra overhead a solo dev can't afford to debug at 3am | Not planned — see simplified stack below |
| RBAC / real auth | A role dropdown that changes what's shown is enough for a demo | Tier 3 |
| Alerts/WebSockets | Static "alerts" list is enough | Tier 3 |

## Simplified solo tech stack

| Layer | Use this instead of the full blueprint stack |
|---|---|
| Backend | FastAPI + **SQLite** (zero setup, one file, fine for a demo) |
| Frontend | React + Vite + Tailwind, plain components (skip shadcn setup overhead unless you already have a starter) |
| Charts | ECharts or Recharts — whichever you already know |
| Map | MapLibre GL JS with a static GeoJSON point/polygon for Balaghat — no tile server needed |
| 3D | Skip react-three-fiber for the base plan. Generate a static 3D block image with `matplotlib`/`plotly` offline, embed as an image. Add r3f only as Tier 2 stretch. |
| ML | pandas, LightGBM (quantile objective), SHAP, scikit-learn |
| Optimization | Plain Python greedy ranking function (sort candidate actions by estimated Δtonnes / cost) |
| PDF | WeasyPrint or ReportLab, one template |
| Background jobs | None — FastAPI `BackgroundTasks` if genuinely needed, otherwise synchronous |
| Containerization | Skip Docker for the build. Optional: a single `Dockerfile` at the end IF ahead of schedule (judges like `docker compose up` but a working demo beats a containerized broken one) |

**Rule: if a tool isn't something you already know well, don't introduce it
mid-hackathon.** Swap anything above for whatever you're fastest in.

---

## Before Hour 0 (do this the moment you read this, it costs nothing)

- [ ] Confirm dev environment works *right now*: Node + npm, Python 3.11+,
      git, code editor. Run a "hello world" for both FastAPI and Vite React
      today, not at hour 0.
- [ ] Download and cache locally (this can take hours in the background,
      start it now):
  - Real MOIL published production figures → a CSV (from annual
    reports/press releases — see `docs/domain-glossary.md` facts #2–4)
  - A real rainfall time series for the Balaghat area (GPM IMERG, or a
    simpler public daily-rainfall dataset for Balaghat district if IMERG
    access is too slow to arrange — realism matters more than the exact
    source)
- [ ] Skim `docs/domain-glossary.md` (10 min) so you can talk about EAR,
      UNFC, MCDR, and the reserve-vs-production distinction confidently in
      Q&A.
- [ ] Read `docs/minimum-working-demo.md` once, fully — this is your target.

If you truly have zero time before hour 0, start the plan below at Hour 0
with a rough/placeholder rainfall series and swap in the real one whenever
it finishes downloading in the background.

---

## The 36-Hour Solo Schedule

Times are cumulative hours from hackathon start. Each block ends with a
concrete, checkable **output** — if you don't have the output, do not move
on to polish; fix the block first.

### H0–1 — Setup
- [ ] `git init`, repo skeleton: `backend/`, `frontend/`, `data/`, `ml/`, `docs/`
- [ ] FastAPI app boots (`/health` returns 200); Vite React app boots
- [ ] SQLite file created, one table stubbed
- **Output:** both servers run locally, empty pages load

### H1–4 — Synthetic data generator
- [ ] `scripts/generate_synthetic.py`: daily production for Balaghat,
      2018–2026, scaled to be consistent with real MOIL published totals
      (see domain glossary #2–4), with a monsoon-suppression term driven by
      the real rainfall series, weekday effects, and randomized equipment
      downtime shocks
- [ ] Write output to SQLite (`production_daily` table)
- **Output:** a CSV/DB table you can plot and it visibly dips every monsoon

### H4–6 — Backend core API
- [ ] `GET /mine` (Balaghat static metadata), `GET /production` (time series),
      `GET /kpi` (latest actual vs target)
- **Output:** `curl`/`/docs` shows real data coming back

### H6–11 — Forecast model (the highest-value block — protect this time)
- [ ] Feature engineering: lag features, rolling means, rainfall (real),
      day-of-week/month, synthetic equipment-downtime flag
- [ ] LightGBM quantile regression (P10/P50/P90), trained on the synthetic
      series
- [ ] Shortfall probability: P(P50 forecast < monthly target), simple Monte
      Carlo or quantile-based approximation
- [ ] SHAP values for the point forecast → top 3–5 drivers ranked
- [ ] `POST /forecast` returns fan-chart data + shortfall probability +
      driver list
- **Output:** a real fan chart with real numbers and a real shortfall %

### H11–13 — Frontend shell + map + KPIs
- [ ] Routing/layout, MapLibre view centered on Balaghat with one marker/polygon
- [ ] KPI cards (actual vs target, shortfall probability)
- [ ] Production history chart
- **Output:** app looks like a product, not a form

### H13–15 — Forecast UI + what-if slider
- [ ] Fan chart component (ECharts) wired to `/forecast`
- [ ] Driver panel showing SHAP bars
- [ ] Rainfall what-if slider → re-POSTs with adjusted rainfall feature →
      re-renders in < 3s
- **Output:** moving the slider visibly moves the shortfall probability —
  this is your best demo moment, get it rock solid

### H15–17 — Greedy prescriptive actions
- [ ] A small candidate-action table (extra shift, redeploy equipment,
      reduce a named downtime cause), each with a hand-justified/estimated
      Δtonnes and cost
- [ ] Greedy ranking function: sort by Δtonnes (optionally per unit cost)
- [ ] `POST /suggest-actions`, `POST /apply-action` → writes an audit log row
- [ ] Frontend: "Suggest actions" button → ranked list → "Apply" → audit log
      entry appears in a simple table
- **Output:** the full suggest→apply→audit loop works

### H17–20 — SLEEP (yes, even solo)
Set an alarm. 2.5–3 hours minimum. You present worse at hour 34 without it,
and presentation quality is a large share of the score. This is not optional
time you can reclaim by cutting it — teams (and solo builders) who skip
sleep make careless mistakes in exactly the parts judges are watching.

### H20–23 — Static 3D block visual + grade-tonnage curve
- [ ] Offline: generate a synthetic block model (simple 3D array with a
      folded ore-band shape, grade values), render as a static image (matplotlib
      3D scatter/voxel plot or a plotly 3D export) — colored by grade
- [ ] Grade-tonnage curve chart (tonnage above cutoff grade vs cutoff) from
      the same synthetic block model
- [ ] Embed both in the frontend as a "Reserve" panel + your EAR number
      (a single computed metric: geological tonnage × an accessibility
      discount factor you define and can explain)
- **Output:** a credible-looking reserve visual, even if not interactive

### H23–26 — PDF report
- [ ] One WeasyPrint/ReportLab template: mine summary, forecast chart image,
      top drivers, suggested actions
- [ ] `GET /report/pdf` generates and returns it
- **Output:** a real downloadable PDF with real numbers

### H26–28 — Data-honesty + polish pass 1
- [ ] Add the UI badge: *"Demo data: real rainfall + MOIL published
      production totals; synthetic daily detail calibrated to match."*
- [ ] Loading states, empty states, no raw JSON errors on screen
- **Output:** nothing on screen looks broken or unexplained

### H28–30 — Full run-through + bug fixes
- [ ] Run the entire demo script (see below) from a cold start, twice
- [ ] Add a "reset demo" script/button that restores known-good DB state
- **Output:** the demo runs twice in a row without manual fixes

### H30–33 — Stretch tier (only if you are genuinely ahead)
Attempt in this order, stop the moment you're not ahead anymore:
1. **Tier 1:** Equipment failure risk (simple Weibull via `lifelines`) as an
   extra named driver
2. **Tier 2:** Greedy → real small MILP/OR-Tools optimisation for actions;
   OR an interactive 3D viewer if you already know react-three-fiber
3. **Tier 3:** A second mine on the map; a role-based view toggle

Do not start a stretch item you can't finish and revert cleanly in 45 minutes.

### H33–35 — Freeze, deck, rehearsal
- [ ] Code freeze — no more feature changes
- [ ] Prepare a short slide deck / talking points (problem → EAR concept →
      demo → data honesty → what's next)
- [ ] Rehearse the demo script out loud, twice, with a timer
- [ ] **Record a screen-capture backup video of a full working demo run.**
      Non-negotiable — laptop/Wi-Fi failure is common and this is your
      insurance.

### H35–36 — Final checks
- [ ] Laptop charged, offline mode tested (does the demo work with Wi-Fi off?)
- [ ] Backup video accessible without internet (local file, not just cloud)
- [ ] One-line README: what it is, how to run it, what's real vs synthetic

---

## Demo Script (rehearse this exact sequence)

1. Open on the map, Balaghat selected, KPI cards visible
2. Point at the EAR number and the reserve panel (static 3D image + grade-tonnage curve)
3. Show the forecast fan chart and say the shortfall probability out loud
4. Open the driver panel — name the top SHAP driver
5. Move the rainfall what-if slider — narrate the shortfall probability changing live
6. Click "Suggest actions" — read the top-ranked action and its Δtonnes
7. Apply it — point at the audit log entry appearing
8. Download the PDF report
9. Close on the data-honesty badge and one sentence on what Phase 2 would add

## If something breaks during the real demo

Fall back immediately to the backup video. Say so plainly ("let me show you
the recorded run to save time") and keep talking through the story — judges
penalize panic and dead air far more than they penalize using a backup video.

---

## Reference documents

- `docs/minimum-working-demo.md` — the exact target this schedule builds
- `docs/domain-glossary.md` — facts and terms for Q&A confidence
- `OreSight_SIH_Blueprint.md` — full rationale, data strategy (§13.3), Q&A
  prep (§16.3), and everything considered but cut for this solo plan
