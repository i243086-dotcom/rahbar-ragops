#!/usr/bin/env python3
"""Build the report body from source plus committed result JSON.

Phase 0 intentionally renders one placeholder page per planned section. Later phases replace
placeholder text with tables and figures populated only from eval/results/*.json and traces/.
"""

from __future__ import annotations

import json
import html
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "report_body.pdf"
RESULTS = ROOT / "eval" / "results"

PAGES = [
    ("RAHBAR RAGOps — Assignment 03", "System overview, team identity, repository, and architecture."),
    ("Figure 3 stage mapping", "Ingest → verify → data lake → retrieval sources → offline/live tests → coverage."),
    ("Table 2 quality mapping", "Adaptability, monitorability, observability, traceability, and reliability."),
    ("Part A — data management", "Verification and incremental-update measurements will come from Phase 2 JSON."),
    ("Part B — offline testing", "Module, component, end-to-end, noise, and stochasticity results will come from Phase 4 JSON."),
    ("Parts C and F — release", "Experiment, gate, controlled rollout, rollback, and measured resources."),
    ("Parts D and E — operations", "Traces, guardrails, root cause, coverage, and drift."),
    ("Short answers and contributions", "Drafts remain pending measured evidence and human confirmation."),
]


def result_inventory() -> list[list[str]]:
    rows = [["Committed result", "Top-level keys"]]
    if RESULTS.exists():
        for path in sorted(RESULTS.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                keys = ", ".join(sorted(payload)[:8]) if isinstance(payload, dict) else type(payload).__name__
            except (OSError, json.JSONDecodeError) as exc:
                keys = f"INVALID: {type(exc).__name__}"
            rows.append([str(path.relative_to(ROOT)), keys])
    if len(rows) == 1:
        rows.append(["None yet", "Phase 0 has no A03 measurements"])
    return rows


def build() -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle("PageTitle", parent=styles["Title"], fontSize=19, leading=23,
                           alignment=TA_CENTER, spaceAfter=10 * mm)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.25, leading=14)
    table_cell = ParagraphStyle(
        "TableCell", parent=styles["BodyText"], fontSize=7, leading=9, splitLongWords=True
    )
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm,
                            title="RAHBAR RAGOps Assignment 03")
    story = []
    inventory = result_inventory()
    for index, (heading, text) in enumerate(PAGES, start=1):
        story.extend([
            Paragraph(heading, title),
            Paragraph(text, body),
            Spacer(1, 8 * mm),
            Paragraph(f"Phase 0 report skeleton — planned body page {index} of 8.", body),
        ])
        if index == 1:
            story.extend([Spacer(1, 8 * mm), Paragraph("Names and roll numbers: PENDING OWNER INPUT", body),
                          Paragraph("Repository: github.com/i243086-dotcom/rahbar-ragops", body)])
        if index == 3:
            wrapped_inventory = [
                [Paragraph(html.escape(str(cell)), table_cell) for cell in row]
                for row in inventory
            ]
            table = Table(wrapped_inventory, colWidths=[62 * mm, 108 * mm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.extend([Spacer(1, 8 * mm), table])
        if index < len(PAGES):
            story.append(PageBreak())
    doc.build(story)
    print(f"built {OUT}")


if __name__ == "__main__":
    build()

