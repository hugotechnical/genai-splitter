SAMPLE_RULES = [
    # --- NHÓM: Hồ sơ pháp lý ---
    ("CAN CUOC", "Hồ sơ pháp lý", "Căn cước công dân/CMND", ["SAO Y"], ["Thông tin Căn cước công dân"]),
    ("DANG KY KINH DOANH", "Hồ sơ pháp lý", "Giấy chứng nhận Đăng ký kinh doanh"),
    ("CHUNG MINH NHAN DAN", "Hồ sơ pháp lý", "Chứng minh nhân dân"),
    ("KET HON", "Hồ sơ pháp lý", "Giấy chứng nhận kết hôn/Trích lục kết hôn"),
    ("XAC NHAN TINH TRANG HON NHAN", "Hồ sơ pháp lý", "Giấy xác nhận tình trạng hôn nhân"),
    ("CU TRU", "Hồ sơ pháp lý", "Giấy xác nhận thông tin cư trú"),
    ("THONG TIN CU TRU", "Hồ sơ pháp lý", "Thông tin cư trú (VNeID)"),
    ("TOI CAM KET CHI SU DUNG 1 SO CCCD", "Hồ sơ pháp lý", "Cam kết sử dụng 01 số CCCD/CMND"),
    ("TOI CAM KET CHI SU DUNG 2 SO CCCD", "Hồ sơ pháp lý", "Cam kết sử dụng 02 số CCCD/CMND"),
    ("GIAY KHAI SINH", "Hồ sơ pháp lý", "Giấy khai sinh"),
    ("GIAY CHUNG NHAN DANG KY DOANH NGHIEP", "Hồ sơ pháp lý", "Giấy chứng nhận Đăng ký doanh nghiệp"),
    ("NHOM KHACH HANG LIEN QUAN", "Hồ sơ pháp lý", "Danh sách nhóm khách hàng liên quan"),
    ("DIEU LE", "Hồ sơ pháp lý", "Điều lệ công ty"),
    ("BIEN BAN HOP", "Hồ sơ pháp lý", "Biên bản họp HĐQT/HĐTV"),
    ("SO DANG KI DOANH NGHIEP", "Hồ sơ pháp lý", "Sổ đăng ký thành viên"),
    ("SO CO DONG", "Hồ sơ pháp lý", "Sổ đăng ký cổ đông"),
    ("DANH SACH HOI DONG QUAN TRI", "Hồ sơ pháp lý", "Danh sách thành viên HĐQT/HĐTV"),
    
    # --- NHÓM: Hồ sơ lịch sử tín dụng ---
    ("HTTPS://10.36.28.94/CICINTERNAL", "Hồ sơ lịch sử tín dụng", "Báo cáo lịch sử tín dụng (CIC)"),

    # --- NHÓM: Hồ sơ hoạt động ---
    ("HOA DON", "Hồ sơ hoạt động", "Hóa đơn/Chứng từ hoạt động"),

    # --- NHÓM: Hồ sơ quan hệ tín dụng ---
    ("CIC", "Hồ sơ quan hệ tín dụng", "Báo cáo quan hệ tín dụng"),

    # --- NHÓM: Hồ sơ mục đích cấp tín dụng ---
    ("GIAY DE NGHI CAP TIN DUNG", "Hồ sơ mục đích cấp tín dụng", "Giấy đề nghị cấp tín dụng"),
    ("BAO CAO DE XUAT CAP TIN DUNG", "Hồ sơ mục đích cấp tín dụng", "Báo cáo đề xuất cấp tín dụng"),
    ("TO TRINH THAM DINH TIN DUNG", "Hồ sơ mục đích cấp tín dụng", "Tờ trình thẩm định tín dụng"),
    ("BANG KE", "Hồ sơ mục đích cấp tín dụng", "Bảng kê mục đích sử dụng vốn"),

    # --- NHÓM: Hồ sơ tài chính ---
    ("BAO CAO TINH HINH TAI CHINH", "Hồ sơ tài chính", "Báo cáo tài chính"),
    ("BANG CAN DOI KE TOAN", "Hồ sơ tài chính", "Bảng cân đối kế toán"),
    ("BAO CAO KET QUA HOAT DONG SAN XUAT KINH DOANH", "Hồ sơ tài chính", "Báo cáo kết quả hoạt động kinh doanh"),
    
    ("TO KHAI THUE GIA TRI GIA TANG", "Hồ sơ tài chính", "Tờ khai thuế GTGT"),
    ("CHAP NHAN HO SO KHAI THUE", "Hồ sơ tài chính", "Thông báo chấp nhận hồ sơ khai thuế"),

    # --- NHÓM: Hồ sơ tài sản ---
    ("HOP DONG MUA BAN", "Hồ sơ tài sản", "Hợp đồng mua bán tài sản"),
    ("HOP DONG KINH TE", "Hồ sơ tài sản", "Hợp đồng kinh tế"),
    ("BAO GIA TAI SAN", "Hồ sơ tài sản", "Bảng báo giá tài sản"),
    ("BAO CAO TU VAN GIA TRI TAI SAN", "Hồ sơ tài sản", "Báo cáo tư vấn định giá"),
    ("BAO CAO DINH GIA TAI SAN", "Hồ sơ tài sản", "Báo cáo thẩm định giá"),
    ("BAO CAO DANH GIA HIEN TRANG TAI SAN BAO DAM", "Hồ sơ tài sản", "Báo cáo đánh giá hiện trạng TSBĐ"),
    ("BIEN BAN DINH GIA TAI SAN", "Hồ sơ tài sản", "Biên bản định giá tài sản"),
    ("DANG KY KET HON", "Hồ sơ tài sản", "Giấy chứng nhận kết hôn (Hồ sơ TSBĐ)"),
    ("CAM KET TAI SAN RIENG", "Hồ sơ tài sản", "Cam kết/Thỏa thuận tài sản riêng"),
    ("DANG KIEM / DANG KY XE /GIAY HEN", "Hồ sơ tài sản", "Đăng ký xe/Đăng kiểm/Giấy hẹn"),
    ("QUYEN SU DUNG DAT", "Hồ sơ tài sản", "Giấy chứng nhận Quyền sử dụng đất (Sổ đỏ)"),
    ("HOP DONG THE CHAP", "Hồ sơ tài sản", "Hợp đồng thế chấp"),
    ("HOP DONG CAM Co", "Hồ sơ tài sản", "Hợp đồng cầm cố"),
    ("HOP DONG BAO DAM", "Hồ sơ tài sản", "Hợp đồng bảo đảm"),
    ("DON DANG KY", "Hồ sơ tài sản", "Đơn đăng ký giao dịch bảo đảm"),
    ("PHIEU YEU CAU DANG KY", "Hồ sơ tài sản", "Phiếu yêu cầu đăng ký biện pháp bảo đảm"),

    # --- NHÓM: Hồ sơ bảo hiểm ---
    ("GIAY XAC NHAN CHUYEN QUYEN THU HUONG BAO HIEM", "Hồ sơ bảo hiểm", "Xác nhận chuyển quyền thụ hưởng bảo hiểm"),
    
    # --- NHÓM: Hồ sơ khác ---
    ("MOI TRUONG XA HOI", "Hồ sơ khác", "Đánh giá rủi ro môi trường xã hội"),
    ("BANG TRA LOI CAU HOI", "Hồ sơ khác", "Bảng câu hỏi đánh giá khách hàng"),
    ("KHACH HANG LIEN QUAN", "Hồ sơ khác", "Danh sách khách hàng liên quan"),
    ("PHUONG TIEN", "Hồ sơ khác", "Giấy chứng nhận đăng ký phương tiện"),
    ("GIAY DE NGHI NHAP KHO TAI SAN BAO DAM", "Hồ sơ khác", "Giấy đề nghị nhập kho TSBĐ"),
    ("QUYET DINH PHE DUYET TIN DUNG", "Hồ sơ khác", "Quyết định/Thông báo phê duyệt tín dụng"),
    ("GIAY BIEN NHAN HO SO TAI SAN BAO DAM", "Hồ sơ khác", "Giấy biên nhận hồ sơ TSBĐ"),
    ("HOP DONG BAO LANH", "Hồ sơ khác", "Hợp đồng bảo lãnh"),
    ("HOP DONG CHO VAY", "Hồ sơ khác", "Hợp đồng tín dụng/Cho vay"),
    ("GIAY DE NGHI TRICH PHI BAO HIEM TU DONG", "Hồ sơ khác", "Giấy đề nghị trích phí bảo hiểm tự động"),
    ("XE CO GIOI", "Hồ sơ khác", "Giấy tờ xe cơ giới"),
    ("PHIEU PHAN LOAI RUI RO MOI TRUONG VA XA HOI", "Hồ sơ khác","Phiếu phân loại rủi ro môi trường - xã hội"),
    ("PHIEU DON VI KINH DOANH KHAI BAO THONG TIN NHOM KHACH HANG LIEN QUAM", "Phiếu khai báo thông tin KHDN", "Phiếu ĐVKD khai báo thông tin nhóm KHLQ"),
    ("PHIEU NHAP KHO BO SUNG TAI SAN BAO DAM","Hồ sơ khác","Phiếu nhập kho bổ sung TSBĐ"),
    ("THONG TIN CAN CUOC CONG DAN", "Hồ sơ khác", "Thông tin Căn cước công dân"),
    ("QUYET DINH", "Hồ sơ khác", "Quyết định hành chính/Quản trị"),
    ("KINH DOANH VAN TAI BANG XE O TO", "Hồ sơ khác", "Giấy phép kinh doanh vận tải", ["SAO Y"], ["VAN TAI BANG XE O TO"]),
    ("PHIEU GIAO DỊCH", "Hồ sơ tài sản", "Phiếu giao dịch"),
    # Lưu ý: Các mục bị comment (ví dụ: Dang ky xe, Giay hen) đã được gộp vào mục chung
    # Lưu ý: Mục "Phiếu giao dịch" (VN0010186) thường là thông tin giao dịch, có thể bổ sung nếu cần 
]      

NHA_DU_AN_RULES = [
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
    ("BANG KE THU NHAP", "Hồ sơ nguồn thu", "Bảng kê thu nhập", ["SAO Y"], ["Ngan Hang Việt Nam Thịnh Vượng BANG KE THU NHAP"]),
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