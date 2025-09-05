from django.shortcuts import render
from django.http import FileResponse, HttpResponseBadRequest
from django.conf import settings
import os
from PIL import Image
from pdf2image import convert_from_path
from pdf2docx import Converter
from django.utils.text import get_valid_filename


# Centralized metadata for all operations
OPERATIONS_META = {
    "pdf_to_image": {
        "title": "PDF to Image",
        "subtitle": "Convert your PDF file into high-quality images",
        "button": "Upload PDF",
        "accept": ".pdf",
    },
    "pdf_to_word": {
        "title": "PDF to Word",
        "subtitle": "Convert your PDF file into editable Word documents",
        "button": "Upload PDF",
        "accept": ".pdf",
    },
    "image_to_jpg": {
        "title": "Image to JPG",
        "subtitle": "Convert any image into JPG format",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "image_to_png": {
        "title": "Image to PNG",
        "subtitle": "Convert any image into PNG format",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "image_to_bmp": {
        "title": "Image to BMP",
        "subtitle": "Convert any image into BMP format",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "image_to_wbmp": {
        "title": "Image to WBMP",
        "subtitle": "Convert any image into WBMP format",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "image_to_ico": {
        "title": "Image to ICO",
        "subtitle": "Convert any image into ICO format",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "image_to_svg": {
        "title": "Image to SVG",
        "subtitle": "Convert any image into SVG format (experimental)",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "resize_image": {
        "title": "Resize Image",
        "subtitle": "Resize your images to custom dimensions",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "image_to_webp": {
        "title": "Image to WEBP",
        "subtitle": "Convert your images into WEBP format",
        "button": "Upload Image",
        "accept": "image/*",
    },
    "image_to_avif": {
        "title": "Image to AVIF",
        "subtitle": "Convert your images into AVIF format",
        "button": "Upload Image",
        "accept": "image/*",
    },
}


def index(request):
    """Landing page with cards linking to detail pages."""
    return render(request, "index.html", {"operations": OPERATIONS_META})


def detail_page(request, operation):
    """Render the detail upload form for each operation dynamically."""
    meta = OPERATIONS_META.get(operation)
    if not meta:
        return HttpResponseBadRequest("Invalid operation")

    return render(request, "inner-page.html", {"meta": meta, "operation": operation})


def convert(request, operation):
    """Perform the actual conversion based on operation."""
    if request.method != "POST" or "file" not in request.FILES:
        return HttpResponseBadRequest("No file uploaded.")

    uploaded_file = request.FILES["file"]
    safe_filename = get_valid_filename(uploaded_file.name)
    input_path = os.path.join(settings.MEDIA_ROOT, safe_filename)

    # Save uploaded file
    with open(input_path, "wb+") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    output_path = os.path.join(settings.MEDIA_ROOT, f"converted_{safe_filename}")


    # ----- Conversion Logic -----
    try:
        if operation == "pdf_to_image":
            images = convert_from_path(input_path)
            output_path = output_path.replace(".pdf", ".jpg")
            images[0].save(output_path, "JPEG")

        elif operation == "pdf_to_word":
            output_path = output_path.replace(".pdf", ".docx")
            cv = Converter(input_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()

        elif operation.startswith("image_to_") or operation == "resize_image":
            img = Image.open(input_path)

            if operation == "image_to_jpg":
                output_path = os.path.splitext(output_path)[0] + ".jpg"
                img.convert("RGB").save(output_path, "JPEG")

            elif operation == "image_to_png":
                output_path = os.path.splitext(output_path)[0] + ".png"
                img.save(output_path, "PNG")

            elif operation == "image_to_bmp":
                output_path = os.path.splitext(output_path)[0] + ".bmp"
                img.save(output_path, "BMP")

            elif operation == "image_to_wbmp":
                output_path = os.path.splitext(output_path)[0] + ".wbmp"
                img.save(output_path, "WBMP")

            elif operation == "image_to_ico":
                output_path = os.path.splitext(output_path)[0] + ".ico"
                img.save(output_path, "ICO")

            elif operation == "image_to_svg":
                # PIL does not support SVG export → placeholder
                return HttpResponseBadRequest("SVG export not supported natively.")

            elif operation == "resize_image":
                try:
                    width = int(request.POST.get("width", 0))
                    height = int(request.POST.get("height", 0))
                except ValueError:
                    return HttpResponseBadRequest("Invalid width or height.")

                if width <= 0 or height <= 0:
                    return HttpResponseBadRequest("Width and height must be positive integers.")

                resized_img = img.resize((width, height))
                output_path = os.path.splitext(output_path)[0] + f"_resized.jpg"
                resized_img.convert("RGB").save(output_path, "JPEG")

            elif operation == "image_to_webp":
                output_path = os.path.splitext(output_path)[0] + ".webp"
                img.save(output_path, "WEBP")

            elif operation == "image_to_avif":
                output_path = os.path.splitext(output_path)[0] + ".avif"
                img.save(output_path, "AVIF")

        else:
            return HttpResponseBadRequest("Invalid operation")

    except Exception as e:
        return HttpResponseBadRequest(f"Conversion failed: {str(e)}")

    return FileResponse(open(output_path, "rb"), as_attachment=True)
