# KIẾN TRÚC DATA PIPELINE: MÔ HÌNH PHÂN LOẠI RỦI RO TÍN DỤNG

**Mục tiêu:** Xây dựng hệ thống Data Pipeline chuẩn xác, sử dụng chiến lược "Phân tách từ gốc" (Early Splitting) để ngăn chặn tuyệt đối hiện tượng rò rỉ dữ liệu (Data Leakage). Toàn bộ quy trình tuân thủ nguyên tắc: **Chỉ "Học" (Fit) trên tập Train, và "Áp dụng" (Transform) lên tập Train và Test** .

---

## BƯỚC 1: GIAI ĐOẠN KHỞI TẠO & PHÂN TÁCH TỪ GỐC
*Giai đoạn này đảm bảo tập Test được cách ly hoàn toàn và đóng vai trò như dữ liệu tương lai chưa từng tồn tại .*

* **Data Convert:** Dữ liệu được làm sạch sơ bộ và JOIN các bảng cần thiết thông qua các View trên SQL, sau đó đẩy dữ liệu thô vào môi trường Python .
* **Early Splitting (Chia tách dữ liệu):** Thực hiện chia tập Train/Test theo tỷ lệ **80/20** ngay sau khi load dữ liệu .
* **Cân bằng lớp:** Bắt buộc khai báo tham số `stratified=y` (dựa trên biến mục tiêu `loan_status`) để đảm bảo tỷ lệ vỡ nợ ở hai tập là tương đương nhau .

---

## BƯỚC 2: GIAI ĐOẠN "HỌC" QUY LUẬT (FIT PHASE)
*Xây dựng bộ "từ điển" quy luật thống kê chỉ dựa trên dữ liệu của tập Train .*

* **Missing Value Imputation:** Tính toán giá trị Trung vị (Median) cho các biến số và Yếu vị (Mode - Giá trị xuất hiện nhiều nhất) cho các biến phân loại .
* **Risk Target Encoding (K-Fold + Smoothing):** Kỹ thuật chuyển biến chữ (vd: `loan_intent`, `person_home_ownership`) thành số hóa (tỷ lệ vỡ nợ) để giảm đa cộng tuyến mà không làm phình to dữ liệu . 
  * **K-Fold Out-of-Fold:** Chia tập Train thành K phần (K=5). Giá trị mã hóa của một dòng dữ liệu được tính từ các fold còn lại, đảm bảo dòng đó không tự học nhãn của chính nó.
  * **M-estimate Smoothing:** Đóng vai trò là "lưới an toàn", kéo tỷ lệ rủi ro của các nhóm có ít dữ liệu (nhóm hiếm) về mức tỷ lệ vỡ nợ trung bình toàn cục (Global Mean) để chống Overfitting .
* **Xác định mốc Outlier (Ngoại lai):** Tính toán các mốc phân vị (ví dụ 1% và 99%) từ tập Train để sử dụng cho bước cắt cụt (Capping) sau này .
* **Tính tham số Scaling:** Khởi tạo `StandardScaler` hoặc `RobustScaler` và `fit()` để tìm giá trị trung bình (mean) và độ lệch chuẩn (std).

---

## BƯỚC 3: GIAI ĐOẠN "ÁP DỤNG" & FEATURE ENGINEERING (TRANSFORM PHASE)
*Sử dụng bộ "từ điển" ở Bước 2 để biến đổi dữ liệu trên cả tập Train và tập Test.*

* **Điền khuyết dữ liệu:** Điền các giá trị NaN bằng các giá trị Median/Mode đã học.
* **Map Target Encoding:** Sử dụng bảng Tỷ lệ rủi ro học từ tập Train để ánh xạ (Map) sang tập Test [12]. **Tuyệt đối không tính toán lại tỷ lệ này trên tập Test**. (Nếu Test xuất hiện danh mục mới, điền bằng Global Mean của tập Train) .
* **Data Binning:** Rời rạc hóa biến `person_age` thành các khoảng 7 năm (ví dụ: 22-28, 29-35) để giúp mô hình bắt chu kỳ độ tuổi vay .
* **Feature Creation (Tạo đặc trưng mới):**
  * `age_at_first_credit` = `person_age` - `cb_person_cred_hist_length` . Ngay sau khi tính toán xong biến `age_at_first_credit`, **bắt buộc phải loại bỏ (drop)** cột gốc `cb_person_cred_hist_length` ra khỏi tập dữ liệu ở cả hai nhánh Train và Test. Việc này đảm bảo biến mới hoàn toàn thay thế biến cũ, triệt tiêu đa cộng tuyến hoàn hảo, giúp trọng số của mô hình Ridge Classifier không bị sai lệch.
  * `Estimated_Annual_Interest` = `loan_amnt` * (`loan_int_rate` / 100) .
  * `Income_per_Employment_Year` = `person_income` / (`person_emp_length` + epsilon) [Tham số mặd định: EPSILON = 1e-6].

---

## BƯỚC 4: RẼ NHÁNH XỬ LÝ CHO CÁC MÔ HÌNH (MODEL BRANCHES)
*Pipeline tách làm 2 nhánh để tối ưu hóa theo đặc thù đề kháng nhiễu và thang đo của thuật toán [11].*

### Nhánh A: Dành cho Baseline Model (Ridge Classifier)
*Bản chất: Mô hình tuyến tính có L2 Regularization, cực kỳ nhạy cảm với thang đo và ngoại lai.*
* **Xử lý Outlier (Capping):** Cắt cụt (Clip) các giá trị dị biệt vượt mốc phân vị 1% và 99% đã học .
* **Feature Scaling:** Bắt buộc áp dụng `StandardScaler` hoặc `RobustScaler` để đưa các biến có giá trị lớn (như thu nhập) và biến nhỏ (như độ tuổi) về cùng một hệ quy chiếu .

### Nhánh B: Dành cho Tree-based Models (AdaBoost & LightGBM)
*Bản chất: Mô hình chia cắt theo ngưỡng (threshold), đề kháng cực tốt với thang đo và khoảng cách dữ liệu .*
* **KHÔNG Capping Outlier:** Giữ nguyên vẹn thông tin gốc (tuy nhiên AdaBoost rất nhạy cảm với nhiễu, nên cần cẩn thận làm sạch những điểm dữ liệu quá bất thường) .
* **KHÔNG Feature Scaling:** Các mô hình cây không cần chuẩn hóa dữ liệu .

---

## BƯỚC 5: ĐÁNH GIÁ & TỐI ƯU HÓA MÔ HÌNH (MODEL EVALUATION)
*Đặc thù bài toán rủi ro tín dụng là sự mất cân bằng lớp nghiêm trọng. Tuyệt đối KHÔNG sử dụng độ chính xác tổng thể (Accuracy) .*

* **Tối ưu hóa Threshold bằng F2-Score:** Thay vì dùng F1-Score cân bằng, F2-Score đặt trọng số của Recall cao gấp 2 lần Precision . Điều này hoàn toàn phù hợp với triết lý: *"Thà từ chối nhầm khách tốt, còn hơn cho vay nhầm khách xấu"* .
* **Khung Metrics Đánh Giá Chéo:**
  * **Recall (Nhóm 1 - Nợ xấu):** Chỉ số sinh tử ưu tiên hàng đầu, cần tối đa hóa để không lọt lưới nợ xấu gây tổn thất vốn trực tiếp [17, 19].
  * **Precision (Nhóm 1 - Nợ xấu):** Cần duy trì ở mức hợp lý để không từ chối "oan" quá nhiều khách tốt, làm mất cơ hội doanh thu .
  * **Hệ số Gini:** Tiêu chuẩn ngành chấm điểm tín dụng. Mục tiêu Gini > 0.4 (tương đương ROC-AUC > 0.7) để đảm bảo mô hình phân tách tốt rủi ro .
  * **PR-AUC (Precision-Recall AUC):** Thước đo gắt gao nhất, tập trung hoàn toàn vào lớp thiểu số, phản ánh hiệu suất thực tế tốt hơn ROC-AUC khi tỷ lệ nợ xấu cực kỳ thấp .