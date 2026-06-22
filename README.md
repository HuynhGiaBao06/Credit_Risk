# 🛡️ Predictive Credit Risk Modeling & Architecture

## 📌 1. Tổng quan dự án (Project Overview)
Dự án tập trung vào việc xây dựng hệ thống chấm điểm và phân loại rủi ro tín dụng dựa trên bộ dữ liệu hơn 30.000 hồ sơ khách hàng. Bài toán đối mặt với thách thức mất cân bằng lớp nghiêm trọng (Highly Imbalanced), trong đó tỷ lệ vỡ nợ (Class 1) chiếm tỷ trọng rất nhỏ.

**Vấn đề kinh doanh (Business Problem):**
Triết lý quản trị rủi ro cốt lõi của toàn bộ dự án là: *"Thà từ chối nhầm khách tốt, còn hơn cho vay nhầm khách xấu"*. Ưu tiên hàng đầu về mặt kỹ thuật là thiết lập các chốt chặn triệt tiêu hiện tượng rò rỉ dữ liệu (Data Leakage) khi xây dựng mô hình.

## 🚀 2. Hướng dẫn "Nhập môn" cho thành viên (Onboarding Guide)
Các thành viên (An Duy, Hữu Kiệt, Gia Bảo) làm việc theo kiến trúc OOP + Builder Pipeline, tuân thủ nguyên tắc "1 Class = 1 File". Dưới đây là checklist để bắt nhịp:

- [ ] **Bước 1: Hiểu bức tranh tổng thể.** Đọc lướt qua file README này và tài liệu Dataflow để nắm rõ luồng chảy dữ liệu chống rò rỉ.
- [ ] **Bước 2: Nắm quy trình quản lý task.** Truy cập Trello dự án để xem các thẻ công việc riêng biệt đã được chia chi tiết (Sprint 1 đến 4) cho từng người để tránh xung đột Git.
- [ ] **Bước 3: Thiết lập môi trường code.** Cài đặt extension `Database Client` trên VS Code để kết nối vào hệ thống cơ sở dữ liệu PostgreSQL (Neon.tech) theo đúng thông tin User (`member_duyna`, `member_kietnh`) được cấp phát.
- [ ] **Bước 4: Lưu ý môi trường Database.** Cần xử lý kịch bản "Cold Start", đợi 2-3s khởi động ở lệnh gọi đầu tiên do database serverless sẽ tự ngủ sau 5 phút không hoạt động.

## 🏗️ 3. Kiến trúc Dữ liệu & Pipeline (Single Source of Truth)
Dự án áp dụng chiến lược chống rò rỉ dữ liệu gồm 3 lớp bảo vệ kiên cố. Mọi xử lý phải tuân thủ nghiêm ngặt mô hình rẽ nhánh sau:

- **Giai đoạn 1 (Early Splitting):** Chia tập Train (80%) và Test (20%) ngay sau khi load dữ liệu thô, bắt buộc có tham số `stratified=y` theo `loan_status` để cô lập và "khóa chặt" tập Test hoàn toàn.
- **Giai đoạn 2 (Fit Phase):** Hệ thống chỉ "học" quy luật trên tập Train: Học mốc điền khuyết (Median/Mode), học K-Fold Target Encoding (K=5) kết hợp M-estimate Smoothing (m=50-100), học mốc ngoại lai 1%-99% và tham số StandardScaler.
- **Giai đoạn 3 (Transform Phase):** Áp dụng bộ quy luật sang cả Train và Test. **Bắt buộc:** Gọi lệnh `.drop()` để xóa cột `cb_person_cred_hist_length` ngay sau khi tạo biến phái sinh nhằm tránh đa cộng tuyến hoàn hảo.
- **Giai đoạn 4 (Model Branches - Rẽ nhánh cục bộ):**
  - **Nhánh A (Ridge Classifier - Tuyến tính):** Thực hiện cắt cụt ngoại lai (Capping) và chuẩn hóa thang đo (Scaling).
  - **Nhánh B (AdaBoost / LightGBM - Cây quyết định):** Bỏ qua Capping và bỏ qua Scaling do mô hình cây tự phân cắt ranh giới hiệu quả.

## ❓ 4. Câu hỏi nghiên cứu (Research Questions)
Dự án sẽ giải quyết 3 câu hỏi nghiên cứu trọng tâm để phục vụ nghiệp vụ tín dụng:

1. **Đánh giá Mô hình:** Trong ba mô hình Ridge Classifier, AdaBoost và LightGBM, mô hình nào dự đoán rủi ro vỡ nợ tín dụng tốt nhất khi được đánh giá trên tập dữ liệu mất cân bằng nghiêm trọng?
2. **Phân tích Insight:** Những yếu tố (features) nào có tác động lớn nhất đến xác suất vỡ nợ của khách hàng, và chúng phản ánh hành vi tài chính thực tế như thế nào?
3. **Tối ưu Ngưỡng & Bài toán Kinh doanh:** Việc tinh chỉnh ngưỡng quyết định (Threshold) dựa trên F2-Score giải quyết bài toán đánh đổi (trade-off) giữa quản trị rủi ro và tăng trưởng doanh thu tín dụng như thế nào?

## 🛠 5. Công nghệ & Thư viện sử dụng (Tech Stack)
- **Ngôn ngữ:** Python, SQL.
- **Quản lý Cơ sở dữ liệu:** PostgreSQL (Neon.tech Serverless Database).
- **Kiến trúc mã nguồn:** OOP (Object-Oriented Programming), Builder Design Pattern.
- **Xử lý dữ liệu:** Pandas, NumPy.
- **Học máy:** Scikit-learn (Ridge Classifier), LightGBM, AdaBoost.
- **Trực quan hóa Insight:** Matplotlib, Seaborn (Thiết kế ghép cặp đồ thị Horizontal Bar, Vertical Bar và Donut Chart).
- **Đánh giá mô hình (Metrics):** F2-Score, Recall, Hệ số Gini (>0.4) và PR-AUC (*Tuyệt đối không dùng Accuracy tổng thể*).

## 📊 6. Dữ liệu & Tiền xử lý (Data & Preparation)
- **Nguồn:** Credit Risk Dataset (>,000 dòng).
- **Đặc trưng chính:** Biến mục tiêu là `loan_status` (0: Không vỡ nợ, 1: Vỡ nợ). Chứa các thông tin nhân khẩu học, độ dài lịch sử tín dụng và xếp hạng khoản vay.
- **Kỹ nghệ đặc trưng (Feature Engineering):**
  - **Risk Target Encoding:** Biến danh mục chữ được nén thành xác suất rủi ro bằng cơ chế Out-of-Fold để giảm chiều dữ liệu.
  - **Data Binning:** Rời rạc hóa độ tuổi `person_age` thành các nhóm chu kỳ 7 năm.
  - **age_at_first_credit:** Độ chín muồi tài chính = `person_age` - `cb_person_cred_hist_length`.
  - **Estimated_Annual_Interest:** Áp lực lãi vay = `loan_amnt` * (`loan_int_rate` / 100).
  - **Income_per_Employment_Year:** Năng lực dòng tiền = `person_income` / (`person_emp_length` + 1e-6).
# Credit_Risk
