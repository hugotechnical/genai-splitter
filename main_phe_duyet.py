import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

import fitz  # PyMuPDF
from thefuzz import fuzz

from rules import SAMPLE_RULES


# ==============================================================================
# CONFIGURATION
# ==============================================================================

class Config:
    """Cấu hình các thông số xử lý tài liệu."""
    LINES_THRESHOLD = 20         # Số dòng đầu trang để quét tiêu đề
    MIN_CONTENT_LENGTH = 15      # Độ dài tối thiểu để coi là trang có nội dung
    PAGE_BREAK_DELIMITER = '--- Page Break ---'
    FUZZY_THRESHOLD = 90         # Ngưỡng mờ cơ bản (dùng cho exclude)
    DATA_DIR_PARSER = Path("data_parser")
    DATA_DIR = Path("data_input")
    OUTPUT_DIR = Path("data_output/results_ho_so_phe_duyet")
    
    # Từ khóa phải xuất hiện trong 5 từ đầu tiên của dòng (index 0-4)
    MAX_KEYWORD_POSITION = 4 

# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class DocumentRule:
    key: str
    category: str
    name: str
    exclude_keys: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

@dataclass
class Document:
    stt: int
    category: str
    name: str
    start: int
    end: int
    trigger: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stt": self.stt,
            "category": self.category,
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "trigger": self.trigger
        }

# ==============================================================================
# UTILITIES
# ==============================================================================

class TextUtils:
    @staticmethod
    def remove_accents(text: str) -> str:
        """Chuyển đổi chuỗi sang không dấu, giữ nguyên độ dài chuỗi để map index."""
        if not text:
            return ""
        nfkd_form = unicodedata.normalize('NFKD', text)
        s = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        return s.replace('đ', 'd').replace('Đ', 'D')

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Làm sạch tên file để lưu."""
        filename = TextUtils.remove_accents(filename)
        filename = re.sub(r'[^\w\s-]', '', filename).strip()
        return re.sub(r'[-\s]+', '_', filename)

    @staticmethod
    def clean_text_for_comparison(text: str) -> str:
        """Chuẩn hóa text để so sánh (Bỏ dấu, In hoa, Bỏ ký tự đặc biệt)."""
        no_accents = TextUtils.remove_accents(text)
        clean_text = re.sub(r'[^a-zA-Z0-9]', ' ', no_accents)
        return re.sub(r'\s+', ' ', clean_text).strip().upper()

    @staticmethod
    def extract_header(text: str, lines_limit: int = Config.LINES_THRESHOLD) -> str:
        if not text:
            return ""
        return '\n'.join(text.split('\n')[:lines_limit])

    @staticmethod
    def is_blank_page(text: str) -> bool:
        """Kiểm tra trang trắng hoặc trang chỉ có rác OCR."""
        if not text or len(text.strip()) == 0:
            return True
        noise = re.sub(r'[.\-–—_~•·›‰¾°]', '', text)
        noise = re.sub(r'\s+', '', noise)
        return len(noise) < Config.MIN_CONTENT_LENGTH

# ==============================================================================
# CORE LOGIC: MATCHING ENGINE (UPDATED)
# ==============================================================================

# class MatchingEngine:
#     """
#     Engine so sánh khớp lệnh tối ưu:
#     1. Section Filter: Loại bỏ dòng mục lục.
#     2. Dynamic Threshold: Từ ngắn bắt chặt, từ dài bắt lỏng.
#     3. [NEW] Punctuation Guard: Chặn từ ngắn dính ngoặc/phẩy (CIC, -> Loại).
#     4. Sliding Window & Smart Case.
#     """
#     @staticmethod
#     def find_match_with_score(page_text: str, rule: DocumentRule) -> Tuple[Optional[str], int]:
#         header_lines = page_text.split('\n')[:Config.LINES_THRESHOLD]
#         clean_key = TextUtils.clean_text_for_comparison(rule.key)
#         key_word_count = len(clean_key.split())
        
#         # --- 1. THIẾT LẬP NGƯỠNG ĐỘNG ---
#         # Kiểm tra xem có phải key ngắn không
#         is_short_key = len(clean_key.replace(" ", "")) <= 4
        
#         if is_short_key:
#             MIN_SCORE = 100 
#         else:
#             MIN_SCORE = Config.FUZZY_THRESHOLD

#         best_score = 0
#         best_text = None

#         SECTION_PATTERN = r'^(?:I{1,3}|IV|V|VI{0,3}|IX|X|\d{1,2}|[A-Z])[\.\)]\s+'

#         for line in header_lines:
#             line = line.strip()
#             if not line: continue

#             # --- 2. BỘ LỌC MỤC LỤC ---
#             if re.match(SECTION_PATTERN, line, re.IGNORECASE):
#                 continue
#             if re.match(r'^(MỤC|PHẦN|CHƯƠNG)\s+\d+', line, re.IGNORECASE):
#                 continue

#             words_in_line = line.split()
#             total_words = len(words_in_line)
#             if total_words < key_word_count: continue

#             # --- 3. SLIDING WINDOW ---
#             min_len = max(1, key_word_count - 1)
#             max_len = min(total_words, key_word_count + 1)
#             max_start_index = min(Config.MAX_KEYWORD_POSITION, total_words)

#             for start_idx in range(total_words):
#                 if start_idx > max_start_index: break 
                
#                 for length in range(min_len, max_len + 1):
#                     end_idx = start_idx + length
#                     if end_idx > total_words: continue

#                     candidate_words = words_in_line[start_idx:end_idx]
#                     candidate_text_original = " ".join(candidate_words)
#                     candidate_clean = TextUtils.clean_text_for_comparison(candidate_text_original)

#                     score = fuzz.ratio(clean_key, candidate_clean)

#                     if score >= MIN_SCORE:
#                         # --- [UPDATE QUAN TRỌNG] LOẠI BỎ KÝ TỰ RÁC CHO KEY NGẮN ---
#                         # Nếu là Key ngắn (CIC), tuyệt đối không chấp nhận dính dấu câu
#                         # Ví dụ: "(CIC," -> Có chứa '(', ',' -> LOẠI
#                         if is_short_key:
#                             # Regex tìm: Ngoặc đơn, Dấu phẩy, Chấm phẩy
#                             if re.search(r'[(),;]', candidate_text_original):
#                                 continue

#                         # --- 4. SMART CASE CHECK ---
#                         is_upper = candidate_text_original.isupper()
#                         is_title = candidate_text_original.istitle()
                        
#                         letters = [c for c in candidate_text_original if c.isalpha()]
#                         if letters:
#                             upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
#                             is_mostly_upper = upper_ratio > 0.75
#                         else:
#                             is_mostly_upper = False

#                         if is_upper or is_title or is_mostly_upper:
#                             if score > best_score:
#                                 best_score = score
#                                 best_text = candidate_text_original
        
#         return best_text, best_score

class MatchingEngine:
    """
    Engine so sánh khớp lệnh tối ưu:
    1. Section Filter: Loại bỏ dòng mục lục.
    2. Dynamic Threshold: Từ ngắn bắt chặt, từ dài bắt lỏng.
    3. Punctuation Guard: Chặn từ ngắn dính ngoặc/phẩy (CIC, -> Loại).
    4. [NEW] Contextual Guard: Kiểm tra từ đứng trước để loại bỏ nhiễu.
    5. Sliding Window & Smart Case.
    """
    @staticmethod
    def find_match_with_score(page_text: str, rule: DocumentRule) -> Tuple[Optional[str], int]:
        header_lines = page_text.split('\n')[:Config.LINES_THRESHOLD]
        clean_key = TextUtils.clean_text_for_comparison(rule.key)
        key_word_count = len(clean_key.split())
        
        # --- 1. THIẾT LẬP NGƯỠNG ĐỘNG ---
        is_short_key = len(clean_key.replace(" ", "")) <= 4
        
        if is_short_key:
            MIN_SCORE = 100 
        else:
            MIN_SCORE = Config.FUZZY_THRESHOLD

        best_score = 0
        best_text = None

        SECTION_PATTERN = r'^(?:I{1,3}|IV|V|VI{0,3}|IX|X|\d{1,2}|[A-Z])[\.\)]\s+'

        for line in header_lines:
            line = line.strip()
            if not line: continue

            # --- 2. BỘ LỌC MỤC LỤC ---
            if re.match(SECTION_PATTERN, line, re.IGNORECASE):
                continue
            if re.match(r'^(MỤC|PHẦN|CHƯƠNG)\s+\d+', line, re.IGNORECASE):
                continue

            words_in_line = line.split()
            total_words = len(words_in_line)
            if total_words < key_word_count: continue

            # --- 3. SLIDING WINDOW ---
            min_len = max(1, key_word_count - 1)
            max_len = min(total_words, key_word_count + 1)
            max_start_index = min(Config.MAX_KEYWORD_POSITION, total_words)

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
                        # --- [UPDATE] LOGIC XỬ LÝ TỪ KHÓA NGẮN ---
                        if is_short_key:
                            # 1. Punctuation Guard: Tuyệt đối không chấp nhận dính dấu câu BÊN TRONG
                            # Ví dụ: "(CIC," -> Có chứa '(', ',' -> LOẠI
                            if re.search(r'[(),;]', candidate_text_original):
                                continue

                            # 2. [NEW] Contextual Guard: Kiểm tra từ đứng TRƯỚC có chứa ký tự nhiễu không
                            # Ví dụ: "(Marky CIC" -> từ trước là "(Marky" -> LOẠI
                            if start_idx > 0:
                                prev_word = words_in_line[start_idx - 1]
                                # Nếu từ đứng trước chứa dấu ngoặc mở, khả năng cao là nhiễu
                                if '(' in prev_word:
                                    continue

                        # --- 4. SMART CASE CHECK ---
                        is_upper = candidate_text_original.isupper()
                        is_title = candidate_text_original.istitle()
                        
                        letters = [c for c in candidate_text_original if c.isalpha()]
                        if letters:
                            upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
                            is_mostly_upper = upper_ratio > 0.75
                        else:
                            is_mostly_upper = False

                        if is_upper or is_title or is_mostly_upper:
                            if score > best_score:
                                best_score = score
                                best_text = candidate_text_original
        
        return best_text, best_score
    
# ==============================================================================
# PROCESSOR LOGIC
# ==============================================================================

class DocumentProcessor:
    def __init__(self, rules_data: List[Tuple]):
        self.rules = self._parse_rules(rules_data)
        self.documents: List[Document] = []
        self.current_doc_state: Dict = {"start": None}

    def _parse_rules(self, rules_data: List[Tuple]) -> List[DocumentRule]:
        rules = []
        for item in rules_data:
            key, category, name, *rest = item
            exclude_keys = rest[0] if len(rest) > 0 else []
            aliases = rest[1] if len(rest) > 1 else []
            rules.append(DocumentRule(key, category, name, exclude_keys, aliases))
        return rules

    def _find_matching_rule(self, page_text: str) -> Optional[Tuple[DocumentRule, str]]:
        header_raw = TextUtils.extract_header(page_text)
        header_clean_for_comparison = TextUtils.clean_text_for_comparison(header_raw)
        
        candidates = []

        # Duyệt qua TẤT CẢ các rules để tìm ứng viên
        for rule in self.rules:
            # 1. Check Alias (Ưu tiên cao nhất)
            for alias in rule.aliases:
                normalized_alias = TextUtils.clean_text_for_comparison(alias)
                if normalized_alias in header_clean_for_comparison:
                    # Alias khớp 100% -> Score 100, lấy độ dài alias
                    candidates.append((100, len(alias), rule, alias)) 
                    break 
            
            # 2. Check Engine (Nếu chưa khớp alias)
            # Hàm này trả về trigger text và score của rule đó trên trang hiện tại
            trigger_text, score = MatchingEngine.find_match_with_score(page_text, rule)
            if trigger_text:
                candidates.append((score, len(rule.key), rule, trigger_text))

        # --- LOGIC "BEST MATCH WINS" ---
        if not candidates:
            return None

        # Sắp xếp ứng viên để chọn ra người chiến thắng:
        # Tiêu chí 1: Độ dài từ khóa (x[1]) -> Càng dài càng cụ thể (Tờ trình phê duyệt > Phê duyệt)
        # Tiêu chí 2: Điểm số (x[0]) -> Điểm cao hơn thắng
        candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
        
        # Lấy ứng viên tốt nhất
        best_score, _, best_rule, best_trigger = candidates[0]

        # --- CHECK EXCLUDE (LOẠI TRỪ) TRÊN ỨNG VIÊN TỐT NHẤT ---
        is_excluded = False
        for ex_key in best_rule.exclude_keys:
            ex_clean = TextUtils.clean_text_for_comparison(ex_key)
            # Check khớp chính xác
            if ex_clean in header_clean_for_comparison:
                is_excluded = True
                break
            # Check fuzzy cho exclude (Dùng threshold thấp hơn chút để an toàn)
            if fuzz.partial_ratio(ex_clean, header_clean_for_comparison) >= 85:
                is_excluded = True
                break
        
        if is_excluded:
            return None

        # Logic loại bỏ tài liệu "ĐÍNH KÈM"
        if "DINH KEM" in header_clean_for_comparison:
            key_check = TextUtils.clean_text_for_comparison(best_trigger if best_trigger else best_rule.key)
            key_pos = header_clean_for_comparison.find(key_check)
            attach_pos = header_clean_for_comparison.find("DINH KEM")
            # Nếu chữ ĐÍNH KÈM xuất hiện trước Từ khóa -> Đây là phụ lục đính kèm, không phải văn bản chính
            if attach_pos != -1 and key_pos != -1 and attach_pos < key_pos:
                return None

        return (best_rule, best_trigger)

    def _finalize_document(self, end_page: int) -> None:
        if self.current_doc_state.get("start") is not None:
            doc = Document(
                stt=len(self.documents) + 1,
                category=self.current_doc_state["category"],
                name=self.current_doc_state["name"],
                start=self.current_doc_state["start"],
                end=end_page,
                trigger=self.current_doc_state["trigger"]
            )
            self.documents.append(doc)
            self.current_doc_state = {"start": None}

    def process_pages(self, pages: List[str]) -> List[Document]:
        total_pages = len(pages)
        print(f"** Bắt đầu xử lý {total_pages} trang (Cơ chế: Best Match Wins & Strict Case) **\n")

        for i, page_text in enumerate(pages):
            page_num = i + 1
            page_text_clean = page_text.strip()
            
            if TextUtils.is_blank_page(page_text_clean):
                if self.current_doc_state.get("start") is None:
                    # Trang trắng đầu file
                    pass 
                continue

            match_result = self._find_matching_rule(page_text_clean)
            
            matched_rule = None
            trigger_text = None
            if match_result:
                matched_rule, trigger_text = match_result

            is_continuation = False
            # Nếu tìm thấy rule, check xem có phải là rule của tài liệu đang mở không
            if matched_rule and self.current_doc_state.get("start") is not None:
                if matched_rule.name == self.current_doc_state.get("name"):
                    is_continuation = True

            if matched_rule and not is_continuation:
                # Phát hiện tài liệu MỚI -> Đóng tài liệu cũ
                print(f" -> P{page_num}: NEW DOC: '{matched_rule.name}' (Trigger: '{trigger_text}')")
                self._finalize_document(page_num - 1)
                
                # Mở tài liệu mới
                self.current_doc_state = {
                    "category": matched_rule.category,
                    "name": matched_rule.name,
                    "start": page_num,
                    "trigger": f"{matched_rule.key} -> '{trigger_text}'" 
                }
            else:
                # Không tìm thấy rule nào
                if self.current_doc_state.get("start") is None:
                    # Nếu chưa có tài liệu nào đang mở -> Đánh dấu là chưa xác định
                    self.documents.append(Document(
                        len(self.documents) + 1, "Phân loại", "Tài liệu không xác định", page_num, page_num, "NOT_FOUND"
                    ))
                # Nếu đang có tài liệu mở -> Coi như trang tiếp theo của tài liệu đó (Do nothing)

        # Đóng tài liệu cuối cùng
        self._finalize_document(total_pages)
        return self.documents

# ==============================================================================
# FILE HANDLERS
# ==============================================================================

class FileHandler:
    @staticmethod
    def load_json(json_path: str) -> Optional[Dict]:
        path = Path(json_path)
        if not path.exists():
            path = Config.DATA_DIR_PARSER / json_path
            if not path.exists():
                print(f"[Error] Không tìm thấy file JSON: {json_path}")
                return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f, strict=False) 
        except Exception as e:
            print(f"[Error] Lỗi đọc JSON: {e}")
            return None

    @staticmethod
    def split_pdf(documents: List[Document], original_pdf_path: str, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = Path(original_pdf_path)
        if not pdf_path.exists():
            pdf_path = Config.DATA_DIR / original_pdf_path
        
        if not pdf_path.exists():
            print(f"[Skip] Không tìm thấy file PDF gốc để cắt: {original_pdf_path}")
            return

        try:
            src_doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"[Error] Không mở được PDF: {e}")
            return

        print(f"\nĐang cắt file PDF vào: {output_dir} ...")
        count = 0
        for doc in documents:
            # Bỏ qua trang trắng hoặc trang không xác định chỉ có 1 trang
            if doc.trigger in ["BLANK_PAGE", "NOT_FOUND"] and doc.start == doc.end:
                 continue

            with fitz.open() as new_doc:
                start_idx = doc.start - 1
                end_idx = min(doc.end - 1, len(src_doc) - 1)
                
                if start_idx < len(src_doc):
                    new_doc.insert_pdf(src_doc, from_page=start_idx, to_page=end_idx)
                    
                    if len(new_doc) > 0:
                        safe_name = TextUtils.sanitize_filename(doc.name)
                        out_name = f"{doc.stt:02d}_{doc.start}-{doc.end}_{safe_name}.pdf"
                        new_doc.save(output_dir / out_name)
                        count += 1
        
        src_doc.close()
        print(f"Hoàn tất cắt {count} file.")

    @staticmethod
    def display_results(documents: List[Document]) -> None:
        print("\n" + "=" * 110)
        print(f"{'STT | TÊN TÀI LIỆU':<50} | {'TRANG':<10} | {'TRIGGER'}")
        print("-" * 110)
        for doc in documents:
            page_range = f"{doc.start}-{doc.end}" if doc.start != doc.end else str(doc.start)
            print(f"{str(doc.stt) + ' | ' + doc.name:<50} | {page_range:<10} | {doc.trigger}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    json_filename = "ho-so-phe-duyet-2.json"
    pdf_filename = "ho-so-phe-duyet.pdf"
    
    # 1. Load Data
    data = FileHandler.load_json(json_filename)
    if not data:
        return

    content = data.get('extracted_content', '')
    pages = re.split(Config.PAGE_BREAK_DELIMITER, content)

    # 2. Process
    processor = DocumentProcessor(rules_data=SAMPLE_RULES)
    documents = processor.process_pages(pages)

    # 3. Output
    FileHandler.display_results(documents)
    FileHandler.split_pdf(documents, pdf_filename, Config.OUTPUT_DIR)

if __name__ == "__main__":
    main()