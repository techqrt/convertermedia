import os
import fitz 
import tempfile
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path
from pdf2docx import Converter
from media_converter import settings

# ===========================
# PDF → Images
# ===========================
def pdf_to_images(pdf_file, output_format="PNG"):
    """
    Convert a PDF file into a list of image file paths.
    Returns: list of image paths
    """
    output_files = []

    # Ensure persistent directory exists
    output_dir = Path(settings.MEDIA_ROOT) / "pdf_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf = fitz.open(pdf_file)
    base_name = Path(pdf_file).stem

    for i, page in enumerate(pdf):
        pix = page.get_pixmap(dpi=200)
        out_path = output_dir / f"{base_name}_page_{i+1}.{output_format.lower()}"
        pix.save(str(out_path))
        output_files.append(str(out_path))

    return output_files


# ===========================
# PDF → Word (DOCX)
# ===========================
def pdf_to_word(pdf_file, output_docx=None):
    """
    Convert PDF to Word document.
    Returns: output docx file path
    """
    if output_docx is None:
        fd, output_docx = tempfile.mkstemp(suffix=".docx")
        os.close(fd)

    cv = Converter(pdf_file)
    cv.convert(output_docx, start=0, end=None)
    cv.close()

    return output_docx


# ===========================
# Image → Other Formats
# ===========================
def image_convert(input_file, output_format="PNG"):
    """
    Convert image into another format (JPG, PNG, BMP, WBMP, ICO).
    For SVG output, raster is converted using cairosvg (optional).
    Returns: output file path
    """
    from cairosvg import svg2png  # used only if SVG input/output

    img = Image.open(input_file)

    # Handle transparency → JPG (white bg)
    if output_format.upper() == "JPG":
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # 3 = alpha channel
            img = background
        else:
            img = img.convert("RGB")

    # Save to temp file
    fd, out_path = tempfile.mkstemp(suffix=f".{output_format.lower()}")
    os.close(fd)
    img.save(out_path, output_format.upper())

    return out_path
