import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
from app.core.config import settings
from app.utils.logger import logger

class PDFProcessor:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

    def process_pdf(self, path: str) -> dict:
        logger.info(f"Processing PDF: {path}")
        doc = fitz.open(path)
        full_text = ""
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if not text.strip():
                logger.debug(f"Page {page_num} has no text, attempting OCR.")
                text = self._ocr_page(page)
            
            full_text += text + "\n"
            pages.append({
                "page_num": page_num + 1,
                "text": text
            })

        doc.close()
        return {
            "full_text": full_text,
            "pages": pages
        }

    def _ocr_page(self, page) -> str:
        # Render page to image (pixmap)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Better resolution
        img_data = pix.tobytes("png")
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Enhance image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        # Threshold
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # OCR
        text = pytesseract.image_to_string(thresh)
        return text

pdf_processor = PDFProcessor()
