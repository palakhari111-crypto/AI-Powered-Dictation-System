from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
from backend.app.core.config import settings

@dataclass
class OCRResult:
    text: str
    confidence: float | None
    provider: str
    needs_review: bool
    message: str = ""

def extract_text(image_path: str) -> OCRResult:
    # Adapter boundary: replace this function with a handwriting-specific HTR provider.
    try:
        import pytesseract
        image = Image.open(image_path).convert("L")
        image = ImageEnhance.Contrast(image).enhance(1.7)
        image = image.filter(ImageFilter.SHARPEN)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        words, confidences = [], []
        for word, conf in zip(data["text"], data["conf"]):
            word = word.strip()
            try:
                score = float(conf)
            except (ValueError, TypeError):
                continue
            if word and score >= 0:
                words.append(word)
                confidences.append(score)
        text = " ".join(words)
        confidence = sum(confidences) / len(confidences) if confidences else None
        needs_review = not text or confidence is None or confidence < settings.OCR_MIN_CONFIDENCE
        return OCRResult(text, confidence, "tesseract", needs_review,
                         "Review the extracted text. Tesseract is a baseline and may not recognize handwriting reliably.")
    except Exception as exc:
        return OCRResult("", None, "unavailable", True,
                         f"OCR unavailable: {type(exc).__name__}. Install Tesseract and its Python package.")
