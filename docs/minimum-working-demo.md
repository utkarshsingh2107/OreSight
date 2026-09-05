# OreSight — Minimum Working Demo (MWD)

This is the non-negotiable floor the team commits to in Phase 0. Per the
blueprint (§13.6): **build this first, end-to-end, before building anything
else outward.** Everything beyond this list is upside.

If the hackathon clock runs out and only this exists, the team can still
present a complete, honest, coherent story.

## Scope: Single mine (Balaghat)

- [ ] Real **IMERG rainfall** time series for the Balaghat lease area
- [ ] Synthetic-but-calibrated **daily production, 2018–2026**, scaled so the
      mine's contribution is consistent with MOIL's real published totals
- [ ] A **LightGBM quantile forecast** producing a P10/P50/P90 fan chart with
      an explicit **shortfall probability** (P(output < target))
- [ ] A **SHAP driver panel** explaining the top contributors to that forecast
- [ ] A **rainfall what-if slider** that recomputes the shortfall probability
      live (target: < 3 seconds)
- [ ] **Three greedy-heuristic corrective actions** with an estimated Δtonnes
      each (MILP optimiser is upside; greedy fallback is the floor)
- [ ] A **static, pre-rendered 3D block model image** + a grade-tonnage curve
      (does not need to be interactive for the floor version)

Estimated effort: buildable by two people in ~12 hours (per blueprint).

## Definition of done for the MWD

All 8 of these must work live, in this order, without manual intervention:

1. [ ] Map → mine selection → live KPIs
2. [ ] 3D block model (static image is acceptable) with grade/confidence info
      + the EAR funnel number
3. [ ] Forecast fan chart with a real shortfall probability
4. [ ] Driver attribution panel with real SHAP values
5. [ ] What-if slider → recompute in < 3s → shortfall probability visibly moves
6. [ ] "Suggest actions" → ranked actions (greedy fallback is acceptable)
7. [ ] Apply action → schedule updates → an audit log entry appears
8. [ ] One generated PDF report

## What this deliberately excludes (build later, in this order)

Interactive 3D viewer → multi-mine map → prospectivity ML layer → MILP solver
→ equipment survival model → weather derating curves → hierarchical
reconciliation → alerts/webhooks → RBAC.

See `EXECUTION_PLAN.md` Phase 2 for the full MVP feature build order (M1–M14).

## Data honesty commitment

Every screen must make clear which data is real vs synthetic. Planned UI
badge text: *"Demo data: real EO/geoscience + synthetic operational data
calibrated to MOIL's published production."* This is a deliberate
credibility move (blueprint §13.3) — do not skip it, even in the MWD.
