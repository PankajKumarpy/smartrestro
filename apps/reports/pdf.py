from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def render_daily_closing_pdf(*, title: str, date_str: str, lines: list[tuple[str, str]]) -> bytes:
    """
    Very lightweight PDF renderer (pure Python).
    lines: list of (label, value)
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, title)
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Date: {date_str}")

    y -= 1.2 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Summary")
    y -= 0.6 * cm

    c.setFont("Helvetica", 11)
    for label, value in lines:
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
        c.drawString(2 * cm, y, label)
        c.drawRightString(width - 2 * cm, y, value)
        y -= 0.55 * cm

    c.showPage()
    c.save()
    return buffer.getvalue()

