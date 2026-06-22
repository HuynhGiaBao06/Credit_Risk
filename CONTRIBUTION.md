# 📖 HƯỚNG DẪN ĐÓNG GÓP & GIT WORKFLOW (CONTRIBUTING GUIDELINES)

Chào mừng các thành viên (An Duy, Hữu Kiệt, Gia Bảo) đến với dự án Phân loại Rủi ro Tín dụng! Để đảm bảo quy trình làm việc nhóm hiệu quả, tránh xung đột code (conflict) trên kiến trúc OOP "1 Class = 1 File", vui lòng tuân thủ nghiêm ngặt các quy tắc dưới đây.

## 🛠 1. Cài đặt môi trường làm việc (Getting Started)
Mỗi thành viên cần thiết lập môi trường phát triển độc lập trên máy cá nhân:

- **Clone repository:** `git clone <url_của_repository>` và `cd <tên_thư_mục_dự_án>`
- **Tạo môi trường ảo (Virtual Environment):** `python -m venv venv`
  - Windows: `venv\Scripts\activate`
  - macOS/Linux: `source venv/bin/activate`
- **Cài đặt thư viện:** `pip install -r requirements.txt` (đảm bảo cài đặt đủ thư viện như Scikit-learn, LightGBM, Pandas, psycopg2...)

## 🌿 2. Quy Tắc Đặt Tên Branch (Branching Strategy)
Tuyệt đối không push code trực tiếp lên nhánh `main`. Mọi thay đổi phải thực hiện trên nhánh riêng.

**Cú pháp bắt buộc:** `<số thứ tự>_<user_thành viên>_<file thay đổi>`

- `<số thứ tự>`: Số thứ tự Sprint hoặc Task (gồm 2 chữ số: 01, 02, 03...).
- `<user_thành viên>`: Tên người thực hiện viết tắt và in hoa (NAD, NHK, HGB).
- `<file thay đổi>`: Tên file class bạn làm chủ (viết thường, cách nhau bằng dấu gạch dưới).

**Ví dụ nhánh hợp lệ (bám sát phân công):**
- `01_NAD_db_config` (An Duy làm file db_config.py tuần 1)
- `02_NHK_feature_engineer` (Hữu Kiệt làm file feature_engineer.py tuần 2)
- `03_HGB_pipeline_builder` (Gia Bảo làm pipeline_builder.py tuần 3)
- `04_NAD_02_models_regression` (An Duy làm file notebook tuần 4)

❌ **Không dùng:** feat/..., fix/..., main, hoặc các tên chung chung như 01_update.

## 📊 3. Quy Tắc Với Dữ Liệu & Notebook
- **Không commit file dữ liệu lớn:** Các file `credit_risk_dataset.csv`, `data_raw.csv` trong thư mục `data/data_raw/` bắt buộc phải được liệt kê trong `.gitignore`.
- **Quy tắc Jupyter Notebook (trong notebooks/):**
  - Trước khi commit, chọn **Kernel -> Restart & Run All** để đảm bảo code chạy không lỗi.
  - **Xóa output quá dài:** Tránh in ra hàng nghìn dòng dữ liệu làm phình to file `.ipynb`.
  - Ghi chú rõ ràng bằng Markdown khi vẽ các biểu đồ phân tích Insight hoặc tính toán Threshold bằng F2-Score.

## 📝 4. Quy Tắc Viết Commit Message
Sử dụng định dạng Conventional Commits: `<loại>: <mô tả ngắn gọn>`.

- `feat: add k-fold target encoding in k_fold.py`
- `fix: update db_config.py to handle cold start`
- `docs: update README with OOP structure`
- `refactor: refactor structure/file or fixbug,debug`

Lưu ý: Không dùng các commit chung chung như "update", "fix", "done".

## 🚀 5. Hướng Dẫn Lệnh Git Chi Tiết (Tóm Tắt)
Ghi nhớ: `origin` = repository trên GitHub. `main` = nhánh chính của team.

- **Lấy code mới nhất:** Luôn chạy `git pull origin main` trên nhánh main trước khi bắt đầu công việc.
- **Tạo nhánh mới:** `git checkout -b <tên_nhánh>` (vd: `git checkout -b 01_anduy_db_config`).
- **Lưu thay đổi:** `git add <tên_file>` và `git commit -m "feat: mô tả"`.
- **Đẩy code lên GitHub:** Lần đầu tiên chạy `git push -u origin <tên_nhánh>`, các lần sau chỉ cần `git push`.

## 🔀 6. Quy Trình Pull Request (PR) Trên GitHub
1. Vào repository trên GitHub → **Pull requests** → **New pull request**.
2. `base: main` ← `compare: nhánh của bạn` (ví dụ: 02_NHK_feature_engineer).
3. Điền mô tả PR và gán ít nhất 1 Reviewer (có thể gán Gia Bảo làm QA duyệt code).
4. Bấm **Create pull request**.

**Quy tắc bắt buộc khi Merge:**
- Không push trực tiếp lên `main`.
- Không tự merge PR của chính mình.
- PR chỉ được merge khi code chạy qua được các chốt chặn Assertions (ví dụ không có Missing Values) và có ≥ 1 Approve.
- Sau khi merge, nhấn **Delete branch** trên GitHub để dọn dẹp các nhánh đã hoàn thành.
