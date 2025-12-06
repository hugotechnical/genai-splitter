import re
import unicodedata
from app.core.config import settings

class TextUtils:
    @staticmethod
    def remove_accents(text: str) -> str:
        if not text:
            return ""
        nfkd_form = unicodedata.normalize('NFKD', text)
        s = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        return s.replace('đ', 'd').replace('Đ', 'D')

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        filename = TextUtils.remove_accents(filename)
        filename = re.sub(r'[^\w\s-]', '', filename).strip()
        return re.sub(r'[-\s]+', '_', filename)

    @staticmethod
    def clean_text_for_comparison(text: str) -> str:
        no_accents = TextUtils.remove_accents(text)
        clean_text = re.sub(r'[^a-zA-Z0-9]', ' ', no_accents)
        return re.sub(r'\s+', ' ', clean_text).strip().upper()

    @staticmethod
    def extract_header(text: str, lines_limit: int = settings.LINES_THRESHOLD) -> str:
        if not text:
            return ""
        return '\n'.join(text.split('\n')[:lines_limit])

    @staticmethod
    def is_blank_page(text: str) -> bool:
        if not text or len(text.strip()) == 0:
            return True
        noise = re.sub(r'[.\-–—_~•·›‰¾°]', '', text)
        noise = re.sub(r'\s+', '', noise)
        return len(noise) < settings.MIN_CONTENT_LENGTH