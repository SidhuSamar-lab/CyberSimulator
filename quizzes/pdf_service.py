"""
PDF Certificate Generator for CyberSimulator.
Produces a vector-quality, print-ready Certificate of Cyber Mastery
in landscape PDF format using ReportLab.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def generate_certificate_pdf(
    student_name: str,
    class_name: str,
    roll_number: str,
    rank_title: str = "Digital Cadet",
    badges_count: int = 0,
    total_quizzes: int = 0,
    avg_accuracy: float = 0.0,
    cert_id: str = None,
    issue_date: str = None
) -> bytes:
    """
    Generates a dark-mode Nexus Studio cyber-aesthetic Certificate of Mastery in PDF format.
    Returns bytes of the generated PDF document.
    """
    if not cert_id:
        cert_id = f"CS-{abs(hash(student_name + roll_number)) % 900000 + 100000}"
    if not issue_date:
        issue_date = datetime.now().strftime("%B %d, %Y")

    buffer = io.BytesIO()
    # Landscape Letter: 792 wide x 612 high points
    page_width, page_height = landscape(letter)
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    c.setTitle(f"CyberShield Certificate - {student_name}")
    c.setAuthor("CyberSimulator Platform")
    c.setSubject("Certificate of Cyber Mastery")

    # 1. Dark Canvas Background (#04040a)
    c.setFillColor(colors.HexColor('#04040a'))
    c.rect(0, 0, page_width, page_height, fill=True, stroke=False)

    # 2. Outer Cyber Grid Pattern (Subtle background grid lines)
    c.setStrokeColor(colors.HexColor('#0f0f20'))
    c.setLineWidth(0.5)
    for x in range(30, int(page_width), 45):
        c.line(x, 25, x, page_height - 25)
    for y in range(25, int(page_height), 45):
        c.line(30, y, page_width - 30, y)

    # 3. Double Cyber Borders
    # Outer Signal Lime Border (#e8ff47)
    c.setStrokeColor(colors.HexColor('#e8ff47'))
    c.setLineWidth(2.5)
    c.roundRect(28, 24, page_width - 56, page_height - 48, 14, stroke=True, fill=False)

    # Inner Subtle White/Mist Border
    c.setStrokeColor(colors.HexColor('#1f1f3a'))
    c.setLineWidth(1)
    c.roundRect(36, 32, page_width - 72, page_height - 64, 10, stroke=True, fill=False)

    # Decorative Corner Accents
    c.setStrokeColor(colors.HexColor('#e8ff47'))
    c.setLineWidth(2)
    # Top-Left Accent
    c.line(24, page_height - 40, 48, page_height - 40)
    c.line(40, page_height - 24, 40, page_height - 48)
    # Top-Right Accent
    c.line(page_width - 48, page_height - 40, page_width - 24, page_height - 40)
    c.line(page_width - 40, page_height - 24, page_width - 40, page_height - 48)
    # Bottom-Left Accent
    c.line(24, 40, 48, 40)
    c.line(40, 24, 40, 48)
    # Bottom-Right Accent
    c.line(page_width - 48, 40, page_width - 24, 40)
    c.line(page_width - 40, 24, page_width - 40, 48)

    center_x = page_width / 2

    # 4. Top Organization Pill Badge
    pill_w = 210
    pill_h = 22
    pill_y = page_height - 72
    c.setFillColor(colors.HexColor('#0b0b18'))
    c.setStrokeColor(colors.HexColor('#e8ff47'))
    c.setLineWidth(1)
    c.roundRect(center_x - (pill_w / 2), pill_y, pill_w, pill_h, 11, fill=True, stroke=True)

    # Dot indicator in pill
    c.setFillColor(colors.HexColor('#e8ff47'))
    c.circle(center_x - (pill_w / 2) + 14, pill_y + 11, 3.5, fill=True, stroke=False)

    c.setFillColor(colors.HexColor('#e8ff47'))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(center_x + 6, pill_y + 7, "CYBERSHIELD DEFENSE ACADEMY")

    # 5. Main Certificate Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(center_x, page_height - 110, "CERTIFICATE OF CYBER MASTERY")

    c.setFillColor(colors.HexColor('#9898b8'))
    c.setFont("Courier-Bold", 9)
    c.drawCentredString(center_x, page_height - 126, "OFFICIAL DIGITAL SAFETY DISTINCTION &bull; CADET HONORS")

    # Thin Divider Line
    c.setStrokeColor(colors.HexColor('#2a2a44'))
    c.setLineWidth(0.8)
    c.line(center_x - 180, page_height - 140, center_x + 180, page_height - 140)

    # 6. Recipient Introduction
    c.setFillColor(colors.HexColor('#c4c4d8'))
    c.setFont("Helvetica", 11)
    c.drawCentredString(center_x, page_height - 164, "THIS CERTIFICATE IS PROUDLY CONFERRED UPON")

    # Student Name (Large Neon Lime)
    c.setFillColor(colors.HexColor('#e8ff47'))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(center_x, page_height - 208, student_name)

    # Student Class and Roll Number
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(center_x, page_height - 230, f"{class_name}  &bull;  Cadet Roll #{roll_number}")

    # 7. Commendation Narrative
    c.setFillColor(colors.HexColor('#c4c4d8'))
    c.setFont("Helvetica", 9.5)
    c.drawCentredString(center_x, page_height - 258,
        "For demonstrating verified aptitude in spotting deceptive phishing lures, defending one-time verification codes,")
    c.drawCentredString(center_x, page_height - 272,
        f"identifying fraudulent domains, and outsmarting AI deepfakes to achieve the distinguished rank of {rank_title}.")

    # 8. Achievement Metrics Box (4 Stat Columns)
    box_w = 580
    box_h = 56
    box_y = page_height - 350
    c.setFillColor(colors.HexColor('#080814'))
    c.setStrokeColor(colors.HexColor('#222238'))
    c.setLineWidth(1)
    c.roundRect(center_x - (box_w / 2), box_y, box_w, box_h, 10, fill=True, stroke=True)

    col_w = box_w / 4
    metrics = [
        ("STUDENT RANK", rank_title, '#e8ff47'),
        ("BADGES EARNED", f"{badges_count} / 8", '#e8ff47'),
        ("QUIZZES TAKEN", f"{total_quizzes}", '#ffffff'),
        ("ACCURACY RATE", f"{avg_accuracy:.0f}%", '#e8ff47'),
    ]

    for idx, (lbl, val, val_color) in enumerate(metrics):
        col_center_x = center_x - (box_w / 2) + (idx * col_w) + (col_w / 2)
        # Vertical divider between stat columns
        if idx > 0:
            c.setStrokeColor(colors.HexColor('#1f1f32'))
            c.setLineWidth(0.8)
            div_x = center_x - (box_w / 2) + (idx * col_w)
            c.line(div_x, box_y + 8, div_x, box_y + box_h - 8)

        c.setFillColor(colors.HexColor('#9898b8'))
        c.setFont("Courier-Bold", 7.5)
        c.drawCentredString(col_center_x, box_y + 36, lbl)

        c.setFillColor(colors.HexColor(val_color))
        c.setFont("Helvetica-Bold", 12.5)
        c.drawCentredString(col_center_x, box_y + 16, val)

    # 9. Dual Signatures & Central Verified Seal
    # Left Signature: AI Cyber Mentor
    sig_left_x = center_x - 190
    c.setFillColor(colors.HexColor('#e8ff47'))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(sig_left_x, page_height - 408, "CyberQuizAgent (GPT-5)")

    c.setStrokeColor(colors.HexColor('#3a3a55'))
    c.setLineWidth(1)
    c.line(sig_left_x - 75, page_height - 416, sig_left_x + 75, page_height - 416)

    c.setFillColor(colors.HexColor('#9898b8'))
    c.setFont("Courier", 7.5)
    c.drawCentredString(sig_left_x, page_height - 428, "AI CYBER MENTOR / EVALUATION")

    # Center Verified Seal
    seal_y = page_height - 418
    c.setFillColor(colors.HexColor('#080814'))
    c.setStrokeColor(colors.HexColor('#e8ff47'))
    c.setLineWidth(1.5)
    c.circle(center_x, seal_y, 32, fill=True, stroke=True)

    # Inner dashed ring
    c.setStrokeColor(colors.HexColor('#b8cc38'))
    c.setLineWidth(0.8)
    c.circle(center_x, seal_y, 27, fill=False, stroke=True)

    c.setFillColor(colors.HexColor('#e8ff47'))
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(center_x, seal_y + 8, "VERIFIED")
    c.drawCentredString(center_x, seal_y - 3, "SECURE")
    c.setFillColor(colors.HexColor('#9898b8'))
    c.setFont("Courier", 6.5)
    c.drawCentredString(center_x, seal_y - 14, "ACADEMY &bull; 2026")

    # Right Signature: Course Instructor
    sig_right_x = center_x + 190
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(sig_right_x, page_height - 408, "Course Instructor")

    c.setStrokeColor(colors.HexColor('#3a3a55'))
    c.setLineWidth(1)
    c.line(sig_right_x - 75, page_height - 416, sig_right_x + 75, page_height - 416)

    c.setFillColor(colors.HexColor('#9898b8'))
    c.setFont("Courier", 7.5)
    c.drawCentredString(sig_right_x, page_height - 428, f"INSTRUCTOR &bull; {issue_date}")

    # 10. Bottom Credential Serial Footer
    c.setFillColor(colors.HexColor('#9898b8'))
    c.setFont("Courier", 8)
    c.drawCentredString(
        center_x, 48,
        f"Certificate ID: {cert_id}   |   Authenticated by CyberSimulator Threat Laboratory   |   Date: {issue_date}"
    )

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
