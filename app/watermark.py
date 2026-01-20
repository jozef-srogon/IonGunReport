from reportlab.lib.utils import ImageReader

def draw_image_watermark(canvas, doc, image_path, opacity=0.15):
    canvas.saveState()
    try:
        canvas.setFillAlpha(opacity)
    except AttributeError:
        pass

    img = ImageReader(image_path)
    img_width, img_height = img.getSize()

    page_w, page_h = doc.pagesize

    scale = (page_w * 0.7) / img_width
    w = img_width * scale
    h = img_height * scale

    x = (page_w - w) / 2
    y = (page_h - h) / 2

    canvas.drawImage(
        img,
        x, y,
        width=w,
        height=h,
        mask='auto'
    )
    canvas.restoreState()