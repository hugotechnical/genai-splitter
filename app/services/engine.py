import re
from typing import Tuple, Optional, List
from dataclasses import dataclass, field
from thefuzz import fuzz

from app.core.config import settings
from app.utils.text import TextUtils

@dataclass
class DocumentRule:
    key: str
    category: str
    name: str
    exclude_keys: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

class MatchingEngine:
    """
    Engine so sánh khớp lệnh tối ưu:
    1. Section Filter: Loại bỏ dòng mục lục.
    2. Dynamic Threshold: Từ ngắn bắt chặt, từ dài bắt lỏng.
    3. Punctuation Guard: Chặn từ ngắn dính ngoặc/phẩy.
    4. Contextual Guard: Kiểm tra từ đứng trước.
    5. Sliding Window & Smart Case.
    """
    @staticmethod
    def find_match_with_score(page_text: str, rule: DocumentRule) -> Tuple[Optional[str], int]:
        header_lines = page_text.split('\n')[:settings.LINES_THRESHOLD]
        clean_key = TextUtils.clean_text_for_comparison(rule.key)
        key_word_count = len(clean_key.split())
        
        # --- 1. THIẾT LẬP NGƯỠNG ĐỘNG ---
        is_short_key = len(clean_key.replace(" ", "")) <= 4
        MIN_SCORE = 100 if is_short_key else settings.FUZZY_THRESHOLD

        best_score = 0
        best_text = None

        SECTION_PATTERN = r'^(?:I{1,3}|IV|V|VI{0,3}|IX|X|\d{1,2}|[A-Z])[\.\)]\s+'

        for line in header_lines:
            line = line.strip()
            if not line: continue

            # --- 2. BỘ LỌC MỤC LỤC ---
            if re.match(SECTION_PATTERN, line, re.IGNORECASE): continue
            if re.match(r'^(MỤC|PHẦN|CHƯƠNG)\s+\d+', line, re.IGNORECASE): continue

            words_in_line = line.split()
            total_words = len(words_in_line)
            if total_words < key_word_count: continue

            # --- 3. SLIDING WINDOW ---
            min_len = max(1, key_word_count - 1)
            max_len = min(total_words, key_word_count + 1)
            max_start_index = min(settings.MAX_KEYWORD_POSITION, total_words)

            for start_idx in range(total_words):
                if start_idx > max_start_index: break 
                
                for length in range(min_len, max_len + 1):
                    end_idx = start_idx + length
                    if end_idx > total_words: continue

                    candidate_words = words_in_line[start_idx:end_idx]
                    candidate_text_original = " ".join(candidate_words)
                    candidate_clean = TextUtils.clean_text_for_comparison(candidate_text_original)

                    score = fuzz.ratio(clean_key, candidate_clean)

                    if score >= MIN_SCORE:
                        # --- [LOGIC XỬ LÝ TỪ KHÓA NGẮN] ---
                        if is_short_key:
                            # Punctuation Guard: (CIC,
                            if re.search(r'[(),;]', candidate_text_original):
                                continue
                            # Contextual Guard: (Marky CIC
                            if start_idx > 0:
                                prev_word = words_in_line[start_idx - 1]
                                if '(' in prev_word: continue

                        # --- 4. SMART CASE CHECK ---
                        is_upper = candidate_text_original.isupper()
                        is_title = candidate_text_original.istitle()
                        letters = [c for c in candidate_text_original if c.isalpha()]
                        
                        is_mostly_upper = False
                        if letters:
                            upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
                            is_mostly_upper = upper_ratio > 0.75

                        if is_upper or is_title or is_mostly_upper:
                            if score > best_score:
                                best_score = score
                                best_text = candidate_text_original
        
        return best_text, best_score