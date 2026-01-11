import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image as RLImage, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image as PILImage

def export_images_to_pdf(images, output_dir):
    pdf_path = os.path.join(output_dir, "Ion_gun_maps.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []
    data, row, temp_files = [], [], []

    for i, photo in enumerate(images):
        img = PILImage.open(photo.image_path)
        img = img.resize((250, 250), PILImage.LANCZOS)

        tmp = os.path.join(output_dir, f"_tmp_image_{i}.png")
        img.save(tmp)
        temp_files.append(tmp)

        cell = [
            RLImage(tmp),
            Spacer(1, 2 * mm),
            Paragraph(photo.name.removesuffix(".bmp"), styles["Normal"])
        ]

        row.append(cell)
        if len(row) == 2:
            data.append(row)
            row = []

    if row:
        row.append('')
        data.append(row)

    table = Table(data, colWidths=[90 * mm, 90 * mm])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    doc.build([table])

    for f in temp_files:
        if os.path.exists(f):
            os.remove(f)
    
    return pdf_path
