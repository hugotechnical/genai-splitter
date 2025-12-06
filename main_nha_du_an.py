import json
import re
import os
import unicodedata
from typing import List, Dict, Optional, Any
import fitz

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
    LINES_THRESHOLD = 25        # Số dòng đầu trang để quét tiêu đề
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
            # --- HỒ SƠ TÍN DỤNG ---
            ("HOP DONG CHO VAY", "Hồ sơ tín dụng", "Hợp đồng cho vay"),
            ("PHU LUC HOP DONG CHO VAY", "Hồ sơ tín dụng", "Phụ lục HĐCV"),
            ("KHE UOC NHAN NO", "Hồ sơ tín dụng", "Khế ước nhận nợ"),
            ("DE NGHI GIAI NGAN", "Hồ sơ tín dụng", "Đề nghị giải ngân"), # Sẽ bắt được "GIALNGAN"
            ("DE NGHI GIALNGAN", "Hồ sơ tín dụng", "Đề nghị giải ngân"), # Sẽ bắt được "GIALNGAN"
            ("VAN BAN XAC NHAN", "Hồ sơ tín dụng", "Văn bản xác nhận dữ liệu"),
            ("VAN BAN TU CHOI BAO LANH", "Hồ sơ tín dụng", "Văn bản từ chối bảo lãnh"), # Mới
            ("THOA THUAN TRA THAY", "Hồ sơ tín dụng", "Thỏa thuận trả thay lãi vay", ["BA BEN"]),

            # --- HỒ SƠ PHÊ DUYỆT & KIỂM SOÁT ---
            ("DANH MUC", "Hồ sơ phê duyệt", "Danh mục hồ sơ chi tiết"),
            ("NGHI QUYET PHE DUYET", "Hồ sơ phê duyệt", "Nghị quyết phê duyệt"),
            ("THONG BAO CAP TIN DUNG", "Hồ sơ phê duyệt", "Thông báo cấp tín dụng"),
           
            # --- HỒ SƠ PHÁP LÝ ---
            ("CAN CUOC", "Hồ sơ pháp lý", "Căn cước công dân"),
            ("TRICH LUC KET HON", "Hồ sơ pháp lý", "ĐKKH/ Trích lục kết hôn"),
            ("XAC NHAN TINH TRANG HON NHAN", "Hồ sơ pháp lý", "Giấy XN tình trạng hôn nhân"),
            ("XAC NHAN CU TRU", "Hồ sơ pháp lý", "Giấy xác nhận thông tin cư trú"),
            ("THONG TIN CU TRU", "Hồ sơ pháp lý", "VNEID"),
            ("CAM KET SU DUNG CCCD", "Hồ sơ pháp lý", "Cam kết CMT nhân dân"),
            ("GIAY KHAI SINH", "Hồ sơ pháp lý", "Giấy khai sinh"),
            ("XAC NHAN NHAN KHAU", "Hồ sơ pháp lý", "Giấy xác nhận nhân khẩu"),
           
            # --- HỒ SƠ LỊCH SỬ ---
            ("BAO CAO", "Hồ sơ lịch sử TDTD", "CIC", ["TAI CHINH"]),
            ("XAC NHAN TAT TOAN", "Hồ sơ lịch sử TDTD", "Xác nhận tất toán"),
            ("XAC NHAN DU NO", "Hồ sơ lịch sử TDTD", "Xác nhận dư nợ"),
           
            # --- HỒ SƠ VAY VỐN ---
            ("DE NGHI VAY VON", "Hồ sơ đề nghị vay vốn", "Giấy đề nghị vay vốn"),
           
            # --- HỒ SƠ MỤC ĐÍCH ---
            ("HOP DONG MUA BAN", "Hồ sơ mục đích", "Hợp đồng mua bán"),
            ("HOP DONG CHUYEN NHUONG", "Hồ sơ mục đích", "Hợp đồng chuyển nhượng"),
            ("HOP DONG DAT COC", "Hồ sơ mục đích", "Hợp đồng đặt cọc"),
            ("GIAY BIEN NHAN TIEN", "Hồ sơ mục đích", "Giấy biên nhận tiền"),
            ("XAC NHAN GIAO DICH", "Hồ sơ mục đích", "Xác nhận giao dịch"),
            ("XAC NHAN THANH TOAN", "Hồ sơ mục đích", "Giấy xác nhận thanh toán"),
            ("DON DE NGHI", "Hồ sơ mục đích", "Đơn đề nghị"),
            ("HOP DONG VAY", "Hồ sơ mục đích", "Bộ Hợp đồng vay"),
            ("THONG BAO THANH TOAN", "Hồ sơ mục đích", "Thông báo thanh toán"),
            ("DE NGHI CHUYEN TIEN", "Hồ sơ mục đích", "Đề nghị chuyển tiền"),
            ("THONG BAO BAN GIAO CAN HO", "Hồ sơ mục đích", "Thông báo bàn giao căn hộ"),
            ("BIEN BAN BAN GIAO CAN HO", "Hồ sơ mục đích", "Biên bản bàn giao căn hộ"),

            # --- HỒ SƠ NGUỒN THU ---
            # ("BANG KE THU NHAP", "Hồ sơ nguồn thu", "Bảng kê thu nhập"),
            ("NGUON THU NHAP", "Hồ sơ nguồn thu", "Bảng kê thu nhập"),
            ("XAC NHAN HOAT DONG HKD", "Hồ sơ nguồn thu", "Xác nhận hoạt động hộ kinh doanh"),
            ("DANG KY KINH DOANH", "Hồ sơ nguồn thu", "Đăng ký kinh doanh"),
            ("GIAY NOP TIEN", "Hồ sơ nguồn thu", "Giấy nộp tiền vào ngân sách NN"),
            ("HOP DONG LAO DONG", "Hồ sơ nguồn thu", "Hợp đồng lao động"),
            ("QUYET DINH BO NHIEM", "Hồ sơ nguồn thu", "Quyết định bổ nhiệm"),
            ("XAC NHAN LUONG", "Hồ sơ nguồn thu", "Xác nhận lương"),
            ("SAO KE", "Hồ sơ nguồn thu", "Sao kê lương"),
            ("SO PHU", "Hồ sơ nguồn thu", "Sổ phụ"),
            ("HOP DONG CHO THUE", "Hồ sơ nguồn thu", "Hợp đồng thuê tài sản"),
            ("BAO CAO TAI CHINH", "Hồ sơ nguồn thu", "Báo cáo tài chính"),
            ("BANG KE TAI SAN", "Hồ sơ nguồn thu", "Bảng kê tài sản tích lũy"),

            # --- HỒ SƠ TSBD ---
            ("HOP DONG THE CHAP", "Hồ sơ TSBD", "Hợp đồng thế chấp"),
            ("PHIEU YEU CAU DANG KY", "Hồ sơ TSBD", "Đơn đăng ký GDBĐ"),
            ("BIEN BAN DINH GIA TAI SAN", "Hồ sơ TSBD", "Biên bản định giá / Kết quả GDBĐ"),
            # ("BIEN NHAN TAI SAN", "Hồ sơ TSBD", "Biên nhận tài sản"),
            ("GIAY BIEN NHAN HO SƠ TAI SAN ", "Hồ sơ TSBD", "Biên nhận tài sản"),
            ("PHIEU NHAP KHO", "Hồ sơ TSBD", "Phiếu nhập kho"),
            ("THOA THUAN BA BEN", "Hồ sơ TSBD", "Văn bản thỏa thuận 3 bên"),

            ("VAN BAN THOA THUAN", "Hồ sơ TSBD", "Văn bản thỏa thuận"),
            ("THOA THUAN DAT COC", "Hồ sơ TSBD", "Thỏa thuận đặt cọc"),

            # --- HỒ SƠ BẢO HIỂM ---
            ("GIAY CHUNG NHAN", "Hồ sơ bảo hiểm", "Giấy chứng nhận bảo hiểm", ["BAO HIEM"]),
            ("GIAY CHUNG NHAN BAO HIEM", "Hồ sơ bảo hiểm", "Hợp đồng bảo hiểm"),
            ("CHUYEN QUYEN THU HUONG", "Hồ sơ bảo hiểm", "Chuyển quyền thụ hưởng bảo hiểm"),
            ("HOA DON GIA TRI GIA TANG", "Hồ sơ bảo hiểm", "Hóa đơn bảo hiểm", ["BAO HIEM"]),
            ("PHIEU THU", "Hồ sơ bảo hiểm", "Phiếu thu", ["NOP PHI BAO HIEM"]),
            ("DE NGHI TAI TUC", "Hồ sơ bảo hiểm", "Đề nghị tái tục Hợp đồng bảo hiểm"),
            ("GIAY YEU CAU BAO HIEM", "Hồ sơ bảo hiểm", "Giấy yêu cầu bảo hiểm"),
            
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
    def check_keyword_position(original_text: str, keyword: str) -> bool:
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
            
            if re.search(pattern_before, original_line, re.IGNORECASE) or \
               re.search(pattern_after, original_line, re.IGNORECASE):
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

            # KIỂM TRA ĐIỀU KIỆN IN HOA và độ dài tối thiểu
            if search_text and search_text == search_text.upper():
                if len(search_text) < len(keyword_norm) * 0.6:
                    continue

                # Tính điểm tương đồng bằng WRatio
                score = fuzz.WRatio(keyword_norm, search_text)

                if score >= Config.FUZZY_THRESHOLD: 
                    # Note: Dùng Config.FUZZY_THRESHOLD thay cho 88 để đồng bộ cấu hình
                    print(f"   **Debug**: Tìm thấy '{keyword}' (Text: '{search_text}') - Score (WRatio): {score}%")
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
   
    def _find_matching_rule(self, original_text: str) -> Optional[DocumentRule]:
        header_strict = TextProcessor.extract_header(original_text)
        header_upper_check = header_strict.upper()

        for rule in self.rules:
            # 1. Logic loại trừ (Exclude)
            # Fuzzy check cho exclude keys luôn nếu cần, nhưng exact match thường đủ cho loại trừ
            if "DINH KEM" in header_upper_check:
                pass # Logic đính kèm phức tạp, giữ nguyên hoặc tùy chỉnh

            # 2. Kiểm tra KEYWORD bằng FUZZY LOGIC
            if TextProcessor.check_keyword_position(original_text, rule.key):
               
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
            matched_rule = self._find_matching_rule(page_text_clean)
           
            is_continuation = False
            if matched_rule and current_doc.get("start") is not None:
                if matched_rule.name == current_doc.get("name"):
                    is_continuation = True

            if matched_rule and not is_continuation:
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
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Đường dẫn file gốc
        # Cố gắng tìm file pdf ở cùng thư mục script hoặc data/
        base_dirs = [
            "data", 
            os.path.dirname(__file__), 
            os.path.join(os.path.dirname(__file__), "data")
        ]
        
        full_pdf_path = None
        for b_dir in base_dirs:
            temp_path = os.path.join(b_dir, original_file_path)
            if os.path.exists(temp_path):
                full_pdf_path = temp_path
                break
        
        if not full_pdf_path and os.path.exists(original_file_path):
            full_pdf_path = original_file_path

        if not full_pdf_path:
            print(f"Không tìm thấy file PDF gốc: {original_file_path}")
            return

        try:
            source_doc = fitz.open(full_pdf_path)
        except Exception as e:
            print(f"Không mở được PDF gốc: {e}")
            return

        for doc in documents:
            new_doc = fitz.open()
            # PDF pages are 0-indexed
            start_page = doc.start - 1
            end_page = doc.end - 1
            
            if start_page < len(source_doc):
                # Clamp end_page
                end_page = min(end_page, len(source_doc) - 1)
                new_doc.insert_pdf(source_doc, from_page=start_page, to_page=end_page)

                if len(new_doc) > 0:
                    clean_name = sanitize_filename(doc.name)
                    output_filename = f"./data_output/{save_dir}/{doc.stt}-{doc.start}-{doc.end}_{clean_name}.pdf"
                    new_doc.save(output_filename)
            new_doc.close()

# ==============================================================================
# **MAIN**
# ==============================================================================

def process_documents_fuzzy(json_path: str, original_path: str, save_dir: str) -> List[Document]:
    data = FileProcessor.load_json_file(json_path)
    if not data: return []
    pages = FileProcessor.extract_pages(data)
    processor = DocumentProcessor()
    documents = processor.process_pages(pages)
    FileProcessor.display_results(documents)
    FileProcessor.split_documents(documents, save_dir, original_path)
    return documents

if __name__ == "__main__":
    # Thay đổi tên file phù hợp
    result = process_documents_fuzzy("nha-du-an.json", "./data_input/nha-du-an-2.pdf", "results_nha_du_an")