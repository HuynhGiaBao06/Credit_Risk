=======================================================================================
                         GIAI ĐOẠN 1: NẠP & PHÂN TÁCH TỪ GỐC
=======================================================================================

      [ SQL Database / Views ] 
                 │
                 ▼ (Import In-Memory)
      [ Dữ liệu thô (Raw Data) ]
                 │
                 ▼ (train_test_split | Tỷ lệ 80/20 | stratify=loan_status)
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
[ TẬP TRAIN (80%) ]       [ TẬP TEST (20%) ] ──────> (KHÓA LẠI: Tránh Data Leakage)
    │                                                   │
    │                                                   │
=======================================================================================
                   GIAI ĐOẠN 2: PREPROCESSING (ĐỒNG BỘ HÓA TRAIN & TEST)
=======================================================================================
    │
    ▼ (1) "HỌC" (FIT) TỪ TẬP TRAIN:
    ├─> Học Median/Mode để điền khuyết
    ├─> Học K-Fold Target Encoding + Smoothing (Tạo Bảng Tỷ Lệ Rủi Ro)
    ├─> Học các mốc phân vị (1% - 99%) để tìm Outlier
    └─> Học giá trị Mean, Std để Scaling
    │
    ▼ (2) "ÁP DỤNG" (TRANSFORM) LÊN CẢ TRAIN VÀ TEST:   <──(Kéo TẬP TEST vào để biến đổi)
    │
[ Dữ liệu đã điền khuyết ]                              
    │                                                   
    ├─> Map Target Encoding (Dựa vào Bảng Rủi Ro đã học)
    ├─> Rời rạc hóa (Binning) nhóm tuổi
    └─> Tạo 3 Feature mới (Lãi vay, Độ tuổi vay lần đầu, Thu nhập/Thâm niên)
    │
=======================================================================================
                       GIAI ĐOẠN 3: RẼ NHÁNH XỬ LÝ (MODEL BRANCHING)
=======================================================================================
    │
    ├─────────────────────────────────────────┐
    │                                         │
    ▼ NHÁNH A: MÔ HÌNH TUYẾN TÍNH             ▼ NHÁNH B: MÔ HÌNH CÂY QUYẾT ĐỊNH
  (Dành cho Ridge Classifier)               (Dành cho AdaBoost, LightGBM)
    │                                         │
    ▼                                         ▼
[ Cắt cụt Outlier (Capping) ]             [ BỎ QUA Outlier Capping ] 
  (Theo mốc 1-99% đã học)                   (Giữ nguyên gốc để cây tự chia cắt)
    │                                         │
    ▼                                         ▼
[ Cân bằng thang đo (Scaling) ]           [ BỎ QUA Scaling ]
  (Dùng StandardScaler)                     (Không cần thiết)
    │                                         │
=======================================================================================
                       GIAI ĐOẠN 4: HUẤN LUYỆN & XUẤT ĐÁNH GIÁ
=======================================================================================
    │                                         │
    ▼                                         ▼
[ Train: Ridge Classifier ]               [ Train: AdaBoost / LightGBM ]
    │                                         │
    └────────────────────┬────────────────────┘
                         │
                         ▼
               [ ĐÁNH GIÁ TRÊN TẬP TEST ]
         (Tối ưu Threshold dựa trên F2-Score)
         (So sánh bằng: Recall, Gini, PR-AUC)