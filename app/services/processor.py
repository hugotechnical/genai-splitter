import re
import fitz
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from thefuzz import fuzz

from app.core.config import settings
from app.utils.text import TextUtils
from app.utils.rules_data import get_rules_by_profile
from app.schemas.enums import ProfileType
from app.schemas.splitter import DocumentResult
from app.services.engine import MatchingEngine, DocumentRule

class DocumentState:
    """Helper class để quản lý trạng thái tài liệu"""
    def __init__(self, stt, category, name, start, end, trigger):
        self.stt = stt
        self.category = category
        self.name = name
        self.start = start
        self.end = end
        self.trigger = trigger

    def to_schema(self, output_path: str = None) -> DocumentResult:
        return DocumentResult(
            stt=self.stt,
            category=self.category,
            name=self.name,
            start=self.start,
            end=self.end,
            trigger=self.trigger,
            output_path=output_path
        )

class DocumentProcessor:
    def __init__(self, profile_type: ProfileType):
        # Load rules động dựa trên profile_type
        raw_rules = get_rules_by_profile(profile_type)
        self.rules = self._parse_rules(raw_rules)
                
        self.documents: List[DocumentState] = []
        self.current_doc_state: Dict = {"start": None}

    def _parse_rules(self, rules_data: List[Tuple]) -> List[DocumentRule]:
        rules = []
        for item in rules_data:
            # Handle variable length tuple safely
            key = item[0]
            category = item[1]
            name = item[2]
            exclude_keys = item[3] if len(item) > 3 else []
            aliases = item[4] if len(item) > 4 else []
            
            rules.append(DocumentRule(key, category, name, exclude_keys, aliases))
        return rules

    def _find_matching_rule(self, page_text: str) -> Optional[Tuple[DocumentRule, str]]:
        header_raw = TextUtils.extract_header(page_text)
        header_clean = TextUtils.clean_text_for_comparison(header_raw)
        
        candidates = []

        # Quét qua tất cả rules
        for rule in self.rules:
            # 1. Check Alias (Ưu tiên tuyệt đối)
            for alias in rule.aliases:
                normalized_alias = TextUtils.clean_text_for_comparison(alias)
                if normalized_alias in header_clean:
                    candidates.append((100, len(alias), rule, alias))
                    break
            
            # 2. Check Matching Engine
            trigger_text, score = MatchingEngine.find_match_with_score(page_text, rule)
            if trigger_text:
                candidates.append((score, len(rule.key), rule, trigger_text))

        # Logic "Best Match Wins"
        if not candidates:
            return None

        # Sort: Length DESC (Ưu tiên key dài), Score DESC
        candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
        best_score, _, best_rule, best_trigger = candidates[0]

        # 3. Check Exclude (Loại trừ)
        for ex_key in best_rule.exclude_keys:
            ex_clean = TextUtils.clean_text_for_comparison(ex_key)
            # Fuzzy exclude để an toàn
            if fuzz.partial_ratio(ex_clean, header_clean) >= 85:
                return None
        
        # 4. Check "DINH KEM" (Phụ lục đính kèm không được coi là đầu mục)
        if "DINH KEM" in header_clean:
            key_check = TextUtils.clean_text_for_comparison(best_trigger if best_trigger else best_rule.key)
            attach_pos = header_clean.find("DINH KEM")
            key_pos = header_clean.find(key_check)
            if attach_pos != -1 and key_pos != -1 and attach_pos < key_pos:
                return None

        return (best_rule, best_trigger)

    def _finalize_document(self, end_page: int):
        if self.current_doc_state.get("start") is not None:
            doc = DocumentState(
                stt=len(self.documents) + 1,
                category=self.current_doc_state["category"],
                name=self.current_doc_state["name"],
                start=self.current_doc_state["start"],
                end=end_page,
                trigger=self.current_doc_state["trigger"]
            )
            self.documents.append(doc)
            self.current_doc_state = {"start": None}

    def process(self, content: str) -> List[DocumentState]:
        """Core flow xử lý trang"""
        pages = re.split(settings.PAGE_BREAK_DELIMITER, content)
        total_pages = len(pages)
        
        for i, page_text in enumerate(pages):
            page_num = i + 1
            page_text_clean = page_text.strip()
            
            # Bỏ qua trang trắng (nhưng nếu đang trong doc thì coi như trang nội dung)
            if TextUtils.is_blank_page(page_text_clean):
                continue

            match_result = self._find_matching_rule(page_text_clean)
            matched_rule, trigger_text = match_result if match_result else (None, None)

            # Check Continuation: Nếu rule tìm thấy trùng tên với doc đang mở -> Gộp
            is_continuation = False
            if matched_rule and self.current_doc_state.get("start") is not None:
                if matched_rule.name == self.current_doc_state.get("name"):
                    is_continuation = True

            if matched_rule and not is_continuation:
                # Tìm thấy tài liệu MỚI -> Đóng tài liệu cũ
                self._finalize_document(page_num - 1)
                
                # Mở tài liệu mới
                self.current_doc_state = {
                    "category": matched_rule.category,
                    "name": matched_rule.name,
                    "start": page_num,
                    "trigger": f"{matched_rule.key} -> '{trigger_text}'" 
                }
            elif self.current_doc_state.get("start") is None:
                # Không tìm thấy rule và chưa có doc nào mở -> Không xác định
                self.documents.append(DocumentState(
                    len(self.documents) + 1, "Phân loại", "Tài liệu không xác định", 
                    page_num, page_num, "NOT_FOUND"
                ))
            # Else: Đang có doc mở và không tìm thấy rule mới -> Coi như trang tiếp theo của doc đó

        # Đóng tài liệu cuối cùng
        self._finalize_document(total_pages)
        return self.documents

    def split_pdf(self, pdf_path: Path, output_dir: Path) -> List[DocumentResult]:
        results = []
        try:
            src_doc = fitz.open(pdf_path)
        except Exception:
            return [d.to_schema() for d in self.documents]

        for doc in self.documents:
            # Bỏ qua trang trắng hoặc Not Found có độ dài 1 trang
            if doc.trigger in ["BLANK_PAGE", "NOT_FOUND"] and doc.start == doc.end:
                results.append(doc.to_schema(output_path=None))
                continue

            start_idx = doc.start - 1
            end_idx = min(doc.end - 1, len(src_doc) - 1)
            
            out_rel_path = None
            if start_idx < len(src_doc):
                with fitz.open() as new_doc:
                    new_doc.insert_pdf(src_doc, from_page=start_idx, to_page=end_idx)
                    if len(new_doc) > 0:
                        safe_name = TextUtils.sanitize_filename(doc.name)
                        filename = f"{doc.stt:02d}_{doc.start}-{doc.end}_{safe_name}.pdf"
                        save_path = output_dir / filename
                        new_doc.save(save_path)
                        
                        try:
                            out_rel_path = str(save_path.relative_to(settings.BASE_DIR))
                        except ValueError:
                            out_rel_path = str(save_path)
            
            results.append(doc.to_schema(output_path=out_rel_path))
        
        src_doc.close()
        return results
    
    def preview_results(self) -> List[DocumentResult]:
        """
        Chỉ in kết quả phân tách ra console và trả về metadata.
        Không cần file PDF gốc, không thực hiện cắt file.
        """
        results = []
        
        print("\n" + "="*110)
        print(f"🚀 KẾT QUẢ PHÂN TÁCH TÀI LIỆU (PREVIEW MODE)")
        print("="*110)
        print(f"{'STT':<4} | {'PHẠM VI':<10} | {'TÊN TÀI LIỆU':<50} | {'TRIGGER'}")
        print("-" * 110)

        for doc in self.documents:
            # 1. Logic lọc bỏ (Giữ nguyên: Bỏ trang trắng/Not found đơn lẻ)
            if doc.trigger in ["BLANK_PAGE", "NOT_FOUND"] and doc.start == doc.end:
                results.append(doc.to_schema(output_path=None))
                continue

            # 2. Tạo tên file giả lập (để visualize)
            safe_name = TextUtils.sanitize_filename(doc.name)
            filename_simulated = f"{doc.stt:02d}_{doc.start}-{doc.end}_{safe_name}.pdf"
            
            # 3. In ra Console
            page_range = f"{doc.start}-{doc.end}"
            # Cắt ngắn trigger nếu quá dài để hiển thị bảng cho đẹp
            display_trigger = (doc.trigger[:30] + '..') if len(doc.trigger) > 30 else doc.trigger
            
            print(f"{doc.stt:<4} | {page_range:<10} | {doc.name:<50} | {display_trigger}")

            # 4. Tạo kết quả trả về API
            # output_path là None vì không có file thật
            results.append(doc.to_schema(output_path=None))
        
        print("="*110 + "\n")
        
        return results