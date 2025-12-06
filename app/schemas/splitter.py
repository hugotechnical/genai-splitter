from typing import List, Optional
from pydantic import BaseModel
from app.schemas.enums import ProfileType

class DocumentResult(BaseModel):
    stt: int
    category: str
    name: str
    start: int
    end: int
    trigger: str
    output_path: Optional[str] = None

class SplitterRequest(BaseModel):
    json_filename: str
    pdf_filename: str
    # Mặc định là phê duyệt, nhưng user có thể chọn loại khác
    profile_type: ProfileType = ProfileType.HO_SO_PHE_DUYET 

class SplitterResponse(BaseModel):
    status: str
    profile_used: str
    total_docs: int
    documents: List[DocumentResult]