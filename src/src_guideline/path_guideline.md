# 🗺️ Hướng dẫn sử dụng Trung tâm Đường dẫn (`src/paths.py`)

File `src/paths.py` đóng vai trò là "bản đồ" quản lý toàn bộ đường dẫn của dự án. Việc sử dụng file này đảm bảo:
- **Chống đạn 100%** với lỗi sai đường dẫn (`FileNotFoundError`).
- **Tương thích chéo (Cross-platform):** Chạy mượt mà trên cả Windows, macOS và Linux.
- **Tự thích nghi:** Tự động nhận biết đang chạy bằng Script (`.py`) hay Jupyter Notebook (`.ipynb`).

---

## 1. Các biến đường dẫn khả dụng

Bạn có thể `import` trực tiếp các biến sau tùy vào mục đích sử dụng:
* **Thư mục hệ thống:** `PROJECT_ROOT`, `SRC_DIR`
* **Dữ liệu đầu vào:** `DATA_DIR` , `PROCESSED_DATA_DIR`
* **Dữ liệu đầu ra:** `MODELS_DIR`, `REPORTS_DIR`, `FIGURES_DIR`, `DATA_REPORTS_DIR`

---

## 2. Cách sử dụng trong file Python truyền thống (`.py`)

Vì cấu trúc đã được tự động hóa, bạn chỉ cần import đường dẫn và dùng dấu `/` để nối tên file.

```python
import pandas as pd
import joblib
from src.paths import PROCESSED_DATA_DIR, MODELS_DIR

# Đọc file tự động trỏ đúng vào data/processed_data/
df = pd.read_parquet(PROCESSED_DATA_DIR / "data_clean.parquet")

# Lưu model tự động trỏ vào thư mục models/
model_path = MODELS_DIR / "linear_model.pkl"
joblib.dump(model, model_path)
```

---

## 3. Cách sử dụng trong Jupyter Notebook (`.ipynb`)

Jupyter Notebook không nạp sẵn thư mục gốc của dự án. Do đó, bạn bắt buộc phải dán đoạn code sau vào ô (cell) đầu tiên của mọi file Notebook trước khi làm việc:

```python
import sys
from pathlib import Path

# 1. Thêm thư mục gốc vào hệ thống tìm kiếm của Python
sys.path.append(str(Path.cwd().parent))

# 2. Import đường dẫn và hàm khởi tạo thư mục
from src.paths import RAW_DATA_DIR, FIGURES_DIR, check_and_create_directories

# 3. Quét và tự động tạo các thư mục dự án nếu máy bạn chưa có
check_and_create_directories(auto_create=True)
```

Sau khi chạy ô trên, ở các ô code tiếp theo, bạn có thể gọi thư viện và đường dẫn bình thường như file `.py`.

---

## 4. Quản trị cấu trúc thư mục

File `paths.py` cung cấp hàm `check_and_create_directories` để team kiểm soát cấu trúc dự án đồng nhất trên mọi máy tính.

* **Chỉ kiểm tra (Mặc định):** Phù hợp để kiểm tra an toàn xem bạn có đang thiếu thư mục nào không.
```python
from src.paths import check_and_create_directories
check_and_create_directories() 
```

* **Tự động khởi tạo (Auto Create):** Nếu bạn mới clone dự án về hoặc thêm thư mục mới, hãy bật cờ `True`.
```python
from src.paths import check_and_create_directories
check_and_create_directories(auto_create=True)
```