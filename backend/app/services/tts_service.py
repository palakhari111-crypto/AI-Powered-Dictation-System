from pathlib import Path
from gtts import gTTS
from backend.app.core.config import settings

def generate_audio(text: str, language: str = "en", filename: str = "dictation.mp3"):
    out_dir = Path(settings.AUDIO_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    gTTS(text=text, lang=language).save(str(path))
    return str(path)
