SAMPLE_RULES = [
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
            ("GIAY CHUNG NHAN", "Hồ sơ bảo hiểm", "GIẤY CHỨNG NHẬN BẢO HIỂM", ["GROUPING"]), # Lưu ý: Key này khá chung chung
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
            ("HOP DONG BAO HIEM", "HỒ SƠ KHÁC", "Hợp đồng bảo hiểm", ["GROUPING"]),
            ("PHIEU PHAN LOAI RUI RO", "HỒ SƠ KHÁC", "Phiếu phân loại rủi ro"),
            ("PHIEU KHAI BAO THONG TIN", "HỒ SƠ KHÁC", "Phiếu khai báo thông tin"),
            ("CERTIFICATE OF CONFORMITY", "HỒ SƠ KHÁC", "Phiếu kiểm tra chất lượng xuất xưởng"),

        ]

# SAMPLE_RULES = [

#             # ================================
#             # NHÓM 1 – DANH MỤC HỒ SƠ CHI TIẾT
#             # ================================
#             ("DANH MUC", "Danh mục hồ sơ chi tiết", "Danh mục hồ sơ chi tiết"),

#             # =====================================
#             # NHÓM 2 – HỒ SƠ PHÊ DUYỆT
#             # =====================================

#             # Nghị quyết phê duyệt
#             ("PHE DUYET", "Hồ sơ phê duyệt", "Nghị quyết phê duyệt"),

#             # Thông báo cấp tín dụng có điều kiện
#             ("THONG BAO CAP TIN DUNG CO DIEU KIEN", "Hồ sơ phê duyệt", "Thông báo cấp tín dụng có điều kiện"),

#             # =====================================
#             # NHÓM 3 – HỒ SƠ PHÁP LÝ
#             # =====================================
#             ("CAN CUOC", "Hồ sơ pháp lý", "CCCD / Căn cước công dân"),
#             ("KET HON", "Hồ sơ pháp lý", "ĐKKH / Trích lục kết hôn"),
#             ("XAC NHAN TINH TRANG HON NHAN", "Hồ sơ pháp lý", "Giấy xác nhận tình trạng hôn nhân"),
#             ("CU TRU", "Hồ sơ pháp lý", "Giấy xác nhận thông tin cư trú"),
#             ("THONG TIN CU TRU", "Hồ sơ pháp lý", "VNeID thông tin cư trú"),
#             ("TOI CAM KET CHI SU DUNG", "Hồ sơ pháp lý", "Cam kết CMT/CCCD"),
#             ("GIAY KHAI SINH", "Hồ sơ pháp lý", "Giấy khai sinh"),
#             ("XAC NHAN NHAN KHAU", "Hồ sơ pháp lý", "Giấy xác nhận nhân khẩu"),

#             # =====================================
#             # NHÓM 4 – HỒ SƠ LỊCH SỬ QUAN HỆ TÍN DỤNG
#             # =====================================
#             ("BAO CAO", "Hồ sơ lịch sử tín dụng", "CIC"),
#             ("XAC NHAN TAT TOAN", "Hồ sơ lịch sử tín dụng", "Xác nhận tất toán"),
#             ("XAC NHAN DU NO", "Hồ sơ lịch sử tín dụng", "Xác nhận dư nợ"),
#             ("HOP DONG", "Hồ sơ lịch sử tín dụng", "HĐCV/KUNN món vay cũ"),  # chung

#             # =====================================
#             # NHÓM 5 – HỒ SƠ ĐỀ NGHỊ VAY VỐN
#             # =====================================
#             ("DE NGHI VAY VON", "Hồ sơ đề nghị vay vốn", "Giấy đề nghị vay vốn"),

#             # =====================================
#             # NHÓM 6 – HỒ SƠ MỤC ĐÍCH
#             # =====================================
#             ("HOP DONG MUA BAN", "Hồ sơ mục đích", "Hợp đồng mua bán"),
#             ("LOI CHUNG", "Hồ sơ mục đích", "Hợp đồng mua bán công chứng (trang cuối)"),
#             ("HOP DONG CHUYEN NHUONG", "Hồ sơ mục đích", "Hợp đồng chuyển nhượng"),
#             ("HOP DONG DAT COC", "Hồ sơ mục đích", "Hợp đồng đặt cọc"),
#             ("GIAY BIEN NHAN TIEN", "Hồ sơ mục đích", "Giấy biên nhận tiền"),
#             ("XAC NHAN GIAO DICH", "Hồ sơ mục đích", "Xác nhận giao dịch"),
#             ("XAC NHAN THANH TOAN", "Hồ sơ mục đích", "Giấy xác nhận thanh toán"),
#             ("DON DE NGHI", "Hồ sơ mục đích", "Đơn đề nghị"),
#             ("HOP DONG VAY", "Hồ sơ mục đích", "Bộ hợp đồng vay"),
#             ("THONG BAO THANH TOAN", "Hồ sơ mục đích", "Thông báo thanh toán"),
#             ("DE NGHI CHUYEN TIEN", "Hồ sơ mục đích", "Đề nghị chuyển tiền"),
#             ("THONG BAO BAN GIAO CAN HO", "Hồ sơ mục đích", "Thông báo bàn giao căn hộ"),
#             ("BIEN BAN BAN GIAO CAN HO", "Hồ sơ mục đích", "Biên bản bàn giao căn hộ"),

#             # =====================================
#             # NHÓM 7 – HỒ SƠ NGUỒN THU / TÀI CHÍNH
#             # =====================================
#             ("BANG KE THU NHAP", "Hồ sơ nguồn thu", "Bảng kê thu nhập"),
#             ("XAC NHAN HOAT DONG HO KINH DOANH", "Hồ sơ nguồn thu", "Xác nhận hoạt động hộ KD"),
#             ("DANG KY KINH DOANH", "Hồ sơ nguồn thu", "Đăng ký kinh doanh"),
#             ("GIAY NOP TIEN", "Hồ sơ nguồn thu", "Giấy nộp tiền NSNN"),
#             ("HOP DONG LAO DONG", "Hồ sơ nguồn thu", "Hợp đồng lao động"),
#             ("QUYET DINH BO NHIEM", "Hồ sơ nguồn thu", "Quyết định bổ nhiệm"),
#             ("XAC NHAN LUONG", "Hồ sơ nguồn thu", "Xác nhận lương"),
#             ("SAO KE", "Hồ sơ nguồn thu", "Sao kê lương"),
#             ("SO PHU", "Hồ sơ nguồn thu", "Sổ phụ"),
#             ("HOP DONG CHO THUE", "Hồ sơ nguồn thu", "Hợp đồng thuê tài sản"),
#             ("BAO CAO TAI CHINH", "Hồ sơ nguồn thu", "Báo cáo tài chính"),
#             ("BANG KE TAI SAN TICH LUY", "Hồ sơ nguồn thu", "Bảng kê tài sản tích lũy"),

#             # =====================================
#             # NHÓM 8 – HỒ SƠ TÀI SẢN BẢO ĐẢM
#             # =====================================
#             ("HOP DONG THE CHAP", "Hồ sơ TSBD", "Hợp đồng thế chấp"),
#             ("PHIEU YEU CAU DANG KY", "Hồ sơ TSBD", "Đơn đăng ký GDBĐ"),
#             ("BIEN BAN DINH GIA TAI SAN", "Hồ sơ TSBD", "Biên bản định giá"),
#             ("BIEN NHAN TAI SAN", "Hồ sơ TSBD", "Biên nhận tài sản"),
#             ("PHIEU NHAP KHO", "Hồ sơ TSBD", "Phiếu nhập kho"),
#             ("PHIEU NHAP KHO BO SUNG", "Hồ sơ TSBD", "Phiếu nhập kho bổ sung"),
#             ("THOA THUAN BA BEN", "Hồ sơ TSBD", "Thỏa thuận 3 bên quản lý TSĐB"),

#             # =====================================
#             # NHÓM 9 – HỒ SƠ BẢO HIỂM
#             # =====================================
#             ("GIAY CHUNG NHAN", "Hồ sơ bảo hiểm", "Giấy chứng nhận bảo hiểm"),
#             ("GIAY CHUNG NHAN BAO HIEM", "Hồ sơ bảo hiểm", "Hợp đồng bảo hiểm"),
#             ("GIAY XAC NHAN CHUYEN QUYEN THU HUONG BAO HIEM", "Hồ sơ bảo hiểm", "Chuyển quyền thụ hưởng"),
#             ("HOA DON GIA TRI GIA TANG", "Hồ sơ bảo hiểm", "Hóa đơn bảo hiểm"),
#             ("PHIEU THU", "Hồ sơ bảo hiểm", "Phiếu thu phí bảo hiểm"),
#             ("DE NGHI TAI TUC", "Hồ sơ bảo hiểm", "Đề nghị tái tục"),
#             ("GIAY YEU CAU BAO HIEM", "Hồ sơ bảo hiểm", "Giấy yêu cầu bảo hiểm"),

#             # =====================================
#             # NHÓM 10 – HỒ SƠ TÍN DỤNG
#             # =====================================
#             ("HOP DONG CHO VAY", "Hồ sơ tín dụng", "Hợp đồng cho vay"),
#             ("PHU LUC HOP DONG CHO VAY", "Hồ sơ tín dụng", "Phụ lục HĐCV"),
#             ("KHE UOC NHAN NO", "Hồ sơ tín dụng", "Khế ước nhận nợ"),
#             ("DE NGHI GIAI NGAN", "Hồ sơ tín dụng", "Đề nghị giải ngân"),
#             ("THOA THUAN BA BEN TRa THAY LAI VAY", "Hồ sơ tín dụng", "Thỏa thuận trả thay lãi vay"),
#             ("VAN BAN XAC NHAN", "Hồ sơ tín dụng", "Văn bản xác nhận dữ liệu"),

#             # =====================================
#             # NHÓM 11 – HỒ SƠ KHÁC
#             # =====================================
#             ("VAN BAN THOA THUAN", "Văn bản thỏa thuận", "Văn bản thỏa thuận"),

#             ("", "Khác", "Không thuộc các loại trên")
#         ]

# RULES_KEY2 = [

#     ("MB03.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB03"),
#     ("MB07.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB07"),
#     ("MB09.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB09"),
#     ("MB13.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB13"),
#     ("MB15.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB15"),
#     ("MB11.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB11"),
#     ("MB17.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB17"),
#     ("MB19.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB19"),
#     ("MB23.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB23"),

#     ("MB49A.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB49A"),
#     ("MB49B.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB49B"),

#     ("MB01.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB01"),
#     ("MB02.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB02"),
#     ("MB04.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB04"),

#     ("MB08.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB08"),
#     ("MB12.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB12"),
#     ("MB14.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB14"),
#     ("MB16.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB16"),
#     ("MB18.HDM-TT.DT.TK/02", "Form & Phụ lục", "Mã hiệu của form MB18"),
#     ("MB20.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB20"),

#     ("MB38.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB38"),
#     ("MB40.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB40"),
#     ("MB37.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB37"),
#     ("MB39.HDM-TT.DT.TK02", "Form & Phụ lục", "Mã hiệu của form MB39"),

# ]


# SAMPLE_RULES = [

#     # ===========================
#     # 1. NHÓM: FORM & PHỤ LỤC (MB01 – MB49)
#     # ===========================

#     ("GIAY DE NGHI DANG KY KIEM HOP DONG SU DUNG DICH VU", "Form & Phụ lục", "MB03/MB49A/MB49B/MB04"),
#     ("PHU LUC NHAN BIET KHACH HANG VA THU THAP THONG TIN FATCA", "Form & Phụ lục", "MB07/MB08"),
#     ("PHU LUC DANG KY MO VA SU DUNG TAI KHOAN THANH TOAN", "Form & Phụ lục", "MB09/MB11"),
#     ("PHU LUC DANG KY SU DUNG DICH VU VPBANK NEOBIZ", "Form & Phụ lục", "MB13/MB14"),
#     ("PHU LUC DANG KY SU DUNG DICH VU VPBANK NEOBIZ PLUS", "Form & Phụ lục", "MB15/MB16/MB17/MB18"),
#     ("PHU LUC DANG KY PHAT HANH VA SU DUNG THE GHI NO", "Form & Phụ lục", "MB19/MB20"),
#     ("PHU LUC DANG KY MO THEM TAI KHOAN THANH TOAN", "Form & Phụ lục", "MB23"),
#     ("GIAY DANG KY THIET LAP QUAN HE", "Form & Phụ lục", "MB01/MB02"),
#     ("GIAY DE NGHI DANG KY KIEM HOP DONG SU DUNG DICH VU", "Form & Phụ lục", "MB04"),
#     ("PHU LUC SU DUNG/THAY DOI THONG TIN GIAO DICH QUA FAX", "Form & Phụ lục", "MB37/MB38"),
#     ("PHU LUC SU DUNG/THAY DOI THONG TIN GIAO DICH QUA EMAIL", "Form & Phụ lục", "MB39/MB40"),

#     # ===========================
#     # 2. NHÓM: ĐKKD & CCCD & HỘ CHIẾU
#     # ===========================

#     ("GIAY CHUNG NHAN DANG KY KINH DOANH", "ĐKKD & Định danh", "Giấy ĐKKD"),
#     ("GIAY CHUNG NHAN DANG KY DOANH NGHIEP", "ĐKKD & Định danh", "Giấy ĐKKD"),
#     ("GIAY PHEP THANH LAP", "ĐKKD & Định danh", "Giấy ĐKKD"),
#     ("QUYET DINH THANH LAP", "ĐKKD & Định danh", "Giấy ĐKKD"),

#     ("CAN CUOC CONG DAN", "ĐKKD & Định danh", "CCCD"),
#     ("CAN CUOC", "ĐKKD & Định danh", "Căn cước"),
#     ("PASSPORT", "ĐKKD & Định danh", "Hộ chiếu"),

#     ("THI THUC", "ĐKKD & Định danh", "Thị thực/visa"),
#     ("THE TAM TRU", "ĐKKD & Định danh", "Thẻ tạm trú"),

#     # ===========================
#     # 3. NHÓM: GIẤY TỜ CÔNG TY
#     # ===========================

#     ("DIEU LE", "Giấy tờ công ty", "Điều lệ hoạt động"),
#     ("QUY CHE THANH LAP", "Giấy tờ công ty", "Điều lệ/Quy chế"),
#     ("QUY CHE HOAT DONG", "Giấy tờ công ty", "Điều lệ/Quy chế"),
#     ("QUY CHE THU PHI", "Giấy tờ công ty", "Quy chế thu chi"),

#     ("bo nhiem ke toan truong", "Giấy tờ công ty", "Bổ nhiệm kế toán trưởng"),
#     ("QUYET DINH BO NHIEM", "Giấy tờ công ty", "Bổ nhiệm kế toán trưởng"),
#     ("PHU TRACH KE TOAN", "Giấy tờ công ty", "Bổ nhiệm kế toán trưởng"),

#     ("CAM KET KHONG KE TOAN TRUONG", "Giấy tờ công ty", "Cam kết không có kế toán trưởng"),
#     ("CHUA DANG KY KE TOAN TRUONG", "Giấy tờ công ty", "Cam kết không có kế toán trưởng"),

#     ("BIEN BAN HOP HOI DONG", "Giấy tờ công ty", "Biên bản họp HĐTV/HĐQT"),

#     ("QUYET DINH MIEN NHIEM", "Giấy tờ công ty", "Quyết định miễn nhiệm KT trưởng"),

#     # ===========================
#     # 4. NHÓM: GIẤY TỜ KHÁC
#     # ===========================

#     ("BIEN BAN GIAO NHAN", "Giấy tờ khác", "Biên bản bàn giao"),
#     ("BIEN BAN BAN GIAO", "Giấy tờ khác", "Biên bản bàn giao"),

#     ("TTTB SO GTTT", "Giấy tờ khác", "Tra cứu 1414"),
#     ("CONG THONG TIN QUOC GIA", "Giấy tờ khác", "Tra cứu doanh nghiệp"),
#     ("THUE VIET NAM", "Giấy tờ khác", "Tra cứu thuế"),

#     ("VNEID", "Giấy tờ khác", "Kết quả định danh điện tử"),
#     ("QR CODE", "Giấy tờ khác", "Ảnh quét QR từ app định danh"),

#     ("PHIEU THU PHI", "Giấy tờ khác", "Phiếu thu phí"),
#     ("GIAY NOP TIEN MAT", "Giấy tờ khác", "Phiếu thu phí"),

#     ("UY QUYEN", "Giấy tờ khác", "Văn bản ủy quyền"),
#     ("GIAY UY QUYEN", "Giấy tờ khác", "Văn bản ủy quyền"),
#     ("POWER OF AUTHORIZE", "Giấy tờ khác", "Văn bản ủy quyền"),

# ]
