import json
import re
import os
import unicodedata
from typing import List, Dict, Optional, Any
import fitz
import pandas as pd
# --- THƯ VIỆN MỚI CHO FUZZY MATCHING ---
try:
    from thefuzz import fuzz
except ImportError:
    print("LỖI: Chưa cài đặt thư viện 'thefuzz'. Vui lòng chạy: pip install thefuzz")
    exit()

# ==============================================================================
# **CẤU HÌNH TOÀN CỤC**
# ==============================================================================

class Config:
    """**Cấu hình các thông số xử lý tài liệu**"""
    LINES_THRESHOLD = 22        # Số dòng đầu trang để quét tiêu đề
    MIN_CONTENT_LENGTH = 15     # Độ dài tối thiểu để coi là trang có nội dung
    PAGE_BREAK_DELIMITER = '--- Page Break ---'
    MAX_KEYWORD_POSITION = 4    # Nới lỏng vị trí từ khóa để fuzzy search hoạt động tốt hơn
    FUZZY_THRESHOLD = 90        # ĐỘ CHÍNH XÁC TỐI THIỂU (Thang 100). 
                                # VD: "GIALNGAN" vs "GIAI NGAN" sẽ có điểm ~90 -> OK

def remove_accents(input_str):
    """
    Chuyển đổi chuỗi sang không dấu và viết hoa toàn bộ.
    Ví dụ: "Giấy Hẹn" -> "GIAY HEN"
    """
    if not input_str:
        return ""
    # Chuẩn hóa unicode tổ hợp sang dựng sẵn
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    # Lọc bỏ các dấu kết hợp (combining characters)
    result = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return result.strip()

def sanitize_filename(filename):
    """Chuyển đổi tên file thành dạng an toàn để lưu"""
    filename = remove_accents(filename)
    filename = re.sub(r'[^\w\s-]', '', filename).strip()
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename

def load_json_safe(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f, strict=False)
    except Exception:
        return None

# ==============================================================================
# **ĐỊNH NGHĨA CẤU TRÚC DỮ LIỆU**
# ==============================================================================

class DocumentRule:
    def __init__(self, key: str, category: str, name: str, exclude_keys: Optional[List[str]] = None):
        self.key = key              # KEYWORD LÀ CHỮ IN HOA
        self.category = category
        self.name = name
        self.exclude_keys = exclude_keys or []

class Document:
    def __init__(self, stt: int, category: str, name: str, start: int, end: int, trigger: str):
        self.stt = stt
        self.category = category
        self.name = name
        self.start = start
        self.end = end
        self.trigger = trigger
   
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
# **DANH SÁCH QUY TẮC NHẬN DIỆN TÀI LIỆU**
# ==============================================================================

class DocumentRules:
    @staticmethod
    def get_rules() -> List[DocumentRule]:
        rules_data = [
            # --- NHÓM: HỒ SƠ TÍN DỤNG ---
            ("HOP DONG CHO VAY", "Hồ sơ tín dụng", "Hợp đồng cho vay"),
            ("PHU LUC HOP DONG", "Hồ sơ tín dụng", "Phụ lục hợp đồng cho vay"),
            ("HOP DONG SUA DOI BO SUNG", "Hồ sơ tín dụng", "Phụ lục hợp đồng cho vay"),
            ("THONG BAO CAP TIN DUNG", "Hồ sơ tín dụng", "Thông báo cấp tín dụng"),
            ("HOP DONG BAO LANH", "Hồ sơ tín dụng", "Hợp đồng bảo lãnh"),
            ("THOA THUAN KHUNG VE CAP TIN DUNG", "Hồ sơ tín dụng", "Thỏa thuận khung+PL về cấp BL+PL cho vay..."),
            ("PHU LUC CAC THOA THUAN CU THE", "Hồ sơ tín dụng", "Thỏa thuận khung+PL về cấp BL+PL cho vay..."),
            ("PHU LUC THOA THUAN CU THE", "Hồ sơ tín dụng", "Thỏa thuận khung+PL về cấp BL+PL cho vay..."),
            ("GIAY CAM KET", "Hồ sơ tín dụng", "Giấy cam kết"),
            ("THOA THUAN SU DUNG HE THONG TU DONG", "Hồ sơ tín dụng", "Thỏa thuận sử dụng hệ thống"),
            ("VAN BAN XAC NHAN", "Hồ sơ tín dụng", "Văn bản xác nhận dữ liệu"),

            # --- NHÓM: HỒ SƠ BẢO HIỂM ---

            ("VAN BAN CHUNG NHAN", "Hồ sơ khác", "VĂN BẢN CHỨNG NHẬN"), # Lưu ý: Key này khá chung chung
            ("GIAY CHUNG NHAN", "Hồ sơ bảo hiểm", "GIẤY CHỨNG NHẬN BẢO HIỂM"), # Lưu ý: Key này khá chung chung
            ("GIAY CHUNG NHAN BAO HIEM", "Hồ sơ bảo hiểm", "Hợp đồng bảo hiểm"),
            ("GIAY XAC NHAN CHUYEN QUYEN THU HUONG BAO HIEM", "Hồ sơ bảo hiểm", "Chuyển quyền thụ hưởng bảo hiểm"),
            ("HOA DON GIA TRI GIA TANG", "Hồ sơ bảo hiểm", "Hóa đơn bảo hiểm"), # Cần logic check thêm chữ "BẢO HIỂM" trong nội dung
            ("PHIEU THU", "Hồ sơ bảo hiểm", "Phiếu thu"), # Cần logic check thêm chữ "NỘP PHÍ BẢO HIỂM"
            ("DE NGHI TAI TUC HOP DONG BAO HIEM", "Hồ sơ bảo hiểm", "Đề nghị tái tục hợp đồng bảo hiểm"),
            ("APP@VPB.COM.VN", "Hồ sơ bảo hiểm", "Mail bảo hiểm"),
            ("GIAY YEU CAU BAO HIEM", "Hồ sơ bảo hiểm", "Giấy yêu cầu bảo hiểm"),

            # --- NHÓM: HỒ SƠ TÀI SẢN ---
            ("GIAY CHUNG NHAN", "Hồ sơ tài sản", "Giấy chứng nhận BĐS"), # Trùng key với BH, cần xử lý ưu tiên hoặc ngữ cảnh
            ("BAO CAO DINH GIA TAI SAN", "Hồ sơ tài sản", "Báo cáo định giá tài sản"),
            ("HOP DONG THE CHAP", "Hồ sơ tài sản", "Hợp đồng thế chấp"),
            ("HOP DONG CAM CO", "Hồ sơ tài sản", "Hợp đồng thế chấp"),
            ("HOP DONG BAO DAM", "Hồ sơ tài sản", "Hợp đồng thế chấp"),
            # ("PHIEU YEU CAU DANG KY BIEN PHAP BAO DAM", "Hồ sơ tài sản", "Đăng ký GDBĐ"),
            ("PHIEU YEU CAU DANG KY", "Hồ sơ tài sản", "Đăng ký GDBĐ"),
            ("DON DANG KY THE CHAP", "Hồ sơ tài sản", "Đăng ký GDBĐ"),
            ("BIEN BAN DINH GIA TAI SAN", "Hồ sơ tài sản", "Biên bản định giá tài sản"),
            ("GIAY BIEN NHAN HO SO TAI SAN BAO DAM", "Hồ sơ tài sản", "Giấy biên nhận hồ sơ tài sản bảo đảm"),
            ("PHIEU NHAP KHO TAI SAN BAO DAM", "Hồ sơ tài sản", "Nhập kho"),
            ("CHUNG NHAN DANG KY XE O TO", "Hồ sơ tài sản", "Đăng ký xe"),
            # ("GIAY HEN", "Hồ sơ tài sản", "Giấy hẹn"),
            ("GIAY CHUNG NHAN KIEM DINH", "Hồ sơ tài sản", "Đăng kiểm"),
            ("CAM KET BAN GIAO GIAY TO XE", "Hồ sơ tài sản", "Cam kết bàn giao giấy tờ xe"),
            ("HOP DONG TIEN GUI CO KY HAN", "Hồ sơ tài sản", "Hợp đồng tiền gửi"),
            ("GIAY DE NGHI PHONG TOA SO DU TIEN GUI", "Hồ sơ tài sản", "Đề nghị phong tỏa"),
            ("DE NGHI XAC NHAN VA QUAN LY TAI SAN BAO DAM", "Hồ sơ tài sản", "ĐN xác nhận và quản lý tài sản bảo đảm"),
            ("GIAY BIEN NHAN TAI SAN", "Hồ sơ tài sản", "Giấy biên nhận tài sản"),
            ("HOP DONG CAM CO", "Hồ sơ tài sản", "Hợp đồng cầm cố"), # Key này xuất hiện lần 2 cho loại hồ sơ riêng biệt

            # --- NHÓM: HỒ SƠ GIẢI NGÂN/PHÁT HÀNH BẢO LÃNH ---
            ("TO TRINH", "Hồ sơ giải ngân/phát hành bảo lãnh", "Tờ trình"),
            ("KHE UOC", "Hồ sơ giải ngân/phát hành bảo lãnh", "KUNN"),
            ("DE NGHI PHAT HANH BAO LANH", "Hồ sơ giải ngân/phát hành bảo lãnh", "Đề nghị phát hành bảo lãnh"),

            # --- NHÓM: HỒ SƠ CHỨNG MINH MỤC ĐÍCH ---
            ("HOP DONG MUA BAN", "Hồ sơ chứng minh mục đích", "Hợp đồng"),
            ("HOP DONG KINH TE", "Hồ sơ chứng minh mục đích", "Hợp đồng"),
            ("DON DAT HANG", "Hồ sơ chứng minh mục đích", "Hợp đồng"),
            ("HOA DON", "Hồ sơ chứng minh mục đích", "Hóa đơn"), # Cẩn thận nhầm với hóa đơn bảo hiểm
            ("CONG NO", "Hồ sơ chứng minh mục đích", "Đối chiếu công nợ"),
            ("DE NGHI THANH TOAN", "Hồ sơ chứng minh mục đích", "Đề nghị thanh toán"),
            ("THONG BAO", "HỒ SƠ KHÁC", "Thông báo"),
            ("GIAY DE NGHI", "HỒ SƠ KHÁC", "Giấy đề nghị"),
            ("HOP DONG BAO HIEM", "HỒ SƠ KHÁC", "Hợp đồng bảo hiểm"),
            ("PHIEU PHAN LOAI RUI RO", "HỒ SƠ KHÁC", "Phiếu phân loại rủi ro"),
            ("PHIEU KHAI BAO THONG TIN", "HỒ SƠ KHÁC", "Phiếu khai báo thông tin"),
        ]
                    
        rules = []
        for item in rules_data:
            key, category, name, *rest = item
            exclude_keys = rest[0] if rest else None
            rules.append(DocumentRule(key, category, name, exclude_keys))
        return rules

# ==============================================================================
# **LỚP XỬ LÝ CHUỖI VÀ HEADER (CẬP NHẬT LOGIC FUZZY)**
# ==============================================================================

# ==============================================================================
# **LỚP XỬ LÝ CHUỖI VÀ HEADER (CẬP NHẬT LOGIC FUZZY)**
# ==============================================================================

# ==============================================================================
# **LỚP XỬ LÝ CHUỖI VÀ HEADER (CẬP NHẬT LOGIC FUZZY VÀ COLON CHECK)**
# ==============================================================================
class TextProcessor:
    """**Lớp xử lý và chuẩn hóa văn bản**"""
    
    @staticmethod
    def remove_accents(text: str) -> str:
        if not text: return ""
        normalized = unicodedata.normalize('NFD', text)
        no_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return no_accents.replace('đ', 'd').replace('Đ', 'D')
    
    @staticmethod
    def normalize_text_strict(text: str) -> str:
        """
        Chuẩn hóa để so sánh fuzzy:
        - Bỏ dấu.
        - Giữ nguyên Case (để ưu tiên IN HOA).
        - Chỉ giữ lại ký tự chữ và số.
        """
        no_accents = TextProcessor.remove_accents(text)
        clean_text = re.sub(r'[^a-zA-Z0-9]', ' ', no_accents)
        return re.sub(r'\s+', ' ', clean_text).strip()

    @staticmethod
    def extract_header(text: str, lines_limit: int = Config.LINES_THRESHOLD) -> str:
        if not text: return ""
        header_lines = text.split('\n')[:lines_limit]
        # Giữ nguyên bản gốc để colon check (:) hoạt động trên text gốc
        return '\n'.join(header_lines)
    
    @staticmethod
    def is_mostly_upper(text: str, threshold: float = 0.8) -> bool:
        # Lấy các ký tự là chữ cái
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return False  # Không có chữ cái thì không coi là uppercase

        # Đếm số chữ cái viết hoa
        upper_count = sum(c.isupper() for c in letters)

        # Tính tỷ lệ
        return upper_count / len(letters) >= threshold
    
    @staticmethod
    def word_overlap(keyword: str, search_text: str):
        A = set(keyword.lower().split())
        B = set(search_text.lower().split())
        return len(A & B) / min(len(A), len(B)) * 100 + 5

    @staticmethod
    def check_keyword_position(original_text: str, keyword: str, page_num) -> bool:
        """
        Kiểm tra từ khóa bằng FUZZY MATCHING (Chấp nhận lỗi OCR) và 
        CẬP NHẬT: Loại bỏ nếu có dấu ":" ngay trước hoặc sau từ khóa.
        """
        if not original_text or not keyword: return False
        
        # Lấy các dòng đầu tiên (original text, chưa chuẩn hóa) để kiểm tra dấu ":"
        original_lines = original_text.split('\n')[:Config.LINES_THRESHOLD]
        
        # Chuẩn hóa keyword một lần (keyword trong rule luôn là IN HOA)
        keyword_norm = TextProcessor.normalize_text_strict(keyword)

        for line_idx, original_line in enumerate(original_lines):
            if not original_line.strip(): continue

            # ==================================================================
            # 1. KIỂM TRA COLON (DẤU HAI CHẤM - YÊU CẦU MỚI)
            # Dùng line gốc để check vì ký tự ":" bị xóa trong `normalize_text_strict`
            # ==================================================================
            # Dùng regex để tìm kiếm với khoảng trắng tùy chọn
            # Mẫu 1: Dấu ":" trước từ khóa (ví dụ: ": DE NGHI...")
            pattern_before = r':\s*' + re.escape(keyword)
            # Mẫu 2: Dấu ":" sau từ khóa (ví dụ: "DE NGHI :\s...")
            pattern_after = re.escape(keyword) + r'\s*:'
            
            # Loại bỏ dấu và chuẩn hóa line gốc thành IN HOA
            line_upper = remove_accents(original_line).upper()
            
            if re.search(pattern_before, line_upper, re.IGNORECASE) or \
               re.search(pattern_after, line_upper, re.IGNORECASE):
                print(f"   **Cảnh báo**: Key '{keyword}' bị loại vì có dấu ':' ngay cạnh (trang/dòng: {line_idx+1}).")
                continue # Bỏ qua dòng này và chuyển sang dòng tiếp theo để tìm kiếm tiếp

            # ==================================================================
            # 2. CHUẨN HÓA VÀ FUZZY MATCHING (LOGIC CŨ)
            # ==================================================================
            
            # Chuẩn hóa dòng văn bản (không dấu, chỉ chữ/số)
            line_norm = TextProcessor.normalize_text_strict(original_line)

            # Xử lý lỗi OCR: XÓA KÝ TỰ LẶP "Cc" HOẶC "cc" Ở ĐẦU DÒNG
            line_norm = re.sub(r'^[Cc]{2}\s*', '', line_norm)
            
            # Giới hạn vùng tìm kiếm (Search Window)
            search_window_len = len(keyword_norm) + 25 
            search_text = line_norm[:search_window_len]

            # --- LOGIC MỚI: ADAPTIVE CHECKING ---
            
            if not search_text: continue

            # A. Kiểm tra tỷ lệ In Hoa (Heuristic)
            # Nếu là tiêu đề xịn thì thường là IN HOA HẾT
            
            is_upper_case = TextProcessor.is_mostly_upper(search_text)
            
            # Nếu không phải in hoa hết, thì ÍT NHẤT ký tự đầu phải in hoa (Title Case)
            # Ví dụ: "thông tin..." (bỏ) vs "Thông tin..." (lấy)
            if not is_upper_case:
                first_char = search_text[0]
                # Nếu ký tự đầu là chữ thường -> Khả năng cao là văn bản rác -> Bỏ qua
                if first_char.islower(): 
                    continue

            # B. Thiết lập Ngưỡng điểm (Adaptive Threshold)
            # Nếu là IN HOA: Dễ tính hơn (90 điểm)
            # Nếu là Thường: Khắt khe hơn (95 điểm) để tránh bắt nhầm từ na ná
            required_score = Config.FUZZY_THRESHOLD 
            if not is_upper_case:
                required_score += 5  # Tăng độ khó lên 5 điểm

            # KIỂM TRA ĐIỀU KIỆN IN HOA và độ dài tối thiểu
            # if page_num == 122 and keyword_norm == "PHU LUC CAC THOA THUAN CU THE":
            #     print(search_text)
            #     print(len(search_text))
            #     print(len(keyword_norm))
            if len(search_text) < len(keyword_norm) * 0.6:
                continue
            score = fuzz.WRatio(keyword_norm, search_text.upper())
            if keyword_norm == "PHU LUC CAC THOA THUAN CU THE" and page_num == 141:
                print(search_text, keyword_norm, score, required_score, TextProcessor.word_overlap(keyword_norm, search_text.upper()))

            if score >= required_score:
                print(f"   -> Matched: '{keyword}' (Text: '{search_text}') - Score: {score}% (Ngưỡng: {required_score})")
                return True
        
        return False
# ==============================================================================
# **LỚP XỬ LÝ TÀI LIỆU**
# ==============================================================================

# ==============================================================================
# **LỚP XỬ LÝ TÀI LIỆU (CẬP NHẬT)**
# ==============================================================================

class DocumentProcessor:
    def __init__(self):
        self.rules = DocumentRules.get_rules()
        self.documents: List[Document] = []
   
    def _is_blank_page(self, text: str) -> bool:
        clean_text = re.sub(r'\s+', '', text)
        return len(clean_text) < Config.MIN_CONTENT_LENGTH
   
    def _find_matching_rule(self, original_text: str, page_num) -> Optional[DocumentRule]:
        header_strict = TextProcessor.extract_header(original_text)
        header_upper_check = header_strict.upper()

        for rule in self.rules:
            # 1. Logic loại trừ (Exclude)
            # Fuzzy check cho exclude keys luôn nếu cần, nhưng exact match thường đủ cho loại trừ
            if "DINH KEM" in header_upper_check:
                pass # Logic đính kèm phức tạp, giữ nguyên hoặc tùy chỉnh

            # 2. Kiểm tra KEYWORD bằng FUZZY LOGIC
            if TextProcessor.check_keyword_position(original_text, rule.key, page_num):
               
                # 3. Kiểm tra Exclude Keys (nếu có)
                is_excluded = False
                if rule.exclude_keys:
                    for ex_key in rule.exclude_keys:
                        # Dùng simple check cho exclude key để nhanh
                        if ex_key in header_upper_check:
                            print(f"   **Cảnh báo**: Key '{rule.key}' bị loại vì có từ khóa loại trừ '{ex_key}'.")
                            is_excluded = True
                            break
               
                # Check "ĐÍNH KÈM" đơn giản
                dinh_kem_pos = header_upper_check.find("DINH KEM")
                # Tìm vị trí key trong chuỗi đã chuẩn hóa (ước lượng)
                key_pos = header_upper_check.find(rule.key) 
                # Lưu ý: Vì dùng fuzzy nên key_pos bằng .find() có thể ra -1 dù thực tế có match
                # Tuy nhiên, logic ĐÍNH KÈM thường là text rác, ta chấp nhận rủi ro nhỏ ở đây.

                if dinh_kem_pos != -1 and key_pos != -1 and dinh_kem_pos < key_pos:
                     is_excluded = True

                if not is_excluded:
                    return rule
        return None
    
    def _add_document(self, category: str, name: str, start: int, end: int, trigger: str) -> None:
        doc = Document(len(self.documents) + 1, category, name, start, end, trigger)
        self.documents.append(doc)

    def _close_current_document(self, current_doc: Optional[Dict], page_num: int) -> None:
        if current_doc and current_doc.get("start") is not None:
            doc = Document(
                stt=len(self.documents) + 1,
                category=current_doc["category"],
                name=current_doc["name"],
                start=current_doc["start"],
                end=page_num - 1,
                trigger=current_doc["trigger"]
            )
            self.documents.append(doc)

    # --- PHƯƠNG THỨC ĐÃ ĐƯỢC CẬP NHẬT LOGIC ---
    # def process_pages(self, pages: List[str]) -> List[Document]:
    #     total_pages = len(pages)
    #     current_doc = {"start": None}
       
    #     print(f"**Đang xử lý {total_pages} trang với chế độ FUZZY MATCHING (Ngưỡng: {Config.FUZZY_THRESHOLD}%)**")
       
    #     for i, page_text in enumerate(pages):
    #         page_num = i + 1
    #         page_text_clean = page_text.strip()

    #         print(f"\n**Trang {page_num}**: Đang quét...")
        
    #         if self._is_blank_page(page_text_clean):
    #             print(f"   **Kết quả**: Trang trắng")
    #             self._close_current_document(current_doc, page_num)
    #             self._add_document("Phân cách", "Trang trắng/Không xác định", page_num, page_num, "BLANK_PAGE")
    #             current_doc = {"start": None}
    #             continue
        
    #         matched_rule = self._find_matching_rule(page_text_clean)
        
    #         # --- LOGIC MỚI: KIỂM TRA NẾU TÀI LIỆU TÌM THẤY TRÙNG VỚI TÀI LIỆU HIỆN TẠI ---
    #         is_continuation = False
    #         if matched_rule and current_doc.get("start") is not None:
    #             # Nếu tên tài liệu của rule mới trùng với tên tài liệu đang mở -> coi là trang tiếp theo
    #             if matched_rule.name == current_doc.get("name"):
    #                 is_continuation = True

    #         # --- CẬP NHẬT LUỒNG XỬ LÝ CHÍNH ---
    #         if matched_rule and not is_continuation:
    #             # Trường hợp 1: Tìm thấy một TÀI LIỆU MỚI THỰC SỰ
    #             print(f"   **Kết quả**: BẮT ĐƯỢC TÀI LIỆU MỚI -> '{matched_rule.key}'")
    #             self._close_current_document(current_doc, page_num)
    #             current_doc = {
    #                 "category": matched_rule.category,
    #                 "name": matched_rule.name,
    #                 "start": page_num,
    #                 "trigger": matched_rule.key
    #             }
    #         else:
    #             # Trường hợp 2: Không tìm thấy rule, HOẶC là trang tiếp theo của tài liệu hiện tại
    #             if current_doc.get("start") is None:
    #                 # Nếu chưa có tài liệu nào đang mở -> trang không xác định
    #                 print("   **Kết quả**: Không xác định.")
    #                 self._add_document("Phân loại", "Tài liệu không xác định",
    #                                 page_num, page_num, "NOT_FOUND")
    #                 current_doc = {"start": None}
    #             else:
    #                 # Nếu đã có tài liệu đang mở -> gộp trang này vào
    #                 if is_continuation:
    #                     print(f"   **Kết quả**: Gộp (cùng loại tài liệu): {current_doc['name']}")
    #                 else:
    #                     print(f"   **Kết quả**: Gộp vào tài liệu trước: {current_doc['name']}")
    #     self._close_current_document(current_doc, total_pages + 1)
    #     return self.documents

    # --- PHƯƠNG THỨC ĐÃ ĐƯỢC CẬP NHẬT LOGIC ---
    def process_pages(self, pages: List[str]) -> List[Document]:
        total_pages = len(pages)
        current_doc = {"start": None}
       
        print(f"**Đang xử lý {total_pages} trang với chế độ FUZZY MATCHING (Ngưỡng: {Config.FUZZY_THRESHOLD}%)**")
       
        for i, page_text in enumerate(pages):
            page_num = i + 1
            page_text_clean = page_text.strip()

            print(f"\n**Trang {page_num}**: Đang quét...")
            # --- LOGIC XỬ LÝ TRANG TRẮNG ĐÃ CẬP NHẬT ---
            if self._is_blank_page(page_text_clean):
                # Nếu có tài liệu đang mở, chỉ cần bỏ qua và gộp trang trắng này vào.
                if current_doc.get("start") is not None:
                    print(f"   **Kết quả**: Trang trắng, gộp vào tài liệu trước: {current_doc['name']}")
                    continue # Chuyển sang trang tiếp theo
                # Nếu không, đây là trang trắng đơn lẻ, tạo mục riêng.
                else:
                    print(f"   **Kết quả**: Trang trắng (đơn lẻ)")
                    self._add_document("Phân cách", "Trang trắng/Không xác định", page_num, page_num, "BLANK_PAGE")
                    current_doc = {"start": None}
                    continue
            
            # --- LOGIC CŨ GIỮ NGUYÊN ---
            matched_rule = self._find_matching_rule(page_text_clean, page_num)
           
            is_continuation = False
            if matched_rule and current_doc.get("start") is not None:
                if matched_rule.name == current_doc.get("name"):
                    is_continuation = True

            if matched_rule:# and not is_continuation:
                print(f"   **Kết quả**: BẮT ĐƯỢC TÀI LIỆU MỚI -> '{matched_rule.key}'")
                self._close_current_document(current_doc, page_num)
                current_doc = {
                    "category": matched_rule.category,
                    "name": matched_rule.name,
                    "start": page_num,
                    "trigger": matched_rule.key
                }
            else:
                if current_doc.get("start") is None:
                    print("   **Kết quả**: Không xác định.")
                    self._add_document("Phân loại", "Tài liệu không xác định",
                                     page_num, page_num, "NOT_FOUND")
                    current_doc = {"start": None}
                else:
                    if is_continuation:
                        print(f"   **Kết quả**: Gộp (cùng loại tài liệu): {current_doc['name']}")
                    else:
                        print(f"   **Kết quả**: Gộp vào tài liệu trước: {current_doc['name']}")

        self._close_current_document(current_doc, total_pages + 1)
        return self.documents

# ==============================================================================
# **LỚP XỬ LÝ FILE**
# ==============================================================================

class FileProcessor:
    BASE_DIR = "data_parser" # Thư mục chứa file JSON

    @staticmethod
    def load_json_file(file_name: str) -> Optional[Dict]:
        file_path = os.path.join(FileProcessor.BASE_DIR, file_name)
        if not os.path.exists(file_path):
            # Fallback thử tìm ở thư mục hiện tại
            file_path = file_name 
            if not os.path.exists(file_path):
                print(f"**Lỗi**: File {file_path} không tồn tại!")
                return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f, strict=False)
        except Exception as e:
            print(f"**Lỗi đọc file**: {e}")
            return None
   
    @staticmethod
    def extract_pages(data: Dict) -> List[str]:
        content = data.get('extracted_content', '')
        return re.split(Config.PAGE_BREAK_DELIMITER, content)
   
    @staticmethod
    def display_results(documents: List[Document]) -> None:
        print("\n" + "=" * 110)
        print(f"{'STT | TÊN TÀI LIỆU':<50} | {'TRANG':<10} | {'KEY NHẬN DIỆN'}")
        print("-" * 110)
        for doc in documents:
            page_range = f"{doc.start}-{doc.end}" if doc.start != doc.end else str(doc.start)
            print(f"{str(doc.stt) + ' | ' + doc.name:<50} | {page_range:<10} | {doc.trigger}")
    
    @staticmethod
    def split_documents(documents: List[Document], save_dir: str, original_file_path: str) -> None:
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        try:
            source_doc = fitz.open(original_file_path)
        except:
            print("Không mở được PDF gốc.")
            return
        for doc in documents:
            new_doc = fitz.open()
            if doc.end < source_doc.page_count:
                new_doc.insert_pdf(source_doc, from_page=doc.start-1, to_page=doc.end-1)
            
            if len(new_doc) > 0:
                clean_name = sanitize_filename(doc.name)
                output_filename = f"{save_dir}/{doc.stt}_{clean_name}.pdf"
                new_doc.save(output_filename)
            else:
                print(doc.stt)
            new_doc.close()
    
    @staticmethod
    def evaluate(documents: List[Document], ground_truth_excel_path: str, output_excel_path: str = "evaluation_results.xlsx") -> None:
        """
        **Hàm đánh giá kết quả split documents so với ground truth**
        
        **Tham số đầu vào:**
           documents: Danh sách các Document đã được split
           ground_truth_excel_path: Đường dẫn file Excel chứa ground truth
           output_excel_path: Đường dẫn file Excel để lưu kết quả đánh giá
        
        **Kết quả:**
           Tạo file Excel với các cột: filename, range, status
        """
        try:
            # **Đọc file ground truth**
            ground_truth_df = pd.read_excel(ground_truth_excel_path)
            
            # **Kiểm tra các cột bắt buộc**
            required_columns = ['Filename', 'Start', 'End']
            missing_columns = [col for col in required_columns if col not in ground_truth_df.columns]
            if missing_columns:
                print(f"**Lỗi**: File ground truth thiếu các cột: {missing_columns}")
                return
            
            # **Tạo dictionary từ ground truth để tra cứu nhanh**
            ground_truth_dict = {}
            for _, row in ground_truth_df.iterrows():
                filename = str(row['Filename']).strip()
                start = int(row['Start'])
                end = int(row['End'])
                ground_truth_dict[filename] = (start, end)
            
            # **Tạo dictionary từ documents để tra cứu**
            documents_dict = {}
            for doc in documents:
                clean_name = sanitize_filename(doc.name)
                filename = f"{doc.stt}_{clean_name}.pdf"
                documents_dict[filename] = (doc.start, doc.end)
            
            # **Đánh giá kết quả**
            evaluation_results = []
            
            # **Kiểm tra các file trong ground truth**
            for gt_filename, (gt_start, gt_end) in ground_truth_dict.items():
                gt_range = f"{gt_start}-{gt_end}" if gt_start != gt_end else str(gt_start)
                
                # **Tìm file tương ứng trong documents**
                found_match = False
                for doc_filename, (doc_start, doc_end) in documents_dict.items():
                    if doc_start == gt_start and doc_end == gt_end:
                        status = "PASS"
                        found_match = True
                        evaluation_results.append({
                            'filename': gt_filename,
                            'range': gt_range,
                            'status': status,
                            'ground_truth_range': gt_range,
                            'detected_range': f"{doc_start}-{doc_end}" if doc_start != doc_end else str(doc_start),
                            'matched_document': doc_filename
                        })
                        break
                
                if not found_match:
                    evaluation_results.append({
                        'filename': gt_filename,
                        'range': gt_range,
                        'status': "FAIL",
                        'ground_truth_range': gt_range,
                        'detected_range': "Not Found",
                        'matched_document': "None"
                    })
            
            # **Kiểm tra các file được detect nhưng không có trong ground truth**
            for doc_filename, (doc_start, doc_end) in documents_dict.items():
                doc_range = f"{doc_start}-{doc_end}" if doc_start != doc_end else str(doc_start)
                
                # **Kiểm tra xem có match với ground truth không**
                found_in_gt = False
                for gt_filename, (gt_start, gt_end) in ground_truth_dict.items():
                    if doc_start == gt_start and doc_end == gt_end:
                        found_in_gt = True
                        break
                
                if not found_in_gt:
                    evaluation_results.append({
                        'filename': f"EXTRA_{doc_filename}",
                        'range': doc_range,
                        'status': "FAIL",
                        'ground_truth_range': "Not in GT",
                        'detected_range': doc_range,
                        'matched_document': doc_filename
                    })
            
            # **Tạo DataFrame và lưu kết quả**
            results_df = pd.DataFrame(evaluation_results)
            
            # **Tạo summary statistics**
            total_gt = len(ground_truth_dict)
            total_detected = len(documents_dict)
            passed = len([r for r in evaluation_results if r['status'] == 'PASS'])
            failed = total_gt - passed
            
            # **Lưu kết quả ra Excel với nhiều sheet**
            with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
                # **Sheet chính với kết quả đánh giá**
                results_df.to_excel(writer, sheet_name='Evaluation_Results', index=False)
                
                # **Sheet summary**
                summary_data = {
                    'Metric': ['Total Ground Truth', 'Total Detected', 'Passed', 'Failed', 'Precision', 'Recall', 'F1-Score'],
                    'Value': [
                        total_gt,
                        total_detected,
                        passed,
                        failed,
                        f"{(passed/total_detected*100):.2f}%" if total_detected > 0 else "0%",
                        f"{(passed/total_gt*100):.2f}%" if total_gt > 0 else "0%",
                        f"{(2*passed/(total_gt+total_detected)*100):.2f}%" if (total_gt+total_detected) > 0 else "0%"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # **In kết quả ra console**
            print(f"\n**Kết quả đánh giá:**")
            print(f"   Tổng số file ground truth: {total_gt}")
            print(f"   Tổng số file được detect: {total_detected}")
            print(f"   Số file PASS: {passed}")
            print(f"   Số file FAIL: {failed}")
            print(f"   Precision: {(passed/total_detected*100):.2f}%" if total_detected > 0 else "   Precision: 0%")
            print(f"   Recall: {(passed/total_gt*100):.2f}%" if total_gt > 0 else "   Recall: 0%")
            print(f"\n**Kết quả đã được lưu vào**: {output_excel_path}")
            
        except Exception as e:
            print(f"**Lỗi trong quá trình đánh giá**: {e}")

# ==============================================================================
# **HÀM CHÍNH**
# ==============================================================================
def process_documents_strict_case(json_path: str, original_path: str, save_dir: str) -> List[Document]:
    data = FileProcessor.load_json_file(json_path)
    if not data: return []
    pages = FileProcessor.extract_pages(data)
    processor = DocumentProcessor()
    documents = processor.process_pages(pages)
    FileProcessor.display_results(documents)
    # Gọi hàm evaluate
    FileProcessor.evaluate(
        documents=documents, 
        ground_truth_excel_path="hsgn_result.xlsx",
        output_excel_path="evaluation_results_2.xlsx"
    )

    FileProcessor.split_documents(documents, save_dir, original_path)
    return documents

# ==============================================================================
# **CHẠY CHƯƠNG TRÌNH**
# ==============================================================================

if __name__ == "__main__":
    # **Thay thế "1.json" bằng đường dẫn file của bạn**
    result = process_documents_strict_case("ho_so_giai_ngan.json", "hsgn.pdf", "results")