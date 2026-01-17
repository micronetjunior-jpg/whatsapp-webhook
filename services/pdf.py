from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER

def generar_pdf(texto):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(texto.replace("\n", "<br/>"), styles["Normal"])])
    buffer.seek(0)
    return buffer.read()