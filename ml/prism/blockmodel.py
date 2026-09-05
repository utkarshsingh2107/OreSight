"""
PRISM (reserve) — a synthetic-but-geologically-plausible 3D block model for
Balaghat, used to render the reserve panel (static image for the solo/36h
plan — see EXECUTION_PLAN.md H20-23) and to compute:
  - the grade-tonnage curve
  - the Effective Accessible Reserve (EAR): geological tonnage discounted by
    an operational accessibility factor (depth/development status/flooding)

Geology basis (see docs/domain-glossary.md): Balaghat's manganese ore is a
folded, stratabound gondite band in the Sausar Group, long along strike and
thin across it. This is a simplified stand-in for real kriging/SGS (blueprint
§6.2), explicitly disclosed as synthetic.

Real, disclosed facts used to bound realism:
  - Grade range ~10-54% Mn (IBM Indian Minerals Yearbook)
  - Balaghat is underground, reaches >400m depth (MOIL public disclosures)
  - Bulk density for manganese ore ~ 3.6-3.8 t/m3 (typical for gondite ore)
"""
from __future__ import annotations

import json
import math
import os
import random

import numpy as np

random.seed(7)
np.random.seed(7)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_CURVE = os.path.join(BASE_DIR, "data", "processed", "grade_tonnage_balaghat.json")
OUT_SUMMARY = os.path.join(BASE_DIR, "data", "processed", "reserve_summary_balaghat.json")
OUT_IMAGE = os.path.join(BASE_DIR, "frontend", "public", "block-model-balaghat.png")

# Grid: along-strike (x, 2.8km strike length per public subsidence report),
# across-strike/thickness (y), depth levels (z, down to ~450m).
NX, NY, NZ = 56, 12, 18
BLOCK_SIZE_M = (50.0, 10.0, 25.0)  # x, y, z metres per block
BULK_DENSITY_T_PER_M3 = 3.7

BASE_GRADE = 34.0  # % Mn, central tendency
GRADE_STD = 9.0

# The raw grid geometry (calibrated to the real 2.8km strike length and
# ~450m depth from public disclosures) produces a much larger tonnage than
# is plausible for a single mine's reserve once block volume x density is
# taken literally. Rather than hand-fudge individual blocks, we apply one
# transparent global rescale so the DISCLOSED total lands in a believable
# range for a major underground manganese mine, while preserving the
# relative geometry/grade/confidence/accessibility structure used for the
# visualisation and grade-tonnage curve.
TARGET_TOTAL_TONNAGE = 22_000_000.0


def _fold_center_y(x_idx: int) -> float:
    """Sinusoidal fold of the ore band across strike (in block-y units)."""
    return NY / 2 + 2.2 * math.sin(x_idx / 7.5) + 1.0 * math.sin(x_idx / 2.3)


def _band_half_width(x_idx: int) -> float:
    """Band thickens/thins along strike (per public description: 1m-30m)."""
    return 1.2 + 1.8 * (0.5 + 0.5 * math.sin(x_idx / 10.0))


def generate_block_model() -> dict:
    blocks = []
    borehole_xy = [(random.uniform(0, NX), random.uniform(0, NY)) for _ in range(14)]

    for xi in range(NX):
        center_y = _fold_center_y(xi)
        half_width = _band_half_width(xi)
        for yi in range(NY):
            in_band = abs(yi - center_y) <= half_width
            if not in_band:
                continue
            # Grade: smooth spatial field + noise, decaying with depth slightly
            for zi in range(NZ):
                depth_m = zi * BLOCK_SIZE_M[2]
                spatial = math.sin(xi / 6.0) * 4 + math.cos(yi / 2.5) * 3
                depth_decay = -0.01 * depth_m  # very slight grade decay with depth
                grade = BASE_GRADE + spatial + depth_decay + np.random.normal(0, GRADE_STD * 0.35)
                grade = float(np.clip(grade, 8.0, 54.0))

                # Confidence from distance to nearest synthetic borehole
                dists = [math.hypot(xi - bx, yi - by) for bx, by in borehole_xy]
                min_dist = min(dists)
                if min_dist < 4:
                    confidence = "Measured"
                elif min_dist < 9:
                    confidence = "Indicated"
                else:
                    confidence = "Inferred"

                # Accessibility: shallower + closer to existing development = more accessible.
                # Below level 12 (300m) accessibility drops (undeveloped levels);
                # a synthetic "flooded sector" (yi far from center in one fold trough)
                # further discounts a subset of blocks.
                level_factor = 1.0 if zi <= 8 else max(0.15, 1.0 - 0.09 * (zi - 8))
                flood_zone = (xi % 18) < 3 and zi <= 4
                flood_factor = 0.4 if flood_zone else 1.0
                accessibility = round(level_factor * flood_factor, 3)

                volume_m3 = BLOCK_SIZE_M[0] * BLOCK_SIZE_M[1] * BLOCK_SIZE_M[2]
                tonnage = volume_m3 * BULK_DENSITY_T_PER_M3

                blocks.append(
                    {
                        "x": xi,
                        "y": yi,
                        "z": zi,
                        "grade": round(grade, 1),
                        "confidence": confidence,
                        "accessibility": accessibility,
                        "tonnage": tonnage,
                    }
                )
    return {"blocks": blocks}


def compute_grade_tonnage_curve(blocks: list[dict]) -> list[dict]:
    cutoffs = list(range(8, 55, 2))
    curve = []
    for cutoff in cutoffs:
        eligible = [b for b in blocks if b["grade"] >= cutoff]
        tonnage = sum(b["tonnage"] for b in eligible)
        avg_grade = (
            sum(b["tonnage"] * b["grade"] for b in eligible) / tonnage if tonnage > 0 else 0.0
        )
        curve.append(
            {
                "cutoff_grade": cutoff,
                "tonnage": round(tonnage, 0),
                "avg_grade": round(avg_grade, 1),
            }
        )
    return curve


def compute_reserve_summary(blocks: list[dict]) -> dict:
    total_tonnage = sum(b["tonnage"] for b in blocks)
    ear_tonnage = sum(b["tonnage"] * b["accessibility"] for b in blocks)

    by_confidence = {}
    for conf in ("Measured", "Indicated", "Inferred"):
        conf_blocks = [b for b in blocks if b["confidence"] == conf]
        by_confidence[conf] = round(sum(b["tonnage"] for b in conf_blocks), 0)

    return {
        "total_geological_tonnage": round(total_tonnage, 0),
        "effective_accessible_reserve_tonnage": round(ear_tonnage, 0),
        "accessibility_discount_pct": round(100 * (1 - ear_tonnage / total_tonnage), 1),
        "tonnage_by_confidence": by_confidence,
        "bulk_density_t_per_m3": BULK_DENSITY_T_PER_M3,
        "note": (
            "Synthetic block model calibrated to publicly disclosed geometry "
            "(strike length, depth, grade range) and globally rescaled to a "
            "believable total-reserve order of magnitude — not real MOIL "
            "borehole assays or a real reserve statement."
        ),
    }


def render_static_image(blocks: list[dict]):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Subsample for a fast, legible static render
    sample = blocks[::3] if len(blocks) > 4000 else blocks
    xs = [b["x"] for b in sample]
    ys = [b["y"] for b in sample]
    zs = [-b["z"] for b in sample]  # depth downward
    grades = [b["grade"] for b in sample]

    fig = plt.figure(figsize=(10, 7), facecolor="#0b0f14")
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#0b0f14")

    p = ax.scatter(xs, ys, zs, c=grades, cmap="turbo", s=6, alpha=0.85, vmin=8, vmax=54)
    cbar = fig.colorbar(p, ax=ax, shrink=0.6, pad=0.1)
    cbar.set_label("Mn grade (%)", color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.get_yticklabels(), color="white")

    ax.set_xlabel("Along strike (blocks)", color="white")
    ax.set_ylabel("Across strike (blocks)", color="white")
    ax.set_zlabel("Depth level (blocks, down)", color="white")
    ax.tick_params(colors="white")
    ax.set_title(
        "Balaghat — synthetic 3D block model (grade-colored)\nSynthetic geometry calibrated to public geology",
        color="white",
        fontsize=11,
    )

    os.makedirs(os.path.dirname(OUT_IMAGE), exist_ok=True)
    fig.savefig(OUT_IMAGE, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def rescale_tonnage(blocks: list[dict], target_total: float) -> None:
    raw_total = sum(b["tonnage"] for b in blocks)
    scale = target_total / raw_total if raw_total > 0 else 1.0
    for b in blocks:
        b["tonnage"] = b["tonnage"] * scale


def main():
    model = generate_block_model()
    blocks = model["blocks"]
    print(f"Generated {len(blocks)} ore blocks")
    rescale_tonnage(blocks, TARGET_TOTAL_TONNAGE)

    curve = compute_grade_tonnage_curve(blocks)
    summary = compute_reserve_summary(blocks)

    os.makedirs(os.path.dirname(OUT_CURVE), exist_ok=True)
    with open(OUT_CURVE, "w") as f:
        json.dump(curve, f, indent=2)
    with open(OUT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    render_static_image(blocks)

    print(f"Total geological tonnage: {summary['total_geological_tonnage']:,.0f} t")
    print(
        f"Effective Accessible Reserve: {summary['effective_accessible_reserve_tonnage']:,.0f} t "
        f"({summary['accessibility_discount_pct']}% discounted)"
    )
    print(f"Wrote {OUT_CURVE}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_IMAGE}")


if __name__ == "__main__":
    main()
