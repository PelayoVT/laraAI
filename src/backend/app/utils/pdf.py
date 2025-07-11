from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def split_line(text, max_length):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_length:
            current += " " + word if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def generar_pdf(conversacion_id, mensajes):
    os.makedirs("pdfs", exist_ok=True)
    pdf_path = f"pdfs/conversacion_{conversacion_id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Conversación ID: {conversacion_id}")
    y -= 30

    for msg in mensajes:
        line = f"[{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {msg.tipo.upper()}: {msg.contenido}"
        for subline in split_line(line, 100):
            c.drawString(50, y, subline)
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50

    c.save()
    return pdf_path
