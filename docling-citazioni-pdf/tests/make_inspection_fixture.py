"""Create synthetic native/image/OCR-layer/blank pages for inspection tests.

Requires reportlab and Pillow. The OCR layer is intentionally inaccurate;
this fixture is source data, not an instruction or a real client document.
"""
from io import BytesIO
from pathlib import Path
import argparse

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


def create(destination):
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    image = Image.new('RGB', (900, 1270), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=36)
    draw.text((50, 140), 'PAGINA RASTER DI PROVA', fill='black', font=font)
    draw.text((50, 230), 'Importo richiesto: 1.200,00 euro', fill='black', font=font)
    data = BytesIO()
    image.save(data, format='PNG')
    data.seek(0)
    pdf = canvas.Canvas(str(destination), pagesize=A4, invariant=1)
    pdf.setFont('Helvetica', 12)
    pdf.drawString(45, 760, 'Pagina prevalentemente testuale: origine non certificata dal solo testo.')
    pdf.showPage()
    pdf.drawImage(ImageReader(data), 0, 0, width=A4[0], height=A4[1])
    pdf.showPage()
    data.seek(0)
    pdf.drawImage(ImageReader(data), 0, 0, width=A4[0], height=A4[1])
    hidden = pdf.beginText(45, 760)
    hidden.setFont('Helvetica', 12)
    hidden.setTextRenderMode(3)
    hidden.textLine('Livello OCR sintetico errato: importo richiesto 12.000,00 euro, da controllare.')
    pdf.drawText(hidden)
    pdf.showPage()
    pdf.showPage()  # A blank page must not be labelled a certain scan.
    pdf.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    create(parser.parse_args().output)
