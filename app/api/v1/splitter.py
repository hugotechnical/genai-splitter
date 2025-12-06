import json
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.schemas.splitter import SplitterResponse
from app.schemas.enums import ProfileType
from app.services.processor import DocumentProcessor
from app.utils import write_log  as logger

log = logger.setup_logger(__name__)
splitter_router = APIRouter()

__all__ = ["splitter_router"]

@splitter_router.post("/splitter", response_model=SplitterResponse)
async def split_document(
    # 1. Thay đổi: Nhận file trực tiếp và các tham số qua Form
    json_file: UploadFile = File(..., description="Upload file JSON chứa extracted_content"),
    profile_type: ProfileType = Form(default=ProfileType.HO_SO_PHE_DUYET, description="Loại hồ sơ"),
    pdf_filename: Optional[str] = Form(None, description="Tên file PDF giả lập (để hiển thị tên file output)")
):
    """
    Endpoint nhận file JSON upload trực tiếp và trả về kết quả phân tách.
    """
    
    # 2. Validate loại file (Optional)
    if not json_file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File upload phải là định dạng JSON")

    # 3. Đọc nội dung file từ memory
    try:
        content_bytes = await json_file.read()
        data = json.loads(content_bytes.decode('utf-8'))
        
        extracted_content = data.get('extracted_content', '')
        if not extracted_content:
            raise ValueError("Không tìm thấy trường 'extracted_content' trong JSON")
            
    except json.JSONDecodeError:
        log.error("File upload không phải JSON hợp lệ")
        raise HTTPException(status_code=400, detail="File JSON bị lỗi format")
    except Exception as e:
        log.error(f"Lỗi xử lý file: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # 4. Khởi tạo Processor
    log.info(f"Processing uploaded file: {json_file.filename} with profile: {profile_type}")
    processor = DocumentProcessor(profile_type=profile_type)
    
    # 5. Chạy Logic xử lý
    processor.process(extracted_content)
    
    # 6. Lấy kết quả Preview 
    # (Sử dụng hàm preview_results đã viết ở bước trước, không cần pdf_path thật)
    final_docs = processor.preview_results()

    return SplitterResponse(
        status="success",
        profile_used=profile_type.value,
        total_docs=len(final_docs),
        documents=final_docs
    )