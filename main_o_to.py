import json
import re
import os
import unicodedata
from typing import List, Dict, Optional, Any

import fitz

# ==============================================================================
# **CẤU HÌNH TOÀN CỤC**
# ==============================================================================

class Config:
    """**Cấu hình các thông số xử lý tài liệu**"""
    LINES_THRESHOLD = 15        # Số dòng đầu trang để quét tiêu đề
    MIN_CONTENT_LENGTH = 15     # Độ dài tối thiểu để coi là trang có nội dung
    PAGE_BREAK_DELIMITER = '--- Page Break ---'
    MAX_KEYWORD_POSITION = 4    # Từ khóa phải xuất hiện trong N từ đầu tiên của dòng

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
    filename = remove_accents(filename) # Tận dụng hàm remove_accents
    # Thay thế ký tự không phải chữ/số bằng gạch dưới
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
    """**Lớp đại diện cho quy tắc nhận diện tài liệu**"""
    def __init__(self, key: str, category: str, name: str, exclude_keys: Optional[List[str]] = None):
        self.key = key              # KEYWORD LÀ CHỮ IN HOA (VD: HOP DONG)
        self.category = category
        self.name = name
        self.exclude_keys = exclude_keys or []

class Document:
    """**Lớp đại diện cho một tài liệu được phân loại**"""
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
    """**Quản lý danh sách các quy tắc nhận diện tài liệu**"""
    
    @staticmethod
    def get_rules() -> List[DocumentRule]:
        # Lưu ý: Các Key ở đây ĐỀU PHẢI VIẾT IN HOA để khớp với logic ưu tiên
        rules_data = [
            # NHÓM 1: HỒ SƠ TÀI SẢN BẢO ĐẢM
            ("GIAY HEN", "Hồ sơ TSBD", "Giấy hẹn/Đăng ký xe"),
            ("GIAY CHUNG NHAN", "Hồ sơ TSBD", "GCN QSD Đất/Nhà", ["DANG KY"]),
            ("HOP DONG THE CHAP", "Hồ sơ TSBD", "Hợp đồng thế chấp"),
            ("PHIEU YEU CAU DANG KY", "Hồ sơ TSBD", "Đơn đăng ký giao dịch bảo đảm"),
            ("BIEN NHAN TAI SAN", "Hồ sơ TSBD", "Biên nhận tài sản bảo đảm"),
            ("BIEN BAN DINH GIA TAI SAN", "Hồ sơ TSBD", "Biên bản định giá tài sản"),
            ("PHIEU NHAP KHO", "Hồ sơ TSBD", "Phiếu nhập kho"),
            ("BIEN BAN KIEM TRA HIEN TRANG", "Hồ sơ TSBD", "Biên bản kiểm tra hiện trạng xe"),

            # NHÓM 2: HỒ SƠ TÍN DỤNG
            ("HOP DONG CHO VAY", "Hồ sơ tín dụng", "Hợp đồng cho vay"),
            ("PHU LUC HOP DONG CHO VAY", "Hồ sơ tín dụng", "Phụ lục HĐCV"),
            ("KHE UOC NHAN NO", "Hồ sơ tín dụng", "Khế ước nhận nợ"),
            ("GIAY DE NGHI GIAI NGAN", "Hồ sơ tín dụng", "Đề nghị giải ngân"),
            ("VAN BAN XAC NHAN", "Hồ sơ tín dụng", "Văn bản xác nhận dữ liệu"),
            ("XAC NHAN CONG NO", "Hồ sơ tín dụng", "Xác nhận công nợ"),
            ("HOP DONG MUA BAN XE", "Hồ sơ tín dụng", "HĐMB Xe & Phụ lục"),
            ("HOA DON", "Hồ sơ tín dụng", "Hóa đơn VAT/Pin"),
            ("HOP DONG BAO HIEM", "Hồ sơ tín dụng", "Hợp đồng bảo hiểm xe cơ giới"),

            # NHÓM 3: HỒ SƠ PHÁP LÝ
            ("DE NGHI VAY VON", "Hồ sơ pháp lý", "Đơn đề nghị vay vốn"),
            ("NGHI QUYET PHE DUYET", "Hồ sơ pháp lý", "Nghị quyết phê duyệt"),
            ("CAN CUOC CONG DAN", "Hồ sơ pháp lý", "Căn cước công dân"),
            ("XAC NHAN TINH TRANG HON NHAN", "Hồ sơ pháp lý", "Xác nhận TTHN"),
            ("QUAN LY TAI SAN DAM BAO", "Hồ sơ pháp lý", "Thỏa thuận quản lý TSĐB"),
            ("BIEN BAN BAN GIAO", "Hồ sơ pháp lý", "Biên bản bàn giao căn hộ"),
            ("BANG KE", "Hồ sơ pháp lý", "Hồ sơ nguồn thu/TSTL"),

            ("VAY MUA O TO", "Hồ sơ pháp lý", "Vay mua ô tô"),
            ("XAC NHAN CHUYEN QUYEN", "Hồ sơ pháp lý", "Xác nhận chuyển quyền"),
            ("UY QUYEN", "Hồ sơ pháp lý", "Ủy Quyền"),
            ("PHIEU THU", "Hồ sơ pháp lý", "Phiếu Thu"),
            ("THU XAC NHAN TRAO TANG", "Hồ sơ pháp lý", "Thư xác nhận trao tặng"),
            ("DE NGHI TAI TUC", "Hồ sơ pháp lý", "Đề Nghị Tái Tục"),
            ("VAN BAN CHUNG NHAN", "Hồ sơ pháp lý", "Văn bản chứng nhận"),
            ("DANG KY THE CHAP", "Hồ sơ pháp lý", "Đăng Ký Thế Chấp"),
            ("HOP DONG SUA DOL", "Hồ sơ pháp lý", "Hợp Đồng Sửa Đổi"),
            ("BIEN NHAN", "Hồ sơ pháp lý", "GIẤY BIẾN NHẬN"),
            ("PHIEU NHAP KHO TAI SAN BAO DAM", "Hồ sơ pháp lý", "PHIẾU NHẬP KHO TÀI SẢN BẢO ĐẢM"),
            ("CAM KET BAN GIAO GIAY TO XE", "Hồ sơ pháp lý", "CAM KẾT BÀN GIAO GIẤY TỜ XE"),
            ("THONG BAO", "Hồ sơ pháp lý", "Thông Báo"),
            ("DE NGHI VA XAC NHAN CUA DON VI KINH DOANH", "Hồ sơ pháp lý", "ĐỀ NGHỊ VÀ XÁC NHẬN CỦA ĐƠN VỊ KINH DOANH")
        ]
        
        rules = []
        for item in rules_data:
            key, category, name, *rest = item
            exclude_keys = rest[0] if rest else None
            rules.append(DocumentRule(key, category, name, exclude_keys))
        return rules

# ==============================================================================
# **LỚP XỬ LÝ CHUỖI VÀ HEADER (CẬP NHẬT LOGIC CASE-SENSITIVE)**
# ==============================================================================

class TextProcessor:
    """**Lớp xử lý và chuẩn hóa văn bản**"""
    
    @staticmethod
    def remove_accents(text: str) -> str:
        """
        Loại bỏ dấu tiếng Việt nhưng GIỮ NGUYÊN VIẾT HOA/THƯỜNG.
        Đây là mấu chốt để ưu tiên từ viết in.
        """
        if not text: return ""
        normalized = unicodedata.normalize('NFD', text)
        no_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        # Thay thế đ/Đ thủ công vì NFD không tách được hết
        return no_accents.replace('đ', 'd').replace('Đ', 'D')
    
    @staticmethod
    def normalize_text_strict(text: str) -> str:
        """
        Chuẩn hóa văn bản để so sánh chính xác:
        - Bỏ dấu.
        - Giữ nguyên Case (không upper).
        - Chỉ giữ lại ký tự chữ và số, thay thế ký tự lạ bằng khoảng trắng.
        """
        no_accents = TextProcessor.remove_accents(text)
        # Giữ lại a-z, A-Z, 0-9. Các ký tự khác thành space
        clean_text = re.sub(r'[^a-zA-Z0-9]', ' ', no_accents)
        return re.sub(r'\s+', ' ', clean_text).strip()

    @staticmethod
    def extract_header(text: str, lines_limit: int = Config.LINES_THRESHOLD) -> str:
        """Lấy header nhưng dùng chuẩn hóa strict (có dấu, có case) để debug dễ hơn"""
        if not text: return ""
        # Lấy N dòng đầu
        header_lines = text.split('\n')[:lines_limit]
        # Nối lại và chuẩn hóa sơ bộ để log
        return TextProcessor.normalize_text_strict('\n'.join(header_lines))
    
    @staticmethod
    def check_keyword_position(text: str, keyword: str) -> bool:
        """
        Kiểm tra từ khóa với độ ưu tiên Case-Sensitive (In hoa).
        Vì keyword input (VD: 'HOP DONG') là IN HOA, nên hàm này sẽ
        chỉ trả về True nếu trong text gốc cũng là IN HOA.
        """
        if not text or not keyword: return False
        
        lines = text.split('\n')[:Config.LINES_THRESHOLD]
        for line in lines:
            if not line.strip(): continue
            
            # Bước 1: Chuẩn hóa dòng (Bỏ dấu, GIỮ NGUYÊN CASE)
            normalized_line = TextProcessor.normalize_text_strict(line)
            
            # Bước 2: Kiểm tra chứa chuỗi (Case-sensitive)
            # VD: keyword="HOP DONG"
            # normalized_line="Hop Dong Mua Ban" -> False (Không khớp)
            # normalized_line="HOP DONG MUA BAN" -> True (Khớp)
            if keyword in normalized_line:
                words = normalized_line.split()
                keyword_words = keyword.split()
                
                # Bước 3: Kiểm tra vị trí từ khóa (phải nằm ở đầu câu)
                # Logic này giúp tránh bắt nhầm chữ nằm giữa câu
                for i in range(len(words) - len(keyword_words) + 1):
                    if words[i:i+len(keyword_words)] == keyword_words:
                        keyword_start_pos = i + 1
                        if keyword_start_pos <= Config.MAX_KEYWORD_POSITION:
                            print(f"   **Debug**: Tìm thấy KEY IN HOA '{keyword}' tại vị trí {keyword_start_pos}. Hợp lệ.")
                            return True
                        else:
                            print(f"   **Debug**: Tìm thấy KEY IN HOA '{keyword}' nhưng ở vị trí {keyword_start_pos} (quá xa). Bỏ qua.")
        return False

# ==============================================================================
# **LỚP XỬ LÝ TÀI LIỆU**
# ==============================================================================

class DocumentProcessor:
    """**Lớp chính xử lý phân loại tài liệu**"""
    
    def __init__(self):
        self.rules = DocumentRules.get_rules()
        self.documents: List[Document] = []
    
    def _is_blank_page(self, text: str) -> bool:
        """Kiểm tra trang trắng dựa trên độ dài nội dung thực tế"""
        clean_text = re.sub(r'\s+', '', text)
        return len(clean_text) < Config.MIN_CONTENT_LENGTH
    
    def _find_matching_rule(self, original_text: str) -> Optional[DocumentRule]:
        """
        Tìm quy tắc khớp.
        Logic mới: Duyệt qua Rules và kiểm tra trực tiếp trên Text gốc (đã xử lý dấu)
        """
        # Chuẩn bị header dạng "Sạch nhưng có Case" để kiểm tra điều kiện loại trừ
        header_strict = TextProcessor.extract_header(original_text)
        
        # Tạo bản Upper để check điều kiện loại trừ (cho dễ bắt lỗi OCR)
        header_upper_check = header_strict.upper() 

        for rule in self.rules:
            # 1. Kiểm tra logic loại trừ trước (Dùng bản Upper để an toàn cho việc loại trừ)
            # Nếu có "ĐÍNH KÈM" -> Bỏ qua ngay
            if "DINH KEM" in header_upper_check:
                # Kiểm tra vị trí: Nếu ĐÍNH KÈM xuất hiện trước KEYWORD thì mới loại
                # Nhưng ở đây chưa tìm thấy keyword, nên ta check tổng quát
                # Nếu dòng tiêu đề bắt đầu bằng ĐÍNH KÈM -> Rất rủi ro -> Skip nếu cần
                # Ở logic cũ: check vị trí tương đối. 
                pass 

            # 2. Kiểm tra KEYWORD chính xác (Case-Sensitive)
            # Gọi hàm check_keyword_position, hàm này sẽ tự lo việc so khớp IN HOA
            if TextProcessor.check_keyword_position(original_text, rule.key):
                
                # 3. Kiểm tra điều kiện loại trừ cụ thể của Rule (Exclude Keys)
                # VD: Rule GIAY CHUNG NHAN kỵ DANG KY
                is_excluded = False
                if rule.exclude_keys:
                    for ex_key in rule.exclude_keys:
                        # Check exclude key cũng nên linh hoạt, thường exclude key cũng là in hoa
                        if ex_key in header_upper_check: 
                            print(f"   **Cảnh báo**: Key '{rule.key}' bị loại vì tìm thấy từ khóa loại trừ '{ex_key}'.")
                            is_excluded = True
                            break
                
                # Check từ "ĐÍNH KÈM" cụ thể cho rule này
                # Nếu tìm thấy "DINH KEM" đứng trước "KEYWORD" trong cùng 1 dòng hoặc context gần
                dinh_kem_pos = header_upper_check.find("DINH KEM")
                key_pos = header_upper_check.find(rule.key) # rule.key is UPPER
                
                if dinh_kem_pos != -1 and key_pos != -1 and dinh_kem_pos < key_pos:
                     print(f"   **Cảnh báo**: Key '{rule.key}' bị loại do có 'Đính kèm' đứng trước.")
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

    def process_pages(self, pages: List[str]) -> List[Document]:
        total_pages = len(pages)
        current_doc = {"start": None}
        
        print(f"**Đang xử lý {total_pages} trang với chế độ ƯU TIÊN TỪ KHÓA VIẾT IN**")
        
        for i, page_text in enumerate(pages):
            page_num = i + 1
            page_text_clean = page_text.strip()
            
            print(f"\n**Trang {page_num}**: Đang quét...")
            
            # Check trang trắng
            if self._is_blank_page(page_text_clean):
                print(f"   **Kết quả**: Trang trắng")
                self._close_current_document(current_doc, page_num)
                self._add_document("Phân cách", "Trang trắng/Không xác định", page_num, page_num, "BLANK_PAGE")
                current_doc = {"start": None}
                continue
            
            # Tìm Rule khớp
            matched_rule = self._find_matching_rule(page_text_clean)
            
            if matched_rule:
                print(f"   **Kết quả**: BẮT ĐƯỢC TÀI LIỆU MỚI -> '{matched_rule.key}'")
                self._close_current_document(current_doc, page_num)
                current_doc = {
                    "category": matched_rule.category,
                    "name": matched_rule.name,
                    "start": page_num,
                    "trigger": matched_rule.key
                }
            else:
                # Logic cũ: Nếu đang có doc dở dang -> coi như trang con
                # Nếu không -> coi như trang không xác định (hoặc trang con của doc trước đó chưa closed?)
                # Ở đây giữ logic: Nếu không tìm thấy key mới, nó thuộc về doc cũ.
                # TRỪ KHI: Doc cũ đã bị ngắt bởi trang trắng, thì trang này là NOT_FOUND
                if current_doc.get("start") is None:
                    print("   **Kết quả**: Không tìm thấy Key in hoa. Đánh dấu Không xác định.")
                    self._add_document("Phân loại", "Tài liệu không xác định",
                                     page_num, page_num, "NOT_FOUND")
                    current_doc = {"start": None}
                else:
                     print(f"   **Kết quả**: Không có Key mới (hoặc chỉ có chữ thường). Gộp vào tài liệu trước: {current_doc['name']}")
        
        self._close_current_document(current_doc, total_pages + 1)
        
        return self.documents

# ==============================================================================
# **LỚP XỬ LÝ FILE VÀ HIỂN THỊ KẾT QUẢ**
# ==============================================================================

class FileProcessor:
    """**Lớp xử lý file JSON và hiển thị kết quả**"""
    
    @staticmethod
    def load_json_file(file_path: str) -> Optional[Dict]:
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
            if doc.end <= source_doc.page_count:
                new_doc.insert_pdf(source_doc, from_page=doc.start-1, to_page=doc.end-1)
            
            if len(new_doc) > 0:
                clean_name = sanitize_filename(doc.name)
                output_filename = f"./data_output/{save_dir}/{doc.stt}_{clean_name}.pdf"
                new_doc.save(output_filename)
            new_doc.close()


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
    FileProcessor.split_documents(documents, save_dir, original_path)
    return documents

# ==============================================================================
# **CHẠY CHƯƠNG TRÌNH**
# ==============================================================================

if __name__ == "__main__":
    # **Thay thế "1.json" bằng đường dẫn file của bạn**
    result = process_documents_strict_case("./data_parser/o_to_1.json", "./data_input/o_to.pdf", "results_o_to")