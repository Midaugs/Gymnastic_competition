# backend/app/pdf_utils.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io

def generate_results_pdf(competition, group, coach, children, results):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(20*mm, height-20*mm, f"Gymnastics Competition Results")
    p.setFont("Helvetica", 12)
    p.drawString(20*mm, height-28*mm, f"Competition Date: {competition.date}")
    p.drawString(20*mm, height-35*mm, f"Group: {group.name}")
    p.drawString(20*mm, height-42*mm, f"Referee/Coach: {coach.name} {coach.surname}")

    # headers
    y = height-55*mm
    headers = ["Name","Surname","Birthday","Participated","C1","C2","C3","C4","C5","Sum"]
    x_positions = [10, 45, 85, 120, 150, 165, 180, 195, 210, 225]  # in mm
    p.setFont("Helvetica-Bold", 10)
    for h, x in zip(headers, x_positions):
        p.drawString(x*mm, y, h)
    p.line(10*mm, y-2, (width-10*mm), y-2)
    p.setFont("Helvetica", 10)
    y -= 12

    for child in children:
        r = next((rr for rr in results if rr.child_id == child.id), None)
        if r:
            total = r.criteria1 + r.criteria2 + r.criteria3 + r.criteria4 + r.criteria5
            row = [
                child.name,
                child.surname,
                str(child.birthday),
                "Yes" if r.participated else "No",
                str(r.criteria1), str(r.criteria2), str(r.criteria3), str(r.criteria4), str(r.criteria5),
                str(total)
            ]
            for val, x in zip(row, x_positions):
                p.drawString(x*mm, y, val)
            y -= 12
            if y < 20*mm:  # new page if too low
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height-20*mm

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
