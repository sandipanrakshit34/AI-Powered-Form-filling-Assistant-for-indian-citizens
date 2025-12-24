# ocr_utils.py (FINAL VERSION for Hindi + Bengali + English)
import easyocr
import numpy as np
import fitz  # PyMuPDF (no poppler needed)
from PIL import Image
import os

# -------------------------------------------------------------------------
# ✅ LANGUAGE GROUPS (only bn, hi, en — as per your requirement)
# -------------------------------------------------------------------------

SCRIPT_GROUPS = {
    "devanagari": ["hi", "en"],       # Hindi + English
    "bangla": ["bn", "as", "en"],     # Bengali + Assamese + English
    "english": ["en"],                # English only fallback
}

# -------------------------------------------------------------------------
# ✅ Simple script detection (based on filename / probability)
# -------------------------------------------------------------------------

def guess_script_from_filename(path):
    """Very simple but effective script guessing."""
    name = path.lower()

    # Bengali
    if "bn" in name or "bengali" in name or "ben" in name:
        return "bangla"

    # Hindi (Devanagari)
    if "hin" in name or "hindi" in name or "hi" in name:
        return "devanagari"

    # Default fallback
    return "english"

# -------------------------------------------------------------------------
# ✅ Cached EasyOCR model loader
# -------------------------------------------------------------------------

def get_reader(script_group):
    """
    Load EasyOCR reader for a script group.
    Cached so models load only once.
    """
    if not hasattr(get_reader, "cache"):
        get_reader.cache = {}

    if script_group not in get_reader.cache:
        langs = SCRIPT_GROUPS[script_group]
        print(f"[OCR] Loading model for script: {script_group} → {langs}")
        get_reader.cache[script_group] = easyocr.Reader(langs, gpu=False)

    return get_reader.cache[script_group]

# -------------------------------------------------------------------------
# ✅ PDF → Image (with PyMuPDF, no poppler required)
# -------------------------------------------------------------------------

def pdf_to_images(pdf_path, dpi=350):
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

# -------------------------------------------------------------------------
# ✅ Main OCR function
# -------------------------------------------------------------------------

def extract_text(path):
    """
    Universal OCR handler:
    - Auto-select correct script model
    - Handle image + PDF
    - Use EasyOCR only
    """
    print("\n[OCR] Starting OCR for:", path)

    # 1. Guess script from filename
    script_group = guess_script_from_filename(path)
    reader = get_reader(script_group)

    ext = os.path.splitext(path)[1].lower()
    full_text = ""

    # ---------------------------------------------------------------------
    # ✅ If PDF → convert pages to images
    # ---------------------------------------------------------------------
    if ext == ".pdf":
        images = pdf_to_images(path)
        print(f"[OCR] PDF detected → {len(images)} pages")

        for img in images:
            arr = np.array(img)
            result = reader.readtext(arr)
            full_text += "\n".join([r[1] for r in result]) + "\n"

        return full_text.strip()

    # ---------------------------------------------------------------------
    # ✅ If normal image
    # ---------------------------------------------------------------------
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    result = reader.readtext(arr)
    text = "\n".join([r[1] for r in result])

    return text.strip()
