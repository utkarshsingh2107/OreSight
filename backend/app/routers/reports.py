import io
import json
import os
import sys

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet

from ..database import get_db
from .. import models

router = APIRouter()

SIH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if SIH_ROOT not in sys.path:
    sys.path.insert(0, SIH_ROOT)

from ml.pulse import forecast as pulse_forecast  # noqa: E402

DATA_PROCESSED = os.path.join(SIH_ROOT, "data", "processed")
BLOCK_MODEL_IMAGE = os.path.join(SIH_ROOT, "frontend", "public", "block-model-balaghat.png")


@router.get("/mines/{mine_id}/report.pdf")
def get_report(mine_id: int, db: Session = Depends(get_db)):
    mine = db.query(models.Mine).filter(models.Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")

    rows = (
        db.query(models.ProductionDaily)
        .filter(models.ProductionDaily.mine_id == mine_id)
        .order_by(models.ProductionDaily.date.asc())
        .all()
    )
    if len(rows) < 60:
        raise HTTPException(status_code=400, detail="Not enough production history yet")

    df = pd.DataFrame(
        [
            {
                "date": r.date,
                "tonnes": r.tonnes,
                "rainfall_mm": r.rainfall_mm or 0.0,
                "equipment_downtime_hours": r.equipment_downtime_hours or 0.0,
                "is_holiday": r.is_holiday or 0,
            }
            for r in rows
        ]
    )

    forecast = pulse_forecast.predict(
        mine_id=mine_id,
        horizon_days=30,
        history_df=df,
        monthly_target_tonnes=mine.monthly_target_tonnes,
    )

    reserve_summary_path = os.path.join(DATA_PROCESSED, "reserve_summary_balaghat.json")
    reserve = None
    if os.path.exists(reserve_summary_path):
        with open(reserve_summary_path) as f:
            reserve = json.load(f)

    actions_rows = (
        db.query(models.ActionLog)
        .filter(models.ActionLog.mine_id == mine_id)
        .order_by(models.ActionLog.applied_at.desc())
        .limit(5)
        .all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm, leftMargin=18 * mm, rightMargin=18 * mm
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("OreSight — Mine Status Report", styles["Title"]))
    story.append(Paragraph(f"{mine.name}, {mine.state} ({mine.mine_type})", styles["Heading2"]))
    story.append(
        Paragraph(
            "Demo data: real rainfall + MOIL published production totals; "
            "synthetic daily detail calibrated to match. See docs/domain-glossary.md.",
            styles["Italic"],
        )
    )
    story.append(Spacer(1, 8 * mm))

    if reserve:
        story.append(Paragraph("Reserve summary", styles["Heading2"]))
        reserve_table_data = [
            ["Total geological reserve", f"{reserve['total_geological_tonnage']:,.0f} t"],
            [
                "Effective Accessible Reserve (EAR)",
                f"{reserve['effective_accessible_reserve_tonnage']:,.0f} t",
            ],
            ["Accessibility discount", f"{reserve['accessibility_discount_pct']}%"],
        ]
        t = Table(reserve_table_data, colWidths=[90 * mm, 70 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 4 * mm))
        if os.path.exists(BLOCK_MODEL_IMAGE):
            story.append(Image(BLOCK_MODEL_IMAGE, width=160 * mm, height=110 * mm))
        story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Production forecast (next 30 days)", styles["Heading2"]))
    forecast_table_data = [
        ["P10", "P50", "P90", "Shortfall probability"],
        [
            f"{forecast['p10']:,.0f} t",
            f"{forecast['p50']:,.0f} t",
            f"{forecast['p90']:,.0f} t",
            f"{forecast['shortfall_probability'] * 100:.1f}%",
        ],
    ]
    t2 = Table(forecast_table_data, colWidths=[40 * mm] * 4)
    t2.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(t2)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Top shortfall drivers", styles["Heading3"]))
    driver_data = [["Driver", "Relative impact", "Direction"]]
    for d in forecast["drivers"]:
        driver_data.append([d["name"], f"{d['impact']:.2f}", d["direction"]])
    t3 = Table(driver_data, colWidths=[70 * mm, 40 * mm, 40 * mm])
    t3.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(t3)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Recently applied corrective actions", styles["Heading3"]))
    if actions_rows:
        action_data = [["Action", "Expected Δtonnes", "Applied at"]]
        for a in actions_rows:
            action_data.append(
                [a.action_name, f"+{a.expected_delta_tonnes:.0f} t", a.applied_at.strftime("%Y-%m-%d %H:%M")]
            )
        t4 = Table(action_data, colWidths=[80 * mm, 40 * mm, 40 * mm])
        t4.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(t4)
    else:
        story.append(Paragraph("None applied yet.", styles["Normal"]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=oresight_{mine.name.lower()}_report.pdf"},
    )
